"""Diagnostics for the uniform pre-turning Laguerre/Bessel phase in A-005.

For L_(n-1)^(1)(4 n u), DLMF 18.15.18-19 gives the leading Bessel phase
4 n xi(u)-3*pi/4 with
    xi(u)=1/2*(sqrt(u-u^2)+asin(sqrt(u))).

This script compares the exact stationary map from that phase with the older
small-u approximation and checks its critical-line Cayley phase identity.
Numerical zeta zeros are obtained with mpmath and are diagnostics, not certified data.
"""

from __future__ import annotations

import argparse
import json
from math import pi, sqrt
from pathlib import Path

from rh_tools import (
    critical_cayley_phase_per_n,
    get_zeta_zeros,
    laguerre_uniform_xi,
    small_u_stationary_u_from_gamma,
    uniform_preturning_stationary_u_from_gamma,
)


def phase_curvature(u: float) -> float:
    """Return -xi''(u)>0 on 0<u<1."""
    return 1.0 / (4.0 * u ** 1.5 * sqrt(1.0 - u))


def stationary_normalization(u: float) -> float:
    """Leading stationary amplitude normalization; analytically equal to 1."""
    amplitude = u ** (-0.75) * (1.0 - u) ** (-0.25)
    return 0.5 * amplitude / sqrt(phase_curvature(u))


def row_for_gamma(gamma: float, s0: float) -> dict[str, float]:
    A = 2.0 * s0 - 1.0
    u = uniform_preturning_stationary_u_from_gamma(gamma, s0)
    u_small = small_u_stationary_u_from_gamma(gamma, s0)
    xi = laguerre_uniform_xi(u)
    saddle_phase = 4.0 * (gamma * u / A - xi)
    cayley_phase = critical_cayley_phase_per_n(gamma, s0)
    return {
        "gamma": gamma,
        "u_uniform": u,
        "u_small": u_small,
        "small_u_relative_error": (u_small - u) / u,
        "log_x_per_n": 4.0 * A / (A * A + 4.0 * gamma * gamma),
        "saddle_phase_per_n": saddle_phase,
        "cayley_phase_per_n": cayley_phase,
        "phase_residual": saddle_phase - cayley_phase,
        "stationary_normalization": stationary_normalization(u),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--s0", type=float, default=3.0)
    parser.add_argument("--zeros", type=int, default=5)
    parser.add_argument("--dps", type=int, default=35)
    parser.add_argument("--output-json")
    parser.add_argument("--plot")
    args = parser.parse_args()
    if args.s0 <= 1.0:
        parser.error("s0 must be > 1")
    if args.zeros < 1:
        parser.error("zeros must be >= 1")

    gammas = get_zeta_zeros(args.zeros, dps=args.dps)
    rows = [row_for_gamma(g, args.s0) for g in gammas]
    A = 2.0 * args.s0 - 1.0

    print(f"s0={args.s0:g} A={A:g} zeros={args.zeros}")
    print(
        "k gamma u_uniform u_small rel_error_small log_x_per_n "
        "phase_residual saddle_norm"
    )
    for k, row in enumerate(rows, 1):
        print(
            f"{k:2d} {row['gamma']:.12f} {row['u_uniform']:.12e} "
            f"{row['u_small']:.12e} {row['small_u_relative_error']:+.6e} "
            f"{row['log_x_per_n']:.12e} {row['phase_residual']:+.3e} "
            f"{row['stationary_normalization']:.12f}"
        )

    payload = {
        "s0": args.s0,
        "A": A,
        "dps": args.dps,
        "zero_source": "mpmath.zetazero numerical evaluation; not a certificate",
        "rows": rows,
        "formulas": {
            "xi": "0.5*(sqrt(u-u^2)+asin(sqrt(u)))",
            "u_uniform": "A^2/(A^2+4 gamma^2)",
            "u_small": "A^2/(4 gamma^2)",
            "log_x_per_n": "4A/(A^2+4 gamma^2)",
            "critical_phase_per_n": "-2 atan(A/(2 gamma))",
        },
    }

    if args.output_json:
        path = Path(args.output_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"saved_json={path}")

    if args.plot:
        import matplotlib.pyplot as plt

        path = Path(args.plot)
        path.parent.mkdir(parents=True, exist_ok=True)
        gs = [row["gamma"] for row in rows]
        uniform = [row["u_uniform"] for row in rows]
        small = [row["u_small"] for row in rows]
        plt.figure()
        plt.plot(gs, uniform, marker="o", label="uniform pre-turning map")
        plt.plot(gs, small, marker="x", linestyle="--", label="small-u approximation")
        plt.xlabel("zero ordinate gamma")
        plt.ylabel("stationary coordinate u")
        plt.title(f"Laguerre stationary map, s0={args.s0:g}")
        plt.legend()
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        print(f"saved_plot={path}")

    print("NOTE: zero ordinates and plot are numerical diagnostics only.")
    print("The stationary-map and phase identities are analytic derivations checked separately.")


if __name__ == "__main__":
    main()
