"""Qualify interruption and corruption at exact owned-wave publication seams."""
from pathlib import Path
import argparse
import hashlib
import json
import runpy
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--origin-commit', required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    from scripts.whole_source import resources, exact, exact_tasks, task_groups
    from scripts.whole_source.contract import ContractError, canonical_bytes
    from scripts.whole_source.execution import WorkloadExecution, exact_telemetry, _write
    from scripts.whole_source.receipts import discover_receipts, verify_stage
    factory = runpy.run_path(str(Path(__file__).with_name('verify-variant-snapshots-v1.py')))['manufactured_inputs']
    allocator = resources.auto_plan
    def allocate(template, *, parallel, memory_mib=None, helper_root=ROOT):
        return allocator(template, parallel=parallel, cpus=2, memory_mib=2048, helper_root=helper_root)
    origin = {'origin_git_commit': args.origin_commit, 'origin_git_dirty': True}
    results = []
    for mode in ('before-group-commit', 'after-group-commit', 'changed-committed-panel'):
        case = output/mode
        with patch.object(resources, 'auto_plan', allocate):
            problem, source, proposal, _ = factory(case/'manufactured', origin)
            inputs = exact.prepare_exact_inputs(problem, source.path, proposal, case/'exact-inputs', **origin)
        seal, stage = exact_tasks.seal_group, WorkloadExecution.run_stage
        reached, protected = [], {}
        def commit(lock, execution, name, context, outputs):
            if name == 'first' and mode == 'before-group-commit':
                reached.append(name)
                raise OSError('CONTROL_ONLY interruption before group commit')
            record = seal(lock, execution, name, context, outputs)
            if name == 'first' and mode == 'after-group-commit':
                reached.append(name)
                for path in (lock.root/'seals').iterdir():
                    protected[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
                raise OSError('CONTROL_ONLY interruption after group commit')
            return record
        def execute(execution, name, tasks):
            if name == 'second' and mode == 'changed-committed-panel':
                for path in (execution.collection_lock.root/'seals').iterdir():
                    value = json.loads(path.read_bytes())
                    if value.get('header', {}).get('family') == 'J':
                        path.write_bytes(b'CONTROL_ONLY changed committed first contraction')
                        reached.append(name)
                        break
                assert reached
            return stage(execution, name, tasks)
        with patch.object(exact_tasks, 'seal_group', commit), patch.object(WorkloadExecution, 'run_stage', execute):
            try:
                exact.run_exact(inputs['problem'], source.path, proposal, inputs['execution'], case/'exact')
            except (ContractError, OSError, RuntimeError) as error:
                failure = type(error).__name__+': '+str(error)
            else:
                raise AssertionError('deliberate dependency boundary failure was accepted')
        assert reached and not (case/'exact/report.json').exists()
        assert all(hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest for path, digest in protected.items())
        groups = []
        for path in (case/'exact/collection/seals').iterdir():
            value = json.loads(path.read_bytes()) if mode != 'changed-committed-panel' or path.read_bytes().startswith(b'{') else {}
            if value.get('format') == 'whole-source-task-group-v1':
                groups.append(value['context']['operation'])
        assert ('first' in groups) is (mode != 'before-group-commit')
        assert 'second' not in groups and 'reduce' not in groups
        receipts = []
        for path in discover_receipts(case):
            value = json.loads(path.read_bytes())
            assert value['worker_cleanup_verified'] is True
            if value['exit_code'] == 0:
                verify_stage(path)
            else:
                assert mode == 'changed-committed-panel'
            receipts.append({'path': str(path), 'exit_code': value['exit_code']})
        results.append({'case': mode, 'failure': failure, 'committed_operations': sorted(groups),
                        'preserved_immutable_files': len(protected), 'receipts': receipts,
                        'no_final_report': True, 'cleanup_verified': True})
    result = {'status': 'PASS_CONTROL_ONLY_DEPENDENCY_FAILURE_BOUNDARIES', 'cases': results,
              'full_qualification': False, 'production_admission': False}
    _write(output/'verification.json', canonical_bytes(exact_telemetry(result)))
    print(json.dumps({'status': result['status'], 'cases': len(results)}))


if __name__ == '__main__':
    main()
