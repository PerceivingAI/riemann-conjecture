# Fresh clean-source combined-Schur v3 proof candidate passes both independent gates

- **Finding ID:** F-20261018-001
- **Created:** 2026-10-18T00:58:36Z
- **Last updated:** 2026-10-18T00:58:36Z
- **Type:** FINITE_SUPPORT_MATHEMATICAL_PROOF_BEARING_CANDIDATE / CONDITIONAL_THEOREM_ADMISSION
- **Status:** **SYS-5.3 COMPLETE — CLEAN PROOF-BEARING VERIFICATION PASSED; NO NEW THEOREM ADMITTED**
- **Reproducible evidence:** [X-20261018-002](../computations/2026-10-18T010000Z-v3-clean-proof-candidate/record.md).
- **Clean source revision:** `f0350f89ec5189648cfc271c4ddd3a97355a2343`, pushed and matched to `origin/main`.

The previously unresolved SYS-5.3 clean-source gate is now **satisfied** for one fixed exact configuration, \(T=11/20,N=192,K=32,\eta=2^{-24}\). A clean Git checkout of the committed mathematical/Rust/Lean proof infrastructure regenerated the entire Arb-1024 rational input matrix and exact congruence **byte-for-byte** against the historical archived source and witness. A completely separate Arb-2048 analytic reconstruction strictly contained every one of the 37,056 low/combined-Gram scalar intervals and both complementary/residual scalar bounds.

The newly generated **honest clean-source** `rh-weil-certificate-v3` has SHA-256 `f9948f22010d258d1c01c988fd0f18a3110c3c13453473c8c48953560a7fffcb`, with `provenance.status=clean_candidate_pending_admission`, `git_dirty=false` and a precise committed source fingerprint. An independent final replay against that **actual certificate**, binding the same immutable captured bytes to the analytical and Rust gates, returned full rigorous input acceptance and independently reconstructed exact rational Schur positivity with a minimum exact Gershgorin margin matching the original mathematical witness. The final audit SHA-256 is `b5eaa805933a967357d01d46c684f1a7e5e2444f145eef7defc1994178bc321f`.

This is evidence for the **precisely scoped finite-support Suzuki/Weil smooth-test-class positivity statement** under the documented sound Arb/source-analytic assumptions. It does **not** constitute automatic admission into the repository's formally governed theorem whitelist: the normal Rust production `verify` path explicitly rejected the clean v3 candidate because the v3 admission list remains empty. Previous eight v1 retained theorem profiles and unrelated factor-three v2 semantics remain frozen. There is **no** RH proof and no assertion for untested support values or equality of entire canonical source operator domains.

**Disposition:** The specific clean proof-bearing *engineering and mathematical acceptance* completion gate of SYS-5.3 is satisfied. Any explicit new theorem admission, retained-proof registration and separate admission/acceptance soundness decision remain unperformed; no theorem was auto-promoted.
