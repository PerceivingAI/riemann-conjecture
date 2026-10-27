"""Research-only scalar controls for the two reference routes; no matrix or admission."""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
from fractions import Fraction as Q
from pathlib import Path
import sys

from flint import acb, arb, ctx
from scripts.cert.constants import arb_to_rational_enclosure

sys.set_int_max_str_digits(0)


def ball(q):
    q = Q(q)
    return arb(q.numerator) / q.denominator


def interval(x):
    lo, hi = arb_to_rational_enclosure(x)
    magnitude = max(abs(lo), abs(hi))
    exponent = magnitude.numerator.bit_length() - magnitude.denominator.bit_length() if magnitude else 0
    scale = 1 << max(0, 128 - exponent)
    lower = Q(lo.numerator * scale // lo.denominator, scale)
    upper = Q(-((-hi.numerator * scale) // hi.denominator), scale)
    return {"lower": str(lower), "upper": str(upper), "display": x.str(16)}


def exact(q):
    q = Q(q)
    return {"exact": str(q), "log10_abs_display": math.log10(abs(q.numerator)) - math.log10(q.denominator) if q else None}


def legendre_tail(c, n):
    c = Q(c)
    ratio = c*c / ((2*n+1)*(2*n+3))
    if not (0 <= ratio < 1):
        raise ValueError("Legendre geometric majorant ratio must be below one")
    odd_product = math.prod(range(1, 2*n+2, 2))
    return Q(2*n+1) * c**(2*n) / odd_product**2 / (1-ratio)


def bump_gap_upper(c, p):
    # Upper bound on the optimal exterior mass, never a lower certificate.
    return Q(math.factorial(p)**2 * math.factorial(4*p+1),
             2**(2*p)*(2*p+1)*math.factorial(2*p)**2) / c**(2*p)


def archimedean(t):
    return acb(arb(1)/4, ball(t)/2).digamma().real - arb.pi().log()


def independent_digamma_enclosure(t, length):
    # DLMF5.7.6; the tail need not be positive. Pay both signed tail bounds.
    y = ball(t)/2
    subtotal = sum((arb(1)/(k+1) - (arb(k)+arb(1)/4)/((arb(k)+arb(1)/4)**2+y*y)
                    for k in range(length)), arb(0))
    base = -arb.const_euler() - arb.pi().log() + subtotal
    q = ball(Q(length)-Q(3,4))
    return base-3/(4*q), base+y*y/(2*q*q)


def kernel_controls(t, length):
    t = ball(t)
    if t == 0:
        return {"t": "0", "g_exact": "1/4", "g_prime_exact": "-1/48", "g_second_exact": "-1/16"}
    w = (-2*t).exp()
    base = (-t/2).exp()/(1-w)
    slope = -arb(1)/2-2*w/(1-w)
    direct = (base-1/(2*t), base*slope+1/(2*t*t),
              base*(slope*slope+4*w/(1-w)**2)-1/t**3)
    sech = 1/(t/2).cosh()
    tanh = (t/2).tanh()
    partial = [sech/4, -sech*tanh/8, sech*(2*tanh*tanh-1)/16]
    for k in range(1, length+1):
        a2 = (2*arb.pi()*k)**2
        denominator = t*t+a2
        sign = (-1)**k
        partial[0] += sign*t/denominator
        partial[1] += sign*(a2-t*t)/denominator**2
        partial[2] += sign*2*t*(t*t-3*a2)/denominator**3
    errors = [t/(t*t+(2*arb.pi()*(length+1))**2),
              1/(4*arb.pi()**2*length), 3/(16*arb.pi()**3*length**2)]
    checks = []
    for name, actual, approximation, error in zip(("g", "g_prime", "g_second"), direct, partial, errors):
        margin = error-abs(actual-approximation)
        if not margin > 0:
            raise ValueError("partial-fraction corroboration failed: "+name)
        checks.append({"quantity": name, "direct": interval(actual),
                       "partial_fraction_sum": interval(approximation),
                       "error_allowance": interval(error), "strict_overlap_margin": interval(margin)})
    if not abs(direct[1]) < ball(Q(5,48)) or not abs(direct[2]) < ball(Q(23,288)):
        raise ValueError("point control exceeds the proved uniform derivative bound")
    return {"t": t.str(16), "series_terms": length, "checks": checks}


def compute(inputs):
    ctx.prec = 512
    omega, a = Q(256), Q(7,2)
    endpoint = archimedean(omega)
    lower_series, upper_series = independent_digamma_enclosure(omega, 4096)
    if not lower_series < endpoint < upper_series or not lower_series-ball(a) > 0:
        raise ValueError("independent archimedean lower bound did not qualify the exterior")
    p = arb(2).log()/arb(2).sqrt()+arb(3).log()/arb(3).sqrt()
    m = ball(a)-p
    if not m > 2:
        raise ValueError("first-window bounded arithmetic reference lost strict coercivity")
    a0 = archimedean(0)
    width = max(abs(a0-ball(a)), abs(endpoint-ball(a)))
    cases = []
    for support in (Q(3,5), Q(1353,2048)):
        c = support*omega
        bump_degree = c.numerator//(2*c.denominator)
        gap = bump_gap_upper(c, bump_degree)
        if not 0 < gap < 1:
            raise ValueError("bump upper control must be strictly between zero and one")
        rows = []
        for n in (192,312):
            plane = legendre_tail(c,n)
            small_plane = min(Q(1),plane)
            beta = 2*ball(c)/arb.pi()
            pole = 4*ball(support)*ball(support).exp()*ball(legendre_tail(support/2,n))
            compact = width*beta*ball(small_plane)+pole
            compact_cross = width*(beta*ball(small_plane)).sqrt()+pole.sqrt()*(4*ball(support)*ball(support).exp()).sqrt()
            # Cross-pole estimate here is the independently qualified 4T exp(T) sqrt(E).
            tail_margin = m-compact
            rows.append({"dimension": n, "plane_tail_majorant": exact(plane),
                         "band_weight_W": interval(width), "band_trace_beta": interval(beta),
                         "compact_double_tail_upper": interval(compact),
                         "compact_cross_upper": interval(compact_cross),
                         "bounded_reference_tail_margin": interval(tail_margin),
                         "strict_tail_positive": bool(tail_margin>0)})
        cases.append({"support": str(support), "active_terms": [2,3], "a": str(a), "omega": str(omega),
                      "bump_degree": bump_degree, "optimal_exterior_mass_upper_only": exact(gap), "rows": rows})
    physical = []
    for support in (Q(1353,2048),Q(2)):
        t = ball(support)
        constant = Q(11,24)*support**2+Q(23,144)*support**3
        for n in (20,312):
            plane = ball(legendre_tail(support/2,n))
            smooth = ball(constant)/ (n*(n+1))
            double = smooth+4*t*t.exp()*plane
            one = smooth+4*(t*t.exp()*t.sinh()*plane).sqrt()
            physical.append({"support": str(support), "dimension": n,
                             "C_exact": str(constant), "double_tail_upper": interval(double),
                             "one_sided_tail_upper": interval(one), "past_local_Taylor_radius": bool(2*t>arb.pi())})
    local = Q(inputs["retained_local_double_tail_upper"])
    current = next(row for row in physical if row["support"]=="1353/2048" and row["dimension"]==312)
    current["ratio_to_retained_local_upper"] = interval(ball(Q(current["double_tail_upper"]["upper"])/local))
    return {"format": "reference-route-scalar-controls-v1", "scope": "analytical constants only; no low matrix, positivity theorem or admission",
            "precision_bits": 512, "archimedean_endpoint": interval(endpoint),
            "independent_endpoint_lower": interval(lower_series), "independent_endpoint_upper": interval(upper_series),
            "exterior_weight_lower_from_series": interval(lower_series-ball(a)),
            "arithmetic_norm_allowance_first_window": interval(p), "arithmetic_coercivity_lower": interval(m),
            "arithmetic_base_scalar_Schur_lower": interval(m-p*p/m),
            "fourier_cases": cases, "physical_rows": physical,
            "kernel_point_controls": [kernel_controls(t,32) for t in (Q(0),Q(1,2),Q(1),Q(4))],
            "retained_local_comparison_input": inputs,
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "rounding_helper_sha256": hashlib.sha256(Path(inspect.getfile(arb_to_rational_enclosure)).read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    result = compute(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"scope":result["scope"],"fourier_N312_tail_positive":[c["rows"][1]["strict_tail_positive"] for c in result["fourier_cases"]],
                      "kernel_controls":len(result["kernel_point_controls"]),"admission_changed":False}))
