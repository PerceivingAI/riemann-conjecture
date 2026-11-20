"""Owned stage containment, with no handles to unrelated jobs.

WindowsJob must be attached to a child blocked on its GO pipe before arithmetic.
Its aggregate private-commit limit includes descendants, denies excess commits,
and kills the owned process tree on close. CPU rates in nested jobs are relative
to the parent job, so the requested hard rate can be stricter than requested.

POSIX RLIMIT_AS limits each process's virtual address space, not aggregate RSS.
It is inherited by descendants but is not a cgroup. The supervisor must own the
process group and monitor aggregate RSS separately.
"""
from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from ctypes import wintypes
from fractions import Fraction

_SIZE = ctypes.c_size_t
_U64 = ctypes.c_uint64
_DWORD = ctypes.c_uint32


class _MemoryStatus(ctypes.Structure):
    _fields_ = [("length", _DWORD), ("load", _DWORD),
                ("total_physical", _U64), ("available_physical", _U64),
                ("total_commit", _U64), ("available_commit", _U64),
                ("total_virtual", _U64), ("available_virtual", _U64),
                ("available_extended_virtual", _U64)]


class _ProcessMemory(ctypes.Structure):
    _fields_ = [("cb", _DWORD), ("page_faults", _DWORD),
                ("peak_working_set", _SIZE), ("working_set", _SIZE),
                ("peak_paged_pool", _SIZE), ("paged_pool", _SIZE),
                ("peak_nonpaged_pool", _SIZE), ("nonpaged_pool", _SIZE),
                ("pagefile_usage", _SIZE), ("peak_pagefile_usage", _SIZE),
                ("private_usage", _SIZE)]


class _BasicLimits(ctypes.Structure):
    _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                ("flags", _DWORD), ("minimum_working_set", _SIZE),
                ("maximum_working_set", _SIZE), ("active_process_limit", _DWORD),
                ("affinity", _SIZE), ("priority", _DWORD), ("scheduling", _DWORD)]


class _IOCounters(ctypes.Structure):
    _fields_ = [(name, _U64) for name in (
        "read_operations", "write_operations", "other_operations",
        "read_bytes", "write_bytes", "other_bytes")]


class _ExtendedLimits(ctypes.Structure):
    _fields_ = [("basic", _BasicLimits), ("io", _IOCounters),
                ("process_memory_limit", _SIZE), ("job_memory_limit", _SIZE),
                ("peak_process_memory", _SIZE), ("peak_job_memory", _SIZE)]


class _BasicAccounting(ctypes.Structure):
    _fields_ = [("user_time", ctypes.c_int64), ("kernel_time", ctypes.c_int64),
                ("period_user_time", ctypes.c_int64), ("period_kernel_time", ctypes.c_int64),
                ("page_faults", _DWORD), ("total_processes", _DWORD),
                ("active_processes", _DWORD), ("terminated_processes", _DWORD)]


class _CpuRate(ctypes.Structure):
    _fields_ = [("flags", _DWORD), ("rate", _DWORD)]


class _JobMemory(ctypes.Structure):
    _fields_ = [("current", _U64), ("peak", _U64)]


def _windows_api():
    if sys.platform != "win32":
        raise OSError("Windows job containment is only available on Windows")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    signatures = {
        "GetCurrentProcess": ([], wintypes.HANDLE),
        "GetProcessAffinityMask": ([wintypes.HANDLE, ctypes.POINTER(_SIZE),
                                    ctypes.POINTER(_SIZE)], wintypes.BOOL),
        "GetActiveProcessorCount": ([wintypes.WORD], _DWORD),
        "GlobalMemoryStatusEx": ([ctypes.POINTER(_MemoryStatus)], wintypes.BOOL),
        "IsProcessInJob": ([wintypes.HANDLE, wintypes.HANDLE,
                            ctypes.POINTER(wintypes.BOOL)], wintypes.BOOL),
        "CreateJobObjectW": ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
        "SetInformationJobObject": ([wintypes.HANDLE, ctypes.c_int,
                                      ctypes.c_void_p, _DWORD], wintypes.BOOL),
        "QueryInformationJobObject": ([wintypes.HANDLE, ctypes.c_int,
                                        ctypes.c_void_p, _DWORD,
                                        ctypes.POINTER(_DWORD)], wintypes.BOOL),
        "AssignProcessToJobObject": ([wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
        "TerminateJobObject": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
        "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
        "OpenProcess": ([_DWORD, wintypes.BOOL, _DWORD], wintypes.HANDLE),
    }
    for name, (arguments, result) in signatures.items():
        function = getattr(kernel, name)
        function.argtypes = arguments
        function.restype = result
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE,
        ctypes.POINTER(_ProcessMemory), _DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    return kernel, psapi


def _winerror(operation):
    code = ctypes.get_last_error()
    return OSError(code, operation + ": " + ctypes.FormatError(code).strip())


def _query(kernel, handle, information_class, value):
    if not kernel.QueryInformationJobObject(handle, information_class,
            ctypes.byref(value), ctypes.sizeof(value), None):
        raise _winerror("QueryInformationJobObject class " + str(information_class))
    return value


def _process_memory(psapi, handle):
    value = _ProcessMemory()
    value.cb = ctypes.sizeof(value)
    if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(value), value.cb):
        raise _winerror("GetProcessMemoryInfo")
    return {"committed_bytes": int(value.private_usage),
            "working_set_bytes": int(value.working_set),
            "peak_working_set_bytes": int(value.peak_working_set),
            "peak_committed_bytes": int(value.peak_pagefile_usage)}


def _job_pids(kernel, handle):
    capacity = 16
    while True:
        class ProcessIds(ctypes.Structure):
            _fields_ = [("assigned", _DWORD), ("listed", _DWORD),
                        ("pids", _SIZE * capacity)]
        value = ProcessIds()
        if kernel.QueryInformationJobObject(handle, 3, ctypes.byref(value),
                                            ctypes.sizeof(value), None):
            if value.listed <= capacity and value.assigned <= capacity:
                return [int(value.pids[index]) for index in range(value.listed)]
            capacity = max(capacity * 2, int(value.assigned))
        else:
            code = ctypes.get_last_error()
            if code != 234:  # ERROR_MORE_DATA, the tree may grow during enumeration.
                raise _winerror("QueryInformationJobObject process list")
            capacity = max(capacity * 2, int(value.assigned))
        if capacity > 1_048_576:
            raise OSError("job process list cannot be sampled consistently")


def _job_usage(kernel, handle):
    limits = _query(kernel, handle, 9, _ExtendedLimits())
    diagnostics = []
    try:
        pids = _job_pids(kernel, handle)
    except OSError as error:
        pids = None
        diagnostics.append(str(error))
    try:
        # Class 28 is supported on current Windows but is not a documented SDK
        # contract. Never replace its failure with a purported exact sample.
        memory = _query(kernel, handle, 28, _JobMemory())
        current = int(memory.current)
        peak = max(int(memory.peak), int(limits.peak_job_memory))
        method = "JobObjectMemoryUsageInformation"
    except OSError as error:
        diagnostics.append(str(error))
        current = None
        peak = int(limits.peak_job_memory)
        method = "unavailable"
    cpu_seconds = None
    active_count = len(pids) if pids is not None else None
    try:
        accounting = _query(kernel, handle, 1, _BasicAccounting())
        cpu_seconds = (int(accounting.user_time) + int(accounting.kernel_time)) / 10_000_000
        active_count = int(accounting.active_processes)
    except OSError as error:
        diagnostics.append(str(error))
    return {"current_committed_bytes": current, "peak_committed_bytes": peak,
            "active_process_ids": pids,
            "active_process_count": active_count, "cpu_seconds": cpu_seconds,
            "peak_counter_scope": "raw OS high-water; denied allocation demand may be counted before rollback",
            "memory_accounting": method, "diagnostics": diagnostics}


def windows_resource_snapshot():
    """Sample host/process/current-job constraints without changing any job.

    Querying a NULL job handle exposes only the calling process's immediate job.
    Windows does not expose ancestor handles here. Class-28 memory accounting is
    optional; a finite current-job cap without that sample needs a manual limit.
    """
    kernel, psapi = _windows_api()
    diagnostics = []
    candidates = []
    process = kernel.GetCurrentProcess()
    cpu_complete = memory_complete = True
    total_cpus = int(kernel.GetActiveProcessorCount(0xFFFF))
    if total_cpus < 1:
        total_cpus = max(1, os.cpu_count() or 1)
        diagnostics.append(str(_winerror("GetActiveProcessorCount")))
        cpu_complete = False
    process_mask, system_mask = _SIZE(), _SIZE()
    if kernel.GetProcessAffinityMask(process, ctypes.byref(process_mask),
                                      ctypes.byref(system_mask)) and process_mask.value:
        affinity = min(total_cpus, int(process_mask.value).bit_count())
    else:
        affinity = 1
        cpu_complete = False
        diagnostics.append(str(_winerror("GetProcessAffinityMask")))
    status = _MemoryStatus()
    status.length = ctypes.sizeof(status)
    if kernel.GlobalMemoryStatusEx(ctypes.byref(status)):
        candidates.extend([
            {"source": "windows.available_physical", "available_bytes": int(status.available_physical)},
            {"source": "windows.available_commit", "available_bytes": int(status.available_commit)},
            {"source": "windows.available_virtual", "available_bytes": int(status.available_virtual)}])
        host = {"total_physical_bytes": int(status.total_physical),
                "available_physical_bytes": int(status.available_physical),
                "total_commit_bytes": int(status.total_commit),
                "available_commit_bytes": int(status.available_commit)}
    else:
        host = None
        memory_complete = False
        diagnostics.append(str(_winerror("GlobalMemoryStatusEx")))
    try:
        current_process = _process_memory(psapi, process)
    except OSError as error:
        current_process = None
        memory_complete = False
        diagnostics.append(str(error))
    member = wintypes.BOOL()
    job = None
    cpu_fraction = None
    if not kernel.IsProcessInJob(process, None, ctypes.byref(member)):
        diagnostics.append(str(_winerror("IsProcessInJob")))
        cpu_complete = memory_complete = False
    elif member.value:
        job = {"visibility": "immediate job only; ancestor handles are not available"}
        diagnostics.append("Windows ancestor job limits are not enumerable; only the immediate job is sampled")
        try:
            limits = _query(kernel, None, 9, _ExtendedLimits())
            job["limit_flags"] = int(limits.basic.flags)
            job["process_memory_limit_bytes"] = int(limits.process_memory_limit) if limits.basic.flags & 0x100 else None
            job["job_memory_limit_bytes"] = int(limits.job_memory_limit) if limits.basic.flags & 0x200 else None
            if limits.basic.flags & 0x10:
                job_affinity = int(limits.basic.affinity).bit_count()
                if job_affinity:
                    affinity = min(affinity, job_affinity)
            if limits.basic.flags & 0x100:
                if current_process is None:
                    memory_complete = False
                    candidates.append({"source": "windows.job_process_memory_limit_only",
                        "limit_bytes": int(limits.process_memory_limit), "usage_bytes": None,
                        "available_bytes": int(limits.process_memory_limit)})
                else:
                    candidates.append({"source": "windows.job_process_memory_remaining",
                        "limit_bytes": int(limits.process_memory_limit),
                        "usage_bytes": current_process["committed_bytes"],
                        "available_bytes": max(0, int(limits.process_memory_limit) - current_process["committed_bytes"])})
            if limits.basic.flags & 0x200:
                usage = _job_usage(kernel, None)
                job["usage"] = usage
                if usage["current_committed_bytes"] is None:
                    memory_complete = False
                    diagnostics.extend(usage["diagnostics"])
                    candidates.append({"source": "windows.job_memory_limit_only",
                        "limit_bytes": int(limits.job_memory_limit), "usage_bytes": None,
                        "available_bytes": int(limits.job_memory_limit)})
                else:
                    candidates.append({"source": "windows.job_memory_remaining",
                        "limit_bytes": int(limits.job_memory_limit),
                        "usage_bytes": usage["current_committed_bytes"],
                        "available_bytes": max(0, int(limits.job_memory_limit) - usage["current_committed_bytes"])})
        except OSError as error:
            memory_complete = False
            diagnostics.append(str(error))
        try:
            rate = _query(kernel, None, 15, _CpuRate())
            job["cpu_control_flags"] = int(rate.flags)
            job["cpu_rate_raw"] = int(rate.rate)
            if rate.flags & 1 and rate.flags & 4:
                if not 1 <= rate.rate <= 10000:
                    raise ValueError("invalid Windows hard CPU rate")
                cpu_fraction = Fraction(int(rate.rate), 10000)
            elif rate.flags & 1 and rate.flags & 16:
                maximum = int(rate.rate) >> 16
                if not 1 <= maximum <= 10000:
                    raise ValueError("invalid Windows maximum CPU rate")
                cpu_fraction = Fraction(maximum, 10000)
        except (OSError, ValueError) as error:
            cpu_complete = False
            diagnostics.append(str(error))
    return {"logical_cpus": total_cpus, "affinity_cpus": affinity,
            "job_cpu_fraction": str(cpu_fraction) if cpu_fraction is not None else None,
            "cpu_detection_complete": cpu_complete,
            "memory_detection_complete": memory_complete,
            "memory_candidates": candidates, "host": host,
            "process": current_process, "job": job, "diagnostics": diagnostics}


class WindowsJob:
    """A new, unnamed, non-inheritable job owned solely by this object.

    Construction applies both budgets or raises and closes the handle. attach()
    accepts a live subprocess.Popen with its captured Windows process handle.
    No breakaway flags are enabled. close() kills all attached descendants; the
    caller still waits for its Popen. Use a context manager or an explicit finally.
    """
    def __init__(self, memory_bytes: int, cpu_budget: int):
        for name, value in (("memory_bytes", memory_bytes), ("cpu_budget", cpu_budget)):
            if type(value) is not int or value <= 0:
                raise ValueError(name + " must be a positive integer")
        if memory_bytes > (1 << (ctypes.sizeof(_SIZE) * 8)) - 1:
            raise ValueError("memory_bytes exceeds the Windows SIZE_T range")
        self._kernel, _ = _windows_api()
        self._handle = None
        logical = int(self._kernel.GetActiveProcessorCount(0xFFFF))
        if logical < 1:
            raise _winerror("GetActiveProcessorCount")
        if cpu_budget > logical:
            raise ValueError("cpu_budget exceeds the active logical CPU count")
        handle = self._kernel.CreateJobObjectW(None, None)
        if not handle:
            raise _winerror("CreateJobObjectW")
        self._handle = handle
        self.memory_bytes = memory_bytes
        self.cpu_budget = cpu_budget
        self.cpu_rate = max(1, min(10000, cpu_budget * 10000 // logical))
        try:
            limits = _ExtendedLimits()
            limits.basic.flags = 0x2000 | 0x200 | 0x100  # KILL_ON_JOB_CLOSE, JOB/PROCESS_MEMORY
            limits.process_memory_limit = memory_bytes
            limits.job_memory_limit = memory_bytes
            self._set(9, limits)
            self._set(15, _CpuRate(1 | 4, self.cpu_rate))
        except BaseException:
            self._kernel.CloseHandle(handle)
            self._handle = None
            raise

    def _set(self, information_class, value):
        if not self._kernel.SetInformationJobObject(self._handle, information_class,
                ctypes.byref(value), ctypes.sizeof(value)):
            raise _winerror("SetInformationJobObject class " + str(information_class))

    def _open_handle(self):
        if self._handle is None:
            raise RuntimeError("WindowsJob is closed")
        return self._handle

    def attach(self, process: subprocess.Popen):
        handle = self._open_handle()
        if not isinstance(process, subprocess.Popen) or not getattr(process, "_handle", None):
            raise TypeError("attach requires a Windows subprocess.Popen with its captured handle")
        if process.pid == os.getpid():
            raise ValueError("cannot attach the supervisor to its owned stage job")
        if not self._kernel.AssignProcessToJobObject(handle, int(process._handle)):
            raise _winerror("AssignProcessToJobObject")

    def attach_worker_pid(self, pid):
        """Attach the live worker identified by the private READY/GO pipe.

        A Windows venv redirector may create the real interpreter before its
        Popen launcher is assigned to this job. The worker has not imported
        mathematics yet and is waiting on GO, so its handle remains live.
        """
        if type(pid) is not int or pid <= 0 or pid == os.getpid():
            raise ValueError("invalid owned worker pid")
        handle = self._kernel.OpenProcess(0x0100 | 0x0001 | 0x0400, False, pid)
        if not handle:
            raise _winerror("OpenProcess owned READY worker")
        try:
            belongs = wintypes.BOOL()
            if not self._kernel.IsProcessInJob(handle, self._open_handle(), ctypes.byref(belongs)):
                raise _winerror("IsProcessInJob owned READY worker")
            if not belongs.value and not self._kernel.AssignProcessToJobObject(self._open_handle(), handle):
                raise _winerror("AssignProcessToJobObject owned READY worker")
        finally:
            self._kernel.CloseHandle(handle)

    def usage(self) -> dict:
        result = _job_usage(self._kernel, self._open_handle())
        return {**result, "memory_limit_bytes": self.memory_bytes,
                "cpu_budget": self.cpu_budget, "cpu_rate_per_10000": self.cpu_rate,
                "cpu_rate_reference": "parent job if rate-controlled, otherwise system"}

    def terminate(self):
        if not self._kernel.TerminateJobObject(self._open_handle(), 1):
            raise _winerror("TerminateJobObject")

    def close(self):
        if self._handle is None:
            return
        handle = self._handle
        if not self._kernel.CloseHandle(handle):
            raise _winerror("CloseHandle owned job")
        self._handle = None

    def __enter__(self):
        self._open_handle()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def apply_posix_memory_limit(memory_bytes: int) -> dict:
    """Tighten this worker's inherited RLIMIT_AS, never increase a prior cap."""
    if type(memory_bytes) is not int or memory_bytes <= 0:
        raise ValueError("memory_bytes must be a positive integer")
    if os.name != "posix":
        raise OSError("RLIMIT_AS containment requires POSIX")
    import resource
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    finite = [value for value in (soft, hard) if value != resource.RLIM_INFINITY]
    effective = min([memory_bytes, *finite])
    if effective < memory_bytes:
        raise ValueError("memory_bytes exceeds the inherited RLIMIT_AS allowance")
    resource.setrlimit(resource.RLIMIT_AS, (effective, effective))
    return {"mechanism": "RLIMIT_AS", "limit_bytes": effective,
            "scope": "per-process virtual address space, inherited by descendants",
            "aggregate_rss_enforced": False}
