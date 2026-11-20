"""Actual persisted false-source caches: structural success must not imply truth."""
from __future__ import annotations
import argparse
from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source.contract import ArtifactRef, bind_problem, canonical_bytes
from scripts.whole_source.artifacts import CollectionLock, CollectionSpec, ChunkStore, _decode_chunk, _task
from scripts.whole_source.execution import ExecutionPlan
from scripts.whole_source.slice import _run_role, check_entries


def load(path):
    return json.loads(path.read_bytes())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        raw = canonical_bytes(value)
        assert stream.write(raw) == len(raw)


def baseline_report(path):
    state = load(path/'slice-state.json')
    assert state['status'] == 'VERIFIED_SELECTED_COMPLETE_ARITHMETIC'
    raw = (path/state['receipt']['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == state['receipt']['sha256']
    return json.loads(raw)


def chunk_frames(baseline):
    frames = []
    for path in (baseline/'producer/attempts').glob('*/arithmetic-results/*.json'):
        value = load(path)
        for item in value.get('result', {}).get('chunks', []):
            frames.append(item)
    assert len(frames) == 240
    return sorted(frames, key=lambda item: canonical_bytes(item['task']))


def one_case(inputs, baseline, expected, directory, fault):
    directory.mkdir()
    problem = bind_problem('retained-t081')
    row = load(inputs/'execution.json')['roles']['producer']
    spec = CollectionSpec.from_dict(problem, row['collection'])
    plan = ExecutionPlan.from_dict(row['execution'])
    collection = directory/'producer'
    mutated = 0
    with CollectionLock.acquire(collection, spec) as lock:
        name = 'untrusted_cache_submission'
        (collection/'attempts'/name).mkdir()
        lock.register_attempt(name)
        store = ChunkStore(lock, spec, attempt_id=name)
        for frame in chunk_frames(baseline):
            task = _task(frame['task'])
            ref = ArtifactRef(**frame['ref'])
            source = baseline/'producer/chunks'/ref.sha256
            raw = source.read_bytes()
            assert len(raw) == ref.size and hashlib.sha256(raw).hexdigest() == ref.sha256
            term, window, node_axis = task.axes
            change = (fault == 'omitted-prime5' and term.start == 3 or
                      fault == 'omitted-last-node' and task.quantity.entry == (0, 0) and
                      term.start == 3 and window.start == 1 and node_axis.stop == problem.source_gauss_order)
            if change:
                snapshot = _decode_chunk(spec, raw)
                values = []
                for record in snapshot.records:
                    omit = fault == 'omitted-prime5' or record.contribution[-1] == problem.source_gauss_order-1
                    values.append(replace(record, lower=Fraction(0), upper=Fraction(0)) if omit else record)
                    mutated += int(omit)
                staged = store.stage_chunk(task, values)
                store.publish_chunk(task, staged)
            else:
                old_attempt = ref.path.split('/')[1]
                old_directory = collection/'attempts'/old_attempt
                if not old_directory.exists():
                    (old_directory/'staging').mkdir(parents=True)
                    shutil.copyfile(baseline/'producer/attempts'/old_attempt/'artifact-owner.json',
                                    old_directory/'artifact-owner.json')
                destination = collection/ref.path
                destination.write_bytes(raw)
                store.recover_staged_chunk(task, ref)
        lock.invalidate_attempt(name)
    # This is the production persisted/reduction/receipt path, with a new owner,
    # all full domains and actual owned prefix arithmetic. No cache is treated
    # as independent analytical truth, and no Gauss recomputation is claimed.
    produced = _run_role(collection, spec, plan, code_root=ROOT, resume=True)
    assert all(entry['covered'] == 9912 for entry in produced['entries'])
    proposal = {'format': 'untrusted-persisted-selected-source-v1', 'fault': fault,
                'source': produced, 'scope': 'STRUCTURAL_CACHE_NOT_ANALYTICAL_ACCEPTANCE'}
    save(directory/'proposal.json', proposal)
    consumed = (directory/'proposal.json').read_bytes()
    proposal = json.loads(consumed)
    try:
        checked = check_entries(problem, proposal['source']['entries'], expected['roles']['analytic']['entries'])
    except ValueError as exc:
        assert fault != 'positive'
        assert 'independent arithmetic containment failed' in str(exc)
        status, rejection = 'REJECTED_AT_INDEPENDENT_MATHEMATICS', str(exc)
    else:
        assert fault == 'positive'
        assert checked == expected['entries']
        assert produced['quantity_seals'] == expected['roles']['producer']['quantity_seals']
        status, rejection = 'ACCEPTED_POSITIVE_CACHE_CONTROL', None
    report = {'fault': fault, 'status': status, 'mutated_nonproof_cache_records': mutated,
        'all_6_complete_entries_persisted_and_reduced': True,
        'all_terms_windows_nodes_structurally_covered': True,
        'correct_consumed_proposal_sha256': hashlib.sha256(consumed).hexdigest(),
        'rejection': rejection, 'actual_owned_reduction_receipts': produced['owned_receipts'],
        'all_owned_cleanup_verified': all(item['worker_cleanup_verified'] for item in produced['owned_receipts']),
        'scientific_acceptance': fault == 'positive', 'full_source': False,
        'scope': 'SELECTED_COMPLETE_ARITHMETIC_ONLY'}
    save(directory/'qualification.json', report)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    args = p.parse_args()
    args.inputs, args.baseline, args.output_dir = (v.resolve() for v in (args.inputs, args.baseline, args.output_dir))
    args.output_dir.mkdir(parents=True, exist_ok=False)
    expected = baseline_report(args.baseline)
    reports = []
    for fault in ('positive', 'omitted-prime5', 'omitted-last-node'):
        print('persisted_cache_control_started '+fault, flush=True)
        reports.append(one_case(args.inputs, args.baseline, expected, args.output_dir/fault, fault))
    assert all(report['all_owned_cleanup_verified'] for report in reports)
    save(args.output_dir/'qualification.json', {'status': 'PASS_PERSISTED_FALSE_MATH_REJECTION',
        'positive_completed_first': True, 'cases': reports, 'scope': 'SELECTED_COMPLETE_ARITHMETIC_ONLY',
        'full_source': False, 'matrix_positivity': False, 'production_admission': False})
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
