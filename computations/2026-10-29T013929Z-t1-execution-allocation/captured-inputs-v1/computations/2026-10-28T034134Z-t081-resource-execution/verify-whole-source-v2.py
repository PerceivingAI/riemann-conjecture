"""Independent T81/100 complete signed weighted-Gram source audit.

Only standard-library and python-flint operations are used. The sealed scalar
qualification is replayed by its pinned standalone declaration checker. All six
analytic matrix enclosures are reconstructed at 6144 bits without producer or
project mathematical imports. The reference beta is a supported-form bound,
not a pointwise multiplier bound. This audit does
not check positivity and cannot admit a production certificate.
"""
import os
for _variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                  'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_variable, '1')

import argparse
import gzip
import hashlib
import io
import json
import math
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path, PurePosixPath, PureWindowsPath

from flint import acb, arb, arb_mat, arb_poly, ctx, fmpq, fmpq_poly
from execution_events_v1 import emit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N, EXTENT, DIM, ORDER, BITS = 826, 1652, 413, 86, 256
SUPPORT = fmpq(81, 100)
SCALE = 1 << BITS
INPUTS_PIN = '19eac80d7869fcc6d6ddd0d33dcb90901b65254b2f076c6964148575019982a1'
DECLARATION_PIN = '026658a580d6ebe2ff8543d9e94ebbd24ea92d13027c5e43714e876cce353341'
SEAL_PIN = '7b29db1a39707f489de185c48d7b361077686e9713d294397e24466b3f4f0dc3'
PRODUCER_PIN = 'aacfb2d122b2bf62b1cf7940cb4aace764cdb11b413a504c81f15ca7b8427976'
DECLARATION_CHECKER_PIN = 'a99f306135c88c3a155ebc1cbea30866deac4a71c49d7dde0d6a2bd801edea3f'
ACTIVE_TERMS = ((2, 2), (3, 3), (4, 2), (5, 5))
KINDS = ('A_model', 'weighted_head', 'weighted_complete_tail')
MAX_JSON_BYTES = 32 * 1024 * 1024
MAX_COMPRESSED_BYTES = 32 * 1024 * 1024


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
    require(len(raw) <= MAX_JSON_BYTES, 'JSON byte limit exceeded')
    return json.loads(raw, object_pairs_hook=unique_object,
                      parse_constant=nonfinite, parse_float=Decimal)


def rational(value):
    require(type(value) is str and 0 < len(value) <= 20000,
            'rational must be a bounded string')
    result = fmpq(value)
    require(str(result) == value, 'noncanonical rational: ' + value)
    return result


def endpoints(value):
    require(value.is_finite(), 'nonfinite independent enclosure')
    return value.lower().fmpq(), value.upper().fmpq()


def bounded_bytes(path, maximum=MAX_JSON_BYTES):
    require(path.is_file(), 'missing regular file: ' + str(path))
    with path.open('rb') as handle:
        raw = handle.read(maximum + 1)
    require(len(raw) <= maximum, 'file byte limit exceeded: ' + str(path))
    return raw


def pinned(path, expected, maximum=MAX_JSON_BYTES):
    require(type(expected) is str and len(expected) == 64 and
            all(c in '0123456789abcdef' for c in expected), 'invalid SHA256')
    raw = bounded_bytes(path, maximum)
    require(digest(raw) == expected, 'SHA256 mismatch: ' + str(path))
    return raw


def confined(base, relative):
    require(type(relative) is str and relative and '\\' not in relative and
            '\x00' not in relative and ':' not in relative,
            'expected confined portable relative path')
    portable = PurePosixPath(relative)
    require(not portable.is_absolute() and not PureWindowsPath(relative).drive and
            all(part not in ('.', '..') for part in relative.split('/')),
            'invalid relative path component')
    result = (base / relative).resolve()
    require(result.is_relative_to(base.resolve()), 'path escapes source bundle/root')
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
        for j in range(1, ORDER + 3)]
    quotient, result = [], []
    for n in range(ORDER + 1):
        rhs = fmpq(-1, 2) ** (n + 1) / math.factorial(n + 1)
        rhs -= denominator[n + 2] / 2
        rhs -= sum((denominator[j] * quotient[n + 1 - j]
                    for j in range(2, n + 2)), fmpq(0))
        coefficient = rhs / 2
        quotient.append(coefficient)
        if n % 2 == 0:
            coefficient -= fmpq(2, 2 ** n * math.factorial(n))
        result.append(-SUPPORT ** (n + 1) * coefficient)
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
        require(len(result) <= n + ORDER + 1,
                'residual output exceeds degree/band proof')
        require(len(result) <= EXTENT,
                'finite residual has physical output at or beyond M')
        require(all(not result[k] for k in range(1 - n % 2, len(result), 2)),
                'residual parity violation at mode ' + str(n))
        outputs.append(result)
        if (n+1)%64==0 or n+1==N:
            emit('work',phase='residual_outputs',completed=n+1,total=N,unit='modes')
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
    cutoff = (arb(2 * SUPPORT)).exp()
    require(5 < endpoints(cutoff)[0] and endpoints(cutoff)[1] < 7,
            'incomplete active prime-power cutoff')
    for term_index,(m, prime) in enumerate(ACTIVE_TERMS):
        tau = arb(m).log() / arb(SUPPORT)
        coefficient = arb(prime).log() / arb(m).sqrt()
        require(0 < endpoints(tau)[0] and endpoints(tau)[1] < 2,
                'arithmetic window outside support')
        # Both physical translation windows are evaluated separately.  No
        # reflected-parity factor of two is used in P or in the signed VP.
        windows = ((arb(-1), 1 - tau, tau, True, False),
                   (-1 + tau, arb(1), -tau, False, True))
        for window_index,(left, right, shift, left_endpoint, right_endpoint) in enumerate(windows):
            shifted = []
            for n in modes:
                row = binomial_shift(polynomials[n], shift, factorials)
                shifted.append(row + [arb(0)] * (N - len(row)))
            shifted_transpose = arb_mat(shifted).transpose()
            moments = power_window_moments(left, right, 3 * N - 2)
            low_moments = arb_mat([[moments[2 * k + parity + j]
                                     for j in range(N)] for k in range(DIM)])
            tail_moments = arb_mat([[moments[2 * k + parity + j]
                                      for j in range(N)] for k in range(N)])
            logarithms = logarithmic_window_moments(
                left, right, 2 * N - 2, harmonic, left_endpoint, right_endpoint)
            log_moments = arb_mat([[logarithms[2 * k + parity + j]
                                     for j in range(N)] for k in range(DIM)])
            low_images = low_moments * shifted_transpose
            tail_images = tail_moments * shifted_transpose
            log_images = log_moments * shifted_transpose
            plow -= coefficients_low * low_images * coefficient
            ptail -= coefficients_tail * tail_images * coefficient
            vp -= coefficients_low * log_images * coefficient
            emit('work',phase='arithmetic_blocks',parity=parity,completed=2*term_index+window_index+1,total=8,unit='signed_windows')
    return plow, ptail, vp


def complete_arithmetic_squared(parity, nodes):
    # On each overlap cell, PP_n has degree <=825. Gauss826 integrates
    # every squared/mixed product exactly. Sum all signed 2/3/4/5 shifts
    # BEFORE the Gram. All nine physical cells are integrated independently.
    shifts = [(arb(m).log() / arb(SUPPORT),
               arb(prime).log() / arb(m).sqrt())
              for m, prime in ACTIVE_TERMS]
    boundaries = [arb(-1), arb(1)]
    for tau, _ in shifts:
        boundaries.extend([tau - 1, 1 - tau])
    boundaries.sort(key=lambda value: value.mid().fmpq())
    require(len(boundaries) - 1 == 9, 'incomplete arithmetic overlap partition')
    for left, right in zip(boundaries, boundaries[1:]):
        require(endpoints(right - left)[0] > 0,
                'arithmetic squared overlap cells are not strictly ordered')
    result = arb_mat(DIM, DIM)
    modes = list(range(parity, N, 2))
    for cell_index,(left, right) in enumerate(zip(boundaries, boundaries[1:]),1):
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
            rows.append(row)
            weighted_rows.append([value * half * weight for value in row])
        result += arb_mat(rows).transpose() * arb_mat(weighted_rows)
        emit('work',phase='complete_arithmetic_squared',parity=parity,completed=cell_index,total=9,unit='translation_cells')
    return symmetrize(result)


def inverse_weight_function(t, declaration):
    # Reflection/duplication give A_F(0) without a digamma evaluation at zero.
    a0 = -arb.const_euler() - arb.pi() / 2 - 3 * arb.const_log2() - arb.pi().log()
    alpha, beta = rational(declaration['alpha']), rational(declaration['beta'])
    return ((1 - alpha) *
            (acb(arb(fmpq(1, 4)), arb(t) / 2).digamma().real - arb.pi().log())
            + alpha * a0 - alpha - beta)


def validate_weights(source, declaration):
    expected = [fmpq(0), fmpq(declaration['R'])]
    terminal = 32 * expected[-1]
    while expected[-1] * fmpq(17, 16) < terminal:
        expected.append(expected[-1] * fmpq(17, 16))
    expected.append(terminal)
    require(type(source['frequency_edges']) is list and
            type(source['inverse_weight_uppers']) is list, 'invalid frequency arrays')
    edges = [rational(x) for x in source['frequency_edges']]
    weights = [rational(x) for x in source['inverse_weight_uppers']]
    require(edges == expected == [rational(x) for x in declaration['frequency_edges']],
            'frequency partition differs from sealed exact declaration')
    require(weights == [rational(x) for x in declaration['inverse_weight_step_uppers']]
            and len(weights) == len(edges), 'inverse weights differ from declaration')
    m = rational(declaration['m'])
    require(m == fmpq(1, 3) and weights[0] == 1 / m and
            all(0 < w <= 1 / m for w in weights), 'invalid inverse floor or weight')
    require(all(weights[k] >= weights[k + 1] for k in range(len(weights) - 1)),
            'nonmonotone inverse step majorant')
    # Re psi(a+iy) increases for y>0: each differentiated positive-series
    # summand is 2y(k+a)/((k+a)^2+y^2)^2. Thus a left-edge bound covers its
    # complete rightward cell. The final weight pays the infinite exterior.
    for edge, weight in zip(edges[1:], weights[1:]):
        value = inverse_weight_function(edge, declaration)
        require(endpoints(value)[0] > m, 'unqualified inverse-weight anchor')
        require(weight >= endpoints(1 / value)[1],
                'inverse weight underpays anchor ' + str(edge))
    kappa = rational(source['weighted_tail_norm_upper'])
    require(kappa == rational(declaration['weighted_physical_tail_inverse_upper'])
            and 0 < kappa <= 1 / m, 'sealed complete physical-tail bound mismatch')
    return edges, weights, kappa


def frequency_kernels(edges, weights):
    modes = [list(range(N + parity, EXTENT, 2)) for parity in (0, 1)]
    result = [diagonal([arb(weights[-1] * fmpq(2, 2 * n + 1))
                        for n in ids]) for ids in modes]
    # The nonzero final diagonal pays the entire frequency exterior, not a
    # truncated frequency integral and not an inverse compressed-form shortcut.
    for k, omega in enumerate(edges[1:]):
        c = arb(SUPPORT * omega)
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
        emit('work',phase='frequency_kernels',completed=k+1,total=len(edges)-1,unit='frequency_anchors')
    return [symmetrize(matrix) for matrix in result]


def reconstruct(parity, polynomials, outputs, harmonic, harmonic2,
                frequency_kernel, kappa, nodes):
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
    # Fresh combined square at this support, with all signed mixed products.
    gp_low = (complete_arithmetic_squared(parity, nodes) -
              arithmetic.transpose() * inverse_mass * arithmetic)
    c_t = arb.const_euler() + (2 * arb.pi() * arb(SUPPORT)).log()
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
    gp_tail = gp_low - arithmetic_tail.transpose() * inverse_tail_mass * arithmetic_tail
    vp_tail = (vp_full - potential * inverse_mass * arithmetic -
               potential_tail.transpose() * inverse_tail_mass * arithmetic_tail)
    # Both signs and both mixed orientations are present in the exact complete
    # omitted-output Gram.  R86 is absent here by the proved polynomial degree.
    complete_gram = gv_tail + gp_tail + vp_tail + vp_tail.transpose()
    expansion = inverse_tail_mass * (potential_tail + arithmetic_tail + residual_tail)
    return {'A_model': symmetrize(a_model),
            'weighted_head': symmetrize(expansion.transpose() * frequency_kernel * expansion),
            'weighted_complete_tail': symmetrize(symmetrize(complete_gram) * arb(kappa))}


def validate_model_allowance(declaration, kernel):
    eta = rational(declaration['eta'])
    require(eta == 1 - fmpq(1, 1 << 128), 'eta is not the frozen exact value')
    require(rational(declaration['alpha']) == fmpq(1, 4) and
            rational(declaration['beta']) == fmpq(821, 512), 'supported-form scalar reference changed')
    pi, t = arb.pi(), arb(SUPPORT)
    require(endpoints(pi - 2 * t)[0] > 0, 'canonical Taylor domain fails')
    delta = 2 * t * ((2 / pi) * (2 * t / pi) ** (ORDER + 1) /
                     (1 - 2 * t / pi) +
                     2 * t ** (ORDER + 1) /
                     (math.factorial(ORDER + 1) * (1 - t / (ORDER + 2))))
    arithmetic_norm = 2 * sum((arb(prime).log() / arb(m).sqrt()
                               for m, prime in ACTIVE_TERMS), arb(0))
    cross = pi / 2 + arithmetic_norm + 2 * arb(sum(
        (abs(c) * 2 ** d for d, c in enumerate(kernel)), fmpq(0)))
    allowance = delta + (2 * cross * delta + delta ** 2) / (
        arb(rational(declaration['m'])) * arb(eta))
    require(endpoints(delta)[1] <= rational(declaration['complete_remainder_upper']),
            'declared complete canonical remainder is underpaid')
    require(endpoints(cross)[1] <= rational(declaration['combined_model_cross_norm_upper']),
            'declared complete model-cross norm is underpaid')
    require(endpoints(allowance)[1] <= rational(declaration['complete_model_error_upper']),
            'declared complete canonical allowance is underpaid')


def check_matrix(source, source_parent, kind, parity, independent):
    key = kind + '-' + str(parity)
    descriptor = source['matrices'][key]
    require(type(descriptor) is dict and set(descriptor) == {'path', 'sha256', 'size'},
            'matrix descriptor schema: ' + key)
    require(type(descriptor['size']) is int and
            0 < descriptor['size'] <= MAX_COMPRESSED_BYTES,
            'invalid compressed size: ' + key)
    raw = pinned(confined(source_parent, descriptor['path']), descriptor['sha256'],
                 MAX_COMPRESSED_BYTES)
    require(len(raw) == descriptor['size'], 'compressed size mismatch: ' + key)
    with gzip.GzipFile(fileobj=io.BytesIO(raw), mode='rb') as compressed:
        expanded = compressed.read(MAX_JSON_BYTES + 1)
    payload = load(expanded)
    require(type(payload) is dict and
            set(payload) == {'kind', 'parity', 'dimension', 'bits', 'upper_triangle'},
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
                    all(type(x) is int and x.bit_length() <= 16384 for x in pair) and
                    pair[0] <= pair[1], 'invalid signed dyadic pair: ' + key + ' ' + str((i, j)))
            lower, upper = endpoints(independent[i, j])
            published_lower, published_upper = (fmpq(x, SCALE) for x in pair)
            require(published_lower <= lower <= upper <= published_upper,
                    'source enclosure fails at ' + key + ' cell ' + str((i, j)) +
                    '; published=[' + str(published_lower) + ',' + str(published_upper) +
                    ']; independent=[' + str(lower) + ',' + str(upper) + ']')
            offset += 1
        if (i+1)%64==0 or i+1==DIM:
            emit('work',phase='check_matrix',kind=kind,parity=parity,completed=offset,total=DIM*(DIM+1)//2,unit='entries')
    return offset


def frozen_inputs(path):
    raw = pinned(path, INPUTS_PIN)
    inputs = load(raw)
    required = {'K', 'M', 'N', 'bits', 'consumer_precision', 'created',
                'first_attempt_seal', 'first_attempt_seal_sha256', 'format',
                'production_admission', 'source_helper',
                'source_helper_sha256', 'source_precision', 'support',
                'target_declaration', 'target_declaration_sha256'}
    require(type(inputs) is dict and set(inputs) == required, 'whole-input schema mismatch')
    require(inputs['format'] == 't081-complete-gram-inputs-v1' and
            inputs['support'] == '81/100' and inputs['production_admission'] is False, 'whole-input identity mismatch')
    for key, value in (('K', ORDER), ('M', EXTENT), ('N', N), ('bits', BITS),
                       ('consumer_precision', 6144), ('source_precision', 4608)):
        require(type(inputs[key]) is int and inputs[key] == value,
                'frozen numerical input mismatch: ' + key)
    require(inputs['target_declaration_sha256'] == DECLARATION_PIN and
            inputs['first_attempt_seal_sha256'] == SEAL_PIN, 'declaration/seal pin mismatch')
    declaration = load(pinned(confined(ROOT, inputs['target_declaration']), DECLARATION_PIN))
    seal = load(pinned(confined(ROOT, inputs['first_attempt_seal']), SEAL_PIN))
    require(type(declaration) is dict and type(seal) is dict and
            declaration['format'] == 't081-qualified-target-declaration-v1' and
            seal['format'] == 't081-first-attempt-declaration-seal-v1' and
            seal['target_declaration_sha256'] == DECLARATION_PIN,
            'sealed target declaration identity mismatch')
    for packet in (declaration, seal):
        require(packet['support'] == '81/100' and packet['production_admission'] is False,
                'sealed target support/admission mismatch')
        for key, value in (('N', N), ('M', EXTENT), ('K', ORDER)):
            require(type(packet[key]) is int and packet[key] == value,
                    'sealed target dimension mismatch')
    require(declaration['first_attempt'] == seal['first_attempt'] and
            declaration['first_attempt']['core_symmetric_source_entries'] == 512946 and
            declaration['first_attempt']['parity_dimensions'] == [DIM, DIM] and
            declaration['first_attempt']['independent_combined_square_Gauss_order'] == N and
            declaration['first_attempt']['source_arithmetic_Gauss_order'] == 1239,
            'sealed first-attempt arithmetic mismatch')
    require(declaration['precision']['independent_bits'] == 6144 and
            declaration['precision']['matrix_publication_bits'] == BITS and
            declaration['precision']['source_bits'] == 4608 and
            2 * ORDER < N and EXTENT == 2 * N, 'sealed degree/precision policy mismatch')
    # This producer dependency is fingerprinted but never imported or evaluated.
    pinned(confined(ROOT, inputs['source_helper']), inputs['source_helper_sha256'])
    return raw, inputs, declaration, seal


def replay_declaration(inputs, declaration, seal):
    # Replay only the sealed scalar/reference qualification. Its checker and
    # nested reference checkers use stdlib/FLINT, never the matrix producer.
    # The supported-form beta cannot be treated as a pointwise rho bound.
    declaration_path = confined(ROOT, inputs['target_declaration'])
    bundle = declaration_path.parent.parent
    checker = confined(bundle, 'verify-target-declaration-v1.py')
    pinned(checker, DECLARATION_CHECKER_PIN)
    parameter_inputs = confined(bundle, 'parameter-inputs-v1.json')
    pinned(parameter_inputs, declaration['bindings']['inputs_sha256'])
    reference_audit = confined(bundle, 'data/supported-reference-audit-v1.json')
    require(declaration['bindings']['reference_audit_sha256'] ==
            seal['supported_reference_audit_sha256'] and
            declaration['bindings']['reference_source_sha256'] ==
            seal['supported_reference_source_sha256'],
            'sealed supported-reference binding mismatch')
    pinned(reference_audit, seal['supported_reference_audit_sha256'])
    accepted_raw = pinned(confined(bundle, 'data/target-declaration-audit-v1.json'),
                          seal['target_declaration_audit_sha256'])
    accepted = load(accepted_raw)
    require(type(accepted) is dict and
            accepted['format'] == 't081-target-declaration-independent-audit-v1' and
            accepted['status'] == 'PASS' and accepted['source_sha256'] == DECLARATION_PIN and
            accepted['consumer_sha256'] == DECLARATION_CHECKER_PIN and
            accepted['fresh_complete_reference_native_acceptance_replayed'] is True and
            accepted['full_remainder_and_coefficient_checks'] is True and
            accepted['frequency_weights_checked'] == 60 and
            accepted['N'] == N and accepted['verifiedK'] == ORDER and
            accepted['target_low_coupling_matrix_computed'] is False and
            accepted['target_positivity_proved'] is False and
            accepted['production_admission'] is False,
            'sealed scalar/reference qualification is not an accepted complete premise')
    with tempfile.TemporaryDirectory(prefix='t081_complete_gram_qualification_') as directory:
        output = Path(directory) / 'fresh-target-declaration-audit.json'
        command = [sys.executable, '-B', str(checker),
                   '--inputs', str(parameter_inputs), '--source', str(declaration_path),
                   '--reference-audit', str(reference_audit), '--output', str(output)]
        process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        require(process.returncode == 0 and output.is_file(),
                'fresh native scalar/reference qualification failed: ' +
                process.stdout + process.stderr)
        fresh = load(bounded_bytes(output))
        require(fresh == accepted, 'fresh scalar/reference qualification differs from sealed audit')
    return {'status': 'PASS_FRESH_NATIVE_DECLARATION_REPLAY',
            'declaration_checker_sha256': DECLARATION_CHECKER_PIN,
            'accepted_declaration_audit_sha256': digest(accepted_raw),
            'reference_source_sha256': seal['supported_reference_source_sha256'],
            'reference_audit_sha256': seal['supported_reference_audit_sha256'],
            'supported_form_beta': declaration['beta'],
            'reference_native_acceptance_replayed': True,
            'positivity_checked': False, 'production_admission': False}


def audit(inputs_path, source_path):
    ctx.prec = 6144
    inputs_raw, inputs, declaration, seal = frozen_inputs(inputs_path)
    qualification = replay_declaration(inputs, declaration, seal)
    source_raw = bounded_bytes(source_path)
    source = load(source_raw)
    required = {'format', 'support', 'N', 'physical_extent', 'order', 'bits',
                'precision', 'inputs_sha256', 'producer_sha256', 'frequency_edges',
                'inverse_weight_uppers', 'weighted_tail_norm_upper',
                'model_error_upper', 'eta_lower', 'matrices'}
    # Producer provenance metadata may be present; it is not a mathematical premise.
    require(type(source) is dict and required <= set(source), 'source core schema mismatch')
    require(source['format'] == 't081-complete-signed-weighted-Gram-source-v1' and
            source['support'] == '81/100', 'source format/support mismatch')
    require(source['inputs_sha256'] == digest(inputs_raw), 'whole-input fingerprint mismatch')
    producer = HERE / 'build-whole-source-v4.py'
    require(source['producer_sha256'] == PRODUCER_PIN, 'frozen producer pin mismatch')
    pinned(producer, PRODUCER_PIN)
    for key, value in (('N', N), ('physical_extent', EXTENT), ('order', ORDER),
                       ('bits', BITS), ('precision', inputs['source_precision'])):
        require(type(source[key]) is int and source[key] == value,
                'source numerical identity mismatch: ' + key)
    if 'production_admission' in source:
        require(source['production_admission'] is False, 'source claims production admission')
    if 'basis' in source:
        require(source['basis'] == 'ordinary Legendre, physical masses 2/(2n+1)',
                'source basis mismatch')
    require(source['eta_lower'] == declaration['eta'] and
            source['model_error_upper'] == declaration['complete_model_error_upper'],
            'source eta/canonical allowance mismatch')
    require(type(source['matrices']) is dict and set(source['matrices']) ==
            {kind + '-' + str(p) for kind in KINDS for p in (0, 1)},
            'missing or extra core matrix descriptor')
    kernel = residual_kernel()
    require(type(declaration['kernel_coefficients']) is list and
            kernel == [rational(x) for x in declaration['kernel_coefficients']] and
            len(kernel) == ORDER + 1 and kernel[1] == SUPPORT ** 2 / 48,
            'native canonical quotient differs from sealed coefficients')
    validate_model_allowance(declaration, kernel)
    edges, weights, kappa = validate_weights(source, declaration)
    polynomials = [rodrigues(n) for n in range(EXTENT)]
    harmonic, harmonic2 = harmonic_tables(EXTENT + 2)
    outputs = residual_outputs(polynomials, kernel)
    kernels = frequency_kernels(edges, weights)
    nodes = [arb.legendre_p_root(N, j, weight=True) for j in range(N)]
    checked, parity_summary = 0, []
    for parity in (0, 1):
        reconstructed = reconstruct(parity, polynomials, outputs, harmonic, harmonic2,
                                    kernels[parity], kappa, nodes)
        counts = {}
        for kind in KINDS:
            counts[kind] = check_matrix(source, source_path.parent, kind, parity,
                                        reconstructed[kind])
            checked += counts[kind]
        if parity == 0 and os.environ.get('T081_NATIVE_CONTROLS'):
            import native_controls_v1
            native_controls_v1.run(sys.modules[__name__], source, source_path.parent, declaration, reconstructed, Path(os.environ['T081_NATIVE_CONTROLS']), source_sha256=digest(source_raw), positive_counts=counts)
        parity_summary.append({'parity': parity, 'dimension': DIM,
                               'first_low_mode': parity, 'last_low_mode': N - 2 + parity,
                               'first_head_mode': N + parity,
                               'last_head_mode': EXTENT - 2 + parity,
                               'matrix_entries': counts,
                               'checked_triangular_entries': sum(counts.values()),
                               'status': 'PASS_NATIVE_CONTAINMENT'})
    require(checked == 512946, 'incomplete core matrix audit')
    return {'format': 't081-complete-gram-source-audit-v1',
            'status': 'PASS_COMPLETE_SOURCE', 'source': str(source_path),
            'inputs': str(inputs_path), 'inputs_sha256': digest(inputs_raw),
            'source_sha256': digest(source_raw), 'producer_sha256': source['producer_sha256'],
            'consumer_sha256': digest(Path(__file__).read_bytes()),
            'target_declaration_sha256': DECLARATION_PIN, 'first_attempt_seal_sha256': SEAL_PIN,
            'support': '81/100', 'N': N, 'order': ORDER, 'physical_extent': EXTENT,
            'independent_precision_bits': ctx.prec, 'publication_bits': BITS,
            'checked_matrix_files': 6, 'checked_triangular_entries': checked,
            'parity_summary': parity_summary,
            'entry_requirement': 'native endpoints contained in inclusive published dyadic endpoints',
            'fresh_arithmetic_fields': ['P_low', 'P_tail', 'VP', 'P_squared', 'GP'],
            'both_translation_windows_evaluated': True,
            'all_combined_2_3_4_5_square_products': True,
            'arithmetic_squared_overlap_cells': 9,
            'active_prime_powers': [m for m, _ in ACTIVE_TERMS],
            'von_mangoldt_prime_bases': [prime for _, prime in ACTIVE_TERMS],
            'both_signed_VP_orientations': True,
            'frequency_anchors': len(edges), 'frequency_exterior_paid': True,
            'physical_exterior_complete': True,
            'ordinary_legendre_masses': '2/(2n+1)',
            'residual_endpoint_boundaries': [-1, 1],
            'R86_exterior_zero': 'polynomial model only: exact endpoint primitive degrees below 1652',
            'true_residual_discrepancy': 'paid by the complete declared canonical model allowance',
            'scalar_premise': 'fresh native supported-form reference qualification and complete physical-tail inverse bound',
            'reference_beta_scope': 'supported quadratic-form bound, not a pointwise multiplier bound',
            'scalar_qualification': qualification,
            'shared_arithmetic_premise': 'python-flint/Arb rigorous arithmetic and Gauss root/weight enclosures',
            'ignored_producer_metadata': sorted(set(source) - required),
            'positivity_checked': False, 'production_admission': False,
            'scope': 'analytic matrix source audit only; no positivity or admission claim'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Exclusive creation is repeated below, protecting against an intervening writer.
    if args.output.exists() or args.output.is_symlink():
        parser.error('refusing to overwrite audit output')
    try:
        result = audit(args.inputs.resolve(), args.source.resolve())
        exit_code = 0
    except Exception as error:
        exit_code = 1 if isinstance(error, (ValueError, KeyError, TypeError, OSError,
                                            OverflowError, EOFError)) else 2
        result = {'format': 't081-complete-gram-source-audit-v1',
                  'status': 'REJECT_COMPLETE_SOURCE', 'error_type': type(error).__name__,
                  'error': str(error), 'source': str(args.source.resolve()),
                  'inputs': str(args.inputs.resolve()), 'independent_precision_bits': 6144,
                  'consumer_sha256': digest(Path(__file__).read_bytes()),
                  'positivity_checked': False, 'production_admission': False,
                  'exit_code': exit_code}
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    try:
        with args.output.open('x', encoding='utf-8', newline='\n') as output:
            output.write(encoded)
    except OSError as error:
        parser.exit(2, 'cannot create fresh audit output: ' + str(error) + '\n')
    print(encoded, end='')
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
