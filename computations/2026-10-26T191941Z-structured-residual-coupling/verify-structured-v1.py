"""Independent polynomial/source and complete structured-error verification."""
import argparse,gzip,hashlib,json,math
from fractions import Fraction as Q
from pathlib import Path
from flint import arb,ctx,fmpq,fmpq_poly
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PINS=('9e7b0e03254261e4a971be192d21c7991faefaf2f71b0cbbfe8faf946b186cef','6e18940d7e34eaa29acd6d3457f75c036729b1a4de652ac0b37802b8c0486340')
def q(v):
    if isinstance(v,Q):return v
    v=fmpq(v);return Q(int(v.numerator),int(v.denominator))
def f(v):v=q(v);return fmpq(v.numerator,v.denominator)
def a(v):v=q(v);return arb(v.numerator)/v.denominator
def ends(v):return q(v.lower().fmpq()),q(v.upper().fmpq())
def contains(name,pair,v):
    lo,hi=ends(v)
    if not q(pair['lower'])<=lo<=hi<=q(pair['upper']):raise ValueError(name+' enclosure')
def upper(name,bound,v):
    if q(bound)<ends(v)[1]:raise ValueError(name+' upper')
def legendre(n):
    values=[fmpq(0) for _ in range(n+1)]
    for k in range(n//2+1):values[n-2*k]=f(Q((-1)**k*math.comb(n,k)*math.comb(2*n-2*k,n),1<<n))
    return fmpq_poly(values)
def independent_coefficients(K,T):
    # Solve (1-exp(-2t))g=exp(-t/2)-(1-exp(-2t))/(2t).
    D=[Q(0)]+[Q((-1)**(j+1)*2**j,math.factorial(j)) for j in range(1,K+3)]
    g=[];out=[]
    for n in range(K+1):
        rhs=Q(-1,2)**(n+1)/math.factorial(n+1)-D[n+2]/2
        value=(rhs-sum(D[j]*g[n+1-j] for j in range(2,n+2)))/2;g.append(value)
        aa=value-(Q(2,2**n*math.factorial(n)) if n%2==0 else 0)
        out.append(-T**(n+1)*aa)
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('packet',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise ValueError('fresh audit output required')
    raw=args.packet.read_bytes();s=json.loads(raw);declraw=(HERE/'qualification-inputs-v1.json').read_bytes();decl=json.loads(declraw)
    if s['format']!='exact-structured-residual-coupling-v1' or s['N']!=312 or s['support']!='3/4':raise ValueError('declared control')
    if s['producer_sha256']!=hashlib.sha256((HERE/'qualify-structured-v1.py').read_bytes()).hexdigest() or s['inputs_sha256']!=hashlib.sha256(declraw).hexdigest():raise ValueError('executable/declaration binding')
    pr=(ROOT/decl['old_positive_proof']).read_bytes();cr=(ROOT/decl['critical_witness_packet']).read_bytes()
    if (hashlib.sha256(pr).hexdigest(),hashlib.sha256(cr).hexdigest())!=PINS or (s['old_positive_proof_sha256'],s['critical_witness_sha256'])!=PINS:raise ValueError('accepted premise bytes')
    proof=json.loads(gzip.decompress(pr));critical=json.loads(cr);gaps=[]
    if proof['support']!=[3,4] or proof['dimension']!=312 or proof['basis']!='ordinary_unnormalized_legendre':raise ValueError('old proof source meaning')
    for parity,name in enumerate(('even','odd')):
        block=proof['blocks'][name];transform=block['transform']
        if len(transform)!=156 or any(len(row)!=156 for row in transform):raise ValueError('whole old parity witness')
        trace=sum((Q(2,2*(2*j+parity)+1)*sum(q(v)**2 for v in row) for j,row in enumerate(transform)),Q(0))
        gap=q(block['claimed_margin'])/trace
        if gap!=q(block['mass_normalized_gap_exact']) or gap<=0:raise ValueError('physical gap conversion')
        gaps.append(gap)
    g=min(gaps);mu=Q(63,32)-Q(4,10**49);b0=Q(49,32)+Q(2,10**24);ell=min(g/(1+2*(b0/mu)**2),mu/2);control=Q(1,10**15)
    for key,value in [('finite_control_gap',g),('control_mu',mu),('control_cross_bound',b0),('derived_full_form_gap',ell),('adopted_control_gap',control)]:
        if q(s[key])!=value:raise ValueError(key)
    if not ell>control:raise ValueError('control full-gap lower')
    ctx.prec=768;T=Q(3,4);N=312;K=s['order'];target=control/1024
    if K%2 or K<2 or 2*K>=N:raise ValueError('declared exact-band regime')
    def remainder(k):
        u=2*a(T);p=arb.pi();regular=(2/p)*(u/p)**(k+1)/(1-u/p)
        polar=2*a(T)**(k+1)/math.factorial(k+1)/(1-a(T)/(k+2))
        return 2*a(T)*(regular+polar)
    if [v['order'] for v in s['order_selection_ladder']]!=list(range(2,K+1,2)):raise ValueError('complete derived-order ladder')
    for row in s['order_selection_ladder']:
        rr=remainder(row['order']);contains('complete kernel remainder',row['complete_remainder'],rr);upper('published kernel remainder',row['published_upper'],rr)
        if row['order']<K and not ends(rr)[0]>target:raise ValueError('least even sufficient order not established')
    delta=q(s['complete_remainder_upper'])
    if delta!=q(s['order_selection_ladder'][-1]['published_upper']) or not 0<delta<=target:raise ValueError('full infinite remainder publication')
    upper('full infinite operator remainder',delta,remainder(K))
    coeff=independent_coefficients(K,T)
    if list(map(q,s['kernel_coefficients']))!=coeff:raise ValueError('independent full residual Taylor coefficients')
    inputs=list(range(N-K,N));outputs=list(range(N,N+K))
    if s['input_modes']!=inputs or s['output_modes']!=outputs or s['basis']!='ordinary_unnormalized_legendre_expansion_coefficients' or s['mass_rule']!='2/(2n+1)':raise ValueError('whole-map physical convention')
    U=s['coefficient_map']
    if len(U)!=K or any(len(row)!=K for row in U):raise ValueError('complete cross-band matrix')
    high={m:legendre(m) for m in outputs};verified=[[fmpq(0) for n in inputs] for m in outputs]
    for col,n in enumerate(inputs):
        primitive=legendre(n);combined=fmpq_poly([0])
        for step in range(1,K+1):
            primitive=primitive.integral()
            if step%2==0:combined+=2*math.factorial(step-1)*f(coeff[step-1])*primitive
        # Exact power-polynomial high projection, not the producer's Legendre walk.
        for m in reversed(outputs):
            value=combined[m]/high[m][m];verified[m-N][col]=value;combined-=value*high[m]
            if q(U[m-N][col])!=q(value):raise ValueError('exact residual cross entry '+str((m,n)))
        if combined.degree()>=N:raise ValueError('unpaid model high polynomial')
    for i,m in enumerate(outputs):
        for j,n in enumerate(inputs):
            if ((m+n)%2 or m-n>K) and verified[i][j]:raise ValueError('parity/band invariant')
    eta=1-Q(9,10**49);floor=Q(1,3);bk=arb.pi()/2+a(Q(49,32)+Q(1,300000)+delta)
    upper('combined signed model cross bound',s['combined_model_cross_norm_upper'],bk)
    Lambda=a(delta)+(2*bk*a(delta)/a(floor)+a(delta)**2/a(floor))/a(eta)
    lu=q(s['complete_model_error_upper']);upper('complete low/coupling model error',lu,Lambda)
    necessary=control-delta-lu
    if q(s['whole_low_necessary_budget_lower'])!=necessary or lu>control/16 or necessary<Q(7,8)*control:raise ValueError('whole-low necessary error budget')
    if len(s['critical_diagnostics'])!=2:raise ValueError('both critical controls')
    for original,reported in zip(critical['witnesses'],s['critical_diagnostics']):
        x=list(map(q,original['exact_legendre_coefficients']));x+=[Q(0)]*(N-len(x));norm=sum(Q(2,2*n+1)*v*v for n,v in enumerate(x))
        images=[sum((value*f(x[n]) for n,value in zip(inputs,row)),fmpq(0)) for row in verified]
        if reported['parity']!=original['parity'] or list(map(q,reported['exact_model_output_coefficients']))!=[q(v) for v in images]:raise ValueError('critical exact image')
        normout=sum(Q(2,2*m+1)*q(v)**2 for m,v in zip(outputs,images));head=sum(Q(2,2*n+1)*x[n]**2 for n in inputs)/norm
        if q(reported['mass'])!=norm or norm!=q(original['exact_mass']) or q(reported['model_output_norm_squared'])!=normout or q(reported['input_strip_mass_fraction'])!=head:raise ValueError('critical physical image mass')
        full=3*(a(normout/norm).sqrt()+a(delta))**2;upper('complete critical residual image',reported['full_residual_weighted_image_upper'],full)
    if not s['model_R_retained_inside_signed_V_P_R_Gram'] or not s['full_model_low_R_even_terms_not_discarded'] or s['mixed_Gram_or_new_Schur_sign_computed'] or s['new_support_or_admission']:raise ValueError('false mathematical scope')
    for item in s['imported_project_modules']:
        path=(ROOT/item['path']).resolve()
        if not path.is_relative_to(ROOT) or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('captured canonical helper identity')
    audit={'format':'independent-structured-residual-audit-v1','status':'PASS_EXACT_WHOLE_MAP_AND_COMPLETE_ERROR_BUDGET','source_sha256':hashlib.sha256(raw).hexdigest(),'audit_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'precision_bits':768,'N':N,'order':K,'matrix_entries_checked':K*K,'exact_nonzero_entries':sum(bool(v) for row in verified for v in row),'complete_infinite_kernel_remainder_checked':True,'old_gap_conversion_reconstructed_not_new_source_replay':True,'whole_low_budget_lower':s['whole_low_necessary_budget_lower'],'critical_images_checked':2,'new_mixed_Gram_or_Schur_sign':False,'new_support_or_admission':False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as handle:json.dump(audit,handle,sort_keys=True,indent=2);handle.write('\n')
    print(json.dumps(audit))
if __name__=='__main__':
    try:main()
    except (ValueError,AssertionError,KeyError,ZeroDivisionError) as exc:raise SystemExit(type(exc).__name__+': '+str(exc))
