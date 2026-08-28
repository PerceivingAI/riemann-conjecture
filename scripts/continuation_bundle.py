"""Self-contained artifact writer for pre-theorem continuation runs.

The bundle is evidence packaging only.  It never emits a theorem certificate,
changes admission state, or invokes the independent verifier.  Git commands in
this module are fixed read-only provenance queries.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import flint

from scripts.run_observability import LIVE_DIRECTORY_NAME, RUN_LOCK_FILENAME


BUNDLE_FORMAT = "rh-continuation-candidate-bundle-v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _run_read_only_git(root: Path, args: tuple[str, ...]) -> str:
    allowed = {
        ("rev-parse", "HEAD"),
        ("status", "--porcelain=v1", "--untracked-files=normal"),
    }
    if args not in allowed:
        raise ValueError("only fixed read-only Git provenance queries are allowed")
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Git provenance query failed ({' '.join(args)}): {completed.stderr.strip()}"
        )
    return completed.stdout.strip()


def collect_runtime_provenance(repository_root: Path | None = None) -> dict[str, object]:
    root = repository_root or Path(__file__).resolve().parents[1]
    commit = _run_read_only_git(root, ("rev-parse", "HEAD"))
    status = _run_read_only_git(
        root, ("status", "--porcelain=v1", "--untracked-files=normal")
    )
    return {
        "git_commit": commit,
        "git_dirty": bool(status),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_flint_version": str(getattr(flint, "__version__", "unknown")),
    }


def _json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _atomic_write_json(path: Path, payload: object) -> tuple[str, int]:
    data = _json_bytes(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)
    return hashlib.sha256(data).hexdigest(), len(data)


def _summary_payload(result: dict[str, Any]) -> dict[str, Any]:
    # Raw floating scout outputs live in stage artifacts, not in the summary.
    return {key: value for key, value in result.items() if key != "scout_runs"}


def _configuration_payload(result: dict[str, Any]) -> dict[str, object]:
    keys = (
        "support",
        "dimensions",
        "scout_resolution_count",
        "scout_resolution_plan",
        "scout_workers",
        "rigorous_workers",
        "precision_start",
        "precision_max",
        "precision_ladder",
        "residual_order",
        "matrix_bits_start",
        "matrix_bits_max",
        "matrix_bits_ladder",
        "witness_bits_start",
        "witness_bits_max",
        "candidate_precision_step",
        "candidate_precision_extra_steps",
        "witness_bits_ladder",
        "cache_dir",
    )
    return {key: result.get(key) for key in keys}


def _selected_candidate_payload(result: dict[str, Any]) -> dict[str, object] | None:
    selected_dimension = result.get("selected_candidate_dimension")
    for candidate_run in result.get("candidates", []):
        if candidate_run.get("dimension") != selected_dimension:
            continue
        for attempt in reversed(candidate_run.get("attempts", [])):
            if attempt.get("all_margins_positive") is True:
                return attempt
    return None


def write_continuation_bundle(
    result: dict[str, Any],
    output_dir: Path,
    *,
    run_started_at: str | None = None,
    run_completed_at: str | None = None,
    provenance: dict[str, object] | None = None,
) -> dict[str, Any]:
    """Write a complete P8 continuation bundle and return its manifest."""
    if output_dir.exists():
        entries = list(output_dir.iterdir())
        allowed_names = {LIVE_DIRECTORY_NAME, RUN_LOCK_FILENAME}
        unexpected = [entry for entry in entries if entry.name not in allowed_names]
        live_entries = [entry for entry in entries if entry.name == LIVE_DIRECTORY_NAME]
        lock_entries = [entry for entry in entries if entry.name == RUN_LOCK_FILENAME]
        if (
            unexpected
            or any(not entry.is_dir() for entry in live_entries)
            or any(not entry.is_file() for entry in lock_entries)
        ):
            raise ValueError(
                "continuation output directory must be empty except for .live and .run.lock"
            )
    output_dir.mkdir(parents=True, exist_ok=True)

    started = run_started_at or utc_now()
    completed = run_completed_at or utc_now()
    runtime = provenance or collect_runtime_provenance()
    artifacts: list[dict[str, object]] = []

    def write(relative_path: str, payload: object, kind: str) -> None:
        sha256, byte_count = _atomic_write_json(output_dir / relative_path, payload)
        artifacts.append(
            {
                "path": relative_path.replace("\\", "/"),
                "kind": kind,
                "sha256": sha256,
                "bytes": byte_count,
            }
        )

    write("summary.json", _summary_payload(result), "summary")

    for index, run in enumerate(result.get("scout_runs", []), start=1):
        write(
            f"scout/resolution-{index:02d}.json",
            run,
            "floating_reconnaissance",
        )

    for screening in result.get("rigorous_screening", []):
        dimension = int(screening["dimension"])
        for attempt in screening.get("attempts", []):
            precision = int(attempt["precision_bits"])
            write(
                f"rigorous/N{dimension:03d}-p{precision}.json",
                {
                    "role": "rigorous_full_tail_screening_attempt",
                    "support": result.get("support"),
                    "dimension": dimension,
                    "residual_order": result.get("residual_order"),
                    "screening_status": screening.get("status"),
                    "selected_precision_bits": screening.get("selected_precision_bits"),
                    "attempt": attempt,
                },
                "rigorous_screening",
            )

    for candidate_run in result.get("candidates", []):
        stability = candidate_run.get("candidate_precision_stability")
        if not isinstance(stability, dict):
            continue
        dimension = int(candidate_run["dimension"])
        write(
            f"candidate/precision-stability-N{dimension:03d}.json",
            {
                "role": "pre_theorem_candidate_precision_stability",
                "support": result.get("support"),
                "dimension": dimension,
                "stability": stability,
                "theorem_status": False,
                "independently_verified": False,
            },
            "candidate_precision_stability",
        )

    for failure in result.get("rigorous_failures", []):
        dimension = int(failure["dimension"])
        write(
            f"rigorous/N{dimension:03d}-failure.json",
            {
                "role": "rigorous_full_tail_screening_failure",
                "support": result.get("support"),
                **failure,
            },
            "rigorous_screening_failure",
        )

    write(
        "candidate/candidate.json",
        {
            "role": "pre_theorem_exact_candidate_stage",
            "status": result.get("state"),
            "support": result.get("support"),
            "selected_dimension": result.get("selected_candidate_dimension"),
            "selected_candidate": _selected_candidate_payload(result),
            "candidate_runs": result.get("candidates", []),
            "candidate_failures": result.get("candidate_failures", []),
            "theorem_status": result.get("theorem_status", False),
            "independently_verified": result.get("independently_verified", False),
            "whitelisted": result.get("whitelisted", False),
            "warning": result.get("warning"),
        },
        "exact_candidate",
    )

    artifacts.sort(key=lambda artifact: str(artifact["path"]))
    manifest = {
        "format": BUNDLE_FORMAT,
        "role": "pre_theorem_continuation_bundle_manifest",
        "driver_version": result.get("driver_version"),
        "cache_version": result.get("cache_version"),
        "run_started_at_utc": started,
        "run_completed_at_utc": completed,
        "configuration": _configuration_payload(result),
        "provenance": runtime,
        "final_state": result.get("state"),
        "workflow_state": result.get("workflow_state", result.get("state")),
        "workflow_trace": result.get("workflow_trace", []),
        "theorem_status": result.get("theorem_status", False),
        "independently_verified": result.get("independently_verified", False),
        "whitelisted": result.get("whitelisted", False),
        "artifacts": artifacts,
        "warning": (
            "This bundle contains pre-theorem continuation evidence only. "
            "It contains no theorem certificate and records no independent verifier admission."
        ),
    }
    _atomic_write_json(output_dir / "run-manifest.json", manifest)
    return manifest
