import json,time
from fractions import Fraction as Q
from flint import arb,ctx
from scripts.cert.legendre_schur import legendre_polynomials,potential_moment,potential_square_moment
from scripts.cert.mixed_gram_research import logarithmic_cell_moments
from scripts.verify_combined_schur_analytic_entries import qarb,endpoints,cell_v_moments,global_v_moments
start=time.perf_counter();basis=legendre_polynomials(25)
def mul(a,b):
 out=[Q() for _ in range(len(a)+len(b)-1)]
 for i,x in enumerate(a):
  for j,y in enumerate(b):out[i+j]+=x*y
 return out
def integ(p,a,b):return sum((c*(b**(i+1)-a**(i+1))/(i+1) for i,c in enumerate(p)),Q())
def val(p,x):return sum((c*x**i for i,c in enumerate(p)),Q())
def deriv(p):return [i*p[i] for i in range(1,len(p))] or [Q()]
bs=list(map(Q,['-3/4','-1/2','1/2','3/4']));sigma_checks=0
for b in bs:
 for k in range(1,25):
  direct=integ(basis[k],b,Q(1))-(1-b)*integ(basis[k],Q(-1),Q(1))/2
  assert direct==(val(basis[k-1],b)-val(basis[k+1],b))/(2*k+1)
  sigma_checks+=1
partition=[Q(-1),*bs,Q(1)]
for a in bs:
 for b in bs:
  direct=Q()
  for lo,hi in zip(partition[:-1],partition[1:]):
   mid=(lo+hi)/2;ca=Q(mid>a)-(1-a)/2;cb=Q(mid>b)-(1-b)/2
   direct+=(hi-lo)*ca*cb
  assert direct==(1+min(a,b))*(1-max(a,b))/2
cells=[(Q(-1),Q(-1,2)),(Q(-1,2),Q(1,2)),(Q(1,2),Q(1))]
p={'q':[[Q(-3),Q(-2)],[Q()],[Q(3),Q(-2)]],'s':[[Q(-2)],[Q()],[Q(2)]],'r':[[Q(-1),Q(-2)],[Q()],[Q(1),Q(-2)]]}
for i,(_,b) in enumerate(cells[:-1]):assert val(p['r'][i],b)==val(p['r'][i+1],b)
for i in range(3):
 for x in [cells[i][0],sum(cells[i],Q())/2,cells[i][1]]:
  assert val(p['q'][i],x)==val(p['s'][i],x)+val(p['r'][i],x)
def inner(a,b):return sum((integ(mul(x,y),lo,hi) for (lo,hi),x,y in zip(cells,p[a],p[b])),Q())
whole={n:inner(n,n) for n in p};cross=inner('s','r')
Dr=sum((integ(mul(mul(deriv(poly),deriv(poly)),[Q(1),Q(),Q(-1)]),lo,hi) for (lo,hi),poly in zip(cells,p['r'])),Q())
assert (whole['q'],whole['s'],whole['r'],cross,Dr)==(Q(7,3),Q(4),Q(1,3),Q(-1),Q(5,3))
raw={n:[sum((integ(mul(basis[k],poly),lo,hi) for (lo,hi),poly in zip(cells,polys)),Q()) for k in range(12)] for n,polys in p.items()}
def head(a,b,L):return sum((Q(2*k+1,2)*raw[a][k]*raw[b][k] for k in range(L)),Q())
rows=[]
for L in [3,4,8,12]:
 S=whole['s']-head('s','s',L);C=cross-head('s','r',L);R=whole['r']-head('r','r',L);T=whole['q']-head('q','q',L)
 assert S>=0 and 0<=R<=Dr/(L*(L+1)) and T==S+2*C+R
 M=S+2*C+Dr/(L*(L+1));assert M>=T>=0
 if L==3:assert (S,C,R,T,M)==(Q(5,8),Q(-1,16),Q(7,96),Q(55,96),Q(23,36))
 rows.append({k:str(v) for k,v in {'L':L,'S':S,'C':C,'R':R,'joint_exact':T,'joint_sobolev_upper':M}.items()})
with ctx.workprec(256):
 vm=[potential_moment(j,arb.const_log2()) for j in range(13)]
 v2=potential_square_moment(2,arb.const_log2(),arb.pi())
 cm=[logarithmic_cell_moments(qarb(a),qarb(b),2) for a,b in cells]
 def vx_inner(name):return sum((sum((qarb(c)*mom[j+1] for j,c in enumerate(poly)),arb(0)) for poly,mom in zip(p[name],cm)),arb(0))
 ivq,ivs,ivr=[vx_inner(n) for n in ['q','s','r']]
 vg=[sum((qarb(c)*vm[j] for j,c in enumerate(mul(basis[k],[Q(),Q(1)]))),arb(0)) for k in range(12)]
 GW=v2+2*ivs+qarb(whole['s']);CW=ivr+qarb(cross);FW=v2+2*ivq+qarb(whole['q'])
 full=[]
 for L in [3,4,8,12]:
  G=GW-sum(((2*k+1)*(vg[k]+qarb(raw['s'][k]))**2/2 for k in range(L)),arb(0))
  C=CW-sum(((2*k+1)*(vg[k]+qarb(raw['s'][k]))*qarb(raw['r'][k])/2 for k in range(L)),arb(0))
  F=FW-sum(((2*k+1)*(vg[k]+qarb(raw['q'][k]))**2/2 for k in range(L)),arb(0))
  R=whole['r']-head('r','r',L);ident=G+2*C+qarb(R)-F;lo,hi=endpoints(ident);assert lo<=0<=hi
  M=G+2*C+qarb(Dr/(L*(L+1)));assert M>F and M>0
  full.append({'L':L,'C_display':float(C.mid()),'complete_tail_display':float(F.mid()),'joint_upper_display':float(M.upper())})
  if L==3:
   eps=Q(1,16);bound=(M.sqrt()+qarb(eps)*qarb(Q(2,3)).sqrt())**2
   for sign in [-1,1]:
    actual=F+sign*2*qarb(eps)*(vg[5]+qarb(raw['q'][5]))+qarb(eps*eps*Q(2,11))
    assert bound>actual
 gen_cells=[[endpoints(v) for v in row] for row in cm];gen_v2=endpoints(v2)
with ctx.workprec(512):
 count=0
 for (a,b),bounds in zip(cells,gen_cells):
  for (lo,hi),v in zip(bounds,cell_v_moments(qarb(a),qarb(b),2)):
   rl,rh=endpoints(v);assert lo<=rl<=rh<=hi;count+=1
 rl,rh=endpoints(global_v_moments(2,True)[2]);assert gen_v2[0]<=rl<=rh<=gen_v2[1]
print(json.dumps({'format':'jump-refinement-small-controls-v1','step_coefficient_identities':sigma_checks,'step_gram_identities':16,'exact_whole':{**{n:str(v) for n,v in whole.items()},'cross':str(cross),'weighted_derivative':str(Dr)},'arithmetic_tails':rows,'full_potential_source_tails':full,'independent_log_cell_containments':count,'independent_v2_containment':True,'collective_residual_controls':2,'internal_seconds':time.perf_counter()-start},indent=2))
