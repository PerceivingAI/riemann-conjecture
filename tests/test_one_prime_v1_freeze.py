"""Regression guard for the frozen one-prime v1 theorem path.

The multi-prime upgrade must be additive. These checks deliberately lock the
historical v1 support boundary, theorem admission grid, schema semantics, and
retained theorem identities so future tooling cannot silently broaden or
reinterpret C-0050 through C-0057.
"""

from __future__ import annotations

import json
from fractions import Fraction

import pytest

from scripts.cert.constants import require_one_prime_support
from scripts.cert.exact_prime_schur_certificate import ALLOWED_CONFIGURATIONS
from scripts.cert.export_certificate import SCHEMA_PATH, _is_allowed_exact_prime_configuration
from scripts.cert.verify_retained_proofs import (
    EXACT_PRIME_PROFILE,
    EXPECTED_RETAINED_CLAIMS_V1,
    MANIFEST_FORMAT_V1,
    load_retained_proof_manifest,
)


EXPECTED_V1_CONFIGURATIONS = {
    (Fraction(7, 20), 32),
    (Fraction(2, 5), 40),
    (Fraction(17, 40), 48),
    (Fraction(9, 20), 56),
    (Fraction(19, 40), 68),
    (Fraction(1, 2), 80),
    (Fraction(21, 40), 96),
    (Fraction(27, 50), 104),
}

EXPECTED_RETAINED_IDENTITIES = {
    "C-0050": ("7/20", 32, "localized_weil_positivity_T_7_20"),
    "C-0051": ("2/5", 40, "localized_weil_positivity_T_2_5"),
    "C-0052": ("17/40", 48, "localized_weil_positivity_T_17_40"),
    "C-0053": ("9/20", 56, "localized_weil_positivity_T_9_20"),
    "C-0054": ("19/40", 68, "localized_weil_positivity_T_19_40"),
    "C-0055": ("1/2", 80, "localized_weil_positivity_T_1_2"),
    "C-0056": ("21/40", 96, "localized_weil_positivity_T_21_40"),
    "C-0057": ("27/50", 104, "localized_weil_positivity_T_27_50"),
}


def test_v1_support_gate_remains_strictly_one_prime() -> None:
    require_one_prime_support(7, 20)
    require_one_prime_support(27, 50)

    with pytest.raises(ValueError, match="one-prime window"):
        require_one_prime_support(1, 3)
    # 11/20 = 0.55 lies just above log(3)/2 ~= 0.549306.
    with pytest.raises(ValueError, match="one-prime window"):
        require_one_prime_support(11, 20)


def test_v1_admission_grid_is_frozen_to_eight_pairs() -> None:
    assert ALLOWED_CONFIGURATIONS == EXPECTED_V1_CONFIGURATIONS
    for support, dimension in EXPECTED_V1_CONFIGURATIONS:
        assert _is_allowed_exact_prime_configuration(support, dimension)

    assert not _is_allowed_exact_prime_configuration(Fraction(11, 20), 104)
    assert not _is_allowed_exact_prime_configuration(Fraction(27, 50), 108)


def test_v1_schema_keeps_c2_g2_exact_prime_semantics() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema["properties"]["format"]["const"] == "rh-weil-certificate-v1"
    assert set(schema["properties"]["claim_profile"]["enum"]) == {
        "synthetic_matrix",
        "digamma_finite_block",
        "exact_prime_legendre_schur",
    }

    exact_prime_rule = next(
        rule["then"]
        for rule in schema["allOf"]
        if rule["if"]["properties"]["claim_profile"].get("const")
        == "exact_prime_legendre_schur"
    )
    constants_rule = exact_prime_rule["properties"]["constants"]
    assert constants_rule["required"] == ["c2", "c_T", "rho_R"]
    assert constants_rule["minProperties"] == 3
    assert constants_rule["maxProperties"] == 3

    schur_rule = schema["$defs"]["schurProof"]
    assert schur_rule["required"] == [
        "residual_order",
        "GV",
        "G2",
        "GR",
        "even_witness",
        "odd_witness",
    ]
    assert schur_rule["properties"]["residual_order"]["const"] == 32


def test_v1_retained_chain_identity_is_frozen_to_c0050_through_c0057() -> None:
    manifest = load_retained_proof_manifest()

    assert manifest.format == MANIFEST_FORMAT_V1
    assert EXPECTED_RETAINED_CLAIMS_V1 == frozenset(EXPECTED_RETAINED_IDENTITIES)
    observed = {
        proof.claim: (proof.support_t, proof.dimension, proof.verified_scope)
        for proof in manifest.proofs
    }
    assert observed == EXPECTED_RETAINED_IDENTITIES
    assert all(proof.claim_profile == EXACT_PRIME_PROFILE for proof in manifest.proofs)
