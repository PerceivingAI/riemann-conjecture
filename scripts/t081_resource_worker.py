"""Execute a numerical stage only after the owned supervisor installs its budget."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time

if __package__:
    from .t081_resource_records import safe_error
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from t081_resource_records import safe_error


BUNDLE = "computations/2026-10-28T034134Z-t081-resource-execution"
STAGES = {
    "source": ("residual_matrices", "combined_square", "kernel_step", "source"),
    "audit": ("frozen_inputs", "replay_declaration", "residual_kernel", "validate_model_allowance",
              "validate_weights", "residual_outputs", "residual_blocks", "arithmetic_blocks",
              "complete_arithmetic_squared", "frequency_kernels", "reconstruct", "check_matrix"),
    "exact": (),
    "fixture": (),
}


def report_failure(exception):
    error = safe_error(exception)
    print("T081_DIAGNOSTIC " + json.dumps(error, sort_keys=True), file=sys.stderr, flush=True)
    code = 130 if isinstance(exception, KeyboardInterrupt) else 75 if isinstance(exception, MemoryError) else 1
    return code, error


def phase_totals(events, phases):
    report = events.report()["phases"]
    totals = {}
    for phase in phases:
        record = report.get(phase)
        if not isinstance(record, dict):
            continue
        calls = record.get("calls")
        if type(calls) is not int or not 0 <= calls < 2**63:
            continue
        timing = {key: record.get(key) for key in (
            "inclusive_wall_seconds", "exclusive_wall_seconds", "cpu_seconds",
        )}
        if all(type(value) in (int, float) and 0 <= value < 2**63 and math.isfinite(value)
               for value in timing.values()):
            totals[phase] = {"calls": calls, **timing}
    return totals


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise SystemExit(2)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--program-sha256", required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--config-sha256", required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--kind", choices=tuple(STAGES), required=True)
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    # The parent attaches the owned job before releasing this GO gate.
    print("T081_READY " + json.dumps({"pid": os.getpid(), "config_sha256": args.config_sha256}), flush=True)
    if sys.stdin.readline().strip() != "GO":
        raise RuntimeError("supervisor did not authorize the budgeted stage")
    raw = args.config.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.config_sha256:
        raise ValueError("execution configuration changed")
    config = json.loads(raw)
    if hashlib.sha256(args.program.read_bytes()).hexdigest() != args.program_sha256:
        raise ValueError("numerical program changed")

    # Both the checked-out worker and its captured copy sit under scripts/.
    bundle = Path(__file__).resolve().parents[1] / BUNDLE
    sys.path.insert(0, str(bundle))
    from resource_limits_v1 import apply_posix_memory_limit

    containment = {"mechanism": "owned Windows job installed before GO"}
    if os.name == "posix":
        containment = apply_posix_memory_limit(config["memory_budget_bytes"])
        if hasattr(os, "sched_setaffinity"):
            available = sorted(os.sched_getaffinity(0))
            os.sched_setaffinity(0, set(available[:config["cpu_budget"]]))

    from flint import ctx
    import execution_events_v1 as events

    sys.path.insert(0, str(args.program.parent))

    spec = importlib.util.spec_from_file_location("t081_owned_stage", args.program)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    ctx.threads = config["native_threads"]
    phases = STAGES[args.kind]
    events.wrap(module, phases)
    rest = args.arguments[1:] if args.arguments[:1] == ["--"] else args.arguments
    sys.argv = [str(args.program), *rest]
    wall, cpu = time.monotonic(), time.process_time()
    code, error = 0, None
    events.emit("program_started", kind=args.kind, threads=ctx.threads)
    try:
        code = int(module.main() or 0)
    except BaseException as exception:
        code, error = report_failure(exception)
    payload = {
        "format": "t081-budgeted-stage-profile-v2", "kind": args.kind, "exit_code": code,
        "error": error, "program_sha256": args.program_sha256,
        "wall_seconds": time.monotonic() - wall, "cpu_seconds": time.process_time() - cpu,
        "native_threads": ctx.threads, "precision": ctx.prec, "containment": containment,
        "phases": phase_totals(events, phases),
        "timing_note": "inclusive includes nested calls; exclusive subtracts wrapped children; CPU is current process only",
    }
    if os.name == "nt":
        from resource_limits_v1 import windows_resource_snapshot

        payload["process_memory"] = windows_resource_snapshot()["process"]
    args.profile.parent.mkdir(parents=True, exist_ok=True)
    with args.profile.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    events.emit("program_finished", kind=args.kind, exit_code=code, wall_seconds=payload["wall_seconds"])
    return code


if __name__ == "__main__":
    try:
        exit_code = main()
    except SystemExit as error:
        exit_code = error.code if type(error.code) is int else int(error.code is not None)
        if exit_code:
            report_failure(error)
    except BaseException as error:
        exit_code, _ = report_failure(error)
    raise SystemExit(exit_code)
