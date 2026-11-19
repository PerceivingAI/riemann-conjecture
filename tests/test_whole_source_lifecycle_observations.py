"""Synthetic lifecycle authority and comparison fixtures, not scientific runs."""
import hashlib
import json
import os
from pathlib import Path
import runpy

import pytest

from scripts.whole_source import lifecycle_observations as reader


COMPARISON = (Path(__file__).resolve().parents[1] / "computations" /
              "2026-10-31T124328Z-integrated-reference-qualification" / "compare-execution-v4.py")


def _store(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _bind_log(root, identity, rows=None, raw=None):
    path = root / "observations" / (identity + ".jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    if raw is None:
        raw = b"".join((json.dumps(row) + "\n").encode() for row in rows)
    path.write_bytes(raw)
    return {"path": "observations/" + identity + ".jsonl",
            "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)}


def _fixture(root, identity="invocationA", status="COMPLETED", elapsed=10, cumulative=10):
    policy = {"memory_bytes": 1000000, "max_active_ns": 1000}
    intent = {"format": "whole-source-lifecycle-intent-v1", "invocation_id": identity,
              "operation_id": "operationA", "policy": policy}
    sample = {"event": "sample", "invocation_id": identity, "monotonic_ns": 100,
              "phase": "source", "job": {"cpu_total_100ns": 30,
              "current_committed_bytes": 100, "peak_committed_bytes": 500},
              "caller": {"cpu_total_100ns": 7, "private_bytes": None},
              "volumes": [{"path": "D:/", "free_bytes": None}], "progress": "opaque"}
    terminal = {**sample, "event": "terminal", "monotonic_ns": 110, "job": None,
                "caller": None, "volumes": None, "phase": None}
    rows = [sample, terminal]
    receipt = {"format": "whole-source-lifecycle-receipt-v1", "invocation_id": identity,
               "operation_id": "operationA", "status": status,
               "reason": None if status == "COMPLETED" else "synthetic stop",
               "elapsed_ns": elapsed, "cumulative_active_ns": cumulative,
               "child_returncode": 0 if status == "COMPLETED" else None,
               "policy": policy, "upstream": {"available": None},
               "final_job": {"cpu_total_100ns": 90, "current_committed_bytes": 0,
                             "peak_committed_bytes": 900, "active_process_count": 0,
                             "active_process_ids": []},
               "cleanup_verified": True, "observation": _bind_log(root, identity, rows),
               "code": {"scripts/whole_source/supervision.py": "a" * 64}}
    _store(root / "intents" / (identity + ".json"), intent)
    _store(root / "receipts" / (identity + ".json"), receipt)
    return intent, receipt, rows


def _receipt(root, value, identity="invocationA"):
    _store(root / "receipts" / (identity + ".json"), value)


def test_all_invocations_stay_separate_and_ledger_is_not_summed(tmp_path):
    _fixture(tmp_path, "invocationZ", "REFUSED", elapsed=0, cumulative=30)
    _fixture(tmp_path, "invocationB", "INTERRUPTED", elapsed=20, cumulative=30)
    _fixture(tmp_path, "invocationA", elapsed=10, cumulative=10)
    report = reader.lifecycle_resources(tmp_path)
    assert report["invocation_count"] == 3
    assert report["status_counts"] == {"COMPLETED": 1, "INTERRUPTED": 1, "REFUSED": 1}
    assert [row["invocation_id"] for row in report["invocations"]] == [
        "invocationA", "invocationB", "invocationZ"]
    assert report["invocation_elapsed_ns"] == 30
    assert report["cumulative_active_ns"] == 30
    assert report["reviewer_waiting_ns"] is None
    assert report["scientific_acceptance_asserted"] is False
    assert report["scope"] == "ALL_LIFECYCLE_INVOCATIONS_OPERATIONAL_ONLY"


def test_raw_final_counters_and_sample_maxima_are_distinct(tmp_path):
    _fixture(tmp_path)
    row = reader.lifecycle_resources(tmp_path)["invocations"][0]
    assert row["raw_os_final_job_counters"]["cpu_total_100ns"] == 90
    assert row["raw_os_final_job_counters"]["peak_committed_bytes"] == 900
    assert row["observations"]["sample_maxima"]["job"]["cpu_total_100ns"] == 30
    assert row["observations"]["sample_maxima"]["job"]["current_committed_bytes"] == 100
    assert row["observations"]["sample_maxima"]["caller"]["cpu_total_100ns"] == 7
    assert row["observations"]["sample_maxima"]["caller"]["private_bytes"] is None
    diagnostics = row["observations"]["field_diagnostics"]
    assert diagnostics["caller.private_bytes:NULL"] == 1
    assert diagnostics["caller.working_set_bytes:MISSING"] == 1
    assert diagnostics["row.job:NULL"] == 1
    assert row["upstream"] == {"available": None}
    for kind in ("intent_binding", "receipt_binding"):
        ref = row[kind]
        raw = (tmp_path / ref["path"]).read_bytes()
        assert ref["sha256"] == hashlib.sha256(raw).hexdigest()
        assert ref["size"] == len(raw)


def test_unretained_historical_metrics_are_unknown():
    report = reader.lifecycle_resources(None)
    assert report["availability"] == "UNAVAILABLE"
    for field in ("invocations", "invocation_count", "status_counts", "invocation_elapsed_ns",
                  "cumulative_active_ns", "reviewer_waiting_ns"):
        assert report[field] is None


@pytest.mark.parametrize("folder,suffix", [("intents", ".json"), ("receipts", ".json"),
                                           ("observations", ".jsonl")])
def test_missing_authority_refused(tmp_path, folder, suffix):
    _fixture(tmp_path)
    (tmp_path / folder / ("invocationA" + suffix)).unlink()
    with pytest.raises(ValueError, match="authority"):
        reader.lifecycle_resources(tmp_path)


def test_empty_root_is_not_success(tmp_path):
    for name in ("intents", "receipts", "observations"):
        (tmp_path / name).mkdir()
    with pytest.raises(ValueError, match="empty"):
        reader.lifecycle_resources(tmp_path)


@pytest.mark.parametrize("field,value", [
    ("format", "wrong"), ("invocation_id", "other"), ("operation_id", "other"),
    ("policy", {}), ("status", "RUNNING"), ("elapsed_ns", True),
    ("elapsed_ns", -1), ("cumulative_active_ns", 9), ("child_returncode", True),
    ("cleanup_verified", False), ("child_returncode", 1), ("upstream", None),
    ("code", {}), ("code", {"../escape.py": "a" * 64}),
    ("code", {"x.py": "bad"}), ("final_job", []),
])
def test_invalid_terminal_receipt_refused(tmp_path, field, value):
    _, receipt, _ = _fixture(tmp_path)
    receipt[field] = value
    _receipt(tmp_path, receipt)
    with pytest.raises(ValueError):
        reader.lifecycle_resources(tmp_path)


@pytest.mark.parametrize("field", ["reason", "final_job", "elapsed_ns", "observation",
                                    "child_returncode", "cleanup_verified"])
def test_missing_receipt_fields_refused(tmp_path, field):
    _, receipt, _ = _fixture(tmp_path)
    del receipt[field]
    _receipt(tmp_path, receipt)
    with pytest.raises(ValueError):
        reader.lifecycle_resources(tmp_path)


def test_null_final_job_remains_unknown_for_refusal(tmp_path):
    _, receipt, _ = _fixture(tmp_path, status="REFUSED")
    receipt["final_job"] = None
    receipt["cleanup_verified"] = False
    _receipt(tmp_path, receipt)
    row = reader.lifecycle_resources(tmp_path)["invocations"][0]
    assert row["final_job"] is None
    assert all(value is None for value in row["raw_os_final_job_counters"].values())
    assert row["final_job_field_diagnostics"] == {"final_job:NULL": 1}


@pytest.mark.parametrize("path", ["../outside.jsonl", "/absolute.jsonl", "observations\\invocationA.jsonl",
                                  "observations/./invocationA.jsonl", "observations//invocationA.jsonl",
                                  "observations/invocationA.jsonl:stream", "observations/NUL.jsonl",
                                  "observations/invocationA.jsonl."])
def test_observation_path_aliases_refused(tmp_path, path):
    _, receipt, _ = _fixture(tmp_path)
    receipt["observation"]["path"] = path
    _receipt(tmp_path, receipt)
    with pytest.raises(ValueError):
        reader.lifecycle_resources(tmp_path)


@pytest.mark.parametrize("change", ["identity", "clock", "no_terminal", "after_terminal",
                                   "duplicate_terminal", "bad_event", "bad_counter", "bad_progress"])
def test_log_authority_and_counter_validation(tmp_path, change):
    _, receipt, rows = _fixture(tmp_path)
    if change == "identity":
        rows[0]["invocation_id"] = "other"
    elif change == "clock":
        rows[1]["monotonic_ns"] = 99
    elif change == "no_terminal":
        rows.pop()
    elif change == "after_terminal":
        rows.append(rows[0])
    elif change == "duplicate_terminal":
        rows.append(rows[1])
    elif change == "bad_event":
        rows[0]["event"] = "invented"
    elif change == "bad_counter":
        rows[0]["job"]["cpu_total_100ns"] = -1
    else:
        rows[0]["progress"] = 20
    receipt["observation"] = _bind_log(tmp_path, "invocationA", rows)
    _receipt(tmp_path, receipt)
    with pytest.raises(ValueError):
        reader.lifecycle_resources(tmp_path)


@pytest.mark.parametrize("raw", [b"{broken}\n", b"[]\n", b"\xff\n", b'{"x":NaN}\n',
                                 b'{"event":"sample","event":"terminal"}\n', b'{}'])
def test_invalid_log_bytes_even_with_matching_hash_refused(tmp_path, raw):
    _, receipt, _ = _fixture(tmp_path)
    receipt["observation"] = _bind_log(tmp_path, "invocationA", raw=raw)
    _receipt(tmp_path, receipt)
    with pytest.raises(ValueError):
        reader.lifecycle_resources(tmp_path)


@pytest.mark.parametrize("field,value", [("sha256", "f" * 64), ("size", 1), ("size", True)])
def test_log_binding_corruption_refused(tmp_path, field, value):
    _, receipt, _ = _fixture(tmp_path)
    receipt["observation"][field] = value
    _receipt(tmp_path, receipt)
    with pytest.raises(ValueError):
        reader.lifecycle_resources(tmp_path)


def test_bounded_document_and_log_loading(tmp_path, monkeypatch):
    _fixture(tmp_path)
    monkeypatch.setattr(reader, "MAX_DOCUMENT_BYTES", 8)
    with pytest.raises(ValueError, match="size bound"):
        reader.lifecycle_resources(tmp_path)
    monkeypatch.setattr(reader, "MAX_DOCUMENT_BYTES", 1024 * 1024)
    monkeypatch.setattr(reader, "MAX_ROW_BYTES", 8)
    with pytest.raises(ValueError, match="oversized"):
        reader.lifecycle_resources(tmp_path)


def test_hardlink_alias_refused(tmp_path):
    _fixture(tmp_path)
    original = tmp_path / "receipts/invocationA.json"
    alias = tmp_path / "receipt-alias.json"
    try:
        os.link(original, alias)
    except OSError as exc:
        pytest.skip(str(exc))
    with pytest.raises(ValueError, match="hard-linked"):
        reader.lifecycle_resources(tmp_path)


@pytest.mark.parametrize("target", ["root", "directory", "file"])
def test_symlink_alias_refused(tmp_path, target):
    root = tmp_path / "real"
    _fixture(root)
    if target == "root":
        link, destination = tmp_path / "alias", root
    elif target == "directory":
        destination = root / "retained-receipts"
        (root / "receipts").rename(destination)
        link = root / "receipts"
    else:
        destination = root / "saved-receipt.json"
        (root / "receipts/invocationA.json").rename(destination)
        link = root / "receipts/invocationA.json"
    try:
        link.symlink_to(destination, target_is_directory=target != "file")
    except OSError as exc:
        pytest.skip(str(exc))
    with pytest.raises(ValueError, match="symlink|reparse|alias"):
        reader.lifecycle_resources(link if target == "root" else root)


def test_case_alias_catalog_refused(tmp_path):
    _fixture(tmp_path)
    # Distinct filenames with case-aliased identities are rejected on every OS.
    alias = tmp_path / "intents/invocationa.json"
    if alias.exists():
        pytest.skip("case-insensitive filesystem cannot represent this fixture")
    _store(alias, {})
    with pytest.raises(ValueError, match="case-aliased"):
        reader.lifecycle_resources(tmp_path)


def test_v4_main_keeps_scientific_seams_and_separates_all_lifecycle(tmp_path, monkeypatch):
    namespace = runpy.run_path(str(COMPARISON))
    main = namespace["main"]
    globals_ = main.__globals__
    assert globals_["resources"].__code__.co_filename.endswith("compare-execution-v3.py")
    run, baseline, lifecycle = (tmp_path / name for name in ("run", "baseline", "lifecycle"))
    run.mkdir()
    baseline.mkdir()
    _fixture(lifecycle)
    monkeypatch.setitem(globals_, "resources", lambda path: {
        "owned_receipts_verified": 2, "all_owned_cleanup_verified": True,
        "scientific_stage_sentinel": "unchanged"})
    monkeypatch.setitem(globals_["_numerical"], "baseline", lambda path: {"old": "unchanged"})
    monkeypatch.setitem(globals_["_numerical"], "footprint", lambda path: {"bytes": 5})
    monkeypatch.setitem(globals_["_numerical"], "compare_sources", lambda new, old: {"source": "unchanged"})
    output = tmp_path / "report.json"
    main(["--run-dir", str(run), "--baseline-dir", str(baseline), "--output", str(output),
          "--new-lifecycle-root", str(lifecycle), "--compare-source"])
    report = json.loads(output.read_bytes())
    assert report["format"] == "whole-source-retained-execution-comparison-v4"
    assert report["status"].startswith("PROSPECTIVE_")
    assert report["new"]["scientific_stage_sentinel"] == "unchanged"
    assert report["baseline"] == {"old": "unchanged"}
    assert report["source_comparison"] == {"source": "unchanged"}
    assert report["lifecycle"]["new"]["invocation_count"] == 1
    assert report["lifecycle"]["baseline"]["invocation_count"] is None
    assert report["production_admission"] is False


def test_v4_requires_new_lifecycle_root():
    main = runpy.run_path(str(COMPARISON))["main"]
    with pytest.raises(SystemExit):
        main(["--run-dir", ".", "--baseline-dir", ".", "--output", "unused.json"])


def test_descriptive_progress_and_raw_held_process_diagnostics_retained(tmp_path):
    _, receipt, rows = _fixture(tmp_path)
    progress = {"phase": "source", "state": "working", "work": "block 7",
                "pid": 123, "monotonic_ns": 99}
    held = [{"pid": 123, "creation_time_100ns": 88, "cpu_user_100ns": None,
             "cpu_kernel_100ns": None, "memory": None, "diagnostics": ["query unavailable"]}]
    rows[0]["progress"] = progress
    rows[0]["job"]["root_processes"] = held
    rows[1]["progress"] = progress
    receipt["observation"] = _bind_log(tmp_path, "invocationA", rows)
    _receipt(tmp_path, receipt)
    observation = reader.lifecycle_resources(tmp_path)["invocations"][0]["observations"]
    assert observation["last_observation"]["progress"] == progress
    assert observation["last_job_observation"]["root_processes"] == held


def test_direct_receipt_verification_checks_actual_intent_binding(tmp_path):
    intent, receipt, _ = _fixture(tmp_path)
    path = tmp_path / "intents/invocationA.json"
    raw = path.read_bytes()
    receipt["intent"] = {"path": "intents/invocationA.json",
                         "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)}
    _receipt(tmp_path, receipt)
    assert reader.read_receipt(tmp_path, "invocationA") == receipt
    intent["extra"] = "changed"
    _store(path, intent)
    with pytest.raises(ValueError, match="intent binding"):
        reader.read_receipt(tmp_path, "invocationA")


def test_direct_receipt_does_not_require_unrelated_invocation_to_end(tmp_path):
    _, receipt, _ = _fixture(tmp_path)
    _store(tmp_path / "intents/pending.json", {
        "format": "whole-source-lifecycle-intent-v1", "invocation_id": "pending"})
    assert reader.read_receipt(tmp_path, "invocationA") == receipt
    _, reference = reader.read_bound_receipt(tmp_path, "invocationA")
    raw = (tmp_path / reference["path"]).read_bytes()
    assert reference == {"path": "receipts/invocationA.json",
                         "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)}
    with pytest.raises(ValueError, match="authority"):
        reader.lifecycle_resources(tmp_path)


def test_current_diagnostics_hash_is_separate_from_terminal_cleanup(tmp_path):
    from scripts.whole_source import supervision

    identity = "1" * 32
    operation_id = "a" * 64
    intent, receipt, rows = _fixture(tmp_path, identity)
    intent.update(format=supervision.INTENT, code=receipt["code"], upstream=receipt["upstream"],
                  operation_id=operation_id)
    intent_path = tmp_path / "intents" / (identity + ".json")
    _store(intent_path, intent)
    diagnostic = tmp_path / "diagnostics" / (identity + ".json")
    _store(diagnostic, {"format": supervision.DIAGNOSTICS, "invocation_id": identity,
                        "stdout_bytes": 10, "stderr_bytes": 0, "headlines": [], "failure": None})
    rows[-1].update(status=receipt["status"], reason=receipt["reason"], job=receipt["final_job"],
                    elapsed_ns=receipt["elapsed_ns"])

    def ref(path):
        raw = path.read_bytes()
        return {"path": path.relative_to(tmp_path).as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)}

    receipt.update(format=supervision.RECEIPT, intent=ref(intent_path), diagnostics=ref(diagnostic),
                   operation_id=operation_id, observation=_bind_log(tmp_path, identity, rows))
    _receipt(tmp_path, receipt, identity)
    assert reader.read_receipt(tmp_path, identity) == receipt
    diagnostic.write_bytes(diagnostic.read_bytes().replace(b'"stdout_bytes": 10', b'"stdout_bytes": 11'))
    with pytest.raises(ValueError, match="diagnostics binding mismatch"):
        reader.read_receipt(tmp_path, identity)
    assert reader.read_authority(tmp_path, identity) == receipt
    binding = {"role": "lifecycle", "invocation_id": identity,
               "operation_id": operation_id, "intent": receipt["intent"]}
    current = {"root": str(tmp_path), "invocation_id": "2" * 32,
               "operation_id": operation_id, "code": receipt["code"]}
    expected = receipt, ref(tmp_path / "receipts" / (identity + ".json"))
    assert supervision.read_phase_authority(binding, current=current) == expected
    diagnostic.unlink()
    assert supervision.read_phase_authority(binding, current=current) == expected
    _store(diagnostic, {"format": supervision.DIAGNOSTICS, "invocation_id": identity,
                        "stdout_bytes": 11, "stderr_bytes": 0, "headlines": [], "failure": None})
    receipt["diagnostics"] = ref(diagnostic)
    _receipt(tmp_path, receipt, identity)
    report = reader.lifecycle_resources(tmp_path)
    assert report["invocations"][0]["stream_diagnostics"]["stdout_bytes"] == 11
    rows[-1]["job"] = None
    receipt["observation"] = _bind_log(tmp_path, identity, rows)
    _receipt(tmp_path, receipt, identity)
    with pytest.raises(ValueError, match="cleanup or elapsed time mismatch"):
        supervision.read_phase_authority(binding, current=current)


def test_terminal_status_cannot_conflict_with_receipt(tmp_path):
    _, receipt, rows = _fixture(tmp_path)
    rows[-1]["status"] = "INTERRUPTED"
    receipt["observation"] = _bind_log(tmp_path, "invocationA", rows)
    _receipt(tmp_path, receipt)
    with pytest.raises(ValueError, match="terminal and receipt"):
        reader.lifecycle_resources(tmp_path)


def test_final_cleanup_cannot_claim_active_owned_processes(tmp_path):
    _, receipt, _ = _fixture(tmp_path)
    receipt["final_job"]["active_process_count"] = 1
    _receipt(tmp_path, receipt)
    with pytest.raises(ValueError):
        reader.lifecycle_resources(tmp_path)


def test_terminal_counters_are_not_relabelled_as_sample_maxima(tmp_path):
    _, receipt, rows = _fixture(tmp_path)
    rows[-1]["job"] = receipt["final_job"]
    receipt["observation"] = _bind_log(tmp_path, "invocationA", rows)
    _receipt(tmp_path, receipt)
    observation = reader.lifecycle_resources(tmp_path)["invocations"][0]["observations"]
    assert observation["sample_maxima"]["job"]["cpu_total_100ns"] == 30
    assert observation["terminal"]["job"]["cpu_total_100ns"] == 90


def test_nonfinite_overflow_number_is_not_json_evidence(tmp_path):
    _, receipt, _ = _fixture(tmp_path)
    receipt["observation"] = _bind_log(tmp_path, "invocationA", raw=b'{"value":1e999}\n')
    _receipt(tmp_path, receipt)
    with pytest.raises(ValueError, match="invalid lifecycle JSON"):
        reader.lifecycle_resources(tmp_path)


def test_artifact_mutation_during_read_refused(tmp_path, monkeypatch):
    _fixture(tmp_path)
    original_exit = reader._Artifact.__exit__

    def mutate_before_exit(self, kind, value, traceback):
        if self.path.name == "invocationA.json" and self.path.parent.name == "intents":
            with self.path.open("ab") as stream:
                stream.write(b" ")
        return original_exit(self, kind, value, traceback)

    monkeypatch.setattr(reader._Artifact, "__exit__", mutate_before_exit)
    with pytest.raises(ValueError, match="changed while reading"):
        reader.lifecycle_resources(tmp_path)
