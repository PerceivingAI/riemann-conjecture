"""Validate committed phase locators separately from scientific producer authority."""
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from scripts.whole_source.contract import ArtifactRef, ContractError, bind_problem, canonical_bytes, problem_id
from scripts.whole_source.artifacts import _raw, _safe, decode_rational
from scripts.whole_source.execution import MIB, _bytes, _json, exact_telemetry
from scripts.whole_source.coordinator import (
    PHASES, SCIENCE_PHASES, read_phase_records, _absolute, _artifact_record, _attempt_directory,
)


_OUTPUT_PATHS = {
    'prepare': {'problem': 'source-inputs/problem.json', 'source_execution': 'source-inputs/execution.json',
                'premises': 'premises/premises-receipt.json'},
    'source': {'source': 'producer/source-manifest.json', 'source_publication': 'producer/source-execution.json'},
    'audit': {'audit': 'analytical-receipt.json', 'audit_execution': 'audit-execution.json'},
    'proposal': {'proposal': 'work/proposal.json'},
    'exact-inputs': {'problem': 'problem.json', 'execution': 'execution.json', 'operands': 'operands.json'},
    'exact': {'exact': 'report.json'},
    'controls': {'controls': 'controls-receipt.json'},
    'replay': {'replay': 'replay-receipt.json'},
}
_PIPELINE_OUTPUTS = {
    'problem': ('prepare', 'problem'), 'source_execution': ('prepare', 'source_execution'),
    'premises': ('prepare', 'premises'), 'source': ('source', 'source'),
    'source_publication': ('source', 'source_publication'), 'audit': ('audit', 'audit'),
    'audit_execution': ('audit', 'audit_execution'), 'proposal': ('proposal', 'proposal'),
    'exact': ('exact', 'exact'),
}


def _require(value, message):
    if not value:
        raise ContractError(message)


def _path(record):
    directory, artifact = _artifact_record(record)
    return directory/artifact.path


def _document(record):
    directory, artifact = _artifact_record(record)
    return _json(_raw(directory, artifact, 8*MIB))


def _record(path):
    from scripts.whole_source.retention import _record as record
    return record(path)


def _selection(run):
    run = _absolute(str(Path(run).absolute()))
    rows = read_phase_records(run)
    context = _json(_bytes(run/'coordinator/context.json'))['context']
    _require(context['implementation'] == _record(run/'implementation/start.json'),
             'coordinator does not bind original science start')
    return run, context, rows


def _mapping(phase, outputs, directory, run, proposal_input):
    _require(phase in PHASES, 'unknown selected phase')
    directory = _attempt_directory(run, phase, str(directory))
    _require(type(outputs) is dict and set(outputs) == set(_OUTPUT_PATHS[phase]),
             'incorrect selected phase output roles')
    if phase == 'proposal' and proposal_input is not None:
        _require(outputs == {'proposal': proposal_input}, 'unbound installed replay proposal')
        _path(proposal_input)
        _require(_json(_bytes(directory/'installed-proposal.json')) == {'proposal': proposal_input},
                 'missing or changed installed proposal marker')
    else:
        for name, relative in _OUTPUT_PATHS[phase].items():
            expected = directory/relative
            actual = _path(outputs[name])
            _require(actual == expected and outputs[name]['directory'] == str(expected.parent)
                     and outputs[name]['artifact']['path'] == expected.name,
                     'selected output is outside intended phase destination')
    return directory


def _start(run, root, context):
    from scripts.whole_source import retention as r
    _require(run.is_relative_to(root), 'coordinator run is outside code root')
    _require(_json(_bytes(run/'integration-execution.json')) == context['configuration'],
             'coordinator configuration differs from original bound inputs')
    value = _document(context['implementation'])
    code, capture, locations = r._implementation_code(root)
    _require(value.get('format') == 'whole-source-coordinator-implementation-v1'
             and value.get('phase') == 'science' and value.get('problem_id') == context['problem_id']
             and value.get('runtime_versions') == r._runtime_versions()
             and value.get('inherited_capture') == capture and value.get('production_admission') is False,
             'changed original science implementation context')
    r._reviewed_code(value.get('code'), code)
    for row in code:
        ref = ArtifactRef(**row['artifact'])
        _raw(run/'implementation', ArtifactRef('snapshots/'+ref.sha256, ref.sha256, ref.size), 8*MIB)
    return code, capture, locations


def validate_pipeline(run, root):
    """Validate selection and coordinator identity, not rerun scientific role gates."""
    from scripts.whole_source import retention as r
    root = Path(root).resolve(strict=True)
    run, context, rows = _selection(run)
    _require(all(phase in rows for phase in SCIENCE_PHASES), 'incomplete selected science phase chain')
    for phase, row in rows.items():
        _mapping(phase, row['outputs'], Path(row['directory']), run, context['proposal_input'])
    code, capture, _ = _start(run, root, context)
    pipeline = _record(run/'pipeline-result.json')
    document = _document(pipeline)
    _require(set(document) == set(_PIPELINE_OUTPUTS) | {
        'format', 'status', 'problem_id', 'implementation', 'phase_chain', 'gamma',
        'fresh_proposal', 'production_admission'}, 'invalid selected pipeline fields')
    _require(document['format'] == 'whole-source-pipeline-result-v3'
             and document['status'] == 'COMPLETE_FRESH_SOURCE_AUDIT_AND_EXACT'
             and document['problem_id'] == context['problem_id']
             and document['implementation'] == context['implementation']
             and document['phase_chain'] == [rows[phase]['record'] for phase in SCIENCE_PHASES]
             and document['fresh_proposal'] is (context['proposal_input'] is None)
             and document['production_admission'] is False,
             'pipeline differs from committed science phase chain')
    for name, (phase, output) in _PIPELINE_OUTPUTS.items():
        _require(document[name] == rows[phase]['outputs'][output], 'pipeline adopts nonselected scientific output')
    _require(document['gamma'] == _document(document['exact'])['assessment']['gamma'],
             'pipeline consequence differs from selected exact output')
    if context['proposal_input'] is not None:
        _require(_path(context['proposal_input']).is_relative_to(root), 'installed replay proposal escapes capture')
    r._coordinator_implementation(run, 'science', {'pipeline': pipeline}, code, capture, context['problem_id'])
    return document, rows


def _replay_child(run, directory, document):
    _require(document.get('original_run') == _record(run/'pipeline-result.json'),
             'replay binds another original pipeline')
    child = document['replayed_run']
    child_path = _path(child)
    tree = directory/'captured-root'
    _require(child['artifact']['path'] == 'pipeline-result.json'
             and child_path.parent.is_relative_to(tree) and child_path.parent != tree,
             'replay child escapes captured execution tree')
    _require(document.get('capture') == _record(tree/'capture-manifest.json'), 'replay capture locator differs')
    return tree, child_path.parent


def selected_execution_roots(run):
    """Return only committed in-operation receipt roots; leave failed history intact."""
    run, context, rows = _selection(run)
    result = []
    for phase, row in rows.items():
        directory = _mapping(phase, row['outputs'], Path(row['directory']), run, context['proposal_input'])
        if phase == 'prepare':
            result.append(('premises', directory/'premises'))
        elif phase in ('source', 'audit', 'exact', 'controls'):
            result.append((phase, directory))
        elif phase == 'proposal' and context['proposal_input'] is None:
            result.append(('proposal', directory/'work'))
        elif phase == 'replay':
            _, child = _replay_child(run, directory, _document(row['outputs']['replay']))
            _selection(child)
            result.append(('replay', child))
    return result


def _stage_tasks(record, *, role, function, plan=None):
    """Join verified raw tasks and completed results without executing either."""
    from scripts.whole_source.receipts import verify_stage
    evidence = verify_stage(_path(record))
    _require(evidence['record'] == record and evidence['plan'].role == role
             and evidence['plan'].task_function == function,
             'owned stage has another scientific role')
    if plan is not None:
        _require(evidence['plan'].to_dict() == plan.to_dict(), 'owned stage has another bound execution plan')
    stage = evidence['stage']
    directory, results = Path(stage['result_dir']), {}
    with (directory/'completed.jsonl').open('rb') as stream:
        for line in stream:
            row = _json(line)
            ref = ArtifactRef(**{key: row[key] for key in ('path', 'sha256', 'size')})
            payload = _json(_raw(directory, ref, evidence['plan'].result_bytes))
            _require(payload['task_id'] not in results, 'duplicate selected task result')
            results[payload['task_id']] = payload['result']
    pairs = []
    with Path(stage['task_file']).open('rb') as stream:
        for line in stream:
            task = _json(line)
            _require(task['task_id'] in results, 'selected task has no completed result')
            pairs.append((task, results.pop(task['task_id'])))
    _require(not results, 'selected result has no assigned task')
    return evidence, pairs


def _telemetry(records):
    return exact_telemetry([json.loads(_bytes(_path(record))) for record in records])


def _capture(tree, problem, original, proposal=None):
    """Check the exact input-only capture inventory against original raw bytes."""
    from scripts.whole_source import retention as r
    files = {}
    def add(name, raw, role):
        ref = asdict(ArtifactRef(name, hashlib.sha256(raw).hexdigest(), len(raw)))
        if name in files:
            _require(files[name]['artifact'] == ref, 'conflicting captured input')
            files[name]['roles'].append(role)
        else:
            files[name] = {'artifact': ref, 'roles': [role]}
        _require(_raw(tree, ArtifactRef(**ref), 8*MIB) == raw, 'captured input differs from original bytes')
    for ref in problem.evidence:
        add(ref.path, _raw(original, ref, 8*MIB), 'scalar-metadata')
    for name in sorted(set((*r.CODE, *r._RUNTIME))):
        add(name, _bytes(original/name), 'executed-code')
    old = original/r.OLD_CAPTURE
    name = r.OLD_CAPTURE+'/captured-source-inputs-v1.json'
    capture = _json(_bytes(old/'captured-source-inputs-v1.json'))
    add(name, _bytes(old/'captured-source-inputs-v1.json'), 'scalar-capture-provenance')
    for row in capture['files']:
        name = row['destination']
        if 'installed' not in row['roles'] or name.startswith(r.OLD_CANDIDATE):
            continue
        raw = _bytes(_safe(old, row['stored']))
        _require((len(raw), hashlib.sha256(raw).hexdigest()) == (row['bytes'], row['sha256']),
                 'changed original scalar capture')
        add(name, raw, 'original-scalar-program-or-input')
        add(r.OLD_CAPTURE+'/'+row['stored'], raw, 'scalar-capture-provenance')
    if proposal is not None:
        path = _path(proposal)
        core = _document(proposal)
        base = path.parent.relative_to(original)
        add(path.relative_to(original).as_posix(), _bytes(path), 'NONPROOF_ONLY')
        refs = [panel['artifact'] for block in core['blocks'] for panel in block['integer_panels']]
        refs.append(core['diagnostics'])
        for value in refs:
            ref = ArtifactRef(**value)
            add((base/ref.path).as_posix(), _raw(path.parent, ref, 8*MIB), 'NONPROOF_ONLY')
    expected = {'format': 'whole-source-captured-inputs-v1', 'problem_id': problem_id(problem),
                'files': [files[name] for name in sorted(files)], 'expected_new_outputs_installed': False,
                'proposal_installed': proposal is not None, 'production_admission': False}
    _require(_json(_bytes(tree/'capture-manifest.json')) == expected, 'capture contains missing or unexpected inputs')
    bind_problem(problem.profile, root=tree)


def _premises(problem, record, directory, root):
    from scripts.whole_source import retention as r
    from scripts.whole_source.receipts import discover_receipts
    from scripts.whole_source.slice import _request
    document = _document(record)
    _require(set(document) == {'format', 'status', 'problem_id', 'outputs', 'owned_receipts', 'production_admission'}
             and document['format'] == 'whole-source-scalar-premises-v1'
             and document['status'] == 'VERIFIED_FRESH_SCALAR_PREMISES'
             and document['problem_id'] == problem_id(problem) and document['production_admission'] is False
             and len(document['outputs']) == 8, 'incomplete scalar premise evidence')
    _capture(directory/'installed', problem, root)
    receipts = {}
    for path in discover_receipts(directory/'collection'):
        record = _record(path)
        evidence, pairs = _stage_tasks(record, role='analytic', function='evaluate_premise')
        stage = path.parent.name
        _require(stage not in receipts, 'repeated scalar premise producer')
        receipts[stage] = record
        _require(len(pairs) == 1, 'scalar premise stage must have one task')
        task, result = pairs[0]
        index = task['index']
        _require(type(index) is int and 0 <= index < 8 and stage == 'premise-'+str(index)
                 and task == _request(index=index, scalar_root=(directory/'installed').relative_to(root).as_posix(),
                                     output=r.QUALIFICATION+'/data/owned-native-reconstruction')
                 and result == document['outputs'][index], 'scalar premise differs from actual owned task')
        script, _, reviewed = r._scalar_steps(task['output'])[index]
        _require(result['status'] == 'VERIFIED_FRESH_SCALAR_PREMISE' and result['index'] == index
                 and result['byte_identical_to_reviewed_scalar'] is True and result['production_admission'] is False
                 and _path(result['output']).is_relative_to(directory/'collection')
                 and _path(result['executed_program']).is_relative_to(directory/'collection'),
                 'scalar premise lacks original output authority')
        _require(_bytes(_path(result['output'])) == _bytes(root/r.QUALIFICATION/'data'/reviewed)
                 and _bytes(_path(result['executed_program'])) == _bytes(root/r.QUALIFICATION/script)
                 and result['program'] == asdict(r._ref(root, task['scalar_root']+'/'+r.QUALIFICATION+'/'+script)),
                 'scalar premise raw declaration/program differs')
    _require(set(receipts) == {'premise-'+str(i) for i in range(8)}
             and document['owned_receipts'] == _telemetry([receipts['premise-'+str(i)] for i in range(8)]),
             'scalar premise receipts differ from eight actual producers')


def _journal(collection, operation, output, configuration, collection_id):
    from scripts.whole_source import recovery
    document = recovery._context_document(collection)
    _require(document == {'format': recovery.RECOVERY_POLICY, 'root': str(collection),
                          'collection_id': collection_id,
                          'context': recovery.operation_context(operation, output, configuration)},
             'selected recovery journal has another operation context')
    records, _ = recovery._state(collection, document)
    waves, terminals = {}, {}
    for _, node in reversed(records):
        target = waves if node['kind'] == 'wave' else terminals if node['kind'] == 'terminal' else None
        if target is not None:
            _require(node['key'] not in target, 'repeated selected recovery checkpoint')
            target[node['key']] = node['payload']
    return waves, terminals


def _terminal(collection, output, terminals, filename, dependencies):
    _require(filename in terminals, 'publication lacks committed terminal authority')
    value = terminals[filename]
    _require(type(value) is dict and set(value) == {'path', 'artifact', 'dependencies'}
             and value['path'] == str(output/filename) and value['dependencies'] == dependencies,
             'terminal publication has another producer selection')
    _require(_raw(collection, ArtifactRef(**value['artifact']), 8*MIB) == _bytes(output/filename),
             'terminal publication differs from committed original bytes')


def _origin(spec, plan, path, root, *, reader_context=None, configuration=None):
    from scripts.whole_source.execution import _provenance
    from scripts.whole_source.slice import _ref
    _require(plan.provenance == _ref(root, path.relative_to(root).as_posix()),
             'phase execution adopts an external origin record')
    value = _provenance(root, plan.provenance)
    fields = {'format', 'origin_git_commit', 'origin_git_dirty', 'files'}
    if reader_context is not None:
        fields.add('reader_contexts')
        _require(value.get('reader_contexts') == [reader_context], 'phase reader context escapes intended inputs')
    _require(set(value) == fields and value['files'] == [asdict(ref) for ref in spec.code_refs],
             'phase origin differs from bound code closure')
    if configuration is not None:
        _require(all(value[name] == configuration[name] for name in ('origin_git_commit', 'origin_git_dirty')),
                 'phase origin claim differs from original configuration')


def _proposal(problem, source, path, directory, root):
    from scripts.whole_source import proposal as p
    from scripts.whole_source.task_groups import _read_group
    _, config, bound = p._bind_proposal(directory/'inputs/problem.json', source.path,
                                        directory/'inputs/execution.json', root)
    snapshot = (directory/'inputs/source-context').relative_to(root).as_posix()
    _require(config['source_snapshot'] == snapshot, 'proposal source snapshot escapes intended inputs')
    for name, (spec, plan) in bound.items():
        _origin(spec, plan, directory/'inputs'/(name+'-origin.json'), root, reader_context=snapshot)
    _require(config['control'] is False, 'reduced proposal cannot qualify a full source')
    core = p.read_proposal(path, problem, asdict(source.ref))
    _require(core['source_control'] is False and core['source_directory_at_execution'] == str(source.path.parent)
             and core['policy'] == config['policy']
             and core['code'] == [asdict(ref) for ref in bound['native'][0].code_refs]
             and core['backend_versions'] == {name: plan.backend_version for name, (_, plan) in bound.items()},
             'proposal differs from bound original source or execution policy')
    work = directory/'work'
    diagnostics = _json(_raw(work, ArtifactRef(**core['diagnostics']), 8*MIB))
    _require(diagnostics.get('format') == 'whole-source-proposal-diagnostics-v1'
             and diagnostics.get('status') == 'NONPROOF_ONLY' and len(diagnostics['blocks']) == 2,
             'proposal has incomplete original producer diagnostics')
    producer_groups = []
    for parity, block in enumerate(diagnostics['blocks']):
        context = {**config['context'], 'parity': parity}
        base = {'context': context, 'source': config['source'], 'source_snapshot': config['source_snapshot']}
        _require(block['parity'] == parity, 'proposal producer parity differs')
        stages = iter(block['native']['stages'])
        factors = []
        def wave(report, operation, deps, column=None, kind='native'):
            tasks = p._make_tasks(base, operation, deps, column)
            root_ = work/(kind+'-'+str(parity))
            group = report['dependency']['record']
            _, _, stage = _read_group(group, p._wave_context(context, operation, column), expected_root=root_)
            _require(stage['plan'] == bound['floating' if kind == 'floating' else 'native'][1].to_dict(),
                     'proposal producer has another execution plan')
            p._check_recovered_wave(report, tasks, operation, column)
            waves, _ = _journal(root_, 'proposal', work, config,
                                 bound['floating' if kind == 'floating' else 'native'][0].collection_id)
            key = operation+('_'+str(column) if column is not None else '')
            _require(key in waves and waves[key]['group'] == group and waves[key]['value'] == report,
                     'proposal producer is not the committed original wave')
            producer_groups.append(group)
            return report['dependency']
        try:
            for column in p._grid(context):
                report = next(stages)
                factors.append(wave(report, 'factor-diagonal', {'factor': list(factors)}, column))
                if p._make_tasks(base, 'factor-below', {'factor': list(factors)}, column):
                    report = next(stages)
                    factors.append(wave(report, 'factor-below', {'factor': list(factors)}, column))
            report = next(stages)
            forward = wave(report, 'whiten-forward', {'factor': factors})
            report = next(stages)
            whitened = wave(report, 'whiten-transpose', {'factor': factors, 'forward': [forward]})
        except StopIteration as exc:
            raise ContractError('incomplete proposal producer wave chain') from exc
        _require(next(stages, None) is None and block['native']['factors'] == factors
                 and block['native']['whitened'] == whitened, 'proposal native producer chain differs')
        floating = wave(block['floating'], 'float-optimize', {'whitened': [whitened]}, kind='floating')
        solved = wave(block['solve'], 'backsolve-quantize', {'factor': factors, 'floating': [floating]}, kind='solve')
        store = p._dependency_store([solved], context, [('backsolve-quantize', None)], binding=base)
        for panel in core['blocks'][parity]['integer_panels']:
            name = f"Z/{panel['row']}/{panel['column']}"
            ref = ArtifactRef(**store.refs[name])
            _require(panel['artifact'] == asdict(ArtifactRef((store.root/ref.path).relative_to(work).as_posix(),
                                                            ref.sha256, ref.size)),
                     'proposal panel does not belong to actual solved producer')
        _require(core['blocks'][parity]['theta'] == block['floating']['diagnostics']['theta'],
                 'proposal theta differs from actual optimization result')
    _, terminals = _journal(work/'recovery-terminal', 'proposal', work, config, bound['native'][0].collection_id)
    _terminal(work/'recovery-terminal', work, terminals, 'proposal.json', producer_groups)
    _terminal(work/'recovery-terminal', work, terminals, 'proposal-diagnostics.json', producer_groups)
    return core


def _operands(problem, config, descriptor, source_record, proposal_record, operands_record, root, spec, plan):
    _require(descriptor['proof_scope'] == 'SOURCE_CONDITIONAL'
             and descriptor['origin'] == {'kind': 'FRESH_NONPROOF', **proposal_record}
             and descriptor['source']['directory'] == source_record['directory']
             and descriptor['source']['manifest'] == source_record['artifact']
             and config['operands'] == asdict(ArtifactRef(_path(operands_record).relative_to(root).as_posix(),
                 operands_record['artifact']['sha256'], operands_record['artifact']['size'])),
             'exact operands adopt another source or proposal')
    _require(descriptor['problem_id'] == problem_id(problem), 'exact operands problem differs')
    inputs = _path(operands_record).parent
    snapshot = (inputs/'source-context').relative_to(root).as_posix()
    _require(descriptor['source_snapshot'] == snapshot
             and descriptor['source']['execution'] == _record(Path(source_record['directory'])/'source-execution.json')['artifact'],
             'exact source snapshot differs from selected original publication')
    _origin(spec, plan, inputs/'exact-origin.json', root, reader_context=snapshot)


def _exact_report(problem, config, descriptor, spec, plan, directory, *, positive):
    from scripts.whole_source import exact_tasks as t
    from scripts.whole_source import retention as r
    from scripts.whole_source.task_groups import _read_group, group_tasks, same_group
    collection = directory/'collection'
    waves, terminals = _journal(collection, 'exact', directory, config, spec.collection_id)
    _require(set(waves) == {'global', 'first', 'second', 'reduce', 'assess'}, 'incomplete exact producer waves')
    groups, outputs, receipts = {}, {}, {}
    for operation in ('global', 'first', 'second', 'reduce', 'assess'):
        group = waves[operation]['group']
        context = t._context(descriptor, config['operands'], operation)
        _, output, stage = _read_group(group, context, expected_root=collection)
        _require(stage['plan'] == plan.to_dict(), 'exact producer has another execution plan')
        group_document = _json(_raw(collection, ArtifactRef(**group['artifact']), 8*MIB))
        record = group_document['stage']
        receipts[str(_path(record))] = record
        groups[operation], outputs[operation] = group, output
        if operation != 'assess':
            t._wave({'operands': config['operands'], 'groups': groups}, descriptor, operation,
                    expected_root=collection, expected_attempt=None)
    dependencies = [groups[name] for name in ('global', 'first', 'second', 'reduce', 'assess')]
    _terminal(collection, directory, terminals, 'report.json', dependencies)
    report = _json(_bytes(directory/'report.json'))
    blocks = [_json(_raw(collection, ArtifactRef(**outputs['reduce'][f'reduce/{p}']), 8*MIB)) for p in (0, 1)]
    actual = list(group_tasks(groups['assess'], t._context(descriptor, config['operands'], 'assess'),
                              expected_root=collection))
    _require(len(actual) == 1 and set(outputs['assess']) == {'assessment'}, 'incomplete exact assessment authority')
    task, result = actual[0]
    refs = [outputs['reduce'][f'reduce/{p}'] for p in (0, 1)]
    _require(task == t._request('assess', config['operands'], task['groups'], blocks=refs)
             and set(task['groups']) == {'reduce'} and same_group(task['groups']['reduce'], groups['reduce'])
             and set(result) == {'scope', 'assessment'} and result['scope'] == 'EXACT_ASSESSMENT_ONLY'
             and result['assessment'] == _json(_raw(collection, ArtifactRef(**outputs['assess']['assessment']), 8*MIB)),
             'exact assessment differs from actual owned result')
    selected = [receipts[key] for key in sorted(receipts)]
    bindings = [asdict(ArtifactRef(_path(record).relative_to(directory).as_posix(),
                                   record['artifact']['sha256'], record['artifact']['size'])) for record in selected]
    producer = _json(_raw(collection, ArtifactRef(**groups['assess']['artifact']), 8*MIB))
    expected = {'format': 'whole-source-exact-assessment-v1', 'status': result['assessment']['status'],
                'proof_scope': descriptor['proof_scope'], 'source': descriptor['source'],
                'proposal': descriptor['origin'], 'problem_id': problem_id(problem), 'blocks': blocks,
                'assessment': result['assessment'], 'product_inventories': report['product_inventories'],
                'operands': config['operands'], 'attempt_id': producer['attempt_id'],
                'owned_receipts': _telemetry(selected), 'receipt_bindings': bindings,
                'analytical_source_acceptance': False, 'production_admission': False}
    _require(report == expected, 'exact report differs from complete original producer authority')
    _require(len(report['product_inventories']) == 2, 'incomplete exact product inventories')
    for p, value in enumerate(report['product_inventories']):
        panels = {name.split('/', 1)[1]: ref for name, ref in outputs['first'].items() if name.startswith(str(p)+'/')}
        _require(_json(_raw(collection, ArtifactRef(**value), 8*MIB)) == {
            'format': 'whole-source-exact-product-inventory-v1', 'context': descriptor['blocks'][p]['context'],
            'panels': panels}, 'exact product inventory differs from selected first wave')
    if positive:
        consequence = r.reviewed_consequence(problem, blocks)
        _require(report['proof_scope'] == 'SOURCE_CONDITIONAL'
                 and report['assessment']['positive_paid_lower'] is True
                 and decode_rational(report['assessment']['gamma'], 65536) == consequence['gamma']
                 and decode_rational(report['assessment']['gamma'], 65536) >= r.FLOOR,
                 'exact report lacks complete positive source-conditional consequence')
    return report


def _control_variant(source, record, case, family, shifts, mutations, destination):
    """Compare the retained false input with the specified change to selected bytes."""
    from scripts.whole_source import controls as c
    from scripts.whole_source.pipeline import SourceReader
    from scripts.whole_source.artifacts import _task, decode_integer, encode_integer
    _require(_path(record) == destination/'source-manifest.json', 'false source escapes intended control destination')
    variant = SourceReader(_path(record), source.spec, control=False)
    _require(variant.execution['provenance'] == {
        'kind': 'MATHEMATICAL_VARIANT', 'original_source': _record(source.path),
        'original_execution': _record(source.execution_path)}, 'false source has another original authority')
    expected = _json(canonical_bytes(source.document))
    changes = []
    for row in expected['tiles']:
        ref = ArtifactRef(**row['artifact'])
        domain = _task(row['task'])
        selected = (case == 'selected-paid-lower-negative' and row['family'] == 'A_model') or (
            row['family'] == family and row['parity'] == 0 and 0 in domain.rows and 0 in domain.columns)
        raw = _raw(source.path.parent, ref, source.spec.bounds.max_raw_bytes)
        if not selected:
            _require(_raw(destination, ref, source.spec.bounds.max_raw_bytes) == raw,
                     'control changed an unselected source tile')
            continue
        payload = _json(raw)
        samples, count = [], 0
        for entry in payload['records']:
            m, n = entry[:2]
            if case != 'selected-paid-lower-negative' and (m, n) != (0, 0):
                continue
            lo, hi = (decode_integer(value, source.spec.bounds.max_endpoint_bits) for value in entry[2:])
            if case == 'selected-paid-lower-negative':
                value = -Fraction(2*(1 << source.bits), 2*m+1) if m == n else Fraction(0)
                lower, upper = value.numerator//value.denominator-1, -((-value.numerator)//value.denominator)+1
            else:
                lower, upper = c._change(case, lo, hi, source.bits, shifts)
                _require((lower, upper) != (lo, hi), 'control did not change its declared mathematical value')
            entry[2:] = [encode_integer(lower, source.spec.bounds.max_endpoint_bits),
                         encode_integer(upper, source.spec.bounds.max_endpoint_bits)]
            count += int((lower, upper) != (lo, hi))
            if len(samples) < 4:
                samples.append({'row': m, 'column': n, 'before': [hex(lo), hex(hi)], 'after': entry[2:]})
        changed = canonical_bytes(payload)
        relative = 'variants/'+ref.sha256+'.json'
        changed_ref = asdict(ArtifactRef(relative, hashlib.sha256(changed).hexdigest(), len(changed)))
        _require(_raw(destination, ArtifactRef(**changed_ref), source.spec.bounds.max_raw_bytes) == changed,
                 'control false input differs from specified original-source mutation')
        row['artifact'] = changed_ref
        changes.append({'family': row['family'], 'parity': row['parity'], 'original': asdict(ref),
                        'modified': changed_ref, 'changed_cells': count, 'sample_cells': samples})
    _require(changes and variant.document == expected and mutations == changes,
             'control source or mutation inventory differs from specified case')


def _control_proposal(problem, original_record, source_record, case, destination):
    from scripts.whole_source.proposal import PanelStore, read_proposal
    path = destination/'proposal-core.json'
    original_path = _path(original_record)
    original = _document(original_record)
    value = read_proposal(path, problem, source_record['artifact'])
    expected = _json(canonical_bytes(original))
    expected['source'] = source_record['artifact']
    expected['source_directory_at_execution'] = source_record['directory']
    identity = hashlib.sha256(canonical_bytes({'problem_id': problem_id(problem), 'source': expected['source'],
        'policy': expected['policy'], 'code': expected['code']})).hexdigest()
    _require(_raw(destination, ArtifactRef(**value['diagnostics']), 8*MIB) ==
             _raw(original_path.parent, ArtifactRef(**original['diagnostics']), 8*MIB),
             'artificial proposal changed original producer diagnostics')
    for p, block in enumerate(expected['blocks']):
        block['context'].update(proposal_id=identity, source_sha256=source_record['artifact']['sha256'])
        before = {f"Z/{row['row']}/{row['column']}": row['artifact'] for row in original['blocks'][p]['integer_panels']}
        after = {f"Z/{row['row']}/{row['column']}": row['artifact'] for row in value['blocks'][p]['integer_panels']}
        old = PanelStore(original_path.parent, original['blocks'][p]['context'], before)
        new = PanelStore(destination, block['context'], after)
        for panel, actual in zip(block['integer_panels'], value['blocks'][p]['integer_panels'], strict=True):
            i, j = panel['row'], panel['column']
            name = f'Z/{i}/{j}'
            integers = list(old.read(name, 'integer'))
            if case == 'singular-full-U' and p == 0 and j == 0:
                b, n = block['context']['panel_size'], block['dimension']
                columns = min(b, n-j)
                for row in range(min(b, n-i)):
                    integers[row*columns] = '0x0'
            _require(new.read(name, 'integer') == integers, 'artificial proposal changed unrelated original integers')
            panel['artifact'] = actual['artifact']
    _require(value == expected, 'artificial proposal changed unrelated original context')
    return {'kind': 'FRESH_NONPROOF', **_record(path)}


def _controls(problem, outputs, directory, prior, source, independent, root, code, capture):
    from scripts.whole_source import controls as c, retention as r
    from scripts.whole_source.exact import _bind_exact
    document = _document(outputs['controls'])
    _require(document.get('format') == 'whole-source-mathematical-controls-v1'
             and document.get('status') == 'PASS_REQUIRED_MATHEMATICAL_CONTROLS'
             and document.get('problem_id') == problem_id(problem)
             and document.get('production_admission') is False and document.get('weil_negativity_claimed') is False,
             'incomplete genuine mathematical controls')
    for name in ('source', 'audit', 'proposal', 'exact'):
        _require(document[name] == prior[name][name]
                 and document[name+'_sha256'] == prior[name][name]['artifact']['sha256'],
                 'controls adopt nonselected scientific inputs')
    _require(document['positive_first'] == c._positive(problem, source, independent, _path(prior['audit']['audit'])),
             'controls positive-first raw audit binding differs')
    expected_cases = [name for name, _ in (*c.SOURCE_CASES, *c.EXACT_CASES)]
    _require(type(document['cases']) is list and [row['case'] for row in document['cases']] == expected_cases,
             'missing or reordered mathematical control cases')
    native_records = []
    from scripts.whole_source.receipts import discover_receipts
    native_paths = discover_receipts(directory/'native')
    native = {path.parent.name: _record(path) for path in native_paths}
    _require(len(native) == len(native_paths)
             and set(native) == {'prime5', *(name for name, _ in c.SOURCE_CASES)},
             'incomplete native control producers')
    evidence, pairs = _stage_tasks(native['prime5'], role='analytic', function='evaluate_control')
    from scripts.whole_source.slice import _request
    _require(len(pairs) == 1 and pairs[0][0] == _request(operation='prime5-shifts')
             and pairs[0][1].get('scope') == c.SCOPE, 'control shifts lack actual owned authority')
    _require(evidence['plan'].scope == c.SCOPE
             and evidence['plan'].task_program == r._ref(root, 'scripts/whole_source/controls.py'),
             'native controls have another bound implementation or scope')
    shifts = {key: tuple(int(value, 16) for value in pair) for key, pair in pairs[0][1]['shifts'].items()}
    _require(set(shifts) == {'omitted-prime5-low-term', 'omitted-prime5-mixed-square'}
             and all(len(pair) == 2 and pair[0] <= pair[1] for pair in shifts.values()),
             'incomplete genuine prime-five control shifts')
    native_records.append(native['prime5'])
    for row in document['cases']:
        name = row['case']
        _require(row == _json(_bytes(directory/name/'case-result.json')) and row['passed'] is True
                 and row['production_admission'] is False, 'control case differs from original publication')
        if name in dict(c.SOURCE_CASES):
            family = dict(c.SOURCE_CASES)[name]
            _require(row['receipt'] == native[name], 'control case has another owned receipt')
            _, pairs = _stage_tasks(row['receipt'], role='analytic', function='evaluate_control', plan=evidence['plan'])
            _require(len(pairs) == 1, 'control case must have one owned task')
            task, result = pairs[0]
            request = {'operation': 'inverse-weights' if family is None else 'containment', 'family': family,
                       'problem_path': str(_path(prior['prepare']['problem'])),
                       'execution_path': str(_path(prior['prepare']['source_execution'])),
                       'variant': row['source'], 'independent': _record(independent.path)}
            expected = 'REJECT_FALSE_INVERSE_WEIGHT_DECLARATION' if family is None else 'REJECT_FALSE_SOURCE_ENCLOSURE'
            if family is None:
                request['declaration'] = row['declaration']
                _require(_path(row['declaration']) == directory/name/'frequency-inverse-weights.json',
                         'terminal inverse-weight declaration escapes control case')
                weights = [str(value) for value in problem.inverse_weights]
                weights[-1] = '0'
                _require(row['source'] == prior['source']['source'] and row['mutations'] == []
                         and row['weight_mutation'] == {'index': len(weights)-1,
                             'declared': str(problem.inverse_weights[-1]), 'false': '0',
                             'field': 'frequency_inverse_weights'}
                         and _document(row['declaration']) == {
                             'format': 'whole-source-control-frequency-weights-v1',
                             'problem_id': problem_id(problem), 'source': asdict(source.ref),
                             'frequency_inverse_weights': weights, 'production_admission': False}
                         and result['declaration_sha256'] == row['declaration']['artifact']['sha256'],
                         'inverse-weight case changed unrelated original source or declaration')
            else:
                _control_variant(source, row['source'], name, family, shifts, row['mutations'], directory/name)
            _require(task == _request(**request) and row['result'] == result and row['expected'] == expected
                     and result['status'] == expected and result['passed'] is True
                     and result['variant_sha256'] == row['source']['artifact']['sha256']
                     and result['independent_sha256'] == independent.ref.sha256
                     and row['owned_receipts'] == _telemetry([native[name]]),
                     'control rejection differs from actual bound owned result')
            _require(result['scope'] == c.SCOPE and result['production_admission'] is False,
                     'native control result has another mathematical scope')
            native_records.append(native[name])
        else:
            case_dir = directory/name
            bound = _bind_exact(case_dir/'inputs/problem.json', case_dir/'inputs/execution.json', root)
            _, config, descriptor, spec, plan = bound
            if name == 'singular-full-U':
                _require(row['source'] == prior['source']['source'] and row['mutations'] == [],
                         'singular-transform control changed original source')
            else:
                _control_variant(source, row['source'], name,
                    'A_model' if name == 'excessive-numerical-width' else None,
                    shifts, row['mutations'], case_dir/'source')
            origin = _control_proposal(problem, prior['proposal']['proposal'], row['source'],
                                       name, case_dir/'proposal')
            _require(row['proposal'] == origin, 'exact control adopts an external proposal')
            _operands(problem, config, descriptor, row['source'],
                      {key: origin[key] for key in ('directory', 'artifact')}, row['operands'], root, spec, plan)
            report = _exact_report(problem, config, descriptor, spec, plan, case_dir/'run', positive=False)
            _require(row['report'] == _record(case_dir/'run/report.json')
                     and row['operands'] == _record(case_dir/'inputs/operands.json')
                     and row['source']['directory'] == descriptor['source']['directory']
                     and row['source']['artifact'] == descriptor['source']['manifest']
                     and row['proposal'] == descriptor['origin'] and row['status'] == report['status']
                     and row['expected'] == dict(c.EXACT_CASES)[name]
                     and row['owned_receipts'] == report['owned_receipts']
                     and row['receipt_bindings'] == report['receipt_bindings']
                     and row['artificial_mathematical_input'] is True and row['weil_negativity_claimed'] is False,
                     'exact control differs from actual normalized owned inputs')
            if name == 'singular-full-U':
                passed = (report['blocks'][0]['modular']['residue'] == 0
                          and report['blocks'][0]['modular']['nonsingular'] is False
                          and report['assessment']['positive_paid_lower'] is False)
            elif name == 'selected-paid-lower-negative':
                passed = report['status'] == row['expected'] and any(
                    decode_rational(block['direction_upper'], 65536) < 0
                    and decode_rational(block['direction_mass'], 65536) > 0 for block in report['blocks'])
            else:
                passed = report['status'] == row['expected'] and any(
                    decode_rational(block['width'], 65536) > decode_rational(block['goal'], 65536)
                    for block in report['blocks'])
            _require(passed, 'exact control did not reach its required mathematical rejection')
    _require(document['native_owned_receipts'] == _telemetry(native_records), 'native control receipt inventory differs')
    r._coordinator_implementation(directory, 'controls', outputs, code, capture, problem_id(problem))


def _replay(problem, outputs, directory, run, root, code, capture):
    from scripts.whole_source import retention as r
    document = _document(outputs['replay'])
    tree, child = _replay_child(run, directory, document)
    original, _ = validate_pipeline(run, root)
    replayed, rows = validate_pipeline(child, tree)
    _require(set(rows) == set(SCIENCE_PHASES) and replayed['fresh_proposal'] is False,
             'replay child must select only its independent science phases')
    _capture(tree, problem, root, original['proposal'])
    _, child_context, _ = _selection(child)
    installed = _record(tree/_path(original['proposal']).relative_to(root))
    _require(child == tree/run.relative_to(root) and child_context['proposal_input'] == installed
             and replayed['proposal'] == installed
             and _bytes(child/'integration-execution.json') == _bytes(run/'integration-execution.json'),
             'replay child changed captured configuration or installed proposal')
    prior = {}
    for phase in SCIENCE_PHASES:
        row = rows[phase]
        validate_phase(phase, row['outputs'], Path(row['directory']), run=child, root=tree,
                       prior=prior, replay_proposal=installed)
        prior[phase] = row['outputs']
    compared = r.compare_science(run, child)
    child_receipts = r._verify_receipts(child, code_root=tree)
    _require(all(document.get(key) == value for key, value in compared.items())
             and document.get('format') == 'whole-source-scientific-replay-v1'
             and document.get('expected_new_outputs_installed') is False
             and type(document.get('exit_code')) is int and document['exit_code'] == 0
             and document.get('shared_installed_arithmetic_runtime') is True
             and document['owned_receipts'] == child_receipts,
             'replay lacks genuine captured scientific comparison and cleanup')
    argv = document['argv']
    entry = "import sys;sys.path.insert(0,sys.argv[1]);from scripts.whole_source.retention import _replay_child;_replay_child(sys.argv[2],sys.argv[3],sys.argv[4])"
    _require(type(argv) is list and len(argv) == 9 and argv[:5] == [r.sys.executable, '-I', '-B', '-c', entry]
             and argv[5:] == [str(tree), str(child), str(child/'integration-execution.json'), str(_path(installed))],
             'replay invocation does not bind captured scientific inputs')
    r._coordinator_implementation(directory, 'replay', outputs, code, capture, problem_id(problem))


def validate_phase(phase, outputs, directory, *, run, root, prior, replay_proposal=None):
    """Admit only the intended attempt's genuinely bound original role outputs."""
    from scripts.whole_source import retention as r
    from scripts.whole_source import pipeline as p
    root = Path(root).resolve(strict=True)
    run, context, rows = _selection(run)
    _require(phase in PHASES, 'unknown selected phase')
    expected_prior = PHASES[:PHASES.index(phase)]
    _require(type(prior) is dict and set(prior) == set(expected_prior)
             and all(name in rows and prior[name] == rows[name]['outputs'] for name in expected_prior),
             'phase inputs differ from committed predecessor outputs')
    _require(replay_proposal == context['proposal_input'], 'phase changed bound replay proposal policy')
    directory = _mapping(phase, outputs, Path(directory), run, replay_proposal)
    code, capture, locations = _start(run, root, context)
    r._check_phase_history(directory)
    if phase not in ('exact-inputs', 'replay') and not (phase == 'proposal' and replay_proposal is not None):
        receipt_root = directory/'work' if phase == 'proposal' else directory
        for receipt in r._verify_receipts(receipt_root, code_root=root):
            r._stage_implementation(receipt, code, locations)
    prepare = outputs if phase == 'prepare' else prior['prepare']
    problem, config, bound = p._bind(_path(prepare['problem']), _path(prepare['source_execution']), root)
    _, integrated = r._bind(_path(prepare['problem']), run/'integration-execution.json', root)
    _require(problem_id(problem) == context['problem_id'] and integrated == context['configuration']
             and config['control'] is False and config['tile_modes'] == integrated['tile_modes'],
             'phase changed complete integrated science context')
    for role, (spec, plan) in bound.items():
        _origin(spec, plan, _path(prepare['problem']).parent/(role+'-origin.json'), root,
                configuration=integrated)
    if phase == 'prepare':
        _premises(problem, outputs['premises'], directory/'premises', root)
        return
    source_record = outputs['source'] if phase == 'source' else prior['source']['source']
    source = p.SourceReader(_path(source_record), bound['producer'][0], control=False)
    _require(source.execution['provenance'].get('plan') == bound['producer'][1].to_dict(),
             'source publication has another prepared execution plan')
    p.verify_source_execution(source)
    for _ in source.tiles():
        pass
    if phase == 'source':
        _require(outputs['source_publication']['artifact'] == asdict(source.execution_ref),
                 'source publication locator differs from original execution')
        return
    if phase in ('audit', 'controls'):
        audit_record = outputs['audit'] if phase == 'audit' else prior['audit']['audit']
        independent = p.SourceReader(_path(audit_record).parent/'analytic/source-manifest.json',
                                     bound['analytic'][0], control=False)
        _require(independent.execution['provenance'].get('plan') == bound['analytic'][1].to_dict(),
                 'audit reconstruction has another prepared execution plan')
        from scripts.whole_source.controls import _positive
        _positive(problem, source, independent, _path(audit_record))
        if phase == 'audit':
            _require(outputs['audit_execution']['artifact'] == p.verify_audit_execution(
                _path(audit_record), source, independent), 'audit execution locator differs')
            return
    if phase == 'proposal':
        if replay_proposal is None:
            _proposal(problem, source, _path(outputs['proposal']), directory, root)
        else:
            from scripts.whole_source.proposal import read_proposal
            path = _path(replay_proposal)
            _require(path.is_relative_to(root), 'installed replay proposal escapes capture')
            manifest = _json(_bytes(root/'capture-manifest.json'))
            _require(manifest.get('format') == 'whole-source-captured-inputs-v1'
                     and manifest.get('problem_id') == problem_id(problem)
                     and manifest.get('expected_new_outputs_installed') is False
                     and manifest.get('proposal_installed') is True
                     and {'artifact': asdict(ArtifactRef(path.relative_to(root).as_posix(),
                         replay_proposal['artifact']['sha256'], replay_proposal['artifact']['size'])),
                          'roles': ['NONPROOF_ONLY']} in manifest['files'],
                     'replay proposal was not installed by the input-only capture')
            _require(read_proposal(path, problem, asdict(source.ref))['source_control'] is False,
                     'installed replay proposal does not bind complete reconstructed source')
        return
    if phase in ('exact-inputs', 'exact'):
        from scripts.whole_source.exact import _bind_exact
        inputs = outputs if phase == 'exact-inputs' else prior['exact-inputs']
        exact_problem, exact_config, descriptor, spec, plan = _bind_exact(
            _path(inputs['problem']), _path(inputs['execution']), root)
        _require(problem_id(exact_problem) == problem_id(problem), 'exact phase problem differs')
        _operands(problem, exact_config, descriptor, prior['source']['source'], prior['proposal']['proposal'],
                  inputs['operands'], root, spec, plan)
        if phase == 'exact':
            _exact_report(problem, exact_config, descriptor, spec, plan, directory, positive=True)
        return
    if phase == 'controls':
        _controls(problem, outputs, directory, prior, source, independent, root, code, capture)
    elif phase == 'replay':
        _replay(problem, outputs, directory, run, root, code, capture)
