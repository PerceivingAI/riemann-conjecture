"""Exact finite residual cross map and complete known-control error qualification."""
from __future__ import annotations
import argparse,gzip,hashlib,json,math,sys
from pathlib import Path
from fractions import Fraction as Q
from flint import arb,acb,ctx,fmpq
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT))
from scripts.cert.residual_kernel import _suzuki_residual_series_coefficients,_suzuki_residual_tail_radius
PROOF='9e7b0e03254261e4a971be192d21c7991faefaf2f71b0cbbfe8faf946b186cef'
CRITICAL='6e18940d7e34eaa29acd6d3457f75c036729b1a4de652ac0b37802b8c0486340'
def q(x):
    if isinstance(x,Q):return x
    z=fmpq(x);return Q(int(z.numerator),int(z.denominator))
def f(x):x=q(x);return fmpq(x.numerator,x.denominator)
def a(x):x=q(x);return arb(x.numerator)/x.denominator
def text(x):return str(f(x))
def ends(x):return q(x.lower().fmpq()),q(x.upper().fmpq())
def pub(x):
    lo,hi=ends(x);s=1<<192
    return {'lower':text(Q(math.floor(lo*s)-1,s)),'upper':text(Q(math.ceil(hi*s)+1,s))}
def ceil_upper(x):return Q(math.ceil(ends(x)[1]*(1<<192))+1,1<<192)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise ValueError('fresh output required')
    declraw=(HERE/'qualification-inputs-v1.json').read_bytes();decl=json.loads(declraw)
    proofraw=(ROOT/decl['old_positive_proof']).read_bytes();criticalraw=(ROOT/decl['critical_witness_packet']).read_bytes()
    if hashlib.sha256(proofraw).hexdigest()!=PROOF or hashlib.sha256(criticalraw).hexdigest()!=CRITICAL:raise ValueError('accepted premise byte identity')
    proof=json.loads(gzip.decompress(proofraw));critical=json.loads(criticalraw)
    if proof['support']!=[3,4] or proof['dimension']!=312 or proof['status']!='COMPLETE_POSITIVE_SUFFICIENT_LOWER':raise ValueError('known positive control meaning')
    g=min(q(b['mass_normalized_gap_exact']) for b in proof['blocks'].values());mu=Q(63,32)-Q(4,10**49);b0=Q(49,32)+Q(2,10**24)
    ell=min(g/(1+2*(b0/mu)**2),mu/2);control=Q(1,10**15)
    if not ell>control:raise ValueError('known full-gap control not established')
    ctx.prec=512;T=Q(3,4);N=312;target=control/1024
    ladder=[];K=None
    for order in range(2,N//2,2):
        raw=2*a(T)*_suzuki_residual_tail_radius(acb(a(2*T)),order);du=ceil_upper(raw)
        ladder.append({'order':order,'complete_remainder':pub(raw),'published_upper':text(du)})
        if du<=target:K=order;delta=du;break
    if K is None:raise ValueError('derived error target not reached in declared exact-band regime')
    coeff=[-f(T)**(d+1)*c for d,c in enumerate(_suzuki_residual_series_coefficients(K))]
    if coeff[1]!=f(T*T/48):raise ValueError('residual cusp normalization')
    inputs=list(range(N-K,N));outputs=list(range(N,N+K));matrix=[[fmpq(0) for n in inputs] for m in outputs]
    for col,n in enumerate(inputs):
        current={n:fmpq(1)}
        for step in range(1,K+1):
            moved={}
            for j,value in current.items():
                if j<=0:raise ValueError('declared primitive degree regime')
                value/=2*j+1
                moved[j+1]=moved.get(j+1,fmpq(0))+value
                moved[j-1]=moved.get(j-1,fmpq(0))-value
            current=moved
            if step%2==0:
                factor=2*math.factorial(step-1)*coeff[step-1]
                for m,value in current.items():
                    if m>=N:matrix[m-N][col]+=factor*value
    for i,m in enumerate(outputs):
        for j,n in enumerate(inputs):
            if (m+n)%2 or m-n>K:
                if matrix[i][j]:raise ValueError('exact parity/band invariant')
    eta=1-Q(9,10**49);floor=Q(1,3);r=Q(1,300000)
    bk=arb.pi()/2+a(Q(49,32)+r+delta)
    Lambda=a(delta)+(2*bk*a(delta)/a(floor)+a(delta)**2/a(floor))/a(eta)
    lu=ceil_upper(Lambda);necessary=control-delta-lu
    if not lu<=control/16 or not necessary>=Q(7,8)*control:raise ValueError('whole-low model error budget failed')
    diagnostic=[]
    for row in critical['witnesses']:
        x=list(map(q,row['exact_legendre_coefficients']));x+= [Q(0)]*(N-len(x))
        norm=sum(Q(2,2*n+1)*v*v for n,v in enumerate(x))
        if norm!=q(row['exact_mass']):raise ValueError('critical physical mass')
        images=[sum((value*f(x[n]) for n,value in zip(inputs,rr)),fmpq(0)) for rr in matrix]
        image_norm=sum(Q(2,2*m+1)*q(v)**2 for m,v in zip(outputs,images))
        strip_norm=sum(Q(2,2*n+1)*x[n]**2 for n in inputs)
        complete=(a(image_norm).sqrt()+a(delta)*a(norm).sqrt())**2/(a(floor)*a(norm))
        diagnostic.append({'parity':row['parity'],'mass':text(norm),'input_strip_mass_fraction':text(strip_norm/norm),'exact_model_output_coefficients':[str(v) for v in images],'model_output_norm_squared':text(image_norm),'full_residual_weighted_image_upper':pub(complete)['upper'],'scope':'Unit-normalized actual residual-image upper including full model remainder; not a separate mixed-Gram positivity allowance.'})
    project=[]
    for name,module in sorted(sys.modules.items()):
        if name.startswith('scripts') and getattr(module,'__file__',None):
            path=Path(module.__file__).resolve()
            if not path.is_relative_to(ROOT):raise ValueError('project import escaped captured source root')
            project.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    obj={'format':'exact-structured-residual-coupling-v1','status':'QUALIFIED_EXACT_WHOLE_LOW_RESIDUAL_MODEL_AND_ERROR_BUDGET','support':'3/4','N':N,'order':K,'input_modes':inputs,'output_modes':outputs,'basis':'ordinary_unnormalized_legendre_expansion_coefficients','mass_rule':'2/(2n+1)','kernel_coefficients':[str(v) for v in coeff],'coefficient_map':[[str(v) for v in row] for row in matrix],'complete_remainder_upper':text(delta),'order_selection_ladder':ladder,'old_positive_proof_sha256':PROOF,'critical_witness_sha256':CRITICAL,'finite_control_gap':text(g),'control_mu':text(mu),'control_cross_bound':text(b0),'derived_full_form_gap':text(ell),'adopted_control_gap':text(control),'combined_model_cross_norm_upper':pub(bk)['upper'],'complete_model_error_upper':text(lu),'whole_low_necessary_budget_lower':text(necessary),'critical_diagnostics':diagnostic,'model_R_retained_inside_signed_V_P_R_Gram':True,'full_model_low_R_even_terms_not_discarded':True,'mixed_Gram_or_new_Schur_sign_computed':False,'new_support_or_admission':False,'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inputs_sha256':hashlib.sha256(declraw).hexdigest(),'imported_project_modules':project}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as handle:json.dump(obj,handle,sort_keys=True,indent=2);handle.write('\n')
    print(json.dumps({'status':obj['status'],'order':K,'band_shape':[K,K],'nonzero_entries':sum(bool(v) for row in matrix for v in row),'delta_upper':float(delta),'complete_error_upper':float(lu),'known_gap_lower':float(control),'whole_low_necessary_budget_lower':float(necessary),'critical_residual_weighted_image_uppers':[float(q(v['full_residual_weighted_image_upper'])) for v in diagnostic]}))
if __name__=='__main__':
    try:main()
    except (ValueError,AssertionError,KeyError,ZeroDivisionError) as exc:raise SystemExit(type(exc).__name__+': '+str(exc))
