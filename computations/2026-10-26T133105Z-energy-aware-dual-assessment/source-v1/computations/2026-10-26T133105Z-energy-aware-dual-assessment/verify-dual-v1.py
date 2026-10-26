"""Independent higher-precision assessment replay, not a theorem-admission tool."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from flint import acb,arb,ctx
from scripts.cert.constants import arb_to_rational_enclosure


def aq(x):
    x=Q(x)
    return arb(x.numerator)/x.denominator


def reject_numbers(value):
    raise ValueError("nonexact JSON number")


def rat(value):
    if not isinstance(value,str) or str(Q(value))!=value:
        raise ValueError("noncanonical rational")
    return Q(value)


def bounds(x):
    lo,hi=arb_to_rational_enclosure(x)
    return {"lower":str(lo),"upper":str(hi)}


def require(test,message):
    if not test:
        raise ValueError(message)


def contain(claim,lower,upper,label):
    require(rat(claim["lower"])<=lower<=upper<=rat(claim["upper"]),"dishonest "+label+" enclosure")


def audit(path):
    raw=path.read_bytes();packet=json.loads(raw,parse_float=reject_numbers,parse_constant=reject_numbers)
    require(packet["format"]=="research-energy-aware-dual-assessment-v1","wrong research format")
    require((packet["support"],packet["alpha"],packet["beta"],packet["m"],packet["precision_bits"],packet["series_terms"],packet["active_terms"])==("3/4","1/4","873/1024","1/3",384,64,[2,3,4]),"changed fixed source")
    here=Path(__file__).parent;producer=here/'assess-dual-v1.py';inputs=here/'assessment-inputs-v1.json'
    require(hashlib.sha256(producer.read_bytes()).hexdigest()==packet["producer_sha256"],"producer fingerprint changed")
    require(hashlib.sha256(inputs.read_bytes()).hexdigest()==packet["inputs_sha256"],"input declaration changed")
    pins=json.loads(inputs.read_bytes())
    require((pins["independent_terms"],pins["independent_precision_bits"])==(128,512),"changed independent declaration")
    ctx.prec=512;T=Q(3,4);L=2*T;alpha=Q(1,4);beta=Q(873,1024);m=Q(1,3);count=128
    pi=arb.pi();log2=arb(2).log();log3=arb(3).log()
    require(all(arb(k).log()<aq(L) for k in [2,3,4]) and aq(L)<arb(5).log(),"strict active window not proved")
    A0=acb(aq(Q(1,4)),0).digamma().real-pi.log()
    A4=acb(aq(Q(1,4)),2).digamma().real-pi.log()
    for label,value in [("A0",A0),("A4",A4)]:
        lo,hi=arb_to_rational_enclosure(value);contain(packet[label],lo,hi,label)
    require(arb_to_rational_enclosure(A4)[1]<0,"central-band sign not established")
    arch=A0;cross=arb(0)
    for k in range(count):
        a=Q(k)+Q(1,4);z=1-(-4*aq(T*a)).exp()
        arch+=z/aq(4*T*a*a)
        cross+=z*z/aq(8*T*a*a)
    a_next=Q(count)+Q(1,4);z_next=1-(-4*aq(T*a_next)).exp()
    arch_tail_lower=z_next/aq(4*T*a_next)
    cross_tail_lower=z_next*z_next/aq(8*T*a_next)
    arch_tail_upper=Q(1,4*T*(Q(count)-Q(3,4)))
    cross_tail_upper=Q(1,8*T*(Q(count)-Q(3,4)))
    # This organization does not call the producer or its arithmetic enumeration.
    prime=-2*(log2/arb(2).sqrt()*(1-log2/aq(L))+log3/arb(3).sqrt()*(1-log3/aq(L))+(log2/2)*(1-2*log2/aq(L)))
    pole=8*((aq(T)).exp()+(-aq(T)).exp()-2)/aq(L)
    base=arch+prime+pole
    q_lower=arb_to_rational_enclosure(base+arch_tail_lower)[0]
    q_upper=arb_to_rational_enclosure(base)[1]+arch_tail_upper
    i_lower=arb_to_rational_enclosure(cross+cross_tail_lower)[0]
    i_upper=arb_to_rational_enclosure(cross)[1]+cross_tail_upper
    contain(packet["physical_constant_low"],q_lower,q_upper,"physical constant low")
    contain(packet["outside_archimedean_coupling"],i_lower,i_upper,"outside archimedean coupling")
    C=5/(8*pi*aq(T));clo,chi=arb_to_rational_enclosure(C)
    contain(packet["universal_witness_energy_excess"],clo,chi,"full witness energy excess")
    require(q_lower>0 and i_lower>0,"physical or cross sign unresolved")
    source_q=rat(packet["physical_constant_low"]["upper"])
    source_i=rat(packet["outside_archimedean_coupling"]["lower"])
    source_C=rat(packet["universal_witness_energy_excess"]["upper"])
    source_raw=source_q-source_i*source_i/(m+source_C)
    require(rat(packet["current_ideal_schur_upper_raw"])==source_raw,"source Schur arithmetic inconsistent")
    grid=Q(1,1024);published=rat(packet["current_ideal_schur_upper"])
    require(published==Q((source_raw/grid).__ceil__())*grid,"Schur publication policy changed")
    fresh_negative=q_upper-i_lower*i_lower/(m+chi)
    require(fresh_negative<=published<0,"negative current contraction not independently proved")
    require(packet["status"]=="NEGATIVE_CURRENT_CONTRACTION_CERTIFIED","false assessment status")
    raw_floor=source_i*source_i/source_q-source_C
    grid=Q(1,16);floor=rat(packet["necessary_repair_floor_lower"])
    require(rat(packet["necessary_repair_floor_raw_lower"])==raw_floor and floor==Q((raw_floor/grid).__floor__())*grid,"floor publication policy inconsistent")
    require(floor<=i_lower*i_lower/q_upper-chi,"repair floor overstated")
    effective_lower=arb_to_rational_enclosure(aq(beta)+aq(alpha)*(1-A0))[0]
    labels=["all_allowed_relative_pairs","fixed_alpha_beta"]
    require([r["label"] for r in packet["repair_dimension_requirements"]]==labels,"dimension labels changed")
    rows=[]
    for source_row,label in zip(packet["repair_dimension_requirements"],labels,strict=True):
        target=floor if label==labels[0] else (floor+effective_lower)/(1-alpha)
        require(rat(source_row["exterior_target_lower"])<=target,"exterior target overstated")
        R_lower=arb_to_rational_enclosure(2*pi*aq(target-Q(1,8)).exp())[0]
        N_lower=T*R_lower/2-1
        source_R=rat(source_row["R_lower"]);source_N=rat(source_row["N_lower"])
        require(source_R<=R_lower and source_N==T*source_R/2-1,"dishonest cutoff/dimension lower")
        n=source_row["published_N_strictly_greater_than"]
        require(type(n) is int and n>0 and n&(n-1)==0 and n<=source_N<2*n and n<=N_lower,"dimension publication overstated")
        require(source_row["dense_array_entries_at_minimum_integer_N"]==(n+1)**2,"dense accounting inconsistent")
        rows.append({"label":label,"published_N_strictly_greater_than":n,"independent_N_lower":str(N_lower)})
    require(packet["all_finite_low_subtractions_covered"] is True and packet["all_N_with_constant_and_same_m_covered"] is True and packet["new_Weil_negative_direction"] is False and packet["new_support_or_full_matrix"] is False,"scope flags changed")
    modules={}
    for name,module in sorted(sys.modules.items()):
        if (name=="scripts" or name.startswith("scripts.")) and getattr(module,"__file__",None):
            file=Path(module.__file__).resolve();require(file.is_relative_to(ROOT),"project import escaped source root")
            modules[file.relative_to(ROOT).as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest()
    return {"format":"research-energy-aware-dual-audit-v1","status":"PASS_NEGATIVE_DUAL_CONTRACTION",
            "source_sha256":hashlib.sha256(raw).hexdigest(),"audit_code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "precision_bits":512,"positive_series_terms":128,"independent_two_sided_tails":True,
            "independent_physical_constant_low":{"lower":str(q_lower),"upper":str(q_upper)},
            "independent_outside_coupling":{"lower":str(i_lower),"upper":str(i_upper)},
            "accepted_negative_schur_upper":str(published),"necessary_floor_lower":str(floor),
            "repair_dimensions":rows,"imported_project_modules":modules,
            "new_Weil_negative_direction":False,"new_support_or_full_matrix":False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source",type=Path);parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    try:
        result=audit(args.source)
    except (ValueError,KeyError,TypeError,AssertionError) as exc:
        print("REJECT: "+str(exc),file=sys.stderr);raise SystemExit(2)
    with args.output.open("x",encoding="utf-8",newline="\n") as handle:
        json.dump(result,handle,indent=2);handle.write("\n")
    print(json.dumps({"status":result["status"],"negative_schur_upper":result["accepted_negative_schur_upper"],"new_Weil_negative_direction":False}))


if __name__=="__main__":
    main()
