"""Resource-limit and retained-payload rejection regressions for new tools."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "computations/2026-10-28T024305Z-t081-execution-corrections"
OLD = ROOT / "computations/2026-10-27T140745Z-t081-complete-gram-attempt"


def module(filename, name):
    spec = importlib.util.spec_from_file_location(name, BUNDLE / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


@pytest.fixture
def policy():
    return module("execution_resources_v1.py", "t081_policy_test")


def linux(policy, monkeypatch, files, *, cpus=8):
    def read(path):
        try:
            return files[str(path)]
        except KeyError:
            raise FileNotFoundError(str(path)) from None
    monkeypatch.setattr(policy, "sys", SimpleNamespace(platform="linux"))
    monkeypatch.setattr(policy, "os", SimpleNamespace(cpu_count=lambda: cpus,
        sched_getaffinity=lambda pid: set(range(cpus)), environ={}))
    monkeypatch.setattr(policy, "Path", PurePosixPath)
    monkeypatch.setattr(policy, "_read_text", read)


def v2_files():
    return {"/proc/self/cgroup": "0::/parent/child\n",
        "/proc/self/mountinfo": "36 25 0:32 / /sys/fs/cgroup rw - cgroup2 cgroup rw\n",
        "/sys/fs/cgroup/cpu.max": "max 100000",
        "/sys/fs/cgroup/parent/cpu.max": "100000 100000",
        "/sys/fs/cgroup/parent/child/cpu.max": "600000 100000"}


def test_nested_v2_ancestor_limit_beats_child_and_root(policy, monkeypatch):
    linux(policy, monkeypatch, v2_files())
    result = policy.detect_cpu_resources()
    assert result["effective_cpu_budget"] == 1
    assert result["quota_cpu_limit"] == "1"
    assert not result["warnings"]


def test_v1_reads_real_period_and_parent_limit(policy, monkeypatch):
    files = {"/proc/self/cgroup": "3:cpu,cpuacct:/parent/child\n",
        "/proc/self/mountinfo": "36 25 0:32 / /sys/fs/cgroup/cpu rw - cgroup cgroup rw,cpu,cpuacct\n"}
    for suffix, quota, period in (("", "-1", "100000"),
                                  ("/parent", "200000", "200000"),
                                  ("/parent/child", "400000", "100000")):
        base = "/sys/fs/cgroup/cpu" + suffix
        files[base + "/cpu.cfs_quota_us"] = quota
        files[base + "/cpu.cfs_period_us"] = period
    linux(policy, monkeypatch, files)
    result = policy.detect_cpu_resources()
    assert result["effective_cpu_budget"] == 1
    assert result["quota_cpu_limit"] == "1"
    assert not result["warnings"]


@pytest.mark.parametrize("membership", ["/delegated/child", "/"])
def test_mount_root_and_namespace_root_mapping(policy, monkeypatch, membership):
    files = {"/proc/self/cgroup": "0::" + membership,
        "/proc/self/mountinfo": "36 25 0:32 /delegated /sys/fs/cgroup rw - cgroup2 cgroup rw",
        "/sys/fs/cgroup/cpu.max": "200000 100000",
        "/sys/fs/cgroup/child/cpu.max": "max 100000"}
    linux(policy, monkeypatch, files)
    assert policy.detect_cpu_resources()["effective_cpu_budget"] == 2


@pytest.mark.parametrize("quota,expected", [("50000", 1), ("150000", 1), ("250000", 2)])
def test_fractional_cpu_quota_is_conservative_and_explained(policy, monkeypatch, quota, expected):
    files = v2_files()
    files["/sys/fs/cgroup/parent/cpu.max"] = quota + " 100000"
    linux(policy, monkeypatch, files)
    result = policy.detect_cpu_resources()
    assert result["effective_cpu_budget"] == expected
    assert "throttled" in result["fractional_quota_policy"]


def test_bad_or_unreadable_quota_falls_back_instead_of_using_all_cpus(policy, monkeypatch):
    files = v2_files()
    files["/sys/fs/cgroup/parent/cpu.max"] = "not-a-quota"
    linux(policy, monkeypatch, files)
    result = policy.detect_cpu_resources()
    assert result["effective_cpu_budget"] == 1
    assert "unreadable" in result["warnings"][0]


def test_override_precedence_and_rejection_obey_effective_budget(policy, monkeypatch):
    linux(policy, monkeypatch, v2_files())
    policy.os.environ["T081_THREADS"] = "2"
    with pytest.raises(ValueError, match="exceeds"):
        policy.resolve_thread_budget()
    assert policy.resolve_thread_budget(1)["threads"] == 1
    with pytest.raises(ValueError, match="positive"):
        policy.resolve_thread_budget(0)
    policy.os.environ["T081_THREADS"] = "invalid"
    with pytest.raises(ValueError, match="integer"):
        policy.resolve_thread_budget()


def test_actual_process_affinity_restricts_cli_budget():
    code = r'''
import ctypes, os, runpy, sys
if sys.platform == 'win32':
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.GetCurrentProcess.restype=ctypes.c_void_p
    k.GetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
    k.SetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
    h=k.GetCurrentProcess();m=ctypes.c_size_t();s=ctypes.c_size_t()
    assert k.GetProcessAffinityMask(h,ctypes.byref(m),ctypes.byref(s))
    assert k.SetProcessAffinityMask(h,m.value & -m.value)
else:
    os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
path=sys.argv[1];sys.argv=[path,'--threads','2'];runpy.run_path(path,run_name='__main__')
'''
    if sys.platform != "win32" and not hasattr(os, "sched_setaffinity"):
        pytest.skip("OS has no process-affinity interface")
    result = subprocess.run([sys.executable, "-B", "-c", code,
        str(BUNDLE / "execution_resources_v1.py")], capture_output=True, text=True)
    assert result.returncode == 2
    assert "CPU allowance 1" in result.stderr


def test_producer_rejects_invalid_budget_before_reading_inputs(tmp_path):
    output = tmp_path / "never-created.json"
    result = subprocess.run([sys.executable, "-B", str(BUNDLE / "build-whole-source-v3.py"),
        "--threads", "0", "--inputs", str(tmp_path / "missing-input.json"),
        "--output", str(output)], capture_output=True, text=True)
    assert result.returncode != 0
    assert "thread budget must be positive" in result.stderr
    assert "FileNotFoundError" not in result.stderr
    assert not output.exists()


@pytest.fixture
def publication(tmp_path):
    metadata = json.loads((OLD / "data/source-v1.json").read_text(encoding="utf-8"))
    producer = BUNDLE / "build-whole-source-v3.py"
    metadata["producer_sha256"] = hashlib.sha256(producer.read_bytes()).hexdigest()
    for descriptor in metadata["matrices"].values():
        target = tmp_path / descriptor["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(OLD / "data" / descriptor["path"], target)
    path = tmp_path / "source.json"
    path.write_text(json.dumps(metadata), encoding="utf-8")
    return path, metadata, producer


@pytest.mark.parametrize("mutation", ["precision", "descriptor-hash", "descriptor-size",
                                     "missing-matrix", "extra-metadata", "producer", "packet"])
def test_comparer_rejects_changed_packets_or_metadata(publication, tmp_path, mutation):
    source, data, producer = publication
    if mutation == "precision":
        data["precision"] = 1
    elif mutation == "descriptor-hash":
        data["matrices"]["A_model-0"]["sha256"] = "0" * 64
    elif mutation == "descriptor-size":
        data["matrices"]["A_model-0"]["size"] += 1
    elif mutation == "missing-matrix":
        del data["matrices"]["A_model-1"]
    elif mutation == "extra-metadata":
        data["unexpected"] = True
    elif mutation == "producer":
        data["producer_sha256"] = "0" * 64
    else:
        (source.parent / data["matrices"]["A_model-0"]["path"]).write_bytes(b"different")
    source.write_text(json.dumps(data), encoding="utf-8")
    output = tmp_path / "comparison.json"
    result = subprocess.run([sys.executable, "-B", str(BUNDLE / "compare-v2-v1.py"),
        "--source", str(source), "--producer", str(producer), "--output", str(output)],
        capture_output=True, text=True)
    assert result.returncode == 1
    assert "FAIL_SOURCE_IDENTITY" in result.stderr
    assert not output.exists()
