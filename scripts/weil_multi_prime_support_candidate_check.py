#!/usr/bin/env python3
"""Generator-side exact candidate check for the generic multi-prime Schur path.

This stage is rigorous on the generator side but is NOT a theorem certificate.
It uses Arb assembly, outward dyadic interval rounding, an exact rational
factor-3 Schur reconstruction from A/GV/GP/GR, and exact rational parity
witnesses. No contract mutation or independent verifier invocation occurs here.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx

from scripts.cert.constants import arb_to_rational_enclosure, c_T_enclosure
from scripts.cert.exact_prime_schur_common import (
    exact_matrix_json,
    coarsen_matrix,
    dyadic_outward_interval,
    force_exact_parity_zeros,
    interval_matrix_json,
    parity_block,
)
from scripts.cert.legendre_schur import harmonic
from scripts.cert.matrices import RationalInterval, RationalIntervalMatrix
from scripts.cert.multi_prime_legendre_schur import assemble_multi_prime_schur
from scripts.cert.multi_prime_exact_witness import make_witness
from scripts.multi_prime_precision_diagnostics import arb_matrix_exact_width_diagnostics
from scripts.precision_diagnostics import (
    arb_width_fraction,
    exact_matrix_width_diagnostics,
    fraction_text,
)
from scripts.audit_multi_prime_candidate import AUDIT_FORMAT, AUDIT_ROLE

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


class CandidateStageError(RuntimeError):
    def __init__(self, stage: str, message: str, *, audit_inputs: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.stage = stage
        self.audit_inputs = audit_inputs


def theorem_boundary_payload() -> dict[str, object]:
    return {
        "theorem_status": THEOREM_STATUS,
        "independently_verified": False,
        "whitelisted": False,
        "automatic_promotion": False,
        "promotion_requirements": list(PROMOTION_REQUIREMENTS),
        "forbidden_automatic_actions": list(FORBIDDEN_AUTOMATIC_ACTIONS),
    }


def _fraction_interval_text(value: arb) -> dict[str, str]:
    lo, hi = arb_to_rational_enclosure(value)
    return {
        "lower": fraction_text(lo),
        "upper": fraction_text(hi),
        "width": fraction_text(hi - lo),
    }


def _matrix_max_width_fraction(matrix: list[list[arb]]) -> Fraction:
    return max(arb_width_fraction(value) for row in matrix for value in row)


def _ratio_text(numerator: Fraction, denominator: Fraction) -> str | None:
    if denominator == 0:
        return None
    return fraction_text(numerator / denominator)


def _exact_multi_prime_schur(
    a_matrix: RationalIntervalMatrix,
    gv: RationalIntervalMatrix,
    gp: RationalIntervalMatrix,
    gr: RationalIntervalMatrix,
    c_t: RationalInterval,
    complement_terms: list[RationalInterval],
    rho_r: RationalInterval,
    dimension: int,
) -> tuple[list[list[RationalInterval]], Fraction]:
    matrices = (a_matrix, gv, gp, gr)
    if dimension < 1 or any(matrix.dim != dimension for matrix in matrices):
        raise ValueError("all serialized matrices must match the positive dimension")
    if not all(matrix.is_symmetric() for matrix in matrices):
        raise ValueError("all serialized matrices must be exactly symmetric")
    arithmetic_upper = sum((term.hi for term in complement_terms), Fraction(0))
    mu_lower = harmonic(dimension) - c_t.hi - arithmetic_upper - rho_r.hi
    if mu_lower <= 0:
        raise RuntimeError("serialized complement lower bound is not positive")
    factor = Fraction(3, 1) / mu_lower
    schur: list[list[RationalInterval]] = []
    for i in range(dimension):
        row: list[RationalInterval] = []
        for j in range(dimension):
            gram = gv.rows[i][j] + gp.rows[i][j] + gr.rows[i][j]
            row.append(a_matrix.rows[i][j] - gram * factor)
        schur.append(row)
    return schur, mu_lower


def _active_term_diagnostics(
    assembled: dict[str, object],
    matrix_bits: int,
) -> tuple[list[dict[str, object]], list[RationalInterval]]:
    terms = assembled["active_terms"]
    bounds = assembled["arithmetic_norm_bounds"]
    if not isinstance(terms, tuple) or not isinstance(bounds, dict):
        raise TypeError("assembler returned malformed active-term diagnostics")
    rows: list[dict[str, object]] = []
    exact_contributions: list[RationalInterval] = []
    for term in terms:
        m = int(term.m)
        bound = bounds[m]
        contribution = term.coefficient * bound
        exact_contribution = dyadic_outward_interval(contribution, matrix_bits)
        exact_contributions.append(exact_contribution)
        rows.append(
            {
                "m": m,
                "prime": int(term.prime),
                "exponent": int(term.exponent),
                "tau": _fraction_interval_text(term.tau),
                "coefficient": _fraction_interval_text(term.coefficient),
                "compressed_shift_norm_bound": _fraction_interval_text(bound),
                "complement_contribution": _fraction_interval_text(contribution),
                "rounded_complement_contribution": {
                    "lower": fraction_text(exact_contribution.lo),
                    "upper": fraction_text(exact_contribution.hi),
                    "width": fraction_text(exact_contribution.hi - exact_contribution.lo),
                },
            }
        )
    return rows, exact_contributions


def _precision_contraction(
    lower: dict[str, object],
    higher: dict[str, object],
    lower_prec: int,
    higher_prec: int,
) -> dict[str, object]:
    matrix_names = ("A", "GV", "GP", "GR", "P", "P_squared")
    contractions: dict[str, object] = {}
    all_nonincreasing = True
    for name in matrix_names:
        low_width = _matrix_max_width_fraction(lower[name])  # type: ignore[arg-type]
        high_width = _matrix_max_width_fraction(higher[name])  # type: ignore[arg-type]
        all_nonincreasing = all_nonincreasing and high_width <= low_width
        contractions[name] = {
            "from_width": fraction_text(low_width),
            "to_width": fraction_text(high_width),
            "ratio": _ratio_text(high_width, low_width),
            "nonincreasing": high_width <= low_width,
        }
    scalar_names = ("mu", "rho_R", "delta_R")
    scalar_rows: dict[str, object] = {}
    for name in scalar_names:
        low_width = arb_width_fraction(lower[name])
        high_width = arb_width_fraction(higher[name])
        all_nonincreasing = all_nonincreasing and high_width <= low_width
        scalar_rows[name] = {
            "from_width": fraction_text(low_width),
            "to_width": fraction_text(high_width),
            "ratio": _ratio_text(high_width, low_width),
            "nonincreasing": high_width <= low_width,
        }
    return {
        "status": "compared",
        "from_precision_bits": lower_prec,
        "to_precision_bits": higher_prec,
        "matrix_width_contraction": contractions,
        "scalar_width_contraction": scalar_rows,
        "all_reported_widths_nonincreasing": all_nonincreasing,
    }


def run_candidate(
    support: Fraction,
    *,
    dimension: int,
    prec: int,
    residual_order: int,
    matrix_bits: int,
    witness_bits: int,
    comparison_prec: int | None = None,
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
    if comparison_prec is not None and not (64 <= comparison_prec < prec):
        raise ValueError("comparison_prec must satisfy 64 <= comparison_prec < prec")

    with ctx.workprec(prec):
        assembled = assemble_multi_prime_schur(
            n=dimension,
            prec=prec,
            residual_order=residual_order,
            support_num=support.numerator,
            support_den=support.denominator,
        )
        active_terms, exact_contributions = _active_term_diagnostics(assembled, matrix_bits)
        matrix_widths = {
            name: arb_matrix_exact_width_diagnostics(assembled[name])  # type: ignore[arg-type]
            for name in ("A", "GV", "GP", "GR", "P", "P_squared")
        }
        p_width = Fraction(matrix_widths["P"]["max_width"])
        p_squared_width = Fraction(matrix_widths["P_squared"]["max_width"])
        gp_width = Fraction(matrix_widths["GP"]["max_width"])
        working_precision_diagnostics = {
            "matrix_widths": matrix_widths,
            "scalar_widths": {
                "mu": fraction_text(arb_width_fraction(assembled["mu"])),
                "rho_R": fraction_text(arb_width_fraction(assembled["rho_R"])),
                "residual_remainder": fraction_text(arb_width_fraction(assembled["delta_R"])),
            },
            "combined_prime_conditioning": {
                "active_term_count": len(active_terms),
                "P_max_width": fraction_text(p_width),
                "P_squared_max_width": fraction_text(p_squared_width),
                "GP_max_width": fraction_text(gp_width),
                "GP_width_over_P_squared_width": _ratio_text(gp_width, p_squared_width),
                "P_squared_width_over_P_width": _ratio_text(p_squared_width, p_width),
            },
        }
        try:
            a = force_exact_parity_zeros(coarsen_matrix(assembled["A"], matrix_bits))  # type: ignore[arg-type]
            gv = force_exact_parity_zeros(coarsen_matrix(assembled["GV"], matrix_bits))  # type: ignore[arg-type]
            gp = force_exact_parity_zeros(coarsen_matrix(assembled["GP"], matrix_bits))  # type: ignore[arg-type]
            gr = force_exact_parity_zeros(coarsen_matrix(assembled["GR"], matrix_bits))  # type: ignore[arg-type]
            c_t = dyadic_outward_interval(
                c_T_enclosure(prec, support.numerator, support.denominator),
                matrix_bits,
            )
            rho_r = dyadic_outward_interval(assembled["rho_R"], matrix_bits)  # type: ignore[arg-type]
            exact_rounding_diagnostics = {
                "matrix_widths": {
                    "A": exact_matrix_width_diagnostics(a),
                    "GV": exact_matrix_width_diagnostics(gv),
                    "GP": exact_matrix_width_diagnostics(gp),
                    "GR": exact_matrix_width_diagnostics(gr),
                },
                "rounding_succeeded": True,
            }
        except (ValueError, RuntimeError, ZeroDivisionError) as exc:
            raise CandidateStageError("rounding", str(exc)) from exc

    try:
        schur, mu_lower = _exact_multi_prime_schur(
            a,
            gv,
            gp,
            gr,
            c_t,
            exact_contributions,
            rho_r,
            dimension,
        )
    except (ValueError, RuntimeError, ZeroDivisionError) as exc:
        raise CandidateStageError("rounding", str(exc)) from exc
    audit_inputs = {
        "format": AUDIT_FORMAT, "role": AUDIT_ROLE, **theorem_boundary_payload(),
        "support": str(support), "dimension": dimension, "precision_bits": prec,
        "residual_order": residual_order, "matrix_bits": matrix_bits, "witness_bits": witness_bits,
        "basis": "unnormalized_legendre_degree_order", "factor": "3",
        "matrices": {name: interval_matrix_json(matrix)
                     for name, matrix in (("A", a), ("GV", gv), ("GP", gp), ("GR", gr))},
        "c_T": {"lower": fraction_text(c_t.lo), "upper": fraction_text(c_t.hi)},
        "rho_R": {"lower": fraction_text(rho_r.lo), "upper": fraction_text(rho_r.hi)},
        "active_terms": active_terms, "mu_lower": fraction_text(mu_lower),
    }
    try:
        even_witness, even_margin = make_witness(parity_block(schur, 0), witness_bits)
        odd_witness, odd_margin = make_witness(parity_block(schur, 1), witness_bits)
    except (ValueError, RuntimeError, ZeroDivisionError) as exc:
        audit_inputs["status"] = "WITNESS_FAILED"
        raise CandidateStageError("witness", str(exc), audit_inputs=audit_inputs) from exc
    audit_inputs.update({
        "status": "CANDIDATE_READY",
        "witnesses": {"even": exact_matrix_json(even_witness), "odd": exact_matrix_json(odd_witness)},
        "even_gershgorin_margin": fraction_text(even_margin),
        "odd_gershgorin_margin": fraction_text(odd_margin),
    })

    precision_contraction: dict[str, object]
    if comparison_prec is None:
        precision_contraction = {
            "status": "not_requested",
            "note": (
                "Supply comparison_prec independently of matrix_bits/witness_bits "
                "to measure Arb interval contraction without changing exact rounding."
            ),
        }
    else:
        with ctx.workprec(comparison_prec):
            comparison = assemble_multi_prime_schur(
                n=dimension,
                prec=comparison_prec,
                residual_order=residual_order,
                support_num=support.numerator,
                support_den=support.denominator,
            )
        precision_contraction = _precision_contraction(
            comparison,
            assembled,
            comparison_prec,
            prec,
        )

    return {
        "role": "generator_side_exact_multi_prime_candidate_only",
        "status": "CANDIDATE_READY",
        "candidate_status": "CANDIDATE_READY",
        **theorem_boundary_payload(),
        "warning": (
            "This exact candidate is pre-theorem generator evidence only. It is "
            "not a serialized theorem certificate and has not been independently verified."
        ),
        "support": f"{support.numerator}/{support.denominator}",
        "dimension": dimension,
        "precision_bits": prec,
        "comparison_precision_bits": comparison_prec,
        "residual_order": residual_order,
        "matrix_bits": matrix_bits,
        "witness_bits": witness_bits,
        "active_terms": active_terms,
        "working_precision_diagnostics": working_precision_diagnostics,
        "exact_rounding_diagnostics": exact_rounding_diagnostics,
        "precision_contraction": precision_contraction,
        "audit_inputs": audit_inputs,
        "mu_lower": fraction_text(mu_lower),
        "even_gershgorin_margin": fraction_text(even_margin),
        "odd_gershgorin_margin": fraction_text(odd_margin),
        "all_margins_positive": mu_lower > 0 and even_margin > 0 and odd_margin > 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--support", default="3/5")
    parser.add_argument("--dimension", type=int, required=True)
    parser.add_argument("--prec", type=int, default=256)
    parser.add_argument("--compare-prec", type=int)
    parser.add_argument("--residual-order", type=int, default=32)
    parser.add_argument("--matrix-bits", type=int, default=72)
    parser.add_argument("--witness-bits", type=int, default=40)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    result = run_candidate(
        Fraction(args.support),
        dimension=args.dimension,
        prec=args.prec,
        comparison_prec=args.compare_prec,
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
