# Admit exactly one combined mixed-Gram finite-support Weil theorem

- **Finding ID:** F-20261018-002
- **Created:** 2026-10-18T07:18:03Z
- **Last updated:** 2026-10-18T07:18:03Z
- **Type:** INDEPENDENTLY ACCEPTED DERIVED FINITE-SUPPORT THEOREM / EXPLICIT ADMISSION DECISION
- **Status:** **VERIFIED WITH EXPLICIT ANALYTIC TRUST BOUNDARIES; SYS-5.4 ADMISSION PASS**
- **Evidence:** [X-20261018-003](../computations/2026-10-18T071550Z-v3-retained-admission/record.md), [X-20261018-002](../computations/2026-10-18T010000Z-v3-clean-proof-candidate/record.md).
- **Claim:** `C-0067`. RH remains unresolved.

## Precisely admitted assertion

Let \(T=11/20\). In Suzuki's normalization of the localized Weil quadratic form \(Q_W\), **there exists \(\varepsilon_T>0\)** such that
\[
Q_W(f)\ge\varepsilon_T\|f\|_{L^2(-T,T)}^2
\quad\text{for every }f\in C_c^\infty(-T,T).
\]
This concerns one *fixed* support and test class, not all supports, a zero-free theorem of unstated range, canonical Friedrichs-operator domain equality, or the Riemann Hypothesis.

## Independent mathematical and mechanical chain

The closed-form Hilbert-space statement and exact mixed-Gram sufficient Schur reduction are `C-0063..C-0065`. The clean independently rederived \(N=192\), \(K=32\), \(\eta=2^{-24}\) proof input has full 352-bit outward dyadic bounds, a strictly positive full-tail complement and a bounded Suzuki residual. A distinct Arb-2048 evaluation independently strictly contains all 37,056 exact interval inputs and the complementary/error bounds. A separate zero-float Rust exact-rational replay confirms the positive conservative full combined-Schur lower matrix via invertible parity-preserving congruences and **strict positive exact Gershgorin**. The resulting form-Schur coercivity implication proves the stated test-class positivity under the explicitly recorded analytic trust model.

**Explicit admission decision:** Accept only the `C-0067` `rh-weil-certificate-v3` / `combined_multi_prime_legendre_schur` proof at `T=11/20,N=192`, original SHA-256 `f9948f22010d258d1c01c988fd0f18a3110c3c13453473c8c48953560a7fffcb`. The Rust production whitelist binds this one exact certificate's raw bytes; a separate independently accepted retained registry binds claim ID, path, source commit, analytical source SHA and scope. Both gates must pass; manifest metadata or mere source hashes are never counted as proof.

The original frozen v1 eight theorems `C-0050..C-0057` and their manifest remain unchanged. V2 has zero admitted configurations. Lean's elementary `Cert.CombinedSchur` Young/row-absorption soundness supporting lemmas are **not** a Lean proof of the entire Suzuki source identity, full matrix enclosure, or the theorem itself; the admitted evidence is source-analytic Arb plus exact Rust replay, with clearly delimited trust.

No untested \(N\), nearby \(T\), all-\(T\) positivity, canonical domain equality or RH follows. Public historical research stages that reported an empty v3 whitelist were accurate **at those earlier times**; they do not override this later explicit admission record.
