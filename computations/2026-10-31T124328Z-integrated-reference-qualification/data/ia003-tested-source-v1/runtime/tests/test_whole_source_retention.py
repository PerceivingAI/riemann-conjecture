"""Full-domain consequence checks, independent of successful driver metadata."""
from fractions import Fraction as Q
from types import SimpleNamespace
import pytest
from scripts.whole_source.contract import ContractError, canonical_bytes
from scripts.whole_source.retention import reviewed_consequence, _seal, verify_inventory
import json
from pathlib import Path
from scripts.whole_source import retention


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
def proposal_gate(tmp_path):
    """Synthetic upstream metadata stops at the real scalar-premise rejection."""
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
def review_gate(tmp_path):
    """Synthetic science metadata reaches the real review gate, not acceptance."""
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
    with pytest.raises(ContractError, match='complete v2 contract'):
        retention._assess_local(run, root)


@pytest.fixture(scope='module')
def _complete_review_template(tmp_path_factory):
    """Complete review metadata only; never a mathematical qualification."""
    tmp_path = tmp_path_factory.mktemp('complete-review')
    from dataclasses import asdict, replace
    import hashlib
    import sys
    from scripts.whole_source.contract import ArtifactRef
    from scripts.whole_source.execution import BUNDLE, _HELPERS, _RUNTIME
    from scripts.whole_source.controls import SOURCE_CASES, EXACT_CASES
    from tests.test_whole_source_execution import case
    root = Path(__file__).resolve().parents[1]
    bound = retention.bind_problem('retained-t081', root=root)
    pid = retention.problem_id(bound)
    captured, spec, base_plan = case(tmp_path, bound)
    run = tmp_path/'run'
    run.mkdir()

    def store(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical_bytes(value))
        return retention._record(path)

    def science(directory, fresh):
        directory.mkdir(parents=True, exist_ok=True)
        start = retention._capture_implementation(bound, directory, root, 'science')
        source = store(directory/'source/producer/source-manifest.json',
                       {'full_mathematical_source': True, 'control': False})
        proposal = store(directory/'proposal/proposal.json', {'status': 'NONPROOF_ONLY',
            'scope': 'NONPROOF_PROPOSAL_ONLY', 'source': source['artifact']})
        result = {'problem_id': pid, 'fresh_proposal': fresh, 'implementation': start,
            'source': source, 'proposal': proposal,
            'audit': store(directory/'audit/analytical-receipt.json', {
                'status': 'VERIFIED_ALL_DECLARED_SOURCE_ENTRIES',
                'entries_checked': retention.FULL_ENTRIES, 'source_manifest': source['artifact'],
                'full_mathematical_source': True, 'problem_id': pid}),
            'exact': store(directory/'exact/report.json', {
                'source': {'manifest': source['artifact']}, 'proposal': {'artifact': proposal['artifact']},
                'proof_scope': 'SOURCE_CONDITIONAL', 'status': 'PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL'}),
            'premises': store(directory/'premises/premises-receipt.json', {
                'status': 'VERIFIED_FRESH_SCALAR_PREMISES', 'outputs': [{}]*8}),
            'problem': store(directory/'source-inputs/problem.json', {'synthetic': True}),
            'source_execution': store(directory/'source-inputs/execution.json', {'synthetic': True})}
        record = store(directory/'pipeline-result.json', result)
        retention._complete_implementation(directory, root, {'pipeline': record})
        return result, record

    result, pipeline = science(run, True)
    controls_dir = run/'controls'
    controls_dir.mkdir()
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
    replay_dir = run/'replay'
    replay_dir.mkdir()
    retention._capture_implementation(bound, replay_dir, root, 'replay')
    child_dir = replay_dir/'captured-root/child'
    _, child = science(child_dir, False)
    replayed = store(replay_dir/'replay-receipt.json', {
        'status': 'PASS_COMPLETE_SCIENTIFIC_REPLAY_COMPARISON',
        'expected_new_outputs_installed': False, 'replayed_run': child,
        'original_run': {'intentional_stop': True}})
    retention._complete_implementation(replay_dir, root, {'replay': replayed})

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

    stage_rows = [
        ('premises', 'analytic', 'evaluate_premise', 'retention'),
        ('source', 'producer', 'evaluate_source', 'producer'),
        ('audit', 'analytic', 'evaluate_source', 'analytic'),
        ('proposal', 'proposal', 'evaluate_proposal', 'proposal'),
        ('exact', 'exact', 'evaluate_exact', 'exact'),
        ('controls/native', 'analytic', 'evaluate_control', 'controls'),
        ('controls/exact', 'exact', 'evaluate_exact', 'exact'),
        ('replay/captured-root/child/source', 'producer', 'evaluate_source', 'producer'),
        ('replay/captured-root/child/audit', 'analytic', 'evaluate_source', 'analytic'),
        ('replay/captured-root/child/premises', 'analytic', 'evaluate_premise', 'retention'),
        ('replay/captured-root/child/exact', 'exact', 'evaluate_exact', 'exact')]
    attempts = [stage(run/folder, role, function, 'scripts/whole_source/'+program+'.py')
                for folder, role, function, program in stage_rows]
    manifest = retention._review_manifest(run, root)
    implementation = store(tmp_path/'implementation-manifest.json', manifest)
    review = {'format': 'whole-source-independent-review-v2',
        'disposition': 'NO_UNRESOLVED_CORRECTNESS_FINDINGS',
        **{key: manifest[key] for key in ('code', 'pipeline_result', 'controls', 'replay')},
        'implementation': implementation}
    store(run/'review-decision.json', review)
    return run, root, review, store, attempts


@pytest.fixture
def complete_review(_complete_review_template):
    """Restore every mutable fixture artifact after each isolated case."""
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
    with pytest.raises(ContractError, match='replay refers to another original run'):
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


def test_review_preparation_publishes_bound_evidence_without_approval(complete_review):
    from tempfile import TemporaryDirectory
    run, root, _, _, _ = complete_review
    with TemporaryDirectory(prefix='review-preparation-', dir=root/'.pytest_cache') as temporary:
        output = Path(temporary)/'prepared'
        result = retention.prepare_review(run, output, code_root=root)
        assert result['status'] == 'COMPLETE_IMPLEMENTATION_EVIDENCE_PENDING_INDEPENDENT_REVIEW'
        manifest = retention._document(result['implementation'])
        assert manifest == retention._review_manifest(run, root)
        assert not (output/'review-decision.json').exists()
