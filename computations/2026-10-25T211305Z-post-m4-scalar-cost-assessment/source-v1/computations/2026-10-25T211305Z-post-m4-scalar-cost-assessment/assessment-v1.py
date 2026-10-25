"""Executed scalar/error and contraction-volume assessment, no low matrix/sign."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from flint import arb, ctx
from scripts import weil_reference_route_controls as reference
from scripts.weil_fourier_minorant_matrix import panels
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms

T, N, P0, M0 = Q(3,4), 312, Q(49,32), Q(63,32)
OMEGA = 256
BASELINE = 'computations/2026-10-25T155033Z-fourier-minorant-sign/data/source-v2.json.gz'
BASELINE_SHA = '6f8994ee0d8813ddd0bbb3ba88e35b2070905199693788f9660906474edbeb66'


def assessment() -> dict:
    import gzip
    baseline_raw = (ROOT/BASELINE).read_bytes()
    if hashlib.sha256(baseline_raw).hexdigest() != BASELINE_SHA:
        raise ValueError('baseline source identity changed')
    baseline = json.loads(gzip.decompress(baseline_raw))
    baseline_error = Q(baseline['quadrature_operator_error_upper'])
    ball = reference.ball
    with ctx.workprec(512):
        terms = enumerate_active_prime_power_terms(3,4,prec=512)
        if [term.m for term in terms] != [2,3,4]:
            raise ValueError('complete strict active set failed')
        lower_margin = ball(T)-arb(2).log()
        upper_margin = arb(5).log()/2-ball(T)
        overlap = 1-arb(2).log()/ball(T)
        if not lower_margin > ball(Q(1,20)) or not upper_margin > ball(Q(1,20)):
            raise ValueError('support threshold margin below declared floor')
        if not ball(Q(3,40)) < overlap < ball(Q(19,250)):
            raise ValueError('nontrivial fourth-term overlap qualification failed')
        plane = reference.legendre_tail(T*OMEGA,N)
        polar = reference.legendre_tail(T/2,N)
        beta = 2*ball(T*OMEGA)/arb.pi()
        kappa = 9*beta*ball(plane)+4*ball(T)*ball(T).exp()*ball(polar)
        eta = 9*(beta*ball(plane)).sqrt()+4*ball(T)*ball(T).exp()*ball(polar).sqrt()
        k0, e0 = Q(4,10**49), Q(6,10**24)
        if not kappa < ball(k0) or not eta < ball(Q(19,10**25)):
            raise ValueError('pointwise compact envelope failed')
        if not 2*P0*Q(19,10**25)+Q(19,10**25)**2 < e0:
            raise ValueError('full mixed envelope failed')
        quadrature = {}
        errors = {}
        for order in (48,49,64):
            error = sum((8*ball((b-a)/2)*(2*ball(T)/arb.pi()
                         *(4*ball(T)*ball((b-a)/2)).exp()*4096)/(1<<(2*order))
                         for a,b in panels()),arb(0))
            quadrature[str(order)] = reference.interval(error)
            errors[order] = error
        if not errors[48] > ball(baseline_error) > errors[49]:
            raise ValueError('adjacent quadrature comparison failed')
        if not errors[49] < ball(Q(3,10**21)) or not errors[64] < ball(Q(3,10**30)):
            raise ValueError('complete quadrature upper failed')
        factors = {}
        for parity in (0,1):
            degrees = list(range(parity,N,2))
            largest = degrees[-1]
            value = arb(len(degrees))+sum((ball(Q(2*largest+1,2*j+1)).sqrt()
                                          for j in degrees),arb(0))
            if not value < 470:
                raise ValueError('physical-mass interval-order loss bound failed')
            factors[str(parity)] = reference.interval(value)
        denominator = M0-k0
        numerical_a, numerical_gp = Q(1,10**27), Q(1,10**28)
        loss = (470*Q(3,10**21)+numerical_a+numerical_gp/denominator
                +e0/denominator+P0**2*k0/(denominator*M0))
        if not loss < Q(15,10**19):
            raise ValueError('conditional complete scalar-reference resolution failed')
        rounding = Q(2*(N//2)*(2*N-1),2*(1<<128))
        if not rounding < numerical_gp:
            raise ValueError('128-bit outward-grid order allowance too coarse')
        from scripts import verify_weighted_low_space as exact
        toy_radii = [[Q(1),Q(2)],[Q(2),Q(4)]]
        toy_triangle = [[[-1,1],[-2,2]],[[-4,4]]]
        toy_lower,_,_ = exact._order_bounds(toy_triangle,0)
        toy_trial = [Q(1),Q()]
        toy_loss = sum((toy_trial[i]*toy_trial[j]
                        *(toy_radii[i][j]-Q(str(toy_lower[i,j])))
                        for i in range(2) for j in range(2)),Q())
        if toy_loss != 4 or not toy_loss > 1:
            raise ValueError('interval-box physical-mass loss countercontrol failed')
        geometry = {'threshold_lower_margin':reference.interval(lower_margin),
                    'threshold_upper_margin':reference.interval(upper_margin),
                    'each_margin_strictly_above':'1/20',
                    'fourth_term_one_sided_overlap_fraction':reference.interval(overlap),
                    'overlap_fraction_strict_bounds':['3/40','19/250'],
                    'scaled_shifts':{str(term.m):reference.interval(term.tau) for term in terms}}
        scalars = {'kappa':reference.interval(kappa),'eta':reference.interval(eta),
                   'kappa_upper':str(k0),'mixed_Gram_upper':str(e0),
                   'denominator_lower':str(denominator),'quadrature_errors':quadrature,
                   'baseline_quadrature_upper':str(baseline_error),
                   'q49_below_baseline_q48':True,'q48_above_baseline_q48':True,
                   'physical_mass_order_loss_factors':factors,
                   'physical_mass_order_loss_factor_upper':470,
                   'conditional_numerical_A_order_loss_upper':str(numerical_a),
                   'conditional_numerical_GP_order_loss_upper':str(numerical_gp),
                   'dyadic_rounding_only_order_loss_upper':str(rounding),
                   'conditional_total_loss_from_A_minus_GP_over_m0':str(loss),
                   'conditional_total_loss_ceiling':'3/2000000000000000000',
                   'interval_box_countercontrol':{'mass':[1,4],'midpoint':[[0,0],[0,0]],
                       'true_matrix':[[1,2],[2,4]],'radii':[[1,2],[2,4]],
                       'Loewner_lower':[[-3,0],[0,-6]],'trial':[1,0],
                       'nominal_radius':1,'true_to_lower_trial_loss':4}}
    p=N//2
    count=len(panels())
    def proxy(cells, frequency_order, low_pairs, square_pairs):
        producer_arithmetic=4*cells*p*p*N
        producer_band=2*p*p*count*frequency_order
        producer_gp=2*p**3
        audit_arithmetic=(low_pairs+square_pairs)*N*N*(N+1)
        audit_band=N*N*count*64
        audit_gp=N**3
        return {'producer_arithmetic':producer_arithmetic,'producer_band':producer_band,
                'producer_GP':producer_gp,'producer_total':producer_arithmetic+producer_band+producer_gp,
                'audit_arithmetic':audit_arithmetic,'audit_band':audit_band,'audit_GP':audit_gp,
                'audit_total':audit_arithmetic+audit_band+audit_gp}
    before=proxy(4,48,4,8)
    after=proxy(7,49,6,20)
    return {'format':'post-m4-scalar-cost-assessment-v1','support':[3,4],
            'scope':'executed scalar and exact accounting only; no low sign or future implementation contract',
            'a':'7/2','omega':OMEGA,'dimension':N,'active_terms':[2,3,4],
            'geometry':geometry,'scalars':scalars,
            'work':{'proxy_kind':'classical contraction volume, not FLOPs or observed runtime',
                    'frequency_panels':count,'source_frequency_nodes_q49':count*49,
                    'audit_frequency_nodes_q64':count*64,
                    'entries_per_serialized_triangle':N*(N+1)//2,
                    'six_matrix_serialized_slots':6*N*(N+1)//2,
                    'complete_parity_block_sizes':[p,p],
                    'baseline_proxy':before,'post_transition_proxy':after,
                    'producer_proxy_ratio':str(Q(after['producer_total'],before['producer_total'])),
                    'audit_proxy_ratio':str(Q(after['audit_total'],before['audit_total']))},
            'baseline_source_sha256':BASELINE_SHA,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=assessment()
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:
        handle.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'support':result['support'],'mixed_Gram_upper':result['scalars']['mixed_Gram_upper'],
                      'q49_below_baseline_q48':True,'matrix_slots':result['work']['six_matrix_serialized_slots'],
                      'new_low_matrix_computed':False}))
