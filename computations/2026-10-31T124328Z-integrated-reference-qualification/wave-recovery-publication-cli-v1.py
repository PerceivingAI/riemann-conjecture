"""Real CLI recovery with explicitly synthetic review/stage metadata; no approval."""
from pathlib import Path
from types import SimpleNamespace
import argparse
import hashlib
import json
import subprocess
import time
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def fingerprints(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}


def account(directory):
    files = [p for p in directory.rglob('*') if p.is_file()]
    return {'files':len(files),'logical_bytes':sum(p.stat().st_size for p in files)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--proposal-owned-dir', type=Path, required=True)
    args = parser.parse_args()
    output, owned = args.output_dir.resolve(), args.proposal_owned_dir.resolve(strict=True)
    output.relative_to(ROOT)
    from scripts.whole_source import recovery
    output.mkdir(parents=True, exist_ok=False)
    from scripts.whole_source import retention
    from scripts.whole_source.contract import canonical_bytes
    from scripts.whole_source.receipts import discover_receipts
    from tests.test_whole_source_retention import _complete_review_template
    from tests.test_whole_source_retention_recovery import assessment_fixture, prospective_assessment
    records = []

    def cli(label, arguments, expected):
        started = time.perf_counter_ns()
        command = [sys.executable, '-B', '-m', 'scripts.weil_whole_source_split', *arguments]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=300)
        (output/(label+'-stdout.txt')).write_bytes(result.stdout)
        (output/(label+'-stderr.txt')).write_bytes(result.stderr)
        records.append({'label':label,'argv':command,'exit_code':result.returncode,
                        'inclusive_elapsed_ns':time.perf_counter_ns()-started})
        assert result.returncode == expected, result.stderr.decode(errors='replace')

    proposal = owned/'work/proposal-retry'
    core = json.loads((proposal/'proposal.json').read_bytes())
    source = Path(core['source_directory_at_execution'])/core['source']['path']
    payloads = [proposal/'proposal.json', proposal/core['diagnostics']['path']]
    payloads.extend(proposal/row['artifact']['path'] for block in core['blocks']
                    for row in block['integer_panels'])
    before = {path:path.read_bytes() for path in payloads}
    receipts = set(discover_receipts(proposal))
    before_account = account(proposal)
    cli('proposal-completed-resume', ['propose', '--problem',str(owned/'work/proposal-inputs/problem.json'),
        '--source',str(source),'--execution',str(owned/'work/proposal-inputs/execution.json'),
        '--output-dir',str(proposal),'--resume'], 0)
    assert all(path.read_bytes()==raw for path,raw in before.items())
    assert set(discover_receipts(proposal))==receipts
    after_account = account(proposal)
    exact_collection = owned/'work/exact-retry/collection'
    started = time.perf_counter_ns()
    context = recovery._context_document(exact_collection)
    nodes,head = recovery._state(exact_collection,context)
    journal_scan_ns = time.perf_counter_ns()-started
    started = time.perf_counter_ns()
    selected = recovery.selected_receipts(exact_collection)
    selected_validation_ns = time.perf_counter_ns()-started

    fixture = output/'synthetic-review-fixture'
    fixture.mkdir()
    template = _complete_review_template.__wrapped__(SimpleNamespace(mktemp=lambda name:fixture))
    case = assessment_fixture(template,output/'synthetic-assessment')
    prospective_assessment(case)
    expected = case.assessment.read_bytes()
    case.assessment.unlink()  # This procedure's new synthetic publication only.
    collection_before = fingerprints(case.output/'collection')
    absent = output/'absent-context'
    absent.mkdir()
    cli('missing-context-refusal',['recover-assessment-publication','--run-dir',str(case.run),
        '--assessment-dir',str(absent)],2)
    assert not (absent/'assessment.json').exists()
    cli('synthetic-assessment-publication',['recover-assessment-publication','--run-dir',str(case.run),
        '--assessment-dir',str(case.output)],0)
    assert case.assessment.read_bytes()==expected
    assert fingerprints(case.output/'collection')==collection_before
    assert retention.verify_inventory(case.run)['status']=='PASS_RETAINED_INVENTORY'
    sealed = fingerprints(case.run)
    cli('sealed-run-refusal',['recover-assessment-publication','--run-dir',str(case.run),
        '--assessment-dir',str(case.output)],2)
    assert fingerprints(case.run)==sealed
    report = {'status':'PASS_CONTROL_ONLY_PUBLICATION_CLI_RECOVERY','commands':records,
        'proposal_math_and_diagnostics_raw_preserved':True,'proposal_new_receipts':0,
        'synthetic_assessment_collection_raw_preserved':True,
        'assessment_upstream':'SYNTHETIC_REVIEW_AND_STAGE_METADATA_ONLY',
        'genuine_independent_review':False,'scientific_acceptance':False,
        'new_assessment_numerical_execution':False,'production_admission':False,
        'proposal_completed_retry_before':before_account,'proposal_completed_retry_after':after_account,
        'proposal_completed_retry_growth_bytes':after_account['logical_bytes']-before_account['logical_bytes'],
        'cold_exact_journal_scan_ns':journal_scan_ns,'cold_exact_journal_nodes':len(nodes),
        'cold_selected_receipt_validation_ns':selected_validation_ns,'selected_original_receipts':len(selected)}
    (output/'verification.json').write_bytes(canonical_bytes(report))
    print(report['status'])


if __name__=='__main__':
    main()
