"""Numerically split a single explicit-formula zero mode into Laguerre u-bins.

For rho=beta+i*gamma and p=(s0-rho)/A, the exact mode contribution is

    - integral_0^inf exp(-p t) L_{n-1}^{(1)}(t) dt
    = z_rho^{-n} - 1,

where z_rho=(rho-s0)/(rho+s0-1).

The script shows how regional pieces can be much larger than the final transform,
so region-by-region absolute estimates can destroy essential phase cancellation.
This is numerical evidence only; the full-transform identity is analytic.
"""

from __future__ import annotations

import argparse
import cmath
from math import fabs

from rh_tools import laguerre_float


def simpson_complex(func, a: float, b: float, steps: int) -> complex:
    if steps < 2:
        steps = 2
    if steps % 2:
        steps += 1
    h = (b - a) / steps
    total = func(a) + func(b)
    for i in range(1, steps):
        total += (4.0 if i % 2 else 2.0) * func(a + i * h)
    return total * h / 3.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--s0", type=float, default=3.0)
    parser.add_argument("--beta", type=float, default=0.6)
    parser.add_argument("--gamma", type=float, default=15.0)
    parser.add_argument("--n", default="8,16,32")
    parser.add_argument("--u-bins", default="0,0.25,0.5,0.75,1,1.25,1.5,2,2.5")
    parser.add_argument("--steps-per-bin", type=int, default=4000)
    args = parser.parse_args()

    if args.s0 <= 1.0:
        parser.error("s0 must be >1")
    bins = [float(v) for v in args.u_bins.split(",") if v.strip()]
    if len(bins) < 2 or bins[0] != 0.0 or any(b <= a for a, b in zip(bins, bins[1:])):
        parser.error("u-bins must start at 0 and increase strictly")
    ns = [int(v) for v in args.n.split(",") if v.strip()]

    A = 2.0 * args.s0 - 1.0
    rho = complex(args.beta, args.gamma)
    p = (args.s0 - rho) / A
    z = (rho - args.s0) / (rho + args.s0 - 1.0)

    print(
        f"s0={args.s0:g} A={A:g} rho={args.beta:g}+{args.gamma:g}i "
        f"Re(p)={p.real:.12g} Im(p)={p.imag:.12g} |z|^-1={1/abs(z):.12g}"
    )
    print("n u_lo u_hi |piece| arg_piece |cumulative|")

    for n in ns:
        exact = z ** (-n) - 1.0
        cumulative = 0j

        def integrand(t: float) -> complex:
            return -cmath.exp(-p * t) * laguerre_float(n - 1, 1, t)

        for lo, hi in zip(bins, bins[1:]):
            a = 4.0 * n * lo
            b = 4.0 * n * hi
            piece = simpson_complex(integrand, a, b, args.steps_per_bin)
            cumulative += piece
            print(
                f"{n:3d} {lo:5.2f} {hi:5.2f} {abs(piece):.9e} "
                f"{cmath.phase(piece):+.6f} {abs(cumulative):.9e}"
            )
        error = cumulative - exact
        print(
            f"n={n} exact_abs={abs(exact):.12e} truncated_abs={abs(cumulative):.12e} "
            f"abs_error={abs(error):.12e} exact={exact.real:+.6e}{exact.imag:+.6e}i"
        )
        print()

    print("NOTE: the final interval endpoint is finite; abs_error includes the omitted tail and quadrature error.")
    print("Regional magnitudes must not be interpreted as independent asymptotic contributions without phase analysis.")


if __name__ == "__main__":
    main()
