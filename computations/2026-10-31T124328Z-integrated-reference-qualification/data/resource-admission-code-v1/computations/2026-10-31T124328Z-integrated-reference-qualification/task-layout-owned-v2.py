"""Version2: retain real finite-control timing through exact telemetry serialization."""
from pathlib import Path
from fractions import Fraction
from dataclasses import asdict
import argparse
import hashlib
import json
import runpy
import shutil
import subprocess
import sys
import time
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code-root', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--origin-commit', required=True)
    parser.add_argument('--cpus', type=int, default=2)
    parser.add_argument('--copy-code', action='store_true')
    parser.add_argument('--negative-controls', action='store_true')
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    root = args.code_root.resolve()
    if args.copy_code:
        captured = output/'code'
        shutil.copytree(root, captured)
        root = captured
        work = root/'control-work'
    else:
        work = output/'work'
    sys.path.insert(0, str(root))
    from scripts.whole_source import proposal, exact, resources, controls
    from scripts.whole_source.contract import bind_problem, canonical_bytes
    from scripts.whole_source.artifacts import decode_integer
    from scripts.whole_source.receipts import discover_receipts, verify_stage
    from scripts.whole_source.execution import _write, exact_telemetry
    factory = runpy.run_path(str(root/'computations/2026-10-31T124328Z-integrated-reference-qualification/verify-variant-snapshots-v1.py'))['manufactured_inputs']
    allocator = resources.auto_plan
    def allocate(template, *, parallel, memory_mib=None, helper_root=root):
        return allocator(template, parallel=parallel, cpus=args.cpus, memory_mib=2048, helper_root=helper_root)
    origin = {'origin_git_commit': args.origin_commit, 'origin_git_dirty': True}
    started = time.perf_counter()
    with patch.object(resources, 'auto_plan', allocate):
        problem, source, identity, identity_core = factory(work/'manufactured', origin)
        p_inputs = proposal.prepare_proposal_inputs(problem, source.path, work/'proposal-inputs', panel_size=2, **origin)
    command = [sys.executable, '-B', '-m', 'scripts.weil_whole_source_split', 'propose',
               '--problem', str(p_inputs['problem']), '--execution', str(p_inputs['execution']),
               '--source', str(source.path), '--output-dir', str(work/'proposal')]
    before = time.perf_counter()
    proposed = subprocess.run(command, cwd=root, capture_output=True, text=True)
    (output/'proposal-stdout.txt').write_text(proposed.stdout, encoding='utf-8')
    (output/'proposal-stderr.txt').write_text(proposed.stderr, encoding='utf-8')
    assert proposed.returncode == 0, proposed.stderr
    proposal_wall = time.perf_counter()-before
    core = proposal.read_proposal(work/'proposal/proposal.json', problem, controls._record(source.path)['artifact'])
    p_science = []
    for block in core['blocks']:
        store = proposal.PanelStore(work/'proposal', block['context'])
        values = []
        for panel in block['integer_panels']:
            name = f"Z/{panel['row']}/{panel['column']}"
            store.refs[name] = panel['artifact']
            values.append({'row': panel['row'], 'column': panel['column'], 'values': store.read(name, 'integer')})
        p_science.append({'parity': block['parity'], 'theta': block['theta'], 'panels': values})
    with patch.object(resources, 'auto_plan', allocate):
        e_inputs = exact.prepare_exact_inputs(problem, source.path, work/'proposal/proposal.json', work/'exact-inputs', **origin)
    command = [sys.executable, '-B', '-m', 'scripts.weil_whole_source_split', 'exact',
               '--problem', str(e_inputs['problem']), '--execution', str(e_inputs['execution']),
               '--source', str(source.path), '--proposal', str(work/'proposal/proposal.json'),
               '--output-dir', str(work/'exact')]
    before = time.perf_counter()
    assessed = subprocess.run(command, cwd=root, capture_output=True, text=True)
    (output/'exact-stdout.txt').write_text(assessed.stdout, encoding='utf-8')
    (output/'exact-stderr.txt').write_text(assessed.stderr, encoding='utf-8')
    assert assessed.returncode == 0, assessed.stderr
    exact_wall = time.perf_counter()-before
    report = json.loads((work/'exact/report.json').read_bytes())
    assert report['status'] == 'PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL'
    assert report['proof_scope'] == 'CONTROL_ONLY'
    fields = ('parity','dimension','goal','width','margin','tau','direction_index','direction_upper',
              'direction_mass','row_margins','transformed_digest','transformed_upper_entries',
              'modular','source_tiles_consumed','source_consumed_digest')
    # Source-consumed raw digests legitimately bind different code-bound source
    # collections. Compare their complete count, not a relabeled source identity.
    e_science = [{key: block[key] for key in fields if key != 'source_consumed_digest'} for block in report['blocks']]
    case_rows = []
    if args.negative_controls:
        with patch.object(resources, 'auto_plan', allocate):
            for name, expected in controls.EXACT_CASES:
                value = controls._exact_case(problem, source, identity, identity_core, work/name, name, root, origin)
                assert value['passed'] is True and value['status'] == expected
                case_rows.append({'case': name, 'status': value['status']})
    stages, pools = [], []
    peak = 0
    for path in discover_receipts(work):
        verified = verify_stage(path)
        stage, plan = verified['stage'], verified['plan']
        assert plan.cpus == args.cpus and plan.memory_mib == 2048 and plan.workers*plan.threads <= args.cpus
        tasks = [json.loads(line) for line in Path(stage['task_file']).read_bytes().splitlines()]
        complete = json.loads((Path(stage['result_dir'])/'complete.json').read_bytes())
        receipt = json.loads(path.read_bytes())
        peak = max(peak, receipt['peak_budgeted_memory_bytes'])
        stages.append({'receipt': str(path), 'function': plan.task_function,
                       'operations': [task['operation'] for task in tasks], 'task_count': len(tasks),
                       'task_workers': len(complete['worker_pids']), 'workers': plan.workers,
                       'threads': plan.threads})
        observation = path.parent.parent/(receipt['stage']+'-pool-observation.json')
        if observation.exists():
            pools.append(json.loads(observation.read_bytes()))
    result = {'status': 'PASS_CONTROL_ONLY_TASK_LAYOUT', 'code_root': str(root),
              'cpus': args.cpus, 'memory_mib': 2048, 'proposal_science': p_science,
              'exact_science': e_science, 'assessment': report['assessment'],
              'source_consumed_digests': [block['source_consumed_digest'] for block in report['blocks']],
              'control_cases': case_rows, 'stages': stages, 'pool_observations': pools,
              'proposal_wall_s': proposal_wall, 'exact_wall_s': exact_wall,
              'wall_s': time.perf_counter()-started, 'peak_owned_budgeted_bytes': peak,
              'full_qualification': False, 'production_admission': False}
    _write(output/'verification.json', canonical_bytes(exact_telemetry(result)))
    print(json.dumps({'status': result['status'], 'stages': len(stages),
                      'task_count': sum(row['task_count'] for row in stages),
                      'max_task_workers': max(row['task_workers'] for row in stages),
                      'proposal_wall_s': proposal_wall, 'exact_wall_s': exact_wall}))


if __name__ == '__main__':
    main()
