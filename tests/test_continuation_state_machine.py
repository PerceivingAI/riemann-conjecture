from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from scripts import weil_continuation_driver as driver
from scripts.continuation_bundle import write_continuation_bundle


def _scout_result(dimensions: list[int], *, positive: bool = True) -> dict[str, object]:
    value = 1.0 if positive else -1.0
    return {
        "schur_rows": [
            {
                "N": dimension,
                "mu_scout": value,
                "finite_block_min_eigenvalue": value,
                "factor3_truncated_schur_min_eigenvalue": value,
            }
            for dimension in dimensions
        ]
    }


def _stable_rigorous(*args, **kwargs) -> dict[str, object]:
    return {
        "status": "precision_stable",
        "selected_precision_bits": 256,
        "attempts": [],
        "precision_pair_diagnostics": [],
    }


def _trace_states(result: dict[str, object]) -> list[str]:
    return [str(row["to"]) for row in result["workflow_trace"]]


def _patch_success_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values
        ),
    )
    monkeypatch.setattr(driver, "_escalate_rigorous_screen", _stable_rigorous)
    monkeypatch.setattr(
        driver,
        "_construct_candidate",
        lambda *args, **kwargs: {
            "status": "candidate_ready",
            "selected_matrix_bits": 80,
            "selected_witness_bits": 40,
            "attempts": [],
        },
    )


def test_p9_transition_graph_covers_every_workflow_state() -> None:
    assert set(driver.ALLOWED_WORKFLOW_TRANSITIONS) == set(driver.WorkflowState)
    assert driver.FINAL_STATES == {
        state.value for state in driver.TERMINAL_WORKFLOW_STATES
    }


def test_p9_machine_rejects_illegal_jump_and_terminal_reentry() -> None:
    machine = driver.ContinuationStateMachine()

    with pytest.raises(RuntimeError, match="VALIDATE_INPUT -> CANDIDATE_READY"):
        machine.transition(
            driver.WorkflowState.CANDIDATE_READY,
            reason="illegal_direct_promotion",
        )

    machine.transition(driver.WorkflowState.FLOAT_SCOUT, reason="valid")
    machine.transition(driver.WorkflowState.CHECK_SCOUT_STABILITY, reason="valid")
    machine.transition(driver.WorkflowState.NO_CANDIDATE, reason="valid")
    assert machine.require_terminal() is driver.WorkflowState.NO_CANDIDATE

    with pytest.raises(RuntimeError, match="NO_CANDIDATE -> FLOAT_SCOUT"):
        machine.transition(driver.WorkflowState.FLOAT_SCOUT, reason="illegal_reentry")


def test_p9_success_path_visits_every_required_stage(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_success_path(monkeypatch)

    result = driver.run_driver(Fraction(19, 40), [64, 68])

    assert result["state"] == "CANDIDATE_READY"
    assert result["workflow_state"] == "CANDIDATE_READY"
    assert _trace_states(result) == [
        "VALIDATE_INPUT",
        "FLOAT_SCOUT",
        "CHECK_SCOUT_STABILITY",
        "SELECT_DIMENSION",
        "RIGOROUS_PRECISION_SEARCH",
        "CHECK_RIGOROUS_STABILITY",
        "EXACT_ROUNDING_SEARCH",
        "EXACT_WITNESS_CHECK",
        "CANDIDATE_READY",
    ]


def test_p9_negative_scout_stops_before_rigorous_stage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=False
        ),
    )
    rigorous_calls: list[int] = []
    monkeypatch.setattr(
        driver,
        "_escalate_rigorous_screen",
        lambda support, dimension, precisions, residual_order, cache_dir=None: rigorous_calls.append(
            dimension
        ),
    )

    result = driver.run_driver(Fraction(19, 40), [48, 52])

    assert result["state"] == "NO_CANDIDATE"
    assert rigorous_calls == []
    assert _trace_states(result) == [
        "VALIDATE_INPUT",
        "FLOAT_SCOUT",
        "CHECK_SCOUT_STABILITY",
        "NO_CANDIDATE",
    ]


def test_p9_precision_exhaustion_has_explicit_terminal_transition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values
        ),
    )
    monkeypatch.setattr(
        driver,
        "_escalate_rigorous_screen",
        lambda *args, **kwargs: {
            "status": "precision_limit_reached",
            "selected_precision_bits": None,
            "attempts": [],
            "precision_pair_diagnostics": [],
        },
    )

    result = driver.run_driver(Fraction(19, 40), [64])

    assert result["state"] == "PRECISION_LIMIT_REACHED"
    assert _trace_states(result)[-3:] == [
        "RIGOROUS_PRECISION_SEARCH",
        "CHECK_RIGOROUS_STABILITY",
        "PRECISION_LIMIT_REACHED",
    ]
    assert "EXACT_ROUNDING_SEARCH" not in _trace_states(result)


def test_p9_witness_failure_cannot_skip_witness_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values
        ),
    )
    monkeypatch.setattr(driver, "_escalate_rigorous_screen", _stable_rigorous)
    monkeypatch.setattr(
        driver,
        "_construct_candidate",
        lambda *args, **kwargs: {
            "status": "witness_failed",
            "selected_matrix_bits": None,
            "selected_witness_bits": None,
            "attempts": [],
        },
    )

    result = driver.run_driver(Fraction(19, 40), [64])

    assert result["state"] == "WITNESS_FAILED"
    assert _trace_states(result)[-3:] == [
        "EXACT_ROUNDING_SEARCH",
        "EXACT_WITNESS_CHECK",
        "WITNESS_FAILED",
    ]
    assert "CANDIDATE_READY" not in _trace_states(result)


def test_p9_bundle_manifest_retains_state_trace(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _patch_success_path(monkeypatch)
    result = driver.run_driver(Fraction(19, 40), [64])
    output_dir = tmp_path / "bundle"

    write_continuation_bundle(
        result,
        output_dir,
        provenance={
            "git_commit": "a" * 40,
            "git_dirty": True,
            "python_version": "3.14.0",
            "python_implementation": "CPython",
            "python_flint_version": "0.9.0",
        },
    )
    manifest = json.loads(
        (output_dir / "run-manifest.json").read_text(encoding="utf-8")
    )

    assert manifest["workflow_state"] == "CANDIDATE_READY"
    assert manifest["workflow_trace"] == result["workflow_trace"]
