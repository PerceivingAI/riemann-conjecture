"""Fresh whole-source qualification, captured replay and conditional acceptance.

Reports are evidence from reviewed local drivers, not signatures from arbitrary
untrusted processes. Installed FLINT/Arb and source-form premises remain explicit.
"""
from __future__ import annotations
from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
import importlib.metadata
from itertools import islice
import json
import os
from pathlib import Path
import runpy
import re
import shutil
import sys
import uuid

from scripts.whole_source.contract import ROOT, ArtifactRef, ContractError, bind_problem, canonical_bytes, problem_id
from scripts.whole_source.artifacts import CollectionSpec, CollectionLock, _raw, _safe, decode_rational
from scripts.whole_source.execution import MIB, WorkloadExecution, _RUNTIME, BUNDLE, _HELPERS, _bytes, _json, _write, exact_telemetry
from scripts.whole_source.slice import _ref, _slice_writer, _request

QUALIFICATION = 'computations/2026-10-27T132236Z-t081-prime-five-qualification'
OLD_CAPTURE = 'computations/2026-10-27T182100Z-t081-retained-acceptance'
OLD_CANDIDATE = 'computations/2026-10-27T140745Z-t081-complete-gram-attempt/'
CODE = ('scripts/weil_whole_source_split.py',
        *('scripts/whole_source/'+name+'.py' for name in
          ('__init__','contract','artifacts','execution','resources','slice','gram','producer','analytic',
           'pipeline','proposal','proposal_float','exact','exact_global','controls','retention',
           'receipts','source_dependencies','coordinator','selection','admission','storage',
           'supervision','lifecycle_windows','lifecycle_observations')))
CODE = (*CODE,*(BUNDLE+'/'+name for name in sorted(_HELPERS)))
FULL_ENTRIES = 512946
FLOOR = Fraction(1,10**21)
REPLAY_EXCLUSIONS = {'audit':['source_directory_at_execution'],
                     'exact':['attempt_id','owned_receipts','receipt_bindings','operands',
                              'source.directory','proposal.directory','product_inventories']}


def _require(condition,message):
    if not condition:
        raise ContractError(message)


def _record(path):
    path = Path(path).resolve(strict=True)
    return {'directory':str(path.parent),'artifact':asdict(_ref(path.parent,path.name))}


def _document(record):
    return _json(_raw(Path(record['directory']),ArtifactRef(**record['artifact']),8*MIB))


def _hash_file(path):
    digest,size = hashlib.sha256(),0
    with Path(path).open('rb') as stream:
        while value := stream.read(MIB):
            digest.update(value)
            size += len(value)
    return {'size':size,'sha256':digest.hexdigest()}


def _new_copy(source,target):
    target = Path(target)
    from scripts.whole_source.storage import current_budget
    budget = current_budget(target)
    if budget is not None:
        budget.copy(source, target)
        return
    target.parent.mkdir(parents=True,exist_ok=True)
    with Path(source).open('rb') as incoming,target.open('xb') as outgoing:
        shutil.copyfileobj(incoming,outgoing,MIB)


def prepare_inputs(problem,directory,*,origin_git_commit,origin_git_dirty,code_root=ROOT):
    root,directory = Path(code_root).resolve(),Path(directory).resolve()
    directory.relative_to(root)
    _require(problem.profile=='retained-t081','full target execution is not admitted')
    directory.mkdir(parents=True,exist_ok=False)
    problem_doc = problem.to_dict()
    problem_doc['problem_id'] = problem_id(problem)
    _write(directory/'problem.json',canonical_bytes(problem_doc))
    config = {'format':'whole-source-integrated-execution-v5','problem_id':problem_id(problem),
        'origin_git_commit':origin_git_commit,'origin_git_dirty':origin_git_dirty,
        'tile_modes':32,'resource_policy':'detected-capacity-v1',
        'lifecycle_admission':'bounded-phase-resources-v1',
        'lifecycle_supervision':'windows-lifecycle-v1',
        'minimum_free_bytes':32*1024*MIB,'gamma_floor':FLOOR,
        'code':[asdict(_ref(root,name)) for name in sorted(set((*CODE,*_RUNTIME)))],
        'replay_exclusions':REPLAY_EXCLUSIONS,'scope':'FULL_MATCHED_REFERENCE_QUALIFICATION',
        'production_admission':False}
    _write(directory/'execution.json',canonical_bytes(config))
    return {'problem':directory/'problem.json','execution':directory/'execution.json'}


def _bind(problem_path,execution_path,root):
    document,config = (_json(_bytes(Path(p))) for p in (problem_path,execution_path))
    problem = bind_problem('retained-t081',root=root)
    expected = problem.to_dict()
    expected['problem_id'] = problem_id(problem)
    _require(canonical_bytes(document)==canonical_bytes(expected),'changed integrated problem')
    _require(set(config)=={'format','problem_id','origin_git_commit','origin_git_dirty','tile_modes',
        'resource_policy','minimum_free_bytes','gamma_floor','code','lifecycle_admission',
        'lifecycle_supervision','replay_exclusions','scope','production_admission'} and
        config['format']=='whole-source-integrated-execution-v5' and
        config['problem_id']==problem_id(problem) and config['tile_modes']==32 and
        config['resource_policy']=='detected-capacity-v1' and
        config['lifecycle_admission']=='bounded-phase-resources-v1' and
        config['lifecycle_supervision']=='windows-lifecycle-v1' and
        config['minimum_free_bytes']==32*1024*MIB and
        decode_rational(config['gamma_floor'],65536)==FLOOR and
        config['replay_exclusions']==REPLAY_EXCLUSIONS and
        config['scope']=='FULL_MATCHED_REFERENCE_QUALIFICATION' and config['production_admission'] is False,
        'changed integrated execution policy')
    expected_names = sorted(set((*CODE,*_RUNTIME)))
    _require([ref['path'] for ref in config['code']]==expected_names,'incomplete integrated code closure')
    for ref in config['code']:
        _raw(root,ArtifactRef(**ref),8*MIB)
    return problem,config


def capture_inputs(problem,directory,*,code_root=ROOT,proposal_path=None):
    """Install only code, scalar premises and an optional bound NONPROOF proposal."""
    root,directory = Path(code_root).resolve(),Path(directory).resolve()
    directory.mkdir(parents=True,exist_ok=False)
    files = {}
    def install(name,raw,role):
        ref = ArtifactRef(name,hashlib.sha256(raw).hexdigest(),len(raw))
        parts = name.split('/')
        for count in range(1,len(parts)):
            parent = _safe(directory,'/'.join(parts[:count]),missing=True)
            parent.mkdir(exist_ok=True)
        _safe(directory,name,missing=True)
        if name in files:
            _require(files[name]['artifact']==asdict(ref),'conflicting captured input')
            files[name]['roles'].append(role)
            return
        _write(directory/name,raw)
        files[name] = {'artifact':asdict(ref),'roles':[role]}
    for ref in problem.evidence:
        install(ref.path,_raw(root,ref,8*MIB),'scalar-metadata')
    for name in sorted(set((*CODE,*_RUNTIME))):
        install(name,_bytes(root/name),'executed-code')
    capture_root = root/OLD_CAPTURE
    capture = _json(_bytes(capture_root/'captured-source-inputs-v1.json'))
    install(OLD_CAPTURE+'/captured-source-inputs-v1.json',
            _bytes(capture_root/'captured-source-inputs-v1.json'),'scalar-capture-provenance')
    for row in capture['files']:
        name = row['destination']
        if 'installed' not in row['roles'] or name.startswith(OLD_CANDIDATE):
            continue
        raw = _bytes(_safe(capture_root,row['stored']))
        _require((len(raw),hashlib.sha256(raw).hexdigest())==(row['bytes'],row['sha256']),
                 'changed original scalar capture')
        install(name,raw,'original-scalar-program-or-input')
        install(OLD_CAPTURE+'/'+row['stored'],raw,'scalar-capture-provenance')
    if proposal_path is not None:
        from scripts.whole_source.proposal import read_proposal
        path = Path(proposal_path).resolve(strict=True)
        core = _json(_bytes(path))
        read_proposal(path,problem,core['source'])
        base = path.parent.relative_to(root)
        install(path.relative_to(root).as_posix(),_bytes(path),'NONPROOF_ONLY')
        for block in core['blocks']:
            for panel in block['integer_panels']:
                ref = ArtifactRef(**panel['artifact'])
                install((base/ref.path).as_posix(),_raw(path.parent,ref,8*MIB),'NONPROOF_ONLY')
        diagnostic = ArtifactRef(**core['diagnostics'])
        install((base/diagnostic.path).as_posix(),_raw(path.parent,diagnostic,8*MIB),'NONPROOF_ONLY')
    _require(not any(name.startswith(OLD_CANDIDATE) for name in files),
             'old target oracle or coordinates entered captured scientific tree')
    manifest = {'format':'whole-source-captured-inputs-v1','problem_id':problem_id(problem),
        'files':[files[name] for name in sorted(files)],'expected_new_outputs_installed':False,
        'proposal_installed':proposal_path is not None,'production_admission':False}
    _write(directory/'capture-manifest.json',canonical_bytes(manifest))
    bind_problem(problem.profile,root=directory)
    return manifest


def _scalar_steps(output):
    q = Path(QUALIFICATION)
    names = ('global-source','global-audit','supported-source','supported-audit',
             'declaration','declaration-audit','topology-source','topology-audit')
    paths = {name:Path(output)/(name+'.json') for name in names}
    return (
        ('qualify-reference-v1.py',['--inputs',q/'qualification-inputs-v2.json','--output',paths['global-source']], 'reference-source-v2.json'),
        ('verify-reference-v1.py',['--inputs',q/'qualification-inputs-v2.json','--source',paths['global-source'],'--output',paths['global-audit']], 'reference-audit-v2.json'),
        ('qualify-reference-v2.py',['--inputs',q/'qualification-inputs-v3.json','--output',paths['supported-source']], 'supported-reference-source-v1.json'),
        ('verify-reference-v2.py',['--inputs',q/'qualification-inputs-v3.json','--source',paths['supported-source'],'--output',paths['supported-audit']], 'supported-reference-audit-v1.json'),
        ('declare-target-v1.py',['--inputs',q/'parameter-inputs-v1.json','--reference-audit',paths['supported-audit'],'--output',paths['declaration']], 'target-declaration-source-v1.json'),
        ('verify-target-declaration-v1.py',['--inputs',q/'parameter-inputs-v1.json','--source',paths['declaration'],'--reference-audit',paths['supported-audit'],'--output',paths['declaration-audit']], 'target-declaration-audit-v1.json'),
        ('qualify-prime-five-topology-v1.py',['--inputs',q/'topology-inputs-v1.json','--output',paths['topology-source']], 'topology-source-v1.json'),
        ('verify-prime-five-topology-v1.py',['--inputs',q/'topology-inputs-v1.json','--source',paths['topology-source'],'--output',paths['topology-audit']], 'topology-audit-v1.json'))


def _scalar_data_tree(task,staging):
    """Copy verified code/inputs to owned writable data, outside sealed runtime."""
    prefix = task['scalar_root']
    refs = {ref.path:ref for ref in staging.spec.code_refs}
    manifest_name = prefix+'/capture-manifest.json'
    _require(manifest_name in refs,'scalar capture omitted from owned closure')
    manifest = _json(_raw(ROOT,refs[manifest_name],8*MIB))
    destination = staging.root/'attempts'/staging.attempt_id/'scalar-code-inputs'
    destination.mkdir(parents=True,exist_ok=True)
    for row in manifest['files']:
        ref = ArtifactRef(**row['artifact'])
        name = prefix+'/'+ref.path
        _require(name in refs and refs[name].sha256==ref.sha256 and refs[name].size==ref.size,
                 'scalar dependency differs from owned capture')
        raw = _raw(ROOT,refs[name],8*MIB)
        target = destination/ref.path
        if target.exists():
            _require(_bytes(target)==raw,'changed scalar code/input after installation')
        else:
            _write(target,raw)
    return destination


def evaluate_premise(task,staging):
    from scripts.whole_source import execution
    from flint import ctx
    from scripts.whole_source.storage import scalar_builtins
    _require(execution._WORKER is not None and execution._WORKER[-1] is staging and
             execution._WORKER[0].role=='analytic','scalar checking requires owned analytic worker')
    index = task['index']
    steps = _scalar_steps(task['output'])
    _require(type(index) is int and 0<=index<len(steps),'unknown scalar premise')
    script,args,expected = steps[index]
    scalar_root = _scalar_data_tree(task,staging)
    _require(task['output']==QUALIFICATION+'/data/owned-native-reconstruction',
             'scalar outputs must remain inside their original input bundle')
    (scalar_root/task['output']).mkdir(parents=True,exist_ok=True)
    program = scalar_root/QUALIFICATION/script
    argv = [str(program),*(str(value) if str(value).startswith('--') else
                           str(Path(value) if Path(value).is_absolute() else scalar_root/value) for value in args)]
    before_argv,before_path,before_prec,before_threads = sys.argv[:],sys.path[:],ctx.prec,ctx.threads
    before_modules = {name:value for name,value in sys.modules.items()
                      if name=='scripts' or name.startswith('scripts.')}
    for name in before_modules:
        sys.modules.pop(name)
    try:
        sys.argv = argv
        sys.path.insert(0,str(scalar_root))
        legacy_package = __import__('scripts')
        legacy_package.__path__ = [str(scalar_root/'scripts')]
        try:
            runpy.run_path(str(program),run_name='__main__',
                           init_globals={'__builtins__': scalar_builtins()})
        except SystemExit as exc:
            _require(exc.code in (None,0),'scalar premise program rejected')
    finally:
        sys.argv,sys.path[:],ctx.prec,ctx.threads = before_argv,before_path,before_prec,before_threads
        for name in list(sys.modules):
            if name=='scripts' or name.startswith('scripts.'):
                sys.modules.pop(name)
        sys.modules.update(before_modules)
    path = Path(args[-1])
    path = path if path.is_absolute() else scalar_root/path
    raw = _bytes(path)
    old = _bytes(scalar_root/QUALIFICATION/'data'/expected)
    _require(raw==old,'fresh scalar premise differs from frozen reviewed declaration')
    return {'status':'VERIFIED_FRESH_SCALAR_PREMISE','index':index,'output':_record(path),
        'program':asdict(_ref(ROOT,task['scalar_root']+'/'+QUALIFICATION+'/'+script)),
        'executed_program':_record(program),
        'byte_identical_to_reviewed_scalar':True,'production_admission':False}


def run_premises(problem,base_spec,base_plan,directory,*,code_root=ROOT):
    root,directory = Path(code_root).resolve(),Path(directory).resolve()
    directory.mkdir(parents=True,exist_ok=False)
    closure = directory/'installed'
    capture_inputs(problem,closure,code_root=root)
    # Scalar programs run from the installed closed tree, not mutable originals.
    paths = [p.relative_to(root).as_posix() for p in closure.rglob('*') if p.is_file()]
    refs = {r.path:r for r in base_spec.code_refs}
    for name in (*paths,'scripts/whole_source/retention.py'):
        refs[name] = _ref(root,name)
    spec = CollectionSpec.create(problem,role='analytic',quantities=base_spec.quantities,
        partition=base_spec.partition,backend='python-flint',backend_version=base_spec.backend_version,
        native_threads=1,code_refs=tuple(refs[name] for name in sorted(refs)),bounds=base_spec.bounds,code_root=root)
    origin_path = directory/'scalar-origin.json'
    origin = _json(_bytes(root/base_plan.provenance.path))
    origin['files'] = [asdict(r) for r in spec.code_refs]
    _write(origin_path,canonical_bytes(origin))
    plan = replace(base_plan,collection_sha256=spec.collection_id,
        task_program=_ref(root,'scripts/whole_source/retention.py'),task_function='evaluate_premise',
        precision_bits=6144,max_tasks=8,provenance=_ref(root,origin_path.relative_to(root).as_posix()))
    from scripts.whole_source.resources import auto_plan
    plan = auto_plan(plan,parallel=False,helper_root=root)
    spec = replace(spec,native_threads=plan.threads)
    spec._validate()
    plan = replace(plan,collection_sha256=spec.collection_id)
    # The worker uses a separately declared scalar root from this bound task.
    with CollectionLock.acquire(directory/'collection',spec) as lock:
        with WorkloadExecution(lock,spec,plan,code_root=root) as execution:
            rows = []
            for index in range(8):
                execution.run_stage('premise-'+str(index),[_request(index=index,
                    scalar_root=closure.relative_to(root).as_posix(),
                    output=QUALIFICATION+'/data/owned-native-reconstruction')])
                rows.append(next(execution.read_results('premise-'+str(index)))['result'])
            result = {'format':'whole-source-scalar-premises-v1','status':'VERIFIED_FRESH_SCALAR_PREMISES',
                'problem_id':problem_id(problem),'outputs':rows,
                'owned_receipts':exact_telemetry(execution.receipts),'production_admission':False}
            _write(directory/'premises-receipt.json',canonical_bytes(result))
    return result


def _verify_receipts(directory, *, code_root=ROOT):
    """Verify selected recovery producers and all cleanup; keep legacy stage checks."""
    from scripts.whole_source.receipts import discover_receipts, verify_stage
    if (Path(directory)/'coordinator/context.json').exists():
        from scripts.whole_source.selection import selected_execution_roots
        _check_phase_history(directory)
        selected = []
        for _, folder in selected_execution_roots(directory):
            selected.extend(_verify_receipts(folder, code_root=code_root))
        _require(selected, 'no complete selected phase execution evidence')
        unique = {str(Path(row['directory'])/row['artifact']['path']): row for row in selected}
        return [unique[name] for name in sorted(unique)]
    paths = discover_receipts(directory)
    _require(paths, 'missing owned execution receipts')
    rows, collections = [], set()
    from scripts.whole_source.recovery import selected_receipts
    for path in paths:
        collection = path.parents[3] if path.parents[2].name == 'attempts' else None
        if collection is not None and (collection/'source-execution.json').exists():
            if collection in collections:
                continue
            from scripts.whole_source.pipeline import SourceReader, source_execution_document, verify_source_execution
            execution = source_execution_document(collection/'source-manifest.json')
            problem = bind_problem('retained-t081', root=Path(code_root))
            spec = CollectionSpec.from_dict(problem, execution['collection'], code_root=Path(code_root))
            control = _json(_bytes(collection/'source-manifest.json'))['control']
            reader = SourceReader(collection/'source-manifest.json', spec, control=control)
            selected = verify_source_execution(reader)
            rows.extend(_record(collection/ref['path']) for ref in selected['receipts'])
            collections.add(collection)
        else:
            if collection is not None:
                if collection in collections:
                    continue
                selected = selected_receipts(collection)
                if selected is not None:
                    _require(selected, 'no committed recovery producer evidence')
                    rows.extend(verify_stage(Path(row['directory'])/row['artifact']['path'])['record']
                                for row in selected)
                    collections.add(collection)
                    continue
            rows.append(verify_stage(path)['record'])
    _require(rows, 'no complete owned stage evidence')
    return sorted(rows, key=lambda row: str(Path(row['directory'])/row['artifact']['path']))


def _selected_phase(run, phase):
    from scripts.whole_source.coordinator import read_phase_records
    rows = read_phase_records(run)
    _require(phase in rows, 'missing committed coordinator phase: '+phase)
    return rows[phase]


def reviewed_consequence(problem,blocks):
    from scripts.whole_source.exact_global import assess
    _require(len(blocks)==2,'both complete parity reports required')
    values = []
    for p,block in enumerate(blocks):
        _require(block['dimension']==413 and block['parity']==p and
                 block['scope']=='SOURCE_CONDITIONAL' and len(block['row_margins'])==413,
                 'incomplete or nonfresh exact scope')
        rows = [decode_rational(v,65536) for v in block['row_margins']]
        margin = decode_rational(block['margin'],65536)
        _require(min(rows)==margin and block['modular']['global_input_entries']==413**2 and
                 block['modular']['prime']==65521 and 0<block['modular']['residue']<65521 and
                 block['modular']['nonsingular'] is True,'incomplete global exact proof')
        selected = {key:decode_rational(block[key],65536) for key in
                    ('width','goal','margin','tau','direction_upper','direction_mass')}
        _require(selected['goal']==problem.numerical_goal,'changed exact numerical goal')
        selected.update(modular_nonsingular=True,direction_index=block['direction_index'])
        values.append(selected)
    result = assess(values,eta=problem.eta,m=problem.m,b_K=problem.b_K,delta=problem.delta)
    _require(result['positive_paid_lower'] is True and result['gamma']>=FLOOR,
             'complete source-norm consequence does not meet retained floor')
    return result


def _scientific_exact(report):
    return {'format':report['format'],'status':report['status'],'proof_scope':report['proof_scope'],
        'problem_id':report['problem_id'],'blocks':report['blocks'],'assessment':report['assessment'],
        'source_manifest':report['source']['manifest'],'proposal_artifact':report['proposal']['artifact'],
        'analytical_source_acceptance':report['analytical_source_acceptance'],
        'production_admission':report['production_admission']}


def compare_science(first,second):
    from scripts.whole_source.pipeline import compare_source_audits
    reports = [_json(_bytes(Path(run)/'pipeline-result.json')) for run in (first,second)]
    def path(record):
        return Path(record['directory'])/record['artifact']['path']
    compared = compare_source_audits(path(reports[0]['source']),path(reports[0]['audit']),
                                    path(reports[1]['source']),path(reports[1]['audit']))
    _require(compared['control'] is False and compared['entries_compared']==FULL_ENTRIES and
             compared['complete_parity_dimensions']==[413,413],
             'full-reference scientific replay required')
    before,after = (_document(row['exact']) for row in reports)
    _require(canonical_bytes(_scientific_exact(before))==canonical_bytes(_scientific_exact(after)),
             'replayed exact mathematics differs')
    return {'status':'PASS_COMPLETE_SCIENTIFIC_REPLAY_COMPARISON','entries_compared':FULL_ENTRIES,
        'complete_parity_dimensions':[413,413],'exact_row_margins_compared':826,
        'exclusions':REPLAY_EXCLUSIONS,'production_admission':False}


def _publish_identical(path, value):
    raw = canonical_bytes(value)
    if Path(path).exists():
        _require(_bytes(path) == raw, 'conflicting coordinator publication: '+str(path))
    else:
        _write(Path(path), raw)


def _check_phase_history(run):
    """Nonselected failed attempts remain evidence and must have verified cleanup."""
    from scripts.whole_source.recovery import check_history
    run = Path(run)
    check_history(run)
    for collection in run.rglob('attempts'):
        if collection.is_dir():
            check_history(collection.parent)


def _phase_outputs(phase, directory, *, replay_proposal=None):
    directory = Path(directory)
    paths = {
        'prepare': {'problem': 'source-inputs/problem.json',
                    'source_execution': 'source-inputs/execution.json',
                    'premises': 'premises/premises-receipt.json'},
        'source': {'source': 'producer/source-manifest.json',
                   'source_publication': 'producer/source-execution.json'},
        'audit': {'audit': 'analytical-receipt.json', 'audit_execution': 'audit-execution.json'},
        'proposal': {'proposal': 'work/proposal.json'},
        'exact-inputs': {'problem': 'problem.json', 'execution': 'execution.json', 'operands': 'operands.json'},
        'exact': {'exact': 'report.json'},
        'controls': {'controls': 'controls-receipt.json'},
        'replay': {'replay': 'replay-receipt.json'},
    }
    if phase == 'proposal' and replay_proposal is not None:
        return {'proposal': replay_proposal}
    return {key: _record(directory/name) for key, name in paths[phase].items()}


def _phase_path(record):
    return Path(record['directory'])/record['artifact']['path']


def _dispatch_phase(phase, directory, prior, problem, config, run, root, *, reuse=False,
                    proposal_input=None):
    from scripts.whole_source.pipeline import prepare_source_inputs, run_source, run_audit, _bind as bind_source
    from scripts.whole_source.proposal import prepare_proposal_inputs, run_proposal
    from scripts.whole_source.exact import prepare_exact_inputs, run_exact
    origin = {'origin_git_commit': config['origin_git_commit'], 'origin_git_dirty': config['origin_git_dirty']}
    directory = Path(directory)
    if phase == 'prepare':
        inputs = prepare_source_inputs(problem, directory/'source-inputs', code_root=root,
                                       tile_modes=32, **origin)
        _, _, bound = bind_source(inputs['problem'], inputs['execution'], root)
        run_premises(problem, *bound['analytic'], directory/'premises', code_root=root)
    elif phase == 'source':
        inputs = prior['prepare']
        run_source(_phase_path(inputs['problem']), _phase_path(inputs['source_execution']),
                   directory, resume=reuse, code_root=root)
    elif phase == 'audit':
        inputs = prior['prepare']
        run_audit(_phase_path(inputs['problem']), _phase_path(prior['source']['source']),
                  _phase_path(inputs['source_execution']), directory, code_root=root)
    elif phase == 'proposal':
        if proposal_input is not None:
            directory.mkdir(parents=True, exist_ok=False)
            _publish_identical(directory/'installed-proposal.json', {'proposal': _record(proposal_input)})
        else:
            if not reuse:
                inputs = prepare_proposal_inputs(problem, _phase_path(prior['source']['source']),
                    directory/'inputs', code_root=root, **origin)
            else:
                inputs = {'problem': directory/'inputs/problem.json', 'execution': directory/'inputs/execution.json'}
            run_proposal(inputs['problem'], _phase_path(prior['source']['source']), inputs['execution'],
                         directory/'work', code_root=root, resume=reuse)
    elif phase == 'exact-inputs':
        prepare_exact_inputs(problem, _phase_path(prior['source']['source']),
            _phase_path(prior['proposal']['proposal']), directory, code_root=root, **origin)
    elif phase == 'exact':
        inputs = prior['exact-inputs']
        run_exact(_phase_path(inputs['problem']), _phase_path(prior['source']['source']),
                  _phase_path(prior['proposal']['proposal']), _phase_path(inputs['execution']),
                  directory, code_root=root, resume=reuse)
    elif phase == 'controls':
        from scripts.whole_source.controls import run_controls
        inputs = prior['prepare']
        run_controls(_phase_path(inputs['problem']), _phase_path(inputs['source_execution']),
            _phase_path(prior['source']['source']), _phase_path(prior['audit']['audit']),
            _phase_path(prior['proposal']['proposal']), _phase_path(prior['exact']['exact']),
            directory, code_root=root)
    elif phase == 'replay':
        replay(run, directory, code_root=root)
    else:
        raise ContractError('unknown coordinator phase')


def _resume_phase(phase, directory):
    markers = {'source': 'pipeline-context.json',
               'proposal': 'work/recovery-terminal/recovery/head.json',
               'exact': 'collection/recovery/head.json'}
    return phase in markers and (Path(directory)/markers[phase]).is_file()


def _open_coordinator(problem, config, output, root, *, resume, proposal_input=None):
    from scripts.whole_source.coordinator import PhaseJournal
    _check_loaded_implementation(root)
    if resume:
        start = _record(output/'implementation/start.json')
        value = _document(start)
        code, capture, _ = _implementation_code(root)
        _reviewed_code(value['code'], code)
        _require(value['phase'] == 'science' and value['problem_id'] == problem_id(problem) and
                 value['runtime_versions'] == _runtime_versions() and value['inherited_capture'] == capture,
                 'changed coordinator implementation context')
        for row in code:
            ref = ArtifactRef(**row['artifact'])
            _raw(output/'implementation', ArtifactRef('snapshots/'+ref.sha256, ref.sha256, ref.size), 8*MIB)
    else:
        start = _capture_implementation(problem, output, root, 'science')
    context = {'problem_id': problem_id(problem), 'configuration': config,
               'implementation': start,
               'proposal_input': None if proposal_input is None else _record(proposal_input)}
    return PhaseJournal(output, context, resume=resume)


def _publish_pipeline(problem, config, output, root, journal):
    from scripts.whole_source.coordinator import SCIENCE_PHASES
    prior = {name: journal.completed[name]['outputs'] for name in SCIENCE_PHASES}
    exact = _document(prior['exact']['exact'])
    result = {'format': 'whole-source-pipeline-result-v3', 'status': 'COMPLETE_FRESH_SOURCE_AUDIT_AND_EXACT',
        'problem_id': problem_id(problem), 'source': prior['source']['source'],
        'audit': prior['audit']['audit'], 'proposal': prior['proposal']['proposal'],
        'exact': prior['exact']['exact'], 'premises': prior['prepare']['premises'],
        'source_execution': prior['prepare']['source_execution'], 'problem': prior['prepare']['problem'],
        'source_publication': prior['source']['source_publication'],
        'audit_execution': prior['audit']['audit_execution'],
        'implementation': _record(output/'implementation/start.json'),
        'phase_chain': [journal.completed[name]['record'] for name in SCIENCE_PHASES],
        'gamma': exact['assessment']['gamma'], 'fresh_proposal': journal.context['proposal_input'] is None,
        'production_admission': False}
    _publish_identical(output/'pipeline-result.json', result)
    completion = {'format': 'whole-source-coordinator-completion-v1', 'start': result['implementation'],
                  'outputs': {'pipeline': _record(output/'pipeline-result.json')}, 'production_admission': False}
    _publish_identical(output/'implementation/complete.json', completion)
    return result


def _execute(problem, config, output, root, *, proposal_input=None, resume=False, through='exact'):
    from scripts.whole_source.admission import admitted_phase, admit_attempt, topology, bind_phase_attempt
    from scripts.whole_source.coordinator import PHASES, SCIENCE_PHASES
    from scripts.whole_source.selection import validate_phase
    _require(through in PHASES, 'unknown coordinator stop phase')
    with admitted_phase('validation', problem, output, root):
        _check_phase_history(output)
        journal = _open_coordinator(problem, config, output, root, resume=resume, proposal_input=proposal_input)
        if resume and journal.completed:
            _selected_supervision(output, root)
    replay_proposal = journal.context['proposal_input']
    prior = {}
    for phase in PHASES[:PHASES.index(through)+1]:
        existing = journal.completed.get(phase)
        pending = journal.pending
        scope = 'validation' if existing is not None else phase
        directory = None if existing is None and pending is None else Path((existing or pending)['directory'])
        with admitted_phase(scope, problem, output, root, directory=directory, inputs=prior) as admission:
            if phase == 'controls':
                _publish_pipeline(problem, config, output, root, journal)
            if existing is not None:
                validate_phase(phase, existing['outputs'], Path(existing['directory']), run=output,
                               root=root, prior=prior, replay_proposal=replay_proposal)
                prior[phase] = existing['outputs']
                continue
            recovered = False
            if pending is not None:
                directory = Path(pending['directory'])
                original_admission = Path(output)/'admission'/('attempt-'+phase+'-'+directory.name+'.json')
                _require(original_admission.is_file(), 'missing original phase admission')
                bind_phase_attempt(admission, directory, output)
                try:
                    candidate = _phase_outputs(phase, directory, replay_proposal=replay_proposal)
                except FileNotFoundError:
                    pass
                else:
                    if phase != 'proposal' or replay_proposal is None or (directory/'installed-proposal.json').is_file():
                        validate_phase(phase, candidate, directory, run=output, root=root,
                                       prior=prior, replay_proposal=replay_proposal)
                        journal.complete(phase, candidate)
                        recovered = True
            if not recovered:
                reuse = pending is not None and _resume_phase(phase, pending['directory'])
                admit_attempt(journal, phase, topology(problem), reuse=reuse)
                directory, reuse = journal.begin(phase, prior, reuse=reuse)
                bind_phase_attempt(admission, directory, output)
                _dispatch_phase(phase, directory, prior, problem, config, output, root,
                                reuse=reuse, proposal_input=proposal_input)
                candidate = _phase_outputs(phase, directory, replay_proposal=replay_proposal)
                validate_phase(phase, candidate, directory, run=output, root=root,
                               prior=prior, replay_proposal=replay_proposal)
                journal.complete(phase, candidate)
            prior[phase] = journal.completed[phase]['outputs']
    science_complete = all(name in journal.completed for name in SCIENCE_PHASES)
    if science_complete:
        with admitted_phase('validation', problem, output, root):
            _publish_pipeline(problem, config, output, root, journal)
            if through == 'replay':
                ready = {'status': 'COMPLETE_EVIDENCE_PENDING_INDEPENDENT_REVIEW',
                         'pipeline_result': _record(output/'pipeline-result.json'),
                         'controls': prior['controls']['controls'], 'replay': prior['replay']['replay'],
                         'production_admission': False}
                _publish_identical(output/'ready-for-review.json', ready)
                return ready
    return {'status': 'PAUSED_AFTER_VERIFIED_PHASE', 'completed_through': through,
            'science_complete': science_complete,
            'production_admission': False, 'reference_qualification_accepted': False}


def _replay_process(command, tree, output, root):
    """Bound captured replay streams; cooperative interruption is not a deadline."""
    import subprocess
    import threading
    from scripts.whole_source.storage import guarded_open
    from scripts.whole_source.admission import waiting_caller
    failures = []
    lock = threading.Lock()
    with waiting_caller(helper_root=root):
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        with guarded_open(output/'stdout.txt') as stdout, guarded_open(output/'stderr.txt') as stderr:
            process = subprocess.Popen(command, cwd=tree, env=env, stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            def copy(incoming, outgoing):
                size = 0
                failed = False
                try:
                    while raw := incoming.read(65536):
                        if failed:
                            continue
                        try:
                            _require(size+len(raw) <= 4*MIB, 'captured replay stream allowance exceeded')
                            outgoing.write(raw)
                            size += len(raw)
                        except BaseException as error:
                            failed = True
                            with lock:
                                failures.append(error)
                                try:
                                    process.stdin.write(b'!')
                                    process.stdin.flush()
                                except (OSError, BrokenPipeError):
                                    pass
                finally:
                    incoming.close()
            readers = [threading.Thread(target=copy, args=(incoming, outgoing), daemon=True)
                       for incoming, outgoing in ((process.stdout, stdout), (process.stderr, stderr))]
            for reader in readers:
                reader.start()
            try:
                process.wait()
            except BaseException:
                try:
                    process.stdin.write(b'!')
                    process.stdin.flush()
                except (OSError, BrokenPipeError):
                    pass
                raise
            finally:
                process.stdin.close()
                for reader in readers:
                    reader.join()
            if failures:
                raise ContractError('captured replay stream refused: '+str(failures[0]))
            return process.returncode


def replay(run_dir,output_dir,*,code_root=ROOT):
    root,run,output = Path(code_root).resolve(),Path(run_dir).resolve(),Path(output_dir).resolve()
    from scripts.whole_source.selection import validate_pipeline
    from scripts.whole_source.supervision import require_current
    require_current()
    result, _ = validate_pipeline(run, root)
    problem = bind_problem('retained-t081',root=root)
    output.mkdir(parents=True,exist_ok=False)
    _capture_implementation(problem,output,root,'replay')
    tree = output/'captured-root'
    proposal = Path(result['proposal']['directory'])/result['proposal']['artifact']['path']
    capture_inputs(problem,tree,code_root=root,proposal_path=proposal)
    child_run = tree/run.relative_to(root)
    _require(not any((child_run/name).exists() for name in
                     ('source','audit','exact','prepare','proposal','coordinator','pipeline-result.json')),
             'expected scientific outputs leaked into replay')
    child_run.mkdir(parents=True,exist_ok=True)
    _new_copy(run/'integration-execution.json',child_run/'integration-execution.json')
    child_proposal = tree/proposal.relative_to(root)
    # Imported module ROOT is not the captured module. Execute a separate Python
    # interpreter whose project imports resolve only from the captured tree.
    entry = "import sys;sys.path.insert(0,sys.argv[1]);from scripts.whole_source.retention import _replay_child;_replay_child(sys.argv[2],sys.argv[3],sys.argv[4])"
    command = [sys.executable,'-I','-B','-c',entry,str(tree),str(child_run),
               str(child_run/'integration-execution.json'),str(child_proposal)]
    returncode = _replay_process(command, tree, output, root)
    _require(returncode==0,'captured scientific replay failed')
    compared = compare_science(run,child_run)
    receipt = {'format':'whole-source-scientific-replay-v1',**compared,
        'original_run':_record(run/'pipeline-result.json'),'replayed_run':_record(child_run/'pipeline-result.json'),
        'capture':_record(tree/'capture-manifest.json'),'expected_new_outputs_installed':False,
        'argv':command,'exit_code':returncode,'shared_installed_arithmetic_runtime':True,
        'owned_receipts':_verify_receipts(child_run)}
    _write(output/'replay-receipt.json',canonical_bytes(receipt))
    _complete_implementation(output,root,{'replay':_record(output/'replay-receipt.json')})
    return receipt


def _replay_child(run_dir,config_path,proposal_path):
    import _thread
    import threading
    from scripts.whole_source.supervision import require_current, cancel_current
    require_current()
    def cancel():
        if sys.stdin.buffer.read(1) == b'!':
            cancel_current()
            _thread.interrupt_main()
    threading.Thread(target=cancel, daemon=True).start()
    run = Path(run_dir)
    from scripts.whole_source.admission import bootstrap_scope
    with bootstrap_scope(ROOT, input_count=1):
        config = _json(_bytes(Path(config_path)))
        _require(config.get('format') == 'whole-source-integrated-execution-v5' and
                 config.get('lifecycle_supervision') == 'windows-lifecycle-v1',
                 'captured replay requires current supervised execution policy')
        problem = bind_problem('retained-t081',root=ROOT)
        for ref in config['code']:
            _raw(ROOT,ArtifactRef(**ref),8*MIB)
    with _slice_writer(run, resume=True):
        _execute(problem, config, run, ROOT, proposal_input=Path(proposal_path))


def _inventory_files(directory,excluded):
    from scripts.whole_source.admission import admit_names
    admit_names(directory)
    return sorted(p.relative_to(directory).as_posix() for p in directory.rglob('*')
                  if p.is_file() and p.relative_to(directory).as_posix() not in excluded)


def _write_inventory_snapshot(directory,path,names):
    """Publish canonical JSONL without retaining all member rows or encoded bytes."""
    temporary = path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
    _require(not path.exists(),'immutable inventory snapshot already exists')
    from scripts.whole_source.storage import current_budget
    budget = current_budget(temporary)
    with (budget.stream(temporary) if budget is not None else temporary.open('xb')) as stream:
        for name in names:
            raw = canonical_bytes({'path':name,**_hash_file(_safe(directory,name))})
            _require(stream.write(raw)==len(raw),'short inventory snapshot write')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary,path)


def _snapshot_rows(directory,ref):
    ref = ArtifactRef(**ref)
    path = _safe(directory,ref.path)
    _require(_hash_file(path)=={'size':ref.size,'sha256':ref.sha256},'changed inventory snapshot')
    with path.open('rb') as stream:
        while raw := stream.readline(8*MIB+1):
            _require(len(raw)<=8*MIB,'oversized inventory member')
            yield _json(raw)


def _verify_inventory_rows(directory,rows):
    """Yield ordered, hash-checked members; consumers must exhaust the iterator."""
    previous = ''
    for row in rows:
        _require(type(row) is dict and set(row)=={'path','size','sha256'} and
                 type(row['path']) is str and row['path']>previous,'invalid inventory member ordering')
        ref = ArtifactRef(**row)
        _require(_hash_file(_safe(directory,ref.path))=={'size':ref.size,'sha256':ref.sha256},
                 'retained member changed')
        previous = row['path']
        yield row


def _inventory_intent(directory,ref,snapshot):
    document = _json(_raw(directory,ArtifactRef(**ref),8*MIB))
    _require(document=={'format':'whole-source-inventory-intent-v1','snapshot':snapshot},
             'invalid pending inventory intent')


def _verify_inventory_document(directory,manifest):
    _require(manifest['excluded']==['.slice.lock','retained-manifest.json'],'invalid retained inventory')
    names = [ref['path'] for ref in manifest['shards']]
    _require(names==sorted(set(names)),'missing, extra or repeated inventory shard')
    active = set(names)
    if manifest['format']=='whole-source-retained-inventory-v1':
        _require(names==sorted(p.relative_to(directory).as_posix()
            for p in (directory/'inventory').rglob('*') if p.is_file()),
            'missing, extra or repeated inventory shard')
        expected = []
        for shard in manifest['shards']:
            for row in _json(_raw(directory,ArtifactRef(**shard),8*MIB))['files']:
                _require(_hash_file(_safe(directory,row['path']))==
                         {'size':row['size'],'sha256':row['sha256']},'retained member changed')
                expected.append(row['path'])
        actual = [name for name in _inventory_files(directory,{'.slice.lock','retained-manifest.json'})
                  if not name.startswith('inventory/')]
        _require(expected==actual and len(expected)==len(set(expected)),'incomplete retained inventory')
        return len(expected)
    else:
        _require(set(manifest)=={'format','excluded','generation','snapshot','intent','shards',
                                'production_admission'} and
                 manifest['format']=='whole-source-retained-inventory-v2' and
                 manifest['production_admission'] is False,'invalid retained inventory')
        generation = manifest['generation']
        _require(type(generation) is str and len(generation)==32 and
                 all(c in '0123456789abcdef' for c in generation),'invalid inventory generation')
        prefix = 'inventory/'+generation+'/'
        _require(names==[prefix+'%06d.json'%i for i in range(len(names))] and
                 manifest['snapshot']['path']==prefix+'snapshot.jsonl' and
                 manifest['intent']['path']==prefix+'intent.json','foreign inventory generation metadata')
        _inventory_intent(directory,manifest['intent'],manifest['snapshot'])
        active.update((manifest['snapshot']['path'],manifest['intent']['path']))
    snapshot = iter(_snapshot_rows(directory,manifest['snapshot']))
    exhausted = object()
    def matched_rows():
        for shard in manifest['shards']:
            document = _json(_raw(directory,ArtifactRef(**shard),8*MIB))
            _require(type(document) is dict and set(document)=={'files'} and
                     type(document['files']) is list,'invalid inventory shard')
            for row in document['files']:
                _require(next(snapshot,exhausted)==row,'inventory snapshot coverage differs')
                yield row
            # Drop the decoded shard before requesting the next one.
            del document
    expected = [row['path'] for row in _verify_inventory_rows(directory,matched_rows())]
    _require(next(snapshot,exhausted) is exhausted,'inventory snapshot coverage differs')
    excluded = {'.slice.lock','retained-manifest.json'} | active
    _require(expected==_inventory_files(directory,excluded),'incomplete retained inventory')
    return len(expected)


def verify_inventory(directory,manifest_path=None):
    directory = Path(directory).resolve()
    path = directory/'retained-manifest.json' if manifest_path is None else Path(manifest_path)
    manifest = _json(_bytes(path))
    members = _verify_inventory_document(directory,manifest)
    return {'status':'PASS_RETAINED_INVENTORY','members':members,'manifest':_record(path)}


def _verify_pending_inventories(directory):
    for path in sorted((directory/'inventory').glob('*/intent.json')):
        try:
            intent = _json(_bytes(path))
        except ValueError as exc:
            raise ContractError('invalid pending inventory intent') from exc
        _require(type(intent) is dict and set(intent)=={'format','snapshot'} and
                 intent['format']=='whole-source-inventory-intent-v1' and
                 intent['snapshot']['path']==path.with_name('snapshot.jsonl').relative_to(directory).as_posix(),
                 'invalid pending inventory intent')
        pending = {}
        for shard in sorted(path.parent.glob('[0-9]*.json')):
            _require(shard.stem.isdecimal(),'invalid pending inventory shard')
            index = int(shard.stem)
            _require(shard.name=='%06d.json'%index,'unexpected pending inventory shard')
            pending[index] = shard
        rows = _verify_inventory_rows(directory,_snapshot_rows(directory,intent['snapshot']))
        index = 0
        while batch := list(islice(rows,4096)):
            shard = pending.pop(index,None)
            if shard is not None:
                _require(_bytes(shard)==canonical_bytes({'files':batch}),'conflicting pending inventory shard')
            index += 1
            del batch
        _require(not pending,'unexpected pending inventory shard')


def _seal(directory):
    directory = Path(directory).resolve()
    final = directory/'retained-manifest.json'
    # lstat preserves malformed and broken-link final markers rather than replacing them.
    try:
        final.lstat()
    except FileNotFoundError:
        pass
    else:
        return verify_inventory(directory)
    _verify_pending_inventories(directory)
    names = _inventory_files(directory,{'.slice.lock','retained-manifest.json'})
    generation = uuid.uuid4().hex
    folder = directory/'inventory'/generation
    folder.mkdir(parents=True,exist_ok=False)
    snapshot = folder/'snapshot.jsonl'
    _write_inventory_snapshot(directory,snapshot,names)
    del names
    snapshot_ref = asdict(_ref(directory,snapshot.relative_to(directory).as_posix()))
    intent = folder/'intent.json'
    _write(intent,canonical_bytes({'format':'whole-source-inventory-intent-v1','snapshot':snapshot_ref}))
    shards = []
    rows = iter(_snapshot_rows(directory,snapshot_ref))
    while batch := list(islice(rows,4096)):
        path = folder/('%06d.json'%len(shards))
        _write(path,canonical_bytes({'files':batch}))
        shards.append(asdict(_ref(directory,path.relative_to(directory).as_posix())))
        del batch
    manifest = {'format':'whole-source-retained-inventory-v2','excluded':['.slice.lock','retained-manifest.json'],
        'generation':generation,'snapshot':snapshot_ref,
        'intent':asdict(_ref(directory,intent.relative_to(directory).as_posix())),
        'shards':shards,'production_admission':False}
    _verify_inventory_document(directory,manifest)
    _write(final,canonical_bytes(manifest))
    return verify_inventory(directory)


def _runtime_versions():
    return {'python':sys.version,**{name:importlib.metadata.version(name)
            for name in ('python-flint','numpy','scipy')}}


def _implementation_code(root):
    """Closed current implementation plus directly reviewed inherited Python code."""
    root = Path(root)
    current = [asdict(_ref(root,name)) for name in sorted(set((*CODE,*_RUNTIME)))]
    capture_ref = _ref(root,OLD_CAPTURE+'/captured-source-inputs-v1.json')
    capture = _json(_raw(root,capture_ref,8*MIB))
    inherited,locations = [],{}
    for row in capture['files']:
        name = row['destination']
        if ('installed' not in row['roles'] or name.startswith(OLD_CANDIDATE)
                or not name.endswith('.py')):
            continue
        ref = ArtifactRef(name,row['sha256'],row['bytes'])
        stored = OLD_CAPTURE+'/'+row['stored']
        raw = _raw(root,ArtifactRef(stored,ref.sha256,ref.size),8*MIB)
        _require(name not in locations,'duplicate inherited implementation')
        locations[name] = (stored,raw)
        inherited.append(asdict(ref))
    code = ([{'kind':'current','artifact':ref} for ref in current] +
            [{'kind':'inherited','artifact':ref} for ref in sorted(inherited,key=lambda r:r['path'])])
    _require(inherited,'missing inherited executable dependency inventory')
    return code,asdict(capture_ref),locations


def _reviewed_code(code,expected):
    _require(type(code) is list and code==expected,
             'incomplete, duplicate or changed reviewed implementation')


def _check_loaded_implementation(root):
    """A source-root argument cannot relabel a different executing coordinator."""
    root = Path(root)
    _require(_hash_file(Path(__file__))==_hash_file(root/'scripts/whole_source/retention.py'),
             'coordinator differs from declared implementation')
    for name,module in tuple(sys.modules.items()):
        if name in ('scripts.run_observability','scripts.weil_whole_source_split') or name.startswith('scripts.whole_source'):
            path = getattr(module,'__file__',None)
            if path is not None:
                logical = name.replace('.','/')+('.py' if not hasattr(module,'__path__') else '/__init__.py')
                _require(_hash_file(Path(path))==_hash_file(root/logical),
                         'loaded coordinator module differs from frozen implementation')


def _capture_implementation(problem,directory,root,phase):
    """Capture coordinator code before work, separately from scientific identity."""
    root,directory = Path(root).resolve(),Path(directory).resolve()
    _check_loaded_implementation(root)
    code,capture,locations = _implementation_code(root)
    target = directory/'implementation'
    target.mkdir(exist_ok=False)
    (target/'snapshots').mkdir()
    for row in code:
        ref = ArtifactRef(**row['artifact'])
        raw = (_raw(root,ref,8*MIB) if row['kind']=='current' else locations[ref.path][1])
        path = target/'snapshots'/ref.sha256
        if not path.exists():
            _write(path,raw)
    value = {'format':'whole-source-coordinator-implementation-v1','phase':phase,
        'problem_id':problem_id(problem),'code':code,'inherited_capture':capture,
        'runtime_versions':_runtime_versions(),
        'argv':list(sys.argv),'production_admission':False}
    _write(target/'start.json',canonical_bytes(value))
    return _record(target/'start.json')


def _complete_implementation(directory,root,outputs):
    directory = Path(directory)
    start = _record(directory/'implementation/start.json')
    value = _document(start)
    code,capture,_ = _implementation_code(root)
    _reviewed_code(value['code'],code)
    _require(value.get('runtime_versions')==_runtime_versions(),
             'installed runtime changed during coordination')
    _require(value['inherited_capture']==capture,'inherited capture changed during coordination')
    for record in outputs.values():
        _document(record)
    _write(directory/'implementation/complete.json',canonical_bytes({
        'format':'whole-source-coordinator-completion-v1','start':start,
        'outputs':outputs,'production_admission':False}))
    return _record(directory/'implementation/complete.json')


def _coordinator_implementation(directory,phase,outputs,code,capture,pid):
    directory = Path(directory)
    start,complete = (_record(directory/'implementation'/name) for name in ('start.json','complete.json'))
    value,finished = _document(start),_document(complete)
    _require(value.get('runtime_versions')==_runtime_versions(),'coordinator runtime version differs')
    _require(value.get('format')=='whole-source-coordinator-implementation-v1' and
             value.get('phase')==phase and value.get('inherited_capture')==capture and
             value.get('problem_id')==pid and
             finished.get('format')=='whole-source-coordinator-completion-v1' and
             finished.get('start')==start and finished.get('outputs')==outputs,
             'missing or changed coordinator execution identity')
    _reviewed_code(value.get('code'),code)
    for row in code:
        ref = ArtifactRef(**row['artifact'])
        _raw(directory/'implementation',ArtifactRef('snapshots/'+ref.sha256,ref.sha256,ref.size),8*MIB)
    return {'start':start,'complete':complete}


def _stage_implementation(receipt_record,code,locations):
    """Check receipt-bound origin/runtime bytes, not the present working tree."""
    from scripts.whole_source.execution import ExecutionPlan
    receipt = json.loads(_raw(Path(receipt_record['directory']),
                             ArtifactRef(**receipt_record['artifact']),8*MIB))
    argv = receipt['argv']
    attempt = Path(receipt_record['directory']).parent
    stage_path = Path(argv[argv.index('--stage')+1]).resolve(strict=True)
    _require(stage_path==attempt/(receipt['stage']+'-stage.json') and
             _hash_file(stage_path)['sha256']==argv[argv.index('--stage-sha256')+1],
             'changed implementation stage binding')
    stage = _json(_bytes(stage_path))
    _require(stage.get('format')=='whole-source-task-stage-v2' and
             stage.get('code_origin',{}).get('path')=='code-origin.json',
             'stage lacks prospective code-origin evidence')
    origin_ref = ArtifactRef(**stage['code_origin'])
    origin = _json(_raw(attempt,origin_ref,8*MIB))
    plan = ExecutionPlan.from_dict(stage['plan'])
    _require(origin.get('format')=='whole-source-code-origin-v1' and
             stage['attempt_id']==attempt.name,'changed implementation origin')
    _require(stage.get('profile')=='retained-t081','unqualified reviewed execution profile')
    versions = _runtime_versions()
    expected_backend = (versions['python-flint'] if plan.backend in ('python-flint','python-flint-exact')
                        else versions['numpy']+'/'+versions['scipy'] if plan.backend=='numpy-scipy'
                        else 'stdlib-v1')
    _require(stage.get('python_version')==versions['python'] and plan.backend_version==expected_backend,
             'executed installed runtime version differs')
    current = {r['artifact']['path']:r['artifact'] for r in code if r['kind']=='current'}
    inherited = {r['artifact']['path']:r['artifact'] for r in code if r['kind']=='inherited'}
    stored_legacy = {stored:name for name,(stored,_) in locations.items()}
    origin_rows = origin['files']
    names = [r['path'] for r in origin_rows]
    _require(names==sorted(set(names)) and set(_RUNTIME)<=set(names),
             'incomplete or duplicate executed origin')
    refs = {r['path']:r for r in origin_rows}
    _require(all(refs.get(r['path'])==r for r in stage['collection']['code_refs']) and
             refs.get(plan.task_program.path)==asdict(plan.task_program) and
             current.get(plan.task_program.path)==asdict(plan.task_program),
             'executed task/collection differs from reviewed implementation')
    task_path = Path(stage['task_file'])
    _require(task_path.parent==attempt and _hash_file(task_path)['sha256']==stage['task_sha256'],
             'changed implementation task spool')
    scalar_roots = set()
    contexts = origin.get('reader_contexts',[])
    _require(type(contexts) is list and all(type(p) is str and p.endswith('/source-context') for p in contexts) and
             contexts==sorted(set(contexts)) and
             (not contexts or plan.task_function in ('evaluate_exact','evaluate_proposal')),
             'unclassified historical reader context')
    with task_path.open('rb') as stream:
        for line in stream:
            _require(len(line)<=plan.task_bytes+1,'oversized implementation task')
            task = _json(line)
            if plan.task_function=='evaluate_premise':
                scalar_roots.add(task['scalar_root']+'/')
    for row in origin_rows:
        ref = ArtifactRef(**row)
        _raw(attempt/'runtime',ref,8*MIB)
        logical,expected = ref.path,None
        if logical in current:
            expected = current[logical]
        elif logical in stored_legacy:
            expected = inherited[stored_legacy[logical]]
        else:
            scalar_prefix = next((prefix for prefix in scalar_roots if logical.startswith(prefix)),None)
            if scalar_prefix:
                logical = logical[len(scalar_prefix):]
                expected = current.get(logical) or inherited.get(logical)
                if expected is None and logical in stored_legacy:
                    expected = inherited[stored_legacy[logical]]
            elif any(logical.startswith(prefix+'/') for prefix in contexts):
                # Reader-only historical metadata, never the task program/import root.
                _require(ref.path!=plan.task_program.path,'source context executed as implementation')
                continue
        if expected is not None:
            _require((ref.sha256,ref.size)==(expected['sha256'],expected['size']),
                     'executed code differs from frozen reviewed implementation')
        else:
            _require(not ref.path.endswith(('.py','.pyc','.pyd','.so','.dll')),
                     'unclassified executed implementation dependency')
    for name,digest in _HELPERS.items():
        logical = BUNDLE+'/'+name
        ref = current.get(logical)
        _require(ref is not None and ref['sha256']==digest,'unreviewed neutral execution helper')
        _raw(attempt/'runtime',ArtifactRef(**ref),8*MIB)
    problem = bind_problem(stage['profile'],root=attempt/'runtime')
    allowed = set(refs) | {r.path for r in problem.evidence} | {BUNDLE+'/'+name for name in _HELPERS}
    actual = {p.relative_to(attempt/'runtime').as_posix()
              for p in (attempt/'runtime').rglob('*') if p.is_file()}
    _require(actual==allowed,'unbound or missing captured implementation input')
    return {'receipt':receipt_record,'stage':_record(stage_path),
            'origin':{'directory':str(attempt),'artifact':asdict(origin_ref)},
            'role':plan.role,'function':plan.task_function}


def _phase_supervision(run, phase, row, admitted, current):
    """Verify one original dispatch or continuation without upgrading its status."""
    from scripts.whole_source import admission, lifecycle_observations
    directory = Path(row['directory'])
    document = _document(admitted)
    _require(document.get('format') == admission.FORMAT and
             document.get('policy') == admission.POLICY and document.get('phase') == phase and
             document.get('attempt_directory') == str(directory) and
             document.get('inputs') == row['inputs'],
             'selected phase admission does not match original attempt')
    binding = document.get('supervision')
    _require(type(binding) is dict and set(binding) == {'root','invocation_id','operation_id','intent'},
             'missing selected phase supervisor authority')
    identity = binding['invocation_id']
    _require(type(identity) is str and re.fullmatch('[0-9a-f]{32}', identity) and
             binding['operation_id'] == current['operation_id'] and
             identity != current['invocation_id'],
             'selected phase requires prior terminal supervisor authority')
    observed = Path(binding['root'])
    _require(observed.is_absolute() and str(observed.resolve()) == binding['root'],
             'invalid selected phase observation root')
    intent = binding['intent']
    _require(type(intent) is dict and set(intent) == {'path','sha256','size'} and
             intent.get('path') == 'intents/'+identity+'.json',
             'invalid selected phase supervisor intent')
    try:
        intent_document = _json(_raw(observed, ArtifactRef(**intent), MIB))
        receipt = lifecycle_observations.read_receipt(observed, identity)
        receipt_record = _record(observed/'receipts'/(identity+'.json'))
        _require(_document(receipt_record) == receipt, 'changed supervisor terminal receipt')
    except (OSError, KeyError, TypeError, ValueError) as error:
        raise ContractError('unverified selected phase supervisor authority: '+str(error)[:512]) from error
    _require(receipt.get('intent') == intent and
             receipt.get('operation_id') == binding['operation_id'] and
             receipt.get('code') == current['code'] == intent_document.get('code'),
             'selected phase supervisor operation, code or intent differs')
    _require(receipt.get('status') in ('COMPLETED','INTERRUPTED') and
             receipt.get('cleanup_verified') is True and
             type(receipt.get('final_job')) is dict and
             receipt['final_job'].get('active_process_count') == 0,
             'selected phase supervisor cleanup is unverified')
    return {'phase': phase, 'attempt_directory': str(directory),
            'phase_completion': row['record'], 'admission': admitted,
            'supervision': binding, 'intent': {'directory': str(observed), 'artifact': intent},
            'receipt': receipt_record, 'observation': {'directory': str(observed),
                'artifact': receipt['observation']},
            'invocation_status': receipt['status']}


def _selected_supervision(run, root, *, selected=None):
    """Bind every selected attempt's original dispatch and all resumed work."""
    from scripts.whole_source import supervision
    from scripts.whole_source.coordinator import PHASES, read_phase_records
    current = supervision.require_current()
    _require(all(_ref(root, name).sha256 == digest for name, digest in current['code'].items()),
             'selected phase supervisor implementation root differs')
    run = Path(run).resolve()
    selected = read_phase_records(run) if selected is None else selected
    result = []
    for phase in PHASES:
        if phase not in selected:
            continue
        row = selected[phase]
        directory = Path(row['directory'])
        _require(directory.parent == run/phase/'attempts' and
                 re.fullmatch('[0-9a-f]{32}', directory.name),
                 'invalid selected supervisor attempt')
        prefix = 'attempt-'+phase+'-'+directory.name
        try:
            paths = [_safe(run, 'admission/'+prefix+'.json')]
            with os.scandir(run/'admission') as entries:
                for entry in entries:
                    if not entry.name.startswith(prefix+'-'):
                        continue
                    _require(len(paths) < 1024 and
                             re.fullmatch(re.escape(prefix)+'-[0-9a-f]{32}\\.json', entry.name),
                             'invalid selected supervisor continuation')
                    paths.append(_safe(run, 'admission/'+entry.name))
            for path in sorted(paths):
                result.append(_phase_supervision(run, phase, row, _record(path), current))
        except ContractError:
            raise
        except (OSError, KeyError, TypeError, ValueError) as error:
            raise ContractError('unverified original selected phase supervisor admission') from error
    _require(result, 'missing selected phase supervisor authority')
    return result


def _review_manifest(run,root):
    run,root = Path(run).resolve(),Path(root).resolve()
    supervisor_receipts = _selected_supervision(run, root)
    code,capture,locations = _implementation_code(root)
    from scripts.whole_source.selection import validate_pipeline
    original, selected = validate_pipeline(run, root)
    _require('controls' in selected and 'replay' in selected, 'required coordinator phases are incomplete')
    pipeline = _record(run/'pipeline-result.json')
    controls = selected['controls']['outputs']['controls']
    replayed = selected['replay']['outputs']['replay']
    replay_document = _document(replayed)
    child = replay_document['replayed_run']
    child_document, child_selected = validate_pipeline(Path(child['directory']),
                                         Path(selected['replay']['directory'])/'captured-root')
    supervisor_receipts += _selected_supervision(Path(child['directory']),
        Path(selected['replay']['directory'])/'captured-root', selected=child_selected)
    pid = problem_id(bind_problem('retained-t081',root=root))
    for directory,document in ((run,original),(Path(child['directory']),child_document)):
        _require(document.get('problem_id')==pid,'coordinator problem differs')
        _require(document.get('format') == 'whole-source-pipeline-result-v3',
                 'unqualified pipeline format')
        publication = _document(document['source_publication'])
        audit_execution = _document(document['audit_execution'])
        _require(publication.get('format')=='whole-source-publication-execution-v2' and
                 publication.get('source_manifest')==document['source']['artifact'] and
                 publication.get('provenance',{}).get('kind')=='OWNED_SOURCE' and
                 audit_execution.get('format')=='whole-source-audit-execution-v1' and
                 audit_execution.get('audit')==document['audit']['artifact'] and
                 audit_execution.get('source',{}).get('execution')==document['source_publication']['artifact'],
                 'reviewed publication/execution binding differs')
        _require(document.get('implementation')==_record(directory/'implementation/start.json'),
                 'pipeline omits coordinator implementation identity')
    coordinators = [
        _coordinator_implementation(run,'science',{'pipeline':pipeline},code,capture,pid),
        _coordinator_implementation(Path(selected['controls']['directory']), 'controls',
                                    {'controls': controls}, code, capture, pid),
        _coordinator_implementation(Path(selected['replay']['directory']), 'replay',
                                    {'replay': replayed}, code, capture, pid),
        _coordinator_implementation(Path(child['directory']),'science',{'pipeline':child},code,capture,pid)]
    stages,seen = [],set()
    required = {
        ('premises','analytic','evaluate_premise'),('source','producer','evaluate_source'),
        ('audit','analytic','evaluate_source'),('proposal','proposal','evaluate_proposal'),
        ('exact','exact','evaluate_exact'),('controls','analytic','evaluate_control'),
        ('controls','exact','evaluate_exact'),('replay','producer','evaluate_source'),
        ('replay','analytic','evaluate_source'),('replay','analytic','evaluate_premise'),
        ('replay','exact','evaluate_exact')}
    for receipt in _verify_receipts(run, code_root=root):
        bound = _stage_implementation(receipt,code,locations)
        group = Path(receipt['directory']).relative_to(run).parts[0]
        if group == 'prepare':
            group = 'premises'
        _require(group in {r[0] for r in required},'unexpected scientific execution group')
        if group=='replay':
            _require(Path(receipt['directory']).is_relative_to(Path(child['directory'])),
                     'replay stage outside captured scientific execution')
        seen.add((group,bound['role'],bound['function']))
        stages.append(bound)
    _require(required<=seen,'missing required reviewed execution stages')
    return {'format':'whole-source-review-manifest-v5','code':code,
        'inherited_capture':capture,'pipeline_result':pipeline,'controls':controls,'replay':replayed,
        'runtime_versions':_runtime_versions(),
        'receipt_policy':'artifact-derived-source-stages-v1',
        'supervisor_receipts':supervisor_receipts,
        'publications':[row[key] for row in (original,child_document)
                        for key in ('source_publication','audit_execution')],
        'coordinators':coordinators,'stages':stages,'production_admission':False}


def _check_sealed_output(output):
    """Inspect every ancestor without treating an unreadable marker as absent."""
    for parent in (output,*output.parents):
        marker = parent/'retained-manifest.json'
        try:
            marker.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ContractError('cannot inspect retained seal marker: '+str(marker)) from exc
        raise ContractError('output must be outside sealed retained bundles: '+str(parent))


def _check_review_output(run,output,root):
    """Keep new review/assessment files outside scientific and sealed trees."""
    output.relative_to(root)
    _require(not output.is_relative_to(run) and not run.is_relative_to(output),
             'output must be outside the reviewed scientific run and its ancestors')
    _check_sealed_output(output)


def prepare_review(run_dir,output_dir,*,code_root=ROOT):
    """Prepare complete evidence for a human/independent review; never approve it."""
    from scripts.whole_source.supervision import require_current
    require_current()
    run,output,root = Path(run_dir).resolve(),Path(output_dir).resolve(),Path(code_root).resolve()
    _check_review_output(run,output,root)
    from scripts.whole_source.admission import admitted_phase, admitted_problem
    _check_sealed_output(run)
    problem = admitted_problem(root)
    with _slice_writer(run,resume=True):
        _check_sealed_output(run)
        with admitted_phase('review', problem, run, root, external=output):
            manifest = _review_manifest(run,root)
            _check_review_output(run,output,root)
            output.mkdir(parents=True,exist_ok=False)
            _write(output/'implementation-manifest.json',canonical_bytes(manifest))
    return {'status':'COMPLETE_IMPLEMENTATION_EVIDENCE_PENDING_INDEPENDENT_REVIEW',
            'implementation':_record(output/'implementation-manifest.json'),'production_admission':False}


def _validate_review(run,root):
    review = _json(_bytes(Path(run)/'review-decision.json'))
    _require(type(review) is dict and set(review)=={
        'format','disposition','pipeline_result','controls','replay','implementation','code'} and
        review.get('format')=='whole-source-independent-review-v4' and
        review.get('disposition')=='NO_UNRESOLVED_CORRECTNESS_FINDINGS',
        'independent review requires the complete phase-bound v4 contract')
    code,_,_ = _implementation_code(root)
    _reviewed_code(review.get('code'),code)
    expected = _review_manifest(run,root)
    _require(all(review[key]==expected[key] for key in ('pipeline_result','controls','replay')) and
             _document(review['implementation'])==expected,
             'independent review does not bind the executed implementation')
    return review


def _assess_local(run,root):
    _selected_supervision(run, root)
    problem = bind_problem('retained-t081',root=root)
    result = _json(_bytes(run/'pipeline-result.json'))
    source,audit,exact,proposal,premises = (_document(result[key]) for key in ('source','audit','exact','proposal','premises'))
    _require(source['full_mathematical_source'] is True and source['control'] is False and
             audit['status']=='VERIFIED_ALL_DECLARED_SOURCE_ENTRIES' and audit['entries_checked']==FULL_ENTRIES and
             audit['source_manifest']==result['source']['artifact'] and audit['full_mathematical_source'] is True and
             audit['problem_id']==result['problem_id']==problem_id(problem),'incomplete source/audit conjunction')
    _require(result['fresh_proposal'] is True and proposal.get('status')=='NONPROOF_ONLY' and
             proposal.get('scope')=='NONPROOF_PROPOSAL_ONLY' and
             proposal['source']==result['source']['artifact'] and
             exact['source']['manifest']==result['source']['artifact'] and
             exact['proposal']['artifact']==result['proposal']['artifact'] and
             exact['proof_scope']=='SOURCE_CONDITIONAL' and
             exact['status']=='PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL', 'wrong source/proposal/exact binding')
    _require(premises['status']=='VERIFIED_FRESH_SCALAR_PREMISES' and len(premises['outputs'])==8,
             'fresh scalar-premise checks missing')
    review = _validate_review(run,root)
    from scripts.whole_source.controls import SOURCE_CASES,EXACT_CASES
    controls_ref = _selected_phase(run, 'controls')['outputs']['controls']
    replay_ref = _selected_phase(run, 'replay')['outputs']['replay']
    controls, replayed = _document(controls_ref), _document(replay_ref)
    _require(controls['status']=='PASS_REQUIRED_MATHEMATICAL_CONTROLS' and
             replayed['status']=='PASS_COMPLETE_SCIENTIFIC_REPLAY_COMPARISON' and
             replayed['expected_new_outputs_installed'] is False,'control/replay conjunction failed')
    _require([row['case'] for row in controls['cases']]==[name for name,_ in (*SOURCE_CASES,*EXACT_CASES)] and
             all(row['passed'] is True for row in controls['cases']) and
             all(controls[key]==result[key] for key in ('source','audit','proposal','exact')),
             'missing, rebound or unsuccessful mathematical controls')
    for row in controls['cases']:
        _require(_json(_bytes(Path(controls_ref['directory'])/row['case']/'case-result.json'))==row,
                 'changed mathematical case evidence')
    _require(replayed['original_run']==_record(run/'pipeline-result.json'),
             'replay refers to another original run')
    _document(replayed['original_run'])
    child = _document(replayed['replayed_run'])
    _require(child['fresh_proposal'] is False,'replay must install bound NONPROOF coordinates')
    compare_science(run,Path(replayed['replayed_run']['directory']))
    from scripts.whole_source.pipeline import _bind as bind_source,SourceReader
    from scripts.whole_source.controls import _positive
    _,_,bound = bind_source(Path(result['problem']['directory'])/result['problem']['artifact']['path'],
        Path(result['source_execution']['directory'])/result['source_execution']['artifact']['path'],root)
    produced = SourceReader(Path(result['source']['directory'])/result['source']['artifact']['path'],
                            bound['producer'][0],control=False)
    independently = SourceReader(Path(result['audit']['directory'])/'analytic/source-manifest.json',
                                 bound['analytic'][0], control=False)
    _positive(problem, produced, independently, _phase_path(result['audit']))
    consequence = reviewed_consequence(problem,exact['blocks'])
    receipts = _verify_receipts(run, code_root=root)
    for value in premises['outputs']:
        _require(value['status']=='VERIFIED_FRESH_SCALAR_PREMISE' and
                 value['byte_identical_to_reviewed_scalar'] is True,'scalar reconstruction failed')
        _document(value['output'])
    report = {'format':'whole-source-reviewed-acceptance-v6','implementation':review['implementation'],
        'status':'PASS_NEW_SOURCE_CONDITIONAL_REFERENCE_QUALIFICATION','problem_id':problem_id(problem),
        'entries_checked':FULL_ENTRIES,'dimensions':[413,413],'gamma':consequence['gamma'],
        'conservative_source_norm_floor':FLOOR,'scalar_premises':result['premises'],
        'source':result['source'],'audit':result['audit'],'proposal':result['proposal'],'exact':result['exact'],
        'source_publication':result['source_publication'],'audit_execution':result['audit_execution'],
        'controls':controls_ref,'replay':replay_ref,
        'owned_receipts':receipts,'review':_record(run/'review-decision.json'),
        'supervisor_receipts':_document(review['implementation'])['supervisor_receipts'],
        'premises':'Suzuki/source-form agreement; reviewed scalar bounds; FLINT/Arb/Gauss enclosures',
        'unitary_physical_L2_scaling':True,'production_admission':False,'RH_proved':False}
    return report


def evaluate_acceptance(task,staging):
    from scripts.whole_source import execution
    worker = execution._WORKER
    _require(worker is not None and worker[-1] is staging and
             worker[0].role=='exact' and worker[0].backend=='python-flint-exact',
             'final norm/conjunction requires owned exact arithmetic')
    code,_,_ = _implementation_code(ROOT)
    current = {r['artifact']['path']:r['artifact'] for r in code if r['kind']=='current'}
    _require(asdict(worker[0].task_program)==current['scripts/whole_source/retention.py'] and
             set(current)<={ref.path for ref in staging.spec.code_refs} and
             all(asdict(ref)==current[ref.path] for ref in staging.spec.code_refs if ref.path in current),
             'unreviewed captured final assessor')
    return _assess_local(Path(task['run']),ROOT)


def _completed_assessment(run,output,root):
    """Reconstruct the published report from strict, frozen owned evidence."""
    review = _validate_review(run,root)
    code,_,locations = _implementation_code(root)
    _reviewed_code(_document(review['implementation'])['code'],code)
    records = _verify_receipts(output/'collection',code_root=root)
    _require(len(records)==1,'retention requires exactly one completed owned assessment')
    implementations = [_stage_implementation(record,code,locations) for record in records]
    implementation = implementations[0]
    stage = _document(implementation['stage'])
    plan = stage['plan']
    _require(implementation['role']=='exact' and implementation['function']=='evaluate_acceptance' and
             plan['backend']=='python-flint-exact' and plan['scope']=='EXACT_ASSESSMENT_ONLY' and
             stage['task_count']==1,'retention requires the reviewed exact assessment stage')
    task = _json(_bytes(Path(stage['task_file'])))
    _require(task==_request(run=str(run)),'assessment task belongs to another run')
    result_dir = Path(stage['result_dir'])
    row = _json(_bytes(result_dir/'completed.jsonl'))
    payload = _json(_raw(result_dir,ArtifactRef(**{k:row[k] for k in ('path','sha256','size')}),4*MIB))
    _require(payload['task_id']==task['task_id'],'assessment result belongs to another task')
    report = payload['result']
    _require(type(report) is dict,'invalid completed assessment result')
    pipeline = _json(_bytes(run/'pipeline-result.json'))
    _require(report.get('format')=='whole-source-reviewed-acceptance-v6' and
             report.get('status')=='PASS_NEW_SOURCE_CONDITIONAL_REFERENCE_QUALIFICATION' and
             report.get('problem_id')==pipeline['problem_id'] and
             report.get('implementation')==review['implementation'] and
             report.get('review')==_record(run/'review-decision.json') and
             report.get('production_admission') is False and report.get('RH_proved') is False,
             'completed assessment is not bound to this reviewed qualification')
    _require(all(report.get(key)==pipeline[key] for key in
                 ('source','audit','proposal','exact','source_publication','audit_execution')) and
             report.get('scalar_premises')==pipeline['premises'] and
             report.get('controls')==_selected_phase(run, 'controls')['outputs']['controls'] and
             report.get('replay')==_selected_phase(run, 'replay')['outputs']['replay'] and
             report.get('owned_receipts')==_verify_receipts(run,code_root=root),
             'completed assessment scientific evidence changed')
    _require(report.get('supervisor_receipts') ==
             _document(review['implementation'])['supervisor_receipts'],
             'completed assessment supervisor authority changed')
    for key in ('source','audit','proposal','exact','premises','problem','source_execution',
                'source_publication','audit_execution'):
        _document(pipeline[key])
    report['assessment_owned_receipts'] = exact_telemetry([
        json.loads(_raw(Path(record['directory']),ArtifactRef(**record['artifact']),8*MIB))
        for record in records])
    report['assessment_implementation'] = implementations
    return report


def finalize_retention(run_dir,assessment_path,*,code_root=ROOT):
    """Seal completed owned evidence without repeating mathematical execution."""
    from scripts.whole_source.supervision import require_current, event
    require_current()
    event('retention', work='sealed-inventory-verification')
    root,run,assessment = Path(code_root).resolve(),Path(run_dir).resolve(),Path(assessment_path).resolve()
    run.relative_to(root)
    assessment.relative_to(root)
    _require(assessment.name=='assessment.json' and not assessment.is_relative_to(run),
             'retention requires an external published assessment.json')
    # Completed seals are read-only, including historical v1 inventories.
    try:
        (run/'retained-manifest.json').lstat()
    except FileNotFoundError:
        pass
    else:
        result = verify_inventory(run)
        event('retention', state='complete')
        return result
    _require(assessment.is_file(),'published assessment missing')
    _check_sealed_output(run.parent)
    from scripts.whole_source.admission import admitted_phase, admitted_problem
    problem = admitted_problem(root)
    with _slice_writer(run,resume=True):
        _check_sealed_output(run.parent)
        with admitted_phase('retention', problem, run, root, external=assessment.parent):
            try:
                (run/'retained-manifest.json').lstat()
            except FileNotFoundError:
                expected = _completed_assessment(run,assessment.parent,root)
                _require(_json(_bytes(assessment))==expected,'published assessment differs from owned result')
            else:
                return verify_inventory(run)
            return _seal(run)


def _assessment_context(run,output,root,configuration):
    from scripts.whole_source.recovery import operation_context
    code,capture,_ = _implementation_code(root)
    return operation_context('assessment',output,{
        'format':'whole-source-assessment-publication-v1','run':str(run),'code_root':str(root),
        'destination':str(output/'assessment.json'),'pipeline':_record(run/'pipeline-result.json'),
        'review':_record(run/'review-decision.json'),'code':code,'capture':capture,
        'runtime':_runtime_versions(),'configuration':configuration})


def _assessment_publication_context(run,output,root):
    """Require a prospective original context, not a historical result repair."""
    path = _safe(output,'assessment-publication.json')
    context = _json(_bytes(path))
    configuration = context.get('configuration',{}).get('configuration')
    _require(type(configuration) is dict and set(configuration)=={'collection','execution'},
             'missing prospective assessment publication context')
    _require(context==_assessment_context(run,output,root,configuration),
             'assessment publication context or revision changed')
    return context


def _publish_assessment(run,output,root,context):
    from scripts.whole_source.recovery import check_history, finish_publication
    check_history(output/'collection')
    report = _completed_assessment(run,output,root)
    implementations = report['assessment_implementation']
    stage = _document(implementations[0]['stage'])
    _require(len(implementations)==1 and
             {'collection':stage['collection'],'execution':stage['plan']}==
             context['configuration']['configuration'],
             'assessment stage differs from original publication configuration')
    intent = {'format':'whole-source-assessment-terminal-v1',
              'context_sha256':hashlib.sha256(canonical_bytes(context)).hexdigest(),'report':report}
    _check_review_output(run,output,root)
    _check_sealed_output(run)
    published = _safe(output,'assessment.json',missing=True)
    if published.exists():
        _require(_bytes(published)==canonical_bytes(report),'conflicting terminal publication')
    finish_publication(output/'assessment-terminal.json',canonical_bytes(intent))
    # Recheck the destination and seals immediately before publishing the fixed report.
    _check_review_output(run,output,root)
    _check_sealed_output(run)
    finish_publication(output/'assessment.json',canonical_bytes(report))
    return report


def recover_assessment_publication(run_dir,assessment_dir,*,code_root=ROOT):
    """Publish only an original completed, reviewed, prospective assessment result."""
    from scripts.whole_source.supervision import require_current
    require_current()
    root,run,output = Path(code_root).resolve(),Path(run_dir).resolve(),Path(assessment_dir).resolve()
    run.relative_to(root)
    _check_review_output(run,output,root)
    _check_sealed_output(run)
    _require(output.is_dir(),'prospective assessment output missing')
    _require((output/'assessment-publication.json').is_file(),
             'missing prospective assessment publication context')
    from scripts.whole_source.admission import admitted_phase, admitted_problem
    problem = admitted_problem(root)
    # Lock order is always scientific run, then external assessment output.
    with _slice_writer(run,resume=True):
        _check_sealed_output(run)
        with admitted_phase('assessment', problem, run, root, external=output):
            _check_review_output(run,output,root)
            _check_sealed_output(run)
            with _slice_writer(output,resume=True):
                context = _assessment_publication_context(run,output,root)
                report = _publish_assessment(run,output,root,context)
                _seal(run)
                return report


def accept(run_dir,output_dir,*,code_root=ROOT):
    from scripts.whole_source.supervision import require_current
    require_current()
    root,run,output = Path(code_root).resolve(),Path(run_dir).resolve(),Path(output_dir).resolve()
    _check_sealed_output(run)
    _check_review_output(run,output,root)
    from scripts.whole_source.admission import admitted_phase, admitted_problem
    problem = admitted_problem(root)
    with _slice_writer(run,resume=True):
        _check_sealed_output(run)
        with admitted_phase('assessment', problem, run, root, external=output):
            return _accept_held(run,output,code_root=root)


def _accept_held(run_dir,output_dir,*,code_root=ROOT):
    from scripts.whole_source.pipeline import _bind as bind_source
    root,run,output = Path(code_root).resolve(),Path(run_dir).resolve(),Path(output_dir).resolve()
    _check_sealed_output(run)
    _selected_supervision(run, root)
    result = _json(_bytes(run/'pipeline-result.json'))
    problem,_,bound = bind_source(Path(result['problem']['directory'])/result['problem']['artifact']['path'],
        Path(result['source_execution']['directory'])/result['source_execution']['artifact']['path'],root)
    _require((run/'review-decision.json').is_file(),'independent execution review is required before release')
    review = _validate_review(run,root)
    _check_review_output(run,output,root)
    _check_sealed_output(run)
    output.mkdir(parents=True,exist_ok=False)
    base_spec,base_plan = bound['analytic']
    refs = {r.path:r for r in base_spec.code_refs}
    for name in CODE:
        refs[name] = _ref(root,name)
    _,capture,locations = _implementation_code(root)
    for name in (capture['path'],*(stored for stored,_ in locations.values())):
        refs[name] = _ref(root,name)
    for path in (run/'pipeline-result.json',run/'review-decision.json',
                 _phase_path(_selected_phase(run, 'controls')['outputs']['controls']),
                 _phase_path(_selected_phase(run, 'replay')['outputs']['replay']),
                 Path(review['implementation']['directory'])/review['implementation']['artifact']['path']):
        name = path.relative_to(root).as_posix()
        refs[name] = _ref(root,name)
    spec = CollectionSpec.create(problem,role='exact',quantities=base_spec.quantities,
        partition=base_spec.partition,backend='python-flint-exact',backend_version=base_spec.backend_version,
        native_threads=1,code_refs=tuple(refs[name] for name in sorted(refs)),bounds=base_spec.bounds,code_root=root)
    provenance = _json(_bytes(root/base_plan.provenance.path))
    provenance['files'] = [asdict(ref) for ref in spec.code_refs]
    _check_review_output(run,output,root)
    _check_sealed_output(run)
    _write(output/'assessment-origin.json',canonical_bytes(provenance))
    from scripts.whole_source.admission import phase_caller_account
    review_private_mib = (phase_caller_account('assessment', problem, run=run)['required_bytes']+MIB-1)//MIB
    plan = replace(base_plan,role='exact',collection_sha256=spec.collection_id,
        resource_policy=None,workers=1,worker_private_mib=max(base_plan.worker_private_mib,review_private_mib),
        codec_mib=(base_plan.codec_mib+base_plan.workers-1)//base_plan.workers,
        reserve_mib=(base_plan.resource_policy["baseline"]["reserve_mib"]
                     if base_plan.resource_policy is not None else base_plan.reserve_mib),
        backend='python-flint-exact',precision_bits=65536,max_tasks=1,result_bytes=4*MIB,queue_mib=16,
        task_program=refs['scripts/whole_source/retention.py'],task_function='evaluate_acceptance',
        scope='EXACT_ASSESSMENT_ONLY',provenance=_ref(root,(output/'assessment-origin.json').relative_to(root).as_posix()))
    from scripts.whole_source.resources import auto_plan
    plan = auto_plan(replace(plan,resource_policy=None),parallel=False,helper_root=root)
    spec = replace(spec,native_threads=plan.threads)
    spec._validate()
    plan = replace(plan,collection_sha256=spec.collection_id)
    from scripts.whole_source.recovery import finish_publication
    context = _assessment_context(run,output,root,
        {'collection':spec.to_dict(),'execution':plan.to_dict()})
    # The science lock is already held; acquire the external output lock second.
    with _slice_writer(output,resume=True):
        _check_review_output(run,output,root)
        _check_sealed_output(run)
        finish_publication(output/'assessment-publication.json',canonical_bytes(context))
        with CollectionLock.acquire(output/'collection',spec) as lock:
            with WorkloadExecution(lock,spec,plan,code_root=root) as execution:
                execution.run_stage('reviewed-consequence',[_request(run=str(run))])
        report = _publish_assessment(run,output,root,context)
        _seal(run)
    return report


def run(problem_path, execution_path, output_dir, *, code_root=ROOT, resume=False, through='replay'):
    from scripts.whole_source.coordinator import PHASES
    from scripts.whole_source.supervision import require_current
    require_current()
    _require(through in PHASES, 'unknown coordinator stop phase')
    root, output = Path(code_root).resolve(), Path(output_dir).resolve()
    output.relative_to(root)
    _check_sealed_output(output)
    if resume:
        _require(output.is_dir() and (output/'integration-execution.json').is_file()
                 and (output/'implementation/start.json').is_file(),
                 'resume requires an existing original coordinator operation')
    from scripts.whole_source.admission import bootstrap_scope
    with bootstrap_scope(root, input_count=3 if resume else 2):
        problem, config = _bind(problem_path, execution_path, root)
        if resume:
            _require(_json(_bytes(output/'integration-execution.json')) == config,
                     'resume differs from original integration inputs')
    output.parent.mkdir(parents=True, exist_ok=True)
    _require(shutil.disk_usage(output.parent).free >= config['minimum_free_bytes'],
             'insufficient full-path free disk allowance')
    with _slice_writer(output, resume=resume):
        from scripts.whole_source.admission import admitted_phase
        with admitted_phase('validation', problem, output, root):
            _publish_identical(output/'integration-execution.json', config)
        try:
            return _execute(problem, config, output, root, resume=resume, through=through)
        except BaseException as exc:
            try:
                with admitted_phase('validation', problem, output, root):
                    failure = canonical_bytes({
                        'status': 'FAILED_NO_REFERENCE_ACCEPTANCE', 'error_type': type(exc).__name__,
                        'error': str(exc)[:65536], 'production_admission': False})
                    _write(output/('failure-'+uuid.uuid4().hex+'.json'), failure)
            except (ContractError, OSError) as reporting_error:
                exc.add_note('Failure receipt could not be admitted: '+str(reporting_error))
            raise
