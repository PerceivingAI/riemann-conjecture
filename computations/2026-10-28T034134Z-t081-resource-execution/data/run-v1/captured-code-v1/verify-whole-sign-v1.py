"""Zero-float full T81/100 interval sign; analytic source truth is separate."""
import argparse,gzip,hashlib,json
from pathlib import Path
from flint import fmpq,fmpq_mat
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];DIM=413;N=826;BITS=256
INPUTS_PIN='19eac80d7869fcc6d6ddd0d33dcb90901b65254b2f076c6964148575019982a1'

def require(ok,message):
    if not ok:raise ValueError(message)

def q(x):
    require(type(x) is str,'rational must be a string');r=fmpq(x)
    require(str(r)==x,'noncanonical rational');return r

def pinned(path,sha):
    raw=path.read_bytes();require(hashlib.sha256(raw).hexdigest()==sha,'SHA mismatch '+str(path));return raw

def unique(items):
    out={}
    for k,v in items:require(k not in out,'duplicate JSON key');out[k]=v
    return out

def load(raw):return json.loads(raw,object_pairs_hook=unique,parse_constant=lambda v:(_ for _ in ()).throw(ValueError('nonfinite JSON')))

def matrix(base,d,kind,parity):
    path=(base/d['path']).resolve();require(path.is_relative_to(base.resolve()),'matrix path escapes source directory')
    raw=pinned(path,d['sha256']);require(len(raw)==d['size'],'matrix byte size');p=load(gzip.decompress(raw))
    require((p['dimension'],p['bits'],p['kind'],p['parity'])==(DIM,BITS,kind,parity),'matrix metadata')
    require(len(p['upper_triangle'])==DIM*(DIM+1)//2,'matrix triangle size');lo=fmpq_mat(DIM,DIM);hi=fmpq_mat(DIM,DIM);k=0
    for i in range(DIM):
        for j in range(i,DIM):
            pair=p['upper_triangle'][k];k+=1;require(len(pair)==2 and all(type(x) is int for x in pair),'integer endpoints')
            l,u=[fmpq(v,1<<BITS) for v in pair];require(l<=u,'reversed interval');lo[i,j]=lo[j,i]=l;hi[i,j]=hi[j,i]=u
    return lo,hi

def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--proposal',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    require(not args.output.exists(),'fresh output required');iraw=pinned(args.inputs,INPUTS_PIN);inp=load(iraw)
    decl=load(pinned(ROOT/inp['target_declaration'],inp['target_declaration_sha256']));sraw=args.source.read_bytes();s=load(sraw);praw=args.proposal.read_bytes();proposal=load(gzip.decompress(praw))
    require(s['inputs_sha256']==INPUTS_PIN==proposal['inputs_sha256'],'source/proposal inputs binding')
    require(proposal['source_sha256']==hashlib.sha256(sraw).hexdigest(),'proposal source binding')
    require((s['support'],s['N'],s['order'],s['physical_extent'],s['bits'])==('81/100',N,86,1652,BITS),'frozen source metadata')
    eta=q(decl['eta']);lam=q(decl['complete_model_error_upper']);goal=q(decl['precision']['numerical_error_physical_norm_goal'])
    require(s['eta_lower']==str(eta) and s['model_error_upper']==str(lam) and 0<eta<=1 and lam>=0,'complete scalar inputs')
    out={'format':'t081-complete-paid-lower-exact-assessment-v1','source_sha256':hashlib.sha256(sraw).hexdigest(),'proposal_sha256':hashlib.sha256(praw).hexdigest(),'inputs_sha256':INPUTS_PIN,'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'analytic_source_acceptance_is_separate':True,'production_admission':False,'blocks':{}};positive=True;width_ok=True;negative=False
    for parity,label in ((0,'even'),(1,'odd')):
        theta=q(proposal['blocks'][label]['theta']);require(theta>0,'positive exact Young parameter')
        al,au=matrix(args.source.parent,s['matrices'][f'A_model-{parity}'],'A_model',parity)
        hl,hu=matrix(args.source.parent,s['matrices'][f'weighted_head-{parity}'],'weighted_head',parity)
        el,eu=matrix(args.source.parent,s['matrices'][f'weighted_complete_tail-{parity}'],'weighted_complete_tail',parity)
        head=(1+theta)/eta;tail=(1+1/theta)/eta;lower=al-hu*head-eu*tail;upper=au-hl*head-el*tail
        masses=[fmpq(2,2*n+1) for n in range(parity,N,2)]
        for i,d in enumerate(masses):lower[i,i]-=lam*d;upper[i,i]-=lam*d
        center=(lower+upper)*fmpq(1,2);radius=(upper-lower)*fmpq(1,2)
        numerical=max(sum((radius[i,j] for j in range(DIM)),fmpq(0)) for i in range(DIM))/min(masses);block_width_ok=numerical<=goal;width_ok &= block_width_ok
        w=proposal['blocks'][label]['proposal_transform'];require(len(w)==DIM and all(len(row)==DIM for row in w),'full proposal shape')
        U=fmpq_mat([[q(x) for x in row] for row in w]);require(U.det()!=0,'singular full congruence')
        absU=fmpq_mat([[abs(U[i,j]) for j in range(DIM)] for i in range(DIM)]);B=U.transpose()*center*U;E=absU.transpose()*radius*absU
        margins=[B[i,i]-sum((abs(B[i,j]) for j in range(DIM) if j!=i),fmpq(0))-sum((E[i,j] for j in range(DIM)),fmpq(0)) for i in range(DIM)]
        upperdirs=[B[i,i]+E[i,i] for i in range(DIM)];worst=min(range(DIM),key=lambda i:upperdirs[i]);minimum=min(margins);ok=minimum>0;positive &= ok;negative |= upperdirs[worst]<0
        trace_mass=sum((masses[i]*sum((U[i,j]**2 for j in range(DIM)),fmpq(0)) for i in range(DIM)),fmpq(0));direction_mass=sum((masses[i]*U[i,worst]**2 for i in range(DIM)),fmpq(0))
        out['blocks'][label]={'dimension':DIM,'theta':str(theta),'exact_nonsingularity':True,'positive_complete_paid_lower':ok,'minimum_complete_congruence_margin':str(minimum),'row_margins':[str(x) for x in margins],'complete_physical_lower_if_positive':str(minimum/trace_mass) if ok else None,'numerical_radius_physical_upper':str(numerical),'numerical_radius_physical_goal':str(goal),'numerical_width_goal_passed':block_width_ok,'minimum_directional_upper_of_selected_lower_NOT_actual_criterion':str(upperdirs[worst]),'selected_lower_negative_direction_proved':upperdirs[worst]<0,'direction_index':worst,'direction_mass':str(direction_mass),'selected_lower_direction_physical_upper':str(upperdirs[worst]/direction_mass),'direction_coefficients':[str(U[i,worst]) for i in range(DIM)] if upperdirs[worst]<0 else []}
        print(label,'positive complete sign',ok,'negative selected lower direction',upperdirs[worst]<0,'physical width qualified',block_width_ok,flush=True)
    out['status']='PASS_COMPLETE_SOURCE_CONDITIONAL_CANDIDATE' if positive and width_ok else 'NUMERICAL_WIDTH_GOAL_FAILED' if not width_ok else 'SELECTED_CONSERVATIVE_SCHUR_NEGATIVE_NOT_WEIL_NEGATIVITY' if negative else 'UNRESOLVED_COMPLETE_PAID_LOWER'
    args.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n',encoding='utf-8');print(out['status'],flush=True)
if __name__=='__main__':main()
