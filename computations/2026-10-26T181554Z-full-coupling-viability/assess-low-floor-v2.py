"""Exact low witness and complete exterior test of isotropic residual completion."""
import argparse,gzip,hashlib,json,math
from pathlib import Path
from fractions import Fraction as Q
from flint import arb,ctx,fmpq,fmpq_poly
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SHA='cd254a2a7002e17b56dce12a0ec00166eac8023e30374e38053d8963ade28b9c'
def qa(q):q=Q(q);return arb(q.numerator)/q.denominator
def fq(q):q=Q(q);return fmpq(q.numerator,q.denominator)
def qq(q):return Q(int(q.numerator),int(q.denominator))
def ends(v):return qq(v.lower().fmpq()),qq(v.upper().fmpq())
def publish(v):
    l,h=ends(v);s=1<<96
    return {'lower':str(Q(math.floor(l*s)-1,s)),'upper':str(Q(math.ceil(h*s)+1,s))}
def integral(p):
    q=p.integral();return qq(q(fmpq(1))-q(fmpq(-1)))
def jacobi_polys(count,alpha):
    p=[fmpq_poly([1]),fmpq_poly([0,alpha+1])];X=fmpq_poly([0,1])
    for n in range(1,count-1):p.append(((2*n+2*alpha+1)*(2*n+2*alpha)*(2*n+2*alpha+2)*X*p[-1]-2*(n+alpha)**2*(2*n+2*alpha+2)*p[-2])/(2*(n+1)*(n+2*alpha+1)*(2*n+2*alpha)))
    return p[:count]
def legendre_polys(count):
    p=[fmpq_poly([1]),fmpq_poly([0,1])];X=fmpq_poly([0,1])
    for n in range(1,count-1):p.append(((2*n+1)*X*p[-1]-n*p[-2])/(n+1))
    return p[:count]
def main():
    p=argparse.ArgumentParser();p.add_argument('proposal',type=Path);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('fresh output required')
    decl=json.loads((HERE/'residual-completion-inputs-v2.json').read_text(encoding='utf-8'));raw=(ROOT/decl['bounded_source']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('bounded source identity')
    old=json.loads(gzip.decompress(raw));prop_raw=args.proposal.read_bytes();prop=json.loads(prop_raw)
    if prop['source_sha256']!=SHA or prop['N']!=312 or len(prop['witnesses'])!=2:raise ValueError('proposal identity')
    ctx.prec=1536;pi=arb.pi();check=(qa(256)/(2*pi)).log()+qa(Q(1,8))-qa(Q(7,2));assert check<qa(Q(1,2))
    rows=[]
    for w in prop['witnesses']:
        parity=w['parity'];degrees=w['jacobi_degrees'];coefs=[Q(v,1<<40) for v in w['jacobi_coefficients_grid40']]
        if w.get('jacobi_parameter')!=4:raise ValueError('Jacobi source convention')
        if degrees!=list(range(parity,304,2)) or len(coefs)!=len(degrees):raise ValueError('complete constrained proposal shape')
        count=max((n for n,c in zip(degrees,coefs) if c),default=0)+1;jp=jacobi_polys(max(2,count),4);poly=fmpq_poly([0])
        for n,c in zip(degrees,coefs):
            if c:poly+=fq(c)*jp[n]
        poly*=fmpq_poly([1,0,-1])**4;degree=poly.degree()
        if not 0<=degree<312:raise ValueError('low polynomial degree')
        norm=integral(poly*poly)
        if norm<=0:raise ValueError('positive physical mass')
        lp=legendre_polys(max(2,degree+1));remainder=poly;leg=[Q(0) for n in range(degree+1)]
        for n in range(degree,-1,-1):
            c=remainder[n]/lp[n][n];leg[n]=qq(c);remainder-=c*lp[n]
        if remainder:raise ValueError('exact Legendre expansion')
        if norm!=sum(Q(2,2*n+1)*c*c for n,c in enumerate(leg)):raise ValueError('independent Legendre mass')
        value=arb(0)
        for i,ci in enumerate(leg):
            if not ci:continue
            for j in range(i,len(leg)):
                cj=leg[j]
                if not cj:continue
                lo,hi=map(lambda x:Q(x,1<<old['bits']),old['matrices']['A'][i][j-i]);entry=qa((lo+hi)/2)+arb(0,qa((hi-lo)/2))
                value+=(1 if i==j else 2)*qa(ci*cj)*entry
        derivative=poly;traces=[]
        for k in range(degree+1):
            left=qq(derivative(fmpq(-1)));right=qq(derivative(fmpq(1)))
            if k<4 and (left or right):raise ValueError('exact endpoint trace')
            traces.append(abs(left)+abs(right));derivative=derivative.derivative()
        d4=poly
        for k in range(4):d4=d4.derivative()
        dnorm=integral(d4*d4);sob=Q(dnorm,2*192**8)
        end=Q(0)
        for k in range(4,len(traces)):
            for l in range(4,len(traces)):
                s=k+l+1;end+=traces[k]*traces[l]*Q(1,192**s)*(Q(1,s*s)+Q(1,2*s))
        endpoint=qa(end)/pi;outside=min(ends(endpoint)[1],sob)
        upper=(value+qa(outside))/qa(norm);normalized=publish(upper);floor=Q(1,30000000000);failure=publish(upper-qa(floor))
        rows.append({'parity':parity,'actual_degree':degree,'jacobi_degrees':degrees,'jacobi_coefficients_grid40':[int(v) for v in w['jacobi_coefficients_grid40']],'exact_legendre_coefficients':[str(v) for v in leg],'exact_mass':str(norm),'bounded_source_quadratic':publish(value),'fourth_derivative_norm_squared':str(dnorm),'complete_sobolev_exterior_upper':str(sob),'complete_endpoint_exterior':publish(endpoint),'complete_exterior_used_upper':str(outside),'actual_Weil_rayleigh_enclosure_upper':normalized['upper'],'norm_completion_rayleigh_upper':failure['upper'],'strict_floor_rejection':Q(failure['upper'])<0})
    out={'format':'whole-space-residual-floor-assessment-v2','status':'COMPLETE_ACTUAL_LOW_AND_EXTERIOR_ENCLOSURE','N':312,'support':'3/4','old_source_sha256':SHA,'proposal_sha256':hashlib.sha256(prop_raw).hexdigest(),'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inputs_sha256':hashlib.sha256((HERE/'residual-completion-inputs-v2.json').read_bytes()).hexdigest(),'source_precision_bits':1536,'jacobi_parameter':4,'residual_allowance':'1/300000','isotropic_floor':'1/30000000000','exterior_log_scalar_check':publish(check),'witnesses':rows,'norm_completion_rejected_on_whole312':any(v['strict_floor_rejection'] for v in rows),'exact_supported_criterion_rejected':False,'actual_Weil_negative_claim':False,'new_support_or_admission':False}
    with args.output.open('x',encoding='utf-8') as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps([{'parity':v['parity'],'degree':v['actual_degree'],'rayleigh_upper':float(Q(v['actual_Weil_rayleigh_enclosure_upper'])),'completion_upper':float(Q(v['norm_completion_rayleigh_upper'])),'rejected':v['strict_floor_rejection']} for v in rows]))
if __name__=='__main__':
    try:main()
    except (ValueError,AssertionError,KeyError,ZeroDivisionError) as e:raise SystemExit(type(e).__name__+': '+str(e))
