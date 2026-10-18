"""Scoped SYS-6.2 regression: research scalar gate and mixed-Gram diagnostics only."""
from fractions import Fraction
import math

import pytest

from scripts.weil_support_scaling_scout import scout_support
from scripts.weil_combined_scaling_profile import research_profile


def test_scalar_budget_requires_more_legendre_modes_with_support():
    sizes = []
    for support, expected_terms in (
        (Fraction(11,20), [2,3]),
        (Fraction(3,5), [2,3]),
        (Fraction(13,20), [2,3]),
        (Fraction(69,100), [2,3]),
        (Fraction(7,10), [2,3,4]),
    ):
        r = scout_support(support, (128,192), precision=256)
        assert r["active_terms"] == expected_terms
        assert r["role"] == "rigorous_arb_scalar_complement_only_no_schur_no_theorem"
        sizes.append(r["minimal_N_for_positive_conservative_mu"])
        n = sizes[-1]
        low = scout_support(support, (n-1,n),precision=256)["sampled_dimensions"]
        assert low[0]["mu_certified_positive"] is False
        assert low[0]["mu_certified_negative"] is True
        assert low[1]["mu_certified_positive"] is True
    assert sizes == [109,160,238,331,624]


def test_baseline_mu_matches_independently_retained_target():
    r = scout_support(Fraction(11,20),(192,),precision=256)
    mu = r["sampled_dimensions"][0]
    assert mu["mu_certified_positive"] is True
    assert abs(mu["mu_lower_decimal_display"] - .5662083067859621) < 1e-12


@pytest.mark.parametrize("support,n", [(Fraction(0),4), (Fraction(3,2),4), (Fraction(11,20),1)])
def test_combined_profile_rejects_invalid_ranges(support,n):
    with pytest.raises(ValueError):
        research_profile(support,n,256)


def test_combined_gram_diagnostic_only_and_trace_identity():
    r = research_profile(Fraction(11,20), 4, 256)
    assert r["role"] == "research_only_arb_truncated_image_gram_diagnostics"
    assert r["active_terms"] == [2,3]
    assert math.isfinite(r["combined_to_separated_trace_ratio_display"])
    assert r["gram_max_width_display"] >= 0
    assert r["normalized_truncated_combined_gram_trace_display"] == pytest.approx(
        r["normalized_truncated_separate_gram_trace_display"] +
        r["normalized_mixed_cross_trace_display"], abs=1e-11)
