"""Own one nested numerical stage and retain only typed operational evidence."""
from __future__ import annotations

import builtins
from contextlib import ExitStack
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import re
import signal
import subprocess
import sys
import threading
import time

from resource_limits_v1 import WindowsJob
from scripts.whole_source.storage import guarded_open


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHANNELS = ('stdout', 'stderr')
_READY = 'T081_READY '
_EVENT = 'T081_EVENT '
_DIAGNOSTIC = 'T081_DIAGNOSTIC '
_KINDS = frozenset(('source', 'audit', 'exact', 'fixture'))
_PHASES = frozenset((
    'owned_tasks', 'residual_matrices', 'combined_square', 'kernel_step', 'source', 'frozen_inputs',
    'replay_declaration', 'residual_kernel', 'validate_model_allowance', 'validate_weights',
    'residual_outputs', 'residual_blocks', 'arithmetic_blocks', 'complete_arithmetic_squared',
    'frequency_kernels', 'reconstruct', 'check_matrix', 'arithmetic',
))
_UNITS = frozenset(('bounded task', 'modes', 'signed_windows', 'translation_cells',
                    'frequency_anchors', 'entries', 'prime_powers', 'parities'))
_WORK_KINDS = _KINDS | {'A_model', 'weighted_head', 'weighted_complete_tail'}
_MEASURES = (
    'active_process_count', 'aggregate_rss_bytes', 'current_committed_bytes', 'peak_committed_bytes',
    'cpu_seconds', 'memory_limit_bytes', 'cpu_budget', 'cpu_rate_per_10000', 'owned_cpu_rate_units',
    'owned_cpu_rate_denominator',
)
_MEASURE_LABELS = {
    'memory_accounting': ('JobObjectMemoryUsageInformation', 'unavailable'),
    'peak_counter_scope': ('raw OS high-water; denied allocation demand may be counted before rollback',),
    'cpu_rate_reference': ('parent job if rate-controlled, otherwise system',),
}


def _file_sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _write(stream, value, *, indent=None):
    raw = (json.dumps(value, sort_keys=True, indent=indent, allow_nan=False) + '\n').encode('utf-8')
    if stream.write(raw) != len(raw):
        raise OSError('short stage evidence write')


def _error_record(value):
    kind = value.get('type')
    if type(kind) is not str:
        return None
    exception_class = getattr(builtins, kind, None)
    if (kind not in ('ContractError', 'StageError') and
            not (isinstance(exception_class, type) and issubclass(exception_class, BaseException))):
        return None
    error = {'type': kind}
    for key in ('errno', 'winerror'):
        code = value.get(key)
        if type(code) is int and -(1 << 31) <= code < 1 << 32:
            error[key] = code
    return error


def _safe_error(exception):
    return _error_record({'type': type(exception).__name__,
                          'errno': getattr(exception, 'errno', None),
                          'winerror': getattr(exception, 'winerror', None)}) or {'type': 'StageError'}


def _object(line):
    try:
        value = json.loads(line)
    except (ValueError, RecursionError):
        return None
    return value if type(value) is dict else None


def _log_record(channel, line):
    prefix = _EVENT if channel == 'stdout' else _DIAGNOSTIC
    if not line.startswith(prefix):
        return None
    raw = _object(line[len(prefix):])
    if raw is None:
        return None
    if channel == 'stderr':
        error = _error_record(raw)
        return None if error is None else {'event': 'diagnostic', **error}

    name = raw.get('event')
    if name not in ('program_started', 'program_finished', 'phase_started', 'phase_finished', 'work'):
        return None
    event = {'event': name}
    for key, allowed in (('phase', _PHASES), ('unit', _UNITS), ('kind', _WORK_KINDS)):
        value = raw.get(key)
        if type(value) is str and value in allowed:
            event[key] = value
    if name in ('work', 'phase_started', 'phase_finished') and 'phase' not in event:
        return None
    for key in ('elapsed_seconds', 'wall_seconds', 'cpu_seconds'):
        value = raw.get(key)
        if type(value) in (int, float) and 0 <= value <= 10**12 and math.isfinite(value):
            event[key] = value
    for key in ('depth', 'threads', 'parity', 'completed', 'total', 'prime_power', 'exit_code'):
        value = raw.get(key)
        if type(value) is int and -(1 << 31) <= value < 1 << 32:
            event[key] = value
    if name == 'work' and not 0 <= event.get('completed', -1) <= event.get('total', -1):
        return None
    return event


def _safe_metrics(raw):
    result = {}
    for key in _MEASURES:
        if key not in raw:
            continue
        value = raw[key]
        if value is None or type(value) is int or type(value) is float and math.isfinite(value):
            result[key] = value
    pids = raw.get('active_process_ids')
    if 'active_process_ids' in raw:
        result['active_process_ids'] = pids if type(pids) is list and all(
            type(pid) is int and 0 < pid < 1 << 32 for pid in pids) else None
    for key, allowed in _MEASURE_LABELS.items():
        if raw.get(key) in allowed:
            result[key] = raw[key]
    if 'diagnostics' in raw:
        diagnostics = raw['diagnostics']
        result['diagnostic_count'] = len(diagnostics) if type(diagnostics) in (list, tuple) else 0
    return result


def _posix_metrics(group):
    rss, pids = 0, []
    page_size = os.sysconf('SC_PAGE_SIZE')
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            text = (entry / 'stat').read_text()
            fields = text[text.rfind(')') + 2:].split()
            if int(fields[2]) == group and fields[0] != 'Z':
                pids.append(int(entry.name))
                rss += int(fields[21]) * page_size
        except (OSError, ValueError, IndexError):
            continue
    return {'active_process_ids': pids, 'active_process_count': len(pids), 'aggregate_rss_bytes': rss}


def _stop_owned(process, job):
    if job is not None:
        job.terminate()
    elif os.name == 'posix':
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def _close_pipe(pipe):
    close = getattr(pipe, 'close', None)
    if close is not None:
        close()


class Execution:
    """Stage backend; WorkloadExecution owns the attempt lock, writer and budget."""

    def __init__(self, output, budget, *, root=ROOT, worker=HERE / 'stage_worker_v3.py'):
        self.output, self.root, self.worker = (Path(path).resolve() for path in (output, root, worker))
        self.budget = budget
        self.receipts = []
        self.lock = self.writer = None
        self.cancelled = threading.Event()

    def cancel(self):
        self.cancelled.set()

    def run(self, name, program, arguments, *, kind, stage_sha256, environment=None, expected_codes=(0,)):
        if type(name) is not str or re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', name) is None:
            raise ValueError('invalid stage name')
        if type(stage_sha256) is not str or re.fullmatch(r'[0-9a-f]{64}', stage_sha256) is None:
            raise ValueError('invalid stage digest')
        if kind not in _KINDS:
            raise ValueError('invalid stage kind')
        folder = self.output / name
        folder.mkdir()
        program = Path(program).resolve()
        program_sha = _file_sha(program)
        profile = folder / 'profile.json'
        command = [sys.executable, '-B', str(self.worker), '--program', str(program),
                   '--program-sha256', program_sha, '--config', str(self.config),
                   '--config-sha256', self.config_sha, '--profile', str(profile),
                   '--kind', kind, '--', *map(str, arguments)]
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                    'NUMEXPR_NUM_THREADS', 'FLINT_NUM_THREADS'):
            env[key] = '1'
        if environment:
            env.update(environment)

        messages = queue.Queue()  # WorkloadExecution replaces this with its bounded transport.
        readers, reader_errors = {}, {}
        process = job = None
        started = time.monotonic()
        metrics, peak, cleanup, error, profile_sha = {}, 0, False, None, None
        history = {}
        log_paths = {channel: folder / (channel + '.jsonl') for channel in CHANNELS}

        def read(channel, stream):
            try:
                for line in stream:
                    messages.put((channel, line))
            except Exception as exc:
                reader_errors[channel] = exc
            finally:
                try:
                    _close_pipe(stream)
                except Exception as exc:
                    reader_errors.setdefault(channel, exc)
                messages.put((channel, None))

        def capture(channel, line):
            record = _log_record(channel, line)
            if record is not None:
                _write(logs[channel], record)
                logs[channel].flush()
            return record

        def sample(*, enforce=False):
            nonlocal metrics, peak
            raw = job.usage() if job is not None else _posix_metrics(process.pid)
            metrics = _safe_metrics(raw)
            if job is not None:
                peak = max(peak, raw['peak_committed_bytes'])
            else:
                rss = raw['aggregate_rss_bytes']
                peak = max(peak, rss)
                if enforce and rss > self.budget['memory_budget_bytes']:
                    raise MemoryError('owned stage aggregate RSS exceeded memory budget')
            return metrics.get('active_process_count')

        def check_cancelled():
            if self.cancelled.is_set():
                raise KeyboardInterrupt('owned execution cancelled')

        with ExitStack() as stack:
            logs = {channel: stack.enter_context(guarded_open(path)) for channel, path in log_paths.items()}
            try:
                self.writer.event('STAGE_STARTED', stage=name, stage_sha256=stage_sha256,
                                  program_sha256=program_sha)
                self.writer.update(workflow_state='RUNNING', current_operation={
                    'stage': name, 'phase': 'initializing', 'budget': self.budget,
                })
                check_cancelled()
                process = subprocess.Popen(command, cwd=self.root, env=env, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                           encoding='utf-8', errors='replace', start_new_session=os.name == 'posix')
                if os.name == 'nt':
                    job = WindowsJob(self.budget['memory_budget_bytes'], self.budget['cpu_budget'])
                    job.attach(process)
                for channel in CHANNELS:
                    reader = threading.Thread(target=read, args=(channel, getattr(process, channel)), daemon=True)
                    reader.start()
                    readers[channel] = reader

                deadline = time.monotonic() + 15
                completed = set()
                while True:
                    check_cancelled()
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError('worker READY deadline exceeded')
                    try:
                        channel, line = messages.get(timeout=min(.5, remaining))
                    except queue.Empty:
                        continue
                    if line is None:
                        if channel in reader_errors:
                            raise reader_errors[channel]
                        if channel == 'stdout':
                            raise RuntimeError('worker exited before READY')
                        completed.add(channel)
                    elif channel == 'stdout' and line.startswith(_READY):
                        ready = _object(line[len(_READY):])
                        pid = ready.get('pid') if ready is not None else None
                        if (type(pid) is not int or not 0 < pid < 1 << 32 or
                                ready.get('config_sha256') != self.config_sha or
                                (os.name == 'posix' and pid != process.pid)):
                            raise ValueError('worker READY identity mismatch')
                        if job is not None:
                            job.attach_worker_pid(pid)
                        break
                    else:
                        capture(channel, line)
                check_cancelled()
                process.stdin.write('GO\n')
                process.stdin.flush()
                process.stdin.close()
                operation = {'stage': name, 'phase': 'program', 'budget': self.budget}
                next_sample = 0.0
                drain_deadline = None
                while process.poll() is None or len(completed) < len(CHANNELS):
                    check_cancelled()
                    if process.poll() is not None:
                        if drain_deadline is None:
                            # Descendants can keep inherited pipes open after the root exits.
                            if sample(enforce=True) != 0:
                                _stop_owned(process, job)
                            drain_deadline = time.monotonic() + 10
                        elif time.monotonic() >= drain_deadline:
                            raise TimeoutError('owned stage pipes did not reach EOF')
                    try:
                        channel, line = messages.get(timeout=.5)
                    except queue.Empty:
                        channel, line = None, None
                    if channel is not None:
                        if line is None:
                            completed.add(channel)
                            if channel in reader_errors:
                                raise reader_errors[channel]
                        else:
                            event = capture(channel, line)
                            if event is not None and channel == 'stdout':
                                self.writer.event('STAGE_PROGRESS', stage=name, detail=event)
                                operation = {'stage': name, **event, 'budget': self.budget,
                                             'remaining_estimate_seconds': None}
                                if event['event'] == 'work':
                                    key = tuple(event.get(k) for k in ('phase', 'parity', 'kind', 'unit', 'total'))
                                    old, now, done = history.get(key), time.monotonic(), event['completed']
                                    if old and done > old[0]:
                                        operation['remaining_estimate_seconds'] = (
                                            (now - old[1]) / (done - old[0]) * (event['total'] - done)
                                        )
                                        operation['estimate_basis'] = 'last comparable observed work-unit interval, not wall-time percentage'
                                    history[key] = (done, now)
                                print(name + ': ' + json.dumps(event, sort_keys=True), flush=True)
                    now = time.monotonic()
                    if now >= next_sample:
                        next_sample = now + 1
                        sample(enforce=True)
                        operation.update(stage_elapsed_seconds=now - started, resources=metrics)
                        self.writer.update(current_operation=operation)
                check_cancelled()
                process.wait()
                if process.returncode not in expected_codes:
                    raise RuntimeError('owned stage exited with an unexpected code; inspect retained diagnostics and profile')
            except BaseException as exc:
                error = exc
            finally:
                if process is not None:
                    try:
                        if process.stdin is not None and not process.stdin.closed:
                            process.stdin.close()
                        if error is not None:
                            _stop_owned(process, job)
                        elif drain_deadline is None and sample(enforce=True) != 0:
                            _stop_owned(process, job)
                        try:
                            process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=10)
                        if job is not None or os.name == 'posix':
                            deadline = time.monotonic() + 10
                            active = sample()
                            while active != 0 and time.monotonic() < deadline:
                                time.sleep(.05)
                                active = sample()
                            cleanup = type(active) is int and active == 0
                        else:
                            cleanup = process.poll() is not None
                    except BaseException as exc:
                        if error is None:
                            error = exc
                    try:
                        try:
                            if job is not None:
                                job.close()
                        finally:
                            if process.poll() is None:
                                process.kill()
                                process.wait(timeout=10)
                    except BaseException as exc:
                        if error is None:
                            error = exc
                    for channel in CHANNELS:
                        reader = readers.get(channel)
                        if reader is None:
                            _close_pipe(getattr(process, channel))
                        else:
                            reader.join(timeout=10)
                            if reader.is_alive() and error is None:
                                error = RuntimeError('owned stage pipe did not close')
                    # A pre-READY or failed worker may have emitted a typed diagnostic on stderr.
                    while True:
                        try:
                            channel, line = messages.get_nowait()
                        except queue.Empty:
                            break
                        if line is not None:
                            capture(channel, line)
                if error is None and not cleanup:
                    error = RuntimeError('owned numerical descendants remain after stage exit')
                if error is None and self.cancelled.is_set():
                    error = KeyboardInterrupt('owned execution cancelled')
                try:
                    if error is None:
                        with profile.open('rb') as stream:
                            raw = stream.read(65537)
                        if len(raw) > 65536:
                            profile_sha = _file_sha(profile)
                            raise ValueError('oversized owned stage profile')
                        profile_sha = hashlib.sha256(raw).hexdigest()
                        report = _object(raw)
                        if (report is None or report.get('format') != 't081-budgeted-stage-profile-v2'
                                or report.get('program_sha256') != program_sha or report.get('kind') != kind
                                or type(report.get('exit_code')) is not int or report['exit_code'] != process.returncode
                                or (process.returncode == 0 and report.get('error', False) is not None)):
                            raise ValueError('owned stage profile identity or outcome mismatch')
                        if _file_sha(program) != program_sha or _file_sha(self.config) != self.config_sha:
                            raise ValueError('owned stage program or configuration changed')
                    else:
                        profile_sha = _file_sha(profile)
                except FileNotFoundError:
                    if error is None:
                        error = RuntimeError('owned stage profile, program or configuration is missing')
                except (OSError, ValueError) as exc:
                    if error is None:
                        error = exc
                stack.close()
                receipt = {
                    'format': 'whole-source-owned-stage-receipt-v3', 'stage': name,
                    'stage_sha256': stage_sha256, 'config_sha256': self.config_sha,
                    'program_sha256': program_sha, 'profile_sha256': profile_sha,
                    'exit_code': None if process is None else process.returncode,
                    'elapsed_seconds': time.monotonic() - started, 'budget': self.budget,
                    'last_metrics': metrics, 'peak_budgeted_memory_bytes': peak,
                    'memory_metric': 'job committed memory' if os.name == 'nt' else
                                     'monitored aggregate RSS plus per-process RLIMIT_AS',
                    'worker_cleanup_verified': cleanup, 'error': None if error is None else _safe_error(error),
                }
                receipt_path = folder / 'receipt.json'
                with guarded_open(receipt_path) as stream:
                    _write(stream, receipt, indent=2)
                self.receipts.append(receipt)
                self.writer.event('STAGE_FINISHED', stage=name, exit_code=receipt['exit_code'], cleanup_verified=cleanup)
                diagnostic = {'format': 'whole-source-owned-stage-diagnostics-v1',
                    'receipt_sha256': _file_sha(receipt_path),
                    'streams': {channel: {'size': path.stat().st_size, 'sha256': _file_sha(path)}
                                for channel, path in log_paths.items()}}
                with guarded_open(folder / 'diagnostics.json') as stream:
                    _write(stream, diagnostic, indent=2)
        if error is not None:
            raise error
        return receipt
