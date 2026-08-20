"""Hypothesis property tests for exact research identities and diagnostic helpers."""

from __future__ import annotations

from fractions import Fraction

from hypothesis import given, settings, strategies as st

from scripts.rh_tools import (
    gamma_from_small_u_stationary_u,
    small_u_stationary_u_from_gamma,
)
from scripts.verify_identities import (
    laguerre_coeffs,
    laplace_integral_of_poly,
    poly_sub,
)


@settings(max_examples=150, deadline=None)
@given(
    n=st.integers(min_value=1, max_value=30),
    alpha=st.integers(min_value=0, max_value=10),
)
def test_laguerre_contiguous_identity_property(n: int, alpha: int) -> None:
    """L_n^(alpha)=L_n^(alpha+1)-L_(n-1)^(alpha+1) exactly."""
    left = laguerre_coeffs(n, alpha)
    rhs = poly_sub(laguerre_coeffs(n, alpha + 1), laguerre_coeffs(n - 1, alpha + 1))
    assert poly_sub(left, rhs) in ([0], [])


@settings(max_examples=120, deadline=None)
@given(
    numerator=st.integers(min_value=2, max_value=80),
    denominator=st.integers(min_value=1, max_value=79),
    n=st.integers(min_value=1, max_value=14),
)
def test_pole_density_integral_property(numerator: int, denominator: int, n: int) -> None:
    """Verify the exact pole-density identity over many rational centers."""
    if denominator >= numerator:
        return
    s0 = Fraction(numerator, denominator)
    a = 2 * s0 - 1
    p = (s0 - 1) / a
    q = -s0 / (s0 - 1)
    coeffs = laguerre_coeffs(n - 1, 1)
    assert laplace_integral_of_poly(coeffs, p) == Fraction(1) - q**n


@settings(max_examples=150, deadline=None)
@given(
    numerator=st.integers(min_value=2, max_value=120),
    denominator=st.integers(min_value=1, max_value=119),
    n=st.integers(min_value=1, max_value=24),
)
def test_shift_filter_annihilation_property(numerator: int, denominator: int, n: int) -> None:
    """The exact degree-two shift filter annihilates 1-q^n."""
    if denominator >= numerator:
        return
    s0 = Fraction(numerator, denominator)
    q = -s0 / (s0 - 1)
    m0 = Fraction(1) - q**n
    m1 = Fraction(1) - q ** (n + 1)
    m2 = Fraction(1) - q ** (n + 2)
    assert m2 - (Fraction(1) + q) * m1 + q * m0 == 0


@settings(max_examples=100, deadline=None)
@given(
    gamma=st.floats(min_value=1.0, max_value=1.0e5, allow_nan=False, allow_infinity=False),
    s0=st.floats(min_value=1.01, max_value=100.0, allow_nan=False, allow_infinity=False),
)
def test_small_u_diagnostic_inverse_property(gamma: float, s0: float) -> None:
    """Only the algebraic inverse of the explicitly small-u diagnostic is asserted."""
    u = small_u_stationary_u_from_gamma(gamma, s0)
    recovered = gamma_from_small_u_stationary_u(u, s0)
    assert abs(recovered - gamma) <= 1e-12 * max(1.0, gamma)
