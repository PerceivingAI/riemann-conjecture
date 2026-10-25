"""Audit inherited-source coupled-tail research without producer mathematics.

For a closed lower-bounded form, nested infima give Schur associativity.
The inherited complete S312 >= K therefore gives S20 >= Schur_E(K).
If r = (K(z,y))_E and K_EE >= g D, completing the square gives
q_K(z,y) - ||r||_(D^-1)^2/g <= z*Schur_E(K)z.  The entire outside
infinite tail is paid by the inherited complete S312 bound, not by a
finite inverse substituted for the full complement inverse.

For the actual principal C_E >= mu20 D, the finite variational energy
F(v) = 2 b_E*v - v*C_E*v has error at most
||C_E*v-b_E||_(D^-1)^2/mu20.  Restricting the full variational supremum
to E proves I_E <= I_true.  These are directional statements only;
this audit neither admits a theorem nor independently rebuilds sources.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import sys
import time

from scripts import verify_weighted_low_space as inherited
from scripts import verify_weighted_low_space_inputs as validation
from scripts import weil_coupled_tail_comparison as source

ROOT = Path(__file__).resolve().parents[1]
BITS = 352
GRID_BITS = 80
N = 20
M = 312
FORMAT = 'research-coupled-tail-comparison-audit-v1'
AUDITOR = 'scripts/verify_coupled_tail_comparison.py'
PRODUCER = 'scripts/weil_coupled_tail_comparison.py'
SCALARS = (
    'lower_quadratic', 'residual_dual_squared', 'residual_penalty',
    'true_schur_lower', 'galerkin_form_upper', 'a_lower', 'a_upper',
    'true_inverse_lower', 'true_inverse_upper', 'gain_lower',
    'finite_inverse_lower', 'finite_inverse_upper', 'outside_excess_upper',
    'stiffness_diagonal_lower', 'stiffness_diagonal_upper',
    'stiffness_offdiagonal_lower', 'stiffness_offdiagonal_upper',
    'stiffness_full_lower', 'stiffness_full_upper',
    'finite_residual_norm_upper',
)


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise ValueError(label)


def _round(value: Q, upward: bool) -> Q:
    scaled = value*(1 << BITS)
    return Q(scaled.__ceil__() if upward else scaled.__floor__(), 1 << BITS)


def _rational(value, label: str, grid_bits: int | None = None) -> Q:
    _require(type(value) is str, label+': expected rational string')
    result = Q(value)
    _require(str(result) == value, label+': noncanonical rational string')
    if grid_bits is not None:
        _require((result*(1 << grid_bits)).denominator == 1,
                 label+': value is not on the required dyadic grid')
    return result


def _fraction(value) -> Q:
    return Q(int(value.p), int(value.q))


def _norm(vector: list[Q], start: int = 0) -> Q:
    return sum((value*value*Q(2, 2*(start+i)+1)
                for i, value in enumerate(vector)), Q())


def _scale(pair: tuple[Q, Q], coefficient: Q) -> tuple[Q, Q]:
    left, right = pair[0]*coefficient, pair[1]*coefficient
    return min(left, right), max(left, right)


def _entry(triangle: list, i: int, j: int) -> tuple[Q, Q]:
    if i > j:
        i, j = j, i
    pair = triangle[i][j-i]
    _require(type(pair) is list and len(pair) == 2
             and all(type(value) is int for value in pair)
             and pair[0] <= pair[1], 'invalid inherited A_K entry')
    return Q(pair[0], 1 << BITS), Q(pair[1], 1 << BITS)


def _quadratic(triangle: list, vector: list[Q]) -> tuple[Q, Q]:
    lower = upper = Q()
    active = [i for i, value in enumerate(vector) if value]
    for offset, i in enumerate(active):
        for j in active[offset:]:
            coefficient = vector[i]*vector[j]*(1 if i == j else 2)
            left, right = _scale(_entry(triangle, i, j), coefficient)
            lower += left
            upper += right
    return lower, upper


def _finite_terms(triangle: list, z: list[Q], v: list[Q],
                  parity: int) -> tuple[Q, Q, Q]:
    """Separate cross/tail interval sums and the physical finite residual."""
    cross_lower = cross_upper = tail_lower = tail_upper = Q()
    active_low = [j for j, value in enumerate(z) if value]
    active_tail = [N+i for i, value in enumerate(v) if value]
    for k in active_tail:
        for j in active_low:
            left, right = _scale(_entry(triangle, k, j), z[j]*v[k-N])
            cross_lower += left
            cross_upper += right
    for offset, k in enumerate(active_tail):
        for j in active_tail[offset:]:
            coefficient = v[k-N]*v[j-N]*(1 if k == j else 2)
            left, right = _scale(_entry(triangle, k, j), coefficient)
            tail_lower += left
            tail_upper += right
    residual_squared = Q()
    for k in range(N+parity, M, 2):
        lower = upper = Q()
        for j in active_low:
            left, right = _scale(_entry(triangle, k, j), -z[j])
            lower += left
            upper += right
        for j in active_tail:
            left, right = _scale(_entry(triangle, k, j), v[j-N])
            lower += left
            upper += right
        residual_squared += max(abs(lower), abs(upper))**2*Q(2*k+1, 2)
    return (2*cross_lower-tail_upper, 2*cross_upper-tail_lower,
            residual_squared)


def _check_harmonic(triangle: list, z: list[Q], h: list[Q],
                    parity: int, mu: Q) -> None:
    """Check the fixed midpoint response, with ties rounded toward +infinity."""
    increment = Q()
    grid = 1 << GRID_BITS
    for k in range(N, M):
        if k > N:
            increment += Q(1, k)
        if k % 2 != parity:
            continue
        head = Q()
        for j, value in enumerate(z):
            if value:
                left, right = _entry(triangle, k, j)
                head += (left+right)*value/2
        physical_diagonal = Q(2, 2*k+1)*(mu+increment)
        expected = Q((head/physical_diagonal*grid+Q(1, 2)).__floor__(), grid)
        _require(h[k-N] == expected, 'fixed harmonic midpoint response changed')


def _stiffness(triangle: list, h: list[Q], mu: Q,
               delta: Q) -> dict[str, Q]:
    diagonal_lower = diagonal_upper = off_lower = off_upper = Q()
    harmonic = Q()
    active = [N+i for i, value in enumerate(h) if value]
    for k in range(N, M):
        if k > N:
            harmonic += Q(1, k)
        coefficient = h[k-N]*h[k-N]
        left, right = _scale(_entry(triangle, k, k), coefficient)
        reference = Q(2, 2*k+1)*(mu+harmonic)*coefficient
        diagonal_lower += left-reference
        diagonal_upper += right-reference
    for offset, k in enumerate(active):
        for j in active[offset+1:]:
            left, right = _scale(_entry(triangle, k, j), 2*h[k-N]*h[j-N])
            off_lower += left
            off_upper += right
    error = delta*_norm(h, N)
    return {'stiffness_diagonal_lower': diagonal_lower,
            'stiffness_diagonal_upper': diagonal_upper,
            'stiffness_offdiagonal_lower': off_lower,
            'stiffness_offdiagonal_upper': off_upper,
            'stiffness_full_lower': diagonal_lower+off_lower-error,
            'stiffness_full_upper': diagonal_upper+off_upper+error}


def _vector(row: dict, name: str, length: int, parity: int,
            start: int, grid_bits: int | None) -> list[Q]:
    values = row.get(name)
    _require(type(values) is list and len(values) == length,
             name+': missing full coordinate inventory')
    result = [_rational(value, name, grid_bits) for value in values]
    _require(all(not value for i, value in enumerate(result)
                 if (start+i) % 2 != parity), name+': nonzero opposite parity')
    return result


def _snap(pins: dict, label: str) -> dict[str, str]:
    _require(type(pins) is dict and bool(pins), label+': missing hashes')
    observed = {}
    for name, expected in pins.items():
        _require(type(name) is str and type(expected) is str
                 and len(expected) == 64, label+': invalid hash binding')
        observed[name] = hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    _require(observed == pins, label+': bound bytes changed')
    return observed


def _origins() -> None:
    for module, name in ((source, PRODUCER),
                         (inherited, 'scripts/verify_weighted_low_space.py'),
                         (validation, 'scripts/verify_weighted_low_space_inputs.py')):
        _require(Path(module.__file__).resolve() == (ROOT/name).resolve(),
                 'audit import origin changed: '+name)
    _require(Path(__file__).resolve() == (ROOT/AUDITOR).resolve(),
             'independent auditor origin changed')


def _row(row: dict, parity: int, context: dict) -> dict:
    _require(type(row) is dict and type(row.get('parity')) is int
             and row['parity'] == parity, 'altered parity inventory')
    reference = context['reference']
    original = reference['blocks'][parity]
    _require(original['parity'] == parity and row.get('trial') == original['trial'],
             'original C0091 physical trial changed')
    z = _vector(row, 'trial', N, parity, 0, None)
    _require(any(z), 'zero physical trial')
    y = _vector(row, 'coupled_minimizer', M-N, parity, N, GRID_BITS)
    v = _vector(row, 'finite_response', M-N, parity, N, GRID_BITS)
    h = _vector(row, 'harmonic_response', M-N, parity, N, GRID_BITS)
    g = _rational(row.get('g_exact'), 'g_exact')
    _require(g == context['gaps'][parity] and g > 0,
             'original certified mass-normalized gap changed')
    norm = _norm(z)
    _require(_rational(row.get('physical_norm_exact'), 'physical_norm_exact') == norm,
             'physical trial mass was normalized or changed')
    fields = {name: _rational(row.get(name), name, BITS) for name in SCALARS}
    reference_upper = original['directional_check']['reference_upper']
    _require(row.get('reference_upper') == reference_upper
             and Q(reference_upper) < 0, 'genuine negative C0091 reference upper changed')
    lower = context['lower']
    w = z+y
    active = [i for i, value in enumerate(w) if value]
    quadratic = Q()
    for i in active:
        for j in active:
            quadratic += w[i]*_fraction(lower[i, j])*w[j]
    residual_squared = Q()
    for k in range(N+parity, M, 2):
        residual = sum((_fraction(lower[k, j])*w[j] for j in active), Q())
        residual_squared += residual*residual*Q(2*k+1, 2)
    exact_bounds = {'lower_quadratic': _round(quadratic, False),
                    'residual_dual_squared': _round(residual_squared, True),
                    'residual_penalty': _round(residual_squared/g, True),
                    'true_schur_lower': _round(quadratic-residual_squared/g, False)}
    for name, expected in exact_bounds.items():
        _require(fields[name] == expected, name+': incorrect exact residual arithmetic')
    packet = context['packet']
    triangle = packet['matrices']['A_K']
    delta = Q(packet['delta'][1], 1 << BITS)
    mu = Q(reference['mu_reference_exact'])
    _require(mu > 0 and delta >= 0, 'invalid inherited coercivity or residual')
    a_lower, a_upper = _quadratic(triangle, z)
    a_lower -= delta*norm
    a_upper += delta*norm
    galerkin = z+[-value for value in v]
    galerkin_upper = _quadratic(triangle, galerkin)[1]+delta*_norm(galerkin)
    _require(fields['a_lower'] <= a_lower <= a_upper <= fields['a_upper'],
             'low form interval or full residual charge is unsafe')
    _require(fields['galerkin_form_upper'] >= galerkin_upper,
             'Galerkin upper underpays the full form or residual')
    _check_harmonic(triangle, z, h, parity, mu)
    derived = {
        'true_inverse_lower': _round(max(Q(), fields['a_lower']-
                                        fields['galerkin_form_upper']), False),
        'true_inverse_upper': _round(fields['a_upper']-fields['true_schur_lower'], True),
        'gain_lower': _round(fields['true_schur_lower']-Q(reference_upper), False),
        'outside_excess_upper': _round(fields['true_inverse_upper']-
                                      fields['finite_inverse_lower'], True),
    }
    for name, expected in derived.items():
        _require(fields[name] == expected, name+': incorrect directed consequence')
    f_lower, f_upper, r_squared = _finite_terms(triangle, z, v, parity)
    v_norm = _norm(v, N)
    perturbation = delta*(2*inherited._sqrt(norm*v_norm, BITS, True)+v_norm)
    finite_residual = (inherited._sqrt(r_squared, BITS, True)
                       +delta*inherited._sqrt(norm+v_norm, BITS, True))
    _require(fields['finite_residual_norm_upper'] >= finite_residual,
             'finite physical dual residual is underpaid')
    _require(fields['finite_inverse_lower'] <= max(Q(), f_lower-perturbation),
             'finite inverse variational lower is too large')
    _require(fields['finite_inverse_upper'] >=
             f_upper+perturbation+finite_residual*finite_residual/mu,
             'finite inverse upper underpays residual completion')
    for prefix in ('true_inverse', 'finite_inverse'):
        _require(0 <= fields[prefix+'_lower'] <= fields[prefix+'_upper'],
                 prefix+': invalid nonnegative inverse interval')
    _require(fields['outside_excess_upper'] >= 0
             and fields['finite_inverse_lower'] <= fields['true_inverse_upper'],
             'invalid outside-tail excess upper')
    _require(fields['true_schur_lower'] <= fields['galerkin_form_upper'],
             'contradictory true Schur lower and upper')
    stiffness = _stiffness(triangle, h, mu, delta)
    for name, bound in stiffness.items():
        _require(fields[name] >= bound if name.endswith('_upper') else fields[name] <= bound,
                 name+': unsafe signed stiffness endpoint')
    for component in ('diagonal', 'offdiagonal', 'full'):
        _require(fields['stiffness_'+component+'_lower'] <=
                 fields['stiffness_'+component+'_upper'],
                 component+': reversed stiffness interval')
    return {'parity': parity, 'checked_scalar_count': len(SCALARS)+3,
            'low_coordinate_count': N, 'response_coordinate_count': M-N,
            'physical_trial_unchanged': True, 'g_exact': str(g),
            'true_schur_lower': str(fields['true_schur_lower']),
            'true_schur_lower_positive': fields['true_schur_lower'] > 0,
            'finite_inverse_interval_verified': True,
            'outside_excess_upper': str(fields['outside_excess_upper']),
            'genuine_reference_gain_lower': str(fields['gain_lower']),
            'stiffness_components': 'TRUNCATED_A_K_MINUS_HARMONIC_DIAGONAL',
            'stiffness_total': 'FULL_FORM_WITH_RESIDUAL_ALLOWANCE'}


def audit(report_path: Path) -> dict:
    """Check every reported direction using independent Fraction interval sums."""
    started = time.perf_counter()
    _origins()
    before = source.fingerprint()
    _require(AUDITOR in before and PRODUCER in before,
             'source fingerprint omits the consumer or independent auditor')
    _snap(before, 'source')
    raw = report_path.read_bytes()
    report = validation.decode_json(raw)
    _require(type(report) is dict, 'report must be an object')
    context = source.load_context()
    inputs_before = _snap(context['bindings'], 'inherited input')
    expected = {'format': 'research-coupled-tail-comparison-v1',
                'source_sha256': before, 'input_sha256': inputs_before,
                'support': [1353, 2048], 'dimension': N,
                'coupled_boundary': M, 'inherited_head_boundary': 1018,
                'residual_order': 38, 'bits': BITS}
    for name, value in expected.items():
        _require(type(report.get(name)) is type(value) and report[name] == value,
                 'report identity changed: '+name)
    scope = report.get('scope')
    _require(type(scope) is str and 'inherited-source' in scope.lower()
             and 'no ' in scope.lower() and 'production admission' in scope.lower(),
             'missing inherited-source research scope')
    elapsed = report.get('elapsed_seconds')
    _require(type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0,
             'invalid elapsed time')
    packet = context['packet']
    _require(all(packet.get(name) == value for name, value in
                 {'bits': BITS, 'support': [1353, 2048], 'dimension': M,
                  'boundary': 1018, 'residual_order': 38}.items()),
             'accepted original source geometry changed')
    _require(context['lower'].nrows() == M and context['lower'].ncols() == M,
             'inherited complete K dimension changed')
    triangle = packet['matrices']['A_K']
    _require(type(triangle) is list and len(triangle) == M
             and all(type(row) is list and len(row) == M-i
                     for i, row in enumerate(triangle)), 'incomplete A_K triangle')
    rows = report.get('rows')
    _require(type(rows) is list and len(rows) == 2,
             'report must contain both parity directions')
    checked = [_row(row, parity, context)
               for parity, row in enumerate(rows)]
    selected_status = ('BOTH_TRUE_SCHUR_DIRECTIONS_POSITIVE'
                       if all(row['true_schur_lower_positive'] for row in checked)
                       else 'DIRECTIONAL_COMPARISON_INCONCLUSIVE')
    _require(report.get('status') == selected_status, 'directional outcome was assumed or mislabeled')
    _require(source.fingerprint() == before, 'source changed during audit')
    _snap(before, 'source')
    _require(_snap(context['bindings'], 'inherited input') == inputs_before,
             'input bindings changed during audit')
    _require(report_path.read_bytes() == raw, 'report changed during audit')
    return {'format': FORMAT, 'status': 'INHERITED_INPUT_CONSEQUENCES_ACCEPTED',
            'selected_status': selected_status,
            'report_sha256': hashlib.sha256(raw).hexdigest(),
            'source_sha256': before, 'input_sha256': inputs_before,
            'support': [1353, 2048], 'dimension': N, 'coupled_boundary': M,
            'inherited_head_boundary': 1018, 'residual_order': 38, 'bits': BITS,
            'response_grid_bits': GRID_BITS, 'parity_dimensions': [10, 10],
            'coupled_parity_dimensions': [146, 146],
            'checked_scalar_count': sum(row['checked_scalar_count'] for row in checked),
            'checked_response_coordinates': 2*3*(M-N), 'rows': checked,
            'complete_outside_tail_paid': True,
            'finite_inverse_is_not_full_inverse': True,
            'fresh_analytical_source_audit': False, 'new_theorem_admission': False,
            'data_authority': 'Inherited C0087 source and C0091 original-v2 evidence; '
                              'common legacy K reconstruction is inherited authority.',
            'scope': 'Fixed P20 inherited-source directional research; '
                     'no production admission or global operator comparison.',
            'elapsed_seconds': time.perf_counter()-started}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        _require(not args.output.exists(), 'output already exists')
        result = audit(args.report)
        with args.output.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
        print(json.dumps({'status': result['status'],
                          'selected_status': result['selected_status']}))
        return 0
    except Exception as exc:
        print('REJECTED: '+str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
