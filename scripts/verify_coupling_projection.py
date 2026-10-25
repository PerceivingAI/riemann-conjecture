"""Audit retained-input coupling projections independently, research only.

Uses the accepted native 512-bit receipt arrays at Arb precision 1536. No
analytical matrix or head reconstruction is performed. A successful receipt
concerns only the original P16 compression, never positivity of all P_L.
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
from scripts import weil_coupling_projection as source

ROOT = Path(__file__).resolve().parents[1]
BITS = 352
INPUT_BITS = 512
PRECISION = 1536
FORMAT = 'research-coupling-projection-audit-v1'
AUDITOR = 'scripts/verify_coupling_projection.py'
DEPENDENCIES = (
    AUDITOR,
    'scripts/verify_combined_schur_analytic_entries.py',
    'scripts/verify_residual_tail_bound.py',
    'scripts/verify_weighted_low_space.py',
    'scripts/verify_weighted_low_space_inputs.py',
)
COMPONENTS = ('V', 'P', 'RK')
CROSSES = (('VP', 'V', 'P'), ('VRK', 'V', 'RK'), ('PRK', 'P', 'RK'))


def _require(condition: bool, label: str) -> None:
    validation.require(condition, label)


def _snapshot() -> dict[str, str]:
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
            for name in DEPENDENCIES}


def _origins() -> None:
    _require(Path(__file__).resolve() == (ROOT/AUDITOR).resolve(),
             'independent auditor origin changed')
    for module, name in ((native, DEPENDENCIES[1]),
                         (tail_validation, DEPENDENCIES[2]),
                         (exact, DEPENDENCIES[3]),
                         (validation, DEPENDENCIES[4]),
                         (source, 'scripts/weil_coupling_projection.py')):
        _require(Path(module.__file__).resolve() == (ROOT/name).resolve(),
                 'audit dependency origin changed: '+name)
    _require(validation.REFERENCE_BITS == INPUT_BITS,
             'native receipt precision changed')


def _rational(value) -> Q:
    return Q(int(value.p), int(value.q))


def _round(value: Q, upward: bool, bits: int = BITS) -> Q:
    scale = 1 << bits
    scaled = value*scale
    return Q(scaled.__ceil__() if upward else scaled.__floor__(), scale)


def _sqrt(value: Q, upward: bool, bits: int = PRECISION) -> Q:
    _require(value >= 0, 'negative square-root argument')
    scale = 1 << bits
    integer = isqrt(value.numerator*scale*scale//value.denominator)
    if upward and integer*integer*value.denominator < value.numerator*scale*scale:
        integer += 1
    return Q(integer, scale)


def _published_pair(pair, label: str) -> tuple[Q, Q]:
    _require(type(pair) is list and len(pair) == 2
             and all(type(v) is str for v in pair), label+': invalid rational pair')
    lo, hi = map(Q, pair)
    _require(lo <= hi, label+': reversed interval')
    _require(all((v*(1 << BITS)).denominator == 1 for v in (lo, hi)),
             label+': pair not outward dyadic352')
    return lo, hi


def _contains(value: arb | tuple[Q, Q], pair, label: str) -> tuple[Q, Q]:
    lo, hi = native.endpoints(value) if isinstance(value, arb) else value
    left, right = _published_pair(pair, label)
    _require(left <= lo <= hi <= right, label+': native interval escaped publication')
    return lo, hi


def _interval(pair: list[int]) -> arb:
    validation.validate_pair(pair, 'native512 input')
    midpoint = Q(pair[0]+pair[1], 1 << (INPUT_BITS+1))
    radius = Q(pair[1]-pair[0], 1 << (INPUT_BITS+1))
    return arb(native.qarb(midpoint), native.qarb(radius))


def _matrix(triangle: list) -> list[list[arb]]:
    _require(len(triangle) == 16, 'native matrix dimension changed')
    result = [[arb(0) for _ in range(16)] for _ in range(16)]
    for i, row in enumerate(triangle):
        _require(len(row) == 16-i, 'native triangle shape changed')
        for offset, pair in enumerate(row):
            j = i+offset
            result[i][j] = result[j][i] = _interval(pair)
    return result


def _quad(matrix: list[list[arb]], z: list[Q]) -> arb:
    result = arb(0)
    for i in range(16):
        if z[i]:
            result += matrix[i][i]*native.qarb(z[i]*z[i])
            for j in range(i+1, 16):
                if z[j]:
                    result += matrix[i][j]*native.qarb(2*z[i]*z[j])
    return result


def _parameters(scalars: dict, coefficients: list[fmpq], projection: int) -> tuple[Q, Q]:
    charges = {name: Q(pair[1]) for name, pair in scalars['scalars'].items()}
    constant = _rational(tail_validation.smoothing_upper(coefficients, projection))
    rho = charges['delta']+constant/Q(projection*(projection+1))
    mu = _rational(native.harmonic(projection))-charges['c_T']-charges['arithmetic']-rho
    _require(mu > 0, 'nonpositive projection complement')
    return mu, rho


def _weights(mu: Q, projection: int) -> dict[int, Q]:
    baseline = _rational(native.harmonic(projection))
    return {k: 1/(mu+_rational(native.harmonic(k))-baseline)
            for k in range(projection, 55)}


def _fresh_scalars(packet: dict, scalars: dict, coefficients: list[fmpq]) -> dict:
    t = native.qarb(Q(*packet['support']))
    raw_coefficients = native.exact_residual_coefficients(38)
    delta, rho_global = native.bound_tail(t, raw_coefficients, 38)
    c_t = (2*arb.pi()*t).log()+arb.const_euler()
    arithmetic = sum((arb(m).log()/arb(m).sqrt() for m in (2, 3)), arb(0))
    _require(arb(3).log() < 2*t < arb(4).log() and 2*t < arb.pi(),
             'fresh arithmetic/analytic window failed')
    fresh = {'delta': delta, 'rho_global': rho_global,
             'c_T': c_t, 'arithmetic': arithmetic}
    for name, value in fresh.items():
        lo, hi = native.endpoints(value)
        left, right = map(Q, scalars['scalars'][name])
        _require(left <= lo <= hi <= right, 'fresh scalar escaped pinned charges: '+name)
    _require(scalars['kernel_coefficients_exact'] == list(map(str, coefficients)),
             'independent Bernoulli coefficients differ from pinned scalars')
    _require(native.endpoints(delta)[1] <= Q(packet['delta'][1], 1 << BITS),
             'fresh full residual exceeds source delta')
    cross = arb.pi()/2+arithmetic+rho_global
    _require(native.endpoints(cross)[1] <= Q(packet['cross_norm_upper']),
             'fresh full cross norm exceeds unchanged charge')
    return {'delta': delta, 'c_T': c_t, 'arithmetic': arithmetic,
            'rho_global': rho_global, 'cross_norm': cross}


def _mode_diagnostic(published: dict, old: dict, matrices: dict,
                     heads: dict, mu16: Q, delta: Q) -> dict:
    parity = old['parity']
    _require(published['parity'] == parity and published['trial'] == old['trial'],
             'retained trial or parity changed')
    z = [Q(v) for v in published['trial']]
    _require(len(z) == 16 and any(z)
             and all(not z[j] for j in range(1-parity, 16, 2)),
             'invalid retained trial dimension/parity')
    norm = sum((v*v*Q(2, 2*j+1) for j, v in enumerate(z)), Q())
    _require(Q(published['norm_exact']) == norm, 'ordinary low mass changed')
    a_pair = _contains(_quad(matrices['A_K'], z), published['A_K_pair'], 'trial A_K')
    weights = _weights(mu16, 16)
    _require(len(published['mode_rows']) == 38, 'incomplete mode inventory')
    energy = {}
    for row, k in zip(published['mode_rows'], range(16, 54), strict=True):
        _require(row['k'] == k, 'mode inventory is not ascending/complete')
        _require(set(row['components']) == set(COMPONENTS)
                 and set(row['self_energy']) == set(COMPONENTS)
                 and set(row['cross_energy']) == {v[0] for v in CROSSES},
                 'signed component inventory changed')
        amplitudes = {}
        for name in COMPONENTS:
            amplitude = sum((heads[name][k-16][j]*native.qarb(v)
                             for j, v in enumerate(z) if v), arb(0))
            _contains(amplitude, row['components'][name], f'mode {k} amplitude {name}')
            amplitudes[name] = amplitude
        factor = native.qarb(Q(2*k+1, 2))
        weighted = factor*native.qarb(weights[k])
        total = sum(amplitudes.values(), arb(0))
        energy[k] = total**2*factor
        _contains(energy[k], row['energy_pair'], f'mode {k} energy')
        _contains(energy[k]*native.qarb(weights[k]), row['weighted_energy_pair'],
                  f'mode {k} weighted energy')
        for name in COMPONENTS:
            _contains(amplitudes[name]**2*weighted, row['self_energy'][name],
                      f'mode {k} weighted self {name}')
        for label, left, right in CROSSES:
            _contains(2*amplitudes[left]*amplitudes[right]*weighted,
                      row['cross_energy'][label], f'mode {k} signed cross {label}')
    ranked = sorted(range(16, 54), key=lambda k: (
        -Q(published['mode_rows'][k-16]['weighted_energy_pair'][0]), k))
    _require(published['ranked_modes'] == ranked, 'weighted lower-charge ranking changed')
    gamma = _quad(matrices['G_K'], z)-sum(energy.values(), arb(0))
    gamma_lo, gamma_hi = native.endpoints(gamma)
    _require(gamma_hi >= 0, 'remaining tail upper contradicts PSD')
    gamma_pair = (max(Q(), gamma_lo), gamma_hi)
    _contains(gamma_pair, published['gamma_pair'], 'trial omitted tail mass')
    # Prefix uses physical order, not the diagnostic ranking. Published lower
    # weighted energies and A_K upper are independently enclosed above.
    _, source_a_hi = _published_pair(published['A_K_pair'], 'prefix A_K')
    error = delta*_sqrt(norm/mu16, True, BITS)
    head_lo = Q()
    first = None
    for row in published['mode_rows']:
        head_lo += Q(row['weighted_energy_pair'][0])
        _require(head_lo >= 0, 'negative certified prefix energy')
        lower_root = max(Q(), _sqrt(head_lo, False, BITS)-error)
        upper = source_a_hi+delta*norm-lower_root*lower_root
        if upper < 0 and first is None:
            first = row['k']
    _require(published['first_negative_prefix'] == first,
             'first negative physical-mode prefix changed')
    return {'parity': parity, 'norm': norm, 'A_K': a_pair,
            'gamma': gamma_pair, 'energy': energy, 'first_negative_prefix': first}


def _directional(mode: dict, weights: dict[int, Q], mu: Q, delta: Q) -> dict:
    head = sum((mode['energy'][k]*native.qarb(weight)
                for k, weight in weights.items() if k < 54), arb(0))
    head_lo, head_hi = native.endpoints(head)
    head_lo = max(Q(), head_lo)
    remainder = weights[54]*mode['gamma'][1]
    h_hi = head_hi+remainder
    _require(h_hi >= 0, 'negative weighted full energy upper')
    e = delta*_sqrt(mode['norm']/mu, True)
    lower = mode['A_K'][0]-delta*mode['norm']-(_sqrt(h_hi, True)+e)**2
    root = max(Q(), _sqrt(head_lo, False)-e)
    upper = mode['A_K'][1]+delta*mode['norm']-root*root
    return {'lower': lower, 'upper': upper, 'head': (head_lo, head_hi),
            'remainder': remainder}


def _proofs(packet: dict, row: dict, residual: Q) -> bool:
    # These unchanged legacy routines use only exact rational arithmetic. The
    # source's interval matrix, not a fresh floating proposal, defines L_matrix.
    a_minus, _, _ = exact._order_bounds(packet['matrices']['A_K'], BITS)
    _, u_plus, _ = exact._order_bounds(row['U_triangle'], BITS)
    lower = a_minus-u_plus
    for j in range(16):
        penalty = residual*Q(2, 2*j+1)
        lower[j, j] -= fmpq(penalty.numerator, penalty.denominator)
    _require(len(row['parity_proofs']) == 2, 'parity proof inventory changed')
    certified = []
    for item, parity in zip(row['parity_proofs'], (0, 1), strict=True):
        _require(item['parity'] == parity, 'proof parity changed')
        proof = item['witness']
        if proof is None:
            _require(item['mass_normalized_gap_exact'] is None, 'gap without witness')
            certified.append(False)
            continue
        indices = list(range(parity, 16, 2))
        block = fmpq_mat([[lower[i, j] for j in indices] for i in indices])
        margin = exact._verify_congruence(block, proof)
        _require(Q(proof['exact_margin']) == margin, 'exact congruence margin changed')
        mass_trace = sum((Q(v, proof['denominator'])**2*Q(2, 2*indices[j]+1)
                          for witness_row in proof['numerators']
                          for j, v in enumerate(witness_row)), Q())
        _require(mass_trace > 0 and Q(item['mass_normalized_gap_exact']) == margin/mass_trace,
                 'physical mass-normalized witness gap changed')
        certified.append(True)
    return all(certified)


def audit(result_path: Path) -> dict:
    """Check a projection report without calling producer mathematics."""
    started = time.perf_counter()
    _origins()
    before = source.fingerprint()
    own_before = _snapshot()
    raw = result_path.read_bytes()
    report = validation.decode_json(raw)
    # This loader binds immutable accepted evidence and replays the historical
    # result. It is the only producer operation used besides byte fingerprints.
    packet, receipt, old_result, scalars, hashes = source.load_inputs()
    required = {'format': source.FORMAT, 'support': [1353, 2048],
                'known_dimension': 16, 'boundary': 54, 'residual_order': 38,
                'bits': BITS, 'source_sha256': before, 'inputs_sha256': hashes}
    for name, value in required.items():
        _require(report.get(name) == value, 'report binding changed: '+name)
    _require(type(report.get('scope')) is str and bool(report['scope']),
             'missing research scope')
    _require(receipt['bits'] == INPUT_BITS and packet['bits'] == BITS,
             'accepted precision changed')
    checked_rows = []
    checked_entries = 0
    with ctx.workprec(PRECISION):
        t = fmpq(*packet['support'])
        coefficients = [-v*t**(d+1) for d, v in
                        enumerate(native.exact_residual_coefficients(38))]
        fresh = _fresh_scalars(packet, scalars, coefficients)
        mu16, _ = _parameters(scalars, coefficients, 16)
        _require(mu16 == Q(packet['mu_reference_exact']),
                 'original tail reference mu16 changed')
        matrices = {name: _matrix(receipt['matrices'][name]) for name in ('A_K', 'G_K')}
        heads = {name: [[_interval(pair) for pair in row]
                        for row in receipt['heads'][name]] for name in COMPONENTS}
        combined = [[sum((heads[name][k][j] for name in COMPONENTS), arb(0))
                     for j in range(16)] for k in range(38)]
        delta = Q(packet['delta'][1], 1 << BITS)
        _require(len(report['mode_diagnostics']) == len(old_result['blocks']) == 2,
                 'retained mode diagnostic inventory changed')
        modes = [_mode_diagnostic(item, old, matrices, heads, mu16, delta)
                 for item, old in zip(report['mode_diagnostics'], old_result['blocks'], strict=True)]
        rows = report['projection_rows']
        _require(type(rows) is list and bool(rows) and len(rows) <= 20,
                 'invalid projection candidate inventory')
        selected = None
        # Independent organization: first remove the finite physical prefix
        # from G16, then add only nonnegative weighted head corrections.
        gram = [[entry for entry in row] for row in matrices['G_K']]
        next_removed = 16
        for row, projection in zip(rows, range(16, 55, 2), strict=False):
            _require(selected is None, 'rows continue after first certified projection')
            _require(type(row['projection']) is int and row['projection'] == projection,
                     'projections must be consecutive ascending even candidates')
            mu, rho = _parameters(scalars, coefficients, projection)
            _require(Q(row['mu_exact']) == mu
                     and Q(row['rho_tail_upper_exact']) == rho,
                     'exact projection complement/rho changed')
            constant = tail_validation.smoothing_upper(coefficients, projection)
            fresh_complement = (native.qarb(native.harmonic(projection))-fresh['c_T']
                                -fresh['arithmetic']-fresh['delta']
                                -native.qarb(constant)/fmpq(projection*(projection+1)))
            _require(mu <= native.endpoints(fresh_complement)[0],
                     'chosen projection mu exceeds fresh native complement')
            weights = _weights(mu, projection)
            while next_removed < projection:
                k = next_removed
                factor = native.qarb(Q(2*k+1, 2))
                for i in range(16):
                    for j in range(i, 16):
                        term = (combined[k-16][i]**2 if i == j else
                                combined[k-16][i]*combined[k-16][j])
                        gram[i][j] = gram[i][j]-term*factor
                next_removed += 1
            _require(len(row['U_triangle']) == 16, 'U triangle dimension changed')
            for i in range(16):
                _require(len(row['U_triangle'][i]) == 16-i, 'U triangle row shape changed')
                for j in range(i, 16):
                    value = gram[i][j]*native.qarb(weights[54])
                    for k in range(projection, 54):
                        term = (combined[k-16][i]**2 if i == j else
                                combined[k-16][i]*combined[k-16][j])
                        value += term*native.qarb((weights[k]-weights[54])*Q(2*k+1, 2))
                    validation.reference_pair(value, row['U_triangle'][i][j-i], BITS,
                                              f'U{projection}[{i},{j}]',
                                              parity_zero=bool((i-j) % 2))
                    checked_entries += 1
            b_full = Q(packet['cross_norm_upper'])
            residual = _round(delta*(1+2*b_full/mu)+delta*delta/mu, True)
            _require(Q(row['uniform_residual_upper_exact']) == residual,
                     'full unchanged cross/residual allowance changed')
            certified = _proofs(packet, row, residual)
            _require(len(row['trial_bounds']) == 2, 'directional inventory changed')
            negative = False
            for published, mode in zip(row['trial_bounds'], modes, strict=True):
                _require(published['parity'] == mode['parity'], 'directional parity changed')
                direction = _directional(mode, weights, mu, delta)
                _contains(direction['head'], published['weighted_head_pair'],
                          f'L{projection} directional weighted head')
                _require(Q(published['weighted_remainder_upper']) >= direction['remainder'],
                         'unknown weighted tail is underpaid')
                _require(Q(published['reference_lower_exact']) <= direction['lower']
                         <= direction['upper'] <= Q(published['reference_upper_exact']),
                         'native full directional bound escaped publication')
                negative |= Q(published['reference_upper_exact']) < 0
            _require(not (certified and negative), 'contradictory certified signs')
            status = ('KNOWN_SUBSPACE_POSITIVE_LOWER' if certified else
                      'NEGATIVE_KNOWN_DIRECTION' if negative else 'INCONCLUSIVE_KNOWN_SUBSPACE')
            _require(row['status'] == status, 'candidate classification changed')
            checked_rows.append(projection)
            if certified:
                selected = projection
        _require(selected is not None or checked_rows[-1] == 54,
                 'incomplete search without a certified selection')
        _require(report['selected_projection'] == selected, 'selection is not first certified row')
    _require(source.fingerprint() == before and _snapshot() == own_before,
             'source or audit dependencies changed during audit')
    _require(result_path.read_bytes() == raw, 'report changed during audit')
    return {'format': FORMAT, 'status': 'RETAINED_INPUT_CONSEQUENCES_ACCEPTED',
            'report_sha256': hashlib.sha256(raw).hexdigest(), 'inputs_sha256': hashes,
            'source_sha256': before, 'audit_source_sha256': own_before,
            'native_input_bits': INPUT_BITS, 'arb_precision_bits': PRECISION,
            'checked_projections': checked_rows, 'checked_modes': [16, 54],
            'checked_mode_rows': 76, 'checked_U_entries': checked_entries,
            'selected_projection': selected, 'exact_witnesses_verified': True,
            'first_certified_selection_verified': True,
            'first_negative_prefixes': [mode['first_negative_prefix'] for mode in modes],
            'scope': 'Research-only consequences of immutable accepted inputs; positivity, if certified, '
                     'is restricted to the original P16 compression. No positivity of all P_L, '
                     'new source admission, true-inverse evaluation or RH claim.',
            'elapsed_seconds': time.perf_counter()-started}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('result', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        _require(not args.output.exists() and not args.output.is_symlink(),
                 'refusing to overwrite previous evidence')
        result = audit(args.result)
        with args.output.open('x', encoding='utf-8', newline='\n') as handle:
            handle.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
        print(json.dumps({'status': result['status'],
                          'selected_projection': result['selected_projection']}))
        return 0
    except Exception as exc:
        print(f'REJECTED: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
