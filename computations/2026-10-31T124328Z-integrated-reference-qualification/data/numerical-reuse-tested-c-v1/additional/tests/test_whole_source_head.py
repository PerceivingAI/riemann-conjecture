"""Frequency normalization, paid inputs and complete signed head contractions."""
from fractions import Fraction
from types import SimpleNamespace

import pytest
from flint import arb, ctx, fmpq

from scripts.whole_source import producer, analytic
from scripts.whole_source.contract import bind_problem
from scripts.whole_source.pipeline import math_problem


@pytest.fixture(scope='module')
def problem():
    return bind_problem('retained-t081')


@pytest.mark.parametrize('parity', [0, 1])
@pytest.mark.parametrize('anchor', [0, 1, 30, -1])
def test_complete_frequency_projectors_and_both_halves(problem, parity, anchor):
    model = math_problem(problem, True)
    omega = problem.frequency_edges[anchor]
    with ctx.workprec(768):
        source = producer.frequency_anchor(model, omega)
        independent = analytic.frequency_anchor(model, omega)
        for m, n in [(parity, parity), (6+parity, 8+parity), (10+parity, 10+parity)]:
            x, y = source(m, n), independent(m, n)
            assert (x-y).contains(0)
            assert (x-y).abs_upper() < arb(2)**-300
            if anchor == 0:
                assert x == 0 and y == 0
            if anchor == -1 and m == n:
                mass = arb(fmpq(2, 2*m+1))
                # A one-sided frequency integral tends to half this physical mass.
                assert (x-mass).abs_upper() < arb(fmpq(1, 5000))
            assert (source(n, m)-x).contains(0)


def test_nonexact_bessel_seed_pays_actual_argument_uncertainty():
    with ctx.workprec(512):
        c = arb(3, arb(fmpq(1, 128)))
        paid = producer._frequency_seed(c, 5)
        middle = producer._frequency_seed(arb(3), 5)
        endpoint = arb(fmpq(385, 128))
        actual = endpoint.bessel_j(arb(fmpq(11, 2)))*(arb.pi()/(2*endpoint)).sqrt()
        assert paid.contains(actual)
        assert not middle.contains(actual)


@pytest.mark.parametrize('parity', [0, 1])
def test_ragged_full_head_product_keeps_both_cross_block_orientations(parity):
    model = SimpleNamespace(N=6, M=12)
    a, b, c = 6+parity, 8+parity, 10+parity
    tiles = [[(a, a, arb(3)), (a, b, arb(1)), (b, b, arb(4))],
             [(a, c, arb(2)), (b, c, arb(3))], [(c, c, arb(5))]]
    column = [arb(2), arb(-1), arb(3)]
    with ctx.workprec(512):
        for role in (producer, analytic):
            image = role.head_image(model, column, iter(tiles))
            assert image == [arb(11), arb(7), arb(16)]
            assert role.head_pair(model, column, image) == 63
            omitted = role.head_image(model, column, iter([tiles[0], tiles[2]]))
            assert role.head_pair(model, column, omitted) == 57


@pytest.mark.parametrize('n', range(6))
def test_signed_residual_head_uses_output_expansion_mass(problem, n):
    model = math_problem(problem, True)
    with ctx.workprec(768):
        source_f = producer.operator_column(model, n)
        independent_f = analytic.operator_column(model, n)
        source = producer.head_column(model, n, source_f)
        independent = analytic.head_column(model, n, independent_f)
        for k, x, y in zip(range(6+n % 2, 12, 2), source, independent):
            assert (x-y).contains(0)
            expected = (independent_f[k//2]+arb(analytic.residual_bilinear(model, k, n)))*fmpq(2*k+1, 2)
            assert (x-expected).abs_upper() < arb(2)**-300
        k = 6+n % 2
        bare_bilinear = independent_f[k//2]+arb(analytic.residual_bilinear(model, k, n))
        assert not (source[0]-bare_bilinear).contains(0)
        assert (analytic.residual_bilinear(model, k, n) != 0) == (n >= 4)


@pytest.mark.parametrize('n', [0, 1, 86, 87, 738, 739, 740, 741, 824, 825])
def test_independent_image_preserves_exact_full_residual_contractions(problem, n):
    image = analytic._residual_image(problem, n)
    parity = n % 2
    for m in (parity, 86+parity, 826+parity, 910+parity, 912+parity, 1650+parity):
        primitive = (analytic.rodrigues_ratio(m)*image).integral()
        actual = primitive(1)-primitive(-1)
        assert actual == analytic.residual_bilinear(problem, m, n)
        if m > n+problem.K+1:
            assert actual == 0
        if (m, n) in ((826, 740), (827, 741), (910, 824), (911, 825)):
            assert actual != 0
    if n == 0:
        primitive = image.integral()
        expected = sum((fmpq(c.numerator, c.denominator)*fmpq(2**(d+3), (d+1)*(d+2))
                        for d, c in enumerate(problem.kernel_coefficients)), fmpq(0))
        assert primitive(1)-primitive(-1) == expected


@pytest.mark.parametrize('damage', ['changed', 'truncated'])
def test_head_rejects_inconsistent_complete_kernel(problem, damage):
    model = math_problem(problem, True)
    coefficients = list(model.kernel_coefficients)
    if damage == 'changed':
        coefficients[-1] += Fraction(1, 7)
    else:
        coefficients.pop()
    invalid = SimpleNamespace(**{**vars(model), 'kernel_coefficients': tuple(coefficients)})
    with pytest.raises(ArithmeticError, match='complete residual coefficients disagree'):
        analytic.head_column(invalid, 4, [arb(0) for _ in range(model.M//2)])


@pytest.mark.parametrize('n', [0, 1, 86, 87, 738, 739, 740, 741, 824, 825])
def test_producer_head_preserves_every_scalar_residual_and_zero_column(problem, n, monkeypatch):
    rows = list(range(problem.N+n % 2, problem.M, 2))
    with ctx.workprec(problem.arithmetic.source_bits):
        full = [arb(fmpq((i % 7)-3, 8)) for i in range(problem.M//2)]
        expected = [(full[k//2]+arb(producer.residual_bilinear(problem, k, n)))*fmpq(2*k+1, 2)
                    for k in rows]
        original = producer._residual_tile_column
        preparations = []
        def prepared(model, column, requested):
            preparations.append((column, tuple(requested)))
            return original(model, column, requested)
        monkeypatch.setattr(producer, '_residual_tile_column', prepared)
        actual = producer.head_column(problem, n, full)
        assert all(left.mid().fmpq() == right.mid().fmpq() and
                   left.rad().fmpq() == right.rad().fmpq()
                   for left, right in zip(actual, expected, strict=True))
        assert len(preparations) == int(any(k <= n+problem.K+1 for k in rows))
