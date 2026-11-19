"""Full-domain consequence checks, independent of successful driver metadata."""
from fractions import Fraction as Q
from types import SimpleNamespace
import pytest
from scripts.whole_source.contract import ContractError, canonical_bytes
from scripts.whole_source.retention import reviewed_consequence, _seal, verify_inventory
import json
from pathlib import Path
from scripts.whole_source import retention


@pytest.fixture(scope='module', autouse=True)
def _synthetic_supervisor(tmp_path_factory):
    """Test metadata authority only; no real guardian or approval is claimed."""
    from scripts.whole_source import supervision
    from tests.test_whole_source_phase_supervision import observer
    code = supervision._code(Path(__file__).resolve().parents[1])
    location = tmp_path_factory.mktemp('synthetic-observer')
    binding, _ = observer(location,'1'*32,code)
    current = {'code':code,'operation_id':'a'*64,'invocation_id':'f'*32,
               'root':str(location),'observation_bytes':16*1024*1024}
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(supervision, 'require_current', lambda: current)
        yield binding


def rational(value):
    value = Q(value)
    return {'numerator':hex(value.numerator),'denominator':hex(value.denominator)}


def problem():
    return SimpleNamespace(eta=Q(3,4),m=Q(2,5),b_K=Q(1,7),delta=Q(1,11),numerical_goal=Q(1,1<<80))


def blocks():
    result = []
    for p in (0,1):
        margin,tau = Q(p+1,3),Q(413+p,5)
        result.append({'dimension':413,'parity':p,'scope':'SOURCE_CONDITIONAL',
            'row_margins':[rational(margin+Q(i,1000)) for i in range(413)],
            'margin':rational(margin),'tau':rational(tau),'width':rational(0),
            'goal':rational(problem().numerical_goal),'direction_upper':rational(1),
            'direction_mass':rational(2),'direction_index':0,
            'modular':{'global_input_entries':413**2,'prime':65521,'residue':1,'nonsingular':True}})
    return result


def test_full_norm_uses_worse_parity_and_complete_physical_trace():
    p = problem()
    rows = blocks()
    sigma = min(Q(1,3)/Q(413,5),Q(2,3)/Q(414,5))
    expected = min(sigma/(1+2*(Q(1,7)+Q(1,11))**2/(Q(3,4)**2*Q(2,5)**2)),Q(3,4)*Q(2,5)/2)
    result = reviewed_consequence(p,rows)
    assert result['sigma']==sigma
    assert result['gamma']==expected
    rows[0]['tau'] = rational(1000)
    assert reviewed_consequence(p,rows)['gamma']<expected


@pytest.mark.parametrize('change',['missing-row','missing-parity','local-determinant','zero-residue','reference-scope','last-row'])
def test_incomplete_global_evidence_cannot_release_norm(change):
    rows = blocks()
    if change=='missing-row': rows[1]['row_margins'].pop()
    elif change=='missing-parity': rows.pop()
    elif change=='local-determinant': rows[1]['modular']['global_input_entries']=32**2
    elif change=='zero-residue': rows[1]['modular']['residue']=0
    elif change=='reference-scope': rows[1]['scope']='REFERENCE_ARITHMETIC_ONLY'
    else: rows[1]['row_margins'][-1]=rational(-1)
    with pytest.raises(ContractError):
        reviewed_consequence(problem(),rows)


def test_width_boundary_is_inclusive_but_over_goal_prevents_release():
    rows = blocks()
    rows[1]['width'] = rows[1]['goal']
    assert reviewed_consequence(problem(),rows)['positive_paid_lower']
    rows[1]['width'] = rational(problem().numerical_goal+Q(1,1<<256))
    with pytest.raises(ContractError,match='source-norm'):
        reviewed_consequence(problem(),rows)


def test_retained_endpoint_change_invalidates_the_sealed_scientific_inventory(tmp_path):
    source = tmp_path/'source.json'
    source.write_bytes(canonical_bytes({'endpoint_pairs':[[0,0,'0x1','0x2']]}))
    assert _seal(tmp_path)['status']=='PASS_RETAINED_INVENTORY'
    source.write_bytes(canonical_bytes({'endpoint_pairs':[[0,0,'0x1','0x3']]}))
    with pytest.raises(ContractError,match='changed'):
        verify_inventory(tmp_path)


@pytest.fixture
def proposal_gate(tmp_path, monkeypatch):
    """Synthetic upstream metadata stops at the real scalar-premise rejection."""
    # This fixture isolates the mathematical conjunction, not operational authority.
    monkeypatch.setattr(retention, '_selected_supervision', lambda *args, **kwargs: [])
    root = Path(__file__).resolve().parents[1]
    bound = retention.bind_problem('retained-t081', root=root)
    pid = retention.problem_id(bound)

    def store(name, value):
        path = tmp_path/(name+'.json')
        path.write_bytes(canonical_bytes(value))
        return retention._record(path)

    def assess(change=None):
        source = store('source', {'full_mathematical_source': True, 'control': False})
        proposal = {
            'status': 'NONPROOF_ONLY', 'scope': 'NONPROOF_PROPOSAL_ONLY',
            'source': source['artifact'],
        }
        if change and change[0] == 'proposal':
            _, field, value = change
            if value == 'ABSENT':
                proposal.pop(field)
            else:
                proposal[field] = value
        proposed = store('proposal', proposal)
        exact = {
            'source': {'manifest': source['artifact']},
            'proposal': {'artifact': proposed['artifact']},
            'proof_scope': 'SOURCE_CONDITIONAL',
            'status': 'PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL',
        }
        if change and change[0] == 'exact':
            _, field, value = change
            exact[field] = value
        result = {
            'problem_id': pid, 'fresh_proposal': change != ('fresh',),
            'source': source, 'proposal': proposed, 'exact': store('exact', exact),
            'audit': store('audit', {
                'status': 'VERIFIED_ALL_DECLARED_SOURCE_ENTRIES',
                'entries_checked': retention.FULL_ENTRIES,
                'source_manifest': source['artifact'],
                'full_mathematical_source': True, 'problem_id': pid,
            }),
            'premises': store('premises', {'status': 'INTENTIONAL_TEST_STOP', 'outputs': []}),
        }
        store('pipeline-result', result)
        return retention._assess_local(tmp_path, root)

    return assess


def test_valid_nonproof_proposal_advances_to_scalar_premise_gate(proposal_gate):
    with pytest.raises(ContractError, match='fresh scalar-premise checks missing'):
        proposal_gate()


@pytest.mark.parametrize('change', [
    ('proposal', 'status', 'WRONG_STATUS'),
    ('proposal', 'status', 'NONPROOF_PROPOSAL_ONLY'),
    ('proposal', 'status', 'ABSENT'),
    ('proposal', 'status', None),
    ('proposal', 'scope', 'NONPROOF_ONLY'),
    ('proposal', 'scope', 'WRONG_SCOPE'),
    ('proposal', 'scope', 'ABSENT'),
    ('proposal', 'scope', None),
    ('fresh',),
    ('proposal', 'source', {'rebound': True}),
    ('exact', 'source', {'manifest': {'rebound': True}}),
    ('exact', 'proposal', {'artifact': {'rebound': True}}),
    ('exact', 'proof_scope', 'CONTROL_ONLY'),
    ('exact', 'status', 'UNRESOLVED'),
])
def test_invalid_proposal_or_exact_binding_cannot_advance(proposal_gate, change):
    with pytest.raises(ContractError, match='wrong source/proposal/exact binding'):
        proposal_gate(change)


@pytest.fixture
def review_gate(tmp_path, monkeypatch):
    """Synthetic science metadata reaches the real review gate, not acceptance."""
    monkeypatch.setattr(retention, '_selected_supervision', lambda *args, **kwargs: [])
    from scripts.whole_source.controls import SOURCE_CASES, EXACT_CASES
    root = Path(__file__).resolve().parents[1]
    pid = retention.problem_id(retention.bind_problem('retained-t081', root=root))

    def store(name, value):
        path = tmp_path/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical_bytes(value))
        return retention._record(path)

    source = store('source.json', {'full_mathematical_source': True, 'control': False})
    proposed = store('proposal.json', {'status': 'NONPROOF_ONLY',
        'scope': 'NONPROOF_PROPOSAL_ONLY', 'source': source['artifact']})
    result = {'source': source, 'proposal': proposed, 'fresh_proposal': True, 'problem_id': pid,
        'audit': store('audit.json', {'status': 'VERIFIED_ALL_DECLARED_SOURCE_ENTRIES',
            'entries_checked': retention.FULL_ENTRIES, 'source_manifest': source['artifact'],
            'full_mathematical_source': True, 'problem_id': pid}),
        'exact': store('exact.json', {'source': {'manifest': source['artifact']},
            'proposal': {'artifact': proposed['artifact']}, 'proof_scope': 'SOURCE_CONDITIONAL',
            'status': 'PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL'}),
        'premises': store('premises.json', {'status': 'VERIFIED_FRESH_SCALAR_PREMISES', 'outputs': [{}]*8})}
    pipeline = store('pipeline-result.json', result)
    cases = []
    for name, _ in (*SOURCE_CASES, *EXACT_CASES):
        row = {'case': name, 'passed': True}
        cases.append(row)
        store('controls/'+name+'/case-result.json', row)
    controls = store('controls/controls-receipt.json', {
        'status': 'PASS_REQUIRED_MATHEMATICAL_CONTROLS', 'cases': cases,
        **{key: result[key] for key in ('source', 'audit', 'proposal', 'exact')}})
    replayed = store('replay/replay-receipt.json', {
        'status': 'PASS_COMPLETE_SCIENTIFIC_REPLAY_COMPARISON',
        'expected_new_outputs_installed': False, 'original_run': {'intentional_stop': True}})
    review = {'format': 'whole-source-independent-review-v1',
        'disposition': 'NO_UNRESOLVED_CORRECTNESS_FINDINGS', 'pipeline_result': pipeline,
        'controls': controls, 'replay': replayed, 'code': []}
    return tmp_path, root, review, store


def test_empty_legacy_review_cannot_pass_actual_final_gate(review_gate):
    run, root, review, store = review_gate
    store('review-decision.json', review)
    with pytest.raises(ContractError, match='independent review'):
        retention._assess_local(run, root)


@pytest.fixture(scope='module')
def _complete_review_template(_synthetic_supervisor):
    """Complete review metadata only; never a mathematical qualification."""
    from scripts.whole_source import admission
    from dataclasses import asdict, replace
    import hashlib
    import sys
    from scripts.whole_source.contract import ArtifactRef
    from scripts.whole_source.execution import BUNDLE, _HELPERS, _RUNTIME
    from scripts.whole_source.controls import SOURCE_CASES, EXACT_CASES
    from tests.test_whole_source_execution import case
    root = Path(__file__).resolve().parents[1]
    from tempfile import TemporaryDirectory
    directory_manager = TemporaryDirectory(prefix='phase-review-', dir=root/'.pytest_cache')
    tmp_path = Path(directory_manager.name)
    bound = retention.bind_problem('retained-t081', root=root)
    pid = retention.problem_id(bound)
    captured, spec, base_plan = case(tmp_path, bound)
    run = tmp_path/'run'
    run.mkdir()

    def store(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical_bytes(value))
        return retention._record(path)

    from scripts.whole_source.coordinator import PhaseJournal, SCIENCE_PHASES, operation_inputs
    integration = retention.prepare_inputs(bound, tmp_path/'integration-inputs',
        origin_git_commit='1'*40, origin_git_dirty=True, code_root=root)
    config = json.loads(integration['execution'].read_bytes())
    phase_roots = {}

    def science(directory, fresh, installed_proposal=None, *, code_root=root):
        directory.mkdir(parents=True, exist_ok=True)
        start = retention._capture_implementation(bound, directory, root, 'science')
        store(directory/'integration-execution.json', config)
        journal = PhaseJournal(directory, {
            'problem_id': pid, 'configuration': config, 'implementation': start,
            'proposal_input': installed_proposal},code_root=code_root)
        prior, roots = {}, {}
        for phase in SCIENCE_PHASES:
            target, _ = journal.begin(phase, prior)
            admission.bind_phase_attempt({'format': admission.FORMAT, 'policy': admission.POLICY,
                'phase':phase,'inputs':operation_inputs(directory,prior,code_root=code_root),
                'supervision':_synthetic_supervisor},
                target, directory)
            roots[phase] = target
            if phase == 'prepare':
                outputs = {
                    'problem': store(target/'source-inputs/problem.json', {'synthetic': True}),
                    'source_execution': store(target/'source-inputs/execution.json', {'synthetic': True}),
                    'premises': store(target/'premises/premises-receipt.json', {
                        'status': 'VERIFIED_FRESH_SCALAR_PREMISES', 'outputs': [{}]*8})}
            elif phase == 'source':
                source = store(target/'producer/source-manifest.json',
                    {'full_mathematical_source': True, 'control': False})
                outputs = {'source': source, 'source_publication': store(target/'producer/source-execution.json', {
                    'format': 'whole-source-publication-execution-v2',
                    'source_manifest': source['artifact'], 'provenance': {'kind': 'OWNED_SOURCE'}})}
            elif phase == 'audit':
                audit = store(target/'analytical-receipt.json', {
                    'status': 'VERIFIED_ALL_DECLARED_SOURCE_ENTRIES', 'entries_checked': retention.FULL_ENTRIES,
                    'source_manifest': source['artifact'], 'full_mathematical_source': True, 'problem_id': pid})
                outputs = {'audit': audit, 'audit_execution': store(target/'audit-execution.json', {
                    'format': 'whole-source-audit-execution-v1', 'audit': audit['artifact'],
                    'source': {'execution': prior['source']['source_publication']['artifact']}})}
            elif phase == 'proposal':
                if installed_proposal is None:
                    proposal = store(target/'work/proposal.json', {'status': 'NONPROOF_ONLY',
                        'scope': 'NONPROOF_PROPOSAL_ONLY', 'source': source['artifact']})
                else:
                    proposal = installed_proposal
                    store(target/'installed-proposal.json', {'proposal': proposal})
                outputs = {'proposal': proposal}
            elif phase == 'exact-inputs':
                outputs = {key: store(target/name, {'synthetic': True}) for key, name in
                    (('problem', 'problem.json'), ('execution', 'execution.json'), ('operands', 'operands.json'))}
            else:
                outputs = {'exact': store(target/'report.json', {
                    'source': {'manifest': source['artifact']}, 'proposal': {'artifact': proposal['artifact']},
                    'proof_scope': 'SOURCE_CONDITIONAL', 'status': 'PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL',
                    'assessment': {'gamma': {'fixture': 'NONPROOF_ONLY'}}})}
            journal.complete(phase, outputs)
            prior[phase] = outputs
        result = {'format': 'whole-source-pipeline-result-v3',
            'status': 'COMPLETE_FRESH_SOURCE_AUDIT_AND_EXACT', 'problem_id': pid,
            'fresh_proposal': fresh, 'implementation': start,
            'source': prior['source']['source'], 'proposal': prior['proposal']['proposal'],
            'audit': prior['audit']['audit'], 'exact': prior['exact']['exact'],
            'premises': prior['prepare']['premises'], 'problem': prior['prepare']['problem'],
            'source_execution': prior['prepare']['source_execution'],
            'source_publication': prior['source']['source_publication'],
            'audit_execution': prior['audit']['audit_execution'],
            'phase_chain': [journal.completed[name]['record'] for name in SCIENCE_PHASES],
            'gamma': {'fixture': 'NONPROOF_ONLY'},
            'production_admission': False}
        record = store(directory/'pipeline-result.json', result)
        retention._complete_implementation(directory, root, {'pipeline': record})
        phase_roots[directory] = roots
        return result, record, journal, prior

    result, pipeline, journal, prior = science(run, True)
    controls_dir, _ = journal.begin('controls', prior)
    admission.bind_phase_attempt({'format': admission.FORMAT, 'policy': admission.POLICY,
        'phase':'controls','inputs':operation_inputs(run,prior,code_root=root),
        'supervision':_synthetic_supervisor},controls_dir,run)
    controls_dir.mkdir(parents=True)
    retention._capture_implementation(bound, controls_dir, root, 'controls')
    cases = []
    for name, _ in (*SOURCE_CASES, *EXACT_CASES):
        row = {'case': name, 'passed': True}
        cases.append(row)
        store(controls_dir/name/'case-result.json', row)
    controls = store(controls_dir/'controls-receipt.json', {
        'status': 'PASS_REQUIRED_MATHEMATICAL_CONTROLS', 'cases': cases,
        **{key: result[key] for key in ('source', 'audit', 'proposal', 'exact')}})
    retention._complete_implementation(controls_dir, root, {'controls': controls})
    journal.complete('controls', {'controls': controls})
    prior['controls'] = {'controls': controls}
    replay_dir, _ = journal.begin('replay', prior)
    admission.bind_phase_attempt({'format': admission.FORMAT, 'policy': admission.POLICY,
        'phase':'replay','inputs':operation_inputs(run,prior,code_root=root),
        'supervision':_synthetic_supervisor},replay_dir,run)
    replay_dir.mkdir(parents=True)
    retention._capture_implementation(bound, replay_dir, root, 'replay')
    capture_root = replay_dir/'captured-root'
    retention.capture_inputs(bound, capture_root, code_root=root)
    installed = store(capture_root/retention._REPLAY_PROPOSAL,retention._document(result['proposal']))
    child_dir = capture_root/'child'
    _, child, _, _ = science(child_dir,False,installed,code_root=capture_root)
    replayed = store(replay_dir/'replay-receipt.json', {
        'format': retention._FROZEN_REPLAY_FORMAT,
        'status': 'PASS_COMPLETE_SCIENTIFIC_REPLAY_COMPARISON',
        'expected_new_outputs_installed': False, 'replayed_run': child,
        'original_run': pipeline, 'capture': retention._record(capture_root/'capture-manifest.json')})
    retention._complete_implementation(replay_dir, root, {'replay': replayed})
    journal.complete('replay', {'replay': replayed})

    def stage(directory, role, function, program):
        """Synthetic raw receipts exercise identity validation, not execution."""
        attempt = directory/'attempts/fixture'
        runtime = attempt/'runtime'
        for ref, raw in spec._snapshots:
            if ref.path == base_plan.task_program.path:
                continue
            path = runtime/ref.path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        for name in (*_HELPERS,):
            path = runtime/BUNDLE/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((captured/BUNDLE/name).read_bytes())
        path = runtime/program
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((root/program).read_bytes())
        refs = [asdict(retention._ref(root, name)) for name in sorted(set((*_RUNTIME, program)))]
        origin = store(attempt/'code-origin.json', {
            'format': 'whole-source-code-origin-v1', 'files': refs})
        policy = ({'scope': 'NONPROOF_PROPOSAL_ONLY', 'precision_bits': 1024} if role == 'proposal'
                  else {'scope': 'EXACT_ASSESSMENT_ONLY', 'backend': 'python-flint-exact'} if role == 'exact'
                  else {'scope': 'SOURCE_EXPRESSIONS_ONLY'})
        plan = replace(base_plan, role=role, task_program=ArtifactRef(**next(
            ref for ref in refs if ref['path'] == program)), task_function=function, **policy)
        task = {'task_id': '1'*64, 'scalar_root': 'fixture-scalar'}
        spool = attempt/'fixture-tasks.jsonl'
        spool.write_bytes(canonical_bytes(task))
        result_dir = attempt/'fixture-results'
        payload = store(result_dir/('1'*64+'.json'), {
            'execution_id': plan.execution_id, 'attempt_id': attempt.name,
            'collection_id': plan.collection_sha256, 'problem_id': plan.problem_sha256,
            'scope': plan.scope, 'task_id': task['task_id'], 'synthetic': True})
        inventory = result_dir/'completed.jsonl'
        inventory.write_bytes(canonical_bytes(payload['artifact']))
        store(result_dir/'complete.json', {'execution_id': plan.execution_id, 'task_count': 1,
            'inventory_sha256': hashlib.sha256(inventory.read_bytes()).hexdigest()})
        budget = store(attempt/'execution-budget.json', {'synthetic': True})
        stage_ref = store(attempt/'fixture-stage.json', {
            'format': 'whole-source-task-stage-v2', 'plan': plan.to_dict(),
            'code_origin': origin['artifact'], 'attempt_id': attempt.name,
            'python_version': sys.version,
            'task_file': str(spool), 'task_sha256': hashlib.sha256(spool.read_bytes()).hexdigest(),
            'task_count': 1, 'result_dir': str(result_dir), 'profile': bound.profile,
            'collection': {'code_refs': refs}})
        execution = retention._ref(runtime, 'scripts/whole_source/execution.py')
        profile = store(attempt/'profile.json', {
            'exit_code': 0, 'error': None, 'program_sha256': execution.sha256})
        logs = {}
        for name in ('stdout', 'stderr'):
            path = attempt/(name+'.txt')
            path.write_bytes(b'')
            logs[name] = asdict(retention._ref(attempt, path.name))
        argv = ['fixture', '--stage', str(attempt/'fixture-stage.json'),
            '--stage-sha256', stage_ref['artifact']['sha256'],
            '--program', str(runtime/execution.path), '--config', str(attempt/'execution-budget.json'),
            '--profile', str(attempt/'profile.json')]
        store(attempt/'fixture/receipt.json', {
            'format': 't081-owned-stage-receipt-v1', 'stage': 'fixture', 'argv': argv,
            'exit_code': 0, 'error': None, 'worker_cleanup_verified': True,
            'last_metrics': {'active_process_count': 0}, 'program_sha256': execution.sha256,
            'config_sha256': budget['artifact']['sha256'], 'logs': logs})
        return attempt

    original_roots, child_roots = phase_roots[run], phase_roots[child_dir]
    stage_rows = [
        (original_roots['prepare']/'premises', 'analytic', 'evaluate_premise', 'retention'),
        (original_roots['source'], 'producer', 'evaluate_source', 'producer'),
        (original_roots['audit'], 'analytic', 'evaluate_source', 'analytic'),
        (original_roots['proposal']/'work', 'proposal', 'evaluate_proposal', 'proposal'),
        (original_roots['exact'], 'exact', 'evaluate_exact', 'exact'),
        (controls_dir/'native', 'analytic', 'evaluate_control', 'controls'),
        (controls_dir/'exact', 'exact', 'evaluate_exact', 'exact'),
        (child_roots['source'], 'producer', 'evaluate_source', 'producer'),
        (child_roots['audit'], 'analytic', 'evaluate_source', 'analytic'),
        (child_roots['prepare']/'premises', 'analytic', 'evaluate_premise', 'retention'),
        (child_roots['exact'], 'exact', 'evaluate_exact', 'exact')]
    attempts = [stage(folder, role, function, 'scripts/whole_source/'+program+'.py')
                for folder, role, function, program in stage_rows]
    manifest = retention._review_manifest(run, root)
    implementation = store(tmp_path/'implementation-manifest.json', manifest)
    review = {'format': 'whole-source-independent-review-v4',
        'disposition': 'NO_UNRESOLVED_CORRECTNESS_FINDINGS',
        **{key: manifest[key] for key in ('code', 'pipeline_result', 'controls', 'replay')},
        'implementation': implementation}
    store(run/'review-decision.json', review)
    try:
        yield run, root, review, store, attempts
    finally:
        directory_manager.cleanup()


@pytest.fixture
def complete_review(_complete_review_template, monkeypatch):
    """Restore every mutable fixture artifact after each isolated case."""
    from contextlib import nullcontext
    from scripts.whole_source import admission
    monkeypatch.setattr(admission, 'admitted_problem',
                        lambda root: retention.bind_problem('retained-t081', root=root))
    monkeypatch.setattr(admission, 'admitted_phase', lambda *args, **kwargs: nullcontext({}))
    run, root, review, store, attempts = _complete_review_template
    paths = [
        run/'review-decision.json', Path(review['implementation']['directory'])/
            review['implementation']['artifact']['path'],
        run/'implementation/complete.json', attempts[0]/'code-origin.json',
        attempts[0]/'runtime/scripts/whole_source/execution.py',
        attempts[0]/'runtime/scripts/run_observability.py',
        attempts[0]/'fixture-stage.json', attempts[0]/'fixture/receipt.json',
    ]
    saved = {path: path.read_bytes() for path in paths}
    extra = attempts[0]/'runtime/unbound.py'
    try:
        yield run, root, json.loads(canonical_bytes(review)), store, attempts
    finally:
        for path, raw in saved.items():
            path.write_bytes(raw)
        if extra.exists():
            extra.unlink()


def test_complete_review_advances_through_actual_gate_without_accepting_science(complete_review):
    run, root, _, _, _ = complete_review
    with pytest.raises((ContractError, KeyError)):
        retention._assess_local(run, root)


@pytest.mark.parametrize('change', [
    'empty', 'subset', 'duplicate', 'unrelated', 'assessor', 'runtime', 'inherited',
    'wrong-hash', 'wrong-size', 'old-contract', 'wrong-disposition',
])
def test_incomplete_or_changed_review_cannot_release_execution(complete_review, change):
    run, root, review, store, _ = complete_review
    if change == 'empty':
        review['code'] = []
    elif change == 'subset':
        review['code'] = review['code'][:1]
    elif change == 'duplicate':
        review['code'].append(review['code'][0])
    elif change == 'unrelated':
        review['code'].append({'kind': 'current', 'artifact': {
            'path': 'uv.lock', 'sha256': '0'*64, 'size': 1}})
    elif change == 'inherited':
        review['code'] = [row for row in review['code'] if row['kind'] != 'inherited']
    elif change in ('assessor', 'runtime'):
        omitted = ('scripts/whole_source/retention.py' if change == 'assessor'
                   else 'scripts/run_observability.py')
        review['code'] = [row for row in review['code'] if row['artifact']['path'] != omitted]
    elif change == 'wrong-hash':
        review['code'][0]['artifact']['sha256'] = '0'*64
    elif change == 'wrong-size':
        review['code'][0]['artifact']['size'] += 1
    elif change == 'old-contract':
        review['format'] = 'whole-source-independent-review-v1'
    else:
        review['disposition'] = 'PENDING'
    store(run/'review-decision.json', review)
    with pytest.raises(ContractError, match='review'):
        retention._assess_local(run, root)


@pytest.mark.parametrize('change', ['origin', 'runtime', 'extra-runtime-file', 'coordinator', 'manifest', 'missing-stage'])
def test_changed_execution_evidence_cannot_satisfy_review(complete_review, change):
    run, root, review, store, attempts = complete_review
    if change == 'origin':
        (attempts[0]/'code-origin.json').write_bytes(b'{}\n')
    elif change == 'runtime':
        (attempts[0]/'runtime/scripts/whole_source/execution.py').write_bytes(b'changed\n')
    elif change == 'extra-runtime-file':
        (attempts[0]/'runtime/unbound.py').write_bytes(b'pass\n')
    elif change == 'coordinator':
        (run/'implementation/complete.json').unlink()
    elif change == 'manifest':
        manifest = retention._document(review['implementation'])
        manifest['code'].pop()
        review['implementation'] = store(Path(review['implementation']['directory'])/
            review['implementation']['artifact']['path'], manifest)
        store(run/'review-decision.json', review)
    else:
        (attempts[0]/'fixture/receipt.json').unlink()
    with pytest.raises((ContractError, OSError)):
        retention._validate_review(run, root)


def test_review_preparation_refuses_output_inside_run_before_writing(tmp_path):
    run = tmp_path/'run'
    run.mkdir()
    with pytest.raises(ContractError, match='outside'):
        retention.prepare_review(run, run/'review', code_root=tmp_path)
    assert not (run/'review').exists()


def test_current_review_cannot_cover_self_consistent_different_executed_revision(complete_review):
    run, root, _, store, attempts = complete_review
    attempt = attempts[0]
    path = attempt/'runtime/scripts/run_observability.py'
    path.write_bytes(path.read_bytes()+b'\n# Different executed revision.\n')
    changed = retention._ref(attempt/'runtime', 'scripts/run_observability.py')
    origin = json.loads((attempt/'code-origin.json').read_bytes())
    for row in origin['files']:
        if row['path'] == changed.path:
            row.update(sha256=changed.sha256, size=changed.size)
    new_origin = store(attempt/'code-origin.json', origin)
    stage = json.loads((attempt/'fixture-stage.json').read_bytes())
    stage['code_origin'] = new_origin['artifact']
    stage['collection']['code_refs'] = origin['files']
    stage_record = store(attempt/'fixture-stage.json', stage)
    receipt_path = attempt/'fixture/receipt.json'
    receipt = json.loads(receipt_path.read_bytes())
    receipt['argv'][receipt['argv'].index('--stage-sha256')+1] = stage_record['artifact']['sha256']
    store(receipt_path, receipt)
    with pytest.raises(ContractError, match='executed code differs'):
        retention._validate_review(run, root)


@pytest.mark.parametrize('kind', ['inherited', 'inherited-drift', 'reader-context', 'unclassified'])
def test_declared_input_roles_preserve_historical_bytes_without_hiding_code(complete_review, kind):
    from dataclasses import asdict
    run, root, _, store, attempts = complete_review
    code, _, locations = retention._implementation_code(root)
    attempt = attempts[3] if kind == 'reader-context' else attempts[0]
    inherited = next(row['artifact'] for row in code if row['kind'] == 'inherited')
    if kind.startswith('inherited'):
        logical = 'fixture-scalar/'+inherited['path']
        raw = locations[inherited['path']][1]
        if kind == 'inherited-drift':
            raw += b'\n# Different inherited implementation.\n'
    elif kind == 'reader-context':
        logical = 'fixture/source-context/scripts/whole_source/execution.py'
        raw = b'# Historical reader context, not current executable code.\n'
    else:
        logical = 'fixture-scalar/unclassified.py'
        raw = b'# Not in the declared executable closure.\n'
    target = attempt/'runtime'/logical
    paths = [attempt/'code-origin.json', attempt/'fixture-stage.json', attempt/'fixture/receipt.json']
    saved = {path: path.read_bytes() for path in paths}
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        origin = json.loads(saved[paths[0]])
        origin['files'].append(asdict(retention._ref(attempt/'runtime', logical)))
        origin['files'].sort(key=lambda row: row['path'])
        if kind == 'reader-context':
            origin['reader_contexts'] = ['fixture/source-context']
        origin_record = store(paths[0], origin)
        stage = json.loads(saved[paths[1]])
        stage['code_origin'] = origin_record['artifact']
        stage['collection']['code_refs'] = origin['files']
        stage_record = store(paths[1], stage)
        receipt = json.loads(saved[paths[2]])
        receipt['argv'][receipt['argv'].index('--stage-sha256')+1] = stage_record['artifact']['sha256']
        receipt_record = store(paths[2], receipt)
        if kind in ('inherited-drift', 'unclassified'):
            with pytest.raises(ContractError, match='executed code differs|unclassified'):
                retention._stage_implementation(receipt_record, code, locations)
        else:
            bound = retention._stage_implementation(receipt_record, code, locations)
            assert bound['origin'] == origin_record
    finally:
        for path, saved_raw in saved.items():
            path.write_bytes(saved_raw)
        if target.exists():
            target.unlink()


def test_review_preparation_refuses_legacy_evidence_without_writing(complete_review):
    from tempfile import TemporaryDirectory
    run, root, _, _, _ = complete_review
    with TemporaryDirectory(prefix='review-preparation-', dir=root/'.pytest_cache') as temporary:
        output = Path(temporary)/'prepared'
        with pytest.raises(ContractError, match='requires a portable scientific run'):
            retention.prepare_review(run, output, code_root=root)
        assert not output.exists()


def test_review_preparation_uses_fixed_role_and_never_writes_approval(tmp_path,monkeypatch):
    from contextlib import nullcontext
    from scripts.whole_source import admission,storage,supervision
    run,output = tmp_path/'synthetic-run',tmp_path/'private-review-placement'
    run.mkdir()
    (run/'.slice.lock').touch()
    manifest = {'format':'whole-source-review-manifest-v6','scope':'TEST_ONLY_NO_MATHEMATICAL_AUTHORITY'}
    monkeypatch.setattr(supervision,'require_current',lambda:None)
    monkeypatch.setattr(admission,'admitted_problem',lambda root:None)
    monkeypatch.setattr(admission,'admitted_phase',lambda *args,**kwargs:nullcontext())
    monkeypatch.setattr(retention,'_review_manifest',lambda run,root:manifest)
    monkeypatch.setattr(storage,'reserve_destination',lambda run,path:path.mkdir())
    result = retention.prepare_review(run,output,code_root=tmp_path)
    assert result['status']=='COMPLETE_IMPLEMENTATION_EVIDENCE_PENDING_INDEPENDENT_REVIEW'
    assert result['implementation']=={'role':'review-implementation',
        'artifact':retention._record(output/'implementation-manifest.json')['artifact']}
    assert b'private-review-placement' not in canonical_bytes(result)
    assert (output/'implementation-manifest.json').read_bytes()==canonical_bytes(manifest)
    assert not (output/'review-decision.json').exists()


@pytest.mark.parametrize('key', ['source_publication', 'audit_execution'])
@pytest.mark.parametrize('change', ['missing', 'changed'])
def test_review_binds_separate_publication_execution_records(complete_review, key, change):
    run, root, _, _, _ = complete_review
    result = json.loads((run/'pipeline-result.json').read_bytes())
    record = result[key]
    path = Path(record['directory'])/record['artifact']['path']
    raw = path.read_bytes()
    try:
        if change == 'missing':
            path.unlink()
        else:
            path.write_bytes(b'{}\n')
        with pytest.raises((ContractError, OSError)):
            retention._validate_review(run, root)
    finally:
        path.write_bytes(raw)


def test_assessment_task_binds_science_bytes_without_locator(tmp_path):
    import hashlib
    from scripts.whole_source.supervision import _wire
    run = tmp_path/'runs/science'
    observer = run.with_name(run.name+'.lifecycle')
    observer.mkdir(parents=True)
    duplicate = tmp_path/'other/science'
    for directory in (run, duplicate):
        directory.mkdir(parents=True)
        (directory/'pipeline-result.json').write_bytes(b'{}\n')
        (directory/'review-decision.json').write_bytes(b'{"TEST_ONLY":true}\n')
    identity = hashlib.sha256(_wire({'operation': str(run), 'code_root': str(tmp_path)})).hexdigest()
    lease = {'root': str(observer), 'operation_id': identity}
    task = retention._assessment_request(run)
    assert task['run'] == 'operation'
    assert task == retention._assessment_request(duplicate)
    assert retention._assessment_roots(lease) == (run, tmp_path)
    assert str(tmp_path).encode() not in canonical_bytes(task)
    (duplicate/'review-decision.json').write_bytes(b'{}\n')
    assert task['task_id'] != retention._assessment_request(duplicate)['task_id']
    with pytest.raises(ContractError, match='not bound to a live code root'):
        retention._assessment_roots({**lease, 'operation_id': '0'*64})
