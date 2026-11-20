"""Independent signed-window arithmetic for declared entry selections only."""
from __future__ import annotations

from fractions import Fraction
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
