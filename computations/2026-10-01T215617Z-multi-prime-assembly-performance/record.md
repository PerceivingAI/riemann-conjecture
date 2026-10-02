# Generic rigorous assembly performance hardening

- **Computation ID:** `X-20261001-001`
- **Created:** `2026-10-01T21:56:17Z`
- **Last updated:** `2026-10-02T09:49:35Z`
- **Status:** phases 1 through 3, 7, 8, 10 and 11 `COMPLETE`; native multi-prime exact-witness cutover verified; strict sufficient-Schur rejection preserved
- **Role:** tool improvement and exact operational verification, not integrated P9 qualification or theorem admission

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

## 2026-10-02T02:58:34Z. Phase 7 exact-safe multi-prime diagnostics

User authorized only Phase 7 of the prerequisite extension. This addendum preserves earlier phase measurements and failures. It does not retry P9 or implement the Phase 8 conditioning redesign.

### Cause and implementation

The recorded 128-bit screen failure was an unsafe Arb-to-binary64 conversion, not failed mathematical assembly. Candidate confirmation also compared working matrix widths as floats. New regressions demonstrate false nonincreasing-width decisions when two positive widths collapse to `0.0` or infinity.

Added `scripts/multi_prime_precision_diagnostics.py` for exact rational widths, radii and widest-entry midpoints. Frozen `scripts/precision_diagnostics.py` remains unchanged. The screen retains exact endpoints and widths. It scales each normalized midpoint matrix by a rigorously derived power of two before binary64 conversion, runs numerical eigendiagnostics in bounded units, then restores units exactly as rational diagnostic values. This does not turn numerical eigenvalues into rigorous spectral bounds.

A lost nonzero entry, unrepresentable basis norm or failed eigendiagnostic returns explicit unavailable status. The driver escalates precision, never treats that status as failed assembly or uses it to accept positivity or stable negativity, and does not bridge stability comparisons across an unavailable sample.

Screen width/sign/change comparisons, candidate working-width comparisons and exact margin-change tolerance decisions now use rational arithmetic. Existing `1e-3` stability tolerances and the screening `1e-12` scale floor are unchanged. Candidate matrix/witness controls remain independent of Arb precision. No arithmetic assembler, support/grid rule, theorem contract or verifier was changed.

The new workflow version is `multi-prime-continuation-driver-p9-phase7-v2`; cache contract is `multi-prime-continuation-driver-v2`. Source fingerprints include the new helper, so incompatible float-payload entries cannot be reused.

### Actual component verification

| Target | Wall seconds | Exact complement lower, decimal display | Maximum GP width, decimal display | Screen outcome |
|---|---:|---:|---:|---|
| `11/20,192` | 29.171 | 0.566208306786 | 2.14021119679e366 | `INSUFFICIENT_PRECISION` |
| `11/20,196` | 31.254 | 0.586774539056 | 9.84794725959e375 | `INSUFFICIENT_PRECISION` |

Both screens use Arb `128`, residual order `32`, no cache and the unchanged generic rigorous assembler. Both complete assembly, serialize valid exact rational diagnostics, confirm active terms `[2,3]`, and expose available scaled eigendiagnostics without conversion exceptions. Each single-rung component ladder correctly ends at `precision_limit_reached`, with no selected candidate and no established mathematical rejection. Timing includes assembly, diagnostic extraction and eigensolving; it is not an isolated assembly benchmark.

The real candidate CLI at the known one-prime overlap `T=2/5,N=40`, Arb `256`, comparison `128`, residual order `32`, matrix/witness bits `64/32`, returns positive exact margins. The driver's real fixed-input confirmation reassembles at `384` and returns `CANDIDATE_STABLE`, using exact width and margin comparisons. This overlap component smoke does not establish readiness at the `{2,3}` targets.

Focused P2/P3/P8, candidate/driver, assembly-equivalence, bundle, admission and frozen-v1 checks pass **144/144 in 36.74 s**. Numerical regressions cover widths and eigenvalue units outside binary64 range, nonzero-entry loss, unavailable diagnostics, no stability bridge across unavailable precision, exact width growth, and a margin change just beyond the existing tolerance that binary64 rounds onto its boundary.

Seven frozen v1 SHA-256 values match the earlier capture. `scripts/precision_diagnostics.py` and `scripts/cert/exact_prime_schur_common.py` are byte-identical to the retained phase 5 snapshot. Full Python/Rust/Lean, workspace rustfmt and retained-proof replay were not rerun. The recorded unrelated formatting failure remains unresolved.

### Reproduction and retained evidence

Base HEAD: `524b8c74eb19fb05ae9cd7ee3cc58b46af3f5e2f`; local Phase 7 changes are retained in `data/phase7-source-snapshot.zip`. `data/phase7-source-provenance.json` records 23 source/test hashes and runtime: Python `3.14.0`, python-flint `0.9.0`, NumPy `2.5.2`, SciPy `1.18.0`, Windows build `26300`.

`data/phase7-screen-command.json` contains the exact standalone `uv run --locked python -c` argv and working directory. It calls `_escalate_rigorous_screen()` sequentially for `192/196` with the settings above, writes `data/phase7-target-screens.json`, and asserts exact positive complements, exact widths and zero assembly failures. It does not call `run_driver()`, launch a scout or use caches.

Candidate CLI:

```text
uv run --locked python -m scripts.weil_multi_prime_support_candidate_check --support 2/5 --dimension 40 --prec 256 --compare-prec 128 --residual-order 32 --matrix-bits 64 --witness-bits 32 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase7-candidate-base.json
```

`data/phase7-confirmation-command.json` retains the exact standalone argv, and `data/phase7-confirmation-console.txt` retains its output. Base candidate and confirmation results are in `data/phase7-candidate-base.json` and `data/phase7-candidate-confirmation.json`. `data/phase7-focused-test-command.json` and `data/phase7-focused-tests.txt` retain the affected acceptance command and output. Frozen/shared helper checks are in `data/phase7-frozen-hashes.json`.

`data/phase7-process-cleanup.json` retains the independent Windows CIM scan after component verification. It finds zero matching verification/component survivors, excluding the identified live Eval harness. Whitespace and Markdown fence checks pass for the changed files.

**Phase 7 gate: PASS.** Conditioning remains unresolved; enormous intervals were not narrowed or hidden. Phases 8 through 12 remain unexecuted. P9 is NOT QUALIFIED; no theorem admission, retained proof, new claim or RH result follows.

## 2026-10-02T04:24:32Z. Phase 8 enclosure diagnosis and representation selection

**Diagnosis/selection gate: PASS. Frozen-target positivity gate: FAIL.** This is a timestamped successor to the unresolved conditioning observations above, not a rewrite of them. Production has not been cut over to the selected representation. P9 is NOT QUALIFIED; P10 remains blocked.

### Measurement scope and causal diagnosis

`scripts/profile_multi_prime_conditioning.py` is a manual generator-side diagnostic. Process-local patches evaluate the same full rigorous assembler using production-global monomials, direct cell-local monomial recurrence, or cell-local Legendre recurrence. Optional exact grouping preserves the existing potential moments. No driver qualification, cache, pool, admission or verifier path is invoked.

Profiles retain exact rational enclosure widths and maximum absolute coefficient bounds through exact basis conversion, translations, combined images, products, primitives, endpoints, integrals, `P`, `P_squared`, `PD^-1P`, `GP`, `A`, `GV`, `GR` and complete factor-3 Schur. Product/primitive/endpoint probes sample diagonal degrees `0,N//2,N-2,N-1`; coefficient and final matrix profiles are full. Basis-conversion profiles in local experiments are controls, not inputs to the local recurrences. Wall-clock output is not a conditioning or throughput acceptance measure.

At `N=192`, Arb 512, exact basis conversion itself has zero width. Global translated coefficient bounds reach `3.5486e143`; sampled square products have width `5.7240e141`, with endpoint width `1.0301e141`. `P_squared` width `3.5513e141` already accounts for nearly all final `GP=3.5533e141`. At lower precision, the low-composition term can instead dominate. Tail subtraction is not a universal explanation.

Local monomials reduce the arithmetic `GP` width to `1.6817e-46`, but translated coefficient bounds still reach `4.6327e35`. Local Legendre coefficients have maximum translated bound `1`, combined-image bound `1.1244`, and `GP` width `1.1764e-82`. No radius is clipped, and no midpoint replaces a rigorous integration value.

Arithmetic stabilization alone leaves production potential cancellation: at `192/196`, Arb 512, `A` widths remain `7.5119e-12/8.2100e-9`, `GV` widths `5.5924e-11/6.2474e-8`, and full-Schur widths `3.0382e-10/3.2762e-7`. Exact rational grouping of the potential coefficients is therefore part of the selected full numerical representation, not an optional claim of readiness from `GP` alone.

### Selected arithmetic: exact identity and enclosure argument

For each existing strict partition cell `[l,r]`, set `a=(l+r)/2`, `b=(r-l)/2>0`, `x=a+bt`. Expand canonical `L_n(a+bt)=sum_k q_nk(a,b)L_k(t)` directly:

$$
q_0=(1),\quad q_1=(a,b),\qquad
(n+1)L_{n+1}(a+bt)=(2n+1)(a+bt)L_n(a+bt)-nL_{n-1}(a+bt),
$$

using `t L_k=((k+1)L_(k+1)+k L_(k-1))/(2k+1)` (the second term is zero at `k=0`). For each basis image, sum every active signed translated term into `s_jk` before squaring. The existing partition and activity decisions are unchanged.

Orthogonality `integral_-1^1 L_k L_h=2 delta_kh/(2k+1)` gives exactly

$$
P_{ij}=\sum_{\text{cells}}b\sum_k\frac{2q_{ik}s_{jk}}{2k+1},\qquad
(P^2)_{ij}=\sum_{\text{cells}}b\sum_k\frac{2s_{ik}s_{jk}}{2k+1},\qquad
G_P=P^2-PD^{-1}P.
$$

The diagonal contraction is in the local polynomial basis, **not** a separation into prime-specific squares. The combined `s_i s_j` retains `P_2P_3+P_3P_2` and all other mixed terms.

Arb encloses the original shift/constants and every recurrence, sum, product, cell Jacobian and division by a positive exact integer. Induction gives coefficient enclosures for the exact affine polynomials; the exact norm identity then gives the same operator integrals. Repeated endpoint/shift dependencies may widen intervals but cannot narrow the true enclosure. Parity, self-adjoint symmetry and the original global basis norms remain exact. Complement losses, residual estimate and factor `3` are unchanged.

The prototype deliberately requires the canonical Legendre basis. A generic exact input polynomial can first be expanded in the global Legendre basis over rationals, then transformed linearly by the same recurrence, retaining its original exact norm. That is the mathematical extension, **not implemented generic-basis support**; production integration and its regressions belong to Phase 9.

### Required potential control: exact grouping

For exact coefficients `c_(2r)` of `phi_i phi_j`, write `ell=log(2)`, `H_k=sum_(j=1)^k 1/j`, `H_k^(2)=sum_(j=1)^k 1/j^2`,

$$
\alpha_r=2H_{2r+2}-H_{r+1},\quad
\beta_r=4H^{(2)}_{2r+2}-H^{(2)}_{r+1},
$$

$$
U=\sum_r\frac{c_{2r}}{2r+1},\quad
E=\sum_r\frac{c_{2r}\alpha_r}{2r+1},\quad
F=\sum_r\frac{c_{2r}(\alpha_r^2+\beta_r)}{2r+1}.
$$

The existing finite moment sums rearrange exactly to

$$
V_{ij}=E-2\ell U,\qquad
(V^2)_{ij}=2\ell^2U-2\ell E+\frac F2-\frac{\pi^2U}{6}.
$$

Compute `U,E,F` over exact rationals before converting to Arb or multiplying transcendental constants. Odd moments remain zero. For an orthogonal basis, `U=D_ii/2` on the diagonal and zero off-diagonal. This eliminates cancellation among independently rounded transcendental moments without changing any potential formula or proof bound.

### Measured full-matrix conditioning

Maximum absolute entry widths at Arb 512, `T=11/20`, residual order `32`:

| N | Representation | P_squared | GP | A | GV | Complete Schur |
|---|---|---:|---:|---:|---:|---:|
| 192 | Production global | `3.5513e141` | `3.5533e141` | `1.4326e68` | `5.5924e-11` | `1.8827e142` |
| 192 | Cell monomial, production potential | `1.5436e-46` | `1.6817e-46` | `7.5119e-12` | `5.5924e-11` | `3.0382e-10` |
| 192 | Cell Legendre, production potential | `2.1794e-83` | `1.1764e-82` | `7.5119e-12` | `5.5924e-11` | `3.0382e-10` |
| 192 | Cell Legendre, grouped potential | `2.1794e-83` | `1.1764e-82` | `3.9877e-83` | `1.6196e-152` | `6.5763e-82` |
| 196 | Production global | `5.7563e147` | `1.0489e148` | `6.8533e72` | `6.2474e-8` | `5.3628e148` |
| 196 | Cell monomial, production potential | `3.1696e-44` | `3.6386e-44` | `8.2100e-9` | `6.2474e-8` | `3.2762e-7` |
| 196 | Cell Legendre, production potential | `7.2204e-82` | `3.9421e-81` | `8.2100e-9` | `6.2474e-8` | `3.2762e-7` |
| 196 | Cell Legendre, grouped potential | `7.2204e-82` | `3.9421e-81` | `1.3195e-81` | `1.6494e-152` | `2.1290e-80` |

All eight retained matrix stages contract at each `128 -> 256 -> 384 -> 512` step for both selected-representation targets: `48/48` exact comparisons. No arbitrary width threshold substitutes for exact candidate acceptance.

Small experiments cover empty arithmetic (`T=1/4`), one prime (`2/5`), `{2,3}` (`11/20`), and `{2,3,4}` with `tau_2<1` (`7/10`). All full-entry reference overlaps pass; grouped `V/V_squared` overlaps the original moments. An independent exact affine reconstruction at degrees `0..9` and `100` rational inner-product pairs verifies the local identity.

### Candidate evaluation, strict negative directions and stop

Actual outward candidate construction reuses each genuinely assembled rigorous result and runs the existing exact Schur/witness algorithms. With both selected arithmetic and grouped potential at Arb 384, `64/32` and frozen-maximal `104/56` matrix/witness bits both fail the final even midpoint LDL pivot: `95` at `N=192`, `97` at `N=196`. These are retained stage failures, not claimed positive margins.

A separate exact diagnostic solves the leading even-block midpoint system and rounds a last-coordinate direction to 56-bit dyadics. Every coordinate is then evaluated against the **rigorous full Schur interval**, not just its midpoint:

| N | Exact interval Rayleigh upper, decimal display | Upper divided by original exact basis norm squared |
|---|---:|---:|
| 192 | `-0.139224102100` | `-1.50060485641e-5` |
| 196 | `-0.0452493461716` | `-2.93867348887e-5` |

The first column uses the retained nonzero, non-unit vectors. Raw endpoints and vectors remain exact rational strings. A fresh zero-float audit independently recomputes the upper-triangular midpoint-plus-radius enclosure, checks agreement with both exact interval endpoints, verifies the basis-norm normalization, and proves strict upper negativity: **`2/2 PASS`**. Initial standalone production and the final canonical diagnostic CLI both retain their inputs/audits.

This rejects the **sufficient grouped factor-3 Schur test** at the two frozen targets for the unchanged residual order/bound and complement. It does **not** prove negativity of the localized Weil form, refute RH, admit a v2 pair, or independently establish upstream transcendental enclosure correctness. Rust theorem verification was not invoked.

Direct residual-Gram evaluation is not selected. The identity `G_P=< (I-Pi)P phi_i, (I-Pi)P phi_j >` is unchanged, but upstream stabilization already resolves enclosure growth. A tighter evaluation of the same sufficient matrix cannot remove its strictly negative direction. Further precision or witness bits cannot establish its positive definiteness.

**Stop:** preserve the result, keep P9 NOT QUALIFIED/P10 blocked, and obtain a separate research decision before changing support, grid or acceptance criteria. Phase 9 and qualification are not started.

### Reproduction, source preservation and limits

```text
uv run --locked python -m scripts.profile_multi_prime_conditioning --dimensions 192,196 --precisions 128,256,512 --witness-precision 512 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase8-target-comparison.json
uv run --locked python -m scripts.profile_multi_prime_conditioning --dimensions 192,196 --precisions 128,256,384,512 --representations cell-legendre --group-potential --witness-precision 384 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase8-grouped-potential-targets.json
uv run --locked python -m scripts.profile_multi_prime_conditioning --dimensions 192,196 --precisions 384 --representations cell-legendre --group-potential --witness-precision 384 --matrix-bits 104 --witness-bits 56 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase8-frozen-max-candidates.json
uv run --locked python -m scripts.profile_multi_prime_conditioning --dimensions 192,196 --precisions 384 --representations cell-legendre --group-potential --rayleigh-check --matrix-bits 104 --witness-bits 56 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase8-rayleigh-cli.json
```

`data/phase8-commands.json` records all nine CLI commands. Versioned diagnostic snapshots preserve the initial comparison, grouped-potential, maximal-candidate and final Rayleigh-replay sources separately; each experiment carries its diagnostic source hash. `data/phase8-source-provenance.json` binds the final 25-input snapshot, including the provenance helper and locked dependencies. `data/phase8-production-preservation.json` confirms all 23 Phase 7 source/test inputs remain byte-identical.

`data/phase8-width-comparison.json` retains exact width ratios and contraction checks. `data/phase8-rayleigh-cli-N192-p384-cell-legendre.zip` and the corresponding `N196` ZIP retain complete even interval matrices and vectors, explicitly marked diagnostic/non-theorem. `data/phase8-rayleigh-cli-audit-source.py`, `data/phase8-rayleigh-cli-audit-command.json` and `data/phase8-rayleigh-cli-audit.json` retain the independently executed zero-float replay. Earlier standalone Rayleigh inputs and audit remain historical evidence.

`data/phase8-artifact-manifest.json` seals raw artifact bytes. `data/phase8-process-cleanup.json` records a separate Windows CIM scan with zero matching diagnostic/audit survivors, excluding the identified Eval harness; this is not an OS-wide containment claim. No permanent test was added and no full Python, Rust, Lean, formatting or retained-theorem replay tier was rerun for this diagnostic-only phase.

## 2026-10-02T05:44:54Z. Phase 9 production representation and replayable exact inputs

The user authorized production implementation after the Phase 8 rejection. This does not authorize a new support, grid, residual bound, precision cap or acceptance criterion. **Implementation/equivalence verification is complete; the full Phase 9 positive-candidate readiness gate remains BLOCKED.** P9 is NOT QUALIFIED and P10 upgrade closure remains blocked.

### Production cutover and generic-basis identity

`scripts/cert/prime_power_terms.py` replaces global shifted monomial coefficients and primitive/endpoint integration with cell-local Legendre recurrence and exact diagonal local norms. `PiecewisePolynomial.legendre_coefficients` explicitly represents `t=(x-(lower+upper)/2)/((upper-lower)/2)`; an empty tuple is an inactive-cell zero image. The obsolete global-coordinate production helpers and `coefficients` field are removed, not aliased.

Every exact input polynomial is decomposed as `phi_i=sum_k a_ik L_k` by finite native rational leading-coefficient elimination. The Phase 8 exact affine identity then applies linearly: local coefficients are `sum_k a_ik q_kj(a,b)`. No canonical-basis assumption remains in the production operator. The existing exact orthogonality/norm check retains each original `D_ii`; reflection parity is certified from input coefficients, not mode indices. Reordered, scaled, mixed-parity and sparse high-degree bases therefore use the same exact projection/tail-Gram identity.

All active signed images are combined before squaring, so mixed terms remain present. `GP=P_squared-PD^-1P` is unchanged. Rigorous active enumeration, strict partition/activity, empty arithmetic, `tau_2<1`, `m=4`, complement losses, residual order/bound and grouped factor `3` remain unchanged.

`scripts/cert/multi_prime_legendre_schur.py::_potential_matrices` now contracts the exact harmonic `U/E/F` moment coefficients before introducing Arb constants, using the identity retained in Phase 8. Odd moments and certified opposite-parity entries remain zero. Potential and residual quantities have not been omitted or sharpened.

The diagnostic CLI now uses production for `cell-legendre` and grouped potential. Global/cell-monomial and ungrouped-moment implementations remain explicitly historical controls confined to that diagnostic, not production fallbacks. The stage profiler follows the new numerical helpers.

### Replayable candidate and bundle contract

`run_candidate()` retains full outward-rounded `A/GV/GP/GR`, rounded `c_T/rho_R` and prime complement losses, support/dimension/controls, basis convention, factor, both exact dyadic witnesses and exact margins in `audit_inputs`. Witness failures retain the completed exact rounded inputs with `status=WITNESS_FAILED`, without inventing successful witnesses.

`scripts/audit_multi_prime_candidate.py` accepts only the pre-theorem `rh-multi-prime-candidate-audit-v1` format. It checks dimensions/coordinate coverage, symmetry/parity, dyadic resolutions, prime-power identities and scalar/loss relationships. It independently derives `mu_N` and `A-(3/mu_N)(GV+GP+GR)`, then evaluates congruence centers and radii with native exact rational matrices rather than generator interval/LDL/congruence helpers. Both strictly positive Gershgorin margins must equal the serialized claims.

Positive multi-prime bundles publish separate manifest-listed base and qualified fixed-input higher-precision audit files. Missing, conflicting, corrupted or changed-control proof inputs prevent the completion seal. One-prime publication remains unchanged. Multi-prime format is now `rh-multi-prime-continuation-candidate-bundle-v2`; workflow/cache versions are `multi-prime-continuation-driver-p9-phase9-v3` / `multi-prime-continuation-driver-v3`. Source fingerprints include both the auditor and publisher; old cache entries are incompatible.

These are rational proof-arithmetic audits, not v2 theorem certificates or admission. Upstream transcendental Arb enclosures and analytic operator bounds remain assumptions. No Rust whitelist bypass, permissive verifier mode, new claim or automatic promotion was added.

### Exercised numerical acceptance

- Focused Python acceptance: **`159/159` in `26.36 s`**. Independent exact small action/Gram references cover reordered/scaled and mixed-parity bases; tighter enclosures cover sparse degree-62/63 mixed bases, real narrow `p=3` cells and all structural windows. Existing one-prime bridge, mixed-square, `{2,3,4}`/`tau_2<1`, threshold, frozen-v1/admission and P8 consistency gates pass.
- Full default Python, including ordinary integration: **`696/696` in `372.58 s`**.
- The first focused run had `156` passes and two fixture failures. Synthetic `tau=3/4,5/4` generated coincident breakpoints, correctly rejected by unchanged strict topology. The intended success fixture now uses `9/8`; a separate coincidence-rejection regression preserves the rejection. Production topology was not relaxed.
- Numerical/adversarial proof tests recompute real complement/Schur/congruence margins and reject corrupted witnesses, matrices, parity, scalar losses, resolutions, factor, reported margins, promotion flags and missing/changed confirmation inputs. Obsolete mechanism/call-count and role-copy tests were removed rather than pinned to the new implementation.
- Actual diagnostic-control CLI at `N=12`, Arb `128/256`, completes all six representation comparisons. The production stage-profiler CLI also completes.

The real one-prime overlap control `T=2/5,N=40` yields positive exact margins at fixed `64/32` bits and Arb 256. The existing confirmation helper genuinely reassembles at 384 and reports `CANDIDATE_STABLE`; both complete serialized audit inputs independently replay in fresh CLI processes, **`2/2 PASS`**. A throwaway publication smoke seals both actual audit payloads through the production publisher, then removes its temporary bundle. Its retained report explicitly says `component_packaging_smoke_not_qualification`; it is not an integrated driver run or frozen-target success.

### Frozen targets: rounded sufficient-Schur rejection

The production diagnostic executes `T=11/20,N=192/196`, residual order `32`, Arb `384/512`, with actual outward candidate construction at 384 and frozen-maximal `104/56` bits. Both candidates complete rounding but fail final even midpoint LDL pivots `95/97`. Higher-precision rows are full assembly/Rayleigh diagnostics, **not successful candidate confirmation**.

| N | Complete Schur width at Arb 384 | Width at Arb 512 | Normalized strict negative Rayleigh upper, decimal display |
|---|---:|---:|---:|
| 192 | `1.9942e-43` | `6.5763e-82` | `-1.50060485641e-5` |
| 196 | `6.4573e-42` | `2.1290e-80` | `-2.93867348887e-5` |

All eight matrix-stage widths contract at `384 -> 512`, **`16/16` exact comparisons**. Complete failed-candidate rounded matrices/scalars are retained in ZIPs; all four rigorous even Schur interval matrices and 56-bit dyadic vectors are retained separately.

A fresh independent zero-float audit checks exact vector/norm arithmetic and interval quadratic forms for all four Arb directions, **`4/4` strictly negative**. It also reconstructs `mu_N` and the complete rounded factor-3 Schur matrices from the failed-candidate inputs and proves the same retained directions have strict negative upper bounds, **`2/2`**. This establishes that neither enclosure width nor coarse outward rounding accounts for the witness failures.

There is no positive frozen-target base candidate or successful confirmation to publish. The one-prime control is not substituted for that missing criterion. The sufficient-Schur rejection does not prove localized Weil-form negativity or an RH counterexample. **Stop before changing support, grid or acceptance.** P9 remains NOT QUALIFIED/P10 blocked.

### Reproduction and retained bytes

```text
uv run --locked --extra test python -m pytest -q tests/test_prime_power_terms.py tests/test_prime_power_local_legendre.py tests/test_multi_prime_legendre_schur.py tests/test_multi_prime_potential_grouping.py tests/test_multi_prime_assembly_performance.py tests/test_multi_prime_candidate_audit.py tests/test_multi_prime_p4_stages.py tests/test_multi_prime_precision_diagnostics.py tests/test_multi_prime_continuation_driver.py tests/test_continuation_bundle.py tests/test_one_prime_v1_freeze.py tests/test_admission_consistency.py tests/test_v2_adversarial_consistency.py tests/test_pre_theorem_boundary.py
uv run --locked --extra test python -m pytest -q
uv run --locked python -m scripts.profile_multi_prime_conditioning --dimensions 192,196 --precisions 384,512 --representations cell-legendre --group-potential --witness-precision 384 --rayleigh-check --matrix-bits 104 --witness-bits 56 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-targets.json
uv run --locked python -m scripts.weil_multi_prime_support_candidate_check --support 2/5 --dimension 40 --prec 256 --matrix-bits 64 --witness-bits 32 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-overlap-base.json
uv run --locked python -m scripts.audit_multi_prime_candidate --input computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-overlap-base-audit-inputs.json --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-overlap-base-audit.json
uv run --locked python -m scripts.audit_multi_prime_candidate --input computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-overlap-confirmation-audit-inputs.json --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-overlap-confirmation-audit.json
```

`data/phase9-source-provenance.json` binds the dirty 30-input production/test snapshot and 12 frozen/shared byte-identical controls. All Phase 8 raw artifacts remain historical evidence. `data/phase9-verification-summary.json` records actual gates and the initial fixture correction; `data/phase9-precision-contraction.json` retains exact ratios.

The measurement snapshot retains the exact tested numerical sources. `data/phase9-final-source-snapshot.zip` also retains the final source tree: the only later Python change corrects the assembler's module description of grouped potential arithmetic. `data/phase9-final-integrity-checks.json` proves unchanged executable AST, binds both source snapshots and maintained-document hashes, and checks syntax, whitespace and Markdown fences. All `31` Phase 8 raw artifacts remain byte-identical; no historical numerical evidence is rewritten.

`data/phase9-overlap-confirmation-command.json` and its source retain the actual confirmation/publication argv. Both `phase9-overlap-*-audit-inputs.json` files retain successful proofs; both `phase9-overlap-*-audit.json` files retain independently recomputed positive margins. `data/phase9-packaging-smoke.json` records packaging only, not qualification.

`data/phase9-targets-candidate-N192-p384-cell-legendre.zip` and its `N196` counterpart retain failed-candidate exact rounded inputs. `data/phase9-targets-N192-p384-cell-legendre.zip` and the three other dimension/precision ZIPs retain rigorous Rayleigh inputs. `data/phase9-negative-exact-audit-source.py`, command JSON and audit JSON retain the independent replay of both raw and rounded sufficient Schur matrices.

`data/phase9-commands.json` records CLI invocations; `data/phase9-artifact-manifest.json` seals raw bytes. `data/phase9-process-cleanup.json` retains an independent scoped Windows process scan. No fresh Rust/Lean/retained-proof replay or workspace-formatting tier was run; no integrated qualification, cache reuse, precision-cap increase or theorem admission occurred.

## 2026-10-02T06:23:49Z. Phase 10 closes workspace formatting separately

The user authorized the four-file formatting cleanup independently of arithmetic and qualification. Rustfmt 1.9.0-stable changes only `crates/rh_engine/src/laguerre.rs`, `lib.rs`, `sieve.rs` and `main.rs`; edition is 2021 and `skip_children=true` prevents recursive edits. Before/after snapshots retain all nine engine source/test inputs, including five byte-unchanged controls.

The separate patch contains line wrapping, whitespace/newline normalization and optional trailing commas only. A source-token comparison retains literal/comment text, identifiers and operators, ignoring whitespace, CRLF line-comment terminators and optional trailing commas before closing delimiters. The initial checker retained CR in comments and falsely flagged differences; only that checker normalization was corrected. Production code received no corrective behavioral edit.

**Phase 10 COMPLETE. Gate PASS.**

| Check | Observed result |
|---|---|
| `cargo fmt --all -- --check` | Exit `0`, complete workspace |
| `cargo test --locked -p rh_engine` | `11` unit + `4` integration tests, `15/15`; empty binary/doc-test targets pass |
| `cargo clippy --locked --workspace --all-targets -- -D warnings` | Exit `0`, strict complete-workspace Clippy |
| Actual `rh_engine prime-trace` CLI | `8/8` rows match independent small finite references |

The CLI smoke exercises the formatted binary, exported library, Laguerre batch and sieve/prime-power code at `s0=3`, degrees `1..4`, cutoffs `16,32`, segment size `32768`. Independent integer trial division recognizes prime powers. Explicit polynomials `1`, `2-t`, `3-3t+t^2/2`, `4-6t+2t^2-t^3/6` replace the engine recurrence in the reference. Prime sums, exact pole values, discrepancies and absolute-value roots match with `1e-12` relative/absolute tolerance. It is a behavior smoke, not a performance measurement or theorem claim.

```text
rustfmt --edition 2021 --config skip_children=true crates/rh_engine/src/laguerre.rs crates/rh_engine/src/lib.rs crates/rh_engine/src/sieve.rs crates/rh_engine/src/main.rs
cargo fmt --all -- --check
cargo test --locked -p rh_engine
cargo clippy --locked --workspace --all-targets -- -D warnings
cargo run --locked -p rh_engine -- prime-trace --s0 3 --n-max 4 --cutoffs 16,32 --segment-size 32768 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase10-cli-smoke.json
```

`data/phase10-engine-before-formatting.zip` and `data/phase10-engine-after-formatting.zip` retain exact inputs/outputs; `phase10-formatting-only.patch` isolates this phase from existing arithmetic work. `phase10-formatting-scope.json` binds source hashes and token comparison. `phase10-rust-checks.json` retains actual argv, exit codes, timings and full stdout/stderr. `phase10-cli-smoke.json` and `phase10-cli-smoke-check.json` retain actual output and independently checked values. `phase10-artifact-manifest.json` seals raw bytes and unchanged Phase 9 evidence; `phase10-process-cleanup.json` records an independent scoped process scan.

All `30` Phase 9 source/test inputs and `30` raw artifacts remain byte-identical. The verifier and mathematical contract did not change, so no Python, `rh_cert` test, Lean or retained-proof tier was repeated. Strict workspace Clippy does include `rh_cert`, but does not substitute for its theorem replay.

The historical workspace-formatting blocker is closed. The frozen sufficient-Schur rejection is unchanged; P9 remains NOT QUALIFIED and P10 upgrade closure remains blocked. No support, grid, precision cap, cache/workflow version, theorem admission or qualification changed. Phases 11 and 12 have not started.

## 2026-10-02T09:49:35Z. Phase 11 acceptance and native exact-witness cutover

The user clarified that this plan improves computational tools for later research. Mathematical positivity is not engineering acceptance. The support/grid, operator/complement bounds, grouped factor `3`, strict proof margins and admission remain frozen. Historical positive-candidate gates and their failures above are preserved rather than rewritten.

### Acceptance and actual preflight

Before the witness cutover, `phase11-acceptance.json` retains focused Python `170/170` in `22.23 s`, default Python `696/696` in `372.55 s`, workspace Rust `82/82`, complete workspace formatting, strict complete-workspace Clippy and retained raw-byte/independent theorem replay `8/8`. `phase11-source-provenance.json` and its ZIP bind 42 dirty-worktree source inputs and all unchanged frozen numerical settings.

Isolated assembly measurements, seconds:

| Arb bits | N=192 | N=196 |
|---|---:|---:|
| 128 | 20.659 | 21.547 |
| 256 | 22.266 | 24.733 |
| 384 | 24.520 | 25.705 |
| 512 | 23.183 | 24.983 |
| 640 | 23.085 | 24.961 |
| 768 | 24.289 | 26.640 |

Bounded two-worker pairs take `23.745/27.260/26.759 s` at Arb `128/512/768`, including lifecycle. The actual eight-resolution floating component over the frozen 28-dimension grid takes `10.588 s`. These are components, not integrated qualification.

`phase11-preflight.json` retains the actual two-worker `192/196` screen ladders, all four ordered precision attempts per target, diagnostics and owned-worker cleanup. Both naturally classify `MATHEMATICAL_NEGATIVE`; the complete pool takes `109.598 s`. Eight separate actual candidate calls at Arb `512/640/768`, `64/32`, and Arb 512, `104/56`, retain their full rounded inputs. Independent Fraction arithmetic reconstructs their positive complements and factor-3 Schur matrices; all eight have strict negative interval quadratic-form upper bounds. This rejects the sufficient matrices, not localized Weil positivity or RH.

Fresh overlap controls `T=2/5,N=40` genuinely confirm `512 -> 640` and `640 -> 768` with fixed `64/32` and no cache. Four fresh-process exact audits pass; independently rebuilt 640-bit base inputs equal the earlier 640-bit confirmation inputs exactly. These controls are not positive frozen targets or Phase 12 runs.

### Performance implementation after the excessive measurements

The initial strategy ran eight expensive candidates and two complete witness probes, consuming about 96 minutes. The user interrupted that strategy and required tool implementation rather than further benchmarking. No later benchmark sweep was run.

The measured shared Fraction implementation spent `313..510 s` in failed even LDL and `715/785 s` in triangular inversion for complete 95/97-mode witnesses. The implementation cutover is confined to `scripts/cert/multi_prime_exact_witness.py` and multi-prime imports/fingerprints. Frozen `exact_prime_schur_common.py`, one-prime callers, certificate exporter and Rust PASS semantics remain unchanged.

The new implementation scales the exact midpoint to an integer matrix and performs fraction-free symmetric Bareiss elimination. It accumulates elimination rows concurrently; each row divided by its positive diagonal is the inverse unit-lower LDL row. Positive leading determinants preserve the exact LDL pivot rejection order. Integer quotient/remainder rounding preserves nearest dyadic values with half ties away from zero. Native `fmpq_mat` products compute exact congruence centers and radii, `W C W^T` and `|W| R |W|^T`, with the same strict Gershgorin margin.

No inverse heuristic, floating approximation, weakened interval bound or positivity assumption replaces verification. The candidate's full exact audit payload and independent audit implementation remain unchanged. The new backend is included in cache and candidate-profile fingerprints; source changes invalidate old keys without a serialized-contract/version change.

### One real-path smoke and post-cutover verification

`native-witness-cutover-smoke-source.py` executes one actual frozen candidate and one retained positive proper-principal-block witness. It does not search dimensions or run the driver.

| Same retained input | Shared Fraction path | Native path | Observed ratio |
|---|---:|---:|---:|
| Actual N=196, Arb 512, matrix/witness 104/56 candidate | 541.946 s | 53.525 s | 10.125 |
| Complete 97-mode proper principal witness | 1306.928 s | 22.725 s | 57.512 |

The actual candidate retains identical complete rounded inputs and the same final even-pivot rejection. The proper principal witness and strict margin are exactly identical to the retained original and independently replay with native zero-float arithmetic. This proper block is not a positive full target, a support/grid change or a theorem.

Post-cutover focused acceptance passes `77/77` in `13.07 s`; the full default Python suite passes `715/715` in `436.21 s`. New mathematical regressions compare exact witnesses/margins against the untouched Fraction reference, including mixed signs, unequal radii, large rationals outside binary64, dyadic ties, singular/negative pivots and interval-margin rejection. All twelve frozen/shared byte controls pass. Rust, Lean and theorem replay are not rerun after the Python-only backend cutover; their source/contract inputs remain unchanged.

### Cost, memory and execution boundary

`phase11-cost-structure.json` accounts for the entire frozen driver: eight screen assemblies, at most 32 base candidate attempts and four higher-precision candidates, 44 total assemblies, sequential candidate/confirmation work, native bundle audits, cache hashing/publication, live output, result freezing, manifest-last sealing and cleanup. Counts are a conservative operation envelope, not a jointly reachable execution or runtime bound.

`native-witness-cutover-cost.json` withdraws the obsolete 60-hour legacy draft. The actual unchanged scout/screen component sum is `120.186 s`; a five-minute fresh-run estimate is a planning inference with unmeasured integrated overhead. Applying the single new complete-witness sample to the conservative operation envelope gives a `48.691 min` proxy. Twice that is `97.382 min`; the new external allowance is **two hours per fresh run, four hours for Run A/B**. This does not authorize launch or guarantee a full positive-target runtime. Neither complete 98-mode target parity nor integrated cache/live/bundle costs was newly measured.

Observed isolated assembly high-water marks are `95.5..125.6 MiB`; failed legacy target candidates are `240.3..263.6 MiB`; complete legacy proper-block witnesses peak at `276.4 MiB`. Real screen workers peak at `140.4/143.3 MiB`, parent at `114.5 MiB`. These are process-lifetime observations, not simultaneous aggregate memory. Native smoke did not measure memory; no native memory improvement or positive integrated-workflow memory bound is claimed. Stage profiles attribute remaining assembly costs mainly to potential matrices, exact/local Legendre inner products and diagonal Gram composition.

### Retention, cleanup and outcome

`phase11-*` artifacts preserve all pre-cutover commands, timings, profiles, exact rejected inputs and positive controls. `native-witness-cutover-*` artifacts preserve the implemented source snapshot, same-input smoke, full Python output, replacement cost model, frozen hashes and raw-byte manifest. The independent scoped Windows CIM scan finds zero matching survivors. It does not claim OS-wide containment.

The first historical-source preservation check used the Phase 9 measurement snapshot and found the already documented post-verification assembler module-description difference. The correct final Phase 9 snapshot resolves that difference; no source was changed to satisfy the check. Historical numerical data remains byte-preserved.

**Phase 11 tooling acceptance COMPLETE.** Target rejection is valid tool output, not engineering failure. Phase 12 has not launched; historical P9 positive-candidate qualification remains NOT QUALIFIED. No new admitted v2 pair, certificate, theorem claim or RH proof exists.

