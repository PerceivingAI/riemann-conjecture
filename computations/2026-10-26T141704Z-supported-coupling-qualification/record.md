# Supported-time source and complete coupling-error qualification

- **Computation ID:** `X-20261026-008`
- **Created:** `2026-10-26T14:17:04Z`
- **Last updated:** `2026-10-26T15:01:06Z`
- **Status:** `COMPLETE`
- **Claim / finding:** C-0114 / F-20261026-008
- **Outcome:** complete supported-source/error operation qualified; no full weighted Gram, sufficient positivity sign or usefulness comparison computed

## Objective and mathematical result

Qualify an explicit coupling estimate using the actual operator output restricted to the physical interval, rather than the whole-line representative rejected by C-0113.

[The contract](supported-coupling-contract-v1.md) derives the full supported polynomial action of the archimedean source. Its boundary logarithms are explicit through F(r)=atanh(exp(-r/2))+atan(exp(-r/2)), with a regular polynomial-difference integral and a complete residual bound. Both prime translations and the signed rank-two pole are retained. An exact time-supported step approximation Z has a proved complete L² source error, including endpoint caps, all cells, jumps, coefficient rounding and the infinite residual sum.

The resulting genuine supported Fourier representative gives the conditional energy-weighted penalty upper

    B*C^-1B<=eta^-1G_s(K).

For an approximation with operator error e and model Gram norm bound rho, the additional Gram charge is2rho e/sqrt(m)+e²/m. Complete finite-band integration, a proved BV/h infinite tail for the approximant and one-sided source errors supply an explicit finite acceptance operation. The unbounded weight is retained;1/m is used for the vanishing source remainder, not as the entire coupling estimate.

No time restriction/inverse/Fourier multiplication is assumed to commute. No weighted norm dominance under restriction is asserted. An outside-time witness now annihilates the real supported output, but that structural fact alone is not the qualification result: actual source approximation and complete errors are independently checked below.

## Inputs and unchanged numerical target

[Original declaration](qualification-inputs-v1.json), [refinement2](qualification-inputs-v2.json) and [refinement3](qualification-inputs-v3.json) all fix existing T3/4, normalized degrees0/1, reference N312, alpha1/4,beta873/1024,m1/3. The operation computes only these two source columns, not the full312-column low source.

All retain384-bit production,128 residual terms, endpoint caps T/2^32,64 subcells per graded doubling,96-bit arithmetic breakpoint enclosures,48-bit rational coefficients and individual norm accuracy1/16. The acceptance threshold is not relaxed. The reference outside hypotheses are inherited from C-0110/C-0111; no new support or discrepancy premise is silently assumed.

## Preserved numerical iteration and diagnosed cause

Every original input, implementation, output and command receipt remains intact. No historical variant is overwritten.

| Source variant | Even squared L² upper | Odd squared L² upper | Requested accuracy |
| --- | ---: | ---: | --- |
| v1, natural full-cell evaluation |91/65536|615/65536|Not met for odd column|
| v2, analytic derivative enclosure |89/65536|353/65536|Not met for odd column|
| v3, exact-cell jump classification |2/65536|23/65536|Met for both columns|

The first bounds were mathematically valid but failed the requested accuracy. The interior-cell charge dominated; endpoint and residual charges were small. [Refinement2](cell-enclosure-refinement-v2.md) preserves cancellation with the analytic smooth-source derivative, improving the enclosure without changing physical parameters.

The retained [branch diagnostic](data/branch-diagnostic-v1.json) then finds six jump branches where the exact rational cell is on one side, while a widened Arb storage ball overlaps the discontinuity. The old branch rule safely paid a jump across each whole neighboring cell. [Refinement3](exact-cell-branches-v3.md) carries exact partition endpoints into the branch decision and keeps actual uncertain slabs fully enclosed. This fixes avoidable overestimation, not an invalidated physical source. No grid, precision, support or target increase is used to obtain the qualified result.

## Qualified supported-source and Fourier results

The final packet stores2054 positive-half cells with both columns and exact reflection parity. It pays both endpoint caps and all omitted residual terms. The accepted two-column error square is25/65536, hence

    ||W(x0 p0+x1 p1)-(x0 Z0+x1 Z1)||
       <=(5/256)sqrt(|x0|²+|x1|²).

This is a bound on the two computed columns, not an error bound on every column of Pi312. It remains valid after projecting the true cross by Q312.

For the stored source approximants without low subtraction, K=0, the complete weighted Fourier-tail operator upper is below1/16 at U16384, about0.030411. Every doubling stage from256 is retained. A nonzero K requires its additional variation and model-error budget, not reuse of this number. The true logarithmically singular source is completed separately by the global L²-to-Gram error; it is not falsely declared BV. The finite weighted Gram integral has not been evaluated.

Actual Fourier controls at0,4,256 use entire step moments with full-source error sqrt(L)e_j. Normalized physical low-moment controls use error e_j. An independent positive-series calculation of the complete constant low entry fits its source enclosure. Exact non-Weil error geometry demonstrates the indispensable mixed Gram term and rejects a zero one-sided acceptance lower. These are source/error controls, not an accepted Schur sign or a new Weil-sign result.

## Independent verification

The [independent512-bit consumer](verify-supported-v1.py) imports no producer. It reconstructs the exact partition, all2054 cell ranges and both columns using log-form F, incomplete first moments, unimodal direct-sum derivative bounds and manual complete2/3/4 arithmetic. The negative odd pole is explicitly present. It verifies every published complete L² error, actual model norm/variation, full Fourier-tail ladder, point/moment completion and source scope.

All three original variants are independently checked. Versions1/2 return PASS_SOURCE_BOUNDS_TARGET_UNRESOLVED; version3 returns PASS_SOURCE_AND_ACCURACY. Valid earlier bounds are not silently promoted to meeting the target. [Independent mathematical, refinement and code/output review](independent-review.md) approves all derivations and acceptance directions, without performing the numerical runs itself.

Three actual altered packets reject with exit2 and no success outputs: missing physical cell, understated source error and unpaid Fourier infinity. [Rejection summary](data/rejection-summary.json) and exact attack inputs/receipts are retained. They are research source-accuracy packets, unrelated to production certificate versions or theorem admission.

## Reproduction and environment

Actual runtime is Python3.14.0/python-flint0.9.0. Baseline commit is `0a10e5aef2ee451d224028f7746c55369002b36f`; this new research source is uncommitted, not clean production-proof provenance.

Canonical qualified reproduction from the repository root, with fresh outputs:

```text
uv run --locked python -B computations/2026-10-26T141704Z-supported-coupling-qualification/build-supported-v3.py --output <fresh-source.json>
uv run --locked python -B computations/2026-10-26T141704Z-supported-coupling-qualification/verify-supported-v1.py <fresh-source.json> --output <fresh-audit.json>
```

Historical source variants use build-supported-v1.py or build-supported-v2.py with their own default input files and separate fresh outputs. The same independent consumer preserves their distinct target-unresolved outcomes. The branch diagnostic takes the v2 source packet explicitly and writes a fresh diagnostic. It never alters that packet.

[Thirteen captured files](source-v1/manifest.json) include all three producers, all three declarations, consumer, diagnostic, three imported project files and pyproject/lock. Captured imports are enforced under their own root and bytecode is disabled. All three source packets AND all three audit packets reproduce canonical bytes under isolated execution. The qualified variant3 hashes are:

- Source `b3b3578d778c9d7af5127ba218dde7d124d8dcb47b7f826e98c8913282c3612c`.
- Audit `9da33ed4b3110da4906e3c40c2f81215e45ca9433bb7c051c5a610aff4b39925`.

[Replay summary](data/replay-summary.json) retains every variant identity. Actual run receipts retain exact argv/cwd, stdout/stderr, exit codes and elapsed observations. The final source takes about2.68seconds and its first independent audit about43.97seconds; these are two-column workload observations, not a full-matrix speedup or a comparative benchmark.

[Preservation](data/preservation-check.json) verifies20 prior seals,1080 historical members and16 protected public source/test/configuration files unchanged. All individual scientific packets are under2MB. Source versions required to reproduce failed accuracy are kept rather than refactored away. Root byte-hash manifest is written last.

## Interpretation and limits

A concrete supported-time source operation is now independently qualified, with a complete conditional energy-weighted coupling/error contract. It does not repeat the unremovable outside-time component of the rejected representative. The old STOP remains correct for that old representation.

Actual full weighted coupling penalties, comparison with the older criterion, whole-low-space positivity, target-scale conditioning/work, support extension and an all-support mechanism remain unverified. Formal disappearance of one witness and accurate two-column source action do not establish any of them. High-degree polynomial and BV approximation costs may still be substantial.

Shared source and Arb/FLINT premises remain explicit. No new canonical full-domain identification, literature originality, root generic CLI/library upgrade, dependency, permanent test suite, cloud operation, Rust/Lean run or production admission. Frozen8v1/0v2/1v3 and RH unresolved are unchanged. No commit or push.
