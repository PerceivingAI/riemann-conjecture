import argparse
import copy
import json
import ast
import os
from contextlib import contextmanager
from fractions import Fraction
from pathlib import Path

import pytest

from scripts import weil_continuation_driver as driver


class _InlineFuture:
    def __init__(self, fn, args, kwargs):
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def result(self):
        return self._fn(*self._args, **self._kwargs)


class _RecordingRunStatus:
    def __init__(self) -> None:
        self.updates: list[dict[str, object]] = []
        self.events: list[dict[str, object]] = []

    def update(self, **kwargs) -> dict[str, object]:
        self.updates.append(dict(kwargs))
        return dict(kwargs)

    def event(self, event: str, **kwargs) -> dict[str, object]:
        record = {"event": event, **kwargs}
        self.events.append(record)
        return record


class _InlineExecutor:
    _processes: dict[object, object] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def submit(self, fn, *args, **kwargs):
        return _InlineFuture(fn, args, kwargs)


def _minimal_terminal_result(support: Fraction, dimensions: list[int]) -> dict[str, object]:
    return {
        "role": "pre_theorem_continuation_driver",
        "driver_version": driver.DRIVER_VERSION,
        "cache_version": driver.CACHE_VERSION,
        "state": "NO_CANDIDATE",
        "status": "NO_CANDIDATE",
        "workflow_state": "NO_CANDIDATE",
        **driver.theorem_boundary_payload(),
        "support": str(support),
        "dimensions": dimensions,
    }


def _scout_result(dimensions: list[int], *, positive: bool) -> dict[str, object]:
    value = 1.0 if positive else -1.0
    return {
        "schur_rows": [
            {
                "N": dimension,
                "mu_scout": value,
                "finite_block_min_eigenvalue": value,
                "factor3_truncated_schur_min_eigenvalue": value,
            }
            for dimension in dimensions
        ]
    }


def _rigorous_result(*, positive: bool) -> dict[str, object]:
    value = 1.0 if positive else -1.0
    return {
        "mu_lower": value,
        "finite_block_min_eigenvalue_midpoint": value,
        "schur_min_eigenvalue_midpoint": value,
        "interval_widths": {
            "A_max": 1.0,
            "GV_max": 1.0,
            "G2_max": 1.0,
            "GR_max": 1.0,
            "mu": 1.0,
            "rho_R": 1.0,
            "residual_remainder": 1.0,
        },
    }


def _stable_candidate_confirmation(*args, **kwargs) -> dict[str, object]:
    return {
        "classification": "CANDIDATE_STABLE",
        "qualified": True,
        "selected_confirmation_precision_bits": 384,
        "attempts": [],
        "pair_diagnostics": [],
    }


def _candidate_attempt(
    precision: int,
    *,
    even_margin: str = "1/100",
    odd_margin: str = "1/200",
    width: float = 1.0,
) -> dict[str, object]:
    scalar_width = "1/1024" if width <= 1.0 else "1/512"
    matrix_widths = {
        name: {
            "max_width": width,
            "max_radius": width / 2,
            "row": 0,
            "column": 0,
            "midpoint_at_widest_entry": 1.0,
        }
        for name in ("A", "GV", "G2", "GR")
    }
    exact_widths = {
        name: {
            "max_width": "1/1024",
            "max_radius": "1/2048",
            "row": 0,
            "column": 0,
            "midpoint_at_widest_entry": "1/1",
        }
        for name in ("A", "GV", "G2", "GR")
    }
    return {
        "precision_bits": precision,
        "mu_lower": "7/10",
        "even_gershgorin_margin": even_margin,
        "odd_gershgorin_margin": odd_margin,
        "all_margins_positive": (
            Fraction(even_margin) > 0 and Fraction(odd_margin) > 0
        ),
        "working_precision_diagnostics": {
            "matrix_widths": matrix_widths,
            "scalar_widths": {
                "mu": scalar_width,
                "rho_R": scalar_width,
                "residual_remainder": scalar_width,
            },
        },
        "exact_rounding_diagnostics": {
            "rounding_succeeded": True,
            "matrix_widths": exact_widths,
        },
    }


def _candidate_ready(base: dict[str, object]) -> dict[str, object]:
    return {
        "status": "candidate_ready",
        "selected_matrix_bits": 64,
        "selected_witness_bits": 32,
        "attempts": [base],
    }


def _p13_candidate_ready_result() -> dict[str, object]:
    return {
        "state": "CANDIDATE_READY",
        "status": "CANDIDATE_READY",
        "support": "19/40",
        "dimensions": [48, 52, 56, 60, 64],
        "reconnaissance": [
            {"dimension": 48, "classification": "negative"},
            {"dimension": 52, "classification": "negative"},
            {"dimension": 56, "classification": "unstable"},
            {"dimension": 60, "classification": "stable_positive"},
            {"dimension": 64, "classification": "stable_positive"},
        ],
        "scout_primary_dimension": 60,
        "selected_candidate_dimension": 64,
        "rigorous_screening": [
            {
                "dimension": 60,
                "status": "precision_limit_reached",
                "precision_status": driver.PRECISION_STATUS_INSUFFICIENT,
                "attempts": [
                    {
                        "precision_bits": 256,
                        "precision_status": driver.PRECISION_STATUS_INSUFFICIENT,
                        "precision_reasons": ["midpoint_not_stable"],
                    },
                    {
                        "precision_bits": 384,
                        "precision_status": driver.PRECISION_STATUS_INSUFFICIENT,
                        "precision_reasons": ["midpoint_not_stable"],
                    },
                ],
            },
            {
                "dimension": 64,
                "status": "precision_stable",
                "precision_status": driver.PRECISION_STATUS_STABLE,
                "selected_precision_bits": 512,
                "attempts": [
                    {
                        "precision_bits": 384,
                        "precision_status": driver.PRECISION_STATUS_INSUFFICIENT,
                        "precision_reasons": ["no_prior_precision_for_stability_check"],
                    },
                    {
                        "precision_bits": 512,
                        "precision_status": driver.PRECISION_STATUS_STABLE,
                        "precision_reasons": ["stable_against_previous_precision"],
                    },
                ],
            },
        ],
        "candidates": [
            {
                "dimension": 64,
                "status": "candidate_ready",
                "selected_matrix_bits": 96,
                "selected_witness_bits": 48,
                "candidate_precision_stability": {
                    "classification": "CANDIDATE_STABLE",
                    "qualified": True,
                    "selected_confirmation_precision_bits": 640,
                    "attempts": [],
                    "pair_diagnostics": [],
                },
                "attempts": [
                    {
                        "all_margins_positive": True,
                        "mu_lower": "7/10",
                        "even_gershgorin_margin": "1/100",
                        "odd_gershgorin_margin": "1/200",
                    }
                ],
            }
        ],
        "theorem_status": False,
        "independently_verified": False,
        "whitelisted": False,
    }


def test_p13_candidate_ready_summary_is_concise_fallback_aware_and_pre_theorem() -> None:
    summary = driver.format_terminal_summary(_p13_candidate_ready_result())

    assert "Support continuation candidate search" in summary
    assert "T = 19/40" in summary
    assert "N=48  negative" in summary
    assert "N=56  unstable" in summary
    assert "N=60  stable-positive" in summary
    assert "Primary rigorous target: N=60" in summary
    assert "Fallback used: N=64" in summary
    assert "Selected candidate: N=64" in summary
    assert "Precision search (N=64):" in summary
    assert "384  insufficient precision - awaiting comparison" in summary
    assert "512  stable positive" in summary
    assert "matrix bits:   96" in summary
    assert "witness bits:  48" in summary
    assert "precision check: stable at next precision" in summary
    assert "confirmed at:  640 bits" in summary
    assert "mu_lower:      +" in summary
    assert "even margin:   +" in summary
    assert "odd margin:    +" in summary
    assert "RESULT: CANDIDATE_READY" in summary
    assert "This is not a theorem." in summary
    assert "Independent verifier admission has not been performed." in summary
    assert "7/10" not in summary


def test_p13_precision_limit_summary_preserves_p12_non_rejection_semantics() -> None:
    result = _p13_candidate_ready_result()
    result["state"] = result["status"] = "PRECISION_LIMIT_REACHED"
    result["selected_candidate_dimension"] = None
    result["candidates"] = []
    result["rigorous_screening"] = [
        {
            "dimension": 60,
            "status": "precision_limit_reached",
            "precision_status": driver.PRECISION_STATUS_INSUFFICIENT,
            "attempts": [
                {
                    "precision_bits": 104,
                    "precision_status": driver.PRECISION_STATUS_INSUFFICIENT,
                    "precision_reasons": ["contradicted_by_higher_precision"],
                },
                {
                    "precision_bits": 128,
                    "precision_status": driver.PRECISION_STATUS_INSUFFICIENT,
                    "precision_reasons": ["key_sign_changed_at_higher_precision"],
                },
            ],
        }
    ]

    summary = driver.format_terminal_summary(result)

    assert "104  insufficient precision - contradicted at higher precision" in summary
    assert "128  insufficient precision - sign changed" in summary
    assert "RESULT: PRECISION_LIMIT_REACHED" in summary
    assert "No mathematical rejection was established." in summary
    assert "NO_CANDIDATE" not in summary


def test_p13_no_candidate_summary_distinguishes_stable_rigorous_negative() -> None:
    result = _p13_candidate_ready_result()
    result["state"] = result["status"] = "NO_CANDIDATE"
    result["selected_candidate_dimension"] = None
    result["candidates"] = []
    result["rigorous_screening"] = [
        {
            "dimension": 60,
            "status": "mathematical_negative",
            "precision_status": driver.PRECISION_STATUS_MATHEMATICAL_NEGATIVE,
            "attempts": [
                {
                    "precision_bits": 384,
                    "precision_status": driver.PRECISION_STATUS_MATHEMATICAL_NEGATIVE,
                }
            ],
        }
    ]

    summary = driver.format_terminal_summary(result)

    assert "RESULT: NO_CANDIDATE" in summary
    assert "Rigorous screening found a stable mathematical negative." in summary
    assert "No mathematical rejection was established." not in summary


def test_p13_scout_unstable_summary_reports_no_rigorous_rejection() -> None:
    result = {
        "state": "SCOUT_UNSTABLE",
        "support": "19/40",
        "dimensions": [56],
        "reconnaissance": [{"dimension": 56, "classification": "unstable"}],
        "rigorous_screening": [],
        "candidates": [],
    }

    summary = driver.format_terminal_summary(result)

    assert "RESULT: SCOUT_UNSTABLE" in summary
    assert "Floating reconnaissance did not stabilize." in summary
    assert "No rigorous mathematical rejection was established." in summary


def test_p13_formatter_does_not_mutate_result() -> None:
    result = _p13_candidate_ready_result()
    original = copy.deepcopy(result)

    driver.format_terminal_summary(result)

    assert result == original


def test_p10_exact_support_parsing_is_rational_and_fail_closed() -> None:
    assert driver.parse_support("19/40") == Fraction(19, 40)
    assert driver.parse_support(" 0.475 ") == Fraction(19, 40)

    for invalid in ("", "0", "-1/2", "not-a-rational", "1/0"):
        with pytest.raises(ValueError):
            driver.parse_support(invalid)


def test_p10_dimension_range_validation() -> None:
    valid = argparse.Namespace(n=None, n_min=48, n_max=56, n_step=4)
    assert driver.dimensions_from_args(valid) == [48, 52, 56]

    invalid_ranges = (
        argparse.Namespace(n=None, n_min=48, n_max=None, n_step=4),
        argparse.Namespace(n=None, n_min=56, n_max=48, n_step=4),
        argparse.Namespace(n=None, n_min=48, n_max=56, n_step=0),
        argparse.Namespace(n="48", n_min=48, n_max=56, n_step=4),
    )
    for args in invalid_ranges:
        with pytest.raises(ValueError):
            driver.dimensions_from_args(args)


def test_p10_invalid_one_prime_support_is_rejected_before_any_stage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scout_calls: list[Fraction] = []
    monkeypatch.setattr(
        driver,
        "scout",
        lambda **kwargs: scout_calls.append(kwargs["support"]),
    )

    with pytest.raises(ValueError, match="one-prime window"):
        driver.run_driver(Fraction(3, 5), [48])

    assert scout_calls == []


def test_parse_dimensions_requires_positive_unique_explicit_values() -> None:
    assert driver.parse_dimensions("48, 52,56") == [48, 52, 56]
    with pytest.raises(ValueError, match="unique"):
        driver.parse_dimensions("48,48")
    with pytest.raises(ValueError, match="positive"):
        driver.parse_dimensions("0")


def test_scout_resolution_plan_increases_with_requested_maximum() -> None:
    plan = driver.build_scout_resolutions([48, 80])

    assert len(plan) == 3
    assert [item.max_mode for item in plan] == sorted(item.max_mode for item in plan)
    assert [item.quadrature_order for item in plan] == sorted(
        item.quadrature_order for item in plan
    )
    assert plan[-1].max_mode > 80


def test_precision_ladder_is_bounded_and_increasing() -> None:
    assert driver.build_precision_ladder(128, 512) == [128, 256, 384, 512]
    assert driver.build_precision_ladder(300, 640) == [300, 384, 512, 640]


def test_p11_scout_tolerance_accepts_historical_drift_but_rejects_large_drift() -> None:
    historical = [
        driver.ScoutDimensionResult(48, 0.73, 5.86e-5, value, 120, 700, 350, "")
        for value in (5.694914867630464e-5, 5.6600646344646804e-5, 5.647773382590833e-5)
    ]
    excessive = [
        driver.ScoutDimensionResult(48, 0.73, 5.86e-5, value, 120, 700, 350, "")
        for value in (5.70e-5, 5.50e-5, 5.30e-5)
    ]

    assert driver.SCOUT_RELATIVE_CONVERGENCE_TOLERANCE == pytest.approx(0.01)
    assert driver._classify_reconnaissance(historical) == "stable_positive"
    assert driver._classify_reconnaissance(excessive) == "unstable"


P12_PRECISION_INCIDENT = {
    104: {
        "mu_lower": 0.7313021813837909,
        "finite_block_min_eigenvalue_midpoint": -196629712.19620165,
        "schur_min_eigenvalue_midpoint": -909134247521819.0,
        "interval_widths": {
            "A_max": 226232615168.0,
            "GV_max": 0.0021600818436127156,
            "G2_max": 1.1133309412469849e24,
            "GR_max": 3.065310024255086e-29,
            "mu": 7.48695076695505e-30,
            "rho_R": 5.660255926359853e-30,
            "residual_remainder": 1.6476927260384555e-49,
        },
    },
    128: {
        "mu_lower": 0.7313021813837909,
        "finite_block_min_eigenvalue_midpoint": 0.00018156780228872172,
        "schur_min_eigenvalue_midpoint": 0.00017535660691424883,
        "interval_widths": {
            "A_max": 13403.878295898438,
            "GV_max": 1.451135227606426e-10,
            "G2_max": 3908566988.0,
            "GR_max": 1.8270671512216843e-36,
            "mu": 4.827891973632074e-37,
            "rho_R": 3.385530377589114e-37,
            "residual_remainder": 9.686901812094774e-57,
        },
    },
    256: {
        "mu_lower": 0.7313021813837909,
        "finite_block_min_eigenvalue_midpoint": 0.00018157137450517234,
        "schur_min_eigenvalue_midpoint": 0.00017030162781616563,
        "interval_widths": {
            "A_max": 3.9406926189081055e-35,
            "GV_max": 3.3363714279054758e-49,
            "G2_max": 4.0470886318609074e-36,
            "GR_max": 5.369267778849058e-75,
            "mu": 1.3148860324177117e-75,
            "rho_R": 9.949179583483123e-76,
            "residual_remainder": 2.8467245892718968e-95,
        },
    },
    384: {
        "mu_lower": 0.7313021813837909,
        "finite_block_min_eigenvalue_midpoint": 0.00018157137450517234,
        "schur_min_eigenvalue_midpoint": 0.00017030162781616563,
        "interval_widths": {
            "A_max": 1.1592685891725904e-73,
            "GV_max": 1.1220836286427468e-87,
            "G2_max": 1.1905613237828362e-74,
            "GR_max": 1.5778859855222997e-113,
            "mu": 4.158504062871947e-114,
            "rho_R": 2.913649335206505e-114,
            "residual_remainder": 8.481593197030518e-134,
        },
    },
}


def test_p12_precision_incident_escalates_to_stability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout_support",
        lambda support, *, dimension, prec, residual_order: P12_PRECISION_INCIDENT[prec],
    )

    result = driver._escalate_rigorous_screen(
        Fraction(2, 5), 40, [104, 128, 256, 384], 32
    )

    assert result["status"] == "precision_stable"
    assert result["precision_status"] == driver.PRECISION_STATUS_STABLE
    assert result["selected_precision_bits"] == 384
    attempts = result["attempts"]
    assert [attempt["precision_status"] for attempt in attempts] == [
        driver.PRECISION_STATUS_INSUFFICIENT,
        driver.PRECISION_STATUS_INSUFFICIENT,
        driver.PRECISION_STATUS_INSUFFICIENT,
        driver.PRECISION_STATUS_STABLE,
    ]
    assert attempts[0]["finite_block_min_eigenvalue_midpoint"] < 0
    assert attempts[0]["schur_min_eigenvalue_midpoint"] < -1e12
    assert "contradicted_by_higher_precision" in attempts[0]["precision_reasons"]
    assert "key_sign_changed_at_higher_precision" in attempts[1]["precision_reasons"]
    assert "midpoint_not_stable" in attempts[2]["precision_reasons"]
    assert all(
        attempt["precision_status"] != driver.PRECISION_STATUS_MATHEMATICAL_NEGATIVE
        for attempt in attempts
    )


def test_p12_unresolved_precision_incident_is_not_no_candidate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    monkeypatch.setattr(
        driver,
        "scout_support",
        lambda support, *, dimension, prec, residual_order: P12_PRECISION_INCIDENT[prec],
    )

    result = driver.run_driver(
        Fraction(2, 5),
        [40],
        precision_start=104,
        precision_max=128,
        cache_dir=None,
    )

    assert result["state"] == "PRECISION_LIMIT_REACHED"
    assert result["state"] != "NO_CANDIDATE"
    rigorous = result["rigorous_screening"][0]
    assert rigorous["precision_status"] == driver.PRECISION_STATUS_INSUFFICIENT
    assert [attempt["precision_status"] for attempt in rigorous["attempts"]] == [
        driver.PRECISION_STATUS_INSUFFICIENT,
        driver.PRECISION_STATUS_INSUFFICIENT,
    ]
    assert result["candidates"] == []


def test_precision_pair_diagnostics_track_widths_changes_and_signs() -> None:
    previous = {
        "precision_bits": 256,
        "finite_block_min_eigenvalue_midpoint": 0.1,
        "schur_min_eigenvalue_midpoint": 0.02,
        "mu_lower": 0.7,
        "interval_widths": {
            "A_max": 2.0,
            "GV_max": 2.0,
            "G2_max": 2.0,
            "GR_max": 2.0,
            "mu": 2.0,
            "rho_R": 2.0,
            "residual_remainder": 2.0,
        },
    }
    current = {
        **previous,
        "precision_bits": 384,
        "finite_block_min_eigenvalue_midpoint": 0.1001,
        "schur_min_eigenvalue_midpoint": 0.0201,
        "interval_widths": {
            name: 1.0 for name in previous["interval_widths"]
        },
    }

    diagnostics = driver._precision_pair_diagnostics(previous, current)

    assert diagnostics["from_precision_bits"] == 256
    assert diagnostics["to_precision_bits"] == 384
    assert diagnostics["widths_reduced"] is True
    assert diagnostics["all_key_signs_stable"] is True


def test_precision_escalation_reports_limit_without_false_candidate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout_support",
        lambda support, *, dimension, prec, residual_order: {
            **_rigorous_result(positive=True),
            "schur_min_eigenvalue_midpoint": float(prec),
        },
    )

    result = driver._escalate_rigorous_screen(
        Fraction(19, 40), 64, [128, 256, 384], 32
    )

    assert result["status"] == "precision_limit_reached"
    assert result["selected_precision_bits"] is None
    assert len(result["attempts"]) == 3


def test_precision_stability_requires_sign_and_width_stability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    width_names = (
        "A_max",
        "GV_max",
        "G2_max",
        "GR_max",
        "mu",
        "rho_R",
        "residual_remainder",
    )

    def fake_screen(support, *, dimension, prec, residual_order):
        return {
            "mu_lower": -1.0 if prec == 128 else 1.0,
            "finite_block_min_eigenvalue_midpoint": -1.0 if prec == 128 else 1.0,
            "schur_min_eigenvalue_midpoint": 0.1 if prec == 128 else 0.10001,
            "interval_widths": {
                name: 2.0 if prec == 128 else 3.0 for name in width_names
            },
        }

    monkeypatch.setattr(driver, "scout_support", fake_screen)
    result = driver._escalate_rigorous_screen(
        Fraction(19, 40), 64, [128, 256], 32
    )

    assert result["status"] == "precision_limit_reached"
    diagnostics = result["precision_pair_diagnostics"][-1]
    assert diagnostics["all_key_signs_stable"] is False
    assert diagnostics["widths_reduced"] is False


def test_candidate_construction_escalates_rounding_and_witness_bits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[int, int]] = []

    def fake_candidate(
        support, *, dimension, prec, residual_order, matrix_bits, witness_bits
    ):
        calls.append((matrix_bits, witness_bits))
        return {
            "all_margins_positive": matrix_bits >= 80 and witness_bits >= 40,
        }

    monkeypatch.setattr(driver, "run_candidate", fake_candidate)
    result = driver._construct_candidate(
        Fraction(19, 40),
        64,
        384,
        32,
        [64, 80],
        [32, 40],
        None,
    )

    assert result["status"] == "candidate_ready"
    assert result["selected_matrix_bits"] == 80
    assert result["selected_witness_bits"] == 40
    assert calls == [(64, 32), (64, 40), (80, 32), (80, 40)]


def test_candidate_precision_confirmation_stops_after_first_stable_higher_precision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []
    base = _candidate_attempt(384, width=2.0)

    def fake_candidate(
        support, *, dimension, prec, residual_order, matrix_bits, witness_bits
    ):
        calls.append(prec)
        return _candidate_attempt(prec, width=1.0)

    monkeypatch.setattr(driver, "run_candidate", fake_candidate)
    result = driver._confirm_candidate_precision_stability(
        Fraction(19, 40),
        68,
        _candidate_ready(base),
        32,
        precision_step=128,
        extra_steps=2,
        cache_dir=None,
    )

    assert result["classification"] == "CANDIDATE_STABLE"
    assert result["qualified"] is True
    assert result["selected_confirmation_precision_bits"] == 512
    assert calls == [512]
    diagnostics = result["pair_diagnostics"][0]
    assert diagnostics["conditioning_improved"] is True
    assert diagnostics["exact_margins_stable"] is True
    assert diagnostics["exact_rounding_survives"] is True


def test_candidate_precision_confirmation_uses_third_precision_when_needed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []
    base = _candidate_attempt(384, even_margin="1/100", width=2.0)

    def fake_candidate(
        support, *, dimension, prec, residual_order, matrix_bits, witness_bits
    ):
        calls.append(prec)
        if prec == 512:
            return _candidate_attempt(prec, even_margin="1/50", width=1.0)
        return _candidate_attempt(prec, even_margin="1/50", width=0.5)

    monkeypatch.setattr(driver, "run_candidate", fake_candidate)
    result = driver._confirm_candidate_precision_stability(
        Fraction(19, 40),
        68,
        _candidate_ready(base),
        32,
        precision_step=128,
        extra_steps=2,
        cache_dir=None,
    )

    assert result["classification"] == "CANDIDATE_STABLE_AFTER_ESCALATION"
    assert result["qualified"] is True
    assert result["selected_confirmation_precision_bits"] == 640
    assert calls == [512, 640]
    assert result["pair_diagnostics"][0]["exact_margins_stable"] is False
    assert result["pair_diagnostics"][1]["exact_margins_stable"] is True


def test_candidate_precision_confirmation_fails_closed_on_persistent_instability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    base = _candidate_attempt(384, width=2.0)

    def fake_candidate(
        support, *, dimension, prec, residual_order, matrix_bits, witness_bits
    ):
        return _candidate_attempt(prec, even_margin="-1/100", width=1.0 / prec)

    monkeypatch.setattr(driver, "run_candidate", fake_candidate)
    result = driver._confirm_candidate_precision_stability(
        Fraction(19, 40),
        68,
        _candidate_ready(base),
        32,
        precision_step=128,
        extra_steps=2,
        cache_dir=None,
    )

    assert result["classification"] == "INSUFFICIENT_WORKING_PRECISION"
    assert result["qualified"] is False
    assert result["selected_confirmation_precision_bits"] is None
    assert len(result["attempts"]) == 3


def test_driver_candidate_precision_instability_is_not_candidate_ready(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    monkeypatch.setattr(
        driver,
        "_escalate_rigorous_screen",
        lambda *args, **kwargs: {
            "status": "precision_stable",
            "selected_precision_bits": 384,
            "attempts": [],
            "precision_pair_diagnostics": [],
        },
    )
    monkeypatch.setattr(
        driver,
        "_construct_candidate",
        lambda *args, **kwargs: _candidate_ready(_candidate_attempt(384)),
    )
    monkeypatch.setattr(
        driver,
        "_confirm_candidate_precision_stability",
        lambda *args, **kwargs: {
            "classification": "INSUFFICIENT_WORKING_PRECISION",
            "qualified": False,
            "selected_confirmation_precision_bits": None,
            "attempts": [],
            "pair_diagnostics": [],
        },
    )

    result = driver.run_driver(Fraction(19, 40), [68])

    assert result["state"] == "PRECISION_LIMIT_REACHED"
    assert result["selected_candidate_dimension"] is None
    assert result["candidates"][0]["candidate_precision_stability"]["qualified"] is False
    trace = [row["to"] for row in result["workflow_trace"]]
    assert trace[-2:] == ["CANDIDATE_PRECISION_CONFIRMATION", "PRECISION_LIMIT_REACHED"]


def test_candidate_failure_stage_is_structured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "run_candidate",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            driver.CandidateStageError("rounding", "serialized complement lost positivity")
        ),
    )
    rounding = driver._construct_candidate(
        Fraction(19, 40), 64, 384, 32, [64], [32], None
    )
    assert rounding["status"] == "rounding_failed"
    assert rounding["attempts"][0]["failure_stage"] == "rounding"

    monkeypatch.setattr(
        driver,
        "run_candidate",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            driver.CandidateStageError("witness", "witness margin is not positive")
        ),
    )
    witness = driver._construct_candidate(
        Fraction(19, 40), 64, 384, 32, [64], [32], None
    )
    assert witness["status"] == "witness_failed"
    assert witness["attempts"][0]["failure_stage"] == "witness"


def test_cache_key_changes_with_source_fingerprint(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    calls: list[str] = []
    fingerprint = {"value": "source-a"}
    monkeypatch.setattr(
        driver, "_cache_source_fingerprint", lambda: fingerprint["value"]
    )

    def produce() -> dict[str, object]:
        calls.append(fingerprint["value"])
        return {"source": fingerprint["value"]}

    first, first_hit = driver._cached_result(tmp_path, {"kind": "test"}, produce)
    second, second_hit = driver._cached_result(tmp_path, {"kind": "test"}, produce)
    fingerprint["value"] = "source-b"
    third, third_hit = driver._cached_result(tmp_path, {"kind": "test"}, produce)

    assert first == second == {"source": "source-a"}
    assert third == {"source": "source-b"}
    assert (first_hit, second_hit, third_hit) == (False, True, False)
    assert calls == ["source-a", "source-b"]


def test_unexpected_candidate_check_failure_has_distinct_final_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    monkeypatch.setattr(
        driver,
        "_escalate_rigorous_screen",
        lambda *args, **kwargs: {
            "status": "precision_stable",
            "selected_precision_bits": 256,
            "attempts": [],
            "precision_pair_diagnostics": [],
        },
    )
    monkeypatch.setattr(
        driver,
        "_construct_candidate",
        lambda *args, **kwargs: {
            "status": "candidate_check_failed",
            "selected_matrix_bits": None,
            "selected_witness_bits": None,
            "attempts": [],
        },
    )

    result = driver.run_driver(Fraction(19, 40), [48])

    assert result["state"] == "CANDIDATE_CHECK_FAILED"
    assert result["selected_candidate_dimension"] is None


def test_cache_fingerprint_covers_candidate_semantics_dependencies() -> None:
    required = {
        "scripts/cert/exact_prime_schur_common.py",
        "scripts/cert/residual_kernel.py",
        "scripts/cert/matrices.py",
        "scripts/precision_diagnostics.py",
    }
    assert required.issubset(set(driver.CACHE_SOURCE_PATHS))
    assert "scripts/cert/exact_prime_schur_certificate.py" not in driver.CACHE_SOURCE_PATHS


def test_reconnaissance_requires_sign_stability_and_convergence() -> None:
    stable = [
        driver.ScoutDimensionResult(64, 1.0, 0.5, value, 120, 700, 350, "")
        for value in (0.0100, 0.010005, 0.010002)
    ]
    unstable = [
        driver.ScoutDimensionResult(64, 1.0, 0.5, value, 120, 700, 350, "")
        for value in (0.010, -0.002, 0.010)
    ]

    assert driver._classify_reconnaissance(stable) == "stable_positive"
    assert driver._classify_reconnaissance(unstable) == "unstable"

def test_driver_rejects_invalid_programmatic_inputs() -> None:
    with pytest.raises(ValueError, match="one-prime window"):
        driver.run_driver(Fraction(3, 5), [48])
    with pytest.raises(ValueError, match="positive"):
        driver.run_driver(Fraction(19, 40), [0])
    with pytest.raises(ValueError, match="unique"):
        driver.run_driver(Fraction(19, 40), [48, 48])
    with pytest.raises(ValueError, match="matrix_bits_start"):
        driver.run_driver(Fraction(19, 40), [48], matrix_bits_start=8)
    with pytest.raises(ValueError, match="witness_bits_start"):
        driver.run_driver(Fraction(19, 40), [48], witness_bits_start=4)
    with pytest.raises(ValueError, match="candidate_precision_step"):
        driver.run_driver(Fraction(19, 40), [48], candidate_precision_step=0)
    with pytest.raises(ValueError, match="candidate_precision_extra_steps"):
        driver.run_driver(Fraction(19, 40), [48], candidate_precision_extra_steps=0)
    with pytest.raises(ValueError, match="scout_workers"):
        driver.run_driver(Fraction(19, 40), [48], scout_workers=0)
    with pytest.raises(ValueError, match="rigorous_workers"):
        driver.run_driver(Fraction(19, 40), [48], rigorous_workers=0)
    with pytest.raises(ValueError, match="matrix_bits"):
        driver.run_candidate(
            Fraction(19, 40),
            dimension=64,
            prec=128,
            residual_order=32,
            matrix_bits=8,
            witness_bits=32,
        )


def test_parallel_orchestration_preserves_deterministic_result_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pool_sizes: list[int] = []
    rigorous_calls: list[int] = []

    monkeypatch.setattr(
        driver,
        "_spawn_process_pool",
        lambda workers: (pool_sizes.append(workers) or _InlineExecutor()),
    )
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )

    def fake_rigorous(support, dimension, precisions, residual_order, cache_dir=None):
        rigorous_calls.append(dimension)
        return {
            "status": "precision_stable",
            "selected_precision_bits": 256,
            "attempts": [],
            "precision_pair_diagnostics": [],
        }

    monkeypatch.setattr(driver, "_escalate_rigorous_screen", fake_rigorous)
    monkeypatch.setattr(
        driver,
        "_construct_candidate",
        lambda *args, **kwargs: {
            "status": "candidate_ready",
            "selected_matrix_bits": 64,
            "selected_witness_bits": 32,
            "attempts": [],
        },
    )
    monkeypatch.setattr(
        driver,
        "_confirm_candidate_precision_stability",
        _stable_candidate_confirmation,
    )

    result = driver.run_driver(
        Fraction(19, 40),
        [52, 48, 56],
        scout_workers=3,
        rigorous_workers=2,
    )

    assert result["state"] == "CANDIDATE_READY"
    assert result["scout_workers"] == 3
    assert result["rigorous_workers"] == 2
    assert [run["resolution"]["level"] for run in result["scout_runs"]] == [0, 1, 2]
    assert [row["dimension"] for row in result["rigorous_screening"]] == [48, 52]
    assert rigorous_calls == [48, 52]
    assert result["selected_candidate_dimension"] == 48
    assert pool_sizes == [3, 2]


def test_run_driver_updates_live_status_without_changing_terminal_semantics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=False
        ),
    )
    status = _RecordingRunStatus()

    result = driver.run_driver(Fraction(19, 40), [48], run_status=status)

    assert result["state"] == "NO_CANDIDATE"
    workflow_states = [update["workflow_state"] for update in status.updates]
    assert workflow_states[0] == "VALIDATE_INPUT"
    assert "FLOAT_SCOUT" in workflow_states
    assert workflow_states[-1] == "NO_CANDIDATE"
    scout_operations = [
        update["current_operation"]
        for update in status.updates
        if isinstance(update.get("current_operation"), dict)
        and update["current_operation"].get("stage") == "FLOAT_SCOUT"
    ]
    assert any(operation.get("resolution_level") == 0 for operation in scout_operations)
    assert status.updates[-1]["current_operation"] == {
        "stage": "FINAL_RESULT_PENDING_BUNDLE",
        "result_state": "NO_CANDIDATE",
    }
    assert status.updates[-1]["terminal"] is False
    event_names = [event["event"] for event in status.events]
    assert event_names[:3] == [
        "VALIDATION_STARTED",
        "VALIDATION_COMPLETED",
        "WORKFLOW_STATE_CHANGED",
    ]
    assert "SCOUT_STAGE_STARTED" in event_names
    assert event_names.count("SCOUT_RESOLUTION_STARTED") == 3
    assert event_names.count("SCOUT_RESOLUTION_COMPLETED") == 3
    assert "SCOUT_STAGE_COMPLETED" in event_names
    assert event_names[-2:] == ["WORKFLOW_STATE_CHANGED", "RUN_RESULT_REACHED"]
    assert status.events[-1]["result_state"] == "NO_CANDIDATE"


def test_live_progress_reports_stage_and_precision_milestones(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    monkeypatch.setattr(
        driver,
        "scout_support",
        lambda *args, **kwargs: _rigorous_result(positive=True),
    )
    monkeypatch.setattr(
        driver,
        "_construct_candidate",
        lambda *args, **kwargs: {
            "status": "candidate_ready",
            "selected_matrix_bits": 64,
            "selected_witness_bits": 32,
            "attempts": [],
        },
    )
    monkeypatch.setattr(
        driver,
        "_confirm_candidate_precision_stability",
        _stable_candidate_confirmation,
    )
    progress = driver.LiveProgress(started_monotonic=driver.time.monotonic())

    result = driver.run_driver(
        Fraction(19, 40),
        [48],
        precision_start=128,
        precision_max=256,
        progress=progress,
    )

    assert result["state"] == "CANDIDATE_READY"
    stderr = capsys.readouterr().err
    assert "] SCOUT resolutions=3 workers=1" in stderr
    assert "] SCOUT resolution 1/3 complete" in stderr
    assert "] SCOUT stable-positive begins at N=48" in stderr
    assert "] RIGOROUS targets N=48 workers=1" in stderr
    assert "] RIGOROUS N=48 started" in stderr
    assert "] N=48 precision=128 started" in stderr
    assert "] N=48 precision=128 insufficient" in stderr
    assert "] N=48 precision=256 started" in stderr
    assert "] N=48 precision=256 stable" in stderr
    assert "] RIGOROUS N=48 complete status=precision_stable" in stderr
    assert "] RIGOROUS complete survivors=1 failures=0" in stderr
    assert "] CANDIDATE N=48 rounding started" in stderr
    assert "] CANDIDATE N=48 rounding complete status=candidate_ready" in stderr
    assert "] CANDIDATE N=48 confirmation started" in stderr
    assert "] CANDIDATE N=48 confirmation complete status=CANDIDATE_STABLE" in stderr


def test_driver_propagates_precision_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    monkeypatch.setattr(
        driver,
        "_escalate_rigorous_screen",
        lambda *args, **kwargs: {
            "status": "precision_limit_reached",
            "selected_precision_bits": None,
            "attempts": [],
            "precision_pair_diagnostics": [],
        },
    )

    result = driver.run_driver(Fraction(19, 40), [48, 52])

    assert result["state"] == "PRECISION_LIMIT_REACHED"
    assert result["selected_dimension"] is None


def test_fallback_candidate_becomes_selected_dimension(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    monkeypatch.setattr(
        driver,
        "_escalate_rigorous_screen",
        lambda support, dimension, precisions, residual_order, cache_dir=None: (
            {
                "status": "precision_limit_reached",
                "selected_precision_bits": None,
                "attempts": [],
                "precision_pair_diagnostics": [],
            }
            if dimension == 48
            else {
                "status": "precision_stable",
                "selected_precision_bits": 256,
                "attempts": [],
                "precision_pair_diagnostics": [],
            }
        ),
    )
    monkeypatch.setattr(
        driver,
        "_confirm_candidate_precision_stability",
        _stable_candidate_confirmation,
    )

    monkeypatch.setattr(
        driver,
        "_construct_candidate",
        lambda *args, **kwargs: {
            "status": "candidate_ready",
            "selected_matrix_bits": 64,
            "selected_witness_bits": 32,
            "attempts": [],
        },
    )

    result = driver.run_driver(Fraction(19, 40), [48, 52])

    assert result["state"] == "CANDIDATE_READY"
    assert result["scout_primary_dimension"] == 48
    assert result["selected_dimension"] == 52
    assert result["selected_candidate_dimension"] == 52


def test_cli_writes_requested_output_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path, capsys: pytest.CaptureFixture[str]
) -> None:
    output_dir = tmp_path / "continuation"
    captured_kwargs: dict[str, object] = {}
    provenance_calls: list[Path | None] = []
    identity_before_work: list[bytes] = []
    provenance = {
        "git_commit": "c" * 40,
        "git_dirty": False,
        "python_version": "3.14.0",
        "python_implementation": "CPython",
        "python_flint_version": "0.9.0",
    }

    def fake_provenance(*, exclude_output_dir=None):
        provenance_calls.append(exclude_output_dir)
        return dict(provenance)

    def fake_run_driver(support, dimensions, **kwargs):
        identity_path = output_dir / ".live" / "run.json"
        assert identity_path.is_file()
        identity_before_work.append(identity_path.read_bytes())
        captured_kwargs.update(kwargs)
        return _minimal_terminal_result(support, dimensions)

    terminal_order: list[str] = []
    original_update = driver.RunStatusWriter.update
    original_event = driver.RunStatusWriter.event
    original_heartbeats = driver.RunStatusWriter.periodic_heartbeats

    @contextmanager
    def recording_heartbeats(self, *args, **kwargs):
        with original_heartbeats(self, *args, **kwargs) as heartbeat:
            yield heartbeat
        terminal_order.append("HEARTBEAT_STOPPED")

    def recording_update(self, **kwargs):
        if kwargs.get("terminal") is True:
            terminal_order.append("STATUS_TERMINAL")
        return original_update(self, **kwargs)

    def recording_event(self, event, **kwargs):
        if event == "RUN_COMPLETED":
            terminal_order.append("RUN_COMPLETED")
        return original_event(self, event, **kwargs)

    monkeypatch.setattr(driver.RunStatusWriter, "periodic_heartbeats", recording_heartbeats)
    monkeypatch.setattr(driver.RunStatusWriter, "update", recording_update)
    monkeypatch.setattr(driver.RunStatusWriter, "event", recording_event)
    monkeypatch.setattr(driver, "collect_runtime_provenance", fake_provenance)
    monkeypatch.setattr(driver, "run_driver", fake_run_driver)
    monkeypatch.setattr(
        "sys.argv",
        [
            "weil_continuation_driver",
            "--support",
            "19/40",
            "--n",
            "48",
            "--output-dir",
            str(output_dir),
        ],
    )

    driver.main()

    summary = (output_dir / "summary.json").read_text(encoding="utf-8")
    manifest = (output_dir / "run-manifest.json").read_text(encoding="utf-8")
    live_identity_path = output_dir / ".live" / "run.json"
    live_identity = json.loads(live_identity_path.read_text(encoding="utf-8"))
    live_status = json.loads(
        (output_dir / ".live" / "run-status.json").read_text(encoding="utf-8")
    )
    lock_metadata = json.loads(
        (output_dir / ".run.lock").read_text(encoding="utf-8")
    )
    live_events = [
        json.loads(line)
        for line in (output_dir / ".live" / "events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert '"state": "NO_CANDIDATE"' in summary
    assert '"final_state": "NO_CANDIDATE"' in manifest
    manifest_payload = json.loads(manifest)
    assert manifest_payload["provenance"] == provenance
    assert provenance_calls == [output_dir]
    assert len(identity_before_work) == 1
    assert live_identity_path.read_bytes() == identity_before_work[0]
    assert live_identity["format"] == "riemann-run-identity-v1"
    assert live_identity["driver"] == "weil_continuation_driver"
    assert live_identity["driver_version"] == driver.DRIVER_VERSION
    assert live_identity["support"] == "19/40"
    assert live_identity["dimensions"] == [48]
    assert live_identity["git_commit"] == "c" * 40
    assert live_identity["git_dirty"] is False
    assert live_status["format"] == "riemann-live-run-v1"
    assert lock_metadata["format"] == "riemann-output-lock-v1"
    assert live_identity["run_id"] == live_status["run_id"]
    assert live_identity["run_id"] == lock_metadata["run_id"]
    assert live_identity["pid"] == live_status["pid"]
    assert live_identity["started_at_utc"] == live_status["started_at_utc"]
    assert lock_metadata["run_id"] == live_status["run_id"]
    assert lock_metadata["pid"] == live_status["pid"]
    assert lock_metadata["started_at_utc"] == live_status["started_at_utc"]
    assert live_status["support"] == "19/40"
    assert live_status["workflow_state"] == "NO_CANDIDATE"
    assert live_status["current_operation"] is None
    assert live_status["terminal"] is True
    assert [event["seq"] for event in live_events] == list(
        range(1, len(live_events) + 1)
    )
    assert [event["event"] for event in live_events] == [
        "RUN_STARTED",
        "WORKER_CLEANUP_VERIFIED",
        "RESULT_PAYLOAD_FROZEN",
        "BUNDLE_FINALIZATION_STARTED",
        "BUNDLE_FINALIZATION_COMPLETED",
        "RUN_COMPLETED",
    ]
    assert terminal_order == ["HEARTBEAT_STOPPED", "STATUS_TERMINAL", "RUN_COMPLETED"]
    assert manifest_payload["finalization"]["worker_cleanup"] == {
        "verified": True,
        "executors_shutdown": 0,
        "worker_processes_reaped": 0,
        "stages": [],
    }
    frozen_digest = manifest_payload["finalization"]["result_payload_sha256"]
    assert isinstance(frozen_digest, str) and len(frozen_digest) == 64
    assert live_events[2]["sha256"] == frozen_digest
    assert manifest_payload["finalization"]["manifest_written_last"] is True
    assert all(event["run_id"] == live_status["run_id"] for event in live_events)
    assert live_events[-1]["final_state"] == "NO_CANDIDATE"
    captured = capsys.readouterr()
    terminal = captured.out
    assert "Support continuation candidate search" in terminal
    assert "RESULT: NO_CANDIDATE" in terminal
    assert '"state"' not in terminal
    assert "] RUN T=19/40 dimensions=48" in captured.err
    assert "] BUNDLE write started" in captured.err
    assert "] BUNDLE write complete" in captured.err
    assert "] TERMINAL NO_CANDIDATE" in captured.err
    assert captured_kwargs["progress"].enabled is True
    available_cpus = driver.os.cpu_count() or 1
    assert captured_kwargs["scout_workers"] == min(
        driver.CLI_SCOUT_WORKERS_MAX, available_cpus
    )
    assert captured_kwargs["rigorous_workers"] == min(
        driver.CLI_RIGOROUS_WORKERS_MAX, available_cpus
    )


def test_live_progress_stderr_failure_is_nonfatal(monkeypatch: pytest.MonkeyPatch) -> None:
    class BrokenStderr:
        def write(self, text: str) -> int:
            raise BrokenPipeError("closed stderr")

        def flush(self) -> None:
            raise BrokenPipeError("closed stderr")

    monkeypatch.setattr(driver.sys, "stderr", BrokenStderr())
    driver.LiveProgress().emit("still nonfatal")


def test_observability_payloads_are_bounded_without_mutating_source() -> None:
    source = {
        "stable_dimensions": list(range(1000)),
        "message": "x" * 5000,
    }
    bounded = driver._bounded_observability_value(source)

    assert source["stable_dimensions"] == list(range(1000))
    assert isinstance(bounded, dict)
    dimensions = bounded["stable_dimensions"]
    assert dimensions["count"] == 1000
    assert dimensions["truncated"] is True
    assert dimensions["preview"] == list(range(driver.OBSERVABILITY_LIST_PREVIEW_LIMIT))
    assert len(bounded["message"]) == driver.OBSERVABILITY_STRING_LIMIT + 3
    assert len(json.dumps(bounded)) < 2000


def test_frozen_result_payload_is_detached_and_digest_stable() -> None:
    original = {"state": "NO_CANDIDATE", "nested": {"values": [1, 2, 3]}}
    frozen, digest = driver._freeze_result_payload(original)

    original["nested"]["values"].append(4)
    assert frozen == {"state": "NO_CANDIDATE", "nested": {"values": [1, 2, 3]}}
    encoded = json.dumps(frozen, separators=(",", ":"), allow_nan=False).encode("utf-8")
    assert digest == driver.hashlib.sha256(encoded).hexdigest()


def test_verified_process_pool_reaps_real_spawned_workers() -> None:
    verifier = driver.WorkerCleanupVerifier()
    with driver._verified_process_pool(
        2,
        stage="TEST_POOL",
        verifier=verifier,
    ) as executor:
        worker_pids = {executor.submit(os.getpid).result() for _ in range(2)}
        assert worker_pids

    report = verifier.verify()
    assert report["verified"] is True
    assert report["executors_shutdown"] == 1
    assert int(report["worker_processes_reaped"]) >= 1
    assert report["stages"] == ["TEST_POOL"]


def test_verified_process_pool_fails_closed_without_process_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class MissingRegistryExecutor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    verifier = driver.WorkerCleanupVerifier()
    monkeypatch.setattr(driver, "_spawn_process_pool", lambda workers: MissingRegistryExecutor())

    with pytest.raises(RuntimeError, match="could not inspect process registry"):
        with driver._verified_process_pool(2, stage="TEST_POOL", verifier=verifier):
            pass

    with pytest.raises(RuntimeError, match="active executor"):
        verifier.verify()


def test_cli_quiet_suppresses_live_stderr_without_changing_stdout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    captured_kwargs: dict[str, object] = {}

    def fake_run_driver(support, dimensions, **kwargs):
        captured_kwargs.update(kwargs)
        return _minimal_terminal_result(support, dimensions)

    monkeypatch.setattr(driver, "run_driver", fake_run_driver)
    monkeypatch.setattr(
        "sys.argv",
        [
            "weil_continuation_driver",
            "--support",
            "19/40",
            "--n",
            "48",
            "--output-dir",
            str(tmp_path / "quiet-continuation"),
            "--quiet",
        ],
    )

    driver.main()

    captured = capsys.readouterr()
    assert "RESULT: NO_CANDIDATE" in captured.out
    assert captured.err == ""
    assert captured_kwargs["progress"].enabled is False


def _fixed_cli_provenance(*, exclude_output_dir=None) -> dict[str, object]:
    return {
        "git_commit": "c" * 40,
        "git_dirty": False,
        "python_version": "3.14.0",
        "python_implementation": "CPython",
        "python_flint_version": "0.9.0",
    }


def test_cli_unexpected_system_exit_is_recorded_as_failed_run(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "system-exit-failure"
    monkeypatch.setattr(driver, "collect_runtime_provenance", _fixed_cli_provenance)

    def unexpected_exit(*args, **kwargs):
        raise SystemExit(7)

    monkeypatch.setattr(driver, "run_driver", unexpected_exit)
    monkeypatch.setattr(
        "sys.argv",
        [
            "weil_continuation_driver",
            "--support",
            "19/40",
            "--n",
            "48",
            "--output-dir",
            str(output_dir),
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        driver.main()

    assert exc_info.value.code == 7
    assert not (output_dir / "run-manifest.json").exists()
    failure = json.loads((output_dir / ".live" / "failure.json").read_text(encoding="utf-8"))
    assert failure["state"] == "RUN_FAILED"
    assert failure["error_type"] == "SystemExit"


def test_cli_runtime_failure_records_run_failed_without_manifest(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "failed-continuation"
    monkeypatch.setattr(driver, "collect_runtime_provenance", _fixed_cli_provenance)
    monkeypatch.setattr(
        driver,
        "run_driver",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("synthetic runtime failure")),
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "weil_continuation_driver",
            "--support",
            "19/40",
            "--n",
            "48",
            "--output-dir",
            str(output_dir),
        ],
    )

    with pytest.raises(RuntimeError, match="synthetic runtime failure"):
        driver.main()

    assert not (output_dir / "run-manifest.json").exists()
    failure = json.loads((output_dir / ".live" / "failure.json").read_text(encoding="utf-8"))
    status = json.loads((output_dir / ".live" / "run-status.json").read_text(encoding="utf-8"))
    events = [
        json.loads(line)
        for line in (output_dir / ".live" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert failure["state"] == "RUN_FAILED"
    assert failure["error_type"] == "RuntimeError"
    assert status["workflow_state"] == "RUN_FAILED"
    assert status["terminal"] is True
    assert events[-1]["event"] == "RUN_FAILED"
    assert all(event["event"] != "RUN_COMPLETED" for event in events)


def test_cli_interrupt_records_run_interrupted_without_manifest(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "interrupted-continuation"
    monkeypatch.setattr(driver, "collect_runtime_provenance", _fixed_cli_provenance)

    def interrupt(*args, **kwargs):
        raise KeyboardInterrupt()

    monkeypatch.setattr(driver, "run_driver", interrupt)
    monkeypatch.setattr(
        "sys.argv",
        [
            "weil_continuation_driver",
            "--support",
            "19/40",
            "--n",
            "48",
            "--output-dir",
            str(output_dir),
        ],
    )

    with pytest.raises(KeyboardInterrupt):
        driver.main()

    assert not (output_dir / "run-manifest.json").exists()
    failure = json.loads((output_dir / ".live" / "failure.json").read_text(encoding="utf-8"))
    status = json.loads((output_dir / ".live" / "run-status.json").read_text(encoding="utf-8"))
    events = [
        json.loads(line)
        for line in (output_dir / ".live" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert failure["state"] == "RUN_INTERRUPTED"
    assert status["workflow_state"] == "RUN_INTERRUPTED"
    assert status["terminal"] is True
    assert events[-1]["event"] == "RUN_INTERRUPTED"
    assert all(event["event"] != "RUN_COMPLETED" for event in events)


def test_cli_finalization_failure_rolls_back_manifest(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "finalization-failure"
    monkeypatch.setattr(driver, "collect_runtime_provenance", _fixed_cli_provenance)
    monkeypatch.setattr(
        driver,
        "run_driver",
        lambda support, dimensions, **kwargs: _minimal_terminal_result(support, dimensions),
    )

    def fail_after_manifest(result, target, **kwargs):
        (target / "run-manifest.json").write_text('{"invalid":true}\n', encoding="utf-8")
        raise ValueError("synthetic finalization failure")

    monkeypatch.setattr(driver, "write_continuation_bundle", fail_after_manifest)
    monkeypatch.setattr(
        "sys.argv",
        [
            "weil_continuation_driver",
            "--support",
            "19/40",
            "--n",
            "48",
            "--output-dir",
            str(output_dir),
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        driver.main()

    assert exc_info.value.code == 2
    assert not (output_dir / "run-manifest.json").exists()
    failure = json.loads((output_dir / ".live" / "failure.json").read_text(encoding="utf-8"))
    assert failure["state"] == "RUN_FAILED"
    events = [
        json.loads(line)
        for line in (output_dir / ".live" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert events[-1]["event"] == "RUN_FAILED"
    assert all(event["event"] != "RUN_COMPLETED" for event in events)


def test_cli_heartbeat_failure_after_bundle_rolls_back_completion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "heartbeat-failure"
    monkeypatch.setattr(driver, "collect_runtime_provenance", _fixed_cli_provenance)
    monkeypatch.setattr(
        driver,
        "run_driver",
        lambda support, dimensions, **kwargs: _minimal_terminal_result(support, dimensions),
    )

    @contextmanager
    def failing_heartbeats(self, *args, **kwargs):
        yield object()
        raise RuntimeError("synthetic heartbeat supervisor failure")

    monkeypatch.setattr(driver.RunStatusWriter, "periodic_heartbeats", failing_heartbeats)
    monkeypatch.setattr(
        "sys.argv",
        [
            "weil_continuation_driver",
            "--support",
            "19/40",
            "--n",
            "48",
            "--output-dir",
            str(output_dir),
        ],
    )

    with pytest.raises(RuntimeError, match="heartbeat supervisor failure"):
        driver.main()

    assert not (output_dir / "run-manifest.json").exists()
    failure = json.loads((output_dir / ".live" / "failure.json").read_text(encoding="utf-8"))
    status = json.loads((output_dir / ".live" / "run-status.json").read_text(encoding="utf-8"))
    events = [
        json.loads(line)
        for line in (output_dir / ".live" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert failure["state"] == "RUN_FAILED"
    assert status["workflow_state"] == "RUN_FAILED"
    assert status["terminal"] is True
    assert events[-1]["event"] == "RUN_FAILED"
    assert all(event["event"] != "BUNDLE_FINALIZATION_COMPLETED" for event in events)
    assert all(event["event"] != "RUN_COMPLETED" for event in events)


def test_cli_rejects_cache_directory_inside_output_before_locking(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "continuation"

    class ForbiddenLock:
        @classmethod
        def acquire(cls, *args, **kwargs):
            raise AssertionError("output locking must not start for invalid cache placement")

    monkeypatch.setattr(driver, "OutputDirectoryLock", ForbiddenLock)
    monkeypatch.setattr(
        "sys.argv",
        [
            "weil_continuation_driver",
            "--support",
            "19/40",
            "--n",
            "48",
            "--output-dir",
            str(output_dir),
            "--cache-dir",
            str(output_dir / "cache"),
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        driver.main()

    assert exc_info.value.code == 2
    assert not output_dir.exists()


def test_cli_lock_contention_exits_before_expensive_work(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    owner = {
        "run_id": "20260828T030000Z-active01",
        "pid": 4242,
        "started_at_utc": "2026-08-28T03:00:00Z",
    }

    class RefusingLock:
        @classmethod
        def acquire(cls, *args, **kwargs):
            raise driver.OutputDirectoryLockedError(owner)

    def forbidden(*args, **kwargs):
        raise AssertionError("expensive work must not start while output lock is owned")

    monkeypatch.setattr(driver, "OutputDirectoryLock", RefusingLock)
    monkeypatch.setattr(driver, "collect_runtime_provenance", forbidden)
    monkeypatch.setattr(driver, "run_driver", forbidden)
    monkeypatch.setattr(
        "sys.argv",
        [
            "weil_continuation_driver",
            "--support",
            "19/40",
            "--n",
            "48",
            "--output-dir",
            str(tmp_path / "contended"),
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        driver.main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert captured.out == ""
    assert "ERROR: output directory is already owned by another active run" in captured.err
    assert "run_id: 20260828T030000Z-active01" in captured.err
    assert "pid: 4242" in captured.err
    assert "started_at: 2026-08-28T03:00:00Z" in captured.err


def test_p13_cli_json_flag_preserves_full_machine_readable_stdout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = _p13_candidate_ready_result()
    monkeypatch.setattr(driver, "run_driver", lambda *args, **kwargs: result)
    monkeypatch.setattr(driver, "write_continuation_bundle", lambda *args, **kwargs: {})
    monkeypatch.setattr(
        "sys.argv",
        [
            "weil_continuation_driver",
            "--support",
            "19/40",
            "--n",
            "60,64",
            "--output-dir",
            str(tmp_path / "continuation"),
            "--json",
        ],
    )

    driver.main()

    captured = capsys.readouterr()
    stdout = captured.out
    parsed = json.loads(stdout)
    assert parsed == result
    assert parsed["state"] == "CANDIDATE_READY"
    assert "Support continuation candidate search" not in stdout
    assert "] RUN T=19/40 dimensions=60..64 step=4" in captured.err
    assert '"state"' not in captured.err




def test_driver_selects_smallest_ready_dimension_without_contract_admission(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    monkeypatch.setattr(
        driver,
        "scout_support",
        lambda support, *, dimension, prec, residual_order: _rigorous_result(
            positive=dimension != 52
        ),
    )
    monkeypatch.setattr(
        driver,
        "run_candidate",
        lambda support, *, dimension, prec, residual_order, matrix_bits, witness_bits: {
            "all_margins_positive": dimension != 52,
            "dimension": dimension,
        },
    )

    monkeypatch.setattr(
        driver,
        "_confirm_candidate_precision_stability",
        _stable_candidate_confirmation,
    )

    result = driver.run_driver(Fraction(19, 40), [52, 48, 56])

    assert result["state"] == "CANDIDATE_READY"
    assert result["scout_primary_dimension"] == 48
    assert result["selected_dimension"] == 48
    assert result["selected_candidate_dimension"] == 48
    assert result["status"] == "CANDIDATE_READY"
    assert result["theorem_status"] is False
    assert result["independently_verified"] is False
    assert result["whitelisted"] is False
    assert result["residual_order"] == 32
    assert result["dimensions"] == [52, 48, 56]
    assert result["fallback_dimensions"] == [52]
    assert [row["dimension"] for row in result["rigorous_screening"]] == [48, 52]


def test_p10_stable_positive_selection_chooses_smallest_eligible_dimension(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    screened: list[int] = []

    def fake_rigorous(support, dimension, precisions, residual_order, cache_dir=None):
        screened.append(dimension)
        return {
            "status": "precision_stable",
            "selected_precision_bits": 256,
            "attempts": [],
            "precision_pair_diagnostics": [],
        }

    monkeypatch.setattr(driver, "_escalate_rigorous_screen", fake_rigorous)
    monkeypatch.setattr(
        driver,
        "_construct_candidate",
        lambda *args, **kwargs: {
            "status": "candidate_ready",
            "selected_matrix_bits": 80,
            "selected_witness_bits": 40,
            "attempts": [],
        },
    )

    monkeypatch.setattr(
        driver,
        "_confirm_candidate_precision_stability",
        _stable_candidate_confirmation,
    )

    result = driver.run_driver(Fraction(19, 40), [72, 64, 68])

    assert result["scout_primary_dimension"] == 64
    assert result["selected_candidate_dimension"] == 64
    assert screened == [64, 68]


def test_p10_unstable_signs_are_rejected_without_rigorous_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {"scout": 0, "rigorous": 0}

    def fake_scout(*, max_mode, quadrature_order, shift_order, n_values, support):
        calls["scout"] += 1
        return _scout_result(n_values, positive=calls["scout"] != 2)

    monkeypatch.setattr(driver, "scout", fake_scout)
    monkeypatch.setattr(
        driver,
        "_escalate_rigorous_screen",
        lambda *args, **kwargs: calls.__setitem__("rigorous", calls["rigorous"] + 1),
    )

    result = driver.run_driver(Fraction(19, 40), [64])

    assert result["state"] == "SCOUT_UNSTABLE"
    assert calls["rigorous"] == 0


def test_p10_no_rigorous_positive_candidate_returns_no_candidate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    monkeypatch.setattr(
        driver,
        "_escalate_rigorous_screen",
        lambda *args, **kwargs: {
            "status": "mathematical_negative",
            "selected_precision_bits": None,
            "attempts": [],
            "precision_pair_diagnostics": [],
        },
    )

    result = driver.run_driver(Fraction(19, 40), [64])

    assert result["state"] == "NO_CANDIDATE"
    assert result["candidates"] == []


def test_p10_precision_escalation_stops_at_first_stable_precision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []
    widths = (4.0, 2.0, 1.0, 0.5)
    schur = (0.01, 0.0101, 0.0101005, 0.0101006)

    def fake_screen(support, *, dimension, prec, residual_order):
        calls.append(prec)
        index = [128, 256, 384, 512].index(prec)
        return {
            "mu_lower": 0.7,
            "finite_block_min_eigenvalue_midpoint": 0.02,
            "schur_min_eigenvalue_midpoint": schur[index],
            "interval_widths": {
                name: widths[index]
                for name in (
                    "A_max",
                    "GV_max",
                    "G2_max",
                    "GR_max",
                    "mu",
                    "rho_R",
                    "residual_remainder",
                )
            },
        }

    monkeypatch.setattr(driver, "scout_support", fake_screen)
    result = driver._escalate_rigorous_screen(
        Fraction(19, 40), 64, [128, 256, 384, 512], 32
    )

    assert result["status"] == "precision_stable"
    assert result["selected_precision_bits"] == 384
    assert calls == [128, 256, 384]


def test_p10_precision_exhaustion_is_distinct_from_mathematical_rejection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    width_names = (
        "A_max",
        "GV_max",
        "G2_max",
        "GR_max",
        "mu",
        "rho_R",
        "residual_remainder",
    )

    def precision_limited(support, *, dimension, prec, residual_order):
        return {
            "mu_lower": 0.7,
            "finite_block_min_eigenvalue_midpoint": 0.02,
            "schur_min_eigenvalue_midpoint": float(prec),
            "interval_widths": {name: 1.0 / prec for name in width_names},
        }

    monkeypatch.setattr(driver, "scout_support", precision_limited)
    exhausted = driver._escalate_rigorous_screen(
        Fraction(19, 40), 64, [128, 256], 32
    )
    assert exhausted["status"] == "precision_limit_reached"

    def mathematical_negative(support, *, dimension, prec, residual_order):
        return {
            "mu_lower": 0.7,
            "finite_block_min_eigenvalue_midpoint": 0.02,
            "schur_min_eigenvalue_midpoint": -0.010000 if prec == 128 else -0.010005,
            "interval_widths": {
                name: 2.0 if prec == 128 else 1.0 for name in width_names
            },
        }

    monkeypatch.setattr(driver, "scout_support", mathematical_negative)
    rejected = driver._escalate_rigorous_screen(
        Fraction(19, 40), 64, [128, 256], 32
    )
    assert rejected["status"] == "mathematical_negative"


def test_p10_exact_rounding_failure_retries_higher_matrix_bits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[int, int]] = []

    def fake_candidate(
        support, *, dimension, prec, residual_order, matrix_bits, witness_bits
    ):
        calls.append((matrix_bits, witness_bits))
        if matrix_bits == 64:
            raise driver.CandidateStageError("rounding", "outward interval too coarse")
        return {"all_margins_positive": True}

    monkeypatch.setattr(driver, "run_candidate", fake_candidate)
    result = driver._construct_candidate(
        Fraction(19, 40), 64, 384, 32, [64, 80], [32, 40], None
    )

    assert result["status"] == "candidate_ready"
    assert result["selected_matrix_bits"] == 80
    assert result["selected_witness_bits"] == 32
    assert calls == [(64, 32), (64, 40), (80, 32)]
    assert [attempt["status"] for attempt in result["attempts"][:2]] == [
        "rounding_failed",
        "rounding_failed",
    ]


def test_p10_witness_failure_is_pre_theorem_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    monkeypatch.setattr(
        driver,
        "_escalate_rigorous_screen",
        lambda *args, **kwargs: {
            "status": "precision_stable",
            "selected_precision_bits": 256,
            "attempts": [],
            "precision_pair_diagnostics": [],
        },
    )
    monkeypatch.setattr(
        driver,
        "_construct_candidate",
        lambda *args, **kwargs: {
            "status": "witness_failed",
            "selected_matrix_bits": None,
            "selected_witness_bits": None,
            "attempts": [],
        },
    )

    result = driver.run_driver(Fraction(19, 40), [64])

    assert result["state"] == "WITNESS_FAILED"
    assert result["theorem_status"] is False
    assert result["independently_verified"] is False
    assert result["whitelisted"] is False


def test_p10_candidate_ready_never_reports_verified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    monkeypatch.setattr(
        driver,
        "_escalate_rigorous_screen",
        lambda *args, **kwargs: {
            "status": "precision_stable",
            "selected_precision_bits": 256,
            "attempts": [],
            "precision_pair_diagnostics": [],
        },
    )
    monkeypatch.setattr(
        driver,
        "_construct_candidate",
        lambda *args, **kwargs: {
            "status": "candidate_ready",
            "selected_matrix_bits": 80,
            "selected_witness_bits": 40,
            "attempts": [],
        },
    )

    monkeypatch.setattr(
        driver,
        "_confirm_candidate_precision_stability",
        _stable_candidate_confirmation,
    )

    result = driver.run_driver(Fraction(19, 40), [64])

    assert result["state"] == "CANDIDATE_READY"
    assert result["status"] == "CANDIDATE_READY"
    assert result["theorem_status"] is False
    assert result["independently_verified"] is False
    assert result["whitelisted"] is False
    assert result["automatic_promotion"] is False


def test_p10_driver_has_no_theorem_admission_import_or_call_surface() -> None:
    source_path = Path(driver.__file__)
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))

    imported_modules: set[str] = set()
    called_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)
        elif isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called_names.add(node.func.attr)

    assert imported_modules.isdisjoint(
        {
            "scripts.cert.exact_prime_schur_certificate",
            "scripts.cert.export_certificate",
        }
    )
    assert called_names.isdisjoint(
        {
            "build_exact_prime_schur_certificate",
            "validate_certificate_schema",
            "allowed_exact_prime_configuration",
            "verify_exact_prime_schur",
        }
    )
    assert "ALLOWED_CONFIGURATIONS" not in source_path.read_text(encoding="utf-8")


def test_driver_does_not_extrapolate_or_run_candidate_for_negative_scout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=False
        ),
    )
    candidate_calls: list[int] = []
    monkeypatch.setattr(
        driver,
        "run_candidate",
        lambda support, *, dimension, prec, residual_order, matrix_bits, witness_bits: candidate_calls.append(dimension),
    )

    result = driver.run_driver(Fraction(19, 40), [48, 52])

    assert result["state"] == "NO_CANDIDATE"
    assert result["selected_dimension"] is None
    assert candidate_calls == []
