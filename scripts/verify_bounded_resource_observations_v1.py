"""Bind completed resource observations without promoting them to mathematical acceptance."""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(value,message):
    if not value:raise ValueError(message)
def profile_for(folder,receipt,program):
    expected=digest(ROOT/program)
    require(receipt['program_sha256']==expected,'unexpected probe program '+program)
    path=folder/'profile.json'
    if not path.exists():
        require(receipt['exit_code']!=0,'missing successful profile '+program)
        return {}
    profile=json.loads(path.read_bytes())
    require(profile['program_sha256']==expected,'unexpected profile program '+program)
    return profile
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    bundle=args.bundle.resolve();inputs=bundle/'inputs-v1.json';config=json.loads(inputs.read_bytes());bound=[]
    for name,b in config['bindings'].items():
        require(digest(ROOT/b['path'])==b['sha256'],'changed dependency '+name);bound.append(name)
    results={};receipts={};observations=[]
    for mode in ('exact','proposal','prepare','images','frequency','transport','aggregate'):
        folder=bundle/'data'/(mode+'-t1');receipt=json.loads((folder/mode/'receipt.json').read_bytes())
        program='scripts/probe_exact_workspace_v1.py' if mode in ('exact','proposal') else 'scripts/probe_native_checkpoint_v1.py'
        profile=profile_for(folder/mode,receipt,program)
        require(receipt['worker_cleanup_verified'],'unverified cleanup '+mode)
        for channel,b in receipt['logs'].items():
            path=folder/mode/(channel+'.txt');require(digest(path)==b['sha256'],'changed raw stream '+mode+'/'+channel)
        result_path=folder/'result.json';result=json.loads(result_path.read_bytes()) if result_path.exists() else None
        status='completed' if receipt['exit_code']==0 else 'failed'
        if status=='completed':
            require(result is not None,'missing result '+mode)
            require(result.get('status') in ('passed','PASS_RESTRICTED_OBSERVATION_ONLY'),'unsuccessful result '+mode)
            require(result.get('target_positivity_proved') is False and result.get('full_target_matrices_computed') is False,'unsupported target flag '+mode)
            result_input=result.get('inputs_sha256',result.get('inputs',{}).get('sha256'))
            require(result_input==digest(inputs),'input/result mismatch '+mode)
            reported_program=result.get('program_sha256',result.get('script',{}).get('sha256'))
            require(reported_program==receipt['program_sha256']==profile['program_sha256'],'program/profile/result mismatch '+mode)
            require(profile['exit_code']==0,'profile failure '+mode)
            results[mode]=result
        observations.append({'mode':mode,'execution_status':status,'exit_code':receipt['exit_code'],'result_present':result is not None,'error':receipt.get('error') or profile.get('error'),'stage_wall_seconds':receipt['elapsed_seconds'],'peak_owned_job_committed_bytes':receipt['peak_budgeted_memory_bytes'],'cleanup_verified':True,'receipt_sha256':digest(folder/mode/'receipt.json'),'result_sha256':digest(result_path) if result is not None else None})
        receipts[mode]=receipt
    if 'exact' in results:
        r=results['exact']['exact'];d=r['dimension'];p=r['modulus'];expected=1
        require(p==65521 and all(p%i for i in range(2,math.isqrt(p)+1)),'unverified modulus')
        for i in range(d):
            for j in range(i+1,d):expected=expected*(j-i)%p
        require(r['vandermonde_determinant']==r['independent_expected_determinant']==expected!=0,'global determinant result')
        require(r['full_inner_domain']==2782 and r['mass_lcm_bits']>=10000,'wrong exact domain')
        require(all(c['exact_match'] and c['omitted_final_inner_differs'] for c in r['selected_entry_checks']),'integer controls')
        require(r['mass_selected_entry_checks_passed'],'mass control')
    if 'proposal' in results:
        r=results['proposal'];require(r['reduced']['known_factor_contained'] and r['reduced']['exact_solution_contained'],'proposal exact controls')
        require(r['float']['full_eigenvector_shape']==[2782,2782] and r['float']['full_spectrum_count']==2782,'incomplete float shape')
        require(all(x['relative_residual']<=x['tolerance'] for x in r['float']['selected_residual_checks']),'float residual control')
    if 'prepare' in results:require(results['prepare']['details']['exact_highest_polynomial_agrees'],'highest basis mismatch')
    if 'images' in results:
        r=results['images']['details'];require(r['active_powers']==[2,3,4,5,7] and r['highest_head_mode']==11127,'wrong image domain')
        require(r['checked_enclosures']==16 and r['prime7_omission_rejected_nodes']>0,'image controls')
        require(r['all_native_widths_or_full_target_goal_checked'] is False,'overstated width scope')
    if 'frequency' in results:require(results['frequency']['details']['checked_enclosures']==4 and results['frequency']['details']['complete_frequency_domain_checked'] is False,'band scope')
    if 'transport' in results:require(results['transport']['details']['corrupt_CRC_rejected'],'transport corruption control')
    if 'aggregate' in results:require(results['aggregate']['details']['owned_child_processes_reaped'],'native children remain')
    for mode,suffix,program,expected_status in (
        ('coefficients','coefficients-t1','scripts/probe_coefficient_reuse_v1.py','PASS_EXACT_SELECTED_COEFFICIENTS'),
        ('panels','panels-detected','scripts/probe_compact_native_panels_v1.py','PASS_COMPLETE_SYNTHETIC_INNER_PRODUCT')):
        folder=bundle/'data'/suffix;receipt=json.loads((folder/mode/'receipt.json').read_bytes())
        profile=profile_for(folder/mode,receipt,program)
        require(receipt['worker_cleanup_verified'],'unverified cleanup '+mode)
        for channel,b in receipt['logs'].items():require(digest(folder/mode/(channel+'.txt'))==b['sha256'],'changed extra stream '+mode)
        result_path=folder/'result.json';result=json.loads(result_path.read_bytes()) if result_path.exists() else None
        if receipt['exit_code']==0:
            require(result is not None and result['status']==expected_status,'unsuccessful extra result '+mode)
            require(result['inputs_sha256']==digest(inputs),'extra input mismatch '+mode)
            require(result['program_sha256']==digest(ROOT/program)==receipt['program_sha256']==profile['program_sha256'],'extra program mismatch '+mode)
            require(result['target_positivity_proved'] is False and result['production_admission'] is False,'extra scope mismatch '+mode)
            if mode=='coefficients':
                require([r['degree'] for r in result['rows']]==[0,1,2,132,5563,11127],'coefficient domains')
                require(all(r['all_exact_equal'] and r['omitted_leading_coefficient_detected'] and r['all_coefficients_checked']==r['degree']+1 for r in result['rows']),'coefficient mathematics')
            else:
                require(result['full_inner_count']==8346 and result['native_precision']==34304 and result['checkpoint_grid']==512,'compact product domain')
                require(all(r['complete_endpoint_range_contained'] and r['omitted_final_inner_rejected'] for r in result['checks']),'compact interval controls')
            results[mode]=result
        observations.append({'mode':mode,'execution_status':'completed' if receipt['exit_code']==0 else 'failed','exit_code':receipt['exit_code'],'result_present':result is not None,'error':receipt.get('error') or profile.get('error'),'stage_wall_seconds':receipt['elapsed_seconds'],'peak_owned_job_committed_bytes':receipt['peak_budgeted_memory_bytes'],'cleanup_verified':True,'receipt_sha256':digest(folder/mode/'receipt.json'),'result_sha256':digest(result_path) if result is not None else None})
    out={'format':'bounded-resource-observation-qualification-v1','status':'PASS_RETAINED_SCOPED_OBSERVATIONS' if len(results)==9 else 'PASS_RETAINED_OBSERVATIONS_WITH_CLASSIFIED_FAILURES','inputs_sha256':digest(inputs),'bindings_checked':bound,'observations':observations,'successful_modes':sorted(results),'complete_target_feasibility_established':False,'target_positivity_proved':False,'production_admission':False,'limits':['Synthetic exact/float matrices are not a target witness or target conditioning.','Selected nodes/bands are not complete quadrature or kernel acceptance.','No source/consumer/proposal/exact end-to-end target implementation or run.','Timing observations are not universal scaling laws or cold-storage benchmarks.']}
    with args.output.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'successful_modes':out['successful_modes'],'all_recorded_cleanups_verified':True},sort_keys=True))
    return 0
if __name__=='__main__':raise SystemExit(main())
