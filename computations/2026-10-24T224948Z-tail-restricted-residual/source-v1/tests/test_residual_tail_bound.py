"""Behavioral controls for a two-sided Legendre-tail norm estimate."""
from fractions import Fraction as Q

from flint import fmpq, fmpq_mat
import pytest

from scripts import verify_residual_tail_bound as independent
from scripts.weil_residual_tail_bound import tail_constant


def test_even_polynomial_boundary_survives_but_lower_degree_is_annihilated():
    coefficients = [Q(0)]*4+[Q(1)]
    exact = [fmpq(0)]*4+[fmpq(1)]
    p2 = independent.native.poly_basis(3)[2]
    image = independent.project_tail(independent.kernel_image(exact, p2), 2)
    assert image == fmpq(16, 15)*p2
    assert tail_constant(coefficients, 2)/6 >= Q(16, 15)
    # Degree4 is below2N only at N>=3. All higher input degrees are
    # orthogonal to the kernel's degree4 input polynomial.
    assert tail_constant(coefficients, 3) == 0
    for poly in independent.native.poly_basis(5)[3:]:
        assert not independent.project_tail(independent.kernel_image(exact, poly), 3)


def test_signed_kernel_bound_covers_complete_projected_polynomial_images():
    coefficients = [Q(3), Q(-1), Q(2, 7), Q(1, 20), Q(-1, 11), Q(-1, 300)]
    exact = [fmpq(value.numerator, value.denominator) for value in coefficients]
    n = 3
    inputs = independent.native.poly_basis(7)[n:]
    images = [independent.project_tail(independent.kernel_image(exact, p), n) for p in inputs]
    radius = tail_constant(coefficients, n)/(n*(n+1))
    r = fmpq(radius.numerator, radius.denominator)
    slack = fmpq_mat([[(r*r*fmpq(2, 2*(n+i)+1) if i == j else 0)
                       -independent.inner(left, right)
                       for j, right in enumerate(images)] for i, left in enumerate(images)])
    for k in range(1, len(inputs)+1):
        assert fmpq_mat([[slack[i, j] for j in range(k)] for i in range(k)]).det() > 0


@pytest.mark.parametrize("dimension", [0, -1])
def test_zero_spectral_gap_is_outside_the_bound_domain(dimension):
    with pytest.raises(ValueError, match="positive integer"):
        tail_constant([Q(0), Q(1)], dimension)
