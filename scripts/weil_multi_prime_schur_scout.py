#!/usr/bin/env python3
"""Floating reconnaissance for the generic multi-prime Legendre-Schur path.

This script is intentionally numerical. It independently builds the active
prime-power translations in ordinary floating point and truncates all tail
Grams at max_mode. Nothing emitted here is proof-bearing. Rigorous Arb assembly
and exact candidate construction live in separate P4 stages.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.linalg import eigvalsh
from scipy.special import eval_legendre, roots_legendre

EULER_GAMMA = 0.577215664901532860606512090082402431


def harmonic(n: int) -> float:
    return sum(1.0 / k for k in range(1, n + 1))


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def _factor_prime_power(m: int) -> tuple[int, int] | None:
    if m < 2:
        return None
    if _is_prime(m):
        return m, 1
    prime = 2 if m % 2 == 0 else None
    if prime is None:
        divisor = 3
        while divisor * divisor <= m:
            if m % divisor == 0:
                prime = divisor
                break
            divisor += 2
    if prime is None:
        return None
    remaining = m
    exponent = 0
    while remaining % prime == 0:
        remaining //= prime
        exponent += 1
    return (prime, exponent) if remaining == 1 else None


def active_prime_power_terms(support: Fraction) -> list[dict[str, float | int]]:
    T = float(support)
    terms: list[dict[str, float | int]] = []
    m = 2
    while math.log(m) < 2.0 * T:
        factorization = _factor_prime_power(m)
        if factorization is not None:
            prime, exponent = factorization
            log_m = math.log(m)
            coefficient = math.log(prime) / math.sqrt(m)
            tau = log_m / T
            chain_vertices = max(1, math.ceil(2.0 / tau))
            norm_bound = 2.0 * math.cos(math.pi / (chain_vertices + 1.0))
            terms.append(
                {
                    "m": m,
                    "prime": prime,
                    "exponent": exponent,
                    "tau": tau,
                    "coefficient": coefficient,
                    "chain_vertices": chain_vertices,
                    "norm_bound": norm_bound,
                    "complement_contribution": coefficient * norm_bound,
                }
            )
        m += 1
    return terms


def _translated_term_matrix(
    max_mode: int,
    shift_order: int,
    tau: float,
    coefficient: float,
) -> np.ndarray:
    if not (0.0 < tau < 2.0):
        raise ValueError("active compressed translation requires 0 < tau < 2")
    z, z_weights = roots_legendre(shift_order)
    lower, upper = -1.0, 1.0 - tau
    t = (lower + upper) / 2.0 + (upper - lower) * z / 2.0
    weights = z_weights * (upper - lower) / 2.0
    base = np.column_stack(
        [math.sqrt((2 * n + 1) / 2) * eval_legendre(n, t) for n in range(max_mode)]
    )
    shifted = np.column_stack(
        [
            math.sqrt((2 * n + 1) / 2) * eval_legendre(n, t + tau)
            for n in range(max_mode)
        ]
    )
    return -coefficient * (
        shifted.T @ (weights[:, None] * base)
        + base.T @ (weights[:, None] * shifted)
    )


def scout(
    max_mode: int,
    quadrature_order: int,
    shift_order: int,
    n_values: list[int],
    support: Fraction = Fraction(3, 5),
) -> dict[str, object]:
    if max_mode < 10:
        raise ValueError("max_mode must be at least 10")
    if quadrature_order < 16 or shift_order < 16:
        raise ValueError("quadrature orders must be at least 16")
    if any(n <= 0 or n >= max_mode for n in n_values):
        raise ValueError("every Schur N must satisfy 0 < N < max_mode")
    if support <= 0:
        raise ValueError("support must be positive")

    T = float(support)
    active_terms = active_prime_power_terms(support)
    if not active_terms:
        raise ValueError("support activates no prime-power translation")

    x, weights = roots_legendre(quadrature_order)
    basis = np.column_stack(
        [math.sqrt((2 * n + 1) / 2) * eval_legendre(n, x) for n in range(max_mode)]
    )

    Vx = -0.5 * np.log(1 - x * x)
    V = basis.T @ ((weights * Vx)[:, None] * basis)

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

    prime_matrices: dict[int, np.ndarray] = {}
    P = np.zeros((max_mode, max_mode), dtype=float)
    for term in active_terms:
        matrix = _translated_term_matrix(
            max_mode,
            shift_order,
            float(term["tau"]),
            float(term["coefficient"]),
        )
        prime_matrices[int(term["m"])] = matrix
        P += matrix

    H = np.array([harmonic(n) for n in range(max_mode)])
    cT = math.log(2 * math.pi * T) + EULER_GAMMA
    A = np.diag(H - cT) + V + P + R

    rho_R_scout = 2.0 * T * float(np.max(np.abs(rpp)))
    arithmetic_loss = sum(float(term["complement_contribution"]) for term in active_terms)
    threshold = cT + arithmetic_loss + rho_R_scout

    rows: list[dict[str, object]] = []
    for N in n_values:
        mu = H[N] - threshold
        component_grams: dict[str, np.ndarray] = {}
        for name, component in (("GV", V), ("GP", P), ("GR", R)):
            tail = component[:N, N:]
            component_grams[name] = tail @ tail.T
        combined_gram = component_grams["GV"] + component_grams["GP"] + component_grams["GR"]
        schur = A[:N, :N] - (3.0 / mu) * combined_gram
        p_low = P[:N, :N]
        singular_values = np.linalg.svd(p_low, compute_uv=False)
        smallest = float(singular_values[-1])
        condition = (
            float(singular_values[0] / smallest)
            if smallest > np.finfo(float).eps * max(1.0, float(singular_values[0]))
            else None
        )
        per_term_tail_norms = {}
        for m, matrix in prime_matrices.items():
            tail = matrix[:N, N:]
            per_term_tail_norms[str(m)] = float(np.linalg.norm(tail, ord=2))
        rows.append(
            {
                "N": N,
                "mu_scout": float(mu),
                "finite_block_min_eigenvalue": float(eigvalsh(A[:N, :N])[0]),
                "factor3_truncated_schur_min_eigenvalue": float(eigvalsh(schur)[0]),
                "component_tail_gram_operator_norms": {
                    name: float(np.linalg.norm(gram, ord=2))
                    for name, gram in component_grams.items()
                },
                "combined_prime_conditioning": {
                    "low_block_operator_norm": float(singular_values[0]),
                    "low_block_smallest_singular_value": smallest,
                    "low_block_condition_number": condition,
                    "per_term_tail_operator_norms": per_term_tail_norms,
                },
            }
        )

    return {
        "role": "floating_reconnaissance_only",
        "warning": (
            "All arithmetic, residual, eigenvalue, conditioning, and tail-Gram "
            "quantities in this file are floating/truncated diagnostics only."
        ),
        "support": f"{support.numerator}/{support.denominator}",
        "support_T": T,
        "active_terms": active_terms,
        "arithmetic_complement_loss_scout": arithmetic_loss,
        "rho_R_scout": rho_R_scout,
        "max_mode": max_mode,
        "quadrature_order": quadrature_order,
        "shift_order": shift_order,
        "lowest_full_finite_ritz_values": [float(value) for value in eigvalsh(A)[:8]],
        "schur_rows": rows,
    }


def parse_n_values(text: str) -> list[int]:
    values = [int(part.strip()) for part in text.split(",") if part.strip()]
    if not values:
        raise ValueError("at least one N is required")
    return values


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
    parser.add_argument("--n", default="40,48,56,64,72,80,96")
    parser.add_argument("--support", default="3/5", help="exact rational support T")
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
