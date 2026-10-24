# Both parity blocks certify the whole harmonic reference at T=3/5

- **Finding ID:** `F-20261024-003`
- **Created:** `2026-10-24T15:40:06Z`
- **Last updated:** `2026-10-24T15:40:06Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` for the source-conditional whole-reference inequality by analytical acceptance and exact rational replay; research only, not production theorem admission
- **Claim:** C-0084
- **Evidence:** [X-20261024-003](../computations/2026-10-24T153012Z-weighted-reference-continuation/record.md)

## Statement

At unchanged T=3/5,N=192,K=32, active arithmetic [2,3] and the original exact rational mu, the accuracy-selected evaluation boundary m=626 yields strictly positive rational lower matrices for both 96-dimensional parity blocks of

\[
S_0=A-B^*C_0^{-1}B,\qquad C_0e_k=(\mu+H_k-H_{192})e_k.
\]

With the ordinary Legendre mass D_jj=2/(2j+1), exact positive rationals g_even and g_odd satisfy S0_even>=g_even D_even and S0_odd>=g_odd D_odd. Thus S0>=min(g_even,g_odd)D>0 on the entire192-dimensional low space, including complex coefficient vectors.

| Parity block | Dimension | Decimal display of exact mass-normalized lower |
| --- | ---: | ---: |
| Even | 96 | 1.5816571091127121e-09 |
| Odd | 96 | 5.6610701001944871e-07 |

The decimals are displays, not exact endpoints. Exact rationals, witnesses and their source/result byte bindings are in `data/analysis.stdout.json`, `data/result-summary.json` and the assessment artifact in X-20261024-003. These are reference-block gaps, not full-Weil-form spectral gaps.

## Derivation and complete error

C-0082 provides S0>=L_m=Aminus-Uplus_m-rD, retaining the complete signed V/P/R32 source, all cross-direction terms, the infinite omitted tail and full residual. Source, low-space projection and reference mu were not changed to obtain positivity. The evaluation sequence224,316,626 was selected by the uniform weight-halving rule before the new source values, not by searching for favorable signs.

For each parity p, the retained exact lower-triangular dyadic W_p has a nonzero diagonal and exact Gershgorin margin eta_p>0 for W_p L_p W_p^T. Set t_p=trace(W_p D_p W_p^T)>0 and g_p=eta_p/t_p. Since W_p D_p W_p^T<=t_p I, invertible congruence gives L_p>=g_p D_p. The diagnostic CLI independently rechecks the witnesses and this physical-mass calculation, using actual parity degrees rather than consecutive block positions. Reflection and the exact zero cross-parity entries combine the two inequalities.

The global omitted-tail diagnostic displays 6.3283667291444949; the full residual allowance displays 6.8816432788767504e-13. The trace diagnostic is not an eigenvalue or a scalar replacement for the correlated final matrix. Native exact interval bounds include all coefficient, radius and inverse-weight uncertainty before Loewner inflation.

## Analytical input acceptance

| Accepted input | Slots | Reconstruction provenance |
| --- | ---: | --- |
| Raw A_K and complete Q192 G_K upper triangles | 37,056 | Inherited independently accepted low data; exact ancestor hashes, source definitions and copied enclosures rechecked |
| Complement and full residual scalars | 2 | Inherited independently accepted scalars; original exact mu retained and validity rechecked |
| Rectangular V/P/R32 head pairings | 249,984 | Every component freshly reconstructed at6144 bits against3072-bit generation |
| Total | 287,042 | Explicit pinned-low/fresh-head provenance, not all-fresh low reconstruction |

Low/Gram construction/reference precisions remain1024/2048. Outward publication/reference receipts use352/512 bits. All192 exact residual images are freshly reconstructed and checked; per-column degree zeros and opposite parity are justified, not silently omitted.

Packet SHA256: `0d63fe8f879138ddfa60cbf6dab2f00190dea624dc91c77c3a5556394d8f1fda`. Audit SHA256: `0fd0aa63bead51efcc863df9bbbef56a07688be8fbee0b382081fbaa536606e2`. Assessment SHA256: `5f0836bf8b67d6e84c0973fc7de127aa5b728771617c9b02ea244d05f2dfc3c2`.

## Conditional full-form consequence

Under C-0072, the true Schur complement is above S0, and the full tail form has positive lower mu. Domain-safe square completion therefore proves strict positivity of the constructed closed form: if the low part is nonzero, its true-Schur contribution is positive; if it is zero, the nonzero tail is positive. C-0063's identification on the admissible Suzuki smooth-test class transfers this as a **source-conditional localized Weil-positivity implication at T=3/5**. No equality of the full canonical operator domains or direct evaluation of the true inverse is needed.

This is a research-level mathematical consequence under the documented Suzuki, Arb, exact-polynomial and source/domain premises. It is not clean-source production certificate generation, independent Rust acceptance or Lean-kernel verification of the source identity. The admission inventory remains eight frozen v1, zero v2 and one v3 C-0067. Do not silently promote this research result to an admitted theorem.

## Verification and lessons

Source generation, pinned-low/fresh-head analytical acceptance, both-block exact assessment, separate exact replay and the mass-gap diagnostic completed. Altering the odd witness's exact margin caused the real replay CLI to reject with exit2 and no success output. Read-only independent mathematical review accepted the outcome and conditional implication; it executed no numerical work.

All six owned executions exited/reaped, with no timeout. New elapsed numerical execution was 238.588436299935 seconds. The earlier m626 timeout remains preserved in its original bundle; this separate run required no change to the scientific implementations or fixed mathematical inputs. No permanent test, production verifier or formal source changed, and prior tests were not rerun as a substitute for the new actual calculation.

The earlier negative conservative lower did not reject this reference. Preserving more weighted tail information now certifies every low direction, not just the original successful odd trial. This is a specific implemented and verified refinement, not a claim of a new general Schur principle, literature-first support record, comparative cost advantage or scalable all-support proof. No further cutoff is required to decide this fixed positive reference; the null next-boundary field reflects the decisive classification, not exhaustion of the1024 scope.

## Dependencies and limits

C-0063 through C-0065, C-0072, C-0082, and the independently accepted retained low evidence are premises. C-0081 and C-0083 supply earlier comparisons, not substitutes for this both-block proof. All previous source versions, failures, outputs and research records remain unchanged. This result neither establishes an unbounded support-covering family nor proves RH.
