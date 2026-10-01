"""Rigorous Legendre-Schur assembly with generic active prime powers.

This is the additive post-v1 assembler defined by the multi-prime contract.
It deliberately leaves ``assemble_exact_prime_schur()`` and
``first_prime_matrices()`` untouched.  The archimedean potential and Suzuki
residual components reuse the already-rigorous shared implementations, while
the complete arithmetic component is supplied by ``prime_power_terms``.

The arithmetic operator is formed first as

    P = sum_m P_m,

then its low matrix, operator-square matrix, and tail Gram are derived from the
combined piecewise action.  Therefore mixed products such as
``P_2 P_3 + P_3 P_2`` are present by construction.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

from flint import acb, arb, ctx

from scripts.cert.constants import c_T_enclosure
from scripts.cert.legendre_schur import (
    harmonic,
    legendre_norm_sq,
    legendre_polynomials,
    potential_matrices,
    residual_truncation_operator,
)
from scripts.cert.prime_power_terms import (
    ArbMatrix,
    PrimePowerTerm,
    assemble_active_prime_power_operator,
)
from scripts.cert.residual_kernel import (
    _suzuki_residual_series_coefficients,
    _suzuki_residual_tail_radius,
)


def _arb_fraction(value: Fraction) -> arb:
    return arb(value.numerator) / value.denominator


def _zero_matrix(n: int) -> ArbMatrix:
    return [[arb(0) for _ in range(n)] for _ in range(n)]


def _mat_add(a: ArbMatrix, b: ArbMatrix) -> ArbMatrix:
    n = len(a)
    return [[a[i][j] + b[i][j] for j in range(n)] for i in range(n)]


def _mat_sub(a: ArbMatrix, b: ArbMatrix) -> ArbMatrix:
    n = len(a)
    return [[a[i][j] - b[i][j] for j in range(n)] for i in range(n)]


def _mat_scale(a: ArbMatrix, scale: arb | Fraction | int) -> ArbMatrix:
    s = scale if isinstance(scale, arb) else _arb_fraction(Fraction(scale))
    return [[s * value for value in row] for row in a]


def _mat_mul_diag_inverse(a: ArbMatrix, norms: Sequence[Fraction]) -> ArbMatrix:
    """Return ``A D^-1 A`` for symmetric ``A`` and exact diagonal ``D``."""
    n = len(a)
    out = _zero_matrix(n)
    for i in range(n):
        for j in range(i, n):
            value = arb(0)
            for k in range(n):
                value += a[i][k] * a[k][j] / _arb_fraction(norms[k])
            out[i][j] = value
            out[j][i] = value
    return out


def _chain_vertices(term: PrimePowerTerm) -> int:
    """Rigorously determine the essential compressed-shift chain length.

    On the scaled interval ``[-1,1]`` the chain length is
    ``ceil(2 / tau_m)``.  A topology decision is accepted only when Arb proves
    that the ratio lies strictly between two adjacent integers.  If the
    requested precision cannot separate a threshold, fail closed.
    """
    ratio = 2 / term.tau
    if not ratio > 1:
        raise ValueError(f"active term m={term.m} does not certify tau_m < 2")

    upper_integer = 2
    while True:
        lower_integer = upper_integer - 1
        if ratio > lower_integer and ratio < upper_integer:
            return upper_integer
        if ratio > upper_integer:
            upper_integer += 1
            continue
        raise ValueError(
            "cannot rigorously determine compressed-shift chain length for "
            f"m={term.m} at precision={term.precision_bits}; increase Arb precision"
        )


def compressed_shift_norm_bound(term: PrimePowerTerm, prec: int) -> arb:
    """Return the exact path-graph norm as a rigorous Arb enclosure."""
    if prec < 32:
        raise ValueError("prec must be at least 32 bits")
    with ctx.workprec(prec):
        vertices = _chain_vertices(term)
        if vertices == 2:
            # 2 cos(pi/3) = 1 exactly; keeping this exact reproduces v1's
            # one-prime complement loss without unnecessary interval widening.
            return arb(1)
        if vertices == 3:
            # 2 cos(pi/4) = sqrt(2).
            return arb(2).sqrt()
        return 2 * (arb.pi() / (vertices + 1)).cos()


def _residual_rho(
    support_t: arb,
    residual_order: int,
) -> arb:
    u_max = 2 * support_t
    coeffs = _suzuki_residual_series_coefficients(residual_order)
    residual_abs = arb(0)
    for degree, coefficient in enumerate(coeffs):
        c_abs = Fraction(abs(int(coefficient.p)), int(coefficient.q))
        residual_abs += _arb_fraction(c_abs) * u_max**degree
    residual_abs += _suzuki_residual_tail_radius(acb(u_max), residual_order)
    return 2 * support_t * residual_abs


def assemble_multi_prime_schur(
    n: int = 32,
    prec: int = 256,
    residual_order: int = 32,
    support_num: int = 3,
    support_den: int = 5,
    require_positive_mu: bool = True,
) -> dict[str, object]:
    """Assemble the rigorous grouped ``V,P,R`` Legendre-Schur reduction.

    Canonical arithmetic outputs include the certified active prime-power set,
    combined low matrix ``P``, combined operator-square matrix ``P_squared``,
    and ``GP``.  The remaining canonical outputs mirror the established
    one-prime structure: ``A``, ``GV``, ``GR``, ``rho_R``, ``mu``, and
    ``schur``.
    """
    if n < 1:
        raise ValueError("n must be positive")
    if prec < 64:
        raise ValueError("prec must be at least 64 bits")
    if residual_order < 8:
        raise ValueError("residual_order must be at least 8")
    if not isinstance(support_num, int) or not isinstance(support_den, int):
        raise TypeError("support numerator and denominator must be integers")
    if support_num <= 0 or support_den <= 0:
        raise ValueError("support T must be a positive rational")

    with ctx.workprec(prec):
        support_exact = Fraction(support_num, support_den)
        support_t = arb(support_exact.numerator) / support_exact.denominator
        polys = legendre_polynomials(n - 1)
        norms = [legendre_norm_sq(k) for k in range(n)]

        V, V2 = potential_matrices(polys, prec)
        arithmetic = assemble_active_prime_power_operator(
            polys,
            support_num=support_exact.numerator,
            support_den=support_exact.denominator,
            prec=prec,
        )
        P = arithmetic.p_matrix
        P_squared = arithmetic.p_squared_matrix
        GP = arithmetic.g_p

        _, Rk, Rk2, delta_R = residual_truncation_operator(
            polys,
            residual_order,
            prec,
            support_exact.numerator,
            support_exact.denominator,
        )
        cT = c_T_enclosure(
            prec,
            support_exact.numerator,
            support_exact.denominator,
        )

        A = _zero_matrix(n)
        for i in range(n):
            for j in range(n):
                value = V[i][j] + P[i][j] + Rk[i][j]
                if i == j:
                    norm = _arb_fraction(norms[i])
                    value += _arb_fraction(harmonic(i)) * norm
                    value -= (cT + delta_R) * norm
                A[i][j] = value

        GV = _mat_sub(V2, _mat_mul_diag_inverse(V, norms))
        GRk = _mat_sub(Rk2, _mat_mul_diag_inverse(Rk, norms))
        GR = _mat_scale(GRk, 2)
        for i in range(n):
            GR[i][i] += 2 * delta_R * delta_R * _arb_fraction(norms[i])

        rho_R = _residual_rho(support_t, residual_order)
        norm_bounds: dict[int, arb] = {}
        arithmetic_loss = arb(0)
        for term in arithmetic.terms:
            bound = compressed_shift_norm_bound(term, prec)
            norm_bounds[term.m] = bound
            arithmetic_loss += term.coefficient * bound

        mu = _arb_fraction(harmonic(n)) - cT - arithmetic_loss - rho_R
        mu_positive = bool(mu.lower() > 0)
        if require_positive_mu and not mu_positive:
            raise RuntimeError("failed to certify positive complement mu_N")

        schur: ArbMatrix | None = None
        if mu_positive:
            grams = _mat_add(_mat_add(GV, GP), GR)
            schur = _mat_sub(A, _mat_scale(grams, arb(3) / mu))

        return {
            "dimension": n,
            "support_num": support_exact.numerator,
            "support_den": support_exact.denominator,
            "support_T": support_t,
            "precision_bits": prec,
            "residual_order": residual_order,
            "norms": norms,
            "active_terms": arithmetic.terms,
            "arithmetic_norm_bounds": norm_bounds,
            "P": P,
            "P_squared": P_squared,
            "A": A,
            "GV": GV,
            "GP": GP,
            "GR": GR,
            "delta_R": delta_R,
            "rho_R": rho_R,
            "mu": mu,
            "mu_positive": mu_positive,
            "schur": schur,
        }
