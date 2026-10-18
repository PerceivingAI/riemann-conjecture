"""SYS-6.4 bounded selective combined-Schur sign probe.

Research-only single pair, not a certificate or independent analytic acceptance.
A float eigenvector proposes a rational trial direction; an Arb-bound strict
negative directional UPPER proves failure of the chosen conservative Schur
sufficient matrix, never negativity of the Weil quadratic form.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from fractions import Fraction
from pathlib import Path

import numpy as np
from flint import arb, ctx

from scripts.cert.constants import arb_to_rational_enclosure, c_T_enclosure
from scripts.cert.legendre_schur import harmonic
from scripts.cert.mixed_gram_research import assemble_truncated_mixed_gram
from scripts.cert.multi_prime_legendre_schur import (
    _arb_fraction, _residual_rho, compressed_shift_norm_bound,
)

K=32
ETA=Fraction(1,2**24)
SOURCE_PATHS=(
    "scripts/cert/mixed_gram_research.py",
    "scripts/cert/multi_prime_legendre_schur.py",
    "scripts/cert/prime_power_terms.py",
    "scripts/cert/residual_kernel.py",
    "scripts/weil_selective_support_probe.py",
)


def _pair(x: arb):
    return arb_to_rational_enclosure(x)


def _upper(x: arb):
    return _pair(x)[1]


def _lower(x: arb):
    return _pair(x)[0]


def run(t: Fraction, n: int, precision: int):
    if not Fraction(11,20)<t<Fraction(69,100) or n<160 or n>256 or precision<768:
        raise ValueError("restricted finite two-prime selective scout parameters")
    started=time.perf_counter()
    with ctx.workprec(precision):
        inputs=assemble_truncated_mixed_gram(
            n=n,prec=precision,residual_order=K,
            support_num=t.numerator,support_den=t.denominator)
        if [x.m for x in inputs["active_terms"]] != [2,3]:
            raise RuntimeError("unexpected active prime power set")
        print("SOURCE_ASSEMBLED",n,t,"seconds",round(time.perf_counter()-started,3),flush=True)
        T=arb(t.numerator)/t.denominator
        cT=c_T_enclosure(precision,t.numerator,t.denominator)
        rho=_residual_rho(T,K)
        loss=sum((u.coefficient*compressed_shift_norm_bound(u,precision)
                  for u in inputs["active_terms"]),arb(0))
        mu=_arb_fraction(harmonic(n))-cT-rho-loss
        mu_lo,mu_hi=_pair(mu)
        if mu_lo<=0:
            raise ValueError("no positive conservative complement")
        delta_hi=_upper(inputs["delta_R"])
        norms=inputs["norms"]
        # Approximate eigenvectors are candidate selectors ONLY.
        # Rigorous scalar sign controls are performed separately below.
        a=np.zeros((n,n),dtype=np.float64)
        g=np.zeros((n,n),dtype=np.float64)
        max_a_width=Fraction(0)
        max_g_width=Fraction(0)
        for i in range(n):
            for j in range(i,n):
                ai=inputs["V"][i][j]+inputs["P"][i][j]+inputs["Rk"][i][j]
                if i==j:
                    ai+=_arb_fraction(norms[i])*(_arb_fraction(harmonic(i))-cT)
                gi=inputs["Gk"][i][j]
                al,ah=_pair(ai); gl,gh=_pair(gi)
                max_a_width=max(max_a_width,ah-al)
                max_g_width=max(max_g_width,gh-gl)
                a[i,j]=a[j,i]=float((al+ah)/2)
                g[i,j]=g[j,i]=float((gl+gh)/2)
        di=np.array([float(v) for v in norms])
        scale=np.sqrt(di)
        # Research-only unverified eigenvalue diagnostics in normalized basis.
        s=(a - (1+float(ETA))*g/float(mu_lo))
        s[np.diag_indices(n)]-=(
            float(delta_hi) +
            (1+1/float(ETA))*float(delta_hi)**2/float(mu_lo)
        )*di
        sym=(s/scale[:,None])/scale[None,:]
        eigenvalues,eigenvectors=np.linalg.eigh(sym)
        trial=eigenvectors[:,0]/scale
        # Exact rational candidate direction, rounded from floating proposal.
        coeffs=[Fraction(round(float(v)*(1<<20)),1<<20) for v in trial]
        if not any(coeffs):
            raise RuntimeError("zero proposed rational vector")
        arb_coeffs=[_arb_fraction(c) for c in coeffs]
        norm=arb(0)
        ar=arb(0)
        gr=arb(0)
        for i,ci in enumerate(arb_coeffs):
            if ci==0:continue
            norm+=ci*ci*_arb_fraction(norms[i])
            for j,cj in enumerate(arb_coeffs):
                if cj==0:continue
                aij=inputs["V"][i][j]+inputs["P"][i][j]+inputs["Rk"][i][j]
                if i==j:
                    aij+=_arb_fraction(norms[i])*(_arb_fraction(harmonic(i))-cT)
                ar+=ci*cj*aij
                gr+=ci*cj*inputs["Gk"][i][j]
        norm_lo,norm_hi=_pair(norm)
        # The full low block differs from truncated Rk by at most delta*norm.
        a_full_upper=_upper(ar)+delta_hi*norm_hi
        # Lower full Gram via reverse Young:
        # ||B||^2 >= (1-eta)||Bk||^2 - (eta^-1 -1) delta^2 ||u||^2.
        gram_lower=(1-ETA)*_lower(gr)-(1/ETA-1)*delta_hi**2*norm_hi
        if gram_lower<0:gram_lower=Fraction(0)
        # mu_lo is an independently rigorous admissible *chosen* full-tail bound.
        exact_upper=a_full_upper-gram_lower/mu_lo
        result={
            "format":"sys6-selective-signed-combined-scout-v1",
            "role":"RESEARCH_ONLY_NOT_A_CERTIFICATE",
            "support":f"{t.numerator}/{t.denominator}",
            "dimension":n,"arb_precision_bits":precision,"K":K,
            "eta":f"{ETA.numerator}/{ETA.denominator}",
            "active_terms":[x.m for x in inputs["active_terms"]],
            "source_sha256":{x:hashlib.sha256(Path(x).read_bytes()).hexdigest() for x in SOURCE_PATHS},
            "mu_lower_exact":str(mu_lo),"mu_lower_display":float(mu_lo),
            "delta_upper_exact":str(delta_hi),
            "max_low_entry_width_display":float(max_a_width),
            "max_gram_entry_width_display":float(max_g_width),
            "float_min_normalized_schur_display":float(eigenvalues[0]),
            "float_second_normalized_schur_display":float(eigenvalues[1]),
            "rational_trial_bits":20,
            "trial_rational_vector":[str(x) for x in coeffs],
            "trial_norm_exact_enclosure":[str(norm_lo),str(norm_hi)],
            "a_full_rayleigh_upper_exact":str(a_full_upper),
            "gram_full_rayleigh_lower_exact":str(gram_lower),
            "rigorous_chosen_schur_rayleigh_upper_exact":str(exact_upper),
            "rigorous_chosen_schur_rayleigh_upper_display":float(exact_upper),
            "sign_classification":(
                "CERTIFIED_NEGATIVE_CHOSEN_SUFFICIENT_MATRIX_NOT_WEIL"
                if exact_upper<0 else "NO_DECISIVE_NEGATIVE_DIRECTION"
            ),
            "elapsed_seconds_observational":round(time.perf_counter()-started,3),
            "limitations":"Single-generator Arb source enclosures not independently rederived; "
                          "a negative upper concerns the selected mu-bound Schur matrix "
                          "only. Positive/inconclusive upper gives no theorem."
        }
        return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--support",default="3/5")
    p.add_argument("--dimension",type=int,default=192)
    p.add_argument("--precision",type=int,default=1024)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    t=Fraction(a.support)
    r=run(t,a.dimension,a.precision)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    tmp=a.output.with_suffix(a.output.suffix+".partial")
    tmp.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n",encoding="utf8")
    os.replace(tmp,a.output)
    print("DECISION",r["sign_classification"],
          "FLOAT",r["float_min_normalized_schur_display"],
          "RIGOROUS_UPPER",r["rigorous_chosen_schur_rayleigh_upper_display"],
          "SECONDS",r["elapsed_seconds_observational"],flush=True)


if __name__=="__main__":
    main()
