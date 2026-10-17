# SYS-2.2 — Combined low-to-tail Gram ordering and form-Schur positivity criterion

- **Finding ID:** F-20261017-002
- **Created:** 2026-10-17T12:11:00Z
- **Last updated:** 2026-10-17T12:13:09Z
- **Type:** DERIVED_RESULT
- **Status:** VERIFIED — mathematical quadratic-form proof, using the explicitly stated SYS-2.1 source/domain assumptions; not Lean-kernel formalization or numerical positivity
- **Claim:** C-0064
- **Source tree inspected:** `fcf4353adaf090480b695cf089bf9f17f5ad9f04` with the uncommitted SYS-2.1 findings preserved
- **Scope:** SYS-2.2 only: prove exact Gram ordering, form-Schur sufficiency, and positivity meaning. No mixed-kernel evaluation, certificate creation, theorem admission, or code change.

## 1. Precise theorem and hypotheses

Let \(0<T<\pi/2\), with the first \(\{2,3\}\) multi-prime support window
\[
 \tfrac12\log 3<T<\log 2
\]
being the immediate application. Adopt the **Suzuki normalized form** and established SYS-2.1 result `F-20261017-001` / `C-0063`:

\[
\begin{aligned}
 \mathcal H&=L^2((-1,1),dx;\mathbb C),\\
 \mathcal F_T&=D(J^{1/2})\cap D(V^{1/2}),\\
 \mathfrak l_T[f]&=\mathfrak j[f]+\mathfrak v[f]
    +\langle f,(P_T+R_T-c_TI)f\rangle ,
\end{aligned}
\]
where \(J\) is the self-adjoint Legendre jump operator with eigenvalues \(H_n\), \(V\) is multiplication by \(v(x)=-\tfrac12\log(1-x^2)\), \(P_T\) is the **combined** bounded self-adjoint signed prime-power translation, and \(R_T\) is the **full** bounded self-adjoint Suzuki residual. The scalar is \(c_T=\log(2\pi T)+\gamma\). \(\mathfrak l_T\) is a densely defined closed, lower-semibounded symmetric quadratic form with associated self-adjoint form operator. Its domain is the specified \(\mathcal F_T\), not all of \(\mathcal H\).

Fix \(N\ge1\). Write
\[
 E=E_N=\operatorname{span}\{P_0,\dots,P_{N-1}\},
 \quad F=E^\perp,\quad
 \Pi=\Pi_N,\quad Q=Q_N=I-\Pi .
\]
\(\Pi\) and \(Q\) are bounded orthogonal projections preserving \(\mathcal F_T\). Every \(u\in E\) lies in \(D(J)\cap D(V)\subset D(L_T^{\mathrm{form}})\), while \(q\in F\cap\mathcal F_T\) need *not* lie in \(D(V)\), \(D(J)\), or \(D(L_T^{\mathrm{form}})\).

For each \(X\in\{V,P_T,R_T\}\), define an everywhere-defined bounded finite-rank operator on \(\mathcal H\) by
\[
       B_X=QX\Pi:\mathcal H\longrightarrow F .
\]
This notation means **apply \(\Pi\) first**, placing the input in the finite-dimensional space \(E\subset D(X)\), then apply \(X\) and \(Q\); it does not assert that the potentially unbounded \(V\) is defined on all \(\mathcal H\). Restricted to \(E\), \(B_X:E\to F\) is bounded. Put
\[
             B=B_V+B_P+B_R:E\longrightarrow F .
\]
Every adjoint \(B_X^*:F\to E\) and \(B^*:F\to E\) exists and is bounded.

Define the exact low-form operator \(A_N:E\to E\) by
\[
 \langle u,A_Nv\rangle=\mathfrak l_T[u,v], \qquad u,v\in E,
\]
and define the tail quadratic form on \(F\cap\mathcal F_T\) by
\[
 \mathfrak c_N[q]=\mathfrak l_T[q].
\]
**Hypothesis (H-tail):** a real constant \(\mu_N>0\) is established such that
\[
       \mathfrak c_N[q]\ge\mu_N\|q\|^2
       \quad\text{for every }q\in F\cap\mathcal F_T.
\]
The previously derived bound \(\mu_N=H_N-c_T-\sum_{m\in\mathcal A(T)}c_mb_m-\rho_R\) is one sufficient way to establish (H-tail), provided that the numerical interval for it is rigorously strictly positive. SYS-2.2 **assumes** (H-tail); it makes no new numerical assertion about \(\mu_N\).

All inequalities below are on the *finite-dimensional low space* \(E\) unless explicitly stated otherwise. For self-adjoint operators \(S_1,S_2\) on \(E\), \(S_1\preceq S_2\) means \(\langle u,S_1u\rangle\le\langle u,S_2u\rangle\) for every \(u\in E\). \(S\succ0\) means \(\langle u,Su\rangle>0\) for every nonzero \(u\in E\).

## 2. Exact algebraic combined-Gram identity

For arbitrary bounded operators \(B_1,B_2,B_3:E\to F\), set \(B=B_1+B_2+B_3\). Direct expansion gives the **operator identity**
\[
 3\sum_{i=1}^3B_i^*B_i-B^*B
   =\sum_{1\le i<j\le3}(B_i-B_j)^*(B_i-B_j).
 \tag{2.1}
\]
It is an identity in the bounded self-adjoint operators on \(E\), not an approximation or an integral estimate.

**Proof.** For each \(u\in E\), let \(z_i=B_iu\in F\). The elementary Hilbert-space parallelogram expansion yields
\[
\begin{aligned}
 \sum_{i<j}\|z_i-z_j\|^2
  &=2\sum_i\|z_i\|^2
    -2\operatorname{Re}\sum_{i<j}\langle z_i,z_j\rangle\\
  &=3\sum_i\|z_i\|^2-\Big\|\sum_i z_i\Big\|^2.
\end{aligned}
\]
Polarization, or direct expansion of both sides, proves (2.1). Each summand on the right is positive semidefinite. Substituting \(B_V,B_P,B_R\) proves
\[
  \boxed{B^*B\preceq
    3\bigl(B_V^*B_V+B_P^*B_P+B_R^*B_R\bigr).}
 \tag{2.2}
\]
The result requires **no** signs, mutual commutativity, mutual orthogonality, disjoint prime supports, or positivity of \(V,P_T,R_T\). The only necessary algebraic condition is that the three \(B_X\) have a common Hilbert-space domain/codomain; that condition is established in SYS-2.1.

Equation (2.1) also describes the exact amount lost by the old three-component Cauchy–Schwarz estimate. It is not a sign test for the new combined Gram.

## 3. Domain-safe off-diagonal form decomposition

For \(u\in E\) and \(q\in F\cap\mathcal F_T\), the form \(\mathfrak l_T\) is well-defined on \(u+q\). SYS-2.1 establishes
\[
       \mathfrak l_T[u,q]=\langle Bu,q\rangle .
 \tag{3.1}
\]
Indeed \(J\) is exactly diagonal in the Legendre decomposition and \(-c_TI\) is scalar, so their low/tail cross terms vanish; the bounded prime and residual operators contribute through \(Q P_Tu\) and \(QR_Tu\). For the **unbounded** multiplier \(V\), we use \(u\in D(V)\) and form symmetry to obtain \(\mathfrak v[u,q]=\langle Vu,q\rangle\), *without* requiring \(q\in D(V)\).

Consequently, writing \(w=u+q\) with \(u=\Pi w\), \(q=Qw\),
\[
 \boxed{
 \mathfrak l_T[w]
   =\langle u,A_Nu\rangle
    +2\operatorname{Re}\langle Bu,q\rangle
    +\mathfrak c_N[q].
 }
 \tag{3.2}
\]
This is a quadratic-form block decomposition, **not** an assertion that the unbounded full operator is a bounded \(2\times2\) block matrix on \(E\oplus F\).

The form-tail domain \(F\cap\mathcal F_T\) is dense in \(F\), since \(Q\) maps the dense domain \(\mathcal F_T\) into itself and \(\operatorname{ran}Q=F\). The restricted form is closed: the finite-rank map \(\Pi:\mathcal F_T\to\mathcal F_T\) is bounded in the form norm (all low polynomial modes have finite form norm), hence \(F\cap\mathcal F_T=\ker(\Pi|_{\mathcal F_T})\) is closed in that norm. Its lower bound can therefore be understood in form sense; no multiplication of an undefined \(Q V Q\) on all \(F\) is involved.

## 4. Combined-block sufficient positivity theorem

**Theorem (form-Schur sufficiency).** Under the setting and (H-tail) from §1, let
\[
    S_{\mathrm{comb}}=A_N-\frac1{\mu_N}B^*B .
\]
If
\[
                     \boxed{S_{\mathrm{comb}}\succ0,}
 \tag{4.1}
\]
then \(\mathfrak l_T[w]>0\) for every \(0\ne w\in\mathcal F_T\). In fact there exists a constant \(\delta>0\) such that
\[
                    \mathfrak l_T[w]\ge\delta\|w\|^2
                    \qquad(w\in\mathcal F_T).
 \tag{4.2}
\]
Thus the self-adjoint operator associated with the closed form obeys \(L_T^{\mathrm{form}}\succeq\delta I\).

**Proof.** From (3.2) and (H-tail), for arbitrary \(w=u+q\in\mathcal F_T\),
\[
 \mathfrak l_T[w]
 \ge\langle u,A_Nu\rangle
    +2\operatorname{Re}\langle Bu,q\rangle
    +\mu_N\|q\|^2.
\]
The exact Hilbert-space square identity
\[
 \mu_N\|q\|^2+2\operatorname{Re}\langle Bu,q\rangle
  =\mu_N\Big\|q+\frac{Bu}{\mu_N}\Big\|^2
     -\frac{\|Bu\|^2}{\mu_N}
\]
therefore yields
\[
 \boxed{\displaystyle
 \mathfrak l_T[u+q]\ge
       \langle u,S_{\mathrm{comb}}u\rangle
       +\mu_N\Big\|q+\frac{Bu}{\mu_N}\Big\|^2.
 }
 \tag{4.3}
\]
The square is **only a norm in \(F\)**. We do *not* assume that \(Bu\in\mathcal F_T\) or evaluate the unbounded tail quadratic form on \(q+\mu_N^{-1}Bu\).

Because \(E\) is finite-dimensional, (4.1) implies
\(\langle u,S_{\mathrm{comb}}u\rangle\ge\lambda_N\|u\|^2\)
for some \(\lambda_N>0\). Let \(r=q+\mu_N^{-1}Bu\in F\). Equation (4.3) gives
\[
 \mathfrak l_T[u+q]\ge
  \lambda_N\|u\|^2+\mu_N\|r\|^2.
\]
The bounded triangular transform \((u,q)\mapsto(u,r)\) on \(E\oplus F\) is invertible, with inverse \((u,r)\mapsto(u,r-\mu_N^{-1}Bu)\) and
\[
 \|(u,q)\|\le
   \Big(1+\frac{\|B\|}{\mu_N}\Big)\|(u,r)\|.
\]
Hence an explicit valid coercivity constant is
\[
 \boxed{\displaystyle
 \delta=\frac{\min(\lambda_N,\mu_N)}
                  {(1+\|B\|/\mu_N)^2}>0.}
 \tag{4.4}
\]
This proves strict positivity and uniform \(L^2\) coercivity on the full closed-form domain. By the representation theorem the associated self-adjoint operator is bounded below by \(\delta I\). No inverse of \(C_N\), no full-operator square, and no undefined product \(VQ_NV\) was used. \(\square\)

**Critical qualification:** The positivity hypothesis (4.1) is not proved for any new \((T,N)\) in this finding. The theorem proves only an *implication*. A negative value in the former factor-3 sufficient matrix neither disproves (4.1) nor proves it.

## 5. Relation to the existing v2 factor-3 theorem

With \(G_X=B_X^*B_X\) and \(G_{\mathrm{comb}}=B^*B\), define the exact mathematical low-space operators
\[
 \begin{split}
 S_{\mathrm{old}}^{\mathrm{exact}}
     &=A_N-\frac3{\mu_N}(G_V+G_P+G_R),\\
 S_{\mathrm{comb}}^{\mathrm{exact}}
     &=A_N-\frac1{\mu_N}G_{\mathrm{comb}} .
 \end{split}
\]
By (2.1),
\[
 \boxed{\displaystyle
 S_{\mathrm{comb}}^{\mathrm{exact}}-
 S_{\mathrm{old}}^{\mathrm{exact}}
 =\frac1{\mu_N}\sum_{X<Y}(B_X-B_Y)^*(B_X-B_Y)
 \succeq0.}
 \tag{5.1}
\]
This is the precise sense in which the proposed exact combined-block sufficient criterion retains terms discarded by the old factor-3 bound. It proves that every *exact old-criterion* positive support would also pass the *exact new criterion* under the same \(\mu_N\), not that the new criterion passes anywhere else.

**Orientation compatibility with the frozen contract:** The frozen contract `docs/MULTI_PRIME_CONTRACT.md` writes a cross block from tail **to** low as \(B_N^{\mathrm{old}}=\Pi_N X Q_N\) and uses \(B_N^{\mathrm{old}}(B_N^{\mathrm{old}})^*\). Here \(B_X:E\to F\) points from low **to** tail, so the corresponding Gram is \(B_X^*B_X\). On the form domain the old tail-to-low cross term is the *bounded adjoint* \(B_X^*\), which extends the formal expression \(\Pi_N X Q_N\) where that expression makes sense. In particular \(\Pi_N VQ_N\) must **not** be applied as an everywhere-defined unbounded product to arbitrary \(q\in F\): \(B_V^*\) is the correct extension. The two descriptions give the same finite low Gram when correctly oriented, without changing the v1/v2 contract.

**Existing certificate enclosures are not exact equalities:** Current Python v2 assembly records a conservative lower enclosure \(\underline A_N\) (including \(-\delta_R D_N\)) and conservative residual Gram upper enclosure \(\overline G_R\), rather than the exact \(A_N\) and \(G_R\). Its Rust v2 arithmetic gate independently reconstructs the *frozen* factor-3 sufficient matrix, not \(S_{\mathrm{comb}}^{\mathrm{exact}}\). Equation (5.1) compares **mathematical exact operators** under common assumptions. It must not be used to label any existing serialized approximate/certificate matrix as the new exact combined-block matrix or to change the v2 admission rule.

**Legendre matrix normalization:** If \(K_{ij}=\langle P_i,SP_j\rangle\) represents \(S\) in the unnormalized polynomial basis, then positivity is the coordinate quadratic inequality \(z^*Kz>0\) for all \(z\ne0\). A Hilbert-space coercivity eigenvalue is that of \(D_N^{-1/2}KD_N^{-1/2}\), not an unadjusted ordinary eigenvalue of the underlying operator in the \(P_n\) basis. The two positivity tests are equivalent; their lower *constants* require the \(D_N\) normalization.

## 6. Assumptions, nonclaims, and completed checks

**Assumptions relied upon:**
- The exact scaled Suzuki form matches the original localized Weil form on its original admissible test class (`R-0028`; SYS-2.1 records this as an externally established input).
- Tuck's jump identity and the resulting Legendre spectral realization (`R-0032/0033`, `C-0045`).
- On \(0<T<\pi/2\), the *full* Suzuki residual is a bounded self-adjoint kernel with the established valid remainder; the arithmetic prime-power sum is finite and bounded.
- The closed form domain and low-mode operator-domain inclusion established by SYS-2.1 (`C-0063`).
- A **separately verified strictly positive** tail lower bound \(\mu_N\) whenever the criterion is applied.

**Checks completed in the proof:**
- The exact three-term polarization identity (2.1), with the coefficient \(3\) counting \(V,P,R\), **not** the number of prime powers.
- Correct low-to-tail orientation and adjoints, including the unbounded \(V\).
- The full form expansion (3.2) for every admissible \(u+q\).
- The norm-only completion of the square (4.3); no assumption \(Bu\in D(\mathfrak c_N)\).
- Strict positivity for every nonzero form vector and quantitative coercivity (4.4).
- The exact operator ordering (5.1), with no implication from failure of the old criterion.
- The precise distinction between exact Gram operators and current Arb/certificate *enclosures*.

**Not established or performed:** no positivity of \(S_{\mathrm{comb}}\) at \(T=11/20\) or any other support, no evaluation/enclosure of \(V/P/R\) mixed Gram integrals, no change to historical negative witnesses, no new certificate implementation or v2 admission, no local Lean formalization, and no claim of RH. No numerical qualification experiment was run.

**SYS-2.2 conclusion: COMPLETE as a paper-level conditional mathematical theorem.** The combined-cross-block criterion is a valid sufficient condition under the explicitly enumerated form/domain and positive-tail hypotheses. Its actual satisfaction at any support is a **different proposition**, not proved here.

## Sources

- [SYS-2.1 finding / C-0063](2026-10-17T115900Z-scaled-weil-operator-domain-and-low-tail-maps.md) — the needed operator domains, projection invariance, and full residual.
- [Frozen generic multi-prime contract](../docs/MULTI_PRIME_CONTRACT.md) and `C-0058/0059` — grouped \(V,P,R\), first \(\{2,3\}\) window, conservative tail complement and existing factor-3 sufficient operator.
- [Suzuki source R-0028](../references/BIBLIOGRAPHY.md) — source of the fixed finite-support normalization; not reproved here.
- [OAI-8 source comparison](../research/openai-math/RESEARCH_DIRECTION.md) — earlier statement of the conditional candidate, with no numerical positivity.
- [Current Python v2 assembly](../scripts/cert/multi_prime_legendre_schur.py) and [Rust v2 verifier](../crates/rh_cert/src/v2.rs) — the existing separate conservative enclosure/closed-admission implementation, unchanged.
