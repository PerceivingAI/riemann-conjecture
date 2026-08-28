from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

from scripts.run_observability import (
    HEARTBEAT_INTERVAL_SECONDS,
    LIVE_RUN_FORMAT,
    RUN_IDENTITY_FORMAT,
    RUN_LOCK_FORMAT,
    OutputDirectoryLock,
    OutputDirectoryLockedError,
    PeriodicHeartbeat,
    RunStatusWriter,
    write_run_identity,
)


def _read_events(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_run_status_is_small_valid_json_and_atomically_replaced(tmp_path: Path) -> None:
    clock_values = iter(
        [
            "2026-08-28T02:00:01Z",
            "2026-08-28T02:00:03Z",
            "2026-08-28T02:00:04Z",
        ]
    )
    monotonic_values = iter([100.0, 100.25, 103.5, 104.0])
    output_dir = tmp_path / "continuation"

    status = RunStatusWriter.start(
        output_dir,
        command="weil_continuation_driver",
        support="27/50",
        started_at_utc="2026-08-28T02:00:00Z",
        workflow_state="VALIDATE_INPUT",
        current_operation={"stage": "VALIDATE_INPUT"},
        pid=18432,
        clock=lambda: next(clock_values),
        monotonic=lambda: next(monotonic_values),
    )

    initial = json.loads(status.path.read_text(encoding="utf-8"))
    assert initial["format"] == LIVE_RUN_FORMAT
    assert initial["run_id"].startswith("20260828T020000Z-")
    assert initial["command"] == "weil_continuation_driver"
    assert initial["support"] == "27/50"
    assert initial["pid"] == 18432
    assert initial["started_at_utc"] == "2026-08-28T02:00:00Z"
    assert initial["last_heartbeat_utc"] == "2026-08-28T02:00:01Z"
    assert initial["elapsed_seconds"] == pytest.approx(0.25)
    assert initial["workflow_state"] == "VALIDATE_INPUT"
    assert initial["current_operation"] == {"stage": "VALIDATE_INPUT"}
    assert initial["terminal"] is False

    initial_events = _read_events(status.events_path)
    assert len(initial_events) == 1
    assert initial_events[0]["seq"] == 1
    assert initial_events[0]["event"] == "RUN_STARTED"
    assert initial_events[0]["time"] == "2026-08-28T02:00:00Z"
    assert initial_events[0]["run_id"] == initial["run_id"]

    status.update(
        workflow_state="RIGOROUS_PRECISION_SEARCH",
        current_operation={"dimension": 108, "precision_ladder": [128, 256, 384]},
    )
    updated = json.loads(status.path.read_text(encoding="utf-8"))
    assert updated["run_id"] == initial["run_id"]
    assert updated["last_heartbeat_utc"] == "2026-08-28T02:00:03Z"
    assert updated["elapsed_seconds"] == pytest.approx(3.5)
    assert updated["workflow_state"] == "RIGOROUS_PRECISION_SEARCH"
    assert updated["current_operation"]["dimension"] == 108
    assert updated["terminal"] is False

    events_before_heartbeat = status.events_path.read_bytes()
    status.heartbeat()
    heartbeat = json.loads(status.path.read_text(encoding="utf-8"))
    assert heartbeat["last_heartbeat_utc"] == "2026-08-28T02:00:04Z"
    assert heartbeat["elapsed_seconds"] == pytest.approx(4.0)
    assert heartbeat["workflow_state"] == updated["workflow_state"]
    assert heartbeat["current_operation"] == updated["current_operation"]
    assert heartbeat["terminal"] is False
    assert status.events_path.read_bytes() == events_before_heartbeat
    assert not list(status.path.parent.glob("*.tmp"))
    assert status.path.stat().st_size < 4096


def test_event_journal_appends_small_ordered_json_lines(tmp_path: Path) -> None:
    clock_values = iter(
        [
            "2026-08-28T02:00:01Z",
            "2026-08-28T02:00:02Z",
            "2026-08-28T02:00:03Z",
        ]
    )
    monotonic_values = iter([100.0, 100.1])
    status = RunStatusWriter.start(
        tmp_path / "continuation",
        command="weil_continuation_driver",
        support="27/50",
        started_at_utc="2026-08-28T02:00:00Z",
        clock=lambda: next(clock_values),
        monotonic=lambda: next(monotonic_values),
    )
    prefix = status.events_path.read_bytes()

    status.event("SCOUT_STAGE_STARTED", resolution_count=3, worker_count=3)
    after_first_append = status.events_path.read_bytes()
    status.event("SCOUT_RESOLUTION_COMPLETED", level=0)

    assert after_first_append.startswith(prefix)
    assert status.events_path.read_bytes().startswith(after_first_append)
    events = _read_events(status.events_path)
    assert [event["seq"] for event in events] == [1, 2, 3]
    assert [event["event"] for event in events] == [
        "RUN_STARTED",
        "SCOUT_STAGE_STARTED",
        "SCOUT_RESOLUTION_COMPLETED",
    ]
    assert all(event["run_id"] == status.run_id for event in events)
    assert events[1]["resolution_count"] == 3
    assert events[2]["level"] == 0
    assert all(len(line) < 1024 for line in status.events_path.read_bytes().splitlines())


def test_output_directory_lock_is_os_backed_and_shares_run_identity(tmp_path: Path) -> None:
    output_dir = tmp_path / "locked-continuation"
    with OutputDirectoryLock.acquire(
        output_dir,
        command="weil_continuation_driver",
        support="27/50",
        started_at_utc="2026-08-28T03:00:00Z",
        pid=os.getpid(),
    ) as owner:
        metadata = json.loads(owner.path.read_text(encoding="utf-8"))
        assert metadata["format"] == RUN_LOCK_FORMAT
        assert metadata["run_id"] == owner.run_id
        assert metadata["pid"] == os.getpid()
        assert metadata["started_at_utc"] == "2026-08-28T03:00:00Z"

        write_run_identity(
            owner,
            driver_version="continuation-driver-test-v1",
            dimensions=[96],
            git_commit="a" * 40,
            git_dirty=False,
        )
        status = RunStatusWriter.start(
            output_dir,
            command="weil_continuation_driver",
            support="27/50",
            started_at_utc="2026-08-28T03:00:00Z",
            output_lock=owner,
        )
        assert status.run_id == owner.run_id
        assert status.pid == owner.pid

        child = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; from pathlib import Path; "
                    "from scripts.run_observability import OutputDirectoryLock, OutputDirectoryLockedError; "
                    "p=Path(sys.argv[1]); "
                    "\ntry:\n"
                    " OutputDirectoryLock.acquire(p, command='child', support='27/50')\n"
                    "except OutputDirectoryLockedError as exc:\n"
                    " print(str(exc)); raise SystemExit(23)\n"
                    "raise SystemExit(0)"
                ),
                str(output_dir),
            ],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )

        assert child.returncode == 23
        assert "already owned by another active run" in child.stdout
        assert f"run_id: {owner.run_id}" in child.stdout
        assert f"pid: {owner.pid}" in child.stdout
        assert "started_at: 2026-08-28T03:00:00Z" in child.stdout

    assert not owner.is_held


def test_lock_backed_status_requires_run_identity_first(tmp_path: Path) -> None:
    output_dir = tmp_path / "missing-identity"
    with OutputDirectoryLock.acquire(
        output_dir,
        command="weil_continuation_driver",
        support="27/50",
        started_at_utc="2026-08-28T04:00:00Z",
    ) as owner:
        with pytest.raises(ValueError, match="run.json must be written"):
            RunStatusWriter.start(
                output_dir,
                command="weil_continuation_driver",
                support="27/50",
                started_at_utc="2026-08-28T04:00:00Z",
                output_lock=owner,
            )


def test_run_identity_is_immutable_and_shared_by_subsequent_live_state(tmp_path: Path) -> None:
    output_dir = tmp_path / "identity-continuation"
    with OutputDirectoryLock.acquire(
        output_dir,
        command="weil_continuation_driver",
        support="27/50",
        started_at_utc="2026-08-28T04:00:00Z",
        pid=18432,
    ) as owner:
        identity_path = write_run_identity(
            owner,
            driver_version="continuation-driver-test-v1",
            dimensions=[96, 100, 104],
            git_commit="a" * 40,
            git_dirty=True,
        )
        identity_bytes = identity_path.read_bytes()
        identity = json.loads(identity_bytes)

        assert identity == {
            "format": RUN_IDENTITY_FORMAT,
            "run_id": owner.run_id,
            "driver": "weil_continuation_driver",
            "driver_version": "continuation-driver-test-v1",
            "support": "27/50",
            "dimensions": [96, 100, 104],
            "pid": 18432,
            "started_at_utc": "2026-08-28T04:00:00Z",
            "git_commit": "a" * 40,
            "git_dirty": True,
        }

        status = RunStatusWriter.start(
            output_dir,
            command="weil_continuation_driver",
            support="27/50",
            started_at_utc="2026-08-28T04:00:00Z",
            output_lock=owner,
        )
        status.update(
            workflow_state="RIGOROUS_PRECISION_SEARCH",
            current_operation={"dimension": 100, "precision": 256},
        )
        status.event("RIGOROUS_DIMENSION_STARTED", dimension=100)

        assert identity_path.read_bytes() == identity_bytes
        assert json.loads(status.path.read_text(encoding="utf-8"))["run_id"] == owner.run_id
        assert all(event["run_id"] == owner.run_id for event in _read_events(status.events_path))

        with pytest.raises(ValueError, match="before other live state"):
            write_run_identity(
                owner,
                driver_version="continuation-driver-test-v2",
                dimensions=[108],
                git_commit="b" * 40,
                git_dirty=False,
            )
        assert identity_path.read_bytes() == identity_bytes


def test_run_identity_prevents_silent_directory_reuse_after_lock_release(tmp_path: Path) -> None:
    output_dir = tmp_path / "interrupted-run"
    first = OutputDirectoryLock.acquire(
        output_dir,
        command="weil_continuation_driver",
        support="27/50",
        started_at_utc="2026-08-28T04:00:00Z",
    )
    write_run_identity(
        first,
        driver_version="continuation-driver-test-v1",
        dimensions=[96],
        git_commit="a" * 40,
        git_dirty=False,
    )
    first.release()

    with pytest.raises(ValueError, match="must be empty"):
        OutputDirectoryLock.acquire(
            output_dir,
            command="weil_continuation_driver",
            support="27/50",
            started_at_utc="2026-08-28T04:05:00Z",
        )

    identity = json.loads((output_dir / ".live" / "run.json").read_text(encoding="utf-8"))
    assert identity["run_id"] == first.run_id
    assert identity["driver"] == "weil_continuation_driver"


def test_stale_lock_file_does_not_block_reacquisition(tmp_path: Path) -> None:
    output_dir = tmp_path / "reusable-lock"
    first = OutputDirectoryLock.acquire(
        output_dir,
        command="weil_continuation_driver",
        support="27/50",
        started_at_utc="2026-08-28T03:00:00Z",
    )
    first_run_id = first.run_id
    first.release()

    second = OutputDirectoryLock.acquire(
        output_dir,
        command="weil_continuation_driver",
        support="27/50",
        started_at_utc="2026-08-28T03:05:00Z",
    )
    try:
        metadata = json.loads(second.path.read_text(encoding="utf-8"))
        assert second.run_id != first_run_id
        assert metadata["run_id"] == second.run_id
        assert metadata["started_at_utc"] == "2026-08-28T03:05:00Z"
    finally:
        second.release()


def test_lock_refuses_used_directory_without_leaving_new_lock_file(tmp_path: Path) -> None:
    output_dir = tmp_path / "used-before-lock"
    output_dir.mkdir()
    (output_dir / "evidence.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must be empty"):
        OutputDirectoryLock.acquire(
            output_dir,
            command="weil_continuation_driver",
            support="27/50",
        )

    assert not (output_dir / ".run.lock").exists()


def test_periodic_heartbeat_runs_without_claiming_progress_and_stops() -> None:
    class RecordingWriter:
        run_id = "test-run"

        def __init__(self) -> None:
            self.calls = 0
            self.called = threading.Event()

        def heartbeat(self) -> dict[str, object]:
            self.calls += 1
            self.called.set()
            return {"calls": self.calls}

    writer = RecordingWriter()
    heartbeat = PeriodicHeartbeat(writer, interval_seconds=0.01)  # type: ignore[arg-type]

    heartbeat.start()
    assert heartbeat.is_alive
    assert writer.called.wait(0.5)
    heartbeat.stop()
    calls_after_stop = writer.calls

    assert not heartbeat.is_alive
    time.sleep(0.03)
    assert writer.calls == calls_after_stop
    assert HEARTBEAT_INTERVAL_SECONDS == pytest.approx(12.0)


def test_periodic_heartbeat_context_joins_thread_on_exception(tmp_path: Path) -> None:
    status = RunStatusWriter.start(
        tmp_path / "continuation",
        command="weil_continuation_driver",
        support="27/50",
    )
    heartbeat: PeriodicHeartbeat | None = None

    with pytest.raises(RuntimeError, match="synthetic failure"):
        with status.periodic_heartbeats(interval_seconds=1.0) as heartbeat:
            assert heartbeat.is_alive
            raise RuntimeError("synthetic failure")

    assert heartbeat is not None
    assert not heartbeat.is_alive


def test_run_status_refuses_to_reuse_nonempty_output_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "used"
    output_dir.mkdir()
    existing = output_dir / "evidence.json"
    existing.write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must be empty"):
        RunStatusWriter.start(
            output_dir,
            command="weil_continuation_driver",
            support="27/50",
        )

    assert existing.read_text(encoding="utf-8") == "{}\n"
    assert not (output_dir / ".live").exists()
