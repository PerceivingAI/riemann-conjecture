import argparse
import ast
from fractions import Fraction
from pathlib import Path

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


def test_p10_exact_support_parsing_is_rational_and_fail_closed() -> None:
    assert driver.parse_support("19/40") == Fraction(19, 40)
    assert driver.parse_support(" 0.475 ") == Fraction(19, 40)

    for invalid in ("", "0", "-1/2", "not-a-rational", "1/0"):
        with pytest.raises(ValueError):
            driver.parse_support(invalid)


def test_p10_dimension_range_validation() -> None:
    valid = argparse.Namespace(n=None, n_min=48, n_max=56, n_step=4)
    assert driver.dimensions_from_args(valid) == [48, 52, 56]

    invalid_ranges = (
        argparse.Namespace(n=None, n_min=48, n_max=None, n_step=4),
        argparse.Namespace(n=None, n_min=56, n_max=48, n_step=4),
        argparse.Namespace(n=None, n_min=48, n_max=56, n_step=0),
        argparse.Namespace(n="48", n_min=48, n_max=56, n_step=4),
    )
    for args in invalid_ranges:
        with pytest.raises(ValueError):
            driver.dimensions_from_args(args)


def test_p10_invalid_one_prime_support_is_rejected_before_any_stage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scout_calls: list[Fraction] = []
    monkeypatch.setattr(
        driver,
        "scout",
        lambda **kwargs: scout_calls.append(kwargs["support"]),
    )

    with pytest.raises(ValueError, match="one-prime window"):
        driver.run_driver(Fraction(3, 5), [48])

    assert scout_calls == []


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
        "scripts/cert/exact_prime_schur_common.py",
        "scripts/cert/residual_kernel.py",
        "scripts/cert/matrices.py",
    }
    assert required.issubset(set(driver.CACHE_SOURCE_PATHS))
    assert "scripts/cert/exact_prime_schur_certificate.py" not in driver.CACHE_SOURCE_PATHS


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

    summary = (output_dir / "summary.json").read_text(encoding="utf-8")
    manifest = (output_dir / "run-manifest.json").read_text(encoding="utf-8")
    assert '"state": "NO_CANDIDATE"' in summary
    assert '"final_state": "NO_CANDIDATE"' in manifest


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
    assert result["status"] == "CANDIDATE_READY"
    assert result["theorem_status"] is False
    assert result["independently_verified"] is False
    assert result["whitelisted"] is False
    assert result["residual_order"] == 32
    assert result["dimensions"] == [52, 48, 56]
    assert result["fallback_dimensions"] == [52]
    assert [row["dimension"] for row in result["rigorous_screening"]] == [48, 52]


def test_p10_stable_positive_selection_chooses_smallest_eligible_dimension(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        driver,
        "scout",
        lambda *, max_mode, quadrature_order, shift_order, n_values, support: _scout_result(
            n_values, positive=True
        ),
    )
    screened: list[int] = []

    def fake_rigorous(support, dimension, precisions, residual_order, cache_dir=None):
        screened.append(dimension)
        return {
            "status": "precision_stable",
            "selected_precision_bits": 256,
            "attempts": [],
            "precision_pair_diagnostics": [],
        }

    monkeypatch.setattr(driver, "_escalate_rigorous_screen", fake_rigorous)
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

    result = driver.run_driver(Fraction(19, 40), [72, 64, 68])

    assert result["scout_primary_dimension"] == 64
    assert result["selected_candidate_dimension"] == 64
    assert screened == [64, 68]


def test_p10_unstable_signs_are_rejected_without_rigorous_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {"scout": 0, "rigorous": 0}

    def fake_scout(*, max_mode, quadrature_order, shift_order, n_values, support):
        calls["scout"] += 1
        return _scout_result(n_values, positive=calls["scout"] != 2)

    monkeypatch.setattr(driver, "scout", fake_scout)
    monkeypatch.setattr(
        driver,
        "_escalate_rigorous_screen",
        lambda *args, **kwargs: calls.__setitem__("rigorous", calls["rigorous"] + 1),
    )

    result = driver.run_driver(Fraction(19, 40), [64])

    assert result["state"] == "SCOUT_UNSTABLE"
    assert calls["rigorous"] == 0


def test_p10_no_rigorous_positive_candidate_returns_no_candidate(
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
            "status": "mathematical_negative",
            "selected_precision_bits": None,
            "attempts": [],
            "precision_pair_diagnostics": [],
        },
    )

    result = driver.run_driver(Fraction(19, 40), [64])

    assert result["state"] == "NO_CANDIDATE"
    assert result["candidates"] == []


def test_p10_precision_escalation_stops_at_first_stable_precision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []
    widths = (4.0, 2.0, 1.0, 0.5)
    schur = (0.01, 0.0101, 0.0101005, 0.0101006)

    def fake_screen(support, *, dimension, prec, residual_order):
        calls.append(prec)
        index = [128, 256, 384, 512].index(prec)
        return {
            "mu_lower": 0.7,
            "finite_block_min_eigenvalue_midpoint": 0.02,
            "schur_min_eigenvalue_midpoint": schur[index],
            "interval_widths": {
                name: widths[index]
                for name in (
                    "A_max",
                    "GV_max",
                    "G2_max",
                    "GR_max",
                    "mu",
                    "rho_R",
                    "residual_remainder",
                )
            },
        }

    monkeypatch.setattr(driver, "scout_support", fake_screen)
    result = driver._escalate_rigorous_screen(
        Fraction(19, 40), 64, [128, 256, 384, 512], 32
    )

    assert result["status"] == "precision_stable"
    assert result["selected_precision_bits"] == 384
    assert calls == [128, 256, 384]


def test_p10_precision_exhaustion_is_distinct_from_mathematical_rejection(
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

    def precision_limited(support, *, dimension, prec, residual_order):
        return {
            "mu_lower": 0.7,
            "finite_block_min_eigenvalue_midpoint": 0.02,
            "schur_min_eigenvalue_midpoint": float(prec),
            "interval_widths": {name: 1.0 / prec for name in width_names},
        }

    monkeypatch.setattr(driver, "scout_support", precision_limited)
    exhausted = driver._escalate_rigorous_screen(
        Fraction(19, 40), 64, [128, 256], 32
    )
    assert exhausted["status"] == "precision_limit_reached"

    def mathematical_negative(support, *, dimension, prec, residual_order):
        return {
            "mu_lower": 0.7,
            "finite_block_min_eigenvalue_midpoint": 0.02,
            "schur_min_eigenvalue_midpoint": -0.010000 if prec == 128 else -0.010005,
            "interval_widths": {
                name: 2.0 if prec == 128 else 1.0 for name in width_names
            },
        }

    monkeypatch.setattr(driver, "scout_support", mathematical_negative)
    rejected = driver._escalate_rigorous_screen(
        Fraction(19, 40), 64, [128, 256], 32
    )
    assert rejected["status"] == "mathematical_negative"


def test_p10_exact_rounding_failure_retries_higher_matrix_bits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[int, int]] = []

    def fake_candidate(
        support, *, dimension, prec, residual_order, matrix_bits, witness_bits
    ):
        calls.append((matrix_bits, witness_bits))
        if matrix_bits == 64:
            raise driver.CandidateStageError("rounding", "outward interval too coarse")
        return {"all_margins_positive": True}

    monkeypatch.setattr(driver, "run_candidate", fake_candidate)
    result = driver._construct_candidate(
        Fraction(19, 40), 64, 384, 32, [64, 80], [32, 40], None
    )

    assert result["status"] == "candidate_ready"
    assert result["selected_matrix_bits"] == 80
    assert result["selected_witness_bits"] == 32
    assert calls == [(64, 32), (64, 40), (80, 32)]
    assert [attempt["status"] for attempt in result["attempts"][:2]] == [
        "rounding_failed",
        "rounding_failed",
    ]


def test_p10_witness_failure_is_pre_theorem_failure(
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
            "status": "witness_failed",
            "selected_matrix_bits": None,
            "selected_witness_bits": None,
            "attempts": [],
        },
    )

    result = driver.run_driver(Fraction(19, 40), [64])

    assert result["state"] == "WITNESS_FAILED"
    assert result["theorem_status"] is False
    assert result["independently_verified"] is False
    assert result["whitelisted"] is False


def test_p10_candidate_ready_never_reports_verified(
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
            "status": "candidate_ready",
            "selected_matrix_bits": 80,
            "selected_witness_bits": 40,
            "attempts": [],
        },
    )

    result = driver.run_driver(Fraction(19, 40), [64])

    assert result["state"] == "CANDIDATE_READY"
    assert result["status"] == "CANDIDATE_READY"
    assert result["theorem_status"] is False
    assert result["independently_verified"] is False
    assert result["whitelisted"] is False
    assert result["automatic_promotion"] is False


def test_p10_driver_has_no_theorem_admission_import_or_call_surface() -> None:
    source_path = Path(driver.__file__)
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))

    imported_modules: set[str] = set()
    called_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)
        elif isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called_names.add(node.func.attr)

    assert imported_modules.isdisjoint(
        {
            "scripts.cert.exact_prime_schur_certificate",
            "scripts.cert.export_certificate",
        }
    )
    assert called_names.isdisjoint(
        {
            "build_exact_prime_schur_certificate",
            "validate_certificate_schema",
            "allowed_exact_prime_configuration",
            "verify_exact_prime_schur",
        }
    )
    assert "ALLOWED_CONFIGURATIONS" not in source_path.read_text(encoding="utf-8")


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
