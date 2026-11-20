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
