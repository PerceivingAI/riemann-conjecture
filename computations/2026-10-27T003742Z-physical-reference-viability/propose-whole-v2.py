"""Nonproof exact-parameter/transform proposals from complete source intervals."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ.setdefault(k,'1')
import argparse,gzip,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar
from flint import arb,arb_mat,ctx,fmpq
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def matrix(descriptor):
    raw=(HERE/descriptor['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=descriptor['sha256']:raise ValueError('source matrix byte binding')
    q=json.loads(gzip.decompress(raw));out=arb_mat(156,156);k=0
    for i in range(156):
        for j in range(i,156):
            lo,hi=[fmpq(x,1<<q['bits']) for x in q['upper_triangle'][k]];k+=1
            out[i,j]=out[j,i]=arb((lo+hi)/2,arb((hi-lo)/2))
    return out

def floating(m):return np.array([[float(m[i,j].mid()) for j in range(156)] for i in range(156)])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.prec=1024;s=json.loads(args.source.read_text());decl=json.loads((HERE/'whole-gram-inputs-v2.json').read_text())
    raw=(ROOT/decl['old_combined_arithmetic_proof']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=decl['old_combined_arithmetic_proof_sha256']:raise ValueError('old transform pin')
    old=json.loads(gzip.decompress(raw));eta=arb(fmpq(s['eta_lower']));lam=arb(fmpq(s['model_error_upper']))
    out={'format':'whole-Gram-proposal-v2','source_sha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),'status':'NONPROOF_ONLY','blocks':{}}
    for parity,label in ((0,'even'),(1,'odd')):
        T=arb_mat([[arb(fmpq(x)) for x in row] for row in old['blocks'][label]['transform']])
        D=arb_mat(156,156)
        for i,n in enumerate(range(parity,312,2)):D[i,i]=arb(fmpq(2,2*n+1))
        A=T.transpose()*(matrix(s['matrices'][f'A_model-{parity}'])-D*lam)*T
        H=T.transpose()*matrix(s['matrices'][f'weighted_head-{parity}'])*T*(1/eta)
        E=T.transpose()*matrix(s['matrices'][f'weighted_complete_tail-{parity}'])*T*(1/eta)
        af,hf,ef=map(floating,(A,H,E));L=np.linalg.cholesky((af+af.T)/2);Linv=np.linalg.solve(L,np.eye(156))
        hw=Linv@hf@Linv.T;ew=Linv@ef@Linv.T
        def objective(logtheta):
            theta=math.exp(logtheta);g=(1+theta)*hw+(1+1/theta)*ew
            return float(np.linalg.eigvalsh((g+g.T)/2)[-1])
        opt=minimize_scalar(objective,bounds=(-20,20),method='bounded',options={'xatol':1e-10})
        numerator=max(1,round(math.exp(opt.x)*(1<<40)));theta=fmpq(numerator,1<<40)
        S=A-H*arb(1+theta)-E*arb(1+1/theta);sf=floating(S);eigen,vectors=np.linalg.eigh((sf+sf.T)/2)
        if eigen[0]>0:
            W=vectors@np.diag(1/np.sqrt(eigen));kind='positive_whitening'
        else:W=vectors;kind='signed_diagonalization'
        exactW=[[str(fmpq(round(float(x)*(1<<40)),1<<40)) for x in row] for row in W]
        out['blocks'][label]={'parity':parity,'theta':str(theta),'maximum_relative_Gram_proposal':objective(math.log(float(theta))),'minimum_preconditioned_lower_midpoint':float(eigen[0]),'proposal_transform':exactW,'transform_kind':kind}
        print(label,'theta',float(theta),'relative_Gram',out['blocks'][label]['maximum_relative_Gram_proposal'],'Smin',float(eigen[0]),flush=True)
    args.output.write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n')
if __name__=='__main__':main()
