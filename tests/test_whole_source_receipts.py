"""Consumer-facing owned receipt discovery and evidence verification."""
from dataclasses import asdict
import hashlib
import json

import pytest

from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes
from scripts.whole_source.execution import ExecutionPlan
from scripts.whole_source.receipts import discover_receipts, verify_stage


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _store(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))
    return path


def _ref(path):
    return ArtifactRef(path.name, _digest(path), path.stat().st_size)


@pytest.fixture
def stage_receipt(tmp_path):
    attempt = tmp_path/'attempt'
    runtime = attempt/'runtime'
    program = runtime/'scripts/whole_source/execution.py'
    program.parent.mkdir(parents=True)
    program.write_bytes(b'# captured runtime\n')
    task_program = runtime/'task.py'
    task_program.write_bytes(b'def evaluate(task): return task\n')
    plan = ExecutionPlan(
        problem_sha256='1'*64, collection_sha256='2'*64, role='producer',
        cpus=1, workers=1, threads=1, memory_mib=64, reserve_mib=0,
        root_mib=1, worker_base_mib=1, worker_private_mib=1,
        native_workspace_mib=0, conversion_mib=0, codec_mib=1, queue_mib=2,
        supervisor_increment_mib=0, repository_mib=1, temporary_mib=1,
        minimum_free_mib=0, max_tasks=1, task_bytes=1024, result_bytes=1024,
        log_bytes=1024, task_program=_ref(task_program), task_function='evaluate',
        precision_bits=64, backend='integer-rational', backend_version='fixture',
        provenance=ArtifactRef('provenance.json', '3'*64, 1))
    tasks = _store(attempt/'fixture-tasks.jsonl', {'task_id': 'task'})
    result_dir = attempt/'fixture-results'
    payload = _store(result_dir/'task.json', {
        'execution_id': plan.execution_id, 'attempt_id': attempt.name,
        'collection_id': plan.collection_sha256, 'problem_id': plan.problem_sha256,
        'scope': plan.scope, 'task_id': 'task'})
    inventory = _store(result_dir/'completed.jsonl', asdict(_ref(payload)))
    _store(result_dir/'complete.json', {'execution_id': plan.execution_id,
        'task_count': 1, 'inventory_sha256': _digest(inventory)})
    stage = _store(attempt/'fixture-stage.json', {'plan': plan.to_dict(),
        'attempt_id': attempt.name, 'task_file': str(tasks), 'task_sha256': _digest(tasks),
        'task_count': 1, 'result_dir': str(result_dir)})
    config = _store(attempt/'execution-budget.json', {'fixture': True})
    profile = _store(attempt/'profile.json', {'exit_code': 0, 'error': None,
        'program_sha256': _digest(program)})
    logs = {}
    for name in ('stdout', 'stderr'):
        path = attempt/(name+'.txt')
        path.write_bytes(b'')
        logs[name] = asdict(_ref(path))
    receipt = _store(attempt/'fixture/receipt.json', {
        'format': 't081-owned-stage-receipt-v1', 'stage': 'fixture',
        'argv': ['fixture', '--stage', str(stage), '--stage-sha256', _digest(stage),
                 '--program', str(program), '--config', str(config), '--profile', str(profile)],
        'exit_code': 0, 'error': None, 'worker_cleanup_verified': True,
        'last_metrics': {'active_process_count': 0}, 'program_sha256': _digest(program),
        'config_sha256': _digest(config), 'logs': logs})
    return receipt


def test_verified_stage_exposes_bound_evidence(stage_receipt):
    verified = verify_stage(stage_receipt)
    assert set(verified) == {'record', 'stage', 'plan'}
    assert verified['stage']['plan'] == verified['plan'].to_dict()
    assert verified['record'] == {'directory': str(stage_receipt.parent),
                                  'artifact': asdict(_ref(stage_receipt))}
    assert discover_receipts(stage_receipt.parent.parent) == [stage_receipt]


def test_missing_result_is_rejected(stage_receipt):
    (stage_receipt.parent.parent/'fixture-results/task.json').unlink()
    with pytest.raises((ContractError, OSError)):
        verify_stage(stage_receipt)


@pytest.mark.parametrize('changes', [
    {'exit_code': 1}, {'error': 'failed'}, {'worker_cleanup_verified': False},
    {'last_metrics': {'active_process_count': 1}},
])
def test_discovery_keeps_failed_but_verification_rejects(stage_receipt, changes):
    value = json.loads(stage_receipt.read_bytes())
    value.update(changes)
    _store(stage_receipt, value)
    assert discover_receipts(stage_receipt.parent.parent) == [stage_receipt]
    with pytest.raises(ContractError, match='failed/uncontained owned scientific stage'):
        verify_stage(stage_receipt)


@pytest.mark.parametrize('relative', ['runtime/scripts/whole_source/execution.py', 'runtime/task.py'])
def test_captured_code_tamper_is_rejected(stage_receipt, relative):
    (stage_receipt.parent.parent/relative).write_bytes(b'changed\n')
    with pytest.raises(ContractError):
        verify_stage(stage_receipt)


def test_unknown_receipt_is_not_selected(tmp_path):
    path = _store(tmp_path/'receipt.json', {'format': 'other'})
    assert discover_receipts(tmp_path) == []
    with pytest.raises(ContractError, match='unrecognized owned stage receipt format'):
        verify_stage(path)
