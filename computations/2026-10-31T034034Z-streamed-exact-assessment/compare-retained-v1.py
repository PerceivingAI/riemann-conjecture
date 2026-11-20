"""Read-only comparison of retained and streamed reference arithmetic results."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source.contract import canonical_bytes

REFERENCE = ROOT / 'computations/2026-10-27T140745Z-t081-complete-gram-attempt/data'
SOURCE_SHA = 'f69fee0feb9c08833ad6a3091718c9a6a301e5b5ddbea96ee5f0f6c0553c8b6e'
PROPOSAL_SHA = '3444b4cd498e16b46d9c10b539285cd5038489976a88b3111bd47364d247c85e'
REPORT_SHA = 'b8a439634131a51cbbe029fd0e438eceb2851fe1a8e8d40cac5082009f36046d'
SCOPE = 'REFERENCE_ARITHMETIC_ONLY'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def document(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def pinned(path, digest, size=None):
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == digest, 'artifact hash mismatch: ' + str(path))
    require(size is None or len(raw) == size, 'artifact size mismatch: ' + str(path))
    return raw


def rational(value):
    require(type(value) is dict and set(value) == {'numerator', 'denominator'},
            'new result requires a canonical rational object')
    require(all(type(text) is str for text in value.values()), 'hex rational strings required')
    numerator, denominator = int(value['numerator'], 16), int(value['denominator'], 16)
    require(denominator > 0, 'positive denominator required')
    result = Fraction(numerator, denominator)
    require(value == {'numerator': hex(result.numerator), 'denominator': hex(result.denominator)},
            'noncanonical new rational')
    return result


def old_rational(text):
    require(type(text) is str, 'old canonical rational string required')
    result = Fraction(text)
    require(str(result) == text, 'noncanonical old rational')
    return result


def inside(root, relative):
    require(type(relative) is str, 'relative artifact path required')
    path = (root / relative).resolve()
    require(path.is_relative_to(root) and path != root, 'artifact path escapes run directory')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run = args.run_dir.resolve()
    require(not args.output.exists(), 'comparison output must be fresh')
    pinned(REFERENCE / 'source-v1.json', SOURCE_SHA)
    pinned(REFERENCE / 'proposal-v1.json.gz', PROPOSAL_SHA)
    old = json.loads(pinned(REFERENCE / 'exact-sign-v1.json', REPORT_SHA), object_pairs_hook=unique)
    require(old['source_sha256'] == SOURCE_SHA and old['proposal_sha256'] == PROPOSAL_SHA and
            old['status'] == 'PASS_COMPLETE_SOURCE_CONDITIONAL_CANDIDATE' and
            old['production_admission'] is False, 'changed retained report context')
    preparation = document(run / 'prepare-result.json')
    require(preparation['format'] == 'retained-exact-preparation-v1' and
            preparation['proof_scope'] == SCOPE and preparation['endpoint_pairs'] == 512946 and
            preparation['Z_entries'] == 341138, 'incomplete reference transcription')
    origin_ref = preparation['origin']
    require(origin_ref['kind'] == 'REFERENCE_TRANSCRIPTION' and
            Path(origin_ref['directory']).resolve() == run and
            origin_ref['artifact']['path'] == 'reference-origin.json', 'changed reference origin')
    origin_artifact = origin_ref['artifact']
    origin = json.loads(pinned(run / 'reference-origin.json', origin_artifact['sha256'],
                               origin_artifact['size']), object_pairs_hook=unique)
    require(origin['format'] == 'retained-exact-reference-origin-v1' and origin['proof_scope'] == SCOPE and
            origin['source']['sha256'] == SOURCE_SHA and origin['proposal']['sha256'] == PROPOSAL_SHA and
            origin['endpoint_pairs'] == 512946 and origin['Z_entries'] == 341138 and
            origin['fresh_source_construction'] is False and
            origin['fresh_proposal_construction'] is False and
            origin['analytical_source_acceptance'] is False and origin['production_admission'] is False,
            'invalid reference arithmetic scope')
    for key, filename in (('source', 'source-v1.json'), ('proposal', 'proposal-v1.json.gz')):
        ref = origin[key]
        require(ref['path'] == (REFERENCE / filename).relative_to(ROOT).as_posix(),
                'changed reference origin path')
        pinned(REFERENCE / filename, ref['sha256'], ref['size'])
    inputs = preparation['inputs']
    operands = document(inside(run, inputs['operands']))
    require(operands['origin'] == origin_ref and operands['proof_scope'] == SCOPE,
            'exact operands do not bind reference origin and scope')
    problem = document(inside(run, inputs['problem']))
    parameters = problem['parameters']
    require(parameters['profile'] == 'retained-t081' and parameters['N'] == 826 and
            parameters['M'] == 1652 and parameters['K'] == 86, 'changed frozen problem geometry')
    report_path = run / 'exact/report.json'
    new = document(report_path)
    require(new['proof_scope'] == SCOPE and type(new['blocks']) is list and len(new['blocks']) == 2,
            'reference comparison requires both scoped new parity reports')
    require(new.get('production_admission') is False, 'reference report must not admit production')
    comparisons = []
    sigmas = []
    widths = []
    goals = []
    margins = []
    for parity, label in enumerate(('even', 'odd')):
        before, after = old['blocks'][label], new['blocks'][parity]
        require(before['dimension'] == after['dimension'] == 413 and after['parity'] == parity and
                after['scope'] == SCOPE and after['analytical_source_acceptance'] is False and
                after['production_admission'] is False, 'changed parity proof scope')
        require(len(before['row_margins']) == len(after['row_margins']) == 413,
                'incomplete row margin comparison')
        rows = [old_rational(value) for value in before['row_margins']]
        for index, (expected, actual) in enumerate(zip(rows, after['row_margins'])):
            require(expected == rational(actual), f'{label} row {index} margin differs')
        scalar_fields = {
            'width': 'numerical_radius_physical_upper',
            'goal': 'numerical_radius_physical_goal',
            'margin': 'minimum_complete_congruence_margin',
            'direction_upper': 'minimum_directional_upper_of_selected_lower_NOT_actual_criterion',
            'direction_mass': 'direction_mass',
        }
        values = {}
        for field, original in scalar_fields.items():
            values[field] = rational(after[field])
            require(values[field] == old_rational(before[original]), f'{label} {field} differs')
        require(values['margin'] == min(rows) and values['margin'] > 0,
                'changed complete positive minimum margin')
        require(type(after['direction_index']) is int and
                after['direction_index'] == before['direction_index'], 'direction index differs')
        require(values['direction_mass'] > 0 and
                values['direction_upper'] / values['direction_mass'] ==
                old_rational(before['selected_lower_direction_physical_upper']),
                'physical selected direction consequence differs')
        require(before['selected_lower_negative_direction_proved'] is
                (values['direction_upper'] < 0), 'selected direction sign consequence differs')
        sigma = old_rational(before['complete_physical_lower_if_positive'])
        tau = rational(after['tau'])
        require(tau > 0 and tau == values['margin'] / sigma and
                values['margin'] / tau == sigma, 'trace or physical lower consequence differs')
        modular = after['modular']
        require(before['exact_nonsingularity'] is True and modular['prime'] == 65521 and
                type(modular['residue']) is int and 0 < modular['residue'] < 65521 and
                modular['nonsingular'] is True, 'complete modular nonsingularity not proved')
        require(before['numerical_width_goal_passed'] is True and
                values['width'] <= values['goal'] and before['positive_complete_paid_lower'] is True,
                'changed width or paid-lower consequence')
        sigmas.append(sigma)
        widths.append(values['width'])
        goals.append(values['goal'])
        margins.append(values['margin'])
        comparisons.append({'parity': parity, 'row_margins_compared': 413,
            'scalar_equalities_compared': len(scalar_fields) + 4,
            'complete_modular_nonsingularity': True, 'all_equal': True})
    sigma = min(sigmas)
    eta, m, b_K, delta = (rational(parameters[key]) for key in ('eta', 'm', 'b_K', 'delta'))
    gamma = min(sigma / (1 + 2*(b_K+delta)**2/(eta**2*m**2)), eta*m/2)
    assessment = new['assessment']
    require(rational(assessment['sigma']) == sigma and rational(assessment['gamma']) == gamma,
            'global sigma or full gamma differs')
    require(all(width <= goal for width, goal in zip(widths, goals)) and min(margins) > 0 and
            assessment['width_passed'] is True and assessment['global_nonsingularity'] is True and
            assessment['positive_paid_lower'] is True and assessment['source_conditional'] is True and
            assessment['proof_scope'] == SCOPE and
            assessment['smooth_test_consequence_conditional'] is False and
            assessment['status'] == new['status'] == 'PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL',
            'changed global arithmetic consequence or reference scope')
    output = {'format': 'retained-exact-comparison-v1', 'status': 'PASS_EXACT_REFERENCE_COMPARISON',
        'proof_scope': SCOPE, 'source_sha256': SOURCE_SHA, 'proposal_sha256': PROPOSAL_SHA,
        'reference_report_sha256': REPORT_SHA,
        'new_report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(),
        'reference_origin': origin_artifact, 'endpoint_pairs_transcribed': 512946,
        'Z_entries_transcribed': 341138, 'blocks': comparisons,
        'row_margins_compared': 826, 'global_sigma_equal': True, 'full_gamma_equal': True,
        'fresh_supported_source_qualified': False, 'fresh_proposal_qualified': False,
        'analytical_source_acceptance': False, 'positivity_release': False, 'production_admission': False}
    with args.output.open('xb') as stream:
        stream.write(canonical_bytes(output))
    print(json.dumps(output, sort_keys=True))


if __name__ == '__main__':
    main()
