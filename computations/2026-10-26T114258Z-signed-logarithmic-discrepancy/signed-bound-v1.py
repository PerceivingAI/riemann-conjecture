"""Fixed-support signed multiplier enclosure, not a Weil positivity certificate."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import heapq
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from flint import arb, acb, ctx
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms
from scripts.weil_reference_route_controls import ball, interval, archimedean, legendre_tail


def up(x):
    endpoint=arb_to_rational_enclosure(x)[1];scale=1<<128
    return Q((endpoint*scale).__ceil__(),scale)
def down(x):
    endpoint=arb_to_rational_enclosure(x)[0];scale=1<<128
    return Q((endpoint*scale).__floor__(),scale)


def evaluate():
    pins_path=Path(__file__).with_name('qualified-inputs-v1.json');pins=json.loads(pins_path.read_text(encoding='utf-8'))
    if (pins['support'],pins['alpha'],pins['certification_frequency_boundary'],pins['reference_legendre_N'])!=('3/4','1/4','256',312):raise ValueError('only declared fixed parameters supported')
    ctx.prec=pins['producer_precision_bits'];T=Q(pins['support']);alpha=Q(pins['alpha']);boundary=Q(pins['certification_frequency_boundary']);target=Q(pins['finite_supremum_gap_target'])
    terms=enumerate_active_prime_power_terms(3,4,prec=ctx.prec)
    if [term.m for term in terms]!=[2,3,4]:raise ValueError('incomplete active arithmetic')
    A0=archimedean(Q(0));exponential=ball(T).exp()
    S=2*sum((term.coefficient for term in terms),arb(0))
    lip=up(2*sum((term.coefficient*term.log_m for term in terms),arb(0))+8*ball(T)*(exponential-1))
    weights={}
    def weight(t):
        if t not in weights:weights[t]=archimedean(t)-A0+1
        return weights[t]
    def symbol(t):
        z=acb(ball(Q(1,2)),ball(t))
        continuous=((z*ball(2*T)).exp()-1)/z
        return 2*sum((term.coefficient*(ball(t)*term.log_m).cos() for term in terms),arb(0))-2*continuous.real
    heap=[];best_lower=None;witness=None;evaluations=0
    def add(left,right):
        nonlocal best_lower,witness,evaluations
        center=(left+right)/2;rho=symbol(center)
        bound=up(rho+ball(lip*(right-left)/2)-ball(alpha)*weight(left))
        low=down(rho-ball(alpha)*weight(center))
        if best_lower is None or low>best_lower:best_lower=low;witness=center
        heapq.heappush(heap,(-bound,left,right));evaluations+=1
    width=Q(pins['initial_interval_width']);count=int(boundary/width)
    if count*width!=boundary:raise ValueError('initial cover does not partition proof interval')
    for i in range(count):add(i*width,(i+1)*width)
    refinements=0
    while -heap[0][0]-best_lower>target:
        negative,left,right=heapq.heappop(heap);center=(left+right)/2
        add(left,center);add(center,right);refinements+=1
    finite_upper=-heap[0][0]
    denominator=ball(boundary*boundary+Q(1,4))
    # Triangle envelope of the complex quotient; verifier uses sharper real formula.
    infinite_upper=up(S+2*(exponential+1)/denominator.sqrt()-ball(alpha)*weight(boundary))
    raw_beta=max(Q(0),finite_upper,infinite_upper);grid=Q(pins['publication_beta_grid'])
    beta=Q((raw_beta/grid).__ceil__())*grid
    N=pins['reference_legendre_N'];reference=[]
    for label,R in [('closed_policy',Q(N,3)/T),('retained_source_anchor',boundary)]:
        leakage=2*ball(T*R)/arb.pi()*ball(legendre_tail(T*R,N))
        if not leakage<1:raise ValueError('reference band leakage not below one')
        mu=1+(archimedean(R)-A0)*(1-leakage)
        margin=(1-ball(alpha))*mu+A0-1-ball(beta)
        reference.append({'label':label,'R':str(R),'full_band_leakage':interval(leakage),'mu_lower':str(down(mu)),
                          'outside_lower':str(down(margin)),'outside_upper':str(up(margin)),
                          'outside_lower_positive':down(margin)>0})
    cells=[{'left':str(left),'right':str(right),'upper':str(-negative)} for negative,left,right in sorted(heap,key=lambda row:row[1])]
    current=Q(0)
    for cell in cells:
        if Q(cell['left'])!=current or Q(cell['right'])<=current:raise ValueError('coverage defect')
        current=Q(cell['right'])
    if current!=boundary or finite_upper-best_lower>target:raise ValueError('finite certification incomplete')
    modules={};namespaces={}
    for name,module in sorted(sys.modules.items()):
        if name=='scripts' or name.startswith('scripts.'):
            if getattr(module,'__file__',None) is None:
                namespaces[name]=sorted({Path(path).resolve().relative_to(ROOT).as_posix() for path in module.__path__});continue
            path=Path(module.__file__).resolve();modules[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    return {'format':'research-signed-log-discrepancy-v1','status':'GLOBAL_FORM_BOUND_CERTIFIED',
            'scope':'Fixed T3/4 global frequency/form bound, not a full Weil positivity certificate or production admission.',
            'support':'3/4','alpha':'1/4','frequency_proof_boundary':str(boundary),'reference_N':N,
            'producer_precision_bits':pins['producer_precision_bits'],'source_publication_bits':128,
            'active_terms':[term.m for term in terms],'coarse_lipschitz_upper':str(lip),
            'finite_gap_target':str(target),'finite_max_lower':str(best_lower),'finite_max_upper':str(finite_upper),
            'lower_witness_frequency':str(witness),'infinite_tail_upper':str(infinite_upper),'beta':str(beta),
            'reference_tail_controls':reference,'cells':cells,'interval_evaluations':evaluations,'refinements':refinements,
            'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'qualified_inputs_sha256':hashlib.sha256(pins_path.read_bytes()).hexdigest(),
            'imported_project_module_sha256':modules,'namespace_package_paths':namespaces,
            'new_support_matrix_computed':False,'complete_low_cross_positivity_proved':False,'all_support_estimate_proved':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();result=evaluate()
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:handle.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'leaf_intervals':len(result['cells']),'beta':result['beta'],
                      'reference_tails':[{key:r[key] for key in ['label','outside_lower','outside_lower_positive']} for r in result['reference_tail_controls']],
                      'new_support_matrix_computed':False,'all_support_estimate_proved':False}))
