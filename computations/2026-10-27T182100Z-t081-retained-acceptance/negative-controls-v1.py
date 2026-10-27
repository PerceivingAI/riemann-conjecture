"""Nine retained false-input probes for the frozen T81/100 candidate.

CLI: --output FRESH.json, confined beneath this bundle's data/ directory.
The output owns a fresh <output-stem>-cases/ directory. Summary fields are
format, status, candidate_source_sha256, candidate_manifest_sha256,
case_directory, native_batch_proof, files, and cases. Every cases[] record has
case, passed, consumer, source_sha256, expected, and files[{path,bytes,sha256}].
All file paths in these two files arrays are relative to case_directory.
case-result.json records the assessment before the enclosing files inventory.

The six native probes share ONE fresh independent parity-0 reconstruction.
All three original even families, 256473 triangular entries, must pass the
unchanged native check_matrix before any false packet is tried. This is an
efficient local SUBSET probe, not a standalone full source audit, a general
untrusted-input verifier, or a replacement for the separate fresh full replay.
The same python-flint/Arb arithmetic and Gauss enclosures remain a shared
premise. No producer module is imported and no consumer predicate is changed.

The three exact probes use the unchanged exact CLI, full 413-dimensional
transforms, and deterministic gzip proposals bound to the raw source bytes.
The artificial negative source is explicitly NOT analytic truth or actual
Weil negativity. No adversarial source is allowed a candidate PASS status.
All old research files remain untouched. A failed original native control
retains its receipt and aborts before adversarial cases can be assessed.
"""
import argparse
import copy
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_PIN = 'f69fee0feb9c08833ad6a3091718c9a6a301e5b5ddbea96ee5f0f6c0553c8b6e'
MANIFEST_PIN = 'b44bdfcb3567e9182b659b0037edc7bdca4fe464dfca6eebd595ac5c93debe24'
NATIVE_PIN = '4bc4d25db589fe987bb2c7f78f31bd7dc83849666daae82b017295db30d94720'
EXACT_PIN = 'def3d7d7d242a319c9f93fec39674c2c2cf40796b653ddb44f47df2e8019fd64'
INPUTS_PIN = '19eac80d7869fcc6d6ddd0d33dcb90901b65254b2f076c6964148575019982a1'
DIM, BITS, SCALE = 413, 256, 1 << 256
KINDS = ('A_model', 'weighted_head', 'weighted_complete_tail')
THREADS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS',
           'FLINT_NUM_THREADS')
CASES = (
    ('wrongactual-lowconstant', 'source', 'A_model',
     'source enclosure fails at A_model-0 cell (0, 0)'),
    ('underpaidweightedhead', 'source', 'weighted_head',
     'source enclosure fails at weighted_head-0 cell (0, 0)'),
    ('omitted-complete-physicalexterior', 'source', 'weighted_complete_tail',
     'source enclosure fails at weighted_complete_tail-0 cell (0, 0)'),
    ('underpaid-terminal-inverseweight', 'source', None,
     'inverse weights differ from declaration'),
    ('omitted-prime5-low-term', 'source', 'A_model',
     'source enclosure fails at A_model-0 cell (0, 0)'),
    ('omitted-prime5-mixed-square', 'source', 'weighted_complete_tail',
     'source enclosure fails at weighted_complete_tail-0 cell (0, 0)'),
    ('singular-fullspace-witness', 'exact', None, 'singular full congruence'),
    ('synthetic-selected-negative', 'exact', None,
     'SELECTED_CONSERVATIVE_SCHUR_NEGATIVE_NOT_WEIL_NEGATIVITY'),
    ('numerical-width-uncertainty', 'exact', None, 'NUMERICAL_WIDTH_GOAL_FAILED'),
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(items):
    result = {}
    for key, value in items:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def load(raw):
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode('utf-8')


def fresh(path, raw):
    with path.open('xb') as handle:
        handle.write(raw)


def confined(base, relative):
    require(type(relative) is str and relative and '\\' not in relative and
            '\x00' not in relative and ':' not in relative, 'portable relative path required')
    require(not PurePosixPath(relative).is_absolute() and
            not PureWindowsPath(relative).drive and
            all(part not in ('', '.', '..') for part in relative.split('/')),
            'invalid relative path component')
    path = (base / relative).resolve()
    require(path.is_relative_to(base.resolve()), 'path escapes bound directory')
    return path


def file_record(path, base):
    raw = path.read_bytes()
    return {'path': path.relative_to(base).as_posix(), 'bytes': len(raw), 'sha256': digest(raw)}


def capture():
    """Validate all 33 size-bearing members and the nine captured project pins."""
    acceptance_raw = (HERE / 'acceptance-inputs-v1.json').read_bytes()
    acceptance = load(acceptance_raw)
    require(acceptance['candidate_manifest_sha256'] == MANIFEST_PIN and
            acceptance['source_sha256'] == SOURCE_PIN, 'acceptance candidate pins')
    require((acceptance['support'], acceptance['N'], acceptance['K'], acceptance['M']) ==
            ('81/100', 826, 86, 1652), 'acceptance full tuple')
    candidate = confined(ROOT, acceptance['candidate_bundle'])
    manifest_raw = (candidate / 'manifest.json').read_bytes()
    require(digest(manifest_raw) == MANIFEST_PIN, 'candidate manifest SHA')
    manifest = load(manifest_raw)
    require(len(manifest['members']) == 33, '33 sealed members required')
    members, checked = {}, []
    for entry in manifest['members']:
        name = entry['path']
        require(name not in members, 'duplicate manifest member')
        raw = confined(candidate, name).read_bytes()
        require(type(entry['size']) is int and len(raw) == entry['size'] and
                digest(raw) == entry['sha256'], 'sealed member mismatch: ' + name)
        members[name] = raw
        checked.append({'path': name, 'bytes': len(raw), 'sha256': digest(raw)})
    for name, sha in (('verify-whole-source-v1.py', NATIVE_PIN),
                      ('verify-whole-sign-v1.py', EXACT_PIN),
                      ('whole-inputs-v1.json', INPUTS_PIN)):
        require(digest(members[name]) == sha, 'consumer/input pin: ' + name)
    captured = load(members['captured-source-v1.json'])
    require(captured['source_sha256'] == SOURCE_PIN and len(captured['members']) == 9,
            'nine captured project source pins required')
    external, seen = [], set()
    for entry in captured['members']:
        name, captured_name = entry['project_path'], entry['captured_path']
        require(name not in seen, 'duplicate captured project path')
        seen.add(name)
        raw = confined(ROOT, name).read_bytes()
        require(len(raw) == entry['size'] and digest(raw) == entry['sha256'] and
                members[captured_name] == raw, 'external/captured project pin: ' + name)
        external.append({'path': name, 'captured_path': captured_name,
                         'bytes': len(raw), 'sha256': digest(raw)})
    source_raw = members['data/source-v1.json']
    require(digest(source_raw) == SOURCE_PIN, 'candidate source SHA')
    source = load(source_raw)
    require((source['support'], source['N'], source['order'], source['physical_extent'],
             source['bits'], source['precision']) == ('81/100', 826, 86, 1652, BITS, 4608),
            'source frozen tuple')
    require(source['inputs_sha256'] == INPUTS_PIN, 'source inputs binding')
    require(set(source['matrices']) == {kind + '-' + str(p) for kind in KINDS for p in (0, 1)},
            'six matrix families required')
    matrices = {}
    for key, descriptor in source['matrices'].items():
        require(set(descriptor) == {'path', 'sha256', 'size'}, 'matrix descriptor schema')
        path = confined(candidate / 'data', descriptor['path'])
        raw = members[path.relative_to(candidate).as_posix()]
        require(len(raw) == descriptor['size'] and digest(raw) == descriptor['sha256'],
                'matrix binding: ' + key)
        payload = load(gzip.decompress(raw))
        kind, parity = key.rsplit('-', 1)
        validate_payload(payload, kind, int(parity))
        matrices[key] = (raw, payload)
    proposal_raw = members['data/proposal-v1.json.gz']
    proposal = load(gzip.decompress(proposal_raw))
    require(proposal['source_sha256'] == SOURCE_PIN and proposal['inputs_sha256'] == INPUTS_PIN,
            'original gzip proposal binding')
    require(set(proposal['blocks']) == {'even', 'odd'}, 'two proposal parity blocks')
    for block in proposal['blocks'].values():
        transform = block['proposal_transform']
        require(len(transform) == DIM and all(len(row) == DIM for row in transform),
                'full 413 by 413 proposal shape')
    receipt = {'format': 't081-negative-control-capture-v1', 'status': 'PASS_PIN_CAPTURE',
               'candidate_manifest_sha256': MANIFEST_PIN, 'candidate_source_sha256': SOURCE_PIN,
               'acceptance_inputs_sha256': digest(acceptance_raw),
               'candidate_bundle': acceptance['candidate_bundle'], 'candidate_members': checked,
               'external_project_source_pins': external, 'checked_candidate_members': 33,
               'checked_external_project_source_pins': 9,
               'original_compressed_proposal_sha256': digest(proposal_raw),
               'producer_imported': False, 'production_admission': False}
    return candidate, source, matrices, proposal_raw, receipt


def validate_payload(payload, kind, parity):
    require(set(payload) == {'kind', 'parity', 'dimension', 'bits', 'upper_triangle'},
            'matrix payload schema')
    require((payload['kind'], payload['parity'], payload['dimension'], payload['bits']) ==
            (kind, parity, DIM, BITS), 'matrix identity')
    triangle = payload['upper_triangle']
    require(type(triangle) is list and len(triangle) == DIM * (DIM + 1) // 2,
            'matrix triangle size')
    require(all(type(pair) is list and len(pair) == 2 and
                all(type(x) is int and x.bit_length() <= 16384 for x in pair) and
                pair[0] <= pair[1] for pair in triangle), 'matrix endpoint structure')


def floor_q(value):
    value = Fraction(str(value))
    return value.numerator // value.denominator


def ceil_q(value):
    return -floor_q(-Fraction(str(value)))


def prime5_changes(native, kappa):
    """Independent P_0 window formula; no producer arithmetic is evaluated."""
    arb = native.arb
    support = arb(native.fmpq(81, 100))
    tau5 = arb(5).log() / support
    delta = 2 - tau5
    c5 = arb(5).log() / arb(5).sqrt()
    other = (arb(2).log() / arb(2).sqrt() + arb(3).log() / arb(3).sqrt() +
             arb(2).log() / arb(4).sqrt())
    # On both edge windows, P5 P0 = -c5; each has length delta.
    # P5's signed low constant is -2 delta c5. Removing it adds that magnitude.
    # In P^2 the two mixed orientations and two edge windows contribute
    # 4 delta c5 (c2+c3+c4). Keep the low/head subtractions unchanged.
    require(native.endpoints(delta)[0] > 0, 'nonpositive prime-five edge window')
    low = 2 * c5 * delta
    mixed = -arb(kappa) * 4 * delta * c5 * other
    require(native.endpoints(tau5 - 1)[0] > 0, 'prime-five edge windows overlap')
    overlap_checks = []
    for m in (2, 3, 4):
        tau = arb(m).log() / support
        separated = native.endpoints(tau5 + tau - 2)
        nested = native.endpoints(tau5 - tau)
        require(separated[0] > 0 and nested[0] > 0,
                'prime-five mixed constant window formula not qualified')
        overlap_checks.append({'m': m, 'tau5_plus_tau_minus_2': [str(x) for x in separated],
                               'tau5_minus_tau': [str(x) for x in nested]})
    changes = {}
    evidence = {'tau5': [str(x) for x in native.endpoints(tau5)],
                'delta_equals_2_minus_tau5': [str(x) for x in native.endpoints(delta)],
                'c5': [str(x) for x in native.endpoints(c5)],
                'c2_plus_c3_plus_c4': [str(x) for x in native.endpoints(other)],
                'kappa': str(kappa), 'publication_bits': BITS, 'changes': {}}
    evidence['other_shift_window_inequalities'] = overlap_checks
    evidence['signed_prime5_low_P00'] = [str(x) for x in native.endpoints(-low)]
    for name, value, formula in (
            ('omitted-prime5-low-term', low, '+2*c5*(2-log(5)/T)'),
            ('omitted-prime5-mixed-square', mixed, '-kappa*4*(2-log(5)/T)*c5*(c2+c3+c4)')):
        lower, upper = native.endpoints(value)
        pair = [floor_q(lower * SCALE), ceil_q(upper * SCALE)]
        changes[name] = pair
        evidence['changes'][name] = {'formula': formula, 'cell': [0, 0],
                                      'exact_Arb_endpoint_enclosure': [str(lower), str(upper)],
                                      'outward_dyadic_shift_numerators': pair}
    return changes, evidence


def native_even_control(candidate, source, case_root):
    """Call immutable native functions at their actual frozen dimensions."""
    for name in THREADS:
        os.environ[name] = '1'
    checker = candidate / 'verify-whole-source-v1.py'
    require(digest(checker.read_bytes()) == NATIVE_PIN, 'native consumer SHA before import')
    spec = importlib.util.spec_from_file_location('t081_retained_immutable_native', checker)
    require(spec is not None and spec.loader is not None, 'native consumer import spec')
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    native.ctx.prec = 6144
    require((native.N, native.ORDER, native.EXTENT, native.DIM, native.BITS) ==
            (826, 86, 1652, DIM, BITS), 'native full tuple')
    started = time.monotonic()
    receipt = {'format': 't081-native-even-negative-probe-control-v1',
               'status': 'FAIL_ORIGINAL_NATIVE_SUBSET_CONTROL', 'consumer_sha256': NATIVE_PIN,
               'source_sha256': SOURCE_PIN, 'inputs_sha256': INPUTS_PIN,
               'scope': 'SUBSET parity 0 only, not complete source audit',
               'parity': 0, 'dimension': DIM, 'independent_precision_bits': 6144,
               'original_families_checked': [], 'checked_triangular_entries': 0,
               'successful_original_controls': False, 'numerical_threads': 1,
               'one_fresh_even_reconstruction_shared_only_by_invalid_input_probes': True,
               'full_original_source_acceptance_requires_separate_fresh_full_replay': True,
               'consumer_predicates_unchanged': True, 'producer_imported': False,
               'shared_arithmetic_premise': 'python-flint/Arb rigorous arithmetic and Gauss root/weight enclosures',
               'positivity_checked': False, 'production_admission': False}
    try:
        inputs_raw, inputs, declaration, seal = native.frozen_inputs(candidate / 'whole-inputs-v1.json')
        receipt['scalar_qualification'] = native.replay_declaration(inputs, declaration, seal)
        require(digest(inputs_raw) == INPUTS_PIN, 'native frozen inputs binding')
        kernel = native.residual_kernel()
        require(kernel == [native.rational(x) for x in declaration['kernel_coefficients']] and
                len(kernel) == native.ORDER + 1 and kernel[1] == native.SUPPORT ** 2 / 48,
                'native canonical kernel coefficients differ')
        native.validate_model_allowance(declaration, kernel)
        edges, weights, kappa = native.validate_weights(source, declaration)
        polynomials = [native.rodrigues(n) for n in range(native.EXTENT)]
        harmonic, harmonic2 = native.harmonic_tables(native.EXTENT + 2)
        outputs = native.residual_outputs(polynomials, kernel)
        frequency = native.frequency_kernels(edges, weights)
        nodes = [native.arb.legendre_p_root(native.N, j, weight=True) for j in range(native.N)]
        reconstructed = native.reconstruct(0, polynomials, outputs, harmonic, harmonic2,
                                           frequency[0], kappa, nodes)
        for kind in KINDS:
            count = native.check_matrix(source, candidate / 'data', kind, 0, reconstructed[kind])
            require(count == DIM * (DIM + 1) // 2, 'original family entry count')
            receipt['original_families_checked'].append(
                {'family': kind + '-0', 'checked_triangular_entries': count,
                 'status': 'PASS_NATIVE_SUBSET_CONTAINMENT'})
            receipt['checked_triangular_entries'] += count
        require(receipt['checked_triangular_entries'] == 256473, 'original even control incomplete')
        changes, evidence = prime5_changes(native, kappa)
        receipt.update({'status': 'PASS_ORIGINAL_NATIVE_SUBSET_CONTROL',
                        'successful_original_controls': True, 'kernel_and_model_allowance_checked': True,
                        'frequency_weights_checked': len(weights),
                        'Gauss_order': native.N, 'fresh_reconstruct_calls': 1,
                        'prime5_independent_cell_formulas': evidence})
    except Exception as error:
        receipt.update({'error_type': type(error).__name__, 'error': str(error),
                        'elapsed_seconds': time.monotonic() - started})
        fresh(case_root / 'native-even-control.json', encode(receipt))
        raise
    receipt['elapsed_seconds'] = time.monotonic() - started
    fresh(case_root / 'native-even-control.json', encode(receipt))
    return native, declaration, reconstructed, changes, receipt


def modify(payload, mode, changes):
    """Native omissions change only cell 00, a sufficient false-enclosure witness."""
    kind, parity = payload['kind'], payload['parity']
    triangle = payload['upper_triangle']
    lo, hi = triangle[0]
    if parity == 0:
        if mode == 'wrongactual-lowconstant' and kind == 'A_model':
            triangle[0] = [lo + 2 * SCALE, hi + 2 * SCALE]
        elif mode == 'underpaidweightedhead' and kind == 'weighted_head':
            triangle[0] = [lo // 2, -(-hi // 2)]
        elif mode == 'omitted-complete-physicalexterior' and kind == 'weighted_complete_tail':
            triangle[0] = [0, 0]
        elif ((mode == 'omitted-prime5-low-term' and kind == 'A_model') or
              (mode == 'omitted-prime5-mixed-square' and kind == 'weighted_complete_tail')):
            shift_lo, shift_hi = changes[mode]
            triangle[0] = [lo + shift_lo, hi + shift_hi]
    if mode == 'synthetic-selected-negative' and kind == 'A_model':
        replacement = []
        for i in range(DIM):
            for j in range(i, DIM):
                value = -Fraction(2 * SCALE, 2 * (2 * i + parity) + 1) if i == j else Fraction(0)
                replacement.append([floor_q(value) - 1, ceil_q(value) + 1])
        payload['upper_triangle'] = replacement
    elif mode == 'numerical-width-uncertainty' and kind == 'A_model':
        triangle[0] = [lo - SCALE, hi + SCALE]


def packet(directory, source, matrices, mode, changes):
    result = copy.deepcopy(source)
    (directory / 'matrices').mkdir()
    mutations = []
    for key, (original_raw, original) in matrices.items():
        payload = copy.deepcopy(original)
        modify(payload, mode, changes)
        validate_payload(payload, original['kind'], original['parity'])
        changed = payload != original
        raw = gzip.compress(encode(payload), compresslevel=9, mtime=0) if changed else original_raw
        relative = 'matrices/' + key + '.json.gz'
        fresh(confined(directory, relative), raw)
        result['matrices'][key] = {'path': relative, 'sha256': digest(raw), 'size': len(raw)}
        if changed:
            mutations.append({'family': key, 'original_sha256': digest(original_raw),
                              'modified_sha256': digest(raw),
                              'original_cell_00': original['upper_triangle'][0],
                              'modified_cell_00': payload['upper_triangle'][0]})
    if mode == 'underpaid-terminal-inverseweight':
        result['inverse_weight_uppers'][-1] = '0'
    raw = encode(result)
    fresh(directory / 'source.json', raw)
    return result, digest(raw), mutations


def native_probe(native, declaration, reconstructed, source, source_sha, directory, kind, expected):
    started = time.monotonic()
    record = {'consumer_sha256': NATIVE_PIN, 'source_sha256': source_sha,
              'scope': 'SUBSET parity 0; shared fresh independent even reconstruction',
              'shared_control': '../native-even-control.json',
              'predicate': 'validate_weights' if kind is None else 'check_matrix',
              'family': None if kind is None else kind + '-0',
              'expected': expected, 'status': 'SOURCE_PROBE_DID_NOT_REJECT',
              'complete_source_audit': False, 'production_admission': False}
    passed = False
    try:
        # Re-read retained packet, rather than bypassing its serialized source.
        retained_raw = (directory / 'source.json').read_bytes()
        require(digest(retained_raw) == source_sha, 'retained probe source binding')
        retained = native.load(retained_raw)
        require(retained == source, 'retained probe packet differs')
        if kind is None:
            native.validate_weights(retained, declaration)
        else:
            native.check_matrix(retained, directory, kind, 0, reconstructed[kind])
    except Exception as error:
        record.update({'status': 'REJECT_NATIVE_SUBSET_SOURCE_PROBE',
                       'error_type': type(error).__name__, 'error': str(error)})
        passed = isinstance(error, ValueError) and str(error).startswith(expected)
    record.update({'passed': passed, 'elapsed_seconds': time.monotonic() - started})
    fresh(directory / 'receipt.json', encode(record))
    return passed


def run(command, receipt):
    environment = dict(os.environ)
    environment.update({name: '1' for name in THREADS})
    started = time.monotonic()
    process = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True)
    record = {'argv': command, 'cwd': str(ROOT), 'numerical_threads': 1,
              'exit_code': process.returncode, 'elapsed_seconds': time.monotonic() - started,
              'stdout': process.stdout.decode('utf-8', errors='replace'),
              'stderr': process.stderr.decode('utf-8', errors='replace')}
    fresh(receipt, encode(record))
    return record


def exact_probe(candidate, proposal_raw, source_sha, directory, name, expected):
    proposal = load(gzip.decompress(proposal_raw))
    proposal['source_sha256'] = source_sha
    if name == 'singular-fullspace-witness':
        for row in proposal['blocks']['even']['proposal_transform']:
            row[0] = '0'
    raw = gzip.compress(encode(proposal), compresslevel=9, mtime=0)
    fresh(directory / 'proposal.json.gz', raw)
    checker = candidate / 'verify-whole-sign-v1.py'
    require(digest(checker.read_bytes()) == EXACT_PIN, 'exact consumer SHA before subprocess')
    audit = directory / 'audit.json'
    command = [sys.executable, '-I', '-B', str(checker),
               '--inputs', str(candidate / 'whole-inputs-v1.json'),
               '--source', str(directory / 'source.json'),
               '--proposal', str(directory / 'proposal.json.gz'), '--output', str(audit)]
    record = run(command, directory / 'receipt.json')
    assessment = load(audit.read_bytes()) if audit.exists() else None
    if name == 'singular-fullspace-witness':
        passed = (record['exit_code'] == 1 and assessment is None and
                  'ValueError: ' + expected in record['stderr'])
    else:
        passed = (record['exit_code'] == 0 and assessment is not None and
                  assessment.get('status') == expected and
                  assessment.get('source_sha256') == source_sha and
                  assessment.get('proposal_sha256') == digest(raw) and
                  assessment.get('inputs_sha256') == INPUTS_PIN and
                  assessment.get('verifier_sha256') == EXACT_PIN and
                  assessment.get('production_admission') is False and
                  assessment.get('analytic_source_acceptance_is_separate') is True and
                  set(assessment.get('blocks', {})) == {'even', 'odd'})
        if passed:
            blocks = assessment['blocks'].values()
            passed = all(block['dimension'] == DIM and block['exact_nonsingularity'] is True
                         for block in blocks)
            if name == 'synthetic-selected-negative':
                passed = passed and all(
                    block['selected_lower_negative_direction_proved'] is True and
                    Fraction(block['minimum_directional_upper_of_selected_lower_NOT_actual_criterion']) < 0 and
                    block['numerical_width_goal_passed'] is True and
                    block['positive_complete_paid_lower'] is False
                    for block in assessment['blocks'].values())
            else:
                passed = passed and all(block['numerical_width_goal_passed'] is False
                                        for block in assessment['blocks'].values())
    return bool(passed), digest(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.is_symlink(), 'fresh nonsymlink output required')
    output = args.output.resolve()
    require(output.suffix == '.json' and output.is_relative_to((HERE / 'data').resolve()),
            'output must be JSON under acceptance data/')
    require(not output.exists(), 'fresh output required')
    case_root = output.parent / (output.stem + '-cases')
    require(not case_root.exists() and not case_root.is_symlink(), 'fresh per-output case directory required')
    candidate, source, matrices, proposal_raw, capture_receipt = capture()
    output.parent.mkdir(parents=True, exist_ok=True)
    case_root.mkdir()
    fresh(case_root / 'capture-receipt.json', encode(capture_receipt))
    native, declaration, reconstructed, changes, native_receipt = native_even_control(
        candidate, source, case_root)
    results = []
    for name, consumer, kind, expected in CASES:
        directory = case_root / name
        directory.mkdir()
        bad_source, source_sha, mutations = packet(directory, source, matrices, name, changes)
        if consumer == 'source':
            passed = native_probe(native, declaration, reconstructed, bad_source, source_sha,
                                  directory, kind, expected)
            proposal_sha = None
        else:
            passed, proposal_sha = exact_probe(candidate, proposal_raw, source_sha,
                                                directory, name, expected)
        result = {'case': name, 'consumer': consumer, 'expected': expected,
                  'expected_exit_code': (1 if name == 'singular-fullspace-witness' else
                                         0 if consumer == 'exact' else None),
                  'passed': bool(passed), 'source_sha256': source_sha,
                  'consumer_sha256': NATIVE_PIN if consumer == 'source' else EXACT_PIN,
                  'proposal_sha256': proposal_sha, 'original_proposal_sha256': digest(proposal_raw),
                  'mathematical_matrix_mutations': mutations,
                  'synthetic_not_analytic_truth': name == 'synthetic-selected-negative',
                  'production_admission': False,
                  'actual_Weil_negativity_claimed': False}
        if consumer == 'source':
            result.update({'scope': 'SUBSET parity 0; not a complete source audit',
                           'shared_native_control_receipt': 'native-even-control.json',
                           'changed_matrix_cells': [[0, 0]] if kind else [],
                           'terminal_inverse_weight_set_to_zero': kind is None})
        fresh(directory / 'case-result.json', encode(result))
        result['files'] = [file_record(path, case_root) for path in sorted(directory.rglob('*'))
                           if path.is_file()]
        results.append(result)
    summary = {'format': 't081-retained-negative-controls-v1',
               'status': 'PASS_NEGATIVE_CONTROLS' if len(results) == 9 and
               all(item['passed'] for item in results) else 'FAIL_NEGATIVE_CONTROLS',
               'candidate_manifest_sha256': MANIFEST_PIN, 'candidate_source_sha256': SOURCE_PIN,
               'case_directory': case_root.relative_to(HERE).as_posix(), 'cases': results,
               'files': [file_record(case_root / name, case_root) for name in
                         ('capture-receipt.json', 'native-even-control.json')],
               'native_batch_proof': native_receipt,
               'positive_candidate_must_pass_independently': True,
               'full_original_source_acceptance_requires_separate_fresh_full_replay': True,
               'native_scope': 'SUBSET parity 0 only, 256473 original matrix entries; six false-input probes',
               'underpaid_head_scope': 'Outward-rounded halving of cell 00; not isolation of the terminal frequency payment.',
               'physical_exterior_omission_scope': 'Cell 00 zeroed as a local witness to dropping the complete physical exterior.',
               'prime5_mixed_scope': 'Remove only P5 cross terms with 2/3/4 in the full P-squared cell 00; low/head subtractions unchanged.',
               'synthetic_negative_scope': 'Artificial A_model=-D in both full 413-dimensional parity blocks; finite selected paid-lower negativity only, NOT analytic source truth or actual Weil negativity.',
               'shared_arithmetic_premise': native_receipt['shared_arithmetic_premise'],
               'production_admission': False, 'actual_Weil_negativity_claimed': False}
    fresh(output, encode(summary))
    print(summary['status'], flush=True)
    return 0 if summary['status'] == 'PASS_NEGATIVE_CONTROLS' else 1


if __name__ == '__main__':
    sys.exit(main())
