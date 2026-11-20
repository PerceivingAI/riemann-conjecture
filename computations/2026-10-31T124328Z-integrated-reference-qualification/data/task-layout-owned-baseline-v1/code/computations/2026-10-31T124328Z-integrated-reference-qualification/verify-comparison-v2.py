"""Exercise comparison CLI on metadata fixtures, never scientific qualification."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.whole_source.contract import ROOT, canonical_bytes
from tests.test_whole_source_receipts import stage_receipt

BASE = Path(__file__).resolve().parent


def store(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(document))


def make_stage(directory, label, state=None, elapsed=None, failed=False):
    receipt = stage_receipt.__wrapped__(directory/'source'/label)
    document = json.loads(receipt.read_bytes())
    document.update(elapsed_seconds=2, peak_budgeted_memory_bytes=1024)
    document['last_metrics']['cpu_seconds'] = 1
    if failed:
        document['exit_code'] = 1
    store(receipt, document)
    attempt = receipt.parent.parent
    store(attempt/'fixture-resources.json', {'sampled_external_increment_bytes':64})
    store(attempt/'fixture-pool-observation.json', {'concurrent_workers_observed':1})
    if state is not None:
        identity = {'format':'riemann-run-identity-v1','run_id':'fixture-'+label,
            'pid':123,'started_at_utc':'2026-11-12T00:00:00Z',
            'driver':'whole-source-owned-execution-v1','support':'81/100'}
        store(attempt/'.live/run.json', identity)
        store(attempt/'.live/run-status.json', {'format':'riemann-live-run-v1',
            'run_id':identity['run_id'],'pid':identity['pid'],'started_at_utc':identity['started_at_utc'],
            'command':identity['driver'],'support':identity['support'],
            'terminal':state!='RUNNING','workflow_state':state,'elapsed_seconds':elapsed})
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    output = parser.parse_args().output_dir.resolve()
    output.relative_to(ROOT)
    output.mkdir(parents=True, exist_ok=False)
    baseline = output/'baseline-fixture'
    for phase in ('source','independent-audit','exact-sign'):
        store(baseline/phase/'receipt.json', {'exit_code':0,'worker_cleanup_verified':True,
            'elapsed_seconds':2,'last_metrics':{'cpu_seconds':1},'peak_budgeted_memory_bytes':1024,
            'budget':{'memory_budget_bytes':4096},'fixture':'METADATA_ONLY_NOT_AN_EXECUTED_BASELINE'})
        store(baseline/phase/'profile.json', {'cpu_seconds':1,'native_threads':1})
    store(baseline/'qualification.json', {'status':'PASS_CAPTURED_SOURCE_ANALYTICAL_EXACT_AND_NINE_CONTROLS',
        'fixture':'SYNTHETIC_BASELINE_PREREQUISITE_NOT_GENUINE_QUALIFICATION'})
    unavailable, available, rejected = (output/name for name in ('run-unavailable','run-available','run-rejected'))
    make_stage(unavailable, 'missing')
    make_stage(unavailable, 'stale', 'RUNNING', 3)
    make_stage(unavailable, 'failed-owner', 'RUN_FAILED', 10)
    make_stage(available, 'first', 'RUN_COMPLETED', 10)
    make_stage(available, 'second', 'RUN_INTERRUPTED', 20)
    make_stage(available, 'third', 'RUN_FAILED', 30)
    make_stage(rejected, 'invalid-owned-stage', failed=True)
    outputs = []
    for name, run in (('unavailable', unavailable), ('available', available), ('rejected', rejected)):
        report_path = output/(name+'-report.json')
        command = [sys.executable,'-B',str(BASE/'compare-execution-v2.py'),
            '--run-dir',str(run),'--baseline-dir',str(baseline),'--output',str(report_path)]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=60)
        (output/(name+'-stdout.txt')).write_text(result.stdout, encoding='utf-8')
        (output/(name+'-stderr.txt')).write_text(result.stderr, encoding='utf-8')
        outputs.append({'case':name,'exit_code':result.returncode,'command':command})
        if name == 'rejected':
            assert result.returncode != 0 and not report_path.exists(), result.stdout
            continue
        assert result.returncode == 0, result.stderr
        report = json.loads(report_path.read_bytes())
        assert report['format'] == 'whole-source-retained-execution-comparison-v2'
        assert report['status'] == 'OPERATIONAL_AND_DIAGNOSTIC_COMPARISON_ONLY'
        assert report['new']['owned_receipts_verified'] == 3
        assert report['new']['completion']['whole_pipeline_completion_asserted'] is False
        assert report['new']['completion']['scientific_acceptance_asserted'] is False
        phase = report['new']['phases']['source']
        assert phase['stage_elapsed_seconds'] == 6 and phase['owned_cpu_seconds'] == 3
        if name == 'unavailable':
            assert phase['collection_owner_elapsed_seconds'] is None
            assert phase['aggregate_cpu_per_owner_wall'] is None
            assert sorted(t['availability'] for t in phase['owner_timings']) == ['AVAILABLE','UNAVAILABLE','UNAVAILABLE']
        else:
            assert phase['collection_owner_elapsed_seconds'] == 60
            assert phase['aggregate_cpu_per_owner_wall'] == 0.05
    original_hash = hashlib.sha256((BASE/'compare-execution-v1.py').read_bytes()).hexdigest()
    assert original_hash == 'dc65b70d78a6ece1d6f78fbabc60f2bf054065782b2523ea3ac8d26e8d6d8bdb'
    result = {'status':'PASS_METADATA_COMPARISON_V2_CLI','cases':outputs,
        'scope':'Synthetic stage/timing/baseline prerequisites; real strict verification, comparison CLI and dirrake census. No mathematical execution, qualification, physical I/O or speedup measurement.',
        'original_comparator_sha256':original_hash}
    store(output/'verification.json', result)
    print(result['status'])
    print('Missing/stale timing: report published with null owner total and ratio')
    print('Terminal failed/interrupted owners: selected successful stages retained')
    print('Invalid owned stage: rejected without report')


if __name__ == '__main__':
    main()
