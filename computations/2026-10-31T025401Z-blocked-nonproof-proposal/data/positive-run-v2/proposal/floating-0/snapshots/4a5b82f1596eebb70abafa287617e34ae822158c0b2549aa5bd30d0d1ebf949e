"""Inspect bound metadata or execute independently checked source expressions."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

from scripts.whole_source.contract import (
    ContractError, GateReceipt, PROFILES, QuantityKey, bind_problem,
    canonical_bytes, collection_id, expected_domain, inspection_plan, problem_id,
)


def _write_new(path: Path, document: dict) -> dict:
    raw = canonical_bytes(document)
    if path.exists():
        raise FileExistsError(path)
    temporary = path.with_name("." + path.name + ".tmp")
    with temporary.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    return {"path": path.name, "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)}


def inspect_profile(profile: str, output_dir: Path, input_manifest: Path | None = None,
                    *, root: Path | None = None) -> dict:
    """Write one new inspection bundle; never overwrite or resume any directory.

    A rejected binding retains failure.json if the fresh output is writable.
    inspection.json is written last and is not an analytical acceptance receipt.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    created = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    try:
        kwargs = {} if root is None else {"root": root}
        spec = bind_problem(profile, input_manifest, **kwargs)
        plan = inspection_plan(spec)
        pid, cid = problem_id(spec), collection_id(spec, plan)
        domains = tuple(expected_domain(spec, QuantityKey(name, parity))
                        for parity in (0, 1)
                        for name in ("A_model", "weighted_head", "weighted_complete_tail", "F_H", "R_H", "K_H"))
        problem = spec.to_dict()
        problem["problem_id"] = pid
        problem_ref = _write_new(output_dir / "problem.json", problem)
        plan_ref = _write_new(output_dir / "inspection-plan.json", {
            "format": "whole-source-split-inspection-plan-v1", "plan": plan,
            "collection_id": cid, "domains": domains,
            "partition_meaning": "complete logical ranges, not native allocation or resource admission",
            "execution_authorized": False,
        })
        report = GateReceipt(pid, cid).to_dict()
        report.update(created_utc=created, profile=profile, support=str(spec.support),
                      N=spec.N, M=spec.M, K=spec.K,
                      reference_kind=spec.reference_kind,
                      evidence_files=len(spec.evidence),
                      bound_bytes=sum(ref.size for ref in spec.evidence),
                      artifacts=[problem_ref, plan_ref])
        _write_new(output_dir / "inspection.json", report)
        return report
    except (ContractError, OSError, ValueError, TypeError, KeyError) as exc:
        failure = {"format": "whole-source-split-inspection-failure-v1", "created_utc": created,
                   "profile": profile, "status": "PROFILE_BINDING_REJECTED",
                   "error": str(exc), "native_verification_executed": False,
                   "execution_authorized": False}
        try:
            _write_new(output_dir / "failure.json", failure)
        except OSError:
            pass  # The original error is still returned to the caller on unwritable output.
        raise


def inspect_resources(problem_path: Path, execution_path: Path, output_dir: Path,
                      *, root: Path | None = None, overrides: dict | None = None) -> dict:
    """Inspect admission only. This does not start a worker or create a collection."""
    from dataclasses import replace
    from scripts.whole_source.execution import (
        ExecutionPlan, _bytes, _json, _provenance, detect_budget,
    )
    source_root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    problem_raw, execution_raw = _bytes(problem_path), _bytes(execution_path)
    document = _json(problem_raw)
    profile = document.get("parameters", {}).get("profile")
    spec = bind_problem(profile, root=source_root)
    expected = spec.to_dict()
    expected["problem_id"] = problem_id(spec)
    if canonical_bytes(document) != canonical_bytes(expected):
        raise ContractError("problem snapshot does not match its original bound profile")
    plan = ExecutionPlan.from_dict(_json(execution_raw))
    if overrides:
        plan = replace(plan, **overrides)
    if plan.problem_sha256 != problem_id(spec):
        raise ContractError("execution plan binds another problem")
    role_bits = spec.arithmetic.audit_bits if plan.role == "analytic" else spec.arithmetic.source_bits
    if plan.role != "exact" and plan.precision_bits != role_bits:
        raise ContractError("execution precision differs from the bound role policy")
    _provenance(source_root, plan.provenance)
    budget = detect_budget(plan, repository=output_dir, temporary=output_dir, helper_root=source_root)
    # Admission happens before output creation; resource refusal is not a partial run.
    output_dir.mkdir(parents=True, exist_ok=False)
    report = {"format": "whole-source-resource-inspection-v1", "status": "RESOURCE_ENVELOPE_ADMITTED",
              "scope": "OPERATIONAL_ENVELOPE_SNAPSHOT_ONLY", "profile": profile,
              "problem_id": problem_id(spec), "collection_id": plan.collection_sha256,
              "execution_id": plan.execution_id, "budget": budget.to_dict(),
              "problem_sha256": hashlib.sha256(problem_raw).hexdigest(),
              "execution_input_sha256": hashlib.sha256(execution_raw).hexdigest(),
              "native_verification_executed": False, "matrix_computed": False,
              "positivity_proved": False, "production_admission": False,
              "execution_authorized": False}
    _write_new(output_dir / "resource-inspection.json", report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="Bind reviewed metadata or inspect an explicit resource envelope")
    subject = inspect.add_mutually_exclusive_group(required=True)
    subject.add_argument("--profile", choices=PROFILES)
    subject.add_argument("--problem", type=Path, help="Previously bound problem.json, revalidated against its original inputs")
    inspect.add_argument("--resources", action="store_true", help="Inspect resource admission without starting a worker")
    inspect.add_argument("--execution", type=Path, help="Bound owned-execution-plan JSON")
    for name in ("cpus", "workers", "threads", "memory-mib", "reserve-mib"):
        inspect.add_argument("--" + name, type=int)
    inspect.add_argument("--input-manifest", type=Path,
                         help="The profile's canonical reviewed manifest beneath the source root")
    inspect.add_argument("--output-dir", type=Path, required=True,
                         help="A new, nonexistent output directory")
    arithmetic = commands.add_parser("slice", help="Execute independently checked selected arithmetic or signed low/exterior quantities")
    for name in ("problem", "cases", "execution", "output-dir"):
        arithmetic.add_argument("--"+name, type=Path, required=True)
    arithmetic.add_argument("--resume", action="store_true", help="Revalidate and resume the same scientific collection")
    arithmetic.add_argument("--source-root", type=Path, help="Exact captured input/code root; no Git checkout required")
    arithmetic.add_argument("--qualification-stop", help="Explicit process-interruption barrier; requires external release")
    arithmetic.add_argument("--qualification-role", choices=("producer", "analytic"), default="producer")
    for name in ("source", "audit"):
        command = commands.add_parser(name, help=(
            "Publish complete bounded source expressions" if name == "source"
            else "Independently reconstruct and contain every declared source entry"))
        for option in ("problem", "execution", "output-dir"):
            command.add_argument("--"+option, type=Path, required=True)
        command.add_argument("--source-root", type=Path, help="Exact captured input/code root")
        if name == "source":
            command.add_argument("--resume", action="store_true")
        else:
            command.add_argument("--source", type=Path, required=True, help="Bound scientific source manifest")
    propose = commands.add_parser("propose", help="Build a fresh nonproof blocked congruence proposal")
    for option in ("problem", "source", "execution", "output-dir"):
        propose.add_argument("--"+option, type=Path, required=True)
    propose.add_argument("--source-root", type=Path, help="Exact captured proposal input/code root")
    args = parser.parse_args(argv)
    if args.command == "propose":
        from scripts.whole_source.proposal import run_proposal
        kwargs = {} if args.source_root is None else {"code_root": args.source_root}
        try:
            report = run_proposal(args.problem, args.source, args.execution, args.output_dir, **kwargs)
        except (ContractError, OSError, ValueError, TypeError, KeyError, RuntimeError, ArithmeticError) as exc:
            print("Nonproof proposal unresolved: "+str(exc), file=sys.stderr)
            return 2
        print(f"{report['status']}: blocks={len(report['blocks'])} scope={report['scope']}")
        return 0
    if args.command in ("source", "audit"):
        from scripts.whole_source.pipeline import run_source, run_audit
        kwargs = {} if args.source_root is None else {"code_root": args.source_root}
        try:
            if args.command == "source":
                report = run_source(args.problem, args.execution, args.output_dir, resume=args.resume, **kwargs)
            else:
                report = run_audit(args.problem, args.source, args.execution, args.output_dir, **kwargs)
        except (ContractError, OSError, ValueError, TypeError, KeyError, RuntimeError, ArithmeticError) as exc:
            print("Source operation rejected: "+str(exc), file=sys.stderr)
            return 2
        print(f"{report['status']}: entries={report.get('entries', report.get('entries_checked'))} scope={report['scope']}")
        return 0
    if args.command == "slice":
        from scripts.whole_source.slice import run_slice
        kwargs = {} if args.source_root is None else {"code_root": args.source_root}
        try:
            report = run_slice(args.problem, args.cases, args.execution, args.output_dir,
                resume=args.resume, qualification_stop=args.qualification_stop,
                qualification_role=args.qualification_role, **kwargs)
        except (ContractError, OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
            print("Arithmetic slice rejected: "+str(exc), file=sys.stderr)
            return 2
        print(f"{report['status']}: {report['profile']} entries={len(report['entries'])} scope={report['scope']}")
        return 0
    if args.resources != (args.problem is not None) or args.resources != (args.execution is not None):
        parser.error("--resources requires --problem and --execution, not --profile")
    overrides = {name: getattr(args, name) for name in ("cpus", "workers", "threads", "memory_mib", "reserve_mib")
                 if getattr(args, name) is not None}
    if not args.resources and overrides:
        parser.error("resource overrides require --resources")
    try:
        if args.resources:
            if args.input_manifest:
                parser.error("--input-manifest applies only to --profile")
            report = inspect_resources(args.problem, args.execution, args.output_dir, overrides=overrides)
        else:
            report = inspect_profile(args.profile, args.output_dir, args.input_manifest)
    except (ContractError, OSError, ValueError, TypeError, KeyError) as exc:
        print("Profile inspection rejected: " + str(exc), file=sys.stderr)
        return 2
    print(f"{report['status']}: {report['profile']} problem={report['problem_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
