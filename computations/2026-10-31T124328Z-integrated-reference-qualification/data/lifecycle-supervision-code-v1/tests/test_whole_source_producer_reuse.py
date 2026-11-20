"""Exact enclosure preservation and bounded producer preparation reuse."""
from types import SimpleNamespace

import pytest
from flint import arb, ctx, fmpq

from scripts.whole_source import producer, execution
from scripts.whole_source.contract import bind_problem
from scripts.whole_source.pipeline import math_problem, _producer_tile_requirements
from scripts.whole_source.reuse import WorkingSet, PREPARED_BYTES, exact_polynomial_bytes


def same(left, right):
    assert len(left) == len(right)
    for x, y in zip(left, right):
        assert x.mid() == y.mid()
        assert x.rad() == y.rad()


def model(full=False):
    problem = bind_problem('retained-t081')
    base = math_problem(problem, not full)
    values = {name: getattr(base, name) for name in (
        'N', 'M', 'K', 'support', 'kernel_coefficients', 'active_terms', 'source_gauss_order', 'kappa')}
    # Keep physical boundary degrees, while explicitly limiting integration work.
    values.update(source_gauss_order=3 if full else 35,
                  active_terms=base.active_terms[:1])
    return SimpleNamespace(**values)


@pytest.mark.parametrize('parity', [0, 1])
@pytest.mark.parametrize('full', [False, True])
def test_columns_preserve_scalar_midpoints_and_radii(full, parity):
    problem = model(full)
    inputs = (problem.N-4+parity, problem.N-2+parity)
    with ctx.workprec(160):
        expected = {n: producer.operator_column(problem, n) for n in inputs}
        actual = producer.operator_columns(problem, inputs)
        for n in inputs:
            same(actual[n], expected[n])
        same(producer.operator_columns(problem, inputs[:1])[inputs[0]], expected[inputs[0]])


@pytest.mark.parametrize('inputs', [(), (0, 1), (2, 0), (0, 0), (0, 2, 4), (-1,), (6,), (True,)])
def test_columns_reject_invalid_panels(inputs):
    with pytest.raises(ValueError):
        producer.operator_columns(model(), inputs)


def test_operator_panel_shares_each_recurrence(monkeypatch):
    problem = model()
    original = producer.legendre_values
    counts = []
    def counted(x, count):
        counts.append(count)
        return original(x, count)
    monkeypatch.setattr(producer, 'legendre_values', counted)
    with ctx.workprec(160):
        producer.operator_columns(problem, (2, 4))
    assert counts.count(problem.M) == 2*problem.source_gauss_order
    assert counts.count(5) == 2*problem.source_gauss_order
    assert len(counts) == 4*problem.source_gauss_order


@pytest.mark.parametrize('parity', [0, 1])
def test_head_images_consume_ragged_tiles_once_and_reflect(parity):
    problem = model()
    a, b, c = (problem.N+parity+i for i in (0, 2, 4))
    tiles = [[(a, a, arb(3)), (a, b, arb(1)), (b, b, arb(4))],
             [(a, c, arb(2)), (b, c, arb(3))], [(c, c, arb(5))]]
    columns = {parity: [arb(2), arb(-1), arb(3)],
               parity+2: [arb(fmpq(1, 3)), arb(2, fmpq(1, 128)), arb(-4)]}
    consumed = []
    def stream():
        for tile in tiles:
            consumed.append(1)
            yield iter(tile)
    with ctx.workprec(160):
        actual = producer.head_images(problem, columns, stream())
        for n, column in columns.items():
            same(actual[n], producer.head_image(problem, column, iter(tiles)))
        assert actual[parity] == [arb(11), arb(7), arb(16)]
    assert len(consumed) == len(tiles)
    with pytest.raises(ValueError, match='incomplete'):
        producer.head_images(problem, {parity: [arb(0)]}, iter(tiles))
    with pytest.raises(ValueError, match='physical'):
        producer.head_images(problem, columns, [[(a+1, a+1, arb(1))]])
    with pytest.raises(ValueError):
        producer.head_images(problem, {0: columns[parity], 1: columns[parity]}, [])


def test_row_basis_reuse_invalidation_and_exact_results(monkeypatch):
    problem = model()
    cache = WorkingSet(PREPARED_BYTES)
    monkeypatch.setattr(producer, '_ROW_BASES', cache)
    original = producer.basis
    calls = []
    def counted(n):
        calls.append(n)
        return original(n)
    monkeypatch.setattr(producer, 'basis', counted)


    with ctx.workprec(160):
        columns = producer.operator_columns(problem, (0, 2))
        columns.update(producer.operator_columns(problem, (4,)))
        first = producer.assemble_tile(problem, (0, 2), (2,), columns)
        producer.assemble_tile(problem, (0, 2), (4,), columns)
        assert cache.hits == 2
        assert set(cache.values) == {0, 2}
        before_hits = cache.hits
        repeated = producer.assemble_tile(problem, (0, 2), (2,), columns)
        assert cache.hits == before_hits+2
        for pair in first:
            for key in first[pair]:
                same([first[pair][key]], [repeated[pair][key]])
        producer.assemble_tile(problem, (0,), (4,), columns)
        assert calls[-2:] == [0, 4]
        with ctx.workprec(192):
            producer.assemble_tile(problem, (0,), (4,), columns)
        assert calls[-2:] == [0, 4]
    assert cache.resident <= cache.peak <= cache.limit


@pytest.mark.parametrize('parity', [0, 1])
def test_head_images_preserve_full_physical_boundary(parity):
    problem = model(True)
    a, b, c = (problem.M-6+parity+i for i in (0, 2, 4))
    tiles = [[(a, a, arb(3)), (a, b, arb(fmpq(1, 7))), (b, b, arb(4))],
             [(a, c, arb(2)), (b, c, arb(3))], [(c, c, arb(5))]]
    inputs = (problem.N-4+parity, problem.N-2+parity)
    columns = {n: [arb(fmpq((k+n) % 11-5, 13))
                   for k in range((problem.M-problem.N)//2)] for n in inputs}
    with ctx.workprec(160):
        result = producer.head_images(problem, columns, iter(tiles))
        for n in inputs:
            same(result[n], producer.head_image(problem, columns[n], iter(tiles)))


def test_basis_reservation_precedes_construction(monkeypatch):
    problem = model()
    cache = WorkingSet(4096)
    monkeypatch.setattr(producer, '_ROW_BASES', cache)
    original = producer.basis
    reservations = []
    reserve = cache.reserve
    def admitted(key, size):
        reservations.append(key)
        return reserve(key, size)
    def constructed(n):
        if n == 4:
            assert reservations == [4]
            assert cache.resident == 4096
        return original(n)
    monkeypatch.setattr(cache, 'reserve', admitted)
    monkeypatch.setattr(producer, 'basis', constructed)
    with ctx.workprec(160):
        columns = producer.operator_columns(problem, (4,))
        producer.assemble_tile(problem, (4,), (4,), columns)
    assert not cache.values
    assert cache.peak <= cache.limit
    assert 4096+sum(exact_polynomial_bytes(n)+1024 for n in range(762, 826, 2)) < PREPARED_BYTES


def test_runtime_account_includes_catalog_and_all_reuse(monkeypatch):
    problem = model()
    monkeypatch.setattr(execution, '_WORKER', None)
    base = _producer_tile_requirements(problem, (0,), (2,), precision_bits=ctx.prec)
    account = producer.tile_account(problem, (0,), (2,))
    assert account['private_bytes'] == base['private_bytes']+104*1024**2
    monkeypatch.setattr(execution, '_WORKER', (SimpleNamespace(
        worker_private_mib=104, native_workspace_mib=128),))
    with pytest.raises(MemoryError, match='allowance'):
        producer.tile_account(problem, (0,), (2,))
