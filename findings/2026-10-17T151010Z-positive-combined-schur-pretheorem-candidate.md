# Exact rational positive candidate for the combined low-to-tail sufficient matrix at T=11/20

- **Finding ID:** F-20261017-011
- **Created:** 2026-10-17T15:10:10Z
- **Last updated:** 2026-10-17T15:12:44Z
- **Type:** COMPUTATIONAL_POSITIVE_CANDIDATE / research-side exact rational sign under documented analytic source enclosures
- **Status:** **POSITIVE_CANDIDATE — PRE-THEOREM; NO THEOREM ADMISSION OR RH CONCLUSION**
- **Evidence:** X-20261017-003; complete rational input packet, complete rational congruence witness and an independent exact checker with SHA-256 fingerprints
- **Mathematical dependencies:** C-0063, C-0064, C-0065 (closed Suzuki-scaled form, complete combined Gram, conditional tail-Schur positivity); F-20261017-010 (generator capability audit)
- **Research separation:** This finding records an **executed** rigorous computational outcome, not unexecuted research plans.

## Exact result stated with its trust boundary

At exact \(T=11/20\), low \(E_{192}=\mathrm{span}\{P_0,\ldots,P_{191}\}\) in ordinary unnormalized Legendre coordinates, with active arithmetic terms exactly \(\{2,3\}\), define
\[
B=Q_{192}(V+P_T+R_T)|_{E_{192}},\qquad
S_{\mathrm{comb}}=A_{192}-\mu_{192}^{-1}B^*B.
\]
The full complementary form lower bound has a rigorously positive lower endpoint \(\underline\mu_{192}\) (approximately 0.566208306786). With full Suzuki residual order-32 allowance \(\delta_K\) (upper approximately \(9.82803\times10^{-16}\)), exact \(\eta=2^{-24}\), all mixed \(VP,VR_K,PR_K\) ordered image terms, the complete \(KD^{-1}K\) projection, and rigorous Arb-1024 interval enclosures, the research generator computed exact rational
\[
  \underline S=\underline A_{192}
            -\underline\mu_{192}^{-1}\overline G_{\mathrm{full}}
  \preceq S_{\mathrm{comb}}.
\]

**An invertible EXACT dyadic rational matrix \(W\)** (lower triangular, diagonal nonzero, denominator \(2^{48}\)) was retained in the proof packet. A separate exact rational checker reconstructed \(\underline S\) from the full dyadic input intervals, recomputed \(W\underline SW^{\mathsf T}\), independently checked every Gershgorin row and matched the asserted minimum rational margin. That minimum exact Gershgorin margin is **strictly greater than zero** (decimal approximation \(0.9999999993343024\)); the entire exact fraction is in the proof packet. By congruence, **\(\underline S\succ0\)**. Accordingly the prior mathematical implication yields **strict positivity of the combined sufficient matrix**, conditional on the Suzuki/Arb analytical source premises.

The float Cholesky/eigenvalue calculations only **proposed** a rational witness; the mathematical positive-definiteness test was **entirely exact rational**. The positive result did not follow from a float eigenvalue, lack of negative trial witnesses, or from an old grouped factor-3 matrix.

## What has NOT been established

The independent checker **reconstructed exact rational consequences**; it does **not** independently certify every upstream transcendental Arb enclosure or the full Suzuki-domain identity. This result therefore remains in the **research-generator / independently verified rational-implications** trust level, **not** the frozen v1/v2 independent closed theorem verifier. There is **no admitted v2 theorem**, no Rust certificate for the combined criterion, no Lean formalization of the new analytic source inputs, and no RH proof.

The rigorously negative old **factor-3 sufficient matrices** at the same support/dimension are not contradicted: those were **weaker distinct sufficient bounds**. Negative \(\underline S\) would have been inconclusive; here its **positive** exact rational congruence is the decisive direction.

This is **one support and one dimension**. The predetermined secondary \(N=196\) experiment was correctly stopped, not performed, because the first case produced a positive candidate. This does not establish a continuation through all supports or all dimensions.

## Full reproducibility

See [X-20261017-003](../computations/2026-10-17T150153Z-combined-schur-bounded-test/record.md) and its complete hashed rational matrix, dyadic witness, exact checker output and source commands. Frozen one-prime positive controls and 44/44 focus tests passed, exact interval-width gate passed, and the analytic and numerical trust limitations are stated in the computation record.

**Disposition:** A **new positive pre-theorem research candidate** for the named combined criterion has been established with independent exact rational matrix checking. All promotion or generalization is explicitly deferred; no theorem/admission changes follow automatically.
