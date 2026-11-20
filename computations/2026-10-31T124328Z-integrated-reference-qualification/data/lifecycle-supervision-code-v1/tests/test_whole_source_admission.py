"""Operational admission on disposable metadata; never scientific approval."""
from contextlib import nullcontext
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import pytest

from scripts.whole_source import admission as a, storage, retention, execution, resources
from scripts.whole_source.contract import ROOT, ContractError, bind_problem, canonical_bytes
from tests.test_whole_source_resources import detected, template


@pytest.fixture(autouse=True)
def clear_context(monkeypatch):
    monkeypatch.delenv(a._ENV, raising=False)
    monkeypatch.delenv(storage.ENV, raising=False)


@pytest.fixture
def owned():
    with TemporaryDirectory(prefix='phase-admission-', dir=ROOT/'.pytest_cache') as path:
        yield Path(path)


def test_live_memory_admits_only_future_caller_growth():
    account = {'required_bytes': 512*a.MIB}
    snapshot = detected(available_memory_bytes=256*a.MIB)
    result = a.admit_caller(account, snapshot, existing_bytes=400*a.MIB)
    assert result['future_caller_bytes'] == 112*a.MIB
    with pytest.raises(ContractError, match='caller/preparation'):
        a.admit_caller(account, snapshot, existing_bytes=200*a.MIB)


@pytest.mark.parametrize('field', ['memory_detection_complete', 'cpu_detection_complete'])
def test_unknown_discovery_refuses(field):
    with pytest.raises(ContractError, match='incomplete'):
        a.admit_caller({'required_bytes': a.MIB}, detected(**{field: False}), existing_bytes=0)


def test_limiting_commit_source_cannot_hide_behind_host_ram():
    snapshot = detected(memory_sources=[{'source': 'limiting commit', 'available_bytes': 100*a.MIB}])
    with pytest.raises(ContractError, match='limiting commit'):
        a.admit_caller({'required_bytes': 256*a.MIB}, snapshot, existing_bytes=128*a.MIB)


def test_caller_and_supervisor_are_not_charged_twice(monkeypatch):
    monkeypatch.setenv(a._ENV, json.dumps([{'pid': 91, 'required_bytes': 1000}]))
    monkeypatch.setattr(a, 'current_commit', lambda *args, **kw: 600)
    assert a.caller_future(helper_root=ROOT, external_bytes=300) == 400
    assert a.caller_future(helper_root=ROOT, external_bytes=500) == 500


def test_replay_waiting_ancestor_is_separate_from_active_child(monkeypatch):
    monkeypatch.setenv(a._ENV, json.dumps([
        {'pid': 91, 'required_bytes': 700}, {'pid': 92, 'required_bytes': 1000}]))
    monkeypatch.setattr(a, 'current_commit', lambda *args, **kw: {91: 600, 92: 800}[kw['pid']])
    assert a.caller_future(helper_root=ROOT, external_bytes=300) == 400


def test_invalid_or_duplicate_caller_authority_refuses(monkeypatch):
    monkeypatch.setenv(a._ENV, json.dumps([{'pid': 91, 'required_bytes': 1}]*2))
    with pytest.raises(ContractError, match='duplicate'):
        a.caller_future(helper_root=ROOT)


def test_worker_selection_charges_caller_before_selecting_workers(monkeypatch):
    evidence = detected(available_memory_bytes=2048*a.MIB)
    plain = resources.auto_plan(template(), parallel=True, detected=evidence)
    monkeypatch.setenv(a._ENV, json.dumps([{'pid': 91, 'required_bytes': 1400*a.MIB}]))
    monkeypatch.setattr(a, 'current_commit', lambda *args, **kw: 100*a.MIB)
    charged = resources.auto_plan(template(), parallel=True, detected=evidence)
    assert charged.workers < plain.workers
    assert charged.resource_policy['detection']['phase_caller_future_bytes'] == 1300*a.MIB
    resources.validate_policy(charged)
    with pytest.raises(ContractError, match='future owned'):
        resources.current_allowance(charged, detected(available_memory_bytes=1400*a.MIB))


def test_worker_job_remaining_does_not_charge_its_external_caller(monkeypatch):
    plan = resources.auto_plan(template(), parallel=True, detected=detected())
    monkeypatch.setenv(a._ENV, json.dumps([{'pid': 91, 'required_bytes': 1000*a.MIB}]))
    monkeypatch.setattr(a, 'current_commit', lambda *args, **kw: 100*a.MIB)
    own = {'memory_sources': [{'source': 'windows.job_memory_remaining',
        'limit_bytes': plan.memory_mib*a.MIB, 'available_bytes': 32*a.MIB}]}
    resources.admit_worker_growth(plan, own, 16*a.MIB)
    with pytest.raises(ContractError, match='future task'):
        resources.admit_worker_growth(plan, {'available_memory_bytes': 512*a.MIB}, 16*a.MIB)


def test_complete_metadata_account_has_no_numerical_import():
    script = ('import sys; from scripts.whole_source.contract import bind_problem; '
              'from scripts.whole_source.admission import topology; '
              'r=topology(bind_problem("retained-t081")); '
              'assert r["geometry"]["N"] == 826; '
              'assert not any(n in sys.modules for n in ("flint","numpy","scipy")); '
              'assert r["remaining_exact_basis"] == "LOCAL_CEILING_NOT_ACTUAL_OPERANDS"')
    result = subprocess.run([sys.executable, '-B', '-c', script], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr


def test_retry_allowance_counts_original_intents_even_without_directories():
    journal = SimpleNamespace(nodes={str(i): (None, {'kind': 'intent', 'payload': {'phase': 'audit'}})
                                    for i in range(2)})
    with pytest.raises(ContractError, match='retry allowance'):
        a.admit_attempt(journal, 'audit', {'attempts_per_phase': 2})
    a.admit_attempt(journal, 'audit', {'attempts_per_phase': 2}, reuse=True)


def test_phase_budget_admits_only_next_growth_and_retains_external_history(owned, monkeypatch):
    from scripts.whole_source import supervision
    monkeypatch.setattr(supervision, 'require_current', lambda: {'observation_bytes': 16*a.MIB})
    problem = bind_problem('retained-t081')
    run = owned/'operation'
    run.mkdir()
    (run/'retained').write_bytes(b'old evidence')
    monkeypatch.setattr(storage.shutil, 'disk_usage', lambda path: SimpleNamespace(free=1 << 50))
    first, forecast = a.operation_budget(problem, run, ROOT, phase='review', external=owned/'review')
    with first.scope():
        first.write(owned/'review'/'review.json', b'{}')
    second, _ = a.operation_budget(problem, run, ROOT, phase='source')
    roots = dict(second.roots)
    assert roots[owned/'review'] == 2
    report = second.admit()
    future = sum(row['future_growth_bytes'] for row in report['volumes'])
    assert future == forecast['phase_growth_bytes']['source']+32*a.MIB
    assert roots[run] < forecast['logical_allowance_bytes']


def test_external_attempts_are_bounded_without_deleting_prior_outputs(owned, monkeypatch):
    from scripts.whole_source import supervision
    monkeypatch.setattr(supervision, 'require_current', lambda: {'observation_bytes': 16*a.MIB})
    problem = bind_problem('retained-t081')
    run = owned/'operation'
    run.mkdir()
    monkeypatch.setattr(storage.shutil, 'disk_usage', lambda path: SimpleNamespace(free=1 << 50))
    for index in range(2):
        output = owned/f'review-{index}'
        budget, _ = a.operation_budget(problem, run, ROOT, phase='review', external=output)
        with budget.scope():
            budget.write(output/'retained', b'old')
    with pytest.raises(ContractError, match='external retry'):
        a.operation_budget(problem, run, ROOT, phase='review', external=owned/'review-2')
    assert (owned/'review-0'/'retained').read_bytes() == b'old'
    assert not (owned/'review-2').exists()


def test_generic_write_and_live_snapshot_cannot_bypass_allowance(owned, monkeypatch):
    from scripts.run_observability import _atomic_write_json
    monkeypatch.setattr(storage.shutil, 'disk_usage', lambda path: SimpleNamespace(free=1 << 50))
    budget = storage.StorageBudget({owned: 65536}, operation_id='test',
        policy_path=owned/'policy.json', code_root=ROOT)
    with budget.scope():
        budget.write(owned/'old', b'preserve')
        remaining = 65536-budget.admit()['volumes'][0]['existing_logical_bytes']
        execution._write(owned/'fill', b'x'*remaining)
        for call in (lambda: execution._write(owned/'next', b'x'),
                     lambda: _atomic_write_json(owned/'live.json', {'state': 'running'})):
            with pytest.raises(ContractError, match='allowance exhausted'):
                call()
        assert (owned/'old').read_bytes() == b'preserve'
        assert not (owned/'live.json').exists()


@pytest.mark.skipif(os.name != 'nt', reason='Caller commitment qualification uses Windows counters')
def test_real_owned_stage_uses_shared_storage_policy(owned, monkeypatch):
    from tests.test_whole_source_execution import case, task
    from scripts.whole_source.artifacts import CollectionLock
    from dataclasses import replace
    problem = bind_problem('retained-t081')
    captured, spec, plan = case(owned, problem)
    parts = {'runtime_bytes': 128*a.MIB,
             'decoder_bytes': a.decoded_bound(spec.bounds.max_decoded_bytes),
             'capture_bytes': 3*sum(ref.size for ref, raw in spec._snapshots)}
    caller = {'required_bytes': sum(parts.values()), 'components': parts,
              'basis': 'bounded-future-growth-v1'}
    budget = storage.StorageBudget({owned: 256*a.MIB}, operation_id='owned-control',
        policy_path=owned/'storage-policy.json', code_root=ROOT)
    with a.caller_scope(caller, helper_root=captured), budget.scope():
        cpus = min(2, resources._cpu_limit(execution.neutral_helpers(captured)[0].detect_resources()))
        plan = resources.auto_plan(plan, parallel=True, cpus=cpus, helper_root=captured)
        spec = replace(spec, native_threads=plan.threads)
        plan = replace(plan, collection_sha256=spec.collection_id)
        with CollectionLock.acquire(owned/'collection', spec) as lock:
            with execution.WorkloadExecution(lock, spec, plan, code_root=captured) as work:
                work.run_stage('bounded-control', [task(0, mode='polynomial', x=2),
                                                   task(1, mode='polynomial', x=3)])
                rows = list(work.read_results('bounded-control'))
                assert {row['result']['polynomial'] for row in rows} == {'0x9', '0x16'}
                assert work.receipts[-1]['worker_cleanup_verified'] is True
                work.run_stage('bounded-chunks', [task(index, mode='stage', contribution=index, row=problem.N)
                                                  for index in (0, 1)])
                from scripts.whole_source.artifacts import _decode_chunk
                for row in work.read_results('bounded-chunks'):
                    result = row['result']
                    chunk = _decode_chunk(spec, Path(result['path']).read_bytes())
                    for record in chunk.records:
                        index = record.contribution[0]
                        expected = (-1)**index*(record.row+1)*(record.column+2)*(index+1)
                        assert record.lower < expected < record.upper
                assert work.receipts[-1]['worker_cleanup_verified'] is True


def test_replay_stream_overflow_is_failure_and_keeps_bounded_logs(owned, monkeypatch):
    # A short real child, not a scientific replay. It responds to the same
    # cooperative cancellation byte so no forced process kill is part of this test.
    monkeypatch.setattr(a, 'waiting_caller', lambda **kw: nullcontext())
    code = 'import sys; sys.stdout.buffer.write(b"x"*(5*1024*1024)); sys.stdout.flush(); sys.stdin.buffer.read(1)'
    with pytest.raises(ContractError, match='stream allowance'):
        retention._replay_process([sys.executable, '-B', '-c', code], owned, owned, ROOT)
    assert (owned/'stdout.txt').stat().st_size <= 4*a.MIB


@pytest.mark.parametrize('method', ['open', 'write_text', 'write_bytes'])
def test_inherited_path_publication_cannot_bypass_budget(owned, monkeypatch, method):
    import runpy
    script = owned/'scalar-fixture.py'
    actions = {
        'open': "with output.open('x',encoding='utf-8',newline='\\n') as handle: handle.write(data)",
        'write_text': "output.write_text(data,encoding='utf-8')",
        'write_bytes': "output.write_bytes(data.encode('utf-8'))",
    }
    raw = ("from pathlib import Path\nimport sys,json\n"
           "output=Path(sys.argv[1]); data=json.dumps({'sum':sum(range(10))})+'\\n'\n"+
           actions[method]+"\n").encode()
    script.write_bytes(raw)
    monkeypatch.setattr(sys, 'argv', [str(script), str(owned/'result.json')])
    budget = storage.StorageBudget({owned: 65536}, operation_id='scalar-control',
        policy_path=owned/'policy.json', code_root=ROOT)
    with budget.scope():
        budget.write(owned/'fill', b'x'*(65536-budget.admit()['volumes'][0]['existing_logical_bytes']))
        with pytest.raises(ContractError, match='allowance exhausted'):
            runpy.run_path(str(script), run_name='__main__',
                           init_globals={'__builtins__': storage.scalar_builtins()})
    assert script.read_bytes() == raw
    assert not (owned/'result.json').exists() or (owned/'result.json').stat().st_size == 0


@pytest.mark.parametrize('decoder', ['execution', 'artifacts', 'contract', 'policy'])
def test_decode_refuses_exhausted_envelope_before_object_creation(monkeypatch, decoder):
    from scripts.whole_source import artifacts, contract
    raw = b'{"value":1}\n'
    original = json.loads
    def load(value, *args, **kwargs):
        if value is raw:
            pytest.fail('JSON objects were allocated before admission')
        return original(value, *args, **kwargs)
    monkeypatch.setenv(a._ENV, json.dumps([{'pid': os.getpid(), 'required_bytes': 1001}]))
    monkeypatch.setattr(a, 'current_commit', lambda *args, **kw: 1000)
    monkeypatch.setattr(json, 'loads', load)
    token = a._PROBE.set((ROOT, SimpleNamespace(), None))
    try:
        readers = {'execution': execution._json, 'artifacts': lambda value: artifacts._json(value, a.MIB),
                   'contract': contract._load, 'policy': storage._decode}
        with pytest.raises(ContractError, match='decoder exceeds admitted caller'):
            readers[decoder](raw)
    finally:
        a._PROBE.reset(token)
