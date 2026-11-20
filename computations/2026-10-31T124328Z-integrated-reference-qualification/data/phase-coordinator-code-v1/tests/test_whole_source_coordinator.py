"""Deterministic phase-authority controls, not numerical qualification evidence."""
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from scripts.whole_source import coordinator
from scripts.whole_source.contract import ContractError, canonical_bytes
from scripts.whole_source.coordinator import PHASES, SCIENCE_PHASES, PhaseJournal, read_phase_records

ROLES = (
    ('problem', 'source_execution', 'premises'), ('source', 'source_publication'),
    ('audit', 'audit_execution'), ('proposal',), ('problem', 'execution', 'operands'),
    ('exact',), ('controls',), ('replay',),
)


def record(path, raw=b'SYNTHETIC_NONPROOF_CONTROL'):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw)
    return {'directory': str(path.parent.resolve()), 'artifact': {
        'path': path.name, 'sha256': hashlib.sha256(raw).hexdigest(), 'size': len(raw)}}


def outputs(directory, phase, *, suffix=''):
    return {role: record(directory/(role+suffix+'.json'),
                         canonical_bytes({'control': 'NONPROOF', 'phase': phase, 'role': role, 'suffix': suffix}))
            for role in ROLES[PHASES.index(phase)]}


def inputs(journal):
    return {phase: row['outputs'] for phase, row in journal.completed.items()}


@pytest.fixture
def operation(tmp_path):
    run = tmp_path/'run'
    run.mkdir()
    context = {'problem_id': '1'*64, 'configuration': {'control': 'NONPROOF'},
               'implementation': record(run/'implementation'/'start.json'), 'proposal_input': None}
    return run, context


def finish(journal, phase):
    directory, reused = journal.begin(phase, inputs(journal))
    assert reused is False and not directory.exists()
    result = outputs(directory, phase)
    return directory, journal.complete(phase, result)


def head_path(run):
    return run/'coordinator'/'head.json'


def rewrite(path, value):
    path.write_bytes(canonical_bytes(value))


def publish_node(run, head, kind, payload):
    """Adversarial bytes use the real schema/hash, without asserting authority."""
    node = {'format': coordinator.FORMAT, 'context_sha256': head['context_sha256'],
            'previous': head['tip'], 'kind': kind, 'payload': payload}
    raw = canonical_bytes(node)
    digest = hashlib.sha256(raw).hexdigest()
    path = 'coordinator/nodes/'+digest+'.json'
    with (run/path).open('xb') as stream:
        stream.write(raw)
    return {'directory': str(run), 'artifact': {'path': path, 'sha256': digest, 'size': len(raw)}}


def test_committed_continuation_preserves_original_authority(operation):
    run, context = operation
    journal = PhaseJournal(run, context)
    selected = {}
    for phase in PHASES:
        directory, row = finish(journal, phase)
        selected[phase] = row
        before = {path: path.read_bytes() for path in run.rglob('*') if path.is_file()}
        journal = PhaseJournal(run, context, resume=True)
        assert journal.context == context
        assert journal.pending is None
        assert journal.completed == selected == read_phase_records(run)
        assert all(path.read_bytes() == raw for path, raw in before.items())
        assert Path(row['directory']) == directory
        assert row['inputs'] == {name: selected[name]['outputs'] for name in selected if name != phase}
    assert SCIENCE_PHASES == PHASES[:6]
    assert journal.completed['prepare']['outputs']['problem'] != journal.completed['exact-inputs']['outputs']['problem']
    with pytest.raises(ContractError):
        journal.begin('replay', inputs(journal))


def test_pending_exposes_prelaunch_intent_and_explicit_reuse(operation):
    run, context = operation
    journal = PhaseJournal(run, context)
    directory, reused = journal.begin('prepare', {})
    assert reused is False and not directory.exists()
    assert journal.pending['phase'] == 'prepare'
    assert journal.pending['directory'] == str(directory)
    assert journal.pending['inputs'] == {}
    pending = journal.pending
    retry = PhaseJournal(run, context, resume=True)
    assert retry.pending == pending and read_phase_records(run) == {}
    assert retry.begin('prepare', {}, reuse=True) == (directory, True)
    # Genuine role validation is the caller's responsibility before this commit.
    result = outputs(directory, 'prepare')
    row = retry.complete('prepare', result)
    assert row['intent'] == pending['record']


def test_fresh_retry_retains_abandoned_intent_and_attempt(operation):
    run, context = operation
    journal = PhaseJournal(run, context)
    first, _ = journal.begin('prepare', {})
    abandoned = record(first/'failure.json')
    old_intent = journal.pending['record']
    old_bytes = (run/old_intent['artifact']['path']).read_bytes()
    retry = PhaseJournal(run, context, resume=True)
    second, reused = retry.begin('prepare', {})
    assert second != first and reused is False and not second.exists()
    retry.complete('prepare', outputs(second, 'prepare'))
    assert first.is_dir() and (first/'failure.json').read_bytes() == b'SYNTHETIC_NONPROOF_CONTROL'
    assert abandoned['directory'] == str(first)
    assert (run/old_intent['artifact']['path']).read_bytes() == old_bytes
    assert read_phase_records(run)['prepare']['directory'] == str(second)


@pytest.mark.parametrize('change', ['configuration', 'problem', 'implementation', 'proposal'])
def test_changed_resume_context_refuses_without_publication(operation, change):
    run, context = operation
    journal = PhaseJournal(run, context)
    finish(journal, 'prepare')
    before = head_path(run).read_bytes()
    altered = dict(context)
    if change == 'configuration':
        altered['configuration'] = {'control': 'DIFFERENT_NONPROOF'}
    elif change == 'problem':
        altered['problem_id'] = '2'*64
    elif change == 'implementation':
        altered['implementation'] = record(run/'other-start.json')
    else:
        altered['proposal_input'] = record(run/'installed-proposal.json')
    with pytest.raises(ContractError):
        PhaseJournal(run, altered, resume=True)
    assert head_path(run).read_bytes() == before


@pytest.mark.parametrize('change', ['output', 'start', 'node', 'python', 'path', 'head'])
def test_committed_corruption_is_not_existence_recovery(operation, tmp_path, change):
    run, context = operation
    journal = PhaseJournal(run, context)
    directory, row = finish(journal, 'prepare')
    if change == 'output':
        (directory/'problem.json').write_bytes(b'ALTERED_NONPROOF')
    elif change == 'start':
        (run/'implementation'/'start.json').write_bytes(b'ALTERED_NONPROOF')
    elif change == 'node':
        (run/row['record']['artifact']['path']).write_bytes(b'{}')
    elif change in ('python', 'path'):
        path = run/'coordinator'/'context.json'
        document = json.loads(path.read_bytes())
        document['python' if change == 'python' else 'run'] = 'different binding'
        rewrite(path, document)
    else:
        head_path(run).unlink()
    with pytest.raises(ContractError):
        read_phase_records(run)
    with pytest.raises(ContractError):
        PhaseJournal(run, context, resume=True)


def test_copying_operation_does_not_rebind_its_absolute_path(operation, tmp_path):
    run, context = operation
    journal = PhaseJournal(run, context)
    finish(journal, 'prepare')
    copied = tmp_path/'copied'
    shutil.copytree(run, copied)
    with pytest.raises(ContractError, match='path'):
        read_phase_records(copied)
    with pytest.raises(ContractError):
        PhaseJournal(copied, context, resume=True)


def test_orphan_completion_before_atomic_head_is_not_selected(operation, monkeypatch):
    run, context = operation
    journal = PhaseJournal(run, context)
    directory, _ = journal.begin('prepare', {})
    result = outputs(directory, 'prepare')
    before = head_path(run).read_bytes()
    pending = journal.pending
    original = journal._replace_head
    def interrupted(head):
        raise OSError('deterministic interruption before head publication')
    monkeypatch.setattr(journal, '_replace_head', interrupted)
    with pytest.raises(OSError):
        journal.complete('prepare', result)
    assert head_path(run).read_bytes() == before
    assert read_phase_records(run) == {}
    retry = PhaseJournal(run, context, resume=True)
    assert retry.pending == pending
    monkeypatch.setattr(journal, '_replace_head', original)
    # No automatic adoption. The caller validates and republishes the same result.
    row = retry.complete('prepare', result)
    assert read_phase_records(run) == {'prepare': row}
    assert len(list((run/'coordinator'/'nodes').iterdir())) == 2


def test_conflicting_orphan_completion_refuses_ambiguous_recovery(operation, monkeypatch):
    run, context = operation
    journal = PhaseJournal(run, context)
    directory, _ = journal.begin('prepare', {})
    first = outputs(directory, 'prepare')
    def interrupted(head):
        raise OSError('deterministic head interruption')
    monkeypatch.setattr(journal, '_replace_head', interrupted)
    with pytest.raises(OSError):
        journal.complete('prepare', first)
    retry = PhaseJournal(run, context, resume=True)
    changed = outputs(directory, 'prepare', suffix='-conflict')
    before = head_path(run).read_bytes()
    with pytest.raises(ContractError, match='ambiguous'):
        retry.complete('prepare', changed)
    assert read_phase_records(run) == {} and head_path(run).read_bytes() == before
    retry.complete('prepare', first)


def test_orphan_intent_cannot_advance_committed_phase(operation, monkeypatch):
    run, context = operation
    journal = PhaseJournal(run, context)
    def interrupted(head):
        raise OSError('deterministic intent interruption')
    monkeypatch.setattr(journal, '_replace_head', interrupted)
    with pytest.raises(OSError):
        journal.begin('prepare', {})
    retry = PhaseJournal(run, context, resume=True)
    assert retry.pending is None and retry.completed == {}
    with pytest.raises(ContractError, match='pending'):
        retry.begin('prepare', {}, reuse=True)
    directory, _ = retry.begin('prepare', {})
    retry.complete('prepare', outputs(directory, 'prepare'))
    assert read_phase_records(run)['prepare']['directory'] == str(directory)


def test_sequential_graph_and_exact_predecessors_are_required(operation):
    run, context = operation
    journal = PhaseJournal(run, context)
    for phase in PHASES[1:]:
        with pytest.raises(ContractError, match='phase order'):
            journal.begin(phase, {})
    with pytest.raises(ContractError, match='pending'):
        journal.complete('prepare', {})
    finish(journal, 'prepare')
    with pytest.raises(ContractError, match='completed'):
        journal.begin('prepare', {})
    for altered in ({}, {'prepare': {}}, {'other': journal.completed['prepare']['outputs']}):
        with pytest.raises(ContractError, match='predecessor'):
            journal.begin('source', altered)
    assert journal.pending is None
    assert not (run/'source').exists()


def test_committed_duplicate_completion_and_foreign_attempt_refuse(operation):
    run, context = operation
    journal = PhaseJournal(run, context)
    _, row = finish(journal, 'prepare')
    head = json.loads(head_path(run).read_bytes())
    payload = {key: value for key, value in row.items() if key != 'record'}
    ref = publish_node(run, head, 'completion', payload)
    rewrite(head_path(run), {**head, 'count': head['count']+1, 'tip': ref})
    with pytest.raises(ContractError, match='phase order'):
        read_phase_records(run)


def test_head_rejects_wrong_count_and_missing_or_foreign_tip(operation):
    run, context = operation
    journal = PhaseJournal(run, context)
    finish(journal, 'prepare')
    path = head_path(run)
    good = json.loads(path.read_bytes())
    for bad in ({**good, 'count': good['count']+1},
                {**good, 'tip': {**good['tip'], 'directory': str(run.parent)}},
                {**good, 'tip': {'directory': str(run), 'artifact': {
                    'path': 'coordinator/nodes/'+'f'*64+'.json', 'sha256': 'f'*64, 'size': 1}}}):
        rewrite(path, bad)
        with pytest.raises(ContractError):
            read_phase_records(run)
    rewrite(path, good)
    assert read_phase_records(run) == journal.completed


def test_active_stale_writer_and_fresh_open_refuse(operation):
    run, context = operation
    journal = PhaseJournal(run, context)
    stale = PhaseJournal(run, context, resume=True)
    journal.begin('prepare', {})
    with pytest.raises(ContractError, match='head'):
        stale.begin('prepare', {})
    with pytest.raises(ContractError, match='resume'):
        PhaseJournal(run, context)


def test_per_file_and_decoded_journal_limits_refuse_before_commit(operation, monkeypatch):
    run, context = operation
    journal = PhaseJournal(run, context)
    directory, _ = journal.begin('prepare', {})
    result = outputs(directory, 'prepare')
    before = head_path(run).read_bytes()
    monkeypatch.setattr(coordinator, 'METADATA_BYTES', journal.resident+1)
    with pytest.raises(ContractError, match='allowance'):
        journal.complete('prepare', result)
    assert head_path(run).read_bytes() == before
    monkeypatch.setattr(coordinator, 'METADATA_BYTES', 16*1024*1024)
    monkeypatch.setattr(coordinator, 'FILE_BYTES', 64)
    with pytest.raises(ContractError, match='allowance'):
        journal.complete('prepare', result)
    assert head_path(run).read_bytes() == before


def test_uncommitted_nodes_count_toward_journal_cap(operation, monkeypatch):
    run, context = operation
    journal = PhaseJournal(run, context)
    journal.begin('prepare', {})
    before = head_path(run).read_bytes()
    monkeypatch.setattr(coordinator, 'MAX_NODES', 1)
    with pytest.raises(ContractError, match='allowance'):
        journal.begin('prepare', {})
    assert head_path(run).read_bytes() == before


def test_output_path_escape_refuses_without_head_change(operation):
    run, context = operation
    journal = PhaseJournal(run, context)
    directory, _ = journal.begin('prepare', {})
    result = outputs(directory, 'prepare')
    result['problem']['artifact']['path'] = '../problem.json'
    before = head_path(run).read_bytes()
    with pytest.raises(ContractError):
        journal.complete('prepare', result)
    assert head_path(run).read_bytes() == before


def test_interrupted_initial_head_keeps_temporary_and_recovers_only_empty_state(operation, monkeypatch):
    run, context = operation
    replace = coordinator.replace_path_with_permission_retry
    def interrupted(source, destination):
        raise OSError('deterministic initial head interruption')
    monkeypatch.setattr(coordinator, 'replace_path_with_permission_retry', interrupted)
    with pytest.raises(OSError):
        PhaseJournal(run, context)
    temporaries = list((run/'coordinator').glob('.head-*.json'))
    assert len(temporaries) == 1
    before = temporaries[0].read_bytes()
    assert not (run/'coordinator'/'context.json').exists()
    monkeypatch.setattr(coordinator, 'replace_path_with_permission_retry', replace)
    retry = PhaseJournal(run, context, resume=True)
    assert retry.completed == {} and retry.pending is None
    assert temporaries[0].read_bytes() == before


def test_foreign_attempt_directory_cannot_be_committed_even_with_correct_hash(operation):
    run, context = operation
    journal = PhaseJournal(run, context)
    journal.begin('prepare', {})
    head = json.loads(head_path(run).read_bytes())
    payload = {key: value for key, value in journal.pending.items() if key != 'record'}
    payload['directory'] = str(run.parent/'foreign'/'attempts'/('a'*32))
    ref = publish_node(run, head, 'intent', payload)
    rewrite(head_path(run), {**head, 'count': head['count']+1, 'tip': ref})
    with pytest.raises(ContractError, match='foreign phase attempt'):
        read_phase_records(run)


def test_output_artifact_directory_is_exactly_bound(operation):
    run, context = operation
    journal = PhaseJournal(run, context)
    directory, _ = journal.begin('prepare', {})
    result = outputs(directory, 'prepare')
    row = journal.complete('prepare', result)
    # Equal bytes elsewhere do not permit changing a predecessor's locator.
    alternate = outputs(run/'alternate', 'prepare')
    changed = {'prepare': {**row['outputs'], 'problem': alternate['problem']}}
    before = head_path(run).read_bytes()
    with pytest.raises(ContractError, match='predecessor'):
        journal.begin('source', changed)
    assert head_path(run).read_bytes() == before


def test_external_replay_proposal_binding_requires_original_bytes(operation):
    run, context = operation
    installed = record(run.parent/'installed'/'proposal.json')
    replay_context = {**context, 'proposal_input': installed}
    journal = PhaseJournal(run, replay_context)
    assert journal.context['proposal_input'] == installed
    finish(journal, 'prepare')
    (Path(installed['directory'])/'proposal.json').write_bytes(b'CHANGED_NONPROOF')
    with pytest.raises(ContractError, match='artifact'):
        read_phase_records(run)


def test_metadata_codec_rejects_noncanonical_and_oversized_files(operation):
    run, context = operation
    journal = PhaseJournal(run, context)
    good = head_path(run).read_bytes()
    head_path(run).write_bytes(good+b'\\n')
    with pytest.raises(ContractError):
        read_phase_records(run)
    head_path(run).write_bytes(b' '*(coordinator.HEAD_BYTES+1))
    with pytest.raises(ContractError, match='allowance'):
        read_phase_records(run)
    head_path(run).write_bytes(good)
    assert read_phase_records(run) == journal.completed
