"""Replay the scalar-only successor and reject all original mathematical controls."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

BUNDLE = Path(__file__).resolve().parent
ROOT = BUNDLE.parents[1]
REL = BUNDLE.relative_to(ROOT)
CAPTURE = "captured-scalar-inputs-v2.json"
PROGRAMS = (
    ("qualify-reference-v2.py", "cost-inputs-v2.json", None, "cost-source-v2.json"),
    ("verify-reference-v3.py", "cost-inputs-v2.json", "cost-source-v2.json", "cost-audit-v2.json"),
    ("qualify-direct-v2.py", "direct-inputs-v2.json", None, "direct-source-v2.json"),
    ("verify-direct-v2.py", "direct-inputs-v2.json", "direct-source-v2.json", "direct-audit-v2.json"),
)
PROJECT_INPUTS = {
    "computations/2026-10-27T050743Z-t080-target-qualification/data/reference-audit-v1.json",
    "computations/2026-10-27T050743Z-t080-target-qualification/data/reference-v1.json",
    "computations/2026-10-27T050743Z-t080-target-qualification/qualification-inputs-v1.json",
    "computations/2026-10-28T183329Z-t081-retained-completion/data/run-v1/retained-acceptance-v1.json",
    "pyproject.toml", "uv.lock", "scripts/cert/__init__.py", "scripts/cert/constants.py",
    "scripts/cert/prime_power_terms.py", "scripts/cert/quadrature.py", "scripts/cert/residual_kernel.py",
    "scripts/verify_t080_reference_qualification.py", "scripts/weil_reference_route_controls.py",
    "scripts/weil_t080_reference_qualification.py",
}
INPUTS = PROJECT_INPUTS | {
    (REL / name).as_posix() for name in {
        "comparison-manifest-v2.json", *(name for row in PROGRAMS for name in row[:2])
    }
}
COST_CONTROLS = (
    ("added-prime-norm", ("transfer", "added_prime_norm"), {"lower": "0", "upper": "1"},
     "native containment failed: transfer added_prime_norm"),
    ("complete-leakage", ("reference", "selected", "leakage"), {"lower": "0", "upper": "0"},
     "native containment failed: N=9072 leakage"),
    ("canonical-polar", ("residual", "coefficients", 0), "0",
     "canonical exact residual coefficients disagree"),
    ("terminal-infinity", ("frequency", "inverse_weight_step_uppers", -1), "0",
     "false rational upper: frequency step 59"),
    ("small-geometric-cutoff", (), {"N": 826, "M": 1652}, "geometric-invalid leakage cutoff"),
    ("model-discrepancy", ("residual", "ladder", -1, "Lambda_upper"), "0",
     "incorrect residual Lambda upper"),
    ("floating-math", ("beta",), 3.28, "nonexact JSON number"),
)
DIRECT_CONTROLS = (
    ("prime7-coefficient", ("active_terms", -1, "coefficient"), {"lower": "0", "upper": "0"},
     "native containment failed: Lambda/sqrt(m) at 7"),
    ("false-cell-upper", ("direct_bound", "cells", 0, "upper"), lambda upper: str(Fraction(upper) - 1),
     "false direct cell upper at leaf 0"),
    ("frequency-gap", ("direct_bound", "cells", 0), None, "frequency cover has a gap"),
    ("unpaid-frequency-infinity", ("direct_bound", "infinite_tail_upper"), "0",
     "unpaid infinite frequency tail"),
    ("false-finite-witness", ("direct_bound", "finite_max_lower"), "3", "false finite witness lower bound"),
    ("canonical-polar", ("residual", "coefficients", 0), "0",
     "canonical exact residual coefficients disagree"),
    ("terminal-inverse", ("frequency", "inverse_weight_step_uppers", -1), "0",
     "false rational upper: frequency step 59"),
    ("model-discrepancy", ("residual", "ladder", -1, "Lambda_upper"), "0",
     "incorrect residual Lambda upper"),
    ("floating-math", ("beta",), 2.91, "nonexact JSON number"),
    ("false-achieved-width", ("high_mode_widths_achieved",), True,
     "incorrect unachieved numerical declaration.high_mode_widths_achieved"),
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, record):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, indent=2, sort_keys=True) + "\n")


def copy_inputs(root, capture):
    if (set(capture) != {"format", "destinations"}
            or capture["format"] != "selected-t1-scalar-input-capture-v2"):
        raise ValueError("wrong scalar capture format")
    rows = capture["destinations"]
    paths = [row["destination"] for row in rows]
    if len(paths) != len(INPUTS) or set(paths) != INPUTS:
        raise ValueError("incorrect scalar input destination set")
    for row in rows:
        if set(row) != {"destination", "sha256", "bytes"}:
            raise ValueError("invalid scalar input capture row")
        relative = PurePosixPath(row["destination"])
        source = (ROOT / relative).resolve()
        if not source.is_relative_to(ROOT) or source != ROOT / relative:
            raise ValueError(f"redirected scalar input: {relative}")
        raw = source.read_bytes()
        if sha(raw) != row["sha256"] or len(raw) != row["bytes"]:
            raise ValueError(f"changed scalar input: {relative}")
        dest = root / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("xb") as stream:
            stream.write(raw)


def run(root, script, inputs, source, output):
    if output.exists():
        raise ValueError("replay output already exists: " + output.name)
    child = root / REL
    argv = [sys.executable, "-I", "-B", str(child / script), "--inputs", str(child / inputs),
            "--output", str(output)]
    if source is not None:
        argv += ["--source", str(source)]
    return subprocess.run(argv, cwd=root, capture_output=True, text=True)


def controls(root, cases, program, route):
    script, inputs, source_name, _ = program
    source = (root / REL / "data" / source_name).read_bytes()
    results = []
    for name, keys, replacement, expected in cases:
        packet = json.loads(source)
        if not keys:
            packet.update(replacement)
        else:
            parent = packet
            for key in keys[:-1]:
                parent = parent[key]
            key = keys[-1]
            if replacement is None:
                del parent[key]
            else:
                parent[key] = replacement(parent[key]) if callable(replacement) else replacement
        case = root / "controls" / route / name
        case.mkdir(parents=True)
        packet_path, audit_path = case / "source.json", case / "audit.json"
        save(packet_path, packet)
        process = run(root, script, inputs, packet_path, audit_path)
        result = json.loads(process.stdout)
        if (process.returncode != 2 or result.get("status") != "REJECTED"
                or expected not in result.get("error", "") or audit_path.exists()):
            raise ValueError(f"{route} control {name} did not reject at {expected!r}")
        results.append({"name": name, "rejection": result["error"], "exit_code": 2,
                        "no_pass_file": True, "source_sha256": sha(packet_path.read_bytes())})
    return results


def qualify():
    capture_raw = (BUNDLE / CAPTURE).read_bytes()
    comparisons = []
    with tempfile.TemporaryDirectory(prefix="selected_t1_scalar_") as directory:
        root = Path(directory).resolve()
        copy_inputs(root, json.loads(capture_raw))
        data = root / REL / "data"
        data.mkdir()
        for script, inputs, source, output in PROGRAMS:
            result = run(root, script, inputs, data / source if source else None, data / output)
            if result.returncode != 0:
                raise ValueError(f"{script} failed: {result.stdout}{result.stderr}")
            raw = (data / output).read_bytes()
            if raw != (BUNDLE / "data" / output).read_bytes():
                raise ValueError(f"scientific replay bytes differ: {output}")
            comparisons.append({"artifact": "data/" + output, "sha256": sha(raw), "byte_identical": True})
        cost = controls(root, COST_CONTROLS, PROGRAMS[1], "cost")
        direct = controls(root, DIRECT_CONTROLS, PROGRAMS[3], "direct")
    if root.exists():
        raise ValueError("owned scalar replay tree remained")
    return {"format": "selected-t1-scalar-qualification-v2", "status": "PASS",
            "program_sha256": sha(Path(__file__).read_bytes()), "capture_sha256": sha(capture_raw),
            "input_count": len(INPUTS), "comparisons": comparisons, "cost_controls": cost,
            "direct_controls": direct, "expected_outputs_withheld": True,
            "owned_tree_removed": True, "target_matrix_computed": False,
            "target_positivity_proved": False, "production_admission": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be a fresh path")
    result = qualify()
    save(args.output, result)
    print(json.dumps({"status": result["status"], "replayed": len(result["comparisons"]),
                      "cost_controls": len(result["cost_controls"]),
                      "direct_controls": len(result["direct_controls"])}))


if __name__ == "__main__":
    main()
