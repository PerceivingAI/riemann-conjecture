"""Small independent controls for nonproof floating congruence proposals."""
import builtins
from fractions import Fraction
import json
import math
import runpy
from types import SimpleNamespace

import numpy as np
import pytest
from scipy import optimize

from scripts.whole_source import proposal_float
from scripts.whole_source.proposal_float import optimize_theta


def residual(aw, hw, ew, theta):
    value = aw - (1.0 + float(theta)) * hw - (1.0 + 1.0 / float(theta)) * ew
    return (value + value.T) / 2.0


def assert_exact_json(value):
    if isinstance(value, dict):
        assert all(isinstance(key, str) for key in value)
        for item in value.values():
            assert_exact_json(item)
    elif isinstance(value, list):
        for item in value:
            assert_exact_json(item)
    else:
        assert type(value) in (str, int, bool, type(None))


def test_import_does_not_load_numerical_libraries(monkeypatch):
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.split(".")[0] in {"numpy", "scipy"}:
            raise AssertionError("numerical import before optimizer invocation")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    namespace = runpy.run_path(proposal_float.__file__)
    assert callable(namespace["optimize_theta"])


def test_diagonal_closed_optimum_and_exact_diagnostics():
    aw = np.diag([100.0, 80.0, 60.0])
    hw = np.diag([1.0, 0.25, 0.125])
    ew = 9.0 * hw
    inputs = [matrix.copy() for matrix in (aw, hw, ew)]
    theta, vectors, diagnostics = optimize_theta(aw, hw, ew)
    assert isinstance(theta, Fraction)
    assert theta > 0 and ((theta * (1 << 40)).denominator == 1)
    assert float(theta) == pytest.approx(math.sqrt(9.0 / 1.0), abs=2e-7)
    assert vectors.shape == aw.shape and vectors.dtype == np.dtype("float64")
    assert_exact_json(diagnostics)
    assert json.loads(json.dumps(diagnostics, allow_nan=False)) == diagnostics
    assert diagnostics["status"] == "NONPROOF_ONLY"
    assert diagnostics["production_admission"] is False
    objective = np.linalg.eigvalsh((1 + float(theta)) * hw + (1 + 1 / float(theta)) * ew)[-1]
    assert float.fromhex(diagnostics["rounded_objective_hex"]) == objective
    spectrum = np.linalg.eigvalsh(residual(aw, hw, ew, theta))
    np.testing.assert_allclose([float.fromhex(value) for value in diagnostics["residual_eigenvalues_hex"]], spectrum)
    assert diagnostics["residual_positive_eigenvalues"] == 3
    assert diagnostics["residual_zero_eigenvalues"] == 0
    assert diagnostics["residual_negative_eigenvalues"] == 0
    for matrix, original in zip((aw, hw, ew), inputs):
        np.testing.assert_array_equal(matrix, original)


def test_positive_full_rotated_whitening_is_identity():
    rotation = np.array([[0.6, -0.8, 0.0], [0.8, 0.6, 0.0], [0.0, 0.0, 1.0]])
    aw = rotation @ np.diag([20.0, 40.0, 80.0]) @ rotation.T
    hw = rotation @ np.diag([1.0, 2.0, 3.0]) @ rotation.T
    ew = 4.0 * hw
    theta, vectors, diagnostics = optimize_theta(aw, hw, ew)
    assert float(theta) == pytest.approx(2.0, abs=2e-7)
    assert vectors.shape == (3, 3)
    assert not np.allclose(vectors, np.diag(np.diag(vectors)))
    np.testing.assert_allclose(vectors.T @ residual(aw, hw, ew, theta) @ vectors,
                               np.eye(3), atol=2e-14, rtol=2e-14)
    assert diagnostics["transform_kind"] == "positive_whitening"


def test_negative_spectrum_keeps_full_nonidentity_signed_eigenbasis():
    rotation = np.array([[0.6, -0.8], [0.8, 0.6]])
    aw = rotation @ np.diag([1.0, 20.0]) @ rotation.T
    hw = np.eye(2)
    ew = np.eye(2)
    theta, vectors, diagnostics = optimize_theta(aw, hw, ew)
    spectrum = np.linalg.eigvalsh(residual(aw, hw, ew, theta))
    assert spectrum[0] < 0 < spectrum[1]
    assert vectors.shape == (2, 2)
    assert not np.allclose(vectors, np.diag(np.diag(vectors)))
    np.testing.assert_allclose(vectors.T @ vectors, np.eye(2), atol=2e-15)
    np.testing.assert_allclose(vectors.T @ residual(aw, hw, ew, theta) @ vectors,
                               np.diag(spectrum), atol=1e-14)
    assert diagnostics["transform_kind"] == "signed_diagonalization"
    assert diagnostics["residual_negative_eigenvalues"] == 1
    assert diagnostics["residual_positive_eigenvalues"] == 1


def test_zero_spectrum_uses_full_unscaled_basis():
    zero = np.zeros((3, 3))
    _, vectors, diagnostics = optimize_theta(zero, zero, zero)
    np.testing.assert_allclose(vectors.T @ vectors, np.eye(3), atol=1e-15)
    assert diagnostics["transform_kind"] == "signed_diagonalization"
    assert diagnostics["residual_zero_eigenvalues"] == 3
    assert np.isfinite(vectors).all()


def test_asymmetric_roundoff_is_symmetrized():
    aw = np.array([[20.0, 3.0], [1.0, 30.0]])
    hw = np.array([[1.0, 0.5], [0.25, 2.0]])
    ew = 4.0 * hw
    theta, vectors, _ = optimize_theta(aw, hw, ew)
    np.testing.assert_allclose(vectors.T @ residual(aw, hw, ew, theta) @ vectors,
                               np.eye(2), atol=1e-14)


@pytest.mark.parametrize("bad", [
    [[1.0]], np.ones(2), np.ones((2, 3)), np.empty((0, 0)),
    np.ones((1, 1), dtype=np.float32), np.ones((1, 1), dtype=np.int64),
    np.ones((1, 1), dtype=np.complex128), np.array([[np.nan]]),
    np.array([[np.inf]]), np.array([[-np.inf]]),
])
@pytest.mark.parametrize("position", [0, 1, 2])
def test_rejects_malformed_and_nonfinite_inputs(bad, position):
    matrices = [np.eye(1), np.eye(1), np.eye(1)]
    matrices[position] = bad
    with pytest.raises(ValueError):
        optimize_theta(*matrices)


def test_rejects_different_common_dimension():
    with pytest.raises(ValueError):
        optimize_theta(np.eye(2), np.eye(3), np.eye(2))


@pytest.mark.parametrize("position", [0, 1, 2])
def test_rejects_finite_inputs_with_overflowing_computation(position):
    matrices = [np.eye(2), np.eye(2), np.eye(2)]
    matrices[position] = np.eye(2) * np.finfo(np.float64).max
    with pytest.raises(ValueError):
        optimize_theta(*matrices)


def test_failed_optimizer_has_no_transform_fallback(monkeypatch):
    def unsuccessful(*args, **kwargs):
        return SimpleNamespace(success=False, x=0.0, fun=1.0, nfev=1)

    monkeypatch.setattr(optimize, "minimize_scalar", unsuccessful)
    with pytest.raises(ValueError):
        optimize_theta(np.eye(2), np.eye(2), np.eye(2))


def test_failed_eigendecomposition_has_no_transform_fallback(monkeypatch):
    def failed(*args, **kwargs):
        raise np.linalg.LinAlgError("control eigensolver failure")

    monkeypatch.setattr(np.linalg, "eigh", failed)
    with pytest.raises(ValueError):
        optimize_theta(np.eye(2), np.eye(2), np.eye(2))


def test_nonfinite_eigenvectors_are_rejected(monkeypatch):
    original = np.linalg.eigh

    def corrupted(matrix):
        spectrum, vectors = original(matrix)
        vectors[0, 0] = np.nan
        return spectrum, vectors

    monkeypatch.setattr(np.linalg, "eigh", corrupted)
    with pytest.raises(ValueError):
        optimize_theta(np.eye(2), np.eye(2), np.eye(2))
