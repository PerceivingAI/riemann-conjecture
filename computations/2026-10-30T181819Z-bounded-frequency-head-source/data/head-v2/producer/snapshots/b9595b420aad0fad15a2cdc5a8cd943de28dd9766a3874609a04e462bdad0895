"""Complete source publication and independent streamed analytical containment."""
from __future__ import annotations

from dataclasses import asdict
from fractions import Fraction
import hashlib
import importlib.metadata
from pathlib import Path
from types import SimpleNamespace

from scripts.whole_source.contract import (
    ROOT, ArtifactRef, ContractError, ModeRange, QuantityKey, bind_problem,
    canonical_bytes, problem_id,
)
from scripts.whole_source.artifacts import (
    Axis, CodecBounds, CollectionLock, CollectionSpec, ContributionTask, ChunkStore,
    IntervalRecord, QuantitySpec, _coordinates, _decode_chunk, _raw, _round, _safe,
    _task, decode_publication, publish_publication, stage_publication,
)
from scripts.whole_source.execution import (
    MIB, ExecutionPlan, WorkloadExecution, _RUNTIME, _bytes, _json, _write, exact_telemetry,
)
from scripts.whole_source.slice import _parse_staged, _ref, _request, _slice_writer
from scripts.whole_source.gram import _find, _record, _stage

COMPLETE = (Axis("complete", 0, 1),)
FAMILIES = {"A_model": "A_model", "weighted_head": "head_complete",
            "weighted_complete_tail": "tail_complete"}


def _require(value, message):
    if not value:
        raise ContractError(message)


def math_problem(problem, control=False):
    """The reduced algebra is explicitly non-admissible, never another RH profile."""
    _require(type(control) is bool, "explicit control policy required")
    if not control:
        return problem
    values = {name: getattr(problem, name) for name in problem.__dataclass_fields__
              if not name.startswith("_")}
    values.update(N=6, M=12, K=2, source_gauss_order=9,
                  kernel_coefficients=problem.kernel_coefficients[:3])
    return SimpleNamespace(**values)


def _quantities(problem, control):
    model = math_problem(problem, control)
    result = []
    for p in (0, 1):
        low = ModeRange(p, model.N+p if control else model.N)
        head = ModeRange(model.N+p, model.M+p if control else model.M)
        for name in ("F_column", "head_column", "head_image", "kernel_complete",
                     "A_model", "head_complete", "tail_complete"):
            rows = ModeRange(p, model.M+p if control else model.M) if name == "F_column" else (
                head if name in ("head_column", "head_image", "kernel_complete") else low)
            columns = head if name.startswith("kernel_") else low
            symmetric = name not in ("F_column", "head_column", "head_image")
            axes = COMPLETE
            scope = "FULL_QUANTITY" if not control and name in FAMILIES.values() else "DECLARED_SLICE"
            result.append(QuantitySpec(QuantityKey(name, p), rows, columns, symmetric, axes, scope))
    return tuple(result)


def _partition(problem, control, tile_modes):
    model = math_problem(problem, control)
    values = {"anchor_prefix": 1, "columns": tile_modes, "complete": 1, "rows": tile_modes,
              "F_column.rows": model.M//2, "F_column.columns": 1}
    for name in ("head_column", "head_image"):
        values[name+".rows"] = (model.M-model.N)//2
        values[name+".columns"] = 1
    return tuple(sorted(values.items()))


def prepare_source_inputs(problem, directory, *, origin_git_commit, origin_git_dirty,
                          code_root=ROOT, control=False, tile_modes=16, memory_mib=1536):
    """Bind role-isolated code and explicit storage/working-set allowances; run nothing."""
    _require(problem.profile == "retained-t081", "full target execution is not qualified")
    _require(type(tile_modes) is int and 1 <= tile_modes <= 32, "invalid bounded tile size")
    _require(control or tile_modes in (16, 32), "full-source tile geometry exceeds fixed transport limits")
    root, directory = Path(code_root).resolve(), Path(directory).resolve()
    directory.relative_to(root)
    directory.mkdir(parents=True, exist_ok=False)
    document = problem.to_dict()
    document["problem_id"] = problem_id(problem)
    _write(directory/"problem.json", canonical_bytes(document))
    roles = {}
    for role in ("producer", "analytic"):
        paths = (*_RUNTIME, "scripts/whole_source/slice.py", "scripts/whole_source/gram.py",
                 "scripts/whole_source/pipeline.py", "scripts/weil_whole_source_split.py",
                 "scripts/whole_source/"+role+".py")
        refs = tuple(sorted((_ref(root, p) for p in paths), key=lambda r: r.path))
        origin = directory/(role+"-origin.json")
        _write(origin, canonical_bytes({"format": "whole-source-code-origin-v1",
            "origin_git_commit": origin_git_commit, "origin_git_dirty": origin_git_dirty,
            "files": [asdict(r) for r in refs]}))
        bounds = CodecBounds(8*MIB, 8*MIB, 8*MIB, 16384, 8192, 256*1024,
                             64*1024, 8*1024*MIB, 128*MIB, 64*MIB)
        spec = CollectionSpec.create(problem, role=role, quantities=_quantities(problem, control),
            partition=_partition(problem, control, tile_modes),
            backend="python-flint", backend_version=importlib.metadata.version("python-flint"),
            native_threads=1, code_refs=refs, bounds=bounds, code_root=root)
        plan = ExecutionPlan(problem_id(problem), spec.collection_id, role, 1, 1, 1,
            memory_mib=memory_mib, reserve_mib=128, root_mib=128, worker_base_mib=80,
            worker_private_mib=128, native_workspace_mib=128, conversion_mib=64,
            codec_mib=256, queue_mib=8, supervisor_increment_mib=256,
            repository_mib=8192, temporary_mib=128, minimum_free_mib=64,
            max_tasks=4096, task_bytes=128*1024, result_bytes=MIB, log_bytes=4*MIB,
            task_program=_ref(root, "scripts/whole_source/"+role+".py"), task_function="evaluate_source",
            precision_bits=problem.arithmetic.source_bits if role == "producer" else problem.arithmetic.audit_bits,
            backend="python-flint", backend_version=spec.backend_version,
            provenance=_ref(root, origin.relative_to(root).as_posix()), scope="SOURCE_EXPRESSIONS_ONLY")
        roles[role] = {"collection": spec.to_dict(), "execution": plan.to_dict()}
    config = {"format": "whole-source-pipeline-execution-v1", "control": control,
              "tile_modes": tile_modes, "roles": roles}
    _write(directory/"execution.json", canonical_bytes(config))
    return {name: directory/(name+".json") for name in ("problem", "execution")}


def _bind(problem_path, execution_path, root):
    document, config = (_json(_bytes(Path(p))) for p in (problem_path, execution_path))
    problem = bind_problem(document["parameters"]["profile"], root=root)
    expected = problem.to_dict()
    expected["problem_id"] = problem_id(problem)
    _require(canonical_bytes(document) == canonical_bytes(expected) and problem.profile == "retained-t081",
             "changed or unqualified pipeline problem")
    _require(set(config) == {"format", "control", "tile_modes", "roles"} and
             config["format"] == "whole-source-pipeline-execution-v1" and
             type(config["control"]) is bool and type(config["tile_modes"]) is int and
             1 <= config["tile_modes"] <= 32 and set(config["roles"]) == {"producer", "analytic"},
             "invalid pipeline execution policy")
    _require(config["control"] or config["tile_modes"] in (16, 32),
             "full-source tile geometry exceeds fixed transport limits")
    bound = {}
    for role in ("producer", "analytic"):
        spec = CollectionSpec.from_dict(problem, config["roles"][role]["collection"], code_root=root)
        plan = ExecutionPlan.from_dict(config["roles"][role]["execution"])
        _require(spec.role == plan.role == role and
                 spec.quantities == _quantities(problem, config["control"]) and
                 spec.partition == _partition(problem, config["control"], config["tile_modes"]) and
                 spec.grid_bits == problem.arithmetic.checkpoint_bits and
                 plan.task_program.path == "scripts/whole_source/"+role+".py" and
                 plan.task_function == "evaluate_source" and plan.scope == "SOURCE_EXPRESSIONS_ONLY",
                 "changed source role/domain/grid/function policy")
        bound[role] = spec, plan
    return problem, config, bound


def _tiles(spec, key):
    q = spec.quantity(key)
    width = dict(spec.partition)["rows"]*2
    for row in range(q.rows.start, q.rows.stop, width):
        for column in range(q.columns.start, q.columns.stop, width):
            if q.symmetric_upper and column < row:
                continue
            yield ContributionTask(key, ModeRange(row, min(row+width, q.rows.stop)),
                ModeRange(column, min(column+width, q.columns.stop)), COMPLETE)


def _column_task(spec, name, n):
    q = spec.quantity(QuantityKey(name, n % 2))
    return ContributionTask(q.key, q.rows, ModeRange(n, min(n+2, q.columns.stop)), COMPLETE)


def _native(value):
    from flint import arb, fmpq
    lo, hi = value.lower, value.upper
    mid, rad = (lo+hi)/2, (hi-lo)/2
    return arb(arb(fmpq(mid.numerator, mid.denominator)), arb(fmpq(rad.numerator, rad.denominator)))


def _fixed_bounds(value, bits):
    """Outward fixed-point bounds without allocating full-precision Fractions."""
    _require(value.is_finite(), "nonfinite native cache expression")
    result = []
    for endpoint, upper in ((value.lower(), False), (value.upper(), True)):
        mantissa, exponent = endpoint.man_exp()
        mantissa, shift = int(mantissa), int(exponent)+bits
        _require(mantissa.bit_length()+max(shift, 0) <= bits+32 or shift < 0,
                 "kernel checkpoint magnitude exceeds compact representation")
        if shift >= 0:
            scaled = mantissa << shift
        else:
            scaled = -((-mantissa) >> -shift) if upper else mantissa >> -shift
        result.append(scaled+1 if upper else scaled-1)
    return tuple(result)


def _cache_record(m, n, value, contribution=(0,)):
    lo, hi = _fixed_bounds(value, 512)
    return IntervalRecord(m, n, contribution, Fraction(lo, 1 << 512), Fraction(hi, 1 << 512))


def _read(spec, root, task, ref):
    data = _decode_chunk(spec, _raw(root, ref, spec.bounds.max_compressed_bytes))
    _require(_task(data.header["task"]) == task, "foreign cache dependency domain")
    return data.records


def _column(staging, name, n, ref):
    task = _column_task(staging.spec, name, n)
    return [_native(r) for r in _read(staging.spec, staging.root, task, ArtifactRef(**ref))]


def _wire(staged):
    return {"task": staged.task.to_dict(), "path": str(staged.path), "ref": asdict(staged.ref),
            "generation": staged.generation, "attempt_id": staged.attempt_id}


def _discard(staging, staged):
    staging._check()
    _require(staged.generation == staging.generation and staged.attempt_id == staging.attempt_id and
             staged.ref.path.startswith("attempts/"+staging.attempt_id+"/staging/"), "foreign scratch")
    _raw(staging.root, staged.ref, staging.spec.bounds.max_compressed_bytes)
    _safe(staging.root, staged.ref.path).unlink()


def _kernel(staging, model, p, functions):
    """One bounded compact integer cache; never a full high-precision native K."""
    import sys
    from scripts.whole_source import execution
    spec = staging.spec
    h = (model.M-model.N)//2
    count = h*(h+1)//2
    integer_bits = spec.grid_bits+32
    integer_bytes = sys.getsizeof((1 << integer_bits)-1)
    account = 2*count*(integer_bytes+16)+2*sys.getsizeof([])
    worker = execution._WORKER
    allowance = worker[0].worker_private_mib*MIB if worker is not None else 128*MIB
    _require(account <= allowance, "compact kernel exceeds declared private allowance")
    lower, upper = [0]*count, [0]*count
    modes = range(model.N+p, model.M, 2)
    for anchor in range(len(model.frequency_edges)):
        contribution = functions["frequency_step"](model, anchor)
        index = 0
        for i, m in enumerate(modes):
            for n in range(m, model.M, 2):
                lo, hi = _fixed_bounds(contribution(m, n), spec.grid_bits)
                # Exact fixed-grid prefix arithmetic; pay one additional unit per term.
                lo, hi = lower[index]+lo-1, upper[index]+hi+1
                _require(max(abs(lo).bit_length(), abs(hi).bit_length()) <= integer_bits,
                         "compact kernel prefix exceeds admitted bit bound")
                lower[index], upper[index] = lo, hi
                index += 1
        _require(index == count, "incomplete kernel anchor domain")
    chunks = []
    for task in _tiles(spec, QuantityKey("kernel_complete", p)):
        def records():
            for m, n in _coordinates(task, True):
                i, j = (m-model.N-p)//2, (n-model.N-p)//2
                index = i*h-i*(i-1)//2+j-i
                yield IntervalRecord(m, n, (0,), Fraction(lower[index], 1 << spec.grid_bits),
                                     Fraction(upper[index], 1 << spec.grid_bits))
        chunks.append(_stage(staging, task, records()))
    return chunks


def evaluate_owned(task, staging, functions):
    """Transport only; every mathematical operation is supplied by its own role."""
    staging._check()
    spec = staging.spec
    control = task.get("control")
    _require(type(control) is bool and
             spec.quantities == _quantities(spec.problem, control), "changed worker geometry")
    model = math_problem(spec.problem, control)
    operation, p = task.get("operation"), task.get("parity")
    _require(type(p) is int and p in (0, 1), "invalid source parity")
    chunks, publications = [], []
    if operation == "kernel":
        chunks = _kernel(staging, model, p, functions)
    elif operation == "column":
        n = task["n"]
        _require(type(n) is int and n in range(p, model.N, 2), "foreign input column")
        values = functions["column"](model, n)
        _require(len(values) == model.M//2, "incomplete F column")
        chunks.append(_stage(staging, _column_task(spec, "F_column", n),
                             (_cache_record(m, n, value) for m, value in zip(range(p, model.M, 2), values))))
    elif operation == "head":
        n = task["n"]
        _require(type(n) is int and n in range(p, model.N, 2), "foreign head column")
        column = functions["head_column"](model, n, _column(staging, "F_column", n, task["F"]))
        expected = list(_tiles(spec, QuantityKey("kernel_complete", p)))
        _require(len(task["kernel"]) == len(expected), "incomplete head kernel tile inventory")
        def kernel_tiles():
            for domain, ref in zip(expected, task["kernel"]):
                yield ((r.row, r.column, _native(r)) for r in
                       _read(spec, staging.root, domain, ArtifactRef(**ref)))
        image = functions["head_image"](model, column, kernel_tiles())
        _require(len(column) == len(image) == (model.M-model.N)//2, "incomplete coupled head image")
        for name, values in (("head_column", column), ("head_image", image)):
            chunks.append(_stage(staging, _column_task(spec, name, n),
                (_cache_record(m, n, value) for m, value in zip(range(model.N+p, model.M, 2), values))))
    elif operation == "final":
        domain = _task(task["domain"])
        expected = list(_tiles(spec, QuantityKey("A_model", p)))
        _require(domain in expected, "foreign final output tile")
        modes = sorted(set(domain.rows) | set(domain.columns))
        _require([r["n"] for r in task["columns"]] == modes, "incomplete final panel dependencies")
        columns, head, images = {}, {}, {}
        for row in task["columns"]:
            n = row["n"]
            columns[n] = _column(staging, "F_column", n, row["F"])
            head[n] = _column(staging, "head_column", n, row["C"])
            images[n] = _column(staging, "head_image", n, row["Y"])
        outputs = {name: [] for name in FAMILIES}
        for m, n in _coordinates(domain, True):
            values = functions["entry"](model, m, n, columns)
            outputs["A_model"].append(_record(m, n, values[("A_model", m, n)]))
            outputs["weighted_complete_tail"].append(_record(m, n, values[("weighted_complete_tail", m, n)]))
            outputs["weighted_head"].append(_record(m, n, functions["head_pair"](model, head[m], images[n])))
        for canonical, name in FAMILIES.items():
            target = ContributionTask(QuantityKey(name, p), domain.rows, domain.columns, COMPLETE)
            publications.append(_wire(stage_publication(staging, target, outputs[canonical])))
    else:
        raise ContractError("unknown source operation")
    from scripts.whole_source.execution import _WORKER
    return {"chunks": chunks, "publications": publications, "scope": _WORKER[0].scope,
            "statistics": {"operation": operation, "parity": p, "control": control,
                "frequency_anchors": len(model.frequency_edges) if operation == "kernel" else 0,
                "terminal_full_mass": True, "complete_head_axes": (model.M-model.N)//2}}


def _admit_transport(output, spec, plan, control):
    """Price complete inventories before starting a numerical stage."""
    model = math_problem(spec.problem, control)
    dummy_ref = {"path": "chunks/"+("f"*64)+".json", "sha256": "f"*64,
                 "size": spec.bounds.max_compressed_bytes}
    relative = "attempts/"+("f"*32)+"/staging/"+("f"*32)
    for p in (0, 1):
        kernels = list(_tiles(spec, QuantityKey("kernel_complete", p)))
        finals = list(_tiles(spec, QuantityKey("A_model", p)))
        _require(max(model.N//2, len(finals)) <= plan.max_tasks, "source stage task count exceeds transport")
        request = _request(operation="head", parity=p, control=control, n=model.N-2+p,
                           F=dummy_ref, kernel=[dummy_ref]*len(kernels))
        _require(len(canonical_bytes(request))+1024 <= plan.task_bytes, "kernel inventory exceeds task transport")
        descriptors = [{"task": t.to_dict(), "path": str(output/relative),
                        "ref": {"path": relative, "sha256": "f"*64, "size": spec.bounds.max_compressed_bytes},
                        "generation": "f"*64, "attempt_id": "f"*32} for t in kernels]
        result = {"chunks": descriptors, "publications": [], "scope": "SELECTION_ONLY"}
        _require(len(canonical_bytes(result))+4096 <= plan.result_bytes,
                 "kernel inventory exceeds result transport")
        widest = max(finals, key=lambda t: len(set(t.rows) | set(t.columns)))
        modes = sorted(set(widest.rows) | set(widest.columns))
        request = _request(operation="final", parity=p, control=control, domain=widest.to_dict(),
                           columns=[{"n": n, "F": dummy_ref, "C": dummy_ref, "Y": dummy_ref} for n in modes])
        _require(len(canonical_bytes(request))+1024 <= plan.task_bytes, "final panel exceeds task transport")


def _run_role(output, spec, plan, control, *, code_root, resume=False):
    _admit_transport(output, spec, plan, control)
    with CollectionLock.acquire(output, spec, resume=resume) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=code_root) as execution:
            store = ChunkStore(lock, spec, attempt_id=execution.attempt_id)
            cached = {canonical_bytes(t.to_dict()): r for t, r in store._chunk_events()}
            index_path = output/"publication-index.json"
            published = _json(_bytes(index_path)) if index_path.exists() else {}
            statistics = []
            def find(task):
                return cached.get(canonical_bytes(task.to_dict()))
            def stage(name, requests):
                requests = list(requests)
                if not requests:
                    return
                execution.run_stage(name, requests)
                for result in execution.read_results(name):
                    data = result["result"]
                    _require(data["scope"] == plan.scope, "changed source worker scope")
                    for row in data["chunks"]:
                        task, value = _parse_staged(row)
                        cached[canonical_bytes(task.to_dict())] = store.publish_chunk(task, value)
                        _discard(store.staging_context(), value)
                    for row in data["publications"]:
                        task, value = _parse_staged(row)
                        ref = publish_publication(store, task, value)
                        key = canonical_bytes(task.to_dict()).hex()
                        if key in published:
                            _require(published[key] == asdict(ref), "conflicting published retry")
                        published[key] = asdict(ref)
                    statistics.append(data["statistics"])
                from scripts.whole_source.slice import _atomic_snapshot
                _atomic_snapshot(index_path, published)
            model = math_problem(spec.problem, control)
            for p in (0, 1):
                kernels = list(_tiles(spec, QuantityKey("kernel_complete", p)))
                if spec.role == "analytic" or any(find(t) is None for t in kernels):
                    stage("kernel-"+str(p), [_request(operation="kernel", parity=p, control=control)])
                refs = [asdict(find(t)) for t in kernels]
                stage("columns-"+str(p), (_request(operation="column", parity=p, control=control, n=n)
                    for n in range(p, model.N, 2) if spec.role == "analytic" or
                    find(_column_task(spec, "F_column", n)) is None))
                stage("head-"+str(p), (_request(operation="head", parity=p, control=control, n=n,
                    F=asdict(find(_column_task(spec, "F_column", n))), kernel=refs)
                    for n in range(p, model.N, 2) if spec.role == "analytic" or
                    any(find(_column_task(spec, name, n)) is None for name in ("head_column", "head_image"))))
                requests = []
                for domain in _tiles(spec, QuantityKey("A_model", p)):
                    final_tasks = [ContributionTask(QuantityKey(name, p), domain.rows, domain.columns, COMPLETE)
                                   for name in FAMILIES.values()]
                    if spec.role == "producer" and all(canonical_bytes(t.to_dict()).hex() in published for t in final_tasks):
                        continue
                    modes = sorted(set(domain.rows) | set(domain.columns))
                    dependencies = [{"n": n, **{label: asdict(find(_column_task(spec, name, n)))
                        for label, name in (("F", "F_column"), ("C", "head_column"), ("Y", "head_image"))}}
                        for n in modes]
                    requests.append(_request(operation="final", parity=p, control=control,
                                             domain=domain.to_dict(), columns=dependencies))
                stage("final-"+str(p), requests)
            tiles = []
            for canonical, name in FAMILIES.items():
                for p in (0, 1):
                    for task in _tiles(spec, QuantityKey(name, p)):
                        ref = ArtifactRef(**published[canonical_bytes(task.to_dict()).hex()])
                        bits = spec.problem.arithmetic.publication_bits if spec.role == "producer" else spec.grid_bits
                        decode_publication(spec, _raw(output, ref, spec.bounds.max_raw_bytes), task, bits)
                        tiles.append({"family": canonical, "parity": p, "task": task.to_dict(), "artifact": asdict(ref)})
            report = {"format": "whole-source-scientific-manifest-v1", "problem_id": problem_id(spec.problem),
                "collection": spec.to_dict(), "control": control,
                "geometry": {"N": model.N, "M": model.M, "K": model.K},
                "role": spec.role, "publication_bits": 256 if spec.role == "producer" else spec.grid_bits,
                "scope": "CONTROL_ONLY_REDUCED_MODEL" if control else "FULL_DECLARED_SOURCE",
                "tiles": tiles, "full_mathematical_source": not control,
                "analytical_acceptance": False, "matrix_positivity": False, "production_admission": False,
                "residual_model_payment": "Lambda D once in later exact full-space proof"}
            path = output/"source-manifest.json"
            raw = canonical_bytes(report)
            if path.exists():
                _require(_bytes(path) == raw, "changed completed scientific manifest")
            else:
                _write(path, raw)
            from scripts.whole_source.slice import _atomic_snapshot
            _atomic_snapshot(output/("run-"+execution.attempt_id+".json"), {
                "status": "COMPLETE_SOURCE_EXPRESSIONS", "manifest_sha256": hashlib.sha256(raw).hexdigest(),
                "statistics": statistics, "owned_receipts": exact_telemetry(execution.receipts)})
            return report


class SourceReader:
    """Bound one immutable scientific byte image and its exact ordered domain cover."""
    def __init__(self, path, spec, *, control):
        self.path, self.spec = Path(path).resolve(), spec
        raw = _bytes(self.path)
        self.ref = ArtifactRef(self.path.name, hashlib.sha256(raw).hexdigest(), len(raw))
        self.document = _json(raw)
        value = self.document
        model = math_problem(spec.problem, control)
        bits = spec.problem.arithmetic.publication_bits if spec.role == "producer" else spec.grid_bits
        _require(type(value) is dict and set(value) == {
            "format", "problem_id", "collection", "control", "geometry", "role", "publication_bits",
            "scope", "tiles", "full_mathematical_source", "analytical_acceptance", "matrix_positivity",
            "production_admission", "residual_model_payment"} and
            value["residual_model_payment"] == "Lambda D once in later exact full-space proof",
            "invalid closed scientific manifest")
        _require(value["format"] == "whole-source-scientific-manifest-v1" and
                 canonical_bytes(value["collection"]) == canonical_bytes(spec.to_dict()) and value["problem_id"] == problem_id(spec.problem) and
                 value["control"] is control and value["role"] == spec.role and
                 canonical_bytes(value["geometry"]) == canonical_bytes({"N": model.N, "M": model.M, "K": model.K}) and
                 value["publication_bits"] == bits and value["full_mathematical_source"] is (not control) and
                 value["scope"] == ("CONTROL_ONLY_REDUCED_MODEL" if control else "FULL_DECLARED_SOURCE") and
                 value["analytical_acceptance"] is False and value["matrix_positivity"] is False and
                 value["production_admission"] is False, "changed source mathematical context")
        expected = [(family, p, task) for family, name in FAMILIES.items() for p in (0, 1)
                    for task in _tiles(spec, QuantityKey(name, p))]
        _require(type(value["tiles"]) is list and len(value["tiles"]) == len(expected), "incomplete source family cover")
        for row, (family, p, task) in zip(value["tiles"], expected):
            _require(set(row) == {"family", "parity", "task", "artifact"} and row["family"] == family and
                     type(row["parity"]) is int and row["parity"] == p and
                     canonical_bytes(row["task"]) == canonical_bytes(task.to_dict()), "source domain order/coordinate mismatch")
        self.bits = bits

    def tiles(self):
        for row in self.document["tiles"]:
            task = _task(row["task"])
            ref = ArtifactRef(**row["artifact"])
            yield row, decode_publication(self.spec, _raw(self.path.parent, ref,
                                         self.spec.bounds.max_raw_bytes), task, self.bits)


def run_source(problem_path, execution_path, output_dir, *, resume=False, code_root=ROOT):
    root, output = Path(code_root).resolve(), Path(output_dir).absolute()
    problem, config, bound = _bind(problem_path, execution_path, root)
    with _slice_writer(output, resume=resume):
        context = {"problem_id": problem_id(problem), "execution_sha256": hashlib.sha256(
                   canonical_bytes(config)).hexdigest(), "role": "producer"}
        from scripts.whole_source.slice import _atomic_snapshot
        if resume:
            _require(_json(_bytes(output/"pipeline-context.json")) == context, "incompatible source resume")
        else:
            _write(output/"pipeline-context.json", canonical_bytes(context))
        _atomic_snapshot(output/"source-state.json", {"status": "RUNNING_SOURCE_NO_ANALYTICAL_ACCEPTANCE"})
        try:
            report = _run_role(output/"producer", *bound["producer"], config["control"], code_root=root,
                               resume=resume and (output/"producer/collection.json").exists())
            reader = SourceReader(output/"producer/source-manifest.json", bound["producer"][0], control=config["control"])
            count = sum(len(records) for _, records in reader.tiles())
            _atomic_snapshot(output/"source-state.json", {"status": "COMPLETE_SOURCE_EXPRESSIONS", "entries": count,
                "manifest": {**asdict(reader.ref), "path": "producer/"+reader.ref.path},
                "scope": report["scope"], "analytical_acceptance": False})
            return {"status": "COMPLETE_SOURCE_EXPRESSIONS", "entries": count, "scope": report["scope"],
                    "manifest": str(reader.path)}
        except BaseException as exc:
            _atomic_snapshot(output/"source-state.json", {"status": "FAILED_NO_ANALYTICAL_ACCEPTANCE", "error": str(exc)})
            raise


def run_audit(problem_path, source_path, execution_path, output_dir, *, code_root=ROOT):
    root, output = Path(code_root).resolve(), Path(output_dir).absolute()
    problem, config, bound = _bind(problem_path, execution_path, root)
    source = SourceReader(source_path, bound["producer"][0], control=config["control"])
    with _slice_writer(output, resume=False):
        from scripts.whole_source.slice import _atomic_snapshot
        _atomic_snapshot(output/"audit-state.json", {"status": "RUNNING_INDEPENDENT_RECONSTRUCTION"})
        try:
            _run_role(output/"analytic", *bound["analytic"], config["control"], code_root=root)
            independent = SourceReader(output/"analytic/source-manifest.json", bound["analytic"][0], control=config["control"])
            checked, consumed = 0, hashlib.sha256()
            for (sr, produced), (ar, actual) in zip(source.tiles(), independent.tiles(), strict=True):
                _require(sr["family"] == ar["family"] and sr["parity"] == ar["parity"] and
                         len(produced) == len(actual), "analytical output cover mismatch")
                consumed.update(canonical_bytes(sr))
                for x, y in zip(produced, actual, strict=True):
                    _require((x.row, x.column) == (y.row, y.column) and
                             x.lower <= y.lower <= y.upper <= x.upper,
                             "independent source containment failed at "+str((sr["family"], x.row, x.column)))
                    checked += 1
            _raw(source.path.parent, source.ref, bound["producer"][0].bounds.max_raw_bytes)
            expected = 3*(math_problem(problem, config["control"]).N//2)*(math_problem(problem, config["control"]).N//2+1)
            _require(checked == expected, "analytical source domain incomplete")
            report = {"format": "whole-source-analytical-receipt-v1", "status": "VERIFIED_ALL_DECLARED_SOURCE_ENTRIES",
                "problem_id": problem_id(problem), "source_manifest": asdict(source.ref),
                "source_directory_at_execution": str(source.path.parent),
                "source_collection_id": bound["producer"][0].collection_id,
                "analytic_collection_id": bound["analytic"][0].collection_id,
                "consumed_source_tiles_sha256": consumed.hexdigest(), "entries_checked": checked,
                "scope": source.document["scope"], "inclusive_containment": True,
                "independent_preparation": True, "frequency_exterior_terminal_mass": True,
                "both_complete_head_axes": True, "full_mathematical_source": not config["control"],
                "premises": "reviewed scalar/source-form and FLINT/Arb/Gauss premises",
                "matrix_positivity": False, "physical_row_width_accepted": False, "production_admission": False}
            _write(output/"analytical-receipt.json", canonical_bytes(report))
            _atomic_snapshot(output/"audit-state.json", {"status": report["status"], "scope": report["scope"]})
            return report
        except BaseException as exc:
            _atomic_snapshot(output/"audit-state.json", {"status": "FAILED_NO_ANALYTICAL_ACCEPTANCE", "error": str(exc)})
            raise
