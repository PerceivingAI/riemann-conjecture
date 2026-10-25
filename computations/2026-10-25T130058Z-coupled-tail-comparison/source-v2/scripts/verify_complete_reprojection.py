"""Audit the complete P20 reprojection from inherited original-version evidence.

Native 512-bit receipt intervals are propagated with Arb1536. This checks new
consequences of retained data, not a fresh analytical source reconstruction.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from math import isqrt
from pathlib import Path
import sys
import time

from flint import arb, ctx, fmpq, fmpq_mat

from scripts import verify_combined_schur_analytic_entries as native
from scripts import verify_residual_tail_bound as tail_validation
from scripts import verify_weighted_low_space as exact
from scripts import verify_weighted_low_space_inputs as validation
from scripts import weil_complete_reprojection as source

ROOT = Path(__file__).resolve().parents[1]
BITS = 352
INPUT_BITS = 512
PRECISION = 1536
N = 20
M = 312
BOUNDARY = 1018
FORMAT = 'research-complete-reprojection-audit-v1'
AUDITOR = 'scripts/verify_complete_reprojection.py'
DEPENDENCIES = (
    AUDITOR,
    'scripts/verify_combined_schur_analytic_entries.py',
    'scripts/verify_residual_tail_bound.py',
    'scripts/verify_weighted_low_space.py',
    'scripts/verify_weighted_low_space_inputs.py',
)
COMPONENTS = ('V', 'P', 'RK')


def _require(condition: bool, label: str) -> None:
    validation.require(condition, label)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot() -> dict[str, str]:
    return {name: _sha(ROOT/name) for name in DEPENDENCIES}


def _input_snapshot(identity: dict) -> dict[str, str]:
    pins = identity['input_sha256']
    _require(type(pins) is dict and bool(pins), 'missing retained input identities')
    observed = {name: _sha(ROOT/name) for name in pins}
    _require(observed == pins, 'retained input bytes changed')
    return observed


def _origins() -> None:
    _require(Path(__file__).resolve() == (ROOT/AUDITOR).resolve(),
             'independent auditor origin changed')
    for module, name in ((native, DEPENDENCIES[1]),
                         (tail_validation, DEPENDENCIES[2]),
                         (exact, DEPENDENCIES[3]),
                         (validation, DEPENDENCIES[4]),
                         (source, 'scripts/weil_complete_reprojection.py')):
        _require(Path(module.__file__).resolve() == (ROOT/name).resolve(),
                 'audit dependency origin changed: '+name)
    _require(validation.REFERENCE_BITS == INPUT_BITS,
             'native receipt precision changed')


def _rational(value) -> Q:
    return Q(int(value.p), int(value.q))


def _round(value: Q, upward: bool, bits: int = BITS) -> Q:
    scale = 1 << bits
    value *= scale
    return Q(value.__ceil__() if upward else value.__floor__(), scale)


def _sqrt(value: Q, upward: bool) -> Q:
    _require(value >= 0, 'negative square-root argument')
    scale = 1 << PRECISION
    integer = isqrt(value.numerator*scale*scale//value.denominator)
    if upward and integer*integer*value.denominator < value.numerator*scale*scale:
        integer += 1
    return Q(integer, scale)


def _published(value, label: str) -> Q:
    _require(type(value) is str, label+': expected rational string')
    result = Q(value)
    _require((result*(1 << BITS)).denominator == 1,
             label+': expected outward dyadic352')
    return result


def _interval(pair: list[int]) -> arb:
    validation.validate_pair(pair, 'native512 input')
    midpoint = Q(pair[0]+pair[1], 1 << (INPUT_BITS+1))
    radius = Q(pair[1]-pair[0], 1 << (INPUT_BITS+1))
    return arb(native.qarb(midpoint), native.qarb(radius))


def _principal(triangle: list) -> list[list[arb]]:
    _require(type(triangle) is list and len(triangle) == M,
             'native principal matrix dimension changed')
    result = [[arb(0) for _ in range(N)] for _ in range(N)]
    for i in range(N):
        _require(len(triangle[i]) == M-i, 'native matrix row shape changed')
        for j in range(i, N):
            result[i][j] = result[j][i] = _interval(triangle[i][j-i])
    return result


def _heads(receipt: dict) -> list[list[arb]]:
    """Use low offdiagonal A entries, then the original unsplit head sum."""
    triangle = receipt['matrices']['A_K']
    for name in COMPONENTS:
        _require(len(receipt['heads'][name]) == BOUNDARY-M,
                 'native component head inventory changed: '+name)
    result = []
    for k in range(N, BOUNDARY):
        row = []
        for j in range(N):
            if k < M:
                value = _interval(triangle[j][k-j])
            else:
                for name in COMPONENTS:
                    _require(len(receipt['heads'][name][k-M]) == M,
                             'native component head row shape changed')
                value = sum((_interval(receipt['heads'][name][k-M][j])
                             for name in COMPONENTS), arb(0))
            if (k-j) % 2:
                _require(value.contains(0), 'native cross-parity head excludes zero')
                value = arb(0)
            row.append(value)
        result.append(row)
    _require(len(result) == 998, 'incomplete complete20 cross inventory')
    return result


def _fresh_parameters(packet: dict, scalars: dict, coupling: dict) -> tuple[Q, dict]:
    t_exact = fmpq(*packet['support'])
    t = native.qarb(t_exact)
    raw_coefficients = native.exact_residual_coefficients(38)
    coefficients = [-v*t_exact**(d+1) for d, v in enumerate(raw_coefficients)]
    _require(scalars['kernel_coefficients_exact'] == list(map(str, coefficients)),
             'independent Bernoulli coefficients differ from pinned scalars')
    delta, rho_global = native.bound_tail(t, raw_coefficients, 38)
    c_t = (2*arb.pi()*t).log()+arb.const_euler()
    arithmetic = sum((arb(k).log()/arb(k).sqrt() for k in (2, 3)), arb(0))
    _require(arb(3).log() < 2*t < arb(4).log() and 2*t < arb.pi(),
             'fresh arithmetic/analytic window failed')
    fresh = {'delta': delta, 'rho_global': rho_global,
             'c_T': c_t, 'arithmetic': arithmetic}
    for name, value in fresh.items():
        lo, hi = native.endpoints(value)
        left, right = map(Q, scalars['scalars'][name])
        _require(left <= lo <= hi <= right,
                 'fresh scalar escaped pinned charge: '+name)
    delta_lo, delta_hi = native.endpoints(delta)
    _require(Q(packet['delta'][0], 1 << BITS) <= delta_lo <= delta_hi
             <= Q(packet['delta'][1], 1 << BITS),
             'fresh full residual escaped source delta')
    cross = arb.pi()/2+arithmetic+rho_global
    _require(native.endpoints(cross)[1] <= Q(packet['cross_norm_upper']),
             'fresh full cross norm exceeds unchanged charge')
    constant = tail_validation.smoothing_upper(coefficients, N)
    charges = {name: Q(value[1]) for name, value in scalars['scalars'].items()}
    rho = charges['delta']+_rational(constant)/Q(N*(N+1))
    mu = _rational(native.harmonic(N))-charges['c_T']-charges['arithmetic']-rho
    _require(mu > 0, 'nonpositive complete20 complement')
    rows = [row for row in coupling['projection_rows'] if row['projection'] == N]
    _require(coupling['selected_projection'] == N and len(rows) == 1
             and Q(rows[0]['mu_exact']) == mu
             and Q(rows[0]['rho_tail_upper_exact']) == rho,
             'independent complete20 complement differs from pinned C0090')
    complement = (native.qarb(native.harmonic(N))-c_t-arithmetic-delta
                  -native.qarb(constant)/fmpq(N*(N+1)))
    _require(mu <= native.endpoints(complement)[0],
             'chosen complete20 mu exceeds fresh complement')
    fresh['cross_norm'] = cross
    fresh['complement20'] = complement
    return mu, fresh


def _weights(mu: Q) -> dict[int, Q]:
    shift = Q()
    result = {}
    for k in range(N, BOUNDARY+1):
        if k > N:
            shift += Q(1, k)
        result[k] = 1/(mu+shift)
    _require(all(result[k] >= result[BOUNDARY] > 0
                 for k in range(N, BOUNDARY)),
             'harmonic correction coefficient is negative')
    return result


def _majorant(gram: list[list[arb]], heads: list[list[arb]],
              weights: dict[int, Q]) -> tuple[list[list[arb]], arb]:
    # Independent organization: enlarge G_M to G_N before weighting anything.
    enlarged = [[entry for entry in row] for row in gram]
    for k in range(N, M):
        h = heads[k-N]
        factor = native.qarb(Q(2*k+1, 2))
        for i in range(N):
            for j in range(i, N):
                rank = h[i]**2 if i == j else h[i]*h[j]
                enlarged[i][j] += rank*factor
    wm = native.qarb(weights[BOUNDARY])
    result = [[arb(0) for _ in range(N)] for _ in range(N)]
    for i in range(N):
        for j in range(i, N):
            value = wm*enlarged[i][j]
            for k in range(N, BOUNDARY):
                h = heads[k-N]
                rank = h[i]**2 if i == j else h[i]*h[j]
                value += rank*native.qarb((weights[k]-weights[BOUNDARY])*Q(2*k+1, 2))
            result[i][j] = result[j][i] = value
    # The newly restored low-cross prefix cancels from the omitted tail.
    gamma = arb(0)
    for j in range(N):
        diagonal = gram[j][j]
        for k in range(M, BOUNDARY):
            diagonal -= heads[k-N][j]**2*native.qarb(Q(2*k+1, 2))
        _require(native.endpoints(diagonal)[1] >= 0,
                 'omitted diagonal upper contradicts PSD')
        gamma += diagonal*native.qarb(Q(2*j+1, 2))
    _require(native.endpoints(gamma)[1] >= 0,
             'omitted trace upper contradicts PSD')
    return result, gamma


def _check_triangle(matrix: list[list[arb]], triangle: list, label: str) -> int:
    validation._rows(triangle, list(range(N, 0, -1)), label)
    checked = 0
    for i in range(N):
        for j in range(i, N):
            pair = triangle[i][j-i]
            if (i-j) % 2:
                _require(pair == [0, 0], label+': cross-parity entry is not exact zero')
            validation.reference_pair(matrix[i][j], pair, BITS,
                                      f'{label}[{i},{j}]', parity_zero=bool((i-j) % 2))
            checked += 1
    return checked


def _lower(report: dict, residual: Q) -> fmpq_mat:
    a_minus, _, _ = exact._order_bounds(report['A_K_triangle'], BITS)
    _, u_plus, _ = exact._order_bounds(report['U_triangle'], BITS)
    lower = a_minus-u_plus
    for j in range(N):
        penalty = residual*Q(2, 2*j+1)
        lower[j, j] -= fmpq(penalty.numerator, penalty.denominator)
    return lower


def _proof(block: dict, lower: fmpq_mat, parity: int) -> bool:
    indices = list(range(parity, N, 2))
    proof = block['positive_lower_witness']
    if proof is None:
        _require(block['mass_normalized_gap_exact'] is None, 'gap without witness')
        return False
    compressed = fmpq_mat([[lower[i, j] for j in indices] for i in indices])
    _require(compressed.nrows() == compressed.ncols() == 10,
             'complete parity witness is not ten-dimensional')
    margin = exact._verify_congruence(compressed, proof)
    _require(type(proof.get('exact_margin')) is str
             and Q(proof['exact_margin']) == margin, 'exact congruence margin changed')
    mass = sum((Q(v, proof['denominator'])**2*Q(2, 2*indices[j]+1)
                for row in proof['numerators'] for j, v in enumerate(row)), Q())
    _require(mass > 0 and type(block['mass_normalized_gap_exact']) is str
             and Q(block['mass_normalized_gap_exact']) == margin/mass,
             'physical mass-normalized complete20 witness gap changed')
    return True


def _quadratic(matrix: list[list[arb]], z: list[Q]) -> arb:
    value = arb(0)
    for i in range(N):
        if z[i]:
            value += matrix[i][i]*native.qarb(z[i]*z[i])
            for j in range(i+1, N):
                if z[j]:
                    value += matrix[i][j]*native.qarb(2*z[i]*z[j])
    return value


def _directional(block: dict, parity: int, a: list[list[arb]],
                 heads: list[list[arb]], weights: dict[int, Q], mu: Q,
                 delta: Q) -> dict:
    trial = block['trial']
    _require(type(trial) is list and len(trial) == N
             and all(type(v) is str for v in trial), 'invalid complete20 trial shape')
    z = list(map(Q, trial))
    _require(any(z) and all(not z[j] for j in range(1-parity, N, 2))
             and all((v*(1 << 48)).denominator == 1 for v in z),
             'trial is not nonzero, parity-supported on the exact 2^48 grid')
    norm = sum((v*v*Q(2, 2*j+1) for j, v in enumerate(z)), Q())
    energy = arb(0)
    for k in range(N, BOUNDARY):
        amplitude = sum((heads[k-N][j]*native.qarb(v)
                         for j, v in enumerate(z) if v), arb(0))
        energy += amplitude**2*native.qarb(weights[k]*Q(2*k+1, 2))
    energy_low = max(Q(), native.endpoints(energy)[0])
    error = delta*_sqrt(norm/mu, True)
    inverse_low = max(Q(), _sqrt(energy_low, False)-error)**2
    a_upper = native.endpoints(_quadratic(a, z))[1]+delta*norm
    upper = a_upper-inverse_low
    published = block['directional_check']
    _require(type(published) is dict, 'invalid directional check')
    _require(_published(published['norm'], 'direction norm') == _round(norm, True),
             'direction physical mass changed')
    published_a = _published(published['a_full_upper'], 'direction full A upper')
    published_inverse = _published(published['full_inverse_energy_lower'],
                                   'direction inverse energy lower')
    published_upper = _published(published['reference_upper'], 'direction reference upper')
    _require(published_a >= a_upper, 'full A directional upper is underpaid')
    _require(0 <= published_inverse <= inverse_low,
             'direction inverse energy lower exceeds native reverse-triangle bound')
    _require(published_upper >= upper,
             'genuine full reference directional upper is underpaid')
    return {'parity': parity, 'norm_exact': str(norm),
            'native_full_A_upper': str(a_upper),
            'finite_weighted_energy_lower': str(energy_low),
            'native_full_inverse_energy_lower': str(inverse_low),
            'native_reference_upper': str(upper),
            'published_reference_upper': str(published_upper)}


def audit(report_path: Path, origin_path: Path) -> dict:
    """Validate complete20 consequences without producer mathematics."""
    started = time.perf_counter()
    _origins()
    before = source.fingerprint()
    own_before = _snapshot()
    origin_raw = origin_path.read_bytes()
    raw = report_path.read_bytes()
    report = validation.decode_json(raw)
    packet, receipt, coupling, scalars, identity = source.load_inputs(origin_path)
    input_before = _input_snapshot(identity)
    origin_sha = hashlib.sha256(origin_raw).hexdigest()
    _require(identity['origin_sha256'] == origin_sha, 'origin receipt identity changed')
    required = {'format': 'research-complete-reprojection-v1',
                'source_sha256': before, 'input_sha256': identity['input_sha256'],
                'origin_sha256': origin_sha, 'support': [1353, 2048],
                'dimension': N, 'origin_dimension': M, 'boundary': BOUNDARY,
                'residual_order': 38, 'bits': BITS}
    for name, expected in required.items():
        _require(report.get(name) == expected, 'report binding changed: '+name)
    scope = report.get('scope')
    _require(type(scope) is str and all(term in scope.lower() for term in
             ('p20', 'research', 'source-conditional', 'no production admission',
              'spectral minimum')), 'missing complete20 source-conditional research scope')
    for obj, bits in ((packet, BITS), (receipt, INPUT_BITS)):
        _require(all(obj.get(k) == v for k, v in
                     {'bits': bits, 'support': [1353, 2048], 'dimension': M,
                      'boundary': BOUNDARY, 'residual_order': 38}.items()),
                 'accepted retained geometry or precision changed')
    _require(report['delta'] == packet['delta']
             and report['cross_norm_upper'] == packet['cross_norm_upper'],
             'full original source error charges changed')
    expected_a = [packet['matrices']['A_K'][i][:N-i] for i in range(N)]
    _require(report['A_K_triangle'] == expected_a,
             'complete principal A20 differs from retained source')
    with ctx.workprec(PRECISION):
        mu, fresh = _fresh_parameters(packet, scalars, coupling)
        _require(Q(report['mu_reference_exact']) == mu,
                 'complete20 reference differs from pinned harmonic complement')
        a = _principal(receipt['matrices']['A_K'])
        gram = _principal(receipt['matrices']['G_K'])
        heads = _heads(receipt)
        weights = _weights(mu)
        majorant, gamma = _majorant(gram, heads, weights)
        a_entries = _check_triangle(a, report['A_K_triangle'], 'A20')
        u_entries = _check_triangle(majorant, report['U_triangle'], 'U20')
        gamma_upper = _published(report['gamma_upper_exact'], 'omitted trace upper')
        _require(gamma_upper >= native.endpoints(gamma)[1] >= 0,
                 'unknown k>=1018 residual Gram tail is underpaid')
        tail_loss = _published(report['tail_loss_upper_exact'], 'weighted omitted tail upper')
        _require(tail_loss >= weights[BOUNDARY]*gamma_upper,
                 'unknown high tail loss is underpaid')
        delta = Q(packet['delta'][1], 1 << BITS)
        b_full = Q(packet['cross_norm_upper'])
        residual = _round(delta*(1+2*b_full/mu)+delta*delta/mu, True)
        _require(_published(report['residual_allowance_exact'], 'uniform residual') == residual,
                 'full unchanged cross/residual allowance changed')
        lower = _lower(report, residual)
        blocks = report['blocks']
        _require(type(blocks) is list and len(blocks) == 2,
                 'complete20 requires exactly two parity blocks')
        certified = []
        directions = []
        for block, parity in zip(blocks, (0, 1), strict=True):
            _require(type(block) is dict and type(block.get('parity')) is int
                     and block['parity'] == parity, 'complete block parity changed')
            certified.append(_proof(block, lower, parity))
            directions.append(_directional(block, parity, a, heads, weights, mu, delta))
        positive = all(certified)
        negative = any(Q(row['published_reference_upper']) < 0 for row in directions)
        _require(not (positive and negative), 'contradictory complete20 certified signs')
        selected_status = ('POSITIVE_REFERENCE_LOWER' if positive else
                           'NEGATIVE_REFERENCE_DIRECTION' if negative else
                           'INCONCLUSIVE_LOWER')
        _require(report['status'] == selected_status, 'complete20 classification changed')
        scalar_intervals = {name: list(map(str, native.endpoints(value)))
                            for name, value in fresh.items()}
    _require(source.fingerprint() == before and _snapshot() == own_before,
             'source or audit dependencies changed during audit')
    _require(_input_snapshot(identity) == input_before,
             'retained source inputs changed during audit')
    _require(origin_path.read_bytes() == origin_raw, 'origin receipt changed during audit')
    _require(report_path.read_bytes() == raw, 'complete20 report changed during audit')
    return {'format': FORMAT, 'status': 'RETAINED_INPUT_CONSEQUENCES_ACCEPTED',
            'report_sha256': hashlib.sha256(raw).hexdigest(),
            'source_sha256': before, 'input_sha256': input_before,
            'origin_sha256': origin_sha, 'audit_source_sha256': own_before,
            'support': [1353, 2048], 'dimension': N, 'origin_dimension': M,
            'boundary': BOUNDARY, 'residual_order': 38,
            'native_input_bits': INPUT_BITS, 'arb_precision_bits': PRECISION,
            'checked_A_entries': a_entries, 'checked_U_entries': u_entries,
            'checked_triangle_entries': a_entries+u_entries,
            'checked_head_rows': len(heads), 'checked_mode_range': [N, BOUNDARY],
            'gram_enlargement_mode_range': [N, M],
            'parity_dimensions': [10, 10], 'positive_parity_witnesses': certified,
            'exact_witnesses_verified': True, 'directional_checks': directions,
            'fresh_scalar_intervals': scalar_intervals,
            'selected_status': selected_status, 'omitted_high_tail_paid': True,
            'data_authority': 'Inherited C0087 original-version source and native receipt '
                              'evidence accepted through the bound original-v2 origin gate; '
                              'not a fresh analytical source audit.',
            'scope': 'Complete P20 source-conditional research reference; '
                     'no production admission or full spectral minimum.',
            'elapsed_seconds': time.perf_counter()-started}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--origin', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        _require(not args.output.exists() and not args.output.is_symlink(),
                 'refusing to overwrite previous evidence')
        result = audit(args.report, args.origin)
        with args.output.open('x', encoding='utf-8', newline='\n') as handle:
            handle.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
        print(json.dumps({'status': result['status'],
                          'selected_status': result['selected_status']}))
        return 0
    except Exception as exc:
        print(f'REJECTED: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
