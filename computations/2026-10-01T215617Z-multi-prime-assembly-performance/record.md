# Generic rigorous assembly performance hardening

- **Computation ID:** `X-20261001-001`
- **Created:** `2026-10-01T21:56:17Z`
- **Last updated:** `2026-10-02T00:29:37Z`
- **Status:** phases 1 through 3 `COMPLETE`; phase 4 measurements/checks executed, readiness gate `BLOCKED`
- **Role:** isolated performance measurement and implementation verification, not P9 qualification

## Original phase 1 and 2 objective

Execute only phases 1 and 2 of `notes/ADD_PLAN.md`. Profile the current generic rigorous assembler, optimize measured hot operations without changing mathematics, and report exercised verification. Do not run the frozen P9 qualification or grant theorem status.

## Inputs and predeclared measurements

Support `T=11/20`, 128-bit Arb precision, residual order `32`. Baseline sequential dimensions `32,64,96,128`, with `160` only if feasible. Diagnostic assembly uses `require_positive_mu=False` so nonpositive small-dimension complements do not hide stage cost. This does not relax any qualification gate.

Stage instrumentation and uninstrumented timings are separate runs. Native polynomial operations are investigated only after stage measurements. The baseline source snapshots are retained before changing either generic module.

## Provenance and artifacts

`data/starting-provenance.json` records starting HEAD, pre-existing worktree changes, source/frozen-file SHA-256 hashes, lockfile, and test configuration identity. `data/baseline-prime_power_terms.py` and `data/baseline-multi_prime_legendre_schur.py` preserve the exact generic baseline source.

The manual profiler records Python/platform, installed package versions, CPU count, thread environment, source hashes, wall/CPU timings, process-lifetime peak working set, and diagnostic completion state. No continuation cache or internal process pools are used.

## Reproduction commands

```text
uv run --locked python -m scripts.profile_multi_prime_assembly --support 11/20 --dimensions 32 --mode stages --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/baseline-stages-32.json
uv run --locked python -m scripts.profile_multi_prime_assembly --support 11/20 --dimensions 32,64,96,128 --mode timing --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/baseline-timing.json
```

The source hashes in baseline output bind these measurements to the old implementation. Repeating the commands after implementation changes measures the new implementation, not the retained baseline. Use the retained snapshots for differential checks.

## First stage observation

The initial instrumented `N=32` assembly completed in `9.558 s` wall / `9.422 s` CPU. The residual truncation stage took `7.547 s` inclusive; potential matrices took `0.954 s`; combined low `P` and operator square took `0.357 s` and `0.367 s`. The residual path's exact inner products and Python Fraction polynomial convolution dominate this sample. Stage times are nested and must not be summed indiscriminately.

## Limitations

Measurements are performance evidence only. Small dimensions may have nonpositive complement; completed assembly is not an exact positive candidate. The historical one-hour two-worker P9 timeout remains a censored observation, not an isolated baseline duration. No P9 rerun, theorem admission, verifier change, or proof claim belongs to this record.

## Related material

`notes/ADD_PLAN.md`, `docs/MULTI_PRIME_CONTRACT.md`, `C-0058`, `C-0059`, `A-20260826-001`, and the retained P9 qualification record.

## 2026-10-01T22:39:34Z. Phase 1 and 2 results

### Measured cause and baseline scaling

At `N=64`, the instrumented residual stage took `50.892 s` of `78.121 s` total, potential matrices took `13.890 s`, and arithmetic `P/P_squared` took `4.168/4.372 s`. Exact residual inner products took `41.023 s` inclusive, primarily Python Fraction polynomial convolution. Baseline `N=32` cProfile found `math.gcd`, Fraction dispatch, Fraction multiplication, and Fraction addition among the hottest exclusive operations. Timings under cProfile include substantial instrumentation overhead and are not substituted for uninstrumented totals.

Uninstrumented baseline growth exponents were `3.081`, `3.412`, and `3.580` over successive dimension pairs. Extrapolating only the last segment predicts about `3831 s` at `N=192` and `1995 s` at `N=160`. These are estimates, not measurements. Baseline `160/192/196` were not run: the measured 15-minute `N=128` sample already explained the timeout and justified moving to optimization. The historical one-hour two-worker run remains separate, censored evidence.

### Implemented changes

- Exact basis validation and polynomial inner products use native `fmpq_poly` multiplication and definite integration. Arbitrary exact orthogonal bases still undergo validation; no unchecked Legendre/norm assertion was added.
- The new assembler uses the frozen potential moment formulas, computed once per degree, with native exact polynomial convolution. The frozen v1 file remains unchanged.
- The Suzuki residual uses the same split absolute-power integral, Taylor coefficients, and tail radius. Exact residual actions on occupied monomials are cached once per support/order/degree within the assembly, then combined linearly into basis images. Exact-image tests show coefficient equality with the frozen residual.
- Shifted arithmetic images use native Arb polynomial composition; term activity is certified once per partition interval and reused across basis indices.
- `P` and `P_squared` reuse the same combined piecewise images, converted to native Arb polynomials once. Product integration uses native Arb antiderivative evaluation on the shared interval endpoints. Mixed prime products remain present.
- Coefficient-certified parity skips opposite-parity entries and mirrors one triangle. Mixed-parity bases retain full computation; reordered bases do not use index parity.
- `D^-1` scaling is converted once per composition rather than inside every cubic-loop iteration. Precision-dependent data remains assembly-local.

The first native exact cutover reduced `N=32/64` to `1.175/10.502 s`. Native arithmetic products, cached interval moments, parity, and scaling then reduced `N=128` to `14.515 s` and `N=192` to `48.304 s`. Target profiling still measured `13.158 s` in repeated residual-image action and `7.243 s` in binomial shifts. Monomial-action reuse and native shift composition removed those costs. Native antiderivative integration replaced the intermediate Python cached-moment dot loop; it avoids exporting every product coefficient and allocating a moment table. Intermediate outputs remain retained rather than rewritten.

### Final before/after timings

All rows use `T=11/20`, 128-bit Arb, residual order `32`, diagnostic nonpositive-complement handling, sequential execution, and no continuation cache.

| N | Baseline wall s | Baseline CPU s | Final wall s | Final CPU s | Measured wall speedup | Final peak MiB |
|---|---:|---:|---:|---:|---:|---:|
| 32 | 9.490 | 9.250 | 0.165 | 0.141 | 57.4x | 45.8 |
| 64 | 80.324 | 77.438 | 0.894 | 0.828 | 89.8x | 49.6 |
| 96 | 320.340 | 311.203 | 2.738 | 2.672 | 117.0x | 56.5 |
| 128 | 897.221 | 881.562 | 6.779 | 6.703 | 132.3x | 69.8 |
| 160 | Not run | Not run | 14.198 | 14.031 | Not measured | 84.0 |
| 192 | Not run | Not run | 26.259 | 25.984 | Not measured | 101.5 |
| 196 | Not run | Not run | 28.069 | 27.750 | Not measured | 105.5 |

Peak memory is the lifetime high-water mark of the process running the dimension sequence, not isolated incremental memory per sample. The baseline table and all intermediate/final measurements retain their source hashes.

Final adjacent wall-time exponents over `32→64→96→128→160→192→196` are `2.435,2.760,3.151,3.313,3.373,3.232`. The measured speedup does not establish an asymptotic cubic bound; high-degree native product integration still dominates, and rational coefficient sizes grow with dimension. No target higher-precision or two-worker total-runtime estimate is claimed from these 128-bit single-process samples.

Final instrumented `N=192` took `26.495 s`. Combined native arithmetic product integration remains the largest cost at `13.237 s` inclusive across low `P` and operator-square assembly. The residual stage took `5.427 s`, including `4.700 s` in exact inner products; potential matrices took `2.429 s`; `GV/GR` diagonal composition took `2.247 s`; `GP` composition took `1.229 s`. Shift construction fell to `0.193 s` and absolute-power action to `0.467 s`. These nested values are not an additive breakdown of the total.

### Exercised verification

Focused acceptance passed `65/65` in `24.39 s`, covering new optimization references, P2/P3, P4, P5, P6/P8, and frozen v1 regressions. The four one-prime bridges and existing strictly nonzero cross-term checks passed. Added references compare complete small assemblies at multiple supports/precisions, exact residual image coefficients, arbitrary mixed-parity orthogonal bases, reordered parity bases, and zero-vector rejection. The exact-zero parity regression failed before the cutover and passes afterward. Enclosure ordering changes are checked by overlap; exact residual image equality and native rigorous operations establish the unchanged formulas, rather than treating overlap alone as a proof.

A real new-path candidate smoke at `T=2/5,N=40`, 256-bit Arb, residual order `32`, matrix/witness bits `64/32`, with 128-bit diagnostic comparison, returned generator-side `CANDIDATE_READY`. Approximate displays of its exact rational margins are `mu=0.7313021813837909`, even `0.004176569409177554`, odd `0.013120531469863986`; all exact margins are positive. All reported matrix/scalar widths were nonincreasing under the precision comparison. This is a one-prime overlap smoke of the new machinery, not a P9 result or a new theorem.

All seven frozen-file hashes match the starting raw-byte hashes. Both baseline source snapshots also match the captured originals. `git diff --check` passed with only line-ending warnings. An OS process scan found no remaining benchmark/candidate/pytest workers; the two live repository Python processes were explicitly identified as this Eval tool and its parent harness, not leaked research workers. Raw scan results and classification are retained in `data/phase12-summary.json`.

### Commands for the final implementation

```text
uv run --locked python -m scripts.profile_multi_prime_assembly --support 11/20 --dimensions 32,64,96,128,160,192,196 --mode timing --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/final-timing.json
uv run --locked python -m scripts.profile_multi_prime_assembly --support 11/20 --dimensions 64,192 --mode stages --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/final-stages.json
uv run --locked python -m scripts.profile_multi_prime_assembly --support 11/20 --dimensions 32 --mode cprofile --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/final-cprofile-32.json
uv run --locked python -m scripts.weil_multi_prime_support_candidate_check --support 2/5 --dimension 40 --prec 256 --compare-prec 128 --matrix-bits 64 --witness-bits 32 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/final-candidate-smoke-one-prime-bridge.json
uv run --locked --extra test python -m pytest -n 0 -q tests/test_multi_prime_assembly_performance.py tests/test_prime_power_terms.py tests/test_multi_prime_legendre_schur.py tests/test_multi_prime_p4_stages.py tests/test_multi_prime_continuation_driver.py tests/test_certificate_v2_contract.py tests/test_v2_adversarial_consistency.py tests/test_one_prime_v1_freeze.py
```

### Remaining gates and theorem boundary

Phases 3 and 4 are not closed by these focused checks. Additional structural/equivalence acceptance, full Python/Rust/retained-proof gates, target-dimension higher-precision and concurrent throughput measurements, and total frozen-run cost assessment remain before qualification. No claim is made that 128-bit target matrices are sufficiently conditioned or positive merely because assembly completes and the scalar complement is positive.

P9 was not run. Its support, grid, precision/rounding/witness ladders, worker limits, and criteria remain frozen. Production v2 admission remains empty. No theorem certificate, theorem admission, retained proof, verifier change, or RH claim was created.

## 2026-10-01T23:14:26Z. Phase 3 equivalence and regression guards

Phase 3 was separately authorized after phases 1 and 2. This addendum closes only that verification slice. No production implementation, driver, certificate contract, verifier, admission table, or qualification setting was edited.

### Exact identities and rigor

Native polynomial composition uses the same binomial identity `p(x+s)=sum_k p_k sum_r binom(k,r)x^r s^(k-r)`. Arb operations enclose the coefficients and endpoint evaluations. For every partition cell, integrating a product means multiplying the complete two polynomials, taking its antiderivative, and subtracting the endpoint values. The independent test-local reference performs binomial shifting and unskipped coefficient convolution/integration, builds activity separately for every basis/cell/term, and evaluates both matrix triangles.

For nonnegative integers `q,k`, split the residual action at `y=x`:

```text
I_q,k(x) = integral_-1^x (x-y)^q y^k dy + integral_x^1 (y-x)^q y^k dy
         = sum_{r=0}^q binom(q,r)/(r+k+1) *
           [ ((-1)^r-(-1)^(q-r)) x^(q+k+1)
             + ((-1)^(q-r)-(-1)^r*(-1)^(r+k+1)) x^(q-r) ].
```

The native implementation groups exactly these rational coefficients. Linearity permits computing `R_K x^k` once and combining the images with the exact basis coefficients. Tests compare every residual image coefficient with the frozen Fraction implementation, and prove that native and reference matrix balls both enclose the independently computed exact rational inner products. Native rational convolution and antiderivative evaluation are exact; converting the resulting rational to Arb is outward-enclosing, not a float approximation.

Potential matrices retain the frozen moment functions. Exact coefficient convolution followed by the finite moment sum changes evaluation order, not the polynomial product or integral. Every signed left/right translation pair, the even potential, and the `|x-y|` residual kernel commute with reflection. Exact homogeneous coefficient parity therefore makes opposite-parity entries zero; mixed-parity bases must not use that skip. `D` still contains the actual exact basis norms, including noncanonical rational rescalings.

The combined image is still `P phi_j=sum_m P_m phi_j`. Its image Gram contains all mixed terms. `GP=P_squared-PD^-1P`, the grouped factor `3`, complement contributions, and residual remainder are unchanged. These identities explain equivalence. Interval overlap alone is not used as a proof of a new formula.

### Coverage

- Complete small old/new assemblies at 128 and 256 bits cover empty arithmetic `T=1/4`, one-prime `2/5`, both two-prime supports `11/20` and `3/5`, and `{2,3,4}` at `7/10` with `tau_2<1`. Checks include active identities, exact norms, arithmetic norm bounds, all canonical matrices, `delta_R/rho_R/mu`, Schur availability, symmetry, and exact opposite-parity zeros.
- The same support grid compares 128-bit output with 384-bit optimized and independent reference enclosures. Both lower-precision formulations contain the tighter high-precision balls. At certified exact zeros, the unskipped reference must contain zero instead of requiring a zero-width ball to contain its roundoff width.
- Rationally rescaled/reordered homogeneous-parity bases retain exact norms and unskipped arithmetic agreement. A mixed-parity orthogonal basis retains nonzero arithmetic, potential, and residual cross entries. Nonorthogonal and zero-vector rejection remain guarded.
- Strict active-set threshold failures remain covered. Added piecewise tests reject exact, overlapping, and inactive shift boundaries; compressed-shift norm tests reject unresolved integer chain lengths rather than selecting a bound silently.
- Structural work bounds at dimensions 3 and 6 constrain shifts by `2*n*term_count`, activity by `2*term_count*cell_count`, and arithmetic integrations by twice the triangular same-parity pair count times the cell count. A full assembler guard requires one shared partition. Potential moment degrees cannot repeat; residual monomial-action coefficient work cannot exceed the occupied-degree/series-term bound. Every work bound is coupled to behavioral or exact-image references. Bounds permit fewer operations; there are no runtime thresholds.
- Real rigorous-screen cache tests isolate support and precision, check tighter `GP` widths, and verify hits on repeat. Mutating copied source bytes for each generic module independently forces recomputation through the actual source fingerprint. No production helper was added, so fingerprint inputs did not change.
- Real candidates use independent Arb/matrix/witness controls `256/64/32`, `256/72/40`, and `384/64/32`. Tests independently reconstruct dyadic outward bounds, the exact complement and factor-3 parity Schur blocks, and signed rational congruence/Gershgorin margins. A real nonpositive `T=2/5,N=24` candidate fails at the exact witness gate.
- Runtime file-open guards forbid both v2 acceptance corpora in the exercised scout/candidate paths. Production-source filename search finds only their documentation mentions, not Python/Rust implementation references. Existing v2 adversarial/admission and pre-theorem checks pass.

Presence-only, module-name-absence, and mocked diagnostic echo tests were removed rather than repinned. The four original v1 bridges and strictly nonzero mixed-square assertions remain unchanged.

### Observed verification

The final focused gate passes **121/121 in 34.49 s**, outer pytest sequential. Raw output is retained in `data/phase3-final-focused-output.txt`.

The initial narrow run reported one test-harness failure and 66 passes. The standalone frozen residual helper converts matrix rationals at its caller's ambient precision; the new test initially omitted the enclosing precision scope used by the actual v1 assembler. The corrected test supplies that scope and checks the exact rational integrals rather than pinning equal ball representations across different conversion orders. No production fix was needed. Initial and intermediate output remain retained.

The real CLI smoke at `T=2/5,N=40`, Arb `384`, comparison `128`, matrix/witness `72/40`, returns generator-side `CANDIDATE_READY`. Its exact positive rational margins are retained in `data/phase3-candidate-smoke-one-prime-bridge.json`; approximate displays are `mu=0.7313021813837909`, even `0.004176569432300938`, odd `0.013120531611009081`. Every reported width is nonincreasing. All theorem/admission/independent-verification flags remain false. This is a known one-prime overlap smoke, not qualification of the post-`p=3` target.

All four targeted production-stack hashes match `data/phase3-starting-provenance.json`. All seven frozen hashes also match the original phase 1 capture. The post-check process scan found no remaining matching verification workers, excluding the two identified live Eval harness processes. Test source hashes, raw process results, exact smoke margins, and gate metadata are retained in `data/phase3-summary.json`.

```text
uv run --locked --extra test python -m pytest -n 0 -q tests/test_multi_prime_assembly_performance.py tests/test_prime_power_terms.py tests/test_multi_prime_legendre_schur.py tests/test_multi_prime_p4_stages.py tests/test_multi_prime_continuation_driver.py tests/test_certificate_v2_contract.py tests/test_v2_adversarial_consistency.py tests/test_one_prime_v1_freeze.py tests/test_continuation_bundle.py tests/test_pre_theorem_boundary.py tests/test_admission_consistency.py
uv run --locked python -m scripts.weil_multi_prime_support_candidate_check --support 2/5 --dimension 40 --prec 384 --compare-prec 128 --matrix-bits 72 --witness-bits 40 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase3-candidate-smoke-one-prime-bridge.json
```

### Remaining gates

Phase 4 remains pending: target `192/196` higher-precision timings through `512` and possible `640/768` confirmation precision, contention/total-cost assessment, full Python/Rust checks, and retained `8/8` replay. None is inferred from the focused gate or small overlap smoke. P9 qualification and reproduction were not run; production v2 admission remains empty; RH remains unresolved.

## 2026-10-02T00:29:37Z. Phase 4 measurements and blocked readiness gate

Scope: phase 4 only. No qualification, reproduction, admission, mathematical settings, production implementation, or frozen v1 source changed. `data/phase4-predeclaration.json`, `phase4-benchmark-revision.json`, and `phase4-commands.json` retain provenance, the benchmark-only instrumentation revision, and exact commands. Diagnostic benchmarks did not overlap acceptance jobs or other benchmark groups. All measurements exclude continuation caches.

### Actual baseline comparison

Support `11/20`, residual order `32`, Arb `128`; wall/CPU seconds:

| N | Old wall / CPU | New wall / CPU | Wall / CPU speedup | Old / new peak MiB |
|---|---:|---:|---:|---:|
| 32 | 9.490 / 9.250 | 0.155 / 0.141 | 61.03 / 65.78 | 44.4 / 45.7 |
| 64 | 80.324 / 77.438 | 0.860 / 0.828 | 93.43 / 93.51 | 47.8 / 49.5 |
| 96 | 320.340 / 311.203 | 2.661 / 2.641 | 120.37 / 117.85 | 53.2 / 56.3 |
| 128 | 897.221 / 881.562 | 6.576 / 6.453 | 136.43 / 136.61 | 64.6 / 70.3 |
| 160 | unattempted | 13.877 / 13.844 | not measured | — / 84.0 |
| 192 | no isolated baseline | 25.530 / 25.344 | not measured | — / 101.4 |
| 196 | no isolated baseline | 27.490 / 27.438 | not measured | — / 105.2 |

Historical parallel `192/196` work was right-censored by the external execution boundary, not an isolated timing baseline. No extrapolated old speedups are reported. Memory is process-lifetime high-water working set, not independently attributable per-sample allocation. Exact data: `data/phase4-isolated-comparison.json`.

### Precision scaling and contention

Isolated wall / CPU seconds, then lifetime peak MiB:

| Arb bits | N=192 wall / CPU / MiB | N=196 wall / CPU / MiB |
|---|---:|---:|
| 128 | 25.530 / 25.344 / 101.4 | 27.490 / 27.438 / 105.2 |
| 256 | 31.313 / 31.062 / 107.9 | 33.572 / 33.344 / 113.8 |
| 384 | 32.830 / 32.672 / 111.1 | 35.220 / 34.984 / 117.3 |
| 512 | 34.893 / 34.750 / 114.2 | 37.460 / 37.219 / 121.2 |
| 640 | 36.972 / 36.672 / 117.8 | 39.572 / 39.312 / 124.8 |
| 768 | 39.205 / 38.906 / 120.5 | 41.951 / 41.812 / 128.5 |

At 512 bits, instrumented totals are `35.284/37.725 s`. Exclusive combined-prime polynomial integrations consume `59.74/59.78%`; exact residual inner products `13.03/12.96%`; potential-matrix work excluding its moment children `6.89/6.98%`. Full nested inclusive/exclusive records are in `data/phase4-stages-512.json`; overlapping nested timers must not be summed as independent costs.

Bounded two-worker spawn pair wall time, including startup/publication/shutdown: `28.467 s` at 128 bits, `38.208 s` at 512, `42.910 s` at 768. Relative to the sum of isolated samples, speedups are `1.863/1.894/1.891`. Worker assembly durations remain close to isolated durations; no substantial contention appears in these samples. The full eight-resolution, 28-dimension floating scout component takes `10.669 s` with three workers. This component benchmark does not select a candidate or run continuation.

### Exact candidate diagnostics: conditioning remains unresolved

Actual sequential `run_candidate()` cases use independent matrix/witness bits `64/32`. Every case fails closed in midpoint LDL witness construction:

| Arb bits | N=192 candidate seconds / max GP width | N=196 candidate seconds / max GP width | First failing pivot |
|---|---:|---:|---:|
| 512 | 149.949 / 3.553e141 | 161.785 / 1.049e148 | 57 |
| 640 | 209.058 / 9.961e102 | 225.400 / 1.616e109 | 67 |
| 768 | 273.969 / 2.819e64 | 298.370 / 4.574e70 | 77 |

The `N=192`, Arb `512`, maximum frozen matrix/witness `104/56` case also fails at pivot 57, taking `192.618 s`. Raising rounding/witness resolution cannot repair the enormous native arithmetic enclosures. Widths contract sharply with Arb precision but remain unusable even at the possible confirmation precisions. This is **unresolved conditioning, not a mathematical negative or theorem failure**. The higher-precision cases are diagnostic candidate calls, not successful candidate confirmations.

Failed-candidate peak working set reaches `183.5 MiB`; witness work, not assembly, dominates their cost (`109–250 s` at `64/32`). Exact rational widths and native complement enclosures are retained even for failed candidates. The real known overlap smoke at `T=2/5,N=40` still returns positive exact generator margins; it does not establish the target result.

### Frozen workflow cost model and predeclared allowance

`data/phase4-cost-model.json` preserves all frozen controls. It models two rigorous ladders at `128/256/384/512`, up to `16` matrix/witness combinations per dimension (`32` candidate calls), and up to two sequential higher-precision calls for each of two candidate dimensions (`4` confirmations). Each uncached candidate call reassembles; no reuse is assumed.

Measured contention extrapolates the two rigorous ladders to `138.496 s`. Maximum-bit candidate estimates are `207.821 s` at base 512 and `383.273 s` for higher-precision calls, using the measured `N=192` bit-cost ratio for the unmeasured `N=196` maximum-bit case. The measured failure-path extrapolation totals `2.348 h`, including scout and a **120-second unmeasured reserve** for screening eigendiagnostics, serialization and sealing. Observed progress JSON serialization/hash/fsync/atomic publication takes at most `0.0175 s` per write; no qualification bundle was sealed.

Successful full two-parity witnesses have not been measured. A factor-4 reserve on candidate/confirmation costs gives `9.167 h`; another 25% headroom gives `11.459 h`. Predeclared external allowance for any later explicitly approved unchanged-workflow run: **43,200 seconds / 12 hours**. These are estimates, not runtime upper bounds or permission to launch. Re-estimate after any separately approved conditioning redesign.

### Acceptance, integrity and stop decision

- Focused Python: **121 passed**, `33.47 s`.
- Full default Python: **647 passed**, `422.02 s`, two workers, including ordinary integration; manual `slow_acceptance`, `retained_proofs`, and `parallel_acceptance` tiers excluded.
- `cargo test -p rh_cert`: **67 passed** across ten suites.
- `cargo fmt --all -- --check`: **FAILED** in four untouched `rh_engine` files: `laguerre.rs`, `lib.rs`, `sieve.rs`, `main.rs`. Unrelated formatting was not rewritten.
- Supplemental `cargo fmt -p rh_cert -- --check` and strict `rh_cert` Clippy: **PASS**. Scoped formatting does not satisfy the failed workspace gate.
- Canonical retained byte-integrity plus independent Rust replay: **8/8 PASS**.
- All four production hashes match phase 3; all seven frozen hashes match the original phase 1 capture. Owned throughput/scout pools report verified cleanup with zero active children; the final OS process scan finds only the two identified live Eval harness processes.
- `git diff --check`: no whitespace errors; Git emits existing LF-to-CRLF advisory warnings.

Raw gate output, configuration/provenance, exact diagnostics, cost model and cleanup are retained under `data/phase4-*`. The new `scripts/profile_multi_prime_workflow.py` is manual benchmark instrumentation only and does not call `run_driver()`, use a continuation cache, or seal qualification.

**Readiness gate: BLOCKED.** Wall-clock assembly performance is now practical, but target arithmetic conditioning and the workspace formatting gate remain blockers. Stop before phase 5. A stable polynomial-coordinate/basis evaluation redesign is a separate explicitly scoped task; do not increase the frozen precision cap or change acceptance to hide the failure. No P9 qualification/reproduction, theorem admission, or RH proof claim occurred.
