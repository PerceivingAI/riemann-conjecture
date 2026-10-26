"""Fixed declared form-criterion controls, not a Weil matrix/proof tool."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from math import factorial
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from flint import acb, arb, ctx
from scripts.cert.constants import arb_to_rational_enclosure


def aq(value):
    value = Q(value)
    return arb(value.numerator) / value.denominator


def bounds(value):
    lower, upper = arb_to_rational_enclosure(value)
    return {"lower": str(lower), "upper": str(upper)}


def vec(values):
    return [Q(x) for x in values]


def dot(a, b):
    return sum((x * y for x, y in zip(a, b, strict=True)), Q(0))


def weighted(a, b, h):
    return sum((x * y / z for x, y, z in zip(a, b, h, strict=True)), Q(0))


def qualify(inputs):
    raw = inputs.read_bytes()
    pins = json.loads(raw)
    if pins["format"] != "energy-aware-schur-control-inputs-v1":
        raise ValueError("wrong declared control format")
    cases = pins["exact_controls"]
    results = {}

    row = cases["compression"]
    h = vec(row["frequency_weight"])
    mass = Q(row["equal_unit_components_squared"])
    compressed_inverse = 1 / (mass * sum(h))
    inverse_compression = mass * sum((1 / x for x in h), Q(0))
    assert compressed_inverse == Q(2, 5) < inverse_compression == Q(5, 8)
    results["compression_not_inverse_commutation"] = {
        "inverse_of_compression": str(compressed_inverse),
        "compression_of_inverse": str(inverse_compression),
        "strict_upper_not_equality": True,
    }

    row = cases["leakage_counterexample"]
    g, h, v = vec(row["g"]), vec(row["h"]), vec(row["tail_unit_vector"])
    assert dot(v, v) == 1
    actual = sum((a * z * z for a, z in zip(g, v, strict=True)), Q(0))
    compressed_h = sum((a * z * z for a, z in zip(h, v, strict=True)), Q(0))
    leakage = v[0] ** 2
    deficit = h[0] - g[0]
    eta = 1 - deficit * leakage / min(h)
    certified = eta * compressed_h
    low, cross = Q(row["low_diagonal"]), Q(row["cross"])
    actual_schur = low - cross**2 / actual
    invalid_schur = low - cross**2 / compressed_h
    safe_schur = low - cross**2 / certified
    assert certified <= actual < compressed_h
    assert actual_schur == Q(-1, 44) < 0 < invalid_schur
    assert safe_schur < 0
    results["omitting_leakage_creates_false_positive"] = {
        "actual_tail": str(actual), "compressed_positive_weight": str(compressed_h),
        "eta": str(eta), "certified_weighted_tail": str(certified),
        "actual_schur": str(actual_schur), "invalid_unpaid_schur": str(invalid_schur),
        "paid_sufficient_schur": str(safe_schur),
    }

    row = cases["weighted_projection"]
    h, f, xi = vec(row["h"]), vec(row["low_unit_vector"]), vec(row["dual_column"])
    assert dot(f, f) == 1
    M, R, H = weighted(f, f, h), weighted(f, xi, h), weighted(xi, xi, h)
    k_opt, k_plain = R / M, dot(f, xi)
    minimum = H - R * R / M
    plain = H - 2 * R * k_plain + M * k_plain**2
    residual = R - M * k_plain
    assert k_opt == Q(38, 15) and k_plain == 3
    assert minimum == Q(67, 60) < plain == Q(39, 32)
    assert plain - minimum == residual**2 / M == M * (k_plain - k_opt)**2
    results["weight_derived_finite_projection"] = {
        "M": str(M), "R": str(R), "H": str(H), "K_opt": str(k_opt),
        "unweighted_K": str(k_plain), "minimum_gram": str(minimum),
        "unweighted_projection_gram": str(plain), "exact_residual_gap": str(residual**2 / M),
    }

    row = cases["reference_comparison"]
    actual, h = vec(row["actual_tail"]), vec(row["new_weight"])
    old = Q(row["old_scalar"])
    assert all(a >= old and a >= z > 0 for a, z in zip(actual, h, strict=True))
    comparisons = []
    for entries in row["cross_vectors"]:
        b = vec(entries)
        new_penalty, old_penalty = weighted(b, b, h), dot(b, b) / old
        comparisons.append({"cross": entries, "weighted_penalty": str(new_penalty),
                            "old_scalar_penalty": str(old_penalty)})
    assert Q(comparisons[0]["weighted_penalty"]) > Q(comparisons[0]["old_scalar_penalty"])
    assert Q(comparisons[1]["weighted_penalty"]) < Q(comparisons[1]["old_scalar_penalty"])
    results["smaller_floor_does_not_order_coupling_penalties"] = comparisons

    row = cases["strict_leakage_gate"]
    m, g_zero = Q(row["m"]), Q(row["g_zero"])
    gates = []
    for value in row["lambda"]:
        epsilon = max(Q(0), m - g_zero) * Q(value)
        gates.append({"lambda": value, "eta": str(1 - epsilon / m), "qualified": epsilon < m})
    assert [x["qualified"] for x in gates] == [True, False, False]
    results["strict_denominator_boundary"] = gates

    row = cases["source_error_gate"]
    eta, gram = Q(row["eta_lower"]), Q(row["nominal_gram"])
    error = Q(row["low_error"]) + Q(row["gram_error"]) / eta
    gates = []
    for value in row["nominal_low"]:
        lower = Q(value) - gram / eta - error
        gates.append({"nominal_low": value, "nominal_schur": str(Q(value)-gram/eta),
                      "complete_lower": str(lower), "strictly_positive": lower > 0})
    assert [x["strictly_positive"] for x in gates] == [False, True]
    results["one_sided_source_error_boundary"] = gates

    row = cases["norm_gap"]
    a, c, b = Q(row["low"]), Q(row["tail"]), Q(row["cross"])
    gram, sigma = b*b/c, a-b*b/c
    gap = min(sigma / (1+2*gram/c), c/2)
    assert gap == Q(14, 9) and a-gap > 0 and (a-gap)*(c-gap)-b*b > 0
    results["complete_form_norm_gap"] = {"gap": str(gap), "shifted_determinant": str((a-gap)*(c-gap)-b*b)}

    fixed = pins["fixed_reference"]
    T, N = Q(fixed["T"]), fixed["N"]
    alpha, beta, anchor, floor = [Q(fixed[k]) for k in ("alpha", "beta", "R", "positive_floor_m")]
    if (T, N, alpha, beta, anchor, floor, fixed["precision_bits"]) != (Q(3,4),312,Q(1,4),Q(873,1024),Q(256),Q(1,3),384):
        raise ValueError("fixed-case qualification parameters changed")
    ctx.prec = fixed["precision_bits"]
    pi = arb.pi()
    A0 = aq(Q(1,4)).digamma() - pi.log()
    AR = acb(aq(Q(1,4)), aq(anchor)/2).digamma().real - pi.log()
    gamma, s = 1-aq(alpha), 1+aq(beta)-A0
    g_anchor = gamma*(AR-A0+1)-s
    ratio = (T*anchor)**2 / ((2*N+1)*(2*N+3))
    assert 0 <= ratio < 1
    doublefac = factorial(2*N+1)//(2**N*factorial(N))
    E = Q(2*N+1)*(T*anchor)**(2*N)/doublefac**2/(1-ratio)
    leakage = 2*aq(T*anchor)/pi*aq(E)
    deficit = aq(floor)-gamma+s
    epsilon = deficit*leakage
    publication = Q(fixed["epsilon_publication_upper"])
    assert publication == Q(3,10**49)
    assert arb_to_rational_enclosure(g_anchor)[0] > floor
    assert arb_to_rational_enclosure(deficit)[0] > 0
    assert 0 <= arb_to_rational_enclosure(epsilon)[0] <= arb_to_rational_enclosure(epsilon)[1] < publication
    eta_lower = 1-publication/floor
    assert eta_lower > 0 and floor*eta_lower > Q(1,4)
    scalar = {"support": str(T), "N": N, "alpha": str(alpha), "beta": str(beta), "R": str(anchor),
              "m": str(floor), "precision_bits": ctx.prec, "g_R": bounds(g_anchor),
              "complete_leakage": bounds(leakage), "epsilon": bounds(epsilon),
              "published_epsilon_upper": str(publication), "published_eta_lower": str(eta_lower),
              "weighted_reference_norm_lower": str(floor*eta_lower),
              "new_Weil_schur_sign": False}
    modules = {}
    for name, module in sorted(sys.modules.items()):
        if (name == "scripts" or name.startswith("scripts.")) and getattr(module, "__file__", None):
            path = Path(module.__file__).resolve()
            if not path.is_relative_to(ROOT):
                raise RuntimeError("project import escaped the captured source root")
            modules[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"format": "research-energy-aware-schur-controls-v1", "status": "PASS",
            "scope": pins["scope"], "inputs_sha256": hashlib.sha256(raw).hexdigest(),
            "program_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "exact_control_groups": results, "fixed_positive_weight_qualification": scalar,
            "imported_project_modules": modules, "new_low_Weil_matrix": False,
            "all_support_or_comparative_advantage_proved": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=Path(__file__).with_name("control-inputs-v1.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = qualify(args.inputs)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"status": result["status"], "exact_control_groups": len(result["exact_control_groups"]),
                      "fixed_positive_weight_qualified": True, "new_low_Weil_matrix": False}))


if __name__ == "__main__":
    main()
