"""Retained-data coupled-mode diagnosis and projection choice, research only.

A selected projection certifies only the original P16 compression of the new
reference. It does not certify new low rows or the complete enlarged low space.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import time

from flint import fmpq, fmpq_mat
from scripts import verify_weighted_low_space as exact
from scripts import verify_weighted_low_space_inputs as validation
from scripts import weil_tail_complement_assessment as reference
from scripts import weil_residual_tail_bound as residual
from scripts import weil_weighted_extension_diagnostics as diagnostics

ROOT = Path(__file__).resolve().parents[1]
BITS = 352
FORMAT = 'research-coupling-projection-v1'
BASE = 'computations/2026-10-24T231555Z-tail-complement-weighted-reference/data/'
INPUTS = {
    BASE+'source-m54-v1.json.gz': '8c7626b05e5f686155eca520d05c9908f829f3c78fbfe3cea900cd22b63da8af',
    BASE+'audit-m54-v1.json.gz': '563f7ad158e7362d5417166c01b9a63e4289378961cc70c85f885c7c0d477335',
    BASE+'result-m54-v1.json': 'ce6f31d8393452ee5d55b1c8e12049d8090b60556d1ab4c689d788a4d9c521d9',
    BASE+'prior-scalars-v1.json': '65cc22df9e5edfbaebd9b183edbc29b179c7d3474731e24170cc9abc543a0b9a',
}
SOURCE_PATHS = tuple(dict.fromkeys((
    'scripts/weil_coupling_projection.py', 'scripts/verify_coupling_projection.py',
    *reference.SOURCE_PATHS,
)))


def fingerprint() -> dict:
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCE_PATHS}


def save(path: Path, value: dict) -> None:
    reference.save(path, value)


def load_inputs() -> tuple[dict, dict, dict, dict, dict]:
    blobs = {}
    for name, expected in INPUTS.items():
        raw = (ROOT/name).read_bytes()
        validation.require(hashlib.sha256(raw).hexdigest() == expected, 'retained input bytes changed: '+name)
        blobs[name] = validation.decode_json(gzip.decompress(raw) if name.endswith('.gz') else raw)
    packet, sha, audit_sha = reference.load_accepted(ROOT/(BASE+'source-m54-v1.json.gz'), ROOT/(BASE+'audit-m54-v1.json.gz'))
    result = blobs[BASE+'result-m54-v1.json']
    validation.require(reference.assess(packet, sha, audit_sha, result) == result, 'original reference does not replay')
    return packet, blobs[BASE+'audit-m54-v1.json.gz'], result, blobs[BASE+'prior-scalars-v1.json'], dict(INPUTS)


def rounded(pair, bits=BITS) -> tuple[Q, Q]:
    den = 1 << bits
    return Q((pair[0]*den).__floor__(), den), Q((pair[1]*den).__ceil__(), den)


def encoded(pair) -> list[str]:
    return [str(value) for value in rounded(pair)]


def scaled(pair, value: Q):
    a, b = pair[0]*value, pair[1]*value
    return min(a, b), max(a, b)


def multiplied(left, right):
    return exact._product(left, right)


def squared(pair):
    return exact._square(pair)


def quadratic_pair(triangle: list, z: list[Q], bits: int) -> tuple[Q, Q]:
    low = high = Q(0)
    for i, row in enumerate(triangle):
        for offset, pair in enumerate(row):
            j = i+offset
            a, b = scaled(tuple(Q(v, 1 << bits) for v in pair), z[i]*z[j]*(1 if i == j else 2))
            low += a; high += b
    return rounded((low, high))


def projection_parameters(scalars: dict, projection: int) -> tuple[Q, Q]:
    validation.require(type(projection) is int and 16 <= projection <= 54 and projection % 2 == 0,
                       'projection outside retained even window')
    coefficients = [Q(value) for value in scalars['kernel_coefficients_exact']]
    constant = residual.tail_constant(coefficients, projection)
    rho = Q(scalars['scalars']['delta'][1])+constant/(projection*(projection+1))
    mu = exact._harmonic(projection)-Q(scalars['scalars']['c_T'][1])-Q(scalars['scalars']['arithmetic'][1])-rho
    validation.require(mu > 0, 'projection reference is not positive')
    return mu, rho


def projection_majorant(gram: list, heads: list, original_n: int, projection: int,
                        boundary: int, mu: Q, bits: int = BITS) -> list:
    """Complete U on the old low space, including negative promoted-prefix terms."""
    if not (original_n <= projection <= boundary and mu > 0):
        raise ValueError('invalid projection or reference')
    if len(gram) != original_n or len(heads) != boundary-original_n:
        raise ValueError('incomplete Gram/head geometry')
    harmonic = exact._harmonic(projection)
    wm = 1/(mu+exact._harmonic(boundary)-harmonic)
    wm_pair = exact._weight(wm, bits)
    coefficients = [exact._weight(-wm if k < projection else 1/(mu+exact._harmonic(k)-harmonic)-wm, bits)
                    for k in range(original_n, boundary)]
    triangle = []
    for i in range(original_n):
        row = []
        for j in range(i, original_n):
            lo, hi = exact._product(gram[i][j-i], wm_pair)
            lo <<= bits+1; hi <<= bits+1
            for k, head, coefficient in zip(range(original_n, boundary), heads, coefficients, strict=True):
                product = exact._square(head[i]) if i == j else exact._product(head[i], head[j])
                a, b = exact._product(product, coefficient)
                lo += (2*k+1)*a; hi += (2*k+1)*b
            row.append(exact._round_pair(lo, hi, 2*bits+1))
        triangle.append(row)
    return triangle


def mode_diagnostic(packet: dict, block: dict) -> dict:
    z = [Q(value) for value in block['trial']]
    norm = sum((value*value*Q(2, 2*j+1) for j, value in enumerate(z)), Q(0))
    a = quadratic_pair(packet['matrices']['A_K'], z, BITS)
    g = quadratic_pair(packet['matrices']['G_K'], z, BITS)
    mu = Q(packet['mu_reference_exact']); hn = exact._harmonic(16)
    rows = []
    for offset, k in enumerate(range(16, 54)):
        parts = {}
        for name in ('V', 'P', 'RK'):
            lo = hi = Q(0)
            for value, pair in zip(z, packet['heads'][name][offset], strict=True):
                left, right = scaled(tuple(Q(v, 1 << BITS) for v in pair), value)
                lo += left; hi += right
            parts[name] = rounded((lo, hi))
        combined = tuple(sum((part[e] for part in parts.values()), Q(0)) for e in (0, 1))
        mass = rounded(scaled(squared(combined), Q(2*k+1, 2)))
        weight = 1/(mu+exact._harmonic(k)-hn)
        factor = weight*Q(2*k+1, 2)
        selves = {name: encoded(scaled(squared(value), factor)) for name, value in parts.items()}
        crosses = {left+right: encoded(scaled(multiplied(parts[left], parts[right]), 2*factor))
                   for left, right in (('V', 'P'), ('V', 'RK'), ('P', 'RK'))}
        rows.append({'k': k, 'components': {name: encoded(value) for name, value in parts.items()},
                     'energy_pair': encoded(mass), 'weighted_energy_pair': encoded(scaled(mass, weight)),
                     'self_energy': selves, 'cross_energy': crosses})
    total_low = sum((Q(row['energy_pair'][0]) for row in rows), Q(0))
    total_high = sum((Q(row['energy_pair'][1]) for row in rows), Q(0))
    gamma = rounded((max(Q(0), g[0]-total_high), g[1]-total_low))
    validation.require(gamma[1] >= 0, 'omitted mass upper contradicts positivity')
    delta = Q(packet['delta'][1], 1 << BITS)
    error = delta*exact._sqrt(norm/mu, BITS, True)
    prefix, first = Q(0), None
    for row in rows:
        prefix += Q(row['weighted_energy_pair'][0])
        inverse = max(Q(0), exact._sqrt(prefix, BITS, False)-error)**2
        if a[1]+delta*norm-inverse < 0:
            first = row['k']; break
    return {'parity': block['parity'], 'trial': block['trial'], 'norm_exact': str(norm),
            'A_K_pair': encoded(a), 'gamma_pair': encoded(gamma), 'mode_rows': rows,
            'ranked_modes': [row['k'] for row in sorted(rows, key=lambda r: (-Q(r['weighted_energy_pair'][0]), r['k']))],
            'first_negative_prefix': first}


def directional_bound(mode: dict, projection: int, mu: Q, delta: Q) -> dict:
    harmonic = exact._harmonic(projection)
    head_low = head_high = Q(0)
    for row in mode['mode_rows']:
        if row['k'] >= projection:
            weight = 1/(mu+exact._harmonic(row['k'])-harmonic)
            left, right = rounded(scaled(tuple(map(Q, row['energy_pair'])), weight))
            head_low += left; head_high += right
    head = rounded((head_low, head_high))
    wm = 1/(mu+exact._harmonic(54)-harmonic)
    remainder = exact._up(wm*Q(mode['gamma_pair'][1]), BITS)
    norm = Q(mode['norm_exact']); error = delta*exact._sqrt(norm/mu, BITS, True)
    inverse_low = max(Q(0), exact._sqrt(head[0], BITS, False)-error)**2
    inverse_high = (exact._sqrt(head[1]+remainder, BITS, True)+error)**2
    lower = Q(mode['A_K_pair'][0])-delta*norm-inverse_high
    upper = Q(mode['A_K_pair'][1])+delta*norm-inverse_low
    return {'parity': mode['parity'], 'reference_lower_exact': str(lower), 'reference_upper_exact': str(upper),
            'weighted_head_pair': encoded(head), 'weighted_remainder_upper': str(remainder)}


def analyze(prior: dict | None = None) -> dict:
    started = time.perf_counter()
    packet, audit, original, scalars, hashes = load_inputs()
    before = fingerprint()
    mu16, _ = projection_parameters(scalars, 16)
    validation.require(mu16 == Q(packet['mu_reference_exact']), 'initial harmonic reference changed')
    modes = [mode_diagnostic(packet, block) for block in original['blocks']]
    heads = [[[sum(packet['heads'][name][offset][j][end] for name in ('V', 'P', 'RK')) for end in (0, 1)]
              for j in range(16)] for offset in range(38)]
    a_minus, _, _ = exact._order_bounds(packet['matrices']['A_K'], BITS)
    delta = Q(packet['delta'][1], 1 << BITS); full_cross = Q(packet['cross_norm_upper'])
    rows, selected = [], None
    for projection in range(16, 55, 2):
        mu, rho = projection_parameters(scalars, projection)
        triangle = projection_majorant(packet['matrices']['G_K'], heads, 16, projection, 54, mu)
        _, u_plus, _ = exact._order_bounds(triangle, BITS)
        residual_upper = diagnostics.uniform_residual(delta, full_cross, mu)
        lower = a_minus-u_plus
        for j in range(16):
            amount = residual_upper*Q(2, 2*j+1)
            lower[j, j] -= fmpq(amount.numerator, amount.denominator)
        proofs = []
        for parity in (0, 1):
            indices = list(range(parity, 16, 2))
            matrix = fmpq_mat([[lower[i, j] for j in indices] for i in indices])
            if prior is None:
                proof = exact._positive_proof(matrix)
            else:
                old = prior['projection_rows'][(projection-16)//2]['parity_proofs'][parity]
                validation.require(old['parity'] == parity, 'altered parity inventory')
                proof = old['witness']
                if proof is not None:
                    validation.require(exact._verify_congruence(matrix, proof) == Q(proof['exact_margin']),
                                       'altered exact matrix margin')
            gap = None
            if proof is not None:
                trace = sum((Q(value, proof['denominator'])**2*Q(2, 2*indices[j]+1)
                             for row in proof['numerators'] for j, value in enumerate(row)), Q(0))
                gap = str(Q(proof['exact_margin'])/trace)
            proofs.append({'parity': parity, 'witness': proof, 'mass_normalized_gap_exact': gap})
        trials = [directional_bound(mode, projection, mu, delta) for mode in modes]
        positive = all(item['witness'] is not None for item in proofs)
        negative = any(Q(item['reference_upper_exact']) < 0 for item in trials)
        validation.require(not (positive and negative), 'contradictory old-subspace signs')
        status = 'KNOWN_SUBSPACE_POSITIVE_LOWER' if positive else 'NEGATIVE_KNOWN_DIRECTION' if negative else 'INCONCLUSIVE_KNOWN_SUBSPACE'
        rows.append({'projection': projection, 'mu_exact': str(mu), 'rho_tail_upper_exact': str(rho),
                     'U_triangle': triangle, 'uniform_residual_upper_exact': str(residual_upper),
                     'parity_proofs': proofs, 'trial_bounds': trials, 'status': status})
        if positive:
            selected = projection; break
    validation.require(fingerprint() == before, 'source changed during diagnosis')
    return {'format': FORMAT, 'source_sha256': before, 'inputs_sha256': hashes,
            'support': packet['support'], 'known_dimension': 16, 'boundary': 54, 'residual_order': 38,
            'bits': BITS, 'mode_diagnostics': modes, 'projection_rows': rows,
            'selected_projection': selected, 'elapsed_seconds': time.perf_counter()-started,
            'scope': 'Projection choice certifies only the original P16 compression; new low directions and full P_L positivity untested.'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('analyze', 'replay'))
    parser.add_argument('--result', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prior = validation.decode_json(args.result.read_bytes()) if args.operation == 'replay' else None
    value = analyze(prior)
    if prior is not None:
        left, right = dict(value), dict(prior)
        left.pop('elapsed_seconds'); right.pop('elapsed_seconds')
        validation.require(left == right, 'altered projection consequence')
        value = {'status': 'EXACT_PROJECTION_REPLAY_PASS', 'result_sha256': hashlib.sha256(args.result.read_bytes()).hexdigest()}
    save(args.output, value)
    print(json.dumps({'status': value.get('status', 'PROJECTION_DIAGNOSED'),
                      'selected_projection': value.get('selected_projection'), 'output': str(args.output)}))


if __name__ == '__main__':
    main()
