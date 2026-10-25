"""Research-only C-0088 residual compression and scalar cutoffs at the C-0087 support.

This evaluates no low Schur matrix and changes no certificate/admission contract.
The bound is for Q_N R_T Q_N, not Q_N R_T P_N. See F-20261024-007.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
from typing import Sequence

from flint import acb, arb, ctx

from scripts.cert.constants import arb_to_rational_enclosure, c_T_enclosure
from scripts.cert.multi_prime_legendre_schur import _residual_rho, compressed_shift_norm_bound
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms
from scripts.cert.residual_kernel import (
    _suzuki_residual_series_coefficients,
    _suzuki_residual_tail_radius,
)

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "computations/2026-10-24T191616Z-weighted-support-extension/data/selection-v1.json"
BASELINE_SHA256 = "e120acab4919b9ab28e6fd6c7044053bb14514f300d810952a2d52e5dae6d7a3"
SOURCE_PATHS = (
    "scripts/weil_residual_tail_bound.py",
    "scripts/cert/constants.py",
    "scripts/cert/multi_prime_legendre_schur.py",
    "scripts/cert/prime_power_terms.py",
    "scripts/cert/residual_kernel.py",
)


def tail_constant(coefficients: Sequence[Q], dimension: int) -> Q:
    """Bound ||L F_N|| after removing only even polynomial degrees below 2N.

    Coefficients multiply |x-y|^d, not the unscaled Suzuki Taylor series.
    The degree-one cusp multiplication is included in the factor six.
    """
    if type(dimension) is not int or dimension < 1:
        raise ValueError("dimension must be a positive integer")
    total = 6 * abs(coefficients[1]) if len(coefficients) > 1 else Q(0)
    for degree in range(2, len(coefficients)):
        if degree % 2 or degree >= 2 * dimension:
            total += 2 ** (degree - 1) * (degree + 4) * abs(coefficients[degree])
    return total


def outward(value: arb, bits: int = 352) -> list[str]:
    lower, upper = arb_to_rational_enclosure(value)
    scale = 1 << bits
    lo = (lower.numerator * scale) // lower.denominator
    hi = -((-upper.numerator * scale) // upper.denominator)
    return [str(Q(lo, scale)), str(Q(hi, scale))]


def assess(coefficients: Sequence[Q], scalars: dict[str, list[str]], reserve: Q,
           current_dimension: int) -> dict:
    """First sufficient scalar cutoffs for the published rational upper charges."""
    cost = Q(scalars["c_T"][1]) + Q(scalars["arithmetic"][1])
    delta, full = Q(scalars["delta"][1]), Q(scalars["rho_global"][1])
    cutoffs: dict[str, int] = {}
    harmonic = Q(0)
    rows = []
    dimension = 0
    while len(cutoffs) < 8 or dimension < current_dimension:
        dimension += 1
        harmonic += Q(1, dimension)
        constant = tail_constant(coefficients, dimension)
        tail = delta + constant / (dimension * (dimension + 1))
        mu_global, mu_tail = harmonic - cost - full, harmonic - cost - tail
        for name, mu in (("global", mu_global), ("tail", mu_tail)):
            for target, accepted in (("positive", mu > 0), ("reserve", mu >= reserve)):
                key = f"{name}_{target}"
                if accepted:
                    cutoffs.setdefault(key, dimension)
                    if dimension % 2 == 0:
                        cutoffs.setdefault(key + "_even", dimension)
        rows.append({
            "dimension": dimension, "M_exact": str(constant),
            "rho_tail_upper_exact": str(tail),
            "mu_global_lower_exact": str(mu_global), "mu_tail_lower_exact": str(mu_tail),
        })
    selected = {current_dimension}
    for value in cutoffs.values():
        selected.update((max(1, value - 1), value))
    return {"cutoffs": cutoffs, "rows": [row for row in rows if row["dimension"] in selected]}


def evaluate() -> dict:
    raw = (ROOT / BASELINE).read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASELINE_SHA256:
        raise ValueError("retained baseline bytes changed")
    baseline = json.loads(raw)
    if (baseline["support"], baseline["dimension"], baseline["residual_order"]) != ([1353, 2048], 312, 38):
        raise ValueError("unexpected retained baseline parameters")
    support = Q(*baseline["support"])
    order = baseline["residual_order"]
    coefficients = [
        -Q(int(c.p), int(c.q)) * support ** (degree + 1)
        for degree, c in enumerate(_suzuki_residual_series_coefficients(order))
    ]
    with ctx.workprec(512):
        t = arb(support.numerator) / support.denominator
        if not (arb(3).log() < 2*t < arb(4).log() and 2*t < arb.pi()):
            raise ValueError("current strict support window not certified")
        terms = enumerate_active_prime_power_terms(support.numerator, support.denominator, 512)
        if [term.m for term in terms] != [2, 3] or not all(1 < term.tau < 2 for term in terms):
            raise ValueError("current arithmetic norm-one window not certified")
        arithmetic = sum((term.coefficient * compressed_shift_norm_bound(term, 512) for term in terms), arb(0))
        scalars = {
            "c_T": outward(c_T_enclosure(512, support.numerator, support.denominator)),
            "arithmetic": outward(arithmetic),
            "delta": outward(2*t*_suzuki_residual_tail_radius(acb(2*t), order)),
            "rho_global": outward(_residual_rho(t, order)),
        }
    reserve = Q(baseline["mu_reference_exact"])
    result = {
        "format": "research-residual-tail-scalar-v1",
        "scope": "scalar tail bounds only; no low-block positivity or theorem admission",
        "support": baseline["support"], "residual_order": order,
        "current_dimension": baseline["dimension"], "active_terms": [2, 3],
        "arb_precision_bits": 512, "outward_bits": 352,
        "baseline_path": BASELINE, "baseline_sha256": BASELINE_SHA256,
        "reserve_exact": str(reserve), "kernel_coefficients_exact": list(map(str, coefficients)),
        "scalars": scalars,
        "sources": {path: hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in SOURCE_PATHS},
    }
    result.update(assess(coefficients, scalars, reserve, baseline["dimension"]))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "cutoffs": result["cutoffs"]}, indent=2))


if __name__ == "__main__":
    main()
