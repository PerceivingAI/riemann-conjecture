"""Generate and validate exact `rh-weil-certificate-v1` certificates."""

from __future__ import annotations

import argparse
import datetime
import json
import subprocess
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import flint
from flint import arb, ctx
from jsonschema import Draft202012Validator, FormatChecker

from scripts.cert import __version__
from scripts.cert.constants import get_certified_constants_bundle
from scripts.cert.matrices import RationalIntervalMatrix
from scripts.cert.residual_kernel import digamma_positive_operator_matrix


CERTIFICATE_FORMAT_V1 = "rh-weil-certificate-v1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPOSITORY_ROOT / "docs" / "contracts" / "rh-weil-certificate-v1.json"


def _first_float_path(value: Any, path: str = "$") -> str | None:
    if isinstance(value, float):
        return path
    if isinstance(value, dict):
        for key, child in value.items():
            found = _first_float_path(child, f"{path}.{key}")
            if found is not None:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = _first_float_path(child, f"{path}[{index}]")
            if found is not None:
                return found
    return None


@lru_cache(maxsize=1)
def _certificate_validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _format_schema_error(error: Any) -> str:
    path = "$"
    for part in error.absolute_path:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return f"{path}: {error.message}"


def _parse_canonical_rational(value: dict[str, Any], path: str) -> Fraction:
    numerator = value["num"]
    denominator = value["den"]
    rational = Fraction(int(numerator), int(denominator))
    if str(rational.numerator) != numerator or str(rational.denominator) != denominator:
        raise ValueError(f"{path} must be a reduced canonical rational")
    return rational


def _parse_canonical_interval(value: dict[str, Any], path: str) -> tuple[Fraction, Fraction]:
    lo = _parse_canonical_rational(
        {"num": value["lo_num"], "den": value["lo_den"]},
        f"{path}.lo",
    )
    hi = _parse_canonical_rational(
        {"num": value["hi_num"], "den": value["hi_den"]},
        f"{path}.hi",
    )
    if lo > hi:
        raise ValueError(f"{path} has lower endpoint greater than upper endpoint")
    return lo, hi


def _parse_interval_matrix_object(
    value: dict[str, Any],
    dimension: int,
    path: str,
) -> dict[tuple[int, int], tuple[Fraction, Fraction]]:
    if value["dimension"] != dimension:
        raise ValueError(f"{path}.dimension must equal {dimension}")
    expected_count = dimension * dimension
    entries = value["entries"]
    if len(entries) != expected_count:
        raise ValueError(f"{path}.entries must contain exactly {expected_count} entries")

    matrix: dict[tuple[int, int], tuple[Fraction, Fraction]] = {}
    for index, entry in enumerate(entries):
        row = entry["row"]
        col = entry["col"]
        if row >= dimension or col >= dimension:
            raise ValueError(f"{path}.entries[{index}] coordinate is outside the matrix")
        coordinate = (row, col)
        if coordinate in matrix:
            raise ValueError(f"{path}.entries contains duplicate coordinate {coordinate}")
        matrix[coordinate] = _parse_canonical_interval(entry, f"{path}.entries[{index}]")

    for row in range(dimension):
        for col in range(dimension):
            coordinate = (row, col)
            if coordinate not in matrix:
                raise ValueError(f"{path}.entries is missing coordinate {coordinate}")
            if matrix[coordinate] != matrix[(col, row)]:
                raise ValueError(f"{path} is not exactly symmetric at {coordinate}")
    return matrix


def _parse_exact_witness(
    value: dict[str, Any],
    dimension: int,
    path: str,
) -> dict[tuple[int, int], Fraction]:
    if value["dimension"] != dimension:
        raise ValueError(f"{path}.dimension must equal {dimension}")
    if len(value["entries"]) != dimension * dimension:
        raise ValueError(f"{path}.entries must contain exactly {dimension * dimension} entries")
    matrix: dict[tuple[int, int], Fraction] = {}
    for index, entry in enumerate(value["entries"]):
        row = entry["row"]
        col = entry["col"]
        if row >= dimension or col >= dimension:
            raise ValueError(f"{path}.entries[{index}] coordinate is outside the matrix")
        coordinate = (row, col)
        if coordinate in matrix:
            raise ValueError(f"{path}.entries contains duplicate coordinate {coordinate}")
        matrix[coordinate] = _parse_canonical_rational(entry, f"{path}.entries[{index}]")
    for row in range(dimension):
        for col in range(dimension):
            coordinate = (row, col)
            if coordinate not in matrix:
                raise ValueError(f"{path}.entries is missing coordinate {coordinate}")
            if col > row and matrix[coordinate] != 0:
                raise ValueError(f"{path} must be lower triangular")
        if matrix[(row, row)] == 0:
            raise ValueError(f"{path} diagonal must be nonzero")
    return matrix


def _require_parity_block_diagonal(
    matrix: dict[tuple[int, int], tuple[Fraction, Fraction]],
    dimension: int,
    path: str,
) -> None:
    for row in range(dimension):
        for col in range(dimension):
            if (row % 2) != (col % 2) and matrix[(row, col)] != (Fraction(0), Fraction(0)):
                raise ValueError(f"{path} opposite-parity entry ({row}, {col}) must be exactly zero")


def _validate_certificate_semantics(cert: dict[str, Any]) -> None:
    support = _parse_canonical_rational(cert["support_T"], "$.support_T")
    if support <= 0:
        raise ValueError("$.support_T must be strictly positive")
    expected_frac = f"{support.numerator}/{support.denominator}"
    if cert["support_T"]["frac"] != expected_frac:
        raise ValueError("$.support_T.frac does not equal the canonical num/den value")

    dimension = cert["dimension"]
    if cert["basis"]["dimension"] != dimension:
        raise ValueError("$.basis.dimension must equal $.dimension")
    matrix = _parse_interval_matrix_object(cert["matrix"], dimension, "$.matrix")

    for name, interval in cert["constants"].items():
        _parse_canonical_interval(interval, f"$.constants.{name}")

    profile = cert["claim_profile"]
    tail = cert["tail_bound"]
    if profile == "synthetic_matrix":
        if "schur_proof" in cert:
            raise ValueError("$.schur_proof is only valid for exact_prime_legendre_schur")
        if cert["constants"]:
            raise ValueError("$.constants must be empty for synthetic_matrix")
        if tail["type"] != "exact_scalar_identity":
            raise ValueError("$.tail_bound is incompatible with synthetic_matrix")
        _parse_canonical_rational(tail["lambda"], "$.tail_bound.lambda")
    elif profile == "digamma_finite_block":
        if "schur_proof" in cert:
            raise ValueError("$.schur_proof is only valid for exact_prime_legendre_schur")
        if set(cert["constants"]) != {"m0_digamma"}:
            raise ValueError("$.constants must contain only m0_digamma for digamma_finite_block")
        if cert["basis"]["domain"] != "[-T, T]":
            raise ValueError("$.basis.domain must be [-T, T] for digamma_finite_block")
        if tail["type"] != "nonnegative_digamma_remainder":
            raise ValueError("$.tail_bound is incompatible with digamma_finite_block")
        if tail["first_omitted_k"] != tail["k_max"] + 1:
            raise ValueError("$.tail_bound.first_omitted_k must equal k_max + 1")
    elif profile == "exact_prime_legendre_schur":
        if support != Fraction(7, 20):
            raise ValueError("$.support_T must equal 7/20 for exact-prime profile")
        if dimension != 32:
            raise ValueError("$.dimension must equal 32 for exact-prime profile")
        if cert["basis"] != {"type": "legendre", "dimension": 32, "domain": "[-1, 1]"}:
            raise ValueError("$.basis must be the 32-dimensional Legendre basis on [-1, 1]")
        if cert["parity_sector"] != "both":
            raise ValueError("$.parity_sector must be both for exact-prime profile")
        if set(cert["constants"]) != {"c2", "c_T", "rho_R"}:
            raise ValueError("$.constants must contain exactly c2, c_T, and rho_R")
        if tail["type"] != "legendre_component_gram_schur":
            raise ValueError("$.tail_bound is incompatible with exact-prime profile")
        if tail["harmonic_index"] != dimension:
            raise ValueError("$.tail_bound.harmonic_index must equal dimension")
        if _parse_canonical_rational(tail["factor"], "$.tail_bound.factor") != Fraction(3):
            raise ValueError("$.tail_bound.factor must equal 3")
        proof = cert["schur_proof"]
        if proof["residual_order"] != 32:
            raise ValueError("$.schur_proof.residual_order must equal 32")
        _require_parity_block_diagonal(matrix, dimension, "$.matrix")
        for name in ("GV", "G2", "GR"):
            component = _parse_interval_matrix_object(
                proof[name], dimension, f"$.schur_proof.{name}"
            )
            _require_parity_block_diagonal(
                component, dimension, f"$.schur_proof.{name}"
            )
        _parse_exact_witness(proof["even_witness"], dimension // 2, "$.schur_proof.even_witness")
        _parse_exact_witness(proof["odd_witness"], dimension // 2, "$.schur_proof.odd_witness")
        c2_hi = _parse_canonical_interval(cert["constants"]["c2"], "$.constants.c2")[1]
        c_t_hi = _parse_canonical_interval(cert["constants"]["c_T"], "$.constants.c_T")[1]
        rho_hi = _parse_canonical_interval(cert["constants"]["rho_R"], "$.constants.rho_R")[1]
        harmonic_n = sum((Fraction(1, k) for k in range(1, dimension + 1)), Fraction(0))
        if harmonic_n - c2_hi - c_t_hi - rho_hi <= 0:
            raise ValueError("derived exact-prime complement lower bound must be positive")
    else:
        raise ValueError(f"unsupported claim profile: {profile}")

    timestamp_text = cert["generator_metadata"]["timestamp_utc"]
    try:
        timestamp = datetime.datetime.fromisoformat(
            timestamp_text.removesuffix("Z") + "+00:00"
        )
    except ValueError as error:
        raise ValueError("$.generator_metadata.timestamp_utc is not a valid UTC date") from error
    if timestamp.utcoffset() != datetime.timedelta(0):
        raise ValueError("$.generator_metadata.timestamp_utc must use UTC")


def validate_certificate_schema(cert: dict[str, Any]) -> tuple[bool, str]:
    """Run the canonical JSON Schema and all cross-field semantic checks."""
    float_path = _first_float_path(cert)
    if float_path is not None:
        return False, f"{float_path}: ordinary floating-point data is prohibited"

    try:
        errors = sorted(
            _certificate_validator().iter_errors(cert),
            key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
        )
    except (OSError, json.JSONDecodeError) as error:
        return False, f"Unable to load certificate schema: {error}"

    if errors:
        return False, _format_schema_error(errors[0])

    try:
        _validate_certificate_semantics(cert)
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        return False, str(error)

    return True, "Certificate conforms to rh-weil-certificate-v1."


def _generator_metadata(
    prec_bits: int,
    script: str = "scripts.cert.export_certificate",
) -> dict[str, Any]:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError(f"Unable to collect required Git provenance: {error}") from error

    if len(commit) != 40 or any(ch not in "0123456789abcdef" for ch in commit):
        raise RuntimeError(f"Git returned malformed commit hash: {commit!r}")

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "generator": "scripts.cert",
        "script": script,
        "version": __version__,
        "git_commit": commit,
        "git_dirty": bool(status.strip()),
        "flint_version": flint.__FLINT_VERSION__,
        "python_flint_version": flint.__version__,
        "prec_bits": prec_bits,
        "timestamp_utc": timestamp,
    }


def build_certificate(
    *,
    claim: str,
    claim_profile: str,
    matrix: RationalIntervalMatrix,
    basis_type: str,
    basis_domain: str,
    parity_sector: str,
    support_num: int,
    support_den: int,
    constants: dict[str, dict[str, str]],
    tail_bound: dict[str, Any],
    prec_bits: int,
) -> dict[str, Any]:
    """Assemble and strictly validate one v1 proof certificate."""
    support = Fraction(support_num, support_den)
    cert: dict[str, Any] = {
        "format": CERTIFICATE_FORMAT_V1,
        "claim": claim,
        "claim_profile": claim_profile,
        "support_T": {
            "num": str(support.numerator),
            "den": str(support.denominator),
            "frac": f"{support.numerator}/{support.denominator}",
        },
        "basis": {
            "type": basis_type,
            "dimension": matrix.dim,
            "domain": basis_domain,
        },
        "parity_sector": parity_sector,
        "dimension": matrix.dim,
        "constants": constants,
        "matrix": {
            "dimension": matrix.dim,
            "entries": matrix.to_entries(),
        },
        "tail_bound": tail_bound,
        "generator_metadata": _generator_metadata(prec_bits),
    }

    valid, message = validate_certificate_schema(cert)
    if not valid:
        raise ValueError(f"Generated certificate failed validation: {message}")
    return cert


def export_digamma_operator_certificate(
    *,
    claim: str,
    k_max: int = 1,
    dimension: int = 2,
    basis_type: str = "legendre",
    support_num: int = 7,
    support_den: int = 20,
    prec: int = 128,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Generate a finite-basis digamma certificate with a checked series tail rule."""
    if k_max < 0:
        raise ValueError("k_max must be nonnegative")
    if dimension < 1:
        raise ValueError("dimension must be positive")
    if prec < 32:
        raise ValueError("prec must be at least 32 bits")
    support = Fraction(support_num, support_den)
    if support <= 0:
        raise ValueError("support_T must be strictly positive")

    with ctx.workprec(prec):
        t_arb = arb(support.numerator) / arb(support.denominator)
        arb_matrix = digamma_positive_operator_matrix(
            k_max=k_max,
            basis_type=basis_type,
            dim=dimension,
            T_val=t_arb,
            prec=prec,
        )
        matrix = RationalIntervalMatrix.from_arb_mat(arb_matrix)
        bundle = get_certified_constants_bundle(
            prec=prec,
            num=support.numerator,
            den=support.denominator,
        )
        certificate = build_certificate(
            claim=claim,
            claim_profile="digamma_finite_block",
            matrix=matrix,
            basis_type=basis_type,
            basis_domain="[-T, T]",
            parity_sector="both",
            support_num=support.numerator,
            support_den=support.denominator,
            constants={"m0_digamma": bundle["m0_digamma"]},
            tail_bound={
                "type": "nonnegative_digamma_remainder",
                "k_max": k_max,
                "first_omitted_k": k_max + 1,
            },
            prec_bits=prec,
        )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(certificate, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser(description="Export an exact rational interval certificate.")
    parser.add_argument("--claim", type=str, default="digamma_partial_sum", help="Claim identifier")
    parser.add_argument("--dimension", type=int, default=2, help="Finite block dimension")
    parser.add_argument("--k-max", type=int, default=1, help="Max digamma bracket index")
    parser.add_argument("--basis", type=str, default="legendre", help="Basis type")
    parser.add_argument("--prec", type=int, default=128, help="Precision in bits")
    parser.add_argument("--support-num", type=int, default=7, help="Numerator of support T")
    parser.add_argument("--support-den", type=int, default=20, help="Denominator of support T")
    parser.add_argument("--output-json", type=Path, help="Target JSON output path")
    args = parser.parse_args()

    certificate = export_digamma_operator_certificate(
        claim=args.claim,
        k_max=args.k_max,
        dimension=args.dimension,
        basis_type=args.basis,
        support_num=args.support_num,
        support_den=args.support_den,
        prec=args.prec,
        output_path=args.output_json,
    )
    print(f"Generated certificate for: {certificate['claim']}")
    print(f"Dimension: {certificate['dimension']}")
    print("Verification: run `rh_cert verify --cert <path>` in the independent Rust process")
    if args.output_json:
        print(f"Saved certificate to: {args.output_json}")


if __name__ == "__main__":
    main()
