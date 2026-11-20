"""CONTROL_ONLY exact algebra and real filesystem/process artifact controls."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
import multiprocessing
import os
from pathlib import Path

import pytest

from scripts.whole_source import artifacts
from scripts.whole_source.artifacts import (
    ArtifactError, Axis, ChunkStore, CodecBounds, CollectionLock, CollectionSpec,
    ContributionTask, IntervalRecord, QuantitySpec, StagedChunk,
    decode_integer, decode_rational, encode_integer, encode_rational,
)
from scripts.whole_source.contract import (
    ArtifactRef, ModeRange, QuantityKey, bind_problem, canonical_bytes,
    expected_domain, inspection_plan,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def problem():
    return bind_problem("retained-t081")


@pytest.fixture(scope="module")
def code_refs():
    result = []
    for relative in ("scripts/run_observability.py", "scripts/whole_source/__init__.py",
                     "scripts/whole_source/artifacts.py", "scripts/whole_source/contract.py"):
        raw = (ROOT / relative).read_bytes()
        result.append(ArtifactRef(relative, hashlib.sha256(raw).hexdigest(), len(raw)))
    return tuple(result)


def limits(**changes):
    values = dict(max_raw_bytes=8*1024*1024, max_compressed_bytes=1024*1024,
                  max_decoded_bytes=2*1024*1024, max_records=512,
                  max_endpoint_bits=65536, max_header_bytes=128*1024,
                  max_record_bytes=64*1024, max_total_bytes=256*1024*1024,
                  max_temporary_bytes=16*1024*1024, max_snapshot_bytes=64*1024*1024)
    values.update(changes)
    return CodecBounds(**values)


def collection(problem, code_refs, **changes):
    key = QuantityKey("A_model", 0)
    values = dict(role="producer",
                  quantities=(QuantitySpec(key, ModeRange(0, 6), ModeRange(0, 6),
                                           True, (Axis("cell", 0, 3),)),),
                  partition=(("cell", 1), ("columns", 2), ("rows", 2)),
                  backend="CONTROL_ONLY-exact-polynomial", backend_version="1",
                  native_threads=1, code_refs=code_refs, bounds=limits())
    values.update(changes)
    return CollectionSpec.create(problem, **values)


def attempt(lock, name="control"):
    (lock.root / "attempts" / name).mkdir()
    lock.register_attempt(name)
    return ChunkStore(lock, lock.spec, attempt_id=name)


def output_tasks(spec):
    quantity = spec.quantities[0]
    widths = dict(spec.partition)
    for row in range(quantity.rows.start, quantity.rows.stop, 2*widths["rows"]):
        for column in range(quantity.columns.start, quantity.columns.stop, 2*widths["columns"]):
            rows = ModeRange(row, min(quantity.rows.stop, row + 2*widths["rows"]))
            columns = ModeRange(column, min(quantity.columns.stop, column + 2*widths["columns"]))
            if any(r <= c or not quantity.symmetric_upper for r in rows for c in columns):
                yield ContributionTask(quantity.key, rows, columns, quantity.axes)


def partial(task, cell):
    return replace(task, axes=(Axis("cell", cell, cell+1),))


def polynomial_records(task, *, offset=Fraction(0)):
    """Nonzero signed polynomial intervals, not a production mathematical model."""
    for row in task.rows:
        for column in task.columns:
            if row > column and task.quantity.name != "F_H":
                continue
            pools = [range(a.start, a.stop, a.step) for a in task.axes]
            for contribution in itertools.product(*pools):
                cell = contribution[0] if contribution else 0
                value = Fraction((row+1)*(column+3)-2*cell*cell+(-1)**cell, 8) + offset
                yield IntervalRecord(row, column, contribution, value-Fraction(1, 32), value+Fraction(3, 64))


def publish(store, task, **kwargs):
    staged = store.stage_chunk(task, polynomial_records(task, **kwargs))
    return store.publish_chunk(task, staged)


def standalone(root, relative, raw):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return ArtifactRef(relative, hashlib.sha256(raw).hexdigest(), len(raw))


def lock_contender(root, spec, connection):
    try:
        with CollectionLock.acquire(Path(root), spec, resume=True):
            connection.send("owned")
    except ArtifactError:
        connection.send("excluded")
    finally:
        connection.close()


def worker_stage(context, task, connection):
    try:
        connection.send(context.stage_chunk(task, polynomial_records(task)))
    except BaseException as exc:
        connection.send((type(exc).__name__, str(exc)))
    finally:
        connection.close()


def test_bound_identity_and_explicit_scientific_policy(problem, code_refs):
    spec = collection(problem, code_refs)
    assert spec.problem is problem and spec.role == "producer"
    assert spec.native_threads == 1
    assert spec.collection_id == collection(problem, code_refs).collection_id
    for changes in (dict(role="analytic"), dict(native_threads=2), dict(backend_version="2"),
                    dict(partition=(("cell", 1), ("columns", 1), ("rows", 2))),
                    dict(bounds=limits(max_records=513)), dict(grid_bits=511)):
        assert collection(problem, code_refs, **changes).collection_id != spec.collection_id
    document = spec.to_dict()
    assert document["scope"] == "STRUCTURAL_ONLY"
    assert not document["analytical_acceptance"] and not document["matrix_positivity"]
    assert not document["production_admission"]
    with pytest.raises(FrozenInstanceError):
        spec.native_threads = 2
    with pytest.raises(ArtifactError):
        CollectionLock.acquire(Path("unused-inspection-output"), inspection_plan(problem))
    with pytest.raises(ArtifactError):
        collection(problem, ())


def test_wire_factory_rebinds_captured_tree_and_rejects_changed_policy(tmp_path, problem, code_refs):
    spec = collection(problem, code_refs)
    captured = tmp_path / "captured"
    for ref, raw in spec._snapshots:
        target = captured / ref.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    assert not (captured / ".git").exists()
    rebound = bind_problem("retained-t081", root=captured)
    restored = CollectionSpec.from_dict(rebound, json.loads(canonical_bytes(spec.to_dict())), code_root=captured)
    assert restored.collection_id == spec.collection_id
    assert restored.to_dict() == spec.to_dict()
    for field, value in (("format", "unknown"), ("grid_bits", True),
                         ("checkpoint_rounding", "nearest"), ("extra", 1)):
        document = spec.to_dict()
        document[field] = value
        with pytest.raises(ArtifactError):
            CollectionSpec.from_dict(rebound, document, code_root=captured)
    path = captured / code_refs[0].path
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ArtifactError, match="artifact"):
        CollectionSpec.from_dict(rebound, spec.to_dict(), code_root=captured)


def test_full_head_axes_and_physical_mode_identity(problem, code_refs):
    key = QuantityKey("weighted_head", 1)
    rows = ModeRange(1, 5)
    head = Axis("head_left", problem.N+1, problem.M, 2)
    other = replace(head, name="head_right")
    partition = (("columns", 2), ("head_left", 1), ("head_right", 1), ("rows", 2))
    quantity = QuantitySpec(key, rows, rows, True, (head, other))
    good = collection(problem, code_refs, quantities=(quantity,), partition=partition)
    assert good.quantities[0].axes == (head, other)
    for axes in ((head,), (replace(head, stop=head.stop-2), other),
                 (replace(head, start=1, stop=problem.N), other)):
        with pytest.raises(ArtifactError, match="head axis"):
            collection(problem, code_refs, quantities=(replace(quantity, axes=axes),), partition=partition)
    exterior = QuantitySpec(QuantityKey("weighted_complete_tail", 1), rows, rows, True,
                            (Axis("head", problem.N+1, problem.M, 2),))
    collection(problem, code_refs, quantities=(exterior,),
               partition=(("columns", 2), ("head", 1), ("rows", 2)))
    with pytest.raises(ArtifactError):
        collection(problem, code_refs, quantities=(replace(exterior, axes=()),),
                   partition=(("columns", 2), ("rows", 2)))
    with pytest.raises(ArtifactError, match="physical"):
        collection(problem, code_refs, quantities=(replace(quantity, rows=ModeRange(0, 3)),), partition=partition)
    with pytest.raises(ArtifactError, match="slice"):
        collection(problem, code_refs, quantities=(replace(quantity, scope="FULL_QUANTITY"),), partition=partition)


def test_real_two_process_exclusion_and_stable_inode(tmp_path, problem, code_refs):
    spec = collection(problem, code_refs)
    root = tmp_path / "collection"
    context = multiprocessing.get_context("spawn")
    with CollectionLock.acquire(root, spec) as lock:
        inode = (root / ".collection.lock").stat().st_ino
        receiver, sender = context.Pipe(duplex=False)
        child = context.Process(target=lock_contender, args=(str(root), spec, sender))
        child.start()
        sender.close()
        try:
            assert receiver.poll(30), "contender did not report OS ownership result"
            assert receiver.recv() == "excluded"
        finally:
            child.join(30)
            if child.is_alive():
                child.kill()
                child.join()
            receiver.close()
        assert child.exitcode == 0
        assert lock.is_held
        first_generation = lock.generation
    assert (root / ".collection.lock").stat().st_ino == inode
    with CollectionLock.acquire(root, spec, resume=True) as resumed:
        assert resumed.generation != first_generation
        assert (root / ".collection.lock").stat().st_ino == inode
    with pytest.raises(ArtifactError, match="unused"):
        CollectionLock.acquire(root, spec)


def test_fresh_unrelated_and_resume_incompatible_refused(tmp_path, problem, code_refs):
    spec = collection(problem, code_refs)
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    (unrelated / "mine.txt").write_bytes(b"preserved")
    with pytest.raises(ArtifactError):
        CollectionLock.acquire(unrelated, spec)
    assert (unrelated / "mine.txt").read_bytes() == b"preserved"
    root = tmp_path / "collection"
    with CollectionLock.acquire(root, spec):
        pass
    with pytest.raises(ArtifactError, match="incompatible"):
        CollectionLock.acquire(root, collection(problem, code_refs, native_threads=2), resume=True)
    snapshot = next((root / "snapshots").iterdir())
    snapshot.write_bytes(b"changed")
    with pytest.raises(ArtifactError, match="artifact"):
        CollectionLock.acquire(root, spec, resume=True)


def test_attempt_registration_worker_staging_and_late_result(tmp_path, problem, code_refs):
    spec = collection(problem, code_refs)
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        with pytest.raises(ArtifactError, match="registered"):
            ChunkStore(lock, spec, attempt_id="not-created")
        with pytest.raises((ArtifactError, FileNotFoundError)):
            lock.register_attempt("not-created")
        store = attempt(lock)
        task = partial(next(output_tasks(spec)), 0)
        context = multiprocessing.get_context("spawn")
        receiver, sender = context.Pipe(duplex=False)
        child = context.Process(target=worker_stage, args=(store.staging_context(), task, sender))
        child.start()
        sender.close()
        try:
            assert receiver.poll(30), "staging worker did not return"
            staged = receiver.recv()
        finally:
            child.join(30)
            if child.is_alive():
                child.kill()
                child.join()
            receiver.close()
        assert child.exitcode == 0 and isinstance(staged, StagedChunk), staged
        assert staged.path.is_file()
        worker_context = store.staging_context()
        assert not hasattr(worker_context, "publish_chunk")
        lock.invalidate_attempt(store.attempt_id)
        with pytest.raises(ArtifactError):
            store.publish_chunk(task, staged)
        with pytest.raises(ArtifactError):
            worker_context.stage_chunk(task, polynomial_records(task))
        with pytest.raises(ArtifactError):
            lock.register_attempt(store.attempt_id)


def test_identical_retry_conflict_stale_context_and_semantic_partition(tmp_path, problem, code_refs):
    spec = collection(problem, code_refs)
    root = tmp_path / "collection"
    with CollectionLock.acquire(root, spec) as lock:
        store = attempt(lock)
        full = next(output_tasks(spec))
        task = partial(full, 0)
        ref = publish(store, task)
        assert publish(store, task) == ref
        with pytest.raises(ArtifactError, match="conflicting"):
            publish(store, task, offset=Fraction(1))
        staged = store.stage_chunk(partial(full, 1), polynomial_records(partial(full, 1)))
        with pytest.raises(ArtifactError, match="stale"):
            store.publish_chunk(partial(full, 1), replace(staged, generation="old"))
        with pytest.raises(ArtifactError, match="partition"):
            store.stage_chunk(replace(task, axes=(Axis("cell", 0, 2),)), ())
        with pytest.raises(ArtifactError):
            store.commit_prefix(full, None, [ref, ref])
        wrong_parity = replace(task, quantity=QuantityKey("A_model", 1))
        with pytest.raises(ArtifactError):
            store.stage_chunk(wrong_parity, ())
    with CollectionLock.acquire(root, spec, resume=True) as lock:
        store = attempt(lock, "new")
        with pytest.raises(ArtifactError, match="stale"):
            store.publish_chunk(partial(full, 1), staged)


def complete_tile(store, full, *, split=False):
    refs = {cell: publish(store, partial(full, cell)) for cell in (2, 0, 1)}
    if split:
        first = store.commit_prefix(full, None, [refs[0]])
        return store.commit_prefix(full, first, [refs[2], refs[1]])
    return store.commit_prefix(full, None, [refs[2], refs[0], refs[1]])


def test_actual_nonzero_prefix_exact_rounding_ragged_cover_and_slice_seal(tmp_path, problem, code_refs):
    spec = collection(problem, code_refs)
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        store = attempt(lock)
        for full in output_tasks(spec):
            refs = {cell: publish(store, partial(full, cell)) for cell in (2, 0, 1)}
            with pytest.raises(ArtifactError, match="prefix domain"):
                store.commit_prefix(full, None, [refs[1]])
            ref = store.commit_prefix(full, None, [refs[2], refs[0], refs[1]])
            assert store.commit_prefix(full, None, [refs[1], refs[2], refs[0]]) == ref
            prefix = store.resume_prefix(full)
            assert prefix.ref == ref and prefix.covered == prefix.rounds == 3
            unit = Fraction(1, 1 << spec.grid_bits)
            originals = list(polynomial_records(full))
            for result in prefix.records:
                terms = [r for r in originals if (r.row, r.column) == (result.row, result.column)]
                assert result.lower == sum((r.lower for r in terms), Fraction(0)) - 6*unit
                assert result.upper == sum((r.upper for r in terms), Fraction(0)) + 6*unit
                assert result.lower != 0 and result.upper != 0
        seal = store.seal_quantity(spec.quantities[0].key)
        document = json.loads((lock.root / seal.path).read_bytes())
        assert document["scope"] == "STRUCTURAL_ONLY" and document["coverage_scope"] == "DECLARED_SLICE"
        assert not document["analytical_acceptance"] and not document["matrix_positivity"]
        with pytest.raises(ArtifactError, match="every real family"):
            store.seal_source()


def test_resume_consumes_same_canonical_nonzero_prefix_and_scientific_seal(tmp_path, problem, code_refs):
    spec = collection(problem, code_refs)
    tasks = list(output_tasks(spec))
    expected = {}
    roots = [tmp_path / "uninterrupted", tmp_path / "resumed"]
    with CollectionLock.acquire(roots[0], spec) as lock:
        store = attempt(lock)
        for full in tasks:
            complete_tile(store, full)
            expected[full] = store.resume_prefix(full).records
        expected_seal = store.seal_quantity(spec.quantities[0].key)
        expected_bytes = (lock.root / expected_seal.path).read_bytes()
    continuations = {}
    with CollectionLock.acquire(roots[1], spec) as lock:
        store = attempt(lock)
        for full in tasks:
            refs = {cell: publish(store, partial(full, cell)) for cell in (2, 0, 1)}
            first = store.commit_prefix(full, None, [refs[0]])
            continuations[full] = (first, refs)
        generation = lock.generation
    with CollectionLock.acquire(roots[1], spec, resume=True) as lock:
        assert lock.generation != generation
        store = attempt(lock, "continued")
        for full, (first, refs) in continuations.items():
            prefix = store.resume_prefix(full)
            assert prefix.ref == first and prefix.covered == 1
            store.commit_prefix(full, first, [refs[1], refs[2]])
            assert store.resume_prefix(full).records == expected[full]
            with pytest.raises(ArtifactError):
                store.commit_prefix(full, first, [refs[0]])
        actual_seal = store.seal_quantity(spec.quantities[0].key)
        assert actual_seal.sha256 == expected_seal.sha256
        assert (lock.root / actual_seal.path).read_bytes() == expected_bytes


def test_missing_coordinate_cannot_seal_by_count(tmp_path, problem, code_refs):
    spec = collection(problem, code_refs)
    tasks = list(output_tasks(spec))
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        store = attempt(lock)
        complete_tile(store, tasks[0])
        with pytest.raises(ArtifactError, match="semantic"):
            store.seal_quantity(spec.quantities[0].key)
        malformed = list(polynomial_records(partial(tasks[-1], 0)))
        malformed[0] = replace(malformed[0], row=0, column=0)
        with pytest.raises(ArtifactError, match="order/domain"):
            store.stage_chunk(partial(tasks[-1], 0), malformed)


@pytest.mark.parametrize("text", ["0X1", "+0x1", "0x01", "-0x0", "0xA", "1", "0x", " 0x1"])
def test_noncanonical_signed_hex_refused(text):
    with pytest.raises(ArtifactError):
        decode_integer(text, 65536)


def test_actual_maximum_declared_endpoint_bits_and_rationals(tmp_path, problem, code_refs):
    spec = collection(problem, code_refs)
    bits = spec.bounds.max_endpoint_bits
    maximum = (1 << bits)-1
    assert decode_integer(encode_integer(maximum, bits), bits) == maximum
    assert decode_integer(encode_integer(-maximum, bits), bits) == -maximum
    rational = Fraction(-(1 << (bits-1))+1, (1 << (bits-2))+1)
    assert decode_rational(encode_rational(rational, bits), bits) == rational
    for value in ({"numerator": "0x1", "denominator": "0x0"},
                  {"numerator": "0x2", "denominator": "0x2"},
                  {"numerator": "0x1", "denominator": "-0x1"}):
        with pytest.raises(ArtifactError):
            decode_rational(value, bits)
    with pytest.raises(ArtifactError):
        decode_integer(hex(1 << bits), bits)
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        store = attempt(lock)
        full = next(output_tasks(spec))
        task = partial(full, 0)
        value = Fraction((1 << bits)-2, 1 << spec.grid_bits)
        records = [replace(r, lower=-value, upper=value) for r in polynomial_records(task)]
        ref = store.publish_chunk(task, store.stage_chunk(task, records))
        snapshot = store.read_chunk(ref)
        assert snapshot.records[0].upper.numerator.bit_length() == bits
        assert snapshot.records[0].lower < -value and snapshot.records[0].upper > value
        with pytest.raises(ArtifactError, match="cap"):
            store.stage_chunk(partial(full, 1), [replace(r, lower=Fraction(0), upper=Fraction(1 << bits))
                                               for r in polynomial_records(partial(full, 1))])


def altered_chunk(store, ref, mutate):
    raw = (store.lock.root / ref.path).read_bytes()
    decoded = gzip.decompress(raw)
    changed = mutate(decoded)
    return standalone(store.lock.root, "attempts/" + store.attempt_id + "/staging/control-malformed-" + hashlib.sha256(changed).hexdigest(),
                      gzip.compress(changed, mtime=0))


@pytest.mark.parametrize("mutation", ["duplicate", "reversed", "order", "zero-denominator", "oversized", "truncated", "extra"])
def test_actual_malformed_compressed_payloads_refused(tmp_path, problem, code_refs, mutation):
    spec = collection(problem, code_refs)
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        store = attempt(lock)
        task = partial(next(output_tasks(spec)), 0)
        ref = publish(store, task)
        def mutate(decoded):
            lines = decoded.splitlines(keepends=True)
            if mutation == "duplicate":
                lines[0] = lines[0].replace(b'{', b'{"role":"producer",', 1)
            elif mutation == "reversed":
                record = json.loads(lines[1])
                record[3:5] = ["0x2", "-0x2"]
                lines[1] = canonical_bytes(record)
            elif mutation == "order":
                lines[1], lines[2] = lines[2], lines[1]
            elif mutation == "zero-denominator":
                record = json.loads(lines[1])
                record[3] = {"numerator": "0x1", "denominator": "0x0"}
                lines[1] = canonical_bytes(record)
            elif mutation == "oversized":
                lines[1] = b'[' + b'0'*spec.bounds.max_record_bytes + b']\n'
            elif mutation == "truncated":
                lines = lines[:-1]
            elif mutation == "extra":
                lines.append(lines[-1])
            return b''.join(lines)
        malformed = altered_chunk(store, ref, mutate)
        with pytest.raises(ArtifactError):
            store.read_chunk(malformed)
        raw = (lock.root / ref.path).read_bytes()
        corrupt = standalone(lock.root, "attempts/control/staging/corrupt", raw[:-7] + b"garbage")
        with pytest.raises(ArtifactError):
            store.read_chunk(corrupt)


def test_snapshot_bytes_survive_path_replacement_and_hash_mismatch_rejects(tmp_path, problem, code_refs):
    spec = collection(problem, code_refs)
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        store = attempt(lock)
        task = partial(next(output_tasks(spec)), 0)
        ref = publish(store, task)
        snapshot = store.read_chunk(ref)
        accepted = snapshot.records
        (lock.root / ref.path).write_bytes(b"replaced")
        assert snapshot.records == accepted and accepted[0].lower != 0
        with pytest.raises(ArtifactError, match="artifact"):
            store.read_chunk(ref)


def test_confinement_alias_escape_and_symlink_refused(tmp_path, problem, code_refs):
    spec = collection(problem, code_refs)
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        store = attempt(lock)
        ref = publish(store, partial(next(output_tasks(spec)), 0))
        for path in ("../outside", "chunks//alias", "chunks/./alias", "C:/outside", "chunks\\alias"):
            with pytest.raises((ArtifactError, ValueError)):
                store.read_chunk(ArtifactRef(path, ref.sha256, ref.size))
        target = tmp_path / "outside"
        target.write_bytes((lock.root / ref.path).read_bytes())
        link = lock.root / "chunks" / "link"
        try:
            link.symlink_to(target)
        except OSError:
            pytest.skip("OS does not grant symlink creation")
        with pytest.raises(ArtifactError, match="symlink"):
            store.read_chunk(ArtifactRef("chunks/link", ref.sha256, ref.size))


@pytest.mark.parametrize("cap", ["max_compressed_bytes", "max_decoded_bytes", "max_records", "max_temporary_bytes", "max_total_bytes"])
def test_real_caps_never_publish_success(tmp_path, problem, code_refs, cap):
    value = {"max_compressed_bytes": 64, "max_decoded_bytes": 512, "max_records": 1,
             "max_temporary_bytes": 128, "max_total_bytes": 128}[cap]
    changes = {cap: value}
    if cap == "max_decoded_bytes":
        changes["max_record_bytes"] = 512
    spec = collection(problem, code_refs, bounds=limits(**changes))
    root = tmp_path / "collection"
    with pytest.raises((ArtifactError, OSError)):
        with CollectionLock.acquire(root, spec) as lock:
            store = attempt(lock)
            publish(store, partial(next(output_tasks(spec)), 0))
            store.seal_quantity(spec.quantities[0].key)
    if (root / "collection.json").exists():
        manifest = json.loads((root / "collection.json").read_bytes())
        assert manifest["index"] is None


def test_fsync_refusal_keeps_manifest_before_uncommitted_chunk(tmp_path, problem, code_refs, monkeypatch):
    spec = collection(problem, code_refs)
    root = tmp_path / "collection"
    with CollectionLock.acquire(root, spec) as lock:
        store = attempt(lock)
        task = partial(next(output_tasks(spec)), 0)
        staged = store.stage_chunk(task, polynomial_records(task))
        manifest = (root / "collection.json").read_bytes()
        def refuse(fd):
            raise OSError("CONTROL_ONLY fsync refusal")
        with monkeypatch.context() as patch:
            patch.setattr(artifacts.os, "fsync", refuse)
            with pytest.raises(OSError, match="fsync refusal"):
                store.publish_chunk(task, staged)
        assert (root / "collection.json").read_bytes() == manifest
    with CollectionLock.acquire(root, spec, resume=True) as lock:
        store = attempt(lock, "retry")
        assert store.resume_prefix(next(output_tasks(spec))) is None


def test_rename_refusal_manifest_last_and_identical_retry(tmp_path, problem, code_refs, monkeypatch):
    spec = collection(problem, code_refs)
    root = tmp_path / "collection"
    with CollectionLock.acquire(root, spec) as lock:
        store = attempt(lock)
        full = next(output_tasks(spec))
        ref = publish(store, partial(full, 0))
        before = (root / "collection.json").read_bytes()
        original_replace = os.replace
        def refuse(source, destination):
            if Path(destination).name == "collection.json":
                raise PermissionError("CONTROL_ONLY manifest rename refusal")
            return original_replace(source, destination)
        with monkeypatch.context() as patch:
            patch.setattr(artifacts.os, "replace", refuse)
            with pytest.raises(PermissionError):
                store.commit_prefix(full, None, [ref])
        assert (root / "collection.json").read_bytes() == before
        assert store.resume_prefix(full) is None
        assert store.commit_prefix(full, None, [ref]).path.startswith("prefixes/")


def test_real_short_write_and_quota_refusal_do_not_advance_manifest(tmp_path, problem, code_refs, monkeypatch):
    spec = collection(problem, code_refs)
    root = tmp_path / "collection"
    with CollectionLock.acquire(root, spec) as lock:
        store = attempt(lock)
        task = partial(next(output_tasks(spec)), 0)
        staged = store.stage_chunk(task, polynomial_records(task))
        before = (root / "collection.json").read_bytes()
        original_open = Path.open
        class ShortFile:
            def __init__(self, wrapped):
                self.wrapped = wrapped
            def __enter__(self):
                self.wrapped.__enter__()
                return self
            def __exit__(self, *args):
                return self.wrapped.__exit__(*args)
            def write(self, raw):
                return self.wrapped.write(raw[:max(1, len(raw)//2)])
            def __getattr__(self, name):
                return getattr(self.wrapped, name)
        def opening(path, mode="r", *args, **kwargs):
            result = original_open(path, mode, *args, **kwargs)
            return ShortFile(result) if mode == "xb" and path.parent.name == "chunks" else result
        with monkeypatch.context() as patch:
            patch.setattr(Path, "open", opening)
            with pytest.raises(OSError, match="short"):
                store.publish_chunk(task, staged)
        assert (root / "collection.json").read_bytes() == before
        # A genuine retained file consumes the declared volume. No fake free-space detector.
        occupied = root / "attempts" / "control" / "quota-evidence"
        with occupied.open("wb") as stream:
            stream.truncate(spec.bounds.max_total_bytes)
        with pytest.raises(ArtifactError, match="volume"):
            store.publish_chunk(task, staged)
        assert (root / "collection.json").read_bytes() == before


def test_stage_capability_rejects_released_owner_without_replacement(tmp_path, problem, code_refs):
    spec = collection(problem, code_refs)
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        store = attempt(lock)
        context = store.staging_context()
        task = partial(next(output_tasks(spec)), 0)
    with pytest.raises(ArtifactError, match="no longer holds"):
        context.stage_chunk(task, polynomial_records(task))


def test_staged_prefix_cannot_cross_intervening_index_commit(tmp_path, problem, code_refs):
    spec = collection(problem, code_refs)
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        store = attempt(lock)
        full = next(output_tasks(spec))
        first = publish(store, partial(full, 0))
        staged = store.staging_context().stage_prefix(full, None, [first])
        publish(store, partial(full, 1))
        with pytest.raises(ArtifactError, match="stale staged prefix"):
            store.publish_prefix(staged)
        assert store.resume_prefix(full) is None
