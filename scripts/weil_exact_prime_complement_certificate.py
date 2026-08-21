#!/usr/bin/env python3
"""Proof-path diagnostics for A-20260821-004 at T=7/20.

This script uses only exact rational inputs and python-flint/Arb enclosures for
its mathematical outputs. It certifies two facts used by the exact-prime
Legendre-Schur route:

1. the global replacement V + P_2 >= (69/100)V is too lossy to make the
   resulting residual lower operator positive (explicit test w=P_0-P_2);
2. the exact-prime operator has a positive crude high-Legendre-mode
   complement bound from a finite mode onward.

It does NOT certify full first-prime Weil positivity.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx, fmpq

from scripts.cert.constants import (
    c2_enclosure,
    c_T_enclosure,
    log2_enclosure,
    rational_enclosure_dict,
)
from scripts.cert.residual_kernel import (
    _suzuki_residual_series_coefficients,
    _suzuki_residual_tail_radius,
    suzuki_residual_kernel_matrix,
)


def exact_fraction_dict(value: Fraction) -> dict[str, str]:
    return {"num": str(value.numerator), "den": str(value.denominator)}


def harmonic_fraction(n: int) -> Fraction:
    return sum((Fraction(1, k) for k in range(1, n + 1)), Fraction(0))


def certified_run(prec: int, max_n: int, residual_order: int) -> dict[str, object]:
    if prec < 64:
        raise ValueError("prec must be at least 64 bits")
    if max_n < 1:
        raise ValueError("max_n must be positive")
    if residual_order < 8:
        raise ValueError("residual_order must be at least 8")

    with ctx.workprec(prec):
        T = arb(7) / 20
        log2 = log2_enclosure(prec)
        c2 = c2_enclosure(prec)
        cT = c_T_enclosure(prec)
        tau = log2 / T

        # Test function w=P_0-P_2=(3/2)(1-x^2).
        norm_sq_exact = Fraction(12, 5)
        jump_exact = Fraction(3, 5)
        norm_sq = arb(norm_sq_exact.numerator) / norm_sq_exact.denominator
        jump = arb(jump_exact.numerator) / jump_exact.denominator

        # V(w)=-1/2 int log(1-x^2)|w|^2 dx
        #     =47/25-(12/5)log 2.
        V = arb(47) / 25 - (arb(12) / 5) * log2
        V69 = (arb(69) / 100) * V

        residual_matrix = suzuki_residual_kernel_matrix(
            basis_type="legendre",
            dim=3,
            T_val=T,
            prec=prec,
        )
        residual_w = (
            residual_matrix[0, 0]
            - 2 * residual_matrix[0, 2]
            + residual_matrix[2, 2]
        )

        q69 = jump + V69 + residual_w - cT * norm_sq
        if not q69.upper() < 0:
            raise RuntimeError("failed to certify Q_0.69(P0-P2) < 0")

        base_without_V = jump + residual_w - cT * norm_sq
        alpha_critical = (-base_without_V) / V

        # Exact p=2 translation on w. For real w,
        # P_2(w)=-2*c2*int_{-1}^{1-tau} w(t)w(t+tau) dt.
        def antiderivative(t: arb) -> arb:
            return (arb(9) / 4) * (
                (1 - tau * tau) * t
                - tau * t * t
                + ((-2 + tau * tau) / 3) * t**3
                + (tau / 2) * t**4
                + t**5 / 5
            )

        overlap = antiderivative(1 - tau) - antiderivative(arb(-1))
        prime_w = -2 * c2 * overlap
        q_exact = jump + V + prime_w + residual_w - cT * norm_sq
        if not q_exact.lower() > 0:
            raise RuntimeError("test-function exact-prime value was not certified positive")

        # Uniform residual operator norm bound by the Schur test:
        # ||R_T|| <= 2T sup_{|u|<=2T}|r''(u)|.
        u_max = 2 * T
        coefficients = _suzuki_residual_series_coefficients(residual_order)
        residual_abs_series = arb(0)
        for degree, coefficient in enumerate(coefficients):
            abs_coeff = fmpq(abs(int(coefficient.p)), int(coefficient.q))
            residual_abs_series += arb(abs_coeff) * (u_max**degree)
        residual_abs_series += _suzuki_residual_tail_radius(
            acb(u_max), residual_order
        )
        rho_R = 2 * T * residual_abs_series

        threshold = cT + c2 + rho_R
        complement_rows: list[dict[str, object]] = []
        first_positive_n: int | None = None
        for n in range(1, max_n + 1):
            H_fraction = harmonic_fraction(n)
            H = arb(H_fraction.numerator) / H_fraction.denominator
            mu = H - threshold
            positive = bool(mu.lower() > 0)
            if positive and first_positive_n is None:
                first_positive_n = n
            complement_rows.append(
                {
                    "N": n,
                    "H_N": exact_fraction_dict(H_fraction),
                    "mu_N": rational_enclosure_dict(mu),
                    "certified_positive": positive,
                }
            )

        if first_positive_n is None:
            raise RuntimeError(f"no positive complement bound found through N={max_n}")

        return {
            "role": "proof_path_arb_certificate",
            "claim_scope": "A-20260821-004 intermediate lemmas only; not full Weil positivity",
            "precision_bits": prec,
            "support_T": {"num": "7", "den": "20", "frac": "7/20"},
            "residual_series_order": residual_order,
            "test_function": {
                "description": "w=P_0-P_2=(3/2)(1-x^2)",
                "norm_sq": exact_fraction_dict(norm_sq_exact),
                "jump_energy": exact_fraction_dict(jump_exact),
                "V": rational_enclosure_dict(V),
                "residual": rational_enclosure_dict(residual_w),
                "q_069": rational_enclosure_dict(q69),
                "q_069_certified_negative": True,
                "alpha_critical": rational_enclosure_dict(alpha_critical),
                "prime_exact": rational_enclosure_dict(prime_w),
                "prime_loss_ratio_minus_P_over_V": rational_enclosure_dict((-prime_w) / V),
                "retained_fraction_exact_prime": rational_enclosure_dict((V + prime_w) / V),
                "q_exact_prime": rational_enclosure_dict(q_exact),
                "q_exact_prime_certified_positive_on_test": True,
            },
            "complement_bound": {
                "formula": "mu_N=H_N-c_T-c_2-rho_R",
                "residual_sup_abs_bound": rational_enclosure_dict(residual_abs_series),
                "rho_R": rational_enclosure_dict(rho_R),
                "threshold_c_T_plus_c_2_plus_rho_R": rational_enclosure_dict(threshold),
                "first_certified_positive_N": first_positive_n,
                "rows": complement_rows,
            },
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prec", type=int, default=224)
    parser.add_argument("--max-n", type=int, default=30)
    parser.add_argument("--residual-order", type=int, default=32)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    result = certified_run(args.prec, args.max_n, args.residual_order)
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
