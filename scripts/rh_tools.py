"""Numerical helpers for the Riemann-conjecture research repo.

The core prime/Laguerre routines remain standard-library based for reproducibility.
Selected research helpers may use dependencies pinned by the project environment;
in particular, zeta-zero evaluation uses mpmath. Decimal is used where cancellation
can be severe, while binary64 helpers are reserved for exploratory diagnostics.
"""

from __future__ import annotations

from decimal import Decimal, localcontext
from math import exp, isfinite, log, sqrt
from typing import Callable, Iterable


def laguerre_decimal_sequence(max_degree: int, alpha: int, x: Decimal) -> list[Decimal]:
    """Return L_0^(alpha)(x) ... L_max_degree^(alpha)(x) via three-term recurrence."""
    if max_degree < 0:
        raise ValueError("max_degree must be nonnegative")
    if alpha < 0:
        raise ValueError("alpha must be a nonnegative integer")
    one = Decimal(1)
    values = [one]
    if max_degree == 0:
        return values
    values.append(Decimal(1 + alpha) - x)
    for k in range(1, max_degree):
        # (k+1)L_{k+1} = (2k+1+alpha-x)L_k - (k+alpha)L_{k-1}
        numerator = (Decimal(2 * k + 1 + alpha) - x) * values[k]
        numerator -= Decimal(k + alpha) * values[k - 1]
        values.append(numerator / Decimal(k + 1))
    return values


def laguerre_float(degree: int, alpha: int, x: float) -> float:
    """Evaluate L_degree^(alpha)(x) by recurrence using binary64 arithmetic."""
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if degree == 0:
        return 1.0
    prev = 1.0
    cur = 1.0 + alpha - x
    if degree == 1:
        return cur
    for k in range(1, degree):
        nxt = ((2.0 * k + 1.0 + alpha - x) * cur - (k + alpha) * prev) / (k + 1.0)
        prev, cur = cur, nxt
    return cur


def primes_up_to(limit: int) -> list[int]:
    """Simple bytearray sieve."""
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    end = int(limit**0.5)
    for p in range(2, end + 1):
        if sieve[p]:
            start = p * p
            sieve[start : limit + 1 : p] = b"\x00" * (((limit - start) // p) + 1)
    return [i for i in range(2, limit + 1) if sieve[i]]


def von_mangoldt_prime_powers(limit: int, precision: int = 50) -> list[tuple[int, Decimal]]:
    """Return sorted (m, Lambda(m)) for prime powers m <= limit.

    Lambda(p^k) = log(p). Decimal.ln() is used under the requested precision.
    """
    if limit < 2:
        return []
    items: list[tuple[int, Decimal]] = []
    _validate_decimal_precision(precision)
    with localcontext() as ctx:
        ctx.prec = precision
        for p in primes_up_to(limit):
            lp = Decimal(p).ln()
            power = p
            while power <= limit:
                items.append((power, +lp))
                if power > limit // p:
                    break
                power *= p
    items.sort(key=lambda item: item[0])
    return items


def pole_parameters(s0: Decimal) -> tuple[Decimal, Decimal]:
    """Return A=2s0-1 and q=-s0/(s0-1)."""
    if s0 <= 1:
        raise ValueError("s0 must be > 1")
    one = Decimal(1)
    return Decimal(2) * s0 - one, -s0 / (s0 - one)


def pole_term(n: int, q: Decimal) -> Decimal:
    if n < 1:
        raise ValueError("n must be >= 1")
    return Decimal(1) - q**n


def nth_root_abs(value: Decimal, n: int) -> Decimal:
    """Return |value|^(1/n), with 0 mapped to 0."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    if not value:
        return Decimal(0)
    return (abs(value).ln() / Decimal(n)).exp()


def _validate_decimal_precision(precision: int) -> None:
    if isinstance(precision, bool) or not isinstance(precision, int) or precision < 1:
        raise ValueError("precision must be a positive integer")


def prime_trace_snapshots(
    *,
    s0: Decimal,
    n_max: int,
    cutoffs: Iterable[int],
    precision: int = 50,
) -> dict[int, list[Decimal]]:
    """Compute truncated P_n(X) snapshots at requested cutoffs.

    P_n(X)=A sum_{m<=X} Lambda(m)m^-s0 L_{n-1}^{(1)}(A log m).
    The returned sequence at each cutoff is indexed by n-1.
    """
    _validate_decimal_precision(precision)
    cuts = sorted(set(int(c) for c in cutoffs))
    if not cuts or cuts[0] < 2:
        raise ValueError("cutoffs must contain integers >= 2")
    if n_max < 1:
        raise ValueError("n_max must be >= 1")
    max_cutoff = cuts[-1]
    items = von_mangoldt_prime_powers(max_cutoff, precision=precision)
    snapshots: dict[int, list[Decimal]] = {}
    totals = [Decimal(0) for _ in range(n_max)]
    cut_index = 0

    with localcontext() as ctx:
        ctx.prec = precision
        A, _ = pole_parameters(s0)
        for m, lam in items:
            while cut_index < len(cuts) and m > cuts[cut_index]:
                snapshots[cuts[cut_index]] = [+v for v in totals]
                cut_index += 1
            logm = Decimal(m).ln()
            x = A * logm
            lag = laguerre_decimal_sequence(n_max - 1, 1, x)
            weight = A * lam * (Decimal(m) ** (-s0))
            for idx in range(n_max):
                totals[idx] += weight * lag[idx]
        while cut_index < len(cuts):
            snapshots[cuts[cut_index]] = [+v for v in totals]
            cut_index += 1
    return snapshots


def composite_simpson(func: Callable[[float], float], a: float, b: float, steps: int) -> float:
    """Composite Simpson integration with an even number of steps."""
    if a == b:
        return 0.0
    if b < a:
        return -composite_simpson(func, b, a, steps)
    if steps < 2:
        steps = 2
    if steps % 2:
        steps += 1
    h = (b - a) / steps
    total = func(a) + func(b)
    for i in range(1, steps):
        total += (4.0 if i % 2 else 2.0) * func(a + i * h)
    return total * h / 3.0


def density_kernel(n: int, s0: float, t: float) -> float:
    """Continuous prime-density kernel e^{-p t} L_{n-1}^{(1)}(t).

    After t=A log x, the pole/main-density integral is integral_0^inf of
    this function, with p=(s0-1)/(2s0-1).
    """
    if n < 1 or s0 <= 1.0 or t < 0.0:
        raise ValueError("require n>=1, s0>1, t>=0")
    A = 2.0 * s0 - 1.0
    p = (s0 - 1.0) / A
    lag = laguerre_float(n - 1, 1, t)
    value = exp(-p * t) * lag
    if not isfinite(value):
        raise OverflowError("density kernel overflowed binary64")
    return value


def t_from_m(m: int, s0: float) -> float:
    if isinstance(m, bool) or not isinstance(m, int) or m < 1 or s0 <= 1.0:
        raise ValueError("require integer m>=1 and s0>1")
    return (2.0 * s0 - 1.0) * log(m)


def turning_u(n: int, t: float) -> float:
    """Return u=t/(4n), the DLMF turning-scale variable for L_{n-1}^{(1)}."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    return t / (4.0 * n)


def get_zeta_zeros(count: int, dps: int = 25) -> list[float]:
    """Numerically evaluate the first `count` non-trivial zero ordinates.

    Zeros are indexed from k=1 and evaluated with ``mpmath.zetazero`` at the
    requested working precision. Returned floats are numerical research values,
    not certificates of zero existence or location.
    """
    if count < 1:
        return []

    import mpmath
    if isinstance(dps, bool) or not isinstance(dps, int) or dps < 1:
        raise ValueError("dps must be a positive integer")


    old_dps = mpmath.mp.dps
    try:
        mpmath.mp.dps = dps
        return [float(mpmath.im(mpmath.zetazero(k))) for k in range(1, count + 1)]
    finally:
        mpmath.mp.dps = old_dps


def small_u_stationary_t_from_gamma(gamma: float, n: int, s0: float) -> float:
    """Small-u Bessel-phase diagnostic t ~= n A^2/gamma^2.

    This matches d/dt[2 sqrt(n t)] to gamma/A. It is an approximation associated
    with the small-u/fixed-argument Bessel phase and MUST NOT be treated as the
    uniform stationary-phase map for an arbitrary fixed 0<u<1. A-005 is tasked
    with deriving the uniform pre-turning phase before any such generalization.
    """
    if gamma <= 0.0 or n < 1 or s0 <= 1.0:
        raise ValueError("require gamma > 0, n >= 1, s0 > 1")
    A = 2.0 * s0 - 1.0
    return float(n) * (A * A) / (gamma * gamma)


def small_u_stationary_u_from_gamma(gamma: float, s0: float) -> float:
    """Small-u diagnostic u ~= A^2/(4 gamma^2), derived from t/(4n)."""
    if gamma <= 0.0 or s0 <= 1.0:
        raise ValueError("require gamma > 0, s0 > 1")
    A = 2.0 * s0 - 1.0
    return (A * A) / (4.0 * gamma * gamma)


def gamma_from_small_u_stationary_u(u: float, s0: float) -> float:
    """Algebraic inverse of ``small_u_stationary_u_from_gamma`` only."""
    if u <= 0.0 or s0 <= 1.0:
        raise ValueError("require u > 0, s0 > 1")
    A = 2.0 * s0 - 1.0
    return A / (2.0 * sqrt(u))


def laguerre_uniform_xi(u: float) -> float:
    """DLMF pre-turning Laguerre phase coordinate xi(u), 0 <= u <= 1."""
    if u < 0.0 or u > 1.0:
        raise ValueError("require 0 <= u <= 1")
    return 0.5 * (sqrt(u * (1.0 - u)) + __import__("math").asin(sqrt(u)))


def uniform_preturning_stationary_u_from_gamma(gamma: float, s0: float) -> float:
    """Uniform pre-turning stationary coordinate u_gamma=A^2/(A^2+4 gamma^2).

    Derived from the DLMF Bessel phase 4n*xi(u) for L_(n-1)^(1)(4nu),
    by matching xi'(u)=gamma/A for the stationary branch.
    """
    if gamma <= 0.0 or s0 <= 1.0:
        raise ValueError("require gamma > 0, s0 > 1")
    A = 2.0 * s0 - 1.0
    return (A * A) / (A * A + 4.0 * gamma * gamma)


def uniform_preturning_stationary_t_from_gamma(gamma: float, n: int, s0: float) -> float:
    """Return t_gamma=4n*u_gamma for the uniform pre-turning phase."""
    if n < 1:
        raise ValueError("require n >= 1")
    return 4.0 * n * uniform_preturning_stationary_u_from_gamma(gamma, s0)


def gamma_from_uniform_preturning_u(u: float, s0: float) -> float:
    """Inverse of the uniform pre-turning stationary map."""
    if u <= 0.0 or u >= 1.0 or s0 <= 1.0:
        raise ValueError("require 0 < u < 1, s0 > 1")
    A = 2.0 * s0 - 1.0
    return 0.5 * A * sqrt((1.0 - u) / u)


def critical_cayley_phase_per_n(gamma: float, s0: float) -> float:
    """Principal phase of z_rho^(-1) for rho=1/2+i gamma, gamma>0."""
    if gamma <= 0.0 or s0 <= 1.0:
        raise ValueError("require gamma > 0, s0 > 1")
    from math import atan

    A = 2.0 * s0 - 1.0
    return -2.0 * atan(A / (2.0 * gamma))
