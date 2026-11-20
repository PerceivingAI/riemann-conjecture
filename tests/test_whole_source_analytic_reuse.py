"""Exact analytic panel enclosures and byte-admitted Rodrigues reuse."""
from collections import Counter
from types import SimpleNamespace

import pytest
from flint import arb, ctx, fmpq

from scripts.whole_source import analytic, execution
from scripts.whole_source.contract import bind_problem
from scripts.whole_source.pipeline import math_problem, _analytic_tile_requirements
from scripts.whole_source.reuse import WorkingSet, PREPARED_BYTES, exact_polynomial_bytes


def model():
    return math_problem(bind_problem('retained-t081'), True)


def same(left, right):
    assert len(left) == len(right)
    for x, y in zip(left, right):
        assert x.mid() == y.mid()
        assert x.rad() == y.rad()


@pytest.mark.parametrize('parity', [0, 1])
@pytest.mark.parametrize('count', [1, 2])
def test_columns_match_independent_scalar(parity, count):
    problem = model()
    inputs = (parity, parity+2)[:count]
    with ctx.workprec(160):
        expected = {n: analytic.operator_column(problem, n) for n in inputs}
        actual = analytic.operator_columns(problem, inputs)
        for n in inputs:
            same(expected[n], actual[n])


@pytest.mark.parametrize('inputs', [(), (0, 1), (2, 0), (0, 0), (0, 2, 4), (-1,), (True,)])
def test_invalid_panels(inputs):
    with pytest.raises(ValueError):
        analytic.operator_columns(model(), inputs)


def test_outside_panel_domain():
    problem = model()
    with pytest.raises(ValueError):
        analytic.operator_columns(problem, (problem.N,))


def test_each_physical_rodrigues_row_is_shared(monkeypatch):
    problem = model()
    original = analytic.rodrigues_ratio
    calls = Counter()
    def counted(n):
        calls[n] += 1
        return original(n)
    monkeypatch.setattr(analytic, 'rodrigues_ratio', counted)
    with ctx.workprec(160):
        analytic.operator_columns(problem, (0, 2))
    assert calls == Counter({n: 1 + (n in (0, 2)) for n in range(0, problem.M, 2)})


@pytest.mark.parametrize('parity', [0, 1])
def test_ragged_head_tiles_read_once_with_both_reflections(parity):
    problem = model()
    width = (problem.M-problem.N)//2
    inputs = (parity, parity+2)
    with ctx.workprec(160):
        columns = {n: [arb(fmpq((k+1)*(n+1), k+3)) for k in range(width)] for n in inputs}
        entries = [(problem.N+parity+2*i, problem.N+parity+2*j,
                    arb(fmpq(i+j+1, i+j+3))) for i in range(width) for j in range(i, width)]
        tiles = [entries[:1], entries[1:4], entries[4:]]
        visits = []
        def once():
            for tile in tiles:
                visits.append(1)
                yield iter(tile)
        result = analytic.head_images(problem, columns, once())
        assert len(visits) == len(tiles)
        for n in inputs:
            same(result[n], analytic.head_image(problem, columns[n], tiles))
        with pytest.raises(ValueError):
            analytic.head_images(problem, columns, [[(problem.N+1-parity, problem.N+1-parity, arb(1))]])
        with pytest.raises(ValueError):
            analytic.head_images(problem, {parity: []}, [])


def test_row_cache_reuses_only_anchor_rows_and_invalidates(monkeypatch):
    problem = model()
    cache = WorkingSet(PREPARED_BYTES)
    monkeypatch.setattr(analytic, '_ROW_BASES', cache)
    original = analytic.rodrigues_ratio
    calls = []
    def counted(n):
        calls.append(n)
        return original(n)
    with ctx.workprec(160):
        columns = analytic.operator_columns(problem, (0, 2))
        columns.update(analytic.operator_columns(problem, (4,)))
        monkeypatch.setattr(analytic, 'rodrigues_ratio', counted)
        first = analytic.assemble_tile(problem, (0, 2), (2,), columns)
        bases = {n: entry[0] for n, entry in cache.values.items()}
        snapshots = {n: str(value) for n, value in bases.items()}
        analytic.assemble_tile(problem, (0, 2), (4,), columns)
        assert set(cache.values) == {0, 2}
        assert all(cache.values[n][0] is bases[n] for n in bases)
        assert snapshots == {n: str(value) for n, value in bases.items()}
        repeated = analytic.assemble_tile(problem, (0, 2), (2,), columns)
        for pair in first:
            for key in first[pair]:
                same([first[pair][key]], [repeated[pair][key]])
        assert calls.count(0) == 1
        # Residual images also construct their own independent Rodrigues input.
        assert calls.count(4) == 2
        analytic.assemble_tile(problem, (0,), (4,), columns)
        assert cache.policy[-1] == (0,)
        previous = cache.values[0][0]
        with ctx.workprec(192):
            analytic.assemble_tile(problem, (0,), (4,), columns)
        assert cache.values[0][0] is not previous
    assert cache.resident <= cache.peak <= cache.limit


def test_reservation_precedes_real_construction(monkeypatch):
    problem = model()
    cache = WorkingSet(4096)
    monkeypatch.setattr(analytic, '_ROW_BASES', cache)
    original = analytic.rodrigues_ratio
    reserve = cache.reserve
    reservations = []
    def admitted(key, size):
        reservations.append(key)
        return reserve(key, size)
    def constructed(n):
        if n == 4:
            assert reservations == [4]
            assert cache.resident == 4096
        return original(n)
    with ctx.workprec(160):
        columns = analytic.operator_columns(problem, (4,))
        monkeypatch.setattr(cache, 'reserve', admitted)
        monkeypatch.setattr(analytic, 'rodrigues_ratio', constructed)
        analytic.assemble_tile(problem, (4,), (4,), columns)
    assert not cache.values
    assert cache.peak <= cache.limit
    assert 4096+sum(exact_polynomial_bytes(n)+1024 for n in range(762, 826, 2)) < PREPARED_BYTES


def test_account_includes_reuse_and_catalog(monkeypatch):
    problem = model()
    monkeypatch.setattr(execution, '_WORKER', None)
    base = _analytic_tile_requirements(problem, (0,), (2,), precision_bits=ctx.prec)
    account = analytic.tile_account(problem, (0,), (2,))
    assert account['private_bytes'] == base['private_bytes']+104*1024**2
    monkeypatch.setattr(execution, '_WORKER', (SimpleNamespace(worker_private_mib=104, native_workspace_mib=128),))
    with pytest.raises(MemoryError, match='allowance'):
        analytic.tile_account(problem, (0,), (2,))


@pytest.mark.parametrize('parity', [0, 1])
def test_fullmode_head_boundary_uses_bounded_sparse_tiles(parity):
    problem = math_problem(bind_problem('retained-t081'), False)
    width = (problem.M-problem.N)//2
    first = problem.N+parity
    last = first+2*(width-1)
    with ctx.workprec(160):
        columns = {parity: [arb(fmpq(k+1, k+2)) for k in range(width)]}
        tiles = [[(first, first, arb(2)), (first, last, arb(fmpq(2, 3)))],
                 [(last, last, arb(3))]]
        actual = analytic.head_images(problem, columns, iter(tiles))
        same(actual[parity], analytic.head_image(problem, columns[parity], tiles))
