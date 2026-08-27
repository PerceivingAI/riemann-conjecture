"""Precision/conditioning observability helpers for continuation tooling.

These helpers expose widths, radii, and widest-entry locations for rigorous Arb
matrices and outward-rounded exact rational interval matrices. They are
observability only: they do not decide theorem admission, positivity, or
certificate validity.
"""

from __future__ import annotations

from fractions import Fraction

from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.matrices import RationalIntervalMatrix


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def arb_width_fraction(value: object) -> Fraction:
    lo, hi = arb_to_rational_enclosure(value)  # type: ignore[arg-type]
    return hi - lo


def arb_width_float(value: object) -> float:
    return float(arb_width_fraction(value))


def arb_midpoint_float(value: object) -> float:
    midpoint = value.mid().fmpq()  # type: ignore[attr-defined]
    return float(Fraction(int(midpoint.p), int(midpoint.q)))


def arb_matrix_width_diagnostics(matrix: list[list[object]]) -> dict[str, object]:
    if not matrix or not matrix[0]:
        raise ValueError("matrix must be non-empty")
    widest: tuple[Fraction, int, int, object] | None = None
    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            width = arb_width_fraction(value)
            if widest is None or width > widest[0]:
                widest = (width, row_index, column_index, value)
    if widest is None:
        raise ValueError("matrix must contain at least one entry")
    width, row_index, column_index, value = widest
    radius = width / 2
    return {
        "max_width": float(width),
        "max_radius": float(radius),
        "row": row_index,
        "column": column_index,
        "midpoint_at_widest_entry": arb_midpoint_float(value),
    }


def exact_matrix_width_diagnostics(matrix: RationalIntervalMatrix) -> dict[str, object]:
    widest: tuple[Fraction, int, int] | None = None
    for row_index, row in enumerate(matrix.rows):
        for column_index, interval in enumerate(row):
            width = interval.hi - interval.lo
            if widest is None or width > widest[0]:
                widest = (width, row_index, column_index)
    if widest is None:
        raise ValueError("matrix must contain at least one entry")
    width, row_index, column_index = widest
    interval = matrix.rows[row_index][column_index]
    return {
        "max_width": fraction_text(width),
        "max_radius": fraction_text(width / 2),
        "row": row_index,
        "column": column_index,
        "midpoint_at_widest_entry": fraction_text(interval.midpoint()),
    }
