"""Prospective operational accounts; never mathematical acceptance or a reservation.

The accounts deliberately price legal writer ceilings, not extrapolated peaks.
A phase may refuse on a small host even when a less conservative account could
fit. Complete numerical qualification is separate from metadata admission.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import sys

from scripts.whole_source.contract import ROOT, ContractError, canonical_bytes, problem_id

MIB = 1024*1024
FORMAT = 'whole-source-phase-admission-v2'
LEGACY_FORMAT = 'whole-source-phase-admission-v1'
POLICY = 'bounded-phase-resources-v1'
_ENV = 'RH_WHOLE_SOURCE_CALLER_ACCOUNT'
_PROBE = ContextVar('whole_source_caller_probe', default=None)
_PHASES = frozenset(('prepare', 'source', 'audit', 'proposal', 'exact-inputs', 'exact',
                     'controls', 'replay', 'review', 'assessment', 'retention', 'validation'))
_REPORT_FIELDS = frozenset(('format', 'policy', 'phase', 'problem_id', 'inputs', 'caller',
                            'storage', 'lifetime', 'supervision', 'mathematical_acceptance',
                            'reservation', 'attempt_id'))


def _require(value, message):
    if not value:
        raise ContractError(message)


def _positive(value, name, minimum=1):
    _require(type(value) is int and minimum <= value <= 1 << 60, 'invalid '+name)
    return value


def decoded_bound(raw_bytes):
    """Conservative CPython-64 canonical JSON object/slot/string expansion.

    A minimal JSON container costs at least two input bytes. 128 bytes per raw
    byte covers container overhead, dict/list slots, scalar objects, UTF-32
    storage and parser/encoding overlap. This is a codec account, not a claim
    that arbitrary native library allocations have this ratio.
    """
    _positive(raw_bytes, 'raw decoder bytes', 0)
    _require(sys.implementation.name == 'cpython' and struct.calcsize('P') == 8,
             'caller codec account requires 64-bit CPython')
    return 128*raw_bytes + 4096


def caller_account(phase, *, metadata_bytes=0, file_count=0, path_bytes=0, capture_bytes=0):
    _require(phase in _PHASES, 'unknown resource-account phase')
    for name, value in (('metadata bytes', metadata_bytes), ('file count', file_count),
                        ('path bytes', path_bytes), ('capture bytes', capture_bytes)):
        _positive(value, name, 0)
    # Full path/reference lists, sorted copies and inventory/review membership
    # maps can coexist. Numerical payloads are streamed, not charged as a full
    # decoded matrix. Existing per-collection catalogs have their own account.
    references = 8*(path_bytes+file_count*1024)
    parts = {'runtime_and_import_bytes': 128*MIB,
             'bounded_decoders_bytes': decoded_bound(8*MIB),
             'journal_and_catalog_bytes': 3*16*MIB,
             'capture_bytes': 3*capture_bytes,
             'retained_metadata_bytes': decoded_bound(metadata_bytes),
             'filename_and_reference_bytes': references,
             'stream_and_copy_bytes': 4*MIB}
    return {'phase': phase, 'components': parts, 'required_bytes': sum(parts.values()),
            'basis': 'bounded-future-growth-v1',
            'measured_peak': False, 'os_enforced': False}


def topology(problem, *, tile_modes=32, cpu_limit=61):
    """Closed full-shape writer lifetime, without importing a numerical backend.

    Caps are allowed cumulative growth, not expected physical consumption.
    Operand-dependent exact demand remains pending until actual preparation.
    """
    _require(problem.profile == 'retained-t081' and tile_modes in (16, 32),
             'unqualified phase resource geometry')
    _positive(cpu_limit, 'CPU limit')
    n, h = problem.N//2, (problem.M-problem.N)//2
    q, k = (n+tile_modes-1)//tile_modes, (h+tile_modes-1)//tile_modes
    triangular = q*(q+1)//2
    source_tasks = 2*(min(cpu_limit, len(problem.frequency_edges)) + k +
                      2*((n+1)//2) + triangular)
    source_stages = 10
    from scripts.whole_source.proposal import _proposal_accounts
    proposal = _proposal_accounts(n, tile_modes)
    # Each task has a bounded input/result, completion and dependency record.
    # Runtime capture is per execution owner (not per numerical task).
    capture = sum(ref.size for ref in problem.evidence) + 64*MIB
    source_payload = (2*h*(h+1)//2 + problem.N*(problem.M//2+2*h) + 3*n*(n+1))
    endpoint_record = 2*((8192+3)//4+6)+64
    source_wire = source_payload*endpoint_record + (6*problem.N+12*triangular)*4096
    source_evidence = source_tasks*(128*1024+MIB+4096) + source_stages*(4*MIB+8*MIB)
    source = min(8192*MIB, 2*source_wire+source_evidence+2*capture)
    proposal_bytes = 2*(proposal['per_parity_panel_disk_bytes']+proposal['retained_graph_bytes'])
    proposal_bytes += 2*max(proposal['native_staging_bytes'], proposal['floating_staging_bytes']) + 4*capture
    # Exact's local repository cap is a hard allowed maximum, NOT an operand
    # estimate. A later actual-operand admission must independently pass.
    exact_ceiling = 8192*MIB
    scalar = 10*capture + 8*(128*1024+MIB+12*MIB)
    variants = 8*(3*n*(n+1)*endpoint_record + 2*capture)
    controls = variants + 3*exact_ceiling + source_evidence + 2*capture
    science = scalar + 2*source + proposal_bytes + exact_ceiling + 2*capture
    # One fresh retry per phase. Every failed byte remains charged. Replay
    # reconstructs science; controls are not repeated inside replay.
    phases = {'prepare': scalar, 'source': source, 'audit': source,
              'proposal': proposal_bytes, 'exact-inputs': 2*capture+2*n*n*(8192//4+64),
              'exact': exact_ceiling, 'controls': controls, 'replay': science+2*capture+8*MIB}
    # External review/assessment, bounded observations and two pending/final
    # inventory generations are explicit lifetime charges, not absent zeros.
    external = {'review': 16*MIB, 'assessment': exact_ceiling,
                'telemetry': 16*MIB,
                'inventory': 4*262144*(6*1024+256)+16*MIB}
    return {'format': 'whole-source-lifetime-account-v1', 'problem_id': problem_id(problem),
            'geometry': {'N': problem.N, 'M': problem.M, 'K': problem.K, 'tile_modes': tile_modes},
            'source_tasks': source_tasks, 'source_stages': source_stages,
            'phase_growth_bytes': phases, 'external_growth_bytes': external,
            'attempts_per_phase': 2, 'remaining_exact_basis': 'LOCAL_CEILING_NOT_ACTUAL_OPERANDS',
            'logical_allowance_bytes': 2*sum(phases.values())+2*sum(external.values())+1024*9*MIB,
            'physical_forecast_kind': 'CONSERVATIVE_ALLOWED_GROWTH_NOT_REQUIRED_USAGE',
            'hardlink_discount': False, 'reservation': False}


def current_commit(helper_root, *, pid=None):
    from scripts.whole_source.execution import neutral_helpers
    probe = _PROBE.get()
    limits = probe[2] if probe is not None and probe[0] == Path(helper_root).resolve() else neutral_helpers(helper_root)[1]
    _require(os.name == 'nt', 'caller commitment admission requires qualified Windows counters')
    if pid is None or pid == os.getpid():
        sample = limits.windows_resource_snapshot()['process']
    else:
        kernel, psapi = limits._windows_api()
        handle = kernel.OpenProcess(0x1000 | 0x10, False, pid)
        _require(handle, 'caller process is unavailable')
        try:
            sample = limits._process_memory(psapi, handle)
        finally:
            kernel.CloseHandle(handle)
    _require(type(sample) is dict, 'caller commitment unavailable')
    return _positive(sample.get('committed_bytes'), 'caller commitment', 0)


def admit_caller(account, detected, *, existing_bytes):
    from scripts.whole_source.supervision import constrain_detection
    detected = constrain_detection(detected)
    _positive(existing_bytes, 'existing caller bytes', 0)
    from scripts.whole_source.resources import _cpu_limit
    _require(detected.get('cpu_detection_complete') is True and
             detected.get('memory_detection_complete') is True, 'incomplete phase resource discovery')
    cpus = _cpu_limit(detected)
    future = max(0, account['required_bytes']-existing_bytes)
    available = detected.get('available_memory_bytes')
    _positive(available, 'available phase memory', 0)
    reserve = max(128*MIB, (available+9)//10)
    sources = detected.get('memory_sources') or [{'source': 'available_memory', 'available_bytes': available}]
    for source in sources:
        free = _positive(source.get('available_bytes'), 'memory constraint', 0)
        _require(free >= future+reserve, 'phase caller/preparation account exceeds live memory: '+source['source'])
    return {'detected': detected, 'cpus': cpus, 'existing_caller_bytes': existing_bytes,
            'future_caller_bytes': future, 'reserve_bytes': reserve, 'account': account}


def _context():
    raw = os.environ.get(_ENV)
    if raw is None:
        return []
    _require(len(raw) <= 4096, 'oversized caller context')
    value = json.loads(raw)
    _require(type(value) is list and 1 <= len(value) <= 2, 'invalid caller resource context')
    seen = set()
    for row in value:
        _require(type(row) is dict and set(row) == {'pid', 'required_bytes'}, 'invalid caller resource context')
        for name, number in row.items():
            _positive(number, 'caller '+name)
        _require(row['pid'] not in seen, 'duplicate caller resource charge')
        seen.add(row['pid'])
    return value


def caller_future(*, helper_root, external_bytes=0):
    """Charge concurrent callers once; host availability excludes live bytes."""
    rows = _context()
    if not rows:
        return external_bytes
    total = 0
    for index, value in enumerate(rows):
        current = current_commit(helper_root, pid=value['pid'])
        growth = max(0, value['required_bytes']-current)
        # The last coordinator is the numerical job's external supervisor,
        # even when this query executes inside one of its numerical children.
        total += max(external_bytes, growth) if index == len(rows)-1 else growth
    return total


@contextmanager
def caller_scope(account, *, helper_root, detected=None):
    from scripts.whole_source.execution import neutral_helpers, exact_telemetry
    resources, limits, _, _ = neutral_helpers(helper_root)
    token = _PROBE.set((Path(helper_root).resolve(), resources, limits))
    previous = os.environ.get(_ENV)
    try:
        existing = current_commit(helper_root)
        detection = exact_telemetry(resources.detect_resources() if detected is None else detected)
        resolved = dict(account)
        if account.get('basis') == 'bounded-future-growth-v1':
            resolved['required_bytes'] += existing
            resolved['components'] = {**account['components'], 'already_live_bytes': existing}
        ancestors = [row for row in _context() if row['pid'] != os.getpid()]
        _require(len(ancestors) < 2, 'unsupported concurrent caller depth')
        ancestor_growth = sum(max(0, row['required_bytes']-current_commit(helper_root, pid=row['pid']))
                              for row in ancestors)
        combined = {**resolved, 'required_bytes': resolved['required_bytes']+ancestor_growth}
        report = admit_caller(combined, detection, existing_bytes=existing)
        report['ancestor_future_bytes'] = ancestor_growth
        os.environ[_ENV] = json.dumps([*ancestors, {'pid': os.getpid(),
            'required_bytes': resolved['required_bytes']}], separators=(',', ':'))
        yield report
    finally:
        if previous is None:
            os.environ.pop(_ENV, None)
        else:
            os.environ[_ENV] = previous
        _PROBE.reset(token)


@contextmanager
def waiting_caller(*, helper_root):
    """Replay comparison is sequential; only bounded pipe copying overlaps."""
    previous = os.environ.get(_ENV)
    rows = [row for row in _context() if row['pid'] != os.getpid()]
    rows.append({'pid': os.getpid(), 'required_bytes': current_commit(helper_root)+4*MIB})
    os.environ[_ENV] = json.dumps(rows, separators=(',', ':'))
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(_ENV, None)
        else:
            os.environ[_ENV] = previous


MAX_FILES = 262144
MAX_PATH_BYTES = 1024
_ID = re.compile('[0-9a-f]{32}')
_STORAGE_FILE = re.compile(r'storage-([a-z-]+?)(?:-([0-9a-f]{64}))?-([0-9a-f]{32})(-bound)?\.json')


def _external_path(path, run, root):
    from scripts.whole_source.storage import _inspect
    _inspect(path)
    _require(path.is_relative_to(root) and not path.is_relative_to(run) and
             not run.is_relative_to(path), 'external resource output overlaps operation')
    return path


def _storage_history(run, root, operation_id, output):
    from scripts.whole_source import storage
    owner = storage.owner_binding(run, root)
    run_binding = storage.root_binding(owner, run)
    expected, locations = set(), {}
    targets = {'review': set(), 'assessment': set()}
    for path in storage.retained_root_locations():
        _external_path(path, run, root)
        identity = storage.root_binding(owner, path)
        _require(identity not in locations, 'aliased retained storage roots')
        locations[identity] = path
    if output is not None and output.exists():
        locations.setdefault(storage.root_binding(owner, output), output)

    folder = run/'admission'
    storage._inspect(folder)
    if not folder.exists():
        return set(), targets, owner
    policies = 0
    with os.scandir(folder) as entries:
        for entry in entries:
            if not entry.name.casefold().startswith('storage-') or not entry.name.casefold().endswith('.json'):
                continue
            policies += 1
            _require(policies < 1024, 'retained admission policy allowance exhausted')
            name = _STORAGE_FILE.fullmatch(entry.name)
            _require(name and name[1] in _PHASES, 'invalid retained storage policy name')
            phase = name[1]
            path = Path(entry.path)
            raw = storage._policy_bytes(path)
            doc = storage._decode(raw)
            if doc.get('format') == storage.LEGACY_FORMAT:
                _require(name[4] is None, 'invalid historical storage policy name')
                # Frozen v1 policies carry their own locations. Do not rewrite them.
                _require(doc.get('operation_id') == operation_id and doc.get('code_root') == str(root) and
                         doc.get('policy_path') == str(path) and type(doc.get('roots')) is list and
                         0 < len(doc['roots']) <= 7, 'unbound retained resource policy')
                seen = set()
                for row in doc['roots']:
                    _require(type(row) is dict and type(row.get('path')) is str,
                             'invalid historical storage root')
                    location = storage._absolute(row['path'])
                    _require(location not in seen, 'duplicate historical storage root')
                    seen.add(location)
                    if location == run:
                        continue
                    _external_path(location, run, root)
                    identity = location
                    if location.exists():
                        identity = storage.root_binding(owner, location)
                        locations[identity] = location
                        expected.add(identity)
                    if phase in targets and name[2] == hashlib.sha256(row['path'].encode('utf-8')).hexdigest():
                        targets[phase].add(identity)
                _require(run in seen, 'unbound retained resource policy')
            else:
                _require(name[2] is None, 'invalid retained storage policy name')
                storage.retained_policy(raw, path, doc, run=run, owner=owner,
                                        run_binding=run_binding, operation_id=operation_id)
                expected.update(row['binding_sha256'] for row in doc['roots'][1:])
                destination = doc['external_target']
                _require(doc['pending_external_ceiling'] is None or phase in targets,
                         'unbound prospective storage destination')
                _require(name[4] is None or destination is not None, 'missing bound storage destination')
                if destination is not None:
                    _require(phase in targets, 'unbound retained storage destination')
                    targets[phase].add(destination)
            _require(len(expected) <= 6, 'too many retained external resource roots')
            _require(all(len(items) <= 2 for items in targets.values()), 'external retry allowance exhausted')
    _require(expected <= locations.keys(), 'missing private locations for retained storage roots')
    return {locations[identity] for identity in expected}, targets, owner


def operation_budget(problem, run, root, *, phase, external=None, resume_external=False):
    """Price the next phase against retained history, not all future phases at once.

    The caller holds the operation slice lock. Earlier external roots remain
    included read-only; new external destinations consume the same retained
    lifetime allowance. A later phase always undergoes a new live admission.
    """
    from scripts.whole_source.storage import StorageBudget, _absolute, _census, _volume, root_binding
    from scripts.whole_source.supervision import require_current
    supervision = require_current()
    observation_headroom = _positive(supervision['observation_bytes'], 'observer storage headroom')
    _require(observation_headroom <= 16*MIB, 'observer storage allowance exceeds lifecycle policy')
    run, root = _absolute(Path(run).absolute()), _absolute(Path(root).absolute())
    output = None if external is None else _external_path(Path(external).absolute(), run, root)
    _require((output is not None) == (phase in ('review', 'assessment', 'retention')) and
             (not resume_external or phase == 'assessment'), 'invalid external storage phase')
    operation_id = problem_id(problem)
    forecast = topology(problem)
    previous, destinations, owner = _storage_history(run, root, operation_id, output)
    reserve = False
    if output is not None:
        if phase == 'retention' or resume_external:
            _require(output in previous and root_binding(owner, output) in destinations['assessment'],
                     'external assessment storage lacks original ownership')
        else:
            _require(not output.exists(), 'external resource output already exists')
            _require(output in destinations[phase] or len(destinations[phase]) < 2,
                     'external retry allowance exhausted')
            reserve = True
        previous.add(output)
    _require(len(previous) <= 6, 'too many retained external resource roots')
    roots = {}
    existing_total = 0
    for path in (run, *previous):
        row = _census(path, _volume(path), MAX_FILES, MAX_PATH_BYTES)
        existing_total += row['logical_bytes']
        roots[path] = row['logical_bytes']
    _require(existing_total <= forecast['logical_allowance_bytes'], 'retained lifetime allowance exhausted')
    metadata = 32*MIB
    if phase in forecast['phase_growth_bytes']:
        growth = forecast['phase_growth_bytes'][phase]+metadata
    elif phase in ('assessment', 'retention'):
        growth = forecast['external_growth_bytes']['inventory']+metadata
    elif phase in ('review', 'validation'):
        growth = 2*(sum(ref.size for ref in problem.evidence)+64*MIB)+metadata
    else:
        raise ContractError('unknown storage admission phase')
    roots[run] += growth
    if output is not None and phase in ('assessment', 'review'):
        roots[output] += forecast['external_growth_bytes'][phase]
    _require(sum(roots.values()) <= forecast['logical_allowance_bytes'],
             'next phase exceeds retained lifetime allowance')
    import uuid
    destination = output if phase in ('review', 'assessment') else None
    # The guardian's sibling root can still grow concurrently on this volume.
    # Reserve its full policy ceiling as headroom, not extra scientific quota.
    return StorageBudget(roots, operation_id=operation_id, run_root=run,
        policy_path=run/'admission'/('storage-'+phase+'-'+uuid.uuid4().hex+'.json'),
        min_free_bytes=64*MIB+observation_headroom, max_files=MAX_FILES, max_path_bytes=MAX_PATH_BYTES,
        code_root=root, external_target=destination, reserve_external=reserve), forecast


def phase_caller_account(phase, problem, *, run=None):
    from scripts.whole_source.storage import _census, _volume
    capture = sum(ref.size for ref in problem.evidence)+64*MIB
    rows = {'file_count': 0, 'path_bytes': 0}
    if run is not None:
        rows = _census(Path(run), _volume(Path(run)), MAX_FILES, MAX_PATH_BYTES)
    return caller_account(phase, file_count=rows['file_count'],
                          path_bytes=rows['path_bytes'], capture_bytes=capture)


def _retained_caller(memory):
    from scripts.whole_source.supervision import _observed_upstream
    detected = memory['detected']
    retained = _observed_upstream(detected, cpus=memory['cpus'],
                                  available=detected['available_memory_bytes'],
                                  reserve=memory['reserve_bytes'])
    return {'detected': retained, **{key: memory[key] for key in (
        'cpus', 'existing_caller_bytes', 'future_caller_bytes', 'reserve_bytes',
        'ancestor_future_bytes', 'account')}}


def _attempt_id(directory, run):
    from scripts.whole_source.storage import _inspect
    directory, run = Path(directory).absolute(), Path(run).absolute()
    _inspect(directory)
    _require(directory.parent.name == 'attempts' and directory.parent.parent.parent == run and
             directory.parent.parent.name in _PHASES and _ID.fullmatch(directory.name),
             'invalid admitted phase attempt')
    return directory.name


def _write_admission(path, report):
    from scripts.whole_source.execution import _write
    raw = canonical_bytes(report)
    _require(len(raw) <= 8*MIB, 'phase admission record exceeds codec')
    _write(path, raw)


@contextmanager
def admitted_phase(phase, problem, run, root, *, directory=None, inputs=None, external=None,
                   resume_external=False):
    """Admit caller decoding and next-phase growth before role dispatch."""
    from scripts.whole_source.coordinator import operation_inputs
    from scripts.whole_source.storage import current_budget
    from contextlib import nullcontext
    from scripts.whole_source.supervision import require_current, current_binding, event, validate_binding
    require_current()
    event(phase, work='admission-census')
    # The recursive census has bounded depth/path residency; admit that scratch
    # before walking, then price the actual retained filename/reference set.
    with caller_scope({'required_bytes': current_commit(root)+64*MIB}, helper_root=root):
        account = phase_caller_account(phase, problem, run=run)
    with caller_scope(account, helper_root=root) as memory:
        predecessors = operation_inputs(run, {} if inputs is None else inputs, code_root=root)
        identity = _attempt_id(directory, run) if directory is not None else None
        supervision = current_binding()
        validate_binding(supervision)
        budget = current_budget(Path(run)/'admission/probe')
        own = budget is None
        if own:
            budget, forecast = operation_budget(problem, run, root, phase=phase, external=external,
                                                resume_external=resume_external)
        else:
            # Captured replay shares its outer operation's admitted volume
            # allowance. Its caller/ancestor memory is still admitted separately.
            forecast = topology(problem)
        with (budget.scope() if own else nullcontext()):
            volumes = budget.admit()
            report = {'format': FORMAT, 'policy': POLICY, 'phase': phase,
                      'problem_id': problem_id(problem), 'inputs': predecessors,
                      'caller': _retained_caller(memory), 'storage': volumes, 'lifetime': forecast,
                      'supervision': supervision,
                      'mathematical_acceptance': False, 'reservation': False}
            import uuid
            path = Path(run)/'admission'/('phase-'+phase+'-'+uuid.uuid4().hex+'.json')
            if identity is not None:
                report['attempt_id'] = identity
            _write_admission(path, report)
            event(phase, work='phase-work')
            try:
                yield report
            except BaseException:
                try:
                    event(phase, state='failed')
                except (ValueError, OSError):
                    pass
                raise
            else:
                event(phase, state='complete')


def admit_attempt(journal, phase, forecast, *, reuse=False):
    """A fresh retry consumes retained allowance; never retire old attempts."""
    if reuse:
        return
    count = sum(node['kind'] == 'intent' and node['payload']['phase'] == phase
                for _, node in journal.nodes.values())
    _require(count < forecast['attempts_per_phase'], 'phase retry allowance exhausted')


def verify_attempt(document, *, phase, directory, inputs, legacy_inputs=None):
    """Check an admission's exact predecessor and attempt bindings before adoption."""
    from scripts.whole_source.supervision import validate_binding
    directory = Path(directory)
    _require(type(document) is dict and document.get('format') in (LEGACY_FORMAT, FORMAT) and
             document.get('policy') == POLICY and document.get('phase') == phase and
             directory.is_absolute() and _ID.fullmatch(directory.name),
             'selected phase admission does not match original attempt')
    legacy = document['format'] == LEGACY_FORMAT
    if legacy:
        bound = document.get('attempt_directory') == str(directory)
        expected = inputs if legacy_inputs is None else legacy_inputs
    else:
        bound = document.get('attempt_id') == directory.name and set(document) <= _REPORT_FIELDS
        expected = inputs
    _require(bound and document.get('inputs') == expected,
             'selected phase admission does not match original attempt')
    binding = document.get('supervision')
    _require(type(binding) is dict, 'missing selected phase supervisor authority')
    validate_binding(binding, legacy=legacy)
    return binding


def bind_phase_attempt(report, directory, run, *, legacy_inputs=None):
    """Retain the original admission before an attempt can produce any output."""
    from scripts.whole_source.execution import _bytes, _json
    from scripts.whole_source.storage import _inspect
    from scripts.whole_source.supervision import verify_binding
    phase = report['phase']
    directory, run = Path(directory).absolute(), Path(run).absolute()
    identity = _attempt_id(directory, run)
    _require(directory.parent == run/phase/'attempts' and report.get('attempt_id', identity) == identity,
             'invalid admitted phase attempt')
    _require(report.get('format') == FORMAT and set(report) <= _REPORT_FIELDS,
             'invalid new phase admission record')
    candidate = {**report, 'attempt_id': identity}
    active = verify_attempt(candidate, phase=phase, directory=directory, inputs=report['inputs'])
    path = run/'admission'/('attempt-'+phase+'-'+identity+'.json')
    _inspect(path)
    if not path.exists():
        if path.parent.exists():
            with os.scandir(path.parent) as entries:
                _require(not any(entry.name.casefold().startswith(path.stem+'-') for entry in entries),
                         'phase continuation lacks an original admission')
        _write_admission(path, candidate)
        return

    def read_binding(item):
        _inspect(item)
        return verify_attempt(_json(_bytes(item)), phase=phase, directory=directory,
                              inputs=report['inputs'], legacy_inputs=legacy_inputs)

    original = read_binding(path)
    active_id = active['invocation_id']
    seen = {original['invocation_id']}
    try:
        if original != active:
            verify_binding(original)
        prefix = path.stem+'-'
        with os.scandir(path.parent) as entries:
            for entry in entries:
                if not entry.name.casefold().startswith(prefix):
                    continue
                suffix = entry.name[len(prefix):]
                _require(len(seen) < 1024 and entry.name.startswith(prefix) and
                         suffix.endswith('.json') and _ID.fullmatch(suffix[:-5]),
                         'invalid prior phase continuation')
                binding = read_binding(Path(entry.path))
                invocation = binding['invocation_id']
                _require(invocation == suffix[:-5] and invocation not in seen,
                         'changed prior phase continuation identity')
                seen.add(invocation)
                if binding != active:
                    verify_binding(binding)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ContractError('unverified prior phase supervision') from error
    if active_id not in seen:
        continuation = path.with_name(path.stem+'-'+active_id+'.json')
        _write_admission(continuation, candidate)


@contextmanager
def bootstrap_scope(root, *, input_count=0):
    """Admit the fixed scalar closure and bounded external execution documents."""
    from scripts.whole_source.supervision import require_current, event
    require_current()
    event('bootstrap', work='scalar-decoding')
    from scripts.whole_source.contract import _PROFILES, _manifest_name, _snapshot_names
    bundle = _PROFILES['retained-t081'][0]
    paths = {Path(root)/bundle/_manifest_name('retained-t081'),
             *(Path(root)/bundle/name for name in _snapshot_names('retained-t081').values())}
    sizes = [path.stat().st_size for path in paths]
    _require(all(0 < size <= 8*MIB for size in sizes), 'scalar bootstrap exceeds codec')
    _positive(input_count, 'bootstrap input count', 0)
    _require(input_count <= 3, 'too many bootstrap documents')
    raw = sum(sizes)
    account = {'phase': 'bootstrap', 'components': {
        'runtime_and_import_bytes': 128*MIB, 'retained_closure_bytes': 64*MIB,
        'scalar_decoder_bytes': 4*decoded_bound(raw),
        'external_decoder_bytes': decoded_bound(input_count*8*MIB)},
        'os_enforced': False, 'measured_peak': False}
    account['required_bytes'] = sum(account['components'].values())
    with caller_scope(account, helper_root=root) as report:
        try:
            yield report
        except BaseException:
            try:
                event('bootstrap', state='failed')
            except (ValueError, OSError):
                pass
            raise
        else:
            event('bootstrap', state='complete')


def admitted_problem(root):
    from scripts.whole_source.contract import bind_problem
    with bootstrap_scope(root):
        return bind_problem('retained-t081', root=root)


def _admit_increment(demand, label):
    rows = _context()
    if not rows or rows[-1]['pid'] != os.getpid():
        return
    from scripts.whole_source.execution import neutral_helpers, exact_telemetry
    probe = _PROBE.get()
    root, resources = (ROOT, neutral_helpers(ROOT)[0]) if probe is None else probe[:2]
    current = current_commit(root)
    _require(current+demand <= rows[-1]['required_bytes'], label+' exceeds admitted caller envelope')
    admit_caller({'required_bytes': current+demand},
                 exact_telemetry(resources.detect_resources()), existing_bytes=current)


def admit_decode(raw_bytes):
    """Check actual serialized demand before constructing Python JSON objects.

    Owned numerical children retain their separate job/codec admission. The
    coordinator's commitment includes already-live decoded predecessors; another
    decode may not silently borrow beyond its admitted envelope.
    """
    if os.environ.get(_ENV) is not None:
        _admit_increment(decoded_bound(raw_bytes), 'decoder')


def admit_names(directory):
    """Admit an actual complete filename/reference view before materializing it."""
    if not _context() or _context()[-1]['pid'] != os.getpid():
        return
    from scripts.whole_source.storage import _census, _volume
    _admit_increment(64*MIB, 'census')
    stats = _census(Path(directory), _volume(Path(directory)), MAX_FILES, MAX_PATH_BYTES)
    _admit_increment(8*(stats['path_bytes']+stats['file_count']*1024), 'filename view')
