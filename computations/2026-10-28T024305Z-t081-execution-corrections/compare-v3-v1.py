"""Reject any source difference except the explicitly supplied producer hash.

This is a byte-identity check against an independently audited publication,
not an analytical reconstruction or a new mathematical admission.
JSON value types are preserved, including bool/int and int/float distinctions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETAINED = ROOT / "computations/2026-10-27T140745Z-t081-complete-gram-attempt"
RETAINED_SOURCE_SHA = "f69fee0feb9c08833ad6a3091718c9a6a301e5b5ddbea96ee5f0f6c0553c8b6e"


def _unique(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _load(raw: bytes) -> dict:
    def invalid(value):
        raise ValueError("nonfinite JSON constant: " + value)
    return json.loads(raw, object_pairs_hook=_unique, parse_constant=invalid)


def _packet(base: Path, descriptor: dict) -> bytes:
    name = descriptor["path"]
    if not isinstance(name, str) or "\\" in name or ":" in name:
        raise ValueError("nonportable packet path")
    if any(part in ("", ".", "..") for part in name.split("/")):
        raise ValueError("unsafe packet path")
    path = (base / name).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError("packet path escapes source directory")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != descriptor["sha256"]:
        raise ValueError("packet digest mismatch: " + name)
    if len(raw) != descriptor["size"]:
        raise ValueError("packet size mismatch: " + name)
    return raw


def compare(source: Path, producer: Path) -> dict:
    source_raw = source.read_bytes()
    fresh = _load(source_raw)
    retained_raw = (RETAINED / "data/source-v1.json").read_bytes()
    if hashlib.sha256(retained_raw).hexdigest() != RETAINED_SOURCE_SHA:
        raise ValueError("retained source fingerprint changed")
    retained = _load(retained_raw)
    producer_sha = hashlib.sha256(producer.read_bytes()).hexdigest()
    expected = {**retained, "producer_sha256": producer_sha}
    canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if canonical(fresh) != canonical(expected):
        different = sorted(key for key in set(fresh) | set(expected)
                           if canonical(fresh.get(key)) != canonical(expected.get(key)))
        raise ValueError("source differs beyond the authorized producer hash: "
                         + ", ".join(different))
    rows = []
    for name, descriptor in retained["matrices"].items():
        old = _packet(RETAINED / "data", descriptor)
        new = _packet(source.parent, fresh["matrices"][name])
        if old != new:
            raise ValueError("matrix bytes differ: " + name)
        rows.append({"matrix": name, "sha256": descriptor["sha256"],
                     "bytes": len(new), "identical": True})
    return {
        "format": "t081-strict-source-comparison-v3",
        "status": "PASS_EXACT_RETAINED_PAYLOAD_IDENTITY",
        "source_sha256": hashlib.sha256(source_raw).hexdigest(),
        "producer_sha256": producer_sha,
        "comparer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "retained_source_sha256": RETAINED_SOURCE_SHA,
        "source_equal_after_only_producer_hash_substitution": True,
        "matrices": rows,
        "all_matrices_identical": True,
        "production_admission": False,
        "analytic_containment": "inherited by exact byte identity, not reexecuted",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--producer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise FileExistsError(args.output)
        report = compare(args.source, args.producer)
        with args.output.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "FAIL_SOURCE_IDENTITY", "error": str(error)}),
              file=sys.stderr, flush=True)
        return 1
    print(json.dumps({"status": report["status"], "matrix_count": len(report["matrices"])}),
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
