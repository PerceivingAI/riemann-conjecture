from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.continuation_bundle import BUNDLE_FORMAT, write_continuation_bundle


def _result() -> dict[str, object]:
    return {
        "role": "pre_theorem_continuation_driver",
        "driver_version": "continuation-driver-p8-v1",
        "cache_version": "continuation-driver-v4",
        "state": "CANDIDATE_READY",
        "status": "CANDIDATE_READY",
        "theorem_status": False,
        "independently_verified": False,
        "whitelisted": False,
        "support": "19/40",
        "dimensions": [60, 64],
        "scout_resolution_count": 2,
        "scout_workers": 3,
        "rigorous_workers": 2,
        "scout_resolution_plan": [
            {"level": 0, "max_mode": 120, "quadrature_order": 700, "shift_order": 350},
            {"level": 1, "max_mode": 160, "quadrature_order": 860, "shift_order": 430},
        ],
        "precision_start": 128,
        "precision_max": 256,
        "precision_ladder": [128, 256],
        "residual_order": 32,
        "matrix_bits_start": 64,
        "matrix_bits_max": 80,
        "matrix_bits_ladder": [64, 80],
        "witness_bits_start": 32,
        "witness_bits_max": 40,
        "witness_bits_ladder": [32, 40],
        "cache_dir": ".cache/continuation-driver",
        "scout_runs": [
            {
                "status": "completed",
                "resolution": {"level": 0, "max_mode": 120, "quadrature_order": 700, "shift_order": 350},
                "result": {"role": "floating_reconnaissance_only", "schur_rows": []},
            },
            {
                "status": "completed",
                "resolution": {"level": 1, "max_mode": 160, "quadrature_order": 860, "shift_order": 430},
                "result": {"role": "floating_reconnaissance_only", "schur_rows": []},
            },
        ],
        "reconnaissance": [],
        "scout_failures": [],
        "rigorous_screening": [
            {
                "dimension": 64,
                "status": "precision_stable",
                "selected_precision_bits": 256,
                "attempts": [
                    {
                        "precision_bits": 128,
                        "mu_lower": 0.7,
                        "finite_block_min_eigenvalue_midpoint": 0.01,
                        "schur_min_eigenvalue_midpoint": 0.001,
                    },
                    {
                        "precision_bits": 256,
                        "mu_lower": 0.71,
                        "finite_block_min_eigenvalue_midpoint": 0.011,
                        "schur_min_eigenvalue_midpoint": 0.0011,
                    },
                ],
                "precision_pair_diagnostics": [],
            }
        ],
        "rigorous_failures": [],
        "candidates": [
            {
                "dimension": 64,
                "status": "candidate_ready",
                "selected_matrix_bits": 80,
                "selected_witness_bits": 40,
                "attempts": [
                    {
                        "role": "generator_side_exact_candidate_only",
                        "status": "CANDIDATE_READY",
                        "support": "19/40",
                        "dimension": 64,
                        "precision_bits": 256,
                        "matrix_bits": 80,
                        "witness_bits": 40,
                        "mu_lower": "7/10",
                        "even_gershgorin_margin": "1/100",
                        "odd_gershgorin_margin": "1/200",
                        "all_margins_positive": True,
                        "theorem_status": False,
                        "independently_verified": False,
                        "whitelisted": False,
                    }
                ],
            }
        ],
        "candidate_failures": [],
        "scout_primary_dimension": 64,
        "selected_dimension": 64,
        "selected_candidate_dimension": 64,
        "fallback_dimensions": [],
        "warning": "Candidate is generator-side evidence only.",
    }


def test_p8_bundle_writes_stage_artifacts_and_hash_manifest(tmp_path: Path) -> None:
    output_dir = tmp_path / "continuation-T019-040"
    provenance = {
        "git_commit": "a" * 40,
        "git_dirty": True,
        "python_version": "3.14.0",
        "python_implementation": "CPython",
        "python_flint_version": "0.9.0",
    }

    manifest = write_continuation_bundle(
        _result(),
        output_dir,
        run_started_at="2026-08-27T09:00:00Z",
        run_completed_at="2026-08-27T09:05:00Z",
        provenance=provenance,
    )

    expected = {
        "summary.json",
        "scout/resolution-01.json",
        "scout/resolution-02.json",
        "rigorous/N064-p128.json",
        "rigorous/N064-p256.json",
        "candidate/candidate.json",
        "run-manifest.json",
    }
    actual = {
        path.relative_to(output_dir).as_posix()
        for path in output_dir.rglob("*")
        if path.is_file()
    }
    assert actual == expected
    assert not any("certificate" in path.lower() for path in actual)

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["state"] == "CANDIDATE_READY"
    assert "scout_runs" not in summary

    candidate = json.loads(
        (output_dir / "candidate" / "candidate.json").read_text(encoding="utf-8")
    )
    assert candidate["selected_candidate"]["dimension"] == 64
    assert candidate["selected_candidate"]["all_margins_positive"] is True
    assert candidate["theorem_status"] is False
    assert candidate["independently_verified"] is False
    assert candidate["whitelisted"] is False

    stored_manifest = json.loads(
        (output_dir / "run-manifest.json").read_text(encoding="utf-8")
    )
    assert stored_manifest == manifest
    assert manifest["format"] == BUNDLE_FORMAT
    assert manifest["run_started_at_utc"] == "2026-08-27T09:00:00Z"
    assert manifest["run_completed_at_utc"] == "2026-08-27T09:05:00Z"
    assert manifest["provenance"] == provenance
    assert manifest["configuration"]["support"] == "19/40"
    assert manifest["configuration"]["precision_ladder"] == [128, 256]
    assert manifest["configuration"]["scout_workers"] == 3
    assert manifest["configuration"]["rigorous_workers"] == 2

    artifact_paths = {entry["path"] for entry in manifest["artifacts"]}
    assert artifact_paths == expected - {"run-manifest.json"}
    for entry in manifest["artifacts"]:
        data = (output_dir / entry["path"]).read_bytes()
        assert entry["sha256"] == hashlib.sha256(data).hexdigest()
        assert entry["bytes"] == len(data)


def test_bundle_allows_live_operational_directory_without_manifesting_it(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "live-continuation"
    live_dir = output_dir / ".live"
    live_dir.mkdir(parents=True)
    live_status = live_dir / "run-status.json"
    live_status.write_text('{"terminal": false}\n', encoding="utf-8")
    live_events = live_dir / "events.jsonl"
    live_events.write_text(
        '{"seq":1,"time":"2026-08-28T02:00:00Z","event":"RUN_STARTED"}\n',
        encoding="utf-8",
    )

    manifest = write_continuation_bundle(
        _result(),
        output_dir,
        provenance={
            "git_commit": "a" * 40,
            "git_dirty": False,
            "python_version": "3.14.0",
            "python_implementation": "CPython",
            "python_flint_version": "0.9.0",
        },
    )

    assert live_status.read_text(encoding="utf-8") == '{"terminal": false}\n'
    assert live_events.read_text(encoding="utf-8").startswith('{"seq":1,')
    assert all(not str(entry["path"]).startswith(".live/") for entry in manifest["artifacts"])
    assert (output_dir / "run-manifest.json").is_file()


def test_p8_bundle_refuses_nonempty_output_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "existing"
    output_dir.mkdir()
    (output_dir / "stale.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must be empty"):
        write_continuation_bundle(
            _result(),
            output_dir,
            provenance={
                "git_commit": "a" * 40,
                "git_dirty": False,
                "python_version": "3.14.0",
                "python_implementation": "CPython",
                "python_flint_version": "0.9.0",
            },
        )
