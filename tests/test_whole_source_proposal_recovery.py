"""Proposal consumers retain paid arithmetic and original checkpoint authority."""
from contextlib import ExitStack
from types import SimpleNamespace

import pytest
from flint import arb, ctx, fmpq

from scripts.whole_source import proposal
from scripts.whole_source.contract import ContractError, canonical_bytes
from tests.test_whole_source_proposal_tasks import base, context, harness, matrices, owner_fixture
from tests.test_whole_source_artifacts import collection, code_refs, problem
from scripts.whole_source.artifacts import CollectionLock
from scripts.whole_source.recovery import RecoveryJournal, operation_context


def checkpoint(staged, dependency):
    rows = staged.groups[dependency['record']['fixture']]['tasks']
    diagnostics = [{'task_id':task['task_id'],'diagnostics':result['diagnostics']}
                   for task,result in reversed(rows)]
    return {'status':'NONPROOF_ONLY','scope':proposal.SCOPE,'attempt_id':staged.attempt_id,
            'dependency':dependency,'diagnostics':diagnostics[0]['diagnostics'] if len(rows) == 1 else {},
            'tasks':diagnostics,'owned_receipts':[],'production_admission':False}


@pytest.mark.parametrize('parity',[0,1])
def test_paid_factor_checkpoint_survives_multiple_retry_adoptions(tmp_path,monkeypatch,parity):
    c = context(n=5,b=2,parity=parity)
    staged,wave,_ = harness(monkeypatch,tmp_path/'tasks',c,matrices(5))
    with ctx.workprec(proposal.BITS):
        dependency = wave('factor-diagonal',{'factor':[]},0)
    report = checkpoint(staged,dependency)
    before = canonical_bytes(report)
    monkeypatch.setattr(proposal,'same_group',lambda left,right,**authority:left == right)
    monkeypatch.setattr(proposal,'local_group',lambda root,record:record)
    adoptions = []
    store = proposal._dependency_store([dependency],c,[('factor-diagonal',0)],binding=base(c))
    with ctx.workprec(proposal.BITS):
        paid = store.native('L/0/0')
        for i in range(2):
            for j in range(2):
                expected = (fmpq(i+2,1 << i) if i == j else
                            fmpq((-1)**(i+j)*(i+j+1),1 << (i+4)) if i > j else fmpq(0))
                assert paid[i,j].contains(arb(expected))
                assert (paid[i,j]-arb(expected)).abs_upper() < arb(2)**-1000
    journal = SimpleNamespace(get=lambda key:{'group':dependency['record'],'value':report},
        adopt=lambda key:adoptions.append(key) or dependency['record'])
    owner = proposal._ProposalWaves(tmp_path,None,None,code_root=tmp_path,
                                   recovery_context={},resume=True)
    owner.journal,owner.execution = journal,None
    monkeypatch.setattr(proposal,'WorkloadExecution',lambda *args,**kwargs:pytest.fail('reused wave launched a worker'))
    tasks = proposal._make_tasks(base(c),'factor-diagonal',{'factor':[]},0)
    for _ in range(3):
        reused = owner.wave(tasks,'factor-diagonal',0)
        assert canonical_bytes(reused['_producer_report']) == before
        assert reused['attempt_id'] == staged.attempt_id
    assert adoptions == ['factor-diagonal_0']*3
    assert canonical_bytes(report) == before


@pytest.mark.parametrize('change',['raw','predecessor','missing-task'])
def test_corrupt_committed_dependency_never_falls_back_to_execution(tmp_path,monkeypatch,change):
    c = context(n=5,b=2)
    staged,wave,_ = harness(monkeypatch,tmp_path/'tasks',c,matrices(5))
    with ctx.workprec(proposal.BITS):
        diagonal = wave('factor-diagonal',{'factor':[]},0)
        below = wave('factor-below',{'factor':[diagonal]},0)
    report = checkpoint(staged,below)
    tasks = proposal._make_tasks(base(c),'factor-below',{'factor':[diagonal]},0)
    group = staged.groups[below['record']['fixture']]
    if change == 'raw':
        ref = next(iter(group['outputs'].values()))
        (staged.root/ref['path']).write_bytes(b'changed')
    elif change == 'missing-task':
        group['tasks'].pop()
    else:
        tasks = proposal._make_tasks(base(c),'factor-below',
            {'factor':[{**diagonal,'record':{'fixture':'foreign'}}]},0)
    monkeypatch.setattr(proposal,'same_group',lambda left,right,**authority:left == right)
    owner = proposal._ProposalWaves(tmp_path,None,None,code_root=tmp_path,
                                   recovery_context={},resume=True)
    owner.execution = None
    owner.journal = SimpleNamespace(get=lambda key:{'group':below['record'],'value':report},
        adopt=lambda key:pytest.fail('corrupt checkpoint adopted'))
    monkeypatch.setattr(proposal,'WorkloadExecution',lambda *args,**kwargs:pytest.fail('corruption recomputed'))
    with pytest.raises((ContractError,ValueError)):
        owner.wave(tasks,'factor-below',0)


@pytest.mark.parametrize('interrupt',['group','journal'])
def test_uncommitted_wave_preserves_every_original_staging_payload(tmp_path,monkeypatch,interrupt):
    lock,owned,tasks,published,sealed = owner_fixture(tmp_path,monkeypatch)
    original = {path:path.read_bytes() for path in (lock.root/'attempts'/owned.attempt_id/'staging').iterdir()}
    def stop(*args):
        raise OSError('checkpoint interruption')
    if interrupt == 'group':
        monkeypatch.setattr(proposal,'seal_group',stop)
    journal = SimpleNamespace(commit=stop)
    with pytest.raises(OSError,match='checkpoint interruption'):
        proposal._run_wave(lock,owned,tasks,'whiten-forward',journal=journal)
    assert original
    assert all(path.read_bytes() == raw for path,raw in original.items())
    assert len(sealed) == (interrupt == 'journal')


def test_staging_release_is_after_complete_journal_commit(tmp_path,monkeypatch):
    lock,owned,tasks,published,sealed = owner_fixture(tmp_path,monkeypatch)
    original = list((lock.root/'attempts'/owned.attempt_id/'staging').iterdir())
    commits = []
    def commit(key,record,value):
        assert sealed and all(path.exists() for path in original)
        commits.append((key,record,value))
    report = proposal._run_wave(lock,owned,tasks,'whiten-forward',
                                journal=SimpleNamespace(commit=commit))
    assert commits[0][2] == report
    assert not any(path.exists() for path in original)
    assert all((lock.root/ref.path).exists() for ref in published)


def test_orphan_group_is_not_a_checkpoint(tmp_path,monkeypatch):
    owner = proposal._ProposalWaves(tmp_path,None,None,code_root=tmp_path,
                                   recovery_context={},resume=True)
    owner.stack = ExitStack()
    owner.lock = object()
    owner.journal = SimpleNamespace(get=lambda key:None)
    owner.execution = object()
    calls = []
    monkeypatch.setattr(proposal,'_run_wave',lambda *args,**kwargs:calls.append(args) or {'fresh':True})
    assert owner.wave([{'irrelevant':'orphan group is never consulted'}],'float-optimize') == {'fresh':True}
    assert len(calls) == 1


@pytest.mark.parametrize('change',['configuration','output'])
def test_proposal_journal_rejects_changed_operation_identity(tmp_path,problem,code_refs,change):
    output = tmp_path/'proposal'
    output.mkdir()
    root = output/'recovery-terminal'
    spec = collection(problem,code_refs)
    context = operation_context('proposal',output,{'format':'manufactured-recovery-control','panel_size':2})
    with CollectionLock.acquire(root,spec) as lock:
        RecoveryJournal(lock,context)
    changed = operation_context('proposal',tmp_path/'relocated' if change == 'output' else output,
        {'format':'manufactured-recovery-control','panel_size':3 if change == 'configuration' else 2})
    with CollectionLock.acquire(root,spec,resume=True) as lock:
        with pytest.raises(ContractError):
            RecoveryJournal(lock,changed,resume=True)


def test_proposal_terminal_publication_is_identical_and_conflicts_remain_untouched(tmp_path,problem,code_refs):
    output = tmp_path/'proposal'
    output.mkdir()
    root = output/'recovery-terminal'
    spec = collection(problem,code_refs)
    context = operation_context('proposal',output,{'format':'manufactured-recovery-control'})
    payload = {'format':'manufactured-terminal-control','scope':'NONPROOF_ONLY','theta':'3/8'}
    path = output/'proposal.json'
    with CollectionLock.acquire(root,spec) as lock:
        journal = RecoveryJournal(lock,context)
        journal.publish(path,payload)
    original = path.read_bytes()
    with CollectionLock.acquire(root,spec,resume=True) as lock:
        journal = RecoveryJournal(lock,context,resume=True)
        journal.publish(path,payload)
        assert journal.terminal(path) == payload
        assert path.read_bytes() == original == canonical_bytes(payload)
        path.write_bytes(b'conflicting terminal bytes')
        with pytest.raises(ContractError):
            journal.publish(path,payload)
        assert path.read_bytes() == b'conflicting terminal bytes'


def test_proposal_terminal_intent_recovers_absent_publication_without_math(tmp_path,problem,code_refs):
    output = tmp_path/'proposal'
    output.mkdir()
    root = output/'recovery-terminal'
    spec = collection(problem,code_refs)
    context = operation_context('proposal',output,{'format':'manufactured-recovery-control'})
    payload = {'format':'manufactured-terminal-control','scope':'NONPROOF_ONLY'}
    path = output/'proposal.json'
    with CollectionLock.acquire(root,spec) as lock:
        RecoveryJournal(lock,context).publish(path,payload)
    path.unlink()
    with CollectionLock.acquire(root,spec,resume=True) as lock:
        journal = RecoveryJournal(lock,context,resume=True)
        assert journal.terminal(path) == payload
        journal.publish(path,payload)
    assert path.read_bytes() == canonical_bytes(payload)


def test_terminal_record_without_atomic_head_is_not_recovered(tmp_path,problem,code_refs,monkeypatch):
    output = tmp_path/'proposal'
    output.mkdir()
    root = output/'recovery-terminal'
    spec = collection(problem,code_refs)
    context = operation_context('proposal',output,{'format':'manufactured-recovery-control'})
    payload = {'format':'manufactured-terminal-control','scope':'NONPROOF_ONLY'}
    path = output/'proposal.json'
    with CollectionLock.acquire(root,spec) as lock:
        journal = RecoveryJournal(lock,context)
        replace = journal._replace
        def interrupted(relative,raw):
            if relative == 'recovery/head.json':
                raise OSError('before atomic head')
            return replace(relative,raw)
        monkeypatch.setattr(journal,'_replace',interrupted)
        with pytest.raises(OSError,match='before atomic head'):
            journal.publish(path,payload)
        assert not path.exists()
    with CollectionLock.acquire(root,spec,resume=True) as lock:
        journal = RecoveryJournal(lock,context,resume=True)
        assert journal.terminal(path) is None
        journal.publish(path,payload)
    assert path.read_bytes() == canonical_bytes(payload)
