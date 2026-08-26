"""Generate the exact-prime Legendre-Schur certificate for A-20260821-004.

The analytic matrices are assembled with exact Fraction polynomial algebra and
Arb enclosures. All serialized matrix intervals are outward-rounded to dyadic
rational endpoints. The congruence witnesses are proposed without floating
point: exact rational midpoint LDL is computed independently on the two parity
blocks, L^{-1} is formed exactly, and its lower-triangular entries are rounded
to dyadic rationals. The witness has no proof authority by itself; the Rust
verifier recomputes the Schur matrix, exact congruence, and Gershgorin margins.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from flint import arb, ctx

from scripts.cert.constants import arb_to_rational_enclosure, c2_enclosure, c_T_enclosure
from scripts.cert.export_certificate import _generator_metadata, validate_certificate_schema
from scripts.cert.legendre_schur import assemble_exact_prime_schur, harmonic
from scripts.cert.matrices import RationalInterval, RationalIntervalMatrix


PROFILE = "exact_prime_legendre_schur"
TAIL_RULE = "legendre_component_gram_schur"
ALLOWED_CONFIGURATIONS = {
    (Fraction(7, 20), 32),
    (Fraction(2, 5), 40),
    (Fraction(17, 40), 48),
    (Fraction(9, 20), 56),
}


def _dyadic_outward_interval(value: arb, bits: int) -> RationalInterval:
    if bits < 16:
        raise ValueError("matrix interval bits must be at least 16")
    lo, hi = arb_to_rational_enclosure(value)
    denominator = 1 << bits
    lo_numerator = (lo.numerator * denominator) // lo.denominator
    hi_numerator = -((-hi.numerator * denominator) // hi.denominator)
    return RationalInterval(
        Fraction(lo_numerator, denominator),
        Fraction(hi_numerator, denominator),
    )


def _coarsen_matrix(matrix: list[list[arb]], bits: int) -> RationalIntervalMatrix:
    return RationalIntervalMatrix(
        [[_dyadic_outward_interval(value, bits) for value in row] for row in matrix]
    )


def _force_exact_parity_zeros(matrix: RationalIntervalMatrix) -> RationalIntervalMatrix:
    rows = [[entry for entry in row] for row in matrix.rows]
    for i in range(matrix.dim):
        for j in range(matrix.dim):
            if (i % 2) != (j % 2):
                interval = rows[i][j]
                if not (interval.lo <= 0 <= interval.hi):
                    raise RuntimeError(
                        f"opposite-parity enclosure ({i}, {j}) excludes exact zero"
                    )
                rows[i][j] = RationalInterval(0)
    return RationalIntervalMatrix(rows)


def _round_fraction_nearest_dyadic(value: Fraction, bits: int) -> Fraction:
    if bits < 8:
        raise ValueError("witness bits must be at least 8")
    if value == 0:
        return Fraction(0)
    denominator = 1 << bits
    sign = -1 if value < 0 else 1
    magnitude = abs(value)
    scaled_num = magnitude.numerator * denominator
    quotient, remainder = divmod(scaled_num, magnitude.denominator)
    if 2 * remainder >= magnitude.denominator:
        quotient += 1
    return Fraction(sign * quotient, denominator)


def _exact_ldl_midpoint(matrix: list[list[RationalInterval]]) -> tuple[list[list[Fraction]], list[Fraction]]:
    n = len(matrix)
    midpoint = [[entry.midpoint() for entry in row] for row in matrix]
    lower = [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    diagonal = [Fraction(0) for _ in range(n)]
    for j in range(n):
        diagonal[j] = midpoint[j][j] - sum(
            lower[j][k] * lower[j][k] * diagonal[k] for k in range(j)
        )
        if diagonal[j] <= 0:
            raise RuntimeError(f"midpoint LDL pivot {j} is not positive")
        for i in range(j + 1, n):
            lower[i][j] = (
                midpoint[i][j]
                - sum(lower[i][k] * lower[j][k] * diagonal[k] for k in range(j))
            ) / diagonal[j]
    return lower, diagonal


def _inverse_lower_triangular(lower: list[list[Fraction]]) -> list[list[Fraction]]:
    n = len(lower)
    inverse = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for column in range(n):
        for row in range(n):
            right = Fraction(int(row == column)) - sum(
                lower[row][k] * inverse[k][column] for k in range(row)
            )
            inverse[row][column] = right / lower[row][row]
    return inverse


def _point_interval(value: Fraction) -> RationalInterval:
    return RationalInterval(value)


def _exact_congruence(
    witness: list[list[Fraction]],
    matrix: list[list[RationalInterval]],
) -> list[list[RationalInterval]]:
    n = len(witness)
    left = [[RationalInterval(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            total = RationalInterval(0)
            for k in range(n):
                total += matrix[k][j] * witness[i][k]
            left[i][j] = total

    result = [[RationalInterval(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            total = RationalInterval(0)
            for k in range(n):
                total += left[i][k] * witness[j][k]
            result[i][j] = total
    return result


def _sup_abs(interval: RationalInterval) -> Fraction:
    return max(abs(interval.lo), abs(interval.hi))


def _gershgorin_margin(matrix: list[list[RationalInterval]]) -> Fraction:
    margins: list[Fraction] = []
    for i, row in enumerate(matrix):
        off_diagonal = sum(
            (_sup_abs(value) for j, value in enumerate(row) if j != i),
            Fraction(0),
        )
        margins.append(row[i].lo - off_diagonal)
    return min(margins)


def _parity_block(matrix: list[list[RationalInterval]], parity: int) -> list[list[RationalInterval]]:
    indices = list(range(parity, len(matrix), 2))
    return [[matrix[i][j] for j in indices] for i in indices]


def _make_witness(
    block: list[list[RationalInterval]],
    witness_bits: int,
) -> tuple[list[list[Fraction]], Fraction]:
    lower, _ = _exact_ldl_midpoint(block)
    inverse = _inverse_lower_triangular(lower)
    witness: list[list[Fraction]] = []
    for i, row in enumerate(inverse):
        witness.append(
            [
                Fraction(0) if j > i else _round_fraction_nearest_dyadic(value, witness_bits)
                for j, value in enumerate(row)
            ]
        )
    margin = _gershgorin_margin(_exact_congruence(witness, block))
    if margin <= 0:
        raise RuntimeError("rational congruence witness failed strict Gershgorin positivity")
    return witness, margin


def _exact_matrix_json(matrix: list[list[Fraction]]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for row_index, row in enumerate(matrix):
        for col_index, value in enumerate(row):
            entries.append(
                {
                    "row": row_index,
                    "col": col_index,
                    "num": str(value.numerator),
                    "den": str(value.denominator),
                }
            )
    return {"dimension": len(matrix), "entries": entries}


def _interval_matrix_json(matrix: RationalIntervalMatrix) -> dict[str, Any]:
    return {"dimension": matrix.dim, "entries": matrix.to_entries()}


def _schur_from_serialized_inputs(
    a_matrix: RationalIntervalMatrix,
    gv: RationalIntervalMatrix,
    g2: RationalIntervalMatrix,
    gr: RationalIntervalMatrix,
    c_t: RationalInterval,
    c2: RationalInterval,
    rho_r: RationalInterval,
    dimension: int,
) -> tuple[list[list[RationalInterval]], Fraction]:
    mu_lower = harmonic(dimension) - c_t.hi - c2.hi - rho_r.hi
    if mu_lower <= 0:
        raise RuntimeError("serialized complement lower bound is not positive")
    factor = Fraction(3, 1) / mu_lower
    schur: list[list[RationalInterval]] = []
    for i in range(dimension):
        row: list[RationalInterval] = []
        for j in range(dimension):
            gram = gv.rows[i][j] + g2.rows[i][j] + gr.rows[i][j]
            row.append(a_matrix.rows[i][j] - gram * factor)
        schur.append(row)
    return schur, mu_lower


def build_exact_prime_schur_certificate(
    *,
    claim: str,
    support_num: int = 7,
    support_den: int = 20,
    dimension: int = 32,
    prec: int = 160,
    residual_order: int = 32,
    matrix_bits: int = 64,
    witness_bits: int = 32,
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    support = Fraction(support_num, support_den)
    if (support, dimension) not in ALLOWED_CONFIGURATIONS:
        allowed = ", ".join(
            f"T={value},N={dim}" for value, dim in sorted(ALLOWED_CONFIGURATIONS)
        )
        raise ValueError(f"v1 exact-prime profile allows only {allowed}")
    if residual_order != 32:
        raise ValueError("v1 exact-prime profile is locked to residual order 32")
    if prec < 128:
        raise ValueError("precision must be at least 128 bits")

    with ctx.workprec(prec):
        assembled = assemble_exact_prime_schur(
            n=dimension,
            prec=prec,
            residual_order=residual_order,
            support_num=support.numerator,
            support_den=support.denominator,
        )
        a_matrix = _force_exact_parity_zeros(_coarsen_matrix(assembled["A"], matrix_bits))
        gv = _force_exact_parity_zeros(_coarsen_matrix(assembled["GV"], matrix_bits))
        g2 = _force_exact_parity_zeros(_coarsen_matrix(assembled["G2"], matrix_bits))
        gr = _force_exact_parity_zeros(_coarsen_matrix(assembled["GR"], matrix_bits))
        c_t = _dyadic_outward_interval(
            c_T_enclosure(prec, support.numerator, support.denominator), matrix_bits
        )
        c2 = _dyadic_outward_interval(c2_enclosure(prec), matrix_bits)
        rho_r = _dyadic_outward_interval(assembled["rho_R"], matrix_bits)

    schur, mu_lower = _schur_from_serialized_inputs(
        a_matrix,
        gv,
        g2,
        gr,
        c_t,
        c2,
        rho_r,
        dimension,
    )
    even_witness, even_margin = _make_witness(_parity_block(schur, 0), witness_bits)
    odd_witness, odd_margin = _make_witness(_parity_block(schur, 1), witness_bits)

    certificate: dict[str, Any] = {
        "format": "rh-weil-certificate-v1",
        "claim": claim,
        "claim_profile": PROFILE,
        "support_T": {
            "num": str(support.numerator),
            "den": str(support.denominator),
            "frac": f"{support.numerator}/{support.denominator}",
        },
        "basis": {
            "type": "legendre",
            "dimension": dimension,
            "domain": "[-1, 1]",
        },
        "parity_sector": "both",
        "dimension": dimension,
        "constants": {
            "c2": c2.to_dict(),
            "c_T": c_t.to_dict(),
            "rho_R": rho_r.to_dict(),
        },
        "matrix": _interval_matrix_json(a_matrix),
        "tail_bound": {
            "type": TAIL_RULE,
            "harmonic_index": dimension,
            "factor": {"num": "3", "den": "1"},
        },
        "schur_proof": {
            "residual_order": residual_order,
            "GV": _interval_matrix_json(gv),
            "G2": _interval_matrix_json(g2),
            "GR": _interval_matrix_json(gr),
            "even_witness": _exact_matrix_json(even_witness),
            "odd_witness": _exact_matrix_json(odd_witness),
        },
        "generator_metadata": _generator_metadata(
            prec,
            script="scripts.cert.exact_prime_schur_certificate",
        ),
    }

    valid, message = validate_certificate_schema(certificate)
    if not valid:
        raise ValueError(f"generated exact-prime certificate failed validation: {message}")

    diagnostics = {
        "mu_lower": mu_lower,
        "even_gershgorin_margin": even_margin,
        "odd_gershgorin_margin": odd_margin,
    }
    return certificate, diagnostics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim", default="C-0050")
    parser.add_argument("--support", default="7/20")
    parser.add_argument("--dimension", type=int, default=32)
    parser.add_argument("--prec", type=int, default=160)
    parser.add_argument("--matrix-bits", type=int, default=64)
    parser.add_argument("--witness-bits", type=int, default=32)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    support = Fraction(args.support)
    certificate, diagnostics = build_exact_prime_schur_certificate(
        claim=args.claim,
        support_num=support.numerator,
        support_den=support.denominator,
        dimension=args.dimension,
        prec=args.prec,
        matrix_bits=args.matrix_bits,
        witness_bits=args.witness_bits,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(certificate, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"certificate={args.output_json}")
    print(f"mu_lower={diagnostics['mu_lower']}")
    print(f"even_gershgorin_margin={diagnostics['even_gershgorin_margin']}")
    print(f"odd_gershgorin_margin={diagnostics['odd_gershgorin_margin']}")


if __name__ == "__main__":
    main()
