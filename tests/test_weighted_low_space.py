"""Finite matrix-order controls and a real polynomial-degree zero regression."""
from fractions import Fraction as Q
import gzip
import json

import pytest

from flint import arb, fmpq, fmpq_mat

from scripts.verify_weighted_low_space import directional_upper, weighted_matrices
from scripts.verify_weighted_low_space_inputs import reconstruct_heads, reference_pair
from scripts import verify_combined_schur_analytic_entries as native
from scripts import verify_weighted_low_space_inputs as audit_inputs


def _matrix(rows):
    return fmpq_mat([[fmpq(x.numerator,x.denominator) for x in row] for row in rows])


def _psd2(matrix):
    return (matrix[0,0]>=0 and matrix[1,1]>=0
            and matrix[0,0]*matrix[1,1]-matrix[0,1]**2>=0)


def _fixture(delta=Q(),margin=Q(10)):
    bits,n,m = 64,2,5
    den = 1 << bits
    def pair(value):
        return [(value*den).__floor__(),(value*den).__ceil__()]
    raw = [[Q(1),Q(2)],[Q(-2),Q(1)],[Q(1),Q(-1)],[Q(2),Q(-1)]]
    degrees = [2,3,4,6]
    mass = _matrix([[Q(2),Q()],[Q(),Q(2,3)]])
    gram = [[Q() for _ in range(n)] for _ in range(n)]
    energy = [[Q() for _ in range(n)] for _ in range(n)]
    for row,k in zip(raw,degrees):
        weight = 1/(Q(1,2)+sum((Q(1,l) for l in range(n+1,k+1)),Q()))
        for i in range(n):
            for j in range(n):
                value = row[i]*row[j]*Q(2*k+1,2)
                gram[i][j] += value
                energy[i][j] += weight*value
    A = _matrix(energy)+mass*fmpq(margin.numerator,margin.denominator)
    V = [[Q(2),Q(1)],[Q(-1),Q(2)],[Q(3),Q(-2)]]
    P = [[x-y for x,y in zip(row,v)] for row,v in zip(raw[:3],V)]
    packet = {'dimension':n,'boundary':m,'bits':bits,'mu_reference_exact':'1/2',
              'delta':pair(delta),'matrices':{},'heads':{}}
    packet['matrices']['G_K'] = [[pair(gram[i][j]) for j in range(i,n)] for i in range(n)]
    packet['matrices']['A_K'] = [[pair(Q(str(A[i,j]))) for j in range(i,n)] for i in range(n)]
    packet['heads'] = {name:[[pair(x) for x in row] for row in rows]
                       for name,rows in [('V',V),('P',P),('R32',[[Q(),Q()]]*3)]}
    return packet,A,_matrix(energy),mass,raw,degrees


def test_weighted_outer_products_preserve_mass_and_signed_cross_terms():
    packet,A,energy,mass,raw,degrees = _fixture()
    result = weighted_matrices(packet)
    wm = 1/(Q(1,2)+sum((Q(1,k) for k in range(3,6)),Q()))
    w6 = 1/(Q(1,2)+sum((Q(1,k) for k in range(3,7)),Q()))
    tail = _matrix([[Q(26),Q(-13)],[Q(-13),Q(13,2)]])
    expected = energy+tail*fmpq((wm-w6).numerator,(wm-w6).denominator)
    assert result['gamma'] == Q(91,4)
    assert _psd2(result['u_plus']-expected)
    assert _psd2((A-energy)-result['lower'])
    # The off-diagonal is negative and large; diagonal-only tests miss it.
    assert abs(result['u_plus'][0,1]-expected[0,1]) < fmpq(1,1 << 40)


def test_full_signed_residual_cross_effects_are_paid_in_physical_metric():
    delta = Q(1,100)
    packet,A,energy,mass,raw,degrees = _fixture(delta)
    result = weighted_matrices(packet)
    changed = [[v+delta*Q((-1)**(i+j),64) for j,v in enumerate(row)] for i,row in enumerate(raw)]
    frobenius = sum((delta**2/Q(64**2)*Q(2*k+1,2)*Q(2*j+1,2)
                     for k in degrees for j in range(2)),Q())
    assert frobenius < delta**2/4
    actual_energy = [[Q() for _ in range(2)] for _ in range(2)]
    for row,k in zip(changed,degrees):
        weight = 1/(Q(1,2)+sum((Q(1,l) for l in range(3,k+1)),Q()))
        for i in range(2):
            for j in range(2):
                actual_energy[i][j] += weight*row[i]*row[j]*Q(2*k+1,2)
    actual = A-mass*fmpq(delta.numerator,4*delta.denominator)-_matrix(actual_energy)
    assert _psd2(actual-result['lower'])


def test_negative_lower_does_not_manufacture_a_negative_reference_direction():
    packet,A,energy,mass,_,_ = _fixture(margin=Q(1,1000))
    result = weighted_matrices(packet)
    actual = A-energy
    assert actual[0,0]>0 and actual.det()>0
    assert result['lower'][0,0]<0
    bound = directional_upper(packet,result,[Q(1),Q(-1)])
    assert Q(bound['reference_upper'])>0


def test_individual_residual_degree_zeros_survive_independent_reconstruction():
    basis = native.poly_basis(36)
    residual = native.residual_polys(basis[:4],32,fmpq(3,5),native.exact_residual_coefficients(32))
    heads = reconstruct_heads(4,36,512,residual)
    assert residual[0].degree() == 32
    # Same parity, above R32(P0)'s degree, but below the global degree35.
    assert reference_pair(heads['R32'][34-4,0],[0,0],352,'R32[34,0]') == [0,0]
    p = (basis[32]*residual[0]).integral()
    exact = p(1)-p(-1)
    assert exact != 0
    with native.ctx.workprec(512):
        assert heads['R32'][32-4,0].contains(arb(exact))
    assert not heads['R32'][32-4,0].contains(0)


def test_pinned_low_reuse_rejects_a_changed_matrix():
    path = audit_inputs.ROOT/'computations/2026-10-24T124142Z-weighted-low-space/data/source-m224-v1.json.gz'
    packet = json.loads(gzip.decompress(path.read_bytes()))
    packet['matrices']['A_K'][0][0][0] -= 1
    with pytest.raises(audit_inputs.InputRejected,match='low input changed: matrices'):
        audit_inputs._accepted_low(packet)


def test_pinned_low_reuse_rejects_forged_ancestor_bytes(tmp_path,monkeypatch):
    data = tmp_path/'computations/2026-10-24T124142Z-weighted-low-space/data'
    data.mkdir(parents=True)
    (data/'source-m224-v1.json.gz').write_bytes(b'forged source')
    (data/'audit-m224-v2.json.gz').write_bytes(b'forged accepted flag')
    monkeypatch.setattr(audit_inputs,'ROOT',tmp_path)
    with pytest.raises(audit_inputs.InputRejected,match='accepted low source bytes changed'):
        audit_inputs._accepted_low({})


def test_native_interval_contraction_pays_signed_noncentered_uncertainty():
    packet,A,energy,mass,_,_ = _fixture()
    quantum = (1 << packet['bits'])//64
    for row in packet['heads']['V']:
        for pair in row:
            pair[0] -= quantum
            pair[1] += 3*quantum
    result = weighted_matrices(packet)
    wm = 1/(Q(1,2)+sum((Q(1,k) for k in range(3,6)),Q()))
    w6 = 1/(Q(1,2)+sum((Q(1,k) for k in range(3,7)),Q()))
    tail = _matrix([[Q(26),Q(-13)],[Q(-13),Q(13,2)]])
    exact = energy+tail*fmpq((wm-w6).numerator,(wm-w6).denominator)
    assert _psd2(result['u_plus']-exact)
    assert _psd2((A-energy)-result['lower'])
