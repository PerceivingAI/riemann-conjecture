"""Summarize retained full-source measurements using inclusive phase timings."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASELINE = ROOT / "computations/2026-10-27T230830Z-t081-execution-profile/data/source-profile-v1.json"


def load(path):
    return json.loads(path.read_bytes())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def summarize(run_dir: Path, identity_path: Path) -> dict:
    receipt = load(run_dir / "execution-receipt-v1.json")
    require(receipt["status"] == "PASS_MEASURED_SOURCE_AND_EXACT_RETAINED_PAYLOAD_IDENTITY",
            "full benchmark did not pass")
    require(all(step["exit_code"] == 0 for step in receipt["steps"]), "benchmark child failed")
    for descriptor in [*receipt["programs"].values(), receipt["inputs"],
                       receipt["profile"], receipt["source"], receipt["comparison"]]:
        path = ROOT / descriptor["path"]
        require(digest(path) == descriptor["sha256"] and path.stat().st_size == descriptor["bytes"],
                "receipt fingerprint mismatch: " + descriptor["path"])
    for step in receipt["steps"]:
        for name in ("stdout", "stderr"):
            descriptor = step[name]
            path = ROOT / descriptor["path"]
            require(digest(path) == descriptor["sha256"] and path.stat().st_size == descriptor["bytes"],
                    "execution log changed")
    identity = load(identity_path)
    require(identity["format"] == "t081-strict-source-comparison-v3"
            and identity["status"] == "PASS_EXACT_RETAINED_PAYLOAD_IDENTITY", "strict v3 identity required")
    require(identity["source_sha256"] == receipt["source"]["sha256"], "identity is for another source")
    require(identity["producer_sha256"] == receipt["programs"]["producer"]["sha256"], "producer identity mismatch")
    require(identity["comparer_sha256"] == digest(HERE / "compare-v3-v1.py"), "identity checker changed")
    fresh, baseline = load(run_dir / "instrumentation-v2.json"), load(BASELINE)
    require(fresh["status"] == baseline["status"] == "COMPLETED", "profile did not complete")
    require(fresh["ctx_precision"] == baseline["ctx_precision"] == 4608, "precision changed")
    require(fresh["program_sha256"] == receipt["programs"]["producer"]["sha256"], "profile code mismatch")
    require(fresh["harness_sha256"] == receipt["programs"]["instrument"]["sha256"], "profile instrument mismatch")
    resources = None
    for line in (run_dir / "source-stdout.txt").read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get("event") == "execution_resources":
            resources = event["resources"]
    require(resources is not None and fresh["ctx_threads"] == resources["threads"], "thread configuration missing or inconsistent")
    require(resources["threads"] <= resources["effective_cpu_budget"], "thread budget exceeded")
    old_stages = {row["stage"]: row for row in baseline["stages"]}
    new_stages = {row["stage"]: row for row in fresh["stages"]}
    rows = []
    for name in ("combined_square", "source"):
        old, new = old_stages[name], new_stages[name]
        require(old["calls"] == new["calls"], "phase workload differs")
        before, after = old["inclusive_wall_seconds"], new["inclusive_wall_seconds"]
        rows.append({"phase": name, "calls": new["calls"], "timing": "inclusive",
                     "baseline_seconds": before, "new_seconds": after, "wall_speedup": before / after})
    rows.append({"phase": "program_main", "timing": "main wall including instrumentation finalization",
                 "baseline_seconds": baseline["wall_seconds"], "new_seconds": fresh["wall_seconds"],
                 "wall_speedup": baseline["wall_seconds"] / fresh["wall_seconds"]})
    return {"format": "t081-source-benchmark-summary-v1", "status": "PASS_MEASURED_IDENTICAL_PAYLOAD",
            "baseline_profile_sha256": digest(BASELINE), "new_profile_sha256": digest(run_dir / "instrumentation-v2.json"),
            "identity_check_sha256": digest(identity_path), "rows": rows, "resources": resources,
            "new_cpu_seconds": fresh["cpu_seconds"], "new_cpu_over_wall": fresh["cpu_over_wall"],
            "new_peak_working_set_bytes": fresh["peak_working_set_bytes"],
            "new_sampled_peak_private_bytes": fresh["peak_private_bytes"],
            "old_memory_peak_not_comparable": "v1 sampled only current working set; new profile retains OS high-water",
            "limitations": ["one full run per configuration", "v1 full wrappers versus new coarse wrappers",
                            "uncontrolled thermal, frequency and host background activity",
                            "no live Linux runtime or larger-host scaling qualification",
                            "no full independent analytical audit rerun; exact audited-payload identity only"],
            "production_admission": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--identity-check", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = summarize(args.run_dir, args.identity_check)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "rows": result["rows"]}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
