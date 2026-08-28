# Exact-prime Legendre-Schur certificate at T=21/40

- **Computation ID:** `X-20260828-001`
- **Created:** `2026-08-28T01:08:11Z`
- **Last updated:** `2026-08-28T01:25:03Z`
- **Type:** `RIGOROUS FULL-TAIL ASSEMBLY / EXACT RATIONAL CERTIFICATE / INDEPENDENT VERIFIER`
- **Supports:** `A-20260826-001`, `F-20260828-001`, `C-0056`
- **Generator Git commit:** `dc8b63c8d47a983d290d6b1ba3d05a621d1d830b`
- **Generator working tree:** `dirty` (the explicit `(21/40,96)` closed-contract admission was present and is recorded in certificate metadata)

## Objective

The historical pre-theorem continuation `X-20260827-005` isolated the smallest successful exact candidate `(T,N)=(21/40,96)` and confirmed it from 512 to 640 Arb bits. This theorem slice separately admits exactly

```text
(T,N)=(21/40,96)
```

to the closed v1 `exact_prime_legendre_schur` profile, generates a fresh certificate from scratch, and requires a fresh independent zero-float Rust PASS before theorem status is granted. The earlier continuation bundle remains separate and non-proof-bearing.

## Contract admission

The Python theorem generator, Python semantic validator, JSON Schema, and Rust verifier were each extended only by `(21/40,96)`. The test-only admission corpus contains seven allowed pairs, the full `7 x 7` off-diagonal forbidden grid, and selected outsiders including `(21/40,92)` and `(21/40,100)`. Thus the larger generator-side `N=100` candidate remains deliberately unadmitted.

Admission testing caught two stale independent guards before theorem generation: the JSON Schema exact-prime dimension/harmonic-index enums and Rust's internal exact-prime dimension guard still stopped at `80`. Both were extended to `96`; mixed pairs remain rejected.

Focused admission checks pass:

```text
Python cross-layer admission consistency: 6/6 passed
Rust shared-corpus admission replay: PASS
Rust explicit (21/40,96) acceptance: PASS
Rust explicit (21/40,100) rejection: PASS
```

Admission by itself did not grant theorem status.

## Parameters

```text
support T        = 21/40
Legendre N       = 96
Arb precision    = 512 bits
residual order   = 32
matrix endpoints = 64-bit dyadic outward rounding
witness entries  = 32-bit dyadic rationals
Schur factor     = 3
```

The pre-theorem driver had already shown that the same 64-bit matrix / 32-bit witness candidate is unchanged when the underlying Arb assembly is sharpened from 512 to 640 bits.

## Fresh proof certificate

Command:

```text
uv run --locked python -m scripts.cert.exact_prime_schur_certificate \
  --claim C-0056 \
  --support 21/40 \
  --dimension 96 \
  --prec 512 \
  --matrix-bits 64 \
  --witness-bits 32 \
  --output-json computations/2026-08-28T010811Z-t21-40-schur-certificate/data/certificate.json
```

The fresh assembly completed in about `349.8 s`. Python schema and semantic validation pass. Its exact rational quantities reproduce the pre-theorem candidate exactly and correspond approximately to

```text
mu_96       > 0.69600913384063989
even margin > 0.00090134267068206139
odd  margin > 0.0037494074424420441.
```

The certificate contains no floating-point proof data.

## Independent Rust replay

Command:

```text
cargo run -q -p rh_cert -- verify \
  --cert computations/2026-08-28T010811Z-t21-40-schur-certificate/data/certificate.json \
  --json
```

The independent verifier completed in about `105.9 s` and returned

```text
passed=true
claim=C-0056
support_T=21/40
dimension=96
verified_scope=localized_weil_positivity_T_21_40.
```

Rust independently derives `mu_96>0`, reconstructs the factor-3 Schur matrix, checks exact lower-triangular witnesses, and proves both `48 x 48` parity blocks positive by exact rational interval congruence and Gershgorin. The exact Rust lower bounds agree with the generator values stored in the certificate.

## Adversarial replay

Two temporary mutations of the real certificate were tested without modifying the retained artifact:

1. `factor=3 -> 2`: contract validation rejects the certificate with exit `2`;
2. replace the finite-matrix `(0,0)` interval by exact `-1`: the contract remains valid, theorem verification runs, and returns `passed=false`, exit `1`; the even block fails while the odd block remains positive.

The unchanged theorem certificate returns exit `0` and `passed=true`.

## Retained-proof acceptance

The proof was explicitly registered as `C-0056` / `X-20260828-001` in `computations/retained-proofs.json`. No automatic computation discovery or theorem promotion was introduced.

Focused retained-proof unit tests pass `67/67`, the complete exact-prime Rust integration target passes `19/19`, and strict `cargo clippy -p rh_cert --all-targets -- -D warnings` passes. The canonical retained-proof gate completed in about `236.9 s` and returns

```text
C-0050 HASH PASS VERIFY PASS T=7/20 N=32
C-0051 HASH PASS VERIFY PASS T=2/5 N=40
C-0052 HASH PASS VERIFY PASS T=17/40 N=48
C-0053 HASH PASS VERIFY PASS T=9/20 N=56
C-0054 HASH PASS VERIFY PASS T=19/40 N=68
C-0055 HASH PASS VERIFY PASS T=1/2 N=80
C-0056 HASH PASS VERIFY PASS T=21/40 N=96
RETAINED PROOF CHAIN: PASS - 7/7
```

The Lean soundness layer was not changed in this slice and was not redundantly rebuilt; `C-0056` uses the same previously built generic exact interval/congruence/Gershgorin soundness layer.

## Artifact hashes (SHA-256)

```text
a455dcb995a56f6d387e79b199cfc6f18ba6fca108fcfe3c00987e1c47b44824  data/certificate.json
9530b53b00c1e96a1be82b2127adc7d1424e63af444803f169be8434f51d2e83  data/rust-verification.json
```

Relevant source hashes at the theorem state:

```text
57c9f0a4d81fc35837bb37bf3c870ec2c13d2d99f599cd54cc5fce0793b76956  scripts/cert/legendre_schur.py
83f10c19f49d0709d5f5e357799123ddd3ccca4675557d96369a170533b7e653  scripts/cert/exact_prime_schur_certificate.py
c75ff232f85ba9b7d27ea7c8fc63becf6d30eb2032872d63405cf277ef45feb3  scripts/cert/export_certificate.py
6306c53dc933d1393c6dcb467f82b88e8d4da78558867065256b5251bcc5c7eb  crates/rh_cert/src/cert.rs
7a6d1812c365ae58fdac93e5277adb1d7477a5ebb0b6c6bbd095f2c1c635d6ca  docs/contracts/rh-weil-certificate-v1.json
8b9f17a6eb3adea664f3a0fefd6ae75a4e14575ba209fe68ca64fad4840cc62d  tests/data/exact-prime-admission-v1.json
46c0f849f39e27acaf372db0dab6dc798a3772f2de50e77f48e7b64bd44ad9a8  crates/rh_cert/tests/test_exact_prime_schur.rs
5356b959391427a6817ae937d06678554f2761d825ea80fc23890ea9f5d37ac3  computations/retained-proofs.json
4900a4ea4bdb191608d84817af5aae912e5931d5bae82af6159e45c0279d4d89  scripts/cert/verify_retained_proofs.py
```

## Conclusion

The independently verified exact certificate establishes strict localized Weil positivity at `T=21/40` under the existing one-prime Legendre-complement/component-Gram Schur mechanism. This establishes `F-20260828-001` / `C-0056`.

This is a finite-support theorem at one fixed support value. It does not prove RH and does not imply positivity at larger support. The `p=3` compressed-translation threshold `(1/2)log 3` has not been crossed.
