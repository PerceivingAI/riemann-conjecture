# Harmonic-tail inverse majorant: domain-safe ordering and limits of a negative screen

- **Finding ID:** `F-20261022-001`
- **Created:** `2026-10-22T18:30:11Z`
- **Last updated:** `2026-10-22T18:37:16Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` — conditional written form argument, separately reviewed; input-identity/scalar checks and small source-composition smoke executed. Not a new positivity certificate or Lean proof.
- **Claim:** `C-0072`
- **Code baseline:** `172469536bdce79757e591835c3b1331a861167d`; analytical implementations unchanged.

## Statement and assumptions

Work in the Suzuki-scaled local form setting of C-0063–C-0065, with `0<T<pi/2`, ordinary Legendre polynomials `P_k`, squared masses `d_k=2/(2k+1)`, orthonormal modes `e_k=P_k/sqrt(d_k)`, and harmonic eigenvalues `J e_k=H_k e_k`. The complete signed source is

\[
\mathfrak l=\mathfrak j+\mathfrak v+\langle\cdot,(P_T+R_T-c_TI)\cdot\rangle,
\quad v(x)=-\tfrac12\log(1-x^2)\ge0.
\]

The identification with the original smooth-test Weil functional is an existing Suzuki-source premise, not rederived here. The unitary scaling is `(U_T f)(x)=sqrt(T)f(Tx)`; no additional `T` or `2T` multiplier belongs in the form. Both signed translations occur in each `P_m=-(Lambda(m)/sqrt(m))S_{log(m)/T}`. The residual `R_T` is complete.

Let `E_N=span(P_0,...,P_{N-1})`, `F_N=E_N^perp`, `Q_N` the orthogonal tail projection, `A` the exact low form, and `B=Q_N(V+P_T+R_T)|E_N`. The tail form `c` is the restriction of the closed form to

\[
D(\mathfrak c)=F_N\cap D(J^{1/2})\cap D(V^{1/2}).
\]

Assume a rigorous real `mu>0` obtained from the bounded-perturbation estimate, so that the **stronger** inequality

\[
\mathfrak c[q]\ge\mathfrak j[q]-(H_N-\mu)\|q\|^2
\tag{1}
\]

holds on this domain. The usual construction `mu <= H_N-c_T-sum_m c_m b_m-rho_R`, with `b_m >= ||S_tau||` and `rho_R >= ||R_T||`, establishes (1) by dropping `V>=0`. Merely knowing `c[q]>=mu||q||^2` without (1) would not justify harmonic growth in the reference.

Define the positive diagonal reference on the full infinite tail by

\[
C_0e_k=(\mu+H_k-H_N)e_k,\qquad k\ge N,
\quad w_k=(\mu+H_k-H_N)^{-1}.
\]

For `G=B*B` and `T_k u=<e_k,Bu>`, the finite whole-tail majorant is

\[
U_M=w_M G+\sum_{N\le k<M}(w_k-w_M)T_k^*T_k,\qquad M\ge N.
\tag{2}
\]

Then

\[
A-\mu^{-1}G\preceq A-U_M
\preceq A-B^*C_0^{-1}B
\preceq A-B^*C^{-1}B,
\tag{3}
\]

where `C` is the self-adjoint operator associated with the restricted tail form.

## Derivation and domain check

The form-domain inclusion has the direction

\[
D(\mathfrak c)\subseteq D(\mathfrak c_0)=F_N\cap D(J^{1/2}).
\]

Both forms are closed and densely defined on `F_N`, and bounded below by `mu I`. For any `z` in that Hilbert space,

\[
\langle z,C^{-1}z\rangle
=\sup_{q\in D(\mathfrak c)}
 (2\operatorname{Re}\langle z,q\rangle-\mathfrak c[q])
\le\sup_{q\in D(\mathfrak c_0)}
 (2\operatorname{Re}\langle z,q\rangle-\mathfrak c_0[q])
=\langle z,C_0^{-1}z\rangle.
\]

Thus `C^-1 <= C0^-1 <= mu^-1 I`; equality of form domains is unnecessary. No application of the unbounded `V` to arbitrary tail vectors is used. The exact square completion is legal because `C^-1 Bu` lies in `D(C)`, hence in the tail form domain.

Parseval gives `G=sum_{k>=N} T_k* T_k` and
`B* C0^-1 B=sum_{k>=N} w_k T_k* T_k`. For `k>=M`, `w_k<=w_M`; replacing precisely those weights by `w_M` proves (2) is an upper bound. It does **not** discard the remaining infinite tail. Also `U_M<=mu^-1 G`, proving (3). The refinement is monotone:

\[
U_M-U_{M+1}=(w_M-w_{M+1})
\left(G-\sum_{k=N}^{M}T_k^*T_k\right)\succeq0.
\]

These are standard positive-form and spectral arguments specialized to the existing source, not an originality claim or an all-support positivity mechanism.

## Exact one-sided predicate and its scope

For a fixed real rational low vector `u=sum_i z_i P_i`, suppose full-source bounds satisfy
`a_up>=<u,Au>`, `g_low<=||Bu||^2`. Its norm is `sum_i z_i^2 d_i`, not the Euclidean coefficient norm. An arbitrary finite set of outward truncated-moment intervals `[l_k,h_k]` may be used, provided omitted finite terms are dropped only as nonnegative corrections.

If `||R-R_K||<=delta` and `||u||<=1`, then

\[
t_k=\langle e_k,(V+P_T+R)u\rangle
\in I_k=[l_k-\delta,h_k+\delta],
\quad d_k^{\rm abs}=\operatorname{dist}(0,I_k).
\]

For indices `N<=k<M` with verified intervals,

\[
\langle u,(A-U_M)u\rangle
\le a_{\rm up}-w_Mg_{\rm low}
-\sum_k(w_k-w_M)(d_k^{\rm abs})^2.
\tag{4}
\]

All weights and endpoint comparisons can be exact rational arithmetic after analytical enclosure. Correlated residual errors do not invalidate separate conservative enlargements. Already full-source `a_up,g_low` are not corrected a second time. For an exactly odd vector and reflection-preserving complete source, even-index moments vanish exactly.

A strict negative right side in (4) rejects **only `A-U_M` at the specified parameters**. It does **not** reject the exact diagonal-inverse reference `A-B* C0^-1 B`, the exact Schur complement, or the Weil form. Conversely, a nonnegative upper is inconclusive, not positive evidence. Full low-space positivity, including both parity sectors in the proper mass metric, would be a different assertion. No new target moments or new majorant sign were evaluated in this review.

## Checks actually executed

### Original input identity and scalar prerequisites

The original [SYS-6.4 packet](../computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json) has SHA-256 `44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b`. All five embedded analytical/probe source fingerprints match the current bytes. Its `T=3/5,N=192,K=32`, Arb-1024 and `[2,3]` metadata match the retained record. The original negative sign was not rerun.

Exact coefficient inspection found 192 entries, exactly 96 nonzero odd entries, zero even entries, and denominators dividing `2^20`. Direct mass-norm computation gives

```text
23089135979572240883279966641158374553152726041409248460599174419749932317988269165097485132472763971467942068266605362267
/
23089136706817477019784453685055190827087574074158698964636991041265655492253334303495421639675454645940456793619562496000
```

This is inside the stored norm enclosure and strictly below one; decimal display `0.9999999685027099`. The stored positive `mu` lower and `delta` upper were separately enclosed in the correct directions using `bound_tail` and the independently coded Bernoulli coefficients in `scripts/verify_combined_schur_analytic_entries.py` at 2048 bits. Strict activation of `[2,3]`, exclusion of `4`, `1<tau_m<2` for each active shift, and `2T<pi` were certified with Arb. All 33 residual coefficients matched exactly. Scalar-check elapsed time was approximately `0.0022 s`.

This adds independent reconstruction of these **scalar prerequisites only**. It does not independently reconstruct the original `A` and `G` directional bounds or all matrix entries. Their original generator-source-qualified trust remains explicit.

### Sparse source-composition smoke

Existing functions were exercised at `T=3/5` with the ordinary polynomial `u=P_1+P_3/7`, test degrees `[5,7,9]`, and residual order 8. The sparse basis has four orthogonal polynomials; no contiguous matrix or mixed-Gram assembly was needed.

- Generator at 256 bits: `_potential_matrices`, `assemble_active_prime_power_operator`, `_residual_truncation_operator`.
- Separate reference at 512 bits: independent polynomial recurrence, whole-potential moments, direct binomial translated-cell integration of **both signed shifts**, and exact split-kernel residual images from `verify_combined_schur_analytic_entries.py`.
- Observed: three V, three P, and three residual comparisons passed; independently generated basis and residual polynomials matched exactly. Elapsed source-composition time was approximately `0.0099 s`.

This is a small capability smoke, **not** high-degree conditioning, a target-scale benchmark, independent acceptance of new target moments, or a positivity test. Shared Arb arithmetic remains part of both analytical paths' trust base.

### Residual image-degree guard

Kernel truncation degree is not image degree. For odd kernel power `d`, integrating `|x-y|^d y^i` across the split `y=x` can produce degree `i+d+1`. The exact coefficient at kernel degree 1 is `-1/48`, and the independently coded action of `|x-y|` on `y^191` has degree 193. At order 32 and input degree at most 191, a safe image-degree bound is **223**, not 32 or 65. High-mode residual pairings cannot be discarded merely because the kernel was polynomially truncated. The full residual remainder must still be included.

## Dependencies and verification limits

- C-0063, C-0064, C-0065; C-0058 bounded-perturbation complement; external Suzuki normalization R-0028 already registered in those premises.
- [Closed-form domain derivation](2026-10-17T115900Z-scaled-weil-operator-domain-and-low-tail-maps.md), especially the local residual, form restriction and mass conventions.
- [SYS-6.4 record](../computations/2026-10-18T090311Z-sys6-selective-support/record.md) for the preserved vector and original A/G trust scope.
- Current source: `scripts/cert/prime_power_terms.py`, `multi_prime_legendre_schur.py`, `residual_kernel.py`, and the separate `scripts/verify_combined_schur_analytic_entries.py` helper formulas. Its complete `run()` remains fixed to `T=11/20`; it was not invoked as though it accepted arbitrary support.

A separate read-only mathematical review independently checked the domain inclusion, inverse order, entire-tail majorant, residual enlargement and interpretation. The executable checks used locked-environment CPython 3.14.0 with python-flint/Arb. No analytical source was changed, no test suite or certificate replay was run, and no Lean acceptance is claimed. Historical artifacts and their earlier interpretations remain unchanged.

## Significance and limits

This establishes a domain-safe comparison and a valid one-sided rejection predicate under stated local source assumptions. It distinguishes finite-majorant failure from failure of the exact inverse reference. The implemented sparse-basis source operations were exercised without claiming unmeasured high-degree performance.

RH remains unresolved. Admissions remain eight frozen v1, zero v2 and one v3 C-0067. This finding admits no support, does not prove a positive sufficient matrix, does not extend the residual enclosure beyond `2T<pi`, and does not establish an unbounded support-covering positivity family.

## Reproducing the lightweight checks

From the repository root, pass the following Python block to `uv run --locked python -c`. It checks input identity and the small source composition, not the original negative predicate or any unevaluated high-mode screen. All assertions must pass before its final output. The analytical source revision is the baseline above.

```python
import hashlib, json, time
from pathlib import Path
from fractions import Fraction as Q
from flint import arb, ctx, fmpq
from scripts.cert.legendre_schur import legendre_polynomials
from scripts.cert.multi_prime_legendre_schur import (
    _potential_matrices, _residual_truncation_operator,
)
from scripts.cert.prime_power_terms import (
    _exact_polynomials, _exact_inner, assemble_active_prime_power_operator,
)
from scripts.cert.residual_kernel import _suzuki_residual_series_coefficients
import scripts.verify_combined_schur_analytic_entries as ref

start = time.perf_counter()
raw = Path("computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b"
p = json.loads(raw)
assert (p["support"], p["dimension"], p["K"], p["arb_precision_bits"], p["active_terms"]) == ("3/5", 192, 32, 1024, [2, 3])
assert len(p["source_sha256"]) == 5
assert all(hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest
           for path, digest in p["source_sha256"].items())
z = list(map(Q, p["trial_rational_vector"]))
assert len(z) == 192 and sum(bool(x) for x in z) == 96
assert all(z[i] == 0 for i in range(0, 192, 2))
assert all((1 << 20) % x.denominator == 0 for x in z)
norm = sum((x*x*Q(2, 2*i+1) for i, x in enumerate(z)), Q())
nl, nu = map(Q, p["trial_norm_exact_enclosure"])
assert 0 < nl <= norm <= nu < 1
with ctx.workprec(2048):
    t = arb(3)/5
    c = ref.exact_residual_coefficients(32)
    assert tuple(c) == _suzuki_residual_series_coefficients(32)
    delta, rho = ref.bound_tail(t, c, 32)
    mu = ref.qarb(ref.harmonic(192)) - (2*arb.pi()*t).log() - arb.const_euler()
    mu -= sum((arb(m).log()/arb(m).sqrt() for m in (2, 3)), arb(0)) + rho
    assert 0 < Q(p["mu_lower_exact"]) <= ref.endpoints(mu)[0]
    assert 0 < ref.endpoints(delta)[1] <= Q(p["delta_upper_exact"])
    assert arb(3).log() < 2*t < arb(4).log() and 2*t < arb.pi()
    assert all(1 < arb(m).log()/t < 2 for m in (2, 3))
assert c[1] == fmpq(-1, 48)
assert ref.monomial_kernel_power(1, 191).degree() == 193

polys = legendre_polynomials(9)
u = [(polys[1][j] if j < len(polys[1]) else Q()) + Q(1, 7)*polys[3][j]
     for j in range(4)]
basis = [u, polys[5], polys[7], polys[9]]
exact = _exact_polynomials(basis)
assert ref.poly_basis(10) == _exact_polynomials(polys)
with ctx.workprec(256):
    v, _ = _potential_matrices(basis, 256)
    arith = assemble_active_prime_power_operator(basis, 3, 5, 256)
    images, r, _, _ = _residual_truncation_operator(basis, 8, 256, 3, 5)
assert [term.m for term in arith.terms] == [2, 3]
other_images = ref.residual_polys(exact, 8, fmpq(3, 5), ref.exact_residual_coefficients(8))
assert images == other_images
with ctx.workprec(512):
    for j, k in enumerate((5, 7, 9), 1):
        product = exact[j]*exact[0]
        vm = ref.global_v_moments(product.degree())
        vr = sum((ref.qarb(a)*vm[i] for i, a in enumerate(product.coeffs())), arb(0))
        assert v[j][0].overlaps(vr)
        pr = arb(0)
        for m in (2, 3):
            tau, coefficient = arb(m).log()/(arb(3)/5), arb(m).log()/arb(m).sqrt()
            for shift, a, b in ((tau, arb(-1), 1-tau), (-tau, -1+tau, arb(1))):
                shifted = ref.translate(exact[0], shift, len(exact[0]))
                moments = ref.integrate_power(a, b, k+3)
                pr -= coefficient*sum(
                    (ref.qarb(x)*y*moments[i+h]
                     for i, x in enumerate(exact[j].coeffs())
                     for h, y in enumerate(shifted)), arb(0))
        assert arith.p_matrix[j][0].overlaps(pr)
        assert r[j][0].contains(arb(_exact_inner(exact[j], other_images[0])))
print("PASS input identity, exact norm, scalar prerequisites, 3 V/P/R comparisons")
print("Elapsed seconds:", time.perf_counter()-start)
```

Documented-block replay: `uv run --locked python -c <block above>` exited **0**, printing `PASS input identity, exact norm, scalar prerequisites, 3 V/P/R comparisons`. Internal check time was approximately **0.0131 s** in CPython 3.14.0 / python-flint 0.9.0. This replay executed the block extracted from this file; it did not invoke a target-scale evaluation or the original negative sign checker.
