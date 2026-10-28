"""Measure whether python-flint's public Arb API actually uses native threads.

Identical inputs and precision are multiplied under increasing
``flint.ctx.threads`` settings while wall time, process CPU time and the
observed OS thread count are recorded. The matrix shapes mirror the products in
the frozen T81/100 operations (tall-skinny and square). Nothing here is a
mathematical result.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import sys
import threading
import time
from pathlib import Path

from flint import arb, arb_mat, ctx, fmpq

SAMPLE_SECONDS = 0.02
WIN = sys.platform == "win32"

if WIN:
    from ctypes import wintypes

    class THREADENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
            ("th32ThreadID", wintypes.DWORD), ("th32OwnerProcessID", wintypes.DWORD),
            ("tpBasePri", wintypes.LONG), ("tpDeltaPri", wintypes.LONG),
            ("dwFlags", wintypes.DWORD),
        ]

    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    _kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    _kernel32.Thread32First.argtypes = [wintypes.HANDLE, ctypes.POINTER(THREADENTRY32)]
    _kernel32.Thread32Next.argtypes = [wintypes.HANDLE, ctypes.POINTER(THREADENTRY32)]
    _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    _kernel32.GetCurrentProcessId.restype = wintypes.DWORD


def thread_count() -> int:
    if WIN:
        snapshot = _kernel32.CreateToolhelp32Snapshot(0x4, 0)
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
    with open("/proc/self/status", "r", encoding="ascii") as handle:
        for line in handle:
            if line.startswith("Threads:"):
                return int(line.split()[1])
    return len(threading.enumerate())


class ThreadWatcher:
    def __init__(self) -> None:
        self.peak = thread_count()
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        while not self.stop.wait(SAMPLE_SECONDS):
            self.peak = max(self.peak, thread_count())

    def start(self) -> None:
        self.thread.start()

    def finish(self) -> int:
        self.stop.set()
        self.thread.join(timeout=2)
        return max(self.peak, thread_count())


def matrix(rows: int, columns: int):
    out = arb_mat(rows, columns)
    for i in range(rows):
        for j in range(columns):
            out[i, j] = arb(fmpq((i * 37 + j * 11) % 97 - 48, (i + j) % 89 + 1))
    return out


def timed_product(left, right, budget: float, rows: int) -> dict:
    started = time.perf_counter()
    product = left * right
    single = time.perf_counter() - started
    repetitions = max(1, min(4, int(budget / single) if single > 0 else 1))
    blocks = []
    if repetitions > 1:
        for _ in range(repetitions):
            mark = time.perf_counter()
            product = left * right
            blocks.append(time.perf_counter() - mark)
    else:
        blocks.append(single)
    entries = [(i, j, str(product[i, j])) for i, j in ((0, 0), (rows // 2, 0), (rows - 1, 0))]
    return {"single_seconds": single, "repetitions": len(blocks),
            "wall_seconds": sum(blocks), "entries": entries, "product": product}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--precisions", default="4608,6144")
    parser.add_argument("--budget", type=float, default=12.0)
    args = parser.parse_args()

    report = {
        "format": "t081-native-threading-probe-v1",
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": sys.version,
        "cpu_count": os.cpu_count(),
        "affinity": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "thread_environment": {name: os.environ.get(name) for name in (
            "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "FLINT_NUM_THREADS")},
        "flint_version": __import__("flint").__version__,
        "settings": [],
        "production_admission": False,
    }
    shapes = (("tall-skinny-1x3", 160, 480), ("square-256", 256, 256), ("square-413", 413, 413))
    for precision in (int(item) for item in args.precisions.split(",")):
        ctx.prec = precision
        for label, rows, columns in shapes:
            left = matrix(rows, columns)
            right = matrix(columns, rows)
            baseline = None
            settings = (1, 6) if label == "square-413" else (1, 2, 3, 6)
            for threads in settings:
                ctx.threads = threads
                watcher = ThreadWatcher()
                watcher.start()
                cpu_before = time.process_time()
                wall_before = time.perf_counter()
                outcome = timed_product(left, right, args.budget, rows)
                wall = time.perf_counter() - wall_before
                cpu = time.process_time() - cpu_before
                peak_threads = watcher.finish()
                entries = outcome["entries"]
                if baseline is None:
                    baseline = entries
                identical = entries == baseline
                ctx.prec = precision
                report["settings"].append({
                    "precision": precision, "shape": label, "rows": rows, "columns": columns,
                    "ctx_threads": threads, "observed_peak_threads": peak_threads,
                    "wall_seconds": round(wall, 6), "cpu_seconds": round(cpu, 6),
                    "cpu_over_wall": round(cpu / wall, 4) if wall else None,
                    "repetitions": outcome["repetitions"],
                    "identical_entries_across_settings": identical,
                })
                print(json.dumps(report["settings"][-1], sort_keys=True), flush=True)
        ctx.threads = 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
