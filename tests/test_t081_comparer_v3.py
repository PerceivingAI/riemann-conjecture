"""Versioned identity-gate regressions, including JSON numeric type substitutions."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "computations/2026-10-28T024305Z-t081-execution-corrections"
PRIOR = ROOT / "computations/2026-10-27T235900Z-t081-parallel-source"


def invoke(source, output):
    return subprocess.run([sys.executable, "-B", str(BUNDLE / "compare-v3-v1.py"),
        "--source", str(source), "--producer", str(PRIOR / "build-whole-source-v2.py"),
        "--output", str(output)], capture_output=True, text=True)


def test_actual_retained_equivalent_publication_passes(tmp_path):
    output = tmp_path / "identity.json"
    result = invoke(PRIOR / "data/run-v2/source-v2.json", output)
    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_bytes())
    assert report["status"] == "PASS_EXACT_RETAINED_PAYLOAD_IDENTITY"
    assert all(item["identical"] for item in report["matrices"])


@pytest.mark.parametrize("mutation", ["precision-float", "admission-zero", "size-float",
    "digest", "precision-value", "missing-matrix", "extra-metadata", "producer", "packet", "duplicate-key"])
def test_changed_json_types_metadata_and_packets_fail(tmp_path, mutation):
    data = json.loads((PRIOR / "data/run-v2/source-v2.json").read_bytes())
    for descriptor in data["matrices"].values():
        target = tmp_path / descriptor["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PRIOR / "data/run-v2" / descriptor["path"], target)
    if mutation == "precision-float":
        data["precision"] = float(data["precision"])
    elif mutation == "admission-zero":
        data["production_admission"] = 0
    elif mutation == "size-float":
        data["matrices"]["A_model-0"]["size"] = float(data["matrices"]["A_model-0"]["size"])
    elif mutation == "digest":
        data["matrices"]["A_model-0"]["sha256"] = "0" * 64
    elif mutation == "precision-value":
        data["precision"] = 1
    elif mutation == "missing-matrix":
        del data["matrices"]["A_model-1"]
    elif mutation == "extra-metadata":
        data["extra"] = True
    elif mutation == "producer":
        data["producer_sha256"] = "0" * 64
    elif mutation == "packet":
        (tmp_path / data["matrices"]["A_model-0"]["path"]).write_bytes(b"changed")
    raw = json.dumps(data)
    if mutation == "duplicate-key":
        raw = raw[:-1] + ', "precision": 4608}'
    source, output = tmp_path / "source.json", tmp_path / "comparison.json"
    source.write_text(raw, encoding="utf-8")
    result = invoke(source, output)
    assert result.returncode == 1
    assert "FAIL_SOURCE_IDENTITY" in result.stderr
    assert not output.exists()


def test_existing_report_is_not_overwritten(tmp_path):
    report = tmp_path / "existing.json"
    report.write_bytes(b"preserved")
    result = invoke(PRIOR / "data/run-v2/source-v2.json", report)
    assert result.returncode == 1
    assert report.read_bytes() == b"preserved"
