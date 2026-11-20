"""Missing consumer edges. TEST_ONLY metadata never grants mathematical authority."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace

import pytest

from scripts.whole_source import retention, selection, supervision
from scripts.whole_source.contract import ROOT, ContractError, bind_problem, canonical_bytes
from scripts.whole_source.coordinator import SCIENCE_PHASES, read_phase_records
from tests.test_whole_source_phase_run import control
from tests.test_whole_source_phase_selection import (
    finish, metadata_runtime, operation, science,
)


QUALIFICATION = ROOT/'computations/2026-10-31T124328Z-integrated-reference-qualification'


def tree(directory):
    return {path.relative_to(directory).as_posix(): path.read_bytes()
            for path in directory.rglob('*') if path.is_file()}


def forbidden(*args, **kwargs):
    raise AssertionError('rejected TEST_ONLY metadata must not dispatch downstream work')


@pytest.mark.parametrize('completed_count', range(len(SCIENCE_PHASES)))
def test_incomplete_selected_science_refuses_before_downstream_work(
        tmp_path, metadata_runtime, monkeypatch, completed_count):
    run, journal = operation(tmp_path, metadata_runtime)
    for phase in SCIENCE_PHASES[:completed_count]:
        finish(journal, phase)
    before = tree(run)
    monkeypatch.setattr(retention, '_dispatch_phase', forbidden)
    monkeypatch.setattr(retention, '_replay_process', forbidden)
    with pytest.raises(ContractError, match='incomplete selected science phase chain'):
        selection.validate_pipeline(run, tmp_path)
    assert tree(run) == before
    assert not (run/'pipeline-result.json').exists()
    assert not (run/'ready-for-review.json').exists()


@pytest.mark.parametrize('runtime', ['python', 'python-flint'])
def test_selected_pipeline_refuses_changed_runtime_without_writes(science, monkeypatch, runtime):
    root, run, _, _ = science
    before = tree(run)
    monkeypatch.setattr(retention, '_runtime_versions',
                        lambda: {'TEST_ONLY_RUNTIME': True, runtime: 'TEST_ONLY_WRONG_RUNTIME'})
    monkeypatch.setattr(retention, '_dispatch_phase', forbidden)
    monkeypatch.setattr(retention, '_replay_process', forbidden)
    with pytest.raises(ContractError, match='changed original science implementation context'):
        selection.validate_pipeline(run, root)
    assert tree(run) == before
    assert not (run/'ready-for-review.json').exists()


@pytest.mark.parametrize('damage', ['expected-output-claim', 'unexpected-inventory-output'])
def test_real_input_capture_refuses_expected_output_inventory(tmp_path, monkeypatch, damage):
    # Real retained metadata and code are copied, but no numerical role is run.
    problem = bind_problem('retained-t081')
    captured = tmp_path/'captured-root'
    retention.capture_inputs(problem, captured)
    manifest = captured/'capture-manifest.json'
    document = json.loads(manifest.read_bytes())
    if damage == 'expected-output-claim':
        document['expected_new_outputs_installed'] = True
    else:
        path = captured/'TEST_ONLY_NONAPPROVAL/report.json'
        path.parent.mkdir()
        path.write_bytes(canonical_bytes({'TEST_ONLY_NONAPPROVAL': True}))
        artifact = retention._record(path)['artifact']
        artifact['path'] = path.relative_to(captured).as_posix()
        document['files'].append({'artifact': artifact, 'roles': ['expected-new-output']})
    manifest.write_bytes(canonical_bytes(document))
    before = tree(captured)
    monkeypatch.setattr(retention, '_dispatch_phase', forbidden)
    monkeypatch.setattr(retention, '_replay_process', forbidden)
    with pytest.raises(ContractError, match='capture contains missing or unexpected inputs'):
        selection._capture(captured, problem, ROOT)
    assert tree(captured) == before
    assert not (captured/'replay-receipt.json').exists()


@pytest.mark.parametrize('through,next_phase', [('prepare', 'source'), ('source', 'audit')])
def test_public_cli_pause_names_verified_phase_and_next_action(
        control, monkeypatch, capsys, through, next_phase):
    """Synthetic operational adapters exercise public output, not real acceptance."""
    from scripts.weil_whole_source_split import main
    _, _, original_run, calls, _ = control
    inputs = original_run.parent/'inputs'
    output = original_run.parent/'cli-operation'
    monkeypatch.setenv(supervision.ENV, 'TEST_ONLY_NONAPPROVAL')
    monkeypatch.setattr(retention.shutil, 'disk_usage', lambda path: SimpleNamespace(free=1 << 60))
    result = main([
        'run', '--problem', str(inputs/'problem.json'), '--execution', str(inputs/'execution.json'),
        '--output-dir', str(output), '--through', through])
    text = capsys.readouterr()
    assert result == 0, text.err
    assert text.out.splitlines() == [
        'Completed through: '+through, 'Next action: --resume --through '+next_phase,
        'PAUSED_AFTER_VERIFIED_PHASE']
    assert list(read_phase_records(output)) == list(SCIENCE_PHASES[:SCIENCE_PHASES.index(through)+1])
    assert [phase for phase, _ in calls] == list(SCIENCE_PHASES[:SCIENCE_PHASES.index(through)+1])
    assert not (output/next_phase).exists()
    assert not (output/'ready-for-review.json').exists()
    assert not (output/'assessment.json').exists()
    assert not (output/'retained-manifest.json').exists()


@pytest.mark.skipif(sys.platform != 'win32', reason='Genuine Windows CLI guardian controls')
def test_real_public_cli_negative_and_completed_seal_evidence():
    # The script accepts a fresh persistent output path for qualification evidence.
    # This test uses a disposable path; the focused standalone invocation preserves it.
    with tempfile.TemporaryDirectory(prefix='qualification-cli-', dir=ROOT/'.pytest_cache') as name:
        output = Path(name)/'evidence'
        environment = dict(os.environ)
        environment.pop(supervision.ENV, None)
        result = subprocess.run([
            sys.executable, '-B', str(QUALIFICATION/'integrated-qualification-cli-v1.py'),
            '--output-dir', str(output)], cwd=ROOT, env=environment,
            capture_output=True, text=True, timeout=240)
        assert result.returncode == 0, result.stdout+'\n'+result.stderr
        document = json.loads((output/'integrated-qualification-cli-result-v1.json').read_bytes())
        assert document['status'] == 'PASS_CLI_BOUNDARY_CONTROLS'
        assert document['cases'] == ['missing-resume', 'stale-policy', 'completed-seal', 'damaged-seal']
        assert document['full_math_executed'] is False
        assert document['independent_review_performed'] is False
        assert document['scientific_acceptance'] is False
        assert document['production_admission'] is False
