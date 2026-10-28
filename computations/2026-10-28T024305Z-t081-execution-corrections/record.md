# Complete-source execution corrections and retained-packet identity

- **ID:** X-20261028-001
- **Created:** 2026-10-28T02:43:05Z
- **Last updated:** 2026-10-28T03:25:55Z
- **Status:** PASS_SOURCE_EXECUTION_CORRECTIONS_AND_RETAINED_PACKET_IDENTITY
- **Scope:** Fixed T81/100 complete-source execution and measurement. No new mathematical claim or production admission.

## Objective and preserved evidence

Correct the resource, measurement and rejection defects found in the uncommitted [execution profile](../2026-10-27T230830Z-t081-execution-profile/record.md) and [native-thread source](../2026-10-27T235900Z-t081-parallel-source/record.md). Preserve their code, records, manifests and outputs verbatim. All213 manifest members in those two bundles plus the original qualification, candidate and full-replay checkpoint pass their hash/size checks. Their five original manifests are also unchanged.

This is a new measured run, not a reconstruction of the earlier source v2 timing receipt. That earlier reported elapsed time and phase table remain historical evidence with the limitations identified below.

## Versioned corrections

1. Scoped Git `-text` rules preserve the fingerprinted LF/CRLF bytes in both original measured bundles and this bundle. With the host's `core.autocrlf=true`, filtered and unfiltered Git hashes now agree for the original producer. No original file was normalized or re-fingerprinted.
2. [Producer v3](build-whole-source-v3.py) uses the pinned [execution resource policy](execution_resources_v1.py). The non-Windows path no longer references an unimported module. The policy resolves process affinity, actual Linux CPU-controller membership/mounts, visible ancestor quotas, and the configured cgroup-v1 period. It records fractional-quota treatment and falls back conservatively on discovery errors. Explicit CLI limits take precedence over the environment and cannot exceed the detected allowance.
3. [Measurement driver v2](measure-t081-execution-v2.py) checks owned-tree removal after context exit. Actual subprocess-driven regression fixtures cover successful and failing cleanup. Source/audit/both selection is explicit; this correction did not rerun the complete analytical audit.
4. [Instrumentation v2](instrument-t081-v2.py) retains the OS working-set high-water counter through a final observation, distinguishes nullable Linux private memory from virtual address space, and labels sampled private maxima as sampled. It selects the innermost matching Python frame, but explicitly warns that GIL-starved stack samples are not time attribution. Child metrics unavailable from the observer are null. Coarse mode avoids per-entry timer wrappers while retaining inclusive phase timings.
5. [Strict comparer v3](compare-v3-v1.py) rejects changed packets, descriptor fingerprints/sizes, source metadata, JSON types, duplicate keys and unauthorized producer fingerprints. It checks actual retained and fresh packet bytes against the fixed independently audited source. Only substitution of the explicitly supplied producer's SHA256 is allowed in source metadata. Failure returns a nonzero exit and does not publish a passing report.
6. [Benchmark summary](summarize-benchmark-v1.py) compares inclusive phase timings with inclusive timings. The earlier table compared v1 exclusive891.945397/3186.119898s against v2 inclusive values. Those phase ratios are not like-for-like. This record uses the original inclusive fields instead and does not rewrite the earlier record.
7. [Benchmark runner](run-source-benchmark-v1.py) retains complete stdout/stderr, argv, elapsed time and code/input/log fingerprints. The successful [execution receipt](data/run-v3/execution-receipt-v1.json) names the code actually executed. A type-sensitive checker was added while that run's pins were frozen, so its internal comparer v2 and intermediate report remain as produced. Final qualification additionally requires [v3 identity](data/run-v3/identity-v3.json), and the summary requires that v3 result. The earlier local comparer is not the final identity authority.

The11 original mathematical helper functions are AST-identical to the frozen v1 producer. T81/100,N826,K86,M1652, source4608/publication256 bits, nine translation cells, signed2/3/4/5 images combined before squaring, every mixed square, both VP orientations, complete residual and both infinite exteriors are unchanged.

## Actual full-source measurement

The run started at2026-10-28T02:53:17Z and finished at2026-10-28T03:23:22Z, on Windows/Python3.14.0/python-flint0.9.0. It selected one process and6 native threads from the actual affinity allowance. Inputs retain SHA25619eac80d7869fcc6d6ddd0d33dcb90901b65254b2f076c6964148575019982a1. The [raw profile](data/run-v3/instrumentation-v2.json), [stdout](data/run-v3/source-stdout.txt), [stderr](data/run-v3/source-stderr.txt) and [derived summary](data/benchmark-summary-v1.json) are retained.

| Metric | Frozen v1 | Corrected v3 | Ratio, old/new |
| --- | --- | --- | --- |
| Native-thread budget | 1 | 6 | Not a speed ratio |
| Combined square inclusive wall, seconds | 943.497 | 315.153 | 2.99x |
| Both source calls inclusive wall, seconds | 3429.042 | 1452.590 | 2.36x |
| Program-main wall, seconds | 4424.638 | 1804.360 | 2.45x |
| Program CPU, seconds | 4389.359 | 4276.938 | 1.03x |

The corrected process's OS peak working set is6,621,491,200 bytes, or6.17GiB. Its sampled private-memory maximum is5,416,038,400 bytes, not an OS private-memory high-water measurement. The old5.61GiB value sampled current working set and is not a comparable true peak. This run does not establish absence of a memory regression.

One run per configuration, different full/coarse instrumentation levels, and uncontrolled host/thermal/frequency activity limit the performance claim. The demonstrated benefit is for this unchanged source workload on this host. No general scaling law or mandatory process-decomposition conclusion follows from it.

## Correctness and qualification

The final strict check passes all six compressed packets with identical bytes, sizes and SHA256 values. Complete source metadata is equal after only the producer-hash substitution, including JSON value types. The new source SHA256 is9bf110dea8a1f74f168fd3362debf2722690e9c66d4bc07f27f170f5aa4c3ad2; its producer SHA256 is4555cd6179ac26b190880790a100c997091996c6d961b97d1dd4860f0e2a8bf7. The original independently audited source identity remainsf69fee0feb9c08833ad6a3091718c9a6a301e5b5ddbea96ee5f0f6c0553c8b6e.

Analytical containment is inherited by exact identity to those already reconstructed packets. No updated consumer was used to pretend that the frozen producer pin accepts different metadata, and no full analytical reconstruction or new exact-sign execution is claimed here. The source status remains COMPLETE_INTERVAL_MATRICES_NOT_YET_POSITIVITY_VERIFIED.

The [focused qualification](data/correction-qualification-v1.json) and [raw JUnit report](data/qualification-tests-v1.xml) retain43 collected/passing test functions. The XML aggregate reports45 while containing43 testcase elements; it is preserved without alteration. Coverage includes actual Windows one-CPU affinity/over-budget rejection, nested v1/v2 quotas and periods, fractional/malformed limits, altered packet/metadata rejection, JSON numeric/boolean type substitutions, OS peak/final sampling, innermost frames, real subprocess failure reporting and temporary-tree cleanup.

Actual installed Python3.12.13 passes the CPU-policy CLI, strict checker against the original measured publication, syntax compilation of the new tools and a synthetic allocation-target profiler CLI. Its [runtime receipt](data/python312-runtime-smoke-v1.json) claims stdlib-tool behavior, not Python3.12 FLINT arithmetic. The only installed WSL distribution is docker-desktop and has no python3 executable, so no live Linux run is claimed. Linux parser behavior is fixture-tested.

## Commands and reproducibility

Executed full-source command:

```text
uv run --locked python -B computations/2026-10-28T024305Z-t081-execution-corrections/run-source-benchmark-v1.py --output-dir computations/2026-10-28T024305Z-t081-execution-corrections/data/run-v3
```

Executed final gates:

```text
uv run --locked python -B computations/2026-10-28T024305Z-t081-execution-corrections/compare-v3-v1.py --source computations/2026-10-28T024305Z-t081-execution-corrections/data/run-v3/source-v3.json --producer computations/2026-10-28T024305Z-t081-execution-corrections/build-whole-source-v3.py --output computations/2026-10-28T024305Z-t081-execution-corrections/data/run-v3/identity-v3.json
uv run --locked python -B computations/2026-10-28T024305Z-t081-execution-corrections/summarize-benchmark-v1.py --run-dir computations/2026-10-28T024305Z-t081-execution-corrections/data/run-v3 --identity-check computations/2026-10-28T024305Z-t081-execution-corrections/data/run-v3/identity-v3.json --output computations/2026-10-28T024305Z-t081-execution-corrections/data/benchmark-summary-v1.json
uv run --locked --extra test python -B -m pytest -n 0 -q tests/test_t081_execution_corrections.py tests/test_t081_profile_v2.py tests/test_t081_comparer_v3.py
```

For repetition use a fresh output directory and fresh comparison/summary names; existing evidence is refused, not overwritten. The runner's internal v2 comparison is intermediate. Final qualification requires the v3 checker and summary shown above.

## Remaining limits and mathematical boundary

This is a source-only fixed-target improvement. The independent analytical consumer is unoptimized. No general process pool, streaming heartbeat/progress service, complete memory-budget enforcement, Windows job CPU-rate detection, hidden-cgroup-ancestor detection or larger-host scaling qualification is supplied.

The prior full T81/100 captured replay remains valid. Its nine substantive adversarial cases and final conjunctive smooth-test acceptance remain unexecuted and paused. No C-0124, retained T81/100 smooth-test release, production admission, support extension, global positivity family or RH result is created by this execution work. Production inventories remain8v1/0v2/1v3. RH is unresolved.
