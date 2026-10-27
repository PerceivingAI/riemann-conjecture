"""Retained false-input gates; no source generation, admission, or Weil-negativity claim.

All case files are fresh and retained. The finite-negative packet is deliberately
synthetic, not an analytically qualified source. The original positive packet
must independently pass both unchanged consumers in the separate retained replay.
"""
import argparse
import copy
from fractions import Fraction
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_PIN = 'f50d8a194bf4d13ad4cd65ccbcf5762c403d8f5e26d384cbdb38be5ccb807fe6'
SCALE = 1 << 256
DIM = 161
THREADS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS',
           'FLINT_NUM_THREADS')


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
    require(type(relative) is str and not Path(relative).is_absolute(), 'relative path required')
    path = (base / relative).resolve()
    require(path.is_relative_to(base.resolve()), 'path escapes bound directory')
    return path


def capture():
    """Capture each sealed member once, checking all hashes before any case writes."""
    acceptance = load((HERE / 'acceptance-inputs-v1.json').read_bytes())
    candidate = confined(ROOT, acceptance['candidate_bundle'])
    manifest_raw = (candidate / 'manifest.json').read_bytes()
    require(digest(manifest_raw) == acceptance['candidate_manifest_sha256'], 'candidate manifest SHA')
    manifest = load(manifest_raw)
    members = {}
    for entry in manifest['members']:
        name = entry['path']
        require(name not in members, 'duplicate manifest member')
        raw = confined(candidate, name).read_bytes()
        require(len(raw) == entry['bytes'] and digest(raw) == entry['sha256'], 'sealed member mismatch: ' + name)
        members[name] = raw
    for name, sha in manifest['external_immutable_or_captured_project_input_sha256'].items():
        raw = confined(ROOT, name).read_bytes()
        require(digest(raw) == sha, 'external input SHA: ' + name)
    source_raw = members['data/whole-source-v2.json']
    require(digest(source_raw) == SOURCE_PIN == acceptance['source_sha256'], 'candidate source SHA')
    source = load(source_raw)
    matrices = {}
    for key, descriptor in source['matrices'].items():
        original = confined(candidate / 'data', descriptor['path'])
        name = original.relative_to(candidate).as_posix()
        raw = members[name]
        require(digest(raw) == descriptor['sha256'] and len(raw) == descriptor['size'], 'matrix binding: ' + key)
        payload = load(gzip.decompress(raw))
        require(payload['dimension'] == DIM and payload['bits'] == 256, 'matrix dimensions')
        require(len(payload['upper_triangle']) == DIM * (DIM + 1) // 2, 'matrix triangle')
        require(all(type(pair) is list and len(pair) == 2 and
                    all(type(x) is int for x in pair) and pair[0] <= pair[1]
                    for pair in payload['upper_triangle']), 'matrix endpoint structure')
        matrices[key] = (raw, payload)
    require(len(matrices) == 6, 'six matrices required')
    proposal_raw = members['data/whole-proposal-v2.json']
    require(load(proposal_raw)['source_sha256'] == SOURCE_PIN, 'original proposal binding')
    return candidate, source, matrices, proposal_raw, digest(manifest_raw)


def modify(payload, mode):
    kind, parity = payload['kind'], payload['parity']
    if mode == 'wrongactual-lowconstant' and kind == 'A_model':
        offset = 0
        for i in range(DIM):
            mass = Fraction(2 * SCALE, 2 * (2 * i + parity) + 1)
            lo, hi = payload['upper_triangle'][offset]
            payload['upper_triangle'][offset] = [lo + mass.numerator // mass.denominator,
                                                 hi - (-mass.numerator // mass.denominator)]
            offset += DIM - i
    elif mode == 'underpaidweightedhead' and kind == 'weighted_head':
        payload['upper_triangle'] = [[lo // 2, -(-hi // 2)] for lo, hi in payload['upper_triangle']]
    elif mode == 'omitted-complete-physicalexterior' and kind == 'weighted_complete_tail':
        payload['upper_triangle'] = [[0, 0] for _ in payload['upper_triangle']]
    elif mode == 'synthetic-selected-negative' and kind == 'A_model':
        triangle = []
        for i in range(DIM):
            for j in range(i, DIM):
                value = -Fraction(2 * SCALE, 2 * (2 * i + parity) + 1) if i == j else Fraction(0)
                triangle.append([value.numerator // value.denominator - 1,
                                 -(-value.numerator // value.denominator) + 1])
        payload['upper_triangle'] = triangle
    elif mode == 'numerical-width-uncertainty' and kind == 'A_model':
        payload['upper_triangle'][0][0] -= SCALE
        payload['upper_triangle'][0][1] += SCALE


def packet(directory, source, matrices, mode):
    result = copy.deepcopy(source)
    (directory / 'matrices').mkdir()
    for key, (raw, original) in matrices.items():
        payload = copy.deepcopy(original)
        modify(payload, mode)
        if payload != original:
            raw = gzip.compress(encode(payload), compresslevel=9, mtime=0)
        relative = 'matrices/' + key + '.json.gz'
        fresh(confined(directory, relative), raw)
        result['matrices'][key] = {'path': relative, 'sha256': digest(raw), 'size': len(raw)}
    if mode == 'underpaid-terminal-inverseweight':
        result['inverse_weight_uppers'][-1] = '0'
    raw = encode(result)
    fresh(directory / 'source.json', raw)
    return digest(raw)


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    data = HERE / 'data'
    require(output.suffix == '.json' and output.is_relative_to(data.resolve()), 'output must be JSON under acceptance data/')
    require(not output.exists() and not output.is_symlink(), 'fresh output required')
    case_root = output.parent / (output.stem + '-cases')
    require(not case_root.exists() and not case_root.is_symlink(), 'fresh per-output case directory required')
    candidate, source, matrices, proposal_raw, manifest_sha = capture()
    output.parent.mkdir(parents=True, exist_ok=True)
    case_root.mkdir()
    cases = [
        ('wrongactual-lowconstant', 'source', 'source enclosure fails at A_model-0'),
        ('underpaidweightedhead', 'source', 'source enclosure fails at weighted_head-0'),
        ('omitted-complete-physicalexterior', 'source', 'source enclosure fails at weighted_complete_tail-0'),
        ('underpaid-terminal-inverseweight', 'source', 'inverse weights differ from declaration'),
        ('singular-fullspace-witness', 'exact', 'singular full congruence'),
        ('synthetic-selected-negative', 'exact', 'SELECTED_CONSERVATIVE_SCHUR_NEGATIVE_NOT_WEIL_NEGATIVITY'),
        ('numerical-width-uncertainty', 'exact', 'NUMERICAL_WIDTH_GOAL_FAILED'),
    ]
    results = []
    for name, consumer, expected in cases:
        directory = case_root / name
        directory.mkdir()
        source_sha = packet(directory, source, matrices, name)
        audit = directory / 'audit.json'
        command = [sys.executable, '-I', '-B', str(candidate / (
            'verify-whole-source-v2.py' if consumer == 'source' else 'verify-whole-sign-v1.py')),
            '--inputs', str(candidate / 'whole-inputs-v1.json'),
            '--source', str(directory / 'source.json'), '--output', str(audit)]
        proof_exception = None
        if consumer == 'exact':
            proposal = load(proposal_raw)
            proposal['source_sha256'] = source_sha
            if name == 'singular-fullspace-witness':
                for row in proposal['blocks']['even']['proposal_transform']:
                    row[0] = '0'
            raw = encode(proposal)
            fresh(directory / 'proposal.json', raw)
            command.extend(['--proposal', str(directory / 'proposal.json')])
            if len(raw) > 2_000_000:
                proof_exception = {'path': 'proposal.json', 'bytes': len(raw), 'sha256': digest(raw),
                                   'reason': 'Necessary exact full rational witness consumed by unchanged zero-float checker; required proof-artifact exception.'}
        else:
            # Analytic source audits do not consume a proposal. The original exact
            # proposal remains immutable and is not copied into these cases.
            proof_exception = None
        record = run(command, directory / 'receipt.json')
        assessment = load(audit.read_bytes()) if audit.exists() else None
        if consumer == 'source':
            passed = (record['exit_code'] == 1 and assessment is not None and
                      assessment.get('status') == 'REJECT_COMPLETE_SOURCE' and
                      expected in assessment.get('error', ''))
        elif name == 'singular-fullspace-witness':
            passed = record['exit_code'] == 1 and assessment is None and expected in record['stderr']
        else:
            passed = record['exit_code'] == 0 and assessment is not None and assessment.get('status') == expected
            if name == 'synthetic-selected-negative' and assessment is not None:
                passed = passed and all(block['selected_lower_negative_direction_proved'] is True and
                                        Fraction(block['minimum_directional_upper_of_selected_lower_NOT_actual_criterion']) < 0 and
                                        block['numerical_width_goal_passed'] is True and
                                        block['positive_complete_paid_lower'] is False
                                        for block in assessment['blocks'].values())
            elif assessment is not None:
                passed = passed and all(block['numerical_width_goal_passed'] is False
                                        for block in assessment['blocks'].values())
        result = {'case': name, 'consumer': consumer, 'expected': expected,
                  'expected_exit_code': 1 if consumer == 'source' or name == 'singular-fullspace-witness' else 0,
                  'passed': bool(passed), 'source_sha256': source_sha,
                  'original_proposal_sha256': digest(proposal_raw),
                  'synthetic_not_analytic_truth': name == 'synthetic-selected-negative',
                  'large_required_proof_input': proof_exception}
        fresh(directory / 'case-result.json', encode(result))
        result['files'] = [{'path': path.relative_to(case_root).as_posix(),
                            'bytes': path.stat().st_size, 'sha256': digest(path.read_bytes())}
                           for path in sorted(directory.rglob('*')) if path.is_file()]
        results.append(result)
    summary = {'format': 't080-retained-negative-controls-v1',
               'status': 'PASS_NEGATIVE_CONTROLS' if all(item['passed'] for item in results) else 'FAIL_NEGATIVE_CONTROLS',
               'candidate_manifest_sha256': manifest_sha, 'candidate_source_sha256': SOURCE_PIN,
               'production_admission': False, 'actual_Weil_negativity_claimed': False,
               'positive_candidate_must_pass_independently': True,
               'synthetic_negative_scope': 'Artificial A_model=-D with narrow dyadic intervals; only finite selected paid-lower negativity, not analytic source truth or actual Weil negativity.',
               'underpaid_head_scope': 'Outward-rounded halving of weighted_head, not a claim to isolate the terminal frequency payment.',
               'case_directory': case_root.relative_to(HERE).as_posix(), 'cases': results}
    fresh(output, encode(summary))
    print(summary['status'], flush=True)
    return 0 if summary['status'] == 'PASS_NEGATIVE_CONTROLS' else 1


if __name__ == '__main__':
    sys.exit(main())
