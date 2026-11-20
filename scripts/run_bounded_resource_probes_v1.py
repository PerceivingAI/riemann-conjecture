"""Run named contained resource observations under existing owned supervision."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RETAINED=ROOT/'computations/2026-10-29T013929Z-t1-execution-allocation/run-probes-v1.py'
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['exact','proposal','prepare','images','frequency','transport','aggregate'],required=True)
    p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--memory-mib',type=int,required=True);p.add_argument('--threads',type=int);p.add_argument('--cpus',type=int)
    args=p.parse_args()
    if args.output_dir.exists():raise FileExistsError(args.output_dir)
    inputs=json.loads(args.inputs.read_bytes())
    for b in inputs['bindings'].values():
        if hashlib.sha256((ROOT/b['path']).read_bytes()).hexdigest()!=b['sha256']:raise ValueError('changed bound input '+b['path'])
    spec=importlib.util.spec_from_file_location('retained_resource_probe_supervision',RETAINED);runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    budget=runner.policy.resolve_resources(memory_mib=args.memory_mib,threads=args.threads,cpus=args.cpus,required_bytes=512*runner.policy.MIB)
    name='probe_exact_workspace_v1.py' if args.mode in ('exact','proposal') else 'probe_native_checkpoint_v1.py'
    program=ROOT/'scripts'/name
    with runner.ProbeExecution(args.output_dir,budget) as execution:
        execution.run(args.mode,program,['--mode',args.mode,'--inputs',args.inputs.resolve(),'--output',(args.output_dir/'result.json').resolve()],kind='fixture',environment={'BOUNDED_CPU_BUDGET':str(budget['cpu_budget'])})
    return 0
if __name__=='__main__':raise SystemExit(main())
