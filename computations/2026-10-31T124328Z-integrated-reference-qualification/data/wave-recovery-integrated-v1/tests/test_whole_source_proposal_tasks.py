"""Dependency geometry and persisted arithmetic of native proposal callbacks."""
from dataclasses import asdict
from fractions import Fraction
import hashlib
from types import SimpleNamespace

import pytest
from flint import arb, arb_mat, ctx, fmpq, fmpq_mat

from scripts.whole_source import execution, proposal
from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes


def context(n=7, b=2, parity=0):
    return {'proposal_id':'a'*64,'problem_id':'b'*64,'source_sha256':'c'*64,
            'dimension':n,'panel_size':b,'precision_bits':proposal.BITS,
            'grid_bits':proposal.BITS,'transform_bits':80,'parity':parity}


def base(c):
    return {'context':c,'source':{'fixture':'manufactured finite operands'},'source_snapshot':'fixture'}


def panel(matrix, i, j, c):
    n,b = c['dimension'],c['panel_size']
    return arb_mat([[matrix[r,k] for k in range(j,min(j+b,n))]
                    for r in range(i,min(i+b,n))])


def matrices(n):
    lower = fmpq_mat(n,n)
    for i in range(n):
        lower[i,i] = fmpq(i+2,1 << i)
        for j in range(i):
            lower[i,j] = fmpq((-1)**(i+j)*(i+j+1),1 << (i+4))
    image = fmpq_mat([[fmpq((-1)**(i+j)*(i+j+2)+(9 if i == j else 0),64)
                       for j in range(n)] for i in range(n)])
    return {'A_model':lower*lower.transpose(),'weighted_head':image,
            'weighted_complete_tail':image*fmpq(3,8)}


def staging(root):
    root.mkdir()
    (root/'.volume.lock').touch()
    (root/'attempts'/('d'*32)/'staging').mkdir(parents=True)
    return SimpleNamespace(root=root,attempt_id='d'*32,_check=lambda:None,
        spec=SimpleNamespace(problem=object(),bounds=SimpleNamespace(
            max_total_bytes=512*proposal.MIB,max_temporary_bytes=512*proposal.MIB)))


def harness(monkeypatch, root, c, operands):
    """Supply the owned context, leaving real panel codecs and FLINT arithmetic."""
    staged = staging(root)
    source_checks = []
    groups = {}
    staged.groups = groups
    reader = SimpleNamespace(ref=SimpleNamespace(sha256=c['source_sha256']),
                             document={'geometry':{'N':2*c['dimension']}})
    def source(*args):
        source_checks.append(args)
        return reader
    monkeypatch.setattr(proposal,'_reader',source)
    monkeypatch.setattr(proposal,'problem_id',lambda problem:c['problem_id'])
    monkeypatch.setattr(proposal,'SourcePanels',lambda reader,context:SimpleNamespace(
        matrix=lambda family,i,j:panel(operands[family],i,j,context)))
    monkeypatch.setattr(proposal,'sys',SimpleNamespace(modules={'flint':True}))
    plan = SimpleNamespace(role='proposal',scope=proposal.SCOPE,
                           worker_private_mib=128,backend='python-flint')
    monkeypatch.setattr(execution,'_WORKER',(plan,staged))
    def read(record, expected):
        value = groups[record['fixture']]
        if value['context'] != expected:
            raise ContractError('changed dependency group context')
        return root,value['outputs']
    monkeypatch.setattr(proposal,'read_group',read)
    monkeypatch.setattr(proposal,'group_tasks',lambda record,expected:iter(groups[record['fixture']]['tasks']))
    def wave(operation, dependencies, column=None):
        tasks = proposal._make_tasks(base(c),operation,dependencies,column)
        outputs,rows = {},[]
        # Deliberately reverse independent task completions.
        for task in reversed(tasks):
            result = proposal.evaluate_proposal(task,staged)
            proposal._validate_result(result,task,root,staged.attempt_id)
            rows.append((task,result))
            assert not (outputs.keys() & result['panels'].keys())
            outputs.update(result['panels'])
        assert set(outputs) == proposal._wave_names(c,operation,column)
        token = str(len(groups))
        groups[token] = {'context':proposal._wave_context(c,operation,column),'outputs':outputs,'tasks':rows}
        return {'operation':operation,'column':column,'record':{'fixture':token}}
    return staged,wave,source_checks


def quantize(store, c):
    n,b = c['dimension'],c['panel_size']
    for i in range(0,n,b):
        for j in range(0,n,b):
            value = store.native(f'W/{i}/{j}')
            integers = []
            for r in range(value.nrows()):
                for k in range(value.ncols()):
                    midpoint = Fraction(str(value[r,k].mid().fmpq()))*(1 << 80)
                    integer = (2*midpoint.numerator+midpoint.denominator)//(2*midpoint.denominator)
                    integers.append(proposal.encode_integer(integer,8192))
            store.put(f'Z/{i}/{j}','integer',integers)


@pytest.mark.parametrize('parity',[0,1])
@pytest.mark.parametrize('width',[2,3])
def test_signed_ragged_callbacks_match_complete_literal_persisted_endpoints(tmp_path,monkeypatch,parity,width):
    c = context(b=width,parity=parity)
    operands = matrices(c['dimension'])
    literal_root = tmp_path/'literal'
    literal_root.mkdir()
    literal = proposal.PanelStore(literal_root,c)
    staged,wave,checks = harness(monkeypatch,tmp_path/'tasks',c,operands)
    factors = []
    with ctx.workprec(proposal.BITS):
        proposal.blocked_cholesky(lambda i,j:panel(operands['A_model'],i,j,c),literal)
        for family,name in proposal._FAMILIES.items():
            proposal.whiten_tiles(lambda i,j:panel(operands[name],i,j,c),literal,family)
        for j in proposal._grid(c):
            factors.append(wave('factor-diagonal',{'factor':list(factors)},j))
            if j != proposal._grid(c)[-1]:
                factors.append(wave('factor-below',{'factor':list(factors)},j))
        forward = wave('whiten-forward',{'factor':factors})
        whitened = wave('whiten-transpose',{'factor':factors,'forward':[forward]})
        actual_factor = proposal._dependency_store(factors,c,proposal._factor_waves(c),binding=base(c))
        actual_white = proposal._dependency_store([forward],c,[('whiten-forward',None)],binding=base(c))
        actual_white.refs.update(proposal._dependency_store(
            [whitened],c,[('whiten-transpose',None)],binding=base(c)).refs)
        for actual in (actual_factor,actual_white):
            for name in actual.refs:
                assert actual.read(name,'interval') == literal.read(name,'interval')
        vectors = proposal.PanelStore(staged.root,c,staging=staged)
        for i in proposal._grid(c):
            for j in proposal._grid(c):
                rows,columns = proposal._shape(c,i,j)
                vectors.put(f'V/{i}/{j}','binary64',[
                    float(((-1)**(i+r+j+k))*(i+r+1)/(j+k+2)).hex()
                    for r in range(rows) for k in range(columns)])
        floating_task = proposal._make_tasks(base(c),'float-optimize',{'whitened':[whitened]})[0]
        staged.groups['floating'] = {
            'context':proposal._wave_context(c,'float-optimize'),'outputs':vectors.created,
            'tasks':[(floating_task,{'scope':proposal.SCOPE,'diagnostics':{},'panels':vectors.created})]}
        floating = {'operation':'float-optimize','column':None,'record':{'fixture':'floating'}}
        proposal.triangular_solve(literal,lambda i,j:vectors.vectors(f'V/{i}/{j}'),literal,'W',transpose=True)
        quantize(literal,c)
        solved = wave('backsolve-quantize',{'factor':factors,'floating':[floating]})
        actual = proposal._dependency_store([solved],c,[('backsolve-quantize',None)],binding=base(c))
        for name in actual.refs:
            kind = 'integer' if name.startswith('Z/') else 'interval'
            assert actual.read(name,kind) == literal.read(name,kind)
    q = len(proposal._grid(c))
    assert len(checks) == q*(q+1)//2+7*q
    assert len([name for name in actual.refs if name.startswith('Z/')]) == q*q


@pytest.mark.parametrize('change',['missing','repeated','column','operation','context','cover'])
def test_factor_dependencies_require_complete_ordered_committed_columns(tmp_path,monkeypatch,change):
    c = context(n=5)
    descriptors = []
    for operation in ('factor-diagonal','factor-below'):
        tasks = proposal._make_tasks(base(c),operation,{'factor':[]},0)
        outputs,rows = {},[]
        for task in tasks:
            refs = {name:asdict(ArtifactRef('fixture/'+name,'f'*64,1))
                    for name in proposal._task_panels(task)}
            outputs.update(refs)
            rows.append((task,{'scope':proposal.SCOPE,'panels':refs,'diagnostics':{}}))
        descriptors.append({'operation':operation,'column':0,'record':{
            'outputs':outputs,'context':proposal._wave_context(c,operation,0),'tasks':rows}})
    def read(record, expected):
        if record['context'] != expected:
            raise ContractError('changed dependency context')
        return tmp_path,record['outputs']
    monkeypatch.setattr(proposal,'read_group',read)
    monkeypatch.setattr(proposal,'group_tasks',lambda record,expected:iter(record['tasks']))
    if change == 'missing': descriptors.pop()
    elif change == 'repeated': descriptors[1] = descriptors[0]
    elif change == 'column': descriptors[1]['column'] = 2
    elif change == 'operation': descriptors[1]['operation'] = 'whiten-forward'
    elif change == 'context': descriptors[0]['record']['context']['context'] = {**c,'parity':1}
    else: descriptors[1]['record']['outputs'].pop('L/4/0')
    with pytest.raises(ContractError):
        proposal._dependency_store(descriptors,c,proposal._factor_waves(c,2),binding=base(c))


def test_failed_stage_dependency_is_not_consumed(tmp_path,monkeypatch):
    c = context(n=1,b=1)
    staged,wave,checks = harness(monkeypatch,tmp_path/'tasks',c,matrices(1))
    def failed(*args):
        raise ContractError('owned stage did not succeed')
    monkeypatch.setattr(proposal,'read_group',failed)
    task = proposal._make_tasks(base(c),'backsolve-quantize',{
        'factor':[{'operation':'factor-diagonal','column':0,'record':{}}],
        'floating':[{'operation':'float-optimize','column':None,'record':{}}]})[0]
    with pytest.raises(ContractError,match='did not succeed'):
        proposal.evaluate_proposal(task,staged)
    assert not (staged.root/'attempts').exists()
    assert len(checks) == 1


@pytest.mark.parametrize('operation',['factor-diagonal','factor-below','whiten-forward','whiten-transpose','backsolve-quantize'])
def test_closed_task_identity_rejects_foreign_geometry(operation):
    c = context()
    task = proposal._make_tasks(base(c),operation,{},0)[0]
    task['column'] = 1
    with pytest.raises(ContractError,match='column'):
        proposal._task_panels(task)
    task['column'] = 0
    task['unexpected'] = True
    with pytest.raises(ContractError,match='closed'):
        proposal._task_panels(task)


@pytest.mark.parametrize('edge',['schur','below','forward','backward'])
def test_uncertain_paid_pivots_reject_at_actual_consumer_edge(tmp_path,edge):
    c = context(n=2,b=1)
    store = proposal.PanelStore(tmp_path,c)
    with ctx.workprec(proposal.BITS):
        if edge == 'schur':
            store.put_native('L/0/0',arb_mat([[1]]))
            store.put_native('L/1/0',arb_mat([[arb(1,1)]]))
            with pytest.raises(ContractError,match='uncertain Cholesky pivot'):
                proposal._factor_diagonal(lambda i,j:arb_mat([[1]]),store,1)
            assert 'L/1/1' not in store.refs
        else:
            store.put_native('L/0/0',arb_mat([[arb(1,2)]]))
            store.put_native('L/1/1',arb_mat([[1]]))
            store.put_native('L/1/0',arb_mat([[0]]))
            with pytest.raises(ContractError,match='uncertain triangular pivot'):
                if edge == 'below':
                    proposal._factor_below(lambda i,j:arb_mat([[1]]),store,store,1,0)
                else:
                    proposal._solve_column(store,lambda i,j:arb_mat([[1]]),store,'W',0,
                                           transpose=edge == 'backward')
            assert 'Z/0/0' not in store.refs


@pytest.mark.parametrize('change',['missing','extra','wrong-kind','foreign-path','cross-context','raw-hash'])
def test_owner_rejects_wrong_assigned_panel_results(tmp_path,change):
    c = context(n=1,b=1)
    staged = staging(tmp_path/'tasks')
    store = proposal.PanelStore(staged.root,c,staging=staged)
    with ctx.workprec(proposal.BITS):
        store.put_native('L/0/0',arb_mat([[2]]))
    task = proposal._make_tasks(base(c),'factor-diagonal',{'factor':[]},0)[0]
    result = {'scope':proposal.SCOPE,'panels':dict(store.created),'diagnostics':{}}
    if change == 'missing': result['panels'].clear()
    elif change == 'extra': result['panels']['L/1/0'] = result['panels']['L/0/0']
    elif change == 'foreign-path': result['panels']['L/0/0'] = {**result['panels']['L/0/0'],'path':'foreign'}
    elif change == 'raw-hash': result['panels']['L/0/0'] = {**result['panels']['L/0/0'],'sha256':'0'*64}
    else:
        ref = result['panels']['L/0/0']
        path = staged.root/ref['path']
        document = proposal._json(path.read_bytes())
        if change == 'wrong-kind': document['header']['kind'] = 'integer'
        else: document['header']['context']['parity'] = 1
        raw = canonical_bytes(document)
        path.write_bytes(raw)
        result['panels']['L/0/0'] = asdict(ArtifactRef(ref['path'],hashlib.sha256(raw).hexdigest(),len(raw)))
    with pytest.raises((ContractError,FileNotFoundError)):
        proposal._validate_result(result,task,staged.root,staged.attempt_id)


def test_geometry_prices_bounded_wave_transport_and_retained_receipts():
    accounts = proposal._proposal_accounts(413,32)
    layout = proposal._proposal_layout(413,32)
    assert layout['panel_columns'] == 13
    assert layout['native_max_tasks'] == 39
    assert layout['factor_below_tasks'] == 78
    assert layout['stages_per_parity'] == 29
    assert accounts['native_result_bytes'] < proposal.MIB
    assert accounts['floating_result_bytes'] < proposal.MIB
    assert accounts['retained_graph_bytes'] > layout['native_max_tasks']*accounts['native_result_bytes']
    assert accounts['per_parity_panel_disk_bytes']+accounts['retained_graph_bytes']+64*proposal.MIB < 8192*proposal.MIB
    assert accounts['native_working_bytes'] <= 128*proposal.MIB
    # Tiny panels are not an unbounded task/result escape hatch.
    assert proposal._proposal_accounts(413,1)['floating_result_bytes'] > proposal.MIB


def owner_fixture(tmp_path, monkeypatch, *, completion='reverse', fail_publication=None):
    c = context(n=3,b=2)
    staged = staging(tmp_path/'owner')
    tasks = proposal._make_tasks(base(c),'whiten-forward',{'factor':[]})
    rows = []
    with ctx.workprec(proposal.BITS):
        for task in tasks:
            store = proposal.PanelStore(staged.root,c,staging=staged)
            for name in proposal._task_panels(task):
                _,i,j = name.split('/')
                shape = proposal._shape(c,int(i),int(j))
                store.put_native(name,arb_mat([[1]*shape[1] for _ in range(shape[0])]))
            rows.append({'task_id':task['task_id'],'scope':proposal.SCOPE,
                         'result':{'scope':proposal.SCOPE,'diagnostics':{},'panels':store.created}})
    if completion == 'reverse': rows.reverse()
    elif completion == 'missing': rows.pop()
    elif completion == 'repeated': rows[-1] = rows[0]
    elif completion == 'foreign': rows[-1] = {**rows[-1],'task_id':'0'*64}
    published,sealed = [],[]
    def immutable(folder, raw):
        if fail_publication is not None and len(published) == fail_publication:
            raise OSError('interrupted owner publication')
        sha = hashlib.sha256(raw).hexdigest()
        path = f'{folder}/{sha}'
        proposal._write(staged.root/path,raw)
        ref = ArtifactRef(path,sha,len(raw))
        published.append(ref)
        return ref
    lock = SimpleNamespace(root=staged.root,_immutable=immutable)
    def seal(lock, execution, stage, context, outputs):
        sealed.append(dict(outputs))
        return {'root':str(lock.root),'artifact':asdict(ArtifactRef('group','f'*64,1))}
    monkeypatch.setattr(proposal,'seal_group',seal)
    owned = SimpleNamespace(attempt_id=staged.attempt_id,receipts=[],
        run_stage=lambda stage,tasks:None,read_results=lambda stage:iter(rows))
    return lock,owned,tasks,published,sealed


def test_owner_publication_is_canonical_under_reversed_completions(tmp_path,monkeypatch):
    lock,owned,tasks,published,sealed = owner_fixture(tmp_path,monkeypatch)
    report = proposal._run_wave(lock,owned,tasks,'whiten-forward')
    assert len(sealed) == 1
    assert set(sealed[0]) == proposal._wave_names(tasks[0]['context'],'whiten-forward')
    assert [row['task_id'] for row in report['tasks']] == [task['task_id'] for task in tasks]
    expected = [name for task in tasks for name in sorted(proposal._task_panels(task))]
    actual = [proposal._json((lock.root/ref.path).read_bytes())['header']['name'] for ref in published]
    assert actual == expected


@pytest.mark.parametrize('completion',['missing','repeated','foreign'])
def test_incomplete_successful_wave_never_publishes_a_dependency(tmp_path,monkeypatch,completion):
    lock,owned,tasks,published,sealed = owner_fixture(tmp_path,monkeypatch,completion=completion)
    with pytest.raises(ContractError):
        proposal._run_wave(lock,owned,tasks,'whiten-forward')
    assert published == sealed == []


@pytest.mark.parametrize('interruption',[0,1])
def test_interrupted_owner_publication_never_seals_partial_group(tmp_path,monkeypatch,interruption):
    lock,owned,tasks,published,sealed = owner_fixture(tmp_path,monkeypatch,fail_publication=interruption)
    with pytest.raises(OSError,match='interrupted'):
        proposal._run_wave(lock,owned,tasks,'whiten-forward')
    assert len(published) == interruption
    assert all((lock.root/ref.path).exists() for ref in published)
    assert sealed == []


def test_native_account_equality_and_overrun_precede_source_validation(tmp_path,monkeypatch):
    c = context(n=7,b=32)
    staged = SimpleNamespace(root=tmp_path,_check=lambda:None,spec=SimpleNamespace(problem=object()))
    accounts = proposal._proposal_accounts(7,32)
    assert accounts['native_working_bytes'] == 70*proposal.MIB
    class ReachedSource(Exception):
        pass
    def source(*args):
        raise ReachedSource()
    monkeypatch.setattr(proposal,'_reader',source)
    monkeypatch.setattr(proposal,'sys',SimpleNamespace(modules={'flint':True}))
    task = proposal._make_tasks(base(c),'factor-diagonal',{'factor':[]},0)[0]
    for private,expected in ((69,ContractError),(70,ReachedSource)):
        plan = SimpleNamespace(role='proposal',scope=proposal.SCOPE,
                               worker_private_mib=private,backend='python-flint')
        monkeypatch.setattr(execution,'_WORKER',(plan,staged))
        with pytest.raises(expected):
            proposal.evaluate_proposal(task,staged)


def test_oversized_callback_geometry_rejects_before_allocating_names(tmp_path,monkeypatch):
    c = context(n=413,b=1)
    staged = SimpleNamespace(root=tmp_path,_check=lambda:None)
    plan = SimpleNamespace(role='proposal',scope=proposal.SCOPE,worker_private_mib=128)
    monkeypatch.setattr(execution,'_WORKER',(plan,staged))
    monkeypatch.setattr(proposal,'_task_panels',lambda task:pytest.fail('allocated oversized output cover'))
    with pytest.raises(ContractError,match='bounded transport'):
        proposal.evaluate_proposal({'context':c,'operation':'factor-diagonal'},staged)


@pytest.mark.parametrize('edge',['below','forward','backward'])
def test_positive_native_pivot_can_become_uncertain_only_at_paid_grid_consumer(tmp_path,edge):
    c = context(n=2 if edge == 'below' else 1,b=1)
    store = proposal.PanelStore(tmp_path,c)
    tiny = fmpq(1,1 << 2200)
    with ctx.workprec(proposal.BITS):
        lower = proposal._factor_diagonal(lambda i,j:arb_mat([[tiny]]),store,0)
        assert lower > 0
        assert store.native('L/0/0')[0,0].contains(0)
        with pytest.raises(ContractError,match='uncertain triangular pivot'):
            if edge == 'below':
                proposal._factor_below(lambda i,j:arb_mat([[0]]),store,store,1,0)
            else:
                proposal._solve_column(store,lambda i,j:arb_mat([[1]]),store,'W',0,
                                       transpose=edge == 'backward')
        assert 'W/0/0' not in store.refs


def test_strictly_positive_exact_schur_complement_rejects_native_uncertainty(tmp_path):
    c = context(n=2,b=1)
    store = proposal.PanelStore(tmp_path,c)
    matrix = fmpq_mat([[1,1],[1,1+fmpq(1,1 << 2200)]])
    with ctx.workprec(proposal.BITS):
        with pytest.raises(ContractError,match='uncertain Cholesky pivot'):
            proposal.blocked_cholesky(lambda i,j:panel(matrix,i,j,c),store)
    assert 'L/0/0' in store.refs and 'L/1/0' in store.refs
    assert 'L/1/1' not in store.refs


def test_native_writer_magnitude_guard_justifies_interval_and_quantization_disk_bounds(tmp_path):
    c = context(n=1,b=1)
    store = proposal.PanelStore(tmp_path,c)
    with ctx.workprec(proposal.BITS):
        store.put_native('W/0/0',arb_mat([[arb(2)**31]]))
        pair = store.read('W/0/0','interval')[0]
        assert len(canonical_bytes(pair)) <= 560
        quantize(store,c)
        assert len(canonical_bytes(store.read('Z/0/0','integer')[0])) <= 64
        with pytest.raises(ContractError,match='compact representation'):
            store.put_native('L/0/0',arb_mat([[arb(2)**32]]))
    assert 'L/0/0' not in store.refs


@pytest.mark.parametrize('change',[None,'swapped','missing-task','repeated-task','unrelated-operation','foreign-source'])
def test_consumed_group_binds_exact_requests_and_named_result_attribution(tmp_path,monkeypatch,change):
    c = context(n=5,b=2)
    tasks = proposal._make_tasks(base(c),'factor-below',{'factor':[]},0)
    outputs,rows = {},[]
    for index,task in enumerate(tasks):
        name, = proposal._task_panels(task)
        sha = format(index+1,'064x')
        outputs[name] = asdict(ArtifactRef('seals/'+str(index),sha,1))
        actual = asdict(ArtifactRef('attempts/staging/'+str(index),sha,1))
        rows.append((task,{'scope':proposal.SCOPE,'diagnostics':{},'panels':{name:actual}}))
    if change == 'swapped':
        names = list(outputs)
        outputs[names[0]],outputs[names[1]] = outputs[names[1]],outputs[names[0]]
    elif change == 'missing-task':
        rows.pop()
    elif change == 'repeated-task':
        rows[-1] = rows[0]
    elif change in ('unrelated-operation','foreign-source'):
        task,result = rows[0]
        task = {**task}
        if change == 'unrelated-operation':
            task['operation'] = 'factor-diagonal'
            task.pop('row')
        else:
            task['source'] = {'different':'source binding'}
        task['task_id'] = hashlib.sha256(canonical_bytes(
            {key:value for key,value in task.items() if key != 'task_id'})).hexdigest()
        rows[0] = task,result
    monkeypatch.setattr(proposal,'read_group',lambda record,expected:(tmp_path,outputs))
    monkeypatch.setattr(proposal,'group_tasks',lambda record,expected:iter(rows))
    descriptors = [{'operation':'factor-below','column':0,'record':{}}]
    if change is None:
        store = proposal._dependency_store(descriptors,c,[('factor-below',0)],binding=base(c))
        assert store.refs == outputs
    else:
        with pytest.raises(ContractError):
            proposal._dependency_store(descriptors,c,[('factor-below',0)],binding=base(c))
