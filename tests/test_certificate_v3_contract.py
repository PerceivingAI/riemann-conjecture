"""v3 research-only boundary, fail-closed contract and source binding tests."""
from __future__ import annotations

import copy
import gzip
import json
from pathlib import Path

import pytest

from scripts.cert.export_combined_schur_v3 import (
    SCHEMA,read_json,validate,to_analytic_packet,check_integer,
)

CANDIDATE=Path("computations/2026-10-17T222400Z-v3-research-bundle/data/certificate-v3-research.json")


@pytest.fixture(scope="module")
def candidate():
    return read_json(CANDIDATE)


def test_real_research_candidate_is_structurally_valid(candidate):
    validate(candidate)
    assert candidate["provenance"]["status"]=="research_uncommitted_not_proof_bearing"
    assert candidate["generator_metadata"]["git_dirty"] is True
    assert to_analytic_packet(candidate)["dimension"]==192


@pytest.mark.parametrize("mutation",[
    lambda x: x.update({"format":"rh-weil-certificate-v2"}),
    lambda x: x.update({"active_terms":[2]}),
    lambda x: x["eta"].update({"num":"3"}),
    lambda x: x["basis"].update({"normalization":"orthonormal"}),
    lambda x: x["provenance"].update({"status":"clean_candidate_pending_admission"}),
    lambda x: x["mu_dyadic"].__setitem__(0,"0"),
    lambda x: x["delta_dyadic"].__setitem__(0,"-1"),
    lambda x: x["low_A_triangular"][0][0].__setitem__(0, "100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"),
    lambda x: x["witness_numerators"][0].__setitem__(1,"1"),
    lambda x: x["witness_numerators"][0].__setitem__(0,"0"),
])
def test_wrong_mathematical_inputs_fail_closed(candidate,mutation):
    copy_candidate=copy.deepcopy(candidate)
    mutation(copy_candidate)
    with pytest.raises((ValueError,KeyError)):
        validate(copy_candidate)


def test_noncanonical_numeric_strings_fail_closed():
    for text in ("+1","01","-0","","NaN","-00","1.0"):
        with pytest.raises(ValueError):
            check_integer(text)


def test_duplicate_json_key_fails(tmp_path):
    p=tmp_path/"dupe.json"
    p.write_text('{"format":"v3","format":"v1"}',encoding="utf8")
    with pytest.raises(ValueError,match="duplicate JSON"):
        read_json(p)


def test_clean_provenance_requires_distinct_producer(candidate):
    trial=copy.deepcopy(candidate)
    trial["provenance"]["status"]="clean_candidate_pending_admission"
    trial["generator_metadata"]["git_dirty"]=False
    with pytest.raises(ValueError,match="clean-source producer"):
        validate(trial)
    trial=copy.deepcopy(candidate)
    trial["generator_metadata"]["script"]="scripts/cert/export_combined_schur_v3_clean.py"
    with pytest.raises(ValueError,match="research exporter"):
        validate(trial)


def test_two_gate_rejects_forged_clean_claim_before_expensive_audit(candidate,tmp_path):
    from scripts.verify_combined_schur_v3_bundle import check
    trial=copy.deepcopy(candidate)
    trial["provenance"]["status"]="clean_candidate_pending_admission"
    trial["generator_metadata"]["git_dirty"]=False
    trial["generator_metadata"]["script"]="scripts/cert/export_combined_schur_v3_clean.py"
    path=tmp_path/"forged-clean.json"
    path.write_text(json.dumps(trial),encoding="utf8")
    with pytest.raises(ValueError,match="clean-source certificate"):
        check(path,tmp_path/"should-not-exist.json",Path("target/debug/rh_cert.exe"))


def test_two_gate_rejects_unpinned_analytic_code(candidate,tmp_path):
    from scripts.verify_combined_schur_v3_bundle import check
    trial=copy.deepcopy(candidate)
    trial["provenance"]["independent_auditor_sha256"]="0"*64
    path=tmp_path/"unmatched-auditor.json"
    path.write_text(json.dumps(trial),encoding="utf8")
    with pytest.raises(ValueError,match="independent analytical implementation"):
        check(path,tmp_path/"should-not-exist.json",Path("target/debug/rh_cert.exe"))


def test_archive_not_relabelled_clean(candidate):
    trial=copy.deepcopy(candidate)
    trial["generator_metadata"]["git_dirty"]=False
    with pytest.raises(ValueError):
        validate(trial)
