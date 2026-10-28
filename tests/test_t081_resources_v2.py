"""Measured resource selection and owned OS containment regressions."""
from __future__ import annotations

import importlib.util
import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path, PurePosixPath
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "computations/2026-10-28T034134Z-t081-resource-execution"
MIB = 1024 * 1024


def load(filename, name):
    spec = importlib.util.spec_from_file_location(name, BUNDLE / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


@pytest.fixture
def policy(monkeypatch):
    monkeypatch.syspath_prepend(str(BUNDLE))
    for name in ("CPUS", "WORKERS", "THREADS", "MEMORY_MIB", "RESERVE_MIB"):
        monkeypatch.delenv("T081_" + name, raising=False)
    return load("execution_resources_v2.py", "t081_resources_v2_test")


@pytest.fixture
def limits():
    return load("resource_limits_v1.py", "t081_limits_v1_test")


def linux(policy, monkeypatch, files, *, cpus=8, affinity=None, rlimit=None):
    def read(path):
        try:
            value = files[str(path)]
        except KeyError:
            raise FileNotFoundError(str(path)) from None
        if isinstance(value, BaseException):
            raise value
        return value
    monkeypatch.setattr(policy, "sys", SimpleNamespace(platform="linux"))
    monkeypatch.setattr(policy, "os", SimpleNamespace(cpu_count=lambda: cpus,
        sched_getaffinity=lambda pid: set(range(cpus if affinity is None else affinity)),
        environ={}))
    monkeypatch.setattr(policy, "Path", PurePosixPath)
    monkeypatch.setattr(policy, "_read_text", read)
    monkeypatch.setattr(policy, "_address_space_limit", lambda: rlimit)


def v2_files():
    files = {
        "/proc/self/cgroup": "0::/parent/child\n",
        "/proc/self/mountinfo": "36 25 0:32 / /sys/fs/cgroup rw - cgroup2 cgroup rw\n",
        "/proc/meminfo": "MemTotal: 16777216 kB\nMemAvailable: 8388608 kB\n",
        "/proc/self/status": "VmSize: 65536 kB\n"}
    for suffix, cpu, memory, usage in (
            ("", "max 100000", "max", "0"),
            ("/parent", "250000 100000", str(1024 * MIB), str(256 * MIB)),
            ("/parent/child", "600000 100000", str(2048 * MIB), str(128 * MIB))):
        base = "/sys/fs/cgroup" + suffix
        files[base + "/cpu.max"] = cpu
        files[base + "/memory.max"] = memory
        files[base + "/memory.current"] = usage
    return files


def test_minimum_of_affinity_ancestor_cpu_and_remaining_memory(policy, monkeypatch):
    linux(policy, monkeypatch, v2_files(), affinity=4)
    selected = policy.resolve_resources(required_bytes=128 * MIB)
    assert selected["cpu_budget"] == selected["native_threads"] == 2
    assert selected["workers"] == 1
    assert selected["available_memory_bytes"] == 768 * MIB
    assert selected["reserve_bytes"] == 768 * MIB // 10
    assert selected["memory_budget_bytes"] == 768 * MIB - selected["reserve_bytes"]
    assert selected["detection"]["quota_cpu_limit"] == "5/2"
    assert not selected["diagnostics"]
    json.dumps(selected)


@pytest.mark.parametrize("quota,expected", [("50000", 1), ("150000", 1), ("350000", 3)])
def test_fractional_cpu_policy_never_rounds_up(policy, monkeypatch, quota, expected):
    files = v2_files()
    files["/sys/fs/cgroup/parent/cpu.max"] = quota + " 100000"
    linux(policy, monkeypatch, files)
    selected = policy.resolve_resources()
    assert selected["native_threads"] == expected
    assert "throttled" in selected["detection"]["fractional_quota_policy"]


def test_affinity_can_be_tighter_than_quota(policy, monkeypatch):
    linux(policy, monkeypatch, v2_files(), affinity=1)
    assert policy.resolve_resources()["cpu_budget"] == 1
    with pytest.raises(ValueError, match="CPU allowance 1"):
        policy.resolve_resources(cpus=2)


def test_v1_uses_real_periods_and_ancestor_memory_usage(policy, monkeypatch):
    files = {"/proc/self/cgroup": "3:cpu,cpuacct,memory:/parent/child\n",
        "/proc/self/mountinfo": "36 25 0:32 / /sys/fs/cgroup/combined rw - cgroup cgroup rw,cpu,cpuacct,memory\n",
        "/proc/meminfo": "MemAvailable: 8388608 kB\n"}
    for suffix, quota, period, cap, used in (
            ("", "-1", "100000", str((1 << 63) - 4096), "0"),
            ("/parent", "200000", "200000", str(1024 * MIB), str(256 * MIB)),
            ("/parent/child", "600000", "100000", str(2048 * MIB), str(128 * MIB))):
        base = "/sys/fs/cgroup/combined" + suffix
        files[base + "/cpu.cfs_quota_us"] = quota
        files[base + "/cpu.cfs_period_us"] = period
        files[base + "/memory.limit_in_bytes"] = cap
        files[base + "/memory.usage_in_bytes"] = used
    linux(policy, monkeypatch, files)
    selected = policy.resolve_resources(reserve_mib=0)
    assert selected["cpu_budget"] == 1
    assert selected["memory_budget_bytes"] == 768 * MIB
    assert selected["detection"]["quota_cpu_limit"] == "1"
    del files["/sys/fs/cgroup/combined/parent/cpu.cfs_period_us"]
    snapshot = policy.detect_resources()
    assert snapshot["effective_cpu_budget"] == 1
    assert not snapshot["cpu_detection_complete"]
    assert any("actual period unavailable" in item for item in snapshot["cpu_diagnostics"])


@pytest.mark.parametrize("membership", ["/delegated/child", "/"])
def test_delegated_mount_and_namespace_root_include_visible_ancestor(policy, monkeypatch, membership):
    files = {"/proc/self/cgroup": "0::" + membership,
        "/proc/self/mountinfo": "36 25 0:32 /delegated /sys/fs/cgroup/a\\040b rw - cgroup2 cgroup rw",
        "/proc/meminfo": "MemAvailable: 8388608 kB\n",
        "/sys/fs/cgroup/a b/cpu.max": "200000 100000",
        "/sys/fs/cgroup/a b/memory.max": str(512 * MIB),
        "/sys/fs/cgroup/a b/memory.current": str(128 * MIB),
        "/sys/fs/cgroup/a b/child/cpu.max": "max 100000",
        "/sys/fs/cgroup/a b/child/memory.max": "max"}
    linux(policy, monkeypatch, files)
    result = policy.resolve_resources(reserve_mib=0)
    assert result["cpu_budget"] == 2
    assert result["memory_budget_bytes"] == 384 * MIB


def test_host_and_process_remaining_capacity_join_the_minimum(policy, monkeypatch):
    files = v2_files()
    files["/proc/meminfo"] = "MemAvailable: 524288 kB\n"
    linux(policy, monkeypatch, files, rlimit=384 * MIB)
    result = policy.resolve_resources(reserve_mib=0)
    assert result["memory_budget_bytes"] == 320 * MIB
    assert result["detection"]["process"]["virtual_bytes"] == 64 * MIB
    files["/proc/meminfo"] = "MemAvailable: 262144 kB\n"
    assert policy.resolve_resources(reserve_mib=0)["memory_budget_bytes"] == 256 * MIB


def test_reserve_and_explicit_cap_do_not_overcommit_known_availability(policy, monkeypatch):
    linux(policy, monkeypatch, v2_files())
    result = policy.resolve_resources(memory_mib=600, reserve_mib=100,
                                      required_bytes=600 * MIB)
    assert result["memory_budget_bytes"] == 600 * MIB
    assert result["reserve_bytes"] == 100 * MIB
    with pytest.raises(ValueError, match="after reserve"):
        policy.resolve_resources(memory_mib=669, reserve_mib=100)
    with pytest.raises(ValueError, match="reserve leaves no"):
        policy.resolve_resources(reserve_mib=768)
    with pytest.raises(ValueError, match="N and precision will not be reduced"):
        policy.resolve_resources(memory_mib=600, reserve_mib=100,
                                 required_bytes=600 * MIB + 1)


def test_cli_overrides_every_environment_setting(policy, monkeypatch):
    linux(policy, monkeypatch, v2_files())
    policy.os.environ.update(T081_CPUS="2", T081_WORKERS="2", T081_THREADS="2",
                             T081_MEMORY_MIB="700", T081_RESERVE_MIB="100")
    with pytest.raises(ValueError, match="unsupported"):
        policy.resolve_resources()
    result = policy.resolve_resources(cpus=1, workers=1, threads=1,
                                      memory_mib=400, reserve_mib=0)
    assert (result["cpu_budget"], result["workers"], result["native_threads"]) == (1, 1, 1)
    assert result["memory_budget_bytes"] == 400 * MIB
    assert result["reserve_bytes"] == 0
    assert all(value.startswith("--") for value in result["selection"].values())
    policy.os.environ["T081_WORKERS"] = "1"
    policy.os.environ["T081_MEMORY_MIB"] = "600"
    result = policy.resolve_resources()
    assert result["native_threads"] == 2
    assert result["memory_budget_bytes"] == 600 * MIB
    assert all(value.startswith("T081_") for value in result["selection"].values())


@pytest.mark.parametrize("options", [{"cpus": 0}, {"workers": 0}, {"threads": -1},
    {"memory_mib": 0}, {"reserve_mib": -1}, {"required_bytes": -1},
    {"threads": True}, {"memory_mib": 1.5}])
def test_invalid_values_are_rejected(policy, monkeypatch, options):
    linux(policy, monkeypatch, v2_files())
    with pytest.raises(ValueError, match="integer"):
        policy.resolve_resources(**options)


@pytest.mark.parametrize("name", ["CPUS", "WORKERS", "THREADS", "MEMORY_MIB", "RESERVE_MIB"])
def test_malformed_environment_requires_an_explicit_override(policy, monkeypatch, name):
    linux(policy, monkeypatch, v2_files())
    policy.os.environ["T081_" + name] = "invalid"
    with pytest.raises(ValueError, match="must be an integer"):
        policy.resolve_resources()
    key = name.lower()
    value = 128 if name == "MEMORY_MIB" else 1
    assert policy.resolve_resources(**{key: value})["workers"] == 1


def test_threads_cannot_exceed_selected_or_detected_cpu_cap(policy, monkeypatch):
    linux(policy, monkeypatch, v2_files())
    with pytest.raises(ValueError, match="selected CPU allowance 1"):
        policy.resolve_resources(cpus=1, threads=2)
    with pytest.raises(ValueError, match="detected CPU allowance 2"):
        policy.resolve_resources(cpus=3)
    with pytest.raises(ValueError, match="selected CPU allowance 2"):
        policy.resolve_resources(threads=3)


def test_malformed_cpu_detection_uses_one_thread_with_evidence(policy, monkeypatch):
    files = v2_files()
    files["/sys/fs/cgroup/parent/cpu.max"] = "not-a-quota"
    linux(policy, monkeypatch, files)
    result = policy.resolve_resources()
    assert result["native_threads"] == 1
    assert not result["detection"]["cpu_detection_complete"]
    assert any("CPU quota unreadable" in message for message in result["diagnostics"])


def test_unknown_memory_requires_explicit_manual_cap_and_reserve(policy, monkeypatch):
    linux(policy, monkeypatch, {})
    with pytest.raises(ValueError, match="explicit --memory-mib and --reserve-mib"):
        policy.resolve_resources()
    with pytest.raises(ValueError, match="explicit --memory-mib and --reserve-mib"):
        policy.resolve_resources(memory_mib=128)
    result = policy.resolve_resources(memory_mib=128, reserve_mib=0)
    assert result["available_memory_bytes"] is None
    assert result["memory_budget_bytes"] == 128 * MIB
    assert result["cpu_budget"] == 1
    assert any("acknowledge incomplete" in item for item in result["diagnostics"])


def test_unreadable_usage_preserves_known_memory_ceiling(policy, monkeypatch):
    files = v2_files()
    files["/sys/fs/cgroup/parent/memory.max"] = str(256 * MIB)
    del files["/sys/fs/cgroup/parent/memory.current"]
    linux(policy, monkeypatch, files)
    with pytest.raises(ValueError, match="incomplete"):
        policy.resolve_resources()
    with pytest.raises(ValueError, match="safe allowance"):
        policy.resolve_resources(memory_mib=257, reserve_mib=0)
    result = policy.resolve_resources(memory_mib=128, reserve_mib=0)
    assert result["available_memory_bytes"] == 256 * MIB
    assert not result["detection"]["memory_detection_complete"]


@pytest.mark.parametrize("limit,usage", [(0, 0), (100 * MIB, 100 * MIB), (100 * MIB, 101 * MIB)])
def test_exhausted_container_memory_never_becomes_manual_fallback(policy, monkeypatch, limit, usage):
    files = v2_files()
    files["/sys/fs/cgroup/parent/memory.max"] = str(limit)
    files["/sys/fs/cgroup/parent/memory.current"] = str(usage)
    linux(policy, monkeypatch, files)
    with pytest.raises(ValueError, match="reserve leaves no"):
        policy.resolve_resources(memory_mib=1, reserve_mib=0)


def test_cpu_windows_job_cap_and_memory_snapshot_minima(policy, monkeypatch):
    import resource_limits_v1
    monkeypatch.setattr(policy, "sys", SimpleNamespace(platform="win32"))
    monkeypatch.setattr(resource_limits_v1, "windows_resource_snapshot", lambda: {
        "logical_cpus": 16, "affinity_cpus": 8, "job_cpu_fraction": "3/16",
        "cpu_detection_complete": True, "memory_detection_complete": True,
        "memory_candidates": [
            {"source": "physical", "available_bytes": 8 * 1024 * MIB},
            {"source": "commit", "available_bytes": 6 * 1024 * MIB},
            {"source": "job_remaining", "available_bytes": 512 * MIB}],
        "diagnostics": [], "process": {"committed_bytes": 32 * MIB,
                                         "working_set_bytes": 20 * MIB}})
    result = policy.resolve_resources(reserve_mib=64)
    assert result["cpu_budget"] == 3
    assert result["memory_budget_bytes"] == 448 * MIB
    assert result["detection"]["windows"]["process"]["working_set_bytes"] == 20 * MIB


def test_failed_windows_detection_is_explicit_and_does_not_assume_host_ram(policy, monkeypatch):
    import resource_limits_v1
    monkeypatch.setattr(policy, "sys", SimpleNamespace(platform="win32"))
    def unavailable():
        raise OSError("resource APIs denied")
    monkeypatch.setattr(resource_limits_v1, "windows_resource_snapshot", unavailable)
    with pytest.raises(ValueError, match="incomplete"):
        policy.resolve_resources()
    result = policy.resolve_resources(memory_mib=128, reserve_mib=0)
    assert result["cpu_budget"] == 1
    assert result["available_memory_bytes"] is None
    assert any("resource APIs denied" in item for item in result["diagnostics"])


def line_with_timeout(process, timeout=15):
    result = queue.Queue()
    threading.Thread(target=lambda: result.put(process.stdout.readline()), daemon=True).start()
    try:
        return result.get(timeout=timeout).strip()
    except queue.Empty:
        raise AssertionError("contained child did not report within timeout") from None


def attach_ready_worker(job, process):
    """Contain both a venv launcher and its actual waiting interpreter."""
    job.attach(process)
    ready = line_with_timeout(process)
    assert ready.startswith("READY ")
    job.attach_worker_pid(int(ready.split()[1]))


@pytest.mark.skipif(sys.platform != "win32", reason="actual Windows job semantics")
def test_owned_windows_job_denies_excess_commit_and_accounts_only_child(limits):
    code = """
import sys,os
print('READY',os.getpid(),flush=True)
sys.stdin.readline()
blocks = []
try:
    for _ in range(32):
        blocks.append(bytearray(8 * 1024 * 1024))
except MemoryError:
    print('DENIED', flush=True)
else:
    print('UNCONTAINED', flush=True)
sys.stdin.readline()
"""
    job = limits.WindowsJob(96 * MIB, 1)
    process = subprocess.Popen([sys.executable, "-B", "-c", code], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    attached = False
    try:
        attach_ready_worker(job, process)
        attached = True
        process.stdin.write("GO\n")
        process.stdin.flush()
        assert line_with_timeout(process) == "DENIED"
        usage = job.usage()
        assert process.pid in usage["active_process_ids"]
        assert os.getpid() not in usage["active_process_ids"]
        assert usage["active_process_count"] == len(usage["active_process_ids"])
        assert usage["cpu_seconds"] is not None and usage["cpu_seconds"] >= 0
        if usage["current_committed_bytes"] is not None:
            assert 0 < usage["current_committed_bytes"] <= 96 * MIB
            assert usage["current_committed_bytes"] <= usage["peak_committed_bytes"]
    finally:
        job.close()
        if not attached and process.poll() is None:
            process.kill()
        process.wait(timeout=15)
        for stream in (process.stdin, process.stdout, process.stderr):
            stream.close()


@pytest.mark.skipif(sys.platform != "win32", reason="actual Windows aggregate commit cap")
def test_owned_windows_memory_cap_is_shared_with_descendant(limits):
    descendant = """
import time
try:
    block = bytearray(64 * 1024 * 1024)
except MemoryError:
    print('DENIED', flush=True)
else:
    print('UNCONTAINED', flush=True)
time.sleep(60)
"""
    code = ("import subprocess,sys,time,os\nprint('READY',os.getpid(),flush=True)\nsys.stdin.readline()\n"
            "block=bytearray(48*1024*1024)\n"
            "p=subprocess.Popen([sys.executable,'-B','-S','-c'," + repr(descendant) + "])\n"
            "print(p.pid,flush=True)\ntime.sleep(60)\n")
    job = limits.WindowsJob(96 * MIB, 1)
    process = subprocess.Popen([sys.executable, "-B", "-S", "-c", code],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    try:
        attach_ready_worker(job, process)
        process.stdin.write("GO\n")
        process.stdin.flush()
        lines = [line_with_timeout(process), line_with_timeout(process)]
        assert "DENIED" in lines
        child_pid = int(next(line for line in lines if line.isdigit()))
        usage = job.usage()
        assert {process.pid, child_pid} <= set(usage["active_process_ids"])
        assert os.getpid() not in usage["active_process_ids"]
        # Windows can count a denied request in its historical peak before rollback.
        # DENIED proves the aggregate limit rejected an allocation that fits the
        # per-process limit. Do not mistake attempted demand for retained commit.
        if usage["current_committed_bytes"] is not None:
            assert usage["current_committed_bytes"] <= 96 * MIB
    finally:
        job.close()
        if process.poll() is None:
            process.kill()
        process.wait(timeout=15)
        process.stdin.close()
        process.stdout.close()


@pytest.mark.skipif(sys.platform != "win32", reason="actual Windows attachment failure")
def test_windows_attachment_failure_raises_instead_of_running_uncontained(limits):
    with limits.WindowsJob(96 * MIB, 1) as job:
        process = subprocess.Popen([sys.executable, "-B", "-S", "-c", "pass"])
        process.wait(timeout=15)
        with pytest.raises(OSError, match="AssignProcessToJobObject"):
            job.attach(process)
        assert job.usage()["active_process_count"] == 0


@pytest.mark.parametrize("memory,cpu", [(0, 1), (MIB, 0), (-1, 1), (MIB, True)])
def test_containment_rejects_invalid_budgets_before_os_calls(limits, memory, cpu):
    with pytest.raises(ValueError, match="positive integer"):
        limits.WindowsJob(memory, cpu)


@pytest.mark.skipif(sys.platform != "win32", reason="actual Windows descendant ownership")
@pytest.mark.parametrize("operation", ["close", "terminate"])
def test_owned_windows_job_reaps_descendants_without_touching_unrelated_process(limits, operation):
    descendant = "import time; time.sleep(60)"
    code = ("import subprocess,sys,time,os\nprint('READY',os.getpid(),flush=True)\nsys.stdin.readline()\n"
            "p=subprocess.Popen([sys.executable,'-B','-c'," + repr(descendant) + "])\n"
            "print(p.pid,flush=True)\ntime.sleep(60)\n")
    job = limits.WindowsJob(192 * MIB, 1)
    unrelated = subprocess.Popen([sys.executable, "-B", "-c", descendant])
    process = subprocess.Popen([sys.executable, "-B", "-c", code], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, text=True)
    child_handle = None
    try:
        attach_ready_worker(job, process)
        process.stdin.write("GO\n")
        process.stdin.flush()
        child_pid = int(line_with_timeout(process))
        kernel = job._kernel
        kernel.WaitForSingleObject.argtypes = [limits.wintypes.HANDLE, limits._DWORD]
        kernel.WaitForSingleObject.restype = limits._DWORD
        child_handle = kernel.OpenProcess(0x00100000, False, child_pid)
        assert child_handle
        usage = job.usage()
        assert {process.pid, child_pid} <= set(usage["active_process_ids"])
        assert os.getpid() not in usage["active_process_ids"]
        assert unrelated.pid not in usage["active_process_ids"]
        assert usage["active_process_count"] == len(usage["active_process_ids"])
        getattr(job, operation)()
        process.wait(timeout=15)
        assert kernel.WaitForSingleObject(child_handle, 15000) == 0
        assert unrelated.poll() is None
    finally:
        job.close()
        if process.poll() is None:
            process.kill()
        process.wait(timeout=15)
        if child_handle:
            kernel.CloseHandle(child_handle)
        unrelated.kill()
        unrelated.wait(timeout=15)
        process.stdin.close()
        process.stdout.close()


@pytest.mark.skipif(os.name != "posix", reason="actual POSIX virtual-address-space limit")
def test_posix_memory_limit_rejects_large_allocation_in_isolated_process():
    code = """
import sys
sys.path.insert(0, sys.argv[1])
from resource_limits_v1 import apply_posix_memory_limit
value = apply_posix_memory_limit(128 * 1024 * 1024)
assert not value['aggregate_rss_enforced']
try:
    apply_posix_memory_limit(129 * 1024 * 1024)
except ValueError:
    pass
else:
    raise AssertionError('inherited address-space limit was increased')
try:
    bytearray(256 * 1024 * 1024)
except MemoryError:
    print('DENIED', flush=True)
else:
    raise AssertionError('uncontained allocation')
"""
    result = subprocess.run([sys.executable, "-B", "-c", code, str(BUNDLE)],
                            text=True, capture_output=True, timeout=15)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "DENIED"
