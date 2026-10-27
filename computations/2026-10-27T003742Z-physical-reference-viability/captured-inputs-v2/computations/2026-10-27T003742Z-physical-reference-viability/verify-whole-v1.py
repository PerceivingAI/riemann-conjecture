"""Independent complete signed weighted-Gram source audit (not positivity).

Only python-flint and the Python standard library are imported.  Rodrigues
coefficients, endpoint primitives, binomial shifts, integration-by-parts log
moments, and upward spherical Bessel recurrence reconstruct the mathematics.
Both retained arithmetic P and GP enclosures are independently reconstructed.
"""
import os
for _variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                  'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_variable, '1')

import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path

from flint import acb, arb, arb_mat, arb_poly, ctx, fmpq, fmpq_poly

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N = 312
EXTENT = 624
DIM = 156
BITS = 192
SCALE = 1 << BITS
DECLARATION_PIN = '4c8ff1748fb3424e401d753b9be39031965265a41ab71ac564a11a9a8b3324b5'
ARITHMETIC_PIN = '9e7b0e03254261e4a971be192d21c7991faefaf2f71b0cbbfe8faf946b186cef'
RESIDUAL_PIN = 'afa2a31af3f25fbe1e75aa36633c2be70433fea0479e0d4bea90cd1899f2d01b'
PRODUCER_PIN = '9544fac738809ae929f52d6bbb74196b72442198dc59098438a66bd5f6867a34'
KINDS = ('A_model', 'weighted_head', 'weighted_complete_tail')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_object(items):
    result = {}
    for key, value in items:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def nonfinite(value):
    raise ValueError('nonfinite JSON token: ' + value)


def load(raw):
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=nonfinite)


def rational(value):
    require(type(value) is str, 'rational must be a string')
    result = fmpq(value)
    require(str(result) == value, 'noncanonical rational: ' + value)
    return result


def endpoints(value):
    require(value.is_finite(), 'nonfinite independent enclosure')
    return value.lower().fmpq(), value.upper().fmpq()


def pinned(path, expected):
    raw = path.read_bytes()
    require(digest(raw) == expected, 'SHA256 mismatch: ' + str(path))
    return raw


def confined(base, relative):
    require(type(relative) is str and not Path(relative).is_absolute(),
            'expected confined relative path')
    result = (base / relative).resolve()
    require(result.is_relative_to(base), 'path escapes source bundle/root')
    return result


def diagonal(values):
    result = arb_mat(len(values), len(values))
    for i, value in enumerate(values):
        result[i, i] = value
    return result


def symmetrize(matrix):
    return (matrix + matrix.transpose()) * arb(fmpq(1, 2))


def rodrigues(n):
    coefficients = [fmpq(0)] * (n + 1)
    for k in range(n // 2 + 1):
        coefficients[n - 2 * k] = fmpq(
            (-1) ** k * math.comb(n, k) * math.comb(2 * n - 2 * k, n),
            1 << n)
    return fmpq_poly(coefficients)


def harmonic_tables(maximum):
    h, h2 = [fmpq(0)], [fmpq(0)]
    for k in range(1, maximum + 1):
        h.append(h[-1] + fmpq(1, k))
        h2.append(h2[-1] + fmpq(1, k * k))
    return h, h2


def residual_kernel():
    # Formal series quotient, including both even polar kernels and constants.
    denominator = [fmpq(0)] + [
        fmpq((-1) ** (j + 1) * 2 ** j, math.factorial(j))
        for j in range(1, 59)]
    quotient, result = [], []
    for n in range(57):
        rhs = fmpq(-1, 2) ** (n + 1) / math.factorial(n + 1)
        rhs -= denominator[n + 2] / 2
        rhs -= sum((denominator[j] * quotient[n + 1 - j]
                    for j in range(2, n + 2)), fmpq(0))
        coefficient = rhs / 2
        quotient.append(coefficient)
        if n % 2 == 0:
            coefficient -= fmpq(2, 2 ** n * math.factorial(n))
        result.append(-fmpq(3, 4) ** (n + 1) * coefficient)
    return result


def residual_outputs(polynomials, kernel):
    # I_-1 and I_1 are independently endpoint-normalized power primitives.
    # Integral |x-y|^d P_n(y)dy = d! [I_-1^(d+1)P_n
    #                                  + (-1)^(d+1) I_1^(d+1)P_n].
    # This includes the low boundary polynomial, not just a positive-index walk.
    outputs = []
    for n in range(N):
        left = right = polynomials[n]
        result = fmpq_poly([0])
        for d, coefficient in enumerate(kernel):
            left = left.integral()
            right = right.integral()
            left -= fmpq_poly([left(fmpq(-1))])
            right -= fmpq_poly([right(fmpq(1))])
            result += (left + right * ((-1) ** (d + 1))) * (
                coefficient * math.factorial(d))
        require(len(result) <= n + 57 or n < 57,
                'residual output exceeds degree/band proof')
        require(len(result) <= EXTENT,
                'R56 has a nonzero physical output beyond Q624')
        require(all(not result[k] for k in range(1 - n % 2, len(result), 2)),
                'residual parity violation at mode ' + str(n))
        outputs.append(result)
    return outputs


def monomial_legendre_moment(k, n):
    if k < n or (k - n) % 2:
        return fmpq(0)
    # 2 k! / ((k-n)!! (k+n+1)!!), ordinary, not normalized, mass.
    denominator = (2 ** ((k - n) // 2) * math.factorial((k - n) // 2))
    odd = k + n + 1
    denominator *= math.factorial(odd) // (
        2 ** ((odd - 1) // 2) * math.factorial((odd - 1) // 2))
    return fmpq(2 * math.factorial(k), denominator)


def residual_blocks(outputs, parity):
    low = list(range(parity, N, 2))
    tail = list(range(N + parity, EXTENT, 2))
    degree = max(len(outputs[n]) for n in low)
    powers = list(range(parity, degree, 2))
    output_coefficients = arb_mat([
        [arb(outputs[n][k]) for n in low] for k in powers])
    def block(modes):
        moments = arb_mat([[arb(monomial_legendre_moment(k, m))
                            for k in powers] for m in modes])
        return moments * output_coefficients
    return block(low), block(tail)


def binomial_shift(poly, tau, factorials):
    # q_j = sum_{k>=j} p_k binom(k,j) tau^(k-j).  One convolution
    # evaluates this manual binomial formula without polynomial composition.
    n = len(poly) - 1
    reversed_scaled = arb_poly([arb(poly[k] * factorials[k])
                               for k in range(n, -1, -1)])
    exponential = [arb(1)]
    for k in range(1, n + 1):
        exponential.append(exponential[-1] * tau / k)
    product = reversed_scaled * arb_poly(exponential)
    return [product[n - j] / factorials[j] for j in range(n + 1)]


def power_window_moments(left, right, maximum):
    lp, rp = arb(1), arb(1)
    result = []
    for k in range(maximum + 1):
        lp *= left
        rp *= right
        result.append((rp - lp) / (k + 1))
    return result


def log_minus_primitives(x, maximum, harmonic, at_one=False):
    # Integration by parts with a polynomial division of x^(k+1)/(1-x).
    # At x=1 the removable (x^(k+1)-1) log(1-x) term is exactly zero.
    if at_one:
        return [-arb(harmonic[k + 1]) / (k + 1)
                for k in range(maximum + 1)]
    logarithm = (1 - x).log()
    power, partial = arb(1), arb(0)
    result = []
    for k in range(maximum + 1):
        power *= x
        partial += power / (k + 1)
        result.append(((power - 1) * logarithm - partial) / (k + 1))
    return result


def logarithmic_window_moments(left, right, maximum, harmonic,
                               left_minus_one=False, right_one=False):
    la = log_minus_primitives(left, maximum, harmonic)
    lb = log_minus_primitives(right, maximum, harmonic, at_one=right_one)
    ra = log_minus_primitives(-right, maximum, harmonic)
    rb = log_minus_primitives(-left, maximum, harmonic, at_one=left_minus_one)
    return [-(lb[k] - la[k] + (-1) ** k * (rb[k] - ra[k])) / 2
            for k in range(maximum + 1)]


def arithmetic_blocks(polynomials, parity, harmonic):
    modes = list(range(parity, N, 2))
    tail = list(range(N + parity, EXTENT, 2))
    coefficients_low = arb_mat([[arb(polynomials[n][2 * k + parity])
                                 for k in range(DIM)] for n in modes])
    coefficients_tail = arb_mat([[arb(polynomials[n][2 * k + parity])
                                  for k in range(N)] for n in tail])
    plow, ptail, vp = (arb_mat(DIM, DIM) for _ in range(3))
    factorials = [math.factorial(k) for k in range(N)]
    cutoff = (arb(fmpq(3, 2))).exp()
    require(4 < endpoints(cutoff)[0] and endpoints(cutoff)[1] < 5,
            'incomplete active prime-power cutoff')
    for m in (2, 3, 4):
        tau = arb(m).log() / arb(fmpq(3, 4))
        coefficient = arb(3 if m == 3 else 2).log() / arb(m).sqrt()
        require(0 < endpoints(tau)[0] and endpoints(tau)[1] < 2,
                'arithmetic window outside support')
        # Both physical translation windows are evaluated separately.  No
        # reflected-parity factor of two is used in P or in the signed VP.
        windows = ((arb(-1), 1 - tau, tau, True, False),
                   (-1 + tau, arb(1), -tau, False, True))
        for left, right, shift, left_endpoint, right_endpoint in windows:
            shifted = []
            for n in modes:
                row = binomial_shift(polynomials[n], shift, factorials)
                shifted.append(row + [arb(0)] * (N - len(row)))
            shifted_transpose = arb_mat(shifted).transpose()
            moments = power_window_moments(left, right, 934)
            low_moments = arb_mat([[moments[2 * k + parity + j]
                                     for j in range(N)] for k in range(DIM)])
            tail_moments = arb_mat([[moments[2 * k + parity + j]
                                      for j in range(N)] for k in range(N)])
            logarithms = logarithmic_window_moments(
                left, right, 622, harmonic, left_endpoint, right_endpoint)
            log_moments = arb_mat([[logarithms[2 * k + parity + j]
                                     for j in range(N)] for k in range(DIM)])
            low_images = low_moments * shifted_transpose
            tail_images = tail_moments * shifted_transpose
            log_images = log_moments * shifted_transpose
            plow -= coefficients_low * low_images * coefficient
            ptail -= coefficients_tail * tail_images * coefficient
            vp -= coefficients_low * log_images * coefficient
    return plow, ptail, vp


def inherited_matrix(packet, name, parity):
    rows = packet['matrices'][name]
    require(len(rows) == N and all(len(row) == N - i
                                    for i, row in enumerate(rows)),
            'retained ' + name + ': ragged upper-triangle schema')
    bits = packet['bits']
    require(type(bits) is int and bits == 128, 'retained precision mismatch')
    modes = list(range(parity, N, 2))
    result = arb_mat(DIM, DIM)
    for i, m in enumerate(modes):
        for j, n in enumerate(modes):
            pair = rows[min(m, n)][abs(m - n)]
            require(type(pair) is list and len(pair) == 2 and
                    all(type(x) is int for x in pair) and pair[0] <= pair[1],
                    'invalid retained interval ' + name)
            low, high = (fmpq(x, 1 << bits) for x in pair)
            result[i, j] = arb((low + high) / 2, arb((high - low) / 2))
    return result


def assert_retained(packet, name, matrix, parity):
    modes = list(range(parity, N, 2))
    for i, m in enumerate(modes):
        for j, n in enumerate(modes):
            pair = packet['matrices'][name][min(m, n)][abs(m - n)]
            low, high = endpoints(matrix[i, j])
            require(fmpq(pair[0], 1 << packet['bits']) <= low and
                    high <= fmpq(pair[1], 1 << packet['bits']),
                    'independent arithmetic ' + name + ' outside retained enclosure: '
                    + str((m, n)))


def complete_arithmetic_squared(parity, nodes):
    # On each overlap cell, PP_n is a polynomial of degree <=311.
    # Gauss312 therefore integrates every squared/mixed product exactly.
    # All shifts are summed BEFORE the Gram, retaining every 2/3/4 mixed term.
    shifts = [(arb(m).log() / arb(fmpq(3, 4)),
               arb(3 if m == 3 else 2).log() / arb(m).sqrt())
              for m in (2, 3, 4)]
    boundaries = [arb(0), 1 - shifts[0][0], shifts[1][0] - 1,
                  shifts[2][0] - 1, arb(1)]
    for left, right in zip(boundaries, boundaries[1:]):
        require(endpoints(right - left)[0] > 0,
                'arithmetic squared overlap cells are not strictly ordered')
    result = arb_mat(DIM, DIM)
    modes = list(range(parity, N, 2))
    for left, right in zip(boundaries, boundaries[1:]):
        midpoint, half = (left + right) / 2, (right - left) / 2
        active = []
        for tau, coefficient in shifts:
            for signed_tau in (tau, -tau):
                lo, hi = endpoints(midpoint + signed_tau)
                if -1 < lo and hi < 1:
                    active.append((signed_tau, coefficient))
                else:
                    require(hi < -1 or 1 < lo,
                            'uncertain arithmetic squared cell membership')
        rows, weighted_rows = [], []
        for node, weight in nodes:
            x = midpoint + half * node
            row = [arb(0) for _ in modes]
            for signed_tau, coefficient in active:
                z = x + signed_tau
                values = [arb(1), z]
                for n in range(1, N - 1):
                    values.append(((2 * n + 1) * z * values[-1] -
                                   n * values[-2]) / (n + 1))
                for j, n in enumerate(modes):
                    row[j] -= coefficient * values[n]
            # PP preserves physical parity; its same-parity product is even.
            # Only this full squared Gram uses reflection of positive cells.
            reflected_weight = 2 * half * weight
            rows.append(row)
            weighted_rows.append([value * reflected_weight for value in row])
        result += arb_mat(rows).transpose() * arb_mat(weighted_rows)
    return symmetrize(result)


def inverse_weight_function(t):
    a0 = -arb.const_euler() - arb.pi() / 2 - 3 * arb.const_log2() - arb.pi().log()
    return (arb(fmpq(3, 4)) *
            (acb(arb(fmpq(1, 4)), arb(t) / 2).digamma().real - arb.pi().log())
            + a0 / 4 - arb(fmpq(1129, 1024)))


def validate_weights(source):
    expected = [fmpq(0), fmpq(256)]
    while expected[-1] * fmpq(17, 16) < 8192:
        expected.append(expected[-1] * fmpq(17, 16))
    expected.append(fmpq(8192))
    edges = [rational(x) for x in source['frequency_edges']]
    weights = [rational(x) for x in source['inverse_weight_uppers']]
    require(edges == expected and len(weights) == len(edges),
            'frequency partition anchors or coverage mismatch')
    require(weights[0] == 3 and all(0 < w <= 3 for w in weights),
            'invalid inverse-weight floor or upper choice')
    require(all(weights[k] >= weights[k + 1] for k in range(len(weights) - 1)),
            'nonmonotone inverse step majorant')
    # Re digamma(a+iy) has positive derivative for y>0: its convergent
    # series has derivative sum 2y(k+a)/((k+a)^2+y^2)^2.  Thus the
    # left endpoint anchor bounds 1/h throughout each rightward cell.
    for edge, weight in zip(edges[1:], weights[1:]):
        value = inverse_weight_function(edge)
        require(endpoints(value)[0] > fmpq(1, 3), 'unqualified weight anchor')
        require(weight >= endpoints(1 / value)[1],
                'inverse step weight underpays anchor ' + str(edge))
    c, m = fmpq(384), 624
    ratio = c * c / ((2 * m + 1) * (2 * m + 3))
    require(0 <= ratio < 1, 'invalid leakage geometric ratio')
    double_factorial = math.factorial(2 * m + 1) // (2 ** m * math.factorial(m))
    leakage_bound = (2 * arb(c) / arb.pi() * arb(
        (2 * m + 1) * c ** (2 * m) / double_factorial ** 2 / (1 - ratio)))
    leakage = rational(source['physical_tail_leakage_upper'])
    require(endpoints(leakage_bound)[1] <= leakage <= 1,
            'complete physical exterior leakage is underpaid')
    anchor = rational(source['tail_inverse_anchor_upper'])
    g512 = inverse_weight_function(fmpq(512))
    require(endpoints(g512)[0] > fmpq(1, 3), 'unqualified tail anchor')
    require(endpoints(1 / g512)[1] <= anchor <= 3,
            'tail inverse anchor is underpaid')
    kappa = rational(source['weighted_tail_norm_upper'])
    require(kappa == anchor + (3 - anchor) * leakage,
            'tail inverse norm combination mismatch')
    return edges, weights, kappa


def frequency_kernels(edges, weights):
    modes = [list(range(N + parity, EXTENT, 2)) for parity in (0, 1)]
    result = [diagonal([arb(weights[-1] * fmpq(2, 2 * n + 1))
                        for n in ids]) for ids in modes]
    # The nonzero final diagonal pays the entire frequency exterior, not a
    # truncated frequency integral and not an inverse compressed-form shortcut.
    for k, omega in enumerate(edges[1:]):
        c = arb(fmpq(3, 4) * omega)
        sine, cosine = c.sin(), c.cos()
        js = [sine / c, (sine - c * cosine) / (c * c)]
        for n in range(1, EXTENT):
            js.append((2 * n + 1) / c * js[-1] - js[-2])
        derivatives = [n / c * js[n] - js[n + 1] for n in range(EXTENT)]
        diagonal_integrals = [(2 * c).si() + ((2 * c).cos() - 1) / (2 * c)]
        for n in range(1, EXTENT):
            diagonal_integrals.append(diagonal_integrals[-1] -
                                      c * (js[n - 1] ** 2 + js[n] ** 2))
        difference = arb(weights[k] - weights[k + 1])
        for parity, ids in enumerate(modes):
            block = arb_mat(DIM, DIM)
            for i, n in enumerate(ids):
                block[i, i] = 4 * diagonal_integrals[n] / (arb.pi() * (2 * n + 1))
                for j in range(i):
                    m = ids[j]
                    value = (4 / arb.pi() * ((-1) ** ((m - n) // 2)) * c ** 2 *
                             (derivatives[n] * js[m] - derivatives[m] * js[n]) /
                             (n * (n + 1) - m * (m + 1)))
                    block[i, j] = block[j, i] = value
            result[parity] += block * difference
    return [symmetrize(matrix) for matrix in result]


def reconstruct(parity, polynomials, outputs, harmonic, harmonic2,
                inherited, frequency_kernel, kappa, nodes):
    modes = list(range(parity, N, 2))
    tail = list(range(N + parity, EXTENT, 2))
    masses = [fmpq(2, 2 * n + 1) for n in modes]
    tail_masses = [fmpq(2, 2 * n + 1) for n in tail]
    inverse_mass = diagonal([arb(1 / x) for x in masses])
    inverse_tail_mass = diagonal([arb(1 / x) for x in tail_masses])
    def v(m, n):
        if m == n:
            return arb(fmpq(2, 2 * n + 1)) * (
                2 * arb(harmonic[2 * n]) - 2 * arb(harmonic[n]) +
                arb(fmpq(1, 2 * n + 1)) - arb.const_log2())
        return arb(fmpq(2, abs(m - n) * (m + n + 1)))
    potential = arb_mat([[v(m, n) for n in modes] for m in modes])
    potential_tail = arb_mat([[v(m, n) for n in modes] for m in tail])
    residual, residual_tail = residual_blocks(outputs, parity)
    arithmetic, arithmetic_tail, vp_full = arithmetic_blocks(polynomials, parity, harmonic)
    # Reconstruct both accepted arithmetic fields tightly.  Repropagating the
    # old 128-bit radii through new associations would not prove containment.
    inherited_matrix(inherited, 'P', parity)
    inherited_matrix(inherited, 'GP', parity)
    assert_retained(inherited, 'P', arithmetic, parity)
    gp_q312 = (complete_arithmetic_squared(parity, nodes) -
               arithmetic.transpose() * inverse_mass * arithmetic)
    assert_retained(inherited, 'GP', gp_q312, parity)
    c_t = arb.const_euler() + (2 * arb.pi() * arb(fmpq(3, 4))).log()
    jump = diagonal([arb(masses[i]) * (arb(harmonic[n]) - c_t)
                     for i, n in enumerate(modes)])
    a_model = jump + potential + arithmetic + residual
    vv_moments = []
    for r in range(N):
        log_mean = 2 * arb.const_log2() - 2 * arb(harmonic[2 * r + 2]) + arb(harmonic[r + 1])
        trigamma = (-arb.pi() ** 2 / 3 + 4 * arb(harmonic2[2 * r + 2]) -
                    arb(harmonic2[r + 1]))
        vv_moments.append((log_mean ** 2 + trigamma) / (2 * (2 * r + 1)))
    coefficients = arb_mat([[arb(polynomials[n][2 * k + parity])
                            for k in range(DIM)] for n in modes])
    moment_matrix = arb_mat([[vv_moments[i + j + parity] for j in range(DIM)]
                             for i in range(DIM)])
    vv_full = coefficients * moment_matrix * coefficients.transpose()
    gv_tail = (vv_full - potential * inverse_mass * potential -
               potential_tail.transpose() * inverse_tail_mass * potential_tail)
    gp_tail = gp_q312 - arithmetic_tail.transpose() * inverse_tail_mass * arithmetic_tail
    vp_tail = (vp_full - potential * inverse_mass * arithmetic -
               potential_tail.transpose() * inverse_tail_mass * arithmetic_tail)
    # Both signs and both mixed orientations are present in the exact complete
    # omitted-output Gram.  R56 is absent here by the proved polynomial degree.
    complete_gram = gv_tail + gp_tail + vp_tail + vp_tail.transpose()
    expansion = inverse_tail_mass * (potential_tail + arithmetic_tail + residual_tail)
    return {'A_model': symmetrize(a_model),
            'weighted_head': symmetrize(expansion.transpose() * frequency_kernel * expansion),
            'weighted_complete_tail': symmetrize(symmetrize(complete_gram) * arb(kappa))}


def check_matrix(source, kind, parity, independent):
    key = kind + '-' + str(parity)
    descriptor = source['matrices'][key]
    require(set(descriptor) == {'path', 'sha256', 'size'}, 'matrix descriptor schema: ' + key)
    raw = pinned(confined(HERE, descriptor['path']), descriptor['sha256'])
    require(type(descriptor['size']) is int and len(raw) == descriptor['size'],
            'matrix compressed size mismatch: ' + key)
    payload = load(gzip.decompress(raw))
    require(set(payload) == {'kind', 'parity', 'dimension', 'bits', 'upper_triangle'},
            'matrix payload schema: ' + key)
    require(payload['kind'] == kind and type(payload['parity']) is int and
            payload['parity'] == parity and type(payload['dimension']) is int and
            payload['dimension'] == DIM and type(payload['bits']) is int and
            payload['bits'] == BITS, 'matrix identity mismatch: ' + key)
    triangle = payload['upper_triangle']
    require(type(triangle) is list and len(triangle) == DIM * (DIM + 1) // 2,
            'matrix triangular entry count mismatch: ' + key)
    offset = 0
    for i in range(DIM):
        for j in range(i, DIM):
            pair = triangle[offset]
            require(type(pair) is list and len(pair) == 2 and
                    all(type(x) is int for x in pair) and pair[0] < pair[1],
                    'invalid signed dyadic pair: ' + key + ' ' + str((i, j)))
            lower, upper = endpoints(independent[i, j])
            published_lower, published_upper = (fmpq(x, SCALE) for x in pair)
            require(published_lower <= lower <= upper <= published_upper,
                    'source enclosure fails at ' + key + ' cell ' + str((i, j)) +
                    '; published=[' + str(published_lower) + ',' + str(published_upper) +
                    ']; independently reconstructed=[' + str(lower) + ',' + str(upper) + ']')
            offset += 1
    return offset


def audit(source_path, precision):
    require(precision >= 4096, 'independent precision must be at least 4096 bits')
    ctx.prec = precision
    declaration_raw = pinned(HERE / 'whole-gram-inputs-v2.json', DECLARATION_PIN)
    declaration = load(declaration_raw)
    source_raw = source_path.read_bytes()
    source = load(source_raw)
    required_keys = {'format', 'support', 'N', 'physical_extent', 'order', 'bits',
                     'precision', 'basis', 'inputs_sha256', 'producer_sha256',
                     'frequency_edges', 'inverse_weight_uppers',
                     'physical_tail_leakage_upper', 'tail_inverse_anchor_upper',
                     'weighted_tail_norm_upper', 'model_error_upper', 'eta_lower',
                     'matrices', 'status', 'production_admission', 'imported_project_sources'}
    require(set(source) == required_keys, 'complete source top-level schema mismatch')
    require(source['format'] == 'complete-signed-weighted-Gram-source-v4',
            'expected current complete source format v4')
    require(source['inputs_sha256'] == DECLARATION_PIN,
            'source declaration fingerprint mismatch')
    require(source['producer_sha256'] == PRODUCER_PIN, 'producer declaration pin mismatch')
    pinned(HERE / 'build-whole-source-v4.py', PRODUCER_PIN)
    require(source['support'] == '3/4' and type(source['N']) is int and source['N'] == N and
            type(source['physical_extent']) is int and source['physical_extent'] == EXTENT and
            type(source['order']) is int and source['order'] == 56 and
            type(source['bits']) is int and source['bits'] == BITS and
            source['precision'] == declaration['source_precision_bits'] and
            source['basis'] == 'ordinary Legendre, physical masses 2/(2n+1)',
            'fixed support, dimensions, basis, or precision mismatch')
    require(source['production_admission'] is False and
            source['status'] == 'COMPLETE_INTERVAL_MATRICES_NOT_YET_POSITIVITY_VERIFIED',
            'source is not a nonadmitting complete interval assessment')
    require(source['eta_lower'] == declaration['reference_eta_lower'] and
            rational(source['eta_lower']) == 1 - fmpq(9, 10 ** 49),
            'eta lower mismatch')
    imports = source['imported_project_sources']
    require(type(imports) is dict and imports, 'missing producer import fingerprints')
    for relative, fingerprint in imports.items():
        require(relative.startswith('scripts/'), 'unexpected imported-source path')
        pinned(confined(ROOT, relative), fingerprint)
    require(set(source['matrices']) == {kind + '-' + str(p) for kind in KINDS for p in (0, 1)},
            'missing or extra complete matrix descriptor')
    require(declaration['old_combined_arithmetic_proof_sha256'] == ARITHMETIC_PIN and
            declaration['residual_packet_sha256'] == RESIDUAL_PIN,
            'retained raw source pin mismatch')
    inherited = load(gzip.decompress(pinned(
        confined(ROOT, declaration['old_combined_arithmetic_proof']), ARITHMETIC_PIN)))
    require(inherited['format'] == 'research-fourier-m4-minorant-matrix-v1' and
            inherited['dimension'] == N and inherited['active_terms'] == [2, 3, 4] and
            inherited['support'] == [3, 4] and
            inherited['basis'] == 'ordinary_unnormalized_legendre',
            'retained arithmetic source identity mismatch')
    residual_packet = load(pinned(confined(ROOT, declaration['residual_packet']), RESIDUAL_PIN))
    kernel = residual_kernel()
    require(kernel == [rational(x) for x in residual_packet['kernel_coefficients']],
            'R56 kernel differs from independent formal quotient')
    require(source['model_error_upper'] == declaration['model_error_upper'] ==
            residual_packet['complete_model_error_upper'], 'C117 model error mismatch')
    edges, weights, kappa = validate_weights(source)
    polynomials = [rodrigues(n) for n in range(EXTENT)]
    harmonic, harmonic2 = harmonic_tables(EXTENT + 2)
    outputs = residual_outputs(polynomials, kernel)
    kernels = frequency_kernels(edges, weights)
    nodes = [arb.legendre_p_root(N, j, weight=True) for j in range(N)]
    checked = 0
    for parity in (0, 1):
        reconstructed = reconstruct(parity, polynomials, outputs, harmonic, harmonic2,
                                    inherited, kernels[parity], kappa, nodes)
        for kind in KINDS:
            checked += check_matrix(source, kind, parity, reconstructed[kind])
    require(checked == 73476, 'incomplete matrix audit')
    return {'status': 'PASS_COMPLETE_SOURCE', 'source': str(source_path),
            'source_sha256': digest(source_raw), 'consumer_sha256': digest(Path(__file__).read_bytes()),
            'declaration_sha256': DECLARATION_PIN, 'independent_precision_bits': precision,
            'checked_matrix_files': 6, 'checked_triangular_entries': checked,
            'entry_requirement': 'independent endpoints contained in published 192-bit intervals',
            'retained_fields_independently_reconstructed': ['P', 'GP'],
            'inherited_arithmetic_sha256': ARITHMETIC_PIN,
            'frequency_anchors': len(edges), 'frequency_exterior_paid': True,
            'complete_signed_VP_Gram': True, 'ordinary_legendre_masses': '2/(2n+1)',
            'R56_exterior_zero': 'endpoint primitive polynomial degree strictly below 624',
            'positivity_checked': False, 'production_admission': False,
            'scope': 'complete mathematical source enclosure audit only; no positivity or admission claim'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--precision', type=int, default=4096)
    args = parser.parse_args()
    require(not args.output.exists(), 'refusing to overwrite audit output')
    try:
        result = audit(args.source.resolve(), args.precision)
        exit_code = 0
    except Exception as error:
        result = {'status': 'REJECT_COMPLETE_SOURCE', 'error_type': type(error).__name__,
                  'error': str(error), 'source': str(args.source.resolve()),
                  'positivity_checked': False, 'production_admission': False}
        exit_code = 1
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    with args.output.open('x', encoding='utf-8') as output:
        output.write(encoded)
    print(encoded, end='')
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
