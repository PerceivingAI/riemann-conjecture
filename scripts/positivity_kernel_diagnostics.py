"""Diagnostics for A-20260821-002: Li Gram/CND kernels and prime-atom sign structure.

This script is diagnostic only. It checks finite synthetic zero-orbit examples and
the deterministic sign structure of the generalized prime contribution. It does
not use numerical zeta zeros and does not prove any RH statement.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


def laguerre_l1(degree: int, x: float) -> float:
    """Evaluate L_degree^(1)(x) by the three-term recurrence."""
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if degree == 0:
        return 1.0
    l0 = 1.0
    l1 = 2.0 - x
    if degree == 1:
        return l1
    for k in range(1, degree):
        # (k+1)L_{k+1}^{(a)}=(2k+a+1-x)L_k^{(a)}-(k+a)L_{k-1}^{(a)}, a=1
        l2 = ((2.0 * k + 2.0 - x) * l1 - (k + 1.0) * l0) / (k + 1.0)
        l0, l1 = l1, l2
    return l1


def unit_circle_pair_lambdas(theta: float, n_max: int) -> list[float]:
    return [0.0] + [2.0 - 2.0 * math.cos(n * theta) for n in range(1, n_max + 1)]


def offline_quartet_lambdas(r: float, theta: float, n_max: int) -> list[float]:
    return [0.0] + [
        4.0 - 2.0 * (r**n + r ** (-n)) * math.cos(n * theta)
        for n in range(1, n_max + 1)
    ]


def gram_kernel(lambdas: list[float], n_dim: int) -> np.ndarray:
    k = np.empty((n_dim, n_dim), dtype=float)
    for j in range(1, n_dim + 1):
        for m in range(1, n_dim + 1):
            k[j - 1, m - 1] = lambdas[j] + lambdas[m] - lambdas[abs(j - m)]
    return k


def schoenberg_toeplitz(lambdas: list[float], n_dim: int, t: float) -> np.ndarray:
    q = np.empty((n_dim + 1, n_dim + 1), dtype=float)
    for j in range(n_dim + 1):
        for k in range(n_dim + 1):
            q[j, k] = math.exp(-t * lambdas[abs(j - k)])
    return q


def prime_atom_kernel(x: float, n_dim: int) -> np.ndarray:
    """Prime-atom contribution up to a positive common factor A Lambda(m)m^-s0.

    The actual contribution is minus this matrix.
    B_n=L_(n-1)^(1)(x), B_0=0.
    """
    b = [0.0] + [laguerre_l1(n - 1, x) for n in range(1, n_dim + 1)]
    g = np.empty((n_dim, n_dim), dtype=float)
    for j in range(1, n_dim + 1):
        for k in range(1, n_dim + 1):
            g[j - 1, k - 1] = -(b[j] + b[k] - b[abs(j - k)])
    return g


def eig_summary(matrix: np.ndarray) -> dict[str, float]:
    vals = np.linalg.eigvalsh(matrix)
    return {
        "min": float(vals[0]),
        "max": float(vals[-1]),
        "trace": float(np.trace(matrix)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-dim", type=int, default=8)
    parser.add_argument("--theta", type=float, default=0.7)
    parser.add_argument("--r", type=float, default=1.2)
    parser.add_argument("--search-n", type=int, default=100)
    parser.add_argument("--t", type=float, default=0.5)
    parser.add_argument("--x", type=str, default="0,1,5,10")
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    if args.n_dim < 1 or args.search_n < args.n_dim or args.r <= 1.0 or args.t <= 0.0:
        raise SystemExit("require n-dim>=1, search-n>=n-dim, r>1, t>0")

    on = unit_circle_pair_lambdas(args.theta, args.search_n)
    off = offline_quartet_lambdas(args.r, args.theta, args.search_n)

    first_negative = next((n for n in range(1, args.search_n + 1) if off[n] < 0.0), None)
    if first_negative is None:
        first_negative_value = None
    else:
        first_negative_value = off[first_negative]

    summary = {
        "n_dim": args.n_dim,
        "theta": args.theta,
        "r": args.r,
        "schoenberg_t": args.t,
        "unit_circle": {
            "gram": eig_summary(gram_kernel(on, args.n_dim)),
            "schoenberg": eig_summary(schoenberg_toeplitz(on, args.n_dim, args.t)),
        },
        "off_line_quartet": {
            "first_negative_lambda_n": first_negative,
            "first_negative_lambda_value": first_negative_value,
            "gram": eig_summary(gram_kernel(off, args.n_dim)),
            "schoenberg": eig_summary(schoenberg_toeplitz(off, args.n_dim, args.t)),
        },
        "prime_atom_kernels": {},
    }

    for x in [float(part.strip()) for part in args.x.split(",") if part.strip()]:
        mat = prime_atom_kernel(x, args.n_dim)
        summary["prime_atom_kernels"][str(x)] = {
            "k11": float(mat[0, 0]),
            **eig_summary(mat),
        }

    print(f"unit-circle Gram min eigenvalue: {summary['unit_circle']['gram']['min']:.6e}")
    print(f"unit-circle Schoenberg min eigenvalue: {summary['unit_circle']['schoenberg']['min']:.6e}")
    print(
        "off-line first negative lambda: "
        f"n={first_negative} value={first_negative_value}"
    )
    print(f"off-line Gram min eigenvalue (N={args.n_dim}): {summary['off_line_quartet']['gram']['min']:.6e}")
    print(f"off-line Schoenberg min eigenvalue: {summary['off_line_quartet']['schoenberg']['min']:.6e}")
    for x, item in summary["prime_atom_kernels"].items():
        print(f"prime atom x={x}: K11={item['k11']:.6e} min_eig={item['min']:.6e}")

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"saved_json={args.output_json}")


if __name__ == "__main__":
    main()
