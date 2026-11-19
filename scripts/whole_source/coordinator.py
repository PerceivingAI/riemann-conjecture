"""Bounded phase authority for a caller holding the operation's slice writer.

The caller owns the outer ``_slice_writer`` lock throughout construction and
mutation. This module does not acquire another lock. It checks the unchanged
committed head before publication, but that check is not a replacement for the
operation lock. A completion records verified artifact bytes, not mathematical
acceptance. Callers must validate role authority and selected output locations
before ``complete`` and before using a selected phase.

Only head-reachable nodes select attempts. Uncommitted nodes never establish
completion. A caller may recover genuine evidence against ``pending`` before
dispatch, or explicitly choose a fresh intent. Neither action deletes history.
"""
from dataclasses import asdict
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import uuid

from scripts.run_observability import replace_path_with_permission_retry
from scripts.whole_source.artifacts import _json, _root_path, _safe, _sync_directory
from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes
from scripts.whole_source.reuse import python_bytes
from scripts.whole_source.storage import guarded_open

PHASES = ('prepare', 'source', 'audit', 'proposal', 'exact-inputs', 'exact', 'controls', 'replay')
SCIENCE_PHASES = PHASES[:6]
FORMAT = 'whole-source-phase-coordinator-v2'
_LEGACY_FORMAT = 'whole-source-phase-coordinator-v1'
REPLAY_PROPOSAL = 'replay-inputs/proposal.json'
MAX_NODES = 4096
METADATA_BYTES = 16*1024*1024
FILE_BYTES = 1024*1024
HEAD_BYTES = 65536
_OUTPUTS = {
    'prepare': {'problem', 'source_execution', 'premises'},
    'source': {'source', 'source_publication'},
    'audit': {'audit', 'audit_execution'},
    'proposal': {'proposal'},
    'exact-inputs': {'problem', 'execution', 'operands'},
    'exact': {'exact'}, 'controls': {'controls'}, 'replay': {'replay'},
}


def _require(condition, message):
    if not condition:
        raise ContractError(message)


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _snapshot(value):
    raw = canonical_bytes(value)
    _require(len(raw) <= FILE_BYTES, 'coordinator metadata file allowance exceeded')
    return _json(raw, FILE_BYTES)


def _absolute(value):
    _require(type(value) is str and 0 < len(value) <= 32768, 'invalid coordinator absolute path')
    path = Path(value)
    _require(path.is_absolute() and str(path.absolute()) == value and str(path.resolve()) == value,
             'changed or ambiguous coordinator path')
    return path


def _read(root, relative, cap):
    path = _safe(root, relative)
    info = path.stat()
    _require(stat.S_ISREG(info.st_mode) and info.st_size <= cap, 'coordinator metadata file allowance exceeded')
    with path.open('rb') as stream:
        raw = stream.read(cap+1)
    _require(len(raw) == info.st_size and len(raw) <= cap, 'changed coordinator metadata file')
    return _json(raw, cap)


def _artifact_record(record, *, verify=True):
    _require(type(record) is dict and set(record) == {'directory', 'artifact'}, 'invalid phase artifact record')
    root = _absolute(record['directory'])
    _root_path(root)
    value = record['artifact']
    _require(type(value) is dict and set(value) == {'path', 'sha256', 'size'}, 'invalid phase artifact reference')
    try:
        ref = ArtifactRef(**value)
    except (TypeError, ValueError) as exc:
        raise ContractError('invalid phase artifact reference') from exc
    if verify:
        path = _safe(root, ref.path)
        before = path.stat()
        _require(stat.S_ISREG(before.st_mode) and before.st_size == ref.size, 'changed phase artifact size')
        digest, size = hashlib.sha256(), 0
        flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
        with os.fdopen(os.open(path, flags), 'rb') as stream:
            opened = os.fstat(stream.fileno())
            _require((opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino),
                     'phase artifact changed during open')
            while raw := stream.read(1024*1024):
                digest.update(raw)
                size += len(raw)
                _require(size <= ref.size, 'changed phase artifact size')
        _require(size == ref.size and digest.hexdigest() == ref.sha256, 'changed phase artifact fingerprint')
    return root, ref


def _reference(run, ref):
    return {'directory': str(run), 'artifact': ref}



def operation_record(run, record, *, code_root=None):
    """Encode a verified operation-local record or the exact captured proposal role."""
    folder, ref = _artifact_record(record, verify=False)
    path = folder/ref.path
    if code_root is not None and path == code_root/REPLAY_PROPOSAL:
        return {'scope': 'captured-proposal', 'artifact': asdict(ArtifactRef(
            REPLAY_PROPOSAL, ref.sha256, ref.size))}
    _require(path.is_relative_to(run) and path != run, 'foreign operation artifact')
    return {'scope': 'operation', 'artifact': asdict(ArtifactRef(
        path.relative_to(run).as_posix(), ref.sha256, ref.size))}


def resolve_operation_record(run, record, *, code_root=None):
    """Resolve only the two defined authorities; never search for matching bytes."""
    _require(type(record) is dict and set(record) == {'scope', 'artifact'},
             'invalid operation artifact record')
    value = record['artifact']
    _require(type(value) is dict and set(value) == {'path', 'sha256', 'size'},
             'invalid operation artifact reference')
    ref = ArtifactRef(**value)
    if record['scope'] == 'captured-proposal':
        _require(code_root is not None and ref.path == REPLAY_PROPOSAL,
                 'unbound captured proposal')
        root = code_root
    else:
        _require(record['scope'] == 'operation', 'unknown operation artifact scope')
        root = run
    path = _safe(root, ref.path)
    if root == run and ref.path == 'coordinator/nodes/'+ref.sha256+'.json':
        return _reference(run, value)
    return _reference(path.parent, asdict(ArtifactRef(path.name, ref.sha256, ref.size)))


def operation_inputs(run, inputs, *, code_root=None, decode=False):
    _require(type(inputs) is dict, 'invalid phase predecessor mapping')
    transform = resolve_operation_record if decode else operation_record
    result = {}
    for stage, outputs in inputs.items():
        _require(stage in PHASES and type(outputs) is dict, 'invalid phase predecessor outputs')
        result[stage] = {name: transform(run, record, code_root=(
            code_root if stage == 'proposal' and name == 'proposal' else None))
            for name, record in outputs.items()}
    return result


def _payload_paths(run, payload, code_root, *, encode):
    def bind(record, *, proposal=False):
        transform = operation_record if encode else resolve_operation_record
        return transform(run, record, code_root=code_root if proposal else None)

    _require(type(payload) is dict and {'phase', 'directory', 'inputs', 'predecessors'} <= set(payload),
             'invalid phase node payload')
    phase = payload['phase']
    _require(type(phase) is str and phase in PHASES, 'unknown coordinator phase')
    directory = payload['directory']
    if encode:
        directory = _attempt_directory(run, phase, directory).relative_to(run).as_posix()
    else:
        _require(type(directory) is str and re.fullmatch(phase+r'/attempts/[0-9a-f]{32}', directory),
                 'foreign phase attempt directory')
        directory = str(run/directory)
    def mapping(stage, outputs):
        _require(type(outputs) is dict, 'invalid phase output mapping')
        return {name: bind(record, proposal=stage == 'proposal' and name == 'proposal')
                for name, record in outputs.items()}
    _require(type(payload['predecessors']) is dict, 'invalid phase predecessors')
    result = {**payload, 'directory': directory,
              'inputs': operation_inputs(run, payload['inputs'], code_root=code_root, decode=not encode),
              'predecessors': {stage: bind(record) for stage, record in payload['predecessors'].items()}}
    if 'intent' in payload:
        result['intent'] = bind(payload['intent'])
    if 'outputs' in payload:
        result['outputs'] = mapping(phase, payload['outputs'])
    return result

def _node_ref(run, record):
    root, ref = _artifact_record(record, verify=False)
    _require(root == run and ref.path == 'coordinator/nodes/'+ref.sha256+'.json' and ref.size <= FILE_BYTES,
             'foreign coordinator node reference')
    return ref


def _attempt_directory(run, phase, value):
    path = _absolute(value)
    _require(path.parent == run/phase/'attempts' and re.fullmatch('[0-9a-f]{32}', path.name) is not None,
             'foreign phase attempt directory')
    _root_path(path, missing=True)
    return path


def _check_context(context):
    _require(type(context) is dict and set(context) == {
        'problem_id', 'configuration', 'implementation', 'proposal_input'}, 'invalid coordinator context')
    _require(type(context['problem_id']) is str and re.fullmatch('[0-9a-f]{64}', context['problem_id']) is not None
             and type(context['configuration']) is dict, 'invalid coordinator scientific context')
    _artifact_record(context['implementation'])
    if context['proposal_input'] is not None:
        _artifact_record(context['proposal_input'])


def _context_paths(run, context, code_root, *, encode):
    _require(type(context) is dict and set(context) == {
        'problem_id', 'configuration', 'implementation', 'proposal_input'}, 'invalid coordinator context')
    transform = operation_record if encode else resolve_operation_record
    start = transform(run, context['implementation'])
    _require(start['artifact']['path'] == ('implementation/start.json' if encode else 'start.json')
             and (encode or start['directory'] == str(run/'implementation')),
             'foreign coordinator implementation start')
    proposal = context['proposal_input']
    if proposal is not None:
        proposal = transform(run, proposal, code_root=code_root)
        _require(code_root is not None and (proposal['scope'] == 'captured-proposal' if encode else
                 proposal['directory'] == str(code_root/'replay-inputs') and
                 proposal['artifact']['path'] == 'proposal.json'), 'foreign captured proposal')
    return {**context, 'implementation': start, 'proposal_input': proposal}


def _node_schema(run, document, context_sha256, format_id):
    _require(type(document) is dict and set(document) == {
        'format', 'context_sha256', 'previous', 'kind', 'payload'} and document['format'] == format_id
        and document['context_sha256'] == context_sha256 and document['kind'] in ('intent', 'completion'),
        'invalid coordinator node')
    if document['previous'] is not None:
        _node_ref(run, document['previous'])
    payload = document['payload']
    common = {'phase', 'directory', 'inputs', 'predecessors'}
    _require(type(payload) is dict and set(payload) == (
        common if document['kind'] == 'intent' else common | {'intent', 'outputs'}), 'invalid phase node payload')
    phase = payload['phase']
    _require(type(phase) is str and phase in PHASES, 'unknown coordinator phase')
    _attempt_directory(run, phase, payload['directory'])
    _require(type(payload['inputs']) is dict and type(payload['predecessors']) is dict,
             'invalid phase predecessor mapping')
    for record in payload['predecessors'].values():
        _node_ref(run, record)
    if document['kind'] == 'completion':
        _node_ref(run, payload['intent'])
        _require(type(payload['outputs']) is dict and set(payload['outputs']) == _OUTPUTS[phase],
                 'incorrect phase output roles')
        for record in payload['outputs'].values():
            _artifact_record(record, verify=False)


def _head(document, context_sha256, format_id):
    fields = {'format', 'context_sha256', 'count', 'tip'}
    if format_id == FORMAT:
        fields.add('operation_id')
    _require(type(document) is dict and set(document) == fields
             and document['format'] == format_id and document['context_sha256'] == context_sha256
             and type(document['count']) is int and 0 <= document['count'] <= MAX_NODES
             and ((document['count'] == 0) == (document['tip'] is None)), 'invalid committed coordinator head')
    return document


def _load(run, code_root):
    """Bound the complete journal, then reconstruct only committed authority."""
    wire = _read(run, 'coordinator/context.json', FILE_BYTES)
    _require(type(wire) is dict, 'invalid coordinator context')
    format_id = wire.get('format')
    key = 'operation_id' if format_id == FORMAT else 'run'
    _require(set(wire) == {'format', key, 'python', 'phases', 'context'}
             and (format_id == FORMAT and type(wire[key]) is str
                  and re.fullmatch('[0-9a-f]{32}', wire[key]) is not None
                  or format_id == _LEGACY_FORMAT and wire[key] == str(run))
             and wire['python'] == sys.version and wire['phases'] == list(PHASES),
             'changed coordinator path, Python or phase context')
    context = (_context_paths(run, wire['context'], code_root, encode=False)
               if format_id == FORMAT else wire['context'])
    _check_context(context)
    document = {**wire, 'context': context}
    context_sha256 = _digest(canonical_bytes(wire))
    head = _head(_read(run, 'coordinator/head.json', HEAD_BYTES), context_sha256, format_id)
    if format_id == FORMAT:
        _require(head['operation_id'] == wire['operation_id'], 'foreign coordinator head')
        if head['tip'] is not None:
            head = {**head, 'tip': resolve_operation_record(run, head['tip'])}
    nodes, resident = {}, python_bytes(document)+python_bytes(head)+HEAD_BYTES
    _require(resident <= METADATA_BYTES, 'coordinator decoded journal allowance exceeded')
    folder = _safe(run, 'coordinator/nodes')
    _root_path(folder)
    with os.scandir(folder) as entries:
        for entry in entries:
            _require(len(nodes) < MAX_NODES and re.fullmatch('[0-9a-f]{64}\\.json', entry.name) is not None,
                     'excessive or unknown coordinator journal node')
            name = 'coordinator/nodes/'+entry.name
            node = _read(run, name, FILE_BYTES)
            raw = canonical_bytes(node)
            _require(_digest(raw)+'.json' == entry.name, 'corrupt immutable coordinator node')
            if format_id == FORMAT:
                _require(type(node) is dict and {'previous', 'payload'} <= set(node),
                         'invalid coordinator node')
                previous = node['previous']
                node = {**node,
                        'previous': None if previous is None else resolve_operation_record(run, previous),
                        'payload': _payload_paths(run, node['payload'], code_root, encode=False)}
            _node_schema(run, node, context_sha256, format_id)
            ref = asdict(ArtifactRef(name, _digest(raw), len(raw)))
            resident += python_bytes(node)+python_bytes(ref)+python_bytes(name)+512
            _require(resident <= METADATA_BYTES, 'coordinator decoded journal allowance exceeded')
            nodes[name] = (ref, node)
    # Interrupted head temporaries are never authority and remain retained.
    with os.scandir(run/'coordinator') as entries:
        for entry in entries:
            if entry.name in ('context.json', 'head.json', 'nodes'):
                continue
            _require(re.fullmatch(r'\.head-[0-9a-f]{32}\.json', entry.name) is not None,
                     'unknown coordinator journal member')
            path = _safe(run, 'coordinator/'+entry.name)
            info = path.stat()
            _require(stat.S_ISREG(info.st_mode) and info.st_size <= HEAD_BYTES, 'unsafe coordinator head temporary')
            resident += info.st_size+512
            _require(resident <= METADATA_BYTES, 'coordinator decoded journal allowance exceeded')
    chain, seen, record = [], set(), head['tip']
    while record is not None:
        ref = _node_ref(run, record)
        _require(ref.path not in seen and len(chain) < MAX_NODES, 'cyclic coordinator journal')
        seen.add(ref.path)
        _require(ref.path in nodes and nodes[ref.path][0] == asdict(ref), 'missing or changed committed coordinator node')
        node = nodes[ref.path][1]
        chain.append((record, node))
        record = node['previous']
    _require(len(chain) == head['count'], 'incomplete committed coordinator chain')
    completed, pending, directories = {}, None, set()
    for record, node in reversed(chain):
        payload = node['payload']
        phase = payload['phase']
        _require(len(completed) < len(PHASES) and phase == PHASES[len(completed)], 'incorrect phase order')
        inputs = {name: row['outputs'] for name, row in completed.items()}
        predecessors = {name: row['record'] for name, row in completed.items()}
        _require(payload['inputs'] == inputs and payload['predecessors'] == predecessors,
                 'changed phase predecessor binding')
        if node['kind'] == 'intent':
            _require(payload['directory'] not in directories, 'ambiguous repeated phase attempt')
            directories.add(payload['directory'])
            pending = {**payload, 'record': record}
        else:
            _require(pending is not None and payload['intent'] == pending['record']
                     and all(payload[key] == pending[key] for key in ('phase', 'directory', 'inputs', 'predecessors')),
                     'ambiguous or unmatched phase completion')
            for output in payload['outputs'].values():
                _artifact_record(output)
            completed[phase] = {**payload, 'record': record}
            pending = None
    return document, head, nodes, resident, completed, pending


def read_phase_selection(run, *, code_root=None):
    """Read the strict committed selection and hash every selected output."""
    run = _absolute(str(Path(run).absolute()))
    code_root = None if code_root is None else _absolute(str(Path(code_root).absolute()))
    _root_path(run)
    try:
        state = _load(run, code_root)
        return state[0]['context'], state[4]
    except OSError as exc:
        raise ContractError('missing or unreadable coordinator authority') from exc


def read_phase_records(run, *, code_root=None):
    return read_phase_selection(run, code_root=code_root)[1]


class PhaseJournal:
    """Append immutable intents/completions under the caller's operation lock.

    ``begin`` never creates an attempt leaf. Its boolean is true only when the
    caller explicitly requests reuse of the current matching pending intent.
    Inputs map each completed predecessor phase to its selected output mapping.
    Completed phases cannot begin again. Fresh retry retains every earlier intent
    and attempt. Exposed rows are snapshots, never mutable publication authority.
    """
    def __init__(self, run, context, *, resume=False, code_root=None):
        self.run = _absolute(str(Path(run).absolute()))
        self.code_root = None if code_root is None else _absolute(str(Path(code_root).absolute()))
        _root_path(self.run)
        _check_context(context)
        bound = _context_paths(self.run, context, self.code_root, encode=True)
        folder = _safe(self.run, 'coordinator', missing=True)
        if folder.exists():
            _require(resume, 'coordinator already exists; explicit resume required')
        else:
            folder.mkdir()
        context_path = _safe(self.run, 'coordinator/context.json', missing=True)
        if not context_path.exists():
            # Head first, context last. Only the empty initialization may recover.
            head_path = _safe(self.run, 'coordinator/head.json', missing=True)
            prior = _read(self.run, 'coordinator/head.json', HEAD_BYTES) if head_path.exists() else None
            operation_id = prior.get('operation_id') if type(prior) is dict else uuid.uuid4().hex
            _require(type(operation_id) is str and re.fullmatch('[0-9a-f]{32}', operation_id) is not None,
                     'invalid unbound coordinator identity')
            expected = _snapshot({'format': FORMAT, 'operation_id': operation_id, 'python': sys.version,
                                  'phases': list(PHASES), 'context': bound})
            initial = {'format': FORMAT, 'operation_id': operation_id,
                       'context_sha256': _digest(canonical_bytes(expected)), 'count': 0, 'tip': None}
            nodes = _safe(self.run, 'coordinator/nodes', missing=True)
            nodes.mkdir(exist_ok=True)
            _root_path(nodes)
            _require(not any(nodes.iterdir()), 'unbound coordinator journal nodes')
            if head_path.exists():
                _require(prior == initial,
                         'conflicting unbound coordinator head')
            else:
                self._replace_head(initial)
            self._exclusive(context_path, canonical_bytes(expected))
        try:
            self._refresh()
        except OSError as exc:
            raise ContractError('missing or unreadable coordinator authority') from exc
        _require(self.document['format'] == FORMAT and self.context == context,
                 'incompatible coordinator resume context or read-only legacy journal')

    def _refresh(self):
        state = _load(self.run, self.code_root)
        self.document, self.head, self.nodes, self.resident, self.completed, self.pending = state
        self.context = self.document['context']

    @staticmethod
    def _exclusive(path, raw):
        with guarded_open(path) as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        _sync_directory(path.parent)

    def _replace_head(self, head):
        temporary = self.run/'coordinator'/('.head-'+uuid.uuid4().hex+'.json')
        self._exclusive(temporary, canonical_bytes(head))
        replace_path_with_permission_retry(temporary, self.run/'coordinator/head.json')
        _sync_directory(self.run/'coordinator')

    def _check(self):
        old_document, old_head = self.document, self.head
        try:
            self._refresh()
        except OSError as exc:
            raise ContractError('missing or unreadable coordinator authority') from exc
        _require(self.document == old_document and self.head == old_head, 'changed active coordinator context or head')

    def _append(self, kind, payload):
        node = {'format': FORMAT, 'context_sha256': self.head['context_sha256'],
                'previous': self.head['tip'], 'kind': kind, 'payload': payload}
        wire = {**node, 'payload': _payload_paths(self.run, payload, self.code_root, encode=True)}
        if wire['previous'] is not None:
            wire['previous'] = operation_record(self.run, wire['previous'])
        raw = canonical_bytes(wire)
        _require(len(raw) <= FILE_BYTES, 'coordinator metadata file allowance exceeded')
        name = 'coordinator/nodes/'+_digest(raw)+'.json'
        ref = asdict(ArtifactRef(name, _digest(raw), len(raw)))
        charge = python_bytes(node)+python_bytes(ref)+python_bytes(name)+512
        _require(self.head['count'] < MAX_NODES and self.resident+charge <= METADATA_BYTES,
                 'coordinator journal allowance exceeded')
        if name in self.nodes:
            _require(self.nodes[name] == (ref, node), 'conflicting immutable coordinator node')
        else:
            _require(len(self.nodes) < MAX_NODES, 'coordinator node allowance exceeded')
            self._exclusive(self.run/name, raw)
        head = {**self.head, 'count': self.head['count']+1,
                'tip': operation_record(self.run, _reference(self.run, ref))}
        self._replace_head(head)
        self._refresh()
        return _reference(self.run, ref)

    def begin(self, phase, inputs, *, reuse=False):
        self._check()
        _require(type(phase) is str and phase in PHASES and phase not in self.completed
                 and len(self.completed) < len(PHASES) and phase == PHASES[len(self.completed)],
                 'incorrect phase order or already completed phase')
        inputs = _snapshot(inputs)
        expected = {name: row['outputs'] for name, row in self.completed.items()}
        _require(inputs == expected, 'changed phase predecessor inputs')
        if reuse:
            _require(self.pending is not None and self.pending['phase'] == phase and self.pending['inputs'] == inputs,
                     'no matching pending phase intent')
            return Path(self.pending['directory']), True
        parent = self.run/phase
        _root_path(parent, missing=True)
        parent.mkdir(exist_ok=True)
        attempts = parent/'attempts'
        _root_path(attempts, missing=True)
        attempts.mkdir(exist_ok=True)
        directory = attempts/uuid.uuid4().hex
        _require(not directory.exists() and all(node['payload']['directory'] != str(directory)
                 for _, node in self.nodes.values()), 'phase attempt directory already exists')
        payload = {'phase': phase, 'directory': str(directory), 'inputs': inputs,
                   'predecessors': {name: row['record'] for name, row in self.completed.items()}}
        self._append('intent', payload)
        return directory, False

    def complete(self, phase, outputs):
        self._check()
        _require(self.pending is not None and self.pending['phase'] == phase and phase not in self.completed,
                 'no matching pending phase intent')
        outputs = _snapshot(outputs)
        _require(type(outputs) is dict and set(outputs) == _OUTPUTS[phase], 'incorrect phase output roles')
        for record in outputs.values():
            _artifact_record(record)
        payload = {key: self.pending[key] for key in ('phase', 'directory', 'inputs', 'predecessors')}
        payload.update(intent=self.pending['record'], outputs=outputs)
        for _, node in self.nodes.values():
            if node['kind'] == 'completion' and node['payload']['intent'] == self.pending['record']:
                _require(node['payload'] == payload, 'ambiguous conflicting orphan phase completion')
        self._append('completion', payload)
        return self.completed[phase]
