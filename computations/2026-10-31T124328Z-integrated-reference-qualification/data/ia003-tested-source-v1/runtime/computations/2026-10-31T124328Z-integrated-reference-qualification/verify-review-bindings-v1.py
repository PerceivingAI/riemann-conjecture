"""CONTROL_ONLY owned execution identity smoke, not scientific acceptance."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.whole_source import retention
from scripts.whole_source.artifacts import CollectionLock
from scripts.whole_source.contract import ContractError, bind_problem, canonical_bytes
from scripts.whole_source.execution import WorkloadExecution
from tests.test_whole_source_execution import case, task


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    output = parser.parse_args().output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    problem = bind_problem('retained-t081')
    captured, spec, plan = case(output, problem)
    requests = [task(x=x) for x in (-3, 0, 5)]
    expected = {request['task_id']: hex(1-2*x+3*x*x)
                for request, x in zip(requests, (-3, 0, 5), strict=True)}
    with CollectionLock.acquire(output/'collection', spec) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=captured) as execution:
            execution.run_stage('review-identity', requests)
            observed = {row['task_id']: row['result']['polynomial']
                        for row in execution.read_results('review-identity')}
            if observed != expected or not execution.receipts[-1]['worker_cleanup_verified']:
                raise ContractError('owned polynomial results or cleanup differ')
        code, _, locations = retention._implementation_code(ROOT)
        # This artificial control program is not in the production review closure.
        code.append({'kind': 'current', 'artifact': asdict(plan.task_program)})
        receipts = retention._verify_receipts(lock.root)
        identities = [retention._stage_implementation(ref, code, locations) for ref in receipts]
        changed = [dict(row, artifact=dict(row['artifact'])) for row in code]
        for row in changed:
            if row['artifact']['path'] == 'scripts/whole_source/execution.py':
                row['artifact']['sha256'] = '0'*64
        try:
            retention._stage_implementation(receipts[0], changed, locations)
        except ContractError as error:
            if str(error) != 'executed code differs from frozen reviewed implementation':
                raise
        else:
            raise ContractError('wrong reviewed version was accepted')
    report = {'status': 'PASS_CONTROL_ONLY_EXECUTION_IDENTITY_BINDING',
        'scope': 'ARTIFICIAL_POLYNOMIAL_CONTROL_NOT_FULL_REVIEW_OR_SCIENTIFIC_ACCEPTANCE',
        'results': observed, 'expected': expected, 'identities': identities,
        'control_program': asdict(plan.task_program),
        'wrong_reviewed_version_rejected': True, 'worker_cleanup_verified': True,
        'runtime_versions': retention._runtime_versions(), 'production_admission': False}
    retention._write(output/'smoke-result.json', canonical_bytes(report))
    print(report['status'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
