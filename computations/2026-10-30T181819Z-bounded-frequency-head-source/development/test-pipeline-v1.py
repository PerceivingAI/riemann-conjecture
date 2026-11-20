"""Completed column partitions, exact publications and complete source-domain reading."""
from contextlib import contextmanager
from fractions import Fraction
import json
from pathlib import Path
import tempfile

import pytest
from flint import arb, ctx, fmpq

from scripts.whole_source import producer, analytic
from scripts.whole_source.artifacts import (
    CollectionLock, ChunkStore, IntervalRecord, _coordinates, _raw,
    decode_publication, publish_publication, stage_publication,
)
from scripts.whole_source.contract import ArtifactRef, ContractError, QuantityKey, ROOT, bind_problem, canonical_bytes, problem_id
from scripts.whole_source.pipeline import (
    COMPLETE, FAMILIES, SourceReader, _bind, _column_task, _kernel, _quantities, _tiles,
    math_problem, prepare_source_inputs,
)
from scripts.whole_source.slice import _parse_staged


@pytest.fixture(scope='module')
def bound():
    cache = ROOT/'.pytest_cache'
    cache.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='source-contract-', dir=cache) as folder:
        folder = Path(folder)
        inputs = prepare_source_inputs(bind_problem('retained-t081'), folder/'inputs',
            origin_git_commit='b19905565ace1f4a1b9ea1387ce123377c65a0e0', origin_git_dirty=True,
            control=True, tile_modes=2)
        problem, config, roles = _bind(inputs['problem'], inputs['execution'], ROOT)
        yield folder, problem, config, roles


@contextmanager
def collection(bound, name):
    folder, _, _, roles = bound
    spec = roles['producer'][0]
    with CollectionLock.acquire(folder/name, spec) as lock:
        (lock.root/'attempts/check').mkdir()
        lock.register_attempt('check')
        yield lock, ChunkStore(lock, spec, attempt_id='check'), spec


def test_whole_dependency_column_and_ragged_square_tiles_keep_distinct_partitions(bound):
    with collection(bound, 'column-shape') as (lock, store, spec), ctx.workprec(768):
        model = math_problem(spec.problem, True)
        data = producer.operator_column(model, 0)
        domain = _column_task(spec, 'F_column', 0)
        staged = store.stage_chunk(domain, (IntervalRecord(m, 0, (0,), Fraction(str(v.lower().fmpq())),
                                  Fraction(str(v.upper().fmpq()))) for m, v in zip(range(0, 12, 2), data)))
        records = store.read_chunk(store.publish_chunk(domain, staged)).records
        expected = analytic.operator_column(model, 0)
        assert [r.row for r in records] == [0, 2, 4, 6, 8, 10]
        assert not expected[-1].contains(0)
        for record, value in zip(records, expected):
            assert arb(fmpq(record.lower.numerator, record.lower.denominator)) <= value.upper()
            assert arb(fmpq(record.upper.numerator, record.upper.denominator)) >= value.lower()
        finals = list(_tiles(spec, QuantityKey('A_model', 0)))
        assert [[len(t.rows), len(t.columns)] for t in finals] == [[2, 2], [2, 1], [1, 1]]


@pytest.mark.parametrize('parity', [0, 1])
def test_actual_kernel_cache_keeps_terminal_full_mass_with_zero_weight_jumps(bound, parity):
    with collection(bound, 'terminal-'+str(parity)) as (lock, store, spec), ctx.workprec(768):
        model = math_problem(spec.problem, True)
        model.inverse_weights = (Fraction(7, 3),)*len(model.frequency_edges)
        rows = _kernel(store.staging_context(), model, parity, {'frequency_step': producer.frequency_step})
        count = 0
        for wire in rows:
            task, staged = _parse_staged(wire)
            for record in store.read_chunk(store.publish_chunk(task, staged)).records:
                expected = Fraction(14, 3*(2*record.row+1)) if record.row == record.column else Fraction(0)
                assert record.lower <= expected <= record.upper
                if record.row == record.column:
                    assert record.lower > 0
                count += 1
        assert count == 6


def _manifest(spec, tiles):
    return {'format':'whole-source-scientific-manifest-v1', 'problem_id':problem_id(spec.problem),
            'collection':spec.to_dict(), 'control':True, 'geometry':{'N':6,'M':12,'K':2},
            'role':'producer','publication_bits':256,'scope':'CONTROL_ONLY_REDUCED_MODEL',
            'tiles':tiles,'full_mathematical_source':False,'analytical_acceptance':False,
            'matrix_positivity':False,'production_admission':False,
            'residual_model_payment':'Lambda D once in later exact full-space proof'}


@pytest.fixture(scope='module')
def publications(bound):
    with collection(bound, 'publication') as (lock, store, spec):
        tiles = []
        for family, name in FAMILIES.items():
            for parity in (0, 1):
                for task in _tiles(spec, QuantityKey(name, parity)):
                    records = (IntervalRecord(m, n, (0,), Fraction(m-n+1, 3), Fraction(m-n+1, 3))
                               for m, n in _coordinates(task, True))
                    staged = stage_publication(store.staging_context(), task, records)
                    ref = publish_publication(store, task, staged)
                    tiles.append({'family':family,'parity':parity,'task':task.to_dict(),
                                  'artifact':{'path':ref.path,'sha256':ref.sha256,'size':ref.size}})
        manifest = _manifest(spec, tiles)
        path = lock.root/'source-manifest.json'
        path.write_bytes(canonical_bytes(manifest))
        yield path, spec, manifest


def test_publication_is_outward_on_actual_256_bit_grid_and_covers_both_parities(publications):
    path, spec, _ = publications
    reader = SourceReader(path, spec, control=True)
    count = 0
    for row, records in reader.tiles():
        for record in records:
            exact = Fraction(record.row-record.column+1, 3)
            assert record.lower < exact < record.upper
            assert (record.lower*(1 << 256)).denominator == 1
            assert (record.upper*(1 << 256)).denominator == 1
            assert record.upper-record.lower <= Fraction(3, 1 << 256)
            count += 1
    assert count == 36
    assert reader.document['full_mathematical_source'] is False


@pytest.mark.parametrize('change', ['missing_last_tile', 'repeated_tile', 'wrong_parity'])
def test_source_reader_requires_exact_complete_coordinate_cover(publications, tmp_path, change):
    path, spec, original = publications
    value = json.loads(json.dumps(original))
    if change == 'missing_last_tile':
        value['tiles'].pop()
    elif change == 'repeated_tile':
        value['tiles'][-1] = value['tiles'][-2]
    else:
        value['tiles'][-1]['parity'] = 0
    candidate = tmp_path/'source.json'
    candidate.write_bytes(canonical_bytes(value))
    with pytest.raises(ContractError, match='cover|coordinate'):
        SourceReader(candidate, spec, control=True)
