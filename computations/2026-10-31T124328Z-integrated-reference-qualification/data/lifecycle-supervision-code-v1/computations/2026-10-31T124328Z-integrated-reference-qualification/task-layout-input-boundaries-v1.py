"""Reject independently changed source/normalized inputs after the actual parent bind."""
from pathlib import Path
import argparse
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
    from scripts.whole_source import resources, exact
    from scripts.whole_source.contract import ContractError, canonical_bytes
    from scripts.whole_source.execution import _write
    from scripts.whole_source.receipts import discover_receipts, verify_stage
    factory = runpy.run_path(str(Path(__file__).with_name('verify-variant-snapshots-v1.py')))['manufactured_inputs']
    allocator = resources.auto_plan
    def allocate(template, *, parallel, memory_mib=None, helper_root=ROOT):
        return allocator(template, parallel=parallel, cpus=2, memory_mib=2048, helper_root=helper_root)
    origin = {'origin_git_commit': args.origin_commit, 'origin_git_dirty': True}
    rows = []
    for mode in ('original-source', 'normalized-transform'):
        case = output/mode
        with patch.object(resources, 'auto_plan', allocate):
            problem, source, proposal, _ = factory(case/'manufactured', origin)
            inputs = exact.prepare_exact_inputs(problem, source.path, proposal, case/'inputs', **origin)
        run = exact._run_bound_exact
        bindings = []
        def corrupt(root, destination, binding):
            bindings.append(1)
            descriptor = binding[2]
            path = (source.path.parent/source.document['tiles'][0]['artifact']['path'] if mode == 'original-source' else
                    root/next(iter(descriptor['blocks'][0]['panels'].values()))['path'])
            path.write_bytes(b'CONTROL_ONLY changed independent operand after actual parent bind')
            return run(root, destination, binding)
        with patch.object(exact, '_run_bound_exact', corrupt):
            try:
                exact.run_exact(inputs['problem'], source.path, proposal, inputs['execution'], case/'exact')
            except (ContractError, OSError, RuntimeError) as error:
                failure = type(error).__name__+': '+str(error)
            else:
                raise AssertionError('changed independent operand was accepted')
        assert len(bindings) == 1 and not (case/'exact/report.json').exists()
        stages = []
        failed = 0
        for receipt_path in discover_receipts(case):
            receipt = json.loads(receipt_path.read_bytes())
            assert receipt['worker_cleanup_verified'] is True
            if receipt['exit_code'] == 0:
                verify_stage(receipt_path)
            else:
                failed += 1
            stages.append({'path': str(receipt_path), 'exit_code': receipt['exit_code']})
        assert failed == 1
        rows.append({'case': mode, 'failure': failure, 'actual_parent_bindings': len(bindings),
                     'no_final_report': True, 'cleanup_verified': True, 'stages': stages})
    report = {'status': 'PASS_CONTROL_ONLY_POST_BIND_INPUT_REJECTION', 'cases': rows,
              'full_qualification': False, 'production_admission': False}
    _write(output/'verification.json', canonical_bytes(report))
    print(json.dumps({'status': report['status'], 'cases': len(rows)}))


if __name__ == '__main__':
    main()
