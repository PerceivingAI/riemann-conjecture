import hashlib, json
from fractions import Fraction as F
from pathlib import Path
original_path=Path("computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json")
source_path=Path("computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json")
a=original_path.read_bytes(); b=source_path.read_bytes()
assert hashlib.sha256(a).hexdigest()=="44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b"
assert hashlib.sha256(b).hexdigest()=="9b9a1a0a0b420df0147f07c6fa1f5d9ee9005fb68dc8213cd8880d98556dd843"
p=json.loads(a); q=json.loads(b)
mu=F(p["mu_lower_exact"]); delta=F(p["delta_upper_exact"])
def w(k):
    return 1/(mu+sum((F(1,j) for j in range(193,k+1)),F()))
base=F(p["a_full_rayleigh_upper_exact"])-w(211)*F(p["gram_full_rayleigh_lower_exact"])
correction=F()
for k in range(193,211,2):
    x,y=q["moments"][str(k)]["sum_truncated"]["published_dyadic"]
    lo,hi=F(x,2**352)-delta,F(y,2**352)+delta
    square=F() if lo<=0<=hi else min(lo*lo,hi*hi)
    correction+=(w(k)-w(211))*square
upper=base-correction
assert upper < -F(6,5)
print(json.dumps({"status":"PASS_INDEPENDENT_EXACT_RATIONAL_REPLAY","theta_exact":str(base),"weighted_sum_lower_exact":str(correction),"directional_upper_exact":str(upper),"strict_upper_below_minus_six_fifths":True,"source_reassembly_performed":False},sort_keys=True))
