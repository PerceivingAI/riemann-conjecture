"""Independent complete signed-window arithmetic with bounded current-mode tiles."""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb
import hashlib
from time import perf_counter_ns

from flint import arb, arb_poly, ctx, fmpq, fmpq_poly

from scripts.whole_source.artifacts import Axis, ContributionTask, IntervalRecord
from scripts.whole_source.contract import ProblemSpec, canonical_bytes, quantity_document


_TERMS = ((2, 2, 1), (3, 3, 1), (4, 2, 2), (5, 5, 1))


def rodrigues_ratio(n: int) -> fmpq_poly:
    """Construct the complete ordinary Legendre polynomial by integer ratios."""
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative integer degree required")
    coefficients = [0] * (n + 1)
    value = comb(2 * n, n)
    for k in range(n // 2 + 1):
        coefficients[n - 2 * k] = value
        if k < n // 2:
            numerator = -value * (n - 2 * k) * (n - 2 * k - 1)
            denominator = 2 * (k + 1) * (2 * n - 2 * k - 1)
            value, remainder = divmod(numerator, denominator)
            if remainder:
                raise ArithmeticError("nonexact Legendre coefficient ratio")
    return fmpq_poly(coefficients) * fmpq(1, 1 << n)


def _factorials(width: int) -> list[int]:
    result = [1] * width
    for k in range(1, width):
        result[k] = result[k - 1] * k
    return result


def binomial_shift(poly: fmpq_poly, shift: arb, factorials: list[int],
                   width: int | None = None) -> list[arb]:
    """Expand p(x+shift) by a factorial-scaled binomial convolution."""
    n = len(poly) - 1
    width = n + 1 if width is None else width
    if n < 0 or width < n + 1 or len(factorials) < n + 1:
        raise ValueError("complete polynomial and factorial domains required")
    reversed_scaled = arb_poly([arb(poly[k] * factorials[k])
                                for k in range(n, -1, -1)])
    exponential = [arb(1)]
    for k in range(1, n + 1):
        exponential.append(exponential[-1] * shift / k)
    product = reversed_scaled * arb_poly(exponential)
    result = [product[n - j] / factorials[j] for j in range(n + 1)]
    result.extend(arb(0) for _ in range(width - n - 1))
    return result


def power_window_moments(left: arb, right: arb, maximum: int) -> list[arb]:
    """Return one vector of all monomial integrals, including degree maximum."""
    if type(maximum) is not int or maximum < 0:
        raise ValueError("nonnegative maximum moment required")
    lp, rp = arb(1), arb(1)
    moments = []
    for k in range(maximum + 1):
        lp *= left
        rp *= right
        moments.append((rp - lp) / (k + 1))
    return moments


def integrate_window(row: fmpq_poly | arb_poly, shifted: list[arb] | arb_poly,
                     moments: list[arb], *, width: int | None = None) -> arb:
    """Multiply full operands and integrate every coefficient against its moment."""
    width = len(shifted) if width is None else width
    if (not len(row) or not len(shifted) or width < len(shifted) or
            len(moments) < len(row) + width - 1):
        raise ValueError("incomplete polynomial or moment domain")
    native_row = row if isinstance(row, arb_poly) else arb_poly(row)
    native_shift = shifted if isinstance(shifted, arb_poly) else arb_poly(shifted)
    product = native_row * native_shift
    # Native polynomials trim trailing zeros. The declared padded domain remains
    # part of the dot product, including the actual highest input coefficient.
    result = arb(0)
    for k in range(len(row) + width - 1):
        result += product[k] * moments[k]
    if not result.is_finite():
        raise ArithmeticError("nonfinite signed-window integral")
    return result


def _window_parameters(problem: ProblemSpec, term_index: int,
                       window_index: int) -> tuple[arb, arb, arb, arb]:
    if type(term_index) is not int or not 0 <= term_index < len(_TERMS):
        raise ValueError("invalid arithmetic term index")
    if type(window_index) is not int or window_index not in (0, 1):
        raise ValueError("invalid physical window index")
    if tuple((t.m, t.prime, t.exponent) for t in problem.active_terms) != _TERMS:
        raise ValueError("complete selected arithmetic terms required")
    power, prime, _ = _TERMS[term_index]
    support = arb(fmpq(problem.support.numerator, problem.support.denominator))
    tau = arb(power).log() / support
    if not 0 < tau or not tau < 2:
        raise ArithmeticError("arithmetic window outside support")
    coefficient = -arb(prime).log() / arb(power).sqrt()
    if window_index == 0:
        return arb(-1), 1 - tau, tau, coefficient
    return -1 + tau, arb(1), -tau, coefficient


def signed_window_arithmetic(problem: ProblemSpec, m: int, n: int,
                             term_index: int, window_index: int) -> arb:
    """Compute one full ordinary bilinear term/window, without mass division."""
    if (type(m) is not int or type(n) is not int or
            not 0 <= m < problem.M or not 0 <= n < problem.N):
        raise ValueError("physical modes outside the head/low domains")
    with ctx.workprec(problem.arithmetic.audit_bits):
        left, right, shift, coefficient = _window_parameters(problem, term_index, window_index)
        row, column = rodrigues_ratio(m), rodrigues_ratio(n)
        shifted = binomial_shift(column, shift, _factorials(problem.N), problem.N)
        moments = power_window_moments(left, right, problem.M + problem.N - 2)
        return coefficient * integrate_window(row, shifted, moments)


def _fraction(value: arb) -> Fraction:
    rational = value.fmpq()
    return Fraction(int(rational.numerator), int(rational.denominator))

def preparation(problem) -> list[dict]:
    """Independently derive requested coefficients, exact endpoints and L2 masses."""
    degrees = sorted({0, 1, problem.K, problem.K+1, problem.N-problem.K,
                      problem.N-problem.K+1, problem.N-2, problem.N-1, problem.N, problem.N+1,
                      problem.M-2, problem.M-1})
    rows = []
    for degree in degrees:
        poly = rodrigues_ratio(degree)
        digest = hashlib.sha256()
        for coefficient in poly:
            digest.update(canonical_bytes([hex(int(coefficient.numerator)),
                                           hex(int(coefficient.denominator))]))
        square_primitive = (poly*poly).integral()
        mass = square_primitive(1)-square_primitive(-1)
        if mass != fmpq(2, 2*degree+1) or poly(1) != 1 or poly(-1) != (-1)**degree:
            raise ArithmeticError("independent exact endpoint/mass mismatch")
        rows.append({"degree": degree, "coefficients": degree+1,
                     "coefficients_sha256": digest.hexdigest(),
                     "mass": {"numerator": hex(2), "denominator": hex(2*degree+1)},
                     "positive_endpoint": 1, "negative_endpoint": (-1)**degree})
    return rows

def _physical_modes(problem, m: int, n: int, *, low_pair: bool = False) -> None:
    row_limit = problem.N if low_pair else problem.M
    if (type(m) is not int or type(n) is not int or
            not 0 <= m < row_limit or not 0 <= n < problem.N):
        raise ValueError("physical modes outside the declared domains")


@lru_cache(maxsize=8)
def _formal_kernel(numerator: int, denominator: int, order: int) -> tuple[fmpq, ...]:
    """Expand exp(3u/2)/((exp(2u)-1)/(2u)), then remove both polar parts."""
    if type(order) is not int or order < 0:
        raise ValueError("nonnegative complete residual order required")
    factorials = _factorials(order + 3)
    divisor = [fmpq(2**j, factorials[j + 1]) for j in range(order + 2)]
    quotient = [fmpq(1)]
    exponential = fmpq(1)
    for j in range(1, order + 2):
        exponential *= fmpq(3, 2 * j)
        quotient.append(exponential - sum(
            (divisor[k] * quotient[j - k] for k in range(1, j + 1)), fmpq(0)))
    support = fmpq(numerator, denominator)
    scale = support
    coefficients = []
    for degree in range(order + 1):
        regular = quotient[degree + 1] / 2
        if degree % 2 == 0:
            regular -= fmpq(2, 2**degree * factorials[degree])
        coefficients.append(-scale * regular)
        scale *= support
    return tuple(coefficients)


def residual_bilinear(problem, m: int, n: int) -> fmpq:
    """Integrate the complete signed R_K kernel with separate endpoint primitives."""
    _physical_modes(problem, m, n)
    coefficients = _formal_kernel(problem.support.numerator,
                                  problem.support.denominator, problem.K)
    bound = getattr(problem, "kernel_coefficients", None)
    if bound is not None and tuple(
            fmpq(c.numerator, c.denominator) for c in bound) != coefficients:
        raise ArithmeticError("independent complete residual coefficients disagree")
    row = rodrigues_ratio(m)
    lower = rodrigues_ratio(n)
    upper = lower
    image = fmpq_poly()
    factorial = 1
    for degree, coefficient in enumerate(coefficients):
        lower = lower.integral()
        lower -= lower(-1)
        upper = upper.integral()
        upper = upper(1) - upper
        if degree:
            factorial *= degree
        if coefficient:
            image += (lower + upper) * (coefficient * factorial)
    primitive = (row * image).integral()
    return primitive(1) - primitive(-1)


def _potential_integral(poly: fmpq_poly, *, squared: bool = False) -> arb:
    """Contract exact odd-reciprocal beta derivatives before rounding constants."""
    odd_sum, odd_square_sum = fmpq(0), fmpq(0)
    constant, logarithm, log_square, pi_square = (fmpq(0) for _ in range(4))
    for degree in range(0, len(poly), 2):
        odd = degree + 1
        odd_sum += fmpq(1, odd)
        odd_square_sum += fmpq(1, odd * odd)
        weight = poly[degree] / odd
        if squared:
            constant += 2 * weight * (odd_sum * odd_sum + odd_square_sum)
            logarithm -= 4 * weight * odd_sum
            log_square += 2 * weight
            pi_square -= weight / 6
        else:
            constant += 2 * weight * odd_sum
            logarithm -= 2 * weight
    log2 = arb(2).log()
    result = arb(constant) + arb(logarithm) * log2
    if squared:
        result += arb(log_square) * log2 * log2 + arb(pi_square) * arb.pi()**2
    if not result.is_finite():
        raise ArithmeticError("nonfinite independent potential integral")
    return result


def potential_bilinear(m: int, n: int) -> arb:
    """Return the ordinary bilinear integral of V L_m L_n."""
    return _potential_integral(rodrigues_ratio(m) * rodrigues_ratio(n))


def potential_square(m: int, n: int) -> arb:
    """Return the ordinary bilinear integral of V squared L_m L_n."""
    return _potential_integral(rodrigues_ratio(m) * rodrigues_ratio(n), squared=True)


def _potential_moments(maximum: int) -> list[arb]:
    odd_sum = fmpq(0)
    log2 = arb(2).log()
    moments = []
    for degree in range(maximum + 1):
        if degree % 2:
            moments.append(arb(0))
        else:
            odd_sum += fmpq(1, degree + 1)
            moments.append((2 * arb(odd_sum) - 2 * log2) / (degree + 1))
    return moments


def _potential_endpoint_values(x: arb, maximum: int):
    """Yield manual integration-by-parts values, including the finite log limits."""
    minus_endpoint, plus_endpoint = x == 1, x == -1
    if not minus_endpoint and not 0 < 1 - x:
        raise ArithmeticError("uncertified negative logarithm endpoint")
    if not plus_endpoint and not 0 < 1 + x:
        raise ArithmeticError("uncertified positive logarithm endpoint")
    minus_log = arb(0) if minus_endpoint else (1 - x).log()
    plus_log = arb(0) if plus_endpoint else (1 + x).log()
    power, minus_sum, plus_sum = arb(1), arb(0), arb(0)
    harmonic = fmpq(0)
    for degree in range(maximum + 1):
        order = degree + 1
        power *= x
        harmonic += fmpq(1, order)
        term = power / order
        minus_sum += term
        plus_sum = term - plus_sum
        minus = (-arb(harmonic) if minus_endpoint else
                 (power - 1) * minus_log - minus_sum) / order
        plus = (arb(harmonic) * (-1)**degree if plus_endpoint else
                (power - (-1)**order) * plus_log - plus_sum) / order
        yield -(minus + plus) / 2


def _potential_window_moments(left: arb, right: arb, maximum: int) -> list[arb]:
    if not left < right or not left >= -1 or not right <= 1:
        raise ArithmeticError("uncertified logarithmic window")
    return [b - a for a, b in zip(_potential_endpoint_values(left, maximum),
                                 _potential_endpoint_values(right, maximum))]


def _gram_windows(problem) -> list[tuple[arb, arb, arb, arb]]:
    """Enumerate both signed physical windows for every declared prime power."""
    support = arb(fmpq(problem.support.numerator, problem.support.denominator))
    windows = []
    for term in problem.active_terms:
        tau = arb(term.m).log() / support
        if not 0 < tau or not tau < 2:
            raise ArithmeticError("arithmetic window outside support")
        coefficient = -arb(term.prime).log() / arb(term.m).sqrt()
        windows.append((arb(-1), 1 - tau, tau, coefficient))
        windows.append((-1 + tau, arb(1), -tau, coefficient))
    return windows


def ordered_vp(problem, m: int, n: int) -> arb:
    """Integrate V L_m P L_n without exchanging the ordered factors."""
    _physical_modes(problem, m, n)
    row, column = rodrigues_ratio(m), rodrigues_ratio(n)
    factorials = _factorials(n + 1)
    value = arb(0)
    for left, right, shift, coefficient in _gram_windows(problem):
        shifted = binomial_shift(column, shift, factorials)
        moments = _potential_window_moments(left, right, m + n)
        value += coefficient * integrate_window(row, shifted, moments)
    if not value.is_finite():
        raise ArithmeticError("nonfinite ordered potential/arithmetic integral")
    return value


def _strict_cells(windows: list[tuple[arb, arb, arb, arb]]):
    boundaries = [arb(-1), arb(1)]
    for index in range(0, len(windows), 2):
        boundaries.extend((windows[index][1], windows[index + 1][0]))
    boundaries.sort()
    for left, right in zip(boundaries, boundaries[1:]):
        if not left < right:
            raise ArithmeticError("arithmetic breakpoints are not strictly separated")
        center = (left + right) / 2
        active = []
        for index, (start, end, _, _) in enumerate(windows):
            if start < center and center < end:
                active.append(index)
            elif not center < start and not end < center:
                raise ArithmeticError("uncertified arithmetic cell activity")
        yield left, right, active


def _endpoint_integral(poly: arb_poly, left: arb, right: arb) -> arb:
    primitive = poly.integral()
    return primitive(right) - primitive(left)


def combined_square_entry(problem, m: int, n: int) -> arb:
    """Integrate full signed combined images on every strict overlap cell."""
    _physical_modes(problem, m, n, low_pair=True)
    windows = _gram_windows(problem)
    left_basis, right_basis = rodrigues_ratio(m), rodrigues_ratio(n)
    factorials = _factorials(max(m, n) + 1)
    left_images = [arb_poly(binomial_shift(left_basis, shift, factorials)) * coefficient
                   for _, _, shift, coefficient in windows]
    right_images = left_images if m == n else [
        arb_poly(binomial_shift(right_basis, shift, factorials)) * coefficient
        for _, _, shift, coefficient in windows]
    value = arb(0)
    for left, right, active in _strict_cells(windows):
        combined_left, combined_right = arb_poly(), arb_poly()
        for index in active:
            combined_left += left_images[index]
            combined_right += right_images[index]
        value += _endpoint_integral(combined_left * combined_right, left, right)
    if not value.is_finite():
        raise ArithmeticError("nonfinite combined arithmetic square")
    return value


def operator_column(problem, n: int) -> list[arb]:
    """Return all same-parity physical F=V+P bilinears, without mass division."""
    _physical_modes(problem, n, n)
    column = rodrigues_ratio(n)
    native_column = arb_poly(column)
    factorials = _factorials(n + 1)
    windows = [(left, right, arb_poly(binomial_shift(column, shift, factorials)) * coefficient)
               for left, right, shift, coefficient in _gram_windows(problem)]
    moments = _potential_moments(problem.M + n - 1)
    result = []
    for m in range(n % 2, problem.M, 2):
        row = arb_poly(rodrigues_ratio(m))
        product = row * native_column
        value = sum((product[k] * moments[k] for k in range(len(product))), arb(0))
        for left, right, shifted in windows:
            value += _endpoint_integral(row * shifted, left, right)
        if not value.is_finite():
            raise ArithmeticError("nonfinite full physical operator column")
        result.append(value)
    return result


def tile_account(problem, rows, columns):
    """Price the independent current images and all live physical columns."""
    from scripts.whole_source import execution
    from scripts.whole_source.pipeline import _analytic_tile_requirements
    account = _analytic_tile_requirements(problem, rows, columns, precision_bits=ctx.prec)
    worker = execution._WORKER
    private_limit = worker[0].worker_private_mib if worker else 128
    native_limit = worker[0].native_workspace_mib if worker else 128
    if account["private_bytes"] > private_limit*1024**2 or account["native_bytes"] > native_limit*1024**2:
        raise MemoryError("independent tile exceeds declared private/native allowance")
    return account


def _residual_image(problem, n):
    """Construct one independent full endpoint image, not one image per pair."""
    coefficients = _formal_kernel(problem.support.numerator,
                                  problem.support.denominator, problem.K)
    bound = getattr(problem, "kernel_coefficients", None)
    if bound is not None and tuple(
            fmpq(c.numerator, c.denominator) for c in bound) != coefficients:
        raise ArithmeticError("independent complete residual coefficients disagree")
    lower = rodrigues_ratio(n)
    upper, image, factorial = lower, fmpq_poly(), 1
    for degree, coefficient in enumerate(coefficients):
        lower = lower.integral()
        lower -= lower(-1)
        upper = upper.integral()
        upper = upper(1)-upper
        if degree:
            factorial *= degree
        if coefficient:
            image += (lower+upper)*(coefficient*factorial)
    return image


def assemble_tile(problem, rows, columns, full_F_columns):
    """Independently assemble complete upper entries with current-mode images."""
    from flint import arb_mat
    rows, columns = tuple(rows), tuple(columns)
    tile_account(problem, rows, columns)
    modes = sorted(set(rows) | set(columns))
    if any(len(full_F_columns[n]) != len(range(n % 2, problem.M, 2)) for n in modes):
        raise ValueError("complete physical F columns required")
    pairs = [(m, n) for m in rows for n in columns if m <= n]
    bases = {n: rodrigues_ratio(n) for n in modes}
    factorials = _factorials(max(modes)+1)
    windows = _gram_windows(problem)
    square = {pair: arb(0) for pair in pairs}
    for left, right, active in _strict_cells(windows):
        combined = {n: arb_poly() for n in modes}
        for index in active:
            _, _, shift, coefficient = windows[index]
            for n in modes:
                # Shift temporary dies here; no eight-window image inventory.
                combined[n] += arb_poly(binomial_shift(
                    bases[n], shift, factorials))*coefficient
        for m, n in pairs:
            square[m, n] += _endpoint_integral(combined[m]*combined[n], left, right)
        del combined
    ordered = set(pairs) | {(n, m) for m, n in pairs}
    vp = {pair: arb(0) for pair in ordered}
    maximum = 2*max(modes)
    for left, right, shift, coefficient in windows:
        moments = _potential_window_moments(left, right, maximum)
        shifted = {n: arb_poly(binomial_shift(bases[n], shift, factorials)) for n in modes}
        for m in modes:
            row = arb_poly(bases[m])
            for n in modes:
                if (m, n) in ordered:
                    product = row*shifted[n]
                    vp[m, n] += coefficient*sum(
                        (product[k]*moments[k] for k in range(len(product))), arb(0))
        del shifted, moments
    # Exact beta derivatives are contracted before rounding the constants.
    beta = []
    odd_sum, odd_square = fmpq(0), fmpq(0)
    for degree in range(0, maximum+1, 2):
        odd = degree+1
        odd_sum += fmpq(1, odd)
        odd_square += fmpq(1, odd*odd)
        beta.append((2*(odd_sum*odd_sum+odd_square)/odd,
                     -4*odd_sum/odd, fmpq(2, odd), fmpq(-1, 6*odd),
                     2*odd_sum/odd, fmpq(-2, odd)))
    log2, pi_square = arb(2).log(), arb.pi()**2
    physical = range(modes[0] % 2, problem.M, 2)
    projection = arb_mat([[full_F_columns[m][k//2] for k in physical] for m in rows])*arb_mat(
        [[full_F_columns[n][k//2]*fmpq(2*k+1, 2) for n in columns] for k in physical])
    result = {}
    for n in columns:
        image = _residual_image(problem, n)
        for m in rows:
            if m > n:
                continue
            product = bases[m]*bases[n]
            sums = [fmpq(0) for _ in range(6)]
            for k in range(0, len(product), 2):
                for j, value in enumerate(beta[k//2]):
                    sums[j] += product[k]*value
            vv = arb(sums[0])+arb(sums[1])*log2+arb(sums[2])*log2**2+arb(sums[3])*pi_square
            v = arb(sums[4])+arb(sums[5])*log2
            primitive = (bases[m]*image).integral()
            residual = primitive(1)-primitive(-1)
            result[m, n] = assemble_entry(problem, m, n, full_F_columns, _parts=(
                v, vv, square[m, n], vp[m, n], vp[n, m], residual),
                _projection=projection[rows.index(m), columns.index(n)])
        del image
    return result


def assemble_entry(problem, m: int, n: int,
                   columns: dict[int, list[arb]], *, _parts=None,
                   _projection=None) -> dict[tuple[str, int, int], arb]:
    """Assemble one selected low entry and the full physical exterior projection."""
    _physical_modes(problem, m, n, low_pair=True)
    if m % 2 != n % 2:
        raise ValueError("same-parity Gram entry required")
    left, right = columns[m], columns[n]
    physical = range(n % 2, problem.M, 2)
    if len(left) != len(physical) or len(right) != len(physical):
        raise ValueError("complete same-role physical columns required")
    if _parts is None:
        v = potential_bilinear(m, n)
        vv = potential_square(m, n)
        p2 = combined_square_entry(problem, m, n)
        vp = ordered_vp(problem, m, n)
        reverse_vp = vp if m == n else ordered_vp(problem, n, m)
        residual = residual_bilinear(problem, m, n)
    else:
        v, vv, p2, vp, reverse_vp, residual = _parts
    joint = vv + p2 + vp + reverse_vp
    f = right[m // 2]
    actual = f + arb(residual)
    if m == n:
        harmonic = sum((fmpq(1, k) for k in range(1, m + 1)), fmpq(0))
        support = arb(fmpq(problem.support.numerator, problem.support.denominator))
        actual += arb(fmpq(2, 2 * m + 1)) * (
            arb(harmonic) - arb.const_euler() - (2 * arb.pi() * support).log())
    if _projection is None:
        _projection = arb(0)
        for k in physical:
            _projection += left[k // 2] * right[k // 2] * fmpq(2 * k + 1, 2)
    exterior = joint - _projection
    kappa = arb(fmpq(problem.kappa.numerator, problem.kappa.denominator))
    result = {
        ("V", m, n): v, ("VV", m, n): vv, ("P_squared", m, n): p2,
        ("VP", m, n): vp, ("J_F", m, n): joint, ("P_L", m, n): f - v,
        ("A_model", m, n): actual, ("G_exterior", m, n): exterior,
        ("weighted_complete_tail", m, n): kappa * exterior,
    }
    if m != n:
        result[("VP", n, m)] = reverse_vp
    if any(not value.is_finite() for value in result.values()):
        raise ArithmeticError("nonfinite independent selected Gram entry")
    return result


def frequency_anchor(problem, omega: Fraction):
    """Return ordinary bilinears for the complete projector [-omega, omega]."""
    if not isinstance(omega, Fraction) or omega < 0:
        raise ValueError("nonnegative exact frequency required")
    if omega:
        c = arb(fmpq(problem.support.numerator, problem.support.denominator) *
                fmpq(omega.numerator, omega.denominator))
        sine, cosine = c.sin(), c.cos()
        js = [sine / c, (sine - c * cosine) / (c * c)]
        for n in range(1, problem.M + 1):
            js.append((2 * n + 1) / c * js[-1] - js[-2])
        twice_c = 2 * c
        integrals = [twice_c.si() + (twice_c.cos() - 1) / twice_c]
        for n in range(1, problem.M):
            integrals.append(integrals[-1] - c * (js[n - 1]**2 + js[n]**2))
        scale = 4 / arb.pi()

    def entry(m: int, n: int) -> arb:
        if (type(m) is not int or type(n) is not int or
                not 0 <= m < problem.M or not 0 <= n < problem.M or m % 2 != n % 2):
            raise ValueError("same-parity physical frequency modes required")
        if not omega:
            return arb(0)
        if m == n:
            value = scale * integrals[n] / (2 * n + 1)
        else:
            if m > n:
                m, n = n, m
            derivative_m = m / c * js[m] - js[m + 1]
            derivative_n = n / c * js[n] - js[n + 1]
            sign = -1 if ((m - n) // 2) % 2 else 1
            value = (scale * sign * c**2 *
                     (derivative_n * js[m] - derivative_m * js[n]) /
                     (n * (n + 1) - m * (m + 1)))
        if not value.is_finite():
            raise ArithmeticError("nonfinite independent frequency projector")
        return value

    return entry


def frequency_step(problem, anchor: int):
    """Independently form a weighted frequency term, including full exterior mass."""
    if type(anchor) is not int or not 0 <= anchor < len(problem.frequency_edges):
        raise ValueError("invalid independent frequency anchor")
    if anchor == 0:
        terminal = problem.inverse_weights[-1]
        terminal = fmpq(terminal.numerator, terminal.denominator)
        def mass(m, n):
            return arb(terminal*fmpq(2, 2*n+1)) if m == n else arb(0)
        return mass
    compact = frequency_anchor(problem, problem.frequency_edges[anchor])
    left, right = problem.inverse_weights[anchor-1:anchor+1]
    jump = fmpq(left.numerator, left.denominator)-fmpq(right.numerator, right.denominator)
    return lambda m, n: compact(m, n)*jump


def head_column(problem, n: int, full_column: list[arb]) -> list[arb]:
    """Convert full F bilinears plus residuals to head expansion coefficients."""
    _physical_modes(problem, n, n)
    parity = n % 2
    if len(full_column) != len(range(parity, problem.M, 2)):
        raise ValueError("complete same-parity physical column required")
    if any(not isinstance(value, arb) or not value.is_finite() for value in full_column):
        raise ValueError("finite physical column required")
    result = []
    image = _residual_image(problem, n)
    for k in range(problem.N + parity, problem.M, 2):
        primitive = (rodrigues_ratio(k) * image).integral()
        residual = primitive(1) - primitive(-1)
        value = ((full_column[k // 2] + arb(residual)) *
                 fmpq(2 * k + 1, 2))
        if not value.is_finite():
            raise ArithmeticError("nonfinite independent head coefficient")
        result.append(value)
    return result


def head_image(problem, column: list[arb], tiles) -> list[arb]:
    """Multiply symmetric head tiles by C, including both off-diagonal images."""
    width = (problem.M - problem.N) // 2
    if len(column) != width:
        raise ValueError("complete head column required")
    if any(not isinstance(value, arb) or not value.is_finite() for value in column):
        raise ValueError("finite head column required")
    image = [arb(0) for _ in range(width)]
    parity = None
    for tile in tiles:
        for i, j, value in tile:
            if (type(i) is not int or type(j) is not int or
                    not problem.N <= i <= j < problem.M or i % 2 != j % 2 or
                    not isinstance(value, arb) or not value.is_finite()):
                raise ValueError("finite upper same-parity physical head entry required")
            if parity is None:
                parity = i % 2
            elif i % 2 != parity:
                raise ValueError("one physical head parity required")
            row = (i - problem.N - parity) // 2
            col = (j - problem.N - parity) // 2
            if not 0 <= row < width or not 0 <= col < width:
                raise ValueError("physical head entry outside column domain")
            image[row] += value * column[col]
            if row != col:
                image[col] += value * column[row]
    if any(not value.is_finite() for value in image):
        raise ArithmeticError("nonfinite independent head image")
    return image


def head_pair(problem, left: list[arb], image: list[arb]) -> arb:
    """Contract the complete head expansion against a complete kernel image."""
    width = (problem.M - problem.N) // 2
    if len(left) != width or len(image) != width:
        raise ValueError("complete head contraction columns required")
    value = arb(0)
    for k in range(width):
        if (not isinstance(left[k], arb) or not isinstance(image[k], arb) or
                not left[k].is_finite() or not image[k].is_finite()):
            raise ValueError("finite head contraction columns required")
        value += left[k] * image[k]
    if not value.is_finite():
        raise ArithmeticError("nonfinite independent head contraction")
    return value


def evaluate_source(task: dict, staging) -> dict:
    """Enter the neutral source coordinator only through the owned analytic role."""
    from scripts.whole_source import execution

    worker = execution._WORKER
    if worker is None or worker[-1] is not staging:
        raise RuntimeError("analytic source evaluation requires an owned worker")
    plan = worker[0]
    spec = staging.spec
    problem = spec.problem
    if (plan.role != "analytic" or spec.role != "analytic" or
            ctx.prec != problem.arithmetic.audit_bits or
            ctx.prec != plan.precision_bits or ctx.threads != spec.native_threads):
        raise RuntimeError("analytic source native policy differs from owned worker")
    staging._check()
    from scripts.whole_source.pipeline import evaluate_owned

    return evaluate_owned(task, staging, {
        "column": operator_column, "entry": assemble_entry, "tile": assemble_tile,
        "tile_account": tile_account, "frequency_step": frequency_step,
        "head_column": head_column, "head_image": head_image, "head_pair": head_pair,
    })


def evaluate_gram(task: dict, staging) -> dict:
    """Enter the neutral Gram coordinator only through the owned analytic role."""
    from scripts.whole_source import execution

    worker = execution._WORKER
    if worker is None or worker[-1] is not staging:
        raise RuntimeError("analytic Gram evaluation requires an owned worker")
    plan = worker[0]
    spec = staging.spec
    problem = spec.problem
    if (plan.role != "analytic" or spec.role != "analytic" or
            ctx.prec != problem.arithmetic.audit_bits or
            ctx.prec != plan.precision_bits or ctx.threads != spec.native_threads):
        raise RuntimeError("analytic Gram native policy differs from owned worker")
    staging._check()
    from scripts.whole_source.gram import evaluate_owned

    return evaluate_owned(task, staging, {
        "column": operator_column, "residual": residual_bilinear,
        "potential": potential_bilinear, "potential_square": potential_square,
        "vp": ordered_vp, "square": combined_square_entry, "entry": assemble_entry,
    })




def evaluate(task: dict, staging) -> dict:
    """Stage complete selected term/windows inside the owned analytic worker."""
    from scripts.whole_source import execution

    worker = execution._WORKER
    if worker is None or worker[-1] is not staging:
        raise RuntimeError("signed arithmetic requires an owned worker")
    plan = worker[0]
    spec = staging.spec
    problem = spec.problem
    if (plan.role != "analytic" or spec.role != "analytic" or
            ctx.prec != problem.arithmetic.audit_bits or
            ctx.prec != plan.precision_bits or ctx.threads != spec.native_threads):
        raise RuntimeError("analytic native arithmetic policy differs from owned worker")
    if task.get("operation") == "preparation":
        return {"preparation": preparation(problem), "scope": "SELECTION_ONLY"}
    if type(task) is not dict or task.get("operation") != "window":
        raise ValueError("signed-window worker task required")
    term_index, window_index = task.get("term_index"), task.get("window_index")
    started = perf_counter_ns()
    left, right, shift, coefficient = _window_parameters(problem, term_index, window_index)
    expected = ((0, 0), (1, 1), (problem.N, problem.N - 2),
                (problem.N + 1, problem.N - 1),
                (problem.M - 2, problem.N - 2), (problem.M - 1, problem.N - 1))
    if len(spec.quantities) != len(expected) or {q.key.entry for q in spec.quantities} != set(expected):
        raise ValueError("complete six-entry arithmetic selection required")
    for quantity in spec.quantities:
        m, n = quantity.key.entry
        expected_name = "P_L" if m < problem.N else "P_H"
        if (quantity.key.name != expected_name or quantity.key.parity != m % 2 or m % 2 != n % 2 or
                tuple(quantity.rows) != (m,) or tuple(quantity.columns) != (n,) or
                quantity.symmetric_upper != (m < problem.N and m == n) or
                quantity.axes != (Axis("term", 0, 4), Axis("window", 0, 2))):
            raise ValueError("selected entry differs from physical arithmetic domain")
    staging._check()
    degrees = {degree for pair in expected for degree in pair}
    exact = {degree: rodrigues_ratio(degree) for degree in sorted(degrees)}
    rows = {m: arb_poly(exact[m]) for m, _ in expected}
    factorials = _factorials(problem.N)
    moments = power_window_moments(left, right, problem.M + problem.N - 2)
    setup_ns = perf_counter_ns() - started
    shifted = {}
    chunks = []
    shift_ns = 0
    full_term_ns = 0
    for quantity in spec.quantities:
        m, n = quantity.key.entry
        if n not in shifted:
            before = perf_counter_ns()
            shifted[n] = arb_poly(binomial_shift(exact[n], shift, factorials, problem.N))
            shift_ns += perf_counter_ns() - before
        before = perf_counter_ns()
        value = coefficient * integrate_window(rows[m], shifted[n], moments, width=problem.N)
        full_term_ns += perf_counter_ns() - before
        if not value.is_finite():
            raise ArithmeticError("nonfinite selected arithmetic contribution")
        domain = ContributionTask(quantity.key, quantity.rows, quantity.columns,
                                  (Axis("term", term_index, term_index + 1),
                                   Axis("window", window_index, window_index + 1)))
        record = IntervalRecord(m, n, (term_index, window_index),
                                _fraction(value.lower()), _fraction(value.upper()))
        staged = staging.stage_chunk(domain, (record,))
        wire = domain.to_dict()
        wire["quantity"] = quantity_document(quantity.key)
        chunks.append({"task": wire, "path": str(staged.path),
                       "ref": {"path": staged.ref.path, "sha256": staged.ref.sha256,
                               "size": staged.ref.size},
                       "generation": staged.generation, "attempt_id": staged.attempt_id})
    return {"chunks": chunks, "scope": "SELECTION_ONLY", "statistics": {
        "native_precision_bits": ctx.prec, "native_threads": ctx.threads,
        "basis_rows_constructed": len(exact), "basis_rows_reused": 2 * len(expected) - len(exact),
        "exact_ratio_divisions": sum(degree // 2 for degree in degrees),
        "factorial_positions": len(factorials), "moment_vectors": 1, "moment_positions": len(moments),
        "low_power_positions": problem.N, "shift_convolutions": len(shifted),
        "shift_rows_reused": len(expected) - len(shifted), "full_term_window_count": len(chunks),
        "coefficient_products": len(chunks), "records_staged": len(chunks),
        "setup_ns": setup_ns, "shift_ns": shift_ns, "full_term_ns": full_term_ns,
        "wall_ns": perf_counter_ns() - started}}
