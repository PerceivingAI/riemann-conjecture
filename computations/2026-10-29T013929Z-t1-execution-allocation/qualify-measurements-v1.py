"""Qualify retained resource evidence without calling it a target proof.

Native aborts remain failures with no result; they are not converted to passes.
This command verifies resource/layout conclusions and selected completed kernels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    contract = read(HERE/'probe-inputs-v1.json')
    for binding in contract['bindings'].values():
        assert digest(ROOT/binding['path']) == binding['sha256'], binding['path']
    storage = read(HERE/'data/storage-v1/result.json')
    assert storage['N'] == 5564 and storage['target_dense_matrix_allocated'] is False
    assert len(storage['cases']) == 10
    accounts = []
    for case in storage['cases']:
        assert case['moment_count'] == 16691
        assert case['reflected_window_exact_ball_equality'] is True
        assert case['native_vector_crosscheck']['exact_agreement'] is True
        heap = case['precision']//8
        assert case['native_heap_bytes_histogram'] == {str(heap):16691}
        for account in case['parity_accounts']:
            assert account['entries'] == 5564**2
            assert account['native_struct_array_bytes'] == 5564**2*48
            assert account['native_fresh_copy_heap_bytes'] == 5564**2*heap
            assert account['midpoint_limb_payload_lower_bytes'] == 5564**2*heap
            assert account['dense_native_copy_account_bytes'] == 5564**2*(48+heap)
            accounts.append(account['dense_native_copy_account_bytes'])
    expected_pairs = None
    completed, failed = [], []
    names = ('storage-v1','product-dense-v1','product-blocked-v1',
             'product-dense-v2','product-blocked-v2','product-convolution-v1',
             'product-convolution-threads1-v1')
    for name in names:
        folder = HERE/'data'/name
        stage = 'storage' if name == 'storage-v1' else 'convolution' if 'convolution' in name else 'product'
        receipt = read(folder/stage/'receipt.json')
        assert receipt['worker_cleanup_verified'] is True
        assert receipt['last_metrics']['active_process_count'] == 0
        for channel, binding in receipt['logs'].items():
            assert digest(folder/stage/(channel+'.txt')) == binding['sha256']
        program = Path(receipt['argv'][receipt['argv'].index('--program')+1])
        assert digest(program) == receipt['program_sha256']
        row = {'run':name,'exit_code':receipt['exit_code'],
            'elapsed_seconds':receipt['elapsed_seconds'],
            'native_threads':receipt['budget']['native_threads'],
            'memory_budget_bytes':receipt['budget']['memory_budget_bytes'],
            'raw_job_peak_committed_bytes':receipt['peak_budgeted_memory_bytes'],
            'owned_cleanup_verified':True}
        if receipt['exit_code']:
            assert 'convolution' in name
            assert not (folder/'result.json').exists()
            assert not (folder/stage/'profile.json').exists()
            assert 'Cannot reallocate memory' in (folder/stage/'stderr.txt').read_text(encoding='utf-8')
            row['status'] = 'NATIVE_ALLOCATION_ABORT_UNDER_CONFIGURED_CAP_NO_RESULT'
            failed.append(row)
            continue
        result = read(folder/'result.json')
        profile = read(folder/stage/'profile.json')
        assert profile['exit_code'] == 0
        assert profile['program_sha256'] == receipt['program_sha256']
        row['process_peak_commit_bytes'] = profile['process_memory']['peak_committed_bytes']
        row['process_peak_working_set_bytes'] = profile['process_memory']['peak_working_set_bytes']
        row['process_cpu_seconds'] = profile['cpu_seconds']
        if name != 'storage-v1':
            assert result['inner_powers'] == 5564 and result['precision'] == 34304
            assert result['independent_checked_entries'] == 48
            assert result['omitted_nonzero_leading_power_rejected'] is True
            assert result['target_numerical_goals_checked'] is False
            pairs = result['selected_output_pairs']
            if expected_pairs is None:
                expected_pairs = pairs
            assert pairs == expected_pairs, ('selected dyadic pair mismatch',name)
            row['contraction_wall_seconds'] = result['contraction_wall_seconds']
            row['contraction_cpu_seconds'] = result['contraction_cpu_seconds']
            row['independent_checked_entries'] = 48
        row['status'] = 'COMPLETED_WITH_SCOPED_CHECKS'
        completed.append(row)
    dense = read(HERE/'data/product-dense-v2/live-allocations-v2.json')
    blocked = read(HERE/'data/product-blocked-v2/live-allocations-v2.json')
    assert len(dense['observations']) == 1 and len(blocked['observations']) == 6
    assert all(x['rows'] == 2 and x['columns'] == 5564 for x in blocked['observations'])
    live = {'dense_live_process_commit_bytes':max(x['native_matrix_live']['committed_bytes'] for x in dense['observations']),
            'blocked_live_process_commit_bytes':max(x['native_matrix_live']['committed_bytes'] for x in blocked['observations']),
            'dense_hankel_native_account_bytes':12*5564*(34304//8+48),
            'blocked_hankel_native_account_bytes':2*5564*(34304//8+48),
            'whole_process_peak_reduction_claimed':False}
    host = read(HERE/'data/storage-v1/execution-budget.json')['detection']['windows']['host']
    audit_bytes = 5564**2*(48+34304//8)
    assert audit_bytes > host['total_commit_bytes'] > host['total_physical_bytes']
    output = {'format':'t1-execution-allocation-qualification-v1',
        'status':'PASS_SCOPED_EXECUTION_ASSESSMENT_NOT_FULL_TARGET_ADMISSION',
        'inputs_sha256':digest(HERE/'probe-inputs-v1.json'),
        'qualifier_sha256':digest(Path(__file__)),
        'storage_cases':10,'native_vector_copy_checks':40960,
        'audit_single_dense_hankel_native_account_bytes':audit_bytes,
        'minimum_midpoint_limb_payload_bytes':5564**2*(34304//8),
        'observed_host_total_commit_bytes':host['total_commit_bytes'],
        'observed_host_total_physical_bytes':host['total_physical_bytes'],
        'layout_exceeds_observed_host_total_commit':True,
        'completed_runs':completed,'failed_runs_preserved':failed,
        'selected_completed_outputs_same_dyadic_pairs':True,
        'live_contraction_memory':live,
        'full_target_execution_decision':'NOT_ADMITTED',
        'decision_reasons':['The fixed .81 pipeline is not a T=1 producer/consumer/witness implementation.',
            'The existing N-square audit power-moment layout at the accepted precision exceeds observed host total commit before other data.',
            'Selected blocking/structured probes do not qualify every other live matrix, all target widths or the complete exact path.'],
        'full_target_cost_or_runtime_measured':False,'mathematical_negative_claimed':False,
        'hardware_impossibility_for_other_implementations_claimed':False,
        'target_positivity_proved':False,'production_admission':False,'RH_status':'UNRESOLVED'}
    with args.output.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(output,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':output['status'],'completed_runs':len(completed),'preserved_failed_runs':len(failed),'full_target_execution_decision':'NOT_ADMITTED'}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
