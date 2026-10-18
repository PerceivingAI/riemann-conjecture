# Finite-support combined-Schur theorem: mathematical proof obligations and independent analytic gate

- **Finding ID:** F-20261017-014
- **Created:** 2026-10-17T21:41:29Z
- **Last updated:** 2026-10-17T22:02:54Z
- **Type:** MATHEMATICAL_PROOF_OBLIGATION_AUDIT / bounded analytical source review and exact identity tests
- **Status:** **SCOPED MATHEMATICAL IDENTITIES VERIFIED; INDEPENDENT ALL-ENTRY ENCLOSURE GATE NOT YET CLOSED. PRE-THEOREM ONLY.**
- **Underlying positive research candidate:** [F-20261017-013](2026-10-17T153741Z-bounded-combined-schur-experiment-closure.md), `T=11/20,N=192`.
- **Independent control:** [X-20261017-005](../computations/2026-10-17T214044Z-sys5-analytic-proof-audit/record.md).
- **Repository baseline:** `bae1b975abc053f6aba12972621b540110b9b2f9`. No change to existing certificate profiles, admitted mathematical claims, Rust, Lean, or historical experimental artifacts.

## 1. Exact potential finite-support theorem statement

Let \(T=11/20\), \(H=L^2(-1,1)\), and denote by \(U_T:L^2(-T,T)\to H\) the unitary map \((U_Tf)(x)=\sqrt T f(Tx)\). Let \(Q_W\) be Weil's localized quadratic form on \(C_c^\infty(-T,T)\). For the constructed lower-semibounded closed form \(\mathfrak l_T\) of C-0063, source identity (Suzuki, eqs. (2.5), (4.4)–(4.5)) gives
\[
 Q_W(f)=\mathfrak l_T[U_Tf]\qquad(f\in C_c^\infty(-T,T)).
\]
The relevant **potential theorem** is:

> There exists \(\varepsilon_T>0\) such that \(Q_W(f)\ge\varepsilon_T\|f\|_{L^2(-T,T)}^2\) for every \(f\in C_c^\infty(-T,T)\), in the stated Suzuki normalization.

The theorem concerns **one exact finite support** only; it does not claim RH, positivity at every support, or equality of the entire constructed form/operator domain with the canonical Friedrichs-extension domain. Agreement with Suzuki's expression on the source Sobolev/test class plus the inclusion \(C_c^\infty\subset H_0^1\subset\mathcal F_T\) is enough to transfer positivity *if* the source matrix bounds are fully certified. The equality above is for the normalized form, not a claim about an unbounded operator acting on all \(H\).

## 2. Closed mathematical implication: what would prove the stated theorem

In ordinary **unnormalized** Legendre coordinates \(d_i=2/(2i+1)\), \(D_N=\operatorname{diag}(d_i)\), \(N=192\), \(Q_N=I-\Pi_N\), let \(W=V+P_T+R_T\), \(B=Q_NW\vert_{E_N}\). Define the exact low form \(A_N\), the certified full complementary bound \(\mu_N>0\), and \(G=B^*B\succeq0\). The operator/form arguments in C-0063–C-0065 give
\[
 \mathfrak l_T[u+q]\ge
 \langle u,(A_N-\mu_N^{-1}G)u\rangle+
 \mu_N\|q+\mu_N^{-1}Bu\|^2,
 \quad u\in E_N,\;q\in Q_N\mathcal F_T.
\]
Thus a **strictly positive lower matrix** \(S_{\rm low}\preceq A_N-\mu_N^{-1}G\) implies strict coercivity for all \(u+q\in\mathcal F_T\) and then for every admissible smooth test. The matrix-order direction matters; negativity of \(S_{\rm low}\) would be inconclusive. The existing packet's independently computed exact rational congruence/Gershgorin witness for \(S_{\rm low}\) was previously verified; the **mathematical remaining burden** is proving the supplied rational endpoints enclose all their purported analytical entries.

## 3. Source-side mathematical formulas reviewed

The source is Masatoshi Suzuki, *Weil's quadratic form via the screw function*, [arXiv:2606.09096v3 (2026-09-23)](https://arxiv.org/html/2606.09096v3), especially (2.2), (2.5), and (4.4)–(4.5). The previously established source-domain proof F-20261017-001 and independent audit F-20261017-004 establish the scale, sign, jump spectrum, finite-column domain, residual norm, and form-Schur square argument. This review inspected the actual published research source implementations, not merely the public status summaries.

### 3.1 Whole-interval potential and squared-potential moments

For \(r\ge0\), set \(L=\log2\), \(\alpha_r=2H_{2r+2}-H_{r+1}\), \(\beta_r=4H_{2r+2}^{(2)}-H_{r+1}^{(2)}\), and \(u_r=(2r+1)^{-1}\). Differentiating
\[
 I_r(s)=\int_{-1}^1 x^{2r}(1-x^2)^s\,dx
      =B(r+\tfrac12,s+1)
\]
at \(s=0\) gives the **exact analytic** identities
\[
 \int_{-1}^1x^{2r}v(x)\,dx=u_r(\alpha_r-2L),
\]
\[
 \int_{-1}^1x^{2r}v(x)^2\,dx
   =\frac{u_r}{2}\left[(\alpha_r-2L)^2+\beta_r-\frac{\pi^2}{3}\right],
 \qquad v(x)=-\tfrac12\log(1-x^2).
\]
Odd moments vanish by reflection. The grouped harmonic rational contraction in `_potential_matrices` is algebraically consistent with these identities: it contracts rational Legendre products exactly before introducing the Arb enclosures of \(L,\pi\). The formulas hold for **arbitrary degree**, so the mathematical validity does not depend on numerical quadrature or a small-degree heuristic.

### 3.2 Translated logarithmic \(VP\) moments

The existing elementary primitives
\[
 F_n^-(x)=\frac{(x^{n+1}-1)\log(1-x)-\sum_{j=1}^{n+1}x^j/j}{n+1},
\quad
 F_n^+(x)=\frac{(x^{n+1}-(-1)^{n+1})\log(1+x)-\sum_{j=0}^n(-1)^j x^{n-j+1}/(n-j+1)}{n+1}
\]
satisfy \((F_n^\pm)'=x^n\log(1\mp x)\) with the matching signs; direct polynomial division cancels the nonlogarithmic derivatives for every integer \(n\ge0\). Singular endpoints have finite removable limits (the corresponding signed harmonic sums). On any certified active translated subinterval \([a,b]\),
\[
 \int_a^b x^nv(x)\,dx=-\tfrac12\big[F_n^-(b)-F_n^-(a)+F_n^+(b)-F_n^+(a)\big].
\]
Strictly certified interior breakpoints and strictly positive logarithm arguments are essential. The source algorithm represents \(P_TP_j(x)\) by rigorously enclosed shifted polynomials on exactly the two supported intervals for each active prime power; the signs are \(-\Lambda(m)/\sqrt m\), and \(T=11/20\) rigorously selects precisely \(m=2,3\). The ordered \(VP\) integrals are combinations of these exact moment identities, not applications of an unproven singular numerical quadrature.

### 3.3 Residual and \(VR_K/PR_K/PP\)

The residual approximation \(R_K\) is a finite signed sum of exact rational polynomial kernels \(-T\sum_{\ell\le K}a_\ell (T|x-y|)^\ell\), with coefficients derived from exact Bernoulli polynomials and the even Suzuki positive-side branch. The action on each Legendre polynomial is an **exact rational polynomial**, because each \(\int_{-1}^1 |x-y|^\ell y^k\,dy\) is the sum of two exact polynomial endpoint primitives. Hence \(VR_K\) is a whole-interval potential moment of a rational polynomial; \(PR_K\) is a finite sum of ordinary translated-cell polynomial moments. No nonrational integration is needed for the last pairing. The combined **\(PP\)** image Gram must sum the signed prime-power images **before squaring**, retaining both \((2,3)\) cross terms; the existing cell-local Legendre construction does this.

For the **full** \(R_T\), the uniform Taylor remainder proof in F-20261017-004, based on the Bernoulli Fourier coefficient bounds and \(2T<\pi\), gives rigorously positive \(\delta_K,\rho_R\) satisfying \(\|R_T-R_K\|\le\delta_K\), \(\|R_T\|\le\rho_R\). The generator does not assert \(R_T=R_K\). In unnormalized coordinates,
\[
 G_{\rm full}\preceq(1+\eta)G_K+(1+\eta^{-1})\delta_K^2D_N,\quad \eta=2^{-24}.
\]
The full complementary form lower bound uses \(H_N-c_T-\sum c_mb_m-\rho_R\); the exact research input enclosure for \(\mu_N\) is strictly positive. The scalar low-form remainder is \(-\delta_KD_N\), in the correct LOWER direction.

### 3.4 Rational matrix order and proof direction

The exact finite low-image Gram satisfies
\[
 G_K=\sum_{X,Y\in\{V,P,R_K\}}\langle XP_i,YP_j\rangle
  -(K_V+K_P+K_R)D_N^{-1}(K_V+K_P+K_R),
\]
with **nine ordered image terms**. From entrywise symmetric intervals \([L_{ij},U_{ij}]\), an exact rational center \(C_{ij}=(L_{ij}+U_{ij})/2\) and radius \(r_{ij}=(U_{ij}-L_{ij})/2\) yield valid **Loewner**, not merely entrywise, matrix inequalities:
\[
 C-\operatorname{diag}\Big(\sum_jr_{ij}\Big)
 \preceq X
 \preceq C+\operatorname{diag}\Big(\sum_jr_{ij}\Big).
\]
The valid candidate \(S_{\rm low}\) is built by lower-inflating \(A\), upper-inflating \(G_K\), applying the **full** \(R_T\) Young correction, and dividing the positive majorant by the strictly positive certified lower complementary bound. The independent rational checker verifies this order arithmetic and the complete strict rational congruence margin. An arbitrary independently checked invertible rational congruence with every exact Gershgorin margin positive proves \(S_{\rm low}\succ0\), regardless of how a floating-point algorithm proposed that congruence.

## 4. Newly executed independent controls

A separate, **research-only** source-checking script `scripts/audit_suzuki_math_closure.py` ran over the immutable SYS-4 input packet (hash `655d481d638f8b6fba0f95d01a4bab45079d905fbc6cb4f3e822571729d4d7c1`):

- **81/81 exact rational tests PASS**: independently expand the two halves of \(\int_{-1}^1|x-y|^\ell y^kdy\), for \(\ell,k=0,\ldots,8\), and compare the exact polynomial to `_abs_power_action`. These are genuine equality tests over rationals and validate sampled instances of the general binomial/endpoint identity.
- **8/8 high-precision reference checks PASS**: \(\int x^nv(x)\) and \(\int x^nv(x)^2\) for \(n=0,2,20,190\), against independent 75-decimal-digit `mpmath` quadrature. Maximum absolute discrepancy among these diagnostic comparisons was about \(4.15\times10^{-76}\). **Numerical quadrature is NOT the enclosure proof; the preceding beta-derivative identities are.**
- **All 37,056 saved rational entry slots PRESENT**: two separate \(192\times192\) symmetric matrices represented by 18,528 upper-triangular entries each. This is a packet-**completeness** check, not verification of the analytical value inside every interval.
- Primary packet SHA-256 confirmed unchanged. No full \(N=192\) reassembly, secondary dimension or new theorem admission was performed.

Script SHA-256: `369531ec58196d5939d2fa6d4facc93d45aa18992d4821c0dc15140f20c35ad1`. Output [`analytic-identity-audit.json`](../computations/2026-10-17T214044Z-sys5-analytic-proof-audit/data/analytic-identity-audit.json), SHA-256 `2727d45bc3080d16a850bb65e9ee06b27d73579942b7485c6abfbfa504e7ece4`.

## 5. Unclosed independent all-entry input-verification obligation

**This is a substantive distinction, not a numerical sign failure.** The exact rational checker proves:
\[
 \text{if every serialized } A,G_K,\mu,\delta\text{ interval contains its specified analytic quantity, then } S_{\rm low}\succ0.
\]
The verified algebraic identities and correct Arb ball semantics explain **how** such enclosures can be obtained for every matrix entry, but the currently archived rational packet does **not** provide an independently checked chain of exact/rigorous per-entry analytical derivations in a separate acceptance system. It contains their final interval endpoints and source hashes. Recomputing a few entries or simply trusting the generator's completion flag would not close this obligation.

Specifically not independently closed from the archived packet:

1. Complete exact rational Legendre and residual polynomial derivation for *every* indexed input, including all \(R_KP_j\) images and all \(PP,PR_K,VR_K,VP,VV,R_KR_K\) matrix contractions.
2. Independently validated rigorous values of the shared transcendental constants and moving endpoints (\(\log 2,\log 3,\sqrt2,\sqrt3,\pi,\gamma,\log(2\pi T)\)) for the entire interval evaluation, including branch/topology positivity controls and dependence management.
3. Independently reconstructed outward input bounds for every low-form and truncated Gram entry, and checked their containment in the **immutable** stored rational endpoints; plus independently reconstructed \(\underline\mu_N\) and full-residual \(\overline\delta_K\).
4. A complete trusted chain from these checked bounds through the exact rational matrix proof. The **last link already exists** as a separate rational verifier; the first three are not yet linked to it in an independently closed system.

An independently checkable mathematical route is available **without duplicating arbitrary-precision quadrature**: use the displayed exact rational polynomial identities, finite Legendre recurrences, exact Bernoulli coefficients, the potential/beta-moment formulas, and certified interval evaluations of elementary functions/constant enclosures at the finite translated boundaries. Every entry is a finite expression assembled from these operations, after which the already independent exact rational matrix-order check applies. This describes a **rigorous mathematical reduction**, not an already completed independent all-entry proof of the archived data. The concrete contract/implementation and admissibility decision remain separate; nothing is assumed admitted.

### Domain boundary

The original source equation is established on \(H_0^1\) and hence its \(C_c^\infty\) test subclass. The constructed closed form has the correct inclusion and agreement for these functions, so **full equality of canonical Friedrichs extension operator domains is not required for the finite-support test-class theorem**. Such equality remains **UNESTABLISHED** and is not represented as a missing condition if the precise theorem is only about \(C_c^\infty(-T,T)\).

## 6. Mathematical gate assessment

| Requirement | Assessment |
|---|---|
| Precise finite-support theorem, test class and non-RH scope | **CLOSED** as a conditional target statement |
| Suzuki scaling, jump spectrum, signed arithmetic and closed-form implication | **MATHEMATICALLY SUPPORTED** by source/C-0063..65 and reinspection |
| Correct exact whole-interval \(V,V^2\) moments | **MATHEMATICALLY DERIVED**; eight new numerical references pass |
| Correct translated logarithmic \(VP\) integrals | **MATHEMATICALLY DERIVED** via general antiderivative; previously independently checked |
| Exact residual kernel polynomial action and full norm tail | **MATHEMATICALLY DERIVED**; 81 new exact action references pass |
| Complete mixed \(PP,PR_K,VR_K\) finite-integral identities | **MATHEMATICALLY DERIVED**; prior independent cell/reference checks survive |
| Correct \(D_N\) Gram/Loewner/complement/Schur inequality directions | **CLOSED** at the algebraic/mathematical level |
| Full immutable rational input packet and exact rational positivity | **EXIST / INDEPENDENTLY EXACT-CHECKED** |
| Independent rigorous validation of **every** analytical input enclosure against the archived packet | **NOT COMPLETE** |
| Full canonical source operator-domain equality | **NOT PROVED; NOT NEEDED** for the stated test-class theorem |
| Admission of a new theorem or RH | **NOT ATTEMPTED; NOT SUPPORTED** |

**Disposition:** The mathematical reduction and proof implications are explicit and source-grounded, but the **complete independent analytical-input closure gate remains NOT SATISFIED**. The positive result remains `POSITIVE_CANDIDATE`, PRE-THEOREM; this finding neither invalidates the candidate nor promotes it. No theorem-level claim has been admitted, and no RH conclusion follows.

---

## 2026-10-17T22:02:54Z — Later complete input-enclosure verification closes this prior gap

The original proof-obligation audit above described the repository **before** the subsequently executed independent high-dimensional analytical reference. [`F-20261017-015`](2026-10-17T220105Z-complete-independent-analytic-enclosure-closure.md) / [`X-20261017-006`](../computations/2026-10-17T215700Z-sys5-full-analytic-acceptance/record.md) subsequently performed a wholly separate rigorous 2048-bit Arb reconstruction and verified strong **per-entry rational containment** of all **37,056** archived matrix intervals, plus \(\mu,\delta\), followed by a successful separate strict exact rational Schur-congruence replay. The previously unclosed analytical-input gate documented in this finding is therefore **SATISFIED** for the **fixed** \(T=11/20,N=192\) case under the explicitly stated Arb/source-identity trusted base. The historical content above is preserved as an as-of audit; its former missing-input classification must **not** be construed as the current mathematical result. No Rust/Lean certificate, explicit repository theorem admission, all-support positivity or RH proof results from this update.
