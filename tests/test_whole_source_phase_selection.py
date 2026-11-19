"""Test-only selection metadata. These fixtures have no mathematical authority."""
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.whole_source import retention, selection
from scripts.whole_source.contract import ContractError, canonical_bytes
from scripts.whole_source.coordinator import PHASES, SCIENCE_PHASES, PhaseJournal


TEST_ONLY = {'TEST_ONLY_NO_MATHEMATICAL_AUTHORITY': True}


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = canonical_bytes(value)
    path.write_bytes(raw)
    return {'directory': str(path.parent.resolve()), 'artifact': {
        'path': path.name, 'sha256': hashlib.sha256(raw).hexdigest(), 'size': len(raw)}}


def synthetic_outputs(directory, phase):
    return {name: put(directory/relative, {**TEST_ONLY, 'phase': phase, 'role': name,
                        **({'assessment': {'gamma': None}} if phase == 'exact' else {})})
            for name, relative in selection._OUTPUT_PATHS[phase].items()}




@pytest.fixture
def metadata_runtime(monkeypatch):
    """Replace implementation identity only, never a role's mathematical gates."""
    capture = {'TEST_ONLY_CAPTURE': True}
    versions = {'TEST_ONLY_RUNTIME': True}
    monkeypatch.setattr(retention, '_implementation_code', lambda root: ([], capture, {}))
    monkeypatch.setattr(retention, '_runtime_versions', lambda: versions)
    return capture, versions


def operation(root, metadata_runtime, *, proposal_input=None):
    run = root/('replay-run' if proposal_input else 'run')
    run.mkdir(parents=True)
    capture, versions = metadata_runtime
    start = put(run/'implementation/start.json', {
        'format': 'whole-source-coordinator-implementation-v1', 'phase': 'science',
        'problem_id': '1'*64, 'code': [], 'inherited_capture': capture,
        'runtime_versions': versions, 'argv': ['TEST_ONLY'], 'production_admission': False})
    put(run/'integration-execution.json', TEST_ONLY)
    context = {'problem_id': '1'*64, 'configuration': TEST_ONLY,
               'implementation': start, 'proposal_input': proposal_input}
    return run, PhaseJournal(run, context, code_root=root)


def finish(journal, phase, outputs=None):
    prior = {name: row['outputs'] for name, row in journal.completed.items()}
    directory, reused = journal.begin(phase, prior)
    assert not reused
    if outputs is None:
        outputs = synthetic_outputs(directory, phase)
    else:
        directory.mkdir()
        put(directory/'installed-proposal.json', outputs)
    journal.complete(phase, outputs)
    return directory


def publish_pipeline(run, journal, **changes):
    rows = journal.completed
    document = {name: rows[phase]['outputs'][output]
                for name, (phase, output) in selection._PIPELINE_OUTPUTS.items()}
    document.update({
        'format': 'whole-source-pipeline-result-v3', 'status': 'COMPLETE_FRESH_SOURCE_AUDIT_AND_EXACT',
        'problem_id': '1'*64, 'implementation': journal.context['implementation'],
        'phase_chain': [rows[phase]['record'] for phase in SCIENCE_PHASES], 'gamma': None,
        'fresh_proposal': journal.context['proposal_input'] is None, 'production_admission': False})
    document.update(changes)
    pipeline = put(run/'pipeline-result.json', document)
    put(run/'implementation/complete.json', {
        'format': 'whole-source-coordinator-completion-v1', 'start': journal.context['implementation'],
        'outputs': {'pipeline': pipeline}, 'production_admission': False})
    return document


@pytest.fixture
def science(tmp_path, metadata_runtime):
    run, journal = operation(tmp_path, metadata_runtime)
    for phase in SCIENCE_PHASES:
        finish(journal, phase)
    document = publish_pipeline(run, journal)
    return tmp_path, run, journal, document


def test_current_pipeline_and_completion_can_be_verified_after_relocation(tmp_path, metadata_runtime, monkeypatch):
    import shutil
    root = tmp_path/'private-project-location'
    run, journal = operation(root, metadata_runtime)
    for phase in SCIENCE_PHASES:
        finish(journal, phase)
    monkeypatch.setattr(retention, 'problem_id', lambda problem: '1'*64)
    before = retention._publish_pipeline(None, TEST_ONLY, run, root, journal)
    for name in ('pipeline-result.json', 'implementation/complete.json'):
        raw = (run/name).read_bytes()
        assert b'private-project-location' not in raw and b'"directory"' not in raw
    relocated = tmp_path/'moved'
    shutil.copytree(root, relocated)
    selected, _ = selection.validate_pipeline(relocated/'run', relocated)
    assert selected['gamma'] == before['gamma']
    assert selection._path(selected['source']).is_relative_to(relocated)
    assert selected['phase_chain'][0]['artifact'] == before['phase_chain'][0]['artifact']
    corrupted = selection._path(selected['source'])
    corrupted.write_bytes(b'CHANGED_NONPROOF')
    with pytest.raises(ContractError):
        selection.validate_pipeline(relocated/'run', relocated)


def test_pipeline_metadata_does_not_run_scientific_roles(science, monkeypatch):
    from scripts.whole_source import pipeline, exact, proposal
    def forbidden(*args, **kwargs):
        raise AssertionError('metadata selection must not execute a scientific role validator')
    monkeypatch.setattr(pipeline, 'SourceReader', forbidden)
    monkeypatch.setattr(pipeline, '_bind', forbidden)
    monkeypatch.setattr(exact, '_bind_exact', forbidden)
    monkeypatch.setattr(proposal, 'read_proposal', forbidden)
    root, run, journal, document = science
    result, rows = selection.validate_pipeline(run, root)
    assert result == document
    assert rows == journal.completed
    assert result['production_admission'] is False
    assert selection._document(result['source'])['TEST_ONLY_NO_MATHEMATICAL_AUTHORITY'] is True


@pytest.mark.parametrize('field,value', [
    ('format', 'whole-source-pipeline-result-v2'),
    ('phase_chain', []), ('fresh_proposal', False), ('production_admission', True),
    ('problem_id', '2'*64), ('gamma', {'numerator': '0x1', 'denominator': '0x1'}),
])
def test_pipeline_rejects_unbound_metadata(science, field, value):
    root, run, journal, _ = science
    publish_pipeline(run, journal, **{field: value})
    with pytest.raises(ContractError):
        selection.validate_pipeline(run, root)


def test_pipeline_rejects_reordered_completion_chain(science):
    root, run, journal, _ = science
    chain = [journal.completed[phase]['record'] for phase in reversed(SCIENCE_PHASES)]
    publish_pipeline(run, journal, phase_chain=chain)
    with pytest.raises(ContractError, match='phase chain'):
        selection.validate_pipeline(run, root)


def test_pipeline_rejects_byte_identical_external_adoption(science):
    root, run, journal, document = science
    source = selection._document(document['source'])
    external = put(root/'unrelated/source-manifest.json', source)
    publish_pipeline(run, journal, source=external)
    with pytest.raises(ContractError, match='nonselected'):
        selection.validate_pipeline(run, root)


def test_pipeline_rejects_missing_original_completion(science):
    root, run, _, _ = science
    (run/'implementation/complete.json').unlink()
    with pytest.raises((ContractError, OSError)):
        selection.validate_pipeline(run, root)


def test_pipeline_rejects_changed_original_configuration(science):
    root, run, _, _ = science
    put(run/'integration-execution.json', {'TEST_ONLY_CHANGED_CONFIGURATION': True})
    with pytest.raises(ContractError, match='configuration'):
        selection.validate_pipeline(run, root)


def test_pipeline_rejects_changed_original_start(science):
    root, run, _, _ = science
    put(run/'implementation/start.json', {'TEST_ONLY_REPLACED_START': True})
    with pytest.raises(ContractError):
        selection.validate_pipeline(run, root)


@pytest.mark.parametrize('phase', PHASES)
def test_output_mapping_rejects_extra_roles(tmp_path, phase):
    run = tmp_path/'run'
    directory = run/phase/'attempts'/('a'*32)
    outputs = synthetic_outputs(directory, phase)
    outputs['unbound'] = next(iter(outputs.values()))
    with pytest.raises(ContractError, match='output roles'):
        selection._mapping(phase, outputs, directory, run, None)


@pytest.mark.parametrize('phase', PHASES)
def test_output_mapping_rejects_foreign_attempt(tmp_path, phase):
    run = tmp_path/'run'
    directory = run/phase/'attempts'/('a'*32)
    foreign = run/phase/'attempts'/('b'*32)
    outputs = synthetic_outputs(foreign, phase)
    with pytest.raises(ContractError, match='intended phase'):
        selection._mapping(phase, outputs, directory, run, None)


def test_mapping_rejects_noncanonical_locator_even_for_same_file(tmp_path):
    run = tmp_path/'run'
    directory = run/'proposal/attempts'/('a'*32)
    outputs = synthetic_outputs(directory, 'proposal')
    outputs['proposal'] = {'directory': str(directory), 'artifact': {
        **outputs['proposal']['artifact'], 'path': 'work/proposal.json'}}
    with pytest.raises(ContractError, match='intended phase'):
        selection._mapping('proposal', outputs, directory, run, None)


def test_mapping_rejects_changed_selected_bytes(tmp_path):
    run = tmp_path/'run'
    directory = run/'exact/attempts'/('a'*32)
    outputs = synthetic_outputs(directory, 'exact')
    put(directory/'report.json', {'TEST_ONLY_TAMPER': True})
    with pytest.raises(ContractError, match='changed phase artifact'):
        selection._mapping('exact', outputs, directory, run, None)


@pytest.mark.parametrize('damage', ['missing', 'different'])
def test_installed_proposal_requires_original_dispatch_marker(tmp_path, damage):
    run = tmp_path/'run'
    directory = run/'proposal/attempts'/('a'*32)
    directory.mkdir(parents=True)
    installed = put(tmp_path/'captured/proposal.json', TEST_ONLY)
    if damage == 'different':
        other = put(tmp_path/'other/proposal.json', TEST_ONLY)
        put(directory/'installed-proposal.json', {'proposal': other})
    with pytest.raises((ContractError, OSError)):
        selection._mapping('proposal', {'proposal': installed}, directory, run, installed)


def test_installed_proposal_is_only_exact_context_record_exception(tmp_path):
    run = tmp_path/'run'
    directory = run/'proposal/attempts'/('a'*32)
    directory.mkdir(parents=True)
    installed = put(tmp_path/'captured/proposal.json', TEST_ONLY)
    other = put(tmp_path/'other/proposal.json', TEST_ONLY)
    put(directory/'installed-proposal.json', {'proposal': installed})
    assert selection._mapping('proposal', {'proposal': installed}, directory, run, installed) == directory
    with pytest.raises(ContractError, match='unbound installed'):
        selection._mapping('proposal', {'proposal': other}, directory, run, installed)
    with pytest.raises(ContractError, match='intended phase'):
        selection._mapping('proposal', {'proposal': installed}, directory, run, None)


def test_validate_phase_rejects_flattened_or_swapped_prior(science):
    root, run, journal, _ = science
    row = journal.completed['exact']
    prior = {name: value['outputs'] for name, value in journal.completed.items() if name != 'exact'}
    prior['prepare'] = prior['exact-inputs']
    with pytest.raises(ContractError, match='predecessor'):
        selection.validate_phase('exact', row['outputs'], Path(row['directory']),
                                 run=run, root=root, prior=prior)


def test_validate_phase_refuses_synthetic_outputs_without_owned_authority(science):
    root, run, journal, _ = science
    row = journal.completed['source']
    prior = {'prepare': journal.completed['prepare']['outputs']}
    with pytest.raises(ContractError, match='owned execution receipts'):
        selection.validate_phase('source', row['outputs'], Path(row['directory']),
                                 run=run, root=root, prior=prior)


def test_fabricated_exact_report_cannot_replace_producer_journal(tmp_path):
    put(tmp_path/'report.json', {'status': 'PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL', **TEST_ONLY})
    with pytest.raises((ContractError, OSError)):
        selection._exact_report(None, {}, {}, SimpleNamespace(collection_id='0'*64), None, tmp_path, positive=True)


def test_selected_roots_ignore_uncommitted_and_nonselected_attempts(science):
    root, run, journal, _ = science
    abandoned = run/'source/attempts'/('f'*32)
    put(abandoned/'receipt.json', {'TEST_ONLY_FAILED_UNSELECTED': True})
    put(run/'controls/attempts'/('e'*32)/'controls-receipt.json', TEST_ONLY)
    roots = selection.selected_execution_roots(run, root)
    assert roots == [
        ('premises', Path(journal.completed['prepare']['directory'])/'premises', root),
        ('source', Path(journal.completed['source']['directory']), root),
        ('audit', Path(journal.completed['audit']['directory']), root),
        ('proposal', Path(journal.completed['proposal']['directory'])/'work', root),
        ('exact', Path(journal.completed['exact']['directory']), root),
    ]
    assert (abandoned/'receipt.json').exists()
    assert not any(path == abandoned for _, path, _ in roots)


def test_installed_child_has_no_new_proposal_execution_root(tmp_path, metadata_runtime):
    installed = put(tmp_path/retention._REPLAY_PROPOSAL, TEST_ONLY)
    run, journal = operation(tmp_path, metadata_runtime, proposal_input=installed)
    for phase in SCIENCE_PHASES:
        finish(journal, phase, {'proposal': installed} if phase == 'proposal' else None)
    publish_pipeline(run, journal)
    selection.validate_pipeline(run, tmp_path)
    assert 'proposal' not in [group for group, _, _ in selection.selected_execution_roots(run, tmp_path)]


def test_selected_replay_recurses_actual_child_not_flat_attempt(science, metadata_runtime):
    root, run, journal, _ = science
    finish(journal, 'controls')
    prior = {name: row['outputs'] for name, row in journal.completed.items()}
    directory, _ = journal.begin('replay', prior)
    tree = directory/'captured-root'
    installed = put(tree/retention._REPLAY_PROPOSAL, TEST_ONLY)
    child, child_journal = operation(tree, metadata_runtime, proposal_input=installed)
    for phase in SCIENCE_PHASES:
        finish(child_journal, phase, {'proposal': installed} if phase == 'proposal' else None)
    publish_pipeline(child, child_journal)
    put(tree/'capture-manifest.json', TEST_ONLY)
    replay = put(directory/'replay-receipt.json', {
        'format': retention._REPLAY_FORMAT, **retention._replay_bindings(run, child, tree)})
    journal.complete('replay', {'replay': replay})
    roots = selection.selected_execution_roots(run, root)
    assert roots[-1] == ('replay', child, tree)
    assert not any(path == directory for _, path, _ in roots)


def test_frozen_replay_reader_rejects_external_child(science):
    root, run, journal, _ = science
    finish(journal, 'controls')
    prior = {name: row['outputs'] for name, row in journal.completed.items()}
    directory, _ = journal.begin('replay', prior)
    capture = put(directory/'captured-root/capture-manifest.json', TEST_ONLY)
    replay = put(directory/'replay-receipt.json', {
        'format': retention._FROZEN_REPLAY_FORMAT, 'original_run': retention._record(run/'pipeline-result.json'),
        'replayed_run': put(root/'foreign/pipeline-result.json', TEST_ONLY), 'capture': capture})
    journal.complete('replay', {'replay': replay})
    with pytest.raises(ContractError, match='escapes captured'):
        selection.selected_execution_roots(run, root)


@pytest.mark.parametrize('role,file', [
    ('original_run', 'pipeline-result.json'),
    ('replayed_run', 'captured-root/replay-run/pipeline-result.json'),
    ('capture', 'captured-root/capture-manifest.json'),
])
def test_current_replay_rejects_changed_bound_artifact(tmp_path, role, file):
    run, directory = tmp_path/'run', tmp_path/'replay'
    tree, child = directory/'captured-root', directory/'captured-root/replay-run'
    put(run/'pipeline-result.json', TEST_ONLY)
    put(child/'pipeline-result.json', TEST_ONLY)
    put(tree/'capture-manifest.json', TEST_ONLY)
    receipt = {'format': retention._REPLAY_FORMAT, **retention._replay_bindings(run, child, tree)}
    changed = (run if role == 'original_run' else directory)/file
    put(changed, {**TEST_ONLY, 'changed': role})
    with pytest.raises(ContractError, match='artifact role binding differs'):
        selection._replay_child(run, directory, receipt, tmp_path)


def test_current_replay_never_adopts_pipeline_from_another_captured_run(tmp_path):
    run, directory = tmp_path/'run', tmp_path/'replay'
    tree = directory/'captured-root'
    foreign = tree/'not-the-original-run'
    put(run/'pipeline-result.json', TEST_ONLY)
    put(foreign/'pipeline-result.json', TEST_ONLY)
    put(tree/'capture-manifest.json', TEST_ONLY)
    receipt = {'format': retention._REPLAY_FORMAT, **retention._replay_bindings(run, foreign, tree)}
    with pytest.raises(ContractError, match='missing collection root'):
        selection._replay_child(run, directory, receipt, tmp_path)


@pytest.mark.parametrize('exit_code', [0, 17, None])
def test_current_replay_writer_keeps_launch_paths_in_memory(tmp_path,metadata_runtime,monkeypatch,exit_code):
    from scripts.whole_source import supervision
    root = tmp_path
    run,journal = operation(root,metadata_runtime)
    for phase in SCIENCE_PHASES:
        finish(journal,phase)
    directory = root/'replay'
    monkeypatch.setattr(retention, 'problem_id', lambda problem: '1'*64)
    pipeline = retention._publish_pipeline(None, TEST_ONLY, run, root, journal)
    tree, child = directory/'captured-root', directory/'captured-root/replay-run'
    proposal = selection._path(pipeline['proposal'])
    installed = tree/retention._REPLAY_PROPOSAL
    empty = {'size': 0, 'sha256': hashlib.sha256(b'').hexdigest()}

    def capture_inputs(problem, destination, *, code_root, proposal_path):
        assert (destination, code_root, proposal_path) == (tree, root, proposal)
        put(tree/'capture-manifest.json', TEST_ONLY)
        put(installed, selection._document(pipeline['proposal']))

    def launch(command, cwd, code_root):
        assert command == [retention.sys.executable, '-I', '-B', '-c', retention._REPLAY_ENTRY,
                           str(tree), str(child), str(child/'integration-execution.json'), str(installed)]
        assert (cwd, code_root) == (tree, root)
        assert not (child/'proposal').exists()
        assert (child/'integration-execution.json').read_bytes() == (run/'integration-execution.json').read_bytes()
        if exit_code is None:
            raise FileNotFoundError(2, 'load failed', str(installed))
        if exit_code:
            return exit_code, {'stdout': empty, 'stderr': empty}
        start = retention._capture_implementation(None, child, tree, 'science')
        installed_record = retention._record(installed)
        journal = PhaseJournal(child, {'problem_id': '1'*64, 'configuration': TEST_ONLY,
                                       'implementation': start, 'proposal_input': installed_record}, code_root=tree)
        for phase in SCIENCE_PHASES:
            finish(journal, phase, {'proposal': installed_record} if phase == 'proposal' else None)
        retention._publish_pipeline(None, TEST_ONLY, child, tree, journal)
        return 0, {'stdout': empty, 'stderr': empty}

    def receipts(receipt_root, *, code_root):
        assert (receipt_root, code_root) == (child, tree)
        return [put(child/'stage/receipt.json', TEST_ONLY)]

    monkeypatch.setattr(supervision, 'require_current', lambda: None)
    monkeypatch.setattr(retention, 'bind_problem', lambda *args, **kwargs: None)
    monkeypatch.setattr(retention, 'problem_id', lambda problem: '1'*64)
    monkeypatch.setattr(retention, '_check_loaded_implementation', lambda path: None)
    monkeypatch.setattr(retention, 'capture_inputs', capture_inputs)
    monkeypatch.setattr(retention, '_replay_process', launch)
    monkeypatch.setattr(retention, 'compare_science', lambda *args, **kwargs: TEST_ONLY)
    monkeypatch.setattr(retention, '_verify_receipts', receipts)
    if exit_code != 0:
        with pytest.raises((ContractError, FileNotFoundError)):
            retention.replay(run, directory, code_root=root)
        failure = selection._document(retention._record(directory/'replay-failure.json'))
        assert failure['reason'] == ('launch_or_wait_failed' if exit_code is None else 'child_exit')
        assert failure['exit_code'] == exit_code
        assert b'load failed' not in canonical_bytes(failure)
        assert retention._REPLAY_PROPOSAL.name.encode() not in canonical_bytes(failure)
        assert not (directory/'replay-receipt.json').exists()
        return
    document = retention.replay(run, directory, code_root=root)
    assert document['format'] == retention._REPLAY_FORMAT
    for path in (directory/'replay-receipt.json', directory/retention._REPLAY_DIAGNOSTICS,
                 directory/'implementation/start.json', child/'implementation/start.json'):
        raw = path.read_bytes()
        assert b'"argv"' not in raw and b'"directory"' not in raw
        assert root.as_posix().encode() not in raw and b'PYTHONPATH' not in raw
    assert selection._replay_child(run, directory, document, root) == (tree, child)
    selection._replay_invocation(document, tree, child, installed)
    selection._replay_cleanup(document, tree, child)
    assert 'streams' not in document
    previous, = retention.verify_retained_diagnostics(directory)
    sealed = retention._seal(directory,independent_diagnostics=True)
    diagnostic_path = directory/retention._REPLAY_DIAGNOSTICS
    diagnostics = selection._document(retention._record(diagnostic_path))
    revised = b'corrected-summary'
    diagnostics['streams']['stdout'] = {'size':len(revised),'sha256':hashlib.sha256(revised).hexdigest()}
    put(diagnostic_path, diagnostics)
    current, = retention.verify_retained_diagnostics(directory)
    assert previous['sha256'] != current['sha256']
    assert retention.verify_inventory(directory) == sealed
    diagnostics['streams'].pop('stderr')
    put(diagnostic_path, diagnostics)
    with pytest.raises(ContractError, match='stream evidence'):
        retention.verify_retained_diagnostics(directory)
    assert retention.verify_inventory(directory) == sealed
    selection._replay_invocation(document, tree, child, installed)
    with pytest.raises(ContractError, match='genuine owned cleanup'):
        selection._replay_cleanup({**document, 'owned_cleanup': None}, tree, child)
    put(installed, {'changed_nonproof_proposal': True})
    with pytest.raises(ContractError, match='invocation does not bind'):
        selection._replay_invocation(document, tree, child, installed)


def test_current_capture_installs_only_proposal_inputs_under_fixed_role(tmp_path, monkeypatch):
    from scripts.whole_source import proposal
    root, tree = tmp_path/'original', tmp_path/'capture'
    original = root/'run/proposal/attempts/a/work'
    panel = put(original/'panels/one.json', TEST_ONLY)['artifact'] | {'path': 'panels/one.json'}
    put(original/'proposal-producers.json', TEST_ONLY)
    ref = put(original/'proposal.json', {'format': proposal._PROPOSAL_CORE, 'source': TEST_ONLY,
                                        'blocks': [{'integer_panels': [{'artifact': panel}]}]})
    put(root/retention.OLD_CAPTURE/'captured-source-inputs-v1.json', {'files': []})
    problem = SimpleNamespace(evidence=[], profile='TEST_ONLY')
    for module in (retention, selection):
        monkeypatch.setattr(module, 'bind_problem', lambda *args, **kwargs: problem)
        monkeypatch.setattr(module, 'problem_id', lambda problem: '1'*64)
    monkeypatch.setattr(retention, 'CODE', ())
    monkeypatch.setattr(retention, '_RUNTIME', ())
    monkeypatch.setattr(proposal, 'read_proposal', lambda *args: None)
    manifest = retention.capture_inputs(problem, tree, code_root=root, proposal_path=original/'proposal.json')
    assert manifest['format'] == retention._REPLAY_CAPTURE_FORMAT
    selection._capture(tree, problem, root, ref, proposal_destination=retention._REPLAY_PROPOSAL)
    assert not (tree/'run').exists()
    files = [entry['artifact']['path'] for entry in manifest['files'] if entry['roles'] == ['NONPROOF_ONLY']]
    assert files == ['replay-inputs/panels/one.json', 'replay-inputs/proposal.json']
    legacy = original/'legacy-proposal.json'
    put(legacy, {'format':'whole-source-congruence-proposal-v1','source':TEST_ONLY})
    rejected = tmp_path/'legacy-capture'
    with pytest.raises(ContractError, match='legacy proposal is read-only'):
        retention.capture_inputs(problem, rejected, code_root=root, proposal_path=legacy)
    assert not rejected.exists()


def test_capture_inventory_cannot_claim_expected_scientific_outputs(tmp_path):
    put(tmp_path/'capture-manifest.json', {**TEST_ONLY, 'expected_new_outputs_installed': True})
    installed = put(tmp_path/'proposal.json', TEST_ONLY)
    directory = tmp_path/'run/proposal/attempts'/('a'*32)
    directory.mkdir(parents=True)
    put(directory/'installed-proposal.json', {'proposal': installed})
    # A marker binds dispatch only. It does not turn these bytes into a proposal.
    assert selection._mapping('proposal', {'proposal': installed}, directory, tmp_path/'run', installed) == directory
    from scripts.whole_source.proposal import read_proposal
    with pytest.raises(ContractError, match='nonproof proposal core'):
        read_proposal(tmp_path/'proposal.json', None, {})


def test_phase_predecessor_mapping_is_not_dict_insertion_order(science):
    root, run, journal, _ = science
    row = journal.completed['exact']
    prior = {phase: journal.completed[phase]['outputs'] for phase in reversed(SCIENCE_PHASES[:-1])}
    with pytest.raises(ContractError, match='owned execution receipts'):
        selection.validate_phase('exact', row['outputs'], Path(row['directory']),
                                 run=run, root=root, prior=prior)


def test_raw_stage_receipt_cannot_claim_owned_producer_authority(tmp_path):
    receipt = put(tmp_path/'receipt.json', {'TEST_ONLY_FORGED_OWNERSHIP': True})
    with pytest.raises(ContractError, match='receipt format'):
        selection._stage_tasks(receipt, role='exact', function='evaluate_exact')
