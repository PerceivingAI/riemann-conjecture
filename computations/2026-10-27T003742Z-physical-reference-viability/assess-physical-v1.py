"""Complete physical dual bounds at a fixed reference. Research, not theorem admission."""
import argparse,hashlib,json,math,sys
from fractions import Fraction as Q
from pathlib import Path
from flint import arb,arb_poly,fmpq,ctx
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT))
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms
from physical_model_v1 import exact_residual_head,legendre_polynomials,primitive_walk

def f(x):return fmpq(x)
def q(x):
    if isinstance(x,Q):return x
    x=fmpq(x);return Q(int(x.numerator),int(x.denominator))
def text(x):x=q(x);return str(fmpq(x.numerator,x.denominator))
def aa(x):return arb(fmpq(x))
def pub(x):
    lo=q(x.lower().fmpq());hi=q(x.upper().fmpq());s=1<<192
    return {'lower':text(Q(math.floor(lo*s)-1,s)),'upper':text(Q(math.ceil(hi*s)+1,s))}
def upper(x):return q(pub(x)['upper'])
def norm(c):return sum((fmpq(2,2*n+1)*v*v for n,v in c.items()),fmpq(0))
def jump(c,H):return sum((fmpq(2,2*n+1)*H[n]*v*v for n,v in c.items()),fmpq(0))
def potential(c,H):
    out=fmpq(0);items=list(c.items())
    for i,(n,v) in enumerate(items):
        out+=v*v*fmpq(2,2*n+1)*(2*H[2*n]-2*H[n]+fmpq(1,2*n+1))
        for m,w in items[:i]:
            if (m-n)%2:continue
            out+=2*v*w*fmpq(2,abs(m-n)*(m+n+1))
    return out

def cross_potential(u,v):return sum((un*vm*fmpq(2,(m-n)*(m+n+1)) for n,un in u.items() for m,vm in v.items() if not (m-n)%2),fmpq(0))

def residual(c,kernel,head):
    K=len(kernel)-1;out=fmpq(0)
    for n,value in c.items():
        if n<=K:
            out+=value*sum((fmpq(2,2*m+1)*c.get(m,fmpq(0))*w for m,w in enumerate(head[n])),fmpq(0))
        else:
            for step,walk in primitive_walk(n,K):
                factor=2*math.factorial(step-1)*kernel[step-1]
                out+=value*factor*sum((fmpq(2,2*m+1)*c.get(m,fmpq(0))*w for m,w in walk.items()),fmpq(0))
    return out

def poly(c,basis):
    out=basis[0]*0
    for n,value in c.items():out+=basis[n]*value
    return out

def overlap(left,right,tau):
    half=1-tau/2;x=arb_poly([-tau/2,half]);y=arb_poly([tau/2,half]);prod=left(x)*right(y)
    return half*sum((prod[k]*arb(2)/(k+1) for k in range(0,len(prod),2)),arb(0))

def main():
    p=argparse.ArgumentParser();p.add_argument('proposal',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('fresh output required')
    declraw=(HERE/'assessment-inputs-v1.json').read_bytes();decl=json.loads(declraw);raw=a.proposal.read_bytes();proposal=json.loads(raw);rraw=(ROOT/decl['residual_packet']).read_bytes();r=json.loads(rraw)
    if hashlib.sha256(rraw).hexdigest()!=decl['residual_packet_sha256']:raise ValueError('accepted residual source identity')
    if proposal['format']!='whole-physical-dual-proposals-v2' or proposal['N']!=312 or proposal['auxiliary_extent']!=624:raise ValueError('declared whole-space proposal')
    if fmpq(decl['leakage_deficit_upper'])!=fmpq(3,10**49):raise ValueError('complete fixed leakage bound')
    ctx.prec=3072;T=fmpq(3,4);K=56;kernel=list(map(f,r['kernel_coefficients']));head=exact_residual_head(kernel);basis=legendre_polynomials(623);H=[fmpq(0)]
    for n in range(1,1247):H.append(H[-1]+fmpq(1,n))
    delta=f(r['complete_remainder_upper']);dr=upper(2*aa(T)*(2/arb.pi())*(2*aa(T)/arb.pi())**57/(1-2*aa(T)/arb.pi()));cT=arb.const_euler()+(arb(3)*arb.pi()/2).log();A0=-arb.const_euler()-arb.pi()/2-3*arb(2).log()-arb.pi().log();terms=enumerate_active_prime_power_terms(3,4,prec=3072)
    if [t.m for t in terms]!=[2,3,4]:raise ValueError('complete arithmetic active set')
    U=[[f(x) for x in row] for row in r['coefficient_map']];rows=[]
    for block in proposal['witnesses']:
        parity=block['parity'];selected=block['proposals'][0];u={n:fmpq(z,2**96) for n,z in zip(selected['low_modes'],selected['low_coefficients_grid96']) if z};v={n:fmpq(z,2**96) for n,z in zip(selected['tail_modes'],selected['tail_coefficients_grid96']) if z}
        if any(n>=312 or n%2!=parity for n in u) or any(not 312<=n<624 or n%2!=parity for n in v):raise ValueError('low/tail parity domain')
        nu=norm(u);nv=norm(v)
        if nu<=0 or nv<=0:raise ValueError('nonzero physical pair')
        ju=jump(u,H);jv=jump(v,H);vu=potential(u,H);vv=potential(v,H);ru=residual(u,kernel,head);rv=residual(v,kernel,head);vc=cross_potential(u,v)
        rc=sum((v.get(m,fmpq(0))*fmpq(2,2*m+1)*sum((U[m-312][n-256]*u.get(n,fmpq(0)) for n in range(256,312)),fmpq(0)) for m in range(312,368)),fmpq(0))
        up=poly(u,basis);vp=poly(v,basis);ua=arb_poly([aa(z) for z in up]);va=arb_poly([aa(z) for z in vp]);pu=arb(0);pc=arb(0);arithmetic=[]
        for term in terms:
            low=-2*term.coefficient*overlap(ua,ua,term.tau);cross=-2*term.coefficient*overlap(va,ua,term.tau);pu+=low;pc+=cross
            arithmetic.append({'m':term.m,'tau':pub(term.tau),'coefficient':pub(term.coefficient),'low':pub(low),'cross':pub(cross)})
        Vu=aa(vu)-aa(nu)*arb(2).log();Vv=aa(vv)-aa(nv)*arb(2).log();model=aa(ju+ru)+Vu+pu-cT*aa(nu);modelc=aa(vc+rc)+pc;gap=aa(delta)*(aa(nu)*aa(nv)).sqrt()
        intervals={'cT':pub(cT),'A0':pub(A0),'potential_low':pub(Vu),'potential_tail':pub(Vv),'arithmetic_low':pub(pu),'arithmetic_cross':pub(pc),'finite_low_model':pub(model),'actual_low':pub(model+arb(0,aa(delta*nu))),'arch_tail':pub(aa(jv+rv)+Vv-cT*aa(nv)+arb(0,aa(f(dr)*nv))),'model_cross':pub(modelc),'actual_cross':pub(modelc+arb(0,gap))}
        qh=Q(3,4)*q(intervals['arch_tail']['upper'])+(q(intervals['A0']['upper'])/4-Q(1129,1024)+Q(3,10**49))*q(nv);deficit=q(intervals['actual_low']['upper'])+qh-2*q(intervals['actual_cross']['lower'])
        if qh<q(nv)/3:raise ValueError('reference norm floor inconsistent')
        if q(intervals['actual_low']['upper'])<q(nu)/10**15:raise ValueError('actual low source inconsistent with known control')
        row={'parity':parity,'proposal_index':0,'low_coefficients':[text(u.get(n,fmpq(0))) for n in range(312)],'tail_modes':selected['tail_modes'],'tail_coefficients':[text(v.get(n,fmpq(0))) for n in selected['tail_modes']],'exact':{'low_mass':text(nu),'tail_mass':text(nv),'jump_low':text(ju),'jump_tail':text(jv),'residual_model_low':text(ru),'residual_model_tail':text(rv),'potential_low_rational':text(vu),'potential_tail_rational':text(vv),'potential_cross':text(vc),'residual_model_cross':text(rc)},'intervals':intervals,'arithmetic_terms':arithmetic,'delta_full_upper':text(delta),'delta_regular_upper':text(dr),'reference_h_upper':text(qh),'deficit_upper':text(deficit),'strict_negative':deficit<0}
        rows.append(row);print(json.dumps({'parity':parity,'actual_low_upper':float(q(intervals['actual_low']['upper'])),'h_upper':float(qh),'cross_lower':float(q(intervals['actual_cross']['lower'])),'physical_deficit_upper':float(deficit),'strict_negative':deficit<0}),flush=True)
    imports=[]
    for name,module in sorted(sys.modules.items()):
        if name.startswith('scripts') and getattr(module,'__file__',None):
            path=Path(module.__file__).resolve()
            if not path.is_relative_to(ROOT.resolve()):raise ValueError('project imports outside captured root')
            imports.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    obj={'format':'complete-physical-reference-assessment-v1','support':'3/4','N':312,'K':56,'precision_bits':3072,'inputs_sha256':hashlib.sha256(declraw).hexdigest(),'proposal_path':a.proposal.resolve().relative_to(ROOT.resolve()).as_posix(),'proposal_sha256':hashlib.sha256(raw).hexdigest(),'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((HERE/'physical_model_v1.py').read_bytes()).hexdigest(),'imported_project_modules':imports,'residual_packet_sha256':hashlib.sha256(rraw).hexdigest(),'witnesses':rows,'reference_rejection_proved':any(z['strict_negative'] for z in rows),'actual_Weil_negative_claim':False,'full_matrix_positive_claim':False,'status':'STRICT_FIXED_REFERENCE_REJECTION' if any(z['strict_negative'] for z in rows) else 'VALID_PHYSICAL_BOUNDS_NONREJECTING'}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as stream:json.dump(obj,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({'status':obj['status']}))
if __name__=='__main__':
    try:main()
    except (ValueError,ArithmeticError) as e:raise SystemExit(str(e))
