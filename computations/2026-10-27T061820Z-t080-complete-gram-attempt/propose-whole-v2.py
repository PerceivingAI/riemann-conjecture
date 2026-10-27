"""Nonproof full target Young-parameter and exact congruence proposals."""
import os
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_key,'1')
import argparse,gzip,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar
from flint import arb,arb_mat,ctx,fmpq,fmpq_mat
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];DIM=161;N=322

def pinned(path,sha):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('byte binding '+str(path))
    return raw

def base_transforms(inputs):
    oldinputs=json.loads(pinned(ROOT/inputs['old_whole_inputs'],inputs['old_whole_inputs_sha256']))
    old=json.loads(gzip.decompress(pinned(ROOT/oldinputs['old_combined_arithmetic_proof'],oldinputs['old_combined_arithmetic_proof_sha256'])))
    proposal=json.loads(pinned(ROOT/inputs['old_coordinate_proposal'],inputs['old_coordinate_proposal_sha256']))
    result={}
    for label in ('even','odd'):
        T=fmpq_mat([[fmpq(x) for x in row] for row in old['blocks'][label]['transform']]);W=fmpq_mat([[fmpq(x) for x in row] for row in proposal['blocks'][label]['proposal_transform']]);oldU=T*W;U=fmpq_mat(DIM,DIM)
        for i in range(DIM):
            for j in range(DIM):U[i,j]=oldU[i,j] if i<156 and j<156 else fmpq(int(i==j))
        result[label]=U
    return result

def matrix(base,d):
    raw=pinned(base/d['path'],d['sha256'])
    if len(raw)!=d['size']:raise ValueError('matrix size')
    p=json.loads(gzip.decompress(raw))
    if p['dimension']!=DIM or p['bits']!=256 or len(p['upper_triangle'])!=DIM*(DIM+1)//2:raise ValueError('matrix shape')
    out=arb_mat(DIM,DIM);k=0
    for i in range(DIM):
        for j in range(i,DIM):
            lo,hi=[fmpq(x,1<<256) for x in p['upper_triangle'][k]];k+=1
            if lo>hi:raise ValueError('reversed endpoints')
            out[i,j]=out[j,i]=arb((lo+hi)/2,arb((hi-lo)/2))
    return out

def floating(x):return np.array([[float(x[i,j].mid()) for j in range(DIM)] for i in range(DIM)])

def cholesky(matrix):
    L=arb_mat(DIM,DIM);smallest=None
    for i in range(DIM):
        for j in range(i+1):
            value=matrix[i,j]-sum((L[i,k]*L[j,k] for k in range(j)),arb(0))
            if i==j:
                if not value>0:raise ValueError('fresh actual A Cholesky pivot not strictly positive at '+str(i))
                L[i,j]=value.sqrt();smallest=value.lower().fmpq() if smallest is None else min(smallest,value.lower().fmpq())
            else:L[i,j]=value/L[j,j]
    return L,smallest

def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.prec=1024;iraw=args.inputs.read_bytes();inp=json.loads(iraw);sraw=args.source.read_bytes();s=json.loads(sraw)
    if s['inputs_sha256']!=hashlib.sha256(iraw).hexdigest():raise ValueError('source inputs mismatch')
    transforms=base_transforms(inp);eta=arb(fmpq(s['eta_lower']));lam=arb(fmpq(s['model_error_upper']))
    out={'format':'t080-whole-congruence-proposal-v2','source_sha256':hashlib.sha256(sraw).hexdigest(),'inputs_sha256':hashlib.sha256(iraw).hexdigest(),'proposer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'status':'NONPROOF_ONLY','native_precision_bits':1024,'rational_transform_bits':80,'conditioning_change':'fresh actual A-LambdaD Cholesky BEFORE floating; old transforms remain coordinates only','production_admission':False,'blocks':{}}
    for parity,label in ((0,'even'),(1,'odd')):
        T=arb_mat([[arb(transforms[label][i,j]) for j in range(DIM)] for i in range(DIM)]);D=arb_mat(DIM,DIM)
        for i,n in enumerate(range(parity,N,2)):D[i,i]=arb(fmpq(2,2*n+1))
        A=T.transpose()*(matrix(args.source.parent,s['matrices'][f'A_model-{parity}'])-D*lam)*T
        H=T.transpose()*matrix(args.source.parent,s['matrices'][f'weighted_head-{parity}'])*T/eta
        E=T.transpose()*matrix(args.source.parent,s['matrices'][f'weighted_complete_tail-{parity}'])*T/eta
        L,smallest=cholesky(A);Linv=L.inv();aw=Linv*A*Linv.transpose();hw=Linv*H*Linv.transpose();ew=Linv*E*Linv.transpose()
        hf,ef=map(floating,(hw,ew))
        def objective(logtheta):
            theta=math.exp(logtheta);g=(1+theta)*hf+(1+1/theta)*ef
            return float(np.linalg.eigvalsh((g+g.T)/2)[-1])
        opt=minimize_scalar(objective,bounds=(-20,20),method='bounded',options={'xatol':1e-10})
        if not opt.success or not math.isfinite(opt.fun):raise ValueError('Young proposal optimization failed')
        theta=fmpq(max(1,round(math.exp(opt.x)*(1<<40))),1<<40)
        S=aw-hw*arb(1+theta)-ew*arb(1+1/theta);sf=floating(S);eigen,vectors=np.linalg.eigh((sf+sf.T)/2)
        V=vectors@np.diag(1/np.sqrt(eigen)) if eigen[0]>0 else vectors
        exactV=arb_mat([[arb(fmpq(*float(x).as_integer_ratio())) for x in row] for row in V]);W=Linv.transpose()*exactV;scale=1<<80
        exactW=[[str(fmpq(int((W[i,j].mid().fmpq()*scale+fmpq(1,2)).floor()),scale)) for j in range(DIM)] for i in range(DIM)]
        out['blocks'][label]={'parity':parity,'theta':str(theta),'old_full_transform_identity_padding':5,'native_A_cholesky_before_floating':True,'minimum_native_cholesky_pivot_lower':str(smallest),'maximum_relative_Gram_proposal':objective(math.log(float(theta))),'minimum_fresh_A_whitened_lower_midpoint':float(eigen[0]),'proposal_transform':exactW,'transform_kind':'fresh_A_then_positive_whitening' if eigen[0]>0 else 'fresh_A_then_signed_diagonalization'}
        print(label,'theta',float(theta),'relativeGram',out['blocks'][label]['maximum_relative_Gram_proposal'],'fresh_whitened_S_min',float(eigen[0]),flush=True)
    args.output.write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
if __name__=='__main__':main()
