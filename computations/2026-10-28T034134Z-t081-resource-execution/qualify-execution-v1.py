"""Bind a completed captured run to code, numerical outcomes and resource evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OLD=ROOT/'computations/2026-10-27T140745Z-t081-complete-gram-attempt'


def load(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def require(condition,message):
    if not condition:raise ValueError(message)
def write(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(value,indent=2,sort_keys=True)+'\n')


def qualify(folder):
    result=load(folder/'qualification.json')
    require(result['status']=='PASS_CAPTURED_SOURCE_ANALYTICAL_EXACT_AND_NINE_CONTROLS','full captured verification did not pass')
    require(result['captured_tree_removed'] and result['capture']['expected_full_target_outputs_installed'] is False,'capture isolation/cleanup failed')
    budget=result['budget']
    require(budget['workers']==1 and 1<=budget['native_threads']<=budget['cpu_budget'],'invalid global execution budget')
    require(budget['memory_budget_bytes']>=budget['required_bytes'],'insufficient fixed-workload reservation')
    for name,digest in result['capture']['new_programs'].items():
        require(sha(folder/'captured-code-v1'/name)==digest,'captured code mismatch: '+name)
        if name!='verify-whole-sign-v1.py':require(sha(HERE/name)==digest,'active version changed after execution: '+name)
        else:require(sha(OLD/name)==digest,'exact verifier historical bytes changed')
    source=folder/'results/source.json';audit=load(folder/'results/audit.json');exact=load(folder/'results/exact.json')
    source_sha=sha(source)
    require(source_sha==result['source_sha256']==audit['source_sha256']==exact['source_sha256'],'mixed source byte snapshots')
    require(audit['checked_triangular_entries']==512946 and audit['checked_matrix_files']==6,'incomplete independent input acceptance')
    require(audit['consumer_sha256']==result['capture']['new_programs']['verify-whole-source-v2.py'],'analytical consumer identity mismatch')
    require(exact['blocks']==load(OLD/'data/exact-sign-v1.json')['blocks'],'exact full paid signs/radii differ from retained target')
    require(set(exact['blocks'])=={'even','odd'} and all(block['positive_complete_paid_lower'] and block['exact_nonsingularity'] and block['numerical_width_goal_passed'] for block in exact['blocks'].values()),'complete exact result missing')
    native=load(folder/'native-controls/native-controls.json')
    require(native['source_sha256']==source_sha and len(native['cases'])==6 and all(case['passed'] for case in native['cases']),'native controls missing')
    require(len(result['exact_controls'])==3 and all(case['passed'] for case in result['exact_controls']),'exact controls missing')
    # This summary records the original even control that was performed before
    # the six false packets. It does not execute or claim another reconstruction.
    even=next(block for block in audit['parity_summary'] if block['parity']==0)
    require(even['checked_triangular_entries']==256473 and even['status']=='PASS_NATIVE_CONTAINMENT','original even control missing')
    shared=folder/'native-controls/native-even-control.json'
    if not shared.exists():
        write(shared,{'format':'t081-even-control-derived-from-full-audit-v1',
            'status':'PASS_ORIGINAL_EVEN_CONTROL_FROM_COMPLETE_AUDIT','source_sha256':source_sha,
            'consumer_sha256':audit['consumer_sha256'],'complete_audit_sha256':sha(folder/'results/audit.json'),
            'complete_audit':'../results/audit.json','parity':even,
            'scope':'same fresh even reconstruction checked in the full audit before six false-source probes; no second reconstruction',
            'production_admission':False})
    else:require(load(shared)['complete_audit_sha256']==sha(folder/'results/audit.json'),'shared control summary binding changed')
    profiles={};stages=[]
    for stage in result['stages']:
        name=stage['stage'];receipt=load(folder/name/'receipt.json')
        require(receipt==stage and receipt['worker_cleanup_verified'],'stage receipt/cleanup mismatch')
        require(receipt['config_sha256']==sha(folder/'execution-budget.json'),'stage used another budget')
        require(receipt['budget']==budget,'stage budget changed')
        for channel,descriptor in receipt['logs'].items():
            require(sha(folder/descriptor['path'])==descriptor['sha256'],'stage stream changed')
        profile=load(folder/name/'profile.json')
        require(profile['native_threads']==budget['native_threads'],'selected native threads were not applied')
        require(profile['program_sha256']==receipt['program_sha256'],'stage program fingerprint mismatch')
        profiles[name]=profile
        stages.append({'stage':name,'elapsed_seconds':receipt['elapsed_seconds'],
            'cpu_seconds':profile['cpu_seconds'],'job_cpu_seconds':receipt['last_metrics'].get('cpu_seconds'),
            'raw_os_job_peak_bytes':receipt['peak_budgeted_memory_bytes'],
            'memory_metric':receipt['memory_metric'],'worker_cleanup_verified':True})
    require(profiles['source']['precision']==4608 and profiles['independent-audit']['precision']==6144,'fixed precision changed')
    terminal=load(folder/'.live/run-status.json')
    require(terminal['terminal'] and terminal['workflow_state']=='RUN_COMPLETED','live workflow did not finish successfully')
    identity=load(folder/'identity.json')
    require(identity['status']=='PASS_EXACT_RETAINED_PAYLOAD_IDENTITY' and identity['source_sha256']==source_sha and len(identity['matrices'])==6,'retained packet identity failed')
    return {'format':'t081-complete-execution-upgrade-qualification-v1',
        'status':'PASS_COMPLETE_LOCAL_EXECUTION_QUALIFICATION','source_sha256':source_sha,
        'qualifier_sha256':sha(Path(__file__)),
        'analytical_entries':512946,'exact_full_parity_blocks':2,'native_countercases':6,'exact_countercases':3,
        'captured_tree_removed':True,'all_owned_workers_reaped':True,'budget':budget,'stages':stages,
        'memory_enforcement':'owned Windows allocation limits; raw OS high-water counters are not an allocation-ceiling assertion',
        'metadata_only_shared_control_derivation':str(shared.relative_to(folder)),
        'source_enclosures_independently_reconstructed':True,'retained_smooth_test_admission_executed':False,
        'production_admission':False,'rh_status':'UNRESOLVED'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    result=qualify(args.run_dir.resolve());write(args.output,result)
    print(json.dumps({'status':result['status'],'analytical_entries':result['analytical_entries'],
        'countercases':result['native_countercases']+result['exact_countercases']}),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
