# Weighted source tails resolve the preserved reference direction

- **Finding ID:** `F-20261023-006`
- **Created:** `2026-10-23T19:28:21Z`
- **Last updated:** `2026-10-23T19:45:46Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` under the inherited local Suzuki source and tail-form hypotheses, Arb interval primitives, separately organized source reconstruction and exact consequence replay. Not a new admitted support theorem or Lean proof.
- **Claims:** C-0080, C-0081.
- **Evidence:** [X-20261023-004](../computations/2026-10-23T192821Z-weighted-source-tail/record.md).

## Result and unchanged mathematical object

For the original exact odd trial at T=3/5,N=192,K=32 and the original exact rational mu, the complete diagonal-reference directional value is strictly positive:

\[
0.6257295744306691\;\lesssim\;
s_0=\langle u,Au\rangle-\langle Bu,C_0^{-1}Bu\rangle
\;\lesssim\;0.8504608367268481.
\]

The decimal displays are not the proof endpoints. The exact rational bracket in [result-v2.json](../computations/2026-10-23T192821Z-weighted-source-tail/data/result-v2.json) is contained in (3/5,9/10), as separately replayed using integer/rational inequalities.

Under C-0072's inverse ordering, the same strict lower transfers to the **true Schur quadratic value on this same trial**. It proves neither positivity of the whole low-space reference/Schur matrix nor a full Weil test-class result. No support, trial, arithmetic term, residual order, Legendre low-space dimension, source formula or reference parameter was changed.

## 1. Qualifying the harmonic-moment estimate

Write F_K=(V+mathcal P_T+R_32)u, f=F_K+e with ||e||<=delta||u||. Since the residual image has degree 223, b=Q_224 F_K=Q_224(V+mathcal P_T)u. Put

\[
\lambda_k=\mu+H_k-H_{192},\quad w_k=\lambda_k^{-1},\quad
M=\sum_{k\ge224}|b_k|^2,\quad
D=\sum_{k\ge224}\lambda_k|b_k|^2.
\]

Weighted Cauchy gives J_b=sum_{k>=224} w_k|b_k|^2>=M^2/D. A usable numerical lower would require M_-^2/D_+, not M_+^2/D_-.

### Domain and complete convergence

D is finite for this truncated source without a global H1 assumption on its discontinuous arithmetic image or logarithmic potential. Let A_z=sum|z_j|, eta=1-191*192/(224*225)>0 and mathcal V(q) be C-0075's finite jump-aware weighted variation. C-0075's reviewed coefficient bounds imply

\[
|b_k|^2\le
\frac{12A_z^2}{\eta^2 k^3}
+\frac{\pi\mathcal V(q)^2}{(k-1)^2},\qquad k\ge224.
\]

Because 0<lambda_k<=mu+1+log k, the corresponding weighted series converge. The variation is finite by C-0075 equation (10), with strict first-window translation topology. Thus b belongs to the harmonic form domain, even though it need not belong to H1.

This does not assign harmonic energy to e. Only its L2 norm is given. On any projected tail Q_l, the bounded inverse square root supplies

\[
\|C_0^{-1/2}Q_l e\|\le\delta\sqrt{w_l}\|u\|.
\]

Consequently a truncated inverse-energy lower J_b,- restores to [max(0,sqrt(J_b,-)-delta sqrt(w_224)||u||)]^2. No infinite sum of independent coefficient errors or unsupported bound on the residual's unbounded harmonic energy is used.

### Assessing the scalar rule without implementing an unhelpful moment integral

A finite band below B gives the rigorous lower

\[
D\ge\lambda_B M-
\sum_{224\le k<B}(\lambda_B-\lambda_k)|b_k|^2.
\]

Use M_- and coefficient-square uppers for a numerical D_-. Then M^2/D<=M_+^2/D_-. This is an **upper ceiling on the Cauchy expression**, not an upper bound on J_b. A validated upper on the full near contribution in modes 211,...,223 strengthens the failure screen beyond a fixed near lower.

On the evaluated source, D_->0.9120232714 and the scalar expression is below 0.5450345404. Even with the exact near contribution, the retained h minus the near upper and this expression stays above 0.8071149546. Thus this scalar-Cauchy negative-certification rule cannot bridge the gap. D itself and a target D_+ were not evaluated; the ceiling made that extra operation unnecessary. This does not exclude other weighted estimates.

## 2. Same-source iteration to an accuracy-controlled weighted bracket

Rather than stop at that failed scalar compression, retain the individual inverse weights in a finite band and pay the entire remaining tail. The boundary was fixed **before evaluating any new source coefficients** as the smallest even B>=224 satisfying

\[
w_B M_+\le h/4,\qquad h=a_{\rm old,+}-P_-.
\]

The exact retained-data selection gives B=874. This is a declared error allocation, not a sequence of cutoffs tested until a desired sign appears. It bounds omitted truncated inverse energy by one quarter of the known headroom; it does not guarantee sign resolution. N remains 192, and the original accepted prefix still ends before 211. No A-U_874 matrix is constructed.

Let

\[
S=\sum_{211\le k<B}w_k|F_{K,k}|^2,\qquad
T_B=M-\sum_{224\le k<B}|b_k|^2.
\]

Only the 332 odd indices 211,213,...,873 contribute. The signed V, combined arithmetic and R_32 coefficients are added before squaring. R_32 contributes through mode 223 and is zero only above that degree. Complete-tail projection and monotonic weights give

\[
S\le J_K\le S+w_B T_B.
\]

Restore the full residual **once in the bounded inverse-weighted norm**, with epsilon=delta sqrt(w_211)||u||:

\[
[\max(0,\sqrt{S_-}-\epsilon)]^2\le J
\le[\sqrt{S_++w_B T_{B,+}}+\epsilon]^2.
\]

The older valid J lower is retained by maximum, not addition over overlapping modes. Negative upper endpoints on nonnegative masses are rejected. Lower endpoints may be clipped at zero only using known nonnegativity.

## 3. Independently enclosed physical low-form scalar

A positive direction requires a genuine a_- and prefix upper; the old positive upper h could not establish this. Scalar-only source composition reconstructs

\[
a_K=\sum_jH_jz_j^2\frac2{2j+1}
-[\log(2\pi T)+\gamma]\|u\|^2
+\langle u,Vu\rangle+\langle u,\mathcal P_Tu\rangle
+\langle u,R_{32}u\rangle.
\]

Then a lies in a_K plus/minus delta||u||^2. These are physical, unnormalized values. The original serialized field named `a_full_rayleigh_upper_exact` is also physical in the original source code; no extra norm multiplication or division is applied. Its valid upper is retained by intersection, followed by outward rounding.

The same source primitives supply scalar potential, signed translated-cell and residual pairings. The reference uses a separately coded exact basis, per-monomial potential moments, four signed cells/Taylor shifts and an independent residual-polynomial construction. Only this directional low-form scalar is reconstructed; the old full A/G matrices are not reconstructed or promoted.

With the already accepted prefix endpoints, opposite interval directions give

\[
a_- -P_+-J_+\le s_0\le a_+-P_--J_-.
\]

## 4. Evaluated endpoints

| Quantity | Lower display | Upper display |
| --- | ---: | ---: |
| Full physical a | 6.407116781359613 | 6.407116781359653 |
| Full omitted inverse energy J, k>=211 | 0.8118726377190583 | 1.036603900014265 |
| Exact diagonal-reference direction s0 | 0.6257295744306691 | 0.8504608367268481 |

The remaining unweighted mass above B is near 0.3817004434 and its entire omitted inverse energy is bounded above by 0.2247312623. It is not dropped. The full residual and all signed component interactions are included.

### Consequence for the true Schur direction

C-0072 gives C^-1<=C0^-1 and therefore

\[
\langle u,(A-B^*C^{-1}B)u\rangle
\ge s_0\ge s_{0,-}>3/5>0.
\]

This transfer uses the established form-domain inclusion and positive tail hypotheses. It requires no direct evaluation of C^-1 or equality of unbounded operator domains.

The producer's `actual_true_schur_or_weil_sign: UNDETERMINED` flag concerns the unresolved **overall operator/form sign**, not the directional implication proved here. Distinguish: diagonal-reference direction positive by enclosure; true Schur direction positive by inverse ordering; direct true-inverse value uncomputed; full matrix/Weil positivity unresolved.

The result explains why the same trial's older negative conservative sufficient-matrix bound does not reject the stronger reference. It is not a contradiction between two evaluations of one matrix.

## 5. Numerical acceptance and implementation correction

The fixed generator/reconstruction precisions were chosen before source evaluation as 4096/8192 bits. The generator uses C-0075's exact high-potential pairing, Horner shifts and two doubled positive cells. The reference uses monomial logarithmic moments, Taylor shifts and four signed cells. Trial/residual polynomial hashes agree; all 2 scalar and 1328 head raw-reference containments passed. Outward-rounded 512-bit reference receipts are also contained in the 352-bit generator publication and retained in the result. Fourteen older joint-head compatibility checks passed. Arb, source identities and some polynomial/projection operations remain shared dependencies.

The first implementation failed at the integer-to-text limit while serializing large exact rational consequences. A small finite-spectral reproduction isolated the same failure, and two behavioral regressions failed before correction. Exact accumulation of hundreds of unrelated inverse-weight denominators was unnecessary; very high-precision squared root endpoints also needed bounded serialization.

Version 2 accumulates each weighted term outward on the 352-bit dyadic grid and rounds consequential endpoints outward. This changes enclosure bookkeeping, not source, reference, boundary, precision or proof predicate. Python's integer limit was not disabled. The two regressions then passed, covering zero and nonzero collective errors against known finite spectral energies. Original v1 source, empty result stdout, diagnostics and failures remain preserved separately from corrected v2 source/output.

Independent mathematical/static review accepted the source/domain argument, scalar-rule screening, complete weighted bracket, normalization, directed rounding and true-Schur directional transfer. It did not execute or independently rerun numerical code. A separate standard-library exact replay checked all 1330 serialized containments, the minimal accuracy boundary, endpoint algebra and squared rational predicates for the residual norm inequalities. It verified the strict bracket (3/5,9/10). A changed-input smoke rejected before source work.

Eight owned direct executions exited without timeout. All failures, tests and the explicit corrected-version run are charged: new 74.6472387999529 seconds; cumulative 91.74805250007194/180 seconds; cap 60 seconds per child. No numerical precision or cutoff search, full matrix/inverse, full test suite, Rust/retained-theorem replay, Lean build or external compute occurred.

## Dependencies, circularity and limits

C-0063 through C-0065 supply the local source, metric and maps; C-0072 the reference/inverse order; C-0074 the prefix and directional identity; C-0075 coefficient decay/domain inputs; C-0077/C-0079 the signed source and accepted complete M_224. Existing Suzuki and Arb premises, full residual, strict arithmetic topology and 2T<pi remain unchanged. No unknown cancellation, positivity or RH-equivalent estimate is assumed.

The chosen direction is resolved; positivity over all low directions, both parity sectors or the full smooth class is not. No full source A/G audit, globally covering family, new certificate profile or support theorem is established. RH remains unresolved. Admissions remain eight frozen v1, zero v2 and one v3 C-0067. All older records, source modules and proof artifacts remain unchanged.
