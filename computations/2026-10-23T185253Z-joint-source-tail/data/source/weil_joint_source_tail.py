"""Fixed research-only complete source-tail enclosure, not a theorem verifier.

T=3/5, N=192, K=32, L=224; generator 1536 bits, reconstruction 3072 bits.
No search, precision retry, matrix assembly, or theorem admission.
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
from scripts.cert.mixed_gram_research import _shift_poly, logarithmic_cell_moments
from scripts.cert.multi_prime_legendre_schur import _potential_matrices
from scripts.weil_jump_refinement_check import INPUTS, _require
import scripts.verify_combined_schur_analytic_entries as ref

L = 224
BITS = 352
MODEL_INPUT = (
    "computations/2026-10-23T174341Z-jump-refinement-controls/data/canonical-result.json",
    "77ec109a1718ab2efa1e6c94fe015e94a9dcb1da3252550f9d15b76b54459887",
)


def _integral(poly: arb_poly, moments: list[arb]) -> arb:
    return sum((c * moments[j] for j, c in enumerate(poly.coeffs()) if c != 0), arb(0))


def _publish(value: arb) -> list[str]:
    lo, hi = ref.endpoints(value)
    scale = 1 << BITS
    return [str(Q((lo * scale).__floor__(), scale)),
            str(Q((hi * scale).__ceil__(), scale))]


def _contained(value: arb, pair: list[str]) -> bool:
    lo, hi = ref.endpoints(value)
    return Q(pair[0]) <= lo <= hi <= Q(pair[1])


def _evaluate(z: list[Q], independent: bool) -> tuple[dict[str, arb], dict[str, list[arb]], str]:
    """Distinct basis/shift/log-moment paths; shared trusted Arb and projection algebra."""
    precision = 3072 if independent else 1536
    with ctx.workprec(precision):
        if independent:
            basis = ref.poly_basis(L)
            u = sum((basis[k] * fmpq(c.numerator, c.denominator)
                     for k, c in enumerate(z) if c), fmpq_poly())
        else:
            coefficients = legendre_polynomials(L - 1)
            basis = [fmpq_poly([fmpq(c.numerator, c.denominator) for c in row])
                     for row in coefficients]
            u = sum((basis[k] * fmpq(c.numerator, c.denominator)
                     for k, c in enumerate(z) if c), fmpq_poly())
        _require(u.degree() == 191 and all(not u[k] for k in range(0, len(u), 2)),
                 "unexpected exact trial parity/degree")
        exact_norm = (u * u).integral()
        mass = exact_norm(1) - exact_norm(-1)
        _require(Q(int(mass.p), int(mass.q)) == sum(
            (c*c*Q(2, 2*k+1) for k, c in enumerate(z)), Q()), "exact basis norm mismatch")
        identity = hashlib.sha256("|".join(map(str, u.coeffs())).encode()).hexdigest()
        upoly = arb_poly([arb(c) for c in u.coeffs()])
        endpoint = arb(u(1))
        tau = [arb(m).log() * 5 / 3 for m in (2, 3)]
        c = [arb(m).log() / arb(m).sqrt() for m in (2, 3)]
        _require(1 < tau[0] < tau[1] < 2, "uncertified first-window topology")
        a = [t - 1 for t in tau]
        whole = {name: arb(0) for name in ("q2", "s2", "r2", "vs", "vr", "sr", "vq")}
        heads = {name: [] for name in ("V", "q", "s")}
        positive = [(a[0], a[1], (0,)), (a[1], arb(1), (0, 1))]
        if independent:
            geometry = [(-hi, -lo, active, -1, 1) for lo, hi, active in reversed(positive)]
            geometry += [(lo, hi, active, 1, 1) for lo, hi, active in positive]
        else:
            geometry = [(lo, hi, active, 1, 2) for lo, hi, active in positive]
        cells = []
        for lo, hi, active, side, factor in geometry:
            q = arb_poly()
            for j in active:
                shifted = (ref.translate(u, -side*tau[j], len(u)) if independent
                           else _shift_poly(u, -side*tau[j]))
                q -= arb_poly(shifted) * c[j]
            s = endpoint * side * sum((c[j] for j in active), arb(0))
            r = q - s
            powers = (ref.integrate_power(lo, hi, 2*191) if independent
                      else [(hi**(j+1)-lo**(j+1))/(j+1) for j in range(2*191+1)])
            logs = (ref.cell_v_moments(lo, hi, 2*191) if independent
                    else logarithmic_cell_moments(lo, hi, 2*191))
            for name, poly in (("q2", q*q), ("s2", arb_poly([s*s])),
                               ("r2", r*r), ("sr", r*s)):
                whole[name] += factor * _integral(poly, powers)
            for name, poly in (("vs", upoly*s), ("vr", upoly*r), ("vq", upoly*q)):
                whole[name] += factor * _integral(poly, logs)
            # Higher powers are needed only for the polynomial head pairings.
            headpowers = (ref.integrate_power(lo, hi, 191+L-1) if independent
                          else [(hi**(j+1)-lo**(j+1))/(j+1) for j in range(191+L)])
            cells.append((q, s, factor, headpowers))
        if independent:
            vm = ref.global_v_moments(191+L-1)
            v2m = ref.global_v_moments(2*191, squared=True)
            v2 = sum((arb(value)*v2m[j] for j, value in enumerate((u*u).coeffs()) if value), arb(0))
        else:
            as_fractions = [Q(int(value.p), int(value.q)) for value in u.coeffs()]
            _, v2matrix = _potential_matrices([as_fractions], precision)
            v2 = v2matrix[0][0]
            harmonics = [fmpq(0)]
            for j in range(1, 191+L+3):
                harmonics.append(harmonics[-1] + fmpq(1, j))
            rational_moments = [(2*harmonics[j+2]-harmonics[(j+2)//2])/(j+1)
                                if j % 2 == 0 else fmpq(0) for j in range(191+L)]
        for k in range(1, L, 2):
            scale = (arb(2*k+1)/2).sqrt()
            product = u*basis[k]
            if independent:
                vk = sum((arb(value)*vm[j] for j, value in enumerate(product.coeffs()) if value), arb(0))
            else:
                rational = sum((value*rational_moments[j]
                                for j, value in enumerate(product.coeffs()) if value), fmpq(0))
                ordinary_mass = (product.integral()(1)-product.integral()(-1))
                vk = arb(rational)-arb.const_log2()*arb(ordinary_mass)
            qk, sk = arb(0), arb(0)
            pk = arb_poly([arb(value) for value in basis[k].coeffs()])
            for q, s, factor, powers in cells:
                qk += factor * _integral(pk*q, powers)
                sk += factor * _integral(pk*s, powers)
            for name, value in (("V", vk), ("q", qk), ("s", sk)):
                heads[name].append(scale*value)
        vg = [v+s for v, s in zip(heads["V"], heads["s"], strict=True)]
        regular = [q-s for q, s in zip(heads["q"], heads["s"], strict=True)]
        joint = [v+q for v, q in zip(heads["V"], heads["q"], strict=True)]
        values = dict(whole)
        values.update({
            "v2": v2,
            "G": v2+2*whole["vs"]+whole["s2"]-sum((x*x for x in vg), arb(0)),
            "C": whole["vr"]+whole["sr"]-sum((x*y for x, y in zip(vg, regular, strict=True)), arb(0)),
            "regular_tail": whole["r2"]-sum((x*x for x in regular), arb(0)),
            "joint_tail": v2+2*whole["vq"]+whole["q2"]-sum((x*x for x in joint), arb(0)),
            "potential_tail": v2-sum((x*x for x in heads["V"]), arb(0)),
            "arithmetic_tail": whole["q2"]-sum((x*x for x in heads["q"]), arb(0)),
            "step_tail": whole["s2"]-sum((x*x for x in heads["s"]), arb(0)),
        })
        discrepancy = values["joint_tail"]-(values["G"]+2*values["C"]+values["regular_tail"])
        dl, dh = ref.endpoints(discrepancy)
        _require(dl <= 0 <= dh, "direct/correlated tail identity mismatch")
        for name in ("G", "regular_tail", "joint_tail", "potential_tail", "arithmetic_tail", "step_tail"):
            _require(ref.endpoints(values[name])[0] > 0, f"unresolved nonnegative quantity: {name}")
        return values, heads, identity


def run() -> dict[str, object]:
    started = time.perf_counter()
    packets = []
    for name, digest in INPUTS:
        raw = Path(name).read_bytes()
        _require(hashlib.sha256(raw).hexdigest() == digest, f"input identity: {name}")
        packets.append(json.loads(raw))
    original, source, audit = packets
    _require((original["support"], original["dimension"], original["K"], original["active_terms"])
             == ("3/5", 192, 32, [2, 3]), "unexpected original configuration")
    _require(source["residual_image_degree"] == L-1, "unexpected residual image degree")
    z = list(map(Q, original["trial_rational_vector"]))
    _require(len(z) == 192 and all(not z[k] for k in range(0, 192, 2)), "unexpected trial")
    norm = sum((x*x*Q(2, 2*k+1) for k, x in enumerate(z)), Q())
    _require(norm == Q(source["exact_trial_mass_norm"]), "physical norm mismatch")
    for packet in (original, source):
        for name, digest in packet["source_sha256"].items():
            _require(hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest,
                     f"source identity: {name}")
    model_raw = Path(MODEL_INPUT[0]).read_bytes()
    _require(hashlib.sha256(model_raw).hexdigest() == MODEL_INPUT[1], "prior control identity")
    model = json.loads(model_raw)
    print("evaluating fixed 1536-bit joint scalar", file=sys.stderr, flush=True)
    generated, heads, uhash = _evaluate(z, False)
    with ctx.workprec(1536):
        published = {name: _publish(value) for name, value in generated.items()}
        head_intervals = {str(k): {name: _publish(values[i]) for name, values in heads.items()}
                          for i, k in enumerate(range(1, L, 2))}
    print("reconstructing fixed 3072-bit joint scalar", file=sys.stderr, flush=True)
    checked, check_heads, check_hash = _evaluate(z, True)
    _require(uhash == check_hash, "independent exact trial disagreement")
    with ctx.workprec(3072):
        _require(all(_contained(checked[name], pair) for name, pair in published.items()),
                 "scalar reference not contained in published intervals")
        _require(all(_contained(check_heads[name][i], head_intervals[str(k)][name])
                     for i, k in enumerate(range(1, L, 2)) for name in heads),
                 "head reference not contained in published intervals")
        prefix_checks = 0
        for k in range(193, 211, 2):
            i = (k-1)//2
            old = source["moments"][str(k)]
            vp = [str(Q(x, 1 << BITS)) for x in old["V"]["published_dyadic"]]
            qp = [str(Q(old["P2"]["published_dyadic"][j]+old["P3"]["published_dyadic"][j],
                        1 << BITS)) for j in range(2)]
            _require(_contained(check_heads["V"][i], vp) and _contained(check_heads["q"][i], qp),
                     "accepted prefix V/q incompatibility")
            prefix_checks += 2
        ml, mh = map(Q, model["exact"]["step_tail_norm2"])
        sl, sh = ref.endpoints(checked["step_tail"])
        _require(ml <= sl <= sh <= mh, "prior step model incompatibility")
        joint_upper = Q(published["joint_tail"][1])
        correlated_upper = Q(published["G"][1])+2*Q(published["C"][1])+Q(published["regular_tail"][1])
        _require(joint_upper >= 0 and correlated_upper >= 0, "negative nonnegative-mass upper")
        cap = min(joint_upper, correlated_upper)
        delta = Q(source["delta_upper_exact"])
        full = (ref.qarb(cap).sqrt()+ref.qarb(delta)*ref.qarb(norm).sqrt())**2
        _, full_upper = ref.endpoints(full)
        mu = Q(original["mu_lower_exact"])
        mass_lower = Q(audit["exact"]["omitted_mass_lower"])
        h = Q(audit["exact"]["prefix_only_reference_upper"])
        _require(mu > 0 and delta >= 0 and mass_lower > 0 and h > 0, "invalid inherited scalar premise")
        weight = 1/(mu+sum((Q(1, j) for j in range(193, L)), Q()))
        concentration_lower = weight*max(Q(), mass_lower-full_upper)
        reference_upper = h-concentration_lower
        exact = {"joint_tail_upper": str(joint_upper), "correlated_tail_upper": str(correlated_upper),
                 "truncated_tail_cap": str(cap), "full_source_tail_upper": str(full_upper),
                 "collective_residual_norm_upper": str(ref.endpoints(ref.qarb(delta)*ref.qarb(norm).sqrt())[1]),
                 "omitted_mass_lower": str(mass_lower), "prefix_only_reference_upper": str(h),
                 "weight_223": str(weight), "J_concentration_lower": str(concentration_lower),
                 "reference_directional_upper": str(reference_upper),
                 "tail_cap_needed_for_negative_upper": str(mass_lower-h/weight)}
        old_control = Q(model["exact"]["full_source_control_upper"])
        exact["prior_full_source_control_upper"] = str(old_control)
        improved = full_upper < old_control
    return {
        "format": "fixed-joint-source-tail-v1", "role": "research-only complete scalar tail; no theorem admission",
        "support": "3/5", "N": 192, "K": 32, "L": L,
        "generator_precision_bits": 1536, "reference_precision_bits": 3072, "publication_bits": BITS,
        "exact_trial_polynomial_sha256": uhash, "input_sha256": dict((*INPUTS, MODEL_INPUT)),
        "scalars": published, "head_coefficients": head_intervals,
        "scalar_containments": len(published), "head_containments": 3*(L//2),
        "reference_scalars": {name: [str(x) for x in ref.endpoints(value)] for name, value in checked.items()},
        "reference_head_coefficients": {
            str(k): {name: [str(x) for x in ref.endpoints(values[i])] for name, values in check_heads.items()}
            for i, k in enumerate(range(1, L, 2))
        },
        "accepted_prefix_compatibility_checks": prefix_checks,
        "prior_step_model_contains_reconstruction": True,
        "full_source_upper_improves_prior_control": improved,
        "independent_source_reconstruction_accepted": True,
        "reconstruction_scope": "distinct exact basis, four signed cells vs doubled positive cells, Taylor vs Horner shifts, and log/whole moments; shared Arb and projection algebra",
        "exact": exact, "display": {name: float(Q(value)) for name, value in exact.items()},
        "status": "NEGATIVE_DIAGONAL_REFERENCE_DIRECTION" if reference_upper < 0 else "INCONCLUSIVE",
        "actual_reference_sign": "STRICTLY_NEGATIVE" if reference_upper < 0 else "UNDETERMINED",
        "true_schur_or_weil_sign": "UNDETERMINED", "full_joint_correlation_bound_evaluated": True,
        "full_residual_restored": True, "full_matrix_or_inverse_assembled": False,
        "original_A_G_independently_reconstructed": False,
        "source_sha256": {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in (
            "scripts/weil_joint_source_tail.py", "scripts/weil_jump_refinement_check.py",
            "scripts/verify_combined_schur_analytic_entries.py", "scripts/cert/legendre_schur.py",
            "scripts/cert/mixed_gram_research.py", "scripts/cert/multi_prime_legendre_schur.py",
            "scripts/cert/prime_power_terms.py", "scripts/cert/residual_kernel.py", "pyproject.toml", "uv.lock")},
        "internal_seconds": time.perf_counter()-started,
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        result = run()
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"joint source-tail calculation rejected: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
