"""Real exact panel reuse preserves signed integers and fresh integrity checks."""
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json

import pytest
from scripts.whole_source import exact
from scripts.whole_source.contract import ContractError,ArtifactRef,canonical_bytes
from scripts.whole_source.reuse import WorkingSet,PANEL_DECODED_BYTES
from tests.test_whole_source_proposal_reuse import source_panels


def context(parity=0):
    return {'dimension':3,'panel_size':2,'parity':parity,'u':2,'endpoint_bits':512,
        'z_bits':8,'product_bits':1024,'problem_id':'a'*64,'source_sha256':'b'*64,'proposal_sha256':'c'*64}


def integer_store(tmp_path):
    store=exact.IntegerTiles(tmp_path,context())
    store.put_values('Z',0,0,[2,-1,3,4])
    store.put_values('Z',2,0,[-5,6])
    return store


def test_integer_tile_hits_save_parsing_and_never_alias_mutable_results(tmp_path,monkeypatch):
    store=integer_store(tmp_path)
    parsed,read=[],[]
    original_json,original_raw=exact._json,exact._raw
    def decode(raw):
        parsed.append(1)
        return original_json(raw)
    def raw(*args):
        read.append(1)
        return original_raw(*args)
    monkeypatch.setattr(exact,'_json',decode)
    monkeypatch.setattr(exact,'_raw',raw)
    first=store.tile(0,0)
    first[0,0]=77
    second=store.tile(0,0)
    assert [int(second[r,c]) for r in range(2) for c in range(2)]==[2,-1,3,4]
    assert len(parsed)==1 and len(read)==2
    assert store.decoded.resident<=store.decoded.peak<=store.decoded.limit


@pytest.mark.parametrize('change',['bytes','deleted','header','context','path'])
def test_exact_hit_never_bypasses_raw_or_context_validation(tmp_path,change):
    store=integer_store(tmp_path)
    store.tile(0,0)
    row=store.refs['Z/0/0']
    path=tmp_path/row['path']
    if change=='bytes':
        path.write_bytes(b'changed after cache fill')
    elif change=='deleted':
        path.unlink()
    elif change=='context':
        store.context['z_bits']=1
    elif change=='path':
        store.refs['Z/0/0']={**row,'path':'../foreign'}
    else:
        document=json.loads(path.read_bytes())
        document['header']['columns']=1
        raw=canonical_bytes(document)
        path.write_bytes(raw)
        store.refs['Z/0/0']=asdict(ArtifactRef(row['path'],hashlib.sha256(raw).hexdigest(),len(raw)))
    with pytest.raises((ContractError,OSError)):
        store.tile(0,0)


@pytest.mark.parametrize('parity',[0,1])
def test_source_bounds_reuse_keeps_reflection_endpoints_and_mutable_ownership(tmp_path,monkeypatch,parity):
    panels=source_panels(tmp_path,parity)
    source=exact.SourceIntegers(panels.reader,context(parity))
    calls=[]
    original=exact.publication_integers
    def decode(*args):
        calls.append(1)
        return original(*args)
    monkeypatch.setattr(exact,'publication_integers',decode)
    lower,upper=source.bounds('A_model',0,0)
    expected=int(lower[0,0])
    lower[0,0]=123
    again,_=source.bounds('A_model',0,0)
    assert int(again[0,0])==expected and len(calls)==1
    reflected=source.bounds('A_model',2,0)
    forward=source.bounds('A_model',0,2)
    assert reflected[0].transpose()==forward[0] and reflected[1].transpose()==forward[1]
    assert source.consumed
    source.context['endpoint_bits']=8
    with pytest.raises(ContractError,match='endpoint'):
        source.bounds('A_model',0,0)


@pytest.mark.parametrize('change',['bytes','deleted'])
def test_cached_source_keeps_original_raw_dependency_checks(tmp_path,change):
    panels=source_panels(tmp_path)
    source=exact.SourceIntegers(panels.reader,context())
    source.bounds('A_model',0,0)
    row=next(row for row in panels.reader.document['tiles'] if row['family']=='A_model')
    path=tmp_path/row['artifact']['path']
    if change=='bytes':path.write_bytes(b'changed after source decode')
    else:path.unlink()
    with pytest.raises((ContractError,OSError)):
        source.bounds('A_model',0,0)


def test_refused_retention_computes_real_integers_without_exceeding_allowance(tmp_path,monkeypatch):
    store=integer_store(tmp_path)
    store.decoded=WorkingSet(4096)
    calls=[]
    original=exact._json
    def decoded(raw):
        calls.append(1)
        return original(raw)
    monkeypatch.setattr(exact,'_json',decoded)
    assert store.tile(0,0)==store.tile(0,0)
    assert len(calls)==2 and not store.decoded.values
    assert store.decoded.peak<=store.decoded.limit


def test_exact_account_prices_each_simultaneous_decode_store():
    c=context()
    parameters=exact.paid_parameters(256,Fraction(3,2),Fraction(7,8))
    account=exact.integer_bounds(c,parameters,Fraction(1,1024))
    assert account['private_bytes']>=16*1024**2+3*PANEL_DECODED_BYTES
