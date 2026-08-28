from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.run_observability import LIVE_RUN_FORMAT, RunStatusWriter


def _read_events(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_run_status_is_small_valid_json_and_atomically_replaced(tmp_path: Path) -> None:
    clock_values = iter(
        [
            "2026-08-28T02:00:01Z",
            "2026-08-28T02:00:03Z",
        ]
    )
    monotonic_values = iter([100.0, 100.25, 103.5])
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
