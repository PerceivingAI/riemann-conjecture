from __future__ import annotations

import json
from fractions import Fraction

import pytest
from flint import arb, ctx

from scripts import weil_multi_prime_continuation_driver as driver
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.multi_prime_precision_diagnostics import (
    arb_matrix_exact_width_diagnostics,
    scaled_midpoint_eigenvalue,
)


@pytest.mark.parametrize("exponent", [-1400, 0, 1400])
@pytest.mark.parametrize("largest", [False, True])
def test_scaled_eigenvalue_restores_normalized_units_outside_binary64(exponent, largest):
    with ctx.workprec(128):
        magnitude = arb(2) ** exponent
        matrix = [[2 * magnitude, arb(0)], [arb(0), 3 * magnitude]]
        value, diagnostic = scaled_midpoint_eigenvalue(
            matrix, [Fraction(2), Fraction(2)], largest=largest,
        )
    scale = Fraction(1 << exponent) if exponent >= 0 else Fraction(1, 1 << -exponent)
    expected = scale * (Fraction(3, 2) if largest else 1)
    assert abs(Fraction(value) / expected - 1) <= Fraction(1, 1 << 50)
    assert diagnostic["status"] == "available"
    json.dumps({"value": value, "diagnostic": diagnostic}, allow_nan=False)


@pytest.mark.parametrize("exponent", [-1400, 1400])
def test_arb_diagnostics_retain_exact_widest_entry_and_radius(exponent):
    with ctx.workprec(128):
        radius = arb(2) ** exponent
        matrix = [[arb(0, radius), arb(0)], [arb(0), arb(0, 3 * radius)]]
        result = arb_matrix_exact_width_diagnostics(matrix)
        lo, hi = arb_to_rational_enclosure(matrix[1][1])
    assert Fraction(result["max_width"]) == hi - lo > 0
    assert Fraction(result["max_radius"]) == (hi - lo) / 2
    assert (result["row"], result["column"]) == (1, 1)
    assert Fraction(result["midpoint_at_widest_entry"]) == 0
    json.dumps(result, allow_nan=False)


def test_scaled_eigenvalue_does_not_silently_discard_small_nonzero_entry():
    value, diagnostic = scaled_midpoint_eigenvalue(
        [[arb(2) ** 1400, arb(0)], [arb(0), -(arb(2) ** -1400)]],
        [Fraction(1), Fraction(1)],
    )
    assert value is None
    assert diagnostic["status"] == "unavailable"
    assert diagnostic["reason"] == "normalized_entry_outside_binary64"


def _screen(width: str, *, available=True, schur="1/1"):
    return {
        "mu_lower": "1/1", "mu_midpoint": "2/1", "mu_upper": "3/1",
        "rho_R_upper": "1/1", "residual_remainder_upper": "1/1",
        "finite_block_min_eigenvalue_midpoint": "1/1",
        "schur_min_eigenvalue_midpoint": schur,
        "midpoint_diagnostics_available": available,
        "interval_widths": {name: width for name in (
            "A_max", "GV_max", "GP_max", "GR_max", "mu", "rho_R", "residual_remainder",
        )},
    }


@pytest.mark.parametrize("width", ["1e400", "1e-400"])
@pytest.mark.parametrize("growing", [False, True])
def test_screen_escalation_uses_exact_width_ordering(monkeypatch, width, growing):
    samples = {
        128: _screen(width),
        256: _screen(str(Fraction(width) * (2 if growing else Fraction(1, 2)))),
    }
    monkeypatch.setattr(driver, "scout_support", lambda *args, prec, **kwargs: samples[prec])
    result = driver._escalate_rigorous_screen(Fraction(11, 20), 8, [128, 256], 16)
    assert result["precision_status"] == (
        driver.PRECISION_STATUS_INSUFFICIENT if growing else driver.PRECISION_STATUS_STABLE
    )
    assert result["selected_precision_bits"] == (None if growing else 256)
    assert result["precision_pair_diagnostics"][0]["widths_reduced"] is not growing


@pytest.mark.parametrize("schur", ["1/1", "-1/1"])
def test_unavailable_diagnostic_cannot_qualify_or_reject_screen(monkeypatch, schur):
    samples = {
        128: _screen("1/128", schur=schur),
        256: _screen("1/256", available=False, schur=schur),
        384: _screen("1/384", schur=schur),
    }
    monkeypatch.setattr(driver, "scout_support", lambda *args, prec, **kwargs: samples[prec])
    result = driver._escalate_rigorous_screen(Fraction(11, 20), 8, [128, 256, 384], 16)
    assert result["status"] == "precision_limit_reached"
    assert result["selected_precision_bits"] is None
    assert all(row["precision_status"] == driver.PRECISION_STATUS_INSUFFICIENT
               for row in result["attempts"])
    assert "midpoint_diagnostic_unavailable" in result["attempts"][1]["precision_reasons"]
    assert result["attempts"][2]["stable_change"] is False


@pytest.mark.parametrize("schur", ["1e400", "1e-400", "-1e400", "-1e-400"])
def test_screen_signs_and_stability_do_not_require_binary64_range(monkeypatch, schur):
    samples = {128: _screen("1/128", schur=schur), 256: _screen("1/256", schur=schur)}
    monkeypatch.setattr(driver, "scout_support", lambda *args, prec, **kwargs: samples[prec])
    result = driver._escalate_rigorous_screen(Fraction(11, 20), 8, [128, 256], 16)
    assert result["status"] == (
        "mathematical_negative" if Fraction(schur) < 0 else "precision_stable"
    )
