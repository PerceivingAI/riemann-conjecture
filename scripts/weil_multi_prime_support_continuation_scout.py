#!/usr/bin/env python3
"""Rigorous-assembly diagnostics for multi-prime continuation screening.

The underlying A/GV/GP/GR/mu objects are assembled with Arb by the generic
multi-prime proof path. Ordinary floating point is used only on certified Arb
midpoints to rank dimensions and diagnose precision stability. This module does
not construct an exact candidate or grant theorem status.
"""

from __future__ import annotations

from fractions import Fraction

import numpy as np
from scipy.linalg import eigvalsh

from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.multi_prime_legendre_schur import assemble_multi_prime_schur
from scripts.precision_diagnostics import (
    arb_matrix_width_diagnostics,
    arb_midpoint_float,
    arb_width_float,
)


def _normalized_midpoint_matrix(
    matrix: list[list[object]],
    norms: list[Fraction],
) -> np.ndarray:
    n = len(matrix)
    scale = np.array([float(norm) ** -0.5 for norm in norms], dtype=float)
    midpoint = np.array(
        [
            [arb_midpoint_float(matrix[i][j]) for j in range(n)]
            for i in range(n)
        ],
        dtype=float,
    )
    return (scale[:, None] * midpoint) * scale[None, :]


def _arb_lower_float(value: object) -> float:
    lo, _ = arb_to_rational_enclosure(value)  # type: ignore[arg-type]
    return float(lo)


def _arb_upper_float(value: object) -> float:
    _, hi = arb_to_rational_enclosure(value)  # type: ignore[arg-type]
    return float(hi)


def _matrix_max_width(matrix: list[list[object]]) -> float:
    return float(arb_matrix_width_diagnostics(matrix)["max_width"])


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

    a = _normalized_midpoint_matrix(assembled["A"], norms)  # type: ignore[arg-type]
    gv = _normalized_midpoint_matrix(assembled["GV"], norms)  # type: ignore[arg-type]
    gp = _normalized_midpoint_matrix(assembled["GP"], norms)  # type: ignore[arg-type]
    gr = _normalized_midpoint_matrix(assembled["GR"], norms)  # type: ignore[arg-type]
    mu_mid = arb_midpoint_float(assembled["mu"])
    mu_positive = bool(assembled["mu_positive"])

    penalties: dict[str, float] | None = None
    schur_min: float | None = None
    if mu_positive:
        schur = _normalized_midpoint_matrix(assembled["schur"], norms)  # type: ignore[arg-type]
        factor_mid = 3.0 / mu_mid
        penalties = {
            "GV": float(
                eigvalsh(
                    factor_mid * gv,
                    subset_by_index=[dimension - 1, dimension - 1],
                )[0]
            ),
            "GP": float(
                eigvalsh(
                    factor_mid * gp,
                    subset_by_index=[dimension - 1, dimension - 1],
                )[0]
            ),
            "GR": float(
                eigvalsh(
                    factor_mid * gr,
                    subset_by_index=[dimension - 1, dimension - 1],
                )[0]
            ),
        }
        schur_min = float(eigvalsh(schur, subset_by_index=[0, 0])[0])

    return {
        "support": f"{support.numerator}/{support.denominator}",
        "support_decimal": float(support),
        "active_terms": active,
        "mu_lower": _arb_lower_float(assembled["mu"]),
        "mu_midpoint": mu_mid,
        "mu_upper": _arb_upper_float(assembled["mu"]),
        "mu_certified_positive": mu_positive,
        "finite_block_min_eigenvalue_midpoint": float(
            eigvalsh(a, subset_by_index=[0, 0])[0]
        ),
        "schur_min_eigenvalue_midpoint": schur_min,
        "component_schur_penalty_operator_norm_midpoint": penalties,
        "rho_R_upper": _arb_upper_float(assembled["rho_R"]),
        "residual_remainder_upper": _arb_upper_float(assembled["delta_R"]),
        "interval_widths": {
            "A_max": _matrix_max_width(assembled["A"]),  # type: ignore[arg-type]
            "GV_max": _matrix_max_width(assembled["GV"]),  # type: ignore[arg-type]
            "GP_max": _matrix_max_width(assembled["GP"]),  # type: ignore[arg-type]
            "GR_max": _matrix_max_width(assembled["GR"]),  # type: ignore[arg-type]
            "mu": arb_width_float(assembled["mu"]),
            "rho_R": arb_width_float(assembled["rho_R"]),
            "residual_remainder": arb_width_float(assembled["delta_R"]),
        },
        "matrix_interval_diagnostics": {
            "A": arb_matrix_width_diagnostics(assembled["A"]),  # type: ignore[arg-type]
            "GV": arb_matrix_width_diagnostics(assembled["GV"]),  # type: ignore[arg-type]
            "GP": arb_matrix_width_diagnostics(assembled["GP"]),  # type: ignore[arg-type]
            "GR": arb_matrix_width_diagnostics(assembled["GR"]),  # type: ignore[arg-type]
        },
    }
