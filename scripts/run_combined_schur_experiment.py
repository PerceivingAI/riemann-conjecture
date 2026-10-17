"""One bounded, pre-theorem combined-Schur research run.

Produces an exact rational input packet for separate rechecking. This does not
create a certificate, alter theorem admission, or certify numerical eigenvalues.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
import time
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx

from scripts.cert.constants import arb_to_rational_enclosure, c_T_enclosure
from scripts.cert.legendre_schur import harmonic
from scripts.cert.mixed_gram_research import assemble_truncated_mixed_gram
from scripts.cert.multi_prime_legendre_schur import (
    _arb_fraction, _residual_rho, compressed_shift_norm_bound,
)

DYADIC_BITS=352
ETA=Fraction(1,2**24)
MAX_WIDTH=Fraction(1,2**128)


def dyadic_pair(value: arb, bits: int=DYADIC_BITS) -> list[int]:
    lo,hi=arb_to_rational_enclosure(value)
    factor=1<<bits
    l=lo.numerator*factor//lo.denominator
    h=-((-hi.numerator*factor)//hi.denominator)
    if h<l:
        raise RuntimeError("impossible outward dyadic bounds")
    return [l,h]


def stable_source_hashes() -> dict[str,str]:
    paths=(
        "scripts/cert/mixed_gram_research.py",
        "scripts/run_combined_schur_experiment.py",
        "scripts/profile_mixed_gram_research.py",
        "tests/test_mixed_gram_research.py",
        "scripts/weil_projected_mixed_schur_check.py",
    )
    return {p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--dimension",type=int,choices=[192,196],required=True)
    ap.add_argument("--precision",type=int,choices=[1024,1280],default=1024)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    start=time.perf_counter()
    n=args.dimension
    print("START",n,args.precision,flush=True)
    hashes=stable_source_hashes()
    with ctx.workprec(args.precision):
        t=arb(11)/20
        data=assemble_truncated_mixed_gram(
            n=n,prec=args.precision,residual_order=32,support_num=11,support_den=20)
        if [term.m for term in data["active_terms"]] != [2,3]:
            raise RuntimeError("FAIL CLOSED: active prime powers not [2,3]")
        print("ASSEMBLED",n,round(time.perf_counter()-start,3),flush=True)
        cT=c_T_enclosure(args.precision,11,20)
        rho=_residual_rho(t,32)
        loss=sum((term.coefficient*compressed_shift_norm_bound(term,args.precision)
                  for term in data["active_terms"]),arb(0))
        mu=_arb_fraction(harmonic(n))-cT-rho-loss
        mu_pair=dyadic_pair(mu)
        if mu_pair[0]<=0:
            raise RuntimeError("FAIL CLOSED: complementary bound not strictly positive")

        low=[]
        gram=[]
        amax=0
        gmax=0
        norms=data["norms"]
        for i in range(n):
            lrow=[]
            grow=[]
            for j in range(i,n):
                a=data["V"][i][j]+data["P"][i][j]+data["Rk"][i][j]
                if i==j:
                    a += _arb_fraction(norms[i])*(
                        _arb_fraction(harmonic(i))-cT-data["delta_R"])
                if i!=j and (i-j)%2:
                    if not a.contains(0):
                        raise RuntimeError("FAIL CLOSED: low-form parity mismatch")
                    a=arb(0)
                if i!=j and not a.overlaps(
                    data["V"][j][i]+data["P"][j][i]+data["Rk"][j][i]):
                    raise RuntimeError("FAIL CLOSED: low-form nonsymmetry")
                ga=data["Gk"][i][j]
                apair=dyadic_pair(a)
                gpair=dyadic_pair(ga)
                amax=max(amax,apair[1]-apair[0])
                gmax=max(gmax,gpair[1]-gpair[0])
                lrow.append(apair)
                grow.append(gpair)
            low.append(lrow)
            gram.append(grow)
        delta_pair=dyadic_pair(data["delta_R"])
        if delta_pair[0]<0:
            raise RuntimeError("FAIL CLOSED: negative residual radius")
        print("BOUNDS",n,"LOW_MAX_DYADIC",amax,"GRAM_MAX_DYADIC",gmax,
              "GATE",max(amax,gmax) <= (1<<DYADIC_BITS)//(1<<128),flush=True)
        # All finite rational data needed to reconstruct A_lower, Gk upper,
        # full-residual G upper, and S_lower with a separate exact checker.
        packet={
            "format":"pretheorem-combined-schur-rational-inputs-v1",
            "status":"GENERATOR_INTERVAL_INPUTS_ONLY_NOT_A_THEOREM",
            "support":[11,20],
            "dimension":n,"precision_bits":args.precision,
            "residual_order":32,
            "active_terms":[term.m for term in data["active_terms"]],
            "basis":"ordinary_unnormalized_legendre",
            "dyadic_bits":DYADIC_BITS,
            "eta":[ETA.numerator,ETA.denominator],
            "mu_dyadic":mu_pair,
            "delta_dyadic":delta_pair,
            "low_A_triangular":low,
            "truncated_gram_triangular":gram,
            "source_sha256":hashes,
            "research_limits":{
                "full_gram_has_Suzuki_residual_only_via_delta":True,
                "matrix_sign_not_verified":True
            }
        }
        args.output.parent.mkdir(parents=True,exist_ok=True)
        raw=json.dumps(packet,separators=(",",":"),sort_keys=True).encode("utf8")
        compressed=gzip.compress(raw,compresslevel=6,mtime=0)
        partial=args.output.with_name(args.output.name+".partial")
        partial.write_bytes(compressed)
        os.replace(partial,args.output)
        sha=hashlib.sha256(compressed).hexdigest()
        print("PACKET",args.output,"BYTES",len(compressed),"SHA256",sha,
              "RAW_BYTES",len(raw),flush=True)
        print("COMPLEMENT_LOWER_APPROX_DIAGNOSTIC",float(Fraction(mu_pair[0],1<<DYADIC_BITS)),
              "DELTA_UPPER_APPROX_DIAGNOSTIC",float(Fraction(delta_pair[1],1<<DYADIC_BITS)),flush=True)
        print("INTERVAL_WIDTH_GATE",max(amax,gmax) <= (1<<(DYADIC_BITS-128)),flush=True)
        print("COMPLETED",n,"SECONDS",round(time.perf_counter()-start,3),flush=True)


if __name__=="__main__":
    main()
