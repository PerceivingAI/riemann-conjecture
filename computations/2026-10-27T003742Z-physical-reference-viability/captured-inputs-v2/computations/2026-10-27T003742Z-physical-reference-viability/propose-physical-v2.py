"""NON_PROOF whole-low/tail search at fixed support and projection."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ.setdefault(k,'1')
import argparse,hashlib,json,math,sys
from pathlib import Path
import numpy as np
from scipy.special import roots_legendre
from flint import arb,fmpq,ctx
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT))
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms
from physical_model_v1 import exact_residual_head
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists():raise ValueError('fresh output required')
inputs=json.loads((HERE/'assessment-inputs-v1.json').read_text());raw=(ROOT/inputs['residual_packet']).read_bytes();assert hashlib.sha256(raw).hexdigest()==inputs['residual_packet_sha256'];packet=json.loads(raw)
K=56;N=312;M=624;ctx.prec=256;terms=enumerate_active_prime_power_terms(3,4,prec=256);assert [t.m for t in terms]==[2,3,4]
exactc=[fmpq(x) for x in packet['kernel_coefficients']];c=[float(x) for x in exactc];head=exact_residual_head(exactc)
nodes,weights=roots_legendre(M);hn=np.r_[0.,np.cumsum(1/np.arange(1,2*M+1))];cT=math.log(2*math.pi*.75)+float(arb.const_euler());A0=-float(arb.const_euler())-math.pi/2-3*math.log(2)-math.log(math.pi);shift=A0/4-1129/1024;rows=[]
for parity in (0,1):
    idx=np.arange(parity,M,2);lookup={int(n):j for j,n in enumerate(idx)};scale=np.sqrt((2*idx+1)/2);ii=idx[:,None];jj=idx[None,:];gap=np.abs(ii-jj)
    V=np.sqrt((2*ii+1)*(2*jj+1))/np.where(gap==0,1,gap*(ii+jj+1));np.fill_diagonal(V,2*hn[2*idx]-2*hn[idx]+1/(2*idx+1)-math.log(2));R=np.zeros_like(V);P=np.zeros_like(V)
    for col,n in enumerate(idx):
        if n<=K:
            for m,value in enumerate(head[n]):
                if m in lookup:R[lookup[m],col]=float(value)*math.sqrt((2*n+1)/(2*m+1))
        else:
            current={int(n):1.}
            for step in range(1,K+1):
                nxt={}
                for j,value in current.items():
                    value/=2*j+1;nxt[j+1]=nxt.get(j+1,0.)+value;nxt[j-1]=nxt.get(j-1,0.)-value
                current=nxt
                if step%2==0:
                    factor=2*math.factorial(step-1)*c[step-1]
                    for m,value in current.items():
                        if m in lookup:R[lookup[m],col]+=factor*value*math.sqrt((2*n+1)/(2*m+1))
    asym=float(np.max(np.abs(R-R.T)));R=(R+R.T)/2
    for term in terms:
        tau=float(term.tau);half=(2-tau)/2;x=-tau/2+half*nodes;y=x+tau
        lo=np.polynomial.legendre.legvander(x,M-1)[:,idx]*scale;hi=np.polynomial.legendre.legvander(y,M-1)[:,idx]*scale;cross=lo.T@((half*weights)[:,None]*hi);P-=float(term.coefficient)*(cross+cross.T)
    base=V+R+np.diag(hn[idx]-cT);nlow=N//2;F=np.empty_like(base);F[:nlow,:nlow]=(base+P)[:nlow,:nlow];F[:nlow,nlow:]=(V+R+P)[:nlow,nlow:];F[nlow:,:nlow]=F[:nlow,nlow:].T;F[nlow:,nlow:]=.75*base[nlow:,nlow:]+shift*np.eye(len(idx)-nlow)
    values,vectors=np.linalg.eigh(F);proposals=[]
    for j in range(4):
        eigvec=vectors[:,j];u=eigvec[:nlow]*scale[:nlow];v=-eigvec[nlow:]*scale[nlow:];proposals.append({'floating_block_eigenvalue_NOT_PROOF':float(values[j]),'low_modes':idx[:nlow].tolist(),'low_coefficients_grid96':[int(round(float(z)*2**96)) for z in u],'tail_modes':idx[nlow:].tolist(),'tail_coefficients_grid96':[int(round(float(z)*2**96)) for z in v]})
    rows.append({'parity':parity,'floating_residual_symmetry_error_NOT_PROOF':asym,'proposals':proposals})
out={'format':'whole-physical-dual-proposals-v2','status':'NON_PROOF_PROPOSALS','N':N,'auxiliary_extent':M,'support':'3/4','residual_order':K,'low_space':'ALL0..311','inputs_sha256':hashlib.sha256((HERE/'assessment-inputs-v1.json').read_bytes()).hexdigest(),'source_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'model_code_sha256':hashlib.sha256((HERE/'physical_model_v1.py').read_bytes()).hexdigest(),'witnesses':rows,'positive_finite_block_implies_whole_positivity':False}
a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open('x',encoding='utf-8') as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps([{'parity':r['parity'],'minima_NON_PROOF':[v['floating_block_eigenvalue_NOT_PROOF'] for v in r['proposals']],'residual_symmetry_error':r['floating_residual_symmetry_error_NOT_PROOF']} for r in rows]))
