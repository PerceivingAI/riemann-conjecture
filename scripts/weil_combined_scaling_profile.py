"""Rigorous Arb combined mixed-Gram width and cancellation *reconnaissance*.

This exposes source-enclosed Gram input diagnostics, not a Schur sign theorem:
no new v3 certificate, no Rust production verifier and no theorem admission.
All printed decimals are unverified floating DISPLAY conversions of Arb balls.
"""
from __future__ import annotations

import argparse
import json
import time
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.mixed_gram_research import assemble_truncated_mixed_gram
from scripts.weil_support_scaling_scout import scout_support


def _display(x: arb) -> float:
    a, b = arb_to_rational_enclosure(x)
    return float((a + b) / 2)


def research_profile(support: Fraction, n: int, prec: int, order: int = 32) -> dict:
    if support <= 0 or support >= Fraction(3, 2) or n < 2 or prec < 64 or order < 8:
        raise ValueError("invalid support, dimension, precision or order")
    t0 = time.perf_counter()
    with ctx.workprec(prec):
        r = assemble_truncated_mixed_gram(
            n=n, prec=prec, residual_order=order,
            support_num=support.numerator, support_den=support.denominator,
        )
        elapsed = time.perf_counter() - t0
        if [term.m for term in r["active_terms"]] != [2, 3]:
            raise ValueError("first two-prime profile requires exact active [2,3]")
        v, p, rk = r["V"], r["P"], r["Rk"]
        norms = r["norms"]
        inv = [arb(q.denominator) / q.numerator for q in norms]
        cross_trace = arb(0)
        combined_trace = arb(0)
        diag = {}
        for i in range(n):
            vp = r["VP"][i][i]
            vr = r["VRk"][i][i]
            pr = r["PRk"][i][i]
            projection = sum((
                (v[i][k]*p[k][i] + v[i][k]*rk[k][i] + p[i][k]*rk[k][i])*inv[k]
                for k in range(n)
            ), arb(0))
            cross = 2 * (vp + vr + pr - projection)
            cross_trace += cross * inv[i]
            combined_trace += r["Gk"][i][i] * inv[i]
            if i in (0, 1, 8, 16):
                diag[str(i)] = {
                    "combined_gram_diagonal_display": _display(r["Gk"][i][i]),
                    "mixed_cross_diagonal_display": _display(cross),
                }
        separated_trace = combined_trace - cross_trace
        widths = [arb_to_rational_enclosure(r["Gk"][i][j])
                  for i in range(n) for j in range(i,n)]
        max_width = max((hi-lo for lo, hi in widths), default=Fraction(0))
        budget = scout_support(support,(n,),precision=prec,order=order)
        return {
            "support": f"{support.numerator}/{support.denominator}",
            "n": n, "prec_bits": prec, "order": order,
            "active_terms": [int(t.m) for t in r["active_terms"]],
            "assembly_seconds_display": elapsed,
            "gram_max_width_exact": f"{max_width.numerator}/{max_width.denominator}",
            "gram_max_width_display": float(max_width),
            "delta_R_display": _display(r["delta_R"]),
            "normalized_truncated_combined_gram_trace_display": _display(combined_trace),
            "normalized_truncated_separate_gram_trace_display": _display(separated_trace),
            "normalized_mixed_cross_trace_display": _display(cross_trace),
            "combined_to_separated_trace_ratio_display": (
                _display(combined_trace / separated_trace)
                if separated_trace.is_finite() and not separated_trace.contains(0)
                else None
            ),
            "selected_diagonals":diag,
            "rigorous_complement_positive_at_n": budget["sampled_dimensions"][0]["mu_certified_positive"],
            "rigorous_min_complement_n": budget["minimal_N_for_positive_conservative_mu"],
            "role": "research_only_arb_truncated_image_gram_diagnostics",
            "warning": "Full Suzuki residual remains separately bounded by delta_R. "
                       "No sign test of the full infinite-tail Schur form; "
                       "no new theorem; decimal values are displays, not certificates.",
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supports", default="11/20,3/5,13/20")
    parser.add_argument("--dimension", type=int, default=64)
    parser.add_argument("--precision", type=int, default=384)
    parser.add_argument("--order", type=int, default=32)
    parser.add_argument("--output-json", type=Path, required=True)
    a = parser.parse_args()
    supports = tuple(Fraction(x.strip()) for x in a.supports.split(","))
    rows = []
    for support in supports:
        v = research_profile(support,a.dimension,a.precision,a.order)
        print("COMPLETE",v["support"],"N",a.dimension,
              "secs",round(v["assembly_seconds_display"],2),
              "width",v["gram_max_width_display"],flush=True)
        rows.append(v)
    output = {"format":"sys6-scaling-combined-research-v1","results":rows}
    a.output_json.parent.mkdir(parents=True, exist_ok=True)
    a.output_json.write_text(json.dumps(output,indent=2,allow_nan=False)+"\n",encoding="utf8")


if __name__ == "__main__":
    main()
