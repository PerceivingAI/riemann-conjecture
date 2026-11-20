"""Synthetic consumer fixtures; these do not claim scientific execution."""
import hashlib
import json
from pathlib import Path
import runpy

import pytest

from scripts.whole_source.contract import ContractError
from tests.test_whole_source_receipts import stage_receipt


COMPARISON = (Path(__file__).resolve().parents[1] / 'computations' /
    '2026-10-31T124328Z-integrated-reference-qualification' / 'compare-execution-v2.py')


@pytest.fixture(scope='module')
def resources():
    return runpy.run_path(str(COMPARISON))['resources']


def _store(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Noncanonical bytes exercise bindings to the actual retained files.
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def _binding(path):
    raw = path.read_bytes()
    return {'path': str(path.resolve()), 'size': len(raw),
        'sha256': hashlib.sha256(raw).hexdigest()}


def _owner(root, collection='collectionA'):
    receipt = stage_receipt.__wrapped__(root / 'source' / collection)
    value = json.loads(receipt.read_bytes())
    value.update(elapsed_seconds=2, peak_budgeted_memory_bytes=1024)
    value['last_metrics']['cpu_seconds'] = 1
    _store(receipt, value)
    attempt = receipt.parent.parent
    _store(attempt / 'fixture-resources.json', {'sampled_external_increment_bytes': 512})
    _store(attempt / 'fixture-pool-observation.json', {'concurrent_workers_observed': 1})
    return attempt, receipt


def _telemetry(attempt, elapsed=10, state='RUN_COMPLETED'):
    identity = {'format': 'riemann-run-identity-v1', 'run_id': 'synthetic-run',
        'pid': 4242, 'started_at_utc': '2026-10-31T12:43:28Z',
        'driver': 'synthetic-fixture', 'support': '19/40'}
    snapshot = {'format': 'riemann-live-run-v1', 'run_id': identity['run_id'],
        'pid': identity['pid'], 'started_at_utc': identity['started_at_utc'],
        'command': identity['driver'], 'support': identity['support'],
        'terminal': True, 'workflow_state': state, 'elapsed_seconds': elapsed}
    _store(attempt / '.live/run.json', identity)
    _store(attempt / '.live/run-status.json', snapshot)
    return snapshot, identity


def _phase(report, stages=1):
    assert report['owned_receipts_verified'] == stages
    assert report['all_owned_cleanup_verified'] is True
    assert report['completion'] == {
        'scope': 'SELECTED_SUCCESSFUL_OWNED_STAGES_ONLY',
        'whole_source_completion_asserted': False,
        'whole_pipeline_completion_asserted': False,
        'scientific_acceptance_asserted': False,
    }
    assert len(report['stages']) == stages
    for row in report['stages']:
        assert row['elapsed_seconds'] == 2
        assert row['aggregate_owned_cpu_seconds'] in (1, None)
        assert row['peak_owned_committed_bytes'] == 1024
        assert row['sampled_external_increment_bytes'] == 512
        assert row['cleanup_verified'] is True
    phase = report['phases']['source']
    assert phase['stages'] == stages
    assert phase['stage_elapsed_seconds'] == 2 * stages
    assert phase['peak_owned_committed_bytes'] == 1024
    assert phase['peak_sampled_external_increment_bytes'] == 512
    assert phase['configured_cpu_budgets'] == [1]
    assert phase['configured_worker_budgets'] == [1]
    assert phase['configured_native_threads_per_worker'] == [1]
    assert phase['max_concurrently_observed_workers'] == 1
    assert phase['collection_owners'] == stages
    return phase


def _reason(value):
    assert isinstance(value, str) and value.strip()


def _unavailable(phase):
    assert phase['collection_owner_elapsed_available'] is False
    assert phase['collection_owner_elapsed_seconds'] is None
    _reason(phase['collection_owner_elapsed_unavailable_reason'])
    assert phase['aggregate_cpu_per_owner_wall'] is None
    _reason(phase['aggregate_cpu_per_owner_wall_unavailable_reason'])


def _unavailable_owner(timing, attempt):
    assert timing['attempt'] == str(attempt.resolve())
    assert timing['availability'] == 'UNAVAILABLE'
    assert timing['elapsed_seconds'] is None
    _reason(timing['reason'])
    assert 'snapshot' in timing and 'identity' in timing and 'workflow_state' in timing


def test_missing_optional_telemetry_keeps_verified_stage(resources, tmp_path):
    attempt, _ = _owner(tmp_path)
    report = resources(tmp_path)
    phase = _phase(report)
    assert phase['owned_cpu_seconds'] == 1
    _unavailable(phase)
    timing, = phase['owner_timings']
    _unavailable_owner(timing, attempt)
    assert timing['snapshot'] is None
    assert timing['identity'] is None


@pytest.mark.parametrize('state', ['RUN_COMPLETED', 'RUN_FAILED', 'RUN_INTERRUPTED'])
def test_terminal_owner_timing_does_not_assert_source_completion(resources, tmp_path, state):
    attempt, receipt = _owner(tmp_path)
    _telemetry(attempt, state=state)
    report = resources(tmp_path)
    phase = _phase(report)
    assert phase['owned_cpu_seconds'] == 1
    assert report['stages'][0]['aggregate_owned_cpu_seconds'] == 1
    assert phase['collection_owner_elapsed_available'] is True
    assert phase['collection_owner_elapsed_seconds'] == 10
    assert phase['collection_owner_elapsed_unavailable_reason'] is None
    assert phase['aggregate_cpu_per_owner_wall'] == pytest.approx(0.1)
    assert phase['aggregate_cpu_per_owner_wall_unavailable_reason'] is None
    assert phase['owner_timings'] == [{
        'attempt': str(attempt.resolve()), 'availability': 'AVAILABLE', 'reason': None,
        'elapsed_seconds': 10, 'snapshot': _binding(attempt / '.live/run-status.json'),
        'identity': _binding(attempt / '.live/run.json'), 'workflow_state': state,
    }]
    assert report['stages'][0]['receipt'] == _binding(receipt)
    row = report['stages'][0]
    assert row['stage_descriptor'] == _binding(attempt / 'fixture-stage.json')
    assert row['completion'] == _binding(attempt / 'fixture-results/complete.json')
    assert row['completed_results'] == _binding(attempt / 'fixture-results/completed.jsonl')


def test_zero_owner_time_available_but_ratio_unavailable(resources, tmp_path):
    attempt, _ = _owner(tmp_path)
    _telemetry(attempt, elapsed=0.0)
    phase = _phase(resources(tmp_path))
    assert phase['collection_owner_elapsed_available'] is True
    assert phase['collection_owner_elapsed_seconds'] == 0
    assert phase['collection_owner_elapsed_unavailable_reason'] is None
    timing, = phase['owner_timings']
    assert timing['availability'] == 'AVAILABLE'
    assert timing['elapsed_seconds'] == 0
    assert timing['reason'] is None
    assert phase['aggregate_cpu_per_owner_wall'] is None
    _reason(phase['aggregate_cpu_per_owner_wall_unavailable_reason'])


@pytest.mark.parametrize('elapsed', [True, -0.5, float('nan'), float('inf'), None, '10', []],
    ids=['boolean', 'negative', 'nan', 'inf', 'null', 'string', 'list'])
def test_invalid_owner_elapsed_never_substitutes_stage_time(resources, tmp_path, elapsed):
    attempt, _ = _owner(tmp_path)
    _telemetry(attempt, elapsed=elapsed)
    phase = _phase(resources(tmp_path))
    _unavailable(phase)
    _unavailable_owner(phase['owner_timings'][0], attempt)
    assert phase['owned_cpu_seconds'] == 1


@pytest.mark.parametrize('changes', [
    {'terminal': False, 'workflow_state': 'RUNNING'},
    {'terminal': False, 'workflow_state': 'RUN_COMPLETED'},
    {'terminal': 1}, {'workflow_state': 'UNKNOWN'}, {'format': 'other'},
])
def test_nonterminal_or_wrong_format_snapshot_unavailable(resources, tmp_path, changes):
    attempt, _ = _owner(tmp_path)
    snapshot, _ = _telemetry(attempt)
    snapshot.update(changes)
    _store(attempt / '.live/run-status.json', snapshot)
    phase = _phase(resources(tmp_path))
    _unavailable(phase)
    _unavailable_owner(phase['owner_timings'][0], attempt)


@pytest.mark.parametrize('field', ['terminal', 'workflow_state', 'elapsed_seconds', 'format'])
def test_missing_snapshot_fields_unavailable(resources, tmp_path, field):
    attempt, _ = _owner(tmp_path)
    snapshot, _ = _telemetry(attempt)
    del snapshot[field]
    _store(attempt / '.live/run-status.json', snapshot)
    phase = _phase(resources(tmp_path))
    _unavailable(phase)
    _unavailable_owner(phase['owner_timings'][0], attempt)


@pytest.mark.parametrize('filename', ['run-status.json', 'run.json'])
@pytest.mark.parametrize('raw', [b'{broken', b'[]', b'\xff'])
def test_malformed_optional_live_documents_unavailable(resources, tmp_path, filename, raw):
    attempt, _ = _owner(tmp_path)
    _telemetry(attempt)
    (attempt / '.live' / filename).write_bytes(raw)
    phase = _phase(resources(tmp_path))
    _unavailable(phase)
    _unavailable_owner(phase['owner_timings'][0], attempt)


@pytest.mark.parametrize('filename', ['run-status.json', 'run.json'])
def test_missing_one_optional_live_document_unavailable(resources, tmp_path, filename):
    attempt, _ = _owner(tmp_path)
    _telemetry(attempt)
    (attempt / '.live' / filename).unlink()
    phase = _phase(resources(tmp_path))
    _unavailable(phase)
    _unavailable_owner(phase['owner_timings'][0], attempt)


@pytest.mark.parametrize('field,value', [
    ('run_id', 'stale-run'), ('pid', 4243),
    ('started_at_utc', '2026-10-30T12:43:28Z'),
    ('driver', 'another-driver'), ('support', '1/2'),
    ('format', 'other'),
])
def test_identity_mismatch_rejects_stale_owner_telemetry(resources, tmp_path, field, value):
    attempt, _ = _owner(tmp_path)
    _, identity = _telemetry(attempt)
    identity[field] = value
    _store(attempt / '.live/run.json', identity)
    phase = _phase(resources(tmp_path))
    _unavailable(phase)
    _unavailable_owner(phase['owner_timings'][0], attempt)


@pytest.mark.parametrize('field,value', [
    ('run_id', ''), ('started_at_utc', 7),
    ('pid', True), ('pid', 0), ('pid', 4242.0),
])
def test_matching_but_invalid_owner_identity_unavailable(resources, tmp_path, field, value):
    attempt, _ = _owner(tmp_path)
    snapshot, identity = _telemetry(attempt)
    snapshot[field] = identity[field] = value
    _store(attempt / '.live/run-status.json', snapshot)
    _store(attempt / '.live/run.json', identity)
    phase = _phase(resources(tmp_path))
    _unavailable(phase)
    _unavailable_owner(phase['owner_timings'][0], attempt)


@pytest.mark.parametrize('field', ['format', 'run_id', 'pid', 'started_at_utc', 'driver', 'support'])
def test_missing_identity_field_unavailable(resources, tmp_path, field):
    attempt, _ = _owner(tmp_path)
    _, identity = _telemetry(attempt)
    del identity[field]
    _store(attempt / '.live/run.json', identity)
    phase = _phase(resources(tmp_path))
    _unavailable(phase)
    _unavailable_owner(phase['owner_timings'][0], attempt)


def test_all_owners_sum_sorted_timings_without_replacing_stage_metrics(resources, tmp_path):
    later, _ = _owner(tmp_path, 'collectionZ')
    earlier, _ = _owner(tmp_path, 'collectionA')
    _telemetry(later, elapsed=20)
    _telemetry(earlier, elapsed=10)
    phase = _phase(resources(tmp_path), stages=2)
    assert phase['owned_cpu_seconds'] == 2
    assert phase['collection_owner_elapsed_available'] is True
    assert phase['collection_owner_elapsed_seconds'] == 30
    assert phase['collection_owner_elapsed_unavailable_reason'] is None
    assert phase['aggregate_cpu_per_owner_wall'] == pytest.approx(2 / 30)
    assert phase['aggregate_cpu_per_owner_wall_unavailable_reason'] is None
    assert [row['attempt'] for row in phase['owner_timings']] == [
        str(earlier.resolve()), str(later.resolve())]
    assert [row['elapsed_seconds'] for row in phase['owner_timings']] == [10, 20]


def test_mixed_owner_availability_never_reports_partial_sum(resources, tmp_path):
    unavailable, _ = _owner(tmp_path, 'collectionZ')
    available, _ = _owner(tmp_path, 'collectionA')
    _telemetry(available, elapsed=10)
    phase = _phase(resources(tmp_path), stages=2)
    assert phase['owned_cpu_seconds'] == 2
    _unavailable(phase)
    first, second = phase['owner_timings']
    assert first['attempt'] == str(available.resolve())
    assert first['availability'] == 'AVAILABLE'
    assert first['elapsed_seconds'] == 10
    _unavailable_owner(second, unavailable)


def test_missing_cpu_keeps_owner_time_but_not_ratio(resources, tmp_path):
    attempt, receipt = _owner(tmp_path)
    _telemetry(attempt)
    value = json.loads(receipt.read_bytes())
    del value['last_metrics']['cpu_seconds']
    _store(receipt, value)
    report = resources(tmp_path)
    phase = _phase(report)
    assert report['stages'][0]['aggregate_owned_cpu_seconds'] is None
    assert phase['owned_cpu_seconds'] == 0
    assert phase['cpu_counter_missing'] == 1
    assert phase['collection_owner_elapsed_available'] is True
    assert phase['collection_owner_elapsed_seconds'] == 10
    assert phase['collection_owner_elapsed_unavailable_reason'] is None
    assert phase['aggregate_cpu_per_owner_wall'] is None
    _reason(phase['aggregate_cpu_per_owner_wall_unavailable_reason'])


@pytest.mark.parametrize('changes', [
    {'exit_code': 1}, {'error': 'failed'}, {'worker_cleanup_verified': False},
    {'last_metrics': {'active_process_count': 1, 'cpu_seconds': 1}},
])
def test_optional_status_absence_never_weakens_receipt_validation(resources, tmp_path, changes):
    _, receipt = _owner(tmp_path)
    value = json.loads(receipt.read_bytes())
    value.update(changes)
    _store(receipt, value)
    with pytest.raises(ContractError):
        resources(tmp_path)


@pytest.mark.parametrize('relative', [
    'runtime/scripts/whole_source/execution.py', 'runtime/task.py',
    'fixture-results/task.json', 'fixture-results/completed.jsonl',
    'fixture-results/complete.json', 'fixture-stage.json',
])
def test_optional_status_absence_never_hides_bound_artifact_tamper(resources, tmp_path, relative):
    attempt, _ = _owner(tmp_path)
    path = attempt / relative
    if relative.startswith('runtime/'):
        path.write_bytes(path.read_bytes() + b'\n# changed\n')
    else:
        value = json.loads(path.read_bytes())
        if path.name == 'complete.json':
            value['task_count'] += 1
        elif path.name == 'completed.jsonl':
            value['sha256'] = '0' * 64
        elif path.name == 'task.json':
            value['task_id'] = 'another-task'
        else:
            value['attempt_id'] = 'another-attempt'
        _store(path, value)
    with pytest.raises(ContractError):
        resources(tmp_path)


def test_unreadable_optional_snapshot_does_not_hide_verified_stage(resources, tmp_path, monkeypatch):
    attempt, _ = _owner(tmp_path)
    _telemetry(attempt)
    target = attempt / '.live/run-status.json'
    read_bytes = Path.read_bytes

    def denied(path):
        if path == target:
            raise PermissionError('controlled advisory read denial')
        return read_bytes(path)

    monkeypatch.setattr(Path, 'read_bytes', denied)
    phase = _phase(resources(tmp_path))
    _unavailable(phase)
    _unavailable_owner(phase['owner_timings'][0], attempt)
    assert phase['owned_cpu_seconds'] == 1
