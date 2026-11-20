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


@pytest.mark.parametrize('n', [4, 5])
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
        assert analytic.residual_bilinear(model, k, n) != 0


@pytest.mark.parametrize('parity', [0, 1])
def test_constant_frequency_majorant_retains_positive_terminal_full_mass(problem, parity):
    model = math_problem(problem, True)
    weight = Fraction(7, 3)
    weights = [weight]*len(problem.frequency_edges)
    with ctx.workprec(512):
        for n in range(6+parity, 12, 2):
            total = arb(fmpq(weight.numerator, weight.denominator))*fmpq(2, 2*n+1)
            for k, omega in enumerate(problem.frequency_edges[1:]):
                total += (weights[k]-weights[k+1])*producer.frequency_anchor(model, omega)(n, n)
            assert (total-arb(fmpq(14, 3*(2*n+1)))).contains(0)
            assert total > 0
            # Dropping the terminal term would produce zero despite full positive mass.
            assert not total.contains(0)
