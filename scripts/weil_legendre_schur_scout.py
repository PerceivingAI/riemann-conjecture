#!/usr/bin/env python3
"""Floating reconnaissance for the A-20260821-004 Legendre-Schur reduction.

This script intentionally uses NumPy/SciPy floating point to choose a plausible
finite Legendre dimension. It is NOT a proof tool. In particular, its tail
Gram matrices are truncated at ``max_mode`` and therefore are not rigorous
upper bounds for the infinite complement.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from math import log, sqrt
from pathlib import Path

import numpy as np
from scipy.linalg import eigvalsh
from scipy.special import eval_legendre, roots_legendre

from scripts.cert.constants import require_one_prime_support

EULER_GAMMA = 0.577215664901532860606512090082402431


def harmonic(n: int) -> float:
    return sum(1.0 / k for k in range(1, n + 1))


def scout(
    max_mode: int,
    quadrature_order: int,
    shift_order: int,
    n_values: list[int],
    support: Fraction = Fraction(7, 20),
) -> dict[str, object]:
    if max_mode < 10:
        raise ValueError("max_mode must be at least 10")
    if any(n <= 0 or n >= max_mode for n in n_values):
        raise ValueError("every Schur N must satisfy 0 < N < max_mode")

    require_one_prime_support(support.numerator, support.denominator)
    T = float(support)
    tau = log(2) / T
    x, weights = roots_legendre(quadrature_order)
    basis = np.column_stack(
        [sqrt((2 * n + 1) / 2) * eval_legendre(n, x) for n in range(max_mode)]
    )

    # Endpoint multiplication V(x)=-1/2 log(1-x^2).
    Vx = -0.5 * np.log(1 - x * x)
    V = basis.T @ ((weights * Vx)[:, None] * basis)

    # Suzuki residual kernel in the exact v2 normalization, evaluated here in floats.
    distances = np.abs(x[:, None] - x[None, :]) * T
    rpp = np.empty_like(distances)
    near_zero = distances < 1e-8
    rpp[near_zero] = -7.0 / 4.0
    u = distances[~near_zero]
    rpp[~near_zero] = (
        -(np.exp(u / 2) + np.exp(-u / 2))
        + np.exp(-u / 2) / (1 - np.exp(-2 * u))
        - 1 / (2 * u)
    )
    residual_kernel = -T * rpp
    R = basis.T @ (weights[:, None] * (residual_kernel * weights[None, :])) @ basis

    # Exact-p=2 compressed translation, numerically integrated on its overlap.
    c2 = log(2) / sqrt(2)
    lower, upper = -1.0, 1.0 - tau
    z, z_weights = roots_legendre(shift_order)
    t = (lower + upper) / 2 + (upper - lower) * z / 2
    shift_weights = z_weights * (upper - lower) / 2
    basis_t = np.column_stack(
        [sqrt((2 * n + 1) / 2) * eval_legendre(n, t) for n in range(max_mode)]
    )
    basis_shifted = np.column_stack(
        [
            sqrt((2 * n + 1) / 2) * eval_legendre(n, t + tau)
            for n in range(max_mode)
        ]
    )
    P2 = -c2 * (
        basis_shifted.T @ (shift_weights[:, None] * basis_t)
        + basis_t.T @ (shift_weights[:, None] * basis_shifted)
    )

    H = np.array([harmonic(n) for n in range(max_mode)])
    cT = log(2 * np.pi * T) + EULER_GAMMA
    A = np.diag(H - cT) + V + P2 + R

    # Reconnaissance Schur bound for the residual norm at this support. The
    # same r'' grid used above is sampled; this is not a rigorous supremum.
    rho_R_scout = 2.0 * T * float(np.max(np.abs(rpp)))
    threshold = cT + c2 + rho_R_scout

    lowest_full_ritz = eigvalsh(A)[:8]
    rows: list[dict[str, object]] = []
    for N in n_values:
        mu = H[N] - threshold
        component_gram = np.zeros((N, N))
        for component in (V, P2, R):
            tail = component[:N, N:]
            component_gram += tail @ tail.T
        factor3_schur = A[:N, :N] - (3.0 / mu) * component_gram
        rows.append(
            {
                "N": N,
                "mu_scout": mu,
                "finite_block_min_eigenvalue": float(eigvalsh(A[:N, :N])[0]),
                "factor3_truncated_schur_min_eigenvalue": float(eigvalsh(factor3_schur)[0]),
            }
        )

    return {
        "role": "floating_reconnaissance_only",
        "warning": "Tail Grams are truncated at max_mode and are not infinite-dimensional bounds.",
        "support": f"{support.numerator}/{support.denominator}",
        "support_T": T,
        "rho_R_scout": rho_R_scout,
        "max_mode": max_mode,
        "quadrature_order": quadrature_order,
        "shift_order": shift_order,
        "lowest_full_finite_ritz_values": [float(value) for value in lowest_full_ritz],
        "schur_rows": rows,
    }


def parse_n_values(text: str) -> list[int]:
    return [int(part.strip()) for part in text.split(",") if part.strip()]


def parse_support(text: str) -> Fraction:
    value = Fraction(text.strip())
    if value <= 0:
        raise ValueError("support must be positive")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-mode", type=int, default=120)
    parser.add_argument("--quadrature-order", type=int, default=700)
    parser.add_argument("--shift-order", type=int, default=350)
    parser.add_argument("--n", default="18,20,22,24,28,32,40,50")
    parser.add_argument("--support", default="7/20", help="exact rational support T")
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    result = scout(
        max_mode=args.max_mode,
        quadrature_order=args.quadrature_order,
        shift_order=args.shift_order,
        n_values=parse_n_values(args.n),
        support=parse_support(args.support),
    )
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
