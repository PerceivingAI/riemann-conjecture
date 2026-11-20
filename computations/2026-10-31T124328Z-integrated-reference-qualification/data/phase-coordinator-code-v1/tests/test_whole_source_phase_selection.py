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
    run = root/'run'
    run.mkdir(parents=True)
    capture, versions = metadata_runtime
    start = put(run/'implementation/start.json', {
        'format': 'whole-source-coordinator-implementation-v1', 'phase': 'science',
        'problem_id': '1'*64, 'code': [], 'inherited_capture': capture,
        'runtime_versions': versions, 'argv': ['TEST_ONLY'], 'production_admission': False})
    put(run/'integration-execution.json', TEST_ONLY)
    context = {'problem_id': '1'*64, 'configuration': TEST_ONLY,
               'implementation': start, 'proposal_input': proposal_input}
    return run, PhaseJournal(run, context)


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
    roots = selection.selected_execution_roots(run)
    assert roots == [
        ('premises', Path(journal.completed['prepare']['directory'])/'premises'),
        ('source', Path(journal.completed['source']['directory'])),
        ('audit', Path(journal.completed['audit']['directory'])),
        ('proposal', Path(journal.completed['proposal']['directory'])/'work'),
        ('exact', Path(journal.completed['exact']['directory'])),
    ]
    assert (abandoned/'receipt.json').exists()
    assert not any(path == abandoned for _, path in roots)


def test_installed_child_has_no_new_proposal_execution_root(tmp_path, metadata_runtime):
    installed = put(tmp_path/'installed/proposal.json', TEST_ONLY)
    run, journal = operation(tmp_path, metadata_runtime, proposal_input=installed)
    for phase in SCIENCE_PHASES:
        finish(journal, phase, {'proposal': installed} if phase == 'proposal' else None)
    publish_pipeline(run, journal)
    selection.validate_pipeline(run, tmp_path)
    assert 'proposal' not in [group for group, _ in selection.selected_execution_roots(run)]


def test_selected_replay_recurses_actual_child_not_flat_attempt(science, metadata_runtime):
    root, run, journal, _ = science
    finish(journal, 'controls')
    prior = {name: row['outputs'] for name, row in journal.completed.items()}
    directory, _ = journal.begin('replay', prior)
    tree = directory/'captured-root'
    installed = put(tree/'installed/proposal.json', TEST_ONLY)
    child, child_journal = operation(tree, metadata_runtime, proposal_input=installed)
    for phase in SCIENCE_PHASES:
        finish(child_journal, phase, {'proposal': installed} if phase == 'proposal' else None)
    publish_pipeline(child, child_journal)
    capture = put(tree/'capture-manifest.json', TEST_ONLY)
    replay = put(directory/'replay-receipt.json', {
        **TEST_ONLY, 'original_run': retention._record(run/'pipeline-result.json'),
        'replayed_run': retention._record(child/'pipeline-result.json'), 'capture': capture})
    journal.complete('replay', {'replay': replay})
    assert selection.selected_execution_roots(run)[-1] == ('replay', child)
    assert ('replay', directory) not in selection.selected_execution_roots(run)


def test_selected_replay_rejects_external_child(science):
    root, run, journal, _ = science
    finish(journal, 'controls')
    prior = {name: row['outputs'] for name, row in journal.completed.items()}
    directory, _ = journal.begin('replay', prior)
    capture = put(directory/'captured-root/capture-manifest.json', TEST_ONLY)
    replay = put(directory/'replay-receipt.json', {
        **TEST_ONLY, 'original_run': retention._record(run/'pipeline-result.json'),
        'replayed_run': put(root/'foreign/pipeline-result.json', TEST_ONLY), 'capture': capture})
    journal.complete('replay', {'replay': replay})
    with pytest.raises(ContractError, match='escapes captured'):
        selection.selected_execution_roots(run)


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
