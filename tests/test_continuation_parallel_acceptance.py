from __future__ import annotations

from fractions import Fraction

import pytest

from scripts import weil_continuation_driver as driver


pytestmark = [pytest.mark.integration, pytest.mark.parallel_acceptance]


def _reconnaissance_classification(result: dict[str, object], dimension: int) -> str:
    rows = result["reconnaissance"]
    assert isinstance(rows, list)
    row = next(item for item in rows if item["dimension"] == dimension)
    return str(row["classification"])


def _rigorous_row(result: dict[str, object], dimension: int) -> dict[str, object]:
    rows = result["rigorous_screening"]
    assert isinstance(rows, list)
    return next(item for item in rows if item["dimension"] == dimension)


def _assert_pre_theorem(result: dict[str, object]) -> None:
    assert result["theorem_status"] is False
    assert result["independently_verified"] is False
    assert result["whitelisted"] is False


def test_parallel_replays_two_fifths_n40_history() -> None:
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
        scout_workers=3,
        rigorous_workers=2,
        cache_dir=None,
    )

    assert _reconnaissance_classification(result, 32) == "negative"
    assert _reconnaissance_classification(result, 40) == "stable_positive"
    assert result["scout_primary_dimension"] == 40
    rigorous = _rigorous_row(result, 40)
    assert rigorous["status"] == "precision_stable"
    assert rigorous["selected_precision_bits"] == 384
    assert result["state"] == "CANDIDATE_READY"
    assert result["selected_candidate_dimension"] == 40
    _assert_pre_theorem(result)


def test_parallel_replays_seventeen_fortieths_n48_history() -> None:
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
        scout_workers=3,
        rigorous_workers=2,
        cache_dir=None,
    )

    assert _reconnaissance_classification(result, 40) == "negative"
    assert _reconnaissance_classification(result, 48) == "stable_positive"
    assert result["scout_primary_dimension"] == 48
    rigorous = _rigorous_row(result, 48)
    assert rigorous["status"] == "precision_stable"
    assert rigorous["selected_precision_bits"] == 384
    assert result["state"] == "CANDIDATE_READY"
    assert result["selected_candidate_dimension"] == 48
    _assert_pre_theorem(result)


def test_parallel_replays_nineteen_fortieths_primary_negative_fallback_positive() -> None:
    result = driver.run_driver(
        Fraction(19, 40),
        [64, 68],
        scout_resolution_count=3,
        precision_start=256,
        precision_max=512,
        residual_order=32,
        matrix_bits_start=64,
        matrix_bits_max=64,
        witness_bits_start=32,
        witness_bits_max=32,
        scout_workers=3,
        rigorous_workers=2,
        cache_dir=None,
    )

    assert _reconnaissance_classification(result, 64) == "stable_positive"
    assert _reconnaissance_classification(result, 68) == "stable_positive"
    assert result["scout_primary_dimension"] == 64
    assert result["fallback_dimensions"] == [68]
    assert [row["dimension"] for row in result["rigorous_screening"]] == [64, 68]

    primary = _rigorous_row(result, 64)
    assert primary["status"] == "mathematical_negative"
    assert primary["precision_status"] == driver.PRECISION_STATUS_MATHEMATICAL_NEGATIVE

    fallback = _rigorous_row(result, 68)
    assert fallback["status"] == "precision_stable"
    assert fallback["selected_precision_bits"] == 384

    assert result["state"] == "CANDIDATE_READY"
    assert result["selected_candidate_dimension"] == 68
    _assert_pre_theorem(result)
