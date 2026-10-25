"""New-window arithmetic, signed-pole and complete-grid enclosure regressions."""
from fractions import Fraction as Q

from flint import arb, ctx
import pytest

from scripts import weil_m4_fourier_matrix as source


def test_constant_image_square_keeps_four_and_central_two_pair(monkeypatch):
    monkeypatch.setattr(source,'N',4)
    with ctx.workprec(256):
        p,square,_=source.arithmetic()
        terms=source.enumerate_active_prime_power_terms(3,4,prec=256)
        assert [term.m for term in terms]==[2,3,4]
        assert terms[-1].coefficient.overlaps(arb(2).log()/2)
        expected_low=-2*sum((term.coefficient*(2-term.tau) for term in terms),arb(0))
        same_sign=2*sum((a.coefficient*b.coefficient*(2-max(a.tau,b.tau))
                         for a in terms for b in terms),arb(0))
        central=2*terms[0].coefficient**2*(2-2*terms[0].tau)
        assert central>0
        assert p[0][0,0].overlaps(expected_low)
        assert not p[0][0,0].overlaps(expected_low/2)
        assert square[0][0,0].overlaps(same_sign+central)
        assert not square[0][0,0].overlaps(same_sign)


@pytest.mark.parametrize('argument',[Q(1,1024),Q(191)])
def test_entire_transform_at_small_and_expanded_arguments(argument):
    with ctx.workprec(256):
        w=source.qa(argument)
        actual=source.bessel_vector(w,count=6)
        spherical=[w.sin()/w,(w.sin()/w-w.cos())/w]
        for degree in range(1,5):
            spherical.append((2*degree+1)*spherical[-1]/w-spherical[-2])
        for degree,expected in enumerate(spherical):
            assert actual[degree].overlaps(2*(-1 if (degree//2)%2 else 1)*expected)


def test_odd_pole_stays_negative_with_physical_scaling(monkeypatch):
    monkeypatch.setattr(source,'N',4)
    with ctx.workprec(256):
        even,odd=source.pole()
        t=source.qa(Q(3,4));alpha=t/2
        constant=2*alpha.sinh()/alpha
        linear=2*(alpha*alpha.cosh()-alpha.sinh())/alpha**2
        assert even[0,0].overlaps(2*t*constant**2)
        assert odd[0,0].overlaps(-2*t*linear**2)
        assert odd[0,0]<0


def test_analytic_band_radius_rounds_outward_on_non_square_mass():
    error=Q(1,1<<source.BITS)
    triangle=[[[0,0],[0,0],[0,0]],[[0,0],[0,0]],[[0,0]]]
    source.inflate_band(triangle,error)
    assert triangle[0][0]==[-2,2]
    assert triangle[0][1]==[0,0]
    assert triangle[0][2]==[-1,1]
    assert source.integer_band_radius(0,1,error)==2
