"""Fixed research-only weighted source-tail bracket, not a positivity verifier.

Same T=3/5,N=192,K=32 trial and exact reference. Accuracy selects B=874
before new source evaluation; no support/trial/cutoff or precision search.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

from flint import arb, arb_poly, ctx, fmpq, fmpq_poly

from scripts.cert.legendre_schur import legendre_polynomials
from scripts.cert.mixed_gram_research import _shift_poly
from scripts.cert.multi_prime_legendre_schur import _potential_matrices, _residual_truncation_operator
from scripts.weil_joint_source_tail import _contained, _integral
from scripts.weil_jump_refinement_check import INPUTS, _require
import scripts.verify_combined_schur_analytic_entries as ref

JOINT = (
    "computations/2026-10-23T185253Z-joint-source-tail/data/result.json",
    "67eba074fdc79e48934fbb2ae80212fa920f62bddc6a324e500bf8c4a296c2c8",
)
B = 874
PRECISION = 4096
BITS = 352
REFERENCE_BITS = 512


def _publish(value: arb, bits: int) -> list[str]:
    lo, hi = ref.endpoints(value)
    scale = 1 << bits
    return [str(Q((lo*scale).__floor__(), scale)), str(Q((hi*scale).__ceil__(), scale))]


def _evaluate(z: list[Q], independent: bool) -> tuple[dict[str, arb], dict[str, dict[str, arb]], str]:
    precision = 2*PRECISION if independent else PRECISION
    with ctx.workprec(precision):
        if independent:
            basis = ref.poly_basis(B)
            u = sum((basis[j]*fmpq(c.numerator, c.denominator)
                     for j, c in enumerate(z) if c), fmpq_poly())
        else:
            ordinary = legendre_polynomials(B-1)
            basis = [fmpq_poly([fmpq(c.numerator, c.denominator) for c in p]) for p in ordinary]
            u = sum((basis[j]*fmpq(c.numerator, c.denominator)
                     for j, c in enumerate(z) if c), fmpq_poly())
        norm = sum((c*c*Q(2, 2*j+1) for j, c in enumerate(z)), Q())
        primitive = (u*u).integral()
        exact_norm = primitive(1)-primitive(-1)
        _require(Q(int(exact_norm.p), int(exact_norm.q)) == norm,
                 "exact trial norm mismatch")
        fractions = [Q(int(c.p), int(c.q)) for c in u.coeffs()]
        _require(u.degree() == 191 and all(not u[j] for j in range(0, len(u), 2)),
                 "trial parity/degree mismatch")
        if independent:
            coefficients = ref.exact_residual_coefficients(32)
            residual = ref.residual_polys([u], 32, fmpq(3, 5), coefficients)[0]
            delta, _ = ref.bound_tail(arb(3)/5, coefficients, 32)
            moments = ref.global_v_moments(191+B-1)
            vlow = sum((arb(c)*moments[j] for j, c in enumerate((u*u).coeffs()) if c), arb(0))
        else:
            images, rlow, _, delta = _residual_truncation_operator([fractions], 32, precision, 3, 5)
            residual = images[0]
            v, _ = _potential_matrices([fractions], precision)
            vlow = v[0][0]
        _require(residual.degree() <= 223 and all(not residual[j] for j in range(0, len(residual), 2)),
                 "residual image parity/degree mismatch")
        upoly = arb_poly([arb(c) for c in u.coeffs()])
        tau = [arb(m).log()*5/3 for m in (2, 3)]
        c = [arb(m).log()/arb(m).sqrt() for m in (2, 3)]
        _require(1 < tau[0] < tau[1] < 2, "uncertified first-window topology")
        positive = [(tau[0]-1, tau[1]-1, (0,)), (tau[1]-1, arb(1), (0, 1))]
        geometry = ([(lo, hi, active, 1, 2) for lo, hi, active in positive] if not independent else
                    [(-hi, -lo, active, -1, 1) for lo, hi, active in reversed(positive)] +
                    [(lo, hi, active, 1, 1) for lo, hi, active in positive])
        shifted = {}
        for side in ((-1, 1) if independent else (1,)):
            for j in range(2):
                values = (ref.translate(u, -side*tau[j], len(u)) if independent
                          else _shift_poly(u, -side*tau[j]))
                shifted[side, j] = arb_poly(values)
        cells = []
        plow = arb(0)
        for lo, hi, active, side, factor in geometry:
            q = -sum((shifted[side, j]*c[j] for j in active), arb_poly())
            powers = (ref.integrate_power(lo, hi, 191+B-1) if independent else
                      [(hi**(j+1)-lo**(j+1))/(j+1) for j in range(191+B)])
            plow += factor*_integral(upoly*q, powers)
            cells.append((q, factor, powers))
        rp = (u*residual).integral()
        rpair = rp(1)-rp(-1)
        if not independent:
            _require((arb(rpair)-rlow[0][0]).contains(0), "residual pairing mismatch")
        jump = sum((ref.harmonic(j)*fmpq(c.numerator, c.denominator)**2*fmpq(2, 2*j+1)
                    for j, c in enumerate(z) if c), fmpq(0))
        c_t = (2*arb.pi()*arb(3)/5).log()+arb.const_euler()
        atrunc = arb(jump)-c_t*ref.qarb(norm)+vlow+plow+arb(rpair)
        heads = {}
        for k in range(211, B, 2):
            scale = (arb(2*k+1)/2).sqrt()
            if independent:
                product = u*basis[k]
                vk = sum((arb(a)*moments[j] for j, a in enumerate(product.coeffs()) if a), arb(0))
            else:
                # C-0075 exact logarithmic pairing for k>degree(u), same odd parity.
                vk = ref.qarb(2*sum((a/Q(k*(k+1)-j*(j+1))
                                    for j, a in enumerate(z) if a), Q()))
            pk = arb_poly([arb(a) for a in basis[k].coeffs()])
            qk = sum((factor*_integral(pk*q, powers) for q, factor, powers in cells), arb(0))
            if k < 224:
                primitive = (basis[k]*residual).integral()
                rk = arb(primitive(1)-primitive(-1))
            else:
                rk = arb(0)
            row = {"V": scale*vk, "q": scale*qk, "R32": scale*rk}
            row["sum_truncated"] = sum(row.values(), arb(0))
            heads[str(k)] = row
        signature = hashlib.sha256(("|".join(map(str, u.coeffs()))+"\n"+
                                    "|".join(map(str, residual.coeffs()))).encode()).hexdigest()
        return {"a_truncated": atrunc, "delta": delta}, heads, signature


def _square(pair: list[str]) -> tuple[Q, Q]:
    lo, hi = map(Q, pair)
    return (Q() if lo <= 0 <= hi else min(lo*lo, hi*hi), max(lo*lo, hi*hi))


def _weighted_error_bounds(lo: Q, hi: Q, weight: Q, delta: Q, norm: Q) -> tuple[Q, Q]:
    _require(0 <= lo <= hi and weight > 0, "invalid inverse-energy endpoints")
    _, epsilon = ref.endpoints(ref.qarb(delta)*ref.qarb(weight*norm).sqrt())
    root_lo, _ = ref.endpoints(ref.qarb(lo).sqrt())
    _, root_hi = ref.endpoints(ref.qarb(hi).sqrt())
    return max(Q(), root_lo-epsilon)**2, (root_hi+epsilon)**2


def _consequences(original: dict, source: dict, audit: dict, joint: dict,
                  scalars: dict, heads: dict) -> dict:
    mu = Q(original["mu_lower_exact"])
    norm = Q(source["exact_trial_mass_norm"])
    delta = Q(source["delta_upper_exact"])
    Mlo, Mhi = map(Q, joint["scalars"]["joint_tail"])
    h = Q(audit["exact"]["prefix_only_reference_upper"])
    lam = {192: mu}
    for k in range(193, B+1):
        lam[k] = lam[k-1]+Q(1, k)
    Slo = Shi = near_lo = near_hi = mass_lo = mass_hi = Q()
    correction = Q()
    for text, row in heads.items():
        k = int(text)
        lo, hi = _square(row["sum_truncated"])
        Slo += lo/lam[k]
        Shi += hi/lam[k]
        if k < 224:
            near_lo += lo/lam[k]
            near_hi += hi/lam[k]
        else:
            _require(row["R32"] == ["0", "0"], "unexpected high residual polynomial coefficient")
            mass_lo += lo
            mass_hi += hi
            correction += (lam[B]-lam[k])*hi
    tail_lo, tail_hi = max(Q(), Mlo-mass_hi), Mhi-mass_lo
    _require(0 <= tail_lo <= tail_hi, "inconsistent complete omitted-tail mass")
    Dlower = max(lam[224]*Mlo, lam[B]*Mlo-correction)
    cauchy_ceiling = Mhi*Mhi/Dlower
    with ctx.workprec(2*PRECISION):
        Jlo, Jhi = _weighted_error_bounds(Slo, Shi+tail_hi/lam[B], 1/lam[211], delta, norm)
        _, near_upper = _weighted_error_bounds(near_lo, near_hi, 1/lam[211], delta, norm)
    # The old concentration bound covers the same J, so intersect rather than add.
    Jlo = max(Jlo, Q(joint["exact"]["J_concentration_lower"]))
    atrunc_lo, atrunc_hi = map(Q, scalars["a_truncated"])
    alo, ahi = atrunc_lo-delta*norm, atrunc_hi+delta*norm
    _require(alo <= Q(original["a_full_rayleigh_upper_exact"]), "original low-form upper inconsistency")
    ahi = min(ahi, Q(original["a_full_rayleigh_upper_exact"]))
    Plo = Q(audit["exact"]["known_inverse_lower"])
    Phi = Q(audit["exact"]["known_inverse_upper"])
    reflo, refhi = alo-Phi-Jhi, ahi-Plo-Jlo
    _require(reflo <= refhi and Jlo <= Jhi, "reversed reference bracket")
    cauchy_floor = h-near_upper-cauchy_ceiling
    exact = {
        "a_full_lower": alo, "a_full_upper": ahi,
        "prefix_lower": Plo, "prefix_upper": Phi,
        "M224_lower": Mlo, "M224_upper": Mhi,
        "band_inverse_energy_lower": Slo, "band_inverse_energy_upper": Shi,
        "remaining_mass_lower": tail_lo, "remaining_mass_upper": tail_hi,
        "remaining_inverse_energy_upper": tail_hi/lam[B],
        "a_priori_tail_error_budget": h/4, "a_priori_tail_error_ceiling": Mhi/lam[B],
        "J_full_lower": Jlo, "J_full_upper": Jhi,
        "reference_lower": reflo, "reference_upper": refhi,
        "harmonic_moment_lower": Dlower, "scalar_cauchy_expression_upper": cauchy_ceiling,
        "near_full_inverse_energy_upper": near_upper,
        "scalar_cauchy_reported_upper_floor": cauchy_floor,
    }
    return {
        "exact": {k: str(v) for k, v in exact.items()},
        "display": {k: float(v) for k, v in exact.items()},
        "scalar_cauchy_rule_excluded": cauchy_floor > 0,
        "status": ("POSITIVE_DIAGONAL_REFERENCE_DIRECTION" if reflo > 0 else
                   "NEGATIVE_DIAGONAL_REFERENCE_DIRECTION" if refhi < 0 else "INCONCLUSIVE"),
        "scope": "one unchanged trial and exact diagonal reference; not a positive matrix, true Schur sign or Weil/RH result",
    }


def run() -> dict:
    started = time.perf_counter()
    packets = []
    for name, digest in (*INPUTS, JOINT):
        raw = Path(name).read_bytes()
        _require(hashlib.sha256(raw).hexdigest() == digest, f"input identity: {name}")
        packets.append(json.loads(raw))
    original, source, audit, joint = packets
    for packet in (original, source, joint):
        for name, digest in packet["source_sha256"].items():
            _require(hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest,
                     f"source identity: {name}")
    _require((original["support"], original["dimension"], original["K"], original["active_terms"])
             == ("3/5", 192, 32, [2, 3]), "source configuration changed")
    z = list(map(Q, original["trial_rational_vector"]))
    _require(len(z) == 192 and all(not z[k] for k in range(0, 192, 2)), "trial parity changed")
    Mhi = Q(joint["scalars"]["joint_tail"][1])
    h = Q(audit["exact"]["prefix_only_reference_upper"])
    mu = Q(original["mu_lower_exact"])
    _require(mu > 0 and h > 0 and Mhi > 0, "nonpositive accuracy-selection premise")
    chosen = 224
    lam = mu+sum((Q(1, j) for j in range(193, 225)), Q())
    while Mhi/lam > h/4:
        _require(chosen < 1024, "accuracy-selected boundary outside fixed scope")
        lam += Q(1, chosen+1)+Q(1, chosen+2)
        chosen += 2
    _require(chosen == B and ((4*B+512+255)//256)*256 == PRECISION,
             "fixed predeclared accuracy/precision contract changed")
    print("evaluating fixed 4096-bit weighted source band", file=sys.stderr, flush=True)
    generated, heads, signature = _evaluate(z, False)
    with ctx.workprec(PRECISION):
        scalars = {k: _publish(v, BITS) for k, v in generated.items()}
        published = {k: {name: _publish(v, BITS) for name, v in row.items()} for k, row in heads.items()}
    print("reconstructing fixed 8192-bit weighted source band", file=sys.stderr, flush=True)
    checked, check_heads, check_signature = _evaluate(z, True)
    _require(signature == check_signature, "exact trial/residual reconstruction mismatch")
    with ctx.workprec(2*PRECISION):
        reference_scalars = {k: _publish(v, REFERENCE_BITS) for k, v in checked.items()}
        reference_heads = {k: {name: _publish(v, REFERENCE_BITS) for name, v in row.items()}
                           for k, row in check_heads.items()}
        for k, value in checked.items():
            _require(_contained(value, scalars[k]), "scalar reference containment: "+k)
        for k, row in check_heads.items():
            for name, value in row.items():
                _require(_contained(value, published[k][name]), "head reference containment: "+k+"/"+name)
        for left, right in ((scalars, reference_scalars),):
            for k in left:
                a, b = map(Q, left[k]); c, d = map(Q, right[k])
                _require(a <= c <= d <= b, "rounded scalar reference containment")
        for k, row in published.items():
            for name, pair in row.items():
                a, b = map(Q, pair); c, d = map(Q, reference_heads[k][name])
                _require(a <= c <= d <= b, "rounded head reference containment")
        for k in range(211, 224, 2):
            for name in ("V", "q"):
                _require(_contained(check_heads[str(k)][name], joint["head_coefficients"][str(k)][name]),
                         "prior joint head compatibility")
        _require(ref.endpoints(checked["delta"])[1] <= Q(source["delta_upper_exact"])
                 and ref.endpoints(generated["delta"])[1] <= Q(source["delta_upper_exact"]),
                 "accepted full residual allowance not sufficient")
    result = _consequences(original, source, audit, joint, scalars, published)
    result.update({
        "format": "fixed-weighted-source-tail-v1", "support": "3/5", "N": 192, "K": 32,
        "original_prefix_end": 211, "residual_tail_start": 224, "evaluation_boundary": B,
        "boundary_selection": "smallest even B>=224 with w_B*M224_upper<=h/4, before new source evaluation",
        "generator_precision_bits": PRECISION, "reference_precision_bits": 2*PRECISION,
        "publication_bits": BITS, "reference_publication_bits": REFERENCE_BITS,
        "scalar_intervals": scalars, "head_coefficients": published,
        "reference_scalar_intervals": reference_scalars, "reference_head_coefficients": reference_heads,
        "reference_receipts": "outward 512-bit rounded enclosures; full raw intervals also checked during execution",
        "scalar_containments": len(scalars), "head_containments": sum(map(len, published.values())),
        "prior_joint_head_compatibility_checks": 14,
        "trial_and_residual_polynomial_sha256": signature,
        "input_sha256": dict((*INPUTS, JOINT)),
        "consumer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_sha256": {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in (
            "scripts/weil_joint_source_tail.py", "scripts/weil_jump_refinement_check.py",
            "scripts/verify_combined_schur_analytic_entries.py", "scripts/cert/legendre_schur.py",
            "scripts/cert/mixed_gram_research.py", "scripts/cert/multi_prime_legendre_schur.py",
            "scripts/cert/prime_power_terms.py", "scripts/cert/residual_kernel.py", "pyproject.toml", "uv.lock")},
        "new_full_matrix_or_inverse": False, "new_trial_or_support": False,
        "original_full_A_G_matrices_reconstructed": False,
        "new_directional_low_form_scalar_reconstructed": True,
        "actual_true_schur_or_weil_sign": "UNDETERMINED", "theorem_admission": False,
        "internal_seconds": time.perf_counter()-started,
    })
    return result


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        result = run()
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"weighted source-tail calculation rejected: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
