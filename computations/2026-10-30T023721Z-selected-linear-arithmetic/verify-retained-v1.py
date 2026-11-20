"""Read-only byte, exact reduction and selected-containment evidence verification.

This rechecks retained data. It does not repeat native analytical reconstruction,
prove the native library/source premises, or admit any production theorem.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE/'captured-code-v5'))
from scripts.whole_source.contract import ArtifactRef, bind_problem, canonical_bytes
from scripts.whole_source.artifacts import CollectionSpec, _decode_chunk, _decode_prefix, _task, encode_rational
from scripts.whole_source.slice import check_entries


def load(path):
    return json.loads(path.read_bytes())


def consumed(root, reference):
    ref = ArtifactRef(**reference)
    path = root/ref.path
    assert path.resolve().is_relative_to(root.resolve()) and path.is_file() and not path.is_symlink()
    raw = path.read_bytes()
    assert len(raw) == ref.size and hashlib.sha256(raw).hexdigest() == ref.sha256, ref.path
    return raw


def collection_entries(root, spec):
    state = load(root/'collection.json')
    assert state['collection_id'] == spec.collection_id and state['collection'] == spec.to_dict()
    accumulators = {q.key: [Fraction(0), Fraction(0), set()] for q in spec.quantities}
    prefixes = {}
    head = state['index']
    metadata_bytes = 0
    while head:
        raw = consumed(root, head)
        metadata_bytes += len(raw)
        assert metadata_bytes <= spec.bounds.max_total_bytes
        node = json.loads(raw)
        assert canonical_bytes(node) == raw and node['collection_id'] == spec.collection_id
        receipt = json.loads(consumed(root, node['receipt']))
        assert receipt['event'] == node['event'] and receipt['collection_id'] == spec.collection_id
        assert receipt['scientific_acceptance'] is False
        owner = json.loads(consumed(root, receipt['owner']))
        assert owner['generation'] == receipt['generation'] and owner['attempt_id'] == receipt['attempt_id']
        event = node['event']
        raw_artifact = consumed(root, event['artifact'])
        if event['kind'] == 'chunk':
            snapshot = _decode_chunk(spec, raw_artifact)
            task = _task(snapshot.header['task'])
            assert task.to_dict() == event['task']
            lower, upper, seen = accumulators[task.quantity]
            for record in snapshot.records:
                assert record.contribution not in seen
                seen.add(record.contribution)
                lower += record.lower
                upper += record.upper
            accumulators[task.quantity][:2] = [lower, upper]
        elif event['kind'] == 'prefix':
            prefix = _decode_prefix(spec, raw_artifact, ArtifactRef(**event['artifact']))
            prefixes.setdefault(prefix.task.quantity, prefix)
        head = node['previous']
    rows = []
    for quantity in spec.quantities:
        lower, upper, seen = accumulators[quantity.key]
        expected = 1
        for axis in quantity.axes:
            expected *= len(axis)
        assert len(seen) == expected
        # All chunk endpoints are on q512. Each prefix contribution therefore
        # pays exactly one additional unit on each side, even across resume.
        lower -= Fraction(expected, 1 << spec.grid_bits)
        upper += Fraction(expected, 1 << spec.grid_bits)
        prefix = prefixes[quantity.key]
        assert prefix.covered == prefix.rounds == expected and len(prefix.records) == 1
        actual = prefix.records[0]
        assert (actual.lower, actual.upper) == (lower, upper)
        rows.append({'quantity': quantity.to_dict()['quantity'], 'covered': expected,
                     'lower': encode_rational(lower, 8192), 'upper': encode_rational(upper, 8192),
                     'prefix': {'path': prefix.ref.path, 'sha256': prefix.ref.sha256, 'size': prefix.ref.size}})
    return rows


def accepted(path, problem, config, code_root):
    state = load(path/'slice-state.json')
    assert state['status'] == 'VERIFIED_SELECTED_COMPLETE_ARITHMETIC'
    report = json.loads(consumed(path, state['receipt']))
    rows = {}
    for role in ('producer', 'analytic'):
        spec = CollectionSpec.from_dict(problem, config['roles'][role]['collection'], code_root=code_root)
        rows[role] = collection_entries(path/role, spec)
        assert rows[role] == report['roles'][role]['entries']
        assert report['roles'][role]['scope'] == 'SELECTION_ONLY'
        assert all(row['worker_cleanup_verified'] for row in report['roles'][role]['owned_receipts'])
    recomputed = check_entries(problem, rows['producer'], rows['analytic'])
    assert recomputed == report['entries'] and report['all_owned_cleanup_verified']
    assert not any(report[name] for name in ('full_mathematical_source', 'matrix_positivity',
                                            'production_admission', 'full_target_run'))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle-dir', type=Path, default=HERE)
    args = parser.parse_args()
    base = args.bundle_dir.resolve()
    manifest = load(base/'manifest.json')
    assert manifest['status'] == 'QUALIFIED_SELECTED_COMPLETE_ARITHMETIC'
    for ref in manifest['members']:
        consumed(base, ref)
    code_root = base/'captured-code-v5'
    problem = bind_problem('retained-t081', root=code_root)
    config = load(base/'data/inputs-v5/execution.json')
    normal = accepted(base/'data/normal-v5', problem, config, code_root)
    recovery = load(base/'data/recovery-v3/partial-qualification.json')
    assert len(recovery['cuts']) == 8 and {r['cut'] for r in recovery['cuts']} == {'K%02d' % n for n in range(1, 9)}
    for row in recovery['cuts']:
        actual = accepted(base/'data/recovery-v3'/row['cut'], problem, config, code_root)
        assert actual['entries'] == normal['entries'] and row['same_canonical_endpoints']
        assert actual['roles']['producer']['quantity_seals'] == normal['roles']['producer']['quantity_seals']
        assert actual['roles']['analytic']['quantity_seals'] == normal['roles']['analytic']['quantity_seals']
    assert len(recovery['mathematical_controls']) == 7 and len(recovery['native_mathematical_controls']) == 3
    assert all(r['rejection'] for r in recovery['mathematical_controls']+recovery['native_mathematical_controls'])
    retries = recovery['retry_and_late_output']
    assert retries['identical_actual_retry']['no_new_index_or_contribution']
    assert retries['stale_actual_native_response']['rejection'] and retries['conflicting_correct_hash_retry']['rejection']
    boundaries = load(base/'data/boundaries-v3/qualification.json')
    assert boundaries['all_five_controls_passed'] and len(boundaries['controls']) == 5
    assert {r['cut'] for r in boundaries['controls']} == {'K%02d' % n for n in range(9, 14)}
    for row in boundaries['controls']:
        assert row['status'] == 'PASSED'
    persisted = load(base/'data/persisted-cache-v2/qualification.json')
    assert persisted['positive_completed_first'] and len(persisted['cases']) == 3
    assert persisted['cases'][0]['status'] == 'ACCEPTED_POSITIVE_CACHE_CONTROL'
    assert all(r['status'] == 'REJECTED_AT_INDEPENDENT_MATHEMATICS' and r['all_owned_cleanup_verified']
               for r in persisted['cases'][1:])
    partial = load(base/'data/partial-inner-prefix-v2/qualification.json')
    assert partial['committed_before_interrupt'] == 257 and partial['complete_entry_contributions'] == 9912
    assert partial['same_all_six_final_endpoints'] and partial['same_all_quantity_seals']
    continued = accepted(base/'data/partial-inner-prefix-v2/collection-run', problem, config, code_root)
    assert continued['entries'] == normal['entries']
    replayed = accepted(base/'data/frozen-replay-v2', problem, config, code_root)
    assert replayed['entries'] == normal['entries']
    print(json.dumps({'status': 'PASS_RETAINED_SELECTED_ARITHMETIC_EVIDENCE', 'members_verified': len(manifest['members']),
        'complete_entries': 6, 'scientific_recovery_cuts': 13, 'mathematical_rejections': 12,
        'scope': 'READ_ONLY_RETAINED_DATA_NOT_FRESH_NATIVE_RECONSTRUCTION',
        'full_source': False, 'matrix_positivity': False, 'production_admission': False}, sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
