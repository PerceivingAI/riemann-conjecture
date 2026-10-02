"""Zero-float replay of pre-theorem candidate arithmetic, never admission.

Only serialized rational consistency and positivity are checked. Upstream Arb
transcendental enclosures and the analytic operator bounds remain assumptions.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from math import isqrt
import json
from pathlib import Path

from flint import fmpq, fmpq_mat

AUDIT_FORMAT = "rh-multi-prime-candidate-audit-v1"
AUDIT_ROLE = "pre_theorem_multi_prime_candidate_audit"


def _fraction(value: object) -> Fraction:
    if not isinstance(value, str):
        raise ValueError("audit rationals must be strings, never floating-point numbers")
    return Fraction(value)


def _integer(value: object, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"invalid {name}")
    return value


def _bounds(value: dict) -> tuple[Fraction, Fraction]:
    lo, hi = _fraction(value["lower"]), _fraction(value["upper"])
    if lo > hi:
        raise ValueError("reversed interval")
    return lo, hi


def _dyadic(value: Fraction, bits: int) -> None:
    denominator = value.denominator
    if denominator > 1 << bits or denominator & (denominator - 1):
        raise ValueError("interval/witness exceeds its dyadic resolution")


def _interval_matrix(payload: dict, n: int, bits: int) -> list[list[tuple[Fraction, Fraction]]]:
    if _integer(payload["dimension"], "matrix dimension", 1) != n or len(payload["entries"]) != n * n:
        raise ValueError("matrix dimension/coordinate coverage mismatch")
    grid = [[None for _ in range(n)] for _ in range(n)]
    for entry in payload["entries"]:
        i, j = _integer(entry["row"], "row"), _integer(entry["col"], "col")
        if i >= n or j >= n or grid[i][j] is not None:
            raise ValueError("out-of-range or duplicate matrix coordinate")
        lo = Fraction(_fraction(entry["lo_num"]), _fraction(entry["lo_den"]))
        hi = Fraction(_fraction(entry["hi_num"]), _fraction(entry["hi_den"]))
        if lo > hi:
            raise ValueError("reversed matrix interval")
        _dyadic(lo, bits)
        _dyadic(hi, bits)
        grid[i][j] = (lo, hi)
    for i in range(n):
        for j in range(n):
            if grid[i][j] != grid[j][i]:
                raise ValueError("matrix is not symmetric")
            if i % 2 != j % 2 and grid[i][j] != (0, 0):
                raise ValueError("matrix violates exact Legendre parity")
    return grid


def _witness(payload: dict, n: int, bits: int) -> list[list[Fraction]]:
    if _integer(payload["dimension"], "witness dimension", 1) != n or len(payload["entries"]) != n * n:
        raise ValueError("witness dimension/coordinate coverage mismatch")
    grid = [[None for _ in range(n)] for _ in range(n)]
    for entry in payload["entries"]:
        i, j = _integer(entry["row"], "row"), _integer(entry["col"], "col")
        if i >= n or j >= n or grid[i][j] is not None:
            raise ValueError("out-of-range or duplicate witness coordinate")
        value = Fraction(_fraction(entry["num"]), _fraction(entry["den"]))
        _dyadic(value, bits)
        if j > i and value != 0 or i == j and value != 1:
            raise ValueError("witness must be unit lower triangular")
        grid[i][j] = value
    return grid


def _q(value: Fraction) -> fmpq:
    return fmpq(value.numerator, value.denominator)


def _margin(block: list[list[tuple[Fraction, Fraction]]], witness: list[list[Fraction]]) -> Fraction:
    # Independent native rational midpoint/radius contraction, not generator
    # interval operations, LDL, congruence or Gershgorin helpers.
    n = len(block)
    midpoint = fmpq_mat([[_q((lo + hi) / 2) for lo, hi in row] for row in block])
    radius = fmpq_mat([[_q((hi - lo) / 2) for lo, hi in row] for row in block])
    w = fmpq_mat([[_q(value) for value in row] for row in witness])
    absolute = fmpq_mat([[_q(abs(value)) for value in row] for row in witness])
    centers = w * midpoint * w.transpose()
    radii = absolute * radius * absolute.transpose()
    margins = []
    for i in range(n):
        lower = centers[i, i] - radii[i, i]
        off = sum((abs(centers[i, j]) + radii[i, j] for j in range(n) if j != i), fmpq(0))
        value = lower - off
        margins.append(Fraction(int(value.p), int(value.q)))
    return min(margins)


def audit_candidate_inputs(payload: dict) -> dict[str, object]:
    if payload["format"] != AUDIT_FORMAT or payload["role"] != AUDIT_ROLE:
        raise ValueError("not a pre-theorem multi-prime candidate audit")
    for field in ("theorem_status", "independently_verified", "whitelisted", "automatic_promotion"):
        if payload.get(field) is not False:
            raise ValueError("audit inputs must retain the non-promoting boundary")
    n = _integer(payload["dimension"], "dimension", 2)
    _integer(payload["precision_bits"], "precision_bits", 64)
    _integer(payload["residual_order"], "residual_order", 8)
    matrix_bits = _integer(payload["matrix_bits"], "matrix_bits", 16)
    witness_bits = _integer(payload["witness_bits"], "witness_bits", 8)
    if _fraction(payload["support"]) <= 0 or payload["basis"] != "unnormalized_legendre_degree_order":
        raise ValueError("invalid support/basis convention")
    if _fraction(payload["factor"]) != 3:
        raise ValueError("grouped Schur factor must equal 3")
    c_t, rho = _bounds(payload["c_T"]), _bounds(payload["rho_R"])
    for endpoints in (c_t, rho):
        for value in endpoints: _dyadic(value, matrix_bits)
    if rho[0] < 0:
        raise ValueError("negative residual norm bound")
    arithmetic_upper, previous = Fraction(0), 1
    if payload.get("status") != "CANDIDATE_READY":
        raise ValueError("audit inputs do not contain a completed positive candidate")
    for term in payload["active_terms"]:
        m = _integer(term["m"], "prime power", 2)
        prime = _integer(term["prime"], "prime", 2)
        exponent = _integer(term["exponent"], "exponent", 1)
        if m <= previous or prime ** exponent != m or any(prime % k == 0 for k in range(2, isqrt(prime) + 1)):
            raise ValueError("noncanonical prime-power identities")
        previous = m
        coefficient, bound = _bounds(term["coefficient"]), _bounds(term["compressed_shift_norm_bound"])
        tau = _bounds(term["tau"])
        if coefficient[0] <= 0 or bound[0] <= 0 or tau[0] <= 0 or tau[1] >= 2:
            raise ValueError("invalid arithmetic scalar bounds")
        loss = _bounds(term["rounded_complement_contribution"])
        if loss[0] > coefficient[0] * bound[0] or loss[1] < coefficient[1] * bound[1]:
            raise ValueError("prime loss does not enclose coefficient times norm bound")
        for value in loss: _dyadic(value, matrix_bits)
        arithmetic_upper += loss[1]
    harmonic = sum((Fraction(1, k) for k in range(1, n + 1)), Fraction(0))
    mu = harmonic - c_t[1] - rho[1] - arithmetic_upper
    if mu <= 0 or mu != _fraction(payload["mu_lower"]):
        raise ValueError("nonpositive or inconsistent complement lower bound")
    matrices = {name: _interval_matrix(payload["matrices"][name], n, matrix_bits)
                for name in ("A", "GV", "GP", "GR")}
    factor = Fraction(3) / mu
    schur = [[(matrices["A"][i][j][0] - factor * sum((matrices[name][i][j][1] for name in ("GV", "GP", "GR")), Fraction(0)),
               matrices["A"][i][j][1] - factor * sum((matrices[name][i][j][0] for name in ("GV", "GP", "GR")), Fraction(0)))
              for j in range(n)] for i in range(n)]
    margins = {}
    for parity, name in enumerate(("even", "odd")):
        indices = list(range(parity, n, 2))
        block = [[schur[i][j] for j in indices] for i in indices]
        witness = _witness(payload["witnesses"][name], len(indices), witness_bits)
        margin = _margin(block, witness)
        if margin <= 0 or margin != _fraction(payload[f"{name}_gershgorin_margin"]):
            raise ValueError(f"nonpositive or inconsistent {name} exact witness margin")
        margins[f"{name}_gershgorin_margin"] = str(margin)
    return {"status": "PASS", "support": payload["support"], "dimension": n,
            "precision_bits": payload["precision_bits"], "mu_lower": str(mu), **margins,
            "theorem_status": False, "trust_boundary": "serialized rational arithmetic only; no Arb enclosure certification or admission"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    try:
        result = audit_candidate_inputs(json.loads(args.input.read_text(encoding="utf-8")))
    except (ValueError, TypeError, KeyError, ZeroDivisionError) as error:
        parser.error(str(error))
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
