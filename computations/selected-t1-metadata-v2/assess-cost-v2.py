"""Attach measured baseline observations to the independently qualified scalar shape."""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

MEASUREMENTS_SHA256 = "bd7877a478ab6f1ed9cf07478031cbcaccaa4a35171dffc6b8d44d6139ff1712"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs',type=Path,required=True)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--audit',type=Path,required=True)
    p.add_argument('--measurements',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    source = json.loads(args.source.read_bytes())
    audit = json.loads(args.audit.read_bytes())
    if not (source['format']=='t1-reference-cost-source-v2'
            and audit['format']=='t1-reference-cost-audit-v2'
            and audit['status']=='PASS' and audit['source_sha256']==sha(args.source)
            and source['inputs_sha256']==audit['inputs_sha256']==sha(args.inputs)
            and audit['audit_code_sha256']==sha(Path(__file__).with_name('verify-reference-v3.py'))
            and source['target_matrix_computed'] is False
            and source['target_positivity_proved'] is False):
        raise ValueError('qualified same-byte scalar source required')
    measurement_bytes = args.measurements.read_bytes()
    if hashlib.sha256(measurement_bytes).hexdigest() != MEASUREMENTS_SHA256:
        raise ValueError('changed portable baseline observations')
    measured = json.loads(measurement_bytes)
    N, M = source['N'],source['M']
    ratio = Q(N,826)
    cells = Q(source['shape']['translation_cells'],9)
    entries = Q(source['shape']['six_triangular_entries'],512946)
    rows = []
    for name,old_bits,new_bits in [('source',4608,source['precision']['source_bits']),
                                   ('independent-audit',6144,source['precision']['audit_bits'])]:
        baseline = next(row for row in measured['stages'] if row['stage']==name)
        peak = baseline['process_peak_committed_bytes']
        quadratic = peak*ratio**2
        linear_limb = quadratic*Q(new_bits,old_bits)
        rows.append({'stage':name,'measured_baseline_wall_seconds':str(baseline['new_stage_wall_seconds']),
                     'measured_baseline_peak_committed_bytes':peak,
                     'baseline_precision_bits':old_bits,'target_starting_precision_bits':new_bits,
                     'quadratic_only_scenario_bytes':str(quadratic),
                     'quadratic_times_precision_scenario_bytes':str(linear_limb),
                     'scenario_assumptions':'same live allocation count per matrix shape; latter additionally assumes linear mantissa storage in working precision',
                     'scenario_is_not_measured_target_peak_or_admission_bound':True})
    first_geometric = 2
    while (2*first_geometric+1)*(2*first_geometric+3)<=source['R']**2:
        first_geometric += 2
    result={'format':'t1-qualified-shape-and-conditional-cost-v2',
            'status':'QUANTIFIED_REFERENCE_POLICY_OBSTACLE_WITH_UNVALIDATED_RESOURCE_SCENARIOS',
            'source_sha256':sha(args.source),'audit_sha256':sha(args.audit),
            'measurements_sha256':MEASUREMENTS_SHA256,'program_sha256':sha(Path(__file__)),
            'sanitized_report_sha256':measured['sanitized_report_sha256'],
            'support':'1','N':N,'M':M,'K':source['K'],
            'exact_shape':{'N_ratio':str(ratio),'dense_square_ratio':str(ratio**2),
                           'six_triangular_entry_ratio':str(entries),
                           'dense_cubic_ratio':str(ratio**3),'translation_cell_ratio':str(cells),
                           'cell_times_dense_cubic_work_index':str(cells*ratio**3),
                           'first_even_N_with_geometric_ratio_below_one':first_geometric},
            'conditional_memory_scenarios':rows,
            'measured_baseline_memory_ceiling_bytes':measured['memory_budget_bytes'],
            'baseline_reserve_bytes':measured['reserve_bytes'],
            'target_memory_measured':False,'validated_peak_memory_estimator':False,
            'target_runtime_measured':False,'target_wall_time_prediction':None,
            'interpretation':'The inherited sufficient reference policy forces a much larger declared shape. These scenarios flag a planning obstacle; they do not prove that every implementation exceeds host RAM, that the selected matrix is negative, or that another reference or parameter policy fails.',
            'target_matrix_computed':False,'target_positivity_proved':False,
            'production_admission':False,'RH_status':'UNRESOLVED'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'exact_shape':result['exact_shape'],
                      'target_peak_or_runtime_measured':False}))


if __name__=='__main__':
    main()
