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
from scripts.whole_source.task_groups import (
    GROUP, LEGACY_GROUP, PROPOSAL_COLLECTIONS, _group_document, _group_evidence, _portable_bytes,
    _seal_evidence, local_group, operation_group,
)

LEGACY_RECOVERY_POLICY = 'whole-source-wave-recovery-v1'
RECOVERY_POLICY = 'whole-source-wave-recovery-v2'
METADATA_BYTES = 16*MIB
PUBLICATION_BYTES = 16*MIB
MAX_RECORDS = 4096
LEGACY_ADOPTION = 'whole-source-task-adoption-v1'
ADOPTION = 'whole-source-task-adoption-v2'
_COLLECTIONS = {'proposal': PROPOSAL_COLLECTIONS | {'recovery-terminal'},
                'exact': {'collection'}, 'assessment': {'collection'}}
_TERMINALS = {'proposal': {'proposal.json', 'proposal-producers.json'},
              'exact': {'report.json'}, 'assessment': {'assessment.json'}}


def _require(value, message):
    if not value:
        raise ContractError(message)


def _digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def operation_context(operation, output, configuration):
    _require(operation in _COLLECTIONS, 'unknown recoverable operation')
    return {'format': RECOVERY_POLICY, 'operation': operation,
            'output': str(Path(output).absolute()), 'configuration': configuration, 'python': sys.version}


def _journal_document(collection, context, collection_id, *, format=RECOVERY_POLICY):
    collection = Path(collection).resolve(strict=True)
    _require(type(context) is dict and
             set(context) == {'format', 'operation', 'output', 'configuration', 'python'} and
             context['format'] == RECOVERY_POLICY and context['python'] == sys.version and
             context['operation'] in _COLLECTIONS, 'incompatible recovery operation context')
    output = Path(context['output']).resolve()
    if format == LEGACY_RECOVERY_POLICY:
        _require(collection.is_relative_to(output), 'foreign legacy recovery operation context')
        return {'format': format, 'root': str(collection), 'collection_id': collection_id,
                'context': {**context, 'format': format}}
    _require(format == RECOVERY_POLICY and output == collection.parent and
             collection.name in _COLLECTIONS[context['operation']] and _safe(output, collection.name) == collection,
             'incompatible recovery operation context')
    return {'format': format, 'collection': collection.name, 'collection_id': collection_id,
            'context': {key: value for key, value in context.items() if key != 'output'}}


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
    format = document.get('format')
    context = document.get('context')
    _require(type(context) is dict and format in (LEGACY_RECOVERY_POLICY, RECOVERY_POLICY) and
             context.get('format') == format and context.get('python') == sys.version and
             context.get('operation') in _COLLECTIONS, 'changed recovery journal context')
    if format == LEGACY_RECOVERY_POLICY:
        _require(set(document) == {'format', 'root', 'collection_id', 'context'} and
                 document['root'] == str(root) and
                 set(context) == {'format', 'operation', 'output', 'configuration', 'python'} and
                 root.is_relative_to(Path(context['output']).resolve()), 'changed legacy recovery journal context')
    else:
        _require(set(document) == {'format', 'collection', 'collection_id', 'context'} and
                 document['collection'] == root.name and root.name in _COLLECTIONS[context['operation']] and
                 set(context) == {'format', 'operation', 'configuration', 'python'},
                 'changed recovery journal context')
    return document


def _state(root, context):
    context_sha256 = _digest(context)
    format = context['format']
    _require((root/'recovery/head.json').exists(), 'missing committed recovery journal head')
    value = _json(_bytes(_safe(root, 'recovery/head.json'), 65536))
    _require(set(value) == {'format', 'context_sha256', 'count', 'tip'} and value['format'] == format and
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
                 node['format'] == format and node['context_sha256'] == context_sha256 and
                 node['kind'] in ('wave', 'adoption', 'terminal', 'stage-intent') and type(node['key']) is str and
                 0 < len(node['key']) <= 128, 'invalid recovery journal record')
        resident += python_bytes(node)+512
        _require(resident <= METADATA_BYTES, 'recovery decoded journal allowance exceeded')
        records.append((ref, node))
        ref = node['previous']
    _require(len(records) == value['count'], 'incomplete recovery journal chain')
    return records, value


def _original(record):
    root, ref, document = _group_document(record)
    if document.get('format') in (ADOPTION, LEGACY_ADOPTION):
        return resolve_adoption(record, document['context'], expected_root=root)
    _require(document.get('format') in (GROUP, LEGACY_GROUP), 'unknown recovery group format')
    return {'root': str(root), 'artifact': asdict(ref)}


def _wave(root, payload, journal):
    _require(type(payload) is dict and set(payload) == {'group', 'value'}, 'invalid recovery wave payload')
    group = payload['group']
    legacy = journal['format'] == LEGACY_RECOVERY_POLICY
    _require(type(group) is dict and set(group) == ({'root', 'artifact'} if legacy else {'artifact'}),
             'invalid recovery wave group')
    _, ref, document = _group_document(group, expected_root=root)
    _require(document.get('format') == (LEGACY_GROUP if legacy else GROUP),
             'recovery checkpoint is not a fresh producer')
    _, _, evidence = _group_evidence(group, document['context'], expected_root=root)
    _require(evidence['plan'].collection_sha256 == journal['collection_id'], 'foreign recovery wave collection')
    return {'root': str(root), 'artifact': asdict(ref)}, evidence['record']


def _terminal_payload(collection, output, filename, value, format):
    _require(type(value) is dict and type(value.get('dependencies')) is list, 'invalid recovery terminal intent')
    if format == LEGACY_RECOVERY_POLICY:
        _require(set(value) == {'path', 'artifact', 'dependencies'} and value['path'] == str(output/filename),
                 'changed legacy recovery terminal intent')
    else:
        _require(format == RECOVERY_POLICY and set(value) == {'filename', 'artifact', 'dependencies'} and
                 value['filename'] == filename and output == collection.parent,
                 'changed recovery terminal intent')
    ref = ArtifactRef(**value['artifact'])
    _require(ref.path.startswith('recovery/'), 'foreign recovery terminal bytes')
    return ref


def _terminal_dependency(output, context, record):
    group = operation_group(output, record)
    operation = context['operation']
    allowed = PROPOSAL_COLLECTIONS if operation == 'proposal' else {'collection'}
    _require(group['collection'] in allowed, 'foreign recovery terminal dependency role')
    root = _safe(output, group['collection'])
    journal = _context_document(root)
    _require(journal['format'] == RECOVERY_POLICY and journal['context'] == context,
             'foreign operation for recovery terminal dependency')
    _, ref, document = _group_document(group, expected_root=root)
    _require(document.get('format') == GROUP, 'terminal dependency is not an original producer')
    _, _, evidence = _group_evidence(group, document['context'], expected_root=root)
    _require(evidence['plan'].collection_sha256 == journal['collection_id'],
             'foreign recovery terminal dependency collection')
    return {'collection': root.name, 'artifact': asdict(ref)}


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
        expected = _journal_document(self.root, context, lock.spec.collection_id)
        raw_context = _portable_bytes(expected)
        _require(len(raw_context) <= 8*MIB, 'recovery context exceeds bounded codec')
        self.output = self.root.parent
        check_history(self.root)
        folder = _safe(self.root, 'recovery', missing=True)
        if not folder.exists():
            folder.mkdir()
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
            self._replace('recovery/context.json', raw_context)
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
        raw = _portable_bytes(node)
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
        group, _ = _wave(self.root, payload, self.document)
        return {'group': group, 'value': payload['value']}

    def commit(self, key, group, value):
        _require(key not in self.waves, 'recovery checkpoint already committed')
        payload = {'group': local_group(self.root, group), 'value': value}
        _wave(self.root, payload, self.document)
        ref = self._append('wave', key, payload)
        self.waves[key] = ref
        return ref

    def adopt(self, key, *, attempt_id=None):
        value = self.get(key)
        _require(value is not None, 'missing recovery checkpoint')
        attempt_id = self.retry_id if attempt_id is None else attempt_id
        if attempt_id != self.retry_id:
            self.lock._check(attempt_id=attempt_id)
        source = local_group(self.root, value['group'])
        _, _, source_doc = _group_document(source, expected_root=self.root)
        if source_doc['attempt_id'] == attempt_id:
            return value['group']
        owner = {'format': RECOVERY_POLICY, 'retry_id': self.retry_id, 'attempt_id': attempt_id,
                 'generation': self.lock.generation, 'collection_id': self.lock.spec.collection_id,
                 'context_sha256': _digest(self.document)}
        owner['artifact_owner'] = (asdict(self.lock._attempts[attempt_id])
                                   if attempt_id != self.retry_id else None)
        owner_ref = asdict(self.lock._immutable('recovery', _portable_bytes(owner)))
        document = {'format': ADOPTION, 'context': source_doc['context'], 'origin': source,
                    'checkpoint': self.waves[key], 'owner': owner_ref, 'attempt_id': attempt_id,
                    'collection_id': self.lock.spec.collection_id, 'generation': self.lock.generation,
                    'journal_context': _digest(self.document)}
        ref = asdict(self.lock._immutable('recovery', _portable_bytes(document)))
        self._append('adoption', key, {'artifact': ref})
        return {'root': str(self.root), 'artifact': ref}

    def terminal(self, path):
        _, raw, _ = self._terminal(path)
        return None if raw is None else _json(raw)

    def _terminal(self, path):
        self._check_head()
        path = Path(path).absolute()
        operation = self.document['context']['operation']
        _require(path.parent == self.output and path.name in _TERMINALS[operation] and
                 (operation != 'proposal' or self.root.name == 'recovery-terminal'),
                 'foreign recovery terminal destination')
        _safe(self.output, path.name, missing=True)
        ref = self.terminals.get(path.name)
        if ref is None:
            _require(not path.exists(), 'terminal file has no committed publication intent')
            return path, None, None
        value = self._node(ref)['payload']
        artifact = _terminal_payload(self.root, self.output, path.name, value, RECOVERY_POLICY)
        for group in value['dependencies']:
            _require(type(group) is dict and set(group) == {'collection', 'artifact'},
                     'invalid recovery terminal dependency')
            _terminal_dependency(self.output, self.document['context'], group)
        raw = _raw(self.root, artifact, 8*MIB)
        if path.exists():
            _require(_bytes(path, 8*MIB) == raw, 'conflicting terminal publication')
        return path, raw, value['dependencies']

    def publish(self, path, document, *, dependencies=()):
        path, prior, prior_dependencies = self._terminal(path)
        context = self.document['context']
        if prior is None:
            selected = [_terminal_dependency(self.output, context, group) for group in dependencies]
        else:
            selected = [operation_group(self.output, group) for group in dependencies]
        raw = _portable_bytes(document)
        _require(len(raw) <= 8*MIB, 'invalid terminal publication bytes')
        if prior is None:
            ref = asdict(self.lock._immutable('recovery', raw))
            node = self._append('terminal', path.name, {'filename': path.name, 'artifact': ref,
                                                      'dependencies': selected})
            self.terminals[path.name] = node
        else:
            _require(prior == raw, 'conflicting intended terminal bytes')
            _require(prior_dependencies == selected, 'conflicting intended terminal dependencies')
        return finish_publication(path, raw, operation=context['operation'])

    def intend_assessment(self, execution, task, context):
        """Bind the one final task before launch, not arbitrary orphan work."""
        _require(self.document['context']['operation'] == 'exact' and task.get('operation') == 'assess' and
                 execution.collection_lock is self.lock and
                 execution.output == self.root/'attempts'/execution.attempt_id, 'invalid final-assessment intent')
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
                     value['context'] == context and value['task'].get('operation') == 'assess' and
                     value['receipt'] == f"attempts/{value['attempt_id']}/assess/receipt.json",
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
        outputs = {'assessment': asdict(self.lock._immutable('seals', _portable_bytes(result['assessment'])))}
        group = _seal_evidence(self.lock, evidence, context, outputs)
        self.commit('assess', group, {'outputs': outputs})
        return self.get('assess')

    def receipts(self):
        self._check_head()
        return _selected_receipts(self.root, self.document, (self._node(ref) for ref in self.waves.values()))


def resolve_adoption(record, context, *, expected_root=None, expected_attempt=None):
    root, ref, document = _group_document(record, expected_root=expected_root)
    legacy = document.get('format') == LEGACY_ADOPTION
    _require(set(document) == {'format', 'context', 'origin', 'checkpoint', 'owner', 'attempt_id',
                               'collection_id', 'generation', 'journal_context'} and
             document['format'] in (ADOPTION, LEGACY_ADOPTION) and
             canonical_bytes(document['context']) == canonical_bytes(context), 'invalid recovery adoption')
    _require(expected_attempt is None or expected_attempt == document['attempt_id'], 'foreign adopted execution attempt')
    journal = _context_document(root)
    policy = LEGACY_RECOVERY_POLICY if legacy else RECOVERY_POLICY
    _require(journal['format'] == policy and document['journal_context'] == _digest(journal) and
             document['collection_id'] == journal['collection_id'],
             'foreign adopted recovery context')
    owner = _json(_raw(root, ArtifactRef(**document['owner']), 8*MIB))
    _require(owner.get('format') == policy and owner.get('attempt_id') == document['attempt_id'] and
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
    # The append-only chain must already contain the original wave before its
    # adoption. Compare the exact ref and original payload, not output equality.
    adoption_key = None
    for checkpoint_ref, node in records:
        if node['kind'] == 'adoption' and node['payload'] == {'artifact': asdict(ref)}:
            adoption_key = node['key']
        if checkpoint_ref != document['checkpoint']:
            continue
        _require(adoption_key is not None and node['kind'] == 'wave' and node['key'] == adoption_key and
                 node['payload']['group'] == document['origin'], 'missing or foreign adopted producer checkpoint')
        origin = document['origin']
        _require(type(origin) is dict and set(origin) == ({'root', 'artifact'} if legacy else {'artifact'}),
                 'invalid adopted producer locator')
        _, source, source_doc = _group_document(origin, expected_root=root)
        _require(source_doc.get('format') == (LEGACY_GROUP if legacy else GROUP) and
                 source_doc['collection_id'] == journal['collection_id'],
                 'nested, cyclic or foreign group adoption')
        return {'root': str(root), 'artifact': asdict(source)}
    raise ContractError('uncommitted recovery adoption or missing producer checkpoint')


def selected_receipts(directory):
    """Select a prospective collection's committed producers; keep all cleanup history."""
    root = Path(directory).resolve(strict=True)
    if not (root/'recovery/context.json').exists():
        return None
    check_history(root)
    document = _context_document(root)
    records, _ = _state(root, document)
    return _selected_receipts(root, document, (node for _, node in records))


def _selected_receipts(root, document, nodes):
    selected, waves = {}, set()
    for node in nodes:
        if node['kind'] == 'wave':
            _require(node['key'] not in waves, 'repeated recovery checkpoint')
            waves.add(node['key'])
            _, record = _wave(root, node['payload'], document)
            selected[str(Path(record['directory'])/record['artifact']['path'])] = record
    return [selected[key] for key in sorted(selected)]
