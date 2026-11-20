"""Short real Windows CLI boundary controls, not mathematical qualification.

All generated scientific-looking inputs are TEST_ONLY_NONAPPROVAL fixtures.
Completed inventory verification does not assert scientific acceptance or review.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
SCOPE = 'TEST_ONLY_NONAPPROVAL_CLI_BOUNDARIES'


def save(path, value):
    from scripts.whole_source.contract import canonical_bytes
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(canonical_bytes(value))


def tree(directory):
    return {path.relative_to(directory).as_posix(): path.read_bytes()
            for path in directory.rglob('*') if path.is_file()}


def invoke(base, name, command, operation, expected_code, expected_message, policy_path):
    from scripts.whole_source import supervision
    from scripts.whole_source.lifecycle_observations import read_receipt
    observer = operation.with_name(operation.name+'.lifecycle')
    argv = [sys.executable, '-B', '-m', 'scripts.weil_whole_source_split', *command,
            '--lifecycle-policy', str(policy_path), '--supervision-dir', str(observer)]
    environment = dict(os.environ)
    environment.pop(supervision.ENV, None)
    result = subprocess.run(argv, cwd=ROOT, env=environment, capture_output=True, timeout=60)
    with (base/(name+'-stdout.log')).open('xb') as stream:
        stream.write(result.stdout)
    with (base/(name+'-stderr.log')).open('xb') as stream:
        stream.write(result.stderr)
    assert result.returncode == expected_code, result.stderr.decode(errors='replace')
    text = (result.stdout+result.stderr).decode(errors='replace')
    assert expected_message in text, text
    assert 'Lifecycle ' in text, text
    paths = list((observer/'receipts').glob('*.json'))
    assert len(paths) == 1, paths
    receipt = read_receipt(observer, paths[0].stem)
    assert receipt['child_returncode'] == expected_code, receipt
    assert receipt['cleanup_verified'] is True, receipt
    assert receipt['final_job']['active_process_count'] == 0, receipt
    assert receipt['final_job']['active_process_ids'] == [], receipt
    assert (receipt['status'] == 'COMPLETED') is (expected_code == 0), receipt
    save(base/(name+'-outcome.json'), {
        'scope': SCOPE, 'argv': argv, 'returncode': result.returncode,
        'observation_root': str(observer), 'receipt': str(paths[0]),
        'status': receipt['status'], 'cleanup_verified': receipt['cleanup_verified'],
        'scientific_acceptance': False, 'production_admission': False})
    return name


def main():
    from scripts.whole_source import retention, supervision
    from scripts.whole_source.contract import bind_problem, canonical_bytes
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if sys.platform != 'win32':
        parser.error('these controls require the genuine Windows lifecycle supervisor')
    base = args.output_dir.resolve()
    base.relative_to(ROOT)
    base.mkdir(parents=True, exist_ok=False)
    policy_path = base/'integrated-qualification-cli-policy-v1.json'
    save(policy_path, {
        'format': supervision.POLICY, 'wall_seconds': 30, 'active_seconds': 120,
        'grace_seconds': 2, 'memory_mib': None, 'sample_milliseconds': 100,
        'stale_milliseconds': 2000, 'observation_bytes': 16*supervision.MIB})
    cases = []

    # Resume must fail before reading even the nonexistent caller input files.
    operation = base/'missing-operation'
    cases.append(invoke(base, 'missing-resume', [
        'run', '--problem', str(base/'missing-problem.json'),
        '--execution', str(base/'missing-execution.json'), '--output-dir', str(operation),
        '--through', 'prepare', '--resume'], operation, 2,
        'resume requires an existing original coordinator operation', policy_path))
    assert not operation.exists()

    # Real retained-target metadata is cheap to bind. No scalar or matrix task runs.
    problem = bind_problem('retained-t081')
    inputs = retention.prepare_inputs(problem, base/'stale-inputs',
        origin_git_commit='0'*40, origin_git_dirty=True)
    config = json.loads(inputs['execution'].read_bytes())
    config['format'] = 'whole-source-integrated-execution-v4'
    inputs['execution'].write_bytes(canonical_bytes(config))
    before_inputs = tree(base/'stale-inputs')
    operation = base/'stale-operation'
    cases.append(invoke(base, 'stale-policy', [
        'run', '--problem', str(inputs['problem']), '--execution', str(inputs['execution']),
        '--output-dir', str(operation), '--through', 'prepare'], operation, 2,
        'changed integrated execution policy', policy_path))
    assert not operation.exists()
    assert tree(base/'stale-inputs') == before_inputs

    # An inventory seal is a byte inventory only. It is not an acceptance report.
    for damaged in (False, True):
        name = 'damaged-seal' if damaged else 'completed-seal'
        operation = base/name
        operation.mkdir()
        payload = operation/'TEST_ONLY_NONAPPROVAL.json'
        save(payload, {'scope': SCOPE, 'scientific_acceptance': False})
        retention._seal(operation)
        if damaged:
            payload.write_bytes(canonical_bytes({'scope': SCOPE, 'changed': True}))
        before = tree(operation)
        assessment = base/(name+'-external')/'assessment.json'
        cases.append(invoke(base, name, [
            'finalize-retention', '--run-dir', str(operation), '--assessment', str(assessment)],
            operation, 2 if damaged else 0,
            'Integrated qualification rejected:' if damaged else 'PASS_RETAINED_INVENTORY', policy_path))
        assert tree(operation) == before
        assert not assessment.parent.exists()
        assert not (operation/'implementation').exists()
        assert not (operation/'collection').exists()
        assert not (operation/'.slice.lock').exists()

    save(base/'integrated-qualification-cli-result-v1.json', {
        'scope': SCOPE, 'status': 'PASS_CLI_BOUNDARY_CONTROLS', 'cases': cases,
        'full_math_executed': False, 'independent_review_performed': False,
        'scientific_acceptance': False, 'production_admission': False})
    print('PASS_CLI_BOUNDARY_CONTROLS')


if __name__ == '__main__':
    main()
