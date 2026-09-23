# Canonical pre-theorem continuation at T=27/50

- **Computation ID:** `X-20260923-001`
- **Created:** `2026-09-23T23:46:41Z`
- **Last updated:** `2026-09-23T23:46:41Z`
- **Type:** `PRE-THEOREM CONTINUATION / RIGOROUS FULL-TAIL SCREEN / EXACT CANDIDATE`
- **Supports:** `A-20260826-001`
- **Status:** `PLANNED — RUN NOT YET EXECUTED`

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

## Planned command

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

## Interpretation boundary

A future `CANDIDATE_READY` result would be generator-side evidence only. Any theorem-facing admission would require a separate explicit decision and a fresh independently verified proof-bearing computation. None of this proves RH.
