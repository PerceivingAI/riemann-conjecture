"""SYS-5.4 closed v3 retained-proof admission guards.

These inexpensive controls never invoke the full 37,056-entry Arb replay.
That separately required acceptance is scripts.cert.verify_retained_v3.
"""
from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest

from scripts.cert import verify_retained_v3 as admission

ROOT = Path(__file__).resolve().parents[1]


def test_closed_v3_manifest_matches_only_approved_artifact():
    entry = admission.checked_manifest()
    assert entry == admission.EXPECTED
    raw = ROOT / entry["certificate_path"]
    assert admission.sha(raw.read_bytes()) == admission.APPROVED_SHA


@pytest.mark.parametrize("mutation", ["add_claim", "change_hash", "change_scope", "change_path", "extra_field"])
def test_v3_manifest_rejects_altered_or_extra_proofs(tmp_path: Path, mutation: str):
    original = json.loads(admission.MANIFEST.read_text(encoding="utf8"))
    altered = copy.deepcopy(original)
    if mutation == "add_claim":
        second = copy.deepcopy(altered["proofs"][0])
        second["claim"] = "C-0068"
        altered["proofs"].append(second)
    elif mutation == "change_hash":
        altered["proofs"][0]["certificate_sha256"] = "0" * 64
    elif mutation == "change_scope":
        altered["proofs"][0]["verified_scope"] = "all_supports"
    elif mutation == "change_path":
        altered["proofs"][0]["certificate_path"] = "../certificate-v3-clean.json"
    else:
        altered["proofs"][0]["unexpected"] = "unauthorized"
    path = tmp_path / "forged-manifest.json"
    path.write_text(json.dumps(altered), encoding="utf8")
    with pytest.raises(ValueError):
        admission.checked_manifest(path)


def test_v3_production_rejects_semantically_valid_reencoded_proof(tmp_path: Path):
    """Changing one harmless JSON byte cannot inherit the theorem admission."""
    source = ROOT / admission.APPROVED_CERT_REL
    modified = tmp_path / "same-json-different-bytes.json"
    modified.write_bytes(source.read_bytes() + b" ")
    binary = ROOT / "target/debug/rh_cert.exe"
    assert binary.is_file(), "build the independent Rust verifier first"
    proc = subprocess.run(
        [str(binary), "verify", "--cert", str(modified), "--json"],
        cwd=ROOT, capture_output=True, text=True, timeout=90,
    )
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "not the exact admitted" in proc.stderr
