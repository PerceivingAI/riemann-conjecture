"""Measured single-process/native-thread policy for fixed T081 workloads.

CPU fractions are floored above one CPU; below one CPU the one native thread
is throttled by the existing OS quota. Workers other than one are unsupported.
Memory is a fresh-stage byte allowance, not a change to N or precision. Automatic
headroom is max(64 MiB, 10% of measured available bytes). Explicit memory caps
must fit after that reserve. Snapshots are not reservations against other jobs.

Only visible Linux cgroup ancestors and the immediate Windows job are readable.
Hidden namespace/job ancestors remain a visibility limitation. Incomplete memory
queries require both a manual memory cap and an explicit reserve, including zero
if intended. Known measured caps still cannot be exceeded.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from fractions import Fraction
from pathlib import Path, PurePosixPath

MIB = 1024 * 1024


def _read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _unescape_mount(value: str) -> str:
    return re.sub(r"\\([0-7]{3})", lambda match: chr(int(match[1], 8)), value)


def _visible_cgroups():
    """Map memberships through mount roots, then visit every visible ancestor."""
    diagnostics = []
    try:
        memberships_text = _read_text("/proc/self/cgroup")
        mounts_text = _read_text("/proc/self/mountinfo")
    except OSError as error:
        return [], ["cgroup discovery unavailable: " + type(error).__name__]
    memberships = []
    for line in memberships_text.splitlines():
        try:
            hierarchy, controllers, name = line.split(":", 2)
            member = PurePosixPath(name)
            if not hierarchy.isdigit() or not member.is_absolute() or ".." in member.parts:
                raise ValueError("unsafe membership")
            memberships.append((hierarchy, set(controllers.split(",")), member))
        except ValueError:
            diagnostics.append("Malformed cgroup membership")
    entries = []
    seen = set()
    for line in mounts_text.splitlines():
        try:
            before, after = line.split(" - ", 1)
            fields, extra = before.split(), after.split()
            kind = extra[0]
            if kind not in ("cgroup", "cgroup2"):
                continue
            controllers = set(extra[2].split(","))
            if kind == "cgroup" and not controllers.intersection({"cpu", "memory"}):
                continue
            root = PurePosixPath(_unescape_mount(fields[3]))
            mount = Path(_unescape_mount(fields[4]))
            if not root.is_absolute() or not mount.is_absolute() or ".." in root.parts or ".." in mount.parts:
                raise ValueError("unsafe mount")
        except (ValueError, IndexError):
            diagnostics.append("Malformed cgroup mount information")
            continue
        for hierarchy, member_controllers, member in memberships:
            active = {"cpu", "memory"} if kind == "cgroup2" else controllers.intersection(member_controllers)
            if kind == "cgroup2" and hierarchy != "0":
                continue
            if kind == "cgroup" and not active.intersection({"cpu", "memory"}):
                continue
            if member.is_relative_to(root):
                relative = member.relative_to(root)
            elif member == PurePosixPath("/"):
                relative = PurePosixPath()
            else:
                diagnostics.append("cgroup membership is outside visible mount root")
                continue
            current = mount.joinpath(*relative.parts)
            while True:
                identity = (kind, str(current), tuple(sorted(active)))
                if identity not in seen:
                    seen.add(identity)
                    entries.append((kind, current, active))
                if current == mount:
                    break
                current = current.parent
    return entries, diagnostics


def _integer_file(path):
    words = _read_text(path).split()
    if len(words) != 1 or not re.fullmatch(r"-?[0-9]+", words[0]):
        raise ValueError("invalid integer file")
    return int(words[0])


def _cgroup_constraints():
    entries, discovery = _visible_cgroups()
    cpu_sources, memory_sources = [], []
    cpu_diagnostics, memory_diagnostics = list(discovery), list(discovery)
    for kind, current, controllers in entries:
        if "cpu" in controllers:
            quota_path = current / ("cpu.max" if kind == "cgroup2" else "cpu.cfs_quota_us")
            try:
                if kind == "cgroup2":
                    words = _read_text(quota_path).split()
                    if (len(words) != 2 or not re.fullmatch(r"[0-9]+", words[1])
                            or words[0] != "max" and not re.fullmatch(r"[0-9]+", words[0])):
                        raise ValueError("invalid cpu.max")
                    quota = None if words[0] == "max" else int(words[0])
                    period = int(words[1])
                else:
                    quota = _integer_file(quota_path)
                    period = _integer_file(current / "cpu.cfs_period_us")
                    if quota == -1:
                        quota = None
                if period <= 0 or quota is not None and quota <= 0:
                    raise ValueError("invalid CPU quota/period")
                if quota is not None:
                    cpu_sources.append({"path": str(quota_path), "quota": quota,
                        "period": period, "cpus": str(Fraction(quota, period))})
            except FileNotFoundError:
                if kind == "cgroup":
                    cpu_diagnostics.append("CPU quota or actual period unavailable: " + str(current))
            except (OSError, ValueError) as error:
                cpu_diagnostics.append("CPU quota unreadable: " + str(current) + " " + type(error).__name__)
        if "memory" in controllers:
            limit_path = current / ("memory.max" if kind == "cgroup2" else "memory.limit_in_bytes")
            usage_path = current / ("memory.current" if kind == "cgroup2" else "memory.usage_in_bytes")
            try:
                raw = _read_text(limit_path).strip()
                if kind == "cgroup2" and raw == "max":
                    continue
                if not re.fullmatch(r"[0-9]+", raw):
                    raise ValueError("invalid memory limit")
                limit = int(raw)
                # Linux v1 uses a page-rounded LONG_MAX sentinel for unlimited.
                if kind == "cgroup" and limit >= (1 << 60):
                    continue
                candidate = {"source": str(limit_path), "limit_bytes": limit,
                             "usage_bytes": None, "available_bytes": limit}
                memory_sources.append(candidate)
                usage = _integer_file(usage_path)
                if usage < 0:
                    raise ValueError("negative memory usage")
                candidate.update(usage_bytes=usage, available_bytes=max(0, limit - usage))
            except FileNotFoundError:
                # An absent v2 controller is normal, but a limit without its
                # current usage is not evidence of any available capacity.
                if kind == "cgroup2":
                    try:
                        _read_text(limit_path)
                    except FileNotFoundError:
                        continue
                    except OSError:
                        pass
                memory_diagnostics.append("Memory limit/current usage unavailable: " + str(current))
            except (OSError, ValueError) as error:
                memory_diagnostics.append("Memory cgroup unreadable: " + str(current) + " " + type(error).__name__)
    return cpu_sources, memory_sources, cpu_diagnostics, memory_diagnostics


def _affinity_count(logical):
    try:
        count = len(os.sched_getaffinity(0))
        if count:
            return min(logical, count), []
    except (AttributeError, OSError):
        pass
    return 1, ["Process affinity unavailable; using one native thread"]


def _address_space_limit():
    import resource
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    values = [value for value in (soft, hard) if value != resource.RLIM_INFINITY]
    return min(values) if values else None


def _linux_memory():
    candidates, diagnostics = [], []
    process = {}
    try:
        text = _read_text("/proc/meminfo")
        match = re.search(r"^MemAvailable:\s+([0-9]+)\s+kB\s*$", text, re.MULTILINE)
        if match is None:
            raise ValueError("MemAvailable is missing or malformed")
        candidates.append({"source": "/proc/meminfo:MemAvailable",
                           "available_bytes": int(match[1]) * 1024})
    except (OSError, ValueError) as error:
        diagnostics.append("Host available memory unknown: " + str(error))
    try:
        cap = _address_space_limit()
        process["rlimit_as_bytes"] = cap
        if cap is not None:
            if cap < 0:
                raise ValueError("negative RLIMIT_AS")
            candidate = {"source": "RLIMIT_AS limit only", "limit_bytes": cap,
                         "usage_bytes": None, "available_bytes": cap}
            candidates.append(candidate)
            text = _read_text("/proc/self/status")
            match = re.search(r"^VmSize:\s+([0-9]+)\s+kB\s*$", text, re.MULTILINE)
            if match is None:
                raise ValueError("VmSize is missing or malformed")
            used = int(match[1]) * 1024
            process["virtual_bytes"] = used
            candidate.update(source="RLIMIT_AS remaining", usage_bytes=used,
                             available_bytes=max(0, cap - used))
    except (ImportError, AttributeError, OSError, ValueError) as error:
        diagnostics.append("Process address-space allowance unknown: " + str(error))
    return candidates, process, diagnostics


def detect_resources() -> dict:
    """Return JSON-safe evidence and the minimum of measured constraints."""
    logical = max(1, os.cpu_count() or 1)
    cpu_diagnostics, memory_diagnostics = [], []
    cpu_sources, memory_sources = [], []
    platform_metadata = {}
    if sys.platform == "win32":
        from resource_limits_v1 import windows_resource_snapshot
        try:
            windows = windows_resource_snapshot()
        except (OSError, AttributeError) as error:
            windows = {"logical_cpus": logical, "affinity_cpus": 1,
                "job_cpu_fraction": None, "cpu_detection_complete": False,
                "memory_detection_complete": False, "memory_candidates": [],
                "diagnostics": ["Windows resource discovery unavailable: " + str(error)]}
        logical = windows["logical_cpus"]
        affinity = windows["affinity_cpus"]
        if windows["job_cpu_fraction"] is not None:
            quota = Fraction(windows["job_cpu_fraction"]) * logical
            cpu_sources.append({"source": "windows.immediate_job_cpu_rate",
                                "cpus": str(quota)})
        memory_sources = windows["memory_candidates"]
        if not windows["cpu_detection_complete"]:
            cpu_diagnostics.extend(windows["diagnostics"])
        if not windows["memory_detection_complete"]:
            memory_diagnostics.extend(windows["diagnostics"])
        memory_complete = windows["memory_detection_complete"]
        platform_metadata["windows"] = windows
    elif sys.platform.startswith("linux"):
        affinity, cpu_diagnostics = _affinity_count(logical)
        cgroup_cpu, cgroup_memory, cpu_warnings, memory_warnings = _cgroup_constraints()
        cpu_sources.extend(cgroup_cpu)
        cpu_diagnostics.extend(cpu_warnings)
        memory_sources, process, host_warnings = _linux_memory()
        memory_sources.extend(cgroup_memory)
        memory_diagnostics.extend(host_warnings)
        memory_diagnostics.extend(memory_warnings)
        memory_complete = not memory_diagnostics
        platform_metadata["process"] = process
    else:
        affinity, cpu_diagnostics = _affinity_count(logical)
        memory_diagnostics.append("Automatic memory discovery is unsupported on " + sys.platform)
        memory_complete = False
    quota = min((Fraction(row["cpus"]) for row in cpu_sources), default=None)
    effective_cpu = min(logical, affinity)
    if quota is not None:
        effective_cpu = min(effective_cpu, max(1, quota.numerator // quota.denominator))
    if cpu_diagnostics:
        effective_cpu = 1
    available = min((row["available_bytes"] for row in memory_sources), default=None)
    return {"platform": sys.platform, "logical_cpus": logical,
            "affinity_cpus": affinity, "effective_cpu_budget": max(1, effective_cpu),
            "quota_cpu_limit": str(quota) if quota is not None else None,
            "cpu_sources": cpu_sources, "memory_sources": memory_sources,
            "available_memory_bytes": available,
            "cpu_detection_complete": not cpu_diagnostics,
            "memory_detection_complete": memory_complete,
            "cpu_diagnostics": cpu_diagnostics, "memory_diagnostics": memory_diagnostics,
            "diagnostics": list(dict.fromkeys(cpu_diagnostics + memory_diagnostics)),
            "fractional_quota_policy": "floor above one CPU; one throttled native thread below one CPU",
            "visibility": "Linux visible cgroup ancestors only; Windows immediate job only; snapshots are not memory reservations",
            **platform_metadata}


def detect_cpu_resources() -> dict:
    """Expose the same snapshot used by resolution, without choosing overrides."""
    return detect_resources()


def _option(name, value, *, zero=False):
    environment = "T081_" + name.upper()
    selection = "--" + name.replace("_", "-")
    if value is None:
        raw = os.environ.get(environment)
        if raw is None:
            return None, "detected"
        try:
            value = int(raw)
        except (ValueError, TypeError) as error:
            raise ValueError(environment + " must be an integer") from error
        selection = environment
    if type(value) is not int or value < (0 if zero else 1):
        raise ValueError(selection + " must be a " + ("nonnegative" if zero else "positive") + " integer")
    return value, selection


def resolve_resources(*, cpus=None, workers=None, threads=None, memory_mib=None,
                      reserve_mib=None, required_bytes=0) -> dict:
    """Resolve CLI-over-environment limits; reject before any workload allocation.

    memory_budget_bytes is the entire stage commitment/virtual-space allowance.
    required_bytes must include the caller's declared fixed-workload overhead.
    A manual cap under incomplete detection acknowledges unknown OS restrictions;
    it never waives a measured upper bound and does not promise OS reservation.
    """
    cpus, cpu_source = _option("cpus", cpus)
    workers, worker_source = _option("workers", workers)
    threads, thread_source = _option("threads", threads)
    memory_mib, memory_source = _option("memory_mib", memory_mib)
    reserve_mib, reserve_source = _option("reserve_mib", reserve_mib, zero=True)
    if type(required_bytes) is not int or required_bytes < 0:
        raise ValueError("required_bytes must be a nonnegative integer")
    if workers is not None and workers != 1:
        raise ValueError("workers > 1 are unsupported; this workload uses one process with native threads")
    detected = detect_resources()
    effective_cpu = detected["effective_cpu_budget"]
    cpu_budget = cpus if cpus is not None else effective_cpu
    if cpu_budget > effective_cpu:
        raise ValueError("CPU budget exceeds the detected CPU allowance " + str(effective_cpu))
    native_threads = threads if threads is not None else cpu_budget
    if native_threads > cpu_budget:
        raise ValueError("native thread budget exceeds the selected CPU allowance " + str(cpu_budget))
    available = detected["available_memory_bytes"]
    diagnostics = list(detected["diagnostics"])
    if not detected["memory_detection_complete"]:
        if memory_mib is None or reserve_mib is None:
            raise ValueError("memory detection is incomplete; explicit --memory-mib and --reserve-mib are required: "
                             + "; ".join(detected["memory_diagnostics"]))
        diagnostics.append("Manual memory/reserve limits acknowledge incomplete detection; unknown limits may still reject allocations")
    if available is None:
        if memory_mib is None:
            raise ValueError("available memory is unknown; provide --memory-mib and --reserve-mib")
        reserve = reserve_mib * MIB
        safe = None
    else:
        reserve = reserve_mib * MIB if reserve_mib is not None else max(64 * MIB, available // 10)
        if reserve >= available:
            raise ValueError("memory reserve leaves no measured stage allowance")
        safe = available - reserve
    budget = memory_mib * MIB if memory_mib is not None else safe
    if safe is not None and budget > safe:
        raise ValueError("memory budget exceeds detected safe allowance after reserve: " + str(safe) + " bytes")
    if budget is None or budget <= 0:
        raise ValueError("memory budget must be positive")
    if required_bytes > budget:
        raise ValueError("fixed workload requires " + str(required_bytes)
                         + " bytes, exceeding memory budget " + str(budget)
                         + "; N and precision will not be reduced")
    return {"cpu_budget": cpu_budget, "workers": 1, "native_threads": native_threads,
            "memory_budget_bytes": budget, "reserve_bytes": reserve,
            "available_memory_bytes": available, "required_bytes": required_bytes,
            "diagnostics": diagnostics, "detection": detected,
            "selection": {"cpus": cpu_source, "workers": worker_source,
                "threads": thread_source, "memory_mib": memory_source,
                "reserve_mib": reserve_source},
            "execution_mode": "single-process/native-threads"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cpus", "workers", "threads", "memory-mib", "reserve-mib"):
        parser.add_argument("--" + name, type=int)
    parser.add_argument("--required-bytes", type=int, default=0)
    arguments = parser.parse_args()
    try:
        result = resolve_resources(**vars(arguments))
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
