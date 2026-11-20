"""Complete manufactured integer graph versus the retained contraction reference."""
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.whole_source import exact as e, exact_tasks as graph
from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes
from scripts.whole_source.artifacts import CodecBounds
from scripts.whole_source.execution import MIB, _write


@pytest.fixture
def finite_graph(tmp_path, monkeypatch):
    from flint import fmpz_mat
    n, b = 7, 2
    problem = SimpleNamespace(eta=Fraction(7,8), model_error=Fraction(1,1024), numerical_goal=Fraction(1,100))
    contexts, blocks, tiles = [], [], []
    for p in (0,1):
        context = {'dimension':n,'panel_size':b,'parity':p,'u':3,'endpoint_bits':12,'z_bits':8,
                   'problem_id':'2'*64,'source_sha256':'3'*64,'proposal_sha256':'1'*64}
        parameters = e.paid_parameters(8,Fraction(3,2),problem.eta)
        context['product_bits'] = e.integer_bounds(context,parameters,problem.model_error)['product_bits']
        transform = e.IntegerTiles(tmp_path,context)
        for i in range(0,n,b):
            for j in range(0,n,b):
                transform.put_values('Z',i,j,[8*(r+2) if r==c else (r+c)%3-1
                    for r in range(i,min(i+b,n)) for c in range(j,min(j+b,n))])
        contexts.append(context)
        blocks.append({'context':context,'theta':'3/2','panels':transform.refs})
        for family in ('A_model','weighted_head','weighted_complete_tail'):
            ref = _write(tmp_path/f'{family}-{p}.json',canonical_bytes({'declared_control':family,'parity':p}))
            tiles.append({'family':family,'parity':p,'artifact':asdict(ref)})
    reader = SimpleNamespace(bits=8,path=tmp_path/'source-manifest.json',document={'tiles':tiles})
    class Source:
        def __init__(self,reader,context):
            self.context=context
            self.consumed=set()
        def bounds(self,family,i,j):
            row=next(row for row in tiles if row['family']==family and row['parity']==self.context['parity'])
            ref=row['artifact']
            self.consumed.add((ref['path'],ref['sha256'],ref['size']))
            centers={'A_model':2048,'weighted_head':16,'weighted_complete_tail':24}
            values=[[centers[family]*(r+1) if r==c else (r+c)%5-2
                for c in range(j,min(j+b,n))] for r in range(i,min(i+b,n))]
            return fmpz_mat([[x-1 for x in row] for row in values]),fmpz_mat([[x+1 for x in row] for row in values])
    monkeypatch.setattr(e,'ROOT',tmp_path)
    monkeypatch.setattr(e,'SourceIntegers',Source)
    descriptor={'blocks':blocks,'proof_scope':'CONTROL_ONLY'}
    staging=SimpleNamespace(root=tmp_path,attempt_id='control',_check=lambda:None,
        spec=SimpleNamespace(problem=problem,bounds=CodecBounds(8*MIB,8*MIB,8*MIB,2048,65536,
            256*1024,64*1024,1024*MIB,512*MIB,64*MIB)))
    (tmp_path/'attempts/control/staging').mkdir(parents=True)
    (tmp_path/'.volume.lock').touch()
    worker=[SimpleNamespace(worker_private_mib=128,native_workspace_mib=128)]
    waves={}
    def read_group(record,context,**authority):
        assert record=={'operation':context['operation']}
        assert authority=={'expected_root':tmp_path,'expected_attempt':'control'}
        return tmp_path,waves[context['operation']]
    monkeypatch.setattr(graph,'read_group',read_group)
    task_results={}
    monkeypatch.setattr(graph,'group_tasks',lambda record,context,**authority: iter(reversed(task_results[context['operation']])))
    monkeypatch.setattr(graph,'same_group',lambda left,right:left==right)
    operands={'path':'operands.json','sha256':'4'*64,'size':1}
    reports=[]
    for operation in ('global','first','second','reduce'):
        outputs={}
        task_results[operation]=[]
        deps={key:{'operation':key} for key in waves}
        for p,block in enumerate(blocks):
            coords=([{}] if operation in ('global','reduce') else [{'row':i} for i in range(0,n,b)]
                    if operation=='first' else [{'row':i,'column':j} for i in range(0,n,b) for j in range(i,n,b)])
            for fields in coords:
                task=graph._request(operation,operands,deps,parity=p,**fields)
                result=graph.evaluate(task,staging,descriptor,reader,worker)
                task_results[operation].append((task,result))
                if operation in ('global','reduce'):
                    key='metadata' if operation=='global' else 'report'
                    outputs[f'{operation}/{p}']=asdict(_write(tmp_path/f'{operation}-{p}.json',canonical_bytes(result[key])))
                    if operation=='reduce': reports.append(result['report'])
                elif operation=='first':
                    outputs.update({f'{p}/{key}':value for key,value in result['panels'].items()})
                    i=fields['row']
                    outputs[f'row/{p}/{i}']=asdict(_write(tmp_path/f'row-{p}-{i}.json',canonical_bytes(result['metadata'])))
                else:
                    outputs[f"block/{p}/{fields['row']}/{fields['column']}"]=result['block']
        waves[operation]=outputs
    return tmp_path,problem,reader,Source,descriptor,waves,reports,operands


def test_complete_graph_matches_signed_ragged_reference(finite_graph):
    root,problem,reader,Source,descriptor,waves,reports,_=finite_graph
    for p,block in enumerate(descriptor['blocks']):
        context=block['context']
        transform=e.IntegerTiles(root,context,block['panels'])
        masses=e.mass_trace(7,p,3,2,transform.tile)
        products=e.IntegerTiles(root,context)
        source=Source(reader,context)
        reference=e.integer_congruence(source,transform,products,e.paid_parameters(8,Fraction(3,2),problem.eta),masses,problem.model_error)
        for key,value in reference.items():
            assert reports[p][key]==value,key
        for name,ref in products.refs.items():
            i,j=map(int,name.split('/')[1:])
            family=name.split('/')[0]
            actual=e.IntegerTiles(root,context,{name:waves['first'][f'{p}/{name}']})
            assert actual.tile(i,j,family)==products.tile(i,j,family)
        assert reports[p]['source_tiles_consumed']==3
        assert reports[p]['modular']['global_input_entries']==49


def test_missing_upper_block_cannot_be_consumed(finite_graph):
    root,_,_,_,descriptor,waves,_,operands=finite_graph
    del waves['second']['block/1/0/2']
    task=graph._request('reduce',operands,{'second':{'operation':'second'}},parity=0)
    with pytest.raises(ContractError,match='wave cover'):
        graph._wave(task,descriptor,'second',expected_root=root,expected_attempt='control')


def test_other_context_is_rejected_before_block_reduction(finite_graph):
    root,problem,reader,Source,descriptor,waves,reports,operands=finite_graph
    reference=waves['second']['block/0/0/2']
    raw=(root/reference['path']).read_bytes()
    account=e.integer_bounds(descriptor['blocks'][1]['context'],e.paid_parameters(8,Fraction(3,2),problem.eta),problem.model_error)
    with pytest.raises(ContractError,match='block context'):
        graph._block_values(raw,descriptor['blocks'][1]['context'],0,2,account)


@pytest.mark.parametrize('operation',['global','first','second','reduce'])
@pytest.mark.parametrize('change',['missing','repeated','identity','foreign','attribution'])
def test_complete_wave_rejects_invalid_task_provenance(finite_graph,monkeypatch,operation,change):
    import copy
    root,_,_,_,descriptor,waves,_,operands=finite_graph
    context=graph._context(descriptor,operands,operation)
    rows=copy.deepcopy(list(graph.group_tasks({'operation':operation},context)))
    if change=='missing':
        rows.pop()
    elif change=='repeated':
        rows.append(rows[0])
    elif change=='identity':
        rows[0][0]['task_id']='0'*64
    elif change=='foreign':
        rows[0][0]['operands']={**operands,'sha256':'5'*64}
        original=rows[0][0]
        original['task_id']=graph._request(operation,original['operands'],original['groups'],
            **{key:value for key,value in original.items()
               if key not in ('operation','operands','groups','task_id')})['task_id']
    else:
        names=sorted(waves[operation])
        waves[operation][names[0]]=waves[operation][names[-1]]
    monkeypatch.setattr(graph,'group_tasks',lambda record,context,**authority:iter(rows))
    task=graph._request('assess',operands,{operation:{'operation':operation}},blocks=[])
    with pytest.raises(ContractError):
        graph._wave(task,descriptor,operation,expected_root=root,expected_attempt='control')


@pytest.mark.parametrize('change',['shape','negative_radius','integer','coordinate','parity'])
def test_canonical_output_payload_rejects_corruption(finite_graph,change):
    import json
    root,problem,_,_,descriptor,waves,_,_=finite_graph
    context=descriptor['blocks'][0]['context']
    ref=waves['second']['block/0/0/2']
    data=json.loads((root/ref['path']).read_bytes())
    if change=='shape':
        data['center'].pop()
    elif change=='negative_radius':
        data['radius'][0]='-0x1'
    elif change=='integer':
        data['center'][0]='0x00'
    elif change=='coordinate':
        data['column']=4
    else:
        data['context']['parity']=1
    account=e.integer_bounds(context,e.paid_parameters(8,Fraction(3,2),problem.eta),problem.model_error)
    with pytest.raises(ContractError):
        graph._block_values(canonical_bytes(data),context,0,2,account)


def test_signed_ragged_graph_matches_independent_fraction_entries(finite_graph):
    from tests.test_whole_source_exact import multiply,transpose
    root,problem,reader,Source,descriptor,waves,reports,_=finite_graph
    for p,block in enumerate(descriptor['blocks']):
        context=block['context']
        transform=e.IntegerTiles(root,context,block['panels'])
        z=[[Fraction(int(transform.tile((r//2)*2,(c//2)*2)[r%2,c%2]),8)
            for c in range(7)] for r in range(7)]
        source=Source(reader,context)
        low,high=[],[]
        for r in range(7):
            lr,hr=[],[]
            for c in range(7):
                bounds=[source.bounds(family,(r//2)*2,(c//2)*2) for family in
                        ('A_model','weighted_head','weighted_complete_tail')]
                a,h,t=[(Fraction(int(lo[r%2,c%2]),256),Fraction(int(hi[r%2,c%2]),256))
                       for lo,hi in bounds]
                head,tail=Fraction(5,2)/problem.eta,Fraction(5,3)/problem.eta
                lr.append(a[0]-head*h[1]-tail*t[1])
                hr.append(a[1]-head*h[0]-tail*t[0])
            low.append(lr)
            high.append(hr)
        centers=[[(lo+hi)/2 for lo,hi in zip(lr,hr,strict=True)] for lr,hr in zip(low,high,strict=True)]
        radii=[[(hi-lo)/2 for lo,hi in zip(lr,hr,strict=True)] for lr,hr in zip(low,high,strict=True)]
        absolute=[[abs(value) for value in row] for row in z]
        center=multiply(multiply(transpose(z),centers),z)
        radius=multiply(multiply(transpose(absolute),radii),absolute)
        mass=[[Fraction(2,2*(2*r+p)+1) if r==c else Fraction(0)
               for c in range(7)] for r in range(7)]
        transformed_mass=multiply(multiply(transpose(z),mass),z)
        report=reports[p]
        BD,ED=int(report['center_denominator'],16),int(report['radius_denominator'],16)
        account=e.integer_bounds(context,e.paid_parameters(8,Fraction(3,2),problem.eta),problem.model_error)
        for i in range(0,7,2):
            for j in range(i,7,2):
                ref=waves['second'][f'block/{p}/{i}/{j}']
                _,actual_center,actual_radius=graph._block_values((root/ref['path']).read_bytes(),context,i,j,account)
                columns=min(2,7-j)
                for r in range(min(2,7-i)):
                    for c in range(columns):
                        index=r*columns+c
                        assert Fraction(actual_center[index],BD)==center[i+r][j+c]-problem.model_error*transformed_mass[i+r][j+c]
                        assert Fraction(actual_radius[index],ED)==radius[i+r][j+c]
        margins=[center[r][r]-problem.model_error*transformed_mass[r][r]
                 -sum(abs(center[r][c]-problem.model_error*transformed_mass[r][c]) for c in range(7) if c!=r)
                 -sum(radius[r]) for r in range(7)]
        assert report['row_margins']==margins


def _reduce_graph(finite_graph):
    root,problem,reader,_,descriptor,_,_,operands=finite_graph
    staging=SimpleNamespace(root=root,attempt_id='control',spec=SimpleNamespace(problem=problem,
        bounds=SimpleNamespace(max_temporary_bytes=512*MIB)))
    worker=[SimpleNamespace(worker_private_mib=128,native_workspace_mib=128)]
    task=graph._request('reduce',operands,
        {name:{'operation':name} for name in ('global','first','second')},parity=0)
    return graph.evaluate(task,staging,descriptor,reader,worker)


@pytest.mark.parametrize('change',['missing','corrupt'])
def test_reducer_rechecks_actual_transformed_payload_bytes(finite_graph,change):
    root,_,_,_,_,waves,_,_=finite_graph
    path=root/waves['second']['block/0/0/2']['path']
    if change=='missing':
        path.unlink()
    else:
        path.write_bytes(path.read_bytes()+b' ')
    with pytest.raises((ContractError,OSError)):
        _reduce_graph(finite_graph)


@pytest.mark.parametrize('change',['missing','repeated','foreign','negative'])
def test_reducer_rejects_invalid_source_consumption_metadata(finite_graph,change):
    root,_,reader,_,descriptor,waves,_,operands=finite_graph
    rows=list(graph.group_tasks({'operation':'first'},graph._context(descriptor,operands,'first')))
    for task,result in rows:
        if task['parity']!=0:
            continue
        metadata=result['metadata']
        if change=='missing':
            metadata['consumed']=metadata['consumed'][1:]
        elif change=='repeated':
            metadata['consumed'].append(metadata['consumed'][0])
        elif change=='foreign':
            ref=next(row['artifact'] for row in reader.document['tiles'] if row['parity']==1)
            metadata['consumed'].append((ref['path'],ref['sha256'],ref['size']))
        else:
            metadata['row_sums'][0]='-0x1'
        waves['first'][f"row/0/{task['row']}"]=asdict(_write(
            root/f"invalid-source-row-{task['row']}.json",canonical_bytes(metadata)))
    with pytest.raises(ContractError,match='source|radius'):
        _reduce_graph(finite_graph)


def test_final_assessment_requires_canonical_complete_parities(finite_graph):
    root,_,_,_,descriptor,waves,_,operands=finite_graph
    refs=[waves['reduce'][f'reduce/{p}'] for p in (0,1)]
    task=graph._request('assess',operands,{'reduce':{'operation':'reduce'}},blocks=refs)
    assert graph.assessment_reports(task,descriptor,root,'control')==refs
    for invalid in (refs[::-1],refs[:1],[refs[0],refs[0]]):
        task=graph._request('assess',operands,{'reduce':{'operation':'reduce'}},blocks=invalid)
        with pytest.raises(ContractError,match='complete parity'):
            graph.assessment_reports(task,descriptor,root,'control')


@pytest.mark.parametrize('foreign',['root','attempt'])
def test_owned_consumer_supplies_current_group_authority(finite_graph,monkeypatch,foreign):
    root,*_=finite_graph
    def refuse(record,context,*,expected_root,expected_attempt):
        assert expected_root==root and expected_attempt=='control'
        raise ContractError('foreign exact dependency '+foreign)
    monkeypatch.setattr(graph,'read_group',refuse)
    with pytest.raises(ContractError,match='foreign exact dependency'):
        _reduce_graph(finite_graph)
