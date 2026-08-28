import argparse
import copy
import json
import ast
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
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def submit(self, fn, *args, **kwargs):
        return _InlineFuture(fn, args, kwargs)


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

    def fake_run_driver(support, dimensions, **kwargs):
        captured_kwargs.update(kwargs)
        return {
            "state": "NO_CANDIDATE",
            "support": str(support),
            "dimensions": dimensions,
        }

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
    live_status = json.loads(
        (output_dir / ".live" / "run-status.json").read_text(encoding="utf-8")
    )
    live_events = [
        json.loads(line)
        for line in (output_dir / ".live" / "events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert '"state": "NO_CANDIDATE"' in summary
    assert '"final_state": "NO_CANDIDATE"' in manifest
    assert live_status["format"] == "riemann-live-run-v1"
    assert live_status["support"] == "19/40"
    assert live_status["workflow_state"] == "NO_CANDIDATE"
    assert live_status["current_operation"] is None
    assert live_status["terminal"] is True
    assert [event["seq"] for event in live_events] == list(
        range(1, len(live_events) + 1)
    )
    assert [event["event"] for event in live_events] == [
        "RUN_STARTED",
        "BUNDLE_FINALIZATION_STARTED",
        "BUNDLE_FINALIZATION_COMPLETED",
        "RUN_COMPLETED",
    ]
    assert all(event["run_id"] == live_status["run_id"] for event in live_events)
    assert live_events[-1]["final_state"] == "NO_CANDIDATE"
    terminal = capsys.readouterr().out
    assert "Support continuation candidate search" in terminal
    assert "RESULT: NO_CANDIDATE" in terminal
    assert '"state"' not in terminal
    available_cpus = driver.os.cpu_count() or 1
    assert captured_kwargs["scout_workers"] == min(
        driver.CLI_SCOUT_WORKERS_MAX, available_cpus
    )
    assert captured_kwargs["rigorous_workers"] == min(
        driver.CLI_RIGOROUS_WORKERS_MAX, available_cpus
    )


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

    stdout = capsys.readouterr().out
    parsed = json.loads(stdout)
    assert parsed == result
    assert parsed["state"] == "CANDIDATE_READY"
    assert "Support continuation candidate search" not in stdout




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
