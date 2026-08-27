from __future__ import annotations

import ast
from fractions import Fraction
from pathlib import Path

import pytest

from scripts import weil_continuation_driver as driver
from scripts import weil_support_candidate_check as candidate
from scripts.cert.exact_prime_schur_certificate import build_exact_prime_schur_certificate
from scripts.cert.exact_prime_schur_common import (
    make_witness,
    parity_block,
    schur_from_serialized_inputs,
)
from scripts.cert.matrices import RationalInterval, RationalIntervalMatrix


PRE_THEOREM_MODULES = (
    Path("scripts/weil_continuation_driver.py"),
    Path("scripts/weil_support_candidate_check.py"),
)
FORBIDDEN_IMPORTS = {
    "scripts.cert.exact_prime_schur_certificate",
    "scripts.cert.export_certificate",
    "subprocess",
}


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module)
        elif isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
    return modules


def test_pre_theorem_modules_cannot_import_theorem_admission_code() -> None:
    for path in PRE_THEOREM_MODULES:
        assert _imported_modules(path).isdisjoint(FORBIDDEN_IMPORTS), path


def test_p7_boundary_is_machine_readable_and_non_promoting() -> None:
    boundary = candidate.theorem_boundary_payload()

    assert boundary["theorem_status"] is False
    assert boundary["independently_verified"] is False
    assert boundary["whitelisted"] is False
    assert boundary["automatic_promotion"] is False
    assert boundary["promotion_requirements"] == [
        "explicit_closed_contract_admission",
        "retained_full_certificate_generation",
        "fresh_independent_rust_verifier_pass",
    ]
    assert {
        "emit_theorem_certificate",
        "edit_closed_contract_or_whitelist",
        "invoke_independent_rust_verifier",
        "grant_theorem_status",
    } == set(boundary["forbidden_automatic_actions"])
    assert all("THEOREM" not in state and "VERIFIED" not in state for state in driver.FINAL_STATES)


def test_continuation_cache_depends_on_neutral_candidate_primitives_not_exporter() -> None:
    assert "scripts/cert/exact_prime_schur_common.py" in driver.CACHE_SOURCE_PATHS
    assert "scripts/cert/exact_prime_schur_certificate.py" not in driver.CACHE_SOURCE_PATHS


def test_p6_shared_exact_construction_proves_simple_positive_blocks() -> None:
    zero = RationalInterval(0)
    a = RationalIntervalMatrix(
        [
            [RationalInterval(4), zero],
            [zero, RationalInterval(3)],
        ]
    )
    empty_gram = RationalIntervalMatrix([[zero, zero], [zero, zero]])

    schur, mu_lower = schur_from_serialized_inputs(
        a,
        empty_gram,
        empty_gram,
        empty_gram,
        zero,
        zero,
        zero,
        2,
    )
    even_witness, even_margin = make_witness(parity_block(schur, 0), 8)
    odd_witness, odd_margin = make_witness(parity_block(schur, 1), 8)

    assert mu_lower == Fraction(3, 2)
    assert even_margin > 0
    assert odd_margin > 0
    assert even_witness == [[Fraction(1)]]
    assert odd_witness == [[Fraction(1)]]


def test_p6_shared_exact_construction_rejects_nonsymmetric_inputs() -> None:
    nonsymmetric = RationalIntervalMatrix(
        [
            [RationalInterval(2), RationalInterval(1)],
            [RationalInterval(0), RationalInterval(2)],
        ]
    )
    zero = RationalInterval(0)
    empty_gram = RationalIntervalMatrix([[zero, zero], [zero, zero]])

    with pytest.raises(ValueError, match="symmetric"):
        schur_from_serialized_inputs(
            nonsymmetric,
            empty_gram,
            empty_gram,
            empty_gram,
            zero,
            zero,
            zero,
            2,
        )


def test_p7_closed_exporter_rejects_current_frontier_pair_before_assembly() -> None:
    with pytest.raises(ValueError, match="allows only"):
        build_exact_prime_schur_certificate(
            claim="frontier-must-remain-pre-theorem",
            support_num=19,
            support_den=40,
            dimension=64,
            prec=128,
        )
