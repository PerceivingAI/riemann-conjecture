"""Exact algebraic property and identity tests for research formulations.

Tests verify:
1. Contiguous relations for generalized Laguerre polynomials:
   L_n^(alpha)(x) = L_n^(alpha+1)(x) - L_{n-1}^(alpha+1)(x)
2. Exact continuous Laplace/main-density integral:
   A * integral_0^inf e^{-pt} L_{n-1}^(1)(t) dt = 1 - q^n
   where p = (s0-1)/A, A = 2s0-1, q = -s0/(s0-1)
3. Shift-operator annihilation:
   T = (E - 1)(E - q) annihilates (1 - q^n) for all n >= 1 and s0 > 1.
"""

from __future__ import annotations

from fractions import Fraction
import random
import pytest

from scripts.verify_identities import laguerre_coeffs, poly_sub, laplace_integral_of_poly


class TestLaguerreIdentities:
    """Exact algebraic tests for Laguerre polynomial contiguous relations."""

    @pytest.mark.parametrize("n", range(1, 25))
    @pytest.mark.parametrize("alpha", [0, 1, 2, 3])
    def test_contiguous_identity_exact(self, n: int, alpha: int) -> None:
        """L_n^(alpha) == L_n^(alpha+1) - L_{n-1}^(alpha+1)."""
        left = laguerre_coeffs(n, alpha)
        r1 = laguerre_coeffs(n, alpha + 1)
        r2 = laguerre_coeffs(n - 1, alpha + 1)
        diff = poly_sub(left, poly_sub(r1, r2))
        assert diff == [0] or diff == []

    def test_randomized_contiguous_properties(self) -> None:
        """Fuzz contiguous identity across 100 randomized (n, alpha) pairs."""
        rng = random.Random(42)
        for _ in range(100):
            n = rng.randint(1, 30)
            alpha = rng.randint(0, 10)
            left = laguerre_coeffs(n, alpha)
            r1 = laguerre_coeffs(n, alpha + 1)
            r2 = laguerre_coeffs(n - 1, alpha + 1)
            diff = poly_sub(left, poly_sub(r1, r2))
            assert diff == [0] or diff == [], f"Failed for n={n}, alpha={alpha}"


class TestPoleIntegralIdentities:
    """Exact rational verification of the zeta-pole density integral."""

    @pytest.mark.parametrize("s0", [
        Fraction(3, 2),
        Fraction(2, 1),
        Fraction(5, 2),
        Fraction(3, 1),
        Fraction(7, 2),
        Fraction(4, 1),
        Fraction(5, 1),
        Fraction(10, 1),
    ])
    @pytest.mark.parametrize("n", [1, 2, 3, 5, 8, 12, 16, 20])
    def test_pole_integral_exact(self, s0: Fraction, n: int) -> None:
        """A * integral_0^inf e^{-pt} L_{n-1}^(1)(t) dt == 1 - q^n."""
        A = 2 * s0 - 1
        p = (s0 - 1) / A
        q = -s0 / (s0 - 1)

        coeffs = laguerre_coeffs(n - 1, 1)
        laplace_val = laplace_integral_of_poly(coeffs, p)
        expected = Fraction(1) - (q ** n)

        assert laplace_val == expected
    def test_randomized_rational_centers(self) -> None:
        """Fuzz rational centers s0 in (1, 50) and degrees n in [1, 20]."""
        rng = random.Random(1337)
        for _ in range(50):
            # Generate random rational s0 > 1
            num = rng.randint(2, 200)
            den = rng.randint(1, num - 1)
            s0 = Fraction(num, den)
            assert s0 > 1

            A = 2 * s0 - 1
            p = (s0 - 1) / A
            q = -s0 / (s0 - 1)

            n = rng.randint(1, 15)
            coeffs = laguerre_coeffs(n - 1, 1)
            laplace_val = laplace_integral_of_poly(coeffs, p)
            expected = Fraction(1) - (q ** n)

            assert laplace_val == expected, f"Failed for s0={s0}, n={n}"


class TestShiftFilterAnnihilation:
    """Exact verification that T = (E - 1)(E - q) annihilates 1 - q^n."""

    @pytest.mark.parametrize("s0", [
        Fraction(4, 3),
        Fraction(2, 1),
        Fraction(3, 1),
        Fraction(5, 1),
        Fraction(17, 9),
    ])
    def test_shift_filter_exact(self, s0: Fraction) -> None:
        """T(1 - q^n) = (1 - q^(n+2)) - (1+q)(1 - q^(n+1)) + q(1 - q^n) == 0."""
        q = -s0 / (s0 - 1)
        for n in range(1, 25):
            m0 = Fraction(1) - (q ** n)
            m1 = Fraction(1) - (q ** (n + 1))
            m2 = Fraction(1) - (q ** (n + 2))
            annihilated = m2 - (Fraction(1) + q) * m1 + q * m0
            assert annihilated == 0

    def test_randomized_shift_filter(self) -> None:
        """Fuzz shift filter across arbitrary rational centers and degrees."""
        rng = random.Random(2026)
        for _ in range(100):
            num = rng.randint(3, 500)
            den = rng.randint(1, num - 1)
            s0 = Fraction(num, den)
            q = -s0 / (s0 - 1)
            n = rng.randint(1, 30)

            m0 = Fraction(1) - (q ** n)
            m1 = Fraction(1) - (q ** (n + 1))
            m2 = Fraction(1) - (q ** (n + 2))
            annihilated = m2 - (Fraction(1) + q) * m1 + q * m0
            assert annihilated == 0, f"Failed for s0={s0}, n={n}"
