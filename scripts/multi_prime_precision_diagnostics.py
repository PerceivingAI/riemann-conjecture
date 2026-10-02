"""Exact observability and scaled midpoint diagnostics for multi-prime tooling.

Widths and rescaled eigenvalues serialize as rationals. Midpoint eigenvalues
remain numerical diagnostics, not rigorous spectral bounds. Frozen v1 helpers
in precision_diagnostics.py are deliberately unchanged.
"""

from __future__ import annotations

from fractions import Fraction
import math

import numpy as np
from scipy.linalg import eigvalsh

from scripts.precision_diagnostics import arb_width_fraction, fraction_text


def arb_midpoint_fraction(value: object) -> Fraction:
    midpoint = value.mid().fmpq()  # type: ignore[attr-defined]
    return Fraction(int(midpoint.p), int(midpoint.q))


def arb_matrix_exact_width_diagnostics(matrix: list[list[object]]) -> dict[str, object]:
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
    return {
        "max_width": fraction_text(width),
        "max_radius": fraction_text(width / 2),
        "row": row_index,
        "column": column_index,
        "midpoint_at_widest_entry": fraction_text(arb_midpoint_fraction(value)),
    }


def scaled_midpoint_eigenvalue(
    matrix: list[list[object]], norms: list[Fraction], *, largest: bool = False,
) -> tuple[str | None, dict[str, object]]:
    """Normalize after exact power-of-two scaling, then restore units exactly.

    For d=min(norms), max(abs(midpoint))/d bounds every normalized entry.
    Scaling by a power of two above that bound keeps every binary64 input
    bounded by one. Losing a nonzero entry during conversion/normalization
    makes the diagnostic unavailable, rather than silently changing its sign.
    """
    n = len(matrix)
    if n == 0 or len(norms) != n or any(len(row) != n for row in matrix):
        raise ValueError("matrix and norms must have matching positive dimensions")
    if any(norm <= 0 for norm in norms):
        raise ValueError("basis norms must be positive")
    midpoints = [[arb_midpoint_fraction(value) for value in row] for row in matrix]
    bound = max(abs(value) for row in midpoints for value in row) / min(norms)
    exponent = bound.numerator.bit_length() - bound.denominator.bit_length() + 1 if bound else 0
    scale = Fraction(1 << exponent) if exponent >= 0 else Fraction(1, 1 << -exponent)
    metadata: dict[str, object] = {
        "status": "unavailable",
        "scale_power_of_two": exponent,
        "scaled_eigenvalue": None,
        "reason": None,
    }
    try:
        norm_floats = [float(norm) for norm in norms]
    except OverflowError:
        metadata["reason"] = "basis_norm_outside_binary64"
        return None, metadata
    if any(not math.isfinite(norm) or norm <= 0 for norm in norm_floats):
        metadata["reason"] = "basis_norm_outside_binary64"
        return None, metadata
    normalization = [norm ** -0.5 for norm in norm_floats]
    normalized = np.empty((n, n), dtype=float)
    for i, row in enumerate(midpoints):
        for j, value in enumerate(row):
            entry = float(value / scale) * normalization[i] * normalization[j]
            if not math.isfinite(entry) or (value != 0 and entry == 0):
                metadata["reason"] = "normalized_entry_outside_binary64"
                return None, metadata
            normalized[i, j] = entry
    index = n - 1 if largest else 0
    try:
        eigenvalue = float(eigvalsh(normalized, subset_by_index=[index, index])[0])
    except np.linalg.LinAlgError:
        metadata["reason"] = "eigensolver_did_not_converge"
        return None, metadata
    if not math.isfinite(eigenvalue):
        metadata["reason"] = "non_finite_scaled_eigenvalue"
        return None, metadata
    metadata.update(status="available", scaled_eigenvalue=eigenvalue)
    return fraction_text(Fraction(eigenvalue) * scale), metadata
