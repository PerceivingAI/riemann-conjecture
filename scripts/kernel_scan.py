"""Numerical localization scan for the Laguerre density kernel.

The scan uses u=t/(4n), because DLMF's uniform Laguerre scaling for
L_{n-1}^{(1)} has nu=4n and turning point u=1.
"""

from __future__ import annotations

import argparse
from math import fabs, log

if __package__:
    from scripts.rh_tools import density_kernel
else:
    from rh_tools import density_kernel


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--s0", type=float, default=3.0)
    parser.add_argument("--n", default="8,16,32,64")
    parser.add_argument("--u-max", type=float, default=1.6)
    parser.add_argument("--steps", type=int, default=6400)
    args = parser.parse_args()
    ns = [int(v.strip()) for v in args.n.split(",") if v.strip()]
    if args.s0 <= 1.0:
        parser.error("s0 must be > 1")
    if not ns or any(n < 1 for n in ns):
        parser.error("n must contain positive integers")
    if args.u_max <= 0.0:
        parser.error("u-max must be > 0")
    if args.steps < 1:
        parser.error("steps must be >= 1")

    A = 2.0 * args.s0 - 1.0
    p = (args.s0 - 1.0) / A
    q_abs = args.s0 / (args.s0 - 1.0)
    u_star = (A * A) / (A * A - 1.0)
    log_q = log(q_abs)
    print(
        f"s0={args.s0:g} A={A:g} p={p:.12g} u=t/(4n) "
        f"predicted_u_star={u_star:.12g} log_abs_q={log_q:.12g}"
    )
    print(
        "n u_at_max_abs t_at_max_abs log_abs_max log_abs_max_per_n "
        "gap_to_log_abs_q sign_at_max m_scale=exp(t/A)"
    )

    for n in ns:
        best_u = 0.0
        best_t = 0.0
        best_val = density_kernel(n, args.s0, 0.0)
        best_abs = fabs(best_val)
        for i in range(1, args.steps + 1):
            u = args.u_max * i / args.steps
            t = 4.0 * n * u
            val = density_kernel(n, args.s0, t)
            aval = fabs(val)
            if aval > best_abs:
                best_u, best_t, best_val, best_abs = u, t, val, aval
        log_abs = log(best_abs) if best_abs > 0.0 else float("-inf")
        # Avoid overflow in exp for exploratory output.
        log_m = best_t / A
        m_scale = f"exp({log_m:.6f})"
        rate = log_abs / n
        print(
            f"{n:3d} {best_u:.6f} {best_t:.6f} {log_abs:.9f} {rate:.9f} "
            f"{(log_q-rate):+.9f} {1 if best_val >= 0 else -1:+d} {m_scale}"
        )

    print("NOTE: this locates the largest sampled |e^{-pt} L_{n-1}^{(1)}(t)|.")
    print("It is reconnaissance, not a uniform asymptotic theorem.")


if __name__ == "__main__":
    main()
