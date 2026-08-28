"""Validate and replay the explicit retained-proof manifest.

The manifest is a closed whitelist of the exact proof-bearing certificate
artifacts cited by this repository. Validation is deliberately layered:

1. validate the manifest contract without touching certificate files;
2. resolve each registered repository-relative path and verify its raw-byte
   SHA-256 before any theorem replay;
3. invoke the independent zero-float Rust verifier only for hash-valid
   artifacts and require exact theorem-identity agreement with the manifest.

This command never regenerates certificates. Its full acceptance mode is
fail-closed per artifact but exhaustive across the manifest: one broken proof
does not prevent the remaining registered proofs from being checked.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Literal


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = REPOSITORY_ROOT / "computations" / "retained-proofs.json"
MANIFEST_FORMAT_V1 = "rh-retained-proofs-v1"
EXACT_PRIME_PROFILE = "exact_prime_legendre_schur"
EXPECTED_RETAINED_CLAIMS_V1 = frozenset({"C-0050", "C-0051", "C-0052", "C-0053", "C-0054", "C-0055", "C-0056"})
DEFAULT_VERIFIER_TIMEOUT_SECONDS = 600

_TOP_LEVEL_FIELDS = frozenset({"format", "proofs"})
_PROOF_FIELDS = frozenset(
    {
        "claim",
        "computation_id",
        "certificate_path",
        "certificate_sha256",
        "support_T",
        "dimension",
        "claim_profile",
        "verified_scope",
    }
)
_CLAIM_RE = re.compile(r"^C-[0-9]{4}$")
_COMPUTATION_RE = re.compile(r"^X-[0-9]{8}-[0-9]{3}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SUPPORT_RE = re.compile(r"^([1-9][0-9]*)/([1-9][0-9]*)$")
_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")

_RunCommand = Callable[..., subprocess.CompletedProcess[str]]
AcceptanceStage = Literal[
    "PASS",
    "MISSING",
    "HASH_MISMATCH",
    "VERIFIER_ERROR",
    "THEOREM_FAILURE",
    "SEMANTIC_MISMATCH",
]


class RetainedProofManifestError(ValueError):
    """Raised when the retained-proof manifest violates its closed v1 contract."""


class RetainedProofAcceptanceError(RuntimeError):
    """Base class for a retained artifact or verifier acceptance failure."""


class RetainedProofArtifactError(RetainedProofAcceptanceError):
    """Raised when a registered certificate cannot be safely resolved as a file."""


class RetainedProofMissing(RetainedProofArtifactError):
    """Raised when a registered retained certificate does not exist."""


class RetainedProofHashMismatch(RetainedProofAcceptanceError):
    """Raised when a retained certificate no longer has its registered SHA-256."""


class RetainedProofVerifierError(RetainedProofAcceptanceError):
    """Raised when the independent verifier cannot produce trustworthy JSON output."""


class RetainedProofTheoremFailure(RetainedProofAcceptanceError):
    """Raised when the independent verifier reaches theorem checking and returns failure."""


class RetainedProofSemanticMismatch(RetainedProofAcceptanceError):
    """Raised when verifier theorem identity differs from the retained manifest."""


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build a JSON object while rejecting duplicate keys at any nesting level."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RetainedProofManifestError(f"JSON contains duplicate object key '{key}'")
        result[key] = value
    return result


@dataclass(frozen=True, slots=True)
class RetainedProof:
    claim: str
    computation_id: str
    certificate_path: str
    certificate_sha256: str
    support_t: str
    dimension: int
    claim_profile: str
    verified_scope: str


@dataclass(frozen=True, slots=True)
class RetainedProofManifest:
    format: str
    proofs: tuple[RetainedProof, ...]


@dataclass(frozen=True, slots=True)
class RetainedProofAcceptance:
    """Successful integrity and independent-verifier acceptance for one proof."""

    proof: RetainedProof
    certificate_path: Path
    certificate_sha256: str
    verifier_output: dict[str, Any]


@dataclass(frozen=True, slots=True)
class RetainedProofResult:
    """Operational result for one registered theorem artifact."""

    proof: RetainedProof
    stage: AcceptanceStage
    detail: str = ""
    hash_passed: bool = False
    acceptance: RetainedProofAcceptance | None = None

    @property
    def passed(self) -> bool:
        return self.stage == "PASS"


def _require_exact_fields(value: dict[str, Any], required: frozenset[str], path: str) -> None:
    fields = set(value)
    missing = sorted(required - fields)
    unexpected = sorted(fields - required)
    if missing:
        raise RetainedProofManifestError(f"{path} is missing required field(s): {', '.join(missing)}")
    if unexpected:
        raise RetainedProofManifestError(f"{path} contains unexpected field(s): {', '.join(unexpected)}")


def _require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise RetainedProofManifestError(f"{path} must be a non-empty string")
    return value


def _validate_repository_relative_path(value: Any, path: str) -> str:
    raw = _require_string(value, path)
    if "\\" in raw:
        raise RetainedProofManifestError(f"{path} must use forward slashes")
    if _WINDOWS_DRIVE_RE.match(raw):
        raise RetainedProofManifestError(f"{path} must be repository-relative, not drive-qualified")

    parsed = PurePosixPath(raw)
    if parsed.is_absolute():
        raise RetainedProofManifestError(f"{path} must be repository-relative")
    if any(part in {".", ".."} for part in parsed.parts):
        raise RetainedProofManifestError(f"{path} must not contain '.' or '..' segments")
    if raw != parsed.as_posix():
        raise RetainedProofManifestError(f"{path} must be normalized repository-relative POSIX syntax")
    return raw


def _validate_support(value: Any, path: str) -> str:
    raw = _require_string(value, path)
    match = _SUPPORT_RE.fullmatch(raw)
    if match is None:
        raise RetainedProofManifestError(f"{path} must be a positive canonical fraction such as '7/20'")
    support = Fraction(int(match.group(1)), int(match.group(2)))
    canonical = f"{support.numerator}/{support.denominator}"
    if raw != canonical:
        raise RetainedProofManifestError(f"{path} must be reduced canonical fraction '{canonical}'")
    return raw


def _expected_scope(support_t: str) -> str:
    numerator, denominator = support_t.split("/", maxsplit=1)
    return f"localized_weil_positivity_T_{numerator}_{denominator}"


def _validate_proof(value: Any, index: int) -> RetainedProof:
    path = f"$.proofs[{index}]"
    if not isinstance(value, dict):
        raise RetainedProofManifestError(f"{path} must be an object")
    _require_exact_fields(value, _PROOF_FIELDS, path)

    claim = _require_string(value["claim"], f"{path}.claim")
    if _CLAIM_RE.fullmatch(claim) is None:
        raise RetainedProofManifestError(f"{path}.claim must match C-NNNN")

    computation_id = _require_string(value["computation_id"], f"{path}.computation_id")
    if _COMPUTATION_RE.fullmatch(computation_id) is None:
        raise RetainedProofManifestError(f"{path}.computation_id must match X-YYYYMMDD-NNN")

    certificate_path = _validate_repository_relative_path(
        value["certificate_path"], f"{path}.certificate_path"
    )

    certificate_sha256 = _require_string(value["certificate_sha256"], f"{path}.certificate_sha256")
    if _SHA256_RE.fullmatch(certificate_sha256) is None:
        raise RetainedProofManifestError(
            f"{path}.certificate_sha256 must be exactly 64 lowercase hexadecimal characters"
        )

    support_t = _validate_support(value["support_T"], f"{path}.support_T")

    dimension = value["dimension"]
    if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension <= 0:
        raise RetainedProofManifestError(f"{path}.dimension must be a positive integer")

    claim_profile = _require_string(value["claim_profile"], f"{path}.claim_profile")
    if claim_profile != EXACT_PRIME_PROFILE:
        raise RetainedProofManifestError(
            f"{path}.claim_profile must equal '{EXACT_PRIME_PROFILE}'"
        )

    verified_scope = _require_string(value["verified_scope"], f"{path}.verified_scope")
    expected_scope = _expected_scope(support_t)
    if verified_scope != expected_scope:
        raise RetainedProofManifestError(
            f"{path}.verified_scope must equal '{expected_scope}' for support_T={support_t}"
        )

    return RetainedProof(
        claim=claim,
        computation_id=computation_id,
        certificate_path=certificate_path,
        certificate_sha256=certificate_sha256,
        support_t=support_t,
        dimension=dimension,
        claim_profile=claim_profile,
        verified_scope=verified_scope,
    )


def validate_retained_proof_manifest(document: Any) -> RetainedProofManifest:
    """Validate a parsed manifest document without touching certificate artifacts."""
    if not isinstance(document, dict):
        raise RetainedProofManifestError("$ must be an object")
    _require_exact_fields(document, _TOP_LEVEL_FIELDS, "$")

    manifest_format = _require_string(document["format"], "$.format")
    if manifest_format != MANIFEST_FORMAT_V1:
        raise RetainedProofManifestError(f"$.format must equal '{MANIFEST_FORMAT_V1}'")

    proof_values = document["proofs"]
    if not isinstance(proof_values, list):
        raise RetainedProofManifestError("$.proofs must be an array")

    proofs = tuple(_validate_proof(value, index) for index, value in enumerate(proof_values))

    claims = [proof.claim for proof in proofs]
    duplicate_claims = sorted({claim for claim in claims if claims.count(claim) > 1})
    if duplicate_claims:
        raise RetainedProofManifestError(f"$.proofs contains duplicate claim(s): {', '.join(duplicate_claims)}")

    paths = [proof.certificate_path for proof in proofs]
    duplicate_paths = sorted({path for path in paths if paths.count(path) > 1})
    if duplicate_paths:
        raise RetainedProofManifestError(
            f"$.proofs contains duplicate certificate_path(s): {', '.join(duplicate_paths)}"
        )

    claim_set = frozenset(claims)
    if claim_set != EXPECTED_RETAINED_CLAIMS_V1:
        missing = sorted(EXPECTED_RETAINED_CLAIMS_V1 - claim_set)
        unexpected = sorted(claim_set - EXPECTED_RETAINED_CLAIMS_V1)
        details: list[str] = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected {', '.join(unexpected)}")
        raise RetainedProofManifestError(
            "$.proofs must contain exactly C-0050 through C-0056 (" + "; ".join(details) + ")"
        )

    return RetainedProofManifest(format=manifest_format, proofs=proofs)


def load_retained_proof_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> RetainedProofManifest:
    """Load and validate only the manifest JSON; certificate files are not accessed."""
    try:
        document = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_strict_json_object,
        )
    except OSError as error:
        raise RetainedProofManifestError(f"cannot read manifest '{path}': {error}") from error
    except json.JSONDecodeError as error:
        raise RetainedProofManifestError(f"manifest is not valid JSON: {error}") from error
    return validate_retained_proof_manifest(document)


def resolve_retained_certificate_path(
    proof: RetainedProof,
    repository_root: Path = REPOSITORY_ROOT,
) -> Path:
    """Resolve one retained path and prove it names a regular file inside the repository."""
    try:
        root = repository_root.resolve(strict=True)
    except OSError as error:
        raise RetainedProofArtifactError(
            f"{proof.claim}: cannot resolve repository root '{repository_root}': {error}"
        ) from error
    if not root.is_dir():
        raise RetainedProofArtifactError(f"{proof.claim}: repository root is not a directory: '{root}'")

    relative = PurePosixPath(proof.certificate_path)
    candidate = root.joinpath(*relative.parts)
    if candidate.is_symlink():
        raise RetainedProofArtifactError(
            f"{proof.claim}: retained certificate path must not be a symbolic link: '{proof.certificate_path}'"
        )
    if not candidate.exists():
        raise RetainedProofMissing(
            f"{proof.claim}: retained certificate is missing: '{proof.certificate_path}'"
        )
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise RetainedProofArtifactError(
            f"{proof.claim}: retained certificate does not resolve safely: '{proof.certificate_path}': {error}"
        ) from error

    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise RetainedProofArtifactError(
            f"{proof.claim}: retained certificate resolves outside repository root: '{proof.certificate_path}'"
        ) from error

    try:
        mode = resolved.stat().st_mode
    except OSError as error:
        raise RetainedProofArtifactError(
            f"{proof.claim}: cannot stat retained certificate '{proof.certificate_path}': {error}"
        ) from error
    if not stat.S_ISREG(mode):
        raise RetainedProofArtifactError(
            f"{proof.claim}: retained certificate is not a regular file: '{proof.certificate_path}'"
        )
    return resolved


def sha256_raw_file(path: Path) -> str:
    """Return SHA-256 over the artifact's raw bytes without decoding or normalization."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_retained_certificate_integrity(
    proof: RetainedProof,
    repository_root: Path = REPOSITORY_ROOT,
) -> tuple[Path, str]:
    """Resolve and hash one artifact, raising before replay on any integrity failure."""
    certificate_path = resolve_retained_certificate_path(proof, repository_root)
    try:
        actual_sha256 = sha256_raw_file(certificate_path)
    except OSError as error:
        raise RetainedProofArtifactError(
            f"{proof.claim}: cannot read retained certificate bytes: {error}"
        ) from error
    if actual_sha256 != proof.certificate_sha256:
        raise RetainedProofHashMismatch(
            f"{proof.claim}: SHA-256 mismatch for '{proof.certificate_path}': "
            f"expected {proof.certificate_sha256}, got {actual_sha256}"
        )
    return certificate_path, actual_sha256


def _parse_verifier_json(stdout: str, claim: str) -> dict[str, Any]:
    try:
        document = json.loads(stdout, object_pairs_hook=_strict_json_object)
    except (json.JSONDecodeError, RetainedProofManifestError) as error:
        raise RetainedProofVerifierError(
            f"{claim}: rh_cert did not emit valid unambiguous JSON: {error}"
        ) from error
    if not isinstance(document, dict):
        raise RetainedProofVerifierError(f"{claim}: rh_cert JSON output must be an object")
    return document


def replay_retained_certificate(
    proof: RetainedProof,
    certificate_path: Path,
    repository_root: Path = REPOSITORY_ROOT,
    *,
    run_command: _RunCommand = subprocess.run,
    timeout_seconds: int = DEFAULT_VERIFIER_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Replay one hash-valid artifact through the current independent Rust verifier."""
    command = [
        "cargo",
        "run",
        "--quiet",
        "-p",
        "rh_cert",
        "--",
        "verify",
        "--cert",
        str(certificate_path),
        "--json",
    ]
    try:
        completed = run_command(
            command,
            cwd=repository_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise RetainedProofVerifierError(f"{proof.claim}: cannot execute rh_cert: {error}") from error

    if completed.returncode == 1:
        detail = completed.stderr.strip()
        suffix = f": {detail}" if detail else ""
        raise RetainedProofTheoremFailure(
            f"{proof.claim}: rh_cert returned theorem failure (exit 1){suffix}"
        )
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        detail = f": {stderr}" if stderr else ""
        raise RetainedProofVerifierError(
            f"{proof.claim}: rh_cert exited {completed.returncode}, expected 0 or theorem-failure exit 1{detail}"
        )

    output = _parse_verifier_json(completed.stdout, proof.claim)
    if output.get("passed") is not True:
        raise RetainedProofTheoremFailure(f"{proof.claim}: rh_cert output does not contain passed=true")

    expected: dict[str, Any] = {
        "claim": proof.claim,
        "support_T": proof.support_t,
        "dimension": proof.dimension,
        "claim_profile": proof.claim_profile,
        "verified_scope": proof.verified_scope,
    }
    for field, expected_value in expected.items():
        if field not in output:
            raise RetainedProofSemanticMismatch(
                f"{proof.claim}: rh_cert output is missing required identity field '{field}'"
            )
        actual_value = output[field]
        if actual_value != expected_value:
            raise RetainedProofSemanticMismatch(
                f"{proof.claim}: rh_cert identity mismatch for '{field}': "
                f"expected {expected_value!r}, got {actual_value!r}"
            )
    return output


def verify_retained_proof(
    proof: RetainedProof,
    repository_root: Path = REPOSITORY_ROOT,
    *,
    run_command: _RunCommand = subprocess.run,
    timeout_seconds: int = DEFAULT_VERIFIER_TIMEOUT_SECONDS,
) -> RetainedProofAcceptance:
    """Run the P2 integrity gate, then P3 replay only if P2 succeeds."""
    certificate_path, actual_sha256 = verify_retained_certificate_integrity(proof, repository_root)
    verifier_output = replay_retained_certificate(
        proof,
        certificate_path,
        repository_root,
        run_command=run_command,
        timeout_seconds=timeout_seconds,
    )
    return RetainedProofAcceptance(
        proof=proof,
        certificate_path=certificate_path,
        certificate_sha256=actual_sha256,
        verifier_output=verifier_output,
    )


def check_retained_proof(
    proof: RetainedProof,
    repository_root: Path = REPOSITORY_ROOT,
    *,
    run_command: _RunCommand = subprocess.run,
    timeout_seconds: int = DEFAULT_VERIFIER_TIMEOUT_SECONDS,
) -> RetainedProofResult:
    """Return an explicit operational stage instead of leaking acceptance exceptions."""
    try:
        certificate_path, actual_sha256 = verify_retained_certificate_integrity(proof, repository_root)
    except RetainedProofMissing as error:
        return RetainedProofResult(proof=proof, stage="MISSING", detail=str(error))
    except RetainedProofHashMismatch as error:
        return RetainedProofResult(proof=proof, stage="HASH_MISMATCH", detail=str(error))
    except RetainedProofArtifactError as error:
        return RetainedProofResult(proof=proof, stage="VERIFIER_ERROR", detail=str(error))

    try:
        verifier_output = replay_retained_certificate(
            proof,
            certificate_path,
            repository_root,
            run_command=run_command,
            timeout_seconds=timeout_seconds,
        )
    except RetainedProofTheoremFailure as error:
        return RetainedProofResult(
            proof=proof,
            stage="THEOREM_FAILURE",
            detail=str(error),
            hash_passed=True,
        )
    except RetainedProofSemanticMismatch as error:
        return RetainedProofResult(
            proof=proof,
            stage="SEMANTIC_MISMATCH",
            detail=str(error),
            hash_passed=True,
        )
    except RetainedProofVerifierError as error:
        return RetainedProofResult(
            proof=proof,
            stage="VERIFIER_ERROR",
            detail=str(error),
            hash_passed=True,
        )

    acceptance = RetainedProofAcceptance(
        proof=proof,
        certificate_path=certificate_path,
        certificate_sha256=actual_sha256,
        verifier_output=verifier_output,
    )
    return RetainedProofResult(
        proof=proof,
        stage="PASS",
        hash_passed=True,
        acceptance=acceptance,
    )


def check_retained_proof_manifest(
    manifest: RetainedProofManifest,
    repository_root: Path = REPOSITORY_ROOT,
    *,
    run_command: _RunCommand = subprocess.run,
    timeout_seconds: int = DEFAULT_VERIFIER_TIMEOUT_SECONDS,
) -> tuple[RetainedProofResult, ...]:
    """Check every registered proof, continuing after individual artifact failures."""
    return tuple(
        check_retained_proof(
            proof,
            repository_root,
            run_command=run_command,
            timeout_seconds=timeout_seconds,
        )
        for proof in manifest.proofs
    )


def format_retained_proof_result(result: RetainedProofResult) -> str:
    """Format one concise, stage-explicit theorem row for operational use."""
    proof = result.proof
    if result.passed:
        return f"{proof.claim} HASH PASS VERIFY PASS T={proof.support_t} N={proof.dimension}"
    if result.stage in {"MISSING", "HASH_MISMATCH"}:
        return f"{proof.claim} {result.stage} VERIFY SKIPPED T={proof.support_t} N={proof.dimension}: {result.detail}"
    if result.hash_passed:
        return f"{proof.claim} HASH PASS {result.stage} T={proof.support_t} N={proof.dimension}: {result.detail}"
    return f"{proof.claim} {result.stage} VERIFY SKIPPED T={proof.support_t} N={proof.dimension}: {result.detail}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that every registered retained theorem certificate is byte-intact and "
            "accepted by the current independent zero-float Rust verifier."
        )
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help="retained-proof manifest (default: computations/retained-proofs.json)",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="validate only the manifest contract; do not access or replay certificate artifacts",
    )
    parser.add_argument(
        "--verifier-timeout",
        type=int,
        default=DEFAULT_VERIFIER_TIMEOUT_SECONDS,
        help=f"per-artifact rh_cert timeout in seconds (default: {DEFAULT_VERIFIER_TIMEOUT_SECONDS})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.verifier_timeout <= 0:
        print("RETAINED PROOF MANIFEST: INVALID: --verifier-timeout must be positive", file=sys.stderr)
        return 2

    try:
        manifest = load_retained_proof_manifest(args.manifest)
    except RetainedProofManifestError as error:
        print(f"RETAINED PROOF MANIFEST: INVALID: {error}", file=sys.stderr)
        return 2

    if args.manifest_only:
        print(f"RETAINED PROOF MANIFEST: VALID ({len(manifest.proofs)} registered proofs)")
        return 0

    results = check_retained_proof_manifest(
        manifest,
        REPOSITORY_ROOT,
        timeout_seconds=args.verifier_timeout,
    )
    for result in results:
        target = sys.stdout if result.passed else sys.stderr
        print(format_retained_proof_result(result), file=target, flush=True)

    passed = sum(result.passed for result in results)
    total = len(results)
    if passed != total:
        print(f"RETAINED PROOF CHAIN: FAIL - {passed}/{total}", file=sys.stderr, flush=True)
        return 1

    print(f"RETAINED PROOF CHAIN: PASS - {total}/{total}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
