# Exact-prime Legendre-Schur certificate at T=9/20

- **Computation ID:** `X-20260826-003`
- **Created:** `2026-08-26T19:05:17Z`
- **Last updated:** `2026-08-26T19:05:17Z`
- **Type:** `RIGOROUS FULL-TAIL ASSEMBLY / EXACT RATIONAL CERTIFICATE / INDEPENDENT VERIFIER`
- **Supports:** `A-20260826-001`, `F-20260826-004`, `C-0053`
- **Generator Git commit:** `1336bf9c06460d4c4e1fda5f1a37a1f511d1bd3e`
- **Generator working tree:** `dirty` (recorded explicitly in the certificate metadata)

## Objective

Test whether the exact-prime Legendre-Schur continuation mechanism remains rigorously positive at

```text
T=9/20=0.45,
N=56,
```

using the same analytic complement and component tail-Gram Schur reduction as `C-0050`, `C-0051`, and `C-0052`, while raising Arb precision enough to control the known high-degree monomial conditioning.

## Parameters

```text
support T       = 9/20
Legendre N      = 56
Arb precision   = 512 bits
residual order  = 32
matrix endpoints= 104-bit dyadic outward rounding
witness entries = 56-bit dyadic rationals
Schur factor    = 3
```

The v1 `exact_prime_legendre_schur` contract was extended only by the explicit pair `(T,N)=(9/20,56)`; it remains closed and does not admit arbitrary nearby supports.

## High-precision full-tail diagnostic

Command:

```text
python -m scripts.weil_support_continuation_scout --supports 9/20 --dimension 56 --prec 512 --output-json computations/2026-08-26T190517Z-nine-twentieths-schur-certificate/data/full-tail-T045-N56.json
```

The Arb/exact-polynomial assembly gives the midpoint diagnostics

```text
mu_56                              ~ 0.7060951994695617
finite A_56 min eigenvalue midpoint~ 1.6182468463299702e-5
Schur min eigenvalue midpoint      ~ 1.5010127025502423e-5
rho_R upper                        ~ 1.7986600484862887
residual remainder upper           ~ 9.744797596524764e-19
```

These eigenvalues are reconnaissance only. The theorem evidence is the exact rational certificate below.

## Generator-side exact candidate

Command:

```text
python -m scripts.weil_support_candidate_check --support 9/20 --dimension 56 --prec 512 --residual-order 32 --matrix-bits 104 --witness-bits 56 --output-json computations/2026-08-26T190517Z-nine-twentieths-schur-certificate/data/candidate-T045-N56.json
```

The exact rational candidate reports

```text
mu_56 > 0.7060951994695617
even Gershgorin margin > 0.003888027441177187
odd  Gershgorin margin > 0.004366893328949625
```

All three quantities are exact rationals in the retained artifact.

## Proof certificate

Command:

```text
python -m scripts.cert.exact_prime_schur_certificate --claim C-0053 --support 9/20 --dimension 56 --prec 512 --matrix-bits 104 --witness-bits 56 --output-json computations/2026-08-26T190517Z-nine-twentieths-schur-certificate/data/certificate.json
```

Rust replay:

```text
cargo run -q -p rh_cert -- verify --cert computations/2026-08-26T190517Z-nine-twentieths-schur-certificate/data/certificate.json --json
```

The independent verifier returns

```text
passed=true
verified_scope=localized_weil_positivity_T_9_20
dimension=56
support_T=9/20
```

Rust independently derives

```text
mu_56 = H_56 - c_T^hi - c_2^hi - rho_R^hi > 0,
S_56 = A_56 - (3/mu_56)(G_V+G_2+G_R),
```

extracts the two `28 x 28` parity blocks, applies the exact rational lower-triangular congruence witnesses, and proves strict interval Gershgorin positivity.

## Adversarial replay

The real certificate was mutated in two ways:

1. change the exact Schur factor from `3` to `2`: Rust rejects the certificate as a contract error (`exit 2`);
2. keep the contract valid but replace one diagonal interval by exact `-1`: Rust executes theorem verification and returns `passed=false` (`exit 1`).

The unchanged certificate returns `exit 0`. Temporary adversarial files were deleted after replay.

## Artifact hashes (SHA-256)

```text
0983d7ccce2a737e5438559d4ff5f2c0bd979152426c1a0077596dba68b6c894  data/full-tail-T045-N56.json
183ed24ce924ff5754fe77af2a61c7ead532326f370878c4c5951f28c1ca8026  data/candidate-T045-N56.json
98f2b839d7f52c971966e7f9da9ae4e318c30a491821ad86abee6411b51932e0  data/certificate.json
e8f7b0b99e41687829da795582690af141e0c7fb833d273767b255bdc53180fe  data/rust-verification.json
```

Relevant source hashes at the retained state:

```text
51bace1ded6eb111c99097beca9982730a19e31abc4f81337f781ae2c188f6a5  scripts/cert/legendre_schur.py
d81144b600079d436306362ce760d1558f82561df72403e3f39dd202e8ef2566  scripts/cert/exact_prime_schur_certificate.py
dfd7fa3a9d79f1282d030f4d28cd0678b0ea468695b592c2bac5298c8fcd55c6  scripts/cert/export_certificate.py
ce2a71cf8df163ea7e4c342291a11dd57502ce664f44b57114a2b1e02007448f  crates/rh_cert/src/cert.rs
f73becd47cda0a570d8d0f31bba9e81d0a944abce74eba24be2c49fcebeb4596  docs/contracts/rh-weil-certificate-v1.json
13a0a1edcab311b4657557bcb940943117901e779240a39fd62aad847537b41c  tests/test_exact_prime_schur_certificate.py
3579cb0ab3956a4a6d44cd928887c56ebfc77c7b95ca15e96fcc19d07f5eccce  crates/rh_cert/tests/test_exact_prime_schur.rs
```

## Conclusion

The independently verified exact certificate establishes strict localized Weil positivity at `T=9/20` under the same analytic Legendre-complement/Schur mechanism used at the earlier support values.

This is a finite-support theorem. It does not prove RH and does not imply positivity at any larger support without a fresh certificate.
