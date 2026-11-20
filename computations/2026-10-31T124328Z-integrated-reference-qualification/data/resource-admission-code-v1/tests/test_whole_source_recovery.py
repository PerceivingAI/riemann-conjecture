"""Recovery consumer controls. Synthetic receipts here make no Weil claim."""
from dataclasses import asdict
import hashlib
import json
from types import SimpleNamespace

import pytest

from scripts.whole_source import recovery
from scripts.whole_source.artifacts import CollectionLock
from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes
from scripts.whole_source.recovery import RecoveryJournal, operation_context
from scripts.whole_source.task_groups import read_group, seal_group, same_group
from tests.test_whole_source_artifacts import collection, code_refs, problem
from tests.test_whole_source_task_groups import group_case
from tests.test_whole_source_receipts import _store


class ControlOwner:
    """Filesystem owner double around the real typed receipt/group codec."""
    def __init__(self, root):
        self.root = root
        root.mkdir(parents=True)
        (root/'attempts').mkdir()
        (root/'.volume.lock').touch()
        self.spec = SimpleNamespace(collection_id='2'*64)
        self.generation = 1
        self._attempts = {}

    def _check(self, *, attempt_id=None):
        if attempt_id is not None and attempt_id not in self._attempts:
            raise ContractError('unregistered control owner')

    def _exclusive(self, name, raw):
        path = self.root/name
        path.parent.mkdir(exist_ok=True)
        with path.open('xb') as stream:
            stream.write(raw)

    def _immutable(self, folder, raw):
        digest = hashlib.sha256(raw).hexdigest()
        name = folder+'/'+digest
        path = self.root/name
        if path.exists():
            assert path.read_bytes() == raw
        else:
            self._exclusive(name, raw)
        return ArtifactRef(name, digest, len(raw))

    def attempt(self, name):
        self._attempts[name] = self._immutable('owners', canonical_bytes({
            'attempt_id': name, 'generation': self.generation,
            'collection_id': self.spec.collection_id}))
        return name


@pytest.fixture
def committed(tmp_path):
    root = tmp_path/'collection'
    owner = ControlOwner(root)
    context = operation_context('exact', tmp_path, {'kind': 'SYNTHETIC_NONPROOF_CONTROL'})
    journal = RecoveryJournal(owner, context)
    # The common receipt fixture supplies a closed ExecutionPlan, actual raw
    # programs/tasks/results/profile/streams, but does not launch mathematics.
    lock, execution, group_context, outputs, receipt = group_case.__wrapped__(tmp_path)
    group = seal_group(lock, execution, 'fixture', group_context, outputs)
    journal.commit('first', group, {'outputs': outputs})
    return owner, journal, context, group_context, group, outputs, receipt


def test_multiple_adoptions_preserve_original_task_and_receipt_bytes(committed):
    owner, journal, context, gc, group, outputs, receipt = committed
    before = {p: p.read_bytes() for p in owner.root.rglob('*') if p.is_file() and
              'recovery' not in p.parts}
    for number in range(2):
        owner.generation += 1
        retry = RecoveryJournal(owner, context, resume=True)
        attempt = owner.attempt('retry-'+str(number))
        adopted = retry.adopt('first', attempt_id=attempt)
        assert read_group(adopted, gc, expected_root=owner.root,
                          expected_attempt=attempt) == (owner.root, outputs)
        assert same_group(adopted, group)
        assert retry.receipts() == recovery.selected_receipts(owner.root)
        assert retry.receipts()[0]['directory'] == str(receipt.parent)
    assert all(path.read_bytes() == raw for path, raw in before.items())


@pytest.mark.parametrize('change', ['attempt', 'root', 'context'])
def test_adopted_consumer_rejects_foreign_identity(committed, tmp_path, change):
    owner, journal, _, gc, _, _, _ = committed
    adopted = journal.adopt('first', attempt_id=owner.attempt('retry'))
    other = tmp_path/'foreign'
    other.mkdir()
    with pytest.raises(ContractError):
        read_group(adopted, {**gc, 'parity': 1} if change == 'context' else gc,
                   expected_root=other if change == 'root' else owner.root,
                   expected_attempt='foreign' if change == 'attempt' else 'retry')


@pytest.mark.parametrize('change', ['origin', 'cycle', 'owner'])
def test_tampered_adoption_cannot_create_new_authority(committed, change):
    owner, journal, _, gc, _, _, _ = committed
    adopted = journal.adopt('first', attempt_id=owner.attempt('retry'))
    document = json.loads((owner.root/adopted['artifact']['path']).read_bytes())
    if change == 'owner':
        document['attempt_id'] = 'foreign'
    elif change == 'cycle':
        document['origin'] = adopted
    else:
        document['origin'] = {**document['origin'], 'root': str(owner.root.parent)}
    altered = {'root': str(owner.root), 'artifact': asdict(owner._immutable(
        'recovery', canonical_bytes(document)))}
    # Even append-only, correctly hashed but uncommitted wrappers reject.
    with pytest.raises(ContractError):
        read_group(altered, gc, expected_root=owner.root, expected_attempt='retry')
    # A maliciously committed wrapper still cannot substitute its origin.
    journal._append('adoption', 'first', {'artifact': altered['artifact']})
    with pytest.raises(ContractError):
        read_group(altered, gc, expected_root=owner.root, expected_attempt='retry')


def test_corrupt_committed_operand_rejects_without_repair(committed):
    owner, journal, context, _, _, outputs, _ = committed
    path = owner.root/outputs['report']['path']
    path.write_bytes(b'SYNTHETIC_CONTROL_CORRUPTION')
    with pytest.raises(ContractError):
        RecoveryJournal(owner, context, resume=True).get('first')
    assert path.read_bytes() == b'SYNTHETIC_CONTROL_CORRUPTION'


def test_duplicate_checkpoint_and_stale_head_reject(committed):
    owner, journal, context, _, group, outputs, _ = committed
    with pytest.raises(ContractError, match='already committed'):
        journal.commit('first', group, {'outputs': outputs, 'conflicting': True})
    stale = RecoveryJournal(owner, context, resume=True)
    journal.adopt('first')
    with pytest.raises(ContractError, match='head'):
        stale.get('first')


def test_group_and_record_without_head_are_not_adopted(committed, monkeypatch):
    owner, journal, context, _, group, outputs, _ = committed
    previous = (owner.root/'recovery/head.json').read_bytes()
    def interrupted(*args):
        raise OSError('control before atomic journal head')
    monkeypatch.setattr(journal, '_replace', interrupted)
    with pytest.raises(OSError):
        journal.commit('second', group, {'outputs': outputs})
    assert (owner.root/'recovery/head.json').read_bytes() == previous
    retry = RecoveryJournal(owner, context, resume=True)
    assert retry.get('second') is None
    with pytest.raises(ContractError, match='missing recovery checkpoint'):
        retry.adopt('second')


@pytest.mark.parametrize('lookup', ['existing-wave', 'missing-wave', 'terminal'])
def test_missing_head_rejects_warm_and_cold_consumers(committed, lookup):
    owner, journal, context, _, _, _, _ = committed
    (owner.root/'recovery/head.json').unlink()
    with pytest.raises((ContractError, OSError)):
        if lookup == 'terminal':
            journal.terminal(owner.root.parent/'report.json')
        else:
            journal.get('first' if lookup == 'existing-wave' else 'absent')
    with pytest.raises((ContractError, OSError)):
        RecoveryJournal(owner, context, resume=True)
    assert not (owner.root/'recovery/head.json').exists()


@pytest.mark.parametrize('cleanup', ['failed-contained', 'unresolved', 'missing'])
def test_later_failed_stage_is_history_not_selected_math(committed, cleanup):
    owner, journal, context, _, _, _, _ = committed
    attempt = owner.root/'attempts/attempt'
    _store(attempt/'later-stage.json', {'attempt_id': 'attempt'})
    path = attempt/'later/receipt.json'
    if cleanup != 'missing':
        _store(path, {'format': 't081-owned-stage-receipt-v1', 'stage': 'later',
                     'exit_code': 1, 'worker_cleanup_verified': cleanup == 'failed-contained'})
    if cleanup == 'failed-contained':
        assert len(recovery.check_history(owner.root)) == 2
        assert RecoveryJournal(owner, context, resume=True).receipts() == journal.receipts()
        assert len(recovery.selected_receipts(owner.root)) == 1
    else:
        with pytest.raises(ContractError, match='cleanup'):
            RecoveryJournal(owner, context, resume=True)


@pytest.fixture
def terminal_owner(tmp_path, problem, code_refs):
    output = tmp_path/'operation'
    output.mkdir()
    (output/'.volume.lock').touch()
    spec = collection(problem, code_refs)
    context = operation_context('exact', output, {'kind': 'SYNTHETIC_NONPROOF_CONTROL'})
    with CollectionLock.acquire(output/'collection', spec) as lock:
        yield output, lock, RecoveryJournal(lock, context)


@pytest.mark.parametrize('change', ['output', 'configuration', 'python', 'format'])
def test_closed_operation_context_rejects_changes(terminal_owner, change):
    output, lock, journal = terminal_owner
    changed = dict(journal.context)
    changed[change] = {'changed': True} if change == 'configuration' else str(output/'other')
    with pytest.raises(ContractError):
        RecoveryJournal(lock, changed, resume=True)


def test_terminal_intent_is_immutable_and_root_bound(terminal_owner):
    output, _, journal = terminal_owner
    path = output/'report.json'
    payload = {'scope': 'CONTROL_ONLY', 'not_a_Weil_acceptance': True}
    journal.publish(path, payload)
    raw = path.read_bytes()
    with pytest.raises(ContractError):
        journal.publish(path, {**payload, 'changed': True})
    assert path.read_bytes() == raw
    with pytest.raises(ContractError, match='destination'):
        journal.terminal(output/'collection/report.json')
    path.unlink()
    assert journal.terminal(path) == payload
    journal.publish(path, payload)
    assert path.read_bytes() == raw


def test_terminal_refuses_orphan_and_conflicting_fixed_bytes(terminal_owner):
    output, _, journal = terminal_owner
    path = output/'report.json'
    path.write_bytes(b'orphan')
    with pytest.raises(ContractError, match='no committed'):
        journal.publish(path, {'scope': 'CONTROL_ONLY'})
    assert path.read_bytes() == b'orphan'


def test_terminal_external_quota_is_checked_before_fixed_publication(terminal_owner):
    output, _, journal = terminal_owner
    with (output/'retained-control.bin').open('wb') as stream:
        stream.truncate(recovery.PUBLICATION_BYTES)
    with pytest.raises(ContractError, match='allowance'):
        journal.publish(output/'report.json', {'scope': 'CONTROL_ONLY'})
    assert not (output/'report.json').exists()
    # Intent survives quota refusal and remains the same intended document.
    assert journal.terminal(output/'report.json') == {'scope': 'CONTROL_ONLY'}


def test_journal_record_and_decoded_metadata_caps(terminal_owner, monkeypatch):
    _, _, journal = terminal_owner
    monkeypatch.setattr(recovery, 'MAX_RECORDS', 0)
    with pytest.raises(ContractError, match='record limit'):
        journal._append('stage-intent', 'control', {})
    monkeypatch.setattr(recovery, 'MAX_RECORDS', 4096)
    monkeypatch.setattr(recovery, 'METADATA_BYTES', 1)
    with pytest.raises(ContractError, match='allowance'):
        journal._append('stage-intent', 'control', {})
    assert journal.head['count'] == 0
