"""Complete selected low/exterior quantities; shared transport, not shared mathematics."""
from __future__ import annotations

from dataclasses import asdict
from fractions import Fraction
import hashlib
import importlib.metadata
from pathlib import Path
from time import perf_counter_ns
import uuid

from scripts.whole_source.contract import (
    ROOT, ArtifactRef, ContractError, ModeRange, QuantityKey, bind_problem,
    canonical_bytes, expected_domain, problem_id, quantity_document,
)
from scripts.whole_source.artifacts import (
    Axis, ChunkStore, CodecBounds, CollectionLock, CollectionSpec, ContributionTask,
    IntervalRecord, QuantitySpec, _decode_chunk, _raw, _task, decode_rational, encode_rational,
)
from scripts.whole_source.execution import (
    MIB, ExecutionPlan, WorkloadExecution, _RUNTIME, _bytes, _json, _write, exact_telemetry,
)
from scripts.whole_source.slice import _atomic_snapshot, _parse_staged, _ref, _request, _slice_writer

FORMAT = "whole-source-signed-cases-v1"
COMPLETE = (Axis("complete", 0, 1),)
FAMILIES = ("V", "VV", "P_squared", "VP", "J_F", "A_model", "P_L",
            "G_exterior", "weighted_complete_tail")


def _require(condition, message):
    if not condition:
        raise ContractError(message)


def selected_pairs(problem):
    return ((0, 0), (1, 1), (0, problem.N-2), (1, problem.N-1),
            (problem.N-2, problem.N-2), (problem.N-1, problem.N-1))


def residual_pairs(problem):
    n, k, m = problem.N, problem.K, problem.M
    return ((0, 0), (2, 0), (k, k), (k+2, k), (k+1, k+1),
            (n, n-k-2), (n, n-k), (n, n-2), (n+1, n-1),
            (n+k-2, n-2), (n+k, n-2), (m-2, n-2))


def entry_keys(m, n):
    keys = [QuantityKey(name, m % 2, entry=(m, n)) for name in FAMILIES]
    if m != n:
        keys.append(QuantityKey("VP", m % 2, entry=(n, m)))
    return tuple(keys)


def selected_keys(problem):
    return tuple(key for m, n in selected_pairs(problem) for key in entry_keys(m, n)) + tuple(
        QuantityKey("R_action", m % 2, entry=(m, n)) for m, n in residual_pairs(problem))


def cases_document(problem):
    return {"format": FORMAT, "problem_id": problem_id(problem),
            "entries": [list(pair) for pair in selected_pairs(problem)],
            "residual_entries": [list(pair) for pair in residual_pairs(problem)],
            "scope": "SELECTION_ONLY", "projection_extent": problem.M,
            "source_gauss_order": problem.source_gauss_order,
            "square_gauss_order": problem.N}


def prepare_gram_inputs(problem, directory, *, origin_git_commit, origin_git_dirty,
                        code_root=ROOT, memory_mib=1536):
    """Bind exact selected complete quantities and role-specific owned programs."""
    root, directory = Path(code_root).resolve(), Path(directory).resolve()
    _require(problem.profile == "retained-t081", "only the retained signed selection is qualified")
    directory.mkdir(parents=True, exist_ok=False)
    document = problem.to_dict()
    document["problem_id"] = problem_id(problem)
    _write(directory/"problem.json", canonical_bytes(document))
    _write(directory/"cases.json", canonical_bytes(cases_document(problem)))
    version = importlib.metadata.version("python-flint")
    roles = {}
    for role, filename in (("producer", "producer.py"), ("analytic", "analytic.py")):
        paths = (*_RUNTIME, "scripts/weil_whole_source_split.py", "scripts/whole_source/slice.py",
                 "scripts/whole_source/gram.py", "scripts/whole_source/"+filename)
        refs = tuple(sorted((_ref(root, path) for path in paths), key=lambda r: r.path))
        origin_path = directory/(role+"-origin.json")
        _write(origin_path, canonical_bytes({"format": "whole-source-code-origin-v1",
            "origin_git_commit": origin_git_commit, "origin_git_dirty": origin_git_dirty,
            "files": [asdict(ref) for ref in refs]}))
        quantities = []
        for parity in (0, 1):
            key = QuantityKey("F_column", parity)
            domain = expected_domain(problem, key)
            quantities.append(QuantitySpec(key, domain.rows, domain.columns, False, COMPLETE))
        for key in selected_keys(problem):
            domain = expected_domain(problem, key)
            quantities.append(QuantitySpec(key, domain.rows, domain.columns, domain.symmetric_upper, COMPLETE))
        bounds = CodecBounds(8*MIB, 8*MIB, 8*MIB, 16384, 8192, 256*1024,
                             64*1024, 512*MIB, 64*MIB, 64*MIB)
        spec = CollectionSpec.create(problem, role=role, quantities=tuple(quantities),
            partition=(("columns", 1), ("complete", 1), ("rows", problem.M//2)),
            backend="python-flint", backend_version=version, native_threads=1,
            code_refs=refs, bounds=bounds, code_root=root)
        plan = ExecutionPlan(problem_id(problem), spec.collection_id, role, 1, 1, 1,
            memory_mib=memory_mib, reserve_mib=128, root_mib=128, worker_base_mib=80,
            worker_private_mib=128, native_workspace_mib=128, conversion_mib=64,
            codec_mib=256, queue_mib=8, supervisor_increment_mib=256,
            repository_mib=384, temporary_mib=64, minimum_free_mib=64,
            max_tasks=128, task_bytes=32768, result_bytes=32768, log_bytes=4*MIB,
            task_program=_ref(root, "scripts/whole_source/"+filename), task_function="evaluate_gram",
            precision_bits=problem.arithmetic.source_bits if role == "producer" else problem.arithmetic.audit_bits,
            backend="python-flint", backend_version=version,
            provenance=_ref(root, origin_path.relative_to(root).as_posix()), scope="SELECTION_ONLY")
        roles[role] = {"collection": spec.to_dict(), "execution": plan.to_dict()}
    _write(directory/"execution.json", canonical_bytes({"format": "whole-source-signed-execution-v1",
                                                       "roles": roles, "scope": "SELECTION_ONLY"}))
    return {name: directory/(name+".json") for name in ("problem", "cases", "execution")}


def column_task(spec, n):
    quantity = spec.quantity(QuantityKey("F_column", n % 2))
    return ContributionTask(quantity.key, quantity.rows, ModeRange(n, min(n+2, spec.problem.N)), COMPLETE)


def value_task(spec, key):
    quantity = spec.quantity(key)
    return ContributionTask(key, quantity.rows, quantity.columns, COMPLETE)


def _read_complete(spec, root, task, ref):
    snapshot = _decode_chunk(spec, _raw(root, ref, spec.bounds.max_compressed_bytes))
    _require(_task(snapshot.header["task"]) == task, "completed expression domain changed")
    _require(all(record.contribution == (0,) for record in snapshot.records),
             "completed expression has partial contributions")
    return snapshot


def load_column(staging, ref, n):
    """Decode only this role's raw-bound complete physical column."""
    from flint import arb, fmpq
    snapshot = _read_complete(staging.spec, staging.root, column_task(staging.spec, n), ref)
    modes = range(n % 2, staging.spec.problem.M, 2)
    _require(len(snapshot.records) == len(modes), "incomplete physical projection column")
    values = []
    for m, record in zip(modes, snapshot.records):
        _require((record.row, record.column) == (m, n), "incorrect projection row/mass mapping")
        lo, hi = record.lower, record.upper
        midpoint, radius = (lo+hi)/2, (hi-lo)/2
        values.append(arb(arb(fmpq(midpoint.numerator, midpoint.denominator)),
                          arb(fmpq(radius.numerator, radius.denominator))))
    return values


def evaluate_owned(task, staging, functions):
    """Neutral role dispatch and closed-chunk staging. Role mathematics stays separate."""
    staging._check()
    problem, spec = staging.spec.problem, staging.spec
    _require(problem.profile == "retained-t081", "unqualified signed profile")
    started = perf_counter_ns()
    operation = task.get("operation")
    values, chunks = {}, []
    if operation == "column":
        n = task.get("n")
        _require(type(n) is int and n in {v for pair in selected_pairs(problem) for v in pair},
                 "unselected complete projection column")
        column = functions["column"](problem, n)
        domain = column_task(spec, n)
        modes = range(n % 2, problem.M, 2)
        _require(len(column) == len(modes), "incomplete computed column")
        records = (_record(m, n, value) for m, value in zip(modes, column))
        chunks.append(_stage(staging, domain, records))
        statistics = {"physical_rows": len(modes), "source_gauss_order": problem.source_gauss_order,
                      "signed_windows": 2*len(problem.active_terms), "column": n}
    elif operation == "gram":
        m, n = task.get("m"), task.get("n")
        _require(type(m) is int and type(n) is int and (m, n) in selected_pairs(problem),
                 "unselected complete low/exterior entry")
        _require(type(task.get("columns")) is list and len(task["columns"]) == len({m, n}),
                 "missing projection column bindings")
        columns = {}
        for item in task["columns"]:
            index = item["n"]
            _require(type(index) is int and index in (m, n) and index not in columns,
                     "duplicate or foreign projection column")
            columns[index] = load_column(staging, ArtifactRef(**item["ref"]), index)
        computed = functions["entry"](problem, m, n, columns)
        _require(set(computed) == {(key.name, *key.entry) for key in entry_keys(m, n)},
                 "incomplete signed family output")
        for key in entry_keys(m, n):
            a, b = key.entry
            chunks.append(_stage(staging, value_task(spec, key), (_record(a, b, computed[(key.name, a, b)]),)))
        statistics = {"projection_rows": problem.M//2, "low_projection_rows": problem.N//2,
                      "head_projection_rows": (problem.M-problem.N)//2,
                      "overlap_cells": 2*len(problem.active_terms)+1,
                      "source_square_nodes_per_cell": problem.N, "both_vp_orientations": True}
    elif operation == "residual":
        m, n = task.get("m"), task.get("n")
        _require(type(m) is int and type(n) is int and (m, n) in residual_pairs(problem),
                 "unselected residual entry")
        key = QuantityKey("R_action", m % 2, entry=(m, n))
        chunks.append(_stage(staging, value_task(spec, key),
                             (_record(m, n, functions["residual"](problem, m, n)),)))
        statistics = {"kernel_terms": problem.K+1, "input_mode": n, "output_mode": m}
    else:
        raise ContractError("unknown complete signed operation")
    return {"chunks": chunks, "statistics": {**statistics, "wall_ns": perf_counter_ns()-started},
            "scope": "SELECTION_ONLY"}


def _record(m, n, value):
    from flint import arb
    value = arb(value)
    _require(value.is_finite(), "nonfinite complete signed value")
    def fraction(x):
        q = x.fmpq()
        return Fraction(int(q.numerator), int(q.denominator))
    return IntervalRecord(m, n, (0,), fraction(value.lower()), fraction(value.upper()))


def _stage(staging, task, records):
    value = staging.stage_chunk(task, records)
    return {"task": task.to_dict(), "path": str(value.path), "ref": asdict(value.ref),
            "generation": value.generation, "attempt_id": value.attempt_id}


def _find(store, task):
    return next((ref for other, ref in store._chunk_events() if other == task), None)


def _run_role(root, spec, plan, *, code_root, resume):
    with CollectionLock.acquire(root, spec, resume=resume) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=code_root) as execution:
            store = ChunkStore(lock, spec, attempt_id=execution.attempt_id)
            modes = sorted({n for pair in selected_pairs(spec.problem) for n in pair})
            requests = [_request(operation="column", n=n) for n in modes
                        if spec.role == "analytic" or _find(store, column_task(spec, n)) is None]
            statistics = []
            def stage(name, tasks):
                if not tasks:
                    return
                execution.run_stage(name, tasks)
                for result in execution.read_results(name):
                    _require(result["scope"] == result["result"]["scope"] == "SELECTION_ONLY",
                             "changed signed scientific scope")
                    for value in result["result"]["chunks"]:
                        task, staged = _parse_staged(value)
                        store.publish_chunk(task, staged)
                    statistics.append(result["result"]["statistics"])
            stage("columns", requests)
            columns = {n: _find(store, column_task(spec, n)) for n in modes}
            _require(all(columns.values()), "missing complete projection columns")
            requests = [_request(operation="gram", m=m, n=n,
                columns=[{"n": i, "ref": asdict(columns[i])} for i in sorted({m, n})])
                for m, n in selected_pairs(spec.problem)
                if spec.role == "analytic" or any(_find(store, value_task(spec, key)) is None
                                                   for key in entry_keys(m, n))]
            stage("gram", requests)
            stage("residual", [_request(operation="residual", m=m, n=n)
                for m, n in residual_pairs(spec.problem)
                if spec.role == "analytic" or _find(store, value_task(spec,
                    QuantityKey("R_action", m % 2, entry=(m, n)))) is None])
            rows = []
            for key in selected_keys(spec.problem):
                task = value_task(spec, key)
                ref = _find(store, task)
                _require(ref is not None, "missing completed signed quantity")
                snapshot = _read_complete(spec, root, task, ref)
                _require(len(snapshot.records) == 1, "incomplete selected scalar quantity")
                record = snapshot.records[0]
                rows.append({"quantity": quantity_document(key), "lower": encode_rational(record.lower, 8192),
                             "upper": encode_rational(record.upper, 8192), "chunk": asdict(ref)})
            return {"role": spec.role, "collection_id": spec.collection_id,
                    "attempt_id": execution.attempt_id, "entries": rows,
                    "column_chunks": [{"n": n, "ref": asdict(columns[n])} for n in modes],
                    "statistics": statistics, "owned_receipts": exact_telemetry(execution.receipts),
                    "scope": "SELECTION_ONLY"}


def check_entries(problem, source, analytic):
    keys = selected_keys(problem)
    _require(len(source) == len(analytic) == len(keys), "incomplete selected signed comparison")
    result = []
    for key, producer, consumer in zip(keys, source, analytic):
        _require(producer["quantity"] == consumer["quantity"] == quantity_document(key),
                 "incorrect signed physical quantity")
        lo, hi = (decode_rational(producer[k], 8192) for k in ("lower", "upper"))
        alo, ahi = (decode_rational(consumer[k], 8192) for k in ("lower", "upper"))
        scale = 1 << problem.arithmetic.publication_bits
        public_lo, public_hi = Fraction((lo*scale).__floor__()-1, scale), Fraction((hi*scale).__ceil__()+1, scale)
        _require(public_lo <= lo <= hi <= public_hi and public_lo <= alo <= ahi <= public_hi,
                 "independent complete signed containment failed: "+str((key.name, key.entry)))
        m, n = key.entry
        radius = (public_hi-public_lo)/2*max(Fraction(2*m+1, 2), Fraction(2*n+1, 2))
        _require(radius < problem.numerical_goal, "selected signed physical width goal failed")
        result.append({"quantity": quantity_document(key),
                       "publication": [encode_rational(public_lo, 8192), encode_rational(public_hi, 8192)],
                       "physical_radius_upper": encode_rational(radius, 8192),
                       "analytic_checkpoint": [consumer["lower"], consumer["upper"]],
                       "scope": "SELECTION_ONLY"})
    return result


def check_columns(problem, bound, output, roles):
    """Check every completed dependency column before releasing derived values."""
    scale = 1 << problem.arithmetic.publication_bits
    count, maximum = 0, Fraction(0)
    expected = sorted({n for pair in selected_pairs(problem) for n in pair})
    for role in ("producer", "analytic"):
        _require([row["n"] for row in roles[role]["column_chunks"]] == expected,
                 "incomplete role projection-column inventory")
    for source, independent in zip(roles["producer"]["column_chunks"], roles["analytic"]["column_chunks"]):
        n = source["n"]
        snapshots = []
        for role, row in (("producer", source), ("analytic", independent)):
            spec = bound[role][0]
            snapshots.append(_read_complete(spec, output/role, column_task(spec, n), ArtifactRef(**row["ref"])))
        _require(len(snapshots[0].records) == len(snapshots[1].records) == problem.M//2,
                 "incomplete physical column comparison")
        for m, producer, consumer in zip(range(n % 2, problem.M, 2),
                                         snapshots[0].records, snapshots[1].records):
            _require((producer.row, producer.column) == (consumer.row, consumer.column) == (m, n),
                     "physical column coordinates differ")
            lo = Fraction((producer.lower*scale).__floor__()-1, scale)
            hi = Fraction((producer.upper*scale).__ceil__()+1, scale)
            _require(lo <= consumer.lower <= consumer.upper <= hi,
                     "independent full projection-column containment failed")
            radius = (hi-lo)/2*max(Fraction(2*m+1, 2), Fraction(2*n+1, 2))
            _require(radius < problem.numerical_goal, "projection-column physical width goal failed")
            maximum = max(maximum, radius)
            count += 1
    return {"entries": count, "physical_extent": problem.M,
            "maximum_physical_radius_upper": encode_rational(maximum, 8192),
            "both_low_and_head": True, "scope": "SELECTION_ONLY"}


def run_gram_slice(problem_path, cases_path, execution_path, output_dir, *, code_root=ROOT,
                   resume=False, qualification_stop=None, qualification_role="producer"):
    _require(qualification_stop is None, "signed selection has no interruption qualification mode")
    root, output = Path(code_root).resolve(), Path(output_dir).absolute()
    document, cases, config = (_json(_bytes(Path(p))) for p in (problem_path, cases_path, execution_path))
    problem = bind_problem(document["parameters"]["profile"], root=root)
    expected = problem.to_dict()
    expected["problem_id"] = problem_id(problem)
    _require(problem.profile == "retained-t081" and canonical_bytes(document) == canonical_bytes(expected),
             "unqualified signed problem binding")
    _require(canonical_bytes(cases) == canonical_bytes(cases_document(problem)), "changed signed selection")
    _require(set(config) == {"format", "roles", "scope"} and
             config["format"] == "whole-source-signed-execution-v1" and config["scope"] == "SELECTION_ONLY" and
             set(config["roles"]) == {"producer", "analytic"}, "invalid signed execution format")
    bound = {}
    for role in ("producer", "analytic"):
        spec = CollectionSpec.from_dict(problem, config["roles"][role]["collection"], code_root=root)
        plan = ExecutionPlan.from_dict(config["roles"][role]["execution"])
        expected_keys = (QuantityKey("F_column", 0), QuantityKey("F_column", 1), *selected_keys(problem))
        _require(spec.role == plan.role == role and plan.task_function == "evaluate_gram" and
                 plan.task_program.path == "scripts/whole_source/"+role+".py" and
                 tuple(q.key for q in spec.quantities) == expected_keys and
                 all(q.axes == COMPLETE and q.scope == "DECLARED_SLICE" and
                     (q.rows, q.columns, q.symmetric_upper) == (
                         expected_domain(problem, q.key).rows, expected_domain(problem, q.key).columns,
                         expected_domain(problem, q.key).symmetric_upper) for q in spec.quantities) and
                 spec.grid_bits == problem.arithmetic.checkpoint_bits and plan.scope == "SELECTION_ONLY",
                 "changed signed role/domain policy")
        bound[role] = spec, plan
    context = {"format": "whole-source-signed-context-v1", "problem_id": problem_id(problem),
               "cases_sha256": hashlib.sha256(canonical_bytes(cases)).hexdigest(),
               "execution_sha256": hashlib.sha256(canonical_bytes(config)).hexdigest(), "scope": "SELECTION_ONLY"}
    with _slice_writer(output, resume=resume):
        context_path = output/"slice-context.json"
        if resume:
            _require(_json(_bytes(context_path)) == context, "incompatible signed resume context")
        else:
            _write(context_path, canonical_bytes(context))
            (output/"acceptances").mkdir()
        attempt = uuid.uuid4().hex
        _atomic_snapshot(output/"slice-state.json", {"status": "RUNNING", "attempt": attempt})
        try:
            roles = {}
            for role in ("producer", "analytic"):
                spec, plan = bound[role]
                child = output/role
                roles[role] = _run_role(child, spec, plan, code_root=root,
                                        resume=resume and (child/"collection.json").exists())
            entries = check_entries(problem, roles["producer"]["entries"], roles["analytic"]["entries"])
            column_check = check_columns(problem, bound, output, roles)
            receipts = [r for value in roles.values() for r in value["owned_receipts"]]
            _require(receipts and all(r["worker_cleanup_verified"] for r in receipts), "signed owned cleanup missing")
            report = {"format": "whole-source-signed-slice-v1", "status": "VERIFIED_SELECTED_COMPLETE_SIGNED_QUANTITIES",
                      "profile": problem.profile, "problem_id": problem_id(problem), "context": context,
                      "entries": entries, "roles": roles, "scope": "SELECTION_ONLY",
                      "independent_columns": column_check,
                      "projection_extent": problem.M, "model_error_upper": encode_rational(problem.model_error, 8192),
                      "full_mathematical_source": False, "matrix_positivity": False, "production_admission": False,
                      "full_target_run": False, "all_owned_cleanup_verified": True}
            name = "acceptances/"+attempt+".json"
            raw = canonical_bytes(report)
            _write(output/name, raw)
            _atomic_snapshot(output/"slice-state.json", {"status": report["status"], "attempt": attempt,
                "receipt": {"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)},
                "scope": "SELECTION_ONLY"})
            return report
        except BaseException as exc:
            _atomic_snapshot(output/"slice-state.json", {"status": "FAILED_NO_SCIENTIFIC_ACCEPTANCE", "attempt": attempt,
                "error": type(exc).__name__+": "+str(exc), "scope": "SELECTION_ONLY"})
            raise
