"""Coordinator dispatch controls with nonproof role adapters, never full acceptance."""
from pathlib import Path
import json

import pytest

from scripts.whole_source import retention, selection
from scripts.whole_source.contract import ROOT, ContractError, bind_problem, canonical_bytes
from scripts.whole_source.coordinator import read_phase_records


@pytest.fixture
def control(monkeypatch):
    from tempfile import TemporaryDirectory
    from contextlib import nullcontext
    from scripts.whole_source import admission, supervision
    # No guardian or numerical execution is claimed by this dispatch fixture.
    # Actual admission and observer authority have separate regression coverage.
    binding = {'root': str(ROOT/'.pytest_cache/synthetic-phase-observer'),
               'invocation_id': '1'*32, 'operation_id': '2'*64,
               'intent': {'path': 'intents/'+'1'*32+'.json', 'sha256': '3'*64, 'size': 1}}
    monkeypatch.setattr(supervision, 'require_current', lambda: binding)
    def synthetic_admission(phase, problem, run, root, **kwargs):
        return nullcontext({'format': admission.FORMAT, 'policy': admission.POLICY,
            'phase': phase, 'inputs': kwargs.get('inputs') or {},
            'supervision': binding, 'scope': 'SYNTHETIC_NONAPPROVAL'})
    monkeypatch.setattr(admission, 'admitted_phase', synthetic_admission)
    monkeypatch.setattr(admission, 'bootstrap_scope', lambda *args, **kw: nullcontext({}))
    directory_manager = TemporaryDirectory(prefix='phase-run-', dir=ROOT/'.pytest_cache')
    tmp_path = Path(directory_manager.name)
    problem = bind_problem('retained-t081')
    paths = retention.prepare_inputs(problem, tmp_path/'inputs', origin_git_commit='1'*40,
        origin_git_dirty=True)
    config = json.loads(paths['execution'].read_bytes())
    run = tmp_path/'operation'
    run.mkdir()
    calls = []
    fail = set()

    def dispatch(phase, directory, prior, *args, **kwargs):
        calls.append((phase, directory))
        directory.mkdir(parents=True, exist_ok=True)
        if phase in fail:
            (directory/'partial-control.json').write_bytes(b'NONPROOF_FAILED_ATTEMPT')
            raise RuntimeError('controlled phase interruption')
        names = {
            'prepare': ('source-inputs/problem.json', 'source-inputs/execution.json', 'premises/premises-receipt.json'),
            'source': ('producer/source-manifest.json', 'producer/source-execution.json'),
            'audit': ('analytical-receipt.json', 'audit-execution.json'),
            'proposal': ('work/proposal.json',),
        }
        for name in names[phase]:
            path = directory/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(canonical_bytes({'scope': 'CONTROL_ONLY', 'phase': phase}))

    def validate(phase, outputs, directory, **kwargs):
        assert outputs == retention._phase_outputs(phase, directory)
        assert all(retention._document(record) == {'scope': 'CONTROL_ONLY', 'phase': phase}
                   for record in outputs.values())

    monkeypatch.setattr(retention, '_dispatch_phase', dispatch)
    monkeypatch.setattr(selection, 'validate_phase', validate)
    try:
        yield problem, config, run, calls, fail
    finally:
        directory_manager.cleanup()


def execute(control, through, resume=False):
    problem, config, run, _, _ = control
    return retention._execute(problem, config, run, ROOT, through=through, resume=resume)


def test_stop_before_exact_preparation_then_continue_without_repeating(control):
    report = execute(control, 'source')
    run, calls = control[2:4]
    original = read_phase_records(run)
    assert report['status'] == 'PAUSED_AFTER_VERIFIED_PHASE'
    assert report['reference_qualification_accepted'] is False
    assert not (run/'audit').exists()
    report = execute(control, 'proposal', resume=True)
    assert [phase for phase, _ in calls] == ['prepare', 'source', 'audit', 'proposal']
    assert read_phase_records(run)['source'] == original['source']
    assert report['science_complete'] is False
    assert not (run/'exact-inputs').exists()
    assert not (run/'pipeline-result.json').exists()
    assert not (run/'implementation/complete.json').exists()


def test_failed_nonresumable_phase_uses_fresh_attempt_preserving_upstream(control):
    execute(control, 'source')
    run, calls, fail = control[2:]
    original = read_phase_records(run)['source']
    fail.add('audit')
    with pytest.raises(RuntimeError, match='controlled'):
        execute(control, 'audit', resume=True)
    failed = calls[-1][1]
    retained = (failed/'partial-control.json').read_bytes()
    fail.clear()
    execute(control, 'audit', resume=True)
    assert [phase for phase, _ in calls] == ['prepare', 'source', 'audit', 'audit']
    assert calls[-1][1] != failed
    assert (failed/'partial-control.json').read_bytes() == retained
    assert read_phase_records(run)['source'] == original


def test_complete_intended_phase_recovers_without_redispatch(control, monkeypatch):
    from scripts.whole_source.coordinator import PhaseJournal
    original = PhaseJournal.complete

    def interrupted(self, phase, outputs):
        if phase == 'source':
            raise RuntimeError('owner publication interrupted')
        return original(self, phase, outputs)

    monkeypatch.setattr(PhaseJournal, 'complete', interrupted)
    with pytest.raises(RuntimeError, match='publication'):
        execute(control, 'source')
    monkeypatch.setattr(PhaseJournal, 'complete', original)
    execute(control, 'source', resume=True)
    assert [phase for phase, _ in control[3]] == ['prepare', 'source']
    assert 'source' in read_phase_records(control[2])


def test_changed_committed_output_refuses_before_later_work(control):
    execute(control, 'source')
    source = read_phase_records(control[2])['source']['outputs']['source']
    retention._phase_path(source).write_bytes(b'CHANGED')
    count = len(control[3])
    with pytest.raises(ContractError):
        execute(control, 'proposal', resume=True)
    assert len(control[3]) == count
    assert not (control[2]/'audit').exists()


def test_changed_configuration_refuses_resume_before_dispatch(control):
    execute(control, 'source')
    control[1]['origin_git_dirty'] = False
    count = len(control[3])
    with pytest.raises(ContractError):
        execute(control, 'proposal', resume=True)
    assert len(control[3]) == count


def test_unresolved_failed_history_blocks_next_phase_without_recomputing(control):
    execute(control, 'source')
    run = control[2]
    failed = run/'audit/attempts/nonselected/collection/attempts/failed/task/receipt.json'
    failed.parent.mkdir(parents=True)
    failed.write_bytes(canonical_bytes({'format': 't081-owned-stage-receipt-v1',
                                       'worker_cleanup_verified': False}))
    count = len(control[3])
    with pytest.raises(ContractError, match='cleanup'):
        execute(control, 'proposal', resume=True)
    assert len(control[3]) == count
    assert not (run/'proposal').exists()


def test_public_resume_requires_existing_operation_without_creating_it(control, monkeypatch):
    from types import SimpleNamespace
    parent = control[2].parent
    output = parent/'never-created'
    monkeypatch.setattr(retention.shutil, 'disk_usage', lambda path: SimpleNamespace(free=1 << 60))
    with pytest.raises(ContractError, match='resume'):
        retention.run(parent/'inputs/problem.json', parent/'inputs/execution.json', output, resume=True)
    assert not output.exists()


def test_missing_original_integration_input_is_not_rewritten_on_resume(control, monkeypatch):
    from types import SimpleNamespace
    execute(control, 'source')
    run = control[2]
    head = (run/'coordinator/head.json').read_bytes()
    monkeypatch.setattr(retention.shutil, 'disk_usage', lambda path: SimpleNamespace(free=1 << 60))
    parent = run.parent
    with pytest.raises(ContractError, match='resume'):
        retention.run(parent/'inputs/problem.json', parent/'inputs/execution.json', run, resume=True)
    assert not (run/'integration-execution.json').exists()
    assert (run/'coordinator/head.json').read_bytes() == head
