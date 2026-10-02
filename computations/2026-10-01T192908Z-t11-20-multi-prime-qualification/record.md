# P9 multi-prime non-theorem qualification

- **Predeclared:** `2026-10-01T19:29:08Z`
- **Role:** non-theorem end-to-end qualification
- **Support:** `T=11/20=0.55`
- **Structural window:** strict `log(3)/2 < T < log(4)/2`
- **Required active set:** exactly `{2,3}`
- **Theorem admission:** none; v2 whitelist remains empty
- **Stop condition:** terminal pre-theorem driver state only; if `CANDIDATE_READY` is reached, stop there and do not generate/admit a theorem certificate.

## Predeclared diagnostic grid

The dimension grid is frozen before observing any P9 numerical result:

```text
N = 96,100,104,108,112,116,120,124,128,132,136,140,144
```

This range deliberately brackets the existing one-prime frontier near `N=104` while extending far enough to exercise the new two-term stack without changing the grid after seeing scout or rigorous outcomes.

## Frozen driver settings

```text
scout resolutions: 8
scout workers: 3
rigorous workers: 2
Arb precision ladder: 128,256,384,512 bits
residual order: 32
matrix rounding bits: 64..104 using the driver's canonical ladder
witness bits: 32..56 using the driver's canonical ladder
candidate precision step: 128 bits
candidate precision extra steps: 2
```

Primary qualification output:

```text
computations/2026-10-01T192908Z-t11-20-multi-prime-qualification/data/run-a
```

Reproduction output, using the same source state and settings:

```text
computations/2026-10-01T192908Z-t11-20-multi-prime-qualification/data/run-b
```

The shared rigorous cache is allowed only as a performance optimization; bundle/result equivalence must be checked independently from cache-hit status.

## Required qualification observations

The run must demonstrate, without theorem promotion:

- strict support-window detection and exact active set `{2,3}`;
- combined two-term assembly;
- nontrivial combined-prime `GP` path including cross terms;
- positive rigorous complement when a candidate survives;
- Arb precision escalation behavior;
- exact candidate construction and precision-stability confirmation if reached;
- deterministic canonical ordering despite parallel completion;
- verified worker cleanup with zero active children;
- a sealed manifest-last bundle;
- reproduction under the identical predeclared configuration.

Results are appended only after both qualification executions complete.

## Qualification attempt A result

Run A completed at `NO_CANDIDATE` after the floating scout. All 13 predeclared dimensions `96..144` were classified negative. The bundle sealed correctly with active set `[2,3]`, strict v2 structural-window metadata, three scout workers reaped, and `active_children_after_cleanup=0`.

This does **not** satisfy P9 because rigorous assembly, precision escalation, exact candidate construction, and candidate stability were not reached. The original grid is not altered or reinterpreted.

## Predeclared diagnostic extension C

- **Predeclared:** `2026-10-01T19:30:49Z`
- **Reason:** the first qualification grid exhausted its predeclared upper boundary without entering the rigorous stage.
- **Status:** separate diagnostic extension; it is not part of a theorem claim and is transparently adaptive to the failed coverage boundary of Run A.
- **Support remains fixed:** `T=11/20`.
- **All driver settings remain identical to Run A.**
- **New grid is frozen before observing any result from this extension:**

```text
N = 148,152,156,160,164,168,172,176,180,184,188,192,196,200,204,208,212,216,220,224,228,232,236,240,244,248,252,256
```

Primary extension output:

```text
computations/2026-10-01T192908Z-t11-20-multi-prime-qualification/data/run-c
```

If Run C reaches a terminal state that exercises the rigorous/candidate path, its reproducibility run will use the identical frozen extension grid and settings at:

```text
computations/2026-10-01T192908Z-t11-20-multi-prime-qualification/data/run-d
```

No further grid extension is part of this predeclaration.

## Qualification attempt C execution-boundary result

Run C did not reach a mathematical terminal state. At `2026-10-01T20:01:13Z`, the external Portus execution session reached its configured 1800-second limit while both rigorous workers were still actively computing the first 128-bit assemblies for `N=192` and `N=196`. The session controller terminated the complete process tree and confirmed `descendantsRemaining=0`.

Before termination:
- all eight scout resolutions completed;
- the stable-positive scout frontier began at `N=192`;
- rigorous targets were deterministically selected as `N=192,196`;
- both rigorous workers remained responsive and accumulated CPU continuously;
- no rigorous attempt returned, so no cache entry, candidate, or completed bundle was produced.

The output directory contains only operational `.live` state and `.run.lock`; there is no `run-manifest.json`. It is therefore explicitly incomplete evidence, not a continuation result.

## Execution retry E

- **Predeclared:** `2026-10-01T20:01:49Z`
- **Reason:** retry the exact frozen Run C qualification after an external execution-session timeout.
- **Mathematical/search configuration:** byte-for-byte equivalent CLI settings to Run C.
- **Grid:** unchanged `148,152,...,256`.
- **Support:** unchanged `11/20`.
- **Precision/matrix/witness/scout/worker settings:** unchanged.
- **Cache:** unchanged `.cache/p9-t11-20-qualification`.
- **Only changes:** fresh output directory and a longer external execution-session allowance.

Retry output:

```text
computations/2026-10-01T192908Z-t11-20-multi-prime-qualification/data/run-e
```

If Run E reaches `CANDIDATE_READY`, reproducibility run D remains reserved for the identical frozen configuration after E is inspected. No dimension or precision tuning is permitted between E and D.

## Qualification attempt E execution-boundary result

Run E repeated the exact frozen extension configuration from Run C with a longer external execution allowance. It again entered the rigorous stage at the same deterministically selected targets:

```text
primary:  N=192
fallback: N=196
precision ladder: 128,256,384,512
```

Both workers began the first `128`-bit rigorous assembly and remained continuously CPU-active. Neither worker returned a rigorous result before the external execution session reached its hard one-hour limit.

Recorded live-state facts:

```text
Run E started:              2026-10-01T20:02:35Z
last heartbeat:             2026-10-01T21:02:26Z
recorded elapsed:           3590.867 s
workflow state:             RIGOROUS_PRECISION_SEARCH
active dimensions:          192,196
completed rigorous attempts: 0
```

The session controller terminated the complete Run E process tree at the hard execution boundary and verified that no descendants remained. A subsequent OS process scan found no repository Python/uv/Rust processes still running.

No rigorous result had completed, therefore:

- no rigorous `A/GV/GP/GR` artifact was returned;
- no rigorous `mu_N` value was returned;
- no precision escalation beyond the first 128-bit assembly was reached;
- no exact candidate was constructed;
- no candidate stability check was reached;
- no `CANDIDATE_READY` state was reached;
- no reproduction run was justified;
- no theorem admission was considered.

The shared cache directory contains no committed cache entries. The interrupted assembly therefore cannot be resumed from a durable rigorous checkpoint; an identical retry would restart the same first 128-bit computation.

## P9 qualification verdict

**Status: NOT QUALIFIED — rigorous-stage performance blocker.**

P9 successfully demonstrated the front half of the new stack:

- strict support detection at `T=11/20`;
- exact active set `{2,3}`;
- deterministic multi-resolution floating scout;
- combined two-prime reconnaissance;
- stable-positive scout frontier beginning at `N=192`;
- deterministic primary/fallback selection `192,196`;
- bounded parallel worker execution;
- correct scout cleanup and sealed bundle behavior in Run A.

P9 did **not** demonstrate the proof-bearing back half:

- completed two-prime rigorous assembly at the qualifying dimensions;
- returned combined-prime `GP` at those dimensions;
- returned rigorous complement `mu_N`;
- rigorous precision escalation;
- exact candidate construction;
- higher-precision candidate stability;
- `CANDIDATE_READY`;
- completed-run reproducibility.

This is an operational/tooling qualification failure, **not a mathematical negative result**. No claim is made that `N=192`, `N=196`, or `T=11/20` fails the rigorous inequality. The rigorous computation did not finish.

No further dimension extension or parameter tuning belongs to P9. The next prerequisite for another end-to-end qualification is a separate performance-hardening slice for the generic rigorous multi-prime assembler. Only after that optimization is independently verified should a new qualification run be predeclared.

The production v2 theorem whitelist remains empty. No theorem certificate, retained proof, or theorem claim was created.



