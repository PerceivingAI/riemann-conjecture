"""Reconstruct fixed weighted low-space source inputs, for research only.

The source generator is never imported. Low matrices use the separate native
moment formulas; rectangular heads use global monomial and Taylor contractions.
A successful receipt records every outward 512-bit reference interval.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

from flint import arb, arb_mat, ctx, fmpq, fmpq_poly

from scripts import verify_combined_schur_analytic_entries as native


ROOT = Path(__file__).resolve().parents[1]
PACKET_FORMAT = "research-weighted-low-space-source-v1"
AUDIT_FORMAT = "research-weighted-low-space-analytic-audit-v1"
DIMENSION = 192
ORDER = 32
SOURCE_BITS = 352
REFERENCE_BITS = 512
NATIVE_PRECISION = 2048
MU_INPUT = "computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json"
MU_INPUT_SHA256 = "44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b"
SOURCE_PATHS = (
    "scripts/weil_weighted_low_space.py",
    "scripts/cert/constants.py",
    "scripts/cert/legendre_schur.py",
    "scripts/cert/mixed_gram_research.py",
    "scripts/cert/multi_prime_legendre_schur.py",
    "scripts/cert/prime_power_terms.py",
    "scripts/cert/residual_kernel.py",
    "scripts/verify_combined_schur_analytic_entries.py",
)
AUDITOR_PATH = "scripts/verify_weighted_low_space_inputs.py"


class InputRejected(ValueError):
    """A source packet or its independent reconstruction did not pass."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InputRejected(message)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise InputRejected(f"nonfinite JSON constant: {value}")


def decode_json(raw: bytes) -> Any:
    return json.loads(raw, object_pairs_hook=_unique_object,
                      parse_constant=_invalid_constant)


def _integer(value: Any, label: str) -> int:
    require(type(value) is int, f"{label} must be an integer")
    return value


def validate_pair(value: Any, label: str) -> None:
    require(type(value) is list and len(value) == 2,
            f"{label} must be an integer endpoint pair")
    lo = _integer(value[0], label + " lower")
    hi = _integer(value[1], label + " upper")
    require(lo <= hi, f"{label} has reversed endpoints")


def _rows(value: Any, lengths: list[int], label: str) -> None:
    require(type(value) is list and len(value) == len(lengths),
            f"{label} has the wrong row count")
    for i, length in enumerate(lengths):
        row = value[i]
        require(type(row) is list and len(row) == length,
                f"{label}[{i}] has the wrong column count")
        for j, pair in enumerate(row):
            validate_pair(pair, f"{label}[{i}][{j}]")


def head_precision(boundary: int) -> int:
    return 256 * ((4 * max(boundary, 224) + 512 + 255) // 256)


def validate_packet(packet: Any, mu_reference_exact: str) -> None:
    """Validate the entire fixed mathematical payload before any Arb work."""
    require(type(packet) is dict, "packet must be an object")
    fixed = {
        "format": PACKET_FORMAT,
        "support": [3, 5],
        "dimension": DIMENSION,
        "residual_order": ORDER,
        "active_terms": [2, 3],
        "basis": "ordinary_unnormalized_legendre",
        "bits": SOURCE_BITS,
        "source_precision": 1024,
        "original_mu_input_sha256": MU_INPUT_SHA256,
        "mu_reference_exact": mu_reference_exact,
    }
    for key, expected in fixed.items():
        require(key in packet and type(packet[key]) is type(expected)
                and packet[key] == expected, f"fixed header mismatch: {key}")
    for key in ("support", "active_terms"):
        require(all(type(v) is int for v in packet[key]),
                f"{key} must contain integers")
    boundary = _integer(packet.get("boundary"), "boundary")
    require(224 <= boundary <= 1024 and boundary % 2 == 0,
            "boundary must be even and lie in [224,1024]")
    require(type(packet.get("head_precision")) is int
            and packet["head_precision"] == head_precision(boundary),
            "head_precision does not match the fixed formula")
    for key, names in (("matrices", {"A_K", "G_K"}),
                       ("heads", {"V", "P", "R32"})):
        require(type(packet.get(key)) is dict and set(packet[key]) == names,
                f"{key} has missing or unexpected components")
    for name in ("A_K", "G_K"):
        _rows(packet["matrices"][name], list(range(DIMENSION, 0, -1)), name)
    for name in ("V", "P", "R32"):
        _rows(packet["heads"][name], [DIMENSION] * (boundary - DIMENSION), name)
    for name in ("delta", "complement"):
        validate_pair(packet.get(name), name)
    signature = packet.get("residual_signature")
    require(type(signature) is str and len(signature) == 64
            and all(c in "0123456789abcdef" for c in signature),
            "invalid residual_signature")
    sources = packet.get("source_sha256")
    require(type(sources) is dict and set(sources) == set(SOURCE_PATHS),
            "source_sha256 must identify the eight fixed source modules")
    for name, digest in sources.items():
        require(type(digest) is str and len(digest) == 64
                and all(c in "0123456789abcdef" for c in digest),
                f"invalid source digest: {name}")
    require(Fraction(mu_reference_exact) > 0, "chosen mu must be positive")


def residual_signature(polynomials: list[fmpq_poly]) -> str:
    text = "\n".join("|".join(map(str, p.coeffs())) for p in polynomials)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _geometry() -> tuple[list[tuple[int, arb, arb]], list[tuple[arb, arb]]]:
    t = native.qarb(fmpq(3, 5))
    terms = []
    for m in (2, 3):
        logarithm = arb(m).log()
        require(logarithm < 2*t, f"active term {m} is not certified")
        terms.append((m, logarithm/t, logarithm/arb(m).sqrt()))
    require(arb(4).log() > 2*t, "next prime-power threshold is not excluded")
    require(1 < terms[0][1] < terms[1][1] < 2,
            "first-window b_m=1 topology is not certified")
    tau2, tau3 = terms[0][1], terms[1][1]
    points = [arb(-1), 1-tau3, 1-tau2, -1+tau2, -1+tau3, arb(1)]
    require(all(a < b for a, b in zip(points[:-1], points[1:])),
            "signed-cell ordering is not certified")
    return terms, list(zip(points[:-1], points[1:]))


def _check_exact_images(basis: list[fmpq_poly], residual: list[fmpq_poly]) -> int:
    require(len(basis) == len(residual), "residual image count mismatch")
    for j, (p, image) in enumerate(zip(basis, residual)):
        require(p.degree() == j and all(not c for k, c in enumerate(p.coeffs())
                                       if (k-j) % 2),
                f"basis parity/degree mismatch at {j}")
        require(image.degree() <= j+ORDER
                and all(not c for k, c in enumerate(image.coeffs()) if (k-j) % 2),
                f"residual parity/degree mismatch at {j}")
    degree = max(p.degree() for p in residual)
    require(degree <= len(basis)+ORDER-1, "residual degree bound failed")
    return degree


def reconstruct(n: int = DIMENSION, precision: int = NATIVE_PRECISION) -> dict[str, Any]:
    """Rebuild raw A, complete projected Gram and scalars without a packet.

    Small dimensions are available for exact mathematical controls. This helper
    does not assert complement positivity at those dimensions.
    """
    require(type(n) is int and n >= 1, "dimension must be positive")
    require(type(precision) is int and precision >= 64, "precision must be at least 64")
    with ctx.workprec(precision):
        t = fmpq(3, 5)
        T = native.qarb(t)
        terms, cells = _geometry()
        basis = native.poly_basis(n)
        C = native.coeffs(basis, n)
        coefficients = native.exact_residual_coefficients(ORDER)
        residual = native.residual_polys(basis, ORDER, t, coefficients)
        degree = _check_exact_images(basis, residual)
        mr = degree+1
        R = native.coeffs(residual, mr)
        V = C*native.hankel(native.global_v_moments(2*n-2), n, n)*C.transpose()
        V2 = C*native.hankel(native.global_v_moments(2*n-2, True), n, n)*C.transpose()
        VR = C*native.hankel(native.global_v_moments(n+mr-2), n, mr)*R.transpose()
        moments = native.integrate_power(arb(-1), arb(1), 2*mr-2)
        Rlow = C*native.hankel(moments, n, mr)*R.transpose()
        R2 = R*native.hankel(moments, mr, mr)*R.transpose()
        P, P2, VP, PR = (arb_mat(n, n) for _ in range(4))
        active_cells = 0
        for a, b in cells:
            S, L, active = native.shifted_cell_images(basis, terms, a, b)
            if not active:
                continue
            active_cells += 1
            radius = (b-a)/2
            A = native.local_legendre((a+b)/2, radius, n)
            W = arb_mat(n, n)
            for k in range(n):
                W[k, k] = 2*radius/(2*k+1)
            P += A*W*L.transpose()
            P2 += L*W*L.transpose()
            PR += S*native.hankel(native.integrate_power(a, b, n+mr-2), n, mr)*R.transpose()
            VP += C*native.hankel(native.cell_v_moments(a, b, 2*n-2), n, n)*S.transpose()
        require(active_cells == 4, "expected four signed active cells")
        delta, rho = native.bound_tail(T, coefficients, ORDER)
        cT = (2*arb.pi()*T).log()+arb.const_euler()
        complement = (native.qarb(native.harmonic(n))-cT-rho
                      - sum((c for _, _, c in terms), arb(0)))
        inverse_norm = arb_mat(n, n)
        for i in range(n):
            inverse_norm[i, i] = arb(2*i+1)/2
        K = V+P+Rlow
        G = (V2+P2+R2+VP+VP.transpose()+VR+VR.transpose()+PR+PR.transpose()
             - K*inverse_norm*K)
        A_K = K
        for i in range(n):
            # Raw low form. The separate residual-error delta is not subtracted.
            A_K[i, i] += arb(2)/(2*i+1)*(native.qarb(native.harmonic(i))-cT)
        return {"A_K": A_K, "G_K": G, "delta": delta,
                "complement": complement, "residual": residual, "basis": basis,
                "residual_signature": residual_signature(residual),
                "residual_max_degree": degree, "precision": precision}


def reconstruct_heads(n: int, boundary: int, precision: int,
                      residual: list[fmpq_poly]) -> dict[str, arb_mat]:
    """Rebuild raw rectangular heads by global monomial moment contractions."""
    require(type(n) is int and n >= 1 and type(boundary) is int and boundary > n,
            "head dimensions must satisfy 1 <= n < boundary")
    require(type(precision) is int and precision >= 64, "head precision must be at least 64")
    with ctx.workprec(precision):
        basis = native.poly_basis(boundary)
        low = basis[:n]
        degree = _check_exact_images(low, residual)
        height = boundary-n
        C_high = native.coeffs(basis[n:], boundary)
        C_low = native.coeffs(low, n)
        V = (C_high*native.hankel(native.global_v_moments(boundary+n-2), boundary, n)
             * C_low.transpose())
        P = arb_mat(height, n)
        terms, cells = _geometry()
        active_cells = 0
        for a, b in cells:
            # LOW must be consecutive P_0,...,P_{n-1}; the native helper's
            # Taylor arrays are square with side len(low), never len(high).
            S, _, active = native.shifted_cell_images(low, terms, a, b)
            if active:
                active_cells += 1
                moments = native.integrate_power(a, b, boundary+n-2)
                P += C_high*native.hankel(moments, boundary, n)*S.transpose()
        require(active_cells == 4, "head reconstruction lost an active signed cell")
        R32 = arb_mat(height, n)
        # Legendre orthogonality proves all rows k > degree exactly zero.
        # For the fixed packet degree <= 223, so this applies only from k=224.
        end = min(boundary, degree+1)
        if end > n:
            C_residual_head = native.coeffs(basis[n:end], end)
            R = native.coeffs(residual, degree+1)
            moments = native.integrate_power(arb(-1), arb(1), end+degree-1)
            rectangle = (C_residual_head*native.hankel(moments, end, degree+1)
                         * R.transpose())
            for k in range(end-n):
                for j in range(n):
                    value = rectangle[k, j]
                    if n+k > residual[j].degree():
                        # Orthogonality is column-specific, not just the
                        # largest residual degree over the whole low space.
                        require(value.contains(0),
                                "individual residual degree zero excluded")
                        value = arb(0)
                    R32[k, j] = value
        return {"V": V, "P": P, "R32": R32}


def reference_pair(value: arb, published: list[int], bits: int,
                   label: str, *, parity_zero: bool = False) -> list[int]:
    """Check exact Arb endpoints first, then retain an outward 512-bit pair."""
    lo, hi = native.endpoints(value)
    if parity_zero:
        require(lo <= 0 <= hi, f"{label}: reconstructed parity interval excludes zero")
        # V and the symmetric shift/residual kernels commute with reflection.
        # Their form, image Gram and projected Gram pair opposite parities to 0.
        lo = hi = Fraction(0)
    denominator = 1 << bits
    require(Fraction(published[0], denominator) <= lo <= hi
            <= Fraction(published[1], denominator),
            f"{label}: independent interval is not contained in the source")
    scale = 1 << REFERENCE_BITS
    pair = [(lo*scale).__floor__(), (hi*scale).__ceil__()]
    require(Fraction(published[0], denominator) <= Fraction(pair[0], scale)
            <= Fraction(pair[1], scale) <= Fraction(published[1], denominator),
            f"{label}: outward reference receipt escaped the source")
    return pair


def _parity_counts() -> dict[str, int]:
    return {"entries": 0, "even_even": 0, "odd_odd": 0,
            "even_odd": 0, "odd_even": 0}


def _count(counts: dict[str, int], row: int, column: int) -> None:
    counts["entries"] += 1
    key = ("even" if row % 2 == 0 else "odd") + "_" + ("even" if column % 2 == 0 else "odd")
    counts[key] += 1


def _source_snapshot() -> dict[str, str]:
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
            for name in (*SOURCE_PATHS, AUDITOR_PATH)}


def audit(packet_path: Path) -> dict[str, Any]:
    """Capture the gzip bytes once and return a complete successful receipt."""
    raw = packet_path.read_bytes()
    packet_sha256 = hashlib.sha256(raw).hexdigest()
    packet = decode_json(gzip.decompress(raw))
    mu_raw = (ROOT/MU_INPUT).read_bytes()
    require(hashlib.sha256(mu_raw).hexdigest() == MU_INPUT_SHA256,
            "original chosen-mu input byte identity changed")
    original = decode_json(mu_raw)
    require(type(original) is dict and type(original.get("mu_lower_exact")) is str,
            "original input is missing its exact chosen mu")
    mu_exact = original["mu_lower_exact"]
    validate_packet(packet, mu_exact)
    sources = _source_snapshot()
    for name in SOURCE_PATHS:
        require(sources[name] == packet["source_sha256"][name],
                f"source byte identity mismatch: {name}")
    require(Path(native.__file__).resolve() == (ROOT/SOURCE_PATHS[-1]).resolve(),
            "native analytic helper was imported from a different path")
    print("Reconstructing all low and complete Gram entries at 2048 bits", file=sys.stderr, flush=True)
    rebuilt = reconstruct()
    require(rebuilt["residual_max_degree"] <= 223,
            "fixed residual degree bound failed")
    require(rebuilt["residual_signature"] == packet["residual_signature"],
            "exact residual polynomial signature mismatch")
    fresh_mu_lower, _ = native.endpoints(rebuilt["complement"])
    require(0 < Fraction(mu_exact) <= fresh_mu_lower,
            "chosen original mu exceeds the independent complement lower bound")
    matrices: dict[str, list[list[list[int]]]] = {}
    counts: dict[str, Any] = {"matrices": {}, "heads": {}, "scalars": 2}
    for name in ("A_K", "G_K"):
        rows = []
        count = _parity_counts()
        for i in range(DIMENSION):
            row = []
            for j in range(i, DIMENSION):
                row.append(reference_pair(rebuilt[name][i, j],
                           packet["matrices"][name][i][j-i], SOURCE_BITS,
                           f"{name}[{i},{j}]", parity_zero=bool((i-j) % 2)))
                _count(count, i, j)
            rows.append(row)
        require(count["entries"] == DIMENSION*(DIMENSION+1)//2,
                f"{name}: incomplete triangular reconstruction")
        matrices[name] = rows
        counts["matrices"][name] = count
    scalars = {name: reference_pair(rebuilt[name], packet[name], SOURCE_BITS, name)
               for name in ("delta", "complement")}
    precision = 2*packet["head_precision"]
    print(f"Reconstructing every rectangular head at {precision} bits", file=sys.stderr, flush=True)
    fresh_heads = reconstruct_heads(DIMENSION, packet["boundary"], precision,
                                    rebuilt["residual"])
    heads: dict[str, list[list[list[int]]]] = {}
    for name in ("V", "P", "R32"):
        rows = []
        count = _parity_counts()
        for k in range(DIMENSION, packet["boundary"]):
            row = []
            for j in range(DIMENSION):
                row.append(reference_pair(fresh_heads[name][k-DIMENSION, j],
                           packet["heads"][name][k-DIMENSION][j], SOURCE_BITS,
                           f"{name}[{k},{j}]", parity_zero=bool((k-j) % 2)))
                _count(count, k, j)
            rows.append(row)
        require(count["entries"] == (packet["boundary"]-DIMENSION)*DIMENSION,
                f"{name}: incomplete rectangular reconstruction")
        heads[name] = rows
        counts["heads"][name] = count
    require(_source_snapshot() == sources, "source bytes changed during the audit")
    return {
        "format": AUDIT_FORMAT, "status": "SOURCE_INPUTS_ACCEPTED",
        "passes_all_stored_intervals": True,
        "support": [3, 5], "dimension": DIMENSION, "residual_order": ORDER,
        "active_terms": [2, 3], "basis": "ordinary_unnormalized_legendre",
        "boundary": packet["boundary"], "bits": REFERENCE_BITS,
        "source_bits": SOURCE_BITS, "source_precision": 1024,
        "head_precision": packet["head_precision"],
        "reference_precision": NATIVE_PRECISION, "head_reference_precision": precision,
        "packet_sha256": packet_sha256,
        "source_sha256": {name: sources[name] for name in SOURCE_PATHS},
        "audit_source_sha256": {name: sources[name] for name in (AUDITOR_PATH, SOURCE_PATHS[-1])},
        "original_mu_input_sha256": MU_INPUT_SHA256, "mu_reference_exact": mu_exact,
        "mu_below_independent_complement_lower": True,
        "complement_lower_exact": str(fresh_mu_lower),
        "residual_signature": rebuilt["residual_signature"],
        "residual_max_degree": rebuilt["residual_max_degree"],
        "residual_head_zero_from": 224,
        "counts": counts, "matrices": matrices, "heads": heads, **scalars,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        # The exclusive create below also rejects a path created during the audit.
        require(not args.output.exists() and not args.output.is_symlink(),
                "output already exists")
        receipt = audit(args.packet)
        payload = (json.dumps(receipt, sort_keys=True, separators=(",", ":"),
                              allow_nan=False)+"\n").encode("utf-8")
        if args.output.suffix == ".gz":
            payload = gzip.compress(payload, mtime=0)
        with args.output.open("xb") as stream:
            stream.write(payload)
        print(json.dumps({"status": receipt["status"], "packet_sha256": receipt["packet_sha256"],
                          "output": str(args.output), "counts": receipt["counts"]},
                         sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "REJECTED", "error": str(exc)}, sort_keys=True),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
