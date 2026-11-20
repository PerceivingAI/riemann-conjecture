"""Cooperating-writer logical storage limits, not reservations or physical I/O caps.

Every pathname is charged, including hardlinks. Free-space forecasts concern only
future growth; existing logical bytes have already consumed their own storage.
The stable operation lock is never held while acquiring a collection lock.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import stat
import threading
import time
import uuid

from scripts.whole_source.contract import ContractError

MIB = 1024 * 1024
__all__ = ('StorageBudget', 'current_budget', 'guarded_open')
MIN_FREE_BYTES = 64 * MIB
FORMAT = 'whole-source-storage-policy-v1'
ENV = 'RH_WHOLE_SOURCE_STORAGE_POLICY'
_CODE_ROOT = Path(__file__).resolve().parents[2]
_MAX_POLICY_BYTES = MIB
_MAX_ENTRIES = 262_144
_MAX_DEPTH = 128
_STATES = {}
_STATES_LOCK = threading.Lock()


def _require(condition, message):
    if not condition:
        raise ContractError(message)


def _integer(value, name, minimum=0):
    _require(type(value) is int and minimum <= value <= 1 << 60,
             'invalid storage '+name)
    return value


def _absolute(path):
    _require(isinstance(path, (str, os.PathLike)), 'invalid storage path type')
    path = Path(path)
    _require(path.is_absolute() and '..' not in path.parts,
             'absolute non-traversing storage path required')
    _require(len(str(path).encode('utf-8')) <= 32768 and len(path.parts) <= _MAX_DEPTH,
             'absolute storage path exceeds metadata bound')
    return path


def _safe_info(path):
    info = path.lstat()
    _require(not stat.S_ISLNK(info.st_mode) and
             not getattr(info, 'st_file_attributes', 0) & 0x400,
             'unsafe link/reparse storage path')
    _require(stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode),
             'unsafe storage file type')
    return info


def _inspect(path):
    """Check every existing ancestor without resolving away a link."""
    path = _absolute(path)
    nearest = None
    for part in reversed((path, *path.parents)):
        try:
            info = _safe_info(part)
        except FileNotFoundError:
            continue
        if part != path:
            _require(stat.S_ISDIR(info.st_mode), 'non-directory storage ancestor')
        nearest = (part, info)
    _require(nearest is not None, 'missing storage volume ancestor')
    return nearest


def _volume(path):
    # st_dev identifies the actual filesystem, not a drive-letter spelling.
    return str(_inspect(path)[1].st_dev)


def _under(path, root):
    return path == root or root in path.parents


def _census(root, volume, max_files, max_path_bytes):
    """Depth-bounded streaming traversal; never retain a tree-sized listing."""
    _inspect(root)
    result = {'logical_bytes': 0, 'entry_count': 0, 'file_count': 0, 'path_bytes': 0}
    if not root.exists():
        return result
    _require(root.is_dir(), 'storage root must be a directory')

    def walk(directory, depth):
        _require(depth <= _MAX_DEPTH, 'storage census depth exceeds bound')
        with os.scandir(directory) as children:
            for entry in children:
                result['entry_count'] += 1
                _require(result['entry_count'] <= max_files,
                         'storage census entry count exceeds bound')
                path = Path(entry.path)
                length = len(path.relative_to(root).as_posix().encode('utf-8'))
                _require(length <= max_path_bytes, 'storage census path exceeds bound')
                result['path_bytes'] += length
                info = _safe_info(path)
                _require(str(info.st_dev) == volume,
                         'storage root crosses a filesystem boundary')
                if stat.S_ISDIR(info.st_mode):
                    walk(path, depth + 1)
                else:
                    result['file_count'] += 1
                    result['logical_bytes'] += info.st_size
                    _integer(result['logical_bytes'], 'logical census bytes')
    walk(root, 0)
    return result


def _canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True)+'\n').encode('ascii')


def _decode(raw):
    from scripts.whole_source.admission import admit_decode
    admit_decode(len(raw))
    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, 'duplicate storage policy field')
            result[key] = value
        return result
    try:
        value = json.loads(raw, object_pairs_hook=pairs)
    except (ValueError, UnicodeError) as exc:
        raise ContractError('invalid storage policy JSON') from exc
    _require(type(value) is dict, 'storage policy object required')
    return value


@dataclass
class _LockState:
    mutex: object = field(default_factory=threading.RLock)
    depth: int = 0
    stream: object = None
    totals: object = None
    identity: object = None


def _state(path):
    key = (os.getpid(), os.path.normcase(str(path)))
    with _STATES_LOCK:
        return _STATES.setdefault(key, _LockState())


def _os_lock(stream, acquire):
    if os.name == 'nt':
        import msvcrt
        stream.seek(0)
        if not acquire:
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            return
        while True:
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                return
            except OSError as exc:
                import errno
                if exc.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                    raise
                time.sleep(0.01)
    else:
        import fcntl
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX if acquire else fcntl.LOCK_UN)


class StorageBudget:
    """One operation's immutable, cumulative pathname allowances.

    ``roots`` maps disjoint absolute directory paths to total logical ceilings,
    including retained history and operational metadata. A ceiling is not an
    additional allowance on each retry. Missing or unknown bounds are refused.
    ``policy_path`` names fresh operation metadata, never an existing history file.
    """

    def __init__(self, roots, *, operation_id, policy_path,
                 min_free_bytes=MIN_FREE_BYTES, code_root=None,
                 max_files=_MAX_ENTRIES, max_path_bytes=1024):
        _require(type(operation_id) is str and 0 < len(operation_id) <= 128 and
                 all(c.isalnum() or c in '-_.' for c in operation_id),
                 'invalid storage operation identity')
        _require(hasattr(roots, 'items') and 0 < len(roots) <= 32,
                 'bounded storage roots required')
        self.roots = tuple(sorted(((_absolute(path), _integer(limit, 'logical ceiling'))
                                  for path, limit in roots.items()), key=lambda pair: str(pair[0])))
        for index, (root, _) in enumerate(self.roots):
            _inspect(root)
            for other, _ in self.roots[:index]:
                _require(not _under(root, other) and not _under(other, root),
                         'overlapping storage roots')
        self.operation_id = operation_id
        self.policy_path = _absolute(policy_path)
        self.code_root = _absolute(_CODE_ROOT if code_root is None else code_root)
        _inspect(self.code_root)
        _require(_under(self.policy_path, self.code_root),
                 'storage policy must be inside captured code root')
        self.min_free_bytes = _integer(min_free_bytes, 'minimum free bytes', MIN_FREE_BYTES)
        self.max_files = _integer(max_files, 'maximum census entries', 1)
        self.max_path_bytes = _integer(max_path_bytes, 'maximum path bytes', 1)
        _require(self.max_files <= _MAX_ENTRIES and self.max_path_bytes <= 32768,
                 'storage census metadata bounds exceed limits')
        self.volumes = tuple(_volume(root) for root, _ in self.roots)
        self.lock_path = self.policy_path.with_name(self.policy_path.name+'.lock')
        self._document = {'format': FORMAT, 'operation_id': operation_id,
                          'code_root': str(self.code_root),
                          'policy_path': str(self.policy_path),
                          'minimum_free_bytes': self.min_free_bytes,
                          'max_files': self.max_files, 'max_path_bytes': self.max_path_bytes,
                          'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                          'roots': [{'path': str(root), 'logical_ceiling': limit, 'volume': volume}
                                    for (root, limit), volume in zip(self.roots, self.volumes)]}
        self.raw = _canonical(self._document)
        _require(len(self.raw) <= _MAX_POLICY_BYTES, 'storage policy exceeds bound')
        self.digest = hashlib.sha256(self.raw).hexdigest()

    def _index(self, path):
        path = _absolute(path)
        _inspect(path)
        for index, (root, _) in enumerate(self.roots):
            if _under(path, root) and path != root:
                relative = path.relative_to(root)
                _require(len(relative.as_posix().encode('utf-8')) <= self.max_path_bytes and
                         len(relative.parts) <= _MAX_DEPTH,
                         'storage write path exceeds metadata bound')
                _require(_volume(path) == self.volumes[index], 'changed storage volume')
                return path, index
        raise ContractError('write path outside operation storage roots')

    def _totals(self):
        rows = []
        for (root, limit), volume in zip(self.roots, self.volumes):
            _require(_volume(root) == volume, 'changed storage root volume')
            row = _census(root, volume, self.max_files, self.max_path_bytes)
            _require(row['logical_bytes'] <= limit,
                     'cumulative storage logical allowance exhausted')
            rows.append(row)
        _require(sum(row['entry_count'] for row in rows) <= self.max_files,
                 'storage census entry count exceeds bound')
        return rows

    def _check(self, totals, *, index=None, growth=0):
        _integer(growth, 'write growth')
        state = _state(self.lock_path)
        opened, named = os.fstat(state.stream.fileno()), _safe_info(self.lock_path)
        _require((opened.st_dev, opened.st_ino, opened.st_nlink) ==
                 (named.st_dev, named.st_ino, 1), 'storage lock inode replaced')
        if index is not None:
            _require(totals[index]['logical_bytes']+growth <= self.roots[index][1],
                     'cumulative storage logical allowance exhausted before write')
        grouped = {}
        for idx, ((root, limit), volume) in enumerate(zip(self.roots, self.volumes)):
            row = grouped.setdefault(volume, {'volume': volume, 'existing_logical_bytes': 0,
                'logical_ceiling_bytes': 0, 'future_growth_bytes': 0, 'roots': [],
                'available_bytes': None})
            row['existing_logical_bytes'] += totals[idx]['logical_bytes']
            row['logical_ceiling_bytes'] += limit
            row['future_growth_bytes'] += limit-totals[idx]['logical_bytes']
            row['roots'].append(str(root))
            free = shutil.disk_usage(_inspect(root)[0]).free
            row['available_bytes'] = free if row['available_bytes'] is None else min(row['available_bytes'], free)
        for row in grouped.values():
            row['minimum_free_bytes'] = self.min_free_bytes
            row['required_free_bytes'] = row['future_growth_bytes']+self.min_free_bytes
            _require(row['available_bytes'] >= row['required_free_bytes'],
                     'insufficient live free storage for remaining forecast and headroom')
        return {'format': 'whole-source-storage-admission-v1', 'operation_id': self.operation_id,
                'volumes': list(grouped.values()),
                'roots': [dict(row, path=str(root), logical_ceiling_bytes=limit)
                          for row, (root, limit) in zip(totals, self.roots)],
                'file_count': sum(row['file_count'] for row in totals),
                'path_bytes': sum(row['path_bytes'] for row in totals),
                'reservation': False, 'physical_io_enforced': False, 'hardlink_discount': False}

    @contextmanager
    def _locked(self):
        state = _state(self.lock_path)
        with state.mutex:
            if state.depth:
                _require(state.identity == self.digest, 'conflicting nested storage policy')
            else:
                _inspect(self.lock_path)
                self.lock_path.parent.mkdir(parents=True, exist_ok=True)
                _inspect(self.lock_path)
                descriptor = os.open(self.lock_path, os.O_RDWR | os.O_CREAT |
                                     getattr(os, 'O_NOFOLLOW', 0), 0o600)
                state.stream = os.fdopen(descriptor, 'r+b', buffering=0)
                try:
                    _require(stat.S_ISREG(os.fstat(descriptor).st_mode) and
                             os.fstat(descriptor).st_nlink == 1, 'unsafe storage lock file')
                    _os_lock(state.stream, True)
                    state.identity = self.digest
                    state.totals = self._totals()
                except BaseException:
                    state.stream.close()
                    state.stream = None
                    state.identity = None
                    raise
            state.depth += 1
            try:
                yield state
            finally:
                state.depth -= 1
                if not state.depth:
                    try:
                        _os_lock(state.stream, False)
                    finally:
                        state.stream.close()
                        state.stream = None
                        state.totals = None
                        state.identity = None

    def admit(self, *, path=None, required_bytes=0):
        """Check the forecast, optionally requiring space before attempt allocation."""
        _integer(required_bytes, 'prospective allocation bytes')
        _require(path is not None or required_bytes == 0,
                 'prospective storage allocation path required')
        index = self._index(path)[1] if path is not None else None
        with self._locked() as state:
            return self._check(state.totals, index=index, growth=required_bytes)

    def _open(self, path, mode, state):
        path, index = self._index(path)
        root = self.roots[index][0]
        missing = []
        for candidate in (path, *path.parents):
            if candidate == root:
                break
            if not candidate.exists():
                missing.append(candidate)
        _require(sum(row['entry_count'] for row in state.totals)+len(missing) <= self.max_files,
                 'storage write entry count exceeds bound before write')
        if path.exists():
            _require(_safe_info(path).st_nlink == 1, 'unsafe hardlinked storage write file')
        path.parent.mkdir(parents=True, exist_ok=True)
        _inspect(path)
        flags = os.O_WRONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
        flags |= os.O_CREAT | (os.O_EXCL if mode == 'xb' else os.O_APPEND)
        descriptor = os.open(path, flags, 0o600)
        try:
            info = os.fstat(descriptor)
            _require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                     str(info.st_dev) == self.volumes[index], 'unsafe storage write file')
            row = state.totals[index]
            row['entry_count'] += len(missing)
            row['file_count'] += int(path in missing)
            row['path_bytes'] += sum(len(item.relative_to(root).as_posix().encode('utf-8'))
                                     for item in missing)
            return os.fdopen(descriptor, mode, buffering=0), index
        except BaseException:
            os.close(descriptor)
            raise

    @contextmanager
    def stream(self, path, mode='xb'):
        """Capped binary writes. ``wb`` atomically replaces with temporary overlap charged."""
        _require(mode in ('xb', 'ab', 'wb'), 'invalid bounded storage stream mode')
        if mode == 'wb':
            with self._replacement(path) as outgoing:
                yield outgoing
            return
        with self._locked() as state:
            self._check(state.totals)
            stream, index = self._open(path, mode, state)
        bounded = _BoundedStream(self, stream, index, Path(path))
        try:
            yield bounded
            if not bounded.closed:
                bounded.flush()
                os.fsync(bounded.fileno())
        finally:
            stream.close()

    def _renamed(self, state, temporary, path, index, old_size=0):
        row = state.totals[index]
        row['logical_bytes'] -= old_size
        row['path_bytes'] -= len(temporary.name.encode('utf-8'))-len(path.name.encode('utf-8'))

    @contextmanager
    def _replacement(self, path):
        path, index = self._index(path)
        with self._locked() as state:
            exists = path.exists()
            old_size = _safe_info(path).st_size if exists else 0
            temporary = path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
            try:
                with self.stream(temporary) as outgoing:
                    yield outgoing
                _inspect(path)
                os.replace(temporary, path)
                self._renamed(state, temporary, path, index, old_size)
                if exists:
                    row = state.totals[index]
                    row['entry_count'] -= 1
                    row['file_count'] -= 1
                    row['path_bytes'] -= len(path.relative_to(self.roots[index][0]).as_posix().encode('utf-8'))
            except BaseException:
                if temporary.exists():
                    temporary.unlink()
                    state.totals = self._totals()
                raise

    def _publish(self, path, size, produce):
        path, index = self._index(path)
        with self._locked() as state:
            _require(not path.exists(), 'immutable storage artifact already exists')
            # Publication renames one temporary pathname into one final pathname.
            # Neither the census nor this prospective check counts both as live.
            self._check(state.totals, index=index, growth=size)
            temporary = path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
            try:
                with self.stream(temporary) as outgoing:
                    produce(outgoing)
                    _require(outgoing.tell() == size, 'storage source changed during copy/write')
                _inspect(path)
                _require(not path.exists(), 'immutable storage artifact already exists')
                os.replace(temporary, path)
                self._renamed(state, temporary, path, index)
            except BaseException:
                # Only this call's unpublished temporary is removable, never history.
                if temporary.exists():
                    temporary.unlink()
                    state.totals = self._totals()
                raise
        return path

    def write(self, path, raw):
        _require(isinstance(raw, (bytes, bytearray, memoryview)), 'storage binary bytes required')
        return self._publish(path, memoryview(raw).nbytes, lambda outgoing: outgoing.write(raw))

    def copy(self, source, target):
        source = _absolute(source)
        _inspect(source)
        info = _safe_info(source)
        _require(stat.S_ISREG(info.st_mode), 'regular storage copy source required')
        def produce(outgoing):
            flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
            with os.fdopen(os.open(source, flags), 'rb', buffering=0) as incoming:
                opened = os.fstat(incoming.fileno())
                _require((opened.st_dev, opened.st_ino, opened.st_size) ==
                         (info.st_dev, info.st_ino, info.st_size), 'storage copy source changed')
                while block := incoming.read(MIB):
                    outgoing.write(block)
                final = os.fstat(incoming.fileno())
                _require((final.st_size, final.st_mtime_ns) == (info.st_size, info.st_mtime_ns),
                         'storage copy source changed')
        return self._publish(target, info.st_size, produce)

    def link(self, source, target):
        """Publish a preserved inode while charging every logical pathname."""
        source = _absolute(source)
        _inspect(source)
        info = _safe_info(source)
        _require(stat.S_ISREG(info.st_mode), 'regular storage link source required')
        target, index = self._index(target)
        with self._locked() as state:
            self._check(state.totals, index=index, growth=info.st_size)
            _require(sum(row['entry_count'] for row in state.totals)+len(target.parts) <= self.max_files,
                     'storage link entry count exceeds bound')
            target.parent.mkdir(parents=True, exist_ok=True)
            _inspect(target)
            os.link(source, target)

    def _publish_policy(self):
        _inspect(self.policy_path)
        if self.policy_path.exists():
            _require(_policy_bytes(self.policy_path) == self.raw, 'changed immutable storage policy')
            return
        _require(any(_under(self.policy_path, root) and self.policy_path != root
                     for root, _ in self.roots), 'policy must be inside an allowed storage root')
        self.write(self.policy_path, self.raw)

    @contextmanager
    def scope(self):
        """Publish a digest-bound policy token inherited by cooperating workers."""
        with self._locked() as state:
            self._check(state.totals)
            self._publish_policy()
            state.totals = self._totals()
            self._check(state.totals)
        previous = os.environ.get(ENV)
        os.environ[ENV] = _canonical({'path': str(self.policy_path), 'sha256': self.digest}).decode('ascii')
        try:
            yield self
        finally:
            if previous is None:
                os.environ.pop(ENV, None)
            else:
                os.environ[ENV] = previous


class _BoundedStream(io.RawIOBase):
    def __init__(self, budget, stream, index, path):
        self._budget, self._path = budget, path
        self._stream, self._index = stream, index

    def write(self, raw):
        _require(isinstance(raw, (bytes, bytearray, memoryview)), 'storage binary bytes required')
        size = memoryview(raw).nbytes
        with self._budget._locked() as state:
            self._budget._check(state.totals, index=self._index, growth=size)
            opened, named = os.fstat(self._stream.fileno()), _safe_info(self._path)
            _require((opened.st_dev, opened.st_ino) == (named.st_dev, named.st_ino) and
                     named.st_nlink == 1, 'bounded stream pathname changed')
            count = self._stream.write(raw)
            state.totals[self._index]['logical_bytes'] += count or 0
            _require(count == size, 'short bounded storage write')
            return count

    def flush(self):
        if not self._stream.closed:
            return self._stream.flush()

    def fileno(self):
        return self._stream.fileno()

    def tell(self):
        return self._stream.tell()

    @property
    def closed(self):
        return self._stream.closed

    def writable(self):
        return True

    def close(self):
        if not self._stream.closed:
            try:
                super().close()
            finally:
                self._stream.close()


def _policy_bytes(path):
    _inspect(path)
    info = _safe_info(path)
    _require(stat.S_ISREG(info.st_mode) and info.st_size <= _MAX_POLICY_BYTES,
             'invalid storage policy file')
    with path.open('rb') as stream:
        raw = stream.read(_MAX_POLICY_BYTES+1)
    _require(len(raw) <= _MAX_POLICY_BYTES, 'storage policy exceeds bound')
    return raw


def current_budget(path, *, code_root=None):
    """Return the active capability, or None only when no operation token exists.

    A captured runtime may pass its independently bound code root explicitly.
    Environment content never chooses that trusted root. No unrestricted write
    fallback is allowed when a token is present but invalid or out of scope.
    """
    token = os.environ.get(ENV)
    if token is None:
        return None
    _require(len(token) <= 8192, 'storage policy token exceeds bound')
    token = _decode(token)
    _require(set(token) == {'path', 'sha256'} and type(token['path']) is str and
             type(token['sha256']) is str and len(token['sha256']) == 64,
             'invalid storage policy token')
    policy_path = _absolute(token['path'])
    loaded_root = _absolute(_CODE_ROOT if code_root is None else code_root)
    raw = _policy_bytes(policy_path)
    _require(hashlib.sha256(raw).hexdigest() == token['sha256'], 'changed storage policy digest')
    doc = _decode(raw)
    _require(set(doc) == {'format', 'operation_id', 'code_root', 'policy_path',
                         'minimum_free_bytes', 'roots', 'max_files', 'max_path_bytes',
                         'implementation_sha256'} and doc['format'] == FORMAT and
             type(doc['code_root']) is str and doc['policy_path'] == str(policy_path) and
             doc['implementation_sha256'] == hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'changed storage policy identity/implementation')
    trusted_root = _absolute(doc['code_root'])
    _require(_under(policy_path, trusted_root) and _under(loaded_root, trusted_root),
             'storage policy outside captured code root')
    _require(type(doc['roots']) is list and 0 < len(doc['roots']) <= 32,
             'invalid storage policy roots')
    roots = {}
    for row in doc['roots']:
        _require(type(row) is dict and set(row) == {'path', 'logical_ceiling', 'volume'} and
                 type(row['path']) is str and type(row['volume']) is str,
                 'invalid storage policy root')
        root = _absolute(row['path'])
        _require(root not in roots and _volume(root) == row['volume'], 'changed storage policy roots/volume')
        roots[root] = row['logical_ceiling']
    _require(loaded_root == trusted_root or any(_under(loaded_root, root) for root in roots),
             'captured storage implementation outside operation roots')
    budget = StorageBudget(roots, operation_id=doc['operation_id'], policy_path=policy_path,
                           min_free_bytes=doc['minimum_free_bytes'], code_root=trusted_root,
                           max_files=doc['max_files'], max_path_bytes=doc['max_path_bytes'])
    _require(budget.raw == raw, 'noncanonical or changed storage policy')
    budget._index(path)
    return budget


def guarded_open(path, mode='xb'):
    """Use the operation capability when active; never silently bypass its roots."""
    budget = current_budget(path)
    return budget.stream(path, mode) if budget is not None else Path(path).open(mode)


class _ManagedOutput(io.RawIOBase):
    """A pathlib-compatible handle owning its bounded stream context."""
    def __init__(self, manager):
        self._manager = manager
        self._output = None
        self._failure = (None, None, None)
        self._output = manager.__enter__()

    def writable(self):
        return True

    def write(self, raw):
        try:
            return self._output.write(raw)
        except BaseException as error:
            self._failure = (type(error), error, error.__traceback__)
            raise

    def flush(self):
        if self._output is not None and not self._output.closed:
            self._output.flush()

    def fileno(self):
        return self._output.fileno()

    def close(self):
        if not self.closed:
            try:
                if self._output is not None:
                    self._manager.__exit__(*self._failure)
            finally:
                super().close()


class BoundedPath(type(Path())):
    """Path adapter for the closed inherited scalar programs' output arguments."""
    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        if not any(flag in mode for flag in 'wax') or current_budget(Path(self)) is None:
            return super().open(mode, buffering, encoding, errors, newline)
        _require(mode in ('w', 'x', 'a', 'wb', 'xb', 'ab'), 'unsupported scalar output mode')
        raw = _ManagedOutput(guarded_open(Path(self), mode if 'b' in mode else mode+'b'))
        if 'b' in mode:
            return raw
        return io.TextIOWrapper(raw, encoding=io.text_encoding(encoding), errors=errors, newline=newline)


def scalar_builtins():
    """Adapt only this runpy namespace's pathlib import, never the global module.

    All eight retained scalar entrypoints publish through an output Path
    argument. Their original bytes, serializers, imports and mathematics remain
    unchanged. This operational adapter is part of the captured current driver.
    """
    import builtins
    import types
    import pathlib
    original = builtins.__import__
    proxy = types.SimpleNamespace(**{**vars(pathlib), 'Path': BoundedPath})
    def importing(name, *args, **kwargs):
        return proxy if name == 'pathlib' else original(name, *args, **kwargs)
    return {**vars(builtins), '__import__': importing}
