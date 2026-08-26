# Strict localized Weil positivity at T=2/5

- **Finding ID:** `F-20260826-002`
- **Created:** `2026-08-26T17:49:29Z`
- **Last updated:** `2026-08-26T17:49:29Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For Suzuki's scaled localized Weil quadratic form at

```text
T=2/5,
```

including the exact `p=2` compressed-translation term and the mandatory Suzuki residual kernel, one has

```text
Q_T(w) > 0
```

for every nonzero admissible localized test function `w`.

This extends the independently verified basepoint `C-0050` from `T=7/20` to `T=2/5`.

## Proof architecture

The proof uses the same analytic mechanism as `C-0050`, but with Legendre cutoff `N=40`:

```text
C_40 >= mu_40 I,
mu_40 = H_40 - c_T - c_2 - rho_R,
```

and the component tail-Gram Schur reduction

```text
S_40 = A_40 - (3/mu_40)(G_V + G_2 + G_R).
```

The rigorous Python/Arb generator encloses `A_40`, `G_V`, `G_2`, and `G_R`, outward-rounds them to exact dyadic rational intervals, and supplies exact rational lower-triangular congruence witnesses for the even and odd `20 x 20` parity blocks.

The independent zero-float Rust verifier does not trust a precomputed Schur matrix or eigenvalue. It independently:

1. validates the closed `(T,N)=(2/5,40)` whitelist entry;
2. derives `mu_40` from the serialized upper scalar endpoints;
3. requires `mu_40>0`;
4. reconstructs the exact interval factor-3 Schur matrix;
5. checks the exact rational parity witnesses for invertibility/lower-triangular structure;
6. recomputes both interval congruences; and
7. verifies strict positive Gershgorin lower margins.

The retained certificate gives

```text
mu_40 > 0.7313021813837909,
even Gershgorin margin > 0.004176569432300938,
odd  Gershgorin margin > 0.013120531611009081.
```

Rust returns

```text
passed = true
verified_scope = localized_weil_positivity_T_2_5
```

for the retained proof object.

## Adversarial replay

The retained real certificate was mutated in two ways:

- replacing the exact Schur factor `3` by `2` is rejected as a contract error, exit code `2`;
- replacing the `(0,0)` low-matrix interval by the exact value `-1` leaves the contract valid but destroys the even-block positivity margin, producing theorem failure, exit code `1`.

The unchanged theorem certificate exits `0`.

Thus the verifier distinguishes malformed proof objects from contract-valid false theorem instances for the new configuration.

## Provenance

The retained certificate records:

```text
git_commit = b5405a9347a8b6bc6d3a8c022c4e0fa60e425361
git_dirty  = true
```

The dirty flag is explicitly preserved in the proof artifact. Exact source/artifact hashes and reproduction commands are recorded in `X-20260826-001`.

Retained artifact hashes:

```text
8f9fa235beb9b4ee3c4f7cde11732a1b0b5295a7bbc94c03857417ee8a2b1be2  data/certificate-T040-N40.json
85900f61c8105a87a19b2dfe9c4863d14fc7fbf0cef609801e435fdb0b296891  data/rust-verification-T040-N40.json
```

## Dependencies

- `C-0039` — prime powers are thresholded compressed translations;
- `C-0040` — first-prime compressed-shift geometry;
- `C-0044` — Suzuki residual kernel is mandatory;
- `C-0045` — Legendre jump spectrum / harmonic coercivity;
- `C-0047` — exact-prime complement lower-bound mechanism;
- `C-0048` — component tail-Gram Schur reduction;
- `A-20260826-001`, `X-20260826-001`.

`C-0050` is the historical verified basepoint and trust-architecture precedent, but its positivity statement is not a mathematical dependency of the `T=2/5` proof.

## Scope / circularity guard

This is a finite-support theorem at one additional support value. It does **not** prove positivity for every support, does not cross the `p=3` threshold, and does not prove RH.

No RH assumption is used in the proof. The next continuation values remain independent research targets.