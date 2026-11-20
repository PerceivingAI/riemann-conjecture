"""Qualify metadata changes with real owned execution and explicit controls only."""
from dataclasses import asdict, replace
from pathlib import Path
import argparse
import json
import runpy
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source.artifacts import ChunkStore, CollectionLock, CollectionSpec, StagedChunk
from scripts.whole_source import exact, pipeline, proposal, resources
from scripts.whole_source.contract import ArtifactRef, QuantityKey, bind_problem, canonical_bytes
from scripts.whole_source.execution import WorkloadExecution, _write
from scripts.whole_source.receipts import discover_receipts, verify_stage
from scripts.whole_source.slice import _ref, _request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-report', type=Path, required=True)
    parser.add_argument('--corrected-report', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--origin-commit', required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    before = json.loads(args.baseline_report.read_bytes())
    after = json.loads(args.corrected_report.read_bytes())
    assert before['status'] == after['status'] == 'PASS_CONTROL_ONLY_STRUCTURAL_METADATA'
    assert len(before['results']) == len(after['results'])
    for old, new in zip(before['results'], after['results']):
        assert old['chunks'] == new['chunks']
        assert old['science_sha256'] == new['science_sha256']
        old_counts, new_counts = old['publication_counters'], new['publication_counters']
        assert old_counts['quota_checks'] == new_counts['quota_checks']
        assert old_counts['tree_walks'] == 2*new_counts['tree_walks']
        assert new_counts['index_reads'] == 0
    origin = {'origin_git_commit':args.origin_commit,'origin_git_dirty':True}
    allocator = resources.auto_plan
    def allocate(template, *, parallel, memory_mib=None, helper_root=ROOT):
        return allocator(template, parallel=parallel, cpus=2, memory_mib=2048,
                         helper_root=helper_root)
    problem = bind_problem('retained-t081')
    with patch.object(resources,'auto_plan',allocate):
        reduced = pipeline.prepare_source_inputs(problem,output/'reduced-inputs',
            control=True,tile_modes=2,**origin)
    _, _, roles = pipeline._bind(reduced['problem'],reduced['execution'],ROOT)
    spec, plan = roles['producer']
    program = Path(__file__).with_name('metadata-owned-control-v1.py')
    task_ref = _ref(ROOT,program.relative_to(ROOT).as_posix())
    refs = tuple(sorted((*spec.code_refs,task_ref),key=lambda ref:ref.path))
    control_spec = CollectionSpec.create(problem,role=spec.role,quantities=spec.quantities,
        partition=spec.partition,backend='integer-rational',backend_version='stdlib-v1',
        native_threads=spec.native_threads,code_refs=refs,bounds=spec.bounds,grid_bits=spec.grid_bits)
    origin_path = output/'structural-origin.json'
    _write(origin_path,canonical_bytes({'format':'whole-source-code-origin-v1',**origin,
        'files':[asdict(ref) for ref in refs]}))
    control_plan = replace(plan,collection_sha256=control_spec.collection_id,
        task_program=task_ref,task_function='evaluate',scope='OPERATIONAL_CONTROL_ONLY',
        backend='integer-rational',backend_version='stdlib-v1',
        provenance=_ref(ROOT,origin_path.relative_to(ROOT).as_posix()))
    tasks = list(pipeline._tiles(control_spec,QuantityKey('A_model',0)))[:2]
    assert len(tasks) == 2
    with CollectionLock.acquire(output/'owned-structural',control_spec) as lock:
        with WorkloadExecution(lock,control_spec,control_plan) as execution:
            execution.run_stage('metadata-control',[_request(domain=task.to_dict()) for task in tasks])
            results = [item['result'] for item in execution.read_results('metadata-control')]
            store = ChunkStore(lock,control_spec,attempt_id=execution.attempt_id)
            by_domain = {canonical_bytes(item['domain']):item for item in results}
            for task in tasks:
                result = by_domain[canonical_bytes(task.to_dict())]
                assert result['scope'] == 'CONTROL_ONLY_STRUCTURAL_NOT_WEIL_SOURCE'
                ref = ArtifactRef(**result['artifact'])
                staged = StagedChunk(lock.root/ref.path,task,ref,result['generation'],result['attempt_id'])
                published = store.publish_chunk(task,staged)
                assert store.read_chunk(published).records
    pipeline.run_source(reduced['problem'],reduced['execution'],output/'source')
    audited = pipeline.run_audit(reduced['problem'],output/'source/producer/source-manifest.json',
        reduced['execution'],output/'audit')
    assert audited['entries_checked'] == 36 and audited['full_mathematical_source'] is False
    factory_path = Path(__file__).with_name('verify-variant-snapshots-v1.py')
    factory = runpy.run_path(str(factory_path))['manufactured_inputs']
    with patch.object(resources,'auto_plan',allocate):
        manufactured_problem, reader, _, _ = factory(output/'manufactured',origin)
        proposed_inputs = proposal.prepare_proposal_inputs(manufactured_problem,reader.path,
            output/'proposal-inputs',panel_size=2,**origin)
    proposed = proposal.run_proposal(proposed_inputs['problem'],reader.path,
        proposed_inputs['execution'],output/'proposal')
    assert proposed['status'] == 'NONPROOF_ONLY' and proposed['matrix_positivity'] is False
    with patch.object(resources,'auto_plan',allocate):
        exact_inputs = exact.prepare_exact_inputs(manufactured_problem,reader.path,
            output/'proposal/proposal.json',output/'exact-inputs',**origin)
    cli = subprocess.run([sys.executable,'-B','-m','scripts.weil_whole_source_split','exact',
        '--problem',str(exact_inputs['problem']),'--source',str(reader.path),
        '--proposal',str(output/'proposal/proposal.json'),'--execution',str(exact_inputs['execution']),
        '--output-dir',str(output/'exact')],cwd=ROOT,capture_output=True,text=True)
    (output/'exact-cli-stdout.txt').write_text(cli.stdout,encoding='utf-8')
    (output/'exact-cli-stderr.txt').write_text(cli.stderr,encoding='utf-8')
    assert cli.returncode == 0, cli.stderr
    assessed = json.loads((output/'exact/report.json').read_bytes())
    assert assessed['status'] == 'EXACT_MATRIX_POSITIVITY' and assessed['proof_scope'] == 'CONTROL_ONLY'
    checks = []
    for receipt in discover_receipts(output):
        evidence = verify_stage(receipt)
        checks.append({'receipt':receipt.relative_to(output).as_posix(),
            'task_count':evidence['stage']['task_count']})
    assert len(checks) == 30
    resource_paths = list((output/'owned-structural').rglob('metadata-control-resources.json'))
    assert len(resource_paths) == 1
    observed = json.loads(resource_paths[0].read_bytes())
    assert observed['cleanup_verified'] is True
    report = {'status':'PASS_CONTROL_ONLY_METADATA_CORRECTION','origin':origin,
        'verification_envelope':{'cpus':2,'memory_mib':2048,'production_defaults_changed':False},
        'structural_comparison':{'baseline':str(args.baseline_report),'corrected':str(args.corrected_report),
            'same_decoded_manufactured_values':True,'mathematical_source':False},
        'owned_structural_resources':observed,'owned_stage_count':len(checks),'owned_stages':checks,
        'independent_reduced_entries_checked':audited['entries_checked'],
        'proposal_status':proposed['status'],'exact_status':assessed['status'],
        'manufactured_factory':asdict(_ref(ROOT,factory_path.relative_to(ROOT).as_posix())),
        'scientific_full_source_acceptance':False,'production_admission':False}
    _write(output/'verification.json',canonical_bytes(report))
    print(json.dumps({'status':report['status'],'owned_stage_count':len(checks),
        'independent_reduced_entries_checked':audited['entries_checked'],
        'exact_status':assessed['status']},sort_keys=True))


if __name__ == '__main__':
    main()
