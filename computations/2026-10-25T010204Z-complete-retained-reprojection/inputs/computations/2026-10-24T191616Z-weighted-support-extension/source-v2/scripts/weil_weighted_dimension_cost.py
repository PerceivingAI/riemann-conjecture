"""Conditional fixed-support Schur completeness and its norm-only cutoff cost.

A known full-form gap is a premise, never a way to prove a new support positive.
This computes exact conservative thresholds, not actual required dimensions.
"""
from fractions import Fraction as Q
import argparse
import hashlib
import json
from pathlib import Path

from flint import arb, ctx
from scripts import weil_weighted_extension_diagnostics as diagnostics
from scripts.cert.constants import c_T_enclosure
from scripts.cert.multi_prime_legendre_schur import _residual_rho
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms


def derive() -> dict:
    source_path = diagnostics.BASE/'source-m626-v1.json.gz'
    result_path = diagnostics.BASE/'assessment-m626-v1.json'
    packet = diagnostics.read_json(source_path)
    result = diagnostics.read_json(result_path)
    if result['packet_sha256'] != hashlib.sha256(source_path.read_bytes()).hexdigest():
        raise ValueError('reference witness/source binding changed')
    gaps = []
    n = packet['dimension']
    for parity, block in enumerate(result['blocks']):
        if block['parity'] != parity or block['positive_lower_witness'] is None:
            raise ValueError('missing accepted reference-gap premise')
        proof = block['positive_lower_witness']
        indices = list(range(parity, n, 2))
        trace = sum((Q(value*value, proof['denominator']**2)*Q(2, 2*indices[j]+1)
                     for row in proof['numerators'] for j, value in enumerate(row)), Q())
        gaps.append(Q(proof['exact_margin'])/trace)
    g, mu = min(gaps), Q(packet['mu_reference_exact'])
    if g <= 0 or mu <= 0:
        raise ValueError('positive reference/tail premises are missing')
    with ctx.workprec(512):
        t = Q(*packet['support'])
        terms = enumerate_active_prime_power_terms(t.numerator, t.denominator, 512)
        if [term.m for term in terms] != [2, 3] or not all(1 < term.tau < 2 for term in terms):
            raise ValueError('first-window norm premises are missing')
        v = diagnostics.upper(arb.pi()/2)
        p = diagnostics.upper(sum((term.coefficient for term in terms), arb(0)))
        rho = diagnostics.upper(_residual_rho(diagnostics.ar(t), packet['residual_order']))
        cost = diagnostics.upper(c_T_enclosure(512, t.numerator, t.denominator)
                                 +_residual_rho(diagnostics.ar(t), packet['residual_order'])
                                 +sum((term.coefficient for term in terms), arb(0)))
        b = diagnostics.cross_norm_bound(t, packet['residual_order'])
    full_gap = min(g/(1+2*(b/mu)**2), mu/2)
    flat = cost+b*b/full_gap
    grouped = cost+3*(v*v+p*p+rho*rho)/full_gap
    values = {'reference_gap': g, 'tail_mu': mu, 'full_cross_norm_upper': b,
              'full_scaled_form_gap_lower': full_gap,
              'scalar_cost_upper': cost,
              'flat_log_N_plus_1_sufficient_threshold': flat,
              'factor3_log_N_plus_1_sufficient_threshold': grouped}
    return {'format': 'research-weighted-conditional-dimension-cost-v1',
            'support': packet['support'],
            'values': {key: {'exact': str(value), 'display': float(value)} for key, value in values.items()},
            'premises': 'Existing accepted C0084 reference/tail gaps, C0085 uniform cross norm, C0063/C0072 domain-safe closed scaled form. This is not a fresh replay of C0084.',
            'threshold_meaning': 'log(N+1)>threshold is sufficient for the indicated exact full-source criterion, using H_N>=log(N+1). Not a necessary dimension bound or a fixed-K exporter guarantee.',
            'baseline_source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
            'baseline_result_sha256': hashlib.sha256(result_path.read_bytes()).hexdigest(),
            'analysis_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'warning': 'No new support positivity, unbounded family, originality, production admission or RH result follows.'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(derive(), stream, indent=2, allow_nan=False)
        stream.write('\n')
    print('CONDITIONAL_DIMENSION_COST_COMPLETE')


if __name__ == '__main__':
    main()
