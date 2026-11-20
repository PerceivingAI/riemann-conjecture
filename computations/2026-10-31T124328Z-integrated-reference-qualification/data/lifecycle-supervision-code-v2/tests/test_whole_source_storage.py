"""Disposable filesystem tests for operational storage limits, not proof gates."""
from collections import namedtuple
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading

import pytest

from scripts.whole_source import storage
from scripts.whole_source.contract import ContractError

Usage = namedtuple('Usage', 'total used free')


@pytest.fixture(autouse=True)
def ample_space(monkeypatch):
    monkeypatch.setattr(storage.shutil, 'disk_usage', lambda path: Usage(1 << 50, 0, 1 << 50))
    monkeypatch.delenv(storage.ENV, raising=False)


def budget(tmp_path, ceiling=64, **kwargs):
    root = tmp_path/'run'
    return storage.StorageBudget({root: ceiling}, operation_id='operation-1',
        policy_path=root/'policy.json', code_root=tmp_path, **kwargs)


def test_low_space_refuses_without_history_change(tmp_path, monkeypatch):
    item = budget(tmp_path)
    root = tmp_path/'run'
    root.mkdir()
    history = root/'history'
    history.write_bytes(b'kept')
    monkeypatch.setattr(storage.shutil, 'disk_usage',
        lambda path: Usage(1 << 40, 0, storage.MIN_FREE_BYTES+59))
    with pytest.raises(ContractError, match='live free'):
        item.admit()
    assert history.read_bytes() == b'kept'
    assert not (root/'policy.json').exists()


def test_shared_volume_aggregates_all_future_roots(tmp_path, monkeypatch):
    item = storage.StorageBudget({tmp_path/'run': 40, tmp_path/'review': 60},
        operation_id='operation-1', policy_path=tmp_path/'run'/'policy.json', code_root=tmp_path)
    monkeypatch.setattr(storage.shutil, 'disk_usage',
        lambda path: Usage(1 << 40, 0, storage.MIN_FREE_BYTES+99))
    with pytest.raises(ContractError, match='live free'):
        item.admit()
    monkeypatch.setattr(storage.shutil, 'disk_usage',
        lambda path: Usage(1 << 40, 0, storage.MIN_FREE_BYTES+100))
    report = item.admit()
    assert len(report['volumes']) == 1
    assert report['volumes'][0]['future_growth_bytes'] == 100
    assert report['reservation'] is False
    assert report['physical_io_enforced'] is False


def test_existing_logical_bytes_are_not_charged_as_future_growth(tmp_path, monkeypatch):
    item = budget(tmp_path, 100)
    root = tmp_path/'run'
    root.mkdir()
    (root/'history').write_bytes(b'x'*80)
    monkeypatch.setattr(storage.shutil, 'disk_usage',
        lambda path: Usage(1 << 40, 0, storage.MIN_FREE_BYTES+20))
    row = item.admit()['volumes'][0]
    assert row['existing_logical_bytes'] == 80
    assert row['future_growth_bytes'] == 20
    assert row['required_free_bytes'] == storage.MIN_FREE_BYTES+20


def test_retry_does_not_reset_cumulative_allowance(tmp_path):
    first = budget(tmp_path, 6)
    first.write(tmp_path/'run'/'attempt-1', b'123456')
    second = budget(tmp_path, 6)
    with pytest.raises(ContractError, match='allowance exhausted'):
        second.write(tmp_path/'run'/'attempt-2', b'x')
    assert (tmp_path/'run'/'attempt-1').read_bytes() == b'123456'
    assert not (tmp_path/'run'/'attempt-2').exists()


@pytest.mark.parametrize('method', ['write', 'copy'])
def test_known_overflow_refuses_before_opening_output(tmp_path, method):
    item = budget(tmp_path, 3)
    target = tmp_path/'run'/'out'
    if method == 'write':
        action = lambda: item.write(target, b'four')
    else:
        source = tmp_path/'source'
        source.write_bytes(b'four')
        action = lambda: item.copy(source, target)
    with pytest.raises(ContractError, match='before write'):
        action()
    assert not target.exists()
    assert not list(target.parent.glob('.*.tmp'))


def test_stream_checks_each_chunk_before_write_and_retains_history(tmp_path):
    item = budget(tmp_path, 5)
    path = tmp_path/'run'/'events'
    with item.stream(path) as stream:
        assert stream.write(b'123') == 3
        with pytest.raises(ContractError, match='before write'):
            stream.write(b'456')
        assert path.read_bytes() == b'123'
        stream.write(b'45')
    assert path.read_bytes() == b'12345'
    with item.stream(path, 'ab') as stream:
        with pytest.raises(ContractError, match='before write'):
            stream.write(b'6')
    assert path.read_bytes() == b'12345'


def test_live_free_space_is_rechecked_before_each_chunk(tmp_path, monkeypatch):
    item = budget(tmp_path, 10)
    path = tmp_path/'run'/'events'
    with item.stream(path) as stream:
        stream.write(b'12')
        monkeypatch.setattr(storage.shutil, 'disk_usage',
            lambda path: Usage(1 << 40, 0, storage.MIN_FREE_BYTES+7))
        with pytest.raises(ContractError, match='live free'):
            stream.write(b'3')
    assert path.read_bytes() == b'12'


def test_hardlinks_are_each_charged_logically(tmp_path):
    item = budget(tmp_path, 8)
    root = tmp_path/'run'
    root.mkdir()
    original = root/'original'
    original.write_bytes(b'1234')
    try:
        os.link(original, root/'alias')
    except OSError as exc:
        pytest.skip(str(exc))
    report = item.admit()
    assert report['volumes'][0]['existing_logical_bytes'] == 8
    assert report['hardlink_discount'] is False
    with pytest.raises(ContractError, match='hardlinked'):
        with item.stream(original, 'ab'):
            pytest.fail('hardlinked append opened')
    with pytest.raises(ContractError, match='allowance exhausted'):
        item.write(root/'new', b'x')


def test_atomic_write_has_one_live_logical_copy(tmp_path):
    item = budget(tmp_path, 4)
    path = tmp_path/'run'/'artifact'
    item.write(path, b'1234')
    assert path.read_bytes() == b'1234'
    assert item.admit()['volumes'][0]['existing_logical_bytes'] == 4
    with pytest.raises(ContractError, match='immutable'):
        item.write(path, b'x')
    assert path.read_bytes() == b'1234'


def test_atomic_replacement_charges_temporary_overlap(tmp_path):
    item = budget(tmp_path, 6)
    path = tmp_path/'run'/'live'
    item.write(path, b'1234')
    with pytest.raises(ContractError, match='before write'):
        with item.stream(path, 'wb') as stream:
            stream.write(b'abc')
    assert path.read_bytes() == b'1234'
    with item.stream(path, 'wb') as stream:
        stream.write(b'ab')
        assert path.read_bytes() == b'1234'
    assert path.read_bytes() == b'ab'
    assert item.admit()['volumes'][0]['existing_logical_bytes'] == 2


def test_short_write_cannot_publish_artifact(tmp_path, monkeypatch):
    item = budget(tmp_path, 10)
    original = item._open

    class ShortStream:
        def __init__(self, stream):
            self.stream = stream

        def write(self, raw):
            return self.stream.write(memoryview(raw)[:1])

        def __getattr__(self, name):
            return getattr(self.stream, name)

    def short(path, mode, state):
        stream, index = original(path, mode, state)
        return ShortStream(stream), index

    monkeypatch.setattr(item, '_open', short)
    with pytest.raises(ContractError, match='short bounded'):
        item.write(tmp_path/'run'/'artifact', b'123')
    assert not (tmp_path/'run'/'artifact').exists()
    assert not list((tmp_path/'run').glob('.*.tmp'))


def test_nested_same_thread_writers_share_one_cumulative_account(tmp_path):
    item = budget(tmp_path, 5)
    with item.stream(tmp_path/'run'/'first') as stream:
        stream.write(b'12')
        item.write(tmp_path/'run'/'second', b'34')
        with pytest.raises(ContractError, match='before write'):
            stream.write(b'56')
        stream.write(b'5')
    assert item.admit()['volumes'][0]['existing_logical_bytes'] == 5


def test_threads_serialize_stable_lock_and_retain_lock_inode(tmp_path):
    item = budget(tmp_path, 10)
    item.admit()
    identity = item.lock_path.stat().st_ino
    started, finished = threading.Event(), threading.Event()
    failures = []

    def writer():
        started.set()
        try:
            item.write(tmp_path/'run'/'other', b'2')
        except BaseException as exc:
            failures.append(exc)
        finally:
            finished.set()

    with item.stream(tmp_path/'run'/'first') as stream:
        stream.write(b'1')
        thread = threading.Thread(target=writer)
        thread.start()
        assert started.wait(2)
        assert finished.wait(2)
    thread.join(2)
    assert finished.is_set() and not failures
    assert item.lock_path.stat().st_ino == identity


@pytest.mark.parametrize('kind', ['outside', 'traversal', 'overlap', 'unknown-bound'])
def test_unsafe_or_unknown_boundaries_are_refused(tmp_path, kind):
    item = budget(tmp_path)
    with pytest.raises(ContractError):
        if kind == 'outside':
            item.write(tmp_path/'outside', b'x')
        elif kind == 'traversal':
            item.write(tmp_path/'run'/'..'/'outside', b'x')
        elif kind == 'overlap':
            storage.StorageBudget({tmp_path/'run': 10, tmp_path/'run'/'nested': 10},
                operation_id='x', policy_path=tmp_path/'run'/'policy', code_root=tmp_path)
        else:
            budget(tmp_path, None)
    assert not (tmp_path/'outside').exists()


def test_symlink_census_and_linked_parent_are_refused(tmp_path):
    item = budget(tmp_path)
    root = tmp_path/'run'
    root.mkdir()
    outside = tmp_path/'outside'
    outside.mkdir()
    link = root/'link'
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(str(exc))
    with pytest.raises(ContractError, match='link/reparse'):
        item.admit()
    with pytest.raises(ContractError, match='link/reparse'):
        item.write(link/'artifact', b'x')
    assert not (outside/'artifact').exists()


@pytest.mark.skipif(not hasattr(os, 'mkfifo'), reason='FIFO unavailable')
def test_special_files_are_refused_without_opening_them(tmp_path):
    item = budget(tmp_path)
    root = tmp_path/'run'
    root.mkdir()
    os.mkfifo(root/'pipe')
    with pytest.raises(ContractError, match='file type'):
        item.admit()


def test_census_metadata_and_prospective_paths_are_bounded(tmp_path):
    item = budget(tmp_path, max_files=2, max_path_bytes=100)
    root = tmp_path/'run'
    root.mkdir()
    (root/'one').write_bytes(b'1')
    # The stable lock is also a retained metadata pathname.
    item.admit()
    with pytest.raises(ContractError, match='entry count'):
        item.write(root/'two', b'2')
    assert not (root/'two').exists()
    other = budget(tmp_path, max_path_bytes=4)
    with pytest.raises(ContractError, match='path exceeds'):
        other.write(root/'long-name', b'x')
    assert not (root/'long-name').exists()


def test_scope_closed_policy_digest_and_allowed_roots(tmp_path):
    item = budget(tmp_path, 65536)
    with item.scope():
        active = storage.current_budget(tmp_path/'run'/'artifact', code_root=tmp_path)
        assert active.operation_id == item.operation_id
        assert active.max_files == 262144
        with pytest.raises(ContractError, match='outside operation'):
            storage.current_budget(tmp_path/'outside', code_root=tmp_path)
        raw = item.policy_path.read_bytes()
        item.policy_path.write_bytes(raw+b' ')
        with pytest.raises(ContractError, match='digest'):
            storage.current_budget(tmp_path/'run'/'artifact', code_root=tmp_path)
        item.policy_path.write_bytes(raw)
    assert storage.current_budget(tmp_path/'outside') is None
    assert item.policy_path.exists() and item.lock_path.exists()


def test_captured_root_must_be_inside_operation_and_match_implementation(tmp_path):
    item = budget(tmp_path, 65536)
    with item.scope():
        captured = tmp_path/'run'/'attempt'/'runtime'
        assert storage.current_budget(tmp_path/'run'/'out', code_root=captured) is not None
        with pytest.raises(ContractError, match='outside operation roots'):
            storage.current_budget(tmp_path/'run'/'out', code_root=tmp_path/'unrelated')
        doc = json.loads(item.policy_path.read_bytes())
        doc['implementation_sha256'] = '0'*64
        raw = storage._canonical(doc)
        item.policy_path.write_bytes(raw)
        os.environ[storage.ENV] = storage._canonical({'path': str(item.policy_path),
            'sha256': hashlib.sha256(raw).hexdigest()}).decode('ascii')
        with pytest.raises(ContractError, match='implementation'):
            storage.current_budget(tmp_path/'run'/'out', code_root=captured)


def test_policy_unknown_fields_refused_even_with_matching_token(tmp_path):
    item = budget(tmp_path, 65536)
    with item.scope():
        doc = json.loads(item.policy_path.read_bytes())
        doc['extra'] = True
        raw = storage._canonical(doc)
        item.policy_path.write_bytes(raw)
        os.environ[storage.ENV] = storage._canonical({'path': str(item.policy_path),
            'sha256': hashlib.sha256(raw).hexdigest()}).decode('ascii')
        with pytest.raises(ContractError, match='identity'):
            storage.current_budget(tmp_path/'run'/'out', code_root=tmp_path)


def test_worker_inherits_immutable_policy_and_cumulative_limit(tmp_path):
    item = budget(tmp_path, 65536)
    target = tmp_path/'run'/'worker-output'
    with item.scope():
        existing = item.admit()['volumes'][0]['existing_logical_bytes']
        remaining = 65536-existing
        code = ('import sys; from pathlib import Path; from scripts.whole_source.storage import current_budget; '
                'p=Path(sys.argv[1]); b=current_budget(p,code_root=Path(sys.argv[2])); '
                'b.write(p,b"x"*int(sys.argv[3]))')
        result = subprocess.run([sys.executable, '-c', code, str(target), str(tmp_path), str(remaining)],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=20)
        assert result.returncode == 0, result.stderr
        assert target.stat().st_size == remaining
        with pytest.raises(ContractError, match='allowance exhausted'):
            storage.current_budget(tmp_path/'run'/'retry', code_root=tmp_path).write(tmp_path/'run'/'retry', b'x')


def test_guarded_hardlink_cannot_consume_unavailable_logical_allowance(tmp_path):
    item = budget(tmp_path, 8)
    root = tmp_path/'run'
    item.write(root/'original', b'1234')
    item.link(root/'original', root/'alias')
    assert item.admit()['volumes'][0]['existing_logical_bytes'] == 8
    with pytest.raises(ContractError, match='allowance exhausted'):
        item.link(root/'original', root/'second-alias')
    assert not (root/'second-alias').exists()
    assert (root/'original').read_bytes() == b'1234'


@pytest.mark.parametrize('early_flush', [False, True])
def test_compressed_staging_preserves_packet_bytes_across_diagnostic_flush(early_flush):
    import gzip
    import io
    from scripts.whole_source.artifacts import _CompressedWriter
    parts = [b'header\n']+[f'{index}:0x123456789abcdef\n'.encode() for index in range(4096)]
    original, current = io.BytesIO(), io.BytesIO()
    buffered = _CompressedWriter(current, storage.MIB)
    for destination in (original, buffered):
        with gzip.GzipFile(fileobj=destination, mode='wb', filename='', mtime=0) as compressed:
            for index, part in enumerate(parts):
                compressed.write(part)
                if early_flush and index == 0:
                    destination.flush()
        destination.flush()
    assert current.getvalue() == original.getvalue()
