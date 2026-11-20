"""Owned, resumable selected linear arithmetic with independent reconstruction."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import uuid

from scripts.whole_source.contract import (
    ROOT, ArtifactRef, ContractError, QuantityKey, bind_problem, canonical_bytes,
    expected_domain, problem_id, quantity_document,
)
from scripts.whole_source.artifacts import (
    Axis, CodecBounds, CollectionLock, CollectionSpec, ContributionTask, ChunkStore,
    QuantitySpec, StagedChunk, _check_lock_file, _decode_chunk, _os_lock, _root_path,
    _safe, _task, decode_rational, encode_rational, qualification_barrier,
)
from scripts.whole_source.execution import (
    MIB, ExecutionPlan, WorkloadExecution, _RUNTIME, _bound, _bytes, _json, _write, exact_telemetry,
)


def _require(condition, message):
    if not condition:
        raise ContractError(message)


def _ref(root, path):
    raw = (root/path).read_bytes()
    return ArtifactRef(path, hashlib.sha256(raw).hexdigest(), len(raw))


def _request(**value):
    return {"task_id": hashlib.sha256(canonical_bytes(value)).hexdigest(), **value}


def selected_pairs(problem):
    return ((0, 0), (1, 1), (problem.N, problem.N-2), (problem.N+1, problem.N-1),
            (problem.M-2, problem.N-2), (problem.M-1, problem.N-1))


def prepare_inputs(problem, directory, *, origin_git_commit, origin_git_dirty,
                   code_root=ROOT, memory_mib=None, node_block=257):
    """Write explicit input/resource bindings; this function executes no native work."""
    root, directory = Path(code_root).resolve(), Path(directory).resolve()
    _require(problem.profile == "retained-t081", "only retained arithmetic selections are qualified")
    _require(type(node_block) is int and 1 <= node_block <= problem.source_gauss_order,
             "invalid node partition")
    directory.mkdir(parents=True, exist_ok=False)
    problem_document = problem.to_dict()
    problem_document["problem_id"] = problem_id(problem)
    _write(directory/"problem.json", canonical_bytes(problem_document))
    cases = {"format": "whole-source-arithmetic-cases-v1", "problem_id": problem_id(problem),
             "entries": [list(pair) for pair in selected_pairs(problem)], "node_block": node_block,
             "scope": "SELECTION_ONLY"}
    _write(directory/"cases.json", canonical_bytes(cases))
    roles = {}
    for role, filename, function in (("producer", "producer.py", "evaluate"),
                                     ("analytic", "analytic.py", "evaluate")):
        paths = (*_RUNTIME, "scripts/whole_source/slice.py",
                 "scripts/whole_source/"+filename)
        refs = tuple(sorted((_ref(root, path) for path in paths), key=lambda ref: ref.path))
        origin = {"format": "whole-source-code-origin-v1", "origin_git_commit": origin_git_commit,
                  "origin_git_dirty": origin_git_dirty, "files": [asdict(ref) for ref in refs]}
        origin_path = directory/(role+"-origin.json")
        _write(origin_path, canonical_bytes(origin))
        axes = (Axis("term", 0, 4), Axis("window", 0, 2))
        if role == "producer":
            axes += (Axis("node", 0, problem.source_gauss_order),)
        quantities = []
        for m, n in selected_pairs(problem):
            key = QuantityKey("P_L" if m < problem.N else "P_H", m % 2, entry=(m, n))
            domain = expected_domain(problem, key)
            quantities.append(QuantitySpec(key, domain.rows, domain.columns,
                                           domain.symmetric_upper, axes))
        partition = {"rows": 1, "columns": 1, "term": 1, "window": 1}
        if role == "producer":
            partition["node"] = node_block
        bounds = CodecBounds(8*MIB, 8*MIB, 8*MIB, 16384, 8192, 256*1024,
                             64*1024, 512*MIB, 64*MIB, 64*MIB)
        version = importlib.metadata.version("python-flint")
        spec = CollectionSpec.create(problem, role=role, quantities=tuple(quantities),
            partition=tuple(sorted(partition.items())), backend="python-flint", backend_version=version,
            native_threads=1, code_refs=refs, bounds=bounds, code_root=root)
        plan = ExecutionPlan(problem_id(problem), spec.collection_id, role, 1, 1, 1,
            memory_mib=memory_mib or 1, reserve_mib=128, root_mib=128, worker_base_mib=80,
            worker_private_mib=128, native_workspace_mib=128, conversion_mib=64,
            codec_mib=256, queue_mib=8, supervisor_increment_mib=256,
            repository_mib=384, temporary_mib=64, minimum_free_mib=64,
            max_tasks=128, task_bytes=32768, result_bytes=32768, log_bytes=4*MIB,
            task_program=_ref(root, "scripts/whole_source/"+filename), task_function=function,
            precision_bits=problem.arithmetic.source_bits if role == "producer" else problem.arithmetic.audit_bits,
            backend="python-flint", backend_version=version,
            provenance=_ref(root, origin_path.relative_to(root).as_posix()), scope="SELECTION_ONLY")
        from scripts.whole_source.resources import auto_plan
        plan = auto_plan(plan, parallel=True, memory_mib=memory_mib, helper_root=root)
        spec = replace(spec, native_threads=plan.threads)
        spec._validate()
        plan = replace(plan, collection_sha256=spec.collection_id)
        roles[role] = {"collection": spec.to_dict(), "execution": plan.to_dict()}
    config = {"format": "whole-source-arithmetic-execution-v1", "roles": roles, "scope": "SELECTION_ONLY"}
    _write(directory/"execution.json", canonical_bytes(config))
    return {name: directory/(name+".json") for name in ("problem", "cases", "execution")}


def _atomic_snapshot(path, value):
    from scripts.run_observability import replace_path_with_permission_retry
    temporary = path.with_name("."+path.name+"-"+uuid.uuid4().hex)
    _write(temporary, canonical_bytes(value))
    replace_path_with_permission_retry(temporary, path)


def _parse_staged(value):
    task = _task(value["task"])
    return task, StagedChunk(Path(value["path"]), task, ArtifactRef(**value["ref"]),
                             value["generation"], value["attempt_id"])


def _full_task(quantity):
    return ContributionTask(quantity.key, quantity.rows, quantity.columns, quantity.axes)


def _recover_orphans(store):
    recovered, quarantined = [], []
    accepted = {canonical_bytes(task.to_dict()): ref for task, ref in store._chunk_events()}
    for directory in sorted((store.lock.root/"attempts").iterdir()):
        if directory.name == store.attempt_id or not (directory/"staging").is_dir():
            continue
        for path in sorted((directory/"staging").iterdir()):
            _require(path.is_file() and not path.is_symlink(), "unsafe prior staging member")
            if path.stat().st_size > store.spec.bounds.max_compressed_bytes:
                quarantined.append({"path": path.relative_to(store.lock.root).as_posix(), "reason": "oversized orphan"})
                continue
            raw = path.read_bytes()
            ref = ArtifactRef(path.relative_to(store.lock.root).as_posix(), hashlib.sha256(raw).hexdigest(), len(raw))
            try:
                snapshot = _decode_chunk(store.spec, raw)
                task = _task(snapshot.header["task"])
            except (ContractError, OSError, ValueError):
                quarantined.append({"ref": asdict(ref), "reason": "not a complete compatible chunk"})
                continue
            key = canonical_bytes(task.to_dict())
            if key in accepted:
                _require((accepted[key].sha256, accepted[key].size) == (ref.sha256, ref.size),
                         "conflicting complete orphan retry")
            else:
                committed = store.recover_staged_chunk(task, ref)
                recovered.append({"orphan": asdict(ref), "committed": asdict(committed), "task": task.to_dict()})
                accepted[key] = committed
    return {"recovered": recovered, "quarantined": quarantined}


def _pending_tasks(spec, store):
    accepted = {canonical_bytes(task.to_dict()) for task, _ in store._chunk_events()}
    width = dict(spec.partition).get("node", 1)
    starts = range(0, spec.problem.source_gauss_order, width) if spec.role == "producer" else (0,)
    for start in starts:
        for term in range(4):
            for window in range(2):
                axes = (Axis("term", term, term+1), Axis("window", window, window+1))
                values = {"operation": "window", "term_index": term, "window_index": window}
                if spec.role == "producer":
                    stop = min(spec.problem.source_gauss_order, start+width)
                    axes += (Axis("node", start, stop),)
                    values.update(operation="nodes", node_start=start, node_stop=stop)
                if spec.role == "analytic" or any(
                        canonical_bytes(ContributionTask(q.key, q.rows, q.columns, axes).to_dict()) not in accepted
                        for q in spec.quantities):
                    # Stored analytical values are not an independent oracle.
                    # Fresh reconstruction must agree before any new acceptance.
                    yield _request(**values)


def _read_prefix(root, ref, spec):
    from scripts.whole_source.artifacts import _decode_prefix
    return _decode_prefix(spec, _bound(root, ref), ref)


def _run_role(root, spec, plan, *, code_root, resume, qualification_stop=None):
    with CollectionLock.acquire(root, spec, resume=resume) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=code_root,
                               qualification_stop=qualification_stop) as execution:
            store = ChunkStore(lock, spec, attempt_id=execution.attempt_id)
            orphan_report = _recover_orphans(store) if resume else {"recovered": [], "quarantined": []}
            execution.run_stage("preparation", [_request(operation="preparation")])
            preparation = next(execution.read_results("preparation"))["result"]["preparation"]
            pending = tuple(_pending_tasks(spec, store))
            statistics = []
            if pending:
                execution.run_stage("arithmetic", pending)
                for result in execution.read_results("arithmetic"):
                    _require(result["scope"] == "SELECTION_ONLY", "incorrect scientific task scope")
                    for value in result["result"]["chunks"]:
                        task, staged = _parse_staged(value)
                        store.publish_chunk(task, staged)
                    statistics.append(result["result"]["statistics"])
            rows = []
            for quantity in spec.quantities:
                full = _full_task(quantity)
                prior_ref = store._latest_prefix(full)
                prior = _read_prefix(root, prior_ref, spec) if prior_ref else None
                covered = prior.covered if prior else 0
                refs = []
                for task, ref in store._chunk_events():
                    if task.quantity == quantity.key:
                        rank = 0
                        for axis, part in zip(quantity.axes, task.axes):
                            rank = rank*len(axis)+(part.start-axis.start)//axis.step
                        if rank >= covered:
                            refs.append(ref)
                if refs:
                    final = execution.reduce_prefix(store, full, prior_ref, refs)
                else:
                    # Actual owned revalidation, not an old-PASS shortcut.
                    request = _request(operation="read-prefix", task=full.to_dict())
                    name = "validate_"+str(len(rows))
                    execution.run_stage(name, [request])
                    checked = next(execution.read_results(name))["result"]
                    _require(prior_ref is not None and checked["prefix"] == asdict(prior_ref), "prefix validation changed")
                    final = prior_ref
                snapshot = _read_prefix(root, final, spec)
                total = 1
                for axis in full.axes:
                    total *= len(axis)
                _require(snapshot.covered == total and len(snapshot.records) == 1, "incomplete selected entry")
                record = snapshot.records[0]
                rows.append({"quantity": quantity_document(quantity.key), "covered": total,
                    "lower": encode_rational(record.lower, 8192), "upper": encode_rational(record.upper, 8192),
                    "prefix": asdict(final)})
            qualification_barrier(lock.root, execution.attempt_id, "slice-before-seal")
            seals = [asdict(store.seal_quantity(q.key)) for q in spec.quantities]
            return {"role": spec.role, "collection_id": spec.collection_id, "execution_id": plan.execution_id,
                "attempt_id": execution.attempt_id, "entries": rows, "preparation": preparation,
                "quantity_seals": seals, "statistics": statistics, "orphan_recovery": orphan_report,
                "owned_receipts": exact_telemetry(execution.receipts), "scope": "SELECTION_ONLY"}


def _interval(row):
    lower, upper = decode_rational(row["lower"], 8192), decode_rational(row["upper"], 8192)
    _require(lower <= upper, "reversed scientific interval")
    return lower, upper


def check_entries(problem, source, analytic):
    """Containment, exact physical mass and endpoint payments, not matrix positivity."""
    pairs = selected_pairs(problem)
    _require(len(source) == len(analytic) == len(pairs), "incomplete six-entry comparison")
    result = []
    for (m, n), producer, consumer in zip(pairs, source, analytic):
        key = QuantityKey("P_L" if m < problem.N else "P_H", m % 2, entry=(m, n))
        _require(producer["quantity"] == consumer["quantity"] == quantity_document(key),
                 "incorrect physical head/low entry mapping")
        _require(producer["covered"] == 8*problem.source_gauss_order and consumer["covered"] == 8,
                 "incomplete signed arithmetic contribution cover")
        lo, hi = _interval(producer)
        alo, ahi = _interval(consumer)
        _require(lo <= alo <= ahi <= hi, "independent arithmetic containment failed at "+str((m, n)))
        mass, input_mass = Fraction(2, 2*m+1), Fraction(2, 2*n+1)
        if "mass" in producer:
            _require(decode_rational(producer["mass"], 8192) == mass, "incorrect physical output mass")
        expansion = (lo/mass, hi/mass)
        if "expansion" in producer:
            proposed = tuple(decode_rational(x, 8192) for x in producer["expansion"])
            _require(proposed == expansion, "bilinear/expansion physical mass payment failed")
        scale = 1 << problem.arithmetic.publication_bits
        public_lo = Fraction((lo*scale).__floor__()-1, scale)
        public_hi = Fraction((hi*scale).__ceil__()+1, scale)
        physical_radius = (public_hi-public_lo)/2*max(1/mass, 1/input_mass)
        _require(physical_radius < problem.numerical_goal, "selected physical entry numerical goal failed")
        ledger = {"checkpoint_stage_per_endpoint_upper": Fraction(2*producer["covered"], 1<<512),
                  "checkpoint_prefix_per_endpoint": Fraction(producer["covered"], 1<<512),
                  "publication_per_endpoint_upper": Fraction(2, scale),
                  "selected_physical_radius_upper": physical_radius}
        result.append({"quantity": quantity_document(key), "source_checkpoint": [producer["lower"], producer["upper"]],
            "analytic_checkpoint": [consumer["lower"], consumer["upper"]],
            "publication": [encode_rational(public_lo, 8192), encode_rational(public_hi, 8192)],
            "physical_output_mass": encode_rational(mass, 8192),
            "head_expansion_checkpoint": [encode_rational(x, 8192) for x in expansion],
            "endpoint_payment": {name: encode_rational(value, 8192) for name, value in ledger.items()},
            "scope": "SELECTION_ONLY"})
    return result


@contextmanager
def _slice_writer(output, *, resume):
    """Own shared context, both collections and acceptance until final publication."""
    _root_path(output, missing=True)
    output.mkdir(parents=True, exist_ok=resume)
    path = _safe(output, ".slice.lock", missing=True)
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    with os.fdopen(os.open(path, flags, 0o600), "r+b") as stream:
        _check_lock_file(stream, path)
        try:
            _os_lock(stream, True)
        except OSError as exc:
            raise ContractError("arithmetic slice already owned") from exc
        try:
            _check_lock_file(stream, path)
            yield
        finally:
            _os_lock(stream, False)


def run_slice(problem_path, cases_path, execution_path, output_dir, *, code_root=ROOT,
              resume=False, qualification_stop=None, qualification_role="producer"):
    root, output = Path(code_root).resolve(), Path(output_dir).absolute()
    document, cases, configuration = (_json(_bytes(Path(p))) for p in (problem_path, cases_path, execution_path))
    if cases.get("format") == "whole-source-signed-cases-v1":
        from scripts.whole_source.gram import run_gram_slice
        return run_gram_slice(problem_path, cases_path, execution_path, output_dir, code_root=code_root,
                              resume=resume, qualification_stop=qualification_stop,
                              qualification_role=qualification_role)
    problem = bind_problem(document["parameters"]["profile"], root=root)
    expected = problem.to_dict()
    expected["problem_id"] = problem_id(problem)
    _require(canonical_bytes(document) == canonical_bytes(expected) and problem.profile == "retained-t081",
             "unqualified arithmetic problem binding")
    _require(cases == {"format": "whole-source-arithmetic-cases-v1", "problem_id": problem_id(problem),
             "entries": [list(pair) for pair in selected_pairs(problem)], "node_block": cases.get("node_block"),
             "scope": "SELECTION_ONLY"}, "incorrect complete arithmetic case set")
    _require(configuration.get("format") == "whole-source-arithmetic-execution-v1" and
             configuration.get("scope") == "SELECTION_ONLY" and set(configuration["roles"]) == {"producer", "analytic"},
             "incorrect arithmetic execution format")
    bound = {}
    for role in ("producer", "analytic"):
        row = configuration["roles"][role]
        spec = CollectionSpec.from_dict(problem, row["collection"], code_root=root)
        plan = ExecutionPlan.from_dict(row["execution"])
        _require(spec.role == plan.role == role and plan.scope == "SELECTION_ONLY" and
                 spec.grid_bits == problem.arithmetic.checkpoint_bits and
                 tuple(q.key.entry for q in spec.quantities) == selected_pairs(problem), "incorrect arithmetic role/context")
        expected_axes = (Axis("term", 0, 4), Axis("window", 0, 2))
        if role == "producer":
            expected_axes += (Axis("node", 0, problem.source_gauss_order),)
        _require(all(q.axes == expected_axes and q.scope == "DECLARED_SLICE" for q in spec.quantities),
                 "incomplete arithmetic inner domain")
        _require(role != "producer" or dict(spec.partition)["node"] == cases["node_block"], "changed node partition")
        bound[role] = spec, plan
    context = {"format": "whole-source-arithmetic-slice-context-v1", "problem_id": problem_id(problem),
        "cases_sha256": hashlib.sha256(canonical_bytes(cases)).hexdigest(),
        "execution_sha256": hashlib.sha256(canonical_bytes(configuration)).hexdigest(),
        "scope": "SELECTION_ONLY"}
    with _slice_writer(output, resume=resume):
        return _run_owned_slice(problem, context, bound, output, root, resume,
                                qualification_stop, qualification_role)


def _run_owned_slice(problem, context, bound, output, root, resume,
                     qualification_stop, qualification_role):
    context_path = output/"slice-context.json"
    if resume:
        _require(_json(_bytes(context_path)) == context, "incompatible slice resume context")
    else:
        _write(context_path, canonical_bytes(context))
        (output/"acceptances").mkdir()
    attempt = uuid.uuid4().hex
    _atomic_snapshot(output/"slice-state.json", {"status": "RUNNING", "attempt": attempt, "scope": "SELECTION_ONLY"})
    try:
        roles = {}
        for role in ("producer", "analytic"):
            spec, plan = bound[role]
            child_root = output/role
            roles[role] = _run_role(child_root, spec, plan, code_root=root,
                resume=resume and (child_root/"collection.json").exists(),
                qualification_stop=qualification_stop if qualification_role == role else None)
        _require(roles["producer"]["preparation"] == roles["analytic"]["preparation"],
                 "independent exact preparation differs")
        entries = check_entries(problem, roles["producer"]["entries"], roles["analytic"]["entries"])
        receipts = [receipt for row in roles.values() for receipt in row["owned_receipts"]]
        _require(receipts and all(r["worker_cleanup_verified"] for r in receipts), "owned scientific cleanup missing")
        report = {"format": "whole-source-arithmetic-slice-v1", "status": "VERIFIED_SELECTED_COMPLETE_ARITHMETIC",
            "profile": problem.profile, "problem_id": problem_id(problem), "context": context,
            "entries": entries, "roles": roles, "scope": "SELECTION_ONLY",
            "all_owned_cleanup_verified": True, "full_mathematical_source": False,
            "matrix_positivity": False, "production_admission": False, "full_target_run": False}
        raw = canonical_bytes(report)
        name = "acceptances/"+attempt+".json"
        _write(output/name, raw)
        _atomic_snapshot(output/"slice-state.json", {"status": report["status"], "attempt": attempt,
            "receipt": {"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)},
            "scope": "SELECTION_ONLY", "full_mathematical_source": False})
        return report
    except BaseException as exc:
        _atomic_snapshot(output/"slice-state.json", {"status": "FAILED_NO_SCIENTIFIC_ACCEPTANCE", "attempt": attempt,
            "error": type(exc).__name__+": "+str(exc), "scope": "SELECTION_ONLY", "full_mathematical_source": False})
        raise
