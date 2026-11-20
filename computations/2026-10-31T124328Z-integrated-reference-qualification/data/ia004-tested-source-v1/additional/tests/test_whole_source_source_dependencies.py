"""METADATA_ONLY source dependency tests, not native/scientific acceptance.

These fixtures retain real locks, zero-polynomial interval artifacts, captured
runtime bytes and hash-bound owned stage evidence. No worker or native numerical
operation runs. The graph models group -> reduction -> head -> final, with F
columns feeding head and final. Only the structural provenance is under test.
"""
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

import pytest

from scripts.whole_source.artifacts import (
    CollectionLock, ChunkStore, ContributionTask, IntervalRecord, _coordinates,
    publish_publication, stage_publication,
)
from scripts.whole_source.contract import (
    ArtifactRef, ContractError, QuantityKey, ROOT, bind_problem, canonical_bytes,
)
from scripts.whole_source.pipeline import (
    COMPLETE, FAMILIES, _bind, _column_task, _kernel_panels, _tiles, _wire,
    math_problem, prepare_source_inputs,
)
from scripts.whole_source.source_dependencies import SourceDependencies, check_history


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))
    return path


def _reference(path, root):
    return asdict(ArtifactRef(path.relative_to(root).as_posix(), _digest(path), path.stat().st_size))


def _change(path, update):
    value = json.loads(path.read_bytes())
    update(value)
    _write_json(path, value)


@pytest.fixture(scope='module')
def source_contract():
    # Preparation binds repository/runtime inputs but does not execute them.
    cache = ROOT/'.pytest_cache'
    cache.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='source-dependencies-', dir=cache) as folder:
        inputs = prepare_source_inputs(bind_problem('retained-t081'), Path(folder)/'inputs',
            origin_git_commit='b19905565ace1f4a1b9ea1387ce123377c65a0e0',
            origin_git_dirty=True, control=True, tile_modes=32)
        _, _, roles = _bind(inputs['problem'], inputs['execution'], ROOT)
        yield roles['producer']


def _request(identity, operation, **fields):
    request = dict(task_id=identity, operation=operation, parity=0, control=True)
    request.update(fields)
    return request


def _zero_records(spec, task):
    return (IntervalRecord(m, n, (0,), Fraction(0), Fraction(0))
            for m, n in _coordinates(task, spec.quantity(task.quantity).symmetric_upper))


def _stage(lock, store, spec, plan, name, jobs):
    """Retain a complete METADATA_ONLY stage, then bind before publishing."""
    attempt = lock.root/'attempts'/store.attempt_id
    runtime = attempt/'runtime'
    for relative in ('scripts/whole_source/execution.py', plan.task_program.path):
        target = runtime/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/relative, target)
    program = runtime/'scripts/whole_source/execution.py'
    tasks = attempt/(name+'-tasks.jsonl')
    tasks.write_bytes(b''.join(canonical_bytes(request) for request, _, _ in jobs))
    results = attempt/(name+'-results')
    rows, payloads = [], []
    for request, data, _ in jobs:
        payload = dict(execution_id=plan.execution_id, attempt_id=store.attempt_id,
            collection_id=spec.collection_id, problem_id=plan.problem_sha256,
            scope=plan.scope, generation=store.generation,
            task_id=request['task_id'], result=data)
        path = _write_json(results/(request['task_id']+'.json'), payload)
        rows.append(_reference(path, results))
        payloads.append(payload)
    inventory = results/'completed.jsonl'
    inventory.write_bytes(b''.join(canonical_bytes(row) for row in rows))
    _write_json(results/'complete.json', dict(execution_id=plan.execution_id,
        task_count=len(jobs), inventory_sha256=_digest(inventory)))
    descriptor = _write_json(attempt/(name+'-stage.json'), dict(
        fixture_scope='METADATA_ONLY', plan=plan.to_dict(), collection=spec.to_dict(),
        generation=store.generation, attempt_id=store.attempt_id,
        task_file=str(tasks), task_sha256=_digest(tasks), task_count=len(jobs),
        result_dir=str(results)))
    config = _write_json(attempt/'execution-budget.json', {'fixture_scope': 'METADATA_ONLY'})
    profile = _write_json(attempt/(name+'-profile.json'), dict(
        exit_code=0, error=None, program_sha256=_digest(program), fixture_scope='METADATA_ONLY'))
    logs = {}
    for stream in ('stdout', 'stderr'):
        path = attempt/(name+'-'+stream+'.txt')
        path.write_bytes(b'METADATA_ONLY: no worker executed\n')
        logs[stream] = _reference(path, attempt)
    receipt = _write_json(attempt/name/'receipt.json', dict(
        format='t081-owned-stage-receipt-v1', stage=name, fixture_scope='METADATA_ONLY',
        argv=['metadata-only', '--stage', str(descriptor), '--stage-sha256', _digest(descriptor),
              '--program', str(program), '--config', str(config), '--profile', str(profile)],
        exit_code=0, error=None, worker_cleanup_verified=True,
        last_metrics={'active_process_count': 0}, program_sha256=_digest(program),
        config_sha256=_digest(config), logs=logs))
    dependencies = SourceDependencies(lock.root, spec, plan)
    published = []
    for (_, _, outputs), payload in zip(jobs, payloads):
        dependencies.bind(lock, name, payload)
        refs = []
        for kind, staged in outputs:
            if kind == 'chunk':
                ref = store.publish_chunk(staged.task, staged)
            elif kind == 'publication':
                ref = publish_publication(store, staged.task, staged)
            else:
                ref = lock._immutable('seals', staged.read_bytes())
                staged.unlink()
            refs.append(asdict(ref))
        published.append(refs)
    return published, receipt


def _data(chunks=(), publications=(), group=None):
    return dict(chunks=list(chunks), publications=list(publications), kernel_group=group,
                scope='SOURCE_EXPRESSIONS_ONLY', statistics={'fixture_scope': 'METADATA_ONLY'})


@pytest.fixture
def graph(tmp_path, source_contract):
    spec, plan = source_contract
    root = tmp_path/'collection'
    with CollectionLock.acquire(root, spec) as lock:
        (root/'attempts/old').mkdir()
        lock.register_attempt('old')
        store = ChunkStore(lock, spec, attempt_id='old')
        old_generation = store.generation
        stop = len(math_problem(spec.problem, True).frequency_edges)
        panels, page_paths = [], []
        for index, domain in enumerate(_kernel_panels(spec, 0)):
            page = _write_json(root/'attempts/old/staging'/('page-'+str(index)), dict(
                format='whole-source-frequency-group-v1', scope='PARTIAL_FREQUENCY_SUM',
                collection_id=spec.collection_id, role=spec.role, grid_bits=spec.grid_bits,
                domain=domain.to_dict(), anchor_start=0, anchor_stop=stop,
                records=[[m, n, '0x0', '0x0'] for m, n in _coordinates(domain, True)]))
            panels.append({'domain': domain.to_dict(), 'artifact': _reference(page, root)})
            page_paths.append(('kernel_page', page))
        jobs = [(_request('group', 'kernel-group', anchor_start=0, anchor_stop=stop),
            _data(group=dict(anchor_start=0, anchor_stop=stop, panels=panels)), page_paths)]
        final_domain = next(_tiles(spec, QuantityKey('A_model', 0)))
        modes = sorted(set(final_domain.rows) | set(final_domain.columns))
        # The odd column is deliberately not a dependency of the selected root.
        for n in [*modes, 1]:
            domain = _column_task(spec, 'F_column', n)
            staged = store.stage_chunk(domain, _zero_records(spec, domain))
            jobs.append((_request('column-'+str(n), 'column', n=n, parity=n % 2),
                         _data(chunks=[_wire(staged)]), [('chunk', staged)]))
        leaves, leaf_receipt = _stage(lock, store, spec, plan, 'leaves', jobs)
        columns = dict(zip([*modes, 1], (refs[0] for refs in leaves[1:])))
        jobs = []
        for panel, ref in zip(panels, leaves[0]):
            domain = next(d for d in _kernel_panels(spec, 0) if d.to_dict() == panel['domain'])
            outputs = []
            for tile in _tiles(spec, QuantityKey('kernel_complete', 0)):
                if tile.rows == domain.rows:
                    outputs.append(store.stage_chunk(tile, _zero_records(spec, tile)))
            jobs.append((_request('reduce-'+str(len(jobs)), 'kernel-reduce', domain=domain.to_dict(),
                groups=[dict(anchor_start=0, anchor_stop=stop, artifact=ref)]),
                _data(chunks=[_wire(staged) for staged in outputs]),
                [('chunk', staged) for staged in outputs]))
        reduced, _ = _stage(lock, store, spec, plan, 'reduce', jobs)
        kernels = [ref for refs in reduced for ref in refs]
    with CollectionLock.acquire(root, spec, resume=True) as lock:
        (root/'attempts/new').mkdir()
        lock.register_attempt('new')
        store = ChunkStore(lock, spec, attempt_id='new')
        new_generation = store.generation
        jobs = []
        for n in modes:
            outputs = []
            for name in ('head_column', 'head_image'):
                task = _column_task(spec, name, n)
                outputs.append(store.stage_chunk(task, _zero_records(spec, task)))
            jobs.append((_request('head-'+str(n), 'head', n=n, F=columns[n], kernel=kernels),
                _data(chunks=[_wire(staged) for staged in outputs]),
                [('chunk', staged) for staged in outputs]))
        heads, _ = _stage(lock, store, spec, plan, 'heads', jobs)
        outputs = []
        for name in FAMILIES.values():
            task = ContributionTask(QuantityKey(name, 0), final_domain.rows, final_domain.columns, COMPLETE)
            outputs.append(stage_publication(store.staging_context(), task, _zero_records(spec, task)))
        request = _request('final', 'final', domain=final_domain.to_dict(), columns=[
            dict(n=n, F=columns[n], C=refs[0], Y=refs[1]) for n, refs in zip(modes, heads)])
        published, final_receipt = _stage(lock, store, spec, plan, 'final', [(request,
            _data(publications=[_wire(staged) for staged in outputs]),
            [('publication', staged) for staged in outputs])])
        tile = {'task': outputs[0].task.to_dict(), 'artifact': published[0][0]}
    with CollectionLock.acquire(root, spec, resume=True) as lock:
        (root/'attempts/unrelated').mkdir()
        lock.register_attempt('unrelated')
        store = ChunkStore(lock, spec, attempt_id='unrelated')
        task = _column_task(spec, 'F_column', 3)
        staged = store.stage_chunk(task, _zero_records(spec, task))
        _, failed = _stage(lock, store, spec, plan, 'failed', [(
            _request('unrelated-column', 'column', n=3, parity=1),
            _data(chunks=[_wire(staged)]), [('chunk', staged)])])
    _change(failed, lambda value: value.update(exit_code=9,
        error='metadata-only interrupted attempt', last_metrics={'active_process_count': 3}))
    return dict(root=root, spec=spec, plan=plan, tile=tile, input=columns[modes[0]],
                leaf_receipt=leaf_receipt, final_receipt=final_receipt, failed=failed,
                old_generation=old_generation, new_generation=new_generation)


def _select(graph):
    # Always reverify from disk, including after mutations.
    return SourceDependencies(graph['root'], graph['spec'], graph['plan']).select([graph['tile']])


def test_dependencies_cross_attempts_and_retain_cleaned_failure(graph):
    selected = _select(graph)
    assert graph['old_generation'] != graph['new_generation']
    receipt_paths = {ref['path'] for ref in selected['receipts']}
    assert receipt_paths == {'attempts/old/leaves/receipt.json', 'attempts/old/reduce/receipt.json',
                             'attempts/new/heads/receipt.json', 'attempts/new/final/receipt.json'}
    assert 'dependencies/'+graph['input']['sha256']+'.json' in {
        ref['path'] for ref in selected['dependencies']}
    assert [ref['path'] for ref in selected['history']] == [
        graph['failed'].relative_to(graph['root']).as_posix()]


@pytest.mark.parametrize('missing', ['binding', 'input'])
def test_missing_transitive_producer_or_artifact_rejects(graph, missing):
    _select(graph)
    relative = ('dependencies/'+graph['input']['sha256']+'.json'
                if missing == 'binding' else graph['input']['path'])
    (graph['root']/relative).unlink()
    with pytest.raises((ContractError, OSError)):
        _select(graph)


@pytest.mark.parametrize('mutation', ['failed', 'cleanup', 'unselected-result', 'runtime', 'log'])
def test_entire_selected_stage_must_remain_verified(graph, mutation):
    _select(graph)
    receipt = graph['leaf_receipt']
    attempt = receipt.parent.parent
    if mutation == 'failed':
        _change(receipt, lambda value: value.update(exit_code=9, error='failed'))
    elif mutation == 'cleanup':
        _change(receipt, lambda value: value.update(worker_cleanup_verified=False))
    elif mutation == 'unselected-result':
        _change(attempt/'leaves-results/column-1.json', lambda value: value.update(task_id='foreign'))
    elif mutation == 'runtime':
        (attempt/'runtime'/graph['plan'].task_program.path).write_bytes(b'# altered runtime\n')
    else:
        (attempt/'leaves-stdout.txt').write_bytes(b'changed stream\n')
    with pytest.raises((ContractError, OSError)):
        _select(graph)


@pytest.mark.parametrize('mutation', ['domain', 'input', 'ref'])
def test_binding_cannot_change_domain_inputs_or_producer_reference(graph, mutation):
    _select(graph)
    path = graph['root']/('dependencies/'+graph['tile']['artifact']['sha256']+'.json')
    def alter(value):
        if mutation == 'domain':
            value['output']['domain']['quantity']['parity'] = 1
        elif mutation == 'input':
            value['inputs'].pop()
        else:
            value['result']['sha256'] = '0'*64
    _change(path, alter)
    with pytest.raises(ContractError):
        _select(graph)


def test_uncontained_noncontributing_history_rejects_selection_and_history(graph):
    _select(graph)
    _change(graph['failed'], lambda value: value.update(worker_cleanup_verified=False))
    with pytest.raises(ContractError, match='uncontained source execution history'):
        check_history(graph['root'])
    with pytest.raises(ContractError, match='uncontained source execution history'):
        _select(graph)
