"""Read-only closeout of post-bind input rejection, including prelaunch refusal."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    from scripts.whole_source.contract import canonical_bytes
    from scripts.whole_source.execution import _write
    from scripts.whole_source.receipts import discover_receipts, verify_stage
    rows = []
    for mode in ('original-source', 'normalized-transform'):
        case = args.run_dir.resolve()/mode
        failure = json.loads((case/'exact/failure.json').read_bytes())
        assert not (case/'exact/report.json').exists()
        assert 'invalid regular artifact' in failure['error'] or mode == 'original-source'
        descriptor = json.loads((case/'inputs/operands.json').read_bytes())
        if mode == 'original-source':
            manifest = json.loads((case/'manufactured/original-source/source-manifest.json').read_bytes())
            ref = manifest['tiles'][0]['artifact']
            changed = case/'manufactured/original-source'/ref['path']
        else:
            ref = next(iter(descriptor['blocks'][0]['panels'].values()))
            changed = ROOT/ref['path']
        assert hashlib.sha256(changed.read_bytes()).hexdigest() != ref['sha256']
        stages, failed = [], 0
        for path in discover_receipts(case):
            value = json.loads(path.read_bytes())
            assert value['worker_cleanup_verified'] is True
            if value['exit_code'] == 0:
                verify_stage(path)
            else:
                failed += 1
            stages.append({'path': str(path), 'exit_code': value['exit_code']})
        if mode == 'original-source':
            assert len(stages) == 2 and failed == 1
            boundary = 'owned first-contraction consumer'
        else:
            assert not stages and not list((case/'exact').rglob('*-stage.json'))
            boundary = 'raw runtime-input capture before owned stage launch'
        rows.append({'case': mode, 'failure': failure['error'], 'rejection_boundary': boundary,
                     'no_final_report': True, 'cleanup_verified': True, 'stages': stages})
    report = {'status': 'PASS_CONTROL_ONLY_POST_BIND_INPUT_REJECTION', 'cases': rows,
              'numerical_work_rerun': False, 'original_qualifier_count_assertion_was_wrong': True,
              'full_qualification': False, 'production_admission': False}
    _write(args.output, canonical_bytes(report))
    print(json.dumps({'status': report['status'], 'cases': len(rows), 'numerical_work_rerun': False}))


if __name__ == '__main__':
    main()
