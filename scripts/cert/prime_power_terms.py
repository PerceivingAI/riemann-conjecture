"""Generic rigorous prime-power compressed-translation operators.

This module is the additive multi-prime operator core defined by P1.  It does
not modify or depend on the frozen one-prime ``first_prime_matrices()`` path.
All support decisions and transcendental coefficients are made with Arb.  The
polynomial basis itself remains exact over :class:`fractions.Fraction`.

For an active prime power ``m=p^k`` the signed arithmetic operator is

    P_m = -Lambda(m)/sqrt(m) * S_m,

where ``S_m`` is the self-adjoint compressed translation at
``tau_m=log(m)/T`` on ``[-1, 1]``.  Each translated basis polynomial is built
piecewise on its actual support.  The active terms are summed *before*
integration; consequently the matrix of ``P^2`` obtained from the combined
images automatically contains every cross-prime term.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from itertools import count
from typing import Sequence

from flint import arb, arb_poly, ctx, fmpq, fmpq_poly

FractionPoly = list[Fraction]
ArbPoly = list[arb]
ArbMatrix = list[list[arb]]


class ThresholdIndeterminateError(ValueError):
    """Raised when Arb cannot certify a strict prime-power support decision."""


class PiecewiseTopologyError(ValueError):
    """Raised when the translation partition cannot be rigorously ordered."""


@dataclass(frozen=True)
class PrimePowerFactorization:
    """Exact integer factorization data for ``m=p^k``."""

    m: int
    prime: int
    exponent: int


@dataclass(frozen=True)
class PrimePowerTerm:
    """Rigorous constants for one active or candidate prime-power term."""

    m: int
    prime: int
    exponent: int
    log_m: arb
    support: Fraction
    precision_bits: int
    tau: arb
    von_mangoldt: arb
    coefficient: arb


@dataclass(frozen=True)
class PiecewisePolynomial:
    """One polynomial piece on a rigorously ordered interval."""

    lower: arb
    upper: arb
    coefficients: tuple[arb, ...]


@dataclass(frozen=True)
class PrimePowerOperatorAssembly:
    """Combined low-space arithmetic operator data.

    ``p_matrix`` is ``<phi_i, P phi_j>`` and ``p_squared_matrix`` is
    ``<phi_i, P^2 phi_j> = <P phi_i, P phi_j>``.  ``g_p`` is the exact
    low/tail Gram representation ``P^2 - P D^{-1} P`` for an orthogonal
    polynomial basis with diagonal norm matrix ``D``.
    """

    terms: tuple[PrimePowerTerm, ...]
    breakpoints: tuple[arb, ...]
    images: tuple[tuple[PiecewisePolynomial, ...], ...]
    norms: tuple[Fraction, ...]
    p_matrix: ArbMatrix
    p_squared_matrix: ArbMatrix
    g_p: ArbMatrix


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    limit = math.isqrt(n)
    divisor = 3
    while divisor <= limit:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def factor_prime_power(m: int) -> PrimePowerFactorization | None:
    """Return the unique ``p^k`` representation of ``m``, or ``None``.

    The implementation uses integer arithmetic only and does not delegate
    primality or factorization to a floating/numerical library.
    """
    if not isinstance(m, int):
        raise TypeError("m must be an integer")
    if m < 2:
        return None
    if _is_prime(m):
        return PrimePowerFactorization(m=m, prime=m, exponent=1)

    prime = 2 if m % 2 == 0 else None
    if prime is None:
        divisor = 3
        limit = math.isqrt(m)
        while divisor <= limit:
            if m % divisor == 0:
                prime = divisor
                break
            divisor += 2
    if prime is None:
        # The earlier primality test makes this unreachable, but fail closed if
        # integer-factorization logic is ever changed independently.
        raise RuntimeError(f"failed to factor composite integer {m}")

    remaining = m
    exponent = 0
    while remaining % prime == 0:
        remaining //= prime
        exponent += 1
    if remaining != 1:
        return None
    return PrimePowerFactorization(m=m, prime=prime, exponent=exponent)


def is_prime_power(m: int) -> bool:
    """Return whether ``m`` is a prime power, including primes (exponent 1)."""
    return factor_prime_power(m) is not None


def _validate_support(support_num: int, support_den: int) -> None:
    if not isinstance(support_num, int) or not isinstance(support_den, int):
        raise TypeError("support numerator and denominator must be integers")
    if support_num <= 0 or support_den <= 0:
        raise ValueError("support T must be a positive rational")


def _term_from_factorization(
    factorization: PrimePowerFactorization,
    support_num: int,
    support_den: int,
    prec: int,
    *,
    log_m: arb | None = None,
) -> PrimePowerTerm:
    _validate_support(support_num, support_den)
    if prec < 32:
        raise ValueError("prec must be at least 32 bits")
    with ctx.workprec(prec):
        support_exact = Fraction(support_num, support_den)
        support = arb(support_exact.numerator) / support_exact.denominator
        log_value = arb(factorization.m).log() if log_m is None else +log_m
        lambda_value = arb(factorization.prime).log()
        tau_value = log_value / support
        coefficient = lambda_value / arb(factorization.m).sqrt()
        return PrimePowerTerm(
            m=factorization.m,
            prime=factorization.prime,
            exponent=factorization.exponent,
            log_m=log_value,
            support=support_exact,
            precision_bits=prec,
            tau=tau_value,
            von_mangoldt=lambda_value,
            coefficient=coefficient,
        )


def prime_power_term(
    m: int,
    support_num: int,
    support_den: int,
    prec: int = 256,
) -> PrimePowerTerm:
    """Build rigorous ``log(m)``, ``tau_m``, ``Lambda(m)``, and ``c_m`` balls."""
    factorization = factor_prime_power(m)
    if factorization is None:
        raise ValueError(f"m={m} is not a prime power")
    return _term_from_factorization(
        factorization,
        support_num,
        support_den,
        prec,
    )


def enumerate_active_prime_power_terms(
    support_num: int,
    support_den: int,
    prec: int = 256,
) -> tuple[PrimePowerTerm, ...]:
    """Enumerate exactly the prime powers satisfying ``log(m) < 2T``.

    Prime powers are inspected in increasing integer order.  The first one
    rigorously proved to satisfy ``log(m) > 2T`` terminates the enumeration,
    since every later prime power is larger.  If the Arb intervals cannot
    establish either strict inequality at the requested precision, the
    function fails closed instead of guessing which side of the threshold the
    rational support occupies.
    """
    _validate_support(support_num, support_den)
    if prec < 32:
        raise ValueError("prec must be at least 32 bits")

    active: list[PrimePowerTerm] = []
    with ctx.workprec(prec):
        support = arb(support_num) / support_den
        threshold = 2 * support
        for m in count(2):
            factorization = factor_prime_power(m)
            if factorization is None:
                continue
            log_m = arb(m).log()
            if log_m < threshold:
                active.append(
                    _term_from_factorization(
                        factorization,
                        support_num,
                        support_den,
                        prec,
                        log_m=log_m,
                    )
                )
                continue
            if log_m > threshold:
                return tuple(active)
            raise ThresholdIndeterminateError(
                "cannot certify strict prime-power support threshold at "
                f"m={m}, T={support_num}/{support_den}, precision={prec}; "
                "increase Arb precision"
            )

    raise RuntimeError("unreachable active prime-power enumeration state")


def _arb_fraction(value: Fraction) -> arb:
    return arb(value.numerator) / value.denominator


def _arb_poly(poly: Sequence[Fraction]) -> ArbPoly:
    return [_arb_fraction(value) for value in poly]


def _arb_poly_shift(poly: Sequence[Fraction], shift: arb) -> ArbPoly:
    """Return coefficients of ``poly(x + shift)`` with rigorous Arb entries."""
    coefficients = arb_poly(_arb_poly(poly))(arb_poly([shift, 1])).coeffs()
    # Retain the coefficient shape even when Flint trims exact trailing zeros.
    coefficients.extend(arb(0) for _ in range(len(poly) - len(coefficients)))
    return coefficients


def _arb_poly_add_in_place(target: ArbPoly, source: Sequence[arb], scale: arb) -> None:
    if len(source) > len(target):
        target.extend(arb(0) for _ in range(len(source) - len(target)))
    for index, value in enumerate(source):
        target[index] += scale * value


def _integrated_product(left: arb_poly, right: arb_poly, interval: tuple[arb, arb]) -> arb:
    """Integrate the full interval product using native Arb antiderivative evaluation."""
    if not len(left) or not len(right):
        return arb(0)
    primitive = (left * right).integral()
    lower, upper = interval
    return primitive(upper) - primitive(lower)


def _exact_polynomials(polys: Sequence[Sequence[Fraction]]) -> list[fmpq_poly]:
    return [
        fmpq_poly([fmpq(value.numerator, value.denominator) for value in poly])
        for poly in polys
    ]


def _exact_inner(a: fmpq_poly, b: fmpq_poly) -> fmpq:
    primitive = (a * b).integral()
    return primitive(1) - primitive(-1)


def _polynomial_parities(polys: Sequence[Sequence[Fraction]]) -> tuple[int | None, ...]:
    """Certify reflection parity from exact coefficients, not basis indices."""
    parities: list[int | None] = []
    for poly in polys:
        occupied = {degree % 2 for degree, value in enumerate(poly) if value}
        parities.append(next(iter(occupied)) if len(occupied) == 1 else None)
    return tuple(parities)


def _opposite_parity(left: int | None, right: int | None) -> bool:
    return left is not None and right is not None and left != right


def _orthogonal_basis_norms(polys: Sequence[Sequence[Fraction]]) -> tuple[Fraction, ...]:
    exact = _exact_polynomials(polys)
    parities = _polynomial_parities(polys)
    norms: list[Fraction] = []
    for i, poly in enumerate(exact):
        norm = _exact_inner(poly, poly)
        if norm <= 0:
            raise ValueError(f"basis polynomial {i} has nonpositive exact norm")
        for j in range(i):
            if not _opposite_parity(parities[i], parities[j]) and _exact_inner(poly, exact[j]) != 0:
                raise ValueError("prime-power Gram assembly requires an exact orthogonal basis")
        norms.append(Fraction(int(norm.p), int(norm.q)))
    return tuple(norms)


def _strict_order(a: arb, b: arb, *, context: str) -> int:
    if a < b:
        return -1
    if a > b:
        return 1
    raise PiecewiseTopologyError(
        f"cannot rigorously order piecewise breakpoints ({context}); increase Arb precision"
    )


def _sorted_breakpoints(terms: Sequence[PrimePowerTerm]) -> tuple[arb, ...]:
    values: list[arb] = [arb(-1), arb(1)]
    for term in terms:
        left_end = 1 - term.tau
        right_start = -1 + term.tau
        if not (left_end > -1 and left_end < 1):
            raise PiecewiseTopologyError(
                f"cannot certify 0 < tau_{term.m} < 2 from left breakpoint"
            )
        if not (right_start > -1 and right_start < 1):
            raise PiecewiseTopologyError(
                f"cannot certify 0 < tau_{term.m} < 2 from right breakpoint"
            )
        values.extend((left_end, right_start))

    ordered: list[arb] = []
    for value in values:
        inserted = False
        for index, existing in enumerate(ordered):
            relation = _strict_order(
                value,
                existing,
                context="translation partition",
            )
            if relation < 0:
                ordered.insert(index, value)
                inserted = True
                break
        if not inserted:
            ordered.append(value)
    return tuple(ordered)


def _activity(midpoint: arb, boundary: arb, *, before: bool, term: PrimePowerTerm) -> bool:
    if midpoint < boundary:
        return before
    if midpoint > boundary:
        return not before
    direction = "left" if before else "right"
    raise PiecewiseTopologyError(
        f"cannot certify {direction} piece activity for m={term.m}; increase Arb precision"
    )


def combined_piecewise_images(
    polys: Sequence[Sequence[Fraction]],
    terms: Sequence[PrimePowerTerm],
    prec: int = 256,
) -> tuple[tuple[arb, ...], tuple[tuple[PiecewisePolynomial, ...], ...]]:
    """Apply the combined signed arithmetic operator to every basis polynomial.

    All translation breakpoints from all active terms are globally partitioned.
    On each open subinterval the correct left/right shifted polynomial pieces
    are summed.  Endpoint values are irrelevant to the quadratic form because
    they have measure zero.
    """
    if not polys:
        raise ValueError("at least one basis polynomial is required")
    if not terms:
        with ctx.workprec(prec):
            breakpoints = (arb(-1), arb(1))
            images = tuple(
                (
                    PiecewisePolynomial(
                        lower=breakpoints[0],
                        upper=breakpoints[1],
                        coefficients=tuple(arb(0) for _ in poly),
                    ),
                )
                for poly in polys
            )
            return breakpoints, images

    term_ids = [term.m for term in terms]
    if term_ids != sorted(term_ids) or len(term_ids) != len(set(term_ids)):
        raise ValueError("prime-power terms must be unique and sorted by m")

    with ctx.workprec(prec):
        breakpoints = _sorted_breakpoints(terms)
        shifted: list[list[tuple[ArbPoly, ArbPoly]]] = []
        for poly in polys:
            per_term: list[tuple[ArbPoly, ArbPoly]] = []
            for term in terms:
                plus = _arb_poly_shift(poly, term.tau)
                minus = _arb_poly_shift(poly, -term.tau)
                per_term.append((plus, minus))
            shifted.append(per_term)
        partition = tuple(zip(breakpoints[:-1], breakpoints[1:], strict=True))
        activities = []
        for lower, upper in partition:
            midpoint = (lower + upper) / 2
            activities.append(tuple(
                (
                    _activity(midpoint, 1 - term.tau, before=True, term=term),
                    _activity(midpoint, -1 + term.tau, before=False, term=term),
                    -term.coefficient,
                )
                for term in terms
            ))

        all_images: list[tuple[PiecewisePolynomial, ...]] = []
        for basis_index, poly in enumerate(polys):
            pieces: list[PiecewisePolynomial] = []
            for cell_index, (lower, upper) in enumerate(partition):
                coefficients = [arb(0) for _ in poly]
                for term_index, (plus_active, minus_active, scale) in enumerate(activities[cell_index]):
                    plus_poly, minus_poly = shifted[basis_index][term_index]
                    if plus_active:
                        _arb_poly_add_in_place(coefficients, plus_poly, scale)
                    if minus_active:
                        _arb_poly_add_in_place(coefficients, minus_poly, scale)
                pieces.append(
                    PiecewisePolynomial(
                        lower=lower,
                        upper=upper,
                        coefficients=tuple(coefficients),
                    )
                )
            all_images.append(tuple(pieces))
        return breakpoints, tuple(all_images)


def _zero_matrix(n: int) -> ArbMatrix:
    return [[arb(0) for _ in range(n)] for _ in range(n)]


def _low_matrix_from_images(
    basis: Sequence[arb_poly],
    images: Sequence[Sequence[arb_poly]],
    intervals: Sequence[tuple[arb, arb]],
    parities: Sequence[int | None],
) -> ArbMatrix:
    n = len(basis)
    out = _zero_matrix(n)
    for i in range(n):
        for j in range(i, n):
            # Reflection commutes with every signed left+right translation.
            if _opposite_parity(parities[i], parities[j]):
                continue
            value = arb(0)
            for image, interval in zip(images[j], intervals, strict=True):
                value += _integrated_product(basis[i], image, interval)
            out[i][j] = out[j][i] = value
    return out


def _operator_square_matrix_from_images(
    images: Sequence[Sequence[arb_poly]],
    intervals: Sequence[tuple[arb, arb]],
    parities: Sequence[int | None],
) -> ArbMatrix:
    n = len(images)
    out = _zero_matrix(n)
    for i in range(n):
        for j in range(i, n):
            if _opposite_parity(parities[i], parities[j]):
                continue
            value = arb(0)
            for left, right, interval in zip(images[i], images[j], intervals, strict=True):
                value += _integrated_product(left, right, interval)
            out[i][j] = out[j][i] = value
    return out


def _tail_gram(
    p_matrix: ArbMatrix,
    p_squared_matrix: ArbMatrix,
    norms: Sequence[Fraction],
) -> ArbMatrix:
    n = len(p_matrix)
    out = _zero_matrix(n)
    inverse_norms = tuple(_arb_fraction(1 / norm) for norm in norms)
    for i in range(n):
        for j in range(i, n):
            low_composition = arb(0)
            for k in range(n):
                low_composition += (
                    p_matrix[i][k]
                    * p_matrix[k][j]
                    * inverse_norms[k]
                )
            value = p_squared_matrix[i][j] - low_composition
            out[i][j] = value
            out[j][i] = value
    return out


def assemble_combined_prime_power_operator(
    polys: Sequence[Sequence[Fraction]],
    terms: Sequence[PrimePowerTerm],
    prec: int = 256,
) -> PrimePowerOperatorAssembly:
    """Assemble ``P``, ``P^2``, and ``G_P`` from already-certified terms."""
    if prec < 32:
        raise ValueError("prec must be at least 32 bits")
    norms = _orthogonal_basis_norms(polys)
    if terms:
        supports = {term.support for term in terms}
        if len(supports) != 1:
            raise ValueError("prime-power terms must share one exact rational support")

    with ctx.workprec(prec):
        breakpoints, images = combined_piecewise_images(polys, terms, prec)
        basis = tuple(arb_poly(_arb_poly(poly)) for poly in polys)
        native_images = tuple(
            tuple(arb_poly(list(piece.coefficients)) for piece in image) for image in images
        )
        intervals = tuple(zip(breakpoints[:-1], breakpoints[1:], strict=True))
        parities = _polynomial_parities(polys)
        p_matrix = _low_matrix_from_images(basis, native_images, intervals, parities)
        p_squared_matrix = _operator_square_matrix_from_images(native_images, intervals, parities)
        g_p = _tail_gram(p_matrix, p_squared_matrix, norms)
        return PrimePowerOperatorAssembly(
            terms=tuple(terms),
            breakpoints=breakpoints,
            images=images,
            norms=norms,
            p_matrix=p_matrix,
            p_squared_matrix=p_squared_matrix,
            g_p=g_p,
        )


def assemble_active_prime_power_operator(
    polys: Sequence[Sequence[Fraction]],
    support_num: int,
    support_den: int,
    prec: int = 256,
) -> PrimePowerOperatorAssembly:
    """Enumerate active terms and assemble their combined operator rigorously."""
    terms = enumerate_active_prime_power_terms(
        support_num=support_num,
        support_den=support_den,
        prec=prec,
    )
    return assemble_combined_prime_power_operator(polys, terms, prec=prec)
