"""Complete selected arithmetic entries by streamed certified Gauss recurrence."""
from __future__ import annotations

from dataclasses import asdict
from fractions import Fraction
import hashlib
from time import perf_counter_ns

from flint import arb, ctx, fmpq, fmpq_poly

from scripts.whole_source.artifacts import (
    Axis, ContributionTask, IntervalRecord, qualification_barrier,
)
from scripts.whole_source.contract import canonical_bytes

_GAUSS_BATCH = None


def _gauss_batch(order, start, stop):
    """Retain at most one declared node batch, keyed by the native policy."""
    global _GAUSS_BATCH
    key = (order, start, stop, ctx.prec, ctx.threads)
    if _GAUSS_BATCH is not None and _GAUSS_BATCH[0] == key:
        return _GAUSS_BATCH[1], True
    _GAUSS_BATCH = None
    values = tuple(arb.legendre_p_root(order, index, weight=True) for index in range(start, stop))
    _GAUSS_BATCH = key, values
    return values, False


def _width_exponent(width):
    if not width:
        return None
    numerator, denominator = width.numerator, width.denominator
    exponent = numerator.bit_length()-denominator.bit_length()
    above = numerator > denominator << exponent if exponent >= 0 else numerator << -exponent > denominator
    return exponent+int(above)


def basis(n: int) -> fmpq_poly:
    """Construct only a requested exact ordinary Legendre row."""
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative physical degree required")
    return fmpq_poly.legendre_p(n)


def legendre_values(x: arb, count: int) -> list[arb]:
    if type(count) is not int or count < 1:
        raise ValueError("positive recurrence extent required")
    values = [arb(1)]
    if count > 1:
        values.append(x)
    for n in range(1, count - 1):
        values.append(((2*n+1)*x*values[-1] - n*values[-2])/(n+1))
    return values


def _fraction(value: arb) -> Fraction:
    q = value.fmpq()
    return Fraction(int(q.numerator), int(q.denominator))


def _coefficient_fingerprint(poly) -> str:
    digest = hashlib.sha256()
    for coefficient in poly:
        digest.update(canonical_bytes([hex(int(coefficient.numerator)),
                                       hex(int(coefficient.denominator))]))
    return digest.hexdigest()


def preparation(problem) -> list[dict]:
    """Exact endpoint/mass witnesses for requested low, band and terminal modes."""
    degrees = sorted({0, 1, problem.K, problem.K+1, problem.N-problem.K,
                      problem.N-problem.K+1, problem.N-2, problem.N-1, problem.N, problem.N+1,
                      problem.M-2, problem.M-1})
    result = []
    for degree in degrees:
        poly = basis(degree)
        primitive = (poly*poly).integral()
        mass = fmpq(2, 2*degree+1)
        if poly(1) != 1 or poly(-1) != (-1)**degree or primitive(1)-primitive(-1) != mass:
            raise ArithmeticError("exact basis endpoint or physical mass mismatch")
        result.append({"degree": degree, "coefficients": degree+1,
                       "coefficients_sha256": _coefficient_fingerprint(poly),
                       "mass": {"numerator": hex(2), "denominator": hex(2*degree+1)},
                       "positive_endpoint": 1, "negative_endpoint": (-1)**degree})
    return result


def linear_arithmetic(problem, pairs, term_index, window_index, start, stop, *, statistics=None,
                      native_started=None):
    """Evaluate every prescribed node in one ragged block; no reflected doubling."""
    if (type(term_index) is not int or not 0 <= term_index < len(problem.active_terms) or
            type(window_index) is not int or window_index not in (0, 1) or
            type(start) is not int or type(stop) is not int or
            not 0 <= start < stop <= problem.source_gauss_order):
        raise ValueError("incomplete or invalid Gauss block")
    if tuple((term.m, term.prime) for term in problem.active_terms) != ((2, 2), (3, 3), (4, 2), (5, 5)):
        raise ValueError("retained arithmetic active set required")
    term = problem.active_terms[term_index]
    tau = arb(term.m).log()/arb(fmpq(problem.support.numerator, problem.support.denominator))
    coefficient = -arb(term.prime).log()/arb(term.m).sqrt()
    half = 1-tau/2
    if not half > 0:
        raise ArithmeticError("unresolved arithmetic window")
    midpoint = (-1 if window_index == 0 else 1)*tau/2
    shift = tau if window_index == 0 else -tau
    records = [[] for _ in pairs]
    nodes, reused = _gauss_batch(problem.source_gauss_order, start, stop)
    maximum_width = None
    if native_started is not None:
        native_started()
    for index, (node, weight) in enumerate(nodes, start):
        x = midpoint+half*node
        rows = legendre_values(x, problem.M)
        columns = legendre_values(x+shift, problem.N)
        factor = coefficient*half*weight
        for out, (m, n) in zip(records, pairs):
            value = rows[m]*columns[n]*factor
            if not value.is_finite():
                raise ArithmeticError("nonfinite complete-node contribution")
            lower, upper = _fraction(value.lower()), _fraction(value.upper())
            exponent = _width_exponent(upper-lower)
            if exponent is not None:
                maximum_width = exponent if maximum_width is None else max(maximum_width, exponent)
            out.append(IntervalRecord(m, n, (term_index, window_index, index), lower, upper))
    if statistics is not None:
        statistics.update(gauss_batch_nodes=len(nodes), gauss_batch_reused=reused,
                          gauss_roots_constructed=0 if reused else len(nodes),
                          native_interval_width_upper_power2=maximum_width)
    return records


def evaluate(task: dict, staging) -> dict:
    from scripts.whole_source import execution
    worker = execution._WORKER
    if worker is None or worker[-1] is not staging:
        raise RuntimeError("Gauss arithmetic requires an owned worker")
    plan, problem = worker[0], staging.spec.problem
    if (plan.role != "producer" or staging.spec.role != "producer" or
            ctx.prec != problem.arithmetic.source_bits or ctx.prec != plan.precision_bits or
            ctx.threads != staging.spec.native_threads):
        raise RuntimeError("producer native policy differs from owned worker")
    if task.get("operation") == "preparation":
        return {"preparation": preparation(problem), "scope": "SELECTION_ONLY"}
    if task.get("operation") != "nodes":
        raise ValueError("Gauss node-block task required")
    pairs = tuple(q.key.entry for q in staging.spec.quantities)
    expected = ((0, 0), (1, 1), (problem.N, problem.N-2), (problem.N+1, problem.N-1),
                (problem.M-2, problem.N-2), (problem.M-1, problem.N-1))
    if pairs != expected or problem.profile != "retained-t081":
        raise ValueError("complete retained six-entry selection required")
    term, window = task["term_index"], task["window_index"]
    start, stop = task["node_start"], task["node_stop"]
    started = perf_counter_ns()
    counters = {}
    records = linear_arithmetic(problem, pairs, term, window, start, stop, statistics=counters,
        native_started=lambda: qualification_barrier(staging.root, staging.attempt_id, "native-running"))
    evaluated = perf_counter_ns()
    chunks = []
    for quantity, values in zip(staging.spec.quantities, records):
        domain = ContributionTask(quantity.key, quantity.rows, quantity.columns,
                                  (Axis("term", term, term+1), Axis("window", window, window+1),
                                   Axis("node", start, stop)))
        staged = staging.stage_chunk(domain, values)
        chunks.append({"task": domain.to_dict(), "path": str(staged.path), "ref": asdict(staged.ref),
                       "generation": staged.generation, "attempt_id": staged.attempt_id})
    return {"chunks": chunks, "scope": "SELECTION_ONLY", "statistics": {
        "native_precision_bits": ctx.prec, "native_threads": ctx.threads,
        "node_start": start, "node_stop": stop, "gauss_order": problem.source_gauss_order,
        "full_low_recurrence_positions": problem.N, "output_recurrence_positions": problem.M,
        "signed_window": window, "prime_power": problem.active_terms[term].m,
        "records_staged": (stop-start)*len(pairs), "node_pairs_evaluated": stop-start,
        "native_to_exact_endpoint_transitions": 2*(stop-start)*len(pairs),
        **counters,
        "evaluate_ns": evaluated-started, "wall_ns": perf_counter_ns()-started}}


def _harmonics(maximum):
    first, second = [fmpq(0)], [fmpq(0)]
    for k in range(1, maximum+1):
        first.append(first[-1]+fmpq(1, k))
        second.append(second[-1]+fmpq(1, k*k))
    return first, second


def potential_bilinear(m, n):
    """Ordinary bilinear logarithmic potential, including its diagonal."""
    if (m-n) % 2:
        return arb(0)
    if m != n:
        return arb(fmpq(2, abs(m-n)*(m+n+1)))
    harmonic, _ = _harmonics(2*n)
    return arb(fmpq(2, 2*n+1))*(2*arb(harmonic[2*n])-2*arb(harmonic[n])
                                  +arb(fmpq(1, 2*n+1))-arb.const_log2())


def residual_bilinear(problem, m, n):
    """Full finite residual: low endpoint polynomial or sparse primitive walk."""
    import math
    if (m-n) % 2 or m > n+problem.K+1:
        return fmpq(0)
    coefficients = [fmpq(c.numerator, c.denominator) for c in problem.kernel_coefficients]
    if n > problem.K:
        current, answer = {n: fmpq(1)}, fmpq(0)
        for step in range(1, problem.K+1):
            following = {}
            for degree, value in current.items():
                value /= 2*degree+1
                following[degree+1] = following.get(degree+1, fmpq(0))+value
                following[degree-1] = following.get(degree-1, fmpq(0))-value
            current = following
            if step % 2 == 0:
                answer += 2*math.factorial(step-1)*coefficients[step-1]*current.get(m, fmpq(0))
        return answer*fmpq(2, 2*m+1)
    polynomial = basis(n)
    moments = [sum((polynomial[k]*fmpq(2, k+j+1)
                    for k in range(len(polynomial)) if (k+j) % 2 == 0), fmpq(0))
               for j in range(problem.K+1)]
    halves = [sum((polynomial[k]/(k+j+1) for k in range(len(polynomial))), fmpq(0))
              for j in range(problem.K+1)]
    image = fmpq_poly([0])
    for d, coefficient in enumerate(coefficients):
        boundary = [fmpq(0)]*(d+1)
        if d % 2 == 0:
            for j in range(d+1):
                boundary[d-j] = coefficient*((-1)**j)*math.comb(d, j)*moments[j]
        else:
            primitive = polynomial
            for _ in range(d+1):
                primitive = primitive.integral()
            image += primitive*(2*math.factorial(d)*coefficient)
            for j in range(d+1):
                boundary[d-j] = coefficient*math.comb(d, j)*(
                    (-1)**n-(-1)**j)*halves[j]
        image += fmpq_poly(boundary)
    integral = (basis(m)*image).integral()
    return integral(1)-integral(-1)


def potential_square(m, n):
    """Complete log-squared integral; no finite-output approximation."""
    if (m-n) % 2:
        return arb(0)
    product = basis(m)*basis(n)
    harmonic, second = _harmonics(len(product)+1)
    total = arb(0)
    for k in range(0, len(product), 2):
        if not product[k]:
            continue
        r = k//2
        mean = 2*arb.const_log2()-2*arb(harmonic[2*r+2])+arb(harmonic[r+1])
        variance = -arb.pi()**2/3+4*arb(second[2*r+2])-arb(second[r+1])
        total += arb(product[k])*(mean*mean+variance)/(2*(2*r+1))
    return total


def _log_moments(left, right, maximum):
    """Complete endpoint limits and power-vector logarithmic primitives."""
    def primitives(x):
        if x == 1:
            harmonic, _ = _harmonics(maximum+1)
            return [-arb(harmonic[k+1])/(k+1) for k in range(maximum+1)]
        if not x < 1:
            raise ArithmeticError("unresolved logarithmic endpoint")
        logarithm = (1-x).log()
        power, partial, result = arb(1), arb(0), []
        for k in range(maximum+1):
            power *= x
            partial += power/(k+1)
            result.append(((power-1)*logarithm-partial)/(k+1))
        return result
    la, lb, ra, rb = primitives(left), primitives(right), primitives(-right), primitives(-left)
    return [-(lb[k]-la[k]+(-1)**k*(rb[k]-ra[k]))/2 for k in range(maximum+1)]


def _terms(problem):
    if not problem.active_terms:
        raise ValueError("active arithmetic terms required")
    support = arb(fmpq(problem.support.numerator, problem.support.denominator))
    result = []
    for term in problem.active_terms:
        shift = arb(term.m).log()/support
        if not 0 < shift < 2:
            raise ArithmeticError("unresolved active arithmetic support")
        result.append((shift, arb(term.prime).log()/arb(term.m).sqrt()))
    return result


def ordered_vp(problem, m, n):
    """Ordered int V L_m P L_n; both signed windows, no symmetry shortcut."""
    from flint import arb_poly
    row, column = basis(m), basis(n)
    total = arb(0)
    for tau, coefficient in _terms(problem):
        for left, right, shift in ((arb(-1), 1-tau, tau), (-1+tau, arb(1), -tau)):
            shifted = arb_poly(column)(arb_poly([shift, 1]))
            product = arb_poly(row)*shifted
            moments = _log_moments(left, right, m+n)
            total -= coefficient*sum((product[k]*moments[k] for k in range(m+n+1)), arb(0))
    return total


_GRAM_RULE = None


def _gram_rule(order):
    """One role-local rule vector, never node-by-mode tables for all cells."""
    global _GRAM_RULE
    key = order, ctx.prec, ctx.threads
    if _GRAM_RULE is None or _GRAM_RULE[0] != key:
        _GRAM_RULE = None
        _GRAM_RULE = key, tuple(arb.legendre_p_root(order, i, weight=True) for i in range(order))
    return _GRAM_RULE[1]


def combined_square_entry(problem, m, n):
    """Integrate complete combined signed images on every strict overlap cell."""
    terms = _terms(problem)
    points = [arb(-1), arb(1)]
    for tau, _ in terms:
        points.extend((-1+tau, 1-tau))
    points.sort(key=lambda x: x.mid().fmpq())
    if any(not left < right for left, right in zip(points, points[1:])):
        raise ArithmeticError("unresolved combined-square cells")
    result = arb(0)
    for left, right in zip(points, points[1:]):
        midpoint, half = (left+right)/2, (right-left)/2
        active = []
        for tau, coefficient in terms:
            for shift in (-tau, tau):
                point = midpoint+shift
                if -1 < point < 1:
                    active.append((shift, coefficient))
                elif not (point < -1 or 1 < point):
                    raise ArithmeticError("unresolved signed-image membership")
        for node, weight in _gram_rule(problem.N):
            x = midpoint+half*node
            a, b = arb(0), arb(0)
            for shift, coefficient in active:
                values = legendre_values(x+shift, max(m, n)+1)
                a -= coefficient*values[m]
                b -= coefficient*values[n]
            result += half*weight*a*b
    return result


def operator_column(problem, n):
    """One complete bilinear V+P column, all physical low/head output rows."""
    from flint import arb_mat
    if type(n) is not int or not 0 <= n < problem.N:
        raise ValueError("invalid low input mode")
    modes = range(n % 2, problem.M, 2)
    result = arb_mat(len(modes), 1)
    terms = _terms(problem)
    for start in range(0, problem.source_gauss_order, 32):
        nodes = _gram_rule(problem.source_gauss_order)[start:start+32]
        for tau, coefficient in terms:
            for sign in (-1, 1):
                half = 1-tau/2
                midpoint = -sign*tau/2
                rows, weighted = [], []
                for node, weight in nodes:
                    x = midpoint+half*node
                    values = legendre_values(x, problem.M)
                    shifted = legendre_values(x+sign*tau, n+1)[n]
                    rows.append([values[m] for m in modes])
                    weighted.append([-coefficient*half*weight*shifted])
                result += arb_mat(rows).transpose()*arb_mat(weighted)
    return [result[i, 0]+potential_bilinear(m, n) for i, m in enumerate(modes)]


def assemble_entry(problem, m, n, columns):
    """Complete low/J/exterior entries, with every physical projection row."""
    from flint import arb_mat
    v = potential_bilinear(m, n)
    vv = potential_square(m, n)
    p2 = combined_square_entry(problem, m, n)
    vp = ordered_vp(problem, m, n)
    pv = vp if m == n else ordered_vp(problem, n, m)
    joint = vv+p2+vp+pv
    modes = range(m % 2, problem.M, 2)
    left = arb_mat([[columns[m][i]*arb(fmpq(2*k+1, 2)) for i, k in enumerate(modes)]])
    right = arb_mat([[value] for value in columns[n]])
    exterior = joint-(left*right)[0, 0]
    actual = columns[n][m//2]+arb(residual_bilinear(problem, m, n))
    if m == n:
        harmonic, _ = _harmonics(m)
        support = arb(fmpq(problem.support.numerator, problem.support.denominator))
        actual += arb(fmpq(2, 2*m+1))*(arb(harmonic[m])-arb.const_euler()
                                             -(2*arb.pi()*support).log())
    result = {("V", m, n): v, ("VV", m, n): vv, ("P_squared", m, n): p2,
              ("VP", m, n): vp, ("J_F", m, n): joint, ("A_model", m, n): actual,
              ("P_L", m, n): columns[n][m//2]-v, ("G_exterior", m, n): exterior,
              ("weighted_complete_tail", m, n): exterior*arb(fmpq(
                  problem.kappa.numerator, problem.kappa.denominator))}
    if m != n:
        result[("VP", n, m)] = pv
    return result


def evaluate_gram(task, staging):
    """Dispatch complete selected mathematics only inside the owned role worker."""
    from scripts.whole_source import execution
    from scripts.whole_source.gram import evaluate_owned
    worker = execution._WORKER
    if (worker is None or worker[-1] is not staging or staging.spec.role != "producer" or
            ctx.prec != staging.spec.problem.arithmetic.source_bits or
            ctx.prec != worker[0].precision_bits or ctx.threads != staging.spec.native_threads):
        raise RuntimeError("signed low/exterior mathematics requires owned producer policy")
    return evaluate_owned(task, staging, {
        "column": operator_column, "residual": residual_bilinear,
        "potential": potential_bilinear, "potential_square": potential_square,
        "vp": ordered_vp, "square": combined_square_entry, "entry": assemble_entry})


def _frequency_seed(c, n):
    """Pay nonexact argument error using |j_n'(real)| <= 1."""
    midpoint = c.mid()
    value = midpoint.bessel_j(arb(fmpq(2*n+1, 2)))*(arb.pi()/(2*midpoint)).sqrt()
    return arb(value.mid(), (value.rad()+c.rad()).upper())


def frequency_anchor(problem, omega):
    """Full compact frequency projector, with one paid downward Bessel vector."""
    from fractions import Fraction
    if type(omega) is not Fraction or omega < 0:
        raise ValueError("nonnegative exact frequency required")
    if not omega:
        def zero(m, n):
            if not (type(m) is int and type(n) is int and
                    0 <= m < problem.M and 0 <= n < problem.M and (m-n) % 2 == 0):
                raise ValueError("invalid frequency modes")
            return arb(0)
        return zero
    c = arb(fmpq(problem.support.numerator, problem.support.denominator))*fmpq(
        omega.numerator, omega.denominator)
    if not c > 0:
        raise ArithmeticError("unresolved positive frequency")
    js = [arb(0) for _ in range(problem.M+2)]
    for n in (problem.M, problem.M+1):
        js[n] = _frequency_seed(c, n)
        if js[n].rel_accuracy_bits() < min(2048, ctx.prec//4):
            raise ArithmeticError("unresolved downward Bessel seed")
    for n in range(problem.M, 0, -1):
        js[n-1] = (2*n+1)/c*js[n]-js[n+1]
    derivatives = [n/c*js[n]-js[n+1] for n in range(problem.M)]
    integrals = [(2*c).si()+((2*c).cos()-1)/(2*c)]
    for n in range(1, problem.M):
        integrals.append(integrals[-1]-c*(js[n-1]**2+js[n]**2))
    def entry(m, n):
        if not (type(m) is int and type(n) is int and
                0 <= m < problem.M and 0 <= n < problem.M and (m-n) % 2 == 0):
            raise ValueError("invalid frequency modes")
        if m == n:
            value = 4*integrals[n]/(arb.pi()*(2*n+1))
        else:
            value = 4/arb.pi()*((-1)**((m-n)//2))*c*c*(
                derivatives[n]*js[m]-derivatives[m]*js[n])/(n*(n+1)-m*(m+1))
        if not value.is_finite():
            raise ArithmeticError("nonfinite frequency projector")
        return value
    return entry


def head_column(problem, n, full_column):
    """Convert signed F+R_K ordinary bilinears into physical head expansion."""
    if (type(n) is not int or not 0 <= n < problem.N or
            len(full_column) != problem.M//2):
        raise ValueError("invalid full physical input column")
    return [(full_column[k//2]+arb(residual_bilinear(problem, k, n)))*fmpq(2*k+1, 2)
            for k in range(problem.N+n % 2, problem.M, 2)]


def head_image(problem, column, tiles):
    """Y=K C using current native blocks, including every transposed cross block."""
    h = (problem.M-problem.N)//2
    if len(column) != h:
        raise ValueError("incomplete physical head column")
    result = [arb(0) for _ in range(h)]
    for tile in tiles:
        entries = list(tile)
        if not entries:
            raise ValueError("empty head kernel tile")
        rows = sorted({i for i, _, _ in entries})
        columns = sorted({j for _, j, _ in entries})
        parity = rows[0] % 2
        if any(not problem.N <= k < problem.M or k % 2 != parity for k in rows+columns):
            raise ValueError("invalid physical head tile")
        # A diagonal upper block includes its reflected values in the same product.
        diagonal = rows[0] == columns[0]
        if diagonal:
            modes = sorted(set(rows+columns))
            indices = {m: i for i, m in enumerate(modes)}
            matrix = arb_mat(len(modes), len(modes))
            for i, j, value in entries:
                matrix[indices[i], indices[j]] = value
                matrix[indices[j], indices[i]] = value
            image = matrix*arb_mat([[column[(k-problem.N)//2]] for k in modes])
            for index, k in enumerate(modes):
                result[(k-problem.N)//2] += image[index, 0]
        else:
            ri, ci = {k: i for i, k in enumerate(rows)}, {k: i for i, k in enumerate(columns)}
            matrix = arb_mat(len(rows), len(columns))
            for i, j, value in entries:
                matrix[ri[i], ci[j]] = value
            forward = matrix*arb_mat([[column[(k-problem.N)//2]] for k in columns])
            reverse = matrix.transpose()*arb_mat([[column[(k-problem.N)//2]] for k in rows])
            for index, k in enumerate(rows):
                result[(k-problem.N)//2] += forward[index, 0]
            for index, k in enumerate(columns):
                result[(k-problem.N)//2] += reverse[index, 0]
    return result


def head_pair(problem, left, image):
    h = (problem.M-problem.N)//2
    if len(left) != h or len(image) != h:
        raise ValueError("incomplete head contraction")
    value = (arb_mat([left])*arb_mat([[x] for x in image]))[0, 0]
    if not value.is_finite():
        raise ArithmeticError("nonfinite coupled head")
    return value


def evaluate_source(task, staging):
    """Evaluate source work only in the bound owned producer."""
    from scripts.whole_source import execution
    worker = execution._WORKER
    if (worker is None or worker[-1] is not staging or staging.spec.role != "producer" or
            ctx.prec != staging.spec.problem.arithmetic.source_bits or
            ctx.prec != worker[0].precision_bits or ctx.threads != staging.spec.native_threads):
        raise RuntimeError("source mathematics requires owned producer policy")
    staging._check()
    from scripts.whole_source.pipeline import evaluate_owned
    return evaluate_owned(task, staging, {
        "column": operator_column, "entry": assemble_entry, "anchor": frequency_anchor,
        "head_column": head_column, "head_image": head_image, "head_pair": head_pair})
