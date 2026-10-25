"""Complete P20 consequence of retained original-v2 research inputs.

Old validators and analytical artifacts are unchanged. Original-version gate
execution is separate from the new reference and does not regenerate sources.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from flint import fmpq, fmpq_mat
from scripts import verify_weighted_low_space as exact
from scripts import verify_weighted_low_space_inputs as validation
from scripts import weil_residual_tail_bound as residual
from scripts import weil_weighted_extension_diagnostics as diagnostics
from scripts import weil_weighted_low_space as old_source

ROOT = Path(__file__).resolve().parents[1]
BITS = 352
FORMAT = 'research-complete-reprojection-v1'
AUDIT_FORMAT = 'research-complete-reprojection-audit-v1'
ORIGINAL = 'computations/2026-10-24T191616Z-weighted-support-extension/'
OLD_DATA = ORIGINAL+'data/'
COUPLING = 'computations/2026-10-25T001555Z-coupling-derived-projection/data/'
SCALARS = 'computations/2026-10-24T231555Z-tail-complement-weighted-reference/data/prior-scalars-v1.json'
SEAL_SHA = '28eff565a893a54b5ae111e6b70dd92f46d9440b736aa8ac5469bdf3b487da92'
INPUTS = {
    OLD_DATA+'extension-source-v1.json.gz': 'c9790a7b129aae0d410670830e8a472d639105d01884a041165fc119e627671e',
    OLD_DATA+'extension-audit-v1.json.gz': 'e23fa00b66d5ebe5ccc261e23b886c10e2e4fdd3f816d9a8a3dcbca38282408e',
    OLD_DATA+'extension-assessment-v1.json': 'd7569a7037021fc729987b27851e64648f8f8f1eead8123dbd3391c4ce27cb8d',
    OLD_DATA+'selection-v1.json': 'e120acab4919b9ab28e6fd6c7044053bb14514f300d810952a2d52e5dae6d7a3',
    COUPLING+'projection-v1.json': '74f8cc2e4e62af60392a1a15b02902c8ab461620f778bbd3aa657e4c78357587',
    COUPLING+'projection-audit-v1.json': '7010026f00aa906a02cf3dddf6b69c34fe266865b1178bf10ee0f032eaf87d4c',
    SCALARS: '65cc22df9e5edfbaebd9b183edbc29b179c7d3474731e24170cc9abc543a0b9a',
}
SOURCE_PATHS = tuple(dict.fromkeys((
    'scripts/weil_complete_reprojection.py', 'scripts/verify_complete_reprojection.py',
    'scripts/verify_weighted_low_space.py', 'scripts/verify_weighted_low_space_inputs.py',
    'scripts/weil_weighted_extension_diagnostics.py', 'scripts/weil_residual_tail_bound.py',
    'scripts/verify_residual_tail_bound.py', 'scripts/cert/quadrature.py',
    'scripts/cert/__init__.py', *old_source.SOURCES,
)))


def fingerprint() -> dict:
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCE_PATHS}


def save(path: Path, value: dict) -> None:
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False)+'\n')


def pinned(relative: str, expected: str) -> bytes:
    raw = (ROOT/relative).read_bytes()
    validation.require(hashlib.sha256(raw).hexdigest() == expected, 'retained bytes changed: '+relative)
    return raw


def decode(raw: bytes, compressed: bool = False) -> dict:
    return validation.decode_json(gzip.decompress(raw) if compressed else raw)


def original_manifest() -> dict:
    manifest = decode(pinned(ORIGINAL+'manifest.json', SEAL_SHA))
    return {member['path']: member for member in manifest['members']}


def archive_sources(manifest: dict) -> dict:
    return {name.removeprefix('source-v2/'): member['sha256']
            for name, member in manifest.items() if name.startswith('source-v2/')}


def baseline_inputs(selection: dict) -> dict:
    base = 'computations/2026-10-24T153012Z-weighted-reference-continuation/data/'
    return {base+'source-m626-v1.json.gz': selection['baseline_packet_sha256'],
            base+'assessment-m626-v1.json': selection['baseline_result_sha256']}


def verify_origin() -> dict:
    """Execute the original checker and exact replay in their original code tree."""
    started = time.perf_counter(); before = fingerprint(); members = original_manifest()
    selection = decode(pinned(OLD_DATA+'selection-v1.json', INPUTS[OLD_DATA+'selection-v1.json']))
    archive = archive_sources(members)
    old_inputs = {name: value for name, value in INPUTS.items() if name.startswith(ORIGINAL)}
    old_inputs.update(baseline_inputs(selection))
    for name, value in old_inputs.items():
        pinned(name, value)
    with tempfile.TemporaryDirectory(prefix='rh-original-v2-gate-') as temporary:
        isolated = Path(temporary)
        for relative, expected in archive.items():
            raw = pinned(ORIGINAL+'source-v2/'+relative, expected)
            target = isolated/relative; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
        for relative in ('check-selection-v1.py', 'source-v1/scripts/weil_weighted_extension_diagnostics.py', 'data/selection-v1.json'):
            raw = pinned(ORIGINAL+relative, members[relative]['sha256'])
            target = isolated/ORIGINAL/relative; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
        for relative, expected in baseline_inputs(selection).items():
            raw = pinned(relative, expected)
            target = isolated/relative; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
        wrapper = (
            "import pathlib,runpy,sys; root=pathlib.Path(sys.argv[1]).resolve(); "
            "mode,target=sys.argv[2:4]; sys.path.insert(0,str(root)); sys.argv=[target]+sys.argv[4:]; "
            "runpy.run_path(target,run_name='__main__') if mode=='path' else runpy.run_module(target,run_name='__main__'); "
            "loaded=[pathlib.Path(m.__file__).resolve() for name,m in sys.modules.items() "
            "if name.startswith('scripts.') and getattr(m,'__file__',None)]; "
            "assert loaded and all(p.is_relative_to(root) for p in loaded),loaded"
        )
        output = isolated/'original-exact-replay.json'
        steps = (
            ('frozen-contract', 'path', str(isolated/ORIGINAL/'check-selection-v1.py'),
             [str(ROOT/(OLD_DATA+'extension-source-v1.json.gz'))]),
            ('original-replay', 'module', 'scripts.weil_weighted_support_extension',
             ['replay', '--packet', str(ROOT/(OLD_DATA+'extension-source-v1.json.gz')),
              '--audit', str(ROOT/(OLD_DATA+'extension-audit-v1.json.gz')),
              '--result', str(ROOT/(OLD_DATA+'extension-assessment-v1.json')), '--output', str(output)]),
        )
        logs = {}
        env = os.environ.copy()
        for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
            env.setdefault(key, '1')
        for label, mode, target, arguments in steps:
            tick = time.perf_counter()
            completed = subprocess.run([sys.executable, '-I', '-c', wrapper, str(isolated), mode, target, *arguments],
                                       cwd=isolated, env=env, capture_output=True, check=False)
            logs[label] = {'exit_code': completed.returncode, 'elapsed_seconds': time.perf_counter()-tick,
                           'stdout': completed.stdout.decode('utf-8'), 'stderr': completed.stderr.decode('utf-8')}
            if completed.returncode:
                return {'status': 'ORIGINAL_V2_ACCEPTANCE_FAILED', 'steps': logs, 'source_sha256': before}
        frozen = decode(logs['frozen-contract']['stdout'].strip().encode())
        replay = decode(output.read_bytes())
    validation.require(fingerprint() == before, 'gate implementation changed during replay')
    return {'status': 'ORIGINAL_V2_ACCEPTANCE_PASS', 'source_version': 'source-v2',
            'original_manifest_sha256': SEAL_SHA, 'original_inputs_sha256': old_inputs,
            'source_archive_sha256': archive, 'source_sha256': before,
            'frozen_contract': frozen, 'replay': replay, 'steps': logs,
            'live_original_script_imports': False, 'elapsed_seconds': time.perf_counter()-started,
            'scope': 'Original-version exact acceptance/replay, not fresh analytical generation or production admission'}


def load_inputs(origin_path: Path) -> tuple[dict, dict, dict, dict, dict]:
    origin_raw = origin_path.read_bytes(); origin = decode(origin_raw)
    members = original_manifest()
    validation.require(origin['status'] == 'ORIGINAL_V2_ACCEPTANCE_PASS'
                       and origin['source_version'] == 'source-v2'
                       and origin['original_manifest_sha256'] == SEAL_SHA
                       and origin['source_archive_sha256'] == archive_sources(members)
                       and origin['source_sha256'] == fingerprint()
                       and origin['live_original_script_imports'] is False, 'original-version gate identity mismatch')
    frozen, replay = origin['frozen_contract'], origin['replay']
    validation.require(frozen['status'] == 'FULL_FROZEN_CONTRACT_PASS'
                       and frozen['packet_sha256'] == INPUTS[OLD_DATA+'extension-source-v1.json.gz']
                       and frozen['selection_sha256'] == INPUTS[OLD_DATA+'selection-v1.json']
                       and frozen['checker_sha256'] == members['check-selection-v1.py']['sha256']
                       and frozen['selector_sha256'] == members['source-v1/scripts/weil_weighted_extension_diagnostics.py']['sha256'],
                       'complete original selection not accepted')
    validation.require(replay['status'] == 'EXACT_REPLAY_PASS'
                       and replay['packet_sha256'] == INPUTS[OLD_DATA+'extension-source-v1.json.gz']
                       and replay['audit_sha256'] == INPUTS[OLD_DATA+'extension-audit-v1.json.gz']
                       and replay['result_sha256'] == INPUTS[OLD_DATA+'extension-assessment-v1.json'], 'original exact replay not accepted')
    values = {name: decode(pinned(name, expected), name.endswith('.gz')) for name, expected in INPUTS.items()}
    packet, receipt = values[OLD_DATA+'extension-source-v1.json.gz'], values[OLD_DATA+'extension-audit-v1.json.gz']
    selected = values[OLD_DATA+'selection-v1.json']
    expected_origin = {name: expected for name, expected in INPUTS.items() if name.startswith(ORIGINAL)}
    expected_origin.update(baseline_inputs(selected))
    validation.require(origin['original_inputs_sha256'] == expected_origin
                       and all(step['exit_code'] == 0 for step in origin['steps'].values()), 'original input/step binding changed')
    validation.require(packet['selection'] == selected and packet['selection_sha256'] == INPUTS[OLD_DATA+'selection-v1.json'],
                       'frozen complete selection changed')
    validation.require(packet['support'] == [1353, 2048] and packet['dimension'] == 312
                       and packet['boundary'] == 1018 and packet['residual_order'] == 38
                       and packet['bits'] == 352 and packet['basis'] == 'ordinary_unnormalized_legendre'
                       and packet['active_terms'] == [2, 3], 'wrong retained source geometry')
    validation.require(receipt['status'] == 'ALL_FRESH_SOURCE_INPUTS_ACCEPTED'
                       and receipt['packet_sha256'] == INPUTS[OLD_DATA+'extension-source-v1.json.gz']
                       and receipt['bits'] == 512 and receipt['accepted_entries'] == 758475
                       and receipt['source_sha256'] == packet['source_sha256'], 'retained receipt identity changed')
    for name, expected in packet['source_sha256'].items():
        validation.require(expected == origin['source_archive_sha256'][name], 'source not bound to original code: '+name)
    validation.require(receipt['auditor_sha256'] == origin['source_archive_sha256']['scripts/verify_weighted_support_extension_inputs.py'],
                       'original auditor source changed')
    choice, choice_audit = values[COUPLING+'projection-v1.json'], values[COUPLING+'projection-audit-v1.json']
    validation.require(choice['selected_projection'] == choice_audit['selected_projection'] == 20
                       and choice['known_dimension'] == 16
                       and choice_audit['status'] == 'RETAINED_INPUT_CONSEQUENCES_ACCEPTED'
                       and choice_audit['report_sha256'] == INPUTS[COUPLING+'projection-v1.json'], 'coupling-derived choice changed')
    identity = {'input_sha256': dict(INPUTS), 'origin_sha256': hashlib.sha256(origin_raw).hexdigest()}
    return packet, receipt, choice, values[SCALARS], identity


def weights(mu: Q, n: int, boundary: int) -> list[Q]:
    increment = Q(0); result = []
    for k in range(n, boundary+1):
        if k > n:
            increment += Q(1, k)
        result.append(1/(mu+increment))
    return result


def project_arrays(packet: dict, n: int = 20) -> tuple[list, list, list]:
    original, boundary = packet['dimension'], packet['boundary']
    validation.require(1 <= n <= original <= boundary, 'invalid retained projection geometry')
    low = [row[:n-i] for i, row in enumerate(packet['matrices']['A_K'][:n])]
    tail = [row[:n-i] for i, row in enumerate(packet['matrices']['G_K'][:n])]
    heads = [[packet['matrices']['A_K'][j][k-j] for j in range(n)] for k in range(n, original)]
    heads += [[[sum(packet['heads'][name][k-original][j][e] for name in ('V', 'P', 'RK')) for e in (0, 1)]
               for j in range(n)] for k in range(original, boundary)]
    return low, tail, heads


def positive_majorant(tail: list, heads: list, n: int, original: int, boundary: int,
                      mu: Q, bits: int = BITS) -> list:
    validation.require(1 <= n <= original <= boundary and mu > 0 and len(heads) == boundary-n,
                       'invalid full projection or tail reference')
    w = weights(mu, n, boundary); wm = w[-1]
    wp = exact._weight(wm, bits)
    coefficients = [exact._weight(w[k-n] if k < original else w[k-n]-wm, bits) for k in range(n, boundary)]
    triangle = []
    for i in range(n):
        row = []
        for j in range(i, n):
            lo, hi = exact._product(tail[i][j-i], wp)
            lo <<= bits+1; hi <<= bits+1
            for k, head, coefficient in zip(range(n, boundary), heads, coefficients, strict=True):
                product = exact._square(head[i]) if i == j else exact._product(head[i], head[j])
                a, b = exact._product(product, coefficient)
                lo += (2*k+1)*a; hi += (2*k+1)*b
            row.append(exact._round_pair(lo, hi, 2*bits+1))
        triangle.append(row)
    return triangle


def gamma_upper(tail: list, heads: list, n: int, original: int, boundary: int, bits: int = BITS) -> Q:
    total = 0
    for j in range(n):
        diagonal = tail[j][0][1] << (bits+1)
        for k in range(original, boundary):
            square, _ = exact._square(heads[k-n][j])
            diagonal -= (2*k+1)*square
        validation.require(diagonal >= 0, 'complete omitted-tail upper contradicts PSD')
        total += diagonal*(2*j+1)
    return exact._up(Q(total, 1 << (2*bits+2)), bits)


def directional_upper(heads: list, a_plus: fmpq_mat, z: list[Q], mu: Q, delta: Q,
                      n: int, boundary: int) -> dict:
    norm = sum((value*value*Q(2, 2*j+1) for j, value in enumerate(z)), Q(0))
    column = fmpq_mat([[fmpq(value.numerator, value.denominator)] for value in z])
    a = exact._q((column.transpose()*a_plus*column)[0, 0])+delta*norm
    energy = Q(0)
    # Round every head-energy contribution down for the inverse-energy lower.
    for k, weight in zip(range(n, boundary), weights(mu, n, boundary)[:-1], strict=True):
        lo = hi = Q(0)
        for value, pair in zip(z, heads[k-n], strict=True):
            first, second = Q(pair[0], 1 << BITS)*value, Q(pair[1], 1 << BITS)*value
            lo += min(first, second); hi += max(first, second)
        square = Q(0) if lo <= 0 <= hi else min(lo*lo, hi*hi)
        term = square*Q(2*k+1, 2)*Q(exact._weight(weight, BITS)[0], 1 << BITS)
        energy += Q((term*(1 << BITS)).__floor__(), 1 << BITS)
    inverse = max(Q(0), exact._sqrt(energy, BITS, False)-delta*exact._sqrt(norm/mu, BITS, True))**2
    return {'norm': str(exact._up(norm, BITS)), 'a_full_upper': str(exact._up(a, BITS)),
            'full_inverse_energy_lower': str(Q((inverse*(1 << BITS)).__floor__(), 1 << BITS)),
            'reference_upper': str(exact._up(a-inverse, BITS))}


def analyze(origin_path: Path, prior: dict | None = None) -> dict:
    started = time.perf_counter(); before = fingerprint()
    packet, receipt, choice, scalars, identity = load_inputs(origin_path)
    selected = next(row for row in choice['projection_rows'] if row['projection'] == 20)
    mu = Q(selected['mu_exact'])
    coefficients = [Q(value) for value in scalars['kernel_coefficients_exact']]
    rho = Q(scalars['scalars']['delta'][1])+residual.tail_constant(coefficients, 20)/(20*21)
    expected_mu = exact._harmonic(20)-Q(scalars['scalars']['c_T'][1])-Q(scalars['scalars']['arithmetic'][1])-rho
    validation.require(mu == expected_mu > 0, 'new projection complement changed')
    low, tail, heads = project_arrays(packet)
    upper_triangle = positive_majorant(tail, heads, 20, 312, 1018, mu)
    a_minus, a_plus, _ = exact._order_bounds(low, BITS)
    _, u_plus, _ = exact._order_bounds(upper_triangle, BITS)
    delta = Q(packet['delta'][1], 1 << BITS); cross = Q(packet['cross_norm_upper'])
    charge = diagnostics.uniform_residual(delta, cross, mu)
    lower = a_minus-u_plus
    for j in range(20):
        amount = charge*Q(2, 2*j+1)
        lower[j, j] -= fmpq(amount.numerator, amount.denominator)
    blocks = []
    for parity in (0, 1):
        indices = list(range(parity, 20, 2))
        block_matrix = fmpq_mat([[lower[i, j] for j in indices] for i in indices])
        if prior is None:
            proof = exact._positive_proof(block_matrix)
            trial = exact._candidate(block_matrix, indices, 20)
        else:
            old = prior['blocks'][parity]
            validation.require(old['parity'] == parity, 'altered parity inventory')
            proof = old['positive_lower_witness']; trial = [Q(value) for value in old['trial']]
            if proof is not None:
                validation.require(exact._verify_congruence(block_matrix, proof) == Q(proof['exact_margin']), 'altered congruence margin')
        validation.require(len(trial) == 20 and any(trial)
                           and all(not trial[j] for j in range(1-parity, 20, 2)), 'invalid complete parity trial')
        gap = None
        if proof is not None:
            trace = sum((Q(value, proof['denominator'])**2*Q(2, 2*indices[j]+1)
                         for row in proof['numerators'] for j, value in enumerate(row)), Q(0))
            gap = str(Q(proof['exact_margin'])/trace)
        blocks.append({'parity': parity, 'positive_lower_witness': proof, 'mass_normalized_gap_exact': gap,
                       'trial': list(map(str, trial)),
                       'directional_check': directional_upper(heads, a_plus, trial, mu, delta, 20, 1018)})
    positive = all(block['positive_lower_witness'] is not None for block in blocks)
    negative = any(Q(block['directional_check']['reference_upper']) < 0 for block in blocks)
    validation.require(not (positive and negative), 'contradictory complete reference signs')
    gamma = gamma_upper(tail, heads, 20, 312, 1018)
    validation.require(fingerprint() == before, 'source changed during full reprojection')
    return {'format': FORMAT, 'source_sha256': before, **identity,
            'support': [1353, 2048], 'dimension': 20, 'origin_dimension': 312, 'boundary': 1018,
            'residual_order': 38, 'bits': BITS, 'mu_reference_exact': str(mu),
            'cross_norm_upper': packet['cross_norm_upper'], 'delta': packet['delta'],
            'A_K_triangle': low, 'U_triangle': upper_triangle, 'residual_allowance_exact': str(charge),
            'gamma_upper_exact': str(gamma), 'tail_loss_upper_exact': str(exact._up(weights(mu, 20, 1018)[-1]*gamma, BITS)),
            'blocks': blocks, 'status': 'POSITIVE_REFERENCE_LOWER' if positive else 'NEGATIVE_REFERENCE_DIRECTION' if negative else 'INCONCLUSIVE_LOWER',
            'scope': 'Complete P20 source-conditional research reference; no production admission or full spectral minimum.',
            'input_provenance': 'RETAINED_C0087_ORIGINAL_V2_NO_REGENERATION',
            'elapsed_seconds': time.perf_counter()-started}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('origin', 'analyze', 'replay'))
    parser.add_argument('--origin', type=Path)
    parser.add_argument('--result', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    validation.require(not args.output.exists(), 'refusing previous research output')
    if args.operation == 'origin':
        value = verify_origin()
    else:
        prior = decode(args.result.read_bytes()) if args.operation == 'replay' else None
        value = analyze(args.origin, prior)
        if prior is not None:
            left, right = dict(value), dict(prior); left.pop('elapsed_seconds'); right.pop('elapsed_seconds')
            validation.require(left == right, 'altered complete reference consequence')
            value = {'status': 'EXACT_COMPLETE_REPROJECTION_REPLAY_PASS',
                     'result_sha256': hashlib.sha256(args.result.read_bytes()).hexdigest(),
                     'origin_sha256': hashlib.sha256(args.origin.read_bytes()).hexdigest()}
    save(args.output, value)
    print(json.dumps({'status': value.get('status'), 'output': str(args.output)}))
    if value.get('status') == 'ORIGINAL_V2_ACCEPTANCE_FAILED':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
