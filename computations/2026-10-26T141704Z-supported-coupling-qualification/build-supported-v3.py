"""Fixed two-column supported source qualification, not a positivity generator."""
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
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms


def aq(x):
    x=Q(x);return arb(x.numerator)/x.denominator


def lo(x):return arb_to_rational_enclosure(x)[0]
def hi(x):return arb_to_rational_enclosure(x)[1]
def bounds(x):return {"lower":str(lo(x)),"upper":str(hi(x))}

def upward(x,bits=96):
    scale=1<<bits;return Q((hi(x)*scale).__ceil__(),scale)


def build(inputs):
    raw=inputs.read_bytes();pins=json.loads(raw)
    if (pins['format'],pins['support'],pins['degrees'],pins['residual_terms'],pins['source_precision_bits'])!=('supported-coupling-qualification-inputs-v3','3/4',[0,1],128,384):
        raise ValueError('changed fixed qualification')
    ctx.prec=384;T=Q(3,4);L=2*T;M=128;sub=pins['graded_subcells_per_doubling'];cap_power=pins['cap_relative_to_T_power'];delta=T/(1<<cap_power)
    assert (sub,cap_power,pins['coefficient_bits'],pins['arithmetic_breakpoint_bits'])==(64,32,48,96)
    pi=arb.pi();A0=aq(Q(1,4)).digamma()-pi.log();rootL=aq(L).sqrt();c0=1/rootL;c1=(3/aq(L)).sqrt()/aq(T)
    P=[c0,c1*aq(T)];D=[arb(0),c1]
    terms=enumerate_active_prime_power_terms(3,4,prec=384)
    assert [x.m for x in terms]==[2,3,4]
    hc=4*(aq(T)/2).sinh()/rootL
    hs=c1*(4*aq(T)*(aq(T)/2).cosh()-8*(aq(T)/2).sinh())
    assert lo(hs)>0
    rates=[(aq(Q(4*k+1,2)),aq(Q(4*k+1,2)**2)) for k in range(M)]
    def F(r):
        assert lo(r)>0
        z=(-r/2).exp();return z.atanh()+z.atan()
    def smooth(u):
        rp=aq(T)+u;rm=aq(T)-u;boundary=A0+F(rp)+F(rm)
        residual=arb(0)
        for b,b2 in rates:
            residual+=((1+b*rm)*(-b*rm).exp()-(1+b*rp)*(-b*rp).exp())/b2
        return [c0*boundary+2*(u/2).cosh()*hc,
                c1*(u*boundary+residual)-2*(u/2).sinh()*hs]
    def image(left,right):
        u=aq(left).union(aq(right));lower,upper=left,right;mid=(left+right)/2
        midpoint=aq(mid);offset=aq(lower-mid).union(aq(upper-mid));base=smooth(midpoint)
        rp=aq(T)+u;rm=aq(T)-u
        def kernel(r):return (-r/2).exp()/(1-(-2*r).exp())
        kp=kernel(rp);km=kernel(rm);boundary=A0+F(rp)+F(rm);derivative_boundary=km-kp
        derivative=[c0*derivative_boundary+(u/2).sinh()*hc,
                    c1*(boundary+u*derivative_boundary+rm*km*(1-(-2*M*rm).exp())+rp*kp*(1-(-2*M*rp).exp()))-(u/2).cosh()*hs]
        ambiguous=[arb(0),arb(0)]
        for term in terms:
            for shift in [term.log_m,-term.log_m]:
                y=u-shift;shift_lower,shift_upper=arb_to_rational_enclosure(shift)
                yl,yh=left-shift_upper,right-shift_lower
                if yh < -T or yl > T:continue
                if yl >= -T and yh <= T:
                    base[0]-=term.coefficient*c0;base[1]-=term.coefficient*c1*(midpoint-shift)
                    derivative[1]-=term.coefficient*c1
                else:
                    ambiguous[0]-=term.coefficient*c0.union(arb(0))
                    ambiguous[1]-=term.coefficient*(c1*y).union(arb(0))
        return [base[j]+offset*derivative[j]+ambiguous[j] for j in range(2)]
    edges={Q(0),T-delta}
    for level in range(cap_power):
        a=delta*(1<<level);b=2*a
        for index in range(sub+1):edges.add(T-a-(b-a)*Q(index,sub))
    breakpoint_bounds=[];scale=1<<pins['arithmetic_breakpoint_bits']
    for term in terms:
        value=abs(term.log_m-aq(T));left=Q((lo(value)*scale).__floor__(),scale);right=Q((hi(value)*scale).__ceil__(),scale)
        breakpoint_bounds.append({'m':term.m,'lower':str(left),'upper':str(right)})
        for edge in [left,right]:
            if 0<edge<T-delta:edges.add(edge)
    edges=sorted(edges);cells=[];cell_error=[Q(0),Q(0)];norm=[Q(0),Q(0)];mean=[Q(0),Q(0)]
    for left,right in zip(edges,edges[1:]):
        assert left<right
        values=image(left,right);coeff=[];width=right-left
        for j,value in enumerate(values):
            lower,upper=arb_to_rational_enclosure(value);mid=(lower+upper)/2;scale=1<<pins['coefficient_bits'];q=Q((mid*scale+Q(1,2)).__floor__(),scale)
            error=max(abs(lower-q),abs(upper-q));cell_error[j]+=2*width*error*error;norm[j]+=2*width*q*q
            mean[j]+=2*width*q if j==0 else q*(right*right-left*left)
            coeff.append(str(q))
        cells.append({'left':str(left),'right':str(right),'coefficients':coeff})
    B_L=arb(2).log()+aq(L)/4+pi/4;ell=aq(1/delta).log();error_rows=[];variation=[]
    for j in range(2):
        V=2*P[j]*sum((term.coefficient for term in terms),arb(0))
        V+=2*(aq(T)/2).cosh()*abs(hc) if j==0 else 2*(aq(T)/2).sinh()*abs(hs)
        a=P[j]/2;b=P[j]*(abs(A0)+B_L+F(aq(L)/2))+D[j]*aq(L)*(3*aq(L)/2).exp()+V
        cap=2*aq(delta)*(a*a*(ell*ell+2*ell+2)+2*a*b*(ell+1)+b*b)
        residual=2*D[j]/(4*M-3)
        raw_error=cap+(aq(cell_error[j]).sqrt()+aq(L).sqrt()*residual)**2
        grid=Q(pins['squared_error_publication_grid']);published=Q((hi(raw_error)/grid).__ceil__()+1)*grid
        error_rows.append({'degree':j,'cap_squared_upper':str(upward(cap)),'full_cell_squared_upper':str(cell_error[j]),
                           'uniform_residual_upper':str(upward(residual)),'raw_total_squared_upper':str(upward(raw_error)),
                           'published_L2_squared_upper':str(published),'accuracy_qualified':published<=Q(pins['individual_L2_accuracy'])**2})
        coeff=[Q(row['coefficients'][j]) for row in cells]
        var=2*(abs(coeff[-1])+sum((abs(b-a) for a,b in zip(coeff,coeff[1:])),Q(0)))
        if j==1:var+=2*abs(coeff[0])
        variation.append(var)
    total_variation_squared=sum((v*v for v in variation),Q(0));tail_rows=[];anchor=Q(pins['fourier_tail_anchor_start'])
    alpha=Q(pins['alpha']);beta=Q(pins['beta']);floor=Q(pins['m'])
    def h_bounds(t):
        A=acb(aq(Q(1,4)),aq(t)/2).digamma().real-pi.log();g=A-aq(alpha)*(A-A0+1)-aq(beta)
        return max(floor,lo(g)),max(floor,hi(g))
    while True:
        h_lower,h_upper=h_bounds(anchor);tail=aq(total_variation_squared)/(pi*aq(anchor)*aq(h_lower));upper=upward(tail)
        tail_rows.append({'U':str(anchor),'h_lower':str(h_lower),'h_upper':str(h_upper),'complete_gram_tail_upper':str(upper)})
        if upper<=Q(pins['fourier_gram_tail_target']):break
        anchor*=2
    fourier=[]
    for text in pins['fourier_control_frequencies']:
        t=Q(text);values=[arb(0),arb(0)]
        for row in cells:
            left=Q(row['left']);right=Q(row['right']);width=right-left;mid=(left+right)/2;x=aq(t*width/2)
            sinc=arb(1) if t==0 else x.sin()/x
            values[0]+=2*aq(Q(row['coefficients'][0])*width)*aq(t*mid).cos()*sinc
            values[1]-=2*aq(Q(row['coefficients'][1])*width)*aq(t*mid).sin()*sinc
        sources=[]
        for j,value in enumerate(values):
            error=aq(L*Q(error_rows[j]['published_L2_squared_upper'])).sqrt()
            sources.append({'approximant':bounds(value),'full_source':{'lower':str(lo(value-error)),'upper':str(hi(value+error))}})
        h_lower,h_upper=h_bounds(t)
        fourier.append({'t':text,'even_real':sources[0],'odd_imaginary':sources[1],'h_lower':str(h_lower),'h_upper':str(h_upper)})
    diagonal=[aq(mean[0])*c0,aq(mean[1])*c1]
    source_diagonal=[]
    for j,value in enumerate(diagonal):
        err=aq(Q(error_rows[j]['published_L2_squared_upper'])).sqrt()
        source_diagonal.append({'degree':j,'approximant':bounds(value),'full_source':{'lower':str(lo(value-err)),'upper':str(hi(value+err))}})
    # Exact non-Weil error-completion control, including its indispensable mixed term.
    aerr=Q(1,10);actual=Q(121,100);majorant=1+2*aerr+aerr*aerr
    assert actual==majorant and actual>1+aerr*aerr
    gates=[value-majorant-Q(1,20) for value in [Q(63,50),Q(32,25)]]
    assert gates==[Q(0),Q(1,50)]
    modules={}
    for name,module in sorted(sys.modules.items()):
        if (name=='scripts' or name.startswith('scripts.')) and getattr(module,'__file__',None):
            path=Path(module.__file__).resolve()
            if not path.is_relative_to(ROOT):raise RuntimeError('project import escaped source root')
            modules[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    return {'format':'research-supported-coupling-qualification-v3','status':'SOURCE_ACCURACY_QUALIFIED' if all(row['accuracy_qualified'] for row in error_rows) else 'SOURCE_ACCURACY_UNRESOLVED',
            'support':str(T),'degrees':[0,1],'reference_N':312,'source_precision_bits':384,'residual_terms':M,'cap_width':str(delta),
            'breakpoint_bounds':breakpoint_bounds,'positive_half_cells':cells,'error_bounds':error_rows,'approximant_L2_squared':[str(x) for x in norm],
            'approximant_total_variation':[str(x) for x in variation],'fourier_tail_ladder':tail_rows,'fourier_controls':fourier,
            'physical_low_diagonal_controls':source_diagonal,'exact_error_controls':{'mixed_term_majorant':str(majorant),'nominal_acceptance_complete_lowers':[str(x) for x in gates]},
            'full_weighted_gram_computed':False,'new_full_positivity_or_support':False,'usefulness_assessed':False,
            'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inputs_sha256':hashlib.sha256(raw).hexdigest(),'imported_project_modules':modules}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--inputs',type=Path,default=Path(__file__).with_name('qualification-inputs-v3.json'));parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=build(args.inputs)
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:json.dump(result,handle,indent=2);handle.write('\n')
    print(json.dumps({'status':result['status'],'positive_half_cells':len(result['positive_half_cells']),'L2_squared_uppers':[r['published_L2_squared_upper'] for r in result['error_bounds']],
                      'complete_fourier_tail_U':result['fourier_tail_ladder'][-1]['U'],'full_weighted_gram_computed':False}))


if __name__=='__main__':main()
