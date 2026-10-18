"""Research-only independent spot controls for analytic Weil-form input identities.

Not a certificate, not a theorem-admission check, and not a complete
all-entry independent reconstruction of the N=192 matrix.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import mpmath as mp
from flint import ctx, fmpq, fmpq_poly

from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.multi_prime_legendre_schur import (
    _abs_power_action, _potential_matrices,
)


def _independent_split_power(d: int, k: int) -> fmpq_poly:
    """Exact integral of |x-y|**d * y**k over y in [-1,1] by endpoint primitives."""
    x = fmpq_poly([0, 1])
    result = fmpq_poly()
    for left_half in (True, False):
        for j in range(d + 1):
            sign = (-1) ** (j if left_half else d - j)
            c = fmpq(math.comb(d, j) * sign, k + j + 1)
            primitive = c * x ** (d - j)
            exponent = k + j + 1
            if left_half:
                result += primitive * (
                    x**exponent - fmpq_poly([(-1)**exponent])
                )
            else:
                result += primitive * (
                    fmpq_poly([1]) - x**exponent
                )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    raw = args.packet.read_bytes()
    packet = json.loads(gzip.decompress(raw))
    if packet["dimension"] != 192 or packet["support"] != [11, 20]:
        raise ValueError("wrong audited research packet")
    if packet["active_terms"] != [2, 3]:
        raise ValueError("incorrect active-term set")

    exact_kernel_cases = 0
    for d in range(9):
        for k in range(9):
            image = _abs_power_action(
                d,
                fmpq_poly([0] * k + [1]),
                tuple(math.comb(d, j) for j in range(d+1)),
            )
            if image != _independent_split_power(d, k):
                raise AssertionError(f"incorrect residual polynomial at {d=}, {k=}")
            exact_kernel_cases += 1
    print("SPLIT_KERNEL_INDEPENDENT_EXACT_CHECK", exact_kernel_cases, "PASS", flush=True)

    # High precision quadrature is a nonproof cross-check only. The moment
    # identities themselves follow exactly by differentiating the beta function.
    mp.mp.dps = 75
    errors: dict[str, str] = {}
    with ctx.workprec(512):
        for degree in (0, 2, 20, 190):
            polynomials = [
                [Fraction(1)],
                [Fraction(0)]*degree + [Fraction(1)],
            ]
            v, v2 = _potential_matrices(polynomials, 512)
            for label, ball, exponent in (
                ("V", v[0][1], 1),
                ("V2", v2[0][1], 2),
            ):
                low, high = arb_to_rational_enclosure(ball)
                center = (low+high)/2
                estimate = mp.mpf(center.numerator)/center.denominator
                reference = mp.quad(
                    lambda x: x**degree*(-mp.log(1-x*x)/2)**exponent,
                    [-1, 0, 1],
                )
                error = abs(estimate-reference)
                if error >= mp.mpf("1e-50"):
                    raise AssertionError(f"potential moment mismatch at {degree=}, {label=}, {error=}")
                errors[f"{label}_{degree}"] = mp.nstr(error, 18)
                print("INDEPENDENT_POTENTIAL_MOMENT", label, degree, "ERROR", errors[f"{label}_{degree}"], flush=True)

    n = packet["dimension"]
    if any(
        len(rows) != n or any(len(row) != n-i for i,row in enumerate(rows))
        for rows in (packet["low_A_triangular"], packet["truncated_gram_triangular"])
    ):
        raise ValueError("incomplete high-dimensional research packet")

    report = {
        "scope": "research-only independent analytic identity and reference controls",
        "full_high_dim_transcendental_recomputation": False,
        "theorem_admission": False,
        "matrix_packet_sha256": hashlib.sha256(raw).hexdigest(),
        "exact_residual_polynomial_pairs_verified": exact_kernel_cases,
        "potential_and_square_numeric_reference_errors_nonproof": errors,
        "packet_low_and_gram_entry_count": n*(n+1),
        "status": "PASS_SCOPED_ANALYTIC_CONTROLS_NOT_AN_ALL_ENTRY_CERTIFICATE",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("AUDIT_RECORD", str(args.output), flush=True)


if __name__ == "__main__":
    main()
