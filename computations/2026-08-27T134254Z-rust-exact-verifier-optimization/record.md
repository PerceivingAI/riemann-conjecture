# Rust exact verifier parity/triangular optimization

- **Computation ID:** `X-20260827-003`
- **Created:** `2026-08-27T13:42:54Z`
- **Last updated:** `2026-08-27T13:42:54Z`
- **Status:** `COMPLETE`
- **Type:** `TOOLING PERFORMANCE / EXACT SEMANTIC EQUIVALENCE`
- **Supports:** `A-20260826-001`, verifier infrastructure for `C-0050` through `C-0054`
- **Git base before optimization:** `ed2e48ebf3805b0622c3bb701346b70045130799`

## Objective

Reduce the rapidly growing runtime of the independent zero-float Rust exact verifier before the Legendre dimension grows materially beyond `N=68`, without changing certificate syntax, proof semantics, arithmetic types, PASS/FAIL criteria, or CLI exit semantics.

The pre-optimization retained-certificate replay profile had become material to continuation work. Approximate timings recorded immediately before this slice were

```text
N=32  ~11 s
N=40  ~25 s
N=48  ~54 s
N=56 ~102 s.
```

No comparable clean pre-optimization `N=68` timing is claimed here.

## Implementation

The optimization preserves full certificate validation and the pure `BigRational`/exact-interval trust base.

1. `RationalInterval::scale_by` now multiplies an interval by an exact rational scalar directly. This is mathematically identical to multiplying by a point interval, but uses two endpoint products instead of the generic four-product/min-max path.
2. `rh_cert` still validates every full `N x N` matrix for exact symmetry and exact opposite-parity zeros, but the theorem verifier constructs the even and odd Schur blocks directly. It no longer materializes a full Schur matrix and then copies parity blocks out.
3. Exact congruence multiplication exploits the already-validated lower-triangular witness support and skips exact-zero witness coefficients.
4. For symmetric theorem matrices, the congruence path uses `A C^T = (C A)^T`, computes only one output triangle, and mirrors it exactly.
5. The public generic congruence helper retains its prior semantics for non-symmetric matrices; a dedicated regression checks this so performance does not narrow an unrelated API contract.
6. No dependency, certificate-format, whitelist, theorem contract, or formal statement changed.

## Exact-equivalence tests added

- rational scalar interval multiplication is compared exactly against generic point-interval multiplication for positive, negative, and zero coefficients;
- optimized congruence is compared exactly against a retained naive dense reference on a symmetric mixed-sign rational interval example;
- the generic public congruence helper is separately checked on a non-symmetric matrix.

## Benchmark method

The optimized debug verifier was built once with

```text
cargo build -p rh_cert --quiet
```

and the retained theorem certificates were replayed sequentially using

```text
target/debug/rh_cert.exe verify --cert <certificate> --json
```

in one observable process. Timings are wall-clock seconds from that run.

| Claim | N | Prior approximate replay | Optimized replay |
| --- | ---: | ---: | ---: |
| `C-0050` | 32 | ~11 s | 3.564 s |
| `C-0051` | 40 | ~25 s | 6.145 s |
| `C-0052` | 48 | ~54 s | 13.210 s |
| `C-0053` | 56 | ~102 s | 24.880 s |
| `C-0054` | 68 | not retained | 31.408 s |

Because the older timings are approximate, the corresponding speedups are also approximate: about `3.1x`, `4.1x`, `4.1x`, and `4.1x` for `N=32,40,48,56` respectively.

## Semantic replay

A second independent replay compared each newly emitted verifier JSON object with the retained historical Rust-verification JSON object using parsed JSON equality.

```text
C-0050: exit 0, passed=true, exact_json_match=true
C-0051: exit 0, passed=true, exact_json_match=true
C-0052: exit 0, passed=true, exact_json_match=true
C-0053: exit 0, passed=true, exact_json_match=true
C-0054: exit 0, passed=true, exact_json_match=true
```

Thus scope, tail lower bound, Schur factor, exact even/odd margins, notes, and PASS result are unchanged—not merely the final boolean.

## Adversarial replay

The real `C-0054` certificate was mutated in temporary files only.

```text
wrong Schur factor 3 -> 2:
    exit 2
    contract validation failure

contract-valid matrix[0,0] -> -1:
    exit 1
    passed=false
    even block=false
    odd block=true
```

The optimized negative-diagonal theorem-failure replay took approximately `31.558 s`.

## Acceptance checks

```text
cargo fmt -p rh_cert -- --check
cargo test -p rh_cert --quiet
cargo clippy -p rh_cert --all-targets -- -D warnings
```

All pass. `cargo fmt --all --check` remains blocked by pre-existing unrelated formatting drift under `crates/rh_engine`; no `rh_engine` file was changed in this slice.

## Execution note

An initial attempt to collect a fresh pre-optimization five-certificate baseline through a non-observable long Portus batch crossed the execution boundary and left duplicate wrapper processes. Those process trees were identified and terminated. No output from that abandoned attempt is used in this record. All optimized timings and equivalence results above come from later single observable sessions.

## Interpretation

This is an implementation-efficiency result only. It does not strengthen any mathematical theorem and does not change the independent verifier's trust model. The retained theorem corpus is semantically identical under the optimized verifier while replay cost is reduced by roughly a factor of three to four over the previously measured `N=32..56` range.

The optimization is sufficient to remove the immediate verifier-performance blocker to further one-prime continuation. If exact-rational normalization again becomes dominant at substantially larger dimensions, deeper arithmetic changes should be profiled and justified separately rather than changing the certificate format preemptively.

## Limits

- benchmark timings are machine/debug-build dependent;
- prior baseline values are approximate and are not asserted for `N=68`;
- no claim is made about asymptotic complexity beyond the concrete retained corpus;
- RH remains unresolved.
