# Documentation Index

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T21:20:00Z`

This is the compact index of the Riemann Conjecture research repository.

## Core documents

- [`PROTOCOL.md`](PROTOCOL.md) — authoritative documentation and research-record rules.
- [`STATUS.md`](STATUS.md) — maintained snapshot of the current research frontier.
- [`LOG.md`](LOG.md) — append-only chronological research log.
- [`CLAIMS.md`](CLAIMS.md) — registry of important claims, their status, and dependencies.

## Research records

- [`../attempts/`](../attempts/) — complete proof/research attempts.
- [`../findings/`](../findings/) — atomic findings, lemmas, obstructions, and negative results.
- [`../computations/`](../computations/) — reproducible numerical or symbolic experiments.
- [`../references/BIBLIOGRAPHY.md`](../references/BIBLIOGRAPHY.md) — literature and external sources used by the research.
- [`../scripts/`](../scripts/) — dependency-free research tooling used by computation records.
- [`../crates/rh_engine/`](../crates/rh_engine/) — high-throughput native multi-threaded calculation engine.
- [`../tests/`](../tests/) — property-based and exact algebraic identity test suite.

## Landmark attempt records

- [`A-20260820-001`](../attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md) — generalized Li/Laguerre route; `BLOCKED`; later corrected by `A-002`.
- [`A-20260820-002`](../attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md) — exact zeta-pole removal and discrepancy criterion; `COMPLETE`.
- [`A-20260820-003`](../attempts/2026-08-20T210531Z-airy-saddle-discrepancy-kernel-route.md) — uniform asymptotic saddle analysis; `SUPERSEDED` as active frontier by `A-004`.
- [`A-20260820-004`](../attempts/2026-08-20T212000Z-post-turning-phase-aware-discrepancy-route.md) — post-turning geometry, phase-sensitive single-zero response, and averaging barriers; `COMPLETE`.

## Landmark findings

- [`F-20260820-001`](../findings/2026-08-20T203700Z-critical-line-zero-orbit-contribution.md) — corrected critical-line zero-orbit contribution.
- [`F-20260820-002`](../findings/2026-08-20T203700Z-subexponential-li-growth-suffices.md) — subexponential Li growth suffices for RH.
- [`F-20260820-003`](../findings/2026-08-20T203700Z-generalized-center-restores-half-weight.md) — generalized center restores the fixed-prime half-weight.
- [`F-20260820-004`](../findings/2026-08-20T203700Z-square-root-psi-bound-is-circular.md) — square-root pointwise input is circular.
- [`F-20260820-005`](../findings/2026-08-20T204900Z-raw-prime-trace-has-zeta-pole-exponential.md) — raw trace contains deterministic pole growth.
- [`F-20260820-006`](../findings/2026-08-20T204900Z-pole-subtracted-prime-laguerre-criterion.md) — exact root-growth reformulation of RH.
- [`F-20260820-007`](../findings/2026-08-20T204900Z-pole-subtraction-is-prime-discrepancy.md) — exact `d(psi-x)` representation.
- [`F-20260820-008`](../findings/2026-08-20T204900Z-exact-pole-annihilating-shift-filter.md) — exact degree-two pole filter.
- [`F-20260820-009`](../findings/2026-08-20T210531Z-exact-discrepancy-integration-by-parts.md) — exact integration-by-parts formula.
- [`F-20260820-010`](../findings/2026-08-20T210531Z-airy-saddle-reproduces-pole-rate.md) — smooth-density saddle reproduces pole rate.
- [`F-20260820-011`](../findings/2026-08-20T210531Z-generalized-center-signal-scale-tradeoff.md) — center choice trades prime reach against off-line signal strength.
- [`F-20260820-012`](../findings/2026-08-20T210531Z-pointwise-error-bound-barrier.md) — fixed pointwise exponents above `1/2` fail by absolute bounds.
- [`F-20260820-013`](../findings/2026-08-20T212000Z-post-turning-saddle-width.md) — post-turning classification and exact saddle width.
- [`F-20260820-014`](../findings/2026-08-20T212000Z-regionwise-absolute-bound-barrier.md) — far tail closes; pre-turning absolute route does not.
- [`F-20260820-015`](../findings/2026-08-20T212000Z-single-zero-phase-aware-transform.md) — exact phase-aware single-zero response.
- [`F-20260820-016`](../findings/2026-08-20T212000Z-mean-square-rh-boundary.md) — generic RH-scale dyadic mean square already detects the RH boundary.

## Computations

- [`X-20260820-001`](../computations/2026-08-20T210531Z-exact-identity-verification/record.md) — exact finite identity checks.
- [`X-20260820-002`](../computations/2026-08-20T210531Z-airy-kernel-localization/record.md) — saddle localization scan.
- [`X-20260820-003`](../computations/2026-08-20T210531Z-prime-trace-cutoff-study/record.md) — high-precision cutoff study.
- [`X-20260820-004`](../computations/2026-08-20T210531Z-prime-density-turning-window/record.md) — prime-density turning-window decomposition.
- [`X-20260820-005`](../computations/2026-08-20T212000Z-saddle-window-phase-loss/record.md) — saddle width and phase-loss diagnostics.
- [`X-20260820-006`](../computations/2026-08-20T212000Z-single-zero-regional-cancellation/record.md) — regional cancellation in exact zero modes.

## Templates

- [`../templates/ATTEMPT.md`](../templates/ATTEMPT.md)
- [`../templates/FINDING.md`](../templates/FINDING.md)
- [`../templates/COMPUTATION.md`](../templates/COMPUTATION.md)

## Current state

RH remains unresolved. The active frontier is now phase-aware analysis of the full Laguerre transform; see [`STATUS.md`](STATUS.md).
