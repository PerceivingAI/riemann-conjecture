"""Run bounded nonproof observations with typed, path-free retained streams."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.t081_resource_supervisor import Execution, ROOT
from execution_resources_v2 import MIB, resolve_resources


EXACT_MODES = ('exact', 'proposal', 'control')
NATIVE_MODES = ('prepare', 'images', 'frequency', 'transport', 'aggregate')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=EXACT_MODES + NATIVE_MODES, required=True)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--memory-mib', type=int, required=True)
    parser.add_argument('--threads', type=int)
    parser.add_argument('--cpus', type=int)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error('the output directory must not exist')
    inputs = json.loads(args.inputs.read_bytes())
    for binding in inputs['bindings'].values():
        with (ROOT / binding['path']).open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != binding['sha256']:
                raise ValueError('changed bound input')
    budget = resolve_resources(memory_mib=args.memory_mib, threads=args.threads, cpus=args.cpus,
                               required_bytes=512 * MIB)
    program = 'probe_exact_workspace_v2.py' if args.mode in EXACT_MODES else 'probe_native_checkpoint_v1.py'
    dimensions = (5, 9) if args.mode == 'control' else (5564,)
    with Execution(args.output_dir, budget, identity=('t1-bounded-probe-v2', '1', dimensions)) as execution:
        execution.run(args.mode, ROOT / 'scripts' / program,
                      ['--mode', args.mode, '--inputs', args.inputs.resolve(),
                       '--output', (args.output_dir / 'result.json').resolve()], kind='fixture',
                      environment={'BOUNDED_CPU_BUDGET': str(budget['cpu_budget'])})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
