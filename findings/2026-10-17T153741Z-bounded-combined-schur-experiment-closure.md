# Closure of the bounded combined low-to-tail Schur experiment: positive pre-theorem candidate

- **Finding ID:** F-20261017-013
- **Created:** 2026-10-17T15:37:41Z
- **Last updated:** 2026-10-17T15:37:41Z
- **Type:** RESEARCH_CLASSIFICATION / completed finite-support experiment and independently checked rational consequence
- **Status:** **CLOSED — POSITIVE_CANDIDATE (PRE-THEOREM)**; **NOT an admitted theorem**
- **Related evidence:** [X-20261017-003](../computations/2026-10-17T150153Z-combined-schur-bounded-test/record.md), [F-20261017-011](2026-10-17T151010Z-positive-combined-schur-pretheorem-candidate.md), [X-20261017-004](../computations/2026-10-17T153222Z-analytic-source-review/record.md), [F-20261017-012](2026-10-17T153222Z-independent-analytic-audit-positive-combined-schur.md)
- **Claims/theorem gate:** No new C-claim admitted, no change to frozen v1/v2 theorem acceptance, and **no RH proof**. This document closes an *executed* bounded research experiment; it is not an unpublished research plan.

## 1. Final classified outcome

For exact support \(T=11/20\) and ordinary unnormalized Legendre low dimension \(N=192\), consider the rigorously defined **combined** low-to-tail form-Schur sufficient matrix
\[
 S_{\rm comb}=A_{192}-\mu_{192}^{-1}B^*B,
 \quad B=Q_{192}(V+P_T+R_T)\Pi_{192},
\]
with \(\mu_{192}>0\) a proved lower bound on the **full** complementary form. The existing analytic derivation C-0063–C-0065 gives the conditional implication from positive definiteness of this matrix to positivity of the constructed Suzuki-scaled Weil quadratic form on its stated form domain, hence on the original admissible test class where agreement is established.

The executed full mixed-Gram Arb calculation (1024 bits; residual order \(K=32\); exact \(\eta=2^{-24}\); active prime powers \(\{2,3\}\)) produced outward 352-bit rational enclosures, a **strictly positive** complementary lower bound, and a conservative *matrix-order LOWER bound*
\[
 \underline S
 =\underline A_{192}-\underline\mu_{192}^{-1}\,\overline G_{\rm full}
 \ \preceq\ S_{\rm comb}.
\]
The full \(V/P/R\) mixed image terms, ordinary Legendre \(D_{192}^{-1}\) low-space projection, and full Suzuki residual \((1+\eta^{-1})\delta_K^2D_{192}\) were retained.

**A separate exact rational checker**, starting from the serialized complete dyadic matrix packet and a complete invertible 48-bit dyadic rational congruence, rebuilt \(\underline S\), recomputed \(W\underline SW^\mathsf{T}\) and every exact Gershgorin row, and independently established **strict positive definiteness**. The minimum exact rational margin is retained in the witness and checked independently; decimal diagnostic approximately \(0.9999999993343024\). Floating-point eigenvalues or the numerical Cholesky proposal were **not** used as proof.

**Final classification: `POSITIVE_CANDIDATE`, PRE-THEOREM.** This is a positive finite-support **research** result under the stated analytic/Arb source premises, not a closed independently admitted theorem and not RH. The other three sign classifications (`NEGATIVE_CRITERION`, `NUMERICALLY_UNRESOLVED`, `MATHEMATICALLY_INCONCLUSIVE`) do not describe this executed case. An `EXECUTION_INCOMPLETE` operational classification is also inapplicable: the exact proof completed and all processes were cleaned up.

## 2. Independent evidence and proof boundaries

| Requirement | Disposition |
|---|---|
| Retained positive control and scoped regressions | **PASS** — unchanged one-prime \((7/20,32)\), expected arithmetic term \(\{2\}\), and 44/44 focused tests |
| Fixed inputs and full residual | **PASS** — exact \((T,N)=(11/20,192)\), 1024-bit Arb, \(K=32\), \(\eta=2^{-24}\), active \(\{2,3\}\), \(\underline\mu_{192}>0\) |
| Full mixed-image Gram and projection | **PASS in source-level research implementation** — all nine ordered \(V/P/R_K\) image pairings and all prime-power crosses, correct unnormalized \(D^{-1}\) |
| Matrix containment / conditioning | **PASS** — outward rational packet passed width gate \(2^{-128}\); full residual bound included |
| Complete rational evidence | **PASS** — all 18,528 upper-triangular input bounds for each of two matrices, \(\mu,\delta\), basis/parameters and source fingerprints |
| Independent exact sign determination | **PASS** — entire \(\underline S\) reconstructed and positive exact rational congruence margins independently recomputed |
| Independent analytical source spot checks | **PASS within stated scope** — Suzuki formula, differentiation of cell primitives, low-form/complement references, historical finite-tail compatibility and high-degree *nonproof* quadrature |
| Independent closed all-entry transcendental verification | **NOT ESTABLISHED** — no separate closed evaluator proves every \(N=192\) Arb matrix enclosure; analytic source-trust remains |
| Equality of all canonical source Friedrichs operator/form domains | **NOT ESTABLISHED** — not needed for the documented implication to the original admissible test functions, but do not assert it |
| New theorem/certificate/Rust/Lean admission | **NOT ATTEMPTED; PROHIBITED in this run** |
| Global positivity for all supports / RH | **NOT ESTABLISHED** |

**Important interpretation:** independent exact rational agreement does **not** by itself prove that every transcendental input enclosure is analytically valid. The primary generator, previous mathematical derivations, and source audit supply arguments for these bounds, but the closed all-entry verifier gate remains separate. Accordingly the result is not promoted into the public theorem ledger or v2 accepted theorem list. The original negative results for the **different factor-3 sufficient bound** remain valid and logically compatible with this positive combined criterion.

## 3. Immutable artifacts and bounded stop

Original executed full rational input: [`matrix-N192.json.gz`](../computations/2026-10-17T150153Z-combined-schur-bounded-test/data/matrix-N192.json.gz), SHA-256 `655d481d638f8b6fba0f95d01a4bab45079d905fbc6cb4f3e822571729d4d7c1`.

Exact rational positive congruence witness: [`positive-witness-N192.json.gz`](../computations/2026-10-17T150153Z-combined-schur-bounded-test/data/positive-witness-N192.json.gz), SHA-256 `d9130344b09978fe84026dff0cbe3bf54cbda4c0603828af9f36cc84a32fc48f`.

Original independent exact rational checker result: [`independent-exact-check-N192.json`](../computations/2026-10-17T150153Z-combined-schur-bounded-test/data/independent-exact-check-N192.json), SHA-256 `4132b23ee9017553a878887bfbc96e54db7cb0d2b8d182fb3e9c8cd8c7316e65`. Audited replay: [`independent-exact-check-N192-audited.json`](../computations/2026-10-17T150153Z-combined-schur-bounded-test/data/independent-exact-check-N192-audited.json), SHA-256 `23f0d79fd8d54fe2890da97a2a4335821b04dfdbfc33463873bb394c1e81809c`.

Separate analytical source-control result: [`source-audit-N192.json`](../computations/2026-10-17T150153Z-combined-schur-bounded-test/data/source-audit-N192.json), SHA-256 `0228929f8ca5d884816897e3b7624e395db0c0cf13f9ac72175e1dfadee6fa10`.

The complete reproduction commands, source revision/fingerprints, exact numerical inputs, verifier scope, witness-construction history and earlier termination details are retained in X-20261017-003 and X-20261017-004. The primary Arb calculation completed in **114.83 s**; the separate rational check and the subsequent hardened audit replay succeeded. An unproductive exact-LDL *witness generation* method was stopped with its process tree confirmed absent; it did not invalidate the mathematical result.

**Stop rule honored:** No \(N=196\) sign experiment was executed after the independently exact-positive \(N=192\) result. No additional support/dimension search, precision escalation, theorem promotion, certificate architecture, or infrastructure overhaul followed. The original source packets and their fingerprints were not altered by the later input-validation hardening.

## 4. Closure gate

**The bounded experiment is CLOSED as `POSITIVE_CANDIDATE`**, because the preregistered input controls, complete rational enclosure evidence, positive full complement, strict independently checked exact rational congruence, honest analytic trust classification, record integrity and process-cleanup conditions are met.

**The larger proof/admission gate is OPEN**, not silently satisfied: a genuinely independently closed all-entry transcendental/source enclosure acceptance (and any separately required source/test-class domain checks) has **not** been established. This is a statement of the evidence boundary, **not** authorization for additional experiments or machinery.

The result establishes no RH resolution and leaves frozen one-prime v1 theorems and generic multi-prime v2 admission semantics unchanged.
