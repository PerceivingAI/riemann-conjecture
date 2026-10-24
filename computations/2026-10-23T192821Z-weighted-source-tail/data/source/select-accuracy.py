import json
from fractions import Fraction as Q
from pathlib import Path
p=json.loads(Path("computations/2026-10-23T185253Z-joint-source-tail/data/result.json").read_bytes())
o=json.loads(Path("computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json").read_bytes())
mu=Q(o["mu_lower_exact"])
M=Q(p["scalars"]["joint_tail"][1])
h=Q(p["exact"]["prefix_only_reference_upper"])
lam=mu+sum((Q(1,j) for j in range(193,225)),Q())
B=224
while M/lam>h/4:
    if B>=1024:
        raise ValueError("accuracy-selected boundary exceeds fixed scope")
    lam+=Q(1,B+1)+Q(1,B+2)
    B+=2
bits=((4*B+512+255)//256)*256
print(json.dumps({"B":B,"generator_bits":bits,"reference_bits":2*bits,"publication_bits":352,"reference_publication_bits":512,"tail_error_budget":str(h/4),"tail_error_ceiling":str(M/lam),"display":{"tail_error_budget":float(h/4),"tail_error_ceiling":float(M/lam)},"selection":"smallest even B>=224 with w_B*M224_upper<=h/4; chosen before evaluating new source coefficients","no_cutoff_search":True},indent=2))
