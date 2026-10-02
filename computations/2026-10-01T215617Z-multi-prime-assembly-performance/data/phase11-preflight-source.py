"""Real component screens and fixed-input overlap controls, not qualification.

Run from the repository with:
uv run --locked python computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase11-preflight-source.py

This source is spawn-safe. It never calls run_driver or the floating scout,
uses no rigorous cache, grants no theorem status, and does not select a frozen
candidate. Control qualification is only the existing helper's local outcome.
"""

from __future__ import annotations

import time

IMPORT_STARTED = time.perf_counter()
import functools
import hashlib
import multiprocessing
import os
import sys
import traceback
from concurrent.futures import as_completed
from contextlib import ExitStack
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Driver import first preserves the production one-thread-per-worker defaults.
from scripts import weil_multi_prime_continuation_driver as driver
from scripts import weil_multi_prime_support_candidate_check as candidate_api
from scripts.cert import exact_prime_schur_common as exact_api
from scripts.continuation_bundle import _atomic_write_json
from scripts.profile_multi_prime_assembly import _peak_memory_bytes, _provenance
from scripts.run_observability import WorkerCleanupVerifier

IMPORT_SECONDS = time.perf_counter() - IMPORT_STARTED
OUTPUT = Path(__file__).resolve().parent
ROLE = "phase11_real_component_preflight_not_qualification"
BOUNDARY = {
    "role": ROLE,
    "component_only": True,
    "qualification_run": False,
    "canonical_driver_run": False,
    "theorem_status": False,
    "independently_verified": False,
    "whitelisted": False,
    "automatic_promotion": False,
}


def _error(exc):
    row = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
    if isinstance(exc, candidate_api.CandidateStageError):
        row.update({"failure_stage": exc.stage, "audit_inputs": exc.audit_inputs})
    return row


def _measure_call(stack, owner, name, records, label=None):
    original = getattr(owner, name)
    key = label or name

    @functools.wraps(original)
    def measured(*args, **kwargs):
        wall, cpu = time.perf_counter(), time.process_time()
        row = {"call_index": len(records.setdefault(key, [])) + 1, "status": "running"}
        records[key].append(row)
        try:
            value = original(*args, **kwargs)
            row["status"] = "completed"
            return value
        except Exception as exc:
            row.update({"status": "failed", "error_type": type(exc).__name__, "error": str(exc)})
            raise
        finally:
            row["wall_seconds_inclusive"] = time.perf_counter() - wall
            row["cpu_seconds_inclusive"] = time.process_time() - cpu

    stack.enter_context(patch.object(owner, name, measured))


def _screen_worker(dimension):
    """Use the actual sequential ladder and keep its full exact diagnostics."""
    calls = []
    original = driver.scout_support

    @functools.wraps(original)
    def measured_screen(support, *, dimension, prec, residual_order):
        row = {"precision_bits": prec, "status": "running"}
        calls.append(row)
        wall, cpu = time.perf_counter(), time.process_time()
        try:
            result = original(support, dimension=dimension, prec=prec, residual_order=residual_order)
            row["status"] = "completed"
            return result
        except Exception as exc:
            row.update({"status": "failed", "error": _error(exc)})
            raise
        finally:
            row["wall_seconds"] = time.perf_counter() - wall
            row["cpu_seconds"] = time.process_time() - cpu

    row = {
        **BOUNDARY, "dimension": dimension, "support": "11/20", "worker_pid": os.getpid(),
        "worker_parent_pid": os.getppid(), "worker_import_wall_seconds": IMPORT_SECONDS,
        "cache_policy": "none; cache_dir_text=None", "screen_call_timings": calls,
    }
    wall, cpu = time.perf_counter(), time.process_time()
    try:
        with patch.object(driver, "scout_support", measured_screen):
            row["result"] = driver._rigorous_screen_worker(
                Fraction(11, 20), dimension, [128, 256, 384, 512], 32, None, None,
            )
        row["status"] = "completed"
    except Exception as exc:
        row.update({"status": "failed", "error": _error(exc)})
    finally:
        row["wall_seconds"] = time.perf_counter() - wall
        row["worker_cpu_seconds"] = time.process_time() - cpu
        row["worker_peak_memory_bytes"] = _peak_memory_bytes()
    return row


def _control(base_precision, publish):
    """Fresh assembly for each base, then exactly one real 128-bit helper step."""
    label = f"phase11-control-base{base_precision}"
    stages, candidate_calls = {}, []
    original_candidate = driver.run_candidate

    @functools.wraps(original_candidate)
    def measured_candidate(support, **kwargs):
        row = {"support": str(support), "configuration": kwargs.copy(), "status": "running"}
        candidate_calls.append(row)
        wall, cpu = time.perf_counter(), time.process_time()
        try:
            result = original_candidate(support, **kwargs)
            row.update({"status": "completed", "all_margins_positive": result["all_margins_positive"]})
            return result
        except Exception as exc:
            row.update({"status": "failed", "error": _error(exc)})
            raise
        finally:
            row["wall_seconds"] = time.perf_counter() - wall
            row["cpu_seconds"] = time.process_time() - cpu

    row = {
        **BOUNDARY, "control_role": "one_prime_overlap_positive_control_not_frozen_target",
        "support": "2/5", "active_terms_expected": [2], "dimension": 40, "residual_order": 32,
        "matrix_bits": 64, "witness_bits": 32, "base_precision_bits": base_precision,
        "requested_confirmation_precision_bits": base_precision + 128,
        "precision_step": 128, "extra_steps": 1,
        "control_scope": "one isolated normal step; does not exercise the frozen two-step exhaustion branch",
        "cache_policy": "none; cache_dir=None; separate fresh base assembly for each control",
        "qualified": False, "stage_timings_inclusive": stages, "candidate_call_timings": candidate_calls,
        "audit_artifacts": [],
    }
    wall, cpu = time.perf_counter(), time.process_time()
    try:
        with ExitStack() as stack:
            for name in (
                "assemble_multi_prime_schur", "_active_term_diagnostics", "coarsen_matrix",
                "dyadic_outward_interval", "_exact_multi_prime_schur", "make_witness",
                "arb_matrix_exact_width_diagnostics", "exact_matrix_width_diagnostics",
                "interval_matrix_json", "exact_matrix_json",
            ):
                _measure_call(stack, candidate_api, name, stages)
            for name in ("_exact_ldl_midpoint", "_inverse_lower_triangular", "_exact_congruence", "_gershgorin_margin"):
                _measure_call(stack, exact_api, name, stages, "witness." + name)
            stack.enter_context(patch.object(driver, "run_candidate", measured_candidate))
            base_wall, base_cpu = time.perf_counter(), time.process_time()
            base = driver._construct_candidate(
                Fraction(2, 5), 40, base_precision, 32, [64], [32], None,
            )
            row["base_candidate"] = base
            row["base_construction_wall_seconds"] = time.perf_counter() - base_wall
            row["base_construction_cpu_seconds"] = time.process_time() - base_cpu
            if base["status"] == "candidate_ready":
                confirm_wall, confirm_cpu = time.perf_counter(), time.process_time()
                try:
                    confirmation = driver._confirm_candidate_precision_stability(
                        Fraction(2, 5), 40, base, 32,
                        precision_step=128, extra_steps=1, cache_dir=None,
                    )
                finally:
                    row["confirmation_helper_wall_seconds"] = time.perf_counter() - confirm_wall
                    row["confirmation_helper_cpu_seconds"] = time.process_time() - confirm_cpu
                row["confirmation"] = confirmation
                row["qualified"] = confirmation["qualified"]
                row["status"] = "completed"
            else:
                row["status"] = "base_candidate_not_ready"
                row["confirmation"] = None
    except Exception as exc:
        row.update({"status": "failed", "error": _error(exc)})
    finally:
        row["component_wall_seconds_excluding_publication"] = time.perf_counter() - wall
        row["component_cpu_seconds_excluding_publication"] = time.process_time() - cpu
        row["parent_peak_memory_bytes"] = _peak_memory_bytes()

    # CandidateStageError retains exact audit inputs when that stage reached serialization.
    # Keep separate full artifacts, never stringify Arb/Fraction values or trim matrices.
    base_attempts = row.get("base_candidate", {}).get("attempts", [])
    higher_attempts = (row.get("confirmation") or {}).get("attempts", [])[1:]
    for kind, attempts in (("base", base_attempts), ("confirmation", higher_attempts)):
        for index, attempt in enumerate(attempts, 1):
            inputs = attempt.get("audit_inputs")
            if inputs is not None:
                filename = f"{label}-{kind}-attempt{index}-audit-inputs.json"
                publication = publish(filename, inputs)
                row["audit_artifacts"].append(publication)
    publication = publish(label + ".json", row)
    return row, publication


def main():
    planned = ["phase11-preflight.json"]
    for precision in (512, 640):
        label = f"phase11-control-base{precision}"
        planned += [label + ".json", label + "-base-attempt1-audit-inputs.json",
                    label + "-confirmation-attempt1-audit-inputs.json"]
    existing = [name for name in planned if (OUTPUT / name).exists()]
    if existing:
        raise FileExistsError(f"Refusing to replace prior preflight outputs: {existing}")

    wall, cpu = time.perf_counter(), time.process_time()
    verifier = WorkerCleanupVerifier()
    payload = {
        **BOUNDARY, "status": "running", "parent_pid": os.getpid(),
        "configuration": {"support": "11/20", "active_terms": [2, 3], "dimensions": [192, 196],
                          "precision_ladder": [128, 256, 384, 512], "residual_order": 32,
                          "rigorous_workers": 2, "worker_model": driver.PROCESS_WORKER_MODEL,
                          "cache_policy": "none; all screen/base/confirmation calls recompute"},
        "parent_import_wall_seconds": IMPORT_SECONDS, "provenance": _provenance(),
        "screens": [], "completion_observation_order": [], "worker_pids": [],
        "worker_cleanup_events": [], "controls": [], "publications": [],
        "timing_scope": "Parent CPU excludes worker CPU. Worker ladder time excludes spawn, IPC and shutdown. Nested stage timings are inclusive and must not be summed. Final preflight publication is excluded from its own report.",
        "unmeasured": ["interpreter launch before module execution", "isolated IPC serialization time",
                       "peak live aggregate worker memory", "independent OS process scan"],
    }
    payload["provenance"]["cache_policy"] = "no rigorous cache; component preflight only"
    payload["provenance"]["continuation_source_fingerprint"] = driver._cache_source_fingerprint()
    payload["provenance"]["runner_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for relative in ("scripts/weil_multi_prime_continuation_driver.py",
                     "scripts/weil_multi_prime_support_candidate_check.py",
                     "scripts/weil_multi_prime_support_continuation_scout.py",
                     "scripts/run_observability.py", "scripts/continuation_bundle.py"):
        payload["provenance"]["source_sha256"][relative] = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()

    def publish(filename, result):
        started, cpu_started = time.perf_counter(), time.process_time()
        digest, size = _atomic_write_json(OUTPUT / filename, result)
        row = {"path": filename, "sha256": digest, "bytes": size,
               "wall_seconds": time.perf_counter() - started,
               "parent_cpu_seconds": time.process_time() - cpu_started}
        payload["publications"].append(row)
        return row

    def cleanup_event(event, detail):
        payload["worker_cleanup_events"].append({"event": event, "detail": detail,
                                                "parent_elapsed_seconds": time.perf_counter() - wall})

    publish("phase11-preflight.json", payload)
    try:
        pool_started = time.perf_counter()
        with driver._verified_process_pool(
            2, stage="PHASE11_COMPONENT_RIGOROUS_SCREEN", verifier=verifier, event_sink=cleanup_event,
        ) as executor:
            entered = time.perf_counter()
            futures = {executor.submit(_screen_worker, dimension): dimension for dimension in (192, 196)}
            submitted = time.perf_counter()
            results = {}
            for future in as_completed(futures):
                dimension = futures[future]
                try:
                    results[dimension] = future.result()
                except Exception as exc:
                    results[dimension] = {**BOUNDARY, "dimension": dimension, "status": "failed", "error": _error(exc)}
                payload["completion_observation_order"].append(dimension)
                payload["screens"] = [results[n] for n in sorted(results)]
                publish("phase11-preflight.json", payload)
            collected = time.perf_counter()
            payload["worker_pids"] = [process.pid for process in executor._processes.values()]
        stopped = time.perf_counter()
        payload["rigorous_lifecycle_timing"] = {
            "wall_seconds_including_lifecycle_and_progress_publication": stopped - pool_started,
            "pool_construction_and_entry_seconds": entered - pool_started,
            "submission_seconds": submitted - entered,
            "collection_and_progress_publication_seconds": collected - submitted,
            "shutdown_and_cleanup_verification_seconds": stopped - collected,
            "note": "Spawn/import and IPC overlap collection; construction time is not spawn startup time.",
        }
        payload["worker_cleanup"] = verifier.verify()
        payload["worker_cleanup_verified"] = payload["worker_cleanup"]["verified"]
        payload["worker_shutdown_records"] = verifier.shutdown_records
        payload["active_children_after_cleanup"] = len(multiprocessing.active_children())
        if payload["active_children_after_cleanup"] != 0:
            raise RuntimeError("Active children remain after owned pool cleanup; no unrelated process is terminated")
        publish("phase11-preflight.json", payload)
        for base_precision in (512, 640):
            control, publication = _control(base_precision, publish)
            payload["controls"].append({"result": control, "publication": publication})
            publish("phase11-preflight.json", payload)
        component_failed = any(row["status"] != "completed" for row in payload["screens"])
        component_failed |= any(row["result"]["status"] != "completed" for row in payload["controls"])
        payload["status"] = "completed_with_component_failures" if component_failed else "completed"
    except BaseException as exc:
        payload.update({"status": "failed", "error": _error(exc)})
        payload["worker_shutdown_records"] = verifier.shutdown_records
        payload["active_children_after_cleanup"] = len(multiprocessing.active_children())
        payload.setdefault("worker_cleanup_verified", False)
        raise
    finally:
        payload["wall_seconds_excluding_final_publication"] = time.perf_counter() - wall
        payload["parent_cpu_seconds_excluding_final_publication"] = time.process_time() - cpu
        payload["parent_peak_memory_bytes"] = _peak_memory_bytes()
        _atomic_write_json(OUTPUT / "phase11-preflight.json", payload)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
