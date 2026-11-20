"""Bounded working-set eviction and actual persisted source consumption."""
from dataclasses import asdict
from fractions import Fraction
from tempfile import TemporaryDirectory

import pytest
from flint import ctx
from scripts.whole_source import pipeline
from scripts.whole_source.artifacts import CollectionLock,ChunkStore,IntervalRecord,ArtifactError
from scripts.whole_source.contract import ROOT,ContractError,bind_problem
from scripts.whole_source.reuse import WorkingSet,python_bytes


def test_eviction_retains_the_current_value_without_exceeding_allowance():
    cache=WorkingSet(8192).bind(('role',1))
    cache.put(('a',),(7,11),1200)
    cache.put(('b',),(13,17),1200)
    assert sum(cache.get(('a',)))==18
    cache.put(('c',),(19,23),1200)
    assert cache.get(('b',)) is None
    assert sum(cache.get(('a',)))==18 and sum(cache.get(('c',)))==42
    assert cache.resident<=cache.peak<=cache.limit
    cache.bind(('role',2))
    assert cache.get(('a',)) is None
    assert cache.resident==4096


def test_overlarge_value_is_returned_but_never_retained():
    cache=WorkingSet(8192)
    assert cache.put(('big',),(29,31),8192)==(29,31)
    assert cache.get(('big',)) is None
    assert cache.resident==4096
    with pytest.raises(TypeError):
        python_bytes(object())


@pytest.fixture
def source_store(tmp_path):
    # Real bounded collection and dyadic artifacts, no fabricated source acceptance.
    with TemporaryDirectory(prefix='source-reuse-',dir=ROOT/'.pytest_cache') as folder:
        paths=pipeline.prepare_source_inputs(bind_problem('retained-t081'),folder+'/inputs',
            origin_git_commit='cf1e25303b290448aac968eb9527fa327e496f02',origin_git_dirty=True,
            control=True,tile_modes=2)
        _,_,roles=pipeline._bind(paths['problem'],paths['execution'],ROOT)
        spec=roles['producer'][0]
        with CollectionLock.acquire(tmp_path/'collection',spec) as lock:
            (lock.root/'attempts/unit').mkdir()
            lock.register_attempt('unit')
            yield lock,ChunkStore(lock,spec,attempt_id='unit')


def test_cached_source_column_still_hashes_bytes_and_checks_domain(source_store,monkeypatch):
    lock,store=source_store
    domain=pipeline._column_task(lock.spec,'F_column',0)
    records=[IntervalRecord(m,0,(0,),Fraction(m+1,8),Fraction(m+2,8)) for m in domain.rows]
    ref=store.publish_chunk(domain,store.stage_chunk(domain,records))
    context=store.staging_context()
    cache=WorkingSet(1024*1024).bind(('disposable',str(lock.root)))
    monkeypatch.setattr(pipeline,'_COLUMN_VALUES',cache)
    calls=[]
    decode=pipeline._decode_chunk
    def decoded(*args,**kwargs):
        calls.append(1)
        return decode(*args,**kwargs)
    monkeypatch.setattr(pipeline,'_decode_chunk',decoded)
    with ctx.workprec(512):
        first=pipeline._column(context,'F_column',0,asdict(ref),keep=True)
        second=pipeline._column(context,'F_column',0,asdict(ref),keep=True)
        assert all(a.mid()==b.mid() and a.rad()==b.rad() for a,b in zip(first,second,strict=True))
        assert len(calls)==1 and cache.hits==1
        with pytest.raises(ContractError,match='domain'):
            pipeline._column(context,'F_column',2,asdict(ref),keep=True)
        (lock.root/ref.path).write_bytes(b'changed after valid reuse')
        with pytest.raises(ArtifactError):
            pipeline._column(context,'F_column',0,asdict(ref),keep=True)
