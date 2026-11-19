"""Hash-bound outputs of complete successful owned dependency waves."""
from dataclasses import asdict
from fractions import Fraction
import hashlib
from pathlib import Path

from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes
from scripts.whole_source.artifacts import _raw, _safe
from scripts.whole_source.execution import MIB, _json
from scripts.whole_source.receipts import verify_stage


LEGACY_GROUP = 'whole-source-task-group-v1'
GROUP = 'whole-source-task-group-v2'
PROPOSAL_COLLECTIONS = frozenset(
    f'{phase}-{parity}' for phase in ('native', 'floating', 'solve') for parity in (0, 1))
COLLECTION_ROLES = PROPOSAL_COLLECTIONS | {'collection', 'recovery-terminal'}


def _require(value, message):
    if not value:
        raise ContractError(message)


def _portable_bytes(value):
    """Reject unencoded runtime paths before staging current metadata."""
    def check(item):
        if type(item) is str:
            _require(not item.startswith(('/', '\\')) and not (len(item) >= 2 and item[1] == ':' and
                     item[0].isascii() and item[0].isalpha()),
                     'physical path in portable recovery metadata')
        elif type(item) is dict:
            for key, child in item.items():
                check(key)
                check(child)
        elif type(item) in (list, tuple):
            for child in item:
                check(child)
        else:
            _require(item is None or type(item) in (int, bool, Fraction),
                     'untyped portable recovery metadata')
    check(value)
    return canonical_bytes(value)


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
    return _seal_evidence(lock, evidence, context, outputs)


def _seal_evidence(lock, evidence, context, outputs):
    descriptor = evidence['stage']
    _verify_outputs(lock.root, outputs, _result_authority(descriptor))
    record = evidence['record']
    receipt = ArtifactRef(**record['artifact'])
    path = Path(record['directory'])/receipt.path
    root = Path(lock.root).resolve(strict=True)
    _require(path.is_relative_to(root/'attempts'), 'foreign dependency group receipt')
    relative = ArtifactRef(path.relative_to(root).as_posix(), receipt.sha256, receipt.size)
    document = {'format': GROUP, 'context': context, 'stage': asdict(relative),
                'attempt_id': descriptor['attempt_id'],
                'collection_id': lock.spec.collection_id, 'outputs': outputs}
    ref = lock._immutable('seals', _portable_bytes(document))
    return {'root': str(lock.root), 'artifact': asdict(ref)}


def local_group(root, record):
    """Bind a dependency to the already-authorized collection root."""
    _, ref = _group_locator(record, expected_root=root)
    return {'artifact': asdict(ref)}


def operation_group(output, record):
    """Encode a producer relative to the operation that owns its collection."""
    output = Path(output).resolve(strict=True)
    root, ref = _group_locator(record, operation_root=output)
    _require(root.parent == output and root.name in COLLECTION_ROLES,
             'dependency group belongs to another operation')
    _require(_safe(output, root.name) == root, 'foreign dependency group collection role')
    return {'collection': root.name, 'artifact': asdict(ref)}


def _group_locator(record, *, expected_root=None, operation_root=None):
    _require(type(record) is dict, 'invalid dependency group locator')
    expected = None if expected_root is None else Path(expected_root).resolve(strict=True)
    fields = set(record)
    if fields == {'root', 'artifact'}:
        root = Path(record['root']).resolve(strict=True)
    elif fields == {'artifact'} and expected is not None:
        root = expected
    elif fields == {'collection', 'artifact'}:
        role = record['collection']
        _require(type(role) is str and role in COLLECTION_ROLES, 'invalid dependency collection role')
        if operation_root is not None:
            root = _safe(Path(operation_root).resolve(strict=True), role)
        else:
            _require(expected is not None and expected.name == role,
                     'dependency group requires its authorized operation or collection')
            root = expected
    else:
        raise ContractError('invalid dependency group locator')
    _require(expected is None or root == expected, 'dependency group belongs to another execution root')
    return root, ArtifactRef(**record['artifact'])


def _group_document(record, *, expected_root=None, operation_root=None):
    root, ref = _group_locator(record, expected_root=expected_root, operation_root=operation_root)
    return root, ref, _json(_raw(root, ref, 8*MIB))


def _stage_evidence(root, document):
    locator = document['stage']
    if document['format'] == LEGACY_GROUP:
        _require(type(locator) is dict and set(locator) == {'directory', 'artifact'},
                 'invalid legacy dependency receipt locator')
        receipt_root = Path(locator['directory']).resolve(strict=True)
        receipt = ArtifactRef(**locator['artifact'])
        receipt_path = receipt_root/receipt.path
        _require(receipt_path.is_relative_to(root/'attempts') and
                 receipt_path.parent.parent.name == document['attempt_id'], 'foreign dependency group receipt')
        _raw(receipt_root, receipt, 8*MIB)
        evidence = verify_stage(receipt_path)
        _require(evidence['record'] == locator, 'changed legacy dependency receipt locator')
        return evidence
    receipt = ArtifactRef(**locator)
    parts = receipt.path.split('/')
    _require(len(parts) == 4 and parts[0] == 'attempts' and parts[1] == document['attempt_id']
             and parts[-1] == 'receipt.json', 'foreign dependency group receipt')
    _raw(root, receipt, 8*MIB)
    evidence = verify_stage(root/receipt.path)
    actual = ArtifactRef(**evidence['record']['artifact'])
    _require((actual.sha256, actual.size) == (receipt.sha256, receipt.size),
             'changed dependency group receipt bytes')
    return evidence


def _group_evidence(record, context, *, expected_root=None, expected_attempt=None, operation_root=None):
    root, ref, document = _group_document(record, expected_root=expected_root, operation_root=operation_root)
    from scripts.whole_source.recovery import ADOPTION, LEGACY_ADOPTION, resolve_adoption
    if document.get('format') in (ADOPTION, LEGACY_ADOPTION):
        origin = resolve_adoption({'root': str(root), 'artifact': asdict(ref)}, context,
                                  expected_root=root, expected_attempt=expected_attempt)
        return _group_evidence(origin, context, expected_root=root)
    _require(set(document) == {'format', 'context', 'stage', 'attempt_id', 'collection_id', 'outputs'} and
             document['format'] in (GROUP, LEGACY_GROUP) and
             canonical_bytes(document['context']) == canonical_bytes(context), 'changed dependency group context')
    evidence = _stage_evidence(root, document)
    descriptor = evidence['stage']
    _require(descriptor['attempt_id'] == document['attempt_id'] and
             descriptor['plan']['collection_sha256'] == document['collection_id'], 'changed dependency group authority')
    _require(expected_attempt is None or descriptor['attempt_id'] == expected_attempt,
             'dependency group belongs to another execution attempt')
    _verify_outputs(root, document['outputs'], _result_authority(descriptor))
    return root, document['outputs'], evidence


def _read_group(record, context, *, expected_root=None, expected_attempt=None, operation_root=None):
    """Reverify current raw stage and output bytes at independent consumption."""
    root, outputs, evidence = _group_evidence(record, context, expected_root=expected_root,
                                             expected_attempt=expected_attempt, operation_root=operation_root)
    return root, outputs, evidence['stage']


def group_receipt(record, *, expected_root=None, operation_root=None):
    """Return the original receipt as a runtime locator, never a new receipt."""
    root, ref, document = _group_document(record, expected_root=expected_root, operation_root=operation_root)
    _, _, evidence = _group_evidence({'artifact': asdict(ref)}, document['context'], expected_root=root)
    return evidence['record']


def read_group(record, context, *, expected_root=None, expected_attempt=None, operation_root=None):
    root, outputs, _ = _read_group(record, context, expected_root=expected_root,
                                   expected_attempt=expected_attempt, operation_root=operation_root)
    return root, outputs


def group_tasks(record, context, *, expected_root=None, expected_attempt=None, operation_root=None):
    """Yield raw-bound requests and their actual completed result, not claims."""
    _, _, stage = _read_group(record, context, expected_root=expected_root,
                             expected_attempt=expected_attempt, operation_root=operation_root)
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


def same_group(left, right, *, expected_root=None, operation_root=None):
    """Compare verified original producer identities, never relabel old tasks."""
    from scripts.whole_source.recovery import _original
    originals = []
    for record in (left, right):
        root, ref, document = _group_document(record, expected_root=expected_root, operation_root=operation_root)
        record = {'root': str(root), 'artifact': asdict(ref)}
        _read_group(record, document['context'], expected_root=root)
        originals.append(_original(record))
    return originals[0] == originals[1]
