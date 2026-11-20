# Blocked fresh nonproof congruence proposal

- **Computation ID:** `X-20261031-001`
- **Created:** `2026-10-31T02:54:01Z`
- **Last updated:** `2026-10-31T03:13:03Z`
- **Status:** `VERIFIED_NONPROOF_PROPOSAL_FUNCTIONS_AND_FINITE_CONTROLS`

## Objective and mathematical quantity

Implement actual paid-A panel Cholesky, complete forward/backward solves, two-sided A/H/E whitening, bounded log-Young optimization and full rational congruence coordinates without a native dense inverse. Every output is NONPROOF_ONLY.

The proposer conditions `A=A_model-Lambda D`, with ordinary physical masses `D_nn=2/(2n+1)`, and divides the already weighted head/exterior matrices by exact eta. With `A=L L^T`, it constructs `Aw=L^-1 A L^-T`, `Hw=L^-1 H L^-T` and `Ew=L^-1 E L^-T` using full panel solves. All previous cross panels and both solve orientations are included. This conditioning subtraction does not discharge the separate exact proof's once-only Lambda D obligation.

The floating objective is the maximum eigenvalue of `(1+theta)Hw+(1+1/theta)Ew`, optimized over logtheta in[-20,20]. Positive theta is rounded onto a40-bit dyadic grid and the rounded value is re-evaluated. The complete symmetric residual eigensystem uses conditional inverse-square-root column scaling only when its minimum floating eigenvalue is positive; otherwise the complete signed eigenbasis is retained. A fresh native phase solves `L^T W=V` and rounds every entry onto the common80-bit dyadic grid, giving complete integer Z and `U=Z/2^80`. No identity/retained-coordinate fallback is present.

Native precision and persisted interval grid are1024 bits. Native factor/left-solve/whitened/backsolve data are bounded disk panels; no full native inverse or simultaneously resident A/H/E/Linv/W family is used. The worker and parent use the paid persisted panels, not hidden more accurate factors available only in one process.

## Implemented interfaces and ownership

- `scripts/whole_source/proposal.py`: `blocked_cholesky`, `triangular_solve`, `whiten_tiles`, bounded panel storage, exact source conversion, native/float/native owned callbacks, input binding, `run_proposal` and complete exact-coordinate `read_proposal`.
- `scripts/whole_source/proposal_float.py`: lazy NumPy/SciPy optimizer/full eigensystem. Floating values in diagnostics are exact binary64 hexadecimal strings, not mathematical JSON floats or pickle payloads.
- `scripts.whole_source.execution`: explicit proposal role, NONPROOF_PROPOSAL_ONLY scope and NumPy/SciPy backend/version validation. Floating backends cannot enter producer/analytical/exact proof roles. BLAS settings and actual owned-job attachment precede numerical imports.
- `scripts.weil_whole_source_split propose`: actual CLI, fresh output only, explicit problem/source/execution bindings. An operation-wide OS lock covers all phases and final publication.

`prepare_proposal_inputs()` rebinds old source code from immutable content-addressed collection snapshots in a separate data namespace. Historical source code need not be overwritten or imported as proposal mathematics. Source byte hashes, exact physical coverage and original scalar identity remain bound. The new source/proposal formats do not alter the old32MiB parser or historical certificate semantics.

Workers stage closed panels. Only the collection owner publishes immutable panel blobs and their inventory, then removes committed staging. Each owned numerical pool is released before the next phase. The final proposal core is published only after complete integer-coordinate structural read-through; diagnostics and full floating vector panels are separately bound non-pickle members. Both parity dimensions, u80, positive exact theta, source/problem/code/backend identity and complete n*n integer coordinates are checked. Analytical acceptance, matrix positivity and production admission stay false.

Persisted phase/panel data are completed-stage evidence and input to the next phase. This work does not claim interrupted-stage or power-loss recovery, or a `propose --resume` contract.

## Actual inputs and refusal diagnosis

The initial real CLI run `data/run-v1` consumes the evaluated N6/M12/K2 reduced source from [X-20261030-003](../2026-10-30T181819Z-bounded-frequency-head-source/record.md), `data/control-v6`. It correctly stops at a nonpositive/uncertain Cholesky pivot. No floating phase or closed proposal is published; the owned stage exits1 with cleanup verified. The outer CLI exits2 and retains NONPROOF_PROPOSAL_UNRESOLVED. This reduced source was never certified positive.

The first exact diagnostic considered only diagonals and was inconclusive. `prepare-controls-v2.py --diagnose-source` instead evaluates every leading determinant with exact rational interval arithmetic. `data/reduced-source-diagnosis-v2.json` confirms a strictly negative even third leading minor on the same source SHA. This is a finite reduced-control fact, not negativity of the Weil form, failure of the original .81 result, or a target hardware finding. The refused source is preserved and is not replaced/relabelled as successful.

Successful-path exercises use two separately declared **manufactured finite matrix controls**, not evaluated supported Weil matrices. Their source transport is explicitly control-only and their definition files identify that distinction. Both have known row-scaled rational3x3 L, exact physical Lambda D added to A_model, a rational rotated diagonal whitened H, and E=4H. The positive case has a strictly positive residual spectrum; the signed case requires the full unscaled eigenbasis. Their exact Young optimum is2. Known expected factors/definition files are kept outside numerical runtime inputs; the source-preparation program is captured as source provenance, not imported by proposal mathematics.

## Executed verification

The final authorities are `data/positive-input-v2`, `data/signed-input-v2`, `data/positive-run-v3`, `data/signed-run-v3`, the original refused `data/run-v1`, and `data/exact-control-verification-v3.json`.

Both successful actual CLI runs compute all18 rational coordinates across both parity blocks. `verify-controls-v2.py` independently checks72 source enclosures against their exact defining matrices, all36 final transform coordinates, every exact forward residual `L^T Z/2^80-V`, the complete exact manufactured congruence, known theta optimum and both eigenvector branches. Backsolve residuals must be below2^-70; full congruence errors below2^-35. These are finite-control checks, not target proof acceptance. Its actual status is PASS_EXACT_RETAINED_NONPROOF_PROPOSAL_CONTROLS.

All12 successful owned stages have exit0, bound task/program/plan/raw streams and verified cleanup. The original refused owned stage also has verified cleanup, genuine reduced-source diagnosis and no fallback/dependent float execution. The qualified closure therefore binds13 owned cleanups. Earlier positive/signed v2 profile runs are separately preserved successful development evidence, not substituted for final v3 profiles.

The final `data/affected-tests-v3.xml` reports149 passes, zero failures/errors/skips,26.66 seconds:13 native proposal,43 floating proposal,13 frequency/head,21 pipeline/publication,48 low/exterior and11 affected ordinary cases. Tests cover row-scaled rational factors, ragged panels, every cross-update, full forward/back solve residuals, two-sided normalization, nonpositive pivots, full coordinate/dimension boundaries, known theta/eigenvector behavior and ordinary numeric failures. A separate read-only implementation review found no confirmed mathematical/ownership defect at its inspected revision. The subsequent telemetry and staged-disk corrections were independently exercised by the parent; that review is not described as certification of later changes.

No old adversarial, corruption or process-interruption programs were run. No full suite, Rust or Lean run is claimed.

## Measured resources and declared full layout

Environment: Python3.14.0, python-flint0.9.0, NumPy2.5.2, SciPy1.18.0, Windows10.0.26300 x64, locked project environment. Code origin is b19905565ace1f4a1b9ea1387ce123377c65a0e0 with dirty work recorded, not a claim that uncommitted code equals that commit. One numerical worker/thread,1536MiB hard cap,792MiB owned account,256MiB external increment allowance and128MiB reserve.

| Final finite control | Inclusive proposal CLI seconds | Maximum observed owned bytes |
| --- | ---: | ---: |
| Positive whitening | 48.794557 | 132354048 |
| Signed eigenbasis | 49.061578 | 131088384 |

The largest sampled external increment is1802240 bytes. `data/resource-observations-v1.json` retains exact hexadecimal timings and all12 final stage measurements. These tiny finite matrices exercise real process/library/storage handoffs, not full supported-source speed, memory or conditioning. No matched original-proposer or whole-pipeline speedup is claimed.

`data/full-layout-v1.json` inspects the complete declared .81 dimension413 without importing FLINT/NumPy/SciPy. The standard32-mode layout accounts for341138 final rational coordinates across both parities. Its conservative component figures are:

| Derived account, not measured peak | Bytes |
| --- | ---: |
| Current native panel/buffer slots | 14680064 |
| Dense float arrays/workspace exception | 30327168 |
| Complete native staged-data overlap | 681545168 |
| Complete floating staged-data overlap | 17268144 |
| Native result inventory bound | 631296 |
| Persisted panel stores per parity | 789855600 |

Native/float scratch disk declarations derive from complete stage geometry,666/33MiB at full dimension, rather than a fixed128MiB that would reject the staged factor/left/whitened collection. This is a disk-lifetime correction, not an increased native RAM cap or an allocation-cap ladder. Control runs derive25/25MiB. Preflight checks complete staged storage, repository allowance, inventories and component working accounts before native imports. The16-mode full layout exceeds the fixed1MiB result inventory; it rejects before arithmetic. None of this is an executed full-stage admission or full-target resource guarantee.

## Preserved development corrections

- Initial syntax/decoder authoring errors were corrected before the first native invocation; no result is attributed to those drafts.
- The initial evaluated reduced source refusal is preserved as a genuine mathematical-control refusal, not a code fix or target failure.
- A static serialization exercise caught raw operational receipt floats being rejected by canonical exact JSON. The existing `exact_telemetry` codec is used before storing receipts; successful actual stages exercise that path.
- `prepare-controls-v1.py` and both incomplete v1 input directories are preserved. Its call to the existing dyadic-only rounding primitive correctly rejected general rational fixture endpoints. V2 computes exact outward rational floor/ceil onto the publication grid; the old codec is not weakened. The first diagonal-only diagnostic is also preserved as inconclusive, not advertised as proof.
- Successful initial positive/signed v2 executions are preserved. Full-shape storage analysis then catches the insufficient fixed128MiB temporary allowance; final v3 executions bind the dimension-priced resource revision.
- `verify-controls-v1.py` is preserved with its observed missing flat stdout_sha256 lookup. V2 uses the actual nested raw receipt log schema and passes. This was a retained-checker failure, not failed proposal mathematics.

## Executed reproduction

Use fresh destinations; preserve the authorities above. The preparation commands create explicit manufactured source controls:

```text
uv run --locked --python 3.14 python -B computations/2026-10-31T025401Z-blocked-nonproof-proposal/prepare-controls-v2.py --case positive --output-dir <fresh-positive-input>
uv run --locked --python 3.14 python -B computations/2026-10-31T025401Z-blocked-nonproof-proposal/prepare-controls-v2.py --case signed --output-dir <fresh-signed-input>
uv run --locked --python 3.14 python -B computations/2026-10-31T025401Z-blocked-nonproof-proposal/run-proposal-v1.py --source <positive-input>/source/source-manifest.json --output-dir <fresh-positive-run> --panel-size 2
uv run --locked --python 3.14 python -B computations/2026-10-31T025401Z-blocked-nonproof-proposal/run-proposal-v1.py --source <signed-input>/source/source-manifest.json --output-dir <fresh-signed-run> --panel-size 2
uv run --locked --python 3.14 python -B computations/2026-10-31T025401Z-blocked-nonproof-proposal/inspect-layout-v1.py --output <fresh-layout.json>
uv run --locked --python 3.14 python -B computations/2026-10-31T025401Z-blocked-nonproof-proposal/verify-controls-v2.py --positive-input <positive-input> --positive-run <positive-run> --signed-input <signed-input> --signed-run <signed-run> --refused-run computations/2026-10-31T025401Z-blocked-nonproof-proposal/data/run-v1 --refusal-diagnosis computations/2026-10-31T025401Z-blocked-nonproof-proposal/data/reduced-source-diagnosis-v2.json --output <fresh-retained-control-check.json>
```

For a newly produced real source, use `prepare_proposal_inputs()` and the actual `propose --problem ... --source ... --execution ... --output-dir ...` command. The supported full-reference default panel width is32. Do not treat the manufactured controls as such a source or install old .81 coordinates as fresh output.

## Retention and limits

Final test source, consumed code/input captures, streams, profiles, panels, refusals and failed versions are retained separately. `manifest-v1.json` binds raw members plus declared external code/input/environment/test dependencies. `verify-raw-v1.py` checks that inventory without repeating mathematical acceptance. The manifest and its excluded `raw-verification-v1.json` verdict are not included in their own member list, avoiding a hash cycle.

This delivers complete proposal functions and real finite-control CLI qualification. It is not fresh full supported .81 source/proposal qualification, analytical source acceptance, exact global nonsingularity/row-width/sign or positivity. Those full coupled gates remain unexecuted here. Full T1 remains NOT_ADMITTED; C-0124 and scalar-only C-0126, production8v1/0v2/1v3 and RH unresolved are unchanged. No GPU/dependency/OS-provisioning change, historical artifact rewrite, Rust/Lean admission, commit or push.
