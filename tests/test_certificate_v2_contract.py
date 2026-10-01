from __future__ import annotations

import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.cert.certificate_v2_contract import (
    CERTIFICATE_FORMAT_V2,
    CLAIM_PROFILE_V2,
    V2_ALLOWED_CONFIGURATIONS,
    certificate_v2_validator,
    is_allowed_v2_configuration,
    validate_certificate_v2_schema,
    validate_certificate_v2_structure,
)


ROOT = Path(__file__).resolve().parents[1]
V1_PATH = ROOT / "docs" / "contracts" / "rh-weil-certificate-v1.json"
V2_PATH = ROOT / "docs" / "contracts" / "rh-weil-certificate-v2.json"
V1_SHA256_BEFORE_P6 = "0a58b6a36055b6b56720d275e96c19d0275948872542491099cd68c454bbed48"


def _interval(value: str = "1") -> dict[str, str]:
    return {
        "lo_num": value,
        "lo_den": "1",
        "hi_num": value,
        "hi_den": "1",
    }


def _rational_interval(
    lo_num: str,
    lo_den: str,
    hi_num: str | None = None,
    hi_den: str | None = None,
) -> dict[str, str]:
    return {
        "lo_num": lo_num,
        "lo_den": lo_den,
        "hi_num": hi_num if hi_num is not None else lo_num,
        "hi_den": hi_den if hi_den is not None else lo_den,
    }


def _matrix(dimension: int = 2) -> dict[str, object]:
    entries: list[dict[str, object]] = []
    for row in range(dimension):
        for col in range(dimension):
            value = "1" if row == col else "0"
            entries.append(
                {
                    "row": row,
                    "col": col,
                    "lo_num": value,
                    "lo_den": "1",
                    "hi_num": value,
                    "hi_den": "1",
                }
            )
    return {"dimension": dimension, "entries": entries}


def _exact_matrix(dimension: int = 1) -> dict[str, object]:
    return {
        "dimension": dimension,
        "entries": [
            {
                "row": row,
                "col": col,
                "num": "1" if row == col else "0",
                "den": "1",
            }
            for row in range(dimension)
            for col in range(dimension)
        ],
    }


def _term(m: int, base_prime: int, exponent: int) -> dict[str, object]:
    return {
        "m": m,
        "base_prime": base_prime,
        "exponent": exponent,
        "log_m": _interval(),
        "tau": _rational_interval("3", "2"),
        "von_mangoldt": _interval(),
        "coefficient": _rational_interval("1", "10"),
        "compressed_shift_norm_bound": _interval(),
        "complement_contribution": _rational_interval("1", "10"),
    }


def _fixture() -> dict[str, object]:
    matrix = _matrix()
    witness = _exact_matrix()
    return {
        "format": CERTIFICATE_FORMAT_V2,
        "claim": "v2-structural-fixture",
        "claim_profile": CLAIM_PROFILE_V2,
        "support_T": {"num": "2", "den": "3", "frac": "2/3"},
        "basis": {"type": "legendre", "dimension": 2, "domain": "[-1, 1]"},
        "parity_sector": "both",
        "dimension": 2,
        "constants": {"c_T": _interval("0"), "rho_R": _interval("0")},
        "arithmetic_terms": [_term(2, 2, 1), _term(3, 3, 1)],
        "matrix": matrix,
        "tail_bound": {
            "type": "multi_prime_power_legendre_component_gram_schur",
            "harmonic_index": 2,
            "active_set_rule": "prime_powers_with_log_m_lt_2T",
            "complement_rule": "H_N-c_T-sum(c_m*b_m)-rho_R",
            "grouped_components": ["V", "P", "R"],
            "factor": {"num": "3", "den": "1"},
            "factor_claim": "C-0059",
        },
        "schur_proof": {
            "residual_order": 32,
            "GV": matrix,
            "GP": matrix,
            "GR": matrix,
            "even_witness": witness,
            "odd_witness": witness,
        },
        "generator_metadata": {
            "generator": "p6-test",
            "script": "tests.test_certificate_v2_contract",
            "version": "1",
            "git_commit": "0" * 40,
            "git_dirty": False,
            "flint_version": "test",
            "python_flint_version": "test",
            "prec_bits": 256,
            "timestamp_utc": "2026-10-01T16:30:00Z",
        },
    }


def test_p6_v1_schema_is_byte_unchanged() -> None:
    assert hashlib.sha256(V1_PATH.read_bytes()).hexdigest() == V1_SHA256_BEFORE_P6


def test_p6_v2_schema_is_valid_and_profile_is_closed() -> None:
    schema = json.loads(V2_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert schema["properties"]["format"]["const"] == CERTIFICATE_FORMAT_V2
    assert schema["properties"]["claim_profile"]["const"] == CLAIM_PROFILE_V2
    assert schema["additionalProperties"] is False


def test_p6_structural_fixture_is_schema_valid_but_not_theorem_admitted() -> None:
    fixture = _fixture()
    assert certificate_v2_validator().is_valid(fixture)
    assert validate_certificate_v2_schema(fixture) == (True, "ok")
    assert validate_certificate_v2_structure(fixture) == (True, "ok")
    assert V2_ALLOWED_CONFIGURATIONS == frozenset()
    assert not is_allowed_v2_configuration(Fraction(2, 3), 2)
    assert not is_allowed_v2_configuration(Fraction(2, 3), 160)


def test_p6_term_specific_constants_live_only_in_arithmetic_terms() -> None:
    fixture = _fixture()
    fixture["constants"]["c3"] = _interval()  # type: ignore[index]
    assert not certificate_v2_validator().is_valid(fixture)

    fixture = _fixture()
    fixture["constants"]["c2"] = _interval()  # type: ignore[index]
    assert not certificate_v2_validator().is_valid(fixture)


def test_p6_arithmetic_term_requires_identity_and_interval_data() -> None:
    required = {
        "m",
        "base_prime",
        "exponent",
        "log_m",
        "tau",
        "von_mangoldt",
        "coefficient",
        "compressed_shift_norm_bound",
        "complement_contribution",
    }
    schema = json.loads(V2_PATH.read_text(encoding="utf-8"))
    assert set(schema["$defs"]["arithmeticTerm"]["required"]) == required

    for field in required:
        fixture = _fixture()
        del fixture["arithmetic_terms"][0][field]  # type: ignore[index]
        assert not certificate_v2_validator().is_valid(fixture), field


def test_p6_structural_validator_enforces_canonical_term_identity_and_order() -> None:
    fixture = _fixture()
    fixture["arithmetic_terms"] = list(reversed(fixture["arithmetic_terms"]))  # type: ignore[index]
    valid, message = validate_certificate_v2_structure(fixture)
    assert valid is False
    assert "strictly increasing by m" in message or "was expected" in message

    fixture = _fixture()
    fixture["arithmetic_terms"][1]["base_prime"] = 2  # type: ignore[index]
    valid, message = validate_certificate_v2_structure(fixture)
    assert valid is False
    assert "m = base_prime^exponent" in message or "was expected" in message

    fixture = _fixture()
    fixture["arithmetic_terms"][1]["base_prime"] = 4  # type: ignore[index]
    fixture["arithmetic_terms"][1]["m"] = 4  # type: ignore[index]
    valid, message = validate_certificate_v2_structure(fixture)
    assert valid is False
    assert "base_prime must be prime" in message or "was expected" in message


def test_p6_structural_validator_rejects_noncanonical_intervals_and_dimensions() -> None:
    fixture = _fixture()
    fixture["arithmetic_terms"][0]["coefficient"]["lo_num"] = "2"  # type: ignore[index]
    fixture["arithmetic_terms"][0]["coefficient"]["lo_den"] = "2"  # type: ignore[index]
    valid, message = validate_certificate_v2_structure(fixture)
    assert valid is False
    assert "reduced canonical rational" in message

    fixture = _fixture()
    fixture["schur_proof"]["GP"] = copy.deepcopy(fixture["schur_proof"]["GP"])  # type: ignore[index]
    fixture["schur_proof"]["GP"]["dimension"] = 3  # type: ignore[index]
    valid, message = validate_certificate_v2_structure(fixture)
    assert valid is False
    assert "$.schur_proof.GP.dimension must equal 2" in message


def test_p6_schur_proof_requires_gp_and_rejects_g2_g3() -> None:
    fixture = _fixture()
    del fixture["schur_proof"]["GP"]  # type: ignore[index]
    assert not certificate_v2_validator().is_valid(fixture)

    for legacy_name in ("G2", "G3"):
        fixture = _fixture()
        fixture["schur_proof"][legacy_name] = _matrix()  # type: ignore[index]
        assert not certificate_v2_validator().is_valid(fixture), legacy_name


def test_p6_tail_rule_is_closed_to_verified_factor_three_claim() -> None:
    fixture = _fixture()
    fixture["tail_bound"]["factor"] = {"num": "2", "den": "1"}  # type: ignore[index]
    assert not certificate_v2_validator().is_valid(fixture)

    fixture = _fixture()
    fixture["tail_bound"]["factor_claim"] = "unverified"  # type: ignore[index]
    assert not certificate_v2_validator().is_valid(fixture)

    fixture = _fixture()
    fixture["tail_bound"]["grouped_components"] = ["V", "P", "R", "extra"]  # type: ignore[index]
    assert not certificate_v2_validator().is_valid(fixture)


def test_p6_structural_validation_does_not_grant_theorem_admission() -> None:
    fixture = _fixture()
    assert validate_certificate_v2_structure(fixture) == (True, "ok")
    support = Fraction(fixture["support_T"]["frac"])  # type: ignore[index]
    assert not is_allowed_v2_configuration(support, int(fixture["dimension"]))


def test_p6_schema_does_not_embed_a_support_dimension_theorem_whitelist() -> None:
    schema_text = V2_PATH.read_text(encoding="utf-8")
    assert '"oneOf"' not in schema_text
    for retained_v1_support in ("7/20", "2/5", "17/40", "9/20", "19/40", "1/2", "21/40", "27/50"):
        assert retained_v1_support not in schema_text
