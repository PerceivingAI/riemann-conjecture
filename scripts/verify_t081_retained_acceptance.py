"""Run the original T81/100 adversarial and retained-consequence gates.

Reuse the already successful complete captured replay. Do not regenerate the
source, change the frozen scientific programs, or admit a production theorem.
The legacy case driver records one native thread, so that setting is preserved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "computations/2026-10-27T182100Z-t081-retained-acceptance"
QUALIFIED = ROOT / "computations/2026-10-28T034134Z-t081-resource-execution"
sys.path.insert(0, str(QUALIFIED))
from execution_resources_v2 import resolve_resources
from execution_supervisor_v1 import Execution


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_bytes())


def write(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--negative-output", type=Path, required=True)
    parser.add_argument("--cpus", type=int)
    parser.add_argument("--memory-mib", type=int)
    parser.add_argument("--reserve-mib", type=int)
    args = parser.parse_args()
    negative = args.negative_output.resolve()
    require(negative.is_relative_to((LEGACY / "data").resolve()) and
            negative.suffix == ".json" and not negative.exists(),
            "fresh negative output under the original acceptance data/ required")
    output = args.output_dir.resolve()
    require(not output.exists(), "fresh supervision output directory required")
    budget = resolve_resources(cpus=args.cpus, workers=1, threads=1,
                               memory_mib=args.memory_mib, reserve_mib=args.reserve_mib,
                               required_bytes=9 * 1024**3)
    original = load(LEGACY / "manifest.json")
    original_members = {member["path"]: member for member in original["members"]}
    for member in original_members.values():
        path = LEGACY / member["path"]
        require(sha(path) == member["sha256"] and path.stat().st_size == member["size"],
                "original checkpoint bytes changed: " + member["path"])
    qualified = load(QUALIFIED / "manifest-v2.json")
    qualified_members = {member["path"]: member for member in qualified["members"]}
    helpers = ("execution_resources_v2.py", "execution_supervisor_v1.py",
               "resource_limits_v1.py", "stage_worker_v1.py", "execution_events_v1.py")
    for name in helpers:
        require(sha(QUALIFIED / name) == qualified_members[name]["sha256"],
                "qualified execution helper changed: " + name)
    replay = LEGACY / "data/isolated-replay-v1.json"
    final_output = output / "retained-acceptance-v1.json"
    with Execution(output, budget, root=ROOT) as execution:
        write(output / "bound-inputs-v1.json", {
            "entrypoint_sha256": sha(Path(__file__)),
            "original_checkpoint_manifest_sha256": sha(LEGACY / "manifest.json"),
            "qualified_execution_manifest_sha256": sha(QUALIFIED / "manifest-v2.json"),
            "reused_replay_sha256": sha(replay),
            "source_sha256": "f69fee0feb9c08833ad6a3091718c9a6a301e5b5ddbea96ee5f0f6c0553c8b6e",
            "legacy_programs": {name: sha(LEGACY / name) for name in
                                ("negative-controls-v1.py", "accept-retained-v1.py")},
            "execution_helpers": {name: sha(QUALIFIED / name) for name in helpers},
            "native_threads": 1,
            "complete_source_replay_executed_again": False,
            "production_admission": False,
        })
        execution.run("original-adversarial", LEGACY / "negative-controls-v1.py",
                      ["--output", str(negative)], kind="fixture")
        controls = load(negative)
        require(controls["status"] == "PASS_NEGATIVE_CONTROLS" and
                len(controls["cases"]) == 9 and all(c["passed"] for c in controls["cases"]),
                "original nine-case gate did not pass")
        require(controls["native_batch_proof"]["numerical_threads"] == 1,
                "legacy numerical-thread declaration changed")
        execution.run("original-retained-consequence", LEGACY / "accept-retained-v1.py",
                      ["--replay", str(replay), "--negative-controls", str(negative),
                       "--output", str(final_output)], kind="exact")
        consequence = load(final_output)
        require(consequence["status"] == "PASS_RETAINED_SOURCE_CONDITIONAL_SMOOTH_TEST_POSITIVITY"
                and consequence["production_admission"] is False,
                "original final retained gate did not pass")
    require(all(stage["worker_cleanup_verified"] for stage in execution.receipts),
            "owned process cleanup was not verified")
    receipt = {
        "format": "t081-original-retained-gates-execution-v1",
        "status": "PASS_ORIGINAL_ADVERSARIAL_AND_RETAINED_CONSEQUENCE_GATES",
        "entrypoint_sha256": sha(Path(__file__)),
        "reused_replay_sha256": sha(replay),
        "negative_controls": negative.relative_to(ROOT).as_posix(),
        "negative_controls_sha256": sha(negative),
        "retained_acceptance": final_output.name,
        "retained_acceptance_sha256": sha(final_output),
        "source_sha256": consequence["source_sha256"],
        "budget": budget,
        "stages": execution.receipts,
        "complete_source_replay_executed_again": False,
        "production_admission": False,
        "rh_status": "UNRESOLVED",
    }
    write(output / "milestone3-completion-v1.json", receipt)
    print(json.dumps({"status": receipt["status"],
                      "published_source_norm_gap": consequence["published_rational_source_norm_gap_lower"]}),
          flush=True)


if __name__ == "__main__":
    main()
