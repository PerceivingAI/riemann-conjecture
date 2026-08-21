"""Diagnostics for the microlocal prime-side Laguerre chirp in A-006.

The script works only with logarithmic scales. It does not enumerate primes.
It records the exact local Mellin frequency, chirp curvature, the first-prime
frequency cap, and the exponential scale left by a generic Dirichlet-polynomial
mean-value bound.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def frequency(u: float, A: float) -> float:
    if not 0.0 < u < 1.0:
        raise ValueError("u must lie in (0,1)")
    return 0.5 * A * math.sqrt((1.0 - u) / u)


def phase_second_y(u: float, A: float, n: int) -> float:
    """Second y-derivative of 4n*xi(Ay/(4n)), y=log x."""
    if not 0.0 < u < 1.0 or n < 1:
        raise ValueError("require u in (0,1), n>=1")
    return -(A * A) / (16.0 * n * (u ** 1.5) * math.sqrt(1.0 - u))


def linear_window_half_width(u: float, A: float, n: int, phase_error: float) -> float:
    """H such that (1/2)|Phi''(y0)| H^2 = phase_error."""
    curv = abs(phase_second_y(u, A, n))
    return math.sqrt(2.0 * phase_error / curv)


def first_prime_coordinate(A: float, n: int) -> float:
    return A * math.log(2.0) / (4.0 * n)


def first_prime_frequency(A: float, n: int) -> float:
    u2 = first_prime_coordinate(A, n)
    if u2 >= 1.0:
        return 0.0
    return frequency(u2, A)


def endpoint_density_bound(A: float, n: int) -> float:
    """DLMF 18.14.8 bound for the deterministic interval 1<=x<2."""
    return 2.0 * A * n * (math.sqrt(2.0) - 1.0)


def row(s0: float, n: int, u: float, phase_error: float) -> dict[str, float]:
    A = 2.0 * s0 - 1.0
    y0 = 4.0 * n * u / A
    gamma = frequency(u, A)
    phi2 = phase_second_y(u, A, n)
    H = linear_window_half_width(u, A, n, phase_error)
    # A generic Montgomery-Vaughan mean-value theorem has a length term N~exp(y0+o(n));
    # taking square roots leaves exp(y0/2+o(n)).
    mv_log_rms_per_n = y0 / (2.0 * n)
    return {
        "s0": s0,
        "A": A,
        "n": n,
        "u": u,
        "gamma": gamma,
        "log_X": y0,
        "log_X_per_n": y0 / n,
        "phase_second_y": phi2,
        "linear_half_width_y": H,
        "linear_half_width_over_sqrt_n": H / math.sqrt(n),
        "mv_log_rms_per_n": mv_log_rms_per_n,
        "mv_root_base": math.exp(mv_log_rms_per_n),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--s0", type=float, default=3.0)
    parser.add_argument("--n", type=int, default=256)
    parser.add_argument("--u", type=str, default="0.02,0.05,0.1,0.25,0.5,0.75")
    parser.add_argument("--phase-error", type=float, default=0.25)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    if args.s0 <= 1.0 or args.n < 1 or args.phase_error <= 0.0:
        raise SystemExit("require s0>1, n>=1, phase-error>0")

    us = [float(part.strip()) for part in args.u.split(",") if part.strip()]
    rows = [row(args.s0, args.n, u, args.phase_error) for u in us]
    A = 2.0 * args.s0 - 1.0
    u2 = first_prime_coordinate(A, args.n)
    gamma2 = first_prime_frequency(A, args.n)

    summary = {
        "s0": args.s0,
        "A": A,
        "n": args.n,
        "phase_error": args.phase_error,
        "u_first_prime": u2,
        "gamma_first_prime": gamma2,
        "gamma_first_prime_over_sqrt_n": gamma2 / math.sqrt(args.n),
        "gamma_first_prime_asymptotic_constant": math.sqrt(A / math.log(2.0)),
        "endpoint_1_to_2_bound": endpoint_density_bound(A, args.n),
        "rows": rows,
    }

    print(f"s0={args.s0:g} A={A:g} n={args.n}")
    print(f"u_2={u2:.12e} gamma_2={gamma2:.12e} gamma_2/sqrt(n)={gamma2/math.sqrt(args.n):.12e}")
    print(f"endpoint_bound_1_to_2={summary['endpoint_1_to_2_bound']:.12e}")
    print("u gamma logX/n H/sqrt(n) MV-root-base")
    for item in rows:
        print(
            f"{item['u']:.6f} {item['gamma']:.9f} {item['log_X_per_n']:.9f} "
            f"{item['linear_half_width_over_sqrt_n']:.9f} {item['mv_root_base']:.9f}"
        )

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"saved_json={args.output_json}")


if __name__ == "__main__":
    main()
