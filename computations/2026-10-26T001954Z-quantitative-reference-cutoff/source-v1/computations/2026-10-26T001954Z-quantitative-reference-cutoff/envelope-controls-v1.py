"""Scalar/exact controls for a proved envelope; no matrix or admission operation."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import inspect
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from flint import arb, ctx
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms
from scripts.weil_reference_route_controls import archimedean, ball, independent_digamma_enclosure, interval


def ceil_q(q):
    return -((-q.numerator)//q.denominator)


def certified_ceiling(value):
    lo,hi=arb_to_rational_enclosure(value)
    left,right=ceil_q(lo),ceil_q(hi)
    if left!=right:
        raise ValueError('unresolved chain ceiling')
    return left


def overlap(a,b):
    return max(Q(0),min(a[1],b[1])-max(a[0],b[0]))


def evaluate():
    ctx.prec=512
    pins_path=Path(__file__).with_name('input-pins.json')
    pins=json.loads(pins_path.read_text(encoding='utf-8'))
    for item in pins['inputs']:
        raw=(ROOT/item['path']).read_bytes()
        if len(raw)!=item['bytes'] or hashlib.sha256(raw).hexdigest()!=item['sha256']:
            raise ValueError('retained scalar input bytes changed')
    old_path=pins['comparison_path']
    manifest=json.loads((ROOT/pins['comparison_manifest']).read_text(encoding='utf-8'))
    member=next(x for x in manifest['members'] if x['path']=='data/comparison-v1.json')
    old_raw=(ROOT/old_path).read_bytes()
    if member['sha256']!=hashlib.sha256(old_raw).hexdigest() or member['bytes']!=len(old_raw):
        raise ValueError('inherited comparison is not bound by its original seal')
    old=json.loads(old_raw)
    checks={
        'published_upper_is_below_selected_C':Q(103883,100000)<Q(21,20),
        'log563_exceeds5':bool(arb(563).log()>5),
        'cap_domain_endpoint_exp13_over2_exceeds563':bool(ball(Q(13,2)).exp()>563),
        'cap_coefficient_exceeds3_over20':bool((ball(Q(9,10))*ball(Q(-1,2)).exp()-ball(Q(21,20))*ball(Q(-3,2)).exp())/2>ball(Q(3,20))),
        'digamma_sector_remainder_constant':bool(arb(2).sqrt()/6<ball(Q(1,4))),
        'A4_analytic_upper_is_negative':bool((arb(2)/arb.pi()).log()+ball(Q(1,8))<0),
        'integer_chain_endpoint_has_length2':certified_ceiling(arb(2))==2,
    }
    try:
        certified_ceiling(arb('2 +/- 0.01'))
    except ValueError:
        checks['overlapping_chain_boundary_rejected']=True
    else:
        checks['overlapping_chain_boundary_rejected']=False
    caps=[(Q(-7,2),Q(-5,2)),(Q(5,2),Q(7,2))]
    cap_controls=[]
    for delta_text in pins['cap_deltas']:
        delta=Q(delta_text);shift=7-delta
        pair=sum((overlap(left,(right[0]+sign*shift,right[1]+sign*shift))
                  for left in caps for right in caps for sign in [-1,1]),Q(0))/2
        expected=max(Q(0),1-abs(delta-1))
        if pair!=expected:raise ValueError('signed-cap normalization failed')
        cap_controls.append({'delta':str(delta),'signed_pair_rayleigh':str(pair),'expected':str(expected)})
    if sum((b-a for a,b in caps),Q(0))/2!=1:raise ValueError('cap norm is not one')
    cases=[]
    for label in pins['existing_cases']:
        prior=old[label];t=Q(prior['support']);T=ball(t)
        terms=enumerate_active_prime_power_terms(t.numerator,t.denominator,prec=512)
        if [x.m for x in terms]!=prior['active_terms']:raise ValueError('active set changed')
        r=sum((x.coefficient*(2-x.tau) for x in terms),arb(0))
        previous=prior['constant_trial_reference_lower_requirement']
        rlo,rhi=arb_to_rational_enclosure(r)
        if rlo>Q(previous['upper']) or rhi<Q(previous['lower']):
            raise ValueError('fresh constant trial disagrees with retained interval')
        chain=[];p=arb(0)
        for term in terms:
            length=certified_ceiling(2*T/term.log_m)
            norm=2*(arb.pi()/(length+1)).cos()
            contribution=term.coefficient*norm;p+=contribution
            chain.append({'m':term.m,'length':length,'norm_upper':interval(norm),'contribution_upper':interval(contribution)})
        if label=='post_transition':
            if not (arb(2).log()<T and T<arb(5).log()/2):raise ValueError('joint24 window not certified')
            selected=arb(2).log()*(1+arb(17).sqrt())/4+arb(3).log()/arb(3).sqrt()
            sufficient=Q(49,32)
            if not selected<ball(sufficient):raise ValueError('joint24 bound failed')
            selected_name='joint24_plus3'
        else:
            selected=p;sufficient=Q(9,8);selected_name='individual_chain_sum'
            if not selected<ball(sufficient):raise ValueError('baseline norm cap failed')
        global_upper=ball(Q(21,20))*(4*T.exp()-2)
        r_upper=ball(Q(21,20))/T*(4*T.exp()-2*T-4)
        if not r<r_upper:raise ValueError('constant-trial upper envelope failed at retained case')
        if not (r<selected and p<global_upper):raise ValueError('necessary/sufficient ordering failed')
        if label=='post_transition' and not selected<p:raise ValueError('joint24 improvement failed')
        cases.append({'label':label,'support':str(t),'active_terms':[x.m for x in terms],
                      'r':interval(r),'r_global_upper':interval(r_upper),'chain_terms':chain,
                      'p_chain':interval(p),'selected_bound':selected_name,'p_selected':interval(selected),
                      'published_simple_p_upper':str(sufficient),'a':str(Q(prior['a'])),
                      'guaranteed_m_from_simple_p_upper':str(Q(prior['a'])-sufficient),
                      'sufficient_selected_to_constant_trial_ratio':interval(selected/r),
                      'p_global':interval(global_upper)})
    # The integer frequencies beside 2pi exp(7/2) are derived without midpoint rounding.
    central=2*arb.pi()*ball(Q(7,2)).exp();clo,chi=arb_to_rational_enclosure(central)
    floor_lo,floor_hi=clo.numerator//clo.denominator,chi.numerator//chi.denominator
    if floor_lo!=floor_hi:raise ValueError('unresolved integer cutoff neighbors')
    frequencies=[Q(4),Q(floor_lo),Q(floor_lo+1),Q(256)]
    frequency_controls=[]
    for frequency in frequencies:
        t=ball(frequency);direct=archimedean(frequency)
        series_lo,series_hi=independent_digamma_enclosure(frequency,pins['series_terms'])
        center=(t/(2*arb.pi())).log();error=2/t**2
        if not (series_lo<direct and direct<series_hi and center-error<direct and direct<center+error):
            raise ValueError('digamma series or remainder control failed')
        frequency_controls.append({'frequency':str(frequency),'A_direct':interval(direct),
                                   'A_series_lower':interval(series_lo),'A_series_upper':interval(series_hi),
                                   'analytic_lower':interval(center-error),'analytic_upper':interval(center+error)})
    brackets=[]
    for reserve_text in pins['exterior_reserves']:
        reserve=Q(reserve_text);target=Q(7,2)+reserve
        lower=2*arb.pi()*(ball(target)-ball(Q(1,8))).exp()
        upper=2*arb.pi()*(ball(target)+ball(Q(1,8))).exp()
        left=arb_to_rational_enclosure(lower)[0];right=arb_to_rational_enclosure(upper)[1]
        if not (archimedean(left)<ball(target) and archimedean(right)>ball(target)):
            raise ValueError('constructive cutoff bracket failed')
        if not archimedean(Q(256))>ball(target):raise ValueError('retained cutoff reserve failed')
        brackets.append({'a':'7/2','exterior_reserve':str(reserve),'necessary_cutoff_lower':interval(lower),
                         'constructive_cutoff_upper':interval(upper),'retained_Omega256_meets_target':True})
    if not all(checks.values()):raise ValueError('envelope constant or boundary control failed')
    modules={};namespaces={}
    for name,module in sorted(sys.modules.items()):
        if name=='scripts' or name.startswith('scripts.'):
            if getattr(module,'__file__',None) is None:
                namespaces[name]=sorted({Path(path).resolve().relative_to(ROOT).as_posix() for path in module.__path__})
                continue
            path=Path(module.__file__).resolve()
            relative=path.relative_to(ROOT).as_posix()
            modules[relative]=hashlib.sha256(path.read_bytes()).hexdigest()
    return {'format':'quantitative-reference-cutoff-controls-v1','status':'PASS','precision_bits':512,
            'input_pins_sha256':hashlib.sha256(pins_path.read_bytes()).hexdigest(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'constant_and_boundary_checks':checks,'exact_cap_overlap_controls':cap_controls,
            'existing_case_controls':cases,'digamma_series_terms':pins['series_terms'],
            'frequency_controls':frequency_controls,'cutoff_brackets':brackets,
            'imported_project_module_sha256':modules,'namespace_package_paths':namespaces,'new_support_matrix_computed':False,
            'scope':'Checks of a written derivation, not a proof by sampling, new Weil sign, external-theorem replay or admission.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=evaluate()
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:
        handle.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'existing_cases':len(result['existing_case_controls']),
                      'exact_cap_controls':len(result['exact_cap_overlap_controls']),
                      'digamma_frequency_controls':len(result['frequency_controls']),
                      'new_support_matrix_computed':False}))
