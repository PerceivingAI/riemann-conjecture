"""Safe, versioned records for maintained T81 resource supervision."""
from __future__ import annotations

import hashlib
import json
import math
import queue
import re


_EVENT = 'T081_EVENT '
_DIAGNOSTIC = 'T081_DIAGNOSTIC '
_READY = 'T081_READY '
_MAX_LINE = 4096
_STAGE_KINDS = {'source', 'audit', 'exact', 'fixture'}
_PHASES = {
    'residual_matrices', 'combined_square', 'kernel_step', 'source', 'frozen_inputs',
    'replay_declaration', 'residual_kernel', 'validate_model_allowance', 'validate_weights',
    'residual_outputs', 'residual_blocks', 'arithmetic_blocks', 'complete_arithmetic_squared',
    'frequency_kernels', 'reconstruct', 'check_matrix', 'arithmetic',
}
_UNITS = {'modes', 'signed_windows', 'translation_cells', 'frequency_anchors', 'entries', 'prime_powers', 'parities'}
_ERRORS = {
    'ArithmeticError', 'AssertionError', 'AttributeError', 'FileExistsError', 'FileNotFoundError',
    'ImportError', 'KeyError', 'KeyboardInterrupt', 'MemoryError', 'ModuleNotFoundError', 'OSError',
    'OverflowError', 'PermissionError', 'RuntimeError', 'SystemExit', 'TimeoutError', 'TypeError',
    'ValueError', 'ZeroDivisionError', 'StageError',
}


def safe_error(error: BaseException) -> dict:
    kind = type(error).__name__
    record = {'type': kind if kind in _ERRORS else 'StageError'}
    if isinstance(error, OSError) and type(error.errno) is int:
        record['errno'] = error.errno
    if isinstance(error, ValueError) and error.args == ('singular full congruence',):
        record['reason'] = 'singular_full_congruence'
    return record


def _number(value):
    return type(value) in (int, float) and (type(value) is int or math.isfinite(value)) and 0 <= value <= 10**12


def safe_event(line: str) -> dict | None:
    """Allow only typed progress and diagnostic fields from the child pipe."""
    if line.startswith(_EVENT):
        prefix = _EVENT
    elif line.startswith(_DIAGNOSTIC):
        prefix = _DIAGNOSTIC
    else:
        return None
    try:
        raw = json.loads(line[len(prefix):])
    except (ValueError, RecursionError):
        return None
    if type(raw) is not dict:
        return None
    if prefix == _DIAGNOSTIC:
        kind = raw.get('type')
        if type(kind) is not str or kind not in _ERRORS:
            return None
        event = {'event': 'diagnostic', 'type': kind}
        if type(raw.get('errno')) is int:
            event['errno'] = raw['errno']
        if kind == 'ValueError' and raw.get('reason') == 'singular_full_congruence':
            event['reason'] = 'singular_full_congruence'
        return event
    name = raw.get('event')
    if name not in ('program_started', 'program_finished', 'phase_started', 'phase_finished', 'work'):
        return None
    event = {'event': name}
    labels = {'phase': _PHASES, 'unit': _UNITS,
              'kind': _STAGE_KINDS | {'A_model', 'weighted_head', 'weighted_complete_tail'}}
    for key, allowed in labels.items():
        value = raw.get(key)
        if type(value) is str and value in allowed:
            event[key] = value
    if name in ('work', 'phase_started', 'phase_finished') and 'phase' not in event:
        return None
    for key in ('elapsed_seconds', 'wall_seconds', 'cpu_seconds'):
        if _number(raw.get(key)):
            event[key] = raw[key]
    for key in ('depth', 'threads', 'parity', 'completed', 'total', 'prime_power', 'exit_code'):
        if type(raw.get(key)) is int and abs(raw[key]) <= 2**31:
            event[key] = raw[key]
    return event


def read_stream(channel, stream, messages, stop=None):
    """Drain pipes without buffering unbounded lines or forwarding unstructured text."""
    def send(value):
        while stop is None or not stop.is_set():
            try:
                messages.put((channel, value), timeout=0.1)
                return True
            except queue.Full:
                continue
        return False

    try:
        overlong = False
        while stop is None or not stop.is_set():
            chunk = stream.readline(_MAX_LINE + 1)
            if not chunk:
                break
            newline = chunk.endswith(b'\n' if isinstance(chunk, bytes) else '\n')
            if overlong or len(chunk) > _MAX_LINE:
                overlong = not newline
                continue
            if isinstance(chunk, bytes):
                chunk = chunk.decode('utf-8', errors='replace')
            if chunk.startswith((_EVENT, _DIAGNOSTIC, _READY)) and not send(chunk):
                break
    finally:
        send(None)


def write_event(stream, event):
    stream.write(json.dumps(event, sort_keys=True, allow_nan=False) + '\n')
    stream.flush()


def safe_budget(budget: dict) -> dict:
    """Retain applied limits and non-identifying detection facts, not discovery paths."""
    fields = ('cpu_budget', 'workers', 'native_threads', 'memory_budget_bytes',
              'reserve_bytes', 'required_bytes')
    result = {name: budget[name] for name in fields}
    if any(type(value) is not int or value < 0 for value in result.values()):
        raise ValueError('invalid applied resource budget')
    available = budget.get('available_memory_bytes')
    if type(available) is int:
        result['available_memory_bytes'] = available
    if type(budget.get('diagnostics')) is list:
        result['discovery_warning_count'] = len(budget['diagnostics'])
    elif type(budget.get('discovery_warning_count')) is int:
        result['discovery_warning_count'] = budget['discovery_warning_count']
    if type(budget.get('detection')) is dict:
        detection = budget['detection']
        result['detection'] = {key: detection[key] for key in (
            'logical_cpus', 'affinity_cpus', 'effective_cpu_budget', 'available_memory_bytes',
        ) if type(detection.get(key)) is int}
        result['detection'].update({key: detection[key] for key in (
            'cpu_detection_complete', 'memory_detection_complete',
        ) if type(detection.get(key)) is bool})
        quota = detection.get('quota_cpu_limit')
        if type(quota) is str and re.fullmatch(r'[0-9]+(?:/[1-9][0-9]*)?', quota):
            result['detection']['quota_cpu_limit'] = quota
    if type(budget.get('selection')) is dict:
        result['selection'] = {}
        for key in ('cpus', 'workers', 'threads', 'memory_mib', 'reserve_mib'):
            value = budget['selection'].get(key)
            if value in ('detected', '--'+key.replace('_', '-'), 'T081_'+key.upper()):
                result['selection'][key] = value
    return result


def verify_stage_receipt(folder, stage, budget):
    """Verify actual v2 receipt, applied budget, persisted stream bytes and profile."""
    def require(condition, message):
        if not condition:
            raise ValueError(message)

    name = stage['stage']
    require(type(name) is str and re.fullmatch(r'[a-z][a-z0-9-]{0,63}', name), 'invalid stage name')
    stage_dir = folder / name
    require(stage_dir.resolve().is_relative_to(folder.resolve()), 'stage path escapes run')
    receipt = json.loads((stage_dir/'receipt.json').read_bytes())
    require(receipt == stage and receipt.get('format') == 't081-owned-stage-receipt-v2'
            and receipt.get('worker_cleanup_verified') is True, 'stage receipt/cleanup mismatch')
    config = (folder/'execution-budget.json').read_bytes()
    require(receipt['config_sha256'] == hashlib.sha256(config).hexdigest(), 'stage used another budget')
    require(receipt['budget'] == budget == json.loads(config) == safe_budget(budget), 'stage budget changed')
    expected_exit = 1 if name == 'singular-fullspace-witness' else 0
    require(type(receipt['exit_code']) is int and receipt['exit_code'] == expected_exit
            and receipt.get('error') is None, 'stage exit outcome changed')
    require(set(receipt['logs']) == {'stdout', 'stderr'}, 'stage stream set changed')
    for channel, descriptor in receipt['logs'].items():
        path = stage_dir / (channel+'.jsonl')
        require(descriptor['path'] == f'{name}/{channel}.jsonl' and not path.is_symlink(), 'stage stream path changed')
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        require(digest == descriptor['sha256'], 'stage stream changed')
    profile = json.loads((stage_dir/'profile.json').read_bytes())
    require(profile.get('format') == 't081-budgeted-stage-profile-v2', 'stage profile format changed')
    require(profile['native_threads'] == budget['native_threads'], 'selected native threads were not applied')
    require(profile['program_sha256'] == receipt['program_sha256'], 'stage program fingerprint mismatch')
    require(profile['exit_code'] == expected_exit, 'profile exit outcome changed')
    if expected_exit:
        require(profile.get('error') == {'type': 'ValueError', 'reason': 'singular_full_congruence'},
                'singular witness did not reach exact nonsingularity rejection')
    return profile
