"""Manual component-cost benchmarks, never a continuation qualification.

Assembly throughput uses the driver's verified spawn-pool lifecycle. Candidate
cases are sequential. Scout mode measures only the floating component. No mode
calls run_driver(), selects a candidate, uses a cache, or seals a qualification.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import time
from concurrent.futures import as_completed
from contextlib import ExitStack
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

# Import the driver first to preserve its one-thread-per-worker defaults.
from scripts import weil_multi_prime_continuation_driver as driver
from scripts import weil_multi_prime_support_candidate_check as candidate
from scripts.continuation_bundle import _atomic_write_json
from scripts.profile_multi_prime_assembly import _peak_memory_bytes, _provenance, run_sample
from scripts.run_observability import WorkerCleanupVerifier


def _candidate_sample(n, support, precision, order, matrix_bits, witness_bits):
    stages = {}
    assembled = None

    def install(stack, name):
        original = getattr(candidate, name)

        @functools.wraps(original)
        def measured(*args, **kwargs):
            nonlocal assembled
            wall, cpu = time.perf_counter(), time.process_time()
            print(f"STAGE START N={n} {name}", flush=True)
            try:
                value = original(*args, **kwargs)
                if name == "assemble_multi_prime_schur":
                    assembled = value
                return value
            finally:
                row = stages.setdefault(name, {"calls": 0, "wall_inclusive": 0.0, "cpu_inclusive": 0.0})
                row["calls"] += 1
                row["wall_inclusive"] += time.perf_counter() - wall
                row["cpu_inclusive"] += time.process_time() - cpu
                print(f"STAGE DONE N={n} {name} cumulative={row['wall_inclusive']:.3f}s", flush=True)

        stack.enter_context(patch.object(candidate, name, measured))

    wall, cpu = time.perf_counter(), time.process_time()
    with ExitStack() as stack:
        for name in ("assemble_multi_prime_schur", "_active_term_diagnostics", "coarsen_matrix",
                     "dyadic_outward_interval", "_exact_multi_prime_schur", "make_witness"):
            install(stack, name)
        try:
            result = candidate.run_candidate(
                support, dimension=n, prec=precision, residual_order=order,
                matrix_bits=matrix_bits, witness_bits=witness_bits,
            )
            outcome = result["status"]
            error = None
        except candidate.CandidateStageError as exc:
            result = None
            outcome = f"{exc.stage}_failed"
            error = {"type": type(exc).__name__, "stage": exc.stage, "message": str(exc)}
    elapsed_wall, elapsed_cpu = time.perf_counter() - wall, time.process_time() - cpu
    native_widths = {
        name: candidate.fraction_text(candidate._matrix_max_width_fraction(assembled[name]))
        for name in ("A", "GV", "GP", "GR", "P", "P_squared", "schur")
        if assembled[name] is not None
    }
    return {
        "dimension": n, "precision_bits": precision, "residual_order": order,
        "matrix_bits": matrix_bits, "witness_bits": witness_bits, "support": str(support),
        "status": "completed", "candidate_outcome": outcome, "error": error,
        "wall_seconds": elapsed_wall, "cpu_seconds": elapsed_cpu,
        "peak_memory_bytes": _peak_memory_bytes(), "stages": stages, "result": result,
        "theorem_status": False,
        "post_timing_native_max_widths": native_widths,
        "post_timing_mu_enclosure": candidate._fraction_interval_text(assembled["mu"]),
    }


def _scout_sample(support, dimensions, resolution):
    wall, cpu = time.perf_counter(), time.process_time()
    result = driver._scout_resolution_worker(support, dimensions, resolution)
    return {
        "resolution": resolution.as_dict(), "status": "completed",
        "wall_seconds": time.perf_counter() - wall, "cpu_seconds": time.process_time() - cpu,
        "peak_memory_bytes": _peak_memory_bytes(), "pid": os.getpid(),
        "result": result, "theorem_status": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=("throughput", "candidate", "scout"))
    parser.add_argument("--support", required=True, type=Fraction)
    parser.add_argument("--dimensions", required=True)
    parser.add_argument("--precision", type=int, default=512)
    parser.add_argument("--residual-order", type=int, default=32)
    parser.add_argument("--matrix-bits", type=int, default=64)
    parser.add_argument("--witness-bits", type=int, default=32)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--scout-resolutions", type=int, default=8)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()
    dimensions = [int(value) for value in args.dimensions.split(",")]
    if args.support <= 0 or not dimensions or any(n < 1 for n in dimensions):
        parser.error("support and dimensions must be positive")
    if len(dimensions) != len(set(dimensions)):
        parser.error("dimensions must be unique")
    if not 1 <= args.workers <= (3 if args.mode == "scout" else 2):
        parser.error("workers must respect the driver's bounded 3/2 pools")
    provenance = _provenance()
    root = Path(__file__).resolve().parents[1]
    provenance["source_sha256"].update({
        relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for relative in driver.CACHE_SOURCE_PATHS
    })
    relative = "scripts/profile_multi_prime_workflow.py"
    provenance["source_sha256"][relative] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    provenance["continuation_source_fingerprint"] = driver._cache_source_fingerprint()
    provenance["cache_policy"] = "no continuation cache; diagnostic components only"
    payload = {
        "role": "manual_multi_prime_component_cost_benchmark", "theorem_status": False,
        "provenance": provenance, "configuration": vars(args) | {
            "support": str(args.support), "dimensions": dimensions, "output_json": str(args.output_json),
            "workers": 1 if args.mode == "candidate" else args.workers,
        },
        "status": "running", "active_dimension": None, "samples": [],
        "completion_observation_order": [], "progress_publications": [],
        "publication_scope": "JSON serialization/hash/fsync/atomic writes; final report publication excluded",
    }

    def publish(*, measure=True):
        wall, cpu = time.perf_counter(), time.process_time()
        digest, size = _atomic_write_json(args.output_json, payload)
        if measure:
            payload["progress_publications"].append({
                "wall_seconds": time.perf_counter() - wall,
                "cpu_seconds": time.process_time() - cpu, "bytes": size, "sha256": digest,
            })

    publish()
    started, cpu_started = time.perf_counter(), time.process_time()
    try:
        if args.mode == "candidate":
            for n in dimensions:
                payload["active_dimension"] = n
                publish()
                print(f"START candidate N={n} precision={args.precision} bits={args.matrix_bits}/{args.witness_bits}", flush=True)
                row = _candidate_sample(n, args.support, args.precision, args.residual_order,
                                        args.matrix_bits, args.witness_bits)
                payload["samples"].append(row)
                payload["completion_observation_order"].append(n)
                publish()
                print(f"DONE candidate N={n} wall={row['wall_seconds']:.3f}s outcome={row['candidate_outcome']}", flush=True)
        else:
            verifier = WorkerCleanupVerifier()
            results = {}
            stage = "manual-diagnostic-" + args.mode
            with driver._verified_process_pool(args.workers, stage=stage, verifier=verifier) as executor:
                if args.mode == "throughput":
                    futures = {
                        executor.submit(run_sample, n, args.support, args.precision,
                                        args.residual_order, "timing"): n for n in dimensions
                    }
                else:
                    futures = {
                        executor.submit(_scout_sample, args.support, dimensions, resolution): resolution.level
                        for resolution in driver.build_scout_resolutions(dimensions, args.scout_resolutions)
                    }
                for future in as_completed(futures):
                    identity = futures[future]
                    results[identity] = future.result()
                    payload["completion_observation_order"].append(identity)
                    payload["samples"] = [results[key] for key in sorted(results)]
                    publish()
                    print(f"DONE {args.mode} identity={identity} wall={results[identity]['wall_seconds']:.3f}s", flush=True)
                payload["worker_pids"] = [process.pid for process in executor._processes.values()]
            payload["worker_cleanup"] = verifier.verify()
            payload["worker_shutdown_records"] = verifier.shutdown_records
            payload["worker_model"] = driver.PROCESS_WORKER_MODEL
        payload["wall_seconds_including_lifecycle"] = time.perf_counter() - started
        payload["parent_cpu_seconds"] = time.process_time() - cpu_started
        payload["parent_peak_memory_bytes"] = _peak_memory_bytes()
        payload["status"] = "completed"
        payload["active_dimension"] = None
        publish(measure=False)
    except BaseException as exc:
        payload["status"] = "failed"
        payload["error"] = {"type": type(exc).__name__, "message": str(exc)}
        publish(measure=False)
        raise


if __name__ == "__main__":
    main()
