# v3 combined-Schur verifier: real two-gate research PASS, no theorem admission

- **Finding ID:** F-20261017-016
- **Created:** 2026-10-17T22:43:10Z
- **Last updated:** 2026-10-18T00:42:00Z
- **Type:** Closed proof-profile implementation and independent mathematical replay
- **Status:** **REAL RESEARCH TWO-GATE PASS; CLEAN PROOF-BEARING VERIFICATION PENDING**
- **Computation:** [X-20261017-007](../computations/2026-10-17T222400Z-v3-research-bundle/record.md)

A strictly separate `rh-weil-certificate-v3` profile was implemented for the **complete combined** \(V+P_2+P_3+R_K\) Gram and fixed exact \(T=11/20,N=192\), not the frozen v1 rule or the existing v2 factor-three grouped criterion. Its source producer and validator encode all 37,056 352-bit dyadic rational input intervals, full residual and complement, and the original invertible exact dyadic congruence.

**Actually executed:** a separate 2048-bit Arb evaluator recomputed and strongly contained **all 37,056** analytical entries plus the complementary/residual bounds in the exact v3 research artifact; a newly implemented **zero-float Rust integer-arithmetic congruence** reproduced the **same strict positive exact rational Gershgorin margin** as the earlier research proof. The source and rational proof checks were executed as distinct verification gates on the same certificate bytes, not inferred from source hashes or generator status flags. Python focused checks 34/34 passed and the Rust suite 73/73 passed.

Production v3 admission remains explicitly **EMPTY**: ordinary theorem verification rejects this candidate, and the clean-source producer refuses uncommitted provenance. Existing eight v1 theorems, unrelated v2 semantics and its empty admission list are unchanged.

**Later hardening/replay (2026-10-18):** [`X-20261018-001`](../computations/2026-10-18T004000Z-v3-gate-hardening-replay/record.md) bound both independent gates to one immutable input byte snapshot, hardened clean/research generator provenance and result identity, and repeated complete Arb-2048 analytical containment plus exact Rust rational congruence successfully. 37/37 focused Python tests, 73/73 Rust tests and a full-profile synthetic negative rational test passed. The historical clean-proof completion condition is still open: a new clean committed source artifact has not been generated or accepted. The earlier implementation and mathematical proof status below remain research-only.

**The code-level research and verification gates have been exercised successfully.** A **fresh clean-source proof-bearing candidate and final two-gate replay have not been executed** and are not represented as completed. No new theorem is admitted, no new support value is established, and RH is unresolved.
