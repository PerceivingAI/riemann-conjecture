"""Compare selected phase-owned stages without asserting complete qualification."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
ORIGINAL = Path(__file__).with_name('compare-execution-v1.py')
# Frozen baseline/source/operand methods stay reproducible through their original file.
_inherited = runpy.run_path(str(ORIGINAL))


def require(value, message):
    if not value:
        raise ValueError(message)


def load(path):
    return json.loads(Path(path).read_bytes())


def binding(path):
    return _inherited['binding'](path)


def _optional_document(path):
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return None, None, 'MISSING'
    except OSError:
        return None, None, 'UNREADABLE'
    ref = {'path':str(path), 'sha256':hashlib.sha256(raw).hexdigest(), 'size':len(raw)}
    try:
        document = json.loads(raw)
    except ValueError:
        return None, ref, 'MALFORMED'
    if type(document) is not dict:
        return None, ref, 'MALFORMED'
    return document, ref, None


def _seconds(value):
    if type(value) not in (int, float) or value < 0:
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def owner_timing(attempt):
    """Observe optional terminal telemetry once, with same-byte provenance."""
    attempt = Path(attempt).resolve()
    status, ref, error = _optional_document(attempt/'.live/run-status.json')
    result = {'attempt':str(attempt), 'availability':'UNAVAILABLE', 'reason':None,
        'elapsed_seconds':None, 'snapshot':ref, 'identity':None, 'workflow_state':None}
    if error:
        result['reason'] = 'SNAPSHOT_'+error
        return result
    state = status.get('workflow_state')
    result['workflow_state'] = state if type(state) is str else None
    if status.get('format') != 'riemann-live-run-v1':
        result['reason'] = 'SNAPSHOT_INVALID_FORMAT'
    elif status.get('terminal') is not True or state not in ('RUN_COMPLETED','RUN_FAILED','RUN_INTERRUPTED'):
        result['reason'] = 'SNAPSHOT_NOT_TERMINAL'
    elif not _seconds(status.get('elapsed_seconds')):
        result['reason'] = 'SNAPSHOT_INVALID_COUNTER'
    else:
        identity, ref, error = _optional_document(attempt/'.live/run.json')
        result['identity'] = ref
        if error:
            result['reason'] = 'IDENTITY_'+error
        elif (identity.get('format') != 'riemann-run-identity-v1' or
              type(identity.get('pid')) is not int or identity['pid'] <= 0 or
              any(type(identity.get(key)) is not str or not identity[key]
                  for key in ('run_id','started_at_utc','driver','support'))):
            result['reason'] = 'IDENTITY_INVALID'
        elif (any(status.get(key) != identity[key] for key in ('run_id','pid','started_at_utc')) or
              type(status.get('pid')) is not int or
              status.get('command') != identity['driver'] or status.get('support') != identity['support']):
            result['reason'] = 'SNAPSHOT_IDENTITY_MISMATCH'
        else:
            result.update(availability='AVAILABLE', elapsed_seconds=status['elapsed_seconds'])
    return result


def resources(directory):
    from scripts.whole_source.retention import _verify_receipts
    directory = Path(directory).resolve()
    # No optional-telemetry exception handling encloses this critical verifier.
    verified = _verify_receipts(directory)
    groups = defaultdict(lambda: {'stages':0, 'stage_elapsed_seconds':0.0,
        'owned_cpu_seconds':0.0, 'cpu_counter_missing':0, 'peak_owned_committed_bytes':0,
        'peak_sampled_external_increment_bytes':0, 'attempts':set(),
        'configured_cpu_budgets':set(), 'configured_worker_budgets':set(),
        'configured_native_threads_per_worker':set(), 'max_concurrently_observed_workers':0})
    rows = []
    logical_passes = defaultdict(lambda: defaultdict(lambda: {
        'tasks':0, 'operand_read_passes':0, 'encoded_operand_bytes':0}))
    for record in verified:
        path = Path(record['directory'])/record['artifact']['path']
        receipt = load(path)
        attempt = path.parent.parent
        stage_path = attempt/(receipt['stage']+'-stage.json')
        stage = load(stage_path)
        relative = path.relative_to(directory)
        group = ('scalar-premises' if relative.parts[0] == 'prepare'
                 else _inherited['phase'](relative))
        summary = load(attempt/(receipt['stage']+'-resources.json'))
        observation = load(attempt/(receipt['stage']+'-pool-observation.json'))
        cpu = receipt['last_metrics'].get('cpu_seconds')
        values = groups[group]
        for operation, account in _inherited['source_operand_passes'](stage).items():
            for key, value in account.items():
                logical_passes[group][operation][key] += value
        values['stages'] += 1
        values['stage_elapsed_seconds'] += receipt['elapsed_seconds']
        if cpu is None:
            values['cpu_counter_missing'] += 1
        else:
            values['owned_cpu_seconds'] += cpu
        values['peak_owned_committed_bytes'] = max(values['peak_owned_committed_bytes'], receipt['peak_budgeted_memory_bytes'])
        values['peak_sampled_external_increment_bytes'] = max(
            values['peak_sampled_external_increment_bytes'], summary['sampled_external_increment_bytes'])
        values['attempts'].add(attempt)
        values['configured_cpu_budgets'].add(stage['plan']['cpus'])
        values['configured_worker_budgets'].add(stage['plan']['workers'])
        values['configured_native_threads_per_worker'].add(stage['plan']['threads'])
        values['max_concurrently_observed_workers'] = max(
            values['max_concurrently_observed_workers'], observation['concurrent_workers_observed'])
        result_dir = Path(stage['result_dir'])
        rows.append({'phase':group, 'receipt':binding(path), 'stage_descriptor':binding(stage_path),
            'completion':binding(result_dir/'complete.json'), 'completed_results':binding(result_dir/'completed.jsonl'),
            'elapsed_seconds':receipt['elapsed_seconds'], 'aggregate_owned_cpu_seconds':cpu,
            'peak_owned_committed_bytes':receipt['peak_budgeted_memory_bytes'],
            'sampled_external_increment_bytes':summary['sampled_external_increment_bytes'],
            'cleanup_verified':receipt['worker_cleanup_verified']})
    output = {}
    for name, values in sorted(groups.items()):
        attempts = sorted(values.pop('attempts'))
        timings = [owner_timing(attempt) for attempt in attempts]
        available = all(timing['availability']=='AVAILABLE' for timing in timings)
        owner_seconds = sum(timing['elapsed_seconds'] for timing in timings) if available else None
        reason = None if available else 'ONE_OR_MORE_OWNER_TIMINGS_UNAVAILABLE'
        if available and not _seconds(owner_seconds):
            available, owner_seconds, reason = False, None, 'OWNER_TOTAL_NOT_FINITE'
        values.update(owner_timings=timings, collection_owners=len(attempts),
            collection_owner_elapsed_seconds=owner_seconds, collection_owner_elapsed_available=available,
            collection_owner_elapsed_unavailable_reason=reason)
        ratio, ratio_reason = None, None
        if not available:
            ratio_reason = 'OWNER_TIMING_UNAVAILABLE'
        elif owner_seconds == 0:
            ratio_reason = 'ZERO_OWNER_DURATION'
        elif values['cpu_counter_missing']:
            ratio_reason = 'CPU_COUNTER_MISSING'
        else:
            ratio = values['owned_cpu_seconds']/owner_seconds
            if not _seconds(ratio):
                ratio, ratio_reason = None, 'CPU_OWNER_RATIO_NOT_FINITE'
        values['aggregate_cpu_per_owner_wall'] = ratio
        values['aggregate_cpu_per_owner_wall_unavailable_reason'] = ratio_reason
        for key in ('configured_cpu_budgets','configured_worker_budgets','configured_native_threads_per_worker'):
            values[key] = sorted(values[key])
        output[name] = values
    return {'phases':output, 'stages':rows, 'owned_receipts_verified':len(verified),
        'completion':{'scope':'SELECTED_SUCCESSFUL_OWNED_STAGES_ONLY',
            'whole_source_completion_asserted':False, 'whole_pipeline_completion_asserted':False,
            'scientific_acceptance_asserted':False},
        'source_logical_operand_passes':{name:dict(operations) for name, operations in logical_passes.items()},
        'source_read_scope':'Derived from executed task references and callback read loops; excludes metadata, proposal/exact operand passes, writes and physical OS/device traffic.',
        'all_owned_cleanup_verified':all(row['cleanup_verified'] for row in rows),
        'counter_scope':'Owned job CPU includes descendants. Optional owner timing is advisory monotonic writer lifetime, including inter-stage work and possibly failed noncontributing work; it excludes final caller read-through and unowned CPU. It is not completion authority.'}


def main(argv=None):
    from scripts.whole_source.retention import _check_sealed_output
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--baseline-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--compare-source', action='store_true')
    args = parser.parse_args(argv)
    run, old, output = args.run_dir.resolve(strict=True), args.baseline_dir.resolve(strict=True), args.output.resolve()
    require(not output.exists(), 'report output must be fresh')
    require(not output.is_relative_to(run) and not output.is_relative_to(old), 'report output must be outside input trees')
    _check_sealed_output(output.parent)
    report = {'format':'whole-source-retained-execution-comparison-v3',
        'created_utc':datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),
        'status':'OPERATIONAL_AND_DIAGNOSTIC_COMPARISON_ONLY', 'program':binding(Path(__file__)),
        'inherited_program':binding(ORIGINAL),
        'new':resources(run), 'baseline':_inherited['baseline'](old),
        'disk':{'new':_inherited['footprint'](run), 'baseline':_inherited['footprint'](old)},
        'limits':['Verified selected stages do not establish whole-source/pipeline completion or scientific acceptance.',
            'Live status is optional advisory timing only; missing owner totals and ratios remain null, never partial or substituted.',
            'No matched full-pipeline speedup: baseline reuses a proposal and stage/control/replay boundaries differ.',
            'Native stage sums exclude inter-stage owner work; owner wall excludes final caller read-through.',
            'Unowned supervisor CPU is not captured by job CPU counters.',
            'Disk census is retained logical file bytes, not transient write traffic or physical device I/O; OS I/O counters were not retained.',
            'One execution per implementation is not a statistical scaling study.'],
        'production_admission':False}
    if (run/'elapsed.json').is_file():
        report['new']['coordinator_elapsed'] = load(run/'elapsed.json')
    if args.compare_source:
        report['source_comparison'] = _inherited['compare_sources'](run, old)
    _check_sealed_output(output.parent)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(report, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'report':str(output), 'verified_owned_stages':report['new']['owned_receipts_verified'],
        'all_owned_cleanup_verified':report['new']['all_owned_cleanup_verified'], 'scope':report['status']}, sort_keys=True))


if __name__ == '__main__':
    main()
