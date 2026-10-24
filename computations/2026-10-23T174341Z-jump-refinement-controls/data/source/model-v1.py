import hashlib,json,time
from pathlib import Path
from fractions import Fraction as Q
from flint import arb,ctx
from scripts.verify_combined_schur_analytic_entries import qarb,endpoints
start=time.perf_counter()
paths=[('computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json','44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b'),('computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json','9b9a1a0a0b420df0147f07c6fa1f5d9ee9005fb68dc8213cd8880d98556dd843')]
p=[]
for name,digest in paths:
 data=Path(name).read_bytes();assert hashlib.sha256(data).hexdigest()==digest;p.append(json.loads(data))
o,s=p
assert (o['support'],o['dimension'],o['K'],o['active_terms'])==('3/5',192,32,[2,3])
assert s['residual_image_degree']==223
z=list(map(Q,o['trial_rational_vector']));assert len(z)==192 and all(not z[k] for k in range(0,192,2))
v=sum(z,Q());norm=sum((c*c*Q(2,2*j+1) for j,c in enumerate(z)),Q());assert norm==Q(s['exact_trial_mass_norm'])
for packet in (o,s):
 for name,digest in packet['source_sha256'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest
with ctx.workprec(512):
 def iv(pair):
  lo,hi=map(Q,pair);ball=qarb((lo+hi)/2)+arb(0,qarb((hi-lo)/2).upper())
  bl,bh=endpoints(ball);assert bl<=lo<=hi<=bh;return ball
 c=[iv(s['arithmetic_constants_reference'][str(m)]['coefficient']) for m in (2,3)]
 tau=[iv(s['arithmetic_constants_reference'][str(m)]['tau']) for m in (2,3)]
 assert 1<tau[0]<tau[1]<2 and c[0]>0 and c[1]>0
 a=[x-1 for x in tau];L=224
 full=2*qarb(v)**2*sum((c[i]*c[j]*(1-a[max(i,j)]) for i in range(2) for j in range(2)),arb(0))
 b=[-a[1],-a[0],a[0],a[1]];jump=[qarb(v)*c[1],qarb(v)*c[0],qarb(v)*c[0],qarb(v)*c[1]]
 gram=sum((jump[i]*jump[j]*(1+b[min(i,j)])*(1-b[max(i,j)])/2 for i in range(4) for j in range(4)),arb(0))
 gl,gh=endpoints(full-gram);assert gl<=0<=gh
 leg=[]
 for x in a:
  row=[arb(1),x]
  for k in range(1,L):row.append(((2*k+1)*x*row[-1]-k*row[-2])/(k+1))
  leg.append(row)
 head=arb(0)
 for k in range(1,L,2):
  sk=2*qarb(v)*sum((c[j]*(leg[j][k-1]-leg[j][k+1]) for j in range(2)),arb(0))/(2*(2*k+1))**Q(1,2) if False else 2*qarb(v)*sum((c[j]*(leg[j][k-1]-leg[j][k+1]) for j in range(2)),arb(0))/arb(2*(2*k+1)).sqrt()
  head+=sk*sk
 tail=full-head;tl,th=endpoints(tail);B=(c[0]+c[1])*qarb(norm).sqrt();_,bup=endpoints(B)
 exact={'step_whole_norm2':[str(x) for x in endpoints(full)],'step_tail_norm2':[str(tl),str(th)],'arithmetic_norm_upper':str(bup),'arithmetic_norm2_upper':str(bup*bup)}
 resolved=tl>bup*bup
 if resolved:
  cross=qarb(bup)*qarb(tl).sqrt()-qarb(tl);_,cup=endpoints(cross)
  sep=(2*qarb(tl).sqrt()-qarb(bup))**2;slow,_=endpoints(sep)
  assert cup<0 and slow>bup*bup
  exact.update({'arithmetic_mixed_tail_upper':str(cup),'separate_norm_bound_lower':str(slow)})
 else:cup=None;slow=None
 result={'format':'original-jump-model-cancellation-v1','role':'arithmetic-step-model comparison, NOT full-source tail evaluation','support':'3/5','N':192,'K':32,'tail_index':L,'precision_bits':512,'odd_jump_model_coefficients_evaluated':L//2,'exact':exact,'display':{'step_whole_norm2':float(full.mid()),'step_tail_norm2':float(tail.mid()),'arithmetic_norm2_upper':float(bup*bup),'arithmetic_mixed_tail_upper':float(cup) if cup is not None else None,'separate_norm_bound_lower':float(slow) if slow is not None else None},'status':'SIGNED_CANCELLATION_CERTIFIED' if resolved else 'INCONCLUSIVE','full_source_tail_bound_evaluated':False,'new_full_source_moments':False,'source_images_assembled':False,'actual_reference_sign':'UNDETERMINED','internal_seconds':time.perf_counter()-start}
 print(json.dumps(result,indent=2))
