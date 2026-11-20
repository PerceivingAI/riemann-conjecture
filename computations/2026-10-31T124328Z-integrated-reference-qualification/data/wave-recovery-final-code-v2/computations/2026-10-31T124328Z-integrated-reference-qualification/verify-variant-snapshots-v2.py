"""Read-only qualification of completed variant controls after v1 reporting failure."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source import controls, pipeline
from scripts.whole_source.artifacts import _raw, decode_rational
from scripts.whole_source.contract import ArtifactRef, canonical_bytes, problem_id
from scripts.whole_source.exact import _bind_exact
from scripts.whole_source.execution import MIB, _write
from scripts.whole_source.proposal import read_proposal
from scripts.whole_source.receipts import discover_receipts, verify_stage
from scripts.whole_source.slice import _ref


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--capture-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run, output = args.run_dir.resolve(strict=True), args.output.resolve()
    assert not output.exists() and not output.is_relative_to(run)
    inventory = json.loads(args.inventory.read_bytes())
    assert inventory['format'] == 'variant-snapshots-completed-run-inventory-v1'
    assert inventory['run_directory'] == run.relative_to(ROOT).as_posix()
    assert {p.relative_to(run).as_posix() for p in run.rglob('*') if p.is_file()} == {
        r['path'] for r in inventory['files']}
    for value in inventory['files']:
        _raw(run, ArtifactRef(**value), 8*MIB)
    capture = args.capture_root.resolve(strict=True)
    preservation = json.loads((capture/'preservation.json').read_bytes())
    for value in preservation['files']:
        _raw(capture, ArtifactRef(**value), 8*MIB)
    for name in ('scripts/whole_source/controls.py', 'scripts/whole_source/exact.py'):
        assert (capture/'runtime'/name).read_bytes() == (ROOT/name).read_bytes()
    problem, _, roles = pipeline._bind(run/'source-inputs/problem.json', run/'source-inputs/execution.json', ROOT)
    source = pipeline.SourceReader(run/'original-source/source-manifest.json', roles['producer'][0], control=True)
    proposal_path = run/'original-proposal/proposal.json'
    read_proposal(proposal_path, problem, controls._record(source.path)['artifact'])
    closure = {r.path: r for r in source.spec.problem.evidence + source.spec.code_refs}
    stages, cases, selected = [], [], set()
    peak = 0
    for case, expected in controls.EXACT_CASES:
        directory = run/case
        report = json.loads((directory/'run/report.json').read_bytes())
        bound_problem, _, descriptor, _, _ = _bind_exact(directory/'inputs/problem.json',
                                                        directory/'inputs/execution.json', ROOT)
        assert problem_id(bound_problem) == report['problem_id'] == problem_id(problem)
        assert report['source'] == descriptor['source'] and report['proposal'] == descriptor['origin']
        assert report['proof_scope'] == descriptor['proof_scope'] == 'CONTROL_ONLY'
        assert report['assessment']['smooth_test_consequence_conditional'] is False
        assert report['production_admission'] is False
        assert report['status'] == report['assessment']['status']
        results = {}
        for value in report['receipt_bindings']:
            ref = ArtifactRef(**value)
            _raw(directory/'run', ref, 8*MIB)
            path = directory/'run'/ref.path
            verified = verify_stage(path)
            stage, plan = verified['stage'], verified['plan']
            assert plan.cpus == plan.workers == plan.threads == 1 and plan.memory_mib == 1536
            assert plan.task_function == 'evaluate_exact' and plan.task_program == _ref(ROOT, 'scripts/whole_source/exact.py')
            assert stage['task_count'] == 1
            receipt = json.loads(path.read_bytes())
            name = receipt['stage']
            assert name not in results
            result_dir = Path(stage['result_dir'])
            rows = (result_dir/'completed.jsonl').read_bytes().splitlines()
            assert len(rows) == 1
            value = json.loads(rows[0])
            payload = json.loads(_raw(result_dir, ArtifactRef(**{
                k: value[k] for k in ('path', 'sha256', 'size')}), plan.result_bytes))
            results[name] = payload['result']
            selected.add(path.resolve())
            stages.append({'receipt': path.relative_to(run).as_posix(), 'task_count': 1})
            peak = max(peak, receipt['peak_budgeted_memory_bytes'])
        assert set(results) == {'parity-0', 'parity-1', 'assess'}
        assert report['blocks'] == [results['parity-'+str(p)]['report'] for p in (0, 1)]
        assert report['assessment'] == results['assess']['assessment']
        if case == 'singular-full-U':
            assert report['source']['manifest'] == controls._record(source.path)['artifact']
            assert report['blocks'][0]['modular']['residue'] == 0
            assert report['blocks'][0]['modular']['nonsingular'] is False
            assert report['assessment']['positive_paid_lower'] is False
            copied = {'members': 0, 'bytes': 0}
        else:
            variant = directory/'source'
            reader = pipeline.SourceReader(variant/'source-manifest.json', source.spec, control=True)
            assert report['source']['manifest'] == controls._record(reader.path)['artifact']
            assert reader.execution['provenance'] == {'kind': 'MATHEMATICAL_VARIANT',
                'original_source': controls._record(source.path),
                'original_execution': controls._record(source.execution_path)}
            assert {p.name for p in (variant/'snapshots').iterdir()} == {r.sha256 for r in closure.values()}
            for ref in closure.values():
                local = ArtifactRef('snapshots/'+ref.sha256, ref.sha256, ref.size)
                assert _raw(variant, local, 8*MIB) == _raw(source.path.parent, local, 8*MIB)
                assert not (variant/local.path).samefile(source.path.parent/local.path)
            copied = {'members': len({r.sha256 for r in closure.values()}),
                      'bytes': sum(p.stat().st_size for p in (variant/'snapshots').iterdir())}
            assert report['status'] == expected
            if case == 'selected-paid-lower-negative':
                assert any(decode_rational(b['direction_upper'], 65536) < 0 and
                           decode_rational(b['direction_mass'], 65536) > 0 for b in report['blocks'])
            else:
                assert any(decode_rational(b['width'], 65536) > decode_rational(b['goal'], 65536)
                           for b in report['blocks'])
        cases.append({'case': case, 'status': report['status'], 'passed': True, 'copied_snapshots': copied,
                      'report': controls._record(directory/'run/report.json')})
    assert len(stages) == 9 and selected == set(discover_receipts(run))
    # Detect changes during qualification, without modifying the failed coordinator tree.
    for value in inventory['files']:
        _raw(run, ArtifactRef(**value), 8*MIB)
    result = {'status': 'PASS_CONTROL_ONLY_VARIANT_SNAPSHOTS',
        'scope': 'MANUFACTURED_REDUCED_EXACT_CONTROLS_READ_ONLY_CLOSEOUT',
        'run_inventory': controls._record(args.inventory.resolve()),
        'preserved_execution': controls._record(capture/'preservation.json'),
        'coordinator_v1_final_report_failed': True, 'numerical_stages_rerun': False,
        'executed_controls_sha256': hashlib.sha256((capture/'runtime/scripts/whole_source/controls.py').read_bytes()).hexdigest(),
        'source_geometry': source.document['geometry'], 'required_logical_snapshot_members': len(closure),
        'required_logical_snapshot_bytes': sum(r.size for r in closure.values()), 'cases': cases,
        'verified_owned_stages': stages, 'all_owned_cleanup_verified': True,
        'observed_peak_budgeted_memory_bytes': peak, 'input_tree_unchanged': True,
        'full_controls_gate_executed': False, 'analytical_source_acceptance': False,
        'full_qualification_executed': False, 'production_admission': False}
    _write(output, canonical_bytes(result))
    print(json.dumps({'status': result['status'], 'cases': len(cases), 'owned_stages': len(stages),
                      'numerical_stages_rerun': False}, sort_keys=True))


if __name__ == '__main__':
    main()
