# Moving Legendre dimension restores one-prime continuation through T=2/5

- **Finding ID:** `F-20260826-001`
- **Created:** `2026-08-26T17:14:00Z`
- **Last updated:** `2026-08-26T17:28:53Z`
- **Type:** `COMPUTATIONAL_OBSERVATION`
- **Status:** `PROVISIONAL`

## Statement

In the exact-prime Legendre-Schur continuation architecture, the fixed `N=32` full-tail Schur midpoint loses positivity between the tested supports `T=0.37` and `T=0.375` even though both the finite low block and the rigorous complement lower bound remain positive. Increasing the cutoff to `N=40` restores a positive full-tail midpoint Schur matrix at both `T=3/8` and `T=2/5`.

At `T=2/5,N=40`, a generator-side exact rational candidate check further gives strictly positive exact margins:

```text
mu_40 > 0.7313021813837909,
even congruence/Gershgorin margin > 0.004176569432300938,
odd  congruence/Gershgorin margin > 0.013120531611009081.
```

Thus `T=2/5,N=40` is selected as the next independent certificate target.

## Evidence

- `A-20260826-001`
- `X-20260826-001`
- `support-scan-fine.json`
- `full-tail-T0375-N40.json`
- `full-tail-T040-N40.json`
- `candidate-T040-N40.json`

## Interpretation

The first observed failure beyond `T=0.35` is not low-mode negativity or immediate loss of complement coercivity. It is insufficient full-tail Schur control at fixed dimension. A moving Legendre cutoff restores the mechanism at least through the `T=0.4` candidate.

Stable truncated-tail reconnaissance suggests the required dimension continues to grow with support: roughly `N~48` around `T=0.425` and `N~56` around `T=0.45`. Those later values are not rigorous full-tail certificates.

## Limits

This finding does **not** establish localized Weil positivity at `T=2/5`.

The `T=2/5,N=40` positive rational witness has been checked only on the generator side. The independent Rust certificate profile remains locked to `T=7/20,N=32`. Until the Rust verifier is extended under a closed contract and independently returns PASS, the new support value remains provisional.
