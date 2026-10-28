"""Execution instrumentation for the frozen T81/100 source and audit programs.

Measurement instrument, not a mathematical operation. It imports the frozen
producer or independent consumer byte-for-byte from an isolated tree, wraps the
program's own top-level functions with wall/CPU timers, samples process memory,
thread count and the main-thread Python stack, and accounts for any child
process the program launches. It changes no input, precision, parameter or
control flow. Stage timers are additive only: the wrapped functions are called
unmodified by the program itself.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import json
import os
import platform
import sys
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path

WIN = sys.platform == "win32"
SAMPLE_SECONDS = 0.05
THREAD_SAMPLE_SECONDS = 15.0

# --------------------------------------------------------------------------
# platform counters (standard library + ctypes only; no new dependency)
# --------------------------------------------------------------------------
if WIN:
    import ctypes
    from ctypes import wintypes

    class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
            ("PrivateUsage", ctypes.c_size_t),
        ]

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", wintypes.DWORD),
            ("dwMemoryLoad", wintypes.DWORD),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    class THREADENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ThreadID", wintypes.DWORD),
            ("th32OwnerProcessID", wintypes.DWORD),
            ("tpBasePri", wintypes.LONG),
            ("tpDeltaPri", wintypes.LONG),
            ("dwFlags", wintypes.DWORD),
        ]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    class JOBOBJECT_BASIC_ACCOUNTING_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("TotalUserTime", ctypes.c_longlong),
            ("TotalKernelTime", ctypes.c_longlong),
            ("ThisPeriodTotalUserTime", ctypes.c_longlong),
            ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
            ("TotalPageFaultCount", wintypes.DWORD),
            ("TotalProcesses", wintypes.DWORD),
            ("ActiveProcesses", wintypes.DWORD),
            ("TotalTerminatedProcesses", wintypes.DWORD),
        ]

    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _psapi = ctypes.WinDLL("psapi", use_last_error=True)
    _kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    _kernel32.GetCurrentProcess.argtypes = []
    _psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS_EX), wintypes.DWORD]
    _psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    _kernel32.GetProcessAffinityMask.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
    _kernel32.GetProcessAffinityMask.restype = wintypes.BOOL
    _kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    _kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    _kernel32.Thread32First.argtypes = [wintypes.HANDLE, ctypes.POINTER(THREADENTRY32)]
    _kernel32.Thread32First.restype = wintypes.BOOL
    _kernel32.Thread32Next.argtypes = [wintypes.HANDLE, ctypes.POINTER(THREADENTRY32)]
    _kernel32.Thread32Next.restype = wintypes.BOOL
    _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    _kernel32.GetCurrentProcessId.restype = wintypes.DWORD
    _kernel32.GetCurrentProcessId.argtypes = []
    _kernel32.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MEMORYSTATUSEX)]
    _kernel32.GlobalMemoryStatusEx.restype = wintypes.BOOL
    _kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    _kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    _kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    _kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    _kernel32.QueryInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p]
    _kernel32.QueryInformationJobObject.restype = wintypes.BOOL


def _process_memory() -> dict[str, int]:
    """Current working set and private bytes in bytes."""
    if WIN:
        counters = PROCESS_MEMORY_COUNTERS_EX()
        counters.cb = ctypes.sizeof(counters)
        handle = _kernel32.GetCurrentProcess()
        if not _psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        return {"working_set": int(counters.WorkingSetSize),
                "peak_working_set": int(counters.PeakWorkingSetSize),
                "private_bytes": int(counters.PrivateUsage),
                "pagefile_bytes": int(counters.PagefileUsage)}
    values = {}
    try:
        with open("/proc/self/status", "r", encoding="ascii") as handle:
            for line in handle:
                if line.startswith(("VmRSS:", "VmHWM:", "VmSize:")):
                    key = line.split(":")[0]
                    values[key] = int(line.split()[1]) * 1024
    except OSError:
        pass
    return {"working_set": values.get("VmRSS", 0),
            "peak_working_set": values.get("VmHWM", 0),
            "private_bytes": values.get("VmSize", 0),
            "pagefile_bytes": 0}


def _thread_count() -> int:
    if WIN:
        snapshot = _kernel32.CreateToolhelp32Snapshot(0x00000004, 0)
        if snapshot in (0, ctypes.c_void_p(-1).value):
            return len(threading.enumerate())
        entry = THREADENTRY32()
        entry.dwSize = ctypes.sizeof(entry)
        pid = _kernel32.GetCurrentProcessId()
        total = 0
        try:
            more = _kernel32.Thread32First(snapshot, ctypes.byref(entry))
            while more:
                if entry.th32OwnerProcessID == pid:
                    total += 1
                more = _kernel32.Thread32Next(snapshot, ctypes.byref(entry))
        finally:
            _kernel32.CloseHandle(snapshot)
        return total
    try:
        with open("/proc/self/status", "r", encoding="ascii") as handle:
            for line in handle:
                if line.startswith("Threads:"):
                    return int(line.split()[1])
    except OSError:
        pass
    return len(threading.enumerate())


def _affinity() -> dict[str, object]:
    if WIN:
        process_mask = ctypes.c_size_t()
        system_mask = ctypes.c_size_t()
        handle = _kernel32.GetCurrentProcess()
        if _kernel32.GetProcessAffinityMask(
                handle, ctypes.byref(process_mask), ctypes.byref(system_mask)):
            return {"process_mask": int(process_mask.value),
                    "system_mask": int(system_mask.value),
                    "effective_cpus": _bit_count(int(process_mask.value)),
                    "system_cpus": _bit_count(int(system_mask.value))}
        return {"process_mask": None, "system_mask": None,
                "effective_cpus": None, "system_cpus": None}
    try:
        mask = os.sched_getaffinity(0)  # type: ignore[attr-defined]
        return {"process_mask": None, "system_mask": None,
                "effective_cpus": len(mask), "system_cpus": os.cpu_count()}
    except AttributeError:
        return {"process_mask": None, "system_mask": None,
                "effective_cpus": os.cpu_count(), "system_cpus": os.cpu_count()}


def _bit_count(value: int) -> int:
    return bin(value).count("1")


def _physical_memory() -> dict[str, int]:
    if WIN:
        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(status)
        if _kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return {"total_bytes": int(status.ullTotalPhys),
                    "available_bytes": int(status.ullAvailPhys)}
        return {}
    try:
        with open("/proc/meminfo", "r", encoding="ascii") as handle:
            lines = {line.split(":")[0]: int(line.split()[1]) * 1024 for line in handle}
        return {"total_bytes": lines.get("MemTotal", 0), "available_bytes": lines.get("MemAvailable", 0)}
    except OSError:
        return {}


# --------------------------------------------------------------------------
# child-process accounting (Windows job object; wall time everywhere)
# --------------------------------------------------------------------------
class ChildAccounting:
    def __init__(self) -> None:
        self.records: list[dict[str, object]] = []
        self._lock = threading.Lock()

    def wrap(self, original):
        @functools.wraps(original)
        def run(*args, **kwargs):
            subprocess_module = __import__("subprocess")
            started = time.perf_counter()
            job = None
            stdout = stderr = None
            returncode = None
            if WIN:
                job = _kernel32.CreateJobObjectW(None, None)
            try:
                options = dict(kwargs)
                if options.pop("capture_output", False):
                    options.setdefault("stdout", subprocess_module.PIPE)
                    options.setdefault("stderr", subprocess_module.PIPE)
                process = subprocess_module.Popen(*args, **options)
                if job:
                    try:
                        _kernel32.AssignProcessToJobObject(job, int(process._handle))
                    except Exception:
                        _kernel32.CloseHandle(job)
                        job = None
                stdout, stderr = process.communicate()
                returncode = process.returncode
            finally:
                elapsed = time.perf_counter() - started
                record = {"argv0": None, "elapsed_seconds": elapsed}
                completed = subprocess_module.CompletedProcess(args, returncode, stdout, stderr)
                try:
                    command = args[0] if args else kwargs.get("args")
                    if isinstance(command, (list, tuple)) and command:
                        record["argv0"] = Path(str(command[0])).name
                        record["argv"] = [Path(str(item)).name for item in command]
                except Exception:
                    pass
                if job:
                    try:
                        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
                        _kernel32.QueryInformationJobObject(
                            job, 9, ctypes.byref(info), ctypes.sizeof(info), None)
                        accounting = JOBOBJECT_BASIC_ACCOUNTING_INFORMATION()
                        _kernel32.QueryInformationJobObject(
                            job, 1, ctypes.byref(accounting), ctypes.sizeof(accounting), None)
                        record["child_cpu_seconds"] = (
                            int(accounting.TotalUserTime) + int(accounting.TotalKernelTime)) / 1e7
                        record["child_peak_process_bytes"] = int(info.PeakProcessMemoryUsed)
                        record["child_processes"] = int(accounting.TotalProcesses)
                    finally:
                        _kernel32.CloseHandle(job)
                with self._lock:
                    self.records.append(record)
            return completed
        return run


# --------------------------------------------------------------------------
# stage timers and sampler
# --------------------------------------------------------------------------
class Instrumentation:
    def __init__(self, root: Path, harness_path: Path) -> None:
        self.root = root.resolve()
        self.harness_path = harness_path.resolve()
        self.records: dict[str, list[dict[str, float]]] = defaultdict(list)
        self.stack: list[dict[str, float]] = []
        self.lock = threading.Lock()
        self.samples: Counter = Counter()
        self.stage_samples: Counter = Counter()
        self.sample_count = 0
        self.peak_working_set = 0
        self.peak_private = 0
        self.peak_threads = 1
        self.stage_peak: dict[str, int] = {}
        self.series: list[list[float]] = []
        self.stop = threading.Event()
        self.main_thread = threading.get_ident()
        self._thread = threading.Thread(target=self._sampler, name="t081-sampler", daemon=True)

    # -- sampler -----------------------------------------------------------
    def start(self) -> None:
        self._thread.start()

    def finish(self) -> None:
        self.stop.set()
        self._thread.join(timeout=5)

    def _sampler(self) -> None:
        next_series = 0.0
        next_threads = 0.0
        while not self.stop.wait(SAMPLE_SECONDS):
            try:
                memory = _process_memory()
            except Exception:
                continue
            now = time.monotonic()
            working = memory["working_set"]
            self.peak_working_set = max(self.peak_working_set, working)
            self.peak_private = max(self.peak_private, memory["private_bytes"])
            if now >= next_threads:
                next_threads = now + THREAD_SAMPLE_SECONDS
                try:
                    self.peak_threads = max(self.peak_threads, _thread_count())
                except Exception:
                    pass
            with self.lock:
                stage = self.stack[-1]["name"] if self.stack else "<driver>"
            self.stage_peak[stage] = max(self.stage_peak.get(stage, 0), working)
            location = self._main_frame()
            self.sample_count += 1
            if location:
                self.samples[location] += 1
                self.stage_samples[(stage, location)] += 1
            if now >= next_series:
                next_series = now + 1.0
                self.series.append([round(now, 3), working, memory["private_bytes"]])

    def _main_frame(self):
        frames = sys._current_frames()
        frame = frames.get(self.main_thread)
        chosen = None
        while frame is not None:
            filename = frame.f_code.co_filename
            try:
                path = Path(filename).resolve()
            except (OSError, ValueError):
                frame = frame.f_back
                continue
            if path == self.harness_path:
                frame = frame.f_back
                continue
            try:
                relative = path.relative_to(self.root).as_posix()
            except ValueError:
                frame = frame.f_back
                continue
            chosen = [relative, frame.f_lineno, frame.f_code.co_name]
            frame = frame.f_back
        return tuple(chosen) if chosen else None

    # -- stage timers ------------------------------------------------------
    def wrap(self, module, name: str) -> None:
        original = getattr(module, name)

        @functools.wraps(original)
        def timed(*args, **kwargs):
            frame = {"name": name, "start_wall": time.perf_counter(),
                     "start_cpu": time.process_time(), "child_wall": 0.0,
                     "child_cpu": 0.0, "ws_in": 0}
            try:
                frame["ws_in"] = _process_memory()["working_set"]
            except Exception:
                frame["ws_in"] = 0
            with self.lock:
                self.stack.append(frame)
            try:
                return original(*args, **kwargs)
            finally:
                wall = time.perf_counter() - frame["start_wall"]
                cpu = time.process_time() - frame["start_cpu"]
                try:
                    frame["ws_out"] = _process_memory()["working_set"]
                except Exception:
                    frame["ws_out"] = 0
                with self.lock:
                    if self.stack and self.stack[-1] is frame:
                        self.stack.pop()
                    elif frame in self.stack:
                        self.stack.remove(frame)
                    if self.stack:
                        self.stack[-1]["child_wall"] += wall
                        self.stack[-1]["child_cpu"] += cpu
                self.records[name].append({
                    "wall": wall, "cpu": cpu,
                    "exclusive_wall": max(0.0, wall - frame["child_wall"]),
                    "exclusive_cpu": max(0.0, cpu - frame["child_cpu"]),
                    "ws_in": frame["ws_in"], "ws_out": frame["ws_out"]})

        setattr(module, name, timed)

    # -- report ------------------------------------------------------------
    def report(self, extra: dict[str, object]) -> dict[str, object]:
        stages = []
        for name, calls in self.records.items():
            wall = sum(call["wall"] for call in calls)
            cpu = sum(call["cpu"] for call in calls)
            exclusive_wall = sum(call["exclusive_wall"] for call in calls)
            exclusive_cpu = sum(call["exclusive_cpu"] for call in calls)
            slowest = max(calls, key=lambda call: call["wall"])
            stages.append({
                "stage": name, "calls": len(calls),
                "inclusive_wall_seconds": round(wall, 6),
                "inclusive_cpu_seconds": round(cpu, 6),
                "exclusive_wall_seconds": round(exclusive_wall, 6),
                "exclusive_cpu_seconds": round(exclusive_cpu, 6),
                "cpu_over_wall": round(cpu / wall, 4) if wall else None,
                "slowest_call_wall_seconds": round(slowest["wall"], 6),
                "peak_working_set_bytes": self.stage_peak.get(name, 0),
            })
        stages.sort(key=lambda item: -item["exclusive_wall_seconds"])
        samples = [{"location": list(location), "samples": count}
                   for location, count in self.samples.most_common(60)]
        stages_samples = [{"stage": stage, "location": list(location), "samples": count}
                          for (stage, location), count in self.stage_samples.most_common(80)]
        return {"format": "t081-execution-instrumentation-v1", **extra,
                "samples": self.sample_count,
                "peak_working_set_bytes": self.peak_working_set,
                "peak_private_bytes": self.peak_private,
                "peak_threads": self.peak_threads,
                "stage_peak_working_set_bytes": self.stage_peak,
                "stages": stages,
                "stack_samples": samples,
                "stage_stack_samples": stages_samples,
                "memory_series": self.series}


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------
def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILD_STAGES = ("pinned", "publish", "legendre_values", "residual_matrices", "bessel",
                "kernel_step", "combined_square", "source")

AUDIT_STAGES = ("frozen_inputs", "replay_declaration", "residual_kernel",
                "validate_model_allowance", "validate_weights", "rodrigues",
                "harmonic_tables", "residual_outputs", "residual_blocks",
                "binomial_shift", "power_window_moments", "log_minus_primitives",
                "logarithmic_window_moments", "arithmetic_blocks",
                "complete_arithmetic_squared", "frequency_kernels", "reconstruct",
                "check_matrix", "audit")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--kind", choices=("build", "verify"), required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    root = Path.cwd().resolve()
    if not (root / "scripts").is_dir() or not (root / "computations").is_dir():
        raise SystemExit("run from the isolated repository root")
    sys.path.insert(0, str(root))

    program = args.program.resolve()
    module = load_module(program, "t081_instrumented_program")
    instrument = Instrumentation(root, Path(__file__))
    child = ChildAccounting()
    __import__("subprocess").run = child.wrap(__import__("subprocess").run)

    stages = BUILD_STAGES if args.kind == "build" else AUDIT_STAGES
    for name in stages:
        if hasattr(module, name):
            instrument.wrap(module, name)

    from flint import ctx

    rest = list(args.rest)
    if rest and rest[0] == "--":
        rest = rest[1:]
    sys.argv = [str(program), *rest]
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    instrument.start()
    status, error = "COMPLETED", None
    try:
        exit_code = module.main()
    except BaseException as exception:  # measurement must record the failure
        exit_code = 70
        status, error = "FAILED", f"{type(exception).__name__}: {exception}"
        raise
    finally:
        instrument.finish()
        wall = time.perf_counter() - started_wall
        cpu = time.process_time() - started_cpu
        payload = instrument.report({
            "program": str(program.relative_to(root)).replace("\\", "/"),
            "program_sha256": hashlib.sha256(program.read_bytes()).hexdigest(),
            "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "argv": sys.argv,
            "status": status,
            "error": error,
            "wall_seconds": round(wall, 6),
            "cpu_seconds": round(cpu, 6),
            "cpu_over_wall": round(cpu / wall, 4) if wall else None,
            "python": sys.version,
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "affinity": _affinity(),
            "physical_memory": _physical_memory(),
            "flint_version": getattr(__import__("flint"), "__version__", None),
            "ctx_precision": ctx.prec,
            "ctx_threads": ctx.threads,
            "thread_environment": {name: os.environ.get(name) for name in (
                "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "FLINT_NUM_THREADS")},
            "child_processes": child.records,
        })
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return int(exit_code or 0)


if __name__ == "__main__":
    raise SystemExit(main())
