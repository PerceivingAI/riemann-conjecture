"""SYS-2.5 scoped research diagnostic: rigorously test projected-tail obstruction.

This script is NOT a certificate generator, a production Schur assembler, or an
admission mechanism.  It reuses the existing rigorous assembly without changing
the v1/v2 contracts, and uses historical exact rational witnesses as test inputs.
"""
from __future__ import annotations

import argparse
import json
import time
import zipfile
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx
from scripts.cert.legendre_schur import harmonic
from scripts.cert.multi_prime_legendre_schur import (
    _arb_fraction,
    assemble_multi_prime_schur,
)

EVIDENCE_DIR = Path("computations/2026-10-01T215617Z-multi-prime-assembly-performance/data")
ZIP_NAMES = {
    192: "phase8-rayleigh-cli-N192-p384-cell-legendre.zip",
    196: "phase8-rayleigh-cli-N196-p384-cell-legendre.zip",
}


def read_historical_direction(n: int) -> tuple[list[Fraction], dict]:
    with zipfile.ZipFile(EVIDENCE_DIR / ZIP_NAMES[n]) as bundle:
        payload = json.loads(bundle.read("rayleigh-inputs.json"))
    if (payload["dimension"] != n or payload["support"] != "11/20"
            or payload["parity"] != "even" or len(payload["vector"]) != n // 2):
        raise ValueError("historical exact witness identity mismatch")
    vector = [Fraction(0) for _ in range(n)]
    for k, item in enumerate(payload["vector"]):
        vector[2 * k] = Fraction(item)
    if not any(vector):
        raise ValueError("historical witness is zero")
    return vector, payload


def evaluate(n: int, m: int, a: dict, prec: int) -> dict:
    vector, historical = read_historical_direction(n)
    norms = a["norms"]
    v = [(j, _arb_fraction(x)) for j, x in enumerate(vector) if x]
    exact_norm_sq = sum((vector[j] * vector[j] * norms[j] for j in range(n)), Fraction())
    norm_sq = _arb_fraction(exact_norm_sq)
    delta = a["delta_R"]
    mu = a["mu"] + _arb_fraction(harmonic(n) - harmonic(m))
    if not mu.lower() > 0:
        return {"N": n, "M": m, "status": "NO_CERTIFIED_POSITIVE_COMPLEMENT",
                "mu": str(mu), "mu_lower": str(mu.lower())}

    # The canonical assembled low block is A_K - delta_R D.
    # Therefore A_full <= A_assembler + 2 delta_R D in form order.
    u_a_lower = arb(0)
    for i, ci in v:
        for j, cj in v:
            u_a_lower += ci * a["A"][i][j] * cj
    a_full_upper = (u_a_lower + 2 * delta * norm_sq).upper()

    # For N <= k < M, A[k,i] = <P_k,(V+P+R_K)P_i>.
    # J, -c_T and the delta_R diagonal correction vanish across k != i.
    projected_sq = arb(0)
    nonzero_rows = []
    for k in range(n, m):
        pairing = sum((ci * a["A"][k][i] for i, ci in v), arb(0))
        projected_sq += pairing * pairing / _arb_fraction(norms[k])
        if pairing.lower() > 0 or pairing.upper() < 0:
            nonzero_rows.append(k)

    # ||Q_{N,M}(V+P+R)u|| >= sqrt(projected_sq) - delta_R ||u||.
    p_lower = projected_sq.lower()
    if p_lower < 0:
        p_lower = arb(0)
    residual = delta.upper() * norm_sq.upper().sqrt()
    amplitude = p_lower.sqrt() - residual
    # A strict negative upper Rayleigh quotient disqualifies the new
    # sufficient condition for exactly this N, mu and historical u.
    if amplitude.lower() > 0:
        gram_lower = amplitude.lower() * amplitude.lower()
    else:
        gram_lower = arb(0)
    s_upper = (a_full_upper - gram_lower / mu.upper()).upper()
    conclusion = "CERTIFIED_NEGATIVE" if s_upper < 0 else "INCONCLUSIVE"
    return {
        "N": n, "M": m,
        "historical_vector": ZIP_NAMES[n],
        "historical_vector_bits": historical["vector_bits"],
        "status": conclusion,
        "mu_lower": str(mu.lower()),
        "mu_upper": str(mu.upper()),
        "delta_R_upper": str(delta.upper()),
        "norm_squared_exact": str(exact_norm_sq),
        "a_full_rayleigh_upper": str(a_full_upper),
        "projected_truncated_norm_sq_lower": str(p_lower),
        "residual_norm_allowance": str(residual),
        "projected_full_norm_sq_lower": str(gram_lower),
        "new_schur_rayleigh_upper": str(s_upper),
        "nonzero_certified_projection_rows": nonzero_rows,
        "semantics": ("negative is decisive for the specific chosen positive"
                      " mu_N and finite dimension; inconclusive does not"
                      " establish positivity of S_comb"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tail-dimension", type=int, default=204)
    parser.add_argument("--precision", type=int, default=384)
    parser.add_argument("--residual-order", type=int, default=32)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()
    if args.tail_dimension <= 196:
        raise ValueError("tail dimension must exceed 196")
    if args.precision < 128 or args.residual_order < 8:
        raise ValueError("rigor controls insufficient")

    start = time.perf_counter()
    with ctx.workprec(args.precision):
        data = assemble_multi_prime_schur(
            n=args.tail_dimension, prec=args.precision,
            residual_order=args.residual_order,
            support_num=11, support_den=20,
            require_positive_mu=False,
        )
        if [t.m for t in data["active_terms"]] != [2, 3]:
            raise ValueError("active prime-power set differs from [2,3]")
        results = [evaluate(n, args.tail_dimension, data, args.precision)
                   for n in (192, 196)]
    payload = {
        "role": "SYS-2.5-PRE_THEOREM_PROJECTED_OBSTRUCTION_ONLY",
        "support_T": "11/20",
        "arb_precision_bits": args.precision,
        "residual_order": args.residual_order,
        "assembled_dimension_M": args.tail_dimension,
        "elapsed_seconds_observational": round(time.perf_counter() - start, 3),
        "results": results,
        "not_proved": "positivity of full combined Schur or localized Weil form",
    }
    target = Path(args.output_json)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for result in results:
        print(result["N"], result["status"],
              "rayleigh upper:", result.get("new_schur_rayleigh_upper", "<none>"),
              flush=True)
    print("Saved:", target, flush=True)


if __name__ == "__main__":
    main()
