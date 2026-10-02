"""Small independent references for native arithmetic optimizations.

No wall-clock assertions. The reference integrates the unskipped full image
products, so a wrong parity shortcut or dropped mixed term is observable.
"""

from __future__ import annotations

import math
from fractions import Fraction
from unittest.mock import patch

import pytest
from flint import arb, ctx

from scripts.cert import legendre_schur as frozen
from scripts.cert import multi_prime_legendre_schur as assembly
from scripts.cert import prime_power_terms as arithmetic
from scripts.cert.constants import arb_to_rational_enclosure


def _reference_images(polys, terms):
    # The pre-optimization action, without the shared activity table or shifts.
    breakpoints = arithmetic._sorted_breakpoints(terms) if terms else (arb(-1), arb(1))
    images = []
    for poly in polys:
        pieces = []
        for lower, upper in zip(breakpoints[:-1], breakpoints[1:], strict=True):
            coefficients = [arb(0) for _ in poly]
            midpoint = (lower + upper) / 2
            for term in terms:
                for before, boundary, shift in (
                    (True, 1 - term.tau, term.tau),
                    (False, -1 + term.tau, -term.tau),
                ):
                    if arithmetic._activity(midpoint, boundary, before=before, term=term):
                        shifted = _reference_shift(poly, shift)
                        for k, value in enumerate(shifted):
                            coefficients[k] -= term.coefficient * value
            pieces.append(arithmetic.PiecewisePolynomial(lower, upper, tuple(coefficients)))
        images.append(tuple(pieces))
    return breakpoints, tuple(images)


def _reference_shift(poly, shift):
    out = [arb(0) for _ in poly]
    for degree, coefficient in enumerate(poly):
        c = arb(coefficient.numerator) / coefficient.denominator
        for power in range(degree + 1):
            out[power] += c * math.comb(degree, power) * shift ** (degree - power)
    return out


def _reference_inner(a, b, lower, upper):
    product = [arb(0) for _ in range(len(a) + len(b) - 1)]
    for i, left in enumerate(a):
        for j, right in enumerate(b):
            product[i + j] += left * right
    return sum((c * (upper ** (k + 1) - lower ** (k + 1)) / (k + 1)
                for k, c in enumerate(product)), arb(0))


def _reference_operator(polys, terms, prec=128):
    with ctx.workprec(prec):
        breakpoints, images = _reference_images(polys, terms)
        basis = [[arb(c.numerator) / c.denominator for c in poly] for poly in polys]
        norms = tuple(frozen.exact_poly_inner(poly, poly) for poly in polys)
        n = len(polys)
        p = [[arb(0) for _ in polys] for _ in polys]
        square = [[arb(0) for _ in polys] for _ in polys]
        for i in range(n):
            for j in range(n):
                p[i][j] = sum((_reference_inner(basis[i], piece.coefficients, piece.lower, piece.upper)
                               for piece in images[j]), arb(0))
                square[i][j] = sum(
                    (_reference_inner(left.coefficients, right.coefficients, left.lower, left.upper)
                     for left, right in zip(images[i], images[j], strict=True)), arb(0),
                )
        gp = [[square[i][j] - sum((p[i][k] * p[k][j] / (arb(norms[k].numerator) / norms[k].denominator)
                                  for k in range(n)), arb(0)) for j in range(n)] for i in range(n)]
        return arithmetic.PrimePowerOperatorAssembly(tuple(terms), breakpoints, images, norms, p, square, gp)


def _assert_matrix_overlap(left, right):
    for i in range(len(left)):
        for j in range(len(left)):
            assert left[i][j].overlaps(right[i][j]), (i, j, left[i][j], right[i][j])


@pytest.mark.parametrize("support", [
    Fraction(1, 4), Fraction(2, 5), Fraction(11, 20), Fraction(3, 5), Fraction(7, 10),
])
@pytest.mark.parametrize("prec", [128, 256])
def test_complete_assembly_matches_unoptimized_arithmetic_and_frozen_components(support, prec):
    new, old = _assemblies(support, prec)
    assert new["norms"] == old["norms"] == [Fraction(2, 2 * k + 1) for k in range(6)]
    assert new["arithmetic_norm_bounds"].keys() == old["arithmetic_norm_bounds"].keys()
    for m, bound in new["arithmetic_norm_bounds"].items():
        assert bound.overlaps(old["arithmetic_norm_bounds"][m])
    assert [(t.m, t.prime, t.exponent, t.support) for t in new["active_terms"]] == [
        (t.m, t.prime, t.exponent, t.support) for t in old["active_terms"]
    ]
    for name in ("P", "P_squared", "GP", "A", "GV", "GR"):
        _assert_matrix_overlap(new[name], old[name])
        _assert_symmetry_and_parity(new[name])
    for name in ("rho_R", "mu", "delta_R"):
        assert new[name].overlaps(old[name])
    assert (new["schur"] is None) == (old["schur"] is None)
    if new["schur"] is not None:
        _assert_matrix_overlap(new["schur"], old["schur"])
        _assert_symmetry_and_parity(new["schur"])


def _assemblies(support, prec):
    parameters = dict(n=6, prec=prec, residual_order=8, support_num=support.numerator,
                      support_den=support.denominator, require_positive_mu=False)
    new = assembly.assemble_multi_prime_schur(**parameters)
    with patch.object(arithmetic, "assemble_combined_prime_power_operator", _reference_operator), \
            patch.object(assembly, "_potential_matrices", frozen.potential_matrices), \
            patch.object(assembly, "_residual_truncation_operator", frozen.residual_truncation_operator), \
            patch.object(assembly, "_mat_mul_diag_inverse", frozen._arb_mat_mul_diag_inverse):
        old = assembly.assemble_multi_prime_schur(**parameters)
    return new, old


def test_operator_parity_follows_coefficients_not_basis_indices():
    polys = frozen.legendre_polynomials(3)
    polys = [polys[1], polys[0], polys[3], polys[2]]
    polys = [[c * scale for c in poly] for poly, scale in zip(
        polys, (Fraction(3, 2), Fraction(-2), Fraction(7, 3), Fraction(-5)), strict=True,
    )]
    terms = arithmetic.enumerate_active_prime_power_terms(11, 20, prec=160)
    result = arithmetic.assemble_combined_prime_power_operator(polys, terms, prec=160)
    reference = _reference_operator(polys, terms, prec=160)
    assert result.norms == reference.norms == (Fraction(3, 2), Fraction(8), Fraction(14, 9), Fraction(10))
    for new, old in zip((result.p_matrix, result.p_squared_matrix, result.g_p),
                        (reference.p_matrix, reference.p_squared_matrix, reference.g_p), strict=True):
        _assert_matrix_overlap(new, old)
        for i, pi in enumerate((1, 0, 1, 0)):
            for j, pj in enumerate((1, 0, 1, 0)):
                if pi != pj:
                    assert new[i][j].is_zero()


def test_orthogonal_mixed_parity_basis_does_not_skip_cross_entry():
    polys = [[Fraction(1), Fraction(1)], [Fraction(1), Fraction(-3)]]
    terms = arithmetic.enumerate_active_prime_power_terms(11, 20, prec=160)
    result = arithmetic.assemble_combined_prime_power_operator(polys, terms, prec=160)
    reference = _reference_operator(polys, terms, prec=160)
    assert result.norms == reference.norms == (Fraction(8, 3), Fraction(8))
    _assert_matrix_overlap(result.p_matrix, reference.p_matrix)
    _assert_matrix_overlap(result.p_squared_matrix, reference.p_squared_matrix)
    _assert_matrix_overlap(result.g_p, reference.g_p)
    assert not result.p_matrix[0][1].contains(0)
    for implementation, reference_component in (
        (assembly._potential_matrices(polys, 160), frozen.potential_matrices(polys, 160)),
        (assembly._residual_truncation_operator(polys, 8, 160, 11, 20)[1:3],
         frozen.residual_truncation_operator(polys, 8, 160, 11, 20)[1:3]),
    ):
        for new, old in zip(implementation, reference_component, strict=True):
            _assert_matrix_overlap(new, old)
            assert not new[0][1].contains(0)


def test_zero_polynomial_is_not_an_orthogonal_basis_vector():
    with pytest.raises(ValueError, match="nonpositive exact norm"):
        arithmetic.assemble_combined_prime_power_operator([[Fraction(0)]], [], prec=128)


@pytest.mark.parametrize("support", [Fraction(11, 20), Fraction(7, 10)])
def test_residual_polynomial_images_are_exactly_unchanged(support):
    polys = frozen.legendre_polynomials(5)
    images, low, square, delta = assembly._residual_truncation_operator(
        polys, 32, 160, support.numerator, support.denominator,
    )
    old_images, old_low, old_square, old_delta = frozen.residual_truncation_operator(
        polys, 32, 160, support.numerator, support.denominator,
    )
    for new, old in zip(images, old_images, strict=True):
        assert [Fraction(int(c.p), int(c.q)) for c in new.coeffs()] == old
    _assert_matrix_overlap(low, old_low)
    _assert_matrix_overlap(square, old_square)
    assert delta.overlaps(old_delta)


def _assert_symmetry_and_parity(matrix):
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            assert arb_to_rational_enclosure(value) == arb_to_rational_enclosure(matrix[j][i])
            if i % 2 != j % 2:
                assert value.is_zero()


def _assert_tight_reference_enclosed(low, high, reference):
    lo, hi = arb_to_rational_enclosure(low)
    high_lo, high_hi = arb_to_rational_enclosure(high)
    ref_lo, ref_hi = arb_to_rational_enclosure(reference)
    if lo == hi:
        # The unskipped reference can have roundoff width at an exact zero.
        assert high_lo == high_hi == lo
        assert ref_lo <= lo <= ref_hi
        return
    assert lo <= high_lo <= high_hi <= hi
    assert lo <= ref_lo <= ref_hi <= hi
    assert high.overlaps(reference)
    assert high_hi - high_lo <= hi - lo
    if hi != lo:
        assert high_hi - high_lo < hi - lo


@pytest.mark.parametrize("support", [
    Fraction(1, 4), Fraction(2, 5), Fraction(11, 20), Fraction(3, 5), Fraction(7, 10),
])
def test_high_precision_reference_is_contained_in_lower_precision_assembly(support):
    low, low_reference = _assemblies(support, 128)
    high, high_reference = _assemblies(support, 384)
    for name in ("P", "P_squared", "GP", "A", "GV", "GR", "schur"):
        if low[name] is None:
            assert high[name] is high_reference[name] is None
            continue
        for i in range(6):
            for j in range(6):
                _assert_tight_reference_enclosed(low[name][i][j], high[name][i][j],
                                                high_reference[name][i][j])
                _assert_tight_reference_enclosed(low_reference[name][i][j],
                                                high_reference[name][i][j], high[name][i][j])
    for name in ("rho_R", "mu", "delta_R"):
        _assert_tight_reference_enclosed(low[name], high[name], high_reference[name])
    for m, bound in low["arithmetic_norm_bounds"].items():
        _assert_tight_reference_enclosed(bound, high["arithmetic_norm_bounds"][m],
                                        high_reference["arithmetic_norm_bounds"][m])


@pytest.mark.parametrize("support", [Fraction(11, 20), Fraction(7, 10)])
@pytest.mark.parametrize("dimension", [3, 6])
def test_arithmetic_work_bounds_preserve_unskipped_reference(support, dimension):
    polys = frozen.legendre_polynomials(dimension - 1)
    terms = arithmetic.enumerate_active_prime_power_terms(
        support.numerator, support.denominator, prec=160,
    )
    with patch.object(arithmetic, "_arb_poly_shift", wraps=arithmetic._arb_poly_shift) as shifts, \
            patch.object(arithmetic, "_sorted_breakpoints", wraps=arithmetic._sorted_breakpoints) as partition, \
            patch.object(arithmetic, "_activity", wraps=arithmetic._activity) as activity, \
            patch.object(arithmetic, "_integrated_product", wraps=arithmetic._integrated_product) as integrals:
        result = arithmetic.assemble_combined_prime_power_operator(polys, terms, prec=160)
    cells = len(result.breakpoints) - 1
    assert partition.call_count == 1
    assert shifts.call_count <= 2 * dimension * len(terms)
    assert activity.call_count <= 2 * len(terms) * cells
    even, odd = (dimension + 1) // 2, dimension // 2
    same_parity_pairs = even * (even + 1) // 2 + odd * (odd + 1) // 2
    assert integrals.call_count <= 2 * cells * same_parity_pairs
    reference = _reference_operator(polys, terms, prec=160)
    assert result.norms == reference.norms
    for new, old in zip((result.p_matrix, result.p_squared_matrix, result.g_p),
                        (reference.p_matrix, reference.p_squared_matrix, reference.g_p), strict=True):
        _assert_matrix_overlap(new, old)
        _assert_symmetry_and_parity(new)
    for new_image, old_image in zip(result.images, reference.images, strict=True):
        for new_piece, old_piece in zip(new_image, old_image, strict=True):
            assert all(a.overlaps(b) for a, b in zip(
                new_piece.coefficients, old_piece.coefficients, strict=True,
            ))


def test_potential_moments_are_computed_once_per_degree_without_changing_matrices():
    polys = frozen.legendre_polynomials(5)
    with patch.object(assembly, "potential_moment", wraps=assembly.potential_moment) as moments, \
            patch.object(assembly, "potential_square_moment", wraps=assembly.potential_square_moment) as squares:
        low, square = assembly._potential_matrices(polys, 160)
    for calls in (moments.call_args_list, squares.call_args_list):
        powers = [call.args[0] for call in calls]
        assert len(powers) == len(set(powers))
        assert set(powers) <= set(range(11))
    old_low, old_square = frozen.potential_matrices(polys, 160)
    _assert_matrix_overlap(low, old_low)
    _assert_matrix_overlap(square, old_square)
    _assert_symmetry_and_parity(low)
    _assert_symmetry_and_parity(square)


def test_residual_monomial_actions_are_reused_with_exact_image_equality():
    polys = frozen.legendre_polynomials(5)
    with patch.object(assembly, "_abs_power_action", wraps=assembly._abs_power_action) as actions, \
            patch.object(assembly, "_exact_inner", wraps=assembly._exact_inner) as integrals:
        images, low, square, delta = assembly._residual_truncation_operator(polys, 16, 160, 11, 20)
    degrees = [k for k, c in enumerate(assembly._suzuki_residual_series_coefficients(16)) if c]
    pairs = [(call.args[0], call.args[1].degree()) for call in actions.call_args_list]
    assert len(pairs) == len(set(pairs))
    assert set(pairs) <= {(degree, k) for k in range(6) for degree in degrees}
    coefficient_work = sum(sum(bool(c) for c in call.args[1].coeffs()) for call in actions.call_args_list)
    assert coefficient_work <= 6 * len(degrees)
    assert integrals.call_count <= 24  # Two matrices, six triangular pairs per parity.
    # Match the enclosing precision scope of the real v1 caller.
    with ctx.workprec(160):
        old_images, old_low, old_square, old_delta = frozen.residual_truncation_operator(
            polys, 16, 160, 11, 20,
        )
    for image, old in zip(images, old_images, strict=True):
        assert [Fraction(int(c.p), int(c.q)) for c in image.coeffs()] == old
    for new, old, left_polys in ((low, old_low, polys), (square, old_square, old_images)):
        for i in range(6):
            for j in range(6):
                expected = frozen.exact_poly_inner(left_polys[i], old_images[j])
                for value in (new[i][j], old[i][j]):
                    lower, upper = arb_to_rational_enclosure(value)
                    assert lower <= expected <= upper
    assert arb_to_rational_enclosure(delta) == arb_to_rational_enclosure(old_delta)


def test_support_and_precision_local_reuse_cannot_leak_between_assemblies():
    sequence = [(Fraction(11, 20), 128), (Fraction(7, 10), 256),
                (Fraction(1, 4), 96), (Fraction(11, 20), 128)]
    results = []
    for support, prec in sequence:
        new, reference = _assemblies(support, prec)
        for name in ("P", "P_squared", "GP", "A", "GV", "GR"):
            _assert_matrix_overlap(new[name], reference[name])
        assert new["mu"].overlaps(reference["mu"])
        results.append(new)
    assert [t.m for t in results[1]["active_terms"]] == [2, 3, 4]
    assert results[2]["active_terms"] == ()
    assert not results[0]["P"][0][0].overlaps(results[1]["P"][0][0])
    for name in ("P", "P_squared", "GP", "A", "GV", "GR"):
        for i in range(6):
            for j in range(6):
                assert arb_to_rational_enclosure(results[0][name][i][j]) == \
                    arb_to_rational_enclosure(results[-1][name][i][j])


def test_full_assembler_builds_the_arithmetic_partition_once():
    with patch.object(arithmetic, "_sorted_breakpoints", wraps=arithmetic._sorted_breakpoints) as partition:
        result = assembly.assemble_multi_prime_schur(
            n=6, prec=160, residual_order=8, support_num=11, support_den=20, require_positive_mu=False,
        )
    assert partition.call_count == 1
    _, reference = _assemblies(Fraction(11, 20), 160)
    for name in ("P", "P_squared", "GP", "A", "GV", "GR"):
        _assert_matrix_overlap(result[name], reference[name])
