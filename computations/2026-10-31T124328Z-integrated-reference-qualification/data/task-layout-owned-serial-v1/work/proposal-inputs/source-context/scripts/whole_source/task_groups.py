"""Hash-bound outputs of complete successful owned dependency waves."""
from dataclasses import asdict
import hashlib
from pathlib import Path

from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes
from scripts.whole_source.artifacts import _raw
from scripts.whole_source.execution import MIB, _json
from scripts.whole_source.receipts import verify_stage


def _require(value, message):
    if not value:
        raise ContractError(message)


def _result_authority(stage):
    """Stream bounded result records, not mathematical arrays or live workers."""
    directory = Path(stage['result_dir'])
    authorized = set()
    def references(value):
        if type(value) is dict:
            if set(value) == {'path', 'sha256', 'size'}:
                ref = ArtifactRef(**value)
                authorized.add((ref.sha256, ref.size))
            else:
                for child in value.values():
                    references(child)
        elif type(value) is list:
            for child in value:
                references(child)
    with (directory/'completed.jsonl').open('rb') as stream:
        for line in stream:
            row = _json(line)
            ref = ArtifactRef(**{key: row[key] for key in ('path', 'sha256', 'size')})
            result = _json(_raw(directory, ref, stage['plan']['result_bytes']))['result']
            references(result)
            # Scalars/reports may be sealed by the owner directly from the exact
            # completed result or one of its named metadata values.
            for value in [result, *(result.values() if type(result) is dict else ())]:
                raw = canonical_bytes(value)
                authorized.add((hashlib.sha256(raw).hexdigest(), len(raw)))
    return authorized


def _verify_outputs(root, outputs, authorized):
    _require(type(outputs) is dict and outputs and
             all(type(name) is str and name for name in outputs), 'invalid dependency group outputs')
    for value in outputs.values():
        ref = ArtifactRef(**value)
        _require((ref.sha256, ref.size) in authorized, 'output lacks successful owned result authority')
        _raw(root, ref, 8*MIB)


def seal_group(lock, execution, stage, context, outputs):
    """Commit only after the entire named owned stage succeeds and cleans up."""
    evidence = verify_stage(execution.output/stage/'receipt.json')
    descriptor = evidence['stage']
    _require(descriptor['attempt_id'] == execution.attempt_id,
             'foreign dependency group stage')
    _require(descriptor['plan']['collection_sha256'] == lock.spec.collection_id,
             'dependency group belongs to another collection')
    _verify_outputs(lock.root, outputs, _result_authority(descriptor))
    document = {'format': 'whole-source-task-group-v1', 'context': context,
                'stage': evidence['record'], 'attempt_id': execution.attempt_id,
                'collection_id': lock.spec.collection_id, 'outputs': outputs}
    ref = lock._immutable('seals', canonical_bytes(document))
    return {'root': str(lock.root), 'artifact': asdict(ref)}


def _read_group(record, context, *, expected_root=None, expected_attempt=None):
    """Reverify current raw stage and output bytes at independent consumption."""
    _require(type(record) is dict and set(record) == {'root', 'artifact'}, 'invalid dependency group locator')
    root = Path(record['root']).resolve(strict=True)
    _require(expected_root is None or root == Path(expected_root).resolve(strict=True),
             'dependency group belongs to another execution root')
    document = _json(_raw(root, ArtifactRef(**record['artifact']), 8*MIB))
    _require(set(document) == {'format', 'context', 'stage', 'attempt_id', 'collection_id', 'outputs'} and
             document['format'] == 'whole-source-task-group-v1' and
             canonical_bytes(document['context']) == canonical_bytes(context), 'changed dependency group context')
    locator = document['stage']
    receipt_root = Path(locator['directory']).resolve(strict=True)
    receipt = ArtifactRef(**locator['artifact'])
    _raw(receipt_root, receipt, 8*MIB)
    receipt_path = receipt_root/receipt.path
    _require(receipt_path.is_relative_to(root/'attempts') and
             receipt_path.parent.parent.name == document['attempt_id'], 'foreign dependency group receipt')
    evidence = verify_stage(receipt_path)
    descriptor = evidence['stage']
    _require(evidence['record'] == locator and descriptor['attempt_id'] == document['attempt_id'] and
             descriptor['plan']['collection_sha256'] == document['collection_id'], 'changed dependency group authority')
    _require(expected_attempt is None or descriptor['attempt_id'] == expected_attempt,
             'dependency group belongs to another execution attempt')
    _verify_outputs(root, document['outputs'], _result_authority(descriptor))
    return root, document['outputs'], descriptor

def read_group(record, context, *, expected_root=None, expected_attempt=None):
    root, outputs, _ = _read_group(record, context, expected_root=expected_root,
                                   expected_attempt=expected_attempt)
    return root, outputs


def group_tasks(record, context, *, expected_root=None, expected_attempt=None):
    """Yield raw-bound requests and their actual completed result, not claims."""
    _, _, stage = _read_group(record, context, expected_root=expected_root,
                             expected_attempt=expected_attempt)
    directory = Path(stage['result_dir'])
    results = {}
    with (directory/'completed.jsonl').open('rb') as stream:
        for line in stream:
            row = _json(line)
            ref = ArtifactRef(**{key: row[key] for key in ('path', 'sha256', 'size')})
            payload = _json(_raw(directory, ref, stage['plan']['result_bytes']))
            _require(payload['task_id'] not in results, 'duplicate dependency task result')
            results[payload['task_id']] = ref
    with Path(stage['task_file']).open('rb') as stream:
        for line in stream:
            task = _json(line)
            ref = results.pop(task['task_id'])
            payload = _json(_raw(directory, ref, stage['plan']['result_bytes']))
            yield task, payload['result']
    _require(not results, 'unassigned dependency task result')
