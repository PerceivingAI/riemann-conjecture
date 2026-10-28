# Native-thread budget for the complete T81/100 signed source

- **Created:** `2026-10-28T02:30:00Z`
- **Status:** `PASS_TIME_REDUCED_PAYLOAD_IDENTICAL_TO_RETAINED`
- **Scope:** execution performance of the frozen complete-source producer. No mathematical claim, no theorem admission, no change to any retained artifact.

## Question

The retained complete source (`build-whole-source-v1.py`, `C-0123` / `X-20261027-006`) runs as one process with one numerical-library thread and took `4591.961 s` inside the retained replay, or `4424.6 s` under the isolated stage instrumentation recorded in
[`../2026-10-27T230830Z-t081-execution-profile/`](../2026-10-27T230830Z-t081-execution-profile/record.md).
Those measurements attribute `72.0 %` of that wall time to the two `source(parity, …)` calls and `20.2 %` to `combined_square`, i.e. almost all of it to dense `arb_mat` products.

Question: does an explicit FLINT native-thread budget shorten that wall time while leaving every published number unchanged?

## Change

[`build-whole-source-v2.py`](build-whole-source-v2.py) is a copy of the frozen producer with exactly one behavioural difference: an explicit thread budget for the dense Arb products.

- `--threads N`, else `T081_THREADS`, else `available_cpu_budget()`.
- `available_cpu_budget()` reads the process affinity mask on Windows and `sched_getaffinity` plus a cgroup v2 `cpu.max` / v1 `cfs_quota_us` quota on POSIX, clamped to `os.cpu_count()`; nothing about this host is hardcoded.
- A budget above the detected allowance is rejected before any calculation.
- Inputs, pins, precisions (`source_precision 4608`, `bits 256`), parameters (`T=81/100`, `N=826`, `M=1652`, `K=86`), all arithmetic, both parities, all nine translation cells, all `2/3/4/5` mixed squares, both `VP` orientations, both infinite exteriors and the canonical allowance are untouched.

`flint.ctx.threads` drives `flint_set_num_threads`; the measured scaling below shows the installed `arb_mat` product honours it.

## Measurement

Single run each, identical inputs and precision, back-to-back on the same host (`6` logical CPUs reported by the detected allowance):

| phase | v1 (1 thread) | v2 (6 threads) | factor |
|---|---:|---:|---:|
| `quadrature` roots | — (inside 24.1 s unattributed) | 4.389 s | — |
| `combined_square` | 891.9 s | 310.913 s | 2.87× |
| `source` parity 0 | 1593.1 s (mean of two) | 662.845 s | 2.37× |
| `source` parity 1 | 1593.1 s (mean of two) | 684.518 s | 2.33× |
| process total | 4424.6 s | **1694.01 s** | **2.61×** |

Against the retained replay baseline (`4591.961 s`) the same run is `2.71×`.

The scaling is below the `3.4–5.1×` measured on isolated products
([`../2026-10-27T230830Z-t081-execution-profile/data/native-threading-v1.json`](../2026-10-27T230830Z-t081-execution-profile/data/native-threading-v1.json))
because the remaining wall time is Python-level work that no thread setting accelerates: `kernel_step` (`159.0 s` in v1), `legendre_values` (`133.8 s`), `residual_matrices` (`21.7 s`), element-wise matrix construction, `logarithmic_cell_moments` and polynomial composition inside `source`.

## Correctness evidence

[`data/comparison-v2-v1.json`](data/comparison-v2-v1.json) compares the fresh publication with the retained one:

- all six compressed matrix packets are byte-identical to the retained packets (`A_model-0/1`, `weighted_head-0/1`, `weighted_complete_tail-0/1`), same SHA-256 and same size;
- the source JSON is identical except `producer_sha256`, which is necessarily the hash of `build-whole-source-v2.py` (`960b9a71…`) instead of `build-whole-source-v1.py` (`0d37cc35…`);
- `status` is the unchanged `COMPLETE_INTERVAL_MATRICES_NOT_YET_POSITIVITY_VERIFIED`.

Because the mathematical payload is byte-identical to the payload the retained independent audit already accepted (`512946` triangular entries, `X-20261027-007`), no new containment check is needed for the numbers. The frozen consumer pins the v1 producer hash, so it would reject the v2 metadata even though the payload is identical; a v2 audit replay is therefore not claimed here and would require a consumer version carrying the v2 pin.

Thread count does not change the arithmetic identity of the published endpoints in this run, but that is evidence from one run, not a general determinism guarantee.

## Limits

- One run per configuration; no repetition median, no thermal or frequency control.
- The v2 process peak working set was not instrumented. The v1 single-process peak was `5.61 GiB`; v2 remains one process and does not duplicate matrices.
- Only the source producer is optimized. The independent analytical consumer (`9213.553 s`) is neither optimized nor phase-attributed beyond its total, and the exact sign phase (`33.565 s`) is untouched.
- No progress streaming, budget enforcement across stages, or constrained-resource qualification is implemented here.
- The `2.61×` is wall time on this host at this budget; larger or smaller allowances were not exercised.

## Reproduction

```text
uv run --locked python computations/2026-10-27T235900Z-t081-parallel-source/build-whole-source-v2.py \
  --inputs computations/2026-10-27T140745Z-t081-complete-gram-attempt/whole-inputs-v1.json \
  --output computations/2026-10-27T235900Z-t081-parallel-source/data/run-v2/source-v2.json

uv run --locked python computations/2026-10-27T235900Z-t081-parallel-source/compare-v2-v1.py \
  --source computations/2026-10-27T235900Z-t081-parallel-source/data/run-v2/source-v2.json \
  --output computations/2026-10-27T235900Z-t081-parallel-source/data/comparison-v2-v1.json
```

The v2 run directory `data/run-v2/` holds the fresh source JSON and six packets; the comparison record is regenerable from those bytes.
