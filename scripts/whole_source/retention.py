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
from scripts.whole_source.artifacts import CollectionSpec, CollectionLock, _raw, _root_path, _safe, decode_rational
from scripts.whole_source.artifacts import ASSESSMENT_INPUTS, ASSESSMENT_ORIGIN, SCALAR_INPUTS, SCALAR_ORIGIN
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
_REPLAY_FORMAT = 'whole-source-scientific-replay-v3'
_PREVIOUS_REPLAY_FORMAT = 'whole-source-scientific-replay-v2'
_SCOPED_REPLAY_FORMATS = (_PREVIOUS_REPLAY_FORMAT, _REPLAY_FORMAT)
_PIPELINE_FORMAT = 'whole-source-pipeline-result-v4'
_COMPLETION_FORMAT = 'whole-source-coordinator-completion-v2'
_FROZEN_REPLAY_FORMAT = 'whole-source-scientific-replay-v1'
_REPLAY_CAPTURE_FORMAT = 'whole-source-captured-inputs-v2'
_REPLAY_PROPOSAL = Path('replay-inputs/proposal.json')
_REPLAY_INVOCATION = 'whole-source-replay-invocation-v1'
_REPLAY_CLEANUP = 'whole-source-replay-owned-cleanup-v1'
_REPLAY_STREAM_LIMIT = 4*MIB
_REPLAY_DIAGNOSTICS = 'replay-diagnostics.json'
_REPLAY_OPTIONS = ('-I', '-B', '-c')
_REPLAY_ENTRY = (
    'import sys;sys.path.insert(0,sys.argv[1]);'
    'from scripts.whole_source.retention import _replay_child;'
    '_replay_child(sys.argv[2],sys.argv[3],sys.argv[4])'
)


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
    if proposal_path is not None:
        proposal_path,core,proposal_raw = _capture_proposal(problem,root,proposal_path)
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
    capture_format = 'whole-source-captured-inputs-v1'
    if proposal_path is not None:
        path = proposal_path
        capture_format = _REPLAY_CAPTURE_FORMAT
        base = _REPLAY_PROPOSAL.parent
        install(_REPLAY_PROPOSAL.as_posix(),proposal_raw,'NONPROOF_ONLY')
        for block in core['blocks']:
            for panel in block['integer_panels']:
                ref = ArtifactRef(**panel['artifact'])
                install((base/ref.path).as_posix(),_raw(path.parent,ref,8*MIB),'NONPROOF_ONLY')
    _require(not any(name.startswith(OLD_CANDIDATE) for name in files),
             'old target oracle or coordinates entered captured scientific tree')
    manifest = {'format':capture_format,'problem_id':problem_id(problem),
        'files':[files[name] for name in sorted(files)],'expected_new_outputs_installed':False,
        'proposal_installed':proposal_path is not None,'production_admission':False}
    _write(directory/'capture-manifest.json',canonical_bytes(manifest))
    bind_problem(problem.profile,root=directory)
    return manifest


def _capture_proposal(problem,root,proposal_path):
    from scripts.whole_source.proposal import _PROPOSAL_CORE, read_proposal
    path = Path(proposal_path).absolute()
    _require(path.is_relative_to(root), 'replay original proposal escapes code root')
    path = _safe(root,path.relative_to(root).as_posix())
    raw = _bytes(path)
    core = _json(raw)
    _require(core.get('format') == _PROPOSAL_CORE, 'legacy proposal is read-only')
    read_proposal(path,problem,core['source'])
    _require(_bytes(path)==raw,'proposal changed during replay capture validation')
    return path,core,raw


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
    from scripts.whole_source.coordinator import operation_record
    attempt = staging.root/'attempts'/staging.attempt_id
    portable = task['scalar_root'] == SCALAR_INPUTS
    output_record, program_record = _record(path), _record(program)
    if portable:
        output_record = operation_record(attempt, output_record)
        program_record = operation_record(attempt, program_record)
    return {'status':'VERIFIED_FRESH_SCALAR_PREMISE','index':index,'output':output_record,
        'program':asdict(_ref(ROOT,task['scalar_root']+'/'+QUALIFICATION+'/'+script)),
        'executed_program':program_record,
        'byte_identical_to_reviewed_scalar':True,'production_admission':False}


def run_premises(problem,base_spec,base_plan,directory,*,code_root=ROOT, origin_root=None):
    root,directory = Path(code_root).resolve(),Path(directory).resolve()
    directory.mkdir(parents=True,exist_ok=False)
    closure = directory/SCALAR_INPUTS
    capture_inputs(problem,closure,code_root=root)
    # Scalar programs run from the installed closed tree, not mutable originals.
    paths = [p.relative_to(directory).as_posix() for p in closure.rglob('*') if p.is_file()]
    refs = {r.path:r for r in base_spec.code_refs}
    for name in paths:
        refs[name] = _ref(directory,name)
    for name in ('retention','coordinator'):
        path = 'scripts/whole_source/'+name+'.py'
        refs[path] = _ref(root,path)
    spec = CollectionSpec.create(problem,role='analytic',quantities=base_spec.quantities,
        partition=base_spec.partition,backend='python-flint',backend_version=base_spec.backend_version,
        native_threads=1,code_refs=tuple(refs[name] for name in sorted(refs)),bounds=base_spec.bounds,
        code_root=root,auxiliary_root=directory,auxiliary_role='scalar-premises')
    origin_path = directory/SCALAR_ORIGIN
    origin = _json(_raw(Path(origin_root) if origin_root is not None else root,base_plan.provenance,8*MIB))
    origin['files'] = [asdict(r) for r in spec.code_refs]
    _write(origin_path,canonical_bytes(origin))
    plan = replace(base_plan,collection_sha256=spec.collection_id,
        task_program=_ref(root,'scripts/whole_source/retention.py'),task_function='evaluate_premise',
        precision_bits=6144,max_tasks=8,provenance=_ref(directory,SCALAR_ORIGIN))
    from scripts.whole_source.resources import auto_plan
    plan = auto_plan(plan,parallel=False,helper_root=root)
    spec = replace(spec,native_threads=plan.threads)
    spec._validate()
    plan = replace(plan,collection_sha256=spec.collection_id)
    # The worker uses a separately declared scalar root from this bound task.
    with CollectionLock.acquire(directory/'collection',spec) as lock:
        with WorkloadExecution(lock,spec,plan,code_root=root,auxiliary_root=directory) as execution:
            rows = []
            for index in range(8):
                execution.run_stage('premise-'+str(index),[_request(index=index,
                    scalar_root=SCALAR_INPUTS,
                    output=QUALIFICATION+'/data/owned-native-reconstruction')])
                rows.append(next(execution.read_results('premise-'+str(index)))['result'])
            from scripts.whole_source.coordinator import operation_record
            receipt_refs = [operation_record(directory,_record(execution.output/('premise-'+str(i))/'receipt.json'))
                            for i in range(8)]
            result = {'format':'whole-source-scalar-premises-v2','status':'VERIFIED_FRESH_SCALAR_PREMISES',
                'problem_id':problem_id(problem),'outputs':rows,
                'owned_receipts':receipt_refs,'production_admission':False}
            _write(directory/'premises-receipt.json',canonical_bytes(result))
    return result


def _verify_receipts(directory, *, code_root=ROOT):
    """Verify selected recovery producers and all cleanup; keep legacy stage checks."""
    from scripts.whole_source.receipts import discover_receipts, verify_stage
    if (Path(directory)/'coordinator/context.json').exists():
        from scripts.whole_source.selection import selected_execution_roots
        _check_phase_history(directory)
        selected = []
        for _, folder, root in selected_execution_roots(directory, code_root):
            selected.extend(_verify_receipts(folder, code_root=root))
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


def _selected_phase(run, phase, *, code_root=None):
    from scripts.whole_source.coordinator import read_phase_records
    rows = read_phase_records(run, code_root=code_root)
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


def compare_science(first,second,*,first_root=None,second_root=None):
    from scripts.whole_source.pipeline import compare_source_audits
    reports = [_pipeline_document(run, root) for run, root in ((first,first_root),(second,second_root))]
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
        run_premises(problem,*bound['analytic'],directory/'premises',code_root=root,
                     origin_root=inputs['execution'].parent)
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
            from scripts.whole_source.coordinator import operation_record
            proposal = operation_record(run, _record(proposal_input), code_root=root)
            _require(proposal['scope'] == 'captured-proposal', 'wrong installed proposal role')
            _publish_identical(directory/'installed-proposal.json', {
                'format': 'whole-source-replay-proposal-install-v2', 'proposal': proposal})
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
            directory,code_root=root,operands_path=_phase_path(prior['exact-inputs']['operands']))
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
        _check_coordinator_start(value, 'science', problem_id(problem), capture)
        for row in code:
            ref = ArtifactRef(**row['artifact'])
            _raw(output/'implementation', ArtifactRef('snapshots/'+ref.sha256, ref.sha256, ref.size), 8*MIB)
    else:
        start = _capture_implementation(problem, output, root, 'science')
    context = {'problem_id': problem_id(problem), 'configuration': config,
               'implementation': start,
               'proposal_input': None if proposal_input is None else _record(proposal_input)}
    return PhaseJournal(output, context, resume=resume, code_root=root)


def _pipeline_paths(run, document, root, *, decode):
    from scripts.whole_source.coordinator import operation_record, resolve_operation_record
    from scripts.whole_source.selection import _PIPELINE_OUTPUTS
    transform = resolve_operation_record if decode else operation_record
    fields = set(_PIPELINE_OUTPUTS) | {'implementation'}
    _require(type(document) is dict and fields | {'phase_chain'} <= set(document) and
             type(document['phase_chain']) is list, 'invalid pipeline artifact roles')
    return {**document,
            **{key: transform(run, document[key], code_root=root if key == 'proposal' else None)
               for key in fields},
            'phase_chain': [transform(run, record) for record in document['phase_chain']]}


def _pipeline_document(run, root):
    run = Path(run).resolve()
    root = None if root is None else Path(root).resolve()
    document = _json(_bytes(run/'pipeline-result.json'))
    if document.get('format') == _PIPELINE_FORMAT:
        return _pipeline_paths(run, document, root, decode=True)
    return document


def _implementation_completion(directory, start, outputs):
    from scripts.whole_source.coordinator import operation_record
    return {'format': _COMPLETION_FORMAT, 'start': operation_record(directory, start),
            'outputs': {role: operation_record(directory, record) for role, record in outputs.items()},
            'production_admission': False}


def _publish_pipeline(problem, config, output, root, journal):
    from scripts.whole_source.coordinator import SCIENCE_PHASES
    prior = {name: journal.completed[name]['outputs'] for name in SCIENCE_PHASES}
    exact = _document(prior['exact']['exact'])
    result = {'format': _PIPELINE_FORMAT, 'status': 'COMPLETE_FRESH_SOURCE_AUDIT_AND_EXACT',
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
    _publish_identical(output/'pipeline-result.json', _pipeline_paths(output, result, root, decode=False))
    completion = _implementation_completion(output, result['implementation'],
                                             {'pipeline': _record(output/'pipeline-result.json')})
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
                bind_phase_attempt(admission, directory, output, legacy_inputs=prior)
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
                bind_phase_attempt(admission, directory, output, legacy_inputs=prior)
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
                from scripts.whole_source.coordinator import operation_record
                ready = {'format': 'whole-source-ready-for-review-v2',
                         'status': 'COMPLETE_EVIDENCE_PENDING_INDEPENDENT_REVIEW',
                         'pipeline_result': operation_record(output, _record(output/'pipeline-result.json')),
                         'controls': operation_record(output, prior['controls']['controls']),
                         'replay': operation_record(output, prior['replay']['replay']),
                         'production_admission': False}
                _publish_identical(output/'ready-for-review.json', ready)
                return ready
    return {'status': 'PAUSED_AFTER_VERIFIED_PHASE', 'completed_through': through,
            'science_complete': science_complete,
            'production_admission': False, 'reference_qualification_accepted': False}


def _replay_roots(root, run, directory, *, missing=False, legacy=False):
    """Derive a single child from the original operation and its owned capture."""
    from scripts.whole_source.coordinator import _absolute
    root, run, directory = (_absolute(str(Path(path).absolute())) for path in (root, run, directory))
    _root_path(root)
    _require(run != root and run.is_relative_to(root), 'replay original run escapes code root')
    _root_path(run)
    _root_path(directory, missing=missing)
    tree = directory/'captured-root'
    child = tree/(run.relative_to(root) if legacy else 'replay-run')
    inputs = tree/_REPLAY_PROPOSAL.parent
    _require(not child.is_relative_to(inputs) and not inputs.is_relative_to(child),
             'replay child overlaps the captured proposal directory')
    _root_path(child, missing=missing)
    return tree, child


def _replay_fingerprint(root, name):
    raw = _bytes(_safe(root, name))
    return {'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def _replay_invocation(tree, child, proposal):
    _require(proposal == tree/_REPLAY_PROPOSAL, 'wrong captured replay proposal role')
    descriptor = {
        'format': _REPLAY_INVOCATION,
        'interpreter': {'implementation': sys.implementation.name, 'version': sys.version},
        'options': _REPLAY_OPTIONS,
        'entrypoint_sha256': hashlib.sha256(_REPLAY_ENTRY.encode('ascii')).hexdigest(),
        'working_directory_role': 'captured_root',
        'argument_roles': ['captured_root', 'replayed_run', 'integrated_execution', 'installed_proposal'],
        'inputs': {
            'capture': _replay_fingerprint(tree, 'capture-manifest.json'),
            'integrated_execution': _replay_fingerprint(child, 'integration-execution.json'),
            'installed_proposal': _replay_fingerprint(tree, proposal.relative_to(tree).as_posix()),
        },
        'stream_limit_bytes': _REPLAY_STREAM_LIMIT,
    }
    return {'format': _REPLAY_INVOCATION, 'sha256': hashlib.sha256(canonical_bytes(descriptor)).hexdigest()}


def _replay_bindings(run, child, tree):
    return {
        'original_run': _replay_fingerprint(run, 'pipeline-result.json'),
        'replayed_run': _replay_fingerprint(child, 'pipeline-result.json'),
        'capture': _replay_fingerprint(tree, 'capture-manifest.json'),
    }


def _replay_cleanup(child, records):
    fingerprints = []
    for record in records:
        path = _phase_path(record)
        _require(path.is_relative_to(child) and path.name == 'receipt.json',
                 'owned replay receipt escapes captured run')
        ref = record['artifact']
        fingerprints.append((ref['sha256'], ref['size']))
    _require(fingerprints, 'missing owned replay cleanup evidence')
    return {'format': _REPLAY_CLEANUP, 'count': len(fingerprints),
            'sha256': hashlib.sha256(canonical_bytes(sorted(fingerprints))).hexdigest()}


class _ReplayProcessError(ContractError):
    _MESSAGES = {
        'stream_allowance': 'captured replay stream allowance exceeded',
        'stream_io': 'captured replay stream refused',
        'child_exit': 'captured scientific replay failed',
    }

    def __init__(self, reason, exit_code, streams):
        super().__init__(self._MESSAGES[reason])
        self.reason, self.exit_code, self.streams = reason, exit_code, streams


def _replay_process(command, tree, root):
    """Digest bounded streams without retaining their bytes; the outer job owns the deadline."""
    import subprocess
    import threading
    from scripts.whole_source.admission import waiting_caller
    failures, streams = [], {}
    lock = threading.Lock()
    with waiting_caller(helper_root=root):
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        process = subprocess.Popen(command, cwd=tree, env=env, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        def cancel():
            try:
                process.stdin.write(b'!')
                process.stdin.flush()
            except (OSError, ValueError):
                pass

        def read_stream(role, incoming):
            digest, size = hashlib.sha256(), 0
            failed = False
            try:
                with incoming:
                    while raw := incoming.read(65536):
                        if failed:
                            continue
                        if size+len(raw) > _REPLAY_STREAM_LIMIT:
                            failed = True
                            with lock:
                                failures.append(('stream_allowance', None))
                                cancel()
                        else:
                            digest.update(raw)
                            size += len(raw)
                if not failed:
                    streams[role] = {'size': size, 'sha256': digest.hexdigest()}
            except (OSError, ValueError) as error:
                with lock:
                    failures.append(('stream_io', error))
                    cancel()

        readers = [threading.Thread(target=read_stream, args=(role, incoming), daemon=True)
                   for role, incoming in (('stdout', process.stdout), ('stderr', process.stderr))]
        for reader in readers:
            reader.start()
        try:
            process.wait()
        except BaseException:
            with lock:
                cancel()
            raise
        finally:
            with lock:
                process.stdin.close()
            for reader in readers:
                reader.join()
        if failures:
            reason, error = failures[0]
            raise _ReplayProcessError(reason, process.returncode, streams) from error
        return process.returncode, streams


def _write_replay_failure(output, invocation, error):
    from scripts.whole_source.supervision import _failure
    known = isinstance(error, _ReplayProcessError)
    _write(output/'replay-failure.json', canonical_bytes({
        'format': 'whole-source-replay-failure-v1',
        'status': 'FAILED_CAPTURED_REPLAY',
        'invocation': invocation,
        'reason': error.reason if known else 'launch_or_wait_failed',
        'exit_code': error.exit_code if known else None,
        'streams': error.streams if known else None,
        'error': _failure(error.__cause__ or error),
        'production_admission': False,
    }))


def replay(run_dir,output_dir,*,code_root=ROOT):
    root,run,output = (Path(path).absolute() for path in (code_root,run_dir,output_dir))
    from scripts.whole_source.selection import validate_pipeline
    from scripts.whole_source.coordinator import SCIENCE_PHASES
    from scripts.whole_source.supervision import require_current
    require_current()
    tree, child_run = _replay_roots(root, run, output, missing=True)
    _check_sealed_output(output)
    result, _ = validate_pipeline(run, root)
    problem = bind_problem('retained-t081',root=root)
    _require(result.get('format') == _PIPELINE_FORMAT,'legacy pipeline is read-only')
    proposal_directory = Path(result['proposal']['directory'])
    _require(proposal_directory.is_relative_to(root), 'replay original proposal escapes code root')
    proposal = _safe(proposal_directory, result['proposal']['artifact']['path'])
    _require(not output.exists(),'captured replay output already exists')
    capture_inputs(problem,tree,code_root=root,proposal_path=proposal)
    _capture_implementation(problem,output,root,'replay')
    _root_path(child_run, missing=True)
    _require(not any((child_run/name).exists() for name in
                     ('source','audit','exact','prepare','proposal','coordinator','pipeline-result.json')),
             'expected scientific outputs leaked into replay')
    child_run.mkdir(parents=True,exist_ok=True)
    child_config = child_run/'integration-execution.json'
    _new_copy(_safe(run,'integration-execution.json'),child_config)
    child_proposal = _safe(tree,_REPLAY_PROPOSAL.as_posix())
    invocation = _replay_invocation(tree, child_run, child_proposal)
    # Imported module ROOT is not the captured module. Execute a separate Python
    # interpreter whose project imports resolve only from the captured tree.
    command = [sys.executable,*_REPLAY_OPTIONS,_REPLAY_ENTRY,str(tree),str(child_run),
               str(child_config),str(child_proposal)]
    try:
        returncode, streams = _replay_process(command, tree, root)
        if returncode != 0:
            raise _ReplayProcessError('child_exit', returncode, streams)
    except BaseException as error:
        try:
            _write_replay_failure(output, invocation, error)
        except (ContractError, OSError):
            error.add_note('Replay failure evidence could not be admitted')
        raise
    child, rows = validate_pipeline(child_run, tree)
    _require(set(rows) == set(SCIENCE_PHASES) and child['fresh_proposal'] is False
             and child['proposal'] == _record(child_proposal),
             'replay child did not select independent science with the captured proposal')
    compared = compare_science(run,child_run,first_root=root,second_root=tree)
    child_receipts = _verify_receipts(child_run, code_root=tree)
    receipt = {'format':_REPLAY_FORMAT,**compared,**_replay_bindings(run, child_run, tree),
        'expected_new_outputs_installed':False,'invocation':invocation,
        'exit_code':returncode,'shared_installed_arithmetic_runtime':True,
        'owned_cleanup':_replay_cleanup(child_run, child_receipts)}
    _write(output/'replay-receipt.json',canonical_bytes(receipt))
    _write(output/_REPLAY_DIAGNOSTICS,canonical_bytes({
        'format':'whole-source-replay-diagnostics-v1',
        'replay':_replay_fingerprint(output,'replay-receipt.json'),'streams':streams}))
    _complete_implementation(output,root,{'replay':_record(output/'replay-receipt.json')})
    return receipt


def _replay_child(run_dir,config_path,proposal_path):
    import _thread
    import threading
    from scripts.whole_source.supervision import require_current, cancel_current
    require_current()
    def cancel():
        if os.read(sys.stdin.fileno(), 1) == b'!':
            cancel_current()
            _thread.interrupt_main()
    threading.Thread(target=cancel, daemon=True).start()
    from scripts.whole_source.coordinator import _absolute
    run = _absolute(run_dir)
    _require(run == ROOT/'replay-run', 'wrong captured replay output role')
    config_file = _safe(run,'integration-execution.json')
    proposal_file = _safe(ROOT,_REPLAY_PROPOSAL.as_posix())
    _require(config_path == str(config_file) and proposal_path == str(proposal_file),
             'wrong captured replay input roles')
    from scripts.whole_source.admission import bootstrap_scope
    with bootstrap_scope(ROOT, input_count=1):
        config = _json(_bytes(config_file))
        _require(config.get('format') == 'whole-source-integrated-execution-v5' and
                 config.get('lifecycle_supervision') == 'windows-lifecycle-v1',
                 'captured replay requires current supervised execution policy')
        problem = bind_problem('retained-t081',root=ROOT)
        for ref in config['code']:
            _raw(ROOT,ArtifactRef(**ref),8*MIB)
    with _slice_writer(run, resume=True):
        _execute(problem, config, run, ROOT, proposal_input=proposal_file)


_INVENTORY_FORMAT = 'whole-source-retained-inventory-v3'
_DIAGNOSTIC_ROLES = ('diagnostics.json','stdout.jsonl','stderr.jsonl')
_PREPARATION_DIAGNOSTICS = ('preparation-diagnostics.json','preparation-account.json')


def _diagnostic_preparations(directory):
    """Recognize promoted input roles, not arbitrary diagnostic filename matches."""
    from scripts.whole_source.exact import EXECUTION
    for operands in directory.rglob('operands.json'):
        execution = operands.with_name('execution.json')
        if not execution.exists():
            continue
        config = _json(_bytes(execution))
        if config.get('format') == EXECUTION:
            ref = ArtifactRef(**config['operands'])
            _require(ref.path == 'operands.json','wrong diagnostic preparation operand role')
            _raw(execution.parent,ref,8*MIB)
            yield execution.parent,ref


def _stage_diagnostic_receipts(directory):
    from scripts.whole_source.receipts import discover_receipts, _CURRENT
    for receipt in discover_receipts(directory):
        if json.loads(_bytes(receipt)).get('format') == _CURRENT:
            yield receipt


def _replay_diagnostic_receipts(directory):
    for receipt in directory.rglob('replay-receipt.json'):
        if _json(_bytes(receipt)).get('format') == _REPLAY_FORMAT:
            yield receipt


def _check_replay_streams(streams):
    _require(type(streams) is dict and set(streams) == {'stdout','stderr'}
             and all(type(value) is dict and set(value) == {'size','sha256'}
                     and type(value['size']) is int and 0 <= value['size'] <= _REPLAY_STREAM_LIMIT
                     and type(value['sha256']) is str and len(value['sha256']) == 64
                     and all(digit in '0123456789abcdef' for digit in value['sha256'])
                     and (value['size'] != 0 or value['sha256'] == hashlib.sha256(b'').hexdigest())
                     for value in streams.values()), 'invalid bounded replay stream evidence')


def _diagnostic_members(directory):
    members = {(receipt.parent.relative_to(directory)/name).as_posix()
               for receipt in _stage_diagnostic_receipts(directory) for name in _DIAGNOSTIC_ROLES}
    for root,_ in _diagnostic_preparations(directory):
        members.update((root.relative_to(directory)/name).as_posix() for name in _PREPARATION_DIAGNOSTICS)
    members.update((receipt.parent/_REPLAY_DIAGNOSTICS).relative_to(directory).as_posix()
                   for receipt in _replay_diagnostic_receipts(directory))
    return members


def verify_retained_diagnostics(directory):
    """Verify optional diagnostics without changing scientific seal authority."""
    from scripts.whole_source.receipts import verify_stage_diagnostics
    directory = Path(directory).resolve()
    result = [asdict(verify_stage_diagnostics(receipt)) | {
        'path':(receipt.parent.relative_to(directory)/'diagnostics.json').as_posix()}
        for receipt in _stage_diagnostic_receipts(directory)]
    for root,operands in _diagnostic_preparations(directory):
        filename,account_name = _PREPARATION_DIAGNOSTICS
        record = _ref(root,filename)
        value = _json(_raw(root,record,8*MIB))
        _require(set(value)=={'format','operands','account'} and
                 value['format']=='whole-source-exact-preparation-diagnostics-v1' and
                 value['operands']==asdict(operands),'foreign preparation diagnostic inventory')
        account = ArtifactRef(**value['account'])
        _require(account.path==account_name,'wrong preparation diagnostic role')
        _raw(root,account,8*MIB)
        result.append(asdict(record)|{'path':(root/filename).relative_to(directory).as_posix()})
    for receipt in _replay_diagnostic_receipts(directory):
        record = _ref(receipt.parent,_REPLAY_DIAGNOSTICS)
        value = _json(_raw(receipt.parent,record,8*MIB))
        _require(set(value)=={'format','replay','streams'} and
                 value['format']=='whole-source-replay-diagnostics-v1' and
                 value['replay']==_replay_fingerprint(receipt.parent,receipt.name),
                 'foreign replay diagnostic inventory')
        _check_replay_streams(value['streams'])
        result.append(asdict(record)|{'path':(receipt.parent/record.path).relative_to(directory).as_posix()})
    return sorted(result,key=lambda row:row['path'])


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
                 manifest['format'] in ('whole-source-retained-inventory-v2',_INVENTORY_FORMAT) and
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
    if manifest['format'] == _INVENTORY_FORMAT:
        excluded.update(_diagnostic_members(directory))
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


def _seal(directory, *, independent_diagnostics=False):
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
    excluded = {'.slice.lock','retained-manifest.json'}
    if independent_diagnostics:
        excluded.update(_diagnostic_members(directory))
    names = _inventory_files(directory,excluded)
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
    manifest = {'format':_INVENTORY_FORMAT if independent_diagnostics else 'whole-source-retained-inventory-v2',
        'excluded':['.slice.lock','retained-manifest.json'],
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
    value = {'format':'whole-source-coordinator-implementation-v2','phase':phase,
        'problem_id':problem_id(problem),'code':code,'inherited_capture':capture,
        'runtime_versions':_runtime_versions(),'production_admission':False}
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
    _write(directory/'implementation/complete.json',
           canonical_bytes(_implementation_completion(directory, start, outputs)))
    return _record(directory/'implementation/complete.json')


def _check_coordinator_start(value, phase, pid, capture):
    fields = {'format','phase','problem_id','code','inherited_capture','runtime_versions','production_admission'}
    if value.get('format') == 'whole-source-coordinator-implementation-v1':
        fields.add('argv')
    else:
        _require(value.get('format') == 'whole-source-coordinator-implementation-v2',
                 'unknown coordinator implementation format')
    _require(set(value) == fields and value['phase'] == phase and value['problem_id'] == pid
             and value['inherited_capture'] == capture and value['production_admission'] is False
             and value['runtime_versions'] == _runtime_versions(),
             'missing or changed coordinator execution identity')


def _coordinator_implementation(directory,phase,outputs,code,capture,pid):
    directory = Path(directory)
    start,complete = (_record(directory/'implementation'/name) for name in ('start.json','complete.json'))
    value,finished = _document(start),_document(complete)
    _check_coordinator_start(value, phase, pid, capture)
    if finished.get('format') == _COMPLETION_FORMAT:
        valid = finished == _implementation_completion(directory, start, outputs)
    else:
        valid = (finished.get('format') == 'whole-source-coordinator-completion-v1'
                 and finished.get('start') == start and finished.get('outputs') == outputs)
    _require(valid, 'missing or changed coordinator completion')
    _reviewed_code(value.get('code'),code)
    for row in code:
        ref = ArtifactRef(**row['artifact'])
        _raw(directory/'implementation',ArtifactRef('snapshots/'+ref.sha256,ref.sha256,ref.size),8*MIB)
    return {'start':start,'complete':complete}


def _stage_implementation(receipt_record,code,locations):
    """Check receipt-bound origin/runtime bytes, not the present working tree."""
    from scripts.whole_source.execution import ExecutionPlan
    from scripts.whole_source.receipts import _stage_binding
    receipt = json.loads(_raw(Path(receipt_record['directory']),
                             ArtifactRef(**receipt_record['artifact']),8*MIB))
    attempt = Path(receipt_record['directory']).parent
    stage_path, stage = _stage_binding(Path(receipt_record['directory'])/'receipt.json', receipt)
    _require(stage.get('format') in ('whole-source-task-stage-v2','whole-source-task-stage-v3') and
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
    _require(type(contexts) is list and
             all(type(p) is str and (p == 'source-context' or p.endswith('/source-context')) for p in contexts) and
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


def _phase_supervision(run, phase, row, admitted, current, *, code_root):
    """Verify original dispatch/continuation using the private guardian placement."""
    from scripts.whole_source import admission, supervision
    from scripts.whole_source.coordinator import operation_inputs, operation_record
    directory = Path(row['directory'])
    document = _document(admitted)
    portable = document.get('format') == admission.FORMAT
    inputs = operation_inputs(run, row['inputs'], code_root=code_root) if portable else row['inputs']
    binding = admission.verify_attempt(document, phase=phase, directory=directory, inputs=inputs,
                                       legacy_inputs=row['inputs'])
    receipt, receipt_ref = supervision.read_phase_authority(binding, current=current)
    _require(receipt.get('status') in ('COMPLETED','INTERRUPTED') and
             receipt.get('cleanup_verified') is True and
             type(receipt.get('final_job')) is dict and
             receipt['final_job'].get('active_process_count') == 0,
             'selected phase supervisor cleanup is unverified')
    if not portable:
        observed = str(Path(current['root']))
        return {'phase': phase, 'attempt_directory': str(directory),
                'phase_completion': row['record'], 'admission': admitted,
                'supervision': binding, 'intent': {'directory': observed, 'artifact': binding['intent']},
                'receipt': {'directory': observed, 'artifact': receipt_ref},
                'observation': {'directory': observed, 'artifact': receipt['observation']},
                'invocation_status': receipt['status']}
    return {'phase': phase, 'attempt_id': directory.name,
            'phase_completion': operation_record(run, row['record']),
            'admission': operation_record(run, admitted), 'supervision': binding,
            'intent': binding['intent'], 'receipt': receipt_ref,
            'observation': receipt['observation'], 'invocation_status': receipt['status']}


def _selected_supervision(run, root, *, selected=None):
    """Bind every selected attempt's original dispatch and all resumed work."""
    from scripts.whole_source import supervision
    from scripts.whole_source.coordinator import PHASES, read_phase_records
    current = supervision.require_current()
    _require(all(_ref(root, name).sha256 == digest for name, digest in current['code'].items()),
             'selected phase supervisor implementation root differs')
    run = Path(run).resolve()
    selected = read_phase_records(run, code_root=root) if selected is None else selected
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
                result.append(_phase_supervision(run, phase, row, _record(path), current, code_root=root))
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
    from scripts.whole_source.selection import _replay_child, _replay_invocation, validate_pipeline
    original, selected = validate_pipeline(run, root)
    _require('controls' in selected and 'replay' in selected, 'required coordinator phases are incomplete')
    pipeline = _record(run/'pipeline-result.json')
    controls = selected['controls']['outputs']['controls']
    replayed = selected['replay']['outputs']['replay']
    replay_document = _document(replayed)
    replay_directory = Path(selected['replay']['directory'])
    tree, child_run = _replay_child(run, replay_directory, replay_document, root)
    child = _record(child_run/'pipeline-result.json')
    child_document, child_selected = validate_pipeline(child_run, tree)
    if replay_document['format'] in _SCOPED_REPLAY_FORMATS:
        proposal = _safe(tree, _REPLAY_PROPOSAL.as_posix())
        _require(child_document['proposal'] == _record(proposal)
                 and _bytes(child_run/'integration-execution.json') == _bytes(run/'integration-execution.json'),
                 'replay child changed captured configuration or installed proposal')
        _replay_invocation(replay_document, tree, child_run, proposal)
    supervisor_receipts += _selected_supervision(child_run, tree, selected=child_selected)
    pid = problem_id(bind_problem('retained-t081',root=root))
    for directory,document in ((run,original),(child_run,child_document)):
        _require(document.get('problem_id')==pid,'coordinator problem differs')
        _require(document.get('format') in ('whole-source-pipeline-result-v3', _PIPELINE_FORMAT),
                 'unqualified pipeline format')
        publication = _document(document['source_publication'])
        audit_execution = _document(document['audit_execution'])
        _require(publication.get('format')=='whole-source-publication-execution-v2' and
                 publication.get('source_manifest')==document['source']['artifact'] and
                 publication.get('provenance',{}).get('kind')=='OWNED_SOURCE' and
                 audit_execution.get('format') in (
                     'whole-source-audit-execution-v1','whole-source-audit-execution-v2') and
                 audit_execution.get('audit')==document['audit']['artifact'] and
                 audit_execution.get('source',{}).get('execution')==document['source_publication']['artifact'],
                 'reviewed publication/execution binding differs')
        _require(document.get('implementation')==_record(directory/'implementation/start.json'),
                 'pipeline omits coordinator implementation identity')
    coordinators = [
        _coordinator_implementation(run,'science',{'pipeline':pipeline},code,capture,pid),
        _coordinator_implementation(Path(selected['controls']['directory']), 'controls',
                                    {'controls': controls}, code, capture, pid),
        _coordinator_implementation(replay_directory, 'replay', {'replay': replayed}, code, capture, pid),
        _coordinator_implementation(child_run,'science',{'pipeline':child},code,capture,pid)]
    stages,seen = [],set()
    replay_receipts = []
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
            _require(Path(receipt['directory']).is_relative_to(child_run),
                     'replay stage outside captured scientific execution')
            replay_receipts.append(receipt)
        seen.add((group,bound['role'],bound['function']))
        stages.append(bound)
    _require(required<=seen,'missing required reviewed execution stages')
    if replay_document['format'] in _SCOPED_REPLAY_FORMATS:
        _require(canonical_bytes(replay_document.get('owned_cleanup')) ==
                 canonical_bytes(_replay_cleanup(child_run, replay_receipts)), 'replay lacks genuine owned cleanup')
    if original['format'] == _PIPELINE_FORMAT:
        from scripts.whole_source.coordinator import operation_record
        _require(all('attempt_id' in row for row in supervisor_receipts),
                 'portable review requires original portable supervisor authority')
        return {'format':'whole-source-review-manifest-v6','code':code,
            'inherited_capture':capture,'pipeline_result':operation_record(run, pipeline),
            'controls':operation_record(run, controls),'replay':operation_record(run, replayed),
            'runtime_versions':_runtime_versions(),'receipt_policy':'artifact-derived-source-stages-v1',
            'supervisor_receipts':supervisor_receipts,
            'publications':[operation_record(run,row[key]) for row in (original,child_document)
                            for key in ('source_publication','audit_execution')],
            'coordinators':[{key:operation_record(run, value) for key,value in entry.items()}
                            for entry in coordinators],
            'stages':[{**entry, **{key:operation_record(run,entry[key]) for key in ('receipt','stage','origin')}}
                      for entry in stages],
            'production_admission':False}
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
            _require(manifest.get('format') == 'whole-source-review-manifest-v6',
                     'fresh review preparation requires a portable scientific run')
            from scripts.whole_source.storage import reserve_destination
            reserve_destination(run,output)
            _write(output/'implementation-manifest.json',canonical_bytes(manifest))
    implementation = {'role':'review-implementation',
                      'artifact':_record(output/'implementation-manifest.json')['artifact']}
    return {'status':'COMPLETE_IMPLEMENTATION_EVIDENCE_PENDING_INDEPENDENT_REVIEW',
            'implementation':implementation,'production_admission':False}


def _review_implementation_location(run, root, binding):
    if type(binding) is dict and set(binding) == {'role','artifact'}:
        _require(binding['role'] == 'review-implementation', 'unknown independent review role')
        ref = ArtifactRef(**binding['artifact'])
        _require(ref.path == 'implementation-manifest.json', 'unexpected independent review artifact')
        from scripts.whole_source.coordinator import _absolute
        configured = os.environ.get('RH_WHOLE_SOURCE_REVIEW_DIRECTORY')
        _require(configured is not None, 'private independent review directory is required')
        directory = _absolute(configured)
        _check_review_output(run,directory,root)
        _root_path(directory)
        return directory, ref
    from scripts.whole_source.coordinator import _artifact_record
    return _artifact_record(binding, verify=False)


def _review_implementation(run, root, binding):
    directory, ref = _review_implementation_location(run, root, binding)
    return _json(_raw(directory,ref,8*MIB))


def _validate_review(run,root):
    review = _json(_bytes(Path(run)/'review-decision.json'))
    _require(type(review) is dict and set(review)=={
        'format','disposition','pipeline_result','controls','replay','implementation','code'} and
        review.get('format') in ('whole-source-independent-review-v4','whole-source-independent-review-v5') and
        review.get('disposition')=='NO_UNRESOLVED_CORRECTNESS_FINDINGS',
        'independent review requires a complete phase-bound contract')
    code,_,_ = _implementation_code(root)
    _reviewed_code(review.get('code'),code)
    expected = _review_manifest(run,root)
    expected_format = ('whole-source-independent-review-v5' if expected['format'] == 'whole-source-review-manifest-v6'
                       else 'whole-source-independent-review-v4')
    _require(review['format'] == expected_format and
             (('role' in review['implementation']) == (expected_format == 'whole-source-independent-review-v5')) and
             all(review[key]==expected[key] for key in ('pipeline_result','controls','replay')) and
             _review_implementation(run,root,review['implementation'])==expected,
             'independent review does not bind the executed implementation')
    return review


_ACCEPTANCE_FORMAT = 'whole-source-reviewed-acceptance-v7'
_LEGACY_ACCEPTANCE_FORMAT = 'whole-source-reviewed-acceptance-v6'


def _acceptance_paths(run, report, *, decode):
    from scripts.whole_source.coordinator import operation_record, resolve_operation_record
    binding = resolve_operation_record if decode else operation_record
    roles = ('scalar_premises','source','audit','proposal','exact','source_publication',
             'audit_execution','controls','replay','review')
    return {**report, **{key:binding(run,report[key]) for key in roles},
            'owned_receipts':[binding(run,receipt) for receipt in report['owned_receipts']]}


def _assess_local(run,root):
    _selected_supervision(run, root)
    problem = bind_problem('retained-t081',root=root)
    result = _pipeline_document(run, root)
    source,audit,exact,proposal,premises = (_document(result[key]) for key in ('source','audit','exact','proposal','premises'))
    _require(source['full_mathematical_source'] is True and source['control'] is False and
             audit['status']=='VERIFIED_ALL_DECLARED_SOURCE_ENTRIES' and audit['entries_checked']==FULL_ENTRIES and
             audit['source_manifest']==result['source']['artifact'] and audit['full_mathematical_source'] is True and
             audit['problem_id']==result['problem_id']==problem_id(problem),'incomplete source/audit conjunction')
    exact_fingerprints = exact.get('format') == 'whole-source-exact-assessment-v2'
    def expected_ref(role):
        ref = result[role]['artifact']
        return {key:ref[key] for key in ('sha256','size')} if exact_fingerprints else ref
    _require(result['fresh_proposal'] is True and proposal.get('status')=='NONPROOF_ONLY' and
             proposal.get('scope')=='NONPROOF_PROPOSAL_ONLY' and
             proposal['source']==result['source']['artifact'] and
             exact['source']['manifest']==expected_ref('source') and
             exact['proposal']['artifact']==expected_ref('proposal') and
             exact['proof_scope']=='SOURCE_CONDITIONAL' and
             exact['status']=='PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL', 'wrong source/proposal/exact binding')
    _require(premises['status']=='VERIFIED_FRESH_SCALAR_PREMISES' and len(premises['outputs'])==8,
             'fresh scalar-premise checks missing')
    review = _validate_review(run,root)
    from scripts.whole_source.controls import SOURCE_CASES,EXACT_CASES,_CONTROLS_FORMAT
    controls_ref = _selected_phase(run, 'controls', code_root=root)['outputs']['controls']
    selected_replay = _selected_phase(run, 'replay', code_root=root)
    replay_ref = selected_replay['outputs']['replay']
    controls, replayed = _document(controls_ref), _document(replay_ref)
    _require(controls['status']=='PASS_REQUIRED_MATHEMATICAL_CONTROLS' and
             replayed['status']=='PASS_COMPLETE_SCIENTIFIC_REPLAY_COMPARISON' and
             replayed['expected_new_outputs_installed'] is False,'control/replay conjunction failed')
    roles = ('source','audit','proposal','exact')
    expected_controls = ({key:{'role':key,'artifact':result[key]['artifact']} for key in roles}
                         if controls['format'] == _CONTROLS_FORMAT else {key:result[key] for key in roles})
    _require([row['case'] for row in controls['cases']]==[name for name,_ in (*SOURCE_CASES,*EXACT_CASES)] and
             all(row['passed'] is True for row in controls['cases']) and
             all(controls[key]==expected_controls[key] for key in roles),
             'missing, rebound or unsuccessful mathematical controls')
    for row in controls['cases']:
        _require(_json(_bytes(Path(controls_ref['directory'])/row['case']/'case-result.json'))==row,
                 'changed mathematical case evidence')
    from scripts.whole_source.selection import _replay_child
    tree, child_run = _replay_child(run, Path(selected_replay['directory']), replayed, root)
    child = _pipeline_document(child_run, tree)
    _require(child['fresh_proposal'] is False,'replay must install bound NONPROOF coordinates')
    compared = compare_science(run,child_run,first_root=root,second_root=tree)
    _require(all(replayed.get(key) == value for key, value in compared.items()),
             'replay lacks genuine captured scientific comparison')
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
        output = value['output']
        if premises['format'] == 'whole-source-scalar-premises-v2':
            from scripts.whole_source.coordinator import resolve_operation_record
            premises_root = Path(result['premises']['directory'])
            receipt = resolve_operation_record(premises_root,premises['owned_receipts'][value['index']])
            _document(receipt)
            output = resolve_operation_record(_phase_path(receipt).parents[1],output)
        _document(output)
    portable = review['format'] == 'whole-source-independent-review-v5'
    report = {'format':_ACCEPTANCE_FORMAT if portable else _LEGACY_ACCEPTANCE_FORMAT,
        'implementation':review['implementation'],
        'status':'PASS_NEW_SOURCE_CONDITIONAL_REFERENCE_QUALIFICATION','problem_id':problem_id(problem),
        'entries_checked':FULL_ENTRIES,'dimensions':[413,413],'gamma':consequence['gamma'],
        'conservative_source_norm_floor':FLOOR,'scalar_premises':result['premises'],
        'source':result['source'],'audit':result['audit'],'proposal':result['proposal'],'exact':result['exact'],
        'source_publication':result['source_publication'],'audit_execution':result['audit_execution'],
        'controls':controls_ref,'replay':replay_ref,
        'owned_receipts':receipts,'review':_record(run/'review-decision.json'),
        'supervisor_receipts':_review_implementation(run,root,review['implementation'])['supervisor_receipts'],
        'premises':'Suzuki/source-form agreement; reviewed scalar bounds; FLINT/Arb/Gauss enclosures',
        'unitary_physical_L2_scaling':True,'production_admission':False,'RH_proved':False}
    return _acceptance_paths(run,report,decode=False) if portable else report


def _assessment_request(run):
    return _request(run='operation', pipeline=_replay_fingerprint(run, 'pipeline-result.json'),
                    review=_replay_fingerprint(run, 'review-decision.json'))


def _assessment_roots(lease):
    """Recover the live operation from the guardian, never from task data."""
    from scripts.whole_source.coordinator import _absolute
    from scripts.whole_source.supervision import _wire, runtime_operation_roots
    current = runtime_operation_roots(lease)
    if current is not None:
        run,root = current
        _root_path(run)
        return run,root
    observer = _absolute(lease['root'])
    _root_path(observer)
    suffix = '.lifecycle'
    _require(observer.name.endswith(suffix) and len(observer.name) > len(suffix),
             'invalid assessment operation observer')
    run = observer.with_name(observer.name.removesuffix(suffix))
    _root_path(run)
    for root in run.parents:
        identity = hashlib.sha256(_wire({'operation': str(run), 'code_root': str(root)})).hexdigest()
        if identity == lease['operation_id']:
            return run, root
    raise ContractError('assessment operation is not bound to a live code root')


def _assessment_inputs(run, root, review):
    directory, ref = _review_implementation_location(run,root,review['implementation'])
    records = (
        _record(run/'pipeline-result.json'),
        _record(run/'review-decision.json'),
        _selected_phase(run,'controls',code_root=root)['outputs']['controls'],
        _selected_phase(run,'replay',code_root=root)['outputs']['replay'],
        {'directory':str(directory),'artifact':asdict(ref)})
    return dict(zip(ASSESSMENT_INPUTS, records, strict=True))


def _check_assessment_inputs(run,root,review,refs):
    for name,record in _assessment_inputs(run,root,review).items():
        artifact = record['artifact']
        _require(refs.get(name) == asdict(ArtifactRef(name,artifact['sha256'],artifact['size'])),
                 'assessment input differs from captured binding')


def evaluate_acceptance(task,staging):
    from scripts.whole_source import execution, supervision
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
    run, root = _assessment_roots(supervision.require_current())
    expected = _assessment_request(run)
    _require(canonical_bytes(task) == canonical_bytes(expected), 'assessment task belongs to another run')
    review = _validate_review(run,root)
    if review['format'] == 'whole-source-independent-review-v5':
        _check_assessment_inputs(run,root,review,{ref.path:asdict(ref) for ref in staging.spec.code_refs})
    else:
        refs = {ref.path:ref for ref in staging.spec.code_refs}
        for role,name in (('pipeline','pipeline-result.json'),('review','review-decision.json')):
            relative = (run/name).relative_to(root).as_posix()
            _require(refs.get(relative) == ArtifactRef(relative, **expected[role]),
                     'assessment input differs from captured binding')
    return _assess_local(run, root)


def _completed_assessment(run,output,root):
    """Reconstruct the published report from strict, frozen owned evidence."""
    review = _validate_review(run,root)
    code,_,locations = _implementation_code(root)
    manifest = _review_implementation(run,root,review['implementation'])
    _reviewed_code(manifest['code'],code)
    records = _verify_receipts(output/'collection',code_root=root)
    _require(len(records)==1,'retention requires exactly one completed owned assessment')
    implementations = [_stage_implementation(record,code,locations) for record in records]
    implementation = implementations[0]
    from scripts.whole_source.execution import _resolve_stage
    binding = implementation['stage']
    stage = _resolve_stage(_document(binding), Path(binding['directory'])/binding['artifact']['path'])
    plan = stage['plan']
    _require(implementation['role']=='exact' and implementation['function']=='evaluate_acceptance' and
             plan['backend']=='python-flint-exact' and plan['scope']=='EXACT_ASSESSMENT_ONLY' and
             stage['task_count']==1,'retention requires the reviewed exact assessment stage')
    task = _json(_bytes(Path(stage['task_file'])))
    expected = (_request(run=str(run)) if stage['format'] == 'whole-source-task-stage-v2'
                else _assessment_request(run))
    _require(canonical_bytes(task) == canonical_bytes(expected), 'assessment task belongs to another run')
    result_dir = Path(stage['result_dir'])
    row = _json(_bytes(result_dir/'completed.jsonl'))
    payload = _json(_raw(result_dir,ArtifactRef(**{k:row[k] for k in ('path','sha256','size')}),4*MIB))
    _require(payload['task_id']==task['task_id'],'assessment result belongs to another task')
    report = payload['result']
    _require(type(report) is dict,'invalid completed assessment result')
    pipeline = _pipeline_document(run, root)
    portable = review['format'] == 'whole-source-independent-review-v5'
    if portable:
        _check_assessment_inputs(run,root,review,{ref['path']:ref for ref in stage['collection']['code_refs']})
    _require(report.get('format') == (_ACCEPTANCE_FORMAT if portable else _LEGACY_ACCEPTANCE_FORMAT),
             'unknown reviewed acceptance format')
    checked = _acceptance_paths(run,report,decode=True) if portable else report
    _require(
             report.get('status')=='PASS_NEW_SOURCE_CONDITIONAL_REFERENCE_QUALIFICATION' and
             report.get('problem_id')==pipeline['problem_id'] and
             report.get('implementation')==review['implementation'] and
             checked.get('review')==_record(run/'review-decision.json') and
             report.get('production_admission') is False and report.get('RH_proved') is False,
             'completed assessment is not bound to this reviewed qualification')
    _require(all(checked.get(key)==pipeline[key] for key in
                 ('source','audit','proposal','exact','source_publication','audit_execution')) and
             checked.get('scalar_premises')==pipeline['premises'] and
             checked.get('controls')==_selected_phase(run, 'controls', code_root=root)['outputs']['controls'] and
             checked.get('replay')==_selected_phase(run, 'replay', code_root=root)['outputs']['replay'] and
             checked.get('owned_receipts')==_verify_receipts(run,code_root=root),
             'completed assessment scientific evidence changed')
    _require(report.get('supervisor_receipts') == manifest['supervisor_receipts'],
             'completed assessment supervisor authority changed')
    for key in ('source','audit','proposal','exact','premises','problem','source_execution',
                'source_publication','audit_execution'):
        _document(pipeline[key])
    report['assessment_owned_receipts'] = exact_telemetry([
        json.loads(_raw(Path(record['directory']),ArtifactRef(**record['artifact']),8*MIB))
        for record in records])
    if portable:
        from scripts.whole_source.coordinator import operation_record
        report['assessment_implementation'] = [
            {**entry, **{key:operation_record(output,entry[key]) for key in ('receipt','stage','origin')}}
            for entry in implementations]
    else:
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
            return _seal(run,independent_diagnostics=expected['format'] == _ACCEPTANCE_FORMAT)


def _assessment_context(run,output,root,configuration,*,legacy=False):
    code,capture,_ = _implementation_code(root)
    data = {'format':'whole-source-assessment-publication-v2',
            'destination':'assessment.json','pipeline':_replay_fingerprint(run,'pipeline-result.json'),
            'review':_replay_fingerprint(run,'review-decision.json'),'code':code,'capture':capture,
            'runtime':_runtime_versions(),'configuration':configuration}
    if legacy:
        return {'format':'whole-source-wave-recovery-v1','operation':'assessment','output':str(output),
                'python':sys.version,'configuration':{
                    **data,'format':'whole-source-assessment-publication-v1',
                    'run':str(run),'code_root':str(root),'destination':str(output/'assessment.json'),
                    'pipeline':_record(run/'pipeline-result.json'),'review':_record(run/'review-decision.json')}}
    return {'format':'whole-source-assessment-context-v2','operation':'assessment','python':sys.version,
            'configuration':data}


def _assessment_publication_context(run,output,root):
    """Require a prospective original context, not a historical result repair."""
    path = _safe(output,'assessment-publication.json')
    context = _json(_bytes(path))
    configuration = context.get('configuration',{}).get('configuration')
    _require(type(configuration) is dict and set(configuration)=={'collection','execution'},
             'missing prospective assessment publication context')
    legacy = context.get('format') == 'whole-source-wave-recovery-v1'
    _require(context==_assessment_context(run,output,root,configuration,legacy=legacy),
             'assessment publication context or revision changed')
    return context


def _publish_assessment(run,output,root,context):
    from scripts.whole_source.recovery import check_history, finish_publication
    check_history(output/'collection')
    report = _completed_assessment(run,output,root)
    implementations = report['assessment_implementation']
    _require(len(implementations)==1, 'expected exactly one assessed implementation')
    portable = context['format'] == 'whole-source-assessment-context-v2'
    _require(not portable or report.get('format') == _ACCEPTANCE_FORMAT,
             'portable publication requires a portable owned result')
    binding = implementations[0]['stage']
    if portable:
        from scripts.whole_source.coordinator import resolve_operation_record
        binding = resolve_operation_record(output,binding)
    stage = _document(binding)
    _require(
             {'collection':stage['collection'],'execution':stage['plan']}==
             context['configuration']['configuration'],
             'assessment stage differs from original publication configuration')
    intent = {'format':'whole-source-assessment-terminal-v2' if portable else 'whole-source-assessment-terminal-v1',
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
        with admitted_phase('assessment', problem, run, root, external=output, resume_external=True):
            _check_review_output(run,output,root)
            _check_sealed_output(run)
            with _slice_writer(output,resume=True):
                context = _assessment_publication_context(run,output,root)
                report = _publish_assessment(run,output,root,context)
                _seal(run,independent_diagnostics=report['format'] == _ACCEPTANCE_FORMAT)
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
    from scripts.whole_source.supervision import require_current
    root,run,output = Path(code_root).resolve(),Path(run_dir).resolve(),Path(output_dir).resolve()
    _require((run, root) == _assessment_roots(require_current()), 'wrong live assessment operation')
    _check_sealed_output(run)
    _selected_supervision(run, root)
    result = _pipeline_document(run, root)
    problem,source_config,bound = bind_source(Path(result['problem']['directory'])/result['problem']['artifact']['path'],
        Path(result['source_execution']['directory'])/result['source_execution']['artifact']['path'],root)
    _require((run/'review-decision.json').is_file(),'independent execution review is required before release')
    review = _validate_review(run,root)
    _check_review_output(run,output,root)
    _check_sealed_output(run)
    _require(review['format'] == 'whole-source-independent-review-v5',
             'fresh assessment requires portable review evidence')
    from scripts.whole_source.storage import reserve_destination
    reserve_destination(run,output)
    base_spec,base_plan = bound['analytic']
    refs = {r.path:r for r in base_spec.code_refs}
    for name in CODE:
        refs[name] = _ref(root,name)
    _,capture,locations = _implementation_code(root)
    for name in (capture['path'],*(stored for stored,_ in locations.values())):
        refs[name] = _ref(root,name)
    # Copy only the five explicitly bound assessment inputs under generated names.
    for name,record in _assessment_inputs(run,root,review).items():
        original = ArtifactRef(**record['artifact'])
        raw = _raw(Path(record['directory']),original,8*MIB)
        target = output/name
        target.parent.mkdir(exist_ok=True)
        _write(target,raw)
        refs[name] = ArtifactRef(name,original.sha256,original.size)
    spec = CollectionSpec.create(problem,role='exact',quantities=base_spec.quantities,
        partition=base_spec.partition,backend='python-flint-exact',backend_version=base_spec.backend_version,
        native_threads=1,code_refs=tuple(refs[name] for name in sorted(refs)),bounds=base_spec.bounds,
        code_root=root,auxiliary_root=output,auxiliary_role='assessment')
    from scripts.whole_source.pipeline import _source_origin_root
    source_origin = _source_origin_root(_phase_path(result['source_execution']),source_config)
    provenance = _json(_raw(source_origin or root,base_plan.provenance,8*MIB))
    provenance['files'] = [asdict(ref) for ref in spec.code_refs]
    _check_review_output(run,output,root)
    _check_sealed_output(run)
    _write(output/ASSESSMENT_ORIGIN,canonical_bytes(provenance))
    from scripts.whole_source.admission import phase_caller_account
    review_private_mib = (phase_caller_account('assessment', problem, run=run)['required_bytes']+MIB-1)//MIB
    plan = replace(base_plan,role='exact',collection_sha256=spec.collection_id,
        resource_policy=None,workers=1,worker_private_mib=max(base_plan.worker_private_mib,review_private_mib),
        codec_mib=(base_plan.codec_mib+base_plan.workers-1)//base_plan.workers,
        reserve_mib=(base_plan.resource_policy["baseline"]["reserve_mib"]
                     if base_plan.resource_policy is not None else base_plan.reserve_mib),
        backend='python-flint-exact',precision_bits=65536,max_tasks=1,result_bytes=4*MIB,queue_mib=16,
        task_program=refs['scripts/whole_source/retention.py'],task_function='evaluate_acceptance',
        scope='EXACT_ASSESSMENT_ONLY',provenance=_ref(output,ASSESSMENT_ORIGIN))
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
            with WorkloadExecution(lock,spec,plan,code_root=root,auxiliary_root=output) as execution:
                execution.run_stage('reviewed-consequence',[_assessment_request(run)])
        report = _publish_assessment(run,output,root,context)
        _seal(run,independent_diagnostics=True)
    return report


def run(problem_path, execution_path, output_dir, *, code_root=ROOT, resume=False, through='replay'):
    from scripts.whole_source.coordinator import PHASES
    from scripts.whole_source.supervision import _failure, require_current
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
                        'format': 'whole-source-coordinator-failure-v2',
                        'status': 'FAILED_NO_REFERENCE_ACCEPTANCE',
                        'error': _failure(exc), 'production_admission': False})
                    _write(output/('failure-'+uuid.uuid4().hex+'.json'), failure)
            except (ContractError, OSError):
                exc.add_note('Failure receipt could not be admitted')
            raise
