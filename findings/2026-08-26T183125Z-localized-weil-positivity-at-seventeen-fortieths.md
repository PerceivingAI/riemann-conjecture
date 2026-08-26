# Strict localized Weil positivity at T=17/40

- **Finding ID:** `F-20260826-003`
- **Created:** `2026-08-26T18:31:25Z`
- **Last updated:** `2026-08-26T18:31:25Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For Suzuki's scaled localized Weil quadratic form at

```text
T=17/40=0.425,
```

including the exact `p=2` compressed-translation term and the mandatory finite-support residual kernel, one has

```text
Q_T(w) > 0
```

for every nonzero admissible localized test function `w`.

## Certificate architecture

The proof uses Legendre cutoff `N=48`. The exact-prime full-tail reduction gives

```text
C_48 >= mu_48 I
```

with

```text
mu_48 > 0.7326484380944506.
```

The factor-3 component-Gram Schur matrix

```text
S_48=A_48-(3/mu_48)(G_V+G_2+G_R)
```

is split into even and odd `24 x 24` parity blocks. The retained certificate supplies exact rational lower-triangular congruence witnesses, while the independent zero-float Rust verifier reconstructs `mu_48` and `S_48` from the serialized proof inputs and checks exact interval Gershgorin positivity after congruence.

The independently verified margins are approximately

```text
even > 0.0028958690673761525
odd  > 0.010715413283695166.
```

## Evidence

- `A-20260826-001`
- `X-20260826-002`
- `computations/2026-08-26T183125Z-seventeen-fortieths-schur-certificate/data/certificate.json`
- `computations/2026-08-26T183125Z-seventeen-fortieths-schur-certificate/data/rust-verification.json`
- `C-0045`, `C-0047`, `C-0048`
- pinned Suzuki source `R-0028`

## Independent checks

The real certificate returns `passed=true` with verifier scope `localized_weil_positivity_T_17_40`.

Adversarial replay distinguishes:

- malformed Schur factor: contract failure / exit `2`;
- contract-valid positivity-breaking finite matrix perturbation: theorem failure / exit `1`;
- retained certificate: PASS / exit `0`.

The certificate SHA-256 is

```text
6c74a386097bb30c2924f70d82e90d5ffc4d2dcb029543b7c973949948bdd325
```

and the retained Rust replay SHA-256 is

```text
0378e6419b322eca7fc077271b1694bcb43e916592969e26827387aa8489958c.
```

## Interpretation

This is the third independently verified point in the one-prime support continuation:

```text
T=7/20  -> N=32
T=2/5   -> N=40
T=17/40 -> N=48.
```

The required Legendre dimension is increasing with support, but the exact-prime Schur mechanism still works at `T=0.425`.

## Limits

This is a finite-support theorem at one fixed support value. It does not prove positivity throughout an interval, does not establish the next candidate `T=9/20`, and does not prove RH.
