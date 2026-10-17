# Current Tooling Capabilities and Verification Boundaries

- **Audit:** SYS-1 current-state technical inventory
- **Audited repository revision:** `20a691105ec808e623faef2fc5bbaf4806a0d352` (`main`, 2026-10-08 commit)
- **Audit date:** 2026-10-17
- **Scope:** Implemented Python/Arb mathematics, Rust, Lean, execution/orchestration, retained evidence and agent navigation
- **Disposition:** Public technical record of *existing* behavior only; not a research strategy, roadmap, or tooling-upgrade register
- **Method:** Read current source, tests, schemas, contracts, and retained verification records; independently execute the checks listed in §8

This audit describes the source tree at the pinned revision. An implemented function, a prior passing test, a freshly passing test, an external mathematical premise, and an admitted theorem are different forms of evidence. They are not interchangeable.

The audit did **not** edit or regenerate any historical attempt, finding, computation, or retained certificate. It did **not** run a new mathematical qualification sweep.

## Post-audit research capability addendum — 2026-10-17T14:44:16Z

**This is a separate, later source-evidence addendum** to the pinned SYS-1 audit above, not a claim that its original \`20a6911...\` revision already contained this capability. Research-only \`scripts/cert/mixed_gram_research.py\` now assembles rigorous ordered \(V/P/R_K\) low-image cross terms and a combined truncated low-to-tail Gram, converts entrywise Arb intervals into exact rational Loewner upper bounds, and includes the *full* Suzuki residual through a rigorous \(\delta_K^2D_N\) Young allowance. A separate conditional lower-Schur matrix routine requires certified \(\mu_N>0\); it neither verifies positive definiteness nor exports a certificate.

**Evidence:** [\`F-20261017-009\`](../findings/2026-10-17T142253Z-combined-mixed-gram-implementation-and-validation.md) / [\`X-20261017-002\`](../computations/2026-10-17T142253Z-mixed-gram-implementation/record.md) document earlier source-level implementation, independent reference checks and actual precision/conditioning measurements at \`N=128/192/196\`. Later independent review [\`F-20261017-010\`](../findings/2026-10-17T144247Z-independent-mixed-gram-verification-and-tooling-closure.md) hardened non-rational Young parameters and malformed/asymmetric input-matrix rejection, with **40/40** focused new/overlap tests and a matching post-correction \`N=64\` precision check. All large-dimension widths remain honest **as-run evidence** from the earlier source snapshot, not false replays of the amended hash. **Labels:** \`SOURCE-VERIFIED\`, \`TESTED-CURRENT\` for focused controls, \`GENERATOR-SIDE\`. **NOT ESTABLISHED:** full combined-Schur sign at any support, independent Rust/Lean checking of this new analytical input, theorem/certificate admission or RH. Frozen v1/v2 interfaces and their admitted outcomes remain unchanged.

## 1. How to read this inventory

| Label | Meaning |
|---|---|
| `SOURCE-VERIFIED` | Operation and restrictions inspected in the audited source. This alone is **not** a fresh correctness test. |
| `TESTED-CURRENT` | Applicable tests completed successfully in this audit at the pinned source revision. |
| `RETAINED-EVIDENCE` | Earlier execution is recorded in the public repository; not replayed merely by reading it. |
| `FORMAL-LOCAL` | Exact theorem declaration in the locally pinned Lean project, with build status recorded separately. |
| `GENERATOR-SIDE` | The generator or candidate auditor produces evidence under its stated analytical assumptions; it is not theorem admission. |
| `EXTERNAL` | Attributed result whose proof is maintained outside this repository; independent local replay is separately recorded. |
| `NOT-ESTABLISHED` | The relevant behavior has not been established by the evidence cited here. |

A capability can carry several labels (e.g., `SOURCE-VERIFIED`, `TESTED-CURRENT`, and `GENERATOR-SIDE`). All statuses are scoped to the specific object, inputs, and trust layer.

## 2. Mathematical computation — Python / Arb

| Present operation | Source / entry point | Scope and current evidence |
|---|---|---|
| Frozen one-prime Legendre–Schur calculations | `scripts/cert/legendre_schur.py`; `scripts/cert/exact_prime_schur_certificate.py`; `scripts/weil_continuation_driver.py` | Exact-rational Legendre operations with rigorous Arb enclosures; closed proof export for the eight admitted `(T,N)` pairs. Source guarded by `tests/test_one_prime_v1_freeze.py`, `tests/test_exact_prime_schur_certificate.py` and retained-proof tests. `SOURCE-VERIFIED`. |
| Exact prime-power identities and activity | `scripts/cert/prime_power_terms.py::factor_prime_power`, `enumerate_active_prime_power_terms` | Exact integer recognition of `m=p^k`; rigorous strict `log(m)<2T` decisions with fail-closed unresolved thresholds. `tests/test_prime_power_terms.py`. `SOURCE-VERIFIED`. |
| Combined arithmetic operator | `scripts/cert/prime_power_terms.py::assemble_combined_prime_power_operator`, `assemble_active_prime_power_operator` | Piecewise local Legendre images, normalized compressed translations; computes combined `P`, operator-square low matrix `P_squared`, and `GP=P_squared-PD^{-1}P`. The combined square includes cross-prime terms. Tests cover frozen one-prime overlap, nonzero cross term, `m=4`/small-shift geometry, basis validation and threshold uncertainty. `SOURCE-VERIFIED`. |
| Multi-prime grouped Schur assembly | `scripts/cert/multi_prime_legendre_schur.py::assemble_multi_prime_schur` | Returns `active_terms`, `P`, `P_squared`, `A`, `GV`, `GP`, `GR`, `delta_R`, `rho_R`, `mu` and `schur` when `mu>0`. Uses grouped `V,P,R` and factor `3`. `tests/test_multi_prime_legendre_schur.py`, `tests/test_multi_prime_potential_grouping.py`, `tests/test_multi_prime_p4_stages.py`. `SOURCE-VERIFIED`. |
| Residual approximation and bounds | `scripts/cert/residual_kernel.py`; `scripts/cert/multi_prime_legendre_schur.py::_residual_truncation_operator`, `_residual_rho` | The series truncation `Rk` is distinguished from its remainder; assembled `GR` and `rho_R` include conservative remainder control. The truncated polynomial operator alone is **not** identified with the full residual. `SOURCE-VERIFIED`. |
| Interval constants, outward rationalization | `scripts/cert/constants.py`, `scripts/cert/matrices.py`, `scripts/cert/exact_prime_schur_common.py` and candidate/exporter call sites | `python-flint` Arb/ACB enclosures feed exact dyadic rational endpoints and witnesses. Float reconnaissance does not enter certificate arithmetic. `tests/test_cert_pipeline.py`, `tests/test_multi_prime_precision_diagnostics.py` and certificate tests. `SOURCE-VERIFIED`. |
| Native exact rational witnesses | `scripts/cert/multi_prime_exact_witness.py::make_witness` | Fraction-free integer elimination, dyadic rounding, native exact midpoint/radius congruence and strictly positive Gershgorin margins; rejects nonpositive pivots/margins. `tests/test_multi_prime_exact_witness.py` covers reference equivalence, precision and failure cases. `SOURCE-VERIFIED`. |
| Independent candidate arithmetic audit | `scripts/audit_multi_prime_candidate.py::audit_candidate_inputs` | Reconstructs rational complement/Schur and margins from serialized candidate inputs with separate exact arithmetic. This is a **pre-theorem** consistency audit; it does not establish the upstream transcendental Arb enclosures. `tests/test_multi_prime_candidate_audit.py`. `SOURCE-VERIFIED`, `GENERATOR-SIDE`. |

**Explicit current domains.** The standalone arithmetic operator core handles more general prime-power activity than the **multi-prime continuation driver**, which is deliberately restricted to the first `{2,3}` window `log(3)/2 < T < log(4)/2`. The v1 theorem exporter has exactly eight admitted `(T,N)` configurations. These are distinct interfaces; support in one does not imply end-to-end admission in another.

**Proof meaning.** An Arb enclosure is rigorous only under the implemented mathematical formulas, operator normalizations and analytical estimates used to construct it. Independent checking of serialized rational arithmetic does not rederive those formulas or transcendental input bounds.

## 3. Rust: exact verifier and numerical engine

| Present operation | Source and checks | Scope and boundary |
|---|---|---|
| Format routing | `crates/rh_cert/src/dispatch.rs`; `tests/test_admission_consistency.py` | Dispatches `rh-weil-certificate-v1` to frozen `cert.rs` and `rh-weil-certificate-v2` to `v2.rs`; unsupported/malformed inputs fail closed. |
| Canonical exact interval arithmetic | `crates/rh_cert/src/interval.rs`; `crates/rh_cert/tests/test_interval.rs` | Pure Rust `BigInt/BigRational` arithmetic, rational syntax/endpoint checks; crate declares `#![deny(clippy::float_arithmetic)]`. No native GMP/MPFR verifier bindings. |
| Positive-definiteness primitives | `crates/rh_cert/src/ldl.rs`, `gershgorin.rs`; corresponding unit/proptest suites | Exact interval LDL and rational congruence/Gershgorin positivity; strict margins, matrix/witness dimensional and structural restrictions. |
| Frozen v1 theorem profile | `crates/rh_cert/src/cert.rs`; `crates/rh_cert/tests/test_exact_prime_schur.rs`; `tests/test_one_prime_v1_freeze.py` | Closed `exact_prime_legendre_schur` grid: `(7/20,32)`, `(2/5,40)`, `(17/40,48)`, `(9/20,56)`, `(19/40,68)`, `(1/2,80)`, `(21/40,96)`, `(27/50,104)`. The verifier recomputes the exact rational complement, Schur and parity-witness predicate. |
| V2 structure and theorem gate | `crates/rh_cert/src/v2.rs`; `scripts/cert/certificate_v2_contract.py`; `docs/contracts/rh-weil-certificate-v2.json`; `crates/rh_cert/tests/test_certificate_v2.rs`; `tests/test_v2_adversarial_consistency.py` | First v2 window enforces active terms `[2,3]`, rational threshold/parity/term relations, `b_m=1` and grouped factor `3`. **Production v2 theorem whitelist is empty** in Rust, Python and schema admission. Structural validation is not theorem admission. |
| CLI outcome semantics | `crates/rh_cert/src/main.rs`; verifier acceptance tests | Exit `0` for accepted proof, `1` for valid but nonpositive theorem predicate, `2` for contract/parse/execution verification errors. |
| Independent verifier boundary | `crates/rh_cert/src/cert.rs`, `v2.rs`; `docs/CONTRACTS.md` | Independently recomputes rational consequences of serialized enclosures and proofs. **Does not independently certify the analytic derivation or the truth of the generator-side transcendental Arb enclosures.** |
| Separate high-throughput engine | `crates/rh_engine/src/{sieve,laguerre,trace,bins,phase,summation}.rs`; `crates/rh_engine/src/main.rs` | Rayon-based numerical prime/Laguerre trace, prime-power sieve, turning-scale bins, phase tools, floating exploration and benchmark CLI; **not** the zero-float proof verifier. |

The Python schema checks, semantic validator, Rust verifier and test-only corpora have separate roles. The test-only acceptance corpora under `tests/data/` do not grant production theorem admission.

**Recorded verifier performance (not freshly benchmarked):** [`X-20260827-003`](../computations/2026-08-27T134254Z-rust-exact-verifier-optimization/record.md) documents the exact Rust verifier optimization and input-specific replay timings, including `N=68` at 31.408 s. The performance record is historical evidence, not a guaranteed runtime for other certificate sizes. No current performance failure was reproduced in this audit.

## 4. Lean: exact locally formalized statements

The local formal project pins **Lean `v4.33.0`** and Mathlib `v4.33.0` in `formal/lean-toolchain` and `formal/lakefile.lean`. The umbrella module `formal/Cert.lean` imports four local modules:

| Module | Examined declarations and actual scope |
|---|---|
| `Cert.Interval` | `RatInterval`, rational enclosure-preserving arithmetic; includes `mul_contains`, `inv_contains`, `div_contains`, `sqr_contains`, `strictly_positive_sound`. |
| `Cert.LDL` | Finite-dimensional `ldl_posDef`, `interval_ldl_posDef` for **supplied factorization and enclosure hypotheses**. |
| `Cert.Gershgorin` | `strictPositiveRowDominant_posDef` and `posDef_of_invertible_congruence` for finite symmetric matrices. |
| `Cert.EndpointAbsorption` | Bounds on endpoint coefficients and `first_prime_absorption`, conditional on supplied energy/potential/prime inequalities. |

`SOURCE-VERIFIED` for the declarations and their hypotheses. A successful local `lake build` checks the exact declarations in the imported target, **not** an external analytic operator theorem, Arb transcendental enclosure generation or arbitrary serialized certificate.

**External distinction:** The source-pinned external `EXT-0001` OpenAI theorem uses a separate Lean **4.34.1** environment. Its local Comparator replay is recorded as **NOT PERFORMED** in `references/external-results/`; the reference-only theorem and local written consequences are not local Lean declarations or local Rust certificate PASS.

## 5. Research execution and orchestration

| Current capability | Source | Relevant verification coverage |
|---|---|---|
| Canonical one-prime continuation | `scripts/weil_continuation_driver.py` | Scout → rigorous Arb full-tail precision → exact candidate → fixed-input confirmation; explicitly stops at pre-theorem status. `tests/test_continuation_driver.py`, `test_continuation_integration.py`. |
| Separate multi-prime continuation | `scripts/weil_multi_prime_continuation_driver.py`, `scripts/weil_multi_prime_support_continuation_scout.py` | Strict first `[2,3]` support window; independent stage selection, precision/matrix/witness ladders and pre-theorem terminal states. `tests/test_multi_prime_continuation_driver.py`. |
| Concurrency and deterministic outputs | Both drivers; `scripts/run_observability.py` | Spawn-based bounded process pools, `as_completed` observation, canonical result ordering, tracked worker lifecycle; relevant driver/parallel acceptance tests. |
| Live status and exclusive ownership | `scripts/run_observability.py` | OS-backed output-directory lock, run identity, heartbeat, event JSONL, atomically replaced status/failure records; `tests/test_run_observability.py`. |
| Worker recovery and process cleanup | `scripts/run_observability.py::WorkerCleanupVerifier`; driver executor guards | Join → terminate → kill escalation for owned workers, reaping verification and fail-closed cleanup; `tests/test_run_observability.py`, continuation-driver tests. |
| Reproducible cache identity | Both drivers; `scripts/continuation_bundle.py` | Source fingerprints, keyed cached mathematical payloads, corrupt-cache rejection, atomic publication and runtime Git provenance; `tests/test_continuation_bundle.py`, driver tests. |
| Immutable pre-theorem evidence bundle | `scripts/continuation_bundle.py::write_continuation_bundle` | Stage artifacts, digest/size manifest, manifest-last sealing, cleanup validation and explicit prohibition on theorem status; `tests/test_continuation_bundle.py`, `tests/test_pre_theorem_boundary.py`. |
| Current profiling/diagnostics | `scripts/profile_multi_prime_assembly.py`, `profile_multi_prime_conditioning.py`, `profile_multi_prime_workflow.py`, `multi_prime_precision_diagnostics.py` | Stage-specific measurement and enclosure diagnostics. The historical measured input-specific results remain in the retained computation records; they were not rerun here. |

`CANDIDATE_READY` is **not** an admitted theorem. A driver does not edit admission lists, manufacture claims or call a theorem exporter as a promotion mechanism.

**Recorded multi-prime performance (not freshly benchmarked):** [`X-20261001-001`](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md) records Arb-512 assembly at `N=192/196` in 23.183/24.983 s, the two-worker rigorous screen in 109.598 s, and the native exact witness candidate example in 53.525 s (versus 541.946 s for its earlier implementation). These are historical, machine- and input-specific observations. Other runtime/memory claims remain `NOT-ESTABLISHED` unless supported by their own measurements.

## 6. Research evidence and agent operating surface

| Capability | Authoritative source / implementation | Current contract |
|---|---|---|
| Agent onboarding and navigation | `AGENTS.md`, `README.md`, `scripts/README.md`, `docs/INDEX.md` | Links current tools, canonical workflows, tests and trust boundaries without requiring source discovery from scratch. |
| Mathematical claim identity and dependencies | `docs/CLAIMS.md`, `docs/PROTOCOL.md`, `docs/CONTRACTS.md` | Distinguishes claim type/status and dependencies; forbids conflating external, derived, formal and certificate evidence. |
| External attribution and source identity | `references/BIBLIOGRAPHY.md`, `references/external-results/` | Named external statements, immutable source identifiers and **separate** upstream/local verification status. |
| Historical research evidence | `attempts/`, `findings/`, `computations/`; `docs/LOG.md`, `docs/STATUS.md` | Timestamped historical evidence is preserved. Maintained status/claims/index documents summarize it without silently rewriting source records. |
| Closed retained proof identity | `computations/retained-proofs.json`; `scripts/cert/verify_retained_proofs.py` | Exactly eight canonical certificates, declared SHA-256 bytes and expected proof identities. Manifest-only checking is distinct from full current Rust replay. |
| Generator/proof non-promotion | `scripts/continuation_bundle.py`, `tests/test_pre_theorem_boundary.py`, `docs/CONTRACTS.md` | Candidate bundles are pre-theorem. Explicit theorem admission and independent certificate checking remain different operations. |
| Public documentation | `README.md`, `docs/`, tests and implementation modules | Describes actual source, verification, and completed observations. This audit contains no future project sequencing or upgrade selection. |

**Source-change detection:** Driver source fingerprints and Git run provenance provide change identity for computations; manifest byte hashes verify retained artifacts. Neither establishes a mathematical theorem without the relevant analytic and verifier arguments.

## 7. Exact proof/admission state at the audited revision

- **RH:** unresolved.
- **One-prime v1:** exactly eight admitted finite-support localized Weil theorem pairs `C-0050..C-0057`; `computations/retained-proofs.json` registers precisely those eight.
- **Multi-prime v2:** arithmetic/assembly/scouting/rigorous candidate/certificate structural validation and exact Rust predicate machinery exist; **no production theorem pair is admitted**.
- **Known v2 computation:** the retained exact negative directions at `T=11/20, N=192/196` reject the **particular grouped factor-3 sufficient Schur matrices**, not the full Weil form. This statement is from previously retained evidence, not a fresh recomputation.
- **External OpenAI result:** attributed external theorem `EXT-0001` and repository written deductions `C-0060..C-0062`; local replay not performed and no additional Weil theorem admission follows.

## 8. Verification evidence and coverage

**Current environment observed:** Windows; `uv 0.11.30`; `Python 3.14.0` (project requires Python >=3.12); `cargo 1.97.1`; local `leanprover/lean4:v4.33.0` installed. Tests below are evaluated at the audited revision and recorded as individual checks, not as a claim that unexecuted tiers passed.

| Verification | Result at audit closure |
|---|---|
| `git status --short --branch` at baseline | Clean `main...origin/main` before SYS-1 documentation changes |
| `uv run --locked --extra test python -m pytest -q -m "not integration and not slow_acceptance and not retained_proofs and not parallel_acceptance"` | **PASS**, 712/712 selected tests, 241.32 s, exit 0; excludes explicitly named test tiers |
| `cargo test -p rh_cert --locked --quiet` | **PASS**, 67 tests across the reported Rust suites, exit 0 |
| `cargo test -p rh_engine --locked --quiet` | **PASS**, 15/15 tests (11 unit + 4 integration), exit 0 |
| `cargo fmt -p rh_cert -- --check` | **PASS**, exit 0 |
| `cargo clippy -p rh_cert --all-targets --locked -- -D warnings` | **PASS**, exit 0 |
| `uv run --locked python -m scripts.cert.verify_retained_proofs --manifest-only` | **PASS**, `VALID (8 registered proofs)`. Does **not** replay certificate acceptance |
| `cd formal && lake build` | **PASS**, 8,711 jobs, exit 0, pinned Lean 4.33.0 environment |
| Full eight-certificate Rust replay | **NOT EXECUTED** in this audit |
| New expensive multi-prime rigorous qualification | **NOT EXECUTED** in this audit |
| Independent external Comparator replay | **NOT EXECUTED** in this audit |

**Historical verification records:** `docs/STATUS.md`, `scripts/README.md`, `computations/` and `research/openai-math/README.md` report previous focused/full Python/Rust/Lean gates, retained proof acceptance and documented performance results. Those dated records are not silently recast as fresh tests at this revision.

**Scope of acceptance:** This document inventories existing source behavior, current tests and accurately bounded proof claims. It is neither a new theorem, a correctness proof of every Python formula, nor a future implementation proposal.
