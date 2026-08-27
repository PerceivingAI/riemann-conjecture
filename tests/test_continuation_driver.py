from fractions import Fraction

import pytest

from scripts import weil_continuation_driver as driver


def _scout_result(dimensions: list[int], *, positive: bool) -> dict[str, object]:
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


def _rigorous_result(*, positive: bool) -> dict[str, object]:
    value = 1.0 if positive else -1.0
    return {
        "mu_lower": value,
        "finite_block_min_eigenvalue_midpoint": value,
        "schur_min_eigenvalue_midpoint": value,
        "interval_widths": {
            "A_max": 1.0,
            "GV_max": 1.0,
            "G2_max": 1.0,
            "GR_max": 1.0,
            "mu": 1.0,
            "rho_R": 1.0,
            "residual_remainder": 1.0,
        },
    }


def test_parse_dimensions_requires_positive_unique_explicit_values() -> None:
    assert driver.parse_dimensions("48, 52,56") == [48, 52, 56]
    with pytest.raises(ValueError, match="unique"):
        driver.parse_dimensions("48,48")
    with pytest.raises(ValueError, match="positive"):
        driver.parse_dimensions("0")


def test_scout_resolution_plan_increases_with_requested_maximum() -> None:
    plan = driver.build_scout_resolutions([48, 80])

    assert len(plan) == 3
    assert [item.max_mode for item in plan] == sorted(item.max_mode for item in plan)
    assert [item.quadrature_order for item in plan] == sorted(
        item.quadrature_order for item in plan
    )
    assert plan[-1].max_mode > 80


def test_precision_ladder_is_bounded_and_increasing() -> None:
    assert driver.build_precision_ladder(128, 512) == [128, 256, 384, 512]
    assert driver.build_precision_ladder(300, 640) == [300, 384, 512, 640]


def test_precision_pair_diagnostics_track_widths_changes_and_signs() -> None:
    previous = {
        "precision_bits": 256,
        "finite_block_min_eigenvalue_midpoint": 0.1,
        "schur_min_eigenvalue_midpoint": 0.02,
        "mu_lower": 0.7,
        "interval_widths": {
            "A_max": 2.0,
            "GV_max": 2.0,
            "G2_max": 2.0,
            "GR_max": 2.0,
            "mu": 2.0,
            "rho_R": 2.0,
            "residual_remainder": 2.0,
        },
    }
    current = {
        **previous,
        "precision_bits": 384,
        "finite_block_min_eigenvalue_midpoint": 0.1001,
        "schur_min_eigenvalue_midpoint": 0.0201,
        "interval_widths": {
            name: 1.0 for name in previous["interval_widths"]
        },
    }

    diagnostics = driver._precision_pair_diagnostics(previous, current)

    assert diagnostics["from_precision_bits"] == 256
    assert diagnostics["to_precision_bits"] == 384
    assert diagnostics["widths_reduced"] is True
    assert diagnostics["all_key_signs_stable"] is True


def test_precision_escalation_reports_limit_without_false_candidate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout_support",
        lambda support, *, dimension, prec, residual_order: {
            **_rigorous_result(positive=True),
            "schur_min_eigenvalue_midpoint": float(prec),
        },
    )

    result = driver._escalate_rigorous_screen(
        Fraction(19, 40), 64, [128, 256, 384], 32
    )

    assert result["status"] == "precision_limit_reached"
    assert result["selected_precision_bits"] is None
    assert len(result["attempts"]) == 3


def test_precision_stability_requires_sign_and_width_stability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    width_names = (
        "A_max",
        "GV_max",
        "G2_max",
        "GR_max",
        "mu",
        "rho_R",
        "residual_remainder",
    )

    def fake_screen(support, *, dimension, prec, residual_order):
        return {
            "mu_lower": -1.0 if prec == 128 else 1.0,
            "finite_block_min_eigenvalue_midpoint": -1.0 if prec == 128 else 1.0,
            "schur_min_eigenvalue_midpoint": 0.1 if prec == 128 else 0.10001,
            "interval_widths": {
                name: 2.0 if prec == 128 else 3.0 for name in width_names
            },
        }

    monkeypatch.setattr(driver, "scout_support", fake_screen)
    result = driver._escalate_rigorous_screen(
        Fraction(19, 40), 64, [128, 256], 32
    )

    assert result["status"] == "precision_limit_reached"
    diagnostics = result["precision_pair_diagnostics"][-1]
    assert diagnostics["all_key_signs_stable"] is False
    assert diagnostics["widths_reduced"] is False


def test_candidate_construction_escalates_rounding_and_witness_bits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[int, int]] = []

    def fake_candidate(
        support, *, dimension, prec, residual_order, matrix_bits, witness_bits
    ):
        calls.append((matrix_bits, witness_bits))
        return {
            "all_margins_positive": matrix_bits >= 80 and witness_bits >= 40,
        }

    monkeypatch.setattr(driver, "run_candidate", fake_candidate)
    result = driver._construct_candidate(
        Fraction(19, 40),
        64,
        384,
        32,
        [64, 80],
        [32, 40],
        None,
    )

    assert result["status"] == "candidate_ready"
    assert result["selected_matrix_bits"] == 80
    assert result["selected_witness_bits"] == 40
    assert calls == [(64, 32), (64, 40), (80, 32), (80, 40)]


def test_candidate_failure_stage_is_structured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "run_candidate",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            driver.CandidateStageError("rounding", "serialized complement lost positivity")
        ),
    )
    rounding = driver._construct_candidate(
        Fraction(19, 40), 64, 384, 32, [64], [32], None
    )
    assert rounding["status"] == "rounding_failed"
    assert rounding["attempts"][0]["failure_stage"] == "rounding"

    monkeypatch.setattr(
        driver,
        "run_candidate",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            driver.CandidateStageError("witness", "witness margin is not positive")
        ),
    )
    witness = driver._construct_candidate(
        Fraction(19, 40), 64, 384, 32, [64], [32], None
    )
    assert witness["status"] == "witness_failed"
    assert witness["attempts"][0]["failure_stage"] == "witness"


def test_cache_key_changes_with_source_fingerprint(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    calls: list[str] = []
    fingerprint = {"value": "source-a"}
    monkeypatch.setattr(
        driver, "_cache_source_fingerprint", lambda: fingerprint["value"]
    )

    def produce() -> dict[str, object]:
        calls.append(fingerprint["value"])
        return {"source": fingerprint["value"]}

    first, first_hit = driver._cached_result(tmp_path, {"kind": "test"}, produce)
    second, second_hit = driver._cached_result(tmp_path, {"kind": "test"}, produce)
    fingerprint["value"] = "source-b"
    third, third_hit = driver._cached_result(tmp_path, {"kind": "test"}, produce)

    assert first == second == {"source": "source-a"}
    assert third == {"source": "source-b"}
    assert (first_hit, second_hit, third_hit) == (False, True, False)
    assert calls == ["source-a", "source-b"]


def test_unexpected_candidate_check_failure_has_distinct_final_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    monkeypatch.setattr(
        driver,
        "_escalate_rigorous_screen",
        lambda *args, **kwargs: {
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
            "status": "candidate_check_failed",
            "selected_matrix_bits": None,
            "selected_witness_bits": None,
            "attempts": [],
        },
    )

    result = driver.run_driver(Fraction(19, 40), [48])

    assert result["state"] == "CANDIDATE_CHECK_FAILED"
    assert result["selected_candidate_dimension"] is None


def test_cache_fingerprint_covers_candidate_semantics_dependencies() -> None:
    required = {
        "scripts/cert/exact_prime_schur_certificate.py",
        "scripts/cert/residual_kernel.py",
        "scripts/cert/matrices.py",
    }
    assert required.issubset(set(driver.CACHE_SOURCE_PATHS))


def test_reconnaissance_requires_sign_stability_and_convergence() -> None:
    stable = [
        driver.ScoutDimensionResult(64, 1.0, 0.5, value, 120, 700, 350, "")
        for value in (0.0100, 0.010005, 0.010002)
    ]
    unstable = [
        driver.ScoutDimensionResult(64, 1.0, 0.5, value, 120, 700, 350, "")
        for value in (0.010, -0.002, 0.010)
    ]

    assert driver._classify_reconnaissance(stable) == "stable_positive"
    assert driver._classify_reconnaissance(unstable) == "unstable"

def test_driver_rejects_invalid_programmatic_inputs() -> None:
    with pytest.raises(ValueError, match="one-prime window"):
        driver.run_driver(Fraction(3, 5), [48])
    with pytest.raises(ValueError, match="positive"):
        driver.run_driver(Fraction(19, 40), [0])
    with pytest.raises(ValueError, match="unique"):
        driver.run_driver(Fraction(19, 40), [48, 48])
    with pytest.raises(ValueError, match="matrix_bits_start"):
        driver.run_driver(Fraction(19, 40), [48], matrix_bits_start=8)
    with pytest.raises(ValueError, match="witness_bits_start"):
        driver.run_driver(Fraction(19, 40), [48], witness_bits_start=4)
    with pytest.raises(ValueError, match="matrix_bits"):
        driver.run_candidate(
            Fraction(19, 40),
            dimension=64,
            prec=128,
            residual_order=32,
            matrix_bits=8,
            witness_bits=32,
        )


def test_driver_propagates_precision_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
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

    result = driver.run_driver(Fraction(19, 40), [48, 52])

    assert result["state"] == "PRECISION_LIMIT_REACHED"
    assert result["selected_dimension"] is None


def test_fallback_candidate_becomes_selected_dimension(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
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
            if dimension == 48
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

    result = driver.run_driver(Fraction(19, 40), [48, 52])

    assert result["state"] == "CANDIDATE_READY"
    assert result["scout_primary_dimension"] == 48
    assert result["selected_dimension"] == 52
    assert result["selected_candidate_dimension"] == 52


def test_cli_writes_requested_output_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    output_dir = tmp_path / "continuation"
    monkeypatch.setattr(
        driver,
        "run_driver",
        lambda support, dimensions, **kwargs: {
            "state": "NO_CANDIDATE",
            "support": str(support),
            "dimensions": dimensions,
        },
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "weil_continuation_driver",
            "--support",
            "19/40",
            "--n",
            "48",
            "--output-dir",
            str(output_dir),
        ],
    )

    driver.main()

    payload = (output_dir / "continuation.json").read_text(encoding="utf-8")
    assert '"state": "NO_CANDIDATE"' in payload


def test_driver_selects_smallest_ready_dimension_without_contract_admission(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    monkeypatch.setattr(
        driver,
        "scout_support",
        lambda support, *, dimension, prec, residual_order: _rigorous_result(
            positive=dimension != 52
        ),
    )
    monkeypatch.setattr(
        driver,
        "run_candidate",
        lambda support, *, dimension, prec, residual_order, matrix_bits, witness_bits: {
            "all_margins_positive": dimension != 52,
            "dimension": dimension,
        },
    )

    result = driver.run_driver(Fraction(19, 40), [52, 48, 56])

    assert result["state"] == "CANDIDATE_READY"
    assert result["scout_primary_dimension"] == 48
    assert result["selected_dimension"] == 48
    assert result["selected_candidate_dimension"] == 48
    assert result["theorem_status"] == "not_a_theorem"
    assert result["residual_order"] == 32
    assert result["dimensions"] == [52, 48, 56]
    assert result["fallback_dimensions"] == [52]
    assert [row["dimension"] for row in result["rigorous_screening"]] == [48, 52]


def test_driver_does_not_extrapolate_or_run_candidate_for_negative_scout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=False
        ),
    )
    candidate_calls: list[int] = []
    monkeypatch.setattr(
        driver,
        "run_candidate",
        lambda support, *, dimension, prec, residual_order, matrix_bits, witness_bits: candidate_calls.append(dimension),
    )

    result = driver.run_driver(Fraction(19, 40), [48, 52])

    assert result["state"] == "NO_CANDIDATE"
    assert result["selected_dimension"] is None
    assert candidate_calls == []
