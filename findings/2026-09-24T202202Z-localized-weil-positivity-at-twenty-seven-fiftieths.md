# Strict localized Weil positivity at T=27/50

- **Finding ID:** `F-20260924-001`
- **Created:** `2026-09-24T20:22:02Z`
- **Last updated:** `2026-09-24T21:34:11Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For Suzuki's scaled localized Weil quadratic form at

```text
T=27/50,
```

including the exact `p=2` compressed translation and mandatory finite-support residual kernel,

```text
Q_T(w) > 0
```

for every nonzero admissible localized test function `w`.

## Proof architecture

Historical pre-theorem continuation `X-20260923-001` isolated `N=104` as the first rigorous successful dimension after the p17 floating scout selected `N=100` but complete full-tail Arb screening rejected `N=100` as mathematically negative. The exact `N=104` pre-theorem candidate was stable under fixed-parameter 512-to-640-bit reassembly, but that computation stopped at the hard pre-theorem boundary.

A separate admission decision then added exactly `(T,N)=(27/50,104)` to the closed `exact_prime_legendre_schur` v1 theorem profile. Fresh proof-bearing `X-20260924-001` was generated from clean committed HEAD `86f5fd75360892d92cd584bc5f2eab0cae56851b`, descending from admission-freeze commit `f2d284fd85bee8995ef267450e4038768678c3a3`. Certificate metadata records `git_dirty=false`. The certificate was assembled from scratch at 512-bit Arb precision with residual order `32`, 64-bit outward dyadic matrix endpoints, 32-bit exact dyadic congruence witnesses, and exact Schur factor `3`.

The retained exact lower quantities correspond approximately to

```text
mu_104      > 0.6643369939721553
even margin > 0.0002388902594756742
odd  margin > 0.000779387887620489
```

and are positive as exact rationals in the retained verifier output.

## Independent verification

The zero-floating-point Rust verifier independently returns

```text
passed=true
verified_scope=localized_weil_positivity_T_27_50
dimension=104
support_T=27/50
```

and reconstructs the factor-3 Schur matrix from the certificate data. It proves both `52 x 52` parity blocks positive by exact rational congruence and interval Gershgorin.

Real-certificate adversarial replay on temporary copies distinguishes the trust boundaries:

- exact Schur factor `3 -> 2` -> contract rejection, exit `2`;
- mixed `(21/40,104)` and `(1/2,104)` pairs -> contract rejection, exit `2`;
- zero interval denominator -> contract rejection, exit `2`;
- missing generator `git_commit` -> contract rejection, exit `2`;
- missing matrix coordinate -> contract rejection, exit `2`;
- contract-valid exact `A(0,0)=-1` perturbation -> theorem failure, exit `1`, `passed=false`, with the even block failing while the odd block remains positive;
- unchanged certificate copy -> PASS, exit `0`.

The source certificate remained byte-identical after the attacks. The closed retained-proof audit then independently hash-checks and replays every registered theorem certificate and reports

```text
RETAINED PROOF CHAIN: PASS - 8/8
```

including `C-0057`.

Repository-wide closure subsequently passed the default Python suite (`554/554`), the explicit retained-artifact acceptance (`1/1`, requiring the full `8/8` replay), the complete `rh_cert` Rust tests, Rust format check, strict Clippy, and the authoritative Lean build (`8711 jobs`).

## Evidence

- active continuation attempt `A-20260826-001`;
- historical pre-theorem continuation `X-20260923-001`;
- proof-bearing theorem run `X-20260924-001`;
- `computations/2026-09-24T183715Z-t27-50-schur-certificate/data/certificate.json`;
- `computations/2026-09-24T183715Z-t27-50-schur-certificate/data/rust-verification.json`;
- `computations/retained-proofs.json`.

Certificate SHA-256:

```text
75187f3be283ca9596a714c4a12822c4c58cd4b33e7624110ff102d68c9aab3f
```

Rust replay SHA-256:

```text
e29e80bdb4af140db95934732095e45ce761ad82e6eb09b1bf8a5bd5931512ce
```

## Limits

This is strict localized Weil positivity at one finite support value. It does not establish RH and must not be extrapolated to larger supports. The point `T=27/50=0.54` remains below the structural threshold `(1/2)log 3 ≈ 0.5493`; entry of the `p=3` compressed translation remains a separate mathematical/tooling phase.
