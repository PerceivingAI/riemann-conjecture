"""Verify complete variant dependencies and three manufactured exact controls."""
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source import controls, pipeline, resources
from scripts.whole_source.artifacts import CollectionLock, _publication_header, _raw, decode_rational
from scripts.whole_source.contract import ArtifactRef, QuantityKey, bind_problem, canonical_bytes, problem_id
from scripts.whole_source.execution import MIB, _RUNTIME, _write
from scripts.whole_source.proposal import BITS, TRANSFORM_BITS, SCOPE, PanelStore, read_proposal
from scripts.whole_source.receipts import discover_receipts, verify_stage
from scripts.whole_source.slice import _ref


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manufactured_inputs(output, origin):
    problem = bind_problem('retained-t081')
    inputs = pipeline.prepare_source_inputs(problem, output/'source-inputs', control=True, tile_modes=6, **origin)
    _, _, roles = pipeline._bind(inputs['problem'], inputs['execution'], ROOT)
    spec = roles['producer'][0]
    source = output/'original-source'
    with CollectionLock.acquire(source, spec):
        pass
    bits = problem.arithmetic.publication_bits
    scale = 1 << bits
    tiles = []
    for family, name in (('A_model', 'A_model'), ('weighted_head', 'head_complete'),
                         ('weighted_complete_tail', 'tail_complete')):
        for parity in (0, 1):
            for domain in pipeline._tiles(spec, QuantityKey(name, parity)):
                records = []
                for m in domain.rows:
                    for n in domain.columns:
                        if m > n:
                            continue
                        center = Fraction(8*scale, 2*m+1) if family == 'A_model' and m == n else Fraction(0)
                        lo = center.numerator//center.denominator-1
                        hi = -((-center.numerator)//center.denominator)+1
                        records.append([m, n, hex(lo), hex(hi)])
                raw = canonical_bytes({'header': _publication_header(spec, domain, bits), 'records': records})
                artifact_name = family+'-'+str(parity)+'-'+str(len(tiles))+'.json'
                ref = _write(source/artifact_name, raw)
                tiles.append({'family': family, 'parity': parity, 'task': domain.to_dict(), 'artifact': asdict(ref)})
    manifest = source/'source-manifest.json'
    _write(manifest, canonical_bytes(pipeline.scientific_manifest(spec, True, tiles)))
    pipeline.write_source_execution(manifest, spec, {'kind': 'DECLARED_CONTROL'})
    reader = pipeline.SourceReader(manifest, spec, control=True)
    directory = output/'original-proposal'
    directory.mkdir()
    source_ref = controls._record(manifest)['artifact']
    policy = {'native_bits': BITS, 'working_grid_bits': BITS, 'transform_bits': TRANSFORM_BITS,
              'theta_bits': 40, 'panel_size': 2, 'logtheta_bounds': [-20, 20]}
    paths = sorted(set(_RUNTIME) | {'scripts/whole_source/proposal.py', 'scripts/whole_source/proposal_float.py'})
    code = [asdict(_ref(ROOT, name)) for name in paths]
    identity = controls._digest(canonical_bytes({'problem_id': problem_id(problem), 'source': source_ref,
                                               'policy': policy, 'code': code}))
    diagnostics = _write(directory/'diagnostics.json', canonical_bytes({
        'scope': 'CONTROL_ONLY', 'kind': 'MANUFACTURED_IDENTITY_NOT_FLOATING_PROPOSAL'}))
    blocks = []
    dimension = reader.document['geometry']['N']//2
    for parity in (0, 1):
        context = {'proposal_id': identity, 'problem_id': problem_id(problem), 'source_sha256': source_ref['sha256'],
                   'dimension': dimension, 'panel_size': 2, 'precision_bits': BITS, 'grid_bits': BITS,
                   'transform_bits': TRANSFORM_BITS, 'parity': parity}
        store = PanelStore(directory, context)
        panels = []
        for i in range(0, dimension, 2):
            for j in range(0, dimension, 2):
                name = f'Z/{i}/{j}'
                store.put(name, 'integer', [hex((1 << TRANSFORM_BITS)*int(r == c))
                    for r in range(i, min(i+2, dimension)) for c in range(j, min(j+2, dimension))])
                panels.append({'row': i, 'column': j, 'artifact': store.refs[name]})
        blocks.append({'parity': parity, 'dimension': dimension, 'u': TRANSFORM_BITS, 'theta': '1',
                       'context': context, 'integer_panels': panels, 'inherited_coordinates_used': False})
    core = {'format': 'whole-source-congruence-proposal-v1', 'status': 'NONPROOF_ONLY', 'scope': SCOPE,
        'problem_id': problem_id(problem), 'source': source_ref, 'source_directory_at_execution': str(source),
        'source_control': True, 'policy': policy, 'code': code,
        'backend_versions': {'native': 'manufactured-exact-control', 'floating': 'not-executed'},
        'diagnostics': asdict(diagnostics), 'blocks': blocks, 'analytical_acceptance': False,
        'matrix_positivity': False, 'production_admission': False}
    proposal = directory/'proposal.json'
    _write(proposal, canonical_bytes(core))
    read_proposal(proposal, problem, source_ref)
    return problem, reader, proposal, core


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--origin-commit', required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.relative_to(ROOT)
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    origin = {'origin_git_commit': args.origin_commit, 'origin_git_dirty': True}
    allocator = resources.auto_plan
    def allocate(template, *, parallel, memory_mib=None, helper_root=ROOT):
        return allocator(template, parallel=parallel, cpus=1, memory_mib=1536, helper_root=helper_root)
    results = []
    with patch.object(resources, 'auto_plan', allocate):
        problem, source, proposal, core = manufactured_inputs(output, origin)
        originals = {p.relative_to(source.path.parent): digest(p)
                     for p in source.path.parent.rglob('*') if p.is_file()}
        proposal_originals = {p.relative_to(proposal.parent): digest(p)
                              for p in proposal.parent.rglob('*') if p.is_file()}
        closure = {r.path: r for r in source.spec.problem.evidence + source.spec.code_refs}
        for name, _ in controls.EXACT_CASES:
            directory = output/name
            result = controls._exact_case(problem, source, proposal, core, directory, name, ROOT, origin)
            assert result['passed'] is True
            report = json.loads((directory/'run/report.json').read_bytes())
            assert report['proof_scope'] == 'CONTROL_ONLY'
            assert report['assessment']['smooth_test_consequence_conditional'] is False
            assert report['production_admission'] is False
            if name == 'singular-full-U':
                assert report['blocks'][0]['modular']['residue'] == 0
                assert report['blocks'][0]['modular']['nonsingular'] is False
                assert report['assessment']['positive_paid_lower'] is False
                copied = {'members': 0, 'bytes': 0}
            else:
                variant = directory/'source'
                assert {p.name for p in (variant/'snapshots').iterdir()} == {r.sha256 for r in closure.values()}
                for ref in closure.values():
                    local = ArtifactRef('snapshots/'+ref.sha256, ref.sha256, ref.size)
                    assert _raw(variant, local, 8*MIB) == _raw(source.path.parent, local, 8*MIB)
                    assert not (variant/local.path).samefile(source.path.parent/local.path)
                copied = {'members': len({r.sha256 for r in closure.values()}),
                          'bytes': sum(p.stat().st_size for p in (variant/'snapshots').iterdir())}
                if name == 'selected-paid-lower-negative':
                    assert report['status'] == 'SELECTED_PAID_LOWER_NEGATIVE_NOT_WEIL_NEGATIVITY'
                    assert any(decode_rational(b['direction_upper'], 65536) < 0 and
                               decode_rational(b['direction_mass'], 65536) > 0 for b in report['blocks'])
                else:
                    assert report['status'] == 'WIDTH_GOAL_FAILED'
                    assert any(decode_rational(b['width'], 65536) > decode_rational(b['goal'], 65536)
                               for b in report['blocks'])
            results.append({'case': name, 'status': result['status'], 'passed': True,
                            'copied_snapshots': copied, 'evidence': result})
    stages = []
    peak = 0
    for path in discover_receipts(output):
        verified = verify_stage(path)
        plan = verified['plan']
        assert plan.cpus == 1 and plan.workers == 1 and plan.threads == 1 and plan.memory_mib == 1536
        stages.append({'receipt': path.relative_to(output).as_posix(),
                       'task_count': verified['stage']['task_count']})
        receipt = json.loads(path.read_bytes())
        peak = max(peak, receipt['peak_budgeted_memory_bytes'])
    assert len(stages) == 9
    assert originals == {p.relative_to(source.path.parent): digest(p)
                         for p in source.path.parent.rglob('*') if p.is_file()}
    assert proposal_originals == {p.relative_to(proposal.parent): digest(p)
                                 for p in proposal.parent.rglob('*') if p.is_file()}
    result = {'status': 'PASS_CONTROL_ONLY_VARIANT_SNAPSHOTS', 'scope': 'MANUFACTURED_REDUCED_EXACT_CONTROLS',
        'source_geometry': source.document['geometry'], 'required_logical_snapshot_members': len(closure),
        'required_logical_snapshot_bytes': sum(r.size for r in closure.values()), 'cases': results,
        'verified_owned_stages': stages, 'all_owned_cleanup_verified': True,
        'observed_peak_budgeted_memory_bytes': peak, 'wall_seconds': time.monotonic()-started,
        'original_source_and_proposal_unchanged': True, 'full_controls_gate_executed': False,
        'analytical_source_acceptance': False, 'full_qualification_executed': False, 'production_admission': False}
    _write(output/'verification.json', canonical_bytes(result))
    print(json.dumps({'status': result['status'], 'cases': len(results), 'owned_stages': len(stages),
                      'wall_seconds': result['wall_seconds']}, sort_keys=True))


if __name__ == '__main__':
    main()
