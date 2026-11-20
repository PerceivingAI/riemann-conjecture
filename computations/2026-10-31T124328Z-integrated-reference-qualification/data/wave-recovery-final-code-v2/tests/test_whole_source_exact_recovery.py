"""Recovery preserves complete signed, ragged mathematical wave outputs."""
from dataclasses import asdict
from types import SimpleNamespace
import uuid

import pytest

from scripts.whole_source import exact_tasks as graph
from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes
from scripts.whole_source.execution import _write
from tests.test_whole_source_artifacts import code_refs, problem
from tests.test_whole_source_exact_tasks import finite_graph


class Journal:
    def __init__(self, waves):
        self.waves = dict(waves)
        self.adoptions = []
        self.commits = []

    def get(self, key):
        return ({'group': {'operation': key}, 'value': {'outputs': self.waves[key]}}
                if key in self.waves else None)

    def adopt(self, key, *, attempt_id=None):
        self.adoptions.append((key, attempt_id))
        return self.get(key)['group']

    def commit(self, key, group, value):
        self.waves[key] = value['outputs']
        self.commits.append(key)


def owner(root, problem=None):
    return SimpleNamespace(root=root, spec=SimpleNamespace(problem=problem), _immutable=lambda family, raw:
                           _write(root/(family+'-'+uuid.uuid4().hex), raw))


def execution(root, problem, records):
    calls = []
    current = []
    def run_stage(operation, tasks):
        calls.append(operation)
        current[:] = records[operation]
        assert {task['task_id'] for task in tasks} == {task['task_id'] for task, _ in current}
    owned = SimpleNamespace(attempt_id='control', spec=SimpleNamespace(problem=problem),
        run_stage=run_stage, read_results=lambda operation:
        iter({'task_id': task['task_id'], 'result': result} for task, result in current))
    return owned, calls


def test_complete_retry_preserves_ragged_signed_reports_and_product_bytes(finite_graph):
    root, problem, _, _, descriptor, waves, expected, operands = finite_graph
    before = {name: (root/ref['path']).read_bytes() for outputs in waves.values()
              for name, ref in outputs.items()}
    journal = Journal(waves)
    for retry in range(3):
        reports, refs, products, groups = graph.run_waves(owner(root,problem),
            SimpleNamespace(attempt_id='control'), descriptor, operands, journal=journal)
        assert canonical_bytes(reports) == canonical_bytes(expected)
        assert refs == [waves['reduce'][f'reduce/{p}'] for p in (0, 1)]
        assert len(products) == 2
        for p, ref in enumerate(products):
            import json
            inventory = json.loads((root/ref['path']).read_bytes())
            assert inventory['context'] == descriptor['blocks'][p]['context']
            assert inventory['panels'] == {name.split('/', 1)[1]: value
                for name, value in waves['first'].items() if name.startswith(str(p)+'/')}
        assert journal.commits == []
    assert len(journal.adoptions) == 12
    assert before == {name: (root/ref['path']).read_bytes() for outputs in waves.values()
                      for name, ref in outputs.items()}


@pytest.mark.parametrize('operation', ['global', 'first', 'second', 'reduce'])
def test_changed_committed_bytes_never_trigger_recomputation(finite_graph, monkeypatch, operation):
    root, problem, _, _, descriptor, waves, _, operands = finite_graph
    ref = next(iter(waves[operation].values()))
    original = graph.read_group
    def read(record, context, **authority):
        from scripts.whole_source.artifacts import _raw
        selected_root, outputs = original(record, context, **authority)
        for value in outputs.values():
            _raw(selected_root, ArtifactRef(**value), 8*1024*1024)
        return selected_root, outputs
    monkeypatch.setattr(graph, 'read_group', read)
    (root/ref['path']).write_bytes(b'corrupt committed payload')
    with pytest.raises((ContractError, ValueError)):
        graph.run_waves(owner(root,problem), SimpleNamespace(attempt_id='control'),
                        descriptor, operands, journal=Journal(waves))


@pytest.mark.parametrize('cut', ['global', 'first', 'second', 'reduce'])
def test_only_missing_complete_waves_execute(finite_graph, monkeypatch, cut):
    root, problem, _, _, descriptor, waves, expected, operands = finite_graph
    operations = ['global', 'first', 'second', 'reduce']
    records = {operation: list(graph.group_tasks({'operation': operation},
        graph._context(descriptor, operands, operation))) for operation in operations}
    selected = {operation: waves[operation] for operation in operations[:operations.index(cut)]}
    journal = Journal(selected)
    owned, calls = execution(root, problem, records)
    def seal(lock, execution, operation, context, outputs):
        waves[operation] = outputs
        return {'operation': operation}
    monkeypatch.setattr(graph, 'seal_group', seal)
    reports, _, _, _ = graph.run_waves(owner(root,problem), owned, descriptor, operands, journal=journal)
    assert calls == operations[operations.index(cut):]
    assert journal.commits == calls
    assert canonical_bytes(reports) == canonical_bytes(expected)


def test_uncommitted_first_wave_keeps_all_original_staging(finite_graph, monkeypatch):
    root, problem, _, _, descriptor, waves, _, operands = finite_graph
    records = {operation: list(graph.group_tasks({'operation': operation},
        graph._context(descriptor, operands, operation))) for operation in waves}
    originals = [ArtifactRef(**value) for task, result in records['first']
                 for value in result['panels'].values()]
    before = {ref.path: (root/ref.path).read_bytes() for ref in originals}
    journal = Journal({'global': waves['global']})
    def interrupted(key, group, value):
        raise RuntimeError('interrupted before checkpoint head')
    journal.commit = interrupted
    monkeypatch.setattr(graph, 'seal_group', lambda *args: {'operation': 'first'})
    owned, calls = execution(root, problem, records)
    with pytest.raises(RuntimeError, match='checkpoint head'):
        graph.run_waves(owner(root), owned, descriptor, operands, journal=journal)
    assert calls == ['first']
    assert before == {ref.path: (root/ref.path).read_bytes() for ref in originals}


@pytest.mark.parametrize('change', ['configuration', 'output', 'python'])
def test_exact_journal_rejects_changed_context(tmp_path, problem, code_refs, change):
    from scripts.whole_source.artifacts import CollectionLock
    from scripts.whole_source.recovery import RecoveryJournal, operation_context
    from tests.test_whole_source_artifacts import collection
    output = tmp_path/'exact'
    output.mkdir()
    spec = collection(problem, code_refs)
    context = operation_context('exact', output, {'layout': {'panel_size': 2}})
    with CollectionLock.acquire(output/'collection', spec) as lock:
        RecoveryJournal(lock, context)
    changed = operation_context('exact', tmp_path/'other' if change == 'output' else output,
                                {'layout': {'panel_size': 3 if change == 'configuration' else 2}})
    if change == 'python':
        changed['python'] = 'foreign interpreter'
    with CollectionLock.acquire(output/'collection', spec, resume=True) as lock:
        with pytest.raises(ContractError):
            RecoveryJournal(lock, changed, resume=True)


def test_exact_terminal_intent_recovers_interrupted_publication(tmp_path, problem, code_refs, monkeypatch):
    from scripts.whole_source.artifacts import CollectionLock
    from scripts.whole_source import recovery
    from tests.test_whole_source_artifacts import collection
    output = tmp_path/'exact'
    output.mkdir()
    spec = collection(problem, code_refs)
    context = recovery.operation_context('exact', output, {'layout': {'panel_size': 2}})
    payload = {'format': 'manufactured-exact-terminal', 'proof_scope': 'CONTROL_ONLY',
               'assessment': {'status': 'WIDTH_GOAL_FAILED'}, 'production_admission': False}
    path = output/'report.json'
    publish = recovery.finish_publication
    def interrupted(*args, **kwargs):
        raise RuntimeError('publication interrupted')
    with CollectionLock.acquire(output/'collection', spec) as lock:
        journal = recovery.RecoveryJournal(lock, context)
        monkeypatch.setattr(recovery, 'finish_publication', interrupted)
        with pytest.raises(RuntimeError, match='publication interrupted'):
            journal.publish(path, payload)
        assert not path.exists()
    monkeypatch.setattr(recovery, 'finish_publication', publish)
    for retry in range(2):
        with CollectionLock.acquire(output/'collection', spec, resume=True) as lock:
            journal = recovery.RecoveryJournal(lock, context, resume=True)
            assert journal.terminal(path) == payload
            journal.publish(path, payload)
        assert path.read_bytes() == canonical_bytes(payload)
    path.write_bytes(b'foreign report')
    with CollectionLock.acquire(output/'collection', spec, resume=True) as lock:
        with pytest.raises(ContractError):
            recovery.RecoveryJournal(lock, context, resume=True).terminal(path)
    assert path.read_bytes() == b'foreign report'


@pytest.mark.parametrize('change', [None, 'goal', 'parity', 'row-margin'])
def test_final_stage_uses_complete_actual_reduction_reports(finite_graph, monkeypatch, change):
    from fractions import Fraction
    import sys
    monkeypatch.delitem(sys.modules, 'numpy', raising=False)
    monkeypatch.delitem(sys.modules, 'scipy', raising=False)
    from scripts.whole_source import exact as e, execution as runtime
    from scripts.whole_source.artifacts import _raw
    root, problem, reader, _, descriptor, waves, reports, operands = finite_graph
    problem.m, problem.b_K, problem.delta = Fraction(1), Fraction(0), Fraction(0)
    refs = [waves['reduce'][f'reduce/{p}'] for p in (0, 1)]
    task = graph._request('assess', operands, {'reduce': {'operation': 'reduce'}}, blocks=refs)
    staging = SimpleNamespace(root=root, attempt_id='control', _check=lambda: None,
                              spec=SimpleNamespace(problem=problem))
    worker = SimpleNamespace(role='exact', backend='python-flint-exact', scope=e.SCOPE)
    monkeypatch.setattr(runtime, '_WORKER', [worker, staging])
    monkeypatch.setattr(e, '_validate_operands', lambda bound, data, code_root: reader)
    def raw(directory, ref, cap):
        if ref == ArtifactRef(**operands):
            return canonical_bytes(descriptor)
        return _raw(directory, ref, cap)
    monkeypatch.setattr(e, '_raw', raw)
    if change is not None:
        import json
        report = json.loads((root/refs[0]['path']).read_bytes())
        if change == 'goal':
            report['goal'] = '1/2'
        elif change == 'parity':
            report['parity'] = 1
        else:
            report['row_margins'] = ['1']*report['dimension']
        # The manufactured group resolver is deliberately unchanged; the final
        # consumer still has to reject its own mathematical report contract.
        updated = _write(root/('changed-'+change), canonical_bytes(report))
        waves['reduce']['reduce/0'] = asdict(updated)
        refs[0] = asdict(updated)
        task = graph._request('assess', operands, {'reduce': {'operation': 'reduce'}}, blocks=refs)
        monkeypatch.setattr(graph, '_wave', lambda *args, **kwargs: (root, waves['reduce']))
        with pytest.raises(ContractError):
            e.evaluate_exact(task, staging)
    else:
        result = e.evaluate_exact(task, staging)
        fields = ('width', 'goal', 'margin', 'tau', 'direction_upper', 'direction_mass')
        blocks = [{**{key: Fraction(report[key]) for key in fields},
                   'modular_nonsingular': report['modular']['nonsingular'],
                   'direction_index': report['direction_index']} for report in reports]
        expected = e.assess(blocks, eta=problem.eta, m=problem.m, b_K=problem.b_K,
                            delta=problem.delta, control=True)
        assert result['assessment']['status'] == expected['status']
        assert result['assessment']['positive_paid_lower'] == expected['positive_paid_lower']
        assert result['assessment']['proof_scope'] == 'CONTROL_ONLY'
        assert result['assessment']['smooth_test_consequence_conditional'] is False


def test_exact_context_never_recreates_a_missing_head(tmp_path, problem, code_refs):
    from scripts.whole_source.artifacts import CollectionLock
    from scripts.whole_source.recovery import RecoveryJournal, operation_context
    from tests.test_whole_source_artifacts import collection
    output = tmp_path/'exact'
    output.mkdir()
    spec = collection(problem, code_refs)
    context = operation_context('exact', output, {'panel_size': 2})
    with CollectionLock.acquire(output/'collection', spec) as lock:
        journal = RecoveryJournal(lock, context)
        (lock.root/'recovery/head.json').unlink()
        with pytest.raises(ContractError):
            journal.terminal(output/'report.json')
    with CollectionLock.acquire(output/'collection', spec, resume=True) as lock:
        with pytest.raises(ContractError):
            RecoveryJournal(lock, context, resume=True)
        assert not (lock.root/'recovery/head.json').exists()


@pytest.mark.parametrize('change', [False, True])
def test_exact_interrupted_initial_context_accepts_only_the_bound_empty_head(
        tmp_path, problem, code_refs, monkeypatch, change):
    from scripts.whole_source.artifacts import CollectionLock
    from scripts.whole_source.recovery import RecoveryJournal, operation_context
    from tests.test_whole_source_artifacts import collection
    output = tmp_path/'exact'
    output.mkdir()
    spec = collection(problem, code_refs)
    context = operation_context('exact', output, {'panel_size': 2})
    publish = RecoveryJournal._replace
    def interrupted(self, relative, raw):
        if relative == 'recovery/context.json':
            raise RuntimeError('initial context interrupted')
        return publish(self, relative, raw)
    with CollectionLock.acquire(output/'collection', spec) as lock:
        monkeypatch.setattr(RecoveryJournal, '_replace', interrupted)
        with pytest.raises(RuntimeError, match='initial context interrupted'):
            RecoveryJournal(lock, context)
        assert (lock.root/'recovery/head.json').exists()
        assert not (lock.root/'recovery/context.json').exists()
    monkeypatch.setattr(RecoveryJournal, '_replace', publish)
    if change:
        context = operation_context('exact', output, {'panel_size': 3})
    with CollectionLock.acquire(output/'collection', spec, resume=True) as lock:
        if change:
            with pytest.raises(ContractError):
                RecoveryJournal(lock, context, resume=True)
        else:
            journal = RecoveryJournal(lock, context, resume=True)
            assert journal.head['count'] == 0
            assert journal.head['tip'] is None
