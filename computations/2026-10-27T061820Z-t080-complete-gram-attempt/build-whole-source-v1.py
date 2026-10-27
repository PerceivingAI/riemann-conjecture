"""Fresh complete signed T4/5 weighted-Gram source; research, not admission."""
import os
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_key,'1')
import argparse,gzip,hashlib,importlib.util,json,math,sys
from pathlib import Path
from flint import arb,arb_mat,arb_poly,ctx,fmpq
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from scripts.cert.mixed_gram_research import logarithmic_cell_moments
N=322;M=644;K=76;DIM=161;BITS=256;SCALE=1<<BITS;T=fmpq(4,5)

def pinned(path,sha):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('changed input '+str(path))
    return raw

def a(x):return arb(fmpq(x))
def sym(x):return (x+x.transpose())*a('1/2')
def diag(xs):
    out=arb_mat(len(xs),len(xs))
    for i,x in enumerate(xs):out[i,i]=x
    return out

def publish(x):
    if not x.is_finite():raise ValueError('nonfinite source enclosure')
    return [int((x.lower().fmpq()*SCALE).floor())-1,int((x.upper().fmpq()*SCALE).ceil())+1]

def legendre_values(x,count):
    vals=[arb(1),x]
    for n in range(1,count-1):vals.append(((2*n+1)*x*vals[-1]-n*vals[-2])/(n+1))
    return vals[:count]

def residual_matrices(coefficients,helper):
    head=helper.exact_residual_head(coefficients);out={}
    for n in range(N):
        if n<=K:row={m:x for m,x in enumerate(head[n]) if x}
        else:
            row={}
            for step,walk in helper.primitive_walk(n,K):
                factor=2*math.factorial(step-1)*coefficients[step-1]
                for m,x in walk.items():row[m]=row.get(m,fmpq(0))+factor*x
        out[n]=row
    for n,row in out.items():
        if max(row,default=-1)>=M:raise ValueError('nonzero residual beyond physical extent')
        for m,x in row.items():
            if m<N and x*fmpq(2,2*m+1)!=out[m].get(n,fmpq(0))*fmpq(2,2*n+1):raise ValueError('residual self-adjointness')
            if (m-n)%2 and x:raise ValueError('residual parity')
    return out

def bessel(c,count):
    out=[arb(0)]*(count+2)
    for n in (count,count+1):
        out[n]=c.bessel_j(a(fmpq(2*n+1,2)))*(arb.pi()/(2*c)).sqrt()
        if out[n].rel_accuracy_bits()<2048:raise ValueError('unresolved spherical Bessel seed')
    for n in range(count,0,-1):out[n-1]=(2*n+1)/c*out[n]-out[n+1]
    return out

def kernel_step(edges,weights,parity):
    ids=list(range(N+parity,M,2));mass=[a(fmpq(2,2*n+1)) for n in ids]
    result=diag([a(weights[-1])*x for x in mass])
    for k,omega in enumerate(edges[1:]):
        c=a(T*omega);js=bessel(c,M)
        deriv=[n/c*js[n]-js[n+1] for n in range(M)]
        ds=[(2*c).si()+((2*c).cos()-1)/(2*c)]
        for n in range(1,M):ds.append(ds[-1]-c*(js[n-1]**2+js[n]**2))
        F=arb_mat(DIM,DIM)
        for i,n in enumerate(ids):
            F[i,i]=4/(arb.pi()*(2*n+1))*ds[n]
            for j in range(i):
                m=ids[j]
                F[i,j]=F[j,i]=4/arb.pi()*((-1)**((m-n)//2))*c*c*(deriv[n]*js[m]-deriv[m]*js[n])/(n*(n+1)-m*(m+1))
        result+=F*a(weights[k]-weights[k+1])
    return sym(result)

def combined_square(terms,quadrature):
    # Global partition of every compressed-translation edge. Squaring the
    # COMPLETE signed vector retains all mixed powers and both shift signs.
    points=[arb(-1),arb(1)]
    for tau,coef in terms:points.extend([-1+tau,1-tau])
    points.sort(key=lambda x:float(x.mid()))
    if any(not points[i]<points[i+1] for i in range(len(points)-1)):raise ValueError('unresolved cell ordering')
    total={p:arb_mat(DIM,DIM) for p in (0,1)}
    for left,right in zip(points,points[1:]):
        mid=(left+right)/2;half=(right-left)/2;active=[]
        for tau,coef in terms:
            for sign in (-1,1):
                test=mid+sign*tau
                if arb(-1)<test<arb(1):active.append((sign*tau,coef))
                elif test<arb(-1) or test>arb(1):pass
                else:raise ValueError('unresolved translation membership')
        rows={0:[],1:[]};weighted={0:[],1:[]}
        for node,weight in quadrature:
            x=mid+half*node;values=[arb(0) for _ in range(N)]
            for shift,coef in active:
                shifted=legendre_values(x+shift,N)
                for i in range(N):values[i]-=coef*shifted[i]
            for parity in (0,1):
                row=values[parity::2];rows[parity].append(row);weighted[parity].append([half*weight*v for v in row])
        for parity in (0,1):total[parity]+=arb_mat(rows[parity]).transpose()*arb_mat(weighted[parity])
    print('fresh full combined P squared, all translation cells',len(points)-1,flush=True)
    return {p:sym(x) for p,x in total.items()}

def source(parity,polys,H,H2,rmap,terms,quadrature,P2,edges,weights,kappa):
    ids=list(range(parity,N,2));tail=list(range(N+parity,M,2))
    mass=[a(fmpq(2,2*n+1)) for n in ids];tmass=[a(fmpq(2,2*n+1)) for n in tail]
    def v(m,n):
        if m==n:return a(fmpq(2,2*n+1))*(2*a(H[2*n])-2*a(H[n])+a(fmpq(1,2*n+1))-arb.const_log2())
        return a(fmpq(2,abs(m-n)*(m+n+1)))
    V=arb_mat([[v(m,n) for n in ids] for m in ids]);VT=arb_mat([[v(m,n) for n in ids] for m in tail])
    R=arb_mat([[a(rmap[n].get(m,fmpq(0))*fmpq(2,2*m+1)) for n in ids] for m in ids])
    RT=arb_mat([[a(rmap[n].get(m,fmpq(0))*fmpq(2,2*m+1)) for n in ids] for m in tail])
    P=arb_mat(DIM,DIM);PT=arb_mat(DIM,DIM);VP=arb_mat(DIM,DIM)
    C=arb_mat([[a(polys[n][k]) for k in range(N)] for n in ids])
    for m,(tau,coef) in zip((2,3,4),terms):
        midpoint=-tau/2;half=1-tau/2;lowx=[];highx=[];lowy=[];weighted=[]
        for node,weight in quadrature:
            x=midpoint+half*node;px=legendre_values(x,M);py=legendre_values(x+tau,N)
            lowx.append([px[n] for n in ids]);highx.append([px[n] for n in tail])
            lowy.append([py[n] for n in ids]);weighted.append(-2*coef*half*weight)
        Y=arb_mat([[weighted[j]*x for x in row] for j,row in enumerate(lowy)])
        P+=arb_mat(lowx).transpose()*Y;PT+=arb_mat(highx).transpose()*Y
        moments=logarithmic_cell_moments(arb(-1),1-tau,2*N-2)
        moments_matrix=arb_mat([[moments[i+j] for j in range(N)] for i in range(N)])
        shift=arb_poly([tau,1]);shifted=[arb_poly([a(x) for x in polys[n].coeffs()])(shift) for n in ids]
        shifted_matrix=arb_mat([[p[k] for k in range(N)] for p in shifted])
        VP+=C*moments_matrix*shifted_matrix.transpose()*(-2*coef)
        print('fresh P low/tail and signed VP',parity,m,flush=True)
    P=sym(P)
    A=diag([mass[i]*(a(H[n])-arb.const_euler()-(2*arb.pi()*a(T)).log()) for i,n in enumerate(ids)])+V+P+R
    mono=arb_mat([[a(polys[n][2*k+parity]) for k in range(DIM)] for n in ids]);moments=[]
    for r in range(N):
        aa=2*arb.const_log2()-2*a(H[2*r+2])+a(H[r+1]);tri=-arb.pi()**2/3+4*a(H2[2*r+2])-a(H2[r+1])
        moments.append((aa*aa+tri)/(2*(2*r+1)))
    VV=mono*arb_mat([[moments[i+j+parity] for j in range(DIM)] for i in range(DIM)])*mono.transpose()
    inv=diag([1/x for x in mass]);tinv=diag([1/x for x in tmass])
    GP=P2-P*inv*P;GVtail=VV-V*inv*V-VT.transpose()*tinv*VT
    GPtail=GP-PT.transpose()*tinv*PT;VPtail=VP-V*inv*P-VT.transpose()*tinv*PT
    E=sym(GVtail+GPtail+VPtail+VPtail.transpose())
    Cphysical=tinv*(VT+PT+RT);Kh=kernel_step(edges,weights,parity)
    return {'A_model':sym(A),'weighted_head':sym(Cphysical.transpose()*Kh*Cphysical),'weighted_complete_tail':sym(E*a(kappa))}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    args.output=args.output.resolve()
    if args.output.exists():raise FileExistsError(args.output)
    inp_raw=args.inputs.read_bytes();inp=json.loads(inp_raw)
    decl_raw=pinned(ROOT/inp['target_declaration'],inp['target_declaration_sha256']);decl=json.loads(decl_raw)
    seal=json.loads(pinned(ROOT/inp['first_attempt_seal'],inp['first_attempt_seal_sha256']))
    if (decl['support'],decl['N'],decl['M'],decl['K'])!=('4/5',N,M,K):raise ValueError('not frozen target')
    if seal['target_declaration_sha256']!=hashlib.sha256(decl_raw).hexdigest():raise ValueError('first attempt declaration binding')
    if (inp['source_precision'],inp['bits'])!=(3072,BITS):raise ValueError('not declared numerical controls')
    ctx.prec=inp['source_precision']
    helper_path=ROOT/inp['source_helper'];pinned(helper_path,inp['source_helper_sha256'])
    spec=importlib.util.spec_from_file_location('t080_retained_residual',helper_path);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    coefficients=[fmpq(x) for x in decl['kernel_coefficients']]
    if len(coefficients)!=K+1 or coefficients[1]!=T*T/48:raise ValueError('residual coefficient contract')
    rmap=residual_matrices(coefficients,helper);polys=helper.legendre_polynomials(M-1)
    H=[fmpq(0)];H2=[fmpq(0)]
    for k in range(1,2*M+2):H.append(H[-1]+fmpq(1,k));H2.append(H2[-1]+fmpq(1,k*k))
    terms=[(arb(m).log()/a(T),arb(3 if m==3 else 2).log()/arb(m).sqrt()) for m in (2,3,4)]
    if not arb(4).log()<2*a(T)<arb(5).log() or not 2*a(T)<arb.pi():raise ValueError('active set/residual domain')
    quad=[arb.legendre_p_root(483,j,weight=True) for j in range(483)]
    square_quad=[arb.legendre_p_root(N,j,weight=True) for j in range(N)]
    P2=combined_square(terms,square_quad)
    edges=[fmpq(x) for x in decl['frequency_edges']];weights=[fmpq(x) for x in decl['inverse_weight_step_uppers']];kappa=fmpq(decl['weighted_physical_tail_inverse_upper'])
    if len(edges)!=len(weights) or edges[0]!=0 or weights[0]!=3 or any(weights[i]<weights[i+1] for i in range(len(weights)-1)):raise ValueError('frequency exterior majorant')
    out={'format':'t080-complete-signed-weighted-Gram-source-v1','support':'4/5','N':N,'order':K,'physical_extent':M,'bits':BITS,'precision':ctx.prec,'basis':'ordinary Legendre, physical masses 2/(2n+1)','inputs_sha256':hashlib.sha256(inp_raw).hexdigest(),'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'frequency_edges':[str(x) for x in edges],'inverse_weight_uppers':[str(x) for x in weights],'weighted_tail_norm_upper':str(kappa),'model_error_upper':decl['complete_model_error_upper'],'eta_lower':decl['eta'],'matrices':{},'status':'COMPLETE_INTERVAL_MATRICES_NOT_YET_POSITIVITY_VERIFIED','production_admission':False}
    folder=args.output.parent/'whole-matrices-v1';folder.mkdir(parents=True,exist_ok=False)
    for parity in (0,1):
        matrices=source(parity,polys,H,H2,rmap,terms,quad,P2[parity],edges,weights,kappa)
        for name,mat in matrices.items():
            payload={'kind':name,'parity':parity,'dimension':DIM,'bits':BITS,'upper_triangle':[publish(mat[i,j]) for i in range(DIM) for j in range(i,DIM)]}
            raw=gzip.compress((json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0);path=folder/f'{name}-{parity}.json.gz';path.write_bytes(raw)
            out['matrices'][f'{name}-{parity}']={'path':path.relative_to(args.output.parent).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)}
        print('complete full source parity',parity,flush=True)
    out['imported_project_sources']={str(Path(m.__file__).resolve().relative_to(ROOT)).replace('\\','/'):hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and str(Path(m.__file__).resolve()).startswith(str(ROOT/'scripts')) and Path(m.__file__).is_file()}
    out['retained_residual_helper_sha256']=inp['source_helper_sha256']
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':out['status'],'matrix_files':len(out['matrices']),'frequency_anchors':len(edges),'kappa':str(float(kappa))}),flush=True)
if __name__=='__main__':main()
