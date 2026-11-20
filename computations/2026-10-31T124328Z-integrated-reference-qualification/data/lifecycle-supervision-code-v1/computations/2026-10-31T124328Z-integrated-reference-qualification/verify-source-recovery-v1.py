"""Real reduced source recovery; no full-source or positivity qualification."""
from dataclasses import asdict
from pathlib import Path
import argparse
import hashlib
import json
import runpy
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source import pipeline, retention
from scripts.whole_source.contract import bind_problem, canonical_bytes
from scripts.whole_source.execution import WorkloadExecution, _write
from scripts.whole_source.receipts import discover_receipts
from scripts.whole_source.slice import _request
from scripts.whole_source.source_dependencies import SourceDependencies


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    problem = bind_problem('retained-t081')
    previous = runpy.run_path(str(Path(__file__).with_name('verify-scientific-identity-v1.py')))
    paths = previous['prepare'](problem, output/'inputs', 1, 128)
    _, config, roles = pipeline._bind(paths['problem'], paths['execution'], ROOT)
    original = WorkloadExecution.run_stage
    injected = []
    def fail_later(execution, name, requests):
        if name == 'head-0' and not injected:
            requests = list(requests)
            malformed = {key:value for key,value in requests[0].items() if key != 'task_id'}
            malformed['n'] = -2
            requests[0] = _request(**malformed)
            injected.append(execution.attempt_id)
        return original(execution, name, requests)
    with patch.object(WorkloadExecution, 'run_stage', fail_later):
        try:
            pipeline.run_source(paths['problem'], paths['execution'], output/'source')
        except Exception as exc:
            _write(output/'controlled-failure.json', canonical_bytes({'type':type(exc).__name__, 'message':str(exc)}))
        else:
            raise AssertionError('controlled source stage unexpectedly succeeded')
    assert len(injected) == 1
    collection = output/'source/producer'
    failed_path = collection/'attempts'/injected[0]/'head-0/receipt.json'
    failed_bytes = failed_path.read_bytes()
    failed = json.loads(failed_bytes)
    assert failed['exit_code'] != 0 and failed['worker_cleanup_verified'] is True
    committed_before = json.loads((collection/'collection.json').read_bytes())['index']
    old_success = [path for path in discover_receipts(collection) if path != failed_path]
    assert old_success
    source = pipeline.run_source(paths['problem'], paths['execution'], output/'source', resume=True)
    assert failed_path.read_bytes() == failed_bytes
    source_path = collection/'source-manifest.json'
    reader = pipeline.SourceReader(source_path, roles['producer'][0], control=True)
    evidence = pipeline.verify_source_execution(reader)
    selected_paths = {ref['path'] for ref in evidence['receipts']}
    assert all(path.relative_to(collection).as_posix() in selected_paths for path in old_success)
    assert failed_path.relative_to(collection).as_posix() not in selected_paths
    assert [ref['path'] for ref in evidence['history']] == [failed_path.relative_to(collection).as_posix()]
    new_attempts = {Path(ref['path']).parts[1] for ref in evidence['receipts']} - {injected[0]}
    assert len(new_attempts) == 1
    assert not any((collection/'attempts'/attempt/(name+'-stage.json')).exists()
                   for attempt in new_attempts for name in ('kernel-groups-0','kernel-0','columns-0'))
    audit = pipeline.run_audit(paths['problem'], source_path, paths['execution'], output/'audit')
    assert audit['entries_checked'] == 36 and audit['full_mathematical_source'] is False
    aggregate = retention._verify_receipts(output)
    assert failed_path.resolve() not in {
        (Path(row['directory'])/row['artifact']['path']).resolve() for row in aggregate}
    controls = []
    binding = collection/evidence['dependencies'][0]['path']
    saved = binding.read_bytes()
    try:
        binding.unlink()
        try:
            pipeline.verify_source_execution(reader)
        except (OSError, ValueError) as exc:
            controls.append({'case':'missing-producer','rejected':True,'reason':str(exc)})
        else:
            raise AssertionError('missing producer accepted')
    finally:
        binding.write_bytes(saved)
    report = {'status':'PASS_CONTROL_ONLY_RECOVERED_SOURCE_DEPENDENCIES',
        'scope':'N6_M12_K2_SOURCE_RECOVERY_NOT_FULL_QUALIFICATION',
        'entries_audited':audit['entries_checked'],'original_attempt':injected[0],
        'resumed_attempt':next(iter(new_attempts)),'old_successful_stages_reused':len(old_success),
        'selected_source_stages':len(evidence['receipts']),
        'preserved_failed_receipt_sha256':hashlib.sha256(failed_bytes).hexdigest(),
        'prior_committed_index':committed_before,'selected_dependency_nodes':len(evidence['dependencies']),
        'source_manifest_sha256':reader.ref.sha256,'negative_controls':controls,
        'production_admission':False,'full_qualification_executed':False,'RH_proved':False}
    _write(output/'verification.json', canonical_bytes(report))
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
