"""Account for a matched dense coupled-tail rearrangement, without a new solver."""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

from flint import fmpq, fmpq_mat

BUNDLE = Path(__file__).resolve().parent
ORIGINAL = 'computations/2026-10-24T191616Z-weighted-support-extension/'
BASELINE = 'computations/2026-10-24T153012Z-weighted-reference-continuation/data/source-m626-v1.json.gz'
DIAGNOSTIC = 'computations/2026-10-25T130058Z-coupled-tail-comparison/'


def submatrix(matrix, rows, cols):
    return fmpq_mat([[matrix[i, j] for j in cols] for i in rows])


def schur(matrix, retained):
    low = list(range(retained)); tail = list(range(retained, matrix.nrows()))
    a = submatrix(matrix, low, low); b = submatrix(matrix, low, tail)
    c = submatrix(matrix, tail, tail)
    return a-b*c.inv()*b.transpose()


def controls():
    # L,E,F have one coordinate each. Outside2 is the same in both orders.
    full = fmpq_mat([[4, 1, 0], [1, 2, 1], [0, 1, 2]])
    h = schur(full, 2)
    direct = schur(full, 1)[0, 0]
    nested = schur(h, 1)[0, 0]
    assert direct == nested == fmpq(10, 3)
    bare_finite = fmpq(4)-fmpq(1, 2)
    assert bare_finite > nested  # Dropping F would overstate the lower.
    indefinite = fmpq_mat([[1, 2], [2, -1]])
    false_low = schur(indefinite, 1)[0, 0]
    assert false_low == 5 and indefinite[1, 1] < 0 and indefinite.det() < 0
    changed_outside = fmpq_mat([[4, 1, 0], [1, 2, 1], [0, 1, 1]])
    changed = schur(changed_outside, 1)[0, 0]
    assert changed == 3 and changed != nested
    enclosure = h-fmpq_mat([[fmpq(1, 10), 0], [0, fmpq(1, 10)]])
    bounded = schur(enclosure, 1)[0, 0]
    assert bounded == fmpq(223, 70) and bounded < nested
    return {'matched_outside_direct': str(direct), 'matched_outside_nested': str(nested),
            'bare_finite_overstatement': str(bare_finite),
            'positive_low_schur_with_negative_tail_counterexample': str(false_low),
            'changed_outside_is_a_different_criterion': str(changed),
            'conservative_enclosure_lower': str(bounded),
            'control_count': 4, 'status': 'EXACT_ALGEBRA_CONTROLS_PASS'}


def inventory(packet):
    n, m = packet['dimension'], packet['boundary']
    matrices = packet['matrices']; heads = packet['heads']
    assert set(matrices) == {'A_K', 'G_K'} and len(heads) == 3
    low_count = 0
    for matrix in matrices.values():
        assert len(matrix) == n and all(len(row) == n-i for i, row in enumerate(matrix))
        low_count += sum(map(len, matrix))
    head_count = 0
    for rows in heads.values():
        assert len(rows) == m-n and all(len(row) == n for row in rows)
        head_count += sum(map(len, rows))
    scalar_count = 2+int('cross_norm_upper' in packet)
    return {'dimension': n, 'boundary': m, 'low_and_gram_slots': low_count,
            'signed_head_slots': head_count, 'scalar_slots': scalar_count,
            'total_slots': low_count+head_count+scalar_count,
            'count_scope': 'Serialized interval slots including exact parity zeros, not distinct transcendental integrals'}


def dense_model(m, n):
    assert 0 < n < m
    e = m-n
    full = Q(m**3, 3)
    split = Q(e**3, 3)+e*e*n+e*n*n+Q(n**3, 3)
    full_entries = m*(m+1)//2
    split_entries = e*(e+1)//2+e*n+n*(n+1)//2
    assert full == split and full_entries == split_entries
    return {'parity_order': m, 'low_order': n, 'coupled_order': e,
            'two_parity_dense_leading_work_full': str(2*full),
            'two_parity_dense_leading_work_split': str(2*split),
            'two_parity_triangular_entries_full': 2*full_entries,
            'two_parity_triangular_entries_split': 2*split_entries,
            'scope': 'Dense block-Cholesky leading arithmetic model and parameter identity, not measured runtime, serialized existing witness size or a lower bound for structured algorithms'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=BUNDLE.parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('refusing a previous research output')
    pins = json.loads((BUNDLE/'inputs/manifest.json').read_bytes())
    def load(relative):
        raw = (args.root/relative).read_bytes()
        if hashlib.sha256(raw).hexdigest() != pins[relative]:
            raise ValueError('retained bytes changed: '+relative)
        return json.loads(gzip.decompress(raw) if relative.endswith('.gz') else raw)
    # Check every declared input, not only those decoded below.
    for relative, expected in pins.items():
        if hashlib.sha256((args.root/relative).read_bytes()).hexdigest() != expected:
            raise ValueError('input binding changed: '+relative)
    original = inventory(load(ORIGINAL+'data/extension-source-v1.json.gz'))
    baseline = inventory(load(BASELINE))
    assert original['total_slots'] == 758475 and baseline['total_slots'] == 287042
    assert (original['dimension'], original['boundary']) == (312, 1018)
    original_manifest = load(ORIGINAL+'manifest.json')
    original_members = {row['path']: row['sha256'] for row in original_manifest['members']}
    timings = {}
    for stage in ('source', 'audit', 'assessment', 'replay'):
        relative = ORIGINAL+f'data/{stage}-run.json'
        assert pins[relative] == original_members[f'data/{stage}-run.json']
        receipt = load(relative)
        assert receipt['exit_code'] == 0 and receipt['owned_exit_confirmed'] is True
        timings[stage] = receipt['elapsed_seconds']
    comparison = load(DIAGNOSTIC+'data/comparison-v1.json')
    receipt = load(DIAGNOSTIC+'data/independent-audit-v1.json')
    assert receipt['status'] == 'INHERITED_INPUT_CONSEQUENCES_ACCEPTED'
    assert receipt['report_sha256'] == pins[DIAGNOSTIC+'data/comparison-v1.json']
    assert comparison['coupled_boundary'] == original['dimension']
    assert comparison['inherited_head_boundary'] == original['boundary']
    assert all(comparison['input_sha256'][p] == pins[p] for p in
               (ORIGINAL+'data/extension-source-v1.json.gz', ORIGINAL+'data/extension-assessment-v1.json'))
    observed = load(DIAGNOSTIC+'data/coupled-comparison.run.json')
    assert observed['exit_code'] == 0
    growth = Q(original['total_slots'], baseline['total_slots'])
    result = {'format': 'research-coupled-route-assessment-v1',
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'input_sha256': pins, 'exact_controls': controls(),
              'baseline_inventory': baseline, 'current_inventory': original,
              'dense_accounting': dense_model(156, 10),
              'two_observation_slot_ratio_exact': str(growth),
              'two_observation_ratio_is_not_a_scaling_law': True,
              'recorded_fresh_pipeline_seconds': timings,
              'recorded_fresh_pipeline_total_seconds': sum(timings.values()),
              'recorded_inherited_comparison_seconds': observed['elapsed_seconds'],
              'fresh_coupled_pipeline_seconds': None,
              'timings_are_different_workloads_not_a_speedup_comparison': True,
              'comparison_still_depends_on_full312_analytical_inputs': True,
              'new_support_or_new_outside_reference_evaluated': False,
              'environment': {'python': sys.version, 'python_flint': importlib.metadata.version('python-flint')},
              'scope': 'Matched-criterion algebra and inherited data/work accounting; no new positivity run, theorem admission or global no-go',
              'status': 'MATCHED_CRITERION_AND_COST_ACCOUNTING_PASS'}
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'status': result['status'], 'source_slots': original['total_slots'],
                      'full_parity_order': 156, 'retained_tail_order': 146, 'low_order': 10,
                      'dense_work_identity': result['dense_accounting']['two_parity_dense_leading_work_full'],
                      'fresh_pipeline_seconds': result['recorded_fresh_pipeline_total_seconds'],
                      'inherited_comparison_seconds': observed['elapsed_seconds']}))


if __name__ == '__main__':
    main()
