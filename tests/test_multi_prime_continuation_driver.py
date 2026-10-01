from __future__ import annotations

import json
import os
from concurrent.futures import Future
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import weil_multi_prime_continuation_driver as driver
from scripts.weil_multi_prime_support_continuation_scout import scout_support


class _RecordingRunStatus:
    def __init__(self) -> None:
        self.updates: list[dict[str, object]] = []
        self.events: list[dict[str, object]] = []

    def update(self, **kwargs) -> dict[str, object]:
        self.updates.append(dict(kwargs))
        return dict(kwargs)

    def event(self, event: str, **kwargs) -> dict[str, object]:
        row = {"event": event, **kwargs}
        self.events.append(row)
        return row


class _InlineExecutor:
    _processes: dict[object, object] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def submit(self, fn, *args, **kwargs):
        future: Future = Future()
        try:
            result = fn(*args, **kwargs)
        except BaseException as exc:
            future.set_exception(exc)
        else:
            future.set_result(result)
        return future


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


def _stable_candidate_confirmation(*args, **kwargs) -> dict[str, object]:
    return {
        "classification": "CANDIDATE_STABLE",
        "qualified": True,
        "selected_confirmation_precision_bits": 384,
        "attempts": [],
        "pair_diagnostics": [],
    }


def _candidate_attempt(
    precision: int,
    *,
    width: float,
    even_margin: str = "1/100",
    odd_margin: str = "1/200",
) -> dict[str, object]:
    scalar_width = "1/2048" if width < 1.0 else "1/1024"
    matrix_widths = {
        name: {
            "max_width": width,
            "max_radius": width / 2,
            "row": 0,
            "column": 0,
            "midpoint_at_widest_entry": 1.0,
        }
        for name in ("A", "GV", "GP", "GR")
    }
    exact_widths = {
        name: {
            "max_width": "1/1024",
            "max_radius": "1/2048",
            "row": 0,
            "column": 0,
            "midpoint_at_widest_entry": "1/1",
        }
        for name in ("A", "GV", "GP", "GR")
    }
    return {
        "precision_bits": precision,
        "mu_lower": "7/10",
        "even_gershgorin_margin": even_margin,
        "odd_gershgorin_margin": odd_margin,
        "all_margins_positive": True,
        "working_precision_diagnostics": {
            "matrix_widths": matrix_widths,
            "scalar_widths": {
                "mu": scalar_width,
                "rho_R": scalar_width,
                "residual_remainder": scalar_width,
            },
        },
        "exact_rounding_diagnostics": {
            "rounding_succeeded": True,
            "matrix_widths": exact_widths,
        },
    }


def _candidate_ready(base: dict[str, object]) -> dict[str, object]:
    return {
        "status": "candidate_ready",
        "selected_matrix_bits": 64,
        "selected_witness_bits": 32,
        "attempts": [base],
    }


def test_p5_strict_window_and_active_set_are_verified() -> None:
    assert driver.require_two_prime_window(Fraction(3, 5)) == (2, 3)

    with pytest.raises(ValueError, match=r"log\(3\)/2 < T"):
        driver.require_two_prime_window(Fraction(27, 50))
    with pytest.raises(ValueError, match=r"T < log\(4\)/2"):
        driver.require_two_prime_window(Fraction(7, 10))


def test_p5_active_set_check_is_independent_of_window_check(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "enumerate_active_prime_power_terms",
        lambda *args, **kwargs: (
            SimpleNamespace(m=2),
            SimpleNamespace(m=3),
            SimpleNamespace(m=4),
        ),
    )
    with pytest.raises(ValueError, match=r"exact active set \{2,3\}"):
        driver.require_two_prime_window(Fraction(3, 5))


def test_p5_rigorous_screen_uses_gp_and_certifies_active_terms() -> None:
    result = scout_support(
        Fraction(3, 5),
        dimension=8,
        prec=96,
        residual_order=8,
    )
    assert result["active_terms"] == [2, 3]
    assert "GP_max" in result["interval_widths"]
    assert "G2_max" not in result["interval_widths"]
    assert set(result["matrix_interval_diagnostics"]) == {"A", "GV", "GP", "GR"}


def test_p5_cache_recovers_from_corrupt_json_and_uses_atomic_publication(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(driver, "_cache_source_fingerprint", lambda: "p5-source")
    calls: list[int] = []

    def produce() -> dict[str, object]:
        calls.append(len(calls) + 1)
        return {"generation": calls[-1]}

    first, first_hit = driver._cached_result(tmp_path, {"kind": "p5-test"}, produce)
    cache_files = list(tmp_path.glob("*.json"))
    assert len(cache_files) == 1
    cache_files[0].write_text("{", encoding="utf-8")

    second, second_hit = driver._cached_result(tmp_path, {"kind": "p5-test"}, produce)

    assert first == {"generation": 1}
    assert second == {"generation": 2}
    assert (first_hit, second_hit) == (False, False)
    assert json.loads(cache_files[0].read_text(encoding="utf-8")) == {"generation": 2}
    assert not list(tmp_path.glob("*.tmp"))


def test_p5_cache_fingerprint_covers_multi_prime_semantics() -> None:
    required = {
        "scripts/weil_multi_prime_continuation_driver.py",
        "scripts/weil_multi_prime_schur_scout.py",
        "scripts/weil_multi_prime_support_continuation_scout.py",
        "scripts/weil_multi_prime_support_candidate_check.py",
        "scripts/cert/multi_prime_legendre_schur.py",
        "scripts/cert/prime_power_terms.py",
        "scripts/cert/exact_prime_schur_common.py",
        "scripts/cert/residual_kernel.py",
    }
    assert required.issubset(set(driver.CACHE_SOURCE_PATHS))
    assert "scripts/weil_continuation_driver.py" not in driver.CACHE_SOURCE_PATHS
    assert "scripts/weil_support_candidate_check.py" not in driver.CACHE_SOURCE_PATHS


def test_p5_candidate_confirmation_uses_higher_precision_with_gp(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    base = _candidate_attempt(256, width=1.0)
    candidate = _candidate_ready(base)
    calls: list[tuple[int, int, int]] = []

    def fake_run_candidate(
        support,
        *,
        dimension,
        prec,
        residual_order,
        matrix_bits,
        witness_bits,
        comparison_prec=None,
    ):
        calls.append((prec, matrix_bits, witness_bits))
        return _candidate_attempt(prec, width=0.5)

    monkeypatch.setattr(driver, "run_candidate", fake_run_candidate)

    result = driver._confirm_candidate_precision_stability(
        Fraction(3, 5),
        160,
        candidate,
        16,
        precision_step=128,
        extra_steps=1,
        cache_dir=None,
    )

    assert result["qualified"] is True
    assert result["classification"] == "CANDIDATE_STABLE"
    assert result["selected_confirmation_precision_bits"] == 384
    assert calls == [(384, 64, 32)]
    assert result["pair_diagnostics"][0]["working_matrix_widths_reduced"] is True


def test_p5_fallback_candidate_becomes_selected_dimension(
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
        lambda support, dimension, precisions, residual_order, cache_dir=None: (
            {
                "status": "precision_limit_reached",
                "selected_precision_bits": None,
                "attempts": [],
                "precision_pair_diagnostics": [],
            }
            if dimension == 160
            else {
                "status": "precision_stable",
                "selected_precision_bits": 256,
                "attempts": [],
                "precision_pair_diagnostics": [],
            }
        ),
    )
    monkeypatch.setattr(
        driver,
        "_construct_candidate",
        lambda *args, **kwargs: {
            "status": "candidate_ready",
            "selected_matrix_bits": 64,
            "selected_witness_bits": 32,
            "attempts": [],
        },
    )
    monkeypatch.setattr(
        driver,
        "_confirm_candidate_precision_stability",
        _stable_candidate_confirmation,
    )

    result = driver.run_driver(
        Fraction(3, 5),
        [160, 176],
        scout_resolution_count=3,
        scout_workers=1,
        rigorous_workers=1,
    )

    assert result["state"] == "CANDIDATE_READY"
    assert result["active_terms"] == [2, 3]
    assert result["scout_primary_dimension"] == 160
    assert result["fallback_dimensions"] == [176]
    assert result["selected_candidate_dimension"] == 176
    assert result["theorem_status"] is False
    assert result["independently_verified"] is False


def test_p5_parallel_observation_order_is_separate_from_bundle_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    status = _RecordingRunStatus()
    monkeypatch.setattr(driver, "_spawn_process_pool", lambda workers: _InlineExecutor())
    monkeypatch.setattr(driver, "as_completed", lambda futures: iter(reversed(list(futures))))
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
        lambda support, dimension, precisions, residual_order, cache_dir=None: {
            "status": "precision_stable",
            "selected_precision_bits": 256,
            "attempts": [],
            "precision_pair_diagnostics": [],
        },
    )
    monkeypatch.setattr(
        driver,
        "_construct_candidate",
        lambda *args, **kwargs: {
            "status": "candidate_ready",
            "selected_matrix_bits": 64,
            "selected_witness_bits": 32,
            "attempts": [],
        },
    )
    monkeypatch.setattr(
        driver,
        "_confirm_candidate_precision_stability",
        _stable_candidate_confirmation,
    )

    result = driver.run_driver(
        Fraction(3, 5),
        [176, 160, 192],
        scout_resolution_count=3,
        scout_workers=3,
        rigorous_workers=2,
        run_status=status,
    )

    scout_completion = [
        int(row["level"])
        for row in status.events
        if row["event"] == "SCOUT_RESOLUTION_COMPLETED"
    ]
    rigorous_completion = [
        int(row["dimension"])
        for row in status.events
        if row["event"] == "RIGOROUS_DIMENSION_COMPLETED"
    ]

    assert scout_completion == [2, 1, 0]
    assert rigorous_completion == [176, 160]
    assert [row["resolution"]["level"] for row in result["scout_runs"]] == [0, 1, 2]
    assert [row["dimension"] for row in result["rigorous_screening"]] == [160, 176]
    assert result["selected_candidate_dimension"] == 160


def test_p5_precision_exhaustion_is_fail_closed_terminal_state(
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

    result = driver.run_driver(
        Fraction(3, 5),
        [160, 176],
        scout_resolution_count=3,
    )

    assert result["state"] == "PRECISION_LIMIT_REACHED"
    assert result["state"] in driver.FINAL_STATES
    assert result["selected_candidate_dimension"] is None


def test_p5_verified_process_pool_reaps_spawned_workers() -> None:
    verifier = driver.WorkerCleanupVerifier()
    with driver._verified_process_pool(
        2,
        stage="P5_TEST_POOL",
        verifier=verifier,
    ) as executor:
        worker_pids = {executor.submit(os.getpid).result() for _ in range(2)}
        assert worker_pids

    report = verifier.verify()
    assert report["verified"] is True
    assert report["executors_shutdown"] == 1
    assert int(report["worker_processes_reaped"]) >= 1
    assert report["stages"] == ["P5_TEST_POOL"]
    assert report["active_children_after_cleanup"] == 0


def test_p5_driver_has_no_historical_one_prime_hook_imports() -> None:
    source = Path(driver.__file__).read_text(encoding="utf-8")
    forbidden = (
        "from scripts.weil_continuation_driver",
        "from scripts.weil_legendre_schur_scout",
        "from scripts.weil_support_continuation_scout",
        "from scripts.weil_support_candidate_check",
        "require_one_prime_support",
        '"G2_max"',
    )
    assert all(token not in source for token in forbidden)
