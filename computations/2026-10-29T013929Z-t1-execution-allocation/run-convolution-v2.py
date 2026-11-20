"""Contained structured contraction; same retained neutral worker and policy."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--memory-mib', type=int, default=1536)
    parser.add_argument('--threads', type=int, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    spec = importlib.util.spec_from_file_location('structured_probe_runner_v1', HERE/'run-probes-v1.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    inputs = json.loads(args.inputs.read_bytes())
    assert inputs['product']['algorithm'] == 'convolution'
    for binding in inputs['bindings'].values():
        if hashlib.sha256((ROOT/binding['path']).read_bytes()).hexdigest() != binding['sha256']:
            raise ValueError('changed measurement dependency: '+binding['path'])
    budget = runner.policy.resolve_resources(memory_mib=args.memory_mib, threads=args.threads,
                                             required_bytes=512*runner.policy.MIB)
    with runner.ProbeExecution(args.output_dir,budget) as execution:
        execution.run('convolution',HERE/'probe-convolution-v1.py',
            ['--inputs',args.inputs.resolve(),'--output',(args.output_dir/'result.json').resolve()],
            kind='fixture')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
