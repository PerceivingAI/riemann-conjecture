"""CLI publication controls with synthetic review/stage metadata, never approval."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import argparse
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))


def fingerprints(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    output=parser.parse_args().output_dir.resolve()
    output.relative_to(ROOT)
    output.mkdir(parents=True,exist_ok=False)
    from scripts.whole_source import retention
    from scripts.whole_source.contract import canonical_bytes
    from tests import test_whole_source_execution as execution_fixture
    from tests.test_whole_source_retention import _complete_review_template
    from tests.test_whole_source_retention_recovery import assessment_fixture,prospective_assessment
    original=execution_fixture.case
    def metadata_case(*args,**kwargs):
        root,spec,plan=original(*args,**kwargs)
        # Only artificial stage metadata: long retained paths exceed its old4KiB packet.
        return root,spec,replace(plan,result_bytes=128*1024)
    fixture=output/'synthetic-review-fixture'
    fixture.mkdir()
    with patch.object(execution_fixture,'case',metadata_case):
        template=_complete_review_template.__wrapped__(SimpleNamespace(mktemp=lambda name:fixture))
    case=assessment_fixture(template,output/'synthetic-assessment')
    prospective_assessment(case)
    expected=case.assessment.read_bytes()
    case.assessment.unlink()  # This procedure's new synthetic publication only.
    before=fingerprints(case.output/'collection')
    records=[]
    def cli(label,destination,expected_code):
        command=[sys.executable,'-B','-m','scripts.weil_whole_source_split',
                 'recover-assessment-publication','--run-dir',str(case.run),
                 '--assessment-dir',str(destination)]
        started=time.perf_counter_ns()
        result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=300)
        (output/(label+'-stdout.txt')).write_bytes(result.stdout)
        (output/(label+'-stderr.txt')).write_bytes(result.stderr)
        records.append({'label':label,'argv':command,'exit_code':result.returncode,
                        'inclusive_elapsed_ns':time.perf_counter_ns()-started})
        assert result.returncode==expected_code,result.stderr.decode(errors='replace')
    absent=output/'absent-context'
    absent.mkdir()
    cli('missing-context-refusal',absent,2)
    assert not (absent/'assessment.json').exists()
    cli('synthetic-publication',case.output,0)
    assert case.assessment.read_bytes()==expected
    assert fingerprints(case.output/'collection')==before
    assert retention.verify_inventory(case.run)['status']=='PASS_RETAINED_INVENTORY'
    sealed=fingerprints(case.run)
    cli('sealed-run-refusal',case.output,2)
    assert fingerprints(case.run)==sealed
    report={'status':'PASS_SYNTHETIC_ASSESSMENT_PUBLICATION_CLI','commands':records,
        'upstream':'SYNTHETIC_REVIEW_AND_STAGE_METADATA_ONLY','synthetic_result_bytes':128*1024,
        'collection_raw_preserved':True,'new_numerical_execution':False,
        'genuine_independent_review':False,'scientific_acceptance':False,'production_admission':False}
    (output/'verification.json').write_bytes(canonical_bytes(report))
    print(report['status'])


if __name__=='__main__':
    main()
