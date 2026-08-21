"""Suzuki residual kernel and digamma positive-kernel matrix elements.

This module computes verified Arb interval matrices for:
1. Digamma positive-kernel brackets: (1/a_k) ||f||^2 - <f, e^(-2 a_k |t-s|) f>
2. Archimedean residual kernel matrices: -T <w, r''(T(x-y)) w>
3. L2 inner product matrices and compressed shift operators.
"""

from __future__ import annotations

import math
from functools import lru_cache

from flint import acb, arb, arb_mat, ctx, fmpq

from scripts.cert.constants import digamma_ak, m0_digamma_enclosure
from scripts.cert.quadrature import (
    evaluate_basis_acb,
    require_real_enclosure,
    rigorous_real_integral_1d,
)


def digamma_inner_products_matrix(
    basis_type: str,
    dim: int,
    T_val: arb,
    prec: int = 128,
) -> arb_mat:
    """Compute the Gram matrix M_{i,j} = int_{-T}^T phi_i(t) phi_j(t) dt."""
    if dim < 1:
        raise ValueError(f"Dimension must be positive, got {dim}")

    with ctx.workprec(prec):
        mat = arb_mat(dim, dim)
        for i in range(dim):
            for j in range(i, dim):
                # Parity sector: if basis functions have opposite parity, integral is identically 0
                if (i % 2) != (j % 2):
                    mat[i, j] = arb(0)
                    mat[j, i] = arb(0)
                    continue

                def integrand(t: acb, _: bool) -> acb:
                    # Map t in [-T, T] to x in [-1, 1] for standard polynomial bases
                    x = t / acb(T_val)
                    return evaluate_basis_acb(basis_type, i, x) * evaluate_basis_acb(basis_type, j, x)

                val = rigorous_real_integral_1d(integrand, -T_val, T_val, prec=prec)
                mat[i, j] = val
                mat[j, i] = val

        return mat


def exponential_convolution_matrix(
    a_val: arb,
    basis_type: str,
    dim: int,
    T_val: arb,
    prec: int = 128,
) -> arb_mat:
    """Compute verified matrix E_{i,j} = int_{-T}^T int_{-T}^T e^(-2 a |t-s|) phi_i(t) phi_j(s) ds dt.

    Uses split analytic integration across the corner at s = t.
    """
    if dim < 1:
        raise ValueError(f"Dimension must be positive, got {dim}")

    with ctx.workprec(prec):
        mat = arb_mat(dim, dim)
        a_acb = acb(a_val)
        t_acb = acb(T_val)

        for i in range(dim):
            for j in range(i, dim):
                if (i % 2) != (j % 2):
                    mat[i, j] = arb(0)
                    mat[j, i] = arb(0)
                    continue

                def outer_integrand(t: acb, analytic: bool) -> acb:
                    x_t = t / t_acb
                    phi_i_t = evaluate_basis_acb(basis_type, i, x_t)

                    def left_inner(s: acb, a_in: bool) -> acb:
                        x_s = s / t_acb
                        phi_j_s = evaluate_basis_acb(basis_type, j, x_s)
                        return (-2 * a_acb * (t - s)).exp() * phi_j_s

                    def right_inner(s: acb, a_in: bool) -> acb:
                        x_s = s / t_acb
                        phi_j_s = evaluate_basis_acb(basis_type, j, x_s)
                        return (-2 * a_acb * (s - t)).exp() * phi_j_s

                    i_left = acb.integral(left_inner, -t_acb, t)
                    i_right = acb.integral(right_inner, t, t_acb)
                    return phi_i_t * (i_left + i_right)

                value = rigorous_real_integral_1d(
                    outer_integrand,
                    -t_acb,
                    t_acb,
                    prec=prec,
                )
                mat[i, j] = value
                mat[j, i] = value

        return mat


def digamma_bracket_matrix(
    k: int,
    basis_type: str,
    dim: int,
    T_val: arb,
    gram_mat: arb_mat | None = None,
    prec: int = 128,
) -> arb_mat:
    """Compute the k-th digamma positive bracket matrix:

    B^{(k)} = (1/a_k) M^{(0)} - E^{(k)}, where a_k = k + 1/4.
    """
    with ctx.workprec(prec):
        ak_q = digamma_ak(k)
        ak_arb = arb(int(ak_q.p)) / arb(int(ak_q.q))
        inv_ak = arb(1) / ak_arb

        if gram_mat is None:
            gram = digamma_inner_products_matrix(basis_type, dim, T_val, prec=prec)
        else:
            gram = gram_mat

        e_mat = exponential_convolution_matrix(ak_arb, basis_type, dim, T_val, prec=prec)

        res = arb_mat(dim, dim)
        for i in range(dim):
            for j in range(dim):
                res[i, j] = inv_ak * gram[i, j] - e_mat[i, j]

        return res


def digamma_positive_operator_matrix(
    k_max: int,
    basis_type: str,
    dim: int,
    T_val: arb,
    prec: int = 128,
) -> arb_mat:
    """Compute verified partial sum matrix of the digamma positive operator:

    D_{K_max} = m_0 M^{(0)} + sum_{k=0}^{K_max} B^{(k)}.
    """
    with ctx.workprec(prec):
        m0 = m0_digamma_enclosure(prec)
        gram = digamma_inner_products_matrix(basis_type, dim, T_val, prec=prec)

        total = arb_mat(dim, dim)
        for i in range(dim):
            for j in range(dim):
                total[i, j] = m0 * gram[i, j]

        for k in range(k_max + 1):
            b_k = digamma_bracket_matrix(k, basis_type, dim, T_val, gram_mat=gram, prec=prec)
            for i in range(dim):
                for j in range(dim):
                    total[i, j] += b_k[i, j]

        return total


@lru_cache(maxsize=None)
def _bernoulli_at_three_quarters(n: int) -> fmpq:
    x = fmpq(3, 4)
    return sum(
        (
            fmpq(math.comb(n, k))
            * fmpq.bernoulli(k)
            * (x ** (n - k))
            for k in range(n + 1)
        ),
        fmpq(0),
    )


@lru_cache(maxsize=None)
def _suzuki_residual_series_coefficients(order: int) -> tuple[fmpq, ...]:
    """Return exact Taylor coefficients for the positive-side analytic branch.

    Suzuki's decomposition gives
    `r0''(u) = -2 cosh(u/2)` and
    `r1''(u) = sum B_(m+1)(3/4) (2u)^m / (m+1)!`.
    """
    coefficients: list[fmpq] = []
    for degree in range(order + 1):
        r_zero = (
            fmpq(-2, (2**degree) * math.factorial(degree))
            if degree % 2 == 0
            else fmpq(0)
        )
        r_one = (
            _bernoulli_at_three_quarters(degree + 1)
            * (2**degree)
            / math.factorial(degree + 1)
        )
        coefficients.append(r_zero + r_one)
    return tuple(coefficients)


def _suzuki_residual_tail_radius(u: acb, order: int) -> arb:
    """Bound every omitted Taylor coefficient on `|u| < pi`.

    For `m >= 1`, the Fourier bound for Bernoulli polynomials gives
    `|B_(m+1)(3/4)| <= 2 (m+1)! / (2*pi)^(m+1)`.
    This reduces the `r1''` remainder to the geometric bound below.
    The `r0''` remainder uses the exponential-series term ratio.
    """
    magnitude = abs(u).upper()
    pi = arb.pi()
    if not magnitude < pi:
        raise ValueError("Suzuki residual series requires |T(x-y)| < pi")

    ratio = magnitude / pi
    r_one_tail = (arb(2) / pi) * (ratio ** (order + 1)) / (1 - ratio)

    half_magnitude = magnitude / 2
    first_exp_term = (
        arb(2)
        * (half_magnitude ** (order + 1))
        / math.factorial(order + 1)
    )
    r_zero_tail = first_exp_term / (
        1 - half_magnitude / (order + 2)
    )
    return r_zero_tail + r_one_tail


def _suzuki_residual_r_second_positive_acb(
    u: acb,
    *,
    order: int = 32,
) -> acb:
    coefficients = _suzuki_residual_series_coefficients(order)
    value = acb(0)
    for coefficient in reversed(coefficients):
        value = value * u + acb(coefficient)

    try:
        error = _suzuki_residual_tail_radius(u, order)
    except ValueError:
        return acb("nan")
    error_ball = arb(0, error)
    return value + acb(error_ball, error_ball)


def suzuki_residual_r_second(
    t: arb | fmpq | int,
    prec: int = 128,
) -> arb:
    """Evaluate Suzuki's canonical even residual second derivative."""
    if isinstance(t, bool) or isinstance(t, float):
        raise TypeError("t must be int, fmpq, or arb, not an ordinary float")
    if not isinstance(t, (int, fmpq, arb)):
        raise TypeError("t must be int, fmpq, or arb")
    if isinstance(prec, bool) or not isinstance(prec, int) or prec < 32:
        raise TypeError("prec must be an integer of at least 32 bits")

    with ctx.workprec(prec):
        positive_t = abs(arb(t))
        result = _suzuki_residual_r_second_positive_acb(acb(positive_t))
        return require_real_enclosure(result, "Suzuki residual second derivative")


def suzuki_residual_kernel_matrix(
    basis_type: str,
    dim: int,
    T_val: arb,
    prec: int = 128,
) -> arb_mat:
    """Compute the canonical Suzuki residual matrix from equation (4.5)."""
    if dim < 1:
        raise ValueError(f"Dimension must be positive, got {dim}")
    if not T_val > 0:
        raise ValueError("T_val must be strictly positive")
    if not 2 * abs(T_val).upper() < arb.pi():
        raise ValueError("T_val must satisfy 2*T < pi for residual series evaluation")

    with ctx.workprec(prec):
        matrix = arb_mat(dim, dim)
        t_acb = acb(T_val)

        for i in range(dim):
            for j in range(i, dim):
                if (i % 2) != (j % 2):
                    matrix[i, j] = arb(0)
                    matrix[j, i] = arb(0)
                    continue

                def outer(x: acb, _: bool) -> acb:
                    phi_i_x = evaluate_basis_acb(basis_type, i, x)

                    def left(y: acb, _: bool) -> acb:
                        distance = t_acb * (x - y)
                        kernel = _suzuki_residual_r_second_positive_acb(distance)
                        return (
                            kernel
                            * evaluate_basis_acb(basis_type, j, y)
                        )

                    def right(y: acb, _: bool) -> acb:
                        distance = t_acb * (y - x)
                        kernel = _suzuki_residual_r_second_positive_acb(distance)
                        return (
                            kernel
                            * evaluate_basis_acb(basis_type, j, y)
                        )

                    left_integral = acb.integral(left, -1, x)
                    right_integral = acb.integral(right, x, 1)
                    return phi_i_x * (left_integral + right_integral)

                value = rigorous_real_integral_1d(
                    outer,
                    -1,
                    1,
                    prec=prec,
                )
                value *= -T_val
                matrix[i, j] = value
                matrix[j, i] = value

        return matrix
