"""Owned-evidence recovery with synthetic stage fixtures, not mathematical acceptance."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import pytest

from scripts.whole_source import retention
from scripts.whole_source.contract import ContractError, ROOT, canonical_bytes
from scripts.whole_source.execution import ExecutionPlan
from tests.test_whole_source_retention import _complete_review_template


def store(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))
    return retention._record(path)


def files(directory):
    return {p.relative_to(directory).as_posix(): p.read_bytes()
            for p in directory.rglob('*') if p.is_file()}


@pytest.fixture(scope='module')
def recovery_template():
    with TemporaryDirectory(prefix='retention-recovery-', dir=ROOT/'.pytest_cache') as temp:
        factory = SimpleNamespace(mktemp=lambda name: Path(temp))
        yield _complete_review_template.__wrapped__(factory)


def assessment_fixture(template, output):
    """Construct raw, internally bound test-only stage evidence without executing science."""
    run, root, review, _, attempts = template
    attempt = output/'collection/attempts/fixture'
    shutil.copytree(attempts[0], attempt)
    stage_path = attempt/'fixture-stage.json'
    stage = json.loads(stage_path.read_bytes())
    plan = replace(ExecutionPlan.from_dict(stage['plan']), role='exact',
        task_function='evaluate_acceptance', backend='python-flint-exact', scope='EXACT_ASSESSMENT_ONLY')
    stage.update(plan=plan.to_dict(), task_file=str(attempt/'fixture-tasks.jsonl'),
                 result_dir=str(attempt/'fixture-results'))
    task = retention._request(run=str(run))
    store(Path(stage['task_file']), task)
    pipeline = json.loads((run/'pipeline-result.json').read_bytes())
    report = {'format':'whole-source-reviewed-acceptance-v4',
        'status':'PASS_NEW_SOURCE_CONDITIONAL_REFERENCE_QUALIFICATION',
        'problem_id':pipeline['problem_id'], 'implementation':review['implementation'],
        'review':retention._record(run/'review-decision.json'),
        'production_admission':False, 'RH_proved':False,
        'gamma':{'fixture':'METADATA_ONLY_NOT_A_MATHEMATICAL_RESULT'},
        **{key:pipeline[key] for key in ('source','audit','proposal','exact','source_publication','audit_execution')},
        'scalar_premises':pipeline['premises'],
        'controls':retention._record(run/'controls/controls-receipt.json'),
        'replay':retention._record(run/'replay/replay-receipt.json'),
        'owned_receipts':retention._verify_receipts(run, code_root=root)}
    payload = {'execution_id':plan.execution_id, 'attempt_id':attempt.name,
        'collection_id':plan.collection_sha256, 'problem_id':plan.problem_sha256,
        'scope':plan.scope, 'task_id':task['task_id'], 'result':report}
    result_path = Path(stage['result_dir'])/('1'*64+'.json')
    receipt_path = attempt/'fixture/receipt.json'
    receipt = json.loads(receipt_path.read_bytes())

    def bind():
        payload['execution_id'] = ExecutionPlan.from_dict(stage['plan']).execution_id
        result_ref = store(result_path, payload)['artifact']
        inventory = result_path.parent/'completed.jsonl'
        store(inventory, result_ref)
        store(result_path.parent/'complete.json', {'execution_id':payload['execution_id'],
            'task_count':1, 'inventory_sha256':hashlib.sha256(inventory.read_bytes()).hexdigest()})
        stage['task_sha256'] = hashlib.sha256(Path(stage['task_file']).read_bytes()).hexdigest()
        stage_ref = store(stage_path, stage)['artifact']
        receipt['argv'] = ['fixture', '--stage', str(stage_path), '--stage-sha256', stage_ref['sha256'],
            '--program', str(attempt/'runtime/scripts/whole_source/execution.py'),
            '--config', str(attempt/'execution-budget.json'), '--profile', str(attempt/'profile.json')]
        store(receipt_path, receipt)

    bind()
    expected = retention._completed_assessment(run, output, root)
    assessment = output/'assessment.json'
    store(assessment, expected)
    return SimpleNamespace(run=run, root=root, output=output, assessment=assessment,
        attempt=attempt, stage=stage, task=task, payload=payload, receipt=receipt, bind=bind,
        receipt_path=receipt_path, result_path=result_path)


@pytest.fixture
def recovery(recovery_template):
    run, root, _, _, _ = recovery_template
    (run/'.slice.lock').touch(exist_ok=True)
    protected = [run/'review-decision.json', run/'pipeline-result.json',
                 run/'source/producer/source-manifest.json']
    saved = {p:p.read_bytes() for p in protected}
    with TemporaryDirectory(prefix='assessment-', dir=root/'.pytest_cache') as temp:
        case = assessment_fixture(recovery_template, Path(temp))
        try:
            yield case
        finally:
            for path, raw in saved.items():
                path.write_bytes(raw)
            (run/'retained-manifest.json').unlink(missing_ok=True)
            if (run/'inventory').exists():
                shutil.rmtree(run/'inventory')


def test_retention_only_cli_recovers_unfinished_publication_without_scientific_execution(recovery, monkeypatch):
    c = recovery
    original = retention._write

    def stop(path, raw):
        if Path(path) == c.run/'retained-manifest.json':
            raise OSError('controlled final publication failure')
        return original(path, raw)

    with monkeypatch.context() as patch:
        patch.setattr(retention, '_write', stop)
        with pytest.raises(OSError):
            retention._seal(c.run)
    before = files(c.run)
    result = subprocess.run([sys.executable, '-B', '-m', 'scripts.weil_whole_source_split',
        'finalize-retention', '--run-dir', str(c.run), '--assessment', str(c.assessment),
        '--source-root', str(c.root)], cwd=c.root, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'PASS_RETAINED_INVENTORY'
    assert all((c.run/name).read_bytes() == raw for name, raw in before.items())
    assert retention.verify_inventory(c.run)['status'] == 'PASS_RETAINED_INVENTORY'
    sealed = files(c.run)
    assert retention.finalize_retention(c.run, c.assessment, code_root=c.root)['status'] == 'PASS_RETAINED_INVENTORY'
    assert files(c.run) == sealed


@pytest.mark.parametrize('change', ['published-report', 'missing-report', 'missing-receipt',
    'failed-receipt', 'uncontained', 'foreign-run', 'wrong-function', 'negative-result',
    'changed-source', 'changed-runtime'])
def test_missing_conflicting_or_foreign_assessment_cannot_seal(recovery, change):
    c = recovery
    if change == 'published-report':
        report = json.loads(c.assessment.read_bytes())
        report['gamma'] = {'unbound':True}
        store(c.assessment, report)
    elif change == 'missing-report':
        c.assessment.unlink()
    elif change == 'missing-receipt':
        c.receipt_path.unlink()
    elif change in ('failed-receipt', 'uncontained'):
        c.receipt['exit_code' if change == 'failed-receipt' else 'worker_cleanup_verified'] = 1 if change == 'failed-receipt' else False
        store(c.receipt_path, c.receipt)
    elif change == 'foreign-run':
        task = retention._request(run=str(c.run.parent/'different-run'))
        store(Path(c.stage['task_file']), task)
        c.payload['task_id'] = task['task_id']
        c.bind()
    elif change == 'wrong-function':
        c.stage['plan']['task_function'] = 'evaluate_exact'
        c.bind()
    elif change == 'negative-result':
        c.payload['result']['status'] = 'FAILED_NO_REFERENCE_ACCEPTANCE'
        c.bind()
    elif change == 'changed-source':
        (c.run/'source/producer/source-manifest.json').write_bytes(b'{}')
    else:
        with (c.attempt/'runtime/scripts/whole_source/retention.py').open('ab') as stream:
            stream.write(b'\n# changed runtime\n')
    before = files(c.run)
    with pytest.raises(ContractError):
        retention.finalize_retention(c.run, c.assessment, code_root=c.root)
    assert not (c.run/'retained-manifest.json').exists()
    assert not (c.run/'inventory').exists()
    assert files(c.run) == before


def test_retention_cannot_mutate_a_separately_sealed_ancestor(tmp_path):
    enclosing = tmp_path/'enclosing'
    run = enclosing/'run'
    run.mkdir(parents=True)
    (tmp_path/'assessment.json').write_bytes(b'{}')
    retention._seal(enclosing)
    before = files(enclosing)
    with pytest.raises(ContractError, match='sealed'):
        retention.finalize_retention(run, tmp_path/'assessment.json', code_root=tmp_path)
    assert files(enclosing) == before
    assert not (run/'.slice.lock').exists()
    assert retention.verify_inventory(enclosing)['status'] == 'PASS_RETAINED_INVENTORY'


def prospective_assessment(case):
    """Synthetic review/stage controls only, not genuine independent approval."""
    configuration = {'collection':case.stage['collection'],'execution':case.stage['plan']}
    context = retention._assessment_context(case.run,case.output,case.root,configuration)
    store(case.output/'assessment-publication.json',context)
    (case.output/'.slice.lock').touch()
    return context


def forbid_scientific_execution(monkeypatch):
    def forbidden(*args,**kwargs):
        pytest.fail('publication recovery must not execute mathematical callbacks')
    monkeypatch.setattr(retention.WorkloadExecution,'run_stage',forbidden)
    monkeypatch.setattr(retention,'_assess_local',forbidden)
    monkeypatch.setattr(retention,'reviewed_consequence',forbidden)


def test_missing_assessment_publication_recovers_exact_owned_bytes(recovery,monkeypatch):
    c = recovery
    expected = c.assessment.read_bytes()
    prospective_assessment(c)
    c.assessment.unlink()
    before = files(c.output/'collection')
    forbid_scientific_execution(monkeypatch)
    report = retention.recover_assessment_publication(c.run,c.output,code_root=c.root)
    assert canonical_bytes(report)==expected==c.assessment.read_bytes()
    assert files(c.output/'collection')==before
    assert retention.verify_inventory(c.run)['status']=='PASS_RETAINED_INVENTORY'


@pytest.mark.parametrize('change',[
    'historical','foreign-run','foreign-output','context-revision','context-config',
    'no-approval','receipt','cleanup','result','runtime','source','stream','profile',
    'conflict','noncanonical-conflict','sealed-output','sealed-run'])
def test_prospective_assessment_recovery_rejects_missing_or_changed_authority(recovery,change):
    c = recovery
    context = prospective_assessment(c)
    c.assessment.unlink()
    if change=='historical':
        (c.output/'assessment-publication.json').unlink()
    elif change in ('foreign-run','foreign-output','context-revision','context-config'):
        if change=='foreign-run':
            context['configuration']['run'] = str(c.run.parent/'other')
        elif change=='foreign-output':
            context['output'] = str(c.output.parent/'other')
        elif change=='context-revision':
            context['configuration']['code'][0]['artifact']['sha256'] = '0'*64
        else:
            context['configuration']['configuration']['execution']['precision_bits'] += 1
        store(c.output/'assessment-publication.json',context)
    elif change=='no-approval':
        (c.run/'review-decision.json').write_bytes(b'{}')
    elif change=='receipt':
        c.receipt_path.unlink()
    elif change=='cleanup':
        c.receipt['worker_cleanup_verified'] = False
        store(c.receipt_path,c.receipt)
    elif change=='result':
        c.result_path.write_bytes(b'{}')
    elif change=='runtime':
        with (c.attempt/'runtime/scripts/whole_source/retention.py').open('ab') as stream:
            stream.write(b'\n# changed captured implementation\n')
    elif change=='source':
        (c.run/'source/producer/source-manifest.json').write_bytes(b'{}')
    elif change=='stream':
        path = c.attempt/c.receipt['logs']['stdout']['path']
        path.write_bytes(b'changed')
    elif change=='profile':
        path = c.attempt/'profile.json'
        profile = json.loads(path.read_bytes())
        profile['exit_code'] = 1
        store(path,profile)
    elif change in ('conflict','noncanonical-conflict'):
        raw = b'{}' if change=='conflict' else b' '+canonical_bytes(
            retention._completed_assessment(c.run,c.output,c.root))
        c.assessment.write_bytes(raw)
    elif change=='sealed-output':
        retention._seal(c.output)
    else:
        retention._seal(c.run)
    before_run,before_output = files(c.run),files(c.output)
    with pytest.raises((ContractError,FileNotFoundError)):
        retention.recover_assessment_publication(c.run,c.output,code_root=c.root)
    assert files(c.run)==before_run
    assert files(c.output)==before_output


@pytest.mark.parametrize('lock_target',['science','assessment'])
def test_assessment_publication_lock_exclusion(recovery,lock_target):
    c = recovery
    prospective_assessment(c)
    c.assessment.unlink()
    target = c.run if lock_target=='science' else c.output
    def evidence(directory):
        return {name:raw for name,raw in files(directory).items() if name!='.slice.lock'}
    before_run,before_output = evidence(c.run),evidence(c.output)
    with retention._slice_writer(target,resume=True):
        with pytest.raises(ContractError,match='owned'):
            retention.recover_assessment_publication(c.run,c.output,code_root=c.root)
    assert evidence(c.run)==before_run
    assert evidence(c.output)==before_output


@pytest.mark.parametrize('stop_at',['intent','report','seal'])
def test_assessment_publication_interruption_is_recoverable_without_new_math(recovery,monkeypatch,stop_at):
    from scripts.whole_source import recovery as publication
    c = recovery
    expected = c.assessment.read_bytes()
    prospective_assessment(c)
    c.assessment.unlink()
    forbid_scientific_execution(monkeypatch)
    original = publication.finish_publication
    def stop(path,raw,**kwargs):
        result = original(path,raw,**kwargs)
        if Path(path).name==('assessment-terminal.json' if stop_at=='intent' else 'assessment.json'):
            raise OSError('controlled completed publication interruption')
        return result
    with monkeypatch.context() as patch:
        if stop_at=='seal':
            def stop_seal(*args):
                raise OSError('controlled report-first seal-last interruption')
            patch.setattr(retention,'_seal',stop_seal)
        else:
            patch.setattr(publication,'finish_publication',stop)
        with pytest.raises(OSError,match='controlled'):
            retention.recover_assessment_publication(c.run,c.output,code_root=c.root)
    before = files(c.output)
    report = retention.recover_assessment_publication(c.run,c.output,code_root=c.root)
    assert canonical_bytes(report)==expected==c.assessment.read_bytes()
    assert all((c.output/name).read_bytes()==raw for name,raw in before.items())
    assert retention.verify_inventory(c.run)['status']=='PASS_RETAINED_INVENTORY'


def test_assessment_terminal_intent_tampering_refuses_report(recovery,monkeypatch):
    from scripts.whole_source import recovery as publication
    c = recovery
    prospective_assessment(c)
    c.assessment.unlink()
    original = publication.finish_publication
    def stop(path,raw,**kwargs):
        result = original(path,raw,**kwargs)
        if Path(path).name=='assessment-terminal.json':
            raise OSError('controlled terminal intent interruption')
        return result
    with monkeypatch.context() as patch:
        patch.setattr(publication,'finish_publication',stop)
        with pytest.raises(OSError,match='controlled'):
            retention.recover_assessment_publication(c.run,c.output,code_root=c.root)
    path = c.output/'assessment-terminal.json'
    intent = json.loads(path.read_bytes())
    intent['report']['RH_proved'] = True
    store(path,intent)
    before_run,before_output = files(c.run),files(c.output)
    with pytest.raises(ContractError,match='conflicting'):
        retention.recover_assessment_publication(c.run,c.output,code_root=c.root)
    assert not c.assessment.exists()
    assert files(c.run)==before_run
    assert files(c.output)==before_output


def test_retention_selects_recovery_producers_not_failed_later_history(recovery,monkeypatch):
    """Selection is synthetic; original verify_stage and history cleanup remain real."""
    from scripts.whole_source import recovery as journal
    c = recovery
    collection = c.output/'collection'
    later = collection/'attempts/later'
    failed = dict(c.receipt,stage='failed',exit_code=1)
    store(later/'failed/receipt.json',failed)
    store(later/'failed-stage.json',{'attempt_id':'later'})
    selected = []
    def choose(directory):
        assert directory==collection
        journal.check_history(directory)
        selected.append(directory)
        return [retention._record(c.receipt_path)]
    monkeypatch.setattr(journal,'selected_receipts',choose)
    expected = [retention._record(c.receipt_path)]
    assert retention._verify_receipts(collection,code_root=c.root)==expected
    assert selected==[collection]
    failed['worker_cleanup_verified'] = False
    store(later/'failed/receipt.json',failed)
    with pytest.raises(ContractError,match='cleanup'):
        retention._verify_receipts(collection,code_root=c.root)
