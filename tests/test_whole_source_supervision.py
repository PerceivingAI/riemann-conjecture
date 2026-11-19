"""Real short Windows software controls. None is mathematical qualification."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time

import pytest

from scripts.whole_source import supervision as s
from scripts.whole_source.lifecycle_observations import read_authority, read_diagnostics, read_receipt
from scripts.whole_source.contract import ROOT

pytestmark = pytest.mark.skipif(sys.platform != 'win32', reason='Qualified Windows lifecycle path')


@pytest.fixture
def owned():
    (ROOT/'.pytest_cache').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='lifecycle-control-', dir=ROOT/'.pytest_cache') as name:
        yield Path(name)


def settings(**changes):
    value = {'format': s.POLICY, 'wall_seconds': 15, 'active_seconds': 120,
             'grace_seconds': 1, 'memory_mib': 128, 'sample_milliseconds': 100,
             'stale_milliseconds': 2000, 'observation_bytes': 16*s.MIB}
    return dict(value, **changes)


def run(owned, source, *, config=None, cancel=None, argv=()):
    path = owned/'control.py'
    path.write_text(source, encoding='utf-8')
    operation = owned/'operation'
    root = owned/'operation.lifecycle'
    result = s.supervise(argv, observation_root=root, operation_root=operation,
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
    diagnostic = read_diagnostics(root, result)
    assert diagnostic['stdout_bytes'] > result['stream_limit_bytes']
    assert result['error']['cause'] == 'lifecycle stdout/stderr cap exceeded'
    assert not (root/'stdout').exists()
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


def test_pipe_transport_records_safe_bytes_on_first_write(owned, monkeypatch):
    marker = 'SYNTHETIC_HOST_HOME_MARKER'
    def guarded(original):
        def publish(self, name, raw, **kwargs):
            assert marker.encode() not in raw
            assert str(owned).replace('\\', '\\\\').encode() not in raw
            return original(self, name, raw, **kwargs)
        return publish
    monkeypatch.setattr(s._Store, 'write', guarded(s._Store.write))
    monkeypatch.setattr(s._Store, 'append', guarded(s._Store.append))
    result, root = run(owned, f'''import os,time
from scripts.whole_source.supervision import event
token={marker!r}.encode()
os.write(1,b"x"*4093+token[:3])
time.sleep(.05)
os.write(1,token[3:]+b"\\nPASS_RETAINED_INVENTORY\\n")
os.write(2,token+b"\\n")
event({marker!r},state={marker!r},work={marker!r})
raise FileNotFoundError(2,{marker!r},{str(owned/'missing')!r})
''', argv=[marker*1000])
    assert result['status'] == 'INTERRUPTED'
    assert result['child_returncode'] != 0 and result['cleanup_verified']
    diagnostics = read_diagnostics(root, result)
    assert diagnostics['failure']['type'] == 'FileNotFoundError'
    assert diagnostics['failure']['errno'] == 2
    assert diagnostics['headlines'] == ['PASS_RETAINED_INVENTORY']
    assert diagnostics['stderr_bytes'] > len(marker)
    for directory in ('requests', 'stdout', 'stderr'):
        assert not (root/directory).exists()
    for path in root.rglob('*'):
        if path.is_file():
            assert marker.encode() not in path.read_bytes(), path.name


def test_interrupted_owner_is_adoptable_but_diagnostic_mutation_is_not_verified(owned):
    prior, root = run(owned, 'import os\nos._exit(19)\n')
    assert prior['status'] == 'INTERRUPTED'
    assert prior['cleanup_verified'] and prior['child_returncode'] == 19
    binding = {'role': 'lifecycle', 'invocation_id': prior['invocation_id'],
               'operation_id': prior['operation_id'], 'intent': prior['intent']}
    path = root/prior['diagnostics']['path']
    original = path.read_bytes()
    path.write_bytes(original+b' ')
    with pytest.raises(ValueError, match='diagnostics binding mismatch'):
        read_receipt(root, prior['invocation_id'])
    assert read_authority(root, prior['invocation_id']) == prior
    result, _ = run(owned, f'''from scripts.whole_source.supervision import (
    current_binding, read_phase_authority, require_current, verify_binding)
binding = {binding!r}
prior = verify_binding(binding)
assert prior['status'] == 'INTERRUPTED' and prior['child_returncode'] == 19
assert current_binding()['role'] == 'lifecycle' and 'root' not in current_binding()
receipt, ref = read_phase_authority(binding, current=require_current())
assert receipt == prior and ref['path'] == 'receipts/'+binding['invocation_id']+'.json'
legacy = {{**binding, 'root': {str(root.resolve())!r}}}
del legacy['role']
assert verify_binding(legacy) == prior
''')
    assert result['status'] == 'COMPLETED' and result['cleanup_verified']
    assert result['cumulative_active_ns'] == prior['elapsed_ns']+result['elapsed_ns']
    path.write_bytes(original)
    assert read_receipt(root, prior['invocation_id']) == prior


def test_observer_id_survives_renaming_the_owned_operation_and_observer(owned):
    script = owned/'runtime-location-control.py'
    script.write_text(
        'from scripts.whole_source.supervision import require_current, runtime_operation_roots, LEASE\n'
        'lease = require_current()\n'
        'assert lease["format"] == LEASE\n'
        'run, root = runtime_operation_roots(lease)\n'
        'assert str(run) == lease["operation_root_runtime"]\n'
        'assert str(root) == lease["code_root_runtime"]\n', encoding='utf-8')

    def launch(operation):
        return s.supervise([], observation_root=operation.with_name(operation.name+'.lifecycle'),
                           operation_root=operation, policy_document=settings(), script=script)

    first_run = owned/'SYNTHETIC_WINDOWS_PLACEMENT_A'
    first_run.mkdir()
    first_observer = first_run.with_name(first_run.name+'.lifecycle')
    before = launch(first_run)
    assert before['status'] == 'COMPLETED', before['error']
    context_bytes = (first_observer/'context.json').read_bytes()
    context = json.loads(context_bytes)
    assert context['format'] == s.CONTEXT and context['operation_id'] == before['operation_id']
    assert first_run.name.encode() not in context_bytes
    moved_run = owned/'SYNTHETIC_WINDOWS_PLACEMENT_B'
    moved_observer = moved_run.with_name(moved_run.name+'.lifecycle')
    first_run.rename(moved_run)
    first_observer.rename(moved_observer)
    after = launch(moved_run)
    assert after['status'] == 'COMPLETED', after['error']
    assert after['operation_id'] == before['operation_id']
    assert after['cumulative_active_ns'] == before['elapsed_ns']+after['elapsed_ns']
    assert (moved_observer/'context.json').read_bytes() == context_bytes
    foreign = owned/'foreign'
    copied_observer = foreign.with_name(foreign.name+'.lifecycle')
    shutil.copytree(moved_observer, copied_observer)
    with pytest.raises(ValueError, match='changed lifecycle operation/policy/code'):
        launch(foreign)


def test_abrupt_guardian_exit_leaves_no_private_request_or_resume_authority(owned):
    from scripts.whole_source.lifecycle_windows import process_identity

    marker = owned/'owned-pid'
    child = owned/'abrupt-child.py'
    child.write_text(f'''import os,time
from pathlib import Path
Path({str(marker)!r}).write_text(str(os.getpid()))
while True: time.sleep(.05)
''', encoding='utf-8')
    operation = owned/'operation'
    root = owned/'operation.lifecycle'
    script = (
        'from scripts.whole_source.supervision import supervise\n'
        f'supervise([], observation_root={str(root)!r}, operation_root={str(operation)!r}, '
        f'policy_document={settings()!r}, script={str(child)!r})'
    )
    guardian = subprocess.Popen([sys.executable, '-B', '-c', script], cwd=ROOT)
    try:
        until = time.monotonic()+10
        while not (marker.exists() and marker.stat().st_size):
            assert guardian.poll() is None
            assert time.monotonic() < until, 'owned child never passed GO'
            time.sleep(.02)
        pid = int(marker.read_text())
        identity = process_identity(pid, helper_root=ROOT)
        assert identity is not None
        guardian.kill()
        guardian.wait(timeout=5)
        until = time.monotonic()+5
        while process_identity(pid, helper_root=ROOT) == identity:
            assert time.monotonic() < until, 'owned child survived guardian death'
            time.sleep(.05)
        assert list((root/'intents').glob('*.json'))
        assert not list((root/'receipts').glob('*.json'))
        assert not (root/'requests').exists()
        with pytest.raises(ValueError, match='unfinished lifecycle'):
            run(owned, 'raise AssertionError("must not launch after unresolved ownership")\n')
    finally:
        if guardian.poll() is None:
            guardian.kill()
            guardian.wait(timeout=5)


def test_capacity_ceiling_rounds_down_before_os_installation(owned, monkeypatch):
    from scripts.whole_source import execution
    helpers = execution.neutral_helpers(ROOT)
    helper = helpers[0]
    original = helper.detect_resources
    monkeypatch.setattr(execution, 'neutral_helpers', lambda root=ROOT: helpers)
    available = 512*s.MIB-17
    def detected():
        value = original()
        if min(row['available_bytes'] for row in value['memory_sources']) < available:
            pytest.skip('live capacity is below the bounded rounding control')
        return {**value, 'available_memory_bytes': available,
                'memory_sources': [*value['memory_sources'],
                    {'source': 'declared-software-control', 'available_bytes': available}]}
    monkeypatch.setattr(helper, 'detect_resources', detected)
    result, _ = run(owned, 'from scripts.whole_source.supervision import require_current\nrequire_current()\n',
                    config=settings(memory_mib=None))
    assert result['status'] == 'COMPLETED'
    limits = result['final_job']['installed_limits']
    expected = ((available-256*s.MIB)//s.MIB)*s.MIB
    assert limits['process_memory_limit_bytes'] == limits['job_memory_limit_bytes'] == expected
    assert expected <= available-256*s.MIB
    assert result['cleanup_verified'] and result['final_job']['active_process_ids'] == []
