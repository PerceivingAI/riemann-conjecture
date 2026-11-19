"""Independent Windows invocation supervision. Operational evidence is not proof.

The guardian owns only a new memory-only job. Numerical jobs retain CPU policy.
A READY/GO gate contains the real venv interpreter before application imports.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
ENV = 'RH_WHOLE_SOURCE_LIFECYCLE'
CPU_ENV = 'RH_WHOLE_SOURCE_UPSTREAM_CPUS'
POLICY = 'windows-lifecycle-v1'
CONTEXT = 'whole-source-lifecycle-context-v2'
LEASE = 'whole-source-lifecycle-lease-v2'
INTENT = 'whole-source-lifecycle-intent-v2'
RECEIPT = 'whole-source-lifecycle-receipt-v2'
DIAGNOSTICS = 'whole-source-lifecycle-diagnostics-v1'
_COMMANDS = ('run', 'controls', 'replay', 'assess', 'prepare-review',
             'finalize-retention', 'recover-assessment-publication')
_PHASES = ('prepare', 'source', 'audit', 'proposal', 'exact-inputs', 'exact', 'controls', 'replay')
_HEADLINES = {line.encode(): line for line in (
    'PAUSED_AFTER_VERIFIED_PHASE', 'COMPLETE_EVIDENCE_PENDING_INDEPENDENT_REVIEW',
    'PASS_REQUIRED_MATHEMATICAL_CONTROLS', 'PASS_COMPLETE_SCIENTIFIC_REPLAY_COMPARISON',
    'COMPLETE_IMPLEMENTATION_EVIDENCE_PENDING_INDEPENDENT_REVIEW',
    'PASS_NEW_SOURCE_CONDITIONAL_REFERENCE_QUALIFICATION', 'PASS_RETAINED_INVENTORY',
    'FAILED_NO_REFERENCE_ACCEPTANCE', *('Completed through: '+phase for phase in _PHASES),
    *('Next action: --resume --through '+phase for phase in _PHASES))}
_FAILURE_FRAME = b'whole-source-failure: '
_ERROR_TYPES = ('Exception', 'ValueError', 'ContractError', 'RuntimeError', 'OSError', 'TypeError',
                'MemoryError', 'AssertionError', 'KeyboardInterrupt', 'SystemExit', 'KeyError',
                'FileNotFoundError', 'FileExistsError', 'PermissionError', 'TimeoutExpired',
                'ArithmeticError', 'OverflowError', 'ZeroDivisionError', 'ImportError',
                'ModuleNotFoundError', 'BrokenPipeError')
_CAUSES = ('lifecycle READY deadline', 'lifecycle READY failed',
           'lifecycle READY implementation mismatch', 'lifecycle GO deadline',
           'lifecycle GO transport failed', 'lifecycle stdout/stderr cap exceeded',
           'required safety sampling cadence lost', 'lifecycle process allowance exhausted',
           'guardian memory envelope exhausted', 'changed control script',
           'lifecycle observation allowance exhausted', 'lifecycle volume headroom exhausted',
           'lifecycle observation root already owned', 'changed lifecycle operation/policy/code',
           'unfinished lifecycle intent/receipt authority', 'unresolved previous lifecycle cleanup',
           'cumulative active runtime exhausted', 'invalid lifecycle policy fields/version',
           'inconsistent lifecycle time allowances', 'invalid lifecycle memory override',
           'lifecycle memory override exceeds capacity', 'insufficient lifecycle memory capacity',
           'use the canonical operation sibling lifecycle directory',
           'observation root must be separate from scientific operation', 'oversized lifecycle request')
_MEMORY_SOURCES = ('windows.available_physical', 'windows.available_commit',
                   'windows.available_virtual', 'windows.job_process_memory_limit_only',
                   'windows.job_process_memory_remaining', 'windows.job_memory_limit_only',
                   'windows.job_memory_remaining', 'lifecycle.job_memory_remaining')
MIB = 1024*1024
MAX_ROW = 8192
MAX_META = 65536
_CANCELLED = threading.Event()
_CODE = ('scripts/whole_source/supervision.py', 'scripts/whole_source/lifecycle_windows.py',
         'scripts/whole_source/lifecycle_observations.py', 'scripts/whole_source/admission.py',
         'scripts/whole_source/resources.py', 'scripts/whole_source/execution.py',
         'scripts/whole_source/retention.py', 'scripts/whole_source/storage.py',
         'scripts/weil_whole_source_split.py')
_ERROR_LOCATIONS = (*_CODE, *('scripts/whole_source/'+name+'.py' for name in (
    'analytic', 'artifacts', 'contract', 'controls', 'coordinator', 'exact', 'exact_global',
    'exact_tasks', 'gram', 'pipeline', 'producer', 'proposal', 'proposal_float', 'receipts',
    'recovery', 'reuse', 'selection', 'slice', 'task_groups')))


def _failure(exc):
    """Only closed cause codes and logical repository locations cross into evidence."""
    kind = type(exc).__name__
    location = line = None
    tb = exc.__traceback__
    while tb is not None:
        try:
            logical = Path(tb.tb_frame.f_code.co_filename).relative_to(ROOT).as_posix()
        except ValueError:
            logical = None
        if logical in _ERROR_LOCATIONS:
            location, line = logical, tb.tb_lineno
        tb = tb.tb_next
    cause = exc.args[0] if exc.args and type(exc.args[0]) is str else None
    result = {'type': kind if kind in _ERROR_TYPES else 'Exception',
              'location': location, 'line': line, 'cause': cause if cause in _CAUSES else None}
    for name in ('errno', 'winerror'):
        code = getattr(exc, name, None)
        result[name] = code if type(code) is int and -(1 << 31) <= code < 1 << 32 else None
    return result


def _failure_record(value):
    return (type(value) is dict and set(value) == {'type', 'location', 'line', 'cause', 'errno', 'winerror'} and
            value['type'] in _ERROR_TYPES and value['cause'] in (None, *_CAUSES) and
            value['location'] in (None, *_ERROR_LOCATIONS) and
            (value['line'] is None if value['location'] is None else
             type(value['line']) is int and 0 < value['line'] < 1 << 24) and
            all(value[key] is None or type(value[key]) is int and
                -(1 << 31) <= value[key] < 1 << 32 for key in ('errno', 'winerror')))


def report_failure(exc):
    sys.stderr.buffer.write(b'\n'+_FAILURE_FRAME+_wire(_failure(exc)))
    sys.stderr.buffer.flush()


def _observed_upstream(upstream, *, cpus, available, reserve):
    quota = upstream.get('quota_cpu_limit')
    return {
        'platform': 'win32', 'logical_cpus': upstream['logical_cpus'],
        'affinity_cpus': upstream['affinity_cpus'], 'effective_cpu_budget': cpus,
        'quota_cpu_limit': quota if type(quota) is str and re.fullmatch(r'\d{1,12}(/\d{1,8})?', quota) else None,
        'available_memory_bytes': available, 'reserve_bytes': reserve,
        'cpu_detection_complete': upstream['cpu_detection_complete'],
        'memory_detection_complete': upstream['memory_detection_complete'],
        'memory_sources': [
            {'source': row['source'] if row['source'] in _MEMORY_SOURCES else 'other-measured-limit',
             **{name: row[name] for name in ('available_bytes', 'limit_bytes', 'usage_bytes')
                if name in row}} for row in upstream['memory_sources']],
        'cpu_diagnostic_count': len(upstream.get('cpu_diagnostics', ())),
        'memory_diagnostic_count': len(upstream.get('memory_diagnostics', ())),
    }


def _observed_job(job):
    sample = job.sample()
    for row in (sample, *sample['root_processes']):
        row['diagnostic_count'] = len(row.pop('diagnostics'))
    return sample


def constrain_detection(detected):
    """Include the known ancestor job even when a venv job hides it."""
    if ENV not in os.environ:
        return detected
    value = require_current()
    from scripts.whole_source.lifecycle_windows import inspect_membership
    sample = inspect_membership(value['job_name'], helper_root=ROOT)
    _require(detected.get('cpu_detection_complete') is True and
             detected.get('memory_detection_complete') is True, 'required live discovery unavailable')
    remaining = max(0, sample['memory_limit_bytes']-sample['current_committed_bytes'])
    sources = [row for row in detected.get('memory_sources', [])
               if row['source'] != 'lifecycle.job_memory_remaining']
    sources.append({'source': 'lifecycle.job_memory_remaining', 'available_bytes': remaining,
                    'limit_bytes': sample['memory_limit_bytes'], 'scope': 'ancestor-job'})
    return {**detected, 'memory_sources': sources,
            'available_memory_bytes': min(detected['available_memory_bytes'], remaining)}


def cancel_current():
    """Stop admitting new work; the guardian separately bounds cleanup time."""
    _CANCELLED.set()


def _require(value, message):
    if not value:
        raise ValueError(message)


def _wire(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                       allow_nan=False)+'\n').encode()


def _load(raw, cap=MAX_META):
    _require(type(raw) is bytes and len(raw) <= cap, 'lifecycle metadata exceeds cap')
    def pairs(rows):
        result = {}
        for key, value in rows:
            _require(key not in result, 'duplicate lifecycle field')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite metadata')))


def _utc():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def policy(value):
    """Closed owner policy. Wall allowances are permissions, not runtime estimates."""
    keys = {'format', 'wall_seconds', 'active_seconds', 'grace_seconds', 'memory_mib',
            'sample_milliseconds', 'stale_milliseconds', 'observation_bytes'}
    _require(type(value) is dict and set(value) == keys and value['format'] == POLICY,
             'invalid lifecycle policy fields/version')
    limits = {'wall_seconds': (1, 31536000), 'active_seconds': (1, 31536000),
              'grace_seconds': (1, 120), 'sample_milliseconds': (100, 60000),
              'stale_milliseconds': (200, 600000), 'observation_bytes': (MIB, 16*MIB)}
    for name, (lo, hi) in limits.items():
        _require(type(value[name]) is int and lo <= value[name] <= hi, 'invalid lifecycle '+name)
    _require(value['wall_seconds'] <= value['active_seconds'] and
             value['stale_milliseconds'] >= 2*value['sample_milliseconds'],
             'inconsistent lifecycle time allowances')
    _require(value['memory_mib'] is None or
             (type(value['memory_mib']) is int and 128 <= value['memory_mib'] <= 1 << 30),
             'invalid lifecycle memory override')
    return dict(value)


def _safe(path, *, output=False):
    path = Path(path).absolute()
    _require(len(str(path).encode()) <= 32768 and len(path.parts) <= 128,
             'oversized lifecycle path')
    for item in (path, *path.parents):
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        _require(not item.is_symlink() and not (getattr(info, 'st_file_attributes', 0) & 0x400),
                 'lifecycle reparse path refused')
        if output:
            _require(not (item/'retained-manifest.json').exists() if item.is_dir() else True,
                     'lifecycle output is within a sealed tree')
    return path.resolve()


def _read(path, cap):
    import stat
    info = path.lstat()
    _require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
             not (getattr(info, 'st_file_attributes', 0) & 0x400) and info.st_size <= cap,
             'unsafe or oversized lifecycle input')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        _require((opened.st_dev, opened.st_ino) == (info.st_dev, info.st_ino),
                 'lifecycle input changed during open')
        raw = stream.read(cap+1)
        final = os.fstat(stream.fileno())
    _require(len(raw) <= cap and len(raw) == info.st_size == final.st_size and
             final.st_mtime_ns == info.st_mtime_ns, 'lifecycle input changed during read')
    return raw


def _ref(root, path):
    raw = _read(path, 16*MIB)
    return {'path': path.relative_to(root).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest(),
            'size': len(raw)}


def _code(root):
    return {name: hashlib.sha256(_read(root/name, 4*MIB)).hexdigest() for name in _CODE}


class _Store:
    """One locked observation root, bounded writes and constant live census cost."""
    def __init__(self, root, maximum):
        self.root, self.maximum = root, maximum
        self.root_identity = (root.stat().st_dev, root.stat().st_ino)
        self.lock = threading.RLock()
        self.used = 0
        self.reserved = 0
        count = 0
        for directory, dirs, files in os.walk(root, followlinks=False):
            for name in (*dirs, *files):
                path = Path(directory)/name
                count += 1
                _require(count <= 16384, 'too many lifecycle observation members')
                _safe(path)
                if path.is_file():
                    self.used += path.stat().st_size
        _require(self.used <= maximum, 'lifecycle observation allowance exhausted')

    def _check(self, growth, *, emergency=False):
        _safe(self.root, output=True)
        _require((self.root.stat().st_dev, self.root.stat().st_ino) == self.root_identity,
                 'lifecycle observation root replaced')
        _require(self.used+self.reserved+growth <= self.maximum, 'lifecycle observation allowance exhausted')
        need = max(65536, growth) if emergency else self.reserved+growth+64*MIB
        _require(shutil.disk_usage(self.root).free >= need,
                 'lifecycle volume headroom exhausted')

    def write(self, name, raw, *, replace=False, emergency=False):
        with self.lock:
            path = self.root/name
            _require(path.is_relative_to(self.root), 'invalid lifecycle output path')
            _safe(path, output=True)
            self._check(len(raw), emergency=emergency)
            path.parent.mkdir(parents=True, exist_ok=True)
            if replace:
                old = path.stat().st_size if path.exists() else 0
                temporary = path.with_name('.'+path.name+'.tmp')
                with temporary.open('xb') as stream:
                    stream.write(raw)
                os.replace(temporary, path)
                self.used += len(raw)-old
            else:
                with path.open('xb') as stream:
                    stream.write(raw)
                self.used += len(raw)
            return path

    def append(self, name, raw, *, emergency=False):
        with self.lock:
            self._check(len(raw), emergency=emergency)
            path = self.root/name
            _safe(path, output=True)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('ab') as stream:
                stream.write(raw)
            self.used += len(raw)


@contextlib.contextmanager
def _lease(root):
    root.mkdir(parents=True, exist_ok=True)
    with (root/'.lock').open('a+b') as stream:
        import msvcrt
        stream.seek(0)
        if stream.read(1) == b'':
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        try:
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise ValueError('lifecycle observation root already owned') from exc
        try:
            yield
        finally:
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)


class _Capture:
    def __init__(self, stream, *, ready=False, cap):
        self.stream, self.cap = stream, cap
        self.ready = queue.Queue(maxsize=1) if ready else None
        self.error = None
        self.size = 0
        self.headlines = []
        self.failure = None
        self.thread = threading.Thread(target=self._read, daemon=True)
        self.thread.start()

    def _record(self, raw):
        if self.ready is not None:
            headline = _HEADLINES.get(raw)
            if headline is not None and headline not in self.headlines:
                self.headlines.append(headline)
        elif raw.startswith(_FAILURE_FRAME):
            try:
                value = _load(raw[len(_FAILURE_FRAME):], 1024)
            except (ValueError, RecursionError):
                return
            if _failure_record(value):
                self.failure = value

    def _read(self):
        prefix = bytearray()
        waiting = self.ready is not None
        pending = bytearray()
        overlong = False
        try:
            while True:
                raw = os.read(self.stream.fileno(), 4096)
                if not raw:
                    break
                if waiting:
                    prefix.extend(raw)
                    _require(len(prefix) <= MAX_META, 'oversized lifecycle READY')
                    if b'\n' not in prefix:
                        continue
                    line, raw = bytes(prefix).split(b'\n', 1)
                    self.ready.put_nowait(_load(line))
                    waiting = False
                self.size += len(raw)
                if self.size > self.cap:
                    self.error = ValueError('lifecycle stdout/stderr cap exceeded')
                elif raw and self.error is None:
                    # Keep only closed diagnostic records, even when a line
                    # or an identifying token spans several pipe reads.
                    fragments = raw.split(b'\n')
                    for index, fragment in enumerate(fragments):
                        if len(pending)+len(fragment) > 1024:
                            overlong = True
                            pending.clear()
                        elif not overlong:
                            pending.extend(fragment)
                        if index < len(fragments)-1:
                            if not overlong:
                                self._record(bytes(pending).removesuffix(b'\r'))
                            pending.clear()
                            overlong = False
        except BaseException as exc:
            self.error = exc
        finally:
            self.stream.close()


def _send_go(process, lease, request, deadline):
    """Bound a pipe write even if the held interpreter stops reading after READY."""
    errors = []
    def send():
        try:
            for frame in (lease, request):
                remaining = memoryview(frame)
                while remaining:
                    written = process.stdin.write(remaining)
                    if not written:
                        raise OSError('lifecycle GO transport failed')
                    remaining = remaining[written:]
        except (OSError, ValueError) as exc:
            errors.append(exc)
    writer = threading.Thread(target=send, daemon=True)
    writer.start()
    # A timeout terminates the owned job before stdin is closed, releasing the writer.
    writer.join(max(0, deadline-time.monotonic_ns())/1000000000)
    _require(not writer.is_alive(), 'lifecycle GO deadline')
    if errors:
        raise OSError('lifecycle GO transport failed') from errors[0]


def _context():
    raw = os.environ.get(ENV)
    _require(raw is not None and len(raw) <= MAX_META, 'independent lifecycle supervision required')
    value = _load(raw.encode())
    _require(type(value) is dict and value.get('format') in (POLICY, LEASE), 'invalid lifecycle context')
    for key, width in (('invocation_id', 32), ('operation_id', 64)):
        identity = value.get(key)
        _require(type(identity) is str and len(identity) == width and
                 re.fullmatch('[0-9a-f]+', identity), 'invalid lifecycle identity')
    return value


def _operation_locations(root, operation, code_root):
    _require(root.is_relative_to(code_root) and operation != code_root,
             'lifecycle operation outside captured code root')
    _require(not root.is_relative_to(operation) and not operation.is_relative_to(root),
             'observation root must be separate from scientific operation')
    _require(root == operation.with_name(operation.name+'.lifecycle'),
             'use the canonical operation sibling lifecycle directory')


def runtime_operation_roots(value):
    """Return the explicitly leased locations, or None for a frozen legacy lease."""
    if value.get('format') != LEASE:
        return None
    from scripts.whole_source.storage import owner_binding
    paths = []
    for key in ('root', 'operation_root_runtime', 'code_root_runtime'):
        raw = value.get(key)
        _require(type(raw) is str and Path(raw).is_absolute(), 'invalid private lifecycle location')
        checked = _safe(raw)
        _require(str(checked) == raw, 'noncanonical private lifecycle location')
        paths.append(checked)
    root, operation, code_root = paths
    _operation_locations(root, operation, code_root)
    observed = _load(_read(root/'context.json', MAX_META))
    _require(type(observed) is dict and observed.get('format') == CONTEXT and
             observed.get('operation_id') == value['operation_id'] and observed.get('code') == value['code'] and
             observed.get('owner_sha256') == owner_binding(root, code_root),
             'changed lifecycle operation or private ownership')
    return operation, code_root


def require_current():
    """Refuse outside the actual guardian-owned outer job, including replay."""
    value = _context()
    _require(not _CANCELLED.is_set(), 'lifecycle cancellation requested')
    from scripts.whole_source.lifecycle_windows import inspect_membership, process_identity
    _require(process_identity(value['guardian_pid'], helper_root=ROOT) ==
             value['guardian_creation_time_100ns'], 'lifecycle guardian unavailable or replaced')
    membership = inspect_membership(value['job_name'], helper_root=ROOT)
    _require(membership['belongs'], 'caller is outside lifecycle containment')
    _require(membership['memory_limit_bytes'] == value['memory_limit_bytes'],
             'changed lifecycle memory containment')
    _require(_code(ROOT) == value['code'], 'lifecycle parent/child implementation differs')
    if runtime_operation_roots(value) is None:
        root = _safe(value['root'])
        legacy = _load(_read(root/'context.json', MAX_META))
        _require(type(legacy) is dict and legacy.get('format') == INTENT and
                 legacy.get('operation_id') == value['operation_id'] and legacy.get('code') == value['code'],
                 'changed legacy lifecycle ownership')
    return value


def current_binding():
    value = require_current()
    binding = {'role': 'lifecycle', **{key: value[key]
               for key in ('invocation_id', 'operation_id', 'intent')}}
    validate_binding(binding)
    return binding


def upstream_cpu_limit():
    raw = os.environ.get(CPU_ENV)
    if raw is None:
        return None
    value = _context()
    _require(raw == str(value['upstream_cpus']), 'changed upstream lifecycle CPU authority')
    return value['upstream_cpus']


def _progress_fields(phase, state, work):
    phase = phase if phase in (*_PHASES, 'bootstrap', 'retention', 'owned-stage') else 'opaque'
    state = state if state in ('working', 'complete', 'failed') else 'opaque'
    if type(work) is dict and phase == 'owned-stage':
        attempt = work.get('attempt_id')
        work = ({'attempt_id': attempt} if type(attempt) is str and
                re.fullmatch('[0-9a-f]{32}', attempt) else None)
    elif work not in (None, 'admission-census', 'phase-work', 'scalar-decoding',
                      'sealed-inventory-verification'):
        work = None
    return {'phase': phase, 'state': state, 'work': work}


def event(phase, state='working', work=None):
    value = require_current()
    document = {'invocation_id': value['invocation_id'], **_progress_fields(phase, state, work),
                'pid': os.getpid(), 'monotonic_ns': time.monotonic_ns()}
    raw = _wire(document)
    _require(len(raw) <= MAX_ROW, 'oversized lifecycle progress')
    path = Path(value['root'])/'progress'/(value['invocation_id']+'.json')
    path.parent.mkdir(exist_ok=True)
    temporary = path.with_name('.'+path.name+'.'+str(os.getpid())+'.tmp')
    try:
        with temporary.open('xb') as stream:
            stream.write(raw)
        os.replace(temporary, path)
    except OSError:
        temporary.unlink(missing_ok=True)
        # Independent job/volume observation remains authoritative when optional
        # application progress is unavailable. Never invent completion/ETA.


def _progress(root, identifier, stale_ms):
    path = root/'progress'/(identifier+'.json')
    try:
        with path.open('rb') as stream:
            row = _load(stream.read(MAX_ROW+1), MAX_ROW)
        _require(row['invocation_id'] == identifier, 'changed lifecycle progress identity')
        pid, stamp = row['pid'], row['monotonic_ns']
        _require(type(pid) is int and pid > 0 and type(stamp) is int and stamp >= 0,
                 'invalid lifecycle progress counters')
        progress = {'invocation_id': identifier, 'pid': pid, 'monotonic_ns': stamp,
                    **_progress_fields(row['phase'], row['state'], row['work'])}
        return progress, time.monotonic_ns()-stamp > stale_ms*1000000
    except FileNotFoundError:
        return None, True


def _active(root, context):
    path = root/'context.json'
    if path.exists():
        _require(_load(_read(path, MAX_META)) == context, 'changed lifecycle operation/policy/code')
    else:
        _require(not any((root/'intents').glob('*.json')), 'missing original lifecycle context')
    total = 0
    intents = sorted((root/'intents').glob('*.json'))
    _require(len(intents) < 1024, 'lifecycle invocation allowance exhausted')
    _require({path.stem for path in (root/'receipts').glob('*.json')} ==
             {path.stem for path in intents}, 'unfinished lifecycle intent/receipt authority')
    for intent in intents:
        receipt = root/'receipts'/intent.name
        _require(receipt.is_file(), 'unfinished lifecycle invocation needs explicit investigation')
        from scripts.whole_source.lifecycle_observations import read_authority
        value = read_authority(root, intent.stem)
        _require(value['invocation_id'] == intent.stem and value['operation_id'] == context['operation_id'] and
                 type(value['elapsed_ns']) is int and value['elapsed_ns'] >= 0,
                 'invalid lifecycle runtime authority')
        _require(value['cleanup_verified'], 'unresolved previous lifecycle cleanup')
        total += value['elapsed_ns']
    return total


def validate_binding(binding, *, legacy=False):
    """Validate the retained guardian reference without resolving a location."""
    from scripts.whole_source.contract import ArtifactRef
    location = 'root' if legacy else 'role'
    _require(type(binding) is dict and set(binding) ==
             {location, 'invocation_id', 'operation_id', 'intent'}, 'invalid phase lifecycle binding')
    _require(type(binding[location]) is str and (legacy or binding[location] == 'lifecycle'),
             'invalid phase lifecycle role')
    invocation_id, operation_id = binding['invocation_id'], binding['operation_id']
    _require(type(invocation_id) is str and re.fullmatch('[0-9a-f]{32}', invocation_id) and
             type(operation_id) is str and re.fullmatch('[0-9a-f]{64}', operation_id),
             'invalid phase lifecycle identity')
    intent = binding['intent']
    _require(type(intent) is dict and set(intent) == {'path', 'sha256', 'size'},
             'invalid phase lifecycle intent')
    ref = ArtifactRef(**intent)
    _require(ref.path == 'intents/'+invocation_id+'.json' and 0 < ref.size <= MAX_META,
             'invalid phase lifecycle intent reference')


def _verified_binding(binding, current):
    legacy = type(binding) is dict and 'root' in binding
    validate_binding(binding, legacy=legacy)
    _require(binding['operation_id'] == current['operation_id'] and
             binding['invocation_id'] != current['invocation_id'], 'prior lifecycle identity differs')
    observed = Path(current['root'])
    _require(observed.is_absolute() and str(_safe(observed)) == current['root'] and
             (not legacy or binding['root'] == current['root']),
             'prior lifecycle observation root differs')
    from scripts.whole_source.lifecycle_observations import read_bound_receipt
    receipt, reference = read_bound_receipt(observed, binding['invocation_id'],
                                            verify_diagnostics=False)
    _require(receipt.get('intent') == binding['intent'] and
             receipt['operation_id'] == current['operation_id'] and
             receipt['code'] == current['code'] and receipt['cleanup_verified'] and
             receipt['status'] in ('COMPLETED', 'INTERRUPTED'),
             'prior lifecycle authority or cleanup is unverified')
    return receipt, reference


def verify_binding(binding):
    """Require immutable terminal authority before adopting earlier work."""
    return _verified_binding(binding, require_current())[0]


def read_phase_authority(binding, *, current):
    """Verify selected guardian authority and its receipt reference, not diagnostic bytes."""
    return _verified_binding(binding, current)


def supervise(argv, *, observation_root, operation_root, policy_document, code_root=ROOT,
              script=None, cancel_event=None):
    """Run one CLI invocation or an explicit software-control script in a new job."""
    started = time.monotonic_ns()
    _require(sys.platform == 'win32', 'qualified lifecycle supervision requires Windows')
    _require(ENV not in os.environ, 'nested independent lifecycle guardian refused')
    settings = policy(policy_document)
    root, operation, code_root = _safe(observation_root, output=True), _safe(operation_root), _safe(code_root)
    _operation_locations(root, operation, code_root)
    from scripts.whole_source.execution import neutral_helpers, exact_telemetry
    from scripts.whole_source import admission, resources, storage
    from scripts.whole_source.lifecycle_windows import WindowsLifecycle
    helpers, limits, _, _ = neutral_helpers(code_root)
    upstream = exact_telemetry(helpers.detect_resources())
    cpus = resources._cpu_limit(upstream)
    guardian_initial = admission.current_commit(code_root)
    guardian_growth = 128*MIB
    admission.admit_caller({'required_bytes': guardian_initial+guardian_growth}, upstream,
                           existing_bytes=guardian_initial)
    sources = [item['available_bytes'] for item in upstream['memory_sources']]
    available = min(sources)
    reserve = max(128*MIB, (available+9)//10)
    # Windows rounds job memory to pages. Install an exact lower MiB ceiling.
    memory = ((available-reserve-guardian_growth)//MIB)*MIB
    if settings['memory_mib'] is not None:
        _require(settings['memory_mib']*MIB <= memory, 'lifecycle memory override exceeds capacity')
        memory = settings['memory_mib']*MIB
    _require(memory >= 128*MIB, 'insufficient lifecycle memory capacity')
    identity = _code(code_root)
    upstream = _observed_upstream(upstream, cpus=cpus, available=available, reserve=reserve)
    with _lease(root):
        store = _Store(root, settings['observation_bytes'])
        context_path = root/'context.json'
        if context_path.exists():
            original = _load(_read(context_path, MAX_META))
            _require(type(original) is dict and original.get('format') == CONTEXT,
                     'historical lifecycle context is read-only')
            operation_id = original.get('operation_id')
            _require(type(operation_id) is str and re.fullmatch('[0-9a-f]{64}', operation_id),
                     'invalid lifecycle operation identity')
        else:
            operation_id = os.urandom(32).hex()
        context = {'format': CONTEXT, 'operation_id': operation_id, 'code': identity,
                   'policy': settings, 'owner_sha256': storage.owner_binding(root, code_root)}
        previous = _active(root, context)
        remaining = settings['active_seconds']*1000000000-previous
        _require(remaining > 0, 'cumulative active runtime exhausted')
        wall_ns = min(settings['wall_seconds']*1000000000, remaining)
        sample_ns = settings['sample_milliseconds']*1000000
        stream_cap = min(4*MIB, settings['observation_bytes']//4)
        # Raw pipes are bounded separately from the retained sample and metadata allowance.
        rows = (wall_ns+sample_ns-1)//sample_ns+8
        predicted = rows*MAX_ROW+4*MAX_META
        store._check(predicted)
        if not context_path.exists():
            store.write('context.json', _wire(context))
        identifier = uuid.uuid4().hex
        store.reserved = 64*1024
        request = {'argv': list(argv), 'script': None, 'invocation_id': identifier}
        invocation = {'command': (request['argv'][0] if request['argv'] and
                                  request['argv'][0] in _COMMANDS else 'other')}
        if script is not None:
            target = _safe(script)
            target.relative_to(code_root)
            raw = _read(target, MAX_META)
            request['script'] = {'path': str(target), 'sha256': hashlib.sha256(raw).hexdigest()}
            invocation = {'command': 'software-control', 'script_sha256': request['script']['sha256']}
        request_raw = _wire(request)
        _require(len(request_raw) <= MAX_META, 'oversized lifecycle request')
        log_name = 'observations/'+identifier+'.jsonl'
        job, process, stdout, stderr = None, None, None, None
        reason, final, error = None, None, None
        cleanup, child_code = False, None
        job_name = 'Local\\rh-lifecycle-'+identifier
        samples = 0
        initial_job = None
        intent_doc = {'format': INTENT, 'invocation_id': identifier,
                      'operation_id': operation_id, 'started_utc': _utc(), 'policy': settings,
                      'code': identity, 'upstream': upstream, 'job_name': job_name,
                      'memory_limit_bytes': memory, 'guardian_future_bytes': guardian_growth,
                      'memory_basis': 'LIVE_AVAILABLE_CEILING_NOT_PHASE_DEMAND',
                      'stream_limit_bytes': stream_cap, 'invocation': invocation}
        intent_path = store.write('intents/'+identifier+'.json', _wire(intent_doc))
        intent = _ref(root, intent_path)
        store.write(log_name, b'')
        try:
            job = WindowsLifecycle(memory, helper_root=code_root, name=job_name)
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1', PYTHONPATH=str(code_root))
            process = job.launch([sys.executable, '-B', '-m', 'scripts.whole_source.supervision',
                                  '--child', identifier], cwd=code_root, env=env,
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
            stdout = _Capture(process.stdout, ready=True, cap=stream_cap)
            stderr = _Capture(process.stderr, cap=stream_cap)
            ready = None
            while ready is None:
                _require(time.monotonic_ns()-started < min(wall_ns, 30000000000), 'lifecycle READY deadline')
                _require(process.poll() is None and stdout.error is None, 'lifecycle READY failed')
                try:
                    ready = stdout.ready.get(timeout=0.05)
                except queue.Empty:
                    pass
            _require(type(ready) is dict and ready.get('format') == POLICY and
                     ready.get('invocation_id') == identifier and
                     ready.get('source_sha256') == identity['scripts/whole_source/supervision.py'],
                     'lifecycle READY implementation mismatch')
            job.attach_ready_pid(ready['pid'])
            lease = {'format': LEASE, 'root': str(root), 'invocation_id': identifier,
                     'operation_root_runtime': str(operation), 'code_root_runtime': str(code_root),
                     'operation_id': operation_id, 'intent': intent, 'job_name': job.name,
                     'guardian_pid': os.getpid(), 'upstream_cpus': cpus, 'code': identity,
                     'guardian_creation_time_100ns': job._times(job._kernel.GetCurrentProcess())['creation_time_100ns'],
                     'memory_limit_bytes': memory, 'observation_bytes': settings['observation_bytes'],
                     'request_bytes': len(request_raw)}
            lease_raw = _wire(lease)
            _require(len(lease_raw) <= 4080, 'lifecycle GO frame exceeds bounded pipe allowance')
            initial_job = _observed_job(job)
            _send_go(process, lease_raw, request_raw, started+min(wall_ns, 30000000000))
            last_sample, cancelling = 0, None
            while True:
                now = time.monotonic_ns()
                if cancelling is None:
                    try:
                        if cancel_event is not None and cancel_event.is_set():
                            reason = 'explicit_cancel'
                        elif now-started >= wall_ns:
                            reason = 'wall_or_cumulative_deadline'
                        elif stdout.error is not None or stderr.error is not None:
                            raise stdout.error or stderr.error
                        if now-last_sample >= sample_ns:
                            if last_sample and now-last_sample > settings['stale_milliseconds']*1000000:
                                raise OSError('required safety sampling cadence lost')
                            final = _observed_job(job)
                            _require(final['active_process_count'] <= 256, 'lifecycle process allowance exhausted')
                            progress, stale = _progress(root, identifier, settings['stale_milliseconds'])
                            own = limits.windows_resource_snapshot()['process']['committed_bytes']
                            _require(own <= guardian_initial+guardian_growth, 'guardian memory envelope exhausted')
                            row = {'event': 'sample', 'invocation_id': identifier, 'monotonic_ns': now,
                                   'phase': None if progress is None else progress['phase'],
                                   'progress': 'opaque' if progress is None or stale else progress,
                                   'heartbeat_stale': stale, 'job': final, 'caller': None,
                                   'guardian_committed_bytes': own,
                                   'volumes': [{'role': 'observation', 'free_bytes': shutil.disk_usage(root).free}]}
                            raw = _wire(row)
                            _require(len(raw) <= MAX_ROW, 'lifecycle sample exceeds bounded codec')
                            store.append(log_name, raw)
                            store.write('status.json', raw, replace=True)
                            last_sample, samples = now, samples+1
                    except KeyboardInterrupt:
                        reason = 'explicit_cancel'
                    except BaseException as exc:
                        reason, error = 'required_safety_observation_failed', _failure(exc)
                    if reason is not None:
                        cancelling = now
                        try:
                            process.stdin.write(b'!\n')
                            process.stdin.flush()
                        except (OSError, ValueError):
                            pass
                if cancelling is not None and now-cancelling >= settings['grace_seconds']*1000000000:
                    job.terminate()
                    reason = reason or 'cleanup_escalation'
                    break
                if process.poll() is not None:
                    final = _observed_job(job)
                    if final['active_process_count'] == 0:
                        break
                    if cancelling is None:
                        reason, cancelling = 'remaining_descendants_after_caller_exit', now
                time.sleep(min(settings['sample_milliseconds']/1000, 0.05))
        except BaseException as exc:
            reason = reason or ('explicit_cancel' if isinstance(exc, KeyboardInterrupt) else 'launch_or_attachment_failed')
            error = _failure(exc)
            if job is not None:
                job.terminate()
            elif process is not None and process.poll() is None:
                process.kill()
        finally:
            if job is not None:
                until = time.monotonic()+5
                while time.monotonic() < until:
                    try:
                        final = _observed_job(job)
                        if final['active_process_count'] == 0 and final['active_process_ids'] == []:
                            cleanup = True
                            break
                    except OSError as exc:
                        error = _failure(exc)
                        break
                    time.sleep(0.02)
                if not cleanup:
                    job.terminate()
                job.close()
            if process is not None:
                try:
                    child_code = process.wait(timeout=5)
                except subprocess.TimeoutExpired as exc:
                    error = _failure(exc)
                    cleanup = False
                if process.stdin is not None:
                    process.stdin.close()
            for capture in (stdout, stderr):
                if capture is not None:
                    capture.thread.join(1)
                    if capture.thread.is_alive() or capture.error is not None:
                        if error is None and capture.error is not None:
                            error = _failure(capture.error)
                        reason = reason or 'required_safety_observation_failed'
        elapsed = time.monotonic_ns()-started
        if reason is None and (child_code != 0 or not cleanup):
            reason = 'application_exit_or_unverified_cleanup'
        status = 'COMPLETED' if reason is None and child_code == 0 and cleanup else (
            'INTERRUPTED' if process is not None else 'REFUSED')
        store.reserved = 32*1024
        terminal = {'event': 'terminal', 'invocation_id': identifier,
                    'monotonic_ns': time.monotonic_ns(), 'phase': None, 'progress': 'opaque',
                    'job': final, 'caller': None, 'volumes': None,
                    'status': status, 'reason': reason, 'elapsed_ns': elapsed}
        diagnostics = {'format': DIAGNOSTICS, 'invocation_id': identifier,
                       'stdout_bytes': 0 if stdout is None else stdout.size,
                       'stderr_bytes': 0 if stderr is None else stderr.size,
                       'headlines': [] if stdout is None else stdout.headlines,
                       'failure': None if stderr is None else stderr.failure}
        diagnostics_path = store.write('diagnostics/'+identifier+'.json', _wire(diagnostics), emergency=True)
        store.append(log_name, _wire(terminal), emergency=True)
        receipt = {'format': RECEIPT, 'invocation_id': identifier,
                   'operation_id': operation_id, 'status': status, 'reason': reason,
                   'error': error, 'elapsed_ns': elapsed, 'cumulative_active_ns': previous+elapsed,
                   'child_returncode': child_code, 'policy': settings, 'upstream': upstream,
                   'code': identity, 'intent': intent, 'final_job': final, 'cleanup_verified': cleanup,
                   'initial_job': initial_job,
                   'stream_limit_bytes': stream_cap,
                   'observation': _ref(root, root/log_name), 'sample_count': samples,
                   'diagnostics': _ref(root, diagnostics_path),
                   'guardian_excluded_from_job': True, 'review_wait_included': False,
                   'scientific_acceptance': False}
        store.write('status.json', _wire(terminal), replace=True, emergency=True)
        store.write('receipts/'+identifier+'.json', _wire(receipt), emergency=True)
        return receipt


def _child(identifier):
    _require(re.fullmatch('[0-9a-f]{32}', identifier), 'invalid lifecycle child identity')
    print(json.dumps({'format': POLICY, 'pid': os.getpid(), 'invocation_id': identifier,
                      'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}), flush=True)
    # Raw pipe reads avoid a daemon holding BufferedReader's shutdown lock.
    line = bytearray()
    while not line.endswith(b'\n'):
        piece = os.read(sys.stdin.fileno(), 1)
        _require(piece and len(line) < MAX_META, 'incomplete or oversized lifecycle GO')
        line.extend(piece)
    line = bytes(line)
    lease = _load(line)
    os.environ[ENV] = _wire(lease).decode()
    os.environ[CPU_ENV] = str(lease['upstream_cpus'])
    _require(lease['invocation_id'] == identifier, 'changed lifecycle GO identity')
    require_current()
    remaining = lease['request_bytes']
    _require(type(remaining) is int and 0 < remaining <= MAX_META, 'oversized lifecycle request')
    request_raw = bytearray()
    while remaining:
        piece = os.read(sys.stdin.fileno(), remaining)
        _require(piece, 'incomplete lifecycle request')
        request_raw.extend(piece)
        remaining -= len(piece)
    request = _load(bytes(request_raw))
    _require(request['invocation_id'] == identifier, 'changed lifecycle request identity')
    def watch():
        import _thread
        while True:
            data = os.read(sys.stdin.fileno(), 1)
            if not data or data.startswith(b'!'):
                _CANCELLED.set()
                _thread.interrupt_main()
                return
    threading.Thread(target=watch, daemon=True).start()
    event('bootstrap')
    if request['script'] is not None:
        import runpy
        source = request['script']
        path = Path(source['path'])
        _require(hashlib.sha256(_read(path, MAX_META)).hexdigest() == source['sha256'], 'changed control script')
        runpy.run_path(str(path), run_name='__main__')
        return 0
    from scripts.weil_whole_source_split import main
    return main(request['argv'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--child', required=True)
    args = parser.parse_args()
    return _child(args.child)


if __name__ == '__main__':
    sys.modules['scripts.whole_source.supervision'] = sys.modules[__name__]
    try:
        raise SystemExit(main())
    except BaseException as exc:
        if not isinstance(exc, SystemExit):
            report_failure(exc)
        raise
