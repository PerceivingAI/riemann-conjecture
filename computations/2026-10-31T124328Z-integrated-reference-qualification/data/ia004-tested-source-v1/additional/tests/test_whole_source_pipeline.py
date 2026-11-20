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
    COMPLETE, FAMILIES, SourceReader, _bind, _column_task, _kernel_group, _kernel_panels,
    _kernel_reduce, _quantities, _tiles,
    math_problem, prepare_source_inputs,
)
from scripts.whole_source.pipeline import scientific_manifest, write_source_execution
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
@pytest.mark.parametrize('group_count', [1, 3])
def test_actual_kernel_cache_keeps_terminal_full_mass_with_zero_weight_jumps(bound, parity, group_count):
    with collection(bound, 'terminal-'+str(parity)+'-'+str(group_count)) as (lock, store, spec), ctx.workprec(768):
        model = math_problem(spec.problem, True)
        model.inverse_weights = (Fraction(7, 3),)*len(model.frequency_edges)
        edges = [i*len(model.frequency_edges)//group_count for i in range(group_count+1)]
        groups = [_kernel_group(store.staging_context(), model, parity,
            {'frequency_step': producer.frequency_step}, start, stop)
            for start, stop in zip(edges, edges[1:])]
        rows = []
        for i, panel in enumerate(_kernel_panels(spec, parity)):
            refs = [{'anchor_start': group['anchor_start'], 'anchor_stop': group['anchor_stop'],
                     'artifact': group['panels'][i]['artifact']} for group in groups]
            rows.extend(_kernel_reduce(store.staging_context(), model, parity, panel, refs))
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


@pytest.mark.parametrize('parity', [0, 1])
def test_grouped_kernel_keeps_nonzero_frequency_jumps_against_independent_formula(bound, parity):
    with collection(bound, 'kernel-jumps-'+str(parity)) as (lock, store, spec), ctx.workprec(768):
        model = math_problem(spec.problem, True)
        edges = [0, 1, len(model.frequency_edges)//2, len(model.frequency_edges)]
        groups = [_kernel_group(store.staging_context(), model, parity,
            {'frequency_step': producer.frequency_step}, start, stop)
            for start, stop in zip(edges, edges[1:])]
        actual = {}
        for i, panel in enumerate(_kernel_panels(spec, parity)):
            refs = [{'anchor_start': group['anchor_start'], 'anchor_stop': group['anchor_stop'],
                     'artifact': group['panels'][i]['artifact']} for group in groups]
            for wire in _kernel_reduce(store.staging_context(), model, parity, panel, refs):
                task, staged = _parse_staged(wire)
                for record in store.read_chunk(store.publish_chunk(task, staged)).records:
                    actual[record.row, record.column] = [record.lower, record.upper]
        expected = {pair: arb(0) for pair in actual}
        for anchor in range(len(model.frequency_edges)):
            contribution = analytic.frequency_step(model, anchor)
            for pair in expected:
                expected[pair] += contribution(*pair)
        for pair, value in expected.items():
            lo, hi = actual[pair]
            assert arb(fmpq(lo.numerator, lo.denominator)) <= value.lower()
            assert arb(fmpq(hi.numerator, hi.denominator)) >= value.upper()


def _manifest(spec, tiles):
    return scientific_manifest(spec, True, tiles)


@pytest.fixture(scope='module')
def publications(bound):
    with collection(bound, 'publication') as (lock, store, spec):
        tiles = []
        for family, name in FAMILIES.items():
            for parity in (0, 1):
                for task in _tiles(spec, QuantityKey(name, parity)):
                    records = (IntervalRecord(m, n, (0,), Fraction(m-n+1, 2)+Fraction(1, 1 << 300),
                                              Fraction(m-n+1, 2)+Fraction(1, 1 << 300))
                               for m, n in _coordinates(task, True))
                    staged = stage_publication(store.staging_context(), task, records)
                    ref = publish_publication(store, task, staged)
                    tiles.append({'family':family,'parity':parity,'task':task.to_dict(),
                                  'artifact':{'path':ref.path,'sha256':ref.sha256,'size':ref.size}})
        manifest = _manifest(spec, tiles)
        path = lock.root/'source-manifest.json'
        path.write_bytes(canonical_bytes(manifest))
        write_source_execution(path, spec, {'kind':'DECLARED_CONTROL'})
        yield path, spec, manifest


def test_publication_is_outward_on_actual_256_bit_grid_and_covers_both_parities(publications):
    path, spec, _ = publications
    reader = SourceReader(path, spec, control=True)
    count = 0
    for row, records in reader.tiles():
        for record in records:
            exact = Fraction(record.row-record.column+1, 2)+Fraction(1, 1 << 300)
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


@pytest.mark.parametrize('tile_modes', [1, 2, 4, 8])
def test_full_source_rejects_geometry_that_cannot_fit_complete_inventory(bound, tile_modes):
    folder, problem, _, _ = bound
    destination = folder/('invalid-full-tile-'+str(tile_modes))
    with pytest.raises(ContractError):
        prepare_source_inputs(problem, destination, origin_git_commit='b19905565ace1f4a1b9ea1387ce123377c65a0e0',
                              origin_git_dirty=True, control=False, tile_modes=tile_modes)
    assert not destination.exists()


@pytest.mark.parametrize('precision', [4608, 6144])
@pytest.mark.parametrize('kind', ['zero', 'positive', 'negative', 'microscopic', 'ball'])
def test_fixed_point_cache_matches_exact_endpoint_conversion(precision, kind):
    from scripts.whole_source.artifacts import _round
    from scripts.whole_source.gram import _record
    from scripts.whole_source.pipeline import _fixed_bounds
    with ctx.workprec(precision):
        values = {'zero':arb(0), 'positive':arb(fmpq(1, 3)), 'negative':arb(fmpq(-7, 5)),
                  'microscopic':-(arb(2)**-4000), 'ball':arb(arb(-1), arb(2)**-600)}
        value = values[kind]
        reference = _record(0, 0, value)
        expected = _round(reference.lower, reference.upper, 512)
        assert _fixed_bounds(value, 512) == expected
        lo, hi = expected
        assert Fraction(lo, 1 << 512) <= reference.lower <= reference.upper <= Fraction(hi, 1 << 512)


def test_full_profile_worker_budget_changes_only_operational_identity(bound, monkeypatch):
    from scripts.whole_source import resources
    folder, problem, _, _ = bound
    original = resources.auto_plan
    selected = []
    for cpus in (3, 6):
        def capped(template, *, parallel, memory_mib=None, helper_root=ROOT, cpus=cpus):
            # Declared metadata-only detector; never used to admit live work.
            detected = {'cpu_detection_complete':True, 'memory_detection_complete':True,
                        'affinity_cpus':cpus, 'logical_cpus':cpus, 'effective_cpu_budget':cpus,
                        'quota_cpu_limit':None, 'available_memory_bytes':16*1024**3,
                        'platform':'win32'}
            return original(template, parallel=parallel, cpus=cpus,
                            memory_mib=8192, detected=detected, helper_root=helper_root)
        monkeypatch.setattr(resources, 'auto_plan', capped)
        inputs = prepare_source_inputs(problem, folder/('full-science-'+str(cpus)),
            origin_git_commit='0'*40, origin_git_dirty=True, control=False, tile_modes=32,
            memory_mib=8192)
        _, _, roles = _bind(inputs['problem'], inputs['execution'], ROOT)
        spec, plan = roles['producer']
        assert (plan.workers, plan.threads) == (cpus, 1)
        selected.append(spec)
    assert [spec.bounds.max_temporary_bytes//(1024*1024) for spec in selected] == [131, 261]
    assert selected[0].collection_id != selected[1].collection_id
    assert selected[0].scientific_dict() == selected[1].scientific_dict()
    assert selected[0].scientific_id == selected[1].scientific_id


@pytest.mark.parametrize('change', ['missing', 'source-hash', 'collection-hash', 'scientific-id'])
def test_source_reader_rejects_missing_or_changed_execution_binding(publications, tmp_path, change):
    path, spec, _ = publications
    candidate = tmp_path/path.name
    candidate.write_bytes(path.read_bytes())
    if change != 'missing':
        document = json.loads((path.parent/'source-execution.json').read_bytes())
        if change == 'source-hash':
            document['source_manifest']['sha256'] = '0'*64
        elif change == 'collection-hash':
            document['collection_id'] = '0'*64
        else:
            document['scientific_id'] = '0'*64
        (tmp_path/'source-execution.json').write_bytes(canonical_bytes(document))
    with pytest.raises((ContractError, OSError)):
        SourceReader(candidate, spec, control=True)


def test_declared_control_cannot_supply_owned_source_acceptance(publications):
    from scripts.whole_source.pipeline import verify_source_execution
    path, spec, _ = publications
    with pytest.raises(ContractError, match='owned publication'):
        verify_source_execution(SourceReader(path, spec, control=True))
