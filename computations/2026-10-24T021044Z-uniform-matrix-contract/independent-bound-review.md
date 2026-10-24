## Verdict

The proposed whole-low-space inequalities are **correct under the stated source and tail-form hypotheses**. They control the full residual, preserve the ordinary Legendre mass, and give uniform Loewner bounds rather than directional or entrywise substitutes.

The accuracy rule needs an explicit qualification: a positive margin for the **truncated finite-head matrix** must also pay the nonvanishing full-source residual penalty. Convergence of the weighted tail does not establish that this margin exists, that a usable cutoff is practical, or that the target matrix is positive.

I inspected the named source modules and the two findings. No files were changed, and no numerical execution or checks were run.

## 1. Domain, coordinates, and inverse comparison

For ordinary coordinates \(u=\sum_{j<N}z_jP_j\),
\[
\|u\|^2=z^*Dz,\qquad D_{jj}=\frac{2}{2j+1}.
\]
Consequently, a uniform normalized matrix bound \(M\preceq cD\) means
\[
D^{-1/2}MD^{-1/2}\preceq cI.
\]
Replacing \(D\) by the coefficient-space identity would change the assertion.

The low-space source maps are well-defined in \(L^2\). In particular, a polynomial times the logarithmic potential belongs to \(L^2(-1,1)\). Thus \(B\) and \(B_K\), restricted to the finite-dimensional low space, are bounded maps into the tail Hilbert space. This does not require \(V\) to be bounded on the full Hilbert space.

The required tail comparison is the stronger form inequality
\[
\mathfrak c[q]\ge
\sum_{k\ge N}(\mu+H_k-H_N)|q_k|^2,
\]
not merely \(\mathfrak c[q]\ge\mu\|q\|^2\). Its domain satisfies
\[
D(\mathfrak c)
=F_N\cap D(J^{1/2})\cap D(V^{1/2})
\subseteq F_N\cap D(J^{1/2})
=D(\mathfrak c_0).
\]
The variational inverse formula then gives
\[
0\preceq C^{-1}\preceq C_0^{-1}\preceq\mu^{-1}I.
\]
Equality of form domains is unnecessary. The original exact rational \(\mu>0\) must remain fixed in every weight; a newly computed complement lower bound is not automatically the same reference.

These facts justify
\[
A-B^*C^{-1}B\succeq S_0.
\]

## 2. Full matrix tail and weighted majorant

Regard \(t_k\) as a row acting on ordinary low coordinates. Parseval gives
\[
G_K=\sum_{k\ge N}t_k^*t_k,\qquad
G_{K,m}=\sum_{k\ge m}t_k^*t_k\succeq0.
\]
There is no additional low-coordinate mass factor in these sums. The tail normalization is already in \(e_k\).

Writing
\[
H_{K,\mathrm{head},m}
=\sum_{N\le k<m}w_kt_k^*t_k,
\]
the proposed expression is exactly
\[
U_m=H_{K,\mathrm{head},m}+w_mG_{K,m}.
\]
Therefore
\[
U_m-H_K
=\sum_{k\ge m}(w_m-w_k)t_k^*t_k,
\]
which proves
\[
0\preceq U_m-H_K\preceq w_mG_{K,m}.
\]
It also proves \(U_m\succeq0\), \(U_m\preceq\mu^{-1}G_K\), and monotone refinement:
\[
U_m-U_{m+1}
=(w_m-w_{m+1})G_{K,m+1}\succeq0.
\]

The complete mixed Gram is essential. Expanding \(\|Q_N(V+P+R_K)u\|^2\) requires all ordered cross terms. Independent component-square bounds are not the same matrix and discard the correlations this proposal retains.

## 3. Trace bound and full cross residual

Since \(U^+\succeq U_m\succeq H_K\succeq0\), the normalized upper matrix is PSD. Hence
\[
h=\operatorname{tr}(D^{-1}U^+)
=\operatorname{tr}(D^{-1/2}U^+D^{-1/2})
\ge
\|D^{-1/2}H_KD^{-1/2}\|.
\]
Thus \(h\ge0\) and
\[
z^*H_Kz\le h\,z^*Dz.
\]

Let \(E=B-B_K\). The assumed source error gives
\[
\|Ez\|\le\delta\sqrt{z^*Dz},
\qquad
\|C_0^{-1/2}Ez\|
\le\frac{\delta}{\sqrt\mu}\sqrt{z^*Dz}.
\]
Cauchy–Schwarz in the bounded inverse-weighted norm yields
\[
B^*C_0^{-1}B
\preceq
H_K+
\left(2\delta\sqrt{h/\mu}+\frac{\delta^2}{\mu}\right)D.
\]
Together with
\[
A\succeq A_K-\delta D\succeq A^--\delta D,
\]
this proves
\[
S_0\succeq A^--U^+-rD,
\qquad
r\ge\delta+2\delta\sqrt{h/\mu}+\delta^2/\mu.
\]

This includes the entire cross residual. It assigns no unbounded harmonic energy to \(E\). A rational implementation must enclose the square-root expression outward, not substitute an unchecked rounded value.

Young’s inequality independently proves
\[
S_0\succeq
A^--(1+\eta)U^+
-\left[\delta+(1+\eta^{-1})\delta^2/\mu\right]D,
\qquad \eta>0.
\]
Both proposed residual formulas are valid.

## 4. Uniform tail accuracy and interval order

For any PSD \(G_{K,m}\),
\[
G_{K,m}\preceq
\operatorname{tr}(D^{-1}G_{K,m})D.
\]
Therefore
\[
\Gamma_m\ge\operatorname{tr}(D^{-1}G_{K,m})
\quad\Longrightarrow\quad
0\preceq U_m-H_K\preceq w_m\Gamma_mD.
\]

Diagonal upper intervals suffice to bound this trace, provided they enclose the diagonals of the **full** matrix-tail identity. Computing the trace does not require replacing the final correlated matrix \(U_m\) by a scalar matrix.

A negative certified upper endpoint for a theoretically nonnegative diagonal or trace is an enclosure inconsistency, not something to repair by clipping. A negative lower endpoint may be clipped using established nonnegativity.

The symmetric midpoint plus row-radius construction is a valid Loewner enclosure. If \(|E_{ij}|\le\rho_{ij}=\rho_{ji}\), then
\[
-\operatorname{diag}(s_i)\preceq E
\preceq\operatorname{diag}(s_i),
\qquad s_i=\sum_j\rho_{ij}.
\]
A relative bound is
\[
\operatorname{diag}(s_i)\preceq\varepsilon D,
\qquad
\varepsilon=\max_i\frac{s_i}{d_i}.
\]
For an enclosure of the form midpoint \(\pm\operatorname{diag}(s_i)\), the worst-case gap between the target and either chosen bound is at most \(2\operatorname{diag}(s_i)\). Accuracy accounting must distinguish enclosure half-width from one-sided overestimation.

Entrywise upper endpoints alone do not give a matrix upper bound.

## 5. Parity

The two \(96\times96\) blocks are justified because reflection commutes with \(V\), the complete paired signed translations, \(R_K\), the complete residual, \(Q_N\), and \(C_0\).

Opposite-parity entries therefore vanish mathematically. An interval merely containing zero does not establish that identity. Conversely, failure to contain a mathematically established zero signals an enclosure problem.

After imposing justified zeros, exact rational congruence or LDL can certify the proposed lower matrix separately on both blocks. No irrational square-root normalization is needed to certify positive definiteness. A normalized margin \(g\) can be certified through the rational matrix inequality \(L-gD\succeq0\).

## 6. Correct conditional accuracy contract

The proposed rule is valid as a conditional error allocation, with the residual qualification made explicit.

For example, suppose the exact truncated finite-head matrix satisfies
\[
A_K-H_{K,\mathrm{head},m}\succeq gD,\qquad g>0.
\]
If the interval bounds obey
\[
A_K-A^-\preceq\varepsilon_A D,
\qquad
U^+-U_m\preceq\varepsilon_U D,
\]
then
\[
S_0\succeq
\left(g-w_m\Gamma_m-\varepsilon_A-\varepsilon_U-r\right)D.
\]
Thus the sufficient budget is
\[
w_m\Gamma_m+\varepsilon_A+\varepsilon_U+r<g.
\]
Errors already included in a certified head margin must not be charged twice.

Allocating tail and interval errors each at most \(g/4\) is insufficient unless the remaining margin also covers \(r\). With \(K=32\) fixed, this residual allowance does not vanish as \(m\to\infty\).

There is no circularity in using an independently certified head margin to select a subsequent accuracy. There would be circularity in assuming a positive head margin from the desired conclusion, or treating the existence of a positive margin as already established.

Finite rank and Parseval give
\[
\operatorname{tr}(D^{-1}G_{K,m})
=\sum_{j<N}\frac{\|Q_mW_KP_j\|^2}{d_j}\longrightarrow0.
\]
This proves uniform convergence on the fixed low space. It does not provide a practical cutoff, precision, runtime, or storage budget. The earlier directional boundary \(874\) supplies none of those whole-space guarantees.

## 7. Source-interface hazards

The inspected implementations impose these constraints:

- `assemble_truncated_mixed_gram` returns the complete truncated mixed Gram in ordinary Legendre coordinates. Its projection subtraction uses \(KD^{-1}K\). That matches the proposed \(G_K\).
- `_rational_order_bounds` provides valid row-radius Loewner bounds for a symmetric target. Its triangle-overlap check is a consistency check, not independent evidence that both intervals enclose the intended target.
- `rigorous_combined_schur_lower` is **not** the proposed harmonic-reference implementation. It recomputes a complement bound, uses a scalar inverse majorant, and already subtracts `delta_R` from the low diagonal. Reusing that low matrix as the stipulated \(A_K\) would double-charge the low residual.
- `verify_combined_schur_analytic_entries.run()` is hardcoded to \(T=11/20\), active terms \(2,3\), and order \(32\). Its packet loader also fixes that support, and its CLI only permits dimensions \(8,192\). It cannot validate the \(T=3/5\) target by changing a caller-side label.
- The auditor’s reconstructed `low` already includes the negative residual allowance. Its separately parameterized helpers do not all share the restrictions of `run()`, but their reuse requires explicit support, normalization, and degree handling.
- Kernel truncation order is not residual image degree. The degree bound \(223\) matters here; residual rows cannot be dropped immediately above mode \(32\).
- Reusing generator helpers is not independent reconstruction. Separately coded formulas can provide source-level independence, while still sharing Arb and other arithmetic dependencies.

## 8. Sign interpretation and scope

A negative lower matrix is inconclusive. To prove a negative direction for \(S_0\), one needs a directional **upper** bound. For example, if \(J_{\mathrm{head},K,-}\) bounds a finite truncated weighted head below, then
\[
J_{\mathrm{full}}
\ge
\left[
\max\left(
0,\sqrt{J_{\mathrm{head},K,-}}
-\frac{\delta}{\sqrt\mu}\|u\|
\right)
\right]^2.
\]
Subtracting this from a verified full-source \(a_+\) gives a valid upper for the reference direction.

Even a negative \(S_0\) direction does not prove a negative true-Schur direction: inverse comparison gives the true Schur **above** \(S_0\). The earlier positive directional result likewise does not establish matrix positivity.

**Overall correctness: correct, conditionally.** The proposed inequalities establish a sound uniform sufficient-bound framework. They do not establish a positive target matrix, all-support positivity, an implementable numerical budget, theorem admission, or RH. Confidence in the mathematical assessment: **0.98**.
