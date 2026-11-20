"""Bounded exact artifacts and single-writer structural collection receipts.

These receipts establish byte identity and declared coverage only. They do not
establish analytical correctness, matrix positivity, or production admission.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from fractions import Fraction
import errno
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import uuid
import time
from typing import Iterable, Iterator

from .contract import (
    ROOT, ArtifactRef, ContractError, ModeRange, ProblemSpec, QuantityKey,
    canonical_bytes, expected_domain, problem_id, quantity_document, validate_problem,
)
from scripts.run_observability import replace_path_with_permission_retry


class ArtifactError(ContractError):
    """An artifact violates its bound structural or ownership contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactError(message)


def _int(value: object, minimum: int, maximum: int, label: str) -> int:
    _require(type(value) is int and minimum <= value <= maximum, "invalid " + label)
    return value


def _hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _id(value: object) -> str:
    return _hash(canonical_bytes(value))


def _name(value: str) -> str:
    _require(type(value) is str and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", value) is not None,
             "invalid owned name")
    return value


def _relative(value: str) -> str:
    _require(type(value) is str and value and "\\" not in value and ":" not in value,
             "invalid relative path")
    path = PurePosixPath(value)
    _require(not path.is_absolute() and str(path) == value and
             all(part not in (".", "..") for part in path.parts), "ambiguous artifact path")
    return value


def _root_path(root: Path, *, missing: bool = False) -> None:
    for path in reversed((root, *root.parents)):
        try:
            info = path.lstat()
        except FileNotFoundError:
            _require(missing, "missing collection root")
            return
        _require(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode) and
                 not getattr(info, "st_file_attributes", 0) & 0x400, "reparse/symlink collection ancestor")


def _safe(root: Path, relative: str, *, missing: bool = False) -> Path:
    _relative(relative)
    _root_path(root)
    path = root
    root_info = root.lstat()
    _require(stat.S_ISDIR(root_info.st_mode) and not root.is_symlink() and
             not getattr(root_info, "st_file_attributes", 0) & 0x400, "unsafe collection root")
    for part in relative.split("/"):
        path = path / part
        try:
            info = path.lstat()
        except FileNotFoundError:
            _require(missing and path.parent.is_dir(), "missing artifact parent")
            return path
        _require(not stat.S_ISLNK(info.st_mode) and
                 not getattr(info, "st_file_attributes", 0) & 0x400, "reparse/symlink artifact path")
    _require(path.resolve().is_relative_to(root.resolve()), "artifact escapes collection")
    return path


def _raw(root: Path, ref: ArtifactRef, cap: int) -> bytes:
    _require(type(ref) is ArtifactRef and ref.size <= cap, "raw artifact exceeds cap")
    path = _safe(root, ref.path)
    before = path.stat()
    _require(stat.S_ISREG(before.st_mode) and before.st_size == ref.size, "invalid regular artifact")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        _require((opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino), "artifact changed during open")
        raw = stream.read(cap + 1)
    _require(len(raw) == ref.size and _hash(raw) == ref.sha256, "artifact fingerprint mismatch")
    return raw


def _unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        _require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def _number(text: str) -> int:
    _require(len(text) <= 17, "oversized JSON integer")
    return int(text)


def _bad_number(text: str) -> None:
    raise ArtifactError("nonexact JSON number")


def _json(raw: bytes, cap: int) -> dict | list:
    _require(len(raw) <= cap, "JSON exceeds cap")
    try:
        value = json.loads(raw, object_pairs_hook=_unique, parse_int=_number,
                           parse_float=_bad_number, parse_constant=_bad_number)
        _require(type(value) in (dict, list) and canonical_bytes(value) == raw, "noncanonical JSON")
        return value
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ArtifactError("invalid canonical JSON") from exc


def encode_integer(value: int, max_bits: int) -> str:
    _require(type(value) is int and abs(value).bit_length() <= max_bits, "endpoint bit cap exceeded")
    return hex(value)


def decode_integer(value: str, max_bits: int) -> int:
    _require(type(value) is str and len(value) <= (max_bits + 3)//4 + 3 and
             re.fullmatch(r"-?0x(?:0|[1-9a-f][0-9a-f]*)", value) is not None and value != "-0x0",
             "noncanonical hexadecimal integer")
    result = int(value, 16)
    _require(abs(result).bit_length() <= max_bits, "endpoint bit cap exceeded")
    return result


def encode_rational(value: Fraction, max_bits: int) -> dict:
    _require(type(value) is Fraction, "exact rational required")
    return {"numerator": encode_integer(value.numerator, max_bits),
            "denominator": encode_integer(value.denominator, max_bits)}


def decode_rational(value: dict, max_bits: int) -> Fraction:
    _require(type(value) is dict and set(value) == {"numerator", "denominator"}, "invalid rational")
    numerator = decode_integer(value["numerator"], max_bits)
    denominator = decode_integer(value["denominator"], max_bits)
    _require(denominator > 0, "nonpositive denominator")
    result = Fraction(numerator, denominator)
    _require(result.numerator == numerator and result.denominator == denominator, "noncanonical rational")
    return result


@dataclass(frozen=True, slots=True)
class CodecBounds:
    max_raw_bytes: int
    max_compressed_bytes: int
    max_decoded_bytes: int
    max_records: int
    max_endpoint_bits: int
    max_header_bytes: int
    max_record_bytes: int
    max_total_bytes: int
    max_temporary_bytes: int
    max_snapshot_bytes: int

    def __post_init__(self) -> None:
        for key in self.__dataclass_fields__:
            _int(getattr(self, key), 1, 1 << 50, key)
        _require(self.max_raw_bytes <= 8*1024*1024 and
                 self.max_compressed_bytes <= self.max_raw_bytes and
                 self.max_header_bytes <= self.max_raw_bytes and
                 self.max_record_bytes <= self.max_decoded_bytes and
                 self.max_endpoint_bits <= 1_000_000, "inconsistent codec caps")


@dataclass(frozen=True, slots=True)
class Axis:
    name: str
    start: int
    stop: int
    step: int = 1

    def __post_init__(self) -> None:
        _name(self.name)
        _int(self.start, 0, 1_000_000, "axis start")
        _int(self.stop, 1, 1_000_001, "axis stop")
        _int(self.step, 1, 1_000_000, "axis step")
        _require(self.start < self.stop, "empty axis")

    def __iter__(self) -> Iterator[int]:
        return iter(range(self.start, self.stop, self.step))

    def __len__(self) -> int:
        return len(range(self.start, self.stop, self.step))


def _subset(actual: ModeRange | Axis, expected: ModeRange | Axis) -> bool:
    return (actual.start >= expected.start and actual.stop <= expected.stop and
            actual.step == expected.step and (actual.start - expected.start) % expected.step == 0 and
            (actual.stop == expected.stop or (actual.stop - expected.start) % expected.step == 0))


def _axis_document(axis: Axis) -> dict:
    return {"name": axis.name, "start": axis.start, "stop": axis.stop, "step": axis.step}


def _range_document(value: ModeRange) -> dict:
    return {"start": value.start, "stop": value.stop, "step": value.step}


@dataclass(frozen=True, slots=True)
class QuantitySpec:
    key: QuantityKey
    rows: ModeRange
    columns: ModeRange
    symmetric_upper: bool
    axes: tuple[Axis, ...]
    scope: str = "DECLARED_SLICE"

    def __post_init__(self) -> None:
        _require(type(self.key) is QuantityKey and type(self.rows) is ModeRange and
                 type(self.columns) is ModeRange and type(self.symmetric_upper) is bool,
                 "invalid quantity domain")
        _require(type(self.axes) is tuple and all(type(a) is Axis for a in self.axes) and
                 len({a.name for a in self.axes}) == len(self.axes) and len(self.axes) <= 16,
                 "invalid frozen contribution axes")
        _require(self.scope in ("DECLARED_SLICE", "FULL_QUANTITY"), "invalid quantity scope")

    def to_dict(self) -> dict:
        return {"quantity": quantity_document(self.key),
                "rows": _range_document(self.rows), "columns": _range_document(self.columns),
                "symmetric_upper": self.symmetric_upper,
                "axes": [_axis_document(a) for a in self.axes], "scope": self.scope}


@dataclass(frozen=True, slots=True)
class CollectionSpec:
    problem: ProblemSpec
    role: str
    quantities: tuple[QuantitySpec, ...]
    partition: tuple[tuple[str, int], ...]
    backend: str
    backend_version: str
    native_threads: int
    code_refs: tuple[ArtifactRef, ...]
    bounds: CodecBounds
    grid_bits: int
    _snapshots: tuple[tuple[ArtifactRef, bytes], ...] = field(repr=False)
    _identity: str | None = field(default=None, init=False, repr=False, compare=False)

    @classmethod
    def create(cls, problem: ProblemSpec, *, role: str,
               quantities: tuple[QuantitySpec, ...], partition: tuple[tuple[str, int], ...],
               backend: str, backend_version: str, native_threads: int,
               code_refs: tuple[ArtifactRef, ...], bounds: CodecBounds,
               code_root: Path = ROOT, grid_bits: int | None = None) -> CollectionSpec:
        validate_problem(problem)
        _require(type(bounds) is CodecBounds and type(code_refs) is tuple and code_refs,
                 "explicit code closure and codec bounds required")
        root = Path(code_root).resolve()
        refs = {ref.path: ref for ref in problem.evidence}
        for ref in code_refs:
            _require(type(ref) is ArtifactRef and (ref.path not in refs or refs[ref.path] == ref),
                     "conflicting implementation reference")
            refs[ref.path] = ref
        total = sum(ref.size for ref in refs.values())
        _require(total <= bounds.max_snapshot_bytes, "input snapshot volume exceeds cap")
        frozen = tuple((ref, _raw(root, ref, 8*1024*1024)) for ref in sorted(refs.values(), key=lambda r: r.path))
        result = cls(problem, role, quantities, partition, backend, backend_version,
                     native_threads, code_refs, bounds,
                     problem.arithmetic.checkpoint_bits if grid_bits is None else grid_bits, frozen)
        result._validate()
        return result

    @classmethod
    def from_dict(cls, problem: ProblemSpec, document: dict, *, code_root: Path = ROOT) -> CollectionSpec:
        """Rebind a bounded wire description to actual captured input/code bytes."""
        _require(type(document) is dict and type(document.get("quantities")) is list and
                 0 < len(document["quantities"]) <= 16 and type(document.get("partition")) is list and
                 type(document.get("code_refs")) is list and type(document.get("bounds")) is dict,
                 "invalid collection description")
        try:
            quantities = []
            for row in document["quantities"]:
                _require(type(row) is dict and set(row) == {"quantity", "rows", "columns", "symmetric_upper", "axes", "scope"} and
                         type(row["axes"]) is list, "invalid quantity description")
                quantities.append(QuantitySpec(
                    QuantityKey.from_dict(row["quantity"]), ModeRange(**row["rows"]), ModeRange(**row["columns"]),
                    row["symmetric_upper"], tuple(Axis(**axis) for axis in row["axes"]), row["scope"]))
            result = cls.create(
                problem, role=document["role"], quantities=tuple(quantities),
                partition=tuple(tuple(pair) for pair in document["partition"]),
                backend=document["backend"], backend_version=document["backend_version"],
                native_threads=document["native_threads"],
                code_refs=tuple(_ref(ref) for ref in document["code_refs"]),
                bounds=CodecBounds(**document["bounds"]), grid_bits=document["grid_bits"], code_root=code_root)
        except (TypeError, KeyError) as exc:
            raise ArtifactError("invalid collection description fields") from exc
        _require(canonical_bytes(result.to_dict()) == canonical_bytes(document),
                 "unsupported collection format, fields, or arithmetic policy")
        return result

    def _validate(self) -> None:
        _require(type(self.problem) is ProblemSpec and self.role in ("producer", "analytic", "exact"),
                 "scientific collection specification required")
        _require(type(self.bounds) is CodecBounds and type(self.quantities) is tuple and
                 0 < len(self.quantities) <= 16 and all(type(q) is QuantitySpec for q in self.quantities) and
                 len({q.key for q in self.quantities}) == len(self.quantities), "invalid quantity collection")
        _int(self.native_threads, 1, 1_000_000, "native threads")
        _int(self.grid_bits, 1, self.bounds.max_endpoint_bits, "grid bits")
        _require(type(self.backend) is str and 0 < len(self.backend) <= 256 and
                 type(self.backend_version) is str and 0 < len(self.backend_version) <= 256,
                 "explicit backend and version required")
        _require(type(self.partition) is tuple and self.partition and
                 all(type(p) is tuple and len(p) == 2 and type(p[0]) is str and
                     type(p[1]) is int and 0 < p[1] <= 1_000_000 for p in self.partition) and
                 tuple(sorted(self.partition)) == self.partition and
                 len({p[0] for p in self.partition}) == len(self.partition), "invalid canonical partition")
        _require(type(self.code_refs) is tuple and self.code_refs and
                 tuple(sorted(self.code_refs, key=lambda r: r.path)) == self.code_refs and
                 len({r.path for r in self.code_refs}) == len(self.code_refs), "invalid code closure")
        _require({"scripts/whole_source/__init__.py", "scripts/whole_source/artifacts.py",
                  "scripts/whole_source/contract.py", "scripts/run_observability.py"} <=
                 {r.path for r in self.code_refs}, "missing artifact implementation closure")
        _require(type(self._snapshots) is tuple and self._snapshots and
                 all(type(raw) is bytes and len(raw) == ref.size and _hash(raw) == ref.sha256
                     for ref, raw in self._snapshots), "incomplete bound snapshots")
        needed = {r.path: r for r in self.problem.evidence + self.code_refs}
        _require({ref.path: ref for ref, _ in self._snapshots} == needed, "incomplete snapshot closure")
        _require(sum(len(raw) for _, raw in self._snapshots) <= self.bounds.max_snapshot_bytes,
                 "snapshot cap exceeded")
        for quantity in self.quantities:
            domain = expected_domain(self.problem, quantity.key)
            _require(_subset(quantity.rows, domain.rows) and _subset(quantity.columns, domain.columns) and
                     quantity.symmetric_upper == domain.symmetric_upper, "quantity outside physical domain")
            _require(quantity.key.entry is None or quantity.scope == "DECLARED_SLICE",
                     "a selected arithmetic entry is not a complete matrix")
            if quantity.scope == "FULL_QUANTITY":
                _require(quantity.rows == domain.rows and quantity.columns == domain.columns,
                         "full quantity cannot be a physical slice")
            required = ("head_left", "head_right") if domain.head_inner_axes == 2 else (
                ("head",) if domain.head_inner_axes == 1 else ())
            for name in required:
                axis = next((a for a in quantity.axes if a.name == name), None)
                _require(axis == Axis(name, self.problem.N + quantity.key.parity, self.problem.M, 2),
                         "complete physical head axis required")
            names = {"rows", "columns"} | {a.name for a in quantity.axes}
            _require(names <= {p[0] for p in self.partition}, "partition missing scientific axis")

    @property
    def collection_id(self) -> str:
        if self._identity is None:
            object.__setattr__(self, "_identity", _id(self.to_dict()))
        return self._identity

    def to_dict(self) -> dict:
        return {"format": "whole-source-collection-v1", "problem_sha256": problem_id(self.problem),
                "role": self.role, "quantities": [q.to_dict() for q in self.quantities],
                "partition": [list(p) for p in self.partition], "backend": self.backend,
                "backend_version": self.backend_version, "native_threads": self.native_threads,
                "code_refs": [_ref_document(r) for r in self.code_refs],
                "bounds": {k: getattr(self.bounds, k) for k in self.bounds.__dataclass_fields__},
                "grid_bits": self.grid_bits, "endpoint_codec": "signed-hex-dyadic-v1",
                "reduction": "canonical-domain-order-outward-each-contribution-v1",
                "checkpoint_rounding": "floor-minus-one/ceil-plus-one",
                "durability": "file-flush-fsync-and-manifest-last;no-power-loss-guarantee",
                "resume_trust": "STRUCTURAL_ONLY_REQUIRES_INDEPENDENT_ANALYTICAL_CHECK",
                "scope": "STRUCTURAL_ONLY", "analytical_acceptance": False,
                "matrix_positivity": False, "production_admission": False}

    def quantity(self, key: QuantityKey) -> QuantitySpec:
        result = next((q for q in self.quantities if q.key == key), None)
        _require(result is not None, "quantity not bound to collection")
        return result


def _ref_document(ref: ArtifactRef | None) -> dict | None:
    return None if ref is None else {"path": ref.path, "sha256": ref.sha256, "size": ref.size}


def _ref(value: dict) -> ArtifactRef:
    _require(type(value) is dict and set(value) == {"path", "sha256", "size"}, "invalid artifact reference")
    return ArtifactRef(**value)


def _os_lock(stream, acquire: bool, *, blocking: bool = False) -> None:
    if os.name == "nt":
        import msvcrt
        stream.seek(4096)
        mode = (msvcrt.LK_LOCK if blocking else msvcrt.LK_NBLCK) if acquire else msvcrt.LK_UNLCK
        msvcrt.locking(stream.fileno(), mode, 1)
    else:
        import fcntl
        fcntl.flock(stream.fileno(), (fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB)) if acquire else fcntl.LOCK_UN)


def _write_all(stream, raw: bytes) -> None:
    written = stream.write(raw)
    if written != len(raw):
        raise OSError(errno.ENOSPC, "short artifact write")


def _sync_directory(path: Path) -> None:
    # Windows does not expose a portable directory-fsync primitive in stdlib.
    if os.name != "nt":
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

QUALIFICATION_POINTS = (
    "payload-writing", "payload-closed", "chunk-published", "index-writing",
    "prefix-committed", "prefix-acknowledgement", "slice-before-seal", "native-running",
)


def qualification_barrier(root: Path, attempt_id: str, point: str, *, flush=None) -> None:
    """Pause the actual writer at an explicit attempt-local interruption barrier.

    A flushed marker, not elapsed time, authorizes the external qualification
    process to release or terminate the writer. This is not mathematical input.
    """
    _require(point in QUALIFICATION_POINTS, "unknown qualification point")
    directory = _safe(root, "attempts/" + _name(attempt_id))
    control = directory / "qualification-barrier.json"
    if not control.exists():
        return
    with control.open("rb") as stream:
        document = _json(stream.read(4097), 4096)
    _require(type(document) is dict and set(document) == {"point", "scope"} and
             document["scope"] == "PROCESS_INTERRUPTION_ONLY" and
             document["point"] in QUALIFICATION_POINTS, "invalid qualification barrier")
    if document["point"] != point:
        return
    marker = directory / "barrier-reached.json"
    if marker.exists():
        return
    if flush is not None:
        flush()
    raw = canonical_bytes({"point": point, "pid": os.getpid(), "attempt_id": attempt_id,
                           "scope": "PROCESS_INTERRUPTION_ONLY"})
    with marker.open("xb") as stream:
        _write_all(stream, raw)
        stream.flush()
        os.fsync(stream.fileno())
    while not (directory / "barrier-release").exists():
        time.sleep(0.01)

def _members(root: Path) -> Iterator[tuple[Path, os.stat_result]]:
    with os.scandir(root) as entries:
        for entry in entries:
            info = entry.stat(follow_symlinks=False)
            _require(not stat.S_ISLNK(info.st_mode) and
                     not getattr(info, "st_file_attributes", 0) & 0x400, "unsafe volume member")
            path = Path(entry.path)
            if stat.S_ISDIR(info.st_mode):
                yield from _members(path)
            else:
                _require(stat.S_ISREG(info.st_mode), "nonregular volume member")
                yield path, info


def _volume(root: Path) -> int:
    return sum(info.st_size for _, info in _members(root))


class CollectionLock:
    """Stable-inode OS ownership, independent of fresh per-attempt runtime locks."""

    def __init__(self, root: Path, spec: CollectionSpec, stream) -> None:
        self.root, self.spec, self._stream = root, spec, stream
        self.generation = uuid.uuid4().hex
        self._pid = os.getpid()
        self._held = True
        self._attempts: dict[str, ArtifactRef] = {}
        self._manifest: dict = {}

    @property
    def is_held(self) -> bool:
        return self._held and self._pid == os.getpid()

    @classmethod
    def acquire(cls, root: Path, spec: CollectionSpec, *, resume: bool = False) -> CollectionLock:
        _require(type(spec) is CollectionSpec, "inspection plans do not authorize collections")
        spec._validate()
        root = Path(root).absolute()
        _root_path(root, missing=True)
        root.mkdir(parents=True, exist_ok=True)
        _safe(root, ".collection.lock", missing=True)
        path = root / ".collection.lock"
        if not path.exists():
            _require(not any(root.iterdir()), "fresh collection requires unused directory")
        stream = os.fdopen(os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600), "r+b")
        lock = cls(root, spec, stream)
        acquired = False
        try:
            try:
                _os_lock(stream, True)
                acquired = True
            except OSError as exc:
                raise ArtifactError("collection already owned") from exc
            _require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "nonregular lock file")
            if resume:
                lock._load_manifest()
                lock._validate_snapshots()
                lock._validate_log()
            else:
                _require(all(p.name == ".collection.lock" for p in root.iterdir()),
                         "fresh collection requires unused directory")
                with (root / ".volume.lock").open("xb"):
                    pass
                for name in ("snapshots", "chunks", "prefixes", "index", "seals", "attempts"):
                    (root / name).mkdir()
                for ref, raw in spec._snapshots:
                    lock._immutable("snapshots", raw)
                lock._manifest = {"format": "whole-source-collection-state-v1", "collection": spec.to_dict(),
                                  "collection_id": spec.collection_id, "index": None,
                                  "scope": "STRUCTURAL_ONLY"}
                lock._commit_manifest(lock._manifest)
            metadata = canonical_bytes({"collection_id": spec.collection_id, "generation": lock.generation,
                                        "pid": os.getpid()})
            _require(len(metadata) < 4096, "lock metadata cap exceeded")
            stream.seek(0)
            _write_all(stream, metadata)
            stream.flush()
            os.fsync(stream.fileno())
            return lock
        except BaseException:
            if acquired:
                _os_lock(stream, False)
            lock._held = False
            stream.close()
            raise

    def _check(self, generation: str | None = None, attempt_id: str | None = None) -> None:
        _require(self.is_held and (generation is None or generation == self.generation), "stale collection ownership")
        held = os.fstat(self._stream.fileno())
        current = _safe(self.root, ".collection.lock").stat()
        _require((held.st_dev, held.st_ino) == (current.st_dev, current.st_ino), "lock inode replaced")
        if attempt_id is not None:
            _require(attempt_id in self._attempts, "attempt not registered or invalidated")
            _raw(self.root, self._attempts[attempt_id], self.spec.bounds.max_header_bytes)

    def register_attempt(self, attempt_id: str) -> None:
        self._check()
        _name(attempt_id)
        _require(attempt_id not in self._attempts, "attempt already registered")
        path = _safe(self.root, "attempts/" + attempt_id)
        _require(path.is_dir(), "fresh runtime attempt directory required")
        _require(not any((path / name).exists() for name in ("artifact-owner.json", "staging", "completions")),
                 "attempt has prior artifact ownership")
        (path / "staging").mkdir()
        (path / "completions").mkdir()
        raw = canonical_bytes({"format": "whole-source-local-attempt-v1", "attempt_id": attempt_id,
                               "generation": self.generation, "collection_id": self.spec.collection_id,
                               "pid": self._pid, "scope": "STRUCTURAL_ONLY"})
        ref = self._exclusive("attempts/" + attempt_id + "/artifact-owner.json", raw)
        self._attempts[attempt_id] = ref

    def invalidate_attempt(self, attempt_id: str | None = None) -> None:
        self._check()
        names = tuple(self._attempts) if attempt_id is None else (attempt_id,)
        for name in names:
            if name in self._attempts:
                self._attempts.pop(name)
                self._exclusive("attempts/" + name + "/artifact-invalidated", b"invalidated\n")

    def _quota(self, additional: int, temporary: int = 0) -> None:
        _check_quota(self.root, self.spec.bounds, additional, temporary)

    def _exclusive(self, relative: str, raw: bytes, *, barrier: str | None = None,
                   attempt_id: str | None = None) -> ArtifactRef:
        self._check()
        _require(len(raw) <= self.spec.bounds.max_raw_bytes, "artifact exceeds raw cap")
        with _volume_gate(self.root):
            self._quota(len(raw), len(raw))
            path = _safe(self.root, relative, missing=True)
            with path.open("xb") as stream:
                if barrier is None:
                    _write_all(stream, raw)
                else:
                    split = max(1, len(raw)//2)
                    _write_all(stream, raw[:split])
                    stream.flush()
                    os.fsync(stream.fileno())
                    qualification_barrier(self.root, attempt_id, barrier)
                    _write_all(stream, raw[split:])
                stream.flush()
                os.fsync(stream.fileno())
        _sync_directory(path.parent)
        return ArtifactRef(relative, _hash(raw), len(raw))

    def _immutable(self, family: str, raw: bytes, *, barrier: str | None = None,
                   attempt_id: str | None = None) -> ArtifactRef:
        relative = family + "/" + _hash(raw)
        ref = ArtifactRef(relative, _hash(raw), len(raw))
        if (self.root / relative).exists():
            _raw(self.root, ref, self.spec.bounds.max_raw_bytes)
            return ref
        temporary = family + "/.pending-" + uuid.uuid4().hex
        self._exclusive(temporary, raw, barrier=barrier, attempt_id=attempt_id)
        self._check()
        replace_path_with_permission_retry(self.root / temporary, self.root / relative)
        _sync_directory(self.root / family)
        return ref

    def _commit_manifest(self, state: dict) -> None:
        self._check()
        raw = canonical_bytes(state)
        _require(len(raw) <= self.spec.bounds.max_header_bytes, "manifest header cap exceeded")
        relative = "index/.manifest-" + uuid.uuid4().hex
        self._exclusive(relative, raw)
        self._check()
        # All fallible durability work precedes the final publication syscall.
        # Directory-entry survival across power loss is not promised.
        _sync_directory(self.root)
        replace_path_with_permission_retry(self.root / relative, self.root / "collection.json")
        self._manifest = state

    def _load_manifest(self) -> None:
        path = _safe(self.root, "collection.json")
        _require(stat.S_ISREG(path.stat().st_mode), "nonregular manifest")
        cap = self.spec.bounds.max_header_bytes
        with path.open("rb") as stream:
            raw = stream.read(cap + 1)
        state = _json(raw, cap)
        _require(type(state) is dict and set(state) == {"format", "collection", "collection_id", "index", "scope"} and
                 state["format"] == "whole-source-collection-state-v1" and state["scope"] == "STRUCTURAL_ONLY" and
                 canonical_bytes(state["collection"]) == canonical_bytes(self.spec.to_dict()) and
                 state["collection_id"] == self.spec.collection_id,
                 "incompatible collection manifest")
        self._manifest = state

    def _validate_snapshots(self) -> None:
        for ref, raw in self.spec._snapshots:
            local = ArtifactRef("snapshots/" + ref.sha256, ref.sha256, ref.size)
            _require(_raw(self.root, local, self.spec.bounds.max_raw_bytes) == raw, "bound snapshot differs")

    def _events(self) -> Iterator[dict]:
        head = self._manifest["index"]
        remaining = self.spec.bounds.max_total_bytes
        while head is not None:
            ref = _ref(head)
            _require(ref.path == "index/" + ref.sha256 and ref.size > 0, "invalid index path")
            remaining -= ref.size
            _require(remaining >= 0, "index cycle or volume overflow")
            event = _json(_raw(self.root, ref, self.spec.bounds.max_header_bytes), self.spec.bounds.max_header_bytes)
            _require(type(event) is dict and set(event) == {"format", "collection_id", "previous", "receipt", "event"} and
                     event["format"] == "whole-source-index-v1" and
                     event["collection_id"] == self.spec.collection_id, "incompatible index")
            yield event
            head = event["previous"]

    def _validate_log(self) -> None:
        for node in self._events():
            receipt_ref = _ref(node["receipt"])
            receipt = _json(_raw(self.root, receipt_ref, self.spec.bounds.max_header_bytes),
                            self.spec.bounds.max_header_bytes)
            _require(type(receipt) is dict and receipt.get("format") == "whole-source-local-completion-v1" and
                     receipt.get("collection_id") == self.spec.collection_id and
                     receipt.get("status") == "CLOSED_FSYNCED_STRUCTURAL_ONLY" and
                     receipt.get("scientific_acceptance") is False and receipt.get("event") == node["event"] and
                     receipt_ref.path == "attempts/" + _name(receipt["attempt_id"]) + "/completions/" + receipt_ref.sha256,
                     "missing compatible closed-payload completion receipt")
            owner_ref = _ref(receipt["owner"])
            owner = _json(_raw(self.root, owner_ref, self.spec.bounds.max_header_bytes), self.spec.bounds.max_header_bytes)
            _require(type(owner) is dict and owner.get("format") == "whole-source-local-attempt-v1" and
                     owner.get("generation") == receipt.get("generation") and
                     owner.get("collection_id") == self.spec.collection_id and
                     owner_ref.path == "attempts/" + receipt["attempt_id"] + "/artifact-owner.json",
                     "completion lacks bound attempt authorization")
            event = node["event"]
            _require(type(event) is dict and event.get("kind") in ("chunk", "prefix", "quantity", "source"),
                     "unknown index operation")
            ref = _ref(event["artifact"])
            raw = _raw(self.root, ref, self.spec.bounds.max_raw_bytes)
            if event["kind"] == "chunk":
                _require(ref.path == "chunks/" + ref.sha256, "noncanonical committed chunk path")
                snapshot = _decode_chunk(self.spec, raw)
                _require(snapshot.header["task"] == event.get("task"), "index/chunk task mismatch")
            elif event["kind"] == "prefix":
                _require(ref.path == "prefixes/" + ref.sha256, "noncanonical committed prefix path")
                prefix = _decode_prefix(self.spec, raw)
                _require(prefix.task.to_dict() == event.get("task"), "index/prefix task mismatch")
            else:
                self._validate_seal(_json(raw, self.spec.bounds.max_header_bytes))
        self._quota(0)

    def _validate_seal(self, value: dict) -> None:
        _require(type(value) is dict and value.get("scope") == "STRUCTURAL_ONLY" and
                 value.get("collection_id") == self.spec.collection_id and
                 value.get("analytical_acceptance") is False and value.get("matrix_positivity") is False and
                 value.get("production_admission") is False, "invalid structural seal")
        if value.get("format") == "whole-source-source-seal-v1":
            refs = value.get("quantities")
            _require(type(refs) is list and len(refs) == 16 and
                     all(q.scope == "FULL_QUANTITY" for q in self.spec.quantities),
                     "incomplete source seal")
            for row, quantity in zip(refs, self.spec.quantities):
                ref = _ref(row)
                child = _json(_raw(self.root, ref, self.spec.bounds.max_header_bytes), self.spec.bounds.max_header_bytes)
                _require(child.get("quantity") == quantity.to_dict(), "source quantity binding mismatch")
                self._validate_seal(child)
            return
        _require(value.get("format") == "whole-source-quantity-seal-v1", "unknown structural seal")
        key = QuantityKey.from_dict(value["quantity"]["quantity"])
        quantity = self.spec.quantity(key)
        _require(value["quantity"] == quantity.to_dict() and value.get("coverage_scope") == quantity.scope,
                 "incompatible quantity seal")
        count = _int(value.get("tile_count"), 1, self.spec.bounds.max_total_bytes, "scientific tile count")
        head = value.get("tiles")
        remaining = self.spec.bounds.max_total_bytes
        for task in _output_tasks(self.spec, quantity, reverse=True):
            _require(head is not None and count > 0, "incomplete scientific tile index")
            ref = _ref(head)
            remaining -= ref.size
            _require(remaining >= 0 and ref.path == "seals/" + ref.sha256, "invalid scientific index reference")
            node = _json(_raw(self.root, ref, self.spec.bounds.max_header_bytes), self.spec.bounds.max_header_bytes)
            _require(type(node) is dict and node.get("format") == "whole-source-scientific-tile-index-v1" and
                     node.get("collection_id") == self.spec.collection_id and node.get("scope") == "STRUCTURAL_ONLY" and
                     type(node.get("ordinal")) is int and node["ordinal"] == count and node.get("task") == task.to_dict(),
                     "noncanonical scientific tile index")
            state_ref = _ref(node["state"])
            _require(state_ref.path == "seals/" + state_ref.sha256, "invalid final tile reference")
            state = _json(_raw(self.root, state_ref, self.spec.bounds.max_raw_bytes),
                          min(self.spec.bounds.max_raw_bytes, self.spec.bounds.max_decoded_bytes))
            _require(type(state) is dict and state.get("format") == "whole-source-final-tile-v1" and
                     state.get("collection_id") == self.spec.collection_id and state.get("task") == task.to_dict() and
                     state.get("grid_bits") == self.spec.grid_bits and state.get("scope") == "STRUCTURAL_ONLY",
                     "incompatible final scientific tile")
            expected = 1
            for axis in quantity.axes:
                expected *= len(axis)
            _require(type(state.get("covered")) is int and state["covered"] == expected and
                     state.get("stage_rounds") == expected and state.get("prefix_rounds") == expected and
                     type(state.get("contributions_sha256")) is str and
                     re.fullmatch(r"[0-9a-f]{64}", state["contributions_sha256"]) is not None,
                     "invalid final tile cover/rounding")
            _validate_output_records(self.spec, task, state.get("records"))
            head = node.get("previous")
            count -= 1
        _require(count == 0 and head is None, "extra scientific tiles")

    def _append(self, event: dict, attempt_id: str) -> None:
        self._check(attempt_id=attempt_id)
        completion = {"format": "whole-source-local-completion-v1", "collection_id": self.spec.collection_id,
                      "attempt_id": attempt_id, "generation": self.generation,
                      "owner": _ref_document(self._attempts[attempt_id]), "event": event,
                      "status": "CLOSED_FSYNCED_STRUCTURAL_ONLY", "scientific_acceptance": False}
        receipt = self._immutable("attempts/" + attempt_id + "/completions", canonical_bytes(completion))
        node = {"format": "whole-source-index-v1", "collection_id": self.spec.collection_id,
                "previous": self._manifest["index"], "receipt": _ref_document(receipt), "event": event}
        ref = self._immutable("index", canonical_bytes(node),
                              barrier="index-writing" if event["kind"] == "prefix" else None,
                              attempt_id=attempt_id)
        self._check(attempt_id=attempt_id)
        self._commit_manifest({**self._manifest, "index": _ref_document(ref)})

    def release(self) -> None:
        if self._held:
            try:
                if self._pid == os.getpid():
                    _os_lock(self._stream, False)
            finally:
                self._held = False
                self._attempts.clear()
                self._stream.close()

    def __enter__(self) -> CollectionLock:
        self._check()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.release()
        return False


@dataclass(frozen=True, slots=True)
class ContributionTask:
    quantity: QuantityKey
    rows: ModeRange
    columns: ModeRange
    axes: tuple[Axis, ...]

    def to_dict(self) -> dict:
        return {"quantity": quantity_document(self.quantity),
                "rows": _range_document(self.rows), "columns": _range_document(self.columns),
                "axes": [_axis_document(a) for a in self.axes]}


def _task(value: dict) -> ContributionTask:
    _require(type(value) is dict and set(value) == {"quantity", "rows", "columns", "axes"}, "invalid task")
    try:
        return ContributionTask(QuantityKey.from_dict(value["quantity"]), ModeRange(**value["rows"]),
                                ModeRange(**value["columns"]), tuple(Axis(**a) for a in value["axes"]))
    except (TypeError, KeyError) as exc:
        raise ArtifactError("invalid task fields") from exc


def _validate_task(spec: CollectionSpec, task: ContributionTask, *, full_axes: bool = False) -> QuantitySpec:
    _require(type(task) is ContributionTask and type(task.quantity) is QuantityKey and
             type(task.rows) is ModeRange and type(task.columns) is ModeRange and
             type(task.axes) is tuple and all(type(a) is Axis for a in task.axes), "scientific contribution task required")
    quantity = spec.quantity(task.quantity)
    _require(_subset(task.rows, quantity.rows) and _subset(task.columns, quantity.columns) and
             len(task.axes) == len(quantity.axes) and
             all(a.name == e.name and _subset(a, e) for a, e in zip(task.axes, quantity.axes)),
             "task outside frozen scientific domain")
    _require(not full_axes or task.axes == quantity.axes, "prefix requires complete frozen contribution axes")
    widths = dict(spec.partition)
    for name, actual, expected in (("rows", task.rows, quantity.rows), ("columns", task.columns, quantity.columns)) + tuple(
            (a.name, a, e) for a, e in zip(task.axes, quantity.axes)):
        width = widths[name]
        first = (actual.start - expected.start)//expected.step
        aligned = (first % width == 0 and len(actual) == min(width, len(expected)-first) and
                   actual.stop == min(expected.stop, actual.start + actual.step*width))
        _require(aligned or full_axes and name not in ("rows", "columns") and actual == expected,
                 "task does not match frozen partition")
    _require(not quantity.symmetric_upper or task.rows.start <= task.columns.start + task.columns.step*(len(task.columns)-1),
             "empty canonical output tile")
    return quantity


def _coordinates(task: ContributionTask, symmetric: bool) -> Iterator[tuple[int, int]]:
    for row in task.rows:
        for column in task.columns:
            if not symmetric or row <= column:
                yield row, column


def _contributions(axes: tuple[Axis, ...]) -> Iterator[tuple[int, ...]]:
    # Recursive ranges avoid itertools.product's eager pool copies.
    def walk(index: int, prefix: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
        if index == len(axes):
            yield prefix
        else:
            for value in axes[index]:
                yield from walk(index+1, prefix + (value,))
    return walk(0, ())


def _keys(task: ContributionTask, symmetric: bool) -> Iterator[tuple[int, int, tuple[int, ...]]]:
    for row, column in _coordinates(task, symmetric):
        for contribution in _contributions(task.axes):
            yield row, column, contribution


def _output_count(task: ContributionTask, symmetric: bool) -> int:
    n, m = len(task.rows), len(task.columns)
    if not symmetric:
        return n*m
    step = task.rows.step
    full = max(0, min(n, (task.columns.start-task.rows.start)//step + 1))
    last_column = task.columns.start + step*(m-1)
    eligible = max(0, min(n, (last_column-task.rows.start)//step + 1))
    partial = eligible-full
    first = task.rows.start + step*full
    first_count = m-max(0, (first-task.columns.start+step-1)//step)
    return full*m + partial*first_count - partial*(partial-1)//2


def _contribution_rank(axes: tuple[Axis, ...], values: tuple[int, ...]) -> int:
    _require(len(axes) == len(values), "wrong contribution dimensions")
    rank = 0
    for axis, value in zip(axes, values):
        _require(type(value) is int and axis.start <= value < axis.stop and
                 (value-axis.start) % axis.step == 0, "out-of-domain contribution")
        rank = rank*len(axis) + (value-axis.start)//axis.step
    return rank


def _count(task: ContributionTask, symmetric: bool) -> int:
    output = _output_count(task, symmetric)
    for axis in task.axes:
        output *= len(axis)
    return output


def _round(lower: Fraction, upper: Fraction, grid: int) -> tuple[int, int]:
    _require(type(lower) is Fraction and type(upper) is Fraction and lower <= upper,
             "ordered exact endpoints required")
    for endpoint in (lower, upper):
        _require(endpoint.denominator & (endpoint.denominator - 1) == 0, "dyadic endpoints required")
    scale = 1 << grid
    return ((lower.numerator * scale)//lower.denominator - 1,
            -((-upper.numerator * scale)//upper.denominator) + 1)


@dataclass(frozen=True, slots=True)
class IntervalRecord:
    row: int
    column: int
    contribution: tuple[int, ...]
    lower: Fraction
    upper: Fraction


@dataclass(frozen=True, slots=True)
class StagedChunk:
    path: Path
    task: ContributionTask
    ref: ArtifactRef
    generation: str
    attempt_id: str


@dataclass(frozen=True, slots=True)
class ChunkSnapshot:
    header: dict
    records: tuple[IntervalRecord, ...]
    decoded_bytes: int


@dataclass(frozen=True, slots=True)
class PrefixSnapshot:
    ref: ArtifactRef
    task: ContributionTask
    records: tuple[IntervalRecord, ...]
    covered: int
    rounds: int
    previous: ArtifactRef | None
    contributions: tuple[ArtifactRef, ...]


@dataclass(frozen=True, slots=True)
class StagedPrefix:
    path: Path
    task: ContributionTask
    ref: ArtifactRef
    generation: str
    attempt_id: str
    index_head: ArtifactRef | None


def _chunk_header(spec: CollectionSpec, task: ContributionTask, count: int) -> dict:
    return {"format": "whole-source-exact-chunk-v1", "collection_id": spec.collection_id,
            "role": spec.role, "task": task.to_dict(), "grid_bits": spec.grid_bits,
            "max_endpoint_bits": spec.bounds.max_endpoint_bits, "records": count,
            "rounding": "stage-floor-minus-one/ceil-plus-one", "scope": "STRUCTURAL_ONLY"}


def _decode_chunk(spec: CollectionSpec, raw: bytes, *, decoded_cap: int | None = None,
                  record_cap: int | None = None) -> ChunkSnapshot:
    bounds = spec.bounds
    decoded_limit = bounds.max_decoded_bytes if decoded_cap is None else min(bounds.max_decoded_bytes, decoded_cap)
    record_limit = bounds.max_records if record_cap is None else min(bounds.max_records, record_cap)
    _require(len(raw) <= min(bounds.max_compressed_bytes, bounds.max_raw_bytes), "compressed chunk exceeds cap")
    records = []
    total = 0
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") as stream:
            line = stream.readline(bounds.max_header_bytes + 1)
            header = _json(line, bounds.max_header_bytes)
            _require(type(header) is dict, "invalid chunk header")
            task = _task(header.get("task"))
            quantity = _validate_task(spec, task)
            count = _count(task, quantity.symmetric_upper)
            _require(count <= record_limit and canonical_bytes(header) == canonical_bytes(_chunk_header(spec, task, count)),
                     "incompatible chunk header")
            total += len(line)
            _require(total <= decoded_limit, "decoded header exceeds cap")
            for row, column, contribution in _keys(task, quantity.symmetric_upper):
                line = stream.readline(bounds.max_record_bytes + 1)
                total += len(line)
                _require(total <= decoded_limit, "decoded chunk exceeds cap")
                record = _json(line, bounds.max_record_bytes)
                _require(type(record) is list and len(record) == 5 and
                         type(record[0]) is int and type(record[1]) is int and
                         type(record[2]) is list and all(type(v) is int for v in record[2]) and
                         record[:3] == [row, column, list(contribution)], "record order/domain mismatch")
                lower = decode_integer(record[3], bounds.max_endpoint_bits)
                upper = decode_integer(record[4], bounds.max_endpoint_bits)
                _require(lower <= upper, "reversed endpoint interval")
                records.append(IntervalRecord(row, column, contribution,
                                              Fraction(lower, 1 << spec.grid_bits), Fraction(upper, 1 << spec.grid_bits)))
            _require(not stream.read(1), "extra chunk records")
    except (OSError, EOFError, ValueError, TypeError) as exc:
        if isinstance(exc, ArtifactError):
            raise
        raise ArtifactError("malformed compressed chunk") from exc
    return ChunkSnapshot(header, tuple(records), total)


class _CompressedWriter:
    def __init__(self, stream, cap: int) -> None:
        self.stream, self.cap, self.written = stream, cap, 0

    def write(self, raw: bytes) -> int:
        _require(self.written + len(raw) <= self.cap, "compressed chunk exceeds cap")
        _write_all(self.stream, raw)
        self.written += len(raw)
        return len(raw)

    def flush(self) -> None:
        self.stream.flush()


@contextmanager
def _volume_gate(root: Path):
    path = _safe(root, ".volume.lock")
    with path.open("r+b") as stream:
        _os_lock(stream, True, blocking=True)
        try:
            yield
        finally:
            _os_lock(stream, False)


def _check_quota(root: Path, bounds: CodecBounds, additional: int, temporary: int) -> None:
    _require(temporary <= bounds.max_temporary_bytes, "temporary overlap exceeds cap")
    _require(_volume(root) + additional <= bounds.max_total_bytes, "collection volume exceeds cap")
    staged = 0
    for path, info in _members(root):
        if "staging" in path.relative_to(root).parts or path.name.startswith((".pending-", ".manifest-")):
            staged += info.st_size
    _require(staged + temporary <= bounds.max_temporary_bytes, "aggregate temporary overlap exceeds cap")


@dataclass(frozen=True, slots=True)
class StagingContext:
    """Picklable worker capability. It cannot publish or update collection state."""

    root: Path
    spec: CollectionSpec
    generation: str
    attempt_id: str
    receipt: ArtifactRef
    index_head: ArtifactRef | None = None

    def stage_prefix(self, task, prior_ref, next_refs) -> StagedPrefix:
        """Reduce in an owned worker; this capability cannot advance coverage."""
        self._check()
        reader = _PrefixReader(self)
        current = reader.resume_prefix(task)
        refs = _bounded_refs(next_refs, self.spec.bounds.max_records)
        _require(len(refs) <= self.spec.bounds.max_records and
                 prior_ref == (current.ref if current else None), "stale prior prefix")
        records, covered, rounds = reader._reduce(task, current, refs)
        raw = _prefix_bytes(self.spec, task, prior_ref, refs, records, covered, rounds)
        relative = "attempts/" + self.attempt_id + "/staging/" + uuid.uuid4().hex
        path = _safe(self.root, relative, missing=True)
        with _volume_gate(self.root):
            _check_quota(self.root, self.spec.bounds, len(raw), len(raw))
            with path.open("xb") as stream:
                _write_all(stream, raw)
                stream.flush()
                os.fsync(stream.fileno())
            _sync_directory(path.parent)
        self._check()
        return StagedPrefix(path, task, ArtifactRef(relative, _hash(raw), len(raw)),
                            self.generation, self.attempt_id, self.index_head)

    def _check(self) -> None:
        _raw(self.root, self.receipt, self.spec.bounds.max_header_bytes)
        _require(not (self.root / "attempts" / self.attempt_id / "artifact-invalidated").exists(),
                 "attempt invalidated")
        path = _safe(self.root, ".collection.lock")
        # A retained PID/generation file is not live ownership.
        with path.open("r+b", buffering=0) as probe:
            try:
                _os_lock(probe, True)
            except OSError as exc:
                _require(exc.errno in (errno.EACCES, errno.EAGAIN), "cannot verify live collection owner")
            else:
                _os_lock(probe, False)
                raise ArtifactError("collection owner no longer holds its lock")
        with path.open("rb", buffering=0) as stream:
            metadata = _json(stream.readline(4096), 4096)
        _require(type(metadata) is dict and metadata.get("generation") == self.generation and
                 metadata.get("collection_id") == self.spec.collection_id, "stale worker generation")

    def stage_chunk(self, task: ContributionTask, records: Iterable[IntervalRecord]) -> StagedChunk:
        with _volume_gate(self.root):
            return self._write(task, records)

    def _write(self, task: ContributionTask, records: Iterable[IntervalRecord]) -> StagedChunk:
        self._check()
        quantity = _validate_task(self.spec, task)
        bounds = self.spec.bounds
        count = _count(task, quantity.symmetric_upper)
        _require(count <= bounds.max_records, "record count exceeds cap")
        header = canonical_bytes(_chunk_header(self.spec, task, count))
        _require(len(header) <= bounds.max_header_bytes and len(header) <= bounds.max_decoded_bytes,
                 "chunk header cap exceeded")
        _check_quota(self.root, bounds, bounds.max_compressed_bytes, bounds.max_compressed_bytes)
        relative = "attempts/" + self.attempt_id + "/staging/" + uuid.uuid4().hex
        path = _safe(self.root, relative, missing=True)
        total = len(header)
        source = iter(records)
        with path.open("xb") as output:
            bounded = _CompressedWriter(output, bounds.max_compressed_bytes)
            with gzip.GzipFile(fileobj=bounded, mode="wb", filename="", mtime=0) as stream:
                stream.write(header)
                for index, (row, column, contribution) in enumerate(_keys(task, quantity.symmetric_upper)):
                    record = next(source, None)
                    _require(type(record) is IntervalRecord and type(record.row) is int and
                             type(record.column) is int and type(record.contribution) is tuple and
                             all(type(v) is int for v in record.contribution) and
                             (record.row, record.column, record.contribution) == (row, column, contribution),
                             "record order/domain mismatch")
                    for endpoint in (record.lower, record.upper):
                        _require(type(endpoint) is Fraction and
                                 abs(endpoint.numerator).bit_length() <= bounds.max_endpoint_bits and
                                 endpoint.denominator.bit_length() <= bounds.max_endpoint_bits,
                                 "input endpoint cap exceeded")
                    lower, upper = _round(record.lower, record.upper, self.spec.grid_bits)
                    line = canonical_bytes([row, column, list(contribution),
                                            encode_integer(lower, bounds.max_endpoint_bits),
                                            encode_integer(upper, bounds.max_endpoint_bits)])
                    total += len(line)
                    _require(len(line) <= bounds.max_record_bytes and total <= bounds.max_decoded_bytes,
                             "decoded record cap exceeded")
                    stream.write(line)
                    if index == 0:
                        def flush_partial():
                            stream.flush()
                            output.flush()
                            os.fsync(output.fileno())
                        qualification_barrier(self.root, self.attempt_id, "payload-writing", flush=flush_partial)
                _require(next(source, None) is None, "extra input records")
            output.flush()
            os.fsync(output.fileno())
        _sync_directory(path.parent)
        qualification_barrier(self.root, self.attempt_id, "payload-closed")
        self._check()
        with path.open("rb") as stream:
            raw = stream.read(bounds.max_compressed_bytes + 1)
        ref = ArtifactRef(relative, _hash(raw), len(raw))
        return StagedChunk(path, task, ref, self.generation, self.attempt_id)


class ChunkStore:
    """Stage bounded records; only the held collection owner may commit them."""

    def __init__(self, lock: CollectionLock, spec: CollectionSpec, *, attempt_id: str) -> None:
        _require(type(lock) is CollectionLock and type(spec) is CollectionSpec and
                 lock.spec.collection_id == spec.collection_id, "collection context mismatch")
        self.lock, self.spec, self.attempt_id = lock, spec, _name(attempt_id)
        self.generation = lock.generation
        self._check()

    def _check(self) -> None:
        self.lock._check(self.generation, self.attempt_id)

    def staging_context(self) -> StagingContext:
        self._check()
        return StagingContext(self.lock.root, self.spec, self.generation, self.attempt_id,
                              self.lock._attempts[self.attempt_id],
                              _ref(self.lock._manifest["index"]) if self.lock._manifest["index"] else None)

    def stage_chunk(self, task: ContributionTask, records: Iterable[IntervalRecord]) -> StagedChunk:
        self._check()
        return self.staging_context().stage_chunk(task, records)

    def read_chunk(self, ref: ArtifactRef) -> ChunkSnapshot:
        self._check()
        return _decode_chunk(self.spec, _raw(self.lock.root, ref, self.spec.bounds.max_compressed_bytes))

    def _chunk_events(self) -> Iterator[tuple[ContributionTask, ArtifactRef]]:
        for node in self.lock._events():
            event = node["event"]
            if event["kind"] == "chunk":
                yield _task(event["task"]), _ref(event["artifact"])

    def recover_staged_chunk(self, task: ContributionTask, ref: ArtifactRef) -> ArtifactRef:
        """Revalidate/copy a closed compatible orphan without another grid rounding.

        This imports structural bytes, not analytical truth. Independent
        reconstruction remains mandatory. Incomplete payloads are never adopted.
        """
        self._check()
        parts = ref.path.split("/")
        _require(len(parts) == 4 and parts[0] == "attempts" and parts[2] == "staging" and
                 parts[1] != self.attempt_id, "not a prior staged orphan")
        owner_path = _safe(self.lock.root, "attempts/" + _name(parts[1]) + "/artifact-owner.json")
        with owner_path.open("rb") as stream:
            owner = _json(stream.read(self.spec.bounds.max_header_bytes+1), self.spec.bounds.max_header_bytes)
        _require(owner.get("collection_id") == self.spec.collection_id and
                 owner.get("attempt_id") == parts[1], "orphan belongs to another collection")
        raw = _raw(self.lock.root, ref, self.spec.bounds.max_compressed_bytes)
        snapshot = _decode_chunk(self.spec, raw)
        _require(_task(snapshot.header["task"]) == task, "orphan task changed")
        relative = "attempts/" + self.attempt_id + "/staging/" + uuid.uuid4().hex
        copied = self.lock._exclusive(relative, raw)
        staged = StagedChunk(self.lock.root / relative, task, copied, self.generation, self.attempt_id)
        return self.publish_chunk(task, staged)

    def publish_chunk(self, task: ContributionTask, staged_file: StagedChunk) -> ArtifactRef:
        self._check()
        _require(type(staged_file) is StagedChunk and staged_file.generation == self.generation and
                 staged_file.attempt_id == self.attempt_id and staged_file.task == task and
                 staged_file.path == self.lock.root / staged_file.ref.path and
                 staged_file.ref.path.startswith("attempts/" + self.attempt_id + "/staging/"), "stale staged context")
        raw = _raw(self.lock.root, staged_file.ref, self.spec.bounds.max_compressed_bytes)
        snapshot = _decode_chunk(self.spec, raw)
        _require(_task(snapshot.header["task"]) == task, "staged task mismatch")
        for other, ref in self._chunk_events():
            if other == task:
                _require(ref.sha256 == staged_file.ref.sha256 and ref.size == staged_file.ref.size,
                         "conflicting identical-task retry")
                staged_file.path.unlink()
                return ref
            _require(not _overlap(task, other), "overlapping scientific contribution")
        ref = self.lock._immutable("chunks", raw)
        self._check()
        staged_file.path.unlink()
        _sync_directory(staged_file.path.parent)
        self.lock._append({"kind": "chunk", "task": task.to_dict(), "artifact": _ref_document(ref)}, self.attempt_id)
        qualification_barrier(self.lock.root, self.attempt_id, "chunk-published")
        return ref

    def _latest_prefix(self, task: ContributionTask) -> ArtifactRef | None:
        for node in self.lock._events():
            event = node["event"]
            if event["kind"] == "prefix" and event["task"] == task.to_dict():
                return _ref(event["artifact"])
        return None

    def resume_prefix(self, task: ContributionTask) -> PrefixSnapshot | None:
        self._check()
        _validate_task(self.spec, task, full_axes=True)
        ref = self._latest_prefix(task)
        if ref is None:
            return None
        result = _decode_prefix(self.spec, _raw(self.lock.root, ref, self.spec.bounds.max_raw_bytes), ref)
        self._validate_prefix_chain(result)
        return result

    def _validate_prefix_chain(self, result: PrefixSnapshot) -> None:
        remaining = self.spec.bounds.max_total_bytes
        current = result
        accepted = False
        while True:
            remaining -= current.ref.size
            _require(remaining >= 0, "prefix lineage exceeds volume")
            found_current = False
            expected_previous = None
            for node in self.lock._events():
                event = node["event"]
                if event["kind"] != "prefix":
                    continue
                if _ref(event["artifact"]) == current.ref:
                    found_current = True
                elif found_current and event["task"] == current.task.to_dict():
                    expected_previous = _ref(event["artifact"])
                    break
            _require(found_current and expected_previous == current.previous,
                     "prefix lineage is not the accepted prior state")
            previous = None
            if current.previous is not None:
                previous = _decode_prefix(self.spec, _raw(self.lock.root, current.previous,
                                                         self.spec.bounds.max_raw_bytes), current.previous)
                _require(previous.task == current.task and previous.covered < current.covered,
                         "invalid previous prefix")
            expected = self._reduce(current.task, previous, current.contributions)
            _require(expected == (current.records, current.covered, current.rounds), "prefix sum/coverage mismatch")
            if previous is None:
                break
            current = previous

    def _reduce(self, task: ContributionTask, prior: PrefixSnapshot | None,
                refs: tuple[ArtifactRef, ...]) -> tuple[tuple[IntervalRecord, ...], int, int]:
        quantity = _validate_task(self.spec, task, full_axes=True)
        bounds = self.spec.bounds
        count = _output_count(task, quantity.symmetric_upper)
        _require(count <= bounds.max_records and refs and len(refs) <= bounds.max_records, "bounded nonempty prefix batch required")
        registered = {}
        for candidate in refs:
            _require(candidate.path not in registered, "duplicate prefix contribution reference")
            registered[candidate.path] = candidate
        snapshots = []
        total_records = 0
        total_bytes = 0
        total_decoded = 0
        for ref in refs:
            found = next((t for t, r in self._chunk_events() if r == ref), None)
            _require(found is not None and found.quantity == task.quantity and found.rows == task.rows and
                     found.columns == task.columns, "prefix consumes only committed matching output chunks")
            total_bytes += ref.size
            _require(total_bytes <= bounds.max_compressed_bytes, "prefix input compressed overlap exceeds cap")
            snapshot = _decode_chunk(
                self.spec, _raw(self.lock.root, ref, bounds.max_compressed_bytes),
                decoded_cap=bounds.max_decoded_bytes-total_decoded,
                record_cap=bounds.max_records-total_records)
            total_records += len(snapshot.records)
            total_decoded += snapshot.decoded_bytes
            snapshots.append(snapshot)
        covered = prior.covered if prior is not None else 0
        prior_records = prior.records if prior is not None else ()
        outputs = []
        extension_size = None
        for output_index, (row, column) in enumerate(_coordinates(task, quantity.symmetric_upper)):
            lower, upper = (prior_records[output_index].lower, prior_records[output_index].upper) if prior else (Fraction(0), Fraction(0))
            added = 0
            # Chunks may arrive in any order. Reduction order is the frozen physical axis order.
            candidates = []
            for snapshot in snapshots:
                for record in snapshot.records:
                    if (record.row, record.column) == (row, column):
                        candidates.append(record)
            candidates.sort(key=lambda r: r.contribution)
            for record in candidates:
                _require(_contribution_rank(task.axes, record.contribution) == covered+added,
                         "missing, repeated, or out-of-order prefix domain")
                lo, hi = _round(lower + record.lower, upper + record.upper, self.spec.grid_bits)
                encode_integer(lo, bounds.max_endpoint_bits)
                encode_integer(hi, bounds.max_endpoint_bits)
                lower, upper = Fraction(lo, 1 << self.spec.grid_bits), Fraction(hi, 1 << self.spec.grid_bits)
                added += 1
            _require(added > 0 and (extension_size is None or extension_size == added), "ragged contribution cover")
            extension_size = added
            outputs.append(IntervalRecord(row, column, (), lower, upper))
        new_covered = covered + extension_size
        return tuple(outputs), new_covered, new_covered

    def commit_prefix(self, task: ContributionTask, prior_ref: ArtifactRef | None,
                      next_refs: Iterable[ArtifactRef]) -> ArtifactRef:
        """Standalone structural convenience; owned execution uses stage/publish."""
        self._check()
        refs = _bounded_refs(next_refs, self.spec.bounds.max_records)
        current = self.resume_prefix(task)
        if current is not None and prior_ref == current.previous and tuple(sorted(refs, key=lambda r: r.path)) == current.contributions:
            return current.ref
        return self.publish_prefix(self.staging_context().stage_prefix(task, prior_ref, refs))

    def publish_prefix(self, staged: StagedPrefix) -> ArtifactRef:
        self._check()
        _require(type(staged) is StagedPrefix and staged.generation == self.generation and
                 staged.attempt_id == self.attempt_id and staged.path == self.lock.root / staged.ref.path and
                 staged.ref.path.startswith("attempts/" + self.attempt_id + "/staging/") and
                 _ref_document(staged.index_head) == self.lock._manifest["index"], "stale staged prefix")
        raw = _raw(self.lock.root, staged.ref, self.spec.bounds.max_raw_bytes)
        result = _decode_prefix(self.spec, raw)
        _require(result.task == staged.task and result.previous == self._latest_prefix(staged.task),
                 "staged prefix changed accepted prior")
        # Structural cover only. Arithmetic was performed inside the owned worker.
        prior = None if result.previous is None else _decode_prefix(
            self.spec, _raw(self.lock.root, result.previous, self.spec.bounds.max_raw_bytes), result.previous)
        first = prior.covered if prior else 0
        quantity = _validate_task(self.spec, result.task, full_axes=True)
        ranks = {}
        decoded = 0
        compressed = 0
        for candidate in result.contributions:
            _require(any(ref == candidate for _, ref in self._chunk_events()), "uncommitted prefix input")
            compressed += candidate.size
            _require(compressed <= self.spec.bounds.max_compressed_bytes, "prefix input overlap exceeds cap")
            snapshot = _decode_chunk(self.spec, _raw(self.lock.root, candidate, self.spec.bounds.max_compressed_bytes),
                                     decoded_cap=self.spec.bounds.max_decoded_bytes-decoded)
            decoded += snapshot.decoded_bytes
            task = _task(snapshot.header["task"])
            _require(task.quantity == result.task.quantity and task.rows == result.task.rows and
                     task.columns == result.task.columns, "prefix input physical mismatch")
            for record in snapshot.records:
                rank = _contribution_rank(result.task.axes, record.contribution)
                values = ranks.setdefault((record.row, record.column), set())
                _require(rank not in values, "duplicate prefix contribution")
                values.add(rank)
                _require(sum(len(v) for v in ranks.values()) <= self.spec.bounds.max_records,
                         "prefix cover exceeds bounded records")
        for coordinate in _coordinates(result.task, quantity.symmetric_upper):
            values = ranks.get(coordinate, set())
            _require(values and len(values) == result.covered-first and
                     min(values) == first and max(values) == result.covered-1,
                     "missing/repeated prefix cover")
        ref = self.lock._immutable("prefixes", raw)
        self.lock._append({"kind": "prefix", "task": result.task.to_dict(), "artifact": _ref_document(ref)}, self.attempt_id)
        qualification_barrier(self.lock.root, self.attempt_id, "prefix-committed")
        staged.path.unlink()
        qualification_barrier(self.lock.root, self.attempt_id, "prefix-acknowledgement")
        return ref

    def _scientific_tile(self, prefix: PrefixSnapshot) -> ArtifactRef:
        digest = hashlib.sha256()
        for task in _contribution_tasks(self.spec, prefix.task):
            ref = next((ref for accepted, ref in self._chunk_events() if accepted == task), None)
            _require(ref is not None, "missing canonical tile contribution")
            digest.update(canonical_bytes({"task": task.to_dict(), "artifact": _ref_document(ref)}))
        document = {"format": "whole-source-final-tile-v1", "collection_id": self.spec.collection_id,
                    "task": prefix.task.to_dict(), "grid_bits": self.spec.grid_bits,
                    "covered": prefix.covered, "stage_rounds": prefix.covered, "prefix_rounds": prefix.rounds,
                    "contributions_sha256": digest.hexdigest(), "scope": "STRUCTURAL_ONLY",
                    "records": [[r.row, r.column,
                                 encode_integer(int(r.lower*(1 << self.spec.grid_bits)), self.spec.bounds.max_endpoint_bits),
                                 encode_integer(int(r.upper*(1 << self.spec.grid_bits)), self.spec.bounds.max_endpoint_bits)]
                                for r in prefix.records]}
        raw = canonical_bytes(document)
        _require(len(raw) <= self.spec.bounds.max_decoded_bytes, "final tile decoded cap exceeded")
        return self.lock._immutable("seals", raw)

    def seal_quantity(self, key: QuantityKey) -> ArtifactRef:
        self._check()
        quantity = self.spec.quantity(key)
        tiles = None
        tile_count = 0
        for task in _output_tasks(self.spec, quantity):
            latest = self._latest_prefix(task)
            prefix = None if latest is None else _decode_prefix(
                self.spec, _raw(self.lock.root, latest, self.spec.bounds.max_raw_bytes), latest)
            expected = 1
            for axis in quantity.axes:
                expected *= len(axis)
            _require(prefix is not None and prefix.covered == expected, "incomplete semantic quantity cover")
            state = self._scientific_tile(prefix)
            tile_count += 1
            tiles = self.lock._immutable("seals", canonical_bytes({
                "format": "whole-source-scientific-tile-index-v1", "collection_id": self.spec.collection_id,
                "previous": _ref_document(tiles), "ordinal": tile_count,
                "task": task.to_dict(), "state": _ref_document(state), "scope": "STRUCTURAL_ONLY"}))
        document = {"format": "whole-source-quantity-seal-v1", "collection_id": self.spec.collection_id,
                    "quantity": quantity.to_dict(), "tiles": _ref_document(tiles), "tile_count": tile_count,
                    "scope": "STRUCTURAL_ONLY", "coverage_scope": quantity.scope,
                    "analytical_acceptance": False, "matrix_positivity": False, "production_admission": False}
        ref = self.lock._immutable("seals", canonical_bytes(document))
        self.lock._append({"kind": "quantity", "quantity": quantity_document(key),
                           "artifact": _ref_document(ref)}, self.attempt_id)
        return ref

    def seal_source(self) -> ArtifactRef:
        self._check()
        required = {QuantityKey(name, parity) for name in ("A_model", "weighted_head", "weighted_complete_tail",
                                                        "F_L", "F_H", "J_F", "K_H", "R_H") for parity in (0, 1)}
        _require({q.key for q in self.spec.quantities} == required and
                 all(q.scope == "FULL_QUANTITY" for q in self.spec.quantities), "full source requires every real family and parity")
        seals = []
        for quantity in self.spec.quantities:
            seals.append(self.seal_quantity(quantity.key))
        document = {"format": "whole-source-source-seal-v1", "collection_id": self.spec.collection_id,
                    "quantities": [_ref_document(r) for r in seals], "scope": "STRUCTURAL_ONLY",
                    "coverage_scope": "FULL_DECLARED_SOURCE", "analytical_acceptance": False,
                    "matrix_positivity": False, "production_admission": False}
        ref = self.lock._immutable("seals", canonical_bytes(document))
        self.lock._append({"kind": "source", "artifact": _ref_document(ref)}, self.attempt_id)
        return ref


def _overlap(left: ContributionTask, right: ContributionTask) -> bool:
    if left.quantity != right.quantity:
        return False
    def intersect(a, b) -> bool:
        return max(a.start, b.start) < min(a.stop, b.stop)
    return (intersect(left.rows, right.rows) and intersect(left.columns, right.columns) and
            all(intersect(a, b) for a, b in zip(left.axes, right.axes)))


def _contribution_tasks(spec: CollectionSpec, full: ContributionTask) -> Iterator[ContributionTask]:
    widths = dict(spec.partition)
    def walk(index: int, axes: tuple[Axis, ...]) -> Iterator[ContributionTask]:
        if index == len(full.axes):
            yield ContributionTask(full.quantity, full.rows, full.columns, axes)
        else:
            axis = full.axes[index]
            for start in range(axis.start, axis.stop, axis.step*widths[axis.name]):
                block = Axis(axis.name, start, min(axis.stop, start + axis.step*widths[axis.name]), axis.step)
                yield from walk(index+1, axes + (block,))
    yield from walk(0, ())


def _output_tasks(spec: CollectionSpec, quantity: QuantitySpec, *, reverse: bool = False) -> Iterator[ContributionTask]:
    widths = dict(spec.partition)
    def blocks(value: ModeRange, width: int) -> Iterator[ModeRange]:
        starts = range(value.start, value.stop, value.step * width)
        for start in reversed(starts) if reverse else starts:
            yield ModeRange(start, min(value.stop, start + value.step * width), value.step)
    for rows in blocks(quantity.rows, widths["rows"]):
        for columns in blocks(quantity.columns, widths["columns"]):
            task = ContributionTask(quantity.key, rows, columns, quantity.axes)
            if _output_count(task, quantity.symmetric_upper):
                yield task


def _decode_prefix(spec: CollectionSpec, raw: bytes, ref: ArtifactRef | None = None) -> PrefixSnapshot:
    bounds = spec.bounds
    document = _json(raw, min(bounds.max_raw_bytes, bounds.max_decoded_bytes))
    _require(type(document) is dict and set(document) == {"format", "collection_id", "task", "previous", "contributions",
             "covered", "rounds", "grid_bits", "rounding", "scope", "records"} and
             document["format"] == "whole-source-prefix-v1" and document["collection_id"] == spec.collection_id and
             document["grid_bits"] == spec.grid_bits and document["rounding"] == "outward-after-each-contribution" and
             document["scope"] == "STRUCTURAL_ONLY", "incompatible prefix")
    task = _task(document["task"])
    quantity = _validate_task(spec, task, full_axes=True)
    covered = _int(document["covered"], 1, 1 << 50, "prefix covered")
    _require(type(document["rounds"]) is int and document["rounds"] == covered,
             "prefix rounding ledger mismatch")
    _require(type(document["records"]) is list and
             len(document["records"]) == _output_count(task, quantity.symmetric_upper) <= bounds.max_records,
             "prefix record cap exceeded")
    records = []
    wire = iter(document["records"])
    for row, column in _coordinates(task, quantity.symmetric_upper):
        record = next(wire, None)
        _require(type(record) is list and len(record) == 4 and
                 type(record[0]) is int and type(record[1]) is int and record[:2] == [row, column],
                 "prefix output order mismatch")
        lower, upper = (decode_integer(v, bounds.max_endpoint_bits) for v in record[2:])
        _require(lower <= upper, "reversed prefix interval")
        records.append(IntervalRecord(row, column, (), Fraction(lower, 1 << spec.grid_bits), Fraction(upper, 1 << spec.grid_bits)))
    _require(next(wire, None) is None, "extra prefix output")
    _require(type(document["contributions"]) is list and 0 < len(document["contributions"]) <= bounds.max_records,
             "invalid prefix contribution list")
    contributions = tuple(_ref(r) for r in document["contributions"])
    _require(tuple(sorted(contributions, key=lambda r: r.path)) == contributions, "noncanonical contribution refs")
    previous = _ref(document["previous"]) if document["previous"] is not None else None
    actual_ref = ref or ArtifactRef("prefixes/" + _hash(raw), _hash(raw), len(raw))
    return PrefixSnapshot(actual_ref, task, tuple(records), covered, covered, previous, contributions)


def _prefix_bytes(spec, task, prior_ref, refs, records, covered, rounds):
    raw = canonical_bytes({"format": "whole-source-prefix-v1", "collection_id": spec.collection_id,
        "task": task.to_dict(), "previous": _ref_document(prior_ref),
        "contributions": [_ref_document(ref) for ref in sorted(refs, key=lambda r: r.path)],
        "covered": covered, "rounds": rounds, "grid_bits": spec.grid_bits,
        "rounding": "outward-after-each-contribution", "scope": "STRUCTURAL_ONLY",
        "records": [[r.row, r.column, encode_integer(int(r.lower*(1 << spec.grid_bits)), spec.bounds.max_endpoint_bits),
                     encode_integer(int(r.upper*(1 << spec.grid_bits)), spec.bounds.max_endpoint_bits)] for r in records]})
    _require(len(raw) <= min(spec.bounds.max_raw_bytes, spec.bounds.max_decoded_bytes), "prefix byte cap exceeded")
    return raw


class _ReadOnlyIndex:
    def __init__(self, context):
        self.context, self.root, self.spec = context, context.root, context.spec
        self._manifest = {"index": _ref_document(context.index_head)}

    def _events(self):
        yield from CollectionLock._events(self)


class _PrefixReader(ChunkStore):
    """Read-only evaluator. There is no writer lock or publication capability."""
    def __init__(self, context):
        self.context = context
        self.lock, self.spec = _ReadOnlyIndex(context), context.spec

    def _check(self):
        self.context._check()


def _bounded_refs(source, maximum):
    result = []
    for ref in source:
        _require(type(ref) is ArtifactRef and len(result) < maximum, "prefix reference cap exceeded")
        result.append(ref)
    return tuple(result)
