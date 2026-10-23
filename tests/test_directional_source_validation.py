"""Behavioral controls for the research-only fixed source consumer."""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction as Q

import pytest
from flint import arb, ctx

from scripts.weil_directional_source_validation import (
    COMPONENTS, INPUT, _component, _generate, _load_input, _reconstruct, _trial,
)


def test_original_trial_mass_norm_and_altered_parity_are_rejected():
    packet, z, norm = _load_input(INPUT)
    # Euclidean coefficients are not the physical norm; the true mass is < 1.
    assert norm < 1 < sum(a*a for a in z)
    wrong = deepcopy(packet)
    wrong["trial_rational_vector"][0] = "1/1048576"
    with pytest.raises(ValueError, match="odd dyadic trial"):
        _trial(wrong)
    wrong = deepcopy(packet)
    wrong["trial_norm_exact_enclosure"] = ["1", "2"]
    with pytest.raises(ValueError, match="mass norm"):
        _trial(wrong)


def test_changed_input_bytes_fail_before_analytical_work(tmp_path):
    altered = tmp_path/"altered.json"
    altered.write_bytes(INPUT.read_bytes()+b"\n")
    with pytest.raises(ValueError, match="byte identity"):
        _load_input(altered)


def test_publication_is_outward_for_negative_non_dyadic_value():
    with ctx.workprec(128):
        value = -arb(1)/3
        result = _component(value, value, bits=7)
    lo, hi = (Q(v, 128) for v in result["published_dyadic"])
    assert lo < -Q(1, 3) < hi
    assert (lo, hi) == (-Q(11, 32), -Q(41, 128))
    assert result["status"] == "PASS"


def test_padding_cannot_hide_disjoint_analytical_inputs():
    # Both fit the deliberately broad published interval; source balls disagree.
    with ctx.workprec(128):
        result = _component(arb(0), arb(1)/1024, bits=7)
    assert result["reference_contained"]
    assert result["status"] == "SOURCE_PROOF_GAP"


def test_overlapping_uncontained_reference_is_not_accepted():
    with ctx.workprec(128):
        result = _component(arb(1), arb(1, 1), bits=7)
    assert result["unrounded_overlap"]
    assert not result["reference_contained"]
    assert result["status"] == "NUMERICALLY_UNRESOLVED"


def test_real_source_checks_detect_missing_prime_and_wrong_normalization():
    # Odd u=P1+P3/7 and an even high mode exercise actual reflection cancellation.
    z = [Q(0), Q(1), Q(0), Q(1, 7)]
    degrees = (4, 5, 9)
    generated, _, image, delta = _generate(z, degrees, 8, 256)
    rebuilt, _, other_image, _, _, _ = _reconstruct(z, degrees, 8, 512)
    assert image == other_image
    with ctx.workprec(512):
        for k in degrees:
            for name in COMPONENTS:
                result = _component(generated[k][name], rebuilt[k][name])
                assert result["status"] == "PASS", (k, name)
        assert generated[4]["sum_truncated"].contains(0)
        assert rebuilt[4]["sum_truncated"].contains(0)
        assert not rebuilt[5]["P3"].contains(0)
        assert _component(arb(0), rebuilt[5]["P3"])["status"] == "SOURCE_PROOF_GAP"
        raw_instead_of_normalized = generated[5]["P3"]/(arb(11)/2).sqrt()
        assert _component(raw_instead_of_normalized, rebuilt[5]["P3"])["status"] == "SOURCE_PROOF_GAP"
        # A nonzero retained residual image is not replaced by a zero high action.
        assert not rebuilt[5]["R32"].contains(0)
        assert delta > 0
