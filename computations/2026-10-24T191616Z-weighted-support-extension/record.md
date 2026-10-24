# Weighted continuation selected by prime3 overlap and error controls

- **Computation ID:** `X-20261024-004`
- **Created:** `2026-10-24T19:16:16Z`
- **Last updated:** `2026-10-24T20:37:47Z`
- **Status:** `COMPLETE`, all-fresh analytical acceptance, exact positive parity witnesses and preserved-version replay passed; source-conditional research, not production admission

## Objective

Explain the successful weighted refinement at T=3/5, derive a controlled support extension from source geometry and error bounds, and evaluate that selected experiment without changing prior research or production theorem admission.

The reference is S0=A-B*C0^-1B, with C0 e_k=(mu+H_k-H_N)e_k. The complete signed source is V+P+RK, including all cross terms. Ordinary Legendre masses are d_j=2/(2j+1). The full residual and infinite omitted tail must be paid.

## Selection and inputs fixed before new signs

Baseline is C-0084, T=3/5,N=192,K=32,m=626. Its accepted packet and witnesses are retained in [X-20261024-003](../2026-10-24T153012Z-weighted-reference-continuation/record.md). The old316 comparison uses the separately retained [X-20261024-002](../2026-10-24T124142Z-weighted-low-space/record.md). Original exact mu is preserved as the positive reference reserve, not inferred to remain valid at another support.

The executed scalar rule nearly doubles ell3(T)=2-log3/T, then chooses certified error controls before inspecting any new matrix sign:

| Parameter or control | Selected value or display |
| --- | ---: |
| Exact support |1353/2048|
| Support display |0.66064453125|
| Prime3 overlap ratio |1.9946789612820353|
| Dimension N |312|
| Residual order K |38|
| Evaluation boundary m |1018|
| Original exact mu, display |0.18491998558724346|
| Fresh source complement, display |0.18652798913378738|
| Uniform residual allowance upper, display |1.9466091170109155e-13|
| Old accepted residual budget, display |6.8816432788767504e-13|
| Low/head construction precisions |1792/4608 bits|
| Independent low/head precisions |3584/9216 bits|
| Publication/reference receipt widths |352/512 bits|
| Congruence proposal grid |48 bits|

Selection JSON raw SHA256 is `e120acab4919b9ab28e6fd6c7044053bb14514f300d810952a2d52e5dae6d7a3`. Its actual selector source SHA256 is `31de5cad9e3bfaf3f23e09cf145949d12df94c1d512fdac1d1f73966ccff6489`, preserved in `source-v1/scripts/weil_weighted_extension_diagnostics.py`. Mathematical rules and scope are in [F-20261024-004](../../findings/2026-10-24T193421Z-cross-cut-norm-controlled-continuation.md), C-0085. The first certified choices under a fixed512-bit scalar procedure are not claims of mathematically minimal dimensions.

Strict active set[2,3], translation-chain topology, signed-cell order and2T<pi are required. Equal inverse-weight caps do not imply equal omitted mass, matrix error, margins or computation cost.

## Completed diagnosis and theoretical consequences

`data/baseline-losses-v2.json` compares the same exact retained directions at316/626. The formerly failing odd direction's omitted weighted allowance falls from0.6073756850 to0.2140254027; its lower changes from-0.1574622208 to+0.1100679647. The interval losses are below1e-89. This is a new decomposition of old accepted evidence, not a new baseline theorem or a fresh old analytical audit.

C-0085 proves ||Q_N V P_N||<=pi/2 with a self-contained Hilbert-kernel argument and derives the full residual charge delta(1+2b/mu)+delta^2/mu. This charge is not universally smaller than the old trace charge. K was increased so its new charge fits within the old accepted budget.

[F-20261024-005](../../findings/2026-10-24T194945Z-conditional-schur-completeness-cost.md), C-0086, proves conditional eventual success of the exact scalar-complement and grouped factor3 criteria when a full fixed-support coercive gap is already known. The exact baseline consequence gives a conservative closed scaled-form gap9.5530133375e-13 and sufficient norm-only log(N+1) thresholds of order3e13. No such huge dimension is executed. These are not necessary dimension lower bounds and cannot supply positivity at an unproved support.

## Implementation and checks completed at this timestamp

New additive research scripts preserve the fixed historical consumers:

- `scripts.weil_weighted_extension_diagnostics`, exact retained-direction decomposition and pre-sign structural selection;
- `scripts.weil_weighted_dimension_cost`, exact conditional gap/threshold calculation;
- `scripts.weil_weighted_support_extension`, fresh complete low/head generation and finite weighted consequences;
- `scripts.verify_weighted_support_extension_inputs`, separate global-moment/Taylor reconstruction, without accepted-low reuse.

The internal reuse of `verify_weighted_low_space.weighted_matrices` maps the new packet's canonical RK array into the unchanged kernel's three-component slot named R32. The kernel itself is parameter-independent finite arithmetic; this mapping does not set K=32. Native residual generation, degree checks and heads all use the selected K=38.

The three initial permanent source/residual controls passed, including both support/order cases, per-column residual degree zeros and the signed full residual cross term. This was a focused run, not the full Python/Rust/Lean suite.

The fresh producer completed with exit0 in795.2479035999859 seconds. Source packet SHA256 is `c9790a7b129aae0d410670830e8a472d639105d01884a041165fc119e627671e`,16183360 bytes. All low matrices and heads were rebuilt; there is no cached-low route in this new experiment. The complete all-entry native audit is running. Construction success does not establish analytical acceptance or matrix positivity.

## Preserved failures, review and binding qualification

1. Initial baseline diagnostics requested the nonexistent626 audit-v2 filename and exited1 before numerical assessment. The actual retained file is audit-m626-v1.json.gz. Its source version, failure output and run receipt are preserved. The corrected baseline operation completed with exit0 in4.693936499999836 seconds.
2. Separate read-only mathematical review accepted the cross-cut constant, complete residual inequality, geometric rule and conditional completeness argument. It performed no numerical generation or tests.
3. Static implementation review identified a partial-selection guard: only parameter headers were compared, while the embedded residual budget was later used. A real validation probe changing only that budget reproduces acceptance, exit1 for the desired rejection regression. No analytical reconstruction or matrix sign was evaluated by that probe.
4. The actual original selection and packet are separately checked against the COMPLETE deterministic contract, including every budget and baseline identity. `check-selection-v1.py` returns FULL_FROZEN_CONTRACT_PASS, and raw packet/selection byte identities are pinned. The prospective guard defect does not alter the correctly generated actual parameters or analytical arrays.
5. Executed version2 sources are preserved in `source-v2/`, with runtime and imported dependency closure in `environment-v2.json`. Historical versions are not silently changed. Any later guard correction and its regression evidence will be dated separately and must not be relabeled as the source of an earlier numerical execution.

## Reproduction and source identity

Use the locked environment and exact sources for the stage being replayed. `environment-v2.json` records actual Python3.14, packages and lock identity. `source-v1/` preserves the first selector/failed-diagnostic version. `source-v2/` preserves the executed numerical implementation and required imported research modules. Restore a chosen captured source version into an isolated copy of this repository containing the retained computation data before replay; do not retarget historical hashes to current files after upgrades.

Commands actually executed include:

```text
python -m scripts.weil_weighted_extension_diagnostics select --output computations/2026-10-24T191616Z-weighted-support-extension/data/selection-v1.json
python computations/2026-10-24T191616Z-weighted-support-extension/run-stage-v1.py baseline-v2
python computations/2026-10-24T191616Z-weighted-support-extension/run-stage-v1.py source
python computations/2026-10-24T191616Z-weighted-support-extension/check-selection-v1.py
python computations/2026-10-24T191616Z-weighted-support-extension/run-stage-v1.py audit
python -m scripts.weil_weighted_dimension_cost --output computations/2026-10-24T191616Z-weighted-support-extension/data/conditional-dimension-cost-v1.json
```

The actual argv and executable paths, stdout/stderr, elapsed wall time and confirmed direct-child exit are retained in data run receipts. Only one owned heavy mathematical process runs at a time. The supervisor's direct-child lifecycle is not an OS-wide descendant-containment or descendant-inclusive memory claim. Elapsed-time estimates are not mathematical validity criteria.

## Interpretation and limits at 2026-10-24T19:49:45Z

The controlled extension has been selected and generated, but its new analytical acceptance and matrix signs remain unestablished here. Final results require separately dated evidence. No precision/scope failure is mathematical negativity; a negative conservative lower is not a negative actual reference; a negative reference does not imply a negative Weil form.

No current research result is clean-source production admission, independent Rust acceptance, a full-source Lean proof, an optimality or literature-priority claim, an unbounded support-covering family or RH. The frozen8v1/0v2/1v3 theorem inventory and all prior mathematical sources, tests and proof artifacts remain unchanged.

## 2026-10-24T20:37:47Z: completion

The earlier RUNNING interpretation above is retained as the state at its stated timestamp. This dated completion supersedes that state, not its earlier reasoning or failure records.

### Actual result and execution

The independent audit reports ALL_FRESH_SOURCE_INPUTS_ACCEPTED for758475 inputs:97656 triangular A_K/G_K slots,660816 V/P/RK head slots and3 scalar bounds. All312 exact residual images/signatures are fresh; no analytical arrays or saved PASS receipts are inherited.

Assessment reports POSITIVE_REFERENCE_LOWER on both156-dimensional parity blocks. Exact mass-normalized lower displays are1.4153700144298843e-11 even and8.376781192230801e-9 odd. The separate CLI replay reports EXACT_REPLAY_PASS on the same bytes.

| Core execution | Exit | Wall seconds | Owned direct-child exit confirmed |
| --- | ---: | ---: | --- |
| Fresh source |0|795.2479035999859|true|
| Independent all-entry audit |0|1903.3478026000084|true|
| Exact assessment |0|14.974558799993247|true|
| Separate exact replay |0|13.707486999919638|true|

Core total is2727.277751999907 seconds, about45.5 minutes. Auxiliary controls, attacks, scalar analyses and historical replay have separate receipts; they are not silently included in that core total. No fixed work allowance terminated the computation.

Packet SHA256: `c9790a7b129aae0d410670830e8a472d639105d01884a041165fc119e627671e`.

Audit SHA256: `e23fa00b66d5ebe5ccc261e23b886c10e2e4fdd3f816d9a8a3dcbca38282408e`.

Assessment SHA256: `d7569a7037021fc729987b27851e64648f8f8f1eead8123dbd3391c4ce27cb8d`.

[F-20261024-006](../../findings/2026-10-24T202855Z-controlled-weighted-support-positivity.md), C-0087, states the complete source-conditional closed-form/complex smooth-test implication and physical-mass proof. No Rust/Lean/clean-source admission or RH result follows.

### Interpretation

The scalar scout's conservative cost increases from5.6523929575 to6.1352925716. The c_T increase is about0.0962863, full residual norm-majorant increase about0.3866133, and arithmetic norm charge remains unchanged. The minimum scalar-positive cutoffs are160 and259, not minimum Weil/Schur dimensions. Holding the original positive reserve selects even N=312.

Certified reference bounds are smaller by about112 times even and68 times odd, not measured ratios of full spectral minima. The global tail diagnostic grows to about12.04964 while the correlated matrix stays positive. In the retained weak even proposal, the omitted weighted allowance is about2.17080e-14, full residual charge1.94661e-13 and directional matrix lower1.41538e-11. Interval losses are about5.30e-102 and2.45e-100. More precision is not the observed limiting refinement.

This supports a controlled within-window extension mechanism, not equal omitted mass from matched weights, future positive margins, globally required common mu, comparative superiority, or convergence of isolated windows to RH.

### Rejections and prospective guard correction

Actual version2 replay rejected an altered odd exact margin and reencoded source with a stale audit, without success output. Their exit1 tracebacks are historical validation failures in that version, not negative-reference/theorem-failure evidence.

After all version2 numerical executions and attacks, live version3 replaces the partial selection comparison with complete typed JSON equality against the current deterministic selection, including every budget/provenance field. Generation and acceptance bind the input serialization digest to the embedded contract. ValueError validation failures now return exit2. No mathematical formula changed.

The original metadata regression goes from REGRESSION_FAIL to REGRESSION_PASS. An actual live generate CLI using a CURRENT-source selection with only its budget doubled rejects before numerical work, exit2 and no output. The correct current full contract/byte digest passes;4 focused controls pass. The earlier passing3-test version remains in source-v2, not relabeled as four.

Source-v3 snapshots and selection-v3.json are separate prospective guard evidence, not replacements for the original pre-sign selection or numerical producer identity.

### Historical reproduction after cutover

`replay-archived-v2.py` restored source-v2 in an isolated temporary repository tree and ran the actual mathematical replay on unchanged source/audit/result bytes. It returned ARCHIVED_SOURCE_REPLAY_PASS, exit0, in14.236604399979115 seconds.

Restored generator SHA is `621feca54d90578c61e31078114662acbe706faa2a11f1fdf482bf1a8cb7fd7a`; live corrected SHA is `94d6360ca93b6125e8fd3c7675b340236960d593b40df433528a9f313da91bea`. The temporary restore was removed after its output/receipt were retained. This checks historical replay across a live-source upgrade; it does not regenerate the full analytical audit or claim old guards were generally safe for altered metadata.

Separate read-only mathematical/implementation review accepted the norm, residual, conditional-completeness and final form/test implications and confirmed the guard correction. It performed no numerical execution or independent artifact inspection. Machine evidence consists of the retained actual commands, fresh reconstruction, exact witnesses, replays and attacks. No broad Python/Rust/Lean suite was run or claimed.

All old research, mathematical sources, original tests and proof artifacts remain unchanged. Final source/manifest and documentation/privacy checks are retained separately. No automatic stage, commit, push, format admission or clean-source relabeling occurred.
