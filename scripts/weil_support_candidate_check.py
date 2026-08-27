#!/usr/bin/env python3
"""Generator-side exact candidate check for a new one-prime support value.

This is deliberately NOT a theorem certificate. It reuses the rigorous Arb
assembler, outward-rounds all finite matrices to exact dyadic rational
intervals, derives the same factor-3 Schur matrix used by C-0050, and searches
for exact rational parity congruence witnesses. The closed v1 contract currently
admits exactly (T,N)=(7/20,32), (2/5,40), (17/40,48), and (9/20,56), so a PASS
for another pair is only a strong candidate for a future certificate slice.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from flint import ctx

from scripts.cert.constants import c2_enclosure, c_T_enclosure
from scripts.cert.exact_prime_schur_common import (
    coarsen_matrix,
    dyadic_outward_interval,
    force_exact_parity_zeros,
    make_witness,
    parity_block,
    schur_from_serialized_inputs,
)
from scripts.cert.legendre_schur import assemble_exact_prime_schur


THEOREM_STATUS = False
PROMOTION_REQUIREMENTS = (
    "explicit_closed_contract_admission",
    "retained_full_certificate_generation",
    "fresh_independent_rust_verifier_pass",
)
FORBIDDEN_AUTOMATIC_ACTIONS = (
    "emit_theorem_certificate",
    "edit_closed_contract_or_whitelist",
    "invoke_independent_rust_verifier",
    "grant_theorem_status",
)


def theorem_boundary_payload() -> dict[str, object]:
    """Return the hard P7 boundary attached to every pre-theorem candidate."""
    return {
        "theorem_status": THEOREM_STATUS,
        "independently_verified": False,
        "whitelisted": False,
        "automatic_promotion": False,
        "promotion_requirements": list(PROMOTION_REQUIREMENTS),
        "forbidden_automatic_actions": list(FORBIDDEN_AUTOMATIC_ACTIONS),
    }


class CandidateStageError(RuntimeError):
    """Structured pre-theorem candidate failure with an explicit stage."""

    def __init__(self, stage: str, message: str) -> None:
        super().__init__(message)
        self.stage = stage


def run_candidate(
    support: Fraction,
    *,
    dimension: int,
    prec: int,
    residual_order: int,
    matrix_bits: int,
    witness_bits: int,
) -> dict[str, object]:
    if dimension < 1:
        raise ValueError("dimension must be positive")
    if prec < 64:
        raise ValueError("prec must be at least 64 bits")
    if residual_order < 8:
        raise ValueError("residual_order must be at least 8")
    if matrix_bits < 16:
        raise ValueError("matrix_bits must be at least 16")
    if witness_bits < 8:
        raise ValueError("witness_bits must be at least 8")

    with ctx.workprec(prec):
        assembled = assemble_exact_prime_schur(
            n=dimension,
            prec=prec,
            residual_order=residual_order,
            support_num=support.numerator,
            support_den=support.denominator,
        )
        try:
            a = force_exact_parity_zeros(coarsen_matrix(assembled["A"], matrix_bits))
            gv = force_exact_parity_zeros(coarsen_matrix(assembled["GV"], matrix_bits))
            g2 = force_exact_parity_zeros(coarsen_matrix(assembled["G2"], matrix_bits))
            gr = force_exact_parity_zeros(coarsen_matrix(assembled["GR"], matrix_bits))
            c_t = dyadic_outward_interval(
                c_T_enclosure(prec, support.numerator, support.denominator),
                matrix_bits,
            )
            c2 = dyadic_outward_interval(c2_enclosure(prec), matrix_bits)
            rho_r = dyadic_outward_interval(assembled["rho_R"], matrix_bits)
        except (ValueError, RuntimeError, ZeroDivisionError) as exc:
            raise CandidateStageError("rounding", str(exc)) from exc

    try:
        schur, mu_lower = schur_from_serialized_inputs(
            a,
            gv,
            g2,
            gr,
            c_t,
            c2,
            rho_r,
            dimension,
        )
    except (ValueError, RuntimeError, ZeroDivisionError) as exc:
        raise CandidateStageError("rounding", str(exc)) from exc
    try:
        _, even_margin = make_witness(parity_block(schur, 0), witness_bits)
        _, odd_margin = make_witness(parity_block(schur, 1), witness_bits)
    except (ValueError, RuntimeError, ZeroDivisionError) as exc:
        raise CandidateStageError("witness", str(exc)) from exc
    return {
        "role": "generator_side_exact_candidate_only",
        "status": "CANDIDATE_READY",
        "candidate_status": "CANDIDATE_READY",
        **theorem_boundary_payload(),
        "warning": (
            "Candidate is generator-side evidence only. No theorem status is granted until the pair is separately admitted to the closed verifier contract and independently replayed."
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
