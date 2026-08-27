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
from enum import StrEnum
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

from scripts.continuation_bundle import (
    collect_runtime_provenance,
    utc_now,
    write_continuation_bundle,
)
from scripts.weil_legendre_schur_scout import scout
from scripts.cert.constants import require_one_prime_support
from scripts.weil_support_candidate_check import (
    CandidateStageError,
    run_candidate,
    theorem_boundary_payload,
)
from scripts.weil_support_continuation_scout import scout_support


DRIVER_VERSION = "continuation-driver-p13-v1"
SCOUT_RELATIVE_CONVERGENCE_TOLERANCE = 1e-2
PRECISION_STATUS_INSUFFICIENT = "INSUFFICIENT_PRECISION"
PRECISION_STATUS_STABLE = "PRECISION_STABLE"
PRECISION_STATUS_MATHEMATICAL_NEGATIVE = "MATHEMATICAL_NEGATIVE"
PRECISION_STATUS_ASSEMBLY_FAILED = "ASSEMBLY_FAILED"


class WorkflowState(StrEnum):
    VALIDATE_INPUT = "VALIDATE_INPUT"
    FLOAT_SCOUT = "FLOAT_SCOUT"
    CHECK_SCOUT_STABILITY = "CHECK_SCOUT_STABILITY"
    SELECT_DIMENSION = "SELECT_DIMENSION"
    RIGOROUS_PRECISION_SEARCH = "RIGOROUS_PRECISION_SEARCH"
    CHECK_RIGOROUS_STABILITY = "CHECK_RIGOROUS_STABILITY"
    EXACT_ROUNDING_SEARCH = "EXACT_ROUNDING_SEARCH"
    EXACT_WITNESS_CHECK = "EXACT_WITNESS_CHECK"
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
        WorkflowState.CANDIDATE_READY,
        WorkflowState.WITNESS_FAILED,
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


CACHE_VERSION = "continuation-driver-v4"
CACHE_SOURCE_PATHS = (
    "scripts/weil_continuation_driver.py",
    "scripts/weil_legendre_schur_scout.py",
    "scripts/weil_support_continuation_scout.py",
    "scripts/weil_support_candidate_check.py",
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
        temporary = cache_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
        temporary.replace(cache_path)
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
    def change(name: str) -> float:
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
    return {
        "from_precision_bits": previous["precision_bits"],
        "to_precision_bits": current["precision_bits"],
        "finite_block_midpoint_change": change(
            "finite_block_min_eigenvalue_midpoint"
        ),
        "schur_midpoint_change": change("schur_min_eigenvalue_midpoint"),
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
) -> dict[str, object]:
    import math

    attempts: list[dict[str, object]] = []
    pair_diagnostics: list[dict[str, object]] = []
    previous_schur: float | None = None
    previous_result: dict[str, object] | None = None
    for precision in precisions:
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
            return {
                "status": "precision_stable",
                "precision_status": PRECISION_STATUS_STABLE,
                "selected_precision_bits": precision,
                "attempts": attempts,
                "precision_pair_diagnostics": pair_diagnostics,
            }
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
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    machine = ContinuationStateMachine()

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
    matrix_bits_ladder = build_bit_ladder(matrix_bits_start, matrix_bits_max, 16)
    witness_bits_ladder = build_bit_ladder(witness_bits_start, witness_bits_max, 8)
    resolutions = build_scout_resolutions(dimensions, scout_resolution_count)

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

    machine.transition(
        WorkflowState.FLOAT_SCOUT,
        reason="validated_driver_inputs",
        details={
            "support": f"{support.numerator}/{support.denominator}",
            "dimension_count": len(dimensions),
            "resolution_count": len(resolutions),
        },
    )
    series: dict[int, list[ScoutDimensionResult]] = {
        dimension: [] for dimension in dimensions
    }
    for resolution in resolutions:
        try:
            raw_scout = scout(
                max_mode=resolution.max_mode,
                quadrature_order=resolution.quadrature_order,
                shift_order=resolution.shift_order,
                n_values=dimensions,
                support=support,
            )
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
        except Exception as exc:
            failure = {
                "resolution": resolution.as_dict(),
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            scout_failures.append(failure)
            scout_runs.append({"status": "failed", **failure})

    machine.transition(
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
    if not stable_dimensions:
        unstable = bool(scout_failures) or any(
            row["classification"] == "unstable" for row in reconnaissance
        )
        machine.transition(
            WorkflowState.SCOUT_UNSTABLE if unstable else WorkflowState.NO_CANDIDATE,
            reason=(
                "scout_evidence_unstable"
                if unstable
                else "no_stable_positive_scout_dimension"
            ),
            details={"stable_dimensions": []},
        )
        return finalize()

    machine.transition(
        WorkflowState.SELECT_DIMENSION,
        reason="stable_positive_dimensions_found",
        details={"stable_dimensions": stable_dimensions},
    )
    primary_dimension = stable_dimensions[0]
    fallback_dimensions = stable_dimensions[1:2]
    screening_dimensions = stable_dimensions[:2]

    machine.transition(
        WorkflowState.RIGOROUS_PRECISION_SEARCH,
        reason="selected_primary_and_fallback_dimensions",
        details={
            "primary_dimension": primary_dimension,
            "fallback_dimensions": fallback_dimensions,
        },
    )
    survivors: list[int] = []
    for dimension in screening_dimensions:
        try:
            screening = _escalate_rigorous_screen(
                support, dimension, precisions, residual_order, cache_dir
            )
            rigorous_screening.append({"dimension": dimension, **screening})
            selected_precision = screening["selected_precision_bits"]
            if screening["status"] == "precision_stable" and isinstance(
                selected_precision, int
            ):
                survivors.append(dimension)
        except Exception as exc:
            rigorous_failures.append(
                {
                    "dimension": dimension,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )

    machine.transition(
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
        machine.transition(target, reason=reason, details={"survivors": []})
        return finalize()

    machine.transition(
        WorkflowState.EXACT_ROUNDING_SEARCH,
        reason="rigorous_candidate_survived",
        details={"surviving_dimensions": survivors},
    )
    for dimension in survivors:
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

    ready = [
        candidate for candidate in candidates if candidate["status"] == "candidate_ready"
    ]
    selected_candidate_dimension = int(ready[0]["dimension"]) if ready else None
    if ready:
        machine.transition(
            WorkflowState.EXACT_WITNESS_CHECK,
            reason="outward_rounding_and_exact_schur_succeeded",
            details={"selected_candidate_dimension": selected_candidate_dimension},
        )
        machine.transition(
            WorkflowState.CANDIDATE_READY,
            reason="exact_rational_parity_witnesses_have_positive_margins",
            details={"selected_candidate_dimension": selected_candidate_dimension},
        )
        return finalize()

    failure_statuses = {failure.get("status") for failure in candidate_failures}
    if "candidate_check_failed" in failure_statuses or None in failure_statuses:
        machine.transition(
            WorkflowState.CANDIDATE_CHECK_FAILED,
            reason="candidate_stage_raised_unclassified_failure",
            details={"failure_statuses": sorted(str(status) for status in failure_statuses)},
        )
    elif failure_statuses == {"rounding_failed"}:
        machine.transition(
            WorkflowState.ROUNDING_FAILED,
            reason="matrix_bit_ladder_exhausted_before_exact_witness_stage",
            details={"failure_statuses": ["rounding_failed"]},
        )
    else:
        machine.transition(
            WorkflowState.EXACT_WITNESS_CHECK,
            reason="rounding_succeeded_but_no_witness_passed",
            details={"failure_statuses": sorted(str(status) for status in failure_statuses)},
        )
        machine.transition(
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
        lines.extend(
            [
                "No mathematical rejection was established.",
                "The available precision ladder did not stabilize.",
            ]
        )
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
    parser.add_argument("--precision-start", type=int, default=128)
    parser.add_argument("--precision-max", type=int, default=512)
    parser.add_argument("--residual-order", type=int, default=32)
    parser.add_argument("--matrix-bits-start", type=int, default=64)
    parser.add_argument("--matrix-bits-max", type=int, default=104)
    parser.add_argument("--witness-bits-start", type=int, default=32)
    parser.add_argument("--witness-bits-max", type=int, default=56)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--json",
        action="store_true",
        help="print the full machine-readable result JSON instead of the concise terminal summary",
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

    run_started_at = utc_now()
    provenance = collect_runtime_provenance()
    try:
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
            cache_dir=args.cache_dir,
        )
    except (ValueError, ZeroDivisionError) as exc:
        parser.error(str(exc))

    run_completed_at = utc_now()
    try:
        write_continuation_bundle(
            result,
            args.output_dir,
            run_started_at=run_started_at,
            run_completed_at=run_completed_at,
            provenance=provenance,
        )
    except ValueError as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(result, indent=2, allow_nan=False))
    else:
        print(format_terminal_summary(result))


if __name__ == "__main__":
    main()
