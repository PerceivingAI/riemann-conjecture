"""Execution instrumentation for the frozen T81/100 source and audit programs.

Measurement instrument, not a mathematical operation. The caller selects a
repository or captured tree and a producer or independent consumer version.
Stage timers call its functions unmodified. OS memory counters and Python
stack samples are recorded separately from the mathematical payload.
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



def _process_memory() -> dict[str, int | None]:
    """OS process counters in bytes. Unavailable counters are null, never zero."""
    if WIN:
        counters = PROCESS_MEMORY_COUNTERS_EX()
        counters.cb = ctypes.sizeof(counters)
        handle = _kernel32.GetCurrentProcess()
        if not _psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        return {"working_set": int(counters.WorkingSetSize),
                "peak_working_set": int(counters.PeakWorkingSetSize),
                "private_bytes": int(counters.PrivateUsage),
                "pagefile_bytes": int(counters.PagefileUsage), "virtual_bytes": None}
    values = {}
    try:
        with open("/proc/self/status", "r", encoding="ascii") as handle:
            for line in handle:
                if line.startswith(("VmRSS:", "VmHWM:", "VmSize:")):
                    key = line.split(":")[0]
                    values[key] = int(line.split()[1]) * 1024
    except OSError:
        pass
    return {"working_set": values.get("VmRSS"),
            "peak_working_set": values.get("VmHWM"),
            "private_bytes": None,
            "virtual_bytes": values.get("VmSize"), "pagefile_bytes": None}


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


def memory_provenance() -> dict:
    return {
        "scope": "current process only; excludes child process memory",
        "working_set": "GetProcessMemoryInfo.WorkingSetSize" if WIN else "/proc/self/status VmRSS",
        "peak_working_set": "GetProcessMemoryInfo.PeakWorkingSetSize" if WIN else "/proc/self/status VmHWM",
        "private_bytes": "GetProcessMemoryInfo.PrivateUsage" if WIN else None,
        "virtual_bytes": None if WIN else "/proc/self/status VmSize",
        "unavailable": "null; Linux virtual size is not private memory",
        "private_aggregation": "sampled maximum only; no OS private-memory high-water counter",
        "budget_detection_or_enforcement": False,
    }


def nullable_max(*values):
    known = [value for value in values if value is not None]
    return max(known) if known else None


class ChildAccounting:
    """Observe subprocess.run without changing its timeout/check/input semantics."""

    def __init__(self):
        self.records = []

    def wrap(self, original):
        @functools.wraps(original)
        def run(*args, **kwargs):
            started = time.perf_counter()
            record = {"cpu_seconds": None, "peak_memory_bytes": None}
            try:
                completed = original(*args, **kwargs)
                record["returncode"] = completed.returncode
                return completed
            except BaseException as error:
                record["error"] = f"{type(error).__name__}: {error}"
                record["returncode"] = getattr(error, "returncode", None)
                raise
            finally:
                record["wall_seconds"] = time.perf_counter() - started
                self.records.append(record)
        return run


class Instrumentation:
    def __init__(self, root: Path, harness_path: Path):
        self.root = root.resolve()
        self.harness_path = harness_path.resolve()
        self.records = {}
        self.stack = []
        self.lock = threading.Lock()
        self.samples = Counter()
        self.stage_samples = Counter()
        self.sample_count = 0
        self.peak_working_set = None
        self.os_peak_working_set = None
        self.peak_private = None
        self.peak_threads = None
        self.stage_peak = {}
        self.series = []
        self.memory_errors = []
        self.stop = threading.Event()
        self.main_thread = threading.get_ident()
        self._thread = threading.Thread(target=self._sampler, name="t081-sampler", daemon=True)

    def start(self):
        self.sample()
        self._thread.start()

    def finish(self):
        self.stop.set()
        self._thread.join()
        # OS high-water counters capture spikes even when native code held the GIL.
        self.sample()

    def observe_memory(self, memory, stage):
        working = memory.get("working_set")
        self.peak_working_set = nullable_max(self.peak_working_set, working)
        self.os_peak_working_set = nullable_max(
            self.os_peak_working_set, memory.get("peak_working_set"))
        self.peak_private = nullable_max(self.peak_private, memory.get("private_bytes"))
        self.stage_peak[stage] = nullable_max(self.stage_peak.get(stage), working)

    def sample(self):
        with self.lock:
            stage = self.stack[-1]["name"] if self.stack else "<driver>"
        try:
            memory = _process_memory()
        except Exception as error:
            self.memory_errors.append(f"{type(error).__name__}: {error}")
            memory = {}
        self.observe_memory(memory, stage)
        now = time.monotonic()
        if not self.series or now - self.series[-1][0] >= 1.0 or self.stop.is_set():
            self.series.append([now, memory.get("working_set"),
                                memory.get("private_bytes"), memory.get("virtual_bytes")])
        if not hasattr(self, "next_threads") or now >= self.next_threads:
            self.next_threads = now + THREAD_SAMPLE_SECONDS
            try:
                self.peak_threads = nullable_max(self.peak_threads, _thread_count())
            except Exception:
                pass
        self.sample_count += 1
        location = self._main_frame()
        if location:
            self.samples[location] += 1
            self.stage_samples[(stage, location)] += 1

    def _sampler(self):
        while not self.stop.wait(SAMPLE_SECONDS):
            self.sample()

    def _main_frame(self):
        frame = sys._current_frames().get(self.main_thread)
        while frame is not None:
            try:
                path = Path(frame.f_code.co_filename).resolve()
                if path != self.harness_path:
                    relative = path.relative_to(self.root).as_posix()
                    # _current_frames starts at the innermost frame.
                    return relative, frame.f_lineno, frame.f_code.co_name
            except (OSError, ValueError):
                pass
            frame = frame.f_back
        return None

    def wrap(self, module, name):
        original = getattr(module, name)

        @functools.wraps(original)
        def timed(*args, **kwargs):
            frame = {"name": name, "wall": time.perf_counter(),
                     "cpu": time.process_time(), "child_wall": 0.0, "child_cpu": 0.0}
            with self.lock:
                self.stack.append(frame)
            try:
                return original(*args, **kwargs)
            finally:
                wall = time.perf_counter() - frame["wall"]
                cpu = time.process_time() - frame["cpu"]
                with self.lock:
                    self.stack.remove(frame)
                    if self.stack:
                        self.stack[-1]["child_wall"] += wall
                        self.stack[-1]["child_cpu"] += cpu
                total = self.records.setdefault(name, dict(calls=0, wall=0.0, cpu=0.0,
                    exclusive_wall=0.0, exclusive_cpu=0.0, slowest=0.0))
                total["calls"] += 1
                total["wall"] += wall
                total["cpu"] += cpu
                total["exclusive_wall"] += max(0.0, wall - frame["child_wall"])
                total["exclusive_cpu"] += max(0.0, cpu - frame["child_cpu"])
                total["slowest"] = max(total["slowest"], wall)
        setattr(module, name, timed)

    def report(self, extra):
        stages = []
        for name, total in self.records.items():
            stages.append({"stage": name, "calls": total["calls"],
                "inclusive_wall_seconds": total["wall"],
                "inclusive_cpu_seconds": total["cpu"],
                "exclusive_wall_seconds": total["exclusive_wall"],
                "exclusive_cpu_seconds": total["exclusive_cpu"],
                "slowest_call_wall_seconds": total["slowest"],
                "cpu_over_wall": total["cpu"] / total["wall"] if total["wall"] else None,
                "peak_working_set_bytes": self.stage_peak.get(name)})
        stages.sort(key=lambda stage: -stage["exclusive_wall_seconds"])
        return {"format": "t081-execution-instrumentation-v2", **extra,
            "samples": self.sample_count,
            "peak_working_set_bytes": nullable_max(self.peak_working_set, self.os_peak_working_set),
            "sampled_peak_working_set_bytes": self.peak_working_set,
            "os_peak_working_set_bytes": self.os_peak_working_set,
            "peak_private_bytes": self.peak_private,
            "peak_threads": self.peak_threads,
            "stage_peak_working_set_bytes": self.stage_peak,
            "stages": stages,
            "stage_timing_note": "inclusive contains nested wrapped calls; exclusive subtracts only nested wrapped calls; process CPU includes sampler",
            "stack_sampling": {"interval_seconds": SAMPLE_SECONDS,
                "selection": "innermost matching program frame",
                "bias": "GIL-biased Python thread sampling; native code holding the GIL can starve sampler; sample counts are not time attribution",
                "boundary_samples": "start and final samples included"},
            "stack_samples": [{"location": list(loc), "samples": n}
                              for loc, n in self.samples.most_common(60)],
            "stage_stack_samples": [{"stage": stage, "location": list(loc), "samples": n}
                                    for (stage, loc), n in self.stage_samples.most_common(80)],
            "memory_provenance": memory_provenance(),
            "memory_errors": self.memory_errors,
            "memory_series_columns": ["monotonic_seconds", "working_set_bytes", "private_bytes", "virtual_bytes"],
            "memory_series": self.series}


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


COARSE_BUILD_STAGES = ("residual_matrices", "combined_square", "source", "kernel_step")


def runtime_metadata():
    try:
        import flint
        flint_metadata = {"flint_version": getattr(flint, "__version__", None),
                          "ctx_precision": flint.ctx.prec, "ctx_threads": flint.ctx.threads}
    except ImportError:
        flint_metadata = {"flint_version": None, "ctx_precision": None, "ctx_threads": None}
    return {"python": sys.version, "executable": sys.executable,
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(), "sys_platform": sys.platform,
        "processor": platform.processor(), "cpu_count": os.cpu_count(),
        "affinity": _affinity(), "physical_memory": _physical_memory(),
        **flint_metadata,
        "thread_environment": {name: os.environ.get(name) for name in (
            "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "FLINT_NUM_THREADS")}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--kind", choices=("build", "verify"), required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--level", choices=("full", "coarse"), default="full")
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.report.exists():
        parser.error("fresh report required")
    root = Path.cwd().resolve()
    if not (root / "scripts").is_dir() or not (root / "computations").is_dir():
        parser.error("run from the isolated repository root")
    program = args.program.resolve()
    program_hash = hashlib.sha256(program.read_bytes()).hexdigest()
    import subprocess
    original_run, original_argv, original_path = subprocess.run, sys.argv, list(sys.path)
    instrument = Instrumentation(root, Path(__file__))
    child = ChildAccounting()
    rest = args.rest[1:] if args.rest and args.rest[0] == "--" else args.rest
    argv = [str(program), *rest]
    stages = (COARSE_BUILD_STAGES if args.level == "coarse" else BUILD_STAGES) \
        if args.kind == "build" else AUDIT_STAGES
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    status, error, exit_code = "FAILED", None, 70
    instrument.start()
    try:
        sys.path.insert(0, str(root))
        sys.argv = argv
        subprocess.run = child.wrap(original_run)
        module = load_module(program, "t081_instrumented_program")
        for name in stages:
            if hasattr(module, name):
                instrument.wrap(module, name)
        # Match the original profile's successful-run timing scope: main only.
        started_wall, started_cpu = time.perf_counter(), time.process_time()
        exit_code = int(module.main() or 0)
        status = "COMPLETED" if exit_code == 0 else "FAILED"
        if exit_code:
            error = f"program returned exit status {exit_code}"
    except SystemExit as exception:
        exit_code = exception.code if isinstance(exception.code, int) else (0 if exception.code is None else 1)
        status = "COMPLETED" if exit_code == 0 else "FAILED"
        error = None if exit_code == 0 else f"SystemExit: {exception.code}"
        raise
    except BaseException as exception:
        error = f"{type(exception).__name__}: {exception}"
        raise
    finally:
        subprocess.run, sys.argv = original_run, original_argv
        sys.path[:] = original_path
        instrument.finish()
        wall, cpu = time.perf_counter() - started_wall, time.process_time() - started_cpu
        payload = instrument.report({
            "program": program.relative_to(root).as_posix(),
            "program_sha256": program_hash,
            "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "argv": argv, "level": args.level, "kind": args.kind,
            "status": status, "error": error, "exit_code": exit_code,
            "wall_seconds": wall, "cpu_seconds": cpu,
            "timing_scope": "program main through final sample; module import excluded on success",
            "cpu_over_wall": cpu / wall if wall else None,
            **runtime_metadata(), "child_processes": child.records})
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
