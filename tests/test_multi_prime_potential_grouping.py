"""Numerical regressions for exact harmonic potential contractions."""

from fractions import Fraction

import pytest

from scripts.cert import legendre_schur as frozen
from scripts.cert.multi_prime_legendre_schur import _potential_matrices
from scripts.cert.constants import arb_to_rational_enclosure


def _small_basis(kind):
    legendre = frozen.legendre_polynomials(5)
    if kind == "legendre":
        return legendre
    if kind == "scaled_reordered":
        order = (4, 1, 0, 5, 2, 3)
        scales = (Fraction(2), Fraction(-3, 5), Fraction(7, 3),
                  Fraction(-1), Fraction(5, 2), Fraction(4))
        return [[scale * c for c in legendre[k]]
                for k, scale in zip(order, scales, strict=True)]
    if kind == "orthogonal_mixed_parity":
        return [[Fraction(1), Fraction(1)], [Fraction(1), Fraction(-3)],
                legendre[2], legendre[3]]
    if kind == "nonorthogonal_mixed_parity":
        return [[Fraction(2), Fraction(1), Fraction(3)],
                [Fraction(1), Fraction(0), Fraction(2)],
                [Fraction(0), Fraction(2, 3), Fraction(0), Fraction(1)]]
    raise AssertionError(kind)


def _assert_encloses_reference(value, reference):
    lower, upper = arb_to_rational_enclosure(value)
    ref_lower, ref_upper = arb_to_rational_enclosure(reference)
    if lower == upper:
        # The ungrouped moment sum can round an exact cancellation to a ball.
        assert ref_lower <= lower <= ref_upper
    else:
        assert lower <= ref_lower <= ref_upper <= upper
    return upper - lower


@pytest.mark.parametrize("kind", [
    "legendre", "scaled_reordered", "orthogonal_mixed_parity",
    "nonorthogonal_mixed_parity",
])
def test_full_potential_matrices_enclose_tighter_v1_moment_sums(kind):
    polys = _small_basis(kind)
    if kind == "orthogonal_mixed_parity":
        assert all(frozen.exact_poly_inner(left, right) == 0
                   for i, left in enumerate(polys) for right in polys[i + 1:])
    actual = _potential_matrices(polys, 128)
    reference = frozen.potential_matrices(polys, 512)
    for matrix, ref_matrix in zip(actual, reference, strict=True):
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                width = _assert_encloses_reference(value, ref_matrix[i][j])
                assert width < Fraction(1, 2**100)
                assert arb_to_rational_enclosure(value) == arb_to_rational_enclosure(matrix[j][i])
        if kind == "orthogonal_mixed_parity":
            assert not matrix[0][1].contains(0)


def test_high_degree_grouping_retains_tight_enclosures_and_precision_contraction():
    legendre = frozen.legendre_polynomials(191)
    polys = [legendre[k] for k in (0, 1, 190, 191)]
    low = _potential_matrices(polys, 160)
    high = _potential_matrices(polys, 240)
    reference = frozen.potential_matrices(polys, 1024)
    for low_matrix, high_matrix, ref_matrix in zip(low, high, reference, strict=True):
        for i, row in enumerate(low_matrix):
            for j, value in enumerate(row):
                low_width = _assert_encloses_reference(value, ref_matrix[i][j])
                high_width = _assert_encloses_reference(high_matrix[i][j], ref_matrix[i][j])
                assert low_width < Fraction(1, 2**140)
                assert high_width < Fraction(1, 2**220)
                low_lower, low_upper = arb_to_rational_enclosure(value)
                high_lower, high_upper = arb_to_rational_enclosure(high_matrix[i][j])
                assert low_lower <= high_lower <= high_upper <= low_upper
                if low_width:
                    assert high_width < low_width / 2**60
                else:
                    assert high_width == 0
                if i % 2 != j % 2:
                    assert low_width == high_width == 0
                    assert value.is_zero()

    # These off-diagonal integrals are rational after exact harmonic grouping.
    # At degree 190/191 the old monomial interval sum loses hundreds of bits.
    for i, j, exact in ((0, 2, Fraction(2, 190 * 191)),
                        (1, 3, Fraction(2, 190 * 193))):
        lower, upper = arb_to_rational_enclosure(low[0][i][j])
        assert lower <= exact <= upper
        assert lower > 0
