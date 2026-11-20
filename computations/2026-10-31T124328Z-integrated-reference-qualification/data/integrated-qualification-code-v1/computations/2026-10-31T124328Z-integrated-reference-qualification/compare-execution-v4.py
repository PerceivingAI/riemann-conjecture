"""Prospective comparison of selected numerical stages and all lifecycle invocations."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
ORIGINAL = Path(__file__).with_name("compare-execution-v3.py")
_inherited = runpy.run_path(str(ORIGINAL))
_numerical = _inherited["_inherited"]
resources = _inherited["resources"]
binding = _inherited["binding"]
require = _inherited["require"]


def main(argv=None):
    from scripts.whole_source.lifecycle_observations import lifecycle_resources
    from scripts.whole_source.retention import _check_sealed_output

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compare-source", action="store_true")
    parser.add_argument("--old-lifecycle-root", type=Path)
    parser.add_argument("--new-lifecycle-root", type=Path, required=True)
    args = parser.parse_args(argv)
    run = args.run_dir.resolve(strict=True)
    old = args.baseline_dir.resolve(strict=True)
    output = args.output.resolve()
    # The lifecycle reader checks the original spelling before resolving roots.
    new_lifecycle = lifecycle_resources(args.new_lifecycle_root)
    old_lifecycle = lifecycle_resources(args.old_lifecycle_root)
    inputs = [run, old, Path(new_lifecycle["root"])]
    if old_lifecycle["availability"] == "AVAILABLE":
        inputs.append(Path(old_lifecycle["root"]))
    require(not output.exists(), "report output must be fresh")
    require(not any(output.is_relative_to(path) for path in inputs),
            "report output must be outside input trees")
    _check_sealed_output(output.parent)
    report = {
        "format": "whole-source-retained-execution-comparison-v4",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "status": "PROSPECTIVE_OPERATIONAL_AND_DIAGNOSTIC_COMPARISON_ONLY",
        "program": binding(Path(__file__)),
        "inherited_program": binding(ORIGINAL),
        "inherited_scientific_program": binding(_inherited["ORIGINAL"]),
        "new": resources(run),
        "baseline": _numerical["baseline"](old),
        "lifecycle": {"new": new_lifecycle, "baseline": old_lifecycle},
        "disk": {"new": _numerical["footprint"](run), "baseline": _numerical["footprint"](old)},
        "limits": [
            "Verified selected stages do not establish whole-source/pipeline completion or scientific acceptance.",
            "Lifecycle receipts describe every invocation, including interruptions and refusals, independently of selected successful numerical stages.",
            "Missing historical lifecycle evidence remains unknown, never zero or a substituted stage total.",
            "Live status is optional advisory timing only; missing owner totals and ratios remain null.",
            "No matched full-pipeline speedup: baseline reuses a proposal and stage/control/replay boundaries differ.",
            "Native stage sums exclude inter-stage owner work; owner wall excludes final caller read-through.",
            "Lifecycle wall and cumulative active time exclude unmeasured reviewer waiting between invocations.",
            "Raw OS job CPU and commitment high-water are not sampled maxima; job and process CPU must not be added.",
            "Unowned supervisor CPU is not captured by job CPU counters.",
            "Disk census is retained logical file bytes, not transient writes or physical device I/O.",
            "One execution per implementation is not a statistical scaling study.",
        ],
        "production_admission": False,
    }
    if (run / "elapsed.json").is_file():
        report["new"]["coordinator_elapsed"] = _inherited["load"](run / "elapsed.json")
    if args.compare_source:
        report["source_comparison"] = _numerical["compare_sources"](run, old)
    _check_sealed_output(output.parent)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"report": str(output),
                      "verified_owned_stages": report["new"]["owned_receipts_verified"],
                      "verified_lifecycle_invocations": new_lifecycle["invocation_count"],
                      "all_owned_cleanup_verified": report["new"]["all_owned_cleanup_verified"],
                      "scope": report["status"]}, sort_keys=True))


if __name__ == "__main__":
    main()
