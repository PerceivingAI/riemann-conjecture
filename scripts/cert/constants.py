"""Rigorous mathematical constants and rational enclosure utilities.

This module provides proven interval enclosures and exact outward rational
bounds for transcendental constants involved in the Weil positivity and
first-prime absorption machinery.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from flint import arb, ctx, fmpq


def arb_to_rational_enclosure(x: arb) -> tuple[Fraction, Fraction]:
    """Convert an Arb ball to rigorous lower and upper rational bounds.

    Let x have midpoint m and radius r, so x is the ball [m - r, m + r].
    Both m and r are represented exactly in Arb as dyadic rationals.
    This function extracts m and r as exact fmpq fractions and returns:
        (Fraction(m - r), Fraction(m + r))

    The resulting rational interval [lo, hi] strictly encloses the true
    mathematical quantity.
    """
    m_fmpq = x.mid().fmpq()
    r_fmpq = x.rad().fmpq()

    lo_fmpq = m_fmpq - r_fmpq
    hi_fmpq = m_fmpq + r_fmpq

    lo = Fraction(int(lo_fmpq.p), int(lo_fmpq.q))
    hi = Fraction(int(hi_fmpq.p), int(hi_fmpq.q))
    return lo, hi


def rational_enclosure_dict(x: arb) -> dict[str, str]:
    """Serialize an Arb ball using only exact rational endpoints."""
    lo, hi = arb_to_rational_enclosure(x)
    return {
        "lo_num": str(lo.numerator),
        "lo_den": str(lo.denominator),
        "hi_num": str(hi.numerator),
        "hi_den": str(hi.denominator),
    }


def support_T(num: int = 7, den: int = 20) -> fmpq:
    """Return the exact rational support parameter T."""
    return fmpq(num, den)


def log2_enclosure(prec: int = 256) -> arb:
    """Rigorous enclosure of log(2)."""
    with ctx.workprec(prec):
        return arb.const_log2()


def sqrt2_enclosure(prec: int = 256) -> arb:
    """Rigorous enclosure of sqrt(2)."""
    with ctx.workprec(prec):
        return arb(2).sqrt()


def pi_enclosure(prec: int = 256) -> arb:
    """Rigorous enclosure of pi."""
    with ctx.workprec(prec):
        return arb.pi()


def euler_gamma_enclosure(prec: int = 256) -> arb:
    """Rigorous enclosure of the Euler-Mascheroni constant gamma."""
    with ctx.workprec(prec):
        return arb.const_euler()


def tau_enclosure(prec: int = 256, num: int = 7, den: int = 20) -> arb:
    """Rigorous enclosure of tau = log(2) / T."""
    with ctx.workprec(prec):
        t_arb = arb(num) / arb(den)
        return arb.const_log2() / t_arb


def c2_enclosure(prec: int = 256) -> arb:
    """Rigorous enclosure of c2 = log(2) / sqrt(2)."""
    with ctx.workprec(prec):
        return arb.const_log2() / arb(2).sqrt()


def c_T_enclosure(prec: int = 256, num: int = 7, den: int = 20) -> arb:
    """Rigorous enclosure of c_T = log(2 * pi * T) + gamma."""
    with ctx.workprec(prec):
        t_arb = arb(num) / arb(den)
        two_pi_t = arb(2) * arb.pi() * t_arb
        return two_pi_t.log() + arb.const_euler()


def m0_digamma_enclosure(prec: int = 256) -> arb:
    """Rigorous enclosure of m_0 = psi(1/4) - log(pi)."""
    with ctx.workprec(prec):
        psi_fourth = (arb(1) / arb(4)).digamma()
        return psi_fourth - arb.pi().log()


def digamma_ak(k: int) -> fmpq:
    """Return exact rational a_k = k + 1/4 = (4k + 1)/4."""
    if k < 0:
        raise ValueError(f"k must be non-negative, got {k}")
    return fmpq(4 * k + 1, 4)


def get_certified_constants_bundle(prec: int = 256, num: int = 7, den: int = 20) -> dict[str, Any]:
    """Generate exact rational interval enclosures for certified constants."""
    with ctx.workprec(prec):
        log2_val = log2_enclosure(prec)
        sqrt2_val = sqrt2_enclosure(prec)
        pi_val = pi_enclosure(prec)
        gamma_val = euler_gamma_enclosure(prec)
        tau_val = tau_enclosure(prec, num, den)
        c2_val = c2_enclosure(prec)
        c_T_val = c_T_enclosure(prec, num, den)
        m0_val = m0_digamma_enclosure(prec)

        return {
            "precision_bits": prec,
            "support_T": {"num": num, "den": den, "frac": f"{num}/{den}"},
            "log2": rational_enclosure_dict(log2_val),
            "sqrt2": rational_enclosure_dict(sqrt2_val),
            "pi": rational_enclosure_dict(pi_val),
            "euler_gamma": rational_enclosure_dict(gamma_val),
            "tau": rational_enclosure_dict(tau_val),
            "c2": rational_enclosure_dict(c2_val),
            "c_T": rational_enclosure_dict(c_T_val),
            "m0_digamma": rational_enclosure_dict(m0_val),
        }
