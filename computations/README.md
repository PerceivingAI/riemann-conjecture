# Computations

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T21:20:00Z`

This directory contains timestamped numerical and symbolic experiments. Every retained computation must be reproducible and must distinguish numerical evidence from proof.

## Current computation records

- [`X-20260820-001`](2026-08-20T210531Z-exact-identity-verification.md) — exact rational checks of identities used by `A-002` and `A-003`.
- [`X-20260820-002`](2026-08-20T210531Z-airy-kernel-localization.md) — numerical localization of the uniform saddle.
- [`X-20260820-003`](2026-08-20T210531Z-prime-trace-cutoff-study.md) — high-precision cutoff/stability study of the generalized prime trace.
- [`X-20260820-004`](2026-08-20T210531Z-prime-density-turning-window.md) — discrete-prime versus continuous-density decomposition in turning-scale bins.
- [`X-20260820-005`](2026-08-20T212000Z-saddle-window-phase-loss.md) — post-turning saddle width, pre-turning envelope rates, and phase-loss diagnostics.
- [`X-20260820-006`](2026-08-20T212000Z-single-zero-regional-cancellation.md) — regional decomposition of exact complex zero-mode Laguerre transforms.

## Code

Authoritative research scripts are under [`../scripts/`](../scripts/). They intentionally use only the Python standard library.

When a script is modified after a recorded experiment, the computation record retains the command, relevant environment, and script hash/version information needed to distinguish the historical run.

Use [`../templates/COMPUTATION.md`](../templates/COMPUTATION.md) for new records.
