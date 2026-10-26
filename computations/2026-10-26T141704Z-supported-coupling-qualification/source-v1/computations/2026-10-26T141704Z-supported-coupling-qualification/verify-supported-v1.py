"""Independent full-cell supported-source acceptance; no full Gram positivity."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from flint import arb,acb,ctx
from scripts.cert.constants import arb_to_rational_enclosure


def aq(x):
    x=Q(x);return arb(x.numerator)/x.denominator

def lo(x):return arb_to_rational_enclosure(x)[0]
def hi(x):return arb_to_rational_enclosure(x)[1]
def bounds(x):return {'lower':str(lo(x)),'upper':str(hi(x))}
def require(test,message):
    if not test:raise ValueError(message)

def rat(x):
    require(isinstance(x,str) and str(Q(x))==x,'noncanonical rational')
    return Q(x)

def forbid_float(x):raise ValueError('nonexact JSON value')
def contain(claim,lower,upper,label):
    require(rat(claim['lower'])<=lower<=upper<=rat(claim['upper']),'dishonest '+label)


def audit(path):
    raw=path.read_bytes();packet=json.loads(raw,parse_float=forbid_float,parse_constant=forbid_float)
    formats={f'research-supported-coupling-qualification-v{k}':k for k in [1,2,3]}
    require(packet['format'] in formats,'unknown source version');version=formats[packet['format']];here=Path(__file__).parent
    producer=here/f'build-supported-v{version}.py';inputs=here/f'qualification-inputs-v{version}.json';pins=json.loads(inputs.read_bytes())
    require(hashlib.sha256(producer.read_bytes()).hexdigest()==packet['producer_sha256'],'changed producer fingerprint')
    require(hashlib.sha256(inputs.read_bytes()).hexdigest()==packet['inputs_sha256'],'changed declared inputs')
    require((packet['support'],packet['degrees'],packet['reference_N'],packet['source_precision_bits'],packet['residual_terms'])==('3/4',[0,1],312,384,128),'changed fixed source case')
    require((pins['alpha'],pins['beta'],pins['m'],pins['audit_precision_bits'],pins['individual_L2_accuracy'])==('1/4','873/1024','1/3',512,'1/16'),'changed reference or accuracy')
    ctx.prec=512;T=Q(3,4);L=2*T;M=128;delta=T/(1<<32);pi=arb.pi();rootL=aq(L).sqrt();c0=1/rootL;c1=(3/aq(L)).sqrt()/aq(T)
    A0=acb(aq(Q(1,4)),0).digamma().real-pi.log();alpha=Q(1,4);beta=Q(873,1024);floor=Q(1,3)
    require(rat(packet['cap_width'])==delta,'changed endpoint caps')
    log2=arb(2).log();log3=arb(3).log();terms=[(2,log2,log2/arb(2).sqrt()),(3,log3,log3/arb(3).sqrt()),(4,2*log2,log2/2)]
    require(all(log<aq(L) for _,log,_ in terms) and aq(L)<arb(5).log(),'incomplete strict arithmetic window')
    ex=(aq(T)/2).exp();inv=(-aq(T)/2).exp();hc=2*(ex-inv)/rootL;hs=c1*(2*aq(T)*(ex+inv)-4*(ex-inv));require(lo(hs)>0,'odd pole normalization unresolved')
    def F(r):
        require(lo(r)>0,'source interval meets endpoint singularity')
        z=(-r/2).exp();return ((1+z)/(1-z)).log()/2+z.atan()
    def kernel(r):return (-r/2).exp()/(1-(-2*r).exp())
    def moment_range(left,right,b):
        a=aq(left)*(-aq(b*left)).exp();z=aq(right)*(-aq(b*right)).exp();lower=min(lo(a),lo(z));upper=max(hi(a),hi(z))
        if left<=1/b<=right:upper=max(upper,hi(1/(aq(b)*arb(1).exp())))
        return aq(lower).union(aq(upper))
    def image(left,right):
        mid=(left+right)/2;u=aq(left).union(aq(right));v=aq(mid);rp=aq(T)+u;rm=aq(T)-u;mp=aq(T+mid);mm=aq(T-mid)
        boundary_mid=A0+F(mp)+F(mm);moment=arb(0);derivative_moment=arb(0)
        for k in range(M):
            b=Q(4*k+1,2);b2=aq(b*b)
            moment+=((1-(1+aq(b)*mp)*(-aq(b)*mp).exp())-(1-(1+aq(b)*mm)*(-aq(b)*mm).exp()))/b2
            derivative_moment+=moment_range(T-right,T-left,b)+moment_range(T+left,T+right,b)
        base=[c0*boundary_mid+(v/2).cosh()*2*hc,c1*(v*boundary_mid+moment)-(v/2).sinh()*2*hs]
        boundary=A0+F(rp)+F(rm);db=kernel(rm)-kernel(rp)
        derivative=[c0*db+(u/2).sinh()*hc,c1*(boundary+u*db+derivative_moment)-(u/2).cosh()*hs]
        ambiguous=[arb(0),arb(0)]
        for _,log,coefficient in terms:
            for shift in [log,-log]:
                yl=left-hi(shift);yh=right-lo(shift)
                if yh < -T or yl > T:continue
                if yl >= -T and yh <= T:
                    base[0]-=coefficient*c0;base[1]-=coefficient*c1*(v-shift);derivative[1]-=coefficient*c1
                else:
                    y=u-shift;ambiguous[0]-=coefficient*c0.union(arb(0));ambiguous[1]-=coefficient*(c1*y).union(arb(0))
        offset=aq(left-mid).union(aq(right-mid))
        return [base[j]+offset*derivative[j]+ambiguous[j] for j in range(2)]
    expected_edges={Q(0),T-delta}
    for level in range(32):
        a=delta*(1<<level)
        for index in range(65):expected_edges.add(T-a-a*Q(index,64))
    breakpoints=[];scale=1<<96
    for m,log,_ in terms:
        v=abs(log-aq(T));left=Q((lo(v)*scale).__floor__(),scale);right=Q((hi(v)*scale).__ceil__(),scale);breakpoints.append({'m':m,'lower':str(left),'upper':str(right)})
        expected_edges.update(x for x in [left,right] if 0<x<T-delta)
    require(packet['breakpoint_bounds']==breakpoints,'unqualified arithmetic breakpoint enclosure')
    expected_edges=sorted(expected_edges);cells=packet['positive_half_cells'];require(len(cells)==len(expected_edges)-1,'source coverage count defect')
    E=[Q(0),Q(0)];norm=[Q(0),Q(0)];mean=[Q(0),Q(0)]
    for row,left,right in zip(cells,expected_edges[:-1],expected_edges[1:],strict=True):
        require(rat(row['left'])==left and rat(row['right'])==right,'source cell gap/overlap/endpoint defect')
        require(len(row['coefficients'])==2,'missing parity column');q=[rat(x) for x in row['coefficients']];require(all((x*(1<<48)).denominator==1 for x in q),'coefficient grid defect')
        values=image(left,right);width=right-left
        for j in range(2):
            error=max(abs(lo(values[j])-q[j]),abs(hi(values[j])-q[j]));E[j]+=2*width*error*error;norm[j]+=2*width*q[j]*q[j]
            mean[j]+=2*width*q[j] if j==0 else q[j]*(right*right-left*left)
    BL=arb(2).log()+aq(L)/4+pi/4;ell=aq(1/delta).log();P=[c0,c1*aq(T)];D=[arb(0),c1];accepted=[];fresh_errors=[];variations=[]
    for j in range(2):
        V=2*P[j]*sum((x[2] for x in terms),arb(0))+(2*(aq(T)/2).cosh()*abs(hc) if j==0 else 2*(aq(T)/2).sinh()*abs(hs))
        a=P[j]/2;b=P[j]*(abs(A0)+BL+F(aq(L)/2))+D[j]*aq(L)*(3*aq(L)/2).exp()+V
        cap=2*aq(delta)*(a*a*(ell*ell+2*ell+2)+2*a*b*(ell+1)+b*b)
        residual=2*D[j]/(4*M-3);fresh=hi(cap+(aq(E[j]).sqrt()+aq(L).sqrt()*residual)**2);claimed=rat(packet['error_bounds'][j]['published_L2_squared_upper'])
        require(fresh<=claimed,'understated complete L2 source error')
        require(claimed/Q(1,65536)==int(claimed/Q(1,65536)),'squared error publication grid defect')
        raw_source=rat(packet['error_bounds'][j]['raw_total_squared_upper']);require(Q(1,65536)-Q(1,1<<96)<=claimed-raw_source<=Q(2,65536),'squared error publication reserve defect')
        qualifies=claimed<=Q(1,16)**2;require(packet['error_bounds'][j]['accuracy_qualified']==qualifies,'false per-column accuracy label')
        accepted.append(claimed);fresh_errors.append(str(fresh))
        coeff=[rat(row['coefficients'][j]) for row in cells];var=2*(abs(coeff[-1])+sum((abs(b-a) for a,b in zip(coeff,coeff[1:])),Q(0)))+(2*abs(coeff[0]) if j else 0);variations.append(var)
    require([str(x) for x in norm]==packet['approximant_L2_squared'],'wrong supported model norm')
    require([str(x) for x in variations]==packet['approximant_total_variation'],'understated model variation')
    total_var=sum((x*x for x in variations),Q(0));U=Q(256);target=Q(1,16)
    def weight(t):
        A=acb(aq(Q(1,4)),aq(t)/2).digamma().real-pi.log();g=A-aq(alpha)*(A-A0+1)-aq(beta)
        return max(floor,lo(g)),max(floor,hi(g))
    for index,row in enumerate(packet['fourier_tail_ladder']):
        require(rat(row['U'])==U,'Fourier tail ladder is not the declared doubling sequence');wl,wh=weight(U)
        require(0<rat(row['h_lower'])<=wl<=wh<=rat(row['h_upper']),'dishonest positive frequency weight')
        fresh=hi(aq(total_var)/(pi*aq(U)*aq(rat(row['h_lower']))));upper=rat(row['complete_gram_tail_upper']);require(fresh<=upper,'understated complete Fourier tail')
        require((upper<=target)==(index==len(packet['fourier_tail_ladder'])-1),'tail ladder terminal policy changed');U*=2
    require(packet['fourier_tail_ladder'],'missing full frequency tail')
    require([row['t'] for row in packet['fourier_controls']]==['0','4','256'],'changed Fourier controls')
    for row in packet['fourier_controls']:
        t=rat(row['t']);values=[arb(0),arb(0)]
        for cell in cells:
            left=rat(cell['left']);right=rat(cell['right']);q=[rat(x) for x in cell['coefficients']]
            if t==0:values[0]+=aq(2*q[0]*(right-left));continue
            values[0]+=2*aq(q[0])*((aq(t*right)).sin()-(aq(t*left)).sin())/aq(t)
            values[1]+=2*aq(q[1])*((aq(t*right)).cos()-(aq(t*left)).cos())/aq(t)
        wl,wh=weight(t);require(rat(row['h_lower'])<=wl<=wh<=rat(row['h_upper']),'dishonest control weight')
        for j,key in enumerate(['even_real','odd_imaginary']):
            contain(row[key]['approximant'],lo(values[j]),hi(values[j]),'Fourier model control')
            error=aq(L*accepted[j]).sqrt();contain(row[key]['full_source'],lo(values[j]-error),hi(values[j]+error),'full Fourier source completion')
    diag=[aq(mean[0])*c0,aq(mean[1])*c1]
    for j,row in enumerate(packet['physical_low_diagonal_controls']):
        contain(row['approximant'],lo(diag[j]),hi(diag[j]),'physical low model moment');error=aq(accepted[j]).sqrt();contain(row['full_source'],lo(diag[j]-error),hi(diag[j]+error),'physical low source completion')
    # Independent full constant entry from the positive Fourier-resolvent series.
    arch=A0
    for k in range(128):
        a=Q(k)+Q(1,4);arch+=(1-(-4*aq(T*a)).exp())/aq(4*T*a*a)
    physical=arch+8*((aq(T)).exp()+(-aq(T)).exp()-2)/aq(L)-2*sum((co*(1-log/aq(L)) for _,log,co in terms),arb(0))
    physical_lower=lo(physical);physical_upper=hi(physical)+Q(1,4*T*(Q(128)-Q(3,4)))
    contain(packet['physical_low_diagonal_controls'][0]['full_source'],physical_lower,physical_upper,'independent full constant entry')
    model=[Q(3,5),Q(4,5)];error=[Q(3,50),Q(4,50)];actual=sum(((x+y)**2 for x,y in zip(model,error,strict=True)),Q(0));require(actual==Q(121,100),'exact error geometry defect')
    require(packet['exact_error_controls']=={'mixed_term_majorant':'121/100','nominal_acceptance_complete_lowers':['0','1/50']},'exact one-sided error control mismatch')
    qualified=all(x<=Q(1,16)**2 for x in accepted);require(packet['status']==('SOURCE_ACCURACY_QUALIFIED' if qualified else 'SOURCE_ACCURACY_UNRESOLVED'),'false overall source accuracy status')
    require(packet['full_weighted_gram_computed'] is False and packet['new_full_positivity_or_support'] is False and packet['usefulness_assessed'] is False,'scope escalation')
    modules={}
    for name,module in sorted(sys.modules.items()):
        if (name=='scripts' or name.startswith('scripts.')) and getattr(module,'__file__',None):
            file=Path(module.__file__).resolve();require(file.is_relative_to(ROOT),'project import escaped source root');modules[file.relative_to(ROOT).as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest()
    return {'format':'research-supported-source-audit-v1','status':'PASS_SOURCE_AND_ACCURACY' if qualified else 'PASS_SOURCE_BOUNDS_TARGET_UNRESOLVED','source_variant':version,
            'source_sha256':hashlib.sha256(raw).hexdigest(),'audit_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'audit_precision_bits':512,
            'complete_positive_half_cells_checked':len(cells),'independent_complete_L2_squared_uppers':fresh_errors,'accepted_L2_squared_uppers':[str(x) for x in accepted],
            'finite_column_operator_error_squared':str(sum(accepted,Q(0))),'complete_fourier_tail_upper':packet['fourier_tail_ladder'][-1]['complete_gram_tail_upper'],
            'complete_fourier_tail_U':packet['fourier_tail_ladder'][-1]['U'],'independent_constant_entry':{'lower':str(physical_lower),'upper':str(physical_upper)},
            'organization':'Log-form F, incomplete moments, unimodal direct derivative sum, manual strict arithmetic and endpoint Fourier integrals; producer not imported.',
            'imported_project_modules':modules,'full_weighted_gram_or_new_positivity':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    try:result=audit(args.source)
    except (ValueError,KeyError,TypeError,AssertionError) as exc:print('REJECT: '+str(exc),file=sys.stderr);raise SystemExit(2)
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:json.dump(result,handle,indent=2);handle.write('\n')
    print(json.dumps({'status':result['status'],'source_variant':result['source_variant'],'complete_cells_checked':result['complete_positive_half_cells_checked'],'finite_column_operator_error_squared':result['finite_column_operator_error_squared']}))


if __name__=='__main__':main()
