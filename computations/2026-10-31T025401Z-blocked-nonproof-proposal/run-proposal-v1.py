"""Exercise the real fresh nonproof proposer against a bound scientific source."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.whole_source.contract import bind_problem, canonical_bytes
from scripts.whole_source.proposal import prepare_proposal_inputs, read_proposal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--panel-size',type=int,default=2)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=False)
    revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    inputs = prepare_proposal_inputs(bind_problem('retained-t081'),args.source,output/'inputs',
        origin_git_commit=revision,origin_git_dirty=True,panel_size=args.panel_size)
    config = json.loads(inputs['execution'].read_bytes())
    for ref in config['phases']['native']['collection']['code_refs']:
        if ref['path'].startswith('scripts/'):
            raw = (ROOT/ref['path']).read_bytes()
            if len(raw) != ref['size'] or hashlib.sha256(raw).hexdigest() != ref['sha256']:
                raise ValueError('changed proposal code capture')
            destination = output/'captured-code'/ref['path']
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(raw)
    command = [sys.executable,'-B','-m','scripts.weil_whole_source_split','propose',
        '--problem',str(inputs['problem']),'--source',str(args.source.resolve()),
        '--execution',str(inputs['execution']),'--output-dir',str(output/'proposal')]
    started = time.perf_counter()
    with (output/'stdout.txt').open('xb') as stdout,(output/'stderr.txt').open('xb') as stderr:
        result = subprocess.run(command,cwd=ROOT,stdout=stdout,stderr=stderr,check=False)
    receipt = {'argv':command,'exit_code':result.returncode,
        'created_utc':datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds_hex':(time.perf_counter()-started).hex(),
        'program_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'environment':{'python':platform.python_version(),'platform':platform.platform(),
            'versions':{name:importlib.metadata.version(name) for name in ('python-flint','numpy','scipy')}},
        'scope':'NONPROOF_PROPOSAL_ONLY','matrix_positivity':False,'production_admission':False}
    for label in ('stdout','stderr'):
        raw = (output/(label+'.txt')).read_bytes()
        receipt[label] = {'path':label+'.txt','sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)}
    (output/'invocation.json').write_bytes(canonical_bytes(receipt))
    if result.returncode == 0:
        core = read_proposal(output/'proposal/proposal.json',bind_problem('retained-t081'),config['source']['manifest'])
        print(json.dumps({'status':'PASS_REAL_NONPROOF_PROPOSAL_CLI',
            'entries':sum(block['dimension']**2 for block in core['blocks']),
            'control':core['source_control'],'invocation':receipt},sort_keys=True))
    else:
        print(json.dumps(receipt,sort_keys=True))
    return result.returncode

if __name__ == '__main__':
    raise SystemExit(main())
