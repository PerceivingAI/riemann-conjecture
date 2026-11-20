"""Independent complete signed quantities and physical projection boundaries."""
from fractions import Fraction
from types import SimpleNamespace

from flint import arb, ctx, fmpq
import pytest

from scripts.whole_source import analytic, producer
from scripts.whole_source.contract import QuantityKey, bind_problem, expected_domain


@pytest.fixture(scope="module")
def original():
    return bind_problem("retained-t081")


@pytest.fixture(scope="module")
def control(original):
    # A complete small algebra/analytic control, not an admissible research profile.
    return SimpleNamespace(N=6, M=12, K=2, support=original.support,
        active_terms=original.active_terms, kernel_coefficients=original.kernel_coefficients[:3],
        source_gauss_order=9, kappa=original.kappa, arithmetic=original.arithmetic)


def agree(source, independent, bits=160):
    difference = source-independent
    assert difference.contains(0)
    assert abs(difference).upper() < arb(2)**-bits


@pytest.mark.parametrize("m,n", [(0, 0), (2, 0), (2, 2), (4, 2), (3, 3), (6, 4), (7, 5), (8, 4), (10, 4)])
def test_full_residual_endpoint_low_and_band_agree(control, m, n):
    assert producer.residual_bilinear(control, m, n) == analytic.residual_bilinear(control, m, n)


@pytest.mark.parametrize("m,n", [(0, 0), (1, 1), (0, 4), (4, 0), (4, 4), (5, 5)])
def test_logarithmic_potential_and_complete_square_agree(m, n):
    with ctx.workprec(512):
        agree(producer.potential_bilinear(m, n), analytic.potential_bilinear(m, n), 350)
        agree(producer.potential_square(m, n), analytic.potential_square(m, n), 350)


def test_constant_logarithmic_integrals_have_closed_values():
    with ctx.workprec(512):
        log2 = arb(2).log()
        agree(producer.potential_bilinear(0, 0), 2-2*log2, 350)
        agree(analytic.potential_square(0, 0), 2*log2**2-4*log2+4-arb.pi()**2/6, 350)


@pytest.mark.parametrize("m,n", [(0, 0), (1, 1), (0, 4), (4, 0), (4, 4), (5, 5)])
def test_complete_signed_square_and_ordered_log_windows(control, m, n):
    with ctx.workprec(512):
        agree(producer.combined_square_entry(control, m, n), analytic.combined_square_entry(control, m, n), 300)
        agree(producer.ordered_vp(control, m, n), analytic.ordered_vp(control, m, n), 300)


def test_ordered_vp_is_not_replaced_by_its_transpose(control):
    with ctx.workprec(512):
        forward = analytic.ordered_vp(control, 0, 4)
        reverse = analytic.ordered_vp(control, 4, 0)
        assert not (forward-reverse).contains(0)


@pytest.mark.parametrize("n", [0, 1, 4, 5])
def test_full_physical_column_includes_head_and_correct_masses(control, n):
    with ctx.workprec(512):
        source, consumer = producer.operator_column(control, n), analytic.operator_column(control, n)
        for m, left, right in zip(range(n % 2, control.M, 2), source, consumer):
            agree(left, right, 300)
            linear = sum((analytic.signed_window_arithmetic(control, m, n, t, w)
                          for t in range(4) for w in range(2)), arb(0)) if m < control.M else arb(0)
            agree(left, linear+analytic.potential_bilinear(m, n), 300)


def test_full_exterior_pays_low_and_head_projection(control):
    with ctx.workprec(512):
        columns = {n: analytic.operator_column(control, n) for n in (0, 4)}
        source = producer.assemble_entry(control, 0, 4, columns)
        consumer = analytic.assemble_entry(control, 0, 4, columns)
        for key in source:
            agree(source[key], consumer[key], 280)
        joint = consumer[("J_F", 0, 4)]
        low = sum((columns[0][k//2]*columns[4][k//2]*fmpq(2*k+1, 2)
                   for k in range(0, control.N, 2)), arb(0))
        head = sum((columns[0][k//2]*columns[4][k//2]*fmpq(2*k+1, 2)
                    for k in range(control.N, control.M, 2)), arb(0))
        agree(consumer[("G_exterior", 0, 4)], joint-low-head, 280)
        assert not head.contains(0)
        assert not low.contains(0)
        agree(consumer[("weighted_complete_tail", 0, 4)],
              consumer[("G_exterior", 0, 4)]*fmpq(control.kappa.numerator, control.kappa.denominator), 280)


def test_selected_component_domains_preserve_order_and_projection_extent(original):
    ordered = QuantityKey("VP", 0, entry=(original.N-2, 0))
    domain = expected_domain(original, ordered)
    assert tuple(domain.rows) == (original.N-2,) and tuple(domain.columns) == (0,)
    assert domain.symmetric_upper is False
    column = expected_domain(original, QuantityKey("F_column", 1))
    assert tuple(column.rows)[-1] == original.M-1
    assert tuple(column.columns)[-1] == original.N-1
