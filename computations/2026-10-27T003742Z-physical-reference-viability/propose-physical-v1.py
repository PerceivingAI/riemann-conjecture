"""NON_PROOF physical-tail proposals for a complete fixed-reference rejection test."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ.setdefault(k,'1')
import argparse,hashlib,json,math,sys
from pathlib import Path
import numpy as np
from scipy.special import roots_legendre
from flint import arb,fmpq,ctx
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT))
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists():raise ValueError('fresh output required')
inputs=json.loads((HERE/'assessment-inputs-v1.json').read_text());critical_raw=(ROOT/inputs['critical_packet']).read_bytes();residual_raw=(ROOT/inputs['residual_packet']).read_bytes()
assert hashlib.sha256(critical_raw).hexdigest()==inputs['critical_packet_sha256'] and hashlib.sha256(residual_raw).hexdigest()==inputs['residual_packet_sha256']
critical=json.loads(critical_raw);residual=json.loads(residual_raw);N=312;M=624;K=56;T=.75
ctx.prec=256;terms=enumerate_active_prime_power_terms(3,4,prec=256);assert [t.m for t in terms]==[2,3,4]
c=np.array([float(fmpq(x)) for x in residual['kernel_coefficients']]);U=np.array([[float(fmpq(x)) for x in row] for row in residual['coefficient_map']]);hnum=np.r_[0.,np.cumsum(1/np.arange(1,2*M+1))]
cT=math.log(2*math.pi*T)+float(arb.const_euler());A0=-float(arb.const_euler())-math.pi/2-3*math.log(2)-math.log(math.pi);shift=A0/4-1129/1024
nodes,weights=roots_legendre(M);rows=[]
for witness in critical['witnesses']:
    parity=witness['parity'];tail=np.arange(N+parity,M,2);low=np.arange(parity,N,2);mass=float(fmpq(witness['exact_mass']));u=np.zeros(N);u[:len(witness['exact_legendre_coefficients'])]=[float(fmpq(z)) for z in witness['exact_legendre_coefficients']];un=u/np.sqrt(mass)
    dm=2/(2*tail+1);dn=2/(2*low+1);ii=tail[:,None];jj=tail[None,:];gap=np.abs(ii-jj)
    V=np.sqrt((2*ii+1)*(2*jj+1))/np.where(gap==0,1,gap*(ii+jj+1));np.fill_diagonal(V,2*hnum[2*tail]-2*hnum[tail]+1/(2*tail+1)-math.log(2))
    R=np.zeros_like(V);lookup={n:i for i,n in enumerate(tail)}
    for j,n in enumerate(tail):
        current={int(n):1.}
        for step in range(1,K+1):
            nxt={}
            for ell,value in current.items():
                value/=2*ell+1;nxt[ell+1]=nxt.get(ell+1,0.)+value;nxt[ell-1]=nxt.get(ell-1,0.)-value
            current=nxt
            if step%2==0:
                factor=2*math.factorial(step-1)*c[step-1]
                for ell,value in current.items():
                    if ell in lookup:R[lookup[ell],j]+=factor*value*math.sqrt((2*n+1)/(2*ell+1))
    asym=float(np.max(np.abs(R-R.T)));R=(R+R.T)/2
    H=.75*(V+R+np.diag(hnum[tail]-cT))+shift*np.eye(len(tail))
    vinner=2/((tail[:,None]-low[None,:])*(tail[:,None]+low[None,:]+1));bV=(vinner@un[low])/np.sqrt(dm);bP=np.zeros(len(tail))
    for term in terms:
        tau=float(term.tau);half=(2-tau)/2;x=-tau/2+half*nodes;y=x+tau
        fminus=np.polynomial.legendre.legval(x,un);fplus=np.polynomial.legendre.legval(y,un)
        Lminus=np.polynomial.legendre.legvander(x,M-1)[:,tail]/np.sqrt(dm);Lplus=np.polynomial.legendre.legvander(y,M-1)[:,tail]/np.sqrt(dm)
        bP-=float(term.coefficient)*(Lminus.T@(half*weights*fplus)+Lplus.T@(half*weights*fminus))
    rcoef=U@un[N-K:N];bR=np.zeros_like(bV)
    for i,m in enumerate(range(N,N+K)):
        if m in lookup:bR[lookup[m]]=rcoef[i]*math.sqrt(2/(2*m+1))
    b=bV+bP+bR;sol=np.linalg.solve(H,b);ordinary=sol/np.sqrt(dm)*np.sqrt(mass);qgrid=[int(round(float(z)*2**96)) for z in ordinary];actual_q_upper=float(fmpq(witness['actual_Weil_rayleigh_enclosure_upper']))
    row={'parity':parity,'low_witness_index':len(rows),'tail_modes':tail.tolist(),'tail_coefficients_grid96':qgrid,'floating_h_block_minimum_NOT_PROOF':float(np.linalg.eigvalsh(H)[0]),'floating_V_pair_norm_NOT_PROOF':float(np.linalg.norm(bV)),'floating_P_pair_norm_NOT_PROOF':float(np.linalg.norm(bP)),'floating_R_pair_norm_NOT_PROOF':float(np.linalg.norm(bR)),'floating_dual_lower_NOT_PROOF':float(b@sol),'accepted_actual_low_Rayleigh_upper':witness['actual_Weil_rayleigh_enclosure_upper'],'floating_reference_deficit_NOT_PROOF':float(actual_q_upper-b@sol),'floating_residual_symmetry_error_NOT_PROOF':asym}
    rows.append(row)
result={'format':'floating-physical-dual-proposals-v1','status':'NON_PROOF_PROPOSALS','N':N,'auxiliary_extent':M,'support':'3/4','source_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inputs_sha256':hashlib.sha256((HERE/'assessment-inputs-v1.json').read_bytes()).hexdigest(),'witnesses':rows,'positive_restriction_implies_whole_positivity':False}
a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps([{k:v for k,v in row.items() if k not in ['tail_modes','tail_coefficients_grid96']} for row in rows]))
