"""Literal independent rational products and every bounded symmetric interval vertex."""
from fractions import Fraction as Q
from itertools import product

import pytest
from flint import fmpz_mat

from scripts.whole_source.exact import (
    IntegerTiles, integer_bounds, paid_parameters, paid_integer_tiles,
    integer_congruence, numerical_width,
)
from scripts.whole_source.exact_global import mass_trace, assess


def transpose(a):
    return [list(row) for row in zip(*a,strict=True)]


def multiply(a,b):
    return [[sum((x*y for x,y in zip(row,col,strict=True)),Q(0)) for col in transpose(b)] for row in a]


class Source:
    bits = 4

    def __init__(self,midpoints,radii,panel):
        self.midpoints,self.radii,self.panel = midpoints,radii,panel
        self.n = len(midpoints['A_model'])

    def bounds(self,family,i,j):
        return tuple(fmpz_mat([[self.midpoints[family][r][c]+sign*self.radii[family][r][c]
            for c in range(j,min(j+self.panel,self.n))] for r in range(i,min(i+self.panel,self.n))])
            for sign in (-1,1))


def fixture(tmp_path,parity=0,panel=2):
    centers = {'A_model':[[160,24,-8],[24,144,12],[-8,12,128]],
               'weighted_head':[[8,-2,1],[-2,12,2],[1,2,4]],
               'weighted_complete_tail':[[5,1,-1],[1,6,0],[-1,0,7]]}
    radii = {name:[[1 if i==j or i+j==2 else 0 for j in range(3)] for i in range(3)] for name in centers}
    source = Source(centers,radii,panel)
    z = [[2,1,-1],[1,2,1],[-1,0,2]]
    context = {'problem_id':'a'*64,'source_sha256':'b'*64,'proposal_sha256':'c'*64,
        'parity':parity,'dimension':3,'panel_size':panel,'u':2,'endpoint_bits':9,'z_bits':2}
    params = paid_parameters(4,Q(3,2),Q(5,7))
    context['product_bits'] = integer_bounds(context,params,Q(3,17))['product_bits']
    transforms = IntegerTiles(tmp_path/'z',context)
    for i in range(0,3,panel):
        for j in range(0,3,panel):
            transforms.put_values('Z',i,j,[z[r][c] for r in range(i,min(i+panel,3)) for c in range(j,min(j+panel,3))])
    store = IntegerTiles(tmp_path/'products',context)
    masses = mass_trace(3,parity,2,panel,transforms.tile)
    report = integer_congruence(source,transforms,store,params,masses,Q(3,17))
    return source,z,context,params,masses,report


def literal(source,z,parity):
    theta,eta,lam = Q(3,2),Q(5,7),Q(3,17)
    head,tail = (1+theta)/eta,(1+1/theta)/eta
    low,high = [],[]
    for i in range(3):
        lower,upper = [],[]
        for j in range(3):
            def endpoint(name,sign):
                return Q(source.midpoints[name][i][j]+sign*source.radii[name][i][j],16)
            lower.append(endpoint('A_model',-1)-head*endpoint('weighted_head',1)-tail*endpoint('weighted_complete_tail',1))
            upper.append(endpoint('A_model',1)-head*endpoint('weighted_head',-1)-tail*endpoint('weighted_complete_tail',-1))
        low.append(lower)
        high.append(upper)
    center = [[(low[i][j]+high[i][j])/2 for j in range(3)] for i in range(3)]
    radius = [[(high[i][j]-low[i][j])/2 for j in range(3)] for i in range(3)]
    d = [Q(2,2*(2*i+parity)+1) for i in range(3)]
    paid = [[center[i][j]-(lam*d[i] if i==j else 0) for j in range(3)] for i in range(3)]
    u = [[Q(x,4) for x in row] for row in z]
    absolute = [[abs(x) for x in row] for row in u]
    b = multiply(multiply(transpose(u),paid),u)
    e = multiply(multiply(transpose(absolute),radius),absolute)
    margins = [b[i][i]-sum(abs(b[i][j]) for j in range(3) if i!=j)-sum(e[i]) for i in range(3)]
    upperdirs = [b[i][i]+e[i][i] for i in range(3)]
    tau = sum(d[i]*sum(x*x for x in u[i]) for i in range(3))
    return low,high,center,radius,u,b,e,margins,upperdirs,tau,d


@pytest.mark.parametrize('parity',[0,1])
@pytest.mark.parametrize('panel',[1,2])
def test_full_rational_congruence_all_inner_rows_radii_and_physical_mass(tmp_path,parity,panel):
    source,z,context,params,masses,report = fixture(tmp_path,parity,panel)
    _,_,_,radius,u,b,e,margins,upperdirs,tau,d = literal(source,z,parity)
    assert params['Q'] % 3 == 0  # The non-dyadic Young denominator is paid.
    assert report['row_margins'] == margins
    assert report['margin'] == min(margins)
    assert report['tau'] == tau == masses['tau']
    assert report['width'] == max(sum(row) for row in radius)/min(d)
    worst = min(range(3),key=lambda i:upperdirs[i])
    assert report['direction_index'] == worst
    assert report['direction_upper'] == upperdirs[worst]
    assert report['direction_mass'] == sum(d[i]*u[i][worst]**2 for i in range(3))
    assert report['transformed_upper_entries'] == 6


@pytest.mark.parametrize('parity',[0,1])
def test_all_symmetric_interval_vertices_are_paid_even_with_signed_transform(tmp_path,parity):
    source,z,context,params,masses,report = fixture(tmp_path,parity)
    low,high,center,radius,u,b,e,_,_,_,d = literal(source,z,parity)
    signed_radius = multiply(multiply(transpose(u),radius),u)
    upper_coordinates = [(i,j) for i in range(3) for j in range(i,3)]
    escaped_wrong_abs = False
    for choices in product((0,1),repeat=len(upper_coordinates)):
        vertex = [[Q(0) for _ in range(3)] for _ in range(3)]
        for bit,(i,j) in zip(choices,upper_coordinates,strict=True):
            vertex[i][j] = vertex[j][i] = (high if bit else low)[i][j]
        for i in range(3):
            vertex[i][i] -= Q(3,17)*d[i]
        value = multiply(multiply(transpose(u),vertex),u)
        for i in range(3):
            for j in range(3):
                assert b[i][j]-e[i][j] <= value[i][j] <= b[i][j]+e[i][j]
                escaped_wrong_abs |= not (b[i][j]-signed_radius[i][j] <= value[i][j] <= b[i][j]+signed_radius[i][j])
    assert escaped_wrong_abs


def test_off_diagonal_row_updates_prevent_false_diagonal_positivity(tmp_path):
    centers = {'A_model':[[16,32],[32,16]],'weighted_head':[[0,0],[0,0]],'weighted_complete_tail':[[0,0],[0,0]]}
    source = Source(centers,{name:[[0,0],[0,0]] for name in centers},1)
    context = {'dimension':2,'panel_size':1,'u':0,'parity':0,'endpoint_bits':6,'z_bits':1,
               'problem_id':'a'*64,'source_sha256':'b'*64,'proposal_sha256':'c'*64}
    params = paid_parameters(4,Q(1),Q(1))
    context['product_bits'] = integer_bounds(context,params,Q(0))['product_bits']
    z = IntegerTiles(tmp_path/'z',context)
    for i in range(2):
        for j in range(2): z.put_values('Z',i,j,[int(i==j)])
    masses = mass_trace(2,0,0,1,z.tile)
    result = integer_congruence(source,z,IntegerTiles(tmp_path/'p',context),params,masses,Q(0))
    assert result['row_margins'] == [Q(-1),Q(-1)]
    assert result['direction_upper'] == 1
    block = {name:result[name] for name in ('width','margin','tau','direction_upper','direction_mass','direction_index')}
    block.update(goal=Q(1),modular_nonsingular=True)
    assert assess([block,block],eta=Q(1),m=Q(1),b_K=Q(0),delta=Q(0))['status']=='UNRESOLVED_PAID_LOWER'


def test_width_equality_and_one_grid_unit_above_are_distinct():
    equal = numerical_width([1,0],16,Q(1,2))
    above = numerical_width([2,0],16,Q(1,2))
    assert equal == Q(1,8)
    assert above > equal
    block = {'width':equal,'goal':equal,'modular_nonsingular':True,'margin':Q(1),'tau':Q(1),
             'direction_upper':Q(1),'direction_mass':Q(1),'direction_index':0}
    assert assess([block,block],eta=Q(1),m=Q(1),b_K=Q(0),delta=Q(0))['positive_paid_lower']
    assert assess([{**block,'width':above},block],eta=Q(1),m=Q(1),b_K=Q(0),delta=Q(0))['status']=='WIDTH_GOAL_FAILED'


@pytest.mark.parametrize('parity',[0,1])
def test_paid_negative_direction_uses_actual_lambda_and_physical_mass(tmp_path,parity):
    centers = {'A_model':[[16,0],[0,64]],'weighted_head':[[0,0],[0,0]],
               'weighted_complete_tail':[[0,0],[0,0]]}
    source = Source(centers,{name:[[0,0],[0,0]] for name in centers},1)
    context = {'dimension':2,'panel_size':1,'u':0,'parity':parity,'endpoint_bits':7,'z_bits':1,
               'problem_id':'a'*64,'source_sha256':'b'*64,'proposal_sha256':'c'*64}
    params,lam = paid_parameters(4,Q(1),Q(1)),Q(3)
    context['product_bits'] = integer_bounds(context,params,lam)['product_bits']
    z = IntegerTiles(tmp_path/'z',context)
    for i in range(2):
        for j in range(2): z.put_values('Z',i,j,[int(i==j)])
    masses = mass_trace(2,parity,0,1,z.tile)
    result = integer_congruence(source,z,IntegerTiles(tmp_path/'p',context),params,masses,lam)
    mass = Q(2,2*parity+1)
    assert result['direction_index'] == 0
    assert result['direction_mass'] == mass
    assert result['direction_upper'] == 1-lam*mass < 0
    block = {name:result[name] for name in ('width','margin','tau','direction_upper','direction_mass','direction_index')}
    block.update(goal=Q(1),modular_nonsingular=True)
    verdict = assess([block,block],eta=Q(1),m=Q(1),b_K=Q(0),delta=Q(0))
    assert verdict['status'] == 'SELECTED_PAID_LOWER_NEGATIVE_NOT_WEIL_NEGATIVITY'
    assert verdict['gamma'] is None
