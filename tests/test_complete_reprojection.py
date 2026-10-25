"""Complete reprojection must restore the old-low/new-tail prefix and its mass."""
from fractions import Fraction as Q

from flint import fmpq, fmpq_mat

from scripts import verify_weighted_low_space as exact
from scripts.weil_complete_reprojection import gamma_upper, positive_majorant, project_arrays


def point(value: Q, bits: int) -> list[int]:
    scaled = value*(1 << bits)
    assert scaled.denominator == 1
    return [scaled.numerator, scaled.numerator]


def test_complete_reference_restores_new_tail_rows_and_signed_source_sum():
    bits = 40
    # Original low dimension3, new low dimension2. Full operator couplings
    # at high modes2,3,4 are [1,-1/2], [1/2,-1/4], [1/8,1/4].
    # The last mode is outside the retained head but remains in G3.
    a = [[Q(10), Q(0), Q(1)], [Q(10), Q(-1, 2)], [Q(100)]]
    g = [[Q(121, 128), Q(-19, 64), Q(0)], [Q(1, 2), Q(0)], [Q(0)]]
    packet = {'dimension': 3, 'boundary': 4,
              'matrices': {'A_K': [[point(v, bits) for v in row] for row in a],
                           'G_K': [[point(v, bits) for v in row] for row in g]},
              'heads': {'V': [[point(v, bits) for v in (Q(3, 4), Q(-1, 2), Q())]],
                        'P': [[point(v, bits) for v in (Q(-1, 4), Q(1, 4), Q())]],
                        'RK': [[point(Q(), bits) for _ in range(3)]]}}
    _, tail, heads = project_arrays(packet, 2)
    triangle = positive_majorant(tail, heads, 2, 3, 4, Q(1), bits)
    _, upper, _ = exact._order_bounds(triangle, bits)
    actual = fmpq_mat(2, 2)
    for k, amplitudes, weight in (
        (2, (Q(1), Q(-1, 2)), Q(1)),
        (3, (Q(1, 2), Q(-1, 4)), Q(3, 4)),
        (4, (Q(1, 8), Q(1, 4)), Q(12, 19)),
    ):
        for i in range(2):
            for j in range(2):
                value = amplitudes[i]*amplitudes[j]*Q(2*k+1, 2)*weight
                actual[i, j] += fmpq(value.numerator, value.denominator)
    slack = upper-actual
    assert slack[0, 0] >= 0 and slack[1, 1] >= 0 and slack.det() >= 0
    assert slack[0, 0] < fmpq(1, 100000) and slack[1, 1] < fmpq(1, 100000)


def test_unchanged_low_projection_keeps_the_complete_unobserved_tail():
    bits = 32
    tail = [[point(Q(53, 32), bits)]]
    heads = [[point(Q(1), bits)]]
    triangle = positive_majorant(tail, heads, 1, 1, 2, Q(1), bits)
    lo, hi = [Q(v, 1 << bits) for v in triangle[0][0]]
    assert lo <= Q(77, 48) <= hi
    assert gamma_upper(tail, heads, 1, 1, 2, bits) == Q(5, 64)
