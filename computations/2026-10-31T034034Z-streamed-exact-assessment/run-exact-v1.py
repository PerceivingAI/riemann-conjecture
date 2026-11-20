"""Exercise the actual owned exact CLI on a bound new source/proposal pair."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.whole_source.contract import bind_problem, canonical_bytes
from scripts.whole_source.exact import prepare_exact_inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--proposal',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--expected-exit',type=int,choices=(0,1),default=0)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=False)
    revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    inputs = prepare_exact_inputs(bind_problem('retained-t081'),args.source,args.proposal,output/'inputs',
        origin_git_commit=revision,origin_git_dirty=True)
    config = json.loads(inputs['execution'].read_bytes())
    for ref in config['collection']['code_refs']:
        if ref['path'].startswith('scripts/'):
            raw = (ROOT/ref['path']).read_bytes()
            if len(raw)!=ref['size'] or hashlib.sha256(raw).hexdigest()!=ref['sha256']:
                raise ValueError('changed exact code before capture')
            target = output/'captured-code'/ref['path']
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw)
    command = [sys.executable,'-B','-m','scripts.weil_whole_source_split','exact',
        '--problem',str(inputs['problem']),'--source',str(args.source.resolve()),
        '--proposal',str(args.proposal.resolve()),'--execution',str(inputs['execution']),
        '--output-dir',str(output/'exact')]
    start = time.perf_counter()
    with (output/'stdout.txt').open('xb') as stdout,(output/'stderr.txt').open('xb') as stderr:
        result = subprocess.run(command,cwd=ROOT,stdout=stdout,stderr=stderr,check=False)
    receipt = {'argv':command,'exit_code':result.returncode,'expected_exit_code':args.expected_exit,
        'created_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds_hex':(time.perf_counter()-start).hex(),
        'program_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope':'EXACT_CONTROL_CLI_ONLY','production_admission':False}
    for channel in ('stdout','stderr'):
        raw = (output/(channel+'.txt')).read_bytes()
        receipt[channel] = {'path':channel+'.txt','sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)}
    (output/'invocation.json').write_bytes(canonical_bytes(receipt))
    if result.returncode != args.expected_exit:
        print(json.dumps(receipt,sort_keys=True))
        return 2
    report = json.loads((output/'exact/report.json').read_bytes())
    print(json.dumps({'status':'PASS_REAL_EXACT_CLI_OUTCOME','exact_status':report['status'],
        'proof_scope':report['proof_scope'],'exit_code':result.returncode,'invocation':receipt},sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
