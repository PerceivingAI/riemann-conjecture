"""SYS-6.2 support-scaling reconnaissance: rigorous scalar budget, no theorem.

The tail/complement formula is mathematically rigorous within the project's
Suzuki/Arb trust model.  Printed floating approximations are only displays.
No matrix is certified or admitted by this script.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx

from scripts.cert.constants import arb_to_rational_enclosure, c_T_enclosure
from scripts.cert.legendre_schur import harmonic
from scripts.cert.multi_prime_legendre_schur import (
    _arb_fraction, _residual_rho, compressed_shift_norm_bound,
)
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms


def rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def scout_support(support: Fraction, dimensions: tuple[int, ...], *,
                  precision: int = 256, order: int = 32) -> dict[str, object]:
    if support <= 0 or precision < 64 or order < 8 or not dimensions or min(dimensions) < 1:
        raise ValueError("invalid support-scaling inputs")
    with ctx.workprec(precision):
        t = arb(support.numerator) / support.denominator
        terms = enumerate_active_prime_power_terms(support.numerator, support.denominator, precision)
        c_t = c_T_enclosure(precision, support.numerator, support.denominator)
        rho = _residual_rho(t, order)
        individual = [term.coefficient * compressed_shift_norm_bound(term, precision)
                      for term in terms]
        total_loss = sum(individual, arb(0))
        scalar_cost = c_t + rho + total_loss
        lo, hi = arb_to_rational_enclosure(scalar_cost)
        if lo > hi:
            raise ValueError("invalid scalar cost interval")
        cutoff = 1
        while harmonic(cutoff) <= hi:
            cutoff += 1
            if cutoff > 100000:
                raise ValueError("cannot bound cutoff")
        values = []
        for n in dimensions:
            mu_lo, mu_hi = arb_to_rational_enclosure(_arb_fraction(harmonic(n)) - scalar_cost)
            values.append({
                "N": n, "mu_certified_positive": mu_lo > 0,
                "mu_certified_negative": mu_hi < 0,
                "mu_lower_decimal_display": float(mu_lo),
                "mu_upper_decimal_display": float(mu_hi),
            })
        return {
            "support": rational(support),
            "active_terms": [int(term.m) for term in terms],
            "prec_bits": precision, "residual_order": order,
            "terms": [{
                "m": int(term.m),
                "coefficient_decimal_display": float(term.coefficient),
                "shift_norm_upper_display": float(compressed_shift_norm_bound(term,precision).upper()),
                "loss_upper_display": float(value.upper()),
            } for term, value in zip(terms, individual)],
            "c_T_upper_display": float(c_t.upper()),
            "rho_R_upper_display": float(rho.upper()),
            "scalar_cost_lower": rational(lo),
            "scalar_cost_upper": rational(hi),
            "scalar_cost_upper_display": float(hi),
            "minimal_N_for_positive_conservative_mu": cutoff,
            "sampled_dimensions": values,
            "role": "rigorous_arb_scalar_complement_only_no_schur_no_theorem",
            "warning": "Decimal displays are approximate; binary decisions come from Arb rational enclosures.",
        }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--supports", default="11/20,3/5,13/20,69/100,7/10")
    p.add_argument("--dimensions", default="96,128,192,256")
    p.add_argument("--precision", type=int, default=256)
    p.add_argument("--order", type=int, default=32)
    p.add_argument("--output-json", type=Path)
    a = p.parse_args()
    supports = tuple(Fraction(x.strip()) for x in a.supports.split(","))
    dimensions = tuple(int(x.strip()) for x in a.dimensions.split(","))
    result = {"format": "sys6-support-scaling-scalar-v1",
              "results": [scout_support(t, dimensions, precision=a.precision, order=a.order)
                          for t in supports]}
    value = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if a.output_json:
        a.output_json.parent.mkdir(parents=True, exist_ok=True)
        a.output_json.write_text(value, encoding="utf8")
    else:
        print(value, end="")


if __name__ == "__main__":
    main()
