#!/usr/bin/env python3
"""Rigorous-assembly diagnostics for multi-prime continuation screening.

The underlying A/GV/GP/GR/mu objects are assembled with Arb by the generic
multi-prime proof path. Bounds and widths remain exact. Midpoint eigendiagnostics
use power-of-two scaling before binary64 conversion and do not prove positivity.
This module does not construct an exact candidate or grant theorem status.
"""

from __future__ import annotations

from fractions import Fraction

from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.multi_prime_legendre_schur import assemble_multi_prime_schur
from scripts.multi_prime_precision_diagnostics import (
    arb_matrix_exact_width_diagnostics,
    arb_midpoint_fraction,
    scaled_midpoint_eigenvalue,
)
from scripts.precision_diagnostics import arb_width_fraction, fraction_text



def scout_support(
    support: Fraction,
    *,
    dimension: int,
    prec: int,
    residual_order: int,
) -> dict[str, object]:
    assembled = assemble_multi_prime_schur(
        n=dimension,
        prec=prec,
        residual_order=residual_order,
        support_num=support.numerator,
        support_den=support.denominator,
        require_positive_mu=False,
    )
    terms = assembled["active_terms"]
    if not isinstance(terms, tuple):
        raise TypeError("assembler returned malformed active_terms")
    active = [int(term.m) for term in terms]
    if active != [2, 3]:
        raise ValueError(
            f"multi-prime continuation screen requires active set [2, 3], got {active}"
        )

    norms = assembled["norms"]
    if not isinstance(norms, list):
        raise TypeError("assembler returned invalid Legendre norms")

    matrix_diagnostics = {
        name: arb_matrix_exact_width_diagnostics(assembled[name])  # type: ignore[arg-type]
        for name in ("A", "GV", "GP", "GR")
    }
    finite_min, finite_diagnostic = scaled_midpoint_eigenvalue(
        assembled["A"], norms,  # type: ignore[arg-type]
    )
    eigen_diagnostics = {"A": finite_diagnostic}
    mu_mid = arb_midpoint_fraction(assembled["mu"])
    mu_lo, mu_hi = arb_to_rational_enclosure(assembled["mu"])  # type: ignore[arg-type]
    mu_positive = bool(assembled["mu_positive"])
    penalties: dict[str, str | None] | None = None
    schur_min: str | None = None
    if mu_positive:
        schur_min, eigen_diagnostics["schur"] = scaled_midpoint_eigenvalue(
            assembled["schur"], norms,  # type: ignore[arg-type]
        )
        penalties = {}
        for name in ("GV", "GP", "GR"):
            eigenvalue, eigen_diagnostics[name] = scaled_midpoint_eigenvalue(
                assembled[name], norms, largest=True,  # type: ignore[arg-type]
            )
            penalties[name] = (
                fraction_text(3 * Fraction(eigenvalue) / mu_mid)
                if eigenvalue is not None else None
            )
    else:
        eigen_diagnostics["schur"] = {
            "status": "unavailable", "reason": "complement_not_certified_positive",
        }

    return {
        "support": f"{support.numerator}/{support.denominator}",
        "support_decimal": float(support),
        "active_terms": active,
        "mu_lower": fraction_text(mu_lo),
        "mu_midpoint": fraction_text(mu_mid),
        "mu_upper": fraction_text(mu_hi),
        "mu_certified_positive": mu_positive,
        "finite_block_min_eigenvalue_midpoint": finite_min,
        "schur_min_eigenvalue_midpoint": schur_min,
        "component_schur_penalty_operator_norm_midpoint": penalties,
        "midpoint_diagnostics_available": all(
            row["status"] == "available" for row in eigen_diagnostics.values()
        ),
        "midpoint_eigenvalue_diagnostics": eigen_diagnostics,
        "rho_R_upper": fraction_text(
            arb_to_rational_enclosure(assembled["rho_R"])[1],  # type: ignore[arg-type]
        ),
        "residual_remainder_upper": fraction_text(
            arb_to_rational_enclosure(assembled["delta_R"])[1],  # type: ignore[arg-type]
        ),
        "interval_widths": {
            **{f"{name}_max": row["max_width"] for name, row in matrix_diagnostics.items()},
            "mu": fraction_text(arb_width_fraction(assembled["mu"])),
            "rho_R": fraction_text(arb_width_fraction(assembled["rho_R"])),
            "residual_remainder": fraction_text(arb_width_fraction(assembled["delta_R"])),
        },
        "matrix_interval_diagnostics": matrix_diagnostics,
    }
