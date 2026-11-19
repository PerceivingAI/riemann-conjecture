"""Run a stage after READY/GO and emit only typed failure and profile records."""
from __future__ import annotations

import argparse
import builtins
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import sys
import time


HERE = Path(__file__).resolve().parent
STAGES = {
    'source': ('residual_matrices', 'combined_square', 'kernel_step', 'source'),
    'audit': ('frozen_inputs', 'replay_declaration', 'residual_kernel', 'validate_model_allowance',
              'validate_weights', 'residual_outputs', 'residual_blocks', 'arithmetic_blocks',
              'complete_arithmetic_squared', 'frequency_kernels', 'reconstruct', 'check_matrix'),
    'exact': (),
    'fixture': (),
}
_PROFILE = 't081-budgeted-stage-profile-v2'
_TIMING = ('inclusive_wall_seconds', 'exclusive_wall_seconds', 'cpu_seconds')
_MEMORY = ('committed_bytes', 'working_set_bytes', 'peak_working_set_bytes', 'peak_committed_bytes')


def _failure(exception):
    kind = type(exception).__name__
    if getattr(builtins, kind, None) is not type(exception) and kind != 'ContractError':
        kind = 'StageError'
    error = {'type': kind}
    if isinstance(exception, OSError):
        for key in ('errno', 'winerror'):
            value = getattr(exception, key, None)
            if type(value) is int and -(1 << 31) <= value < 1 << 32:
                error[key] = value
    print('T081_DIAGNOSTIC ' + json.dumps(error, sort_keys=True), file=sys.stderr, flush=True)
    code = 130 if isinstance(exception, KeyboardInterrupt) else 75 if isinstance(exception, MemoryError) else 1
    return code, error


def _phase_totals(events, phases):
    records = events.report()['phases']
    totals = {}
    for phase in phases:
        row = records.get(phase)
        if type(row) is not dict:
            continue
        calls = row.get('calls')
        timing = {key: row.get(key) for key in _TIMING}
        if type(calls) is int and 0 <= calls < 1 << 63 and all(
            type(value) in (int, float) and 0 <= value < 1 << 63 and math.isfinite(value)
            for value in timing.values()
        ):
            totals[phase] = {'calls': calls, **timing}
    return totals


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's default error can echo physical paths or private arguments.
        raise SystemExit(2)


def main():
    parser = _Parser(prog='stage_worker_v3.py', description=__doc__)
    parser.add_argument('--program', type=Path, required=True)
    parser.add_argument('--program-sha256', required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--config-sha256', required=True)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--kind', choices=tuple(STAGES), required=True)
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if any(re.fullmatch(r'[0-9a-f]{64}', digest) is None
           for digest in (args.program_sha256, args.config_sha256)):
        raise ValueError('invalid stage worker digest')

    # The Windows venv launcher can have a different PID from this interpreter.
    print('T081_READY ' + json.dumps({'pid': os.getpid(), 'config_sha256': args.config_sha256}), flush=True)
    if sys.stdin.readline().strip() != 'GO':
        raise RuntimeError('supervisor did not authorize the budgeted stage')
    raw = args.config.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.config_sha256:
        raise ValueError('execution configuration changed')
    config = json.loads(raw)
    with args.program.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != args.program_sha256:
            raise ValueError('numerical program changed')

    sys.path.insert(0, str(HERE))
    from resource_limits_v1 import apply_posix_memory_limit

    containment = {'mechanism': 'owned Windows job installed before GO'}
    if os.name == 'posix':
        containment = apply_posix_memory_limit(config['memory_budget_bytes'])
        if hasattr(os, 'sched_setaffinity'):
            available = sorted(os.sched_getaffinity(0))
            os.sched_setaffinity(0, set(available[:config['cpu_budget']]))

    from flint import ctx
    import execution_events_v1 as events

    sys.path.insert(0, str(args.program.parent))
    spec = importlib.util.spec_from_file_location('t081_owned_stage', args.program)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    ctx.threads = config['native_threads']
    phases = STAGES[args.kind]
    events.wrap(module, phases)
    rest = args.arguments[1:] if args.arguments[:1] == ['--'] else args.arguments
    sys.argv = [str(args.program), *rest]
    wall, cpu = time.monotonic(), time.process_time()
    events.emit('program_started', kind=args.kind, threads=ctx.threads)
    error = None
    try:
        code = int(module.main() or 0)
    except BaseException as exception:
        code, error = _failure(exception)

    payload = {
        'format': _PROFILE, 'kind': args.kind, 'exit_code': code, 'error': error,
        'program_sha256': args.program_sha256,
        'wall_seconds': time.monotonic() - wall, 'cpu_seconds': time.process_time() - cpu,
        'native_threads': ctx.threads, 'precision': ctx.prec, 'containment': containment,
        'phases': _phase_totals(events, phases),
        'timing_note': 'inclusive includes nested calls; exclusive subtracts wrapped children; CPU is current process only',
    }
    if os.name == 'nt':
        from resource_limits_v1 import windows_resource_snapshot

        process = windows_resource_snapshot()['process']
        payload['process_memory'] = None if process is None else {
            key: process[key] for key in _MEMORY if type(process.get(key)) is int
        }

    sys.path.insert(0, str(HERE.parents[2]))
    from scripts.whole_source.storage import guarded_open

    with guarded_open(args.profile) as handle:
        raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf-8')
        if handle.write(raw) != len(raw):
            raise OSError('short stage profile write')
    events.emit('program_finished', kind=args.kind, exit_code=code, wall_seconds=payload['wall_seconds'])
    return code


if __name__ == '__main__':
    try:
        exit_code = main()
    except SystemExit as error:
        exit_code = error.code if type(error.code) is int else int(error.code is not None)
        if exit_code:
            _failure(error)
    except BaseException as error:
        exit_code, _ = _failure(error)
    raise SystemExit(exit_code)
