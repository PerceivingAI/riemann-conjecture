# Weighted whole-low-space implementation and bounded parity assessment

- **Computation ID:** `X-20261024-002`
- **Created:** `2026-10-24T12:41:42Z`
- **Last updated:** `2026-10-24T15:02:23Z`
- **Status:** `COMPLETE` for implementation, controls and the bounded assessment; **odd reference unresolved / resource-limited**, not whole-space positivity
- **Finding:** [F-20261024-002](../../findings/2026-10-24T140543Z-weighted-even-reference-block.md), C-0083
- **Recorded published baseline:** `acc63ac6d41138280236850c3fbc586e20998cc4`, with pre-existing uncommitted research preserved. This is a dirty research run, not a clean production proof-bearing artifact or theorem admission.

## Objective and fixed mathematical inputs

Implement and exercise the C-0082 uniform weighted low-space construction at T=3/5,N=192,K=32, active [2,3], original exact mu and ordinary Legendre coordinates. Assess both 96-dimensional parity blocks, retain every signed cross-direction term and pay the complete omitted tail and full residual. A negative conservative lower is not a negative reference direction.

Original immutable input: `computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json`, SHA-256 `44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b`. Original trial, exact `mu_lower_exact`, support, dimension and residual order are unchanged. Frozen admissions remain v1=8,v2=0,v3=1.

Environment: Windows11 build26300, Python3.14.0, python-flint0.9.0, existing locked environment. One owned numerical child at a time, numerical-library threads one. No install, WSL/cloud/GPU execution, Rust/Lean change or theorem replay.

## Implemented procedures

1. `scripts.weil_weighted_low_space`: freshly constructs raw A_K and full Q192 mixed G_K, then rectangular unnormalized V/P/R32 pairings. Low source precision1024; head precision1536 at224 and1792 at316. `--base` reuses byte-identical low/source arrays when generating a new head. It does not admit or assert a matrix sign.
2. `scripts.verify_weighted_low_space_inputs`: separate exact polynomial, monomial, Taylor and signed-cell reconstruction. Low/Gram precision2048; head reference3072/3584. Every source interval must contain the independent exact endpoints and their outward512-bit receipt, against source352-bit publication. Exact residual signatures, source fingerprints, strict geometry and the original mu/complement relation are checked.
3. `scripts.verify_weighted_low_space`: independently rechecks all serialized containments and derives U_m, the complete tail trace, row-radius Loewner bounds and full residual allowance using exact integer/dyadic arithmetic. Float eig/Cholesky only proposes directions/witnesses. Positive lower proof needs both blocks; negative reference proof needs an actual directional upper below zero. Separate replay reconstructs errors, exact witnesses and trial consequences on captured source/audit bytes.

A_K is raw, without a pre-subtracted delta. The complete signed G_K contains all ordered mixed terms and the full low projection. Tail rows use r_k* r_k/d_k, not unweighted ordinary coefficients or a sparse low-space projection. Publication and comparison distinguish scalar endpoints from matrix order.

## Reproduction

Run from repository root into new output paths. Existing outputs refuse overwrite.

```text
uv run --locked python -m scripts.weil_weighted_low_space --boundary 224 --output <new-source224.json.gz>
uv run --locked python -m scripts.verify_weighted_low_space_inputs --packet <new-source224.json.gz> --output <new-audit224.json.gz>
uv run --locked python -m scripts.verify_weighted_low_space --packet <new-source224.json.gz> --audit <new-audit224.json.gz> --output <new-assessment224.json>
uv run --locked python -m scripts.weil_weighted_low_space --boundary 316 --base <new-source224.json.gz> --output <new-source316.json.gz>
uv run --locked python -m scripts.verify_weighted_low_space_inputs --packet <new-source316.json.gz> --output <new-audit316.json.gz>
uv run --locked --extra test python -m pytest -n 0 -q tests/test_weighted_low_space.py
```

Direct replay of the final retained exact proof and inconclusive odd test:

```text
uv run --locked python -m scripts.verify_weighted_low_space --packet computations/2026-10-24T124142Z-weighted-low-space/data/source-m316-v1.json.gz --audit computations/2026-10-24T124142Z-weighted-low-space/data/audit-m316-v2.json.gz --result computations/2026-10-24T124142Z-weighted-low-space/data/assessment-m316-native.json --output <new-exact-replay.json>
```

The retained comparison/gap helper scripts require repository-root `PYTHONPATH` when invoked by file path. In PowerShell:

```powershell
$env:PYTHONPATH = (Get-Location).Path
uv run --locked python computations/2026-10-24T124142Z-weighted-low-space/compare-fixed-v1.py
uv run --locked python computations/2026-10-24T124142Z-weighted-low-space/even-gap-v1.py
```

Actual absolute commands, source-stage contracts, stdout/stderr and termination receipts are retained. [Executed versions](data/executed-versions.json) bind each execution to preserved procedure snapshots. For an older implementation, restore its snapshot at its original relative module path in an isolated checkout with the recorded dependencies; do not overwrite the working procedure or rewrite earlier results. New generator elapsed metadata changes packet hashes, so fresh inputs require matching fresh audits. Proof replay above consumes the exact retained bytes instead of regenerating them.

## Analytical acceptance and mathematical outcome

| Boundary | Complete accepted interval slots | Even low block | Odd low block |
| --- | ---: | --- | --- |
| 224 | 55,490 | No positive lower witness | No positive lower witness; actual negative direction not certified |
| 316 | 108,482 | Exact positive lower and separate replay | Conservative lower has exact negative direction; actual reference sign unresolved |
| 626 | Not produced | Not evaluated | Source timeout before packet publication |

At316, low/Gram upper triangles each contribute18,528 slots, head V/P/R32 each23,808, plus2 scalars. Symmetry and reflection justify other slots, with numerical consistency checked. The independently reconstructed set of192 exact residual images matches the generator's aggregate signature. The original chosen mu is below the independent exact complement lower, not substituted by a new complement.

The even witness is lower-triangular dyadic with nonzero diagonal; exact native rational congruence verifies every Gershgorin row. Minimum exact margin has display0.999999985300644. [Even gap receipt](data/even-gap.stdout.txt) then derives g=eta/trace(W D_even Wtranspose)>0 with display1.577381523629527e-9. D_even uses physical degrees0,2,...190. This proves a uniform even reference lower under C-0082 and transfers to the true-Schur even block by C-0072, without evaluating that inverse.

[Fixed comparison](data/fixed-comparison-v2.stdout.txt) proves the odd conservative lower quadratic is negative, display-0.1574622207633184. Its full-error upper for the actual S0 value is positive, display0.44991346418918476. These facts do not decide the actual odd sign. The preserved original odd trial's new uniform interval, display[0.2031276216162931,1.0077559508789693], contains its prior accepted bracket[0.6257295744306691,0.8504608367268481]. The lower margin is about0.4226019528 weaker, primarily the conservative finite matrix-tail allowance, not contradictory source values.

## Cause-based corrections and arithmetic implementation

**Independent-audit v1 failed.** R32[192,0] is exactly zero by the individual residual image degree, but the independent monomial contraction returned a nonzero-radius ball. A global maximum-degree cutoff and parity did not cover that same-parity zero. The failed run used66.13400329998694 seconds and remains intact. A focused regression failed before correction.

**Auditor v2 fixes the cause.** For k>degree(R32 P_j), require the independent ball contains0, then impose the proved exact0. Do not clip arbitrary intervals or raise precision. The nonzero degree edge remains checked. The corrected audit accepts every required input at the same precision and source bytes. Four initial tests pass; the final seven controls additionally cover native noncentered radius uncertainty and pinned-cache invalidation/forgery.

**Weighted consequence versions remain distinct.** Initial entry-loop integer endpoints, exact-zero summand skips, and native integer center/radius contractions are preserved separately. The zero skip version replayed the earlier316 result exactly. Native contractions can change last-bit interval widths while preserving the bound, and were reassessed/replayed into separate outputs. Their complete error covers center/radius cross terms, radius products and inverse-weight uncertainty at the common denominator2^(3*bits+4), before row-radius Loewner inflation. No Python numerical guard was disabled.

**Accepted low reuse is narrow and exercised.** Optional `--reuse-accepted-low` pins the exact source224 bytes and its successful full audit bytes. It verifies all low definitions, raw matrices/scalars, mu, residual signature and source fingerprints, plus every copied reference shape/containment. All exact residual polynomials and all requested heads are reconstructed afresh. The actual224 reuse audit passed; its receipt labels inherited low versus fresh head evidence and preserves ancestor/current auditor identities. This is not arbitrary user-supplied cache acceptance or a new theorem whitelist.

**Operational helper failure is retained.** The first file-path comparison lacked repository-root PYTHONPATH and failed before numerical evaluation. The unchanged script then passed with the explicit environment. Both receipts remain; no source or precision was changed to mask the import failure.

An altered exact witness margin and a changed reference mu were rejected by the real CLIs at exit2, with no success output. These negative controls are distinct from mathematical negativity and from software failures.

## Accuracy selection and execution limit

m224 is the residual-degree split, not an assumed sufficient accuracy. The reviewed rule selected316, then626, each the smallest even new index with w_new<=w_old/2. No sign/cutoff or precision sweep occurred. All outside tail mass remains paid.

The626 source contract reserved30seconds for generation,60 for independent head auditing,10 each for assessment/replay and3 for rejection checks. It was declared before execution and fit the then-current balance. The source child exceeded30seconds, was killed/reaped, and produced no packet. Therefore no626 input acceptance or matrix result exists. Restarting the uncompleted generation with all verification phases still reserved no longer fit the remaining allowance. This does not prove the operation cannot finish under a larger envelope or a different justified implementation.

## Complete charged execution ledger

[Machine-readable ledger](data/execution-ledger.json) retains unrounded elapsed values and all commands. Every owned child was observed exited/reaped, including expected rejections, the failed audit/regression/import and the timeout. There is no OS-wide process-tree claim.

| Execution | Charged wall seconds | Exit | Owned termination |
| --- | ---: | ---: | --- |
| source-m224-v1 | 132.671350400 | 0 | exited/reaped |
| audit-m224-v1 | 66.134003300 | 2 | exited/reaped |
| residual-zero-before | 1.941561500 | 1 | exited/reaped |
| weighted-controls-after | 1.258995600 | 0 | exited/reaped |
| audit-m224-v2 | 67.962458700 | 0 | exited/reaped |
| assessment-m224 | 2.810172700 | 0 | exited/reaped |
| source-m316-v1 | 13.145036000 | 0 | exited/reaped |
| audit-m316-v2 | 79.557895200 | 0 | exited/reaped |
| assessment-m316 | 7.138204000 | 0 | exited/reaped |
| weighted-controls-reuse | 1.578907400 | 0 | exited/reaped |
| replay-m316 | 4.766169100 | 0 | exited/reaped |
| weighted-controls-native | 1.862604100 | 0 | exited/reaped |
| assessment-m316-native | 2.463067500 | 0 | exited/reaped |
| source-m626-v1 | 30.010512500 | 1 | timeout; killed/reaped |
| audit-m224-reused-low | 13.742733300 | 0 | exited/reaped |
| replay-m316-native | 1.974256000 | 0 | exited/reaped |
| attack-margin | 1.542770900 | 2 | exited/reaped |
| attack-reference | 0.274123000 | 2 | exited/reaped |
| fixed-comparison | 0.224368000 | 1 | exited/reaped |
| fixed-comparison-v2 | 0.894278000 | 0 | exited/reaped |
| even-gap | 0.921229800 | 0 | exited/reaped |

New charge **432.87469699967187 seconds** plus carried **97.41939420008566 seconds** gives **530.2940911997575/600 seconds**, leaving **69.70590880024247 seconds**. The ceiling was not exhausted. The next fully reserved source/independent-check path did not fit; no reset or silent enlargement occurred. Documentation, source preservation and integrity checks are metadata work, not numerical research.

## Evidence retention and limitations

Full source inputs and independent interval receipts are required to replay the exact even-block claim. The316 source/audit gzip files exceed2MiB and are retained as necessary proof inputs/independent-verifier evidence, not disposable raw datasets. Other raw variants, failed procedures, attacks and exact endpoints remain separately identified. Final manifest binds all retained members except itself by SHA-256 and size.

Independent read-only mathematical/code review accepted the full-source metric/sign/error logic, native contraction, pinned reuse safeguards and even-gap proof. It executed no numerical work. Shared Suzuki source identities, local2T<pi estimates, Arb and some exact polynomial algebra remain trust premises; source-level independence is not a separate arithmetic kernel or Lean proof.

No odd or full reference positivity, negative actual odd reference direction, full Weil positivity atT3/5, direct true inverse, all-support theorem, production certificate profile/admission, clean-source proof-bearing claim or RH result is established. Earlier methods, certificates and research records remain unchanged. The unresolved odd question is not closure or rejection of the method.

## 2026-10-24T15:02:23Z — Final evidence integrity

All843 protected antecedent public research/source files are unchanged; the maintained `scripts/README.md` was intentionally updated for the new commands. Final executed source snapshots match the working procedures. All466 checked local public-document links resolve, authored text has no trailing whitespace, and scoped attributes preserve exact bundle bytes. All21 owned numerical children exited/reaped; the626 packet is absent.

`data/environment-final.json` records runtime and code/input fingerprints. `data/integrity-validation.json` records the metadata checks. The final `manifest.json` binds every other bundle member by relative path, byte size and SHA-256 and excludes itself. No extra numerical run or theorem verification is implied by sealing.
