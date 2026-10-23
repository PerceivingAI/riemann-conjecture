"""Exact one-sided decision boundaries and immutable-input controls."""
from copy import deepcopy
from fractions import Fraction as Q
import json

import pytest

from scripts.weil_directional_exact_screen import (
    DEGREES, ORIGINAL, SOURCE, SOURCE_SHA256, _bound, _load, _validate,
)


def _zero_intervals():
    return {k: (Q(), Q()) for k in DEGREES}


@pytest.mark.parametrize("interval,expected_distance", [
    ((Q(1), Q(2)), Q(1)),
    ((Q(-2), Q(-1)), Q(1)),
    ((Q(-1), Q(1)), Q(0)),
])
def test_absolute_lower_uses_nearest_endpoint_not_midpoint(interval, expected_distance):
    intervals = _zero_intervals()
    intervals[193] = interval
    result = _bound(Q(1), Q(0), Q(0), intervals)
    w193 = 1/(1+Q(1, 193))
    w211 = 1/(1+sum((Q(1, j) for j in range(193, 212)), Q()))
    expected = -(w193-w211)*expected_distance**2
    assert Q(result["directional_upper_exact"]) == expected
    assert result["status"] == ("NEGATIVE_SUFFICIENT_CRITERION" if expected < 0 else "INCONCLUSIVE")


def test_infinite_tail_charge_is_not_dropped_when_finite_moments_vanish():
    result = _bound(Q(1), Q(1), Q(2), _zero_intervals())
    w211 = 1/(1+sum((Q(1, j) for j in range(193, 212)), Q()))
    assert Q(result["directional_upper_exact"]) == 1-2*w211 < 0
    assert result["status"] == "NEGATIVE_SUFFICIENT_CRITERION"


@pytest.mark.parametrize("a", [Q(0), Q(1)])
def test_zero_or_positive_upper_is_only_inconclusive(a):
    result = _bound(Q(1), a, Q(0), _zero_intervals())
    assert Q(result["directional_upper_exact"]) == a
    assert result["status"] == "INCONCLUSIVE"


def test_reversed_interval_and_float_scalar_cannot_enter_predicate():
    intervals = _zero_intervals()
    intervals[193] = Q(2), Q(1)
    with pytest.raises(ValueError, match="rational interval"):
        _bound(Q(1), Q(0), Q(0), intervals)
    with pytest.raises(TypeError, match="exact rationals"):
        _bound(1.0, Q(0), Q(0), _zero_intervals())


def test_changed_accepted_bytes_are_rejected(tmp_path):
    path = tmp_path/"altered.json"
    path.write_bytes(SOURCE.read_bytes()+b"\n")
    with pytest.raises(ValueError, match="byte identity"):
        _load(path, SOURCE_SHA256)


@pytest.mark.parametrize("change,match", [
    ("omit_residual", "residual enlargement"),
    ("unaccepted_component", "analytical acceptance"),
    ("missing_mode", "moment set"),
    ("wrong_metric", "configuration"),
])
def test_source_acceptance_is_required_before_rational_decision(change, match):
    original = json.loads(ORIGINAL.read_bytes())
    source = deepcopy(json.loads(SOURCE.read_bytes()))
    if change == "omit_residual":
        p, q = source["moments"]["193"]["sum_truncated"]["published_dyadic"]
        source["moments"]["193"]["full_source_interval"] = [str(Q(p, 1 << 352)), str(Q(q, 1 << 352))]
    elif change == "unaccepted_component":
        source["moments"]["193"]["P3"]["status"] = "NUMERICALLY_UNRESOLVED"
    elif change == "missing_mode":
        del source["moments"]["209"]
    else:
        source["coordinate_metric"] = "Euclidean"
    with pytest.raises(ValueError, match=match):
        _validate(original, source)
