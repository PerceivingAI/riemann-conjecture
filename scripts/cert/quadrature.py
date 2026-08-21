"""Rigorous integration and quadrature enclosures backed by Arb.

This module provides verified integral evaluations using python-flint's
acb.integral(...) backed by Arb's contour/interval integration algorithms.
"""

from __future__ import annotations

from typing import Callable

from flint import acb, arb, ctx


def legendre_p_acb(n: int, x: acb) -> acb:
    """Evaluate Legendre polynomial P_n(x) using the 3-term recurrence."""
    if n < 0:
        raise ValueError(f"Degree n must be non-negative, got {n}")
    if n == 0:
        return acb(1)
    if n == 1:
        return x
    p0 = acb(1)
    p1 = x
    for k in range(1, n):
        p2 = ((2 * k + 1) * x * p1 - k * p0) / (k + 1)
        p0, p1 = p1, p2
    return p1


def chebyshev_t_acb(n: int, x: acb) -> acb:
    """Evaluate Chebyshev polynomial T_n(x) using the 3-term recurrence."""
    if n < 0:
        raise ValueError(f"Degree n must be non-negative, got {n}")
    if n == 0:
        return acb(1)
    if n == 1:
        return x
    t0 = acb(1)
    t1 = x
    for _ in range(1, n):
        t2 = 2 * x * t1 - t0
        t0, t1 = t1, t2
    return t1


def monomial_acb(n: int, x: acb) -> acb:
    """Evaluate monomial x^n."""
    if n < 0:
        raise ValueError(f"Degree n must be non-negative, got {n}")
    return x**n


def evaluate_basis_acb(basis_type: str, n: int, x: acb) -> acb:
    """Evaluate a named basis function of index n at x."""
    b_type = basis_type.lower()
    if b_type in ("legendre", "p"):
        return legendre_p_acb(n, x)
    if b_type in ("chebyshev", "t"):
        return chebyshev_t_acb(n, x)
    if b_type in ("monomial", "power", "poly"):
        return monomial_acb(n, x)
    raise ValueError(f"Unknown basis type '{basis_type}'. Expected 'legendre', 'chebyshev', or 'monomial'.")


def rigorous_integral_1d(
    func: Callable[[acb, bool], acb],
    a: acb | arb | float | int,
    b: acb | arb | float | int,
    prec: int = 128,
    rel_tol: arb | float | None = None,
    abs_tol: arb | float | None = None,
    eval_limit: int | None = None,
) -> acb:
    """Compute a rigorous 1D integral enclosure int_a^b func(x, analytic) dx.

    Backed by Arb's acb.integral machinery.
    """
    with ctx.workprec(prec):
        a_acb = acb(a)
        b_acb = acb(b)
        kwargs = {}
        if rel_tol is not None:
            kwargs["rel_tol"] = rel_tol
        if abs_tol is not None:
            kwargs["abs_tol"] = abs_tol
        if eval_limit is not None:
            kwargs["eval_limit"] = eval_limit
        return acb.integral(func, a_acb, b_acb, **kwargs)


def rigorous_real_integral_1d(
    func: Callable[[acb, bool], acb],
    a: acb | arb | float | int,
    b: acb | arb | float | int,
    prec: int = 128,
    rel_tol: arb | float | None = None,
    abs_tol: arb | float | None = None,
) -> arb:
    """Compute a rigorous real 1D integral enclosure int_a^b func(x, analytic) dx.

    Checks that the imaginary enclosure contains zero and returns the real enclosure.
    """
    with ctx.workprec(prec):
        res = rigorous_integral_1d(func, a, b, prec=prec, rel_tol=rel_tol, abs_tol=abs_tol)
        if not (arb(0) in res.imag or abs(res.imag) < arb(2) ** (-prec + 10)):
            raise ValueError(f"Integration produced non-real enclosure with imaginary part: {res.imag}")
        return res.real


def rigorous_double_integral_2d(
    func2d: Callable[[acb, acb, bool], acb],
    x_a: acb | arb | float | int,
    x_b: acb | arb | float | int,
    y_a: acb | arb | float | int,
    y_b: acb | arb | float | int,
    prec: int = 128,
) -> acb:
    """Compute a rigorous 2D integral enclosure int_{x_a}^{x_b} ( int_{y_a}^{y_b} func2d(x, y, a) dy ) dx."""
    with ctx.workprec(prec):
        x_a_acb = acb(x_a)
        x_b_acb = acb(x_b)
        y_a_acb = acb(y_a)
        y_b_acb = acb(y_b)

        def outer_integrand(x: acb, analytic: bool) -> acb:
            def inner_integrand(y: acb, analytic_inner: bool) -> acb:
                return func2d(x, y, analytic and analytic_inner)

            return acb.integral(inner_integrand, y_a_acb, y_b_acb)

        return acb.integral(outer_integrand, x_a_acb, x_b_acb)


def rigorous_kernel_matrix_element(
    kernel: Callable[[acb, acb, bool], acb],
    phi_i: Callable[[acb], acb],
    phi_j: Callable[[acb], acb],
    a: acb | arb | float | int,
    b: acb | arb | float | int,
    prec: int = 128,
) -> arb:
    """Compute verified matrix element M_{i,j} = int_a^b int_a^b kernel(x, y) phi_i(x) phi_j(y) dx dy."""
    with ctx.workprec(prec):
        def integrand(x: acb, y: acb, analytic: bool) -> acb:
            return kernel(x, y, analytic) * phi_i(x) * phi_j(y)

        res_2d = rigorous_double_integral_2d(integrand, a, b, a, b, prec=prec)
        return res_2d.real
