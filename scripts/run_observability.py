"""Operational live-state primitives for long-running repository workflows.

This module intentionally carries no mathematical semantics. It provides an
immutable live run-identity record, a tiny atomically replaced JSON status file,
a small append-only JSONL event journal, a parent-owned periodic heartbeat, and
an OS-backed exclusive output-directory lock. Recovery policy belongs to later
lifecycle-hardening slices.
"""

from __future__ import annotations

import errno
import json
import os
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO, Callable, Iterator


LIVE_RUN_FORMAT = "riemann-live-run-v1"
LIVE_DIRECTORY_NAME = ".live"
RUN_STATUS_FILENAME = "run-status.json"
EVENTS_FILENAME = "events.jsonl"
RUN_IDENTITY_FILENAME = "run.json"
RUN_IDENTITY_FORMAT = "riemann-run-identity-v1"
RUN_LOCK_FILENAME = ".run.lock"
RUN_LOCK_FORMAT = "riemann-output-lock-v1"
RUN_LOCK_BYTE_OFFSET = 4096
HEARTBEAT_INTERVAL_SECONDS = 12.0
_EVENT_RESERVED_FIELDS = frozenset({"seq", "time", "run_id", "event"})


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _run_id(started_at_utc: str) -> str:
    timestamp = (
        started_at_utc.replace("-", "")
        .replace(":", "")
        .replace(".", "")
        .replace("+0000", "Z")
    )
    return f"{timestamp}-{uuid.uuid4().hex[:8]}"


def _atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    """Atomically replace *path* with one complete, valid JSON document."""
    data = (json.dumps(payload, indent=2, allow_nan=False) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_bytes(data)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _append_json_line(path: Path, payload: dict[str, object]) -> None:
    """Durably append one complete compact JSON line to *path*."""
    data = (json.dumps(payload, separators=(",", ":"), allow_nan=False) + "\n").encode(
        "utf-8"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def require_unused_output_directory(
    output_dir: Path,
    *,
    allowed_entries: frozenset[str] = frozenset(),
) -> None:
    """Fail closed before live state is created in an already-used directory."""
    if not output_dir.exists():
        return
    unexpected = [entry for entry in output_dir.iterdir() if entry.name not in allowed_entries]
    if unexpected:
        raise ValueError("continuation output directory must be empty")


_UNSET = object()


def _try_acquire_os_lock(stream: BinaryIO) -> bool:
    if os.name == "nt":
        import msvcrt

        stream.seek(RUN_LOCK_BYTE_OFFSET)
        try:
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except OSError as exc:
            if exc.errno in {errno.EACCES, errno.EAGAIN}:
                return False
            raise

    import fcntl

    try:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except BlockingIOError:
        return False


def _release_os_lock(stream: BinaryIO) -> None:
    if os.name == "nt":
        import msvcrt

        stream.seek(RUN_LOCK_BYTE_OFFSET)
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        return

    import fcntl

    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _write_lock_metadata(stream: BinaryIO, payload: dict[str, object]) -> None:
    data = (json.dumps(payload, indent=2, allow_nan=False) + "\n").encode("utf-8")
    if len(data) >= RUN_LOCK_BYTE_OFFSET:
        raise ValueError("output-directory lock metadata is unexpectedly large")
    stream.seek(0)
    stream.write(data)
    stream.truncate()
    stream.flush()
    os.fsync(stream.fileno())


def _read_lock_metadata(stream: BinaryIO) -> dict[str, object]:
    """Read owner metadata while the OS lock itself remains held."""
    try:
        stream.seek(0)
        data = stream.read()
        if not data:
            return {}
        payload = json.loads(data.decode("utf-8"))
        return payload if isinstance(payload, dict) else {}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}


class OutputDirectoryLockedError(RuntimeError):
    """Raised when another live process owns an output-directory OS lock."""

    def __init__(self, metadata: dict[str, object]) -> None:
        self.metadata = metadata
        super().__init__("output directory is already owned by another active run")

    def __str__(self) -> str:
        return "\n".join(
            [
                "output directory is already owned by another active run",
                f"run_id: {self.metadata.get('run_id', '<unknown>')}",
                f"pid: {self.metadata.get('pid', '<unknown>')}",
                f"started_at: {self.metadata.get('started_at_utc', '<unknown>')}",
            ]
        )


class OutputDirectoryLock:
    """Own one continuation output directory through a real OS-backed file lock."""

    def __init__(
        self,
        output_dir: Path,
        stream: BinaryIO,
        *,
        run_id: str,
        command: str,
        support: str,
        started_at_utc: str,
        pid: int,
    ) -> None:
        self.output_dir = output_dir
        self.path = output_dir / RUN_LOCK_FILENAME
        self.run_id = run_id
        self.command = command
        self.support = support
        self.started_at_utc = started_at_utc
        self.pid = pid
        self._stream = stream
        self._held = True

    @property
    def is_held(self) -> bool:
        return self._held

    @classmethod
    def acquire(
        cls,
        output_dir: Path,
        *,
        command: str,
        support: str,
        started_at_utc: str | None = None,
        pid: int | None = None,
        clock: Callable[[], str] = _utc_now,
    ) -> "OutputDirectoryLock":
        """Acquire exclusive ownership before any live state or computation is started."""
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / RUN_LOCK_FILENAME
        if path.exists() and not path.is_file():
            raise ValueError("output-directory lock path must be a regular file")

        existed_before = path.exists()
        fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
        stream = os.fdopen(fd, "r+b")
        try:
            if not _try_acquire_os_lock(stream):
                metadata = _read_lock_metadata(stream)
                stream.close()
                raise OutputDirectoryLockedError(metadata)

            try:
                require_unused_output_directory(
                    output_dir,
                    allowed_entries=frozenset({RUN_LOCK_FILENAME}),
                )
            except Exception:
                _release_os_lock(stream)
                stream.close()
                if not existed_before:
                    path.unlink(missing_ok=True)
                raise

            started = started_at_utc or clock()
            owner_pid = os.getpid() if pid is None else pid
            run_id = _run_id(started)
            metadata = {
                "format": RUN_LOCK_FORMAT,
                "run_id": run_id,
                "command": command,
                "support": support,
                "pid": owner_pid,
                "started_at_utc": started,
            }
            _write_lock_metadata(stream, metadata)
            return cls(
                output_dir,
                stream,
                run_id=run_id,
                command=command,
                support=support,
                started_at_utc=started,
                pid=owner_pid,
            )
        except Exception:
            if not stream.closed:
                stream.close()
            raise

    def release(self) -> None:
        if not self._held:
            return
        try:
            _release_os_lock(self._stream)
        finally:
            self._held = False
            self._stream.close()

    def __enter__(self) -> "OutputDirectoryLock":
        if not self._held:
            raise RuntimeError("output-directory lock is not held")
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        self.release()
        return False


def _read_json_object(path: Path, *, label: str) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    return payload


def write_run_identity(
    output_lock: OutputDirectoryLock,
    *,
    driver_version: str,
    dimensions: list[int],
    git_commit: str,
    git_dirty: bool,
) -> Path:
    """Write the one immutable live run identity before later live state exists."""
    if not output_lock.is_held:
        raise ValueError("output-directory lock must still be held")
    if not driver_version:
        raise ValueError("driver_version must be non-empty")
    if not dimensions or any(not isinstance(value, int) for value in dimensions):
        raise ValueError("run identity dimensions must be a non-empty integer list")
    if not git_commit:
        raise ValueError("git_commit must be non-empty")
    if not isinstance(git_dirty, bool):
        raise TypeError("git_dirty must be boolean")

    live_dir = output_lock.output_dir / LIVE_DIRECTORY_NAME
    if live_dir.exists():
        if not live_dir.is_dir():
            raise ValueError("live run path must be a directory")
        if any(live_dir.iterdir()):
            raise ValueError("run identity must be written before other live state")
    else:
        live_dir.mkdir(parents=False)

    path = live_dir / RUN_IDENTITY_FILENAME
    payload: dict[str, object] = {
        "format": RUN_IDENTITY_FORMAT,
        "run_id": output_lock.run_id,
        "driver": output_lock.command,
        "driver_version": driver_version,
        "support": output_lock.support,
        "dimensions": list(dimensions),
        "pid": output_lock.pid,
        "started_at_utc": output_lock.started_at_utc,
        "git_commit": git_commit,
        "git_dirty": git_dirty,
    }
    data = (json.dumps(payload, indent=2, allow_nan=False) + "\n").encode("utf-8")
    try:
        with path.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise ValueError("run identity already exists and is immutable") from exc
    return path


def _validate_run_identity_for_lock(output_lock: OutputDirectoryLock) -> None:
    live_dir = output_lock.output_dir / LIVE_DIRECTORY_NAME
    if not live_dir.exists():
        raise ValueError("run.json must be written before lock-backed status")
    if not live_dir.is_dir():
        raise ValueError("live run path must be a directory")
    entries = list(live_dir.iterdir())
    if not entries:
        raise ValueError("run.json must be written before lock-backed status")
    if len(entries) != 1 or entries[0].name != RUN_IDENTITY_FILENAME or not entries[0].is_file():
        raise ValueError("live directory must contain only run.json before status start")
    payload = _read_json_object(entries[0], label="run identity")
    expected = {
        "format": RUN_IDENTITY_FORMAT,
        "run_id": output_lock.run_id,
        "driver": output_lock.command,
        "support": output_lock.support,
        "pid": output_lock.pid,
        "started_at_utc": output_lock.started_at_utc,
    }
    mismatched = [key for key, value in expected.items() if payload.get(key) != value]
    if mismatched:
        raise ValueError(
            "run identity does not match output-directory lock: " + ", ".join(mismatched)
        )


class PeriodicHeartbeat:
    """Refresh one run-status file periodically from a dedicated parent thread."""

    def __init__(
        self,
        writer: "RunStatusWriter",
        *,
        interval_seconds: float = HEARTBEAT_INTERVAL_SECONDS,
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("heartbeat interval must be positive")
        self.writer = writer
        self.interval_seconds = interval_seconds
        self._stop = threading.Event()
        self._thread = threading.Thread(
            target=self._run,
            name=f"riemann-heartbeat-{writer.run_id}",
            daemon=True,
        )
        self._started = False

    @property
    def is_alive(self) -> bool:
        return self._thread.is_alive()

    def start(self) -> None:
        if self._started:
            raise RuntimeError("periodic heartbeat cannot be started twice")
        self._started = True
        self._thread.start()

    def stop(self) -> None:
        if not self._started:
            return
        self._stop.set()
        self._thread.join()

    def _run(self) -> None:
        while not self._stop.wait(self.interval_seconds):
            self.writer.heartbeat()


class RunStatusWriter:
    """Maintain authoritative live status and an append-only event chronology."""

    def __init__(
        self,
        output_dir: Path,
        *,
        run_id: str,
        command: str,
        support: str,
        started_at_utc: str,
        pid: int | None = None,
        clock: Callable[[], str] = _utc_now,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self.output_dir = output_dir
        live_dir = output_dir / LIVE_DIRECTORY_NAME
        self.path = live_dir / RUN_STATUS_FILENAME
        self.events_path = live_dir / EVENTS_FILENAME
        self.run_id = run_id
        self.command = command
        self.support = support
        self.started_at_utc = started_at_utc
        self.pid = os.getpid() if pid is None else pid
        self._clock = clock
        self._monotonic = monotonic
        self._started_monotonic = monotonic()
        self._lock = threading.Lock()
        self._event_sequence = 0
        self._workflow_state = "INITIALIZING"
        self._current_operation: dict[str, object] | None = None
        self._terminal = False

    @classmethod
    def start(
        cls,
        output_dir: Path,
        *,
        command: str,
        support: str,
        started_at_utc: str | None = None,
        workflow_state: str = "INITIALIZING",
        current_operation: dict[str, object] | None = None,
        pid: int | None = None,
        clock: Callable[[], str] = _utc_now,
        monotonic: Callable[[], float] = time.monotonic,
        output_lock: OutputDirectoryLock | None = None,
    ) -> "RunStatusWriter":
        """Create the output directory and publish the initial live state."""
        if output_lock is None:
            require_unused_output_directory(output_dir)
            started = started_at_utc or clock()
            run_id = _run_id(started)
            owner_pid = pid
        else:
            if not output_lock.is_held:
                raise ValueError("output-directory lock must still be held")
            if output_lock.output_dir != output_dir:
                raise ValueError("output-directory lock does not match status output directory")
            if output_lock.command != command:
                raise ValueError("status command does not match output-directory lock")
            if output_lock.support != support:
                raise ValueError("status support does not match output-directory lock")
            if started_at_utc is not None and started_at_utc != output_lock.started_at_utc:
                raise ValueError("status start time does not match output-directory lock")
            if pid is not None and pid != output_lock.pid:
                raise ValueError("status pid does not match output-directory lock")
            require_unused_output_directory(
                output_dir,
                allowed_entries=frozenset({RUN_LOCK_FILENAME, LIVE_DIRECTORY_NAME}),
            )
            _validate_run_identity_for_lock(output_lock)
            started = output_lock.started_at_utc
            run_id = output_lock.run_id
            owner_pid = output_lock.pid

        writer = cls(
            output_dir,
            run_id=run_id,
            command=command,
            support=support,
            started_at_utc=started,
            pid=owner_pid,
            clock=clock,
            monotonic=monotonic,
        )
        writer.event(
            "RUN_STARTED",
            time_utc=started,
            command=command,
            support=support,
            pid=writer.pid,
            workflow_state=workflow_state,
        )
        writer.update(
            workflow_state=workflow_state,
            current_operation=current_operation,
            terminal=False,
        )
        return writer

    def _payload(self, now: str) -> dict[str, object]:
        return {
            "format": LIVE_RUN_FORMAT,
            "run_id": self.run_id,
            "command": self.command,
            "support": self.support,
            "pid": self.pid,
            "started_at_utc": self.started_at_utc,
            "last_heartbeat_utc": now,
            "elapsed_seconds": round(
                max(0.0, self._monotonic() - self._started_monotonic), 3
            ),
            "workflow_state": self._workflow_state,
            "current_operation": self._current_operation,
            "terminal": self._terminal,
        }

    def event(
        self,
        event: str,
        *,
        time_utc: str | None = None,
        **details: object,
    ) -> dict[str, object]:
        """Append one structured event and return the exact persisted record."""
        if not event or event != event.strip():
            raise ValueError("event must be a non-empty normalized name")
        collisions = _EVENT_RESERVED_FIELDS.intersection(details)
        if collisions:
            raise ValueError(
                "event details cannot override reserved fields: "
                + ", ".join(sorted(collisions))
            )
        with self._lock:
            self._event_sequence += 1
            payload = {
                "seq": self._event_sequence,
                "time": time_utc or self._clock(),
                "run_id": self.run_id,
                "event": event,
                **details,
            }
            _append_json_line(self.events_path, payload)
            return payload

    def update(
        self,
        *,
        workflow_state: str | None = None,
        current_operation: dict[str, object] | None | object = _UNSET,
        terminal: bool | None = None,
    ) -> dict[str, object]:
        """Atomically publish a new status snapshot and return that snapshot."""
        with self._lock:
            if workflow_state is not None:
                self._workflow_state = workflow_state
            if current_operation is not _UNSET:
                if current_operation is not None and not isinstance(current_operation, dict):
                    raise TypeError("current_operation must be a mapping or None")
                self._current_operation = current_operation
            if terminal is not None:
                self._terminal = terminal
            payload = self._payload(self._clock())
            _atomic_write_json(self.path, payload)
            return payload

    def heartbeat(self) -> dict[str, object]:
        """Refresh liveness timestamps without claiming workflow progress."""
        return self.update()

    @contextmanager
    def periodic_heartbeats(
        self,
        *,
        interval_seconds: float = HEARTBEAT_INTERVAL_SECONDS,
    ) -> Iterator[PeriodicHeartbeat]:
        """Run periodic heartbeats and always join the heartbeat thread on exit."""
        heartbeat = PeriodicHeartbeat(self, interval_seconds=interval_seconds)
        heartbeat.start()
        try:
            yield heartbeat
        finally:
            heartbeat.stop()
