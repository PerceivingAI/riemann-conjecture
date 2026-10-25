"""Coupled-tail consequences of retained research bounds; no theorem admission."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

from flint import fmpq, fmpq_mat
from scripts import weil_complete_reprojection as retained
from scripts import verify_weighted_low_space as exact
from scripts import verify_weighted_low_space_inputs as validation
from scripts import weil_weighted_extension_diagnostics as diagnostics

ROOT = Path(__file__).resolve().parents[1]
BITS, GRID, N, M = 352, 80, 20, 312
FORMAT = 'research-coupled-tail-comparison-v1'
BASE = 'computations/2026-10-25T010204Z-complete-retained-reprojection/'
PINS = {
    BASE+'manifest.json': '6a6fb19db869e6d93a33fa691171571b45aeb23fa31f28a23592363378913bba',
    BASE+'data/original-v2-gate-v1.json': '9e7837dceefc3b3b35d0700077aec2157348c3610a07a82ccb9c76d83567ffcf',
    BASE+'data/complete-reference-v1.json': '35468a0d04b26d3f94aff718f90009a42f260e7caa80dafbf50e56f71bce37c3',
    BASE+'data/independent-audit-v1.json': '6729834e3c35bf85faf735da87865ea7db28636b90c4d8a2b46fbbb1f234920e',
}
SOURCES = ('scripts/weil_coupled_tail_comparison.py',
           'scripts/verify_coupled_tail_comparison.py', *retained.SOURCE_PATHS)
SCOPE = 'Inherited-source directional coupled-tail comparison; full outside tail paid; no new support, full spectral minimum or production admission.'


def fingerprint() -> dict:
    return {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}


def fq(value: Q) -> fmpq:
    return fmpq(value.numerator, value.denominator)


def fraction(value) -> Q:
    return Q(int(value.p), int(value.q))


def rounded(value: Q, up: bool) -> str:
    numerator = (value*(1 << BITS)).__ceil__() if up else (value*(1 << BITS)).__floor__()
    return str(Q(numerator, 1 << BITS))


def column(values: list[Q]) -> fmpq_mat:
    return fmpq_mat([[fq(v)] for v in values])


def norm(values: list[Q], start: int = 0) -> Q:
    return sum((v*v*Q(2, 2*j+1) for j, v in enumerate(values, start)), Q())


def quadratic(matrix: fmpq_mat, values: list[Q]) -> Q:
    z = column(values)
    return fraction((z.transpose()*matrix*z)[0, 0])


def schur_residual(lower: fmpq_mat, values: list[Q], split: int, gap: Q) -> tuple[Q, Q, Q]:
    """A trial minimum minus its certified dual residual, with physical masses."""
    validation.require(gap > 0 and 0 < split < len(values), 'invalid certified elimination')
    w = column(values); residual = lower*w
    squared = sum((fraction(residual[j, 0])**2*Q(2*j+1, 2)
                   for j in range(split, len(values))), Q())
    value = fraction((w.transpose()*residual)[0, 0])
    return value, squared, value-squared/gap


def finite_bracket(a_lo: Q, a_hi: Q, q_lo: Q, q_hi: Q, residual_squared: Q,
                   delta: Q, nz: Q, nv: Q, mu: Q) -> tuple[Q, Q, Q]:
    """Enclose the finite true-tail inverse, never the infinite inverse."""
    validation.require(mu > 0 and min(residual_squared, delta, nz, nv) >= 0,
                       'invalid finite response bounds')
    error = delta*(2*exact._sqrt(nz*nv, BITS, True)+nv)
    residual = exact._sqrt(residual_squared, BITS, True)+delta*exact._sqrt(nz+nv, BITS, True)
    return max(Q(), a_lo-q_hi-error), a_hi-q_lo+error+residual*residual/mu, residual


def load_context() -> dict:
    """Restore accepted upstream authority, without changing either old validator."""
    decoded = {p: validation.decode_json(retained.pinned(p, h)) for p, h in PINS.items()}
    reference = decoded[BASE+'data/complete-reference-v1.json']
    receipt = decoded[BASE+'data/independent-audit-v1.json']
    validation.require(receipt['status'] == 'RETAINED_INPUT_CONSEQUENCES_ACCEPTED'
                       and receipt['report_sha256'] == PINS[BASE+'data/complete-reference-v1.json']
                       and reference['status'] == receipt['selected_status'] == 'NEGATIVE_REFERENCE_DIRECTION'
                       and reference['dimension'] == 20, 'unaccepted complete20 reference')
    packet, native, _, _, identity = retained.load_inputs(ROOT/(BASE+'data/original-v2-gate-v1.json'))
    del native
    original = validation.decode_json(retained.pinned(retained.OLD_DATA+'extension-assessment-v1.json',
                                                      retained.INPUTS[retained.OLD_DATA+'extension-assessment-v1.json']))
    mapped = {**packet, 'heads': {'V': packet['heads']['V'], 'P': packet['heads']['P'], 'R32': packet['heads']['RK']}}
    matrices = exact.weighted_matrices(mapped)
    charge = diagnostics.uniform_residual(matrices['delta'], Q(packet['cross_norm_upper']), matrices['mu'])
    validation.require(str(charge) == original['residual_allowance'], 'original complete charge changed')
    lower = matrices['lower']
    for j in range(M):
        lower[j, j] += fq((matrices['residual']-charge)*Q(2, 2*j+1))
    gaps = []
    for parity in (0, 1):
        indices = list(range(parity, M, 2))
        block = original['blocks'][parity]
        validation.require(block['parity'] == parity and block['positive_lower_witness'] is not None,
                           'missing original complete parity proof')
        compressed = fmpq_mat([[lower[i, j] for j in indices] for i in indices])
        proof = block['positive_lower_witness']
        margin = exact._verify_congruence(compressed, proof)
        trace = sum((Q(v, proof['denominator'])**2*Q(2, 2*indices[j]+1)
                     for row in proof['numerators'] for j, v in enumerate(row)), Q())
        gap = margin/trace
        validation.require(str(margin) == proof['exact_margin']
                           and str(gap) == block['mass_normalized_gap'], 'original exact coercivity changed')
        gaps.append(gap)
    a_minus, a_plus, _ = exact._order_bounds(packet['matrices']['A_K'], BITS)
    midpoint = (a_minus+a_plus)/2
    radii = fmpq_mat(M, M)
    for i, row in enumerate(packet['matrices']['A_K']):
        for offset, pair in enumerate(row):
            j = i+offset
            radii[i, j] = radii[j, i] = fmpq(pair[1]-pair[0], 1 << (BITS+1))
    validation.require(identity['origin_sha256'] == PINS[BASE+'data/original-v2-gate-v1.json'],
                       'reference origin mismatch')
    return {'packet': packet, 'reference': reference, 'lower': lower, 'gaps': gaps,
            'bindings': {**identity['input_sha256'], **PINS},
            'a_minus': a_minus, 'a_plus': a_plus, 'midpoint': midpoint, 'radii': radii}


def quantize(value: Q) -> Q:
    return Q((value*(1 << GRID)+Q(1, 2)).__floor__(), 1 << GRID)


def responses(context: dict, z: list[Q], parity: int) -> tuple[list[Q], list[Q], list[Q]]:
    import numpy as np
    indices = list(range(N+parity, M, 2))
    low = list(range(parity, N, 2))
    def solve(matrix, sign):
        a = np.array([[float(matrix[i, j]) for j in indices] for i in indices])
        b = np.array([float(sum((fraction(matrix[i, j])*z[j] for j in low), Q())) for i in indices])
        values = np.linalg.solve(a, sign*b)
        result = [Q() for _ in range(M-N)]
        for i, value in zip(indices, values, strict=True):
            result[i-N] = quantize(Q.from_float(float(value)))
        return result
    y = solve(context['lower'], -1)
    v = solve(context['midpoint'], 1)
    mu = Q(context['reference']['mu_reference_exact'])
    weights = retained.weights(mu, N, M-1)
    harmonic = [Q() for _ in range(M-N)]
    for i in indices:
        b = sum((fraction(context['midpoint'][i, j])*z[j] for j in low), Q())
        harmonic[i-N] = quantize(b*Q(2*i+1, 2)*weights[i-N])
    return y, v, harmonic


def stiffness(context: dict, harmonic: list[Q], delta: Q) -> dict:
    midpoint, radii = context['midpoint'], context['radii']
    weights = retained.weights(Q(context['reference']['mu_reference_exact']), N, M-1)
    diagonal = Q(); diagonal_radius = Q()
    for j, value in enumerate(harmonic, N):
        diagonal += value*value*(fraction(midpoint[j, j])-Q(2, 2*j+1)/weights[j-N])
        diagonal_radius += value*value*fraction(radii[j, j])
    h = [Q()]*N+harmonic
    total_mid = quadratic(midpoint, h)
    raw_diag = sum((value*value*fraction(midpoint[j, j]) for j, value in enumerate(harmonic, N)), Q())
    off = total_mid-raw_diag
    full_radius = quadratic(radii, [abs(v) for v in h])
    off_radius = full_radius-diagonal_radius
    total_error = full_radius+delta*norm(h)
    return {'stiffness_diagonal_lower': rounded(diagonal-diagonal_radius, False),
            'stiffness_diagonal_upper': rounded(diagonal+diagonal_radius, True),
            'stiffness_offdiagonal_lower': rounded(off-off_radius, False),
            'stiffness_offdiagonal_upper': rounded(off+off_radius, True),
            'stiffness_full_lower': rounded(diagonal+off-total_error, False),
            'stiffness_full_upper': rounded(diagonal+off+total_error, True)}


def analyze(prior: dict | None = None) -> dict:
    tick = time.perf_counter(); before = fingerprint(); context = load_context()
    lower, midpoint, radii = context['lower'], context['midpoint'], context['radii']
    delta = Q(context['packet']['delta'][1], 1 << BITS)
    mu = Q(context['reference']['mu_reference_exact']); rows = []
    for parity in (0, 1):
        old = context['reference']['blocks'][parity]; z = list(map(Q, old['trial']))
        if prior is None:
            y, v, harmonic = responses(context, z, parity)
        else:
            row = prior['rows'][parity]
            validation.require(row['parity'] == parity and row['trial'] == old['trial'], 'changed preserved trial')
            y, v, harmonic = (list(map(Q, row[name])) for name in ('coupled_minimizer', 'finite_response', 'harmonic_response'))
        for values in (y, v, harmonic):
            validation.require(len(values) == M-N and all((q*(1 << GRID)).denominator == 1 for q in values)
                               and all(not values[j-N] for j in range(N+1-parity, M, 2)), 'invalid coupled response')
        nz, nv = norm(z), norm(v, N)
        q, residual_squared, schur = schur_residual(lower, z+y, N, context['gaps'][parity])
        a_z = z+[Q()]*(M-N); galerkin = z+[-q for q in v]
        a_lo_k = quadratic(context['a_minus'], a_z); a_hi_k = quadratic(context['a_plus'], a_z)
        q_lo_k = quadratic(context['a_minus'], galerkin); q_hi_k = quadratic(context['a_plus'], galerkin)
        a_lo = Q(rounded(a_lo_k-delta*nz, False)); a_hi = Q(rounded(a_hi_k+delta*nz, True))
        q_up = Q(rounded(q_hi_k+delta*(nz+nv), True)); s_lo = Q(rounded(schur, False))
        r_center = midpoint*column([-q for q in z]+v)
        r_radius = radii*column([abs(q) for q in z+v])
        r_squared = sum(((abs(fraction(r_center[j, 0]))+fraction(r_radius[j, 0]))**2*Q(2*j+1, 2)
                         for j in range(N, M)), Q())
        finite_lo, finite_hi, finite_r = finite_bracket(a_lo_k, a_hi_k, q_lo_k, q_hi_k,
                                                      r_squared, delta, nz, nv, mu)
        finite_lo = Q(rounded(finite_lo, False)); finite_hi = Q(rounded(finite_hi, True))
        inverse_lo = max(Q(), a_lo-q_up); inverse_hi = a_hi-s_lo
        reference_up = Q(old['directional_check']['reference_upper'])
        validation.require(s_lo <= q_up and 0 <= inverse_lo <= inverse_hi
                           and finite_lo <= finite_hi and finite_lo <= inverse_hi,
                           'contradictory complete coupled comparison')
        rows.append({'parity': parity, 'trial': old['trial'],
                     'coupled_minimizer': list(map(str, y)), 'finite_response': list(map(str, v)),
                     'harmonic_response': list(map(str, harmonic)), 'g_exact': str(context['gaps'][parity]),
                     'physical_norm_exact': str(nz), 'lower_quadratic': rounded(q, False),
                     'residual_dual_squared': rounded(residual_squared, True),
                     'residual_penalty': rounded(residual_squared/context['gaps'][parity], True),
                     'true_schur_lower': str(s_lo), 'galerkin_form_upper': str(q_up),
                     'a_lower': str(a_lo), 'a_upper': str(a_hi),
                     'true_inverse_lower': rounded(inverse_lo, False), 'true_inverse_upper': rounded(inverse_hi, True),
                     'reference_upper': str(reference_up), 'gain_lower': rounded(s_lo-reference_up, False),
                     'finite_inverse_lower': str(finite_lo), 'finite_inverse_upper': str(finite_hi),
                     'outside_excess_upper': rounded(inverse_hi-finite_lo, True),
                     'finite_residual_norm_upper': rounded(finite_r, True), **stiffness(context, harmonic, delta)})
    validation.require(fingerprint() == before, 'comparison source changed during assessment')
    return {'format': FORMAT, 'source_sha256': before, 'input_sha256': context['bindings'],
            'support': [1353, 2048], 'dimension': N, 'coupled_boundary': M, 'inherited_head_boundary': 1018,
            'residual_order': 38, 'bits': BITS, 'rows': rows,
            'status': 'BOTH_TRUE_SCHUR_DIRECTIONS_POSITIVE' if all(Q(r['true_schur_lower']) > 0 for r in rows)
                      else 'DIRECTIONAL_COMPARISON_INCONCLUSIVE',
            'scope': SCOPE, 'elapsed_seconds': time.perf_counter()-tick}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('analyze', 'replay'))
    parser.add_argument('--result', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    validation.require(not args.output.exists(), 'refusing previous research output')
    prior = validation.decode_json(args.result.read_bytes()) if args.operation == 'replay' else None
    value = analyze(prior)
    if prior is not None:
        left, right = dict(value), dict(prior); left.pop('elapsed_seconds'); right.pop('elapsed_seconds')
        validation.require(left == right, 'changed coupled-tail consequence')
        value = {'status': 'EXACT_COUPLED_TAIL_REPLAY_PASS',
                 'report_sha256': hashlib.sha256(args.result.read_bytes()).hexdigest()}
    retained.save(args.output, value)
    print(json.dumps({'status': value['status'], 'output': str(args.output)}))


if __name__ == '__main__':
    main()
