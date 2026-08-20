# Documentation Index

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T20:49:00Z`

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

## Landmark attempt records

- [`A-20260820-001 — Li coefficients, generalized centers, and the Laguerre-weighted prime trace`](attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md) — first formal route; status `BLOCKED`; later raw-trace target corrected by `A-002`.
- [`A-20260820-002 — Pole-subtracted prime-Laguerre trace and exact shift filtering`](attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md) — exact zeta-pole removal and discrepancy criterion; intermediate target `COMPLETE`.

## Landmark findings

- [`F-20260820-001 — Critical-line zero orbit contribution`](findings/2026-08-20T203700Z-critical-line-zero-orbit-contribution.md) — corrects the pre-protocol factor-of-two double count.
- [`F-20260820-002 — Subexponential Li growth suffices`](findings/2026-08-20T203700Z-subexponential-li-growth-suffices.md) — growth target implied by Voros's dichotomy.
- [`F-20260820-003 — Generalized center restores half-weight`](findings/2026-08-20T203700Z-generalized-center-restores-half-weight.md) — exact fixed-prime exponent cancellation and its uniformity limitation.
- [`F-20260820-004 — Square-root psi bound is circular`](findings/2026-08-20T203700Z-square-root-psi-bound-is-circular.md) — circularity boundary for prime-side estimates.
- [`F-20260820-005 — Raw prime trace has zeta-pole exponential`](findings/2026-08-20T204900Z-raw-prime-trace-has-zeta-pole-exponential.md) — invalidates the raw subexponential target.
- [`F-20260820-006 — Pole-subtracted prime-Laguerre criterion`](findings/2026-08-20T204900Z-pole-subtracted-prime-laguerre-criterion.md) — exact root-growth reformulation of RH.
- [`F-20260820-007 — Pole subtraction is prime discrepancy`](findings/2026-08-20T204900Z-pole-subtraction-is-prime-discrepancy.md) — exact `d(psi-x)` representation.
- [`F-20260820-008 — Exact pole-annihilating shift filter`](findings/2026-08-20T204900Z-exact-pole-annihilating-shift-filter.md) — degree-two filter and order-zero Laguerre kernel.

## Templates

- [`templates/ATTEMPT.md`](templates/ATTEMPT.md)
- [`templates/FINDING.md`](templates/FINDING.md)
- [`templates/COMPUTATION.md`](templates/COMPUTATION.md)

## Current state

RH remains unresolved. The active frontier is the pole-subtracted discrepancy transform `S_n`; see [`STATUS.md`](STATUS.md). The next planned route is rigorous large-`n` analysis of that kernel in logarithmic coordinates.
