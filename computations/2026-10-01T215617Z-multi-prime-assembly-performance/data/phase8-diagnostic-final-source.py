"""Manual Phase 8 enclosure diagnosis, never continuation or theorem admission.

Compare the production global monomial arithmetic with direct cell-local
monomial and Legendre recurrences, with optional exact grouping of the existing
potential moments. Substitutions are process-local; production is unchanged.
"""

from __future__ import annotations

import argparse
from contextlib import ExitStack
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from flint import arb, arb_poly, ctx, fmpq, fmpq_poly

from scripts.cert import multi_prime_legendre_schur as assembly
from scripts.cert import prime_power_terms as arithmetic
from scripts import weil_multi_prime_support_candidate_check as candidate
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.legendre_schur import legendre_polynomials
from scripts.multi_prime_precision_diagnostics import arb_matrix_exact_width_diagnostics
from scripts.precision_diagnostics import fraction_text
from scripts.profile_multi_prime_assembly import _provenance


class EnclosureProfile:
    def __init__(self):
        self.rows = {}

    def add(self, name, values):
        row = self.rows.setdefault(name, {
            "values": 0, "max_width": Fraction(0), "max_abs_bound": Fraction(0),
        })
        for value in values:
            lo, hi = arb_to_rational_enclosure(value)
            row["values"] += 1
            row["max_width"] = max(row["max_width"], hi - lo)
            row["max_abs_bound"] = max(row["max_abs_bound"], abs(lo), abs(hi))

    def json(self):
        return {name: {key: fraction_text(value) if isinstance(value, Fraction) else value
                       for key, value in row.items()} for name, row in self.rows.items()}


def _matrix_profile(matrix):
    result = arb_matrix_exact_width_diagnostics(matrix)
    profile = EnclosureProfile()
    profile.add("entries", (value for row in matrix for value in row))
    result["max_abs_bound"] = profile.json()["entries"]["max_abs_bound"]
    return result


def _affine_monomials(n, center, radius):
    affine = arb_poly([center, radius])
    polys = [arb_poly([1])]
    if n > 1:
        polys.append(affine)
    for degree in range(1, n - 1):
        polys.append(((2 * degree + 1) * affine * polys[-1] - degree * polys[-2])
                     * (1 / arb(degree + 1)))
    return polys


def _affine_legendre(n, center, radius):
    polys = [[arb(1)]]
    if n > 1:
        polys.append([center, radius])
    for degree in range(1, n - 1):
        previous = polys[-1]
        older = polys[-2]
        affine = [arb(0) for _ in range(degree + 2)]
        for k, coefficient in enumerate(previous):
            affine[k] += center * coefficient
            affine[k + 1] += radius * coefficient * (k + 1) / (2 * k + 1)
            if k:
                affine[k - 1] += radius * coefficient * k / (2 * k + 1)
        polys.append([( (2 * degree + 1) * value
                       - (degree * older[k] if k < len(older) else arb(0))) / (degree + 1)
                      for k, value in enumerate(affine)])
    return polys


def _sample_indices(n):
    return sorted(set([0, n // 2, max(0, n - 2), n - 1]))


def _product_profile(left, right, lower, upper, profile, label):
    product = left * right
    primitive = product.integral()
    lower_value, upper_value = primitive(lower), primitive(upper)
    profile.add(label + "/product_coefficients", product.coeffs())
    profile.add(label + "/primitive_coefficients", primitive.coeffs())
    profile.add(label + "/endpoint_values", [lower_value, upper_value])
    profile.add(label + "/integral", [upper_value - lower_value])


def _local_operator(polys, support_num, support_den, prec, representation, profile):
    n = len(polys)
    # This experiment specifically compares representations of the Legendre
    # basis, not a proposed generic-basis replacement for the production API.
    if list(polys) != legendre_polynomials(n - 1):
        raise ValueError("conditioning experiment requires the canonical Legendre basis")
    terms = arithmetic.enumerate_active_prime_power_terms(support_num, support_den, prec)
    breakpoints = arithmetic._sorted_breakpoints(terms) if terms else (arb(-1), arb(1))
    p_matrix, square = arithmetic._zero_matrix(n), arithmetic._zero_matrix(n)
    norms = tuple(Fraction(2, 2 * k + 1) for k in range(n))
    weights = [arithmetic._arb_fraction(norm) for norm in norms]
    for lower, upper in zip(breakpoints[:-1], breakpoints[1:], strict=True):
        center, radius = (lower + upper) / 2, (upper - lower) / 2
        if not radius > 0:
            raise arithmetic.PiecewiseTopologyError("cannot certify positive cell radius")
        active = []
        for term in terms:
            if arithmetic._activity(center, 1 - term.tau, before=True, term=term):
                active.append((term.tau, -term.coefficient))
            if arithmetic._activity(center, -1 + term.tau, before=False, term=term):
                active.append((-term.tau, -term.coefficient))
        if not active:
            continue
        generate = _affine_monomials if representation == "cell-monomial" else _affine_legendre
        basis = generate(n, center, radius)
        if representation == "cell-monomial":
            images = [arb_poly() for _ in range(n)]
        else:
            images = [[arb(0) for _ in range(k + 1)] for k in range(n)]
        for shift, coefficient in active:
            translated = generate(n, center + shift, radius)
            for k, values in enumerate(translated):
                profile.add("translated_coefficients", values.coeffs() if representation == "cell-monomial" else values)
                if representation == "cell-monomial":
                    images[k] += values * coefficient
                else:
                    for index, value in enumerate(values):
                        images[k][index] += value * coefficient
        for k in range(n):
            profile.add("cell_basis_coefficients", basis[k].coeffs() if representation == "cell-monomial" else basis[k])
            profile.add("combined_image_coefficients", images[k].coeffs() if representation == "cell-monomial" else images[k])
        if representation == "cell-monomial":
            for k in _sample_indices(n):
                _product_profile(basis[k], images[k], arb(-1), arb(1), profile, "sample_low")
                _product_profile(images[k], images[k], arb(-1), arb(1), profile, "sample_square")
            for i in range(n):
                for j in range(i, n):
                    if (i + j) % 2:
                        continue
                    p_value = radius * arithmetic._integrated_product(basis[i], images[j], (arb(-1), arb(1)))
                    square_value = radius * arithmetic._integrated_product(images[i], images[j], (arb(-1), arb(1)))
                    p_matrix[i][j] += p_value
                    square[i][j] += square_value
                    if i != j:
                        p_matrix[j][i] += p_value
                        square[j][i] += square_value
        else:
            for k in _sample_indices(n):
                profile.add("sample_low/diagonal_inner_products", [a * b * weights[t]
                            for t, (a, b) in enumerate(zip(basis[k], images[k], strict=True))])
                profile.add("sample_square/diagonal_inner_products", [b * b * weights[t]
                            for t, b in enumerate(images[k])])
            for i in range(n):
                for j in range(i, n):
                    if (i + j) % 2:
                        continue
                    p_value, square_value = arb(0), arb(0)
                    for k in range(i + 1):
                        p_value += basis[i][k] * images[j][k] * weights[k]
                        square_value += images[i][k] * images[j][k] * weights[k]
                    p_value *= radius
                    square_value *= radius
                    p_matrix[i][j] += p_value
                    square[i][j] += square_value
                    if i != j:
                        p_matrix[j][i] += p_value
                        square[j][i] += square_value
    return SimpleNamespace(terms=terms, p_matrix=p_matrix, p_squared_matrix=square,
                           g_p=arithmetic._tail_gram(p_matrix, square, norms))


def _verify_affine_identity():
    # Exact rational identity checks avoid using production Gram routines.
    base = [fmpq_poly([fmpq(c.numerator, c.denominator) for c in poly])
            for poly in legendre_polynomials(9)]
    center, radius = fmpq(3, 8), fmpq(1, 4)
    affine = fmpq_poly([center, radius])
    exact_coefficients = [[fmpq(1)], [center, radius]]
    for degree in range(1, 9):
        previous, older = exact_coefficients[-1], exact_coefficients[-2]
        coefficients = [fmpq(0) for _ in range(degree + 2)]
        for k, value in enumerate(previous):
            coefficients[k] += center * value
            coefficients[k + 1] += radius * value * fmpq(k + 1, 2 * k + 1)
            if k:
                coefficients[k - 1] += radius * value * fmpq(k, 2 * k + 1)
        exact_coefficients.append([((2 * degree + 1) * value -
            (degree * older[k] if k < len(older) else 0)) / (degree + 1)
            for k, value in enumerate(coefficients)])
    for degree, coefficients in enumerate(exact_coefficients):
        reconstructed = sum((base[k] * c for k, c in enumerate(coefficients)), fmpq_poly())
        assert reconstructed == base[degree](affine)
    for left in exact_coefficients:
        for right in exact_coefficients:
            dot = sum((a * b * fmpq(2, 2 * k + 1)
                       for k, (a, b) in enumerate(zip(left, right))), fmpq(0))
            l_poly = sum((base[k] * c for k, c in enumerate(left)), fmpq_poly())
            r_poly = sum((base[k] * c for k, c in enumerate(right)), fmpq_poly())
            primitive = (l_poly * r_poly).integral()
            assert dot == primitive(1) - primitive(-1)
    return {"status": "PASS", "exact_affine_degrees": [0, 9], "exact_inner_product_pairs": 100}


def _grouped_potential(polys, prec, profile):
    exact = arithmetic._exact_polynomials(polys)
    parities = arithmetic._polynomial_parities(polys)
    max_power = 2 * max(poly.degree() for poly in exact)
    harmonic, harmonic2 = [fmpq(0)], [fmpq(0)]
    for k in range(1, max_power + 3):
        harmonic.append(harmonic[-1] + fmpq(1, k))
        harmonic2.append(harmonic2[-1] + fmpq(1, k * k))
    moments = []
    for power in range(max_power + 1):
        if power % 2:
            moments.append((fmpq(0), fmpq(0), fmpq(0)))
            continue
        r = power // 2
        alpha = 2 * harmonic[2 * r + 2] - harmonic[r + 1]
        beta = 4 * harmonic2[2 * r + 2] - harmonic2[r + 1]
        moments.append((fmpq(1, power + 1), alpha / (power + 1),
                        (alpha * alpha + beta) / (power + 1)))
    low, square = arithmetic._zero_matrix(len(polys)), arithmetic._zero_matrix(len(polys))
    with ctx.workprec(prec):
        log2, pi = arb.const_log2(), arb.pi()
        for i, left in enumerate(exact):
            for j in range(i, len(exact)):
                if arithmetic._opposite_parity(parities[i], parities[j]):
                    continue
                u, a, b = fmpq(0), fmpq(0), fmpq(0)
                for k, coefficient in enumerate((left * exact[j]).coeffs()):
                    if coefficient:
                        u += coefficient * moments[k][0]
                        a += coefficient * moments[k][1]
                        b += coefficient * moments[k][2]
                u_arb, a_arb, b_arb = arb(u), arb(a), arb(b)
                profile.add("potential/grouped_coefficients", [u_arb, a_arb, b_arb])
                low[i][j] = low[j][i] = a_arb - 2 * u_arb * log2
                square[i][j] = square[j][i] = (
                    2 * u_arb * log2 * log2 - 2 * a_arb * log2
                    + b_arb / 2 - u_arb * pi * pi / 6
                )
        profile.add("potential/V", (value for row in low for value in row))
        profile.add("potential/V_squared", (value for row in square for value in row))
    return low, square


def run_sample(n, support, precision, representation, residual_order, witness, grouped_potential=False,
               matrix_bits=64, witness_bits=32):
    profile = EnclosureProfile()
    original_operator = assembly.assemble_active_prime_power_operator
    original_shift = arithmetic._arb_poly_shift
    original_potential = assembly._potential_matrices
    potential_comparison = None

    def potential(polys, prec):
        nonlocal potential_comparison
        low, square = _grouped_potential(polys, prec, profile)
        if n <= 32:
            reference_low, reference_square = original_potential(polys, prec)
            potential_comparison = all(
                reference[i][j].overlaps(actual[i][j])
                for reference, actual in ((reference_low, low), (reference_square, square))
                for i in range(n) for j in range(n)
            )
            if not potential_comparison:
                raise RuntimeError("exact grouped potential does not overlap original moments")
        return low, square
    captured = []

    def observe_shift(poly, shift):
        values = original_shift(poly, shift)
        profile.add("translated_coefficients", values)
        return values

    def operator(polys, support_num, support_den, prec):
        exact_values = [c for poly in polys for c in poly]
        basis_metadata = {
            "coefficient_width": "0/1", "max_exact_abs_coefficient": fraction_text(max(map(abs, exact_values))),
            "max_numerator_bits": max(abs(c.numerator).bit_length() for c in exact_values),
        }
        profile.add("global_basis_arb_conversion", (c for poly in polys for c in arithmetic._arb_poly(poly)))
        if representation == "global":
            result = original_operator(polys, support_num, support_den, prec)
            for image in result.images:
                for piece in image:
                    profile.add("combined_image_coefficients", piece.coefficients)
            for k in _sample_indices(n):
                for piece in result.images[k]:
                    image = arb_poly(list(piece.coefficients))
                    basis = arb_poly(arithmetic._arb_poly(polys[k]))
                    _product_profile(basis, image, piece.lower, piece.upper, profile, "sample_low")
                    _product_profile(image, image, piece.lower, piece.upper, profile, "sample_square")
        else:
            result = _local_operator(polys, support_num, support_den, prec, representation, profile)
        captured.append((basis_metadata, result))
        return result

    with ctx.workprec(precision), ExitStack() as stack:
        stack.enter_context(patch.object(assembly, "assemble_active_prime_power_operator", operator))
        if grouped_potential:
            stack.enter_context(patch.object(assembly, "_potential_matrices", potential))
        if representation == "global":
            stack.enter_context(patch.object(arithmetic, "_arb_poly_shift", observe_shift))
        result = assembly.assemble_multi_prime_schur(
            n=n, prec=precision, residual_order=residual_order,
            support_num=support.numerator, support_den=support.denominator,
            require_positive_mu=False,
        )
        low_composition = assembly._mat_mul_diag_inverse(result["P"], result["norms"])
        matrices = {name: _matrix_profile(result[name]) for name in ("P", "P_squared", "GP", "A", "GV", "GR")}
        matrices["PD_inverse_P"] = _matrix_profile(low_composition)
        if result["schur"] is not None:
            matrices["schur"] = _matrix_profile(result["schur"])
        mu_lo, mu_hi = arb_to_rational_enclosure(result["mu"])
        candidate_outcome = {"status": "not_requested"}
        if witness:
            if not result["mu_positive"]:
                candidate_outcome = {"status": "complement_not_positive"}
            else:
                with patch.object(candidate, "assemble_multi_prime_schur", return_value=result):
                    try:
                        checked = candidate.run_candidate(
                            support, dimension=n, prec=precision, residual_order=residual_order,
                            matrix_bits=matrix_bits, witness_bits=witness_bits,
                        )
                        candidate_outcome = {key: checked[key] for key in (
                            "mu_lower", "even_gershgorin_margin", "odd_gershgorin_margin", "all_margins_positive",
                            "exact_rounding_diagnostics",
                        )}
                        candidate_outcome["status"] = "positive_exact_candidate" if checked["all_margins_positive"] else "nonpositive_exact_candidate"
                    except candidate.CandidateStageError as error:
                        candidate_outcome = {"status": "failed", "stage": error.stage, "error": str(error)}
    return {
        "dimension": n, "support": str(support), "precision_bits": precision,
        "representation": representation, "active_terms": [term.m for term in captured[0][1].terms],
        "potential_representation": "exact_grouped_constants" if grouped_potential else "production_moment_sum",
        "small_potential_reference_overlap": potential_comparison,
        "basis_exact": captured[0][0], "coefficient_stages": profile.json(), "matrix_stages": matrices,
        "mu": {"lower": fraction_text(mu_lo), "upper": fraction_text(mu_hi)},
        "candidate": candidate_outcome, "candidate_assembly_reused": witness,
        "matrix_bits": matrix_bits, "witness_bits": witness_bits,
        "theorem_status": False,
    }, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--support", default="11/20")
    parser.add_argument("--dimensions", default="16,192,196")
    parser.add_argument("--precisions", default="128,256,512")
    parser.add_argument("--representations", default="global,cell-monomial,cell-legendre")
    parser.add_argument("--residual-order", type=int, default=32)
    parser.add_argument("--witness-precision", type=int)
    parser.add_argument("--matrix-bits", type=int, default=64)
    parser.add_argument("--witness-bits", type=int, default=32)
    parser.add_argument("--group-potential", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()
    representations = args.representations.split(",")
    if any(value not in {"global", "cell-monomial", "cell-legendre"} for value in representations):
        parser.error("unknown representation")
    dimensions = [int(value) for value in args.dimensions.split(",")]
    precisions = [int(value) for value in args.precisions.split(",")]
    support = Fraction(args.support)
    payload = {"role": "conditioning_experiment_not_production_or_qualification", "status": "running",
               "provenance": _provenance(), "diagnostic_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "source_policy": "production unchanged; process-local experimental arithmetic and optional potential substitution",
               "stage_sampling": "all coefficient and final matrix entries; product/primitive/endpoints only selected diagonal degrees",
               "parameters": vars(args) | {"output_json": str(args.output_json)},
               "exact_identity_check": _verify_affine_identity(), "samples": [], "small_representation_comparisons": []}
    args.output_json.parent.mkdir(parents=True, exist_ok=True)

    def publish():
        args.output_json.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    publish()
    for n in dimensions:
        for precision in precisions:
            reference = None
            for representation in representations:
                row, assembled = run_sample(n, support, precision, representation, args.residual_order,
                                            precision == args.witness_precision and n >= 40 and representation != "global",
                                            args.group_potential, args.matrix_bits, args.witness_bits)
                if n <= 32:
                    if reference is None:
                        reference = assembled
                    else:
                        overlap = all(reference[name][i][j].overlaps(assembled[name][i][j])
                                      for name in ("P", "P_squared", "GP", "A")
                                      for i in range(n) for j in range(n))
                        payload["small_representation_comparisons"].append({"dimension": n, "precision": precision,
                            "representation": representation, "all_arithmetic_and_finite_entries_overlap": overlap})
                        if not overlap:
                            raise RuntimeError("small representation comparison failed")
                payload["samples"].append(row)
                publish()
                print(f"N={n} precision={precision} {representation}: recorded; candidate={row['candidate']['status']}", flush=True)
    payload["status"] = "completed"
    publish()


if __name__ == "__main__":
    main()
