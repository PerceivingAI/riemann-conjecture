"""Cross-layer admission consistency for the closed exact-prime theorem profile.

The corpus is test-only. Production Python, schema, and Rust implementations
remain independently hard-coded and must never load the corpus at runtime.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from scripts.cert.exact_prime_schur_certificate import ALLOWED_CONFIGURATIONS
from scripts.cert.export_certificate import (
    _certificate_validator,
    _is_allowed_exact_prime_configuration,
)


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "tests" / "data" / "exact-prime-admission-v1.json"


def _load_corpus() -> dict[str, Any]:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def _pair(case: dict[str, Any]) -> tuple[Fraction, int]:
    return Fraction(case["support_T"]), case["dimension"]


def _point_interval(value: str = "0") -> dict[str, str]:
    return {"lo_num": value, "lo_den": "1", "hi_num": value, "hi_den": "1"}


def _schema_fixture(support_t: str, dimension: int) -> dict[str, Any]:
    support = Fraction(support_t)
    matrix = {
        "dimension": 1,
        "entries": [
            {"row": 0, "col": 0, "lo_num": "1", "lo_den": "1", "hi_num": "1", "hi_den": "1"}
        ],
    }
    exact_matrix = {
        "dimension": 1,
        "entries": [{"row": 0, "col": 0, "num": "1", "den": "1"}],
    }
    return {
        "format": "rh-weil-certificate-v1",
        "claim": "admission-corpus-schema-fixture",
        "claim_profile": "exact_prime_legendre_schur",
        "support_T": {
            "num": str(support.numerator),
            "den": str(support.denominator),
            "frac": support_t,
        },
        "basis": {"type": "legendre", "dimension": dimension, "domain": "[-1, 1]"},
        "parity_sector": "both",
        "dimension": dimension,
        "constants": {"c2": _point_interval(), "c_T": _point_interval(), "rho_R": _point_interval()},
        "matrix": matrix,
        "tail_bound": {
            "type": "legendre_component_gram_schur",
            "harmonic_index": dimension,
            "factor": {"num": "3", "den": "1"},
        },
        "schur_proof": {
            "residual_order": 32,
            "GV": matrix,
            "G2": matrix,
            "GR": matrix,
            "even_witness": exact_matrix,
            "odd_witness": exact_matrix,
        },
        "generator_metadata": {
            "generator": "admission-corpus-test",
            "script": "tests.test_admission_consistency",
            "version": "1",
            "git_commit": "0000000000000000000000000000000000000000",
            "git_dirty": False,
            "flint_version": "test",
            "python_flint_version": "test",
            "prec_bits": 128,
            "timestamp_utc": "2026-08-27T00:00:00Z",
        },
    }


def test_admission_corpus_is_closed_and_complete_for_current_pair_grid() -> None:
    corpus = _load_corpus()
    assert set(corpus) == {"format", "purpose", "allowed", "forbidden"}
    assert corpus["format"] == "exact-prime-admission-corpus-v1"
    assert corpus["purpose"] == "test-only"

    allowed = {_pair(case) for case in corpus["allowed"]}
    forbidden = {_pair(case) for case in corpus["forbidden"]}
    assert len(allowed) == 7
    assert len(forbidden) == 49
    assert allowed.isdisjoint(forbidden)

    supports = {
        Fraction("7/20"),
        Fraction("2/5"),
        Fraction("17/40"),
        Fraction("9/20"),
        Fraction("19/40"),
        Fraction("1/2"),
        Fraction("21/40"),
    }
    dimensions = {32, 40, 48, 56, 68, 80, 96}
    expected_cross_forbidden = {(support, dimension) for support in supports for dimension in dimensions} - allowed
    assert expected_cross_forbidden <= forbidden
    assert (Fraction("19/40"), 64) in forbidden
    assert (Fraction("19/40"), 72) in forbidden
    assert (Fraction("1/2"), 76) in forbidden
    assert (Fraction("21/40"), 92) in forbidden
    assert (Fraction("21/40"), 100) in forbidden


def test_python_generator_admission_matches_test_corpus() -> None:
    corpus = _load_corpus()
    for case in corpus["allowed"]:
        assert _pair(case) in ALLOWED_CONFIGURATIONS, case
    for case in corpus["forbidden"]:
        assert _pair(case) not in ALLOWED_CONFIGURATIONS, case


def test_python_semantic_validator_admission_matches_test_corpus() -> None:
    corpus = _load_corpus()
    for case in corpus["allowed"]:
        support, dimension = _pair(case)
        assert _is_allowed_exact_prime_configuration(support, dimension), case
    for case in corpus["forbidden"]:
        support, dimension = _pair(case)
        assert not _is_allowed_exact_prime_configuration(support, dimension), case


def test_json_schema_admission_matches_test_corpus() -> None:
    corpus = _load_corpus()
    validator = _certificate_validator()
    for case in corpus["allowed"]:
        fixture = _schema_fixture(case["support_T"], case["dimension"])
        assert validator.is_valid(fixture), case
    for case in corpus["forbidden"]:
        fixture = _schema_fixture(case["support_T"], case["dimension"])
        assert not validator.is_valid(fixture), case


def test_authoritative_contract_document_names_every_allowed_pair() -> None:
    corpus = _load_corpus()
    contracts = (ROOT / "docs" / "CONTRACTS.md").read_text(encoding="utf-8")
    for case in corpus["allowed"]:
        assert f"T={case['support_T']},N={case['dimension']}" in contracts
    assert "No other `(T,N)` pair is admitted." in contracts


def test_production_code_does_not_load_test_only_admission_corpus() -> None:
    sentinel = CORPUS_PATH.name
    production_files = list((ROOT / "scripts" / "cert").glob("*.py")) + list(
        (ROOT / "crates" / "rh_cert" / "src").glob("*.rs")
    )
    assert production_files
    for path in production_files:
        assert sentinel not in path.read_text(encoding="utf-8"), path
