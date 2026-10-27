"""Fixed-control full signed physical-tail enclosure; research, not admission.

All ordinary Legendre masses are explicit. The frequency exterior is paid by
Parseval; the infinite physical output is paid by its COMPLETE signed VP Gram.
Publication consists of interval matrices, never entrywise Loewner assertions.
"""
import os
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_key,'1')
import argparse,gzip,hashlib,json,math,sys,time
from pathlib import Path
from fractions import Fraction
from flint import arb,acb,arb_mat,arb_poly,ctx,fmpq
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from physical_model_v1 import legendre_polynomials,exact_residual_head,primitive_walk
from scripts.cert.mixed_gram_research import logarithmic_cell_moments

BITS=192
SCALE=1<<BITS

def f(value):
    if isinstance(value,Fraction):return fmpq(value.numerator,value.denominator)
    return fmpq(value)
def a(value):return arb(f(value))
def publish(value):
    lo,hi=value.lower().fmpq(),value.upper().fmpq()
    return [int((lo*SCALE).floor())-1,int((hi*SCALE).ceil())+1]
def upper(value):return fmpq(publish(value)[1],SCALE)
def ball(pair,bits):
    lo,hi=[fmpq(x,1<<bits) for x in pair]
    return arb((lo+hi)/2,arb((hi-lo)/2))
def transpose(m):return m.transpose()
def sym(m):return (m+transpose(m))*a('1/2')
def old_matrix(proof,name,parity):
    rows=proof['matrices'][name];ids=list(range(parity,312,2))
    return arb_mat([[ball(rows[min(i,j)][abs(i-j)],proof['bits']) for j in ids] for i in ids])
def diag(values):
    n=len(values);out=arb_mat(n,n)
    for i,x in enumerate(values):out[i,i]=x
    return out

def bessel(c,count):
    out=[arb(0)]*(count+2)
    for n in (count,count+1):
        df=math.factorial(2*n+1)//(2**n*math.factorial(n))
        hyper=acb(-c*c/4).hypgeom_0f1(acb(fmpq(2*n+3,2)))
        if not hyper.imag.contains(0):raise ValueError('nonreal spherical Bessel seed')
        out[n]=c**n/df*hyper.real
    for n in range(count,0,-1):out[n-1]=(2*n+1)/c*out[n]-out[n+1]
    return out

def kernel_step(edges,weights,parity):
    ids=list(range(312+parity,624,2));d=[a(fmpq(2,2*n+1)) for n in ids]
    result=diag([a(weights[-1])*x for x in d])
    for k,omega in enumerate(edges[1:]):
        c=a(fmpq(3,4)*omega);js=bessel(c,624)
        deriv=[n/c*js[n]-js[n+1] for n in range(624)]
        ds=[(2*c).si()+((2*c).cos()-1)/(2*c)]
        for n in range(1,624):ds.append(ds[-1]-c*(js[n-1]**2+js[n]**2))
        F=arb_mat(156,156)
        for i,n in enumerate(ids):
            F[i,i]=4/(arb.pi()*(2*n+1))*ds[n]
            for j in range(i):
                m=ids[j]
                value=4/arb.pi()*((-1)**((m-n)//2))*c*c*(deriv[n]*js[m]-deriv[m]*js[n])/(n*(n+1)-m*(m+1))
                F[i,j]=F[j,i]=value
        result+=F*a(weights[k]-weights[k+1])
    return sym(result)

def residual_matrices(coefficients):
    head=exact_residual_head(coefficients);out={}
    for n in range(312):
        row={}
        if n<=56:row={m:x for m,x in enumerate(head[n]) if x}
        else:
            for step,walk in primitive_walk(n,56):
                factor=2*math.factorial(step-1)*coefficients[step-1]
                for m,x in walk.items():row[m]=row.get(m,fmpq(0))+factor*x
        out[n]=row
    for n,row in out.items():
        if max(row,default=-1)>=624:raise ValueError('R56 physical exterior not zero')
        for m,x in row.items():
            if m<312 and x*fmpq(2,2*m+1)!=out[m].get(n,fmpq(0))*fmpq(2,2*n+1):
                raise ValueError('exact residual self-adjointness failed')
    return out

def source(parity,polys,H,H2,rmap,old,edges,weights,kappa):
    ids=list(range(parity,312,2));tail=list(range(312+parity,624,2))
    mass=[a(fmpq(2,2*n+1)) for n in ids];tmass=[a(fmpq(2,2*n+1)) for n in tail]
    def v(m,n):
        if m==n:return a(fmpq(2,2*n+1))*(2*a(H[2*n])-2*a(H[n])+a(fmpq(1,2*n+1))-arb.const_log2())
        return a(fmpq(2,abs(m-n)*(m+n+1)))
    V=arb_mat([[v(m,n) for n in ids] for m in ids]);VT=arb_mat([[v(m,n) for n in ids] for m in tail])
    R=arb_mat([[a(rmap[n].get(m,fmpq(0))*fmpq(2,2*m+1)) for n in ids] for m in ids])
    RT=arb_mat([[a(rmap[n].get(m,fmpq(0))*fmpq(2,2*m+1)) for n in ids] for m in tail])
    P=old_matrix(old,'P',parity);GP=old_matrix(old,'GP',parity)
    cT=arb.const_euler()+(2*arb.pi()*a('3/4')).log()
    A=diag([mass[i]*(a(H[n])-cT) for i,n in enumerate(ids)])+V+P+R
    print('actual A model complete',parity,flush=True)
    Ptail=arb_mat(156,156);VP=arb_mat(156,156)
    C=arb_mat([[a(polys[n][k]) for k in range(312)] for n in ids])
    for m in (2,3,4):
        tau=arb(m).log()/a('3/4');coef=arb(3 if m==3 else 2).log()/arb(m).sqrt()
        midpoint=-tau/2;half=1-tau/2
        low_rows=[];tail_rows=[];quad_weights=[]
        for j in range(468):
            node,weight=arb.legendre_p_root(468,j,weight=True)
            x=midpoint+half*node;y=x+tau
            def values(z):
                q=[arb(1),z]
                for n in range(1,623):q.append(((2*n+1)*z*q[-1]-n*q[-2])/(n+1))
                return q
            px=values(x);py=values(y)
            tail_rows.append([px[n] for n in tail]);low_rows.append([py[n] for n in ids]);quad_weights.append(-2*coef*half*weight)
        Ptail+=transpose(arb_mat(tail_rows))*arb_mat([[quad_weights[j]*x for x in row] for j,row in enumerate(low_rows)])
        moments=logarithmic_cell_moments(arb(-1),1-tau,622)
        M=arb_mat([[moments[i+j] for j in range(312)] for i in range(312)])
        shift=arb_poly([tau,1]);shifted=[arb_poly([a(x) for x in polys[n].coeffs()])(shift) for n in ids]
        S=arb_mat([[p[k] for k in range(312)] for p in shifted])
        VP+=C*M*transpose(S)*(-2*coef)
        print('complete signed arithmetic and VP',parity,m,flush=True)
    monomial=arb_mat([[a(polys[n][2*k+parity]) for k in range(156)] for n in ids])
    moments=[]
    for r in range(312):
        aa=2*arb.const_log2()-2*a(H[2*r+2])+a(H[r+1])
        tri=-arb.pi()**2/3+4*a(H2[2*r+2])-a(H2[r+1])
        moments.append((aa*aa+tri)/(2*(2*r+1)))
    VV=monomial*arb_mat([[moments[i+j+parity] for j in range(156)] for i in range(156)])*transpose(monomial)
    inv=diag([1/x for x in mass]);tinv=diag([1/x for x in tmass])
    GVtail=VV-V*inv*V-transpose(VT)*tinv*VT
    GPtail=GP-transpose(Ptail)*tinv*Ptail
    VPt=VP-V*inv*P-transpose(VT)*tinv*Ptail
    E=sym(GVtail+GPtail+VPt+transpose(VPt))
    print('complete signed infinite-output Gram assembled',parity,flush=True)
    Cphysical=tinv*(VT+Ptail+RT)
    Kh=kernel_step(edges,weights,parity)
    Head=sym(transpose(Cphysical)*Kh*Cphysical)
    Tail=sym(E*a(kappa))
    return {'A_model':sym(A),'weighted_head':Head,'weighted_complete_tail':Tail}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();args.output=args.output.resolve()
    if args.output.exists():raise FileExistsError(args.output)
    decl_path=HERE/'whole-gram-inputs-v1.json';decl=json.loads(decl_path.read_text())
    ctx.prec=decl['source_precision_bits']
    def pinned(path,sha):
        raw=(ROOT/path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('changed retained source '+path)
        return raw
    old=json.loads(gzip.decompress(pinned(decl['old_combined_arithmetic_proof'],decl['old_combined_arithmetic_proof_sha256'])))
    rsource=json.loads(pinned(decl['residual_packet'],decl['residual_packet_sha256']))
    coefficients=[f(x) for x in rsource['kernel_coefficients']]
    rmap=residual_matrices(coefficients);polys=legendre_polynomials(623)
    H=[fmpq(0)];H2=[fmpq(0)]
    for k in range(1,626):H.append(H[-1]+fmpq(1,k));H2.append(H2[-1]+fmpq(1,k*k))
    A0=-arb.const_euler()-arb.pi()/2-3*arb.const_log2()-arb.pi().log()
    def g(t):return a('3/4')*((acb(a('1/4'),a(t)/2)).digamma().real-arb.pi().log())+A0/4-a('1129/1024')
    edges=[fmpq(0),fmpq(256)]
    while edges[-1]*fmpq(17,16)<8192:edges.append(edges[-1]*fmpq(17,16))
    edges.append(fmpq(8192))
    weights=[fmpq(3)]
    for x in edges[1:]:
        gx=g(x)
        if not gx>a('1/3'):raise ValueError('unqualified inverse weight anchor')
        weights.append(upper(1/gx))
    if any(weights[k]<weights[k+1] for k in range(len(weights)-1)):raise ValueError('nonmonotone step majorant')
    c=fmpq(384);M=624;ratio=c*c/((2*M+1)*(2*M+3))
    if not ratio<1:raise ValueError('leakage geometric ratio')
    df=math.factorial(2*M+1)//(2**M*math.factorial(M))
    leak=upper(2*a(c)/arb.pi()*a((2*M+1)*c**(2*M)/df**2/(1-ratio)))
    if not 0<=leak<=1:raise ValueError('unqualified inverse-weight tail leakage')
    inverse=upper(1/g(512))
    if not 0<inverse<=3:raise ValueError('unqualified tail inverse anchor')
    kappa=inverse+(3-inverse)*leak
    out={'format':'complete-signed-weighted-Gram-source-v3','support':'3/4','N':312,'physical_extent':624,'order':56,'bits':BITS,'precision':ctx.prec,'basis':'ordinary Legendre, physical masses 2/(2n+1)','inputs_sha256':hashlib.sha256(decl_path.read_bytes()).hexdigest(),'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'frequency_edges':[str(x) for x in edges],'inverse_weight_uppers':[str(x) for x in weights],'physical_tail_leakage_upper':str(leak),'tail_inverse_anchor_upper':str(inverse),'weighted_tail_norm_upper':str(kappa),'model_error_upper':decl['model_error_upper'],'eta_lower':decl['reference_eta_lower'],'matrices':{},'status':'COMPLETE_INTERVAL_MATRICES_NOT_YET_POSITIVITY_VERIFIED','production_admission':False}
    folder=args.output.parent/'whole-matrices-v3';folder.mkdir(exist_ok=False)
    for parity in (0,1):
        matrices=source(parity,polys,H,H2,rmap,old,edges,weights,kappa)
        for name,mat in matrices.items():
            payload={'kind':name,'parity':parity,'dimension':156,'bits':BITS,'upper_triangle':[publish(mat[i,j]) for i in range(156) for j in range(i,156)]}
            raw=gzip.compress((json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
            path=folder/f'{name}-{parity}.json.gz';path.write_bytes(raw)
            out['matrices'][f'{name}-{parity}']={'path':path.relative_to(HERE).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)}
    out['imported_project_sources']={str(Path(m.__file__).resolve().relative_to(ROOT)).replace('\\','/'):hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and str(Path(m.__file__).resolve()).startswith(str(ROOT/'scripts')) and Path(m.__file__).is_file()}
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'matrix_files':len(out['matrices']),'frequency_anchors':len(edges),'kappa':str(float(kappa))}),flush=True)
if __name__=='__main__':main()
