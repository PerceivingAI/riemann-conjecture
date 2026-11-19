"""Recovery consumer controls. Synthetic receipts here make no Weil claim."""
from dataclasses import asdict
import hashlib
import json
import shutil
from types import SimpleNamespace

import pytest

from scripts.whole_source import recovery
from scripts.whole_source.artifacts import CollectionLock
from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes
from scripts.whole_source.recovery import RecoveryJournal, operation_context
from scripts.whole_source.task_groups import (
    LEGACY_GROUP, group_receipt, local_group, operation_group, read_group, seal_group, same_group,
)
from tests.test_whole_source_artifacts import collection, code_refs, problem
from tests.test_whole_source_task_groups import group_case
from tests.test_whole_source_receipts import _ref, _store


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
        self.first_writes = []

    def _check(self, *, attempt_id=None):
        if attempt_id is not None and attempt_id not in self._attempts:
            raise ContractError('unregistered control owner')

    def _exclusive(self, name, raw):
        path = self.root/name
        path.parent.mkdir(exist_ok=True)
        with path.open('xb') as stream:
            stream.write(raw)
        self.first_writes.append((name, raw))

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


def test_first_writes_use_only_logical_roles_and_refs(tmp_path, monkeypatch):
    output = tmp_path/'SYNTHETIC_PRIVATE_PLACEMENT'
    owner = ControlOwner(output/'collection')
    context = operation_context('exact', output, {'panel_size': 2})
    journal = RecoveryJournal(owner, context)
    _, execution, gc, outputs, _ = group_case.__wrapped__(output)
    group = seal_group(owner, execution, 'fixture', gc, outputs)
    journal.commit('first', local_group(owner.root, group), {'outputs': outputs})
    journal.adopt('first', attempt_id=owner.attempt('retry'))
    intent_execution = SimpleNamespace(attempt_id='retry', collection_lock=owner,
        output=owner.root/'attempts/retry', plan=SimpleNamespace(execution_id='3'*64))
    journal.intend_assessment(intent_execution, {'operation': 'assess'}, {'scope': 'CONTROL_ONLY'})
    publication_writes = []
    original_write = recovery._write
    def record_write(path, raw):
        publication_writes.append((path.name, raw))
        return original_write(path, raw)
    monkeypatch.setattr(recovery, '_write', record_write)
    journal.publish(output/'report.json', {'scope': 'CONTROL_ONLY'}, dependencies=[group])

    writes = owner.first_writes + publication_writes
    assert all(b'SYNTHETIC_PRIVATE_PLACEMENT' not in raw for _, raw in writes)
    assert any(name.startswith('recovery/.publish-') for name, _ in writes)
    assert any(name.startswith('.publication-') for name, _ in writes)
    written = [json.loads(raw) for _, raw in writes]
    terminal = next(row['payload'] for row in written if row.get('kind') == 'terminal')
    wave = next(row['payload'] for row in written if row.get('kind') == 'wave')
    intent = next(row['payload'] for row in written if row.get('kind') == 'stage-intent')
    adoption = next(row for row in written if row.get('format') == recovery.ADOPTION)
    assert wave['group'] == adoption['origin'] == {'artifact': group['artifact']}
    assert terminal['filename'] == 'report.json'
    assert terminal['dependencies'] == [operation_group(output, group)]
    assert intent['receipt'] == 'attempts/retry/assess/receipt.json'


def test_unencoded_paths_never_reach_first_write(tmp_path):
    owner = ControlOwner(tmp_path/'collection')
    private = str(tmp_path/'SYNTHETIC_PRIVATE_FIELD')
    with pytest.raises(ContractError, match='physical path'):
        RecoveryJournal(owner, operation_context('exact', tmp_path, {'nested': [{'cwd': private}]}))
    assert not owner.first_writes and not (owner.root/'recovery').exists()

    journal = RecoveryJournal(owner, operation_context('exact', tmp_path, {'panel_size': 2}))
    before = list(owner.first_writes)
    with pytest.raises(ContractError, match='physical path'):
        journal.publish(tmp_path/'report.json', {'unsafe': private})
    assert owner.first_writes == before
    assert journal.terminal(tmp_path/'report.json') is None


def test_relocated_operation_resumes_exact_intent_and_original_producer(tmp_path):
    output = tmp_path/'SYNTHETIC_LAYOUT_A'
    owner = ControlOwner(output/'collection')
    configuration = {'panel_size': 2}
    journal = RecoveryJournal(owner, operation_context('exact', output, configuration))
    _, execution, gc, outputs, receipt = group_case.__wrapped__(output)
    group = seal_group(owner, execution, 'fixture', gc, outputs)
    journal.commit('first', group, {'outputs': outputs})
    adopted = journal.adopt('first')
    payload = {'scope': 'CONTROL_ONLY'}
    journal.publish(output/'report.json', payload, dependencies=[group])
    before = {path.relative_to(output): path.read_bytes() for path in output.rglob('*') if path.is_file()}
    relocated = tmp_path/'SYNTHETIC_LAYOUT_B'
    output.rename(relocated)
    owner.root = relocated/'collection'
    owner.generation += 1
    retry = RecoveryJournal(owner, operation_context('exact', relocated, configuration), resume=True)
    selected = retry.get('first')['group']
    assert selected['artifact'] == group['artifact']
    portable_adoption = {'artifact': adopted['artifact']}
    assert read_group(portable_adoption, gc, expected_root=owner.root) == (owner.root, outputs)
    assert same_group(portable_adoption, selected, expected_root=owner.root)
    assert retry.receipts() == recovery.selected_receipts(owner.root)
    assert group_receipt(selected)['directory'] == str((relocated/receipt.relative_to(output)).parent)
    retry.publish(relocated/'report.json', payload, dependencies=[selected])
    assert retry.terminal(relocated/'report.json') == payload
    assert all((relocated/relative).read_bytes() == raw for relative, raw in before.items())


def test_committed_terminal_revalidates_dependency_bytes(committed):
    owner, journal, _, _, group, outputs, _ = committed
    path = owner.root.parent/'report.json'
    payload = {'scope': 'CONTROL_ONLY'}
    journal.publish(path, payload, dependencies=[group])
    with pytest.raises(ContractError, match='intended terminal dependencies'):
        journal.publish(path, payload)
    dependency = owner.root/outputs['report']['path']
    raw = dependency.read_bytes()
    dependency.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
    with pytest.raises(ContractError, match='fingerprint'):
        journal.terminal(path)
    assert path.read_bytes() == canonical_bytes(payload)


def test_terminal_rejects_foreign_operation_dependency_context(tmp_path):
    output = tmp_path/'proposal'
    terminal = ControlOwner(output/'recovery-terminal')
    native = ControlOwner(output/'native-0')
    context = operation_context('proposal', output, {'panel_size': 2})
    journal = RecoveryJournal(terminal, context)
    native_journal = RecoveryJournal(native, context)
    fixture, execution, gc, outputs, _ = group_case.__wrapped__(tmp_path/'scaffold')
    shutil.move(execution.output, native.root/'attempts'/execution.attempt_id)
    shutil.move(fixture.root/'seals', native.root/'seals')
    execution.output = native.root/'attempts'/execution.attempt_id
    group = seal_group(native, execution, 'fixture', gc, outputs)
    native_journal.commit('factor-diagonal_0', group, {'outputs': outputs})
    path = output/'proposal-producers.json'
    payload = {'scope': 'CONTROL_ONLY'}
    journal.publish(path, payload, dependencies=[group])

    # Keep exact successful science and the committed terminal unchanged while
    # replacing the producer's operation binding with another configuration.
    foreign = operation_context('proposal', output, {'panel_size': 3})
    foreign_doc = recovery._journal_document(native.root, foreign, native.spec.collection_id)
    _store(native.root/'recovery/context.json', foreign_doc)
    with pytest.raises(ContractError, match='foreign operation'):
        journal.terminal(path)
    assert path.read_bytes() == canonical_bytes(payload)


def test_v1_reader_checks_original_receipt_group_adoption_and_terminal_bytes(tmp_path):
    output = tmp_path/'legacy'
    owner = ControlOwner(output/'collection')
    lock, execution, gc, outputs, receipt = group_case.__wrapped__(output, portable=False)
    context = operation_context('exact', output, {'panel_size': 2})
    policy = recovery.LEGACY_RECOVERY_POLICY
    legacy = recovery._journal_document(lock.root, context, lock.spec.collection_id, format=policy)
    context_fingerprint = hashlib.sha256(canonical_bytes(legacy)).hexdigest()
    original_receipt = {'directory': str(receipt.parent), 'artifact': asdict(_ref(receipt))}
    group_document = {'format': LEGACY_GROUP, 'context': gc, 'stage': original_receipt,
                      'attempt_id': execution.attempt_id, 'collection_id': lock.spec.collection_id,
                      'outputs': outputs}
    group = {'root': str(lock.root), 'artifact': asdict(lock._immutable('seals', canonical_bytes(group_document)))}
    def node(kind, key, payload, previous=None):
        return asdict(owner._immutable('recovery', canonical_bytes({
            'format': policy, 'context_sha256': context_fingerprint, 'previous': previous,
            'kind': kind, 'key': key, 'payload': payload})))
    checkpoint = node('wave', 'first', {'group': group, 'value': {'outputs': outputs}})
    retry = asdict(owner._immutable('recovery', canonical_bytes({
        'format': policy, 'retry_id': 'retry', 'attempt_id': 'retry', 'generation': 1,
        'collection_id': lock.spec.collection_id, 'context_sha256': context_fingerprint, 'artifact_owner': None})))
    adoption = {'root': str(lock.root), 'artifact': asdict(owner._immutable('recovery', canonical_bytes({
        'format': recovery.LEGACY_ADOPTION, 'context': gc, 'origin': group, 'checkpoint': checkpoint,
        'owner': retry, 'attempt_id': 'retry', 'collection_id': lock.spec.collection_id,
        'generation': 1, 'journal_context': context_fingerprint})))}
    adopted = node('adoption', 'first', {'artifact': adoption['artifact']}, previous=checkpoint)
    path = _store(output/'report.json', {'scope': 'CONTROL_ONLY'})
    terminal_ref = asdict(owner._immutable('recovery', path.read_bytes()))
    terminal = {'path': str(path), 'artifact': terminal_ref, 'dependencies': [group]}
    tip = node('terminal', 'report.json', terminal, previous=adopted)
    _store(lock.root/'recovery/context.json', legacy)
    _store(lock.root/'recovery/head.json', {
        'format': policy, 'context_sha256': context_fingerprint, 'count': 3, 'tip': tip})
    before = {p: p.read_bytes() for p in output.rglob('*') if p.is_file()}

    assert read_group(adoption, gc) == (lock.root, outputs)
    assert same_group(adoption, group)
    assert group_receipt(group) == original_receipt
    assert recovery.selected_receipts(lock.root) == [original_receipt]
    document = recovery._context_document(lock.root)
    records, _ = recovery._state(lock.root, document)
    assert document == legacy and records[0][1]['payload'] == terminal
    assert asdict(recovery._terminal_payload(lock.root, output, path.name, terminal, policy)) == terminal_ref
    with pytest.raises(ContractError, match='resume context'):
        RecoveryJournal(owner, context, resume=True)
    wrong_size = {**group, 'artifact': {**group['artifact'], 'size': group['artifact']['size'] + 1}}
    with pytest.raises(ContractError, match='regular artifact'):
        read_group(wrong_size, gc)
    assert {p: p.read_bytes() for p in output.rglob('*') if p.is_file()} == before
