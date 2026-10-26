"""One-column whole-line dual loss assessment; no new support or full matrix."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from flint import acb, arb, ctx
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms


def aq(x):
    x = Q(x)
    return arb(x.numerator) / x.denominator


def endpoints(x):
    lower, upper = arb_to_rational_enclosure(x)
    return {"lower": str(lower), "upper": str(upper)}


def power_lower(x):
    if x < 1:
        return 0
    value = 1
    while 2 * value <= x:
        value *= 2
    return value


def assess(inputs):
    raw = inputs.read_bytes()
    pins = json.loads(raw)
    if pins["format"] != "energy-aware-dual-assessment-inputs-v1":
        raise ValueError("wrong input format")
    T, alpha, beta, m = [Q(pins[k]) for k in ("T", "alpha", "beta", "current_m")]
    count = pins["producer_terms"]
    if (T, alpha, beta, m, count, pins["producer_precision_bits"]) != (Q(3,4),Q(1,4),Q(873,1024),Q(1,3),64,384):
        raise ValueError("declared fixed case changed")
    ctx.prec = 384
    L = 2*T
    pi = arb.pi()
    A0 = aq(Q(1,4)).digamma() - pi.log()
    A4 = acb(aq(Q(1,4)), arb(2)).digamma().real - pi.log()
    if arb_to_rational_enclosure(A4)[1] >= 0:
        raise ValueError("uniform witness-band sign unqualified")
    terms = enumerate_active_prime_power_terms(3,4,prec=384)
    if [term.m for term in terms] != [2,3,4]:
        raise ValueError("strict arithmetic set changed")
    arch = A0
    coupling = arb(0)
    for k in range(count):
        rate = Q(4*k+1,2)
        factor = 1-(-aq(rate*L)).exp()
        arch += 2*factor/aq(L*rate*rate)
        coupling += factor*factor/aq(L*rate*rate)
    pole = 32*(aq(T)/2).sinh()**2/aq(L)
    arithmetic = -2*sum((term.coefficient*(1-term.log_m/aq(L)) for term in terms), arb(0))
    physical = arch+pole+arithmetic
    qlo, qpartial_hi = arb_to_rational_enclosure(physical)
    ilo, ipartial_hi = arb_to_rational_enclosure(coupling)
    qhi = qpartial_hi+Q(2,L*(4*count-3))
    ihi = ipartial_hi+Q(1,L*(4*count-3))
    C = 5/(4*pi*aq(L))
    clo, chi = arb_to_rational_enclosure(C)
    if not 0 < qlo <= qhi or ilo <= 0:
        raise ValueError("positive physical/witness enclosure not qualified")
    negative_raw = qhi-ilo*ilo/(m+chi)
    negative_grid = Q(pins["negative_upper_publication_grid"])
    negative_upper = Q((negative_raw/negative_grid).__ceil__())*negative_grid
    repair_raw = ilo*ilo/qhi-chi
    repair_grid = Q(pins["necessary_floor_publication_grid"])
    repair_lower = Q((repair_raw/repair_grid).__floor__())*repair_grid
    effective = aq(beta)+aq(alpha)*(1-A0)
    effective_lower = arb_to_rational_enclosure(effective)[0]
    dimension_rows = []
    for label,target in [("all_allowed_relative_pairs",repair_lower),("fixed_alpha_beta",(repair_lower+effective_lower)/(1-alpha))]:
        R = 2*pi*aq(target-Q(1,8)).exp()
        R_lower = arb_to_rational_enclosure(R)[0]
        N_lower = T*R_lower/2-1
        published = power_lower(N_lower)
        dimension_rows.append({"label":label,"exterior_target_lower":str(target),
                               "R_lower":str(R_lower),"N_lower":str(N_lower),
                               "published_N_strictly_greater_than":published,
                               "dense_array_entries_at_minimum_integer_N":(published+1)**2,
                               "scope":"Necessary only for the C-0112 geometric leakage recipe when raising its floor to repair this dual loss; no such matrix generated."})
    modules = {}
    for name,module in sorted(sys.modules.items()):
        if (name == "scripts" or name.startswith("scripts.")) and getattr(module,"__file__",None):
            path = Path(module.__file__).resolve()
            if not path.is_relative_to(ROOT):
                raise RuntimeError("project import escaped source root")
            modules[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"format":"research-energy-aware-dual-assessment-v1",
            "status":"NEGATIVE_CURRENT_CONTRACTION_CERTIFIED" if negative_upper<0 else "UNRESOLVED",
            "support":str(T),"alpha":str(alpha),"beta":str(beta),"m":str(m),
            "precision_bits":ctx.prec,"series_terms":count,"active_terms":[term.m for term in terms],
            "A0":endpoints(A0),"A4":endpoints(A4),
            "physical_constant_low":{"lower":str(qlo),"upper":str(qhi)},
            "outside_archimedean_coupling":{"lower":str(ilo),"upper":str(ihi)},
            "universal_witness_energy_excess":{"lower":str(clo),"upper":str(chi)},
            "current_ideal_schur_upper_raw":str(negative_raw),
            "current_ideal_schur_upper":str(negative_upper),
            "necessary_repair_floor_raw_lower":str(repair_raw),
            "necessary_repair_floor_lower":str(repair_lower),
            "repair_dimension_requirements":dimension_rows,
            "all_finite_low_subtractions_covered":True,"all_N_with_constant_and_same_m_covered":True,
            "new_Weil_negative_direction":False,"new_support_or_full_matrix":False,
            "producer_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "inputs_sha256":hashlib.sha256(raw).hexdigest(),"imported_project_modules":modules}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs",type=Path,default=Path(__file__).with_name("assessment-inputs-v1.json"))
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=assess(args.inputs)
    with args.output.open("x",encoding="utf-8",newline="\n") as handle:
        json.dump(result,handle,indent=2);handle.write("\n")
    print(json.dumps({"status":result["status"],"ideal_schur_upper":result["current_ideal_schur_upper"],
                      "necessary_floor_lower":result["necessary_repair_floor_lower"],
                      "new_Weil_negative_direction":False}))


if __name__=="__main__":
    main()
