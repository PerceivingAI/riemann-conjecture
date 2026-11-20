# Complete selected arithmetic through bounded persistence and independent reconstruction

- **Computation ID:** `X-20261030-001`
- **Created:** `2026-10-30T02:37:21Z`
- **Last updated:** `2026-10-30T12:17:32Z`
- **Status:** `QUALIFIED_SELECTED_COMPLETE_ARITHMETIC`

## Objective

Implement and exercise a real, complete selected linear arithmetic path: native producer, compressed exact checkpoints, owned fixed-order reduction, separate analytical reconstruction, exact physical-mass conversion, endpoint payment and actual interruption/recovery. A completed entry is not an entire source matrix or a positivity certificate.

## Mathematical quantity and complete domains

For ordinary Legendre polynomials L_n, T=81/100, tau_a=log(a)/T and c_a=log(p)/sqrt(a), compute

```text
P_mn = -sum_a c_a [integral[-1,1-tau_a] L_m(x)L_n(x+tau_a) dx
                 +integral[-1+tau_a,1] L_m(x)L_n(x-tau_a) dx].
(a,p) = (2,2),(3,3),(4,2),(5,5).
```

The six physical pairs are `(0,0),(1,1),(826,824),(827,825),(1650,824),(1651,825)` at unchanged N826,M1652,K86. Both signed windows are evaluated independently. In particular, the power4 coefficient is log2/2, not log4/2.

The producer uses the complete1239-node prescribed Gauss rule on every term/window, streamed ordinary-Legendre recurrence through all826 low positions and1652 output positions. Largest product degree2476 is below the rule's exact-degree limit2477. Source4608-bit coefficients/shifts are recomputed natively, not taken from the lower-precision scalar-premise intervals. A precision/thread/range-keyed cache holds one node batch;257-node blocks leave a genuine211-node final block.

The independent6144-bit consumer uses exact Rodrigues integer ratios, manual factorial-scaled binomial convolution, full826-position padded input domains and one power-moment vector through degree2476 per signed window. It imports no producer mathematical evaluator or cache. Native cancellation-sensitive evaluation precedes checkpoint rounding. The two methods share the documented Python/FLINT/Arb/Gauss and reviewed source-form premises, not a second proof of the numerical library.

Here P_H means the selected **arithmetic** head/low component, not the full F_H source assembled from other operators. Its ordinary bilinear entries require output-mass division, just as the later full F_H action does.

## Persistence, exact normalization and width

Separate producer/analytic collections bind the exact problem, code/input snapshots, native backend/threads/precision, contribution geometry, logical partition and codec/grid policy. Every selected physical entry has its own immutable quantity identity. Collection ownership is a real OS lock; each resumed runtime attempt has a new generation and fresh directory. Workers stage closed payloads; only the current owner publishes.

The producer contributes59472 complete checkpoint records: six entries times four powers times two windows times1239 nodes. Each complete producer entry covers9912 contributions; each analytic entry covers eight complete signed-window integrals. Prefixes reduce in fixed physical contribution order inside the owned worker. A compatible closed orphan is copied without a second grid rounding; conflicts reject. A completed-prefix resume revalidates the actual prior arithmetic rather than trusting an old success flag.

Both checkpoints use q512. Each staging endpoint pays at most2*2^-512, and each prefix contribution pays exactly2^-512 per endpoint. Final256-bit publication pays at most2*2^-256 per endpoint. Native input/roundoff uncertainty is already enclosed before those payments. The observed largest producer native interval width is bounded by2^-2531.

For D_m=2/(2m+1), the expansion coefficient is P_mn/D_m, **not** P_mn/D_n. Native exact construction and separate Rodrigues preparation agree on every coefficient, endpoint and exact squared-polynomial mass at degrees0,1,86,87,740,741,824,825,826,827,1650,1651. The selected physical publication radius is bounded rationally using max(D_m^-1,D_n^-1), which bounds1/sqrt(D_m D_n). It must satisfy the unchanged exact numerical goal. This is a per-entry payment, not a full-matrix row-radius or source-norm claim.

## Implemented interfaces

- [`producer.py`](../../scripts/whole_source/producer.py): on-demand exact basis, streamed full-domain Gauss arithmetic, bounded node reuse and owned staging.
- [`analytic.py`](../../scripts/whole_source/analytic.py): independent exact ratios, signed binomial/window integration and owned analytical staging.
- [`slice.py`](../../scripts/whole_source/slice.py): explicit input/resource binding, real persisted traversal/resume, separate-role evaluation and exact containment/payment.
- [`artifacts.py`](../../scripts/whole_source/artifacts.py): bounded exact snapshots/chunks, semantic coverage, single-owner publication, compatible orphan revalidation and prefix/quantity state.
- [`execution.py`](../../scripts/whole_source/execution.py): one contained stage root and bounded spawn descendants, role initialization, aggregate admission, owned reduction/revalidation, cleanup and input-only runtime inventories.
- [`scripts.weil_whole_source_split`](../../scripts/weil_whole_source_split.py): actual `inspect` and `slice` commands; no unimplemented full-source/proposal/exact commands.

The pinned supervisor's `kind=fixture` selects its generic owned-task entry. These particular tasks compute the actual arithmetic above; the neutral entry label does not make them synthetic polynomial fixtures.

## Executed checks and qualification scope

The affected suite passed189 cases before the final compressor-pause correction. Its mathematical checks include exact rational low-degree integration, complete highest-mode coefficients, genuine missing leading powers, unsymmetrized signed windows, wrong prime4 base, independent high-mode composition/antiderivatives, physical masses, endpoint containment and native runtime boundaries. A new released-pause compression regression fails before the correction and passes after it.

The first eight scientific interruption cuts resume to all six identical endpoints and scientific quantity seals on the recorded pre-correction implementation. Actual writer ownership, changed committed-byte rejection/restoration, bounded sharing/short-write/quota injections, six changed-context controls and input-only captured replay are implemented and executed. The ownership control exposed the compression-identity defect below; therefore the complete final gate is **not yet claimed** by this working record.

Additional executed checks:

- A real257-of9912 inner contribution prefix is committed, its actual writer interrupted, then the full six-entry CLI resumed with identical endpoints/seals.
- Seven correctly hashed wrong-content candidates reach exact mathematical/mass checking: missing prime, signed window, last node, wrong m4 coefficient, wrong sign, wrong output mass and wrong head/low expansion mass.
- Three actual owned native proposals evaluate complete eight-window quantities: missing highest low power, reversed shift and premature512-bit arithmetic. The first two fail containment; the last fails the physical numerical-width goal.
- A positive complete persisted-cache control passes first. Two complete false caches then pass structural storage/coverage/reduction but fail independent mathematics:14868 prime5 records zeroed, or one genuine final Gauss-node record zeroed. Every case retains all declared logical domains and correct consumed-byte hashes. A self-consistent cache is not mathematical truth.
- An actual previous native response is replayed under a new generation and refused. An identical byte retry adds no index/contribution; correctly hashed conflicting bytes reject.
- The frozen-code `replay-v1.py` reproduces all six mathematical results and quantity seals on its captured implementation. Expected outputs remain external to the native task trees.

Process interruption is not power-loss qualification. Native cancellation is observed at a deterministic boundary in a live native arithmetic task after certified node construction, not claimed as a debugger observation inside a particular C instruction. Replayed stale output is an actual old native response, not a claim that a live delayed worker survived containment. Captured-tree isolation is not a hostile-OS sandbox; installed system packages remain visible.

## Resource observations and measured correction

The normal-v4 path completes16 owned stages with one numerical worker and one native thread. Its observed owned peak is94101504 bytes; maximum sampled external-supervisor increment is2138112 bytes. The admitted account is792MiB owned commitment,1536MiB hard cap and256MiB supervisor-increment allowance. These are selected-entry observations on Windows/Python3.14, not full-target resource recommendations or larger-host scaling results.

A postmortem profile identified repeated scalar-profile normalization while recomputing immutable identities. On exactly the same146 committed nodes:

| Metadata replay | Profiled seconds |
| --- | ---: |
| Before validated immutable-identity caching |64.794|
| After caching |4.469|

This is a local metadata measurement, not a whole-source or T1 speedup. Replacement instances reset their non-init witnesses; mutable snapshot bytes reject. Gauss-batch reuse constructs1239 roots with35 task reuses. All59472 checkpoint records from the initial and reused-node producer versions match exactly, including every endpoint.

## Faithful development and correction record

No failed run is promoted or overwritten by its successor.

1. The first focused run had180 passes and three failing assertions. Direct exact-endpoint comparisons prove those computed rational enclosures sound: `arb.contains(fmpq)` was comparing a converted ball rather than the exact rational in those cases. Tests now compare exact endpoints; no mathematical enclosure was widened or clipped to make them pass.
2. The first native attempt computed all40 source tasks, but was deliberately cancelled during slow publication after146 chunks. Its code, inputs, completed task data, observations and cancellation state remain. Profiling found identity revalidation, and the one-batch node traversal was separately checked against every original checkpoint record.
3. Normal-v2 completed the mathematical paths but failed final report publication because operational timing floats entered an exact-only JSON codec. The existing finite hex-telemetry convention is reused; mathematical data still forbid floats.
4. Actual scientific recovery exposed a missing completed-seal endpoint parser. A permanent failing-before/passing-after test now reopens a sealed quantity. Prefixes and completed seals share the same exact domain/endpoint parser.
5. A275-character Windows script-path reproducer starts with an empty implicit script-directory path. The frozen worker then cannot locate an adjacent helper. The owned launcher now explicitly supplies only the verified helper directory; all five frozen helper programs remain byte-identical. An actual long-path native runtime regression passes.
6. Normal-v4 is mathematically accepted and its replay succeeds. K10-K13 pass, but K09 reveals that `gzip.flush()` in a released pause changes one compressed packet. That packet's complete decompressed contents are identical. The correction flushes/fsyncs existing file bytes without flushing the compressor. Its exact failing test, source version, different packets and diagnosis remain. Final qualification uses a new collection/code binding rather than rewriting v4 evidence.

A separate read-only code review found no important mathematical/recovery defects before the last encoding correction. It is static review, not another numerical proof.

## Reproduction and retained evidence

`data/inputs-v5/` binds the final corrected programs. `captured-code-v5/` retains their code, original scalar/input closure and origin receipts; no Git checkout or expected new mathematical outputs are required there. The final replay entry is [`replay-v2.py`](replay-v2.py). Explicit interruption, boundary, partial-prefix and persisted-cache qualifiers are retained alongside their versioned data. [`verify-retained-v1.py`](verify-retained-v1.py) is a read-only retained-byte/exact-reduction checker, not fresh native reconstruction.

Final authority is `data/normal-v5/`, `data/recovery-v3/`, `data/boundaries-v3/`, `data/persisted-cache-v2/`, `data/partial-inner-prefix-v2/` and `data/frozen-replay-v2/`. All six normal entries pass, all eight interruption cuts and five boundary controls pass, both false persisted-cache cases reject at independent mathematics after the positive case, and the257-of9912 partial-prefix continuation reproduces all endpoints and seals. The fresh frozen-code replay reproduces the same complete selection.

The final affected suite passes **190/190** in155.24 seconds (`development/final-suite-v6.xml`). An earlier run exposed a test observation race: both worker-ready files existed, but live status still held the preceding two-process sample. The retained pool observation independently verified both concurrent workers and cleanup. The corrected test waits for the required three-process sample before releasing workers; its count/resource assertions are unchanged. The failing test version is preserved under `development/before-sampling-wait-correction/`.

The final normal CLI run took316.36 seconds under its declared single-worker/single-native-thread policy. All16 owned stages clean up; observed owned peak94167040 bytes, largest sampled external increment2699264 bytes. These are current-host selected-entry observations, not matched whole-pipeline speedup or target resource estimates.

Executed final commands from the repository root (paths below are relative to this bundle unless prefixed):

```text
uv run --locked --python 3.14 python -B -m scripts.weil_whole_source_split slice --problem <bundle>/data/inputs-v5/problem.json --cases <bundle>/data/inputs-v5/cases.json --execution <bundle>/data/inputs-v5/execution.json --output-dir <bundle>/data/normal-v5
uv run --locked --python 3.14 python -B <bundle>/qualify-recovery-v1.py --inputs <bundle>/data/inputs-v5 --baseline <bundle>/data/normal-v5 --output-dir <bundle>/data/recovery-v3
uv run --locked --python 3.14 python -B <bundle>/qualify-boundaries-v1.py --inputs <bundle>/data/inputs-v5 --baseline <bundle>/data/normal-v5 --output-dir <bundle>/data/boundaries-v3
uv run --locked --python 3.14 python -B <bundle>/qualify-persisted-cache-v1.py --inputs <bundle>/data/inputs-v5 --baseline <bundle>/data/normal-v5 --output-dir <bundle>/data/persisted-cache-v2
uv run --locked --python 3.14 python -B <bundle>/qualify-partial-prefix-v1.py --inputs <bundle>/data/inputs-v5 --baseline <bundle>/data/normal-v5 --output-dir <bundle>/data/partial-inner-prefix-v2
uv run --locked --python 3.14 python -B <bundle>/replay-v2.py --output-dir <bundle>/data/frozen-replay-v2
uv run --locked --python 3.14 --extra test python -B -m pytest -n 0 -q tests/test_whole_source_contract.py tests/test_whole_source_arithmetic.py tests/test_whole_source_analytic.py tests/test_whole_source_artifacts.py tests/test_whole_source_execution.py --junitxml=<bundle>/development/final-suite-v6.xml
```

Use fresh output directories for reproduction; retained outputs must not be overwritten. The same-context `--resume` path is reserved for actual compatible interrupted collections. The manifest binds retained raw files, including preserved unsuccessful development evidence. The read-only verifier checks those bindings, recomputes exact persisted sums and validates final selected containment; it does not repeat native reconstruction.

## Preserved research and limits

All earlier95/53/2332 sealed members and50/123/123 dependency bindings match, covering155 distinct original dependency files. All five frozen neutral helpers are unchanged. Earlier programs, inputs, results, tests, schemas, records and production admission lists remain intact. No Rust/Lean trust layer changed or was rerun.

This computes six complete selected arithmetic entries, not a complete P matrix, the full V/P/R source, weighted Gram, congruence witness, all-entry audit, smooth-test consequence or T1 result. It does not establish full-target practicality, production admission, literature priority, a new positivity support or RH. C-0124's retained source-conditional .81 result, scalar-only C-0126 and production8v1/0v2/1v3 remain unchanged.
