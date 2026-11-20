"""Qualify bounded source panels, partial publication recovery and exact consumers."""
from dataclasses import asdict
from pathlib import Path
import argparse
import hashlib
import json
import runpy
import subprocess
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.whole_source import pipeline,resources,proposal,exact,controls
from scripts.whole_source.artifacts import ChunkStore
from scripts.whole_source.contract import bind_problem,canonical_bytes
from scripts.whole_source.execution import _write
from scripts.whole_source.receipts import discover_receipts,verify_stage


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--origin-commit',required=True)
    parser.add_argument('--comparison-dir',type=Path,required=True)
    args=parser.parse_args()
    output=args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=False)
    comparisons=[]
    for role in ('producer','analytic'):
        reports=[json.loads((args.comparison_dir/f'numerical-reuse-{role}-{side}-v1.json').read_bytes())
                 for side in ('baseline','corrected')]
        assert reports[0]['mathematical_digest']==reports[1]['mathematical_digest']
        assert reports[1]['counters']['basis_constructions']<reports[0]['counters']['basis_constructions']
        assert reports[1]['counters']['kernel_tiles_consumed']<reports[0]['counters']['kernel_tiles_consumed']
        comparisons.append({'role':role,'digest':reports[0]['mathematical_digest'],
            'before':reports[0]['counters'],'after':reports[1]['counters']})
    origin={'origin_git_commit':args.origin_commit,'origin_git_dirty':True}
    allocator=resources.auto_plan
    def allocate(template,*,parallel,memory_mib=None,helper_root=ROOT):
        return allocator(template,parallel=parallel,cpus=2,memory_mib=2048,helper_root=helper_root)
    problem=bind_problem('retained-t081')
    with patch.object(resources,'auto_plan',allocate):
        reduced=pipeline.prepare_source_inputs(problem,output/'source-inputs',control=True,tile_modes=2,**origin)
    publish=ChunkStore.publish_chunk
    interrupted=[]
    def interrupt(store,domain,staged):
        if domain.quantity.name=='F_column' and domain.columns.start==2 and not interrupted:
            earlier=store._chunk_ref(pipeline._column_task(store.spec,'F_column',0))
            assert earlier is not None
            interrupted.append(asdict(earlier))
            raise OSError('CONTROL_ONLY interruption after first panel column publication')
        return publish(store,domain,staged)
    with patch.object(ChunkStore,'publish_chunk',interrupt):
        try:
            pipeline.run_source(reduced['problem'],reduced['execution'],output/'source')
        except OSError as error:
            assert 'CONTROL_ONLY interruption' in str(error)
        else:
            raise AssertionError('partial publication barrier was not exercised')
    assert len(interrupted)==1
    root=output/'source/producer'
    protected={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for folder in ('attempts','snapshots','chunks','index','seals','dependencies')
        for p in (root/folder).rglob('*') if p.is_file()}
    pipeline.run_source(reduced['problem'],reduced['execution'],output/'source',resume=True)
    assert all(hashlib.sha256((root/name).read_bytes()).hexdigest()==value for name,value in protected.items())
    cli=subprocess.run([sys.executable,'-B','-m','scripts.weil_whole_source_split','audit',
        '--problem',str(reduced['problem']),'--execution',str(reduced['execution']),
        '--source',str(root/'source-manifest.json'),'--output-dir',str(output/'audit')],
        cwd=ROOT,capture_output=True,text=True)
    (output/'audit-cli-stdout.txt').write_text(cli.stdout,encoding='utf-8')
    (output/'audit-cli-stderr.txt').write_text(cli.stderr,encoding='utf-8')
    assert cli.returncode==0,cli.stderr
    audited=json.loads((output/'audit/analytical-receipt.json').read_bytes())
    assert audited['entries_checked']==36 and audited['full_mathematical_source'] is False
    factory=runpy.run_path(str(Path(__file__).with_name('verify-variant-snapshots-v1.py')))['manufactured_inputs']
    with patch.object(resources,'auto_plan',allocate):
        manufactured,reader,identity_proposal,identity_core=factory(output/'manufactured',origin)
        proposed_inputs=proposal.prepare_proposal_inputs(manufactured,reader.path,output/'proposal-inputs',panel_size=2,**origin)
    proposed=proposal.run_proposal(proposed_inputs['problem'],reader.path,proposed_inputs['execution'],output/'proposal')
    assert proposed['status']=='NONPROOF_ONLY' and proposed['matrix_positivity'] is False
    with patch.object(resources,'auto_plan',allocate):
        exact_inputs=exact.prepare_exact_inputs(manufactured,reader.path,output/'proposal/proposal.json',output/'exact-inputs',**origin)
    bind=exact._bind_exact
    bindings=[]
    def bound(*values,**kwargs):
        bindings.append(1)
        return bind(*values,**kwargs)
    with patch.object(exact,'_bind_exact',bound):
        assessed=exact.run_exact(exact_inputs['problem'],reader.path,output/'proposal/proposal.json',
            exact_inputs['execution'],output/'exact')
    assert len(bindings)==1
    assert assessed['status']=='PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL'
    assert assessed['proof_scope']=='CONTROL_ONLY' and assessed['assessment']['smooth_test_consequence_conditional'] is False
    cases=[]
    with patch.object(resources,'auto_plan',allocate):
        for name,expected in controls.EXACT_CASES:
            result=controls._exact_case(manufactured,reader,identity_proposal,identity_core,
                output/name,name,ROOT,origin)
            assert result['passed'] is True and result['status']==expected
            cases.append({'case':name,'status':result['status']})
    stages=[]
    peak=0
    panels=[]
    for receipt_path in discover_receipts(output):
        evidence=verify_stage(receipt_path)
        descriptor,plan=evidence['stage'],evidence['plan']
        assert plan.cpus==2 and plan.memory_mib==2048 and plan.workers*plan.threads<=2
        receipt=json.loads(receipt_path.read_bytes())
        peak=max(peak,receipt['peak_budgeted_memory_bytes'])
        tasks=[json.loads(line) for line in Path(descriptor['task_file']).read_bytes().splitlines()]
        if plan.task_function=='evaluate_source':
            panels.extend({'role':plan.role,'operation':task['operation'],'count':len(task['inputs'])}
                for task in tasks if task['operation'] in ('columns','heads'))
        stages.append({'receipt':receipt_path.relative_to(output).as_posix(),'tasks':descriptor['task_count'],
            'workers':plan.workers,'threads':plan.threads})
    assert len(stages)==39
    assert all(any(row['role']==role and row['operation']==operation and row['count']==2 for row in panels)
               for role in ('producer','analytic') for operation in ('columns','heads'))
    assert any(row['count']==1 for row in panels)
    report={'status':'PASS_CONTROL_ONLY_NUMERICAL_REUSE','comparisons':comparisons,
        'partial_panel_publication_recovered':True,'prior_immutable_members_unchanged':len(protected),
        'entries_checked':36,'owned_stage_count':len(stages),'owned_stages':stages,'source_panels':panels,
        'exact_parent_bindings':len(bindings),'exact_status':assessed['status'],'control_cases':cases,
        'max_owned_budgeted_memory_bytes':peak,'verification_cpus':2,'verification_memory_mib':2048,
        'full_qualification_executed':False,'full_mathematical_source':False,'production_admission':False}
    _write(output/'verification.json',canonical_bytes(report))
    print(json.dumps({'status':report['status'],'owned_stages':len(stages),'entries_checked':36,
        'partial_panel_recovered':True,'exact_parent_bindings':len(bindings)},sort_keys=True))


if __name__=='__main__':
    main()
