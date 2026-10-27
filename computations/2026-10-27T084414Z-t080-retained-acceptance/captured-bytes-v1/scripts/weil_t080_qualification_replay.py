"""Replay and adversarial acceptance of the fixed T=4/5 qualification only."""
import argparse,copy,gzip,hashlib,json,subprocess,sys,tempfile,time
from pathlib import Path
from flint import fmpq
ROOT=Path(__file__).resolve().parents[1]
PROGRAMS=('weil_t080_control_budget.py','verify_t080_control_budget.py','weil_t080_reference_qualification.py','verify_t080_reference_qualification.py','weil_t080_target_declaration.py','verify_t080_target_declaration.py','verify_t080_target_declaration_v2.py')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def call(argv,cwd):
    start=time.perf_counter();p=subprocess.run([sys.executable,'-B',*argv],cwd=cwd,text=True,capture_output=True)
    return {'argv':argv,'exit_code':p.returncode,'elapsed_seconds':time.perf_counter()-start,'stdout':p.stdout,'stderr':p.stderr}

def capture(bundle):
    manifest_path=bundle/'captured-source-v1.json'
    if manifest_path.exists():return load(manifest_path)
    ref=load(bundle/'data/reference-v1.json');decl=load(bundle/'data/target-declaration-v1.json');inputs=load(bundle/'control-budget-inputs-v1.json');control=ROOT/inputs['control_directory'];source=load(control/inputs['control_source'])
    paths=set(ref['imported_project_module_sha256'])|set(decl['imported_project_module_sha256'])|{'pyproject.toml','uv.lock',inputs['old_transform_proof']}
    paths.update('scripts/'+name for name in PROGRAMS)
    for name in ('manifest.json',inputs['control_source'],inputs['control_proposal'],inputs['control_exact_proof']):paths.add((control/name).relative_to(ROOT).as_posix())
    for record in source['matrices'].values():paths.add((control/record['path']).relative_to(ROOT).as_posix())
    for name in ('qualification-inputs-v1.json','control-budget-inputs-v1.json','parameter-selection-inputs-v1.json','reference-contract-v1.md','target-source-error-contract-v1.md'):paths.add((bundle/name).relative_to(ROOT).as_posix())
    folder=bundle/'captured-inputs-v1';folder.mkdir(exist_ok=False);records=[]
    for relative in sorted(paths):
        raw=(ROOT/relative).read_bytes();target=folder/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        records.append({'destination':relative,'stored':target.relative_to(bundle).as_posix(),'bytes':len(raw),'sha256':sha(raw)})
    manifest={'format':'t080-qualification-captured-closure-v1','files':records};manifest_path.write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf-8');return manifest

def replay(bundle,output):
    manifest=capture(bundle);relative=bundle.relative_to(ROOT);result={'format':'t080-qualification-isolated-replay-v1','captured_files':len(manifest['files']),'steps':[],'checks':{},'target_low_coupling_matrix_computed':False,'target_positivity_proved':False}
    with tempfile.TemporaryDirectory(prefix='t080_qualification_') as td:
        isolated=Path(td)
        for item in manifest['files']:
            raw=(bundle/item['stored']).read_bytes()
            if sha(raw)!=item['sha256'] or len(raw)!=item['bytes']:raise ValueError('captured closure changed')
            dest=isolated/item['destination'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        (isolated/relative/'data').mkdir(parents=True,exist_ok=True)
        def b(name):return (relative/name).as_posix()
        tasks=[['scripts.weil_t080_control_budget','--inputs',b('control-budget-inputs-v1.json'),'--output',b('data/control-budget-v1.json')],['scripts.verify_t080_control_budget','--inputs',b('control-budget-inputs-v1.json'),'--source',b('data/control-budget-v1.json'),'--output',b('data/control-budget-audit-v1.json')],['scripts.weil_t080_reference_qualification','--inputs',b('qualification-inputs-v1.json'),'--output',b('data/reference-v1.json')],['scripts.verify_t080_reference_qualification','--inputs',b('qualification-inputs-v1.json'),'--source',b('data/reference-v1.json'),'--output',b('data/reference-audit-v1.json')],['scripts.weil_t080_target_declaration','--inputs',b('parameter-selection-inputs-v1.json'),'--reference-audit',b('data/reference-audit-v1.json'),'--control-audit',b('data/control-budget-audit-v1.json'),'--output',b('data/target-declaration-v1.json')],['scripts.verify_t080_target_declaration_v2','--inputs',b('parameter-selection-inputs-v1.json'),'--source',b('data/target-declaration-v1.json'),'--reference-audit',b('data/reference-audit-v1.json'),'--control-audit',b('data/control-budget-audit-v1.json'),'--output',b('data/target-declaration-audit-v2.json')]]
        for task in tasks:
            step=call(['-m',*task],isolated);result['steps'].append(step)
            if step['exit_code']:raise ValueError('isolated qualifier failed '+task[0]+' '+step['stdout']+step['stderr'])
        for name in ('control-budget-v1.json','control-budget-audit-v1.json','reference-v1.json','reference-audit-v1.json','target-declaration-v1.json','target-declaration-audit-v2.json'):
            actual=(bundle/'data'/name).read_bytes();fresh=(isolated/relative/'data'/name).read_bytes()
            if fresh!=actual:raise ValueError('scientific byte mismatch '+name)
            result['checks'][name]=sha(actual)
        control=load(bundle/'data/control-budget-v1.json')
        for parity,row in control['parities'].items():
            for kind,item in row['relative_caps'].items():
                fresh=(isolated/relative/'data'/item['witness']).read_bytes()
                if sha(fresh)!=item['sha256']:raise ValueError('budget proof witness mismatch')
                result['checks'][parity+'-'+kind]=sha(fresh)
    result['own_isolated_tree_removed']=not isolated.exists();result['status']='PASS_CAPTURED_QUALIFICATION_REPLAY'
    return result

def negatives(bundle,output):
    cases=output.parent/(output.stem+'-cases');cases.mkdir(exist_ok=False);decl=load(bundle/'data/target-declaration-v1.json');ref=load(bundle/'data/reference-v1.json');attempts=[]
    badref=copy.deepcopy(ref);badref['infinite_tail_upper']='-1'
    badkernel=copy.deepcopy(decl);badkernel['kernel_coefficients'][0]=str(fmpq(badkernel['kernel_coefficients'][0])+1)
    badloss=copy.deepcopy(decl);badloss['order_selection_ladder'][-1]['Lambda_upper']='0';badloss['complete_model_error_upper']='0'
    for name,packet,kind,error in [('underpaid_frequency_infinity',badref,'reference','dishonest infinite tail'),('wrong_signed_polar_kernel',badkernel,'declaration','incorrect complete formal kernel coefficients'),('unpaid_complete_model_error',badloss,'declaration','model allowance')]:
        path=cases/(name+'.json');path.write_text(json.dumps(packet,sort_keys=True,indent=2)+'\n',encoding='utf-8');audit=cases/(name+'.audit.json')
        if kind=='reference':argv=['-m','scripts.verify_t080_reference_qualification','--inputs',str(bundle/'qualification-inputs-v1.json'),'--source',str(path),'--output',str(audit)]
        else:argv=['-m','scripts.verify_t080_target_declaration_v2','--inputs',str(bundle/'parameter-selection-inputs-v1.json'),'--source',str(path),'--reference-audit',str(bundle/'data/reference-audit-v1.json'),'--control-audit',str(bundle/'data/control-budget-audit-v1.json'),'--output',str(audit)]
        step=call(argv,ROOT)
        if step['exit_code']!=2 or audit.exists() or error not in step['stdout']:raise ValueError('wrong mathematical rejection '+name+' '+str(step))
        step.update({'name':name,'packet_sha256':sha(path.read_bytes()),'mathematical_error_expected':error,'success_file_emitted':False});(cases/(name+'.run.json')).write_text(json.dumps(step,sort_keys=True,indent=2)+'\n',encoding='utf-8');attempts.append(step)
    return {'format':'t080-qualification-negative-controls-v1','status':'PASS_THREE_MATHEMATICAL_REJECTIONS','cases':attempts,'target_low_coupling_matrix_computed':False,'target_positivity_proved':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--negative-controls',action='store_true');args=p.parse_args();bundle=args.bundle.resolve();output=args.output.resolve()
    if output.exists():raise FileExistsError(output)
    if not bundle.is_relative_to(ROOT) or load(bundle/'qualification-inputs-v1.json')['support']!='4/5':raise ValueError('unsupported fixed qualification bundle')
    result=negatives(bundle,output) if args.negative_controls else replay(bundle,output)
    output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':result['status'],'target_low_coupling_matrix_computed':False,'target_positivity_proved':False}),flush=True)
if __name__=='__main__':main()
