"""Qualify actual selected arithmetic interruption/recovery; never full-source proof."""
from __future__ import annotations
import argparse
from copy import deepcopy
import ctypes
from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source.contract import ArtifactRef, bind_problem, canonical_bytes
from scripts.whole_source.artifacts import (
    CollectionLock, CollectionSpec, ChunkStore, StagedChunk, _task, _decode_chunk,
    decode_rational, encode_rational,
)
from scripts.whole_source.execution import ExecutionPlan, WorkloadExecution, _RUNTIME, BUNDLE, _HELPERS
from scripts.whole_source.slice import check_entries


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(canonical_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())


def read(path):
    return json.loads(path.read_bytes())


def receipt(root):
    state = read(root/'slice-state.json')
    assert state['status'] == 'VERIFIED_SELECTED_COMPLETE_ARITHMETIC', state
    ref = state['receipt']
    raw = (root/ref['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ref['sha256'] and len(raw) == ref['size']
    return json.loads(raw)


def command(inputs, output, *, root=ROOT, stop=None):
    result = [sys.executable, '-B', '-m', 'scripts.weil_whole_source_split', 'slice']
    for name in ('problem', 'cases', 'execution'):
        result += ['--'+name, str(inputs/(name+'.json'))]
    result += ['--output-dir', str(output), '--source-root', str(root), '--resume']
    if stop:
        result += ['--qualification-stop', stop]
    return result


def execute(inputs, output, label, logs, *, root=ROOT, expected=0):
    logs.mkdir(parents=True, exist_ok=True)
    with (logs/(label+'.stdout')).open('xb') as stdout, (logs/(label+'.stderr')).open('xb') as stderr:
        started = time.monotonic()
        run = subprocess.run(command(inputs, output, root=root), cwd=ROOT, stdout=stdout, stderr=stderr)
    assert run.returncode == expected, (label, run.returncode, (logs/(label+'.stderr')).read_text())
    return {'exit_code': run.returncode, 'wall_ms': int(1000*(time.monotonic()-started))}


def seed(baseline, target, *, pending=False):
    target.mkdir()
    shutil.copyfile(baseline/'slice-context.json', target/'slice-context.json')
    (target/'acceptances').mkdir()
    shutil.copytree(baseline/'producer', target/'producer')
    state = read(target/'producer/collection.json')
    head = state['index']
    while read(target/'producer'/head['path'])['event']['kind'] != 'chunk':
        head = read(target/'producer'/head['path'])['previous']
    if pending:
        # Rewind one complete six-entry node-block publication group. Its native
        # evaluation must actually run again; all other compatible chunks remain.
        for _ in range(6):
            head = read(target/'producer'/head['path'])['previous']
    state['index'] = head
    (target/'producer/collection.json').write_bytes(canonical_bytes(state))
    return state


def index_state(root):
    state = read(root/'producer/collection.json')
    counts = {'chunk': 0, 'prefix': 0, 'quantity': 0, 'source': 0}
    head = state['index']
    while head:
        node = read(root/'producer'/head['path'])
        counts[node['event']['kind']] += 1
        head = node['previous']
    return counts


def terminate_owned(pid):
    # PID comes from the bound actual writer barrier, not a broad process search.
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.TerminateProcess.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x0001 | 0x00100000, False, pid)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        if not kernel.TerminateProcess(handle, 91):
            raise ctypes.WinError(ctypes.get_last_error())
        assert kernel.WaitForSingleObject(handle, 30000) == 0
    finally:
        kernel.CloseHandle(handle)


def interrupt(inputs, output, point, logs):
    with (logs/(point+'.stdout')).open('xb') as stdout, (logs/(point+'.stderr')).open('xb') as stderr:
        process = subprocess.Popen(command(inputs, output, stop=point), cwd=ROOT, stdout=stdout, stderr=stderr)
        deadline = time.monotonic()+300
        marker = None
        while marker is None:
            markers = list((output/'producer/attempts').glob('*/barrier-reached.json'))
            if markers:
                marker = markers[0]
                break
            assert process.poll() is None, (point, process.returncode, (logs/(point+'.stderr')).read_text())
            if time.monotonic() > deadline:
                process.terminate()
                raise TimeoutError('qualification barrier did not arrive: '+point)
            time.sleep(0.02)
        barrier = read(marker)
        before = index_state(output)
        terminate_owned(barrier['pid'])
        if process.poll() is None:
            process.wait(timeout=120)
        assert process.returncode != 0
    state = read(output/'slice-state.json')
    assert state['status'] != 'VERIFIED_SELECTED_COMPLETE_ARITHMETIC'
    assert before['source'] == 0
    return {'barrier': barrier, 'committed_before_interrupt': before,
            'interrupted_exit': process.returncode, 'latest_state': state,
            'limits': 'actual process interruption; no power-loss claim'}


def same_math(expected, actual):
    assert actual['entries'] == expected['entries']
    for role in ('producer', 'analytic'):
        assert actual['roles'][role]['quantity_seals'] == expected['roles'][role]['quantity_seals']
        assert actual['roles'][role]['preparation'] == expected['roles'][role]['preparation']
    assert actual['all_owned_cleanup_verified'] and not actual['full_mathematical_source']


def mathematical_controls(baseline, expected, output):
    problem = bind_problem('retained-t081')
    source, independent = expected['roles']['producer']['entries'], expected['roles']['analytic']['entries']
    check_entries(problem, source, independent)
    collection = baseline/'producer'
    partial = {'prime': [Fraction(0), Fraction(0)], 'window': [Fraction(0), Fraction(0)],
               'four': [Fraction(0), Fraction(0)], 'node': [Fraction(0), Fraction(0)]}
    spec = CollectionSpec.from_dict(problem, read(collection/'collection.json')['collection'])
    head = read(collection/'collection.json')['index']
    while head:
        event = read(collection/head['path'])
        if event['event']['kind'] == 'chunk':
            task = _task(event['event']['task'])
            if task.quantity.entry == (0, 0):
                ref = event['event']['artifact']
                chunk = _decode_chunk(spec, (collection/ref['path']).read_bytes())
                for record in chunk.records:
                    term, window, node = record.contribution
                    kinds = []
                    if term == 3: kinds.append('prime')
                    if window == 1: kinds.append('window')
                    if term == 2: kinds.append('four')
                    if term == 3 and window == 1 and node == problem.source_gauss_order-1: kinds.append('node')
                    for kind in kinds:
                        partial[kind][0] += record.lower
                        partial[kind][1] += record.upper
        head = event['previous']
    results = []
    for name in ('prime', 'window', 'four', 'node', 'sign', 'mass', 'head-low'):
        bad = deepcopy(source)
        lo, hi = (decode_rational(bad[0][key], 8192) for key in ('lower', 'upper'))
        if name in ('prime', 'window', 'node'):
            lower, upper = partial[name]
            lo, hi = lo-upper, hi-lower
        elif name == 'four':
            lower, upper = partial['four']
            lo, hi = lo+lower, hi+upper  # log4 = 2log2: a genuine wrong coefficient.
        elif name == 'sign':
            lo, hi = -hi, -lo
        elif name == 'mass':
            bad[-1]['mass'] = encode_rational(Fraction(2, 2*(problem.N-1)+1), 8192)
        else:
            mass = Fraction(2, 2*(problem.N-1)+1)
            bad[-1]['expansion'] = [encode_rational(decode_rational(bad[-1][key], 8192)/mass, 8192)
                                    for key in ('lower', 'upper')]
        bad[0]['lower'], bad[0]['upper'] = encode_rational(lo, 8192), encode_rational(hi, 8192)
        candidate = {'format': 'untrusted-complete-arithmetic-candidate-v1', 'entries': bad,
                     'scope': 'DELIBERATELY_FALSE_MATH_CONTROL', 'fault': name}
        path = output/(name+'.json')
        write(path, candidate)
        raw = path.read_bytes()
        rebound = json.loads(raw)
        try:
            check_entries(problem, rebound['entries'], independent)
        except ValueError as exc:
            results.append({'fault': name, 'candidate_sha256': hashlib.sha256(raw).hexdigest(),
                            'candidate_size': len(raw), 'rejection': str(exc),
                            'checker': 'exact physical containment/mass, not a hash/schema rejection'})
        else:
            raise AssertionError('false mathematical candidate accepted: '+name)
    write(output/'controls.json', {'positive_control_passed_first': True, 'cases': results})
    return results


def native_mathematical_controls(inputs, expected, directory):
    """Compute actual complete wrong-power/shift and wide-precision proposals."""
    directory.mkdir(parents=True)
    problem = bind_problem('retained-t081')
    role = read(inputs/'execution.json')['roles']['analytic']
    original = CollectionSpec.from_dict(problem, role['collection'])
    path = (Path(__file__).parent/'false-arithmetic-worker-v1.py').relative_to(ROOT).as_posix()
    raw = (ROOT/path).read_bytes()
    program = ArtifactRef(path, hashlib.sha256(raw).hexdigest(), len(raw))
    refs = tuple(sorted((*original.code_refs, program), key=lambda ref: ref.path))
    spec = CollectionSpec.create(problem, role='analytic', quantities=original.quantities,
        partition=original.partition, backend=original.backend, backend_version=original.backend_version,
        native_threads=original.native_threads, code_refs=refs, bounds=original.bounds)
    old = ExecutionPlan.from_dict(role['execution'])
    origin = read(ROOT/old.provenance.path)
    origin['files'] = [asdict(ref) for ref in refs]
    origin_path = directory/'origin.json'
    write(origin_path, origin)
    origin_raw = origin_path.read_bytes()
    provenance = ArtifactRef(origin_path.relative_to(ROOT).as_posix(), hashlib.sha256(origin_raw).hexdigest(), len(origin_raw))
    plan = replace(old, collection_sha256=spec.collection_id, task_program=program, provenance=provenance)
    write(directory/'execution.json', {'collection': spec.to_dict(), 'execution': plan.to_dict()})
    failures = []
    with CollectionLock.acquire(directory/'collection', spec) as lock:
        with WorkloadExecution(lock, spec, plan) as execution:
            requests = []
            for fault in ('omit-power', 'reverse-shift', 'premature-arithmetic-grid'):
                request = {'operation': 'false-quantity', 'fault': fault}
                requests.append({'task_id': hashlib.sha256(canonical_bytes(request)).hexdigest(), **request})
            execution.run_stage('false_native_quantities', requests)
            for result in execution.read_results('false_native_quantities'):
                value = result['result']
                bad = deepcopy(expected['roles']['producer']['entries'])
                index = next(i for i, row in enumerate(bad) if row['quantity']['entry'] == value['entry'])
                scale = 1 << 512
                lo, hi = (decode_rational(value[key], 8192) for key in ('lower', 'upper'))
                bad[index]['lower'] = encode_rational(Fraction((lo*scale).__floor__()-1, scale), 8192)
                bad[index]['upper'] = encode_rational(Fraction((hi*scale).__ceil__()+1, scale), 8192)
                candidate = {'entries': bad, 'native_false_quantity': value, 'scope': 'DELIBERATE_REJECTION_CONTROL'}
                path = directory/(value['fault']+'.json')
                write(path, candidate)
                consumed = path.read_bytes()
                try:
                    check_entries(problem, json.loads(consumed)['entries'], expected['roles']['analytic']['entries'])
                except ValueError as exc:
                    failures.append({'fault': value['fault'], 'candidate_sha256': hashlib.sha256(consumed).hexdigest(),
                        'rejection': str(exc), 'complete_signed_windows': 8, 'full_low_powers': problem.N,
                        'native_bits': value['evaluated_bits'], 'owned_worker_pid': result['pid']})
                else:
                    raise AssertionError('native false complete arithmetic accepted: '+value['fault'])
            assert all(row['worker_cleanup_verified'] for row in execution.receipts)
    write(directory/'qualification.json', {'positive_control': 'independent accepted baseline',
        'cases': failures, 'all_owned_cleanup_verified': True, 'scope': 'SELECTED_ARITHMETIC_REJECTION_CONTROLS'})
    return failures


def retry_and_stale_controls(inputs, baseline, directory):
    """Submit actual old native output and correct-hash conflicting bytes."""
    directory.mkdir()
    target = directory/'collection-run'
    seed(baseline, target)
    problem = bind_problem('retained-t081')
    row = read(inputs/'execution.json')['roles']['producer']
    spec = CollectionSpec.from_dict(problem, row['collection'])
    response_path = next((baseline/'producer/attempts').glob('*/arithmetic-results/*.json'))
    response = read(response_path)
    wire = response['result']['chunks'][0]
    task = _task(wire['task'])
    oldref = ArtifactRef(**wire['ref'])
    raw = (baseline/'producer/chunks'/oldref.sha256).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == oldref.sha256 and len(raw) == oldref.size
    oldpath = target/'producer'/oldref.path
    oldpath.parent.mkdir(parents=True, exist_ok=True)
    oldpath.write_bytes(raw)
    results = {}
    with CollectionLock.acquire(target/'producer', spec, resume=True) as lock:
        name = 'actual_late_response_control'
        (lock.root/'attempts'/name).mkdir()
        lock.register_attempt(name)
        store = ChunkStore(lock, spec, attempt_id=name)
        before = (lock.root/'collection.json').read_bytes()
        committed = store.recover_staged_chunk(task, oldref)
        assert committed.sha256 == oldref.sha256 and (lock.root/'collection.json').read_bytes() == before
        results['identical_actual_retry'] = {'same_raw_bytes': True, 'no_new_index_or_contribution': True,
                                           'raw_ref': asdict(committed)}
        late = StagedChunk(oldpath, task, oldref, wire['generation'], wire['attempt_id'])
        try:
            store.publish_chunk(task, late)
        except ValueError as exc:
            assert 'stale staged context' in str(exc)
            results['stale_actual_native_response'] = {'rejection': str(exc),
                'actual_original_worker_response': response_path.relative_to(ROOT).as_posix(),
                'old_generation': wire['generation'], 'current_generation': lock.generation,
                'correct_consumed_payload_sha256': oldref.sha256,
                'scope': 'replayed real old worker output, not a delayed live worker claim'}
        else:
            raise AssertionError('stale actual native output published')
        snapshot = _decode_chunk(spec, raw)
        records = list(snapshot.records)
        first = records[0]
        records[0] = replace(first, lower=first.lower+1, upper=first.upper+1)
        staged = store.stage_chunk(task, records)
        try:
            store.publish_chunk(task, staged)
        except ValueError as exc:
            assert 'conflicting identical-task retry' in str(exc)
            results['conflicting_correct_hash_retry'] = {'rejection': str(exc), 'raw_ref': asdict(staged.ref)}
        else:
            raise AssertionError('conflicting complete scientific retry accepted')
        assert (lock.root/'collection.json').read_bytes() == before
    write(target/'slice-state.json', {'status': 'QUARANTINED_DELIBERATE_CONFLICT_CONTROL',
          'scientific_acceptance': False, 'scope': 'REJECTION_CONTROL'})
    write(directory/'qualification.json', results)
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    args = p.parse_args()
    args.inputs, args.baseline, args.output_dir = (path.resolve() for path in (args.inputs, args.baseline, args.output_dir))
    args.output_dir.mkdir(parents=True, exist_ok=False)
    logs = args.output_dir/'logs'
    logs.mkdir()
    expected = receipt(args.baseline)
    cuts = [('K01', 'payload-writing'), ('K02', 'payload-closed'), ('K03', 'chunk-published'),
            ('K04', 'index-writing'), ('K05', 'prefix-committed'), ('K06', 'prefix-acknowledgement'),
            ('K07', 'slice-before-seal'), ('K08', 'native-running')]
    outcomes = []
    for label, point in cuts:
        target = args.output_dir/label
        seed(args.baseline, target, pending=label in ('K01', 'K02', 'K03', 'K08'))
        print(json.dumps({'event': 'recovery_cut_started', 'cut': label, 'point': point}), flush=True)
        stopped = interrupt(args.inputs, target, point, logs)
        result = execute(args.inputs, target, label+'-resume', logs)
        actual = receipt(target)
        same_math(expected, actual)
        outcome = {'cut': label, 'interruption': stopped, 'resume': result, 'same_canonical_endpoints': True,
                   'same_quantity_seals': True, 'all_owned_cleanup_verified': actual['all_owned_cleanup_verified']}
        write(target/'qualification.json', outcome)
        outcomes.append(outcome)
    math = mathematical_controls(args.baseline, expected, args.output_dir/'mathematical-controls')
    native_math = native_mathematical_controls(args.inputs, expected, args.output_dir/'native-mathematical-controls')
    retries = retry_and_stale_controls(args.inputs, args.baseline, args.output_dir/'retry-and-late-controls')
    write(args.output_dir/'partial-qualification.json', {'status': 'EIGHT_INTERRUPTION_CUTS_AND_TEN_MATH_CONTROLS_CHECKED',
          'cuts': outcomes, 'mathematical_controls': math, 'native_mathematical_controls': native_math,
          'retry_and_late_output': retries,
          'scope': 'SELECTED_COMPLETE_ARITHMETIC_ONLY',
          'remaining_controls': ['ownership', 'corruption', 'injected_io', 'changed_context', 'fresh_oracle_isolation']})
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
