"""Manual enclosure diagnosis, never continuation or theorem admission.

Compare historical global/cell-monomial controls with production cell-local
Legendre arithmetic. Optional grouped potential uses production; the default
retains historical ungrouped moments as a diagnostic control only.
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

from flint import arb, arb_poly, ctx, fmpq, fmpq_mat, fmpq_poly

from scripts.cert import multi_prime_legendre_schur as assembly
from scripts.cert import prime_power_terms as arithmetic
from scripts import weil_multi_prime_support_candidate_check as candidate
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.legendre_schur import legendre_polynomials, potential_moment, potential_square_moment
from scripts.multi_prime_precision_diagnostics import arb_matrix_exact_width_diagnostics, arb_midpoint_fraction
from scripts.precision_diagnostics import fraction_text
from scripts.profile_multi_prime_assembly import _provenance


CANDIDATE_SOURCE_PATHS = (
    "scripts/weil_multi_prime_support_candidate_check.py",
    "scripts/cert/exact_prime_schur_common.py",
    "scripts/cert/multi_prime_exact_witness.py",
    "scripts/cert/matrices.py",
    "scripts/precision_diagnostics.py",
    "scripts/multi_prime_precision_diagnostics.py",
    "scripts/audit_multi_prime_candidate.py",
)


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


def _arb_polynomial(poly):
    return [arithmetic._arb_fraction(value) for value in poly]


def _integrated_product(left, right, interval):
    primitive = (left * right).integral()
    return primitive(interval[1]) - primitive(interval[0])


def _global_operator(polys, support_num, support_den, prec, profile):
    """Historical global-coordinate control, never a production fallback."""
    terms = arithmetic.enumerate_active_prime_power_terms(support_num, support_den, prec)
    points = arithmetic._sorted_breakpoints(terms) if terms else (arb(-1), arb(1))
    basis = [arb_poly(_arb_polynomial(poly)) for poly in polys]
    shifted = []
    for base in basis:
        pairs = []
        for term in terms:
            pair = tuple(base(arb_poly([shift, 1])) for shift in (term.tau, -term.tau))
            for values in pair:
                profile.add("translated_coefficients", values.coeffs())
            pairs.append(pair)
        shifted.append(pairs)
    n = len(polys)
    p_matrix, square = arithmetic._zero_matrix(n), arithmetic._zero_matrix(n)
    for lower, upper in zip(points[:-1], points[1:], strict=True):
        midpoint = (lower + upper) / 2
        images = [arb_poly() for _ in polys]
        for t, term in enumerate(terms):
            for side, active in enumerate((
                arithmetic._activity(midpoint, 1 - term.tau, before=True, term=term),
                arithmetic._activity(midpoint, -1 + term.tau, before=False, term=term),
            )):
                if active:
                    for k in range(n):
                        images[k] -= term.coefficient * shifted[k][t][side]
        for values in images:
            profile.add("combined_image_coefficients", values.coeffs())
        for k in _sample_indices(n):
            _product_profile(basis[k], images[k], lower, upper, profile, "sample_low")
            _product_profile(images[k], images[k], lower, upper, profile, "sample_square")
        for i in range(n):
            for j in range(i, n):
                if (i + j) % 2 == 0:
                    p_matrix[i][j] += _integrated_product(basis[i], images[j], (lower, upper))
                    square[i][j] += _integrated_product(images[i], images[j], (lower, upper))
    for i in range(n):
        for j in range(i):
            p_matrix[i][j], square[i][j] = p_matrix[j][i], square[j][i]
    norms = arithmetic._orthogonal_basis_norms(polys)
    return SimpleNamespace(terms=terms, p_matrix=p_matrix, p_squared_matrix=square,
                           g_p=arithmetic._tail_gram(p_matrix, square, norms))


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


def _local_monomial_operator(polys, support_num, support_den, prec, profile):
    n = len(polys)
    # This experiment specifically compares representations of the Legendre
    # basis, not a proposed generic-basis replacement for the production API.
    if list(polys) != legendre_polynomials(n - 1):
        raise ValueError("conditioning experiment requires the canonical Legendre basis")
    terms = arithmetic.enumerate_active_prime_power_terms(support_num, support_den, prec)
    breakpoints = arithmetic._sorted_breakpoints(terms) if terms else (arb(-1), arb(1))
    p_matrix, square = arithmetic._zero_matrix(n), arithmetic._zero_matrix(n)
    norms = tuple(Fraction(2, 2 * k + 1) for k in range(n))
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
        basis = _affine_monomials(n, center, radius)
        images = [arb_poly() for _ in range(n)]
        for shift, coefficient in active:
            translated = _affine_monomials(n, center + shift, radius)
            for k, values in enumerate(translated):
                profile.add("translated_coefficients", values.coeffs())
                images[k] += values * coefficient
        for k in range(n):
            profile.add("cell_basis_coefficients", basis[k].coeffs())
            profile.add("combined_image_coefficients", images[k].coeffs())
        for k in _sample_indices(n):
            _product_profile(basis[k], images[k], arb(-1), arb(1), profile, "sample_low")
            _product_profile(images[k], images[k], arb(-1), arb(1), profile, "sample_square")
        for i in range(n):
            for j in range(i, n):
                if (i + j) % 2:
                    continue
                p_value = radius * _integrated_product(basis[i], images[j], (arb(-1), arb(1)))
                square_value = radius * _integrated_product(images[i], images[j], (arb(-1), arb(1)))
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


def _moment_potential(polys, prec):
    """Historical independent per-moment rounding, diagnostic control only."""
    exact = arithmetic._exact_polynomials(polys)
    parities = arithmetic._polynomial_parities(polys)
    max_power = 2 * max(poly.degree() for poly in exact)
    with ctx.workprec(prec):
        log2, pi = arb.const_log2(), arb.pi()
        moments = [potential_moment(k, log2) for k in range(max_power + 1)]
        square_moments = [potential_square_moment(k, log2, pi) for k in range(max_power + 1)]
        low, square = arithmetic._zero_matrix(len(polys)), arithmetic._zero_matrix(len(polys))
        for i, left in enumerate(exact):
            for j in range(i, len(exact)):
                if arithmetic._opposite_parity(parities[i], parities[j]):
                    continue
                for k, coefficient in enumerate((left * exact[j]).coeffs()):
                    if coefficient:
                        low[i][j] += arb(coefficient) * moments[k]
                        square[i][j] += arb(coefficient) * square_moments[k]
                low[j][i], square[j][i] = low[i][j], square[i][j]
    return low, square


def run_sample(n, support, precision, representation, residual_order, witness, grouped_potential=False,
               matrix_bits=64, witness_bits=32):
    profile = EnclosureProfile()
    original_operator = assembly.assemble_active_prime_power_operator
    original_potential = assembly._potential_matrices
    potential_comparison = None

    def potential(polys, prec):
        nonlocal potential_comparison
        low, square = original_potential(polys, prec)
        if n <= 32:
            reference_low, reference_square = _moment_potential(polys, prec)
            potential_comparison = all(
                reference[i][j].overlaps(actual[i][j])
                for reference, actual in ((reference_low, low), (reference_square, square))
                for i in range(n) for j in range(n)
            )
            if not potential_comparison:
                raise RuntimeError("exact grouped potential does not overlap original moments")
        return low, square
    captured = []

    def operator(polys, support_num, support_den, prec):
        exact_values = [c for poly in polys for c in poly]
        basis_metadata = {
            "coefficient_width": "0/1", "max_exact_abs_coefficient": fraction_text(max(map(abs, exact_values))),
            "max_numerator_bits": max(abs(c.numerator).bit_length() for c in exact_values),
        }
        profile.add("global_basis_arb_conversion", (c for poly in polys for c in _arb_polynomial(poly)))
        if representation == "global":
            result = _global_operator(polys, support_num, support_den, prec, profile)
        elif representation == "cell-monomial":
            result = _local_monomial_operator(polys, support_num, support_den, prec, profile)
        else:
            affine = arithmetic._affine_legendre

            def observe_affine(degree, center, radius):
                table = affine(degree, center, radius)
                for coefficients in table:
                    profile.add("local_affine_coefficients", coefficients)
                return table

            with patch.object(arithmetic, "_affine_legendre", observe_affine):
                result = original_operator(polys, support_num, support_den, prec)
            for image in result.images:
                for piece in image:
                    profile.add("combined_image_coefficients", piece.legendre_coefficients)
            for k in _sample_indices(n):
                for piece in result.images[k]:
                    profile.add("sample_square/diagonal_inner_products",
                                (value * value * 2 / (2 * degree + 1)
                                 for degree, value in enumerate(piece.legendre_coefficients)))
        captured.append((basis_metadata, result))
        return result

    with ctx.workprec(precision), ExitStack() as stack:
        stack.enter_context(patch.object(assembly, "assemble_active_prime_power_operator", operator))
        if grouped_potential:
            stack.enter_context(patch.object(assembly, "_potential_matrices", potential))
        else:
            stack.enter_context(patch.object(assembly, "_potential_matrices", _moment_potential))
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
                            "audit_inputs",
                        )}
                        candidate_outcome["status"] = "positive_exact_candidate" if checked["all_margins_positive"] else "nonpositive_exact_candidate"
                    except candidate.CandidateStageError as error:
                        candidate_outcome = {"status": "failed", "stage": error.stage, "error": str(error),
                                             "audit_inputs": error.audit_inputs}
    return {
        "dimension": n, "support": str(support), "precision_bits": precision,
        "representation": representation, "active_terms": [term.m for term in captured[0][1].terms],
        "potential_representation": "production_exact_grouped_constants" if grouped_potential else "historical_moment_sum",
        "small_potential_reference_overlap": potential_comparison,
        "basis_exact": captured[0][0], "coefficient_stages": profile.json(), "matrix_stages": matrices,
        "mu": {"lower": fraction_text(mu_lo), "upper": fraction_text(mu_hi)},
        "candidate": candidate_outcome, "candidate_assembly_reused": witness,
        "matrix_bits": matrix_bits, "witness_bits": witness_bits,
        "theorem_status": False,
    }, result


def record_rayleigh_direction(assembled, archive_path, vector_bits):
    """Check one exact last-coordinate direction, not a spectral sign oracle."""
    import zipfile

    if assembled["schur"] is None:
        return {"status": "unavailable", "reason": "complement_not_positive"}
    n = assembled["dimension"]
    indices = list(range(0, n, 2))
    midpoint = [[arb_midpoint_fraction(assembled["schur"][i][j]) for j in indices] for i in indices]
    dim = len(indices)
    vector = []
    if dim > 1:
        leading = fmpq_mat([[fmpq(value.numerator, value.denominator) for value in row[:-1]]
                           for row in midpoint[:-1]])
        right = fmpq_mat([[fmpq(-row[-1].numerator, row[-1].denominator)] for row in midpoint[:-1]])
        solution = leading.solve(right)
        scale = 1 << vector_bits
        for i in range(dim - 1):
            value = solution[i, 0]
            exact = Fraction(int(value.p), int(value.q))
            vector.append(Fraction((2 * exact.numerator * scale + exact.denominator)
                                   // (2 * exact.denominator), scale))
    vector.append(Fraction(1))
    lower, upper = Fraction(0), Fraction(0)
    intervals = []
    for i, original_i in enumerate(indices):
        row = []
        for j, original_j in enumerate(indices):
            lo, hi = arb_to_rational_enclosure(assembled["schur"][original_i][original_j])
            weight = vector[i] * vector[j]
            lower += min(weight * lo, weight * hi)
            upper += max(weight * lo, weight * hi)
            row.append([str(lo), str(hi)])
        intervals.append(row)
    norm_sq = sum((value * value * assembled["norms"][degree]
                   for degree, value in zip(indices, vector, strict=True)), Fraction(0))
    proof = {
        "role": "generator_side_schur_rayleigh_diagnostic_only",
        "support": str(Fraction(assembled["support_num"], assembled["support_den"])),
        "dimension": n, "precision_bits": assembled["precision_bits"], "parity": "even",
        "vector_bits": vector_bits, "vector": [str(value) for value in vector],
        "schur_interval_block": intervals, "rayleigh_lower": str(lower), "rayleigh_upper": str(upper),
        "basis_norm_squared": str(norm_sq), "normalized_rayleigh_upper": str(upper / norm_sq),
        "theorem_status": False,
    }
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("rayleigh-inputs.json", json.dumps(proof))
    return {
        "status": "strict_negative_upper" if upper < 0 else "no_negative_direction_proved",
        "rayleigh_lower": str(lower), "rayleigh_upper": str(upper),
        "normalized_rayleigh_upper": str(upper / norm_sq),
        "archive": archive_path.name, "archive_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
    }


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
    parser.add_argument("--rayleigh-check", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()
    representations = args.representations.split(",")
    if any(value not in {"global", "cell-monomial", "cell-legendre"} for value in representations):
        parser.error("unknown representation")
    dimensions = [int(value) for value in args.dimensions.split(",")]
    precisions = [int(value) for value in args.precisions.split(",")]
    support = Fraction(args.support)
    provenance = _provenance()
    root = Path(__file__).resolve().parents[1]
    provenance["source_sha256"].update({
        relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for relative in CANDIDATE_SOURCE_PATHS
    })
    payload = {"role": "conditioning_experiment_not_production_or_qualification", "status": "running",
               "provenance": provenance, "diagnostic_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "source_policy": "production cell-local Legendre/grouped potential; historical controls are process-local only",
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
                exact_inputs = row["candidate"].pop("audit_inputs", None)
                if exact_inputs is not None:
                    import zipfile

                    candidate_archive = args.output_json.with_name(
                        f"{args.output_json.stem}-candidate-N{n}-p{precision}-{representation}.zip"
                    )
                    with zipfile.ZipFile(candidate_archive, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                        archive.writestr("candidate-inputs.json", json.dumps(exact_inputs))
                    row["candidate"]["exact_inputs_archive"] = candidate_archive.name
                    row["candidate"]["exact_inputs_sha256"] = hashlib.sha256(candidate_archive.read_bytes()).hexdigest()
                if args.rayleigh_check:
                    archive = args.output_json.with_name(
                        f"{args.output_json.stem}-N{n}-p{precision}-{representation}.zip"
                    )
                    row["rayleigh_direction"] = record_rayleigh_direction(assembled, archive, args.witness_bits)
                payload["samples"].append(row)
                publish()
                print(f"N={n} precision={precision} {representation}: recorded; candidate={row['candidate']['status']}", flush=True)
    payload["status"] = "completed"
    publish()


if __name__ == "__main__":
    main()
