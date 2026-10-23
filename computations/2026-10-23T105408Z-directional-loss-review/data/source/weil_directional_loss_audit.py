"""Exact audit of retained directional data, not a new source or cutoff trial."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from fractions import Fraction as Q
from pathlib import Path

from scripts.weil_directional_exact_screen import (
    DEGREES, ORIGINAL, ORIGINAL_SHA256, SOURCE, SOURCE_SHA256, _load, _validate,
)


def run() -> dict:
    started = time.perf_counter()
    original = _load(ORIGINAL, ORIGINAL_SHA256)
    source = _load(SOURCE, SOURCE_SHA256)
    intervals = _validate(original, source)
    mu, a_upper, g_lower = (Q(original[key]) for key in (
        "mu_lower_exact", "a_full_rayleigh_upper_exact", "gram_full_rayleigh_lower_exact"))
    mass_lower = mass_upper = inverse_lower = inverse_upper = Q()
    terms = {}
    for k in DEGREES:
        lo, hi = intervals[k]
        lower = Q() if lo <= 0 <= hi else min(lo*lo, hi*hi)
        upper = max(lo*lo, hi*hi)
        weight = 1/(mu+sum((Q(1, j) for j in range(193, k+1)), Q()))
        mass_lower += lower
        mass_upper += upper
        inverse_lower += weight*lower
        inverse_upper += weight*upper
        terms[str(k)] = {"square_lower_exact": str(lower), "square_upper_exact": str(upper),
                         "weight_exact": str(weight)}
    weight_211 = 1/(mu+sum((Q(1, j) for j in range(193, 212)), Q()))
    tail_mass_lower = max(Q(), g_lower-mass_upper)
    prefix_only_upper = a_upper-inverse_lower
    finite_tail_charge_lower = weight_211*tail_mass_lower
    # This is a true omitted-mass lower bound. g_lower-mass_lower is not one.
    exact = {"known_mass_lower": mass_lower, "known_mass_upper": mass_upper,
             "known_inverse_lower": inverse_lower, "known_inverse_upper": inverse_upper,
             "a_upper": a_upper, "g_lower": g_lower, "w_211": weight_211,
             "omitted_mass_lower": tail_mass_lower,
             "prefix_only_reference_upper": prefix_only_upper,
             "known_inverse_interval_width": inverse_upper-inverse_lower,
             "finite_tail_charge_lower": finite_tail_charge_lower,
             "separated_finite_directional_upper": prefix_only_upper-finite_tail_charge_lower}
    # These rational checks establish the scalar information-limit case actually reviewed.
    reviewed_conditions = {
        "known_prefix_does_not_force_negative_reference": inverse_lower < a_upper,
        "all_prefix_choices_have_positive_optimistic_headroom": inverse_upper < a_upper,
        "omitted_mass_lower_positive": tail_mass_lower > 0,
        "even_optimistic_same_mass_at_211_is_negative": inverse_lower+finite_tail_charge_lower > a_upper,
        "prefix_interval_width_below_one_trillionth": inverse_upper-inverse_lower < Q(1, 10**12),
    }
    return {
        "format": "directional-loss-audit-v1", "role": "RESEARCH_ONLY_NOT_A_CERTIFICATE",
        "support": "3/5", "N": 192, "reviewed_prefix_cutoff": 211,
        "original_sha256": ORIGINAL_SHA256, "accepted_source_sha256": SOURCE_SHA256,
        "exact": {name: str(value) for name, value in exact.items()},
        "decimal_displays": {name: float(value) for name, value in exact.items()},
        "reviewed_conditions": reviewed_conditions, "terms": terms,
        "opposite_scalar_bounds_serialized": {
            "a_lower": "a_full_rayleigh_lower_exact" in original,
            "g_upper": "gram_full_rayleigh_upper_exact" in original},
        "new_source_moments": 0, "alternative_cutoffs_evaluated": 0,
        "source_reassembly_performed": False, "exact_reference_sign": "UNDETERMINED",
        "scope": "Spectral loss identities and retained scalar bounds only. A positive prefix-only "
                 "upper is not positivity; omitted-mass lower is not an inverse-tail upper. "
                 "Abstract spectral completions are not alternate Weil sources.",
        "source_sha256": {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in (
            "scripts/weil_directional_loss_audit.py", "scripts/weil_directional_exact_screen.py")},
        "elapsed_seconds": time.perf_counter()-started,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("preserve existing research output; choose a new path")
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix+".partial")
    with temporary.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True)+"\n")
    os.link(temporary, args.output)
    temporary.unlink()
    print("LOSS_AUDIT exact reference UNDETERMINED; prefix upper",
          result["decimal_displays"]["prefix_only_reference_upper"], flush=True)


if __name__ == "__main__":
    main()
