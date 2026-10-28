"""Summarize the T81/100 execution-profile measurements into one report.

Reads the retained instrumentation reports and probes and emits a compact JSON
summary plus a Markdown fragment. Pure post-processing of measured files.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def round_share(value: float, total: float) -> float | None:
    return round(100.0 * value / total, 2) if total else None


def profile_summary(report: dict) -> dict:
    total_wall = report["wall_seconds"]
    total_cpu = report["cpu_seconds"]
    stages = report["stages"]
    for stage in stages:
        stage["exclusive_wall_share_percent"] = round_share(
            stage["exclusive_wall_seconds"], total_wall)
    unattributed = total_wall - sum(stage["exclusive_wall_seconds"] for stage in stages)
    top = []
    for entry in report["stack_samples"][:25]:
        top.append({"location": entry["location"],
                    "samples": entry["samples"],
                    "share_percent": round_share(entry["samples"], report["samples"])})
    by_stage = []
    for entry in report["stage_stack_samples"][:40]:
        by_stage.append({"stage": entry["stage"], "location": entry["location"],
                         "samples": entry["samples"]})
    return {
        "program": report["program"],
        "program_sha256": report["program_sha256"],
        "status": report["status"],
        "wall_seconds": total_wall,
        "cpu_seconds": total_cpu,
        "cpu_over_wall": report["cpu_over_wall"],
        "peak_working_set_bytes": report["peak_working_set_bytes"],
        "peak_private_bytes": report["peak_private_bytes"],
        "peak_threads": report["peak_threads"],
        "samples": report["samples"],
        "sample_interval_seconds": 0.05,
        "affinity": report["affinity"],
        "physical_memory": report["physical_memory"],
        "ctx_precision": report["ctx_precision"],
        "ctx_threads": report["ctx_threads"],
        "child_processes": report["child_processes"],
        "stages": stages,
        "unattributed_wall_seconds": round(unattributed, 6),
        "unattributed_wall_share_percent": round_share(unattributed, total_wall),
        "top_locations": top,
        "stage_locations": by_stage,
        "stage_peak_working_set_bytes": report["stage_peak_working_set_bytes"],
    }


def markdown(summary: dict) -> str:
    lines = []
    for name in ("source", "audit"):
        data = summary[name]
        lines.append(f"### {name}\n")
        lines.append(f"- wall {data['wall_seconds']:.1f}s, CPU {data['cpu_seconds']:.1f}s, "
                     f"CPU/wall {data['cpu_over_wall']}, peak WS "
                     f"{data['peak_working_set_bytes'] / 2**30:.2f} GiB, peak threads "
                     f"{data['peak_threads']}, samples {data['samples']}")
        lines.append(f"- unattributed wall {data['unattributed_wall_seconds']:.1f}s "
                     f"({data['unattributed_wall_share_percent']}%)")
        lines.append("")
        lines.append("| stage | calls | inclusive s | exclusive s | share % | CPU/wall | peak WS GiB |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for stage in data["stages"]:
            lines.append(
                f"| `{stage['stage']}` | {stage['calls']} | "
                f"{stage['inclusive_wall_seconds']:.1f} | "
                f"{stage['exclusive_wall_seconds']:.1f} | "
                f"{stage['exclusive_wall_share_percent']} | "
                f"{stage['cpu_over_wall']} | "
                f"{stage['peak_working_set_bytes'] / 2**30:.2f} |")
        lines.append("")
        lines.append("| location | samples | share % |")
        lines.append("| --- | ---: | ---: |")
        for entry in data["top_locations"][:12]:
            location = entry["location"]
            lines.append(f"| `{location[0]}:{location[1]}` ({location[2]}) | "
                         f"{entry['samples']} | {entry['share_percent']} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()
    data = args.data
    summary = {
        "format": "t081-execution-profile-summary-v1",
        "source": profile_summary(load(data / "source-profile-v1.json")),
        "audit": profile_summary(load(data / "audit-profile-v1.json")),
        "work_unit_costs": load(data / "work-unit-costs-v1.json"),
        "native_threading": load(data / "native-threading-v1.json"),
    }
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    args.markdown.write_text(markdown(summary), encoding="utf-8")
    print(args.markdown.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
