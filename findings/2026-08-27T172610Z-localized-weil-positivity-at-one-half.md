# Strict localized Weil positivity at T=1/2

- **Finding ID:** `F-20260827-002`
- **Created:** `2026-08-27T17:26:10Z`
- **Last updated:** `2026-08-27T17:26:10Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For Suzuki's scaled localized Weil quadratic form at

```text
T=1/2,
```

including the exact `p=2` compressed translation and mandatory finite-support residual kernel,

```text
Q_T(w) > 0
```

for every nonzero admissible localized test function `w`.

## Proof architecture

The proof uses the existing exact-prime Legendre-Schur reduction. The canonical pre-theorem driver first mapped `N=56,60,...,104`: `N=56..68` were floating-negative, `N=72` unstable, and `N=76+` floating stable-positive. Rigorous screening then classified `N=76` as a precision-stable mathematical negative under the present Schur reduction, while fallback `N=80` stabilized positive at 512-bit Arb precision.

At `N=80`, the exact candidate uses 64-bit outward dyadic matrix intervals and 32-bit exact dyadic lower-triangular witnesses. A fixed-parameter reassembly at 640 bits leaves the exact `mu`, even margin, and odd margin unchanged while raw Arb widths contract.

A separate admission decision added only `(T,N)=(1/2,80)` to the closed v1 theorem profile. The fresh proof-bearing certificate was then assembled from scratch at 512 bits and independently replayed by the zero-float Rust verifier.

The retained lower bounds are approximately

```text
mu_80 > 0.6983326376765460
even margin > 0.0006030229450313612
odd  margin > 0.002927388923852846.
```

## Independent verification

Rust independently returns

```text
passed=true
verified_scope=localized_weil_positivity_T_1_2
dimension=80
support_T=1/2.
```

It reconstructs the factor-3 Schur matrix, verifies the exact witnesses, and proves both `40 x 40` parity blocks positive by exact rational interval congruence and Gershgorin.

Real-certificate adversarial replay distinguishes:

- malformed contract data (`factor=2`) -> exit `2`;
- a contract-valid positivity-breaking diagonal perturbation -> exit `1`;
- the unchanged theorem certificate -> exit `0`.

The closed retained-proof gate now passes `6/6` including `C-0055`.

## Evidence

- `A-20260826-001`
- pre-theorem bundle `computations/2026-08-27T151517Z-t1-2-continuation/`
- proof-bearing theorem run `X-20260827-004`
- `computations/2026-08-27T170850Z-one-half-schur-certificate/data/certificate.json`
- `computations/2026-08-27T170850Z-one-half-schur-certificate/data/rust-verification.json`

Certificate SHA-256:

```text
95dd6c7a497ad605ddc81129a774bade5fbbc769d0f6fdf29172b89da2a57a7d
```

Rust replay SHA-256:

```text
7383c91f48ead83ac9268fcdb154f9372c45ac3510339b9eaac3bd6fd461322a
```

## Limits

This is strict localized Weil positivity at one finite support value. It does not establish RH and must not be extrapolated to larger support values. The entry of the `p=3` compressed translation at `(1/2)log 3` remains a separate structural transition.
