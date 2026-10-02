"""Manual isolated rigorous-assembly profiling, never theorem qualification.

Run as ``uv run --locked python -m scripts.profile_multi_prime_assembly``.
Each dimension runs sequentially, without a continuation cache or worker pool.
"""

from __future__ import annotations

import argparse
import cProfile
import ctypes
import functools
import hashlib
import importlib.metadata
import json
import os
import platform
import pstats
import subprocess
import sys
import time
from contextlib import ExitStack
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

from scripts.cert import legendre_schur as shared
from scripts.cert import multi_prime_legendre_schur as assembly
from scripts.cert import prime_power_terms as arithmetic


SOURCE_PATHS = (
    "scripts/profile_multi_prime_assembly.py",
    "scripts/cert/multi_prime_legendre_schur.py",
    "scripts/cert/prime_power_terms.py",
    "scripts/cert/legendre_schur.py",
    "scripts/cert/residual_kernel.py",
    "scripts/cert/constants.py",
    "uv.lock",
)


def _peak_memory_bytes() -> int:
    if sys.platform == "win32":
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                (name, ctypes.c_size_t)
                for name in (
                    "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                    "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                    "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage",
                )
            ]

        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        get_process = ctypes.windll.kernel32.GetCurrentProcess
        get_process.restype = wintypes.HANDLE
        get_info = ctypes.windll.psapi.GetProcessMemoryInfo
        get_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        get_info.restype = wintypes.BOOL
        if not get_info(get_process(), ctypes.byref(counters), counters.cb):
            raise ctypes.WinError()
        return counters.PeakWorkingSetSize
    import resource

    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak if sys.platform == "darwin" else peak * 1024


def _provenance() -> dict[str, object]:
    root = Path(__file__).resolve().parents[1]
    return {
        "utc": datetime.now(timezone.utc).isoformat(),
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "source_sha256": {
            path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in SOURCE_PATHS
        },
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "versions": {name: importlib.metadata.version(name) for name in ("python-flint", "numpy", "scipy")},
        "thread_environment": {name: os.environ.get(name) for name in (
            "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"
        )},
        "cache_policy": "no continuation cache; sequential assemblies in one process",
        "peak_memory_scope": "process lifetime high-water mark, not per-stage allocation",
    }


def _stage_wrappers(stack: ExitStack, records: dict[str, dict[str, float]]) -> None:
    active: list[list[float]] = []

    def install(module, name: str) -> None:
        original = getattr(module, name)
        key = module.__name__ + "." + name

        @functools.wraps(original)
        def timed(*args, **kwargs):
            frame = [0.0, 0.0]
            active.append(frame)
            wall, cpu = time.perf_counter(), time.process_time()
            try:
                return original(*args, **kwargs)
            finally:
                elapsed_wall = time.perf_counter() - wall
                elapsed_cpu = time.process_time() - cpu
                active.pop()
                row = records.setdefault(key, {"calls": 0, "wall_inclusive": 0.0, "cpu_inclusive": 0.0,
                                               "wall_exclusive": 0.0, "cpu_exclusive": 0.0})
                row["calls"] += 1
                row["wall_inclusive"] += elapsed_wall
                row["cpu_inclusive"] += elapsed_cpu
                row["wall_exclusive"] += elapsed_wall - frame[0]
                row["cpu_exclusive"] += elapsed_cpu - frame[1]
                if active:
                    active[-1][0] += elapsed_wall
                    active[-1][1] += elapsed_cpu

        stack.enter_context(patch.object(module, name, timed))

    for name in ("legendre_polynomials", "potential_matrices", "residual_truncation_operator",
                 "_potential_matrices", "_residual_truncation_operator", "_abs_power_action",
                 "potential_moment", "potential_square_moment", "_exact_inner",
                 "_mat_mul_diag_inverse", "_residual_rho", "_mat_add", "_mat_sub", "_mat_scale"):
        if hasattr(assembly, name):
            install(assembly, name)
    for name in ("enumerate_active_prime_power_terms", "_orthogonal_basis_norms", "_sorted_breakpoints",
                 "_legendre_expansions", "_affine_legendre", "_local_basis", "_translation_partition",
                 "_combined_local_images", "_legendre_inner", "_exact_inner", "_low_matrix_from_images",
                 "_operator_square_matrix_from_images", "_tail_gram"):
        # A replacement may remove obsolete helpers; profile only existing operations.
        if hasattr(arithmetic, name):
            install(arithmetic, name)
    for name in ("poly_mul", "potential_moment", "potential_square_moment",
                 "abs_power_action_on_poly", "exact_poly_inner"):
        install(shared, name)


def run_sample(n: int, support: Fraction, precision: int, residual_order: int, mode: str) -> dict[str, object]:
    stages: dict[str, dict[str, float]] = {}
    profiler = cProfile.Profile() if mode == "cprofile" else None
    with ExitStack() as stack:
        if mode == "stages":
            _stage_wrappers(stack, stages)
        wall, cpu = time.perf_counter(), time.process_time()
        if profiler:
            profiler.enable()
        try:
            result = assembly.assemble_multi_prime_schur(
                n=n, prec=precision, residual_order=residual_order,
                support_num=support.numerator, support_den=support.denominator,
                require_positive_mu=False,
            )
        finally:
            if profiler:
                profiler.disable()
        elapsed_wall, elapsed_cpu = time.perf_counter() - wall, time.process_time() - cpu
    row: dict[str, object] = {
        "dimension": n, "precision_bits": precision, "residual_order": residual_order,
        "support": str(support), "mode": mode, "status": "completed",
        "wall_seconds": elapsed_wall, "cpu_seconds": elapsed_cpu,
        "peak_memory_bytes": _peak_memory_bytes(), "stages": stages,
        "active_terms": [term.m for term in result["active_terms"]],
        "mu": str(result["mu"]), "mu_positive": result["mu_positive"],
        "schur_assembled": result["schur"] is not None,
        "theorem_status": False,
    }
    if profiler:
        stats = pstats.Stats(profiler)
        row["profile"] = [
            {"file": key[0], "line": key[1], "function": key[2], "primitive_calls": value[0],
             "calls": value[1], "exclusive_seconds": value[2], "cumulative_seconds": value[3]}
            for key, value in sorted(stats.stats.items(), key=lambda item: item[1][3], reverse=True)[:60]
        ]
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--support", required=True, type=Fraction)
    parser.add_argument("--dimensions", required=True, help="comma-separated dimensions, in execution order")
    parser.add_argument("--precision", type=int, default=128)
    parser.add_argument("--residual-order", type=int, default=32)
    parser.add_argument("--mode", choices=("timing", "stages", "cprofile"), default="timing")
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()
    dimensions = [int(value) for value in args.dimensions.split(",")]
    if args.support <= 0 or any(n < 1 for n in dimensions):
        parser.error("support and dimensions must be positive")
    payload = {
        "provenance": _provenance(),
        "configuration": {
            "support": str(args.support), "dimensions": dimensions,
            "precision_bits": args.precision, "residual_order": args.residual_order,
            "mode": args.mode,
        },
        "status": "running", "active_dimension": None, "samples": [],
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)

    def publish() -> None:
        temporary = args.output_json.with_suffix(args.output_json.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(args.output_json)

    publish()
    for n in dimensions:
        payload["active_dimension"] = n
        publish()
        print(f"START N={n} precision={args.precision} mode={args.mode}", flush=True)
        try:
            row = run_sample(n, args.support, args.precision, args.residual_order, args.mode)
        except Exception as exc:
            payload["status"] = "failed"
            payload["error"] = {"type": type(exc).__name__, "message": str(exc)}
            publish()
            raise
        payload["samples"].append(row)
        publish()
        print(f"DONE N={n} wall={row['wall_seconds']:.3f}s cpu={row['cpu_seconds']:.3f}s", flush=True)
    payload["active_dimension"] = None
    payload["status"] = "completed"
    publish()


if __name__ == "__main__":
    main()
