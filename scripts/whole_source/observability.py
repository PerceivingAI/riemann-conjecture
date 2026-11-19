"""Whole-source live recording; the retained shared observer stays byte-identical."""
from __future__ import annotations

import json
import os
import sys
import uuid

from scripts import run_observability as shared
from scripts.whole_source.storage import guarded_open


def _json_bytes(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode('utf-8')


def _atomic_write_json(path, value, *, retry_permission_errors=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f'.{path.name}.{uuid.uuid4().hex}.tmp')
    try:
        with guarded_open(temporary) as stream:
            stream.write(_json_bytes(value))
        if retry_permission_errors:
            shared.replace_path_with_permission_retry(temporary, path)
        else:
            temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def write_run_identity(lock, *, driver_version, dimensions, git_commit, git_dirty):
    """Write the same lock-bound identity under the active storage allowance."""
    if not lock.is_held:
        raise ValueError('output-directory lock must still be held')
    if not driver_version or not git_commit or not dimensions or not all(type(n) is int for n in dimensions):
        raise ValueError('invalid run identity fields')
    if type(git_dirty) is not bool:
        raise TypeError('git_dirty must be boolean')
    live = lock.output_dir / shared.LIVE_DIRECTORY_NAME
    live.mkdir(exist_ok=True)
    if any(live.iterdir()):
        raise ValueError('run identity must be written before other live state')
    path = live / shared.RUN_IDENTITY_FILENAME
    identity = {'format':shared.RUN_IDENTITY_FORMAT, 'run_id':lock.run_id, 'driver':lock.command,
                'driver_version':driver_version, 'support':lock.support, 'dimensions':list(dimensions),
                'pid':lock.pid, 'started_at_utc':lock.started_at_utc,
                'git_commit':git_commit, 'git_dirty':git_dirty}
    with guarded_open(path) as stream:
        stream.write(_json_bytes(identity))
        stream.flush()
        os.fsync(stream.fileno())
    return path


class RunStatusWriter(shared.RunStatusWriter):
    """Keep live writes accounted without storing raw exception messages."""

    def _append(self, event, now, details):
        self._event_sequence += 1
        payload = {'seq':self._event_sequence, 'time':now, 'run_id':self.run_id, 'event':event, **details}
        path = self.events_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with guarded_open(path, 'ab') as stream:
            stream.write((json.dumps(payload, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8'))
            stream.flush()
            os.fsync(stream.fileno())
        return payload

    def event(self, event, *, time_utc=None, **details):
        if not event or event != event.strip() or shared._EVENT_RESERVED_FIELDS.intersection(details):
            raise ValueError('invalid event name or reserved fields')
        with self._lock:
            return self._append(event, time_utc or self._clock(), details)

    def _snapshot_notice(self, event, now, detail, **fields):
        try:
            self._append(event, now, {'detail':detail, **fields})
        except OSError:
            detail += '; diagnostic journal unavailable'
        try:
            print(f'{event}: {detail}', file=sys.stderr, flush=True)
        except OSError:
            pass  # A diagnostic sink does not authorize or revoke scientific work.

    def update(self, *, workflow_state=None, current_operation=shared._UNSET, terminal=None):
        with self._lock:
            if workflow_state is not None:
                self._workflow_state = workflow_state
            if current_operation is not shared._UNSET:
                if current_operation is not None and not isinstance(current_operation, dict):
                    raise TypeError('current_operation must be a mapping or None')
                self._current_operation = current_operation
            if terminal is not None:
                self._terminal = terminal
            now = self._clock()
            payload = self._payload(now)
            previous = getattr(self, '_snapshot_unavailable', False)
            try:
                _atomic_write_json(self.path, payload, retry_permission_errors=False)
            except OSError as error:
                if not previous:
                    from scripts.whole_source.supervision import _failure
                    self._snapshot_notice('LIVE_STATUS_UNAVAILABLE', now,
                        'Live status snapshot unavailable; computation continues.', error=_failure(error))
                self._snapshot_unavailable = True
            else:
                if previous:
                    self._snapshot_notice('LIVE_STATUS_RECOVERED', now, 'Live status snapshot publication recovered.')
                self._snapshot_unavailable = False
            return payload

    def record_failure(self, terminal_state, exc):
        from scripts.whole_source.supervision import _failure
        if terminal_state not in {'RUN_FAILED', 'RUN_INTERRUPTED'}:
            raise ValueError('invalid operational failure terminal state')
        failure = _failure(exc)
        payload = {'format':'whole-source-live-failure-v1', 'run_id':self.run_id, 'state':terminal_state,
                   'time_utc':self._clock(), 'error':failure}
        _atomic_write_json(self.failure_path, payload)
        self.update(workflow_state=terminal_state, current_operation=None, terminal=True)
        self.event(terminal_state, failure_record=f'{shared.LIVE_DIRECTORY_NAME}/{shared.RUN_FAILURE_FILENAME}',
                   error=failure)
        return payload
