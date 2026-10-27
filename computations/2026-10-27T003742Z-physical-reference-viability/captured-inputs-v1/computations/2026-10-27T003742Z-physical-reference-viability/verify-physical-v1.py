"""Independent fixed-control physical dual audit, with exact power-polynomial algebra.

No project module is imported.  Rodrigues polynomials, potential moments,
zero-at-zero repeated antiderivatives and explicit boundary terms replace the
producer's Legendre matrix algebra.  Arithmetic overlaps use both translations
on the original nonsymmetric interval.  FLINT rational and Arb arithmetic are
shared numerical infrastructure, not an independent implementation of FLINT.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path

from flint import arb, arb_poly, ctx, fmpq, fmpq_poly


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BITS = 4096
N = 312
K = 56
T = fmpq(3, 4)
GRID = 1 << 96
PUBLIC_GRID = 1 << 192
CRITICAL_PIN = '6e18940d7e34eaa29acd6d3457f75c036729b1a4de652ac0b37802b8c0486340'
RESIDUAL_PIN = 'afa2a31af3f25fbe1e75aa36633c2be70433fea0479e0d4bea90cd1899f2d01b'
INPUTS_PIN = '7703ba08736a4b5605630e5a1d9e9d6f90ff31399521310df5e1ee19d6d10458'
EXACT_KEYS = {
    'low_mass', 'tail_mass', 'jump_low', 'jump_tail',
    'residual_model_low', 'residual_model_tail',
    'potential_low_rational', 'potential_tail_rational',
    'potential_cross', 'residual_model_cross',
}
INTERVAL_KEYS = {
    'cT', 'A0', 'potential_low', 'potential_tail', 'arithmetic_low',
    'arithmetic_cross', 'finite_low_model', 'actual_low', 'arch_tail',
    'model_cross', 'actual_cross',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_object(items):
    out = {}
    for key, value in items:
        require(key not in out, 'duplicate JSON key: ' + key)
        out[key] = value
    return out


def invalid_constant(value):
    raise ValueError('nonfinite JSON constant: ' + value)


def load(raw):
    return json.loads(raw, object_pairs_hook=unique_object,
                      parse_constant=invalid_constant)


def rational(value):
    require(isinstance(value, str), 'published rational must be a string')
    return fmpq(value)


def ends(value):
    require(value.is_finite(), 'nonfinite native Arb value')
    return value.lower().fmpq(), value.upper().fmpq()


def interval(pair):
    require(isinstance(pair, dict) and set(pair) == {'lower', 'upper'},
            'interval endpoint schema')
    low, high = rational(pair['lower']), rational(pair['upper'])
    require(low < high, 'empty or reversed published interval')
    require((low * PUBLIC_GRID).denominator == 1 and
            (high * PUBLIC_GRID).denominator == 1,
            'published interval is not on the 192-bit grid')
    return low, high


def contains(name, pair, value):
    contains_range(name, pair, value, value)


def contains_range(name, pair, native_low, native_high):
    low, high = interval(pair)
    lower = ends(native_low)[0]
    upper = ends(native_high)[1]
    require(lower <= upper and low < lower and upper < high,
            name + ': native bounds are not strictly inside publication')


def bounded_above(name, bound, value):
    require(bound >= ends(value)[1], name + ': false upper bound')


def root_file(relative):
    require(isinstance(relative, str), 'root-relative path must be a string')
    path = (ROOT / relative).resolve()
    require(not Path(relative).is_absolute() and path.is_relative_to(ROOT),
            'path outside project root')
    require(path.is_file(), 'missing bound source: ' + relative)
    return path


def verify_hash(relative, expected):
    path = root_file(relative)
    require(sha(path.read_bytes()) == expected, 'fingerprint mismatch: ' + relative)
    return path


def legendre_rodrigues(n):
    coefficients = [fmpq(0)] * (n + 1)
    for k in range(n // 2 + 1):
        coefficients[n - 2 * k] = fmpq(
            (-1) ** k * math.comb(n, k) * math.comb(2 * n - 2 * k, n),
            1 << n)
    return fmpq_poly(coefficients)


def physical_polynomial(modes, coefficients):
    result = fmpq_poly([0])
    for mode, coefficient in zip(modes, coefficients):
        if coefficient:
            result += legendre_rodrigues(mode) * coefficient
    return result


def integral_unit(poly):
    return sum((poly[j] * fmpq(2, j + 1)
                for j in range(0, len(poly), 2)), fmpq(0))


def inner(left, right):
    return integral_unit(left * right)


def harmonic_table(maximum):
    values = [fmpq(0)]
    for n in range(1, maximum + 1):
        values.append(values[-1] + fmpq(1, n))
    return values


def physical_mass(modes, coefficients):
    return sum((fmpq(2, 2 * n + 1) * c * c
                for n, c in zip(modes, coefficients)), fmpq(0))


def jump(modes, coefficients, harmonic):
    return sum((fmpq(2, 2 * n + 1) * harmonic[n] * c * c
                for n, c in zip(modes, coefficients)), fmpq(0))


def potential_rational(product, harmonic):
    # The omitted logarithmic coefficient is -integral(product).
    return sum((product[j] *
                (2 * harmonic[j + 2] - harmonic[(j + 2) // 2]) / (j + 1)
                for j in range(0, len(product), 2)), fmpq(0))


def residual_coefficients():
    # Formal quotient, independently reconstructed instead of trusting R56.
    # (1-exp(-2t))*g = exp(-t/2) - (1-exp(-2t))/(2t).
    denominator = [fmpq(0)] + [
        fmpq((-1) ** (j + 1) * 2 ** j, math.factorial(j))
        for j in range(1, K + 3)
    ]
    quotient = []
    result = []
    for n in range(K + 1):
        rhs = fmpq(-1, 2) ** (n + 1) / math.factorial(n + 1)
        rhs -= denominator[n + 2] / 2
        rhs -= sum((denominator[j] * quotient[n + 1 - j]
                    for j in range(2, n + 2)), fmpq(0))
        coefficient = rhs / 2
        quotient.append(coefficient)
        # The entire polar term is -2*cosh(t/2), including degree zero.
        if n % 2 == 0:
            coefficient -= fmpq(2, 2 ** n * math.factorial(n))
        result.append(-T ** (n + 1) * coefficient)
    return result


def residual_forms(u, v, parity, kernel):
    # M_j and half moments are computed from power coefficients, not a
    # residual-head matrix.  The complete low boundary polynomial is paid.
    moments = []
    half = []
    for j in range(K + 1):
        moments.append(sum((u[k] * fmpq(2, k + j + 1)
                            for k in range(len(u)) if (k + j) % 2 == 0),
                           fmpq(0)))
        half.append(sum((u[k] / (k + j + 1) for k in range(len(u))),
                        fmpq(0)))
    require(all(not sum((v[k] * fmpq(2, k + j + 1)
                         for k in range(len(v)) if (k + j) % 2 == 0),
                        fmpq(0)) for j in range(K + 1)),
            'tail does not annihilate residual boundary polynomials')
    low = fmpq(0)
    tail = fmpq(0)
    cross = fmpq(0)
    primitive_u, primitive_v = u, v
    for d, coefficient in enumerate(kernel):
        if d % 2 == 0:
            low += coefficient * sum((
                (-1) ** j * math.comb(d, j) * moments[d - j] * moments[j]
                for j in range(d + 1)), fmpq(0))
        else:
            # At degree d, these are I^(d+1) with all constants zero at 0.
            primitive_u = primitive_u.integral().integral()
            primitive_v = primitive_v.integral().integral()
            scale = 2 * math.factorial(d)
            boundary = sum((math.comb(d, j) *
                            ((-1) ** parity - (-1) ** j) * half[j] *
                            moments[d - j] for j in range(d + 1)), fmpq(0))
            low += coefficient * (scale * inner(u, primitive_u) + boundary)
            tail += coefficient * scale * inner(v, primitive_v)
            cross += coefficient * scale * inner(v, primitive_u)
    return low, tail, cross


def manual_translate(poly, tau):
    # Horner multiplication by x+tau; no composition or midpoint map.
    translated = arb_poly([0])
    linear = arb_poly([tau, arb(1)])
    for j in range(len(poly) - 1, -1, -1):
        translated = translated * linear + arb_poly([poly[j]])
    return translated


def integrate_window(poly, right):
    antiderivative = poly.integral()
    return antiderivative(right) - antiderivative(arb(-1))


def arithmetic_forms(u, v, rows):
    require(isinstance(rows, list) and len(rows) == 3,
            'all three arithmetic terms are required')
    cutoff_low, cutoff_high = ends((2 * arb(T)).exp())
    require(4 < cutoff_low and cutoff_high < 5,
            'complete active prime-power cutoff')
    ua = arb_poly([arb(c) for c in u.coeffs()])
    va = arb_poly([arb(c) for c in v.coeffs()])
    low, cross = arb(0), arb(0)
    for m, row in zip((2, 3, 4), rows):
        require(set(row) == {'m', 'tau', 'coefficient', 'low', 'cross'} and
                type(row['m']) is int and row['m'] == m,
                'arithmetic term schema or order')
        tau = arb(m).log() / arb(T)
        coefficient = arb(3 if m == 3 else 2).log() / arb(m).sqrt()
        require(ends(tau)[0] > 0 and ends(tau)[1] < 2,
                'active shift outside overlap range')
        contains('arithmetic tau ' + str(m), row['tau'], tau)
        contains('von Mangoldt coefficient ' + str(m),
                 row['coefficient'], coefficient)
        shifted_u = manual_translate(ua, tau)
        shifted_v = manual_translate(va, tau)
        right = 1 - tau
        # Both shifts are retained explicitly.  No parity factor-of-two
        # identity from the producer is used for either form.
        low_integrand = ua * shifted_u + ua * shifted_u
        cross_integrand = va * shifted_u + ua * shifted_v
        term_low = -coefficient * integrate_window(low_integrand, right)
        term_cross = -coefficient * integrate_window(cross_integrand, right)
        contains('arithmetic low ' + str(m), row['low'], term_low)
        contains('arithmetic cross ' + str(m), row['cross'], term_cross)
        low += term_low
        cross += term_cross
    return low, cross


def verify_premises(packet):
    raw = (HERE / 'assessment-inputs-v1.json').read_bytes()
    require(sha(raw) == INPUTS_PIN and packet['inputs_sha256'] == INPUTS_PIN,
            'fixed assessment declaration identity')
    declaration = load(raw)
    expected = {
        'format': 'physical-reference-assessment-inputs-v1', 'N': N,
        'support': '3/4', 'alpha': '1/4', 'beta': '873/1024', 'floor': '1/3',
        'residual_order': K, 'source_precision_bits': 3072,
        'independent_precision_bits': BITS, 'published_rational_bits': 192,
        'tail_coefficient_grid_bits': 96, 'low_witness_space': [0, 311],
        'auxiliary_tail_degrees': [312, 623], 'new_support_or_admission': False,
    }
    for key, value in expected.items():
        require(declaration[key] == value, 'fixed declaration: ' + key)
    require(rational(declaration['leakage_deficit_upper']) == fmpq(3, 10 ** 49),
            'fixed complete leakage upper')
    require(declaration['critical_packet_sha256'] == CRITICAL_PIN and
            declaration['residual_packet_sha256'] == RESIDUAL_PIN and
            packet['residual_packet_sha256'] == RESIDUAL_PIN,
            'accepted premise pins')
    critical = load(verify_hash(declaration['critical_packet'],
                                CRITICAL_PIN).read_bytes())
    residual = load(verify_hash(declaration['residual_packet'],
                                RESIDUAL_PIN).read_bytes())
    require(critical['format'] == 'whole-space-residual-floor-assessment-v2'
            and critical['N'] == N and critical['support'] == '3/4'
            and critical['actual_Weil_negative_claim'] is False,
            'critical premise meaning')
    require(residual['format'] == 'exact-structured-residual-coupling-v1'
            and residual['N'] == N and residual['order'] == K
            and residual['support'] == '3/4'
            and residual['critical_witness_sha256'] == CRITICAL_PIN,
            'accepted residual premise meaning')
    require(packet['producer_sha256'] ==
            sha((HERE / 'assess-physical-v2.py').read_bytes()),
            'producer source identity')
    require(packet['model_sha256'] ==
            sha((HERE / 'physical_model_v1.py').read_bytes()),
            'model source identity')
    modules = packet['imported_project_modules']
    require(isinstance(modules, list) and modules, 'missing project source identities')
    seen = set()
    for item in modules:
        require(set(item) == {'path', 'sha256'} and item['path'] not in seen,
                'project source identity schema or duplicate')
        seen.add(item['path'])
        verify_hash(item['path'], item['sha256'])
    # Check the pinned residual packet's captured project files as well.
    for item in residual['imported_project_modules']:
        verify_hash(item['path'], item['sha256'])
    expected_proposal = (HERE / 'data' / 'proposal-v2.json').relative_to(ROOT).as_posix()
    require(packet['proposal_path'] == expected_proposal, 'fixed proposal selection')
    proposal = load(verify_hash(packet['proposal_path'],
                                packet['proposal_sha256']).read_bytes())
    require(proposal['format'] == 'whole-physical-dual-proposals-v2' and
            proposal['N'] == N and proposal['support'] == '3/4' and
            proposal['residual_order'] == K and proposal['auxiliary_extent'] == 624
            and proposal['low_space'] == 'ALL0..311' and
            proposal['status'] == 'NON_PROOF_PROPOSALS' and
            proposal['positive_finite_block_implies_whole_positivity'] is False and
            proposal['inputs_sha256'] == INPUTS_PIN,
            'proposal mathematical scope')
    require(proposal['model_code_sha256'] == packet['model_sha256'] and
            proposal['source_code_sha256'] ==
            sha((HERE / 'propose-physical-v2.py').read_bytes()),
            'proposal source identities')
    kernel = residual_coefficients()
    require(list(map(rational, residual['kernel_coefficients'])) == kernel,
            'independent complete residual coefficients')
    require(len(proposal['witnesses']) == 2 and
            [r['parity'] for r in proposal['witnesses']] == [0, 1],
            'both proposal parities')
    delta = rational(residual['complete_remainder_upper'])
    regular = (2 / arb.pi()) * (2 * arb(T) / arb.pi()) ** (K + 1)
    regular /= 1 - 2 * arb(T) / arb.pi()
    polar = 2 * arb(T) ** (K + 1) / math.factorial(K + 1)
    polar /= 1 - arb(T) / (K + 2)
    require(delta > 0, 'positive complete residual bound')
    bounded_above('complete regular plus polar remainder', delta,
                  2 * arb(T) * (regular + polar))
    return proposal, kernel, delta, 2 * arb(T) * regular


def verify_row(row, proposal_row, kernel, delta, native_regular, harmonic):
    parity = row['parity']
    require(type(parity) is int and parity in (0, 1) and
            proposal_row['parity'] == parity and
            type(row['proposal_index']) is int and row['proposal_index'] == 0,
            'fixed witness selection')
    selection = proposal_row['proposals'][0]
    low_modes = list(range(parity, N, 2))
    tail_modes = list(range(N + parity, 624, 2))
    require(selection['low_modes'] == low_modes and
            selection['tail_modes'] == tail_modes and row['tail_modes'] == tail_modes,
            'physical low and tail mode sets')
    require(len(row['low_coefficients']) == N and
            len(row['tail_coefficients']) == len(tail_modes) and
            len(selection['low_coefficients_grid96']) == len(low_modes) and
            len(selection['tail_coefficients_grid96']) == len(tail_modes),
            'physical coefficient dimensions')
    require(all(type(c) is int for c in selection['low_coefficients_grid96'] +
                selection['tail_coefficients_grid96']), 'integer proposal grid')
    low_coefficients = list(map(rational, row['low_coefficients']))
    tail_coefficients = list(map(rational, row['tail_coefficients']))
    selected_low = [fmpq(0)] * N
    for n, value in zip(low_modes, selection['low_coefficients_grid96']):
        selected_low[n] = fmpq(value, GRID)
    selected_tail = [fmpq(c, GRID) for c in selection['tail_coefficients_grid96']]
    require(low_coefficients == selected_low and tail_coefficients == selected_tail,
            'exact proposal coefficient binding')
    u = physical_polynomial(range(N), low_coefficients)
    v = physical_polynomial(tail_modes, tail_coefficients)
    uu, vv, uv = u * u, v * v, u * v
    nu, nv = integral_unit(uu), integral_unit(vv)
    require(nu > 0 and nv > 0, 'nonzero physical witnesses')
    require(nu == physical_mass(range(N), low_coefficients) and
            nv == physical_mass(tail_modes, tail_coefficients) and
            integral_unit(uv) == 0,
            'independent monomial mass and orthogonality')
    ju = jump(range(N), low_coefficients, harmonic)
    jv = jump(tail_modes, tail_coefficients, harmonic)
    vu = potential_rational(uu, harmonic)
    vtail = potential_rational(vv, harmonic)
    vc = potential_rational(uv, harmonic)
    ru, rv, rc = residual_forms(u, v, parity, kernel)
    exact = {
        'low_mass': nu, 'tail_mass': nv, 'jump_low': ju, 'jump_tail': jv,
        'residual_model_low': ru, 'residual_model_tail': rv,
        'potential_low_rational': vu, 'potential_tail_rational': vtail,
        'potential_cross': vc, 'residual_model_cross': rc,
    }
    require(set(row['exact']) == EXACT_KEYS, 'complete exact scalar schema')
    for key, value in exact.items():
        require(rational(row['exact'][key]) == value,
                'independent exact scalar mismatch: ' + key)
    published = row['intervals']
    require(set(published) == INTERVAL_KEYS, 'complete interval scalar schema')
    cT = arb.const_euler() + (3 * arb.pi() / 2).log()
    A0 = -arb.const_euler() - arb.pi() / 2 - 3 * arb(2).log() - arb.pi().log()
    Vu = arb(vu) - arb(nu) * arb(2).log()
    Vv = arb(vtail) - arb(nv) * arb(2).log()
    pu, pc = arithmetic_forms(u, v, row['arithmetic_terms'])
    low_model = arb(ju + ru) + Vu + pu - cT * arb(nu)
    cross_model = arb(vc + rc) + pc
    native = {
        'cT': cT, 'A0': A0, 'potential_low': Vu, 'potential_tail': Vv,
        'arithmetic_low': pu, 'arithmetic_cross': pc,
        'finite_low_model': low_model, 'model_cross': cross_model,
    }
    for key, value in native.items():
        contains(key, published[key], value)
    require(rational(row['delta_full_upper']) == delta,
            'complete residual remainder binding')
    dr = rational(row['delta_regular_upper'])
    require(dr > 0 and (dr * PUBLIC_GRID).denominator == 1,
            'regular remainder publication grid')
    bounded_above('complete analytic regular remainder', dr, native_regular)
    # Compare separate endpoint balls.  Constructing arb(0,error) would
    # round its radius to FLINT's magnitude precision rather than 4096 bits.
    low_error = arb(delta * nu)
    cross_error = arb(delta) * arb(nu * nv).sqrt()
    arch_model = arb(jv + rv) + Vv - cT * arb(nv)
    arch_error = arb(dr * nv)
    contains_range('complete actual low', published['actual_low'],
                   low_model - low_error, low_model + low_error)
    contains_range('complete actual cross', published['actual_cross'],
                   cross_model - cross_error, cross_model + cross_error)
    contains_range('complete regular archimedean tail', published['arch_tail'],
                   arch_model - arch_error, arch_model + arch_error)
    # True pole cancellation is analytic.  Every even model kernel is a
    # degree <=56 polynomial annihilated by v, already checked above.
    qh = rational(row['reference_h_upper'])
    qh_required = T * rational(published['arch_tail']['upper'])
    qh_required += (rational(published['A0']['upper']) / 4 -
                    fmpq(1129, 1024) + fmpq(3, 10 ** 49)) * nv
    require(qh >= nv / 3 and qh >= qh_required,
            'complete unscaled h reference bound')
    deficit = (rational(published['actual_low']['upper']) + qh -
               2 * rational(published['actual_cross']['lower']))
    require(rational(row['deficit_upper']) == deficit,
            'exact physical dual deficit publication')
    negative = deficit < 0
    require(type(row['strict_negative']) is bool and
            row['strict_negative'] == negative, 'strict negativity flag')
    return {
        'parity': parity, 'proposal_index': 0,
        'low_mass': str(nu), 'tail_mass': str(nv),
        'deficit_upper': str(deficit), 'strict_negative': bool(negative),
        'exact_scalar_checks': len(EXACT_KEYS),
        'interval_scalar_checks': len(INTERVAL_KEYS) + 12,
        'complete_regular_and_polar_remainders_checked': True,
        'both_shift_arithmetic_terms_checked': [2, 3, 4],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    arguments = parser.parse_args()
    require(not arguments.output.exists(), 'fresh audit output required')
    ctx.prec = BITS
    raw = arguments.packet.read_bytes()
    packet = load(raw)
    require(packet['format'] == 'complete-physical-reference-assessment-v1' and
            packet['support'] == '3/4' and type(packet['N']) is int and
            packet['N'] == N and type(packet['K']) is int and packet['K'] == K and
            type(packet['precision_bits']) is int and packet['precision_bits'] == 3072,
            'fixed source packet controls')
    require(packet['actual_Weil_negative_claim'] is False and
            packet['full_matrix_positive_claim'] is False,
            'false mathematical scope claim')
    proposal, kernel, delta, regular = verify_premises(packet)
    require(isinstance(packet['witnesses'], list) and len(packet['witnesses']) == 2
            and [r['parity'] for r in packet['witnesses']] == [0, 1],
            'both fixed physical witnesses')
    harmonic = harmonic_table(1248)
    rows = [verify_row(row, proposed, kernel, delta, regular, harmonic)
            for row, proposed in zip(packet['witnesses'], proposal['witnesses'])]
    negative = any(row['strict_negative'] for row in rows)
    require(type(packet['reference_rejection_proved']) is bool and
            packet['reference_rejection_proved'] == negative,
            'whole packet rejection flag')
    expected_status = ('STRICT_FIXED_REFERENCE_REJECTION' if negative else
                       'VALID_PHYSICAL_BOUNDS_NONREJECTING')
    require(packet['status'] == expected_status, 'source outcome status')
    audit = {
        'format': 'independent-physical-dual-audit-v1',
        'status': ('PASS_BOUNDS_AND_REFERENCE_REJECTION' if negative else
                   'PASS_BOUNDS_NONREJECTING'),
        'source_sha256': sha(raw),
        'audit_code_sha256': sha(Path(__file__).read_bytes()),
        'precision_bits': BITS, 'source_precision_bits': 3072,
        'published_rational_bits': 192, 'support': '3/4', 'N': N, 'K': K,
        'witnesses': rows, 'reference_rejection_proved': negative,
        'whole_supported_weighted_Gram_criterion_rejected': negative,
        'all_low_subtraction_choices_rejected': negative,
        'exact_fixed_compressed_g_reference_Schur_rejected': negative,
        'unscaled_complete_h_reference_used': True,
        'actual_Weil_negative_claim': False, 'full_matrix_positive_claim': False,
        'new_support_or_admission': False,
        'independent_mathematical_representations': True,
        'shared_FLINT_rational_and_Arb_library': True,
        'project_or_producer_math_imports': False,
        'accepted_critical_and_residual_pins_verified': True,
        'complete_actual_low_and_cross_remainders_checked': True,
        'complete_analytic_regular_tail_remainder_checked': True,
        'true_pole_cancelled_analytically_before_tail_enclosure': True,
        'all_native_scalar_bounds_strictly_inside_publication': True,
        'finite_positive_samples_imply_whole_positivity': False,
    }
    encoded = json.dumps(audit, sort_keys=True, indent=2) + '\n'
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with arguments.output.open('x', encoding='utf-8') as handle:
        handle.write(encoded)
    print(encoded, end='')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, AssertionError, KeyError, TypeError, IndexError,
            ZeroDivisionError, OverflowError, OSError) as error:
        raise SystemExit(type(error).__name__ + ': ' + str(error))
