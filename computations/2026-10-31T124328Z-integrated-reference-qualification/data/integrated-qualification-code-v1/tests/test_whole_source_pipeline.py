"""Completed column partitions, exact publications and complete source-domain reading."""
from contextlib import contextmanager
from dataclasses import replace
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import subprocess
import sys

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

    assert selected[0].collection_id != selected[1].collection_id
    assert selected[0].scientific_dict() == selected[1].scientific_dict()
    assert selected[0].scientific_id == selected[1].scientific_id


@pytest.fixture
def source_factory(bound, monkeypatch):
    from scripts.whole_source import resources
    folder, problem, _, _ = bound
    original = resources.auto_plan
    with tempfile.TemporaryDirectory(prefix='producer-budget-', dir=folder) as directory:
        def prepare(name, *, tile_modes=32, control=False, memory_mib=8192):
            def allocate(template, *, parallel, memory_mib=None, helper_root=ROOT):
                detected = {'cpu_detection_complete':True, 'memory_detection_complete':True,
                    'affinity_cpus':6, 'logical_cpus':6, 'effective_cpu_budget':6,
                    'quota_cpu_limit':None, 'available_memory_bytes':16*1024**3,
                    'platform':'win32'}
                return original(template, parallel=parallel, memory_mib=memory_mib,
                                detected=detected, helper_root=helper_root)
            monkeypatch.setattr(resources, 'auto_plan', allocate)
            return prepare_source_inputs(problem, Path(directory)/name,
                origin_git_commit='0'*40, origin_git_dirty=True, control=control,
                tile_modes=tile_modes, memory_mib=memory_mib)
        yield prepare


@pytest.mark.parametrize('control,tile_modes', [(False, 32), (False, 16), (True, 2)])
def test_factory_producer_budget_admits_every_runtime_tile(source_factory, monkeypatch,
                                                          control, tile_modes):
    from scripts.whole_source import execution
    paths = source_factory('all-tiles', control=control, tile_modes=tile_modes)
    problem, _, roles = _bind(paths['problem'], paths['execution'], ROOT)
    spec, plan = roles['producer']
    model = math_problem(problem, control)
    # Real guard with declared plan state; this metadata control is not an owned run.
    monkeypatch.setattr(execution, '_WORKER', (plan,))
    with ctx.workprec(plan.precision_bits):
        for parity in (0, 1):
            for task in _tiles(spec, QuantityKey('A_model', parity)):
                account = producer.tile_account(model, task.rows, task.columns)
                assert account['private_bytes'] <= plan.worker_private_mib*1024**2
                assert account['native_bytes'] <= plan.native_workspace_mib*1024**2


@pytest.mark.parametrize('field,value,message', [
    ('worker_private_mib', 1, 'private allowance'),
    ('native_workspace_mib', 1, 'native allowance'),
    ('precision_bits', 4096, 'precision'),
])
def test_undersized_producer_plan_rejects_before_output(source_factory, field, value, message):
    from scripts.whole_source.execution import ExecutionPlan
    from scripts.whole_source.pipeline import run_source
    paths = source_factory('undersized')
    config = json.loads(paths['execution'].read_bytes())
    plan = ExecutionPlan.from_dict(config['roles']['producer']['execution'])
    # A valid manual envelope, not a tampered automatic-policy receipt.
    plan = replace(plan, resource_policy=None, **{field:value})
    config['roles']['producer']['execution'] = plan.to_dict()
    paths['execution'].write_bytes(canonical_bytes(config))
    destination = paths['execution'].parent/'must-not-start'
    with pytest.raises(ContractError, match=message):
        run_source(paths['problem'], paths['execution'], destination)
    assert not destination.exists()


def test_producer_budget_rounds_up_and_accepts_extra_headroom(source_factory):
    from scripts.whole_source.execution import MIB
    from scripts.whole_source.pipeline import _producer_requirements
    paths = source_factory('ceiling')
    problem, config, roles = _bind(paths['problem'], paths['execution'], ROOT)
    spec, plan = roles['producer']
    required = _producer_requirements(spec, False)
    # This declared full layout crosses a whole-MiB boundary: truncation must reject.
    below = required['private_bytes']//MIB
    assert below*MIB < required['private_bytes']
    config['roles']['producer']['execution'] = replace(plan, worker_private_mib=below,
                                                       resource_policy=None).to_dict()
    paths['execution'].write_bytes(canonical_bytes(config))
    with pytest.raises(ContractError, match='private allowance'):
        _bind(paths['problem'], paths['execution'], ROOT)
    config['roles']['producer']['execution'] = replace(plan,
        worker_private_mib=plan.worker_private_mib+1, resource_policy=None).to_dict()
    paths['execution'].write_bytes(canonical_bytes(config))
    _, _, rebound = _bind(paths['problem'], paths['execution'], ROOT)
    assert rebound['producer'][1].worker_private_mib*MIB > required['private_bytes']


def test_derived_private_cost_reduces_workers_and_refuses_infeasible_capacity(source_factory):
    from scripts.whole_source.execution import MIB
    paths = source_factory('constrained', memory_mib=1500)
    _, _, roles = _bind(paths['problem'], paths['execution'], ROOT)
    plan = roles['producer'][1]
    assert 0 < plan.workers < plan.cpus
    assert plan.owned_required_bytes <= 1500*MIB
    # The old fixed128MiB private account admitted this cap; the actual tile does not.
    with pytest.raises(ContractError, match='aggregate bounded task working set'):
        source_factory('insufficient', memory_mib=800)
    assert not (paths['problem'].parent.parent/'insufficient/execution.json').exists()

@pytest.mark.parametrize('control,tile_modes', [(False, 32), (False, 16), (True, 2)])
def test_factory_analytic_budget_admits_every_runtime_tile(source_factory, monkeypatch,
                                                         control, tile_modes):
    from scripts.whole_source import execution
    paths = source_factory('analytic-tiles', control=control, tile_modes=tile_modes)
    problem, _, roles = _bind(paths['problem'], paths['execution'], ROOT)
    spec, plan = roles['analytic']
    model = math_problem(problem, control)
    # Declared plan state exercises accounting only, not owned numerical execution.
    monkeypatch.setattr(execution, '_WORKER', (plan,))
    with ctx.workprec(plan.precision_bits):
        for parity in (0, 1):
            for task in _tiles(spec, QuantityKey('A_model', parity)):
                account = analytic.tile_account(model, task.rows, task.columns)
                assert account['private_bytes'] <= plan.worker_private_mib*1024**2
                assert account['native_bytes'] <= plan.native_workspace_mib*1024**2


@pytest.mark.parametrize('field,value,message', [
    ('worker_private_mib', 1, 'private allowance'),
    ('native_workspace_mib', 1, 'native allowance'),
    ('precision_bits', 4096, 'precision'),
])
def test_invalid_analytic_plan_rejects_before_audit_output(source_factory, field, value, message):
    from scripts.whole_source.execution import ExecutionPlan
    from scripts.whole_source.pipeline import run_audit
    paths = source_factory('invalid-analytic')
    config = json.loads(paths['execution'].read_bytes())
    plan = ExecutionPlan.from_dict(config['roles']['analytic']['execution'])
    config['roles']['analytic']['execution'] = replace(
        plan, resource_policy=None, **{field:value}).to_dict()
    paths['execution'].write_bytes(canonical_bytes(config))
    destination = paths['execution'].parent/'must-not-audit'
    with pytest.raises(ContractError, match=message):
        run_audit(paths['problem'], paths['execution'].parent/'absent-source.json',
                  paths['execution'], destination)
    assert not destination.exists()


@pytest.mark.parametrize('account,field', [('private_bytes', 'worker_private_mib'),
                                         ('native_bytes', 'native_workspace_mib')])
def test_analytic_requirement_ceiling_and_extra_headroom(source_factory, account, field):
    from scripts.whole_source.execution import MIB
    from scripts.whole_source.pipeline import _analytic_requirements
    from scripts.whole_source.artifacts import _catalog_limit
    paths = source_factory('analytic-ceiling')
    _, config, roles = _bind(paths['problem'], paths['execution'], ROOT)
    spec, plan = roles['analytic']
    required = _analytic_requirements(spec, False)[account]
    if account == 'private_bytes':
        required += _catalog_limit(spec)
    below = required//MIB
    assert below*MIB < required
    config['roles']['analytic']['execution'] = replace(
        plan, resource_policy=None, **{field:below}).to_dict()
    paths['execution'].write_bytes(canonical_bytes(config))
    with pytest.raises(ContractError, match='allowance'):
        _bind(paths['problem'], paths['execution'], ROOT)
    for allowance in ((required+MIB-1)//MIB, getattr(plan, field)+1):
        config['roles']['analytic']['execution'] = replace(
            plan, resource_policy=None, **{field:allowance}).to_dict()
        paths['execution'].write_bytes(canonical_bytes(config))
        _, _, rebound = _bind(paths['problem'], paths['execution'], ROOT)
        assert getattr(rebound['analytic'][1], field)*MIB >= required


def test_analytic_private_requirement_changes_affordable_concurrency(source_factory):
    from scripts.whole_source.execution import MIB
    from scripts.whole_source.resources import auto_plan
    paths = source_factory('analytic-capacity', memory_mib=1500)
    _, _, roles = _bind(paths['problem'], paths['execution'], ROOT)
    plan = roles['analytic'][1]
    detection = plan.resource_policy['detection']
    # Metadata-only comparison against the former underpriced analytical template.
    old = auto_plan(replace(plan, resource_policy=None, cpus=1, workers=1, threads=1,
                           worker_private_mib=128, native_workspace_mib=128,
                           codec_mib=256, queue_mib=8),
                    parallel=True, memory_mib=1500, detected=detection)
    assert plan.workers < old.workers
    assert plan.owned_required_bytes <= 1500*MIB
    with pytest.raises(ContractError, match='aggregate bounded task working set'):
        auto_plan(replace(plan, resource_policy=None, cpus=1, workers=1, threads=1,
                          native_workspace_mib=128, codec_mib=256, queue_mib=8),
                  parallel=True, memory_mib=800, detected=detection)


def test_full_source_preparation_does_not_import_numerical_backends(source_factory):
    paths = source_factory('metadata-parent')
    destination = paths['problem'].parent/'isolated'
    program = """
import importlib.abc, sys
sys.path.insert(0, sys.argv[1])
class MetadataOnly(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] not in sys.stdlib_module_names and not fullname.startswith('scripts'):
            raise AssertionError('Numerical or external import: '+fullname)
sys.meta_path.insert(0, MetadataOnly())
from scripts.whole_source import resources
from scripts.whole_source.contract import bind_problem
from scripts.whole_source.pipeline import prepare_source_inputs, _bind
original = resources.auto_plan
def allocate(template, *, parallel, memory_mib=None, helper_root=None):
    detected = {'platform':'win32','affinity_cpus':2,'logical_cpus':2,
        'effective_cpu_budget':2,'quota_cpu_limit':None,'available_memory_bytes':16*1024**3,
        'cpu_detection_complete':True,'memory_detection_complete':True}
    return original(template, parallel=parallel, memory_mib=4096, detected=detected)
resources.auto_plan = allocate
paths = prepare_source_inputs(bind_problem('retained-t081'), __import__('pathlib').Path(sys.argv[2]),
    origin_git_commit='0'*40, origin_git_dirty=True, tile_modes=32)
_bind(paths['problem'], paths['execution'], __import__('pathlib').Path(sys.argv[1]))
assert not {'flint','numpy','scipy'} & set(sys.modules)
"""
    result = subprocess.run([sys.executable, '-I', '-B', '-c', program, str(ROOT), str(destination)],
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    config = json.loads((destination/'execution.json').read_bytes())
    assert config['roles']['producer']['execution']['worker_private_mib'] > 128


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
