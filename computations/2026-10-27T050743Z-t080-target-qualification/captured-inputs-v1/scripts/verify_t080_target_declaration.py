"""Independent fixed-support parameter audit; no low matrix or positivity proof.

Exact formal division and direct analytic tails are reconstructed here. FLINT/Arb
arithmetic and transcendental enclosures are shared trust, not independently
implemented arithmetic. The accepted scalar/control audits remain premises.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction as Q
import hashlib
import json
from math import factorial
from pathlib import Path
import sys

from flint import acb, arb, ctx

ROOT = Path(__file__).resolve().parents[1]
T, ALPHA, BETA, FLOOR = Q(4, 5), Q(1, 4), Q(859, 1024), Q(1, 3)
ETA = 1 - Q(1, 1 << 128)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reject_number(_):
    raise ValueError("nonexact JSON number")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    raw = path.read_bytes()
    return json.loads(raw, parse_float=reject_number,
                      parse_constant=reject_number,
                      object_pairs_hook=unique_object), hashlib.sha256(raw).hexdigest()


def rational(value):
    require(isinstance(value, str), "canonical rational string required")
    result = Q(value)
    require(str(result) == value, "noncanonical rational string")
    return result


def exact_fields(record, expected, label):
    require(isinstance(record, dict), "invalid " + label)
    for key, value in expected.items():
        require(type(record.get(key)) is type(value) and record.get(key) == value,
                "incorrect " + label + "." + key)


def aq(value):
    value = Q(value)
    return arb(value.numerator) / value.denominator


def endpoints(value):
    require(value.is_finite(), "nonfinite analytic enclosure")
    mid, rad = value.mid().fmpq(), value.rad().fmpq()
    lo, hi = mid-rad, mid+rad
    return Q(int(lo.p), int(lo.q)), Q(int(hi.p), int(hi.q))


def enclosure(record, label):
    require(isinstance(record, dict) and set(record) == {"lower", "upper"},
            "invalid interval " + label)
    lo, hi = rational(record["lower"]), rational(record["upper"])
    require(lo <= hi, "reversed interval " + label)
    return lo, hi


def bundle_path(bundle, name):
    require(isinstance(name, str), "invalid bound path")
    relative = Path(name)
    path = (bundle / relative).resolve()
    require(not relative.is_absolute() and path.is_relative_to(bundle),
            "path escapes bundle")
    return path


def project_modules(record, label):
    require(isinstance(record, dict) and record, "missing module fingerprints " + label)
    for name, value in record.items():
        require(isinstance(name, str) and isinstance(value, str), "invalid module fingerprint")
        path = (ROOT / name).resolve()
        require(name.startswith("scripts/") and path.is_relative_to(ROOT)
                and path.suffix == ".py", "unsafe project module path")
        require(digest(path) == value, "changed project module: " + name)


def imported_modules(path):
    """Find explicit project imports without executing any project code."""
    result = set()
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [item.name for item in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            names = [node.module or ""]
        else:
            continue
        for name in names:
            if name.startswith("scripts."):
                candidate = ROOT.joinpath(*name.split(".")).with_suffix(".py")
                if not candidate.is_file():
                    candidate = ROOT.joinpath(*name.split("."), "__init__.py")
                require(candidate.is_file(), "unresolved project import " + name)
                result.add(candidate.relative_to(ROOT).as_posix())
    return result


def check_module_closure(producer, modules):
    pending = [producer]
    seen = set()
    while pending:
        path = pending.pop()
        name = path.relative_to(ROOT).as_posix()
        if name in seen:
            continue
        seen.add(name)
        for dependency in imported_modules(path):
            require(dependency in modules, "unbound explicit project import: " + dependency)
            pending.append(ROOT / dependency)


def ceil_log2(value):
    value = Q(value)
    require(value > 0, "log2 argument must be positive")
    n = value.numerator.bit_length() - value.denominator.bit_length()
    power = Q(1 << n) if n >= 0 else Q(1, 1 << -n)
    return n if value <= power else n + 1


def upward_interval(fresh, bits, label):
    require(fresh[0] > 0, "nonpositive upper publication " + label)
    scale = 1 << bits
    lower = Q((fresh[0]*scale).__ceil__()+1, scale)
    upper = Q((fresh[1]*scale).__ceil__()+1, scale)
    require(lower == upper, "ambiguous directed publication " + label)
    return upper


def check_upper(text, fresh, bits, label):
    value = rational(text)
    require(fresh[0] > 0 and fresh[1] <= value, "false analytic upper " + label)
    require(value == upward_interval(fresh, bits, label),
            "wrong upward publication " + label)
    return value


def kernel_coefficients(order):
    """Divide exp(-z/2) by 1-exp(-2z), first removing its exact pole."""
    denominator = [Q(0)] + [Q((-1)**(j+1)*2**j, factorial(j))
                            for j in range(1, order+3)]
    regular, result = [], []
    for n in range(order+1):
        rhs = Q(-1, 2)**(n+1)/factorial(n+1)-denominator[n+2]/2
        rhs -= sum((denominator[j]*regular[n+1-j]
                    for j in range(2, n+2)), Q(0))
        quotient = rhs/denominator[1]
        regular.append(quotient)
        polar = Q(2, 2**n*factorial(n)) if n % 2 == 0 else Q(0)
        result.append(-T**(n+1)*(quotient-polar))
    require(result[1] == T*T/48, "formal quotient normalization")
    return result


def analytic_bounds(order, coefficients):
    pi, t = arb.pi(), aq(T)
    require(2*t < pi and t < order+2, "analytic tail ratio not below one")
    geometric = (2/pi)*(2*t/pi)**(order+1)/(1-2*t/pi)
    exponential = 2*t**(order+1)/(factorial(order+1)*(1-t/(order+2)))
    delta = 2*t*(geometric+exponential)
    arithmetic = arb(2).log()/arb(2).sqrt()+arb(3).log()/arb(3).sqrt()+arb(2).log()/2
    polynomial = sum((abs(c)*2**d for d, c in enumerate(coefficients[:order+1])), Q(0))
    prime_upper = upward_interval(endpoints(2*arithmetic), 192, "arithmetic shift norm")
    cross = pi/2+aq(prime_upper+2*polynomial)
    return endpoints(delta), endpoints(cross)


def frequency_g(edge):
    pi = arb.pi()
    a0 = -arb.const_euler()-pi/2-3*arb(2).log()-pi.log()
    psi = acb(aq(Q(1, 4)), aq(edge/2)).digamma().real
    return aq(Q(3, 4))*(psi-pi.log())+a0/4-aq(Q(1, 4))-aq(BETA)


def verify_audited_inputs(bundle, pins, reference_audit_path, control_audit_path):
    reference_path = bundle_path(bundle, pins["reference_source"])
    control_path = bundle_path(bundle, pins["control_budget_source"])
    reference, reference_hash = load(reference_path)
    control, control_hash = load(control_path)
    ra, ra_hash = load(reference_audit_path)
    ca, ca_hash = load(control_audit_path)
    require(reference_hash == pins["reference_source_sha256"], "reference input seal")
    require(control_hash == pins["control_budget_sha256"], "control input seal")
    exact_fields(ra, {"format": "t080-reference-qualification-audit-v1", "status": "PASS",
                     "source_sha256": reference_hash, "audit_precision_bits": 768,
                     "publication_bits": 192,
                     "audit_code_sha256": digest(ROOT / "scripts/verify_t080_reference_qualification.py")},
                 "reference audit")
    exact_fields(ca, {"format": "t080-control-budget-independent-audit-v1", "status": "PASS",
                     "source_sha256": control_hash, "whole_space_caps_checked": 8,
                     "consumer_sha256": digest(ROOT / "scripts/verify_t080_control_budget.py"),
                     "target_matrices_computed": False}, "control audit")
    fixed = {"support": str(T), "alpha": str(ALPHA), "beta": str(BETA),
             "m": str(FLOOR), "eta": str(ETA), "N": 322, "M": 644, "R": 257, "Rc": 514}
    exact_fields(reference, {"format": "t080-reference-qualification-v1",
                            "status": "SCALAR_REFERENCE_QUALIFIED", **fixed,
                            "new_support_matrix_computed": False,
                            "complete_low_cross_positivity_proved": False,
                            "all_support_estimate_proved": False,
                            "production_admission": False}, "reference")
    exact_fields(ra, {**fixed, "new_support_matrix_computed": False,
                      "complete_low_cross_positivity_proved": False,
                      "all_support_estimate_proved": False,
                      "production_admission": False}, "reference audit")
    _, reference_input_hash = load(bundle_path(bundle, pins["reference_inputs"]))
    require(reference["inputs_sha256"] == ra["inputs_sha256"] == reference_input_hash,
            "reference inputs audit binding")
    require(reference["producer_sha256"] == digest(ROOT / "scripts/weil_t080_reference_qualification.py"),
            "reference producer binding")
    project_modules(reference["imported_project_module_sha256"], "reference")
    final = reference["N_policy_trials"][-1]
    require(final["N"] == reference["N"] and final["outcome"] == "qualified", "reference final trial")
    for name in ("leakage", "outside_lower_form", "epsilon", "epsilon_over_m"):
        source_interval = enclosure(final[name], "reference " + name)
        audit_interval = enclosure(ra["reference_controls"][name], "audited " + name)
        require(source_interval[0] <= audit_interval[0] <= audit_interval[1] <= source_interval[1],
                "reference audited interval mismatch " + name)
    require(rational(final["outside_lower_form"]["lower"]) >= FLOOR
            and rational(final["epsilon_over_m"]["upper"]) <= 1-ETA,
            "reference coercivity and domination premises")
    inverse = reference["inverse_weight"]
    for name in ("a", "complete_leakage", "kappa"):
        source_interval = enclosure(inverse[name], "reference inverse " + name)
        audit_interval = enclosure(ra["inverse_weight"][name], "audited inverse " + name)
        require(source_interval[0] <= audit_interval[0] <= audit_interval[1] <= source_interval[1],
                "inverse audited interval mismatch " + name)
    a = rational(inverse["a"]["upper"])
    leakage = rational(inverse["complete_leakage"]["upper"])
    require(0 < a < 3 and 0 <= leakage < 1 and inverse["global_upper"] == "3",
            "inverse-weight premise")
    kappa = a+(3-a)*leakage
    require(0 < kappa < 3, "missing strict inverse-weight gain")
    exact_fields(control, {"format": "t080-control-budget-v1", "accuracy_goal_is_NOT_target_gap": True,
                           "target_matrices_computed": False}, "control")
    gaps = []
    for parity in ("even", "odd"):
        source_row, audit_row = control["parities"][parity], ca["parities"][parity]
        gap = rational(source_row["control_selected_S_physical_mass_lower"])
        require(gap > 0 and rational(audit_row["physical_selected_S_lower"]) == gap,
                "audited control physical lower bound")
        gaps.append(gap)
        require(set(source_row["relative_caps"]) == set(audit_row["relative_caps"]),
                "control cap coverage")
        for name, record in source_row["relative_caps"].items():
            cap = rational(record["upper"])
            require(cap >= 0 and rational(audit_row["relative_caps"][name]) == cap,
                    "control cap audit mismatch")
        require(rational(audit_row["relative_caps"]["combined_paid"]) < 1,
                "control combined budget not below one")
    gap = min(gaps)
    goal = gap/(1 << 20)
    require(rational(control["certified_control_selected_S_physical_mass_lower"]) == gap,
            "control selected physical bound")
    require(rational(control["target_canonical_model_error_goal"]) == goal
            and rational(ca["target_model_error_goal"]) == goal, "baseline-derived accuracy goal")
    require(control["producer_sha256"] == digest(ROOT / "scripts/weil_t080_control_budget.py"),
            "control producer binding")
    return reference, goal, kappa, {
        "reference_source_sha256": reference_hash, "reference_audit_sha256": ra_hash,
        "control_budget_sha256": control_hash, "control_audit_sha256": ca_hash}


def audit(args):
    pins, input_hash = load(args.inputs)
    source, source_hash = load(args.source)
    bundle = args.inputs.resolve().parent
    require(args.source.resolve().is_relative_to(bundle)
            and args.reference_audit.resolve().is_relative_to(bundle)
            and args.control_audit.resolve().is_relative_to(bundle), "records outside input bundle")
    # The contract is an explicit local premise, never a target positivity claim.
    contract = bundle_path(bundle, "reference-contract-v1.md")
    require(contract.is_file() and contract.stat().st_size > 0, "missing reference contract")
    exact_fields(pins, {
        "format": "t080-parameter-selection-inputs-v1", "support": str(T),
        "scalar_precision_bits": 768, "scalar_publication_bits": 192,
        "matrix_publication_bits": 256, "numerical_guard_bits": 512,
        "precision_block_bits": 512, "producer_precision_floor_bits": 3072,
        "independent_precision_floor_bits": 4096,
        "numerical_width_goal_fraction_of_declared_accuracy": "1/4",
        "precision_policy_is_not_enclosure_or_low_gap_proof": True,
        "production_admission": False, "target_low_gap_assumed": False,
        "target_low_or_coupling_matrix_permitted_in_this_operation": False}, "parameter inputs")
    exact_fields(pins, {
        "K_policy": "first even K>=2 with2K<N and complete canonical Lambda_K<=baseline-derived accuracy goal; all preceding evenK retained",
        "B_K_rule": "pi/2 +2sum_m coefficient_m+2sum_d<=K abs(kernel_coefficient_d)*2^d",
        "complete_model_error_rule": "delta +(2 B_K delta+delta\u00b2)/(m eta)",
        "frequency_partition_policy": "0,R; multiply positiveR by17/16 strictlybelow32R; append32R; nonzero terminal Parsevalmass",
        "inverse_tail_frequency_policy": "Rc=2R",
        "physical_extent_policy": "M=2N >=N+K, not a truncation of physical infinity"},
        "declared mathematical policy")
    reference, goal, kappa, bindings = verify_audited_inputs(
        bundle, pins, args.reference_audit.resolve(), args.control_audit.resolve())
    producer = ROOT / "scripts/weil_t080_target_declaration.py"
    expected_bindings = {"inputs_sha256": input_hash,
                         "producer_sha256": digest(producer), **bindings}
    require(source["bindings"] == expected_bindings, "target source byte bindings")
    modules = source["imported_project_module_sha256"]
    project_modules(modules, "target declaration")
    require(set(modules) == {
        "scripts/cert/__init__.py", "scripts/cert/constants.py",
        "scripts/cert/quadrature.py", "scripts/cert/residual_kernel.py"},
        "incomplete or unexpected target producer dependency set")
    check_module_closure(producer, modules)
    fixed = {"format": "t080-qualified-target-declaration-v1",
             "status": "QUALIFIED_TARGET_PARAMETERS_NOT_POSITIVITY", "support": str(T),
             "N": reference["N"], "M": reference["M"], "R": reference["R"], "Rc": reference["Rc"],
             "alpha": str(ALPHA), "beta": str(BETA), "m": str(FLOOR), "eta": str(ETA),
             "accuracy_goal_is_NOT_target_gap": True,
             "target_low_coupling_matrix_computed": False,
             "target_positivity_proved": False, "production_admission": False}
    exact_fields(source, fixed, "target declaration")
    expected_keys = set(fixed) | {
        "K", "kernel_coefficients", "order_selection_ladder",
        "complete_remainder_upper", "combined_model_cross_norm_upper",
        "complete_model_error_upper", "model_error_accuracy_goal",
        "frequency_edges", "inverse_weight_step_uppers",
        "weighted_physical_tail_inverse_upper", "precision",
        "finite_model_cross_band", "first_attempt", "bindings",
        "imported_project_module_sha256"}
    require(set(source) == expected_keys, "invalid target declaration schema")
    require(rational(source["model_error_accuracy_goal"]) == goal, "changed model accuracy goal")
    require(rational(source["weighted_physical_tail_inverse_upper"]) == kappa,
            "complete physical inverse weight allowance")
    N, M, R, K = source["N"], source["M"], source["R"], source["K"]
    require(type(K) is int and K >= 2 and K % 2 == 0 and 2*K < N and M >= N+K,
            "invalid model band or 2K<N condition")
    coefficients = kernel_coefficients(K)
    require(source["kernel_coefficients"] == [str(value) for value in coefficients],
            "incorrect complete formal kernel coefficients")
    ladder = source["order_selection_ladder"]
    require(isinstance(ladder, list) and len(ladder) == K//2, "incomplete prior-order policy ladder")
    for bits in (512, 1024):
        ctx.prec = bits
        for row, order in zip(ladder, range(2, K+1, 2), strict=True):
            require(set(row) == {"order", "delta_upper", "B_K_upper", "Lambda_upper", "goal_met"},
                    "invalid order-selection row schema")
            exact_fields(row, {"order": order, "goal_met": order == K}, "order selection")
            delta_fresh, cross_fresh = analytic_bounds(order, coefficients)
            delta = check_upper(row["delta_upper"], delta_fresh, 192, "delta at K="+str(order))
            cross = check_upper(row["B_K_upper"], cross_fresh, 192, "cross bound at K="+str(order))
            exact_model = delta+(2*cross*delta+delta*delta)/(FLOOR*ETA)
            model = check_upper(row["Lambda_upper"], (exact_model, exact_model), 192,
                                "model allowance at K="+str(order))
            require((model <= goal) == (order == K), "not the first published qualifying even order")
        final = ladder[-1]
        for field, row_field in (("complete_remainder_upper", "delta_upper"),
                                 ("combined_model_cross_norm_upper", "B_K_upper"),
                                 ("complete_model_error_upper", "Lambda_upper")):
            require(source[field] == final[row_field], "selected allowance mismatch " + field)
        expected_edges = [Q(0), Q(R)]
        while expected_edges[-1]*Q(17, 16) < 32*R:
            expected_edges.append(expected_edges[-1]*Q(17, 16))
        expected_edges.append(Q(32*R))
        require(source["frequency_edges"] == [str(value) for value in expected_edges],
                "incomplete exact frequency partition")
        weights = source["inverse_weight_step_uppers"]
        require(isinstance(weights, list) and len(weights) == len(expected_edges)
                and weights[0] == "3", "incomplete inverse frequency weights")
        previous = Q(3)
        for edge, text in zip(expected_edges[1:], weights[1:], strict=True):
            g = frequency_g(edge)
            require(g > aq(FLOOR), "frequency edge below reference floor")
            weight = check_upper(text, endpoints(1/g), 256, "inverse weight at "+str(edge))
            require(0 < weight <= previous, "nonpositive or increasing frequency weight")
            previous = weight
        # Positive terminal weight multiplies the full Parseval mass; the
        # partition is not interpreted as discarding frequencies above 32R.
        require(previous > 0, "unpaid infinite-frequency exterior")
    band = {"input_start": N-K, "input_end": N-1, "output_start": N,
            "output_end": N+K-1, "dimension": K,
            "all_other_model_cross_entries_zero": True,
            "low_even_and_polar_terms_required": True}
    require(set(source["finite_model_cross_band"]) == set(band), "invalid finite-band schema")
    exact_fields(source["finite_model_cross_band"], band, "finite model band")
    source_amp = ceil_log2(Q(21)**(N-1))
    independent_amp = ceil_log2(Q(3)**(M-1)*Q(7)**(N-1))
    bessel = Q(M+1)
    for n in range(1, M+1):
        bessel *= 1+Q(2*n+1)/(T*R)
    bessel_amp = ceil_log2(bessel)
    block = lambda n: ((n+511)//512)*512
    source_bits = max(3072, block(256+512+source_amp))
    independent_bits = max(4096, source_bits+1024,
                           block(256+512+independent_amp), block(256+512+bessel_amp))
    precision = {"scalar_bits": 768, "scalar_publication_bits": 192,
                 "matrix_publication_bits": 256, "source_bits": source_bits,
                 "independent_bits": independent_bits,
                 "source_coefficient_amplification_bits": source_amp,
                 "independent_coefficient_amplification_bits": independent_amp,
                 "upward_Bessel_amplification_bits": bessel_amp,
                 "numerical_error_physical_norm_goal": str(goal/4),
                 "guarantees_target_gap_false": True}
    require(set(source["precision"]) == set(precision), "invalid precision schema")
    exact_fields(source["precision"], precision, "candidate precision")
    first = source["first_attempt"]
    exact_fields(first, {"initial_low_dimension": N, "initial_residual_order": K,
                         "source_arithmetic_Gauss_order": (M+N)//2,
                         "independent_combined_square_Gauss_order": N,
                         "parity_dimensions": [N//2, N//2],
                         "core_symmetric_source_entries": 3*(N//2)*(N//2+1)}, "first attempt")
    require(set(first) == {
        "initial_low_dimension", "initial_residual_order",
        "source_arithmetic_Gauss_order", "independent_combined_square_Gauss_order",
        "parity_dimensions", "core_symmetric_source_entries",
        "model_error_goal", "refinement_policy"}, "invalid first-attempt schema")
    for key in ("model_error_goal", "refinement_policy"):
        require(isinstance(first[key], str) and first[key].strip(), "missing future policy " + key)
    return {"format": "t080-target-declaration-independent-audit-v1", "status": "PASS",
            "source_sha256": source_hash, "consumer_sha256": digest(Path(__file__)),
            "verifiedK": K, "N": N,
            "full_remainder_and_coefficient_checks": True,
            "policy_prior_orders_checked": len(ladder)-1,
            "policy_minimum_scope": "first qualifying published sufficient allowance, not optimal true residual degree",
            "frequency_weights_checked": len(weights),
            "frequency_exterior_paid_by_terminal_Parseval_weight": True,
            "mapped_Legendre_physical_mass_convention": "D_n=2/(2n+1), with support factors in the mapped operators",
            "precision_policy_checked": True,
            "required_numerical_physical_width_goal": str(goal/4),
            "precision_policy_is_not_an_actual_enclosure_width_or_gap_proof": True,
            "shared_trust": "FLINT/Arb enclosed arithmetic and transcendental functions",
            "target_low_coupling_matrix_computed": False,
            "target_positivity_proved": False, "production_admission": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("inputs", "source", "reference-audit", "control-audit", "output"):
        parser.add_argument("--"+name, type=Path, required=True)
    args = parser.parse_args()
    try:
        require(not args.output.exists(), "output must be a fresh path")
        result = audit(args)
        encoded = json.dumps(result, indent=2, sort_keys=True)+"\n"
        with args.output.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
    except (ValueError, KeyError, TypeError, ZeroDivisionError, OSError, OverflowError,
            AttributeError, IndexError, SyntaxError) as exc:
        print(json.dumps({"status": "REJECT", "error": str(exc)}))
        return 2
    print(json.dumps({"status": "PASS", "verifiedK": result["verifiedK"], "N": result["N"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
