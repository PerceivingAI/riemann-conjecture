"""Fixed research-only jump-model/control replay; not a Weil sign verifier.

Uses the original trial and already accepted constants. No full-source images,
new full-source moments, or joint-correlation bound are evaluated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

from flint import arb, ctx

from scripts.verify_combined_schur_analytic_entries import endpoints, qarb


INPUTS = (
    ("computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json",
     "44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b"),
    ("computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json",
     "9b9a1a0a0b420df0147f07c6fa1f5d9ee9005fb68dc8213cd8880d98556dd843"),
    ("computations/2026-10-23T105408Z-directional-loss-review/data/loss-audit.json",
     "0a2458b5ead5245a439647b2a127ef267e7c8c98f11b9d4cfdb63b2bd49bcc18"),
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _interval(pair: list[str]) -> arb:
    lo, hi = map(Q, pair)
    _require(lo <= hi, "reversed source interval")
    ball = qarb((lo + hi) / 2) + arb(0, qarb((hi - lo) / 2).upper())
    bl, bh = endpoints(ball)
    _require(bl <= lo <= hi <= bh, "source interval not enclosed")
    return ball


def run() -> dict[str, object]:
    start = time.perf_counter()
    packets = []
    for name, digest in INPUTS:
        raw = Path(name).read_bytes()
        _require(hashlib.sha256(raw).hexdigest() == digest, f"input identity: {name}")
        packets.append(json.loads(raw))
    original, source, audit = packets
    _require((original["support"], original["dimension"], original["K"],
              original["active_terms"]) == ("3/5", 192, 32, [2, 3]),
             "unexpected original configuration")
    _require(source["residual_image_degree"] == 223, "unexpected residual degree")
    z = list(map(Q, original["trial_rational_vector"]))
    _require(len(z) == 192 and all(not z[k] for k in range(0, 192, 2)),
             "trial is not the original odd vector")
    v = sum(z, Q())
    coefficient_sum = sum(map(abs, z), Q())
    norm = sum((value * value * Q(2, 2 * k + 1)
                for k, value in enumerate(z)), Q())
    _require(norm == Q(source["exact_trial_mass_norm"]), "trial mass norm mismatch")
    for packet in (original, source):
        for name, digest in packet["source_sha256"].items():
            _require(hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest,
                     f"source identity: {name}")

    with ctx.workprec(512):
        constants = source["arithmetic_constants_reference"]
        c = [_interval(constants[str(m)]["coefficient"]) for m in (2, 3)]
        tau = [_interval(constants[str(m)]["tau"]) for m in (2, 3)]
        _require(1 < tau[0] < tau[1] < 2 and c[0] > 0 and c[1] > 0
                 and c[0] + c[1] > 1, "uncertified source topology/constants")
        a = [value - 1 for value in tau]
        tail_index = 224
        whole = 2 * qarb(v) ** 2 * sum(
            (c[i] * c[j] * (1 - a[max(i, j)])
             for i in range(2) for j in range(2)), arb(0))
        b = [-a[1], -a[0], a[0], a[1]]
        jumps = [qarb(v) * c[1], qarb(v) * c[0],
                 qarb(v) * c[0], qarb(v) * c[1]]
        gram = sum(
            (jumps[i] * jumps[j] * (1 + b[min(i, j)])
             * (1 - b[max(i, j)]) / 2
             for i in range(4) for j in range(4)), arb(0))
        gl, gh = endpoints(whole - gram)
        _require(gl <= 0 <= gh, "paired/combined step Gram disagreement")
        legendre = []
        for x in a:
            row = [arb(1), x]
            for k in range(1, tail_index):
                row.append(((2 * k + 1) * x * row[-1] - k * row[-2]) / (k + 1))
            legendre.append(row)
        head = arb(0)
        for k in range(1, tail_index, 2):
            value = 2 * qarb(v) * sum(
                (c[j] * (legendre[j][k - 1] - legendre[j][k + 1])
                 for j in range(2)), arb(0)) / arb(2 * (2 * k + 1)).sqrt()
            head += value * value
        tail = whole - head
        lower, upper = endpoints(tail)
        _require(upper >= 0, "negative upper on nonnegative step-tail mass")
        arithmetic_norm = (c[0] + c[1]) * qarb(norm).sqrt()
        _, norm_upper = endpoints(arithmetic_norm)
        exact = {
            "step_tail_norm2": [str(lower), str(upper)],
            "arithmetic_norm2_upper": str(norm_upper * norm_upper),
        }
        resolved = lower > norm_upper * norm_upper
        cross_upper = separate_lower = None
        if resolved:
            cross = qarb(norm_upper) * qarb(lower).sqrt() - qarb(lower)
            _, cross_upper = endpoints(cross)
            separate = (2 * qarb(lower).sqrt() - qarb(norm_upper)) ** 2
            separate_lower, _ = endpoints(separate)
            _require(cross_upper < 0 and separate_lower > norm_upper * norm_upper,
                     "inconsistent cancellation/separated-norm predicates")
            exact.update({
                "arithmetic_mixed_tail_upper": str(cross_upper),
                "separate_norm_bound_lower": str(separate_lower),
            })

        # Separate sanity control; not the signed joint-correlation upper.
        eta = 1 - Q(191 * 192, tail_index * (tail_index + 1))
        delta = Q(source["delta_upper_exact"])
        potential_cap = arb(2).sqrt() * qarb(coefficient_sum) / (qarb(eta) * tail_index)
        control = (potential_cap + qarb(norm_upper) + qarb(delta) * qarb(norm).sqrt()) ** 2
        _, control_upper = endpoints(control)
        old_floor = 6 * v * v / Q(tail_index - 2)
        _require(control_upper < old_floor, "control improvement not certified")
        mass_lower = Q(audit["exact"]["omitted_mass_lower"])
        headroom = Q(audit["exact"]["prefix_only_reference_upper"])
        mu = Q(original["mu_lower_exact"])
        _require(mu > 0 and headroom > 0 and mass_lower > 0,
                 "nonpositive reference premise")
        harmonic_increment = sum((Q(1, j) for j in range(193, tail_index)), Q())
        weight = 1 / (mu + harmonic_increment)
        needed = mass_lower - headroom / weight
        _require(needed > 0 and control_upper > mass_lower,
                 "unexpected fixed-control threshold relation")
        exact.update({
            "full_source_control_upper": str(control_upper),
            "old_variation_envelope_lower": str(old_floor),
            "tail_cap_needed_for_negative_upper": str(needed),
        })
        return {
            "format": "original-jump-model-control-v2",
            "role": "jump-model and retained-norm control; NOT joint-correlation-bound evaluation",
            "support": "3/5", "N": 192, "K": 32,
            "tail_index": tail_index, "precision_bits": 512,
            "odd_jump_model_coefficients_evaluated": tail_index // 2,
            "exact": exact,
            "display": {
                "step_tail_norm2": float(tail.mid()),
                "arithmetic_norm2_upper": float(norm_upper * norm_upper),
                "arithmetic_mixed_tail_upper": float(cross_upper) if cross_upper is not None else None,
                "separate_norm_bound_lower": float(separate_lower) if separate_lower is not None else None,
                "full_source_control_upper": float(control_upper),
                "old_variation_envelope_lower": float(old_floor),
                "tail_cap_needed_for_negative_upper": float(needed),
            },
            "status": "SIGNED_CANCELLATION_CERTIFIED" if resolved else "INCONCLUSIVE",
            "control_strictly_improves_old_variation_envelope": True,
            "control_resolves_reference_sign": False,
            "full_joint_correlation_bound_evaluated": False,
            "new_full_source_moments": False,
            "source_images_assembled": False,
            "actual_reference_sign": "UNDETERMINED",
            "internal_seconds": time.perf_counter() - start,
        }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        result = run()
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"jump refinement control rejected: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
