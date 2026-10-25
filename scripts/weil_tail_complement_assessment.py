"""Fixed-support weighted reference with C-0088's tail complement, research only.

No historical packet, full cross-block norm or production admission is changed.
Head accuracy uses a fixed geometric ladder, not a support/dimension search.
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

from flint import acb, arb, ctx

from scripts import verify_weighted_low_space as exact
from scripts import verify_weighted_low_space_inputs as validation
from scripts import weil_residual_tail_bound as scalar
from scripts import weil_weighted_low_space as publishing
from scripts import weil_weighted_support_extension as legacy
from scripts import weil_weighted_extension_diagnostics as diagnostics
from scripts.cert.constants import c_T_enclosure
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms
from scripts.cert.residual_kernel import _suzuki_residual_tail_radius

ROOT = Path(__file__).resolve().parents[1]
BITS = 352
FORMAT = 'research-tail-complement-source-v1'
AUDIT_FORMAT = 'research-tail-complement-audit-v1'
RESULT_FORMAT = 'research-tail-complement-assessment-v1'
AUDITOR_PATHS = (
    'scripts/verify_tail_complement_inputs.py',
    'scripts/verify_weighted_support_extension_inputs.py',
    'scripts/verify_weighted_low_space_inputs.py',
    'scripts/verify_combined_schur_analytic_entries.py',
    'scripts/verify_residual_tail_bound.py',
)
SOURCE_PATHS = tuple(dict.fromkeys((
    'scripts/weil_tail_complement_assessment.py', *AUDITOR_PATHS,
    'scripts/weil_residual_tail_bound.py', 'scripts/cert/quadrature.py',
    'scripts/cert/__init__.py', *legacy.SOURCE_PATHS,
)))


def fingerprint(paths=SOURCE_PATHS) -> dict:
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in paths}


def save(path: Path, value: dict) -> None:
    legacy.save(path, value)


def selection(boundary: int | None = None) -> dict:
    scalars = scalar.evaluate()
    row = next(row for row in scalars['rows'] if row['dimension'] == 16)
    baseline = validation.decode_json((ROOT/scalar.BASELINE).read_bytes())
    mu = Q(row['mu_tail_lower_exact'])
    reserve = Q(baseline['mu_reference_exact'])
    validation.require(mu >= reserve > 0, 'new complement loses the original reserve')
    cap = Q(baseline['selected_weight_upper'])
    initial = 54
    while 1/(mu+exact._harmonic(initial)-exact._harmonic(16)) > cap:
        initial += 2
    if boundary is None:
        boundary = initial
    validation.require(type(boundary) is int and boundary >= initial, 'invalid head boundary')
    selected, level = initial, 0
    while selected < boundary:
        selected = 16+2*(selected-16)
        level += 1
    validation.require(selected == boundary, 'boundary is outside the geometric head ladder')
    with ctx.workprec(512):
        cross = diagnostics.cross_norm_bound(Q(1353, 2048), 38)
    return {
        'support': [1353, 2048], 'dimension': 16, 'residual_order': 38,
        'boundary': boundary, 'bits': BITS, 'active_terms': [2, 3],
        'basis': 'ordinary_unnormalized_legendre',
        'source_precision': 768, 'head_precision': max(768, 5*boundary+256),
        'mu_reference_exact': str(mu), 'minimum_reserve_exact': str(reserve),
        'tail_constant_exact': row['M_exact'],
        'rho_tail_upper_exact': row['rho_tail_upper_exact'],
        'cross_norm_upper': str(cross),
        'residual_allowance_limit': baseline['residual_allowance_upper'],
        'initial_boundary': initial, 'head_refinement_level': level,
        'head_rule': 'double retained tail-row count after inconclusive whole-reference assessment',
        'baseline_selection_sha256': scalar.BASELINE_SHA256,
    }


def generate(boundary: int | None = None) -> dict:
    started = time.perf_counter()
    selected = selection(boundary)
    before = fingerprint()
    t, n, order = Q(*selected['support']), 16, 38
    print(f'FRESH_LOW T={t} N={n} K={order}', file=sys.stderr, flush=True)
    low = legacy.generate_low(t, n, order, selected['source_precision'])
    with ctx.workprec(selected['source_precision']):
        T = diagnostics.ar(t)
        delta = 2*T*_suzuki_residual_tail_radius(acb(2*T), order)
        terms = enumerate_active_prime_power_terms(t.numerator, t.denominator, selected['source_precision'])
        validation.require([term.m for term in terms] == [2, 3] and all(1 < term.tau < 2 for term in terms),
                           'arithmetic norm-one window changed')
        rho = delta+diagnostics.ar(Q(selected['tail_constant_exact']))/(n*(n+1))
        complement = (diagnostics.ar(exact._harmonic(n))
                      -c_T_enclosure(selected['source_precision'], t.numerator, t.denominator)
                      -sum((term.coefficient for term in terms), arb(0))-rho)
        low['complement'] = publishing.publish(complement)
    print(f'FRESH_HEAD m={selected["boundary"]}', file=sys.stderr, flush=True)
    heads, signature = legacy.generate_heads(t, n, order, selected['boundary'], selected['head_precision'])
    validation.require(fingerprint() == before, 'source changed during generation')
    return {**selected, 'format': FORMAT, 'selection': selected,
            'source_sha256': before, **low, 'heads': heads, 'residual_signature': signature,
            'elapsed_seconds': time.perf_counter()-started,
            'scope': 'Fresh same-support research sources; no production or clean-source admission'}


def validate_packet(packet: dict) -> None:
    validation.require(type(packet) is dict and packet.get('format') == FORMAT, 'wrong research source format')
    expected = selection(packet.get('boundary'))
    validation.require(json.dumps(packet.get('selection'), sort_keys=True, allow_nan=False)
                       == json.dumps(expected, sort_keys=True, allow_nan=False), 'selection contract changed')
    for name, value in expected.items():
        validation.require(type(packet.get(name)) is type(value) and packet[name] == value,
                           'source selection mismatch: '+name)
    n, m = packet['dimension'], packet['boundary']
    validation.require(set(packet['matrices']) == {'A_K', 'G_K'}
                       and set(packet['heads']) == {'V', 'P', 'RK'}, 'source components changed')
    for name in ('A_K', 'G_K'):
        validation._rows(packet['matrices'][name], list(range(n, 0, -1)), name)
    for name in ('V', 'P', 'RK'):
        validation._rows(packet['heads'][name], [n]*(m-n), name)
    for name in ('delta', 'complement'):
        validation.validate_pair(packet[name], name)
    validation.require(packet['delta'][0] >= 0 and Q(packet['mu_reference_exact']) > 0,
                       'invalid residual or positive reference')
    validation.require(packet['source_sha256'] == fingerprint(), 'source byte identity changed')


def load_accepted(packet_path: Path, audit_path: Path) -> tuple[dict, str, str]:
    raw, audit_raw = packet_path.read_bytes(), audit_path.read_bytes()
    packet = validation.decode_json(gzip.decompress(raw))
    audit = validation.decode_json(gzip.decompress(audit_raw))
    validate_packet(packet)
    sha = hashlib.sha256(raw).hexdigest()
    validation.require(audit['format'] == AUDIT_FORMAT and audit['status'] == 'ALL_FRESH_SOURCE_INPUTS_ACCEPTED'
                       and audit['packet_sha256'] == sha and audit['bits'] == 512, 'audit identity mismatch')
    for name in ('support', 'dimension', 'residual_order', 'boundary', 'source_sha256',
                 'residual_signature', 'mu_reference_exact', 'tail_constant_exact'):
        validation.require(audit[name] == packet[name], 'audit source mismatch: '+name)
    validation.require(audit['auditor_sha256'] == fingerprint(AUDITOR_PATHS[:1])[AUDITOR_PATHS[0]]
                       and audit['audit_source_sha256'] == fingerprint(AUDITOR_PATHS), 'audit source changed')
    validation.require(0 < Q(packet['mu_reference_exact']) <= Q(audit['complement_lower_exact']),
                       'reference exceeds independently reconstructed complement')
    validation.require(Q(audit['rho_tail_reference_upper_exact']) <= Q(packet['rho_tail_upper_exact']),
                       'tail norm upper not independently accepted')
    validation.require(audit['cross_norm_upper'] == packet['cross_norm_upper']
                       and Q(audit['cross_norm_reference_upper_exact']) <= Q(packet['cross_norm_upper']),
                       'full cross norm not accepted')
    n, m = packet['dimension'], packet['boundary']
    shift = audit['bits']-packet['bits']
    count = 1
    for category, names in (('matrices', ('A_K', 'G_K')), ('heads', ('V', 'P', 'RK'))):
        for name in names:
            lengths = list(range(n, 0, -1)) if category == 'matrices' else [n]*(m-n)
            validation._rows(audit[category][name], lengths, 'audit '+name)
            for source_row, reference_row in zip(packet[category][name], audit[category][name], strict=True):
                for source, reference in zip(source_row, reference_row, strict=True):
                    validation.require(source[0] << shift <= reference[0] <= reference[1] <= source[1] << shift,
                                       'independent reference interval escaped source')
                    count += 1
    for name in ('delta', 'complement'):
        reference, source = audit[name], packet[name]
        validation.validate_pair(reference, name)
        validation.require(source[0] << shift <= reference[0] <= reference[1] <= source[1] << shift,
                           'independent scalar escaped source')
        count += 1
    validation.require(count == audit['accepted_entries'] == n*(n+1)+3*(m-n)*n+3,
                       'incomplete source acceptance')
    validation.require(audit['low_input_provenance'] == 'FRESH_NATIVE_NO_REUSE'
                       and audit['reference_precision'] == 2*packet['source_precision']
                       and audit['head_reference_precision'] == 2*packet['head_precision'],
                       'audit precision or freshness changed')
    return packet, sha, hashlib.sha256(audit_raw).hexdigest()


def assess(packet: dict, sha: str, audit_sha: str, prior: dict | None = None) -> dict:
    result = legacy.assess(packet, sha, audit_sha, prior)
    result['format'] = RESULT_FORMAT
    result['mu_reference_exact'] = packet['mu_reference_exact']
    result['tail_complement_rule'] = 'C-0088 double-compressed residual with full remainder'
    result['scope'] = 'Same-support research reference dimension assessment; not production admission, optimality or RH'
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('select', 'generate', 'assess', 'replay', 'refine'))
    parser.add_argument('--boundary', type=int)
    parser.add_argument('--packet', type=Path)
    parser.add_argument('--audit', type=Path)
    parser.add_argument('--result', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('refusing to overwrite research evidence')
    if args.operation == 'select':
        value = selection(args.boundary)
    elif args.operation == 'generate':
        value = generate(args.boundary)
    else:
        packet, sha, audit_sha = load_accepted(args.packet, args.audit)
        if args.operation == 'assess':
            value = assess(packet, sha, audit_sha)
        else:
            previous = validation.decode_json(args.result.read_bytes())
            value = assess(packet, sha, audit_sha, previous)
            validation.require(value == previous, 'altered exact assessment or binding')
            if args.operation == 'replay':
                value = {'status': 'EXACT_REPLAY_PASS', 'packet_sha256': sha, 'audit_sha256': audit_sha,
                         'result_sha256': hashlib.sha256(args.result.read_bytes()).hexdigest()}
            else:
                validation.require(previous['status'] == 'INCONCLUSIVE_LOWER',
                                   'head refinement requires an inconclusive reference assessment')
                value = selection(16+2*(packet['boundary']-16))
                value['prior_packet_sha256'] = sha
                value['prior_result_sha256'] = hashlib.sha256(args.result.read_bytes()).hexdigest()
    save(args.output, value)
    print(json.dumps({'status': value.get('status', 'SOURCE_OR_SELECTION_WRITTEN'), 'output': str(args.output)}))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
