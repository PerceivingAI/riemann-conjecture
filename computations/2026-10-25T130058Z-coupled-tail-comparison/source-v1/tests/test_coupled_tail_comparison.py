"""Physical residual control and the finite/infinite inverse boundary."""
from fractions import Fraction as Q

from flint import fmpq, fmpq_mat

from scripts.weil_coupled_tail_comparison import finite_bracket, schur_residual


def test_certified_elimination_pays_dual_residual_with_legendre_masses():
    # K>=I>=D/2: K-I is (z+u+v)^2+2z^2. The exact tail minimum is10/3.
    matrix = fmpq_mat([[4, 1, 1], [1, 2, 1], [1, 1, 2]])
    q, residual, lower = schur_residual(matrix, [Q(1), Q(-1, 4), Q(-1, 3)], 1, Q(1, 2))
    assert q == Q(241, 72)
    assert residual == Q(17, 288)  # (1/6)^2/(2/3)+(1/12)^2/(2/5).
    assert lower == q-2*residual < Q(10, 3) < q
    _, optimal_residual, optimal_lower = schur_residual(
        matrix, [Q(1), Q(-1, 3), Q(-1, 3)], 1, Q(1, 2))
    assert optimal_residual == 0 and optimal_lower == Q(10, 3)


def test_finite_inverse_and_full_source_error_cannot_be_discarded():
    # Finite E has C=2,b=1,v=1/2. Adding one outside mode changes its inverse.
    low, high, _ = finite_bracket(Q(4), Q(4), Q(7, 2), Q(7, 2),
                                  Q(), Q(), Q(2), Q(1, 6), Q(1))
    assert low == high == Q(1, 2)
    full_tail = fmpq_mat([[2, 1], [1, 2]])
    b = fmpq_mat([[1], [0]])
    full_energy = (b.transpose()*full_tail.inv()*b)[0, 0]
    assert full_energy == fmpq(2, 3) and full_energy > high
    # A legitimate perturbation -delta D changes C to29/15, so I_E=15/29.
    low, high, _ = finite_bracket(Q(4), Q(4), Q(7, 2), Q(7, 2),
                                  Q(), Q(1, 10), Q(2), Q(1, 6), Q(1))
    assert low <= Q(15, 29) <= high
