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
