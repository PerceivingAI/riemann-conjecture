"""Regression checks for persisted-data trust and whole-slice writer ownership."""
from fractions import Fraction
import hashlib
import json
import os
import multiprocessing
from pathlib import Path

import pytest

from scripts.whole_source.artifacts import (
    ArtifactError, Axis, CodecBounds, CollectionLock, CollectionSpec, QuantitySpec,
)
from scripts.whole_source.contract import ArtifactRef, ModeRange, QuantityKey, ROOT, bind_problem


@pytest.fixture(scope='module')
def problem():
    return bind_problem('retained-t081')


def small_collection(problem):
    refs = []
    for name in ('scripts/run_observability.py', 'scripts/whole_source/__init__.py',
                 'scripts/whole_source/artifacts.py', 'scripts/whole_source/contract.py'):
        raw = (ROOT/name).read_bytes()
        refs.append(ArtifactRef(name, hashlib.sha256(raw).hexdigest(), len(raw)))
    return CollectionSpec.create(problem, role='producer',
        quantities=(QuantitySpec(QuantityKey('A_model', 0), ModeRange(0, 2), ModeRange(0, 2),
                                 True, (Axis('cell', 0, 1),)),),
        partition=(('cell', 1), ('columns', 1), ('rows', 1)),
        backend='CONTROL_ONLY-exact-polynomial', backend_version='1', native_threads=1,
        code_refs=tuple(refs),
        bounds=CodecBounds(8*1024**2, 1024**2, 2*1024**2, 512, 65536, 128*1024,
                           64*1024, 256*1024**2, 16*1024**2, 64*1024**2))


def test_prepared_lock_cannot_modify_an_unrelated_file(tmp_path, problem):
    original = b'Unrelated local data must stay unchanged.\n'*32
    unrelated = tmp_path/'unrelated.txt'
    unrelated.write_bytes(original)
    collection = tmp_path/'collection'
    collection.mkdir()
    os.link(unrelated, collection/'.collection.lock')
    refused = None
    try:
        with CollectionLock.acquire(collection, small_collection(problem)):
            pass
    except ArtifactError as exc:
        refused = exc
    assert unrelated.read_bytes() == original
    assert refused is not None and 'single-link' in str(refused)
    assert {path.name for path in collection.iterdir()} == {'.collection.lock'}


def test_new_link_on_a_held_lock_refuses_further_publication(tmp_path, problem):
    with CollectionLock.acquire(tmp_path/'collection', small_collection(problem)) as lock:
        (lock.root/'attempts/must_not_publish').mkdir()
        os.link(lock.root/'.collection.lock', tmp_path/'unrelated-alias')
        with pytest.raises(ArtifactError, match='single-link'):
            lock.register_attempt('must_not_publish')
        assert not (lock.root/'attempts/must_not_publish/artifact-owner.json').exists()


def _slice_contender(root, result):
    from scripts.whole_source.contract import ContractError
    from scripts.whole_source.slice import _slice_writer
    try:
        with _slice_writer(Path(root), resume=True):
            result.send("acquired")
    except ContractError as exc:
        result.send(str(exc))
    finally:
        result.close()


def test_slice_writer_excludes_another_process_and_allows_resume(tmp_path):
    from scripts.whole_source.slice import _slice_writer
    root = tmp_path/"slice"
    context = multiprocessing.get_context("spawn")
    received, sent = context.Pipe(duplex=False)
    with _slice_writer(root, resume=False):
        state = root/"slice-state.json"
        state.write_text('{"status":"RUNNING"}', encoding="utf-8")
        process = context.Process(target=_slice_contender, args=(str(root), sent))
        process.start()
        sent.close()
        try:
            assert received.poll(30), "slice contender did not report ownership"
            assert received.recv() == "arithmetic slice already owned"
            process.join(30)
            assert process.exitcode == 0
            assert json.loads(state.read_text(encoding="utf-8")) == {"status": "RUNNING"}
        finally:
            if process.is_alive():
                process.terminate()
                process.join(30)
            received.close()
    with _slice_writer(root, resume=True):
        state.write_text('{"status":"COMPLETE"}', encoding="utf-8")
    assert json.loads(state.read_text(encoding="utf-8")) == {"status": "COMPLETE"}
