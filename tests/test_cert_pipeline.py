"""Comprehensive test suite for the scripts.cert certificate generation pipeline."""

from __future__ import annotations

import copy
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
            assert arb(0) in i01 or abs(i01) < arb(1) / (arb(10) ** 15)

    def test_double_integral(self) -> None:
        with ctx.workprec(80):
            res = quadrature.rigorous_double_integral_2d(lambda x, y, _: x + y, 0, 1, 0, 1, prec=80)
            # int_0^1 int_0^1 (x+y) dx dy = 1
            assert arb(99) / 100 < res.real < arb(101) / 100

    @pytest.mark.parametrize(
        ("a", "b", "kwargs"),
        [
            (0.1, 1, {}),
            (0, 0.7, {}),
            (0, 1, {"rel_tol": 1e-12}),
            (0, 1, {"abs_tol": 1e-12}),
            (False, 1, {}),
        ],
    )
    def test_float_and_boolean_inputs_are_rejected(
        self,
        a: object,
        b: object,
        kwargs: dict[str, object],
    ) -> None:
        with pytest.raises(TypeError):
            quadrature.rigorous_integral_1d(lambda x, _: x, a, b, **kwargs)

    def test_exact_endpoint_types_are_accepted(self) -> None:
        inputs = [
            (0, 1),
            (fmpq(0), fmpq(1)),
            (arb(0), arb(1)),
            (acb(0), acb(1)),
        ]
        for lower, upper in inputs:
            result = quadrature.rigorous_integral_1d(lambda x, _: x, lower, upper)
            assert arb(1) / 2 in result.real

    def test_real_projection_requires_zero_containment(self) -> None:
        assert quadrature.require_real_enclosure(acb(1), "real test") == arb(1)
        tiny_nonzero_imaginary = acb(arb(1), arb(1) / (arb(10) ** 100))
        with pytest.raises(ValueError, match="excludes zero"):
            quadrature.require_real_enclosure(tiny_nonzero_imaginary, "non-real test")


class TestResidualKernel:
    def test_public_matrix_builders_reject_inexact_or_invalid_parameters(self) -> None:
        with pytest.raises(TypeError, match="ordinary float"):
            residual_kernel.digamma_inner_products_matrix("legendre", 1, 0.35, prec=64)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="ordinary float"):
            residual_kernel.exponential_convolution_matrix(0.25, "legendre", 1, arb(7) / 20, prec=64)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="k_max"):
            residual_kernel.digamma_positive_operator_matrix(-1, "legendre", 1, arb(7) / 20, prec=64)
        with pytest.raises(ValueError, match="positive"):
            residual_kernel.suzuki_residual_kernel_matrix("legendre", 1, 0, prec=64)
        with pytest.raises(TypeError, match="prec"):
            residual_kernel.digamma_inner_products_matrix("legendre", 1, arb(7) / 20, prec=16)

    def test_digamma_bracket_rejects_wrong_gram_dimension(self) -> None:
        gram = arb_mat(2, 2)
        with pytest.raises(ValueError, match="1x1"):
            residual_kernel.digamma_bracket_matrix(
                0, "legendre", 1, arb(7) / 20, gram_mat=gram, prec=64
            )

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

    def test_suzuki_residual_second_derivative_identities(self) -> None:
        zero_value = residual_kernel.suzuki_residual_r_second(0, prec=96)
        assert arb(-7) / 4 in zero_value

        argument = fmpq(1, 5)
        positive = residual_kernel.suzuki_residual_r_second(argument, prec=96)
        negative = residual_kernel.suzuki_residual_r_second(-argument, prec=96)
        assert positive.overlaps(negative)

        u = arb(1) / 5
        direct = -((u / 2).exp() + (-u / 2).exp())
        direct += (-u / 2).exp() / (1 - (-2 * u).exp()) - 1 / (2 * u)
        assert positive.overlaps(direct)

    def test_suzuki_residual_rejects_float_input(self) -> None:
        with pytest.raises(TypeError):
            residual_kernel.suzuki_residual_r_second(0.1)

    def test_suzuki_matrix_rejects_caller_kernel_substitution(self) -> None:
        with pytest.raises(TypeError, match="r_second_deriv"):
            residual_kernel.suzuki_residual_kernel_matrix(
                basis_type="legendre",
                dim=1,
                T_val=arb(7) / 20,
                prec=64,
                r_second_deriv=lambda value, analytic: value,
            )

    def test_canonical_suzuki_residual_matrix(self) -> None:
        matrix = residual_kernel.suzuki_residual_kernel_matrix(
            basis_type="legendre",
            dim=2,
            T_val=arb(7) / 20,
            prec=64,
        )
        assert matrix[0, 1] == arb(0)
        assert matrix[1, 0] == arb(0)
        assert matrix[0, 0].is_finite()
        assert matrix[1, 1].is_finite()


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

    def test_rational_interval_rejects_binary_float_inputs(self) -> None:
        with pytest.raises(TypeError, match="int or Fraction"):
            matrices.RationalInterval(0.1)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="canonical integer"):
            matrices.RationalInterval.from_dict(
                {"lo_num": 0.1, "lo_den": "1", "hi_num": "1", "hi_den": "1"}
            )

    def test_matrix_from_entries_rejects_duplicate_or_missing_coordinates(self) -> None:
        valid = matrices.RationalIntervalMatrix(
            [
                [matrices.RationalInterval(2), matrices.RationalInterval(0)],
                [matrices.RationalInterval(0), matrices.RationalInterval(2)],
            ]
        ).to_entries()
        round_trip = matrices.RationalIntervalMatrix.from_entries(2, valid)
        assert round_trip.is_symmetric()

        duplicate = copy.deepcopy(valid)
        duplicate[-1]["row"] = 0
        duplicate[-1]["col"] = 0
        with pytest.raises(ValueError, match="duplicate"):
            matrices.RationalIntervalMatrix.from_entries(2, duplicate)

        with pytest.raises(ValueError, match="exactly 4"):
            matrices.RationalIntervalMatrix.from_entries(2, valid[:-1])

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

    def test_exact_ldl_rejects_nonsymmetric_matrix(self) -> None:
        mat = matrices.RationalIntervalMatrix(
            [
                [matrices.RationalInterval(2), matrices.RationalInterval(100)],
                [matrices.RationalInterval(0), matrices.RationalInterval(2)],
            ]
        )
        assert mat.is_symmetric() is False
        with pytest.raises(ValueError, match="symmetric"):
            mat.exact_ldl()
        result = matrices.verify_matrix_positivity_ldl(mat)
        assert result["verified_positive_definite"] is False
        assert result["is_symmetric"] is False

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


class TestExactConstantDiagnostics:
    def test_exact_constant_bundle_checks_bounds_without_mutating_global_precision(self) -> None:
        from scripts.weil_exact_constants import build_payload

        before = ctx.prec
        payload = build_payload(96)
        assert ctx.prec == before
        assert payload["precision_bits"] == 96
        bounds = payload["certified_rational_bounds"]
        assert isinstance(bounds, dict)
        checks = bounds["checks"]
        assert isinstance(checks, dict)
        assert checks and all(checks.values())


class TestEndpointAbsorptionCertificate:
    def test_exact_endpoint_absorption_certificate(self) -> None:
        from scripts.weil_endpoint_absorption_certificate import certify

        result = certify()
        assert result["c2_over_kappa_upper"] == "31/100"
        assert result["retained_V_fraction_lower"] == "69/100"
        assert result["conclusion"] == "V + P_2 >= (69/100) V >= 0"


class TestExportCertificate:
    @staticmethod
    def _apply_operations(base: dict[str, object], operations: list[dict[str, object]]) -> dict[str, object]:
        certificate = copy.deepcopy(base)
        for operation in operations:
            path = operation["path"]
            assert isinstance(path, list)
            target: object = certificate
            for part in path[:-1]:
                target = target[part]  # type: ignore[index]
            final = path[-1]
            if operation["op"] == "set":
                target[final] = copy.deepcopy(operation["value"])  # type: ignore[index]
            elif operation["op"] == "delete":
                del target[final]  # type: ignore[index]
            else:
                raise AssertionError(f"Unknown conformance operation: {operation['op']}")
        return certificate

    def test_shared_conformance_corpus(self) -> None:
        corpus = json.loads(Path("tests/certificate_conformance.json").read_text(encoding="utf-8"))
        for case in corpus["cases"]:
            certificate = self._apply_operations(corpus["base_certificate"], case["operations"])
            valid, message = export_certificate.validate_certificate_schema(certificate)
            assert valid is case["valid"], f"{case['name']}: {message}"

    def test_export_and_roundtrip(self, tmp_path: Path) -> None:
        out_file = tmp_path / "cert.json"
        cert = export_certificate.export_digamma_operator_certificate(
            claim="audit-claim-sentinel",
            k_max=0,
            dimension=1,
            basis_type="legendre",
            support_num=7,
            support_den=20,
            prec=64,
            output_path=out_file,
        )

        loaded = json.loads(out_file.read_text(encoding="utf-8"))
        assert loaded == cert
        assert loaded["claim"] == "audit-claim-sentinel"
        assert loaded["format"] == export_certificate.CERTIFICATE_FORMAT_V1
        assert loaded["claim_profile"] == "digamma_finite_block"
        assert loaded["tail_bound"]["type"] == "nonnegative_digamma_remainder"
        assert loaded["matrix"]["dimension"] == 1

        def assert_no_float(value: object) -> None:
            assert not isinstance(value, float)
            if isinstance(value, dict):
                for child in value.values():
                    assert_no_float(child)
            elif isinstance(value, list):
                for child in value:
                    assert_no_float(child)

        assert_no_float(loaded)

    def test_rust_verifier_integration(self, tmp_path: Path) -> None:
        import shutil
        import subprocess

        cargo_bin = shutil.which("cargo")
        if not cargo_bin:
            pytest.skip("cargo not found in PATH")

        out_file = tmp_path / "synthetic_pos_cert.json"
        matrix = matrices.RationalIntervalMatrix(
            [
                [matrices.RationalInterval(4), matrices.RationalInterval(1)],
                [matrices.RationalInterval(1), matrices.RationalInterval(3)],
            ]
        )
        cert = export_certificate.build_certificate(
            claim="Pytest to Rust integration test",
            claim_profile="synthetic_matrix",
            matrix=matrix,
            basis_type="legendre",
            basis_domain="[-T, T]",
            parity_sector="both",
            support_num=7,
            support_den=20,
            constants={},
            tail_bound={"type": "exact_scalar_identity", "lambda": {"num": "0", "den": "1"}},
            prec_bits=64,
        )
        out_file.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")

        cmd = [cargo_bin, "run", "-q", "-p", "rh_cert", "--", "verify", "--cert", str(out_file), "--json"]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert proc.returncode == 0, proc.stderr
        outcome = json.loads(proc.stdout)
        assert outcome["passed"] is True
        assert outcome["tail_lower_bound"] == "0/1"
        assert outcome["ldl_report"]["is_positive_definite"] is True

    def test_formal_schema_file_validation(self) -> None:
        schema_path = Path("docs/contracts/rh-weil-certificate-v1.json")
        schema_data = json.loads(schema_path.read_text(encoding="utf-8"))
        assert schema_data["title"] == "RH Weil exact interval certificate format v1"
        assert "claim_profile" in schema_data["required"]
        assert schema_data["properties"]["format"]["const"] == "rh-weil-certificate-v1"
        assert schema_data["additionalProperties"] is False

    def test_lean4_formal_build(self) -> None:
        import shutil
        import subprocess

        lake_bin = shutil.which("lake")
        if not lake_bin:
            pytest.skip("lake (Lean 4 build tool) not found in PATH")

        formal_dir = Path("formal")
        assert formal_dir.exists()
        cmd = [lake_bin, "build"]
        proc = subprocess.run(cmd, cwd=str(formal_dir), capture_output=True, text=True, check=False)
        assert proc.returncode == 0, f"lake build failed: {proc.stderr}\n{proc.stdout}"
