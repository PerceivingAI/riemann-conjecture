# SYS-2.5 — Finite-tail projected obstruction test for the combined low-to-tail Schur criterion

- **Finding ID:** F-20261017-005
- **Created:** 2026-10-17T12:45:37Z
- **Last updated:** 2026-10-17T12:48:27Z
- **Type:** DERIVED_RESULT (finite-tail obstruction inequality), with computationally *inconclusive* scoped evaluation
- **Status:** VERIFIED for the mathematical inequality; no new support positivity or negative combined-Schur result
- **Claim:** C-0066
- **Computation:** X-20261017-001
- **Code revision:** `fcf4353adaf090480b695cf089bf9f17f5ad9f04` plus the dedicated, uncommitted research-only script in this record
- **Scope:** The three approved SYS-2.5 steps only. Existing proof certificates, Rust theorem whitelist, historical factor-3 negatives, and software contracts are unchanged.

## 1. SYS-2.5.1 — A sufficient *negative-direction* test

Use the established closed form and exact low-to-tail block from `C-0063..C-0065`: \(H=L^2(-1,1)\), \(E_N=\mathrm{span}\{P_0,\ldots,P_{N-1}\}\), \(Q_N=I-\Pi_N\), \(W=V+P_T+R_T\), \(B=Q_NW|_{E_N}\), and exact finite low form \(A_N\). Fix \(0<T<\pi/2\), a full-tail quadratic-form bound \(\mu_N>0\), a nonzero low vector \(u\in E_N\), and an integer \(M>N\). Let
\[
 Q_{N,M}=\Pi_M-\Pi_N,\qquad
 W_K=V+P_T+R_{T,K},\qquad
 \|R_T-R_{T,K}\|\le\delta_K .
\]
Although \(V\) is unbounded on \(H\), \(W_Ku\in H\) for every finite Legendre \(u\), as established in SYS-2.1. Since \(Q_{N,M}\) and \(Q_N\) are orthogonal projections onto nested tail spaces, the following holds without any matrix-positivity assumption:
\[
 \|Bu\|\ge\|Q_{N,M}Wu\|
 \ge \max\{0,\|Q_{N,M}W_Ku\|-\delta_K\|u\|\}.
 \tag{1.1}
\]
The triangle-inequality allowance is on the **full** Suzuki residual, not merely its Taylor polynomial.

With \(d_k=2/(2k+1)\), the finite projected truncated norm is the exact sum
\[
 g_{N,M,K}(u)
 =\|Q_{N,M}W_Ku\|^2
 =\sum_{k=N}^{M-1}
   \frac{|\langle P_k,W_Ku\rangle|^2}{d_k}.
 \tag{1.2}
\]
For unnormalized low coordinates \(u=\sum_{i<N}z_iP_i\), its entries are
\[
 \langle P_k,W_Ku\rangle
 =\sum_{i<N} z_i
       \bigl(K_V[k,i]+K_{P_T}[k,i]+K_{R_K}[k,i]\bigr).
 \tag{1.3}
\]
Those are **off-diagonal** entries in the rigorously assembled low matrix at enlarged dimension \(M\). They do not contain a \(J-c_TI\) term, since \(k\ge N>i\), or the conservative \(-\delta_K D_M\) diagonal correction. Therefore the *existing* `assemble_multi_prime_schur(n=M)` provides rigorous interval enclosures of exactly the quantities in (1.3) without evaluating any \(V/P/R\) image-image mixed integral. The full-tail complement constant for **\(N\)** is recovered from the same constants by replacing \(H_M\) with \(H_N\), not by incorrectly using \(\mu_M\).

Write
\[
 a_K(u)=\mathfrak j[u]+\mathfrak v[u]
   +\langle u,(P_T+R_{T,K}-c_TI)u\rangle,\quad
 s=\max\{0,\sqrt{g_{N,M,K}(u)}-\delta_K\|u\|\}.
\]
The low full-residual error satisfies
\(\langle u,A_Nu\rangle\le a_K(u)+\delta_K\|u\|^2\).
Thus the **exact mathematical obstruction inequality** is
\[
 \boxed{\displaystyle
 \left\langle u,\left(A_N-\mu_N^{-1}B^*B\right)u\right\rangle
 \le a_K(u)+\delta_K\|u\|^2-\frac{s^2}{\mu_N}
 =:U_{N,M,K}(u).
 }
 \tag{1.4}
\]
Whenever an outward-enclosed upper bound on \(U_{N,M,K}(u)\) is strictly **negative**, that *rigorously rejects* positive definiteness of the **new combined sufficient matrix** at the specified \(T,N,\mu_N\). It would **not** reject the full Weil form. If the upper bound is zero or positive, this test is **inconclusive**: an upper bound of positive sign provides *no* lower positivity bound on the true Schur form.

**Interval safety.** Evaluate \(a_K,\delta_K,\mu_N,g_{N,M,K},\|u\|^2\) with Arb outward intervals; require \(\mu_N^{\rm lower}>0\), take a certified *lower* bound on \(g\), an *upper* bound on \(\delta_K\|u\|\), and divide the resulting nonnegative squared lower bound by an *upper* bound on \(\mu_N\). To bound \(a_K+\delta_K\|u\|^2\) from above using the current assembled `A`, **add \(2\delta_K\|u\|^2\)** because its `A` already includes **\(-\delta_KD_M\)**. Any less conservative double counting would be invalid.

## 2. SYS-2.5.2 — Executed focused rigorous evaluation

The evidence in [X-20261017-001](../computations/2026-10-17T124000Z-sys2-projected-obstruction/record.md) contains the exact reproducible commands, source fingerprint, and rigorous Arb output at \(T=11/20\), residual order \(32\), Arb precision \(384\). Use the preserved **56-bit dyadic vectors** from the *old* factor-3 negative-direction diagnostic solely as test inputs; their previous old-matrix negative results are **not** assumed true of the new Gram.

Two finite projections were evaluated, not a dimension or support sweep:

| \(N\) | \(M\) | Certified projected **full** Gram lower (decimal display) | Certified **new Schur Rayleigh upper** (decimal display) | Decision |
|---:|---:|---:|---:|---|
| 192 | 204 | 0.4139799134 | **+4.8584481571** | INCONCLUSIVE |
| 196 | 204 | 0.06312924965 | **+0.7852570808** | INCONCLUSIVE |
| 192 | 224 | 0.5869287369 | **+4.5529972808** | INCONCLUSIVE |
| 196 | 224 | 0.09675076010 | **+0.7279582237** | INCONCLUSIVE |

In both dimensions the rigorous complement is positive:
\[
 \mu_{192}\in[0.5662083067859621\ldots,0.5662083067859622\ldots],\quad
 \mu_{196}\in[0.5867745390560106\ldots,0.5867745390560107\ldots],
\]
and the full-residual operator error is at most approximately \(9.82803\times10^{-16}\). Exact witness fractions, Arb-enclosed results and decisive *interval sign checks* are retained in the linked JSON files. Decimal displays above are for interpretation, **not** proof inputs.

**Result:** the tests certify neither a negative direction nor positive definiteness for the new Schur matrix. The rigorous *upper* Rayleigh bounds are positive; this cannot be reinterpreted as a positive **lower** bound. Enlarging the finite projection tightened the upper bounds but did not change the conclusion. The retained old factor-3 negative witnesses remain valid evidence **only for the old sufficient matrix**.

## 3. SYS-2.5.3 — Current full-Gram evaluability assessment and stop

The full mixed-Gram formula `C-0065` is mathematically well-defined, but the current `scripts/cert/multi_prime_legendre_schur.py` assembles only `A`, `GV`, `GP`, and conservative `GR`. `scripts/cert/prime_power_terms.py` computes the already-combined \(P^2\) (including cross-prime products); the potential module computes full-interval \(V\) and \(V^2\) moments; and residual machinery supplies **polynomial** \(R_K\) images and rigorous norm remainders. Those currently available outputs **do not enclose**
\[
 M_{VP}+M_{PV},\qquad
 M_{VR}+M_{RV},\qquad
 M_{PR}+M_{RP}
\]
as the **mixed, summed matrix elements required for the new criterion**. In particular a rigorous full image-image mixed pairing with the **logarithmic potential times piecewise compressed translations** is not furnished by the present assembler. Existing separate component Gram bounds cannot be relabeled as the exact combined Gram or substituted without losing the cross terms. The needed *mathematical representations* are in `C-0065`, but **numerical enclosure of the complete combined matrix has not been demonstrated using the current implementation**.

This is a factual present-execution boundary, not a specification or prioritization of any tooling upgrade. In accordance with SYS-2.5, the project did **not** introduce a new mixed-matrix implementation, an admission path, a general-purpose integration subsystem, or a different criterion to force a conclusion.

## 4. Interpretation, circularity, and closure

The finite-tail obstruction lemma is proved as an elementary consequence of nested orthogonal projections and the **full** residual norm bound. It is not circular: it uses neither RH nor assumed new Schur positivity. \(\mu_N\) comes from the existing independent conservative complementary form bound, not from a desired conclusion. Test vectors are historical exact rational input artifacts; no positive or negative Schur value is taken from the old test.

- **SYS-2.5.1:** COMPLETE — mathematically valid finite-tail obstruction inequality.
- **SYS-2.5.2:** EXECUTED — two dimensions, two focused tail projections; all four evaluations **INCONCLUSIVE** (no certified negative direction).
- **SYS-2.5.3:** COMPLETE AS FEASIBILITY ASSESSMENT — the present implementation does not construct the entire mixed Gram; hence **no justified full-Gram rigorous evaluation was executed**.

**SYS-2.5 final disposition:** **COMPLETE WITH INCONCLUSIVE MATHEMATICAL TEST**. The combined-cross-block sufficient criterion remains valid as a conditional theorem, but its actual sign remains **UNRESOLVED** at both retained supports/dimensions. No new theorem, certificate, or historical change follows. No future research priority or tooling upgrade is assigned in this public finding.

## References

- SYS-2.1–2.4: [F-20261017-001](2026-10-17T115900Z-scaled-weil-operator-domain-and-low-tail-maps.md), [F-20261017-002](2026-10-17T121100Z-combined-cross-block-form-schur-criterion.md), [F-20261017-003](2026-10-17T121809Z-exact-mixed-low-tail-gram-identities.md), [F-20261017-004](2026-10-17T122838Z-independent-sys2-analytic-validity-audit.md).
- Existing reference evidence: [multi-prime rigorous assembly performance and negative old-matrix Rayleigh record](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md).
- [Reproducible projected-tail computation X-20261017-001](../computations/2026-10-17T124000Z-sys2-projected-obstruction/record.md).
- Dedicated research-only script: [`scripts/weil_projected_mixed_schur_check.py`](../scripts/weil_projected_mixed_schur_check.py).
