# Research scripts

- **Created:** `2026-08-20T20:59:00Z`
- **Last updated:** `2026-10-08T03:40:31Z`

These scripts are research instruments for the timestamped RH attempts. The core prime/Laguerre routines remain standard-library based where practical, while selected helpers use the scientific packages pinned by `pyproject.toml` and the project lockfiles. Every retained computation must record the environment actually used.

## OAI-9: External OpenAI theorem is not a local verification CLI

The pinned `EXT-0001` theorem is a **cited external Lean result**, not a theorem exported or independently replayed by this repository. For source identity and optional independent Comparator replay **status/checklist**, use [`references/external-results/README.md`](../references/external-results/README.md) and [`EXT-0001`](../references/external-results/EXT-0001-openai-quasi-rh.md). Its upstream solution uses **Lean 4.34.1**, distinct from our local soundness layer. No `scripts/` command builds or verifies the upstream theorem, and source-hash checks do not prove it.

**Do not confuse verification workflows:**
- `uv run --locked python -m scripts.cert.verify_retained_proofs` checks the closed **eight local finite-support** `C-0050..C-0057` artifacts by byte hash and independent Rust exact replay. It does **not** replay `EXT-0001`.
- `scripts/weil_continuation_driver.py` is the **frozen one-prime** continuation workflow; `scripts/weil_multi_prime_continuation_driver.py` is the **separate generic multi-prime** workflow with no admitted v2 theorems. `CANDIDATE_READY` is not an admission.
- OAI-8 identifies rigorously negative factor-3 *sufficient* Schur matrices at `T=11/20,N=192/196`. Before another post-`p=3` qualification, the mathematical bound itself needs a separately justified improvement. Repeating the same negative matrix with more precision does not help.

See [`research/openai-math/RESEARCH_DIRECTION.md`](../research/openai-math/RESEARCH_DIRECTION.md), [`docs/CONTRACTS.md` §5](../docs/CONTRACTS.md) and [`docs/PROTOCOL.md` §7.2](../docs/PROTOCOL.md). Mathematical external-dependent deductions `C-0060..C-0062` introduce no new CLI, code dependency, certificate format, or theorem admission.

## Scripts

### `verify_identities.py`

Exact rational checks of the algebra used by `A-20260820-002`.

```text
python scripts/verify_identities.py --max-n 40
```

### `prime_trace.py`

High-precision `decimal.Decimal` cutoff study of the prime-Laguerre sequence.

```text
python scripts/prime_trace.py --s0 3 --n-max 16 --cutoffs 10000,100000,1000000 --precision 60
```

`S_n(X)` is a cutoff diagnostic, not the exact infinite `S_n` unless convergence is independently established.

### `kernel_scan.py`

Scans the smooth-density Laguerre kernel in `u=t/(4n)` and compares its sampled maximum with the analytic post-turning saddle.

```text
python scripts/kernel_scan.py --s0 3 --n 8,16,32,64 --u-max 1.6
```

### `prime_range_decomposition.py`

Breaks the truncated prime-power trace into `u=t/(4n)` bins and compares discrete prime contribution with continuous density.

```text
python scripts/prime_range_decomposition.py --s0 3 --n 8,12,16 --max-m 2000000
```

### `window_diagnostics.py`

Supports `A-20260820-004`. It reports:

- the post-turning smooth-density saddle and its Gaussian width;
- the post-turning root-one crossing;
- pre-turning absolute-envelope root rates;
- beta-only envelope rates versus exact complex Cayley rates.

```text
python scripts/window_diagnostics.py --s0 3 --n 64,128,256 --betas 0.5,0.6,0.9,1.0 --gammas 0,5,15
```

### `zero_mode_bins.py`

Numerically decomposes one exact complex zero-mode Laplace transform into `u` bins and compares the truncated integral with the analytic value `z_rho^(-n)-1`.

```text
python scripts/zero_mode_bins.py --s0 3 --beta 0.6 --gamma 5 --n 16,32,64 --steps-per-bin 5000
```

Synthetic beta/gamma inputs are diagnostics only and are not asserted to be actual zeta zeros.

### `uniform_phase_diagnostics.py`

Supports `A-20260820-005`. It evaluates the exact uniform pre-turning stationary map

```text
u_gamma=A^2/(A^2+4gamma^2)
```

against the older small-`u` approximation, checks the critical Cayley phase identity and unit stationary normalization, and can save JSON plus a static SVG plot.

```text
python scripts/uniform_phase_diagnostics.py --s0 3 --zeros 8 --dps 40 --output-json computations/.../data/s0-3.json --plot computations/.../plots/stationary-map-s0-3.svg
```

The zero ordinates are numerical `mpmath.zetazero` evaluations, not certificates.

### `chirp_window_diagnostics.py`

Supports `A-20260820-006`. It records the first-prime coordinate/frequency cap, the local chirp curvature and linearization width, and the exponential root base left by a generic Montgomery-Vaughan Dirichlet-polynomial length term.

```text
python scripts/chirp_window_diagnostics.py --s0 3 --n 1024 --output-json computations/.../data/s0-3-n1024.json
```

The script does not enumerate primes; it checks deterministic scale formulas only.

### `bilinear_chirp_geometry.py`

Supports `A-20260821-001`. It computes the four-corner nonseparability defect for `F(r,s)=Phi_n(r+s)`, checks its `1/n` decay on dyadic logarithmic boxes, records the balanced `sqrt(n)` log-width needed for unit cross phase, and verifies the formal pre-turning phase excursion `pi n`.

```text
python scripts/bilinear_chirp_geometry.py --s0 3 --n 1024 --output-json computations/.../data/s0-3-n1024.json
```

The script is deterministic phase geometry only; it does not enumerate primes or test arithmetic cancellation.

### `positivity_kernel_diagnostics.py`

Supports `A-20260821-002`. It checks synthetic Li Gram and Schoenberg matrices and the deterministic negative-diagonal structure of generalized prime-atom Gram contributions.

```text
python scripts/positivity_kernel_diagnostics.py --n-dim 8 --theta 0.7 --r 1.2 --search-n 100 --t 0.5 --x 0,1,5,10 --output-json computations/.../data/kernel-diagnostics.json
```

The zero orbits are synthetic diagnostics only.

### `weil_support_geometry.py`

Supports `A-20260821-002`. It records the half-log prime-power support thresholds and the exact path-graph norm of symmetrized compressed translations on `L2([-T,T])`. The later `A-20260821-003` work adds the exact finite-support normalization and residual-term requirements.

```text
python scripts/weil_support_geometry.py --T 0.45 --max-m 20 --output-json computations/.../data/support-T045.json
```

It does not approximate the archimedean Weil operator.

### `weil_endpoint_absorption_certificate.py`

Supports `A-20260821-003`. It proves the `T=7/20` first-prime endpoint absorption inequality using exact `Fraction` arithmetic, including certified rational logarithm bounds derived from the atanh series:

```text
V + P_2 >= (69/100) V >= 0.
```

```text
python scripts/weil_endpoint_absorption_certificate.py --output-json computations/.../data/endpoint-absorption-rational.json
```

### `weil_exact_constants.py`

Supports `A-20260821-003`. It uses python-flint/Arb to enclose the exact transcendental constants needed by future interval certificates, including `tau=log(2)/T`, `c_2=log(2)/sqrt(2)`, and `c_T=log(2*pi*T)+EulerGamma` at `T=7/20`.

```text
python scripts/weil_exact_constants.py --prec 256 --output-json computations/.../data/exact-constants-arb.json
```

### `weil_exact_prime_complement_certificate.py`

Supports `A-20260821-004`. This is a proof-path Arb script with exact rational inputs. It certifies that the globally absorbed `0.69V` residual target is negative on `P_0-P_2`, verifies the exact-prime value is positive on that same test, and derives the crude rigorous Legendre-complement bound `mu_N=H_N-c_T-c_2-rho_R`.

```text
python -m scripts.weil_exact_prime_complement_certificate --prec 224 --max-n 30 --residual-order 32 --output-json computations/.../data/certified-complement.json
```

Its retained JSON uses exact rational interval endpoints for proof quantities. It does not prove full first-prime positivity.

## Canonical one-prime continuation workflow

For ordinary one-prime continuation research, use `scripts.weil_continuation_driver`. It is the canonical pre-theorem workflow and owns reconnaissance, convergence classification, dimension selection, rigorous precision escalation, conditioning-incident handling, exact candidate construction, candidate-level cross-precision stability confirmation, and the self-contained continuation bundle.

The standalone continuation scripts remain supported research instruments and implementation components. Use them for isolated diagnostics, debugging, or historical reproduction; do **not** manually chain them as the ordinary continuation workflow.

### `weil_continuation_driver.py`

Canonical pre-theorem continuation driver. It accepts an exact rational support and an explicit dimension list or range. The p17 canonical scout runs eight increasing reconnaissance resolutions derived from the requested maximum dimension, retains all eight runs for audit, and applies the existing sign/convergence classifier to the highest three levels. The 1% relative Schur-movement tolerance is unchanged. This lets coarse under-resolution wash out without weakening the rigorous gate; `--scout-resolutions` may still be set explicitly for historical reproduction or diagnostics, and when fewer than three levels are supplied the classifier necessarily uses all supplied levels. The driver then rigorously screens only the smallest stable-positive dimension and its next larger fallback. Rigorous screening and candidate checks use the persistent cache `.cache/continuation-driver` by default; cache keys include support, dimension, precision, residual order, witness/rounding parameters, and a fingerprint of the continuation source files plus `uv.lock`. It accepts only the strict `log(2)/2 < T < log(3)/2` p=2-only support window. It never extrapolates dimensions, invokes the theorem exporter, edits the closed contract, or grants theorem status.

The current canonical workflow version is `continuation-driver-p17-v1`; the cache contract remains `continuation-driver-v6`. `driver_version` identifies the complete canonical workflow/provenance contract, including scout selection semantics, lifecycle, observability, cleanup, and finalization as well as mathematical orchestration. It must advance when those semantics materially change, even if the cached mathematical payload format is unchanged. `cache_version` is narrower: it advances when cached mathematical payload/key semantics change. P17 changes the canonical reconnaissance policy but not the cache payload/key contract, so cache v6 remains correct; cache keys also include a fingerprint of the continuation sources (including this driver) and `uv.lock`, isolating changed implementations automatically. Historical bundles keep the driver/cache versions they were actually produced with.

```text
uv run --locked python -m scripts.weil_continuation_driver \
  --support 19/40 \
  --n-min 48 \
  --n-max 80 \
  --n-step 4 \
  --output-dir computations/.../data/continuation-T019-040
```

An explicit dimension list can be supplied instead:

```text
uv run --locked python -m scripts.weil_continuation_driver \
  --support 19/40 \
  --n 48,52,56,60,64,68,72 \
  --output-dir computations/.../data/continuation-T019-040
```

The default final stdout output is a concise human summary; pass `--json` when the full result object is needed on stdout. During the run, the CLI emits short elapsed-time progress lines to **stderr** and flushes every line immediately, keeping stdout reserved for the final human or JSON result. Live messages cover stage starts/completions, scout resolution completion, stable-positive selection, rigorous targets, per-precision Arb attempts (including from spawned rigorous workers), candidate rounding/confirmation, bundle writing, and the final terminal state. Stderr is advisory: a closed or broken stderr stream cannot invalidate computation/finalization because `.live/` remains the durable operational channel. Pass `--quiet` to suppress these live stderr messages without changing final stdout or the `.live/` observability files. The bundle remains the durable audit artifact.

Before creating live state or doing scout/Arb work, the CLI acquires an exclusive OS-backed lock at `<output-dir>/.run.lock`. Windows uses a nonblocking `msvcrt` byte-range lock and POSIX uses `flock`; the JSON file carries the owning `run_id`, parent PID, command, support, and start time for diagnostics, but the kernel lock—not the PID metadata—decides whether the directory is active. If another process targets the same directory while the lock is held, it exits immediately with the active run ID/PID/start time before any expensive work begins. If a process crashes, the OS releases ownership automatically; a stale `.run.lock` file alone therefore does not block a later run and is overwritten after successful reacquisition. The lock pathname is intentionally never unlinked as part of release/rejection, because deleting a shared lock path after releasing the OS lock can race with a new POSIX owner and create two lock inodes; an unlocked stale file is harmless. The lock file is operational metadata and is excluded from the continuation manifest just like `.live/`.

Immediately after lock acquisition, the CLI captures one start-of-run provenance snapshot and writes `<output-dir>/.live/run.json` before status/events or mathematical computation begin. `run.json` is immutable for the lifetime of the directory and records the shared `run_id`, driver and driver version, exact support, requested dimensions, parent PID, start time, Git commit, and Git dirty flag. When the output directory is inside the repository, the owned output directory itself is excluded from the Git status query so `.run.lock`/`.live` do not make a clean checkout appear dirty; source-tree changes elsewhere still set `git_dirty=true`. The same provenance object is reused for the final bundle rather than queried again. A surviving `run.json` therefore identifies an interrupted/prior run and causes ordinary fresh-run reuse to fail closed even after the OS lock has disappeared.

Finalization is transactional. Reaching a mathematical terminal state does not by itself create a completed bundle. The driver first exits every process-pool context, requires access to the spawned-worker registry, verifies that each captured worker process is no longer alive and has an exit code, verifies that no executor remains active, and only then freezes the final result through JSON and records its SHA-256. The bundle boundary independently validates the complete cleanup-report shape, requires a known pre-theorem terminal state, rejects theorem/admission flags, and recomputes the frozen-result digest rather than trusting the caller. Stage artifacts are written first, `summary.json` is written after them, and `run-manifest.json` is written **last** as the bundle completion seal; artifact writes are flushed/fsynced before publication, with directory metadata fsynced on POSIX. The manifest also records a top-level `process_lifecycle` summary derived from that already-validated cleanup report: the parent PID, canonical `spawn` worker model, `worker_cleanup_verified=true`, `active_children_after_cleanup=0`, and executor/reaped-worker counts. Canonical finalization cross-checks that parent PID against immutable `.live/run.json`, while tests also require it to agree with `.run.lock` and `run-status.json`. Here `active_children_after_cleanup` is deliberately scoped to driver-managed process-pool workers observed by Python; it is not an OS-wide descendant-process claim, which remains Portus's responsibility. After the manifest write, the heartbeat supervisor must stop and join cleanly. Only then is `BUNDLE_FINALIZATION_COMPLETED` appended, live status set `terminal=true`, and `RUN_COMPLETED` appended. A heartbeat I/O failure therefore rolls the manifest back instead of allowing a completed run after supervision was lost. The output-directory lock is then released before final stdout is emitted. Therefore a valid `run-manifest.json` means the mathematical result had already been reached, parallel worker cleanup had been verified, the frozen payload matched its recorded digest, and live supervision survived through bundle finalization—not merely that computation stopped producing output.

Executor cleanup has an explicit defense-in-depth recovery path without replacing the existing `with ProcessPoolExecutor(...)` architecture. After normal pool shutdown returns, the driver checks the exact captured executor `Process` objects and cross-checks them against `multiprocessing.active_children()`. If an owned worker is still alive or unreaped, cleanup escalates through a short join (`0.5s`), `terminate()` plus join (`1.0s`), then `kill()` where available plus join (`1.0s`). Only the captured executor workers are eligible for those actions; unrelated children returned by `active_children()` are recorded diagnostically and never terminated by the continuation driver. Successful recovery is recorded in `.live/events.jsonl` and aggregated into the manifest cleanup fields. Any owned worker still unresolved after the final check fails the run and prevents a completed manifest. This does not solve a Python executor whose own `shutdown(wait=True)` never returns; Portus remains responsible for stronger OS-level process-tree containment, and bounded cancellation of a truly wedged executor is a separate later concern.

If execution raises after live state has started, the CLI does not leave a completed manifest. Runtime/finalization errors produce `<output-dir>/.live/failure.json` with operational state `RUN_FAILED`; `KeyboardInterrupt` produces `RUN_INTERRUPTED`. The same state is written to `run-status.json` with `terminal=true` and appended to `events.jsonl`. If a failure occurs after a manifest was tentatively written but before completion status/events finish, the manifest is removed. Partial scout/rigorous/candidate/summary files may remain for diagnosis, but without `run-manifest.json` they are explicitly incomplete and must not be treated as a finalized continuation bundle.

While the CLI is running, it maintains `<output-dir>/.live/run-status.json` as a tiny atomically replaced operational snapshot. The file records the same stable run ID, command, support, parent PID, start/update timestamps, elapsed time, current workflow state, a bounded current-operation payload, and whether final bundle writing has completed. In addition to milestone-driven updates, a parent-owned heartbeat thread refreshes `last_heartbeat_utc` and `elapsed_seconds` every 12 seconds by default. A heartbeat claims only that the parent process and its heartbeat supervision are alive: it does not change the workflow state/current operation and does not claim mathematical progress. The heartbeat thread is explicitly stopped and joined on every CLI exit path covered by the driver lifecycle.

The same run also maintains `<output-dir>/.live/events.jsonl` as an append-only structured event journal. Each flushed/fsynced JSON line carries a monotonically increasing sequence number, timestamp, run ID, event name, and only small event-specific fields. Canonical driver event/status payloads bound long strings and replace oversized lists with count/preview/truncated summaries, so a large requested dimension range cannot silently turn operational telemetry into multi-kilobyte state; retained mathematical results are not changed by this live-only bounding. The journal records run start/completion, workflow transitions, scout stage/resolution milestones, rigorous dimension milestones, candidate construction/confirmation milestones, bounded failure diagnostics, and bundle finalization. The parent process remains the sole journal writer, so parallel child processes never race on the JSONL file. R4's exact in-child rigorous precision messages are intentionally stderr-only; adding those child details to the durable parent-owned event chronology still belongs to the later worker-observability hardening. All `.live/` files are operational metadata rather than mathematical evidence and are intentionally excluded from `run-manifest.json` artifact hashes.

The CLI uses bounded spawn-based process parallelism by default: up to three workers for the independent floating-scout resolutions and up to two workers for the independent primary/fallback rigorous screens. Parallel futures are observed with completion-order semantics, so `.live/events.jsonl`, live status, and stderr report a completed/failed scout resolution or rigorous dimension as soon as the parent can consume that future; they do not wait for an earlier-submitted job. Completion chronology is operational only. Successful/failed outcomes are buffered by stable resolution level or dimension and then materialized into `scout_runs`, per-dimension scout series, `scout_failures`, `rigorous_screening`, `rigorous_failures`, and survivor/candidate priority in canonical resolution/dimension order. Worker timing therefore cannot change reconnaissance sample order, retained bundle ordering, or which surviving dimension is tried first. Each worker defaults BLAS/OpenMP-style thread counts to one unless explicitly overridden, preventing process-level parallelism from multiplying hidden library threads. The precision ladder inside each rigorous screen, exact candidate construction, and candidate cross-precision confirmation remain sequential by design.

For deterministic sequential reproduction or debugging:

```text
uv run --locked python -m scripts.weil_continuation_driver \
  ... \
  --scout-workers 1 \
  --rigorous-workers 1
```

Programmatic `run_driver()` callers remain sequential by default; the CLI owns the bounded parallel defaults. Cache writes use process-unique temporary files followed by atomic replacement so parallel jobs cannot collide on one generic `.tmp` path. On Windows, short-lived sharing/access denials during atomic publication are retried with a small bounded backoff for live status, bundle artifacts, and cache entries; persistent denial still raises and fails the run rather than silently degrading durability.

The CLI rejects a `--cache-dir` located inside its `--output-dir` before acquiring the run lock. Cache files are operational reuse data rather than bundle artifacts; allowing them inside the output directory would otherwise guarantee a late finalization failure after expensive work.

`CANDIDATE_READY` is generator-side evidence only and does **not** authorize theorem admission. The driver stops there. A separate human/research decision must first admit the exact support/dimension pair to the closed theorem contract; only after that separate change may a fresh independent Rust replay establish theorem status.

The driver escalates matrix rounding bits and witness bits independently when candidate construction fails. Once an exact positive candidate exists, it freezes `T`, `N`, residual order, matrix bits, and witness bits and reassembles at `p+128`; if that comparison is not stable it tries `p+256` before stopping. Candidate confirmation compares exact `mu_N`/even/odd margins, raw Arb enclosure contraction, exact rounded interval widths, and widest-entry conditioning diagnostics. A higher-precision contradiction or unresolved movement ends fail-closed as `PRECISION_LIMIT_REACHED`, not `CANDIDATE_READY`. The defaults are configurable with `--candidate-precision-step` and `--candidate-precision-extra-steps`. Rounding, witness, mathematical-negative, and insufficient-precision outcomes remain distinct.

### `weil_legendre_schur_scout.py`

**Diagnostic/component tool.** Use this directly for isolated floating reconnaissance or historical reproduction, not as the first manual step of the ordinary continuation workflow.

```text
python -m scripts.weil_legendre_schur_scout --support 2/5 --max-mode 120 --quadrature-order 700 --shift-order 350 --n 32,40,48,56,64,72 --output-json computations/.../data/dimension-scout-T040.json
```

This script is reconnaissance only. Its finite tail truncation is not an infinite-dimensional bound and cannot certify positivity.

### `weil_support_continuation_scout.py`

**Diagnostic/component tool.** Use this directly for isolated rigorous full-tail diagnostics or historical reproduction; ordinary continuation precision search is owned by the canonical driver.

Supports `A-20260826-001`. It reuses the exact-polynomial/Arb full-tail assembler at exact rational support values, then converts only normalized matrix midpoints to NumPy/SciPy for support-margin reconnaissance. It reports `mu_N`, finite-block midpoint minima, Schur midpoint minima, and component penalty scales. Positive rows are not theorem certificates.

```text
python -m scripts.weil_support_continuation_scout --supports 7/20,3/8,2/5,17/40,9/20 --dimension 32 --prec 112 --output-json computations/.../data/support-scan.json
```

### `weil_support_candidate_check.py`

**Diagnostic/component tool.** Generator-side exact candidate checker for a deliberately selected continuation point. It performs rigorous Arb assembly, outward dyadic rational rounding, exact rational Schur construction, and exact rational congruence/Gershgorin checks. Ordinary continuation candidate search is owned by the canonical driver. This standalone checker deliberately does **not** emit a theorem certificate, modify the closed contract, authorize admission, or invoke the independent verifier.

```text
python -m scripts.weil_support_candidate_check --support 2/5 --dimension 40 --prec 256 --matrix-bits 72 --witness-bits 40 --output-json computations/.../data/candidate-T040-N40.json
```

### `cert/exact_prime_schur_certificate.py`

Proof-path exporter for the closed `exact_prime_legendre_schur` whitelist. It assembles rigorous exact-prime Legendre-Schur certificates, outward-rounds Arb matrices to exact dyadic rational intervals, derives exact rational parity congruence witnesses from rational midpoint `LDL^T`, and exports only explicitly admitted support/dimension pairs.

Current admitted examples:

```text
python -m scripts.cert.exact_prime_schur_certificate --claim C-0050 --support 7/20 --dimension 32 --prec 160 --matrix-bits 64 --witness-bits 32 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0051 --support 2/5 --dimension 40 --prec 256 --matrix-bits 72 --witness-bits 40 --output-json computations/.../data/certificate-T040-N40.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0052 --support 17/40 --dimension 48 --prec 384 --matrix-bits 88 --witness-bits 48 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0053 --support 9/20 --dimension 56 --prec 512 --matrix-bits 104 --witness-bits 56 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0054 --support 19/40 --dimension 68 --prec 384 --matrix-bits 64 --witness-bits 32 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0055 --support 1/2 --dimension 80 --prec 512 --matrix-bits 64 --witness-bits 32 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0056 --support 21/40 --dimension 96 --prec 512 --matrix-bits 64 --witness-bits 32 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0057 --support 27/50 --dimension 104 --prec 512 --matrix-bits 64 --witness-bits 32 --output-json computations/.../data/certificate.json
```

`(27/50,104)` is contract-admitted and theorem-bearing as `C-0057`. `X-20260924-001` executed the command above from clean committed provenance, received independent zero-float Rust exit `0` / `passed=true`, passed real-certificate adversarial checks, and is explicitly registered in the retained-proof manifest.

The generator does not decide the theorem. `crates/rh_cert` independently validates the whitelisted pair, reconstructs the complement lower bound and factor-3 Schur matrix, and proves the parity blocks positive using exact rational interval congruence/Gershgorin checks. The retained theorem runs are `X-20260821-005`, `X-20260826-001`, `X-20260826-002`, `X-20260826-003`, `X-20260827-002`, `X-20260827-004`, `X-20260828-001`, and `X-20260924-001`.

### `cert/verify_retained_proofs.py`

Canonical retained-theorem artifact acceptance gate. It loads the closed manifest at `computations/retained-proofs.json`, validates its eight registered proof identities, hashes the exact certificate bytes, and replays every hash-valid artifact through the current independent zero-float `rh_cert` verifier.

```text
uv run --locked python -m scripts.cert.verify_retained_proofs
```

A successful run ends with `RETAINED PROOF CHAIN: PASS - 8/8`. The command is fail-closed and reports `MISSING`, `HASH_MISMATCH`, `VERIFIER_ERROR`, `THEOREM_FAILURE`, or `SEMANTIC_MISMATCH` per theorem while continuing through the full manifest. It **does not regenerate certificates** and it does not grant theorem status to a new support/dimension pair. It answers the narrower audit question: are the exact proof artifacts currently cited by the repository still byte-intact and accepted by the current independent verifier?

Fast manifest-only validation remains available as:

```text
uv run --locked python -m scripts.cert.verify_retained_proofs --manifest-only
```

The real eight-artifact pytest acceptance is deliberately excluded from ordinary test runs and can be invoked explicitly with:

```text
uv run --locked --extra test python -m pytest -q -m retained_proofs tests/test_retained_proofs_acceptance.py
```

### `cert/legendre_schur.py`

Rigorous shared assembly for the exact-prime Legendre-Schur proof and continuation work. It uses exact rational polynomial algebra for Legendre actions and overlap identities, Arb only for transcendental enclosures, closed logarithmic/log-squared moments for `G_V`, exact edge-overlap geometry for `G_2`, and the canonical Suzuki residual series plus rigorous remainder for `G_R`. The reusable assembler accepts an exact rational one-prime support `T`; theorem-specific certificate wrappers remain responsible for locking allowed supports/dimensions.

### `cert/prime_power_terms.py`

Additive multi-prime arithmetic operator core. Unlike the frozen one-prime edge-overlap implementation, this module is generic in the active prime powers and translation geometry. It recognizes `m=p^k` with exact integer arithmetic; rigorously constructs `log(m)`, `tau_m`, `Lambda(m)`, and `c_m` using Arb; enumerates the strict active set `log(m)<2T` and fails closed when a requested precision cannot settle a threshold; constructs the left/right translated polynomial pieces on `[-1,1]`; globally partitions by every translation breakpoint; sums all active signed arithmetic images on each cell; and integrates those combined images to obtain `P`, `P^2`, and `G_P=P^2-PD^{-1}P`.

`P^2` is computed from `<P phi_i,P phi_j>`, so mixed terms are present automatically. The focused regression suite includes exact overlap agreement with `first_prime_matrices()` in the one-prime window, a nonzero `P_2/P_3` cross-term test, and a `{2,3,4}` case at `T=7/10` where `tau_2<1`. This module is not yet connected to a multi-prime certificate exporter or verifier.

### `cert/multi_prime_legendre_schur.py`

Full rigorous post-v1 Legendre-Schur assembler. `assemble_multi_prime_schur()` uses the established potential moment formulas and Suzuki residual coefficients/remainder, with native exact polynomial convolution and assembly-local residual monomial-action reuse on the new path. The arithmetic block comes from `cert/prime_power_terms.py`, which uses native Arb shifts, products, and antiderivative evaluation on the shared partition, with coefficient-certified parity. Outputs include the active terms, combined `P`, operator `P_squared`, `A`, `GV`, `GP`, `GR`, `rho_R`, `mu`, and `schur`. The complement derives each compressed-shift norm from the rigorous path-graph chain length rather than assuming the one-prime `tau>1` geometry. Frozen v1 implementation and mathematical estimates are unchanged.

The P3 bridge tests are deliberate: before the `{2,3}` case is accepted, the generic assembler is compared against the frozen v1 path at four historical supports and dimensions 16 through 32. All relevant matrix/scalar enclosures overlap. Only after that bridge passes does the direct `{2,3}` test verify that the combined operator square contains a strictly nonzero cross term and does not reduce to the sum of the two individual squares.

P3 acceptance closes with the integrated focused target at `31/31` and the complete default Python suite at `574/574`. The frozen `cert/legendre_schur.py` remains unchanged.

### `weil_multi_prime_schur_scout.py`

Floating-only reconnaissance for the post-`p=3` path. It independently enumerates the numerically active prime powers, constructs each compressed translation in NumPy/SciPy quadrature, sums the combined `P`, and forms truncated component tail Grams labelled `GV`, `GP`, and `GR`. It reports per-term complement estimates and combined-prime singular-value/tail conditioning. These values are intentionally not Arb bounds and must never be used as theorem evidence.

### `weil_multi_prime_support_candidate_check.py`

Rigorous generator-side exact candidate stage. It consumes `assemble_multi_prime_schur()`, outward-rounds `A`, `GV`, `GP`, and `GR`, outward-rounds every active term's `c_m b_m` contribution separately, reconstructs the exact complement lower bound and factor-3 Schur matrix, and derives exact rational even/odd congruence witnesses. Output diagnostics include the individual active-term constants, `P/P_squared/GP` width conditioning, explicit `GP` widths, exact even/odd Gershgorin margins, and optional lower-vs-higher Arb precision contraction. `--prec`, `--matrix-bits`, and `--witness-bits` are independent controls; `--compare-prec` is diagnostic-only. `--dimension` is required rather than guessed.

P4 acceptance closes with the focused multi-prime/frozen-v1 target at `24/24` and the complete default Python suite at `578/578`.

### `weil_multi_prime_support_continuation_scout.py`

Rigorous-screen adapter for the multi-prime driver. It assembles `A/GV/GP/GR/mu` with `assemble_multi_prime_schur()` and independently confirms active terms `[2,3]`. Endpoints, widths and widest-entry diagnostics serialize as exact rationals. Midpoint eigendiagnostics use power-of-two scaling before binary64 conversion and restore units as rational numerical values, not certified spectral bounds. Unavailable diagnostics are explicit and require more precision, not failed assembly or mathematical rejection. It does not construct exact candidates.

### `weil_multi_prime_continuation_driver.py`

Canonical continuation workflow for future structural windows, initially hard-limited to `log(3)/2 < T < log(4)/2` with exact active set `{2,3}`. It intentionally duplicates the mature operational orchestration rather than refactoring the historical one-prime driver. Workflow: floating multi-resolution scout → stable dimensions → primary/fallback rigorous Arb precision search → exact matrix/witness bit ladders → generator-side exact candidate → higher Arb precision confirmation → `CANDIDATE_READY` or a fail-closed terminal state. Parallel stages use bounded spawn pools and `as_completed` for immediate observation, then materialize retained output in canonical order. Cache publication and result bundles are atomic; the manifest is the completion seal; worker cleanup must verify zero owned active children before finalization. The old `weil_continuation_driver.py` remains the historical one-prime path.

P5 acceptance closes with focused multi-prime/frozen-v1 tests at `35/35`, bundle/P5 regression at `29/29`, a real parallel CLI smoke with verified cleanup, and the complete default Python suite at `591/591`.

### `cert/certificate_v2_contract.py`

P6 structural contract helper for `rh-weil-certificate-v2`. It loads and validates `docs/contracts/rh-weil-certificate-v2.json`, then applies canonical cross-field checks that JSON Schema alone cannot express: no floats, reduced support/interval rationals, strictly increasing `arithmetic_terms`, prime base validation, `m=base_prime^exponent`, full matrix coordinate coverage, and correct even/odd witness dimensions. This module does **not** export theorem certificates and does not call the Rust verifier. `V2_ALLOWED_CONFIGURATIONS` is deliberately an empty `frozenset`; structure-valid v2 data is not theorem-admitted data.

P6 acceptance closes with `21/21` focused certificate-v2/frozen-v1/admission tests and `602/602` for the complete default Python suite.

P7 adds the independent Rust consumer for this structure under `crates/rh_cert/src/v2.rs` with format routing in `crates/rh_cert/src/dispatch.rs`. The Python helper above remains structural/generator-side tooling and does not call or substitute for the Rust verifier. Rust requires exact first-window terms `[2,3]`, independently derives the exact-rational prime losses and `mu_N`, rebuilds the factor-3 `GV+GP+GR` Schur blocks, and checks exact parity witnesses. The production v2 theorem whitelist is still empty. The Rust trust boundary remains exact-rational: it checks serialized interval arithmetic and relationships but does not independently establish the underlying transcendental Arb enclosures.

P7 closure: Rust `63/63`, strict clippy/rustfmt, focused Python `21/21`, complete default Python `602/602`, and retained theorem replay `8/8`.

P8 hardens the pre-continuation boundary. `certificate_v2_contract.py` now semantically enforces exact first-window terms `[2,3]`, exact `b_m=1`, coefficient/norm/complement relationships, matrix symmetry/parity, and fail-closed strict support from the serialized log intervals. The JSON Schema independently closes the serializable term shape to `[2,3]`. Cross-layer structural cases live in `tests/data/certificate-v2-cross-layer-v1.json`; closed theorem-admission cases live in `tests/data/multi-prime-admission-v2.json`. These are test-only oracles and are never production inputs. P8 closure is focused Python `41/41`, Rust `67/67`, full Python `608/608`, retained replay `8/8`, with strict clippy/rustfmt.

### P9 qualification performance result

The first real `T=11/20` qualification exposed a performance boundary in the generic rigorous path. The floating scout completed normally and selected `N=192` with fallback `N=196`, but two independent retries failed to finish even the first 128-bit rigorous assemblies within external execution allowances of roughly 30 minutes and one hour. The workers remained CPU-active; this was not a deadlock. No rigorous cache entry was committed before termination.

Treat this as **NOT QUALIFIED**, not as a mathematical negative. Do not keep extending the dimension grid or retry the same command expecting cached progress. Before another end-to-end qualification, profile and optimize the generic multi-prime rigorous assembler while preserving P2/P3 equivalence and P8 cross-layer gates.

### `profile_multi_prime_assembly.py`

Manual sequential rigorous-assembly timing CLI. It uses no continuation cache or process pool, permits nonpositive diagnostic complement at small dimensions, records source/runtime provenance, and publishes each completed sample. `--mode timing` measures uninstrumented wall/CPU totals; `--mode stages` reports nested inclusive/exclusive stage timings; `--mode cprofile` retains the hottest cumulative call records. Peak memory is a process-lifetime high-water mark. Interrupted output remains marked running, not completed. Diagnostic strings and JSON conversion occur outside the assembly timer.

```text
uv run --locked python -m scripts.profile_multi_prime_assembly --support 11/20 --dimensions 32,64,96,128 --precision 128 --residual-order 32 --mode timing --output-json computations/.../data/assembly-timings.json
```

[Phase 1/2 performance record](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md): 128-bit isolated `N=128` falls from `897.221 s` to `6.779 s`; `N=192/196` complete in `26.259/28.069 s`. Focused tests pass `65/65`, including exact residual-image and unoptimized interval references. These timings do not establish target candidate positivity, higher-precision readiness, full acceptance, or P9 closure. The frozen P9 driver was not run.

Phase 3 extends that record with `121/121` focused checks. `tests/test_multi_prime_assembly_performance.py` compares independent unskipped small references, exact residual coefficients/norms, and tighter high-precision enclosures, and couples bounded work counts to mathematical output comparisons. Driver tests exercise real support/precision cache isolation and generic-source fingerprint invalidation. Candidate tests independently reconstruct outward dyadic bounds, grouped factor-3 Schur blocks, and exact congruence/Gershgorin margins with separate Arb/matrix/witness controls. No runtime thresholds or new production caches were added. The timestamped phase 4 addendum retains higher-precision/throughput measurements and full acceptance executions; its readiness gate is blocked by target conditioning and unrelated workspace formatting failures.

### `profile_multi_prime_workflow.py`

Manual component-cost CLI, not qualification. `--mode throughput` measures uncached assembly in the driver's bounded verified spawn pool; `--mode candidate` times actual sequential candidate assembly, rounding, exact Schur and witness work, retaining expected stage failures and exact native conditioning widths outside the timer; `--mode scout` measures only the floating component over the requested dimension grid/resolutions. Every mode records provenance, lifetime peak memory and atomic JSON publication costs. Pool modes preserve completion observation, canonical result order and cleanup verification. No mode calls `run_driver()`, selects a candidate, uses continuation caches or seals qualification.

```text
uv run --locked python -m scripts.profile_multi_prime_workflow --mode throughput --support 11/20 --dimensions 192,196 --precision 512 --workers 2 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase4-throughput-512.json
uv run --locked python -m scripts.profile_multi_prime_workflow --mode candidate --support 11/20 --dimensions 192,196 --precision 512 --matrix-bits 64 --witness-bits 32 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase4-candidates-512-64-32.json
```

Phase 4 observes `34.893/37.460 s` isolated 512-bit assembly and `38.208 s` two-worker throughput, but target candidates fail exact midpoint LDL witnesses through Arb 768. Native combined-prime widths remain enormous despite precision contraction; this is not a mathematical negative. Full Python `647/647`, Rust `67/67`, strict Clippy and retained replay `8/8` pass; workspace formatting fails in untouched `rh_engine` files. Stop before P9. The retained cost model estimates a conservative 12-hour external allowance, not a runtime guarantee or launch authorization.

The user subsequently authorized the unchanged phase 5 qualification despite those blockers. [X-20261002-001](../computations/2026-10-02T010121Z-t11-20-multi-prime-qualification-after-hardening/record.md) records natural completion in `168.78 s` at `PRECISION_LIMIT_REACHED`: scout selects `192/196`; 128-bit screens report float-conversion overflow, and 256/384/512 remain insufficient. No candidate construction or mathematical rejection occurred. Source snapshots and final driver artifacts are retained, but phase 6 byte audit/reproduction was not run. P9 remains NOT QUALIFIED; do not change frozen controls to hide the conditioning limit.

Phase 6 independently audits both final manifests and every listed artifact, `18/18` per run, plus ordered result-payload digests. Fresh-cache Run B uses the same source snapshot and settings, naturally finishing in `169.39 s` at `PRECISION_LIMIT_REACHED`. Exact recursive canonical comparison passes with zero mathematical/diagnostic differences after predeclared metadata exclusions; `17/18` artifacts are byte-identical. A separate Windows process scan finds zero qualification survivors. These operational checks pass, but the qualification gate fails because both runs stop before candidate construction. P9 remains NOT QUALIFIED; no admission or further retry occurred.

Phase 7 separates exact-safe multi-prime diagnostics in `multi_prime_precision_diagnostics.py`, leaving the shared frozen-v1 helpers unchanged. Screening and candidate confirmation use exact width, sign and margin-tolerance comparisons, including overflow/underflow cases. The workflow version is `multi-prime-continuation-driver-p9-phase7-v2`; cache contract is `multi-prime-continuation-driver-v2`, with the new numerical dependency fingerprinted. Old float-payload cache entries cannot be reused. Rational-valued diagnostic fields now serialize as strings rather than binary64 numbers.

Phase 7 focused acceptance passes `144/144`. Real uncached 128-bit `192/196` screens complete without conversion exceptions but remain insufficient precision. A known one-prime overlap candidate confirms from Arb `256` to `384` at fixed `64/32` bits; this is not `{2,3}` target readiness. Commands, exact outputs and source hashes are retained in [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md). No conditioning redesign or qualification retry occurred; P9 remains NOT QUALIFIED.


### `profile_multi_prime_conditioning.py`

Enclosure diagnostic, never qualification. `--representations cell-legendre` now exercises production generic arithmetic. `global` and `cell-monomial` are explicit historical controls confined to this diagnostic. `--group-potential` uses production exact harmonic contractions; omitting it selects historical per-moment rounding as a control, not a production fallback. The diagnostic CLI uses canonical Legendre modes; the production operator also accepts arbitrary exact orthogonal polynomial bases.

Profiles retain exact rational widths/coefficient bounds through basis conversion, local affine coefficients, combined images, sampled control products/primitives/endpoints, and full `P/P_squared/PD^-1P/GP/A/GV/GR/Schur` matrices. Local Legendre integration uses diagonal exact norms instead of primitives. Product-stage probes sample diagonal degrees `0,N//2,N-2,N-1`; coefficient/matrix profiles are full. Basis-conversion measurements in local runs are controls. No wall-clock figure or width threshold grants acceptance.

`--witness-precision` requests actual outward candidate construction at that Arb precision, with independent `--matrix-bits` and `--witness-bits`. It reuses the genuinely assembled matrices. Exact rounded inputs are retained in candidate ZIPs, including when witness construction fails; failed inputs do not contain a successful witness. `--rayleigh-check` checks a leading-midpoint-system last-coordinate direction rounded to the requested witness bits against the rigorous even Schur block; it is not a spectral sign oracle. Complete intervals/vectors carry SHA-256 and are diagnostic inputs, never theorem certificates.

```text
uv run --locked python -m scripts.profile_multi_prime_conditioning --dimensions 16 --precisions 128,256 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase8-small-comparison.json
uv run --locked python -m scripts.profile_multi_prime_conditioning --dimensions 192,196 --precisions 128,256,384,512 --representations cell-legendre --group-potential --witness-precision 384 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase8-grouped-potential-targets.json
uv run --locked python -m scripts.profile_multi_prime_conditioning --dimensions 192,196 --precisions 384 --representations cell-legendre --group-potential --rayleigh-check --matrix-bits 104 --witness-bits 56 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase8-rayleigh-cli.json
```

[X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md) records Phase 8 selected Arb-512 full-Schur widths `6.5763e-82/2.1290e-80`, but actual candidates fail at both `64/32` and frozen-maximal `104/56` bits. Strict negative exact interval directions at `192/196` independently replay `2/2`. Phase 9 implements the selected representation without changing the sufficient Schur test, support/grid, bounds or precision caps. P9 remains NOT QUALIFIED/P10 blocked. The rejection is not localized Weil-form negativity or an RH counterexample.

### `audit_multi_prime_candidate.py`

Standalone zero-float replay of `rh-multi-prime-candidate-audit-v1` inputs. Successful `weil_multi_prime_support_candidate_check.run_candidate()` results now contain `audit_inputs`: outward-rounded `A/GV/GP/GR`, exact complement inputs and prime losses, controls/basis/factor, both dyadic witness matrices and exact margins. The auditor reconstructs the positive complement and factor-3 Schur matrix, checks dimensions, parity and scalar relationships, and independently evaluates congruence centers/radii with native rational matrices. Reported margins must match the recomputed strictly positive values.

```text
uv run --locked python -m scripts.audit_multi_prime_candidate --input computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-overlap-base-audit-inputs.json --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-overlap-base-audit.json
uv run --locked python -m scripts.audit_multi_prime_candidate --input computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-overlap-confirmation-audit-inputs.json --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-overlap-confirmation-audit.json
```

These exercised inputs are the existing one-prime overlap control `T=2/5,N=40`, with fixed `64/32` bits and real Arb `256 -> 384` confirmation. They are not substitute qualification evidence for frozen `{2,3}` targets. Replay checks serialized rational arithmetic, not upstream transcendental enclosures or theorem admission; it never calls Rust.

The multi-prime workflow/cache versions are `multi-prime-continuation-driver-p9-phase9-v3` / `multi-prime-continuation-driver-v3`. Old cache entries cannot satisfy the new proof-input contract. Source fingerprints include the auditor and bundle publisher. Multi-prime bundle format is `rh-multi-prime-continuation-candidate-bundle-v2`; positive bundles require separate manifest-listed base and fixed-input higher-precision audit artifacts. Frozen one-prime bundle format and behavior remain unchanged.

Production piecewise images in `cert/prime_power_terms.py` expose `PiecewisePolynomial.legendre_coefficients`, representing `t=(x-(lower+upper)/2)/((upper-lower)/2)`. Global monomial `coefficients` and global translation/integration helpers are removed from that production module. An empty local coefficient tuple denotes the zero image on an inactive cell.

Phase 9 implementation/equivalence verification passes `159/159` focused and `696/696` default Python tests. The real frozen `192/196` candidates at Arb 384 and `104/56` bits still fail final even pivots `95/97`. Fresh independent exact replay proves strict negative directions in both complete rounded candidate Schur matrices (`2/2`) and all four Arb-384/512 matrices (`4/4`); all eight matrix-stage widths contract (`16/16`). The positive overlap control and component packaging smoke are not substitute qualification. Full readiness remains **BLOCKED**; no frozen-target positive base/confirmation exists, no qualification ran, and no support/grid/criterion or theorem-admission change occurred. Exact inputs, source snapshots, commands and audits are retained in [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md).

### Native multi-prime exact witnesses

`cert/multi_prime_exact_witness.py` implements the candidate's exact witness path separately from frozen v1. Fraction-free integer midpoint elimination accumulates inverse unit-lower LDL rows directly; exact quotient/remainder rounding and native midpoint/radius congruence preserve the same dyadic witness and strict Gershgorin margin. The independent auditor remains separate. Cache and candidate-profile fingerprints include the backend.

Phase 11's one retained-input smoke produces identical full rounded candidate inputs/rejection and identical proper-block witness/margin. Actual N196 candidate time falls `541.946 -> 53.525 s`; complete 97-mode proper witness time falls `1306.928 -> 22.725 s`. This is not positive full-target evidence. Post-cutover focused/default Python pass `77/77` and `715/715`; twelve frozen/shared byte controls remain unchanged. The reassessed external allowance is two hours per fresh run, four hours for the pair, not a launch authorization or full-positive runtime bound. Native memory is not claimed measured. See the Phase 11 addendum in [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md). No further benchmark sweep or Phase 12 run occurred.


## Shared implementation

`rh_tools.py` contains the standard-library Laguerre recurrence, prime sieve, von Mangoldt prime-power enumeration, pole parameters, high-precision trace accumulation, Simpson integration, turning-scale helpers, numerical zeta-zero evaluation via pinned `mpmath`, the retained small-`u` phase approximation, and the exact uniform pre-turning stationary map derived in `A-20260820-005`.

## Interpretation rule

These scripts can:

- falsify proposed identities or bounds;
- reveal numerical localization and scaling;
- expose phase loss caused by absolute values;
- identify unstable cutoff regimes;
- guide which analytic lemma is worth attempting.
They cannot prove RH by numerical verification. Retained historical/manual research runs use the established `computations/` record structure (`record.md`, `plots/`, `data/`) with exact parameters and limitations. Canonical continuation-driver runs use the driver's self-contained continuation bundle (`summary.json`, scout/rigorous artifacts, candidate data, and `run-manifest.json`). Both formats must retain enough parameters, provenance, and limitations for audit and reproduction.