"""Compare preserved residual traversal and qualify bounded corrected execution."""
from dataclasses import asdict, replace
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source import pipeline, resources
from scripts.whole_source.artifacts import CollectionLock, CollectionSpec
from scripts.whole_source.contract import bind_problem, canonical_bytes
from scripts.whole_source.execution import WorkloadExecution, _write
from scripts.whole_source.receipts import discover_receipts, verify_stage
from scripts.whole_source.slice import _ref, _request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-root', type=Path, required=True)
    parser.add_argument('--corrected-root', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--origin-commit', required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    program = Path(__file__).with_name('residual-reuse-control-v1.py')
    compared = []
    environment = dict(os.environ)
    environment.update({key:'1' for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
                                           'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')})
    for label, root in (('baseline', args.baseline_root), ('corrected', args.corrected_root)):
        command = [sys.executable, '-B', str(program), '--code-root', str(root.resolve()),
                   '--output', str(output/(label+'.json'))]
        result = subprocess.run(command, capture_output=True, text=True, env=environment)
        (output/(label+'-stdout.txt')).write_text(result.stdout, encoding='utf-8')
        (output/(label+'-stderr.txt')).write_text(result.stderr, encoding='utf-8')
        if result.returncode:
            raise RuntimeError(label+' control failed: '+result.stderr)
        compared.append(json.loads((output/(label+'.json')).read_bytes()))
    before, after = compared
    assert before['science'] == after['science']
    assert before['image_constructions'] == {'reduced':18, 'full':826}
    assert after['image_constructions'] == {'reduced':6, 'full':2}
    problem = bind_problem('retained-t081')
    origin = {'origin_git_commit':args.origin_commit, 'origin_git_dirty':True}
    allocator = resources.auto_plan
    def allocate(template, *, parallel, memory_mib=None, helper_root=ROOT):
        return allocator(template, parallel=parallel, cpus=1, memory_mib=1536,
                         helper_root=helper_root)
    with patch.object(resources, 'auto_plan', allocate):
        paths = pipeline.prepare_source_inputs(problem, output/'full-inputs', tile_modes=32, **origin)
    _, _, roles = pipeline._bind(paths['problem'], paths['execution'], ROOT)
    spec, plan = roles['analytic']
    control_ref = _ref(ROOT, program.relative_to(ROOT).as_posix())
    refs = tuple(sorted((*spec.code_refs, control_ref), key=lambda ref:ref.path))
    control_spec = CollectionSpec.create(problem, role=spec.role, quantities=spec.quantities,
        partition=spec.partition, backend=spec.backend, backend_version=spec.backend_version,
        native_threads=spec.native_threads, code_refs=refs, bounds=spec.bounds, grid_bits=spec.grid_bits)
    origin_path = output/'control-origin.json'
    _write(origin_path, canonical_bytes({'format':'whole-source-code-origin-v1', **origin,
                                       'files':[asdict(ref) for ref in refs]}))
    control_plan = replace(plan, collection_sha256=control_spec.collection_id,
        task_program=control_ref, task_function='evaluate', scope='OPERATIONAL_CONTROL_ONLY',
        provenance=_ref(ROOT, origin_path.relative_to(ROOT).as_posix()))
    with CollectionLock.acquire(output/'owned-control', control_spec) as lock:
        with WorkloadExecution(lock, control_spec, control_plan) as execution:
            execution.run_stage('residual-reuse-control', [_request(operation='residual-reuse-control')])
            owned = next(execution.read_results('residual-reuse-control'))['result']
    assert owned['science'] == after['science']
    with patch.object(resources, 'auto_plan', allocate):
        reduced = pipeline.prepare_source_inputs(problem, output/'reduced-inputs',
                                                  control=True, tile_modes=2, **origin)
    pipeline.run_source(reduced['problem'], reduced['execution'], output/'source')
    audited = pipeline.run_audit(reduced['problem'], output/'source/producer/source-manifest.json',
                                 reduced['execution'], output/'audit')
    assert audited['entries_checked'] == 36 and audited['full_mathematical_source'] is False
    checks = []
    for receipt in discover_receipts(output):
        evidence = verify_stage(receipt)
        checks.append({'receipt':receipt.relative_to(output).as_posix(),
                       'task_count':evidence['stage']['task_count']})
    assert len(checks) == 21
    resource_paths = list((output/'owned-control').rglob('residual-reuse-control-resources.json'))
    assert len(resource_paths) == 1
    observed = json.loads(resource_paths[0].read_bytes())
    assert observed['cleanup_verified'] is True
    report = {'status':'PASS_CONTROL_ONLY_RESIDUAL_REUSE_CORRECTION',
        'baseline_image_constructions':before['image_constructions'],
        'corrected_image_constructions':after['image_constructions'],
        'exact_and_enclosure_digests_agree':True, 'science':after['science'],
        'owned_control':owned, 'owned_control_peak_bytes':observed['owned_peak_bytes'],
        'private_allowance_mib':plan.worker_private_mib, 'native_allowance_mib':plan.native_workspace_mib,
        'derived_full_traversal':{'inputs':826, 'previous_images':341138, 'corrected_images':826,
                                  'previous_degree_steps':29679006, 'corrected_degree_steps':71862},
        'reduced_entries_checked':36, 'verified_owned_stages':checks,
        'all_owned_cleanup_verified':True, 'full_qualification_executed':False,
        'scientific_full_source_acceptance':False, 'production_admission':False}
    _write(output/'verification.json', canonical_bytes(report))
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
