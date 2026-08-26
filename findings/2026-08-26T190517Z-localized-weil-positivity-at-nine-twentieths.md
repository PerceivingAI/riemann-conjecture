# Strict localized Weil positivity at T=9/20

- **Finding ID:** `F-20260826-004`
- **Created:** `2026-08-26T19:05:17Z`
- **Last updated:** `2026-08-26T19:05:17Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For Suzuki's scaled localized Weil quadratic form at

```text
T=9/20=0.45,
```

including the exact `p=2` compressed translation and the mandatory finite-support residual kernel,

```text
Q_T(w) > 0
```

for every nonzero admissible localized test function `w`.

## Proof architecture

The proof uses the same exact-prime Legendre-Schur reduction established earlier:

1. Legendre jump coercivity controls the infinite complement;
2. the exact `p=2` translation is retained rather than replaced by the lossy uniform endpoint absorption;
3. `G_V`, `G_2`, and `G_R` encode the low-to-tail couplings through finite component Gram identities;
4. at `N=56`, the rigorous complement lower bound is positive;
5. the factor-3 Schur matrix is serialized as exact rational intervals after 512-bit Arb/exact-polynomial assembly;
6. the independent zero-float Rust verifier reconstructs the Schur matrix and proves both `28 x 28` parity blocks positive via exact rational congruence and interval Gershgorin.

The retained bounds are approximately

```text
mu_56 > 0.7060951994695617
even margin > 0.003888027441177187
odd  margin > 0.004366893328949625.
```

## Independent verification

The closed v1 profile admits `(T,N)=(9/20,56)` explicitly. The retained full certificate returns

```text
passed=true
verified_scope=localized_weil_positivity_T_9_20.
```

Adversarial replay on the real certificate distinguishes:

- malformed contract data (`factor=2`) -> exit `2`;
- contract-valid positivity-breaking perturbation -> exit `1`;
- unchanged theorem certificate -> exit `0`.

## Evidence

- `A-20260826-001`
- `X-20260826-003`
- `computations/2026-08-26T190517Z-nine-twentieths-schur-certificate/data/certificate.json`
- `computations/2026-08-26T190517Z-nine-twentieths-schur-certificate/data/rust-verification.json`

Certificate SHA-256:

```text
98f2b839d7f52c971966e7f9da9ae4e318c30a491821ad86abee6411b51932e0
```

Rust replay SHA-256:

```text
e8f7b0b99e41687829da795582690af141e0c7fb833d273767b255bdc53180fe
```

## Limits

This is strict localized Weil positivity at one finite support value. It does not establish RH and must not be extrapolated to larger support values.
