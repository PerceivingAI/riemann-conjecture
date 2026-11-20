"""Run bounded, actual K09..K13 controls for SELECTION_ONLY arithmetic.

The normal child receives no expected mathematical output. Comparisons happen in
this external qualification process. Captured replay is an input/code isolation
check, not a hostile-OS sandbox; children can use installed system packages.
K11 uses named, bounded I/O injections, never host-device exhaustion.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import replace
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
THIS = Path(__file__).resolve()
BUNDLE = THIS.parent
CUTS = ("K09", "K10", "K11", "K12", "K13")
CLI_TIMEOUT = 3600
BARRIER_TIMEOUT = 300


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def load(path):
    return json.loads(Path(path).read_bytes())


def save(path, value, *, overwrite=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb" if overwrite else "xb") as stream:
        raw = canonical(value)
        require(stream.write(raw) == len(raw), "short qualification report write")
        stream.flush()
        os.fsync(stream.fileno())


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_ref(path, base=None):
    path = Path(path)
    raw = path.read_bytes()
    return {"path": path.relative_to(base).as_posix() if base else path.as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)}


def recovery():
    name = "selected_arithmetic_recovery_qualification_v1"
    spec = importlib.util.spec_from_file_location(name, BUNDLE/"qualify-recovery-v1.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def environment():
    result = dict(os.environ)
    result.pop("PYTHONPATH", None)
    result.pop("PYTHONHOME", None)
    result["PYTHONDONTWRITEBYTECODE"] = "1"
    return result


def child_import_root(root):
    # The launcher is external to the capture. It imports no original project
    # modules and removes its own repository paths before importing captured code.
    root = Path(root).resolve()
    excluded = {ROOT, BUNDLE}
    sys.path[:] = [str(root)] + [entry for entry in sys.path
        if entry and Path(entry).resolve() not in excluded and Path(entry).resolve() != root]


def cli_arguments(inputs, target, root, *, resume=True, stop=None):
    args = ["slice"]
    for name in ("problem", "cases", "execution"):
        args += ["--"+name, str(Path(inputs)/(name+".json"))]
    args += ["--output-dir", str(target), "--source-root", str(root)]
    if resume:
        args.append("--resume")
    if stop:
        args += ["--qualification-stop", stop]
    return args


def cli_command(inputs, target, root=ROOT, *, resume=True, stop=None):
    return [sys.executable, "-B", "-m", "scripts.weil_whole_source_split",
            *cli_arguments(inputs, target, root, resume=resume, stop=stop)]


def stop_known_process(process, helper):
    if process.poll() is None:
        # Popen owns the actual Windows process handle. Do not reopen a PID that
        # could have been recycled after the child exited.
        process.kill()
        process.wait(timeout=120)


def run(command, logs, label, helper, *, cwd=ROOT, expected=0):
    stdout_path, stderr_path = logs/(label+".stdout"), logs/(label+".stderr")
    started = time.monotonic()
    timed_out = False
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        process = subprocess.Popen(command, cwd=cwd, env=environment(), stdout=stdout, stderr=stderr)
        try:
            process.wait(timeout=CLI_TIMEOUT)
        except subprocess.TimeoutExpired:
            timed_out = True
            stop_known_process(process, helper)
    evidence = {"command": command, "cwd": str(cwd), "pid": process.pid,
                "exit_code": process.returncode, "wall_ms": int(1000*(time.monotonic()-started)),
                "timeout": timed_out, "stdout": file_ref(stdout_path), "stderr": file_ref(stderr_path)}
    save(logs/(label+".process.json"), evidence)
    require(not timed_out, label+": setup failure, actual process deadline exceeded")
    require(process.returncode == expected,
            label+": unexpected exit "+str(process.returncode)+"; "+stderr_path.read_text(errors="replace"))
    return evidence


def math_evidence(helper, expected, target):
    actual = helper.receipt(target)
    helper.same_math(expected, actual)
    require(len(actual["entries"]) == 6 and actual["scope"] == "SELECTION_ONLY", "wrong selected scope")
    for role in ("producer", "analytic"):
        require(len(actual["roles"][role]["quantity_seals"]) == 6, "incomplete quantity seals")
    state = load(target/"slice-state.json")
    return {"same_canonical_endpoints": True, "same_quantity_seals": True,
            "same_preparation": True, "baseline_entries_sha256": digest(expected["entries"]),
            "actual_entries_sha256": digest(actual["entries"]),
            "quantity_seals": {role: actual["roles"][role]["quantity_seals"]
                               for role in ("producer", "analytic")},
            "role_collection_ids": {role: actual["roles"][role]["collection_id"]
                                    for role in ("producer", "analytic")},
            "all_owned_cleanup_verified": actual["all_owned_cleanup_verified"],
            "receipt": state["receipt"], "scope": "SELECTION_ONLY",
            "full_mathematical_source": False, "matrix_positivity": False}


def events(collection):
    head = load(collection/"collection.json")["index"]
    seen = set()
    while head:
        require(head["sha256"] not in seen, "qualification encountered index cycle")
        seen.add(head["sha256"])
        node = load(collection/head["path"])
        yield head, node
        head = node["previous"]


def attempts(target):
    return {role: {p.name for p in (target/role/"attempts").iterdir() if p.is_dir()}
            if (target/role/"attempts").is_dir() else set()
            for role in ("producer", "analytic")}


def cleanup_evidence(target, before, *, stage_required):
    retained = []
    for role, old in before.items():
        directory = target/role/"attempts"
        if not directory.is_dir():
            continue
        for attempt in sorted(p for p in directory.iterdir() if p.is_dir() and p.name not in old):
            for path in sorted(attempt.glob("*/receipt.json")):
                value = load(path)
                require(value.get("worker_cleanup_verified") is True, "actual owned stage cleanup not verified")
                retained.append({"receipt": file_ref(path, target), "stage": value.get("stage"),
                                 "worker_cleanup_verified": True, "exit_code": value.get("exit_code")})
    require(bool(retained) or not stage_required, "expected actual owned stage receipt is missing")
    return {"native_stages_observed": len(retained), "stage_receipts": retained,
            "all_observed_owned_cleanup_verified": all(row["worker_cleanup_verified"] for row in retained)}


def scientific_inventory(collection):
    result = {"collection.json": file_ref(collection/"collection.json", collection),
              ".collection.lock.metadata": lock_metadata(collection)}
    for family in ("chunks", "prefixes", "index", "seals"):
        for path in sorted((collection/family).iterdir()):
            require(path.is_file() and not path.is_symlink(), "unsafe scientific inventory member")
            result[path.relative_to(collection).as_posix()] = file_ref(path, collection)
    result["attempt_directories"] = sorted(p.name for p in (collection/"attempts").iterdir())
    return result


def lock_metadata(collection):
    with (collection/".collection.lock").open("rb", buffering=0) as stream:
        return json.loads(stream.readline(4096))


def windows_parent_pid(pid):
    import ctypes
    from ctypes import wintypes
    class Entry(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                    ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", wintypes.LONG),
                    ("dwFlags", wintypes.DWORD), ("szExeFile", wintypes.WCHAR*260)]
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.CreateToolhelp32Snapshot(2, 0)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        entry = Entry()
        entry.dwSize = ctypes.sizeof(entry)
        more = kernel.Process32FirstW(handle, ctypes.byref(entry))
        while more:
            if entry.th32ProcessID == pid:
                return entry.th32ParentProcessID
            more = kernel.Process32NextW(handle, ctypes.byref(entry))
        raise RuntimeError("barrier PID is not a live process")
    finally:
        kernel.CloseHandle(handle)


def descendant_chain(pid, ancestor):
    chain = [pid]
    for _ in range(8):
        if pid == ancestor:
            return chain
        pid = windows_parent_pid(pid)
        require(pid not in chain and pid > 0, "cyclic or missing owned process ancestry")
        chain.append(pid)
    raise AssertionError("process is not a bounded descendant of the captured launcher")


def wait_barrier(process, target, prior, stderr):
    deadline = time.monotonic()+BARRIER_TIMEOUT
    while True:
        candidates = [path for path in (target/"producer/attempts").glob("*/barrier-reached.json")
                      if path.parent.name not in prior["producer"]]
        require(len(candidates) <= 1, "ambiguous actual writer barrier")
        if candidates:
            marker = candidates[0]
            try:
                barrier = load(marker)
            except (json.JSONDecodeError, OSError):
                if time.monotonic() >= deadline:
                    raise TimeoutError("setup failure: writer marker never became readable")
                time.sleep(0.02)
                continue
            require(barrier["point"] == "payload-writing" and
                    barrier["attempt_id"] == marker.parent.name and
                    barrier["scope"] == "PROCESS_INTERRUPTION_ONLY", "unbound writer barrier")
            owner = load(marker.parent/"artifact-owner.json")
            metadata = lock_metadata(target/"producer")
            attachment = load(marker.parent/"arithmetic-attachment.json")
            require(owner["pid"] == metadata["pid"] == attachment["supervisor_pid"],
                    "collection metadata differs from actual CLI ownership")
            cli_chain = descendant_chain(owner["pid"], process.pid)
            require(owner["generation"] == metadata["generation"] == attachment["generation"] and
                    owner["attempt_id"] == attachment["attempt_id"] == barrier["attempt_id"],
                    "writer barrier generation mismatch")
            require(barrier["pid"] != owner["pid"], "barrier unexpectedly belongs to supervisor")
            worker_chain = descendant_chain(barrier["pid"], attachment["pid"])
            require(process.poll() is None, "first CLI exited before ownership check")
            return marker, {"marker": barrier, "owner": owner, "os_lock_metadata": metadata,
                            "owned_stage_attachment": attachment,
                            "actual_worker_parent_pid": attachment["pid"],
                            "cli_launcher_ancestry": cli_chain, "worker_root_ancestry": worker_chain}
        require(process.poll() is None, "setup failure: first CLI exited before barrier; "+stderr.read_text(errors="replace"))
        if time.monotonic() >= deadline:
            raise TimeoutError("setup failure: actual payload-writing barrier did not arrive")
        time.sleep(0.02)


def control_k09(args, helper, expected, directory, logs):
    target = directory/"collection-run"
    helper.seed(args.baseline, target, pending=True)
    prior = attempts(target)
    stdout_path, stderr_path = logs/"K09-first.stdout", logs/"K09-first.stderr"
    command = cli_command(args.inputs, target, stop="payload-writing")
    marker = None
    first_evidence = None
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        started = time.monotonic()
        first = subprocess.Popen(command, cwd=ROOT, env=environment(), stdout=stdout, stderr=stderr)
        try:
            marker, ownership = wait_barrier(first, target, prior, stderr_path)
            before = scientific_inventory(target/"producer")
            second = run(cli_command(args.inputs, target), logs, "K09-second", helper, expected=2)
            rejection = Path(second["stderr"]["path"]).read_text(errors="replace")
            require("collection already owned" in rejection, "loser did not reach actual OS CollectionLock exclusion")
            require(first.poll() is None and not (marker.parent/"barrier-release").exists(),
                    "first writer did not remain held while second CLI requested ownership")
            after = scientific_inventory(target/"producer")
            require(before == after, "losing CLI changed scientific artifacts or attempts")
            with (marker.parent/"barrier-release").open("xb") as release:
                release.write(b"release actual owned writer\n")
                release.flush()
                os.fsync(release.fileno())
            try:
                first.wait(timeout=CLI_TIMEOUT)
            except subprocess.TimeoutExpired as exc:
                raise TimeoutError("setup failure: released first CLI did not complete") from exc
            require(first.returncode == 0, "first CLI failed after release; "+stderr_path.read_text(errors="replace"))
            first_evidence = {"command": command, "pid": first.pid, "exit_code": first.returncode,
                              "wall_ms": int(1000*(time.monotonic()-started)), "timeout": False}
        finally:
            if marker is not None and not (marker.parent/"barrier-release").exists():
                (marker.parent/"barrier-release").write_bytes(b"release after qualification failure\n")
            if first.poll() is None:
                try:
                    first.wait(timeout=120)
                except subprocess.TimeoutExpired:
                    stop_known_process(first, helper)
    first_evidence.update(stdout=file_ref(stdout_path), stderr=file_ref(stderr_path))
    save(logs/"K09-first.process.json", first_evidence)
    comparison = math_evidence(helper, expected, target)
    return {"cut": "K09", "status": "PASSED", "ownership": ownership,
            "first_cli": first_evidence, "second_cli": second, "second_rejection": rejection.strip(),
            "loser_wrote_no_scientific_artifacts": True, "held_inventory_sha256": digest(before),
            "same_math": comparison, "cleanup": cleanup_evidence(target, prior, stage_required=True)}


def failed_state(target, acceptances_before):
    state = load(target/"slice-state.json")
    require(state["status"] == "FAILED_NO_SCIENTIFIC_ACCEPTANCE", "old PASS was reused or failure state is missing")
    require(sorted(p.name for p in (target/"acceptances").iterdir()) == acceptances_before,
            "negative control published a new scientific acceptance")
    return state


def control_k10(args, helper, expected, directory, logs):
    cases = []
    for mode in ("corrupted", "missing"):
        target = directory/mode
        shutil.copytree(args.baseline, target)
        prior = attempts(target)
        acceptance_names = sorted(p.name for p in (target/"acceptances").iterdir())
        ref = next(node["event"]["artifact"] for _, node in events(target/"producer")
                   if node["event"]["kind"] == "chunk")
        path = target/"producer"/ref["path"]
        original = path.read_bytes()
        require(hashlib.sha256(original).hexdigest() == ref["sha256"], "baseline chunk was not authentic")
        if mode == "corrupted":
            require(bool(original), "empty committed chunk")
            changed = bytes([original[0] ^ 1])+original[1:]
            path.write_bytes(changed)
            (directory/"corrupted-chunk-as-found.bin").write_bytes(changed)
            mutation = file_ref(path, target)
        else:
            path.unlink()
            mutation = {"removed": ref["path"]}
        result = run(cli_command(args.inputs, target), logs, "K10-"+mode, helper, expected=2)
        error = Path(result["stderr"]["path"]).read_text(errors="replace")
        if mode == "corrupted":
            require("artifact fingerprint mismatch" in error, "corruption did not reach artifact fingerprint validation")
        else:
            require("missing artifact" in error or "No such file" in error or "cannot find" in error,
                    "missing reference did not reach actual regular-artifact validation")
        state = failed_state(target, acceptance_names)
        failed_cleanup = cleanup_evidence(target, prior, stage_required=False)
        # Restore only the exact referenced baseline bytes in this owned copy.
        # A new actual CLI acceptance must follow full collection revalidation.
        with path.open("wb") as stream:
            require(stream.write(original) == len(original), "short exact chunk restoration")
            stream.flush()
            os.fsync(stream.fileno())
        restored = file_ref(path, target/"producer")
        require(restored == ref, "restored chunk is not the exact bound snapshot")
        resumed = run(cli_command(args.inputs, target), logs, "K10-"+mode+"-restored-resume", helper)
        comparison = math_evidence(helper, expected, target)
        require(len(list((target/"acceptances").iterdir())) > len(acceptance_names),
                "restored resume reused an old acceptance instead of publishing a new checked receipt")
        cases.append({"case": mode, "referenced_committed_chunk": ref, "mutation": mutation,
                      "actual_cli": result, "rejection": error.strip(), "latest_failed_state": state,
                      "old_pass_not_reused": True, "failed_cleanup": failed_cleanup,
                      "exact_snapshot_restoration": restored, "actual_restored_resume": resumed,
                      "same_math": comparison, "cleanup": cleanup_evidence(target, prior, stage_required=True)})
    return {"cut": "K10", "status": "PASSED", "cases": cases,
            "baseline_reference": {"entries_sha256": digest(expected["entries"]), "scope": "SELECTION_ONLY"},
            "same_math": {"all_exactly_restored_actual_resumes_match_baseline": True,
                          "changed_bytes_were_rejected_before_restoration": True}}


def seed_prior_prefix(helper, baseline, target):
    helper.seed(baseline, target)
    oldest = next((ref, node) for ref, node in reversed(list(events(baseline/"producer")))
                  if node["event"]["kind"] == "prefix")
    state = load(target/"producer/collection.json")
    state["index"] = oldest[0]
    save(target/"producer/collection.json", state, overwrite=True)
    return oldest[1]["event"]["artifact"]


def verify_prior_prefix(helper, inputs, target, prior_ref):
    problem = helper.bind_problem("retained-t081")
    config = load(inputs/"execution.json")
    spec = helper.CollectionSpec.from_dict(problem, config["roles"]["producer"]["collection"])
    with helper.CollectionLock.acquire(target/"producer", spec, resume=True) as lock:
        refs = [node["event"]["artifact"] for node in lock._events() if node["event"]["kind"] == "prefix"]
        require(prior_ref in refs, "previous committed mathematical prefix disappeared")
    actual = file_ref(target/"producer"/prior_ref["path"], target/"producer")
    require(actual == prior_ref, "previous mathematical prefix bytes changed")
    return {"prior_prefix": prior_ref, "actual_collection_lock_resume_validation": True,
            "prior_prefix_still_authoritative_and_unchanged": True, "committed_prefixes": len(refs)}


def control_k11(args, helper, expected, directory, logs):
    positive = directory/"positive"
    positive_ref = seed_prior_prefix(helper, args.baseline, positive)
    positive_before = attempts(positive)
    positive_run = run(cli_command(args.inputs, positive), logs, "K11-positive-first", helper)
    positive_math = math_evidence(helper, expected, positive)
    positive_prior = verify_prior_prefix(helper, args.inputs, positive, positive_ref)
    cases = []
    for mode in ("sharing-denial", "short-write", "owned-quota"):
        target = directory/mode
        prior_ref = seed_prior_prefix(helper, args.baseline, target)
        before = attempts(target)
        prior = verify_prior_prefix(helper, args.inputs, target, prior_ref)
        acceptance_names = sorted(p.name for p in (target/"acceptances").iterdir())
        injection_report = directory/(mode+"-injection.json")
        command = [sys.executable, "-B", str(THIS), "--_io-child", mode,
                   "--inputs", str(args.inputs), "--output-dir", str(target),
                   "--_child-report", str(injection_report)]
        rejected = run(command, logs, "K11-"+mode+"-injected", helper, expected=2)
        injection = load(injection_report)
        require(injection["injection_fired"] and injection["actual_cli_exit_code"] == 2,
                "injection did not reach actual changed publication path")
        error = Path(rejected["stderr"]["path"]).read_text(errors="replace")
        expected_error = {"sharing-denial": "INJECTED sharing denial", "short-write": "short artifact write",
                          "owned-quota": "collection volume exceeds cap"}[mode]
        require(expected_error in error, "actual failure stderr does not identify intended I/O refusal")
        state = failed_state(target, acceptance_names)
        retained_prior = verify_prior_prefix(helper, args.inputs, target, prior_ref)
        require(retained_prior["committed_prefixes"] == prior["committed_prefixes"],
                "injected error advanced mathematical prefix coverage")
        failed_cleanup = cleanup_evidence(target, before, stage_required=True)
        resumed = run(cli_command(args.inputs, target), logs, "K11-"+mode+"-resume", helper)
        comparison = math_evidence(helper, expected, target)
        cases.append({"case": mode, "kind": "BOUNDED_INJECTED_IO_ERROR", "injection": injection,
                      "actual_failed_cli": rejected, "failure_stderr": error.strip(), "failure_state": state,
                      "retained_prior": retained_prior, "failed_stage_cleanup": failed_cleanup,
                      "uninjected_resume": resumed, "same_math": comparison,
                      "resume_cleanup": cleanup_evidence(target, before, stage_required=True)})
    return {"cut": "K11", "status": "PASSED", "positive_control_ran_first": True,
            "positive_control": {"actual_cli": positive_run, "same_math": positive_math,
                                 "prior_prefix": positive_prior,
                                 "cleanup": cleanup_evidence(positive, positive_before, stage_required=True)},
            "cases": cases, "host_disk_was_not_filled": True,
            "same_math": {"positive_first_and_all_uninjected_resumes_match_baseline": True},
            "limits": "bounded named injections; no actual device exhaustion claim"}


def copy_capture(helper, inputs, capture):
    capture.mkdir()
    problem = helper.bind_problem("retained-t081")
    config = load(inputs/"execution.json")
    references = {}
    def add(ref):
        previous = references.get(ref.path)
        require(previous is None or previous == ref, "conflicting captured file binding")
        references[ref.path] = ref
    for ref in problem.evidence:
        add(ref)
    for role in ("producer", "analytic"):
        row = config["roles"][role]
        for value in row["collection"]["code_refs"]:
            add(helper.ArtifactRef(**value))
        provenance = helper.ArtifactRef(**row["execution"]["provenance"])
        add(provenance)
        for value in load(ROOT/provenance.path)["files"]:
            add(helper.ArtifactRef(**value))
    for name, sha in helper._HELPERS.items():
        path = ROOT/helper.BUNDLE/name
        ref = helper.ArtifactRef(**file_ref(path, ROOT))
        require(ref.sha256 == sha, "neutral helper changed before capture")
        add(ref)
    for ref in sorted(references.values(), key=lambda item: item.path):
        raw = (ROOT/ref.path).read_bytes()
        require(len(raw) == ref.size and hashlib.sha256(raw).hexdigest() == ref.sha256,
                "captured code/input fingerprint differs: "+ref.path)
        path = capture/ref.path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            require(stream.write(raw) == len(raw), "short captured file write")
    require("scripts/weil_whole_source_split.py" in references, "actual CLI entrypoint is not bound in capture closure")
    return problem, config, references


def rebind_capture(helper, problem, config, capture, *, dirty=False):
    config = deepcopy(config)
    for role in ("producer", "analytic"):
        row = config["roles"][role]
        original = helper.CollectionSpec.from_dict(problem, row["collection"], code_root=ROOT)
        refs = tuple(helper.ArtifactRef(**file_ref(capture/ref.path, capture)) for ref in original.code_refs)
        plan = helper.ExecutionPlan.from_dict(row["execution"])
        origin_path = capture/plan.provenance.path
        origin = load(origin_path)
        origin["files"] = [file_ref(capture/value["path"], capture) for value in origin["files"]]
        if dirty:
            origin["origin_git_dirty"] = True
        save(origin_path, origin, overwrite=True)
        spec = helper.CollectionSpec.create(problem, role=original.role, quantities=original.quantities,
            partition=original.partition, backend=original.backend, backend_version=original.backend_version,
            native_threads=original.native_threads, code_refs=refs, bounds=original.bounds,
            code_root=capture, grid_bits=original.grid_bits)
        plan = replace(plan, collection_sha256=spec.collection_id,
                       task_program=next(ref for ref in refs if ref.path == plan.task_program.path),
                       provenance=helper.ArtifactRef(**file_ref(origin_path, capture)))
        row["collection"], row["execution"] = spec.to_dict(), plan.to_dict()
    return config


def save_inputs(original, directory, config=None, problem=None, cases=None):
    directory.mkdir()
    for name, changed in (("problem", problem), ("cases", cases), ("execution", config)):
        if changed is None:
            shutil.copyfile(original/(name+".json"), directory/(name+".json"))
        else:
            save(directory/(name+".json"), changed)


def control_k12(args, helper, expected, directory, logs):
    problem = helper.bind_problem("retained-t081")
    original_config = load(args.inputs/"execution.json")
    cases = []
    layers = {"partition": "slice-resume-context", "code": "slice-resume-context",
              "role": "arithmetic-role/context", "precision": "slice-resume-context",
              "grid": "arithmetic-role/context", "scalar": "reviewed-problem-semantic-binding"}
    messages = {"partition": "incompatible slice resume context", "code": "incompatible slice resume context",
                "role": "incorrect arithmetic role/context", "precision": "incompatible slice resume context",
                "grid": "incorrect arithmetic role/context", "scalar": "unqualified arithmetic problem binding"}
    for mode in ("partition", "code", "role", "precision", "grid", "scalar"):
        case = directory/mode
        case.mkdir()
        target, inputs = case/"collection-run", case/"inputs"
        helper.seed(args.baseline, target)
        before = attempts(target)
        original_manifest = file_ref(target/"producer/collection.json", target)
        config, case_set, document = deepcopy(original_config), load(args.inputs/"cases.json"), load(args.inputs/"problem.json")
        root = ROOT
        independent = {"wire_schema_validated": True, "alteration": mode,
                       "original_math_code_not_edited": True}
        if mode == "code":
            root = case/"captured-code"
            captured_problem, copied_config, _ = copy_capture(helper, args.inputs, root)
            path = root/"scripts/whole_source/producer.py"
            with path.open("ab") as stream:
                stream.write(b"\n# K12 independently bound changed-code context control.\n")
            config = rebind_capture(helper, captured_problem, copied_config, root, dirty=True)
            independent["new_code_sha256"] = file_ref(path, root)["sha256"]
            independent["new_collection_id"] = helper.CollectionSpec.from_dict(
                problem, config["roles"]["producer"]["collection"], code_root=root).collection_id
        elif mode == "scalar":
            document["parameters"]["support"] = {"numerator": hex(4), "denominator": hex(5)}
            document["problem_id"] = digest({key: value for key, value in document.items() if key != "problem_id"})
            independent.update(wire_schema_validated=True, revised_scalar="4/5",
                reviewed_alternative_problem=False,
                limitation="same-schema scalar candidate is rejected by reviewed exact problem gate; no new mathematical evaluation")
        else:
            row = config["roles"]["producer"]
            old = helper.CollectionSpec.from_dict(problem, row["collection"])
            plan = helper.ExecutionPlan.from_dict(row["execution"])
            kwargs = {}
            if mode == "partition":
                old_width = dict(old.partition)["node"]
                width = old_width-1 if old_width > 1 else 2
                require(width <= problem.source_gauss_order, "no valid different node partition")
                kwargs["partition"] = tuple((name, width if name == "node" else value) for name, value in old.partition)
                case_set["node_block"] = width
                independent.update(old_node_block=old_width, revised_node_block=width)
            elif mode == "role":
                kwargs["role"] = "analytic"
                plan = replace(plan, role="analytic")
            elif mode == "precision":
                plan = replace(plan, precision_bits=plan.precision_bits+1)
                independent["limitation"] = "valid execution-plan integer, incompatible policy; resume context rejects before native precision admission"
            elif mode == "grid":
                kwargs["grid_bits"] = old.grid_bits+1
            revised = helper.CollectionSpec.create(problem, role=kwargs.get("role", old.role), quantities=old.quantities,
                partition=kwargs.get("partition", old.partition), backend=old.backend,
                backend_version=old.backend_version, native_threads=old.native_threads,
                code_refs=old.code_refs, bounds=old.bounds, grid_bits=kwargs.get("grid_bits", old.grid_bits))
            plan = replace(plan, collection_sha256=revised.collection_id)
            row["collection"], row["execution"] = revised.to_dict(), plan.to_dict()
            require(helper.CollectionSpec.from_dict(problem, row["collection"]).collection_id == revised.collection_id,
                    "revised collection is not independently valid")
            helper.ExecutionPlan.from_dict(row["execution"])
            independent["new_collection_id"] = revised.collection_id
        save_inputs(args.inputs, inputs, config=config, problem=document, cases=case_set)
        result = run(cli_command(inputs, target, root), logs, "K12-"+mode, helper, expected=2)
        error = Path(result["stderr"]["path"]).read_text(errors="replace")
        require(messages[mode] in error, mode+": wrong rejection layer, not the intended semantic/context gate")
        require(file_ref(target/"producer/collection.json", target) == original_manifest,
                "incompatible resume changed existing collection manifest")
        require(attempts(target) == before and not (target/"slice-state.json").exists(),
                "incompatible context started native execution or created a new scientific state")
        compatible = run(cli_command(args.inputs, target), logs, "K12-"+mode+"-compatible-resume", helper)
        comparison = math_evidence(helper, expected, target)
        cases.append({"case": mode, "actual_cli": result, "rejection_layer": layers[mode],
                      "rejection": error.strip(), "independent_rebinding": independent,
                      "retained_input_refs": [file_ref(inputs/(name+".json"), directory)
                                              for name in ("problem", "cases", "execution")],
                      "existing_collection_unchanged_by_rejected_variant": True,
                      "rejected_variant_native_scientific_tasks_started": False,
                      "compatible_original_context_resume": compatible, "same_math": comparison,
                      "cleanup": cleanup_evidence(target, before, stage_required=True)})
    return {"cut": "K12", "status": "PASSED", "cases": cases,
            "same_math": {"all_compatible_original_context_resumes_match_baseline": True,
                          "changed_contexts_rejected_before_any_prefix_reuse": True},
            "baseline_entries_sha256": digest(expected["entries"]), "scope": "SELECTION_ONLY"}


def control_k13(args, helper, expected, directory, logs):
    root, inputs = directory/"captured-root", directory/"inputs"
    problem, config, refs = copy_capture(helper, args.inputs, root)
    config = rebind_capture(helper, problem, config, root)
    save_inputs(args.inputs, inputs, config=config)
    inventory = [file_ref(path, root) for path in sorted(root.rglob("*")) if path.is_file()]
    require(not (root/".git").exists() and {value["path"] for value in inventory} == set(refs),
            "captured replay tree is not the exact bound closure")
    require(not any("expected" in value["path"].lower() for value in inventory),
            "expected-output-named file entered normal captured closure")
    for role in ("producer", "analytic"):
        row = config["roles"][role]
        helper.CollectionSpec.from_dict(problem, row["collection"], code_root=root)
        helper.ExecutionPlan.from_dict(row["execution"])
        require(row["execution"]["provenance"]["path"] ==
                load(args.inputs/"execution.json")["roles"][role]["execution"]["provenance"]["path"],
                "capture changed provenance relativepath")
    save(directory/"capture-inventory.json", {"files": inventory, "input_refs": [file_ref(inputs/(name+".json"), directory)
         for name in ("problem", "cases", "execution")], "no_git_directory": True,
         "no_expected_output_in_normal_child_inputs": True,
         "origin_scope": "raw-bound captured origin claim, not a new Git checkout"})
    target = directory/"fresh-replay"
    positive = run(cli_command(inputs, target, root, resume=False), logs, "K13-captured-replay", helper, cwd=root)
    comparison = math_evidence(helper, expected, target)
    positive_cleanup = cleanup_evidence(target, {"producer": set(), "analytic": set()}, stage_required=True)
    candidate = directory/"oracle-attack-candidate.json"
    save(candidate, {"format": "untrusted-expected-selected-arithmetic-v1", "entries": expected["entries"],
                     "scope": "DELIBERATE_NEGATIVE_RUNTIME_INJECTION"})
    probe_report = directory/"oracle-probe.json"
    probe_output = directory/"oracle-probe-collection"
    command = [sys.executable, "-B", str(THIS), "--_oracle-child", "--inputs", str(inputs),
               "--output-dir", str(probe_output), "--_code-root", str(root),
               "--_candidate-file", str(candidate), "--_child-report", str(probe_report)]
    negative = run(command, logs, "K13-runtime-oracle-rejection", helper, cwd=root, expected=2)
    probe = load(probe_report)
    require(probe["owned_workload_execution_entered"] and probe["actual_run_stage_called"] and
            probe["runtime_validator_rejected"] and probe["native_scientific_tasks_started"] is False,
            "oracle injection did not exercise the actual owned runtime admission gate")
    require("unbound file or expected-output oracle" in Path(negative["stderr"]["path"]).read_text(errors="replace"),
            "runtime oracle rejection stderr missing")
    return {"cut": "K13", "status": "PASSED", "fresh_captured_replay": positive,
            "capture_inventory": file_ref(directory/"capture-inventory.json", directory),
            "same_math": comparison, "cleanup": positive_cleanup,
            "runtime_oracle_negative": {"actual_child": negative, "probe": probe,
                                        "candidate": file_ref(candidate, directory)},
            "limits": "input/code isolation and runtime-tree admission, not a hostile-OS sandbox; installed system packages remain visible",
            "scope": "SELECTION_ONLY", "full_mathematical_source": False,
            "matrix_positivity": False, "production_admission": False}


def io_child(args):
    child_import_root(ROOT)
    from scripts import weil_whole_source_split as cli
    from scripts.whole_source import artifacts
    from scripts import run_observability
    producer = (args.output_dir/"producer").resolve()
    mode = args._io_child
    calls = []
    original_replace, original_write = os.replace, artifacts._write_all
    collection = load(producer/"collection.json")["collection"]
    bounds = artifacts.CodecBounds(**collection["bounds"])

    def prefix_index(path, raw=None):
        if not isinstance(path, (str, os.PathLike)):
            return False
        path = Path(path).resolve()
        if path.parent != producer/"index" or not path.name.startswith(".pending-"):
            return False
        try:
            value = json.loads(path.read_bytes() if raw is None else raw)
        except (ValueError, OSError):
            # The actual writer exposes the first half before its interruption
            # barrier. Canonical index fragments still identify the prefix kind.
            return raw is not None and b'"kind":"prefix"' in raw
        return value.get("format") == "whole-source-index-v1" and value.get("event", {}).get("kind") == "prefix"

    def injected_replace(source, destination, *positional, **kwargs):
        if mode == "sharing-denial" and prefix_index(source):
            calls.append({"operation": "os.replace", "source": str(source), "destination": str(destination),
                          "injection": "INJECTED sharing denial", "attempt": len(calls)+1})
            raise PermissionError(errno.EACCES, "INJECTED sharing denial at owned scientific prefix-index publication", str(destination))
        return original_replace(source, destination, *positional, **kwargs)

    def injected_write(stream, raw):
        if mode in ("short-write", "owned-quota") and prefix_index(stream.name, raw):
            if mode == "short-write":
                class ShortWrite:
                    def write(self, payload):
                        requested = max(1, len(payload)//2)
                        actual = stream.write(payload[:requested])
                        calls.append({"operation": "actual stream.write", "path": str(stream.name),
                                      "requested_bytes": len(payload), "actual_written_bytes": actual,
                                      "injection": "INJECTED bounded short write"})
                        return actual
                return original_write(ShortWrite(), raw)
            used = artifacts._volume(producer)
            injected_bounds = replace(bounds, max_total_bytes=used)
            calls.append({"operation": "actual owned _check_quota at scientific index write", "path": str(stream.name),
                          "owned_bytes": used, "injected_owned_cap_bytes": used, "additional_bytes": len(raw),
                          "original_owned_cap_bytes": bounds.max_total_bytes,
                          "injection": "INJECTED bounded owned quota refusal"})
            artifacts._check_quota(producer, injected_bounds, len(raw), len(raw))
            raise AssertionError("owned quota injection unexpectedly allowed publication")
        return original_write(stream, raw)

    with patch("os.replace", injected_replace), patch("scripts.whole_source.artifacts._write_all", injected_write):
        code = cli.main(cli_arguments(args.inputs, args.output_dir, ROOT))
    if mode == "sharing-denial":
        require(len(calls) == len(run_observability.ATOMIC_REPLACE_RETRY_DELAYS_SECONDS)+1,
                "sharing-denial control did not exhaust actual retry policy")
    else:
        require(len(calls) == 1, "write injection did not fire exactly once")
    save(args._child_report, {"format": "selected-arithmetic-bounded-io-injection-v1", "mode": mode,
        "injection_fired": bool(calls), "actual_cli_exit_code": code, "calls": calls,
        "unchanged_mathematical_code_refs": collection["code_refs"],
        "target_scope": "owned producer scientific prefix-index publication only",
        "host_device_exhaustion": False, "collection_bounds_not_persistently_changed": True})
    return code


def oracle_child(args):
    child_import_root(args._code_root)
    from scripts.whole_source.contract import bind_problem, ContractError
    from scripts.whole_source.artifacts import CollectionLock, CollectionSpec
    from scripts.whole_source.execution import ExecutionPlan, WorkloadExecution
    problem = bind_problem("retained-t081", root=args._code_root)
    row = load(args.inputs/"execution.json")["roles"]["producer"]
    spec = CollectionSpec.from_dict(problem, row["collection"], code_root=args._code_root)
    plan = ExecutionPlan.from_dict(row["execution"])
    report = {"format": "selected-arithmetic-runtime-oracle-probe-v1", "owned_workload_execution_entered": False,
              "actual_run_stage_called": False, "runtime_validator_rejected": False}
    execution = None
    error = None
    try:
        with CollectionLock.acquire(args.output_dir, spec) as lock:
            with WorkloadExecution(lock, spec, plan, code_root=args._code_root) as execution:
                report["owned_workload_execution_entered"] = True
                path = execution.runtime_root/"expected-selected-arithmetic.json"
                with path.open("xb") as stream:
                    raw = args._candidate_file.read_bytes()
                    require(stream.write(raw) == len(raw), "short injected oracle write")
                    stream.flush()
                    os.fsync(stream.fileno())
                report["injected_runtime_file"] = file_ref(path, args.output_dir)
                request = {"operation": "preparation"}
                request["task_id"] = digest(request)
                report["actual_run_stage_called"] = True
                execution.run_stage("oracle_probe", [request])
    except ContractError as exc:
        error = str(exc)
        report["rejection"] = error
        report["runtime_validator_rejected"] = "unbound file or expected-output oracle" in error
    require(execution is not None, "runtime oracle probe never entered WorkloadExecution")
    require(report["runtime_validator_rejected"], "installed expected output was not rejected by actual runtime validator")
    require(not execution.receipts and not execution.backend.receipts and
            not (execution.output/"oracle_probe-tasks.jsonl").exists() and
            not (execution.output/"oracle_probe-attachment.json").exists() and
            not (execution.output/"oracle_probe").exists(), "native task began before runtime oracle rejection")
    require((execution.output/"artifact-invalidated").is_file(), "rejected owned attempt was not invalidated")
    report.update(native_scientific_tasks_started=False, owned_stage_receipts=execution.receipts,
                  attempt_invalidated=True, attempt_id=execution.attempt_id,
                  origin_math_code_refs_unchanged=True,
                  cleanup="no native root or pool was started; owned attempt invalidated and context managers exited")
    save(args._child_report, report)
    print("Arithmetic runtime oracle rejected: "+error, file=sys.stderr)
    return 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--_io-child", choices=("sharing-denial", "short-write", "owned-quota"), help=argparse.SUPPRESS)
    parser.add_argument("--_oracle-child", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--_child-report", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--_code-root", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--_candidate-file", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    for name in ("inputs", "baseline", "output_dir", "_child_report", "_code_root", "_candidate_file"):
        if getattr(args, name) is not None:
            setattr(args, name, getattr(args, name).resolve())
    require(not (args._io_child and args._oracle_child), "choose only one qualification child mode")
    if args._io_child:
        require(args._child_report is not None, "I/O child report required")
        return io_child(args)
    if args._oracle_child:
        require(args._child_report is not None and args._code_root is not None and args._candidate_file is not None,
                "oracle child requires captured code, candidate and report")
        return oracle_child(args)
    if args.baseline is None:
        parser.error("--baseline is required")
    require(os.name == "nt", "these actual OS/process qualification controls require Windows")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    logs = args.output_dir/"logs"
    logs.mkdir()
    helper = recovery()
    expected = helper.receipt(args.baseline)
    require(expected["scope"] == "SELECTION_ONLY" and expected["all_owned_cleanup_verified"] and
            not expected["full_mathematical_source"] and len(expected["entries"]) == 6,
            "baseline is not complete selected scientific arithmetic")
    outcomes = []
    for label, function in zip(CUTS, (control_k09, control_k10, control_k11, control_k12, control_k13)):
        directory = args.output_dir/label
        directory.mkdir()
        try:
            outcome = function(args, helper, expected, directory, logs)
        except Exception as exc:
            trace_path = logs/(label+"-setup-or-control-failure.txt")
            with trace_path.open("x", encoding="utf-8") as stream:
                traceback.print_exc(file=stream)
            outcome = {"cut": label, "status": "SETUP_FAILED_OR_UNEXPECTED_RESULT",
                       "error": type(exc).__name__+": "+str(exc), "traceback": file_ref(trace_path),
                       "passed": False, "retained_case_directory": str(directory),
                       "retained_raw_log_directory": str(logs)}
        save(directory/"qualification.json", outcome)
        outcomes.append(outcome)
        print(json.dumps({"event": "boundary_control_complete", "cut": label,
                          "status": outcome["status"]}), flush=True)
    require(len(outcomes) == 5 and [row["cut"] for row in outcomes] == list(CUTS), "incorrect aggregate control table")
    passed = all(row["status"] == "PASSED" for row in outcomes)
    report = {"format": "selected-arithmetic-boundary-qualification-v1",
              "status": "QUALIFIED_SELECTED_BOUNDARIES" if passed else "NOT_QUALIFIED",
              "controls": outcomes, "all_five_controls_passed": passed,
              "baseline_receipt": load(args.baseline/"slice-state.json")["receipt"],
              "baseline_entries_sha256": digest(expected["entries"]),
              "comparison_oracles_external_to_normal_scientific_runtime": True,
              "scope": "SELECTION_ONLY", "full_mathematical_source": False,
              "matrix_positivity": False, "production_admission": False,
              "limits": ["no power-loss guarantee", "K11 is injected I/O refusal, not real device exhaustion",
                         "K13 is bound input/code isolation, not a hostile-OS sandbox",
                         "system Python packages remain visible to completed child runtimes"]}
    save(args.output_dir/"qualification.json", report)
    print(json.dumps({"status": report["status"], "controls": len(outcomes), "scope": "SELECTION_ONLY"}), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
