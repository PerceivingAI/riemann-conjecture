"""Diagnostics for the post-turning saddle and phase loss in A-20260820-004.

This script is exploratory support, not proof. It reports:
- the smooth-density post-turning saddle and its Gaussian width;
- the post-turning point where the absolute envelope drops below root rate 1;
- the positive absolute-envelope rate in the pre-turning region;
- the difference between a beta-only absolute envelope and the exact Cayley
  amplification when a complex phase gamma is retained.
"""

from __future__ import annotations

import argparse
from math import acosh, atanh, exp, log, sqrt

from rh_tools import density_kernel


def airy_bracket(u: float) -> float:
    if u < 1.0:
        raise ValueError("airy_bracket requires u>=1")
    return sqrt(u * u - u) - acosh(sqrt(u))


def pole_phi(A: float, u: float) -> float:
    """Per-nu exponent for the smooth-density kernel in u>=1."""
    return u / (2.0 * A) - 0.5 * airy_bracket(u)


def post_turning_zero(A: float) -> float:
    """Unique u>u_* where pole_phi(A,u)=0, found by bisection."""
    u_star = A * A / (A * A - 1.0)
    lo = u_star
    hi = max(2.0, 2.0 * u_star)
    while pole_phi(A, hi) > 0.0:
        hi *= 2.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if pole_phi(A, mid) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def cayley_amplification(s0: float, beta: float, gamma: float) -> float:
    """Return |z_rho|^-1 for rho=beta+i gamma."""
    numerator = (s0 + beta - 1.0) ** 2 + gamma * gamma
    denominator = (s0 - beta) ** 2 + gamma * gamma
    return sqrt(numerator / denominator)


def beta_envelope_rate(A: float, beta: float) -> float:
    """Maximum absolute-envelope root rate when phase gamma is discarded."""
    delta = 2.0 * beta - 1.0
    if delta <= 0.0:
        return 1.0
    if delta >= A:
        raise ValueError("beta envelope requires 2beta-1 < A")
    return exp(2.0 * atanh(delta / A))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--s0", type=float, default=3.0)
    parser.add_argument("--n", default="64,128,256")
    parser.add_argument("--gammas", default="0,5,15")
    parser.add_argument("--betas", default="0.5,0.6,0.9,1.0")
    args = parser.parse_args()

    if args.s0 <= 1.0:
        parser.error("s0 must be >1")
    ns = [int(v) for v in args.n.split(",") if v.strip()]
    gammas = [float(v) for v in args.gammas.split(",") if v.strip()]
    betas = [float(v) for v in args.betas.split(",") if v.strip()]

    A = 2.0 * args.s0 - 1.0
    q_abs = args.s0 / (args.s0 - 1.0)
    u_star = A * A / (A * A - 1.0)
    u_zero = post_turning_zero(A)
    curvature_k = (A * A - 1.0) ** 2 / (2.0 * A**3)

    print(f"s0={args.s0:g} A={A:g} |q|={q_abs:.12g}")
    print(f"u_star={u_star:.12g} u_post_root1={u_zero:.12g}")
    print(f"quadratic_k_per_n={curvature_k:.12g}")
    print()

    print("Gaussian e^-1 saddle widths (quadratic prediction)")
    print("n delta_u delta_t delta_log_x")
    for n in ns:
        delta_u = 1.0 / sqrt(curvature_k * n)
        delta_t = 4.0 * n * delta_u
        delta_log_x = delta_t / A
        print(f"{n:4d} {delta_u:.9f} {delta_t:.9f} {delta_log_x:.9f}")
    print()

    print("Actual density-kernel log ratios vs quadratic saddle prediction")
    print("n v log_actual_ratio log_quadratic")
    for n in ns:
        t_star = 4.0 * n * u_star
        center = abs(density_kernel(n, args.s0, t_star))
        if center == 0.0:
            continue
        for v in (-2.0, -1.0, 1.0, 2.0):
            u = u_star + v / sqrt(n)
            if u <= 0.0:
                continue
            value = abs(density_kernel(n, args.s0, 4.0 * n * u))
            if value == 0.0:
                continue
            actual = log(value / center)
            predicted = -curvature_k * v * v
            print(f"{n:4d} {v:+.1f} {actual:+.9f} {predicted:+.9f}")
    print()

    print("Smooth-density absolute-envelope root rates before the turning point")
    print("u log_root root_rate")
    for u in (0.25, 0.50, 0.75, 1.00):
        log_root = 2.0 * u / A
        print(f"{u:.2f} {log_root:.9f} {exp(log_root):.9f}")
    print("Any fixed u>0 has root_rate>1 under absolute-value/PNT-scale control.")
    print()

    print("Phase-loss diagnostic: beta-only envelope vs exact |z_rho|^-1")
    print("beta gamma envelope_rate exact_rate log_envelope log_exact")
    for beta in betas:
        envelope = beta_envelope_rate(A, beta)
        for gamma in gammas:
            exact = cayley_amplification(args.s0, beta, gamma)
            print(
                f"{beta:.3f} {gamma:7.3f} {envelope:.12f} {exact:.12f} "
                f"{log(envelope):+.9f} {log(exact):+.9f}"
            )

    print()
    print("NOTE: beta-only envelope rates discard oscillatory phase and are upper-envelope diagnostics.")
    print("For beta=1/2 the exact Cayley amplification is 1 for every gamma, as required by the critical line.")


if __name__ == "__main__":
    main()
