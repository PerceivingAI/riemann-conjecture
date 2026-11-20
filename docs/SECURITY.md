# First-party selected-arithmetic security review

- **First Created (UTC):** 2026-10-30T12:48:35Z
- **Last Updated (UTC):** 2026-10-30T13:15:26Z
- **Workflow Status:** complete
- **Scan Engine:** Portus reference fallback; targeted manual review and ordinary behavior validation
- **Guidance Sources:** repository artifact/ownership/independent-validation contracts; Python standard-library filesystem, JSON/gzip and subprocess boundaries; independent read-only first-party security review
- **Assurance:** Reduced: reference fallback. Codex Security plugin skills are unavailable. Bundled references target web frameworks not used by this CLI and are not claimed as applicable coverage.
- **Scope:** Uncommitted first-party whole-source implementation, selected arithmetic, bounded resource probes and observation verifier, CLI, focused tests and retained-evidence integration.
- **Exclusions:** Third-party libraries, generated/native dependencies, unrelated theorem/application tooling, private planning material, and modification of sealed historical computations. Historical artifacts are readable fixtures, not editable inputs.
- **Target State:** Uncommitted implementation after X-20261030-001; pre-existing work and deletions remain user-owned. Windows/Python3.14 runtime.

## Executive Summary

Three scoped first-party findings have code fixes: one high-severity analytical-cache trust failure and two medium-severity lock/provenance failures. Whole-slice writer exclusion and absent failed-worker profiles are also corrected. Ordinary behavior verification passes, including fresh and resumed six-entry arithmetic. Dedicated attack executions were excluded by the user. This audit does not claim complete repository security.

## Scope and Method

Reviewed complete producer/independent analytical formulas, contribution domains, physical masses, checkpoint/publication error payment, artifact parsing and bounds, coverage/recovery, writer ownership, subprocess capture and resource guards. An independent security reviewer examined the artifact/process integration read-only. Validation uses disposable local test data, actual owned tasks and ordinary API calls; no external targets, credentials or privilege escalation.

Explicit Python task programs and source roots are trusted executable configuration. This is not a sandbox against arbitrary trusted Python or malicious concurrent same-account writes. A prepared external cache is nevertheless data, not authority for its own mathematical truth.

The current audit follows the user's no-adversarial-execution constraint. Earlier reproduction evidence below predates this pass and was read, not rerun. Verification uses ordinary mathematical runs, compatible resume, writer exclusion and read-only retained-observation checks. No corruption, fabricated-cache, hardlink attack, native abort or process-interruption qualification is executed in this pass.

## Findings

### FPA-001 — Cached independent values can suppress independent reconstruction

- **Severity:** high
- **Status:** fixed
- **Impact:** New selected-arithmetic acceptance can certify incorrect cached entries; this undermines research acceptance, not production theorem admission.
- **Evidence:** `scripts/whole_source/slice.py::_pending_tasks` now unconditionally schedules all eight analytical term/window tasks; `_run_role` publishes their freshly staged chunks before checking final entries.
- **Guidance Source:** Portus reference fallback; independent read-only reviewer corroboration.
- **Attack Path:** A self-consistent prepared collection supplies false contributions for both roles. Exact reduction preserves those values; containment compares the cached values to each other instead of a fresh independently reconstructed value.
- **Recommendation:** Always reconstruct analytic signed-window quantities before every new acceptance, including resumed/recovered collections. Preserve producer caching and reject conflicts with cached analytic content.
- **Confidence:** high; actual coordinator reproduction completed.
- **Remediation:** Every analytical signed-window task is reconstructed on every acceptance. `ChunkStore.publish_chunk` compares the fresh bytes with any cached contribution and rejects conflicts; producer cache reuse remains supported.
- **Verification:** The disposable real coordinator run in computations/2026-10-30T124835Z-selected-arithmetic-review/data/before-dual-cache/verdict.json accepted all six fabricated near-zero entries. The actual constant entry is strictly negative: all active arithmetic coefficients are negative and both windows have positive length. No trusted program/configuration was altered by the test.
- **Current verification:** Fresh and compatible-resume CLI runs both return `VERIFIED_SELECTED_COMPLETE_ARITHMETIC`. Resume reuses all producer batches, freshly executes all eight analytical windows and reproduces all six exact entries and twelve quantity seals. All 16 fresh and 15 resumed owned stages report verified cleanup.
- **Remaining Risk:** Dedicated fabricated-cache execution was not repeated. The earlier reproduction remains historical evidence; the current executable proof covers ordinary fresh reconstruction and legitimate cached resume.
- **FINDINGS:** none; no blocked owner decision.

### FPA-002 — A multiply linked writable collection lock modifies unrelated data

- **Severity:** medium
- **Status:** fixed
- **Impact:** Opening a prepared collection lock can overwrite another writable local file on the same filesystem.
- **Evidence:** `scripts/whole_source/artifacts.py::_check_lock_file`, `CollectionLock.acquire` and `CollectionLock._check`.
- **Guidance Source:** Portus reference fallback; independent read-only reviewer corroboration.
- **Attack Path:** A prepared collection contains a regular hardlinked lock path. Symlink/reparse rejection does not reject it; lock metadata is written through the alias.
- **Recommendation:** Require a regular single-link opened lock before any write and retain that invariant during ownership checks.
- **Confidence:** high; actual temporary-file regression demonstrated unrelated content overwritten with lock metadata.
- **Remediation:** Require a regular, single-link lock descriptor matching the current path before acquiring ownership, before metadata writes and during subsequent owner checks.
- **Verification:** Earlier temporary-file failure evidence is retained. Current ordinary stable-inode ownership, exact persistence and compatible-resume regressions pass as part of 51 focused tests. The two hardlink regressions remain available but were not executed in this pass.
- **Remaining Risk:** Local data integrity, not privilege escalation or an OS sandbox guarantee. Same-account active filesystem races remain outside the threat model.
- **FINDINGS:** none; no blocked owner decision.

### FPA-003 — Observation receipts were not bound to their expected probe program

- **Severity:** medium
- **Status:** fixed
- **Impact:** Mutually consistent result/receipt/profile hashes could qualify an observation without identifying the required probe program. This affects resource provenance, not theorem admission.
- **Evidence:** `scripts/verify_bounded_resource_observations_v1.py::profile_for` and both observation loops.
- **Guidance Source:** Portus reference fallback; independent read-only first-party review.
- **Attack Path:** Cross-document hash agreement previously substituted for comparison with the expected first-party program's bytes.
- **Recommendation:** Compare each supervisor receipt and available profile with the expected program for that mode, before observation classification.
- **Confidence:** high; the original comparison omitted that identity.
- **Remediation:** All nine modes now bind receipts and available profiles to their expected current probe bytes. Successful results must agree with those same hashes.
- **Verification:** The ordinary read-only verifier returned `PASS_RETAINED_SCOPED_OBSERVATIONS` for all nine retained modes, with all recorded cleanups verified. No substituted-program demonstration was run.
- **Remaining Risk:** This verifies retained byte/provenance consistency, not authenticity against a malicious same-account writer or fresh numerical truth.
- **FINDINGS:** none.

## Remediation Queue

1. FPA-001: fixed. Fresh and compatible-resume CLI verification passes; all analytical windows execute again on resume.
2. FPA-002: fixed. Ordinary ownership/persistence regressions pass. Dedicated hardlink executions are excluded by the user's instruction.
3. FPA-003: fixed. All nine expected-program-bound retained observations pass read-only verification.
4. Correctness: whole-slice ownership spans context, status, both roles and final acceptance. The real two-process exclusion/reacquisition regression passes.
5. Correctness: failed supervisor receipts may lack a worker profile; successful observations still require one. Read-only handling of an existing natural allocation failure without a profile passes. No new worker failure was induced.

## Unknowns and Assumptions

- Hashes prove consistency with a bound expectation, not authenticity of a self-consistent external cache.
- Explicit Python executable inputs are trusted, not safely executable third-party plugins.
- Live non-Windows, sudden power loss, native-library soundness and full-source/T1 behavior are not established by this review.
- Six-entry acceptance remains distinct from a full source, positivity or production theorem admission.

## Residual Risk

No full-repository or dependency security scan is claimed. Dedicated security countercase execution is excluded from this audit; the two earlier reproductions remain historical evidence. Native source/enclosure premises and same-account active filesystem races remain outside the closure claim.

## Source Provenance

Baseline X-20261030-001 remains sealed and unchanged. Pre-review source is captured separately in computations/2026-10-30T124835Z-selected-arithmetic-review/before/. The original observation verifier is preserved there with sealed-manifest SHA256 `6af8b606a90cd82fe94bd0a5a81a5bde09bfc60a637b79d61479ef9f2fd7e529`. This pass uses fresh temporary inputs and ordinary outputs; it does not replace earlier retained runs or execute their adversarial qualifiers.

## Workflow History

- 2026-10-30T12:48:35Z — discovery baseline recorded; reduced-assurance scoped manual engine selected.
- 2026-10-30T12:48:35Z — report_ready: two validated findings, high1/medium1, both validated, neither blocked. Security remediation may now begin serially.
- 2026-10-30T13:10:30Z — Current uncommitted-work audit adds whole-slice ownership, completes cache/lock corrections and corrects observation profile/program binding. Ordinary focused regressions pass 51/51 and the read-only nine-observation verifier passes. Fresh mathematical execution and compatible resume are pending; no adversarial execution is authorized.
- 2026-10-30T13:15:26Z — Complete. Three code-remediated findings, high1/medium2, none blocked. Ordinary focused regressions pass 67/67. Fresh six-entry arithmetic and compatible resume pass with identical exact entries/seals, fresh analytical reconstruction and all owned cleanups. All nine retained observations and an existing natural failed receipt pass read-only handling. No adversarial, corruption, process-interruption or hardlink attack execution ran in this pass. Windows/Python3.14 verification only.
