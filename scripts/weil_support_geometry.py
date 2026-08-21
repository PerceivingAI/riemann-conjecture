"""Deterministic support/translation geometry for the Weil positivity audit A-20260821-002.

The script records prime-power support thresholds and the exact L2 operator norm
of the symmetrized compressed translation P_T(U_a+U_a^*)P_T on an interval of
logarithmic half-width T. It does not approximate the archimedean Weil operator.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def primes_up_to(n: int) -> list[int]:
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, int(math.isqrt(n)) + 1):
        if sieve[p]:
            sieve[p * p : n + 1 : p] = b"\x00" * (((n - p * p) // p) + 1)
    return [i for i in range(2, n + 1) if sieve[i]]


def von_mangoldt_prime_powers(limit: int) -> list[tuple[int, float]]:
    out: list[tuple[int, float]] = []
    for p in primes_up_to(limit):
        value = math.log(p)
        q = p
        while q <= limit:
            out.append((q, value))
            if q > limit // p:
                break
            q *= p
    out.sort()
    return out


def active_chain_vertices(T: float, a: float) -> int:
    """Essential maximal chain length for shift a on L2([-T,T])."""
    if T <= 0.0 or a <= 0.0:
        raise ValueError("require T>0 and a>0")
    ratio = 2.0 * T / a
    # At exact integer thresholds the new overlap occurs only on a null set, so
    # ceil(ratio) is the correct essential chain length there as well.
    return max(1, math.ceil(ratio - 1e-14))


def symmetrized_shift_norm(T: float, a: float) -> float:
    L = active_chain_vertices(T, a)
    return 2.0 * math.cos(math.pi / (L + 1.0))


def prime_power_row(m: int, lam: float, T: float) -> dict[str, float | int | bool]:
    a = math.log(m)
    threshold = 0.5 * a
    active = T > threshold
    norm = symmetrized_shift_norm(T, a) if active else 0.0
    coefficient = lam / math.sqrt(m)
    return {
        "m": m,
        "lambda_m": lam,
        "shift_a": a,
        "support_threshold_T": threshold,
        "active": active,
        "chain_vertices": active_chain_vertices(T, a) if active else 1,
        "symmetrized_shift_norm": norm,
        "prime_coefficient_lambda_over_sqrt_m": coefficient,
        "worst_case_operator_penalty": coefficient * norm,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--T", type=float, default=0.45)
    parser.add_argument("--max-m", type=int, default=20)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    if args.T <= 0.0 or args.max_m < 2:
        raise SystemExit("require T>0 and max-m>=2")

    rows = [prime_power_row(m, lam, args.T) for m, lam in von_mangoldt_prime_powers(args.max_m)]
    active = [r for r in rows if r["active"]]
    total_penalty = sum(float(r["worst_case_operator_penalty"]) for r in active)

    thresholds = [
        {
            "m": m,
            "T": 0.5 * math.log(m),
            "lambda_m": lam,
            "coefficient": lam / math.sqrt(m),
        }
        for m, lam in von_mangoldt_prime_powers(args.max_m)
    ]

    summary = {
        "T": args.T,
        "max_m": args.max_m,
        "prime_free_threshold_half_log_2": 0.5 * math.log(2.0),
        "first_window_upper_half_log_3": 0.5 * math.log(3.0),
        "first_prime_coefficient_log2_over_sqrt2": math.log(2.0) / math.sqrt(2.0),
        "active_rows": active,
        "crude_total_operator_penalty": total_penalty,
        "thresholds": thresholds,
    }

    print(f"T={args.T:.12f}")
    print(f"prime-free threshold 0.5 log 2={summary['prime_free_threshold_half_log_2']:.12f}")
    print(f"first-window upper 0.5 log 3={summary['first_window_upper_half_log_3']:.12f}")
    print(f"log(2)/sqrt(2)={summary['first_prime_coefficient_log2_over_sqrt2']:.12f}")
    print("active m threshold chain norm coefficient penalty")
    for r in active:
        print(
            f"{r['m']:2d} {r['support_threshold_T']:.9f} {r['chain_vertices']:2d} "
            f"{r['symmetrized_shift_norm']:.9f} "
            f"{r['prime_coefficient_lambda_over_sqrt_m']:.9f} "
            f"{r['worst_case_operator_penalty']:.9f}"
        )
    print(f"crude_total_operator_penalty={total_penalty:.12f}")

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"saved_json={args.output_json}")


if __name__ == "__main__":
    main()
