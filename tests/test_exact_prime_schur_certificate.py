from __future__ import annotations

import copy

import pytest

from scripts.cert.exact_prime_schur_certificate import build_exact_prime_schur_certificate
from scripts.cert.export_certificate import validate_certificate_schema


def _contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(child) for child in value.values())
    if isinstance(value, list):
        return any(_contains_float(child) for child in value)
    return False


def test_invalid_exact_prime_configuration_fails_before_expensive_work() -> None:
    with pytest.raises(ValueError, match="claim"):
        build_exact_prime_schur_certificate(claim="")
    with pytest.raises(ValueError, match="matrix_bits"):
        build_exact_prime_schur_certificate(claim="C-test", matrix_bits=8)
    with pytest.raises(ValueError, match="witness_bits"):
        build_exact_prime_schur_certificate(claim="C-test", witness_bits=4)


def test_exact_prime_certificate_is_strict_and_float_free() -> None:
    certificate, diagnostics = build_exact_prime_schur_certificate(
        claim="pytest-exact-prime",
        prec=128,
        matrix_bits=56,
        witness_bits=28,
    )
    valid, message = validate_certificate_schema(certificate)
    assert valid, message
    assert certificate["claim_profile"] == "exact_prime_legendre_schur"
    assert certificate["dimension"] == 32
    assert certificate["tail_bound"]["type"] == "legendre_component_gram_schur"
    assert diagnostics["mu_lower"] > 0
    assert diagnostics["even_gershgorin_margin"] > 0
    assert diagnostics["odd_gershgorin_margin"] > 0
    assert not _contains_float(certificate)


def test_exact_prime_certificate_accepts_t_two_fifths_dimension_40() -> None:
    certificate, diagnostics = build_exact_prime_schur_certificate(
        claim="pytest-exact-prime-two-fifths",
        support_num=2,
        support_den=5,
        dimension=40,
        prec=256,
        matrix_bits=72,
        witness_bits=40,
    )
    valid, message = validate_certificate_schema(certificate)
    assert valid, message
    assert certificate["support_T"]["frac"] == "2/5"
    assert certificate["dimension"] == 40
    assert certificate["basis"]["dimension"] == 40
    assert certificate["tail_bound"]["harmonic_index"] == 40
    assert diagnostics["mu_lower"] > 0
    assert diagnostics["even_gershgorin_margin"] > 0
    assert diagnostics["odd_gershgorin_margin"] > 0
    assert not _contains_float(certificate)


def test_exact_prime_generator_rejects_mixed_whitelist_pair() -> None:
    try:
        build_exact_prime_schur_certificate(
            claim="pytest-exact-prime-mixed",
            support_num=2,
            support_den=5,
            dimension=32,
            prec=128,
        )
    except ValueError as error:
        assert "allows only" in str(error)
    else:
        raise AssertionError("mixed exact-prime whitelist pair must be rejected")


def test_exact_prime_certificate_accepts_seventeen_fortieths_dimension_48() -> None:
    certificate, diagnostics = build_exact_prime_schur_certificate(
        claim="pytest-exact-prime-seventeen-fortieths",
        support_num=17,
        support_den=40,
        dimension=48,
        prec=384,
        matrix_bits=88,
        witness_bits=48,
    )
    valid, message = validate_certificate_schema(certificate)
    assert valid, message
    assert certificate["support_T"]["frac"] == "17/40"
    assert certificate["dimension"] == 48
    assert certificate["basis"]["dimension"] == 48
    assert certificate["tail_bound"]["harmonic_index"] == 48
    assert diagnostics["mu_lower"] > 0
    assert diagnostics["even_gershgorin_margin"] > 0
    assert diagnostics["odd_gershgorin_margin"] > 0
    assert not _contains_float(certificate)


def test_exact_prime_certificate_accepts_nine_twentieths_dimension_56() -> None:
    certificate, diagnostics = build_exact_prime_schur_certificate(
        claim="pytest-exact-prime-nine-twentieths",
        support_num=9,
        support_den=20,
        dimension=56,
        prec=512,
        matrix_bits=104,
        witness_bits=56,
    )
    valid, message = validate_certificate_schema(certificate)
    assert valid, message
    assert certificate["support_T"]["frac"] == "9/20"
    assert certificate["dimension"] == 56
    assert certificate["basis"]["dimension"] == 56
    assert certificate["tail_bound"]["harmonic_index"] == 56
    assert diagnostics["mu_lower"] > 0
    assert diagnostics["even_gershgorin_margin"] > 0
    assert diagnostics["odd_gershgorin_margin"] > 0
    assert not _contains_float(certificate)


def test_exact_prime_python_validator_rejects_mixed_nine_twentieths_pair() -> None:
    with pytest.raises(ValueError, match="allows only"):
        build_exact_prime_schur_certificate(
            claim="pytest-exact-prime-mixed-nine-twentieths",
            support_num=9,
            support_den=20,
            dimension=48,
            prec=128,
            matrix_bits=56,
            witness_bits=28,
        )


def test_exact_prime_python_validator_rejects_mixed_seventeen_fortieths_pair() -> None:
    with pytest.raises(ValueError, match="allows only"):
        build_exact_prime_schur_certificate(
            claim="pytest-exact-prime-mixed-seventeen-fortieths",
            support_num=17,
            support_den=40,
            dimension=40,
            prec=128,
            matrix_bits=56,
            witness_bits=28,
        )


def test_exact_prime_python_validator_rejects_wrong_factor() -> None:
    certificate, _ = build_exact_prime_schur_certificate(
        claim="pytest-exact-prime-factor",
        prec=128,
        matrix_bits=48,
        witness_bits=24,
    )
    bad = copy.deepcopy(certificate)
    bad["tail_bound"]["factor"] = {"num": "2", "den": "1"}
    valid, _ = validate_certificate_schema(bad)
    assert not valid
