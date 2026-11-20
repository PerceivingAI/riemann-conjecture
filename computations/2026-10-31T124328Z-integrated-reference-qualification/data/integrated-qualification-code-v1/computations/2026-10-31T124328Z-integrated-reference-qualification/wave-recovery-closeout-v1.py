"""Close completed recovery evidence without rerunning owned mathematics.

The original qualifier incorrectly treated deliberately relocated receipt copies
as fresh executions. Copies remain negative evidence, never successful authority.
"""
from pathlib import Path
import argparse
import hashlib
import json
import runpy
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
PROCEDURES=Path(__file__).resolve().parent
FIELDS=('parity','dimension','goal','width','margin','tau','direction_index','direction_upper',
        'direction_mass','row_margins','transformed_digest','transformed_upper_entries','modular',
        'source_tiles_consumed')


def document(path):
    return json.loads(path.read_bytes())


def record(path):
    return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':path.stat().st_size}


def science(report):
    return [{key:block[key] for key in FIELDS} for block in report['blocks']]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    run,output=args.run_dir.resolve(strict=True),args.output_dir.resolve()
    output.relative_to(ROOT)
    output.mkdir(parents=True,exist_ok=False)
    from scripts.whole_source import proposal,recovery,controls
    from scripts.whole_source.contract import canonical_bytes
    from scripts.whole_source.receipts import discover_receipts,verify_stage
    work=run/'work'
    progress_path=sorted(run.glob('qualification-progress-*.json'))[-1]
    progress=document(progress_path)
    calls={row['label']:row['stages'] for row in progress['calls']}
    events={row['label']:row for row in progress['events']}
    assert events['relocated-output-rejected']['outcome']=='retained-error'
    assert calls['relocated-output-rejected']==[]
    assert [row['stage'] for row in calls['exact-second-interruption']]==['first']
    assert [row['stage'] for row in calls['exact-third-owner']]==['second','reduce','assess']
    for label in ('proposal-completed-resume','exact-completed-resume','final-intent-recovery',
                  'corrupt-operand-rejected','changed-config-rejected','normalized-transform-rejected',
                  'original-proposal-rejected'):
        assert calls[label]==[]
    expected_failures=('proposal-owned-failure','proposal-second-interruption','exact-owned-failure',
        'exact-second-interruption','successful-assess-owner-interruption','group-before-journal-head',
        'before-group','before-atomic-head','corrupt-operand-rejected','relocated-output-rejected',
        'changed-config-rejected','original-source-rejected','original-proposal-rejected',
        'normalized-transform-rejected')
    assert all(events[label]['outcome']=='retained-error' for label in expected_failures)
    baseline=document(work/'exact-fresh/report.json')
    assert baseline['status']=='PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL' and baseline['proof_scope']=='CONTROL_ONLY'
    reports=[]
    for name in ('exact-retry','exact-final-publication','exact-orphan-group','exact-before-group',
                 'exact-before-atomic-head','exact-serial'):
        path=work/name/'report.json'
        actual=document(path)
        assert science(actual)==science(baseline) and actual['assessment']==baseline['assessment']
        reports.append(record(path))
    def proposal_science(directory):
        core=document(directory/'proposal.json')
        result=[]
        for block in core['blocks']:
            refs={f"Z/{row['row']}/{row['column']}":row['artifact'] for row in block['integer_panels']}
            store=proposal.PanelStore(directory,block['context'],refs)
            result.append({'parity':block['parity'],'theta':block['theta'],'panels':[
                {'row':row['row'],'column':row['column'],
                 'values':store.read(f"Z/{row['row']}/{row['column']}",'integer')}
                for row in block['integer_panels']]})
        return result
    proposed=proposal_science(work/'proposal-retry')
    assert proposed==proposal_science(work/'proposal-fresh')
    comparisons=[]
    for name in ('task-layout-owned-parallel-v1','task-layout-owned-serial-v1'):
        path=run.parent/name/'verification.json'
        old=document(path)
        assert proposed==old['proposal_science']
        assert science(baseline)==old['exact_science'] and baseline['assessment']==old['assessment']
        comparisons.append(record(path))
    negatives=[]
    available={p.parent.parent.name:p for p in work.glob('*/run/report.json')}
    for name,status in controls.EXACT_CASES:
        path=available[name]
        actual=document(path)
        assert actual['status']==status and actual['proof_scope']=='CONTROL_ONLY'
        negatives.append({'name':name,'status':status,'report':record(path)})
    stages,failed,copies=[],[],[]
    relocated=work/'exact-relocated'
    for path in discover_receipts(work):
        raw=document(path)
        assert raw['worker_cleanup_verified'] is True
        if path.is_relative_to(relocated):
            original=work/'exact-retry'/path.relative_to(relocated)
            assert path.read_bytes()==original.read_bytes()
            copies.append({'copy':record(path),'original':record(original),
                           'contributes_execution_authority':False})
            continue
        if raw['exit_code']!=0:
            failed.append({'receipt':record(path),'exit_code':raw['exit_code'],'cleanup_verified':True})
            continue
        verified=verify_stage(path)
        stage,plan=verified['stage'],verified['plan']
        assert plan.memory_mib==2048 and plan.cpus in (1,2)
        complete=document(Path(stage['result_dir'])/'complete.json')
        stages.append({'receipt':verified['record'],'attempt_id':stage['attempt_id'],'stage':raw['stage'],
            'tasks':stage['task_count'],'actual_task_workers':len(complete['worker_pids']),
            'cpus':plan.cpus,'peak_owned_bytes':raw['peak_budgeted_memory_bytes']})
    assert copies and len(failed)>=2
    multiworker=any(row['stage']=='second' and row['actual_task_workers']>1 and
        Path(row['receipt']['directory']).is_relative_to(work/'exact-retry') for row in stages)
    assert multiworker
    serial=[row for row in stages if Path(row['receipt']['directory']).is_relative_to(work/'exact-serial')]
    assert len(serial)==5 and all(row['cpus']==1 and row['actual_task_workers']==1 for row in serial)
    started=time.perf_counter_ns()
    context=recovery._context_document(work/'exact-retry/collection')
    nodes,head=recovery._state(work/'exact-retry/collection',context)
    journal_scan_ns=time.perf_counter_ns()-started
    started=time.perf_counter_ns()
    selected=recovery.selected_receipts(work/'exact-retry/collection')
    selected_validation_ns=time.perf_counter_ns()-started
    assert len(selected)==5 and len({Path(row['directory']).parent.name for row in selected})==3
    assert len(discover_receipts(work/'exact-retry'))>len(selected)
    for folder in work.rglob('recovery/context.json'):
        if not folder.is_relative_to(relocated):
            recovery.check_history(folder.parent.parent)
    census=runpy.run_path(str(PROCEDURES/'wave-recovery-storage-v1.py'))['census']
    (output/'storage-census.json').write_bytes(canonical_bytes(census(work)))
    report={'format':'wave-recovery-readonly-closeout-v1','status':'PASS_CONTROL_ONLY_WAVE_RECOVERY_CLOSEOUT',
        'scope':'MANUFACTURED_FINITE_CONTROL_ONLY','original_failed_qualifier':record(run/'qualifier-failure.txt'),
        'original_program':record(PROCEDURES/'wave-recovery-qualify-v1.py'),'progress':record(progress_path),
        'reports':reports,'baseline_comparisons':comparisons,'negative_mathematical_controls':negatives,
        'successful_original_stages':stages,'retained_failed_stages':failed,
        'noncontributing_relocated_receipt_copies':copies,'selected_original_retry_receipts':selected,
        'actual_multiworker_missing_wave':multiworker,'actual_one_worker_replay':True,
        'cold_journal_scan_ns':journal_scan_ns,'cold_journal_nodes':len(nodes),
        'cold_selected_raw_validation_ns':selected_validation_ns,'storage':record(output/'storage-census.json'),
        'new_numerical_execution':False,'full_qualification':False,'independent_review':False,
        'production_admission':False,'limitations':['Graceful owned interruption, not power loss.',
            'Relocated copies are negative corpus, not new successful execution.',
            'No historical evidence is migrated, overwritten or deleted.']}
    (output/'verification.json').write_bytes(canonical_bytes(report))
    print(json.dumps({'status':report['status'],'successful_stages':len(stages),
                      'failed_stages':len(failed),'noncontributing_receipt_copies':len(copies)}))


if __name__=='__main__':
    main()
