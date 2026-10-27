"""Derive a fixed T=4/5 first-attempt declaration without target matrices.

This qualifies source/error parameters. A positive reference tail and a small
chosen error tolerance do not establish target low or coupled positivity.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
from flint import arb,acb,ctx,fmpq
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.cert.residual_kernel import _suzuki_residual_series_coefficients,_suzuki_residual_tail_radius

def sha(raw):return hashlib.sha256(raw).hexdigest()
def q(x):return fmpq(x)
def upper(x,bits=192):return fmpq(int((x.upper().fmpq()*(1<<bits)).ceil())+1,1<<bits)
def ceilq(x,bits=192):return fmpq(int((x*(1<<bits)).ceil())+1,1<<bits)
def ceil_log2(x):
    x=q(x)
    if x<=0:raise ValueError('positive amplification required')
    k=int(x.numerator).bit_length()-int(x.denominator).bit_length()
    power=q(2)**k
    return k if x<=power else k+1

def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--reference-audit',type=Path,required=True);p.add_argument('--control-audit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    iraw=args.inputs.read_bytes();inputs=json.loads(iraw);folder=args.inputs.resolve().parent
    def bound_source(key,expected):
        raw=(folder/inputs[key]).read_bytes()
        if sha(raw)!=inputs[expected]:raise ValueError('changed qualified source '+key)
        return raw,json.loads(raw)
    rraw,ref=bound_source('reference_source','reference_source_sha256');braw,budget=bound_source('control_budget_source','control_budget_sha256')
    raraw=args.reference_audit.read_bytes();caraw=args.control_audit.read_bytes();ra=json.loads(raraw);ca=json.loads(caraw)
    if ra['status']!='PASS' or ra['source_sha256']!=sha(rraw) or ca['status']!='PASS' or ca['source_sha256']!=sha(braw):raise ValueError('independent source acceptance required')
    ctx.prec=inputs['scalar_precision_bits'];T=q('4/5');N=ref['N'];M=2*N;R=ref['R'];Rc=2*R;m=q(ref['m']);eta=q(ref['eta']);beta=q(ref['beta']);goal=q(budget['target_canonical_model_error_goal'])
    if ref['support']!='4/5' or N%2 or ref['M']!=M or ref['Rc']!=Rc or not arb(2*T)<arb.pi():raise ValueError('fixed target identity/domain')
    if budget['accuracy_goal_is_NOT_target_gap'] is not True:raise ValueError('accuracy scope')
    prime_upper=upper(2*(arb(2).log()/arb(2).sqrt()+arb(3).log()/arb(3).sqrt()+arb(2).log()/2))
    ladder=[];coefficients=None;K=None
    for order in range(2,N//2,2):
        c=[-T**(d+1)*value for d,value in enumerate(_suzuki_residual_series_coefficients(order))]
        delta=upper(2*arb(T)*_suzuki_residual_tail_radius(acb(2*arb(T)),order))
        rk=2*sum((abs(value)*2**d for d,value in enumerate(c)),q(0))
        cross=upper(arb.pi()/2+arb(prime_upper+rk))
        loss=ceilq(delta+(2*cross*delta+delta*delta)/(m*eta))
        met=loss<=goal;ladder.append({'order':order,'delta_upper':str(delta),'B_K_upper':str(cross),'Lambda_upper':str(loss),'goal_met':met})
        if met:K=order;coefficients=c;break
    if K is None:raise ValueError('accuracy goal not reached in exact-band regime')
    if coefficients[1]!=T*T/48 or not 2*K<N or M<N+K:raise ValueError('residual normalization/band')
    A0=-arb.const_euler()-arb.pi()/2-3*arb.const_log2()-arb.pi().log()
    def g(t):return arb(q('3/4'))*(acb(arb(q('1/4')),arb(t)/2).digamma().real-arb.pi().log())+A0/4-arb(q('1/4')+beta)
    edges=[q(0),q(R)]
    while edges[-1]*q('17/16')<32*R:edges.append(edges[-1]*q('17/16'))
    edges.append(q(32*R));weights=[1/m]
    for edge in edges[1:]:
        value=g(edge)
        if not value>arb(m):raise ValueError('inverse-weight anchor below floor')
        weights.append(upper(1/value,inputs['matrix_publication_bits']))
    if any(weights[i]<weights[i+1] for i in range(len(weights)-1)):raise ValueError('nonmonotone inverse majorant')
    aa=q(ref['inverse_weight']['a']['upper']);leak=q(ref['inverse_weight']['complete_leakage']['upper'])
    if not 0<aa<=1/m or not 0<=leak<=1:raise ValueError('inverse-tail endpoint qualification')
    kappa=aa+(1/m-aa)*leak
    source_amp=ceil_log2(q(21)**(N-1));audit_amp=ceil_log2(q(3)**(M-1)*q(7)**(N-1));upward=q(M+1);cmin=T*R
    for n in range(1,M+1):upward*=1+q(2*n+1)/cmin
    bessel_amp=ceil_log2(upward);block=inputs['precision_block_bits'];base=inputs['matrix_publication_bits']+inputs['numerical_guard_bits']
    def blockceil(v):return ((v+block-1)//block)*block
    source_bits=max(inputs['producer_precision_floor_bits'],blockceil(base+source_amp));audit_bits=max(inputs['independent_precision_floor_bits'],source_bits+1024,blockceil(base+audit_amp),blockceil(base+bessel_amp))
    modules={}
    for name,module in sorted(sys.modules.items()):
        if name.startswith('scripts') and getattr(module,'__file__',None):
            path=Path(module.__file__).resolve()
            if not path.is_relative_to(ROOT):raise ValueError('project import escaped root')
            modules[path.relative_to(ROOT).as_posix()]=sha(path.read_bytes())
    out={'format':'t080-qualified-target-declaration-v1','status':'QUALIFIED_TARGET_PARAMETERS_NOT_POSITIVITY','support':'4/5','N':N,'M':M,'R':R,'Rc':Rc,'alpha':ref['alpha'],'beta':ref['beta'],'m':str(m),'eta':str(eta),'K':K,'kernel_coefficients':[str(c) for c in coefficients],'order_selection_ladder':ladder,'complete_remainder_upper':str(delta),'combined_model_cross_norm_upper':str(cross),'complete_model_error_upper':str(loss),'model_error_accuracy_goal':str(goal),'accuracy_goal_is_NOT_target_gap':True,'frequency_edges':[str(x) for x in edges],'inverse_weight_step_uppers':[str(x) for x in weights],'weighted_physical_tail_inverse_upper':str(kappa),'precision':{'scalar_bits':ctx.prec,'scalar_publication_bits':192,'matrix_publication_bits':inputs['matrix_publication_bits'],'source_bits':source_bits,'independent_bits':audit_bits,'source_coefficient_amplification_bits':source_amp,'independent_coefficient_amplification_bits':audit_amp,'upward_Bessel_amplification_bits':bessel_amp,'numerical_error_physical_norm_goal':str(goal/4),'guarantees_target_gap_false':True},'finite_model_cross_band':{'input_start':N-K,'input_end':N-1,'output_start':N,'output_end':N+K-1,'dimension':K,'all_other_model_cross_entries_zero':True,'low_even_and_polar_terms_required':True},'first_attempt':{'initial_low_dimension':N,'initial_residual_order':K,'source_arithmetic_Gauss_order':(M+N)//2,'independent_combined_square_Gauss_order':N,'parity_dimensions':[N//2,N//2],'core_symmetric_source_entries':3*(N//2)*(N//2+1),'model_error_goal':'accepted old selected-S physical lower /2^20; accuracy policy, never a target positive-gap premise','refinement_policy':'Keep T4/5 fixed. Diagnose numerical width vs analytic loss vs real negative upper. If width fails, increase native precision by1024 and publication by64 only as implicated, retaining versions. If canonical model allowance dominates sensitive directions, increase evenK by2 and recheck2K<N. Alter N/reference/physical split only from a recorded coupled obstruction or complete error requirement, never blind grids. No automatic admission.'},'bindings':{'inputs_sha256':sha(iraw),'reference_source_sha256':sha(rraw),'reference_audit_sha256':sha(raraw),'control_budget_sha256':sha(braw),'control_audit_sha256':sha(caraw),'producer_sha256':sha(Path(__file__).read_bytes())},'imported_project_module_sha256':modules,'target_low_coupling_matrix_computed':False,'target_positivity_proved':False,'production_admission':False}
    args.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':out['status'],'N':N,'K':K,'M':M,'source_bits':source_bits,'independent_bits':audit_bits,'model_error_upper':float(loss),'accuracy_goal':float(goal)}),flush=True)
if __name__=='__main__':main()
