"""Zero-float independent interval endpoint audit of accepted-control budgets.

Analytic truth of the retained control remains its previously accepted premise.
No target low/coupling source or target positivity is tested here.
"""
import argparse,gzip,hashlib,json
from pathlib import Path
from flint import fmpq,fmpq_mat
ROOT=Path(__file__).resolve().parents[1];N=156

def q(x):return fmpq(x)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def z():return fmpq_mat(N,N)
def load_matrix(folder,entry):
    raw=(folder/entry['path']).read_bytes()
    if sha(raw)!=entry['sha256'] or len(raw)!=entry['size']:raise ValueError('control matrix bytes')
    p=json.loads(gzip.decompress(raw));lower=z();upper=z();index=0
    for i in range(N):
        for j in range(i,N):
            lo,hi=(fmpq(x,1<<p['bits']) for x in p['upper_triangle'][index]);index+=1
            if lo>hi:raise ValueError('reversed interval')
            lower[i,j]=lower[j,i]=lo;upper[i,j]=upper[j,i]=hi
    return lower,upper

def directed(pair,U):
    plus=fmpq_mat([[max(q(0),U[i,j]) for j in range(N)] for i in range(N)])
    minus=fmpq_mat([[max(q(0),-U[i,j]) for j in range(N)] for i in range(N)])
    l,h=pair
    lower=plus.transpose()*l*plus+minus.transpose()*l*minus-plus.transpose()*h*minus-minus.transpose()*h*plus
    upper=plus.transpose()*h*plus+minus.transpose()*h*minus-plus.transpose()*l*minus-minus.transpose()*l*plus
    low=min(lower[i,i]-sum((max(abs(lower[i,j]),abs(upper[i,j])) for j in range(N) if i!=j),q(0)) for i in range(N))
    high=max(upper[i,i]+sum((max(abs(lower[i,j]),abs(upper[i,j])) for j in range(N) if i!=j),q(0)) for i in range(N))
    error=max(sum(((upper[i,j]-lower[i,j])/2 for j in range(N)),q(0)) for i in range(N))
    return low,high,error

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,required=True);ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    raw=args.source.read_bytes();packet=json.loads(raw);iraw=args.inputs.read_bytes();decl=json.loads(iraw)
    if packet['inputs_sha256']!=sha(iraw) or packet['producer_sha256']!=sha((ROOT/'scripts/weil_t080_control_budget.py').read_bytes()):raise ValueError('budget source binding')
    folder=ROOT/decl['control_directory'];mraw=(folder/'manifest.json').read_bytes()
    if sha(mraw)!=decl['control_manifest_sha256'] or packet['control_manifest_sha256']!=sha(mraw):raise ValueError('retained control seal')
    members={x['path']:x for x in json.loads(mraw)['members']}
    def accepted(path):
        r=(folder/path).read_bytes()
        if sha(r)!=members[path]['sha256']:raise ValueError('accepted control changed')
        return r
    control_raw=accepted(decl['control_source']);source=json.loads(control_raw);proposal=json.loads(accepted(decl['control_proposal']));proof=json.loads(accepted(decl['control_exact_proof']))
    if packet['control_source_sha256']!=sha(control_raw) or proof['source_sha256']!=sha(control_raw):raise ValueError('control source identity')
    oldraw=(ROOT/decl['old_transform_proof']).read_bytes()
    if sha(oldraw)!=decl['old_transform_sha256']:raise ValueError('old coordinate identity')
    old=json.loads(gzip.decompress(oldraw));eta=q(source['eta_lower']);lam=q(source['model_error_upper']);summary={};physical=[]
    for parity,label in ((0,'even'),(1,'odd')):
        A=load_matrix(folder,source['matrices'][f'A_model-{parity}']);H=load_matrix(folder,source['matrices'][f'weighted_head-{parity}']);E=load_matrix(folder,source['matrices'][f'weighted_complete_tail-{parity}']);theta=q(proposal['blocks'][label]['theta'])
        H=tuple(m*((1+theta)/eta) for m in H);E=tuple(m*((1+1/theta)/eta) for m in E);D=z()
        for i,n in enumerate(range(parity,312,2)):D[i,i]=fmpq(2,2*n+1)
        R=D*lam;total=(H[0]+E[0]+R,H[1]+E[1]+R);parts={'finite_head':H,'complete_physical_tail':E,'canonical_residual_model_error':(R,R),'combined_paid':total}
        T=fmpq_mat([[q(x) for x in row] for row in old['blocks'][label]['transform']]);W=fmpq_mat([[q(x) for x in row] for row in proposal['blocks'][label]['proposal_transform']]);U=T*W
        if not U.det():raise ValueError('singular old coordinate')
        sl,su,error=directed((A[0]-total[1],A[1]-total[0]),U);row=packet['parities'][label]
        if sl!=q(proof['blocks'][label]['minimum_complete_congruence_margin']) or sl<=0:raise ValueError('whole selected S lower')
        tr=sum((D[i,i]*U[i,j]**2 for i in range(N) for j in range(N)),q(0));inv=U.inv();itr=sum((inv[i,j]**2/D[j,j] for i in range(N) for j in range(N)),q(0));gap=sl/tr;physical.append(gap)
        checks={'control_selected_S_physical_mass_lower':gap,'accepted_S_margin':sl,'physical_coordinate_frobenius_squared':tr,'inverse_physical_coordinate_frobenius_squared':itr,'physical_coordinate_condition_squared_upper':tr*itr,'selected_S_physical_condition_upper':su/sl*tr*itr,'all_source_interval_radius_over_accepted_margin':error/sl}
        for name,value in checks.items():
            if q(row[name])!=value:raise ValueError('invalid physical/conditioning bound '+name)
        caps={}
        for kind,part in parts.items():
            desc=row['relative_caps'][kind];wraw=(args.source.parent/desc['witness']).read_bytes()
            if sha(wraw)!=desc['sha256'] or len(wraw)!=desc['bytes']:raise ValueError('budget witness bytes')
            witness=json.loads(gzip.decompress(wraw));V=fmpq_mat([[q(x) for x in line] for line in witness['post_old_transform']]);Q=T*V
            if not Q.det():raise ValueError('singular whole-space budget witness')
            al,_,_=directed(A,Q);_,cu,_=directed(part,Q);cap=q(desc['upper'])
            if al<=0 or cu<0 or al!=q(witness['A_lower']) or cu!=q(witness['component_upper']) or cap!=q(witness['relative_cap']) or cap*al<cu:raise ValueError('false whole-space component cap '+kind)
            caps[kind]=str(cap)
        if q(caps['combined_paid'])>=1:raise ValueError('known control combined budget is not certified below one')
        summary[label]={'relative_caps':caps,'physical_selected_S_lower':str(gap)}
    gap=min(physical);accuracy=gap/decl['target_accuracy_divisor']
    if q(packet['certified_control_selected_S_physical_mass_lower'])!=gap or q(packet['target_canonical_model_error_goal'])!=accuracy or packet['accuracy_goal_is_NOT_target_gap'] is not True or packet['target_matrices_computed'] is not False:raise ValueError('invalid target-accuracy scope')
    result={'format':'t080-control-budget-independent-audit-v1','status':'PASS','source_sha256':sha(raw),'consumer_sha256':sha(Path(__file__).read_bytes()),'arithmetic':'zero float direct positive/negative endpoint congruence; no producer imports','whole_space_caps_checked':8,'parities':summary,'target_model_error_goal':str(accuracy),'target_matrices_computed':False}
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','whole_space_caps_checked':8,'target_matrices_computed':False}),flush=True)
if __name__=='__main__':main()
