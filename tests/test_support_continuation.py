from __future__ import annotations

from fractions import Fraction

import pytest

from scripts.cert.legendre_schur import assemble_exact_prime_schur
from scripts import weil_support_continuation_scout as continuation_scout
from scripts.weil_support_continuation_scout import parse_supports


def test_support_parser_preserves_exact_rationals() -> None:
    assert parse_supports("7/20, 2/5, 1/2") == [
        Fraction(7, 20),
        Fraction(2, 5),
        Fraction(1, 2),
    ]


def test_build_scan_reports_actual_largest_positive_support(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_scout(support, *, dimension, prec, residual_order):
        return {
            "support": f"{support.numerator}/{support.denominator}",
            "schur_min_eigenvalue_midpoint": 1.0,
        }

    monkeypatch.setattr(continuation_scout, "scout_support", fake_scout)
    result = continuation_scout.build_scan(
        [Fraction(1, 2), Fraction(2, 5), Fraction(19, 40)],
        dimension=32,
        prec=128,
        residual_order=32,
    )
    assert result["largest_scanned_positive_midpoint_support"] == "1/2"


def test_parameterized_assembler_keeps_verified_basepoint() -> None:
    result = assemble_exact_prime_schur(
        n=32,
        prec=96,
        residual_order=16,
        support_num=7,
        support_den=20,
    )
    assert result["support_num"] == 7
    assert result["support_den"] == 20
    assert result["mu"].lower() > 0


def test_assembler_rejects_support_outside_true_one_prime_window() -> None:
    for support in (Fraction(1, 3), Fraction(3, 5)):
        with pytest.raises(ValueError, match="one-prime window"):
            assemble_exact_prime_schur(
                n=1,
                prec=64,
                residual_order=8,
                support_num=support.numerator,
                support_den=support.denominator,
                require_positive_mu=False,
            )


def test_parameterized_assembler_accepts_another_one_prime_support() -> None:
    result = assemble_exact_prime_schur(
        n=32,
        prec=96,
        residual_order=16,
        support_num=2,
        support_den=5,
        require_positive_mu=False,
    )
    assert result["support_num"] == 2
    assert result["support_den"] == 5
    assert result["mu"] is not None
