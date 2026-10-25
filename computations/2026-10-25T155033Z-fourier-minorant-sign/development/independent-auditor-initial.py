"""Independent full-band Fourier-minorant matrix audit, research only.

No producer imports. Reconstructs arithmetic from direct signed-shift pair
intersections, Gauss nodes with independently derived weights, finite-series
Bessel anchors and a complete operator-norm frequency quadrature remainder.
Shares Python-Flint/FLINT transcendental and root-enclosure primitives, Suzuki
v3 and C-0094, not an independent arithmetic library or theorem admission.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from math import factorial
from pathlib import Path

from flint import acb, arb, arb_mat, ctx, fmpq, fmpq_mat

ROOT = Path(__file__).resolve().parents[1]
DIMENSION = 312
SOURCE_BITS = 768
FREQUENCY_ORDER = 64
ARITHMETIC_ORDER = 313
ANCHOR_ORDER = 384
MATRIX_NAMES = {"P", "P_squared", "GP", "pole", "band", "A"}


def qarb(value: Q | int) -> arb:
    value = Q(value)
    return arb(value.numerator) / value.denominator


def qflint(value: Q | int) -> fmpq:
    value = Q(value)
    return fmpq(value.numerator, value.denominator)


def endpoints(value: arb) -> tuple[Q, Q]:
    midpoint = value.mid().fmpq()
    radius = value.rad().fmpq()
    left, right = midpoint - radius, midpoint + radius
    return Q(int(left.p), int(left.q)), Q(int(right.p), int(right.q))


def exact_q(value: object) -> Q:
    if not isinstance(value, str):
        raise ValueError("proof rational must be a string")
    result = Q(value)
    if value != str(result):
        raise ValueError("proof rational is not canonical")
    return result


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_float(value: str) -> None:
    raise ValueError(f"nonexact JSON proof number: {value}")


def decode(raw: bytes) -> dict:
    obj = json.loads(raw, object_pairs_hook=unique_object,
                     parse_float=reject_float, parse_constant=reject_float)
    if not isinstance(obj, dict):
        raise ValueError("report must be an object")
    return obj


def legendre_values(x: arb, count: int) -> list[arb]:
    if count < 1:
        return []
    values = [arb(1)]
    if count > 1:
        values.append(x)
    for degree in range(1, count - 1):
        values.append(((2 * degree + 1) * x * values[-1]
                       - degree * values[-2]) / (degree + 1))
    return values


def gauss_rule(order: int) -> tuple[list[arb], list[arb]]:
    """Native rigorous root balls; separate recurrence/derivative weights.

    Native legendre_p_root encloses the indexed exact root. Disjointness and
    range checks identify every root. The Gauss exactness theorem and FLINT's
    root primitive remain explicit common mathematical/library premises.
    """
    nodes = [arb.legendre_p_root(order, k) for k in range(order - 1, -1, -1)]
    weights = []
    previous = arb(-1)
    for node in nodes:
        if not (-1 < node < 1 and previous < node):
            raise ValueError("Gauss roots not strictly ordered in (-1,1)")
        values = legendre_values(node, order + 1)
        if arb(0) not in values[-1]:
            raise ValueError("Legendre root consistency check failed")
        derivative = order * (values[-2] - node * values[-1]) / (1 - node * node)
        weight = 2 / ((1 - node * node) * derivative * derivative)
        if not weight > 0:
            raise ValueError("nonpositive Gauss weight")
        weights.append(weight)
        previous = node
    if arb(2) not in sum(weights, arb(0)):
        raise ValueError("Gauss weights inconsistent with total mass two")
    return nodes, weights


def weighted_cross(left: list[list[arb]], right: list[list[arb]],
                   weights: list[arb]) -> arb_mat:
    if len(left) != len(right) or len(left) != len(weights):
        raise ValueError("quadrature table dimensions disagree")
    a = arb_mat([[row[i] for row in left] for i in range(DIMENSION)])
    b = arb_mat([[weight * value for value in row]
                 for row, weight in zip(right, weights)])
    return a * b


def parity_project(matrix: arb_mat) -> arb_mat:
    # Reflection commutes with P, P^2, the pole and the even band multiplier.
    for i in range(DIMENSION):
        for j in range(i + 1, DIMENSION, 2):
            matrix[i, j] = matrix[j, i] = arb(0)
    return matrix


def interval_integral(left: arb, right: arb, shift_left: arb,
                      shift_right: arb, nodes: list[arb],
                      weights: list[arb]) -> arb_mat:
    if not right > left:
        raise ValueError("nonpositive arithmetic intersection")
    center, half = (left + right) / 2, (right - left) / 2
    first, second = [], []
    for node in nodes:
        x = center + half * node
        first.append(legendre_values(x + shift_left, DIMENSION))
        second.append(legendre_values(x + shift_right, DIMENSION))
    return weighted_cross(first, second, [half * value for value in weights])


def arithmetic_matrices() -> tuple[arb_mat, arb_mat, arb_mat]:
    t = qarb(Q(1353, 2048))
    logs = {m: arb(m).log() for m in (2, 3)}
    if not (logs[3] < 2 * t < arb(4).log()
            and t < logs[2] < logs[3] < 2 * t):
        raise ValueError("independent strict prime activation window failed")
    shifts = {m: logs[m] / t for m in (2, 3)}
    coefficients = {m: -logs[m] / arb(m).sqrt() for m in (2, 3)}
    nodes, weights = gauss_rule(ARITHMETIC_ORDER)
    p = arb_mat(DIMENSION, DIMENSION)
    square = arb_mat(DIMENSION, DIMENSION)
    signed = [(m, sign) for m in (2, 3) for sign in (-1, 1)]
    for m, sign in signed:
        shift = sign * shifts[m]
        left, right = ((arb(-1), 1 - shift) if sign > 0
                       else (-1 - shift, arb(1)))
        p += coefficients[m] * interval_integral(
            left, right, arb(0), shift, nodes, weights)
    # Sum all ordered shift pairs, including both mixed-prime products.
    for m, sign in signed:
        alpha = sign * shifts[m]
        for other, other_sign in signed:
            beta = other_sign * shifts[other]
            if sign != other_sign:
                positive = alpha if sign > 0 else beta
                negative = alpha if sign < 0 else beta
                if not (1 - positive < -1 - negative):
                    raise ValueError("mixed-sign support intersection not empty")
                continue
            largest = shifts[max(m, other)]
            left, right = ((arb(-1), 1 - largest) if sign > 0
                           else (-1 + largest, arb(1)))
            square += coefficients[m] * coefficients[other] * interval_integral(
                left, right, alpha, beta, nodes, weights)
    parity_project(p)
    parity_project(square)
    mass_inverse_p = arb_mat([
        [p[i, j] * qarb(Q(2 * i + 1, 2)) for j in range(DIMENSION)]
        for i in range(DIMENSION)])
    gp = parity_project(square - p * mass_inverse_p)
    return p, square, gp


def finite_hypergeometric(n: int, w: arb, terms: int, alternating: bool) -> arb:
    """Enclose 0F1(n+3/2; +/-w^2/4) with a proven entire tail."""
    u = w * w / 4
    magnitude = u.abs_upper()
    b = qarb(Q(2 * n + 3, 2))
    term = arb(1)
    total = arb(1)
    signed_u = -u if alternating else u
    for k in range(1, terms + 1):
        term = term * signed_u / (k * (b + k - 1))
        total += term
    first = term.abs_upper() * magnitude / ((terms + 1) * (b + terms))
    ratio = magnitude / ((terms + 2) * (b + terms + 1))
    if not 0 <= ratio < 1:
        raise ValueError("hypergeometric geometric tail is not contracting")
    error = first / (1 - ratio)
    return total + arb(0, error.abs_upper())


def double_factorial_odd(n: int) -> int:
    return factorial(2 * n + 1) // (2 ** n * factorial(n))


def transform_vector(w: arb) -> list[arb]:
    if not (0 < w < 170):
        raise ValueError("frequency node argument outside strict anchor range")
    values = [arb(0) for _ in range(DIMENSION + 2)]
    for n in (DIMENSION, DIMENSION + 1):
        values[n] = (w ** n / double_factorial_odd(n)
                     * finite_hypergeometric(n, w, ANCHOR_ORDER, True))
    for n in range(DIMENSION, 0, -1):
        values[n - 1] = (2 * n + 1) * values[n] / w - values[n + 1]
    # I_n(w)=2(-i)^n j_n(w). Within each parity sector the complex
    # I_i(w)I_j(-w) product is the real outer product of these values.
    return [2 * (-1 if (n // 2) % 2 else 1) * values[n]
            for n in range(DIMENSION)]


def panels() -> list[tuple[Q, Q]]:
    edges = [Q(0), Q(1, 4), Q(1, 2), Q(1), Q(2), Q(4)]
    edges.extend(Q(value) for value in range(8, 257, 4))
    return list(zip(edges, edges[1:]))


def operator_error(order: int) -> arb:
    # Uniform 4096 digamma envelope proved in the accompanying qualification.
    t = qarb(Q(1353, 2048))
    result = arb(0)
    for left, right in panels():
        half = qarb((right - left) / 2)
        rho = 2 * half
        bound = 2 * t / arb.pi() * (2 * t * rho).exp() * 4096
        result += 8 * half * bound / (1 << (2 * order))
    return result


def band_matrix() -> tuple[arb_mat, Q]:
    nodes, weights = gauss_rule(FREQUENCY_ORDER)
    t = qarb(Q(1353, 2048))
    result = arb_mat(DIMENSION, DIMENSION)
    for left, right in panels():
        center = qarb((left + right) / 2)
        half = qarb((right - left) / 2)
        vectors, factors = [], []
        for node, weight in zip(nodes, weights):
            frequency = center + half * node
            argument = acb(qarb(Q(1, 4)), frequency / 2)
            multiplier = argument.digamma().real - arb.pi().log() - qarb(Q(7, 2))
            vectors.append(transform_vector(t * frequency))
            factors.append(t / arb.pi() * half * weight * multiplier)
        result += weighted_cross(vectors, vectors, factors)
    parity_project(result)
    error = operator_error(FREQUENCY_ORDER).abs_upper()
    _, error_upper = endpoints(error)
    for i in range(DIMENSION):
        for j in range(i, DIMENSION, 2):
            radius = error * (qarb(Q(2, 2 * i + 1))
                              * qarb(Q(2, 2 * j + 1))).sqrt()
            result[i, j] += arb(0, radius.abs_upper())
            if j != i:
                result[j, i] = result[i, j]
    return result, error_upper


def pole_matrix() -> arb_mat:
    t = qarb(Q(1353, 2048))
    s = t / 2
    values = [2 * s ** n / double_factorial_odd(n)
              * finite_hypergeometric(n, s, 128, False)
              for n in range(DIMENSION)]
    result = arb_mat(DIMENSION, DIMENSION)
    for i in range(DIMENSION):
        for j in range(i, DIMENSION, 2):
            value = 2 * t * (-1 if i % 2 else 1) * values[i] * values[j]
            result[i, j] = result[j, i] = value
    return result


def validate_triangle(value: object, name: str) -> list:
    if not isinstance(value, list) or len(value) != DIMENSION:
        raise ValueError(f"incorrect matrix dimension: {name}")
    for i, row in enumerate(value):
        if not isinstance(row, list) or len(row) != DIMENSION - i:
            raise ValueError(f"incorrect triangular shape: {name}[{i}]")
        for offset, pair in enumerate(row):
            if (not isinstance(pair, list) or len(pair) != 2
                    or any(type(v) is not int for v in pair) or pair[0] > pair[1]):
                raise ValueError(f"invalid integer interval: {name}[{i},{i+offset}]")
            if offset % 2 and pair != [0, 0]:
                raise ValueError(f"opposite parity entry is not exact zero: {name}")
    return value


def contain_triangle(stored: list, fresh: arb_mat, name: str) -> int:
    denominator = 1 << 128
    count = 0
    for i, row in enumerate(stored):
        for offset, (left, right) in enumerate(row):
            j = i + offset
            lower, upper = endpoints(fresh[i, j])
            if not Q(left, denominator) <= lower <= upper <= Q(right, denominator):
                raise ValueError(f"independent input not contained: {name}[{i},{j}]")
            count += 1
    return count


def interval_order_bound(triangle: list, parity: int, upper: bool) -> fmpq_mat:
    indices = list(range(parity, DIMENSION, 2))
    size = len(indices)
    result = fmpq_mat(size, size)
    radii = [0] * size
    for i, source_i in enumerate(indices):
        for j in range(i, size):
            source_j = indices[j]
            lower, higher = triangle[source_i][source_j - source_i]
            result[i, j] = result[j, i] = fmpq(lower + higher, 1 << 129)
            radii[i] += higher - lower
            if i != j:
                radii[j] += higher - lower
    for i, radius in enumerate(radii):
        result[i, i] += fmpq(radius if upper else -radius, 1 << 129)
    return result


def sufficient_lower(matrices: dict, parity: int) -> fmpq_mat:
    result = interval_order_bound(matrices["A"], parity, False)
    gp_upper = interval_order_bound(matrices["GP"], parity, True)
    complement = fmpq(19, 8) - fmpq(1, 10 ** 82)
    for i, degree in enumerate(range(parity, DIMENSION, 2)):
        gp_upper[i, i] += fmpq(3, 10 ** 40) * fmpq(2, 2 * degree + 1)
    return result - gp_upper / complement


def rational_from_flint(value: fmpq) -> Q:
    return Q(int(value.p), int(value.q))


def verify_block(lower: fmpq_mat, proof: dict) -> Q:
    size = lower.nrows()
    rows = proof["transform"]
    if not isinstance(rows, list) or len(rows) != size or any(
            not isinstance(row, list) or len(row) != size for row in rows):
        raise ValueError("invalid exact congruence dimensions")
    witness = fmpq_mat([[qflint(exact_q(value)) for value in row] for row in rows])
    if witness.det() == 0:
        raise ValueError("singular congruence witness")
    transformed = witness.transpose() * lower * witness
    margin = min(transformed[i, i] - sum(
        (abs(transformed[i, j]) for j in range(size) if j != i), fmpq(0))
        for i in range(size))
    exact_margin = rational_from_flint(margin)
    if exact_margin <= 0 or exact_q(proof["claimed_margin"]) != exact_margin:
        raise ValueError("nonpositive or dishonest exact congruence margin")
    return exact_margin


def audit(path: Path) -> dict:
    raw = path.read_bytes()
    obj = decode(raw)
    fixed = {"format": "research-fourier-minorant-matrix-v1",
             "support": [1353, 2048], "a": "7/2", "omega": 256,
             "dimension": DIMENSION, "basis": "ordinary_unnormalized_legendre",
             "bits": 128, "source_precision": 512,
             "frequency_order": 48, "arithmetic_order": 312}
    if any(obj.get(key) != value for key, value in fixed.items()):
        raise ValueError("incorrect fixed full-matrix source configuration")
    if not isinstance(obj.get("matrices"), dict) or set(obj["matrices"]) != MATRIX_NAMES:
        raise ValueError("incomplete full-matrix source set")
    matrices = {name: validate_triangle(value, name)
                for name, value in obj["matrices"].items()}
    checks = {}
    with ctx.workprec(SOURCE_BITS):
        source_error = operator_error(48)
        _, required_upper = endpoints(source_error)
        supplied_upper = exact_q(obj["quadrature_operator_error_upper"])
        if not required_upper <= supplied_upper < Q(1, 10 ** 18):
            raise ValueError("incorrect full-band operator remainder")
        p, square, gp = arithmetic_matrices()
        pole = pole_matrix()
        band, independent_error = band_matrix()
        a = p + pole + band
        for i in range(DIMENSION):
            a[i, i] += qarb(Q(7, 2) * Q(2, 2 * i + 1))
        fresh = {"P": p, "P_squared": square, "GP": gp,
                 "pole": pole, "band": band, "A": a}
        for name in sorted(MATRIX_NAMES):
            checks[name] = contain_triangle(matrices[name], fresh[name], name)
    if not isinstance(obj.get("blocks"), dict) or set(obj["blocks"]) != {"even", "odd"}:
        raise ValueError("both complete parity congruences are required")
    margins = {name: str(verify_block(sufficient_lower(matrices, parity), obj["blocks"][name]))
               for parity, name in enumerate(("even", "odd"))}
    return {"status": "PASS", "format": "research-fourier-minorant-matrix-audit-v1",
            "scope": "complete C-0094 sufficient bounded-minorant lower; research only",
            "input_sha256": hashlib.sha256(raw).hexdigest(),
            "independent_source_precision": SOURCE_BITS,
            "independent_frequency_order": FREQUENCY_ORDER,
            "independent_arithmetic_order": ARITHMETIC_ORDER,
            "anchor_series_order": ANCHOR_ORDER,
            "independent_quadrature_operator_error_upper": str(independent_error),
            "matrix_entries_checked": checks, "exact_congruence_margins": margins,
            "frequency_panels": [[str(a), str(b)] for a, b in panels()],
            "shared_premises": ["Suzuki arXiv2606.09096v3", "public C-0094",
                                "Python-Flint/FLINT Arb and rigorous Legendre-root primitives"],
            "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.input)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"],
                      "matrix_entries_checked": result["matrix_entries_checked"],
                      "exact_congruence_margins": result["exact_congruence_margins"]}, indent=2))


if __name__ == "__main__":
    main()
