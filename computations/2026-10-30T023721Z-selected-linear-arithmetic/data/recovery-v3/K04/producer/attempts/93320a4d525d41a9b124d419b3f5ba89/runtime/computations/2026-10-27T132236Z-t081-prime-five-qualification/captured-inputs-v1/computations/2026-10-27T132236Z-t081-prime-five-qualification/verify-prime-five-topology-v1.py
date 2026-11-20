"""Independent four-mode prime-five diagnostic; no target positivity claim."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from math import comb, factorial
from pathlib import Path
import sys

from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[2]
T = Q(81, 100)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def reject_number(_):
    raise ValueError("nonexact JSON number")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load(path):
    raw = path.read_bytes()
    return json.loads(raw, parse_float=reject_number, parse_constant=reject_number,
                      object_pairs_hook=unique_object), hashlib.sha256(raw).hexdigest()


def rational(text):
    require(isinstance(text, str), "canonical rational string required")
    value = Q(text)
    require(str(value) == text, "noncanonical rational string")
    return value


def aq(value):
    value = Q(value)
    return arb(value.numerator)/value.denominator


def endpoints(value):
    require(value.is_finite(), "nonfinite reconstruction")
    mid, rad = value.mid().fmpq(), value.rad().fmpq()
    lo, hi = mid-rad, mid+rad
    return Q(int(lo.p), int(lo.q)), Q(int(hi.p), int(hi.q))


def contains(record, value, label):
    require(isinstance(record, dict) and set(record) == {"lower", "upper"},
            "interval schema mismatch "+label)
    lower, upper = rational(record["lower"]), rational(record["upper"])
    lo, hi = endpoints(value)
    require(lower <= lo <= hi <= upper, "native containment failure "+label)


def fixed_fields(record, fields, label):
    require(isinstance(record, dict), "invalid "+label)
    for key, value in fields.items():
        require(type(record.get(key)) is type(value) and record[key] == value,
                "unauthorized "+label+" "+key)


def legendre(n):
    # Rodrigues: differentiate (x^2-1)^n exactly, then divide by 2^n n!.
    result = [Q(0)]*(n+1)
    for k in range(n+1):
        degree = 2*k
        if degree >= n:
            result[degree-n] = Q(comb(n, k)*(-1)**(n-k)*factorial(degree),
                                 2**n*factorial(n)*factorial(degree-n))
    return [aq(value) for value in result]


def translate(poly, shift):
    return [sum((poly[k]*comb(k, j)*shift**(k-j)
                 for k in range(j, len(poly))), arb(0)) for j in range(len(poly))]


def product(left, right):
    result = [arb(0) for _ in range(len(left)+len(right)-1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i+j] += a*b
    return result


def ordinary_moment(k, left, right):
    return (right**(k+1)-left**(k+1))/(k+1)


def log_primitive(j, y):
    # The endpoint limit y^(j+1) log(y)=0 is exact, not sampled.
    if y == 0:
        return arb(0)
    require(y > 0, "nonpositive logarithm argument")
    return y**(j+1)*(y.log()/(j+1)-aq(Q(1, (j+1)**2)))


def potential_primitive(k, x):
    minus = -sum((comb(k, j)*(-1)**j*log_primitive(j, 1-x)
                  for j in range(k+1)), arb(0))
    plus = sum((comb(k, j)*(-1)**(k-j)*log_primitive(j, 1+x)
                for j in range(k+1)), arb(0))
    return -(minus+plus)/2


def integrate(poly, left, right, potential=False):
    return sum((coefficient*(potential_primitive(k, right)-potential_primitive(k, left)
                            if potential else ordinary_moment(k, left, right))
                for k, coefficient in enumerate(poly)), arb(0))


def audit(inputs_path, source_path):
    ctx.prec = 768
    pins, input_hash = load(inputs_path)
    source, source_hash = load(source_path)
    fixed_fields(pins, {"format": "t081-prime-five-topology-inputs-v1", "support": str(T),
                       "diagnostic_dimension": 4, "producer_precision_bits": 512,
                       "independent_precision_bits": 768, "publication_bits": 192,
                       "full_target_low_coupling_matrix_permitted": False,
                       "production_admission": False}, "inputs")
    fixed = {"format": "t081-prime-five-topology-qualification-v1", "support": str(T),
             "diagnostic_dimension": 4, "producer_precision_bits": 512, "publication_bits": 192,
             "diagnostic_only": True, "full_target_low_coupling_matrix_computed": False,
             "target_positivity_proved": False, "production_admission": False}
    fixed_fields(source, fixed, "source")
    require(set(source) == set(fixed) | {"active_terms", "breakpoints", "matrices",
            "prime5_mixed_square_constant_mode", "new_edge_width_mapped", "new_edge_width_physical",
            "inputs_sha256", "producer_sha256", "imported_project_module_sha256"}, "source schema mismatch")
    require(source["inputs_sha256"] == input_hash, "input fingerprint mismatch")
    producer = Path(__file__).resolve().with_name("qualify-prime-five-topology-v1.py")
    require(source["producer_sha256"] == hashlib.sha256(producer.read_bytes()).hexdigest(),
            "producer fingerprint mismatch")
    modules = source["imported_project_module_sha256"]
    require(isinstance(modules, dict) and "scripts/cert/prime_power_terms.py" in modules,
            "missing project dependency binding")
    for name, digest in modules.items():
        require(isinstance(name, str) and isinstance(digest, str), "invalid dependency fingerprint")
        path = (ROOT/name).resolve()
        require(name.startswith("scripts/") and path.is_relative_to(ROOT) and path.suffix == ".py",
                "unsafe dependency path")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, "changed dependency "+name)

    require(arb(5).log() < aq(2*T) < arb(7).log(), "strict support thresholds fail")
    active = []
    for integer in range(2, 7):
        p = next(d for d in range(2, integer+1) if integer % d == 0)
        rest, exponent = integer, 0
        while rest % p == 0:
            rest //= p
            exponent += 1
        if rest == 1:
            active.append((integer, p, exponent))
    require(active == [(2, 2, 1), (3, 3, 1), (4, 2, 2), (5, 5, 1)], "prime-power enumeration mismatch")
    require(isinstance(source["active_terms"], list) and len(source["active_terms"]) == 4,
            "incomplete active terms")
    terms = []
    for row, (m, p, exponent) in zip(source["active_terms"], active, strict=True):
        fixed_fields(row, {"m": m, "prime": p, "exponent": exponent}, "active term")
        require(set(row) == {"m", "prime", "exponent", "tau", "coefficient"}, "term schema mismatch")
        tau, coefficient = arb(m).log()/aq(T), arb(p).log()/arb(m).sqrt()
        require(0 < tau < 2, "inactive term")
        contains(row["tau"], tau, "tau")
        contains(row["coefficient"], coefficient, "coefficient")
        terms.append((tau, coefficient))
    tau5, c5 = terms[-1]
    require(1 < tau5 < 2, "prime-five edge geometry failure")
    contains(source["new_edge_width_mapped"], 2-tau5, "mapped width")
    contains(source["new_edge_width_physical"], aq(2*T)-arb(5).log(), "physical width")
    edges = sorted([arb(-1), arb(1)]+[b for tau, _ in terms for b in (1-tau, -1+tau)])
    require(len(edges) == 10 and all(a < b for a, b in zip(edges[:-1], edges[1:])),
            "unordered translation partition")
    require(isinstance(source["breakpoints"], list) and len(source["breakpoints"]) == 10,
            "incomplete breakpoint list")
    for index, (record, edge) in enumerate(zip(source["breakpoints"], edges, strict=True)):
        contains(record, edge, "breakpoint "+str(index))
    basis = [legendre(n) for n in range(4)]
    matrices = {name: [[arb(0) for _ in range(4)] for _ in range(4)]
                for name in ("P", "P_squared", "GP", "VP", "PV")}
    for left, right in zip(edges[:-1], edges[1:]):
        center = (left+right)/2
        images = [[arb(0) for _ in poly] for poly in basis]
        for tau, coefficient in terms:
            for boundary, shift, before in ((1-tau, tau, True), (-1+tau, -tau, False)):
                active_here = center < boundary if before else center > boundary
                require(active_here or (center > boundary if before else center < boundary),
                        "unresolved shift activity")
                if active_here:
                    for j, poly in enumerate(basis):
                        shifted = translate(poly, shift)
                        for k, value in enumerate(shifted):
                            images[j][k] -= coefficient*value
        for i in range(4):
            for j in range(4):
                matrices["P"][i][j] += integrate(product(basis[i], images[j]), left, right)
                matrices["P_squared"][i][j] += integrate(product(images[i], images[j]), left, right)
                matrices["VP"][i][j] += integrate(product(basis[i], images[j]), left, right, True)
                matrices["PV"][i][j] += integrate(product(images[i], basis[j]), left, right, True)
    for i in range(4):
        for j in range(4):
            matrices["GP"][i][j] = matrices["P_squared"][i][j]-sum(
                (matrices["P"][i][k]*aq(Q(2*k+1, 2))*matrices["P"][k][j]
                 for k in range(4)), arb(0))
    checked = 0
    require(isinstance(source["matrices"], dict) and set(source["matrices"]) == set(matrices),
            "matrix family mismatch")
    for name, matrix in matrices.items():
        records = source["matrices"][name]
        require(isinstance(records, list) and len(records) == 4 and
                all(isinstance(row, list) and len(row) == 4 for row in records), "matrix shape mismatch")
        for i in range(4):
            for j in range(4):
                value = matrix[i][j]
                if name in ("P", "P_squared", "GP") and (i+j) % 2:
                    require(value.contains(0), "opposite-parity reconstruction excludes zero")
                    value = arb(0)
                    require(records[i][j] == {"lower": "0", "upper": "0"},
                            "opposite-parity publication not exact zero")
                contains(records[i][j], value, name+"["+str(i)+","+str(j)+"]")
                checked += 1
    require(any(not (matrices["VP"][i][j]-matrices["VP"][j][i]).contains(0)
                for i in range(4) for j in range(i+1, 4) if (i+j) % 2 == 0),
            "ordered potential products were accidentally symmetrized")
    mixed = source["prime5_mixed_square_constant_mode"]
    require(isinstance(mixed, list) and len(mixed) == 3, "incomplete prime-five mixed squares")
    for row, (m, _, _), (_, coefficient) in zip(mixed, active[:-1], terms[:-1], strict=True):
        require(isinstance(row, dict) and set(row) == {"m", "value"}, "mixed-square schema mismatch")
        fixed_fields(row, {"m": m}, "mixed square")
        value = 4*(2-tau5)*c5*coefficient
        require(value > 0, "new mixed square not strictly positive")
        contains(row["value"], value, "mixed square "+str(m))
    return {"format": "t081-prime-five-topology-independent-audit-v1", "status": "PASS",
            "source_sha256": source_hash, "inputs_sha256": input_hash,
            "consumer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "support": str(T), "diagnostic_dimension": 4, "audit_precision_bits": 768,
            "matrix_cells_checked": checked, "breakpoints_checked": 10,
            "prime5_mixed_square_terms_checked": 3, "ordered_potential_asymmetry_verified": True,
            "independent_method": "Rodrigues, binomial shifts, monomial and logarithmic moments",
            "shared_trust": "FLINT/Arb arithmetic and transcendental enclosures",
            "diagnostic_only": True, "full_target_low_coupling_matrix_computed": False,
            "target_positivity_proved": False, "production_admission": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("inputs", "source", "output"):
        parser.add_argument("--"+name, type=Path, required=True)
    args = parser.parse_args()
    try:
        require(not args.output.exists(), "output must be a fresh path")
        result = audit(args.inputs, args.source)
        with args.output.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(result, indent=2)+"\n")
    except (ValueError, KeyError, TypeError, ZeroDivisionError, OSError, OverflowError,
            AttributeError, IndexError) as exc:
        print(json.dumps({"status": "REJECTED", "error": str(exc)}))
        return 2
    print(json.dumps({key: result[key] for key in ("status", "matrix_cells_checked", "breakpoints_checked")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
