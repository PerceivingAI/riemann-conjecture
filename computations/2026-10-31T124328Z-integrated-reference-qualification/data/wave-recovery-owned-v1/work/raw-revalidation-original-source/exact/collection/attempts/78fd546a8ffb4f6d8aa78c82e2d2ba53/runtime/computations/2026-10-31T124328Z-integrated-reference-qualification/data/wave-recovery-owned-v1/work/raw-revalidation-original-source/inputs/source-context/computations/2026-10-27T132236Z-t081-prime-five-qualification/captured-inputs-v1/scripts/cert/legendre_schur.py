"""Exact/rigorous Legendre-Schur assembly for the first-prime Weil form.

All polynomial algebra is exact over Fraction. Transcendental quantities enter
only as Arb balls. The module assembles the finite low block and component tail
Gram bounds used by A-20260821-004 and later one-prime support-continuation work.
The reusable assembler accepts an exact rational support T; proof-bearing certificate
profiles remain responsible for locking any theorem-specific support value.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Iterable

from flint import acb, arb, ctx, fmpq

from scripts.cert.constants import (
    c2_enclosure,
    c_T_enclosure,
    log2_enclosure,
    pi_enclosure,
    require_one_prime_support,
    tau_enclosure,
)
from scripts.cert.residual_kernel import _suzuki_residual_series_coefficients, _suzuki_residual_tail_radius

FractionPoly = list[Fraction]
ArbMatrix = list[list[arb]]


def harmonic(n: int, power: int = 1) -> Fraction:
    return sum((Fraction(1, k**power) for k in range(1, n + 1)), Fraction(0))


def poly_trim(poly: FractionPoly) -> FractionPoly:
    out = list(poly)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def poly_add(a: FractionPoly, b: FractionPoly) -> FractionPoly:
    n = max(len(a), len(b))
    out = [Fraction(0) for _ in range(n)]
    for i, value in enumerate(a):
        out[i] += value
    for i, value in enumerate(b):
        out[i] += value
    return poly_trim(out)


def poly_scale(a: FractionPoly, scale: Fraction) -> FractionPoly:
    return poly_trim([scale * value for value in a])


def poly_mul(a: FractionPoly, b: FractionPoly) -> FractionPoly:
    out = [Fraction(0) for _ in range(len(a) + len(b) - 1)]
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] += ai * bj
    return poly_trim(out)


def poly_x_mul(a: FractionPoly) -> FractionPoly:
    return [Fraction(0), *a]


def legendre_polynomials(max_degree: int) -> list[FractionPoly]:
    if max_degree < 0:
        raise ValueError("max_degree must be nonnegative")
    polys: list[FractionPoly] = [[Fraction(1)]]
    if max_degree == 0:
        return polys
    polys.append([Fraction(0), Fraction(1)])
    for n in range(1, max_degree):
        numerator = poly_add(
            poly_scale(poly_x_mul(polys[n]), Fraction(2 * n + 1)),
            poly_scale(polys[n - 1], Fraction(-n)),
        )
        polys.append(poly_scale(numerator, Fraction(1, n + 1)))
    return polys


def exact_poly_integral(poly: FractionPoly) -> Fraction:
    total = Fraction(0)
    for degree, coefficient in enumerate(poly):
        if degree % 2 == 0:
            total += coefficient * Fraction(2, degree + 1)
    return total


def exact_poly_inner(a: FractionPoly, b: FractionPoly) -> Fraction:
    return exact_poly_integral(poly_mul(a, b))


def legendre_norm_sq(n: int) -> Fraction:
    return Fraction(2, 2 * n + 1)


def _arb_fraction(value: Fraction) -> arb:
    return arb(value.numerator) / value.denominator


def _arb_zero_matrix(n: int) -> ArbMatrix:
    return [[arb(0) for _ in range(n)] for _ in range(n)]


def _arb_mat_add(a: ArbMatrix, b: ArbMatrix) -> ArbMatrix:
    n = len(a)
    return [[a[i][j] + b[i][j] for j in range(n)] for i in range(n)]


def _arb_mat_sub(a: ArbMatrix, b: ArbMatrix) -> ArbMatrix:
    n = len(a)
    return [[a[i][j] - b[i][j] for j in range(n)] for i in range(n)]


def _arb_mat_scale(a: ArbMatrix, scale: arb | Fraction | int) -> ArbMatrix:
    s = scale if isinstance(scale, arb) else _arb_fraction(Fraction(scale))
    return [[s * value for value in row] for row in a]


def _arb_mat_mul_diag_inverse(a: ArbMatrix, norms: list[Fraction]) -> ArbMatrix:
    """Return A D^{-1} A for symmetric A and exact diagonal D."""
    n = len(a)
    out = _arb_zero_matrix(n)
    for i in range(n):
        for j in range(i, n):
            value = arb(0)
            for k in range(n):
                value += a[i][k] * a[k][j] / _arb_fraction(norms[k])
            out[i][j] = value
            out[j][i] = value
    return out


def _arb_poly_shift(poly: FractionPoly, shift: arb) -> list[arb]:
    out = [arb(0) for _ in range(len(poly))]
    for degree, coefficient in enumerate(poly):
        c = _arb_fraction(coefficient)
        for power in range(degree + 1):
            out[power] += c * math.comb(degree, power) * shift ** (degree - power)
    return out


def _arb_poly_mul(a: Iterable[arb], b: Iterable[arb]) -> list[arb]:
    aa = list(a)
    bb = list(b)
    out = [arb(0) for _ in range(len(aa) + len(bb) - 1)]
    for i, ai in enumerate(aa):
        for j, bj in enumerate(bb):
            out[i + j] += ai * bj
    return out


def _arb_poly_integral_between(poly: Iterable[arb], lower: arb, upper: arb) -> arb:
    total = arb(0)
    for degree, coefficient in enumerate(poly):
        total += coefficient * (upper ** (degree + 1) - lower ** (degree + 1)) / (degree + 1)
    return total


def potential_moment(power: int, log2: arb) -> arb:
    """Integral of V(x) x^power on [-1,1], V=-1/2 log(1-x^2)."""
    if power % 2:
        return arb(0)
    r = power // 2
    h_big = _arb_fraction(harmonic(2 * r + 2))
    h_small = _arb_fraction(harmonic(r + 1))
    return (2 * h_big - h_small - 2 * log2) / (2 * r + 1)


def potential_square_moment(power: int, log2: arb, pi: arb) -> arb:
    """Integral of V(x)^2 x^power on [-1,1]."""
    if power % 2:
        return arb(0)
    r = power // 2
    h_big = _arb_fraction(harmonic(2 * r + 2))
    h_small = _arb_fraction(harmonic(r + 1))
    h2_big = _arb_fraction(harmonic(2 * r + 2, 2))
    h2_small = _arb_fraction(harmonic(r + 1, 2))
    a = 2 * log2 - 2 * h_big + h_small
    trigamma_difference = -(pi * pi) / 3 + 4 * h2_big - h2_small
    return (a * a + trigamma_difference) / (2 * (2 * r + 1))


def potential_matrices(polys: list[FractionPoly], prec: int) -> tuple[ArbMatrix, ArbMatrix]:
    n = len(polys)
    with ctx.workprec(prec):
        log2 = log2_enclosure(prec)
        pi = pi_enclosure(prec)
        v = _arb_zero_matrix(n)
        v2 = _arb_zero_matrix(n)
        for i in range(n):
            for j in range(i, n):
                product = poly_mul(polys[i], polys[j])
                vij = arb(0)
                v2ij = arb(0)
                for power, coefficient in enumerate(product):
                    if coefficient:
                        c = _arb_fraction(coefficient)
                        vij += c * potential_moment(power, log2)
                        v2ij += c * potential_square_moment(power, log2, pi)
                v[i][j] = vij
                v[j][i] = vij
                v2[i][j] = v2ij
                v2[j][i] = v2ij
        return v, v2


def first_prime_matrices(
    polys: list[FractionPoly],
    prec: int,
    support_num: int = 7,
    support_den: int = 20,
) -> tuple[ArbMatrix, ArbMatrix]:
    """Return P2 low matrix and P2^2 low matrix on the Legendre span."""
    n = len(polys)
    with ctx.workprec(prec):
        tau = tau_enclosure(prec, support_num, support_den)
        if not (tau > 1 and tau < 2):
            raise ValueError("first-prime matrices require 1 < log(2)/T < 2")
        c2 = c2_enclosure(prec)
        lower = arb(-1)
        upper = 1 - tau
        right_lower = tau - 1
        right_upper = arb(1)
        p2 = _arb_zero_matrix(n)
        p2sq = _arb_zero_matrix(n)
        shifted = [_arb_poly_shift(poly, tau) for poly in polys]
        base = [[_arb_fraction(c) for c in poly] for poly in polys]
        for i in range(n):
            for j in range(i, n):
                overlap = _arb_poly_integral_between(_arb_poly_mul(shifted[i], base[j]), lower, upper)
                overlap += _arb_poly_integral_between(_arb_poly_mul(base[i], shifted[j]), lower, upper)
                value = -c2 * overlap
                product = [_arb_fraction(c) for c in poly_mul(polys[i], polys[j])]
                edge = _arb_poly_integral_between(product, lower, upper)
                edge += _arb_poly_integral_between(product, right_lower, right_upper)
                square_value = c2 * c2 * edge
                p2[i][j] = value
                p2[j][i] = value
                p2sq[i][j] = square_value
                p2sq[j][i] = square_value
        return p2, p2sq


def abs_power_action_on_poly(power: int, poly: FractionPoly) -> FractionPoly:
    """Exact polynomial x -> integral_{-1}^1 |x-y|^power poly(y) dy."""
    if power < 0:
        raise ValueError("power must be nonnegative")
    out = [Fraction(0) for _ in range(len(poly) + power + 2)]
    for k, fk in enumerate(poly):
        if fk == 0:
            continue
        for r in range(power + 1):
            comb = Fraction(math.comb(power, r))
            den = Fraction(r + k + 1)
            # y <= x: (x-y)^power
            left_pref = comb * ((-1) ** r) / den
            out[power + k + 1] += fk * left_pref
            out[power - r] -= fk * left_pref * ((-1) ** (r + k + 1))
            # y >= x: (y-x)^power
            right_pref = comb * ((-1) ** (power - r)) / den
            out[power - r] += fk * right_pref
            out[power + k + 1] -= fk * right_pref
    return poly_trim(out)


def residual_truncation_operator(
    polys: list[FractionPoly],
    order: int,
    prec: int,
    support_num: int = 7,
    support_den: int = 20,
) -> tuple[list[FractionPoly], ArbMatrix, ArbMatrix, arb]:
    """Exact polynomial residual truncation plus a rigorous operator remainder.

    Returns images R_K P_j, the low matrix <P_i,R_K P_j>, the exact low matrix
    <R_K P_i,R_K P_j>, and delta with ||R-R_K|| <= delta.
    """
    if support_den <= 0 or support_num <= 0:
        raise ValueError("support T must be a positive rational")
    T = Fraction(support_num, support_den)
    coefficients = _suzuki_residual_series_coefficients(order)
    images: list[FractionPoly] = []
    for poly in polys:
        image: FractionPoly = [Fraction(0)]
        for degree, coefficient in enumerate(coefficients):
            c = Fraction(int(coefficient.p), int(coefficient.q))
            kernel_coeff = -c * (T ** (degree + 1))
            action = abs_power_action_on_poly(degree, poly)
            image = poly_add(image, poly_scale(action, kernel_coeff))
        images.append(image)

    n = len(polys)
    low = _arb_zero_matrix(n)
    full_square = _arb_zero_matrix(n)
    for i in range(n):
        for j in range(i, n):
            low_exact = exact_poly_inner(polys[i], images[j])
            square_exact = exact_poly_inner(images[i], images[j])
            low_val = _arb_fraction(low_exact)
            square_val = _arb_fraction(square_exact)
            low[i][j] = low_val
            low[j][i] = low_val
            full_square[i][j] = square_val
            full_square[j][i] = square_val
    with ctx.workprec(prec):
        two_t = arb(2 * support_num) / support_den
        u_max = acb(two_t)
        tail = _suzuki_residual_tail_radius(u_max, order)
        delta = two_t * tail
    return images, low, full_square, delta


def assemble_exact_prime_schur(
    n: int = 32,
    prec: int = 256,
    residual_order: int = 32,
    support_num: int = 7,
    support_den: int = 20,
    require_positive_mu: bool = True,
) -> dict[str, object]:
    if n < 1:
        raise ValueError("n must be positive")
    if prec < 64:
        raise ValueError("prec must be at least 64 bits")
    if residual_order < 8:
        raise ValueError("residual_order must be at least 8")
    require_one_prime_support(support_num, support_den, prec)

    with ctx.workprec(prec):
        support_t = arb(support_num) / support_den
        tau = tau_enclosure(prec, support_num, support_den)
        polys = legendre_polynomials(n - 1)
        norms = [legendre_norm_sq(k) for k in range(n)]
        V, V2 = potential_matrices(polys, prec)
        P2, P2sq = first_prime_matrices(polys, prec, support_num, support_den)
        _, Rk, Rk2, delta_R = residual_truncation_operator(
            polys,
            residual_order,
            prec,
            support_num,
            support_den,
        )
        cT = c_T_enclosure(prec, support_num, support_den)

        # A_N lower bound: R >= R_K - delta_R I.
        A = _arb_zero_matrix(n)
        for i in range(n):
            for j in range(n):
                value = V[i][j] + P2[i][j] + Rk[i][j]
                if i == j:
                    norm = _arb_fraction(norms[i])
                    value += _arb_fraction(harmonic(i)) * norm
                    value -= (cT + delta_R) * norm
                A[i][j] = value

        GV = _arb_mat_sub(V2, _arb_mat_mul_diag_inverse(V, norms))
        G2 = _arb_mat_sub(P2sq, _arb_mat_mul_diag_inverse(P2, norms))
        GRk = _arb_mat_sub(Rk2, _arb_mat_mul_diag_inverse(Rk, norms))
        # G_R <= 2 G_RK + 2 delta_R^2 I on the low span.
        GR = _arb_mat_scale(GRk, 2)
        for i in range(n):
            GR[i][i] += 2 * delta_R * delta_R * _arb_fraction(norms[i])

        # Crude rigorous high-mode lower bound mu_N.
        u_max = 2 * support_t
        coeffs = _suzuki_residual_series_coefficients(residual_order)
        residual_abs = arb(0)
        for degree, coefficient in enumerate(coeffs):
            c_abs = Fraction(abs(int(coefficient.p)), int(coefficient.q))
            residual_abs += _arb_fraction(c_abs) * u_max**degree
        residual_abs += _suzuki_residual_tail_radius(acb(u_max), residual_order)
        rho_R = 2 * support_t * residual_abs
        mu = _arb_fraction(harmonic(n)) - cT - c2_enclosure(prec) - rho_R
        mu_positive = bool(mu.lower() > 0)
        if require_positive_mu and not mu_positive:
            raise RuntimeError("failed to certify positive complement mu_N")

        schur: ArbMatrix | None = None
        if mu_positive:
            grams = _arb_mat_add(_arb_mat_add(GV, G2), GR)
            schur = _arb_mat_sub(A, _arb_mat_scale(grams, arb(3) / mu))
        return {
            "dimension": n,
            "support_num": support_num,
            "support_den": support_den,
            "support_T": support_t,

            "precision_bits": prec,
            "residual_order": residual_order,
            "norms": norms,
            "delta_R": delta_R,
            "rho_R": rho_R,
            "mu": mu,
            "mu_positive": mu_positive,
            "A": A,
            "GV": GV,
            "G2": G2,
            "GR": GR,
            "schur": schur,
        }
