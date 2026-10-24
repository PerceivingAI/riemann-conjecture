# Uniform cross-cut norm and a controlled weighted continuation

- **Finding ID:** `F-20261024-004`
- **Created:** `2026-10-24T19:34:21Z`
- **Last updated:** `2026-10-24T19:34:21Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` for the written cross-cut/residual derivation by independent mathematical review; this entry does not establish the new support's matrix sign
- **Claim:** C-0085
- **Computation:** [X-20261024-004](../computations/2026-10-24T191616Z-weighted-support-extension/record.md)

## Question and completed baseline diagnosis

C-0084 established the positive whole harmonic reference at T=3/5,N=192,K=32,m=626. The question here is whether its useful controls admit a meaningful support-growth experiment.

Exact directional decomposition on accepted316/626 inputs shows the following. Directions are retained dyadic proposals, not claims of exact minimum eigenvectors. Values below display exact mass-normalized enclosures retained in `data/baseline-losses-v2.json` of X-20261024-004.

| Retained direction | m | A_K lower | Flat-mu coupling upper | Signed weighted resolved-head upper | Omitted weighted allowance upper | Full matrix lower in this direction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Failing odd direction from316 |316|5.5986794118|8.2917283229|5.1487659476|0.6073756850|-0.1574622208|
| Same direction |626|5.5986794118|8.2917283229|5.2745860443|0.2140254027|0.1100679647|
| Weak odd direction from626 |626|1.7688578315e-6|1.8046693403e-6|1.1589908938e-6|4.3707396101e-8|5.6615885344e-7|
| Weak even direction from626 |626|1.6116364682e-9|7.7805020297e-11|2.7018050146e-11|2.2484268548e-12|1.5816818268e-9|

The A and weighted-upper one-sided interval losses display2.0039253427e-102 and1.5803748126e-90. They are not the operative obstruction. In the former failing direction, resolving additional signed weighted head energy removes more omitted allowance than it adds to the resolved coupling. Separate-component factor3 treatment of the626 resolved heads alone would charge about13.03536 there, above A_K. The signed cross terms and distribution of inverse weights matter.

The global tail-trace allowance is not a minimum eigenvalue or the loss in every direction. Nor does a small allowance in a proposed weak direction certify all other directions. The316 failure and the separate626 whole-space witnesses illustrate that distinction.

## 1. The potential has a uniformly bounded cross cut

Let P_N project onto ordinary Legendre degrees0 through N-1, Q_N=I-P_N, d_j=2/(2j+1), and e_j=P_j/sqrt(d_j). The source potential is V(x)=-log(1-x^2)/2. For k>=N>j with matching parity, the exact source identity gives

\[
\langle e_k,V e_j\rangle
=\frac{\sqrt{(2k+1)(2j+1)}}{(k-j)(k+j+1)}
\le\frac1{k-j}.
\]

The inequality uses sqrt((2k+1)(2j+1))<=k+j+1. Opposite-parity entries vanish. This formula concerns the cross cut, not the full potential matrix. In particular, V is not a bounded multiplication operator on all L2.

For either parity, let q be its first degree at or above N. Write k=q+2a and j=q-2-2b. Thus the cross matrix is entrywise dominated by half the Hilbert kernel H_ab=1/(a+b+1), with a>=0 and b in a finite initial segment.

Here is a self-contained norm bound. For A>0, f_A(x)=1/((A+x)sqrt(x)) has

\[
f_A''(x)=\frac{3}{4x^{5/2}(A+x)}
+\frac1{x^{3/2}(A+x)^2}
+\frac2{x^{1/2}(A+x)^3}>0.
\]

Convexity on each unit interval gives f_A(b+1/2)<=integral_b^(b+1) f_A(x)dx. Summation and the substitution x=A t^2 give

\[
\sum_{b\ge0}f_A(b+1/2)
\le\int_0^\infty\frac{dx}{(A+x)\sqrt x}
=\frac\pi{\sqrt A}.
\]

With p_a=(a+1/2)^(-1/2), this is sum_b H_ab p_b<=pi p_a. Symmetry supplies the column bound. Weighted Cauchy-Schwarz for finitely supported vectors proves ||H||<=pi, and density extends the bound. The two parity blocks form an orthogonal direct sum, so the cross-cut bound is their maximum, not their sum:

\[
\boxed{\|Q_N V P_N\|\le\pi/2\quad\text{for every }N.}
\]

This is an application of the classical Hilbert-kernel bound, proved above. No literature-priority claim is made for the inequality or its application.

## 2. A residual allowance independent of source dimension

Use C-0082 notation B_K=Q_N(V+P+R_K)P_N and E=B-B_K. In the first arithmetic window, active terms are2,3 and their compressed-shift norms are1. More generally retain established bounds b_m>=||S_m||. The source absolute-series quantity rho_R(T,K), including its full remainder, bounds ||R_K|| as well as bounding the full residual norm. Therefore

\[
\|B_K\|\le b(T,K)
:=\pi/2+\sum_m c_m b_m+\rho_R(T,K).
\]

Assume ||E||<=delta, -delta D<=A-A_K<=delta D and C0>=mu I, mu>0. For n=z*Dz,

\[
\|B_Kz\|\le b\sqrt n,\qquad\|Ez\|\le\delta\sqrt n.
\]

Expanding the inverse-weighted quadratic and using ||C0^-1||<=1/mu gives

\[
B^*C_0^{-1}B
\preceq B_K^*C_0^{-1}B_K
+\frac{2b\delta+\delta^2}{\mu}D.
\]

Consequently, with the complete correlated upper Uplus>=U_m from C-0082,

\[
\boxed{S_0\succeq A^- - U^+
-\left[\delta\left(1+\frac{2b}{\mu}\right)
+\frac{\delta^2}{\mu}\right]D.}
\]

No source dimension or finite-trace factor appears in this allowance. It is independently valid, not necessarily sharper than the earlier trace allowance. At the old parameters its display is1.1653135419e-12, larger than the accepted trace-based6.8816432789e-13. The continuation instead increases K until the new uniform allowance fits within that old accepted budget. RK is never identified with the full residual, and the cross term is mandatory.

## 3. Structural selection before new signs

The prime3 translation overlap is ell3(T)=2-log(3)/T in the first window. Solving ell3(Tstar)=2ell3(3/5) yields

\[
T_* =\frac{(3/5)\log3}{2(\log3-3/5)}.
\]

The executed selector rounds Tstar downward to a dyadic, using the first certified depth whose overlap ratio lies in[1.99,2]. It then uses the original exact positive mu from C-0084 and the old accepted residual and inverse-weight budgets. Its fixed512-bit scalar procedure chooses:

- first certified even K>=32 with the new outward uniform residual allowance no greater than the old accepted allowance;
- first certified even N>=192 with H_N-c_T-c2-c3-rho_R>=the original exact mu;
- first even m>=N+K with (mu+H_m-H_N)^-1 no greater than the original exact626 weight.

These are minima under the declared certification procedure, not a claim of optimal mathematical dimensions or cutoffs. Harmonic divergence and the local convergent residual tail ensure existence of the scalar choices. They do not prove the final matrix positive.

The actual pre-sign selection is T=1353/2048=0.66064453125, N=312,K=38,m=1018. Its prime3 overlap ratio displays1.9946789613. Strict log3<2T<log4,1<tau2<tau3<2, signed-cell ordering and2T<pi are checked. The selected uniform residual allowance displays1.9466091170e-13. Low/head construction precisions are1792/4608, with separately organized independent reconstruction at3584/9216. These precision choices are conditioning controls, not a promise about resulting matrix signs.

## 4. What remains to be learned from the execution

Matching the inverse-weight cap does not match the omitted source mass, its matrix shape or w_m Gamma_m. The source dimension, signed translations and low-form cancellation change. Fresh complete A_K/G_K, all V/P/RK heads, independently checked analytical bounds and both parity signs are necessary to assess this selected continuation. Old research receipts do not certify the new support.

A failed conservative lower alone remains inconclusive. A separately certified negative directional upper would reject this S0 reference at its selected parameters, not the true Schur complement or Weil form. A positive result would remain a fixed-support source-conditional research consequence, not clean production admission, novelty, an unbounded family or RH.

This derivation does not pass the m=4 arithmetic/translation-chain boundary or the local2T<pi source radius. No global extension law is assumed. The computation record carries the actual execution status, failures, corrections and final signs separately.
