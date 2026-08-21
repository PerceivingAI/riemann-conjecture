"""Comprehensive test suite for the scripts.cert certificate generation pipeline."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest
from flint import acb, arb, arb_mat, ctx, fmpq, fmpq_mat

from scripts.cert import (
    constants,
    export_certificate,
    matrices,
    quadrature,
    residual_kernel,
)


class TestConstants:
    def test_support_T(self) -> None:
        t_val = constants.support_T(7, 20)
        assert t_val == fmpq(7, 20)

    def test_arb_to_rational_enclosure(self) -> None:
        with ctx.workprec(128):
            pi_val = arb.pi()
            lo, hi = constants.arb_to_rational_enclosure(pi_val)
            assert isinstance(lo, Fraction)
            assert isinstance(hi, Fraction)
            assert lo <= hi
            # Numerical sanity bounds
            assert Fraction(314, 100) < lo < Fraction(315, 100)
            assert Fraction(314, 100) < hi < Fraction(315, 100)

    def test_log2_and_sqrt2_enclosures(self) -> None:
        with ctx.workprec(128):
            log2_arb = constants.log2_enclosure(128)
            sqrt2_arb = constants.sqrt2_enclosure(128)
            c2_arb = constants.c2_enclosure(128)

            lo_c2, hi_c2 = constants.arb_to_rational_enclosure(c2_arb)
            assert lo_c2 <= hi_c2
            # c2 = log(2)/sqrt(2) ~ 0.490129...
            assert Fraction(49, 100) < lo_c2 < Fraction(50, 100)

    def test_digamma_constants(self) -> None:
        a0 = constants.digamma_ak(0)
        a1 = constants.digamma_ak(1)
        a2 = constants.digamma_ak(2)
        assert a0 == fmpq(1, 4)
        assert a1 == fmpq(5, 4)
        assert a2 == fmpq(9, 4)

        with pytest.raises(ValueError):
            constants.digamma_ak(-1)

        m0_arb = constants.m0_digamma_enclosure(128)
        lo_m0, hi_m0 = constants.arb_to_rational_enclosure(m0_arb)
        assert lo_m0 <= hi_m0
        # m0 = psi(1/4) - log(pi) ~ -5.37218...
        assert lo_m0 < Fraction(-53, 10) < hi_m0 or hi_m0 < Fraction(-53, 10)

    def test_certified_bundle(self) -> None:
        bundle = constants.get_certified_constants_bundle(prec=128, num=7, den=20)
        assert bundle["precision_bits"] == 128
        assert bundle["support_T"]["frac"] == "7/20"
        for k in ("log2", "sqrt2", "pi", "euler_gamma", "tau", "c2", "c_T", "m0_digamma"):
            assert k in bundle
            assert "lo_num" in bundle[k]
            assert "lo_den" in bundle[k]
            assert "hi_num" in bundle[k]
            assert "hi_den" in bundle[k]


class TestQuadrature:
    def test_legendre_polynomials(self) -> None:
        with ctx.workprec(80):
            half = acb("0.5")
            p0 = quadrature.legendre_p_acb(0, half)
            p1 = quadrature.legendre_p_acb(1, half)
            p2 = quadrature.legendre_p_acb(2, half)
            assert p0 == acb(1)
            assert p1 == half
            # P2(x) = (3x^2 - 1)/2 => P2(0.5) = (3*0.25 - 1)/2 = -0.125
            assert p2 == acb("-0.125")

    def test_chebyshev_polynomials(self) -> None:
        with ctx.workprec(80):
            half = acb("0.5")
            t0 = quadrature.chebyshev_t_acb(0, half)
            t1 = quadrature.chebyshev_t_acb(1, half)
            t2 = quadrature.chebyshev_t_acb(2, half)
            assert t0 == acb(1)
            assert t1 == half
            # T2(x) = 2x^2 - 1 => T2(0.5) = 2*0.25 - 1 = -0.5
            assert t2 == acb("-0.5")

    def test_monomial_basis(self) -> None:
        with ctx.workprec(80):
            half = acb("0.5")
            m0 = quadrature.monomial_acb(0, half)
            m3 = quadrature.monomial_acb(3, half)
            assert m0 == acb(1)
            assert m3 == acb("0.125")

    def test_legendre_orthogonality(self) -> None:
        with ctx.workprec(80):
            i00 = quadrature.rigorous_real_integral_1d(lambda x, _: quadrature.legendre_p_acb(0, x) ** 2, -1, 1)
            i11 = quadrature.rigorous_real_integral_1d(lambda x, _: quadrature.legendre_p_acb(1, x) ** 2, -1, 1)
            i01 = quadrature.rigorous_real_integral_1d(
                lambda x, _: quadrature.legendre_p_acb(0, x) * quadrature.legendre_p_acb(1, x), -1, 1
            )
            # int P0^2 = 2
            assert arb(199) / 100 < i00 < arb(201) / 100
            # int P1^2 = 2/3
            assert arb(66) / 100 < i11 < arb(67) / 100
            # int P0*P1 = 0
            assert arb(0) in i01 or abs(i01) < arb(1e-15)

    def test_double_integral(self) -> None:
        with ctx.workprec(80):
            res = quadrature.rigorous_double_integral_2d(lambda x, y, _: x + y, 0, 1, 0, 1, prec=80)
            # int_0^1 int_0^1 (x+y) dx dy = 1
            assert arb(99) / 100 < res.real < arb(101) / 100


class TestResidualKernel:
    def test_digamma_inner_products_matrix_symmetry(self) -> None:
        with ctx.workprec(64):
            t_val = arb(7) / 20
            gram = residual_kernel.digamma_inner_products_matrix("legendre", 2, t_val, prec=64)
            assert gram.nrows() == 2
            assert gram.ncols() == 2
            # Check diagonal positivity
            assert gram[0, 0] > arb(0)
            assert gram[1, 1] > arb(0)
            # Check opposite parity orthogonality
            assert gram[0, 1] == arb(0)
            assert gram[1, 0] == arb(0)

    def test_digamma_bracket_matrix(self) -> None:
        with ctx.workprec(64):
            t_val = arb(7) / 20
            b0 = residual_kernel.digamma_bracket_matrix(0, "legendre", 2, t_val, prec=64)
            assert b0[0, 0] > arb(0)
            assert b0[1, 1] > arb(0)


class TestMatrices:
    def test_rational_interval_operations(self) -> None:
        i1 = matrices.RationalInterval(Fraction(1, 2), Fraction(3, 4))
        i2 = matrices.RationalInterval(Fraction(1, 4), Fraction(1, 2))

        # Addition: [1/2+1/4, 3/4+1/2] = [3/4, 5/4]
        i_add = i1 + i2
        assert i_add.lo == Fraction(3, 4)
        assert i_add.hi == Fraction(5, 4)

        # Subtraction: [1/2-1/2, 3/4-1/4] = [0, 1/2]
        i_sub = i1 - i2
        assert i_sub.lo == Fraction(0)
        assert i_sub.hi == Fraction(1, 2)

        # Multiplication: [1/2*1/4, 3/4*1/2] = [1/8, 3/8]
        i_mul = i1 * i2
        assert i_mul.lo == Fraction(1, 8)
        assert i_mul.hi == Fraction(3, 8)

        # Division: [1/2 / (1/2), 3/4 / (1/4)] = [1, 3]
        i_div = i1 / i2
        assert i_div.lo == Fraction(1)
        assert i_div.hi == Fraction(3)

        # Squaring
        i_sqr = i1.sqr()
        assert i_sqr.lo == Fraction(1, 4)
        assert i_sqr.hi == Fraction(9, 16)

    def test_rational_interval_zero_division(self) -> None:
        i1 = matrices.RationalInterval(1, 2)
        i_zero = matrices.RationalInterval(-1, 1)
        with pytest.raises(ZeroDivisionError):
            _ = i1 / i_zero

    def test_exact_ldl_positive_definite(self) -> None:
        # Positive definite symmetric matrix: [[4, 1], [1, 3]]
        # D0 = 4, L10 = 1/4, D1 = 3 - (1/4)^2 * 4 = 3 - 1/4 = 11/4 > 0
        grid = [
            [matrices.RationalInterval(4), matrices.RationalInterval(1)],
            [matrices.RationalInterval(1), matrices.RationalInterval(3)],
        ]
        mat = matrices.RationalIntervalMatrix(grid)
        assert mat.is_symmetric()
        L, D, is_pos = mat.exact_ldl()
        assert is_pos is True
        assert D[0].lo == Fraction(4)
        assert D[1].lo == Fraction(11, 4)
        assert L[1][0].lo == Fraction(1, 4)

    def test_exact_ldl_indefinite(self) -> None:
        # Indefinite matrix: [[1, 2], [2, 1]]
        # D0 = 1, L10 = 2, D1 = 1 - 4 = -3 < 0
        grid = [
            [matrices.RationalInterval(1), matrices.RationalInterval(2)],
            [matrices.RationalInterval(2), matrices.RationalInterval(1)],
        ]
        mat = matrices.RationalIntervalMatrix(grid)
        L, D, is_pos = mat.exact_ldl()
        assert is_pos is False

    def test_fmpq_mat_properties(self) -> None:
        m = fmpq_mat(2, 2, [fmpq(2), fmpq(1), fmpq(1), fmpq(3)])
        props = matrices.fmpq_mat_properties(m)
        assert props["dimension"] == 2
        assert props["determinant"] == "5"
        assert props["is_invertible"] is True

    def test_arb_mat_eigenvalue_cross_check(self) -> None:
        m = arb_mat(2, 2, [arb(4), arb(1), arb(1), arb(3)])
        res = matrices.arb_mat_eigenvalue_cross_check(m, prec=64)
        assert res["status"] == "computed"
        assert res["role"] == "secondary_cross_check_only"
        assert res["all_real_positive"] is True


class TestExportCertificate:
    def test_validate_certificate_schema(self) -> None:
        valid_cert = {
            "format": export_certificate.CERTIFICATE_FORMAT_V1,
            "claim": "Test claim",
            "support_T": {"num": 7, "den": 20, "frac": "7/20"},
            "basis": {"type": "legendre", "dimension": 1, "domain": "[-T, T]"},
            "parity_sector": "both",
            "dimension": 1,
            "constants": {},
            "matrix": {
                "dimension": 1,
                "is_symmetric": True,
                "entries": [
                    {
                        "row": 0,
                        "col": 0,
                        "lo_num": "1",
                        "lo_den": "1",
                        "hi_num": "2",
                        "hi_den": "1",
                    }
                ],
            },
            "tail_bound": {"type": "none"},
            "generator_metadata": {},
        }
        ok, msg = export_certificate.validate_certificate_schema(valid_cert)
        assert ok is True

        # Test invalid format
        invalid_cert = dict(valid_cert)
        invalid_cert["format"] = "wrong-v0"
        ok, msg = export_certificate.validate_certificate_schema(invalid_cert)
        assert ok is False
        assert "Unsupported format" in msg

        # Test missing field
        missing_cert = dict(valid_cert)
        del missing_cert["claim"]
        ok, msg = export_certificate.validate_certificate_schema(missing_cert)
        assert ok is False
        assert "Missing required fields" in msg

    def test_export_and_roundtrip(self, tmp_path: Path) -> None:
        out_file = tmp_path / "cert.json"
        cert = export_certificate.export_digamma_operator_certificate(
            k_max=0,
            dimension=1,
            basis_type="legendre",
            support_num=7,
            support_den=20,
            prec=64,
            output_path=out_file,
        )

        assert out_file.exists()
        loaded = json.loads(out_file.read_text(encoding="utf-8"))
        assert loaded["format"] == export_certificate.CERTIFICATE_FORMAT_V1
        assert loaded["dimension"] == 1
        assert len(loaded["matrix"]["entries"]) == 1
