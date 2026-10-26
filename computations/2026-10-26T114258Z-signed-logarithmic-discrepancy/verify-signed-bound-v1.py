"""Independent fixed-case scalar enclosure replay; not theorem admission."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from math import factorial
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from flint import arb, acb, ctx
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms


def rational(text):
    if not isinstance(text,str):raise ValueError('exact rational string required')
    value=Q(text)
    if str(value)!=text:raise ValueError('noncanonical rational')
    return value

def aq(value):
    value=Q(value);return arb(value.numerator)/value.denominator

def lo(value):return arb_to_rational_enclosure(value)[0]
def hi(value):return arb_to_rational_enclosure(value)[1]
def ceiling128(value):
    scale=1<<128;return Q((hi(value)*scale).__ceil__(),scale)

def no_float(text):raise ValueError('nonexact JSON number')


def audit(path):
    ctx.prec=384;raw=path.read_bytes();packet=json.loads(raw,parse_float=no_float,parse_constant=no_float)
    if (packet['format'],packet['support'],packet['alpha'],packet['frequency_proof_boundary'],packet['reference_N'])!=('research-signed-log-discrepancy-v1','3/4','1/4','256',312):raise ValueError('unauthorized fixed parameters')
    producer=Path(__file__).with_name('signed-bound-v1.py');pins_path=Path(__file__).with_name('qualified-inputs-v1.json')
    if hashlib.sha256(producer.read_bytes()).hexdigest()!=packet['producer_sha256'] or hashlib.sha256(pins_path.read_bytes()).hexdigest()!=packet['qualified_inputs_sha256']:raise ValueError('source/pin fingerprint changed')
    T=Q(3,4);alpha=Q(1,4);boundary=Q(256);N=312
    terms=enumerate_active_prime_power_terms(3,4,prec=384)
    if packet['active_terms']!=[term.m for term in terms] or [term.m for term in terms]!=[2,3,4]:raise ValueError('complete active terms changed')
    pi=arb.pi();exponential=aq(T).exp()
    def A(t):return acb(aq(Q(1,4)),aq(t)/2).digamma().real-pi.log()
    A0=A(Q(0));direct_weights={};independent_weights={}
    def w(t):
        if t not in direct_weights:direct_weights[t]=A(t)-A0+1
        return direct_weights[t]
    def w_lower(t):
        if t not in independent_weights:
            y=aq(t)/2;ysquare=y*y
            prefix=arb(1)+sum((ysquare/((aq(k)+aq(Q(1,4)))*((aq(k)+aq(Q(1,4)))**2+ysquare)) for k in range(128)),arb(0))
            bound=lo(prefix)
            if t>0:bound=max(bound,lo((aq(t)/(2*pi)).log()-2/aq(t)**2-A0+1))
            independent_weights[t]=bound
        return independent_weights[t]
    def rho(t):
        tball=aq(t);den=tball*tball+aq(Q(1,4));phase=2*aq(T)*tball
        arithmetic=2*sum((term.coefficient*(term.log_m*tball).cos() for term in terms),arb(0))
        return arithmetic-2*exponential*(aq(Q(1,2))*phase.cos()+tball*phase.sin())/den+1/den
    arithmetic_lip=2*sum((term.coefficient*term.log_m for term in terms),arb(0))
    coarse=arithmetic_lip+8*aq(T)*(exponential-1)
    sharp=arithmetic_lip+8*((aq(T)-1)*exponential+1)
    claimed_lip=rational(packet['coarse_lipschitz_upper'])
    if hi(coarse)>claimed_lip or not 0<sharp<coarse:raise ValueError('invalid Lipschitz constant')
    beta=rational(packet['beta']);grid=Q(1,1024)
    if beta<0 or (beta/grid).denominator!=1:raise ValueError('invalid published beta')
    current=Q(0);claimed_max=None;independent_max=None;checked=0
    for cell in packet['cells']:
        left,right=rational(cell['left']),rational(cell['right']);claimed=rational(cell['upper'])
        if left!=current or not left<right<=boundary:raise ValueError('frequency coverage gap/overlap/order defect')
        center=(left+right)/2;symbol=rho(center)
        fresh_coarse=symbol+aq(claimed_lip*(right-left)/2)-aq(alpha)*w(left)
        if hi(fresh_coarse)>claimed:raise ValueError('dishonest per-interval source enclosure')
        fresh_independent=symbol+sharp*aq((right-left)/2)-aq(alpha*w_lower(left))
        if hi(fresh_independent)>beta:raise ValueError('independent all-frequency interval bound exceeds beta')
        claimed_max=claimed if claimed_max is None else max(claimed_max,claimed)
        independent_max=hi(fresh_independent) if independent_max is None else max(independent_max,hi(fresh_independent))
        current=right;checked+=1
    if current!=boundary or not checked:raise ValueError('incomplete finite frequency cover')
    if claimed_max!=rational(packet['finite_max_upper']) or claimed_max>beta:raise ValueError('finite maximum not bound by published beta')
    witness=rational(packet['lower_witness_frequency']);lower_claim=rational(packet['finite_max_lower'])
    if not 0<=witness<=boundary or lower_claim>lo(rho(witness)-aq(alpha)*w(witness)):raise ValueError('invalid finite lower witness')
    if claimed_max-lower_claim>Q(1,256):raise ValueError('declared finite enclosure gap not achieved')
    S=2*sum((term.coefficient for term in terms),arb(0));den=aq(boundary*boundary+Q(1,4))
    source_tail=S+2*(exponential+1)/den.sqrt()-aq(alpha)*w(boundary)
    if hi(source_tail)>rational(packet['infinite_tail_upper']):raise ValueError('dishonest source infinite tail')
    independent_tail=S+2*exponential/den.sqrt()+1/den-aq(alpha*w_lower(boundary))
    if hi(independent_tail)>beta:raise ValueError('independent infinite-frequency bound exceeds beta')
    raw_beta=max(Q(0),claimed_max,rational(packet['infinite_tail_upper']))
    if beta!=Q((raw_beta/grid).__ceil__())*grid:raise ValueError('beta publication rule changed')
    reference=[]
    for source_row,(label,R) in zip(packet['reference_tail_controls'],[('closed_policy',Q(N,3)/T),('retained_source_anchor',boundary)],strict=True):
        if source_row['label']!=label or rational(source_row['R'])!=R:raise ValueError('reference anchor changed')
        c=T*R;ratio=c*c/((2*N+1)*(2*N+3))
        if not 0<=ratio<1:raise ValueError('invalid complete-tail geometric ratio')
        doublefac=factorial(2*N+1)//(2**N*factorial(N))
        E=Q(2*N+1)*c**(2*N)/doublefac**2/(1-ratio)
        leakage=2*aq(T*R)/pi*aq(E)
        if not leakage<1:raise ValueError('complete band leakage too large')
        mu=1+(w(R)-1)*(1-leakage)
        margin=(1-aq(alpha))*mu+A0-1-aq(beta)
        if rational(source_row['mu_lower'])>lo(mu) or rational(source_row['outside_lower'])>lo(margin) or rational(source_row['outside_upper'])<hi(margin):raise ValueError('dishonest source reference margin')
        if source_row['outside_lower_positive']!=(rational(source_row['outside_lower'])>0):raise ValueError('dishonest source sign label')
        independent_mu=1+aq(w_lower(R)-1)*(1-leakage)
        independent_margin=(1-aq(alpha))*independent_mu+A0-1-aq(beta)
        reference.append({'label':label,'R':str(R),'independent_outside_lower':str(Q((lo(independent_margin)*(1<<128)).__floor__(),1<<128)),
                          'independent_outside_positive':lo(independent_margin)>0,'independent_outside_above_one_third':lo(independent_margin)>Q(1,3)})
    modules={};namespaces={}
    for name,module in sorted(sys.modules.items()):
        if name=='scripts' or name.startswith('scripts.'):
            if getattr(module,'__file__',None) is None:
                namespaces[name]=sorted({Path(p).resolve().relative_to(ROOT).as_posix() for p in module.__path__});continue
            file=Path(module.__file__).resolve();modules[file.relative_to(ROOT).as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest()
    return {'format':'signed-logarithmic-discrepancy-audit-v1','status':'PASS','source_sha256':hashlib.sha256(raw).hexdigest(),
            'audit_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'audit_precision_bits':384,'complete_intervals_checked':checked,
            'beta':str(beta),'independent_finite_upper':str(ceiling128(aq(independent_max))),
            'independent_infinite_tail_upper':str(ceiling128(independent_tail)),
            'reference_tail_controls':reference,'independent_energy_lower_organization':'128 positive digamma-difference summands plus explicit log remainder bound',
            'symbol_organization':'real trigonometric quotient rather than producer complex exponential quotient',
            'imported_project_module_sha256':modules,'namespace_package_paths':namespaces,
            'new_support_matrix_computed':False,'complete_low_cross_positivity_proved':False,'all_support_estimate_proved':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    try:result=audit(args.source)
    except (ValueError,KeyError,TypeError,ZeroDivisionError) as exc:
        print(json.dumps({'status':'REJECTED','error':str(exc)}));raise SystemExit(2)
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:handle.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'PASS','complete_intervals_checked':result['complete_intervals_checked'],'beta':result['beta'],
                      'reference_tails':result['reference_tail_controls'],'new_support_matrix_computed':False}))
