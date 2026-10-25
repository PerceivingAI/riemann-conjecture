"""Consumer-visible normalization and entire-transform regressions."""
from fractions import Fraction as Q

from flint import arb, ctx
import pytest

from scripts import weil_fourier_minorant_matrix as source


def test_arithmetic_constant_overlap_and_combined_square(monkeypatch):
    monkeypatch.setattr(source, 'N', 4)
    with ctx.workprec(256):
        p, square, _ = source.arithmetic()
        terms = source.enumerate_active_prime_power_terms(1353, 2048, prec=256)
        expected_p = -sum((2*t.coefficient*(2-t.tau) for t in terms), arb(0))
        expected_square = 2*sum((a.coefficient*b.coefficient*(2-max(a.tau,b.tau))
                                 for a in terms for b in terms), arb(0))
        assert p[0][0,0].overlaps(expected_p)
        assert square[0][0,0].overlaps(expected_square)


@pytest.mark.parametrize('argument', [Q(1,1024), Q(169)])
def test_entire_transform_recurrence_preserves_low_modes(argument):
    with ctx.workprec(256):
        w=source.qa(argument)
        values=source.bessel_vector(w,count=6)
        exact=[w.sin()/w,(w.sin()/w-w.cos())/w]
        for n in range(1,5):
            exact.append((2*n+1)*exact[-1]/w-exact[-2])
        for n,value in enumerate(exact):
            assert values[n].overlaps(2*(-1 if (n//2)%2 else 1)*value)


def test_signed_pole_has_correct_physical_scaling(monkeypatch):
    monkeypatch.setattr(source,'N',4)
    with ctx.workprec(256):
        even,odd=source.pole()
        t=source.qa(source.T)
        alpha=t/2
        constant=2*alpha.sinh()/alpha
        linear=2*(alpha*alpha.cosh()-alpha.sinh())/alpha**2
        assert even[0,0]>0 and odd[0,0]<0
        assert even[0,0].overlaps(2*t*constant**2)
        assert odd[0,0].overlaps(-2*t*linear**2)
