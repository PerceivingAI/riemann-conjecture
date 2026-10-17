# SYS-2.3 — Exact mixed low-to-tail Gram identities in the scaled Legendre basis

- **Finding ID:** F-20261017-003
- **Created:** 2026-10-17T12:18:09Z
- **Last updated:** 2026-10-17T12:21:05Z
- **Type:** DERIVED_RESULT
- **Status:** VERIFIED — paper-level operator-image and finite-matrix algebra under the stated SYS-2.1/SYS-2.2 assumptions; not a new Lean theorem or numerical positivity result
- **Claim:** C-0065
- **Inspected source revision:** `fcf4353adaf090480b695cf089bf9f17f5ad9f04` (prior SYS-2.1 and SYS-2.2 records were already uncommitted in the working tree)
- **Scope:** Exact mathematical identities and the rigorously stated *full residual versus truncated residual* error relations. No implementation, finite-support positivity claim, or certificate admission.

## 1. Why this remains necessary after SYS-2.2

SYS-2.2 / `C-0064` proves that strict positivity of \(A_N-\mu_N^{-1}B^*B\), given a positive full-tail form bound, would suffice for positivity of the localized Weil form. It **does not** supply the entries of \(B^*B\). In particular the existing `GV+GP+GR` output consists of *separately bounded* component tail Grams and cannot be substituted for the combined one. SYS-2.3 derives the full exact mixed-Gram identity with the repository's **unnormalized** Legendre basis and quantifies the mathematical effect of replacing the full Suzuki residual by its truncated kernel.

## 2. Domains, images and matrix normalization

Fix \(N\ge1\), \(0<T<\pi/2\), and the SYS-2.1 Hilbert space \(H=L^2((-1,1),dx;\mathbb C)\). The immediate prime-power application is the strict \(\{\!2,3\!\}\) window \(\tfrac12\log3<T<\log2\). Use the ordinary Legendre polynomials
\[
 \ell_i=P_i,\qquad
 d_i=\|\ell_i\|_H^2=\frac2{2i+1},\qquad
 D_N=\operatorname{diag}(d_0,\ldots,d_{N-1}).
\]
Write \(E_N=\operatorname{span}\{\ell_0,\ldots,\ell_{N-1}\}\), \(\Pi=\Pi_N\), \(Q=I-\Pi\).

The symbol \(\mathsf P\) denotes the **combined signed arithmetic operator** \(P_T\), never the Legendre polynomial \(P_i\). Let \(R\) mean the **full** Suzuki residual \(R_T\) and \(V\) the logarithmic potential multiplication operator. Define \(W=V+\mathsf P+R\) on \(D(V)\), and for every \(i<N\) define the actual \(L^2\) images
\[
  v_i=V\ell_i,\quad p_i=\mathsf P\ell_i,\quad r_i=R\ell_i,
  \quad w_i=v_i+p_i+r_i=W\ell_i.
  \tag{2.1}
\]
These are legitimate \(L^2\) vectors: \(\ell_i\in D(V)\) by \(v(x)\in L^2\) and boundedness of polynomials; \(\mathsf P\) is bounded; and the **full** \(R\) is bounded. In particular, no assumption \(\ell_i\in D(W^2)\) is required.

The low-to-tail operator is \(B=QW|_{E_N}\). Its exact coordinate Gram in the *unnormalized Legendre basis* is
\[
   (G_{\rm all})_{ij}
      =\langle Qw_i,Qw_j\rangle,\qquad 0\le i,j<N.
   \tag{2.2}
\]
This is the finite coordinate matrix of the bounded positive semidefinite operator \(B^*B\) on the low Hilbert space. It is **not** the orthonormal-basis representation of that operator; the corresponding orthonormal matrix is \(D_N^{-1/2}G_{\rm all}D_N^{-1/2}\).

## 3. Projection identity without unbounded operator squares

For \(X,Y\in\{V,\mathsf P,R\}\) define
\[
 (K_X)_{ij}=\langle \ell_i,X\ell_j\rangle,\qquad
 (M_{XY})_{ij}=\langle X\ell_i,Y\ell_j\rangle,
 \tag{3.1}
\]
where the inner product is conjugate linear in its first argument. Every entry is finite by §2. Self-adjointness of the three individual operators gives \(K_X=K_X^*\), and \(M_{YX}=M_{XY}^*\).

Since \(\{\ell_k\}_{k<N}\) is orthogonal but **not normalized**,
\[
 \Pi f=\sum_{k<N}\ell_k\frac{\langle\ell_k,f\rangle}{d_k}.
\]
Therefore for every \(i,j<N\),
\[
\begin{aligned}
 \langle QX\ell_i,QY\ell_j\rangle
 &=\langle X\ell_i,Y\ell_j\rangle
       -\langle\Pi X\ell_i,\Pi Y\ell_j\rangle\\
 &=(M_{XY})_{ij}
       -(K_XD_N^{-1}K_Y)_{ij}.
\end{aligned}
\tag{3.2}
\]
No term \(\langle \ell_i,XY\ell_j\rangle\), \(\Pi XY\Pi\), or \(W^2\) has been assumed to be defined. Equation (3.2) follows solely from the **images of the finite low basis vectors** and orthogonal projection.

Define
\[
 K=K_V+K_{\mathsf P}+K_R,\qquad
 M=\sum_{X,Y\in\{V,\mathsf P,R\}}M_{XY}.
\]
Then the full exact matrix identity is
\[
 \boxed{\displaystyle
 G_{\rm all}=M-KD_N^{-1}K.
 }
 \tag{3.3}
\]
Here \(M_{ij}=\langle w_i,w_j\rangle\), not ordinary multiplication of the low matrix \(K\). In particular the subtraction is **\(KD_N^{-1}K\)**, never \(K^2\) without the nonorthonormal-basis Gram factor. Formula (3.3) yields a Hermitian positive semidefinite matrix because it is exactly (2.2), regardless of the signs of its individual off-diagonal mixed pieces.

## 4. All nine \(V/\mathsf P/R\) contributions, including all six ordered mixed terms

The full image Gram in (3.3) contains **nine** ordered terms:
\[
\begin{aligned}
 M={}&M_{VV}+M_{\mathsf P\mathsf P}+M_{RR}\\
    &+M_{V\mathsf P}+M_{\mathsf P V}\\
    &+M_{VR}+M_{RV}\\
    &+M_{\mathsf PR}+M_{R\mathsf P}.
\end{aligned}
\tag{4.1}
\]
The low subtraction expands into precisely the corresponding **nine** products \(K_XD_N^{-1}K_Y\). Define component Grams
\[
 G_X=M_{XX}-K_XD_N^{-1}K_X
\]
and, for each unordered pair \(X\ne Y\), the **Hermitian mixed low-tail Gram**
\[
 \mathcal C_{XY}
   :=M_{XY}+M_{YX}
       -K_XD_N^{-1}K_Y-K_YD_N^{-1}K_X.
 \tag{4.2}
\]
Thus, exactly,
\[
 \boxed{\displaystyle
 G_{\rm all}
  =G_V+G_{\mathsf P}+G_R
       +\mathcal C_{V\mathsf P}
       +\mathcal C_{VR}
       +\mathcal C_{\mathsf PR}.}
 \tag{4.3}
\]
These mixed matrices are individually Hermitian but **not necessarily positive semidefinite**; setting them to zero is an unjustified modification of the combined criterion. The combined sum remains positive semidefinite as the Gram of \(Qw_i\).

To exhibit the actual analytic integrals, put
\[
 v(x)=-\tfrac12\log(1-x^2),\qquad
 s_m[\ell_i](x)
  ={\bf1}_I(x+\tau_m)\ell_i(x+\tau_m)
    +{\bf1}_I(x-\tau_m)\ell_i(x-\tau_m),\quad I=(-1,1),
\]
with \(\tau_m=\log(m)/T\), \(c_m=\Lambda(m)/\sqrt m\), so
\[
 v_i(x)=v(x)\ell_i(x),\qquad
 p_i(x)=-\sum_{m\in\mathcal A(T)}c_m s_m[\ell_i](x),\qquad
 r_i(x)=-T\int_I r''_{\rm even}(T|x-y|)\ell_i(y)\,dy.
 \tag{4.4}
\]
The three unordered cross terms in (4.2) use the following actual image pairings, plus their adjoints:
\[
\begin{aligned}
 (M_{V\mathsf P})_{ij}&=\int_I\overline{v_i(x)}p_j(x)\,dx,\\
 (M_{VR})_{ij}&=\int_I\overline{v_i(x)}r_j(x)\,dx,\\
 (M_{\mathsf PR})_{ij}&=\int_I\overline{p_i(x)}r_j(x)\,dx.
\end{aligned}
\tag{4.5}
\]
The individual diagonal terms are \(M_{VV,ij}=\int_I\overline{v_i}v_j\), \(M_{\mathsf P\mathsf P,ij}=\int_I\overline{p_i}p_j\), and \(M_{RR,ij}=\int_I\overline{r_i}r_j\).

Every integral in (4.5) exists absolutely: \(v_i\in L^2\), each piecewise-shift image \(p_i\in L^2\) (indeed it is essentially bounded for fixed polynomial input), and the full residual image \(r_i\in L^2\) (indeed bounded in this finite support regime). Cauchy–Schwarz applies without any unproved commutation or additional operator domain assumption.

The formula (4.5) is a **mathematical representation**, not a claim that the current v2 assembler already computes these six new ordered mixed entries or encloses their numerical values.

## 5. Mixed prime-power terms are already inside the one combined \(\mathsf P\) block

With \(\mathsf P=\sum_{m\in\mathcal A(T)}\mathsf P_m\), \(\mathsf P_m=-c_mS_{\tau_m}\), write \(p_{m,i}=\mathsf P_m\ell_i=-c_ms_m[\ell_i]\). Then
\[
 (M_{\mathsf P\mathsf P})_{ij}
 =\sum_{m,n\in\mathcal A(T)}
      \langle p_{m,i},p_{n,j}\rangle,\qquad
 K_{\mathsf P}=\sum_m K_{\mathsf P_m}.
 \tag{5.1}
\]
Consequently
\[
 G_{\mathsf P}
 =\sum_{m,n\in\mathcal A(T)}
  \bigl(M_{\mathsf P_m\mathsf P_n}
           -K_{\mathsf P_m}D_N^{-1}K_{\mathsf P_n}\bigr).
 \tag{5.2}
\]
In the first \(\{2,3\}\) window the mixed arithmetic contribution, in addition to the individual \(m=2\) and \(m=3\) terms, is exactly
\[
\begin{aligned}
 \mathcal C_{23}
 ={}&c_2c_3\bigl[
   \langle S_{\tau_2}\ell_i,S_{\tau_3}\ell_j\rangle
  +\langle S_{\tau_3}\ell_i,S_{\tau_2}\ell_j\rangle
  \bigr]_{ij}\\
 &-K_{\mathsf P_2}D_N^{-1}K_{\mathsf P_3}
  -K_{\mathsf P_3}D_N^{-1}K_{\mathsf P_2}.
\end{aligned}
\tag{5.3}
\]
All negative signs of \(\mathsf P_m=-c_mS_{\tau_m}\) are included in the low \(K_{\mathsf P_m}\) matrices; the full-image pair has positive \(c_mc_n\). It is generally false that \(G_{\mathsf P}=G_{\mathsf P_2}+G_{\mathsf P_3}\). The existing `scripts/cert/prime_power_terms.py` already combines the piecewise images **before** forming its arithmetic square/Gram, and `tests/test_prime_power_terms.py::test_combined_square_contains_nonzero_two_prime_cross_terms` confirms a nonzero combined operator-square cross contribution.

The \(V/\mathsf P\) and \(\mathsf P/R\) terms of (4.2) use **that same total** \(\mathsf P\), so they also include each active \(m\). No additional prime-indexed Schur components are introduced.

## 6. Reflection parity and legitimate exact zeros

The reflection \((\mathcal Rf)(x)=f(-x)\) has \(\mathcal R\ell_i=(-1)^i\ell_i\). The multiplication \(V\) is even, the symmetric compressed shifts \(S_{\tau_m}\) commute with reflection, and the **full** Suzuki residual kernel \(r''_{\rm even}(T|x-y|)\) is reflection-invariant under \((x,y)\mapsto(-x,-y)\). Thus \(V,\mathsf P,R,\Pi,Q\) preserve Legendre parity on the relevant low-mode images.

It follows that every \(K_X\), \(M_{XY}\), \(G_X\), \(\mathcal C_{XY}\), and \(G_{\rm all}\) has **exact zero entries between modes of opposite parity**. This is a justified symmetry zero, not an omission of a within-parity \(V/\mathsf P/R\) or \(2/3\) cross term. No positivity of an even or odd block is inferred.

## 7. Full Suzuki residual versus truncated polynomial kernel

The existing code uses the exact rational polynomial truncation \(R_K\) of the **positive-side** residual series and a rigorous full-operator remainder estimate
\[
   R=R_K+E_K,\qquad
   \|E_K\|_{H\to H}\le\delta_K
      :=2T\,\mathrm{tailRadius}(2T,K).
   \tag{7.1}
\]
This is a source-dependent analytical bound in \(|u|<\pi\), verified as the current contract's residual error, not newly proved by an independent numerical run. \(R_K\) is bounded and self-adjoint; \(E_K\) is bounded and self-adjoint.

Define the truncated-image surrogate
\[
 W_K=V+\mathsf P+R_K,\quad
 B_K=QW_K|_{E_N},\quad
 \Delta B=QE_K|_{E_N}.
\]
Then \(B=B_K+\Delta B\) and \(\|\Delta B\|\le\delta_K\). The **exact full residual correction** to the combined Gram is
\[
 \boxed{\displaystyle
 G_{\rm all} =
    B_K^*B_K
   +B_K^*\Delta B+\Delta B^*B_K+\Delta B^*\Delta B.}
 \tag{7.2}
\]
The two cross terms in (7.2) contain mixed \(E_K\) interactions with **all** of \(V,\mathsf P,R_K\); omitting them or setting \(R=R_K\) is invalid.

Since \(B_K\) is bounded on finite \(E_N\), the full-minus-truncated Gram satisfies the operator-norm inequality
\[
 \boxed{\displaystyle
   \|G_{\rm all}-B_K^*B_K\|
      \le2\|B_K\|\delta_K+\delta_K^2.}
 \tag{7.3}
\]
Equivalently, if \(\varepsilon_K=2\|B_K\|\delta_K+\delta_K^2\),
\[
 -\varepsilon_K I_{E_N}
 \preceq G_{\rm all}-B_K^*B_K
 \preceq\varepsilon_K I_{E_N}.
 \tag{7.4}
\]
For every **arbitrary** \(\eta>0\), the Hilbert-space Young inequality also gives the norm-free, conservative Gram upper bound
\[
 \boxed{\displaystyle
 G_{\rm all}\preceq
 (1+\eta)B_K^*B_K+(1+\eta^{-1})\delta_K^2 I_{E_N}.}
 \tag{7.5}
\]
These are exact **analytic inequalities**, not claims that an executable enclosure for \(B_K^*B_K\), all mixed moments, or a certified \(\|B_K\|\) is already available.

The low block has a separate, simpler remainder estimate. Define the exact unnormalized low-form matrices
\[
 (A_{\rm full})_{ij}
 =d_i(H_i-c_T)\delta_{ij}
   +(K_V+K_{\mathsf P}+K_R)_{ij},
\]
\[
 (A_K)_{ij}
 =d_i(H_i-c_T)\delta_{ij}
   +(K_V+K_{\mathsf P}+K_{R_K})_{ij}.
\]
Since \(\|\Pi E_K|_{E_N}\|\le\delta_K\), their **coordinate** quadratic forms satisfy
\[
        -\delta_KD_N\preceq A_{\rm full}-A_K
                  \preceq\delta_KD_N.
 \tag{7.6}
\]
Likewise, (7.4) in the **unnormalized** Legendre matrix representation reads
\[
-\varepsilon_KD_N
 \preceq G_{\rm all}^{\rm(coord)}-G_K^{\rm(coord)}
 \preceq\varepsilon_KD_N.
 \tag{7.7}
\]
The multiplication by \(D_N\) is essential when converting Hilbert-operator bounds to the repository's coordinate matrices.

**Difference from current implementation:** `scripts/cert/multi_prime_legendre_schur.py::assemble_multi_prime_schur` already uses \(A_K-\delta_KD_N\) as a valid lower low-form bound, but computes separate `GV`, `GP`, and the safe old-factor bound `GR=2GR_K+2\delta_K^2D_N`. Those outputs **do not comprise** the full combined Gram \(G_{\rm all}\) and cannot recover its \(V/\mathsf P\), \(V/R\), or \(\mathsf P/R\) cross matrices merely by relabeling or summing. This finding does not change their semantics.

## 8. Representability and what has actually been verified

The exact new Gram is mathematically a *finite* matrix of \(L^2\) image inner products. The integrands are fully specified by (4.4), including both compressed-shift directions, the correct von Mangoldt coefficients, full residual kernel, and endpoint logarithm. They are integrable by §4, and all projection subtractions are explicitly \(D_N^{-1}\)-weighted.

Current code provides separately: rigorous \(V\) first/second moments; combined \(\mathsf P\) piecewise polynomial images and full arithmetic inner products (with cross prime powers); \(R_K\) exact polynomial images and an operator-norm remainder. **The reviewed implementation does not assemble or certify the three new mixed \(V/\mathsf P/R\) pairings** from (4.5). The algebraic representation is therefore proved, but no claim of a fully evaluated or Arb-enclosed combined Gram follows. Whether these newly specified integrals can be evaluated rigorously at a given support/precision is not decided by the identity alone.

**Exact-rational algebra check (independent of the analytic kernels):** A separate ephemeral `fractions.Fraction` calculation represented a 2-dimensional low space and 2-dimensional tail with Legendre diagonal norms \(2,2/3,2/5,2/7\). With four nonzero components \(V,\mathsf P_2,\mathsf P_3,R\), it compared the direct tail-vector Gram, \(M-KD_N^{-1}K\), and expansion across all 16 ordered component pairs. All agreed exactly; all three mixed \(V/\mathsf P/R\) pair groups and the \(\mathsf P_2/\mathsf P_3\) pair were nonzero. This is an algebra/normalization sanity check **only**, not an Arb enclosure, exact Suzuki-kernel evaluation, or positivity test.

## 9. Proof status, assumptions and nonclaims

**Proved conditional on established SYS-2.1:** domain-safe exact Gram identity (3.3), complete nine-term grouped expansion (4.1)–(4.3), exact mixed \(2/3\) arithmetic term (5.3), reflection-parity zeros, and full-residual remainder identities/bounds (7.2)–(7.7). The derivation uses only \(L^2\) image pairings of finite low Legendre modes; no unsupported squared-operator domain assumption is needed.

**Analytical inputs cited, not reproved here:** Suzuki's scaled Weil and canonical full residual formula (R-0028); Tuck's Legendre normalization (R-0032/0033); and the rigorous bound on the truncated residual operator error from `scripts/cert/residual_kernel.py`.

**Not established or performed:** no numerical evaluation of new \(V/\mathsf P/R\) mixed moments, no rigorous enclosure of an actual \(G_{\rm all}\) at \(T=11/20\) or another support, no positive combined Schur matrix, no v2 certificate exporter/verifier modification, no historical change, no theorem-admission decision, no Lean proof, and no progress claim about full RH.

**SYS-2.3 conclusion: COMPLETE as an exact mathematical derivation.** The combined Gram is finite, well-defined and has the explicit images-and-projection matrix formula; it is not yet a computationally qualified positivity result.

## Sources

- [SYS-2.1 domain finding](2026-10-17T115900Z-scaled-weil-operator-domain-and-low-tail-maps.md), claim C-0063.
- [SYS-2.2 form-Schur theorem](2026-10-17T121100Z-combined-cross-block-form-schur-criterion.md), claim C-0064.
- [Frozen multi-prime mathematical contract](../docs/MULTI_PRIME_CONTRACT.md), claims C-0058/C-0059.
- [Current combined prime-power operator](../scripts/cert/prime_power_terms.py) and [current v2 Schur assembler](../scripts/cert/multi_prime_legendre_schur.py).
- [Full Suzuki residual series and remainder](../scripts/cert/residual_kernel.py).
- [Exact source normalization reference R-0028](../references/BIBLIOGRAPHY.md).
