"""Generate the exact-prime Legendre-Schur certificate for A-20260821-004.

The analytic matrices are assembled with exact Fraction polynomial algebra and
Arb enclosures. All serialized matrix intervals are outward-rounded to dyadic
rational endpoints. The congruence witnesses are proposed without floating
point: exact rational midpoint LDL is computed independently on the two parity
blocks, L^{-1} is formed exactly, and its lower-triangular entries are rounded
to dyadic rationals. The witness has no proof authority by itself; the Rust
verifier recomputes the Schur matrix, exact congruence, and Gershgorin margins.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from flint import ctx

from scripts.cert.constants import c2_enclosure, c_T_enclosure
from scripts.cert.exact_prime_schur_common import (
    coarsen_matrix,
    dyadic_outward_interval,
    exact_matrix_json,
    force_exact_parity_zeros,
    interval_matrix_json,
    make_witness,
    parity_block,
    schur_from_serialized_inputs,
)
from scripts.cert.export_certificate import _generator_metadata, validate_certificate_schema
from scripts.cert.legendre_schur import assemble_exact_prime_schur


PROFILE = "exact_prime_legendre_schur"
TAIL_RULE = "legendre_component_gram_schur"
ALLOWED_CONFIGURATIONS = {
    (Fraction(7, 20), 32),
    (Fraction(2, 5), 40),
    (Fraction(17, 40), 48),
    (Fraction(9, 20), 56),
}



def build_exact_prime_schur_certificate(
    *,
    claim: str,
    support_num: int = 7,
    support_den: int = 20,
    dimension: int = 32,
    prec: int = 160,
    residual_order: int = 32,
    matrix_bits: int = 64,
    witness_bits: int = 32,
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    support = Fraction(support_num, support_den)
    if not claim:
        raise ValueError("claim must be non-empty")
    if matrix_bits < 16:
        raise ValueError("matrix_bits must be at least 16")
    if witness_bits < 8:
        raise ValueError("witness_bits must be at least 8")
    if (support, dimension) not in ALLOWED_CONFIGURATIONS:
        allowed = ", ".join(
            f"T={value},N={dim}" for value, dim in sorted(ALLOWED_CONFIGURATIONS)
        )
        raise ValueError(f"v1 exact-prime profile allows only {allowed}")
    if residual_order != 32:
        raise ValueError("v1 exact-prime profile is locked to residual order 32")
    if prec < 128:
        raise ValueError("precision must be at least 128 bits")

    with ctx.workprec(prec):
        assembled = assemble_exact_prime_schur(
            n=dimension,
            prec=prec,
            residual_order=residual_order,
            support_num=support.numerator,
            support_den=support.denominator,
        )
        a_matrix = force_exact_parity_zeros(coarsen_matrix(assembled["A"], matrix_bits))
        gv = force_exact_parity_zeros(coarsen_matrix(assembled["GV"], matrix_bits))
        g2 = force_exact_parity_zeros(coarsen_matrix(assembled["G2"], matrix_bits))
        gr = force_exact_parity_zeros(coarsen_matrix(assembled["GR"], matrix_bits))
        c_t = dyadic_outward_interval(
            c_T_enclosure(prec, support.numerator, support.denominator), matrix_bits
        )
        c2 = dyadic_outward_interval(c2_enclosure(prec), matrix_bits)
        rho_r = dyadic_outward_interval(assembled["rho_R"], matrix_bits)

    schur, mu_lower = schur_from_serialized_inputs(
        a_matrix,
        gv,
        g2,
        gr,
        c_t,
        c2,
        rho_r,
        dimension,
    )
    even_witness, even_margin = make_witness(parity_block(schur, 0), witness_bits)
    odd_witness, odd_margin = make_witness(parity_block(schur, 1), witness_bits)

    certificate: dict[str, Any] = {
        "format": "rh-weil-certificate-v1",
        "claim": claim,
        "claim_profile": PROFILE,
        "support_T": {
            "num": str(support.numerator),
            "den": str(support.denominator),
            "frac": f"{support.numerator}/{support.denominator}",
        },
        "basis": {
            "type": "legendre",
            "dimension": dimension,
            "domain": "[-1, 1]",
        },
        "parity_sector": "both",
        "dimension": dimension,
        "constants": {
            "c2": c2.to_dict(),
            "c_T": c_t.to_dict(),
            "rho_R": rho_r.to_dict(),
        },
        "matrix": interval_matrix_json(a_matrix),
        "tail_bound": {
            "type": TAIL_RULE,
            "harmonic_index": dimension,
            "factor": {"num": "3", "den": "1"},
        },
        "schur_proof": {
            "residual_order": residual_order,
            "GV": interval_matrix_json(gv),
            "G2": interval_matrix_json(g2),
            "GR": interval_matrix_json(gr),
            "even_witness": exact_matrix_json(even_witness),
            "odd_witness": exact_matrix_json(odd_witness),
        },
        "generator_metadata": _generator_metadata(
            prec,
            script="scripts.cert.exact_prime_schur_certificate",
        ),
    }

    valid, message = validate_certificate_schema(certificate)
    if not valid:
        raise ValueError(f"generated exact-prime certificate failed validation: {message}")

    diagnostics = {
        "mu_lower": mu_lower,
        "even_gershgorin_margin": even_margin,
        "odd_gershgorin_margin": odd_margin,
    }
    return certificate, diagnostics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim", default="C-0050")
    parser.add_argument("--support", default="7/20")
    parser.add_argument("--dimension", type=int, default=32)
    parser.add_argument("--prec", type=int, default=160)
    parser.add_argument("--matrix-bits", type=int, default=64)
    parser.add_argument("--witness-bits", type=int, default=32)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    support = Fraction(args.support)
    certificate, diagnostics = build_exact_prime_schur_certificate(
        claim=args.claim,
        support_num=support.numerator,
        support_den=support.denominator,
        dimension=args.dimension,
        prec=args.prec,
        matrix_bits=args.matrix_bits,
        witness_bits=args.witness_bits,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(certificate, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"certificate={args.output_json}")
    print(f"mu_lower={diagnostics['mu_lower']}")
    print(f"even_gershgorin_margin={diagnostics['even_gershgorin_margin']}")
    print(f"odd_gershgorin_margin={diagnostics['odd_gershgorin_margin']}")


if __name__ == "__main__":
    main()
