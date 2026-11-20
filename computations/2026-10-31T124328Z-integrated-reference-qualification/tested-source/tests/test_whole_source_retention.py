"""Full-domain consequence checks, independent of successful driver metadata."""
from fractions import Fraction as Q
from types import SimpleNamespace
import pytest
from scripts.whole_source.contract import ContractError, canonical_bytes
from scripts.whole_source.retention import reviewed_consequence, _seal, verify_inventory
import json


def rational(value):
    value = Q(value)
    return {'numerator':hex(value.numerator),'denominator':hex(value.denominator)}


def problem():
    return SimpleNamespace(eta=Q(3,4),m=Q(2,5),b_K=Q(1,7),delta=Q(1,11),numerical_goal=Q(1,1<<80))


def blocks():
    result = []
    for p in (0,1):
        margin,tau = Q(p+1,3),Q(413+p,5)
        result.append({'dimension':413,'parity':p,'scope':'SOURCE_CONDITIONAL',
            'row_margins':[rational(margin+Q(i,1000)) for i in range(413)],
            'margin':rational(margin),'tau':rational(tau),'width':rational(0),
            'goal':rational(problem().numerical_goal),'direction_upper':rational(1),
            'direction_mass':rational(2),'direction_index':0,
            'modular':{'global_input_entries':413**2,'prime':65521,'residue':1,'nonsingular':True}})
    return result


def test_full_norm_uses_worse_parity_and_complete_physical_trace():
    p = problem()
    rows = blocks()
    sigma = min(Q(1,3)/Q(413,5),Q(2,3)/Q(414,5))
    expected = min(sigma/(1+2*(Q(1,7)+Q(1,11))**2/(Q(3,4)**2*Q(2,5)**2)),Q(3,4)*Q(2,5)/2)
    result = reviewed_consequence(p,rows)
    assert result['sigma']==sigma
    assert result['gamma']==expected
    rows[0]['tau'] = rational(1000)
    assert reviewed_consequence(p,rows)['gamma']<expected


@pytest.mark.parametrize('change',['missing-row','missing-parity','local-determinant','zero-residue','reference-scope','last-row'])
def test_incomplete_global_evidence_cannot_release_norm(change):
    rows = blocks()
    if change=='missing-row': rows[1]['row_margins'].pop()
    elif change=='missing-parity': rows.pop()
    elif change=='local-determinant': rows[1]['modular']['global_input_entries']=32**2
    elif change=='zero-residue': rows[1]['modular']['residue']=0
    elif change=='reference-scope': rows[1]['scope']='REFERENCE_ARITHMETIC_ONLY'
    else: rows[1]['row_margins'][-1]=rational(-1)
    with pytest.raises(ContractError):
        reviewed_consequence(problem(),rows)


def test_width_boundary_is_inclusive_but_over_goal_prevents_release():
    rows = blocks()
    rows[1]['width'] = rows[1]['goal']
    assert reviewed_consequence(problem(),rows)['positive_paid_lower']
    rows[1]['width'] = rational(problem().numerical_goal+Q(1,1<<256))
    with pytest.raises(ContractError,match='source-norm'):
        reviewed_consequence(problem(),rows)


def test_retained_endpoint_change_invalidates_the_sealed_scientific_inventory(tmp_path):
    source = tmp_path/'source.json'
    source.write_bytes(canonical_bytes({'endpoint_pairs':[[0,0,'0x1','0x2']]}))
    assert _seal(tmp_path)['status']=='PASS_RETAINED_INVENTORY'
    source.write_bytes(canonical_bytes({'endpoint_pairs':[[0,0,'0x1','0x3']]}))
    with pytest.raises(ContractError,match='changed'):
        verify_inventory(tmp_path)
