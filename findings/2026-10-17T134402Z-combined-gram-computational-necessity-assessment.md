# Computational necessity of a cancellation-sensitive combined low-to-tail Gram bound

- **Finding ID:** F-20261017-007
- **Created:** 2026-10-17T13:44:02Z
- **Last updated:** 2026-10-17T13:46:00Z
- **Type:** OPEN_REQUIREMENT / source-grounded mathematical-computation capability assessment; not a new theorem
- **Status:** VERIFIED for the documented present mathematical and software capability distinction
- **Current repository revision:** `a18746e437b52cdd0a3f0d4af1654df116be28de` (clean baseline)
- **Scope:** Computational necessity analysis only. No implementation, new test run, theorem admission, new claim ID, or privately scoped planning decision.
- **Source premise:** Consolidated valid-but-not-numerically-resolved combined-form research `F-20261017-006` and the exact `C-0063..C-0066` statements.

## Question and source-grounded answer

**Question.** What exact mathematical information is missing before the established *conditional* combined low-to-tail Schur sufficiency criterion can be tested meaningfully at the retained \((T,N)=(11/20,192)\) or \((11/20,196)\), and has the necessity of any *new software* actually been demonstrated?

**Answer.** The mathematical bottleneck for a positive combined-Schur result is not the algebra, the operator domain, the complete residual estimate, or positivity of the tail-complement estimate at these two configurations. It is the absence of an **available, sufficiently sharp, rigorously justified upper bound on the *combined* low-to-tail Gram**, or an equivalent certified lower bound directly on the combined Schur form. Such a bound must account for the cancellation and reinforcement from all mixed \(V/P/R\) terms and the combined signed arithmetic operator. The current componentwise factor-3 bound is sound but has rigorously negative directions at these targets, so re-evaluating that *same* sufficient matrix at higher precision cannot certify it positive.

The **complete exact mixed-Gram matrix is *not* mathematically necessary as an output**: a valid matrix-order upper enclosure, an equivalent norm/form bound, or another separately justified positivity argument would suffice. This audit does not establish that all such alternatives fail or that writing a new mixed-integral assembler is unavoidable. The necessity is for *additional cancellation-sensitive mathematical information* to decide positivity, **not yet for a particular implementation**.

The available finite-tail projected calculation can already search for a rigorous negative direction of the new sufficient matrix; it supplies a **lower** bound on the Gram, hence an **upper** bound on the Schur Rayleigh form. Its four executed trials were inconclusive. Therefore **a new computational capability is not yet required to express or execute a valid negative-direction test**. No amount of reinterpreting its positive *upper* Rayleigh bounds proves a positive lower bound for the complete Schur form.

## 1. Fixed mathematical target and directional requirements

Use the SYS-2 closed form
\[
 \mathfrak l_T=\mathfrak j+\mathfrak v+
     \langle \,\cdot\,,(P_T+R_T-c_TI)\,\cdot\,\rangle
 \quad\text{on }D(J^{1/2})\cap D(V^{1/2}),
\]
and finite Legendre low space \(E_N=\operatorname{span}\{P_0,\ldots,P_{N-1}\}\). The potential \(V\) is unbounded globally but maps each low polynomial into \(L^2\), so
\[
 W=V+P_T+R_T\ \text{on }E_N,\qquad
 B=Q_NW|_{E_N},\qquad G=B^*B
\]
are meaningful with finite low-to-tail columns. With a verified **positive full-form complement** \(\mathfrak c_N[q]\ge\mu_N\|q\|^2\), \(\mu_N>0\), define
\[
 S_{\mathrm{comb}}=A_N-\mu_N^{-1}G .
\]

### Positive decision

To prove \(S_{\mathrm{comb}}\succ0\), it is sufficient to obtain, under correct \(L^2\)-operator/Legendre-coordinate normalization, an independently justified
\[
 \underline A_N\preceq A_N,\qquad
 0\preceq G\preceq\overline G_N,\qquad
 \underline\mu_N>0
\]
where \(\mu_N\ge\underline\mu_N\), such that
\[
 \boxed{\underline A_N-\underline\mu_N^{-1}\overline G_N\succ0.}
 \tag{1.1}
\]
Other direct ways to certify a positive lower bound for \(S_{\mathrm{comb}}\) are equally admissible. Equation (1.1) does **not** demand every exact \(M_{XY}\) entry; a rigorous cancellation-sensitive matrix-order upper bound is enough. A rigorous computation of a full mixed-Gram upper enclosure would be **one** way to supply it.

The old bound \(G\preceq3(G_V+G_P+G_R)\) is mathematically correct, but the retained \(\underline A-(3/\mu_N)(GV+GP+GR)\) implementation has exact negative directions at the two frozen targets. This disqualifies *that existing sufficient test*, not (1.1), the complete Weil form, or the possibility of other sharper estimates. The software cannot simply relabel the old conservative `GV/GP/GR` entries as \(\overline G_N\) with all mixed cancellations.

### Negative decision

For some nonzero **exact** \(u\in E_N\), it is sufficient to prove
\[
 \boxed{\langle u,A_Nu\rangle-
          \mu_N^{-1}\|Bu\|^2<0.}
 \tag{1.2}
\]
A certified **upper** bound on the left that is strictly negative suffices; one only needs an appropriate **lower** Gram bound along that vector, not a full positive-semidefinite upper matrix.

The existing projected method `C-0066` takes \(Q_{N,M}=\Pi_M-\Pi_N\) and bounds
\[
 \|Bu\|^2\ge
 \left[\max\left(0,\,
 \|Q_{N,M}(V+P_T+R_{T,K})u\|
                 -\delta_K\|u\|\right)\right]^2,
 \qquad \|R_T-R_{T,K}\|\le\delta_K .
\]
Its matrix elements can already be rigorously enclosed using off-diagonal entries of the current low assembler at enlarged \(M\). The complete tail contribution *beyond* \(M\) is omitted only in the direction that makes the bound safe; its absence can prevent a decisive negative conclusion, but not invalidate one. The historical negative directions for the *old* factor-3 Schur are merely candidate trial vectors, not automatically negative for (1.2).

**No current experiment proves (1.2):** the four rigorous projected upper Rayleigh results at \(T=11/20\), \(N=192/196\), \(M=204/224\) remain **INCONCLUSIVE**:
\[
 +4.858448\ldots,\quad +0.785257\ldots,\quad
 +4.552997\ldots,\quad +0.727958\ldots .
\]
A **positive upper bound** cannot be used to conclude positivity of the actual Rayleigh form. More tail modes, another exact direction, or sharper analytic inequalities *might* change the evidence; their value and necessity are not established by this audit. No further numerical sweep is authorized or performed here.

## 2. What the present code already delivers

The following capabilities are observed from the current implementation and the dated source-verified SYS-1/SYS-2 evidence, **not** inferred from a proposed future tool:

| Quantity/capability | Existing implementation | Relation to target |
|---|---|---|
| Exact finite low form with rigorous \(V,P_T,R_{T,K}\), scalar and jump contributions | `scripts/cert/multi_prime_legendre_schur.py::assemble_multi_prime_schur` | Supplies conservative low \(\underline A_N\), including \(-\delta_KD_N\); not the exact full \(A_N\) |
| Positive conservative full-tail complement bound \(\mu_N\) | Same assembler, `compressed_shift_norm_bound` and `_residual_rho` | Verified \(\mu_{192}>0\), \(\mu_{196}>0\) at the tested support; not a global guarantee |
| Potential \(V,V^2\) low-image moments | `_potential_matrices` | Separately encloses \(V\) and its own squared image |
| Combined signed arithmetic \(P_T,P_T^2\), including \(P_2/P_3\) mixed terms | `scripts/cert/prime_power_terms.py` | Existing arithmetic cross-prime terms are retained; not the cross terms with \(V\) and \(R\) |
| Polynomial residual \(R_{T,K}\), \(R_{T,K}^2\), full residual error \(\delta_K\) | `_residual_truncation_operator`; `scripts/cert/residual_kernel.py` | Does not replace the full \(R_T\); error is already rigorously controlled |
| Componentwise \(GV,GP,GR\) with factor-3 Schur | `assemble_multi_prime_schur` | Valid conservative **old** sufficient test; rigorously negative at fixed \((11/20,192/196)\) |
| Finite projected combined low-to-tail norm for selected exact vectors | `scripts/weil_projected_mixed_schur_check.py` (X-20261017-001) | Rigorous **lower** Gram and **upper** Schur Rayleigh bounds; not a positivity proof or full mixed Gram |
| Verified full mixed image-image terms \(M_{VP},M_{VR},M_{PR}\) and conjugates | **Not exposed by the inspected rigorous assembler or projected diagnostic** | A full combined-Gram computation cannot be claimed from currently returned `GV/GP/GR` values |
| Explicit certified **upper** bound that retains all required cross-component cancellations | **Not demonstrated by the reviewed current workflows** | This is the precise *information gap* for applying (1.1) to the frozen targets |

These statements do **not** claim that existing Arb primitives are unable to compute mixed image integrals; whether they can be combined safely to supply the missing enclosures is a separate source-level/mathematical capability question, **not resolved by this necessity audit**.

## 3. Which alleged blockers are *not* established

- **Mathematical validity:** The operator/domain-based combined Schur implication and exact image-matrix formula are already established conditionally (`C-0063..C-0065`); there is no new failed identity motivating speculative tool development.
- **Complement coercivity:** The existing conservative full-tail formula is already certified strictly positive for the two tested configurations. Replacing the complement bound is not justified as a prerequisite for the scoped computational-necessity question.
- **Residual treatment:** The full residual and its rigorously bounded truncation are present. An evaluator must respect them, but there is no observed failure in the existing remainder handling that justifies changing it here.
- **Arithmetic mixed prime powers:** \(P_2/P_3\) cross terms are already included inside \(P_T^2\); no per-prime reconstruction is needed.
- **Interval conditioning:** Historical catastrophic *old assembler* width growth was analyzed and repaired; the SYS-2 projected computation gave rigorous results without reporting an interval blow-up. A conditioning problem **in the yet-uncomputed new mixed image-image terms** has not been measured and must not be presumed.
- **Independent theorem verifier, formalization and orchestration:** No new theorem-acceptance obligation, missing Lean lemma, process leak or cache-integrity failure is demonstrated by the mathematical tests. No change in those systems follows from this audit.
- **Canonical Suzuki operator domains:** The prior caveat regarding equality of entire canonical and constructed operator domains remains. It does not change the supported implication on Suzuki's original admissible test class and is not a missing numerical input for the finite combined criterion.

## 4. Bounded decision and completion gate

**Outcome for SYS-3.1: COMPLETE AS A NECESSITY ASSESSMENT.**

- The precise unresolved question is the sign of \(S_{\mathrm{comb}}\) at retained \(T=11/20\), \(N=192/196\), not the validity of the operator identity or of the old factor-3 negative witnesses.
- The strictly positive complementary bounds needed for the *conditional* Schur reduction have already been exhibited at these two configurations.
- For a **positive result**, a valid sufficiently sharp **cancellation-sensitive upper bound on the combined Gram**, or another direct rigorous lower bound for \(S_{\mathrm{comb}}\), is needed; the complete exact mixed-Gram matrix is *one option, not a mathematical necessity*.
- For a **negative result**, the existing finite-tail projected lower Gram bound is already a mathematically adequate testing mechanism when it supplies a negative upper Rayleigh value. The four executed trials did not.
- The current source interface does not supply a rigorous **full combined Gram** or equivalent cancellation-sensitive upper enclosure, **but this does not prove new production code is necessary**: existing Arb/moment/translation/residual primitives may be sufficient without a new general subsystem.
- **Implementation decision: NOT AUTHORIZED by SYS-3.1.** What is justified is a bounded audit of existing primitives against the specific missing upper-bound problem. No new numerical experiment, certificate profile, theorem admission, general tooling development, or private planning decision belongs to this record.

This finding reports what mathematical information would settle the present scoped criterion and distinguishes existing functionality from missing *demonstrated* output. It records no choice of a future integration primitive or computational method.

## Source map

- [Consolidated SYS-2 mathematical conclusion](2026-10-17T130040Z-sys2-combined-criterion-mathematical-conclusion.md), `F-20261017-006`.
- [Exact combined low-to-tail Schur sufficiency](2026-10-17T121100Z-combined-cross-block-form-schur-criterion.md), `C-0064`.
- [Exact mixed-Gram image identities](2026-10-17T121809Z-exact-mixed-low-tail-gram-identities.md), `C-0065`.
- [Finite-tail projected obstruction and its incomplete sign outcome](2026-10-17T124537Z-projected-mixed-schur-obstruction.md), `C-0066`.
- [Rigorous projected computation](../computations/2026-10-17T124000Z-sys2-projected-obstruction/record.md), `X-20261017-001`.
- [Previously rigorous negative old factor-3 test](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md).
- [Current rigorous multi-prime assembler](../scripts/cert/multi_prime_legendre_schur.py), [combined prime powers](../scripts/cert/prime_power_terms.py), [Suzuki residual series](../scripts/cert/residual_kernel.py), and [finite-projection diagnostic](../scripts/weil_projected_mixed_schur_check.py).
- [Current audited tool interfaces](../docs/TOOL_CAPABILITIES.md).
