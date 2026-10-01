from __future__ import annotations

from fractions import Fraction

import pytest
from flint import arb, ctx

from scripts.cert.legendre_schur import first_prime_matrices, legendre_polynomials
from scripts.cert.prime_power_terms import (
    ThresholdIndeterminateError,
    assemble_active_prime_power_operator,
    assemble_combined_prime_power_operator,
    enumerate_active_prime_power_terms,
    factor_prime_power,
    is_prime_power,
    prime_power_term,
)


def test_prime_power_factorization_is_exact_and_independent() -> None:
    expected = {
        2: (2, 1),
        3: (3, 1),
        4: (2, 2),
        8: (2, 3),
        9: (3, 2),
        16: (2, 4),
        25: (5, 2),
        27: (3, 3),
        49: (7, 2),
    }
    for m, (prime, exponent) in expected.items():
        factorization = factor_prime_power(m)
        assert factorization is not None
        assert factorization.prime == prime
        assert factorization.exponent == exponent
        assert is_prime_power(m)

    for m in (0, 1, 6, 10, 12, 18, 36):
        assert factor_prime_power(m) is None
        assert not is_prime_power(m)


def test_prime_power_constants_use_von_mangoldt_base_prime() -> None:
    with ctx.workprec(160):
        term = prime_power_term(4, 7, 10, prec=160)
        assert term.prime == 2
        assert term.exponent == 2
        assert term.log_m.overlaps(arb(4).log())
        assert term.von_mangoldt.overlaps(arb(2).log())
        assert term.coefficient.overlaps(arb(2).log() / 2)
        assert term.tau.overlaps(arb(4).log() / (arb(7) / 10))


def test_immediate_window_enumerates_exactly_two_active_terms() -> None:
    terms = enumerate_active_prime_power_terms(3, 5, prec=128)
    assert [term.m for term in terms] == [2, 3]
    assert all(term.tau > 1 and term.tau < 2 for term in terms)


def test_support_threshold_fails_closed_when_precision_cannot_decide() -> None:
    # Decimal truncation of log(3)/2.  The rational lies below the threshold by
    # far less than 64-bit Arb can resolve, but 256-bit Arb separates it.
    num = 549306144334054845697622618
    den = 10**27
    with pytest.raises(ThresholdIndeterminateError, match="increase Arb precision"):
        enumerate_active_prime_power_terms(num, den, prec=64)

    terms = enumerate_active_prime_power_terms(num, den, prec=256)
    assert [term.m for term in terms] == [2]


def test_piecewise_core_matches_frozen_one_prime_matrices() -> None:
    polys = legendre_polynomials(4)
    generic = assemble_active_prime_power_operator(polys, 2, 5, prec=160)
    legacy_p, legacy_p2 = first_prime_matrices(polys, 160, 2, 5)

    assert [term.m for term in generic.terms] == [2]
    for i in range(len(polys)):
        for j in range(len(polys)):
            assert generic.p_matrix[i][j].overlaps(legacy_p[i][j])
            assert generic.p_squared_matrix[i][j].overlaps(legacy_p2[i][j])


def test_combined_square_contains_nonzero_two_prime_cross_terms() -> None:
    polys = legendre_polynomials(2)
    terms = enumerate_active_prime_power_terms(3, 5, prec=192)
    assert [term.m for term in terms] == [2, 3]

    combined = assemble_combined_prime_power_operator(polys, terms, prec=192)
    only_two = assemble_combined_prime_power_operator(polys, [terms[0]], prec=192)
    only_three = assemble_combined_prime_power_operator(polys, [terms[1]], prec=192)

    for i in range(len(polys)):
        for j in range(len(polys)):
            sum_low = only_two.p_matrix[i][j] + only_three.p_matrix[i][j]
            assert combined.p_matrix[i][j].overlaps(sum_low)

    cross_00 = (
        combined.p_squared_matrix[0][0]
        - only_two.p_squared_matrix[0][0]
        - only_three.p_squared_matrix[0][0]
    )
    assert cross_00.lower() > 0


def test_piecewise_core_survives_tau2_below_one_and_m4_entry() -> None:
    polys = legendre_polynomials(3)
    assembly = assemble_active_prime_power_operator(polys, 7, 10, prec=192)

    assert [term.m for term in assembly.terms] == [2, 3, 4]
    term_two = assembly.terms[0]
    assert term_two.tau < 1
    assert len(assembly.breakpoints) == 2 + 2 * len(assembly.terms)
    assert all(
        assembly.breakpoints[index] < assembly.breakpoints[index + 1]
        for index in range(len(assembly.breakpoints) - 1)
    )

    for matrix in (
        assembly.p_matrix,
        assembly.p_squared_matrix,
        assembly.g_p,
    ):
        for i in range(len(polys)):
            for j in range(len(polys)):
                assert matrix[i][j].overlaps(matrix[j][i])


def test_combined_operator_rejects_terms_from_different_supports() -> None:
    polys = legendre_polynomials(1)
    term_two = prime_power_term(2, 3, 5, prec=96)
    term_three = prime_power_term(3, 5, 8, prec=96)
    with pytest.raises(ValueError, match="share one exact rational support"):
        assemble_combined_prime_power_operator(
            polys,
            [term_two, term_three],
            prec=96,
        )


def test_combined_operator_requires_exact_orthogonal_basis() -> None:
    term = prime_power_term(2, 2, 5, prec=96)
    with pytest.raises(ValueError, match="orthogonal basis"):
        assemble_combined_prime_power_operator(
            [[Fraction(1)], [Fraction(1), Fraction(1)]],
            [term],
            prec=96,
        )
