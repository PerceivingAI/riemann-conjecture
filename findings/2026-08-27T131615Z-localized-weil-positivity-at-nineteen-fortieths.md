# Strict localized Weil positivity at T=19/40

- **Finding ID:** `F-20260827-001`
- **Created:** `2026-08-27T13:16:15Z`
- **Last updated:** `2026-08-27T13:16:15Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For Suzuki's scaled localized Weil quadratic form at

```text
T=19/40=0.475,
```

including the exact `p=2` compressed translation and the mandatory finite-support residual kernel,

```text
Q_T(w) > 0
```

for every nonzero admissible localized test function `w`.

## Proof architecture

The proof uses the established exact-prime Legendre-Schur reduction:

1. Legendre jump coercivity controls the infinite complement;
2. the exact `p=2` translation is retained;
3. `G_V`, `G_2`, and `G_R` encode low-to-tail couplings through the proved component Gram reduction;
4. at `N=68`, the rigorous complement lower bound is positive;
5. the analytic matrices are assembled at 384-bit Arb precision and outward-rounded to exact 64-bit dyadic rational intervals;
6. exact 32-bit dyadic lower-triangular parity witnesses are serialized;
7. the independent zero-float Rust verifier reconstructs the factor-3 Schur matrix and proves both `34 x 34` parity blocks positive by exact rational congruence and interval Gershgorin.

The retained bounds are approximately

```text
mu_68 > 0.7185353202932019
even margin > 0.0013831260220094517
odd  margin > 0.006360318287493695.
```

## Independent verification

The closed v1 profile explicitly admits `(T,N)=(19/40,68)`. The fresh retained theorem certificate returns

```text
passed=true
verified_scope=localized_weil_positivity_T_19_40.
```

Adversarial replay on the real certificate distinguishes:

- malformed contract data (`factor=2`) -> exit `2`;
- a contract-valid positivity-breaking diagonal perturbation -> exit `1`;
- the unchanged theorem certificate -> exit `0`.

The full default Python suite also passes (`409 passed, 2 slow-acceptance tests deselected`), the new real `N=68` slow-acceptance generator regression passes separately, the full `rh_cert` Rust suite and strict clippy pass, and `lake build` completes successfully.

## Evidence

- `A-20260826-001`
- pre-theorem candidate `X-20260827-001`
- proof-bearing theorem run `X-20260827-002`
- `computations/2026-08-27T122716Z-nineteen-fortieths-schur-certificate/data/certificate.json`
- `computations/2026-08-27T122716Z-nineteen-fortieths-schur-certificate/data/rust-verification.json`

Certificate SHA-256:

```text
d9ba45f0026de31ded30ab3a08cd8272982424368c63426131cd08428aab8ac5
```

Rust replay SHA-256:

```text
43445444b898c1b9f9dcf88a6df458cdd6e9baeef0417cddbec7490308b358f0
```

## Limits

This is strict localized Weil positivity at one finite support value. It does not establish RH and must not be extrapolated to larger support values. The eventual entry of the `p=3` compressed translation at `(1/2)log 3` remains a separate structural transition.
