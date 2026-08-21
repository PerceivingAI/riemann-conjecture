"""Export and validate proof certificates conforming to the rh-weil-certificate-v1 format.

This module serializes rigorous interval matrix calculations and mathematical
constants into an auditable JSON artifact with exact rational endpoints.
"""

from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path
from typing import Any

import flint
from flint import arb, ctx

from scripts.cert import __version__
from scripts.cert.constants import get_certified_constants_bundle
from scripts.cert.matrices import RationalIntervalMatrix, verify_matrix_positivity_ldl
from scripts.cert.residual_kernel import digamma_positive_operator_matrix


CERTIFICATE_FORMAT_V1 = "rh-weil-certificate-v1"

REQUIRED_FIELDS = {
    "format",
    "claim",
    "support_T",
    "basis",
    "parity_sector",
    "dimension",
    "constants",
    "matrix",
    "tail_bound",
    "generator_metadata",
}


def validate_certificate_schema(cert: dict[str, Any]) -> tuple[bool, str]:
    """Validate that a certificate dictionary conforms to rh-weil-certificate-v1."""
    missing = REQUIRED_FIELDS - set(cert.keys())
    if missing:
        return False, f"Missing required fields: {sorted(missing)}"

    if cert["format"] != CERTIFICATE_FORMAT_V1:
        return False, f"Unsupported format '{cert['format']}'. Expected '{CERTIFICATE_FORMAT_V1}'."

    dim = cert.get("dimension")
    if not isinstance(dim, int) or dim < 1:
        return False, f"Invalid dimension: {dim}"

    matrix_obj = cert.get("matrix")
    if not isinstance(matrix_obj, dict) or "entries" not in matrix_obj:
        return False, "Matrix object must be a dictionary containing 'entries' list."

    entries = matrix_obj["entries"]
    if not isinstance(entries, list) or len(entries) != dim * dim:
        return False, f"Expected {dim * dim} matrix entries, found {len(entries) if isinstance(entries, list) else 'invalid'}."

    for entry in entries:
        for key in ("row", "col", "lo_num", "lo_den", "hi_num", "hi_den"):
            if key not in entry:
                return False, f"Matrix entry missing key '{key}': {entry}"

    return True, "Certificate conforms to rh-weil-certificate-v1 schema."


def build_certificate(
    claim: str,
    matrix: RationalIntervalMatrix,
    basis_type: str,
    parity_sector: str = "both",
    support_num: int = 7,
    support_den: int = 20,
    tail_bound: dict[str, Any] | None = None,
    prec_bits: int = 128,
) -> dict[str, Any]:
    """Assemble a validated rh-weil-certificate-v1 certificate dictionary."""
    constants_bundle = get_certified_constants_bundle(prec=prec_bits, num=support_num, den=support_den)
    ldl_res = verify_matrix_positivity_ldl(matrix)

    if tail_bound is None:
        tail_bound = {
            "type": "none",
            "description": "Finite block without active tail bound absorption",
        }

    cert: dict[str, Any] = {
        "format": CERTIFICATE_FORMAT_V1,
        "claim": claim,
        "support_T": {
            "num": support_num,
            "den": support_den,
            "frac": f"{support_num}/{support_den}",
        },
        "basis": {
            "type": basis_type,
            "dimension": matrix.dim,
            "domain": "[-T, T]",
        },
        "parity_sector": parity_sector,
        "dimension": matrix.dim,
        "constants": constants_bundle,
        "matrix": {
            "dimension": matrix.dim,
            "is_symmetric": matrix.is_symmetric(),
            "entries": matrix.to_entries(),
        },
        "tail_bound": tail_bound,
        "internal_ldl_verification": ldl_res,
        "generator_metadata": {
            "generator": "scripts.cert",
            "version": __version__,
            "flint_version": flint.__version__,
            "prec_bits": prec_bits,
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
    }

    valid, msg = validate_certificate_schema(cert)
    if not valid:
        raise ValueError(f"Generated certificate failed schema validation: {msg}")

    return cert


def export_digamma_operator_certificate(
    k_max: int = 1,
    dimension: int = 2,
    basis_type: str = "legendre",
    support_num: int = 7,
    support_den: int = 20,
    prec: int = 128,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Generate and optionally export a certificate for the digamma positive operator partial sum."""
    with ctx.workprec(prec):
        t_arb = arb(support_num) / arb(support_den)
        arb_m = digamma_positive_operator_matrix(
            k_max=k_max,
            basis_type=basis_type,
            dim=dimension,
            T_val=t_arb,
            prec=prec,
        )
        rat_matrix = RationalIntervalMatrix.from_arb_mat(arb_m)

        claim = f"Digamma operator partial sum K_max={k_max} on T={support_num}/{support_den}"
        tail_bound = {
            "type": "digamma_tail_bracket_lower_bound",
            "k_max": k_max,
            "description": "Each omitted bracket k > K_max is non-negative on L2([-T,T])",
        }

        cert = build_certificate(
            claim=claim,
            matrix=rat_matrix,
            basis_type=basis_type,
            parity_sector="both",
            support_num=support_num,
            support_den=support_den,
            tail_bound=tail_bound,
            prec_bits=prec,
        )

        if output_path is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")

        return cert


def main() -> None:
    parser = argparse.ArgumentParser(description="Export an exact rational interval certificate.")
    parser.add_argument("--claim", type=str, default="digamma_partial_sum", help="Claim identifier")
    parser.add_argument("--dimension", type=int, default=2, help="Finite block dimension")
    parser.add_argument("--k-max", type=int, default=1, help="Max digamma bracket index")
    parser.add_argument("--basis", type=str, default="legendre", help="Basis type (legendre, chebyshev, monomial)")
    parser.add_argument("--prec", type=int, default=128, help="Precision in bits")
    parser.add_argument("--support-num", type=int, default=7, help="Numerator of support T")
    parser.add_argument("--support-den", type=int, default=20, help="Denominator of support T")
    parser.add_argument("--output-json", type=Path, help="Target JSON output path")
    args = parser.parse_args()

    cert = export_digamma_operator_certificate(
        k_max=args.k_max,
        dimension=args.dimension,
        basis_type=args.basis,
        support_num=args.support_num,
        support_den=args.support_den,
        prec=args.prec,
        output_path=args.output_json,
    )

    print(f"Generated certificate for: {cert['claim']}")
    print(f"Dimension: {cert['dimension']}")
    print(f"Verified positive definite: {cert['internal_ldl_verification']['verified_positive_definite']}")
    if args.output_json:
        print(f"Saved certificate to: {args.output_json}")


if __name__ == "__main__":
    main()
