# Coupled-mode diagnosis and a projection certificate on the known low space

- **Finding ID:** `F-20261025-001`
- **Created:** `2026-10-25T00:15:55Z`
- **Last updated:** `2026-10-25T00:15:55Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `PROVISIONAL`, projection algebra written before independent qualification and evaluation
- **Proposed claim:** C-0090
- **Computation:** [X-20261025-001](../computations/2026-10-25T001555Z-coupling-derived-projection/record.md)

## Fixed source and scope

Use the independently accepted C-0089 inputs at T=1353/2048,K=38, original low dimension n0=16 and retained head boundary m=54. Keep the full source W=V+P+R_T and truncated source W_K=V+P+R_K, with ||R_T-R_K||<=delta. All diagnostics use the original ordinary Legendre mass d_j=2/(2j+1).

The question is which modes caused the recorded reference failures and which even projection L>=16 removes the obstruction on the known P16 low space. This does not assume positivity on the larger P_L space. New low rows and their couplings remain a separate obligation.

## Correct reference when the projection changes

For16<=L<=54, use C-0088's full residual compression upper

\[
\rho_L^+=\delta_{\rm comp}^++M_L/[L(L+1)],\qquad
\mu_L=H_L-c_T^+-p^+-\rho_L^+>0.
\]

All scalar uppers are the retained rational enclosures. The new reference eigenvalues and inverse weights are

\[
\lambda_{k,L}=\mu_L+H_k-H_L,\qquad
w_{k,L}=1/\lambda_{k,L},\quad k\ge L.
\]

The subtraction uses H_L, not H16. Padding a tested vector in P16 with zero coefficients embeds it in P_L without changing its low-form value or physical norm. C-0072's form ordering applies with the C-0088 complement; it does not identify form domains or give positivity of untested low directions.

## Gram shift and complete weighted majorant

Let t_k=(<P_k,W_K P_j>)_(j<16), so each rank-one physical contribution is t_k* t_k/d_k. The accepted complete Gram is G16=(Q16 W_K P16)*(Q16 W_K P16). Orthogonal projection gives

\[
G_L^{(16)}=G_{16}-\sum_{16\le k<L}t_k^*t_k/d_k.
\]

Splitting the inverse-weighted tail at m gives the complete upper

\[
\begin{aligned}
U_{L,m}
={}&w_{m,L}G_{16}
-w_{m,L}\sum_{16\le k<L}t_k^*t_k/d_k\\
&+\sum_{L\le k<m}(w_{k,L}-w_{m,L})t_k^*t_k/d_k.
\end{aligned}
\]

The negative prefix subtraction is essential. Deleting old head rows without changing G16 would continue charging the promoted modes to the tail. Unknown modes k>=m remain paid through w_m G_m. Signed V/P/RK amplitudes must be added before squaring; their cross terms are not optional.

Let A^- be the source-enclosed low lower on P16 and U^+ a valid Loewner upper from the complete U interval matrix. The established full cross norm b remains unchanged. Since projection is contractive, C-0085 gives the sufficient old-subspace lower

\[
S_{0,L}|_{P16}\succeq A^- -U^+-r_LD_{16},\quad
r_L=\delta(1+2b/\mu_L)+\delta^2/\mu_L.
\]

All scalar arithmetic is rounded outward. Exact positive witnesses for both8-dimensional parity blocks would certify only this known P16 compression. Selecting the first even L carrying those certificates is a data-derived rule, not a theorem that all smaller dimensions are impossible or that the complete P_L reference is positive.

## Mode diagnosis and genuine directional brackets

For either retained trial z, let a_(alpha,k)=sum_j z_j<P_k,W_(alpha,K)P_j>, with alpha in V,P,RK. Mode energy is

\[
s_k=|a_{V,k}+a_{P,k}+a_{RK,k}|^2/d_k.
\]

The signed decomposition contains the three squared amplitudes and all three doubled cross products. Its original weighted charge is w_(k,16)s_k. Use intervals for every term, not midpoint signs. A first ascending prefix producing a negative genuine reference upper localizes a sufficient source of the original failure; it is not a uniqueness statement about causes.

For any L in the retained window, the complete omitted unweighted mass is bounded through

\[
\gamma_m= z^*G_{16}z-\sum_{16\le k<m}s_k\ge0.
\]

Write j_L=sum_(L<=k<m)w_(k,L)s_k. Then the truncated full inverse energy lies between j_L and j_L+w_(m,L)gamma_m. With exact physical squared norm nu=z*D16 z and e_L=delta sqrt(nu/mu_L), full-source inverse energy is bounded below by (sqrt(j_lower)-e_L)_+² and above by (sqrt(j_upper+w_m gamma_upper)+e_L)². Combining with the full low bracket aK±delta nu yields both reference bounds. Neither discarded head rows nor the unknown infinite tail is silently set to zero.

## Initial qualification status

The mathematical review, numerical mode attribution and projection selection are pending at creation. No new matrix positivity, projection value, support, admission or RH conclusion is asserted here. The initial bytes will be preserved before recording the executed consequence.
