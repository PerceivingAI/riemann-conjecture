"""Exercise the real CLI coordinator with fabricated, self-consistent role caches."""
from __future__ import annotations
import argparse
from dataclasses import asdict
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source.contract import bind_problem, canonical_bytes, problem_id
from scripts.whole_source.artifacts import Axis, CollectionLock, CollectionSpec, ContributionTask, ChunkStore, IntervalRecord
from scripts.whole_source.slice import prepare_inputs, run_slice


def save(path, value):
    with path.open('xb') as stream:
        stream.write(canonical_bytes(value))


def seed(collection, spec):
    with CollectionLock.acquire(collection, spec) as lock:
        attempt = 'untrusted_submission'
        (collection/'attempts'/attempt).mkdir()
        lock.register_attempt(attempt)
        store = ChunkStore(lock, spec, attempt_id=attempt)
        for quantity in spec.quantities:
            blocks = []
            for axis in quantity.axes:
                width = dict(spec.partition)[axis.name]
                blocks.append([Axis(axis.name, start, min(axis.stop, start+width*axis.step), axis.step)
                               for start in range(axis.start, axis.stop, width*axis.step)])
            for axes in product(*blocks):
                task = ContributionTask(quantity.key, quantity.rows, quantity.columns, axes)
                m, n = quantity.key.entry
                records = (IntervalRecord(m, n, tuple(coordinate), Fraction(0), Fraction(0))
                           for coordinate in product(*(tuple(axis) for axis in axes)))
                store.publish_chunk(task, store.stage_chunk(task, records))
        lock.invalidate_attempt(attempt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--expect-rejected', action='store_true')
    args = parser.parse_args()
    directory = args.output_dir.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    problem = bind_problem('retained-t081')
    paths = prepare_inputs(problem, directory/'inputs', origin_git_commit='a7d43f501cd7cf6ea74360c4092ecaa11392dbef', origin_git_dirty=True)
    cases, config = (json.loads(paths[name].read_bytes()) for name in ('cases', 'execution'))
    output = directory/'collection'
    output.mkdir()
    (output/'acceptances').mkdir()
    save(output/'slice-context.json', {'format': 'whole-source-arithmetic-slice-context-v1',
        'problem_id': problem_id(problem), 'cases_sha256': hashlib.sha256(canonical_bytes(cases)).hexdigest(),
        'execution_sha256': hashlib.sha256(canonical_bytes(config)).hexdigest(), 'scope': 'SELECTION_ONLY'})
    for role in ('producer', 'analytic'):
        spec = CollectionSpec.from_dict(problem, config['roles'][role]['collection'])
        seed(output/role, spec)
    try:
        result = run_slice(paths['problem'], paths['cases'], paths['execution'], output, resume=True)
    except ValueError as exc:
        assert args.expect_rejected and 'conflicting' in str(exc), str(exc)
        state = json.loads((output/'slice-state.json').read_bytes())
        assert state['status'] == 'FAILED_NO_SCIENTIFIC_ACCEPTANCE'
        verdict = {'status': 'PASS_FABRICATED_DUAL_CACHE_REJECTED', 'error': str(exc), 'scientific_acceptance': False}
    else:
        assert not args.expect_rejected, 'fabricated dual cache was accepted'
        assert result['status'] == 'VERIFIED_SELECTED_COMPLETE_ARITHMETIC'
        verdict = {'status': 'VULNERABLE_ACCEPTED_FABRICATED_ZERO_ARITHMETIC',
                   'accepted_entries': len(result['entries']), 'first_entry': result['entries'][0]}
    save(directory/'verdict.json', verdict)
    print(json.dumps(verdict, sort_keys=True))


if __name__ == '__main__':
    main()
