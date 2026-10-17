# SYS-2.6 — Consolidated mathematical conclusion of the combined low-to-tail investigation

- **Finding ID:** F-20261017-006
- **Created:** 2026-10-17T13:00:40Z
- **Last updated:** 2026-10-17T13:00:40Z
- **Type:** DERIVED_RESULT synthesis and research closure (no new theorem beyond C-0063–C-0066)
- **Status:** VERIFIED for the scoped conditional mathematics; actual combined-Schur positivity is **NOT NUMERICALLY RESOLVED**
- **Classification:** **VALID BUT NOT NUMERICALLY RESOLVED**
- **Consolidated evidence:** F-20261017-001 through F-20261017-005; C-0063 through C-0066; X-20261017-001
- **Research source baseline:** `fcf4353adaf090480b695cf089bf9f17f5ad9f04`; the dated SYS-2.1–2.5 evidence remains separate, unaltered research history
- **Scope:** Mathematical conclusion and evidence boundaries only. No theorem admission, certificate implementation, new computational experiment, or future research/tooling roadmap.

## 1. Mathematical question and answer

The earlier generic multi-prime v2 **factor-3 sufficient** Legendre–Schur matrices at \(T=11/20\), \(N=192\) and \(196\) possess rigorously negative directions (the retained 2026-10-02 record). That conclusion concerns the **old sufficient lower bound**, not the underlying localized Weil quadratic form. The SYS-2 question is whether the *combined* low-to-tail operator block leads to a mathematically valid sufficient alternative, under the exact Suzuki normalization and correct unbounded-operator domains.

**Answer: yes, as a conditional mathematical criterion.** The exact combined-block inequality, matrix identities, and sufficient full-form positivity implication have been derived and independently checked. **No**, the investigation does **not** establish that the new combined sufficient condition is positive at any new support or dimension; its numerical sign at the two retained dimensions remains unresolved.

The two statements must not be conflated: a valid sufficient implication is not a verified instance of its hypotheses.

## 2. Precise Hilbert space, operators and domain hypotheses

For \(0<T<\pi/2\), in particular the first two-prime window \(\tfrac12\log 3<T<\log2\), use
\[
 H=L^2((-1,1),dx;\mathbb C),\qquad
 \mathcal F_T=D(J^{1/2})\cap D(V^{1/2}).
\]
Let \(\ell_n=P_n\) be the ordinary Legendre polynomials, \(e_n=\ell_n/\sqrt{d_n}\), \(d_n=2/(2n+1)\), \(J e_n=H_n e_n\), and \(Vf=-\tfrac12\log(1-x^2)f\) with its natural unbounded multiplication-operator domain. Let
\[
 P_T=-\sum_{\substack{m=p^k\\\log m<2T}}
       \frac{\Lambda(m)}{\sqrt m}S_{\log(m)/T},\quad
 (R_Tf)(x)=-T\int_{-1}^1r''_{\mathrm{even}}(T|x-y|)f(y)\,dy,
 \quad c_T=\log(2\pi T)+\gamma.
\]
Each \(S_{\tau}\) is the self-adjoint two-sided zero-extended compressed shift. There are finitely many active prime powers for fixed \(T\), so \(P_T\) is bounded self-adjoint. Suzuki's **full** residual \(R_T\) is bounded self-adjoint in this range; replacing it by a finite Taylor polynomial \(R_{T,K}\) requires the rigorous norm allowance \(\|R_T-R_{T,K}\|\le\delta_K\).

The localized expression is the closed, lower-semibounded **quadratic-form sum**
\[
 \mathfrak l_T=\mathfrak j+\mathfrak v
      +\langle\cdot,(P_T+R_T-c_TI)\cdot\rangle
           \quad\text{on }\mathcal F_T ,
\]
not an unproved everywhere-defined bounded matrix \(J-c_TI+V+P_T+R_T\). Every finite Legendre polynomial is in \(D(J)\cap D(V)\); hence for
\[
 E_N=\operatorname{span}\{\ell_0,\ldots,\ell_{N-1}\},\qquad
 \Pi_N:H\to E_N,\qquad Q_N=I-\Pi_N ,
\]
the finite-column maps \(B_X=Q_NX\Pi_N:H\to Q_NH\) exist and are bounded for \(X\in\{V,P_T,R_T\}\), **even though \(V\) is not globally bounded**. Both projections preserve the closed-form domain. The jump and scalar contributions have no low/tail cross form.

The source identity relating the constructed form to Suzuki's original localized Weil expression is an explicitly cited mathematical premise, verified on the original admissible test functions. **Identity of the entire constructed form-operator domain with the canonical source Friedrichs-extension operator domain is not established.** Such global operator-domain equality is not required for the conditional implication from strict positivity of the constructed form to Suzuki's admissible test class.

## 3. Exact combined criterion and derivation

Let \(B=B_V+B_P+B_R:E_N\to Q_NH\), \(A_N\) be the **exact** finite low-form operator on \(E_N\), and let \(\mathfrak c_N\) denote the **full** restricted complementary quadratic form on \(Q_N\mathcal F_T\).

For the three bounded low-to-tail maps, the exact operator identity
\[
 \boxed{
 3\sum_X B_X^*B_X-B^*B
  =\sum_{X<Y}(B_X-B_Y)^*(B_X-B_Y)\succeq0
 }
\]
holds as an identity on \(E_N\), without commutativity or disjoint-support assumptions. In particular \(B^*B\preceq3(G_V+G_P+G_R)\) for the **exact** component Grams, not by identifying current conservative v2 Arb enclosure matrices with their exact targets.

The **independent positive-tail hypothesis** is
\[
  \mathfrak c_N[q]\ge\mu_N\|q\|^2,\quad
   \mu_N>0,\quad q\in Q_N\mathcal F_T.
 \tag{H-tail}
\]
One rigorously justified lower candidate is
\[
 \mu_N=H_N-c_T-\sum_{m\in\mathcal A(T)}c_m b_m-\rho_R,
 \quad c_m=\Lambda(m)/\sqrt m,\quad
 b_m\ge\|S_{\log(m)/T}\|,\quad\rho_R\ge\|R_T\|.
\]
This formula supplies a valid **lower-bound inequality**, but positivity of its value must be checked for the actual parameters; it is not automatic.

On \(\mathcal F_T\), each \(w=u+q\) with \(u\in E_N\) and \(q\in Q_N\mathcal F_T\) obeys the exact form expansion
\[
 \mathfrak l_T[w]=\langle u,A_Nu\rangle+
 2\operatorname{Re}\langle Bu,q\rangle+\mathfrak c_N[q].
\]
Completing a square *only in the ordinary \(L^2\) norm* gives
\[
 \mathfrak l_T[u+q]\ge
 \left\langle u,
 \left(A_N-\mu_N^{-1}B^*B\right)u\right\rangle+
 \mu_N\|q+\mu_N^{-1}Bu\|^2.
\]
No application of the tail form to the vector \(Bu\) is presumed. Hence
\[
 \boxed{\text{(H-tail) and }A_N-\mu_N^{-1}B^*B\succ0
  \quad\Longrightarrow\quad
   \exists\delta>0:\ \mathfrak l_T[w]\ge\delta\|w\|^2
   \quad(\forall w\in\mathcal F_T).}
\]
If \(A_N-\mu_N^{-1}B^*B\succeq\lambda_NI_{E_N}\) with \(\lambda_N>0\), one explicit constant is
\[
 \delta=\frac{\min(\lambda_N,\mu_N)}
                  {(1+\|B\|/\mu_N)^2}>0.
\]
This is an **exact proved sufficient condition**, not a proof that its positive-definiteness premise is satisfied.

## 4. Exact Legendre mixed-Gram representation

In the ordinary *unnormalized* Legendre basis let \(D_N=\operatorname{diag}(d_0,\ldots,d_{N-1})\) and \(W=V+P_T+R_T\) applied **only** to low polynomials. Define
\[
 (K_X)_{ij}=\langle\ell_i,X\ell_j\rangle,\quad
 (M_{XY})_{ij}=\langle X\ell_i,Y\ell_j\rangle,\quad
 K=\sum_XK_X,\quad M=\sum_{X,Y}M_{XY}.
\]
Then
\[
 \boxed{
 G_{\mathrm{all}}=[\langle Q_NW\ell_i,Q_NW\ell_j\rangle]_{ij}
    =M-KD_N^{-1}K.
 }
\]
All nine ordered \(VV,VP,VR,PV,PP,PR,RV,RP,RR\) image terms and their matching \(K_XD_N^{-1}K_Y\) low-projection subtractions are present. This includes the already established \(P_2/P_3\) mixed prime-power terms **inside** the one signed arithmetic operator \(P_T\). Opposite-parity entries vanish by exact reflection symmetry, not by omission of same-parity mixed terms.

The image Gram is well-defined via the \(L^2\) vectors \(W\ell_i\); no arbitrary domain claim about \(W^2\) is necessary.

If \(R_T=R_{T,K}+E_K\), \(\|E_K\|\le\delta_K\), \(B_K=Q_N(V+P_T+R_{T,K})|_{E_N}\), and \(\Delta B=Q_NE_K|_{E_N}\), then
\[
 G_{\mathrm{all}}=B_K^*B_K+B_K^*\Delta B+
       \Delta B^*B_K+\Delta B^*\Delta B,
\]
with
\[
 \|G_{\mathrm{all}}-B_K^*B_K\|
 \le 2\|B_K\|\delta_K+\delta_K^2,
\]
and, for any \(\eta>0\),
\[
 G_{\mathrm{all}}\preceq (1+\eta)B_K^*B_K+
                    (1+\eta^{-1})\delta_K^2I_{E_N}.
\]
These correct full-residual inequalities do not imply that the current Python v2 `GV/GP/GR` enclosure outputs are a complete combined mixed-Gram evaluator.

## 5. Independent verification and the rigorous focused test

**Analytical verification.** F-20261017-004 independently checked: source normalization/signs; finite Legendre operator domains and closed-form self-adjointness; projections including the required \(D_N^{-1}\); all mixed \(V/P/R\) and mixed \(P_m/P_n\) terms; the Suzuki full-residual Bernoulli/Taylor remainder; and the complement form bound. It did **not** prove canonical source operator-domain equality or new matrix positivity.

**Rigorous numerical test.** F-20261017-005 / C-0066 proves a finite-tail projected obstruction inequality. For \(M>N\), with \(Q_{N,M}=\Pi_M-\Pi_N\),
\[
 \|Q_NWu\|\ge
 \max\{0,\|Q_{N,M}(V+P_T+R_{T,K})u\|-\delta_K\|u\|\}.
\]
The projected norm is expressible in rigorous off-diagonal Legendre matrix elements from the existing assembler. Together with the full low-form upper bound and positive \(\mu_N\), this gives a **certified upper Rayleigh bound** for the new exact combined sufficient matrix on a selected nonzero \(u\). Only a strictly negative **upper** bound would reject it at that parameter pair.

X-20261017-001 executed the four scoped Arb-384 tests at \(T=11/20\), residual order 32, using the historical exact dyadic old-criterion directions **only as trial vectors**:

| \(N\) | Finite tail \(M\) | Rigorous upper Rayleigh bound (decimal display) | Result |
|---:|---:|---:|---|
| 192 | 204 | +4.8584481571 | **INCONCLUSIVE** |
| 196 | 204 | +0.7852570808 | **INCONCLUSIVE** |
| 192 | 224 | +4.5529972808 | **INCONCLUSIVE** |
| 196 | 224 | +0.7279582237 | **INCONCLUSIVE** |

Both \(\mu_{192}\) and \(\mu_{196}\) were certified strictly positive by the existing complement formula. The projected bounds account for the complete residual error. **Positive upper Rayleigh bounds neither prove positivity of the actual new Schur form nor supply negative witnesses.** The test is not an evaluation of the entire mixed Gram.

**Current computability assessment.** The current rigorous assembler computes low \(V/P/R_K\) blocks, combined prime-power \(P^2\), and separately bounded `GV/GP/GR`; it does not provide numerical enclosures of all three \(VP/VR/PR\) mixed image-image matrices. Therefore **the full combined Schur matrix was not calculated or certified** at either dimension.

## 6. Result classification, completion gate and trust boundaries

**Classification: VALID BUT NOT NUMERICALLY RESOLVED.**

1. **Mathematical statement:** The closed-form combined-cross-block criterion is a valid *conditional* sufficient implication with exact hypotheses, and the complete unnormalized mixed-Gram matrix identities are proved.
2. **Domain assumptions:** Unbounded \(V\) is treated correctly on finite Legendre columns and in the closed form. The full original-source operator-domain identification is not claimed.
3. **Tail assumption:** Strictly positive full-tail \(\mu_N\) is required in an application. It is **verified in the two tested cases**, not asserted globally.
4. **Numerical evidence:** Four executed outward-enclosed projected tests yielded no sign conclusion for the **new** combined sufficient matrices. The original factor-3 negative directions remain valid for the **old** sufficient matrices only.
5. **Actual conclusion:** No combined matrix positivity, negative combined-direction witness, new finite-support theorem, v2 certificate admission, or RH result has been established.
6. **Go/no-go decision for SYS-2's stated purpose:** **GO** on mathematical validity of the *conditional operator criterion and exact identities*; **NO-GO** on promoting any new numerical or theorem claim from this phase. SYS-2's mathematical derivation/review/test gate is satisfied, regardless of the inconclusive sign result.

**SYS-2 is complete as a research phase.** This is a closure of its defined work and evidence, not a claim that the larger mathematical positivity question has been solved. No future research priorities, tooling-upgrade plans, or prospective publication decisions are made in this public conclusion.

## Source and evidence map

- [F-20261017-001: SYS-2.1 exact operator/domain setting](2026-10-17T115900Z-scaled-weil-operator-domain-and-low-tail-maps.md) — C-0063.
- [F-20261017-002: SYS-2.2 combined-cross-block positivity implication](2026-10-17T121100Z-combined-cross-block-form-schur-criterion.md) — C-0064.
- [F-20261017-003: SYS-2.3 complete mixed-Gram identity](2026-10-17T121809Z-exact-mixed-low-tail-gram-identities.md) — C-0065.
- [F-20261017-004: SYS-2.4 independent mathematical audit](2026-10-17T122838Z-independent-sys2-analytic-validity-audit.md).
- [F-20261017-005: SYS-2.5 finite-tail obstruction lemma and evaluated decision](2026-10-17T124537Z-projected-mixed-schur-obstruction.md) — C-0066.
- [X-20261017-001: reproducible Arb evidence](../computations/2026-10-17T124000Z-sys2-projected-obstruction/record.md), with exact historical witness identities and retained JSON interval output.
- [Current multi-prime contract](../docs/MULTI_PRIME_CONTRACT.md); [current source implementation](../scripts/cert/multi_prime_legendre_schur.py); [retained old factor-3 negative evidence](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md).
