"""Native exact witnesses for multi-prime candidates; frozen v1 stays separate.

Fraction-free elimination accumulates the inverse unit-lower midpoint LDL
factor directly. All pivots, dyadic rounding and interval margins are exact.
No numerical approximation or theorem-admission decision occurs here.
"""
from __future__ import annotations

from fractions import Fraction

from flint import fmpq, fmpq_mat, fmpz_mat

from scripts.cert.matrices import RationalInterval


def _q(value: Fraction) -> fmpq:
    return fmpq(value.numerator, value.denominator)


def _inverse_midpoint_factor(midpoint: fmpq_mat) -> fmpz_mat:
    """Return integer rows of L^-1, divided by their diagonal entries.

    Bareiss pivots are leading principal determinants of the common-denominator
    integer midpoint matrix. After positive earlier pivots, their signs equal
    the next LDL pivot's sign. The accumulated elimination row at index i has
    diagonal det(M[:i, :i]); dividing that row by its diagonal gives L^-1.
    Exact divisibility by the preceding pivot avoids rational cubic-loop gcds.
    """
    matrix, _ = midpoint.numer_denom()
    n = midpoint.nrows()
    transform = fmpz_mat(n, n)
    for i in range(n):
        transform[i, i] = 1
    previous = 1
    for j in range(n):
        pivot = matrix[j, j]
        if pivot <= 0:
            raise RuntimeError(f"midpoint LDL pivot {j} is not positive")
        for i in range(j + 1, n):
            multiplier = matrix[i, j]
            for k in range(j):
                transform[i, k] = (
                    pivot * transform[i, k] - multiplier * transform[j, k]
                ) // previous
            transform[i, j] = -multiplier
            transform[i, i] = pivot
            # Only the lower triangle is needed. Column j remains unchanged
            # until every trailing row has consumed its elimination multiplier.
            for k in range(j + 1, i + 1):
                matrix[i, k] = (
                    pivot * matrix[i, k] - multiplier * matrix[k, j]
                ) // previous
        previous = pivot
    return transform


def make_witness(
    block: list[list[RationalInterval]], witness_bits: int,
) -> tuple[list[list[Fraction]], Fraction]:
    """Construct the same exact dyadic congruence witness as frozen v1.

    The midpoint/radius product is exactly the entrywise interval congruence:
    W C W^T +/- |W| R |W|^T. Native matrix products replace Fraction loops;
    the independent auditor remains a separate implementation.
    """
    if not block or any(len(row) != len(block) for row in block):
        raise ValueError("witness block must be a non-empty square matrix")
    n = len(block)
    midpoint, radius = fmpq_mat(n, n), fmpq_mat(n, n)
    for i, row in enumerate(block):
        for j, entry in enumerate(row):
            lo, hi = _q(entry.lo), _q(entry.hi)
            midpoint[i, j] = (lo + hi) / 2
            radius[i, j] = (hi - lo) / 2
    inverse = _inverse_midpoint_factor(midpoint)
    if witness_bits < 8:
        raise ValueError("witness bits must be at least 8")
    denominator = 1 << witness_bits
    zero = Fraction(0)
    witness = [[zero] * n for _ in range(n)]
    native, absolute = fmpq_mat(n, n), fmpq_mat(n, n)
    for i in range(n):
        divisor = inverse[i, i]
        for j in range(i + 1):
            numerator = inverse[i, j]
            quotient, remainder = divmod(abs(numerator) * denominator, divisor)
            if 2 * remainder >= divisor:
                quotient += 1
            if numerator < 0:
                quotient = -quotient
            value = fmpq(quotient, denominator)
            native[i, j] = value
            absolute[i, j] = abs(value)
            witness[i][j] = Fraction(int(value.p), int(value.q))
    centers = native * midpoint * native.transpose()
    radii = absolute * radius * absolute.transpose()
    margin = min(
        centers[i, i] - radii[i, i] - sum(
            (abs(centers[i, j]) + radii[i, j] for j in range(n) if j != i),
            fmpq(0),
        )
        for i in range(n)
    )
    if margin <= 0:
        raise RuntimeError("rational congruence witness failed strict Gershgorin positivity")
    return witness, Fraction(int(margin.p), int(margin.q))
