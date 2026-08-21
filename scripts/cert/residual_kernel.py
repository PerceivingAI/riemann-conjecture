"""Suzuki residual kernel and digamma positive-kernel matrix elements.

This module computes verified Arb interval matrices for:
1. Digamma positive-kernel brackets: (1/a_k) ||f||^2 - <f, e^(-2 a_k |t-s|) f>
2. Archimedean residual kernel matrices: -T <w, r''(T(x-y)) w>
3. L2 inner product matrices and compressed shift operators.
"""

from __future__ import annotations

from typing import Callable

from flint import acb, arb, arb_mat, ctx, fmpq

from scripts.cert.constants import digamma_ak, m0_digamma_enclosure
from scripts.cert.quadrature import evaluate_basis_acb, rigorous_real_integral_1d


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

                val_acb = acb.integral(outer_integrand, -t_acb, t_acb)
                mat[i, j] = val_acb.real
                mat[j, i] = val_acb.real

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


def suzuki_residual_kernel_matrix(
    r_second_deriv: Callable[[acb, bool], acb],
    basis_type: str,
    dim: int,
    T_val: arb,
    prec: int = 128,
) -> arb_mat:
    """Compute Suzuki residual kernel matrix:

    R_{i,j} = -T int_{-1}^1 int_{-1}^1 r''(T(x - y)) phi_i(x) phi_j(y) dx dy.
    """
    with ctx.workprec(prec):
        mat = arb_mat(dim, dim)
        t_acb = acb(T_val)

        for i in range(dim):
            for j in range(i, dim):
                def outer(x: acb, analytic: bool) -> acb:
                    phi_i_x = evaluate_basis_acb(basis_type, i, x)

                    def inner(y: acb, a_in: bool) -> acb:
                        phi_j_y = evaluate_basis_acb(basis_type, j, y)
                        u = t_acb * (x - y)
                        return r_second_deriv(u, analytic and a_in) * phi_j_y

                    return phi_i_x * acb.integral(inner, -1, 1)

                val_acb = -t_acb * acb.integral(outer, -1, 1)
                mat[i, j] = val_acb.real
                mat[j, i] = val_acb.real

        return mat
