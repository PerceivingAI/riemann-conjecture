"""Execute explicitly selected scalar or complete fresh reference qualification."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.whole_source.contract import bind_problem, canonical_bytes
from scripts.whole_source import retention


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=('scalar','full'),required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=False)
    problem = bind_problem('retained-t081')
    origin = {'origin_git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'origin_git_dirty':True}
    started = time.monotonic_ns()
    if args.mode=='scalar':
        from scripts.whole_source.pipeline import prepare_source_inputs,_bind
        prepared = prepare_source_inputs(problem,output/'inputs',tile_modes=32,**origin)
        _,_,roles = _bind(prepared['problem'],prepared['execution'],ROOT)
        result = retention.run_premises(problem,*roles['analytic'],output/'premises')
        receipt = {'mode':args.mode,'status':result['status'],'wall_nanoseconds':time.monotonic_ns()-started,
            'argv':[sys.executable,*sys.argv],'program_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'production_admission':False}
    else:
        prepared = retention.prepare_inputs(problem,output/'inputs',**origin)
        command = [sys.executable,'-B','-m','scripts.weil_whole_source_split','run',
            '--problem',str(prepared['problem']),'--execution',str(prepared['execution']),
            '--output-dir',str(output/'run')]
        with (output/'stdout.txt').open('xb') as stdout,(output/'stderr.txt').open('xb') as stderr:
            result = subprocess.run(command,cwd=ROOT,stdout=stdout,stderr=stderr,check=False)
        receipt = {'mode':args.mode,'exit_code':result.returncode,'argv':command,
            'wall_nanoseconds':time.monotonic_ns()-started,
            'program_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'production_admission':False}
        for name in ('stdout','stderr'):
            raw = (output/(name+'.txt')).read_bytes()
            receipt[name] = {'path':name+'.txt','sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)}
    (output/'invocation.json').write_bytes(canonical_bytes(receipt))
    print(json.dumps(receipt,sort_keys=True))
    return 0 if args.mode=='scalar' else result.returncode

if __name__=='__main__':
    raise SystemExit(main())
