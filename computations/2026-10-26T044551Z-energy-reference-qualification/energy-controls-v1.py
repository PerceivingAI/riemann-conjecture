"""Fixed-source scalar identities and non-Weil toys; no new low matrix/sign."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from flint import arb, acb, ctx
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms
from scripts.weil_reference_route_controls import ball, interval, archimedean, legendre_tail


def upper(x):return arb_to_rational_enclosure(x)[1]
def lower(x):return arb_to_rational_enclosure(x)[0]
def polynomial(coefficients,x):return sum((ball(coef)*x**k for k,coef in enumerate(coefficients)),arb(0))


def moments(rate,left,right,degree):
    def primitive(x):
        exponential=(rate*x).exp();values=[exponential/rate]
        for k in range(1,degree+1):values.append(x**k*exponential/rate-k*values[-1]/rate)
        return values
    a,b=primitive(left),primitive(right)
    return [y-x for x,y in zip(a,b)]


def integral_polynomial(coefficients,rate,left,right):
    values=moments(rate,left,right,len(coefficients)-1)
    return sum((ball(coef)*value for coef,value in zip(coefficients,values)),arb(0))


def cosine_correlation_integral(rate,carrier,T):
    k=arb.pi()/(2*ball(T));length=2*ball(T)
    def term(frequency):
        z=acb(ball(rate),frequency);exponential=(z*length).exp()
        m0=(exponential-1)/z;m1=length*exponential/z-m0/z
        return ((acb(2,-1/(k*ball(T))))*m0-m1/ball(T)).real
    return (term(k+ball(carrier))+term(k-ball(carrier)))/2


def evaluate(input_root):
    ctx.prec=512
    pins_path=Path(__file__).with_name('input-pins.json');pins=json.loads(pins_path.read_text(encoding='utf-8'))
    binding=pins['source'];seal_raw=(input_root/binding['manifest']).read_bytes();source_raw=(input_root/binding['path']).read_bytes()
    if hashlib.sha256(seal_raw).hexdigest()!=binding['manifest_sha256'] or hashlib.sha256(source_raw).hexdigest()!=binding['source_sha256']:raise ValueError('fixed source bytes changed')
    member=next(x for x in json.loads(seal_raw)['members'] if x['path']==binding['member'])
    if member['bytes']!=len(source_raw) or member['sha256']!=binding['source_sha256']:raise ValueError('source is not bound by original seal')
    source=json.loads(gzip.decompress(source_raw))
    if source['support']!=[3,4] or source['dimension']!=312:raise ValueError('only the retained fixed source is authorized')
    T=Q(pins['fixed_support']);length=2*ball(T);terms=enumerate_active_prime_power_terms(T.numerator,T.denominator,prec=512)
    if [term.m for term in terms]!=[2,3,4]:raise ValueError('complete active set changed')
    tolerance=ball(Q(1,2**400));breaks=[arb(0)]+[term.log_m for term in terms]+[length]
    sigma=arb(1);segments=[];B=arb(0)
    for i,(left,right) in enumerate(zip(breaks,breaks[1:])):
        if i:
            sigma=sigma+terms[i-1].von_mangoldt
            if not sigma<terms[i-1].m:raise ValueError('discrepancy post-jump sign not certified')
        if not left<right:raise ValueError('discrepancy interval ordering failed')
        B+=integral_polynomial([Q(1)],ball(Q(1,2)),left,right)-sigma*integral_polynomial([Q(1)],ball(Q(-1,2)),left,right)
        segments.append((left,right,sigma))
    closed_B=2*(ball(T).exp()+(-ball(T)).exp()-2)-2*sum((term.von_mangoldt*(1/arb(term.m).sqrt()-(-ball(T)).exp()) for term in terms),arb(0))
    if not (B>0 and abs(B-closed_B)<tolerance):raise ValueError('complete discrepancy absolute integral disagrees with closed formula')
    phi_coefficients=[[Q(2),-1/T],[Q(2),-3/T,Q(0),Q(1,2)/T**3]]
    exact_overlap=[]
    for shift_text in pins['toy_correlation_shifts']:
        shift=Q(shift_text);a=-T+shift;b=T
        odd_overlap=3/(2*T**3)*((b**3-a**3)/3-shift*(b*b-a*a)/2)
        phi_odd=Q(2)-3*shift/T+shift**3/(2*T**3)
        if 2*odd_overlap!=phi_odd:raise ValueError('exact odd correlation normalization failed')
        even_overlap=(2*T-shift)/(2*T)
        if 2*even_overlap!=2-shift/T:raise ValueError('exact even correlation normalization failed')
        exact_overlap.append({'shift':str(shift),'phi_even':str(2*even_overlap),'phi_odd':str(phi_odd)})
    source_controls=[]
    for n in pins['normalization_modes']:
        coefficients=phi_coefficients[n]
        arithmetic=sum((term.coefficient*polynomial(coefficients,term.log_m) for term in terms),arb(0))
        continuum=integral_polynomial(coefficients,ball(Q(1,2)),arb(0),length)
        laplace=integral_polynomial(coefficients,ball(Q(-1,2)),arb(0),length)
        discrepancy=arithmetic-continuum
        derivative=[Q(k)*coefficients[k] for k in range(1,len(coefficients))]
        derivative.extend(Q(0) for _ in range(len(coefficients)-len(derivative)))
        weighted_derivative=[derivative[k]-coefficients[k]/2 for k in range(len(coefficients))]
        integration_by_parts=arb(0)
        for left,right,s in segments:
            integration_by_parts-=s*integral_polynomial(weighted_derivative,ball(Q(-1,2)),left,right)-integral_polynomial(weighted_derivative,ball(Q(1,2)),left,right)
        if n==0:pole=16/ball(T)*(ball(T)/2).sinh()**2
        else:pole=-3/ball(T**3)*(4*ball(T)*(ball(T)/2).cosh()-8*(ball(T)/2).sinh())**2
        if not (laplace>0 and abs(discrepancy-integration_by_parts)<tolerance and abs((-arithmetic+pole)-(laplace-discrepancy))<tolerance):raise ValueError('signed source/continuum/Stieltjes identity failed')
        for name,value in [('P',-arithmetic),('pole',pole)]:
            lo_int,hi_int=source['matrices'][name][n][0];mass=Q(2,2*n+1);scale=1<<source['bits']
            if not Q(lo_int,scale)/mass<=lower(value)<=upper(value)<=Q(hi_int,scale)/mass:raise ValueError('fresh scalar does not fit original physical-mass source interval')
        if n==1 and not pole<0:raise ValueError('negative odd pole omitted')
        source_controls.append({'mode':n,'physical_mass':str(Q(2,2*n+1)),'P_normalized':interval(-arithmetic),'pole_normalized':interval(pole),
                                'laplace_positive':interval(laplace),'discrepancy':interval(discrepancy),
                                'original_P_and_pole_intervals_independently_contain_fresh_scalars':True,'complete_signed_identity_and_Stieltjes_control':True})
    A0=archimedean(Q(0));N=pins['retained_legendre_N'];R=Q(N,3)/T
    leakage=2*ball(T*R)/arb.pi()*ball(legendre_tail(T*R,N));closed_leakage=2*arb(N)/arb.pi()/arb(2)**N
    dR=archimedean(R)-A0+1
    if not (leakage<closed_leakage and leakage<1 and dR>1):raise ValueError('full logarithmic reference tail premise failed')
    mu=1+(dR-1)*(1-leakage)
    k=arb.pi()/(2*ball(T));norm_bound=2*sum((term.coefficient for term in terms),arb(0))+2*ball(T)+4*ball(T)*ball(T).exp()
    modulations=[]
    for frequency in pins['derivative_modulations']:
        derivative=(arb(frequency)**2+k*k).sqrt();energy_upper=3-A0+(1+arb(frequency)**2+k*k).log()/2
        def phi(l):return (2-l/ball(T))*(k*l).cos()+(k*l).sin()/(k*ball(T))
        arithmetic=sum((term.coefficient*phi(term.log_m)*(arb(frequency)*term.log_m).cos() for term in terms),arb(0))
        discrepancy=arithmetic-cosine_correlation_integral(Q(1,2),frequency,T)
        majorant=B*(2*derivative+1)
        if not (abs(discrepancy)<majorant and abs(discrepancy)<norm_bound):raise ValueError('H1 majorant or actual bounded discrepancy check failed')
        modulations.append({'modulation':frequency,'H1_derivative_norm':interval(derivative),'log_reference_energy_upper':interval(energy_upper),
                            'derivative_to_log_upper_ratio':interval(derivative/energy_upper),'absolute_H1_majorant':interval(majorant),
                            'actual_discrepancy_scalar':interval(discrepancy),'actual_form_remains_bounded':True})
    toys=[]
    for index in pins['compact_toy_phase_indices']:
        frequency=4*arb.pi()*index
        p_rayleigh=-sum((ball(Q(coef))*(2-ball(Q(shift)))*(frequency*ball(Q(shift))).cos() for shift,coef in zip(pins['compact_toy_shifts'],pins['compact_toy_coefficients'])),arb(0))
        compact=(frequency.sin()/frequency)**2
        if not (abs(p_rayleigh+ball(Q(7,2)))<tolerance and abs(compact)<ball(Q(1,2**800))):raise ValueError('commensurate phase/compact toy failed')
        toys.append({'phase_index':index,'arithmetic_rayleigh':interval(p_rayleigh),'rank_one_compact_form':interval(compact),
                     'not_a_Weil_test_or_prime_arithmetic_support':True})
    modules={};namespaces={}
    for name,module in sorted(sys.modules.items()):
        if name=='scripts' or name.startswith('scripts.'):
            if getattr(module,'__file__',None) is None:
                namespaces[name]=sorted({Path(path).resolve().relative_to(ROOT).as_posix() for path in module.__path__});continue
            path=Path(module.__file__).resolve();modules[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    return {'format':'energy-reference-qualification-controls-v1','status':'PASS','precision_bits':512,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_pins_sha256':hashlib.sha256(pins_path.read_bytes()).hexdigest(),
            'source_sha256':binding['source_sha256'],'fixed_support':str(T),'active_terms':[term.m for term in terms],
            'B_absolute_piecewise':interval(B),'B_closed':interval(closed_B),'all_post_jump_discrepancy_values_negative':True,
            'exact_correlation_controls':exact_overlap,'fixed_source_normalization_controls':source_controls,
            'positive_log_reference_tail':{'existing_N':N,'R':str(R),'full_band_leakage_upper_enclosure':interval(leakage),
                                           'closed_leakage_upper_enclosure':interval(closed_leakage),'mu_lower_enclosure':interval(mu),
                                           'not_a_complete_Weil_tail_bound':True},
            'H1_cosine_modulation_controls':modulations,'compact_commensurate_toys':toys,
            'useful_relative_alpha_b_proved':False,'new_support_matrix_computed':False,'new_low_positivity_sign_computed':False,
            'imported_project_module_sha256':modules,'namespace_package_paths':namespaces,
            'scope':'Exact/scalar normalization and toy controls for proved identities/obstructions; no new Weil sign, useful discrepancy-relative constants, formal proof or admission.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input-root',type=Path,default=ROOT);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=evaluate(args.input_root)
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:handle.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'fixed_source_scalar_modes':len(result['fixed_source_normalization_controls']),
                      'exact_correlation_controls':len(result['exact_correlation_controls']),'H1_modulations':len(result['H1_cosine_modulation_controls']),
                      'compact_toys':len(result['compact_commensurate_toys']),'useful_relative_alpha_b_proved':False,'new_support_matrix_computed':False}))
