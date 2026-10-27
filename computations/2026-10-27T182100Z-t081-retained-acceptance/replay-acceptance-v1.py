"""Reproduce the fixed complete T81/100 criterion from captured code/input bytes.

Expected full target outputs are held outside the scientific child tree. The
recorded installed Python/FLINT runtime is shared, not an independent OS image.
"""
import argparse,hashlib,json,os,subprocess,sys,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CANDIDATE='computations/2026-10-27T140745Z-t081-complete-gram-attempt'
QUALIFICATION='computations/2026-10-27T132236Z-t081-prime-five-qualification'
SOURCE_SHA='f69fee0feb9c08833ad6a3091718c9a6a301e5b5ddbea96ee5f0f6c0553c8b6e'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def require(ok,message):
    if not ok:raise ValueError(message)
def confined(base,name):
    require(type(name) is str and name and '\\' not in name and ':' not in name and not name.startswith('/'),'portable relative path required')
    require(all(x not in ('','.','..') for x in name.split('/')),'unsafe path component')
    path=(base/name).resolve();require(path.is_relative_to(base.resolve()),'path escapes captured root');return path

def replay():
    capture_path=HERE/'captured-source-inputs-v1.json';capture_raw=capture_path.read_bytes();capture=json.loads(capture_raw)
    require(capture['format']=='t081-retained-complete-source-input-closure-v1' and capture['source_sha256']==SOURCE_SHA,'capture identity')
    records=capture['files'];require(records and len({r['destination'] for r in records})==len(records),'missing or duplicate capture destination')
    raws={}
    for item in records:
        raw=confined(HERE,item['stored']).read_bytes();require(len(raw)==item['bytes'] and sha(raw)==item['sha256'],'captured file changed '+item['destination']);raws[item['destination']]=raw
    result={'format':'t081-complete-retained-isolated-replay-v1','source_sha256':SOURCE_SHA,'captured_manifest_sha256':sha(capture_raw),'captured_files':len(records),'driver_sha256':sha(Path(__file__).read_bytes()),'steps':[],'qualification_checks':{},'checks':{},'original_tree_scientific_execution':False,'expected_full_target_outputs_installed_in_child':False,'production_admission':False}
    with tempfile.TemporaryDirectory(prefix='rh_t081_retained_') as temporary:
        isolated=Path(temporary)
        for item in records:
            if 'installed' in item['roles']:
                target=confined(isolated,item['destination']);target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as handle:handle.write(raws[item['destination']])
        require(not (isolated/CANDIDATE/'data/source-v1.json').exists() and not (isolated/CANDIDATE/'data/source-audit-v1.json').exists() and not (isolated/CANDIDATE/'data/exact-sign-v1.json').exists(),'expected target outputs leaked into child')
        env=os.environ.copy();env.pop('PYTHONPATH',None);env['PYTHONDONTWRITEBYTECODE']='1'
        for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS','FLINT_NUM_THREADS'):env[key]='1'
        def run(name,args):
            started=time.monotonic();p=subprocess.run([sys.executable,'-I','-B',*map(str,args)],cwd=isolated,env=env,capture_output=True,text=True,encoding='utf-8')
            result['steps'].append({'name':name,'argv':list(map(str,args)),'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-started,'stdout':p.stdout,'stderr':p.stderr})
            require(p.returncode==0,'isolated calculation failed '+name+' '+p.stdout+p.stderr)
        q=Path(QUALIFICATION);qout=q/'data/retained-replay';(isolated/qout).mkdir(parents=True)
        def scalar(name,script,args,expected,output):
            run(name,[q/script,*args]);raw=confined(isolated,output.as_posix()).read_bytes();old=raws[(q/expected).as_posix()]
            require(raw==old,'scalar scientific output not byte-identical '+name)
            result['qualification_checks'][name]={'byte_identical':True,'sha256':sha(raw)}
        gs=qout/'global-source.json';ga=qout/'global-audit.json';rs=qout/'supported-source.json';ra=qout/'supported-audit.json';ds=qout/'declaration.json';da=qout/'declaration-audit.json';ts=qout/'topology-source.json';ta=qout/'topology-audit.json'
        scalar('fresh_global_source','qualify-reference-v1.py',['--inputs',q/'qualification-inputs-v2.json','--output',gs],'data/reference-source-v2.json',gs)
        scalar('fresh_global_native_audit','verify-reference-v1.py',['--inputs',q/'qualification-inputs-v2.json','--source',gs,'--output',ga],'data/reference-audit-v2.json',ga)
        scalar('supported_reference_source','qualify-reference-v2.py',['--inputs',q/'qualification-inputs-v3.json','--output',rs],'data/supported-reference-source-v1.json',rs)
        scalar('supported_reference_native_audit','verify-reference-v2.py',['--inputs',q/'qualification-inputs-v3.json','--source',rs,'--output',ra],'data/supported-reference-audit-v1.json',ra)
        scalar('target_declaration','declare-target-v1.py',['--inputs',q/'parameter-inputs-v1.json','--reference-audit',ra,'--output',ds],'data/target-declaration-source-v1.json',ds)
        scalar('target_declaration_native_audit','verify-target-declaration-v1.py',['--inputs',q/'parameter-inputs-v1.json','--source',ds,'--reference-audit',ra,'--output',da],'data/target-declaration-audit-v1.json',da)
        scalar('four_mode_topology_source','qualify-prime-five-topology-v1.py',['--inputs',q/'topology-inputs-v1.json','--output',ts],'data/topology-source-v1.json',ts)
        scalar('four_mode_topology_native_audit','verify-prime-five-topology-v1.py',['--inputs',q/'topology-inputs-v1.json','--source',ts,'--output',ta],'data/topology-audit-v1.json',ta)
        b=Path(CANDIDATE);out=b/'data/retained-replay';(isolated/out).mkdir(parents=True)
        inp=b/'whole-inputs-v1.json';src=out/'source-v1.json';aud=out/'source-audit-v1.json';proof=out/'exact-sign-v1.json'
        run('fresh_complete_source',[b/'build-whole-source-v1.py','--inputs',inp,'--output',src])
        run('independent_complete_analytic_audit',[b/'verify-whole-source-v1.py','--inputs',inp,'--source',src,'--output',aud])
        run('zero_float_complete_sign',[b/'verify-whole-sign-v1.py','--inputs',inp,'--source',src,'--proposal',b/'data/proposal-v1.json.gz','--output',proof])
        fresh_source=(isolated/src).read_bytes();require(sha(fresh_source)==SOURCE_SHA and fresh_source==raws[CANDIDATE+'/data/source-v1.json'],'fresh source byte mismatch')
        result['checks']['complete_source']={'byte_identical':True,'sha256':SOURCE_SHA}
        source=json.loads(fresh_source)
        for name,descriptor in source['matrices'].items():
            original=raws[CANDIDATE+'/data/'+descriptor['path']];fresh=(isolated/out/descriptor['path']).read_bytes()
            require(fresh==original and sha(fresh)==descriptor['sha256'],'matrix byte mismatch '+name);result['checks'][name]={'byte_identical':True,'sha256':sha(fresh)}
        fresh_audit=load(isolated/aud);old_audit=json.loads(raws[CANDIDATE+'/data/source-audit-v1.json'])
        require(fresh_audit['status']=='PASS_COMPLETE_SOURCE' and fresh_audit['checked_triangular_entries']==512946 and fresh_audit['source_sha256']==SOURCE_SHA,'full native source gate')
        for key in ('source','inputs'):fresh_audit.pop(key);old_audit.pop(key)
        require(fresh_audit==old_audit,'native audit differs beyond execution paths');result['checks']['complete_native_audit']={'identical_except_explicit_paths':['source','inputs'],'all_other_fields_identical':True}
        fresh_proof=(isolated/proof).read_bytes();require(fresh_proof==raws[CANDIDATE+'/data/exact-sign-v1.json'],'exact scientific report byte mismatch');signed=json.loads(fresh_proof)
        require(signed['status']=='PASS_COMPLETE_SOURCE_CONDITIONAL_CANDIDATE' and signed['source_sha256']==SOURCE_SHA and set(signed['blocks'])=={'even','odd'} and all(x['dimension']==413 and x['positive_complete_paid_lower'] and x['exact_nonsingularity'] and x['numerical_width_goal_passed'] for x in signed['blocks'].values()),'complete exact gate')
        result['checks']['complete_exact_sign']={'byte_identical':True,'sha256':sha(fresh_proof)}
    result['own_isolated_tree_removed']=not isolated.exists();require(result['own_isolated_tree_removed'],'owned temporary tree remains')
    result['status']='PASS_COMPLETE_CAPTURED_REFERENCE_SOURCE_AND_EXACT_REPLAY';return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();require(not args.output.exists(),'fresh report required')
    result=replay();args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:handle.write(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'captured_files':result['captured_files'],'qualification_checks':len(result['qualification_checks']),'target_checks':len(result['checks']),'own_isolated_tree_removed':result['own_isolated_tree_removed']}))
if __name__=='__main__':main()
