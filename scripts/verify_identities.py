"""Exact rational verification of identities used by A-20260820-002.

No external packages are required. Polynomial identities are checked with
fractions.Fraction, so a PASS is exact for the tested finite set rather than a
floating-point comparison.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from math import comb, factorial


def laguerre_coeffs(n: int, alpha: int) -> list[Fraction]:
    # L_n^(alpha)(x) = sum_{k=0}^n (-1)^k binom(n+alpha,n-k) x^k / k!
    return [
        Fraction(((-1) ** k) * comb(n + alpha, n - k), factorial(k))
        for k in range(n + 1)
    ]


def poly_sub(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    size = max(len(a), len(b))
    out = [Fraction(0) for _ in range(size)]
    for i in range(size):
        out[i] = (a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def laplace_integral_of_poly(coeffs: list[Fraction], p: Fraction) -> Fraction:
    # int_0^inf e^{-pt} sum c_k t^k dt = sum c_k k! / p^(k+1)
    return sum(c * factorial(k) / (p ** (k + 1)) for k, c in enumerate(coeffs))


def verify(max_n: int, s0_values: list[Fraction]) -> None:
    failures: list[str] = []
    if max_n < 1:
        raise ValueError("max_n must be >= 1")
    if not s0_values or any(s0 <= 1 for s0 in s0_values):
        raise ValueError("s0_values must be non-empty and all > 1")

    for n in range(1, max_n + 1):
        lhs = laguerre_coeffs(n, 0)
        rhs = poly_sub(laguerre_coeffs(n, 1), laguerre_coeffs(n - 1, 1))
        if lhs != rhs:
            failures.append(f"Laguerre contiguous identity failed at n={n}")

    for s0 in s0_values:
        A = 2 * s0 - 1
        q = -s0 / (s0 - 1)
        p = (s0 - 1) / A
        for n in range(1, max_n + 1):
            integral = laplace_integral_of_poly(laguerre_coeffs(n - 1, 1), p)
            expected = 1 - q**n
            if integral != expected:
                failures.append(
                    f"Pole integral identity failed at s0={s0}, n={n}: {integral} != {expected}"
                )

            def h(k: int) -> Fraction:
                return 1 - q**k

            # T=(E-1)(E-q): T h_n = h_{n+2}-(q+1)h_{n+1}+q h_n.
            filtered = h(n + 2) - (q + 1) * h(n + 1) + q * h(n)
            if filtered != 0:
                failures.append(f"Pole filter failed at s0={s0}, n={n}: {filtered}")

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("PASS")
    print(f"Laguerre contiguous identity: exact for n=1..{max_n}")
    for s0 in s0_values:
        q = -s0 / (s0 - 1)
        print(
            f"s0={s0}: pole integral and T=(E-1)(E-q) annihilation exact "
            f"for n=1..{max_n}; q={q}"
        )


def parse_fraction(text: str) -> Fraction:
    if "/" in text:
        left, right = text.split("/", 1)
        return Fraction(int(left), int(right))
    return Fraction(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=30)
    parser.add_argument(
        "--s0",
        action="append",
        default=None,
        help="Rational center such as 2, 3, 5/2; may be repeated",
    )
    args = parser.parse_args()
    centers = [parse_fraction(v) for v in (args.s0 or ["2", "3", "5/2", "4"])]
    if args.max_n < 1:
        parser.error("max-n must be >= 1")
    if any(v <= 1 for v in centers):
        parser.error("all s0 values must be > 1")
    verify(args.max_n, centers)


if __name__ == "__main__":
    main()
