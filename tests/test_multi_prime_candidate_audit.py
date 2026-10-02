"""Replay real candidate inputs; reject plausible proof and packaging corruption."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json

import pytest

from scripts.audit_multi_prime_candidate import audit_candidate_inputs
from scripts.continuation_bundle import write_continuation_bundle, _result_payload_digest
from scripts.weil_multi_prime_support_candidate_check import run_candidate


@pytest.fixture(scope="module")
def candidates():
    return [run_candidate(Fraction(2, 5), dimension=40, prec=prec, residual_order=32,
                          matrix_bits=64, witness_bits=32) for prec in (256, 384)]


def test_real_base_and_confirmation_inputs_recompute_exact_positive_margins(candidates):
    for candidate in candidates:
        replay = audit_candidate_inputs(candidate["audit_inputs"])
        for field in ("mu_lower", "even_gershgorin_margin", "odd_gershgorin_margin"):
            assert Fraction(replay[field]) == Fraction(candidate[field]) > 0
        assert replay["theorem_status"] is False


@pytest.mark.parametrize("attack", [
    "reported_margin", "witness", "negative_matrix", "factor", "complement",
    "prime_loss", "coordinate", "parity", "resolution", "basis", "float_precision",
    "promotion", "missing_gp", "wrong_prime", "incomplete_status",
])
def test_exact_replay_rejects_corrupted_real_candidate(candidates, attack):
    proof = deepcopy(candidates[0]["audit_inputs"])
    if attack == "reported_margin":
        proof["even_gershgorin_margin"] = "1"
    elif attack == "witness":
        proof["witnesses"]["even"]["entries"][0]["num"] = "0"
    elif attack == "negative_matrix":
        proof["matrices"]["A"]["entries"][0].update(lo_num="-100", hi_num="-100", lo_den="1", hi_den="1")
    elif attack == "factor":
        proof["factor"] = "2"
    elif attack == "complement":
        proof["mu_lower"] = "100"
    elif attack == "prime_loss":
        proof["active_terms"][0]["rounded_complement_contribution"]["upper"] = "0"
    elif attack == "coordinate":
        proof["matrices"]["GP"]["entries"][1] = deepcopy(proof["matrices"]["GP"]["entries"][0])
    elif attack == "parity":
        proof["matrices"]["A"]["entries"][1].update(lo_num="1", hi_num="1", lo_den="1", hi_den="1")
        proof["matrices"]["A"]["entries"][40].update(lo_num="1", hi_num="1", lo_den="1", hi_den="1")
    elif attack == "resolution":
        proof["matrix_bits"] = 16
    elif attack == "basis":
        proof["basis"] = "orthonormal_legendre"
    elif attack == "float_precision":
        proof["precision_bits"] = 256.0
    elif attack == "promotion":
        proof["theorem_status"] = True
    elif attack == "missing_gp":
        del proof["matrices"]["GP"]
    elif attack == "wrong_prime":
        proof["active_terms"][0]["prime"] = 4
    else:
        proof["status"] = "WITNESS_FAILED"
    with pytest.raises((ValueError, KeyError)):
        audit_candidate_inputs(proof)


def _result(candidates):
    base, confirmation = candidates
    stability = {"qualified": True, "selected_confirmation_precision_bits": 384,
                 "attempts": [base, confirmation]}
    return {
        "role": "pre_theorem_multi_prime_continuation_driver", "state": "CANDIDATE_READY",
        "workflow_state": "CANDIDATE_READY", "theorem_status": False,
        "independently_verified": False, "whitelisted": False, "automatic_promotion": False,
        "support": "2/5", "active_terms": [2], "residual_order": 32,
        "selected_candidate_dimension": 40,
        "candidates": [{"dimension": 40, "attempts": [base], "candidate_precision_stability": stability}],
    }


def _write(result, directory):
    cleanup = {"verified": True, "executors_shutdown": 0, "worker_processes_reaped": 0,
               "cleanup_escalations": 0, "workers_joined_after_shutdown": 0,
               "workers_terminated": 0, "workers_killed": 0, "active_children_after_cleanup": 0,
               "stages": []}
    return write_continuation_bundle(result, directory, worker_cleanup=cleanup,
                                    result_payload_sha256=_result_payload_digest(result),
                                    provenance={"role": "packaging_test_only"})


def test_bundle_seals_replayable_base_and_fixed_input_confirmation(candidates, tmp_path):
    manifest = _write(_result(candidates), tmp_path / "bundle")
    audits = [item for item in manifest["artifacts"] if item["kind"] == "pre_theorem_exact_candidate_audit"]
    assert len(audits) == 2
    observed_precisions = set()
    for item in audits:
        raw = (tmp_path / "bundle" / item["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item["sha256"]
        proof = json.loads(raw)
        replay = audit_candidate_inputs(proof)
        observed_precisions.add(replay["precision_bits"])
        assert all(Fraction(replay[field]) > 0 for field in (
            "mu_lower", "even_gershgorin_margin", "odd_gershgorin_margin"))
    assert observed_precisions == {256, 384}


@pytest.mark.parametrize("attack", ["missing_audit", "missing_confirmation", "changed_bits", "changed_support", "selected_missing"])
def test_bundle_cannot_seal_incomplete_or_changed_confirmation(candidates, tmp_path, attack):
    result = deepcopy(_result(candidates))
    run = result["candidates"][0]
    if attack == "missing_audit":
        del run["attempts"][0]["audit_inputs"]
    elif attack == "missing_confirmation":
        run["candidate_precision_stability"]["attempts"] = [run["attempts"][0]]
    elif attack == "changed_bits":
        run["candidate_precision_stability"]["attempts"][1]["matrix_bits"] = 72
    elif attack == "changed_support":
        result["support"] = "3/5"
    else:
        result["selected_candidate_dimension"] = 44
    with pytest.raises(ValueError):
        _write(result, tmp_path / "bundle")
    assert not (tmp_path / "bundle" / "run-manifest.json").exists()
