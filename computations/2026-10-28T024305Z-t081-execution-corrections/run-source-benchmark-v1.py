"""Run one unchanged complete source with retained logs, counters and identity checks."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = ROOT / "computations/2026-10-27T140745Z-t081-complete-gram-attempt/whole-inputs-v1.json"
INPUTS_SHA = "19eac80d7869fcc6d6ddd0d33dcb90901b65254b2f076c6964148575019982a1"


def fingerprint(path):
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw)}


def step(name, argv, folder, env):
    stdout_path, stderr_path = folder / (name + "-stdout.txt"), folder / (name + "-stderr.txt")
    started = time.perf_counter()
    with stdout_path.open("x", encoding="utf-8", newline="\n") as stdout, \
            stderr_path.open("x", encoding="utf-8", newline="\n") as stderr:
        with subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=stderr,
                              text=True, encoding="utf-8") as process:
            for line in process.stdout:
                stdout.write(line)
                stdout.flush()
                print(line, end="", flush=True)
            returncode = process.wait()
    return {"name": name, "argv": argv, "exit_code": returncode,
            "elapsed_seconds": time.perf_counter() - started,
            "stdout": fingerprint(stdout_path), "stderr": fingerprint(stderr_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--threads", type=int)
    args = parser.parse_args()
    folder = args.output_dir.resolve()
    if not folder.is_relative_to(HERE / "data"):
        parser.error("benchmark output must be a fresh directory under this bundle's data/")
    folder.mkdir(parents=True, exist_ok=False)
    programs = {name: HERE / filename for name, filename in (
        ("producer", "build-whole-source-v3.py"), ("policy", "execution_resources_v1.py"),
        ("instrument", "instrument-t081-v2.py"), ("comparer", "compare-v2-v1.py"),
        ("runner", "run-source-benchmark-v1.py"))}
    code = {name: fingerprint(path) for name, path in programs.items()}
    if hashlib.sha256(INPUTS.read_bytes()).hexdigest() != INPUTS_SHA:
        raise ValueError("fixed whole-input bytes changed")
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("PYTHONPATH", None)
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env.setdefault(key, "1")
    source = folder / "source-v3.json"
    profile = folder / "instrumentation-v2.json"
    argv = [sys.executable, "-B", str(programs["instrument"]),
            "--program", str(programs["producer"]), "--kind", "build", "--level", "coarse",
            "--report", str(profile), "--", "--inputs", str(INPUTS), "--output", str(source)]
    if args.threads is not None:
        argv.extend(["--threads", str(args.threads)])
    receipt = {"format": "t081-source-benchmark-receipt-v1", "status": "RUNNING",
               "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "inputs": fingerprint(INPUTS), "programs": code,
               "production_admission": False, "steps": [], "full_analytical_audit_reexecuted": False,
               "acceptance_boundary": "exact identity to audited packets; no new theorem admission"}
    error = None
    try:
        receipt["steps"].append(step("source", argv, folder, env))
        if receipt["steps"][-1]["exit_code"]:
            raise ValueError("source process failed")
        compare_argv = [sys.executable, "-B", str(programs["comparer"]), "--source", str(source),
                        "--producer", str(programs["producer"]),
                        "--output", str(folder / "comparison-v3-v1.json")]
        receipt["steps"].append(step("comparison", compare_argv, folder, env))
        if receipt["steps"][-1]["exit_code"]:
            raise ValueError("strict retained-payload comparison failed")
        for name, path in programs.items():
            if fingerprint(path) != code[name]:
                raise ValueError("program changed during run: " + name)
        receipt["profile"] = fingerprint(profile)
        receipt["source"] = fingerprint(source)
        receipt["comparison"] = fingerprint(folder / "comparison-v3-v1.json")
        receipt["status"] = "PASS_MEASURED_SOURCE_AND_EXACT_RETAINED_PAYLOAD_IDENTITY"
    except BaseException as exception:
        receipt["status"] = "FAILED"
        receipt["error"] = f"{type(exception).__name__}: {exception}"
        error = exception
    finally:
        receipt["finished"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with (folder / "execution-receipt-v1.json").open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if error is not None:
        raise error
    print(json.dumps({"status": receipt["status"], "receipt": str(folder / "execution-receipt-v1.json")}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
