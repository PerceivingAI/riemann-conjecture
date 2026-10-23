"""Fixed research-only rational screen for A-U_211, not the exact inverse.

Consumes two approved immutable research packets. No analytical imports,
reassembly, float arithmetic in predicates, parameter search or admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import time
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path

ORIGINAL = Path("computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json")
ORIGINAL_SHA256 = "44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b"
SOURCE = Path("computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json")
SOURCE_SHA256 = "9b9a1a0a0b420df0147f07c6fa1f5d9ee9005fb68dc8213cd8880d98556dd843"
DEGREES = tuple(range(193, 211, 2))
COMPONENTS = ("V", "P2", "P3", "R32", "sum_truncated")
SELF = Path("scripts/weil_directional_exact_screen.py")


def _load(path: Path, expected: str) -> dict:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError(f"immutable input byte identity mismatch: {path.name}")
    return json.loads(raw)


def _validate(original: dict, source: dict) -> dict[int, tuple[Q, Q]]:
    expected = {"format": "directional-source-validation-v1", "status": "SOURCE_INPUTS_ACCEPTED",
                "role": "RESEARCH_ONLY_NOT_A_CERTIFICATE", "support": "3/5", "low_dimension": 192,
                "residual_order": 32, "high_degrees": list(DEGREES), "active_terms": [2, 3],
                "coordinate_metric": "d_k=2/(2k+1)", "publication_bits": 352,
                "precision_bits": 1024, "reference_precision_bits": 2048,
                "input_sha256": ORIGINAL_SHA256, "trial_parity": "odd", "schur_sign_evaluated": False}
    if any(source.get(name) != value for name, value in expected.items()):
        raise ValueError("accepted analytical source configuration mismatch")
    if (original["support"], original["dimension"], original["K"], original["active_terms"]) != (
            "3/5", 192, 32, [2, 3]):
        raise ValueError("original trial configuration mismatch")
    if any(source["source_sha256"].get(name) != digest
           for name, digest in original["source_sha256"].items()):
        raise ValueError("original analytical source identity not retained")
    z = list(map(Q, original["trial_rational_vector"]))
    if (len(z) != 192 or sum(bool(x) for x in z) != 96
            or any(z[i] for i in range(0, 192, 2))
            or any((1 << 20) % x.denominator for x in z)):
        raise ValueError("trial is not the exact odd dyadic vector")
    norm = sum((x*x*Q(2, 2*i+1) for i, x in enumerate(z)), Q())
    nl, nu = map(Q, original["trial_norm_exact_enclosure"])
    if not 0 < nl <= norm <= nu < 1 or Q(source["exact_trial_mass_norm"]) != norm:
        raise ValueError("physical mass norm is not certified below one")
    mu = Q(original["mu_lower_exact"])
    delta = Q(original["delta_upper_exact"])
    independent_mu = list(map(Q, source["independent_mu_exact"]))
    independent_delta = list(map(Q, source["independent_delta_exact"]))
    if not (0 < mu <= independent_mu[0] <= independent_mu[1]
            and 0 <= independent_delta[0] <= independent_delta[1] <= delta
            and Q(source["delta_upper_exact"]) == delta):
        raise ValueError("full residual/complement scalar prerequisite failed")
    if set(source["moments"]) != {str(k) for k in DEGREES}:
        raise ValueError("selected moment set mismatch")
    intervals = {}
    scale = 1 << 352
    for k in DEGREES:
        row = source["moments"][str(k)]
        for name in COMPONENTS:
            cell = row[name]
            gl, gh = map(Q, cell["generator_exact"])
            rl, rh = map(Q, cell["reference_exact"])
            p, q = cell["published_dyadic"]
            pl, ph = Q(p, scale), Q(q, scale)
            if not (cell["status"] == "PASS" and pl <= gl <= gh <= ph
                    and pl <= rl <= rh <= ph and max(gl, rl) <= min(gh, rh)
                    and p == (gl*scale).__floor__()-1 and q == (gh*scale).__ceil__()+1):
                raise ValueError(f"analytical acceptance failed for k={k}, {name}")
        p, q = row["sum_truncated"]["published_dyadic"]
        full = Q(p, scale)-delta, Q(q, scale)+delta
        if tuple(map(Q, row["full_source_interval"])) != full:
            raise ValueError(f"full residual enlargement mismatch for k={k}")
        intervals[k] = full
    return intervals


def _bound(mu: Q, a_upper: Q, gram_lower: Q,
           intervals: dict[int, tuple[Q, Q]]) -> dict:
    if not all(isinstance(x, Q) for x in (mu, a_upper, gram_lower)):
        raise TypeError("predicate scalars must be exact rationals")
    if mu <= 0 or gram_lower < 0 or set(intervals) != set(DEGREES):
        raise ValueError("invalid fixed screen hypotheses")
    weights = {192: 1/mu}
    denominator = mu
    for k in range(193, 212):
        denominator += Q(1, k)
        weights[k] = 1/denominator
    theta = a_upper-weights[211]*gram_lower
    lower_sum, maximum_sum = Q(), Q()
    terms = {}
    for k in DEGREES:
        lo, hi = intervals[k]
        if not isinstance(lo, Q) or not isinstance(hi, Q) or lo > hi:
            raise ValueError("invalid full-source rational interval")
        distance = max(Q(), lo, -hi)
        maximum = max(abs(lo), abs(hi))
        weight = weights[k]-weights[211]
        if weight <= 0:
            raise ValueError("nonpositive finite correction weight")
        contribution = weight*distance*distance
        lower_sum += contribution
        maximum_sum += weight*maximum*maximum
        terms[str(k)] = {"weight_exact": str(weight), "absolute_lower_exact": str(distance),
                         "full_source_interval": [str(lo), str(hi)],
                         "weighted_square_lower_exact": str(contribution)}
    upper = theta-lower_sum
    return {"status": "NEGATIVE_SUFFICIENT_CRITERION" if upper < 0 else "INCONCLUSIVE",
            "theta_exact": str(theta), "weighted_sum_lower_exact": str(lower_sum),
            "weighted_sum_maximum_exact": str(maximum_sum), "directional_upper_exact": str(upper),
            "w_211_exact": str(weights[211]), "terms": terms}


def run(original_path: Path = ORIGINAL, source_path: Path = SOURCE) -> dict:
    started = time.perf_counter()
    own_source = SELF.read_bytes()
    original = _load(original_path, ORIGINAL_SHA256)
    source = _load(source_path, SOURCE_SHA256)
    intervals = _validate(original, source)
    mu, a, g = (Q(original[name]) for name in (
        "mu_lower_exact", "a_full_rayleigh_upper_exact", "gram_full_rayleigh_lower_exact"))
    result = _bound(mu, a, g, intervals)
    result.update({"format": "directional-exact-screen-v1", "role": "RESEARCH_ONLY_NOT_A_CERTIFICATE",
                   "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "support": "3/5", "N": 192, "M": 211, "K": 32,
                   "active_terms": [2, 3], "trial_parity": "odd", "high_degrees": list(DEGREES),
                   "original_sha256": ORIGINAL_SHA256, "accepted_source_sha256": SOURCE_SHA256,
                   "consumer_sha256": hashlib.sha256(own_source).hexdigest(),
                   "original_scalar_inputs": {"mu_lower_exact": str(mu), "a_upper_exact": str(a),
                                              "gram_lower_exact": str(g), "delta_upper_exact": original["delta_upper_exact"]},
                   "directional_upper_decimal_display": float(Q(result["directional_upper_exact"])),
                   "scope": "Only finite A-U_211 at fixed T=3/5,N=192 and original odd trial. "
                            "No sign of exact diagonal-inverse reference, exact Schur complement or Weil form follows. "
                            "INCONCLUSIVE does not establish positivity.",
                   "trust": "Accepted new analytical moments and shared Suzuki/Arb premises; original A/G remain "
                            "generator-source-qualified. This command rechecks rational consequences only.",
                   "source_reassembly_performed": False, "python": platform.python_version(),
                   "elapsed_seconds": time.perf_counter()-started})
    if SELF.read_bytes() != own_source:
        raise ValueError("consumer source changed during evaluation")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, default=ORIGINAL)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("preserve existing research output; choose a new path")
    try:
        result = run(args.original, args.source)
    except (ValueError, KeyError, OSError) as exc:
        result = {"format": "directional-exact-screen-v1", "role": "RESEARCH_ONLY_NOT_A_CERTIFICATE",
                  "status": "SOURCE_PROOF_GAP", "error": str(exc)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix+".partial")
    with temporary.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True)+"\n")
    os.link(temporary, args.output)
    temporary.unlink()
    print("EXACT_SCREEN", result["status"], "UPPER", result.get("directional_upper_decimal_display"), flush=True)
    if result["status"] == "SOURCE_PROOF_GAP":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
