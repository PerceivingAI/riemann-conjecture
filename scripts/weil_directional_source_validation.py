"""Research-only fixed directional source validation, not a Schur sign test.

Compose existing sparse-basis assemblers and separately reconstructed moments.
No inverse is computed, no Gram is reused from the sparse subspace, and no
positivity/theorem admission follows from accepted source intervals.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import time
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path

from flint import arb, ctx, fmpq, fmpq_poly

from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.legendre_schur import legendre_polynomials
from scripts.cert.multi_prime_legendre_schur import (
    _potential_matrices, _residual_truncation_operator,
)
from scripts.cert.prime_power_terms import (
    _exact_polynomials, assemble_combined_prime_power_operator,
    enumerate_active_prime_power_terms,
)
from scripts.cert.residual_kernel import _suzuki_residual_series_coefficients
import scripts.verify_combined_schur_analytic_entries as reference

INPUT = Path("computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json")
INPUT_SHA256 = "44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b"
DEGREES = tuple(range(193, 211, 2))
BITS = 352
COMPONENTS = ("V", "P2", "P3", "R32", "sum_truncated")
SOURCE_PATHS = (
    "scripts/weil_directional_source_validation.py",
    "scripts/verify_combined_schur_analytic_entries.py",
    "scripts/cert/legendre_schur.py", "scripts/cert/constants.py",
    "scripts/cert/multi_prime_legendre_schur.py",
    "scripts/cert/prime_power_terms.py", "scripts/cert/residual_kernel.py",
    "scripts/cert/mixed_gram_research.py", "scripts/weil_selective_support_probe.py",
    "pyproject.toml", "uv.lock",
)


def _trial(packet: dict) -> tuple[list[Q], Q]:
    z = list(map(Q, packet["trial_rational_vector"]))
    if (len(z) != 192 or sum(bool(x) for x in z) != 96
            or any(z[i] for i in range(0, 192, 2))
            or any((1 << 20) % x.denominator for x in z)):
        raise ValueError("invalid original odd dyadic trial")
    norm = sum((x*x*Q(2, 2*i+1) for i, x in enumerate(z)), Q())
    nl, nu = map(Q, packet["trial_norm_exact_enclosure"])
    if not 0 < nl <= norm <= nu < 1:
        raise ValueError("trial mass norm is not enclosed below one")
    return z, norm


def _load_input(path: Path) -> tuple[dict, list[Q], Q]:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != INPUT_SHA256:
        raise ValueError("original input byte identity mismatch")
    packet = json.loads(raw)
    if (packet["support"], packet["dimension"], packet["K"],
            packet["arb_precision_bits"], packet["active_terms"]) != (
            "3/5", 192, 32, 1024, [2, 3]):
        raise ValueError("original source configuration mismatch")
    for name, digest in packet["source_sha256"].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"original source changed: {name}")
    z, norm = _trial(packet)
    return packet, z, norm


def _ordinary_trial(z: list[Q], basis: list[list[Q]]) -> list[Q]:
    return [sum((a*p[j] for a, p in zip(z, basis) if a and j < len(p)), Q())
            for j in range(len(z))]


def _generate(z: list[Q], degrees: tuple[int, ...], order: int, precision: int):
    """Only raw pairings are used; sparse-space Gram/square outputs are ignored."""
    basis = legendre_polynomials(max(degrees))
    trial = _ordinary_trial(z, basis)
    sparse = [trial, *(basis[k] for k in degrees)]
    with ctx.workprec(precision):
        v, _ = _potential_matrices(sparse, precision)
        images, r, _, delta = _residual_truncation_operator(sparse, order, precision, 3, 5)
        terms = enumerate_active_prime_power_terms(3, 5, precision)
        if [term.m for term in terms] != [2, 3]:
            raise ValueError("unexpected active arithmetic terms")
        p = [assemble_combined_prime_power_operator(sparse, [term], precision).p_matrix
             for term in terms]
        rows = {}
        for i, k in enumerate(degrees, 1):
            scale = (arb(2*k+1)/2).sqrt()
            values = {"V": scale*v[i][0], "P2": scale*p[0][i][0],
                      "P3": scale*p[1][i][0], "R32": scale*r[i][0]}
            values["sum_truncated"] = sum(values.values(), arb(0))
            rows[k] = values
    return rows, trial, images[0], delta


def _reconstruct(z: list[Q], degrees: tuple[int, ...], order: int, precision: int):
    """Direct monomial cell integrals, distinct from local-Legendre shifts."""
    basis = reference.poly_basis(max(degrees)+1)
    u = sum((basis[i]*fmpq(a.numerator, a.denominator)
             for i, a in enumerate(z) if a), fmpq_poly())
    coefficients = reference.exact_residual_coefficients(order)
    if tuple(coefficients) != _suzuki_residual_series_coefficients(order):
        raise ValueError("independent residual coefficients disagree")
    residual = reference.residual_polys([u], order, fmpq(3, 5), coefficients)[0]
    with ctx.workprec(precision):
        t = arb(3)/5
        if not arb(3).log() < 2*t < arb(4).log():
            raise ValueError("independent strict active set failed")
        delta, rho = reference.bound_tail(t, coefficients, order)
        mu = (reference.qarb(reference.harmonic(192)) - (2*arb.pi()*t).log()
              - arb.const_euler() - rho)
        cells = []
        constants = {}
        for m in (2, 3):
            logm = arb(m).log()
            tau, c = logm/t, logm/arb(m).sqrt()
            if not 1 < tau < 2:
                raise ValueError("independent compressed-shift norm not one")
            mu -= c
            constants[m] = {"log": reference.endpoints(logm),
                            "tau": reference.endpoints(tau), "coefficient": reference.endpoints(c)}
            for shift, a, b in ((tau, arb(-1), 1-tau), (-tau, -1+tau, arb(1))):
                shifted = reference.translate(u, shift, len(u))
                moments = reference.integrate_power(a, b, max(degrees)+u.degree())
                cells.append((m, c, shifted, moments))
        vm = reference.global_v_moments(max(degrees)+u.degree())
        rows = {}
        for k in degrees:
            product = basis[k]*u
            values = {"V": sum((reference.qarb(c)*vm[j] for j, c in enumerate(product.coeffs())), arb(0)),
                      "P2": arb(0), "P3": arb(0)}
            for m, c, shifted, moments in cells:
                values[f"P{m}"] -= c*sum(
                    (reference.qarb(a)*b*moments[i+j]
                     for i, a in enumerate(basis[k].coeffs()) if a
                     for j, b in enumerate(shifted) if b != 0), arb(0))
            # Independent exact endpoint integration, not the source inner helper.
            product = basis[k]*residual
            integral = sum((c*fmpq(2, j+1) for j, c in enumerate(product.coeffs())
                            if j % 2 == 0), fmpq(0))
            values["R32"] = reference.qarb(integral)
            scale = (arb(2*k+1)/2).sqrt()
            values = {name: scale*value for name, value in values.items()}
            values["sum_truncated"] = sum(values.values(), arb(0))
            rows[k] = values
    return rows, u, residual, mu, delta, constants


def _component(generated: arb, reconstructed: arb, bits: int = BITS) -> dict:
    lo, hi = arb_to_rational_enclosure(generated)
    rl, rh = reference.endpoints(reconstructed)
    scale = 1 << bits
    lower = (lo*scale).__floor__()-1
    upper = (hi*scale).__ceil__()+1
    pl, ph = Q(lower, scale), Q(upper, scale)
    contained = pl <= rl <= rh <= ph
    overlap = max(lo, rl) <= min(hi, rh)
    # Disjoint unrounded source balls expose a discrepancy even if padding masks it.
    status = ("PASS" if contained and overlap else
              "NUMERICALLY_UNRESOLVED" if overlap else "SOURCE_PROOF_GAP")
    return {"generator_exact": [str(lo), str(hi)], "published_dyadic": [lower, upper],
            "reference_exact": [str(rl), str(rh)], "status": status,
            "unrounded_overlap": overlap, "reference_contained": contained}


def run(path: Path, precision: int = 1024) -> dict:
    if precision not in (1024, 1536):
        raise ValueError("supported precision levels are 1024 and 1536")
    started = time.perf_counter()
    packet, z, norm = _load_input(path)
    fingerprints = {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in SOURCE_PATHS}
    print("INPUT_IDENTITY_ACCEPTED", flush=True)
    generator_start = time.perf_counter()
    generated, u, residual, delta = _generate(z, DEGREES, 32, precision)
    generator_seconds = time.perf_counter()-generator_start
    print("GENERATOR_COMPLETE", round(generator_seconds, 3), flush=True)
    reference_start = time.perf_counter()
    rebuilt, other_u, other_residual, mu, other_delta, constants = _reconstruct(
        z, DEGREES, 32, precision*2)
    if _exact_polynomials([u])[0] != other_u or residual != other_residual:
        raise ValueError("independent exact trial/residual image mismatch")
    mu_lower, _ = reference.endpoints(mu)
    _, delta_upper = reference.endpoints(other_delta)
    stored_delta = Q(packet["delta_upper_exact"])
    if not (0 < Q(packet["mu_lower_exact"]) <= mu_lower
            and delta_upper <= stored_delta
            and arb_to_rational_enclosure(delta)[1] <= stored_delta):
        raise ValueError("inherited scalar source bounds not independently contained")
    with ctx.workprec(precision*2):
        for m, values in constants.items():
            term = next(t for t in enumerate_active_prime_power_terms(3, 5, precision*2) if t.m == m)
            if not all(arb_to_rational_enclosure(value)[0] <= values[name][1]
                       and values[name][0] <= arb_to_rational_enclosure(value)[1]
                       for name, value in (("log", term.log_m), ("tau", term.tau),
                                           ("coefficient", term.coefficient))):
                raise ValueError("independent arithmetic constants disagree")
    checks = {}
    for k in DEGREES:
        row = {name: _component(generated[k][name], rebuilt[k][name]) for name in COMPONENTS}
        pl, ph = row["sum_truncated"]["published_dyadic"]
        row["full_source_interval"] = [str(Q(pl, 1 << BITS)-stored_delta),
                                       str(Q(ph, 1 << BITS)+stored_delta)]
        checks[str(k)] = row
    reference_seconds = time.perf_counter()-reference_start
    statuses = [row[name]["status"] for row in checks.values() for name in COMPONENTS]
    status = ("SOURCE_PROOF_GAP" if "SOURCE_PROOF_GAP" in statuses else
              "NUMERICALLY_UNRESOLVED" if "NUMERICALLY_UNRESOLVED" in statuses else
              "SOURCE_INPUTS_ACCEPTED")
    if any(hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest
           for name, digest in fingerprints.items()):
        raise ValueError("source bytes changed during evaluation")
    return {
        "format": "directional-source-validation-v1", "role": "RESEARCH_ONLY_NOT_A_CERTIFICATE",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status, "support": "3/5", "low_dimension": 192, "residual_order": 32,
        "high_degrees": list(DEGREES), "active_terms": [2, 3], "coordinate_metric": "d_k=2/(2k+1)",
        "input_sha256": INPUT_SHA256, "source_sha256": fingerprints,
        "precision_bits": precision, "reference_precision_bits": precision*2,
        "publication_bits": BITS, "exact_trial_mass_norm": str(norm),
        "trial_parity": "odd", "residual_image_degree": residual.degree(),
        "delta_upper_exact": str(stored_delta), "independent_delta_exact": list(map(str, reference.endpoints(other_delta))),
        "independent_mu_exact": list(map(str, reference.endpoints(mu))),
        "arithmetic_constants_reference": {str(m): {k: list(map(str, pair)) for k, pair in values.items()}
                                           for m, values in constants.items()},
        "moments": checks, "schur_sign_evaluated": False,
        "timing_seconds": {"generator": generator_seconds, "reference_and_checks": reference_seconds,
                           "total": time.perf_counter()-started},
        "environment": {"python": platform.python_version(), "python_flint": importlib.metadata.version("python-flint"),
                        "pid": os.getpid()},
        "limitations": "New moments and scalar prerequisites only. Original A/G remain generator-source-qualified. "
                       "Shared Suzuki identities and Arb arithmetic are trusted. No Schur sign, positivity or theorem admission.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--precision", type=int, choices=(1024, 1536), default=1024)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("preserve existing research output; choose a new path")
    started = time.perf_counter()
    try:
        result = run(args.input, args.precision)
    except (ValueError, KeyError, OSError) as exc:
        result = {"format": "directional-source-validation-v1", "role": "RESEARCH_ONLY_NOT_A_CERTIFICATE",
                  "status": "SOURCE_PROOF_GAP", "error": str(exc), "schur_sign_evaluated": False,
                  "elapsed_seconds": time.perf_counter()-started}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Publish atomically without overwriting an existing run, even on POSIX.
    payload = json.dumps(result, indent=2, sort_keys=True)+"\n"
    temporary = args.output.with_suffix(args.output.suffix+".partial")
    with temporary.open("x", encoding="utf-8") as handle:
        handle.write(payload)
    os.link(temporary, args.output)
    temporary.unlink()
    print("SOURCE_VALIDATION", result["status"], "SECONDS", round(time.perf_counter()-started, 3), flush=True)
    if result["status"] != "SOURCE_INPUTS_ACCEPTED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
