# Execution profile of the frozen complete T81/100 source and audit

- **Created:** `2026-10-28T02:32:00Z`
- **Status:** `PARTIAL_SOURCE_PROFILE_COMPLETE_AUDIT_PROFILE_NOT_PRODUCED`
- **Scope:** execution measurement of unchanged frozen programs. No mathematical claim, no theorem admission, no modification of any frozen or retained byte.

## What was measured

[`instrument-t081-v1.py`](instrument-t081-v1.py) imports the frozen producer or consumer byte-for-byte from an isolated tree rebuilt from the retained `55`-destination capture, wraps the program's own top-level functions with wall/CPU timers, samples process working set, and accounts for child processes through a Windows job object. [`measure-t081-execution-v1.py`](measure-t081-execution-v1.py) drives the pair.

Completed: the full source profile, [`data/source-profile-v1.json`](data/source-profile-v1.json).

| stage | calls | exclusive wall | share | CPU/wall |
|---|---:|---:|---:|---:|
| `source` (both parities) | 2 | 3186.1 s | 72.0 % | 0.992 |
| `combined_square` | 1 | 891.9 s | 20.2 % | 0.992 |
| `kernel_step` | 2 | 159.0 s | 3.6 % | 0.991 |
| `legendre_values` | 37,996 | 133.8 s | 3.0 % | 0.999 |
| `residual_matrices` | 1 | 21.7 s | 0.5 % | 0.981 |
| `publish` | 512,946 | 6.3 s | 0.1 % | 1.148 |
| unattributed (roots, validation, gzip, JSON) | — | 24.1 s | 0.5 % | — |

Process totals: `4424.6 s` wall, `4389.4 s` CPU (ratio `0.992`), peak working set `5.61 GiB`, no child processes.

Not produced: the audit profile. The audit pass was stopped during execution at the owner's instruction; no audit profile, no paired byte-identity assertion, and no driver summary (`data/execution-profile-v1.json` does not exist). The source profile alone was never verified against the retained publication by that driver.

## Supporting probes

- [`data/native-threading-v1.json`](data/native-threading-v1.json) — identical inputs at `ctx.threads=1,2,3,6`: CPU/wall reaches `4.85–5.14`, and a `413×413` product at `6144` bits falls from `40.39 s` to `7.78 s`. `ctx.threads` therefore does engage FLINT threading through the public API.
- [`data/work-unit-costs-v1.json`](data/work-unit-costs-v1.json) — bare process spawn `47.8 ms`, spawn plus `import flint` `97.7 ms`; one `413²` publication packet is `3.64 MB` compressed / `12.94 MB` raw, decompress+parse `0.10 s`, encode+compress `0.58 s`; `arb_mat` cannot be pickled, so a parallel work unit must exchange published dyadic integers or recompute.

## Known defect in this bundle

The sampled-stack fields (`stack_samples`, `stage_stack_samples`) are wrong and must not be used. The sampler reported the outermost frame instead of the innermost, so nearly all samples read as `main` lines; and only `243` samples were taken in `4424.6 s` because long Arb calls hold the GIL and starve the sampling thread. Stage timings, CPU/wall ratios, memory figures and child accounting are unaffected: they come from function-entry/exit timers and the OS counters, not from sampling.

The retained file is left as produced rather than rewritten; within-`source` attribution in
[`../2026-10-27T235900Z-t081-parallel-source/record.md`](../2026-10-27T235900Z-t081-parallel-source/record.md)
comes from the operation shapes and the measured per-cell cost, not from these samples.

## Instrumentation cost

Measured in-process: `GetProcessMemoryInfo` `2.7 µs`, stack capture `0.5 µs`, thread enumeration `39.6 ms` (sampled every `15 s`), sampler period `50 ms`. Stage-entry/exit memory queries and `publish` wrappers account for roughly `10 s` of the reported wall time. The `1.148` CPU/wall ratio on `publish` is wrapper overhead on very short calls, not real parallelism.

## Reproduction

```text
uv run --locked python computations/2026-10-27T230830Z-t081-execution-profile/measure-t081-execution-v1.py \
  --output computations/2026-10-27T230830Z-t081-execution-profile/data/execution-profile-v1.json
```

The driver rebuilds the isolated tree from `captured-source-inputs-v1.json`, runs the producer and then the consumer, and asserts byte identity of the fresh source, six packets and audit before writing its summary.
