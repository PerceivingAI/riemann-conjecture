"""Complete panel contractions, row scaling and nonproof transform coverage."""
from fractions import Fraction
import hashlib
from pathlib import Path

import pytest
from flint import arb, arb_mat, ctx, fmpq, fmpq_mat

from scripts.whole_source.contract import ContractError, bind_problem, canonical_bytes, problem_id
from scripts.whole_source.proposal import (
    BITS, SCOPE, PanelStore, blocked_cholesky, triangular_solve, whiten_tiles, read_proposal,
)


def context(n=5,b=2):
    return {'proposal_id':'a'*64,'problem_id':'b'*64,'source_sha256':'c'*64,
            'dimension':n,'panel_size':b,'precision_bits':BITS,'grid_bits':BITS,'transform_bits':80,'parity':0}


def panel(matrix,i,j,c):
    b,n = c['panel_size'],c['dimension']
    return arb_mat([[matrix[r,k] for k in range(j,min(j+b,n))] for r in range(i,min(i+b,n))])


def full(store,prefix):
    n,b = store.context['dimension'],store.context['panel_size']
    result = arb_mat(n,n)
    for i in range(0,n,b):
        for j in range(0,n,b):
            name = f'{prefix}/{i}/{j}'
            if name not in store.refs:
                continue
            value = store.native(name)
            for r in range(value.nrows()):
                for c in range(value.ncols()):
                    result[i+r,j+c] = value[r,c]
    return result


def exact_factor(n):
    result = fmpq_mat(n,n)
    for i in range(n):
        scale = fmpq(1,1 << (3*i))
        result[i,i] = scale*(i+2)
        for j in range(i):
            result[i,j] = scale*fmpq((-1)**(i+j)*(i+j+1),8)
    return result


def close_to_exact(actual,expected,bits=850):
    for i in range(actual.nrows()):
        for j in range(actual.ncols()):
            assert actual[i,j].contains(arb(expected[i,j]))
            assert (actual[i,j]-arb(expected[i,j])).abs_upper() < arb(2)**-bits


@pytest.mark.parametrize('width',[1,2,4])
def test_row_scaled_ragged_factor_reconstructs_every_cross_update(tmp_path,width):
    c = context(b=width)
    store = PanelStore(tmp_path,c)
    factor = exact_factor(c['dimension'])
    matrix = factor*factor.transpose()
    with ctx.workprec(BITS):
        minimum = blocked_cholesky(lambda i,j:panel(matrix,i,j,c),store)
        actual = full(store,'L')
        assert minimum > 0
        close_to_exact(actual,factor)
        close_to_exact(actual*actual.transpose(),matrix)
        # The literal block-diagonal substitute misses nonzero cross panels.
        omitted = arb_mat(actual.nrows(),actual.ncols())
        for i in range(actual.nrows()):
            for j in range(actual.ncols()):
                if i//width == j//width:
                    omitted[i,j] = actual[i,j]
        assert not (omitted*omitted.transpose()-arb_mat(matrix))[4,0].contains(0)


@pytest.mark.parametrize('width',[2,3])
@pytest.mark.parametrize('transpose',[False,True])
def test_full_forward_and_back_solve_pay_all_previous_panels(tmp_path,width,transpose):
    c = context(b=width)
    store = PanelStore(tmp_path,c)
    factor = exact_factor(c['dimension'])
    rhs = fmpq_mat([[fmpq((i+1)*(j+2)+(-1)**(i+j),16) for j in range(5)] for i in range(5)])
    with ctx.workprec(BITS):
        blocked_cholesky(lambda i,j:panel(factor*factor.transpose(),i,j,c),store)
        triangular_solve(store,lambda i,j:panel(rhs,i,j,c),store,'W',transpose=transpose)
        result = full(store,'W')
        operator = factor.transpose() if transpose else factor
        close_to_exact(arb_mat(operator)*result,rhs)
        close_to_exact(result,operator.inv()*rhs)


@pytest.mark.parametrize('width',[2,4])
def test_two_sided_whitening_is_not_one_sided_or_an_inverse_transpose_mixup(tmp_path,width):
    c = context(b=width)
    store = PanelStore(tmp_path,c)
    factor = exact_factor(5)
    a = factor*factor.transpose()
    image = fmpq_mat([[fmpq((i+2)*(j+2)+(3 if i==j else 0),64) for j in range(5)] for i in range(5)])
    with ctx.workprec(BITS):
        blocked_cholesky(lambda i,j:panel(a,i,j,c),store)
        whiten_tiles(lambda i,j:panel(image,i,j,c),store,'H')
        expected = factor.inv()*image*factor.inv().transpose()
        actual = full(store,'H')
        close_to_exact(actual,expected)
        assert not (actual-arb_mat(factor.inv()*image))[4,0].contains(0)
        for i in range(5):
            for j in range(5):
                assert (actual[i,j]-actual[j,i]).contains(0)


@pytest.mark.parametrize('diagonal',[0,-1])
def test_nonpositive_pivot_never_becomes_a_fallback_factor(tmp_path,diagonal):
    c = context(n=3,b=2)
    store = PanelStore(tmp_path,c)
    matrix = arb_mat([[2,1,0],[1,2,0],[0,0,diagonal]])
    with ctx.workprec(BITS),pytest.raises(ContractError,match='pivot'):
        blocked_cholesky(lambda i,j:panel(matrix,i,j,c),store)
    assert 'L/2/2' not in store.refs


def proposal_fixture(tmp_path):
    problem = bind_problem('retained-t081')
    source = {'path':'source.json','sha256':'c'*64,'size':123}
    policy = {'native_bits':BITS,'working_grid_bits':BITS,'transform_bits':80,
              'theta_bits':40,'panel_size':2,'logtheta_bounds':[-20,20]}
    from scripts.whole_source.execution import _RUNTIME
    root = Path(__file__).resolve().parents[1]
    code = []
    for name in sorted((*_RUNTIME,'scripts/whole_source/proposal.py','scripts/whole_source/proposal_float.py')):
        raw = (root/name).read_bytes()
        code.append({'path':name,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    identity = hashlib.sha256(canonical_bytes({'problem_id':problem_id(problem),
        'source':source,'policy':policy,'code':code})).hexdigest()
    blocks = []
    for p in (0,1):
        c = {'proposal_id':identity,'problem_id':problem_id(problem),'source_sha256':source['sha256'],
             'dimension':3,'panel_size':2,'precision_bits':BITS,'grid_bits':BITS,'transform_bits':80,'parity':p}
        store = PanelStore(tmp_path,c)
        panels = []
        for i in (0,2):
            for j in (0,2):
                name = f'Z/{i}/{j}'
                store.put(name,'integer',[hex((r+1)*(k+2)+int(r==k))
                    for r in range(i,min(i+2,3)) for k in range(j,min(j+2,3))])
                panels.append({'row':i,'column':j,'artifact':store.refs[name]})
        blocks.append({'parity':p,'dimension':3,'u':80,'theta':'3/2','context':c,
                       'integer_panels':panels,'inherited_coordinates_used':False})
    diagnostic = b'{}\n'
    (tmp_path/'diagnostics.json').write_bytes(diagnostic)
    core = {'format':'whole-source-congruence-proposal-v1','status':'NONPROOF_ONLY','scope':SCOPE,
        'problem_id':problem_id(problem),'source':source,'source_directory_at_execution':'fixture',
        'source_control':True,'policy':policy,'code':code,
        'backend_versions':{'native':'fixture-native','floating':'fixture-floating'},
        'diagnostics':{'path':'diagnostics.json','sha256':hashlib.sha256(diagnostic).hexdigest(),'size':len(diagnostic)},
        'blocks':blocks,'analytical_acceptance':False,'matrix_positivity':False,'production_admission':False}
    return problem,source,core


def test_full_dyadic_transform_reader_checks_all_rows_and_both_parities(tmp_path):
    problem,source,core = proposal_fixture(tmp_path)
    path = tmp_path/'proposal.json'
    path.write_bytes(canonical_bytes(core))
    read_proposal(path,problem,source)
    core['blocks'][1]['integer_panels'].pop()
    path.write_bytes(canonical_bytes(core))
    with pytest.raises(ContractError,match='coordinate panels'):
        read_proposal(path,problem,source)


def test_declared_smaller_transform_cannot_replace_bound_physical_dimension(tmp_path):
    problem,source,core = proposal_fixture(tmp_path)
    core['blocks'][0]['dimension'] = 0
    core['blocks'][0]['context']['dimension'] = 0
    core['blocks'][0]['integer_panels'] = []
    path = tmp_path/'proposal.json'
    path.write_bytes(canonical_bytes(core))
    with pytest.raises(ContractError,match='proposal block'):
        read_proposal(path,problem,source)
