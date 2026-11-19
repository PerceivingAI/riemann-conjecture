"""Consumer-visible integrity of committed dependency-wave evidence."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes
from scripts.whole_source.task_groups import GROUP, group_receipt, read_group, seal_group
from tests.test_whole_source_receipts import stage_receipt, _store, _ref, _digest


@pytest.fixture
def group_case(tmp_path, *, portable=True):
    root = tmp_path/'collection'
    receipt = stage_receipt.__wrapped__(root/'attempts')
    attempt = receipt.parent.parent
    result_path = attempt/'fixture-results/task.json'
    payload = json.loads(result_path.read_bytes())
    report = {'scope': 'CONTROL_ONLY', 'complete_rows': ['-3/7', '5/9']}
    payload['result'] = {'report': report}
    _store(result_path, payload)
    inventory = _store(attempt/'fixture-results/completed.jsonl', asdict(_ref(result_path)))
    complete = json.loads((attempt/'fixture-results/complete.json').read_bytes())
    complete['inventory_sha256'] = _digest(inventory)
    _store(attempt/'fixture-results/complete.json', complete)
    if portable:
        stage_path = attempt/'fixture-stage.json'
        stage = json.loads(stage_path.read_bytes())
        stage.update(format='whole-source-task-stage-v3',
                     task_file='fixture-tasks.jsonl', result_dir='fixture-results',
                     attachment_path='fixture-attachment.json', generation=1,
                     artifact_context={'attempt_id': attempt.name, 'generation': 1})
        _store(stage_path, stage)
        profile = attempt/'fixture/profile.json'
        (attempt/'profile.json').replace(profile)
        value = json.loads(receipt.read_bytes())
        del value['argv'], value['logs']
        value.update(format='whole-source-owned-stage-receipt-v3', stage_sha256=_digest(stage_path),
                     profile_sha256=_digest(profile), budget={'fixture': True})
        _store(receipt, value)
    def immutable(folder, raw):
        name = folder+'/'+hashlib.sha256(raw).hexdigest()
        path = root/name
        path.parent.mkdir(exist_ok=True)
        with path.open('xb') as stream:
            stream.write(raw)
        return ArtifactRef(name, hashlib.sha256(raw).hexdigest(), len(raw))
    lock = SimpleNamespace(root=root, spec=SimpleNamespace(collection_id='2'*64), _immutable=immutable)
    execution = SimpleNamespace(output=attempt, attempt_id=attempt.name)
    value = immutable('seals', canonical_bytes(report))
    context = {'problem_id': '1'*64, 'parity': 0, 'operation': 'CONTROL_ONLY'}
    return lock, execution, context, {'report': asdict(value)}, receipt


def test_completed_result_report_can_be_consumed_with_its_stage(group_case):
    lock, execution, context, outputs, receipt = group_case
    record = seal_group(lock, execution, 'fixture', context, outputs)
    descriptor = json.loads((lock.root/record['artifact']['path']).read_bytes())
    assert descriptor['format'] == GROUP
    assert descriptor['stage'] == asdict(ArtifactRef('attempts/attempt/fixture/receipt.json',
                                                      _digest(receipt), receipt.stat().st_size))
    assert group_receipt(record) == {'directory': str(receipt.parent), 'artifact': asdict(_ref(receipt))}
    root, verified = read_group(record, context)
    assert root == lock.root and verified == outputs
    report = json.loads((root/verified['report']['path']).read_bytes())
    assert report['complete_rows'] == ['-3/7', '5/9']


def test_unreported_but_existing_output_is_not_authorized(group_case):
    lock, execution, context, _, _ = group_case
    orphan = lock._immutable('seals', canonical_bytes({'scope': 'CONTROL_ONLY', 'unreported': True}))
    with pytest.raises(ContractError, match='successful owned result authority'):
        seal_group(lock, execution, 'fixture', context, {'report': asdict(orphan)})


@pytest.mark.parametrize('target', ['output', 'receipt', 'result', 'task-program'])
def test_committed_group_revalidates_consumed_evidence(group_case, target):
    lock, execution, context, outputs, receipt = group_case
    record = seal_group(lock, execution, 'fixture', context, outputs)
    path = {'output': lock.root/outputs['report']['path'], 'receipt': receipt,
            'result': execution.output/'fixture-results/task.json',
            'task-program': execution.output/'runtime/task.py'}[target]
    path.write_bytes(b'CONTROL_ONLY deliberate corruption')
    with pytest.raises((ContractError, OSError, ValueError, KeyError)):
        read_group(record, context)


def test_other_parity_cannot_consume_same_group(group_case):
    lock, execution, context, outputs, _ = group_case
    record = seal_group(lock, execution, 'fixture', context, outputs)
    with pytest.raises(ContractError, match='context'):
        read_group(record, {**context, 'parity': 1})


def test_failed_stage_cannot_commit_preexisting_results(group_case):
    lock, execution, context, outputs, receipt = group_case
    value = json.loads(receipt.read_bytes())
    value['exit_code'] = 1
    _store(receipt, value)
    with pytest.raises(ContractError, match='failed/uncontained'):
        seal_group(lock, execution, 'fixture', context, outputs)


def test_another_execution_attempt_cannot_adopt_completed_group(group_case):
    lock, execution, context, outputs, _ = group_case
    record = seal_group(lock, execution, 'fixture', context, outputs)
    with pytest.raises(ContractError, match='another execution attempt'):
        read_group(record, context, expected_root=lock.root, expected_attempt='new-attempt')


def test_another_execution_root_cannot_adopt_completed_group(group_case, tmp_path):
    lock, execution, context, outputs, _ = group_case
    record = seal_group(lock, execution, 'fixture', context, outputs)
    foreign = tmp_path/'another-execution'
    foreign.mkdir()
    with pytest.raises(ContractError, match='another execution root'):
        read_group(record, context, expected_root=foreign, expected_attempt=execution.attempt_id)
