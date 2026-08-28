"""Operational live-state primitives for long-running repository workflows.

This module intentionally carries no mathematical semantics. It provides a tiny,
atomically replaced JSON status file, a small append-only JSONL event journal,
and a parent-owned periodic heartbeat that can be inspected safely while a run
is active. Run locking and recovery policy belong to later lifecycle-hardening
slices.
"""

from __future__ import annotations

import json
import os
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator


LIVE_RUN_FORMAT = "riemann-live-run-v1"
LIVE_DIRECTORY_NAME = ".live"
RUN_STATUS_FILENAME = "run-status.json"
EVENTS_FILENAME = "events.jsonl"
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


def require_unused_output_directory(output_dir: Path) -> None:
    """Fail closed before live state is created in an already-used directory."""
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("continuation output directory must be empty")


_UNSET = object()


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
    ) -> "RunStatusWriter":
        """Create the output directory and publish the initial live state."""
        require_unused_output_directory(output_dir)
        started = started_at_utc or clock()
        writer = cls(
            output_dir,
            run_id=_run_id(started),
            command=command,
            support=support,
            started_at_utc=started,
            pid=pid,
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
