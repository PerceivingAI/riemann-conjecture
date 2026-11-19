"""Own one budgeted numerical stage and retain only structured supervision records."""
from __future__ import annotations

from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import signal
import subprocess
import sys
import threading
import time

from .run_observability import OutputDirectoryLock, RunStatusWriter, write_run_identity
from .t081_resource_records import read_stream, safe_budget, safe_error, safe_event, write_event


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUNDLE = ROOT / "computations/2026-10-28T034134Z-t081-resource-execution"
sys.path.insert(0, str(BUNDLE))
from execution_supervisor_v1 import _posix_metrics, encode, sha
from resource_limits_v1 import WindowsJob


DRIVER = "t081-resource-execution-v2"
CHANNELS = ("stdout", "stderr")
READY = "T081_READY "
PREFIX = {"stdout": "T081_EVENT ", "stderr": "T081_DIAGNOSTIC "}
PROGRAMS = {
    "build-whole-source-v4.py": "source",
    "verify-whole-source-v3.py": "audit",
    "verify-whole-sign-v1.py": "exact",
    "negative-controls-v2.py": "fixture",
    "accept-retained-v1.py": "exact",
}


def ready_pid(messages, config_sha):
    deadline = time.monotonic() + 15
    while (remaining := deadline - time.monotonic()) > 0:
        try:
            channel, line = messages.get(timeout=remaining)
        except queue.Empty:
            break
        if line is None:
            raise RuntimeError("worker exited before READY")
        if channel == "stdout" and line.startswith(READY):
            ready = json.loads(line[len(READY):])
            if (type(ready) is not dict or ready.get("config_sha256") != config_sha
                    or type(ready.get("pid")) is not int or not 0 < ready["pid"] < 2**32):
                raise ValueError("worker READY identity mismatch")
            return ready["pid"]
    raise TimeoutError("worker READY deadline exceeded")


def stream_descriptor(path, base):
    with path.open("rb") as stream:
        return {"path": path.relative_to(base).as_posix(),
                "sha256": hashlib.file_digest(stream, "sha256").hexdigest()}

def job_metrics(job):
    metrics = job.usage()
    metrics["diagnostic_count"] = len(metrics.pop("diagnostics", ()))
    return metrics



class Execution:
    def __init__(self, output, budget, *, root=ROOT, worker=HERE / "t081_resource_worker.py",
                 identity=(DRIVER, "81/100", (826,))):
        self.output = Path(output).resolve()
        self.root = Path(root).resolve()
        self.budget = safe_budget(budget)
        self.worker = Path(worker).resolve()
        self.driver, self.support, self.dimensions = identity
        self.receipts = []
        self.lock = None
        self.writer = None
        self.cancelled = threading.Event()

    def cancel(self):
        self.cancelled.set()

    def __enter__(self):
        self.lock = OutputDirectoryLock.acquire(self.output, command=self.driver, support=self.support)
        try:
            commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                    capture_output=True, text=True, check=True).stdout.strip()
            if re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit) is None:
                raise ValueError("invalid checkout identity")
            write_run_identity(self.lock, driver_version=self.driver, dimensions=list(self.dimensions),
                               git_commit=commit, git_dirty=True)
            self.writer = RunStatusWriter.start(self.output, command=self.driver, support=self.support,
                                                output_lock=self.lock)
            self.config = self.output / "execution-budget.json"
            config = encode(self.budget)
            with self.config.open("xb") as stream:
                stream.write(config)
            self.config_sha = sha(config)
            self.writer.event("RESOURCE_BUDGET", budget=self.budget)
            return self
        except BaseException:
            self.lock.release()
            raise

    def __exit__(self, kind, error, traceback):
        try:
            if error is not None:
                terminal = "RUN_INTERRUPTED" if kind is KeyboardInterrupt else "RUN_FAILED"
                self.writer.record_failure(terminal, RuntimeError(json.dumps(safe_error(error), sort_keys=True)))
            else:
                self.writer.update(workflow_state="RUN_COMPLETED", current_operation=None, terminal=True)
        finally:
            self.lock.release()

    def run(self, name, program, arguments, *, kind, environment=None, expected_codes=(0,)):
        if type(name) is not str or re.fullmatch(r"[a-z][a-z0-9-]{0,63}", name) is None:
            raise ValueError("invalid stage name")
        if kind not in ("source", "audit", "exact", "fixture"):
            raise ValueError("invalid stage kind")
        folder = self.output / name
        folder.mkdir()
        program = Path(program).resolve()
        program_sha = sha(program.read_bytes())
        program_info = {"name": program.name if PROGRAMS.get(program.name) == kind else None, "kind": kind}
        command = [sys.executable, "-B", str(self.worker), "--program", str(program),
                   "--program-sha256", program_sha, "--config", str(self.config),
                   "--config-sha256", self.config_sha, "--profile", str(folder / "profile.json"),
                   "--kind", kind, "--", *map(str, arguments)]
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "FLINT_NUM_THREADS"):
            env[key] = "1"
        if environment:
            env.update(environment)
        messages = queue.Queue(maxsize=64)
        stop = threading.Event()
        readers = []
        job = process = None
        started = time.monotonic()
        metrics, peak, cleanup, error = {}, 0, False, None
        history = {}
        self.writer.event("STAGE_STARTED", stage=name, program=program_info, program_sha256=program_sha)
        self.writer.update(workflow_state="RUNNING",
                           current_operation={"stage": name, "phase": "initializing", "budget": self.budget})
        log_paths = {channel: folder / (channel + ".jsonl") for channel in CHANNELS}
        with ExitStack() as stack:
            logs = {channel: stack.enter_context(path.open("x", encoding="utf-8", newline="\n"))
                    for channel, path in log_paths.items()}
            try:
                process = subprocess.Popen(command, cwd=self.root, env=env, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           start_new_session=os.name == "posix")
                if os.name == "nt":
                    job = WindowsJob(self.budget["memory_budget_bytes"], self.budget["cpu_budget"])
                    job.attach(process)
                for channel in CHANNELS:
                    reader = threading.Thread(target=read_stream,
                                              args=(channel, getattr(process, channel), messages, stop), daemon=True)
                    reader.start()
                    readers.append(reader)
                # The actual interpreter can differ from Popen.pid on Windows venvs.
                worker_pid = ready_pid(messages, self.config_sha)
                if job:
                    job.attach_worker_pid(worker_pid)
                process.stdin.write(b"GO\n")
                process.stdin.flush()
                process.stdin.close()
                completed_streams = set()
                operation = {"stage": name, "phase": "program", "budget": self.budget}
                next_sample = 0.0
                while process.poll() is None or len(completed_streams) < len(CHANNELS):
                    if self.cancelled.is_set():
                        raise KeyboardInterrupt("owned execution cancelled")
                    # Reap descendants before waiting on inherited stdout/stderr EOF.
                    if process.poll() is not None:
                        if job and job.usage()["active_process_count"]:
                            job.terminate()
                        elif os.name == "posix" and _posix_metrics(process.pid)["active_process_ids"]:
                            os.killpg(process.pid, signal.SIGKILL)
                    try:
                        channel, line = messages.get(timeout=.5)
                    except queue.Empty:
                        channel, line = None, None
                    if channel is not None:
                        if line is None:
                            completed_streams.add(channel)
                        elif line.startswith(PREFIX[channel]) and (event := safe_event(line)) is not None:
                            write_event(logs[channel], event)
                            if channel == "stdout":
                                self.writer.event("STAGE_PROGRESS", stage=name, detail=event)
                                operation = {"stage": name, **event, "budget": self.budget,
                                             "remaining_estimate_seconds": None}
                                if (event["event"] == "work" and "completed" in event and "total" in event
                                        and event.get("parity") in (None, 0, 1)):
                                    key = tuple(event.get(k) for k in ("phase", "parity", "kind", "unit"))
                                    old, now, done = history.get(key), time.monotonic(), event["completed"]
                                    if old and old[0] < done <= event["total"]:
                                        operation["remaining_estimate_seconds"] = (
                                            (now - old[1]) / (done - old[0]) * (event["total"] - done)
                                        )
                                        operation["estimate_basis"] = "last comparable observed work-unit interval, not wall-time percentage"
                                    history[key] = (done, now)
                                print(name + ": " + json.dumps(event, sort_keys=True), flush=True)
                    now = time.monotonic()
                    if now >= next_sample:
                        next_sample = now + 1
                        if job:
                            metrics = job_metrics(job)
                            peak = max(peak, metrics["peak_committed_bytes"])
                        else:
                            # RLIMIT_AS is inherited; the aggregate is monitored separately.
                            metrics = _posix_metrics(process.pid)
                            rss = metrics["aggregate_rss_bytes"]
                            peak = max(peak, rss)
                            if rss > self.budget["memory_budget_bytes"]:
                                raise MemoryError("owned stage aggregate RSS exceeded memory budget")
                        operation.update(stage_elapsed_seconds=now - started, resources=metrics)
                        self.writer.update(current_operation=operation)
                process.wait()
                if job:
                    metrics = job_metrics(job)
                    peak = max(peak, metrics["peak_committed_bytes"])
                    if metrics["active_process_count"]:
                        job.terminate()
                        deadline = time.monotonic() + 10
                        while job.usage()["active_process_count"] and time.monotonic() < deadline:
                            time.sleep(.05)
                    cleanup = job.usage()["active_process_count"] == 0
                else:
                    metrics = _posix_metrics(process.pid)
                    if metrics["active_process_ids"]:
                        os.killpg(process.pid, signal.SIGKILL)
                        deadline = time.monotonic() + 10
                        while _posix_metrics(process.pid)["active_process_ids"] and time.monotonic() < deadline:
                            time.sleep(.05)
                    cleanup = not _posix_metrics(process.pid)["active_process_ids"]
                if not cleanup:
                    raise RuntimeError("owned numerical descendants remain after stage exit")
                if process.returncode not in expected_codes:
                    raise RuntimeError(f"{name} exited {process.returncode}; inspect retained diagnostics and profile")
                if sha(program.read_bytes()) != program_sha:
                    raise ValueError("numerical program changed during stage")
            except BaseException as exception:
                error = safe_error(exception)
                stop.set()
                if process is not None:
                    if process.stdin is not None and not process.stdin.closed:
                        process.stdin.close()
                    if job:
                        job.terminate()
                    elif os.name == "posix" and _posix_metrics(process.pid)["active_process_ids"]:
                        os.killpg(process.pid, signal.SIGKILL)
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    if job:
                        deadline = time.monotonic() + 10
                        while job.usage()["active_process_count"] and time.monotonic() < deadline:
                            time.sleep(.05)
                        cleanup = job.usage()["active_process_count"] == 0
                    elif os.name == "posix":
                        cleanup = not _posix_metrics(process.pid)["active_process_ids"]
                    else:
                        cleanup = process.poll() is not None
                raise
            finally:
                stop.set()
                if job:
                    job.close()
                if process is not None and process.poll() is None:
                    process.kill()
                    process.wait()
                for reader in readers:
                    reader.join()
                if process is not None:
                    for channel in CHANNELS:
                        getattr(process, channel).close()
                stack.close()
                receipt = {
                    "format": "t081-owned-stage-receipt-v2", "stage": name, "program": program_info,
                    "exit_code": None if process is None else process.returncode,
                    "elapsed_seconds": time.monotonic() - started, "budget": self.budget,
                    "last_metrics": metrics, "peak_budgeted_memory_bytes": peak,
                    "memory_metric": "job committed memory" if os.name == "nt" else
                                     "monitored aggregate RSS plus per-process RLIMIT_AS",
                    "worker_cleanup_verified": cleanup, "error": error,
                    "program_sha256": program_sha, "config_sha256": self.config_sha,
                    "logs": {channel: stream_descriptor(path, self.output) for channel, path in log_paths.items()},
                }
                with (folder / "receipt.json").open("xb") as stream:
                    stream.write(encode(receipt))
                self.receipts.append(receipt)
                self.writer.event("STAGE_FINISHED", stage=name, exit_code=receipt["exit_code"], cleanup_verified=cleanup)
        return receipt
