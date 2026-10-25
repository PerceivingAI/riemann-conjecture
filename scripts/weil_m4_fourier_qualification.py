"""Whole-window scalar/finite controls only; no selected support or sign matrix."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from math import factorial
from pathlib import Path

from flint import arb, ctx, fmpq, fmpq_mat
from scripts import weil_reference_route_controls as reference
from scripts.weil_fourier_minorant_matrix import panels
from scripts.cert.prime_power_terms import factor_prime_power

ROOT = Path(__file__).resolve().parents[1]
SCALAR_SOURCE = 'computations/2026-10-25T142424Z-reference-route-selection/data/scalar-controls-v1.json'
SCALAR_SHA = '7d3975bb76c621f15182c6377503ac9fd63a83c786b66898e271294fbf09f3fc'


def exp_lower(x: Q, order: int) -> Q:
    return sum((x**k/factorial(k) for k in range(order+1)), Q())


def elementary_norm_proof() -> dict:
    exponents = {'log2_upper': Q(111,160), 'log3_upper': Q(11,10),
                 'twice_support_majorant': Q(13,8)}
    exponentials = {key:exp_lower(value,8) for key,value in exponents.items()}
    if not (exponentials['log2_upper']>2 and exponentials['log3_upper']>3
            and exponentials['twice_support_majorant']>5):
        raise ValueError('positive finite exponential proof failed')
    if not Q(33,8)**2>17 or not Q(173,100)**2<3:
        raise ValueError('rational square-root proof failed')
    joint = Q(111,160)*(1+Q(33,8))/4+Q(11,10)/Q(173,100)
    if not joint<Q(49,32): raise ValueError('joint arithmetic rational bound failed')
    m,p=Q(63,32),Q(49,32)
    if m-p*p/m!=Q(7,9): raise ValueError('bare-reference Schur algebra failed')
    return {'finite_exp_lower_order':8,'finite_exp_lowers':{k:str(v) for k,v in exponentials.items()},
            'joint_arithmetic_elementary_upper':str(joint),'p_upper':'49/32',
            'reference_lower':'63/32','bare_reference_scalar_Schur_lower':'7/9',
            'support_majorant_role':'13/16 bounds log5/2; it is not a selected support case'}


def finite_geometry_controls() -> dict:
    shift=fmpq_mat([[0,1,0],[0,0,1],[0,0,0]])
    b=shift+shift.transpose()
    v=fmpq_mat([[1],[1],[1]])
    mass=(v.transpose()*v)[0,0]
    energy=(v.transpose()*b*v)[0,0]
    if not energy>mass: raise ValueError('old norm-one counterdirection failed')
    if b*b-shift*shift.transpose()-shift.transpose()*shift != shift*shift+(shift*shift).transpose():
        raise ValueError('second-shift square identity failed')
    r=fmpq_mat([[0,1,fmpq(1,2)],[fmpq(1,2),0,fmpq(1,2)],[fmpq(1,2),1,0]])
    metric=fmpq_mat([[1,0,0],[0,2,0],[0,0,1]])
    if r.transpose()*metric!=metric*r: raise ValueError('weighted joint fiber not self-adjoint')
    coefficients=list(r.charpoly().coeffs())
    if coefficients!=[fmpq(-1,2),fmpq(-5,4),fmpq(0),fmpq(1)]:
        raise ValueError('joint fiber characteristic polynomial failed')
    signed=[(m,s) for m in (2,3,4) for s in (-1,1)]
    pairs=[]
    for m,s in signed:
        for other,t in signed:
            keep=s==t or m*other<5
            pairs.append({'left':[m,s],'right':[other,t],'nonempty':keep,
                          'criterion':'same sign: max active shift below2; opposite sign: product<exp(2T) with4<exp(2T)<5'})
    nonempty=sum(p['nonempty'] for p in pairs)
    involving4=[p for p in pairs if p['left'][0]==4 or p['right'][0]==4]
    if nonempty!=20 or sum(p['nonempty'] for p in involving4)!=10:
        raise ValueError('complete signed-image pair inventory failed')
    factor=factor_prime_power(4)
    if factor.prime!=2 or factor.exponent!=2: raise ValueError('von Mangoldt4 base changed')
    return {'scope':'dimensionless exact fibers and symbolic window classification, not a support probe',
            'three_chain_full_shift_characteristic':[str(c) for c in b.charpoly().coeffs()],
            'old_norm_one_counterdirection':{'vector':[1,1,1],'mass':str(mass),'energy':str(energy),'Rayleigh':'4/3'},
            'joint_24_characteristic':[str(c) for c in coefficients],
            'ordered_image_pairs':pairs,'nonempty_pairs':nonempty,'empty_pairs':36-nonempty,
            'new_pairs_involving4_nonempty':10,'new_pairs_involving4_empty':10,
            'new_opposite_sign_22_nonempty':2,'prime_power4_base':2}


def scalar_controls() -> dict:
    raw=(ROOT/SCALAR_SOURCE).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SCALAR_SHA:
        raise ValueError('inherited exterior source bytes changed')
    prior=json.loads(raw)
    if not Q(prior['exterior_weight_lower_from_series']['lower'])>Q(1,5):
        raise ValueError('whole exterior premise failed')
    with ctx.workprec(512):
        ball=reference.ball
        upper=Q(13,16)
        c=Q(208)
        n=312
        p=arb(2).log()*(1+arb(17).sqrt())/4+arb(3).log()/arb(3).sqrt()
        a0=reference.archimedean(0)
        endpoint=reference.archimedean(256)
        width=max(abs(a0-ball(Q(7,2))),abs(endpoint-ball(Q(7,2))))
        if not p<ball(Q(49,32)) or not width<9: raise ValueError('source scalar enclosure failed')
        plane=reference.legendre_tail(c,n)
        polar=reference.legendre_tail(upper/2,n)
        beta=2*ball(c)/arb.pi()
        kappa=9*beta*ball(plane)+4*ball(upper)*ball(upper).exp()*ball(polar)
        eta=9*(beta*ball(plane)).sqrt()+4*ball(upper)*ball(upper).exp()*ball(polar).sqrt()
        kappa_bound=Q(3,10**27)
        eta_bound=Q(7,5*10**13)
        epsilon_bound=Q(1,2*10**12)
        if not kappa<ball(kappa_bound) or not eta<ball(eta_bound):
            raise ValueError('whole-window compact envelope failed')
        if not 2*Q(49,32)*eta_bound+eta_bound**2<epsilon_bound:
            raise ValueError('complete mixed Gram allowance failed')
        qerrors={}
        for order in (48,64):
            value=sum((8*ball((right-left)/2)*
                       (2*ball(upper)/arb.pi()*(4*ball(upper)*ball((right-left)/2)).exp()*4096)
                       /(1<<(2*order)) for left,right in panels()),arb(0))
            ceiling=Q(2,10**20) if order==48 else Q(5,10**30)
            if not value<ball(ceiling): raise ValueError('uniform quadrature envelope failed')
            qerrors[str(order)]=reference.interval(value)
        anchor_ratio=Q(10816,1)/(386*Q(1397,2))
        anchor_tail=Q(16,15)*Q(3,11)**385
        if not anchor_ratio<Q(1,16) or not anchor_tail<Q(1,1<<720):
            raise ValueError('expanded Fourier anchor bound failed')
        pole_u=Q(169,4096)
        pole_term=Q(1)
        for k in range(1,130): pole_term*=pole_u/(k*(Q(3,2)+k-1))
        pole_ratio=pole_u/(130*(Q(3,2)+129))
        pole_tail=pole_term/(1-pole_ratio)
        return {'p_joint':reference.interval(p),'reference_gap':reference.interval(ball(Q(7,2))-p),
                'band_weight_upper':reference.interval(width),'rational_band_weight_upper':'9',
                'band_support_upper_only':'13/16','frequency_argument_upper_only':'208',
                'projection_control_role':'existing baselineN312, analytic comparison only; no new case selected',
                'compact_double_tail':reference.interval(kappa),'compact_one_sided_tail':reference.interval(eta),
                'compact_double_tail_upper':str(kappa_bound),'compact_one_sided_tail_upper':str(eta_bound),
                'complete_mixed_Gram_upper':str(epsilon_bound),
                'outside_denominator_lower':str(Q(63,32)-kappa_bound),
                'quadrature_operator_errors':qerrors,'anchor_n_min':312,'anchor_terms':384,
                'anchor_ratio_upper':str(anchor_ratio),'anchor_hypergeometric_tail_upper':str(anchor_tail),
                'anchor_tail_below_2_to_minus720':True,'polar_anchor_terms':128,
                'polar_anchor_u_upper':str(pole_u),'polar_hypergeometric_tail_upper':str(pole_tail),
                'exterior_source_sha256':SCALAR_SHA,'exterior_weight_lower':'1/5'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result={'format':'m4-fourier-qualification-controls-v1',
            'scope':'whole log2<T<log5/2 analytical qualification; no selected support or positivity matrix',
            'elementary_norm':elementary_norm_proof(),'geometry':finite_geometry_controls(),
            'scalars':scalar_controls(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:
        handle.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'scope':result['scope'],'nonempty_signed_image_pairs':20,
                      'reference_lower':'63/32','complete_mixed_Gram_upper':result['scalars']['complete_mixed_Gram_upper'],
                      'new_low_matrix_computed':False}))
