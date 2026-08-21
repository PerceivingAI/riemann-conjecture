from __future__ import annotations

import copy

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
