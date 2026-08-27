# Documentation Index

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-27T17:39:01Z`

This is the compact index of the Riemann Conjecture research repository.

## Core documents

- [`PROTOCOL.md`](PROTOCOL.md) — authoritative documentation and research-record rules.
- [`CONTRACTS.md`](CONTRACTS.md) — formal proof-certificate contracts, trust architecture, and dependency policy.
- [`contracts/rh-weil-certificate-v1.json`](contracts/rh-weil-certificate-v1.json) — JSON Schema for exact rational certificates.
- [`../computations/retained-proofs.json`](../computations/retained-proofs.json) — closed registry binding `C-0050` through `C-0055` to their exact retained certificate paths, SHA-256 values, and theorem identities for first-class integrity/replay acceptance.
- [`STATUS.md`](STATUS.md) — maintained snapshot of the current research frontier.
- [`LOG.md`](LOG.md) — append-only chronological research log.
- [`CLAIMS.md`](CLAIMS.md) — registry of important claims, their status, and dependencies.

## Research records

- [`../attempts/`](../attempts/) — complete proof/research attempts.
- [`../findings/`](../findings/) — atomic findings, lemmas, obstructions, and negative results.
- [`../computations/`](../computations/) — reproducible numerical or symbolic experiments.
- [`../references/BIBLIOGRAPHY.md`](../references/BIBLIOGRAPHY.md) — literature and external sources used by the research.
- [`../scripts/`](../scripts/) — versioned Python research tooling and certificate generators (`scripts/cert/`).
- [`../crates/rh_engine/`](../crates/rh_engine/) — high-throughput native multi-threaded calculation engine.
- [`../crates/rh_cert/`](../crates/rh_cert/) — zero-float independent exact rational certificate verifier.
- [`../tests/`](../tests/) — property-based and exact algebraic identity test suite.
## Landmark attempt records

- [`A-20260820-001`](../attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md) — generalized Li/Laguerre route; `BLOCKED`; later corrected by `A-002`.
- [`A-20260820-002`](../attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md) — exact zeta-pole removal and discrepancy criterion; `COMPLETE`.
- [`A-20260820-003`](../attempts/2026-08-20T210531Z-airy-saddle-discrepancy-kernel-route.md) — uniform asymptotic saddle analysis; `SUPERSEDED` as active frontier by `A-004`.
- [`A-20260820-004`](../attempts/2026-08-20T212000Z-post-turning-phase-aware-discrepancy-route.md) — post-turning geometry, phase-sensitive single-zero response, and averaging barriers; `COMPLETE`.
- [`A-20260820-005`](../attempts/2026-08-20T221500Z-uniform-preturning-laguerre-phase-route.md) — uniform pre-turning phase, exact zero-frequency stationary map, Cayley saddle matching, and `L2` circularity guard; `COMPLETE`.

- [`A-20260820-006`](../attempts/2026-08-20T224400Z-prime-side-chirp-dirichlet-reduction.md) — endpoint closure, microlocal prime Dirichlet reduction, and generic one-dimensional mean-value barrier; `COMPLETE`.

- [`A-20260821-001`](../attempts/2026-08-21T020900Z-global-bilinear-vaughan-chirp-route.md) — global Vaughan/Heath-Brown bilinear phase test; rank-one/separability and square-root-saving barriers; `COMPLETE` negative diagnostic.

- [`A-20260821-002`](../attempts/2026-08-21T022600Z-positivity-moment-weil-mechanism-audit.md) — Li Gram/CND audit, Weil support thresholds, and first-prime compressed-translation mechanism; `COMPLETE`.
- [`A-20260821-003`](../attempts/2026-08-21T040654Z-first-prime-weil-support-continuation.md) — first-prime support continuation; exact endpoint absorption, digamma kernel decomposition, residual-term correction, and external-certificate audit; `COMPLETE` intermediate.
- [`A-20260821-004`](../attempts/2026-08-21T085252Z-exact-prime-legendre-schur-certificate.md) — exact-prime Legendre-Schur route; global `0.69V` target refuted as too lossy, exact high-mode complement and tail-Gram reduction proved, and a clean `N=32` exact certificate establishes strict localized Weil positivity at `T=7/20`; `COMPLETE`.
- [`A-20260826-001`](../attempts/2026-08-26T171400Z-one-prime-support-continuation.md) — continuation inside the one-prime window; moving Legendre dimension yields independently verified theorems at `T=2/5,N=40`, `T=17/40,N=48`, `T=9/20,N=56`, `T=19/40,N=68`, and `T=1/2,N=80`; `PROMISING`.

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
- [`F-20260820-017`](../findings/2026-08-20T221500Z-uniform-preturning-stationary-map.md) — exact uniform zero-frequency stationary map.
- [`F-20260820-018`](../findings/2026-08-20T221500Z-critical-saddle-reproduces-cayley-mode.md) — fixed critical saddle reproduces the Cayley mode with unit leading normalization.
- [`F-20260820-019`](../findings/2026-08-20T221500Z-critical-half-weight-laguerre-chirp.md) — critical-half-weight nonlinear prime-discrepancy chirp.
- [`F-20260820-020`](../findings/2026-08-20T221500Z-coefficient-block-l2-is-rh-equivalent.md) — coefficient-block `L2` root criterion is RH-equivalent.
- [`F-20260820-021`](../findings/2026-08-20T221500Z-high-zero-endpoint-coalescence.md) — high zero frequencies coalesce with the pre-turning endpoint.

- [`F-20260820-022`](../findings/2026-08-20T224400Z-below-first-prime-endpoint-bound.md) — below-first-prime endpoint is polynomial; shrinking endpoints are subexponential.
- [`F-20260820-023`](../findings/2026-08-20T224400Z-prime-frequency-cap.md) — actual prime-side Mellin frequency is only `O(sqrt(n))`.
- [`F-20260820-024`](../findings/2026-08-20T224400Z-microlocal-dirichlet-reduction.md) — fixed-interior chirp cell reduces to a critical-half-weight prime Dirichlet polynomial.
- [`F-20260820-025`](../findings/2026-08-20T224400Z-montgomery-vaughan-length-barrier.md) — classical mean-value length term retains a positive exponential root base.
- [`F-20260820-026`](../findings/2026-08-20T224400Z-microlocal-subexponential-is-zero-sensitive.md) — independent matched-cell subexponential control is zero-sensitive.

- [`F-20260821-001`](../findings/2026-08-21T020900Z-finite-convolutions-preserve-rank-one-chirp.md) — every finite multiplicative convolution preserves rank-one phase geometry.
- [`F-20260821-002`](../findings/2026-08-21T020900Z-dyadic-type-ii-chirp-is-separable.md) — dyadic Type-II chirp kernels are asymptotically separable.
- [`F-20260821-003`](../findings/2026-08-21T020900Z-bilinear-nonseparability-scale.md) — unit cross phase requires `sqrt(n)` logarithmic scale; total formal phase excursion is `pi n`.
- [`F-20260821-004`](../findings/2026-08-21T020900Z-square-root-saving-threshold.md) — direct fixed-interior prime estimates require square-root saving.
- [`F-20260821-005`](../findings/2026-08-21T020900Z-vaughan-phase-route-blocked.md) — generic Vaughan/Heath-Brown phase route is blocked.

- [`F-20260821-006`](../findings/2026-08-21T022600Z-exact-li-gram-kernel.md) — exact finite Li Gram kernel is RH-equivalent.
- [`F-20260821-007`](../findings/2026-08-21T022600Z-li-schoenberg-herglotz-equivalence.md) — Li sequence is CND/Schoenberg-Herglotz exactly under RH.
- [`F-20260821-008`](../findings/2026-08-21T022600Z-prime-atoms-not-positive-gram-pieces.md) — generalized prime atoms are not PSD Gram pieces.
- [`F-20260821-009`](../findings/2026-08-21T022600Z-weil-primes-are-thresholded-compressed-translations.md) — prime powers enter Weil support as compressed translations.
- [`F-20260821-010`](../findings/2026-08-21T022600Z-first-prime-compressed-shift-norm.md) — exact compressed-shift norm and first-prime perturbation size.
- [`F-20260821-011`](../findings/2026-08-21T022600Z-restricted-weil-positivity-is-genuine-foothold.md) — restricted-support Weil positivity supplies an unconditional base regime.
- [`F-20260821-012`](../findings/2026-08-21T040654Z-first-prime-endpoint-absorption.md) — exact rational endpoint absorption at `T=7/20`: `V+P_2 >= (69/100)V`.
- [`F-20260821-013`](../findings/2026-08-21T040654Z-digamma-positive-kernel-decomposition.md) — digamma multiplier decomposes into monotone nonnegative kernel corrections.
- [`F-20260821-014`](../findings/2026-08-21T040654Z-finite-support-residual-is-mandatory.md) — Suzuki finite-support residual kernel is mandatory in the exact localized Weil form.
- [`F-20260821-015`](../findings/2026-08-21T040654Z-external-fp035-certificate-not-verified.md) — public FP-0.35 certificate architecture audited but not accepted as verified.
- [`F-20260821-016`](../findings/2026-08-21T085252Z-legendre-jump-harmonic-coercivity.md) — Legendre jump modes have harmonic-number coercivity.
- [`F-20260821-017`](../findings/2026-08-21T085252Z-uniform-endpoint-absorption-is-too-lossy.md) — the valid `69%` endpoint absorption is too lossy as a global full-proof lower target.
- [`F-20260821-018`](../findings/2026-08-21T085252Z-exact-prime-high-mode-complement.md) — exact-prime high Legendre modes are rigorously coercive from `N=14`.
- [`F-20260821-019`](../findings/2026-08-21T085252Z-component-tail-gram-schur-reduction.md) — component tail-Gram Schur reduction converts the remaining infinite cross problem to finite matrices.
- [`F-20260821-020`](../findings/2026-08-21T085252Z-schur-dimension-scout.md) — floating scout suggests `N=32` as a practical first rigorous Schur target.

- [`F-20260821-021`](../findings/2026-08-21T135237Z-first-prime-localized-weil-positivity.md) — clean exact-prime `N=32` Schur certificate proves strict localized Weil positivity at `T=7/20`.
- [`F-20260826-001`](../findings/2026-08-26T171400Z-moving-dimension-restores-one-prime-continuation.md) — moving the Legendre cutoff to `N=40` restores the full-tail continuation mechanism through the provisional `T=2/5` candidate.
- [`F-20260826-002`](../findings/2026-08-26T174929Z-localized-weil-positivity-at-two-fifths.md) — exact `N=40` certificate plus independent Rust replay proves strict localized Weil positivity at `T=2/5`.

- [`F-20260826-003`](../findings/2026-08-26T183125Z-localized-weil-positivity-at-seventeen-fortieths.md) — high-precision exact `N=48` certificate plus independent Rust replay proves strict localized Weil positivity at `T=17/40`.

- [`F-20260826-004`](../findings/2026-08-26T190517Z-localized-weil-positivity-at-nine-twentieths.md) — 512-bit exact `N=56` certificate plus independent Rust replay proves strict localized Weil positivity at `T=9/20`.
- [`F-20260827-001`](../findings/2026-08-27T131615Z-localized-weil-positivity-at-nineteen-fortieths.md) — separately admitted fresh 384-bit exact `N=68` certificate plus independent Rust replay proves strict localized Weil positivity at `T=19/40`.
- [`F-20260827-002`](../findings/2026-08-27T172610Z-localized-weil-positivity-at-one-half.md) — separately admitted fresh 512-bit exact `N=80` certificate plus independent Rust replay proves strict localized Weil positivity at `T=1/2` (`C-0055`).

## Computations

- [`X-20260820-001`](../computations/2026-08-20T210531Z-exact-identity-verification/record.md) — exact finite identity checks.
- [`X-20260820-002`](../computations/2026-08-20T210531Z-airy-kernel-localization/record.md) — saddle localization scan.
- [`X-20260820-003`](../computations/2026-08-20T210531Z-prime-trace-cutoff-study/record.md) — high-precision cutoff study.
- [`X-20260820-004`](../computations/2026-08-20T210531Z-prime-density-turning-window/record.md) — prime-density turning-window decomposition.
- [`X-20260820-005`](../computations/2026-08-20T212000Z-saddle-window-phase-loss/record.md) — saddle width and phase-loss diagnostics.
- [`X-20260820-006`](../computations/2026-08-20T212000Z-single-zero-regional-cancellation/record.md) — regional cancellation in exact zero modes.
- [`X-20260820-007`](../computations/2026-08-20T221500Z-uniform-preturning-phase/record.md) — uniform stationary map, small-`u` comparison, Cayley phase, and unit-normalization diagnostics.

- [`X-20260820-008`](../computations/2026-08-20T224400Z-chirp-window-reduction/record.md) — first-prime frequency cap, chirp-cell scales, and generic mean-value root diagnostics.

- [`X-20260821-001`](../computations/2026-08-21T020900Z-bilinear-chirp-geometry/record.md) — dyadic cross-defect, separability, and bilinear nonseparability-scale diagnostics.

- [`X-20260821-002`](../computations/2026-08-21T022600Z-positivity-kernel-audit/record.md) — Li Gram/Schoenberg finite diagnostics and Weil support/translation geometry.
- [`X-20260821-003`](../computations/2026-08-21T034825Z-first-prime-weil-continuation/record.md) — exact rational endpoint-absorption certificate and Arb enclosures for first-prime constants.
- [`X-20260821-004`](../computations/2026-08-21T085252Z-exact-prime-legendre-schur/record.md) — Arb-certified `0.69V` obstruction and high-mode complement bound, plus separately labeled floating exact-prime Schur-dimension reconnaissance.

- [`X-20260821-005`](../computations/2026-08-21T123446Z-exact-prime-schur-certificate/record.md) — clean exact-prime `N=32` rational interval certificate, independent Rust Schur/Gershgorin replay, and formal soundness build supporting `C-0050`.
- [`X-20260826-001`](../computations/2026-08-26T171400Z-one-prime-support-continuation/record.md) — support-margin map, moving-dimension diagnostics, rigorous full-tail checks, and proof-bearing exact `T=2/5,N=40` certificate with independent Rust replay supporting `C-0051`.

- [`X-20260826-002`](../computations/2026-08-26T183125Z-seventeen-fortieths-schur-certificate/record.md) — 384-bit full-tail `N=48` assembly, exact rational certificate, adversarial replay, and independent Rust PASS supporting `C-0052` at `T=17/40`.

- [`X-20260826-003`](../computations/2026-08-26T190517Z-nine-twentieths-schur-certificate/record.md) — 512-bit full-tail `N=56` assembly, exact rational certificate, adversarial replay, and independent Rust PASS supporting `C-0053` at `T=9/20`.
- [`X-20260827-001`](../computations/2026-08-27T115112Z-t19-40-continuation/record.md) — canonical pre-theorem `T=19/40` continuation bundle; `N=64` is stable-negative after precision escalation and `N=68` reaches exact `CANDIDATE_READY`; the later separate admission/theorem replay is `X-20260827-002`.
- [`X-20260827-002`](../computations/2026-08-27T122716Z-nineteen-fortieths-schur-certificate/record.md) — proof-bearing exact `T=19/40,N=68` theorem certificate, independent Rust PASS, adversarial replay, and acceptance verification supporting `C-0054`.
- [`X-20260827-003`](../computations/2026-08-27T134254Z-rust-exact-verifier-optimization/record.md) — zero-float Rust verifier optimization and exact semantic replay: retained theorem outputs are byte-semantically unchanged as parsed JSON while debug replay timings fall by roughly `3–4x` over the previously benchmarked `N=32..56` corpus.
- [`X-20260827-004`](../computations/2026-08-27T170850Z-one-half-schur-certificate/record.md) — separately admitted fresh exact `T=1/2,N=80` theorem certificate, independent zero-float Rust PASS, adversarial replay, and retained-proof registration supporting `C-0055`.


## Templates

- [`../templates/ATTEMPT.md`](../templates/ATTEMPT.md)
- [`../templates/FINDING.md`](../templates/FINDING.md)
- [`../templates/COMPUTATION.md`](../templates/COMPUTATION.md)

## Current state

RH remains unresolved. `C-0050` at `T=7/20`, `C-0051` at `T=2/5`, `C-0052` at `T=17/40`, `C-0053` at `T=9/20`, `C-0054` at `T=19/40`, and `C-0055` at `T=1/2` are independently verified finite-support theorems. `A-20260826-001` remains active. The immediate frontier is fresh canonical one-prime continuation above `T=1/2` without extrapolating the next dimension; the entry of the `p=3` compressed translation at `(1/2)log 3` remains a separate structural phase. See [`STATUS.md`](STATUS.md).
