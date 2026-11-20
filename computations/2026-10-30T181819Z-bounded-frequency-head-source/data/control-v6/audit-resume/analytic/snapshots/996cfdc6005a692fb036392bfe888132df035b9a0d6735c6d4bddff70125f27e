"""Bounded, locally owned research tasks. Operational receipts are not proof.

The pinned supervisor owns one root and its descendants. A bounded spawn pool
runs INSIDE that root, never as independent full reconstructions per core.
"""
from __future__ import annotations

# The versioned stage loader imports this file by path after its READY/GO gate.
import sys
from pathlib import Path
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import builtins
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.metadata
import json
import multiprocessing
import os
import queue
import re
import shutil
import stat
import subprocess
import threading
import time
import types
import uuid

from scripts.run_observability import (
    OutputDirectoryLock, RunStatusWriter, write_run_identity,
)
from scripts.whole_source.contract import (
    ArtifactRef, ContractError, MAX_FILE_BYTES, ROOT, canonical_bytes, problem_id,
)

MIB = 1024 * 1024
BUNDLE = "computations/2026-10-28T034134Z-t081-resource-execution"
_HELPERS = {
    "execution_resources_v2.py": "8f3fc4d3bf0ddbba99ff6686ccb4acbe81ed583f8f3fc0ac6572e4acf473a9e2",
    "resource_limits_v1.py": "b6258b25377244cf97fb094e20c017dd3438a66c69cc33aeb737f5333b53b717",
    "execution_supervisor_v1.py": "cc1c10f9d54a0cff7250d3a53f72480c5e56a49262176d32d0b1de98090d334c",
    "stage_worker_v1.py": "3ecc6c00630b7d7eb2bffd8d544f61f18ade7ec30b9b7fc2348e7274d22faeee",
    "execution_events_v1.py": "f89c177e4622b3b939b729d8daa9dd1089942734d5fafe3cbf689ff486c5690f",
}
_RUNTIME = ("scripts/whole_source/__init__.py", "scripts/whole_source/contract.py",
            "scripts/whole_source/artifacts.py", "scripts/whole_source/execution.py",
            "scripts/run_observability.py")
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")


def _require(condition, message):
    if not condition:
        raise ContractError(message)


def _positive(value, label, minimum=1, maximum=1 << 40):
    _require(type(value) is int and minimum <= value <= maximum, "invalid " + label)
    return value


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, "duplicate execution field")
            result[key] = value
        return result
    def reject(value):
        raise ContractError("nonexact execution number: " + value)
    result = json.loads(raw, object_pairs_hook=pairs, parse_float=reject, parse_constant=reject)
    _require(type(result) is dict, "execution object required")
    return result


def _bytes(path, cap=MAX_FILE_BYTES):
    path = Path(path)
    for part in (path, *path.parents):
        info = part.lstat()
        _require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                 "reparse/symlink execution path")
    _require(stat.S_ISREG(path.stat().st_mode), "regular execution file required")
    with path.open("rb") as stream:
        raw = stream.read(cap + 1)
    _require(len(raw) <= cap, "execution file exceeds cap")
    return raw


def _file_digest(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while block := stream.read(65536):
            digest.update(block)
    return digest.hexdigest()


def _write(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + "." + uuid.uuid4().hex + ".tmp")
    _require(not path.exists(), "immutable execution artifact already exists")
    with temporary.open("xb") as stream:
        _require(stream.write(raw) == len(raw), "short execution write")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    return ArtifactRef(path.name, _sha(raw), len(raw))


def _install(root, ref, raw):
    path = Path(root) / ref.path
    if path.exists():
        _require(_bound(root, ref) == raw, "conflicting captured input")
    else:
        _write(path, raw)


def _load_neutral(name, raw, filename, dependencies):
    module = types.ModuleType(name)
    module.__file__ = str(filename)
    original = builtins.__import__
    def importing(name, *args, **kwargs):
        if name in dependencies:
            return dependencies[name]
        return original(name, *args, **kwargs)
    module.__dict__["__builtins__"] = {**vars(builtins), "__import__": importing}
    exec(compile(raw, str(filename), "exec"), module.__dict__)
    return module


def neutral_helpers(root=ROOT):
    """Compile exactly the pinned bounded bytes; never trust a cached alias."""
    root = Path(root)
    snapshots = {}
    for name, digest in _HELPERS.items():
        raw = _bytes(root / BUNDLE / name)
        _require(_sha(raw) == digest, "neutral helper changed: " + name)
        snapshots[name] = raw
    limits = _load_neutral("whole_source_limits", snapshots["resource_limits_v1.py"],
                           root / BUNDLE / "resource_limits_v1.py", {})
    dependencies = {"resource_limits_v1": limits}
    resources = _load_neutral("whole_source_resources", snapshots["execution_resources_v2.py"],
                             root / BUNDLE / "execution_resources_v2.py", dependencies)
    supervisor = _load_neutral("whole_source_supervisor", snapshots["execution_supervisor_v1.py"],
                              root / BUNDLE / "execution_supervisor_v1.py", dependencies)
    return resources, limits, supervisor, snapshots


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    problem_sha256: str
    collection_sha256: str
    role: str
    cpus: int
    workers: int
    threads: int
    memory_mib: int
    reserve_mib: int
    root_mib: int
    worker_base_mib: int
    worker_private_mib: int
    native_workspace_mib: int
    conversion_mib: int
    codec_mib: int
    queue_mib: int
    supervisor_increment_mib: int
    repository_mib: int
    temporary_mib: int
    minimum_free_mib: int
    max_tasks: int
    task_bytes: int
    result_bytes: int
    log_bytes: int
    task_program: ArtifactRef
    task_function: str
    precision_bits: int
    backend: str
    backend_version: str
    provenance: ArtifactRef
    pool_measurement: ArtifactRef | None = None
    scope: str = "OPERATIONAL_CONTROL_ONLY"

    def __post_init__(self):
        _require(_HEX.fullmatch(self.problem_sha256) and _HEX.fullmatch(self.collection_sha256),
                 "invalid scientific execution identity")
        _require(self.role in ("producer", "analytic", "exact"), "invalid execution role")
        for name in ("cpus", "workers", "threads", "memory_mib", "root_mib", "worker_base_mib", "worker_private_mib",
                     "repository_mib", "temporary_mib", "max_tasks", "task_bytes", "result_bytes", "log_bytes",
                     "precision_bits"):
            _positive(getattr(self, name), name)
        for name in ("reserve_mib", "native_workspace_mib", "conversion_mib", "codec_mib", "queue_mib",
                     "supervisor_increment_mib", "minimum_free_mib"):
            _positive(getattr(self, name), name, 0)
        _require(self.workers * self.threads <= self.cpus, "workers times threads exceeds one CPU allowance")
        _require(self.queue_mib * MIB >= 2 * self.workers * self.result_bytes + MIB,
                 "queue allowance omits bounded in-flight results/transport")
        _require(self.codec_mib * MIB >= self.workers * (self.task_bytes + self.result_bytes),
                 "codec allowance omits worker input/output copies")
        _require(self.task_bytes <= MAX_FILE_BYTES and self.result_bytes <= MAX_FILE_BYTES and
                 self.max_tasks <= 1_000_000, "task/record limits exceed bounded runtime")
        _require(self.max_tasks * 256 <= self.root_mib * MIB,
                 "root allowance omits bounded task identity tracking")
        _require(type(self.task_program) is ArtifactRef and type(self.provenance) is ArtifactRef,
                 "program/provenance bindings required")
        _require(self.pool_measurement is None or type(self.pool_measurement) is ArtifactRef,
                 "invalid pool measurement binding")
        _require(_NAME.fullmatch(self.task_function), "invalid task callable")
        _require(self.backend in ("integer-rational", "python-flint") and type(self.backend_version) is str
                 and self.backend_version, "unsupported role arithmetic backend")
        _require(self.scope in ("OPERATIONAL_CONTROL_ONLY", "SELECTION_ONLY", "SOURCE_EXPRESSIONS_ONLY"),
                 "unsupported execution scope")

    @property
    def owned_required_bytes(self):
        per_worker = self.worker_base_mib + self.worker_private_mib + self.native_workspace_mib + self.conversion_mib
        return (self.root_mib + self.workers * per_worker + self.codec_mib + self.queue_mib) * MIB

    @property
    def execution_id(self):
        return _sha(canonical_bytes(asdict(self)))

    @property
    def pool_context(self):
        value = asdict(self)
        for name in ("pool_measurement", "provenance"):
            value.pop(name)
        return _sha(canonical_bytes(value))

    def to_dict(self):
        return {"format": "whole-source-owned-execution-plan-v1", **asdict(self)}

    @classmethod
    def from_dict(cls, value):
        value = dict(value)
        _require(value.pop("format", None) == "whole-source-owned-execution-plan-v1", "unknown execution format")
        for name in ("task_program", "provenance", "pool_measurement"):
            if value.get(name) is not None:
                value[name] = ArtifactRef(**value[name])
        return cls(**value)


def exact_telemetry(value):
    """Encode finite operational floats without admitting floats into mathematics."""
    if type(value) is float:
        _require(value == value and abs(value) != float("inf"), "nonfinite resource telemetry")
        return {"hex_float": value.hex()}
    if type(value) is dict:
        return {key: exact_telemetry(item) for key, item in value.items()}
    if type(value) in (list, tuple):
        return [exact_telemetry(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class WorkloadBudget:
    execution_id: str
    cpu_budget: int
    workers: int
    native_threads: int
    owned_required_bytes: int
    owned_hard_cap_bytes: int
    existing_owned_bytes: int
    future_owned_bytes: int
    external_increment_bytes: int
    reserve_bytes: int
    repository_free_bytes: int
    temporary_free_bytes: int
    detected: dict
    single_root_resolver: dict

    def to_dict(self):
        return exact_telemetry(asdict(self))


def _bound(root, ref):
    path = Path(root) / ref.path
    _require(path.resolve().is_relative_to(Path(root).resolve()), "execution input escapes code root")
    raw = _bytes(path)
    _require(len(raw) == ref.size and _sha(raw) == ref.sha256, "execution input fingerprint mismatch")
    return raw


def detect_budget(plan, *, repository, temporary, helper_root=ROOT, existing_owned_bytes=0,
                  qualify_pool=False):
    """Separate a TOTAL job cap from future host demand and supervisor growth.

    existing_owned_bytes is measured inside the owned job, never guessed from a
    host-wide RSS snapshot. External admission uses zero for the not-yet-born job.
    """
    _require(type(plan) is ExecutionPlan, "scientific execution plan required")
    _positive(existing_owned_bytes, "existing owned commitment", 0)
    _require(existing_owned_bytes <= plan.owned_required_bytes, "existing job already exceeds its declared envelope")
    _require(plan.owned_required_bytes <= plan.memory_mib * MIB, "complete owned commitment exceeds job cap")
    if plan.workers > 1 and not qualify_pool:
        _require(plan.pool_measurement is not None, "pool requires its actual aggregate measurement")
        measurement = _json(_bound(helper_root, plan.pool_measurement))
        _require(measurement.get("format") == "whole-source-pool-observation-v1" and
                 measurement.get("pool_context") == plan.pool_context and
                 measurement.get("workers_observed") == plan.workers and
                 measurement.get("cleanup_verified") is True and
                 measurement.get("platform") == sys.platform and
                 measurement.get("scope") == "OPERATIONAL_CONTROL_ONLY" and
                 0 < measurement.get("peak_committed_bytes", 0) <= plan.owned_required_bytes,
                 "incompatible/unqualified aggregate pool measurement")
        receipt_raw = bytes.fromhex(measurement["receipt_hex"])
        _require(len(receipt_raw) <= MAX_FILE_BYTES and _sha(receipt_raw) == measurement["receipt_sha256"],
                 "pool receipt fingerprint mismatch")
        receipt = json.loads(receipt_raw)
        _require(receipt.get("worker_cleanup_verified") is True and receipt.get("exit_code") == 0 and
                 receipt.get("error") is None and
                 receipt.get("program_sha256") == _sha(_bytes(Path(helper_root) / "scripts/whole_source/execution.py")) and
                 receipt["budget"]["cpu_budget"] == plan.cpus and
                 receipt["budget"]["memory_budget_bytes"] == plan.memory_mib * MIB and
                 receipt["budget"]["descendant_pool_workers"] == plan.workers and
                 measurement.get("concurrent_workers_observed") == plan.workers,
                 "pool lacks its matching successful owned execution receipt")
    resources, _, _, _ = neutral_helpers(helper_root)
    future = plan.owned_required_bytes - existing_owned_bytes
    external = plan.supervisor_increment_mib * MIB
    # Every resolver option is explicit: legacy T081_* variables cannot select it.
    increment = max(1, future + external)
    resolved = resources.resolve_resources(cpus=plan.cpus, workers=1, threads=plan.threads,
        memory_mib=(increment + MIB - 1) // MIB, reserve_mib=plan.reserve_mib,
        required_bytes=increment)
    if os.name == "nt":
        logical = resolved["detection"]["logical_cpus"]
        rate = max(1, plan.cpus*10000//logical)
        _require(rate*logical <= plan.cpus*10000, "requested CPU cap is below Windows rate granularity")
    def free(path):
        path = Path(path).absolute()
        while not path.exists():
            path = path.parent
        _require(path.is_dir(), "volume probe must name a directory")
        return shutil.disk_usage(path).free, os.stat(path).st_dev
    repo_free, repo_device = free(repository)
    temp_free, temp_device = free(temporary)
    repo_need = (plan.repository_mib + plan.minimum_free_mib) * MIB
    temp_need = (plan.temporary_mib + plan.minimum_free_mib) * MIB
    if repo_device == temp_device:
        _require(repo_free >= (plan.repository_mib + plan.temporary_mib + plan.minimum_free_mib) * MIB,
                 "shared repository/temp volume allowance unavailable")
    else:
        _require(repo_free >= repo_need and temp_free >= temp_need, "repository/temp volume allowance unavailable")
    return WorkloadBudget(plan.execution_id, plan.cpus, plan.workers, plan.threads,
        plan.owned_required_bytes, plan.memory_mib * MIB, existing_owned_bytes, future, external,
        plan.reserve_mib * MIB, repo_free, temp_free, resolved["detection"], resolved)


class _Transport:
    """Bound the old supervisor's line reader/queue outside its owned job."""
    def __init__(self, cancelled, max_messages=16, max_characters=16384, log_bytes=MIB):
        self.cancelled = cancelled
        self.max_messages, self.max_characters = max_messages, max_characters
        self.max_log_bytes = log_bytes
        self.error = None
        self.peak_messages = 0
        self.log_bytes = 0
        self._guard = threading.Lock()

    def fail(self, message):
        self.error = message
        self.cancelled.set()

    def messages(self):
        transport = self
        class Messages(queue.Queue):
            def put(self, item, block=True, timeout=None):
                try:
                    super().put(item, block=False)
                    transport.peak_messages = max(transport.peak_messages, self.qsize())
                except queue.Full:
                    transport.fail("bounded supervisor message queue exhausted")
        return Messages(self.max_messages)

    def popen(self, *args, **kwargs):
        process = subprocess.Popen(*args, **kwargs)
        transport = self
        class Pipe:
            def __init__(self, stream):
                self.stream = stream
            def __iter__(self):
                try:
                    while True:
                        line = self.stream.readline(transport.max_characters + 1)
                        if not line:
                            break
                        size = len(line.encode("utf-8"))
                        with transport._guard:
                            transport.log_bytes += size
                        if len(line) > transport.max_characters or transport.log_bytes > transport.max_log_bytes:
                            transport.fail("bounded supervisor line/log allowance exhausted")
                            break
                        yield line
                finally:
                    self.stream.close()
        process.stdout, process.stderr = Pipe(process.stdout), Pipe(process.stderr)
        return process


def _provenance(root, ref):
    raw = _bound(root, ref)
    value = _json(raw)
    _require(value.get("format") == "whole-source-code-origin-v1" and
             type(value.get("origin_git_commit")) is str and
             re.fullmatch(r"[0-9a-f]{40}", value["origin_git_commit"]) and
             type(value.get("origin_git_dirty")) is bool and
             type(value.get("files")) is list and value["files"], "bound code origin required")
    seen = set()
    for row in value["files"]:
        entry = ArtifactRef(**row)
        _require(entry.path not in seen, "duplicate origin path")
        _bound(root, entry)
        seen.add(entry.path)
    _require(set(_RUNTIME).issubset(seen), "code origin omits runtime closure")
    return value


class WorkloadExecution:
    """Own the collection before the fresh attempt, then one contained root.

    Git fields describe the origin CLAIM in a raw-bound capture receipt. No Git
    command or current-checkout cleanliness inference is performed at runtime.
    """
    def __init__(self, collection_lock, spec, plan, *, code_root=ROOT, temporary=None,
                 qualify_pool=False, qualification_stop=None):
        self.collection_lock, self.spec, self.plan = collection_lock, spec, plan
        self.code_root = Path(code_root).resolve()
        self.temporary = Path(temporary or collection_lock.root).absolute()
        self.qualify_pool = qualify_pool
        from scripts.whole_source.artifacts import QUALIFICATION_POINTS
        _require(qualification_stop is None or qualification_stop in QUALIFICATION_POINTS,
                 "unknown process-interruption point")
        self.qualification_stop = qualification_stop
        self.receipts = []
        self.cancelled = threading.Event()
        self.backend = None
        self.lock = None
        self.output = None
        self.failure = None
        self._stage_lock = threading.Lock()

    def __enter__(self):
        _require(self.collection_lock.is_held and self.spec.collection_id == self.plan.collection_sha256 and
                 problem_id(self.spec.problem) == self.plan.problem_sha256 and self.spec.role == self.plan.role and
                 self.spec.native_threads == self.plan.threads and
                 self.spec.backend == self.plan.backend and self.spec.backend_version == self.plan.backend_version,
                 "execution/collection mismatch")
        bounds = self.spec.bounds
        resident = bounds.max_raw_bytes + 8*bounds.max_decoded_bytes
        resident += bounds.max_records * (4*((bounds.max_endpoint_bits+7)//8) + 1024)
        _require(self.plan.codec_mib*MIB >= self.plan.workers*resident and
                 self.plan.supervisor_increment_mib*MIB >= resident,
                 "codec/committer resident expansion omitted from resource account")
        self.origin = _provenance(self.code_root, self.plan.provenance)
        _require(self.plan.task_program in self.spec.code_refs and
                 asdict(self.plan.task_program) in self.origin["files"],
                 "task program omitted from collection/origin code binding")
        for ref in self.spec.code_refs:
            _require(asdict(ref) in self.origin["files"], "collection code differs from bound capture")
        role_bits = (self.spec.problem.arithmetic.audit_bits if self.plan.role == "analytic"
                     else self.spec.problem.arithmetic.source_bits)
        _require(self.plan.role == "exact" or self.plan.precision_bits == role_bits,
                 "native role precision differs from exact problem policy")
        self.budget = detect_budget(self.plan, repository=self.collection_lock.root,
            temporary=self.temporary, helper_root=self.code_root, qualify_pool=self.qualify_pool)
        self.attempt_id = uuid.uuid4().hex
        self.output = self.collection_lock.root / "attempts" / self.attempt_id
        self.output.parent.mkdir(exist_ok=True)
        self.lock = OutputDirectoryLock.acquire(self.output, command="whole-source-owned-execution-v1",
            support=str(self.spec.problem.support))
        try:
            context = {"format": "whole-source-attempt-context-v1", "problem_id": self.plan.problem_sha256,
                "collection_id": self.plan.collection_sha256, "execution_id": self.plan.execution_id,
                "arithmetic": asdict(self.spec.problem.arithmetic), "role": self.plan.role,
                "generation": self.collection_lock.generation, "attempt_id": self.attempt_id,
                "provenance": asdict(self.plan.provenance),
                "legacy_git_fields_scope": "bound capture origin claim, not current checkout state",
                "budget": self.budget.to_dict(), "scope": self.plan.scope}
            context_raw = canonical_bytes(context)
            write_run_identity(self.lock, driver_version="whole-source-owned-execution-v1:" + _sha(context_raw),
                dimensions=[self.spec.problem.N, self.spec.problem.M, self.spec.problem.K],
                git_commit=self.origin["origin_git_commit"], git_dirty=self.origin["origin_git_dirty"])
            self.writer = RunStatusWriter.start(self.output, command=self.lock.command,
                support=self.lock.support, output_lock=self.lock)
            _write(self.output / "attempt-context.json", context_raw)
            self.collection_lock.register_attempt(self.attempt_id)
            if self.qualification_stop is not None:
                _write(self.output / "qualification-barrier.json", canonical_bytes({
                    "point": self.qualification_stop, "scope": "PROCESS_INTERRUPTION_ONLY"}))
            resources, limits, supervisor, snapshots = neutral_helpers(self.code_root)
            self._limits = limits
            self._external_peak_increment = 0
            self._external_baseline = self._external_memory()
            self._resource_failure = None
            envelope = self.plan.max_tasks * (self.plan.task_bytes + self.plan.result_bytes + 1024)
            envelope += self.plan.log_bytes + sum(row["size"] for row in self.origin["files"])
            envelope += sum(len(raw) for _, raw in self.spec._snapshots)
            envelope += sum(len(raw) for raw in snapshots.values()) + MIB
            _require(envelope <= self.plan.repository_mib * MIB,
                     "repository allowance omits code/task/result/log overlap")
            self.runtime_root = self.output / "runtime"
            for ref, raw in self.spec._snapshots:
                _install(self.runtime_root, ref, raw)
            for row in self.origin["files"]:
                ref = ArtifactRef(**row)
                _install(self.runtime_root, ref, _bound(self.code_root, ref))
            for name, raw in snapshots.items():
                _install(self.runtime_root, ArtifactRef(BUNDLE + "/" + name, _sha(raw), len(raw)), raw)
            self.backend = supervisor.Execution(self.output, {}, root=self.runtime_root,
                worker=self.runtime_root / BUNDLE / "stage_worker_v1.py")
            # Do not invoke the legacy fixed-support __enter__ or mutate its identity.
            self.backend.lock, self.backend.writer = self.lock, self.writer
            self.backend.cancelled = self.cancelled
            self.backend.budget = {"cpu_budget": self.plan.cpus, "native_threads": self.plan.threads,
                "workers": 1, "memory_budget_bytes": self.budget.owned_hard_cap_bytes,
                "reserve_bytes": self.budget.reserve_bytes, "required_bytes": self.budget.owned_required_bytes,
                "descendant_pool_workers": self.plan.workers,
                "execution_mode": "one owned root plus bounded spawn descendants"}
            self.backend.config = self.output / "execution-budget.json"
            budget_raw = canonical_bytes(self.backend.budget)
            _write(self.backend.config, budget_raw)
            self.backend.config_sha = _sha(budget_raw)
            self._job_samples = []
            outer = self
            class ObservedJob(limits.WindowsJob):
                def attach_worker_pid(self, pid):
                    super().attach_worker_pid(pid)
                    # The qualified helper verifies membership against THIS held
                    # job handle. NULL-handle worker queries may name an ancestor.
                    ticket = {"format": "whole-source-owned-attachment-v1", "pid": pid,
                        "supervisor_pid": os.getpid(), "execution_id": outer.plan.execution_id,
                        "attempt_id": outer.attempt_id, "generation": outer.collection_lock.generation,
                        "stage_sha256": outer._active_stage_sha, "memory_bytes": self.memory_bytes,
                        "cpu_budget": self.cpu_budget, "verified_against_owned_job_handle": True}
                    _write(outer._attachment_path, canonical_bytes(ticket))
                def usage(self):
                    value = super().usage()
                    outer._sample_external()
                    value["owned_cpu_rate_units"] = self.cpu_rate
                    value["owned_cpu_rate_denominator"] = 10000
                    pids = frozenset(value.get("active_process_ids", ()))
                    if pids and not any(pids <= old for old in outer._job_samples):
                        outer._job_samples = [old for old in outer._job_samples if not old < pids]
                        if len(outer._job_samples) < 64:
                            outer._job_samples.append(pids)
                        else:
                            outer._resource_failure = "owned process sample envelope exceeded"
                            outer.cancelled.set()
                    return value
            supervisor.WindowsJob = ObservedJob
            self._transport = _Transport(self.cancelled, log_bytes=self.plan.log_bytes)
            supervisor.queue = types.SimpleNamespace(Queue=self._transport.messages, Empty=queue.Empty)
            supervisor.subprocess = types.SimpleNamespace(Popen=self._transport.popen,
                TimeoutExpired=subprocess.TimeoutExpired, PIPE=subprocess.PIPE)
            self.writer.event("RESOURCE_BUDGET", budget=self.budget.to_dict())
            return self
        except BaseException:
            self.collection_lock.invalidate_attempt(self.attempt_id)
            if self.lock:
                self.lock.release()
            raise

    def _external_memory(self):
        if os.name == "nt":
            sample = self._limits.windows_resource_snapshot()["process"]
            _require(sample is not None, "external supervisor memory is not visible")
            return sample["committed_bytes"]
        # Current resident pages, not the inherited lifetime high-water counter.
        return int(Path("/proc/self/statm").read_text().split()[1])*os.sysconf("SC_PAGE_SIZE")

    def _sample_external(self):
        try:
            increment = max(0, self._external_memory()-self._external_baseline)
        except (OSError, ValueError) as exc:
            self._resource_failure = "external supervisor visibility lost: " + str(exc)
            self.cancelled.set()
            return
        self._external_peak_increment = max(self._external_peak_increment, increment)
        if increment > self.plan.supervisor_increment_mib*MIB:
            self._resource_failure = "external supervisor growth exceeded its admitted increment"
            self.cancelled.set()

    def cancel_owned(self):
        self.cancelled.set()
        self.collection_lock.invalidate_attempt(self.attempt_id)

    cancel = cancel_owned

    def run_stage(self, name, tasks):
        """Reject concurrent roots; every task pool shares one selected budget."""
        _require(self._stage_lock.acquire(blocking=False), "only one owned stage may run at a time")
        try:
            self._job_samples = []
            return self._run_stage(name, tasks)
        except BaseException as exc:
            self.failure = exc
            self.collection_lock.invalidate_attempt(self.attempt_id)
            raise
        finally:
            self._stage_lock.release()

    def _validate_runtime_tree(self):
        """Allow only bound scientific inputs/code; no preinstalled fresh oracles."""
        allowed = {ref.path: ref for ref, _ in self.spec._snapshots}
        allowed.update({row["path"]: ArtifactRef(**row) for row in self.origin["files"]})
        for name, raw in neutral_helpers(self.code_root)[3].items():
            path = BUNDLE + "/" + name
            allowed[path] = ArtifactRef(path, _sha(raw), len(raw))
        seen = set()
        for folder, directories, names in os.walk(self.runtime_root, followlinks=False):
            for name in directories:
                path = Path(folder) / name
                _require(not path.is_symlink() and
                         not getattr(path.lstat(), "st_file_attributes", 0) & 0x400,
                         "unexpected reparse directory in captured runtime")
            for name in names:
                path = Path(folder) / name
                relative = path.relative_to(self.runtime_root).as_posix()
                _require(relative in allowed, "unbound file or expected-output oracle in captured runtime: " + relative)
                _bound(self.runtime_root, allowed[relative])
                seen.add(relative)
        _require(seen == set(allowed), "captured scientific runtime input is missing")

    def _run_stage(self, name, tasks):
        """Run bounded inputs and return the small completion inventory, not arrays."""
        _require(_NAME.fullmatch(name) and self.backend is not None and not self.cancelled.is_set(),
                 "inactive/invalid owned stage")
        self._validate_runtime_tree()
        # Repeat admission immediately before the new root exists.
        budget = detect_budget(self.plan, repository=self.collection_lock.root, temporary=self.temporary,
            helper_root=self.code_root, qualify_pool=self.qualify_pool)
        task_file = self.output / (name + "-tasks.jsonl")
        count = 0
        with task_file.open("xb") as stream:
            for task in tasks:
                raw = canonical_bytes(task)
                _require(len(raw) <= self.plan.task_bytes and count < self.plan.max_tasks,
                         "bounded task input allowance exceeded")
                _require(stream.write(raw) == len(raw), "short task spool write")
                count += 1
            stream.flush()
            os.fsync(stream.fileno())
        _require(count > 0, "empty stage cannot qualify work")
        program = self.plan.task_program
        _install(self.runtime_root, program, _bound(self.code_root, program))
        from scripts.whole_source.artifacts import ChunkStore
        staging = ChunkStore(self.collection_lock, self.spec, attempt_id=self.attempt_id).staging_context()
        config = {"format": "whole-source-task-stage-v1", "plan": self.plan.to_dict(),
            "task_file": str(task_file), "task_sha256": _file_digest(task_file),
            "task_count": count, "result_dir": str(self.output / (name + "-results")),
            "attempt_id": self.attempt_id, "generation": self.collection_lock.generation,
            "budget": budget.to_dict(), "collection": self.spec.to_dict(), "profile": self.spec.problem.profile,
            "artifact_context": {"root": str(staging.root), "generation": staging.generation,
                "attempt_id": staging.attempt_id, "receipt": asdict(staging.receipt),
                "index_head": None if staging.index_head is None else asdict(staging.index_head)}}
        self._attachment_path = self.output / (name+"-attachment.json")
        config["attachment_path"] = str(self._attachment_path)
        config_path = self.output / (name + "-stage.json")
        _write(config_path, canonical_bytes(config))
        self._active_stage_sha = _sha(canonical_bytes(config))
        try:
            self._sample_external()
            _require(self._resource_failure is None, "external supervisor no longer fits")
            receipt = self.backend.run(name, self.runtime_root / "scripts/whole_source/execution.py",
                ["--stage", str(config_path), "--stage-sha256", _sha(canonical_bytes(config))], kind="fixture",
                # Windows can omit sys.path[0] for a script beyond MAX_PATH.
                # Supply only the raw-bound helper directory, never ambient code.
                environment={"PYTHONPATH": str(self.runtime_root / BUNDLE)})
            self.receipts.append(receipt)
            complete = _json(_bytes(Path(config["result_dir"]) / "complete.json"))
            _require(complete["execution_id"] == self.plan.execution_id and complete["task_count"] == count,
                     "stage completion identity mismatch")
            _require(complete["peak_inflight"] <= self.plan.workers, "unbounded result prefetch")
            _require(receipt["worker_cleanup_verified"] is True, "owned cleanup missing")
            if self.qualify_pool:
                observation = {"format": "whole-source-pool-observation-v1",
                    "pool_context": self.plan.pool_context, "workers_observed": len(complete["worker_pids"]),
                    "cleanup_verified": True, "peak_committed_bytes": receipt["peak_budgeted_memory_bytes"],
                    "receipt_sha256": _sha(_bytes(self.output / name / "receipt.json")),
                    "receipt_hex": _bytes(self.output / name / "receipt.json").hex(),
                    "concurrent_workers_observed": max((len(set(complete["worker_pids"]) & pids)
                                                       for pids in self._job_samples), default=0),
                    "scope": "OPERATIONAL_CONTROL_ONLY", "platform": sys.platform}
                _require(observation["workers_observed"] == self.plan.workers and
                         observation["concurrent_workers_observed"] == self.plan.workers and
                         observation["peak_committed_bytes"] <= self.plan.owned_required_bytes,
                         "observed pool exceeded/failed declared aggregate profile")
                _write(self.output / (name + "-pool-observation.json"), canonical_bytes(observation))
            return complete
        except BaseException as exc:
            self.failure = exc
            self.collection_lock.invalidate_attempt(self.attempt_id)
            if self._resource_failure:
                raise MemoryError(self._resource_failure) from None
            if self._transport.error:
                raise RuntimeError(self._transport.error) from None
            raise
        finally:
            self._sample_external()
            retained = next((r for r in reversed(self.backend.receipts) if r["stage"] == name), None)
            if retained is not None:
                summary = {"format": "whole-source-operational-resources-v1", "stage": name,
                    "execution_id": self.plan.execution_id, "scope": "OPERATIONAL_CONTROL_ONLY",
                    "owned_peak_bytes": retained["peak_budgeted_memory_bytes"],
                    "owned_hard_cap_bytes": self.budget.owned_hard_cap_bytes,
                    "external_baseline_bytes": self._external_baseline,
                    "sampled_external_increment_bytes": self._external_peak_increment,
                    "external_increment_allowance_bytes": self.plan.supervisor_increment_mib*MIB,
                    "supervisor_peak_queue_messages": self._transport.peak_messages,
                    "supervisor_queue_message_cap": self._transport.max_messages,
                    "supervisor_line_character_cap": self._transport.max_characters,
                    "raw_log_bytes": self._transport.log_bytes,
                    "cleanup_verified": retained["worker_cleanup_verified"],
                    "resource_failure": self._resource_failure, "transport_failure": self._transport.error}
                _write(self.output / (name+"-resources.json"), canonical_bytes(summary))
            if self._resource_failure and self.failure is None:
                self.failure = MemoryError(self._resource_failure)
                self.collection_lock.invalidate_attempt(self.attempt_id)
                raise self.failure

    def read_results(self, name):
        """Consume the same bounded result bytes named by the completion inventory."""
        folder = self.output / (name + "-results")
        complete = _json(_bytes(folder / "complete.json"))
        _require(complete["execution_id"] == self.plan.execution_id and
                 _file_digest(folder / "completed.jsonl") == complete["inventory_sha256"],
                 "completion inventory changed")
        with (folder / "completed.jsonl").open("rb") as stream:
            for _ in range(complete["task_count"]):
                raw = stream.readline(2048)
                _require(raw.endswith(b"\n"), "completion row exceeds cap")
                row = _json(raw)
                ref = ArtifactRef(**{k: row[k] for k in ("path", "sha256", "size")})
                payload = _bound(folder, ref)
                _require(len(payload) <= self.plan.result_bytes, "result exceeds cap")
                value = _json(payload)
                _require(value["attempt_id"] == self.attempt_id and
                         value["generation"] == self.collection_lock.generation and
                         value["collection_id"] == self.spec.collection_id, "stale task result")
                yield value
            _require(not stream.read(1), "extra completion rows")

    def reduce_prefix(self, store, task, prior_ref, next_refs):
        """Run exact reduction in an owned slot, then publish under collection ownership."""
        from scripts.whole_source.artifacts import StagedPrefix
        refs = []
        for ref in next_refs:
            _require(len(refs) < self.spec.bounds.max_records, "prefix reference cap exceeded")
            refs.append(asdict(ref))
        request = {"operation": "reduce-prefix", "task": task.to_dict(),
                   "prior": None if prior_ref is None else asdict(prior_ref), "refs": refs}
        request["task_id"] = _sha(canonical_bytes(request))
        name = "reduce_" + uuid.uuid4().hex
        self.run_stage(name, [request])
        result = next(self.read_results(name))["result"]
        staged = StagedPrefix(Path(result["path"]), task, ArtifactRef(**result["ref"]),
            result["generation"], result["attempt_id"],
            None if result["index_head"] is None else ArtifactRef(**result["index_head"]))
        return store.publish_prefix(staged)

    def __exit__(self, kind, error, traceback):
        error = error if error is not None else self.failure
        kind = type(error) if error is not None else kind
        try:
            if error is not None:
                self.writer.record_failure("RUN_INTERRUPTED" if kind is KeyboardInterrupt else "RUN_FAILED", error)
            else:
                self.writer.update(workflow_state="RUN_COMPLETED", current_operation=None, terminal=True)
        finally:
            self.collection_lock.invalidate_attempt(self.attempt_id)
            if self.lock:
                self.lock.release()
        return False


_WORKER = None
_RESOURCES = None


def _require_owned_context(plan, resources, owned_session=None, attachment=None):
    """A budget document is not OS ownership. Refuse an uncontained caller."""
    current = resources.detect_resources()
    if os.name == "nt":
        parent = multiprocessing.parent_process()
        root_pid = os.getpid() if parent is None else parent.pid
        _require(type(attachment) is dict and
                 attachment.get("format") == "whole-source-owned-attachment-v1" and
                 attachment.get("verified_against_owned_job_handle") is True and
                 attachment.get("pid") == root_pid and
                 attachment.get("execution_id") == plan.execution_id and
                 attachment.get("memory_bytes") == plan.memory_mib*MIB and
                 attachment.get("cpu_budget") == plan.cpus and
                 current.get("windows", {}).get("job") is not None,
                 "owned memory job attachment is not bound before task imports")
    else:
        import resource
        soft, _ = resource.getrlimit(resource.RLIMIT_AS)
        _require(soft != resource.RLIM_INFINITY and soft <= plan.memory_mib*MIB and
                 os.getsid(0) == (os.getpid() if owned_session is None else owned_session),
                 "owned memory/session containment is not installed")
    return current


def worker_initialize(plan_document, root, result_dir, attempt_id, generation, collection, profile, artifact_context, owned_session, attachment):
    """Runs only in spawned descendants of the already-contained stage root."""
    global _WORKER, _RESOURCES
    plan = ExecutionPlan.from_dict(plan_document)
    _RESOURCES = neutral_helpers()[0]
    _require_owned_context(plan, _RESOURCES, owned_session, attachment)
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                "FLINT_NUM_THREADS"):
        os.environ[key] = str(plan.threads)
    if plan.backend == "python-flint":
        _require(importlib.metadata.version("python-flint") == plan.backend_version, "native backend version changed")
        from flint import ctx
        ctx.prec, ctx.threads = plan.precision_bits, plan.threads
    else:
        _require(plan.backend_version == "stdlib-v1", "integer/rational backend version changed")
    from scripts.whole_source.contract import bind_problem
    from scripts.whole_source.artifacts import CollectionSpec, StagingContext
    problem = bind_problem(profile, root=Path(root))
    spec = CollectionSpec.from_dict(problem, collection, code_root=Path(root))
    _require(spec.collection_id == plan.collection_sha256, "worker scientific collection changed")
    staging = StagingContext(Path(artifact_context["root"]), spec, artifact_context["generation"],
        artifact_context["attempt_id"], ArtifactRef(**artifact_context["receipt"]),
        None if artifact_context["index_head"] is None else ArtifactRef(**artifact_context["index_head"]))
    raw = _bound(root, plan.task_program)
    module = types.ModuleType("whole_source_task_program")
    module.__file__ = str(Path(root) / plan.task_program.path)
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    if plan.backend == "python-flint":
        ctx.prec, ctx.threads = plan.precision_bits, plan.threads
    function = getattr(module, plan.task_function)
    _require(callable(function), "task callable missing")
    _WORKER = (plan, function, Path(result_dir), attempt_id, generation, staging)


def admit_task(task, plan, *, detected=None):
    """Refresh only FUTURE task growth inside the already-live owned job.

    The root/pool base is already in availability snapshots. Total native/private
    envelopes remain in the outer owned-job cap; do not subtract that base twice.
    """
    _require(type(task) is dict and type(task.get("task_id")) is str and _HEX.fullmatch(task["task_id"]),
             "bound task identity required")
    _require(len(canonical_bytes(task)) <= plan.task_bytes, "task input exceeds cap")
    resources = _RESOURCES if _RESOURCES is not None else neutral_helpers()[0]
    current = resources.detect_resources() if detected is None else detected
    allowance = current["effective_cpu_budget"]
    if allowance < plan.workers*plan.threads and current.get("platform") == "win32":
        logical = current["logical_cpus"]
        selected_rate = max(1, plan.cpus*10000//logical)
        owned_quota = Fraction(selected_rate*logical, 10000)
        # Windows floors its job rate to 1/10000 of host CPU. Match ONLY that
        # known owned cap; never round up an arbitrary external quota/affinity.
        if (current.get("cpu_detection_complete") is True and
                current["affinity_cpus"] >= plan.cpus and
                current.get("quota_cpu_limit") is not None and
                Fraction(current["quota_cpu_limit"]) == owned_quota and
                0 <= plan.cpus-owned_quota < Fraction(logical, 10000)):
            allowance = plan.cpus
    _require(allowance >= plan.workers*plan.threads, "CPU allowance reduced before task")
    future = (plan.worker_private_mib + plan.native_workspace_mib + plan.conversion_mib) * MIB
    future += plan.task_bytes + plan.result_bytes
    available = current["available_memory_bytes"]
    _require(available is not None and available >= future + plan.reserve_mib * MIB,
             "future task growth/reserve exceeds current availability")
    return future


def execute_task(task):
    plan, function, result_dir, attempt_id, generation, staging = _WORKER
    admit_task(task, plan)
    if plan.backend == "python-flint":
        from flint import ctx
        ctx.prec, ctx.threads = plan.precision_bits, plan.threads
    started = time.monotonic()
    if task.get("operation") in ("reduce-prefix", "read-prefix"):
        from scripts.whole_source.artifacts import ContributionTask, Axis, _PrefixReader
        from scripts.whole_source.contract import ModeRange, QuantityKey
        wire = task["task"]
        domain = ContributionTask(QuantityKey.from_dict(wire["quantity"]), ModeRange(**wire["rows"]),
                                 ModeRange(**wire["columns"]), tuple(Axis(**a) for a in wire["axes"]))
        if task["operation"] == "read-prefix":
            current = _PrefixReader(staging).resume_prefix(domain)
            _require(current is not None, "no committed prefix to validate")
            result = {"prefix": asdict(current.ref), "covered": current.covered}
        else:
            staged = staging.stage_prefix(domain, None if task["prior"] is None else ArtifactRef(**task["prior"]),
                                          tuple(ArtifactRef(**r) for r in task["refs"]))
            result = {"path": str(staged.path), "ref": asdict(staged.ref), "generation": staged.generation,
                      "attempt_id": staged.attempt_id,
                      "index_head": None if staged.index_head is None else asdict(staged.index_head)}
    else:
        result = function(task, staging)
    if plan.backend == "python-flint":
        _require(ctx.prec == plan.precision_bits and ctx.threads == plan.threads,
                 "task changed its bound native arithmetic policy")
    raw = canonical_bytes({"format": "whole-source-staged-task-result-v1", "task_id": task["task_id"],
        "problem_id": plan.problem_sha256, "collection_id": plan.collection_sha256,
        "execution_id": plan.execution_id, "attempt_id": attempt_id, "generation": generation,
        "pid": os.getpid(), "result": result, "scope": plan.scope})
    _require(len(raw) <= plan.result_bytes, "task result exceeds bounded codec")
    path = result_dir / (task["task_id"] + ".json")
    _write(path, raw)
    return {"path": path.name, "sha256": _sha(raw), "size": len(raw), "pid": os.getpid(),
            "elapsed_milliseconds": int((time.monotonic() - started) * 1000)}


class TaskScheduler:
    """Completion-order observation, one pending result per admitted slot.

    Return/yield only bounded artifact references. Mathematical reducers consume
    their fixed contribution order, never this scheduling order.
    """
    def __init__(self, plan, budget, *, root, result_dir, attempt_id, generation, collection, profile, artifact_context):
        self.plan, self.budget, self.root = plan, budget, root
        self.result_dir, self.attempt_id, self.generation = Path(result_dir), attempt_id, generation
        self.collection, self.profile, self.artifact_context = collection, profile, artifact_context
        self.peak_inflight = 0
        self.worker_pids = set()

    def run(self, tasks):
        _require(type(self.plan) is ExecutionPlan and
                 self.budget.get("execution_id") == self.plan.execution_id,
                 "scheduler lacks its bound execution budget")
        _require_owned_context(self.plan, neutral_helpers(self.root)[0],
                               attachment=self.budget.get("owned_attachment"))
        self.result_dir.mkdir(exist_ok=False)
        iterator = iter(tasks)
        owned = []
        context = multiprocessing.get_context("spawn")
        try:
            with ProcessPoolExecutor(max_workers=self.plan.workers, mp_context=context,
                    initializer=worker_initialize, initargs=(self.plan.to_dict(), self.root,
                        str(self.result_dir), self.attempt_id, self.generation,
                        self.collection, self.profile, self.artifact_context,
                        os.getsid(0) if os.name == "posix" else None,
                        self.budget.get("owned_attachment"))) as executor:
                pending = {}
                exhausted = False
                while pending or not exhausted:
                    while not exhausted and len(pending) < self.plan.workers:
                        try:
                            task = next(iterator)
                        except StopIteration:
                            exhausted = True
                            break
                        future = executor.submit(execute_task, task)
                        pending[future] = task["task_id"]
                        for process in (executor._processes or {}).values():
                            if process not in owned:
                                owned.append(process)
                        self.peak_inflight = max(self.peak_inflight, len(pending))
                    if pending:
                        completed = next(as_completed(tuple(pending)))
                        task_id = pending.pop(completed)
                        result = completed.result()
                        _require(result["path"] == task_id + ".json", "staged task identity changed")
                        self.worker_pids.add(result["pid"])
                        yield result
        finally:
            # Only executor-captured processes, never active_children ownership.
            for process in owned:
                process.join(timeout=.2)
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=2)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=2)
                _require(not process.is_alive(), "owned pool worker survived shutdown")


def _task_lines(path, plan, expected_sha256):
    seen = set()
    count = 0
    consumed = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while True:
            raw = stream.readline(plan.task_bytes + 1)
            if not raw:
                break
            _require(len(raw) <= plan.task_bytes and raw.endswith(b"\n"), "oversized/incomplete task spool")
            consumed.update(raw)
            task = _json(raw)
            _require(task.get("task_id") not in seen and count < plan.max_tasks, "duplicate/too many tasks")
            seen.add(task.get("task_id"))
            count += 1
            yield task
    _require(consumed.hexdigest() == expected_sha256, "consumed task spool changed")


def main():
    if __name__ != "scripts.whole_source.execution":
        from scripts.whole_source.execution import main as canonical_main
        return canonical_main()
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--stage-sha256", required=True)
    args = parser.parse_args()
    raw = _bytes(args.stage)
    _require(_sha(raw) == args.stage_sha256, "stage configuration changed")
    config = _json(raw)
    plan = ExecutionPlan.from_dict(config["plan"])
    if os.name == "nt":
        attachment = _json(_bytes(Path(config["attachment_path"])))
        _require(attachment.get("stage_sha256") == args.stage_sha256 and
                 attachment.get("attempt_id") == config["attempt_id"] and
                 attachment.get("generation") == config["generation"],
                 "owned attachment belongs to another stage/attempt")
        config["budget"]["owned_attachment"] = attachment
    # Hash the spool in fixed bounded blocks; do not load all tasks into memory.
    digest = hashlib.sha256()
    with Path(config["task_file"]).open("rb") as stream:
        while block := stream.read(65536):
            digest.update(block)
    _require(digest.hexdigest() == config["task_sha256"], "task spool changed")
    scheduler = TaskScheduler(plan, config["budget"], root=ROOT, result_dir=config["result_dir"],
        attempt_id=config["attempt_id"], generation=config["generation"], collection=config["collection"],
        profile=config["profile"], artifact_context=config["artifact_context"])
    inventory = Path(config["result_dir"]) / "completed.jsonl"
    count = 0
    # Directory is created by the actual scheduler before its first result.
    handle = None
    try:
        for result in scheduler.run(_task_lines(config["task_file"], plan, config["task_sha256"])):
            if handle is None:
                handle = inventory.open("xb")
            row = canonical_bytes(result)
            _require(handle.write(row) == len(row), "short completion inventory write")
            count += 1
            print("T081_EVENT " + json.dumps({"event": "work", "phase": "owned_tasks",
                  "completed": count, "total": config["task_count"], "unit": "bounded task"}), flush=True)
        if handle:
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        if handle:
            handle.close()
    _require(count == config["task_count"], "stage task coverage incomplete")
    complete = {"format": "whole-source-task-stage-completion-v1", "execution_id": plan.execution_id,
        "task_count": count, "peak_inflight": scheduler.peak_inflight,
        "worker_pids": sorted(scheduler.worker_pids), "scope": "OPERATIONAL_CONTROL_ONLY",
        "inventory_sha256": _file_digest(inventory),
        "mathematical_verification": False, "positivity_proved": False}
    _write(Path(config["result_dir"]) / "complete.json", canonical_bytes(complete))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
