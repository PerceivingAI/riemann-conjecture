"""Exercise the maintained recorder with actual owned children, not numerical runs."""
import json
import threading
from pathlib import Path
import time

import pytest

from scripts.t081_resource_records import verify_stage_receipt
from scripts.t081_resource_pipeline import capture_tree
from scripts.t081_resource_supervisor import BUNDLE, Execution


MARKER = 'private-stage-fixture-layout'


def budget():
    return {'cpu_budget': 1, 'native_threads': 1, 'workers': 1,
            'memory_budget_bytes': 256 * 1024**2, 'reserve_bytes': 64 * 1024**2,
            'required_bytes': 0, 'diagnostics': [f'/home/{MARKER}'],
            'detection': {'cpu_detection_complete': True, 'cpu_sources': [{'path': MARKER}]}}


def assert_safe(root):
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            continue  # Atomic publication may have renamed the staging file.
        assert MARKER.encode() not in raw, path.name


def make_child(tmp_path, extra):
    private = tmp_path / MARKER
    private.mkdir()
    program = private / (MARKER + '.py')
    program.write_text(
        'import os, sys, time\nfrom pathlib import Path\nfrom execution_events_v1 import emit\n'
        'def main():\n'
        '    print(sys.argv[1], flush=True)\n'
        '    print(sys.argv[1], file=sys.stderr, flush=True)\n'
        "    print('x' * 9000 + sys.argv[1], flush=True)\n"
        "    emit('work', phase='kernel_step', completed=1, total=2, unit='frequency_anchors', detail=sys.argv[1])\n"
        + extra, encoding='utf-8')
    return program


def test_started_stage_retains_safe_progress_and_detects_altered_evidence(tmp_path):
    program = make_child(tmp_path, '    return 0\n')
    output = tmp_path / 'run'
    with Execution(output, budget()) as run:
        receipt = run.run('fixture', program, [str(program)], kind='fixture')
    profile = verify_stage_receipt(output, receipt, run.budget)
    assert profile['exit_code'] == 0 and profile['native_threads'] == 1
    assert receipt['worker_cleanup_verified'] is True and receipt['program_sha256'] == profile['program_sha256']
    events = [json.loads(line) for line in (output/'fixture/stdout.jsonl').read_text(encoding='utf-8').splitlines()]
    assert any(event.get('phase') == 'kernel_step' and event.get('completed') == 1 for event in events)
    assert_safe(output)
    with pytest.raises(ValueError, match='receipt/cleanup'):
        verify_stage_receipt(output, dict(receipt, worker_cleanup_verified=False), run.budget)
    with (output/'fixture/stdout.jsonl').open('ab') as stream:
        stream.write(b'\n')
    with pytest.raises(ValueError, match='stream changed'):
        verify_stage_receipt(output, receipt, run.budget)


def test_child_os_failure_keeps_structured_reason(tmp_path):
    program = make_child(tmp_path, "    raise FileNotFoundError(2, 'missing input', sys.argv[1])\n")
    output = tmp_path / 'run'
    with pytest.raises(RuntimeError, match='fixture exited'):
        with Execution(output, budget()) as run:
            run.run('fixture', program, [str(program)], kind='fixture')
    receipt, = run.receipts
    assert receipt['exit_code'] == 1 and receipt['worker_cleanup_verified'] is True
    profile = json.loads((output/'fixture/profile.json').read_bytes())
    assert profile['error'] == {'type': 'FileNotFoundError', 'errno': 2}
    assert json.loads((output/'.live/run-status.json').read_bytes())['workflow_state'] == 'RUN_FAILED'
    assert_safe(output)


def test_cancellation_during_real_child_never_persists_raw_output(tmp_path, monkeypatch):
    program = make_child(tmp_path, '    Path(sys.argv[2]).touch()\n    time.sleep(45)\n')
    ready = tmp_path / 'ready'
    output = tmp_path / 'run'
    run = Execution(output, budget())
    errors = []
    snapshot_staged = threading.Event()
    release_snapshot = threading.Event()
    replace = Path.replace

    def hold_staged_snapshot(path, target):
        if target == output/'.live/run-status.json' and ready.is_file() and not snapshot_staged.is_set():
            snapshot_staged.set()
            assert release_snapshot.wait(15)
        return replace(path, target)

    monkeypatch.setattr(Path, 'replace', hold_staged_snapshot)

    def execute():
        try:
            with run:
                run.run('fixture', program, [str(program), str(ready)], kind='fixture')
        except BaseException as error:
            errors.append(error)

    thread = threading.Thread(target=execute, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 15
        while not ready.is_file() and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(0.02)
        assert ready.is_file(), errors
        assert snapshot_staged.wait(15)
        assert_safe(output)
    finally:
        run.cancel()
        release_snapshot.set()
        thread.join(15)
    assert not thread.is_alive() and len(errors) == 1 and isinstance(errors[0], KeyboardInterrupt)
    assert run.receipts[0]['worker_cleanup_verified'] is True
    assert json.loads((output/'.live/run-status.json').read_bytes())['workflow_state'] == 'RUN_INTERRUPTED'
    assert_safe(output)


def test_expected_singular_exit_still_binds_the_specific_reason(tmp_path):
    program = make_child(tmp_path, "    raise ValueError('singular full congruence')\n")
    output = tmp_path / 'run'
    with Execution(output, budget()) as run:
        receipt = run.run('singular-fullspace-witness', program, [str(program)], kind='exact', expected_codes=(1,))
    assert verify_stage_receipt(output, receipt, run.budget)['error']['reason'] == 'singular_full_congruence'
    profile = output / 'singular-fullspace-witness/profile.json'
    data = json.loads(profile.read_bytes())
    del data['error']['reason']
    profile.write_text(json.dumps(data), encoding='utf-8')
    with pytest.raises(ValueError, match='singular witness'):
        verify_stage_receipt(output, receipt, run.budget)


def test_full_audit_cli_missing_input_retains_no_physical_paths(tmp_path):
    output = tmp_path / 'run'
    audit = tmp_path / 'audit.json'
    captured = tmp_path / 'capture'
    capture_tree(captured, tmp_path/'retained')
    with pytest.raises(RuntimeError, match='independent-audit exited 1'):
        with Execution(output, budget()) as run:
            run.run('independent-audit', captured/'computations'/BUNDLE.name/'verify-whole-source-v3.py',
                    ['--inputs', str(tmp_path/MARKER/'inputs.json'),
                     '--source', str(tmp_path/MARKER/'source.json'), '--output', str(audit)],
                    kind='audit')
    result = json.loads(audit.read_bytes())
    assert result['status'] == 'REJECT_COMPLETE_SOURCE' and result['exit_code'] == 1
    assert result['error'] == {'type': 'ValueError'}
    assert {'source', 'inputs'}.isdisjoint(result)
    assert_safe(tmp_path)
