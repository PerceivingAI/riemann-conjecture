"""Exact rational construction primitives shared across the Schur proof path.

This module contains only support-agnostic generator mechanics: outward dyadic
rounding, exact parity cleanup, exact rational Schur construction, and rational
congruence/Gershgorin witness construction.  It deliberately contains no
whitelist, claim identifier, certificate metadata, contract mutation, or Rust
verifier invocation.  Pre-theorem continuation and the closed theorem exporter
may both depend on these primitives without allowing the continuation path to
import theorem-admission code.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from flint import arb

from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.legendre_schur import harmonic
from scripts.cert.matrices import RationalInterval, RationalIntervalMatrix


def dyadic_outward_interval(value: arb, bits: int) -> RationalInterval:
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


def coarsen_matrix(matrix: list[list[arb]], bits: int) -> RationalIntervalMatrix:
    return RationalIntervalMatrix(
        [[dyadic_outward_interval(value, bits) for value in row] for row in matrix]
    )


def force_exact_parity_zeros(matrix: RationalIntervalMatrix) -> RationalIntervalMatrix:
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


def _exact_ldl_midpoint(
    matrix: list[list[RationalInterval]],
) -> tuple[list[list[Fraction]], list[Fraction]]:
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


def parity_block(
    matrix: list[list[RationalInterval]], parity: int
) -> list[list[RationalInterval]]:
    if parity not in (0, 1):
        raise ValueError("parity must be 0 or 1")
    indices = list(range(parity, len(matrix), 2))
    return [[matrix[i][j] for j in indices] for i in indices]


def make_witness(
    block: list[list[RationalInterval]],
    witness_bits: int,
) -> tuple[list[list[Fraction]], Fraction]:
    if not block or any(len(row) != len(block) for row in block):
        raise ValueError("witness block must be a non-empty square matrix")
    lower, _ = _exact_ldl_midpoint(block)
    inverse = _inverse_lower_triangular(lower)
    witness: list[list[Fraction]] = []
    for i, row in enumerate(inverse):
        witness.append(
            [
                Fraction(0)
                if j > i
                else _round_fraction_nearest_dyadic(value, witness_bits)
                for j, value in enumerate(row)
            ]
        )
    margin = _gershgorin_margin(_exact_congruence(witness, block))
    if margin <= 0:
        raise RuntimeError(
            "rational congruence witness failed strict Gershgorin positivity"
        )
    return witness, margin


def exact_matrix_json(matrix: list[list[Fraction]]) -> dict[str, Any]:
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


def interval_matrix_json(matrix: RationalIntervalMatrix) -> dict[str, Any]:
    return {"dimension": matrix.dim, "entries": matrix.to_entries()}


def schur_from_serialized_inputs(
    a_matrix: RationalIntervalMatrix,
    gv: RationalIntervalMatrix,
    g2: RationalIntervalMatrix,
    gr: RationalIntervalMatrix,
    c_t: RationalInterval,
    c2: RationalInterval,
    rho_r: RationalInterval,
    dimension: int,
) -> tuple[list[list[RationalInterval]], Fraction]:
    matrices = (a_matrix, gv, g2, gr)
    if dimension < 1 or any(matrix.dim != dimension for matrix in matrices):
        raise ValueError("all serialized matrices must match the positive dimension")
    if not all(matrix.is_symmetric() for matrix in matrices):
        raise ValueError("all serialized matrices must be exactly symmetric")
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
