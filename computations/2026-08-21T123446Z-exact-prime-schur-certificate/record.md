# Exact-prime N=32 Legendre-Schur certificate

- **Computation ID:** `X-20260821-005`
- **Created:** `2026-08-21T12:34:46Z`
- **Last updated:** `2026-08-21T13:52:37Z`
- **Status:** `VERIFIED CERTIFICATE`
- **Supports:** `A-20260821-004`, `F-20260821-021`, `C-0050`

## Objective

Produce and independently verify an exact rational interval certificate proving strict positivity of Suzuki's localized first-prime Weil quadratic form at

```text
T=7/20
```

using the rigorous `N=32` Legendre-Schur reduction from `A-20260821-004`.

## Environment and clean provenance

The retained certificate was regenerated from a clean working tree at

```text
git commit: d620aa649a2d0291e407d4c0c8bc7360b67efc38
git_dirty: false
```

The generator records CPython/python-flint/FLINT metadata inside `data/certificate.json`.

Proof calculation boundaries:

```text
exact polynomial algebra -> fractions.Fraction
transcendental enclosures -> python-flint Arb/Acb
serialized proof data -> exact rational intervals
independent proof judge -> pure-Rust BigRational
formal judge semantics -> Lean 4 + Mathlib
```

No ordinary floating-point value is used as a proof premise or certificate entry.

## Parameters

```text
support T        = 7/20
dimension N      = 32
basis            = Legendre P_0,...,P_31 on [-1,1]
parity           = even + odd
Arb precision    = 160 bits
residual order   = 32
matrix grid      = outward dyadic 2^-64
witness grid     = dyadic 2^-32
Schur factor     = 3/mu_32
certificate      = rh-weil-certificate-v1
claim profile    = exact_prime_legendre_schur
proof rule       = legendre_component_gram_schur
```

## Rigorous assembly

The low block `A_32` retains:

- exact Legendre jump diagonal;
- endpoint potential `V`;
- exact `p=2` compressed translation;
- Suzuki residual `R_T`;
- exact `c_T` interval.

The component cross-tail Grams are enclosed as

```text
G_V=P_32 V Q_32 V P_32,
G_2=P_32 P_2 Q_32 P_2 P_32,
G_R=P_32 R_T Q_32 R_T P_32.
```

`G_V` is reduced to exact logarithmic moments, `G_2` to exact shifted-polynomial edge overlaps, and `G_R` to an exact polynomial residual truncation plus a rigorous analytic remainder.

The complement lower bound used by the verifier is

```text
mu_32=H_32-c_T^hi-c_2^hi-rho_R^hi
```

with exact lower value

```text
36248577317193051188471141673041
/
41621490368165930842884302438400
~ 0.8709101235096008.
```

The verifier forms

```text
S_32=A_32-(3/mu_32)(G_V+G_2+G_R).
```

Parity makes the matrix exactly block diagonal. Each `16 x 16` parity block is transformed by an exact rational lower-triangular invertible congruence witness. Rust recomputes the congruence using exact rational interval arithmetic and applies strict Gershgorin dominance.

## Reproduction

Generate the certificate:

```text
.venv\Scripts\python.exe -m scripts.cert.exact_prime_schur_certificate \
  --claim C-0050 \
  --prec 160 \
  --matrix-bits 64 \
  --witness-bits 32 \
  --output-json computations\2026-08-21T123446Z-exact-prime-schur-certificate\data\certificate.json
```

Independent Rust replay:

```text
cargo run -q -p rh_cert -- verify \
  --cert computations\2026-08-21T123446Z-exact-prime-schur-certificate\data\certificate.json \
  --json
```

Formal soundness build:

```text
cd formal
lake build
```

## Retained result

Rust returns

```text
passed=true
verified_scope=localized_weil_positivity_T_7_20
support_T=7/20
dimension=32
```

with

```text
mu_32 lower
= 36248577317193051188471141673041
  /41621490368165930842884302438400
~ 0.8709101235096008

even Gershgorin margin
= 17785254894936271196540587522097070225539421283851593653545177761745
  /1541843960876386629300146791416119282611162473685916984640787512819712
~ 0.01153505500311919

odd Gershgorin margin
= 304608700982886967968984979448175382184720119319084245444424500463795
  /6167375843505546517200587165664477130444649894743667938563150051278848
~ 0.04939032559587724.
```

Both parity margins are strictly positive.

`lake build` subsequently completed successfully:

```text
Built Cert.Gershgorin
Built Cert
Build completed successfully (8711 jobs).
```

## Retained artifact hashes and generation-source hashes

The two `data/` hashes are the retained clean certificate/replay artifacts. The source hashes below identify the exact clean generation state at commit `d620aa649a2d0291e407d4c0c8bc7360b67efc38`; later documentation-only edits do not retroactively change the source state used by this computation.

SHA-256:

```text
99ed74cc8fdb96ae0e5db1b2dea60da65052d96bc670df5b69d94a47d99c1255  data/certificate.json
d5cd0f8a2787061f19d4f23d2c2344506f324e4f3c57c46f8d755b4255483103  data/rust-verification.json
5b2b22857dca1de40f0a63d106f5d03de63682c124dc51239bb9dacdfdbb4cab  scripts/cert/exact_prime_schur_certificate.py
ad82412d5cf88cd822d204077ed8989c87dc0cc1a5f770506ea927a4be240ee4  scripts/cert/legendre_schur.py
fdf81ec111967dca038b5f7bff02a8780ffe43089e8d1eb04dabcc34257d6e4f  crates/rh_cert/src/cert.rs
dfccb8cb69264688652d7eb53d2bd62c240e9cc1f5e5502efda16f0e9408ef8f  crates/rh_cert/src/gershgorin.rs
dcb72c5ab401ba9434704115648264dc411f4cb763b9f64df55b160da845816f  formal/Cert/Gershgorin.lean
8517ddfcd634dd8220db19e9923579e10bfc1114313a32c74ca7c87f2f6fa399  docs/contracts/rh-weil-certificate-v1.json
```

## Adversarial checks

During verifier integration the real certificate was mutated in two materially different ways:

1. changing the locked factor from `3` to `2` was rejected as a certificate-contract error with exit code `2`;
2. changing a low-block entry enough to destroy positivity while preserving contract validity returned theorem failure with exit code `1`.

The retained certificate returns exit code `0`.

These adversarial temporary files were not retained as theorem artifacts.

## Interpretation

This computation is proof-bearing for the finite-support result `C-0050` because:

- every serialized matrix/witness datum is exact rational data enclosing a rigorously generated Arb quantity;
- the independent Rust verifier reconstructs the Schur matrix rather than trusting a serialized PASS bit or precomputed eigenvalue;
- the positivity judge uses exact rational interval arithmetic;
- the infinite-dimensional complement is encoded through the proved Legendre coercivity/Schur theorem, not a finite-tail truncation;
- the relevant Gershgorin/congruence soundness theorem is separately formalized in Lean.

The result is **not** a proof of RH. It proves the localized Weil form only at `T=7/20`.

## Files

```text
data/certificate.json
data/rust-verification.json
```

No plots are needed for this certificate.

## Limitations / next use

The certificate is locked to the exact theorem semantics at `T=7/20`, `N=32`. A continuation proof at another support value must regenerate the analytic enclosures and cannot inherit this PASS automatically.

The natural next research task is to study continuation in `T` through the one-prime window toward `(1/2)log 3` and determine where the exact-prime Schur mechanism loses certified margin.
