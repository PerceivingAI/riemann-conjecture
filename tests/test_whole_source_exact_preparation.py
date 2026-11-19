"""Admission and byte-identity edges without a numerical backend or full matrices."""
from dataclasses import asdict
from fractions import Fraction
import hashlib
import subprocess
import sys
from types import SimpleNamespace

import pytest

from scripts.whole_source import exact as e
from scripts.whole_source import resources
from scripts.whole_source.artifacts import CodecBounds
from scripts.whole_source.contract import ArtifactRef, ContractError
from scripts.whole_source.execution import MIB


def detected(available=16*1024*MIB):
    return {'platform':'win32','cpu_detection_complete':True,'memory_detection_complete':True,
            'affinity_cpus':2,'logical_cpus':2,'effective_cpu_budget':2,'quota_cpu_limit':None,
            'available_memory_bytes':available}


def record(path, raw=b'{}'):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)
    return ArtifactRef(path.name,hashlib.sha256(raw).hexdigest(),len(raw))


@pytest.fixture
def preparation(tmp_path,monkeypatch):
    source=tmp_path/'source.json'
    source_ref=record(source)
    execution_ref=record(tmp_path/'source-execution.json')
    origin_ref=record(tmp_path/'origin.json')
    tile_ref=record(tmp_path/'tile.json')
    record(tmp_path/'scripts/whole_source/exact.py')
    problem=SimpleNamespace(profile='retained-t081',eta=Fraction(7,8),model_error=Fraction(1,1024))
    bounds=CodecBounds(8*MIB,8*MIB,8*MIB,16384,8192,256*1024,64*1024,
                       8192*MIB,128*MIB,64*MIB)
    reader=SimpleNamespace(path=source,ref=source_ref,bits=1024,
        execution_path=tmp_path/'source-execution.json',execution_ref=execution_ref,
        spec=SimpleNamespace(bounds=bounds,_snapshots=()),
        document={'control':True,'geometry':{'N':14},'tiles':[
            {'parity':p,'task':{},'artifact':asdict(tile_ref)} for p in (0,1)]})
    state={'endpoint':17,'transform':3,'calls':0}
    def read_values(i,j):
        state['calls']+=1
        return [state['transform']]*(min(2,7-i)*min(2,7-j))
    blocks=[{'parity':p,'dimension':7,'panel_size':2,'u':3,'theta':Fraction(3,2),
             'read_values':read_values} for p in (0,1)]
    origin={'kind':'REFERENCE_TRANSCRIPTION','directory':str(tmp_path),'artifact':asdict(origin_ref)}
    monkeypatch.setattr(e,'problem_id',lambda problem:'1'*64)
    monkeypatch.setattr(e,'_preparation_reader',lambda problem,path:reader)
    monkeypatch.setattr(e,'_task',lambda task:task)
    monkeypatch.setattr(e,'publication_integers',lambda *args:[(0,0,-state['endpoint'],state['endpoint'])])
    monkeypatch.setattr(e.importlib.metadata,'version',lambda name:'test-metadata-only')
    return tmp_path,problem,source,blocks,origin,reader,state


def inspect(case,**kwargs):
    root,problem,source,blocks,origin,*_=case
    return e.inspect_exact_preparation(problem,source,blocks,origin,code_root=root,
                                       detected=detected(),**kwargs)


def prepare(case,**kwargs):
    root,problem,source,blocks,origin,*_=case
    return e.prepare_exact_operands(problem,source,root/'output',blocks,origin,
        origin_git_commit='0'*40,origin_git_dirty=False,code_root=root,
        detected=detected(),**kwargs)


def test_low_memory_refuses_before_source_decoder_callback_or_output(preparation,monkeypatch):
    def forbidden(*args,**kwargs):
        pytest.fail('decoder or capture ran before RAM admission')
    monkeypatch.setattr(e,'_preparation_reader',forbidden)
    monkeypatch.setattr(e,'_freeze_source',forbidden)
    with pytest.raises(ContractError,match='preparation exceeds memory cap'):
        prepare(preparation,preparation_mib=1)
    assert preparation[-1]['calls']==0
    assert not (preparation[0]/'output').exists()


def test_proposal_wrapper_refuses_before_loading_large_inputs(preparation,monkeypatch):
    root,problem,source,_,origin,*_=preparation
    monkeypatch.setattr(e,'read_proposal',lambda *args:pytest.fail('proposal decoded before admission'))
    with pytest.raises(ContractError,match='preparation exceeds memory cap'):
        e.prepare_exact_inputs(problem,source,root/origin['artifact']['path'],root/'output',
            origin_git_commit='0'*40,origin_git_dirty=False,code_root=root,
            preparation_mib=1,detected=detected())
    assert not (root/'output').exists()


def test_actual_endpoint_transform_and_theta_change_account(preparation):
    base=inspect(preparation)
    preparation[-1]['endpoint']=1<<511
    endpoint=inspect(preparation)
    assert endpoint['contexts'][0]['endpoint_bits']==512
    assert endpoint['accounts'][0]['center_bits']>base['accounts'][0]['center_bits']
    assert endpoint['accounts'][0]['private_bytes']>base['accounts'][0]['private_bytes']
    preparation[-1]['transform']=1<<1023
    transform=inspect(preparation)
    assert transform['contexts'][0]['z_bits']==1024
    assert transform['normalized_bytes']>endpoint['normalized_bytes']
    assert transform['accounts'][0]['product_bits']>endpoint['accounts'][0]['product_bits']
    for block in preparation[3]:
        block['theta']=Fraction(1,(1<<1024)+1)
    theta=inspect(preparation)
    assert theta['accounts'][0]['parameter_bits']>transform['accounts'][0]['parameter_bits']
    assert theta['preparation_bytes']>transform['preparation_bytes']
    assert theta['source_codec']['max_endpoint_bits']==8192
    assert theta['original_bytes']>0 and theta['decoder_bytes']>0 and theta['caller_scratch_bytes']>0
    assert theta['os_enforced'] is False


def test_declared_scratch_cannot_undercut_codec_minimum(preparation):
    base=inspect(preparation)
    assert inspect(preparation,caller_scratch_bytes=1)['caller_scratch_bytes']==base['caller_scratch_bytes']
    extra=inspect(preparation,caller_scratch_bytes=base['caller_scratch_bytes']+MIB)
    assert extra['preparation_bytes']==base['preparation_bytes']+MIB


def test_unknown_memory_and_live_low_headroom_refuse(preparation):
    root,problem,source,blocks,origin,*_=preparation
    for snapshot,match in [({'memory_detection_complete':False},'discovery is incomplete'),
                           (detected(MIB),'available RAM')]:
        with pytest.raises(ContractError,match=match):
            e.inspect_exact_preparation(problem,source,blocks,origin,code_root=root,detected=snapshot)


def test_owned_plan_refusal_precedes_snapshot_and_output(preparation,monkeypatch):
    def refuse(*args,**kwargs):
        assert not (preparation[0]/'output').exists()
        raise ContractError('owned working set refused')
    monkeypatch.setattr(resources,'auto_plan',refuse)
    monkeypatch.setattr(e,'_freeze_source',lambda *args:pytest.fail('snapshot created before owned admission'))
    with pytest.raises(ContractError,match='owned working set refused'):
        prepare(preparation)
    assert not (preparation[0]/'output').exists()


@pytest.mark.parametrize('changed',['transform','theta','source','origin'])
def test_inputs_rechecked_before_normalization(preparation,changed):
    inspection=inspect(preparation)
    root,_,source,blocks,origin,reader,state=preparation
    if changed=='transform':
        state['transform']=2  # Same bit length, different operand.
    elif changed=='theta':
        blocks[0]['theta']=Fraction(5,3)
    else:
        (source if changed=='source' else root/origin['artifact']['path']).write_bytes(b'[]')
    with pytest.raises(ContractError,match='changed exact transform|fingerprint mismatch'):
        e._recheck_preparation(inspection,reader,blocks,origin)
    assert not (root/'output').exists()


def test_oversized_callback_integer_refuses_without_output(preparation):
    preparation[-1]['transform']=1<<8192
    with pytest.raises(ContractError,match='oversized transform'):
        prepare(preparation)
    assert not (preparation[0]/'output').exists()


def test_changed_normalized_bytes_are_rejected(preparation,monkeypatch):
    root,_,_,_,_,reader,_=preparation
    def frozen(problem,source_reader,directory):
        assert source_reader is reader
        return {},reader,[]
    monkeypatch.setattr(e,'_freeze_source',frozen)
    original=e.IntegerTiles.put_values
    def corrupt(store,*args):
        original(store,*args)
        ref=ArtifactRef(**next(reversed(store.refs.values())))
        (store.root/ref.path).write_bytes(b'{}')
    monkeypatch.setattr(e.IntegerTiles,'put_values',corrupt)
    with pytest.raises(ContractError,match='invalid regular artifact|fingerprint mismatch'):
        prepare(preparation)
    assert not (root/'output/operands.json').exists()
    assert not (root/'output/execution.json').exists()


def test_account_stays_out_of_portable_operand_descriptor(preparation,monkeypatch):
    root,problem,_,_,_,reader,_=preparation
    for name in (*e._RUNTIME,'scripts/whole_source/slice.py','scripts/whole_source/gram.py',
                 'scripts/whole_source/pipeline.py','scripts/whole_source/proposal.py',
                 'scripts/whole_source/proposal_float.py','scripts/whole_source/exact_global.py',
                 'scripts/weil_whole_source_split.py'):
        record(root/name)
    problem.to_dict=lambda:{'profile':'retained-t081'}
    monkeypatch.setattr(e,'_freeze_source',lambda problem,source,directory: ({},reader,[]))
    monkeypatch.setattr(e,'_quantities',lambda *args:())
    monkeypatch.setattr(e,'_partition',lambda *args:())
    monkeypatch.setattr(e.CollectionSpec,'create',lambda *args,**kwargs:
                        SimpleNamespace(collection_id='2'*64,to_dict=lambda:{}))
    result=prepare(preparation)
    descriptor=e._json(result['operands'].read_bytes())
    assert descriptor['format']==e.OPERANDS
    assert 'directory' not in descriptor['origin']
    assert descriptor['origin']['artifact']=={
        field:preparation[4]['artifact'][field] for field in ('sha256','size')}
    assert all(ref['path'].startswith(f'transform-{parity}/')
               for parity,block in enumerate(descriptor['blocks']) for ref in block['panels'].values())
    assert 'preparation' not in descriptor
    account=e._json((root/'output/preparation-account.json').read_bytes())
    assert account['format']=='whole-source-exact-preparation-v1'
    assert account['theta']==['3/2','3/2']
    assert account['os_enforced'] is False
    provenance=e._json((root/'output/exact-origin.json').read_bytes())
    assert all(not row['path'].endswith('preparation-account.json') for row in provenance['files'])
    inventory=e._json((root/'output/preparation-diagnostics.json').read_bytes())
    assert inventory['account']==asdict(e._ref(root/'output','preparation-account.json'))


def test_full_413_geometry_uses_only_bounded_panels(preparation):
    _,_,_,blocks,_,reader,state=preparation
    reader.document['geometry']['N']=826
    maximum=[]
    for block in blocks:
        block['dimension']=413
        block['panel_size']=32
        def read_values(i,j):
            count=min(32,413-i)*min(32,413-j)
            maximum.append(count)
            return [3]*count
        block['read_values']=read_values
    account=inspect(preparation)
    assert max(maximum)==1024
    assert len(account['panel_digests'][0])==13**2
    assert account['layout']['max_wave_tasks']==182
    assert account['accounts'][0]['modular_workspace_bytes']>=32*413**2


def test_metadata_import_does_not_load_numerical_libraries():
    result=subprocess.run([sys.executable,'-c',
        "import sys; from scripts.whole_source.exact import inspect_exact_preparation; "
        "assert not {'flint','numpy','scipy'}.intersection(sys.modules)"],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
