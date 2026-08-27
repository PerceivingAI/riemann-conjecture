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
import json
from math import isfinite
from pathlib import Path

if __package__:
    from scripts.rh_tools import laguerre_float
else:
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
    parser.add_argument("--output-json", type=str, default=None, help="Optional output JSON path")
    args = parser.parse_args()
    if args.s0 <= 1.0:
        parser.error("s0 must be >1")
    if not all(isfinite(value) for value in (args.s0, args.beta, args.gamma)):
        parser.error("s0, beta, and gamma must be finite")
    if args.beta >= args.s0:
        parser.error("beta must be < s0 so the Laplace mode has Re(p)>0")
    if args.steps_per_bin < 2:
        parser.error("steps-per-bin must be >= 2")
    bins = [float(v) for v in args.u_bins.split(",") if v.strip()]
    if len(bins) < 2 or bins[0] != 0.0 or any(b <= a for a, b in zip(bins, bins[1:])):
        parser.error("u-bins must start at 0 and increase strictly")
    ns = [int(v) for v in args.n.split(",") if v.strip()]
    if not ns or any(n < 1 for n in ns):
        parser.error("n must contain positive integers")

    A = 2.0 * args.s0 - 1.0
    rho = complex(args.beta, args.gamma)
    denominator = rho + args.s0 - 1.0
    if denominator == 0:
        parser.error("rho+s0-1 must be nonzero for the Cayley transform")
    p = (args.s0 - rho) / A
    z = (rho - args.s0) / denominator

    print(
        f"s0={args.s0:g} A={A:g} rho={args.beta:g}+{args.gamma:g}i "
        f"Re(p)={p.real:.12g} Im(p)={p.imag:.12g} |z|^-1={1/abs(z):.12g}"
    )
    print("n u_lo u_hi |piece| arg_piece |cumulative|")

    results_by_n = {}
    for n in ns:
        exact = z ** (-n) - 1.0
        cumulative = 0j
        bin_entries = []

        def integrand(t: float) -> complex:
            return -cmath.exp(-p * t) * laguerre_float(n - 1, 1, t)

        for lo, hi in zip(bins, bins[1:]):
            a = 4.0 * n * lo
            b = 4.0 * n * hi
            piece = simpson_complex(integrand, a, b, args.steps_per_bin)
            cumulative += piece
            bin_entries.append({
                "u_lo": lo,
                "u_hi": hi,
                "piece_abs": abs(piece),
                "piece_phase": cmath.phase(piece),
                "cumulative_abs": abs(cumulative),
            })
            print(
                f"{n:3d} {lo:5.2f} {hi:5.2f} {abs(piece):.9e} "
                f"{cmath.phase(piece):+.6f} {abs(cumulative):.9e}"
            )
        error = cumulative - exact
        results_by_n[str(n)] = {
            "exact_real": exact.real,
            "exact_imag": exact.imag,
            "exact_abs": abs(exact),
            "cumulative_abs": abs(cumulative),
            "abs_error": abs(error),
            "bins": bin_entries,
        }
        print(
            f"n={n} exact_abs={abs(exact):.12e} truncated_abs={abs(cumulative):.12e} "
            f"abs_error={abs(error):.12e} exact={exact.real:+.6e}{exact.imag:+.6e}i"
        )
        print()

    if args.output_json:
        out_path = Path(args.output_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "s0": args.s0,
            "beta": args.beta,
            "gamma": args.gamma,
            "ns": ns,
            "results": results_by_n,
        }
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nWrote summary data to {out_path}")
    print("Regional magnitudes must not be interpreted as independent asymptotic contributions without phase analysis.")


if __name__ == "__main__":
    main()
