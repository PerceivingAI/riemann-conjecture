# Complete independent analytical input containment closes the fixed-support proof obligations

- **Finding ID:** F-20261017-015
- **Created:** 2026-10-17T22:01:05Z
- **Last updated:** 2026-10-17T22:01:05Z
- **Type:** MATHEMATICAL_PROOF_CLOSURE / independent interval enclosure and exact rational implication
- **Status:** **ANALYTICAL INPUT GATE CLOSED for T=11/20,N=192; NOT AN ADMITTED THEOREM**
- **Evidence:** [X-20261017-006](../computations/2026-10-17T215700Z-sys5-full-analytic-acceptance/record.md) complete all-entry check; previous [X-20261017-003](../computations/2026-10-17T150153Z-combined-schur-bounded-test/record.md) exact rational witness and [X-20261017-004](../computations/2026-10-17T153222Z-analytic-source-review/record.md) mathematical audit; prior [F-20261017-014](2026-10-17T214129Z-finite-support-theorem-analytic-proof-obligations.md) explicitly identified the missing gate.
- **Acceptance boundary:** Mathematical/source proof closure, **not** a v1/v2 Rust/Lean verifier contract, automatic whitelist admission or RH resolution.

## 1. The missing input proof has been supplied

The mathematical conditional implication established in C-0063–C-0065 and F-20261017-014 is unchanged. In the original **unnormalized** Legendre basis, the exact positive candidate is the conservative Schur lower matrix
\[
  S_{\rm low}=\underline A_{192}
     -\underline\mu_{192}^{-1}\overline G_{\rm full},\qquad
 \overline G_{\rm full}=(1+\eta)\overline G_K+
      (1+\eta^{-1})\overline\delta_K^{\,2}D_{192},
 \quad\eta=2^{-24}.
\]
A rigorously positive full-tail complement, the complete signed \(P_2+P_3\) mixed-image Gram and every ordered \(V/P/R_K\) cross contribution are included. The archived lower-Schur matrix already has a strict independent exact rational congruence witness with positive exact Gershgorin margin.

**New independently executed verification:** a *separate* finite-expression Arb evaluator computed, at **2048 bits**, a rigorously enclosed mathematical interval for each of **18,528** low \(A\) entries and **18,528** combined \(G_K\) entries, and independently enclosed the full-tail \(\mu_N\) and \(\delta_K\) scalars. All **37,056/37,056** new matrix-entry intervals were **entirely contained** in the corresponding original 352-bit dyadic input bounds, as confirmed using exact rational endpoints. The two scalar intervals also passed strong containment. This is substantially stronger than sampled numerical integration, floating agreement or overlapping intervals.

The independent evaluator does not call the existing high-dimensional Gram generator and uses alternate exact residual polynomial expansion, direct local-Legendre shifted-cell matrices, independent whole-interval beta moments, singular-cell logarithmic antiderivatives, and exact matrix contractions. Both routes use python-flint's Arb rigorous arithmetic and exact `fmpq`; Arb primitive correctness and the analytic Suzuki source identity are the mathematical trusted base, not two wholly separate arbitrary-precision libraries. Every bound is derived from finite expressions whose identities are given in F-20261017-014 and X-20261017-006.

## 2. Complete proof implication at this support

The independent full-entry check proves the original intervals really enclose the intended analytic quantities **under the stated Arb/source trust assumptions**. The separate exact rational verifier then rebuilt the entire \(S_{\rm low}\) from these intervals and the full Young residual bound, and verified strict positive definiteness through the unchanged invertible dyadic congruence. Since \(S_{\rm low}\preceq S_{\rm comb}\), with the rigorously positive full-tail form complement, the domain-safe form-Schur identity gives a positive \(L^2\) coercivity constant for the constructed form on \(\mathcal F_T\). Suzuki's scaled source equation agrees with the localized Weil form for \(C_c^\infty(-T,T)\subset H_0^1\subset\mathcal F_T\), so the **precise finite-support mathematical target** is:
\[
 \boxed{\exists\varepsilon>0\quad
    Q_W(f)\ge\varepsilon\|f\|_{L^2(-11/20,11/20)}^2
    \qquad\forall f\in C_c^\infty(-11/20,11/20)}
\]
in Suzuki's normalization.

There is **no claim** of positivity for all \(T\), RH, or full equality of the associated canonical Friedrichs operator domains. The earlier factor-3 negative sufficient bounds are unchanged and logically compatible with the positive **different combined** criterion.

## 3. What is and is not closed

| Gate | Status |
|---|---|
| Mathematically defined finite-support theorem and original source test class | **CLOSED** |
| All derived moments, shifts, residual and form-Schur inequalities | **CLOSED at source mathematics level** |
| Independently evaluated **all** archived low/Gram analytical input entries | **CLOSED — 37,056/37,056 strict containments** |
| Independent complement and residual scalar intervals | **CLOSED** |
| Independent exact rational positivity witness | **CLOSED — original witness replay PASS** |
| Frozen v1 and unrelated v2 semantics | **UNCHANGED** |
| Separate versioned proof-bearing certificate/Rust verifier/Lean acceptance architecture | **NOT IMPLEMENTED** |
| Explicit admission/retained-proof registration | **NOT PERFORMED** |
| Any RH theorem | **NOT ESTABLISHED** |

**Disposition:** The original SYS-5.1 independent analytical enclosure objection is resolved; the **mathematical verification gate is satisfied**, with an explicit shared rigorous Arb and source-form trust base. A new theorem has **not** been admitted into the repository’s governed v1/v2 theorem ledger. Distinguish the mathematically supported one-support positivity statement from formal certificate acceptance and broader RH.
