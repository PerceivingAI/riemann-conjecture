"""Compare the threaded T81/100 producer publication with the retained v1 one.

Checks the six compressed matrix packets by SHA-256 and reports the size,
status and per-phase timings. Byte identity of the mathematical payload is the
correctness gate for a timing-only change; a difference would require a new
independent containment audit rather than acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETAINED = ROOT / "computations/2026-10-27T140745Z-t081-complete-gram-attempt"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    fresh_raw = args.source.read_bytes()
    fresh = load(args.source)
    retained = load(RETAINED / "data/source-v1.json")
    rows = []
    for name, descriptor in retained["matrices"].items():
        fresh_descriptor = fresh["matrices"].get(name)
        path = args.source.parent / fresh_descriptor["path"]
        raw = path.read_bytes()
        rows.append({
            "matrix": name,
            "retained_sha256": descriptor["sha256"],
            "fresh_sha256": hashlib.sha256(raw).hexdigest(),
            "fresh_descriptor_sha256": fresh_descriptor["sha256"],
            "bytes": len(raw),
            "retained_bytes": descriptor["size"],
            "identical": hashlib.sha256(raw).hexdigest() == descriptor["sha256"],
        })
    result = {
        "format": "t081-parallel-source-comparison-v1",
        "source_file": str(args.source.resolve().relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": hashlib.sha256(fresh_raw).hexdigest(),
        "retained_source_sha256": hashlib.sha256(
            (RETAINED / "data/source-v1.json").read_bytes()).hexdigest(),
        "source_json_identical": fresh == retained,
        "status": fresh["status"],
        "matrices": rows,
        "all_matrices_identical": all(row["identical"] for row in rows),
        "production_admission": False,
    }
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"all_matrices_identical": result["all_matrices_identical"],
                      "source_json_identical": result["source_json_identical"],
                      "matrices": [(row["matrix"], row["identical"]) for row in rows]},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
