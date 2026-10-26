"""Complete fixed supported coupling comparison. Research only, no theorem admission."""
from __future__ import annotations
import argparse, gzip, hashlib, json, math, sys
from pathlib import Path
from fractions import Fraction as Q
from flint import arb, acb, ctx

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE_SHA='b3b3578d778c9d7af5127ba218dde7d124d8dcb47b7f826e98c8913282c3612c'
AUDIT_SHA='9da33ed4b3110da4906e3c40c2f81215e45ca9433bb7c051c5a610aff4b39925'
def a(x):
    x=Q(x);return arb(x.numerator)/x.denominator
def ends(x):return Q(str(x.lower().fmpq())),Q(str(x.upper().fmpq()))
def pub(x):
    lo,hi=ends(x);s=1<<64
    return {'lower':str(Q(math.floor(lo*s)-1,s)),'upper':str(Q(math.ceil(hi*s)+1,s))}
def rad(x):
    lo,hi=ends(x);return max(abs(lo),abs(hi))
def integer(x,b):return math.floor(Q(str(x.mid().fmpq()))*(1<<b))
def legendre(x,n):
    out=[arb(1),x]
    for k in range(1,n):out.append(((2*k+1)*x*out[-1]-k*out[-2])/(k+1))
    return out[:n+1]
def clenshaw(c,x):
    b1=b2=arb(0)
    for n in range(len(c)-1,-1,-1):
        b0=c[n]+Q(2*n+1,n+1).numerator*x*b1/Q(2*n+1,n+1).denominator-a(Q(n+1,n+2))*b2
        b2,b1=b1,b0
    return b1

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise ValueError('fresh output required')
    inp=json.loads((HERE/'comparison-inputs-v1.json').read_text(encoding='utf-8'))
    if (inp['physical_uniform_cells'],inp['zero_padding'],inp['reference_N'],inp['degrees'])!=(65536,16,312,[0,1]):raise ValueError('unsupported fixed research case')
    raw=(ROOT/inp['qualified_source']).read_bytes();araw=(ROOT/inp['qualified_audit']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA or hashlib.sha256(araw).hexdigest()!=AUDIT_SHA:raise ValueError('qualified source identity')
    source=json.loads(raw);audit=json.loads(araw)
    if audit['source_sha256']!=SOURCE_SHA or source['reference_N']!=312:raise ValueError('source/audit binding')
    cells=[(Q(v['left']),Q(v['right']),list(map(Q,v['coefficients']))) for v in source['positive_half_cells']]
    if len(cells)!=2054 or cells[0][0]!=0 or any(cells[k][1]!=cells[k+1][0] for k in range(len(cells)-1)):raise ValueError('physical partition')
    T=Q(3,4);L=2*T;N=312;nt=65536;nh=nt//2;pad=16;M=nt*pad;d=L/nt;period=pad*L
    ctx.prec=512
    zn=[2*sum((r-l)*v[j]**2 for l,r,v in cells) for j in (0,1)]
    av=[[Q(0) for _ in range(nh)] for _ in (0,1)]
    pos=0
    for i in range(nh):
        left=i*d;right=left+d
        while pos<len(cells) and cells[pos][1]<=left:pos+=1
        k=pos
        while k<len(cells) and cells[k][0]<right:
            lo=max(left,cells[k][0]);hi=min(right,cells[k][1])
            if hi>lo:
                for j in (0,1):av[j][i]+=(hi-lo)*cells[k][2][j]/d
            k+=1
    ez2=[zn[j]-2*d*sum(v*v for v in av[j]) for j in (0,1)]
    assert all(v>=0 for v in ez2)
    # Integration by parts across exact step jumps. No normalized-mass shortcut.
    b=[[arb(0) for _ in range(N)] for _ in (0,1)]
    for j in (0,1):b[j][0]=a(2*sum((r-l)*v[j] for l,r,v in cells)/L) if j==0 else arb(0)
    edges=[(cells[0][0],[-cells[0][2][j] for j in (0,1)])]
    edges.extend((cells[k][1],[cells[k][2][j]-(cells[k+1][2][j] if k+1<len(cells) else 0) for j in (0,1)]) for k in range(len(cells)))
    for edge,jump in edges:
        pp=legendre(a(edge/T),N)
        for n in range(1,N):b[n%2][n]+=a(jump[n%2])*(pp[n+1]-pp[n-1])
    ci=[[integer(v,64) if n%2==j else 0 for n,v in enumerate(b[j])] for j in (0,1)]
    cc=[[Q(v,1<<64) for v in row] for row in ci]
    ep2=[sum(a(L/Q(2*n+1))*a(rad(b[j][n]-a(cc[j][n])))**2 for n in range(j,N,2)) for j in (0,1)]
    qn=[a(zn[j])-sum(a(L/Q(2*n+1))*b[j][n]**2 for n in range(j,N,2)) for j in (0,1)]
    deriv=[]
    for j in (0,1):
        suffix=sum(cc[j]);val=Q(0)
        for n,c in enumerate(cc[j]):
            suffix-=c;val+=n*(n+1)*(c*c+2*c*suffix)/T
        assert val>=0;deriv.append(val)
    qints=[[],[]];round2=[Q(0),Q(0)]
    ac=[[a(c) for c in row] for row in cc]
    for i in range(nh):
        x=a(((Q(i)+Q(1,2))*d)/T)
        for j in (0,1):
            value=a(av[j][i])-clenshaw(ac[j],x);q=integer(value,48)
            qints[j].append(q);round2[j]+=2*d*rad(value-a(Q(q,1<<48)))**2
    rows=[]
    for j in (0,1):
        es=a(audit['accepted_L2_squared_uppers'][j]).sqrt()
        delta=es+ep2[j].sqrt()+a(ez2[j]).sqrt()+a(d/2)*a(deriv[j]).sqrt()+a(round2[j]).sqrt()
        low=b[j][j]*a(L/Q(2*j+1)).sqrt()
        rows.append({'degree':j,'projection_coefficients_grid64':ci[j],'positive_uniform_coefficients_grid48':qints[j],'error_components':{'source':pub(es),'projection_rounding':pub(ep2[j].sqrt()),'uniform_Z':pub(a(ez2[j]).sqrt()),'polynomial_midpoints':pub(a(d/2)*a(deriv[j]).sqrt()),'uniform_rounding':pub(a(round2[j]).sqrt()),'complete_delta':pub(delta)},'projected_Z_norm_squared':pub(qn[j]),'polynomial_derivative_norm_squared':str(deriv[j]),'actual_low':pub(low+arb(0,a(ends(es)[1])))})
    ctx.prec=128
    pi=arb.pi();omega=2*pi/a(period);A0=(acb(a(Q(1,4))).digamma().real-pi.log());gamma=a(Q(3,4));beta=a(Q(873,1024));floor=a(Q(1,3))
    def weight(t):
        A=(acb(a(Q(1,4)),t/2).digamma().real-pi.log())
        g=gamma*(A-A0+1)-(1+beta-A0)
        if g>floor:return g
        if g<floor:return floor
        lo,hi=ends(g);return a((max(lo,Q(1,3))+max(hi,Q(1,3)))/2)+arb(0,a((max(hi,Q(1,3))-max(lo,Q(1,3)))/2))
    g128=gamma*((acb(a(Q(1,4)),arb(64)).digamma().real-pi.log())-A0+1)-(1+beta-A0)
    assert g128<floor
    K=integer(arb(16384)/omega,0);assert K*omega<16384 and (K+1)*omega>16384 and K<M//2
    w1=a(Q(27,500));w2=2*gamma**2*a(Q(1,125))**2/floor**3+gamma*a(Q(3,16000))/floor**2
    C=4*a(T)**2/floor+4*a(T)*w1+w2+a(L)*w1/pi
    weights=[1/weight(k*omega) for k in range(K+2)]
    for j,row in enumerate(rows):
        coeff=qints[j];full=[(-1 if j else 1)*v for v in reversed(coeff)]+coeff
        norm=d*sum(Q(v,1<<48)**2 for v in full)
        fft=acb.dft([acb(a(Q(v,1<<48))) for v in full]+[acb(0)]*(M-nt))
        weighted=arb(0);mass=arb(0);samples=[]
        for k in range(K+1):
            sinc=arb(1) if k==0 else (pi*k/M).sin()/(pi*k/M)
            energy=a(d)**2*sinc**2*(fft[k].real**2+fft[k].imag**2)
            mass+=(1 if k==0 else 2)*energy/a(period)
            weighted+=(1 if k==0 else 2)*energy*weights[k]/a(period)
            if k in (0,1,2,K):samples.append({'index':k,'sample_squared':pub(energy)})
        remaining=a(norm)-mass;assert ends(remaining)[0]>0
        tail=remaining*weights[K+1];quad=omega**2*C*a(norm)/8
        model_lo=max(Q(0),ends(weighted-quad)[0]);model_hi=ends(weighted+tail+quad)[1]
        delta=a(Q(row['error_components']['complete_delta']['upper']))
        gl=max(Q(0),ends(a(model_lo).sqrt()-delta/floor.sqrt())[0])**2
        gu=(a(model_hi).sqrt()+delta/floor.sqrt())**2
        eta=a(inp['eta_lower']);old=a(inp['old_true_Weil_tail_lower'])
        # Scalar comparator uses the original QZ and original source error only.
        old_u=(a(Q(row['projected_Z_norm_squared']['upper'])).sqrt()+a(audit['accepted_L2_squared_uppers'][j]).sqrt())**2/old
        new_u=gu/eta
        lower=a(Q(row['actual_low']['lower']))-new_u
        row.update({'uniform_norm_squared':str(norm),'weighted_prefix':pub(weighted),'unweighted_prefix':pub(mass),'full_infinite_grid_mass_remainder':pub(remaining),'weighted_infinite_grid_tail_upper':pub(tail),'full_continuum_quadrature_error_upper':pub(quad),'complete_model_weighted_norm':{'lower':str(model_lo),'upper':str(model_hi)},'actual_supported_weighted_norm':{'lower':str(gl),'upper':pub(gu)['upper']},'complete_supported_reference_penalty_upper':pub(new_u)['upper'],'matched_old_scalar_penalty_upper':pub(old_u)['upper'],'two_column_sufficient_diagonal_lower':pub(lower)['lower'],'samples':samples})
        del fft
    def charge2(n,m):return Q((2*n+1)*n*n*(n+1)*(n+1),1)/(T*T*(4*m-3)**2)
    n=311;low=1;hi=1
    while charge2(n,hi)>Q(1,256):hi*=2
    while low<hi:
        mid=(low+hi)//2
        if charge2(n,mid)<=Q(1,256):hi=mid
        else:low=mid+1
    result={'format':'research-supported-penalty-comparison-v1','status':'COMPLETE_TWO_COLUMN_COMPARISON','qualified_source_sha256':SOURCE_SHA,'qualified_audit_sha256':AUDIT_SHA,'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inputs_sha256':hashlib.sha256((HERE/'comparison-inputs-v1.json').read_bytes()).hexdigest(),'support':'3/4','reference_N':N,'physical_cells':nt,'fft_length':M,'frequency_prefix_K':K,'frequency_step':pub(omega),'g128':pub(g128),'quadrature_derivative_constant':pub(C),'columns':rows,'source_rule_work':{'degree3_M128_residual_charge_squared':str(charge2(3,128)),'degree311_M128_residual_charge_squared':str(charge2(311,128)),'degree311_minimum_M_for_individual_1_over_16':low,'minimum_verified_by_adjacent_integer':charge2(311,low)<=Q(1,256)<charge2(311,low-1),'scope':'Necessary only for the current uniform-derivative residual charge; not an actual-error or universal algorithm lower bound.'},'all_two_column_sufficient_diagonals_positive':all(Q(v['two_column_sufficient_diagonal_lower'])>0 for v in rows),'full312_source_or_schur_computed':False,'new_support_or_admission':False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('xb') as f:f.write(gzip.compress((json.dumps(result,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    print(json.dumps({k:result[k] for k in ('status','frequency_prefix_K','all_two_column_sufficient_diagonals_positive','source_rule_work')}))
if __name__=='__main__':
    try:main()
    except (AssertionError,ValueError,KeyError,ZeroDivisionError) as exc:print(type(exc).__name__+': '+str(exc),file=sys.stderr);raise SystemExit(2)
