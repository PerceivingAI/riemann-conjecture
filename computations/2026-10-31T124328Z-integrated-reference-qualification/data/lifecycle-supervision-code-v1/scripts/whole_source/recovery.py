"""Prospective same-method wave recovery with immutable producer lineage."""
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import uuid

from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes
from scripts.whole_source.artifacts import _raw, _safe, _volume_gate, _sync_directory
from scripts.whole_source.execution import MIB, _bytes, _json, _write
from scripts.run_observability import replace_path_with_permission_retry
from scripts.whole_source.receipts import discover_receipts, verify_stage
from scripts.whole_source.reuse import python_bytes

RECOVERY_POLICY = 'whole-source-wave-recovery-v1'
METADATA_BYTES = 16*MIB
PUBLICATION_BYTES = 16*MIB
MAX_RECORDS = 4096
ADOPTION = 'whole-source-task-adoption-v1'


def _require(value, message):
    if not value:
        raise ContractError(message)


def _digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def operation_context(operation, output, configuration):
    _require(operation in ('proposal', 'exact', 'assessment'), 'unknown recoverable operation')
    return {'format': RECOVERY_POLICY, 'operation': operation,
            'output': str(Path(output).absolute()), 'configuration': configuration, 'python': sys.version}


def check_history(root):
    """Earlier failed mathematics is allowed; unresolved owned cleanup is not."""
    root = Path(root).resolve(strict=True)
    receipts = {}
    for path in discover_receipts(root):
        value = json.loads(_bytes(path))
        _require(value.get('worker_cleanup_verified') is True, 'recovery history has unresolved owned cleanup')
        receipts[path.resolve()] = value
    attempts = root/'attempts'
    if attempts.exists():
        for attempt in attempts.iterdir():
            _require(attempt.is_dir() and not attempt.is_symlink(), 'unsafe recovery attempt')
            for stage in attempt.glob('*-stage.json'):
                name = stage.name[:-len('-stage.json')]
                receipt = (attempt/name/'receipt.json').resolve()
                _require(receipt in receipts, 'recovery stage has no owned cleanup receipt')
                descriptor = _json(_bytes(stage))
                _require(descriptor.get('attempt_id') == attempt.name and receipts[receipt].get('stage') == name,
                         'foreign recovery stage history')
    return sorted(receipts, key=str)


def _context_document(root):
    document = _json(_bytes(_safe(root, 'recovery/context.json'), 8*MIB))
    _require(set(document) == {'format', 'root', 'collection_id', 'context'} and
             document['format'] == RECOVERY_POLICY and document['root'] == str(root) and
             document['context'].get('format') == RECOVERY_POLICY and
             document['context'].get('python') == sys.version, 'changed recovery journal context')
    return document


def _state(root, context):
    context_sha256 = _digest(context)
    _require((root/'recovery/head.json').exists(), 'missing committed recovery journal head')
    value = _json(_bytes(_safe(root, 'recovery/head.json'), 65536))
    _require(set(value) == {'format', 'context_sha256', 'count', 'tip'} and value['format'] == RECOVERY_POLICY and
             value['context_sha256'] == context_sha256 and type(value['count']) is int and
             0 <= value['count'] <= MAX_RECORDS and
             ((value['count'] == 0) == (value['tip'] is None)), 'invalid recovery journal head')
    records, seen, ref, resident = [], set(), value['tip'], 0
    while ref is not None:
        artifact = ArtifactRef(**ref)
        _require(artifact.path.startswith('recovery/') and artifact.sha256 not in seen and len(records) < MAX_RECORDS,
                 'cyclic or excessive recovery journal')
        seen.add(artifact.sha256)
        node = _json(_raw(root, artifact, 8*MIB))
        _require(set(node) == {'format', 'context_sha256', 'previous', 'kind', 'key', 'payload'} and
                 node['format'] == RECOVERY_POLICY and node['context_sha256'] == context_sha256 and
                 node['kind'] in ('wave', 'adoption', 'terminal', 'stage-intent') and type(node['key']) is str and
                 0 < len(node['key']) <= 128, 'invalid recovery journal record')
        resident += python_bytes(node)+512
        _require(resident <= METADATA_BYTES, 'recovery decoded journal allowance exceeded')
        records.append((ref, node))
        ref = node['previous']
    _require(len(records) == value['count'], 'incomplete recovery journal chain')
    return records, value


def _original(record):
    root = Path(record['root']).resolve(strict=True)
    document = _json(_raw(root, ArtifactRef(**record['artifact']), 8*MIB))
    if document.get('format') == ADOPTION:
        return document['origin']
    _require(document.get('format') == 'whole-source-task-group-v1', 'unknown recovery group format')
    return record


def _validate_group(record):
    from scripts.whole_source.task_groups import _read_group
    root = Path(record['root']).resolve(strict=True)
    document = _json(_raw(root, ArtifactRef(**record['artifact']), 8*MIB))
    return _read_group(record, document['context'])


def _external_allowance(root, additional, operation):
    allowed = {'collection', 'recovery-terminal'}
    if operation == 'proposal':
        allowed.update(f'{phase}-{p}' for phase in ('native', 'floating', 'solve') for p in (0, 1))
    total = 0
    with os.scandir(root) as entries:
        for entry in entries:
            info = entry.stat(follow_symlinks=False)
            _require(not stat.S_ISLNK(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 0x400,
                     'unsafe recovery publication member')
            if stat.S_ISDIR(info.st_mode):
                _require(entry.name in allowed, 'unaccounted recovery publication directory')
            else:
                _require(stat.S_ISREG(info.st_mode), 'nonregular recovery publication member')
                total += info.st_size
    _require(total+additional <= PUBLICATION_BYTES, 'recovery external publication allowance exceeded')
    _require(shutil.disk_usage(root).free >= additional+64*MIB, 'insufficient recovery publication free space')


def finish_publication(path, raw, *, operation='assessment'):
    """Publish exact intended bytes without replacing a conflicting fixed file."""
    path = Path(path).absolute()
    root = path.parent.resolve(strict=True)
    _safe(root, path.name, missing=True)
    _require(type(raw) is bytes and len(raw) <= 8*MIB, 'invalid terminal publication bytes')
    if path.exists():
        _require(_bytes(path, 8*MIB) == raw, 'conflicting terminal publication')
        return ArtifactRef(path.name, hashlib.sha256(raw).hexdigest(), len(raw))
    volume = root/'.volume.lock'
    if not volume.exists():
        with volume.open('xb'):
            pass
    with _volume_gate(root):
        _external_allowance(root, len(raw), operation)
        temporary = root/('.publication-'+uuid.uuid4().hex)
        _write(temporary, raw)
        _sync_directory(root)
        _require(not path.exists(), 'terminal publication appeared concurrently')
        replace_path_with_permission_retry(temporary, path)
    return ArtifactRef(path.name, hashlib.sha256(raw).hexdigest(), len(raw))


class RecoveryJournal:
    """A bounded owner/head-bound catalog of complete wave and publication commits."""
    def __init__(self, lock, context, *, resume=False):
        lock._check()
        self.lock, self.root, self.context = lock, Path(lock.root).resolve(), context
        self.retry_id = uuid.uuid4().hex
        _require(context.get('format') == RECOVERY_POLICY and context.get('python') == sys.version and
                 self.root.is_relative_to(Path(context['output']).resolve()), 'incompatible recovery operation context')
        check_history(self.root)
        folder = _safe(self.root, 'recovery', missing=True)
        if not folder.exists():
            folder.mkdir()
        expected = {'format': RECOVERY_POLICY, 'root': str(self.root),
                    'collection_id': lock.spec.collection_id, 'context': context}
        path = self.root/'recovery/context.json'
        if path.exists():
            _require(resume and _context_document(self.root) == expected, 'incompatible recovery resume context')
        else:
            _require(not any((self.root/'attempts').iterdir()),
                     'nonempty output lacks a recovery protocol')
            initial = {'format': RECOVERY_POLICY, 'context_sha256': _digest(expected), 'count': 0, 'tip': None}
            head = folder/'head.json'
            if head.exists():
                _require(_bytes(_safe(self.root, 'recovery/head.json'), 65536) == canonical_bytes(initial),
                         'unbound recovery head is not an initial publication')
            else:
                self._replace('recovery/head.json', canonical_bytes(initial))
            # Context last distinguishes interrupted initialization from a lost head.
            self._replace('recovery/context.json', canonical_bytes(expected))
        self.document = expected
        self.records, self.head = _state(self.root, expected)
        self.resident = sum(python_bytes(node)+512 for _, node in self.records)
        self._index()

    def _index(self):
        self.waves, self.terminals = {}, {}
        for ref, node in reversed(self.records):
            target = self.waves if node['kind'] == 'wave' else self.terminals if node['kind'] == 'terminal' else None
            if target is not None:
                _require(node['key'] not in target, 'repeated recovery checkpoint')
                target[node['key']] = ref

    def _replace(self, relative, raw):
        temporary = 'recovery/.publish-'+uuid.uuid4().hex
        self.lock._exclusive(temporary, raw)
        self.lock._check()
        _sync_directory(self.root/'recovery')
        replace_path_with_permission_retry(self.root/temporary, self.root/relative)

    def _append(self, kind, key, payload):
        self.lock._check()
        self._check_head()
        _require(self.head['count'] < MAX_RECORDS and type(key) is str and 0 < len(key) <= 128,
                 'recovery journal record limit exceeded')
        node = {'format': RECOVERY_POLICY, 'context_sha256': _digest(self.document),
                'previous': self.head['tip'], 'kind': kind, 'key': key, 'payload': payload}
        raw = canonical_bytes(node)
        _require(len(raw) <= 8*MIB, 'recovery record exceeds bounded codec')
        charge = python_bytes(node)+512
        _require(self.resident+charge <= METADATA_BYTES, 'recovery decoded journal allowance exceeded')
        ref = asdict(self.lock._immutable('recovery', raw))
        head = {'format': RECOVERY_POLICY, 'context_sha256': _digest(self.document),
                'count': self.head['count']+1, 'tip': ref}
        self._replace('recovery/head.json', canonical_bytes(head))
        self.head = head
        self.records.append((ref, node))
        self.resident += charge
        return ref

    def _node(self, ref):
        self._check_head()
        return _json(_raw(self.root, ArtifactRef(**ref), 8*MIB))


    def _check_head(self):
        self.lock._check()
        _require(_context_document(self.root) == self.document, 'changed active recovery context')
        actual = _json(_bytes(_safe(self.root, 'recovery/head.json'), 65536))
        _require(actual == self.head, 'changed active recovery journal head')
    def get(self, key):
        self._check_head()
        ref = self.waves.get(key)
        if ref is None:
            return None
        payload = self._node(ref)['payload']
        _require(set(payload) == {'group', 'value'}, 'invalid recovery wave payload')
        root, _, stage = _validate_group(payload['group'])
        _require(root == self.root and stage['plan']['collection_sha256'] == self.lock.spec.collection_id,
                 'foreign recovery wave collection')
        return payload

    def commit(self, key, group, value):
        _require(key not in self.waves, 'recovery checkpoint already committed')
        root, _, stage = _validate_group(group)
        _require(root == self.root and stage['plan']['collection_sha256'] == self.lock.spec.collection_id and
                 _original(group) == group, 'cannot commit a foreign or adopted producer as fresh')
        ref = self._append('wave', key, {'group': group, 'value': value})
        self.waves[key] = ref
        return ref

    def adopt(self, key, *, attempt_id=None):
        value = self.get(key)
        _require(value is not None, 'missing recovery checkpoint')
        attempt_id = self.retry_id if attempt_id is None else attempt_id
        if attempt_id != self.retry_id:
            self.lock._check(attempt_id=attempt_id)
        source = value['group']
        _, _, stage = _validate_group(source)
        if stage['attempt_id'] == attempt_id:
            return source
        source_doc = _json(_raw(self.root, ArtifactRef(**source['artifact']), 8*MIB))
        owner = {'format': RECOVERY_POLICY, 'retry_id': self.retry_id, 'attempt_id': attempt_id,
                 'generation': self.lock.generation, 'collection_id': self.lock.spec.collection_id,
                 'context_sha256': _digest(self.document)}
        owner['artifact_owner'] = (asdict(self.lock._attempts[attempt_id])
                                   if attempt_id != self.retry_id else None)
        owner_ref = asdict(self.lock._immutable('recovery', canonical_bytes(owner)))
        document = {'format': ADOPTION, 'context': source_doc['context'], 'origin': source,
                    'checkpoint': self.waves[key], 'owner': owner_ref, 'attempt_id': attempt_id,
                    'collection_id': self.lock.spec.collection_id, 'generation': self.lock.generation,
                    'journal_context': _digest(self.document)}
        ref = asdict(self.lock._immutable('recovery', canonical_bytes(document)))
        self._append('adoption', key, {'artifact': ref})
        return {'root': str(self.root), 'artifact': ref}

    def terminal(self, path):
        self._check_head()
        path = Path(path).absolute()
        _require(path.parent == Path(self.context['output']).resolve() and
                 path.name in ('proposal.json', 'proposal-diagnostics.json', 'report.json', 'assessment.json'),
                 'foreign recovery terminal destination')
        ref = self.terminals.get(path.name)
        if ref is None:
            _require(not path.exists(), 'terminal file has no committed publication intent')
            return None
        value = self._node(ref)['payload']
        _require(set(value) == {'path', 'artifact', 'dependencies'} and value['path'] == str(path),
                 'changed recovery terminal intent')
        for group in value['dependencies']:
            _validate_group(group)
        raw = _raw(self.root, ArtifactRef(**value['artifact']), 8*MIB)
        if path.exists():
            _require(_bytes(path, 8*MIB) == raw, 'conflicting terminal publication')
        return _json(raw)

    def publish(self, path, document, *, dependencies=()):
        path = Path(path).absolute()
        prior = self.terminal(path)
        if prior is None:
            for group in dependencies:
                _validate_group(group)
            raw = canonical_bytes(document)
            ref = asdict(self.lock._immutable('recovery', raw))
            node = self._append('terminal', path.name, {'path': str(path), 'artifact': ref,
                                                      'dependencies': list(dependencies)})
            self.terminals[path.name] = node
        else:
            _require(canonical_bytes(prior) == canonical_bytes(document), 'conflicting intended terminal bytes')
            raw = canonical_bytes(prior)
        return finish_publication(path, raw, operation=self.context['operation'])

    def intend_assessment(self, execution, task, context):
        """Bind the one final task before launch, not arbitrary orphan work."""
        _require(task.get('operation') == 'assess' and execution.collection_lock is self.lock,
                 'invalid final-assessment intent')
        return self._append('stage-intent', 'assess', {
            'receipt': (execution.output/'assess/receipt.json').relative_to(self.root).as_posix(),
            'attempt_id': execution.attempt_id, 'execution_id': execution.plan.execution_id,
            'task': task, 'context': context})

    def recover_assessment(self, context):
        """Recover a complete final owned task only through its prelaunch intent."""
        existing = self.get('assess')
        if existing is not None:
            return existing
        candidates = []
        for ref, node in self.records:
            if node['kind'] != 'stage-intent' or node['key'] != 'assess':
                continue
            value = self._node(ref)['payload']
            _require(set(value) == {'receipt', 'attempt_id', 'execution_id', 'task', 'context'} and
                     value['context'] == context and value['task'].get('operation') == 'assess',
                     'changed final-assessment intent')
            path = self.root/value['receipt']
            if not path.exists():
                continue
            receipt = json.loads(_bytes(_safe(self.root, value['receipt'])))
            if receipt['exit_code'] != 0:
                _require(receipt.get('worker_cleanup_verified') is True, 'uncontained final-assessment history')
                continue
            evidence = verify_stage(path)
            stage, plan = evidence['stage'], evidence['plan']
            _require(stage['attempt_id'] == value['attempt_id'] and plan.execution_id == value['execution_id'] and
                     plan.collection_sha256 == self.lock.spec.collection_id and
                     plan.role == 'exact' and plan.task_function == 'evaluate_exact' and
                     plan.scope == 'EXACT_ASSESSMENT_ONLY' and stage['task_count'] == 1 and
                     _json(_bytes(Path(stage['task_file']))) == value['task'],
                     'final-assessment intent differs from owned execution')
            directory = Path(stage['result_dir'])
            row = _json(_bytes(directory/'completed.jsonl'))
            result = _json(_raw(directory, ArtifactRef(**{k: row[k] for k in ('path', 'sha256', 'size')}),
                               plan.result_bytes))['result']
            _require(set(result) == {'scope', 'assessment'} and result['scope'] == 'EXACT_ASSESSMENT_ONLY',
                     'invalid completed final-assessment result')
            candidates.append((evidence, result))
        _require(len(candidates) <= 1, 'conflicting completed final-assessment intents')
        if not candidates:
            return None
        evidence, result = candidates[0]
        outputs = {'assessment': asdict(self.lock._immutable('seals', canonical_bytes(result['assessment'])))}
        document = {'format': 'whole-source-task-group-v1', 'context': context,
                    'stage': evidence['record'], 'attempt_id': evidence['stage']['attempt_id'],
                    'collection_id': self.lock.spec.collection_id, 'outputs': outputs}
        group = {'root': str(self.root), 'artifact': asdict(self.lock._immutable('seals', canonical_bytes(document)))}
        self.commit('assess', group, {'outputs': outputs})
        return self.get('assess')

    def receipts(self):
        records = {}
        for key in self.waves:
            value = self.get(key)
            original = _original(value['group'])
            doc = _json(_raw(Path(original['root']), ArtifactRef(**original['artifact']), 8*MIB))
            record = doc['stage']
            records[str(Path(record['directory'])/record['artifact']['path'])] = record
        return [records[key] for key in sorted(records)]


def resolve_adoption(record, context, *, expected_root=None, expected_attempt=None):
    root = Path(record['root']).resolve(strict=True)
    document = _json(_raw(root, ArtifactRef(**record['artifact']), 8*MIB))
    _require(set(document) == {'format', 'context', 'origin', 'checkpoint', 'owner', 'attempt_id',
                               'collection_id', 'generation', 'journal_context'} and
             document['format'] == ADOPTION and canonical_bytes(document['context']) == canonical_bytes(context),
             'invalid recovery adoption')
    _require(expected_root is None or root == Path(expected_root).resolve(strict=True), 'foreign adopted execution root')
    _require(expected_attempt is None or expected_attempt == document['attempt_id'], 'foreign adopted execution attempt')
    journal = _context_document(root)
    _require(document['journal_context'] == _digest(journal) and document['collection_id'] == journal['collection_id'],
             'foreign adopted recovery context')
    owner = _json(_raw(root, ArtifactRef(**document['owner']), 8*MIB))
    _require(owner.get('format') == RECOVERY_POLICY and owner.get('attempt_id') == document['attempt_id'] and
             owner.get('generation') == document['generation'] and owner.get('collection_id') == document['collection_id'] and
             owner.get('context_sha256') == document['journal_context'], 'changed recovery adoption owner')
    _require(set(owner) == {'format', 'retry_id', 'attempt_id', 'generation', 'collection_id',
                            'context_sha256', 'artifact_owner'}, 'invalid recovery owner record')
    if owner['artifact_owner'] is not None:
        active = _json(_raw(root, ArtifactRef(**owner['artifact_owner']), 65536))
        _require(active.get('attempt_id') == document['attempt_id'] and
                 active.get('generation') == document['generation'] and
                 active.get('collection_id') == document['collection_id'], 'changed adopted execution owner')
    else:
        _require(owner['attempt_id'] == owner['retry_id'] and expected_attempt is None,
                 'adoption has no current execution owner')
    records, _ = _state(root, journal)
    _require(any(node['kind'] == 'adoption' and node['payload'] == {'artifact': record['artifact']} for _, node in records),
             'uncommitted recovery adoption')
    checkpoints = {canonical_bytes(ref): node for ref, node in records if node['kind'] == 'wave'}
    checkpoint = checkpoints.get(canonical_bytes(document['checkpoint']))
    _require(checkpoint is not None and checkpoint['payload']['group'] == document['origin'] and
             Path(document['origin']['root']).resolve(strict=True) == root,
             'missing or foreign adopted producer checkpoint')
    origin = document['origin']
    source_doc = _json(_raw(root, ArtifactRef(**origin['artifact']), 8*MIB))
    _require(source_doc.get('format') == 'whole-source-task-group-v1', 'nested or cyclic group adoption')
    return origin


def selected_receipts(directory):
    """Select a prospective collection's committed producers; keep all cleanup history."""
    root = Path(directory).resolve(strict=True)
    if not (root/'recovery/context.json').exists():
        return None
    check_history(root)
    document = _context_document(root)
    records, _ = _state(root, document)
    selected = {}
    for _, node in records:
        if node['kind'] != 'wave':
            continue
        group = node['payload']['group']
        _validate_group(group)
        origin = _original(group)
        value = _json(_raw(root, ArtifactRef(**origin['artifact']), 8*MIB))
        record = value['stage']
        selected[str(Path(record['directory'])/record['artifact']['path'])] = record
    return [selected[key] for key in sorted(selected)]
