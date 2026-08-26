#!/usr/bin/env python3
"""Reconnaissance map for one-prime support continuation after C-0050.

The underlying matrices A, G_V, G_2, G_R and the complement enclosure mu are
assembled with the same exact-polynomial/Arb machinery used by the proof path.
This script then converts matrix midpoints to ordinary floating point only to
rank candidate support values and diagnose which term consumes the Schur
margin. Its eigenvalues and norm diagnostics are reconnaissance, not proofs.

The proof-bearing v1 exact_prime_legendre_schur profile remains locked to
T=7/20. A positive row here does not certify a new support value.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.linalg import eigvalsh

from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.legendre_schur import assemble_exact_prime_schur


def parse_supports(text: str) -> list[Fraction]:
    values: list[Fraction] = []
    for part in text.split(","):
        token = part.strip()
        if not token:
            continue
        value = Fraction(token)
        if value <= 0:
            raise ValueError("support values must be positive")
        values.append(value)
    if not values:
        raise ValueError("at least one support value is required")
    return values


def _arb_mid_float(value: object) -> float:
    # Exact dyadic midpoint extraction, converted to float only for reconnaissance.
    midpoint = value.mid().fmpq()  # type: ignore[attr-defined]
    return float(Fraction(int(midpoint.p), int(midpoint.q)))


def _normalized_midpoint_matrix(matrix: list[list[object]], norms: list[Fraction]) -> np.ndarray:
    n = len(matrix)
    scale = np.array([float(norm) ** -0.5 for norm in norms], dtype=float)
    midpoint = np.array(
        [[_arb_mid_float(matrix[i][j]) for j in range(n)] for i in range(n)],
        dtype=float,
    )
    return (scale[:, None] * midpoint) * scale[None, :]


def _arb_lower_float(value: object) -> float:
    lo, _ = arb_to_rational_enclosure(value)  # type: ignore[arg-type]
    return float(lo)


def _arb_upper_float(value: object) -> float:
    _, hi = arb_to_rational_enclosure(value)  # type: ignore[arg-type]
    return float(hi)


def scout_support(
    support: Fraction,
    *,
    dimension: int,
    prec: int,
    residual_order: int,
) -> dict[str, object]:
    assembled = assemble_exact_prime_schur(
        n=dimension,
        prec=prec,
        residual_order=residual_order,
        support_num=support.numerator,
        support_den=support.denominator,
        require_positive_mu=False,
    )
    norms = assembled["norms"]
    assert isinstance(norms, list)

    a = _normalized_midpoint_matrix(assembled["A"], norms)  # type: ignore[arg-type]
    gv = _normalized_midpoint_matrix(assembled["GV"], norms)  # type: ignore[arg-type]
    g2 = _normalized_midpoint_matrix(assembled["G2"], norms)  # type: ignore[arg-type]
    gr = _normalized_midpoint_matrix(assembled["GR"], norms)  # type: ignore[arg-type]
    mu_mid = _arb_mid_float(assembled["mu"])
    mu_positive = bool(assembled["mu_positive"])
    penalties: dict[str, float] | None = None
    schur_min: float | None = None
    if mu_positive:
        schur = _normalized_midpoint_matrix(assembled["schur"], norms)  # type: ignore[arg-type]
        factor_mid = 3.0 / mu_mid
        penalties = {
            "GV": float(eigvalsh(factor_mid * gv, subset_by_index=[dimension - 1, dimension - 1])[0]),
            "G2": float(eigvalsh(factor_mid * g2, subset_by_index=[dimension - 1, dimension - 1])[0]),
            "GR": float(eigvalsh(factor_mid * gr, subset_by_index=[dimension - 1, dimension - 1])[0]),
        }
        schur_min = float(eigvalsh(schur, subset_by_index=[0, 0])[0])

    return {
        "support": f"{support.numerator}/{support.denominator}",
        "support_decimal": float(support),
        "mu_lower": _arb_lower_float(assembled["mu"]),
        "mu_midpoint": mu_mid,
        "mu_upper": _arb_upper_float(assembled["mu"]),
        "mu_certified_positive": mu_positive,
        "finite_block_min_eigenvalue_midpoint": float(eigvalsh(a, subset_by_index=[0, 0])[0]),
        "schur_min_eigenvalue_midpoint": schur_min,
        "component_schur_penalty_operator_norm_midpoint": penalties,
        "rho_R_upper": _arb_upper_float(assembled["rho_R"]),
        "residual_remainder_upper": _arb_upper_float(assembled["delta_R"]),
    }


def build_scan(
    supports: list[Fraction],
    *,
    dimension: int = 32,
    prec: int = 128,
    residual_order: int = 32,
) -> dict[str, object]:
    rows = [
        scout_support(
            support,
            dimension=dimension,
            prec=prec,
            residual_order=residual_order,
        )
        for support in supports
    ]
    positive = [
        row
        for row in rows
        if row["schur_min_eigenvalue_midpoint"] is not None
        and row["schur_min_eigenvalue_midpoint"] > 0
    ]
    return {
        "role": "reconnaissance_only",
        "warning": (
            "Arb/exact-polynomial assembly is reused, but reported eigenvalues and component norms "
            "are floating midpoint diagnostics. This scan does not prove any new support value; "
            "only separately retained exact certificates accepted by the independent verifier are theorem evidence."
        ),
        "dimension": dimension,
        "precision_bits": prec,
        "residual_order": residual_order,
        "rows": rows,
        "largest_scanned_positive_midpoint_support": (
            positive[-1]["support"] if positive else None
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--supports",
        default="7/20,3/8,2/5,17/40,9/20,19/40,1/2,21/40,27/50",
        help="comma-separated exact rational support values",
    )
    parser.add_argument("--dimension", type=int, default=32)
    parser.add_argument("--prec", type=int, default=128)
    parser.add_argument("--residual-order", type=int, default=32)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    result = build_scan(
        parse_supports(args.supports),
        dimension=args.dimension,
        prec=args.prec,
        residual_order=args.residual_order,
    )
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
