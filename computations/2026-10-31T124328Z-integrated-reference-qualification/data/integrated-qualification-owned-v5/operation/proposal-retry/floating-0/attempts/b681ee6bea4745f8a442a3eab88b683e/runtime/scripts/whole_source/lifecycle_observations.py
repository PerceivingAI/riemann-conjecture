"""Verify external lifecycle evidence without granting scientific approval.

Documents are bounded and logs are hashed while streaming. Job counters include
all owned descendants; caller counters are separate observations, never additions.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat


MAX_DOCUMENT_BYTES = 65536
MAX_ROW_BYTES = 8192
MAX_LOG_BYTES = 16 * 1024 * 1024
MAX_INVOCATIONS = 1024
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_JOB_COUNTERS = ("cpu_total_100ns", "cpu_user_100ns", "cpu_kernel_100ns",
                 "current_committed_bytes", "peak_committed_bytes")
_CALLER_COUNTERS = ("cpu_total_100ns", "cpu_user_100ns", "cpu_kernel_100ns",
                    "current_committed_bytes", "private_bytes", "working_set_bytes")


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _integer(value, name):
    _require(type(value) is int and value >= 0, "invalid " + name)
    return value


def _relative(value):
    _require(type(value) is str and 0 < len(value) <= 512, "invalid relative path")
    _require("\\" not in value and ":" not in value and "\0" not in value,
             "noncanonical relative path")
    parts = value.split("/")
    _require(all(part and part not in (".", "..") and
                 not part.endswith((" ", ".")) and
                 not any(ord(char) < 32 for char in part) for part in parts),
             "noncanonical relative path")
    for part in parts:
        _require(part.split(".")[0].upper() not in
                 {"CON", "PRN", "AUX", "NUL", *("COM" + str(i) for i in range(1, 10)),
                  *("LPT" + str(i) for i in range(1, 10))}, "reserved path alias")
    _require(not PurePosixPath(value).is_absolute(), "absolute relative path")
    return value


def _plain(path, *, directory=False):
    info = path.lstat()
    _require(not stat.S_ISLNK(info.st_mode) and
             not (getattr(info, "st_file_attributes", 0) & 0x400),
             "symlink or reparse point: " + str(path))
    _require(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode),
             "unexpected file type: " + str(path))
    if not directory:
        _require(info.st_nlink == 1, "hard-linked artifact: " + str(path))
    return info


def _root(path):
    root = Path(os.path.abspath(path))
    for ancestor in (*reversed(root.parents), root):
        _plain(ancestor, directory=True)
    _require(root.resolve(strict=True) == root, "aliased lifecycle root")
    return root


def _signature(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns,
            getattr(info, "st_birthtime_ns", None), info.st_nlink)


class _Artifact:
    def __init__(self, path, limit):
        self.path, self.limit = path, limit

    def __enter__(self):
        self.before = _plain(self.path)
        _require(self.before.st_size <= self.limit, "artifact exceeds size bound")
        descriptor = os.open(self.path, os.O_RDONLY | getattr(os, "O_BINARY", 0) |
                             getattr(os, "O_NOFOLLOW", 0))
        self.stream = os.fdopen(descriptor, "rb")
        try:
            self.opened = os.fstat(descriptor)
            _require(_signature(self.opened) == _signature(self.before),
                     "artifact changed while opening")
        except BaseException:
            self.stream.close()
            raise
        return self.stream

    def __exit__(self, kind, value, traceback):
        try:
            if kind is None:
                final, named = os.fstat(self.stream.fileno()), _plain(self.path)
                _require(_signature(final) == _signature(self.before) == _signature(named) and
                         final.st_ctime_ns == self.opened.st_ctime_ns and
                         named.st_ctime_ns == self.before.st_ctime_ns,
                         "artifact changed while reading")
        finally:
            self.stream.close()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def _float(value):
    result = float(value)
    _require(math.isfinite(result), "nonfinite JSON number")
    return result


def _json(raw):
    try:
        value = json.loads(raw, object_pairs_hook=_pairs, parse_float=_float,
                           parse_constant=lambda value: (_ for _ in ()).throw(
                               ValueError("nonfinite JSON constant")))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ValueError("invalid lifecycle JSON") from exc
    _require(type(value) is dict, "lifecycle JSON must be an object")
    return value


def _document(path):
    with _Artifact(path, MAX_DOCUMENT_BYTES) as stream:
        raw = stream.read(MAX_DOCUMENT_BYTES + 1)
        _require(len(raw) <= MAX_DOCUMENT_BYTES, "document exceeds size bound")
    return _json(raw), {"path": path.name, "sha256": hashlib.sha256(raw).hexdigest(),
                        "size": len(raw)}


def _catalog(root, name, suffix):
    directory = root / name
    _plain(directory, directory=True)
    result = {}
    with os.scandir(directory) as entries:
        for entry in entries:
            _require(len(result) < MAX_INVOCATIONS, "too many lifecycle invocations")
            _require(entry.name.endswith(suffix), "unexpected lifecycle artifact")
            identity = entry.name[:-len(suffix)]
            _require(_ID.fullmatch(identity) is not None, "invalid invocation filename")
            _require(entry.name == identity + suffix, "aliased invocation filename")
            _plain(directory / entry.name)
            folded = identity.casefold()
            _require(folded not in result, "case-aliased invocation")
            result[folded] = identity
    return result


def _field_diagnostic(diagnostics, value, key, prefix):
    if key not in value:
        diagnostics[prefix + key + ":MISSING"] += 1
    elif value[key] is None:
        diagnostics[prefix + key + ":NULL"] += 1


def _counters(value, keys, prefix, diagnostics, maxima):
    for key in keys:
        _field_diagnostic(diagnostics, value, key, prefix)
        counter = value.get(key)
        if counter is not None:
            _integer(counter, prefix + key)
            previous = maxima[key]
            maxima[key] = counter if previous is None else max(previous, counter)


def _log(root, identity, reference):
    _require(type(reference) is dict and set(reference) == {"path", "sha256", "size"},
             "invalid observation binding")
    relative = _relative(reference["path"])
    _require(relative == "observations/" + identity + ".jsonl", "observation path mismatch")
    _require(type(reference["sha256"]) is str and _SHA.fullmatch(reference["sha256"]),
             "invalid observation digest")
    size = _integer(reference["size"], "observation size")
    _require(size <= MAX_LOG_BYTES, "observation exceeds size bound")
    digest, actual, previous, terminal = hashlib.sha256(), 0, None, False
    counts, diagnostics = Counter(), Counter()
    job_maxima = dict.fromkeys(_JOB_COUNTERS)
    caller_maxima = dict.fromkeys(_CALLER_COUNTERS)
    last = {"phase": None, "progress": None, "caller": None, "volumes": None}
    last_job = None
    with _Artifact(root / relative, MAX_LOG_BYTES) as stream:
        while raw := stream.readline(MAX_ROW_BYTES + 1):
            _require(len(raw) <= MAX_ROW_BYTES and raw.endswith(b"\n"),
                     "oversized or incomplete observation row")
            actual += len(raw)
            _require(actual <= size, "observation size mismatch")
            digest.update(raw)
            _require(not terminal, "observation follows terminal row")
            row = _json(raw)
            _require(row.get("invocation_id") == identity, "observation identity mismatch")
            event = row.get("event")
            _require(type(event) is str and event in ("sample", "phase", "work", "terminal"),
                     "invalid observation event")
            stamp = _integer(row.get("monotonic_ns"), "observation monotonic_ns")
            _require(previous is None or stamp >= previous, "observation clock regressed")
            previous = stamp
            counts[event] += 1
            for key, expected in (("phase", str), ("job", dict), ("caller", dict), ("volumes", list)):
                _field_diagnostic(diagnostics, row, key, "row.")
                _require(row.get(key) is None or type(row[key]) is expected,
                         "invalid observation " + key)
            progress = row.get("progress")
            _require((type(progress) is str and bool(progress)) or
                     (type(progress) is dict and bool(progress)), "missing observation progress")
            if row.get("job") is not None:
                last_job = row["job"]
                _counters(row["job"], _JOB_COUNTERS, "job.", diagnostics,
                          job_maxima if event == "sample" else dict.fromkeys(_JOB_COUNTERS))
            if row.get("caller") is not None:
                _counters(row["caller"], _CALLER_COUNTERS, "caller.", diagnostics,
                          caller_maxima if event == "sample" else dict.fromkeys(_CALLER_COUNTERS))
            for key in last:
                last[key] = row.get(key)
            terminal = event == "terminal"
    _require(actual == size and digest.hexdigest() == reference["sha256"],
             "observation binding mismatch")
    _require(terminal, "missing terminal observation authority")
    return {"events": dict(counts), "sample_maxima": {"job": job_maxima, "caller": caller_maxima},
            "field_diagnostics": dict(sorted(diagnostics.items())), "last_observation": last,
            "last_job_observation": last_job, "terminal": row}


def _invocation(root, identity, *, summarize=True):
    intent, intent_ref = _document(root / "intents" / (identity + ".json"))
    receipt, receipt_ref = _document(root / "receipts" / (identity + ".json"))
    _require(intent.get("format") == "whole-source-lifecycle-intent-v1", "invalid intent format")
    _require(receipt.get("format") == "whole-source-lifecycle-receipt-v1", "invalid receipt format")
    for document in (intent, receipt):
        _require(document.get("invocation_id") == identity, "document identity mismatch")
        _require(type(document.get("operation_id")) is str and bool(document["operation_id"]),
                 "invalid operation identity")
        _require(type(document.get("policy")) is dict, "invalid lifecycle policy")
    _require(intent["operation_id"] == receipt["operation_id"] and
             intent["policy"] == receipt["policy"], "intent and receipt mismatch")
    required = {"status", "reason", "elapsed_ns", "cumulative_active_ns", "child_returncode",
                "upstream", "final_job", "cleanup_verified", "observation", "code"}
    _require(required <= receipt.keys(), "missing receipt authority fields")
    _require(receipt["status"] in ("COMPLETED", "INTERRUPTED", "REFUSED"), "invalid receipt status")
    _require(receipt["reason"] is None or type(receipt["reason"]) is str, "invalid receipt reason")
    _integer(receipt["elapsed_ns"], "elapsed_ns")
    _integer(receipt["cumulative_active_ns"], "cumulative_active_ns")
    _require(receipt["cumulative_active_ns"] >= receipt["elapsed_ns"], "active ledger below invocation time")
    _require(receipt["child_returncode"] is None or type(receipt["child_returncode"]) is int,
             "invalid child return code")
    _require(type(receipt["upstream"]) is dict, "invalid upstream diagnostics")
    _require(receipt["final_job"] is None or type(receipt["final_job"]) is dict, "invalid final job")
    _require(type(receipt["cleanup_verified"]) is bool, "invalid cleanup authority")
    if receipt["status"] == "COMPLETED":
        _require(receipt["child_returncode"] == 0 and receipt["cleanup_verified"],
                 "completed receipt lacks successful cleanup")
    if receipt["cleanup_verified"]:
        final_job = receipt["final_job"]
        _require(type(final_job) is dict and
                 type(final_job.get("active_process_count")) is int and
                 final_job["active_process_count"] == 0 and
                 final_job.get("active_process_ids") == [],
                 "cleanup lacks observed zero owned processes")
    _require(type(receipt["code"]) is dict and bool(receipt["code"]), "missing code bindings")
    folded = set()
    for path, sha in receipt["code"].items():
        _relative(path)
        _require(path.casefold() not in folded, "aliased code binding")
        folded.add(path.casefold())
        _require(type(sha) is str and _SHA.fullmatch(sha), "invalid code digest")
    observation = _log(root, identity, receipt["observation"])
    for field in ("status", "reason"):
        terminal = observation["terminal"]
        if field in terminal:
            _require(terminal[field] == receipt[field], "terminal and receipt " + field + " mismatch")
    diagnostics = Counter()
    final = dict.fromkeys(_JOB_COUNTERS)
    if receipt["final_job"] is not None:
        _counters(receipt["final_job"], _JOB_COUNTERS, "final_job.", diagnostics, final)
    else:
        diagnostics["final_job:NULL"] += 1
    intent_ref["path"] = "intents/" + identity + ".json"
    if "intent" in receipt:
        _require(receipt["intent"] == intent_ref, "intent binding mismatch")
    for field in ("code", "upstream"):
        if field in intent:
            _require(intent[field] == receipt[field], "intent and receipt " + field + " mismatch")
    receipt_ref["path"] = "receipts/" + identity + ".json"
    if not summarize:
        return receipt
    return {**receipt, "intent_binding": intent_ref, "receipt_binding": receipt_ref,
            "raw_os_final_job_counters": final,
            "final_job_field_diagnostics": dict(diagnostics), "observations": observation}


def read_receipt(root, invocation_id) -> dict:
    """Verify one immutable invocation without requiring other invocations to end."""
    _require(type(invocation_id) is str and _ID.fullmatch(invocation_id), "invalid invocation ID")
    root = _root(root)
    for folder, suffix in (("intents", ".json"), ("receipts", ".json"), ("observations", ".jsonl")):
        catalog = _catalog(root, folder, suffix)
        _require(catalog.get(invocation_id.casefold()) == invocation_id,
                 "missing or aliased invocation authority")
    return _invocation(root, invocation_id, summarize=False)


def lifecycle_resources(root) -> dict:
    """Read every invocation or refuse incomplete, corrupt or aliased evidence."""
    if root is None:
        return {"availability": "UNAVAILABLE", "reason": "LIFECYCLE_ROOT_NOT_RETAINED",
                "invocations": None, "invocation_count": None, "status_counts": None,
                "invocation_elapsed_ns": None, "cumulative_active_ns": None,
                "reviewer_waiting_ns": None, "scientific_acceptance_asserted": False}
    root = _root(root)
    intents = _catalog(root, "intents", ".json")
    receipts = _catalog(root, "receipts", ".json")
    observations = _catalog(root, "observations", ".jsonl")
    _require(intents == receipts == observations, "missing or orphaned lifecycle authority")
    _require(bool(intents), "empty lifecycle authority")
    rows = [_invocation(root, identity) for identity in sorted(intents.values())]
    statuses = Counter(row["status"] for row in rows)
    return {"availability": "AVAILABLE", "reason": None, "root": str(root),
            "invocations": rows, "invocation_count": len(rows), "status_counts": dict(statuses),
            "invocation_elapsed_ns": sum(row["elapsed_ns"] for row in rows),
            "cumulative_active_ns": max(row["cumulative_active_ns"] for row in rows),
            "reviewer_waiting_ns": None,
            "all_cleanup_verified": all(row["cleanup_verified"] for row in rows),
            "scientific_acceptance_asserted": False,
            "scope": "ALL_LIFECYCLE_INVOCATIONS_OPERATIONAL_ONLY",
            "counter_scope": "Invocation wall time excludes reviewer waiting between invocations. "
                "Cumulative active time is the highest retained ledger value, never a sum of ledger snapshots. "
                "Concurrent invocation wall times may overlap. Reviewer waiting is not measured. "
                "Raw OS final job CPU and commitment high-water are distinct from sampled maxima. "
                "Job CPU includes descendants and is never added to caller or per-process CPU. "
                "Code bindings identify retained execution, not a scientific correctness claim."}
