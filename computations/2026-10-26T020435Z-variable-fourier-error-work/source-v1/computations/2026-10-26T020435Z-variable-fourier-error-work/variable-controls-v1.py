"""Declared scalar/exact controls for variable error bounds; no low matrix/sign."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from flint import arb, acb, ctx
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms
from scripts.weil_reference_route_controls import ball, interval, archimedean, legendre_tail
from scripts.verify_m4_fourier_matrix import finite_hypergeometric


def upper(x):return arb_to_rational_enclosure(x)[1]
def lower(x):return arb_to_rational_enclosure(x)[0]
def ceil_q(x):return -((-x.numerator)//x.denominator)
def ceil_log2(x):
    if x<=0:raise ValueError('positive logarithm argument required')
    n=x.numerator.bit_length()-x.denominator.bit_length()
    power=Q(2)**n
    return n+(power<x)


def hyper_tail(U,b,K):
    term=Q(1)
    for k in range(1,K+2):term*=U/(k*(b+k-1))
    ratio=U/((K+2)*(b+K+1))
    if not 0<=ratio<1:raise ValueError('noncontracting entire tail')
    return term/(1-ratio)


def mass_factor(n):
    result=[]
    for parity in (0,1):
        degrees=list(range(parity,n,2))
        if not degrees:continue
        value=arb(len(degrees))+sum((ball(Q(2*degrees[-1]+1,2*j+1)).sqrt() for j in degrees),arb(0))
        result.append(value)
    return max(upper(value) for value in result)


def evaluate():
    ctx.prec=512
    pins_path=Path(__file__).with_name('input-pins.json');pins=json.loads(pins_path.read_text(encoding='utf-8'))
    for item in pins['inputs']:
        raw=(ROOT/item['path']).read_bytes()
        if len(raw)!=item['bytes'] or hashlib.sha256(raw).hexdigest()!=item['sha256']:raise ValueError('inherited input bytes changed')
    for binding in pins['bindings']:
        seal=json.loads((ROOT/binding['manifest']).read_text(encoding='utf-8'))
        member=next(x for x in seal['members'] if x['path']==binding['member'])
        raw=(ROOT/binding['path']).read_bytes()
        if member['bytes']!=len(raw) or member['sha256']!=hashlib.sha256(raw).hexdigest():raise ValueError('input is not bound by inherited seal')
    old=json.loads((ROOT/pins['reference_controls']).read_text(encoding='utf-8'))
    previous=json.loads((ROOT/pins['pointwise_assessment']).read_text(encoding='utf-8'))
    delta=Q(pins['compact_schur_loss_target']);theta=Q(pins['theta']);ell_quad=Q(pins['boxed_quadrature_order_loss_target']);ell_pub=Q(pins['publication_order_loss_target'])
    toy_tails=[]
    for z_text in pins['toy_tail_arguments']:
        z=Q(z_text);n=max(1,ceil_q(3*z));actual=legendre_tail(z,n);bound=Q(3,2**n)
        if not actual<bound:raise ValueError('closed geometric-tail inequality failed')
        toy_tails.append({'z':str(z),'N':n,'tail':str(actual),'closed_upper':str(bound)})
    try:legendre_tail(Q(4),1)
    except ValueError:geometric_rejection=True
    else:raise ValueError('noncontracting geometric denominator accepted')
    # Exact interval-recurrence countercontrol. These anchors are toy data, not Bessel values.
    toy_errors=[Q(0),Q(0)];toy_centers={3:Q(0),2:Q(1),1:Q(10,3),0:Q(17,3)}
    e2=e3=Q(0)
    for n in (2,1):
        ahi=Q(2*n+1);alo=ahi/2;ahat=Q(2*n+1)*Q(2,3)
        variation=max(ahat-alo,ahi-ahat)
        enext=ahi*e2+e3+variation*abs(toy_centers[n]);e3,e2=e2,enext
    if e2!=Q(25,3):raise ValueError('uncertain-reciprocal propagation normalization failed')
    if abs(Q(14)-toy_centers[0])!=e2:raise ValueError('endpoint countercontrol failed')
    if abs(Q(14)-toy_centers[0])<=0:raise ValueError('midpoint omission countercontrol failed')
    entire_checks=[]
    for alternating in (True,False):
        w=ball(Q(3,2));enclosed=finite_hypergeometric(0,w,pins['toy_entire_terms'],alternating)
        direct=(w.sin() if alternating else w.sinh())/w
        if not (lower(enclosed)<=lower(direct) and upper(direct)<=upper(enclosed)):raise ValueError('independent sine/sinh series control failed')
        entire_checks.append({'alternating':alternating,'independent_closed_form_enclosed':True})
    cases=[]
    for prior in old['existing_case_controls']:
        T=Q(prior['support']);a=Q(prior['a']);omega=Q(256);p=Q(prior['published_simple_p_upper']);m=a-p
        W=max(upper(abs(archimedean(Q(0))-ball(a))),upper(abs(archimedean(omega)-ball(a))))
        beta=2*ball(T*omega)/arb.pi();H=4*ball(T)*ball(T).exp()
        L=ball(W)*beta+H;J=ball(W)*beta.sqrt()+H
        R=delta*(1-theta)*m/2;eta0=ball(R)/((ball(p*p+R)).sqrt()+ball(p))
        kappa0=min(theta*m,delta*(1-theta)*m*m/(2*p*p)) if p else theta*m
        xi=min(kappa0/upper(L),(lower(eta0)/upper(J))**2)
        n=max(1,ceil_q(3*max(T*omega,T/2)),ceil_log2(3/xi))
        if not Q(3,2**n)<=xi:raise ValueError('derived sufficient N misses declared target')
        def complement(order):
            plane=ball(legendre_tail(T*omega,order));polar=ball(legendre_tail(T/2,order))
            k=ball(W)*beta*plane+H*polar;e=ball(W)*(beta*plane).sqrt()+H*polar.sqrt()
            d=ball(m)-k;eps=2*ball(p)*e+e*e
            if not d>0:raise ValueError('outside denominator nonpositive')
            loss=eps/d+ball(p*p)*k/(d*ball(m))
            return k,e,d,loss
        k,e,d,loss=complement(n)
        if not (k<ball(kappa0) and e<ball(lower(eta0)) and loss<ball(delta)):raise ValueError('sufficient compact-loss policy failed')
        retained=complement(312)
        if prior['label']=='post_transition':
            if not (retained[0]<ball(Q(previous['scalars']['kappa_upper'])) and 2*ball(p)*retained[1]+retained[1]**2<ball(Q(previous['scalars']['mixed_Gram_upper']))):raise ValueError('old pointwise compact controls changed')
        rho=Q(1,4)/max(Q(1),T);panels=ceil_q(omega/rho);h=omega/(2*panels)
        strip=Q(1,4)-rho/2;Lpsi=Q(3,4)+omega/2+rho;B=a+3+Lpsi*(1/strip+1)
        Cquad=8*ball(T*omega)/arb.pi()*ball(B)*(2*ball(T*rho)).exp()
        F=mass_factor(n);quad_target=ell_quad/F
        q=max(1,ceil_log2(upper(Cquad)/quad_target)//2)
        if Q(2)**(2*q)*quad_target<upper(Cquad):q+=1
        error_upper=upper(Cquad)/Q(2)**(2*q)
        if F*error_upper>ell_quad:raise ValueError('boxed analytic quadrature budget failed')
        block=(n+1)//2;pubfactor=block*(2*n-1);bits=max(0,ceil_log2(Q(pubfactor)/ell_pub))
        if Q(pubfactor,2**bits)>ell_pub:raise ValueError('true-to-ordered publication budget failed')
        terms=enumerate_active_prime_power_terms(T.numerator,T.denominator,prec=512)
        ids=[x.m for x in terms];signed=[sign*x.tau for x in terms for sign in (-1,1)]
        d2=0
        for alpha in signed:
            for beta_shift in signed:
                # The active cases have no unresolved breakpoint equality.
                span=max(arb(0),alpha,beta_shift)-min(arb(0),alpha,beta_shift)
                if span<2:d2+=1
                elif not span>2:raise ValueError('unresolved pair-domain threshold')
        mixed=0
        for left in terms:
            for right in terms:
                total=left.log_m+right.log_m
                if total<2*ball(T):mixed+=1
                elif not total>2*ball(T):raise ValueError('unresolved mixed-pair threshold')
        if d2!=2*len(ids)**2+2*mixed:raise ValueError('complete pair-domain count failed')
        points=sorted([x.tau-1 for x in terms]+[1-x.tau for x in terms])
        if not all(x<y for x,y in zip(points,points[1:])):raise ValueError('unresolved cell ordering')
        cells=len(points)+1-(1 if terms[0].tau>1 else 0)
        expected=(4,8) if prior['label']=='baseline' else (7,20)
        if (cells,d2)!=expected:raise ValueError('retained geometry count changed')
        # Analytic anchor-tail policy on a declared positive argument interval, not a new frequency node.
        wminus=T*omega/2-Q(pins['anchor_halfwidth']);wplus=T*omega/2+Q(pins['anchor_halfwidth']);N=312
        gain0=gain1=arb(1);gain_upper=Q(1)
        for degree in range(N,0,-1):
            next_gain=ball(Q(2*degree+1)/wminus)*gain0+gain1;gain1,gain0=gain0,next_gain
            gain_upper=max(gain_upper,upper(next_gain))
        prefactor=max(upper(ball(wplus)**degree/math.prod(range(1,2*degree+2,2))) for degree in (N,N+1))
        vector_target=Q(pins['anchor_vector_tail_target']);tau=vector_target/(2*gain_upper*prefactor)
        U=wplus*wplus/4;b=Q(2*N+3,2);first=max(1,ceil_q(6*U/b),ceil_log2(2/tau));tail=hyper_tail(U,b,first-1)
        propagated=2*gain_upper*prefactor*tail
        if not propagated<=vector_target:raise ValueError('full prefactor/recurrence analytic-tail policy failed')
        envelopes=[]
        for xr,yi in [(Q(0),Q(0)),(omega,Q(0)),(omega/2,rho),(-rho,rho)]:
            z=acb(ball(xr),ball(yi));splus=acb(ball(Q(1,4)))+acb(0,1)*z/2;sminus=acb(ball(Q(1,4)))-acb(0,1)*z/2
            direct=(splus.digamma()+sminus.digamma())/2-arb.pi().log()-ball(a)
            def prefix(s):return -arb.const_euler()+sum((1/(arb(k)+1)-1/(arb(k)+s) for k in range(pins['digamma_prefix_terms'])),acb(0))
            finite=(prefix(splus)+prefix(sminus))/2-arb.pi().log()-ball(a)
            if not (abs(direct)<ball(B) and abs(direct-finite)<ball(Lpsi/pins['digamma_prefix_terms'])):raise ValueError('complex strip envelope or finite digamma remainder failed')
            envelopes.append({'z_real':str(xr),'z_imag':str(yi),'envelope_and_prefix_remainder_checked':True})
        ne,no=(n+1)//2,n//2;B2=ne*ne+no*no;B3=ne**3+no**3
        source_proxy=2*cells*B2*n+B2*panels*q+B3
        audit_proxy=(2*len(ids)+d2)*n*n*(n+1)+n*n*panels*q+n**3
        cases.append({'label':prior['label'],'support':str(T),'a':str(a),'Omega':str(omega),'p_upper':str(p),'m':str(m),'W_upper':str(W),
                      'retained_N312_kappa':interval(retained[0]),'retained_N312_eta':interval(retained[1]),
                      'derived_sufficient_N_for_declared_loss':n,'dimension_is_scalar_policy_not_a_matrix_experiment':True,
                      'kappa':interval(k),'eta':interval(e),'outside_denominator_lower_enclosure':interval(d),'compact_Sstar_loss_upper_enclosure':interval(loss),
                      'rho':str(rho),'panels':panels,'panel_halfwidth':str(h),'complex_envelope_B':str(B),
                      'mass_order_loss_factor_upper':str(F),'frequency_order':q,'frequency_nodes':panels*q,'boxed_quadrature_order_loss_upper':str(F*error_upper),
                      'publication_bits_for_declared_order_loss':bits,'publication_order_loss_upper':str(Q(pubfactor,2**bits)),
                      'active_terms':ids,'nonempty_cells':cells,'ordered_square_domains':d2,
                      'analytic_anchor_policy':{'anchor_N':N,'argument_interval':[str(wminus),str(wplus)],'first_omitted_index':first,
                                                'positive_recurrence_gain_upper_display':ball(gain_upper).str(16),'propagated_transform_tail_upper_display':ball(propagated).str(16),'target':str(vector_target)},
                      'complex_envelope_controls':envelopes,'six_triangle_slots':3*n*(n+1),
                      'classical_contraction_volume_source':source_proxy,'classical_contraction_volume_audit':audit_proxy,
                      'source_and_audit_precision_or_runtime_not_predicted':True})
    modules={};namespaces={}
    for name,module in sorted(sys.modules.items()):
        if name=='scripts' or name.startswith('scripts.'):
            if getattr(module,'__file__',None) is None:
                namespaces[name]=sorted({Path(path).resolve().relative_to(ROOT).as_posix() for path in module.__path__});continue
            path=Path(module.__file__).resolve();modules[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    return {'format':'variable-fourier-error-work-controls-v1','status':'PASS','precision_bits':512,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_pins_sha256':hashlib.sha256(pins_path.read_bytes()).hexdigest(),
            'toy_tail_controls':toy_tails,'noncontracting_geometric_denominator_rejected':geometric_rejection,
            'uncertain_recurrence_countercontrol':{'true_w1_value':'14','midpoint_value':'17/3','propagated_radius':'25/3','midpoint_without_argument_width_is_rejected':True},
            'entire_closed_form_controls':entire_checks,'existing_case_controls':cases,'retained_N312_mass_factor_upper':str(mass_factor(312)),
            'imported_project_module_sha256':modules,'namespace_package_paths':namespaces,'new_support_matrix_computed':False,
            'scope':'Scalar/exact checks of proved sufficient policies, not new source matrices, low positivity, precision law, runtime measurement or admission.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=evaluate()
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:handle.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'existing_cases':len(result['existing_case_controls']),
                      'toy_tail_controls':len(result['toy_tail_controls']),'entire_closed_form_controls':len(result['entire_closed_form_controls']),
                      'new_support_matrix_computed':False}))
