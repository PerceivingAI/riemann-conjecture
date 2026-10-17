# SYS-2.4 — Independent analytical-validity review of the combined Weil form and mixed Gram

- **Finding ID:** F-20261017-004
- **Created:** 2026-10-17T12:28:38Z
- **Last updated:** 2026-10-17T12:31:23Z
- **Type:** DERIVED_RESULT (independent proof verification, not a new positivity theorem)
- **Status:** VERIFIED for the *scoped conditional mathematical identities*; the distinction between canonical source operator domains and the constructed closed-form operator remains explicit
- **Claims checked:** C-0063, C-0064, C-0065 (no new C-claim registered)
- **Audited repository HEAD:** fcf4353adaf090480b695cf089bf9f17f5ad9f04, with uncommitted SYS-2.1–2.3 documentation preserved
- **Scope:** Source formula, domain, mixed-image algebra, remainder, and complementary form bounds **only**. No proof-certificate change, no new support positivity, no numerical search, no historical backfill.

## Conclusion

**The exact operator-domain and combined-Gram sufficient-condition mathematics in C-0063–C-0065 survives an independent analytical check in the specified range \(0<T<\pi/2\).** The full quadratic-form proof, low/tail projection formulas, all \(V/P/R\) and cross-prime terms, and the stated remainder inequalities have been rederived from definitions rather than assumed from those claims. No falsified identity or incorrect sign/normalization was identified within that scope.

**Necessary precision of interpretation:** agreement of the constructed form with Suzuki's localized Weil form on \(H_0^1(-1,1)\) and, in particular, the original admissible smooth test functions is supported directly by Suzuki's formula. Identification of **every vector in the constructed closed-form domain** with **every vector in the canonical source Friedrichs-extension form domain**, or equality of their entire self-adjoint operator domains, was **not independently established** here or by C-0063. The conditional implication *positivity on the constructed form domain ⇒ positivity on the source admissible test class* needs only the verified agreement/inclusion, **not** those global domain equalities. Treating such a stronger equality as verified would exceed the evidence.

No hypothesis that the combined Schur matrix is positive, or that \(\mu_N>0\) at an untested parameter pair, has been introduced.

## 1. Independent source and normalization check — PASS

The directly consulted primary source is Masatoshi Suzuki, *Weil's quadratic form via the screw function*, [arXiv:2606.09096v3, 2026-09-23](https://arxiv.org/html/2606.09096v3), notably equations **(2.2)–(2.5)** and **(4.1)–(4.5)**. The repository's R-0028 retains its **historical August v2** verification metadata. The newer version was checked as **additional current source evidence**; no claim of a byte-for-byte source-version comparison or rewriting of that earlier provenance is made.

Suzuki's original unscaled form on \(H_0^1(-T,T)\), with \(r\) the full even residual, includes
\[
 \mathcal L_T(v)
 -(2A+1)\|v\|^2
 -\sum_{\log m<2T}\frac{\Lambda(m)}{\sqrt m}
    \bigl(\langle U_{\log m}v,v\rangle+\langle U_{-\log m}v,v\rangle\bigr)
 -\iint r''(x-y)v(y)\overline{v(x)}\,dx\,dy,
\]
where the source's **\(A\)** (not our finite low matrix) is
\[
 A_{\rm Suzuki}=\tfrac12\bigl(\log(2\pi)+\gamma-1\bigr).
\]
After \(t=Tx\) and division by the \(L^2\) norm, the Rayleigh form on \((-1,1)\) is
\[
 \mathfrak l_T=\mathfrak j+\mathfrak v-c_TI
               +P_T+R_T,\qquad
 c_T=\log(2\pi T)+\gamma;
\]
indeed
\[
 \log T+(2A_{\rm Suzuki}+1)
   =\log T+\log(2\pi)+\gamma=c_T.
\]
Thus \(-c_T\), \(V(x)=-\frac12\log(1-x^2)\), the **negative** combined shifts \(-c_mS_{\log m/T}\) with \(c_m=\Lambda(m)/\sqrt m\), and the **negative** residual kernel \(-T r''(T|x-y|)\) all have the right signs and scale. The two-sided prime shift is counted once with two translates, not twice. There is no omitted Jacobian factor multiplying the prime coefficient after the unitary scaling.

The scalar, jump, and potential normalization also follow from Suzuki's source equation (4.4):
\[
\mathfrak j[w]=\tfrac14\iint_{I^2}\frac{|w(x)-w(y)|^2}{|x-y|}\,dx\,dy,\quad
\mathfrak v[w]=-\tfrac12\int_I\log(1-x^2)|w(x)|^2\,dx.
\]
The retained local source/code mappings checked include `scripts/cert/constants.py`, `scripts/cert/legendre_schur.py`, `scripts/cert/prime_power_terms.py`, `scripts/cert/multi_prime_legendre_schur.py`, and `scripts/cert/residual_kernel.py`.

## 2. Domain, adjoints and source-test-class distinction — PASS, with a scope guard

Let \(H=L^2(-1,1)\) and let \(e_n=\sqrt{(2n+1)/2}\,P_n\). Tuck's identity gives \(Je_n=H_ne_n\) for the nonnegative jump operator, fixing the \(1/4\) coefficient and \(\mathfrak j[q]\ge H_N\|q\|^2\) for the tail \(q\perp e_0,\ldots,e_{N-1}\).

The multiplier \(Vf=vf\), \(v=-\frac12\log(1-x^2)\), is **not globally bounded** but is nonnegative self-adjoint. Since \(v\in L^p(-1,1)\) for all finite \(p\), every low polynomial \(u\) satisfies \(vu\in L^2\); hence \(E_N\subset D(V)\). The arithmetic operator is a **finite sum of bounded adjoint-paired compressed translations**, and the full residual is a bounded symmetric integral kernel for \(2T<\pi\). Consequently
\[
 \mathcal F_T=D(J^{1/2})\cap D(V^{1/2})
\]
is dense and complete in the sum-form norm; bounded real-symmetric terms give a closed lower-semibounded form and its associated self-adjoint form operator. Nothing requires treating \(V\) as bounded or forming an unverified global operator sum on all of \(H\).

The low finite-rank projection \(\Pi_N\) preserves \(\mathcal F_T\), so \(Q_N=I-\Pi_N\) preserves it also. The operators
\[
 B_X=Q_NX\Pi_N:H\to Q_NH,\qquad X\in\{V,P_T,R_T\},
\]
are bounded because their inputs after \(\Pi_N\) lie in finite \(E_N\subset D(X)\). Their adjoints are bounded on the tail space even when \(\Pi_NVQ_N\), treated as a naive unbounded product, is not defined on arbitrary tail vectors.

For any \(u\in E_N\), \(q\in Q_N\mathcal F_T\), form polarization is valid and the jump/scalar cross terms vanish:
\[
 \mathfrak l_T[u+q]
 =\langle u,A_Nu\rangle
  +2\operatorname{Re}\langle Bu,q\rangle
  +\mathfrak c_N[q].
\]
One does **not** need \(q\in D(J)\cap D(V)\). The source equation (4.5) gives equality on \(H_0^1\) test functions and thus on the original \(C_c^\infty\) admissible class. This suffices for the *conditional* implication in C-0064. Full source-operator domain identification is deliberately not asserted; it is **NOT ESTABLISHED** by this audit.

**Additional domain check (not needed by the proofs):** For each *fixed low polynomial* \(u\), \(V^2u\in L^2\), while \(P_Tu,R_Tu\) are bounded functions (compressed polynomial translates and a bounded-kernel integral). Thus \(V(P_Tu+R_Tu)\in L^2\), and \(W=V+P_T+R_T\) satisfies \(Wu\in D(V)=D(W)\). Hence in this particular setting **\(u\in D(W^2)\)** and \(Q_NWu\in D(W)\) as well. This independently shows that low-column expressions involving \(WQ_NW\) can be interpreted where needed. However, C-0065's image-inner-product definition is more robust and avoids imposing this stronger hypothesis in the theorem statement. This does **not** assert \(D(W^2)=H\).

## 3. Projection and all mixed terms — PASS

In the unnormalized Legendre basis, \(D_N=\operatorname{diag}(2/(2i+1))\) and
\[
 \Pi_Nf=\sum_{k<N}\frac{\langle P_k,f\rangle}{d_k}P_k.
\]
For \(X,Y\in\{V,P,R\}\) define
\(K_X(i,j)=\langle P_i,XP_j\rangle\),
\(M_{XY}(i,j)=\langle XP_i,YP_j\rangle\).
Because each low image belongs to \(L^2\), independently applying \(Q=I-\Pi\) gives
\[
 \langle QXP_i,QYP_j\rangle
 =M_{XY}(i,j)-[K_XD_N^{-1}K_Y]_{ij}.
\]
The correct **nine ordered** terms are
\[
 VV,\;VP,\;VR,\;PV,\;PP,\;PR,\;RV,\;RP,\;RR.
\]
Their sum yields \(G_{\rm all}=M-KD_N^{-1}K\). The three unordered Hermitian mixed contributions \(VP+PV\), \(VR+RV\), \(PR+RP\) are all present with matching projected-low subtraction. They may be individually **indefinite**; none is silently replaced by zero.

The \(PP\) component is the inner product of images of **the combined** \(P=\sum_{m\in\mathcal A(T)}P_m\), and therefore contains every ordered pair \((m,n)\), including \(P_2/P_3\) in the current window, without presupposing commutation. The exact opposite-parity entries vanish from reflection symmetry for all three operators. The matrix \(G_{\rm all}\) remains positive semidefinite because it is the Gram of actual tail vectors. The exact-rational algebra check reported by SYS-2.3 independently verified the \(D_N^{-1}\) placement and mixed terms; those checks are algebraic diagnostics and not Suzuki-kernel computations.

## 4. Full Suzuki residual and error bounds — PASS

Suzuki's v3 §2.4 explicitly gives
\[
 r_0''(u)=-2\cosh(u/2),\qquad
 r_1''(u)=\frac{e^{-u/2}}{1-e^{-2u}}-\frac1{2u}
 \quad(u>0).
\]
The generating function of Bernoulli polynomials yields
\[
 r_1''(u)=\sum_{m\ge0}
    \frac{B_{m+1}(3/4)\,2^m}{(m+1)!}u^m,
 \quad |u|<\pi.
\]
The poles of the generating function nearest zero occur at \(u=\pm i\pi\); the \(u=0\) singularity is removable. The `r0` series is entire.

**Independent analytical remainder check.** For \(n\ge2\) the Bernoulli Fourier series at \(3/4\) has a sinusoidal Dirichlet-beta sum (odd \(n\)) or an alternating even-index sum (even \(n\)). Each absolute normalized sum is at most \(1\); thus
\[
 |B_n(3/4)|\le\frac{2n!}{(2\pi)^n}.
\]
The omitted positive-side \(r_1''\) coefficients therefore have \(|[u^m]r_1''|\le\pi^{-(m+1)}\), so the code's **larger** remainder bound
\[
 E_1(U,K)=\frac{2}{\pi}\frac{(U/\pi)^{K+1}}{1-U/\pi}
\]
is conservative for \(0\le U<\pi\). Similarly the exponential-series ratio gives
\[
 E_0(U,K)=\frac{2(U/2)^{K+1}}{(K+1)!}
     \frac1{1-(U/2)/(K+2)}.
\]
The repository's `_suzuki_residual_tail_radius` returns \(E_0+E_1\). In the current region \(U=2T<2\log2<\pi\); all denominators are strictly positive. The kernel-error supremum is therefore at most \(E_0(2T,K)+E_1(2T,K)\), and Schur's test on an interval of length \(2\) gives
\[
 \|R_T-R_{T,K}\|\le
 \delta_K=2T\left(E_0(2T,K)+E_1(2T,K)\right).
\]
A bounded real symmetric kernel proves \(R_T=R_T^*\) and \(\|R_T\|\le\rho_R=2T\sup_{|u|\le2T}|r''(u)|\).

**Independent numerical consistency diagnostic, not a proof substitute:** at 75 decimal digits, the exact closed \(r''\) formula was compared with the Bernoulli series through order \(32\) at \(u=0.1,0.4,1,1.38,1.5\). The respective absolute discrepancies were approximately \(3.97\cdot10^{-52}\), \(1.16\cdot10^{-31}\), \(3.61\cdot10^{-18}\), \(1.90\cdot10^{-13}\), and \(3.15\cdot10^{-12}\), each below the formula's stated analytic upper remainder (the upper bounds range from \(2.58\cdot10^{-50}\) to \(3.10\cdot10^{-11}\)). These samples do **not** certify uniformity; the preceding analytic bounds do.

With \(E_K=R_T-R_{T,K}\) and \(\Delta B=Q_NE_K|_{E_N}\),
\[
 B=B_K+\Delta B,\quad\|\Delta B\|\le\delta_K,
\]
so expansion and operator Cauchy–Schwarz/Young inequalities independently give exactly the SYS-2.3 bounds
\[
 \|B^*B-B_K^*B_K\|\le2\|B_K\|\delta_K+\delta_K^2
\]
and
\[
 B^*B\preceq(1+\eta)B_K^*B_K+
             (1+\eta^{-1})\delta_K^2 I\quad(\eta>0).
\]
In the unnormalized Legendre coordinates, every scalar operator-order remainder must be multiplied by \(D_N\), as in C-0065. A code output using the old separate `GR` bound is **not** equal to the new exact combined Gram.

## 5. Complement lower bound and full-form positivity criterion — PASS (conditional)

For \(q\in Q_N\mathcal F_T\),
\[
 \mathfrak j[q]\ge H_N\|q\|^2,\quad
 \mathfrak v[q]\ge0,\quad
 \langle q,P_Tq\rangle\ge-\sum_m c_m b_m\|q\|^2,\quad
 \langle q,R_Tq\rangle\ge-\rho_R\|q\|^2
\]
by Legendre orthogonality, \(v\ge0\), each bounded self-adjoint \(S_{\tau_m}\) with \(\|S_{\tau_m}\|\le b_m\), and the bounded self-adjoint full residual. Hence the full *quadratic-form* tail estimate is
\[
 \boxed{\mathfrak c_N[q]\ge
  \left(H_N-c_T-\sum_{m\in\mathcal A(T)}c_mb_m-\rho_R\right)
   \|q\|^2.}
\]
For \(\frac12\log3<T<\log2\), the active set is exactly \(\{2,3\}\); \(1<\tau_2,\tau_3<2\) and each compressed-shift norm is \(b_2=b_3=1\) by the existing path-chain argument. The bound is therefore \(H_N-c_T-c_2-c_3-\rho_R\) there.

This proves a **valid lower bound**, but the inequality \(\mu_N>0\) must be proved separately at the actual target \((T,N)\). Neither existence of a positive \(\mu_N\) *for every* \(N\) nor positivity of the combined Schur matrix is established by this audit. The algebraic form-Schur implication from SYS-2.2 remains valid whenever \(\mu_N>0\) and \(S_{\rm comb}=A_N-\mu_N^{-1}B^*B\succ0\) are separately verified.

Complete-square proof uses only the ordinary \(H\)-norm of \(q+\mu_N^{-1}Bu\), **not** the value of the tail quadratic form at that vector. The finite-dimensional \(S_{\rm comb}\succ0\) yields a positive \(\lambda_N\), and the bounded triangular change of coordinates yields the valid coercivity constant
\[
 \delta=
 \frac{\min(\lambda_N,\mu_N)}{(1+\|B\|/\mu_N)^2}>0.
\]
No inverse of an unbounded tail operator has been used.

## 6. Audit checklist and disposition

| Mathematical requirement | Result | Exact qualification |
|---|---|---|
| Suzuki normalization and signs | **PASS** | Checked v3 equations (2.2), (2.5), (4.4), (4.5); scalar, shifts, Jacobian, full residual agree |
| Domain and self-adjointness | **PASS for the constructed closed form** | \(V\) unbounded; bounded finite-column maps and closed form are valid. **Canonical source full-domain equality NOT ESTABLISHED** |
| Low/tail projections | **PASS** | \(\Pi_N\), \(Q_N\) preserve the form domain; low \(D_N^{-1}\) projection mandatory |
| All cross terms | **PASS** | Nine \(V/P/R\) ordered products, all \(P_m/P_n\) ordered products, all matching low-subtraction pieces present |
| Full residual and remainder | **PASS** | Checked explicit source formula, series coefficients, analytic uniform remainder and operator-norm implications for \(2T<\pi\) |
| Complement lower bound | **PASS as an inequality** | Sign, positive potential, full \(R\), compressed shifts verified; **strict \(\mu_N>0\) is parameter-dependent** |
| Combined criterion | **PASS as conditional sufficient theorem** | No actual combined-Schur positivity established |
| Global equivalence to canonical source operator | **NOT ESTABLISHED** | Not required for positivity on original admissible test class; must not be presented as a proved equality |

**Failed mathematical requirements discovered in the six scoped calculations:** none. **Claims not independently established:** full canonical source-operator/form-domain identification and positivity of \(\mu_N\) or the combined sufficient matrix at new supports. They are limitations of what was proved, not counterexamples to the algebra.

No new code was written, no mathematical qualification run was used to bypass any hypothesis, and no historical certificate, contract, negative direction, or conclusion was modified.

## Source/evidence references

- Suzuki, Masatoshi, [*Weil's quadratic form via the screw function*, arXiv:2606.09096v3](https://arxiv.org/html/2606.09096v3), §§2.2–2.4, 3.1, 4.2, especially (2.2), (2.5), and (4.5); R-0028 retains the original August citation status.
- [SYS-2.1 domain proof / C-0063](2026-10-17T115900Z-scaled-weil-operator-domain-and-low-tail-maps.md).
- [SYS-2.2 conditional Schur proof / C-0064](2026-10-17T121100Z-combined-cross-block-form-schur-criterion.md).
- [SYS-2.3 exact combined Gram / C-0065](2026-10-17T121809Z-exact-mixed-low-tail-gram-identities.md).
- [Historical combined-prime complement and Schur contract](../docs/MULTI_PRIME_CONTRACT.md), C-0058/C-0059; [normalized constants](../scripts/cert/constants.py); [potential/jump moments](../scripts/cert/legendre_schur.py); [prime-power images](../scripts/cert/prime_power_terms.py); [multi-prime assembler](../scripts/cert/multi_prime_legendre_schur.py); [Suzuki residual code](../scripts/cert/residual_kernel.py).
