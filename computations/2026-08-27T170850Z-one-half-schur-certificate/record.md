# Exact-prime Legendre-Schur certificate at T=1/2

- **Computation ID:** `X-20260827-004`
- **Created:** `2026-08-27T17:08:50Z`
- **Last updated:** `2026-08-27T17:26:10Z`
- **Type:** `RIGOROUS FULL-TAIL ASSEMBLY / EXACT RATIONAL CERTIFICATE / INDEPENDENT VERIFIER`
- **Supports:** `A-20260826-001`, `F-20260827-002`, `C-0055`
- **Generator Git commit:** `79ec2ef357bbc5f34c140d1ecfcf1dd725a98949`
- **Generator working tree:** `dirty` (the explicit `(1/2,80)` closed-contract admission was present and is recorded in certificate metadata)

## Objective

The canonical pre-theorem continuation bundle at `T=1/2` isolated `N=80` after floating reconnaissance and rigorous precision screening, then confirmed the fixed exact candidate from 512 to 640 Arb bits. This theorem slice separately admits exactly

```text
(T,N)=(1/2,80)
```

to the closed v1 `exact_prime_legendre_schur` profile, generates a fresh certificate from scratch, and requires a fresh independent zero-float Rust PASS before theorem status is granted. The earlier pre-theorem bundle at `computations/2026-08-27T151517Z-t1-2-continuation/` remains separate and non-proof-bearing.

## Contract admission

The Python theorem exporter, Python semantic validator, JSON Schema, and Rust verifier were each extended only by `(1/2,80)`. The test-only admission corpus now contains six allowed pairs, the full `6 x 6` off-diagonal forbidden grid, and explicit outsiders including the rigorously negative historical `(1/2,76)` point.

Admission testing caught two independent stale closed-dimension guards before theorem generation: the JSON Schema's exact-prime dimension/harmonic-index enums and Rust's internal exact-prime dimension guard still stopped at `68`. Both were extended to `80`; mixed pairs remain rejected.

Focused admission checks pass:

```text
Python cross-layer admission consistency: 6/6 passed
Rust shared-corpus admission replay: PASS
Rust explicit (1/2,80) acceptance: PASS
Rust explicit (1/2,76) rejection: PASS
```

Admission by itself did not grant theorem status.

## Parameters

```text
support T        = 1/2
Legendre N       = 80
Arb precision    = 512 bits
residual order   = 32
matrix endpoints = 64-bit dyadic outward rounding
witness entries  = 32-bit dyadic rationals
Schur factor     = 3
```

The pre-theorem driver had already shown that the same 64-bit matrix / 32-bit witness candidate is unchanged when the underlying Arb assembly is sharpened from 512 to 640 bits: exact `mu`, even margin, and odd margin have zero relative change, raw Arb widths contract, and exact rounded widths do not increase.

## Fresh proof certificate

Command:

```text
uv run --locked python -m scripts.cert.exact_prime_schur_certificate \
  --claim C-0055 \
  --support 1/2 \
  --dimension 80 \
  --prec 512 \
  --matrix-bits 64 \
  --witness-bits 32 \
  --output-json computations/2026-08-27T170850Z-one-half-schur-certificate/data/certificate.json
```

The fresh assembly completed in about `169.6 s`. Python schema and semantic validation pass. The exact positive rational lower quantities have decimal values approximately

```text
mu_80       > 0.6983326376765460
even margin > 0.0006030229450313612
odd  margin > 0.002927388923852846.
```

The retained certificate contains no floating-point proof data.

## Independent Rust replay

Command:

```text
cargo run -q -p rh_cert -- verify \
  --cert computations/2026-08-27T170850Z-one-half-schur-certificate/data/certificate.json \
  --json
```

The current independent verifier completed in about `59.9 s` and returned

```text
passed=true
claim=C-0055
support_T=1/2
dimension=80
verified_scope=localized_weil_positivity_T_1_2
```

Rust independently derives

```text
mu_80 = H_80 - c_T^hi - c_2^hi - rho_R^hi > 0,
S_80 = A_80 - (3/mu_80)(G_V+G_2+G_R),
```

extracts the two `40 x 40` parity blocks, checks the exact lower-triangular witnesses for invertibility, forms exact interval congruences, and proves strict interval Gershgorin positivity. The exact Rust lower bounds are identical to the generator-side rational values stored in the certificate.

## Adversarial replay

Two temporary mutations of the real certificate were tested without modifying the retained artifact:

1. `factor=3 -> 2`: contract validation rejects the certificate with exit `2`;
2. replace the finite-matrix `(0,0)` interval by exact `-1`: the contract remains valid, theorem verification runs, and returns `passed=false`, exit `1`; the even block fails while the odd block remains positive.

The unchanged retained certificate returns exit `0` and `passed=true`.

## Retained-proof acceptance

The proof was explicitly added as `C-0055` / `X-20260827-004` to `computations/retained-proofs.json`. The manifest remains a closed whitelist; no computation-directory discovery or automatic promotion was introduced.

Fast retained-proof contract/adversarial tests pass `67/67`. Full `cargo test -p rh_cert` passes, including the 17-case exact-prime integration target, and strict `cargo clippy -p rh_cert --all-targets -- -D warnings` passes. The canonical retained-proof gate returns

```text
C-0050 HASH PASS VERIFY PASS T=7/20 N=32
C-0051 HASH PASS VERIFY PASS T=2/5 N=40
C-0052 HASH PASS VERIFY PASS T=17/40 N=48
C-0053 HASH PASS VERIFY PASS T=9/20 N=56
C-0054 HASH PASS VERIFY PASS T=19/40 N=68
C-0055 HASH PASS VERIFY PASS T=1/2 N=80
RETAINED PROOF CHAIN: PASS - 6/6
```

The Lean soundness layer was not changed in this slice and was not redundantly rebuilt; the theorem uses the same previously built generic exact interval/congruence/Gershgorin soundness layer.

## Artifact hashes (SHA-256)

```text
95dd6c7a497ad605ddc81129a774bade5fbbc769d0f6fdf29172b89da2a57a7d  data/certificate.json
7383c91f48ead83ac9268fcdb154f9372c45ac3510339b9eaac3bd6fd461322a  data/rust-verification.json
```

Relevant source hashes at the theorem state:

```text
57c9f0a4d81fc35837bb37bf3c870ec2c13d2d99f599cd54cc5fce0793b76956  scripts/cert/legendre_schur.py
26008bebd6f93fd6e5bcb132329b2cb0c8e885edfd8e7a8ee33437a3fd6395b4  scripts/cert/exact_prime_schur_certificate.py
e4d18982faf44eba549a948bc9ee78afb402aa8bf9dd7aa673c327f1471b7328  scripts/cert/export_certificate.py
6dbe5c30402ee0581593fd371c821ba9e27db2293b799d4288a076cd4489cf46  crates/rh_cert/src/cert.rs
fe973dfbcb3c07f1bd963272ef82bff326d05cb4fe3d605ca8e74320baaa2885  docs/contracts/rh-weil-certificate-v1.json
232b9fe64bc1de7cd21d39e80191ea82872d1eb7c5c6ef6e796a23ff5e4a134c  tests/data/exact-prime-admission-v1.json
b90f0a00346222e7473e2ce043e028464aa45d4fb74b08413b699fddc3c126fa  crates/rh_cert/tests/test_exact_prime_schur.rs
```

## Conclusion

The independently verified exact certificate establishes strict localized Weil positivity at `T=1/2` under the same exact-prime Legendre-complement/component-Gram Schur mechanism as `C-0050` through `C-0054`.

This establishes `F-20260827-002` / `C-0055`. It is a finite-support theorem at one fixed support value. It does not prove RH and does not imply positivity at larger support, especially across the later `p=3` structural threshold, without new work.
