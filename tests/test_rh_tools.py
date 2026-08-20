"""Unit and property tests for scripts/rh_tools.py numerical toolkit."""

from __future__ import annotations

from decimal import Decimal, getcontext
import math
import random
import pytest

from scripts.rh_tools import (
    laguerre_decimal_sequence,
    laguerre_float,
    primes_up_to,
    von_mangoldt_prime_powers,
    pole_parameters,
    pole_term,
    nth_root_abs,
    composite_simpson,
    density_kernel,
    t_from_m,
    turning_u,
    get_zeta_zeros,
    small_u_stationary_t_from_gamma,
    small_u_stationary_u_from_gamma,
    gamma_from_small_u_stationary_u,
)
class TestPrimesAndVonMangoldt:
    """Tests for sieve and prime power generator invariants."""

    def test_primes_up_to(self) -> None:
        """Verify primes up to 100 against known prime sequence."""
        known_primes = [
            2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41,
            43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
        ]
        assert primes_up_to(100) == known_primes
        assert primes_up_to(1) == []
        assert primes_up_to(2) == [2]

    def test_von_mangoldt_prime_powers(self) -> None:
        """Verify Lambda(m) values: log(p) for prime powers, 0 for composites."""
        limit = 35
        powers = von_mangoldt_prime_powers(limit, precision=30)
        items = dict(powers)

        # Primes
        for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
            assert p in items
            assert abs(float(items[p]) - math.log(p)) < 1e-12

        # Prime powers: 4=2^2, 8=2^3, 9=3^2, 16=2^4, 25=5^2, 27=3^3, 32=2^5
        assert 4 in items and abs(float(items[4]) - math.log(2)) < 1e-12
        assert 8 in items and abs(float(items[8]) - math.log(2)) < 1e-12
        assert 9 in items and abs(float(items[9]) - math.log(3)) < 1e-12
        assert 16 in items and abs(float(items[16]) - math.log(2)) < 1e-12
        assert 25 in items and abs(float(items[25]) - math.log(5)) < 1e-12
        assert 27 in items and abs(float(items[27]) - math.log(3)) < 1e-12
        assert 32 in items and abs(float(items[32]) - math.log(2)) < 1e-12

        # Non-prime-power composites must NOT be in the result
        for c in [6, 10, 12, 14, 15, 18, 20, 21, 22, 24, 26, 28, 30, 33, 34, 35]:
            assert c not in items


class TestLaguerreEvaluation:
    """Verify consistency between Decimal and Float Laguerre implementations."""

    @pytest.mark.parametrize("degree", [0, 1, 2, 5, 10, 15])
    @pytest.mark.parametrize("alpha", [0, 1, 2])
    @pytest.mark.parametrize("x_val", [0.1, 0.5, 1.0, 2.5, 5.0])
    def test_float_decimal_consistency(self, degree: int, alpha: int, x_val: float) -> None:
        """Float and Decimal evaluations must match within float precision."""
        getcontext().prec = 50
        seq = laguerre_decimal_sequence(degree, alpha, Decimal(str(x_val)))
        dec_val = float(seq[degree])
        flt_val = laguerre_float(degree, alpha, x_val)

        # Tolerating standard binary64 accumulation difference
        assert abs(dec_val - flt_val) < 1e-10 * (1.0 + abs(dec_val))


class TestPoleAndScalingHelpers:
    """Verify pole parameter transformations and DLMF turning scales."""

    def test_pole_parameters(self) -> None:
        """A = 2s0 - 1, q = -s0 / (s0 - 1)."""
        A, q = pole_parameters(Decimal("3"))
        assert A == Decimal("5")
        assert q == Decimal("-1.5")

        A, q = pole_parameters(Decimal("2"))
        assert A == Decimal("3")
        assert q == Decimal("-2")

    def test_turning_u_and_t_from_m(self) -> None:
        """u = t / (4n) and t = (2s0 - 1) log(m)."""
        s0 = 3.0
        m = 100
        t = t_from_m(m, s0)
        expected_t = 5.0 * math.log(100)
        assert abs(t - expected_t) < 1e-12

        u = turning_u(16, t)
        assert abs(u - (t / 64.0)) < 1e-12

    def test_nth_root_abs(self) -> None:
        """nth_root_abs returns |value|^(1/n)."""
        getcontext().prec = 50
        assert nth_root_abs(Decimal("0"), 5) == Decimal("0")
        assert abs(float(nth_root_abs(Decimal("32"), 5)) - 2.0) < 1e-12
        assert abs(float(nth_root_abs(Decimal("-32"), 5)) - 2.0) < 1e-12


class TestCompositeSimpson:
    """Verify numerical quadrature integration accuracy."""

    def test_polynomial_integration(self) -> None:
        """Simpson rule is exact for polynomials of degree <= 3."""
        # int_0^2 (3x^2 + 2x + 1) dx = [x^3 + x^2 + x]_0^2 = 8 + 4 + 2 = 14
        result = composite_simpson(lambda x: 3 * x**2 + 2 * x + 1, 0.0, 2.0, steps=10)
        assert abs(result - 14.0) < 1e-10

    def test_exponential_integration(self) -> None:
        """int_0^1 e^x dx = e - 1."""
        result = composite_simpson(math.exp, 0.0, 1.0, steps=100)
        assert abs(result - (math.e - 1.0)) < 1e-8


class TestZetaZerosAndSmallUPhaseDiagnostic:
    """Verify numerical zero evaluation and the explicitly small-u phase diagnostic."""

    def test_first_zeta_zeros(self) -> None:
        """Check numerical zero ordinates against standard reference values."""
        zeros = get_zeta_zeros(5)
        assert len(zeros) == 5

        # Standard reference ordinates; this test checks numerical agreement only.
        assert abs(zeros[0] - 14.1347251417) < 1e-8
        assert abs(zeros[1] - 21.0220396388) < 1e-8
        assert abs(zeros[2] - 25.0108575801) < 1e-8
        assert abs(zeros[3] - 30.4248761258) < 1e-8
        assert abs(zeros[4] - 32.9350615877) < 1e-8

    def test_small_u_phase_scaling_formula(self) -> None:
        """Verify the algebra of the small-u approximation t~=nA^2/gamma^2."""
        s0 = 3.0
        n = 16
        gamma = 25.0
        A = 5.0

        t_star = small_u_stationary_t_from_gamma(gamma, n, s0)
        expected_t = 16.0 * (25.0) / (625.0)  # 16 * 25 / 625 = 0.64
        assert abs(t_star - expected_t) < 1e-12

        u_star = small_u_stationary_u_from_gamma(gamma, s0)
        assert abs(u_star - (t_star / 64.0)) < 1e-12
        assert abs(u_star - (25.0 / (4.0 * 625.0))) < 1e-12

    def test_small_u_formula_inversion_property(self) -> None:
        """Verify the diagnostic formulas invert algebraically; this is not a uniform-phase proof."""
        s0 = 2.5
        for gamma in [14.1347, 21.0220, 50.0, 100.0, 1000.0]:
            u = small_u_stationary_u_from_gamma(gamma, s0)
            recovered = gamma_from_small_u_stationary_u(u, s0)
            assert abs(gamma - recovered) < 1e-11 * gamma

    def test_small_u_formula_gamma_decay(self) -> None:
        """The small-u diagnostic scales algebraically as gamma^-2."""
        s0 = 3.0
        u1 = small_u_stationary_u_from_gamma(10.0, s0)
        u2 = small_u_stationary_u_from_gamma(100.0, s0)
        # u2 / u1 should be 10^2 / 100^2 = 1 / 100 = 0.01
        assert abs((u2 / u1) - 0.01) < 1e-12
