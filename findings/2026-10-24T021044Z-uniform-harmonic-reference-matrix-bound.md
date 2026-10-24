# Uniform harmonic-reference matrix bound with the full residual

- **Finding ID:** `F-20261024-001`
- **Created:** `2026-10-24T02:10:44Z`
- **Last updated:** `2026-10-24T02:20:54Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` conditional mathematical implication, independently reviewed; not target-matrix positivity or theorem admission

## Statement

C-0082 lifts the finite harmonic-tail majorant to the complete low space, with signed cross-direction terms, a uniform matrix tail bound and a full L2 residual perturbation. It does not assume that a positive matrix margin exists.

Use the source and tail-form hypotheses of C-0063 through C-0065 and C-0072. In ordinary Legendre coordinates, put

\[
D=\operatorname{diag}_{j<N}d_j,\quad d_j=\frac2{2j+1},\qquad e_k=P_k/\sqrt{d_k}.
\]

Let \(W=V+\mathcal P_T+R_T\), \(W_K=V+\mathcal P_T+R_K\), \(B=Q_NWP_N\), and \(B_K=Q_NW_KP_N\). Let \(A_K\) be the truncated low form **without** subtracting the residual allowance. Suppose

\[
\|R_T-R_K\|\le\delta,\quad |A-A_K|\preceq\delta D.
\]

The second expression means both \(-\delta D\preceq A-A_K\preceq\delta D\), not entrywise absolute values. Keep the chosen exact rational \(\mu>0\) fixed and define

\[
\lambda_k=\mu+H_k-H_N,\quad w_k=\lambda_k^{-1},\qquad k\ge N.
\]

The reference is \(S_0=A-B^*C_0^{-1}B\), where \(C_0e_k=\lambda_ke_k\). For \(m>N\), define rows \(t_k=(\langle e_k,W_KP_j\rangle)_{j<N}\) and

\[
G_K=B_K^*B_K,\qquad
G_{K,m}=G_K-\sum_{N\le k<m}t_k^*t_k\succeq0,
\]
\[
U_m=w_mG_K+\sum_{N\le k<m}(w_k-w_m)t_k^*t_k.
\]

Let exact rational symmetric matrices satisfy \(A^-\preceq A_K\) and \(U^+\succeq U_m\). Set \(h=\operatorname{tr}(D^{-1}U^+)\). For any outward rational bound

\[
r\ge\delta+2\delta\sqrt{h/\mu}+\delta^2/\mu,
\]

one has

\[
\boxed{S_0\succeq A^- - U^+ - rD.}
\]

Under C-0072, the true Schur complement is above \(S_0\). Strict positive definiteness of this lower matrix on **both** parity blocks is therefore a sufficient condition; it has not been established for the target here.

## Derivation

### Complete weighted tail, including correlations

Parseval on the finite-dimensional source image gives

\[
H_K:=B_K^*C_0^{-1}B_K=\sum_{k\ge N}w_kt_k^*t_k,
\]
\[
U_m=\sum_{N\le k<m}w_kt_k^*t_k+w_mG_{K,m}.
\]

Consequently,

\[
0\preceq U_m-H_K
=\sum_{k\ge m}(w_m-w_k)t_k^*t_k
\preceq w_mG_{K,m}.
\]

The complete mixed Gram contains every ordered V/P/R_K cross term. A sum of separate component squares is not this Gram. The alternative expression for U_m avoids subtracting nearly equal complete/head matrices when assembling the upper majorant; the subtraction identity remains useful for the tail trace.

For any certified scalar

\[
\Gamma_m\ge\operatorname{tr}(D^{-1}G_{K,m}),
\]

positivity gives

\[
0\preceq U_m-H_K\preceq w_m\Gamma_mD.
\]

Only diagonal upper enclosures are needed for this trace. They must enclose the **complete** tail identity, with the Q_N projection and all source columns. Sparse sampled projections do not supply that trace. A negative certified upper endpoint for a mathematically nonnegative diagonal is an inconsistency, not a value to clip.

The full correlated U_m need not be replaced by a scalar matrix. The scalar trace bound quantifies its possible tail overestimate. Also,

\[
U_m-U_{m+1}=(w_m-w_{m+1})G_{K,m+1}\succeq0.
\]

### Full residual and its cross effects

Write E=B-B_K. Projection is a contraction, so

\[
\|Ez\|\le\delta\sqrt{z^*Dz},\qquad
\|C_0^{-1/2}Ez\|\le\frac\delta{\sqrt\mu}\sqrt{z^*Dz}.
\]

Since \(U^+\succeq U_m\succeq H_K\succeq0\), its mass-normalized trace h bounds the largest eigenvalue of the mass-normalized H_K. Cauchy-Schwarz in the bounded inverse-weighted norm then proves

\[
B^*C_0^{-1}B\preceq
H_K+\left(2\delta\sqrt{h/\mu}+\delta^2/\mu\right)D.
\]

Subtract this upper and the low residual allowance once. This proves the boxed lower bound. No unbounded harmonic-energy norm is applied to an error known only in L2. The square root must be bounded outward, not evaluated through an unchecked floating conversion.

An independently valid alternative, for exact \(\eta>0\), is

\[
S_0\succeq A^--(1+\eta)U^+
-\left[\delta+(1+\eta^{-1})\delta^2/\mu\right]D.
\]

It can be wider because it scales the whole upper matrix. Neither formula identifies W_K with the full source.

### Matrix interval order, coordinates and parity

For a symmetric target with interval centers M and symmetric entry radii \(\rho_{ij}\), put \(s_i=\sum_j\rho_{ij}\). Then

\[
M-\operatorname{diag}(s_i)\preceq X
\preceq M+\operatorname{diag}(s_i).
\]

Entrywise endpoints are not Loewner bounds. A half-width gives relative error \(\max_i s_i/d_i\); the worst gap from the true matrix to either chosen endpoint matrix is at most **twice** that amount. Do not confuse these two error charges.

Reflection commutes with the complete paired signed source, Q_N and C_0. At N=192 this yields two 96-dimensional blocks. Opposite-parity zeros follow from that identity; interval containment of zero only checks consistency. Ordinary-coordinate exact positivity needs no irrational mass rescaling. A normalized margin g can be certified by an exact check of \(L-gD\succeq0\).

Polynomial source images are in L2, including the logarithmic potential image. The finite low-space maps are bounded. The tail inverse ordering uses the stronger harmonic form domination and form-domain inclusion from C-0072, not equality of operator domains or merely C>=mu I. The local residual argument still requires 2T<pi.

### Accuracy and what convergence actually provides

For fixed N, finite rank and Parseval imply

\[
\operatorname{tr}(D^{-1}G_{K,m})
=\sum_{j<N}d_j^{-1}\|Q_mW_KP_j\|^2\longrightarrow0.
\]

This is uniform convergence on the fixed low space, not a practical cutoff or runtime theorem.

One noncircular conditional refinement rule is: if \(\Gamma_m>0\), let \(\theta_m=w_m\Gamma_m\) and choose the smallest even \(\ell>m\) with

\[
w_\ell\Gamma_m\le\theta_m/2.
\]

Before computing new rows, tail nesting already proves \(U_\ell-H_K\preceq\theta_mD/2\). A new trace may improve this bound. If \(\Gamma_m=0\), the exact truncated tail vanishes. The selector is equivalent to halving w_m; harmonic growth can make the required index very large. Existence does not establish feasibility.

A positive independently certified head margin g must cover the **sum** of tail loss, one-sided interval overestimates and full residual allowance. For example, if the exact truncated head matrix is at least gD, sufficient accounting is

\[
w_m\Gamma_m+\varepsilon_A+\varepsilon_U+r<g.
\]

Do not assume g from the desired conclusion or charge already included errors twice. At fixed K, the full-residual allowance does not vanish as m grows. Increasing m cannot fix a residual-dominated bound. A resource stop leaves the uncomputed tail paid and the result unresolved.

### Negative directions require the opposite inequality

Failure of the conservative lower matrix is not negativity of S_0. If an exact trial has a finite truncated weighted head lower J_- and norm squared n, then

\[
J_{\rm full}\ge
\left(\max\{0,\sqrt{\max(0,J_-)}-\delta\sqrt{n/\mu}\}\right)^2.
\]

Subtracting this from an independently verified full low-form upper a_+ provides a genuine directional **upper** for S_0. Strict negativity of that upper rejects reference positivity only, not the larger true Schur or Weil form.

## Executed verification

[X-20261024-001](../computations/2026-10-24T021044Z-uniform-matrix-contract/record.md) retains a fixed operation-level source smoke at T=3/5,K=32. Low degrees 0,1,190,191 and rows 0,1,190,191,192,193,224,225 exercise both parities, nonconsecutive degrees, off-diagonal pairings and the exact residual degree boundary 223.

Existing 1024-bit source helpers and separately coded 2048-bit reconstruction passed **96 V/P/R component containments plus the residual norm bound**, at outward 352-bit publication. All four exact residual image polynomials agree. Exact non-diagonal finite-matrix controls check the weighted upper, complete tail, non-Euclidean mass and signed residual cross error; another control has a negative conservative lower while its actual matrix is positive.

The child exited 0 in 5.553956900024787 seconds, with no retry or timeout and confirmed owned exit. This does not measure the cost of a complete 192-column weighted matrix. Independent read-only mathematical review accepted the inequalities with the domain, residual-floor, factor-two interval and feasibility qualifications above; it ran no numerical work.

## Dependencies and limits

Dependencies: C-0063 through C-0065, C-0072, C-0077/C-0079 and the finite weighted decomposition of C-0080. Shared Suzuki identities, Arb and some exact polynomial operations remain trusted premises, even when source assembly is independently coded.

No complete target A/G reconstruction, full weighted matrix evaluation, selected target cutoff, target matrix sign, smooth-test positivity theorem, production admission, Rust/Lean change or RH proof is established. Earlier C-0081 remains a positive **directional** result. Existing methods, records, failures, inputs and outputs are unchanged.
