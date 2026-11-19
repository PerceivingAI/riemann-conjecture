"""Discovery and strict verification of owned scientific stage evidence."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from scripts.whole_source.contract import ArtifactRef, ContractError
from scripts.whole_source.artifacts import _raw
from scripts.whole_source.execution import ExecutionPlan, MIB, _bytes, _json, _resolve_stage


_FORMAT = 't081-owned-stage-receipt-v1'
_INLINE = 'whole-source-owned-stage-receipt-v2'
_CURRENT = 'whole-source-owned-stage-receipt-v3'
_FORMATS = (_FORMAT, _INLINE, _CURRENT)


def _require(condition, message):
    if not condition:
        raise ContractError(message)


def _hash_file(path):
    digest, size = hashlib.sha256(), 0
    with Path(path).open('rb') as stream:
        while value := stream.read(MIB):
            digest.update(value)
            size += len(value)
    return {'size': size, 'sha256': digest.hexdigest()}


def _record(path):
    return {'directory': str(path.parent),
            'artifact': asdict(ArtifactRef(path.name, **_hash_file(path)))}


def discover_receipts(directory):
    """Find recognized owned receipts, without requiring successful execution."""
    paths = sorted(Path(directory).resolve(strict=True).rglob('receipt.json'))
    return [path for path in paths if
            json.loads(_bytes(path)).get('format') in _FORMATS]


def _stage_binding(path, value):
    _require(value.get('format') in _FORMATS, 'unrecognized owned stage receipt format')
    attempt = path.parent.parent
    name = value['stage']
    _require(path.parent.name == name, 'receipt belongs to another stage')
    stage_path = attempt/(name+'-stage.json')
    if value['format'] == _FORMAT:
        argv = value['argv']
        _require(Path(argv[argv.index('--stage')+1]).resolve(strict=True) == stage_path,
                 'receipt does not bind this stage descriptor')
        expected = argv[argv.index('--stage-sha256')+1]
    else:
        _require('argv' not in value and stage_path.resolve(strict=True) == stage_path,
                 'foreign stage descriptor')
        expected = value['stage_sha256']
    raw = _bytes(stage_path)
    _require(hashlib.sha256(raw).hexdigest() == expected, 'receipt does not bind this stage descriptor')
    stage = _json(raw)
    if value['format'] != _FORMAT:
        _require(stage.get('format') == 'whole-source-task-stage-v3', 'incompatible stage descriptor')
    return stage_path, _resolve_stage(stage, stage_path)


def verify_stage(path):
    """Verify scientific authority and required cleanup; legacy logs stay pinned."""
    path = Path(path).resolve(strict=True)
    value = json.loads(_bytes(path))
    _require(value.get('format') in _FORMATS, 'unrecognized owned stage receipt format')
    _require(value['exit_code']==0 and value['error'] is None and
             value['worker_cleanup_verified'] is True and
             value['last_metrics']['active_process_count']==0,'failed/uncontained owned scientific stage')
    attempt = path.parent.parent
    current = value['format'] != _FORMAT
    def argument(flag, expected):
        if current:
            _require(expected.resolve(strict=True) == expected, 'foreign owned ' + flag[2:])
            return expected
        argv = value['argv']
        return Path(argv[argv.index(flag)+1]).resolve(strict=True)
    _, stage = _stage_binding(path, value)
    plan = ExecutionPlan.from_dict(stage['plan'])
    _require(stage['attempt_id']==attempt.name,'receipt attempt differs')
    program = argument('--program', attempt/'runtime/scripts/whole_source/execution.py')
    _require(program==attempt/'runtime/scripts/whole_source/execution.py' and
             _hash_file(program)['sha256']==value['program_sha256'],
             'receipt program differs from captured runtime')
    config_path = argument('--config', attempt/'execution-budget.json')
    _require(config_path==attempt/'execution-budget.json' and
             _hash_file(config_path)['sha256']==value['config_sha256'],'changed owned budget')
    if current:
        _require(_json(_bytes(config_path)) == value['budget'], 'receipt differs from owned budget')
    _raw(attempt/'runtime',plan.task_program,8*MIB)
    task_file = Path(stage['task_file'])
    _require(task_file.parent==attempt and _hash_file(task_file)['sha256']==stage['task_sha256'],
             'changed owned tasks')
    task_ids = set()
    with task_file.open('rb') as stream:
        for line in stream:
            _require(len(line)<=plan.task_bytes+1,'oversized retained task')
            task = _json(line)
            _require(task['task_id'] not in task_ids,'repeated retained task')
            task_ids.add(task['task_id'])
    result_dir = Path(stage['result_dir'])
    _require(result_dir==attempt/(value['stage']+'-results'),'foreign completion directory')
    complete = _json(_bytes(result_dir/'complete.json'))
    _require(complete['execution_id']==plan.execution_id and
             complete['task_count']==stage['task_count']==len(task_ids) and
             _hash_file(result_dir/'completed.jsonl')['sha256']==complete['inventory_sha256'],
             'changed/incomplete completion inventory')
    completed = set()
    with (result_dir/'completed.jsonl').open('rb') as stream:
        for line in stream:
            row = _json(line)
            ref = ArtifactRef(**{key:row[key] for key in ('path','sha256','size')})
            payload = _json(_raw(result_dir,ref,plan.result_bytes))
            _require(payload['execution_id']==plan.execution_id and
                     payload['attempt_id']==attempt.name and
                     payload['collection_id']==plan.collection_sha256 and
                     payload['problem_id']==plan.problem_sha256 and payload['scope']==plan.scope and
                     payload['task_id'] in task_ids and payload['task_id'] not in completed,
                     'foreign/stale/repeated task result')
            completed.add(payload['task_id'])
    _require(completed==task_ids,'missing owned task result')
    profile_raw = _bytes(argument('--profile', path.parent/'profile.json'))
    if current:
        _require(hashlib.sha256(profile_raw).hexdigest() == value['profile_sha256'],
                 'profile fingerprint differs from receipt')
    profile = json.loads(profile_raw)
    _require(profile['exit_code']==0 and profile['error'] is None and
             profile['program_sha256']==value['program_sha256'],'profile differs from receipt')
    if value['format'] == _CURRENT:
        _require('logs' not in value, 'diagnostics do not belong in scientific authority')
    else:
        _verify_inline_streams(path, value)
    return {'record': _record(path), 'stage': stage, 'plan': plan}


def _verify_inline_streams(path, receipt):
    attempt = path.parent.parent
    for stream in ('stdout','stderr'):
        descriptor = receipt['logs'][stream]
        retained = attempt/descriptor['path']
        if receipt['format'] == _INLINE:
            expected = path.parent/(stream+'.jsonl')
            _require(descriptor['path'] == expected.relative_to(attempt).as_posix() and
                     retained.resolve(strict=True) == expected, 'foreign owned stream')
        _require(hashlib.sha256(_bytes(retained)).hexdigest() == descriptor['sha256'],
                 'changed owned stream')


def verify_stage_diagnostics(path, *, expected_inventory_sha256=None):
    """Verify diagnostic bytes without making them a prerequisite for resume."""
    path = Path(path).absolute()
    raw = _bytes(path)
    receipt = json.loads(raw)
    _require(path.name == 'receipt.json' and receipt.get('format') == _CURRENT and
             receipt.get('stage') == path.parent.name, 'not a separately inventoried stage')
    manifest = _bytes(path.parent/'diagnostics.json')
    digest = hashlib.sha256(manifest).hexdigest()
    _require(expected_inventory_sha256 is None or digest == expected_inventory_sha256,
             'diagnostic inventory fingerprint mismatch')
    diagnostic = _json(manifest)
    _require(set(diagnostic) == {'format','receipt_sha256','streams'} and
             diagnostic['format'] == 'whole-source-owned-stage-diagnostics-v1' and
             diagnostic['receipt_sha256'] == hashlib.sha256(raw).hexdigest() and
             set(diagnostic['streams']) == {'stdout','stderr'}, 'foreign diagnostic inventory')
    for stream, ref in diagnostic['streams'].items():
        data = _bytes(path.parent/(stream+'.jsonl'))
        _require(ref == {'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()},
                 'changed diagnostic stream')
    return ArtifactRef('diagnostics.json', digest, len(manifest))
