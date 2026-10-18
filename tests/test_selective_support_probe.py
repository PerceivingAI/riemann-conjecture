"""SYS-6.4 selective research obstruction: cheap exact sign and tamper checks.

The 1024-bit large matrix was already executed and is NOT rerun by tests.
"""
import json
from fractions import Fraction
from pathlib import Path

import pytest

from scripts.verify_selective_support_probe import verify
from scripts.weil_selective_support_probe import run

SOURCE = Path(
    "computations/2026-10-18T090311Z-sys6-selective-support/"
    "data/T-3-5-N192-probe.json"
)


def test_original_exact_arithmetic_and_scope():
    r=verify(SOURCE)
    assert r["status"]=="PASS_EXACT_RATIONAL_ARITHMETIC_ONLY"
    assert r["trial_parity"]=="odd"
    assert r["negative_rayleigh_upper"] is True
    assert r["original_arb_source_reconstruction"]=="NOT_INDEPENDENTLY_CHECKED"


@pytest.mark.parametrize("key,replacement",[
    ("rigorous_chosen_schur_rayleigh_upper_exact", "1"),
    ("sign_classification", "CERTIFIED_WEIL_NEGATIVE"),
    ("mu_lower_exact", "-1"),
    ("support", "11/20"),
])
def test_tampered_research_evidence_rejected(tmp_path, key, replacement):
    p=json.loads(SOURCE.read_text(encoding="utf8"))
    p[key]=replacement
    copy=tmp_path/"forged.json"
    copy.write_text(json.dumps(p),encoding="utf8")
    with pytest.raises(ValueError):
        verify(copy)


def test_failed_source_fingerprint_rejected(tmp_path):
    p=json.loads(SOURCE.read_text(encoding="utf8"))
    p["source_sha256"]["scripts/cert/mixed_gram_research.py"]="0"*64
    copy=tmp_path/"source-changed.json"
    copy.write_text(json.dumps(p),encoding="utf8")
    with pytest.raises(ValueError):
        verify(copy)


@pytest.mark.parametrize("support,n,prec",[
    (Fraction(11,20),192,1024),
    (Fraction(3,5),100,1024),
    (Fraction(3,5),192,128),
    (Fraction(7,10),192,1024),
])
def test_out_of_scope_probe_refused_without_assembly(support,n,prec):
    with pytest.raises(ValueError):
        run(support,n,prec)
