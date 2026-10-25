"""Independent fixed T=3/4 full Fourier-matrix audit, research only.

No producer or other checker imports. Arithmetic uses all ordered signed-image
intersections. Fourier transforms use finite entire-series anchors and downward
recurrence, with a complete operator-norm quadrature remainder. Python-Flint's
Arb transcendental and rigorous Legendre-root primitives remain shared premises.
This report is not a theorem admission or a production certificate.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
from math import factorial, isqrt
from pathlib import Path

from flint import acb, arb, arb_mat, ctx, fmpq, fmpq_mat

ROOT = Path(__file__).resolve().parents[1]
DIMENSION = 312
SOURCE_BITS = 768
FREQUENCY_ORDER = 64
ARITHMETIC_ORDER = 313
ANCHOR_ORDER = 384
GRID = 1 << 128
MATRIX_NAMES = {"P", "P_squared", "GP", "pole", "band", "A"}
COMPLEMENT_D = Q(63, 32) - Q(4, 10**49)
MIXED_ALLOWANCE = Q(6, 10**24)
QUALIFICATION_PATH = "computations/2026-10-25T203013Z-m4-fourier-qualification/data/qualification-controls-v1.json"
QUALIFICATION_SHA = "b0eacdeeb755b04c08f9f1b41801829943de2577747279ded6995d70cad58a48"
SCALAR_PATH = "computations/2026-10-25T211305Z-post-m4-scalar-cost-assessment/data/assessment-v1.json"
SCALAR_SHA = "f9b98150587834c145c81f17b9946f2a36a9e8e2c091659bd4b56c728e2b08df"
EXTERIOR_PATH = "computations/2026-10-25T142424Z-reference-route-selection/data/scalar-controls-v1.json"
EXTERIOR_SHA = "7d3975bb76c621f15182c6377503ac9fd63a83c786b66898e271294fbf09f3fc"
SOURCE_SCOPE = "complete fixed T3/4 research minorant inputs; no positivity or admission until independently accepted"
FIXED = {"format": "research-fourier-m4-minorant-matrix-v1",
         "support": [3, 4], "active_terms": [2, 3, 4], "a": "7/2", "omega": 256,
         "dimension": DIMENSION, "basis": "ordinary_unnormalized_legendre",
         "bits": 128, "source_precision": 512,
         "frequency_order": 49, "arithmetic_order": 312}
SOURCE_FIELDS = set(FIXED) | {"quadrature_operator_error_upper", "matrices",
                            "complement", "source_sha256", "scope",
                            "numerical_order_loss_bounds"}
PROOF_FIELDS = {"blocks", "source_packet_sha256", "status"}


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


def same_exact(value: object, expected: object) -> bool:
    """JSON equality without accepting booleans as integer configuration values."""
    if type(value) is not type(expected):
        return False
    if isinstance(expected, dict):
        return (value.keys() == expected.keys()
                and all(same_exact(value[key], item) for key, item in expected.items()))
    if isinstance(expected, list):
        return (len(value) == len(expected)
                and all(same_exact(a, b) for a, b in zip(value, expected)))
    return value == expected


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
    """Enclosed Legendre roots, independently derived derivative weights.

    Ordered disjoint root balls and the root recurrence identify all roots.
    Polynomial exactness of the Gauss rule is an explicit mathematical premise.
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


def certified_max(left: arb, right: arb) -> arb:
    if left > right:
        return left
    if right > left:
        return right
    raise ValueError("uncertified arithmetic endpoint ordering")


def image_intersection(alpha: arb, beta: arb, identical: bool) -> tuple[arb, arb] | None:
    """Intersect [-1,1], [-1-alpha,1-alpha], [-1-beta,1-beta]."""
    if identical:
        smallest = largest = alpha
    elif alpha > beta:
        smallest, largest = beta, alpha
    elif beta > alpha:
        smallest, largest = alpha, beta
    else:
        raise ValueError("uncertified signed shift ordering")
    left = certified_max(arb(-1), -1 - smallest)
    right = -certified_max(arb(-1), -1 + largest)
    if right > left:
        return left, right
    if left > right:
        return None
    raise ValueError("uncertified arithmetic intersection domain")


def arithmetic_matrices() -> tuple[arb_mat, arb_mat, arb_mat]:
    t = qarb(Q(3, 4))
    logs = {m: arb(m).log() for m in (2, 3, 4, 5)}
    if not (logs[2] < t < logs[5] / 2
            and 0 < logs[2] < logs[3] < logs[4] < 2 * t):
        raise ValueError("independent strict prime-power activation window failed")
    shifts = {m: logs[m] / t for m in (2, 3, 4)}
    # The fourth term is the prime power 2^2, so its von Mangoldt value is log2.
    coefficients = {2: -logs[2] / arb(2).sqrt(),
                    3: -logs[3] / arb(3).sqrt(), 4: -logs[2] / 2}
    nodes, weights = gauss_rule(ARITHMETIC_ORDER)
    p = arb_mat(DIMENSION, DIMENSION)
    square = arb_mat(DIMENSION, DIMENSION)
    signed = [(m, sign) for m in (2, 3, 4) for sign in (-1, 1)]
    for m, sign in signed:
        shift = sign * shifts[m]
        domain = ((arb(-1), 1 - shift) if sign > 0
                  else (-1 - shift, arb(1)))
        p += coefficients[m] * interval_integral(
            *domain, arb(0), shift, nodes, weights)
    nonempty = 0
    opposite_22 = 0
    # All 36 ordered products are considered directly, including the two
    # opposite-sign 2/2 intersections that survive after the log2 threshold.
    for m, sign in signed:
        alpha = sign * shifts[m]
        for other, other_sign in signed:
            beta = other_sign * shifts[other]
            domain = image_intersection(alpha, beta, (m, sign) == (other, other_sign))
            expected = sign == other_sign or m == other == 2
            if (domain is not None) != expected:
                raise ValueError("fixed ordered image geometry changed")
            if domain is None:
                continue
            nonempty += 1
            opposite_22 += int(m == other == 2 and sign != other_sign)
            square += coefficients[m] * coefficients[other] * interval_integral(
                *domain, alpha, beta, nodes, weights)
    if nonempty != 20 or opposite_22 != 2:
        raise ValueError("incomplete ordered image intersections")
    parity_project(p)
    parity_project(square)
    mass_inverse_p = arb_mat([
        [p[i, j] * qarb(Q(2 * i + 1, 2)) for j in range(DIMENSION)]
        for i in range(DIMENSION)])
    gp = parity_project(square - p * mass_inverse_p)
    return p, square, gp


def finite_hypergeometric(n: int, w: arb, terms: int, alternating: bool) -> arb:
    """Enclose 0F1(n+3/2; +/-w^2/4) with the full geometric entire tail."""
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
    if not (0 < w < 192):
        raise ValueError("frequency node argument outside strict anchor range")
    values = [arb(0) for _ in range(DIMENSION + 2)]
    for n in (DIMENSION, DIMENSION + 1):
        values[n] = (w ** n / double_factorial_odd(n)
                     * finite_hypergeometric(n, w, ANCHOR_ORDER, True))
    for n in range(DIMENSION, 0, -1):
        values[n - 1] = (2 * n + 1) * values[n] / w - values[n + 1]
    # I_n(w)=2(-i)^n j_n(w). Same-parity complex products are these real products.
    return [2 * (-1 if (n // 2) % 2 else 1) * values[n]
            for n in range(DIMENSION)]


def panels() -> list[tuple[Q, Q]]:
    edges = [Q(0), Q(1, 4), Q(1, 2), Q(1), Q(2), Q(4)]
    edges.extend(Q(value) for value in range(8, 257, 4))
    return list(zip(edges, edges[1:]))


def operator_error(order: int) -> arb:
    # Analytic Bernstein-ellipse envelope, including the uniform 4096 digamma
    # bound. The estimate is for the complete operator, not sampled entries.
    t = qarb(Q(3, 4))
    result = arb(0)
    for left, right in panels():
        half = qarb((right - left) / 2)
        rho = 2 * half
        bound = 2 * t / arb.pi() * (2 * t * rho).exp() * 4096
        result += 8 * half * bound / (1 << (2 * order))
    return result


def band_matrix() -> tuple[arb_mat, Q]:
    nodes, weights = gauss_rule(FREQUENCY_ORDER)
    t = qarb(Q(3, 4))
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
    t = qarb(Q(3, 4))
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


def analytic_grid_radius(error: Q, i: int, j: int) -> int:
    """Exact ceil(E*2^128*sqrt(D_i*D_j)), without Arb mag-radius inflation."""
    squared = (error * GRID) ** 2 * Q(4, (2 * i + 1) * (2 * j + 1))
    root = isqrt(squared.numerator // squared.denominator)
    return root + int(root * root * squared.denominator < squared.numerator)


def numerical_order_loss(triangle: list, error: Q | None = None) -> Q:
    """Measure 2*row_radius/D_i after removing prescribed analytic radii."""
    widths = [0] * DIMENSION
    for i, row in enumerate(triangle):
        for offset, (left, right) in enumerate(row):
            j = i + offset
            if offset % 2:
                continue
            if error is not None:
                radius = analytic_grid_radius(error, i, j)
                left, right = left + radius, right - radius
            if left > right:
                raise ValueError("analytic radius exceeds published interval width")
            width = right - left
            widths[i] += width
            if i != j:
                widths[j] += width
    result = max((Q(width * (2 * i + 1), 2 * GRID)
                  for i, width in enumerate(widths)), default=Q())
    if error is not None:
        # Ceiling each analytic radius changes it by less than one grid unit.
        result += Q(97188, GRID)
    return result


def validate_numerical_bounds(source: dict, matrices: dict) -> dict:
    supplied = source.get("numerical_order_loss_bounds")
    if not isinstance(supplied, dict) or set(supplied) != MATRIX_NAMES:
        raise ValueError("incomplete numerical order-loss reports")
    error = exact_q(source["quadrature_operator_error_upper"])
    if not (0 < error < Q(3, 10**21) and (error * GRID).denominator == 1):
        raise ValueError("source remainder is not an admissible 128-bit dyadic upper")
    measured = {name: numerical_order_loss(matrices[name], error if name in {"band", "A"} else None)
                for name in sorted(MATRIX_NAMES)}
    if any(exact_q(supplied[name]) != value for name, value in measured.items()):
        raise ValueError("dishonest numerical order-loss report")
    if measured["A"] > Q(1, 10**27) or measured["GP"] > Q(1, 10**28):
        raise ValueError("fixed numerical A/GP order-loss budget exceeded")
    return {name: str(value) for name, value in measured.items()}


def contain_triangle(stored: list, fresh: arb_mat, name: str) -> int:
    count = 0
    for i, row in enumerate(stored):
        for offset, (left, right) in enumerate(row):
            j = i + offset
            lower, upper = endpoints(fresh[i, j])
            if not Q(left, GRID) <= lower <= upper <= Q(right, GRID):
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
            result[i, j] = result[j, i] = fmpq(lower + higher, 2 * GRID)
            radii[i] += higher - lower
            if i != j:
                radii[j] += higher - lower
    for i, radius in enumerate(radii):
        result[i, i] += fmpq(radius if upper else -radius, 2 * GRID)
    return result


def sufficient_lower(matrices: dict, parity: int) -> fmpq_mat:
    result = interval_order_bound(matrices["A"], parity, False)
    gp_upper = interval_order_bound(matrices["GP"], parity, True)
    for i, degree in enumerate(range(parity, DIMENSION, 2)):
        gp_upper[i, i] += qflint(MIXED_ALLOWANCE * Q(2, 2 * degree + 1))
    return result - gp_upper / qflint(COMPLEMENT_D)


def rational_from_flint(value: fmpq) -> Q:
    return Q(int(value.p), int(value.q))


def verify_block(lower: fmpq_mat, proof: dict, parity: int) -> dict:
    if not isinstance(proof, dict) or set(proof) != {
            "transform", "claimed_margin", "mass_normalized_gap_exact"}:
        raise ValueError("invalid exact congruence proof fields")
    size = lower.nrows()
    rows = proof["transform"]
    if not isinstance(rows, list) or len(rows) != size or any(
            not isinstance(row, list) or len(row) != size for row in rows):
        raise ValueError("invalid exact congruence dimensions")
    witness = fmpq_mat([[qflint(exact_q(value)) for value in row] for row in rows])
    if any(witness[i, i] == 0 or any(witness[i, j] for j in range(i))
           for i in range(size)):
        raise ValueError("singular or non-upper-triangular congruence witness")
    transformed = witness.transpose() * lower * witness
    margin = min(transformed[i, i] - sum(
        (abs(transformed[i, j]) for j in range(size) if j != i), fmpq(0))
        for i in range(size))
    exact_margin = rational_from_flint(margin)
    if exact_margin <= 0 or exact_q(proof["claimed_margin"]) != exact_margin:
        raise ValueError("nonpositive or dishonest exact congruence margin")
    mass_trace = sum((witness[i, j] ** 2 * fmpq(2, 2 * (2 * i + parity) + 1)
                      for i in range(size) for j in range(size)), fmpq(0))
    gap = exact_margin / rational_from_flint(mass_trace)
    if exact_q(proof["mass_normalized_gap_exact"]) != gap:
        raise ValueError("dishonest mass-normalized lower")
    return {"exact_margin": str(exact_margin), "mass_normalized_gap_exact": str(gap)}


def capture(path: Path) -> tuple[bytes, dict]:
    raw = path.read_bytes()
    return raw, decode(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def pinned_data(path: str, expected_sha: str, legacy_display_numbers: bool = False) -> dict:
    raw = (ROOT / path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise ValueError(f"pinned analytical source bytes changed: {path}")
    if not legacy_display_numbers:
        return decode(raw)
    # Original C94 controls have decimal log10 display fields. Preserve their
    # tokens as strings, never floating arithmetic. Its exact rational fields
    # alone enter inequalities, and all bytes are pinned before parsing.
    obj = json.loads(raw, object_pairs_hook=unique_object,
                     parse_float=str, parse_constant=reject_float)
    if not isinstance(obj, dict):
        raise ValueError("pinned analytical source must be an object")
    return obj


def interval_upper(value: dict) -> Q:
    lower, upper = exact_q(value["lower"]), exact_q(value["upper"])
    if lower > upper:
        raise ValueError("inverted inherited analytical interval")
    return upper


def validate_complement(complement: object) -> None:
    expected = {"d_exact": str(COMPLEMENT_D), "mixed_allowance_exact": str(MIXED_ALLOWANCE),
                "qualification_source": QUALIFICATION_PATH, "qualification_sha256": QUALIFICATION_SHA,
                "scalar_source": SCALAR_PATH, "scalar_sha256": SCALAR_SHA}
    if not same_exact(complement, expected):
        raise ValueError("complete complement binding changed")
    qualification = pinned_data(QUALIFICATION_PATH, QUALIFICATION_SHA)
    scalar = pinned_data(SCALAR_PATH, SCALAR_SHA)
    exterior = pinned_data(EXTERIOR_PATH, EXTERIOR_SHA, legacy_display_numbers=True)
    elementary = qualification["elementary_norm"]
    qs = qualification["scalars"]
    ss = scalar["scalars"]
    p0, eta0, kappa0 = Q(49, 32), Q(19, 10**25), Q(4, 10**49)
    if (qualification.get("format") != "m4-fourier-qualification-controls-v1"
            or elementary["p_upper"] != str(p0)
            or elementary["reference_lower"] != "63/32"
            or not exact_q(elementary["joint_arithmetic_elementary_upper"]) < p0
            or not interval_upper(qs["p_joint"]) < p0
            or not Q(7, 2) - p0 == Q(63, 32)
            or qs["exterior_source_sha256"] != EXTERIOR_SHA
            or qs["exterior_weight_lower"] != "1/5"
            or not exact_q(exterior["exterior_weight_lower_from_series"]["lower"]) > Q(1, 5)):
        raise ValueError("inherited arithmetic or original C94 exterior qualification failed")
    if any(not same_exact(scalar.get(key), expected_value) for key, expected_value in
           {"format": "post-m4-scalar-cost-assessment-v1", "support": [3, 4],
            "active_terms": [2, 3, 4], "a": "7/2", "omega": 256,
            "dimension": DIMENSION}.items()):
        raise ValueError("inherited fixed scalar identity changed")
    if (exact_q(ss["kappa_upper"]) != kappa0
            or exact_q(ss["mixed_Gram_upper"]) != MIXED_ALLOWANCE
            or exact_q(ss["denominator_lower"]) != COMPLEMENT_D
            or not 0 <= interval_upper(ss["kappa"]) < kappa0
            or not 0 <= interval_upper(ss["eta"]) < eta0
            or not 2 * p0 * eta0 + eta0**2 < MIXED_ALLOWANCE
            or not COMPLEMENT_D > 0):
        raise ValueError("inherited complete complement inequalities failed")


def validate_identity(obj: dict, source_raw: bytes, source: dict,
                      source_only: bool = False) -> None:
    if set(source) != SOURCE_FIELDS:
        raise ValueError("fixed source inventory changed")
    if any(not same_exact(source.get(key), value) for key, value in FIXED.items()):
        raise ValueError("incorrect fixed full-matrix source configuration")
    if source.get("scope") != SOURCE_SCOPE:
        raise ValueError("fixed research-only scope changed")
    if source_only:
        if not same_exact(obj, source):
            raise ValueError("source-only audit input is not its original source packet")
    else:
        if set(obj) != SOURCE_FIELDS | PROOF_FIELDS:
            raise ValueError("proof/source inventory changed")
        if any(not same_exact(obj.get(key), value) for key, value in source.items()):
            raise ValueError("proof changed its original source packet")
        if obj["source_packet_sha256"] != hashlib.sha256(source_raw).hexdigest():
            raise ValueError("source packet byte binding changed")
        if obj["status"] != "COMPLETE_POSITIVE_SUFFICIENT_LOWER":
            raise ValueError("no complete positive claim")
    producer = ROOT / "scripts/weil_m4_fourier_matrix.py"
    if source["source_sha256"] != hashlib.sha256(producer.read_bytes()).hexdigest():
        raise ValueError("executed producer identity changed")
    if not isinstance(source.get("matrices"), dict) or set(source["matrices"]) != MATRIX_NAMES:
        raise ValueError("incomplete full-matrix source set")
    validate_complement(source["complement"])


def exact_blocks(obj: dict) -> dict:
    if not isinstance(obj.get("blocks"), dict) or set(obj["blocks"]) != {"even", "odd"}:
        raise ValueError("both complete parity congruences are required")
    return {name: verify_block(sufficient_lower(obj["matrices"], parity),
                               obj["blocks"][name], parity)
            for parity, name in enumerate(("even", "odd"))}


def audit(path: Path, source_path: Path, exact_only: bool = False,
          source_only: bool = False) -> dict:
    if exact_only and source_only:
        raise ValueError("source-only analytical acceptance cannot be exact-only")
    if source_only and path.resolve() != source_path.resolve():
        raise ValueError("source-only audit requires input and --source to name the same file")
    raw, obj = capture(path)
    source_raw, source = capture(source_path)
    if source_only and raw != source_raw:
        raise ValueError("source-only input bytes changed during capture")
    validate_identity(obj, source_raw, source, source_only)
    matrices = {name: validate_triangle(value, name)
                for name, value in source["matrices"].items()}
    numerical_bounds = validate_numerical_bounds(source, matrices)
    checks = {}
    independent_error = None
    if not exact_only:
        with ctx.workprec(SOURCE_BITS):
            _, required_upper = endpoints(operator_error(49))
            supplied_upper = exact_q(source["quadrature_operator_error_upper"])
            if not required_upper <= supplied_upper < Q(3, 10**21):
                raise ValueError("incorrect complete full-band operator remainder")
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
    margins = {} if source_only else exact_blocks(obj)
    status = "EXACT_ONLY_PASS" if exact_only else "ANALYTICAL_SOURCE_PASS" if source_only else "PASS"
    return {"status": status,
            "format": "research-fourier-m4-minorant-matrix-audit-v1",
            "scope": ("exact replay only; analytic inputs not rebuilt" if exact_only else
                      "complete fixed analytical source containment; no positivity claim" if source_only else
                      "complete C-0094 sufficient bounded-minorant lower; research only"),
            "input_sha256": hashlib.sha256(raw).hexdigest(),
            "source_packet_sha256": hashlib.sha256(source_raw).hexdigest(),
            "independent_source_precision": None if exact_only else SOURCE_BITS,
            "independent_frequency_order": None if exact_only else FREQUENCY_ORDER,
            "independent_arithmetic_order": None if exact_only else ARITHMETIC_ORDER,
            "anchor_series_order": None if exact_only else ANCHOR_ORDER,
            "independent_quadrature_operator_error_upper": str(independent_error) if independent_error is not None else None,
            "numerical_order_loss_bounds": numerical_bounds,
            "matrix_entries_checked": checks, "blocks": margins,
            "frequency_panels": [[str(a), str(b)] for a, b in panels()],
            "shared_premises": ["Suzuki arXiv2606.09096v3", "public C-0094",
                                "Python-Flint/FLINT Arb and rigorous Legendre-root primitives"],
            "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--source", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--exact-only", action="store_true")
    mode.add_argument("--source-only", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.input, args.source, args.exact_only, args.source_only)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": result["status"],
                      "matrix_entries_checked": result["matrix_entries_checked"],
                      "blocks": result["blocks"]}, indent=2))


if __name__ == "__main__":
    main()
