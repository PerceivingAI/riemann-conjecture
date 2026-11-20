"""Producer task-budget controls and real reduced source/audit; no full qualification."""
from dataclasses import asdict, replace
from pathlib import Path
from copy import deepcopy
import argparse
import json
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source import pipeline, resources
from scripts.whole_source.artifacts import CollectionLock, CollectionSpec
from scripts.whole_source.contract import ContractError, bind_problem, canonical_bytes
from scripts.whole_source.execution import WorkloadExecution, _write
from scripts.whole_source.receipts import discover_receipts, verify_stage
from scripts.whole_source.slice import _ref, _request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--origin-commit', required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    problem = bind_problem('retained-t081')
    origin = {'origin_git_commit': args.origin_commit, 'origin_git_dirty': True}
    original = resources.auto_plan
    def allocate(template, *, parallel, memory_mib=None, helper_root=ROOT):
        # Explicit bounded verification allocation with real resource discovery.
        return original(template, parallel=parallel, cpus=1, memory_mib=1536,
                        helper_root=helper_root)
    layouts = []
    for width in (16, 32):
        with patch.object(resources, 'auto_plan', allocate):
            paths = pipeline.prepare_source_inputs(problem, output/('full-inputs-'+str(width)),
                tile_modes=width, **origin)
        _, config, roles = pipeline._bind(paths['problem'], paths['execution'], ROOT)
        spec, plan = roles['producer']
        required = pipeline._producer_requirements(spec, False)
        layouts.append({'tile_modes': width, 'required_bytes': required,
                        'private_allowance_mib': plan.worker_private_mib,
                        'native_allowance_mib': plan.native_workspace_mib,
                        'workers': plan.workers, 'threads': plan.threads})
        assert plan.worker_private_mib*1024**2 >= required['private_bytes']
        assert plan.native_workspace_mib*1024**2 >= required['native_bytes']
    negatives = []
    for field in ('worker_private_mib', 'native_workspace_mib'):
        invalid = deepcopy(config)
        invalid_plan = replace(plan, resource_policy=None, **{field: 1})
        invalid['roles']['producer']['execution'] = invalid_plan.to_dict()
        path = paths['execution'].parent/(field+'-invalid.json')
        _write(path, canonical_bytes(invalid))
        destination = output/('must-not-start-'+field)
        try:
            pipeline.run_source(paths['problem'], path, destination)
        except ContractError as exc:
            assert not destination.exists()
            negatives.append({'field': field, 'rejected': True, 'reason': str(exc)})
        else:
            raise AssertionError('undersized producer plan accepted')
    guard_program = Path(__file__).with_name('producer-budget-guard-v1.py')
    guard_ref = _ref(ROOT, guard_program.relative_to(ROOT).as_posix())
    refs = tuple(sorted((*spec.code_refs, guard_ref), key=lambda ref: ref.path))
    guard_spec = CollectionSpec.create(problem, role=spec.role, quantities=spec.quantities,
        partition=spec.partition, backend=spec.backend, backend_version=spec.backend_version,
        native_threads=spec.native_threads, code_refs=refs, bounds=spec.bounds,
        grid_bits=spec.grid_bits)
    origin_path = output/'guard-origin.json'
    _write(origin_path, canonical_bytes({'format':'whole-source-code-origin-v1',
        **origin, 'files':[asdict(ref) for ref in refs]}))
    guard_plan = replace(plan, collection_sha256=guard_spec.collection_id,
        task_program=guard_ref, task_function='evaluate', scope='OPERATIONAL_CONTROL_ONLY',
        provenance=_ref(ROOT, origin_path.relative_to(ROOT).as_posix()))
    with CollectionLock.acquire(output/'owned-guard', guard_spec) as lock:
        with WorkloadExecution(lock, guard_spec, guard_plan) as execution:
            execution.run_stage('guard', [_request(operation='producer-budget-guard')])
            result = list(execution.read_results('guard'))[0]['result']
            assert result['tiles_per_parity'] == [91, 91]
            assert result['precision_bits'] == problem.arithmetic.source_bits
            assert result['source_values_evaluated'] is False
    with patch.object(resources, 'auto_plan', allocate):
        reduced = pipeline.prepare_source_inputs(problem, output/'reduced-inputs',
            control=True, tile_modes=2, **origin)
    pipeline.run_source(reduced['problem'], reduced['execution'], output/'source')
    source = output/'source/producer/source-manifest.json'
    audited = pipeline.run_audit(reduced['problem'], source, reduced['execution'], output/'audit')
    assert audited['entries_checked'] == 36 and audited['full_mathematical_source'] is False
    checks = []
    for receipt in discover_receipts(output):
        evidence = verify_stage(receipt)
        checks.append({'receipt':receipt.relative_to(output).as_posix(),
                       'task_count':evidence['stage']['task_count']})
    report = {'status':'PASS_CONTROL_ONLY_PRODUCER_BUDGET_CORRECTION',
        'layouts':layouts, 'early_rejections':negatives, 'owned_guard':result,
        'reduced_entries_audited':audited['entries_checked'], 'owned_stages_verified':checks,
        'all_owned_cleanup_verified':True, 'full_qualification_executed':False,
        'production_admission':False, 'scientific_full_source_acceptance':False}
    _write(output/'verification.json', canonical_bytes(report))
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
