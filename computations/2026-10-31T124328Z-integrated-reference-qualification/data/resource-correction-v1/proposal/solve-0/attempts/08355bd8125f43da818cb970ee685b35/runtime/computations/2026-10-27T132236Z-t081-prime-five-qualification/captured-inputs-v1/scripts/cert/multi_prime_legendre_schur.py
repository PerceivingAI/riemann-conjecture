"""Rigorous Legendre-Schur assembly with generic active prime powers.

This is the additive post-v1 assembler defined by the multi-prime contract.
It deliberately leaves ``assemble_exact_prime_schur()`` and
``first_prime_matrices()`` untouched.  The archimedean potential uses exact
grouped harmonic-moment contractions of the same analytic integrals; the Suzuki
residual is unchanged.  ``prime_power_terms`` supplies the complete arithmetic.

The arithmetic operator is formed first as

    P = sum_m P_m,

then its low matrix, operator-square matrix, and tail Gram are derived from the
combined piecewise action.  Therefore mixed products such as
``P_2 P_3 + P_3 P_2`` are present by construction.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Sequence

from flint import acb, arb, ctx, fmpq, fmpq_poly

from scripts.cert.constants import c_T_enclosure
from scripts.cert.legendre_schur import (
    harmonic,
    legendre_norm_sq,
    legendre_polynomials,
)
from scripts.cert.prime_power_terms import (
    ArbMatrix,
    PrimePowerTerm,
    _exact_inner,
    _exact_polynomials,
    _opposite_parity,
    _polynomial_parities,
    assemble_active_prime_power_operator,
)
from scripts.cert.residual_kernel import (
    _suzuki_residual_series_coefficients,
    _suzuki_residual_tail_radius,
)


def _potential_matrices(
    polys: Sequence[Sequence[Fraction]], prec: int,
) -> tuple[ArbMatrix, ArbMatrix]:
    """Contract rational harmonic moments before introducing Arb constants."""
    exact = _exact_polynomials(polys)
    parities = _polynomial_parities(polys)
    max_power = 2 * max(poly.degree() for poly in exact)
    harmonics, harmonics_squared = [fmpq(0)], [fmpq(0)]
    for k in range(1, max_power + 3):
        harmonics.append(harmonics[-1] + fmpq(1, k))
        harmonics_squared.append(harmonics_squared[-1] + fmpq(1, k * k))
    moments = []
    for r in range(max_power // 2 + 1):
        alpha = 2 * harmonics[2 * r + 2] - harmonics[r + 1]
        beta = 4 * harmonics_squared[2 * r + 2] - harmonics_squared[r + 1]
        u = fmpq(1, 2 * r + 1)
        moments.append((u, alpha * u, (alpha * alpha + beta) * u))
    with ctx.workprec(prec):
        log2, pi = arb.const_log2(), arb.pi()
        minus_two_log2 = -2 * log2
        square_u_factor = 2 * log2 * log2 - pi * pi / 6
        v, v2 = _zero_matrix(len(polys)), _zero_matrix(len(polys))
        for i, left in enumerate(exact):
            for j in range(i, len(exact)):
                if _opposite_parity(parities[i], parities[j]):
                    continue
                u, e, f = fmpq(0), fmpq(0), fmpq(0)
                for power, coefficient in enumerate((left * exact[j]).coeffs()):
                    if coefficient and power % 2 == 0:
                        moment_u, moment_e, moment_f = moments[power // 2]
                        u += coefficient * moment_u
                        e += coefficient * moment_e
                        f += coefficient * moment_f
                u_ball, e_ball = arb(u), arb(e)
                value = e_ball + minus_two_log2 * u_ball
                square = square_u_factor * u_ball + minus_two_log2 * e_ball + arb(f / 2)
                v[i][j] = v[j][i] = value
                v2[i][j] = v2[j][i] = square
        return v, v2


def _abs_power_action(
    power: int, poly: fmpq_poly, binomials: Sequence[int],
) -> fmpq_poly:
    """Exact split integral of |x-y|^power, evaluated with native rationals."""
    out = [fmpq(0) for _ in range(len(poly) + power + 2)]
    for k, coefficient in enumerate(poly.coeffs()):
        if not coefficient:
            continue
        for r, binomial in enumerate(binomials):
            denominator = r + k + 1
            left = fmpq(binomial * (-1) ** r, denominator)
            right = fmpq(binomial * (-1) ** (power - r), denominator)
            out[power + k + 1] += coefficient * (left - right)
            out[power - r] += coefficient * (right - left * (-1) ** (r + k + 1))
    return fmpq_poly(out)


def _residual_truncation_operator(
    polys: Sequence[Sequence[Fraction]], order: int, prec: int,
    support_num: int, support_den: int,
) -> tuple[list[fmpq_poly], ArbMatrix, ArbMatrix, arb]:
    """Same residual polynomial and remainder as v1; no Fraction convolution."""
    support = fmpq(support_num, support_den)
    exact = _exact_polynomials(polys)
    parities = _polynomial_parities(polys)
    terms = [
        (degree, -coefficient * support ** (degree + 1),
         tuple(math.comb(degree, r) for r in range(degree + 1)))
        for degree, coefficient in enumerate(_suzuki_residual_series_coefficients(order))
        if coefficient
    ]
    basis_coefficients = [poly.coeffs() for poly in exact]
    occupied_degrees = sorted({
        k for coefficients in basis_coefficients for k, c in enumerate(coefficients) if c
    })
    # R_K is linear. Its action on x^k depends on support/order/k, not on
    # the basis index, so compute that exact action once and combine natively.
    monomial_images: dict[int, fmpq_poly] = {}
    for k in occupied_degrees:
        monomial = fmpq_poly([0] * k + [1])
        monomial_images[k] = sum(
            (_abs_power_action(degree, monomial, binomials) * scale
             for degree, scale, binomials in terms),
            fmpq_poly(),
        )
    images = [
        sum((monomial_images[k] * c for k, c in enumerate(coefficients) if c), fmpq_poly())
        for coefficients in basis_coefficients
    ]
    with ctx.workprec(prec):
        low, square = _zero_matrix(len(polys)), _zero_matrix(len(polys))
        for i, poly in enumerate(exact):
            for j in range(i, len(exact)):
                # The even |x-y| kernel preserves coefficient-certified parity.
                if _opposite_parity(parities[i], parities[j]):
                    continue
                low[i][j] = low[j][i] = arb(_exact_inner(poly, images[j]))
                square[i][j] = square[j][i] = arb(_exact_inner(images[i], images[j]))
        two_t = arb(2 * support_num) / support_den
        delta = two_t * _suzuki_residual_tail_radius(acb(two_t), order)
        return images, low, square, delta


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
    inverse_norms = tuple(_arb_fraction(1 / norm) for norm in norms)
    for i in range(n):
        for j in range(i, n):
            value = arb(0)
            for k in range(n):
                value += a[i][k] * a[k][j] * inverse_norms[k]
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

        V, V2 = _potential_matrices(polys, prec)
        arithmetic = assemble_active_prime_power_operator(
            polys,
            support_num=support_exact.numerator,
            support_den=support_exact.denominator,
            prec=prec,
        )
        P = arithmetic.p_matrix
        P_squared = arithmetic.p_squared_matrix
        GP = arithmetic.g_p

        _, Rk, Rk2, delta_R = _residual_truncation_operator(
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
