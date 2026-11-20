"""Persisted proposal operands stay authoritative during bounded decode reuse."""
from collections import Counter
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
import subprocess
import sys
from types import SimpleNamespace

import pytest
from flint import arb, arb_mat, ctx, fmpq, fmpq_mat

from scripts.whole_source import artifacts, execution, proposal
from scripts.whole_source.contract import ArtifactRef, ContractError, ROOT, QuantityKey, bind_problem, canonical_bytes
from scripts.whole_source.pipeline import FAMILIES, _partition, _quantities, _tiles
from scripts.whole_source.reuse import PANEL_DECODED_BYTES, WorkingSet, python_bytes


def context(n=5, b=2, parity=0):
    return {'proposal_id':'a'*64,'problem_id':'b'*64,'source_sha256':'c'*64,
            'dimension':n,'panel_size':b,'precision_bits':proposal.BITS,
            'grid_bits':proposal.BITS,'transform_bits':80,'parity':parity}


def panel(matrix, i, j, c):
    n,b = c['dimension'],c['panel_size']
    return arb_mat([[matrix[r,k] for k in range(j,min(j+b,n))]
                    for r in range(i,min(i+b,n))])


def same(left, right):
    assert (left.nrows(),left.ncols()) == (right.nrows(),right.ncols())
    for r in range(left.nrows()):
        for c in range(left.ncols()):
            assert left[r,c].mid() == right[r,c].mid()
            assert left[r,c].rad() == right[r,c].rad()


def replace_ref(root, ref, document):
    raw = canonical_bytes(document)
    path = root/ref['path']
    path.write_bytes(raw)
    return asdict(ArtifactRef(ref['path'],hashlib.sha256(raw).hexdigest(),len(raw)))


@pytest.mark.parametrize('width',[1,2,3])
def test_factor_whitening_and_backsolve_reuse_paid_decodes(tmp_path, monkeypatch, width):
    c = context(b=width)
    factor = fmpq_mat([[fmpq(i+3) if i == j else (fmpq((-1)**(i+j),8) if i > j else 0)
                        for j in range(5)] for i in range(5)])
    a = factor*factor.transpose()
    rhs = fmpq_mat([[fmpq((i+1)*(j+2)+(i == j),16) for j in range(5)] for i in range(5)])
    original = proposal._json
    counts = Counter()
    def counted(raw):
        counts[hashlib.sha256(raw).hexdigest()] += 1
        return original(raw)
    monkeypatch.setattr(proposal,'_json',counted)
    results = []
    totals = []
    with ctx.workprec(proposal.BITS):
        for index, limit in enumerate((PANEL_DECODED_BYTES,4096)):
            root = tmp_path/str(index)
            root.mkdir()
            store = proposal.PanelStore(root,c)
            store.decoded = WorkingSet(limit)
            counts.clear()
            proposal.blocked_cholesky(lambda i,j:panel(a,i,j,c),store)
            proposal.whiten_tiles(lambda i,j:panel(rhs,i,j,c),store,'H')
            proposal.triangular_solve(store,lambda i,j:panel(rhs,i,j,c),store,'W',transpose=True)
            matrices = {name:store.native(name) for name in store.refs}
            results.append(matrices)
            totals.append(sum(counts.values()))
            if limit == PANEL_DECODED_BYTES:
                assert counts and max(counts.values()) == 1
                assert store.decoded.hits > 0
            assert store.decoded.peak <= limit
        assert totals[0] < totals[1]
        for name in results[0]:
            same(results[0][name],results[1][name])


def test_native_cache_saves_hex_decodes_without_changing_public_lists(tmp_path, monkeypatch):
    store = proposal.PanelStore(tmp_path,context(n=2,b=2))
    calls = []
    original = proposal.decode_integer
    def counted(value,bits):
        calls.append(value)
        return original(value,bits)
    monkeypatch.setattr(proposal,'decode_integer',counted)
    with ctx.workprec(proposal.BITS):
        store.put_native('L/0/0',arb_mat([[fmpq(1,3),0],[fmpq(-2,7),2]]))
        first = store.native('L/0/0')
        expected = store.native('L/0/0')
        assert len(calls) == 8
        first[0,0] = 900
        same(store.native('L/0/0'),expected)
        values = store.read('L/0/0','interval')
        assert type(values) is list and all(type(pair) is list for pair in values)
        values[0][0] = '0x0'
        assert store.read('L/0/0','interval')[0][0] != '0x0'
        assert len(calls) == 8
        cached = next(iter(store.decoded.values.values()))[0]
        assert type(cached) is tuple and all(type(pair) is tuple for pair in cached)
        assert all(type(x) is int for pair in cached for x in pair)


def test_float_vectors_reuse_exact_ratios_and_return_fresh_matrices(tmp_path, monkeypatch):
    store = proposal.PanelStore(tmp_path,context(n=2,b=2))
    values = [x.hex() for x in (0.0,-0.0,0.1,-2.5)]
    store.put('V/0/0','binary64',values)
    calls = []
    class CountFloat(float):
        @classmethod
        def fromhex(cls,value):
            calls.append(value)
            return float.fromhex(value)
    monkeypatch.setattr(proposal,'float',CountFloat,raising=False)
    first = store.vectors('V/0/0')
    expected = store.vectors('V/0/0')
    first[1,0] = 12
    same(store.vectors('V/0/0'),expected)
    assert calls == values
    assert store.read('V/0/0','binary64') == values


def test_new_factor_store_rereads_the_paid_rounding(tmp_path):
    c = context(n=1,b=1)
    store = proposal.PanelStore(tmp_path,c)
    with ctx.workprec(proposal.BITS+128):
        unpublished = arb_mat([[arb(2).sqrt()]])
        store.put_native('L/0/0',unpublished)
        assert not store.decoded.values
        paid = store.native('L/0/0')
        reread = proposal.PanelStore(tmp_path,c,store.refs).native('L/0/0')
        same(paid,reread)
        assert paid[0,0].rad() > unpublished[0,0].rad()
        unpublished[0,0] = 7
        same(store.native('L/0/0'),reread)


@pytest.mark.parametrize('change',['bytes','deleted','header','context','path'])
def test_cached_panels_still_check_every_bound_artifact(tmp_path,change):
    store = proposal.PanelStore(tmp_path,context(n=1,b=1))
    store.put_native('L/0/0',arb_mat([[3]]))
    store.native('L/0/0')
    ref = store.refs['L/0/0']
    path = tmp_path/ref['path']
    if change == 'bytes':
        path.write_bytes(path.read_bytes().replace(b'NONPROOF_ONLY',b'NONPROOF_ONLX'))
    elif change == 'deleted':
        path.unlink()
    elif change == 'header':
        document = json.loads(path.read_bytes())
        document['header']['grid_bits'] += 1
        store.refs['L/0/0'] = replace_ref(tmp_path,ref,document)
    elif change == 'context':
        store.context['proposal_id'] = 'd'*64
    else:
        store.refs['L/0/0'] = dict(ref,path='../outside')
    with pytest.raises((ContractError,OSError)):
        store.native('L/0/0')


def source_panels(tmp_path, parity=0):
    problem = bind_problem('retained-t081')
    bounds = artifacts.CodecBounds(8*1024**2,1024**2,8*1024**2,16384,8192,
                                  256*1024,64*1024,256*1024**2,16*1024**2,64*1024**2)
    paths = ('scripts/whole_source/__init__.py','scripts/whole_source/artifacts.py',
             'scripts/whole_source/contract.py','scripts/run_observability.py')
    refs = tuple(ArtifactRef(path,hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),
                            (ROOT/path).stat().st_size) for path in sorted(paths))
    spec = artifacts.CollectionSpec.create(problem,role='producer',quantities=_quantities(problem,True),
        partition=_partition(problem,True,2),backend='CONTROL_ONLY-exact-polynomial',backend_version='1',
        native_threads=1,code_refs=refs,bounds=bounds)
    bits = problem.arithmetic.publication_bits
    tiles = []
    for family,name in FAMILIES.items():
        for task in _tiles(spec,QuantityKey(name,parity)):
            records = [[m,n,hex((m+n+3)*(1 << bits)-1),hex((m+n+3)*(1 << bits)+1)]
                       for m,n in artifacts._coordinates(task,True)]
            raw = canonical_bytes({'header':artifacts._publication_header(spec,task,bits),'records':records})
            path = str(len(tiles))+'.json'
            (tmp_path/path).write_bytes(raw)
            tiles.append({'family':family,'parity':parity,'task':task.to_dict(),
                          'artifact':asdict(ArtifactRef(path,hashlib.sha256(raw).hexdigest(),len(raw)))})
    reader = SimpleNamespace(path=tmp_path/'source-manifest.json',spec=spec,bits=bits,document={'tiles':tiles})
    return proposal.SourcePanels(reader,context(n=3,b=2,parity=parity))


@pytest.mark.parametrize('parity',[0,1])
def test_source_traversal_reuses_publications_across_ragged_reflection(tmp_path,monkeypatch,parity):
    source = source_panels(tmp_path,parity)
    calls = Counter()
    hex_calls = []
    decode_integer = artifacts.decode_integer
    def counted_hex(value,bits):
        hex_calls.append(value)
        return decode_integer(value,bits)
    monkeypatch.setattr(artifacts,'decode_integer',counted_hex)
    original = artifacts.publication_integers
    def counted(spec,raw,task,bits):
        calls[hashlib.sha256(raw).hexdigest()] += 1
        return original(spec,raw,task,bits)
    monkeypatch.setattr(artifacts,'publication_integers',counted)
    with ctx.workprec(proposal.BITS):
        first = source.matrix('weighted_head',0,2)
        reflected = source.matrix('weighted_head',2,0)
        same(first.transpose(),reflected)
        first[0,0] = -90
        same(source.matrix('weighted_head',0,2).transpose(),reflected)
        assert sum(calls.values()) == 1
        for family in FAMILIES:
            for i in (0,2):
                for j in (0,2):
                    actual = source.matrix(family,i,j)
                    for r in range(actual.nrows()):
                        for c in range(actual.ncols()):
                            m,n = 2*(i+r)+parity,2*(j+c)+parity
                            expected = Fraction(m+n+3)
                            grid = 1 << source.reader.bits
                            lower = Fraction((m+n+3)*grid-1,grid)
                            upper = Fraction((m+n+3)*grid+1,grid)
                            middle,radius = (lower+upper)/2,(upper-lower)/2
                            legacy = arb(fmpq(middle.numerator,middle.denominator),
                                         arb(fmpq(radius.numerator,radius.denominator)))
                            if family == 'A_model' and m == n:
                                expected -= source.reader.spec.problem.model_error*Fraction(2,2*m+1)
                                paid = source.reader.spec.problem.model_error*Fraction(2,2*m+1)
                                legacy -= arb(fmpq(paid.numerator,paid.denominator))
                            elif family != 'A_model':
                                expected /= source.reader.spec.problem.eta
                                eta = source.reader.spec.problem.eta
                                legacy /= arb(fmpq(eta.numerator,eta.denominator))
                            assert actual[r,c].contains(arb(fmpq(expected.numerator,expected.denominator)))
                            assert actual[r,c].mid() == legacy.mid()
                            assert actual[r,c].rad() == legacy.rad()
        assert max(calls.values()) == 1
        assert source.decoded.hits > 0
        assert source.decoded.peak <= PANEL_DECODED_BYTES
        assert len(hex_calls) == 36


def test_source_refuses_unadmitted_decode_retention(tmp_path,monkeypatch):
    source = source_panels(tmp_path)
    source.decoded = WorkingSet(4096)
    original = artifacts.publication_integers
    calls = []
    def counted(*args):
        assert not source.decoded.values
        calls.append(1)
        return original(*args)
    monkeypatch.setattr(artifacts,'publication_integers',counted)
    same(source.matrix('A_model',0,0),source.matrix('A_model',0,0))
    assert len(calls) == 2
    assert source.decoded.peak == 4096


@pytest.mark.parametrize('change',['bytes','deleted','header','bits','task'])
def test_cached_source_tiles_keep_raw_and_header_validation(tmp_path,change):
    source = source_panels(tmp_path)
    source.matrix('A_model',0,0)
    row = source.index['A_model',0,0,0]
    ref = row['artifact']
    path = tmp_path/ref['path']
    if change == 'bytes':
        path.write_bytes(path.read_bytes().replace(b'floor-minus-one',b'floor-minus-two'))
    elif change == 'deleted':
        path.unlink()
    elif change == 'header':
        document = json.loads(path.read_bytes())
        document['header']['scientific_id'] = 'd'*64
        row['artifact'] = replace_ref(tmp_path,ref,document)
    elif change == 'bits':
        source.reader.bits += 1
    else:
        row['task']['quantity']['name'] = 'head_complete'
    with pytest.raises((ContractError,OSError)):
        source.matrix('A_model',0,0)


def test_reservation_evicts_before_parsing_and_refuses_large_panels(tmp_path,monkeypatch):
    store = proposal.PanelStore(tmp_path,context(n=2,b=1))
    for name in ('L/0/0','L/1/0'):
        store.put_native(name,arb_mat([[fmpq(1,3)]]))
    # Each candidate's reservation fits, but overlaps an existing decoded entry.
    raw = (tmp_path/store.refs['L/0/0']['path']).read_bytes()
    header = canonical_bytes(store._header('L/0/0','interval'))
    ref = store.refs['L/0/0']
    key = (str(tmp_path.absolute()),ref['path'],ref['sha256'],ref['size'],header)
    estimate = 4*len(raw)+256+4096
    limit = 4096+estimate+512+python_bytes(key)
    store.decoded = WorkingSet(limit)
    original = proposal._json
    observed = []
    def parsing(raw):
        observed.append(len(store.decoded.values))
        return original(raw)
    monkeypatch.setattr(proposal,'_json',parsing)
    store.native('L/0/0')
    store.native('L/1/0')
    store.native('L/0/0')
    assert observed == [0,0,0]
    assert store.decoded.peak <= limit
    store.decoded = WorkingSet(4096)
    store.native('L/0/0')
    store.native('L/0/0')
    assert not store.decoded.values
    assert store.decoded.peak == 4096


def test_owned_callback_rejects_underpriced_reuse_before_source_access(tmp_path,monkeypatch):
    c = context()
    plan = SimpleNamespace(role='proposal',scope=proposal.SCOPE,worker_private_mib=1)
    staging = SimpleNamespace(root=tmp_path,_check=lambda:None)
    monkeypatch.setattr(execution,'_WORKER',(plan,staging))
    monkeypatch.setattr(proposal,'_reader',lambda *args:pytest.fail('source opened before admission'))
    with pytest.raises(ContractError,match='admitted account'):
        proposal.evaluate_proposal({'context':c,'operation':'factor-whiten'},staging)
    accounts = proposal._proposal_accounts(5,2)
    assert accounts['native_working_bytes'] >= 3*PANEL_DECODED_BYTES+32*1024**2
    assert accounts['floating_working_bytes'] >= 3*PANEL_DECODED_BYTES+32*1024**2


def test_importing_proposal_keeps_both_numerical_backends_unloaded():
    code = "import sys; import scripts.whole_source.proposal; assert 'flint' not in sys.modules; assert 'numpy' not in sys.modules"
    subprocess.run([sys.executable,'-c',code],cwd=ROOT,check=True,capture_output=True)
