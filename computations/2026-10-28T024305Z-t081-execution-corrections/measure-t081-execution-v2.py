"""Measure the frozen T81/100 complete source and independent audit execution.

Rebuilds the captured 55-destination input closure exactly as the retained
replay does, adds the instrumentation harness to that isolated tree, runs the
frozen producer and consumer once each under the same environment, verifies
that the fresh scientific outputs are byte-identical to the retained ones, and
retains the measurement reports. No mathematical parameter is changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ACCEPTANCE = ROOT / "computations/2026-10-27T182100Z-t081-retained-acceptance"
CANDIDATE = ROOT / "computations/2026-10-27T140745Z-t081-complete-gram-attempt"
HARNESS = HERE / "instrument-t081-v2.py"
SOURCE_SHA = "f69fee0feb9c08833ad6a3091718c9a6a301e5b5ddbea96ee5f0f6c0553c8b6e"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message: str) -> None:
    if not condition:
        raise ValueError(message)


def confined(base: Path, name: str) -> Path:
    require(type(name) is str and name and "\\" not in name and ":" not in name
            and not name.startswith("/"), "portable relative path required")
    require(all(part not in ("", ".", "..") for part in name.split("/")),
            "unsafe path component")
    path = (base / name).resolve()
    require(path.is_relative_to(base.resolve()), "path escapes captured root")
    return path


def capture_closure() -> tuple[dict, dict[str, bytes]]:
    capture_path = ACCEPTANCE / "captured-source-inputs-v1.json"
    capture_raw = capture_path.read_bytes()
    capture = json.loads(capture_raw)
    require(capture["format"] == "t081-retained-complete-source-input-closure-v1",
            "capture identity")
    require(capture["source_sha256"] == SOURCE_SHA, "capture source identity")
    records = capture["files"]
    require(records and len({r["destination"] for r in records}) == len(records),
            "missing or duplicate capture destination")
    raws: dict[str, bytes] = {}
    for item in records:
        raw = confined(ACCEPTANCE, item["stored"]).read_bytes()
        require(len(raw) == item["bytes"] and digest(raw) == item["sha256"],
                "captured file changed " + item["destination"])
        raws[item["destination"]] = raw
    return capture, raws


def environment() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
                "FLINT_NUM_THREADS"):
        env[key] = "1"
    return env


def run(step: str, argv: list[str], isolated: Path, env: dict[str, str]) -> dict:
    print(f"[{time.strftime('%H:%M:%S')}] start {step}", flush=True)
    started = time.monotonic()
    process = subprocess.run(argv, cwd=isolated, env=env, capture_output=True,
                             text=True, encoding="utf-8")
    elapsed = time.monotonic() - started
    print(f"[{time.strftime('%H:%M:%S')}] end {step} exit={process.returncode} "
          f"elapsed={elapsed:.3f}s", flush=True)
    report = {"step": step, "argv": argv, "exit_code": process.returncode,
              "elapsed_seconds": elapsed, "stdout_tail": process.stdout[-4000:],
              "stderr_tail": process.stderr[-4000:]}
    require(process.returncode == 0, f"{step} failed: {process.stdout}\n{process.stderr}")
    return report


def measure(phase="both", level="full", profile_dir=None) -> dict:
    require(phase in ("source", "audit", "both"), "unknown measurement phase")
    require(level in ("full", "coarse"), "unknown instrumentation level")
    profile_dir = Path(profile_dir) if profile_dir is not None else HERE / "data"
    profiles = {name: profile_dir / f"{name}-profile-v2.json"
                for name in ("source", "audit") if phase in (name, "both")}
    for path in profiles.values():
        require(not path.exists(), "fresh profile required: " + str(path))
    capture, raws = capture_closure()
    harness_raw = HARNESS.read_bytes()
    result = {
        "format": "t081-execution-profile-v2",
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "candidate_bundle": CANDIDATE.relative_to(ROOT).as_posix(),
        "acceptance_bundle": ACCEPTANCE.relative_to(ROOT).as_posix(),
        "capture_sha256": digest((ACCEPTANCE / "captured-source-inputs-v1.json").read_bytes()),
        "captured_files": len(raws), "harness_sha256": digest(harness_raw),
        "driver_sha256": digest(Path(__file__).read_bytes()),
        "source_sha256": SOURCE_SHA, "production_admission": False,
        "phase": phase, "level": level,
        "execution_metadata_note": "measurement of unchanged frozen operations; no mathematical result",
        "steps": [], "profiles": {name: str(path.resolve()) for name, path in profiles.items()},
    }
    with tempfile.TemporaryDirectory(prefix="rh_t081_profile_v2_") as temporary:
        isolated = Path(temporary).resolve()
        for item in capture["files"]:
            if "installed" in item["roles"]:
                target = confined(isolated, item["destination"])
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as handle:
                    handle.write(raws[item["destination"]])
        harness = isolated / "instrument-t081-v2.py"
        harness.write_bytes(harness_raw)
        env = environment()
        bundle = "computations/2026-10-27T140745Z-t081-complete-gram-attempt"
        run_dir = isolated / bundle / "data" / "profile-v2"
        run_dir.mkdir(parents=True)
        inputs = isolated / bundle / "whole-inputs-v1.json"
        source_out = run_dir / "source-v1.json"
        audit_out = run_dir / "source-audit-v1.json"

        def argv(kind, program, report, rest):
            return [sys.executable, "-I", "-B", str(harness),
                    "--program", str(isolated / bundle / program), "--kind", kind,
                    "--level", level, "--report", str(report.resolve()), "--", *rest]

        if phase in ("source", "both"):
            result["steps"].append(run("source_profile", argv("build", "build-whole-source-v1.py",
                profiles["source"], ["--inputs", str(inputs), "--output", str(source_out)]), isolated, env))
        else:
            # Audit-only uses the captured, hash-checked source and matrix bytes.
            source_out.write_bytes(raws[bundle + "/data/source-v1.json"])
            for descriptor in json.loads(source_out.read_bytes())["matrices"].values():
                target = confined(run_dir, descriptor["path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raws[bundle + "/data/" + descriptor["path"]])
            result["audit_source_origin"] = "hash-checked captured source and matrices"
        fresh_source = source_out.read_bytes()
        require(digest(fresh_source) == SOURCE_SHA, "fresh source byte mismatch")
        source = json.loads(fresh_source)
        for name, descriptor in source["matrices"].items():
            fresh = confined(run_dir, descriptor["path"]).read_bytes()
            require(digest(fresh) == descriptor["sha256"], "matrix byte mismatch " + name)
        result["source_byte_identical"] = True
        result["source_matrices_checked"] = len(source["matrices"])
        if phase in ("audit", "both"):
            result["steps"].append(run("audit_profile", argv("verify", "verify-whole-source-v1.py",
                profiles["audit"], ["--inputs", str(inputs), "--source", str(source_out),
                                    "--output", str(audit_out)]), isolated, env))
            fresh_audit = json.loads(audit_out.read_bytes())
            retained = load(CANDIDATE / "data" / "source-audit-v1.json")
            require(fresh_audit.pop("source") is not None and fresh_audit.pop("inputs") is not None,
                    "audit execution paths missing")
            retained.pop("source")
            retained.pop("inputs")
            require(fresh_audit == retained, "fresh audit differs beyond execution paths")
            result["audit_identical_except_execution_paths"] = True
            result["audit_checked_triangular_entries"] = retained["checked_matrix_entries"] \
                if "checked_matrix_entries" in retained else retained["checked_triangular_entries"]
    # This check must run after TemporaryDirectory.__exit__, never inside it.
    result["isolated_tree_removed"] = not isolated.exists()
    require(result["isolated_tree_removed"], "owned temporary tree remains")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=("source", "audit", "both"), default="both")
    parser.add_argument("--level", choices=("full", "coarse"), default="full")
    parser.add_argument("--profile-dir", type=Path)
    args = parser.parse_args()
    require(not args.output.exists(), "fresh report required")
    profile_dir = args.profile_dir if args.profile_dir is not None else args.output.parent
    require(args.output.resolve() not in {
        (profile_dir / f"{name}-profile-v2.json").resolve() for name in ("source", "audit")},
        "summary and profile paths must differ")
    result = measure(args.phase, args.level, profile_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: result[key] for key in (
        "phase", "source_byte_identical", "isolated_tree_removed")}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
