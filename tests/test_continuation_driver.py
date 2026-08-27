from fractions import Fraction

import pytest

from scripts import weil_continuation_driver as driver


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

    result = driver.run_driver(Fraction(19, 40), [52, 48, 56])

    assert result["state"] == "CANDIDATE_READY"
    assert result["selected_dimension"] == 48
    assert result["theorem_status"] == "not_a_theorem"
    assert result["dimensions"] == [52, 48, 56]
    assert result["fallback_dimensions"] == [52]
    assert [row["dimension"] for row in result["rigorous_screening"]] == [48, 52]


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
