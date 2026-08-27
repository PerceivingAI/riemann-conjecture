from __future__ import annotations

from fractions import Fraction

import pytest

from scripts import weil_continuation_driver as driver


pytestmark = pytest.mark.integration


def _reconnaissance_classification(result: dict[str, object], dimension: int) -> str:
    rows = result["reconnaissance"]
    assert isinstance(rows, list)
    row = next(item for item in rows if item["dimension"] == dimension)
    return str(row["classification"])


def _rigorous_row(result: dict[str, object], dimension: int) -> dict[str, object]:
    rows = result["rigorous_screening"]
    assert isinstance(rows, list)
    return next(item for item in rows if item["dimension"] == dimension)


def test_p11_rediscovers_two_fifths_n40_history() -> None:
    """Real pipeline replay of X-20260826-001, stopping before theorem admission."""
    result = driver.run_driver(
        Fraction(2, 5),
        [32, 40],
        scout_resolution_count=3,
        precision_start=256,
        precision_max=384,
        residual_order=32,
        matrix_bits_start=72,
        matrix_bits_max=72,
        witness_bits_start=40,
        witness_bits_max=40,
        cache_dir=None,
    )

    assert _reconnaissance_classification(result, 32) == "negative"
    assert _reconnaissance_classification(result, 40) == "stable_positive"
    assert result["scout_primary_dimension"] == 40

    rigorous = _rigorous_row(result, 40)
    assert rigorous["status"] == "precision_stable"
    assert rigorous["selected_precision_bits"] == 384
    assert [attempt["precision_bits"] for attempt in rigorous["attempts"]] == [256, 384]

    assert result["state"] == "CANDIDATE_READY"
    assert result["selected_candidate_dimension"] == 40
    candidate = next(item for item in result["candidates"] if item["dimension"] == 40)
    assert candidate["selected_matrix_bits"] == 72
    assert candidate["selected_witness_bits"] == 40

    assert result["theorem_status"] is False
    assert result["independently_verified"] is False
    assert result["whitelisted"] is False


def test_p11_rediscovers_seventeen_fortieths_n48_history() -> None:
    """Real pipeline replay of X-20260826-002, stopping before theorem admission."""
    result = driver.run_driver(
        Fraction(17, 40),
        [40, 48],
        scout_resolution_count=3,
        precision_start=256,
        precision_max=384,
        residual_order=32,
        matrix_bits_start=88,
        matrix_bits_max=88,
        witness_bits_start=48,
        witness_bits_max=48,
        cache_dir=None,
    )

    assert _reconnaissance_classification(result, 40) == "negative"
    assert _reconnaissance_classification(result, 48) == "stable_positive"
    assert result["scout_primary_dimension"] == 48

    rigorous = _rigorous_row(result, 48)
    assert rigorous["status"] == "precision_stable"
    assert rigorous["selected_precision_bits"] == 384
    assert [attempt["precision_bits"] for attempt in rigorous["attempts"]] == [256, 384]

    assert result["state"] == "CANDIDATE_READY"
    assert result["selected_candidate_dimension"] == 48
    candidate = next(item for item in result["candidates"] if item["dimension"] == 48)
    assert candidate["selected_matrix_bits"] == 88
    assert candidate["selected_witness_bits"] == 48

    assert result["theorem_status"] is False
    assert result["independently_verified"] is False
    assert result["whitelisted"] is False
