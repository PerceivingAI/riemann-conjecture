# A tail-restricted residual bound from Legendre differential regularity

- **Finding ID:** `F-20261024-007`
- **Created:** `2026-10-24T22:49:48Z`
- **Last updated:** `2026-10-24T23:00:41Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`, independently reviewed conditional derivation and independently reconstructed scalar consequence; not a smaller low-block positivity proof or production admission
- **Claim:** C-0088
- **Computation:** [X-20261024-005](../computations/2026-10-24T224948Z-tail-restricted-residual/record.md)

## Statement and source normalization

Work on L2([-1,1]) with the orthogonal Legendre projection P_N onto degrees0 through N-1 and Q_N=I-P_N, N>=1. The source truncated residual has integral kernel

\[
k_K(x,y)=\sum_{d=0}^K c_d|x-y|^d,
\qquad c_d=-a_dT^{d+1},
\]

where a_d are the exact Suzuki residual coefficients already implemented in `scripts/cert/residual_kernel.py:230-251`. Retain the established full-error bound ||R_T-R_K||<=delta(T,K). Its present source validity requires T>0 and2T<pi. The truncation order used for the current experiment remains K=38 at T=1353/2048.

Define the retained degree set

\[
I_N=\{d:1\le d\le K,\ d\text{ odd or }d\ge2N\},
\]

and the exact rational quantity

\[
M_N=6|c_1|
+\sum_{\substack{d\in I_N\\d\ge2}}
2^{d-1}(d+4)|c_d|,
\]

with c1=0 when absent. Then the proposed bound is

\[
\boxed{\|Q_NR_TQ_N\|
\le\rho_{\rm tail}(N,T,K)
:=\delta(T,K)+\frac{M_N}{N(N+1)}.}
\]

This is a bound for the entire infinite tail compression, not a norm inferred from finitely sampled high columns. It does not bound Q_N R_T P_N by the same small quantity, and it does not replace R_T by R_K.

## 1. Remove only polynomial terms annihilated by both projections

For even d, |x-y|^d=(x-y)^d. Expanding it gives rank-one polynomial kernels x^r y^(d-r). If d<2N, at least one of r,d-r is less than N. Orthogonality therefore gives

\[
Q_N\left[|x-y|^d\right]Q_N=0
\quad(d\text{ even},\ d<2N).
\]

The inequality is strict. Degree d=2N can survive and must not be discarded. The claim is about the double compression; it does not generally remove these terms from a low-to-tail block.

Let F_N be the integral operator with kernel sum_(d in I_N) c_d|x-y|^d. Then Q_N R_K Q_N=Q_N F_N Q_N. For2N>K, all even-degree polynomial terms disappear, but the odd absolute-power kernels remain.

## 2. Auxiliary differential operator, domain and cusp

Use the auxiliary self-adjoint Legendre operator L with normalized eigenvectors e_j and eigenvalues j(j+1). It is not the harmonic jump operator J, whose eigenvalues are H_j. Its differential expression is

\[
Lg=-\frac{d}{dx}\left[(1-x^2)g'(x)\right].
\]

For f in L2, g=F_N f belongs to H2([-1,1]). First kernel derivatives are bounded piecewise polynomials. In the weak second derivative, the degree1 cusp contributes a bounded multiplication term, and every other term has a bounded integral kernel:

\[
\begin{aligned}
(LF_N f)(x)
={}&-2c_1(1-x^2)f(x)\\
&+\int_{-1}^1\Bigg[
2x\sum_{d\in I_N}d c_d\operatorname{sgn}(x-y)|x-y|^{d-1}\\
&\hspace{38mm}-(1-x^2)\sum_{\substack{d\in I_N\\d\ge2}}
d(d-1)c_d|x-y|^{d-2}\Bigg]f(y)\,dy.
\end{aligned}
\]

This uses the distributional identity d2|x-y|/dx2=2 delta_y. Omitting that diagonal term would leave the written proof incomplete.

H2 regularity makes g,g' bounded with endpoint traces; hence (1-x^2)g' vanishes at both endpoints. Integration by parts against each Legendre polynomial has no boundary contribution and gives

\[
\langle e_j,Lg\rangle=j(j+1)\langle e_j,g\rangle.
\]

Because the differential expression Lg lies in L2, Parseval proves sum_j [j(j+1)]^2 |<e_j,g>|^2<infinity. Thus g belongs to the domain of the spectral Legendre operator. This establishes the needed range/domain statement directly, rather than assuming a boundary-extension characterization.

## 3. Uniform norm of the differentiated integral operator

For every integer p>=0,

\[
\sup_{|x|\le1}\int_{-1}^1|x-y|^pdy
=\frac{2^{p+1}}{p+1}.
\]

The same bound holds with x and y exchanged. Bounding |x| and1-x2 by1, the degree-d first-derivative kernel contributes at most2^(d+1)|c_d| to both Schur row and column bounds. For d>=2, the second-derivative kernel contributes at most d2^(d-1)|c_d|. The diagonal multiplication operator has norm at most2|c1|.

The Schur bound and triangle inequality give

\[
\|LF_N\|
\le2|c_1|+\sum_{d\in I_N}2^{d+1}|c_d|
+\sum_{\substack{d\in I_N\\d\ge2}}d2^{d-1}|c_d|
=M_N.
\]

This includes all retained signed source terms through a norm upper, not an unjustified sign assumption on the residual.

## 4. Infinite high-mode bound and complete remainder

For any f in L2, apply the domain result to g=F_N Q_N f. Parseval and j(j+1)>=N(N+1) for j>=N give

\[
\begin{aligned}
\|Q_N F_N Q_Nf\|^2
&\le\frac1{[N(N+1)]^2}\|L F_N Q_Nf\|^2\\
&\le\frac{M_N^2}{[N(N+1)]^2}\|f\|^2.
\end{aligned}
\]

Projection is contractive, so ||Q_N(R_T-R_K)Q_N||<=delta. Adding this proves the boxed estimate for the full residual. No derivative bound on the unknown full remainder is required.

## 5. Separate research complement, not a production contract change

Under the existing source form identity, V>=0 and the established arithmetic norm bound p(T)=sum c_m b_m, the restricted tail form satisfies

\[
C_N\succeq J_{\rm tail}
-[c_T+p(T)+\rho_{\rm tail}(N,T,K)]I.
\]

A separate research scalar lower is therefore

\[
\mu_N^{\rm tail}=H_N-c_T-p(T)-\rho_{\rm tail}(N,T,K).
\]

If this is positive, the same form-order argument can retain harmonic growth and define a stronger tail reference. This estimate is not silently substituted into the frozen global-rho production contract, historical certificates or old proof receipts.

A smaller sufficient scalar cutoff is not a proof of the low Schur matrix at that cutoff. The new tail-to-tail bound must not be substituted for the full/low-to-tail cross norm b in C-0085's residual allowance without another proof.

## Scope and pending checks

The derivation is local under the existing full-residual enclosure premise and does not cross an arithmetic threshold, establish a new full-positivity dimension, extend support, admit a theorem or prove RH. The coefficient/rank identities and domain/cusp constants need separate review. Scalar evaluation will use the current support and existing K, with separate coefficient/remainder reconstruction, not a new full matrix run. No literature-priority claim is made for the standard differential, projection or Schur tools.

## Qualification and executed consequence — 2026-10-24T23:00:41Z

The initial pending-check statement above is preserved as the pre-review state. Its exact initial bytes are retained in the computation's `derivation-v1.md`. The separate read-only mathematical review accepted the normalization, strict polynomial cutoff, cusp, constants, spectral-domain proof and inherited form-domain consequence without a mathematical correction. The second integration-by-parts boundary term also vanishes because g is bounded and (1-x2)e_j' vanishes at the endpoints. The captured review is [independent-review.json](../computations/2026-10-24T224948Z-tail-restricted-residual/independent-review.json).

At T=1353/2048,K=38, a fresh512-bit source calculation and separately organized1024-bit reconstruction agree. All39 exact kernel coefficients, four scalar enclosures and every scalar dimension1 through312 are checked. The complete remainder upper displays3.1042360135654356e-15 and remains included.

| Sufficient scalar quantity at this fixed support | Previous global-residual charge | Tail-restricted charge |
| --- | ---: | ---: |
| Residual norm allowance at N=312 | 3.010326025956 | 0.000000593923468717 |
| Complement lower at N=312 | 0.186527989134 | 3.196853421166 |
| First integer with positive scalar lower | 259 | 13 |
| First even integer with positive scalar lower | 260 | 14 |
| First integer preserving original exact reserve | 312 | 15 |
| First even integer preserving original exact reserve | 312 | 16 |

These integer thresholds are the first sufficient choices for the published outward rational charges, not necessary Weil or Schur dimensions. The original reserve displays0.18491998558724346. The new lower displays0.1263195895268871 at N=14,0.1930207801166317 at N=15 and0.25554921158237676 at N=16. Thus the reserve transition, not just scalar positivity, is explicitly separated.

The result identifies a large avoidable charge from applying a full-space residual norm to a double-compressed tail. Exact polynomial removal and Legendre smoothing justify the replacement; this is not a fitted smaller constant. At fixed K the bound decreases toward delta, not zero.

Both actual research CLIs passed, all4 focused exact-operator regressions passed, and actual omitted-remainder/false-cutoff/false-mu attacks rejected without success files. Isolated replay from the13 captured source/environment files regenerated byte-identical scalar and audit JSON without importing live project scripts. Finite controls include the nonzero d=2N polynomial boundary, annihilation below it, both constant/nonconstant cusp identities and a signed-kernel complete-image Gram bound. These controls do not replace the infinite-dimensional proof.

No new low matrix, signed heads, full positivity dimension, support point, Rust/Lean replay or theorem admission was executed. In particular, N=16 is a scalar-reserve result, not a new full-positivity certificate. Existing C-0087 and every retained admission remain unchanged. The cross-block allowance in C-0085 still requires its established full residual norm. No originality or RH conclusion follows.
