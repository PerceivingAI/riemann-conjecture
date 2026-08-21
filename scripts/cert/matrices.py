"""Rigorous matrix operations, exact rational reductions, and LDL^T certificates.

This module provides:
1. Exact rational interval arithmetic (RationalInterval) with Python Fractions.
2. Conversion of Arb interval matrices (arb_mat) to outward rational intervals.
3. Exact rational linear algebra with fmpq_mat (det, inv, charpoly, rref).
4. Exact interval LDL^T decomposition for provable positive-definiteness certificates.
5. FLINT eigenvalue enclosures strictly as secondary sanity cross-checks.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from flint import arb, arb_mat, ctx, fmpq, fmpq_mat

from scripts.cert.constants import arb_to_rational_enclosure


class RationalInterval:
    """Exact rational interval [lo, hi] using Python Fractions."""

    __slots__ = ("lo", "hi")

    def __init__(self, lo: Fraction | int, hi: Fraction | int | None = None) -> None:
        if hi is None:
            self.lo = Fraction(lo)
            self.hi = Fraction(lo)
        else:
            self.lo = Fraction(lo)
            self.hi = Fraction(hi)
        if self.lo > self.hi:
            raise ValueError(f"Invalid interval: lo ({self.lo}) > hi ({self.hi})")

    @classmethod
    def from_arb(cls, x: arb) -> RationalInterval:
        """Create exact rational interval enclosure from an Arb ball."""
        lo, hi = arb_to_rational_enclosure(x)
        return cls(lo, hi)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> RationalInterval:
        lo = Fraction(int(d["lo_num"]), int(d["lo_den"]))
        hi = Fraction(int(d["hi_num"]), int(d["hi_den"]))
        return cls(lo, hi)

    def to_dict(self) -> dict[str, str]:
        return {
            "lo_num": str(self.lo.numerator),
            "lo_den": str(self.lo.denominator),
            "hi_num": str(self.hi.numerator),
            "hi_den": str(self.hi.denominator),
        }

    def contains_zero(self) -> bool:
        return self.lo <= 0 <= self.hi

    def is_strictly_positive(self) -> bool:
        return self.lo > 0

    def is_strictly_negative(self) -> bool:
        return self.hi < 0

    def midpoint(self) -> Fraction:
        return (self.lo + self.hi) / 2

    def radius(self) -> Fraction:
        return (self.hi - self.lo) / 2

    def __add__(self, other: RationalInterval | Fraction | int) -> RationalInterval:
        if not isinstance(other, RationalInterval):
            other = RationalInterval(other)
        return RationalInterval(self.lo + other.lo, self.hi + other.hi)

    def __radd__(self, other: Fraction | int) -> RationalInterval:
        return self.__add__(other)

    def __sub__(self, other: RationalInterval | Fraction | int) -> RationalInterval:
        if not isinstance(other, RationalInterval):
            other = RationalInterval(other)
        return RationalInterval(self.lo - other.hi, self.hi - other.lo)

    def __rsub__(self, other: Fraction | int) -> RationalInterval:
        return RationalInterval(other) - self

    def __mul__(self, other: RationalInterval | Fraction | int) -> RationalInterval:
        if not isinstance(other, RationalInterval):
            other = RationalInterval(other)
        products = [
            self.lo * other.lo,
            self.lo * other.hi,
            self.hi * other.lo,
            self.hi * other.hi,
        ]
        return RationalInterval(min(products), max(products))

    def __rmul__(self, other: Fraction | int) -> RationalInterval:
        return self.__mul__(other)

    def __truediv__(self, other: RationalInterval | Fraction | int) -> RationalInterval:
        if not isinstance(other, RationalInterval):
            other = RationalInterval(other)
        if other.contains_zero():
            raise ZeroDivisionError(f"Cannot divide by interval containing zero: [{other.lo}, {other.hi}]")
        quotients = [
            self.lo / other.lo,
            self.lo / other.hi,
            self.hi / other.lo,
            self.hi / other.hi,
        ]
        return RationalInterval(min(quotients), max(quotients))

    def sqr(self) -> RationalInterval:
        """Exact interval squaring."""
        if self.contains_zero():
            return RationalInterval(Fraction(0), max(self.lo**2, self.hi**2))
        return RationalInterval(min(self.lo**2, self.hi**2), max(self.lo**2, self.hi**2))

    def __repr__(self) -> str:
        return f"[{self.lo}, {self.hi}]"


class RationalIntervalMatrix:
    """N x N matrix of exact RationalInterval elements."""

    def __init__(self, rows: list[list[RationalInterval]]) -> None:
        if not rows:
            raise ValueError("Matrix must be non-empty")
        n = len(rows)
        for r in rows:
            if len(r) != n:
                raise ValueError(f"Matrix must be square: expected {n} cols, got {len(r)}")
        self.dim = n
        self.rows = rows

    @classmethod
    def from_arb_mat(cls, mat: arb_mat) -> RationalIntervalMatrix:
        n = mat.nrows()
        if n != mat.ncols():
            raise ValueError("Matrix must be square")
        rows: list[list[RationalInterval]] = []
        for i in range(n):
            row: list[RationalInterval] = []
            for j in range(n):
                row.append(RationalInterval.from_arb(mat[i, j]))
            rows.append(row)
        return cls(rows)

    @classmethod
    def from_entries(cls, dim: int, entries: list[dict[str, Any]]) -> RationalIntervalMatrix:
        grid = [[RationalInterval(0, 0) for _ in range(dim)] for _ in range(dim)]
        for entry in entries:
            r = int(entry["row"])
            c = int(entry["col"])
            grid[r][c] = RationalInterval.from_dict(entry)
        return cls(grid)

    def to_entries(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for i in range(self.dim):
            for j in range(self.dim):
                d = self.rows[i][j].to_dict()
                d["row"] = i
                d["col"] = j
                entries.append(d)
        return entries

    def is_symmetric(self) -> bool:
        for i in range(self.dim):
            for j in range(i + 1, self.dim):
                rij = self.rows[i][j]
                rji = self.rows[j][i]
                if rij.lo != rji.lo or rij.hi != rji.hi:
                    return False
        return True

    def to_fmpq_mat_midpoint(self) -> fmpq_mat:
        """Extract exact midpoint matrix as FLINT fmpq_mat."""
        flat: list[fmpq] = []
        for i in range(self.dim):
            for j in range(self.dim):
                mid = self.rows[i][j].midpoint()
                flat.append(fmpq(mid.numerator, mid.denominator))
        return fmpq_mat(self.dim, self.dim, flat)

    def exact_ldl(self) -> tuple[list[list[RationalInterval]], list[RationalInterval], bool]:
        """Perform exact rational interval LDL^T decomposition: A = L * D * L^T.

        Returns:
            (L, D, is_positive_definite)
            where L is unit lower-triangular, D is diagonal, and
            is_positive_definite is True iff every diagonal interval D_j has lo > 0.
        """
        n = self.dim
        L: list[list[RationalInterval]] = [
            [RationalInterval(1 if i == j else 0) for j in range(n)] for i in range(n)
        ]
        D: list[RationalInterval] = [RationalInterval(0) for _ in range(n)]

        for j in range(n):
            # D_j = A_jj - sum_{k=0}^{j-1} L_jk^2 * D_k
            sum_diag = RationalInterval(0)
            for k in range(j):
                sum_diag += L[j][k].sqr() * D[k]

            d_j = self.rows[j][j] - sum_diag
            D[j] = d_j

            if not d_j.is_strictly_positive():
                return L, D, False

            # Compute L_ij for i > j:
            # L_ij = (1 / D_j) * (A_ij - sum_{k=0}^{j-1} L_ik * L_jk * D_k)
            for i in range(j + 1, n):
                sum_off = RationalInterval(0)
                for k in range(j):
                    sum_off += L[i][k] * L[j][k] * D[k]

                diff = self.rows[i][j] - sum_off
                L[i][j] = diff / d_j

        is_pos_def = all(d.is_strictly_positive() for d in D)
        return L, D, is_pos_def


def fmpq_mat_properties(mat: fmpq_mat) -> dict[str, Any]:
    """Compute exact rational linear algebra properties with FLINT fmpq_mat."""
    det_val = mat.det()
    rank = mat.nrows()

    try:
        inv_mat = mat.inv()
        inv_str = inv_mat.str()
        is_invertible = True
    except Exception:
        inv_str = "non-invertible"
        is_invertible = False

    try:
        charpoly_str = mat.charpoly().str()
    except Exception:
        charpoly_str = "unavailable"

    return {
        "dimension": mat.nrows(),
        "determinant": str(det_val),
        "is_invertible": is_invertible,
        "inverse": inv_str,
        "charpoly": charpoly_str,
    }


def arb_mat_eigenvalue_cross_check(mat: arb_mat, prec: int = 128) -> dict[str, Any]:
    """Compute FLINT matrix eigenvalue enclosure strictly as a secondary sanity cross-check.

    WARNING: FLINT eigenvalue enclosures are experimental and must NOT serve as the
    primary certificate of positive definiteness. The exact rational interval LDL^T
    decomposition is the authoritative proof object.
    """
    with ctx.workprec(prec):
        try:
            eigs = mat.eig()
            eig_balls = [e.str(30, radius=True) for e in eigs]
            all_real_pos = all(arb(0) in e.imag and arb(0) < e.real for e in eigs)
            return {
                "status": "computed",
                "eigenvalues": eig_balls,
                "all_real_positive": all_real_pos,
                "role": "secondary_cross_check_only",
            }
        except Exception as err:
            return {
                "status": "failed",
                "error": str(err),
                "role": "secondary_cross_check_only",
            }


def verify_matrix_positivity_ldl(mat: RationalIntervalMatrix) -> dict[str, Any]:
    """Verify positive definiteness using exact rational interval LDL^T decomposition."""
    L, D, is_pos_def = mat.exact_ldl()
    d_entries = [d.to_dict() for d in D]
    d_bounds = [f"[{d.lo}, {d.hi}]" for d in D]

    return {
        "verified_positive_definite": is_pos_def,
        "dimension": mat.dim,
        "is_symmetric": mat.is_symmetric(),
        "diagonal_intervals": d_entries,
        "diagonal_intervals_str": d_bounds,
        "min_diagonal_lower_bound": str(min(d.lo for d in D)) if D else "0",
    }
