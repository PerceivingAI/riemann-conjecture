from __future__ import annotations

from fractions import Fraction

from scripts.cert.legendre_schur import assemble_exact_prime_schur
from scripts.weil_support_continuation_scout import parse_supports


def test_support_parser_preserves_exact_rationals() -> None:
    assert parse_supports("7/20, 2/5, 1/2") == [
        Fraction(7, 20),
        Fraction(2, 5),
        Fraction(1, 2),
    ]


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
