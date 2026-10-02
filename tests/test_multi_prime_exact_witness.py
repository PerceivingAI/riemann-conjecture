"""Native multi-prime witnesses preserve exact proof arithmetic and failures."""
from fractions import Fraction

import pytest

from scripts.cert.exact_prime_schur_common import make_witness as reference_witness
from scripts.cert.matrices import RationalInterval
from scripts.cert.multi_prime_exact_witness import make_witness


def _positive_block(n, scale=Fraction(1)):
    lower = [
        [Fraction(int(i == j)) if j >= i else
         Fraction((-1) ** (i + j) * (i + j + 1), 2 * i + 2 * j + 13)
         for j in range(n)] for i in range(n)
    ]
    diagonal = [scale * Fraction(3 * (i + 1), 2 * i + 5) for i in range(n)]
    midpoint = [
        [sum((lower[i][k] * diagonal[k] * lower[j][k] for k in range(n)), Fraction(0))
         for j in range(n)] for i in range(n)
    ]
    return [
        [RationalInterval(value - scale * Fraction(i + j + 1, 1 << 48),
                          value + scale * Fraction(i + j + 1, 1 << 48))
         for j, value in enumerate(row)] for i, row in enumerate(midpoint)
    ]


@pytest.mark.parametrize("n", [1, 2, 5])
@pytest.mark.parametrize("bits", [8, 24, 56])
def test_native_witness_equals_exact_interval_reference(n, bits):
    block = _positive_block(n)
    expected_witness, expected_margin = reference_witness(block, bits)
    witness, margin = make_witness(block, bits)
    assert witness == expected_witness
    assert margin == expected_margin > 0


def test_native_witness_handles_rationals_outside_binary64():
    block = _positive_block(3, Fraction(1 << 1200, 17))
    assert make_witness(block, 32) == reference_witness(block, 32)


def test_rounding_halfway_values_away_from_zero():
    coefficient = Fraction(1, 512)
    block = [
        [RationalInterval(1), RationalInterval(coefficient), RationalInterval(-coefficient)],
        [RationalInterval(coefficient), RationalInterval(1 + coefficient**2), RationalInterval(-coefficient**2)],
        [RationalInterval(-coefficient), RationalInterval(-coefficient**2), RationalInterval(1 + coefficient**2)],
    ]
    witness, margin = make_witness(block, 8)
    assert witness[1][0] == -Fraction(1, 256)
    assert witness[2][0] == Fraction(1, 256)
    assert (witness, margin) == reference_witness(block, 8)


@pytest.mark.parametrize("block", [
    [[RationalInterval(0)]],
    [[RationalInterval(-1)]],
    [[RationalInterval(1), RationalInterval(2)],
     [RationalInterval(2), RationalInterval(1)]],
    [[RationalInterval(1), RationalInterval(0), RationalInterval(0)],
     [RationalInterval(0), RationalInterval(1), RationalInterval(0)],
     [RationalInterval(0), RationalInterval(0), RationalInterval(0)]],
    [[RationalInterval(-1, 3)]],
])
def test_nonpositive_pivots_and_interval_margin_fail_closed(block):
    with pytest.raises(RuntimeError) as reference:
        reference_witness(block, 32)
    with pytest.raises(RuntimeError) as native:
        make_witness(block, 32)
    # These failure reasons are retained in canonical candidate diagnostics.
    assert str(native.value) == str(reference.value)


@pytest.mark.parametrize("block,bits", [([], 32), ([[RationalInterval(1), RationalInterval(0)]], 32),
                                           ([[RationalInterval(1)]], 7)])
def test_invalid_shape_or_witness_resolution_is_rejected(block, bits):
    with pytest.raises(ValueError):
        make_witness(block, bits)
