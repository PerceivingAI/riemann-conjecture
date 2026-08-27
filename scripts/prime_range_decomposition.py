"""Decompose the prime-Laguerre discrepancy by the uniform turning-scale u=t/(4n).

For each u-bin this compares the discrete prime-power contribution to the
continuous prime-density contribution. Their difference is a cutoff version of
the exact Stieltjes discrepancy transform from A-20260820-002.
"""

from __future__ import annotations

import argparse
from math import exp, log

if __package__:
    from scripts.rh_tools import (
        composite_simpson,
        density_kernel,
        laguerre_float,
        primes_up_to,
    )
else:
    from rh_tools import (
        composite_simpson,
        density_kernel,
        laguerre_float,
        primes_up_to,
    )


def prime_power_items(limit: int) -> list[tuple[int, float]]:
    items: list[tuple[int, float]] = []
    for p in primes_up_to(limit):
        lp = log(p)
        power = p
        while power <= limit:
            items.append((power, lp))
            if power > limit // p:
                break
            power *= p
    items.sort()
    return items


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--s0", type=float, default=3.0)
    parser.add_argument("--n", default="8,12,16")
    parser.add_argument("--max-m", type=int, default=2_000_000)
    parser.add_argument("--u-bins", default="0,0.25,0.5,0.75,1.0,1.25,1.5")
    parser.add_argument("--simpson-steps", type=int, default=600)
    args = parser.parse_args()
    if args.s0 <= 1.0:
        parser.error("s0 must be > 1")
    ns = [int(v.strip()) for v in args.n.split(",") if v.strip()]
    bins = [float(v.strip()) for v in args.u_bins.split(",") if v.strip()]
    if not ns or any(n < 1 for n in ns):
        parser.error("n must contain positive integers")
    if args.max_m < 2:
        parser.error("max-m must be >= 2")
    if args.simpson_steps < 2:
        parser.error("simpson-steps must be >= 2")
    if len(bins) < 2 or bins[0] != 0.0 or any(b <= a for a, b in zip(bins, bins[1:])):
        parser.error("u-bins must start at 0 and increase strictly")

    A = 2.0 * args.s0 - 1.0
    u_star = (A * A) / (A * A - 1.0)
    items = prime_power_items(args.max_m)
    max_t = A * log(args.max_m)
    print(
        f"s0={args.s0:g} A={A:g} max_m={args.max_m} max_t={max_t:.9f} "
        f"predicted_u_star={u_star:.12g}"
    )
    print("n u_lo u_hi m_lo m_hi prime discrete_main discrepancy abs_prime_mass cancellation_ratio")

    for n in ns:
        # Respect the actual m cutoff by clipping the final t endpoint.
        for u_lo, u_hi in zip(bins, bins[1:]):
            t_lo = 4.0 * n * u_lo
            t_hi = min(4.0 * n * u_hi, max_t)
            if t_lo >= max_t:
                continue
            m_lo = exp(t_lo / A)
            m_hi = exp(t_hi / A)
            prime_sum = 0.0
            abs_mass = 0.0
            for m, lam in items:
                if m < m_lo:
                    continue
                if m > m_hi:
                    break
                t = A * log(m)
                lag = laguerre_float(n - 1, 1, t)
                term = A * lam * (m ** (-args.s0)) * lag
                prime_sum += term
                abs_mass += abs(term)

            main_integral = composite_simpson(
                lambda t: density_kernel(n, args.s0, t),
                t_lo,
                t_hi,
                args.simpson_steps,
            )
            discrepancy = prime_sum - main_integral
            ratio = abs(prime_sum) / abs_mass if abs_mass else 0.0
            print(
                f"{n:2d} {u_lo:.3f} {u_hi:.3f} {m_lo:.3e} {m_hi:.3e} "
                f"{prime_sum:+.9e} {main_integral:+.9e} {discrepancy:+.9e} "
                f"{abs_mass:.9e} {ratio:.6f}"
            )

    print("NOTE: bins beyond max_m are omitted; the decomposition is truncated.")
    print("cancellation_ratio=|sum prime terms|/sum |prime terms| within the bin.")


if __name__ == "__main__":
    main()
