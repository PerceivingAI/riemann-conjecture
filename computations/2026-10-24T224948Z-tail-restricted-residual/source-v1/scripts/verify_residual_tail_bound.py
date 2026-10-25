"""Independent research audit of C-0088 scalar output, not a positivity verifier.

Reconstructs coefficients, transcendental bounds and cutoffs without importing
scripts.weil_residual_tail_bound. Finite controls supplement, not prove, the
infinite-tail argument in F-20261024-007.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

from flint import arb, ctx, fmpq, fmpq_mat, fmpq_poly

from scripts import verify_combined_schur_analytic_entries as native

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "computations/2026-10-24T191616Z-weighted-support-extension/data/selection-v1.json"
BASELINE_SHA256 = "e120acab4919b9ab28e6fd6c7044053bb14514f300d810952a2d52e5dae6d7a3"
EXPECTED_SOURCES = (
    "scripts/weil_residual_tail_bound.py", "scripts/cert/constants.py",
    "scripts/cert/multi_prime_legendre_schur.py", "scripts/cert/prime_power_terms.py",
    "scripts/cert/residual_kernel.py",
)


def smoothing_upper(coefficients: list[fmpq], n: int) -> fmpq:
    # Separate multiplication, first-derivative and second-derivative bounds.
    total = 2*abs(coefficients[1]) if len(coefficients) > 1 else fmpq(0)
    for d, coefficient in enumerate(coefficients):
        if d == 0 or (d % 2 == 0 and d < 2*n):
            continue
        total += 2*d*abs(coefficient)*fmpq(2**d, d)
        if d >= 2:
            total += d*(d-1)*abs(coefficient)*fmpq(2**(d-1), d-1)
    return total


def inner(left: fmpq_poly, right: fmpq_poly) -> fmpq:
    primitive = (left*right).integral()
    return primitive(1)-primitive(-1)


def kernel_image(coefficients: list[fmpq], poly: fmpq_poly) -> fmpq_poly:
    return sum((c*v*native.monomial_kernel_power(d, k)
                for d, c in enumerate(coefficients) if c
                for k, v in enumerate(poly.coeffs()) if v), fmpq_poly())


def project_tail(poly: fmpq_poly, n: int) -> fmpq_poly:
    return poly-sum((p*inner(p, poly)*fmpq(2*j+1, 2)
                     for j, p in enumerate(native.poly_basis(n))), fmpq_poly())


def finite_controls() -> dict:
    x = fmpq_poly([0, 1])
    one = fmpq_poly([1])
    cusp = []
    for f, expected in ((one, 6*x*x-2), (x, 4*x**3-4*x)):
        image = kernel_image([fmpq(0), fmpq(1)], f)
        actual = 2*x*image.derivative()-(one-x*x)*image.derivative().derivative()
        regular_only = 2*x*image.derivative()
        with_cusp = regular_only-2*(one-x*x)*f
        if actual != expected or actual != with_cusp or actual == regular_only:
            raise ValueError("cusp/distributional derivative control failed")
        cusp.append({"input": str(f), "image": str(image), "L_image": str(actual)})
    degree_four = [fmpq(0)]*4+[fmpq(1)]
    p2 = native.poly_basis(3)[2]
    boundary_image = project_tail(kernel_image(degree_four, p2), 2)
    if boundary_image != fmpq(16, 15)*p2:
        raise ValueError("degree 2N boundary was incorrectly removed")
    if any(project_tail(kernel_image(degree_four, p), 3)
           for p in native.poly_basis(5)[3:]):
        raise ValueError("even polynomial annihilation failed")
    # Polynomial input images have no omitted output coefficients. Check the
    # full projected image Gram, not just the matching finite output block.
    coeff = [fmpq(3), fmpq(-1), fmpq(2, 7), fmpq(1, 20), fmpq(-1, 11), fmpq(-1, 300)]
    n = 3
    basis = native.poly_basis(7)[n:]
    images = [project_tail(kernel_image(coeff, p), n) for p in basis]
    radius = smoothing_upper(coeff, n)/(n*(n+1))
    slack = fmpq_mat([[((radius*radius*fmpq(2, 2*(n+i)+1)) if i == j else 0)-inner(a, b)
                       for j, b in enumerate(images)] for i, a in enumerate(images)])
    minors = [fmpq_mat([[slack[i, j] for j in range(k)] for i in range(k)]).det()
              for k in range(1, len(images)+1)]
    if not all(value > 0 for value in minors):
        raise ValueError("signed-kernel complete-image norm control failed")
    return {"cusp_identities": cusp, "degree_four_N2_eigenvalue_exact": "16/15",
            "degree_four_N3_zero": True, "signed_complete_image_slack_minors": list(map(str, minors))}


def audit(path: Path) -> dict:
    raw = path.read_bytes()
    obj = json.loads(raw)
    required = {"format": "research-residual-tail-scalar-v1", "support": [1353, 2048],
                "residual_order": 38, "current_dimension": 312, "active_terms": [2, 3],
                "arb_precision_bits": 512, "outward_bits": 352,
                "baseline_path": BASELINE, "baseline_sha256": BASELINE_SHA256}
    if any(obj.get(key) != value for key, value in required.items()):
        raise ValueError("unexpected scalar research parameters")
    baseline_raw = (ROOT/BASELINE).read_bytes()
    if hashlib.sha256(baseline_raw).hexdigest() != BASELINE_SHA256:
        raise ValueError("retained baseline bytes changed")
    baseline = json.loads(baseline_raw)
    reserve = fmpq(baseline["mu_reference_exact"])
    if obj["reserve_exact"] != str(reserve):
        raise ValueError("reference reserve changed")
    sources = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in EXPECTED_SOURCES}
    if obj["sources"] != sources:
        raise ValueError("source fingerprints changed")
    t_exact = fmpq(1353, 2048)
    a = native.exact_residual_coefficients(38)
    coefficients = [-value*t_exact**(d+1) for d, value in enumerate(a)]
    if obj["kernel_coefficients_exact"] != list(map(str, coefficients)):
        raise ValueError("kernel coefficient reconstruction failed")
    containment = {}
    with ctx.workprec(1024):
        t = native.qarb(t_exact)
        if not (arb(3).log() < 2*t < arb(4).log() and 1 < arb(2).log()/t < arb(3).log()/t < 2):
            raise ValueError("independent strict arithmetic window failed")
        delta, full = native.bound_tail(t, a, 38)
        fresh = {"c_T": (2*arb.pi()*t).log()+arb.const_euler(),
                 "arithmetic": arb(2).log()/arb(2).sqrt()+arb(3).log()/arb(3).sqrt(),
                 "delta": delta, "rho_global": full}
        if set(obj["scalars"]) != set(fresh):
            raise ValueError("unexpected scalar fields")
        for name, value in fresh.items():
            lower, upper = native.endpoints(value)
            stored_lower, stored_upper = map(Q, obj["scalars"][name])
            if not stored_lower < lower <= upper < stored_upper:
                raise ValueError(f"fresh scalar is not strictly contained: {name}")
            containment[name] = [str(lower), str(upper)]
    charges = {key: fmpq(value[1]) for key, value in obj["scalars"].items()}
    costs = charges["c_T"]+charges["arithmetic"]
    cutoffs = {}
    recomputed = {}
    n = 0
    while len(cutoffs) < 8 or n < 312:
        n += 1
        constant = smoothing_upper(coefficients, n)
        rho = charges["delta"]+constant/fmpq(n*(n+1))
        mu_full = native.harmonic(n)-costs-charges["rho_global"]
        mu_tail = native.harmonic(n)-costs-rho
        for label, value in (("global", mu_full), ("tail", mu_tail)):
            for target, valid in (("positive", value > 0), ("reserve", value >= reserve)):
                if valid:
                    cutoffs.setdefault(f"{label}_{target}", n)
                    if n % 2 == 0:
                        cutoffs.setdefault(f"{label}_{target}_even", n)
        recomputed[n] = {"dimension": n, "M_exact": str(constant),
                         "rho_tail_upper_exact": str(rho), "mu_global_lower_exact": str(mu_full),
                         "mu_tail_lower_exact": str(mu_tail)}
    if obj["cutoffs"] != cutoffs:
        raise ValueError("scalar cutoff reconstruction failed")
    selected = {312}
    for value in cutoffs.values():
        selected.update((max(1, value-1), value))
    if obj["rows"] != [recomputed[n] for n in sorted(selected)]:
        raise ValueError("exact scalar comparison rows changed")
    return {"status": "PASS", "scope": "independent scalar reconstruction only; not low-block positivity",
            "input_sha256": hashlib.sha256(raw).hexdigest(), "independent_precision_bits": 1024,
            "fresh_scalar_intervals": containment, "coefficients_checked": len(coefficients),
            "dimensions_checked": n, "cutoffs": cutoffs, "finite_controls": finite_controls(),
            "audit_sources": {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in (
                "scripts/verify_residual_tail_bound.py", "scripts/verify_combined_schur_analytic_entries.py")}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.input)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "dimensions_checked": result["dimensions_checked"],
                      "cutoffs": result["cutoffs"]}, indent=2))


if __name__ == "__main__":
    main()
