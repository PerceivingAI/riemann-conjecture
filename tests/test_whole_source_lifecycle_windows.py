"""Tiny real Windows trees, without numerical workloads or speed assertions.

The named query interface supports cooperative descendants. It is not a hostile
same-user security sandbox; only the guardian's held handle authorizes cleanup.
"""
import ctypes
import json
import os
import queue
import subprocess
import sys
import threading
import time

import pytest

from scripts.whole_source.contract import ROOT
from scripts.whole_source.execution import MIB, neutral_helpers
from scripts.whole_source.lifecycle_windows import WindowsLifecycle, inspect_membership


pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows job objects required")
_MEMORY = 512 * MIB
_READY = "import os,sys; print(os.getpid(),flush=True); sys.stdin.readline()"


def _launch(source=_READY, *arguments):
    return subprocess.Popen([sys._base_executable, "-u", "-c", source, *arguments],
        cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8")


def _line(process):
    # A deadline bounds a broken handshake, not an assertion about execution speed.
    result = queue.Queue()
    def reading():
        result.put(process.stdout.readline())
    threading.Thread(target=reading, daemon=True).start()
    value = result.get(timeout=30)
    assert value, "child exited before its expected handshake"
    return value.strip()


def _go(process):
    process.stdin.write("GO\n")
    process.stdin.flush()


def _dispose(process):
    if process.poll() is None:
        process.kill()
    process.wait(timeout=30)
    for stream in (process.stdin, process.stdout, process.stderr):
        if stream is not None:
            stream.close()


def _zero(job):
    job.terminate()
    deadline = time.monotonic() + 30
    while True:
        sample = job.sample()
        if sample["active_process_count"] == 0 and not sample["active_process_ids"]:
            break
        assert time.monotonic() < deadline, sample
        time.sleep(0.01)
    assert sample["listed_process_count"] == 0
    return sample


def _attach(job, process, ready):
    job.attach(process)
    job.attach_ready_pid(ready)


def test_memory_only_job_exact_counters_and_named_query():
    process = _launch()
    try:
        ready = int(_line(process))
        with WindowsLifecycle(_MEMORY) as job:
            assert job.name.startswith("Local\\rh-lifecycle-")
            _attach(job, process, ready)
            sample = job.sample()
            limits = sample["installed_limits"]
            assert limits["flags"] == 0x2300
            assert limits["job_memory_limit_bytes"] == _MEMORY
            assert limits["process_memory_limit_bytes"] == _MEMORY
            assert limits["cpu_rate_flags"] == limits["cpu_rate_per_10000"] == 0
            assert limits["handle_inheritable"] is limits["breakaway_allowed"] is False
            assert {process.pid, ready} <= set(sample["active_process_ids"])
            assert sample["active_process_count"] >= 1
            assert sample["current_committed_bytes"] > 0
            assert sample["peak_committed_bytes"] >= sample["current_committed_bytes"]
            assert type(sample["cpu_user_100ns"]) is type(sample["cpu_kernel_100ns"]) is int
            assert sample["cpu_total_100ns"] == sample["cpu_user_100ns"] + sample["cpu_kernel_100ns"]
            assert sample["accounting"]["user_time"] == sample["cpu_user_100ns"]
            assert sample["accounting"]["kernel_time"] == sample["cpu_kernel_100ns"]
            assert {root["pid"] for root in sample["root_processes"]} == {process.pid, ready}
            for root in sample["root_processes"]:
                assert root["cpu_user_100ns"] is not None or root["diagnostics"]
                assert root["memory"] is not None or root["diagnostics"]
            queried = inspect_membership(job.name, ready)
            assert queried["belongs"] is True
            assert queried["installed_limits"] == limits
            assert inspect_membership(job.name)["belongs"] is False
            final = _zero(job)
            assert final["accounting"]["active_processes"] == 0
            assert final["cpu_total_100ns"] >= sample["cpu_total_100ns"]
    finally:
        _dispose(process)


def test_named_collision_never_reconfigures_or_terminates_existing_job():
    process = _launch()
    try:
        ready = int(_line(process))
        with WindowsLifecycle(_MEMORY) as job:
            _attach(job, process, ready)
            with pytest.raises(OSError, match="already exists"):
                WindowsLifecycle(_MEMORY // 2, name=job.name)
            assert job.sample()["installed_limits"]["job_memory_limit_bytes"] == _MEMORY
            assert process.poll() is None
            assert inspect_membership(job.name, ready)["belongs"] is True
            _zero(job)
    finally:
        _dispose(process)


def test_unrelated_ready_refused_and_survives_owned_termination():
    owned, unrelated = _launch(), _launch()
    try:
        ready, foreign_ready = int(_line(owned)), int(_line(unrelated))
        with WindowsLifecycle(_MEMORY) as job:
            _attach(job, owned, ready)
            with pytest.raises(OSError, match="descendant"):
                job.attach_ready_pid(foreign_ready)
            assert inspect_membership(job.name, foreign_ready)["belongs"] is False
            assert foreign_ready not in job.sample()["active_process_ids"]
            _zero(job)
            assert unrelated.poll() is None
            _go(unrelated)
            assert unrelated.wait(timeout=30) == 0
    finally:
        _dispose(owned)
        _dispose(unrelated)


def test_descendant_created_before_launcher_attachment_proves_lineage():
    source = """
import os, subprocess, sys
child = subprocess.Popen([sys.executable, '-u', '-c',
    'import os,sys; print(os.getpid(),flush=True); sys.stdin.readline()'],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
print(child.stdout.readline().strip(), flush=True)
sys.stdin.readline()
child.stdin.write('GO\\n'); child.stdin.flush()
child.wait()
"""
    process = _launch(source)
    try:
        ready = int(_line(process))
        with WindowsLifecycle(_MEMORY) as job:
            job.attach(process)
            assert inspect_membership(job.name, ready)["belongs"] is False
            job.attach_ready_pid(ready)
            assert inspect_membership(job.name, ready)["belongs"] is True
            assert ready in job.sample()["active_process_ids"]
            _zero(job)
    finally:
        _dispose(process)


def test_construction_failure_closes_new_named_job(monkeypatch):
    import uuid
    name = "Local\\rh-lifecycle-test-" + uuid.uuid4().hex
    def failing(self):
        raise OSError("installed policy verification failed")
    with monkeypatch.context() as patch:
        patch.setattr(WindowsLifecycle, "_installed_limits", failing)
        with pytest.raises(OSError, match="installed policy"):
            WindowsLifecycle(_MEMORY, name=name)
    with pytest.raises(OSError, match="OpenJobObjectW"):
        inspect_membership(name)


def test_attach_failure_closes_duplicate_and_preserves_unassigned_child(monkeypatch):
    process = _launch()
    try:
        ready = int(_line(process))
        with WindowsLifecycle(_MEMORY) as job:
            closed = []
            original = job._close_handle
            def closing(handle):
                closed.append(handle)
                original(handle)
            def failing(handle):
                raise OSError("assignment failed")
            with monkeypatch.context() as patch:
                patch.setattr(job, "_close_handle", closing)
                patch.setattr(job, "_assign", failing)
                with pytest.raises(OSError, match="assignment failed"):
                    job.attach(process)
            # Snapshot and duplicated Popen handles were both released.
            assert len(closed) == 2
            assert job.sample()["root_processes"] == []
            assert job.sample()["active_process_count"] == 0
            assert process.poll() is None
            assert inspect_membership(job.name, ready)["belongs"] is False
            _go(process)
            assert process.wait(timeout=30) == 0
    finally:
        _dispose(process)


def test_inherited_descendant_observes_outer_job_and_is_cleaned():
    source = """
import json, os, subprocess, sys
print(os.getpid(), flush=True)
sys.stdin.readline()
code = ('import json,sys; from scripts.whole_source.lifecycle_windows import inspect_membership; '
        'print(json.dumps(inspect_membership(sys.argv[1])),flush=True); sys.stdin.readline()')
child = subprocess.Popen([sys.executable, '-u', '-c', code, sys.argv[1]],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
print(child.stdout.readline().strip(), flush=True)
sys.stdin.readline()
"""
    with WindowsLifecycle(_MEMORY) as job:
        process = _launch(source, job.name)
        try:
            ready = int(_line(process))
            _attach(job, process, ready)
            _go(process)
            observed = json.loads(_line(process))
            assert observed["belongs"] is True
            descendant = observed["pid"]
            assert descendant not in {process.pid, ready}
            assert descendant in job.sample()["active_process_ids"]
            assert observed["installed_limits"]["cpu_rate_flags"] == 0
            assert observed["installed_limits"]["job_memory_limit_bytes"] == _MEMORY
            _zero(job)
        finally:
            _dispose(process)


def test_existing_numerical_job_cpu_policy_is_not_multiplied():
    helper = neutral_helpers()[1]
    process = _launch()
    try:
        ready = int(_line(process))
        with helper.WindowsJob(_MEMORY, 1) as numerical:
            numerical.attach(process)
            numerical.attach_worker_pid(ready)
            before = helper._query(numerical._kernel, numerical._handle, 15, helper._CpuRate())
            with WindowsLifecycle(_MEMORY) as outer:
                _attach(outer, process, ready)
                assert inspect_membership(outer.name, ready)["belongs"] is True
                after = helper._query(numerical._kernel, numerical._handle, 15, helper._CpuRate())
                assert (before.flags, before.rate) == (after.flags, after.rate)
                assert after.flags == 1 | 4
                assert after.rate == numerical.cpu_rate
                installed = outer.sample()["installed_limits"]
                assert installed["cpu_rate_flags"] == installed["cpu_rate_per_10000"] == 0
                _zero(outer)
    finally:
        _dispose(process)


def test_kill_on_close_releases_tree_and_close_is_idempotent():
    process = _launch()
    job = WindowsLifecycle(_MEMORY)
    try:
        ready = int(_line(process))
        _attach(job, process, ready)
        assert job.sample()["active_process_count"] >= 1
        job.close()
        job.close()
        process.wait(timeout=30)
        assert process.poll() is not None
        with pytest.raises(RuntimeError, match="closed"):
            job.sample()
    finally:
        job.close()
        _dispose(process)


@pytest.mark.parametrize("information_class", [1, 9, 15, 28])
def test_required_job_query_failure_raises(information_class, monkeypatch):
    with WindowsLifecycle(_MEMORY) as job:
        original = job._query
        def failing(kind, value):
            if kind == information_class:
                raise OSError("required job counter unavailable")
            return original(kind, value)
        monkeypatch.setattr(job, "_query", failing)
        with pytest.raises(OSError, match="required job counter"):
            job.sample()


def test_membership_failure_and_enumeration_bound_raise(monkeypatch):
    with WindowsLifecycle(_MEMORY) as job:
        def unavailable():
            raise OSError("required membership unavailable")
        monkeypatch.setattr(job, "_pids", unavailable)
        with pytest.raises(OSError, match="membership"):
            job.sample()
    from scripts.whole_source import lifecycle_windows
    with WindowsLifecycle(_MEMORY) as job:
        monkeypatch.setattr(lifecycle_windows, "_MAX_PROCESSES", 8)
        with pytest.raises(OSError, match="4096"):
            job.sample()


def test_optional_process_observations_remain_null_with_diagnostics(monkeypatch):
    process = _launch()
    try:
        ready = int(_line(process))
        with WindowsLifecycle(_MEMORY) as job:
            _attach(job, process, ready)
            def unavailable(*args):
                raise OSError("optional process observation unavailable")
            monkeypatch.setattr(job, "_times", unavailable)
            monkeypatch.setattr(job._limits, "_process_memory", unavailable)
            sample = job.sample()
            assert sample["active_process_count"] >= 1
            assert sample["diagnostics"]
            for root in sample["root_processes"]:
                assert root["cpu_user_100ns"] is root["cpu_kernel_100ns"] is root["memory"] is None
                assert len(root["diagnostics"]) == 2
            _zero(job)
    finally:
        _dispose(process)


def test_attach_requires_live_owned_popen_and_ready_requires_launcher():
    with WindowsLifecycle(_MEMORY) as job:
        with pytest.raises(TypeError, match="Popen"):
            job.attach(object())
        with pytest.raises(ValueError, match="READY"):
            job.attach_ready_pid(os.getpid())
        process = _launch()
        try:
            ready = int(_line(process))
            with pytest.raises(OSError, match="held Popen launcher"):
                job.attach_ready_pid(ready)
            _go(process)
            process.wait(timeout=30)
            with pytest.raises(OSError, match="no longer live"):
                job.attach(process)
            assert job.sample()["active_process_count"] == 0
        finally:
            _dispose(process)


@pytest.mark.parametrize("value", [0, -1, True, 1.5, 1 << (ctypes.sizeof(ctypes.c_size_t) * 8)])
def test_invalid_memory_rejected(value):
    with pytest.raises(ValueError, match="memory_bytes"):
        WindowsLifecycle(value)


def test_suspended_venv_launch_contains_redirector_and_real_interpreter():
    with WindowsLifecycle(_MEMORY) as job:
        process = job.launch([sys.executable, "-u", "-c", _READY], cwd=ROOT,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8")
        try:
            ready = int(_line(process))
            job.attach_ready_pid(ready)
            sample = job.sample()
            assert {process.pid, ready} <= set(sample["active_process_ids"])
            assert inspect_membership(job.name, ready)["belongs"]
            _zero(job)
        finally:
            _dispose(process)
