"""Finite operators expose missing prefix subtraction, tail mass and H_L shifts."""
from fractions import Fraction as Q

from flint import fmpq, fmpq_mat

from scripts import verify_weighted_low_space as exact
from scripts.weil_coupling_projection import projection_majorant


def point(value: Q, bits: int) -> list[int]:
    integer = value*(1 << bits)
    assert integer.denominator == 1
    return [integer.numerator, integer.numerator]


def test_promoted_mode_is_removed_but_complete_tail_and_new_weights_remain():
    bits = 32
    # High modes1..4 have amplitudes2,1,0,1/6. Mode4 is omitted
    # from the retained head but remains in its complete Gram.
    gram = [[point(Q(69, 8), bits)]]
    heads = [[point(value, bits)] for value in (Q(2), Q(1), Q(0))]
    result = projection_majorant(gram, heads, 1, 2, 4, Q(1), bits)
    lower, upper = [Q(value, 1 << bits) for value in result[0][0]]
    # After promoting mode1, exact energy is (5/2)*1+(1/8)*(12/19).
    actual = Q(49, 19)
    assert lower <= actual <= upper
    assert upper < 3


def test_signed_off_diagonal_majorant_encloses_the_physical_finite_operator():
    bits = 40
    original_n, projection, boundary = 2, 3, 5
    amplitudes = [[Q(1), Q(-1, 2)], [Q(-1, 4), Q(3, 4)],
                  [Q(1, 8), Q(1, 4)], [Q(1, 16), Q(-1, 8)]]
    gram = [[sum((row[i]*row[j]*Q(2*k+1, 2)
                  for k, row in zip(range(2, 6), amplitudes)), Q())
             for j in range(2)] for i in range(2)]
    triangle = [[point(gram[i][j], bits) for j in range(i, 2)] for i in range(2)]
    heads = [[point(value, bits) for value in row] for row in amplitudes[:-1]]
    published = projection_majorant(triangle, heads, original_n, projection, boundary, Q(7, 10), bits)
    _, upper, _ = exact._order_bounds(published, bits)
    actual = fmpq_mat(2, 2)
    for k, row in zip(range(2, 6), amplitudes):
        if k < projection:
            continue
        weight = 1/(Q(7, 10)+sum((Q(1, j) for j in range(projection+1, k+1)), Q()))
        for i in range(2):
            for j in range(2):
                value = row[i]*row[j]*Q(2*k+1, 2)*weight
                actual[i, j] += fmpq(value.numerator, value.denominator)
    slack = upper-actual
    assert slack[0, 0] >= 0 and slack[1, 1] >= 0 and slack.det() >= 0
    assert slack[0, 0] < fmpq(1, 1000) and slack[1, 1] < fmpq(1, 1000)
