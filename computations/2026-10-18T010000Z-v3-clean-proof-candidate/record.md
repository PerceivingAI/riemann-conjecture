# X-20261018-002 — Clean committed-source v3 combined-Schur proof-bearing candidate and final two-gate replay

- **Created:** 2026-10-18T00:58:36Z
- **Last updated:** 2026-10-18T00:58:36Z
- **Type:** SOURCE-REPRODUCIBLE_PROOF_CANDIDATE / INDEPENDENT_ANALYTICAL_AND_EXACT_RATIONAL_REPLAY
- **Status:** **PASS — SYS-5.3 CLEAN PROOF-BEARING VERIFICATION COMPLETED; NO THEOREM ADMITTED**
- **Source revision:** `f0350f89ec5189648cfc271c4ddd3a97355a2343` on `main` / `origin/main`; worktree fully clean before producer execution.
- **Mathematical scope:** exact `T=11/20,N=192,K=32,eta=1/16777216` in the ordinary unnormalized Legendre basis; only `m=2,3` active.
- **Related closure finding:** [F-20261018-001](../../findings/2026-10-18T005836Z-clean-combined-schur-proof-bearing-closure.md).
- **Historical evidence:** [X-20261017-003](../2026-10-17T150153Z-combined-schur-bounded-test/record.md), [X-20261017-006](../2026-10-17T215700Z-sys5-full-analytic-acceptance/record.md), [X-20261018-001](../2026-10-18T004000Z-v3-gate-hardening-replay/record.md).

## 1. Clean source revision and actual generation

The previously uncommitted SYS-5.1/SYS-5.3 source, data, tests, Rust/Lean modules and public documentation were committed as `f0350f89ec5189648cfc271c4ddd3a97355a2343`, pushed to GitHub `origin/main`, and independently compared with the remote head. The worktree status was **clean** before running the producer; private `notes/` remained Git-ignored and unpublished.

The fresh proof-bearing producer executed:

```text
uv run --locked python -m scripts.cert.export_combined_schur_v3_clean --output computations/2026-10-18T010000Z-v3-clean-proof-candidate/data/certificate-v3-clean.json
```

**Exit 0** with process cleanup. It did **not** merely relabel the old dirty research artifact. It **recomputed** the full finite-support Arb 1024-bit matrix packet (118.41 s), regenerated an invertible rational dyadic congruence witness with a strictly positive **exact rational** Gershgorin margin, and independently reassembled the complete low/mixed-Gram analytical inputs at Arb 2048 bits (54.609 s).

Both freshly generated source artifacts matched the previously retained immutable research evidence *byte-for-byte*:

- Regenerated compressed rational matrix SHA-256 `655d481d638f8b6fba0f95d01a4bab45079d905fbc6cb4f3e822571729d4d7c1`.
- Regenerated compressed exact congruence witness SHA-256 `d9130344b09978fe84026dff0cbe3bf54cbda4c0603828af9f36cc84a32fc48f`.

The generator's full-tail complementary bound was **strictly positive** (lower diagnostic ≈ `0.5662083067859621`); the full residual bound ≈ `9.828028288169228e-16`; the rigorous matrix interval-width gate passed. Every regenerated analytic input interval was strictly contained in the fresh packet's stored rational bounds, and the complementary/residual scalar checks passed.

## 2. The new, genuinely clean proof-bearing candidate

Actual generated file: [`data/certificate-v3-clean.json`](data/certificate-v3-clean.json).

- **Size:** 4,438,069 bytes
- **SHA-256:** `f9948f22010d258d1c01c988fd0f18a3110c3c13453473c8c48953560a7fffcb`
- **Schema:** `rh-weil-certificate-v3`; `claim_profile=combined_multi_prime_legendre_schur`.
- **Exact claim identity:** `research-combined-schur-T11-20-N192` (research candidate identifier, **not** a new admitted `C-####` claim).
- **Generator:** `scripts/cert/export_combined_schur_v3_clean.py` at clean committed `f0350f89ec5189648cfc271c4ddd3a97355a2343`.
- **Provenance:** `clean_candidate_pending_admission`, `git_dirty=false`; embedded original source packet and witness hashes as above.
- **Matrix evidence:** all 18,528 low-form and 18,528 full combined-Gram outward dyadic rational intervals, positive complement, full Suzuki residual and complete exact 48-bit dyadic congruence.

This file was created **after** the clean-source gate and does not retrospectively change the historical `research_uncommitted_not_proof_bearing` artifact or its status.

## 3. Separate final two-gate acceptance on the actual clean certificate

Command:

```text
uv run --locked python -m scripts.verify_combined_schur_v3_bundle --candidate computations/2026-10-18T010000Z-v3-clean-proof-candidate/data/certificate-v3-clean.json --rust-binary target/debug/rh_cert.exe --output computations/2026-10-18T010000Z-v3-clean-proof-candidate/data/two-gate-audit-clean.json
```

**Exit 0.** The verifier confirmed the certificate's recorded clean Git revision matches `HEAD` and the source tree was clean **except for the newly generated proof file itself**. It parsed the same exact captured certificate bytes for source Gate A and an immutable snapshot handed to Rust Gate B, including SHA-256 checks before and after Rust execution.

- **Gate A — independently justified analytical inputs:** separate rigorous Arb 2048-bit calculation rederived and strictly contained **18,528/18,528 low** plus **18,528/18,528 full mixed-Gram** intervals; complementary \(\mu\) and full Suzuki residual \(\delta\) intervals both contained. **Zero mathematical input failures.** Fresh second source-assembly time: 52.423 s.
- **Gate B — independent zero-floating-point Rust rational proof:** reconstructed the complete conservative Schur lower matrix with signed mixed prime-power interactions, strict Loewner row-radius inflation, \(D_N\)-weighted full residual Young correction, certified positive complement, and exact integer-scaled even/odd congruences. Every exact Gershgorin margin is positive. The minimum **exact rational** margin equals the original SYS-4 witness value, not merely its sign or approximate decimal (~`0.9999999993343024`).
- **Both gates were bound to the same candidate SHA-256**, same canonical input digest `6c5afa8958cc47750290776ce3cd59cd7873a34d03d148fcfa8e90afb69aea63`.
- **Admission:** `NOT_PERFORMED`, `theorem_admitted=false`; Rust analytic-source status remains external to its exact arithmetic checker.

Machine-readable result: [`data/two-gate-audit-clean.json`](data/two-gate-audit-clean.json), **1,819 bytes**, SHA-256 `b5eaa805933a967357d01d46c684f1a7e5e2444f145eef7defc1994178bc321f`.

Independent Rust binary SHA-256 (as executed): `b4c53bb19fed520e80a720096b4ba74564c758fe21358559f32fa0f8cc103434`. Independent analytical verifier source SHA-256: `15961f4b337e1d26cc63aa41bcb3976fa975636d0b5e006b0f51bd3d625576e4`.

## 4. Admission and theorem boundaries

The normal production command `cargo run -p rh_cert -- verify --cert ... --json` was explicitly tested on **this clean candidate**. It returned **exit 2**, rejecting the attempted theorem verification because `v3` production admission is still empty. This is an **expected policy PASS**, not a failure of the research mathematical proof.

Pre-commit targeted regressions passed: **38/38 Python** (including full-size synthetic negative v3 control), the **complete Rust suite** (all test targets), and 447 local documentation links without missing targets; staged Git whitespace checks passed. Prior narrow Lean `lake build Cert` passed, and its tested sources were included in the clean committed revision. No v1/v2 theorem semantics, retained old certificates, v2 grouped-factor-3 proof rule, or whitelist was changed.

**Final classification: SYS-5.3 CLEAN PROOF-BEARING REPLAY COMPLETE / MATHEMATICALLY VERIFIED AT THE NAMED CONFIGURATION / NO THEOREM ADMITTED.**

The separate theorem-admission/retained-proof registration decision is **not** bypassed: this computation does NOT infer RH, support continuation, the equivalence of entire canonical Friedrichs operator domains, or any extension beyond the stated Suzuki smooth test-function class. The numerical trusted base remains documented Arb outward arithmetic plus the source's analytical identity; the exact rational consequences are independently checked.
