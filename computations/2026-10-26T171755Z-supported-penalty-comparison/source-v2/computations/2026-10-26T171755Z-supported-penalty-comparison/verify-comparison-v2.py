"""Independent full comparison reconstruction; imports no producer/project code."""
from __future__ import annotations
import argparse,gzip,hashlib,json,math,sys
from fractions import Fraction as Q
from pathlib import Path
from flint import arb,acb,ctx
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
S='b3b3578d778c9d7af5127ba218dde7d124d8dcb47b7f826e98c8913282c3612c'
A='9da33ed4b3110da4906e3c40c2f81215e45ca9433bb7c051c5a610aff4b39925'
def ball(q):q=Q(q);return arb(q.numerator)/q.denominator
def endpoints(v):
    # Convert binary rationals directly. Do not round-trip large exact dyadics through decimal strings.
    lo,hi=v.lower().fmpq(),v.upper().fmpq()
    return Q(int(lo.numerator),int(lo.denominator)),Q(int(hi.numerator),int(hi.denominator))
def extent(v):lo,hi=endpoints(v);return max(abs(lo),abs(hi))
def checked(label,interval,value):
    lo,hi=endpoints(value)
    if not Q(interval['lower'])<=lo<=hi<=Q(interval['upper']):raise ValueError(label+' is not a full enclosure')
def upper_checked(label,upper,value):
    if endpoints(value)[1]>Q(upper):raise ValueError(label+' upper is too small')
def lower_checked(label,lower,value):
    if Q(lower)>endpoints(value)[0]:raise ValueError(label+' lower is too large')
def seq(x,N):
    p=[arb(1),x]
    for n in range(2,N+1):p.append(((2*n-1)*x*p[n-1]-(n-1)*p[n-2])/n)
    return p

def main():
    ap=argparse.ArgumentParser();ap.add_argument('packet',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise ValueError('fresh output required')
    packet_raw=args.packet.read_bytes();p=json.loads(gzip.decompress(packet_raw))
    decl_raw=(HERE/'comparison-inputs-v1.json').read_bytes();decl=json.loads(decl_raw)
    if (decl['support'],decl['reference_N'],decl['degrees'],decl['physical_uniform_cells'],decl['zero_padding'])!=('3/4',312,[0,1],65536,16):raise ValueError('declared case')
    eta=1-Q(9,10**49);old=Q(63,32)-Q(4,10**49)
    if Q(decl['eta_lower'])!=eta or Q(decl['old_true_Weil_tail_lower'])!=old:raise ValueError('reference constants')
    raw=(ROOT/decl['qualified_source']).read_bytes();audraw=(ROOT/decl['qualified_audit']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=S or hashlib.sha256(audraw).hexdigest()!=A:raise ValueError('upstream source identity')
    if p['qualified_source_sha256']!=S or p['qualified_audit_sha256']!=A or p['inputs_sha256']!=hashlib.sha256(decl_raw).hexdigest():raise ValueError('packet binding')
    if p['producer_sha256']!=hashlib.sha256((HERE/'compare-supported-v1.py').read_bytes()).hexdigest():raise ValueError('producer identity')
    if (p['format'],p['support'],p['reference_N'],p['physical_cells'],p['fft_length'],len(p['columns']))!=('research-supported-penalty-comparison-v1','3/4',312,65536,1048576,2):raise ValueError('research packet shape')
    if p['full312_source_or_schur_computed'] or p['new_support_or_admission']:raise ValueError('false scope')
    source=json.loads(raw);audit=json.loads(audraw);cells=[(Q(v['left']),Q(v['right']),list(map(Q,v['coefficients']))) for v in source['positive_half_cells']]
    T=Q(3,4);L=Q(3,2);N=312;nt=65536;nh=32768;M=1048576;step=L/nt;period=16*L
    ctx.prec=768
    norms=[2*sum((r-l)*v[j]**2 for l,r,v in cells) for j in (0,1)]
    # Independent full-cell integration, not the producer's step-jump summation.
    b=[[arb(0) for _ in range(N)] for j in (0,1)]
    prev=seq(ball(cells[0][0]/T),N)
    for left,right,v in cells:
        after=seq(ball(right/T),N)
        b[0][0]+=ball(2*(right-left)*v[0]/L)
        for n in range(1,N):
            j=n%2;b[j][n]+=ball(v[j])*((after[n+1]-after[n-1])-(prev[n+1]-prev[n-1]))
        prev=after
    cv=[];rproj=[];derivatives=[];uniform_average=[[Q(0) for i in range(nh)] for j in (0,1)]
    # Independent distribution of each source cell over overlapping time bins.
    for left,right,v in cells:
        first=int(left//step);last=min(nh-1,math.ceil(right/step)-1)
        for i in range(first,last+1):
            length=min(right,(i+1)*step)-max(left,i*step)
            if length>0:
                for j in (0,1):uniform_average[j][i]+=v[j]*length/step
    round_sq=[Q(0),Q(0)];projection_error=[];uniform_error=[]
    for j,row in enumerate(p['columns']):
        if row['degree']!=j or len(row['projection_coefficients_grid64'])!=N or len(row['positive_uniform_coefficients_grid48'])!=nh:raise ValueError('column degree or extent')
        c=[Q(v,1<<64) for v in row['projection_coefficients_grid64']]
        if any(c[n] for n in range(N) if n%2!=j):raise ValueError('projection parity')
        cv.append(c)
        en=sum(ball(L/Q(2*n+1))*ball(extent(b[j][n]-ball(c[n])))**2 for n in range(j,N,2))
        projection_error.append(en.sqrt())
        qn=ball(norms[j])-sum(ball(L/Q(2*n+1))*b[j][n]**2 for n in range(j,N,2));rproj.append(qn)
        checked('projected full source norm',row['projected_Z_norm_squared'],qn)
        epsz=norms[j]-2*step*sum(x*x for x in uniform_average[j]);assert epsz>=0
        uniform_error.append(ball(epsz).sqrt())
        # Direct positive squares of the derivative expansion in orthogonal P_k.
        dc=[]
        for k in range(N-1):dc.append(Q(2*k+1,T)*sum(c[n] for n in range(k+1,N,2)))
        dn=sum(T*Q(2,2*k+1)*dc[k]**2 for k in range(N-1))
        if Q(row['polynomial_derivative_norm_squared'])!=dn:raise ValueError('physical derivative Gram')
        derivatives.append(dn)
        low=b[j][j]*ball(L/Q(2*j+1)).sqrt();es=ball(audit['accepted_L2_squared_uppers'][j]).sqrt()
        lower_checked('actual low',row['actual_low']['lower'],low-ball(endpoints(es)[1]))
        upper_checked('actual low',row['actual_low']['upper'],low+ball(endpoints(es)[1]))
    ac=[[ball(c) for c in row] for row in cv]
    # Forward Legendre values, not producer Clenshaw.
    for i in range(nh):
        values=seq(ball((Q(i)+Q(1,2))*step/T),N-1)
        for j,row in enumerate(p['columns']):
            poly=sum(ac[j][n]*values[n] for n in range(j,N,2));q=Q(row['positive_uniform_coefficients_grid48'][i],1<<48)
            round_sq[j]+=2*step*extent(ball(uniform_average[j][i])-poly-ball(q))**2
    del uniform_average
    for j,row in enumerate(p['columns']):
        components={'source':ball(audit['accepted_L2_squared_uppers'][j]).sqrt(),'projection_rounding':projection_error[j],'uniform_Z':uniform_error[j],'polynomial_midpoints':ball(step/2)*ball(derivatives[j]).sqrt(),'uniform_rounding':ball(round_sq[j]).sqrt()}
        for name,value in components.items():checked(name,row['error_components'][name],value)
        checked('total supported-source error',row['error_components']['complete_delta'],sum(components.values()))
    ctx.prec=192;pi=arb.pi();omega=pi/12;A0=acb(ball(Q(1,4))).digamma().real-pi.log();gamma=ball(Q(3,4));floor=ball(Q(1,3))
    def invweight(t):
        arch=acb(ball(Q(1,4)),t/2).digamma().real-pi.log()
        g=gamma*arch+ball(Q(1,4))*A0-ball(Q(1,4))-ball(Q(873,1024))
        if g<floor:return 1/floor
        if g>floor:return 1/g
        lo,hi=endpoints(g);return 1/(ball((max(lo,Q(1,3))+max(hi,Q(1,3)))/2)+arb(0,ball((max(hi,Q(1,3))-max(lo,Q(1,3)))/2)))
    g128=gamma*(acb(ball(Q(1,4)),arb(64)).digamma().real-pi.log())+ball(Q(1,4))*A0-ball(Q(1,4))-ball(Q(873,1024))
    if not g128<floor:raise ValueError('weight kink location')
    checked('kink location',p['g128'],g128);checked('frequency spacing',p['frequency_step'],omega)
    K=p['frequency_prefix_K']
    if not K*omega<16384<(K+1)*omega or not 0<K<M//2:raise ValueError('complete frequency prefix')
    C=ball(Q(55321677,8000000))+ball(Q(81,1000))/pi
    checked('distributional derivative charge',p['quadrature_derivative_constant'],C)
    inverse_weights=[invweight(k*omega) for k in range(K+2)]
    summaries=[]
    for j,row in enumerate(p['columns']):
        half=row['positive_uniform_coefficients_grid48'];q=[Q(((-1)**j)*v,1<<48) for v in reversed(half)]+[Q(v,1<<48) for v in half]
        norm=step*sum(v*v for v in q)
        if Q(row['uniform_norm_squared'])!=norm:raise ValueError('exact complete uniform norm')
        fourier=acb.dft([acb(ball(v)) for v in q]+[acb(0)]*(M-nt))
        mw=arb(0);mm=arb(0)
        for k in range(K+1):
            factor=ball(step) if k==0 else 2*(omega*k*ball(step)/2).sin()/(omega*k)
            e=factor**2*(fourier[k].real**2+fourier[k].imag**2)
            mm+=e*(1 if k==0 else 2)/24;mw+=e*inverse_weights[k]*(1 if k==0 else 2)/24
        checked('full weighted prefix',row['weighted_prefix'],mw);checked('full unweighted prefix',row['unweighted_prefix'],mm)
        remainder=ball(norm)-mm;assert endpoints(remainder)[0]>0
        tail=remainder*inverse_weights[K+1];quad=omega**2*C*ball(norm)/8
        checked('all omitted alias mass',row['full_infinite_grid_mass_remainder'],remainder)
        checked('all weighted infinite aliases',row['weighted_infinite_grid_tail_upper'],tail)
        checked('continuum and kink error',row['full_continuum_quadrature_error_upper'],quad)
        lower_checked('model integral',row['complete_model_weighted_norm']['lower'],mw-quad)
        upper_checked('model integral',row['complete_model_weighted_norm']['upper'],mw+tail+quad)
        # Four independent direct exponential sums, with exact physical cell phases.
        for sample in row['samples']:
            k=sample['index'];t=omega*k
            if k not in (0,1,2,K):raise ValueError('sample identity')
            if k==0:direct=acb(ball(step*sum(q)))
            else:
                phase=acb(0,-t*ball(-T+step/2)).exp();ratio=acb(0,-t*ball(step)).exp();s=acb(0)
                for value in q:s+=ball(value)*phase;phase*=ratio
                direct=s*(2*(t*ball(step)/2).sin()/t)
            checked('independent direct step transform',sample['sample_squared'],direct.real**2+direct.imag**2)
        delta=ball(row['error_components']['complete_delta']['upper'])
        ml=Q(row['complete_model_weighted_norm']['lower']);mu=Q(row['complete_model_weighted_norm']['upper'])
        gl=max(Q(0),endpoints(ball(max(0,ml)).sqrt()-delta/floor.sqrt())[0])**2
        gu=(ball(mu).sqrt()+delta/floor.sqrt())**2
        if Q(row['actual_supported_weighted_norm']['lower'])>gl:raise ValueError('actual weighted lower')
        upper_checked('actual weighted upper',row['actual_supported_weighted_norm']['upper'],gu)
        new=gu/ball(eta)
        old_bound=(ball(row['projected_Z_norm_squared']['upper']).sqrt()+ball(audit['accepted_L2_squared_uppers'][j]).sqrt())**2/ball(old)
        upper_checked('new reference penalty',row['complete_supported_reference_penalty_upper'],new)
        upper_checked('old matched scalar penalty',row['matched_old_scalar_penalty_upper'],old_bound)
        lower_checked('compressed sufficient diagonal',row['two_column_sufficient_diagonal_lower'],ball(row['actual_low']['lower'])-new)
        summaries.append({'degree':j,'all_uniform_bins_checked':nh,'all_frequency_prefix_samples_checked':K+1,'independent_direct_transform_controls':len(row['samples']),'supported_penalty_upper':row['complete_supported_reference_penalty_upper'],'matched_scalar_penalty_upper':row['matched_old_scalar_penalty_upper'],'compressed_diagonal_lower':row['two_column_sufficient_diagonal_lower']})
        del fourier
    work=p['source_rule_work']
    def r2(n,m):return Q((2*n+1)*n*n*(n+1)*(n+1),1)/(T*T*(4*m-3)**2)
    if Q(work['degree3_M128_residual_charge_squared'])!=r2(3,128) or Q(work['degree311_M128_residual_charge_squared'])!=r2(311,128):raise ValueError('source work charge')
    m=work['degree311_minimum_M_for_individual_1_over_16']
    if not r2(311,m)<=Q(1,256)<r2(311,m-1) or not work['minimum_verified_by_adjacent_integer']:raise ValueError('necessary residual-term integer')
    pos=all(Q(x['two_column_sufficient_diagonal_lower'])>0 for x in p['columns'])
    if p['all_two_column_sufficient_diagonals_positive']!=pos:raise ValueError('compression sign scope')
    out={'format':'independent-supported-penalty-audit-v1','status':'PASS_COMPLETE_TWO_COLUMN_COMPARISON','source_packet_sha256':hashlib.sha256(packet_raw).hexdigest(),'audit_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'projection_precision_bits':768,'transform_precision_bits':192,'columns':summaries,'all_aliases_and_continuum_kinks_paid':True,'necessary_M311':m,'all_two_column_sufficient_diagonals_positive':pos,'full312_source_or_schur_computed':False,'upstream_supported_action_reused_not_freshly_rebuilt':True}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps(out))
if __name__=='__main__':
    try:main()
    except (ValueError,AssertionError,KeyError,ZeroDivisionError) as exc:print(type(exc).__name__+': '+str(exc),file=sys.stderr);raise SystemExit(2)
