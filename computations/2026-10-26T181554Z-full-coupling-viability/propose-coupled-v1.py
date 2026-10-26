"""Floating coupled witness proposals only; no positivity/theorem acceptance."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ.setdefault(key,'1')
import argparse,hashlib,json,math,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from scipy.special import roots_legendre
from flint import arb,ctx
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
if args.output.exists():raise SystemExit('fresh output required')
ctx.prec=256;terms=enumerate_active_prime_power_terms(3,4,prec=256)
assert [v.m for v in terms]==[2,3,4]
K=624;N=312;start=156;nodes,weights=roots_legendre(K);hn=np.r_[0.,np.cumsum(1/np.arange(1,2*K+1))]
cT=math.log(2*math.pi*.75)+float(arb.const_euler());A0=float(__import__('flint').acb(arb(1)/4).digamma().real-arb.pi().log())
shift=A0/4-1/4-873/1024;out=[]
for parity in (0,1):
    idx=np.arange(start+parity,K,2);scale=np.sqrt((2*idx+1)/2)
    ii=idx[:,None];jj=idx[None,:];gap=np.abs(ii-jj);den=gap*(ii+jj+1)
    V=np.sqrt((2*ii+1)*(2*jj+1))/np.where(gap==0,1,den)
    np.fill_diagonal(V,2*hn[2*idx]-2*hn[idx]+1/(2*idx+1)-math.log(2))
    P=np.zeros_like(V)
    for term in terms:
        tau=float(term.tau);coef=float(term.coefficient);half=(2-tau)/2;u=-tau/2+half*nodes
        lo=np.polynomial.legendre.legvander(u,K-1)[:,idx]*scale
        hi=np.polynomial.legendre.legvander(u+tau,K-1)[:,idx]*scale
        cross=lo.T@((half*weights)[:,None]*hi);P-=coef*(cross+cross.T)
    nlow=len(idx[idx<N]);base=V+np.diag(hn[idx]-cT);F=np.zeros_like(V)
    F[:nlow,:nlow]=(base+P)[:nlow,:nlow]+(1/75000+1/300000)*np.eye(nlow)
    F[:nlow,nlow:]=(V+P)[:nlow,nlow:];F[nlow:,:nlow]=F[:nlow,nlow:].T
    F[nlow:,nlow:]=.75*base[nlow:,nlow:]+(shift+.75*333/(1024*N*(N+1))+1/300000+1e-48)*np.eye(len(idx)-nlow)
    eigen,vec=np.linalg.eigh(F);v=vec[:,0];coeff=np.rint(v*scale*(1<<40)).astype(np.int64)
    out.append({'parity':parity,'indices':idx.tolist(),'low_count':nlow,'floating_minimum_NOT_PROOF':float(eigen[0]),'unnormalized_coefficients_grid40':[int(q) for q in coeff]})
result={'format':'floating-coupled-witness-proposals-v1','status':'NON_PROOF_PROPOSALS','N':N,'auxiliary_extent':K,'low_degree_floor':start,'witnesses':out,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inputs_sha256':hashlib.sha256((HERE/'assessment-inputs-v1.json').read_bytes()).hexdigest(),'canonical_prime_power_module_sha256':hashlib.sha256((ROOT/'scripts/cert/prime_power_terms.py').read_bytes()).hexdigest()}
args.output.parent.mkdir(parents=True,exist_ok=True)
with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps([{'parity':v['parity'],'minimum_NON_PROOF':v['floating_minimum_NOT_PROOF']} for v in out]))
