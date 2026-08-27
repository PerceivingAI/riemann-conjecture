"""Arb enclosures for exact first-prime Weil constants at T=7/20.

The goal is not to prove the full first-prime positivity theorem. It records
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


def build_payload(prec: int) -> dict[str, object]:
    """Build the diagnostic bundle with scoped Arb precision and checked bounds."""
    if isinstance(prec, bool) or not isinstance(prec, int) or prec < 80:
        raise ValueError("prec must be an integer of at least 80 bits")

    with ctx.workprec(prec):
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
        log2_lo = arb(log2_lo_q.numerator) / log2_lo_q.denominator
        log2_hi = arb(log2_hi_q.numerator) / log2_hi_q.denominator
        tau_lo = log2_lo / T
        tau_hi = log2_hi / T
        sqrt2_lo = arb(7) / 5
        c2_hi = log2_hi / sqrt2_lo

        checks = {
            "log2_lower": bool(log2 > log2_lo),
            "log2_upper": bool(log2 < log2_hi),
            "tau_lower": bool(tau > tau_lo),
            "tau_upper": bool(tau < tau_hi),
            "sqrt2_lower": bool(sqrt2 > sqrt2_lo),
            "c2_upper": bool(c2 < c2_hi),
            "c_T_upper": bool(c_T < cT_upper),
        }
        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            raise RuntimeError(
                "failed to certify advertised rational bounds: " + ", ".join(failed)
            )

        return {
            "precision_bits": prec,
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
                "checks": checks,
            },
            "interpretation": (
                "A rigorous first-prime matrix certificate should propagate these balls "
                "or proven rational enclosures through every tau/c2/c_T-dependent entry."
            ),
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prec", type=int, default=256)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    if args.prec < 80:
        parser.error("prec must be at least 80 bits")

    payload = build_payload(args.prec)
    for key in ("log2", "sqrt2", "tau_exact", "c2_exact", "c_T_exact"):
        print(f"{key}={payload[key]}")
    bounds = payload["certified_rational_bounds"]
    if not isinstance(bounds, dict):
        raise TypeError("invalid certified_rational_bounds payload")
    print("c_T_upper_minus_exact=" + str(bounds["c_T_upper_minus_exact"]))

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"saved_json={args.output_json}")


if __name__ == "__main__":
    main()
