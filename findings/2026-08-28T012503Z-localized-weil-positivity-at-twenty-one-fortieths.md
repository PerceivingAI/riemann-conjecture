# Strict localized Weil positivity at T=21/40

- **Finding ID:** `F-20260828-001`
- **Created:** `2026-08-28T01:25:03Z`
- **Last updated:** `2026-08-28T01:25:03Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For Suzuki's scaled localized Weil quadratic form at

```text
T=21/40,
```

including the exact `p=2` compressed translation and mandatory finite-support residual kernel,

```text
Q_T(w) > 0
```

for every nonzero admissible localized test function `w`.

## Proof architecture

Historical pre-theorem `X-20260827-005` first showed why the floating scout alone is insufficient at this support: `N=88` and `N=92` looked stable-positive in the truncated scout but became precision-stable mathematical negatives under the rigorous full-tail Schur calculation. Continuing above those cutoffs found `N=96` and `N=100` rigorously stable-positive at 512 bits. The canonical driver selected the smaller `N=96` and confirmed its fixed exact candidate from 512 to 640 bits.

A separate admission decision added only `(T,N)=(21/40,96)` to the closed v1 theorem profile. `N=100` remains outside the whitelist. Fresh proof-bearing `X-20260828-001` then reassembled the `N=96` certificate from scratch at 512 bits using 64-bit outward dyadic matrix intervals and 32-bit exact dyadic congruence witnesses.

The retained exact lower quantities correspond approximately to

```text
mu_96       > 0.69600913384063989
even margin > 0.00090134267068206139
odd  margin > 0.0037494074424420441.
```

## Independent verification

The zero-float Rust verifier independently returns

```text
passed=true
verified_scope=localized_weil_positivity_T_21_40
dimension=96
support_T=21/40.
```

It reconstructs the factor-3 Schur matrix and proves both `48 x 48` parity blocks positive by exact rational interval congruence and Gershgorin.

Real-certificate adversarial replay distinguishes:

- malformed `factor=2` -> contract failure, exit `2`;
- contract-valid positivity-breaking diagonal perturbation -> theorem failure, exit `1`;
- unchanged theorem certificate -> PASS, exit `0`.

The closed retained-proof audit passes `7/7` including `C-0056`.

## Evidence

- `A-20260826-001`
- pre-theorem continuation `X-20260827-005`
- proof-bearing theorem run `X-20260828-001`
- `computations/2026-08-28T010811Z-t21-40-schur-certificate/data/certificate.json`
- `computations/2026-08-28T010811Z-t21-40-schur-certificate/data/rust-verification.json`

Certificate SHA-256:

```text
a455dcb995a56f6d387e79b199cfc6f18ba6fca108fcfe3c00987e1c47b44824
```

Rust replay SHA-256:

```text
9530b53b00c1e96a1be82b2127adc7d1424e63af444803f169be8434f51d2e83
```

## Limits

This is strict localized Weil positivity at one finite support value. It does not establish RH and must not be extrapolated to larger supports. The mechanism is still in the one-prime regime because `21/40 < (1/2)log 3`; entry of the `p=3` compressed translation remains a separate structural transition.
