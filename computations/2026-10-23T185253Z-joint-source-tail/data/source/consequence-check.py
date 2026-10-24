"""Exact consequence replay on the retained joint-tail packet; no analytic reconstruction."""
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("result", type=Path)
args=parser.parse_args()
raw=args.result.read_bytes()
if hashlib.sha256(raw).hexdigest() != "67eba074fdc79e48934fbb2ae80212fa920f62bddc6a324e500bf8c4a296c2c8":
    raise ValueError("retained joint result identity")
p=json.loads(raw)
for name,digest in {**p["input_sha256"],**p["source_sha256"]}.items():
    if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=digest:
        raise ValueError("source/input identity: "+name)
count=0
for name,pair in p["scalars"].items():
    lo,hi=map(Q,pair)
    a,b=map(Q,p["reference_scalars"][name])
    if not lo<=a<=b<=hi:
        raise ValueError("scalar containment: "+name)
    count+=1
for k,row in p["head_coefficients"].items():
    for name,pair in row.items():
        lo,hi=map(Q,pair)
        a,b=map(Q,p["reference_head_coefficients"][k][name])
        if not lo<=a<=b<=hi:
            raise ValueError("head containment: "+k+"/"+name)
        count+=1
source=json.loads(Path("computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json").read_bytes())
original=json.loads(Path("computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json").read_bytes())
audit=json.loads(Path("computations/2026-10-23T105408Z-directional-loss-review/data/loss-audit.json").read_bytes())
n=Q(source["exact_trial_mass_norm"])
d=Q(source["delta_upper_exact"])
m=Q(p["scalars"]["joint_tail"][0])
if not (0<n<1 and 0<m<1 and d>=0 and m>d*d*n):
    raise ValueError("reverse-triangle lower prerequisites")
full_lower=m-2*d
exact={k:Q(v) for k,v in p["exact"].items()}
upper=exact["full_source_tail_upper"]
cap=min(Q(p["scalars"]["joint_tail"][1]),Q(p["scalars"]["G"][1])+2*Q(p["scalars"]["C"][1])+Q(p["scalars"]["regular_tail"][1]))
a=upper-cap-d*d*n
if not (a>=0 and a*a>=4*cap*d*d*n):
    raise ValueError("collective residual upper")
mu=Q(original["mu_lower_exact"])
w=1/(mu+sum((Q(1,k) for k in range(193,224)),Q()))
h=Q(audit["exact"]["prefix_only_reference_upper"])
R=Q(audit["exact"]["omitted_mass_lower"])
J=w*max(Q(),R-upper)
s=h-J
threshold=R-h/w
best_upper_lower=h-w*max(Q(),R-full_lower)
if not (w==exact["weight_223"] and h==exact["prefix_only_reference_upper"] and R==exact["omitted_mass_lower"] and J==exact["J_concentration_lower"] and s==exact["reference_directional_upper"] and threshold==exact["tail_cap_needed_for_negative_upper"]):
    raise ValueError("exact concentration replay")
if not (Q(7,10)<full_lower<=upper<Q(71,100) and full_lower>threshold and best_upper_lower>Q(69,50) and upper<exact["prior_full_source_control_upper"] and J>0 and s>0):
    raise ValueError("fixed comparison predicates")
print(json.dumps({"status":"EXACT_CONSEQUENCE_REPLAY_ACCEPTED","interval_containments":count,"full_source_tail_mass_lower":str(full_lower),"fixed_L_reported_upper_lower":str(best_upper_lower),"reference_directional_upper":str(s),"display":{"full_source_tail_mass_lower":float(full_lower),"fixed_L_reported_upper_lower":float(best_upper_lower)},"actual_reference_sign":"UNDETERMINED","scope":"same L224 concentration formula is too weak, not a no-go for the source/method; exact arithmetic only, no source reconstruction"},indent=2))
