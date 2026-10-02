"""Exact operator references independent of the local Legendre recurrence."""
from dataclasses import replace
from fractions import Fraction
import math

import pytest
from flint import arb, ctx

from scripts.cert.legendre_schur import exact_poly_inner, legendre_polynomials
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.prime_power_terms import (
    assemble_active_prime_power_operator, assemble_combined_prime_power_operator,
    combined_piecewise_images, prime_power_term,
    PiecewiseTopologyError,
)


def _shift(poly, shift):
    return [sum((c * math.comb(k, j) * shift ** (k - j)
                 for k, c in enumerate(poly) if k >= j), Fraction(0))
            for j in range(len(poly))]


def _integral_product(left, right, lo, hi):
    return sum((a * b * (hi ** (i + j + 1) - lo ** (i + j + 1)) / (i + j + 1)
                for i, a in enumerate(left) for j, b in enumerate(right)), Fraction(0))


def _eval(poly, x):
    return sum((c * x ** k for k, c in enumerate(poly)), Fraction(0))


def _exact_operator(polys, shifts, coefficients):
    points = sorted({Fraction(-1), Fraction(1),
                     *(1 - tau for tau in shifts), *(tau - 1 for tau in shifts)})
    p = [[Fraction(0) for _ in polys] for _ in polys]
    square = [[Fraction(0) for _ in polys] for _ in polys]
    cells = []
    for lo, hi in zip(points[:-1], points[1:], strict=True):
        midpoint = (lo + hi) / 2
        images = [[Fraction(0) for _ in poly] for poly in polys]
        for tau, coefficient in zip(shifts, coefficients, strict=True):
            for shift, active in ((tau, midpoint < 1 - tau), (-tau, midpoint > tau - 1)):
                if active:
                    for image, poly in zip(images, polys, strict=True):
                        for k, value in enumerate(_shift(poly, shift)):
                            image[k] -= coefficient * value
        cells.append((lo, hi, images))
        for i in range(len(polys)):
            for j in range(len(polys)):
                p[i][j] += _integral_product(polys[i], images[j], lo, hi)
                square[i][j] += _integral_product(images[i], images[j], lo, hi)
    norms = [exact_poly_inner(poly, poly) for poly in polys]
    gp = [[square[i][j] - sum((p[i][k] * p[k][j] / norms[k] for k in range(len(polys))), Fraction(0))
           for j in range(len(polys))] for i in range(len(polys))]
    return p, square, gp, cells


@pytest.mark.parametrize("shifts", [
    (Fraction(3, 2), Fraction(7, 4)),
    (Fraction(3, 4), Fraction(9, 8), Fraction(3, 2)),
])
@pytest.mark.parametrize("mixed", [False, True])
def test_local_images_and_all_gram_entries_enclose_exact_rational_action(shifts, mixed):
    canonical = legendre_polynomials(5)
    polys = [canonical[5], canonical[0], canonical[4], canonical[1]]
    if mixed:
        polys = [[Fraction(1), Fraction(1)], [Fraction(1), Fraction(-3)], canonical[4], canonical[5]]
    scales = (Fraction(-3, 2), Fraction(5, 3), Fraction(2), Fraction(-1))
    polys = [[scale * c for c in poly] for scale, poly in zip(scales, polys, strict=True)]
    coefficients = tuple(Fraction(k + 2, k + 3) for k in range(len(shifts)))
    with ctx.workprec(160):
        terms = [replace(prime_power_term(m, 7, 10, 160),
                         tau=arb(tau.numerator) / tau.denominator,
                         coefficient=arb(c.numerator) / c.denominator)
                 for m, tau, c in zip((2, 3, 4), shifts, coefficients)]
        result = assemble_combined_prime_power_operator(polys, terms, 160)
        p, square, gp, cells = _exact_operator(polys, shifts, coefficients)
        for actual, expected in zip((result.p_matrix, result.p_squared_matrix, result.g_p),
                                    (p, square, gp), strict=True):
            for i, row in enumerate(actual):
                for j, value in enumerate(row):
                    lo, hi = arb_to_rational_enclosure(value)
                    assert lo <= expected[i][j] <= hi
                    assert hi - lo < Fraction(1, 2**120)
        _, images = combined_piecewise_images(polys, terms, 160)
        local_legendre = legendre_polynomials(5)
        for i, image in enumerate(images):
            for piece, (lo, hi, reference) in zip(image, cells, strict=True):
                t = Fraction(1, 3)
                x = (lo + hi) / 2 + (hi - lo) * t / 2
                value = sum((c * arb(_eval(local_legendre[k], t).numerator)
                             / _eval(local_legendre[k], t).denominator
                             for k, c in enumerate(piece.legendre_coefficients)), arb(0))
                lower, upper = arb_to_rational_enclosure(value)
                assert lower <= _eval(reference[i], x) <= upper


def test_sparse_high_degree_mixed_basis_contracts_and_contains_tighter_enclosures():
    legendre = legendre_polynomials(63)
    left = [a + b for a, b in zip(legendre[62] + [Fraction(0)], legendre[63], strict=True)]
    right = [a - Fraction(127, 125) * b
             for a, b in zip(legendre[62] + [Fraction(0)], legendre[63], strict=True)]
    assert exact_poly_inner(left, right) == 0
    results = [assemble_active_prime_power_operator([left, right], 11, 20, prec)
               for prec in (128, 256, 512)]
    for name in ("p_matrix", "p_squared_matrix", "g_p"):
        for i in range(2):
            for j in range(2):
                bounds = [arb_to_rational_enclosure(getattr(result, name)[i][j]) for result in results]
                for (lo, hi), (tight_lo, tight_hi) in zip(bounds[:-1], bounds[1:], strict=True):
                    assert lo <= tight_lo <= tight_hi <= hi
                    assert tight_hi - tight_lo < hi - lo
                assert bounds[1][1] - bounds[1][0] < Fraction(1, 2**40)


def test_narrow_real_prime_three_cells_remain_strict_and_contract():
    num, den = 549306144334054845697622619, 10**27
    polys = legendre_polynomials(4)
    low = assemble_active_prime_power_operator(polys, num, den, 192)
    high = assemble_active_prime_power_operator(polys, num, den, 384)
    assert [term.m for term in low.terms] == [2, 3]
    for lo, hi in zip(low.breakpoints[:-1], low.breakpoints[1:], strict=True):
        assert lo < hi
    for name in ("p_matrix", "p_squared_matrix", "g_p"):
        for i in range(len(polys)):
            for j in range(len(polys)):
                lo, hi = arb_to_rational_enclosure(getattr(low, name)[i][j])
                tight_lo, tight_hi = arb_to_rational_enclosure(getattr(high, name)[i][j])
                assert lo <= tight_lo <= tight_hi <= hi
                if hi > lo:
                    assert tight_hi - tight_lo < hi - lo


def test_coincident_translation_breakpoints_fail_closed():
    with ctx.workprec(160):
        terms = [replace(prime_power_term(m, 7, 10, 160), tau=arb(tau.numerator) / tau.denominator)
                 for m, tau in zip((2, 3), (Fraction(3, 4), Fraction(5, 4)), strict=True)]
        with pytest.raises(PiecewiseTopologyError, match="order"):
            assemble_combined_prime_power_operator(legendre_polynomials(2), terms, 160)
