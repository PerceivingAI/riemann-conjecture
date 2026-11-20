"""Verify completed finite-control evidence without rerunning its mathematics."""
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
    from scripts.whole_source.receipts import discover_receipts, verify_stage
    from scripts.whole_source.execution import exact_telemetry
    run = args.run_dir.resolve()
    root = run/'code/control-work' if (run/'code').exists() else run/'work'
    report = json.loads((root/'exact/report.json').read_bytes())
    proposal = json.loads((root/'proposal/proposal.json').read_bytes())
    assert report['status'] == 'PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL' and report['proof_scope'] == 'CONTROL_ONLY'
    p_science = []
    for block in proposal['blocks']:
        panels = []
        for panel in block['integer_panels']:
            ref = panel['artifact']
            raw = (root/'proposal'/ref['path']).read_bytes()
            assert len(raw) == ref['size'] and hashlib.sha256(raw).hexdigest() == ref['sha256']
            panels.append({'row': panel['row'], 'column': panel['column'], 'values': json.loads(raw)['values']})
        p_science.append({'parity': block['parity'], 'theta': block['theta'], 'panels': panels})
    fields = ('parity','dimension','goal','width','margin','tau','direction_index','direction_upper',
              'direction_mass','row_margins','transformed_digest','transformed_upper_entries',
              'modular','source_tiles_consumed')
    stages = []
    peak = 0
    for path in discover_receipts(root):
        evidence = verify_stage(path)
        descriptor, plan = evidence['stage'], evidence['plan']
        tasks = [json.loads(line) for line in Path(descriptor['task_file']).read_bytes().splitlines()]
        complete = json.loads((Path(descriptor['result_dir'])/'complete.json').read_bytes())
        receipt = json.loads(path.read_bytes())
        peak = max(peak, receipt['peak_budgeted_memory_bytes'])
        stages.append({'receipt': str(path), 'function': plan.task_function,
                       'task_count': len(tasks), 'operations': [task['operation'] for task in tasks],
                       'workers': plan.workers, 'task_workers': len(complete['worker_pids']),
                       'threads': plan.threads, 'elapsed_seconds': receipt['elapsed_seconds']})
    result = {'status': 'PASS_CONTROL_ONLY_READ_ONLY_TASK_LAYOUT_CLOSEOUT', 'stages': stages,
              'proposal_science': p_science, 'exact_science': [{key: block[key] for key in fields} for block in report['blocks']],
              'assessment': report['assessment'], 'peak_owned_budgeted_bytes': peak,
              'numerical_work_rerun': False, 'full_qualification': False, 'production_admission': False}
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(exact_telemetry(result), stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'stages': len(stages), 'task_count': sum(row['task_count'] for row in stages)}))


if __name__ == '__main__':
    main()
