# Strict first-prime localized Weil positivity at T=7/20

- **Finding ID:** `F-20260821-021`
- **Created:** `2026-08-21T13:52:37Z`
- **Last updated:** `2026-08-21T13:52:37Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For Suzuki's scaled localized Weil quadratic form at

```text
T=7/20,
```

including the exact `p=2` compressed-translation term and the mandatory finite-support residual kernel, the full quadratic form is strictly positive on its localized form domain.

Equivalently, with

```text
Q_T(w)=J(w)+V(w)+P_2(w)+R_T(w)-c_T||w||_2^2,
```

where the terms use the normalization fixed in `A-20260821-004` and `R-0028`, one has

```text
Q_T(w)>0
```

for every nonzero admissible `w`.

This is a finite-support Weil theorem at one support value. It does **not** prove RH.

## Proof architecture

Let `P_32` be projection onto Legendre modes `P_0,...,P_31` and `Q_32=I-P_32`.

1. `C-0045` gives the exact jump spectrum `J(P_n)=H_n||P_n||^2`.
2. The high-mode complement obeys

```text
C_32 >= mu_32 I,
mu_32=H_32-c_T-c_2-rho_R.
```

The retained exact rational certificate gives

```text
mu_32 >=
36248577317193051188471141673041
/
41621490368165930842884302438400

~ 0.8709101235096008 > 0.
```

3. By `C-0048`, it suffices to prove positivity of

```text
S_32=A_32-(3/mu_32)(G_V+G_2+G_R).
```

4. `scripts/cert/legendre_schur.py` constructs rigorous Arb enclosures for `A_32`, `G_V`, `G_2`, and `G_R` using exact rational polynomial algebra plus Arb enclosures of the transcendental constants. The residual operator uses the canonical Suzuki series with an order-32 exact-polynomial truncation and a rigorous remainder.
5. `scripts/cert/exact_prime_schur_certificate.py` outward-rounds the proof matrices to exact rational intervals and constructs exact dyadic rational congruence witnesses independently from the interval matrix midpoint by rational `LDL^T` algebra. Floating point has no proof authority.
6. `crates/rh_cert` independently derives the complement lower bound and Schur factor from the serialized intervals, reconstructs both parity blocks, applies the exact rational congruence witnesses, and proves strict positivity by exact rational interval Gershgorin margins.

The verifier returns the exact positive margins

```text
even:
17785254894936271196540587522097070225539421283851593653545177761745
/
1541843960876386629300146791416119282611162473685916984640787512819712
~ 0.01153505500311919

odd:
304608700982886967968984979448175382184720119319084245444424500463795
/
6167375843505546517200587165664477130444649894743667938563150051278848
~ 0.04939032559587724.
```

Both are strictly positive.

## Independent verifier and formal soundness

The retained certificate uses the closed profile

```text
exact_prime_legendre_schur
```

with proof rule

```text
legendre_component_gram_schur.
```

The Rust verifier accepts the clean-state certificate with `passed=true`. Adversarial checks performed during `A-004` distinguish:

- malformed Schur-factor semantics -> contract rejection / exit `2`;
- contract-valid loss of positivity -> theorem failure / exit `1`;
- the retained certificate -> PASS / exit `0`.

The Lean layer proves the finite-dimensional soundness needed by this judge: strict positive row Gershgorin dominance for a symmetric matrix implies positive definiteness, and invertible congruence transfers positive definiteness back to the original matrix. `lake build` completed successfully with `8711` jobs.

Lean does not formalize every analytic Arb enclosure end-to-end; the transcendental enclosure trust boundary remains python-flint/Arb, while Rust independently verifies the exact rational proof object exported from those enclosures.

## Dependencies

- `C-0039` — prime support/translation normalization;
- `C-0040` — exact first-prime shift norm;
- `C-0044` — mandatory Suzuki residual;
- `C-0045` — Legendre harmonic jump spectrum;
- `C-0047` — high-mode complement lower-bound method;
- `C-0048` — component tail-Gram Schur criterion;
- `R-0028` — authoritative Suzuki localized-form normalization;
- `R-0032`, `R-0033` — Legendre/Tuck identity inputs;
- `X-20260821-005` — retained clean certificate and independent replay.

## Significance for RH research

This independently establishes positivity beyond the first-prime support threshold at the specific support `T=0.35`. It validates the exact-prime Legendre-Schur continuation mechanism as a genuine finite-scale method rather than numerical reconnaissance.

The natural next question is continuation in `T` through the one-prime window toward

```text
(1/2) log 3,
```

where the second prime enters.

## Limits

- This proves one localized support value only.
- It does not prove positivity for every `T` in the first-prime window.
- It does not cross the `p=3` threshold.
- It does not imply the full Weil criterion and therefore does not imply RH.

## Verification artifacts

See `X-20260821-005` for exact reproduction commands, source hashes, certificate hash, verifier-output hash, and clean Git provenance.

## Timestamped addenda / corrections

None.
