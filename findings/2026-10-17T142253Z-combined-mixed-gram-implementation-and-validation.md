# Research implementation of the combined mixed low-to-tail Gram enclosure

- **Finding ID:** F-20261017-009
- **Created:** 2026-10-17T14:22:53Z
- **Last updated:** 2026-10-17T14:25:14Z
- **Type:** SOURCE_VERIFIED / mathematically justified research computation
- **Status:** VERIFIED for rigorous truncated mixed-image enclosures and residual-controlled **upper matrix-order** bounding; **NOT** a mathematical positivity result or accepted certificate
- **Baseline HEAD:** `a18746e437b52cdd0a3f0d4af1654df116be28de`; prior research-only SYS-3.1/3.2 documents remain uncommitted and unaltered
- **Computation:** X-20261017-002
- **Scope:** Narrow combined mixed-Gram research implementation, reference checks, conditioning measurement; frozen v1/v2 assembler, independent verifier, Lean and theorem profiles unchanged.

## Mathematical interface implemented

Define \(W_K=V+P_T+R_{T,K}\) on \(E_N=\operatorname{span}\{P_0,\ldots,P_{N-1}\}\), \(B_K=Q_NW_K|_{E_N}\), \(D_N=\operatorname{diag}(2/(2i+1))\). As proved in `C-0065` and source-audited in F-20261017-008,
\[
 G_{K,\mathrm{coord}}
   =\Big[\langle Q_NW_KP_i,Q_NW_KP_j\rangle\Big]_{ij}
   =\sum_{X,Y\in\{V,P_T,R_K\}} M_{XY}
       -(K_V+K_P+K_R)D_N^{-1}(K_V+K_P+K_R).
\]
The new independent research-only module `scripts/cert/mixed_gram_research.py` computes each diagonal image product \(M_{VV},M_{PP},M_{R_KR_K}\), the three *ordered* cross matrices \(M_{VP},M_{VR_K},M_{PR_K}\), their separately oriented adjoints, and the full low-space projection subtraction. It **does not** assume individual ordered cross products are symmetric. All active prime powers are summed with negative signed coefficients through existing certified prime-power terms; the \(2/3\) arithmetic interference already present in \(M_{PP}\) remains intact.

### Logarithmic \(V/P\) cross term

For each certified term \(m\), compressed shifts act on the two exact support intervals \([-1,1-\tau_m]\) and \([-1+\tau_m,1]\), with \(\tau_m=\log(m)/T\) enclosed by Arb and coefficient \(-\Lambda(m)/\sqrt m\). On each interval the translated \(P_j(x\pm\tau_m)\) is an ordinary polynomial with Arb coefficients. The implementation uses the proved cell-monomial formula
\[
 \int_a^b x^k v(x)\,dx
   =-\frac12\bigl[F_k^-(b)-F_k^-(a)
                     +F_k^+(b)-F_k^+(a)\bigr]
\]
and the explicit elementary logarithmic primitives from F-20261017-008. Exact \(x=\pm1\) logarithmic endpoint limits are used; every uncertain interior breakpoint must certify the log argument strictly positive. No `acb.integral` is invoked at singular endpoints. Polynomial and moment contractions are performed using Arb outward arithmetic with shared moment transforms to avoid quartic enumeration, but high-degree cancellation is still **measured rather than presumed absent**.

### \(V/R_K\), \(P/R_K\), and full Suzuki residual

`_residual_truncation_operator` supplies exact rational polynomial images \(R_KP_j\). The ordered \(M_{VR_K}\) uses the existing grouped exact rational whole-interval harmonic moments prior to conversion to Arb. \(M_{PR_K}\) uses certified two-sided translated supports and exact finite polynomial integrals, without assuming the ordered matrix is symmetric; an independent cell-local Legendre calculation cross-checks representative entries.

The true \(R_T\) is not replaced by \(R_K\). The current rigorous remainder \(\|R_T-R_K\|\le\delta_K\) is returned separately. For a specified exact rational \(\eta>0\), the full combined Gram satisfies
\[
  G_{\mathrm{full}}\preceq
  (1+\eta)G_K+(1+\eta^{-1})\delta_K^2D_N
\]
**in the unnormalized coordinate convention** (the operator-level identity has \(I\) instead of \(D_N\)). `rigorous_full_gram_upper` converts the Arb **entrywise** \(G_K\) intervals into an exact rational **Loewner** upper matrix using a symmetric center and rigorously summed row radii, then applies the full-residual formula. Merely comparing Arb matrix entries would not be a valid matrix-order bound.

For a **certified positive** full-tail \(\mu_N\), `rigorous_combined_schur_lower` independently uses the existing low-form \(\underline A=A_K-\delta_KD_N\), its own exact-rational matrix-order **lower** bound, and the certified \(\mu_N\) **lower** endpoint to return an exact rational **lower matrix-order enclosure** for
\[
 S_{\mathrm{comb}}=A_{\mathrm{full}}-\mu_N^{-1}G_{\mathrm{full}}.
\]
It refuses to construct that lower Schur bound if strict positive \(\mu_N\) is not established. Returning a lower matrix does **not** assert it is positive.

Exact opposite-parity zeros are imposed only after verifying each calculated interval contains the symmetry-forced zero. A mismatch fails closed; same-parity entries are retained with their mixed contributions. No global \(W^2\) domain assertion is needed.

## Independent controls

The focused new tests cover: cell moments split at an interior rational boundary against the pre-existing independent grouped whole-interval potential; exact \(\pm1\) endpoints; rejected ambiguous Arb boundaries; separate cell-local Legendre \(P/R_K\) pairings versus the new shifted-monomial evaluation; independently sampled high-precision `mpmath` direct-shift integrals for \(V/P\) (**NONPROOF control only**); mixed parity, residual normalization, an independently enlarged Legendre finite-tail projection lower bound, and exact rational row-radius Loewner control. A separate certified positive-complement example checks the lower Schur construction; invalid complement and invalid Young parameter must fail closed. The pre-existing grouped v2 regression suite is also retained.

## Measured precision/conditioning

The reproducible research profile `scripts/profile_mixed_gram_research.py` explicitly labels decimal width/runtimes as **diagnostics**, not proof values. With full rigorous Arb matrix construction, residual order 32 and support \(T=11/20\), the observed **largest outward rational interval width among upper-triangular combined \(G_K\) entries** was:

| Low \(N\) | Arb precision | Observed runtime | Maximum combined \(G_K\) entry width (approximate display) |
|---:|---:|---:|---:|
| 32 | 384 bits | 0.799 s | \(2.16064\times10^{-80}\) |
| 64 | 384 bits | 4.582 s | \(5.77321\times10^{-44}\) |
| 128 | 384 bits | 31.328 s | \(1.86013\times10^{30}\) |
| 128 | 768 bits | 32.903 s | \(4.61364\times10^{-86}\) |
| 192 | 1024 bits | 116.963 s | \(1.51810\times10^{-88}\) |
| 196 | 1024 bits | 136.252 s | \(7.49414\times10^{-84}\) |

The \(N=128\), Arb-384 enclosure is **mathematically containing but operationally useless** because of interval explosion. Increasing Arb precision to 768 bits on the *same implementation and dimension* drastically reduces its width without meaningful additional runtime. Both frozen-large reference dimensions have small entry widths at Arb 1024. This is **measured evidence** that a representation rewrite or new quadrature engine is **not presently necessary to obtain tight full mixed-Gram entries at these specific dimensions**, although precision choice and memory/performance outside them are not universally qualified. Per-entry tightness does **not** automatically imply that the full Schur lower matrix is positive; its eigenstructure and exact matrix-order check remain separate proof obligations.

The profile constructs the full combined \(G_K\) entries and the rigorous upper \(\overline G_{\mathrm{full}}\), but records only width diagnostics and representative \((0,0)\) upper values, not a serialized certificate. No new rigorous positive or negative Schur witness is claimed at \(N=192/196\), and the earlier four finite-tail obstruction tests remain INCONCLUSIVE.

## Scope and disposition

**Implementation status: COMPLETE for the specified research capability.** New bounded research-only source and focused tests provide a mathematically justified interval-complete mixed-image Gram and a full-residual Loewner majorant using the existing Arb/prime-power/residual/exact-rational infrastructure. Large-dimensional enclosure feasibility is *demonstrated* at \(N=192\) and \(196\) with Arb 1024, subject to the source-level mathematical analyses of the underlying components.

**Not established:** positivity of \(S_{\mathrm{comb}}\), any new support theorem, a new certificate, independent Rust evaluation of new analytical input enclosures, or RH. New matrix-order bound construction remains *generator-side* research with mathematical derivation and focused independent computational controls; it is not a closed independent exact verification contract. No production v1/v2 interfaces, acceptance profiles, whitelist, Rust verifier, Lean proof, orchestration baseline or old historical evidence was changed.

## Sources

- [Computational necessity](2026-10-17T134402Z-combined-gram-computational-necessity-assessment.md) — F-20261017-007.
- [Mixed moment source audit](2026-10-17T140216Z-mixed-gram-primitives-source-audit.md) — F-20261017-008.
- [Combined criterion and exact Gram](2026-10-17T130040Z-sys2-combined-criterion-mathematical-conclusion.md) — F-20261017-006 / C-0063..C-0066.
- [Reproducible focused validation evidence](../computations/2026-10-17T142253Z-mixed-gram-implementation/record.md) — X-20261017-002.
- [Research-only mixed Gram source](../scripts/cert/mixed_gram_research.py), [research width profile](../scripts/profile_mixed_gram_research.py), and [focused tests](../tests/test_mixed_gram_research.py).
