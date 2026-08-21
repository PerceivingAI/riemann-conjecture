"""Arb enclosures for exact first-prime Weil constants at T=7/20.

The goal is not to prove the full first-prime positivity theorem.  It records
outward-rounded balls for the transcendental constants that a rigorous Schur
certificate must use, instead of injecting binary-float point approximations.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx


def ball_text(x: arb, digits: int = 60) -> str:
    return x.str(digits, radius=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prec", type=int, default=256)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    if args.prec < 80:
        raise SystemExit("use at least 80 bits")

    ctx.prec = args.prec
    T = arb(7) / 20
    log2 = arb.const_log2()
    sqrt2 = arb(2).sqrt()
    tau = log2 / T
    c2 = log2 / sqrt2
    c_T = (arb(2) * arb.pi() * T).log() + arb.const_euler()

    # Rational bounds used or advertised by the external first-prime project.
    cT_upper_q = Fraction(1355726, 993009)
    cT_upper = arb(cT_upper_q.numerator) / cT_upper_q.denominator
    log2_lo_q = Fraction(842, 1215)
    log2_hi_q = Fraction(23581, 34020)
    tau_lo = (arb(log2_lo_q.numerator) / log2_lo_q.denominator) / T
    tau_hi = (arb(log2_hi_q.numerator) / log2_hi_q.denominator) / T
    sqrt2_lo = arb(7) / 5
    c2_hi = (arb(log2_hi_q.numerator) / log2_hi_q.denominator) / sqrt2_lo

    payload = {
        "precision_bits": args.prec,
        "T": "7/20",
        "log2": ball_text(log2),
        "sqrt2": ball_text(sqrt2),
        "tau_exact": ball_text(tau),
        "c2_exact": ball_text(c2),
        "c_T_exact": ball_text(c_T),
        "certified_rational_bounds": {
            "tau_lower_from_log2_lower": ball_text(tau_lo),
            "tau_upper_from_log2_upper": ball_text(tau_hi),
            "c2_upper_from_log2_hi_sqrt2_lo": ball_text(c2_hi),
            "c_T_upper_rational": str(cT_upper_q),
            "c_T_upper_minus_exact": ball_text(cT_upper - c_T),
        },
        "interpretation": (
            "A rigorous first-prime matrix certificate should propagate these balls "
            "or proven rational enclosures through every tau/c2/c_T-dependent entry."
        ),
    }

    for key in ("log2", "sqrt2", "tau_exact", "c2_exact", "c_T_exact"):
        print(f"{key}={payload[key]}")
    print("c_T_upper_minus_exact=" + payload["certified_rational_bounds"]["c_T_upper_minus_exact"])

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"saved_json={args.output_json}")


if __name__ == "__main__":
    main()
