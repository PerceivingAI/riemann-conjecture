"""Standalone FLINT/stdlib audit of the fixed T=81/100 scalar reference packet."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from math import factorial
from pathlib import Path
import sys

from flint import acb, arb, ctx, fmpq

ROOT = Path(__file__).resolve().parents[2]
T, ALPHA, FLOOR, LOSS = Q(81, 100), Q(1, 4), Q(1, 3), Q(1, 1 << 128)
POLICY = "least even N>=2 satisfying complete leakage outside>=m and epsilon/m<=2^-128; K excluded and K<N/2 required separately"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reject_number(_):
    raise ValueError("nonexact JSON number")


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, "duplicate JSON key")
        obj[key] = value
    return obj


def load(path):
    raw = path.read_bytes()
    return json.loads(raw, parse_float=reject_number, parse_constant=reject_number,
                      object_pairs_hook=unique_object), hashlib.sha256(raw).hexdigest()


def rational(text):
    require(isinstance(text, str), "canonical rational string required")
    value = Q(text)
    require(str(value) == text, "noncanonical rational string")
    return value


def aq(value):
    value = Q(value)
    return arb(value.numerator)/value.denominator


def endpoints(value):
    mid, rad = value.mid().fmpq(), value.rad().fmpq()
    lo, hi = mid-rad, mid+rad
    return Q(int(lo.p), int(lo.q)), Q(int(hi.p), int(hi.q))


def point(value):
    return Q(value), Q(value)


def add(x, y):
    return x[0]+y[0], x[1]+y[1]


def sub(x, y):
    return x[0]-y[1], x[1]-y[0]


def mul(x, y):
    products = [a*b for a in x for b in y]
    return min(products), max(products)


def divide(x, y):
    require(y[0] > 0, "nonpositive interval denominator")
    return mul(x, (1/y[1], 1/y[0]))


def check_enclosure(record, fresh, label):
    require(isinstance(record, dict) and set(record) == {"lower", "upper"}, "invalid enclosure "+label)
    lower, upper = rational(record["lower"]), rational(record["upper"])
    require(lower <= fresh[0] <= fresh[1] <= upper, "dishonest enclosure "+label)


def published(interval):
    magnitude = max(abs(interval[0]), abs(interval[1]))
    exponent = magnitude.numerator.bit_length()-magnitude.denominator.bit_length() if magnitude else 0
    scale = 1 << max(0, 192-exponent)
    return {"lower": str(Q((interval[0]*scale).__floor__(), scale)),
            "upper": str(Q((interval[1]*scale).__ceil__(), scale))}


def audit(source_path, inputs_path):
    ctx.prec = 768
    source, source_hash = load(source_path)
    pins, input_hash = load(inputs_path)
    expected = {
        "format": "t081-qualification-inputs-v1", "support": "81/100",
        "alpha_candidate": "1/4", "reference_floor_candidate": "1/3",
        "frequency_proof_boundary": 256, "initial_interval_width": "1/4",
        "finite_supremum_gap_target": "1/256", "publication_beta_grid": "1/1024",
        "producer_precision_bits": 512, "independent_precision_bits": 768,
        "publication_bits": 192, "eta_loss_target": str(LOSS),
        "reference_anchor_reserve": "1/64", "production_admission": False,
        "reference_anchor_policy": "least integer R>=1 with g(R)>=m+1/64; verify all predecessor anchor comparisons or monotone integer bracket",
        "N_policy": "least even N>=2 and N>2K satisfying complete leakage outside>=m and epsilon/m<=2^-128; K selected separately without target low-gap assumption",
    }
    for key, value in expected.items():
        require(type(pins.get(key)) is type(value) and pins.get(key) == value, "unauthorized input "+key)
    fixed = {"format": "t081-reference-qualification-v1", "status": "SCALAR_REFERENCE_QUALIFIED",
             "support": "81/100", "alpha": "1/4", "m": "1/3", "producer_precision_bits": 512,
             "publication_bits": 192, "frequency_proof_boundary": "256", "finite_gap_target": "1/256",
             "anchor_reserve": "1/64", "eta": str(1-LOSS), "eta_loss_target": str(LOSS),
             "scalar_N_policy": POLICY,
             "parent_K_condition": "K<N/2, to be confirmed separately; not used in scalar minimum",
             "new_support_matrix_computed": False, "complete_low_cross_positivity_proved": False,
             "all_support_estimate_proved": False, "production_admission": False}
    for key, value in fixed.items():
        require(type(source.get(key)) is type(value) and source.get(key) == value, "unauthorized source "+key)
    require(set(source) == set(fixed) | {
        "beta", "active_terms", "support_thresholds", "A0", "coarse_lipschitz_upper",
        "finite_max_lower", "finite_max_upper", "lower_witness_frequency", "infinite_tail_upper",
        "cells", "interval_evaluations", "refinements", "R", "g0", "gR", "anchor_predecessor",
        "N_policy_trials", "N", "M", "Rc", "inverse_weight", "inputs_sha256", "producer_sha256",
        "imported_project_module_sha256", "namespace_package_paths"}, "source schema mismatch")
    require(source["inputs_sha256"] == input_hash, "inputs fingerprint mismatch")
    producer = Path(__file__).resolve().with_name("qualify-reference-v1.py")
    require(source["producer_sha256"] == hashlib.sha256(producer.read_bytes()).hexdigest(), "producer fingerprint mismatch")
    modules = source["imported_project_module_sha256"]
    require(isinstance(modules, dict) and {
        "scripts/cert/constants.py", "scripts/cert/prime_power_terms.py",
        "scripts/weil_reference_route_controls.py"}.issubset(modules), "missing producer dependency binding")
    for name, digest in modules.items():
        path = (ROOT/name).resolve()
        require(path.is_relative_to(ROOT) and path.suffix == ".py" and name.startswith("scripts/"), "unsafe dependency path")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, "dependency fingerprint mismatch "+name)
    for name, paths in source["namespace_package_paths"].items():
        require(name == "scripts" or name.startswith("scripts."), "foreign namespace")
        require(isinstance(paths, list) and paths, "empty namespace path binding")
        for item in paths:
            require((ROOT/item).resolve().is_relative_to(ROOT), "namespace outside source root")

    pi = arb.pi()
    require(arb(5).log() < aq(2*T) < arb(7).log() and aq(2*T) < pi, "support threshold failure")
    # Strict log(5)<2T<log(7) excludes every integer >=7. Independently
    # factor the remaining integers: 6 is not a prime power.
    active = []
    for integer in range(2, 7):
        divisor = next(d for d in range(2, integer+1) if integer % d == 0)
        rest, exponent = integer, 0
        while rest % divisor == 0:
            rest //= divisor
            exponent += 1
        if rest == 1:
            require(arb(integer).log() < aq(2*T), "active boundary unresolved")
            active.append((integer, divisor, exponent))
    require(active == [(2, 2, 1), (3, 3, 1), (4, 2, 2), (5, 5, 1)],
            "independent prime-power enumeration mismatch")
    thresholds = source["support_thresholds"]
    require(set(thresholds) == {"log5", "twice_T", "log7", "pi"}, "threshold schema mismatch")
    require(thresholds["twice_T"] == "81/50", "changed support threshold")
    for name, fresh in [("log5", arb(5).log()), ("log7", arb(7).log()), ("pi", pi)]:
        check_enclosure(thresholds[name], endpoints(fresh), name)
    coefficients = [arb(2).log()/arb(2).sqrt(), arb(3).log()/arb(3).sqrt(), arb(2).log()/2, arb(5).log()/arb(5).sqrt()]
    logs = [arb(m).log() for m in [2, 3, 4, 5]]
    require(len(source["active_terms"]) == 4, "incomplete active list")
    for row, m, p, k, coefficient in zip(source["active_terms"], [2, 3, 4, 5], [2, 3, 2, 5], [1, 1, 2, 1], coefficients, strict=True):
        require(set(row) == {"m", "prime", "exponent", "coefficient"} and
                all(type(row[key]) is int for key in ("m", "prime", "exponent")) and
                (row["m"], row["prime"], row["exponent"]) == (m, p, k), "active arithmetic mismatch")
        check_enclosure(row["coefficient"], endpoints(coefficient), "arithmetic coefficient")

    # Reflection and duplication give psi(1/4)=-gamma-pi/2-3 log(2).
    A0 = endpoints(-arb.const_euler()-pi/2-3*arb(2).log()-pi.log())
    check_enclosure(source["A0"], A0, "A0")
    length, order = 128, 64
    x = Q(length)+Q(1, 4)
    bernoulli = []
    for k in range(1, order+1):
        b = fmpq.bernoulli(2*k)
        bernoulli.append(Q(int(b.p), int(b.q)))
    remainder = abs(bernoulli[-1])/(2*order*x**(2*order))
    weights = {Q(0): point(1)}

    def asymptotic(z):
        inverse = 1/z
        square = inverse*inverse
        power = square
        value = z.log()-inverse/2
        for k, b in enumerate(bernoulli[:-1], start=1):
            value -= aq(b/(2*k))*power
            power *= square
        return value

    real_tail_base = asymptotic(acb(aq(x), 0)).real

    def w(t):
        if t not in weights:
            y = aq(t/2)
            y2 = y*y
            positive = arb(1)
            for n in range(length):
                u = aq(Q(n)+Q(1, 4))
                positive += y2/(u*(u*u+y2))
            logarithmic_tail = asymptotic(acb(aq(x), y)).real-real_tail_base
            lo, hi = endpoints(positive+logarithmic_tail)
            weights[t] = lo-2*remainder, hi+2*remainder
        return weights[t]

    beta = rational(source["beta"])
    require(beta >= 0 and (beta/Q(1, 1024)).denominator == 1, "beta grid failure")

    def g(t):
        return sub(add(A0, mul(point(1-ALPHA), sub(w(t), point(1)))), point(ALPHA+beta))

    exponential = aq(T).exp()

    def rho(t):
        tball = aq(t)
        denominator = tball*tball+aq(Q(1, 4))
        phase = aq(2*T)*tball
        arithmetic = 2*sum((c*(tball*l).cos() for c, l in zip(coefficients, logs)), arb(0))
        return arithmetic-2*exponential*(phase.cos()/2+tball*phase.sin())/denominator+1/denominator

    arithmetic_lip = 2*sum((c*l for c, l in zip(coefficients, logs)), arb(0))
    coarse = endpoints(arithmetic_lip+8*aq(T)*(exponential-1))
    sharp = endpoints(arithmetic_lip+8*((aq(T)-1)*exponential+1))
    lip = rational(source["coarse_lipschitz_upper"])
    require(coarse[1] <= lip and 0 < sharp[0] < sharp[1] < coarse[0], "Lipschitz bound failure")
    current, finite_max, independent_max, checked = Q(0), None, None, 0
    for cell in source["cells"]:
        left, right, claimed = [rational(cell[key]) for key in ("left", "right", "upper")]
        require(left == current and left < right <= 256, "finite partition gap/overlap/order")
        refinement_factor = Q(1, 4)/(right-left)
        require(refinement_factor.denominator == 1 and refinement_factor.numerator & (refinement_factor.numerator-1) == 0,
                "leaf is not a midpoint subdivision")
        require((left/(right-left)).denominator == 1, "misaligned leaf")
        center, halfwidth = (left+right)/2, (right-left)/2
        symbol = endpoints(rho(center))
        fresh = symbol[1]+lip*halfwidth-ALPHA*w(left)[0]
        independent = symbol[1]+sharp[1]*halfwidth-ALPHA*w(left)[0]
        require(fresh <= claimed, "dishonest finite cell upper")
        require(independent <= beta, "independent finite bound exceeds beta")
        finite_max = claimed if finite_max is None else max(finite_max, claimed)
        independent_max = independent if independent_max is None else max(independent_max, independent)
        current, checked = right, checked+1
    require(current == 256 and checked > 0, "incomplete frequency cover")
    require(finite_max == rational(source["finite_max_upper"]) and finite_max <= beta, "finite maximum mismatch")
    require(type(source["refinements"]) is int and source["refinements"] >= 0 and
            checked == 1024+source["refinements"] and
            source["interval_evaluations"] == 1024+2*source["refinements"], "refinement accounting mismatch")
    witness, lower = rational(source["lower_witness_frequency"]), rational(source["finite_max_lower"])
    require(0 <= witness <= 256, "witness outside cover")
    require(lower <= endpoints(rho(witness))[0]-ALPHA*w(witness)[1], "invalid lower witness")
    require(finite_max-lower <= Q(1, 256), "finite supremum gap exceeds target")
    S = 2*sum(coefficients, arb(0))
    denominator = aq(Q(256**2)+Q(1, 4))
    source_tail = endpoints(S+2*(exponential+1)/denominator.sqrt())[1]-ALPHA*w(Q(256))[0]
    claimed_tail = rational(source["infinite_tail_upper"])
    require(source_tail <= claimed_tail, "dishonest infinite tail")
    independent_tail = endpoints(S+2*exponential/denominator.sqrt()+1/denominator)[1]-ALPHA*w(Q(256))[0]
    require(independent_tail <= beta, "independent analytic infinity exceeds beta")
    require(beta == Q((max(Q(0), finite_max, claimed_tail)/Q(1, 1024)).__ceil__())*Q(1, 1024), "beta publication policy mismatch")

    R, N = source["R"], source["N"]
    require(type(R) is int and R >= 1, "invalid anchor")
    require(type(N) is int and N >= 2 and N % 2 == 0, "invalid scalar cutoff")
    g0, gR = g(Q(0)), g(Q(R))
    check_enclosure(source["g0"], g0, "g0")
    check_enclosure(source["gR"], gR, "gR")
    require(g0[1] < FLOOR and gR[0] >= FLOOR+Q(1, 64), "floor/anchor comparison failure")
    if R == 1:
        require(source["anchor_predecessor"] is None, "unexpected predecessor")
    else:
        pred = source["anchor_predecessor"]
        require(pred["R"] == R-1, "wrong predecessor anchor")
        gp = g(Q(R-1))
        check_enclosure(pred["g"], gp, "predecessor")
        require(gp[1] < FLOOR+Q(1, 64), "anchor is not first policy integer")

    def leakage(n, radius):
        c = T*radius
        ratio = c*c/((2*n+1)*(2*n+3))
        if ratio >= 1:
            return ratio, None
        # Independent factorial expression, not the producer's odd-product helper.
        df = factorial(2*n+1)//(2**n*factorial(n))
        exact_tail = Q(2*n+1)*c**(2*n)/df**2/(1-ratio)
        return ratio, endpoints(2*aq(c*exact_tail)/pi)

    trials = source["N_policy_trials"]
    require(len(trials) == (N-2)//2+1, "incomplete policy minimum trials")
    final = None
    for row, n in zip(trials, range(2, N+1, 2), strict=True):
        require(type(row["N"]) is int and row["N"] == n, "missing preceding even cutoff")
        ratio, lam = leakage(n, Q(R))
        require(rational(row["ratio"]) == ratio, "wrong geometric ratio")
        if lam is None:
            require(set(row) == {"N", "ratio", "outcome"}, "ratio-failure row schema mismatch")
            require(n < N and row["outcome"] == "ratio_not_below_one", "invalid ratio-policy failure")
            continue
        require(set(row) == {"N", "ratio", "outcome", "leakage", "outside_lower_form",
                             "epsilon", "epsilon_over_m"}, "eligible row schema mismatch")
        outside = sub(gR, mul(sub(gR, g0), lam))
        epsilon = mul(sub(point(FLOOR), g0), lam)
        relative = divide(epsilon, point(FLOOR))
        for key, value in [("leakage", lam), ("outside_lower_form", outside),
                           ("epsilon", epsilon), ("epsilon_over_m", relative)]:
            check_enclosure(row[key], value, key+" at N="+str(n))
        if n < N:
            require(row["outcome"] == "policy_failure" and (outside[1] < FLOOR or relative[0] > LOSS),
                    "preceding even N has no certified policy failure")
        else:
            require(row["outcome"] == "qualified" and outside[0] >= FLOOR and relative[1] <= LOSS,
                    "final N not qualified")
            final = {"leakage": published(lam), "outside_lower_form": published(outside),
                     "epsilon": published(epsilon), "epsilon_over_m": published(relative)}
    require(final is not None, "no qualifying final trial")
    M, Rc = source["M"], source["Rc"]
    require(type(M) is int and M == 2*N and type(Rc) is int and Rc == 2*R, "doubled inverse cutoff mismatch")
    inverse = source["inverse_weight"]
    ratio, lam = leakage(M, Q(Rc))
    require(lam is not None and lam[1] < 1, "complete inverse leakage not paid")
    gRc = g(Q(Rc))
    a = divide(point(1), gRc)
    kappa = add(a, mul(sub(point(1/FLOOR), a), lam))
    require(0 < a[0] <= a[1] < 1/FLOOR and kappa[1] < 1/FLOOR, "no strict inverse-weight gain")
    require(rational(inverse["ratio"]) == ratio and rational(inverse["global_upper"]) == 1/FLOOR, "inverse policy mismatch")
    for key, value in [("gRc", gRc), ("a", a), ("complete_leakage", lam), ("kappa", kappa)]:
        check_enclosure(inverse[key], value, "inverse "+key)
    return {
        "format": "t081-reference-qualification-audit-v1", "status": "PASS",
        "source_sha256": source_hash, "inputs_sha256": input_hash,
        "audit_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "audit_precision_bits": 768, "publication_bits": 192,
        "support": str(T), "alpha": str(ALPHA), "m": str(FLOOR), "beta": str(beta),
        "complete_intervals_checked": checked, "finite_gap": str(finite_max-lower),
        "independent_finite_upper": published(point(independent_max)),
        "independent_infinite_tail_upper": published(point(independent_tail)),
        "R": R, "N": N, "M": M, "Rc": Rc, "eta": str(1-LOSS),
        "policy_minimum_even_cutoffs_checked": len(trials), "scalar_N_policy": POLICY,
        "reference_controls": final,
        "inverse_weight": {"a": published(a), "kappa": published(kappa), "complete_leakage": published(lam)},
        "energy_organization": {"positive_digamma_difference_terms": length,
                                "logarithmic_tail_order": order,
                                "each_shifted_digamma_remainder_upper": str(remainder),
                                "A0": "-EulerGamma-pi/2-3*log(2)-log(pi)"},
        "symbol_organization": "real trigonometric quotient; no producer math imports",
        "shared_trust": "FLINT/Arb arithmetic, transcendental enclosures and exact Bernoulli numbers",
        "parent_K_condition": source["parent_K_condition"],
        "new_support_matrix_computed": False, "complete_low_cross_positivity_proved": False,
        "all_support_estimate_proved": False, "production_admission": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be a fresh path")
    try:
        result = audit(args.source, args.inputs)
    except (ValueError, KeyError, TypeError, ZeroDivisionError, OSError, OverflowError, AttributeError, IndexError) as exc:
        print(json.dumps({"status": "REJECTED", "error": str(exc)}))
        raise SystemExit(2)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k: result[k] for k in ("status", "beta", "R", "N", "M", "Rc")}))


if __name__ == "__main__":
    main()
