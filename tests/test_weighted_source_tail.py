"""Finite spectral fixtures for outward weighted sums and collective residuals."""
from fractions import Fraction as Q
import json

import pytest

from scripts.weil_weighted_source_tail import _consequences


@pytest.mark.parametrize("delta", [Q(), Q(1, 1000)])
def test_many_distinct_inverse_weights_enclose_known_finite_energy(delta):
    # A synthetic finite spectral source, not a claimed Weil source reconstruction.
    # Distinct rational inverse weights reproduce the real denominator-growth bug.
    mu = Q(1, (1 << 1024)-109)
    original = {"mu_lower_exact": str(mu), "a_full_rayleigh_upper_exact": "10"}
    source = {"exact_trial_mass_norm": "1/2", "delta_upper_exact": str(delta)}
    audit = {"exact": {"prefix_only_reference_upper": "9",
                       "known_inverse_lower": "1", "known_inverse_upper": "1"}}
    joint = {"scalars": {"joint_tail": ["1/100", "1/100"]},
             "exact": {"J_concentration_lower": "0"}}
    heads = {str(k): {"sum_truncated": ["1/100", "1/100"], "R32": ["0", "0"]}
             for k in range(225, 425, 2)}
    result = _consequences(original, source, audit, joint,
                          {"a_truncated": ["10", "10"]}, heads)
    # Exercise the actual public JSON boundary without relaxing Python's integer limit.
    packet = json.loads(json.dumps(result))
    expected = sum((Q(1, 10000)/(mu+sum((Q(1, j) for j in range(193, k+1)), Q()))
                    for k in range(225, 425, 2)), Q())
    # A concrete admissible error parallel to the finite source; its L2 norm is
    # below delta*sqrt(1/2). This tests nonzero collective error, not a mock echo.
    full_energy = (1+delta/10)**2*expected
    exact = {name: Q(value) for name, value in packet["exact"].items()}
    assert exact["J_full_lower"] <= full_energy <= exact["J_full_upper"]
    reference = 9-full_energy
    assert exact["reference_lower"] <= reference <= exact["reference_upper"]
    assert packet["status"] == "POSITIVE_DIAGONAL_REFERENCE_DIRECTION"
