"""Independent signed whole-line T=1 reference audit, without target matrices.

Only Python's standard library and FLINT are imported. The comparison proof is replayed in a subprocess solely to validate the
comparison. The new inequality uses a real quotient and a Binet enclosure.
Native Arb balls must be contained in every published analytic interval.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

from flint import acb, arb, ctx, fmpq

ROOT = Path(__file__).resolve().parents[2]
sys.set_int_max_str_digits(0)
T, ALPHA, FLOOR = Q(1), Q(1, 4), Q(1, 3)
LOSS, GOAL, GRID = Q(1, 1 << 128), Q(1, 1 << 78), Q(1, 1024)
PINNED = {
    "accuracy_control": ("computations/2026-10-28T183329Z-t081-retained-completion/data/run-v1/retained-acceptance-v1.json", "3537ac3b419ce9e77241ae278fd1b0ef1301290e9b0e7d3125ccdf985c4474d5"),
    "comparison_audit": ("computations/2026-10-28T220029Z-t1-reference-cost-qualification/data/audit-v2.json", "53fe8418ee5e5e6fce981f24dd704593a52e9f1646ce860966511cf8cba9f2e4"),
    "comparison_inputs": ("computations/2026-10-28T220029Z-t1-reference-cost-qualification/inputs-v1.json", "59a067a652d4ac7b13add553116d092a3a8e492a2cacca6b1bc92d2554d9bde7"),
    "comparison_manifest": ("computations/2026-10-28T220029Z-t1-reference-cost-qualification/manifest.json", "cca77386d39105a7d314e0422b385c5fe02bb971cece6604fd5eba4cb1fbca21"),
    "comparison_source": ("computations/2026-10-28T220029Z-t1-reference-cost-qualification/data/source-v1.json", "7238a102652c3c1519eca2555d8b167735452697c068a4aa9b76aca7d3ce997a"),
}
COMPARISON_BETA = Q(3359, 1024)
FALSE_DECLARATIONS = {
    "gauss_accuracy_achieved", "high_mode_widths_achieved", "target_high_mode_widths_achieved",
    "target_memory_measured", "target_runtime_measured",
}


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


def load(path):
    raw = path.read_bytes()
    return json.loads(raw, parse_float=reject_number, parse_constant=reject_number,
                      object_pairs_hook=unique_object), hashlib.sha256(raw).hexdigest()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rational(text):
    require(isinstance(text, str), "canonical rational string required")
    result = Q(text)
    require(str(result) == text, "noncanonical rational string: " + text)
    return result


def exact_fields(record, expected, label):
    require(isinstance(record, dict), "invalid " + label)
    for key, value in expected.items():
        require(type(record.get(key)) is type(value) and record[key] == value,
                "incorrect " + label + "." + key)


def aq(value):
    value = Q(value)
    return arb(value.numerator) / value.denominator


def endpoints(value):
    require(value.is_finite(), "nonfinite native analytic enclosure")
    midpoint, radius = value.mid().fmpq(), value.rad().fmpq()
    lower, upper = midpoint - radius, midpoint + radius
    return Q(int(lower.p), int(lower.q)), Q(int(upper.p), int(upper.q))


def bounds(record, label):
    require(isinstance(record, dict) and set(record) == {"lower", "upper"},
            "invalid interval " + label)
    lower, upper = rational(record["lower"]), rational(record["upper"])
    require(lower <= upper, "reversed interval " + label)
    return lower, upper


def ceil_log2(value):
    value = Q(value)
    require(value > 0, "nonpositive log2 argument")
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    power = Q(2) ** exponent
    return exponent if value <= power else exponent + 1


def formal_coefficients(order):
    """Remove the pole, formally divide, then subtract the even polar part."""
    denominator = [Q(0)] + [Q((-1) ** (j + 1) * 2 ** j, math.factorial(j))
                            for j in range(1, order + 3)]
    regular, result = [], []
    for n in range(order + 1):
        rhs = Q(-1, 2) ** (n + 1) / math.factorial(n + 1) - denominator[n + 2] / 2
        rhs -= sum((denominator[j] * regular[n + 1 - j]
                    for j in range(2, n + 2)), Q(0))
        quotient = rhs / denominator[1]
        regular.append(quotient)
        polar = Q(2, 2 ** n * math.factorial(n)) if n % 2 == 0 else Q(0)
        result.append(-T ** (n + 1) * (quotient - polar))
    require(result[1] == T * T / 48, "formal division normalization")
    return result


def direct_tail(n, radius):
    """Exact double factorial, not the producer's n-to-n recurrence."""
    c = T * radius
    ratio = c * c / ((2 * n + 1) * (2 * n + 3))
    require(ratio < 1, "geometric-invalid leakage cutoff")
    double_factorial = math.factorial(2 * n + 1) // (2 ** n * math.factorial(n))
    tail = Q(2 * n + 1) * c ** (2 * n) / double_factorial ** 2 / (1 - ratio)
    return ratio, 2 * c * tail


def check_modules(producer, modules):
    """Hash project dependencies and inspect import closure without importing them."""
    require(isinstance(modules, dict) and modules, "missing producer module bindings")
    for name, expected in modules.items():
        require(isinstance(name, str) and isinstance(expected, str), "invalid module binding")
        path = (ROOT / name).resolve()
        require(name.startswith("scripts/") and path.is_relative_to(ROOT)
                and path.suffix == ".py", "unsafe producer module path")
        require(digest(path) == expected, "changed producer module: " + name)
    pending, seen = [producer], set()
    while pending:
        path = pending.pop()
        if path in seen:
            continue
        seen.add(path)
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [node.module or ""]
            else:
                continue
            for name in names:
                if not name.startswith("scripts."):
                    continue
                dependency = ROOT.joinpath(*name.split(".")).with_suffix(".py")
                if not dependency.is_file():
                    dependency = ROOT.joinpath(*name.split("."), "__init__.py")
                require(dependency.is_file(), "unresolved producer import " + name)
                require(dependency.relative_to(ROOT).as_posix() in modules,
                        "unbound producer dependency " + name)
                pending.append(dependency)


def replay_comparison(retained):
    checker = ROOT / PINNED["comparison_manifest"][0]
    checker = checker.with_name("verify-reference-v2.py")
    prior = retained["comparison_audit"]
    require(digest(checker) == prior["audit_code_sha256"], "comparison checker fingerprint mismatch")
    manifest = retained["comparison_manifest"]
    exact_fields(manifest, {"format": "t1-reference-cost-research-manifest-v1",
                            "status": "SCALAR_REFERENCE_ERROR_AND_COST_ONLY",
                            "production_admission": False, "RH_status": "UNRESOLVED",
                            "target_matrix_computed": False, "target_positivity_proved": False},
                 "comparison manifest")
    members = manifest["members"]
    require(isinstance(members, list), "missing comparison manifest members")
    indexed = {}
    for member in members:
        name = member["path"]
        require(isinstance(name, str) and name not in indexed, "duplicate comparison manifest member")
        indexed[name] = member
    for name in ("comparison_source", "comparison_inputs", "comparison_audit"):
        path = ROOT / PINNED[name][0]
        relative = path.relative_to(checker.parent).as_posix()
        exact_fields(indexed[relative], {"sha256": PINNED[name][1], "bytes": path.stat().st_size},
                     "comparison manifest " + relative)
    exact_fields(indexed[checker.name], {"sha256": digest(checker), "bytes": checker.stat().st_size},
                 "comparison manifest checker")
    with tempfile.TemporaryDirectory(prefix="t1_direct_comparison_") as directory:
        output = Path(directory) / "audit.json"
        process = subprocess.run(
            [sys.executable, "-B", str(checker),
             "--inputs", str(ROOT / PINNED["comparison_inputs"][0]),
             "--source", str(ROOT / PINNED["comparison_source"][0]), "--output", str(output)],
            cwd=ROOT, capture_output=True, text=True)
        require(process.returncode == 0 and output.is_file(),
                "comparison native proof failed: " + process.stdout + process.stderr)
        fresh, _ = load(output)
        require(fresh == prior, "comparison audit does not replay exactly")
    return digest(checker)


def weight_encloser():
    """Positive digamma differences and a uniform order-64 Binet tail.

    Shift x=1/4 by 128. The Binet remainder after B_126 is bounded
    uniformly in Im(z) by |B_128|/(128*Re(z)^128). Applying this at
    x+it/2 and x costs twice that bound. No producer digamma is used.
    """
    length, order = 128, 64
    x = Q(length) + Q(1, 4)
    bernoulli = []
    for k in range(1, order + 1):
        value = fmpq.bernoulli(2 * k)
        bernoulli.append(Q(int(value.p), int(value.q)))
    remainder = abs(bernoulli[-1]) / (2 * order * x ** (2 * order))

    def asymptotic(z):
        inverse = 1 / z
        square = inverse * inverse
        power, value = square, z.log() - inverse / 2
        for k, b in enumerate(bernoulli[:-1], start=1):
            value -= aq(b / (2 * k)) * power
            power *= square
        return value

    base = asymptotic(acb(aq(x), 0)).real
    cache = {Q(0): arb(1)}

    def w(t):
        t = Q(t)
        if t not in cache:
            y = aq(t / 2)
            y2 = y * y
            positive = arb(1)
            for n in range(length):
                u = aq(Q(n) + Q(1, 4))
                positive += y2 / (u * (u * u + y2))
            cache[t] = (positive + asymptotic(acb(aq(x), y)).real - base
                        + arb(0, aq(2 * remainder)))
        return cache[t]

    return w


def verify_direct(source, recognized, checks):
    ctx.prec = 768
    terms = [arb(prime).log() / arb(integer).sqrt() for integer, prime, _ in recognized]
    logs = [arb(integer).log() for integer, _, _ in recognized]
    require(arb(7).log() < 2 < arb(8).log() and 2 < arb.pi(),
            "direct support requires log7<2<log8 and 2<pi")
    arithmetic = sum(terms, arb(0))
    arithmetic_lip = 2 * sum((c * shift for c, shift in zip(terms, logs, strict=True)), arb(0))
    exponential = arb(1).exp()
    # The continuum is -2*integral_0^2 exp(x/2)*cos(tx) dx. Bounding
    # x by 2 gives 8(e-1); integrating 2*x*exp(x/2) exactly gives 8.
    coarse = arithmetic_lip + 8 * (exponential - 1)
    sharp = arithmetic_lip + 8
    w = weight_encloser()

    def rho(t):
        t = aq(t)
        denominator = t * t + aq(Q(1, 4))
        phase = 2 * t
        return (2 * sum((c * (t * shift).cos() for c, shift in zip(terms, logs, strict=True)), arb(0))
                - 2 * exponential * (phase.cos() / 2 + t * phase.sin()) / denominator
                + 1 / denominator)

    direct = source["direct_bound"]
    require(isinstance(direct, dict) and set(direct) == {
        "frequency_proof_boundary", "initial_interval_width", "global_gap_target",
        "finite_max_lower", "finite_max_upper", "lower_witness_frequency", "infinite_tail_upper",
        "whole_line_upper", "coarse_lipschitz_upper", "cells", "interval_evaluations", "boundary_stages"},
        "unexpected direct proof declaration fields")
    exact_fields(direct, {"initial_interval_width": "1/4", "global_gap_target": "1/256"}, "direct policy")
    boundary = rational(direct["frequency_proof_boundary"])
    ratio = boundary / 256
    require(ratio.denominator == 1 and ratio >= 1 and ratio.numerator & (ratio.numerator - 1) == 0,
            "final frequency boundary violates power-of-two extension policy")
    lip = rational(direct["coarse_lipschitz_upper"])
    require(0 < endpoints(coarse)[0] <= endpoints(coarse)[1] <= lip,
            "false source coarse Lipschitz upper")
    require(endpoints(sharp)[1] < lip, "independent sharper Lipschitz constant unavailable")
    beta = rational(source["beta"])
    require(beta >= 0 and (beta / GRID).denominator == 1, "beta grid failure")
    cells = direct["cells"]
    require(isinstance(cells, list) and cells, "missing finite frequency cover")
    endpoint, uppers = Q(0), []
    independent_finite = None
    for index, cell in enumerate(cells):
        require(isinstance(cell, dict) and set(cell) == {"left", "right", "upper"},
                "invalid direct frequency cell")
        left, right, upper = (rational(cell[key]) for key in ("left", "right", "upper"))
        width = right - left
        require(left == endpoint and 0 <= left < right <= boundary,
                "frequency cover has a gap, overlap, reversed cell or missing endpoint at leaf " + str(index))
        refinement = Q(1, 4) / width
        require(refinement.denominator == 1 and refinement >= 1
                and refinement.numerator & (refinement.numerator - 1) == 0
                and (left / width).denominator == 1,
                "frequency leaf is not an aligned dyadic subdivision at leaf " + str(index))
        center = (left + right) / 2
        symbol = rho(center)
        weight = w(left)
        coarse_upper = endpoints(symbol + aq(lip * width / 2) - aq(ALPHA) * weight)[1]
        sharp_upper = endpoints(symbol + sharp * aq(width / 2) - aq(ALPHA) * weight)[1]
        require(coarse_upper <= upper, "false direct cell upper at leaf " + str(index))
        require(sharp_upper <= beta, "independent direct inequality fails at leaf " + str(index))
        independent_finite = sharp_upper if independent_finite is None else max(independent_finite, sharp_upper)
        checks["direct_native_cell_upper_checks"] += 2
        endpoint = right
        uppers.append(upper)
    require(endpoint == boundary, "finite frequency cover misses final boundary endpoint")
    finite_upper = rational(direct["finite_max_upper"])
    require(finite_upper == max(uppers), "finite maximum is not the maximum of every direct leaf")
    witness = rational(direct["lower_witness_frequency"])
    require(0 <= witness <= boundary, "finite lower witness is outside the frequency cover")
    finite_lower = rational(direct["finite_max_lower"])
    witness_lower = endpoints(rho(witness) - aq(ALPHA) * w(witness))[0]
    require(finite_lower <= witness_lower <= finite_upper, "false finite witness lower bound")
    checks["direct_native_witness_checks"] += 1

    def tail_at(edge):
        # The positive digamma series proves w increasing on [0,infinity).
        # The real continuum is bounded by 2(e+1)/sqrt(t^2+1/4).
        # Evenness of cos, t*sin(2t), and w covers negative frequencies.
        denominator = aq(edge * edge + Q(1, 4))
        source_cap = 2 * arithmetic + 2 * (exponential + 1) / denominator.sqrt() - aq(ALPHA) * w(edge)
        # Only the oscillating numerator carries e; the remaining quotient
        # contributes exactly 1/(t^2+1/4), a smaller independent cap.
        sharp_cap = 2 * arithmetic + 2 * exponential / denominator.sqrt() + 1 / denominator - aq(ALPHA) * w(edge)
        return endpoints(source_cap)[1], endpoints(sharp_cap)[1]

    tail = rational(direct["infinite_tail_upper"])
    native_tail, independent_tail = tail_at(boundary)
    require(native_tail <= tail, "unpaid infinite frequency tail: false analytic infinity cap")
    require(independent_tail <= beta, "unpaid infinite frequency tail: independent infinity cap exceeds beta")
    checks["direct_native_infinity_checks"] += 2
    whole_upper = rational(direct["whole_line_upper"])
    require(whole_upper == max(Q(0), finite_upper, tail), "incorrect whole-line maximum")
    require(finite_lower <= whole_upper and whole_upper - finite_lower <= Q(1, 256),
            "whole-line gap exceeds 1/256")
    require(beta == math.ceil(whole_upper / GRID) * GRID and beta - GRID < whole_upper <= beta,
            "beta is not the first upward 1/1024 grid point")
    stages = direct["boundary_stages"]
    require(isinstance(stages, list) and len(stages) == ratio.numerator.bit_length(),
            "missing boundary extension chronology")
    preceding_lower, preceding_leaves = None, 0
    preceding_boundary = Q(0)
    for index, stage in enumerate(stages):
        require(isinstance(stage, dict) and set(stage) == {
            "boundary", "finite_lower", "finite_upper", "infinite_tail_upper", "leaves"},
            "invalid boundary chronology record")
        edge = Q(256 * 2 ** index)
        exact_fields(stage, {"boundary": str(edge)}, "boundary extension")
        lower, upper, cap = (rational(stage[key]) for key in ("finite_lower", "finite_upper", "infinite_tail_upper"))
        leaves = stage["leaves"]
        require(type(leaves) is int and leaves >= preceding_leaves + int((edge - preceding_boundary) * 4),
                "boundary stage leaf count violates dyadic extension policy")
        require(lower <= upper and (preceding_lower is None or preceding_lower <= lower),
                "boundary chronology has impossible witness ordering")
        require(tail_at(edge)[0] <= cap, "false boundary-stage analytic infinity cap")
        checks["direct_native_infinity_checks"] += 1
        preceding_lower, preceding_leaves, preceding_boundary = lower, leaves, edge
    exact_fields(stages[-1], {"finite_lower": str(finite_lower), "finite_upper": str(finite_upper),
                             "infinite_tail_upper": str(tail), "leaves": len(cells)}, "final boundary stage")
    # Each initial width-1/4 leaf costs one evaluation; each bisection two.
    exact_fields(direct, {"interval_evaluations": 2 * len(cells) - int(4 * boundary)}, "direct evaluation chronology")
    checks["direct_leaves"] = len(cells)
    checks["direct_boundary_stages"] = len(stages)
    return {"frequency_proof_boundary": str(boundary), "whole_line_upper": str(whole_upper),
            "finite_witness_lower": str(finite_lower), "independent_finite_upper": str(independent_finite),
            "independent_infinite_upper": str(independent_tail), "negative_frequencies_by_evenness": True,
            "uniform_binet_prefix_terms": 128, "uniform_binet_order": 64,
            "source_coarse_lipschitz_checked": True, "independent_lipschitz": "arithmetic_lip+8"}


def audit(inputs_path, source_path):
    pins, input_hash = load(inputs_path)
    source, source_hash = load(source_path)
    expected_inputs = {
        "format": "t1-direct-reference-inputs-v1", "support": "1", "alpha": "1/4", "m": "1/3",
        "comparison_beta": str(COMPARISON_BETA), "created": "2026-10-29T00:46:11Z",
        "bound_kind": "direct_whole_line_multiplier", "accuracy_goal": str(GOAL),
        "accuracy_control_divisor": 1 << 20, "anchor_reserve": "1/64", "beta_grid": str(GRID),
        "eta_loss": str(LOSS), "scalar_precision_bits": 512, "independent_precision_bits": 1024,
        "matrix_publication_bits": 256, "publication_bits": 192, "numerical_guard_bits": 512,
        "precision_block_bits": 512, "source_precision_floor_bits": 3072,
        "audit_precision_floor_bits": 4096, "production_admission": False, "target_low_gap_assumed": False,
        "global_gap_target": "1/256", "initial_frequency_boundary": 256,
        "initial_interval_width": "1/4", "boundary_growth_factor": 2,
    }
    exact_fields(pins, expected_inputs, "inputs")
    require(set(pins) == set(expected_inputs) | {"pins"}, "unexpected input policy field")
    require(isinstance(pins["pins"], dict) and set(pins["pins"]) == set(PINNED), "changed comparison premise set")
    retained = {}
    for name, (path, sha256) in PINNED.items():
        exact_fields(pins["pins"][name], {"path": path, "sha256": sha256}, "pin " + name)
        require(set(pins["pins"][name]) == {"path", "sha256"}, "unexpected pin field")
        record, actual_hash = load(ROOT / path)
        require(actual_hash == sha256, "changed retained premise " + name)
        retained[name] = record
    comparison = retained["comparison_source"]
    exact_fields(comparison, {"format": "t1-reference-cost-source-v1",
                             "status": "SCALAR_REFERENCE_AND_ERROR_QUALIFIED_NOT_POSITIVITY",
                             "support": "1", "alpha": "1/4", "m": "1/3", "beta": str(COMPARISON_BETA),
                             "eta": str(1 - LOSS), "target_matrix_computed": False,
                             "target_positivity_proved": False, "production_admission": False}, "comparison")
    comparison_checker_hash = replay_comparison(retained)
    sigma = rational(retained["accuracy_control"]["sigma_selected_low_Schur"])
    require(0 < GOAL <= sigma / (1 << 20), "accuracy choice exceeds retained control")
    producer = Path(__file__).resolve().with_name("qualify-direct-v1.py")
    producer_hash = digest(producer)
    expected_source = {
        "format": "t1-direct-reference-source-v1", "status": "DIRECT_REFERENCE_AND_ERROR_QUALIFIED_NOT_POSITIVITY",
        "support": "1", "alpha": "1/4", "m": "1/3", "eta": str(1 - LOSS),
        "reference_kind": "direct_whole_line_multiplier", "inputs_sha256": input_hash,
        "producer_sha256": producer_hash, "target_matrix_computed": False,
        "target_positivity_proved": False, "production_admission": False, "RH_status": "UNRESOLVED",
    }
    exact_fields(source, expected_source, "source")
    for key in FALSE_DECLARATIONS & source.keys():
        exact_fields(source, {key: False}, "unachieved numerical declaration")
    require(set(source) - FALSE_DECLARATIONS == set(expected_source) | {
        "beta", "R", "N", "M", "Rc", "K", "active_terms", "direct_bound", "reference",
        "residual", "frequency", "precision", "shape", "imported_project_module_sha256"},
        "unexpected source declaration field")
    check_modules(producer, source["imported_project_module_sha256"])
    for key in ("N", "M", "R", "Rc", "K"):
        require(type(source.get(key)) is int and source[key] > 0, "invalid scalar integer " + key)
    N, M, R, Rc, K = (source[key] for key in ("N", "M", "R", "Rc", "K"))
    beta = rational(source["beta"])
    require(R > 1 and N >= 4 and N % 2 == 0 and K >= 2 and K % 2 == 0,
            "invalid scalar search domains")
    require(M == 2 * N and Rc == 2 * R and 2 * K < N and M >= N + K,
            "physical cutoff or residual cross band mismatch")
    exact_fields(source["residual"], {"accuracy_goal": str(GOAL),
                                      "accuracy_is_not_target_gap": True}, "residual scope")

    # An exhaustive elementary factorization identifies prime powers. Six has
    # two distinct prime factors, so Lambda(6)=0; Lambda(4)=log(2), not log(4).
    recognized = []
    for integer in range(2, 8):
        remaining, factors = integer, []
        divisor = 2
        while divisor * divisor <= remaining:
            exponent = 0
            while remaining % divisor == 0:
                remaining //= divisor
                exponent += 1
            if exponent:
                factors.append((divisor, exponent))
            divisor += 1
        if remaining > 1:
            factors.append((remaining, 1))
        if len(factors) == 1:
            recognized.append((integer, *factors[0]))
    require(recognized == [(2, 2, 1), (3, 3, 1), (4, 2, 2), (5, 5, 1), (7, 7, 1)],
            "independent prime-power recognition failed")
    require(isinstance(source["active_terms"], list) and len(source["active_terms"]) == 5,
            "incomplete active arithmetic list")
    coefficients = formal_coefficients(K)
    require(source["residual"]["coefficients"] == [str(value) for value in coefficients],
            "canonical exact residual coefficients disagree with formal division")
    ladder = source["residual"]["ladder"]
    require(isinstance(ladder, list) and len(ladder) == K // 2,
            "missing preceding even residual order")
    for row, order in zip(ladder, range(2, K + 1, 2), strict=True):
        exact_fields(row, {"K": order}, "residual ladder")
        du = bounds(row["delta"], "delta")[1]
        bu = bounds(row["cross"], "cross")[1]
        require(du > 0 and bu > 0, "nonpositive residual bound")
        allowance = du + (2 * bu * du + du * du) / (FLOOR * (1 - LOSS))
        require(rational(row["Lambda_upper"]) == allowance, "incorrect residual Lambda upper")
        exact_fields(row, {"passes": allowance <= GOAL}, "residual pass flag")
        require((allowance <= GOAL) == (order == K), "not the first passing even K")

    ratio_n, numerator_n = direct_tail(N, Q(R))
    ratio_previous, numerator_previous = direct_tail(N - 2, Q(R))
    ratio_m, numerator_m = direct_tail(M, Q(Rc))
    # r_n decreases strictly. For each valid integer n,
    # lambda_(n+1)/lambda_n = r_n*(1-r_n)/(1-r_(n+1)) < r_n < 1.
    # Invalid r_n>=1 cannot qualify under this geometric-bound policy. Thus a
    # certified N-2 failure excludes every preceding valid even cutoff.
    first_valid_even = 2
    while Q(R * R, (2 * first_valid_even + 1) * (2 * first_valid_even + 3)) >= 1:
        first_valid_even += 2
    require(first_valid_even <= N - 2, "missing valid even policy predecessor")
    for n in (first_valid_even, N - 2, N):
        rn = Q(R * R, (2 * n + 1) * (2 * n + 3))
        rnext = Q(R * R, (2 * n + 3) * (2 * n + 5))
        require(0 < rnext < rn < 1 and 0 < rn * (1 - rn) / (1 - rnext) < 1,
                "complete leakage monotonicity ratio failed")

    edges = [Q(0), Q(R)]
    while edges[-1] * Q(17, 16) < 32 * R:
        edges.append(edges[-1] * Q(17, 16))
    edges.append(Q(32 * R))
    require(source["frequency"]["edges"] == [str(edge) for edge in edges],
            "frequency step partition mismatch")
    weights = source["frequency"]["inverse_weight_step_uppers"]
    require(isinstance(weights, list) and len(weights) == len(edges),
            "missing frequency weight, including terminal infinity step")
    require(rational(weights[0]) == 1 / FLOOR, "incorrect global inverse weight")

    source_amp = ceil_log2(Q(21 ** (N - 1)))
    audit_amp = ceil_log2(Q(3 ** (M - 1) * 7 ** (N - 1)))
    # Closed product instead of the producer's iterative rational update.
    upward_product = Q((M + 1) * math.prod(R + 2 * n + 1 for n in range(1, M + 1)), R ** M)
    bessel_amp = ceil_log2(upward_product)
    blockceil = lambda value: ((value + 511) // 512) * 512
    source_bits = max(3072, blockceil(256 + 512 + source_amp))
    audit_bits = max(4096, source_bits + 1024, blockceil(256 + 512 + audit_amp),
                     blockceil(256 + 512 + bessel_amp))
    precision = {"source_bits": source_bits, "audit_bits": audit_bits,
                 "matrix_publication_bits": 256, "source_amplification_bits": source_amp,
                 "audit_amplification_bits": audit_amp, "bessel_amplification_bits": bessel_amp,
                 "source_gauss_order": 3 * N // 2, "audit_square_gauss_order": N}
    exact_fields(source["precision"], precision, "precision policy")
    # The high physical mode times a translation has degree at most
    # (M-1)+(N-1)=3N-2. A squared translation has degree at most 2N-2.
    # These are exact polynomial-degree conditions, not an accuracy claim for
    # the nonpolynomial Bessel integrands at this unexecuted target.
    require(2 * precision["source_gauss_order"] - 1 >= (M - 1) + (N - 1)
            and 2 * precision["audit_square_gauss_order"] - 1 >= 2 * N - 2,
            "Gauss polynomial-degree policy insufficient")
    parity = N // 2
    shape = {"parity_dimension": parity,
             "six_triangular_entries": 6 * (parity * (parity + 1) // 2),
             "translation_cells": 11}
    exact_fields(source["shape"], shape, "matrix shape")
    require(set(source["precision"]) == set(precision), "unexpected precision achievement declaration")
    require(set(source["shape"]) == set(shape), "unexpected matrix shape declaration")
    checks = {"native_interval_containments": 0, "rational_upper_checks": 0,
              "active_terms_per_precision": 5, "residual_even_orders_per_precision": K // 2,
              "frequency_steps_per_precision": len(edges), "translation_breakpoints_per_precision": 12,
              "native_precisions": [512, 1024], "comparison_complete_native_proof_replays": 1,
              "direct_precision_bits": 768, "direct_native_cell_upper_checks": 0,
              "direct_native_witness_checks": 0, "direct_native_infinity_checks": 0,
              "policy_even_cutoffs_covered": N // 2,
              "geometric_invalid_even_cutoffs_excluded": first_valid_even // 2 - 1,
              "valid_even_cutoffs_covered_by_monotonicity": (N - first_valid_even) // 2 + 1}

    def contain(record, fresh, label):
        lower, upper = bounds(record, label)
        lo, hi = endpoints(fresh)
        require(lower <= lo <= hi <= upper, "native containment failed: " + label)
        checks["native_interval_containments"] += 1

    def cover(text, fresh, label):
        upper = rational(text)
        lo, hi = endpoints(fresh)
        require(0 < lo <= hi <= upper, "false rational upper: " + label)
        checks["rational_upper_checks"] += 1
        return upper

    for bits in (512, 1024):
        ctx.prec = bits
        pi = arb.pi()
        require(arb(7).log() < 2 < arb(8).log() and 2 < pi,
                "strict log7<2<log8 or 2<pi failed")
        terms = [arb(prime).log() / arb(integer).sqrt()
                 for integer, prime, _ in recognized]
        for row, (integer, prime, exponent), coefficient in zip(
                source["active_terms"], recognized, terms, strict=True):
            exact_fields(row, {"m": integer, "prime": prime, "exponent": exponent}, "active term")
            contain(row["coefficient"], coefficient, "Lambda/sqrt(m) at " + str(integer))
        a0 = -arb.const_euler() - pi / 2 - 3 * arb(2).log() - pi.log()

        def g(t):
            psi = acb(aq(Q(1, 4)), aq(Q(t) / 2)).digamma().real
            return aq(1 - ALPHA) * (psi - pi.log()) + aq(ALPHA) * a0 - aq(ALPHA + beta)

        g0, gR, gprevious = g(0), g(R), g(R - 1)
        for key, fresh in (("g0", g0), ("gR", gR), ("g_predecessor", gprevious)):
            contain(source["reference"][key], fresh, key)
        threshold = aq(FLOOR + Q(1, 64))
        require(gR > threshold and gprevious < threshold, "R anchor or predecessor failure")
        require(gR > g0 and g0 < aq(FLOOR), "invalid leakage monotonicity signs")
        # Re psi(a+it/2)-psi(a) is a sum of positive multiples of
        # (t/2)^2/((j+a)^2+(t/2)^2), hence is strictly increasing for t>0.
        # This proves anchor minimality and all frequency tails, not samples.
        for row, n, ratio, numerator, selected in (
                (source["reference"]["selected"], N, ratio_n, numerator_n, True),
                (source["reference"]["previous"], N - 2, ratio_previous, numerator_previous, False)):
            exact_fields(row, {"N": n, "ratio": str(ratio)}, "leakage policy row")
            leakage = aq(numerator) / pi
            outside = gR - (gR - g0) * leakage
            relative_loss = (aq(FLOOR) - g0) * leakage / aq(FLOOR)
            for key, fresh in (("leakage", leakage), ("outside", outside), ("eta_loss", relative_loss)):
                contain(row[key], fresh, "N=" + str(n) + " " + key)
            if selected:
                require(outside > aq(FLOOR) and relative_loss < aq(LOSS),
                        "selected N fails complete leakage policy")
            else:
                require(outside < aq(FLOOR) or relative_loss > aq(LOSS),
                        "N-2 does not have a certified policy failure")

        inverse = source["reference"]["inverse"]
        a, leak_m = 1 / g(Rc), aq(numerator_m) / pi
        contain(inverse["a"], a, "physical inverse a")
        contain(inverse["complete_leakage"], leak_m, "physical inverse complete leakage")
        aa, ll = bounds(inverse["a"], "a")[1], bounds(inverse["complete_leakage"], "leakage")[1]
        require(0 < aa < 1 / FLOOR and 0 <= ll < 1 and ratio_m < 1,
                "physical inverse endpoint signs failed")
        kappa = aa + (1 / FLOOR - aa) * ll
        require(rational(inverse["kappa_upper"]) == kappa and 0 < kappa < 1 / FLOOR,
                "physical complete inverse upper mismatch")
        cover(inverse["kappa_upper"], a + (aq(1 / FLOOR) - a) * leak_m,
              "physical complete inverse kappa")
        for index, edge in enumerate(edges[1:], start=1):
            fresh = 1 / g(edge)
            upper = cover(weights[index], fresh, "frequency step " + str(index))
            lo, hi = endpoints(fresh)
            scale = 1 << 256
            directed_low = Q(math.ceil(lo * scale) + 1, scale)
            directed_high = Q(math.ceil(hi * scale) + 1, scale)
            require(directed_low == directed_high == upper,
                    "frequency weight is not the prescribed upward publication")
        # The last weight covers [32R,infinity), by the same monotonicity.
        breakpoints = [arb(-1), arb(1)]
        for integer, _, _ in recognized:
            shift = arb(integer).log()
            breakpoints.extend((1 - shift, -1 + shift))
        breakpoints.sort(key=lambda value: endpoints(value)[0])
        require(len(breakpoints) == 12 and all(left < right for left, right
                in zip(breakpoints[:-1], breakpoints[1:], strict=True)),
                "translation breakpoints collide or cannot be strictly ordered")
        require(len(breakpoints) - 1 == source["shape"]["translation_cells"],
                "translation cell count mismatch")

        arithmetic = sum(terms, arb(0))
        for row, order in zip(ladder, range(2, K + 1, 2), strict=True):
            require(2 * aq(T) < pi and aq(T) < order + 2, "invalid complete remainder ratios")
            geometric = (2 / pi) * (2 * aq(T) / pi) ** (order + 1) / (1 - 2 * aq(T) / pi)
            factorial_tail = (2 * aq(T) ** (order + 1)
                              / (math.factorial(order + 1) * (1 - aq(T) / (order + 2))))
            delta = 2 * aq(T) * (geometric + factorial_tail)
            polynomial = sum((abs(value) * 2 ** degree for degree, value
                              in enumerate(coefficients[:order + 1])), Q(0))
            cross = pi / 2 + 2 * arithmetic + aq(2 * polynomial)
            contain(row["delta"], delta, "complete residual delta K=" + str(order))
            contain(row["cross"], cross, "complete residual cross K=" + str(order))
            allowance = delta + (2 * cross * delta + delta * delta) / aq(FLOOR * (1 - LOSS))
            cover(row["Lambda_upper"], allowance, "complete residual Lambda K=" + str(order))
            if order < K:
                require(allowance > aq(GOAL), "preceding even residual order is not a native failure")
            else:
                require(allowance <= aq(GOAL), "selected K lacks native accuracy qualification")

    direct_proof = verify_direct(source, recognized, checks)
    require(digest(inputs_path) == input_hash and digest(source_path) == source_hash
            and digest(producer) == producer_hash, "input/source/program changed during audit")
    check_modules(producer, source["imported_project_module_sha256"])
    comparison_checker = (ROOT / PINNED["comparison_manifest"][0]).with_name("verify-reference-v2.py")
    require(digest(comparison_checker) == comparison_checker_hash, "comparison checker changed during audit")
    for name, (path, sha256) in PINNED.items():
        require(digest(ROOT / path) == sha256, "retained premise changed during audit: " + name)
    return {
        "format": "t1-direct-reference-audit-v1", "status": "PASS",
        "inputs_sha256": input_hash, "source_sha256": source_hash,
        "producer_sha256": producer_hash, "audit_code_sha256": digest(Path(__file__)),
        "imported_project_module_sha256": source["imported_project_module_sha256"],
        "retained_pins": pins["pins"], "comparison_audit_code_sha256": comparison_checker_hash,
        "comparison_beta": str(COMPARISON_BETA), "comparison_N": comparison["N"],
        "direct_improves_inherited": beta < COMPARISON_BETA,
        "audit_precision_bits": 1024, "direct_precision_bits": 768, "publication_bits": 192,
        "support": "1", "alpha": "1/4", "m": "1/3", "eta": str(1 - LOSS),
        "reference_kind": "direct_whole_line_multiplier", "direct_proof": direct_proof,
        "beta": str(beta), "R": R, "N": N, "M": M, "Rc": Rc, "K": K,
        "precision": precision, "shape": shape, "checks": checks,
        "accuracy_goal": str(GOAL), "accuracy_is_not_target_gap": True,
        "scalar_N_policy": "first positive even N with r_N<1, outside>m and eta_loss<2^-128; endpoint failure plus strict complete-leakage monotonicity",
        "complete_inverse_qualified": True, "terminal_infinity_step_checked": True,
        "gauss_polynomial_degree_policy_checked": True, "gauss_accuracy_achieved": False,
        "high_mode_widths_achieved": False, "target_memory_measured": False, "target_runtime_measured": False,
        "shared_trust": "FLINT/Arb arithmetic and transcendental enclosures",
        "target_matrix_computed": False, "target_positivity_proved": False,
        "production_admission": False, "RH_status": "UNRESOLVED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be a fresh path")
    try:
        result = audit(args.inputs, args.source)
    except (ValueError, KeyError, TypeError, ZeroDivisionError, OSError, OverflowError) as exc:
        print(json.dumps({"status": "REJECTED", "error": str(exc)}))
        raise SystemExit(2)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "beta", "R", "N", "M", "K", "precision", "shape")}))


if __name__ == "__main__":
    main()
