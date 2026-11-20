"""Interrupt a real 257-of-9912 contribution prefix, then resume exact science."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))


def recovery_module():
    spec = importlib.util.spec_from_file_location('partial_prefix_recovery_helpers', HERE/'qualify-recovery-v1.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def child(args, helper):
    from scripts.whole_source.artifacts import ContributionTask
    problem = helper.bind_problem('retained-t081')
    row = helper.read(args.inputs/'execution.json')['roles']['producer']
    spec = helper.CollectionSpec.from_dict(problem, row['collection'])
    plan = helper.ExecutionPlan.from_dict(row['execution'])
    with helper.CollectionLock.acquire(args.output_dir/'producer', spec, resume=True) as lock:
        with helper.WorkloadExecution(lock, spec, plan, qualification_stop='prefix-committed') as execution:
            store = helper.ChunkStore(lock, spec, attempt_id=execution.attempt_id)
            quantity = spec.quantities[0]
            full = ContributionTask(quantity.key, quantity.rows, quantity.columns, quantity.axes)
            first_task, first = next((task, ref) for task, ref in store._chunk_events()
                if task.quantity == quantity.key and tuple(axis.start for axis in task.axes) == (0, 0, 0))
            assert len(first_task.axes[-1]) == 257
            execution.reduce_prefix(store, full, None, [first])
    raise AssertionError('partial-prefix interruption was not applied')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--_child', action='store_true')
    args = p.parse_args()
    args.inputs, args.baseline, args.output_dir = (path.resolve() for path in (args.inputs, args.baseline, args.output_dir))
    helper = recovery_module()
    if args._child:
        return child(args, helper)
    args.output_dir.mkdir(parents=True, exist_ok=False)
    target = args.output_dir/'collection-run'
    helper.seed(args.baseline, target)
    logs = args.output_dir/'logs'
    logs.mkdir()
    command = [sys.executable, '-B', str(Path(__file__).resolve()), '--_child', '--inputs', str(args.inputs),
               '--baseline', str(args.baseline), '--output-dir', str(target)]
    with (logs/'interrupted.stdout').open('xb') as stdout, (logs/'interrupted.stderr').open('xb') as stderr:
        process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr)
        deadline = time.monotonic()+300
        while True:
            markers = list((target/'producer/attempts').glob('*/barrier-reached.json'))
            if markers:
                marker = markers[0]
                break
            assert process.poll() is None, (logs/'interrupted.stderr').read_text()
            if time.monotonic() > deadline:
                process.kill()
                raise TimeoutError('actual partial-prefix barrier missing')
            time.sleep(0.02)
        observed = helper.read(marker)
        state = helper.read(target/'producer/collection.json')
        node = helper.read(target/'producer'/state['index']['path'])
        assert node['event']['kind'] == 'prefix'
        prefix_ref = node['event']['artifact']
        raw = (target/'producer'/prefix_ref['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == prefix_ref['sha256']
        prefix = json.loads(raw)
        assert prefix['covered'] == prefix['rounds'] == 257
        assert prefix['records'][0][2] != '0x0'
        helper.terminate_owned(observed['pid'])
        process.wait(timeout=120)
        assert process.returncode != 0
    helper.execute(args.inputs, target, 'partial-inner-resume', logs)
    actual, baseline = helper.receipt(target), helper.receipt(args.baseline)
    helper.same_math(baseline, actual)
    helper.write(args.output_dir/'qualification.json', {
        'status': 'PASS_REAL_PARTIAL_INNER_PREFIX_RECOVERY', 'committed_before_interrupt': 257,
        'complete_entry_contributions': 9912, 'prefix_ref_before_interrupt': prefix_ref,
        'actual_barrier': observed, 'interrupted_exit': process.returncode,
        'same_all_six_final_endpoints': True, 'same_all_quantity_seals': True,
        'all_owned_cleanup_verified': actual['all_owned_cleanup_verified'],
        'scope': 'SELECTED_COMPLETE_ARITHMETIC_ONLY', 'full_source': False, 'matrix_positivity': False})
    print('PASS_REAL_PARTIAL_INNER_PREFIX_RECOVERY')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
