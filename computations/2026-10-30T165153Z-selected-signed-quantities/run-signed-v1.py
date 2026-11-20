"""Execute complete selected signed quantities with fresh bound inputs and raw logs."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source.contract import bind_problem
from scripts.whole_source.gram import prepare_gram_inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if not args.resume:
        output.mkdir(parents=True, exist_ok=False)
        revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                                  text=True, capture_output=True).stdout.strip()
        prepare_gram_inputs(bind_problem("retained-t081"), output/"inputs",
                            origin_git_commit=revision, origin_git_dirty=True)
        capture = output/"captured-code"
        names = ("scripts/whole_source/__init__.py", "scripts/whole_source/contract.py",
                 "scripts/whole_source/artifacts.py", "scripts/whole_source/execution.py",
                 "scripts/whole_source/producer.py", "scripts/whole_source/analytic.py",
                 "scripts/whole_source/slice.py", "scripts/whole_source/gram.py",
                 "scripts/weil_whole_source_split.py", "tests/test_whole_source_gram.py")
        for name in names:
            destination = capture/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT/name).read_bytes())
    suffix = "resume" if args.resume else "fresh"
    command = [sys.executable, "-B", "-m", "scripts.weil_whole_source_split", "slice",
        "--problem", str(output/"inputs/problem.json"), "--cases", str(output/"inputs/cases.json"),
        "--execution", str(output/"inputs/execution.json"), "--output-dir", str(output/"collection")]
    if args.resume:
        command.append("--resume")
    started = perf_counter()
    with (output/(suffix+"-stdout.txt")).open("xb") as stdout, (output/(suffix+"-stderr.txt")).open("xb") as stderr:
        run = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr)
    invocation = {"argv": command, "exit_code": run.returncode,
                  "elapsed_seconds_hex": (perf_counter()-started).hex(),
                  "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                  "program_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  "scope": "SELECTED_COMPLETE_QUANTITIES_NOT_FULL_SOURCE"}
    for channel in ("stdout", "stderr"):
        raw = (output/(suffix+"-"+channel+".txt")).read_bytes()
        invocation[channel] = {"sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)}
    with (output/(suffix+"-invocation.json")).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(invocation, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(invocation, sort_keys=True))
    return run.returncode


if __name__ == "__main__":
    raise SystemExit(main())
