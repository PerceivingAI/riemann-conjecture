"""Replay the fixed T4/5 analytic and exact consequence from captured bytes."""
import argparse,gzip,hashlib,json,os,subprocess,sys,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
CANDIDATE='computations/2026-10-27T061820Z-t080-complete-gram-attempt'
QUALIFICATION='computations/2026-10-27T050743Z-t080-target-qualification'
SOURCE_SHA='f50d8a194bf4d13ad4cd65ccbcf5762c403d8f5e26d384cbdb38be5ccb807fe6'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def require(ok,message):
    if not ok:raise ValueError(message)

def confined(base,relative):
    require(type(relative) is str and not Path(relative).is_absolute(),'relative path required')
    path=(base/relative).resolve();require(path.is_relative_to(base.resolve()),'path escapes captured root');return path

def capture():
    path=HERE/'captured-source-inputs-v1.json'
    if path.exists():return load(path)
    inputs=load(HERE/'acceptance-inputs-v1.json');base=ROOT/CANDIDATE
    mraw=(base/'manifest.json').read_bytes();require(sha(mraw)==inputs['candidate_manifest_sha256'],'candidate manifest binding');manifest=json.loads(mraw)
    for item in manifest['members']:
        raw=confined(base,item['path']).read_bytes();require(sha(raw)==item['sha256'] and len(raw)==item['bytes'],'candidate member changed '+item['path'])
    source=load(base/'data/whole-source-v2.json');require(sha((base/'data/whole-source-v2.json').read_bytes())==SOURCE_SHA,'candidate source binding')
    files={}
    def add(destination,raw,role):
        confined(ROOT,destination)
        if destination in files:
            require(files[destination]['sha256']==sha(raw),'conflicting capture destination');files[destination]['roles'].append(role);return
        stored='captured-bytes-v1/'+destination;target=HERE/stored;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as stream:stream.write(raw)
        files[destination]={'destination':destination,'stored':stored,'bytes':len(raw),'sha256':sha(raw),'roles':[role]}
    for relative,expected in manifest['external_immutable_or_captured_project_input_sha256'].items():
        raw=confined(ROOT,relative).read_bytes();require(sha(raw)==expected,'external scientific input changed');add(relative,raw,'installed')
    for name in ('build-whole-source-v2.py','verify-whole-source-v2.py','verify-whole-sign-v1.py','propose-whole-v2.py','whole-inputs-v1.json','data/whole-proposal-v2.json'):
        add(CANDIDATE+'/'+name,(base/name).read_bytes(),'installed')
    for name in ('data/whole-source-v2.json','data/whole-source-audit-v2.json','data/whole-exact-sign-v2.json','manifest.json'):
        add(CANDIDATE+'/'+name,(base/name).read_bytes(),'expected')
    for desc in source['matrices'].values():
        rel='data/'+desc['path'];raw=(base/rel).read_bytes();require(sha(raw)==desc['sha256'],'expected matrix binding');add(CANDIDATE+'/'+rel,raw,'expected')
    # Replay the already accepted scalar/reference qualification too. Its own
    # immutable closure performs all six native/scalar pairs and eight exact caps.
    qb=ROOT/QUALIFICATION;qm=load(qb/'manifest.json');qcapture=load(qb/'captured-source-v1.json')
    workflow='scripts/weil_t080_qualification_replay.py';raw=(ROOT/workflow).read_bytes()
    require(sha(raw)==qm['current_root_source_sha256'][workflow],'qualification workflow changed');add(workflow,raw,'installed')
    add(QUALIFICATION+'/captured-source-v1.json',(qb/'captured-source-v1.json').read_bytes(),'installed')
    for item in qcapture['files']:
        raw=confined(qb,item['stored']).read_bytes();require(sha(raw)==item['sha256'] and len(raw)==item['bytes'],'qualification captured input changed')
        add(QUALIFICATION+'/'+item['stored'],raw,'installed')
    for name in ('control-budget-v1.json','control-budget-audit-v1.json','reference-v1.json','reference-audit-v1.json','target-declaration-v1.json','target-declaration-audit-v2.json'):
        add(QUALIFICATION+'/data/'+name,(qb/'data'/name).read_bytes(),'installed')
    budget=load(qb/'data/control-budget-v1.json')
    for block in budget['parities'].values():
        for cap in block['relative_caps'].values():
            rel='data/'+cap['witness'];raw=(qb/rel).read_bytes();require(sha(raw)==cap['sha256'],'old exact cap input binding');add(QUALIFICATION+'/'+rel,raw,'installed')
    add(QUALIFICATION+'/manifest.json',(qb/'manifest.json').read_bytes(),'evidence')
    result={'format':'t080-retained-complete-source-input-closure-v1','source_sha256':SOURCE_SHA,'files':[files[k] for k in sorted(files)],'capture_contract':'All scientific programs/inputs installed from these bytes only; expected target outputs are not installed','driver_sha256':sha(Path(__file__).read_bytes())}
    with path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(json.dumps(result,sort_keys=True,indent=2)+'\n')
    return result

def replay():
    manifest=capture();mraw=(HERE/'captured-source-inputs-v1.json').read_bytes();records=manifest['files'];require(len({r['destination'] for r in records})==len(records),'duplicate captured destination');raws={}
    for item in records:
        raw=confined(HERE,item['stored']).read_bytes();require(sha(raw)==item['sha256'] and len(raw)==item['bytes'],'captured file changed');raws[item['destination']]=raw
    result={'format':'t080-complete-retained-isolated-replay-v1','source_sha256':SOURCE_SHA,'captured_manifest_sha256':sha(mraw),'captured_files':len(records),'driver_sha256':sha(Path(__file__).read_bytes()),'steps':[],'checks':{},'original_tree_scientific_execution':False,'production_admission':False}
    with tempfile.TemporaryDirectory(prefix='rh_t080_retained_') as temporary:
        isolated=Path(temporary)
        for item in records:
            if 'installed' not in item['roles']:continue
            dest=confined(isolated,item['destination']);dest.parent.mkdir(parents=True,exist_ok=True)
            with dest.open('xb') as stream:stream.write(raws[item['destination']])
        env=os.environ.copy();env.pop('PYTHONPATH',None)
        for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env.setdefault(key,'1')
        def run(name,args):
            start=time.monotonic();process=subprocess.run([sys.executable,'-I','-B',*args],cwd=isolated,env=env,text=True,capture_output=True,encoding='utf-8')
            result['steps'].append({'name':name,'argv':args,'exit_code':process.returncode,'elapsed_seconds':time.monotonic()-start,'stdout':process.stdout,'stderr':process.stderr})
            require(process.returncode==0,'isolated operation failed '+name+' '+process.stdout+process.stderr)
        run('complete_reference_and_error_qualification',['scripts/weil_t080_qualification_replay.py','--bundle',QUALIFICATION,'--output','qualification-replay.json'])
        qualification=load(isolated/'qualification-replay.json');require(qualification['status']=='PASS_CAPTURED_QUALIFICATION_REPLAY' and len(qualification['checks'])==14 and qualification['own_isolated_tree_removed'],'qualification replay not complete')
        result['qualification_replay']=qualification
        b=Path(CANDIDATE);out=b/'data/replayed';(isolated/out).mkdir(parents=True)
        inp=(b/'whole-inputs-v1.json').as_posix();src=(out/'whole-source-v2.json').as_posix();aud=(out/'whole-source-audit-v2.json').as_posix();proof=(out/'whole-exact-sign-v2.json').as_posix()
        run('fresh_complete_source',[(b/'build-whole-source-v2.py').as_posix(),'--inputs',inp,'--output',src])
        run('independent_complete_analytic_audit',[(b/'verify-whole-source-v2.py').as_posix(),'--inputs',inp,'--source',src,'--output',aud])
        run('zero_float_complete_sign',[(b/'verify-whole-sign-v1.py').as_posix(),'--inputs',inp,'--source',src,'--proposal',(b/'data/whole-proposal-v2.json').as_posix(),'--output',proof])
        freshsrc=(isolated/src).read_bytes();require(sha(freshsrc)==SOURCE_SHA and freshsrc==raws[CANDIDATE+'/data/whole-source-v2.json'],'complete source byte mismatch')
        result['checks']['complete_source']={'byte_identical':True,'sha256':sha(freshsrc)}
        for name,desc in source_from_bytes(freshsrc)['matrices'].items():
            original=raws[CANDIDATE+'/data/'+desc['path']];fresh=(isolated/out/desc['path']).read_bytes()
            require(fresh==original and sha(fresh)==desc['sha256'],'matrix byte mismatch '+name);result['checks'][name]={'byte_identical':True,'sha256':sha(fresh)}
        audit=load(isolated/aud);oldaudit=json.loads(raws[CANDIDATE+'/data/whole-source-audit-v2.json'])
        require(audit['status']=='PASS_COMPLETE_SOURCE' and audit['checked_triangular_entries']==78246 and audit['source_sha256']==SOURCE_SHA,'full native source gate')
        for key in ('source','inputs'):audit.pop(key);oldaudit.pop(key)
        require(audit==oldaudit,'native audit differs beyond two explicit execution paths');result['checks']['complete_native_audit']={'identical_except_explicit_paths':['source','inputs'],'all_other_fields_identical':True}
        freshproof=(isolated/proof).read_bytes();require(freshproof==raws[CANDIDATE+'/data/whole-exact-sign-v2.json'],'exact sign scientific byte mismatch');signed=json.loads(freshproof)
        require(signed['status']=='PASS_COMPLETE_SOURCE_CONDITIONAL_CANDIDATE' and signed['source_sha256']==SOURCE_SHA and all(x['positive_complete_paid_lower'] and x['exact_nonsingularity'] and x['numerical_width_goal_passed'] for x in signed['blocks'].values()),'full exact sign gate')
        result['checks']['complete_exact_sign']={'byte_identical':True,'sha256':sha(freshproof)}
    result['own_isolated_tree_removed']=not isolated.exists();require(result['own_isolated_tree_removed'],'owned temporary tree remains');result['status']='PASS_COMPLETE_CAPTURED_REFERENCE_SOURCE_AND_EXACT_REPLAY';return result

def source_from_bytes(raw):return json.loads(raw)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();require(not args.output.exists(),'fresh result required')
    result=replay();args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8',newline='\n') as stream:stream.write(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'captured_files':result['captured_files'],'whole_target_checks':len(result['checks']),'qualification_checks':len(result['qualification_replay']['checks']),'own_isolated_tree_removed':result['own_isolated_tree_removed']}),flush=True)
if __name__=='__main__':main()
