# Exact-prime Legendre-Schur certificate at T=19/40

- **Computation ID:** `X-20260827-002`
- **Created:** `2026-08-27T12:27:16Z`
- **Last updated:** `2026-08-27T13:16:15Z`
- **Type:** `RIGOROUS FULL-TAIL ASSEMBLY / EXACT RATIONAL CERTIFICATE / INDEPENDENT VERIFIER`
- **Supports:** `A-20260826-001`, `F-20260827-001`, `C-0054`
- **Generator Git commit:** `1377e9e6c1a2ec4d6d1d91c677d51a4643b1e40a`
- **Generator working tree:** `dirty` (the explicit `(19/40,68)` closed-contract admission was present and is recorded in certificate metadata)

## Objective

After the canonical continuation driver reached generator-side `CANDIDATE_READY` at

```text
T=19/40=0.475,
N=68,
```

admit exactly that support/dimension pair to the closed v1 `exact_prime_legendre_schur` theorem contract, generate a fresh proof certificate from the admitted configuration, and require a fresh independent zero-float Rust replay before theorem status is granted.

The earlier pre-theorem continuation bundle remains `X-20260827-001`. This record is a separate theorem-certificate run and does not relabel or mutate the candidate bundle.

## Contract admission

The v1 whitelist was extended only by

```text
(T,N)=(19/40,68).
```

The Python exporter/semantic validator, JSON Schema, and Rust verifier all remain closed and enumerated. Mixed pairs such as `(19/40,64)` remain invalid. During admission testing, two independent stale dimension guards were discovered and corrected: the JSON Schema's shared exact-prime dimension/harmonic-index enums and Rust's internal exact-prime dimension guard had still stopped at `56` even after the pair-specific whitelist entry was added.

Admission by itself did not grant theorem status. Promotion occurred only after the fresh certificate and independent replay below passed.

## Parameters

```text
support T        = 19/40
Legendre N       = 68
Arb precision    = 384 bits
residual order   = 32
matrix endpoints = 64-bit dyadic outward rounding
witness entries  = 32-bit dyadic rationals
Schur factor     = 3
```

These are the first exact settings that succeeded in the retained pre-theorem candidate, but the theorem exporter reassembled the analytic matrices from scratch under the admitted contract.

## Fresh proof certificate

Command:

```text
uv run --locked python -m scripts.cert.exact_prime_schur_certificate \
  --claim C-0054 \
  --support 19/40 \
  --dimension 68 \
  --prec 384 \
  --matrix-bits 64 \
  --witness-bits 32 \
  --output-json computations/2026-08-27T122716Z-nineteen-fortieths-schur-certificate/data/certificate.json
```

The generator completed successfully and reported exact positive rational bounds whose decimal values are approximately

```text
mu_68       > 0.7185353202932019
even margin > 0.0013831260220094517
odd  margin > 0.006360318287493695.
```

The retained certificate contains no floating-point proof data.

## Independent Rust replay

Command:

```text
cargo run -q -p rh_cert -- verify \
  --cert computations/2026-08-27T122716Z-nineteen-fortieths-schur-certificate/data/certificate.json \
  --json
```

The independent verifier returns

```text
passed=true
verified_scope=localized_weil_positivity_T_19_40
dimension=68
support_T=19/40
```

Rust independently derives

```text
mu_68 = H_68 - c_T^hi - c_2^hi - rho_R^hi > 0,
S_68 = A_68 - (3/mu_68)(G_V+G_2+G_R),
```

extracts the two `34 x 34` parity blocks, checks the exact lower-triangular witnesses for invertibility, forms the exact interval congruences, and proves strict interval Gershgorin positivity.

The retained exact lower bounds are

```text
mu_68 = 75949417291518920670190058491167918952198873
        /105700325574151851532435390945980102528204800

even margin = 1117057850372388075128957361710227887697811374514782267229023862347982647851921
              /807632733819503428775270872893934384774524214553861762398712559399199498550902784

odd margin  = 41094409971925720619346370628227586741605266848311404583907753226061501104844857
              /6461061870556027430202166983151475078196193716430894099189700475193595988407222272
```

## Adversarial replay

The real certificate was replayed with two temporary mutations, then the temporary files were deleted:

1. change the exact Schur factor from `3` to `2`; Rust rejects the certificate during contract validation with exit `2`;
2. keep the contract valid but replace the `(0,0)` finite-matrix interval by exact `-1`; Rust executes theorem verification and returns `passed=false`, exit `1`. The even Gershgorin margin becomes negative while the odd block remains positive.

The unchanged retained theorem certificate returns exit `0` and `passed=true`.

## Regression and trust-chain verification

After admission and certificate generation:

```text
uv run --locked --extra test python -m pytest -q
    409 passed, 2 deselected in 557.76s

uv run --locked --extra test python -m pytest -q -m slow_acceptance \
  tests/test_exact_prime_schur_certificate.py::test_exact_prime_certificate_accepts_nineteen_fortieths_dimension_68
    1 passed in 111.20s

cargo test -p rh_cert --quiet
    all targets passed; exact-prime integration target 14/14 passed

cargo clippy -p rh_cert --all-targets -- -D warnings
    passed

cd formal && lake build
    Build completed successfully (8711 jobs)
```

The default Python suite deliberately deselects the two slow-acceptance tests; the new real `N=68` slow-acceptance generator test was run separately and passed.

## Artifact hashes (SHA-256)

```text
d9ba45f0026de31ded30ab3a08cd8272982424368c63426131cd08428aab8ac5  data/certificate.json
43445444b898c1b9f9dcf88a6df458cdd6e9baeef0417cddbec7490308b358f0  data/rust-verification.json
```

Relevant source hashes at the retained theorem state:

```text
57c9f0a4d81fc35837bb37bf3c870ec2c13d2d99f599cd54cc5fce0793b76956  scripts/cert/legendre_schur.py
7d38a29610d1033d75a23eca36feb07a589e50e20c558bb1a805bf01422f66b4  scripts/cert/exact_prime_schur_certificate.py
a56579ce6bf35f5f866024452c1c3cc36393e06781929c8b19eb32d5bd5f82fc  scripts/cert/export_certificate.py
c2b6c5dd3a4fac6347fe00937dad3d72dcf2b22574dc45e628a98515c16a0637  crates/rh_cert/src/cert.rs
8e783bd748a653c641b33b5d381c0588588795759e74b6410f3e7292e29f699c  docs/contracts/rh-weil-certificate-v1.json
98e7236b455b250c1b3b2e3fec373f9a5b81fd93a2d99b14f87d79292d370c15  tests/test_exact_prime_schur_certificate.py
826102a723a5a4bb6dac8251aefd1359be2da5e88cee7400308e4e20b129c4e4  crates/rh_cert/tests/test_exact_prime_schur.rs
```

The theorem certificate is about 3.9 MB. It is retained because it is a proof artifact required for independent replay, not a disposable raw dataset; the documentation protocol now states this distinction explicitly.

## Conclusion

The independently verified exact certificate establishes strict localized Weil positivity at `T=19/40` under the same analytic exact-prime Legendre-complement/component-Gram Schur mechanism used for `C-0050` through `C-0053`.

This establishes `F-20260827-001` / `C-0054`. It is a finite-support theorem at one fixed support value. It does not prove RH and does not imply positivity at any larger support without a fresh admitted certificate.
