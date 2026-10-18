# SYS-6.1 — Verified baseline for fixed-support continuation

- **Finding ID:** F-20261018-003
- **Created:** 2026-10-18T07:53:59Z
- **Last updated:** 2026-10-18T07:53:59Z
- **Type:** ANALYTICAL SYNTHESIS / REPOSITORY-DERIVED SMOOTH-TEST CONSEQUENCE
- **Status:** **VERIFIED at paper level under explicitly attributed Suzuki Corollary 1.2 / Theorem 1.3 and existing C-0067 proof trust**
- **Claim:** C-0068 (source-dependent logical consequence; **no new independently certified larger support**)
- **Sources:** C-0067; C-0063..C-0065, C-0058, C-0040; F-20261018-002; X-20261018-003; **external** EXT-0002 / R-0028 (Suzuki arXiv:2606.09096v3, Corollary 1.2 / Theorem 1.3 and eq. 4.5).
- **Repository checked:** `main` at `97f34152929518ab8a991f7c174a7439b9b6c026` before this documentation-only work.

## 1. Exact consequences of C-0067

Let \(T_0=11/20\). The sole v3 certificate-admitted theorem `C-0067` states, in the globally defined **unscaled** Suzuki/Weil normalization, that for some \(\varepsilon_0>0\),
\[
Q_W(f)\ge\varepsilon_0\|f\|_{L^2(\mathbb R)}^2
\quad(f\in C_c^\infty(-T_0,T_0)).
\tag{1}
\]
The coefficient \(\varepsilon_0\) is existential. The **strictly positive Gershgorin margin of a congruence-transformed finite matrix is not itself the full Weil-form coercivity constant**: conversion would require control of the low-basis metric and triangular low/tail transformation (`C-0064`). No numerical \(\varepsilon_0\) is asserted.

**Downward support inheritance (elementary, independent of continuity).** For every \(0<t\le T_0\), zero extension gives
\[
C_c^\infty(-t,t)\subset C_c^\infty(-T_0,T_0).
\]
The unscaled \(Q_W\) and its ambient \(L^2(\mathbb R)\) norm do not change. Thus **the same** \(\varepsilon_0\) in (1) works for every such \(t\). This is an infinite family of test-class consequences from **one** admitted theorem. It does **not** show that the separately scaled Schur *sufficient matrix* \(S_N(t)\) is positive at fixed \(N=192\), or add any configuration to the closed v3 certificate whitelist.

**External lowest-eigenvalue continuity gives a right-hand neighborhood.** Let
\[
\lambda(t)=\inf_{0\ne f\in C_c^\infty(-t,t)}
   Q_W(f)/\|f\|_2^2.
\]
By Suzuki v3 **Corollary 1.2**, this equals the lowest eigenvalue of the corresponding canonical localized Weil form \(Q_W^t\). Equation (1) gives \(\lambda(T_0)\ge\varepsilon_0>0\). Suzuki v3 **Theorem 1.3** establishes continuity of \(\lambda(t)\) at every \(t>0\). By the epsilon-delta definition, there exists some \(\delta>0\) such that
\[
 0<t<T_0+\delta\quad\Longrightarrow\quad
 \lambda(t)>0 .
\tag{2}
\]
For instance, \(\lambda(t)>\varepsilon_0/2\) when \(T_0\le t<T_0+\delta\), after choosing a sufficiently small \(\delta\); for smaller \(t\) inequality (1) gives at least \(\varepsilon_0\). No effective numerical \(\delta\), exact new support, or computable quantitative modulus of continuity is supplied. This conclusion **uses an external published-source theorem** and has **not** passed a fresh v3 admission or independent proof replay.

**Monotonicity.** Test-space inclusion implies \(\lambda(t_2)\le\lambda(t_1)\) whenever \(0<t_1<t_2\); this follows directly from the infimum definition and is compatible with Suzuki's continuity. Neither monotonicity nor continuity alone extends positivity to an arbitrary larger support.

The unrestricted Weil criterion would require positivity on \(C_c^\infty(\mathbb R)=\bigcup_{t>0} C_c^\infty(-t,t)\), i.e. nonnegativity for each *finite* support. No single support-independent positive \(\varepsilon\) is logically required. No number of **isolated** certified support points, with a finite maximum, establishes that. A *proved unbounded support-covering family* with properly uniform logical quantification would be mathematically different. **RH remains unresolved.**

## 2. Why the SYS-5 combined-Schur mechanism works

In the scaled \(\mathcal H=L^2(-1,1)\) formulation, \(\mathfrak l_T=J-c_T I+V+P_T+R_T\) on the proper closed form domain, where:

- \(Je_n=H_ne_n\) is the exact nonlocal jump diagonal; \(H_N\) supplies high-Legendre tail coercivity.
- \(V(x)=-\frac12\log(1-x^2)\ge0\) is the endpoint multiplier, **unbounded** on all of \(\mathcal H\) but well-defined on finite low polynomial modes.
- \(P_T=-\sum_{\log m<2T}(\Lambda(m)/\sqrt m)S_{\log m/T}\) contains all *active prime powers* and their compressed translations. In the first multi-prime window the active set is exactly \(\{2,3\}\).
- \(R_T\) is the complete Suzuki residual integral operator, not an omitted correction.

Split into \(E_N=\operatorname{span}\{P_0,\ldots,P_{N-1}\}\) and orthogonal high tail \(F_N\). The complement lower estimate (`C-0058`) is
\[
\mu_N(T)=H_N-\underbrace{(\log(2\pi T)+\gamma)}_{c_T}
-\sum_{\log m<2T}\frac{\Lambda(m)}{\sqrt m}\,b_m(T)
-\rho_R(T),\quad b_m(T)\ge\|S_{\log m/T}\|.
\tag{3}
\]
Provided \(\mu_N>0\), let \(A_N\) be the exact low quadratic form and \(B=Q_N(V+P_T+R_T)|_{E_N}\). Then
\[
S_{\mathrm{comb}}=A_N-\mu_N^{-1}B^*B\succ0
\quad\Longrightarrow\quad\mathfrak l_T\ge\varepsilon_T I
\tag{4}
\]
as a **sufficient full-form criterion** (`C-0064`). The old factor-three bound replaced the **single** \(B^*B\) by \(3(B_V^*B_V+B_P^*B_P+B_R^*B_R)\) and loses cancellation; the rigorously negative factor-three sufficient matrix at this \(T\) is **not** a negative Weil operator.

The successful `C-0067` proof retained all nine ordered \(V/P/R_K\) image products, the \(P_2/P_3\) cross terms, and exact low-projection subtraction. A rigorously bounded residual truncation \(R_T=R_K+E_K\), \(\|E_K\|\le\delta_K\), gives for each \(\eta>0\):
\[
B^*B\preceq(1+\eta)B_K^*B_K+(1+\eta^{-1})\delta_K^2I.
\tag{5}
\]
In the ordinary **unnormalized** Legendre basis, the \(I\) term in (5) becomes \(D_N=\operatorname{diag}(2/(2i+1))\). The proof-bearing dyadic **Loewner** enclosures for the low \(A\), combined truncated Gram \(G_K\), positive \(\mu\), and \(\delta_K\) yield a conservative exact rational lower Schur matrix. A rational lower-triangular congruence with positive exact Gershgorin margins in **both parity sectors** verifies strict positivity. The independent Arb source-input gate separately reconstructed all 37,056 matrix slots plus \(\mu,\delta\).

**This explains the sufficient mechanism; it does not prove a support-parameter uniform estimate.** In particular, a finite congruence witness at \(T_0\) is not a symbolic witness at nearby \(T\).

## 3. Dependencies on support, dimension, analytic accuracy, and source constraints

| Quantity | Exact mathematical dependence | Evidence / limitation |
| --- | --- | --- |
| Prime-power set | \(\mathcal A(T)=\{m=p^k:\log m<2T\}\) | Piecewise constant; changes at \(T=\frac12\log m\) |
| Shift geometry | \(\tau_m(T)=\log m/T\), truncated translation overlap and image moments | Changes *within* a fixed arithmetic window |
| Prime coefficients | \(c_m=\Lambda(m)/\sqrt m\) for each active \(m\) | Fixed in one arithmetic window; number of terms increases at thresholds |
| Complement | (3), \(H_N=\sum_{k=1}^N 1/k\sim\log N+\gamma\), \(c_T=\log(2\pi T)+\gamma\), \(\rho_R(T)\) | At fixed \(N\), larger \(T\) increases \(c_T\); positive \(\mu_N\) is an **independent gate**, not an automatic consequence of positivity at \(T_0\) |
| Low block / Gram | \(A_N(T)\), \(B_K(T)^*B_K(T)\) retaining full mixed images and low projection | May gain or lose cancellation as \(T\) varies; **no proved monotonicity** |
| Residual | \(R_T\), Bernoulli order \(K\), norm error \(\delta_K(T)\) and \(\rho_R(T)\) | Full residual cannot be dropped; tail and truncation control must be rigorous at each \(T\) |
| Legendre cutoff | \(N\), parity, \(D_N\), \(H_N\), low-image polynomial degrees | Larger \(N\) strengthens \(H_N\) but changes *both* \(A_N,G_K\); no demonstrated general \(N(T)\) |
| Numerical enclosure | Arb precision, outward dyadic denominator bits, endpoint/cell decisions | Conditioning and interval width are independent certification costs, **not** theorems about support scaling |
| Exact proof cost | Current v3 stores two upper triangles: \(N(N+1)\) scalar interval slots in total, plus dense \(N\times N\) witness | At \(N=192\): exactly 37,056 intervals and 36,864 witness positions; serialization is a design cost, **not** a mathematical lower bound |

The SYS-5 execution was **one point only**: \(T_0=11/20,N=192,K=32,\eta=2^{-24}\), source producer at Arb-1024, outward dyadic 352-bit endpoints, and independent source acceptance at Arb-2048. Higher dimensions or supports may require different precision, residual order or proof witnesses. No measured support-to-cost growth law is established by a single point.

**Near-threshold tension.** At \(T_0=0.55\), the \(m=3\) term has only just appeared: \(\frac12\log3\approx0.549306144334\); the excess \(T_0-\frac12\log3\approx0.000693855666\). Its scaled translation is \(\tau_3=\log3/T_0\approx1.997476888487\), with scaled overlap \(2-\tau_3\approx0.002523111513\). Yet the **exact global compressed-shift operator norm is \(b_3=1\)** throughout this two-prime window (`C-0040`, `C-0058`), so the crude complement pays the full fixed \(c_3=\log3/\sqrt3\approx0.634284100598\), even arbitrarily close above entry. Thus the small overlap does **not** make the operator-norm loss small; it may make low-degree polynomial image contributions small. The cancellation retained in \(B^*B\) is therefore especially relevant and must be studied without conflating global norm and finite-low-mode behavior.

No continuity in **operator norm** of moving compressed shifts is claimed. Suzuki's separately proved continuity is for the **lowest eigenvalue** and is enough for the existential support neighborhood in §1.

## 4. Arithmetic support-regime map

The prime-power threshold condition is **strict**. At exactly \(T=\frac12\log m\), the \(m\)-term has zero translation overlap; it enters the active set only to the right.

| Regime / boundary | Approximate T | New arithmetic content / structural meaning |
| --- | ---: | --- |
| \(\frac12\log2\) | 0.346573590280 | \(2\) enters |
| \(\frac12\log3\) | 0.549306144334 | \(3\) enters; begins first two-prime window |
| **\(T_0=11/20\)** | **0.550000000000** | **C-0067 admitted; \(\{2,3\}\) active, barely beyond \(3\)** |
| \(\log2=\frac12\log4\) | 0.693147180560 | \(4=2^2\) enters; at same point \(\tau_2=1\) changes path geometry |
| \(\frac12\log5\) | 0.804718956217 | \(5\) enters; active \(\{2,3,4,5\}\) immediately afterward |
| \(\frac12\log7\) | 0.972955074528 | \(7\) enters |
| \(\frac12\log8\) | 1.039720770840 | \(8=2^3\) enters |
| \(\log3=\frac12\log9\) | 1.098612288668 | \(9=3^2\) enters, and \(\tau_3=1\) |
| \(\frac12\log11\) | 1.198947636399 | \(11\) enters |

The **first** structural interval directly beyond \(T_0\) is \(11/20<T<\log2\), still with exactly \(\{2,3\}\). No selected larger support in that window has a new independent certificate. Crossing \(T=\log2\) adds \(m=4\) and changes the existing \(m=2\) compressed-shift path geometry: by `C-0040`, \(\|S_{\log2/T}\|=1\) at \(T=\log2\), but \(\|S_{\log2/T}\|=\sqrt2\) immediately to its right. The new \(m=4\) norm likewise changes from zero overlap at entry to \(1\) immediately after entry. These can cause a **discontinuous conservative complement lower bound** even though Suzuki's *actual lowest localized eigenvalue is continuous*. The v3 \(\{2,3\}\) proof cannot simply be reused across this wall.

The proof's current residual expansion and form-source checks were made within \(0<T<\pi/2\). Beyond that, new source-domain/analytic handling may be necessary; no all-support extension is asserted by the present formulas. The unrestricted RH criterion ranges over *all* compact supports, far beyond a finite threshold table.

## 5. Evidence classification and closure decision

**PROVED locally under the established Suzuki/Arb trust model:** `C-0067` at the single admitted \(T_0,N\), and (by elementary test-space inclusion) positivity for all \(0<t\le T_0\).

**SOURCE-DEPENDENT VERIFIED DEDUCTION (not separately certificate-admitted):** `C-0068` combines `C-0067` with Suzuki's *external* Corollary 1.2 and Theorem 1.3 to conclude positivity on an *unspecified* interval immediately above \(T_0\). This does not name its upper endpoint or give any new finite-support proof object.

**EXACT STRUCTURAL IDENTITIES:** finite prime-power activation thresholds, shift geometry, norm formula, complement inequality, full mixed-Gram Schur sufficiency, residual Young/Loewner bounds.

**NOT PROVED:** sign of the combined Schur criterion at any selected \(T>T_0\); quantitative rightward neighborhood; a scaling law or \(N(T)\) bound; a valid all-\(T\) combined inequality; domain equality beyond the smooth source-test class; all-support Weil nonnegativity and RH.

**SYS-6.1 COMPLETE:** All five baseline objectives have been checked and mapped without new Arb dimensions, numerical positivity claims, new v1/v2/v3 theorem admissions, Rust/Lean modifications, or private-roadmap disclosure. The verified barrier for further support study is *quantifying* and *scaling* the sufficient criterion, not merely duplicating an existing positive matrix.
