"""Synthetic operational authority only; these fixtures do not run science."""
from contextlib import nullcontext
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.whole_source import admission, execution, retention, supervision
from scripts.whole_source.contract import ContractError, canonical_bytes
from scripts.whole_source.coordinator import PhaseJournal, read_phase_records


def store(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(document))
    return retention._record(path)['artifact']


def observer(root, identity, code, status='COMPLETED'):
    intent = {'format': 'whole-source-lifecycle-intent-v1', 'invocation_id': identity,
              'operation_id': 'a'*64, 'policy': {}, 'code': code}
    intent_ref = store(root/'intents'/(identity+'.json'), intent)
    intent_ref['path'] = 'intents/'+identity+'.json'
    observation = store(root/'observations'/(identity+'.jsonl'), {
        'event': 'terminal', 'invocation_id': identity, 'monotonic_ns': 1,
        'phase': 'prepare', 'progress': {'state': 'complete'}, 'status': status})
    observation['path'] = 'observations/'+identity+'.jsonl'
    receipt = {'format': 'whole-source-lifecycle-receipt-v1', 'invocation_id': identity,
               'operation_id': 'a'*64, 'policy': {}, 'intent': intent_ref, 'code': code,
               'status': status, 'reason': None if status == 'COMPLETED' else 'synthetic stop',
               'elapsed_ns': 1, 'cumulative_active_ns': 1,
               'child_returncode': 0 if status == 'COMPLETED' else 1,
               'cleanup_verified': True, 'final_job': {'active_process_count': 0, 'active_process_ids': []},
               'observation': observation, 'upstream': {}}
    store(root/'receipts'/(identity+'.json'), receipt)
    return {'root': str(root), 'invocation_id': identity, 'operation_id': 'a'*64,
            'intent': intent_ref}, receipt


@pytest.fixture
def selected(tmp_path, monkeypatch):
    code_root = tmp_path/'code'
    code_path = code_root/'scripts/whole_source/supervision.py'
    code_path.parent.mkdir(parents=True)
    code_path.write_bytes(b'SYNTHETIC_NONPROOF_IMPLEMENTATION\n')
    code = {'scripts/whole_source/supervision.py': hashlib.sha256(code_path.read_bytes()).hexdigest()}
    binding, receipt = observer(tmp_path/'observer', '1'*32, code)
    current = {'invocation_id': '9'*32, 'operation_id': 'a'*64, 'code': code,
               'root': binding['root']}
    monkeypatch.setattr(supervision, 'require_current', lambda: current)
    run = tmp_path/'run'
    run.mkdir()
    store(run/'implementation/start.json', {'scope': 'SYNTHETIC_NONPROOF'})
    journal = PhaseJournal(run, {'problem_id': 'b'*64, 'configuration': {},
        'implementation': retention._record(run/'implementation/start.json'), 'proposal_input': None})
    directory, _ = journal.begin('prepare', {})
    report = {'format': admission.FORMAT, 'policy': admission.POLICY, 'phase': 'prepare',
              'problem_id': 'b'*64, 'inputs': {}, 'supervision': binding}
    admission.bind_phase_attempt(report, directory, run)
    for name in ('source-inputs/problem.json', 'source-inputs/execution.json', 'premises/premises-receipt.json'):
        store(directory/name, {'scope': 'SYNTHETIC_NONPROOF'})
    journal.complete('prepare', retention._phase_outputs('prepare', directory))
    return SimpleNamespace(run=run, root=code_root, binding=binding, receipt=receipt,
        current=current, report=report, directory=directory,
        admission=run/'admission'/('attempt-prepare-'+directory.name+'.json'))


def authority(selected):
    return retention._selected_supervision(selected.run, selected.root)


def test_original_selected_attempt_binds_observer_separately(selected):
    row = authority(selected)[0]
    assert row['attempt_directory'] == str(selected.directory)
    assert row['phase_completion'] == read_phase_records(selected.run)['prepare']['record']
    assert row['supervision'] == selected.binding
    assert row['invocation_status'] == 'COMPLETED'
    assert Path(row['receipt']['directory'])/row['receipt']['artifact']['path'] == (
        Path(selected.binding['root'])/'receipts'/('1'*32+'.json'))
    assert row['observation']['artifact'] == selected.receipt['observation']
    assert 'owned_receipts' not in row


def test_current_invocation_cannot_supply_terminal_phase_authority(selected):
    selected.current['invocation_id'] = selected.binding['invocation_id']
    with pytest.raises(ContractError, match='prior terminal'):
        authority(selected)


@pytest.mark.parametrize('artifact', ['admission', 'intent', 'receipt', 'observation'])
def test_missing_original_supervisor_authority_refuses(selected, artifact):
    if artifact == 'admission':
        path = selected.admission
    else:
        key = {'intent': 'intent', 'observation': 'observation'}.get(artifact)
        relative = selected.binding['intent']['path'] if key == 'intent' else (
            selected.receipt['observation']['path'] if key else 'receipts/'+'1'*32+'.json')
        path = Path(selected.binding['root'])/relative
    path.unlink()
    with pytest.raises(ContractError):
        authority(selected)


@pytest.mark.parametrize('field,value', [
    ('cleanup_verified', False), ('final_job', {'active_process_count': 1}),
    ('final_job', None), ('status', 'REFUSED'), ('operation_id', 'c'*64),
    ('code', {'scripts/whole_source/supervision.py': 'c'*64}),
    ('intent', {'path': 'intents/'+'1'*32+'.json', 'sha256': 'c'*64, 'size': 1}),
])
def test_changed_terminal_authority_refuses(selected, field, value):
    selected.receipt[field] = value
    store(Path(selected.binding['root'])/'receipts'/('1'*32+'.json'), selected.receipt)
    with pytest.raises(ContractError):
        authority(selected)


def test_changed_observation_digest_refuses(selected):
    path = Path(selected.binding['root'])/selected.receipt['observation']['path']
    path.write_bytes(path.read_bytes()+b'{}\n')
    with pytest.raises(ContractError):
        authority(selected)


def test_changed_original_intent_refuses(selected):
    path = Path(selected.binding['root'])/selected.binding['intent']['path']
    value = json.loads(path.read_bytes())
    value['policy'] = {'changed': True}
    store(path, value)
    with pytest.raises(ContractError):
        authority(selected)


def test_interrupted_cleaned_invocation_keeps_failed_status_for_completed_phase(selected):
    binding, receipt = observer(Path(selected.binding['root']), '1'*32,
                                selected.current['code'], status='INTERRUPTED')
    assert binding == selected.binding
    selected.receipt = receipt
    row = authority(selected)[0]
    assert row['invocation_status'] == 'INTERRUPTED'
    assert retention._document(row['receipt'])['child_returncode'] == 1
    assert 'reference_qualification_accepted' not in row


def test_unselected_failed_attempt_is_retained_and_cannot_replace_selected_binding(selected):
    failed = selected.run/'prepare/attempts'/('2'*32)
    store(failed/'failed.json', {'scope': 'FAILED_SYNTHETIC_NONPROOF'})
    report = {**selected.report, 'supervision': {**selected.binding, 'invocation_id': '3'*32}}
    admission.bind_phase_attempt(report, failed, selected.run)
    before = (failed/'failed.json').read_bytes()
    assert authority(selected)[0]['attempt_directory'] == str(selected.directory)
    assert (failed/'failed.json').read_bytes() == before
    selected.admission.unlink()
    with pytest.raises(ContractError):
        authority(selected)


@pytest.mark.parametrize('field', ['attempt_directory', 'inputs'])
def test_changed_admission_attempt_or_predecessors_refuses(selected, field):
    document = json.loads(selected.admission.read_bytes())
    document[field] = (str(selected.run/'prepare/attempts'/('2'*32)) if field == 'attempt_directory'
                       else {'source': {'scope': 'SYNTHETIC_REBOUND_PREDECESSOR'}})
    store(selected.admission, document)
    with pytest.raises(ContractError, match='original attempt'):
        authority(selected)


def test_missing_binding_in_original_admission_refuses(selected):
    document = json.loads(selected.admission.read_bytes())
    del document['supervision']
    store(selected.admission, document)
    with pytest.raises(ContractError, match='missing selected phase supervisor'):
        authority(selected)


def test_resumed_work_requires_both_original_and_continuation_cleanup(selected):
    original = selected.admission.read_bytes()
    binding, receipt = observer(Path(selected.binding['root']), '2'*32, selected.current['code'])
    admission.bind_phase_attempt({**selected.report, 'supervision': binding}, selected.directory, selected.run)
    assert selected.admission.read_bytes() == original
    assert {row['supervision']['invocation_id'] for row in authority(selected)} == {'1'*32, '2'*32}
    receipt['cleanup_verified'] = False
    store(Path(binding['root'])/'receipts'/('2'*32+'.json'), receipt)
    with pytest.raises(ContractError, match='cleanup'):
        authority(selected)


@pytest.mark.parametrize('scope', ['bootstrap', 'phase'])
def test_supervision_precedes_bootstrap_and_phase_census(monkeypatch, tmp_path, scope):
    def refuse():
        raise ValueError('synthetic missing guardian')
    monkeypatch.setattr(supervision, 'require_current', refuse)
    context = admission.bootstrap_scope(tmp_path) if scope == 'bootstrap' else (
        admission.admitted_phase('source', object(), tmp_path, tmp_path))
    with pytest.raises(ValueError, match='missing guardian'):
        with context:
            pytest.fail('unsupervised work entered')
    assert not list(tmp_path.iterdir())


def test_phase_admission_retains_binding_and_bounded_progress(monkeypatch, tmp_path):
    binding = {'root': str(tmp_path/'observer'), 'invocation_id': '1'*32,
               'operation_id': 'a'*64, 'intent': {'path': 'intents/'+'1'*32+'.json',
                                               'sha256': 'b'*64, 'size': 1}}
    events, writes = [], []
    monkeypatch.setattr(supervision, 'require_current', lambda: {})
    monkeypatch.setattr(supervision, 'current_binding', lambda: binding)
    monkeypatch.setattr(supervision, 'event', lambda phase, state='working', work=None:
                        events.append((phase, state, work)))
    monkeypatch.setattr(admission, 'current_commit', lambda root: 0)
    monkeypatch.setattr(admission, 'caller_scope', lambda *args, **kwargs: nullcontext({}))
    monkeypatch.setattr(admission, 'phase_caller_account', lambda *args, **kwargs: {})
    monkeypatch.setattr(admission, 'topology', lambda problem: {})
    monkeypatch.setattr(admission, 'problem_id', lambda problem: 'a'*64)
    from scripts.whole_source import storage
    monkeypatch.setattr(storage, 'current_budget', lambda path: SimpleNamespace(admit=lambda: {}))
    monkeypatch.setattr(execution, '_write', lambda path, raw: writes.append(json.loads(raw)))
    with admission.admitted_phase('source', object(), tmp_path, tmp_path) as report:
        assert report['supervision'] == binding
    assert writes[0]['supervision'] == binding
    assert events == [('source', 'working', 'admission-census'),
                      ('source', 'working', 'phase-work'), ('source', 'complete', None)]


@pytest.mark.parametrize('entry', ['prepare_review', 'accept', 'finalize_retention',
                                  'recover_assessment_publication', 'run'])
def test_external_entry_requires_guardian_before_any_path_work(monkeypatch, tmp_path, entry):
    def refuse():
        raise ValueError('synthetic missing guardian')
    monkeypatch.setattr(supervision, 'require_current', refuse)
    function = getattr(retention, entry)
    args = [tmp_path/'missing-run', tmp_path/'missing-output']
    if entry == 'run':
        args.append(tmp_path/'missing-science')
    with pytest.raises(ValueError, match='missing guardian'):
        function(*args, code_root=tmp_path)
    assert not list(tmp_path.iterdir())


def test_already_sealed_verification_requires_guardian_and_never_changes_tree(monkeypatch, tmp_path):
    run = tmp_path/'sealed'
    store(run/'retained-manifest.json', {'scope': 'SYNTHETIC_SEALED'})
    original = (run/'retained-manifest.json').read_bytes()
    def refuse():
        raise ValueError('synthetic missing guardian')
    monkeypatch.setattr(supervision, 'require_current', refuse)
    with pytest.raises(ValueError, match='missing guardian'):
        retention.finalize_retention(run, tmp_path/'assessment.json', code_root=tmp_path)
    assert (run/'retained-manifest.json').read_bytes() == original
    monkeypatch.setattr(supervision, 'require_current', lambda: {})
    monkeypatch.setattr(supervision, 'event', lambda *args, **kwargs: None)
    monkeypatch.setattr(retention, 'verify_inventory', lambda path: {'status': 'SYNTHETIC_VERIFIED'})
    assert retention.finalize_retention(run, tmp_path/'assessment.json', code_root=tmp_path) == {
        'status': 'SYNTHETIC_VERIFIED'}
    assert (run/'retained-manifest.json').read_bytes() == original


@pytest.mark.parametrize('observation_bytes', [admission.MIB, 16*admission.MIB])
def test_observer_future_writes_reserve_free_space_without_science_quota(
        monkeypatch, tmp_path, observation_bytes):
    from scripts.whole_source import storage
    monkeypatch.setattr(supervision, 'require_current',
                        lambda: {'observation_bytes': observation_bytes})
    forecast = {'phase_growth_bytes': {'source': 1234},
                'logical_allowance_bytes': 1024*admission.MIB}
    monkeypatch.setattr(admission, 'topology', lambda problem: forecast)
    monkeypatch.setattr(admission, 'problem_id', lambda problem: 'a'*64)
    monkeypatch.setattr(storage, '_volume', lambda path: 'SYNTHETIC_VOLUME')
    monkeypatch.setattr(storage, '_census', lambda *args: {'logical_bytes': 0})
    monkeypatch.setattr(storage, 'StorageBudget',
                        lambda roots, **kwargs: SimpleNamespace(roots=roots, options=kwargs))
    run = tmp_path/'science'
    budget, actual_forecast = admission.operation_budget(object(), run, tmp_path, phase='source')
    assert budget.options['min_free_bytes'] == 64*admission.MIB+observation_bytes
    assert budget.roots == {run: 32*admission.MIB+1234}
    assert actual_forecast is forecast
    assert actual_forecast['logical_allowance_bytes'] == 1024*admission.MIB


def test_partial_reuse_refuses_missing_original_observer_before_continuation(selected):
    original = selected.admission.read_bytes()
    root = Path(selected.binding['root'])
    binding, _ = observer(root, '2'*32, selected.current['code'])
    (root/'receipts'/('1'*32+'.json')).unlink()
    with pytest.raises(ContractError, match='prior phase supervision'):
        admission.bind_phase_attempt({**selected.report, 'supervision': binding},
                                     selected.directory, selected.run)
    assert selected.admission.read_bytes() == original
    assert not selected.admission.with_name(selected.admission.stem+'-'+'2'*32+'.json').exists()
