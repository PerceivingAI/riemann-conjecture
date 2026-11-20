"""Discovery and strict verification of owned scientific stage evidence."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from scripts.whole_source.contract import ArtifactRef, ContractError
from scripts.whole_source.artifacts import _raw
from scripts.whole_source.execution import ExecutionPlan, MIB, _bytes, _json


_FORMAT = 't081-owned-stage-receipt-v1'


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
            json.loads(_bytes(path)).get('format') == _FORMAT]


def verify_stage(path):
    """Verify every retained stage binding before exposing its descriptor and plan."""
    path = Path(path).resolve(strict=True)
    value = json.loads(_bytes(path))
    _require(value.get('format') == _FORMAT, 'unrecognized owned stage receipt format')
    _require(value['exit_code']==0 and value['error'] is None and
             value['worker_cleanup_verified'] is True and
             value['last_metrics']['active_process_count']==0,'failed/uncontained owned scientific stage')
    attempt = path.parent.parent
    name = value['stage']
    _require(path.parent.name==name,'receipt belongs to another stage')
    argv = value['argv']
    def argument(flag):
        return Path(argv[argv.index(flag)+1]).resolve(strict=True)
    stage_path = argument('--stage')
    _require(stage_path==attempt/(name+'-stage.json') and
             _hash_file(stage_path)['sha256']==argv[argv.index('--stage-sha256')+1],
             'receipt does not bind this stage descriptor')
    stage = _json(_bytes(stage_path))
    plan = ExecutionPlan.from_dict(stage['plan'])
    _require(stage['attempt_id']==attempt.name,'receipt attempt differs')
    program = argument('--program')
    _require(program==attempt/'runtime/scripts/whole_source/execution.py' and
             _hash_file(program)['sha256']==value['program_sha256'],
             'receipt program differs from captured runtime')
    config_path = argument('--config')
    _require(config_path==attempt/'execution-budget.json' and
             _hash_file(config_path)['sha256']==value['config_sha256'],'changed owned budget')
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
    _require(result_dir==attempt/(name+'-results'),'foreign completion directory')
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
    profile = json.loads(_bytes(argument('--profile')))
    _require(profile['exit_code']==0 and profile['error'] is None and
             profile['program_sha256']==value['program_sha256'],'profile differs from receipt')
    for stream in ('stdout','stderr'):
        raw = _bytes(path.parent.parent/value['logs'][stream]['path'])
        _require(hashlib.sha256(raw).hexdigest()==value['logs'][stream]['sha256'],'changed owned stream')
    return {'record': _record(path), 'stage': stage, 'plan': plan}
