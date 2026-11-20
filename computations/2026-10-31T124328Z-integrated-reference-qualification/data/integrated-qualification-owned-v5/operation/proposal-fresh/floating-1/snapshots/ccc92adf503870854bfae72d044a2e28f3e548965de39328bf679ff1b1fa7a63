"""Memory-only containment and exact accounting for an owned Windows process tree.

Attach the Popen launcher and its private READY interpreter before sending GO.
The job never installs CPU rate control, including when numerical jobs nest in it.
Required job accounting fails closed; per-process observations are best effort.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
import subprocess
import uuid
import hashlib
from pathlib import Path

from scripts.whole_source.contract import ROOT
from scripts.whole_source.execution import neutral_helpers


_MAX_PROCESSES = 4096
_LIMIT_FLAGS = 0x2000 | 0x200 | 0x100
_PROCESS_ACCESS = 0x0100 | 0x0001 | 0x1000 | 0x100000
_NATIVE = {}


def _native(root):
    from scripts.whole_source.execution import BUNDLE, _HELPERS
    root = Path(root).resolve()
    for name, digest in _HELPERS.items():
        path = root/BUNDLE/name
        if path.lstat().st_size > 1048576:
            raise OSError("oversized lifecycle native helper")
        with path.open("rb") as stream:
            raw = stream.read(1048577)
        if hashlib.sha256(raw).hexdigest() != digest:
            raise OSError("changed lifecycle native helper")
    if root not in _NATIVE:
        _NATIVE[root] = neutral_helpers(root)[1]
    return _NATIVE[root]


class _ProcessEntry(ctypes.Structure):
    _fields_ = [("size", wintypes.DWORD), ("usage", wintypes.DWORD),
                ("pid", wintypes.DWORD), ("heap", ctypes.c_size_t),
                ("module", wintypes.DWORD), ("threads", wintypes.DWORD),
                ("parent_pid", wintypes.DWORD), ("priority", wintypes.LONG),
                ("flags", wintypes.DWORD), ("executable", wintypes.WCHAR * 260)]


def _filetime(value):
    return (int(value.dwHighDateTime) << 32) | int(value.dwLowDateTime)


class WindowsLifecycle:
    """Own a uniquely named, noninheritable memory job, never an arbitrary PID.

    attach() accepts a live Popen child of this caller. attach_ready_pid() accepts
    a member of this job or a live descendant of a held launcher. Process handles
    remain held through close(), so ownership never depends on a reusable PID.
    terminate() only terminates this job; sample() remains usable afterwards so
    callers can observe zero active processes before releasing the job handle.
    """

    def __init__(self, memory_bytes, *, helper_root=ROOT, name=None):
        if type(memory_bytes) is not int or memory_bytes <= 0:
            raise ValueError("memory_bytes must be a positive integer")
        if memory_bytes > (1 << (ctypes.sizeof(ctypes.c_size_t) * 8)) - 1:
            raise ValueError("memory_bytes exceeds the Windows SIZE_T range")
        if name is not None and (type(name) is not str or not name or "\0" in name):
            raise ValueError("name must be a nonempty Windows job name")
        self._initialize(helper_root)
        self.memory_bytes = memory_bytes
        self.name = name if name is not None else "Local\\rh-lifecycle-" + uuid.uuid4().hex
        ctypes.set_last_error(0)
        handle = self._kernel.CreateJobObjectW(None, self.name)
        if not handle:
            raise self._error("CreateJobObjectW")
        if ctypes.get_last_error() == 183:  # ERROR_ALREADY_EXISTS: never modify another job.
            self._close_handle(handle)
            raise OSError("lifecycle job name already exists")
        self._handle = handle
        try:
            limits = self._limits._ExtendedLimits()
            limits.basic.flags = _LIMIT_FLAGS
            limits.process_memory_limit = memory_bytes
            limits.job_memory_limit = memory_bytes
            if not self._kernel.SetInformationJobObject(handle, 9, ctypes.byref(limits),
                                                        ctypes.sizeof(limits)):
                raise self._error("SetInformationJobObject memory limits")
            self._installed_limits()
        except BaseException:
            self.close()
            raise

    def _initialize(self, helper_root):
        self._limits = _native(helper_root)
        self._kernel, self._psapi = self._limits._windows_api()
        self._handle = None
        self._roots = {}
        self._lineage = {}
        signatures = {
            "GetProcessId": ([wintypes.HANDLE], wintypes.DWORD),
            "GetProcessTimes": ([wintypes.HANDLE] +
                                [ctypes.POINTER(wintypes.FILETIME)] * 4, wintypes.BOOL),
            "WaitForSingleObject": ([wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD),
            "DuplicateHandle": ([wintypes.HANDLE, wintypes.HANDLE, wintypes.HANDLE,
                                 ctypes.POINTER(wintypes.HANDLE), wintypes.DWORD,
                                 wintypes.BOOL, wintypes.DWORD], wintypes.BOOL),
            "GetHandleInformation": ([wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)],
                                     wintypes.BOOL),
            "CreateToolhelp32Snapshot": ([wintypes.DWORD, wintypes.DWORD], wintypes.HANDLE),
            "Process32FirstW": ([wintypes.HANDLE, ctypes.POINTER(_ProcessEntry)], wintypes.BOOL),
            "Process32NextW": ([wintypes.HANDLE, ctypes.POINTER(_ProcessEntry)], wintypes.BOOL),
            "OpenJobObjectW": ([wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR], wintypes.HANDLE),
        }
        for function_name, (arguments, result) in signatures.items():
            function = getattr(self._kernel, function_name)
            function.argtypes = arguments
            function.restype = result

    def _error(self, operation):
        return self._limits._winerror(operation)

    def _open_handle(self):
        if self._handle is None:
            raise RuntimeError("WindowsLifecycle is closed")
        return self._handle

    def _close_handle(self, handle):
        if not self._kernel.CloseHandle(handle):
            raise self._error("CloseHandle owned lifecycle handle")

    def _query(self, information_class, value):
        return self._limits._query(self._kernel, self._open_handle(), information_class, value)

    def _times(self, handle):
        creation, exit_time, kernel, user = (wintypes.FILETIME() for _ in range(4))
        if not self._kernel.GetProcessTimes(handle, ctypes.byref(creation),
                ctypes.byref(exit_time), ctypes.byref(kernel), ctypes.byref(user)):
            raise self._error("GetProcessTimes")
        return {"creation_time_100ns": _filetime(creation),
                "exit_time_100ns": _filetime(exit_time),
                "cpu_user_100ns": _filetime(user), "cpu_kernel_100ns": _filetime(kernel)}

    def _require_live(self, handle):
        state = self._kernel.WaitForSingleObject(handle, 0)
        if state == 0xFFFFFFFF:
            raise self._error("WaitForSingleObject owned process")
        if state != 258:
            raise OSError("owned process is no longer live")

    def _parents(self):
        # Toolhelp PROCESSENTRY32W is the documented Windows parent-PID query.
        snapshot = self._kernel.CreateToolhelp32Snapshot(0x2, 0)
        if snapshot == ctypes.c_void_p(-1).value:
            raise self._error("CreateToolhelp32Snapshot processes")
        try:
            entry = _ProcessEntry()
            entry.size = ctypes.sizeof(entry)
            parents = {}
            present = self._kernel.Process32FirstW(snapshot, ctypes.byref(entry))
            while present:
                if len(parents) >= _MAX_PROCESSES:
                    raise OSError("process ancestry enumeration exceeds 4096 processes")
                parents[int(entry.pid)] = int(entry.parent_pid)
                present = self._kernel.Process32NextW(snapshot, ctypes.byref(entry))
            if ctypes.get_last_error() != 18:  # ERROR_NO_MORE_FILES
                raise self._error("Process32FirstW/Process32NextW")
            return parents
        finally:
            self._close_handle(snapshot)

    def _belongs(self, handle):
        belongs = wintypes.BOOL()
        if not self._kernel.IsProcessInJob(handle, self._open_handle(), ctypes.byref(belongs)):
            raise self._error("IsProcessInJob owned lifecycle process")
        return bool(belongs.value)

    def _assign(self, handle):
        if not self._belongs(handle):
            if not self._kernel.AssignProcessToJobObject(self._open_handle(), handle):
                raise self._error("AssignProcessToJobObject owned lifecycle process")
        if not self._belongs(handle):
            raise OSError("assigned process is absent from the owned lifecycle job")

    def launch(self, command, **kwargs):
        """Contain the suspended launcher before its venv redirector can run."""
        if kwargs.get("creationflags", 0) & 4:
            raise ValueError("launch owns the initial suspension")
        process = subprocess.Popen(command, creationflags=kwargs.pop("creationflags", 0) | 4,
                                   **kwargs)
        try:
            self.attach(process)
            self._resume(process.pid)
            return process
        except BaseException:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream is not None:
                    stream.close()
            raise

    def _resume(self, pid):
        class ThreadEntry(ctypes.Structure):
            _fields_ = [(name, wintypes.DWORD) for name in
                        ("size", "usage", "tid", "owner", "priority", "delta", "flags")]
        kernel = self._kernel
        for name in ("Thread32First", "Thread32Next"):
            function = getattr(kernel, name)
            function.argtypes = [wintypes.HANDLE, ctypes.POINTER(ThreadEntry)]
            function.restype = wintypes.BOOL
        kernel.OpenThread.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenThread.restype = wintypes.HANDLE
        kernel.ResumeThread.argtypes = [wintypes.HANDLE]
        kernel.ResumeThread.restype = wintypes.DWORD
        snapshot = kernel.CreateToolhelp32Snapshot(4, 0)
        if snapshot == ctypes.c_void_p(-1).value:
            raise self._error("CreateToolhelp32Snapshot suspended thread")
        threads = []
        try:
            entry = ThreadEntry()
            entry.size = ctypes.sizeof(entry)
            present, count = kernel.Thread32First(snapshot, ctypes.byref(entry)), 0
            while present:
                count += 1
                if count > 131072:
                    raise OSError("thread enumeration allowance exhausted")
                if entry.owner == pid:
                    threads.append(int(entry.tid))
                present = kernel.Thread32Next(snapshot, ctypes.byref(entry))
            if ctypes.get_last_error() != 18 or len(threads) != 1:
                raise OSError("suspended launcher has no unique initial thread")
            handle = kernel.OpenThread(2, False, threads[0])
            if not handle:
                raise self._error("OpenThread suspended launcher")
            try:
                if kernel.ResumeThread(handle) != 1:
                    raise OSError("launcher initial suspension changed")
            finally:
                self._close_handle(handle)
        finally:
            self._close_handle(snapshot)

    def attach(self, process: subprocess.Popen):
        """Hold and attach a genuine, live child launched by this caller."""
        self._open_handle()
        if not isinstance(process, subprocess.Popen) or not getattr(process, "_handle", None):
            raise TypeError("attach requires a Windows subprocess.Popen with its captured handle")
        pid = process.pid
        if type(pid) is not int or pid <= 0 or pid == os.getpid():
            raise ValueError("invalid owned launcher pid")
        current = self._kernel.GetCurrentProcess()
        duplicate = wintypes.HANDLE()
        if not self._kernel.DuplicateHandle(current, int(process._handle), current,
                                            ctypes.byref(duplicate), 0, False, 2):
            raise self._error("DuplicateHandle Popen launcher")
        handle = duplicate.value
        try:
            if self._kernel.GetProcessId(handle) != pid:
                raise OSError("Popen launcher handle does not match its pid")
            self._require_live(handle)
            creation = self._times(handle)["creation_time_100ns"]
            if (self._parents().get(pid) != os.getpid() or
                    creation < self._times(current)["creation_time_100ns"]):
                raise OSError("Popen launcher is not a child of this caller")
            if pid in self._roots:
                if self._roots[pid]["creation_time_100ns"] != creation:
                    raise OSError("owned launcher identity changed")
                if "launcher" not in self._roots[pid]["roles"]:
                    self._roots[pid]["roles"].append("launcher")
                self._roots[pid]["process"] = process
                return
            self._assign(handle)
            self._roots[pid] = {"handle": handle, "roles": ["launcher"],
                                "creation_time_100ns": creation, "process": process}
            handle = None
        finally:
            if handle is not None:
                self._close_handle(handle)

    def attach_ready_pid(self, pid):
        """Attach a private READY interpreter after proving owned lineage."""
        self._open_handle()
        if type(pid) is not int or pid <= 0 or pid == os.getpid():
            raise ValueError("invalid owned READY pid")
        if not any("launcher" in root["roles"] for root in self._roots.values()):
            raise OSError("READY attachment requires a held Popen launcher")
        handle = self._kernel.OpenProcess(_PROCESS_ACCESS, False, pid)
        if not handle:
            raise self._error("OpenProcess private READY interpreter")
        opened = {}
        try:
            self._require_live(handle)
            creation = self._times(handle)["creation_time_100ns"]
            if not self._belongs(handle):
                parents = self._parents()
                child_pid, child_creation = pid, creation
                seen = {pid}
                while True:
                    parent_pid = parents.get(child_pid)
                    if not parent_pid or parent_pid in seen or parent_pid == os.getpid():
                        raise OSError("READY interpreter is not a descendant of a held launcher")
                    seen.add(parent_pid)
                    if parent_pid in self._roots and "launcher" in self._roots[parent_pid]["roles"]:
                        parent = self._roots[parent_pid]
                        if parent["creation_time_100ns"] > child_creation:
                            raise OSError("READY parent identity changed")
                        break
                    parent_handle = self._kernel.OpenProcess(_PROCESS_ACCESS, False, parent_pid)
                    if not parent_handle:
                        raise self._error("OpenProcess READY ancestor")
                    opened[parent_pid] = parent_handle
                    self._require_live(parent_handle)
                    parent_creation = self._times(parent_handle)["creation_time_100ns"]
                    if parent_creation > child_creation:
                        raise OSError("READY ancestor identity changed")
                    child_pid, child_creation = parent_pid, parent_creation
                # Keep every observed ancestor pinned through assignment and close.
            for ancestor_handle in reversed(tuple(opened.values())):
                self._assign(ancestor_handle)
            self._assign(handle)
            if pid in self._roots:
                root = self._roots[pid]
                if root["creation_time_100ns"] != creation:
                    raise OSError("owned READY identity changed")
                if "ready" not in root["roles"]:
                    root["roles"].append("ready")
            else:
                self._roots[pid] = {"handle": handle, "roles": ["ready"],
                                    "creation_time_100ns": creation, "process": None}
                handle = None
            for ancestor_pid, ancestor_handle in opened.items():
                if ancestor_pid not in self._lineage:
                    self._lineage[ancestor_pid] = ancestor_handle
            opened = {ancestor_pid: ancestor_handle for ancestor_pid, ancestor_handle in opened.items()
                      if self._lineage[ancestor_pid] != ancestor_handle}
        finally:
            if handle is not None:
                self._close_handle(handle)
            for ancestor_handle in opened.values():
                self._close_handle(ancestor_handle)

    def _installed_limits(self):
        limits = self._query(9, self._limits._ExtendedLimits())
        cpu = self._query(15, self._limits._CpuRate())
        flags = wintypes.DWORD()
        if not self._kernel.GetHandleInformation(self._open_handle(), ctypes.byref(flags)):
            raise self._error("GetHandleInformation owned lifecycle job")
        if (limits.basic.flags != _LIMIT_FLAGS or
                limits.process_memory_limit != self.memory_bytes or
                limits.job_memory_limit != self.memory_bytes or cpu.flags or cpu.rate or
                flags.value & 1):
            raise OSError("owned lifecycle job does not have exactly memory-only noninheritable limits")
        return {"flags": int(limits.basic.flags), "kill_on_close": True,
                "process_memory_limit_bytes": int(limits.process_memory_limit),
                "job_memory_limit_bytes": int(limits.job_memory_limit),
                "cpu_rate_flags": int(cpu.flags), "cpu_rate_per_10000": int(cpu.rate),
                "handle_inheritable": False, "breakaway_allowed": False}

    def _pids(self):
        capacity = 16
        while capacity <= _MAX_PROCESSES:
            class ProcessIds(ctypes.Structure):
                _fields_ = [("assigned", self._limits._DWORD), ("listed", self._limits._DWORD),
                            ("pids", self._limits._SIZE * capacity)]
            value = ProcessIds()
            success = self._kernel.QueryInformationJobObject(self._open_handle(), 3,
                ctypes.byref(value), ctypes.sizeof(value), None)
            if success and (value.listed > value.assigned or value.listed > capacity):
                raise OSError("job process membership counters are inconsistent")
            if success and value.listed <= capacity and value.assigned <= capacity:
                return sorted(int(value.pids[index]) for index in range(value.listed))
            if not success and ctypes.get_last_error() != 234:
                raise self._error("QueryInformationJobObject process membership")
            capacity = max(capacity * 2, int(value.assigned))
        raise OSError("job process enumeration exceeds 4096 processes")

    def sample(self) -> dict:
        """Return raw OS counters; never substitute a partial job observation."""
        installed = self._installed_limits()
        accounting = self._query(1, self._limits._BasicAccounting())
        memory = self._query(28, self._limits._JobMemory())
        limits = self._query(9, self._limits._ExtendedLimits())
        pids = self._pids()
        diagnostics = []
        roots = []
        for pid, root in self._roots.items():
            observed = {"pid": pid, "roles": list(root["roles"]),
                        "creation_time_100ns": root["creation_time_100ns"],
                        "cpu_user_100ns": None, "cpu_kernel_100ns": None,
                        "exit_time_100ns": None, "memory": None, "diagnostics": []}
            try:
                observed.update(self._times(root["handle"]))
            except OSError as error:
                observed["diagnostics"].append(str(error))
            try:
                observed["memory"] = self._limits._process_memory(self._psapi, root["handle"])
            except OSError as error:
                observed["diagnostics"].append(str(error))
            diagnostics.extend("process " + str(pid) + ": " + note for note in observed["diagnostics"])
            roots.append(observed)
        raw_accounting = {name: int(getattr(accounting, name)) for name, _ in accounting._fields_}
        return {"cpu_user_100ns": int(accounting.user_time),
                "cpu_kernel_100ns": int(accounting.kernel_time),
                "cpu_total_100ns": int(accounting.user_time) + int(accounting.kernel_time),
                "accounting": raw_accounting,
                "current_committed_bytes": int(memory.current),
                "peak_committed_bytes": max(int(memory.peak), int(limits.peak_job_memory)),
                "active_process_ids": pids, "active_process_count": int(accounting.active_processes),
                "listed_process_count": len(pids), "installed_limits": installed,
                "memory_limit_bytes": self.memory_bytes, "root_processes": roots,
                "memory_accounting": "JobObjectMemoryUsageInformation",
                "scope": "owned job and inherited descendants; raw OS cumulative accounting",
                "peak_counter_scope": "raw OS high-water; denied allocation demand may be counted before rollback",
                "diagnostics": diagnostics}

    def terminate(self):
        if not self._kernel.TerminateJobObject(self._open_handle(), 1):
            raise self._error("TerminateJobObject owned lifecycle job")

    def close(self):
        """Release only owned handles; closing this job kills its descendants."""
        errors = []
        if self._handle is not None:
            try:
                self._close_handle(self._handle)
                self._handle = None
            except OSError as error:
                errors.append(error)
        for collection in (self._roots, self._lineage):
            for pid, value in list(collection.items()):
                handle = value["handle"] if collection is self._roots else value
                try:
                    self._close_handle(handle)
                    del collection[pid]
                except OSError as error:
                    errors.append(error)
        if errors:
            raise errors[0]

    def __enter__(self):
        self._open_handle()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def inspect_membership(name, pid=None, *, helper_root=ROOT) -> dict:
    """Query a specific lifecycle job without acquiring assign/terminate rights.

    This is cooperative operational supervision, not a hostile same-user sandbox.
    A query handle must be closed promptly because any job handle keeps the job
    object alive, including its kill-on-close lifetime.
    """
    if type(name) is not str or not name or "\0" in name:
        raise ValueError("name must be a nonempty Windows job name")
    if pid is not None and (type(pid) is not int or pid <= 0):
        raise ValueError("pid must be a positive integer")
    observer = WindowsLifecycle.__new__(WindowsLifecycle)
    observer._initialize(helper_root)
    observer.name = name
    observer._handle = observer._kernel.OpenJobObjectW(4, False, name)
    if not observer._handle:
        observer._handle = None
        raise observer._error("OpenJobObjectW query lifecycle job")
    process_handle = None
    try:
        limits = observer._query(9, observer._limits._ExtendedLimits())
        observer.memory_bytes = int(limits.job_memory_limit)
        if pid is None:
            process = observer._kernel.GetCurrentProcess()
            queried_pid = os.getpid()
        else:
            process_handle = observer._kernel.OpenProcess(0x1000, False, pid)
            if not process_handle:
                raise observer._error("OpenProcess query lifecycle membership")
            process = process_handle
            queried_pid = pid
        belongs = observer._belongs(process)
        return {**observer.sample(), "name": name, "pid": queried_pid, "belongs": belongs}
    finally:
        try:
            if process_handle is not None:
                observer._close_handle(process_handle)
        finally:
            observer.close()


def process_identity(pid, *, helper_root=ROOT):
    """Return creation time for a live held process, never a PID-only lease."""
    observer = WindowsLifecycle.__new__(WindowsLifecycle)
    observer._initialize(helper_root)
    handle = observer._kernel.OpenProcess(0x1000 | 0x100000, False, pid)
    if not handle:
        return None
    try:
        if observer._kernel.WaitForSingleObject(handle, 0) != 258:
            return None
        return observer._times(handle)["creation_time_100ns"]
    finally:
        observer._close_handle(handle)
