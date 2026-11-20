"""Exercise real scalar rejection cases or replay the captured scalar-only closure."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = Path(__file__).resolve().parent
REL = BUNDLE.relative_to(ROOT)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(value,indent=2,sort_keys=True)+'\n')


def run(command, cwd):
    before = time.perf_counter()
    process = subprocess.run(command,cwd=cwd,capture_output=True,text=True)
    return {'argv':command,'elapsed_seconds':time.perf_counter()-before,
            'exit_code':process.returncode,'stdout':process.stdout,'stderr':process.stderr}


def controls(output):
    source = json.loads((BUNDLE/'data/source-v1.json').read_bytes())
    cases = []
    for name in ('added-prime-norm','complete-leakage','canonical-polar','terminal-infinity',
                 'small-geometric-cutoff','model-discrepancy','floating-math'):
        packet = copy.deepcopy(source)
        if name=='added-prime-norm':
            packet['transfer']['added_prime_norm']={'lower':'0','upper':'1'}
            expected='native containment failed: transfer added_prime_norm'
        elif name=='complete-leakage':
            packet['reference']['selected']['leakage']={'lower':'0','upper':'0'}
            expected='native containment failed: N=9072 leakage'
        elif name=='canonical-polar':
            packet['residual']['coefficients'][0]='0'
            expected='canonical exact residual coefficients disagree'
        elif name=='terminal-infinity':
            packet['frequency']['inverse_weight_step_uppers'][-1]='0'
            expected='false rational upper: frequency step 59'
        elif name=='small-geometric-cutoff':
            packet['N'],packet['M']=826,1652
            expected='geometric-invalid leakage cutoff'
        elif name=='model-discrepancy':
            packet['residual']['ladder'][-1]['Lambda_upper']='0'
            expected='incorrect residual Lambda upper'
        else:
            packet['beta']=3.28
            expected='nonexact JSON number'
        folder=output.parent/(output.stem+'-cases')/name
        source_path, audit_path=folder/'source.json',folder/'audit.json'
        save(source_path,packet)
        receipt=run([sys.executable,'-B',str(BUNDLE/'verify-reference-v2.py'),
                     '--inputs',str(BUNDLE/'inputs-v1.json'),'--source',str(source_path),
                     '--output',str(audit_path)],ROOT)
        try:
            result=json.loads(receipt['stdout'])
        except json.JSONDecodeError:
            raise ValueError('control did not reach a substantive native rejection: '+name)
        if not (receipt['exit_code']==2 and result.get('status')=='REJECTED'
                and expected in result.get('error','') and not audit_path.exists()):
            raise ValueError('incorrect negative-control result '+name+': '+str(receipt))
        save(folder/'receipt.json',receipt)
        cases.append({'name':name,'expected':expected,'observed':result['error'],
                      'exit_code':receipt['exit_code'],'no_pass_file':True,
                      'source_sha256':sha(source_path),'receipt_sha256':sha(folder/'receipt.json')})
    return {'format':'t1-scalar-mathematical-controls-v1','status':'PASS',
            'positive_control_audit_sha256':sha(BUNDLE/'data/audit-v2.json'),
            'case_count':len(cases),'cases':cases,'target_matrix_computed':False}


def replay(capture_path):
    capture=json.loads(capture_path.read_bytes())
    receipts,comparisons=[],[]
    with tempfile.TemporaryDirectory(prefix='t1_scalar_replay_') as directory:
        root=Path(directory)
        for entry in capture['destinations']:
            original=(BUNDLE/entry['captured_path']).resolve()
            destination=(root/entry['destination']).resolve()
            if not original.is_relative_to(BUNDLE) or not destination.is_relative_to(root):
                raise ValueError('unsafe captured destination')
            if sha(original)!=entry['sha256']:
                raise ValueError('captured bytes changed')
            destination.parent.mkdir(parents=True,exist_ok=True)
            with destination.open('xb') as stream:
                stream.write(original.read_bytes())
        child=root/REL
        folder=child/'fresh-results'
        folder.mkdir()
        commands=[('source-v1.json',[sys.executable,'-B',str(child/'qualify-reference-v1.py'),
                    '--inputs',str(child/'inputs-v1.json'),'--output',str(folder/'source-v1.json')]),
                  ('audit-v2.json',[sys.executable,'-B',str(child/'verify-reference-v2.py'),
                    '--inputs',str(child/'inputs-v1.json'),'--source',str(folder/'source-v1.json'),
                    '--output',str(folder/'audit-v2.json')]),
                  ('cost-assessment-v1.json',[sys.executable,'-B',str(child/'assess-cost-v1.py'),
                    '--inputs',str(child/'inputs-v1.json'),'--source',str(folder/'source-v1.json'),
                    '--audit',str(folder/'audit-v2.json'),'--output',str(folder/'cost-assessment-v1.json')])]
        for name,command in commands:
            if (folder/name).exists():
                raise ValueError('expected target output leaked into replay')
            receipt=run(command,root)
            receipts.append(receipt)
            if receipt['exit_code']!=0:
                raise ValueError('captured scalar replay failed: '+str(receipt))
            expected=BUNDLE/'data'/name
            actual=folder/name
            if actual.read_bytes()!=expected.read_bytes():
                raise ValueError('scientific bytes differ: '+name)
            comparisons.append({'name':name,'sha256':sha(actual),'byte_identical':True})
        temp_name=str(root)
    if Path(temp_name).exists():
        raise ValueError('owned temporary replay tree remained')
    return {'format':'t1-captured-scalar-replay-v1','status':'PASS',
            'capture_sha256':sha(capture_path),'destinations':len(capture['destinations']),
            'comparisons':comparisons,'receipts':receipts,'owned_tree_removed':True,
            'expected_outputs_withheld':True,'target_matrix_computed':False,
            'trust':'captured source/input isolation; shared installed Python/FLINT, not an OS sandbox'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('controls','replay'),required=True)
    p.add_argument('--capture',type=Path)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.mode=='replay' and args.capture is None:
        p.error('replay needs --capture')
    result=controls(args.output) if args.mode=='controls' else replay(args.capture)
    save(args.output,result)
    print(json.dumps({'mode':args.mode,'status':result['status'],
                      'cases_or_comparisons':result.get('case_count',len(result.get('comparisons',[])))}))


if __name__=='__main__':
    main()
