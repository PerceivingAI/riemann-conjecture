"""Qualify completed metadata controls without rerunning or altering their evidence."""
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.whole_source import exact, pipeline, retention
from scripts.whole_source.artifacts import CollectionSpec, _decode_chunk, _raw
from scripts.whole_source.contract import ArtifactRef, canonical_bytes, problem_id
from scripts.whole_source.execution import MIB, _write
from scripts.whole_source.proposal import read_proposal
from scripts.whole_source.receipts import discover_receipts, verify_stage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',type=Path,required=True)
    parser.add_argument('--capture-root',type=Path,required=True)
    parser.add_argument('--baseline-report',type=Path,required=True)
    parser.add_argument('--corrected-report',type=Path,required=True)
    parser.add_argument('--baseline-inventory-report',type=Path,required=True)
    parser.add_argument('--corrected-inventory-report',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    run, capture, output = args.run_dir.resolve(strict=True),args.capture_root.resolve(strict=True),args.output.resolve()
    assert not output.exists() and not output.is_relative_to(run)
    inventory_path = output.with_name(output.stem+'-run-inventory.json')
    names = sorted(p.relative_to(run).as_posix() for p in run.rglob('*') if p.is_file())
    members = [{'path':name,**retention._hash_file(run/name)} for name in names]
    _write(inventory_path,canonical_bytes({'format':'metadata-completed-run-inventory-v1',
        'run_directory':run.relative_to(ROOT).as_posix(),'files':members}))
    preservation = json.loads((capture/'preservation.json').read_bytes())
    for value in preservation['files']:
        _raw(capture,ArtifactRef(**value),8*MIB)
    for path in (capture/'runtime/scripts/whole_source').glob('*.py'):
        assert path.read_bytes() == (ROOT/'scripts/whole_source'/path.name).read_bytes()
    reports = [json.loads(path.read_bytes()) for path in (args.baseline_report,args.corrected_report,
        args.baseline_inventory_report,args.corrected_inventory_report)]
    before, after, inventory_before, inventory_after = reports
    for old,new in zip(before['results'],after['results'],strict=True):
        assert old['chunks']==new['chunks'] and old['science_sha256']==new['science_sha256']
        old_counts,new_counts = old['publication_counters'],new['publication_counters']
        assert new_counts['index_reads']==0
        assert old_counts['quota_checks']==new_counts['quota_checks']
        assert old_counts['tree_walks']==2*new_counts['tree_walks']
    for old,new in zip(inventory_before['results'],inventory_after['results'],strict=True):
        assert old['members']==new['members'] and old['member_payload_digest']==new['member_payload_digest']
        assert old['original_member_hash_calls']==new['original_member_hash_calls']==3*new['members']
        assert new['member_hashes_before_first_snapshot_row_encoding']==1
        assert new['max_decoded_shard_rows_ahead_of_member_verification']<=4096
    problem,_,roles = pipeline._bind(run/'reduced-inputs/problem.json',run/'reduced-inputs/execution.json',ROOT)
    source = pipeline.SourceReader(run/'source/producer/source-manifest.json',roles['producer'][0],control=True)
    independent = pipeline.SourceReader(run/'audit/analytic/source-manifest.json',roles['analytic'][0],control=True)
    pipeline.verify_source_execution(source)
    pipeline.verify_source_execution(independent)
    pipeline.verify_audit_execution(run/'audit/analytical-receipt.json',source,independent)
    checked = 0
    for (source_domain,produced),(audit_domain,reconstructed) in zip(source.tiles(),independent.tiles(),strict=True):
        assert (source_domain['family'],source_domain['parity'])==(audit_domain['family'],audit_domain['parity'])
        for left,right in zip(produced,reconstructed,strict=True):
            assert (left.row,left.column)==(right.row,right.column)
            assert left.lower<=right.lower<=right.upper<=left.upper
            checked += 1
    audit = json.loads((run/'audit/analytical-receipt.json').read_bytes())
    assert checked==audit['entries_checked']==36 and audit['full_mathematical_source'] is False
    manufactured_problem,_,manufactured_roles = pipeline._bind(run/'manufactured/source-inputs/problem.json',
        run/'manufactured/source-inputs/execution.json',ROOT)
    manufactured_source = pipeline.SourceReader(run/'manufactured/original-source/source-manifest.json',
        manufactured_roles['producer'][0],control=True)
    proposal_path = run/'proposal/proposal.json'
    proposed = read_proposal(proposal_path,manufactured_problem,asdict(manufactured_source.ref))
    bound_problem,_,descriptor,_,_ = exact._bind_exact(run/'exact-inputs/problem.json',run/'exact-inputs/execution.json',ROOT)
    assessed = json.loads((run/'exact/report.json').read_bytes())
    assert problem_id(bound_problem)==assessed['problem_id']==problem_id(problem)
    assert assessed['source']==descriptor['source'] and assessed['proposal']==descriptor['origin']
    assert assessed['status']==assessed['assessment']['status']=='PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL'
    assert assessed['assessment']['positive_paid_lower'] is True
    assert assessed['proof_scope']==descriptor['proof_scope']=='CONTROL_ONLY'
    assert assessed['assessment']['smooth_test_consequence_conditional'] is False
    assert assessed['production_admission'] is False and proposed['status']=='NONPROOF_ONLY'
    stage_results, stages, peak = {},[],0
    exact_receipts = {run/'exact'/row['path'] for row in assessed['receipt_bindings']}
    structural_results = []
    for receipt_path in discover_receipts(run):
        verified = verify_stage(receipt_path)
        stage,plan = verified['stage'],verified['plan']
        assert plan.cpus==2 and plan.memory_mib==2048 and plan.workers*plan.threads<=2
        result_dir = Path(stage['result_dir'])
        results = []
        for line in (result_dir/'completed.jsonl').read_bytes().splitlines():
            row = json.loads(line)
            payload = json.loads(_raw(result_dir,ArtifactRef(**{key:row[key] for key in ('path','size','sha256')}),plan.result_bytes))
            results.append(payload['result'])
        receipt = json.loads(receipt_path.read_bytes())
        peak = max(peak,receipt['peak_budgeted_memory_bytes'])
        if receipt_path in exact_receipts:
            assert stage['task_count']==1 and len(results)==1
            stage_results[receipt['stage']] = results[0]
        if receipt['stage']=='metadata-control':
            assert stage['task_count']==2 and len(results)==2
            spec = CollectionSpec.from_dict(problem,stage['collection'])
            for result in results:
                assert result['scope']=='CONTROL_ONLY_STRUCTURAL_NOT_WEIL_SOURCE'
                staged = ArtifactRef(**result['artifact'])
                committed = ArtifactRef('chunks/'+staged.sha256,staged.sha256,staged.size)
                snapshot = _decode_chunk(spec,_raw(run/'owned-structural',committed,spec.bounds.max_compressed_bytes))
                assert snapshot.header['task']==result['domain']
                for row in snapshot.records:
                    value = Fraction((row.row+1)*(row.column+3),8)
                    assert row.lower<=value-Fraction(1,32)<=value+Fraction(3,64)<=row.upper
                structural_results.append(committed.sha256)
        stages.append({'receipt':receipt_path.relative_to(run).as_posix(),'task_count':stage['task_count'],
            'workers':plan.workers,'native_threads':plan.threads})
    assert len(stages)==30 and len(structural_results)==2
    assert set(stage_results)=={'parity-0','parity-1','assess'}
    assert assessed['blocks']==[stage_results['parity-'+str(p)]['report'] for p in (0,1)]
    assert assessed['assessment']==stage_results['assess']['assessment']
    pool_path = next((run/'owned-structural').rglob('metadata-control-pool-observation.json'))
    pool = json.loads(pool_path.read_bytes())
    assert pool['workers_observed']==pool['concurrent_workers_observed']==pool['task_workers_observed']==2
    assert pool['cleanup_verified'] is True
    resources_path = next((run/'owned-structural').rglob('metadata-control-resources.json'))
    resources = json.loads(resources_path.read_bytes())
    assert resources['cleanup_verified'] is True and resources['owned_hard_cap_bytes']==2048*MIB
    assert 'PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL: scope=CONTROL_ONLY' in (run/'exact-cli-stdout.txt').read_text()
    assert names==sorted(p.relative_to(run).as_posix() for p in run.rglob('*') if p.is_file())
    for row in members:
        assert retention._hash_file(run/row['path'])=={key:row[key] for key in ('size','sha256')}
    result = {'status':'PASS_CONTROL_ONLY_METADATA_CORRECTION','owned_stage_count':len(stages),'owned_stages':stages,
        'independent_reduced_entries_checked':checked,'exact_status':assessed['status'],'exact_scope':assessed['proof_scope'],
        'observed_two_worker_staging':True,'owned_structural_resources':resources,'max_owned_budgeted_memory_bytes':peak,
        'structural_exact_payloads_agree':True,'inventory_member_payloads_agree':True,'all_owned_cleanup_verified':True,
        'run_inventory':retention._record(inventory_path),'capture_manifest':retention._record(capture/'preservation.json'),
        'structural_reports':[retention._record(path) for path in (args.baseline_report,args.corrected_report)],
        'inventory_reports':[retention._record(path) for path in (args.baseline_inventory_report,args.corrected_inventory_report)],
        'coordinator_v1_reporting_failure':'Expected nonexistent EXACT_MATRIX_POSITIVITY label after completed CLI exact execution.',
        'numerical_stages_rerun':False,'full_qualification_executed':False,'scientific_full_source_acceptance':False,
        'production_admission':False}
    _write(output,canonical_bytes(result))
    print(json.dumps({'status':result['status'],'owned_stages':len(stages),'reduced_entries':checked,
        'concurrent_staging_workers':2,'numerical_stages_rerun':False},sort_keys=True))


if __name__=='__main__':
    main()
