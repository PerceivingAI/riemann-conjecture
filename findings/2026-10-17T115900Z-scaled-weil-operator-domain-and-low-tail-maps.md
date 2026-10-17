# SYS-2.1 — Exact scaled Weil form, domain, and low-to-tail maps

- **Finding ID:** F-20261017-001
- **Created:** 2026-10-17T11:59:00Z
- **Last updated:** 2026-10-17T12:01:35Z
- **Type:** DERIVED_RESULT
- **Status:** VERIFIED — paper-level Hilbert-space argument under the explicitly cited Suzuki normalization; not a Lean-kernel proof
- **Claim:** C-0063
- **Scope:** The operator/domain interface only. No combined-Gram inequality, positivity test, or new certificate claim.
- **Source revision inspected:** fcf4353adaf090480b695cf089bf9f17f5ad9f04
- **Research boundary:** Existing v1/v2 contracts, computational evidence, and theorem admissions are unchanged.

## Statement

Let \(0<T<\pi/2\) and, for the prime-power continuation application, use the strict first multi-prime window
\[
 \tfrac12\log 3<T<\tfrac12\log 4=\log 2.
\]
Assume the established Suzuki scaled formula (source **R-0028**, equation (4.5)) in the precise normalization restated in §1. Then the finite Legendre subspace is contained in the *operator* domain of the closed semibounded form realization of
\[
                 L_T=J-c_T I+V+P_T+R_T.
\]
Each of the three individual low-to-tail maps
\[
 B_{X,N}:=Q_NX\big|_{E_N}:E_N\longrightarrow E_N^\perp,
 \qquad X=V,P_T,R_T,
\]
is a well-defined **bounded map from the finite-dimensional low space to \(L^2\)**, even though \(V\) is unbounded on the whole Hilbert space. The jump and scalar components have zero low/tail cross form. The full residual **\(R_T\)**, rather than only a polynomial Taylor truncation, defines a bounded self-adjoint integral operator in the indicated support range. All these statements follow without asserting positivity of a combined low-to-tail Gram or any new Weil theorem.

The exact form realization, its domain, and the distinction between low-block exact mathematics and conservative generator enclosures are specified below.

## 1. Hilbert space, scaling, normalization

Use the complex Hilbert space
\[
 H=L^2((-1,1),dx;\mathbb C),\qquad
 \langle f,g\rangle=\int_{-1}^{1}\overline{f(x)}g(x)\,dx,
\]
with the unweighted measure \(dx\); the quadratic form is real on its diagonal. The scaled variable is \(x=t/T\). The norm-preserving change from \(L^2((-T,T),dt)\) is
\[
 (U_T f)(x)=\sqrt{T}\,f(Tx).
\]
Define the ordinary (not \(L^2\)-normalized) Legendre polynomials \(P_n\) with
\[
 \|P_n\|_H^2=d_n=\frac{2}{2n+1},\qquad
 e_n=d_n^{-1/2}P_n.
\]
Thus \(\{e_n\}_{n\ge0}\) is an orthonormal basis of \(H\), while the implementation assembles most matrices in the *unnormalized* \(P_n\) basis with low-space Gram matrix \(D_N=\operatorname{diag}(d_0,\dots,d_{N-1})\).

**The normalized Suzuki quadratic form used in the repository** is
\[
 \mathfrak l_T[f]=\mathfrak j[f]+\mathfrak v[f]
       +\langle f,P_Tf\rangle+\langle f,R_Tf\rangle
       -c_T\|f\|^2,
 \qquad c_T=\log(2\pi T)+\gamma,
\]
where
\[
 \mathfrak j[f]
   =\frac14\int_{-1}^{1}\int_{-1}^{1}
       \frac{|f(x)-f(y)|^2}{|x-y|}\,dx\,dy,\qquad
 \mathfrak v[f]
   =\int_{-1}^{1}v(x)|f(x)|^2\,dx,\qquad
 v(x)=-\tfrac12\log(1-x^2).
\]
The actual multiplier is \(Vf=vf\), and **\(v\ge0\)** almost everywhere. The Suzuki residual has not been omitted. The coefficient \(c_T\) is the scalar subtraction, *not* the arithmetic coefficient \(c_m\). These formulas reproduce the historical normalization checks in A-20260821-003/004 and the current `scripts/cert/constants.py`, `legendre_schur.py`, and `multi_prime_legendre_schur.py`.

This result **uses**, rather than independently reproves, the identification of this scaled form with Suzuki's localized Weil functional on its original admissible test class. The paper's original source formulation and its reference to test functions must not be confused with the larger closed-form domain introduced below.

## 2. Exact jump realization

Set \(H_0=0\), \(H_n=\sum_{k=1}^{n}k^{-1}\), and define the nonnegative self-adjoint diagonal operator
\[
 J e_n=H_n e_n,\qquad
 D(J)=\left\{f=\sum a_ne_n:\sum H_n^2|a_n|^2<\infty\right\}.
\]
Its associated closed form is
\[
 \mathfrak j[f]=\sum_{n\ge0}H_n|a_n|^2,\qquad
 D(\mathfrak j)=D(J^{1/2})
      =\left\{f=\sum a_ne_n:\sum H_n|a_n|^2<\infty\right\}.
\]
The equality with the displayed double-integral jump form holds first on polynomials: Tuck's identity (R-0032/0033, C-0045) is
\[
 \int_{-1}^{1}\frac{P_n(x)-P_n(y)}{|x-y|}\,dy=2H_nP_n(x).
\]
Symmetrization and polarization give
\(\mathfrak j[P_m,P_n]=H_n d_n\delta_{mn}\), fixing the factor \(1/4\), with no extra \(T\)-dependent factor.

The spectral and integral forms also agree on \(H^1(-1,1)\): for \(h\in H^1\), Cauchy–Schwarz gives
\(|h(x)-h(y)|^2/|x-y|\le\|h'\|_2^2\); hence the jump form is continuous under \(H^1\) approximation. Polynomial density in \(H^1\), combined with equality for polynomials and closedness of the spectral form, establishes equality for \(H^1\) functions. In particular \(H^1_0(-1,1)\) is included in \(D(\mathfrak j)\).

For every \(N\ge1\), the \(J\) part is exactly diagonal across the Legendre low/tail split; it has **no cross term**, and for \(q\perp E_N\),
\[
 \mathfrak j[q]\ge H_N\|q\|^2.
\]
This is a closed-form inequality, not an assertion that every \(q\in H\) belongs to the unbounded operator domain of \(J\).

## 3. The positive, unbounded endpoint multiplier

Since \(v(x)=-\frac12\log(1-x^2)\), it is nonnegative and belongs to \(L^p(-1,1)\) for every finite \(p\), including \(L^1\) and \(L^2\), but \(v\notin L^\infty\).

Precisely,
\[
 \begin{split}
 D(V)&=\{f\in H:vf\in H\},\\
 D(\mathfrak v)=D(V^{1/2})
     &=\left\{f\in H:\int_{-1}^{1}v|f|^2<\infty\right\},\\
 \mathfrak v[f,g]&=\int_{-1}^{1}v(x)\overline{f(x)}g(x)\,dx.
 \end{split}
\]
The multiplication operator \(V\) is nonnegative self-adjoint and its form is closed. Every polynomial \(u\) is bounded on the compact interval, so \(vu\in L^2\); more generally \(v^ku\in L^2\) for any fixed integer \(k\). In particular **every low Legendre vector belongs to \(D(V)\)**. This is the decisive reason \(Q_NV|_{E_N}\) exists as an \(H\)-valued map despite the global unboundedness of \(V\).

Because \(H^1(-1,1)\hookrightarrow L^\infty(-1,1)\), its functions lie in \(D(\mathfrak v)\); no false global bound of \(V\) is used.

## 4. Finite, bounded, self-adjoint arithmetic operator

For each active prime power \(m=p^k\), define
\[
 \mathcal A(T)=\{m=p^k:\log m<2T\},\quad
 \tau_m=\frac{\log m}{T},\quad
 c_m=\frac{\Lambda(m)}{\sqrt m}>0.
\]
For \(0<\tau<2\), define the zero-extended compressed *two-sided* shift on \(H\):
\[
 (S_\tau f)(x)
  ={\bf1}_{(-1,1)}(x+\tau)f(x+\tau)
   +{\bf1}_{(-1,1)}(x-\tau)f(x-\tau)
 \quad\text{for a.e. }x\in(-1,1).
\]
The two terms are adjoints, and each compression has norm at most \(1\). Therefore \(S_\tau=S_\tau^*\) and \(\|S_\tau\|\le2\) without any domain restriction. The exact path-chain norm in C-0040 is a sharper result when its hypotheses are met.

The combined signed arithmetic operator is
\[
                     P_T=-\sum_{m\in\mathcal A(T)}c_mS_{\tau_m}.
\]
There are finitely many active prime powers for finite \(T\), so \(P_T\) is an **everywhere-defined bounded self-adjoint operator on \(H\)**. Its quadratic form is exactly the signed sum of both translated overlaps. In the strict first multi-prime window, \(\mathcal A(T)=\{2,3\}\) and \(P_T=P_2+P_3\), with no missing factor of two or independently invented \(G_2+G_3\) representation.

## 5. The **full** Suzuki residual is bounded on this support range

Let \(r''_{\rm even}(u)\) denote the canonical *even*, real residual second derivative, represented for \(u\ge0\) by the positive-side Suzuki series used in `scripts/cert/residual_kernel.py`. For \(2T<\pi\), its Taylor/Bernoulli representation and existing rigorous remainder bound establish a finite bound
\[
 M_T=\sup_{0\le u\le2T}|r''_{\rm even}(u)|<\infty.
\]
The **full** residual operator is
\[
 (R_Tf)(x)=-T\int_{-1}^{1}
        r''_{\rm even}(T|x-y|)\,f(y)\,dy.
\]
The kernel is real, symmetric, and bounded on \((-1,1)^2\). It therefore defines a Hilbert–Schmidt, hence bounded, self-adjoint operator on \(H\). Direct Schur/Hilbert–Schmidt estimation yields
\[
                    \|R_T\|\le 2TM_T=:\rho_R.
\]
The operator is defined for **all** \(f\in H\); therefore \(Q_NR_T|_{E_N}\) is unconditionally well-defined.

A Taylor truncation \(R_{T,K}\) in the current implementation is *not* this full operator. The existing norm estimate
\[
 \|R_T-R_{T,K}\|\le\delta_R
\]
comes from bounding the full omitted kernel by its uniformly bounded series tail, with \(\delta_R=2T\cdot \mathrm{tailRadius}(2T,K)\). Retaining this remainder is essential. In the \(\{2,3\}\) window, \(2T<2\log2<\pi\), so the required residual analyticity/boundedness condition holds. This proof does not assert the same Taylor representation for unrestricted \(T\ge\pi/2\).

## 6. The closed form and its associated operator

Define
\[
 \mathcal F_T=D(J^{1/2})\cap D(V^{1/2}),\qquad
 \mathfrak l_T=\mathfrak j+\mathfrak v
                 +\langle\cdot,(P_T+R_T-c_TI)\cdot\rangle
 \quad\text{on }\mathcal F_T.
\]
The intersection contains all polynomials, so it is dense in \(H\). The sum \(\mathfrak j+\mathfrak v\) is nonnegative and **closed**: the norm
\[
 \|f\|_{\mathcal F}^2
    =\|f\|_2^2+\mathfrak j[f]+\mathfrak v[f]
\]
is complete because Cauchy sequences converge separately in the two nonnegative closed form norms and have the same \(L^2\) limit. The remaining arithmetic, residual, and scalar contributions are **bounded symmetric form perturbations**. Thus \(\mathfrak l_T\) is densely defined, closed, symmetric and lower semibounded. By the first representation theorem it has a unique associated lower-semibounded self-adjoint operator \(L_T^{\rm form}\).

The displayed equation \(L_T=J-c_TI+V+P_T+R_T\) is therefore interpreted **as a form sum** on \(\mathcal F_T\). We do not silently assert that the naive unbounded operator sum on \(D(J)\cap D(V)\) is already self-adjoint with the same full operator domain.

Every polynomial \(u\) belongs to \(D(J)\cap D(V)\subset D(L_T^{\rm form})\), and for such \(u\)
\[
 L_T^{\rm form}u=Ju-c_Tu+Vu+P_Tu+R_Tu
 \quad\text{as an identity in }H.
\]
Indeed for every \(f\in\mathcal F_T\) its form pairing with \(u\) is represented by the displayed \(L^2\) vector. This is the operator-domain justification for evaluating the low-mode columns.

The closed-form extension agrees with the repository's Suzuki form on \(H^1_0(-1,1)\), which is included in \(\mathcal F_T\) by §§2–3, with bounded \(P_T,R_T\). No reverse assertion that the *original source's test-function domain* equals \(\mathcal F_T\), nor that it is a form core, is needed or established here. Positivity on this larger form domain would imply positivity on its original admissible subspace, but no such positivity is asserted in SYS-2.1.

## 7. Projections, exact low/tail maps, and cross terms

For \(N\ge1\) define
\[
 E_N=\operatorname{span}\{P_0,\ldots,P_{N-1}\},\qquad
 \Pi_Nf=\sum_{n=0}^{N-1}\langle e_n,f\rangle e_n,\qquad
 Q_N=I-\Pi_N.
\]
These are bounded orthogonal projections, with \(\Pi_N^*=\Pi_N\), \(Q_N^*=Q_N\) and \(\Pi_NQ_N=0\). In the **unnormalized** polynomial basis,
\[
 \Pi_Nf=\sum_{n=0}^{N-1}\frac{\langle P_n,f\rangle}{d_n}\,P_n.
\]
Because every polynomial lies in \(\mathcal F_T\), both \(\Pi_N\) and \(Q_N\) preserve \(\mathcal F_T\): if \(f\in\mathcal F_T\) then \(\Pi_Nf\in\mathcal F_T\), hence \(Q_Nf=f-\Pi_Nf\in\mathcal F_T\).

For \(X\in\{V,P_T,R_T\}\), define
\[
 B_{X,N}: E_N\longrightarrow Q_NH,\qquad
 B_{X,N}u=Q_NXu.
\]
These maps are **bounded**: each \(Xu\) exists in \(H\) by §§3–5, and \(E_N\) is finite dimensional. In particular \(B_{V,N}\) is bounded **only as a map with finite-dimensional domain**, not as a global bound on \(V:H\to H\). Their Hilbert-space adjoints
\(B_{X,N}^*:Q_NH\to E_N\) therefore also exist and are bounded.

For \(u\in E_N\) and \(q\in Q_N\mathcal F_T\), the off-diagonal form is exactly
\[
 \mathfrak l_T[u,q]
   =\langle Vu+P_Tu+R_Tu,q\rangle
   =\langle (B_{V,N}+B_{P,N}+B_{R,N})u,q\rangle,
\]
up to the harmless convention for which argument of the complex inner product is linear. The **\(J\)** cross term is zero because \(J\) is diagonal in the Legendre basis, and the **\(-c_TI\)** cross term is zero by orthogonality.

The corresponding exact low form has entries
\[
 A_{ij}^{\rm exact}=\mathfrak l_T[P_i,P_j]
  =d_i(H_i-c_T)\delta_{ij}
     +\langle P_i,VP_j\rangle
     +\langle P_i,P_TP_j\rangle
     +\langle P_i,R_TP_j\rangle.
\]
There is no unbounded-block ambiguity in this finite matrix.

The tail form is the restriction of \(\mathfrak l_T\) to \(Q_N\mathcal F_T\), not an assertion that an everywhere-defined matrix \(Q_NL_TQ_N\) exists on all \(Q_NH\). For \(q\in Q_N\mathcal F_T\), §§2–5 give
\[
 \mathfrak l_T[q]\ge
 \underbrace{\bigl(H_N-c_T-\sum_{m\in\mathcal A(T)}c_m b_m-\rho_R\bigr)}_{\mu_N}
 \|q\|^2,
 \qquad b_m\ge\|S_{\tau_m}\|.
\]
This recovers the already established C-0058 lower-bound *form* semantics. A strict positive complement follows only when \(\mu_N>0\); SYS-2.1 does not assert that inequality at a new support/dimension.

Finally, each \(B_{X,N}^*B_{X,N}\) is a well-defined finite-rank positive semidefinite operator on \(E_N\), with matrix elements
\[
 \langle B_{X,N}P_i,B_{X,N}P_j\rangle
 =\langle Q_NXP_i,Q_NXP_j\rangle.
\]
This is the **domain-safe definition** of a component tail Gram. Writing \(\Pi_NXQ_NX\Pi_N\) or a full operator-square identity is shorthand only when the relevant compositions are separately well-defined; such shorthand is unnecessary to establish the low-to-tail maps. No mixed \(V/P/R\) Gram expression is calculated or tested in this step.

**Important generator distinction:** `assemble_multi_prime_schur()` returns a rigorous *lower enclosure* for the low matrix `A`, with \(-\delta_R D_N\) included for the residual truncation, and the conservative *upper* residual Gram `GR=2GR_K+2\delta_R^2 D_N`. Those are valid enclosure objects under their recorded error assumptions; neither is automatically equal to the exact \(A_N^{\rm exact}\) or to the exact \(B_{R,N}^*B_{R,N}\). The source implementation uses the unnormalized Gram factors \(D_N^{-1}\) for low-mode projections.

## 8. Proof checks, assumptions, and precise result

**Mathematical checks performed in this record:**

1. Tuck identity plus polarization fixes \(\mathfrak j[P_m,P_n]=H_nd_n\delta_{mn}\).
2. \(\log^p\)-integrability for every finite \(p\) proves \(P_n\in D(V)\), despite unbounded \(V\).
3. Each compressed shift is the sum of mutually adjoint \(L^2\)-bounded translations, and the active sum is finite.
4. Suzuki's **full** residual kernel is bounded and symmetric for \(2T<\pi\); the Schur estimate is \(2TM_T\), not a bound on a truncated kernel alone.
5. Two nonnegative closed forms plus bounded self-adjoint perturbations produce the closed semibounded form and its associated operator.
6. \(\Pi_N,Q_N\) preserve the form domain; finite-dimensional operator-domain inclusion makes all three \(B_{X,N}\) and their adjoints exist.
7. Orthogonality removes the jump/scalar low–tail cross components, leaving exactly \(V,P_T,R_T\).
8. The exact low block and the generator's conservative enclosed low block are explicitly distinguished.
9. The proof makes no unverified claim about self-adjointness of the naive sum, equality of the original source/test domain with the closed-form domain, positivity of a new Gram, or an admitted v2 theorem.

**Inputs not independently reproved here:** Suzuki's equality between the original Weil functional and its scaled form (R-0028); Tuck's classical Legendre identity (R-0032/0033); and the existing analytic Bernoulli/Taylor expression for the full residual in \(|u|<\pi\) (`scripts/cert/residual_kernel.py`). Their statements and normalizations were checked against maintained source derivations and the present implementation. This is a **paper-level derivation**, not a newly executed Lean formal proof or external-paper recompilation.

**Status: SYS-2.1 COMPLETE.** The exact low-to-tail maps are mathematically well-defined in the stated setting. Nothing in this finding asserts that the resulting combined sufficient matrix is positive, that the current v2 negative witnesses disappear, or that RH has been resolved.

## Source and evidence map

- Source normalization / admissible scaled form: R-0028; `attempts/2026-08-21T040654Z-first-prime-weil-support-continuation.md`, `attempts/2026-08-21T085252Z-exact-prime-legendre-schur-certificate.md`.
- Legendre jump coercivity: C-0045, F-20260821-016, R-0032/0033.
- Existing complement and grouped arithmetic: C-0058/0059; `docs/MULTI_PRIME_CONTRACT.md`.
- Unbounded potential and its first/second moments: `scripts/cert/legendre_schur.py::potential_matrices`; `scripts/cert/multi_prime_legendre_schur.py::_potential_matrices`.
- Shift activity and combined signed arithmetic: `scripts/cert/prime_power_terms.py`.
- Full Suzuki residual, series and remainder: `scripts/cert/residual_kernel.py`; `scripts/cert/multi_prime_legendre_schur.py::_residual_truncation_operator`, `_residual_rho`.
- Rigorous low blocks and Gram *enclosures*: `scripts/cert/multi_prime_legendre_schur.py::assemble_multi_prime_schur`.
