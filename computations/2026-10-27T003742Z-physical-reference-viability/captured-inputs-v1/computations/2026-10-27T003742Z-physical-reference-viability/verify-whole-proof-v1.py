"""Independent zero-float interval-congruence check of the complete paid lower.

This does not establish analytic source truth; run the separate complete source
consumer on the same pinned bytes. It never invokes production admission.
"""
import argparse,gzip,hashlib,json
from pathlib import Path
from flint import fmpq,fmpq_mat
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def q(x):return fmpq(x)
def zero():return fmpq_mat(156,156)
def matrices(descriptor):
    raw=(HERE/descriptor['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=descriptor['sha256'] or len(raw)!=descriptor['size']:raise ValueError('matrix byte binding')
    p=json.loads(gzip.decompress(raw))
    if p['dimension']!=156 or p['bits']!=192 or len(p['upper_triangle'])!=12246:raise ValueError('matrix shape')
    lo=zero();hi=zero();k=0
    for i in range(156):
        for j in range(i,156):
            l,u=[fmpq(v,1<<192) for v in p['upper_triangle'][k]];k+=1
            if l>u:raise ValueError('reversed interval')
            lo[i,j]=lo[j,i]=l;hi[i,j]=hi[j,i]=u
    return lo,hi

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--proposal',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    source_raw=args.source.read_bytes();s=json.loads(source_raw);p=json.loads(args.proposal.read_text())
    if p['source_sha256']!=hashlib.sha256(source_raw).hexdigest():raise ValueError('proposal/source byte binding')
    decl_raw=(HERE/'whole-gram-inputs-v2.json').read_bytes();decl=json.loads(decl_raw)
    if s['inputs_sha256']!=hashlib.sha256(decl_raw).hexdigest():raise ValueError('source/input binding')
    old_raw=(ROOT/decl['old_combined_arithmetic_proof']).read_bytes()
    if hashlib.sha256(old_raw).hexdigest()!=decl['old_combined_arithmetic_proof_sha256']:raise ValueError('retained transform pin')
    old=json.loads(gzip.decompress(old_raw))
    eta=q(decl['reference_eta_lower']);lam=q(decl['model_error_upper'])
    if eta<=0 or s['eta_lower']!=str(eta) or s['model_error_upper']!=str(lam):raise ValueError('changed complete error/reference input')
    result={'format':'whole-paid-lower-exact-assessment-v1','source_sha256':hashlib.sha256(source_raw).hexdigest(),'proposal_sha256':hashlib.sha256(args.proposal.read_bytes()).hexdigest(),'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'arithmetic':'zero float exact fmpq interval centers plus full absolute congruence radius','production_admission':False,'blocks':{}}
    passed=True
    for parity,label in ((0,'even'),(1,'odd')):
        theta=q(p['blocks'][label]['theta'])
        if theta<=0:raise ValueError('nonpositive exact Young parameter')
        al,au=matrices(s['matrices'][f'A_model-{parity}']);hl,hu=matrices(s['matrices'][f'weighted_head-{parity}']);el,eu=matrices(s['matrices'][f'weighted_complete_tail-{parity}'])
        head=(1+theta)/eta;tail=(1+1/theta)/eta
        lower=al-hu*head-eu*tail;upper=au-hl*head-el*tail
        for i,n in enumerate(range(parity,312,2)):
            lower[i,i]-=lam*fmpq(2,2*n+1);upper[i,i]-=lam*fmpq(2,2*n+1)
        center=(lower+upper)*fmpq(1,2);radius=(upper-lower)*fmpq(1,2)
        T=fmpq_mat([[q(x) for x in row] for row in old['blocks'][label]['transform']])
        W=fmpq_mat([[q(x) for x in row] for row in p['blocks'][label]['proposal_transform']])
        U=T*W
        # Nonsingularity is checked exactly; a rank-deficient congruence cannot
        # establish positivity on the whole original low space.
        if not U.det():raise ValueError('singular exact full-space transform')
        absU=fmpq_mat([[abs(U[i,j]) for j in range(156)] for i in range(156)])
        B=U.transpose()*center*U;E=absU.transpose()*radius*absU
        margins=[];diagonal_uppers=[]
        for i in range(156):
            err=sum((E[i,j] for j in range(156)),fmpq(0))
            off=sum((abs(B[i,j]) for j in range(156) if j!=i),fmpq(0))
            margins.append(B[i,i]-off-err);diagonal_uppers.append(B[i,i]+E[i,i])
        minimum=min(margins);ok=minimum>0;passed &= ok
        result['blocks'][label]={'theta':str(theta),'dimension':156,'minimum_complete_congruence_margin':str(minimum),'positive_complete_paid_lower':ok,'row_margins':[str(x) for x in margins],'minimum_directional_upper_of_selected_lower_not_actual_criterion':str(min(diagonal_uppers))}
        print(label,'exact complete margin sign',int(minimum>0)-int(minimum<0),flush=True)
    result['status']='PASS_COMPLETE_SUPPORTED_GRAM_CRITERION' if passed else 'UNRESOLVED_COMPLETE_PAID_LOWER_NOT_POSITIVE'
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],flush=True)
if __name__=='__main__':main()
