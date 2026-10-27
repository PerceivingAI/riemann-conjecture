"""Measure exact whole-control budget caps for a separately qualified target.

No target low/coupling source or positivity is evaluated. Numerical eigensystems
only propose exact congruences; every reported cap pays all interval radii.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ.setdefault(key,'1')
import argparse,gzip,hashlib,json,math,sys
from pathlib import Path
import numpy as np
from flint import arb,arb_mat,ctx,fmpq,fmpq_mat
ROOT=Path(__file__).resolve().parents[1];DIM=156

def sha(raw):return hashlib.sha256(raw).hexdigest()
def q(x):return fmpq(x)
def zero():return fmpq_mat(DIM,DIM)
def bounds(folder,desc):
    raw=(folder/desc['path']).read_bytes()
    if sha(raw)!=desc['sha256'] or len(raw)!=desc['size']:raise ValueError('control matrix binding')
    data=json.loads(gzip.decompress(raw));lo=zero();hi=zero();k=0
    for i in range(DIM):
        for j in range(i,DIM):
            l,u=[fmpq(v,1<<data['bits']) for v in data['upper_triangle'][k]];k+=1
            if l>u:raise ValueError('invalid control interval')
            lo[i,j]=lo[j,i]=l;hi[i,j]=hi[j,i]=u
    return lo,hi

def midrad(pair):return (pair[0]+pair[1])*fmpq(1,2),(pair[1]-pair[0])*fmpq(1,2)
def absolute(U):return fmpq_mat([[abs(U[i,j]) for j in range(DIM)] for i in range(DIM)])
def congruence(pair,U):
    C,R=midrad(pair);V=absolute(U)
    return U.transpose()*C*U,V.transpose()*R*V

def gersh(C,R):
    lower=[];upper=[];radii=[]
    for i in range(DIM):
        off=sum((abs(C[i,j]) for j in range(DIM) if i!=j),fmpq(0));err=sum((R[i,j] for j in range(DIM)),fmpq(0))
        lower.append(C[i,i]-off-err);upper.append(C[i,i]+off+err);radii.append(err)
    return min(lower),max(upper),max(radii)

def arball_matrix(pair):
    C,R=midrad(pair)
    return arb_mat([[arb(C[i,j],arb(R[i,j])) for j in range(DIM)] for i in range(DIM)])
def float_matrix(M):return np.array([[float(M[i,j].mid()) for j in range(DIM)] for i in range(DIM)])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    inputs_raw=args.inputs.read_bytes();decl=json.loads(inputs_raw);folder=ROOT/decl['control_directory'];mraw=(folder/'manifest.json').read_bytes()
    if sha(mraw)!=decl['control_manifest_sha256']:raise ValueError('accepted control seal')
    accepted=json.loads(mraw);members={v['path']:v for v in accepted['members']}
    def retained(name):
        raw=(folder/name).read_bytes()
        if sha(raw)!=members[name]['sha256']:raise ValueError('changed control '+name)
        return raw
    source_raw=retained(decl['control_source']);source=json.loads(source_raw)
    proposal=json.loads(retained(decl['control_proposal']));proof=json.loads(retained(decl['control_exact_proof']))
    if proof['source_sha256']!=sha(source_raw) or proof['status']!='PASS_COMPLETE_SUPPORTED_GRAM_CRITERION':raise ValueError('accepted exact control result')
    old_raw=(ROOT/decl['old_transform_proof']).read_bytes()
    if sha(old_raw)!=decl['old_transform_sha256']:raise ValueError('old coordinate proof binding')
    old=json.loads(gzip.decompress(old_raw));ctx.prec=decl['proposal_precision_bits'];eta=q(source['eta_lower']);lam=q(source['model_error_upper'])
    out={'format':'t080-control-budget-v1','inputs_sha256':sha(inputs_raw),'producer_sha256':sha(Path(__file__).read_bytes()),'control_source_sha256':sha(source_raw),'control_manifest_sha256':sha(mraw),'support':'3/4','N':312,'target_matrices_computed':False,'caps_are_whole_space_not_directional_samples':True,'parities':{}}
    witness_dir=args.output.parent/'control-cap-witnesses-v1';witness_dir.mkdir(exist_ok=False)
    for parity,label in ((0,'even'),(1,'odd')):
        A=bounds(folder,source['matrices'][f'A_model-{parity}']);H=bounds(folder,source['matrices'][f'weighted_head-{parity}']);E=bounds(folder,source['matrices'][f'weighted_complete_tail-{parity}'])
        theta=q(proposal['blocks'][label]['theta']);hscale=(1+theta)/eta;escale=(1+1/theta)/eta
        H=tuple(M*hscale for M in H);E=tuple(M*escale for M in E);D=zero()
        for i,n in enumerate(range(parity,312,2)):D[i,i]=fmpq(2,2*n+1)
        loss=D*lam;Loss=(loss,loss);Total=(H[0]+E[0]+loss,H[1]+E[1]+loss)
        T=fmpq_mat([[q(x) for x in row] for row in old['blocks'][label]['transform']]);W=fmpq_mat([[q(x) for x in row] for row in proposal['blocks'][label]['proposal_transform']]);U=T*W
        mass_trace=sum((D[i,i]*U[i,j]**2 for i in range(DIM) for j in range(DIM)),fmpq(0));invU=U.inv()
        inverse_mass_trace=sum((invU[i,j]**2/D[j,j] for i in range(DIM) for j in range(DIM)),fmpq(0))
        old_margin=q(proof['blocks'][label]['minimum_complete_congruence_margin']);physical=old_margin/mass_trace
        S=(A[0]-Total[1],A[1]-Total[0]);sc,sr=congruence(S,U);sl,su,numerical=gersh(sc,sr)
        if sl!=old_margin:raise ValueError('original exact row margin mismatch')
        row={'control_selected_S_physical_mass_lower':str(physical),'accepted_S_margin':str(old_margin),'physical_coordinate_frobenius_squared':str(mass_trace),'inverse_physical_coordinate_frobenius_squared':str(inverse_mass_trace),'physical_coordinate_condition_squared_upper':str(mass_trace*inverse_mass_trace),'selected_S_physical_condition_upper':str((su/sl)*mass_trace*inverse_mass_trace),'all_source_interval_radius_over_accepted_margin':str(numerical/old_margin),'relative_caps':{}}
        Ta=arb_mat([[arb(T[i,j]) for j in range(DIM)] for i in range(DIM)]);Af=Ta.transpose()*arball_matrix(A)*Ta;af=float_matrix(Af);L=np.linalg.cholesky((af+af.T)/2);V=np.linalg.solve(L.T,np.eye(DIM))
        for kind,component in [('finite_head',H),('complete_physical_tail',E),('canonical_residual_model_error',Loss),('combined_paid',Total)]:
            CF=Ta.transpose()*arball_matrix(component)*Ta;cf=V.T@float_matrix(CF)@V;values,vectors=np.linalg.eigh((cf+cf.T)/2);coordinates=V@vectors
            transform=[[str(fmpq(round(float(v)*(1<<decl['transform_grid_bits'])),1<<decl['transform_grid_bits'])) for v in line] for line in coordinates];Q=fmpq_mat([[q(v) for v in line] for line in transform]);B=T*Q
            if not B.det():raise ValueError('singular budget congruence')
            ac,ar=congruence(A,B);cc,cr=congruence(component,B);al,au,_=gersh(ac,ar);cl,cu,_=gersh(cc,cr)
            if al<=0 or cu<0:raise ValueError('invalid positive denominator/cap')
            exact=cu/al;scale=1<<decl['relative_cap_publication_bits'];cap=fmpq(int((exact*scale).ceil()),scale)
            payload={'format':'control-budget-congruence-v1','parity':parity,'component':kind,'post_old_transform':transform,'A_lower':str(al),'component_upper':str(cu),'relative_cap':str(cap),'numerical_eigenvalue_proposal_not_proof':float(values[-1])}
            raw=gzip.compress((json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0);path=witness_dir/(label+'-'+kind+'.json.gz');path.write_bytes(raw)
            row['relative_caps'][kind]={'upper':str(cap),'witness':path.relative_to(args.output.parent).as_posix(),'sha256':sha(raw),'bytes':len(raw)}
            print(label,kind,'certified cap',float(cap),flush=True)
        out['parities'][label]=row
    gap=min(q(v['control_selected_S_physical_mass_lower']) for v in out['parities'].values());accuracy=gap/decl['target_accuracy_divisor']
    out['certified_control_selected_S_physical_mass_lower']=str(gap);out['target_canonical_model_error_goal']=str(accuracy);out['accuracy_goal_is_NOT_target_gap']=True;out['status']='CONTROL_BUDGET_AND_PHYSICAL_ACCURACY_SCALE_CERTIFIED'
    args.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n',encoding='utf-8');print(out['status'],flush=True)
if __name__=='__main__':main()
