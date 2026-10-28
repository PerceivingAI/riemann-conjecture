"""Resolve native-thread limits from process affinity and visible CPU cgroups.

Single-process execution only. This policy neither detects a complete memory
budget nor claims visibility into scheduler restrictions hidden by a namespace.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from fractions import Fraction
from pathlib import Path, PurePosixPath


def _read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _unescape_mount(value: str) -> str:
    return re.sub(r"\\([0-7]{3})", lambda match: chr(int(match[1], 8)), value)


def _affinity_count(logical: int) -> tuple[int, list[str]]:
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        kernel.GetProcessAffinityMask.argtypes = [
            wintypes.HANDLE, ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_size_t)]
        kernel.GetProcessAffinityMask.restype = wintypes.BOOL
        process_mask, system_mask = ctypes.c_size_t(), ctypes.c_size_t()
        if kernel.GetProcessAffinityMask(kernel.GetCurrentProcess(),
                                         ctypes.byref(process_mask),
                                         ctypes.byref(system_mask)):
            count = int(process_mask.value).bit_count()
            if count:
                return min(logical, count), []
        return 1, ["Windows affinity unavailable; using one thread"]
    try:
        count = len(os.sched_getaffinity(0))
        if count:
            return min(logical, count), []
    except (AttributeError, OSError):
        pass
    return 1, ["Process affinity unavailable; using one thread"]


def _cgroup_limits() -> tuple[list[dict], list[str]]:
    """Read process membership and every visible ancestor of CPU mounts."""
    try:
        memberships_text = _read_text("/proc/self/cgroup")
        mounts_text = _read_text("/proc/self/mountinfo")
    except OSError as error:
        return [], ["CPU cgroup discovery unavailable: " + type(error).__name__]
    memberships: list[tuple[str, set[str], PurePosixPath]] = []
    warnings: list[str] = []
    for line in memberships_text.splitlines():
        try:
            hierarchy, controllers, name = line.split(":", 2)
            member = PurePosixPath(name)
            if not member.is_absolute() or ".." in member.parts:
                raise ValueError("unsafe membership")
            memberships.append((hierarchy, set(controllers.split(",")), member))
        except ValueError:
            warnings.append("Malformed CPU cgroup membership")
    limits: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for line in mounts_text.splitlines():
        try:
            before, after = line.split(" - ", 1)
            fields, extra = before.split(), after.split()
            kind = extra[0]
            if kind not in ("cgroup", "cgroup2"):
                continue
            controllers = set(extra[2].split(","))
            if kind == "cgroup" and "cpu" not in controllers:
                continue
            mount_root = PurePosixPath(_unescape_mount(fields[3]))
            mount_point = Path(_unescape_mount(fields[4]))
            if not mount_root.is_absolute() or not mount_point.is_absolute():
                raise ValueError("nonabsolute mount")
        except (ValueError, IndexError):
            warnings.append("Malformed CPU cgroup mount information")
            continue
        for hierarchy, member_controllers, member in memberships:
            if kind == "cgroup2" and hierarchy != "0":
                continue
            if kind == "cgroup" and "cpu" not in member_controllers:
                continue
            if member.is_relative_to(mount_root):
                relative = member.relative_to(mount_root)
            elif member == PurePosixPath("/"):
                # A cgroup namespace reports its own root, not the host path.
                relative = PurePosixPath()
            else:
                warnings.append("CPU cgroup membership is outside visible mount root")
                continue
            current = mount_point.joinpath(*relative.parts)
            while True:
                identity = (kind, str(current))
                if identity not in seen:
                    seen.add(identity)
                    quota_path = current / ("cpu.max" if kind == "cgroup2"
                                            else "cpu.cfs_quota_us")
                    try:
                        raw = _read_text(quota_path).split()
                        if kind == "cgroup2":
                            if len(raw) != 2:
                                raise ValueError("invalid cpu.max")
                            period = int(raw[1])
                            quota = None if raw[0] == "max" else int(raw[0])
                        else:
                            if len(raw) != 1:
                                raise ValueError("invalid quota")
                            quota = int(raw[0])
                            period = int(_read_text(current / "cpu.cfs_period_us").strip())
                            if quota == -1:
                                quota = None
                        if period <= 0 or quota is not None and quota <= 0:
                            raise ValueError("invalid CPU quota/period")
                        if quota is not None:
                            limits.append({"path": str(quota_path), "quota": quota,
                                           "period": period,
                                           "cpus": str(Fraction(quota, period))})
                    except FileNotFoundError:
                        # v2 files may be absent where the CPU controller is not enabled.
                        if kind == "cgroup":
                            warnings.append("CPU quota or period unavailable: " + str(current))
                    except (OSError, ValueError) as error:
                        warnings.append("CPU quota unreadable: " + str(current)
                                        + " " + type(error).__name__)
                if current == mount_point:
                    break
                current = current.parent
    return limits, warnings


def detect_cpu_resources() -> dict:
    logical = max(1, os.cpu_count() or 1)
    affinity, warnings = _affinity_count(logical)
    limits: list[dict] = []
    if sys.platform.startswith("linux"):
        limits, quota_warnings = _cgroup_limits()
        warnings.extend(quota_warnings)
    quota = min((Fraction(row["cpus"]) for row in limits), default=None)
    budget = min(logical, affinity)
    if quota is not None:
        budget = min(budget, max(1, quota.numerator // quota.denominator))
    if warnings:
        budget = 1
    return {
        "platform": sys.platform,
        "logical_cpus": logical,
        "affinity_cpus": affinity,
        "effective_cpu_budget": max(1, budget),
        "quota_cpu_limit": str(quota) if quota is not None else None,
        "quota_sources": limits,
        "warnings": warnings,
        "fractional_quota_policy": "floor above one CPU; one throttled thread below one CPU",
        "limits": "Visible affinity and Linux cgroups only; hidden ancestor, Windows job CPU rate and memory limits are not detected",
    }


def resolve_thread_budget(requested: int | None = None) -> dict:
    resources = detect_cpu_resources()
    value = requested
    source = "--threads"
    if value is None:
        override = os.environ.get("T081_THREADS")
        if override:
            try:
                value = int(override)
            except ValueError as error:
                raise ValueError("T081_THREADS must be an integer") from error
            source = "T081_THREADS"
        else:
            value = resources["effective_cpu_budget"]
            source = "detected"
    if value < 1:
        raise ValueError("thread budget must be positive")
    if value > resources["effective_cpu_budget"]:
        raise ValueError("thread budget exceeds the detected CPU allowance "
                         + str(resources["effective_cpu_budget"]))
    return {**resources, "requested_threads": requested, "threads": value,
            "selection": source}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threads", type=int)
    args = parser.parse_args()
    try:
        resources = resolve_thread_budget(args.threads)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(resources, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
