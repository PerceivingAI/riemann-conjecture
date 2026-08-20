# Documentation Index

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T21:05:31Z`

This is the compact index of the Riemann Conjecture research repository.

## Core documents

- [`PROTOCOL.md`](PROTOCOL.md) — authoritative documentation and research-record rules.
- [`STATUS.md`](STATUS.md) — maintained snapshot of the current research frontier.
- [`LOG.md`](LOG.md) — append-only chronological research log.
- [`CLAIMS.md`](CLAIMS.md) — registry of important claims, their status, and dependencies.

## Research records

- [`attempts/`](attempts/) — complete proof/research attempts.
- [`findings/`](findings/) — atomic findings, lemmas, obstructions, and negative results.
- [`computations/`](computations/) — reproducible numerical or symbolic experiments.
- [`references/BIBLIOGRAPHY.md`](references/BIBLIOGRAPHY.md) — literature and external sources used by the research.
- [`../scripts/`](../scripts/) — dependency-free research tooling used by computation records.

## Landmark attempt records

- [`A-20260820-001 — Li coefficients, generalized centers, and the Laguerre-weighted prime trace`](attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md) — first formal route; `BLOCKED`; later corrected by `A-002`.
- [`A-20260820-002 — Pole-subtracted prime-Laguerre trace and exact shift filtering`](attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md) — exact zeta-pole removal and discrepancy criterion; intermediate target `COMPLETE`.
- [`A-20260820-003 — Airy-saddle structure of the pole-subtracted discrepancy kernel`](attempts/2026-08-20T210531Z-airy-saddle-discrepancy-kernel-route.md) — uniform large-`n` localization, exact Airy saddle, and pointwise-bound barrier; `PROMISING`.

## Landmark findings

- [`F-20260820-001`](findings/2026-08-20T203700Z-critical-line-zero-orbit-contribution.md) — corrected critical-line zero-orbit contribution.
- [`F-20260820-002`](findings/2026-08-20T203700Z-subexponential-li-growth-suffices.md) — subexponential Li growth suffices for RH.
- [`F-20260820-003`](findings/2026-08-20T203700Z-generalized-center-restores-half-weight.md) — generalized center restores the fixed-prime half-weight.
- [`F-20260820-004`](findings/2026-08-20T203700Z-square-root-psi-bound-is-circular.md) — square-root pointwise input is circular.
- [`F-20260820-005`](findings/2026-08-20T204900Z-raw-prime-trace-has-zeta-pole-exponential.md) — raw trace contains deterministic pole growth.
- [`F-20260820-006`](findings/2026-08-20T204900Z-pole-subtracted-prime-laguerre-criterion.md) — exact root-growth reformulation of RH.
- [`F-20260820-007`](findings/2026-08-20T204900Z-pole-subtraction-is-prime-discrepancy.md) — exact `d(psi-x)` representation.
- [`F-20260820-008`](findings/2026-08-20T204900Z-exact-pole-annihilating-shift-filter.md) — exact degree-two pole filter.
- [`F-20260820-009`](findings/2026-08-20T210531Z-exact-discrepancy-integration-by-parts.md) — exact integration-by-parts formula with PNT-closed boundaries.
- [`F-20260820-010`](findings/2026-08-20T210531Z-airy-saddle-reproduces-pole-rate.md) — Airy saddle reproduces exactly the pole rate `|q|^n`.
- [`F-20260820-011`](findings/2026-08-20T210531Z-generalized-center-signal-scale-tradeoff.md) — center choice trades prime reach against off-line signal strength.
- [`F-20260820-012`](findings/2026-08-20T210531Z-pointwise-error-bound-barrier.md) — fixed pointwise exponents above `1/2` cannot finish the route by absolute bounds.

## Computations

- [`X-20260820-001`](computations/2026-08-20T210531Z-exact-identity-verification.md) — exact finite identity checks.
- [`X-20260820-002`](computations/2026-08-20T210531Z-airy-kernel-localization.md) — Airy-saddle localization scan.
- [`X-20260820-003`](computations/2026-08-20T210531Z-prime-trace-cutoff-study.md) — high-precision cutoff study.
- [`X-20260820-004`](computations/2026-08-20T210531Z-prime-density-turning-window.md) — prime-density turning-window decomposition.

## Templates

- [`templates/ATTEMPT.md`](templates/ATTEMPT.md)
- [`templates/FINDING.md`](templates/FINDING.md)
- [`templates/COMPUTATION.md`](templates/COMPUTATION.md)

## Current state

RH remains unresolved. The active frontier is the Airy-window transform of `psi(x)-x`; see [`STATUS.md`](STATUS.md).
