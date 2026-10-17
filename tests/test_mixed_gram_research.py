"""Focused checks for research-only mixed Gram images and Loewner controls."""
from __future__ import annotations

from fractions import Fraction

import pytest
from flint import arb, ctx

from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.legendre_schur import legendre_polynomials, legendre_norm_sq
from scripts.cert.multi_prime_legendre_schur import (
    _potential_matrices, assemble_multi_prime_schur,
    _residual_truncation_operator,
)
from scripts.cert.mixed_gram_research import (
    _rational_order_bounds, _vr_image_matrix,
    assemble_truncated_mixed_gram, logarithmic_cell_moments,
    rigorous_full_gram_upper, rigorous_combined_schur_lower,
)
from scripts.cert.prime_power_terms import _exact_polynomials


def test_log_cell_moments_full_and_split_against_independent_grouped_moments():
    with ctx.workprec(256):
        for n in range(7):
            polys = [[Fraction(1)], [Fraction(0)] * n + [Fraction(1)]]
            reference = _potential_matrices(polys, 256)[0][0][1]
            whole = logarithmic_cell_moments(arb(-1), arb(1), n)[n]
            pivot = arb(1)/3
            split = (logarithmic_cell_moments(arb(-1), pivot, n)[n]
                     + logarithmic_cell_moments(pivot, arb(1), n)[n])
            assert whole.overlaps(reference)
            assert split.overlaps(reference)


def test_cell_endpoint_and_branch_guards():
    with ctx.workprec(128):
        with pytest.raises(ValueError):
            logarithmic_cell_moments(arb(-1), arb("1 +/- 0.00001"), 2)
        with pytest.raises(ValueError):
            logarithmic_cell_moments(arb(1), arb(-1), 2)
        with pytest.raises(ValueError):
            logarithmic_cell_moments(arb(-1), arb(1), -1)


def test_ordered_cross_terms_and_parity():
    r = assemble_truncated_mixed_gram(n=5, prec=192, residual_order=12)
    assert [t.m for t in r["active_terms"]] == [2,3]
    for name in ("VP","VRk","PRk"):
        assert not r[name][0][0].contains(0), name
        for i in range(5):
            for j in range(5):
                if (i-j)%2:
                    assert r[name][i][j].contains(0), (name,i,j)
    for i in range(5):
        for j in range(5):
            assert r["Gk"][i][j].overlaps(r["Gk"][j][i])


def test_vr_agrees_with_independent_existing_potential_assembly():
    with ctx.workprec(192):
        polys=legendre_polynomials(3)
        images,_,_,_=_residual_truncation_operator(
            polys, 12, 192, 11,20)
        exact=_exact_polynomials(polys)
        mixed=_vr_image_matrix(exact,images)
        for i,j in ((0,0),(0,2),(1,3),(2,2)):
            p=[Fraction(int(x.p),int(x.q)) for x in exact[i].coeffs()]
            q=[Fraction(int(x.p),int(x.q)) for x in images[j].coeffs()]
            reference=_potential_matrices([p,q],192)[0][0][1]
            assert mixed[i][j].overlaps(reference)


def test_vp_constant_matches_independent_even_shift_support_identity():
    r=assemble_truncated_mixed_gram(n=1,prec=192,residual_order=10)
    with ctx.workprec(192):
        expected=arb(0)
        for term in r["active_terms"]:
            moment=logarithmic_cell_moments(term.tau-1,arb(1),0)[0]
            expected -= 2*term.coefficient*moment
        assert r["VP"][0][0].overlaps(expected)


def test_combined_gram_dominates_finite_legendre_projection():
    n=3
    r=assemble_truncated_mixed_gram(n=n,prec=192,residual_order=12)
    large=assemble_multi_prime_schur(n=8,prec=192,residual_order=12,
                                     require_positive_mu=False,support_num=11,support_den=20)
    with ctx.workprec(192):
        projected=sum(
            (large["A"][k][0]**2 / (arb(2)/(2*k+1))
             for k in range(n,8)),arb(0))
        assert r["Gk"][0][0].lower()>projected.upper()


def test_exact_rational_row_radius_is_a_loewner_majorant():
    with ctx.workprec(64):
        g=[[arb("1 +/- 0.01"),arb("0.2 +/- 0.02")],
           [arb("0.2 +/- 0.02"),arb("2 +/- 0.01")]]
        lo,up=_rational_order_bounds(g)
        exact=[[Fraction(1),Fraction(1,5)],[Fraction(1,5),Fraction(2)]]
        for z in ((Fraction(1),Fraction(0)),(Fraction(1),Fraction(1)),
                  (Fraction(1),Fraction(-7,3)),(Fraction(2),Fraction(3))):
            def quad(a):
                return sum(z[i]*a[i][j]*z[j] for i in range(2) for j in range(2))
            assert quad(lo)<=quad(exact)<=quad(up)


def test_full_residual_majorant_uses_unnormalized_legendre_diagonal():
    with ctx.workprec(160):
        r=assemble_truncated_mixed_gram(n=3,prec=160,residual_order=12)
        bound=rigorous_full_gram_upper(r,eta=Fraction(1,100))
        low,up=_rational_order_bounds(r["Gk"])
        # Off-diagonal: no residual scalar. Diagonal: residual * d_i.
        assert bound["upper"][0][1]==Fraction(101,100)*up[0][1]
        diagonal=[bound["upper"][i][i]-Fraction(101,100)*up[i][i]
                  for i in range(3)]
        assert diagonal[1]*3==diagonal[0]
        assert diagonal[2]*5==diagonal[0]




def test_pr_mixed_against_independent_cell_local_legendre_inner_products():
    # This computes the same ordered pairing using a different representation:
    # certified combined piecewise images, an affine Legendre transform of R_K,
    # and exact local Legendre norms, rather than shifted global monomials.
    from scripts.cert.prime_power_terms import (
        _legendre_expansions, _affine_legendre, _local_basis,
        _legendre_inner, assemble_active_prime_power_operator,
    )
    with ctx.workprec(192):
        polys=legendre_polynomials(4)
        arithmetic=assemble_active_prime_power_operator(polys,11,20,192)
        images,_,_,_=_residual_truncation_operator(polys,12,192,11,20)
        residual_polys=[
            [Fraction(int(v.p),int(v.q)) for v in q.coeffs()]
            for q in images
        ]
        expansions=_legendre_expansions(residual_polys)
        degree=max(q.degree() for q in images)
        rmat=assemble_truncated_mixed_gram(n=5,prec=192,residual_order=12)
        for i,j in ((0,0),(0,2),(1,3),(2,0),(4,4)):
            reference=arb(0)
            for cell,(a,b) in enumerate(zip(arithmetic.breakpoints[:-1],
                                              arithmetic.breakpoints[1:],strict=True)):
                center,radius=(a+b)/2,(b-a)/2
                table=_affine_legendre(degree,center,radius)
                rlocal=_local_basis(expansions,table)[j]
                pcell=arithmetic.images[i][cell].legendre_coefficients
                weights=[arb(2)/(2*k+1) for k in range(max(len(pcell),len(rlocal)))]
                reference+=radius*_legendre_inner(pcell,rlocal,weights)
            assert rmat["PRk"][i][j].overlaps(reference), (i,j)


def test_vp_mixed_against_independent_numerical_shift_integral():
    # Independent, NONPROOF control: direct high-precision quadrature of the
    # signed shifts. Arb proofs come from the analytical cell primitives.
    import mpmath as mp
    mp.mp.dps=65
    r=assemble_truncated_mixed_gram(n=4,prec=192,residual_order=12)
    t=mp.mpf(11)/20
    def reference(i,j):
        def base(x,shift):
            return (-mp.log(1-x*x)/2*mp.legendre(i,x)
                    *mp.legendre(j,x+shift))
        total=mp.mpf("0")
        for m in (2,3):
            tau=mp.log(m)/t
            coeff=mp.log(m)/mp.sqrt(m)
            total-=coeff*(
                mp.quad(lambda x: base(x,tau),[-1,1-tau])
                +mp.quad(lambda x: base(x,-tau),[-1+tau,1])
            )
        return total
    for i,j in ((0,0),(0,2),(1,1),(2,0)):
        lo,hi=arb_to_rational_enclosure(r["VP"][i][j])
        center=(lo+hi)/2
        actual=mp.mpf(center.numerator)/center.denominator
        assert abs(actual-reference(i,j)) < mp.mpf("1e-30"),(i,j)


def test_full_schur_lower_on_certified_positive_complement():
    # Empty-arithmetic control: the actual full residual is still included.
    r=assemble_truncated_mixed_gram(n=16,prec=192,residual_order=12,
                                    support_num=1,support_den=4)
    b=rigorous_combined_schur_lower(r)
    assert b["mu_lower"]>0
    assert len(b["schur_lower"])==16
    assert b["gram_majorant"]["residual_delta_upper"]>0
    for i in range(16):
        for j in range(16):
            assert b["schur_lower"][i][j]==b["schur_lower"][j][i]


def test_loewner_enclosure_fails_closed_on_bad_shapes_and_asymmetry():
    with ctx.workprec(128):
        with pytest.raises(ValueError, match="square"):
            _rational_order_bounds([])
        with pytest.raises(ValueError, match="square"):
            _rational_order_bounds([[arb(1), arb(0)], [arb(0)]])
        with pytest.raises(ValueError, match="asymmetric"):
            _rational_order_bounds(
                [[arb(1), arb(1)], [arb(-1), arb(1)]]
            )
        # A pair of different but overlapping interval enclosures of
        # the SAME symmetric entry is legal and must still enclose it.
        _, up = _rational_order_bounds(
            [[arb(1), arb("0.2 +/- 0.01")],
             [arb("0.2 +/- 0.02"), arb(1)]]
        )
        assert up[0][1] == up[1][0]


def test_young_parameter_requires_exact_positive_rational():
    r = assemble_truncated_mixed_gram(n=2, prec=128, residual_order=8)
    for eta in (0.0, 0.1, 1, "1/2", None):
        with pytest.raises(TypeError, match="exact Fraction"):
            rigorous_full_gram_upper(r, eta=eta)
    for eta in (Fraction(0), Fraction(-1, 3)):
        with pytest.raises(ValueError, match="strictly positive"):
            rigorous_full_gram_upper(r, eta=eta)
    assert rigorous_full_gram_upper(r, eta=Fraction(1, 10))["eta"] == Fraction(1, 10)


def test_enclosed_combined_gram_bounds_an_independent_tail_projection_for_vectors():
    # Compare the full truncated-image Gram with a strict finite subset of
    # its Legendre tail modes; the latter comes from the old low assembler.
    # The new finite Gram enclosure may be conservative, but its lower
    # matrix-order bound must dominate the projected directional form.
    with ctx.workprec(256):
        n, m = 4, 12
        mixed = assemble_truncated_mixed_gram(n=n, prec=256, residual_order=12)
        enlarged = assemble_multi_prime_schur(
            n=m, prec=256, residual_order=12,
            support_num=11, support_den=20, require_positive_mu=False,
        )
        lo, up = _rational_order_bounds(mixed["Gk"])
        for vector in ((1, 0, 0, 0), (1, 0, 2, 0),
                       (0, 1, 0, -1), (1, -1, 1, 1)):
            exact_lower = sum(
                Fraction(vector[i])*lo[i][j]*vector[j]
                for i in range(n) for j in range(n)
            )
            exact_upper = sum(
                Fraction(vector[i])*up[i][j]*vector[j]
                for i in range(n) for j in range(n)
            )
            projected = arb(0)
            for k in range(n, m):
                pairing = sum(
                    (enlarged["A"][k][i]*vector[i] for i in range(n)), arb(0)
                )
                projected += pairing*pairing / (arb(2)/(2*k+1))
            p_lo, p_hi = arb_to_rational_enclosure(projected)
            assert exact_upper >= p_lo
            assert exact_lower <= exact_upper
def test_research_schur_rejects_unproved_positive_complement():
    r=assemble_truncated_mixed_gram(n=2,prec=128,residual_order=8)
    with pytest.raises(ValueError,match="positive full complement"):
        rigorous_combined_schur_lower(r)
