#!/usr/bin/env python3
"""Generator-side exact candidate check for a new one-prime support value.

This is deliberately NOT a theorem certificate. It reuses the rigorous Arb
assembler, outward-rounds all finite matrices to exact dyadic rational
intervals, derives the same factor-3 Schur matrix used by C-0050, and searches
for exact rational parity congruence witnesses. The current independent Rust
profile is locked to T=7/20, so a PASS here is only a strong candidate for the
next certificate slice.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from flint import ctx

from scripts.cert.constants import c2_enclosure, c_T_enclosure
from scripts.cert.exact_prime_schur_certificate import (
    _coarsen_matrix,
    _dyadic_outward_interval,
    _force_exact_parity_zeros,
    _make_witness,
    _parity_block,
    _schur_from_serialized_inputs,
)
from scripts.cert.legendre_schur import assemble_exact_prime_schur


def run_candidate(
    support: Fraction,
    *,
    dimension: int,
    prec: int,
    residual_order: int,
    matrix_bits: int,
    witness_bits: int,
) -> dict[str, object]:
    with ctx.workprec(prec):
        assembled = assemble_exact_prime_schur(
            n=dimension,
            prec=prec,
            residual_order=residual_order,
            support_num=support.numerator,
            support_den=support.denominator,
        )
        a = _force_exact_parity_zeros(_coarsen_matrix(assembled["A"], matrix_bits))
        gv = _force_exact_parity_zeros(_coarsen_matrix(assembled["GV"], matrix_bits))
        g2 = _force_exact_parity_zeros(_coarsen_matrix(assembled["G2"], matrix_bits))
        gr = _force_exact_parity_zeros(_coarsen_matrix(assembled["GR"], matrix_bits))
        c_t = _dyadic_outward_interval(
            c_T_enclosure(prec, support.numerator, support.denominator),
            matrix_bits,
        )
        c2 = _dyadic_outward_interval(c2_enclosure(prec), matrix_bits)
        rho_r = _dyadic_outward_interval(assembled["rho_R"], matrix_bits)

    schur, mu_lower = _schur_from_serialized_inputs(
        a,
        gv,
        g2,
        gr,
        c_t,
        c2,
        rho_r,
        dimension,
    )
    _, even_margin = _make_witness(_parity_block(schur, 0), witness_bits)
    _, odd_margin = _make_witness(_parity_block(schur, 1), witness_bits)
    return {
        "role": "generator_side_exact_candidate_only",
        "warning": (
            "This generator-side check is not independently verified and is not accepted as a theorem by itself. "
            "A support/dimension pair gains theorem status only after it is explicitly whitelisted by the closed contract and the retained full certificate passes the independent Rust verifier."
        ),
        "support": f"{support.numerator}/{support.denominator}",
        "dimension": dimension,
        "precision_bits": prec,
        "residual_order": residual_order,
        "matrix_bits": matrix_bits,
        "witness_bits": witness_bits,
        "mu_lower": f"{mu_lower.numerator}/{mu_lower.denominator}",
        "even_gershgorin_margin": f"{even_margin.numerator}/{even_margin.denominator}",
        "odd_gershgorin_margin": f"{odd_margin.numerator}/{odd_margin.denominator}",
        "all_margins_positive": mu_lower > 0 and even_margin > 0 and odd_margin > 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--support", default="2/5")
    parser.add_argument("--dimension", type=int, default=40)
    parser.add_argument("--prec", type=int, default=256)
    parser.add_argument("--residual-order", type=int, default=32)
    parser.add_argument("--matrix-bits", type=int, default=72)
    parser.add_argument("--witness-bits", type=int, default=40)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    result = run_candidate(
        Fraction(args.support),
        dimension=args.dimension,
        prec=args.prec,
        residual_order=args.residual_order,
        matrix_bits=args.matrix_bits,
        witness_bits=args.witness_bits,
    )
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
