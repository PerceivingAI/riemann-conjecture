"""Weighted-reference loss decomposition and geometric support selection.

Research only. Selection uses overlap and error budgets, never a matrix sign.
Historical sources, witnesses and theorem admission are not changed.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

from flint import acb, arb, ctx, fmpq, fmpq_mat
from scripts import verify_weighted_low_space as exact
from scripts import weil_weighted_low_space as source
from scripts.cert.constants import c_T_enclosure
from scripts.cert.multi_prime_legendre_schur import _residual_rho
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms
from scripts.cert.residual_kernel import _suzuki_residual_tail_radius
from scripts.verify_combined_schur_analytic_entries import endpoints

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'computations/2026-10-24T153012Z-weighted-reference-continuation/data'
EARLIER = ROOT/'computations/2026-10-24T124142Z-weighted-low-space/data'
BITS = 352


def read_json(path: Path) -> dict:
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def ar(value: Q) -> arb:
    return arb(value.numerator)/value.denominator


def upper(value: arb) -> Q:
    return exact._up(endpoints(value)[1], BITS)


def cross_norm_bound(t: Q, order: int) -> Q:
    """Hilbert cross-potential bound plus complete arithmetic/residual norms."""
    terms = enumerate_active_prime_power_terms(t.numerator, t.denominator, 512)
    if [term.m for term in terms] != [2, 3] or not all(1 < term.tau < 2 for term in terms):
        raise ValueError('cross norm bound requires certified first-window topology')
    return upper(arb.pi()/2+sum((term.coefficient for term in terms), arb(0))
                 + _residual_rho(ar(t), order))


def uniform_residual(delta: Q, bound: Q, mu: Q) -> Q:
    if delta < 0 or bound < 0 or mu <= 0:
        raise ValueError('invalid residual norm parameters')
    return exact._up(delta*(1+2*bound/mu)+delta*delta/mu, BITS)


def select_parameters() -> dict:
    """Double the p=3 overlap, then preserve three independently valid budgets."""
    baseline = read_json(BASE/'source-m626-v1.json.gz')
    assessment = read_json(BASE/'assessment-m626-v1.json')
    mu = Q(baseline['mu_reference_exact'])
    residual_limit = Q(assessment['residual_allowance'])
    with ctx.workprec(512):
        t0 = arb(3)/5
        logarithm = arb(3).log()
        overlap0 = 2-logarithm/t0
        target = t0*logarithm/(2*(logarithm-t0))
        lo, hi = endpoints(target)
        for bits in range(1, 64):
            integer = (lo*(1 << bits)).__floor__()
            if integer != (hi*(1 << bits)).__floor__():
                continue
            t = Q(integer, 1 << bits)
            overlap = 2-logarithm/ar(t)
            if overlap >= arb(199)/100*overlap0 and overlap <= 2*overlap0:
                break
        else:
            raise ValueError('cannot resolve geometric target')
        if not (arb(3).log() < 2*ar(t) < arb(4).log() and 2*ar(t) < arb.pi()):
            raise ValueError('selected support left the analytic/arithmetic window')
        order = 32
        while True:
            delta = upper(2*ar(t)*_suzuki_residual_tail_radius(acb(2*ar(t)), order))
            bound = cross_norm_bound(t, order)
            residual = uniform_residual(delta, bound, mu)
            if residual <= residual_limit:
                break
            order += 2
        terms = enumerate_active_prime_power_terms(t.numerator, t.denominator, 512)
        cost = c_T_enclosure(512, t.numerator, t.denominator)+_residual_rho(ar(t), order)
        cost += sum((term.coefficient for term in terms), arb(0))
        cost_lo, cost_hi = endpoints(cost)
        n = 192
        harmonic = exact._harmonic(n)
        while harmonic-cost_hi < mu:
            harmonic += Q(1, n+1)+Q(1, n+2)
            n += 2
        baseline_increment = exact._harmonic(626)-exact._harmonic(192)
        m = n+order
        increment = exact._harmonic(m)-harmonic
        while increment < baseline_increment:
            increment += Q(1, m+1)+Q(1, m+2)
            m += 2
        old_delta = Q(baseline['delta'][1], 1 << BITS)
        old_bound = cross_norm_bound(Q(3, 5), 32)
        return {
            'format': 'research-weighted-geometric-selection-v1',
            'support': [t.numerator, t.denominator], 'dimension': n,
            'residual_order': order, 'boundary': m, 'bits': BITS,
            'active_terms': [2, 3], 'mu_reference_exact': str(mu),
            'basis': 'ordinary_unnormalized_legendre',
            'source_precision': 256*((4*n+512+255)//256),
            'head_precision': 256*((4*m+512+255)//256),
            'target_support_interval': [str(lo), str(hi)],
            'dyadic_support_resolution_bits': bits,
            'overlap_ratio_interval': [str(q) for q in endpoints(overlap/overlap0)],
            'complement_lower_exact': str(harmonic-cost_hi),
            'complement_upper_exact': str(harmonic-cost_lo),
            'chosen_delta_upper': str(delta), 'cross_norm_upper': str(bound),
            'residual_allowance_upper': str(residual),
            'residual_allowance_limit': str(residual_limit),
            'baseline_uniform_residual_upper': str(uniform_residual(old_delta, old_bound, mu)),
            'baseline_weight_upper': str(exact._up(1/(mu+baseline_increment), BITS)),
            'selected_weight_upper': str(exact._up(1/(mu+increment), BITS)),
            'baseline_packet_sha256': hashlib.sha256((BASE/'source-m626-v1.json.gz').read_bytes()).hexdigest(),
            'baseline_result_sha256': hashlib.sha256((BASE/'assessment-m626-v1.json').read_bytes()).hexdigest(),
            'selection_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'selection_rule': 'double p3 overlap to [1.99,2]; least dyadic resolution; least even K preserving full residual budget; least even N preserving original mu; least even m preserving inverse-weight cap',
            'warning': 'Equal inverse-weight caps do not imply equal omitted mass or matrix error. No matrix positivity was used or established.'}


def _quad(matrix: fmpq_mat, z: list[Q]) -> Q:
    column = fmpq_mat([[fmpq(x.numerator, x.denominator)] for x in z])
    value = (column.transpose()*matrix*column)[0, 0]
    return Q(int(value.p), int(value.q))


def _point(packet: dict, matrices: dict, z: list[Q]) -> dict:
    bits, n = packet['bits'], packet['dimension']
    scale = 1 << 48
    nums = [int(x*scale) for x in z]
    if any(Q(num, scale) != x for num, x in zip(nums, z, strict=True)):
        raise ValueError('diagnostic direction is not on its declared exact grid')
    norm = sum((x*x*Q(2, 2*j+1) for j, x in enumerate(z)), Q())
    if norm <= 0:
        raise ValueError('zero diagnostic direction')
    mass_lower = mass_upper = weight_lower = weight_upper = separate_upper = 0
    for offset, k in enumerate(range(n, packet['boundary'])):
        intervals = []
        separate = 0
        for name in ('V', 'P', 'R32'):
            lo = hi = 0
            for num, pair in zip(nums, packet['heads'][name][offset], strict=True):
                a, b = pair[0]*num, pair[1]*num
                lo += min(a, b)
                hi += max(a, b)
            intervals.append((lo, hi))
            separate += max(lo*lo, hi*hi)
        lo, hi = (sum(pair[e] for pair in intervals) for e in (0, 1))
        left = 0 if lo <= 0 <= hi else min(lo*lo, hi*hi)
        right = max(lo*lo, hi*hi)
        mass_lower += left*(2*k+1)
        mass_upper += right*(2*k+1)
        wl, wh = matrices['weight_pairs'][offset]
        weight_lower += left*(2*k+1)*wl
        weight_upper += right*(2*k+1)*wh
        separate_upper += separate*(2*k+1)*wh
    mass_den = 1 << (2*bits+97)
    weight_den = 1 << (3*bits+97)
    gm, gp, _ = exact._order_bounds(packet['matrices']['G_K'], bits)
    gram_lo, gram_hi = _quad(gm, z), _quad(gp, z)
    tail_lo = max(Q(), gram_lo-Q(mass_upper, mass_den))
    tail_hi = gram_hi-Q(mass_lower, mass_den)
    if tail_hi < 0:
        raise ValueError('directional tail upper contradicts nonnegative tail')
    wm = Q(matrices['weight_pairs'][-1][1], 1 << bits)
    output = {
        'mass_norm': norm,
        'low_A_K_lower': _quad(matrices['lower']+matrices['u_plus'], z)+matrices['residual']*norm,
        'low_A_K_upper': _quad(matrices['a_plus'], z),
        'flat_mu_coupling_upper': gram_hi/matrices['mu'],
        'resolved_signed_weighted_head_lower': Q(weight_lower, weight_den),
        'resolved_signed_weighted_head_upper': Q(weight_upper, weight_den),
        'resolved_three_component_factor3_upper': 3*Q(separate_upper, weight_den),
        'omitted_unweighted_mass_lower': tail_lo,
        'omitted_unweighted_mass_upper': tail_hi,
        'omitted_weighted_allowance_upper': wm*tail_hi,
        'matrix_coupling_upper': _quad(matrices['u_plus'], z),
        'full_residual_allowance': matrices['residual']*norm,
        'matrix_reference_lower': _quad(matrices['lower'], z),
    }
    return {key: {'exact': str(value/norm), 'display': float(value/norm)}
            for key, value in output.items() if key != 'mass_norm'}


def baseline_diagnostics() -> dict:
    p626, _, sha626, audit626 = exact._load(BASE/'source-m626-v1.json.gz', BASE/'audit-m626-v2.json.gz')
    p316, _, sha316, audit316 = exact._load(EARLIER/'source-m316-v1.json.gz', EARLIER/'audit-m316-v2.json.gz')
    result626 = read_json(BASE/'assessment-m626-v1.json')
    result316 = read_json(EARLIER/'assessment-m316-native.json')
    m626, m316 = exact.weighted_matrices(p626), exact.weighted_matrices(p316)
    directions = [('626_even', result626['blocks'][0]['trial']),
                  ('626_odd', result626['blocks'][1]['trial']),
                  ('316_odd', result316['blocks'][1]['trial'])]
    rows = []
    for label, values in directions:
        z = [Q(value) for value in values]
        rows.append({'direction': label, 'at316': _point(p316, m316, z),
                     'at626': _point(p626, m626, z)})
    return {'format': 'research-weighted-loss-diagnostics-v1', 'directions': rows,
            'packet_sha256': {'316': sha316, '626': sha626},
            'audit_sha256': {'316': audit316, '626': audit626},
            'A_one_sided_error': str(m626['A_one_sided_error']),
            'U_one_sided_error': str(m626['U_one_sided_error']),
            'residual_allowance': str(m626['residual']),
            'warning': 'Directions are retained proposals, not rigorous minimum eigenvectors. Exact directional bounds and full-space witnesses have different meanings.'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('baseline', 'select'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('refusing to overwrite existing evidence')
    value = baseline_diagnostics() if args.operation == 'baseline' else select_parameters()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'status': 'COMPLETE', 'operation': args.operation,
                      'output': str(args.output)}, allow_nan=False))


if __name__ == '__main__':
    main()
