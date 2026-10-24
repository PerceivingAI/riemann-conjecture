# Jump-resolved source tails with signed remainder correlation

- **Finding ID:** `F-20261023-004`
- **Created:** `2026-10-23T17:43:41Z`
- **Last updated:** `2026-10-23T18:10:37Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` — independently reviewed paper-level identities and bounds, fixed exact/Arb controls, and a retained-input arithmetic-model comparison. Not an evaluated full joint-tail bound, positivity theorem or Lean proof.
- **Claims:** C-0077, C-0078.
- **Evidence:** [X-20261023-002](../computations/2026-10-23T174341Z-jump-refinement-controls/record.md).

## Question and unchanged source

C-0076 excluded sign resolution by one variation-envelope family; it did not reject the actual source or every refinement. Here the signed arithmetic jumps are retained explicitly rather than compressed into an absolute variation constant. The fixed research source remains T=3/5,N=192,K=32, the same exact odd trial, active terms [2,3], the same accepted prefix and inherited A/G premises. No trial, support or source formula is changed.

Work on unweighted L2(-1,1), with ordinary P_k, orthonormal e_k=sqrt((2k+1)/2)P_k, and Q_L the projection onto k>=L. Put q=mathcal P_T u. All formulas below refer to the original real-valued trial. The regular remainder is called r; it is not Suzuki's residual kernel, and R_T denotes the full residual operator.

## 1. Exact signed step extraction

For every interior breakpoint b let Delta_b=q(b+)-q(b-), and define

\[
\chi_b(x)=\mathbf1_{x>b}-\frac{1-b}{2},\qquad
s=\sum_b\Delta_b\chi_b,\qquad r=q-s.
\tag{1}
\]

Each chi_b has zero mean and one unit jump. Thus s has precisely the signed jumps of q, and r is continuous piecewise polynomial. It follows that r belongs to H1(-1,1), with r'=q'_cell almost everywhere. No endpoint vanishing condition is imposed. Centering only transfers constants between the two components; it does not change q.

In the first-window source, a_m=tau_m-1, b=+-a_m, and both jumps for m are c_m u(1), not their absolute values. Consequently

\[
s_m=c_m u(1)\operatorname{sgn}(x)\mathbf1_{|x|>a_m}.
\]

The paired s and r remain exactly odd. Preserve every P2/P3 contribution in the combined cells and model before forming products.

For k>=1, direct Legendre integration gives

\[
\sigma_k(b)=\langle e_k,\chi_b\rangle
 =\frac{P_{k-1}(b)-P_{k+1}(b)}{\sqrt{2(2k+1)}},\qquad
\sigma_0(b)=0,\qquad s_k=\sum_b\Delta_b\sigma_k(b).
\tag{2}
\]

This follows from (P_{k+1}-P_{k-1})'=(2k+1)P_k and P_j(1)=1. The exact step Gram is

\[
\langle\chi_a,\chi_b\rangle
 =\frac{(1+\min(a,b))(1-\max(a,b))}{2}.
\tag{3}
\]

Hence the COMPLETE infinite step tail is

\[
S_L=\|Q_Ls\|^2
 =\sum_{i,j}\Delta_i\Delta_j\langle\chi_{b_i},\chi_{b_j}\rangle
 -\sum_{k<L}|s_k|^2.
\tag{4}
\]

This is whole norm minus finite head, not a truncated sum over high modes. Off-diagonal products, signs and the mean convention matter. For the paired original source, its whole norm also equals 2|u(1)|^2 sum_{m,n}c_m c_n(1-max(a_m,a_n)), an independently organized algebraic control used in the executable check.

## 2. Complete regular-remainder control

Let rho(x)=1-x^2 and

\[
D_r=\int_{-1}^1\rho(x)|r'(x)|^2\,dx
 =\sum_{\text{cells}}\int\rho(x)|q'_{\rm cell}(x)|^2\,dx.
\]

For the classical Legendre differential eigenvalues lambda_k=k(k+1), integration by parts gives <e_k',r'>_rho=lambda_k r_k. The boundary term vanishes because rho vanishes at both endpoints. The weighted derivatives e_k'/sqrt(lambda_k) are orthonormal; Bessel therefore gives

\[
\sum_{k\ge1}\lambda_k|r_k|^2\le D_r,\qquad
\|Q_Lr\|^2\le\frac{D_r}{L(L+1)}\quad(L\ge1).
\tag{5}
\]

These differential eigenvalues are an auxiliary regularity estimate for r. They do not replace Suzuki's harmonic eigenvalues H_k or the C0 reference weights. No H1 assumption is made on discontinuous q or logarithmic Vu.

For cell-local coordinates t=(x-center)/radius, the derivative integral is radius^-1 int_{-1}^1 [1-(center+radius*t)^2]|d r_local/dt|^2 dt. Omitting this derivative/measure scaling would change the source. The existing cell representation explicitly uses these local coordinates.

## 3. Keep the signed mixed tail in the full bound

Set g=Vu+s, without assuming g is H1. Define

\[
G_L=\|g\|^2-\sum_{k<L}|g_k|^2,\quad
C_L=\operatorname{Re}\left(\langle g,r\rangle
 -\sum_{k<L}\overline{g_k}r_k\right),\quad
\mathcal R_L=\|r\|^2-\sum_{k<L}|r_k|^2.
\tag{6}
\]

Orthogonal projection gives exactly

\[
\|Q_L(Vu+q)\|^2=G_L+2C_L+\mathcal R_L.
\tag{7}
\]

In particular, replacing C_L by its absolute value or independent norm triangles throws away the information this refinement retains. The sign is not prescribed; a checked fixture below has both signs at different indices.

Given valid uppers G+, C+, R+ and D+ for these quantities and D_r, form

\[
M_L=G^++2C^++\min\left(R^+,\frac{D^+}{L(L+1)}\right).
\tag{8}
\]

If R+ has not been supplied, using only D+/lambda_L is valid. The minimum needs no independence assumption: both entries are uppers on the same regular tail. G+,R+,D+ and the resulting M_L must be nonnegative for consistent enclosures. Negative LOWER endpoints can arise from interval dependency; a negative UPPER on one of these nonnegative quantities is an inconsistency, not something to clip silently to zero. A negative C+ is legitimate.

For the actual residual image degree 223 and L>=224, Q_L R_32u=0, but the omitted residual still obeys ||Q_L(R_T-R_32)u||<=delta||u||. Consequently

\[
\|Q_L(V+\mathcal P_T+R_T)u\|^2
 \le E_{\rm joint}(L):=(\sqrt{M_L}+\delta\|u\|)^2.
\tag{9}
\]

This restores one collective norm error, including its cross effect, rather than summing a constant coefficient error over an infinite tail. The original C-0074 implication is unchanged:

\[
J\ge w_{L-1}\max(0,R_--E_{\rm joint}),\qquad
s_0\le h-w_{L-1}\max(0,R_--E_{\rm joint}).
\tag{10}
\]

A certified upper on E_joint is required here. A formula alone supplies no target numerical conclusion.

### Finite input requirements and implemented primitives

The inputs in (6)-(8) consist of whole image norms, signed mixed integrals, a finite head and a weighted derivative energy. Elementary cell integrals handle s/r products and derivative energy. Existing whole V/V2 moments handle the potential square; existing `logarithmic_cell_moments` and independently coded `cell_v_moments` handle the logarithmic mixed cell contractions with s/r. Existing combined arithmetic images retain signed terms in local Legendre coordinates. The scalar projection identity is not claimed novel or automatically tighter; direct joint-image scalar evaluation can be equivalent and preferable. No full matrix or inverse is mathematically required.

The original-trial G_L,C_L and regular-tail enclosures have NOT been computed here. They cannot be inferred from the accepted nine combined source moments or the jump model. This is missing evaluated input, not an established missing source theorem or analytical primitive. High-degree conditioning and independent source acceptance for such a calculation are not demonstrated by the small fixtures.

## 4. Checked fixed fixtures

The rational fixture uses u=x, tau=3/2, c=2, so q=-2(x+3/2) on (-1,-1/2), q=-2(x-3/2) on (1/2,1), and zero centrally. Its jumps are +2. The centered s is -2/0/+2 on those cells and r is continuous. Independent polynomial cell integration gives ||q||^2=7/3, ||s||^2=4, ||r||^2=1/3, <s,r>=-1 and D_r=5/3.

At L=3:

| Quantity | Exact value |
| --- | ---: |
| S_L | 5/8 |
| Arithmetic mixed tail C_sr,L | -1/16 |
| Regular tail | 7/96 |
| Exact joint arithmetic tail | 55/96 |
| Signed-correlation plus derivative upper | 23/36 |

Controls executed: 96 exact step-coefficient identities; 16 exact step-Gram identities; exact continuity, norm and derivative checks; complete projection identities and derivative uppers at L=3,4,8,12. The log-potential full-source version of (7)-(9) was also exercised on that fixture, including two nonzero collective-remainder controls. Nine logarithmic cell enclosures at 256 bits contained separately coded 512-bit reconstructions; the squared-potential whole moment also passed this check. Shared Arb remains trusted. At L=12 the full fixture C_L is positive, so these checks do not assume favorable cancellation.

These are complete-tail identities for small fixtures through whole norms minus finite heads, not an original-trial source reconstruction or general proof by finite examples. The general argument was separately mathematically reviewed.

## 5. Unchanged original configuration: cancellation is real

At L=224=r_residual+1, the jump model is determined entirely by retained exact u(1) and accepted c_m,tau_m. No full q/source coefficients are needed. The norm-one compressed-translation geometry gives ||q||<=(c2+c3)||u||. Write b_+ for an outward scalar upper on that norm budget, not the low-to-tail operator B.

With r=q-s,

\[
C_{sr,L}=\operatorname{Re}\langle Q_Ls,Q_Lr\rangle
 \le b_+\sqrt{S_L}-S_L.
\tag{11}
\]

When S_lower>b_+^2, the right side decreases with S_L, so b_+sqrt(S_lower)-S_lower is a valid strictly negative upper. Reverse triangle also gives

\[
(\|Q_Ls\|+\|Q_Lr\|)^2
 \ge(2\sqrt{S_{\rm lower}}-b_+)^2>b_+^2.
\tag{12}
\]

One fixed 512-bit interval computation, using 112 odd model HEAD coefficients and the exact complete step norm, certified these predicates. Its extended v2 control and canonical replay used the same indices, precision, inputs and arithmetic, not a scan or precision retry.

| Original-trial quantity at L=224 | Display | Meaning |
| --- | ---: | --- |
| Step-model tail S_L | 5.1004452451062665 | Complete tail from whole step Gram minus finite head |
| Global arithmetic norm-squared upper b_+^2 | 1.2643049422911659 | Also an upper on the true arithmetic tail |
| C_sr,L upper | -2.5610519846455455 | Actual arithmetic mixed-tail cancellation; not its exact value |
| Separate-norm treatment lower | 11.508512880873349 | Lower on what separated norm uppers must pay |
| Separate full-source control E_control upper | 6.664365418102699 | Not an evaluation of (9) |
| Old variation-envelope lower | 105.89899680607984 | Lower on the old UPPER ENVELOPE, not actual tail mass |
| Tail cap required by the fixed negative-upper test | 0.24316921753565277 | Threshold for that certificate, not necessary for actual negativity |

Exact rational interval endpoints and comparisons are in the [canonical result](../computations/2026-10-23T174341Z-jump-refinement-controls/data/canonical-result.json); decimals are displays only. The certified C_sr,L omits <Q_L Vu,Q_L r>. It is NOT the full C_L in (6), and cannot be substituted for it.

### Separate sanity control and strict bound improvement

Using the existing potential-tail bound a_L=sqrt(2)A_z/(eta_L L), projection contractivity and the arithmetic norm budget gives the valid full-source CONTROL

\[
E_{\rm control}=(a_L+b_++\delta\|u\|)^2.
\]

At the same original configuration and L=224, its outward upper is strictly below 6 U_e^2/(L-2), whereas the discarded variation envelope is strictly ABOVE that expression by C-0076's actual jump floor and pi>3. This proves a strict improvement over that particular old envelope with unchanged source/trial parameters.

Attribution matters: this control improvement comes from reusing the global arithmetic norm cap, not from evaluating the new joint-correlation formula or the negative model mixed term. It still exceeds R_-, so supplies zero concentration correction. The fixed reported upper would be negative exactly when a valid tail cap E satisfies E<R_--h/w_223. The control does not meet that threshold; E_joint is unevaluated. Neither result determines the actual reference sign.

## Verification, reproducibility and preservation

Independent read-only mathematical review checked (1)-(10), centering/parity, Gram and normalization, H1/Bessel hypotheses, signed interval directions, full residual and inconsistency handling. It separately checked the original-model comparison and the attribution/limits of the separate control improvement. The reviewer performed no numerical executions; original high-degree mixed input enclosures were not independently reconstructed.

[The computation bundle](../computations/2026-10-23T174341Z-jump-refinement-controls/record.md) retains the exact toy, model-v1 and extended model-v2 commands, their distinct outputs, the canonical source snapshot, canonical replay output, and all process receipts. The inert drafting branch in the historical v1 command is preserved as executed; v2 and the canonical consumer remove it. No alternative arithmetic branch was executed and no original result is overwritten.

The fixed research-only consumer is `scripts.weil_jump_refinement_check`. Its ordinary module invocation reproduces the v2 exact comparisons; it does not implement a full-source evaluator, joint-tail enclosure or theorem admission. Actual canonical execution returned 0; a changed-input smoke returned 2 with empty result stdout before source work. No automatic fallback or weakened hash check is used.

Five direct child executions, including the canonical and integrity smokes, used 2.438724899897352 seconds. Cumulative analytical-check charge including the earlier work is **4.620344400056638/180 seconds**; each child had a 60-second cap, all exited, no timeout or precision retry. Source images, new full-source moments, matrix/inverse assembly, a test suite, Rust/retained-theorem replay and Lean build were not run.

## Dependencies, circularity and limits

Dependencies are C-0063–C-0065 for source/metric/maps; C-0072/C-0074 for the reference, weights and retained one-sided data; C-0075/C-0076 for the previous bound and its scoped limitation. The original trial/scalar packets retain their byte identities and original A/G remains generator-source-qualified. Existing Suzuki/Arb trust and 2T<pi remain unchanged. No external theorem or source code is newly imported.

The refinement changes error accounting, not the mathematical source. It assumes no positivity, unknown prime cancellation or RH-equivalent estimate. Its whole-norm/projection identities are an organizing mechanism, not an automatic proof of useful sharpness. Actual original-trial joint enclosures remain unevaluated. No exact reference, true Schur, Weil sign, new support theorem, global family or RH result is established. Admissions remain eight frozen v1, zero v2 and one v3 C-0067. Earlier records and methods remain unchanged.
