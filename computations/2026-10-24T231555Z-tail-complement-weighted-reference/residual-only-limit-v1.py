"""Assess an optimistic scalar reference, not a certified tail domination.

Keep the full source and residual error. Only the residual norm charge in the
hypothetical complement is set to zero. This upper-envelopes every improvement
of that nonnegative charge with the same c_T and arithmetic norm budget.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flint import arb, ctx
from scripts import verify_combined_schur_analytic_entries as native
from scripts import verify_weighted_low_space as exact
from scripts import weil_tail_complement_assessment as experiment
from scripts import weil_weighted_support_extension as legacy

SCALAR_PATH = 'computations/2026-10-24T224948Z-tail-restricted-residual/data/scalars-v1.json'
SCALAR_SHA = '65cc22df9e5edfbaebd9b183edbc29b179c7d3474731e24170cc9abc543a0b9a'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    packet, sha, audit_sha = experiment.load_accepted(args.packet, args.audit)
    result = json.loads(args.result.read_bytes())
    if experiment.assess(packet, sha, audit_sha, result) != result:
        raise ValueError('original exact assessment does not replay')
    raw = (experiment.ROOT/SCALAR_PATH).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SCALAR_SHA:
        raise ValueError('prior scalar bytes changed')
    scalar = json.loads(raw)
    n = packet['dimension']
    optimistic = exact._harmonic(n)-Q(scalar['scalars']['c_T'][0])-Q(scalar['scalars']['arithmetic'][0])
    with ctx.workprec(1536):
        t = native.qarb(Q(*packet['support']))
        exact_zero_charge = (native.qarb(native.harmonic(n))-(2*arb.pi()*t).log()
                             -arb.const_euler()-arb(2).log()/arb(2).sqrt()
                             -arb(3).log()/arb(3).sqrt())
        lower, upper = native.endpoints(exact_zero_charge)
        if not optimistic >= upper > Q(packet['mu_reference_exact']) > 0:
            raise ValueError('optimistic scalar envelope was not independently contained')
    hypothetical = legacy.arithmetic_packet(packet)
    hypothetical['mu_reference_exact'] = str(optimistic)
    matrices = exact.weighted_matrices(hypothetical)
    checks = []
    for block in result['blocks']:
        check = exact.directional_upper(hypothetical, matrices, [Q(x) for x in block['trial']])
        if Q(check['reference_upper']) >= 0:
            raise ValueError('optimistic reference direction is not certified negative')
        checks.append({'parity': block['parity'], 'directional_check': check})
    experiment.save(args.output, {
        'status': 'NEGATIVE_BOTH_OPTIMISTIC_REFERENCE_DIRECTIONS',
        'packet_sha256': sha, 'audit_sha256': audit_sha,
        'result_sha256': hashlib.sha256(args.result.read_bytes()).hexdigest(),
        'scalar_sha256': SCALAR_SHA,
        'optimistic_mu_upper_exact': str(optimistic),
        'independent_zero_charge_mu_interval': [str(lower), str(upper)],
        'independent_precision': 1536, 'blocks': checks,
        'scope': 'Counterfactual reference only. Full source R_T and complete residual error retained; no new tail domination or Weil negativity.',
    })
    print(json.dumps({'status': 'NEGATIVE_BOTH_OPTIMISTIC_REFERENCE_DIRECTIONS',
                      'optimistic_mu_display': float(optimistic),
                      'directional_upper_displays': [float(Q(b['directional_check']['reference_upper'])) for b in checks]}))


if __name__ == '__main__':
    main()
