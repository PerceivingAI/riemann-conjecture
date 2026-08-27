"""Exact rational certificate for first-prime endpoint absorption at T=7/20.

This script proves, without floating-point or Arb assumptions, the scalar
inequality used to absorb the first-prime compressed translation into the
endpoint potential V(x)=-1/2 log(1-x^2):

    c_2 / kappa_edge < 31/100,

where

    c_2 = log(2)/sqrt(2),
    tau = log(2)/T,
    epsilon = 2-tau,
    kappa_edge = 1/2 log(1/(2 epsilon)),
    T = 7/20.

The logarithmic inequalities are proved by the exact atanh series

    log x = 2 sum_{k>=0} y^(2k+1)/(2k+1),
    y=(x-1)/(x+1),

with a rational geometric tail bound.  Hence the output is a self-contained
integer/rational certificate, not a decimal consistency check.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def _require(condition: bool, message: str) -> None:
    """Proof-critical check that remains active under Python optimization."""
    if not condition:
        raise RuntimeError(message)


def frac_text(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def log_bounds_atanh(x: Fraction, terms: int) -> tuple[Fraction, Fraction]:
    """Rigorous rational lower/upper bounds for log(x), x>1."""
    if x <= 1 or terms < 1:
        raise ValueError("require x>1 and terms>=1")
    y = (x - 1) / (x + 1)
    partial = Fraction(0)
    for k in range(terms):
        partial += y ** (2 * k + 1) / (2 * k + 1)
    lower = 2 * partial
    # For k>=terms, 1/(2k+1) <= 1/(2*terms+1), so the
    # remaining positive series is bounded by a geometric series in y^2.
    tail = (
        2
        * y ** (2 * terms + 1)
        / (2 * terms + 1)
        / (1 - y * y)
    )
    return lower, lower + tail


def certify() -> dict:
    T = Fraction(7, 20)

    # Convenient rational bracketing targets.  Unlike a decimal check, their
    # validity is proved below from the atanh series itself.
    log2_target_lo = Fraction(842, 1215)
    log2_target_hi = Fraction(23581, 34020)
    log2_lo, log2_hi = log_bounds_atanh(Fraction(2), 4)
    _require(log2_lo > log2_target_lo, "log(2) lower target was not certified")
    _require(log2_hi < log2_target_hi, "log(2) upper target was not certified")

    two_T = 2 * T
    _require(log2_hi < two_T, "first-prime shift overlap was not certified")

    tau_lo = log2_target_lo / T
    epsilon_hi = 2 - tau_lo
    epsilon_bound = Fraction(34, 1701)
    _require(epsilon_hi == epsilon_bound, "epsilon bound identity failed")
    _require(epsilon_bound < Fraction(1, 41), "epsilon upper bound is too large")

    # From epsilon < 34/1701,
    # 1/(2 epsilon) > 1701/68.  Prove log(1701/68)>16/5 by
    # comparison with 87/32: exact integer inequality plus a rigorous
    # atanh-series proof that log(87/32)>1.
    ratio = Fraction(1701, 68)
    bridge = Fraction(87, 32)
    _require(ratio**5 > bridge**16, "bridge power inequality failed")
    bridge_log_lo, bridge_log_hi = log_bounds_atanh(bridge, 5)
    _require(bridge_log_lo > 1, "bridge logarithm lower bound failed")
    # 5 log(ratio) > 16 log(bridge) > 16.
    kappa_edge_lo = Fraction(8, 5)

    # sqrt(2)>7/5 follows by squaring positive rationals.
    sqrt2_lo = Fraction(7, 5)
    _require(sqrt2_lo * sqrt2_lo < 2, "sqrt(2) lower bound failed")
    c2_hi = log2_target_hi / sqrt2_lo
    c2_bound = Fraction(62, 125)
    _require(c2_hi < c2_bound, "c2 upper bound failed")

    ratio_bound = c2_bound / kappa_edge_lo
    _require(ratio_bound == Fraction(31, 100), "absorption ratio identity failed")
    retained_fraction = 1 - ratio_bound
    _require(retained_fraction == Fraction(69, 100), "retained fraction identity failed")

    return {
        "theorem": "first-prime endpoint absorption at T=7/20",
        "arithmetic": "exact Fraction only",
        "T": frac_text(T),
        "log2_series_terms": 4,
        "log2_series_lower": frac_text(log2_lo),
        "log2_series_upper": frac_text(log2_hi),
        "log2_target_lower": frac_text(log2_target_lo),
        "log2_target_upper": frac_text(log2_target_hi),
        "epsilon_upper": frac_text(epsilon_hi),
        "bridge_power_inequality": {
            "left": "(1701/68)^5",
            "right": "(87/32)^16",
            "verified": True,
        },
        "bridge_log_terms": 5,
        "log_87_over_32_lower": frac_text(bridge_log_lo),
        "log_87_over_32_upper": frac_text(bridge_log_hi),
        "kappa_edge_lower": frac_text(kappa_edge_lo),
        "sqrt2_lower": frac_text(sqrt2_lo),
        "c2_upper_intermediate": frac_text(c2_hi),
        "c2_upper": frac_text(c2_bound),
        "c2_over_kappa_upper": frac_text(ratio_bound),
        "retained_V_fraction_lower": frac_text(retained_fraction),
        "conclusion": "V + P_2 >= (69/100) V >= 0",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    result = certify()
    for key, value in result.items():
        if isinstance(value, dict):
            continue
        print(f"{key}={value}")
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"saved_json={args.output_json}")


if __name__ == "__main__":
    main()
