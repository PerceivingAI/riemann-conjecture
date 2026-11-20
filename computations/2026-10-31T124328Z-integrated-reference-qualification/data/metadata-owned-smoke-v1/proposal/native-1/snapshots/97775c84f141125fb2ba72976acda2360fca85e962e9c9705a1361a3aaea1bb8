"""Complete source publication and independent streamed analytical containment."""
from __future__ import annotations

from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
import json
import importlib.metadata
from pathlib import Path
from types import SimpleNamespace

from scripts.whole_source.contract import (
    ROOT, ArtifactRef, ContractError, ModeRange, QuantityKey, bind_problem,
    canonical_bytes, problem_id,
)
from scripts.whole_source.artifacts import (
    Axis, CodecBounds, CollectionLock, CollectionSpec, ContributionTask, ChunkStore,
    IntervalRecord, QuantitySpec, _coordinates, _decode_chunk, _raw,
    _task, _catalog_limit, decode_publication, publish_publication, stage_publication,
)
from scripts.whole_source.execution import (
    MIB, ExecutionPlan, WorkloadExecution, _RUNTIME, _bytes, _json, _write, exact_telemetry,
)
from scripts.whole_source.slice import _parse_staged, _ref, _request, _slice_writer
from scripts.whole_source.gram import _record, _stage

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
    values = {"columns": tile_modes, "complete": 1, "rows": tile_modes,
              "F_column.rows": model.M//2, "F_column.columns": 1}
    for name in ("head_column", "head_image"):
        values[name+".rows"] = (model.M-model.N)//2
        values[name+".columns"] = 1
    return tuple(sorted(values.items()))


def _producer_tile_requirements(problem, rows, columns, *, precision_bits):
    """Price the producer's live tile operands without importing native arithmetic."""
    rows, columns = tuple(rows), tuple(columns)
    modes = sorted(set(rows) | set(columns))
    if (not modes or len(rows) > 32 or len(columns) > 32 or len(modes) > 64 or
            any(type(n) is not int or not 0 <= n < problem.N for n in modes) or
            len({n % 2 for n in modes}) != 1):
        raise ValueError("bounded same-parity low tile required")
    width, count = max(modes)+1, len(modes)
    ball = 96+16*((precision_bits+63)//64)
    rational = 96+2*((4*width+63)//64)*8
    # Python containers, exact bases, complete live F/C/Y, and all entry results.
    private = (count*(problem.M//2+problem.M-problem.N)*ball +
               count*width*rational + 12*len(rows)*len(columns)*(ball+128) +
               2*problem.source_gauss_order*ball)
    # Current shifted images, endpoint vectors, products, and 32-node matrices.
    native = (count*width+24*width+3*32*count+4*len(rows)*len(columns))*ball
    return {"private_bytes": private, "native_bytes": native}


def _producer_requirements(spec, control):
    model = math_problem(spec.problem, control)
    maxima = {"private_bytes": 0, "native_bytes": 0}
    for parity in (0, 1):
        for task in _tiles(spec, QuantityKey("A_model", parity)):
            account = _producer_tile_requirements(model, task.rows, task.columns,
                precision_bits=spec.problem.arithmetic.source_bits)
            for name in maxima:
                maxima[name] = max(maxima[name], account[name])
    return maxima


def _check_producer_plan(spec, plan, control):
    _require(plan.precision_bits == spec.problem.arithmetic.source_bits,
             "producer execution precision differs from source policy")
    required = _producer_requirements(spec, control)
    _require(plan.worker_private_mib*MIB >= required["private_bytes"] + _catalog_limit(spec),
             "producer private allowance does not cover final source tiles")
    _require(plan.native_workspace_mib*MIB >= required["native_bytes"],
             "producer native allowance does not cover final source tiles")


def _analytic_tile_requirements(problem, rows, columns, *, precision_bits):
    """Price independent analytical operands without importing native arithmetic."""
    rows, columns = tuple(rows), tuple(columns)
    modes = sorted(set(rows) | set(columns))
    if (not modes or len(rows) > 32 or len(columns) > 32 or len(modes) > 64 or
            any(type(n) is not int or not 0 <= n < problem.N for n in modes) or
            len({n % 2 for n in modes}) != 1):
        raise ValueError("bounded same-parity low tile required")
    width, count = max(modes)+1, len(modes)
    ball = 96+16*((precision_bits+63)//64)
    rational = 96+16*((4*(width+problem.K)+63)//64)
    # F/C/Y coexist with exact rows, factorials, beta vectors and returned entries.
    private = (count*(problem.M//2+problem.M-problem.N)*ball +
               (count*width+12*(width+problem.K))*rational +
               12*len(rows)*len(columns)*(ball+128) +
               width*(64+width*max(1, width.bit_length())//8))
    # One combined family OR one shifted family, native multiply/shift scratch.
    native = (count*width+28*(width+problem.K))*ball
    return {"private_bytes": private, "native_bytes": native}


def _analytic_requirements(spec, control):
    model = math_problem(spec.problem, control)
    maxima = {"private_bytes": 0, "native_bytes": 0}
    for parity in (0, 1):
        for task in _tiles(spec, QuantityKey("A_model", parity)):
            account = _analytic_tile_requirements(model, task.rows, task.columns,
                precision_bits=spec.problem.arithmetic.audit_bits)
            for name in maxima:
                maxima[name] = max(maxima[name], account[name])
    return maxima


def _check_analytic_plan(spec, plan, control):
    _require(plan.precision_bits == spec.problem.arithmetic.audit_bits,
             "analytic execution precision differs from audit policy")
    required = _analytic_requirements(spec, control)
    _require(plan.worker_private_mib*MIB >= required["private_bytes"] + _catalog_limit(spec),
             "analytic private allowance does not cover final source tiles")
    _require(plan.native_workspace_mib*MIB >= required["native_bytes"],
             "analytic native allowance does not cover final source tiles")


def prepare_source_inputs(problem, directory, *, origin_git_commit, origin_git_dirty,
                          code_root=ROOT, control=False, tile_modes=16, memory_mib=None):
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
        required = (_producer_requirements(spec, control) if role == "producer"
                    else _analytic_requirements(spec, control))
        plan = ExecutionPlan(problem_id(problem), spec.collection_id, role, 1, 1, 1,
            memory_mib=memory_mib or 1, reserve_mib=128, root_mib=128, worker_base_mib=80,
            worker_private_mib=max(128, (required["private_bytes"]+_catalog_limit(spec)+MIB-1)//MIB),
            native_workspace_mib=max(128, (required["native_bytes"]+MIB-1)//MIB), conversion_mib=64,
            codec_mib=256, queue_mib=8, supervisor_increment_mib=256,
            repository_mib=8192, temporary_mib=128, minimum_free_mib=64,
            max_tasks=4096, task_bytes=128*1024, result_bytes=MIB, log_bytes=4*MIB,
            task_program=_ref(root, "scripts/whole_source/"+role+".py"), task_function="evaluate_source",
            precision_bits=problem.arithmetic.source_bits if role == "producer" else problem.arithmetic.audit_bits,
            backend="python-flint", backend_version=spec.backend_version,
            provenance=_ref(root, origin.relative_to(root).as_posix()), scope="SOURCE_EXPRESSIONS_ONLY")
        from scripts.whole_source.resources import auto_plan
        plan = auto_plan(plan, parallel=True, memory_mib=memory_mib, helper_root=root)
        model = math_problem(problem, control)
        head = (model.M-model.N)//2
        group_bytes = head*(head+1)//2*(2*((spec.grid_bits+35)//4)+64)
        temporary_mib = max(128, (plan.workers*(group_bytes+2*spec.bounds.max_raw_bytes)+MIB-1)//MIB)
        bounds = replace(bounds, max_temporary_bytes=temporary_mib*MIB)
        spec = replace(spec, native_threads=plan.threads, bounds=bounds)
        spec._validate()
        plan = replace(plan, collection_sha256=spec.collection_id, temporary_mib=temporary_mib)
        if role == "producer":
            _check_producer_plan(spec, plan, control)
        else:
            _check_analytic_plan(spec, plan, control)
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
        if role == "producer":
            _check_producer_plan(spec, plan, config["control"])
        else:
            _check_analytic_plan(spec, plan, config["control"])
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


def _kernel_panels(spec, p):
    """Row-wide compact integer pages; native output tiles remain bounded squares."""
    quantity = spec.quantity(QuantityKey("kernel_complete", p))
    previous = None
    for task in _tiles(spec, quantity.key):
        if task.rows != previous:
            yield ContributionTask(quantity.key, task.rows, quantity.columns, COMPLETE)
            previous = task.rows


def _kernel_group(staging, model, p, functions, start, stop):
    """Evaluate each assigned anchor once; no full high-precision native K."""
    import sys
    from scripts.whole_source import execution
    spec = staging.spec
    _require(type(start) is type(stop) is int and
             0 <= start < stop <= len(model.frequency_edges), "invalid kernel anchor range")
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
    for anchor in range(start, stop):
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
    from scripts.whole_source.artifacts import _check_quota, _safe, _volume_gate
    panels = []
    for task in _kernel_panels(spec, p):
        records = []
        for m, n in _coordinates(task, True):
            i, j = (m-model.N-p)//2, (n-model.N-p)//2
            index = i*h-i*(i-1)//2+j-i
            records.append([m, n, hex(lower[index]), hex(upper[index])])
        _require(len(records) <= spec.bounds.max_records, "kernel group page exceeds record cap")
        raw = canonical_bytes({"format": "whole-source-frequency-group-v1",
            "scope": "PARTIAL_FREQUENCY_SUM", "collection_id": spec.collection_id,
            "role": spec.role, "grid_bits": spec.grid_bits, "domain": task.to_dict(),
            "anchor_start": start, "anchor_stop": stop, "records": records})
        _require(len(raw) <= min(spec.bounds.max_raw_bytes, spec.bounds.max_decoded_bytes),
                 "kernel group page exceeds codec cap")
        relative = "attempts/"+staging.attempt_id+"/staging/"+hashlib.sha256(raw).hexdigest()
        staging._check()
        with _volume_gate(staging.root):
            _check_quota(staging.root, spec.bounds, len(raw), 2*len(raw))
            _write(_safe(staging.root, relative, missing=True), raw)
        staging._check()
        panels.append({"domain": task.to_dict(),
                       "artifact": asdict(ArtifactRef(relative, hashlib.sha256(raw).hexdigest(), len(raw)))})
    return {"anchor_start": start, "anchor_stop": stop, "panels": panels}


def _kernel_reduce(staging, model, p, domain, groups):
    """Complete the exact fixed-grid sum before publishing any kernel cache tile."""
    from scripts.whole_source.artifacts import decode_integer
    spec = staging.spec
    _require(domain in tuple(_kernel_panels(spec, p)) and type(groups) is list and
             0 < len(groups) <= len(model.frequency_edges), "invalid kernel reduction domain")
    coordinates = list(_coordinates(domain, True))
    totals = [[0, 0] for _ in coordinates]
    next_anchor = 0
    for group in groups:
        _require(type(group) is dict and set(group) == {"anchor_start", "anchor_stop", "artifact"},
                 "invalid kernel group reference")
        start, stop = group["anchor_start"], group["anchor_stop"]
        _require(type(start) is type(stop) is int and start == next_anchor and
                 start < stop <= len(model.frequency_edges), "incomplete or overlapping anchor cover")
        raw = _raw(staging.root, ArtifactRef(**group["artifact"]), spec.bounds.max_raw_bytes)
        value = _json(raw)
        _require(type(value) is dict and set(value) == {"format", "scope", "collection_id", "role",
                 "grid_bits", "domain", "anchor_start", "anchor_stop", "records"} and
                 value["format"] == "whole-source-frequency-group-v1" and
                 value["scope"] == "PARTIAL_FREQUENCY_SUM" and
                 value["collection_id"] == spec.collection_id and value["role"] == spec.role and
                 type(value["grid_bits"]) is int and value["grid_bits"] == spec.grid_bits and
                 value["domain"] == domain.to_dict() and
                 type(value["anchor_start"]) is type(value["anchor_stop"]) is int and
                 value["anchor_start"] == start and value["anchor_stop"] == stop and
                 type(value["records"]) is list and len(value["records"]) == len(coordinates),
                 "foreign or incomplete kernel group page")
        for record, (m, n), total in zip(value["records"], coordinates, totals, strict=True):
            _require(type(record) is list and len(record) == 4 and
                     type(record[0]) is type(record[1]) is int and record[:2] == [m, n],
                     "noncanonical kernel group coordinate")
            lo, hi = (decode_integer(endpoint, spec.grid_bits+32) for endpoint in record[2:])
            _require(lo <= hi, "reversed kernel group interval")
            total[0] += lo
            total[1] += hi
            _require(max(abs(total[0]).bit_length(), abs(total[1]).bit_length()) <= spec.grid_bits+32,
                     "kernel reduction exceeds compact integer allowance")
        next_anchor = stop
    _require(next_anchor == len(model.frequency_edges), "missing terminal frequency contribution")
    values = dict(zip(coordinates, totals, strict=True))
    return [_stage(staging, task, (IntervalRecord(m, n, (0,),
        Fraction(values[m, n][0], 1 << spec.grid_bits),
        Fraction(values[m, n][1], 1 << spec.grid_bits))
        for m, n in _coordinates(task, True)))
        for task in _tiles(spec, QuantityKey("kernel_complete", p)) if task.rows == domain.rows]


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
    chunks, publications, group = [], [], None
    if operation == "kernel-group":
        group = _kernel_group(staging, model, p, functions, task["anchor_start"], task["anchor_stop"])
    elif operation == "kernel-reduce":
        chunks = _kernel_reduce(staging, model, p, _task(task["domain"]), task["groups"])
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
        functions["tile_account"](model, domain.rows, domain.columns)
        columns, head, images = {}, {}, {}
        for row in task["columns"]:
            n = row["n"]
            columns[n] = _column(staging, "F_column", n, row["F"])
            head[n] = _column(staging, "head_column", n, row["C"])
            images[n] = _column(staging, "head_image", n, row["Y"])
        outputs = {name: [] for name in FAMILIES}
        entries = functions["tile"](model, domain.rows, domain.columns, columns)
        for m, n in _coordinates(domain, True):
            values = entries[m, n]
            outputs["A_model"].append(_record(m, n, values[("A_model", m, n)]))
            outputs["weighted_complete_tail"].append(_record(m, n, values[("weighted_complete_tail", m, n)]))
            outputs["weighted_head"].append(_record(m, n, functions["head_pair"](model, head[m], images[n])))
        for canonical, name in FAMILIES.items():
            target = ContributionTask(QuantityKey(name, p), domain.rows, domain.columns, COMPLETE)
            publications.append(_wire(stage_publication(staging, target, outputs[canonical])))
    else:
        raise ContractError("unknown source operation")
    from scripts.whole_source.execution import _WORKER
    return {"chunks": chunks, "publications": publications, "kernel_group": group, "scope": _WORKER[0].scope,
            "statistics": {"operation": operation, "parity": p, "control": control,
                "frequency_anchors": len(model.frequency_edges) if operation.startswith("kernel-") else 0,
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
        panels = list(_kernel_panels(spec, p))
        groups = min(plan.workers, len(model.frequency_edges))
        _require(groups <= plan.max_tasks and len(panels) <= plan.max_tasks,
                 "kernel split exceeds stage task count")
        quantity = spec.quantity(QuantityKey("kernel_complete", p))
        for panel in panels:
            first = (panel.rows.start-quantity.rows.start)//2
            count = len(panel.rows)*len(quantity.columns)-len(panel.rows)*(2*first+len(panel.rows)-1)//2
            _require(count <= spec.bounds.max_records, "kernel row page exceeds record transport")
        request = _request(operation="kernel-reduce", parity=p, control=control,
            domain=panels[0].to_dict(), groups=[{"anchor_start": 0, "anchor_stop": 1,
                "artifact": dummy_ref}]*groups)
        _require(len(canonical_bytes(request))+1024 <= plan.task_bytes,
                 "kernel partial inventory exceeds task transport")
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


def scientific_manifest(spec, control, tiles):
    model = math_problem(spec.problem, control)
    return {"format": "whole-source-scientific-manifest-v2", "problem_id": problem_id(spec.problem),
        "scientific_spec": spec.scientific_dict(), "scientific_id": spec.scientific_id,
        "control": control, "geometry": {"N": model.N, "M": model.M, "K": model.K},
        "role": spec.role,
        "publication_bits": spec.problem.arithmetic.publication_bits if spec.role == "producer" else spec.grid_bits,
        "scope": "CONTROL_ONLY_REDUCED_MODEL" if control else "FULL_DECLARED_SOURCE",
        "tiles": tiles, "full_mathematical_source": not control,
        "analytical_acceptance": False, "matrix_positivity": False, "production_admission": False,
        "residual_model_payment": "Lambda D once in later exact full-space proof"}


def source_execution_document(source_path, execution_path=None):
    """Read the separate operational record; it never enters scientific bytes."""
    source_path = Path(source_path).resolve()
    raw = _bytes(source_path)
    document = _json(raw)
    _require(document.get("format") == "whole-source-scientific-manifest-v2",
             "source requires scientific manifest v2")
    path = Path(execution_path) if execution_path is not None else source_path.parent/"source-execution.json"
    execution = _json(_bytes(path))
    expected = asdict(ArtifactRef(source_path.name, hashlib.sha256(raw).hexdigest(), len(raw)))
    _require(type(execution) is dict and set(execution) == {
        "format", "source_manifest", "scientific_id", "collection", "collection_id", "provenance"} and
        execution["format"] == "whole-source-publication-execution-v2" and
        execution["source_manifest"] == expected and execution["scientific_id"] == document["scientific_id"] and
        execution["collection_id"] == hashlib.sha256(canonical_bytes(execution["collection"])).hexdigest(),
        "source execution does not bind this scientific publication")
    return execution


def write_source_execution(source_path, spec, provenance):
    """Publish explicit operational provenance, including declared test controls."""
    path = Path(source_path)
    raw = _bytes(path)
    execution = {"format": "whole-source-publication-execution-v2",
        "source_manifest": asdict(ArtifactRef(path.name, hashlib.sha256(raw).hexdigest(), len(raw))),
        "scientific_id": spec.scientific_id, "collection": spec.to_dict(),
        "collection_id": spec.collection_id, "provenance": provenance}
    target = path.parent/"source-execution.json"
    encoded = canonical_bytes(execution)
    if target.exists():
        _require(_bytes(target) == encoded, "changed immutable source execution record")
    else:
        _write(target, encoded)
    return target


def verify_source_execution(reader):
    """Verify the complete producing-task closure, retaining all other history."""
    from scripts.whole_source.source_dependencies import SourceDependencies
    provenance = reader.execution["provenance"]
    _require(provenance["kind"] == "OWNED_SOURCE", "source has no owned publication evidence")
    plan = ExecutionPlan.from_dict(provenance["plan"])
    selected = SourceDependencies(reader.path.parent, reader.spec, plan).select(reader.document["tiles"])
    _require(all(provenance[key] == selected[key] for key in ("receipts", "dependencies", "history")),
             "source publication dependency selection differs")
    return {"source_manifest": asdict(reader.ref), "scientific_id": reader.spec.scientific_id,
            "execution": asdict(reader.execution_ref), "collection_id": reader.spec.collection_id,
            **selected}


def _execution_binding(reader):
    return {"directory": str(reader.path.parent), "manifest": asdict(reader.ref),
            "execution": asdict(reader.execution_ref), "collection_id": reader.spec.collection_id}


def verify_audit_execution(audit_path, source, independent):
    path = Path(audit_path)
    record = _json(_bytes(path.parent/"audit-execution.json"))
    expected = {"format": "whole-source-audit-execution-v1",
        "audit": asdict(_ref(path.parent, path.name)),
        "source": _execution_binding(source), "analytic": _execution_binding(independent)}
    _require(record == expected, "audit operational evidence differs")
    verify_source_execution(source)
    verify_source_execution(independent)
    return asdict(_ref(path.parent, "audit-execution.json"))


def compare_source_audits(first_source, first_audit, second_source, second_audit, *, code_root=ROOT):
    """Compare complete canonical science and separately verify both executions."""
    problem = bind_problem("retained-t081", root=Path(code_root))
    sources, audits, controls = [], [], []
    for source_path, audit_path in ((first_source, first_audit), (second_source, second_audit)):
        source_path, audit_path = Path(source_path), Path(audit_path)
        execution = source_execution_document(source_path)
        spec = CollectionSpec.from_dict(problem, execution["collection"], code_root=Path(code_root))
        control = _json(_bytes(source_path))["control"]
        source = SourceReader(source_path, spec, control=control)
        independent_path = audit_path.parent/"analytic/source-manifest.json"
        other_execution = source_execution_document(independent_path)
        other_spec = CollectionSpec.from_dict(problem, other_execution["collection"], code_root=Path(code_root))
        independent = SourceReader(independent_path, other_spec, control=control)
        _require(spec.role == "producer" and other_spec.role == "analytic",
                 "source/audit execution roles differ")
        verify_audit_execution(audit_path, source, independent)
        audit = _json(_bytes(audit_path))
        expected_count = 3*(math_problem(problem, control).N//2)*(math_problem(problem, control).N//2+1)
        _require(audit.get("format") == "whole-source-analytical-receipt-v2" and
                 audit.get("status") == "VERIFIED_ALL_DECLARED_SOURCE_ENTRIES" and
                 audit.get("source_manifest") == asdict(source.ref) and
                 audit.get("source_scientific_id") == spec.scientific_id and
                 audit.get("analytic_scientific_id") == other_spec.scientific_id and
                 audit.get("entries_checked") == expected_count and
                 audit.get("full_mathematical_source") is (not control),
                 "incomplete scientific audit for replay")
        consumed, checked = hashlib.sha256(), 0
        for (row, produced), (other, enclosed) in zip(source.tiles(), independent.tiles(), strict=True):
            _require((row["family"], row["parity"], row["task"]) ==
                     (other["family"], other["parity"], other["task"]),
                     "replay audit domain differs")
            consumed.update(canonical_bytes(row))
            for value, exact in zip(produced, enclosed, strict=True):
                _require((value.row, value.column) == (exact.row, exact.column) and
                         value.lower <= exact.lower <= exact.upper <= value.upper,
                         "replay source is not independently contained")
                checked += 1
        _require(checked == expected_count and
                 consumed.hexdigest() == audit["consumed_source_tiles_sha256"],
                 "replay audit source cover differs")
        sources.append(source)
        audits.append(audit)
        controls.append(control)
    _require(controls[0] is controls[1] and sources[0].document == sources[1].document,
             "replayed source manifest differs")
    for before, after in zip(sources[0].document["tiles"], sources[1].document["tiles"], strict=True):
        _require(before == after and
                 _raw(sources[0].path.parent, ArtifactRef(**before["artifact"]), 8*MIB) ==
                 _raw(sources[1].path.parent, ArtifactRef(**after["artifact"]), 8*MIB),
                 "replayed scientific publication differs")
    for audit in audits:
        audit.pop("source_directory_at_execution")
    _require(audits[0] == audits[1], "replayed scientific audit differs")
    n = math_problem(problem, controls[0]).N//2
    return {"status": ("PASS_CONTROL_ONLY_SOURCE_AUDIT_REPLAY_COMPARISON" if controls[0]
                       else "PASS_FULL_SOURCE_AUDIT_REPLAY_COMPARISON"),
            "control": controls[0], "entries_compared": 3*n*(n+1),
            "complete_parity_dimensions": [n, n]}


def _run_role(output, spec, plan, control, *, code_root, resume=False):
    _admit_transport(output, spec, plan, control)
    from scripts.whole_source.source_dependencies import SourceDependencies, check_history
    if resume:
        check_history(output)
    with CollectionLock.acquire(output, spec, resume=resume) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=code_root) as execution:
            store = ChunkStore(lock, spec, attempt_id=execution.attempt_id)
            provenance = SourceDependencies(output, spec, plan)
            index_path = output/"publication-index.json"
            published = _json(_bytes(index_path)) if index_path.exists() else {}
            statistics = []
            def find(task):
                return store._chunk_ref(task)
            def stage(name, requests):
                requests = list(requests)
                if not requests:
                    return
                execution.run_stage(name, requests)
                for result in execution.read_results(name):
                    data = result["result"]
                    provenance.bind(lock, name, result)
                    _require(data["scope"] == plan.scope, "changed source worker scope")
                    for row in data["chunks"]:
                        task, value = _parse_staged(row)
                        store.publish_chunk(task, value)
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
                    count = min(plan.workers, len(model.frequency_edges))
                    edges = [i*len(model.frequency_edges)//count for i in range(count+1)]
                    name = "kernel-groups-"+str(p)
                    execution.run_stage(name, [_request(operation="kernel-group", parity=p, control=control,
                        anchor_start=start, anchor_stop=stop) for start, stop in zip(edges, edges[1:])])
                    groups = []
                    for result in execution.read_results(name):
                        data = result["result"]
                        _require(data["scope"] == plan.scope and not data["chunks"] and
                                 not data["publications"], "partial kernel cannot publish complete chunks")
                        provenance.bind(lock, name, result)
                        group = data["kernel_group"]
                        _require([row["domain"] for row in group["panels"]] ==
                                 [task.to_dict() for task in _kernel_panels(spec, p)],
                                 "incomplete partial kernel page cover")
                        panels = []
                        for row in group["panels"]:
                            ref = ArtifactRef(**row["artifact"])
                            _require(ref.path.startswith("attempts/"+execution.attempt_id+"/staging/"),
                                     "foreign partial kernel attempt")
                            raw = _raw(output, ref, spec.bounds.max_raw_bytes)
                            kept = lock._immutable("seals", raw)
                            from scripts.whole_source.artifacts import _safe
                            _safe(output, ref.path).unlink()
                            panels.append({"domain": row["domain"], "artifact": asdict(kept)})
                        groups.append({**group, "panels": panels})
                        statistics.append(data["statistics"])
                    groups.sort(key=lambda group: group["anchor_start"])
                    _require([(group["anchor_start"], group["anchor_stop"]) for group in groups] ==
                             list(zip(edges, edges[1:])), "incomplete kernel anchor task cover")
                    stage("kernel-"+str(p), [_request(operation="kernel-reduce", parity=p, control=control,
                        domain=domain.to_dict(), groups=[{"anchor_start": group["anchor_start"],
                            "anchor_stop": group["anchor_stop"], "artifact": group["panels"][i]["artifact"]}
                            for group in groups]) for i, domain in enumerate(_kernel_panels(spec, p))])
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
            lock.verify_committed()
            tiles = []
            for canonical, name in FAMILIES.items():
                for p in (0, 1):
                    for task in _tiles(spec, QuantityKey(name, p)):
                        ref = ArtifactRef(**published[canonical_bytes(task.to_dict()).hex()])
                        bits = spec.problem.arithmetic.publication_bits if spec.role == "producer" else spec.grid_bits
                        decode_publication(spec, _raw(output, ref, spec.bounds.max_raw_bytes), task, bits)
                        tiles.append({"family": canonical, "parity": p, "task": task.to_dict(), "artifact": asdict(ref)})
            selection = provenance.select(tiles)
            report = scientific_manifest(spec, control, tiles)
            path = output/"source-manifest.json"
            raw = canonical_bytes(report)
            if path.exists():
                _require(_bytes(path) == raw, "changed completed scientific manifest")
            else:
                _write(path, raw)
            write_source_execution(path, spec, {"kind": "OWNED_SOURCE",
                "plan": plan.to_dict(), **selection})
            from scripts.whole_source.slice import _atomic_snapshot
            _atomic_snapshot(output/("run-"+execution.attempt_id+".json"), {
                "status": "COMPLETE_SOURCE_EXPRESSIONS", "manifest_sha256": hashlib.sha256(raw).hexdigest(),
                "statistics": statistics, "owned_receipts": exact_telemetry(execution.receipts)})
            return report


class SourceReader:
    """Bound one immutable scientific byte image and its exact ordered domain cover."""
    def __init__(self, path, spec, *, control, execution_path=None):
        self.path, self.spec = Path(path).resolve(), spec
        raw = _bytes(self.path)
        self.ref = ArtifactRef(self.path.name, hashlib.sha256(raw).hexdigest(), len(raw))
        self.document = _json(raw)
        value = self.document
        model = math_problem(spec.problem, control)
        bits = spec.problem.arithmetic.publication_bits if spec.role == "producer" else spec.grid_bits
        _require(type(value) is dict and set(value) == {
            "format", "problem_id", "scientific_spec", "scientific_id", "control", "geometry", "role", "publication_bits",
            "scope", "tiles", "full_mathematical_source", "analytical_acceptance", "matrix_positivity",
            "production_admission", "residual_model_payment"} and
            value["residual_model_payment"] == "Lambda D once in later exact full-space proof",
            "invalid closed scientific manifest")
        _require(value["format"] == "whole-source-scientific-manifest-v2" and
                 canonical_bytes(value["scientific_spec"]) == canonical_bytes(spec.scientific_dict()) and
                 value["scientific_id"] == spec.scientific_id and value["problem_id"] == problem_id(spec.problem) and
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
        self.execution_path = (Path(execution_path).resolve() if execution_path is not None
                               else self.path.parent/"source-execution.json")
        self.execution_ref = _ref(self.execution_path.parent, self.execution_path.name)
        self.execution = source_execution_document(self.path, self.execution_path)
        _require(canonical_bytes(self.execution["collection"]) == canonical_bytes(spec.to_dict()) and
                 self.execution["collection_id"] == spec.collection_id, "source operational specification differs")
        provenance = self.execution["provenance"]
        kind = provenance.get("kind")
        if kind == "OWNED_SOURCE":
            _require(set(provenance) == {"kind", "plan", "receipts", "dependencies", "history"} and
                     all(type(provenance[key]) is list for key in ("receipts", "dependencies", "history")) and
                     provenance["receipts"] and provenance["dependencies"],
                     "source publication ownership missing")
            plan = ExecutionPlan.from_dict(provenance["plan"])
            _require(plan.collection_sha256 == spec.collection_id and plan.role == spec.role,
                     "source execution plan differs")
            for key in ("receipts", "dependencies", "history"):
                for ref in provenance[key]:
                    _raw(self.path.parent, ArtifactRef(**ref), 8*MIB)
        elif kind == "DECLARED_CONTROL":
            _require(control is True and set(provenance) == {"kind"},
                     "declared source cannot claim supported-source ownership")
        elif kind == "MATHEMATICAL_VARIANT":
            _require(set(provenance) == {"kind", "original_source", "original_execution"},
                     "mathematical variant lacks original bindings")
            for key in ("original_source", "original_execution"):
                record = provenance[key]
                _raw(Path(record["directory"]), ArtifactRef(**record["artifact"]), 8*MIB)
        else:
            raise ContractError("unknown source publication provenance")

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
            verify_source_execution(source)
            verify_source_execution(independent)
            expected = 3*(math_problem(problem, config["control"]).N//2)*(math_problem(problem, config["control"]).N//2+1)
            _require(checked == expected, "analytical source domain incomplete")
            report = {"format": "whole-source-analytical-receipt-v2", "status": "VERIFIED_ALL_DECLARED_SOURCE_ENTRIES",
                "problem_id": problem_id(problem), "source_manifest": asdict(source.ref),
                "source_directory_at_execution": str(source.path.parent),
                "source_scientific_id": bound["producer"][0].scientific_id,
                "analytic_scientific_id": bound["analytic"][0].scientific_id,
                "consumed_source_tiles_sha256": consumed.hexdigest(), "entries_checked": checked,
                "scope": source.document["scope"], "inclusive_containment": True,
                "independent_preparation": True, "frequency_exterior_terminal_mass": True,
                "both_complete_head_axes": True, "full_mathematical_source": not config["control"],
                "premises": "reviewed scalar/source-form and FLINT/Arb/Gauss premises",
                "matrix_positivity": False, "physical_row_width_accepted": False, "production_admission": False}
            _write(output/"analytical-receipt.json", canonical_bytes(report))
            _write(output/"audit-execution.json", canonical_bytes({
                "format": "whole-source-audit-execution-v1",
                "audit": asdict(_ref(output, "analytical-receipt.json")),
                "source": {"directory": str(source.path.parent), "manifest": asdict(source.ref),
                           "execution": asdict(source.execution_ref), "collection_id": source.spec.collection_id},
                "analytic": {"directory": str(independent.path.parent), "manifest": asdict(independent.ref),
                             "execution": asdict(independent.execution_ref),
                             "collection_id": independent.spec.collection_id}}))
            _atomic_snapshot(output/"audit-state.json", {"status": report["status"], "scope": report["scope"]})
            return report
        except BaseException as exc:
            _atomic_snapshot(output/"audit-state.json", {"status": "FAILED_NO_ANALYTICAL_ACCEPTANCE", "error": str(exc)})
            raise
