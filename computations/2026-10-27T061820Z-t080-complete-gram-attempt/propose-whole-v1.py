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

def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.prec=1024;iraw=args.inputs.read_bytes();inp=json.loads(iraw);sraw=args.source.read_bytes();s=json.loads(sraw)
    if s['inputs_sha256']!=hashlib.sha256(iraw).hexdigest():raise ValueError('source inputs mismatch')
    transforms=base_transforms(inp);eta=arb(fmpq(s['eta_lower']));lam=arb(fmpq(s['model_error_upper']))
    out={'format':'t080-whole-congruence-proposal-v1','source_sha256':hashlib.sha256(sraw).hexdigest(),'inputs_sha256':hashlib.sha256(iraw).hexdigest(),'proposer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'status':'NONPROOF_ONLY','production_admission':False,'blocks':{}}
    for parity,label in ((0,'even'),(1,'odd')):
        T=arb_mat([[arb(transforms[label][i,j]) for j in range(DIM)] for i in range(DIM)]);D=arb_mat(DIM,DIM)
        for i,n in enumerate(range(parity,N,2)):D[i,i]=arb(fmpq(2,2*n+1))
        A=T.transpose()*(matrix(args.source.parent,s['matrices'][f'A_model-{parity}'])-D*lam)*T
        H=T.transpose()*matrix(args.source.parent,s['matrices'][f'weighted_head-{parity}'])*T/eta
        E=T.transpose()*matrix(args.source.parent,s['matrices'][f'weighted_complete_tail-{parity}'])*T/eta
        af,hf,ef=map(floating,(A,H,E));a_min=float(np.linalg.eigvalsh((af+af.T)/2)[0]);relative=None
        if a_min>0:
            L=np.linalg.cholesky((af+af.T)/2);Linv=np.linalg.solve(L,np.eye(DIM));hw=Linv@hf@Linv.T;ew=Linv@ef@Linv.T
            def objective(logtheta):
                theta=math.exp(logtheta);g=(1+theta)*hw+(1+1/theta)*ew
                return float(np.linalg.eigvalsh((g+g.T)/2)[-1])
            opt=minimize_scalar(objective,bounds=(-20,20),method='bounded',options={'xatol':1e-10})
            if not opt.success or not math.isfinite(opt.fun):raise ValueError('Young parameter proposal failed')
            theta=fmpq(max(1,round(math.exp(opt.x)*(1<<40))),1<<40);relative=objective(math.log(float(theta)))
        else:theta=fmpq(1)
        S=A-H*arb(1+theta)-E*arb(1+1/theta);sf=floating(S);eigen,vectors=np.linalg.eigh((sf+sf.T)/2)
        W=vectors@np.diag(1/np.sqrt(eigen)) if eigen[0]>0 else vectors
        out['blocks'][label]={'parity':parity,'theta':str(theta),'old_full_transform_identity_padding':5,'actual_A_minus_model_minimum_midpoint':a_min,'maximum_relative_Gram_proposal':relative,'minimum_preconditioned_lower_midpoint':float(eigen[0]),'transform_kind':'positive_whitening' if eigen[0]>0 else 'signed_diagonalization','proposal_transform':[[str(fmpq(round(float(x)*(1<<40)),1<<40)) for x in row] for row in W]}
        print(label,'theta',float(theta),'relativeGram',relative,'S_midpoint_min',float(eigen[0]),flush=True)
    args.output.write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
if __name__=='__main__':main()
