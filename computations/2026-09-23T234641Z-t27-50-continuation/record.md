# Canonical pre-theorem continuation at T=27/50

- **Computation ID:** `X-20260923-001`
- **Created:** `2026-09-23T23:46:41Z`
- **Last updated:** `2026-09-24T02:32:15Z`
- **Type:** `PRE-THEOREM CONTINUATION / RIGOROUS FULL-TAIL SCREEN / EXACT CANDIDATE`
- **Supports:** `A-20260826-001`
- **Status:** `CANDIDATE_READY — PRE-THEOREM EVIDENCE ONLY`

## Objective

Run the next canonical one-prime localized Weil / Legendre-Schur continuation slice at the exact support

```text
T=27/50=0.54
```

which remains strictly inside the current `p=2`-only window and below the structural threshold `(1/2)log 3`.

This is a **pre-theorem** computation. The canonical driver must stop at `CANDIDATE_READY` or another fail-closed terminal state. This run does not admit a support/dimension pair, edit the closed theorem contract, generate a theorem certificate, invoke the independent theorem verifier, or establish RH.

## Predeclared dimension range

Before observing the canonical run results, the search range is fixed as

```text
N=80,84,88,...,144
```

equivalently

```text
--n-min 80
--n-max 144
--n-step 4
```

This range was selected before the p17 diagnostic work: it overlaps the previous `T=21/40` transition region, includes the prior verified dimension `N=96`, and leaves substantial headroom above it without extrapolating the new transition dimension. The dirty-tree p17 diagnostic performed during tooling closure does **not** change this canonical range and is not retained as theorem or canonical research evidence.

If no candidate survives, or if useful scout behavior first appears only at the upper boundary, the result will not be interpreted as a mathematical obstruction without a separately predeclared range extension.

## Canonical workflow

The run uses:

```text
driver_version = continuation-driver-p17-v1
cache_version  = continuation-driver-v6
scout levels   = 8 canonical resolutions
stability      = highest 3 scout levels, existing 1% relative Schur tolerance
rigorous Arb   = 128 -> 256 -> 384 -> 512 bits as needed
candidate      = exact outward rational rounding + exact witness
confirmation   = fixed-parameter higher-precision reassembly
```

The p17 implementation was closed and verified before this record was created. Its implementation commit is:

```text
3516d264e65170fc53d920e6b573b8d5d6a6a832
```

The actual run provenance must report a clean Git tree at its own committed pre-run record revision.

## Executed command

From the repository root:

```text
uv run --locked python -m scripts.weil_continuation_driver \
  --support 27/50 \
  --n-min 80 \
  --n-max 144 \
  --n-step 4 \
  --output-dir computations/2026-09-23T234641Z-t27-50-continuation/data/continuation-T027-050
```

The CLI owns its canonical bounded process parallelism. The output-directory bundle must contain a final `run-manifest.json` before it can be treated as completed evidence.

## Pre-run acceptance conditions

Before execution:

1. the p17 implementation/tests/docs are committed;
2. this record and the active-attempt predeclaration are committed;
3. `git status --short` is empty;
4. no prior continuation process is running.

After execution:

1. inspect the terminal workflow state;
2. verify `git_dirty=false` in immutable run provenance;
3. verify manifest artifact hashes/sizes;
4. verify worker cleanup and no orphan continuation processes;
5. update this record with outputs and limitations;
6. stop at the pre-theorem boundary.

## Completed canonical run

The predeclared command was executed from clean repository commit

```text
392aa3d3ae0583dc7a26956bf70295771af1faee
```

and completed normally with exit code `0`. The immutable manifest records

```text
driver_version = continuation-driver-p17-v1
git_commit      = 392aa3d3ae0583dc7a26956bf70295771af1faee
git_dirty       = false
Python          = CPython 3.14.0
python-flint    = 0.9.0
final_state     = CANDIDATE_READY
```

The p17 floating scout classified the predeclared range as

```text
N=80,84,88,92       negative
N=96                unstable
N=100,104,...,144   stable-positive
```

so the canonical primary/fallback pair was `N=100,N=104`.

Rigorous full-tail Arb screening then gave

```text
N=100 -> MATHEMATICAL_NEGATIVE after 128/256/384/512-bit escalation
N=104 -> PRECISION_STABLE at 512 bits
```

Thus the floating primary was rejected by the rigorous stage and the fallback `N=104` became the exact-candidate target.

## Exact candidate and cross-precision confirmation

At `N=104`, exact outward rounding succeeded with

```text
working precision = 512 bits
residual order    = 32
matrix bits       = 64
witness bits      = 32
```

The retained exact rational lower quantities are

```text
mu_lower =
5555286879239818446537772452241770055413474442715269417182811 /
8362151934403129389124989932521990256254768465142452064354304
≈ 0.6643369939721553

even Gershgorin margin =
225795032211778199860554599793086932609334993295756235322614595054656966643661045652277426626799 /
945183084096279532531840801905299481742737949576160080016356461110647801069817649399237409828241408
≈ 0.0002388902594756742

odd Gershgorin margin =
92083030916052298411705194877268363638350130509372505435337748640783352529515447418897865313969 /
118147885512034941566480100238162435217842243697020010002044557638830975133727206174904676228530176
≈ 0.000779387887620489
```

All three margins are strictly positive. Holding support, dimension, residual order, matrix bits, and witness bits fixed, the candidate was reassembled at 640-bit Arb precision. The precision-stability artifact classifies the result as `CANDIDATE_STABLE`; the exact margins and their signs were unchanged while the underlying Arb enclosures contracted.

The canonical driver therefore terminated at

```text
CANDIDATE_READY
selected (T,N)=(27/50,104)
base precision=512 bits
confirmed precision=640 bits
```

## Bundle integrity and cleanup

The final manifest lists 19 retained artifacts. A post-run audit recomputed every listed SHA-256 and byte count with zero mismatches. Key retained file hashes are

```text
summary.json
9e07b4effb88e586db7bbe50450ef5363aff24b271fc328f082778ab13d5b926

candidate/candidate.json
ead3dde00dcaf7283891968f6c59ab87d015a3e4ab94692c98a734256166a1cb

candidate/precision-stability-N104.json
792f3220156f27fcf11fb0c77a6c16a09bb5dec885df309d385c42c26746a0cd

run-manifest.json
4807d63b42b4fd3509222ea47c4eca2d8ca40cf6859e931992f80b6485371d34
```

Worker cleanup was verified by the manifest:

```text
executors_shutdown=2
worker_processes_reaped=5
cleanup_escalations=0
workers_terminated=0
workers_killed=0
active_children_after_cleanup=0
```

A separate OS process check found no remaining continuation process after completion.

## Interpretation

`X-20260923-001` is the clean canonical pre-theorem continuation record at `T=27/50`. It supplies reproducible generator-side evidence that the current one-prime Legendre-Schur machinery reaches an exact positive, cross-precision-stable candidate at `N=104`, while the smaller floating-scout target `N=100` fails rigorous full-tail screening.

This does **not** establish a new admitted finite-support theorem. `(27/50,104)` has not been added to the closed theorem contract, no proof-bearing theorem certificate has been generated, and no independent zero-float Rust theorem replay has been performed. The independently verified finite-support frontier therefore remains `(T,N)=(21/40,96)` / `C-0056` unless and until a separate explicit admission and fresh proof-bearing replay are completed.

## Interpretation boundary

A future `CANDIDATE_READY` result would be generator-side evidence only. Any theorem-facing admission would require a separate explicit decision and a fresh independently verified proof-bearing computation. None of this proves RH.
