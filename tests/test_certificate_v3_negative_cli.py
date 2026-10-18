"""Adversarial full-profile v3 exact rational negative control.

Mathematically valid *synthetic* fixed-profile Schur input, intentionally NOT
an independently accepted Suzuki source enclosure. The research arithmetic
must classify a negative congruence as mathematical failure (exit 1), not
malformed input (exit 2) or admitted theorem.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scripts.cert.export_combined_schur_v3 import validate

REPO=Path(__file__).resolve().parents[1]
FIXTURE=REPO/"computations/2026-10-17T222400Z-v3-research-bundle/data/certificate-v3-research.json"


def test_full_v3_synthetic_exact_negative_not_a_theorem(tmp_path: Path):
    candidate=json.loads(FIXTURE.read_text(encoding="utf8"))
    # A strictly negative admissible rational Schur direction at index 0;
    # structurally valid but NOT valid as a source-analytic enclosure.
    value=str(-1000*(2**352))
    candidate["low_A_triangular"][0][0]=[value,value]
    validate(candidate)
    modified=tmp_path/"mathematically-negative-source-unverified.json"
    modified.write_text(json.dumps(candidate),encoding="utf8")
    binary=REPO/"target/debug/rh_cert.exe"
    assert binary.is_file(),"build rh_cert before running the full-profile negative test"
    completed=subprocess.run(
        [str(binary),"verify-candidate-v3","--cert",str(modified),"--json"],
        cwd=REPO,capture_output=True,text=True,timeout=110
    )
    assert completed.returncode==1,completed.stderr
    report=json.loads(completed.stdout)
    assert report["mathematical_status"]=="NONPOSITIVE_RATIONAL_SCHUR_LOWER"
    assert report["exact_margin_positive"] is False
    assert report["theorem_admitted"] is False
    assert report["admission_status"]=="UNADMITTED"
