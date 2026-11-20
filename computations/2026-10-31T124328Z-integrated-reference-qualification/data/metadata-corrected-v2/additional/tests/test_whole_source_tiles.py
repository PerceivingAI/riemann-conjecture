"""Complete bounded tiles against scalar mathematics and omitted-term controls."""
from types import SimpleNamespace

from flint import arb, ctx, fmpq
import pytest

from scripts.whole_source import analytic, producer
from scripts.whole_source.contract import bind_problem


@pytest.fixture(scope="module")
def problem():
    original = bind_problem("retained-t081")
    return SimpleNamespace(N=10, M=20, K=2, source_gauss_order=15,
        support=original.support, active_terms=original.active_terms,
        kernel_coefficients=original.kernel_coefficients[:3], kappa=original.kappa,
        arithmetic=original.arithmetic)


def agree(left, right, bits=280):
    difference = left-right
    assert difference.contains(0)
    assert abs(difference).upper() < arb(2)**-bits


@pytest.mark.parametrize("parity", [0, 1])
@pytest.mark.parametrize("shape", ["diagonal", "ragged", "terminal"])
def test_complete_tiles_match_both_scalar_references(problem, parity, shape):
    if shape == "diagonal":
        rows = columns = (parity, parity+2, parity+4)
    elif shape == "ragged":
        rows, columns = (parity, parity+2), (parity+4, parity+6, parity+8)
    else:
        rows, columns = (parity+6, parity+8), (parity+8,)
    with ctx.workprec(512):
        modes = sorted(set(rows) | set(columns))
        source_columns = {n: producer.operator_column(problem, n) for n in modes}
        independent_columns = {n: analytic.operator_column(problem, n) for n in modes}
        source = producer.assemble_tile(problem, rows, columns, source_columns)
        independent = analytic.assemble_tile(problem, rows, columns, independent_columns)
        expected_pairs = {(m, n) for m in rows for n in columns if m <= n}
        assert set(source) == set(independent) == expected_pairs
        for m, n in expected_pairs:
            scalar_source = producer.assemble_entry(problem, m, n, source_columns)
            scalar_independent = analytic.assemble_entry(problem, m, n, independent_columns)
            assert set(source[m, n]) == set(independent[m, n]) == set(scalar_source) == set(scalar_independent)
            for key in scalar_source:
                agree(source[m, n][key], scalar_source[key])
                agree(independent[m, n][key], scalar_independent[key])
                agree(source[m, n][key], independent[m, n][key])


@pytest.mark.parametrize("role", [producer, analytic])
def test_tile_pays_mixed_terms_both_vp_orders_and_full_projection(problem, role):
    with ctx.workprec(512):
        columns = {n: role.operator_column(problem, n) for n in (0, 8)}
        values = role.assemble_tile(problem, (0,), (8,), columns)[0, 8]
        joint = values["J_F", 0, 8]
        agree(joint, values["VV", 0, 8]+values["P_squared", 0, 8]+
              values["VP", 0, 8]+values["VP", 8, 0])
        assert not (values["VP", 0, 8]-values["VP", 8, 0]).contains(0)
        low = sum((columns[0][k//2]*columns[8][k//2]*fmpq(2*k+1, 2)
                   for k in range(0, problem.N, 2)), arb(0))
        head = sum((columns[0][k//2]*columns[8][k//2]*fmpq(2*k+1, 2)
                    for k in range(problem.N, problem.M, 2)), arb(0))
        exterior = values["G_exterior", 0, 8]
        agree(exterior, joint-low-head)
        assert not (exterior-(joint-low)).contains(0)
        assert not (joint-(values["VV", 0, 8]+values["P_squared", 0, 8])).contains(0)
        agree(values["weighted_complete_tail", 0, 8], exterior*fmpq(
            problem.kappa.numerator, problem.kappa.denominator))


def test_constant_tile_retains_cross_power_square_terms(problem):
    with ctx.workprec(512):
        columns = {0: producer.operator_column(problem, 0)}
        full = producer.assemble_tile(problem, (0,), (0,), columns)[0, 0]["P_squared", 0, 0]
        same_power = arb(0)
        for term in problem.active_terms:
            reduced = SimpleNamespace(**vars(problem))
            reduced.active_terms = (term,)
            same_power += producer.combined_square_entry(reduced, 0, 0)
        assert not (full-same_power).contains(0)
        agree(full, analytic.combined_square_entry(problem, 0, 0))


@pytest.mark.parametrize("parity", [0, 1])
def test_current_recurrence_and_exact_walk_include_declared_last_modes(parity):
    problem = bind_problem("retained-t081")
    last = problem.N-2+parity
    modes = (parity, last-2, last)
    with ctx.workprec(512):
        x = arb(fmpq(2, 7))
        selected = producer._selected_values(x, modes)
        for n in modes:
            exact = analytic.rodrigues_ratio(n)(fmpq(2, 7))
            assert selected[n].contains(exact)
        residuals = producer._residual_tile_column(problem, last, modes)
        for m in modes:
            assert residuals[m] == producer.residual_bilinear(problem, m, last)
            assert residuals[m] == analytic.residual_bilinear(problem, m, last)


@pytest.mark.parametrize("role", [producer, analytic])
def test_resource_account_prices_declared_tiles_before_native_work(role):
    problem = bind_problem("retained-t081")
    with ctx.workprec(problem.arithmetic.audit_bits):
        account = role.tile_account(problem, tuple(range(762, 794, 2)), tuple(range(794, 826, 2)))
        assert 0 < account["private_bytes"] <= 128*1024**2
        assert 0 < account["native_bytes"] <= 128*1024**2
        with pytest.raises(MemoryError):
            role.tile_account(problem, tuple(range(0, 64, 2)), tuple(range(762, 826, 2)))
        with pytest.raises(ValueError):
            role.tile_account(problem, tuple(range(0, 66, 2)), (824,))
