"""Real short Windows software controls. None is mathematical qualification."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time

import pytest

from scripts.whole_source import supervision as s
from scripts.whole_source.lifecycle_observations import read_receipt
from scripts.whole_source.contract import ROOT

pytestmark = pytest.mark.skipif(sys.platform != 'win32', reason='Qualified Windows lifecycle path')


@pytest.fixture
def owned():
    with tempfile.TemporaryDirectory(prefix='lifecycle-control-', dir=ROOT/'.pytest_cache') as name:
        yield Path(name)


def settings(**changes):
    value = {'format': s.POLICY, 'wall_seconds': 15, 'active_seconds': 120,
             'grace_seconds': 1, 'memory_mib': 128, 'sample_milliseconds': 100,
             'stale_milliseconds': 2000, 'observation_bytes': 16*s.MIB}
    return dict(value, **changes)


def run(owned, source, *, config=None, cancel=None):
    path = owned/'control.py'
    path.write_text(source, encoding='utf-8')
    operation = owned/'operation'
    root = owned/'operation.lifecycle'
    result = s.supervise([], observation_root=root, operation_root=operation,
                         policy_document=settings() if config is None else config,
                         script=path, cancel_event=cancel)
    assert read_receipt(root, result['invocation_id']) == result
    assert json.loads((root/'status.json').read_bytes())['event'] == 'terminal'
    return result, root


def test_caller_allocation_is_os_bounded_and_accounted(owned):
    marker = owned/'allocation.json'
    result, root = run(owned, f'''import json
from pathlib import Path
from scripts.whole_source.supervision import require_current
context=require_current()
kept=bytearray(16*1024*1024)
try:
    denied=bytearray(256*1024*1024)
except MemoryError:
    Path({str(marker)!r}).write_text(json.dumps({{"denied":True,"cap":context["memory_limit_bytes"]}}))
else:
    raise AssertionError("lifecycle memory limit did not deny allocation")
''')
    assert result['status'] == 'COMPLETED'
    assert json.loads(marker.read_bytes()) == {'denied': True, 'cap': 128*s.MIB}
    assert result['final_job']['peak_committed_bytes'] >= 16*s.MIB
    assert result['final_job']['installed_limits']['cpu_rate_flags'] == 0
    assert result['cleanup_verified'] and result['final_job']['active_process_ids'] == []


def test_explicit_cancel_cooperates_and_unrelated_process_survives(owned):
    ready, clean = owned/'ready', owned/'clean'
    cancel = threading.Event()
    def request():
        until = time.monotonic()+20
        while not ready.exists() and time.monotonic() < until:
            time.sleep(0.02)
        cancel.set()
    control = subprocess.Popen([sys._base_executable, '-B', '-c', 'import time;time.sleep(60)'])
    thread = threading.Thread(target=request, daemon=True)
    thread.start()
    try:
        result, _ = run(owned, f'''from pathlib import Path
import time
from scripts.whole_source.supervision import require_current
Path({str(ready)!r}).write_text("ready")
try:
    while True: time.sleep(.05)
except KeyboardInterrupt:
    try: require_current()
    except ValueError: Path({str(clean)!r}).write_text("cooperative cleanup")
    else: raise AssertionError("new work admitted after cancellation")
''', cancel=cancel)
        assert result['reason'] == 'explicit_cancel' and result['status'] == 'INTERRUPTED'
        assert clean.read_text() == 'cooperative cleanup'
        assert result['cleanup_verified'] and result['final_job']['active_process_count'] == 0
        assert control.poll() is None
    finally:
        control.terminate()
        control.wait(timeout=5)
        thread.join(1)


def test_deadline_escalates_stuck_caller_and_inherited_descendant(owned):
    marker = owned/'descendant.json'
    result, root = run(owned, f'''import json,subprocess,sys,time
from pathlib import Path
child=subprocess.Popen([sys._base_executable,"-B","-c","import time;time.sleep(60)"])
Path({str(marker)!r}).write_text(json.dumps({{"pid":child.pid}}))
while True:
    try: time.sleep(.05)
    except KeyboardInterrupt: pass
''', config=settings(wall_seconds=8))
    descendant = json.loads(marker.read_bytes())['pid']
    assert result['status'] == 'INTERRUPTED' and result['reason'] == 'wall_or_cumulative_deadline'
    assert result['cleanup_verified'] and result['final_job']['active_process_ids'] == []
    rows = [json.loads(raw) for raw in (root/result['observation']['path']).read_bytes().splitlines()]
    assert any(descendant in (row.get('job') or {}).get('active_process_ids', []) for row in rows)


def test_lost_required_counter_cancels_real_job(owned, monkeypatch):
    from scripts.whole_source.lifecycle_windows import WindowsLifecycle
    original = WindowsLifecycle.sample
    calls = 0
    def sample(self):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError('injected required job counter loss')
        return original(self)
    monkeypatch.setattr(WindowsLifecycle, 'sample', sample)
    result, _ = run(owned, 'import time\nwhile True: time.sleep(.05)\n')
    assert result['initial_job']['active_process_count'] > 0
    assert result['status'] == 'INTERRUPTED'
    assert result['reason'] == 'required_safety_observation_failed'
    assert result['cleanup_verified'] and result['final_job']['active_process_count'] == 0


def test_oversized_stdout_stops_without_overwriting_evidence(owned):
    result, root = run(owned, 'import os,time\nos.write(1,b"x"*(5*1024*1024))\ntime.sleep(5)\n')
    assert result['status'] == 'INTERRUPTED'
    assert (root/'stdout'/(result['invocation_id']+'.log')).stat().st_size <= result['stream_limit_bytes']
    assert result['cleanup_verified'] and result['final_job']['active_process_ids'] == []


def test_stale_application_progress_is_not_deadlock_or_failure(owned):
    result, root = run(owned, 'import time\ntime.sleep(2.6)\n', config=settings())
    rows = [json.loads(raw) for raw in (root/result['observation']['path']).read_bytes().splitlines()]
    assert any(row.get('heartbeat_stale') is True for row in rows)
    assert result['status'] == 'COMPLETED' and result['cleanup_verified'], {
        key: result[key] for key in ('reason', 'error', 'child_returncode')}


def test_prior_missing_receipt_blocks_another_invocation(owned):
    result, root = run(owned, 'value=17*19\nassert value==323\n')
    (root/'receipts'/(result['invocation_id']+'.json')).unlink()
    with pytest.raises(ValueError, match='unfinished lifecycle'):
        run(owned, 'raise AssertionError("must not launch")\n')


def test_upstream_capacity_remains_limiting_when_inner_job_has_no_cpu_rate(monkeypatch):
    from scripts.whole_source.resources import _cpu_limit
    context = {'format': s.POLICY, 'invocation_id': 'a'*32, 'operation_id': 'b'*64, 'upstream_cpus': 2}
    monkeypatch.setenv(s.ENV, json.dumps(context))
    monkeypatch.setenv(s.CPU_ENV, '2')
    assert _cpu_limit({'logical_cpus': 8, 'affinity_cpus': 8, 'effective_cpu_budget': 8,
                       'cpu_detection_complete': True}) == 2


def test_cumulative_active_allowance_refuses_another_launch(owned):
    config = settings(wall_seconds=1, active_seconds=1)
    result, root = run(owned,
        'import time\nwhile True:\n try: time.sleep(.05)\n except KeyboardInterrupt: pass\n',
        config=config)
    assert result['status'] == 'INTERRUPTED' and result['cleanup_verified']
    with pytest.raises(ValueError, match='cumulative active runtime exhausted'):
        run(owned, 'raise AssertionError(\"must not launch\")\n', config=config)
