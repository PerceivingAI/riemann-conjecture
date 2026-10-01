"""P8 cross-layer adversarial and closed-grid v2 consistency gates."""

from __future__ import annotations

import copy
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from scripts import weil_multi_prime_continuation_driver as multi_driver
from scripts.cert.certificate_v2_contract import (
    V2_ALLOWED_CONFIGURATIONS,
    certificate_v2_validator,
    is_allowed_v2_configuration,
    validate_certificate_v2_structure,
)
from scripts.cert.constants import require_one_prime_support


ROOT = Path(__file__).resolve().parents[1]
CROSS_LAYER_CORPUS = ROOT / "tests" / "data" / "certificate-v2-cross-layer-v1.json"
ADMISSION_CORPUS = ROOT / "tests" / "data" / "multi-prime-admission-v2.json"
SCHEMA_PATH = ROOT / "docs" / "contracts" / "rh-weil-certificate-v2.json"


def _interval(num: str = "1", den: str = "1") -> dict[str, str]:
    return {
        "lo_num": num,
        "lo_den": den,
        "hi_num": num,
        "hi_den": den,
    }


def _matrix(dimension: int, diagonal: str = "1") -> dict[str, object]:
    return {
        "dimension": dimension,
        "entries": [
            {
                "row": row,
                "col": col,
                "lo_num": diagonal if row == col else "0",
                "lo_den": "1",
                "hi_num": diagonal if row == col else "0",
                "hi_den": "1",
            }
            for row in range(dimension)
            for col in range(dimension)
        ],
    }


def _exact_identity(dimension: int) -> dict[str, object]:
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


def _term(m: int) -> dict[str, object]:
    return {
        "m": m,
        "base_prime": m,
        "exponent": 1,
        "log_m": _interval(),
        "tau": _interval("3", "2"),
        "von_mangoldt": _interval(),
        "coefficient": _interval("1", "10"),
        "compressed_shift_norm_bound": _interval(),
        "complement_contribution": _interval("1", "10"),
    }


def _fixture() -> dict[str, Any]:
    dimension = 4
    matrix = _matrix(dimension)
    zero_matrix = _matrix(dimension, "0")
    return {
        "format": "rh-weil-certificate-v2",
        "claim": "p8-cross-layer-fixture",
        "claim_profile": "multi_prime_power_legendre_schur",
        "support_T": {"num": "2", "den": "3", "frac": "2/3"},
        "basis": {"type": "legendre", "dimension": dimension, "domain": "[-1, 1]"},
        "parity_sector": "both",
        "dimension": dimension,
        "constants": {"c_T": _interval("0"), "rho_R": _interval("0")},
        "arithmetic_terms": [_term(2), _term(3)],
        "matrix": matrix,
        "tail_bound": {
            "type": "multi_prime_power_legendre_component_gram_schur",
            "harmonic_index": dimension,
            "active_set_rule": "prime_powers_with_log_m_lt_2T",
            "complement_rule": "H_N-c_T-sum(c_m*b_m)-rho_R",
            "grouped_components": ["V", "P", "R"],
            "factor": {"num": "3", "den": "1"},
            "factor_claim": "C-0059",
        },
        "schur_proof": {
            "residual_order": 32,
            "GV": zero_matrix,
            "GP": copy.deepcopy(zero_matrix),
            "GR": copy.deepcopy(zero_matrix),
            "even_witness": _exact_identity(2),
            "odd_witness": _exact_identity(2),
        },
        "generator_metadata": {
            "generator": "p8-test",
            "script": "tests.test_v2_adversarial_consistency",
            "version": "1",
            "git_commit": "0" * 40,
            "git_dirty": False,
            "flint_version": "test",
            "python_flint_version": "test",
            "prec_bits": 128,
            "timestamp_utc": "2026-10-01T00:00:00Z",
        },
    }


def _mutate(case_id: str) -> dict[str, Any]:
    value = _fixture()
    if case_id == "valid_first_window_structure":
        return value
    if case_id == "missing_m3":
        value["arithmetic_terms"].pop()
    elif case_id == "duplicate_m3":
        value["arithmetic_terms"][0] = _term(3)
    elif case_id == "substituted_m3":
        value["arithmetic_terms"][1] = _term(5)
    elif case_id == "m4_in_first_window":
        value["arithmetic_terms"][1] = {
            **_term(4),
            "base_prime": 2,
            "exponent": 2,
        }
    elif case_id == "malformed_coefficient_interval":
        value["arithmetic_terms"][0]["coefficient"]["lo_den"] = "0"
    elif case_id == "malformed_norm_interval":
        value["arithmetic_terms"][0]["compressed_shift_norm_bound"] = _interval("2")
    elif case_id == "missing_gp":
        del value["schur_proof"]["GP"]
    elif case_id == "malformed_gp_interval":
        value["schur_proof"]["GP"]["entries"][0]["lo_den"] = "0"
    elif case_id == "wrong_factor":
        value["tail_bound"]["factor"]["num"] = "2"
    else:
        raise AssertionError(f"unknown P8 corpus case {case_id}")
    return value


def test_p8_cross_layer_corpus_python_schema_and_semantics_agree() -> None:
    corpus = json.loads(CROSS_LAYER_CORPUS.read_text(encoding="utf-8"))
    assert corpus["format"] == "rh-weil-certificate-v2-cross-layer-corpus-v1"
    assert corpus["purpose"] == "test-only"
    for case in corpus["cases"]:
        fixture = _mutate(case["id"])
        expected = bool(case["expected_valid"])
        schema_valid = certificate_v2_validator().is_valid(fixture)
        semantic_valid = validate_certificate_v2_structure(fixture)[0]
        assert schema_valid is expected, case
        assert semantic_valid is expected, case


def test_p8_first_window_thresholds_and_near_thresholds_fail_closed() -> None:
    valid = _fixture()
    assert validate_certificate_v2_structure(valid) == (True, "ok")

    lower_equal = _fixture()
    lower_equal["support_T"] = {"num": "1", "den": "2", "frac": "1/2"}
    lower_equal["arithmetic_terms"][0]["tau"] = _interval("2")
    lower_equal["arithmetic_terms"][1]["tau"] = _interval("2")
    ok, message = validate_certificate_v2_structure(lower_equal)
    assert not ok
    assert "strictly" in message

    lower_below = _fixture()
    lower_below["support_T"] = {"num": "499999", "den": "1000000", "frac": "499999/1000000"}
    ok, message = validate_certificate_v2_structure(lower_below)
    assert not ok
    assert "log(3)/2" in message or "tau" in message

    upper_equal = _fixture()
    upper_equal["support_T"] = {"num": "1", "den": "1", "frac": "1/1"}
    ok, message = validate_certificate_v2_structure(upper_equal)
    assert not ok
    assert "log(4)/2" in message or "tau" in message

    upper_above = _fixture()
    upper_above["support_T"] = {"num": "1000001", "den": "1000000", "frac": "1000001/1000000"}
    ok, message = validate_certificate_v2_structure(upper_above)
    assert not ok
    assert "log(4)/2" in message or "tau" in message


def test_p8_real_support_gates_are_strict_and_fail_closed_near_thresholds() -> None:
    require_one_prime_support(27, 50)
    with pytest.raises(ValueError, match="one-prime window"):
        require_one_prime_support(11, 20)

    assert multi_driver.require_two_prime_window(Fraction(3, 5)) == (2, 3)
    with pytest.raises(ValueError, match=r"log\(3\)/2 < T"):
        multi_driver.require_two_prime_window(Fraction(27, 50))
    with pytest.raises(ValueError, match=r"T < log\(4\)/2"):
        multi_driver.require_two_prime_window(Fraction(7, 10))

    lower_near = Fraction(549306144334054845697622618, 10**27)
    with pytest.raises(ValueError):
        multi_driver.require_two_prime_window(lower_near, prec=64)

    upper_near = Fraction(693147180559945309417232121, 10**27)
    with pytest.raises(ValueError):
        multi_driver.require_two_prime_window(upper_near, prec=64)


def test_p8_wrong_parity_fails_python_semantics() -> None:
    fixture = _fixture()
    fixture["schur_proof"]["GP"]["entries"][1]["lo_num"] = "1"
    fixture["schur_proof"]["GP"]["entries"][1]["hi_num"] = "1"
    fixture["schur_proof"]["GP"]["entries"][4]["lo_num"] = "1"
    fixture["schur_proof"]["GP"]["entries"][4]["hi_num"] = "1"
    assert certificate_v2_validator().is_valid(fixture)
    valid, message = validate_certificate_v2_structure(fixture)
    assert not valid
    assert "opposite-parity" in message


def test_p8_closed_grid_admission_consistency_is_empty_everywhere() -> None:
    corpus = json.loads(ADMISSION_CORPUS.read_text(encoding="utf-8"))
    assert set(corpus) == {"format", "purpose", "allowed", "forbidden"}
    assert corpus["format"] == "multi-prime-admission-corpus-v2"
    assert corpus["purpose"] == "test-only"
    assert corpus["allowed"] == []
    assert len(corpus["forbidden"]) == 16
    assert V2_ALLOWED_CONFIGURATIONS == frozenset()

    supports = {Fraction("3/5"), Fraction("5/8"), Fraction("13/20"), Fraction("2/3")}
    dimensions = {104, 112, 120, 128}
    expected = {(support, dimension) for support in supports for dimension in dimensions}
    observed = {
        (Fraction(case["support_T"]), int(case["dimension"]))
        for case in corpus["forbidden"]
    }
    assert observed == expected

    for support, dimension in observed:
        assert not is_allowed_v2_configuration(support, dimension)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    admission_validator = Draft202012Validator(schema["$defs"]["theoremAdmission"])
    for case in corpus["forbidden"]:
        assert not admission_validator.is_valid(case), case


def test_p8_production_code_does_not_load_test_only_v2_corpora() -> None:
    sentinels = {CROSS_LAYER_CORPUS.name, ADMISSION_CORPUS.name}
    production_files = list((ROOT / "scripts" / "cert").glob("*.py")) + list(
        (ROOT / "crates" / "rh_cert" / "src").glob("*.rs")
    )
    assert production_files
    for path in production_files:
        text = path.read_text(encoding="utf-8")
        for sentinel in sentinels:
            assert sentinel not in text, path
