"""Geometry diagnostics for the Vaughan/Type-II chirp route A-007.

This script studies only the deterministic phase geometry. It does not enumerate
primes and does not assert any prime-cancellation theorem.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def xi(u: float) -> float:
    if not 0.0 <= u <= 1.0:
        raise ValueError("u must lie in [0,1]")
    return 0.5 * (math.sqrt(max(0.0, u - u * u)) + math.asin(math.sqrt(u)))


def phi(n: int, A: float, y: float) -> float:
    u = A * y / (4.0 * n)
    if not 0.0 <= u <= 1.0:
        raise ValueError("y outside pre-turning range")
    return 4.0 * n * xi(u) - 0.75 * math.pi


def phi_second_y(n: int, A: float, u: float) -> float:
    if not 0.0 < u < 1.0:
        raise ValueError("u must lie in (0,1)")
    return -(A * A) / (16.0 * n * (u ** 1.5) * math.sqrt(1.0 - u))


def cross_defect(n: int, A: float, y0: float, hr: float, hs: float) -> float:
    """Four-corner non-separability defect for F(r,s)=Phi(r+s)."""
    # Center the rectangle at r+s=y0 with lower-left sum shifted by half-widths.
    base = y0 - 0.5 * (hr + hs)
    return (
        phi(n, A, base + hr + hs)
        - phi(n, A, base + hr)
        - phi(n, A, base + hs)
        + phi(n, A, base)
    )


def row(s0: float, n: int, u: float, log_width: float) -> dict[str, float]:
    A = 2.0 * s0 - 1.0
    y0 = 4.0 * n * u / A
    p2 = phi_second_y(n, A, u)
    defect = cross_defect(n, A, y0, log_width, log_width)
    hcrit = 1.0 / math.sqrt(abs(p2))
    return {
        "u": u,
        "y0": y0,
        "phi_second_y": p2,
        "dyadic_bound_abs": abs(p2) * log_width * log_width,
        "cross_defect": defect,
        "cross_defect_abs": abs(defect),
        "balanced_log_width_for_unit_cross_phase": hcrit,
        "hcrit_over_sqrt_n": hcrit / math.sqrt(n),
        "multiplicative_ratio_hcrit_log10": hcrit / math.log(10.0),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--s0", type=float, default=3.0)
    parser.add_argument("--n", type=int, default=1024)
    parser.add_argument("--u", type=str, default="0.05,0.1,0.25,0.5,0.75")
    parser.add_argument("--log-width", type=float, default=math.log(2.0))
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    if args.s0 <= 1.0 or args.n < 1 or args.log_width <= 0.0:
        raise SystemExit("require s0>1, n>=1, log-width>0")

    A = 2.0 * args.s0 - 1.0
    us = [float(part.strip()) for part in args.u.split(",") if part.strip()]
    if not us or any(not 0.0 < u < 1.0 for u in us):
        raise SystemExit("u must contain values strictly between 0 and 1")
    rows = [row(args.s0, args.n, u, args.log_width) for u in us]
    total_phase_excursion = 4.0 * args.n * (xi(1.0) - xi(0.0))

    result = {
        "s0": args.s0,
        "A": A,
        "n": args.n,
        "log_width": args.log_width,
        "total_preturning_phase_excursion": total_phase_excursion,
        "total_preturning_cycles": total_phase_excursion / (2.0 * math.pi),
        "rows": rows,
    }

    print(f"s0={args.s0:g} A={A:g} n={args.n} log_width={args.log_width:.12g}")
    print(f"total_phase_excursion={total_phase_excursion:.12g} total_cycles={result['total_preturning_cycles']:.12g}")
    print("u |Phi''| dyadic_cross_defect dyadic_bound Hcrit/sqrt(n) log10(exp(Hcrit))")
    for item in rows:
        print(
            f"{item['u']:.6f} {abs(item['phi_second_y']):.12e} "
            f"{item['cross_defect_abs']:.12e} {item['dyadic_bound_abs']:.12e} "
            f"{item['hcrit_over_sqrt_n']:.9f} {item['multiplicative_ratio_hcrit_log10']:.6f}"
        )

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"saved_json={args.output_json}")


if __name__ == "__main__":
    main()
