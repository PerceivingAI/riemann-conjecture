"""Fresh whole-source qualification, captured replay and conditional acceptance.

Reports are evidence from reviewed local drivers, not signatures from arbitrary
untrusted processes. Installed FLINT/Arb and source-form premises remain explicit.
"""
from __future__ import annotations
from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import time
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
           'receipts','source_dependencies')))
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
    config = {'format':'whole-source-integrated-execution-v2','problem_id':problem_id(problem),
        'origin_git_commit':origin_git_commit,'origin_git_dirty':origin_git_dirty,
        'tile_modes':32,'resource_policy':'detected-capacity-v1',
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
        'resource_policy','minimum_free_bytes','gamma_floor','code',
        'replay_exclusions','scope','production_admission'} and
        config['format']=='whole-source-integrated-execution-v2' and
        config['problem_id']==problem_id(problem) and config['tile_modes']==32 and
        config['resource_policy']=='detected-capacity-v1' and
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
            runpy.run_path(str(program),run_name='__main__')
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
    """Verify source dependency selections; verify all other owned stages strictly."""
    from scripts.whole_source.receipts import discover_receipts, verify_stage
    paths = discover_receipts(directory)
    _require(paths, 'missing owned execution receipts')
    rows, collections = [], set()
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
            rows.append(verify_stage(path)['record'])
    _require(rows, 'no complete owned stage evidence')
    return sorted(rows, key=lambda row: str(Path(row['directory'])/row['artifact']['path']))


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


def _execute(problem,config,output,root,*,proposal_input=None):
    from scripts.whole_source.pipeline import prepare_source_inputs,run_source,run_audit,_bind
    from scripts.whole_source.proposal import prepare_proposal_inputs,run_proposal
    from scripts.whole_source.exact import prepare_exact_inputs,run_exact
    origin = {'origin_git_commit':config['origin_git_commit'],'origin_git_dirty':config['origin_git_dirty']}
    implementation = _capture_implementation(problem,output,root,'science')
    inputs = prepare_source_inputs(problem,output/'source-inputs',code_root=root,tile_modes=32,**origin)
    _,_,bound = _bind(inputs['problem'],inputs['execution'],root)
    run_premises(problem,*bound['analytic'],output/'premises',code_root=root)
    run_source(inputs['problem'],inputs['execution'],output/'source',code_root=root)
    source = output/'source/producer/source-manifest.json'
    audit = run_audit(inputs['problem'],source,inputs['execution'],output/'audit',code_root=root)
    _require(audit['entries_checked']==FULL_ENTRIES and audit['full_mathematical_source'] is True,
             'full independent source reconstruction did not pass')
    if proposal_input is None:
        proposal_inputs = prepare_proposal_inputs(problem,source,output/'proposal-inputs',code_root=root,**origin)
        run_proposal(proposal_inputs['problem'],source,proposal_inputs['execution'],output/'proposal',code_root=root)
        proposal = output/'proposal/proposal.json'
    else:
        proposal = Path(proposal_input)
    exact_inputs = prepare_exact_inputs(problem,source,proposal,output/'exact-inputs',code_root=root,**origin)
    exact = run_exact(exact_inputs['problem'],source,proposal,exact_inputs['execution'],output/'exact',code_root=root)
    _require(exact['assessment']['positive_paid_lower'] is True and
             exact['proof_scope']=='SOURCE_CONDITIONAL','full exact assessment did not pass')
    result = {'format':'whole-source-pipeline-result-v2','status':'COMPLETE_FRESH_SOURCE_AUDIT_AND_EXACT',
        'problem_id':problem_id(problem),'source':_record(source),
        'audit':_record(output/'audit/analytical-receipt.json'),'proposal':_record(proposal),
        'exact':_record(output/'exact/report.json'),'premises':_record(output/'premises/premises-receipt.json'),
        'source_execution':_record(inputs['execution']),'problem':_record(inputs['problem']),
        'source_publication':_record(source.parent/'source-execution.json'),
        'audit_execution':_record(output/'audit/audit-execution.json'),
        'implementation':implementation,
        'gamma':exact['assessment']['gamma'],'fresh_proposal':proposal_input is None,'production_admission':False}
    _write(output/'pipeline-result.json',canonical_bytes(result))
    _complete_implementation(output,root,{'pipeline':_record(output/'pipeline-result.json')})
    return result


def replay(run_dir,output_dir,*,code_root=ROOT):
    root,run,output = Path(code_root).resolve(),Path(run_dir).resolve(),Path(output_dir).resolve()
    result = _json(_bytes(run/'pipeline-result.json'))
    problem = bind_problem('retained-t081',root=root)
    output.mkdir(parents=True,exist_ok=False)
    _capture_implementation(problem,output,root,'replay')
    tree = output/'captured-root'
    proposal = Path(result['proposal']['directory'])/result['proposal']['artifact']['path']
    capture_inputs(problem,tree,code_root=root,proposal_path=proposal)
    child_run = tree/run.relative_to(root)
    _require(not any((child_run/name).exists() for name in ('source','audit','exact','source-inputs')),
             'expected scientific outputs leaked into replay')
    child_run.mkdir(parents=True,exist_ok=True)
    _new_copy(run/'integration-execution.json',child_run/'integration-execution.json')
    child_proposal = tree/proposal.relative_to(root)
    # Imported module ROOT is not the captured module. Execute a separate Python
    # interpreter whose project imports resolve only from the captured tree.
    import subprocess
    entry = "import sys;sys.path.insert(0,sys.argv[1]);from scripts.whole_source.retention import _replay_child;_replay_child(sys.argv[2],sys.argv[3],sys.argv[4])"
    env = os.environ.copy()
    env.pop('PYTHONPATH',None)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    command = [sys.executable,'-I','-B','-c',entry,str(tree),str(child_run),
               str(child_run/'integration-execution.json'),str(child_proposal)]
    with (output/'stdout.txt').open('xb') as stdout,(output/'stderr.txt').open('xb') as stderr:
        process = subprocess.run(command,cwd=tree,env=env,stdout=stdout,stderr=stderr,check=False)
    _require(process.returncode==0,'captured scientific replay failed')
    compared = compare_science(run,child_run)
    receipt = {'format':'whole-source-scientific-replay-v1',**compared,
        'original_run':_record(run/'pipeline-result.json'),'replayed_run':_record(child_run/'pipeline-result.json'),
        'capture':_record(tree/'capture-manifest.json'),'expected_new_outputs_installed':False,
        'argv':command,'exit_code':process.returncode,'shared_installed_arithmetic_runtime':True,
        'owned_receipts':_verify_receipts(child_run)}
    _write(output/'replay-receipt.json',canonical_bytes(receipt))
    _complete_implementation(output,root,{'replay':_record(output/'replay-receipt.json')})
    return receipt


def _replay_child(run_dir,config_path,proposal_path):
    run = Path(run_dir)
    config = _json(_bytes(Path(config_path)))
    problem = bind_problem('retained-t081',root=ROOT)
    for ref in config['code']:
        _raw(ROOT,ArtifactRef(**ref),8*MIB)
    _execute(problem,config,run,ROOT,proposal_input=Path(proposal_path))


def _inventory_files(directory,excluded):
    return sorted(p.relative_to(directory).as_posix() for p in directory.rglob('*')
                  if p.is_file() and p.relative_to(directory).as_posix() not in excluded)


def _snapshot_rows(directory,ref):
    ref = ArtifactRef(**ref)
    path = _safe(directory,ref.path)
    _require(_hash_file(path)=={'size':ref.size,'sha256':ref.sha256},'changed inventory snapshot')
    with path.open('rb') as stream:
        while raw := stream.readline(8*MIB+1):
            _require(len(raw)<=8*MIB,'oversized inventory member')
            yield _json(raw)


def _verify_inventory_rows(directory,rows):
    previous = ''
    for row in rows:
        _require(type(row) is dict and set(row)=={'path','size','sha256'} and
                 type(row['path']) is str and row['path']>previous,'invalid inventory member ordering')
        ref = ArtifactRef(**row)
        _require(_hash_file(_safe(directory,ref.path))=={'size':ref.size,'sha256':ref.sha256},
                 'retained member changed')
        previous = row['path']


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
    rows = []
    for shard in manifest['shards']:
        document = _json(_raw(directory,ArtifactRef(**shard),8*MIB))
        _require(type(document) is dict and set(document)=={'files'} and
                 type(document['files']) is list,'invalid inventory shard')
        rows.extend(document['files'])
    _verify_inventory_rows(directory,rows)
    _require(rows==list(_snapshot_rows(directory,manifest['snapshot'])),'inventory snapshot coverage differs')
    excluded = {'.slice.lock','retained-manifest.json'} | active
    actual = _inventory_files(directory,excluded)
    _require([row['path'] for row in rows]==actual,'incomplete retained inventory')
    return len(rows)


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
        rows = list(_snapshot_rows(directory,intent['snapshot']))
        _verify_inventory_rows(directory,rows)
        for shard in sorted(path.parent.glob('[0-9]*.json')):
            _require(shard.stem.isdecimal(),'invalid pending inventory shard')
            index = int(shard.stem)
            _require(shard.name=='%06d.json'%index and index*4096<len(rows),
                     'unexpected pending inventory shard')
            _require(_bytes(shard)==canonical_bytes({'files':rows[index*4096:(index+1)*4096]}),
                     'conflicting pending inventory shard')


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
    rows = [{'path':name,**_hash_file(_safe(directory,name))}
            for name in _inventory_files(directory,{'.slice.lock','retained-manifest.json'})]
    generation = uuid.uuid4().hex
    folder = directory/'inventory'/generation
    folder.mkdir(parents=True,exist_ok=False)
    snapshot = folder/'snapshot.jsonl'
    _write(snapshot,b''.join(canonical_bytes(row) for row in rows))
    snapshot_ref = asdict(_ref(directory,snapshot.relative_to(directory).as_posix()))
    intent = folder/'intent.json'
    _write(intent,canonical_bytes({'format':'whole-source-inventory-intent-v1','snapshot':snapshot_ref}))
    shards = []
    for index in range(0,len(rows),4096):
        path = folder/('%06d.json'%(index//4096))
        _write(path,canonical_bytes({'files':rows[index:index+4096]}))
        shards.append(asdict(_ref(directory,path.relative_to(directory).as_posix())))
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


def _capture_implementation(problem,directory,root,phase):
    """Capture coordinator code before work, separately from scientific identity."""
    root,directory = Path(root).resolve(),Path(directory).resolve()
    code,capture,locations = _implementation_code(root)
    # A source-root argument must not relabel a different executing coordinator.
    _require(_hash_file(Path(__file__))==_hash_file(root/'scripts/whole_source/retention.py'),
             'coordinator differs from declared implementation')
    for name,module in tuple(sys.modules.items()):
        if name in ('scripts.run_observability','scripts.weil_whole_source_split') or name.startswith('scripts.whole_source'):
            path = getattr(module,'__file__',None)
            if path is not None:
                logical = name.replace('.','/')+('.py' if not hasattr(module,'__path__') else '/__init__.py')
                _require(_hash_file(Path(path))==_hash_file(root/logical),
                         'loaded coordinator module differs from frozen implementation')
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


def _review_manifest(run,root):
    run,root = Path(run).resolve(),Path(root).resolve()
    code,capture,locations = _implementation_code(root)
    pipeline = _record(run/'pipeline-result.json')
    controls = _record(run/'controls/controls-receipt.json')
    replayed = _record(run/'replay/replay-receipt.json')
    replay_document = _document(replayed)
    child = replay_document['replayed_run']
    child_document = _document(child)
    original = _document(pipeline)
    pid = problem_id(bind_problem('retained-t081',root=root))
    for directory,document in ((run,original),(Path(child['directory']),child_document)):
        _require(document.get('problem_id')==pid,'coordinator problem differs')
        for key,folder in (('source_publication','source/producer'),('audit_execution','audit')):
            _require(Path(document[key]['directory']).resolve()==directory/folder,
                     'publication evidence outside reviewed execution tree')
        publication = _document(document['source_publication'])
        audit_execution = _document(document['audit_execution'])
        _require(publication.get('format')=='whole-source-publication-execution-v2' and
                 publication.get('source_manifest')==document['source']['artifact'] and
                 publication.get('provenance',{}).get('kind')=='OWNED_SOURCE' and
                 audit_execution.get('format')=='whole-source-audit-execution-v1' and
                 audit_execution.get('audit')==document['audit']['artifact'] and
                 audit_execution.get('source',{}).get('execution')==document['source_publication']['artifact'],
                 'reviewed publication/execution binding differs')
        for key,folder in (('source','source/producer'),('audit','audit'),('proposal','proposal'),
                           ('exact','exact'),('premises','premises'),('problem','source-inputs'),
                           ('source_execution','source-inputs')):
            _require(Path(document[key]['directory']).resolve()==directory/folder,
                     'scientific input outside reviewed execution tree')
        _require(document.get('implementation')==_record(directory/'implementation/start.json'),
                 'pipeline omits coordinator implementation identity')
    coordinators = [
        _coordinator_implementation(run,'science',{'pipeline':pipeline},code,capture,pid),
        _coordinator_implementation(run/'controls','controls',{'controls':controls},code,capture,pid),
        _coordinator_implementation(run/'replay','replay',{'replay':replayed},code,capture,pid),
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
        _require(group in {r[0] for r in required},'unexpected scientific execution group')
        if group=='replay':
            _require(Path(receipt['directory']).is_relative_to(Path(child['directory'])),
                     'replay stage outside captured scientific execution')
        seen.add((group,bound['role'],bound['function']))
        stages.append(bound)
    _require(required<=seen,'missing required reviewed execution stages')
    return {'format':'whole-source-review-manifest-v3','code':code,
        'inherited_capture':capture,'pipeline_result':pipeline,'controls':controls,'replay':replayed,
        'runtime_versions':_runtime_versions(),
        'receipt_policy':'artifact-derived-source-stages-v1',
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
    _require(not output.is_relative_to(run),'output must be outside the reviewed scientific run')
    _check_sealed_output(output)


def prepare_review(run_dir,output_dir,*,code_root=ROOT):
    """Prepare complete evidence for a human/independent review; never approve it."""
    run,output,root = Path(run_dir).resolve(),Path(output_dir).resolve(),Path(code_root).resolve()
    _check_review_output(run,output,root)
    with _slice_writer(run,resume=True):
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
        review.get('format')=='whole-source-independent-review-v2' and
        review.get('disposition')=='NO_UNRESOLVED_CORRECTNESS_FINDINGS',
        'independent review requires the complete v2 contract')
    code,_,_ = _implementation_code(root)
    _reviewed_code(review.get('code'),code)
    expected = _review_manifest(run,root)
    _require(all(review[key]==expected[key] for key in ('pipeline_result','controls','replay')) and
             _document(review['implementation'])==expected,
             'independent review does not bind the executed implementation')
    return review


def _assess_local(run,root):
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
    from scripts.whole_source.controls import SOURCE_CASES,EXACT_CASES
    controls = _json(_bytes(run/'controls/controls-receipt.json'))
    replayed = _json(_bytes(run/'replay/replay-receipt.json'))
    _require(controls['status']=='PASS_REQUIRED_MATHEMATICAL_CONTROLS' and
             replayed['status']=='PASS_COMPLETE_SCIENTIFIC_REPLAY_COMPARISON' and
             replayed['expected_new_outputs_installed'] is False,'control/replay conjunction failed')
    _require([row['case'] for row in controls['cases']]==[name for name,_ in (*SOURCE_CASES,*EXACT_CASES)] and
             all(row['passed'] is True for row in controls['cases']) and
             all(controls[key]==result[key] for key in ('source','audit','proposal','exact')),
             'missing, rebound or unsuccessful mathematical controls')
    for row in controls['cases']:
        _require(_json(_bytes(run/'controls'/row['case']/'case-result.json'))==row,
                 'changed mathematical case evidence')
    review = _validate_review(run,root)
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
    independently = SourceReader(run/'audit/analytic/source-manifest.json',bound['analytic'][0],control=False)
    _positive(problem,produced,independently,run/'audit/analytical-receipt.json')
    consequence = reviewed_consequence(problem,exact['blocks'])
    receipts = _verify_receipts(run, code_root=root)
    for value in premises['outputs']:
        _require(value['status']=='VERIFIED_FRESH_SCALAR_PREMISE' and
                 value['byte_identical_to_reviewed_scalar'] is True,'scalar reconstruction failed')
        _document(value['output'])
    report = {'format':'whole-source-reviewed-acceptance-v4','implementation':review['implementation'],
        'status':'PASS_NEW_SOURCE_CONDITIONAL_REFERENCE_QUALIFICATION','problem_id':problem_id(problem),
        'entries_checked':FULL_ENTRIES,'dimensions':[413,413],'gamma':consequence['gamma'],
        'conservative_source_norm_floor':FLOOR,'scalar_premises':result['premises'],
        'source':result['source'],'audit':result['audit'],'proposal':result['proposal'],'exact':result['exact'],
        'source_publication':result['source_publication'],'audit_execution':result['audit_execution'],
        'controls':_record(run/'controls/controls-receipt.json'),'replay':_record(run/'replay/replay-receipt.json'),
        'owned_receipts':receipts,'review':_record(run/'review-decision.json'),
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
    _require(report.get('format')=='whole-source-reviewed-acceptance-v4' and
             report.get('status')=='PASS_NEW_SOURCE_CONDITIONAL_REFERENCE_QUALIFICATION' and
             report.get('problem_id')==pipeline['problem_id'] and
             report.get('implementation')==review['implementation'] and
             report.get('review')==_record(run/'review-decision.json') and
             report.get('production_admission') is False and report.get('RH_proved') is False,
             'completed assessment is not bound to this reviewed qualification')
    _require(all(report.get(key)==pipeline[key] for key in
                 ('source','audit','proposal','exact','source_publication','audit_execution')) and
             report.get('scalar_premises')==pipeline['premises'] and
             report.get('controls')==_record(run/'controls/controls-receipt.json') and
             report.get('replay')==_record(run/'replay/replay-receipt.json') and
             report.get('owned_receipts')==_verify_receipts(run,code_root=root),
             'completed assessment scientific evidence changed')
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
        return verify_inventory(run)
    _require(assessment.is_file(),'published assessment missing')
    _check_sealed_output(run.parent)
    with _slice_writer(run,resume=True):
        _check_sealed_output(run.parent)
        try:
            (run/'retained-manifest.json').lstat()
        except FileNotFoundError:
            expected = _completed_assessment(run,assessment.parent,root)
            _require(_json(_bytes(assessment))==expected,'published assessment differs from owned result')
        else:
            return verify_inventory(run)
        return _seal(run)


def accept(run_dir,output_dir,*,code_root=ROOT):
    root,run,output = Path(code_root).resolve(),Path(run_dir).resolve(),Path(output_dir).resolve()
    _check_sealed_output(run.parent)
    _check_review_output(run,output,root)
    with _slice_writer(run,resume=True):
        return _accept_held(run,output,code_root=root)


def _accept_held(run_dir,output_dir,*,code_root=ROOT):
    from scripts.whole_source.pipeline import _bind as bind_source
    root,run,output = Path(code_root).resolve(),Path(run_dir).resolve(),Path(output_dir).resolve()
    result = _json(_bytes(run/'pipeline-result.json'))
    problem,_,bound = bind_source(Path(result['problem']['directory'])/result['problem']['artifact']['path'],
        Path(result['source_execution']['directory'])/result['source_execution']['artifact']['path'],root)
    _require((run/'review-decision.json').is_file(),'independent execution review is required before release')
    review = _validate_review(run,root)
    if (run/'retained-manifest.json').exists():
        verify_inventory(run)
    _check_review_output(run,output,root)
    output.mkdir(parents=True,exist_ok=False)
    base_spec,base_plan = bound['analytic']
    refs = {r.path:r for r in base_spec.code_refs}
    for name in CODE:
        refs[name] = _ref(root,name)
    _,capture,locations = _implementation_code(root)
    for name in (capture['path'],*(stored for stored,_ in locations.values())):
        refs[name] = _ref(root,name)
    for path in (run/'pipeline-result.json',run/'review-decision.json',
                 run/'controls/controls-receipt.json',run/'replay/replay-receipt.json',
                 Path(review['implementation']['directory'])/review['implementation']['artifact']['path']):
        name = path.relative_to(root).as_posix()
        refs[name] = _ref(root,name)
    spec = CollectionSpec.create(problem,role='exact',quantities=base_spec.quantities,
        partition=base_spec.partition,backend='python-flint-exact',backend_version=base_spec.backend_version,
        native_threads=1,code_refs=tuple(refs[name] for name in sorted(refs)),bounds=base_spec.bounds,code_root=root)
    provenance = _json(_bytes(root/base_plan.provenance.path))
    provenance['files'] = [asdict(ref) for ref in spec.code_refs]
    _write(output/'assessment-origin.json',canonical_bytes(provenance))
    plan = replace(base_plan,role='exact',collection_sha256=spec.collection_id,
        resource_policy=None,workers=1,
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
    with CollectionLock.acquire(output/'collection',spec) as lock:
        with WorkloadExecution(lock,spec,plan,code_root=root) as execution:
            execution.run_stage('reviewed-consequence',[_request(run=str(run))])
    report = _completed_assessment(run,output,root)
    _write(output/'assessment.json',canonical_bytes(report))
    if not (run/'retained-manifest.json').exists():
        _seal(run)
    return report


def run(problem_path,execution_path,output_dir,*,code_root=ROOT):
    root,output = Path(code_root).resolve(),Path(output_dir).resolve()
    problem,config = _bind(problem_path,execution_path,root)
    output.relative_to(root)
    output.parent.mkdir(parents=True,exist_ok=True)
    _require(shutil.disk_usage(output.parent).free>=config['minimum_free_bytes'],'insufficient full-path free disk allowance')
    started = time.monotonic_ns()
    with _slice_writer(output,resume=False):
        _write(output/'integration-execution.json',canonical_bytes(config))
        try:
            result = _execute(problem,config,output,root)
            from scripts.whole_source.controls import run_controls
            controls = run_controls(Path(result['problem']['directory'])/result['problem']['artifact']['path'],
                Path(result['source_execution']['directory'])/result['source_execution']['artifact']['path'],
                Path(result['source']['directory'])/result['source']['artifact']['path'],
                Path(result['audit']['directory'])/result['audit']['artifact']['path'],
                Path(result['proposal']['directory'])/result['proposal']['artifact']['path'],
                Path(result['exact']['directory'])/result['exact']['artifact']['path'],output/'controls',code_root=root)
            replay(output,output/'replay',code_root=root)
            ready = {'status':'COMPLETE_EVIDENCE_PENDING_INDEPENDENT_REVIEW',
                'pipeline_result':_record(output/'pipeline-result.json'),
                'controls':_record(output/'controls/controls-receipt.json'),
                'replay':_record(output/'replay/replay-receipt.json'),'production_admission':False}
            _write(output/'elapsed.json',canonical_bytes({'wall_nanoseconds':time.monotonic_ns()-started,
                'scope':'SOURCE_AUDIT_PROPOSAL_EXACT_CONTROLS_AND_REPLAY_BEFORE_REVIEW'}))
            _write(output/'ready-for-review.json',canonical_bytes(ready))
            return ready
        except BaseException as exc:
            _write(output/'failure.json',canonical_bytes({'status':'FAILED_NO_REFERENCE_ACCEPTANCE',
                'error_type':type(exc).__name__,'error':str(exc),'production_admission':False}))
            raise
