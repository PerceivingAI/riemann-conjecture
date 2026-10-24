"""Independent standard-library replay of serialized weighted enclosures.
No Arb import or analytical source reconstruction.
"""
import argparse, hashlib, json
from fractions import Fraction as Q
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("result", type=Path)
a=parser.parse_args()
raw=a.result.read_bytes()
if hashlib.sha256(raw).hexdigest()!="92cf2dbc31326167c34f795f72dff394efb57430c24f14d23706d73da63df667":
    raise ValueError("result identity")
p=json.loads(raw)
for name,digest in {**p["input_sha256"],**p["source_sha256"]}.items():
    if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=digest:
        raise ValueError("input/source identity: "+name)
if hashlib.sha256((a.result.parent/"source/weil_weighted_source_tail-v2.py").read_bytes()).hexdigest()!=p["consumer_sha256"]:
    raise ValueError("executed consumer snapshot identity")
count=0
for pairs,refs in [(p["scalar_intervals"],p["reference_scalar_intervals"])]+[(row,p["reference_head_coefficients"][k]) for k,row in p["head_coefficients"].items()]:
    for name,pair in pairs.items():
        lo,hi=map(Q,pair); x,y=map(Q,refs[name])
        if not lo<=x<=y<=hi:
            raise ValueError("interval containment")
        count+=1
original=json.loads(Path("computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json").read_bytes())
source=json.loads(Path("computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json").read_bytes())
audit=json.loads(Path("computations/2026-10-23T105408Z-directional-loss-review/data/loss-audit.json").read_bytes())
joint=json.loads(Path("computations/2026-10-23T185253Z-joint-source-tail/data/result.json").read_bytes())
scale=1<<352
def down(x):
    y=x*scale
    return Q(y.numerator//y.denominator,scale)
def up(x):
    return -down(-x)
mu=Q(original["mu_lower_exact"])
lam={192:mu}
B=p["evaluation_boundary"]
for k in range(193,B+1): lam[k]=lam[k-1]+Q(1,k)
Mlo,Mhi=map(Q,joint["scalars"]["joint_tail"])
h=Q(audit["exact"]["prefix_only_reference_upper"])
if not (Mhi/lam[B]<=h/4<Mhi/lam[B-2]):
    raise ValueError("minimal predeclared even accuracy boundary")
Sl=Su=Nl=Nu=Ml=Mu=correction=Q()
for text,row in p["head_coefficients"].items():
    k=int(text); lo,hi=map(Q,row["sum_truncated"])
    squarelo=Q() if lo<=0<=hi else min(lo*lo,hi*hi)
    squarehi=max(lo*lo,hi*hi)
    termlo,termhi=down(squarelo/lam[k]),up(squarehi/lam[k])
    Sl+=termlo; Su+=termhi
    if k<224: Nl+=termlo; Nu+=termhi
    else:
        if row["R32"]!=["0","0"]: raise ValueError("high residual polynomial coefficient")
        Ml+=squarelo; Mu+=squarehi
        correction+=(lam[B]-lam[k])*squarehi
Tl,Tu=down(max(Q(),Mlo-Mu)),up(Mhi-Ml)
Dlo=down(max(lam[224]*Mlo,lam[B]*Mlo-correction))
ceiling=up(Mhi*Mhi/Dlo)
e={k:Q(v) for k,v in p["exact"].items()}
for name,value in {"band_inverse_energy_lower":Sl,"band_inverse_energy_upper":Su,"remaining_mass_lower":Tl,"remaining_mass_upper":Tu,"harmonic_moment_lower":Dlo,"scalar_cauchy_expression_upper":ceiling,"remaining_inverse_energy_upper":up(Tu/lam[B])}.items():
    if e[name]!=value: raise ValueError("rational endpoint replay: "+name)
d=Q(source["delta_upper_exact"]); n=Q(source["exact_trial_mass_norm"])
eps2=d*d*n/lam[211]
# Squared polynomial predicates establish the root-based norm bounds exactly.
Jlo,Jhi=e["J_full_lower"],e["J_full_upper"]
left=Sl-Jlo-eps2
if not (left>=0 and left*left>=4*eps2*Jlo): raise ValueError("collective inverse-energy lower")
U=Su+Tu/lam[B]
right=Jhi-U-eps2
if not (right>=0 and right*right>=4*eps2*U): raise ValueError("collective inverse-energy upper")
near=e["near_full_inverse_energy_upper"]
r=near-Nu-eps2
if not (r>=0 and r*r>=4*eps2*Nu): raise ValueError("near-energy upper")
alo,ahi=e["a_full_lower"],e["a_full_upper"]
x,y=map(Q,p["scalar_intervals"]["a_truncated"])
if not (alo<=x-d*n and ahi>=min(y+d*n,Q(original["a_full_rayleigh_upper_exact"]))): raise ValueError("full physical low-form error")
Pl,Pu=e["prefix_lower"],e["prefix_upper"]
if not (Pl<=Q(audit["exact"]["known_inverse_lower"]) and Pu>=Q(audit["exact"]["known_inverse_upper"])): raise ValueError("prefix direction")
if not (e["reference_lower"]<=alo-Pu-Jhi and e["reference_upper"]>=ahi-Pl-Jlo): raise ValueError("reference directions")
if not (e["reference_lower"]>Q(3,5) and e["reference_upper"]<Q(9,10)): raise ValueError("strict positive directional bracket")
floor=down(h-near-ceiling)
if not (floor==e["scalar_cauchy_reported_upper_floor"] and floor>0): raise ValueError("scalar Cauchy exclusion")
print(json.dumps({"status":"WEIGHTED_REFERENCE_REPLAY_ACCEPTED","containments":count,"B":B,"reference_lower":str(e["reference_lower"]),"reference_upper":str(e["reference_upper"]),"strict_reference_lower_exceeds":"3/5","scalar_cauchy_rule_excluded":True,"scope":"exact consequences only, no analytical reconstruction; positive one-trial reference, not a positive matrix or RH"},indent=2))
