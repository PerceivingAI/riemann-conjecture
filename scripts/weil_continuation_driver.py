#!/usr/bin/env python3
"""Canonical pre-theorem driver for one-prime support continuation.

The driver runs the existing reconnaissance and generator-side exact candidate
checks for explicitly supplied dimensions. It never extrapolates dimensions,
invokes the theorem certificate exporter, edits the closed contract, or grants
theorem status. ``CANDIDATE_READY`` means that a fresh independent verifier run
is still required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from enum import StrEnum
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Iterator

# Keep each numerical worker single-threaded by default so process-level
# parallelism does not oversubscribe BLAS/OpenMP. Explicit user settings win.
for _thread_env in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ.setdefault(_thread_env, "1")

from scripts.continuation_bundle import (
    collect_runtime_provenance,
    remove_continuation_manifest,
    utc_now,
    write_continuation_bundle,
)
from scripts.run_observability import (
    OutputDirectoryLock,
    OutputDirectoryLockedError,
    PROCESS_WORKER_MODEL,
    RunStatusWriter,
    WorkerCleanupVerifier,
    write_run_identity,
)
from scripts.weil_legendre_schur_scout import scout
from scripts.cert.constants import require_one_prime_support
from scripts.weil_support_candidate_check import (
    CandidateStageError,
    run_candidate,
    theorem_boundary_payload,
)
from scripts.weil_support_continuation_scout import scout_support


DRIVER_VERSION = "continuation-driver-p15-v1"
SCOUT_RELATIVE_CONVERGENCE_TOLERANCE = 1e-2
CANDIDATE_MARGIN_RELATIVE_STABILITY_TOLERANCE = 1e-3
CANDIDATE_PRECISION_STEP_DEFAULT = 128
CANDIDATE_PRECISION_EXTRA_STEPS_DEFAULT = 2
CLI_SCOUT_WORKERS_MAX = 3
CLI_RIGOROUS_WORKERS_MAX = 2
PRECISION_STATUS_INSUFFICIENT = "INSUFFICIENT_PRECISION"
PRECISION_STATUS_STABLE = "PRECISION_STABLE"
PRECISION_STATUS_MATHEMATICAL_NEGATIVE = "MATHEMATICAL_NEGATIVE"
PRECISION_STATUS_ASSEMBLY_FAILED = "ASSEMBLY_FAILED"
OBSERVABILITY_LIST_PREVIEW_LIMIT = 16
OBSERVABILITY_STRING_LIMIT = 500


@dataclass(frozen=True)
class LiveProgress:
    """Emit short elapsed-time progress lines to stderr and flush immediately."""

    enabled: bool = True
    started_monotonic: float = field(default_factory=time.monotonic)

    def emit(self, message: str) -> None:
        if not self.enabled:
            return
        elapsed = max(0, int(time.monotonic() - self.started_monotonic))
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        try:
            sys.stderr.write(
                f"[{hours:02d}:{minutes:02d}:{seconds:02d}] {message}\n"
            )
            sys.stderr.flush()
        except (OSError, ValueError, AttributeError):
            # Live stderr is advisory. The durable .live state remains the
            # authoritative observability channel, so a closed/broken stderr
            # must never invalidate mathematical work or bundle finalization.
            return


def _bounded_observability_value(value: object) -> object:
    """Bound live-only payloads without changing retained mathematical results."""
    if isinstance(value, str):
        if len(value) <= OBSERVABILITY_STRING_LIMIT:
            return value
        return value[:OBSERVABILITY_STRING_LIMIT] + "..."
    if isinstance(value, dict):
        return {
            str(key): _bounded_observability_value(nested)
            for key, nested in value.items()
        }
    if isinstance(value, (list, tuple)):
        preview = [
            _bounded_observability_value(nested)
            for nested in value[:OBSERVABILITY_LIST_PREVIEW_LIMIT]
        ]
        if len(value) <= OBSERVABILITY_LIST_PREVIEW_LIMIT:
            return preview
        return {
            "count": len(value),
            "preview": preview,
            "truncated": True,
        }
    return value


def _dimension_progress_text(dimensions: list[int]) -> str:
    if len(dimensions) == 1:
        return str(dimensions[0])
    if len(dimensions) >= 2:
        step = dimensions[1] - dimensions[0]
        if step > 0 and dimensions == list(range(dimensions[0], dimensions[-1] + 1, step)):
            return f"{dimensions[0]}..{dimensions[-1]} step={step}"
    return ",".join(str(dimension) for dimension in dimensions)


class WorkflowState(StrEnum):
    VALIDATE_INPUT = "VALIDATE_INPUT"
    FLOAT_SCOUT = "FLOAT_SCOUT"
    CHECK_SCOUT_STABILITY = "CHECK_SCOUT_STABILITY"
    SELECT_DIMENSION = "SELECT_DIMENSION"
    RIGOROUS_PRECISION_SEARCH = "RIGOROUS_PRECISION_SEARCH"
    CHECK_RIGOROUS_STABILITY = "CHECK_RIGOROUS_STABILITY"
    EXACT_ROUNDING_SEARCH = "EXACT_ROUNDING_SEARCH"
    EXACT_WITNESS_CHECK = "EXACT_WITNESS_CHECK"
    CANDIDATE_PRECISION_CONFIRMATION = "CANDIDATE_PRECISION_CONFIRMATION"
    NO_CANDIDATE = "NO_CANDIDATE"
    SCOUT_UNSTABLE = "SCOUT_UNSTABLE"
    RIGOROUS_ASSEMBLY_FAILED = "RIGOROUS_ASSEMBLY_FAILED"
    PRECISION_LIMIT_REACHED = "PRECISION_LIMIT_REACHED"
    ROUNDING_FAILED = "ROUNDING_FAILED"
    WITNESS_FAILED = "WITNESS_FAILED"
    CANDIDATE_CHECK_FAILED = "CANDIDATE_CHECK_FAILED"
    CANDIDATE_READY = "CANDIDATE_READY"


TERMINAL_WORKFLOW_STATES = {
    WorkflowState.NO_CANDIDATE,
    WorkflowState.SCOUT_UNSTABLE,
    WorkflowState.RIGOROUS_ASSEMBLY_FAILED,
    WorkflowState.PRECISION_LIMIT_REACHED,
    WorkflowState.ROUNDING_FAILED,
    WorkflowState.WITNESS_FAILED,
    WorkflowState.CANDIDATE_CHECK_FAILED,
    WorkflowState.CANDIDATE_READY,
}
FINAL_STATES = {state.value for state in TERMINAL_WORKFLOW_STATES}

ALLOWED_WORKFLOW_TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
    WorkflowState.VALIDATE_INPUT: {WorkflowState.FLOAT_SCOUT},
    WorkflowState.FLOAT_SCOUT: {WorkflowState.CHECK_SCOUT_STABILITY},
    WorkflowState.CHECK_SCOUT_STABILITY: {
        WorkflowState.SELECT_DIMENSION,
        WorkflowState.NO_CANDIDATE,
        WorkflowState.SCOUT_UNSTABLE,
    },
    WorkflowState.SELECT_DIMENSION: {WorkflowState.RIGOROUS_PRECISION_SEARCH},
    WorkflowState.RIGOROUS_PRECISION_SEARCH: {WorkflowState.CHECK_RIGOROUS_STABILITY},
    WorkflowState.CHECK_RIGOROUS_STABILITY: {
        WorkflowState.EXACT_ROUNDING_SEARCH,
        WorkflowState.NO_CANDIDATE,
        WorkflowState.RIGOROUS_ASSEMBLY_FAILED,
        WorkflowState.PRECISION_LIMIT_REACHED,
    },
    WorkflowState.EXACT_ROUNDING_SEARCH: {
        WorkflowState.EXACT_WITNESS_CHECK,
        WorkflowState.ROUNDING_FAILED,
        WorkflowState.CANDIDATE_CHECK_FAILED,
    },
    WorkflowState.EXACT_WITNESS_CHECK: {
        WorkflowState.CANDIDATE_PRECISION_CONFIRMATION,
        WorkflowState.WITNESS_FAILED,
        WorkflowState.CANDIDATE_CHECK_FAILED,
    },
    WorkflowState.CANDIDATE_PRECISION_CONFIRMATION: {
        WorkflowState.CANDIDATE_READY,
        WorkflowState.PRECISION_LIMIT_REACHED,
        WorkflowState.CANDIDATE_CHECK_FAILED,
    },
    **{state: set() for state in TERMINAL_WORKFLOW_STATES},
}


@dataclass
class ContinuationStateMachine:
    """Fail-closed execution state for one continuation-driver run."""

    current: WorkflowState = WorkflowState.VALIDATE_INPUT
    transitions: list[dict[str, object]] = field(default_factory=list)

    def transition(
        self,
        target: WorkflowState,
        *,
        reason: str,
        details: dict[str, object] | None = None,
    ) -> None:
        allowed = ALLOWED_WORKFLOW_TRANSITIONS[self.current]
        if target not in allowed:
            raise RuntimeError(
                f"invalid continuation transition {self.current.value} -> {target.value}"
            )
        self.transitions.append(
            {
                "sequence": len(self.transitions) + 1,
                "from": self.current.value,
                "to": target.value,
                "reason": reason,
                "details": details or {},
            }
        )
        self.current = target

    def require_terminal(self) -> WorkflowState:
        if self.current not in TERMINAL_WORKFLOW_STATES:
            raise RuntimeError(
                f"continuation workflow ended in non-terminal state {self.current.value}"
            )
        return self.current

    def trace(self) -> list[dict[str, object]]:
        return [
            {
                "sequence": 0,
                "from": None,
                "to": WorkflowState.VALIDATE_INPUT.value,
                "reason": "driver_started",
                "details": {},
            },
            *self.transitions,
        ]


@dataclass(frozen=True)
class ScoutDimensionResult:
    dimension: int
    mu_scout: float
    finite_block_min_eigenvalue: float
    truncated_factor3_schur_min_eigenvalue: float
    max_mode: int
    quadrature_order: int
    shift_order: int
    status: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ScoutResolution:
    level: int
    max_mode: int
    quadrature_order: int
    shift_order: int

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _spawn_process_pool(max_workers: int) -> ProcessPoolExecutor:
    """Create an isolated spawn-based pool for numerical research workers."""
    return ProcessPoolExecutor(
        max_workers=max_workers,
        mp_context=multiprocessing.get_context(PROCESS_WORKER_MODEL),
    )


@contextmanager
def _verified_process_pool(
    max_workers: int,
    *,
    stage: str,
    verifier: WorkerCleanupVerifier,
    event_sink: Callable[[str, dict[str, object]], None] | None = None,
) -> Iterator[ProcessPoolExecutor]:
    """Run one process pool and harden cleanup after normal executor shutdown returns."""
    executor = _spawn_process_pool(max_workers)
    verifier.executor_started(stage)
    processes: list[Any] | None = None
    body_error: BaseException | None = None
    try:
        with executor:
            try:
                yield executor
            finally:
                raw_processes = getattr(executor, "_processes", None)
                if isinstance(raw_processes, dict):
                    processes = list(raw_processes.values())
    except BaseException as exc:
        body_error = exc
        raise
    finally:
        try:
            verifier.executor_stopped(
                stage,
                processes,
                active_children_provider=multiprocessing.active_children,
                event_sink=event_sink,
            )
        except Exception as cleanup_exc:
            if body_error is None:
                raise
            body_error.add_note(
                "executor cleanup also failed: "
                f"{type(cleanup_exc).__name__}: {cleanup_exc}"
            )


def _freeze_result_payload(result: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """Deep-copy the terminal result through JSON and return its immutable-content digest."""
    encoded = json.dumps(result, separators=(",", ":"), allow_nan=False).encode("utf-8")
    frozen = json.loads(encoded.decode("utf-8"))
    if not isinstance(frozen, dict):
        raise TypeError("terminal result must freeze to a JSON object")
    return frozen, hashlib.sha256(encoded).hexdigest()


def _scout_resolution_worker(
    support: Fraction,
    dimensions: list[int],
    resolution: ScoutResolution,
) -> dict[str, object]:
    """Run one independent floating-scout resolution in a child process."""
    return scout(
        max_mode=resolution.max_mode,
        quadrature_order=resolution.quadrature_order,
        shift_order=resolution.shift_order,
        n_values=dimensions,
        support=support,
    )


def _rigorous_screen_worker(
    support: Fraction,
    dimension: int,
    precisions: list[int],
    residual_order: int,
    cache_dir_text: str | None,
    progress: LiveProgress | None,
) -> dict[str, object]:
    """Run one dimension's sequential precision ladder in a child process."""
    cache_dir = Path(cache_dir_text) if cache_dir_text is not None else None
    if progress is None:
        return _escalate_rigorous_screen(
            support,
            dimension,
            precisions,
            residual_order,
            cache_dir,
        )
    return _escalate_rigorous_screen(
        support,
        dimension,
        precisions,
        residual_order,
        cache_dir,
        progress=progress,
    )


def parse_support(text: str) -> Fraction:
    """Parse a positive support value exactly, without a float round-trip."""
    token = text.strip()
    if not token:
        raise ValueError("support must be a non-empty exact rational")
    try:
        support = Fraction(token)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("support must be an exact rational") from exc
    if support <= 0:
        raise ValueError("support must be positive")
    return support


def parse_dimensions(text: str) -> list[int]:
    dimensions: list[int] = []
    for part in text.split(","):
        token = part.strip()
        if not token:
            continue
        value = int(token)
        if value < 1:
            raise ValueError("dimensions must be positive")
        dimensions.append(value)
    if not dimensions:
        raise ValueError("at least one dimension is required")
    if len(set(dimensions)) != len(dimensions):
        raise ValueError("dimensions must be unique")
    return dimensions


def dimensions_from_args(args: argparse.Namespace) -> list[int]:
    explicit = args.n is not None
    ranged = any(value is not None for value in (args.n_min, args.n_max, args.n_step))
    if explicit == ranged:
        raise ValueError("provide either --n or the complete --n-min/--n-max/--n-step range")
    if explicit:
        return parse_dimensions(args.n)
    if args.n_min is None or args.n_max is None or args.n_step is None:
        raise ValueError("--n-min, --n-max, and --n-step must be supplied together")
    if args.n_min < 1 or args.n_max < args.n_min or args.n_step < 1:
        raise ValueError("invalid dimension range")
    return list(range(args.n_min, args.n_max + 1, args.n_step))


def build_scout_resolutions(
    dimensions: list[int], count: int = 3
) -> list[ScoutResolution]:
    if not dimensions:
        raise ValueError("at least one dimension is required")
    if count < 2:
        raise ValueError("at least two scout resolutions are required")
    maximum = max(dimensions)
    base_mode = max(120, maximum + 40)
    base_quadrature = max(4 * maximum + 380, 4 * base_mode + 220)
    base_shift = max(2 * maximum + 190, 2 * base_mode + 110)
    return [
        ScoutResolution(
            level=level,
            max_mode=base_mode + 40 * level,
            quadrature_order=base_quadrature + 160 * level,
            shift_order=base_shift + 80 * level,
        )
        for level in range(count)
    ]



def build_precision_ladder(start: int = 128, maximum: int = 512) -> list[int]:
    if start < 64 or maximum < start:
        raise ValueError("precision ladder requires 64 <= start <= maximum")
    standard = [128, 256, 384, 512, 640, 768, 1024]
    ladder = [precision for precision in standard if start <= precision <= maximum]
    if not ladder or ladder[0] != start:
        ladder.insert(0, start)
    if ladder[-1] != maximum:
        ladder.append(maximum)
    return ladder


CACHE_VERSION = "continuation-driver-v6"
CACHE_SOURCE_PATHS = (
    "scripts/weil_continuation_driver.py",
    "scripts/weil_legendre_schur_scout.py",
    "scripts/weil_support_continuation_scout.py",
    "scripts/weil_support_candidate_check.py",
    "scripts/precision_diagnostics.py",
    "scripts/cert/exact_prime_schur_common.py",
    "scripts/cert/legendre_schur.py",
    "scripts/cert/residual_kernel.py",
    "scripts/cert/matrices.py",
    "scripts/cert/constants.py",
    "uv.lock",
)


def _cache_source_fingerprint() -> str:
    """Hash every source/input that can change continuation semantics."""
    root = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    for relative_path in CACHE_SOURCE_PATHS:
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update((root / relative_path).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _cached_result(
    cache_dir: Path | None,
    key: dict[str, object],
    producer: Callable[[], dict[str, object]],
) -> tuple[dict[str, object], bool]:
    if cache_dir is None:
        return producer(), False
    encoded = json.dumps(
        {
            "version": CACHE_VERSION,
            "source_fingerprint": _cache_source_fingerprint(),
            **key,
        },
        sort_keys=True,
    ).encode()
    cache_path = cache_dir / (hashlib.sha256(encoded).hexdigest() + ".json")
    try:
        return json.loads(cache_path.read_text(encoding="utf-8")), True
    except (FileNotFoundError, json.JSONDecodeError):
        result = producer()
        cache_dir.mkdir(parents=True, exist_ok=True)
        temporary = cache_path.with_name(f"{cache_path.name}.{os.getpid()}.tmp")
        try:
            temporary.write_text(
                json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
            )
            temporary.replace(cache_path)
        finally:
            temporary.unlink(missing_ok=True)
        return result, False



def build_bit_ladder(start: int, maximum: int, step: int) -> list[int]:
    if start < 8 or maximum < start or step < 1:
        raise ValueError("invalid bit ladder")
    values = list(range(start, maximum + 1, step))
    if values[-1] != maximum:
        values.append(maximum)
    return values
def _scout_status(row: ScoutDimensionResult) -> str:
    if (
        row.mu_scout <= 0
        or row.finite_block_min_eigenvalue <= 0
        or row.truncated_factor3_schur_min_eigenvalue <= 0
    ):
        return "negative"
    return "positive"


def _typed_scout_rows(
    raw: dict[str, object],
    *,
    max_mode: int,
    quadrature_order: int,
    shift_order: int,
) -> list[ScoutDimensionResult]:
    raw_rows = raw["schur_rows"]
    if not isinstance(raw_rows, list):
        raise TypeError("scout result has no schur rows")
    rows: list[ScoutDimensionResult] = []
    for raw_row in raw_rows:
        if not isinstance(raw_row, dict):
            raise TypeError("scout result contains an invalid row")
        row = ScoutDimensionResult(
            dimension=int(raw_row["N"]),
            mu_scout=float(raw_row["mu_scout"]),
            finite_block_min_eigenvalue=float(raw_row["finite_block_min_eigenvalue"]),
            truncated_factor3_schur_min_eigenvalue=float(
                raw_row["factor3_truncated_schur_min_eigenvalue"]
            ),
            max_mode=max_mode,
            quadrature_order=quadrature_order,
            shift_order=shift_order,
            status="",
        )
        rows.append(
            ScoutDimensionResult(
                **{**row.as_dict(), "status": _scout_status(row)}
            )
        )
    return rows


def _classify_reconnaissance(rows: list[ScoutDimensionResult]) -> str:
    import math

    if any(
        not all(
            math.isfinite(value)
            for value in (
                row.mu_scout,
                row.finite_block_min_eigenvalue,
                row.truncated_factor3_schur_min_eigenvalue,
            )
        )
        for row in rows
    ):
        return "unstable"
    finite_signs = [row.finite_block_min_eigenvalue > 0 for row in rows]
    schur_signs = [
        row.truncated_factor3_schur_min_eigenvalue > 0 for row in rows
    ]
    if (
        any(sign != finite_signs[0] for sign in finite_signs[1:])
        or any(sign != schur_signs[0] for sign in schur_signs[1:])
    ):
        return "unstable"
    if not schur_signs[0]:
        return "negative"
    if any(row.mu_scout <= 0 for row in rows) or not finite_signs[0]:
        return "negative"
    for previous, current in zip(rows, rows[1:]):
        scale = max(
            abs(previous.truncated_factor3_schur_min_eigenvalue),
            abs(current.truncated_factor3_schur_min_eigenvalue),
            1e-12,
        )
        if (
            abs(
                current.truncated_factor3_schur_min_eigenvalue
                - previous.truncated_factor3_schur_min_eigenvalue
            )
            > SCOUT_RELATIVE_CONVERGENCE_TOLERANCE * scale
        ):
            return "unstable"
    return "stable_positive"



def _precision_pair_diagnostics(
    previous: dict[str, object], current: dict[str, object]
) -> dict[str, object]:
    def change(name: str) -> float | None:
        if name not in previous or name not in current:
            return None
        return abs(float(current[name]) - float(previous[name]))

    width_names = (
        "A_max",
        "GV_max",
        "G2_max",
        "GR_max",
        "mu",
        "rho_R",
        "residual_remainder",
    )
    previous_widths = previous.get("interval_widths", {})
    current_widths = current.get("interval_widths", {})
    if not isinstance(previous_widths, dict) or not isinstance(current_widths, dict):
        raise ValueError("rigorous result is missing interval widths")
    width_changes = {
        name: float(current_widths[name]) - float(previous_widths[name])
        for name in width_names
    }
    signs = {
        "mu_lower_positive": (float(current["mu_lower"]) > 0)
        == (float(previous["mu_lower"]) > 0),
        "finite_block_positive": (
            float(current["finite_block_min_eigenvalue_midpoint"]) > 0
        )
        == (float(previous["finite_block_min_eigenvalue_midpoint"]) > 0),
        "schur_positive": (float(current["schur_min_eigenvalue_midpoint"]) > 0)
        == (float(previous["schur_min_eigenvalue_midpoint"]) > 0),
    }

    penalty_changes: dict[str, float] | None = None
    previous_penalties = previous.get("component_schur_penalty_operator_norm_midpoint")
    current_penalties = current.get("component_schur_penalty_operator_norm_midpoint")
    if isinstance(previous_penalties, dict) and isinstance(current_penalties, dict):
        penalty_changes = {
            name: abs(float(current_penalties[name]) - float(previous_penalties[name]))
            for name in ("GV", "G2", "GR")
        }

    return {
        "from_precision_bits": previous["precision_bits"],
        "to_precision_bits": current["precision_bits"],
        "mu_lower_change": change("mu_lower"),
        "mu_midpoint_change": change("mu_midpoint"),
        "finite_block_midpoint_change": change(
            "finite_block_min_eigenvalue_midpoint"
        ),
        "schur_midpoint_change": change("schur_min_eigenvalue_midpoint"),
        "rho_R_upper_change": change("rho_R_upper"),
        "residual_remainder_upper_change": change("residual_remainder_upper"),
        "component_penalty_midpoint_changes": penalty_changes,
        "interval_width_changes": width_changes,
        "widths_reduced": all(delta <= 0 for delta in width_changes.values()),
        "signs_stable": signs,
        "all_key_signs_stable": all(signs.values()),
    }


def _precision_instability_reasons(
    *,
    usable: bool,
    stable_change: bool,
    diagnostics: dict[str, object] | None,
    schur_value: object,
) -> list[str]:
    """Explain why the current Arb result is not yet precision-qualified."""
    reasons: list[str] = []
    if not usable:
        reasons.append("non_finite_key_quantity")
        return reasons
    if diagnostics is None:
        reasons.append("no_prior_precision_for_stability_check")
    else:
        if diagnostics["all_key_signs_stable"] is not True:
            reasons.append("key_sign_changed_at_higher_precision")
        if diagnostics["widths_reduced"] is not True:
            reasons.append("interval_widths_not_reduced")
        if not stable_change:
            reasons.append("midpoint_not_stable")
    if float(schur_value) < 0 and (
        diagnostics is None
        or diagnostics["all_key_signs_stable"] is not True
        or diagnostics["widths_reduced"] is not True
        or not stable_change
    ):
        reasons.append("negative_result_not_precision_stable")
    return reasons


def _mark_previous_precision_contradiction(
    previous: dict[str, object], diagnostics: dict[str, object], stable_change: bool
) -> None:
    if diagnostics["all_key_signs_stable"] is True and stable_change:
        return
    previous["precision_status"] = PRECISION_STATUS_INSUFFICIENT
    reasons = previous.setdefault("precision_reasons", [])
    if not isinstance(reasons, list):
        raise TypeError("precision_reasons must be a list")
    if "contradicted_by_higher_precision" not in reasons:
        reasons.append("contradicted_by_higher_precision")


def _escalate_rigorous_screen(
    support: Fraction,
    dimension: int,
    precisions: list[int],
    residual_order: int,
    cache_dir: Path | None = None,
    *,
    progress: LiveProgress | None = None,
) -> dict[str, object]:
    import math

    attempts: list[dict[str, object]] = []
    pair_diagnostics: list[dict[str, object]] = []
    previous_schur: float | None = None
    previous_result: dict[str, object] | None = None
    for precision in precisions:
        if progress is not None:
            progress.emit(f"N={dimension} precision={precision} started")
        try:
            result, _ = _cached_result(
                cache_dir,
                {
                    "kind": "rigorous-screen",
                    "support": f"{support.numerator}/{support.denominator}",
                    "dimension": dimension,
                    "precision": precision,
                    "residual_order": residual_order,
                },
                lambda: scout_support(
                    support,
                    dimension=dimension,
                    prec=precision,
                    residual_order=residual_order,
                ),
            )
        except Exception as exc:
            attempts.append(
                {
                    "precision_bits": precision,
                    "status": "assembly_failed",
                    "precision_status": PRECISION_STATUS_ASSEMBLY_FAILED,
                    "precision_reasons": ["assembly_failed"],
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            if progress is not None:
                progress.emit(f"N={dimension} precision={precision} assembly-failed")
            continue

        schur = result["schur_min_eigenvalue_midpoint"]
        finite = result["finite_block_min_eigenvalue_midpoint"]
        mu_lower = result["mu_lower"]
        usable = all(
            isinstance(value, (int, float))
            and math.isfinite(float(value))
            for value in (schur, finite, mu_lower)
        )
        stable_change = (
            previous_schur is not None
            and usable
            and abs(float(schur) - previous_schur)
            <= 1e-3 * max(abs(float(schur)), abs(previous_schur), 1e-12)
        )
        attempt = {
            **result,
            "precision_bits": precision,
            "stable_change": stable_change,
        }
        diagnostics: dict[str, object] | None = None
        if previous_result is not None:
            diagnostics = _precision_pair_diagnostics(previous_result, attempt)
            attempt["change_from_previous"] = diagnostics
            pair_diagnostics.append(diagnostics)
            _mark_previous_precision_contradiction(
                previous_result, diagnostics, stable_change
            )
        attempt["precision_status"] = PRECISION_STATUS_INSUFFICIENT
        attempt["precision_reasons"] = _precision_instability_reasons(
            usable=usable,
            stable_change=stable_change,
            diagnostics=diagnostics,
            schur_value=schur,
        )
        attempts.append(attempt)
        diagnostics_stable = bool(
            diagnostics is not None
            and diagnostics["all_key_signs_stable"] is True
            and diagnostics["widths_reduced"] is True
        )
        if (
            usable
            and stable_change
            and diagnostics_stable
            and float(mu_lower) > 0
            and float(finite) > 0
            and float(schur) > 0
        ):
            attempt["precision_status"] = PRECISION_STATUS_STABLE
            attempt["precision_reasons"] = ["stable_against_previous_precision"]
            if progress is not None:
                progress.emit(f"N={dimension} precision={precision} stable")
            return {
                "status": "precision_stable",
                "precision_status": PRECISION_STATUS_STABLE,
                "selected_precision_bits": precision,
                "attempts": attempts,
                "precision_pair_diagnostics": pair_diagnostics,
            }
        if progress is not None:
            progress.emit(f"N={dimension} precision={precision} insufficient")
        previous_schur = float(schur) if usable else None
        previous_result = attempt if usable else None

    if len(attempts) >= 2:
        previous, current = attempts[-2:]
        if (
            previous.get("status") != "assembly_failed"
            and current.get("status") != "assembly_failed"
            and current.get("stable_change") is True
            and isinstance(current.get("change_from_previous"), dict)
            and current["change_from_previous"]["all_key_signs_stable"] is True
            and current["change_from_previous"]["widths_reduced"] is True
            and float(previous["mu_lower"]) > 0
            and float(current["mu_lower"]) > 0
            and float(previous["finite_block_min_eigenvalue_midpoint"]) > 0
            and float(current["finite_block_min_eigenvalue_midpoint"]) > 0
            and float(previous["schur_min_eigenvalue_midpoint"]) < 0
            and float(current["schur_min_eigenvalue_midpoint"]) < 0
        ):
            current["precision_status"] = PRECISION_STATUS_MATHEMATICAL_NEGATIVE
            current["precision_reasons"] = [
                "stable_negative_across_improving_precisions"
            ]
            return {
                "status": "mathematical_negative",
                "precision_status": PRECISION_STATUS_MATHEMATICAL_NEGATIVE,
                "selected_precision_bits": None,
                "attempts": attempts,
                "precision_pair_diagnostics": pair_diagnostics,
            }
    if not attempts or all(attempt.get("status") == "assembly_failed" for attempt in attempts):
        raise RuntimeError("all precision-ladder assemblies failed")
    return {
        "status": "precision_limit_reached",
        "precision_status": PRECISION_STATUS_INSUFFICIENT,
        "selected_precision_bits": None,
        "attempts": attempts,
        "precision_pair_diagnostics": pair_diagnostics,
    }


def _construct_candidate(
    support: Fraction,
    dimension: int,
    precision: int,
    residual_order: int,
    matrix_bits_ladder: list[int],
    witness_bits_ladder: list[int],
    cache_dir: Path | None,
) -> dict[str, object]:
    attempts: list[dict[str, object]] = []
    for matrix_bits in matrix_bits_ladder:
        for witness_bits in witness_bits_ladder:
            try:
                candidate, cache_hit = _cached_result(
                    cache_dir,
                    {
                        "kind": "candidate-check",
                        "support": f"{support.numerator}/{support.denominator}",
                        "dimension": dimension,
                        "precision": precision,
                        "residual_order": residual_order,
                        "matrix_bits": matrix_bits,
                        "witness_bits": witness_bits,
                    },
                    lambda: run_candidate(
                        support,
                        dimension=dimension,
                        prec=precision,
                        residual_order=residual_order,
                        matrix_bits=matrix_bits,
                        witness_bits=witness_bits,
                    ),
                )
                attempts.append(
                    {
                        **candidate,
                        "matrix_bits": matrix_bits,
                        "witness_bits": witness_bits,
                        "cache_hit": cache_hit,
                    }
                )
                if candidate["all_margins_positive"]:
                    return {
                        "status": "candidate_ready",
                        "selected_matrix_bits": matrix_bits,
                        "selected_witness_bits": witness_bits,
                        "attempts": attempts,
                    }
            except CandidateStageError as exc:
                attempts.append(
                    {
                        "matrix_bits": matrix_bits,
                        "witness_bits": witness_bits,
                        "status": f"{exc.stage}_failed",
                        "failure_stage": exc.stage,
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    }
                )
            except Exception as exc:
                attempts.append(
                    {
                        "matrix_bits": matrix_bits,
                        "witness_bits": witness_bits,
                        "status": "candidate_check_failed",
                        "failure_stage": "candidate_check",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    }
                )
    statuses = {str(attempt.get("status", "")) for attempt in attempts}
    failure_status = (
        "witness_failed"
        if "witness_failed" in statuses
        else "rounding_failed"
        if "rounding_failed" in statuses
        else "candidate_check_failed"
    )
    return {
        "status": failure_status,
        "selected_matrix_bits": None,
        "selected_witness_bits": None,
        "attempts": attempts,
    }



def _successful_candidate_attempt(candidate: dict[str, object]) -> dict[str, object]:
    attempts = candidate.get("attempts", [])
    if not isinstance(attempts, list):
        raise ValueError("candidate attempts must be a list")
    for attempt in reversed(attempts):
        if isinstance(attempt, dict) and attempt.get("all_margins_positive") is True:
            return attempt
    raise ValueError("candidate_ready result is missing its positive exact attempt")


def _fraction_metric(attempt: dict[str, object], name: str) -> Fraction:
    value = attempt.get(name)
    if not isinstance(value, str):
        raise ValueError(f"candidate attempt is missing exact {name}")
    return Fraction(value)


def _relative_fraction_change(previous: Fraction, current: Fraction) -> float:
    delta = abs(current - previous)
    scale = max(abs(previous), abs(current))
    if scale == 0:
        return 0.0
    return float(delta / scale)


def _candidate_precision_pair_diagnostics(
    previous: dict[str, object], current: dict[str, object]
) -> dict[str, object]:
    metric_names = ("mu_lower", "even_gershgorin_margin", "odd_gershgorin_margin")
    previous_metrics = {name: _fraction_metric(previous, name) for name in metric_names}
    current_metrics = {name: _fraction_metric(current, name) for name in metric_names}
    relative_changes = {
        name: _relative_fraction_change(previous_metrics[name], current_metrics[name])
        for name in metric_names
    }
    signs_stable = {
        name: (previous_metrics[name] > 0) == (current_metrics[name] > 0)
        for name in metric_names
    }

    previous_working = previous.get("working_precision_diagnostics")
    current_working = current.get("working_precision_diagnostics")
    if not isinstance(previous_working, dict) or not isinstance(current_working, dict):
        raise ValueError("candidate attempt is missing working-precision diagnostics")
    previous_matrices = previous_working.get("matrix_widths")
    current_matrices = current_working.get("matrix_widths")
    previous_scalars = previous_working.get("scalar_widths")
    current_scalars = current_working.get("scalar_widths")
    if not all(
        isinstance(value, dict)
        for value in (previous_matrices, current_matrices, previous_scalars, current_scalars)
    ):
        raise ValueError("candidate working-precision diagnostics are incomplete")

    matrix_width_changes: dict[str, float] = {}
    matrix_widths_reduced = True
    for name in ("A", "GV", "G2", "GR"):
        previous_row = previous_matrices[name]  # type: ignore[index]
        current_row = current_matrices[name]  # type: ignore[index]
        if not isinstance(previous_row, dict) or not isinstance(current_row, dict):
            raise ValueError("candidate matrix-width diagnostics are malformed")
        previous_width = float(previous_row["max_width"])
        current_width = float(current_row["max_width"])
        matrix_width_changes[name] = current_width - previous_width
        matrix_widths_reduced = matrix_widths_reduced and current_width <= previous_width

    scalar_width_changes: dict[str, str] = {}
    scalar_widths_reduced = True
    for name in ("mu", "rho_R", "residual_remainder"):
        previous_width = Fraction(str(previous_scalars[name]))  # type: ignore[index]
        current_width = Fraction(str(current_scalars[name]))  # type: ignore[index]
        scalar_width_changes[name] = str(current_width - previous_width)
        scalar_widths_reduced = scalar_widths_reduced and current_width <= previous_width

    previous_rounding = previous.get("exact_rounding_diagnostics")
    current_rounding = current.get("exact_rounding_diagnostics")
    if not isinstance(previous_rounding, dict) or not isinstance(current_rounding, dict):
        raise ValueError("candidate attempt is missing exact-rounding diagnostics")
    previous_rounded_matrices = previous_rounding.get("matrix_widths")
    current_rounded_matrices = current_rounding.get("matrix_widths")
    if not isinstance(previous_rounded_matrices, dict) or not isinstance(
        current_rounded_matrices, dict
    ):
        raise ValueError("candidate exact-rounding diagnostics are incomplete")
    exact_rounding_widths_nonincreasing = True
    exact_rounding_width_changes: dict[str, str] = {}
    for name in ("A", "GV", "G2", "GR"):
        previous_row = previous_rounded_matrices[name]
        current_row = current_rounded_matrices[name]
        if not isinstance(previous_row, dict) or not isinstance(current_row, dict):
            raise ValueError("candidate exact matrix-width diagnostics are malformed")
        previous_width = Fraction(str(previous_row["max_width"]))
        current_width = Fraction(str(current_row["max_width"]))
        exact_rounding_width_changes[name] = str(current_width - previous_width)
        exact_rounding_widths_nonincreasing = (
            exact_rounding_widths_nonincreasing and current_width <= previous_width
        )

    margins_stable = all(
        change <= CANDIDATE_MARGIN_RELATIVE_STABILITY_TOLERANCE
        for change in relative_changes.values()
    )
    all_positive = all(value > 0 for value in (*previous_metrics.values(), *current_metrics.values()))
    conditioning_improved = matrix_widths_reduced and scalar_widths_reduced
    exact_rounding_survives = bool(
        previous.get("all_margins_positive") is True
        and current.get("all_margins_positive") is True
        and previous_rounding.get("rounding_succeeded") is True
        and current_rounding.get("rounding_succeeded") is True
    )
    qualified = bool(
        all_positive
        and all(signs_stable.values())
        and margins_stable
        and conditioning_improved
        and exact_rounding_widths_nonincreasing
        and exact_rounding_survives
    )
    return {
        "from_precision_bits": previous["precision_bits"],
        "to_precision_bits": current["precision_bits"],
        "exact_margin_relative_changes": relative_changes,
        "exact_margin_signs_stable": signs_stable,
        "exact_margins_stable": margins_stable,
        "working_matrix_width_changes": matrix_width_changes,
        "working_matrix_widths_reduced": matrix_widths_reduced,
        "working_scalar_width_changes": scalar_width_changes,
        "working_scalar_widths_reduced": scalar_widths_reduced,
        "conditioning_improved": conditioning_improved,
        "exact_rounding_width_changes": exact_rounding_width_changes,
        "exact_rounding_widths_nonincreasing": exact_rounding_widths_nonincreasing,
        "exact_rounding_survives": exact_rounding_survives,
        "all_exact_margins_positive": all_positive,
        "qualified": qualified,
    }


def _confirm_candidate_precision_stability(
    support: Fraction,
    dimension: int,
    candidate: dict[str, object],
    residual_order: int,
    *,
    precision_step: int,
    extra_steps: int,
    cache_dir: Path | None,
    progress: LiveProgress | None = None,
) -> dict[str, object]:
    if precision_step < 1:
        raise ValueError("candidate precision step must be positive")
    if extra_steps < 1:
        raise ValueError("candidate precision confirmation requires at least one extra step")

    base = _successful_candidate_attempt(candidate)
    base_precision = int(base["precision_bits"])
    matrix_bits = int(candidate["selected_matrix_bits"])
    witness_bits = int(candidate["selected_witness_bits"])
    attempts: list[dict[str, object]] = [
        {**base, "confirmation_status": "base_candidate"}
    ]
    pair_diagnostics: list[dict[str, object]] = []
    previous_success = attempts[0]

    for step_index in range(1, extra_steps + 1):
        precision = base_precision + precision_step * step_index
        if progress is not None:
            progress.emit(f"N={dimension} confirmation precision={precision} started")
        try:
            result, cache_hit = _cached_result(
                cache_dir,
                {
                    "kind": "candidate-check",
                    "support": f"{support.numerator}/{support.denominator}",
                    "dimension": dimension,
                    "precision": precision,
                    "residual_order": residual_order,
                    "matrix_bits": matrix_bits,
                    "witness_bits": witness_bits,
                },
                lambda: run_candidate(
                    support,
                    dimension=dimension,
                    prec=precision,
                    residual_order=residual_order,
                    matrix_bits=matrix_bits,
                    witness_bits=witness_bits,
                ),
            )
        except CandidateStageError as exc:
            attempts.append(
                {
                    "precision_bits": precision,
                    "matrix_bits": matrix_bits,
                    "witness_bits": witness_bits,
                    "confirmation_status": f"{exc.stage}_failed",
                    "failure_stage": exc.stage,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            if progress is not None:
                progress.emit(
                    f"N={dimension} confirmation precision={precision} {exc.stage}-failed"
                )
            continue
        except Exception as exc:
            attempts.append(
                {
                    "precision_bits": precision,
                    "matrix_bits": matrix_bits,
                    "witness_bits": witness_bits,
                    "confirmation_status": "candidate_check_failed",
                    "failure_stage": "candidate_check",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            if progress is not None:
                progress.emit(
                    f"N={dimension} confirmation precision={precision} candidate-check-failed"
                )
            return {
                "classification": "CANDIDATE_CHECK_FAILED",
                "qualified": False,
                "fixed_parameters": {
                    "support": f"{support.numerator}/{support.denominator}",
                    "dimension": dimension,
                    "residual_order": residual_order,
                    "matrix_bits": matrix_bits,
                    "witness_bits": witness_bits,
                },
                "base_precision_bits": base_precision,
                "selected_confirmation_precision_bits": None,
                "attempts": attempts,
                "pair_diagnostics": pair_diagnostics,
            }

        current = {
            **result,
            "matrix_bits": matrix_bits,
            "witness_bits": witness_bits,
            "cache_hit": cache_hit,
            "confirmation_status": "completed",
        }
        attempts.append(current)
        diagnostics = _candidate_precision_pair_diagnostics(previous_success, current)
        pair_diagnostics.append(diagnostics)
        if progress is not None:
            progress.emit(
                f"N={dimension} confirmation precision={precision} "
                + ("stable" if diagnostics["qualified"] is True else "insufficient")
            )
        if diagnostics["qualified"] is True:
            return {
                "classification": (
                    "CANDIDATE_STABLE"
                    if step_index == 1
                    else "CANDIDATE_STABLE_AFTER_ESCALATION"
                ),
                "qualified": True,
                "fixed_parameters": {
                    "support": f"{support.numerator}/{support.denominator}",
                    "dimension": dimension,
                    "residual_order": residual_order,
                    "matrix_bits": matrix_bits,
                    "witness_bits": witness_bits,
                },
                "base_precision_bits": base_precision,
                "selected_confirmation_precision_bits": precision,
                "attempts": attempts,
                "pair_diagnostics": pair_diagnostics,
            }
        previous_success = current

    failure_stages = {
        str(attempt.get("failure_stage"))
        for attempt in attempts[1:]
        if attempt.get("failure_stage") is not None
    }
    successful_higher = [
        attempt for attempt in attempts[1:] if attempt.get("confirmation_status") == "completed"
    ]
    if not successful_higher and failure_stages == {"rounding"}:
        classification = "ROUNDING_LIMITED"
    elif not successful_higher and failure_stages == {"witness"}:
        classification = "WITNESS_LIMITED"
    else:
        classification = "INSUFFICIENT_WORKING_PRECISION"
    return {
        "classification": classification,
        "qualified": False,
        "fixed_parameters": {
            "support": f"{support.numerator}/{support.denominator}",
            "dimension": dimension,
            "residual_order": residual_order,
            "matrix_bits": matrix_bits,
            "witness_bits": witness_bits,
        },
        "base_precision_bits": base_precision,
        "selected_confirmation_precision_bits": None,
        "attempts": attempts,
        "pair_diagnostics": pair_diagnostics,
    }


def run_driver(
    support: Fraction,
    dimensions: list[int],
    *,
    scout_resolution_count: int = 3,
    precision_start: int = 128,
    precision_max: int = 512,
    residual_order: int = 32,
    matrix_bits_start: int = 64,
    matrix_bits_max: int = 104,
    witness_bits_start: int = 32,
    witness_bits_max: int = 56,
    candidate_precision_step: int = CANDIDATE_PRECISION_STEP_DEFAULT,
    candidate_precision_extra_steps: int = CANDIDATE_PRECISION_EXTRA_STEPS_DEFAULT,
    scout_workers: int = 1,
    rigorous_workers: int = 1,
    cache_dir: Path | None = None,
    run_status: RunStatusWriter | None = None,
    progress: LiveProgress | None = None,
    worker_cleanup: WorkerCleanupVerifier | None = None,
) -> dict[str, Any]:
    machine = ContinuationStateMachine()
    cleanup_verifier = worker_cleanup or WorkerCleanupVerifier()

    def emit_event(event: str, **details: object) -> None:
        if run_status is not None:
            bounded = _bounded_observability_value(details)
            if not isinstance(bounded, dict):
                raise TypeError("bounded event details must remain a mapping")
            run_status.event(event, **bounded)

    def emit_progress(message: str) -> None:
        if progress is not None:
            progress.emit(message)

    def emit_cleanup_event(event: str, details: dict[str, object]) -> None:
        emit_event(event, **details)

    def observe_operation(operation: dict[str, object] | None) -> None:
        if run_status is not None:
            bounded = _bounded_observability_value(operation)
            if bounded is not None and not isinstance(bounded, dict):
                raise TypeError("bounded current operation must remain a mapping")
            run_status.update(
                workflow_state=machine.current.value,
                current_operation=bounded,
                terminal=False,
            )

    def transition(
        target: WorkflowState,
        *,
        reason: str,
        details: dict[str, object] | None = None,
    ) -> None:
        ContinuationStateMachine.transition(
            machine,
            target,
            reason=reason,
            details=details,
        )
        if target in TERMINAL_WORKFLOW_STATES:
            operation: dict[str, object] | None = {
                "stage": "FINAL_RESULT_PENDING_BUNDLE",
                "result_state": target.value,
            }
        else:
            operation = {
                "stage": target.value,
                "reason": reason,
                "details": details or {},
            }
        observe_operation(operation)
        emit_event(
            "WORKFLOW_STATE_CHANGED",
            workflow_state=target.value,
            reason=reason,
            details=details or {},
        )
        if target in TERMINAL_WORKFLOW_STATES:
            emit_event("RUN_RESULT_REACHED", result_state=target.value)

    observe_operation(
        {
            "stage": WorkflowState.VALIDATE_INPUT.value,
            "dimension_count": len(dimensions),
        }
    )

    emit_event("VALIDATION_STARTED", dimension_count=len(dimensions))

    if support <= 0:
        raise ValueError("support must be positive")
    require_one_prime_support(support.numerator, support.denominator)
    if not dimensions:
        raise ValueError("at least one dimension is required")
    if any(dimension < 1 for dimension in dimensions):
        raise ValueError("dimensions must be positive")
    if len(set(dimensions)) != len(dimensions):
        raise ValueError("dimensions must be unique")
    precisions = build_precision_ladder(precision_start, precision_max)
    if matrix_bits_start < 16:
        raise ValueError("matrix_bits_start must be at least 16")
    if witness_bits_start < 8:
        raise ValueError("witness_bits_start must be at least 8")
    if candidate_precision_step < 1:
        raise ValueError("candidate_precision_step must be positive")
    if candidate_precision_extra_steps < 1:
        raise ValueError("candidate_precision_extra_steps must be positive")
    if scout_workers < 1:
        raise ValueError("scout_workers must be positive")
    if rigorous_workers < 1:
        raise ValueError("rigorous_workers must be positive")
    matrix_bits_ladder = build_bit_ladder(matrix_bits_start, matrix_bits_max, 16)
    witness_bits_ladder = build_bit_ladder(witness_bits_start, witness_bits_max, 8)
    resolutions = build_scout_resolutions(dimensions, scout_resolution_count)

    emit_event(
        "VALIDATION_COMPLETED",
        dimension_count=len(dimensions),
        resolution_count=len(resolutions),
        precision_count=len(precisions),
    )

    reconnaissance: list[dict[str, object]] = []
    scout_failures: list[dict[str, object]] = []
    scout_runs: list[dict[str, object]] = []
    rigorous_screening: list[dict[str, object]] = []
    rigorous_failures: list[dict[str, object]] = []
    candidates: list[dict[str, object]] = []
    candidate_failures: list[dict[str, object]] = []
    stable_dimensions: list[int] = []
    primary_dimension: int | None = None
    fallback_dimensions: list[int] = []
    selected_candidate_dimension: int | None = None

    def finalize() -> dict[str, Any]:
        final_state = machine.require_terminal().value
        return {
            "role": "pre_theorem_continuation_driver",
            "driver_version": DRIVER_VERSION,
            "cache_version": CACHE_VERSION,
            "state": final_state,
            "status": final_state,
            "workflow_state": final_state,
            "workflow_trace": machine.trace(),
            **theorem_boundary_payload(),
            "support": f"{support.numerator}/{support.denominator}",
            "dimensions": dimensions,
            "scout_resolution_count": scout_resolution_count,
            "scout_resolution_plan": [resolution.as_dict() for resolution in resolutions],
            "precision_ladder": precisions,
            "precision_start": precision_start,
            "precision_max": precision_max,
            "matrix_bits_start": matrix_bits_start,
            "matrix_bits_max": matrix_bits_max,
            "witness_bits_start": witness_bits_start,
            "witness_bits_max": witness_bits_max,
            "candidate_precision_step": candidate_precision_step,
            "candidate_precision_extra_steps": candidate_precision_extra_steps,
            "scout_workers": scout_workers,
            "rigorous_workers": rigorous_workers,
            "cache_dir": str(cache_dir) if cache_dir is not None else None,
            "residual_order": residual_order,
            "matrix_bits_ladder": matrix_bits_ladder,
            "witness_bits_ladder": witness_bits_ladder,
            "scout_runs": scout_runs,
            "reconnaissance": reconnaissance,
            "scout_failures": scout_failures,
            "rigorous_screening": rigorous_screening,
            "rigorous_failures": rigorous_failures,
            "candidates": candidates,
            "candidate_failures": candidate_failures,
            "scout_primary_dimension": primary_dimension,
            "selected_dimension": selected_candidate_dimension,
            "selected_candidate_dimension": selected_candidate_dimension,
            "fallback_dimensions": fallback_dimensions,
            "warning": "Candidate is generator-side evidence only. No theorem status is granted until the pair is separately admitted to the closed verifier contract and independently replayed.",
        }

    transition(
        WorkflowState.FLOAT_SCOUT,
        reason="validated_driver_inputs",
        details={
            "support": f"{support.numerator}/{support.denominator}",
            "dimension_count": len(dimensions),
            "resolution_count": len(resolutions),
            "scout_workers": min(scout_workers, len(resolutions)),
        },
    )
    emit_event(
        "SCOUT_STAGE_STARTED",
        resolution_count=len(resolutions),
        worker_count=min(scout_workers, len(resolutions)),
    )
    emit_progress(
        f"SCOUT resolutions={len(resolutions)} workers={min(scout_workers, len(resolutions))}"
    )
    series: dict[int, list[ScoutDimensionResult]] = {
        dimension: [] for dimension in dimensions
    }

    def record_scout_result(
        resolution: ScoutResolution,
        raw_scout: dict[str, object],
    ) -> None:
        scout_runs.append(
            {
                "status": "completed",
                "resolution": resolution.as_dict(),
                "result": raw_scout,
            }
        )
        for row in _typed_scout_rows(
            raw_scout,
            max_mode=resolution.max_mode,
            quadrature_order=resolution.quadrature_order,
            shift_order=resolution.shift_order,
        ):
            series[row.dimension].append(row)

        emit_event(
            "SCOUT_RESOLUTION_COMPLETED",
            level=resolution.level,
            max_mode=resolution.max_mode,
            quadrature_order=resolution.quadrature_order,
            shift_order=resolution.shift_order,
        )
        emit_progress(
            f"SCOUT resolution {resolution.level + 1}/{len(resolutions)} complete"
        )

    def record_scout_failure(resolution: ScoutResolution, exc: Exception) -> None:
        failure = {
            "resolution": resolution.as_dict(),
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        scout_failures.append(failure)
        scout_runs.append({"status": "failed", **failure})

        emit_event(
            "SCOUT_RESOLUTION_FAILED",
            level=resolution.level,
            error_type=type(exc).__name__,
            error=str(exc)[:500],
        )
        emit_progress(
            f"SCOUT resolution {resolution.level + 1}/{len(resolutions)} failed "
            f"type={type(exc).__name__}"
        )

    effective_scout_workers = min(scout_workers, len(resolutions))
    if effective_scout_workers == 1:
        for resolution in resolutions:
            emit_event(
                "SCOUT_RESOLUTION_STARTED",
                level=resolution.level,
                max_mode=resolution.max_mode,
                quadrature_order=resolution.quadrature_order,
                shift_order=resolution.shift_order,
            )
            observe_operation(
                {
                    "stage": WorkflowState.FLOAT_SCOUT.value,
                    "resolution_level": resolution.level,
                    "max_mode": resolution.max_mode,
                    "quadrature_order": resolution.quadrature_order,
                    "shift_order": resolution.shift_order,
                }
            )
            try:
                record_scout_result(
                    resolution,
                    scout(
                        max_mode=resolution.max_mode,
                        quadrature_order=resolution.quadrature_order,
                        shift_order=resolution.shift_order,
                        n_values=dimensions,
                        support=support,
                    ),
                )
            except Exception as exc:
                record_scout_failure(resolution, exc)
    else:
        with _verified_process_pool(
            effective_scout_workers,
            stage="FLOAT_SCOUT",
            verifier=cleanup_verifier,
            event_sink=emit_cleanup_event,
        ) as executor:
            jobs = [
                (
                    resolution,
                    executor.submit(
                        _scout_resolution_worker,
                        support,
                        dimensions,
                        resolution,
                    ),
                )
                for resolution in resolutions
            ]
            for resolution in resolutions:
                emit_event(
                    "SCOUT_RESOLUTION_STARTED",
                    level=resolution.level,
                    max_mode=resolution.max_mode,
                    quadrature_order=resolution.quadrature_order,
                    shift_order=resolution.shift_order,
                )
            observe_operation(
                {
                    "stage": WorkflowState.FLOAT_SCOUT.value,
                    "active_resolution_levels": [resolution.level for resolution in resolutions],
                    "worker_count": effective_scout_workers,
                }
            )
            # Consume in resolution order so bundle/result ordering is deterministic.
            for resolution, future in jobs:
                try:
                    record_scout_result(resolution, future.result())
                except Exception as exc:
                    record_scout_failure(resolution, exc)

    emit_event(
        "SCOUT_STAGE_COMPLETED",
        completed_resolutions=sum(run["status"] == "completed" for run in scout_runs),
        failed_resolutions=len(scout_failures),
    )
    emit_progress(
        "SCOUT complete "
        f"completed={sum(run['status'] == 'completed' for run in scout_runs)} "
        f"failed={len(scout_failures)}"
    )
    transition(
        WorkflowState.CHECK_SCOUT_STABILITY,
        reason="floating_scout_complete",
        details={
            "completed_resolutions": sum(run["status"] == "completed" for run in scout_runs),
            "failed_resolutions": len(scout_failures),
        },
    )
    for dimension in dimensions:
        rows = series[dimension]
        classification = (
            _classify_reconnaissance(rows)
            if len(rows) == len(resolutions)
            else "unstable"
        )
        reconnaissance.append(
            {
                "dimension": dimension,
                "classification": classification,
                "resolutions": [row.as_dict() for row in rows],
            }
        )

    stable_dimensions = sorted(
        int(row["dimension"])
        for row in reconnaissance
        if row["classification"] == "stable_positive"
    )
    emit_event(
        "SCOUT_CLASSIFICATION_COMPLETED",
        stable_dimensions=stable_dimensions,
        unstable_dimensions=[
            int(row["dimension"])
            for row in reconnaissance
            if row["classification"] == "unstable"
        ],
    )
    if stable_dimensions:
        emit_progress(f"SCOUT stable-positive begins at N={stable_dimensions[0]}")
    else:
        emit_progress("SCOUT no stable-positive dimension")
    if not stable_dimensions:
        unstable = bool(scout_failures) or any(
            row["classification"] == "unstable" for row in reconnaissance
        )
        transition(
            WorkflowState.SCOUT_UNSTABLE if unstable else WorkflowState.NO_CANDIDATE,
            reason=(
                "scout_evidence_unstable"
                if unstable
                else "no_stable_positive_scout_dimension"
            ),
            details={"stable_dimensions": []},
        )
        return finalize()

    transition(
        WorkflowState.SELECT_DIMENSION,
        reason="stable_positive_dimensions_found",
        details={"stable_dimensions": stable_dimensions},
    )
    primary_dimension = stable_dimensions[0]
    fallback_dimensions = stable_dimensions[1:2]
    screening_dimensions = stable_dimensions[:2]

    transition(
        WorkflowState.RIGOROUS_PRECISION_SEARCH,
        reason="selected_primary_and_fallback_dimensions",
        details={
            "primary_dimension": primary_dimension,
            "fallback_dimensions": fallback_dimensions,
            "rigorous_workers": min(rigorous_workers, len(screening_dimensions)),
        },
    )
    emit_event(
        "RIGOROUS_STAGE_STARTED",
        dimensions=screening_dimensions,
        worker_count=min(rigorous_workers, len(screening_dimensions)),
    )
    emit_progress(
        "RIGOROUS targets "
        + ",".join(f"N={dimension}" for dimension in screening_dimensions)
        + f" workers={min(rigorous_workers, len(screening_dimensions))}"
    )
    survivors: list[int] = []

    def record_rigorous_result(
        dimension: int,
        screening: dict[str, object],
    ) -> None:
        rigorous_screening.append({"dimension": dimension, **screening})
        selected_precision = screening["selected_precision_bits"]
        if screening["status"] == "precision_stable" and isinstance(
            selected_precision, int
        ):
            survivors.append(dimension)
        emit_event(
            "RIGOROUS_DIMENSION_COMPLETED",
            dimension=dimension,
            status=screening.get("status"),
            selected_precision_bits=screening.get("selected_precision_bits"),
            attempted_precisions=[
                attempt.get("precision_bits")
                for attempt in screening.get("attempts", [])
                if isinstance(attempt, dict)
            ],
        )
        emit_progress(
            f"RIGOROUS N={dimension} complete status={screening.get('status')}"
        )

    def record_rigorous_failure(dimension: int, exc: Exception) -> None:
        rigorous_failures.append(
            {
                "dimension": dimension,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )
        emit_event(
            "RIGOROUS_DIMENSION_FAILED",
            dimension=dimension,
            error_type=type(exc).__name__,
            error=str(exc)[:500],
        )
        emit_progress(f"RIGOROUS N={dimension} failed type={type(exc).__name__}")

    effective_rigorous_workers = min(rigorous_workers, len(screening_dimensions))
    if effective_rigorous_workers == 1:
        for dimension in screening_dimensions:
            emit_event("RIGOROUS_DIMENSION_STARTED", dimension=dimension)
            emit_progress(f"RIGOROUS N={dimension} started")
            observe_operation(
                {
                    "stage": WorkflowState.RIGOROUS_PRECISION_SEARCH.value,
                    "dimension": dimension,
                    "precision_ladder": precisions,
                }
            )
            try:
                screening = (
                    _escalate_rigorous_screen(
                        support, dimension, precisions, residual_order, cache_dir
                    )
                    if progress is None
                    else _escalate_rigorous_screen(
                        support,
                        dimension,
                        precisions,
                        residual_order,
                        cache_dir,
                        progress=progress,
                    )
                )
                record_rigorous_result(dimension, screening)
            except Exception as exc:
                record_rigorous_failure(dimension, exc)
    else:
        cache_dir_text = str(cache_dir) if cache_dir is not None else None
        with _verified_process_pool(
            effective_rigorous_workers,
            stage="RIGOROUS_PRECISION_SEARCH",
            verifier=cleanup_verifier,
            event_sink=emit_cleanup_event,
        ) as executor:
            jobs = [
                (
                    dimension,
                    executor.submit(
                        _rigorous_screen_worker,
                        support,
                        dimension,
                        precisions,
                        residual_order,
                        cache_dir_text,
                        progress,
                    ),
                )
                for dimension in screening_dimensions
            ]
            for dimension in screening_dimensions:
                emit_event("RIGOROUS_DIMENSION_STARTED", dimension=dimension)
                emit_progress(f"RIGOROUS N={dimension} started")
            observe_operation(
                {
                    "stage": WorkflowState.RIGOROUS_PRECISION_SEARCH.value,
                    "active_dimensions": screening_dimensions,
                    "precision_ladder": precisions,
                    "worker_count": effective_rigorous_workers,
                }
            )
            # Consume in selected-dimension order so result semantics stay stable.
            for dimension, future in jobs:
                try:
                    record_rigorous_result(dimension, future.result())
                except Exception as exc:
                    record_rigorous_failure(dimension, exc)

    emit_event(
        "RIGOROUS_STAGE_COMPLETED",
        screened_dimensions=screening_dimensions,
        surviving_dimensions=survivors,
        failure_count=len(rigorous_failures),
    )
    emit_progress(
        f"RIGOROUS complete survivors={len(survivors)} failures={len(rigorous_failures)}"
    )
    transition(
        WorkflowState.CHECK_RIGOROUS_STABILITY,
        reason="rigorous_precision_search_complete",
        details={
            "screened_dimensions": screening_dimensions,
            "surviving_dimensions": survivors,
            "rigorous_failure_count": len(rigorous_failures),
        },
    )
    if not survivors:
        precision_limited = any(
            row.get("status") == "precision_limit_reached"
            for row in rigorous_screening
        )
        if rigorous_failures:
            target = WorkflowState.RIGOROUS_ASSEMBLY_FAILED
            reason = "rigorous_assembly_failed_without_survivor"
        elif precision_limited:
            target = WorkflowState.PRECISION_LIMIT_REACHED
            reason = "precision_ladder_exhausted_without_stable_candidate"
        else:
            target = WorkflowState.NO_CANDIDATE
            reason = "rigorous_screening_rejected_all_dimensions"
        transition(target, reason=reason, details={"survivors": []})
        return finalize()

    transition(
        WorkflowState.EXACT_ROUNDING_SEARCH,
        reason="rigorous_candidate_survived",
        details={"surviving_dimensions": survivors},
    )
    for dimension in survivors:
        emit_event("CANDIDATE_STARTED", dimension=dimension)
        emit_progress(f"CANDIDATE N={dimension} rounding started")
        observe_operation(
            {
                "stage": WorkflowState.EXACT_ROUNDING_SEARCH.value,
                "dimension": dimension,
            }
        )
        screening = next(
            row for row in rigorous_screening if row["dimension"] == dimension
        )
        try:
            candidate = _construct_candidate(
                support,
                dimension,
                int(screening["selected_precision_bits"]),
                residual_order,
                matrix_bits_ladder,
                witness_bits_ladder,
                cache_dir,
            )
            candidates.append({**candidate, "dimension": dimension})
            emit_event(
                "CANDIDATE_COMPLETED",
                dimension=dimension,
                status=candidate.get("status"),
                matrix_bits=candidate.get("selected_matrix_bits"),
                witness_bits=candidate.get("selected_witness_bits"),
            )
            emit_progress(
                f"CANDIDATE N={dimension} rounding complete status={candidate.get('status')}"
            )
            if candidate["status"] != "candidate_ready":
                candidate_failures.append(
                    {"dimension": dimension, "status": candidate["status"]}
                )
        except Exception as exc:
            candidate_failures.append(
                {
                    "dimension": dimension,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            emit_event(
                "CANDIDATE_FAILED",
                dimension=dimension,
                error_type=type(exc).__name__,
                error=str(exc)[:500],
            )
            emit_progress(
                f"CANDIDATE N={dimension} rounding failed type={type(exc).__name__}"
            )

    ready = [
        candidate for candidate in candidates if candidate["status"] == "candidate_ready"
    ]
    if ready:
        ready_dimensions = [int(candidate["dimension"]) for candidate in ready]
        transition(
            WorkflowState.EXACT_WITNESS_CHECK,
            reason="outward_rounding_and_exact_schur_succeeded",
            details={"candidate_ready_dimensions": ready_dimensions},
        )
        transition(
            WorkflowState.CANDIDATE_PRECISION_CONFIRMATION,
            reason="exact_candidate_requires_cross_precision_confirmation",
            details={
                "candidate_ready_dimensions": ready_dimensions,
                "precision_step": candidate_precision_step,
                "extra_steps": candidate_precision_extra_steps,
            },
        )
        confirmation_check_failed = False
        for candidate in ready:
            dimension = int(candidate["dimension"])
            emit_event(
                "CANDIDATE_CONFIRMATION_STARTED",
                dimension=dimension,
                precision_step=candidate_precision_step,
                extra_steps=candidate_precision_extra_steps,
            )
            emit_progress(f"CANDIDATE N={dimension} confirmation started")
            observe_operation(
                {
                    "stage": WorkflowState.CANDIDATE_PRECISION_CONFIRMATION.value,
                    "dimension": dimension,
                    "precision_step": candidate_precision_step,
                    "extra_steps": candidate_precision_extra_steps,
                }
            )
            try:
                confirmation_kwargs = {
                    "precision_step": candidate_precision_step,
                    "extra_steps": candidate_precision_extra_steps,
                    "cache_dir": cache_dir,
                }
                if progress is not None:
                    confirmation_kwargs["progress"] = progress
                stability = _confirm_candidate_precision_stability(
                    support,
                    dimension,
                    candidate,
                    residual_order,
                    **confirmation_kwargs,
                )
            except Exception as exc:
                stability = {
                    "classification": "CANDIDATE_CHECK_FAILED",
                    "qualified": False,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            candidate["candidate_precision_stability"] = stability
            candidate["confirmed_precision_bits"] = stability.get(
                "selected_confirmation_precision_bits"
            )
            emit_event(
                "CANDIDATE_CONFIRMATION_COMPLETED",
                dimension=dimension,
                classification=stability.get("classification"),
                qualified=stability.get("qualified"),
                confirmed_precision_bits=stability.get(
                    "selected_confirmation_precision_bits"
                ),
            )
            emit_progress(
                f"CANDIDATE N={dimension} confirmation complete "
                f"status={stability.get('classification')}"
            )
            if stability.get("qualified") is True:
                selected_candidate_dimension = dimension
                transition(
                    WorkflowState.CANDIDATE_READY,
                    reason="exact_candidate_is_stable_across_improving_working_precision",
                    details={
                        "selected_candidate_dimension": selected_candidate_dimension,
                        "candidate_precision_classification": stability.get(
                            "classification"
                        ),
                        "confirmed_precision_bits": stability.get(
                            "selected_confirmation_precision_bits"
                        ),
                    },
                )
                return finalize()
            classification = str(stability.get("classification", "UNKNOWN"))
            confirmation_check_failed = (
                confirmation_check_failed or classification == "CANDIDATE_CHECK_FAILED"
            )
            candidate_failures.append(
                {
                    "dimension": dimension,
                    "status": "candidate_precision_unstable",
                    "classification": classification,
                }
            )

        if confirmation_check_failed:
            transition(
                WorkflowState.CANDIDATE_CHECK_FAILED,
                reason="candidate_precision_confirmation_raised_unclassified_failure",
                details={"candidate_ready_dimensions": ready_dimensions},
            )
        else:
            transition(
                WorkflowState.PRECISION_LIMIT_REACHED,
                reason="candidate_precision_confirmation_did_not_stabilize",
                details={
                    "candidate_ready_dimensions": ready_dimensions,
                    "classifications": [
                        candidate.get("candidate_precision_stability", {}).get(
                            "classification"
                        )
                        if isinstance(candidate.get("candidate_precision_stability"), dict)
                        else None
                        for candidate in ready
                    ],
                },
            )
        return finalize()

    failure_statuses = {failure.get("status") for failure in candidate_failures}
    if "candidate_check_failed" in failure_statuses or None in failure_statuses:
        transition(
            WorkflowState.CANDIDATE_CHECK_FAILED,
            reason="candidate_stage_raised_unclassified_failure",
            details={"failure_statuses": sorted(str(status) for status in failure_statuses)},
        )
    elif failure_statuses == {"rounding_failed"}:
        transition(
            WorkflowState.ROUNDING_FAILED,
            reason="matrix_bit_ladder_exhausted_before_exact_witness_stage",
            details={"failure_statuses": ["rounding_failed"]},
        )
    else:
        transition(
            WorkflowState.EXACT_WITNESS_CHECK,
            reason="rounding_succeeded_but_no_witness_passed",
            details={"failure_statuses": sorted(str(status) for status in failure_statuses)},
        )
        transition(
            WorkflowState.WITNESS_FAILED,
            reason="witness_bit_ladder_exhausted_without_positive_margin",
            details={"failure_statuses": sorted(str(status) for status in failure_statuses)},
        )
    return finalize()




def _display_scout_classification(value: object) -> str:
    return {
        "stable_positive": "stable-positive",
        "negative": "negative",
        "unstable": "unstable",
    }.get(str(value), str(value).replace("_", "-"))


def _display_precision_attempt(attempt: dict[str, object]) -> str:
    status = str(attempt.get("precision_status", ""))
    if status == PRECISION_STATUS_STABLE:
        return "stable positive"
    if status == PRECISION_STATUS_MATHEMATICAL_NEGATIVE:
        return "stable negative"
    if status == PRECISION_STATUS_ASSEMBLY_FAILED:
        return "assembly failed"
    if status == PRECISION_STATUS_INSUFFICIENT:
        reasons = attempt.get("precision_reasons", [])
        if isinstance(reasons, list):
            reason_set = {str(reason) for reason in reasons}
            if "contradicted_by_higher_precision" in reason_set:
                return "insufficient precision - contradicted at higher precision"
            if "key_sign_changed_at_higher_precision" in reason_set:
                return "insufficient precision - sign changed"
            if "midpoint_not_stable" in reason_set:
                return "insufficient precision - midpoint not stable"
            if "interval_widths_not_reduced" in reason_set:
                return "insufficient precision - enclosure not improving"
            if "negative_result_not_precision_stable" in reason_set:
                return "insufficient precision - negative result not stable"
            if "no_prior_precision_for_stability_check" in reason_set:
                return "insufficient precision - awaiting comparison"
        return "insufficient precision"

    legacy_status = str(attempt.get("status", ""))
    if legacy_status == "assembly_failed":
        return "assembly failed"
    if attempt.get("stable_change") is True:
        return "stable"
    return "not yet stable"


def _display_candidate_stability(value: object) -> str:
    return {
        "CANDIDATE_STABLE": "stable at next precision",
        "CANDIDATE_STABLE_AFTER_ESCALATION": "stable after precision escalation",
        "INSUFFICIENT_WORKING_PRECISION": "insufficient working precision",
        "ROUNDING_LIMITED": "exact rounding limited",
        "WITNESS_LIMITED": "exact witness limited",
        "CANDIDATE_CHECK_FAILED": "candidate confirmation failed",
    }.get(str(value), str(value).replace("_", "-").lower())


def _sign_summary(value: object) -> str:
    if value is None:
        return "not available"
    try:
        numeric = Fraction(str(value))
    except (ValueError, ZeroDivisionError):
        try:
            numeric_float = float(value)
        except (TypeError, ValueError):
            return "not available"
        if numeric_float > 0:
            return "+"
        if numeric_float < 0:
            return "-"
        return "0"
    if numeric > 0:
        return "+"
    if numeric < 0:
        return "-"
    return "0"


def _selected_exact_candidate(result: dict[str, object]) -> dict[str, object] | None:
    selected = result.get("selected_candidate_dimension")
    candidates = result.get("candidates", [])
    if not isinstance(candidates, list):
        return None
    for candidate in candidates:
        if not isinstance(candidate, dict) or candidate.get("dimension") != selected:
            continue
        attempts = candidate.get("attempts", [])
        if not isinstance(attempts, list):
            continue
        stability = candidate.get("candidate_precision_stability")
        if isinstance(stability, dict) and stability.get("qualified") is True:
            confirmation_attempts = stability.get("attempts", [])
            if isinstance(confirmation_attempts, list):
                for attempt in reversed(confirmation_attempts):
                    if (
                        isinstance(attempt, dict)
                        and attempt.get("all_margins_positive") is True
                        and attempt.get("confirmation_status") == "completed"
                    ):
                        return attempt
        for attempt in reversed(attempts):
            if isinstance(attempt, dict) and attempt.get("all_margins_positive") is True:
                return attempt
    return None


def _rigorous_summary_row(
    result: dict[str, object], dimension: object
) -> dict[str, object] | None:
    rows = result.get("rigorous_screening", [])
    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and row.get("dimension") == dimension:
            return row
    return None


def format_terminal_summary(result: dict[str, object]) -> str:
    """Render a concise, human-readable view of a completed driver result."""
    lines = [
        "Support continuation candidate search",
        f"T = {result.get('support', 'unknown')}",
        "",
        "Dimensions tested:",
    ]

    reconnaissance = result.get("reconnaissance", [])
    if isinstance(reconnaissance, list) and reconnaissance:
        for row in reconnaissance:
            if not isinstance(row, dict):
                continue
            lines.append(
                f"  N={row.get('dimension')}  "
                f"{_display_scout_classification(row.get('classification', 'unknown'))}"
            )
    else:
        dimensions = result.get("dimensions", [])
        if isinstance(dimensions, list) and dimensions:
            for dimension in dimensions:
                lines.append(f"  N={dimension}  not available")
        else:
            lines.append("  not available")

    primary = result.get("scout_primary_dimension")
    selected = result.get("selected_candidate_dimension")
    if primary is not None:
        lines.extend(["", f"Primary rigorous target: N={primary}"])
    if selected is not None and primary is not None and selected != primary:
        lines.append(f"Fallback used: N={selected}")
        lines.append(f"Selected candidate: N={selected}")

    precision_dimension = selected if selected is not None else primary
    rigorous = _rigorous_summary_row(result, precision_dimension)
    if rigorous is None:
        screening = result.get("rigorous_screening", [])
        if isinstance(screening, list):
            rigorous = next((row for row in screening if isinstance(row, dict)), None)
            if rigorous is not None:
                precision_dimension = rigorous.get("dimension")
    if rigorous is not None:
        lines.extend(["", f"Precision search (N={precision_dimension}):"])
        attempts = rigorous.get("attempts", [])
        if isinstance(attempts, list) and attempts:
            for attempt in attempts:
                if isinstance(attempt, dict):
                    lines.append(
                        f"  {attempt.get('precision_bits')}  {_display_precision_attempt(attempt)}"
                    )
        else:
            lines.append(f"  {rigorous.get('status', 'not available')}")

    exact = _selected_exact_candidate(result)
    if selected is not None:
        candidate_rows = result.get("candidates", [])
        selected_row = None
        if isinstance(candidate_rows, list):
            selected_row = next(
                (
                    row
                    for row in candidate_rows
                    if isinstance(row, dict) and row.get("dimension") == selected
                ),
                None,
            )
        lines.extend(["", "Exact candidate:", f"  dimension:     N={selected}"])
        if isinstance(selected_row, dict):
            lines.append(f"  matrix bits:   {selected_row.get('selected_matrix_bits', 'not available')}")
            lines.append(f"  witness bits:  {selected_row.get('selected_witness_bits', 'not available')}")
            stability = selected_row.get("candidate_precision_stability")
            if isinstance(stability, dict):
                lines.append(
                    "  precision check: "
                    + _display_candidate_stability(stability.get("classification"))
                )
                lines.append(
                    f"  confirmed at:  {stability.get('selected_confirmation_precision_bits', 'not available')} bits"
                )
        if exact is not None:
            lines.extend(
                [
                    f"  mu_lower:      {_sign_summary(exact.get('mu_lower'))}",
                    f"  even margin:   {_sign_summary(exact.get('even_gershgorin_margin'))}",
                    f"  odd margin:    {_sign_summary(exact.get('odd_gershgorin_margin'))}",
                ]
            )

    state = str(result.get("state", result.get("status", "UNKNOWN")))
    lines.extend(["", f"RESULT: {state}", ""])

    if state == WorkflowState.PRECISION_LIMIT_REACHED.value:
        candidate_rows = result.get("candidates", [])
        candidate_precision_limited = isinstance(candidate_rows, list) and any(
            isinstance(candidate, dict)
            and isinstance(candidate.get("candidate_precision_stability"), dict)
            and candidate["candidate_precision_stability"].get("qualified") is False
            for candidate in candidate_rows
        )
        lines.append("No mathematical rejection was established.")
        if candidate_precision_limited:
            lines.append(
                "An exact positive candidate was found, but cross-precision candidate confirmation did not stabilize."
            )
        else:
            lines.append("The available precision ladder did not stabilize.")
    elif state == WorkflowState.NO_CANDIDATE.value:
        rigorous_rows = result.get("rigorous_screening", [])
        rigorous_negative = isinstance(rigorous_rows, list) and any(
            isinstance(row, dict) and row.get("status") == "mathematical_negative"
            for row in rigorous_rows
        )
        if rigorous_negative:
            lines.append("Rigorous screening found a stable mathematical negative.")
        else:
            lines.append("No stable-positive continuation dimension survived the current search.")
    elif state == WorkflowState.SCOUT_UNSTABLE.value:
        lines.extend(
            [
                "Floating reconnaissance did not stabilize.",
                "No rigorous mathematical rejection was established.",
            ]
        )
    elif state == WorkflowState.RIGOROUS_ASSEMBLY_FAILED.value:
        lines.append("Rigorous assembly failed before a stable mathematical decision was reached.")
    elif state == WorkflowState.ROUNDING_FAILED.value:
        lines.append("Rigorous positivity survived, but exact outward rounding exhausted its bit ladder.")
    elif state == WorkflowState.WITNESS_FAILED.value:
        lines.append("Rigorous positivity survived, but no exact rational witness passed.")
    elif state == WorkflowState.CANDIDATE_CHECK_FAILED.value:
        lines.append("Exact candidate construction ended in an unclassified pre-theorem failure.")

    lines.append("This is not a theorem.")
    if state == WorkflowState.CANDIDATE_READY.value:
        lines.append("Independent verifier admission has not been performed.")
    return "\n".join(lines)


def _path_is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _rollback_completion_manifest(output_dir: Path, primary_error: BaseException) -> None:
    """Best-effort rollback that preserves the primary failure if deletion itself fails."""
    try:
        remove_continuation_manifest(output_dir)
    except Exception as rollback_error:
        primary_error.add_note(
            "CRITICAL: run-manifest rollback also failed: "
            f"{type(rollback_error).__name__}: {rollback_error}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--support", required=True, help="exact rational support T, such as 19/40")
    dimensions = parser.add_mutually_exclusive_group(required=True)
    dimensions.add_argument("--n", help="comma-separated explicit dimensions")
    dimensions.add_argument("--n-min", type=int)
    parser.add_argument("--n-max", type=int)
    parser.add_argument("--n-step", type=int)
    parser.add_argument(
        "--scout-resolutions",
        type=int,
        default=3,
        help="number of increasing scout resolutions (minimum 2)",
    )
    available_cpus = os.cpu_count() or 1
    parser.add_argument(
        "--scout-workers",
        type=int,
        default=min(CLI_SCOUT_WORKERS_MAX, available_cpus),
        help="process workers for independent scout resolutions; use 1 for sequential reproduction",
    )
    parser.add_argument(
        "--rigorous-workers",
        type=int,
        default=min(CLI_RIGOROUS_WORKERS_MAX, available_cpus),
        help="process workers for primary/fallback rigorous screens; each precision ladder stays sequential",
    )
    parser.add_argument("--precision-start", type=int, default=128)
    parser.add_argument("--precision-max", type=int, default=512)
    parser.add_argument("--residual-order", type=int, default=32)
    parser.add_argument("--matrix-bits-start", type=int, default=64)
    parser.add_argument("--matrix-bits-max", type=int, default=104)
    parser.add_argument("--witness-bits-start", type=int, default=32)
    parser.add_argument("--witness-bits-max", type=int, default=56)
    parser.add_argument(
        "--candidate-precision-step",
        type=int,
        default=CANDIDATE_PRECISION_STEP_DEFAULT,
        help="working-precision increment for exact candidate stability confirmation",
    )
    parser.add_argument(
        "--candidate-precision-extra-steps",
        type=int,
        default=CANDIDATE_PRECISION_EXTRA_STEPS_DEFAULT,
        help="maximum higher-precision exact candidate confirmations; stops early when stable",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--json",
        action="store_true",
        help="print the full machine-readable result JSON instead of the concise terminal summary",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress live progress on stderr; final stdout output is unchanged",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(".cache/continuation-driver"),
        help="persistent cache for rigorous assembly results",
    )
    args = parser.parse_args()

    try:
        support = parse_support(args.support)
        dimensions = dimensions_from_args(args)
    except (ValueError, ZeroDivisionError) as exc:
        parser.error(str(exc))

    if _path_is_within(args.cache_dir, args.output_dir):
        parser.error("cache directory must be outside the continuation output directory")

    progress = LiveProgress(enabled=not args.quiet)
    run_started_at = utc_now()
    support_text = f"{support.numerator}/{support.denominator}"
    try:
        run_lock = OutputDirectoryLock.acquire(
            args.output_dir,
            command="weil_continuation_driver",
            support=support_text,
            started_at_utc=run_started_at,
        )
    except OutputDirectoryLockedError as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    except ValueError as exc:
        parser.error(str(exc))

    with run_lock:
        provenance = collect_runtime_provenance(exclude_output_dir=args.output_dir)
        try:
            git_commit = provenance.get("git_commit")
            git_dirty = provenance.get("git_dirty")
            if not isinstance(git_commit, str) or not git_commit:
                raise ValueError("runtime provenance is missing git_commit")
            if not isinstance(git_dirty, bool):
                raise ValueError("runtime provenance has invalid git_dirty")
            write_run_identity(
                run_lock,
                driver_version=DRIVER_VERSION,
                dimensions=dimensions,
                git_commit=git_commit,
                git_dirty=git_dirty,
            )
            run_status = RunStatusWriter.start(
                args.output_dir,
                command="weil_continuation_driver",
                support=support_text,
                started_at_utc=run_started_at,
                workflow_state=WorkflowState.VALIDATE_INPUT.value,
                current_operation={"stage": WorkflowState.VALIDATE_INPUT.value},
                output_lock=run_lock,
            )
        except ValueError as exc:
            parser.error(str(exc))

        progress.emit(
            f"RUN T={support_text} "
            f"dimensions={_dimension_progress_text(dimensions)}"
        )

        worker_cleanup = WorkerCleanupVerifier()
        frozen_result: dict[str, Any] | None = None
        try:
            with run_status.periodic_heartbeats():
                result = run_driver(
                    support,
                    dimensions,
                    scout_resolution_count=args.scout_resolutions,
                    precision_start=args.precision_start,
                    precision_max=args.precision_max,
                    residual_order=args.residual_order,
                    matrix_bits_start=args.matrix_bits_start,
                    matrix_bits_max=args.matrix_bits_max,
                    witness_bits_start=args.witness_bits_start,
                    witness_bits_max=args.witness_bits_max,
                    candidate_precision_step=args.candidate_precision_step,
                    candidate_precision_extra_steps=args.candidate_precision_extra_steps,
                    scout_workers=args.scout_workers,
                    rigorous_workers=args.rigorous_workers,
                    cache_dir=args.cache_dir,
                    run_status=run_status,
                    progress=progress,
                    worker_cleanup=worker_cleanup,
                )

                final_workflow_state = str(
                    result.get("workflow_state", result.get("state", "UNKNOWN"))
                )
                cleanup_report = worker_cleanup.verify()
                run_status.event(
                    "WORKER_CLEANUP_VERIFIED",
                    final_state=final_workflow_state,
                    executors_shutdown=cleanup_report["executors_shutdown"],
                    worker_processes_reaped=cleanup_report["worker_processes_reaped"],
                    cleanup_escalations=cleanup_report["cleanup_escalations"],
                    workers_joined_after_shutdown=cleanup_report[
                        "workers_joined_after_shutdown"
                    ],
                    workers_terminated=cleanup_report["workers_terminated"],
                    workers_killed=cleanup_report["workers_killed"],
                    active_children_after_cleanup=cleanup_report[
                        "active_children_after_cleanup"
                    ],
                )

                frozen_result, result_payload_sha256 = _freeze_result_payload(result)
                run_status.event(
                    "RESULT_PAYLOAD_FROZEN",
                    final_state=final_workflow_state,
                    sha256=result_payload_sha256,
                )
                run_status.event(
                    "BUNDLE_FINALIZATION_STARTED",
                    final_state=final_workflow_state,
                )
                progress.emit("BUNDLE write started")
                run_status.update(
                    workflow_state=final_workflow_state,
                    current_operation={"stage": "BUNDLE_FINALIZATION"},
                    terminal=False,
                )
                write_continuation_bundle(
                    frozen_result,
                    args.output_dir,
                    run_started_at=run_started_at,
                    provenance=provenance,
                    worker_cleanup=cleanup_report,
                    result_payload_sha256=result_payload_sha256,
                    parent_pid=run_lock.pid,
                )
                _, digest_after_bundle = _freeze_result_payload(frozen_result)
                if digest_after_bundle != result_payload_sha256:
                    raise RuntimeError("frozen result payload changed during finalization")

            # A completed run must retain healthy heartbeat supervision through
            # bundle finalization. Only publish completion milestones after the
            # heartbeat thread has stopped and joined without an I/O failure.
            run_status.event(
                "BUNDLE_FINALIZATION_COMPLETED",
                final_state=final_workflow_state,
                manifest="run-manifest.json",
            )
            progress.emit("BUNDLE write complete")
            run_status.update(
                workflow_state=final_workflow_state,
                current_operation=None,
                terminal=True,
            )
            run_status.event("RUN_COMPLETED", final_state=final_workflow_state)
            progress.emit(f"TERMINAL {final_workflow_state}")
        except KeyboardInterrupt as exc:
            _rollback_completion_manifest(args.output_dir, exc)
            run_status.record_failure("RUN_INTERRUPTED", exc)
            progress.emit("TERMINAL RUN_INTERRUPTED")
            raise
        except (ValueError, ZeroDivisionError) as exc:
            _rollback_completion_manifest(args.output_dir, exc)
            run_status.record_failure("RUN_FAILED", exc)
            progress.emit("TERMINAL RUN_FAILED")
            parser.error(str(exc))
        except Exception as exc:
            _rollback_completion_manifest(args.output_dir, exc)
            run_status.record_failure("RUN_FAILED", exc)
            progress.emit("TERMINAL RUN_FAILED")
            raise
        except BaseException as exc:
            _rollback_completion_manifest(args.output_dir, exc)
            run_status.record_failure("RUN_FAILED", exc)
            progress.emit("TERMINAL RUN_FAILED")
            raise

        if frozen_result is None:
            raise RuntimeError("completed run has no frozen result payload")

    if args.json:
        print(json.dumps(frozen_result, indent=2, allow_nan=False))
    else:
        print(format_terminal_summary(frozen_result))


if __name__ == "__main__":
    main()
