"""Fast contract, integrity, replay, and adversarial tests for retained theorem proofs."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from scripts.cert.verify_retained_proofs import (
    DEFAULT_MANIFEST_PATH,
    EXACT_PRIME_PROFILE,
    EXPECTED_RETAINED_CLAIMS_V1,
    MANIFEST_FORMAT_V1,
    RetainedProofArtifactError,
    RetainedProofHashMismatch,
    RetainedProofManifest,
    RetainedProofManifestError,
    RetainedProofMissing,
    RetainedProofResult,
    RetainedProofSemanticMismatch,
    RetainedProofTheoremFailure,
    RetainedProofVerifierError,
    check_retained_proof,
    check_retained_proof_manifest,
    format_retained_proof_result,
    load_retained_proof_manifest,
    main,
    replay_retained_certificate,
    resolve_retained_certificate_path,
    sha256_raw_file,
    validate_retained_proof_manifest,
    verify_retained_certificate_integrity,
    verify_retained_proof,
)


def _document() -> dict[str, object]:
    return json.loads(DEFAULT_MANIFEST_PATH.read_text(encoding="utf-8"))


def _first_proof():
    return load_retained_proof_manifest().proofs[0]


def _verifier_output(proof, **overrides: Any) -> dict[str, Any]:
    output: dict[str, Any] = {
        "passed": True,
        "claim": proof.claim,
        "support_T": proof.support_t,
        "dimension": proof.dimension,
        "claim_profile": proof.claim_profile,
        "verified_scope": proof.verified_scope,
    }
    output.update(overrides)
    return output


def _completed(output: object, *, returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess[str]:
    stdout = output if isinstance(output, str) else json.dumps(output)
    return subprocess.CompletedProcess(args=["cargo"], returncode=returncode, stdout=stdout, stderr=stderr)


def _temp_valid_proof(tmp_path: Path, raw: bytes = b"certificate"):
    artifact = tmp_path / "proof.json"
    artifact.write_bytes(raw)
    proof = replace(
        _first_proof(),
        certificate_path="proof.json",
        certificate_sha256=hashlib.sha256(raw).hexdigest(),
    )
    return proof, artifact


def test_repository_manifest_is_valid_and_closed_to_seven_proofs() -> None:
    manifest = load_retained_proof_manifest()
    assert manifest.format == MANIFEST_FORMAT_V1
    assert {proof.claim for proof in manifest.proofs} == EXPECTED_RETAINED_CLAIMS_V1
    assert len(manifest.proofs) == 7
    assert all(proof.claim_profile == EXACT_PRIME_PROFILE for proof in manifest.proofs)


def test_repository_manifest_contains_only_proof_bearing_computations() -> None:
    manifest = load_retained_proof_manifest()
    assert {proof.computation_id for proof in manifest.proofs} == {
        "X-20260821-005",
        "X-20260826-001",
        "X-20260826-002",
        "X-20260826-003",
        "X-20260827-002",
        "X-20260827-004",
        "X-20260828-001",
    }
    assert "X-20260827-001" not in {proof.computation_id for proof in manifest.proofs}
    assert "X-20260827-003" not in {proof.computation_id for proof in manifest.proofs}
    assert "X-20260827-005" not in {proof.computation_id for proof in manifest.proofs}


@pytest.mark.parametrize("field", ["format", "proofs"])
def test_missing_top_level_field_is_rejected(field: str) -> None:
    document = _document()
    del document[field]
    with pytest.raises(RetainedProofManifestError, match="missing required field"):
        validate_retained_proof_manifest(document)


def test_unexpected_top_level_field_is_rejected() -> None:
    document = _document()
    document["extra"] = True
    with pytest.raises(RetainedProofManifestError, match="unexpected field"):
        validate_retained_proof_manifest(document)


@pytest.mark.parametrize(
    "field",
    [
        "claim",
        "computation_id",
        "certificate_path",
        "certificate_sha256",
        "support_T",
        "dimension",
        "claim_profile",
        "verified_scope",
    ],
)
def test_missing_proof_field_is_rejected(field: str) -> None:
    document = _document()
    del document["proofs"][0][field]  # type: ignore[index]
    with pytest.raises(RetainedProofManifestError, match="missing required field"):
        validate_retained_proof_manifest(document)


def test_unexpected_proof_field_is_rejected() -> None:
    document = _document()
    document["proofs"][0]["extra"] = "no"  # type: ignore[index]
    with pytest.raises(RetainedProofManifestError, match="unexpected field"):
        validate_retained_proof_manifest(document)


def test_derived_margin_field_is_not_part_of_retained_proof_identity() -> None:
    document = _document()
    document["proofs"][0]["expected_gershgorin_margin"] = "1/1000"  # type: ignore[index]
    with pytest.raises(RetainedProofManifestError, match="unexpected field"):
        validate_retained_proof_manifest(document)


def test_duplicate_claim_is_rejected() -> None:
    document = _document()
    document["proofs"][1]["claim"] = "C-0050"  # type: ignore[index]
    with pytest.raises(RetainedProofManifestError, match="duplicate claim"):
        validate_retained_proof_manifest(document)


def test_duplicate_certificate_path_is_rejected() -> None:
    document = _document()
    document["proofs"][1]["certificate_path"] = document["proofs"][0]["certificate_path"]  # type: ignore[index]
    with pytest.raises(RetainedProofManifestError, match="duplicate certificate_path"):
        validate_retained_proof_manifest(document)


@pytest.mark.parametrize(
    "value",
    [
        "A" * 64,
        "a" * 63,
        "g" * 64,
        "0x" + "a" * 64,
    ],
)
def test_noncanonical_sha256_is_rejected(value: str) -> None:
    document = _document()
    document["proofs"][0]["certificate_sha256"] = value  # type: ignore[index]
    with pytest.raises(RetainedProofManifestError, match="64 lowercase hexadecimal"):
        validate_retained_proof_manifest(document)


@pytest.mark.parametrize("value", [0, -1, True, 3.5, "32"])
def test_nonpositive_or_noninteger_dimension_is_rejected(value: object) -> None:
    document = _document()
    document["proofs"][0]["dimension"] = value  # type: ignore[index]
    with pytest.raises(RetainedProofManifestError, match="positive integer"):
        validate_retained_proof_manifest(document)


def test_non_exact_prime_profile_is_rejected() -> None:
    document = _document()
    document["proofs"][0]["claim_profile"] = "synthetic_matrix"  # type: ignore[index]
    with pytest.raises(RetainedProofManifestError, match="exact_prime_legendre_schur"):
        validate_retained_proof_manifest(document)


@pytest.mark.parametrize(
    "value",
    [
        "/absolute/certificate.json",
        "C:/repo/certificate.json",
        "computations\\run\\certificate.json",
        "computations/../certificate.json",
        "./computations/run/certificate.json",
        "computations//run/certificate.json",
        "computations/run/certificate.json/",
    ],
)
def test_non_normalized_or_non_relative_certificate_path_is_rejected(value: str) -> None:
    document = _document()
    document["proofs"][0]["certificate_path"] = value  # type: ignore[index]
    with pytest.raises(RetainedProofManifestError):
        validate_retained_proof_manifest(document)


@pytest.mark.parametrize("value", ["0/1", "7/020", "14/40", "7", "-7/20"])
def test_noncanonical_support_is_rejected(value: str) -> None:
    document = _document()
    document["proofs"][0]["support_T"] = value  # type: ignore[index]
    with pytest.raises(RetainedProofManifestError):
        validate_retained_proof_manifest(document)


def test_scope_must_match_support() -> None:
    document = _document()
    document["proofs"][0]["verified_scope"] = "localized_weil_positivity_T_2_5"  # type: ignore[index]
    with pytest.raises(RetainedProofManifestError, match="verified_scope"):
        validate_retained_proof_manifest(document)


def test_manifest_must_contain_exact_closed_claim_set() -> None:
    document = _document()
    document["proofs"].pop()  # type: ignore[union-attr]
    with pytest.raises(RetainedProofManifestError, match="exactly C-0050 through C-0056"):
        validate_retained_proof_manifest(document)


def test_duplicate_json_object_key_is_rejected(tmp_path: Path) -> None:
    manifest_path = tmp_path / "duplicate-key.json"
    manifest_path.write_text(
        '{"format":"rh-retained-proofs-v1","format":"rh-retained-proofs-v1","proofs":[]}',
        encoding="utf-8",
    )
    with pytest.raises(RetainedProofManifestError, match="duplicate object key 'format'"):
        load_retained_proof_manifest(manifest_path)


def test_loading_custom_manifest_reads_only_the_manifest(tmp_path: Path) -> None:
    document = copy.deepcopy(_document())
    manifest_path = tmp_path / "retained-proofs.json"
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    manifest = load_retained_proof_manifest(manifest_path)
    assert len(manifest.proofs) == 7


def test_resolve_and_hash_regular_repository_file(tmp_path: Path) -> None:
    artifact = tmp_path / "proof.json"
    raw = b'{"proof":"raw-bytes"}\r\n'
    artifact.write_bytes(raw)
    proof = replace(
        _first_proof(),
        certificate_path="proof.json",
        certificate_sha256=hashlib.sha256(raw).hexdigest(),
    )
    resolved = resolve_retained_certificate_path(proof, tmp_path)
    assert resolved == artifact.resolve()
    assert sha256_raw_file(resolved) == hashlib.sha256(raw).hexdigest()
    assert verify_retained_certificate_integrity(proof, tmp_path) == (
        resolved,
        hashlib.sha256(raw).hexdigest(),
    )


def test_missing_artifact_is_rejected(tmp_path: Path) -> None:
    proof = replace(_first_proof(), certificate_path="missing.json")
    with pytest.raises(RetainedProofMissing, match="is missing"):
        resolve_retained_certificate_path(proof, tmp_path)
    assert check_retained_proof(proof, tmp_path).stage == "MISSING"


def test_directory_is_not_accepted_as_artifact(tmp_path: Path) -> None:
    directory = tmp_path / "proof.json"
    directory.mkdir()
    proof = replace(_first_proof(), certificate_path="proof.json")
    with pytest.raises(RetainedProofArtifactError, match="not a regular file"):
        resolve_retained_certificate_path(proof, tmp_path)
    assert check_retained_proof(proof, tmp_path).stage == "VERIFIER_ERROR"


def test_pre_hash_operational_error_does_not_claim_hash_pass(tmp_path: Path) -> None:
    (tmp_path / "proof.json").mkdir()
    proof = replace(_first_proof(), certificate_path="proof.json")
    result = check_retained_proof(proof, tmp_path)
    assert result.stage == "VERIFIER_ERROR"
    assert result.hash_passed is False
    row = format_retained_proof_result(result)
    assert "HASH PASS" not in row
    assert "VERIFY SKIPPED" in row


def test_hash_mismatch_stops_before_verifier_invocation(tmp_path: Path) -> None:
    (tmp_path / "proof.json").write_bytes(b"tampered")
    proof = replace(
        _first_proof(),
        certificate_path="proof.json",
        certificate_sha256=hashlib.sha256(b"original").hexdigest(),
    )
    calls: list[list[str]] = []

    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return _completed(_verifier_output(proof))

    with pytest.raises(RetainedProofHashMismatch, match="SHA-256 mismatch"):
        verify_retained_proof(proof, tmp_path, run_command=runner)
    result = check_retained_proof(proof, tmp_path, run_command=runner)
    assert result.stage == "HASH_MISMATCH"
    assert calls == []


def test_real_retained_certificate_copy_tampering_is_caught_before_replay(tmp_path: Path) -> None:
    """P5 trust regression: never mutate the retained source artifact itself."""
    source_proof = _first_proof()
    source = resolve_retained_certificate_path(source_proof)
    copied = tmp_path / "certificate.json"
    shutil.copyfile(source, copied)
    original_hash = source_proof.certificate_sha256
    copied.write_bytes(copied.read_bytes() + b"\n")
    proof = replace(source_proof, certificate_path="certificate.json")
    calls: list[list[str]] = []

    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return _completed(_verifier_output(proof))

    assert sha256_raw_file(source) == original_hash
    result = check_retained_proof(proof, tmp_path, run_command=runner)
    assert result.stage == "HASH_MISMATCH"
    assert calls == []
    assert sha256_raw_file(source) == original_hash


def test_hash_valid_artifact_replays_through_cargo_rh_cert(tmp_path: Path) -> None:
    proof, artifact = _temp_valid_proof(tmp_path)
    calls: list[tuple[list[str], dict[str, Any]]] = []

    def runner(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append((command, kwargs))
        return _completed(_verifier_output(proof))

    acceptance = verify_retained_proof(proof, tmp_path, run_command=runner)
    assert acceptance.proof == proof
    assert acceptance.certificate_sha256 == proof.certificate_sha256
    assert len(calls) == 1
    command, kwargs = calls[0]
    assert command[:7] == ["cargo", "run", "--quiet", "-p", "rh_cert", "--", "verify"]
    assert command[-3:] == ["--cert", str(artifact.resolve()), "--json"]
    assert kwargs["cwd"] == tmp_path
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True
    assert kwargs["check"] is False


def test_verifier_exit_one_is_theorem_failure(tmp_path: Path) -> None:
    proof = _first_proof()

    def runner(*_: Any, **__: Any) -> subprocess.CompletedProcess[str]:
        return _completed({}, returncode=1, stderr="not positive")

    with pytest.raises(RetainedProofTheoremFailure, match="theorem failure"):
        replay_retained_certificate(proof, tmp_path / "proof.json", tmp_path, run_command=runner)


def test_other_nonzero_verifier_exit_is_verifier_error(tmp_path: Path) -> None:
    proof = _first_proof()

    def runner(*_: Any, **__: Any) -> subprocess.CompletedProcess[str]:
        return _completed({}, returncode=2, stderr="contract/runtime error")

    with pytest.raises(RetainedProofVerifierError, match="exited 2"):
        replay_retained_certificate(proof, tmp_path / "proof.json", tmp_path, run_command=runner)


def test_invalid_verifier_json_is_rejected(tmp_path: Path) -> None:
    proof = _first_proof()

    def runner(*_: Any, **__: Any) -> subprocess.CompletedProcess[str]:
        return _completed("not-json")

    with pytest.raises(RetainedProofVerifierError, match="valid unambiguous JSON"):
        replay_retained_certificate(proof, tmp_path / "proof.json", tmp_path, run_command=runner)


def test_verifier_passed_false_is_theorem_failure(tmp_path: Path) -> None:
    proof = _first_proof()

    def runner(*_: Any, **__: Any) -> subprocess.CompletedProcess[str]:
        return _completed(_verifier_output(proof, passed=False))

    with pytest.raises(RetainedProofTheoremFailure, match="passed=true"):
        replay_retained_certificate(proof, tmp_path / "proof.json", tmp_path, run_command=runner)


def test_verifier_identity_field_must_be_present(tmp_path: Path) -> None:
    proof = _first_proof()
    output = _verifier_output(proof)
    del output["verified_scope"]

    def runner(*_: Any, **__: Any) -> subprocess.CompletedProcess[str]:
        return _completed(output)

    with pytest.raises(RetainedProofSemanticMismatch, match="missing required identity field 'verified_scope'"):
        replay_retained_certificate(proof, tmp_path / "proof.json", tmp_path, run_command=runner)


@pytest.mark.parametrize(
    ("field", "wrong_value"),
    [
        ("claim", "C-9999"),
        ("support_T", "2/5"),
        ("dimension", 999),
        ("claim_profile", "synthetic_matrix"),
        ("verified_scope", "localized_weil_positivity_T_2_5"),
    ],
)
def test_verifier_identity_must_match_manifest(field: str, wrong_value: object, tmp_path: Path) -> None:
    proof = _first_proof()

    def runner(*_: Any, **__: Any) -> subprocess.CompletedProcess[str]:
        return _completed(_verifier_output(proof, **{field: wrong_value}))

    with pytest.raises(RetainedProofSemanticMismatch, match=field):
        replay_retained_certificate(proof, tmp_path / "proof.json", tmp_path, run_command=runner)


@pytest.mark.parametrize(
    ("field", "wrong_value"),
    [
        ("support_t", "2/5"),
        ("dimension", 40),
        ("verified_scope", "localized_weil_positivity_T_2_5"),
    ],
)
def test_manifest_identity_mismatch_is_semantic_failure_after_hash_pass(
    field: str,
    wrong_value: object,
    tmp_path: Path,
) -> None:
    proof, _ = _temp_valid_proof(tmp_path)
    expected_by_verifier = proof
    wrong_manifest_proof = replace(proof, **{field: wrong_value})

    def runner(*_: Any, **__: Any) -> subprocess.CompletedProcess[str]:
        return _completed(_verifier_output(expected_by_verifier))

    result = check_retained_proof(wrong_manifest_proof, tmp_path, run_command=runner)
    assert result.stage == "SEMANTIC_MISMATCH"


def test_all_operational_failure_stages_are_explicit(tmp_path: Path) -> None:
    proof, _ = _temp_valid_proof(tmp_path)

    def theorem_runner(*_: Any, **__: Any) -> subprocess.CompletedProcess[str]:
        return _completed(_verifier_output(proof, passed=False))

    def error_runner(*_: Any, **__: Any) -> subprocess.CompletedProcess[str]:
        return _completed({}, returncode=2, stderr="error")

    def semantic_runner(*_: Any, **__: Any) -> subprocess.CompletedProcess[str]:
        return _completed(_verifier_output(proof, dimension=999))

    assert check_retained_proof(proof, tmp_path, run_command=theorem_runner).stage == "THEOREM_FAILURE"
    assert check_retained_proof(proof, tmp_path, run_command=error_runner).stage == "VERIFIER_ERROR"
    assert check_retained_proof(proof, tmp_path, run_command=semantic_runner).stage == "SEMANTIC_MISMATCH"


def test_main_returns_one_and_reports_every_result_on_mixed_failure(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    manifest = load_retained_proof_manifest()
    results = tuple(
        RetainedProofResult(
            proof=proof,
            stage="HASH_MISMATCH" if index == 0 else "PASS",
            detail="tampered" if index == 0 else "",
            hash_passed=index != 0,
        )
        for index, proof in enumerate(manifest.proofs)
    )
    monkeypatch.setattr(
        "scripts.cert.verify_retained_proofs.load_retained_proof_manifest",
        lambda _: manifest,
    )
    monkeypatch.setattr(
        "scripts.cert.verify_retained_proofs.check_retained_proof_manifest",
        lambda *_, **__: results,
    )

    assert main([]) == 1
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    for proof in manifest.proofs:
        assert proof.claim in combined
    assert "HASH_MISMATCH" in combined
    assert "RETAINED PROOF CHAIN: FAIL - 6/7" in combined


def test_main_returns_zero_only_when_every_registered_proof_passes(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    manifest = load_retained_proof_manifest()
    results = tuple(
        RetainedProofResult(proof=proof, stage="PASS", hash_passed=True)
        for proof in manifest.proofs
    )
    monkeypatch.setattr(
        "scripts.cert.verify_retained_proofs.load_retained_proof_manifest",
        lambda _: manifest,
    )
    monkeypatch.setattr(
        "scripts.cert.verify_retained_proofs.check_retained_proof_manifest",
        lambda *_, **__: results,
    )

    assert main([]) == 0
    captured = capsys.readouterr()
    assert "RETAINED PROOF CHAIN: PASS - 7/7" in captured.out
    assert captured.err == ""


def test_manifest_check_continues_after_failure_and_reports_all_results(tmp_path: Path) -> None:
    first_raw = b"one"
    second_raw = b"two"
    (tmp_path / "one.json").write_bytes(first_raw)
    (tmp_path / "two.json").write_bytes(second_raw)
    base = _first_proof()
    first = replace(
        base,
        claim="C-0050",
        certificate_path="one.json",
        certificate_sha256=hashlib.sha256(b"wrong").hexdigest(),
    )
    second = replace(
        base,
        claim="C-0051",
        certificate_path="two.json",
        certificate_sha256=hashlib.sha256(second_raw).hexdigest(),
    )
    manifest = RetainedProofManifest(format=MANIFEST_FORMAT_V1, proofs=(first, second))
    calls: list[str] = []

    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        certificate = Path(command[-2]).name
        calls.append(certificate)
        return _completed(_verifier_output(second))

    results = check_retained_proof_manifest(manifest, tmp_path, run_command=runner)
    assert [result.stage for result in results] == ["HASH_MISMATCH", "PASS"]
    assert calls == ["two.json"]
    assert "HASH_MISMATCH" in format_retained_proof_result(results[0])
    assert format_retained_proof_result(results[1]).startswith("C-0051 HASH PASS VERIFY PASS")
