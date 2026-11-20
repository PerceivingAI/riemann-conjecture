"""Exact polynomial and native arithmetic checks for selected signed windows."""
from dataclasses import asdict
from fractions import Fraction
import hashlib
import importlib.metadata
import json
from math import comb, factorial
from pathlib import Path
import shutil

from flint import arb, arb_poly, ctx, fmpq, fmpq_poly
import pytest

from scripts.whole_source import analytic
from scripts.whole_source.artifacts import (
    Axis, ChunkStore, CodecBounds, CollectionLock, CollectionSpec, ContributionTask,
    QuantitySpec, StagedChunk,
)
from scripts.whole_source.contract import (
    ArtifactRef, ModeRange, QuantityKey, ROOT, bind_problem, canonical_bytes, expected_domain, problem_id,
)
from scripts.whole_source.execution import BUNDLE, ExecutionPlan, WorkloadExecution, _HELPERS, _RUNTIME


@pytest.fixture(scope="module")
def problem():
    return bind_problem("retained-t081")


def rational(value):
    return fmpq(value.numerator, value.denominator)


def exact_window(row, column, shift, left, right):
    """Small-degree oracle using literal binomial sums and rational integration."""
    total = fmpq(0)
    for i in range(len(row)):
        for k in range(len(column)):
            for j in range(k + 1):
                degree = i + j
                total += (row[i] * column[k] * comb(k, j) * shift ** (k - j) *
                          (right ** (degree + 1) - left ** (degree + 1)) / (degree + 1))
    return total


@pytest.mark.parametrize("degree", [0, 1, 2, 132, 824, 825, 826, 827, 1650, 1651])
def test_ratio_matches_all_native_exact_coefficients(degree):
    actual = analytic.rodrigues_ratio(degree)
    expected = fmpq_poly.legendre_p(degree)
    assert actual == expected
    assert len(actual) == degree + 1
    assert actual[degree] == fmpq(comb(2 * degree, degree), 1 << degree)
    assert all(actual[k] == 0 for k in range((degree + 1) % 2, degree, 2))


@pytest.mark.parametrize("m,n", [(0, 0), (1, 1), (2, 3), (5, 4), (6, 6)])
@pytest.mark.parametrize("window", [0, 1])
def test_signed_rational_window_matches_exact_integral(m, n, window):
    tau = fmpq(3, 7)
    left, right, shift = ((fmpq(-1), 1 - tau, tau) if window == 0 else
                          (-1 + tau, fmpq(1), -tau))
    row, column = fmpq_poly.legendre_p(m), fmpq_poly.legendre_p(n)
    expected = exact_window(row, column, shift, left, right)
    with ctx.workprec(512):
        shifted = analytic.binomial_shift(analytic.rodrigues_ratio(n), arb(shift),
                                          [factorial(k) for k in range(12)], 12)
        moments = analytic.power_window_moments(arb(left), arb(right), m + 11)
        actual = analytic.integrate_window(analytic.rodrigues_ratio(m), shifted, moments)
        assert actual.contains(expected)
        assert actual.rad() < arb(2) ** -400
        assert len(shifted) == 12
        assert all(value.is_zero() for value in shifted[n + 1:])


def test_full_low_power_and_moment_vector_endpoints(problem):
    with ctx.workprec(problem.arithmetic.audit_bits):
        shifted = analytic.binomial_shift(analytic.rodrigues_ratio(problem.N - 1), arb(fmpq(1, 3)),
                                          [factorial(k) for k in range(problem.N)], problem.N)
        assert len(shifted) == 826
        assert shifted[825].contains(fmpq(comb(1650, 825), 1 << 825))
        assert not shifted[825].contains(0)
        moments = analytic.power_window_moments(arb(-1), arb(1), problem.M + problem.N - 2)
        assert len(moments) == 2477
        assert moments[-1].contains(fmpq(2, 2477))
        assert moments[-2].is_zero()


def low_formula(problem, m, term_index):
    power, prime = ((2, 2), (3, 3), (4, 2), (5, 5))[term_index]
    tau = arb(power).log() / arb(rational(problem.support))
    integral = 2 - tau if m == 0 else arb(2) / 3 - tau + tau ** 3 / 6
    return -arb(prime).log() / arb(power).sqrt() * integral


@pytest.mark.parametrize("term_index", range(4))
@pytest.mark.parametrize("window_index", range(2))
@pytest.mark.parametrize("mode", [0, 1])
def test_all_terms_and_physical_windows_match_closed_low_integrals(problem, term_index, window_index, mode):
    with ctx.workprec(problem.arithmetic.audit_bits):
        expected = low_formula(problem, mode, term_index)
        actual = analytic.signed_window_arithmetic(problem, mode, mode, term_index, window_index)
        assert actual.overlaps(expected)
        assert actual.rad() < arb(2) ** -500


def test_wrong_physical_shift_and_prime_four_base_are_rejected_numerically(problem):
    with ctx.workprec(problem.arithmetic.audit_bits):
        tau = arb(2).log() / arb(rational(problem.support))
        factor = -arb(2).log() / arb(2).sqrt()
        first = analytic.signed_window_arithmetic(problem, 0, 1, 0, 0)
        second = analytic.signed_window_arithmetic(problem, 0, 1, 0, 1)
        assert first.overlaps(factor * (tau - tau ** 2 / 2))
        assert second.overlaps(-factor * (tau - tau ** 2 / 2))
        wrong_shift = factor * (-3 * tau + 3 * tau ** 2 / 2)
        assert not first.overlaps(wrong_shift)
        assert not first.overlaps(second)
        correct_four = analytic.signed_window_arithmetic(problem, 0, 0, 2, 0)
        wrong_base = -arb(4).log() / 2 * (2 - arb(4).log() / arb(rational(problem.support)))
        assert not correct_four.overlaps(wrong_base)


def test_omitted_actual_highest_input_coefficient_changes_integral(problem):
    with ctx.workprec(problem.arithmetic.audit_bits):
        tau = arb(2).log() / arb(rational(problem.support))
        complete = analytic.rodrigues_ratio(problem.N - 1)
        omitted = fmpq_poly(complete)
        omitted[problem.N - 1] = 0
        factorials = [factorial(k) for k in range(problem.N)]
        moments = analytic.power_window_moments(arb(-1), 1 - tau, problem.M + problem.N - 2)
        bad_shift = analytic.binomial_shift(omitted, tau, factorials, problem.N)
        bad = -arb(2).log() / arb(2).sqrt() * analytic.integrate_window(
            analytic.rodrigues_ratio(1), bad_shift, moments)
        good = analytic.signed_window_arithmetic(problem, 1, problem.N - 1, 0, 0)
        assert not bad.overlaps(good)


def native_antiderivative_reference(problem, m, n, term_index, window_index):
    """Separate native composition and endpoint integration, not moment reuse."""
    power, prime = ((2, 2), (3, 3), (4, 2), (5, 5))[term_index]
    tau = arb(power).log() / arb(rational(problem.support))
    left, right, shift = ((arb(-1), 1 - tau, tau) if window_index == 0 else
                          (-1 + tau, arb(1), -tau))
    row = arb_poly(fmpq_poly.legendre_p(m))
    column = arb_poly(fmpq_poly.legendre_p(n))
    primitive = (row * column(arb_poly([shift, 1]))).integral()
    return -arb(prime).log() / arb(power).sqrt() * (primitive(right) - primitive(left))


@pytest.mark.parametrize("m,n", [(1650, 824), (1651, 825)])
def test_highest_head_second_window_matches_native_antiderivative(problem, m, n):
    with ctx.workprec(problem.arithmetic.audit_bits):
        expected = native_antiderivative_reference(problem, m, n, 3, 1)
        actual = analytic.signed_window_arithmetic(problem, m, n, 3, 1)
        assert actual.overlaps(expected)
        assert actual.rad() < arb(2) ** -500


def file_ref(root, relative):
    raw = (root / relative).read_bytes()
    return ArtifactRef(relative, hashlib.sha256(raw).hexdigest(), len(raw))


def native_case(tmp_path, problem):
    captured = tmp_path / "captured"
    program = "scripts/whole_source/analytic.py"
    paths = set(_RUNTIME) | {program} | {BUNDLE + "/" + name for name in _HELPERS}
    paths.update(item.path for item in problem.evidence)
    for relative in sorted(paths):
        destination = captured / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    code = tuple(file_ref(captured, relative) for relative in sorted(set(_RUNTIME) | {program}))
    origin = {"format": "whole-source-code-origin-v1", "origin_git_commit": "a7d43f501cd7cf6ea74360c4092ecaa11392dbef",
              "origin_git_dirty": True, "files": [asdict(item) for item in code]}
    (captured / "origin.json").write_bytes(canonical_bytes(origin))
    pairs = ((0, 0), (1, 1), (826, 824), (827, 825), (1650, 824), (1651, 825))
    quantities = []
    for m, n in pairs:
        key = QuantityKey("P_L" if m < problem.N else "P_H", m % 2, entry=(m, n))
        domain = expected_domain(problem, key)
        quantities.append(QuantitySpec(key, domain.rows, domain.columns, domain.symmetric_upper,
                                      (Axis("term", 0, 4), Axis("window", 0, 2))))
    quantities = tuple(quantities)
    bounds = CodecBounds(8 * 1024 ** 2, 256 * 1024, 1024 ** 2, 64, 65536,
                         256 * 1024, 64 * 1024, 256 * 1024 ** 2, 32 * 1024 ** 2, 64 * 1024 ** 2)
    version = importlib.metadata.version("python-flint")
    spec = CollectionSpec.create(problem, role="analytic", quantities=quantities,
        partition=(("columns", 1), ("rows", 1), ("term", 1), ("window", 1)),
        backend="python-flint", backend_version=version, native_threads=1,
        code_refs=code, bounds=bounds, code_root=captured)
    plan = ExecutionPlan(problem_id(problem), spec.collection_id, "analytic", 1, 1, 1,
        memory_mib=768, reserve_mib=64, root_mib=128, worker_base_mib=80, worker_private_mib=64,
        native_workspace_mib=32, conversion_mib=16, codec_mib=64, queue_mib=8,
        supervisor_increment_mib=32, repository_mib=128, temporary_mib=16, minimum_free_mib=16,
        max_tasks=8, task_bytes=8192, result_bytes=16384, log_bytes=1024 ** 2,
        task_program=file_ref(captured, program), task_function="evaluate",
        precision_bits=problem.arithmetic.audit_bits, backend="python-flint", backend_version=version,
        provenance=file_ref(captured, "origin.json"), scope="SELECTION_ONLY")
    return captured, spec, plan


def test_owned_native_worker_stages_real_selected_entries_without_producer(tmp_path, problem):
    captured, spec, plan = native_case(tmp_path, problem)
    task = {"operation": "window", "term_index": 0, "window_index": 0}
    task["task_id"] = hashlib.sha256(canonical_bytes(task)).hexdigest()
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=captured) as execution:
            execution.run_stage("arithmetic", [task])
            results = list(execution.read_results("arithmetic"))
            result = results[0]["result"]
            store = ChunkStore(lock, spec, attempt_id=execution.attempt_id)
            for chunk in result["chunks"]:
                wire = chunk["task"]
                domain = ContributionTask(QuantityKey.from_dict(wire["quantity"]),
                    ModeRange(**wire["rows"]), ModeRange(**wire["columns"]),
                    tuple(Axis(**axis) for axis in wire["axes"]))
                staged = StagedChunk(Path(chunk["path"]), domain, ArtifactRef(**chunk["ref"]),
                                     chunk["generation"], chunk["attempt_id"])
                ref = store.publish_chunk(domain, staged)
                snapshot = store.read_chunk(ref)
                record = snapshot.records[0]
                with ctx.workprec(problem.arithmetic.audit_bits):
                    if record.row < 2:
                        expected = low_formula(problem, record.row, 0)
                    else:
                        expected = native_antiderivative_reference(problem, record.row, record.column, 0, 0)
                    assert expected.upper().fmpq() >= rational(record.lower)
                    assert expected.lower().fmpq() <= rational(record.upper)
                    assert record.upper - record.lower < Fraction(1, 1 << 500)


def test_evaluate_refuses_unowned_call_before_staging():
    with pytest.raises(RuntimeError, match="owned worker"):
        analytic.evaluate({"operation": "window", "term_index": 0, "window_index": 0}, None)
