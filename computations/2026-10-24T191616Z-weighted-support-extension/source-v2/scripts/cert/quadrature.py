"""Rigorous Arb integration with an exact-input proof interface."""

from __future__ import annotations

from typing import Callable

from flint import acb, arb, ctx, fmpq


ExactIntegrationInput = acb | arb | fmpq | int
ExactTolerance = arb | fmpq | int


def _validate_precision(prec: int) -> None:
    if isinstance(prec, bool) or not isinstance(prec, int) or prec < 32:
        raise TypeError("prec must be an integer of at least 32 bits")


def _to_exact_acb(value: ExactIntegrationInput, name: str) -> acb:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError(f"{name} must not be an ordinary float")
    if not isinstance(value, (int, fmpq, arb, acb)):
        raise TypeError(f"{name} must be int, fmpq, arb, or acb")
    return acb(value)


def _to_exact_tolerance(value: ExactTolerance, name: str) -> arb:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError(f"{name} must not be an ordinary float")
    if not isinstance(value, (int, fmpq, arb)):
        raise TypeError(f"{name} must be int, fmpq, or arb")
    return arb(value)


def require_real_enclosure(value: acb, context: str) -> arb:
    """Project a mathematically known-real quantity after an interval consistency check.

    Zero containment of the imaginary ball is not, by itself, a proof that an
    arbitrary complex quantity is real. Callers must know analytically that the
    target integral/kernel value is real; this check ensures the Acb enclosure
    is consistent with that exact realness before its real component is used.
    """
    if arb(0) not in value.imag:
        raise ValueError(
            f"{context} produced an enclosure whose imaginary part excludes zero: {value.imag}"
        )
    return value.real


def legendre_p_acb(n: int, x: acb) -> acb:
    """Evaluate Legendre polynomial P_n(x) using the three-term recurrence."""
    if n < 0:
        raise ValueError(f"Degree n must be non-negative, got {n}")
    if n == 0:
        return acb(1)
    if n == 1:
        return x
    p0 = acb(1)
    p1 = x
    for k in range(1, n):
        p0, p1 = p1, ((2 * k + 1) * x * p1 - k * p0) / (k + 1)
    return p1


def chebyshev_t_acb(n: int, x: acb) -> acb:
    """Evaluate Chebyshev polynomial T_n(x) using the three-term recurrence."""
    if n < 0:
        raise ValueError(f"Degree n must be non-negative, got {n}")
    if n == 0:
        return acb(1)
    if n == 1:
        return x
    t0 = acb(1)
    t1 = x
    for _ in range(1, n):
        t0, t1 = t1, 2 * x * t1 - t0
    return t1


def monomial_acb(n: int, x: acb) -> acb:
    """Evaluate monomial x^n."""
    if n < 0:
        raise ValueError(f"Degree n must be non-negative, got {n}")
    return x**n


def evaluate_basis_acb(basis_type: str, n: int, x: acb) -> acb:
    """Evaluate one of the basis types admitted by the certificate schema."""
    if basis_type == "legendre":
        return legendre_p_acb(n, x)
    if basis_type == "chebyshev":
        return chebyshev_t_acb(n, x)
    if basis_type == "monomial":
        return monomial_acb(n, x)
    raise ValueError(
        f"Unknown basis type '{basis_type}'. Expected 'legendre', 'chebyshev', or 'monomial'."
    )


def rigorous_integral_1d(
    func: Callable[[acb, bool], acb],
    a: ExactIntegrationInput,
    b: ExactIntegrationInput,
    prec: int = 128,
    rel_tol: ExactTolerance | None = None,
    abs_tol: ExactTolerance | None = None,
    eval_limit: int | None = None,
) -> acb:
    """Compute a rigorous one-dimensional Acb integral enclosure."""
    _validate_precision(prec)
    a_acb = _to_exact_acb(a, "a")
    b_acb = _to_exact_acb(b, "b")
    if eval_limit is not None and (
        isinstance(eval_limit, bool) or not isinstance(eval_limit, int) or eval_limit < 1
    ):
        raise TypeError("eval_limit must be a positive integer")

    with ctx.workprec(prec):
        kwargs: dict[str, arb | int] = {}
        if rel_tol is not None:
            kwargs["rel_tol"] = _to_exact_tolerance(rel_tol, "rel_tol")
        if abs_tol is not None:
            kwargs["abs_tol"] = _to_exact_tolerance(abs_tol, "abs_tol")
        if eval_limit is not None:
            kwargs["eval_limit"] = eval_limit
        return acb.integral(func, a_acb, b_acb, **kwargs)


def rigorous_real_integral_1d(
    func: Callable[[acb, bool], acb],
    a: ExactIntegrationInput,
    b: ExactIntegrationInput,
    prec: int = 128,
    rel_tol: ExactTolerance | None = None,
    abs_tol: ExactTolerance | None = None,
) -> arb:
    """Compute a rigorous enclosure for an analytically known-real integral."""
    result = rigorous_integral_1d(
        func,
        a,
        b,
        prec=prec,
        rel_tol=rel_tol,
        abs_tol=abs_tol,
    )
    return require_real_enclosure(result, "one-dimensional integral")


def rigorous_double_integral_2d(
    func2d: Callable[[acb, acb, bool], acb],
    x_a: ExactIntegrationInput,
    x_b: ExactIntegrationInput,
    y_a: ExactIntegrationInput,
    y_b: ExactIntegrationInput,
    prec: int = 128,
) -> acb:
    """Compute a rigorous iterated two-dimensional Acb integral enclosure."""
    _validate_precision(prec)
    x_a_acb = _to_exact_acb(x_a, "x_a")
    x_b_acb = _to_exact_acb(x_b, "x_b")
    y_a_acb = _to_exact_acb(y_a, "y_a")
    y_b_acb = _to_exact_acb(y_b, "y_b")

    with ctx.workprec(prec):
        def outer_integrand(x: acb, analytic: bool) -> acb:
            def inner_integrand(y: acb, analytic_inner: bool) -> acb:
                return func2d(x, y, analytic and analytic_inner)

            return acb.integral(inner_integrand, y_a_acb, y_b_acb)

        return acb.integral(outer_integrand, x_a_acb, x_b_acb)


def rigorous_kernel_matrix_element(
    kernel: Callable[[acb, acb, bool], acb],
    phi_i: Callable[[acb], acb],
    phi_j: Callable[[acb], acb],
    a: ExactIntegrationInput,
    b: ExactIntegrationInput,
    prec: int = 128,
) -> arb:
    """Compute a real rigorous kernel matrix element."""
    def integrand(x: acb, y: acb, analytic: bool) -> acb:
        return kernel(x, y, analytic) * phi_i(x) * phi_j(y)

    result = rigorous_double_integral_2d(integrand, a, b, a, b, prec=prec)
    return require_real_enclosure(result, "kernel matrix element")
