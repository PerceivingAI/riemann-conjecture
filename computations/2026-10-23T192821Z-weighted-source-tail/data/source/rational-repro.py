import json, traceback
from fractions import Fraction as Q
from scripts.weil_weighted_source_tail import _consequences
mu=Q(1,(1<<1024)-109)
source={"exact_trial_mass_norm":"1/2","delta_upper_exact":"0"}
original={"mu_lower_exact":str(mu),"a_full_rayleigh_upper_exact":"10"}
audit={"exact":{"prefix_only_reference_upper":"9","known_inverse_lower":"1","known_inverse_upper":"1"}}
joint={"scalars":{"joint_tail":["1/100","1/100"]},"exact":{"J_concentration_lower":"0"}}
heads={str(k):{"sum_truncated":["1/100","1/100"],"R32":["0","0"]} for k in range(225,425,2)}
try:
    p=_consequences(original,source,audit,joint,{"a_truncated":["10","10"]},heads)
    print(json.dumps(p))
except ValueError:
    traceback.print_exc()
    raise SystemExit(2)
