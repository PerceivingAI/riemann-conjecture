# Complete P20 reference from the retained larger source

- **Finding ID:** `F-20261025-002`
- **Created:** `2026-10-25T01:02:04Z`
- **Last updated:** `2026-10-25T01:02:04Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `PROVISIONAL`, complete reprojection written before original-version acceptance and numerical evaluation
- **Proposed claim:** C-0091
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
