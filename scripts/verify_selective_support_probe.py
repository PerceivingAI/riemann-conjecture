"""SYS-6.4 independent exact-rational *arithmetic* check of a scoped probe.

This checker does NOT reconstruct the upstream Arb analytical input
enclosures. It checks file hashes and exact scalar/sign consistency only.
Never labels the result an independently accepted mathematical theorem.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


def verify(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    packet = json.loads(raw)
    expected = {
        "format": "sys6-selective-signed-combined-scout-v1",
        "role": "RESEARCH_ONLY_NOT_A_CERTIFICATE",
        "support": "3/5",
        "dimension": 192,
        "K": 32,
        "arb_precision_bits": 1024,
        "active_terms": [2, 3],
        "eta": "1/16777216",
        "rational_trial_bits": 20,
    }
    if any(packet.get(key) != value for key, value in expected.items()):
        raise ValueError("scoped research identity mismatch")
    hashes = packet["source_sha256"]
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError("source identity missing")
    for name, digest in hashes.items():
        if (not isinstance(name, str) or not name.startswith("scripts/")
                or not isinstance(digest, str) or len(digest) != 64):
            raise ValueError("malformed source fingerprint")
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"source fingerprint changed: {name}")
    v = [Fraction(s) for s in packet["trial_rational_vector"]]
    if len(v) != 192 or not any(v):
        raise ValueError("invalid nonzero trial vector")
    if any(z.denominator > (1 << 20) for z in v):
        raise ValueError("noncanonical trial denominator")
    # The canonical matrices preserve reflection parity; the proposed
    # floating eigenvector may occupy either parity block.
    even_active=any(v[i] for i in range(0,192,2))
    odd_active=any(v[i] for i in range(1,192,2))
    if even_active == odd_active:
        raise ValueError("trial vector must lie in precisely one parity sector")
    nl,nu = map(Fraction,packet["trial_norm_exact_enclosure"])
    if not 0 < nl <= nu:
        raise ValueError("nonpositive trial norm enclosure")
    mu = Fraction(packet["mu_lower_exact"])
    delta = Fraction(packet["delta_upper_exact"])
    gram_lower = Fraction(packet["gram_full_rayleigh_lower_exact"])
    a_upper = Fraction(packet["a_full_rayleigh_upper_exact"])
    claimed = Fraction(packet["rigorous_chosen_schur_rayleigh_upper_exact"])
    if mu <= 0 or delta < 0 or gram_lower <= 0:
        raise ValueError("invalid strict proof hypotheses")
    independently_recomputed = a_upper - gram_lower / mu
    if independently_recomputed != claimed or independently_recomputed >= 0:
        raise ValueError("no strict negative rational upper or inconsistent arithmetic")
    if packet["sign_classification"] != "CERTIFIED_NEGATIVE_CHOSEN_SUFFICIENT_MATRIX_NOT_WEIL":
        raise ValueError("mislabeled negative result")
    return {
        "status": "PASS_EXACT_RATIONAL_ARITHMETIC_ONLY",
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "support": packet["support"],
        "dimension": packet["dimension"],
        "mu_positive": True,
        "gram_lower_positive": True,
        "negative_rayleigh_upper": True,
        "trial_parity": "even" if even_active else "odd",
        "negative_upper_decimal_display": float(independently_recomputed),
        "original_arb_source_reconstruction": "NOT_INDEPENDENTLY_CHECKED",
        "mathematical_scope": "Failure of one conservative combined Schur sufficient criterion at T=3/5,N=192, not a negative Weil quadratic form or RH result",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = verify(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n",encoding="utf8")
    print(result["status"],"upper",result["negative_upper_decimal_display"])


if __name__=="__main__":
    main()
