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

from flint import arb, ctx, fmpq, fmpq_poly

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
    """Legendre coefficients in t=(x-center)/radius on one strict cell."""

    lower: arb
    upper: arb
    legendre_coefficients: tuple[arb, ...]


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


def _legendre_expansions(polys: Sequence[Sequence[Fraction]]) -> tuple[tuple[fmpq, ...], ...]:
    """Convert any exact polynomial to global Legendre coefficients over Q."""
    exact = _exact_polynomials(polys)
    degree = max(poly.degree() for poly in exact)
    canonical = [fmpq_poly([1])]
    if degree >= 1:
        x = fmpq_poly([0, 1])
        canonical.append(x)
        for k in range(1, degree):
            canonical.append(((2 * k + 1) * x * canonical[-1] - k * canonical[-2])
                             * fmpq(1, k + 1))
    expansions = []
    for poly in exact:
        coefficients = [fmpq(0) for _ in range(poly.degree() + 1)]
        remaining = poly
        while remaining.degree() >= 0:
            k = remaining.degree()
            coefficient = remaining[k] / canonical[k][k]
            coefficients[k] = coefficient
            remaining = remaining - canonical[k] * coefficient
        expansions.append(tuple(coefficients))
    return tuple(expansions)


def _affine_legendre(degree: int, center: arb, radius: arb) -> tuple[tuple[arb, ...], ...]:
    """Enclose L_k(center+radius*t) directly in the Legendre basis of t."""
    table = [(arb(1),)]
    if degree >= 1:
        table.append((center, radius))
    for k in range(1, degree):
        previous, older = table[-1], table[-2]
        multiplied = [arb(0) for _ in range(k + 2)]
        for j, value in enumerate(previous):
            multiplied[j] += center * value
            multiplied[j + 1] += radius * value * (j + 1) / (2 * j + 1)
            if j:
                multiplied[j - 1] += radius * value * j / (2 * j + 1)
        table.append(tuple(((2 * k + 1) * value - (k * older[j] if j < len(older) else 0))
                           / (k + 1) for j, value in enumerate(multiplied)))
    return tuple(table)


def _local_basis(expansions: Sequence[Sequence[fmpq]], table: Sequence[Sequence[arb]]) -> tuple[tuple[arb, ...], ...]:
    transformed = []
    for coefficients in expansions:
        occupied = [(k, value) for k, value in enumerate(coefficients) if value]
        if len(occupied) == 1 and occupied[0][1] == 1:
            transformed.append(tuple(table[occupied[0][0]]))
            continue
        values = [arb(0) for _ in coefficients]
        for k, coefficient in occupied:
            scale = arb(coefficient)
            for j, value in enumerate(table[k]):
                values[j] += scale * value
        transformed.append(tuple(values))
    return tuple(transformed)


def _translation_partition(terms: Sequence[PrimePowerTerm]) -> tuple[arb, ...]:
    term_ids = [term.m for term in terms]
    if term_ids != sorted(term_ids) or len(term_ids) != len(set(term_ids)):
        raise ValueError("prime-power terms must be unique and sorted by m")
    if len({term.support for term in terms}) > 1:
        raise ValueError("prime-power terms must share one exact rational support")
    return _sorted_breakpoints(terms) if terms else (arb(-1), arb(1))


def _combined_local_images(
    expansions: Sequence[Sequence[fmpq]],
    terms: Sequence[PrimePowerTerm],
    breakpoints: Sequence[arb],
) -> tuple[tuple[PiecewisePolynomial, ...], ...]:
    degree = max(len(coefficients) for coefficients in expansions) - 1
    images: list[list[PiecewisePolynomial]] = [[] for _ in expansions]
    for lower, upper in zip(breakpoints[:-1], breakpoints[1:], strict=True):
        center, radius = (lower + upper) / 2, (upper - lower) / 2
        combined = [[arb(0) for _ in coefficients] for coefficients in expansions]
        active = False
        for term in terms:
            for before, boundary, shift in (
                (True, 1 - term.tau, term.tau),
                (False, -1 + term.tau, -term.tau),
            ):
                if not _activity(center, boundary, before=before, term=term):
                    continue
                active = True
                translated = _local_basis(expansions, _affine_legendre(degree, center + shift, radius))
                for values, coefficients in zip(combined, translated, strict=True):
                    for k, value in enumerate(coefficients):
                        values[k] -= term.coefficient * value
        for pieces, values in zip(images, combined, strict=True):
            pieces.append(PiecewisePolynomial(lower, upper, tuple(values) if active else ()))
    return tuple(tuple(pieces) for pieces in images)


def combined_piecewise_images(
    polys: Sequence[Sequence[Fraction]],
    terms: Sequence[PrimePowerTerm],
    prec: int = 256,
) -> tuple[tuple[arb, ...], tuple[tuple[PiecewisePolynomial, ...], ...]]:
    """Apply combined P in cell-local Legendre coordinates, summing before square.

    Piece coefficients describe t=(x-(lower+upper)/2)/((upper-lower)/2).
    An empty coefficient tuple is the zero image on an inactive cell.
    """
    if not polys:
        raise ValueError("at least one basis polynomial is required")
    if prec < 32:
        raise ValueError("prec must be at least 32 bits")
    expansions = _legendre_expansions(polys)
    with ctx.workprec(prec):
        breakpoints = _translation_partition(terms)
        return breakpoints, _combined_local_images(expansions, terms, breakpoints)


def _zero_matrix(n: int) -> ArbMatrix:
    return [[arb(0) for _ in range(n)] for _ in range(n)]


def _legendre_inner(left: Sequence[arb], right: Sequence[arb], weights: Sequence[arb]) -> arb:
    # Different degrees are implicitly zero-padded in this diagonal norm sum.
    return sum((a * b * weight for a, b, weight in zip(left, right, weights)), arb(0))


def _low_matrix_from_images(
    expansions: Sequence[Sequence[fmpq]],
    images: Sequence[Sequence[PiecewisePolynomial]],
    breakpoints: Sequence[arb],
    parities: Sequence[int | None],
) -> ArbMatrix:
    n = len(expansions)
    out = _zero_matrix(n)
    degree = max(len(coefficients) for coefficients in expansions) - 1
    weights = tuple(arb(2) / (2 * k + 1) for k in range(degree + 1))
    for cell, (lower, upper) in enumerate(zip(breakpoints[:-1], breakpoints[1:], strict=True)):
        if all(not image[cell].legendre_coefficients for image in images):
            continue
        center, radius = (lower + upper) / 2, (upper - lower) / 2
        basis = _local_basis(expansions, _affine_legendre(degree, center, radius))
        for i in range(n):
            for j in range(i, n):
                if not _opposite_parity(parities[i], parities[j]):
                    out[i][j] += radius * _legendre_inner(basis[i], images[j][cell].legendre_coefficients, weights)
    for i in range(n):
        for j in range(i):
            out[i][j] = out[j][i]
    return out


def _operator_square_matrix_from_images(
    images: Sequence[Sequence[PiecewisePolynomial]],
    breakpoints: Sequence[arb],
    parities: Sequence[int | None],
) -> ArbMatrix:
    n = len(images)
    out = _zero_matrix(n)
    degree = max(len(piece.legendre_coefficients) for image in images for piece in image)
    weights = tuple(arb(2) / (2 * k + 1) for k in range(degree))
    for cell, (lower, upper) in enumerate(zip(breakpoints[:-1], breakpoints[1:], strict=True)):
        radius = (upper - lower) / 2
        for i in range(n):
            left = images[i][cell].legendre_coefficients
            if not left:
                continue
            for j in range(i, n):
                if not _opposite_parity(parities[i], parities[j]):
                    out[i][j] += radius * _legendre_inner(left, images[j][cell].legendre_coefficients, weights)
    for i in range(n):
        for j in range(i):
            out[i][j] = out[j][i]
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
    if not polys:
        raise ValueError("at least one basis polynomial is required")
    norms = _orthogonal_basis_norms(polys)
    expansions = _legendre_expansions(polys)
    with ctx.workprec(prec):
        breakpoints = _translation_partition(terms)
        images = _combined_local_images(expansions, terms, breakpoints)
        parities = _polynomial_parities(polys)
        p_matrix = _low_matrix_from_images(expansions, images, breakpoints, parities)
        p_squared_matrix = _operator_square_matrix_from_images(images, breakpoints, parities)
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
