# Complete P20 reference from the retained larger source

- **Finding ID:** `F-20261025-002`
- **Created:** `2026-10-25T01:02:04Z`
- **Last updated:** `2026-10-25T01:20:21Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`, source-conditional negative directions in both complete P20 parity sectors
- **Claim:** C-0091
- **Computation:** [X-20261025-002](../computations/2026-10-25T010204Z-complete-retained-reprojection/record.md)

## Question and source coverage

C-0090 selected N20 using certificates on the original P16 compression. Here the target is the entire P20 reference, including the promoted degrees16..19 and every low cross term, at unchanged T=1353/2048,K38.

Use the accepted C-0087 source with original low projection M312 and head boundary m1018. Its complete A_M and truncated mixed tail Gram G_M, plus signed V/P/RK heads above M, contain the information needed. This is a new consequence of old analytical inputs, not a fresh analytical generation or relabeling of their producer version.

## Exact reprojection identity

Let W_K=V+P+R_K, d_k=2/(2k+1), and t_k=(<P_k,W_K P_j>)_(j<N). The low matrix A_M contains the harmonic J-c_T diagonal in addition to W_K. For k>=N and j<N one has k!=j, so

\[
t_{k,j}=(A_M)_{k,j}\quad(N\le k<M).
\]

For M<=k<m, t_k is the sum of all three retained signed component rows. No component split is invented for the lower range. The new low matrix is the complete principal A_N=(A_M)_(j<N). Orthogonality gives

\[
G_N=(G_M)_{P_N}+\sum_{N\le k<M}t_k^*t_k/d_k.
\]

This includes every one of the newly exposed tail rows20..311. Dropping that finite prefix would omit real source energy.

## Complete reference majorant

Use the selected C-0088 lower mu20, displaying0.4726350157991974, and weights w_k=1/(mu20+H_k-H20). Splitting the full inverse-weighted truncated tail at m gives

\[
\boxed{U=w_m(G_M)_{P_N}
+\sum_{N\le k<M}w_kt_k^*t_k/d_k
+\sum_{M\le k<m}(w_k-w_m)t_k^*t_k/d_k.}
\]

All coefficients are nonnegative. This is identical to w_m G_N plus the finite weighted corrections after substituting the Gram identity. The unknown k>=m tail is paid through the remaining Gram. All signed correlations are preserved by summing source amplitudes before the rank-one products.

For an interval Loewner lower A^- and upper U^+, C-0085's complete source error gives

\[
S_{0,20}\succeq A^- -U^+-rD_{20},\qquad
r=\delta(1+2b/\mu20)+\delta^2/\mu20.
\]

Here delta is the full R_T-R_K bound and b remains the full cross norm pi/2+p+rho_global. The small double-tail residual norm is used only to certify mu20. It does not replace b. The inherited form/domain premises and C-0072 inverse ordering apply at N20, not just on P16.

A positive exact lower on both10-dimensional parity blocks would certify the complete P20 reference. A failed sufficient lower alone would not certify a negative reference; any negative conclusion needs the genuine full-source directional upper with its residual error.

## Original-version acceptance boundary

The original source/audit/result bytes and old source-v2 closure must be hash-bound. The original full frozen-selection checker and exact replay run in an isolated restoration of that version, including its earlier baseline inputs. The current version3 validator is not weakened or used to reinterpret old version2 bytes. Newly derived data use a separate research format and a separately organized native-receipt consequence audit.

## Initial status

No complete P20 sign, new support or production admission is claimed at creation. The initial derivation is preserved before subsequent verification/results are recorded. RH remains unresolved.

## Verified outcome — 2026-10-25T01:20:21Z

The complete P20 harmonic reference is not positive. Each ten-dimensional parity block has a retained rational trial with a strictly negative **full-reference upper**, not merely a failed sufficient lower. The trials use the ordinary Legendre mass and exact 2^48 coefficient grid.

| Parity | Full low-form upper | Full inverse-energy lower | Full-reference upper |
| --- | ---: | ---: | ---: |
| Even | 5.49620519673116e-5 | 6.74301189147085e-5 | -1.24680669473969e-5 |
| Odd | 1.02419185055060e-7 | 1.44173624229759e-7 | -4.17544391746990e-8 |

These are decimal displays of outward exact rational bounds in `complete-reference-v1.json`. Physical squared masses display0.9999999999999972 and0.9999999999999998. The directional proof first bounds the finite weighted W_K energy from below, then subtracts the full residual amplitude through reverse triangle. The low-form upper separately pays delta times the physical mass. Unknown higher inverse energy is nonnegative; omitting it in this lower cannot manufacture a negative reference upper.

The original source-v2 full frozen-selection checker and exact replay pass in an isolated old source tree. The new evaluator inherits the original352-bit source and independently accepted512-bit analytical receipt; it does not regenerate their analytical inputs or force them through the later version3 validator. A separately organized Arb1536 evaluator reconstructs all998 combined rows20..1017, restores every newly exposed row20..311 and checks420 A/U triangular entries. It confirms both negative directional bounds and all full-error charges.

Both finite-operator regressions pass. Actual dropped-prefix, altered-new-low-degree19, borrowed-eight-dimensional-witness, forged-negative-upper and rewritten-original-version controls reject with exit2 and no success output. Exact replay passes. Isolated restoration of20 captured source/environment files and32 exact retained inputs reruns original-version acceptance, reproduces the exact replay receipt byte-for-byte and reproduces every independent audit field except elapsed time.

The original derivation is preserved as `derivation-v1.md`; source-version1, inputs, commands, timings and rejection artifacts are sealed in X-20261025-002. Assessment/audit/replay take about2.84/7.09/2.66 seconds; original-version acceptance takes16.02 seconds. These are retained-input consequence costs, not fresh complete analytical generation costs.

## Interpretation and boundaries

C-0090 remains correct: it certifies the old P16 compression under the changed projection. It did not certify the four added low coordinates. The complete assessment establishes that passing this compression was insufficient to select a positive enlarged reference. A positive principal compression does not control the added coordinates and their joint couplings.

Further head rows or precision cannot make this exact fixed reference positive. No claim is made here about every residual-only scalar variant at N20, a minimum positive projection, or the true Schur/Weil form. C-0087 already supplies a source-conditional positive full reference at this support with N312. This negative smaller reference neither contradicts that result nor rejects the overall method. Production admissions remain eight v1, zero v2 and one v3; RH remains unresolved.
