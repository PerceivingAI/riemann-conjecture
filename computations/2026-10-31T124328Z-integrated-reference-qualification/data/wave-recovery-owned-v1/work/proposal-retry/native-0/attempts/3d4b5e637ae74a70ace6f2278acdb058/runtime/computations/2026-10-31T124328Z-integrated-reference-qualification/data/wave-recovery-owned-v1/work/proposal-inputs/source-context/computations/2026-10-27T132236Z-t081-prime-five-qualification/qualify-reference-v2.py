"""Fixed T=81/100 scalar reference qualification; no matrix, sign, or admission."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import heapq
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from flint import acb, arb, ctx
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms
from scripts.weil_reference_route_controls import archimedean, ball, legendre_tail

BITS = 192
T, ALPHA, FLOOR = Q(81, 100), Q(1, 4), Q(1, 3)
LOSS = Q(1, 1 << 128)
SCALAR_POLICY = "least even N>=2 satisfying complete leakage outside>=m and epsilon/m<=2^-128; K excluded and K<N/2 required separately"


def reject_number(_):
    raise ValueError("nonexact JSON number")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def load_inputs(path):
    raw = path.read_bytes()
    pins = json.loads(raw, parse_float=reject_number, parse_constant=reject_number,
                      object_pairs_hook=unique_object)
    required = {
        "format": "t081-qualification-inputs-v1", "support": "81/100",
        "alpha_candidate": "1/4", "reference_floor_candidate": "1/3",
        "frequency_proof_boundary": 256, "initial_interval_width": "1/4",
        "finite_supremum_gap_target": "1/256", "publication_beta_grid": "1/1024",
        "producer_precision_bits": 512, "independent_precision_bits": 768,
        "publication_bits": 192, "eta_loss_target": str(LOSS),
        "reference_anchor_reserve": "1/64", "production_admission": False,
        "reference_anchor_policy": "least integer R>=1 with g(R)>=m+1/64; verify all predecessor anchor comparisons or monotone integer bracket",
    }
    if any(type(pins.get(k)) is not type(v) or pins.get(k) != v for k, v in required.items()):
        raise ValueError("unsupported fixed qualification inputs")
    if pins.get("N_policy") != "least even N>=2 and N>2K satisfying complete leakage outside>=m and epsilon/m<=2^-128; K selected separately without target low-gap assumption":
        raise ValueError("unknown combined N/K policy")
    return pins, hashlib.sha256(raw).hexdigest()


def rounded(x):
    lower, upper = arb_to_rational_enclosure(x)
    magnitude = max(abs(lower), abs(upper))
    exponent = magnitude.numerator.bit_length() - magnitude.denominator.bit_length() if magnitude else 0
    scale = 1 << max(0, BITS - exponent)
    return Q((lower * scale).__floor__(), scale), Q((upper * scale).__ceil__(), scale)


def enclosure(x):
    lower, upper = rounded(x)
    return {"lower": str(lower), "upper": str(upper)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module_bindings():
    files, namespaces = {}, {}
    for name, module in sorted(sys.modules.items()):
        if name == "scripts" or name.startswith("scripts."):
            if getattr(module, "__file__", None) is None:
                namespaces[name] = sorted({Path(p).resolve().relative_to(ROOT).as_posix()
                                           for p in module.__path__})
            else:
                path = Path(module.__file__).resolve()
                files[path.relative_to(ROOT).as_posix()] = sha(path)
    return files, namespaces


def evaluate(inputs):
    pins, inputs_hash = load_inputs(inputs)
    ctx.prec = pins["producer_precision_bits"]
    terms = enumerate_active_prime_power_terms(81, 100, prec=ctx.prec)
    if [(x.m, x.prime, x.exponent) for x in terms] != [(2, 2, 1), (3, 3, 1), (4, 2, 2), (5, 5, 1)]:
        raise ValueError("active prime powers changed")
    if not arb(5).log() < ball(2*T) < arb(7).log() or not ball(2*T) < arb.pi():
        raise ValueError("strict support thresholds not certified")
    if not (terms[2].von_mangoldt-arb(2).log()).contains(0):
        raise ValueError("Lambda(4) is not log(2)")
    A0 = archimedean(Q(0))
    exponential = ball(T).exp()
    cache = {}

    def w(t):
        if t not in cache:
            cache[t] = archimedean(t)-A0+1
        return cache[t]

    def g(t):
        return A0+(1-ball(ALPHA))*(w(t)-1)-ball(ALPHA+beta)

    def rho(t):
        z = acb(ball(Q(1, 2)), ball(t))
        continuum = ((z*ball(2*T)).exp()-1)/z
        return 2*sum((x.coefficient*(ball(t)*x.log_m).cos() for x in terms), arb(0))-2*continuum.real

    lip = rounded(2*sum((x.coefficient*x.log_m for x in terms), arb(0))
                  +8*ball(T)*(exponential-1))[1]
    heap = []
    best_lower = None
    witness = None
    evaluations = 0

    def add(left, right):
        nonlocal best_lower, witness, evaluations
        center = (left+right)/2
        symbol = rho(center)
        upper = rounded(symbol+ball(lip*(right-left)/2)-ball(ALPHA)*w(left))[1]
        lower = rounded(symbol-ball(ALPHA)*w(center))[0]
        if best_lower is None or lower > best_lower:
            best_lower, witness = lower, center
        heapq.heappush(heap, (-upper, left, right))
        evaluations += 1

    boundary, width, gap = Q(256), Q(pins["initial_interval_width"]), Q(1, 256)
    for i in range(int(boundary/width)):
        add(i*width, (i+1)*width)
    refinements = 0
    while -heap[0][0]-best_lower > gap:
        _, left, right = heapq.heappop(heap)
        center = (left+right)/2
        add(left, center)
        add(center, right)
        refinements += 1
    finite_upper = -heap[0][0]
    S = 2*sum((x.coefficient for x in terms), arb(0))
    tail = rounded(S+2*(exponential+1)/ball(boundary**2+Q(1, 4)).sqrt()-ball(ALPHA)*w(boundary))[1]
    grid = Q(1, 1024)
    beta = Q((max(Q(0), finite_upper, tail)/grid).__ceil__())*grid
    global_beta = beta
    baseline = pins["baseline_global_bound"]
    for name in ("source", "inputs", "audit"):
        path = (ROOT / baseline[name+"_path"]).resolve()
        if not path.is_relative_to(ROOT) or sha(path) != baseline[name+"_sha256"]:
            raise ValueError("changed baseline global-bound premise")
    old = json.loads((ROOT/baseline["source_path"]).read_text(encoding="utf-8"))
    if (old["support"], old["alpha"], old["beta"]) != ("4/5", "1/4", "859/1024"):
        raise ValueError("unsupported baseline global-bound premise")
    if not (ball(T) < arb(5).log() < ball(2*T) and ball(T) < ball(Q(8, 5))):
        raise ValueError("new compressed shifts do not have disjoint domain/range")
    c5 = terms[3].coefficient
    continuum_increment = 2*(ball(T).exp()-ball(Q(4, 5)).exp())
    increment = c5+continuum_increment
    unrounded_beta = ball(Q(859, 1024))+increment
    transfer_beta = Q((rounded(unrounded_beta)[1]/grid).__ceil__())*grid
    beta = min(global_beta, transfer_beta)
    transfer = {"baseline_global_bound": baseline, "baseline_support": "4/5",
                "baseline_beta": "859/1024", "coefficient5": enclosure(c5),
                "added_continuum_norm": enclosure(continuum_increment),
                "increment": enclosure(increment), "unrounded_beta": enclosure(unrounded_beta),
                "grid_beta": str(transfer_beta),
                "domain": "supported_H_T_only_not_a_pointwise_Fourier_symbol_bound"}
    R = 1
    while True:
        lower, upper = rounded(g(Q(R)))
        if lower >= FLOOR+Q(1, 64):
            break
        if upper >= FLOOR+Q(1, 64):
            raise ValueError("anchor comparison unresolved at fixed precision")
        R += 1
    g0, gR = g(Q(0)), g(Q(R))
    if not g0 < ball(FLOOR):
        raise ValueError("missing premise: first-anchor floor comparison g(0)<m")

    def controls(n, radius):
        c = T*radius
        ratio = c*c/((2*n+1)*(2*n+3))
        if ratio >= 1:
            return {"N": n, "ratio": str(ratio), "outcome": "ratio_not_below_one"}
        leakage = 2*ball(c)/arb.pi()*ball(legendre_tail(c, n))
        outside = gR-(gR-g0)*leakage
        epsilon = (ball(FLOOR)-g0)*leakage
        outside_bounds, loss_bounds = rounded(outside), rounded(epsilon/ball(FLOOR))
        passed = outside_bounds[0] >= FLOOR and loss_bounds[1] <= LOSS
        if not passed and not (outside_bounds[1] < FLOOR or loss_bounds[0] > LOSS):
            raise ValueError("N-policy comparison unresolved at fixed precision")
        return {"N": n, "ratio": str(ratio), "leakage": enclosure(leakage),
                "outside_lower_form": enclosure(outside), "epsilon": enclosure(epsilon),
                "epsilon_over_m": enclosure(epsilon/ball(FLOOR)),
                "outcome": "qualified" if passed else "policy_failure"}

    trials = []
    N = 2
    while True:
        row = controls(N, Q(R))
        trials.append(row)
        if row["outcome"] == "qualified":
            break
        N += 2
    M, Rc = 2*N, 2*R
    c = T*Rc
    ratio = c*c/((2*M+1)*(2*M+3))
    leakage = 2*ball(c)/arb.pi()*ball(legendre_tail(c, M))
    a = 1/g(Q(Rc))
    kappa = a+(1/ball(FLOOR)-a)*leakage
    if not (0 < a < 1/ball(FLOOR) and leakage < 1 and kappa < 1/ball(FLOOR)):
        raise ValueError("missing premise: strict complete inverse-weight gain at doubled cutoff")
    cells = [{"left": str(left), "right": str(right), "upper": str(-negative)}
             for negative, left, right in sorted(heap, key=lambda row: row[1])]
    modules, namespaces = module_bindings()
    return {
        "format": "t081-supported-reference-qualification-v1", "status": "SCALAR_REFERENCE_QUALIFIED",
        "support": str(T), "alpha": str(ALPHA), "m": str(FLOOR), "beta": str(beta),
        "reference_bound_kind": "minimum_of_fresh_global_symbol_and_supported_prime5_transfer",
        "global_symbol_beta": str(global_beta), "support_transfer": transfer,
        "producer_precision_bits": 512, "publication_bits": BITS,
        "frequency_proof_boundary": "256", "finite_gap_target": "1/256",
        "active_terms": [{"m": x.m, "prime": x.prime, "exponent": x.exponent,
                          "coefficient": enclosure(x.coefficient)} for x in terms],
        "support_thresholds": {"log5": enclosure(arb(5).log()), "twice_T": "81/50",
                               "log7": enclosure(arb(7).log()), "pi": enclosure(arb.pi())},
        "A0": enclosure(A0), "coarse_lipschitz_upper": str(lip),
        "finite_max_lower": str(best_lower), "finite_max_upper": str(finite_upper),
        "lower_witness_frequency": str(witness), "infinite_tail_upper": str(tail),
        "cells": cells, "interval_evaluations": evaluations, "refinements": refinements,
        "R": R, "anchor_reserve": "1/64", "g0": enclosure(g0), "gR": enclosure(gR),
        "anchor_predecessor": None if R == 1 else {"R": R-1, "g": enclosure(g(Q(R-1)))},
        "scalar_N_policy": SCALAR_POLICY, "N_policy_trials": trials, "N": N,
        "eta": str(1-LOSS), "eta_loss_target": str(LOSS),
        "parent_K_condition": "K<N/2, to be confirmed separately; not used in scalar minimum",
        "M": M, "Rc": Rc,
        "inverse_weight": {"gRc": enclosure(g(Q(Rc))), "a": enclosure(a),
                           "ratio": str(ratio), "complete_leakage": enclosure(leakage),
                           "kappa": enclosure(kappa), "global_upper": str(1/FLOOR)},
        "inputs_sha256": inputs_hash, "producer_sha256": sha(Path(__file__)),
        "imported_project_module_sha256": modules, "namespace_package_paths": namespaces,
        "new_support_matrix_computed": False, "complete_low_cross_positivity_proved": False,
        "all_support_estimate_proved": False, "production_admission": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be a fresh path")
    result = evaluate(args.inputs)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k: result[k] for k in ("status", "beta", "R", "N", "M", "Rc")}))


if __name__ == "__main__":
    main()
