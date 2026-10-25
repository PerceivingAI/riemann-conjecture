"""One structurally selected weighted support extension, research only.

Uses a new parameter-bearing packet. Fixed historical sources and admissions
remain unchanged. The low-space arithmetic kernel is reused on its generic
finite-matrix interface, with RK mapped to its internal component slot.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

from flint import arb, arb_mat, ctx, fmpq, fmpq_mat, fmpq_poly
from scripts import verify_weighted_low_space as exact
from scripts import verify_weighted_low_space_inputs as old_inputs
from scripts import weil_weighted_low_space as old_source
from scripts import weil_weighted_extension_diagnostics as diagnostics
from scripts.cert.constants import c_T_enclosure
from scripts.cert.legendre_schur import harmonic, legendre_polynomials
from scripts.cert.mixed_gram_research import assemble_truncated_mixed_gram
from scripts.cert.multi_prime_legendre_schur import _residual_rho, _residual_truncation_operator
from scripts.cert.prime_power_terms import (
    _affine_legendre, _exact_inner, combined_piecewise_images,
    enumerate_active_prime_power_terms,
)

ROOT = Path(__file__).resolve().parents[1]
BITS = 352
FORMAT = 'research-weighted-support-extension-source-v1'
AUDIT_FORMAT = 'research-weighted-support-extension-audit-v1'
RESULT_FORMAT = 'research-weighted-support-extension-assessment-v1'
SOURCE_PATHS = tuple(dict.fromkeys((
    'scripts/weil_weighted_support_extension.py',
    'scripts/weil_weighted_extension_diagnostics.py',
    'scripts/verify_weighted_low_space.py',
    'scripts/verify_weighted_low_space_inputs.py',
    *old_source.SOURCES,
)))


def fingerprint(paths=SOURCE_PATHS) -> dict:
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in paths}


def save(path: Path, value: dict) -> None:
    blob = (json.dumps(value, indent=2, allow_nan=False)+'\n').encode()
    if path.suffix == '.gz':
        blob = gzip.compress(blob, mtime=0)
    with path.open('xb') as stream:
        stream.write(blob)


def generate_low(t: Q, n: int, order: int, precision: int) -> dict:
    built = assemble_truncated_mixed_gram(n, precision, order, t.numerator, t.denominator)
    with ctx.workprec(precision):
        constant = c_T_enclosure(precision, t.numerator, t.denominator)
        a = [[built['V'][i][j]+built['P'][i][j]+built['Rk'][i][j]
              for j in range(n)] for i in range(n)]
        for j in range(n):
            hj = harmonic(j)
            a[j][j] += arb(2)/(2*j+1)*(arb(hj.numerator)/hj.denominator-constant)
        hn = harmonic(n)
        complement = arb(hn.numerator)/hn.denominator-constant
        complement -= _residual_rho(diagnostics.ar(t), order)
        complement -= sum((term.coefficient for term in built['active_terms']), arb(0))
        return {'matrices': {'A_K': old_source.triangular(a),
                             'G_K': old_source.triangular(built['Gk'])},
                'delta': old_source.publish(built['delta_R']),
                'complement': old_source.publish(complement)}


def generate_heads(t: Q, n: int, order: int, boundary: int, precision: int) -> tuple[dict, str]:
    with ctx.workprec(precision):
        polys = legendre_polynomials(boundary-1)
        basis = [fmpq_poly([fmpq(c.numerator, c.denominator) for c in p]) for p in polys]
        terms = enumerate_active_prime_power_terms(t.numerator, t.denominator, precision)
        if [term.m for term in terms] != [2, 3]:
            raise ValueError('selected support lost its active set')
        points, pieces = combined_piecewise_images(polys[:n], terms, prec=precision)
        arithmetic = arb_mat(boundary-n, n)
        for ci, (a, b) in enumerate(zip(points[:-1], points[1:])):
            if not pieces[0][ci].legendre_coefficients:
                continue
            radius = (b-a)/2
            table = _affine_legendre(boundary-1, (a+b)/2, radius)
            high = arb_mat([list(table[k][:n]) for k in range(n, boundary)])
            low = arb_mat(n, n)
            for j in range(n):
                for r, value in enumerate(pieces[j][ci].legendre_coefficients):
                    low[j, r] = value*2*radius/(2*r+1)
            arithmetic += high*low.transpose()
        images, _, _, _ = _residual_truncation_operator(
            polys[:n], order, precision, t.numerator, t.denominator)
        if any(p.degree() > j+order for j, p in enumerate(images)):
            raise ValueError('residual image degree exceeds the selected source bound')
        heads = {name: [] for name in ('V', 'P', 'RK')}
        for row, k in enumerate(range(n, boundary)):
            entries = {name: [] for name in heads}
            for j in range(n):
                if (k-j) % 2:
                    if not arithmetic[row, j].contains(0):
                        raise ValueError('source excludes exact cross-parity zero')
                    values = (arb(0), arb(0), arb(0))
                else:
                    values = (arb(fmpq(2, k*(k+1)-j*(j+1))), arithmetic[row, j],
                              arb(_exact_inner(basis[k], images[j])) if k <= images[j].degree() else arb(0))
                for name, value in zip(heads, values, strict=True):
                    entries[name].append(old_source.publish(value))
            for name in heads:
                heads[name].append(entries[name])
        return heads, old_source.signature(images)


def generate(selection_path: Path) -> dict:
    started = time.perf_counter()
    raw = selection_path.read_bytes()
    selected = old_inputs.decode_json(raw)
    current = diagnostics.select_parameters()
    for name in ('format', 'support', 'dimension', 'residual_order', 'boundary', 'bits',
                 'active_terms', 'mu_reference_exact', 'basis', 'source_precision', 'head_precision'):
        if selected[name] != current[name]:
            raise ValueError('selected mathematical parameter changed: '+name)
    t = Q(*selected['support'])
    n, order, boundary = (selected[name] for name in ('dimension', 'residual_order', 'boundary'))
    before = fingerprint()
    print(f'BUILDING_FRESH_LOW T={t} N={n} K={order}', file=sys.stderr, flush=True)
    low = generate_low(t, n, order, selected['source_precision'])
    print(f'BUILDING_FRESH_HEAD m={boundary}', file=sys.stderr, flush=True)
    heads, signature = generate_heads(t, n, order, boundary, selected['head_precision'])
    if fingerprint() != before:
        raise ValueError('source bytes changed during generation')
    return {**{name: selected[name] for name in ('support', 'dimension', 'residual_order',
                'boundary', 'bits', 'active_terms', 'mu_reference_exact', 'basis',
                'source_precision', 'head_precision')},
            'format': FORMAT, 'selection': selected, 'cross_norm_upper': current['cross_norm_upper'],
            'selection_sha256': hashlib.sha256(raw).hexdigest(),
            'source_sha256': before, **low, 'heads': heads,
            'residual_signature': signature, 'elapsed_seconds': time.perf_counter()-started,
            'scope': 'Fresh research sources, no theorem admission or clean-production claim'}


def validate_packet(packet: dict) -> None:
    required = {'format': FORMAT, 'bits': BITS, 'basis': 'ordinary_unnormalized_legendre',
                'active_terms': [2, 3]}
    for name, expected in required.items():
        old_inputs.require(type(packet.get(name)) is type(expected) and packet[name] == expected,
                           'extension header mismatch: '+name)
    selected = packet['selection']
    expected_selection = diagnostics.select_parameters()
    old_inputs.require(selected['format'] == expected_selection['format'],
                       'unknown geometric selection rule')
    for name in ('support', 'dimension', 'residual_order', 'boundary', 'bits', 'active_terms',
                 'mu_reference_exact', 'basis', 'source_precision', 'head_precision'):
        old_inputs.require(type(packet[name]) is type(selected[name]) and packet[name] == selected[name],
                           'selection/payload mismatch: '+name)
        old_inputs.require(packet[name] == expected_selection[name],
                           'payload differs from the executed geometric rule: '+name)
    old_inputs.require(packet.get('cross_norm_upper') == expected_selection['cross_norm_upper'],
                       'uniform cross-norm bound differs from the selected source')
    n, m, order = (packet[name] for name in ('dimension', 'boundary', 'residual_order'))
    old_inputs.require(all(type(x) is int for x in (n, m, order)), 'noninteger dimensions')
    old_inputs.require(n >= 2 and n % 2 == 0 and order >= 8 and order % 2 == 0
                       and m >= n+order and m % 2 == 0, 'invalid selected source geometry')
    old_inputs.require(type(packet['support']) is list and len(packet['support']) == 2
                       and all(type(v) is int for v in packet['support'])
                       and packet['support'][1] > 0, 'invalid exact rational support')
    old_inputs.require(set(packet['matrices']) == {'A_K', 'G_K'}
                       and set(packet['heads']) == {'V', 'P', 'RK'}, 'source components mismatch')
    for name in ('A_K', 'G_K'):
        old_inputs._rows(packet['matrices'][name], list(range(n, 0, -1)), name)
    for name in ('V', 'P', 'RK'):
        old_inputs._rows(packet['heads'][name], [n]*(m-n), name)
    for name in ('delta', 'complement'):
        old_inputs.validate_pair(packet[name], name)
    old_inputs.require(Q(packet['mu_reference_exact']) > 0 and packet['delta'][0] >= 0,
                       'invalid positive reserve or residual')
    old_inputs.require(packet['source_sha256'] == fingerprint(), 'source byte identity changed')


def arithmetic_packet(packet: dict) -> dict:
    # The unchanged finite-matrix kernel adds three component arrays. Its slot
    # name R32 is internal here; the new packet and analytical source use RK/K.
    return {**packet, 'heads': {'V': packet['heads']['V'], 'P': packet['heads']['P'],
                              'R32': packet['heads']['RK']}}


def load_accepted(packet_path: Path, audit_path: Path) -> tuple[dict, str, str]:
    raw, raw_audit = packet_path.read_bytes(), audit_path.read_bytes()
    packet = old_inputs.decode_json(gzip.decompress(raw))
    audit = old_inputs.decode_json(gzip.decompress(raw_audit))
    validate_packet(packet)
    sha = hashlib.sha256(raw).hexdigest()
    old_inputs.require(audit['format'] == AUDIT_FORMAT and audit['status'] == 'ALL_FRESH_SOURCE_INPUTS_ACCEPTED'
                       and audit['packet_sha256'] == sha and audit['bits'] == 512,
                       'independent receipt identity mismatch')
    for name in ('support', 'dimension', 'residual_order', 'boundary', 'source_sha256',
                 'residual_signature', 'mu_reference_exact'):
        old_inputs.require(audit[name] == packet[name], 'receipt source mismatch: '+name)
    auditor = 'scripts/verify_weighted_support_extension_inputs.py'
    old_inputs.require(audit['auditor_sha256'] == fingerprint((auditor,))[auditor],
                       'independent auditor byte identity changed')
    old_inputs.require(0 < Q(packet['mu_reference_exact']) <= Q(audit['complement_lower_exact']),
                       'chosen mu exceeds fresh independent complement')
    old_inputs.require(audit['cross_norm_upper'] == packet['cross_norm_upper']
                       and Q(audit['cross_norm_reference_upper_exact']) <= Q(packet['cross_norm_upper']),
                       'uniform cross norm is not independently accepted')
    shift = audit['bits']-packet['bits']
    def contained(source, reference):
        old_inputs.validate_pair(reference, 'reference receipt')
        old_inputs.require(source[0] << shift <= reference[0] <= reference[1] <= source[1] << shift,
                           'independent reference interval escaped source')
    count = 1  # Independently accepted uniform cross-norm upper.
    for category, names in (('matrices', ('A_K', 'G_K')), ('heads', ('V', 'P', 'RK'))):
        for name in names:
            for source_row, reference_row in zip(packet[category][name], audit[category][name], strict=True):
                for source, reference in zip(source_row, reference_row, strict=True):
                    contained(source, reference)
                    count += 1
    for name in ('delta', 'complement'):
        contained(packet[name], audit[name])
        count += 1
    old_inputs.require(count == audit['accepted_entries'], 'incomplete accepted source count')
    return packet, sha, hashlib.sha256(raw_audit).hexdigest()


def matrices_for(packet: dict) -> dict:
    matrices = exact.weighted_matrices(arithmetic_packet(packet))
    bound = Q(packet['cross_norm_upper'])
    residual = diagnostics.uniform_residual(matrices['delta'], bound, matrices['mu'])
    old_inputs.require(residual <= Q(packet['selection']['residual_allowance_limit']),
                       'published full residual exceeds the selected budget')
    old = matrices['residual']
    for j in range(packet['dimension']):
        value = (old-residual)*Q(2, 2*j+1)
        matrices['lower'][j, j] += fmpq(value.numerator, value.denominator)
    matrices['trace_residual'] = old
    matrices['residual'] = residual
    matrices['cross_norm_upper'] = bound
    return matrices


def assess(packet: dict, sha: str, audit_sha: str, prior: dict | None = None) -> dict:
    matrices = matrices_for(packet)
    n, bits = packet['dimension'], packet['bits']
    blocks = []
    for parity in (0, 1):
        indices = list(range(parity, n, 2))
        lower = fmpq_mat([[matrices['lower'][i, j] for j in indices] for i in indices])
        if prior is None:
            proof = exact._positive_proof(lower)
            trial = exact._candidate(lower, indices, n)
        else:
            block = prior['blocks'][parity]
            old_inputs.require(block['parity'] == parity, 'altered parity inventory')
            proof = block['positive_lower_witness']
            if proof is not None:
                old_inputs.require(exact._verify_congruence(lower, proof) == Q(proof['exact_margin']),
                                   'altered exact congruence margin')
            trial = [Q(v) for v in block['trial']]
        old_inputs.require(len(trial) == n and any(trial)
                           and all(not trial[j] for j in range(1-parity, n, 2)),
                           'invalid parity trial')
        directional = exact.directional_upper(arithmetic_packet(packet), matrices, trial)
        normalized_gap = None
        if proof is not None:
            witness = fmpq_mat([[fmpq(v, proof['denominator']) for v in row]
                               for row in proof['numerators']])
            mass_trace = sum((Q(int(witness[i, j].p), int(witness[i, j].q))**2
                              *Q(2, 2*indices[j]+1) for i in range(len(indices))
                              for j in range(len(indices))), Q())
            normalized_gap = str(Q(proof['exact_margin'])/mass_trace)
        blocks.append({'parity': parity, 'positive_lower_witness': proof,
                       'mass_normalized_gap': normalized_gap, 'trial': [str(v) for v in trial],
                       'directional_check': directional,
                       'negative_reference_direction': Q(directional['reference_upper']) < 0,
                       'losses': diagnostics._point(arithmetic_packet(packet), matrices, trial)})
    positive = all(b['positive_lower_witness'] is not None for b in blocks)
    negative = any(b['negative_reference_direction'] for b in blocks)
    old_inputs.require(not (positive and negative), 'contradictory exact signs')
    status = 'NEGATIVE_REFERENCE_DIRECTION' if negative else 'POSITIVE_REFERENCE_LOWER' if positive else 'INCONCLUSIVE_LOWER'
    return {'format': RESULT_FORMAT, 'status': status, 'packet_sha256': sha,
            'audit_sha256': audit_sha,
            **{name: packet[name] for name in ('support', 'dimension', 'residual_order', 'boundary')},
            'blocks': blocks, 'gamma_upper': str(exact._up(matrices['gamma'], bits)),
            'tail_loss_upper': str(matrices['theta']), 'residual_allowance': str(matrices['residual']),
            'trace_residual_allowance': str(matrices['trace_residual']),
            'cross_norm_upper': str(matrices['cross_norm_upper']),
            'A_one_sided_error': str(matrices['A_one_sided_error']),
            'U_one_sided_error': str(matrices['U_one_sided_error']),
            'scope': 'Source-conditional fixed-support research reference; not production theorem admission, true-inverse evaluation, novelty or RH'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('generate', 'assess', 'replay'))
    parser.add_argument('--selection', type=Path)
    parser.add_argument('--packet', type=Path)
    parser.add_argument('--audit', type=Path)
    parser.add_argument('--result', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('refusing to overwrite existing evidence')
    if args.operation == 'generate':
        value = generate(args.selection)
    else:
        packet, sha, audit_sha = load_accepted(args.packet, args.audit)
        previous = diagnostics.read_json(args.result) if args.operation == 'replay' else None
        value = assess(packet, sha, audit_sha, previous)
        if previous is not None:
            old_inputs.require(value == previous, 'altered exact assessment or binding')
            value = {'status': 'EXACT_REPLAY_PASS', 'packet_sha256': sha,
                     'audit_sha256': audit_sha, 'result_sha256': hashlib.sha256(args.result.read_bytes()).hexdigest()}
    save(args.output, value)
    print(json.dumps({'status': value.get('status', 'SOURCE_GENERATED'), 'output': str(args.output)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
