"""Floating-point parameter and full congruence proposals, never proof evidence."""
from __future__ import annotations

from fractions import Fraction
import math


def optimize_theta(aw, hw, ew):
    """Return a 40-bit dyadic theta, full float64 transform, and exact JSON diagnostics.

    The caller owns process budgets and BLAS configuration before this function
    imports NumPy or SciPy. All numerical results are NONPROOF_ONLY. A positive
    floating spectrum selects column scaling, not positivity acceptance.
    """
    import numpy as np
    from scipy.optimize import minimize_scalar

    matrices = (aw, hw, ew)
    if any(not isinstance(matrix, np.ndarray) or matrix.dtype != np.dtype("float64")
           or matrix.ndim != 2 or matrix.shape[0] == 0
           or matrix.shape[0] != matrix.shape[1] for matrix in matrices):
        raise ValueError("midpoint matrices must be nonempty square float64 arrays")
    if any(matrix.shape != aw.shape for matrix in matrices):
        raise ValueError("midpoint matrix dimensions differ")
    if any(not np.isfinite(matrix).all() for matrix in matrices):
        raise ValueError("midpoint matrices must be finite")
    dimension = aw.shape[0]

    def symmetric(matrix):
        matrix += matrix.T
        matrix *= 0.5
        if not np.isfinite(matrix).all():
            raise ValueError("nonfinite symmetrized matrix")
        return matrix

    def gram(theta):
        matrix = (1.0 + theta) * hw
        matrix += (1.0 + 1.0 / theta) * ew
        return symmetric(matrix)

    def objective(logtheta):
        theta = math.exp(float(logtheta))
        eigenvalues = np.linalg.eigvalsh(gram(theta))
        if eigenvalues.shape != (dimension,) or not np.isfinite(eigenvalues).all():
            raise ValueError("invalid objective eigenspectrum")
        return float(eigenvalues[-1])

    try:
        with np.errstate(over="raise", divide="raise", invalid="raise"):
            optimum = minimize_scalar(
                objective, bounds=(-20.0, 20.0), method="bounded",
                options={"xatol": 1e-10},
            )
            if (not optimum.success or not math.isfinite(float(optimum.x))
                    or not -20.0 <= optimum.x <= 20.0
                    or not math.isfinite(float(optimum.fun))):
                raise ValueError("Young parameter optimization failed")
            theta = Fraction(max(1, round(math.exp(float(optimum.x)) * (1 << 40))), 1 << 40)
            rounded_theta = float(theta)
            # Evaluate the rounded dyadic itself, rather than the optimizer's
            # unrounded parameter or a log/exp reconstruction of that dyadic.
            rounded_gram = gram(rounded_theta)
            rounded_spectrum = np.linalg.eigvalsh(rounded_gram)
            if (rounded_spectrum.shape != (dimension,)
                    or not np.isfinite(rounded_spectrum).all()):
                raise ValueError("invalid rounded objective eigenspectrum")
            rounded_objective = float(rounded_spectrum[-1])
            del rounded_gram, rounded_spectrum
            residual = aw - (1.0 + rounded_theta) * hw
            residual -= (1.0 + 1.0 / rounded_theta) * ew
            eigenvalues, vectors = np.linalg.eigh(symmetric(residual))
            del residual
            if (eigenvalues.shape != (dimension,) or vectors.shape != aw.shape
                    or vectors.dtype != np.dtype("float64")
                    or not np.isfinite(eigenvalues).all()
                    or not np.isfinite(vectors).all()
                    or np.any(eigenvalues[1:] < eigenvalues[:-1])):
                raise ValueError("invalid full residual eigensystem")
            positive = bool(eigenvalues[0] > 0.0)
            if positive:
                scales = 1.0 / np.sqrt(eigenvalues)
                if not np.isfinite(scales).all() or np.any(scales <= 0.0):
                    raise ValueError("invalid reciprocal square root scaling")
                vectors *= scales[np.newaxis, :]
                del scales
            if not np.isfinite(vectors).all() or np.any(np.max(np.abs(vectors), axis=0) == 0.0):
                raise ValueError("invalid full congruence vectors")
    except (FloatingPointError, OverflowError, np.linalg.LinAlgError) as exc:
        raise ValueError("unresolved floating proposal computation") from exc

    diagnostics = {
        "status": "NONPROOF_ONLY",
        "production_admission": False,
        "dimension": dimension,
        "theta_method": "bounded_logtheta_minimum_maximum_gram_eigenvalue",
        "eigen_method": "symmetric_full_eigh",
        "transform_kind": "positive_whitening" if positive else "signed_diagonalization",
        "optimizer_success": bool(optimum.success),
        "optimizer_evaluations": int(optimum.nfev),
        "logtheta_lower_hex": (-20.0).hex(),
        "logtheta_upper_hex": (20.0).hex(),
        "logtheta_xatol_hex": (1e-10).hex(),
        "optimizer_logtheta_hex": float(optimum.x).hex(),
        "optimizer_objective_hex": float(optimum.fun).hex(),
        "rounded_theta_hex": rounded_theta.hex(),
        "rounded_objective_hex": rounded_objective.hex(),
        "residual_eigenvalues_hex": [float(value).hex() for value in eigenvalues],
        "residual_minimum_eigenvalue_hex": float(eigenvalues[0]).hex(),
        "residual_maximum_eigenvalue_hex": float(eigenvalues[-1]).hex(),
        "residual_positive_eigenvalues": int(np.count_nonzero(eigenvalues > 0.0)),
        "residual_zero_eigenvalues": int(np.count_nonzero(eigenvalues == 0.0)),
        "residual_negative_eigenvalues": int(np.count_nonzero(eigenvalues < 0.0)),
        "vector_maximum_absolute_entry_hex": float(np.max(np.abs(vectors))).hex(),
    }
    return theta, vectors, diagnostics
