"""Non-proof proposals on the whole endpoint-constrained retained low space."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ.setdefault(key,'1')
import argparse,gzip,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.special import roots_legendre,eval_jacobi,gammaln
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
if args.output.exists():raise SystemExit('fresh output required')
inputs=json.loads((HERE/'residual-completion-inputs-v1.json').read_text(encoding='utf-8'));raw=(ROOT/inputs['bounded_source']).read_bytes()
if hashlib.sha256(raw).hexdigest()!=inputs['bounded_source_sha256']:raise SystemExit('old source identity')
old=json.loads(gzip.decompress(raw));N=312;J=304
A=np.zeros((N,N));scale=np.sqrt((2*np.arange(N)+1)/2)
for i,row in enumerate(old['matrices']['A']):
    for offset,pair in enumerate(row):
        j=i+offset;value=(pair[0]+pair[1])/(2**(old['bits']+1));A[i,j]=A[j,i]=value*scale[i]*scale[j]
x,w=roots_legendre(312);leg=np.polynomial.legendre.legvander(x,N-1)*scale
j=np.arange(J);logmass=17*math.log(2)-np.log(2*j+17)+2*gammaln(j+9)-gammaln(j+1)-gammaln(j+17);norm=np.exp(logmass/2)
jac=np.column_stack([eval_jacobi(k,8,8,x) for k in range(J)])*(1-x*x)[:,None]**4/norm
C=leg.T@(w[:,None]*jac);trans=C.T@A@C;out=[]
for parity in (0,1):
    idx=np.arange(parity,J,2);eig,vec=np.linalg.eigh(trans[np.ix_(idx,idx)]);v=vec[:,0];coeff=np.rint(v/norm[idx]*(1<<40)).astype(np.int64)
    out.append({'parity':parity,'jacobi_degrees':idx.tolist(),'jacobi_coefficients_grid40':[int(c) for c in coeff],'floating_minimum_NOT_PROOF':float(eig[0])})
result={'format':'floating-endpoint-constrained-low-proposals-v1','status':'NON_PROOF_PROPOSALS','source_sha256':hashlib.sha256(raw).hexdigest(),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inputs_sha256':hashlib.sha256((HERE/'residual-completion-inputs-v1.json').read_bytes()).hexdigest(),'N':N,'endpoint_zero_order':4,'witnesses':out}
with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps([{'parity':r['parity'],'minimum_NON_PROOF':r['floating_minimum_NOT_PROOF'],'nonzero_quantized_coefficients':sum(c!=0 for c in r['jacobi_coefficients_grid40'])} for r in out]))
