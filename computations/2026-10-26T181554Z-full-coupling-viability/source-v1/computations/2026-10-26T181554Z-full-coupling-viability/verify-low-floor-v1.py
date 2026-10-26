"""Independent exact-polynomial and full-source audit, without producer imports."""
import argparse,gzip,hashlib,json,math
from fractions import Fraction as Q
from pathlib import Path
from flint import arb,ctx,fmpq,fmpq_poly
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PIN='cd254a2a7002e17b56dce12a0ec00166eac8023e30374e38053d8963ade28b9c'
def fq(x):x=Q(x);return fmpq(x.numerator,x.denominator)
def rat(x):return Q(int(x.numerator),int(x.denominator))
def ball(x):x=Q(x);return arb(x.numerator)/x.denominator
def ends(x):return rat(x.lower().fmpq()),rat(x.upper().fmpq())
def contain(label,pair,value):
    l,h=ends(value)
    if not Q(pair['lower'])<=l<=h<=Q(pair['upper']):raise ValueError(label+' enclosure')
def upper(label,bound,value):
    if Q(bound)<ends(value)[1]:raise ValueError(label+' upper too small')
def integ(poly):return sum((2*rat(c)/Q(i+1) for i,c in enumerate(poly) if i%2==0),Q(0))
def explicit_legendre(n):
    c=[fmpq(0) for _ in range(n+1)]
    for k in range(n//2+1):c[n-2*k]=fq(Q((-1)**k*math.comb(n,k)*math.comb(2*n-2*k,n),1<<n))
    return fmpq_poly(c)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('packet',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise ValueError('fresh audit output required')
    packet_raw=a.packet.read_bytes();p=json.loads(packet_raw);version=1 if p['format']=='whole-space-residual-floor-assessment-v1' else 2 if p['format']=='whole-space-residual-floor-assessment-v2' else 0
    if not version:raise ValueError('known scientific format')
    inputs_path=HERE/f'residual-completion-inputs-v{version}.json';decl_raw=inputs_path.read_bytes();decl=json.loads(decl_raw)
    if hashlib.sha256(decl_raw).hexdigest()!=p['inputs_sha256'] or p['producer_sha256']!=hashlib.sha256((HERE/f'assess-low-floor-v{version}.py').read_bytes()).hexdigest():raise ValueError('source binding')
    old_raw=(ROOT/decl['bounded_source']).read_bytes()
    if hashlib.sha256(old_raw).hexdigest()!=PIN or p['old_source_sha256']!=PIN:raise ValueError('accepted source identity')
    old=json.loads(gzip.decompress(old_raw))
    if (old['support'],old['dimension'],old['basis'],old['active_terms'],old['a'],old['omega'])!=([3,4],312,'ordinary_unnormalized_legendre',[2,3,4],'7/2',256):raise ValueError('source meaning')
    if p['N']!=312 or p['support']!='3/4' or p['residual_allowance']!='1/300000' or p['isotropic_floor']!='1/30000000000':raise ValueError('fixed full-operator test')
    if p['exact_supported_criterion_rejected'] or p['actual_Weil_negative_claim'] or p['new_support_or_admission']:raise ValueError('false mathematical scope')
    ctx.prec=2048;pi=arb.pi();scalar=(128/pi).log()-ball(Q(27,8));assert scalar<ball(Q(1,2));contain('complete exterior scalar',p['exterior_log_scalar_check'],scalar)
    alpha=8 if version==1 else 4;X=fmpq_poly([0,1]);plus=[fmpq_poly([1])];minus=[fmpq_poly([1])]
    maxn=max(max(w['jacobi_degrees']) for w in p['witnesses'])
    for n in range(maxn):plus.append(plus[-1]*(X+1));minus.append(minus[-1]*(X-1))
    summaries=[]
    if len(p['witnesses'])!=2:raise ValueError('both parity outcomes required')
    for parity,row in enumerate(p['witnesses']):
        if row['parity']!=parity or row['jacobi_degrees']!=list(range(parity,304,2)):raise ValueError('complete constrained coefficients')
        coeff=row['jacobi_coefficients_grid40']
        if len(coeff)!=152:raise ValueError('coefficient extent')
        poly=fmpq_poly([0])
        for n,c in zip(row['jacobi_degrees'],coeff):
            if not c:continue
            # Explicit binomial Jacobi identity, not producer recurrence.
            j=fmpq_poly([0])
            for k in range(n+1):j+=math.comb(n+alpha,k)*math.comb(n+alpha,n-k)*minus[n-k]*plus[k]
            poly+=fq(Q(c,(1<<40)*(1<<n)))*j
        poly*=fmpq_poly([1,0,-1])**4;degree=poly.degree()
        if degree!=row['actual_degree'] or not 0<=degree<312:raise ValueError('actual degree')
        leg=[]
        for n in range(degree+1):leg.append(Q(2*n+1,2)*integ(poly*explicit_legendre(n)))
        if list(map(Q,row['exact_legendre_coefficients']))!=leg:raise ValueError('independent Legendre moments')
        norm=sum(Q(2,2*n+1)*c*c for n,c in enumerate(leg))
        if norm<=0 or Q(row['exact_mass'])!=norm or integ(poly*poly)!=norm:raise ValueError('exact physical mass')
        lo=Q(0);hi=Q(0)
        # Exact signed rational interval contraction, not Arb radius accumulation.
        for i,ci in enumerate(leg):
            if not ci:continue
            for j in range(i,len(leg)):
                cj=leg[j]
                if not cj:continue
                q=(1 if i==j else 2)*ci*cj
                l,h=(Q(v,1<<old['bits']) for v in old['matrices']['A'][i][j-i])
                lo+=min(q*l,q*h);hi+=max(q*l,q*h)
        if not Q(row['bounded_source_quadratic']['lower'])<=lo<=hi<=Q(row['bounded_source_quadratic']['upper']):raise ValueError('actual bounded source enclosure')
        power=[rat(v) for v in poly];trace=[]
        for k in range(degree+1):
            left=Q(0);right=Q(0)
            for n in range(k,len(power)):
                term=power[n]*Q(math.factorial(n),math.factorial(n-k));right+=term;left+=(-1)**(n-k)*term
            if k<4 and (left or right):raise ValueError('endpoint jets')
            trace.append(abs(left)+abs(right))
        deriv=fmpq_poly([fq(power[n]*n*(n-1)*(n-2)*(n-3)) for n in range(4,len(power))]);dnorm=integ(deriv*deriv)
        if Q(row['fourth_derivative_norm_squared'])!=dnorm:raise ValueError('fourth derivative mass')
        sob=dnorm/Q(2*192**8)
        if Q(row['complete_sobolev_exterior_upper'])!=sob:raise ValueError('complete Sobolev exterior')
        endpoint_rational=Q(0)
        # Aggregate by derivative sum rather than producer's paired integral loop.
        for s in range(9,2*degree+2):
            coefficient=sum((trace[k]*trace[s-1-k] for k in range(4,degree+1) if 4<=s-1-k<=degree),Q(0))
            endpoint_rational+=coefficient*Q(s+2,2*s*s*192**s)
        ep=ball(endpoint_rational)/pi;contain('full endpoint exterior',row['complete_endpoint_exterior'],ep)
        outside=Q(row['complete_exterior_used_upper'])
        if not outside>=min(sob,ends(ep)[1]):raise ValueError('unpaid complete exterior')
        actual=(ball(hi)+ball(outside))/ball(norm)
        upper('actual full Weil quotient',row['actual_Weil_rayleigh_enclosure_upper'],actual)
        completion=actual-ball(Q(1,30000000000));upper('whole completion quotient',row['norm_completion_rayleigh_upper'],completion)
        sign=Q(row['norm_completion_rayleigh_upper'])<0
        if row['strict_floor_rejection']!=sign:raise ValueError('false rejection flag')
        summaries.append({'parity':parity,'degree':degree,'mass_exact':True,'endpoint_jets_exact':True,'bounded_source_and_full_exterior_checked':True,'actual_Weil_rayleigh_upper':row['actual_Weil_rayleigh_enclosure_upper'],'whole_norm_completion_upper':row['norm_completion_rayleigh_upper'],'strict_floor_rejection':sign})
    if p['norm_completion_rejected_on_whole312']!=any(w['strict_floor_rejection'] for w in summaries):raise ValueError('whole-criterion scope flag')
    result={'format':'independent-whole-low-floor-audit-v1','status':'PASS_COMPLETE_SOURCE_AND_EXTERIOR','source_variant':version,'packet_sha256':hashlib.sha256(packet_raw).hexdigest(),'audit_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'precision_bits':2048,'witnesses':summaries,'norm_completion_rejected_on_whole312':p['norm_completion_rejected_on_whole312'],'exact_supported_criterion_rejected':False,'old_source_reused_as_two_sided_H0_not_actual_Weil_A':True,'new_support_or_admission':False}
    with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps(result))
if __name__=='__main__':
    try:main()
    except (ValueError,AssertionError,KeyError,ZeroDivisionError) as e:raise SystemExit(type(e).__name__+': '+str(e))
