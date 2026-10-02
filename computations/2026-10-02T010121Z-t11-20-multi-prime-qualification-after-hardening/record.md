# Frozen P9 extension after assembler hardening

- **Computation ID:** `X-20261002-001`
- **Created:** `2026-10-02T01:01:21Z`
- **Last updated:** `2026-10-02T01:25:32Z`
- **Status:** phases 5/6 execution and audit complete; P9 qualification gate `FAILED`, `NOT QUALIFIED`

## Objective

Execute phase 5 only of `notes/ADD_PLAN.md`. Let the unchanged canonical driver select dimensions and terminate naturally. User requested this run after the phase 4 readiness blocker report. This authorization does not make the blocked conditioning or workspace-formatting gates pass.

## Mathematical quantity tested

Generic exact-prime-power localized Weil Legendre-Schur continuation at `T=11/20`, exact active terms `[2,3]`, combined arithmetic square and grouped factor-3 `V,P,R` reduction. Candidate positivity remains generator-side evidence, never theorem admission or RH proof.

## Environment and source snapshot

HEAD `a26817d3e1bc22b6ed7aa3effefb96f172cb83fa`; working tree dirty. `data/predeclaration.json` records exact source hashes and driver fingerprint `558515583ef6c39456eccdc877fcf6fefc018dcdebe09bd564332cf3b2d530e6` before results. `data/starting-tracked.patch` preserves the tracked dirty patch; `data/source-snapshot.zip` preserves fingerprint inputs, operational helpers, project configuration and new untracked benchmark/test sources. No automatic commit. The retained phase 4 environment is Windows x64, Python 3.14.0, python-flint 0.9.0, NumPy 2.5.2 and SciPy 1.18.0; the driver also captures its actual runtime provenance.

## Inputs and parameters

Support `11/20`; grid `148..256 step 4`; scout resolutions/workers `8/3`; rigorous workers `2`; Arb ladder `128/256/384/512`; residual order `32`; matrix ladder `64/80/96/104`; witness ladder `32/40/48/56`; confirmation precision step/extra steps `128/2`. Expected scout selection `192/196` is not forced. Cache/output directories are fresh. Predeclared external allowance is `43,200 s`, following the phase 4 cost model; no intermediate positive result permits interruption.

## Reproduction procedure

```text
uv run --locked python -m scripts.weil_multi_prime_continuation_driver --support 11/20 --n-min 148 --n-max 256 --n-step 4 --scout-resolutions 8 --scout-workers 3 --rigorous-workers 2 --precision-start 128 --precision-max 512 --residual-order 32 --matrix-bits-start 64 --matrix-bits-max 104 --witness-bits-start 32 --witness-bits-max 56 --candidate-precision-step 128 --candidate-precision-extra-steps 2 --cache-dir computations/2026-10-02T010121Z-t11-20-multi-prime-qualification-after-hardening/data/cache-a --output-dir computations/2026-10-02T010121Z-t11-20-multi-prime-qualification-after-hardening/data/run-a
```

Any later reproduction must use this identical source snapshot and a separate fresh cache/output pair. No second execution is authorized in this phase.

## Output

No numerical outcome existed when this record was predeclared. The driver owns live state and manifest-last publication under `data/run-a`.

## Interpretation and limitations

Phase 4 target witnesses fail through Arb 768 and native combined-prime enclosures remain enormous. Workspace rustfmt also fails in four untouched `rh_engine` files. Neither blocker is hidden or repaired by launching this run. Any fail-closed terminal state must be reported as observed, not replaced by a forced candidate. Phase 6 audit/reproduction and theorem admission are out of scope. Historical Run A/C/E artifacts remain untouched.

## Related claims and records

`C-0058`, `C-0059`, active attempt `A-20260826-001`, performance record `X-20261001-001`, and historical qualification `computations/2026-10-01T192908Z-t11-20-multi-prime-qualification/record.md`. No new claim is admitted. RH remains unresolved.

## 2026-10-02T01:06:38Z. Natural terminal result

The driver ran from `2026-10-02T01:01:44Z` to `2026-10-02T01:04:32Z`. Observed tool wall time is **168.78 seconds**, well inside the predeclared external allowance. No external termination, manual dimension selection, precision-cap change, or acceptance override occurred.

All eight floating resolutions completed. The unchanged driver found stable-positive reconnaissance beginning at `N=192` and selected primary/fallback `192/196`. Both bounded rigorous workers exhausted the frozen precision ladder:

| Dimension | Arb 128 | Arb 256 | Arb 384 | Arb 512 | Terminal screen |
|---|---|---|---|---|---|
| 192 | `ASSEMBLY_FAILED` | `INSUFFICIENT_PRECISION` | `INSUFFICIENT_PRECISION` | `INSUFFICIENT_PRECISION` | `precision_limit_reached` |
| 196 | `ASSEMBLY_FAILED` | `INSUFFICIENT_PRECISION` | `INSUFFICIENT_PRECISION` | `INSUFFICIENT_PRECISION` | `precision_limit_reached` |

Both 128-bit screen attempts record `OverflowError: integer division result too large for a float`. This is the screen's failure report, not a mathematical rejection. At 512 bits, complements are certified positive with approximate lower bounds `0.5662083067859621` and `0.5867745390560106`, but `GP` maximum widths remain `3.553278510597645e141` and `1.048913732729125e148`. Midpoints are not precision-stable, and the diagnostic reasons include `negative_result_not_precision_stable`.

Final state is **`PRECISION_LIMIT_REACHED`**. No mathematical rejection was established. No rigorous survivor reached candidate construction; `candidate_runs` is empty, selected candidate/dimension are null, and theorem/admission/independent-verification flags remain false.

### Retained evidence and verification scope

- `data/driver-console.txt` preserves the tool-delivered driver console; `data/outcome.json` records observed timing, complete screening attempts, launch controls, and the reported lifecycle.
- `data/run-a/run-manifest.json` was emitted by the driver after bundle publication. The final summary, eight scout artifacts, eight rigorous attempt artifacts, and unreached candidate payload are retained.
- Observed manifest controls match every predeclared numerical setting. All captured source hashes and the before/after driver fingerprint match.
- The driver reports spawn workers, two executors shut down, five workers reaped, zero cleanup escalations and `active_children_after_cleanup=0`. This is scoped to driver-managed pools, not an independent OS-wide process audit.
- No tests or known failed checks were rerun to confirm the phase 4 results. Verification here is the actual canonical driver execution and its recorded outputs.
- Phase 6 manifest-listed raw-byte/path/size audit, independent cleanup audit, and reproduction were **not performed**. Emission of a final manifest is not a claim that its bytes have been independently audited.

### Interpretation and next action

Assembly wall-clock performance no longer prevents natural completion of this frozen run. Arithmetic conditioning still prevents rigorous positive selection under the fixed 512-bit cap. P9 remains **NOT QUALIFIED**, rather than `CANDIDATE_READY` or a mathematical negative.

The user-authorized launch did not turn the blocked phase 4 gate into a pass. Workspace formatting remains a separately recorded blocker. Preserve this outcome and the historical Run A/C/E records. A conditioning redesign requires a separate scope; do not raise the precision cap, extend the grid, force a candidate, reproduce automatically, or admit a theorem. RH remains unresolved.

## 2026-10-02T01:25:32Z. Phase 6 independent audit and fresh reproduction

User authorized phase 6. Run A's prelaunch reproduction procedure already required the same source and a separate fresh cache/output pair. `data/phase6-reproduction-predeclaration.json` binds the destinations to `cache-b/run-b`, verifies that neither exists before launch, and declares exact comparison rules before Run B. No warm-cache policy was chosen after seeing results.

### Reproduction and source identity

Run B uses the recorded Run A command, changing only `/data/cache-a` to `/data/cache-b` and `/data/run-a` to `/data/run-b`. All 19 captured source/configuration files match the source archive and Run A hashes before and after reproduction. The archive and dirty tracked patch also match their predeclared raw-byte hashes. All seven frozen v1 files match the original phase 1 capture.

| Run | Output directory under this bundle | Wall seconds | Final state |
|---|---|---:|---|
| A | `data/run-a` | 168.78 | `PRECISION_LIMIT_REACHED` |
| B | `data/run-b` | 169.39 | `PRECISION_LIMIT_REACHED` |

Both runs terminate naturally, with the exact frozen support, active set, grid, worker limits and independent bit/precision controls. Scout selection is `192` with fallback `[196]`; both `selected_dimension` and `selected_candidate_dimension` remain null. Both rigorous histories retain `128/256/384/512` in canonical order. The 128-bit float-conversion overflow and the later insufficient-precision diagnostics reproduce exactly. No mathematical rejection is established.

### Independent artifact and semantic audit

Each final manifest passes an independent **18/18 artifact** audit. Every listed relative path is canonical, contained in its run directory and unique; every listed file's actual byte count and raw SHA-256 match. Both manifests' ordered result-payload digests also match reconstruction from the summary and retained scout records. No live-state file substitutes for a completion manifest.

The audit checks manifest format/role, frozen controls, scout resolution/dimension ordering, stable-positive frontier, primary/fallback selection, complete ordered rigorous history, candidate/summary/manifest consistency, bounded spawn lifecycle, and every serialized theorem/admission boundary flag. `theorem_status`, `independently_verified`, `whitelisted`, and `automatic_promotion` remain false wherever present.

The completed rigorous screens at 256/384/512 exercise the source-bound generic combined `P_squared/GP` path and retain `GP` width/conditioning diagnostics. Full native matrices are not serialized by this continuation bundle. Per-term floating complement contributions are present; separate rigorous/exact candidate prime losses, exact rounded complement, positive even/odd witness margins, selected matrix/witness bits and fixed-input candidate stability were **NOT REACHED**. These missing success criteria are reported, not inferred from positive rigorous complements or floating reconnaissance.

At 512 bits, both runs retain the same approximate rigorous complement lower bounds `0.5662083067859621/0.5867745390560106` and `GP` widths `3.553278510597645e141/1.048913732729125e148`. Candidate lists remain empty.

### Exact recursive canonical comparison

**PASS, zero differences.** All 18 artifact payloads and the manifest are compared recursively with exact type/value equality and original array order. No numerical tolerance, rounding, diagnostic deletion or mathematical field exclusion is used.

The predeclared exclusions are only cache destination/cache-hit execution metadata; manifest start/end timestamps and parent PID; and manifest artifact SHA-256/result-payload digest values, which are independently audited against each run's raw bytes. Artifact sizes, paths, kinds, configuration, workflow decisions and all numerical diagnostics remain compared. Seventeen of eighteen artifact files are byte-identical; only `summary.json` changes due to its cache destination.

Reports retain every audited file's hash/size, actual excluded paths, canonical hashes and the empty difference list:

- `data/phase6-audit-run-a.json`
- `data/phase6-audit-run-b.json`
- `data/phase6-identity-selection-checks.json`
- `data/phase6-canonical-comparison.json`
- `data/driver-console-run-b.txt`

### Independent Windows cleanup check

Both drivers report two spawn executors shut down, five managed workers reaped, verified cleanup, zero escalations and zero active children. The separate post-run Windows CIM scan uses recorded driver PIDs `18000/10864`, PID/PPID ancestry, Python/uv/Rust executable names, command lines and repository/run paths. **Zero qualification-related survivors** remain after excluding the two explicitly identified live Eval harness processes. No process was terminated.

`data/phase6-process-cleanup.json` retains the raw relevant process rows and classification. Individual worker PIDs are not serialized by the driver, so the scan supplements its counts using recorded parents, ancestry and command lines. The OS scan is separate evidence from the driver's scoped owned-worker count.

### Performance and acceptance carried forward, not rerun

The phase 4 measurements and raw checks remain in `X-20261001-001`. Actual old/new 128-bit wall seconds are `9.490/0.155`, `80.324/0.860`, `320.340/2.661`, `897.221/6.576` at `N=32/64/96/128`, giving measured speedups `61.03/93.43/120.37/136.43`. Old target samples have no completed isolated baseline; historical parallel work remains right-censored, so no target speedup is fabricated.

Optimized isolated `N=192/196` costs are `25.530/27.490 s` at 128 bits, `34.893/37.460 s` at 512, and `39.205/41.951 s` at 768. Lifetime peak working sets reach `105.2 MiB` in the 128-bit grid and `128.5 MiB` in the 768-bit pair; failed candidate cases reach `183.5 MiB`. The original bottleneck was Python Fraction residual convolution. Retained optimizations use exact native convolution, assembly-local monomial reuse, invariant potential-moment tables, native Arb combined arithmetic operations, coefficient-certified parity and precomputed diagonal scaling. Exact residual identities, tighter interval references and equivalence gates remain recorded. After optimization, combined-prime integration dominates about 60% of 512-bit assembly; arithmetic enclosure conditioning, not runtime, blocks qualification. The estimated full successful-search allowance remains 12 hours, not a runtime bound; these fail-closed runs finish before the costly candidate stages.

Previously exercised gates are focused Python `121/121`, full default Python `647/647`, Rust `67/67`, strict Clippy, scoped `rh_cert` formatting and retained integrity/independent replay `8/8` PASS. Workspace rustfmt remains FAILED in four untouched `rh_engine` files. Manual Python acceptance tiers were excluded from the default suite. No known failure or full suite was rerun merely to confirm those results; phase 6 verification is fresh real reproduction, independent artifact audits, exact canonical comparison, source integrity and OS cleanup.

### Qualification gate and stop

Audits, canonical reproducibility and independent cleanup pass. The phase 6 qualification gate **FAILS** because neither run reaches `CANDIDATE_READY`, and the exact witness/stability requirements were not reached. P9 remains **NOT QUALIFIED**. No third retry, grid/support/precision change, source change, theorem admission or commit occurred.

`CANDIDATE_READY` is a tooling/qualification result only. It does not establish a localized theorem claim or admit `(11/20,N)` into v2. RH remains unresolved. A separately scoped stable arithmetic-evaluation redesign remains the next prerequisite; do not weaken the frozen controls or conceal the formatting blocker.
