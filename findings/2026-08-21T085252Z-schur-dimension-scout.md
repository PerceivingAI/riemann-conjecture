# Exact-prime Legendre-Schur dimension scout

- **Finding ID:** `F-20260821-020`
- **Created:** `2026-08-21T08:52:52Z`
- **Last updated:** `2026-08-21T08:56:20Z`
- **Type:** `COMPUTATIONAL_OBSERVATION`
- **Status:** `PROVISIONAL`

## Statement

Floating reconnaissance of the exact-prime Legendre reduction at `T=7/20` suggests that a rigorous factor-3 Schur certificate is plausibly obtainable at dimension around `N=28` or above; `N=32` is the recommended first rigorous target.

With component tail Grams truncated at mode `120`, the scout gives factor-3 Schur minimum eigenvalues approximately

```text
N=24  -0.4031
N=28  +0.0011708
N=32  +0.0011848
N=40  +0.0011896.
```

The 120-mode exact-prime finite Ritz matrix has a lowest sampled eigenvalue near `0.00119357`.

## Evidence / derivation

`scripts/weil_legendre_schur_scout.py` uses normalized Legendre polynomials, NumPy/SciPy floating point, Gauss-Legendre quadrature, the exact-prime overlap geometry, and the Suzuki residual closed formula.

## Dependencies

- `F-20260821-018` for the complement formula used as a scout input;
- `F-20260821-019` for the finite Schur reduction;
- `X-20260821-004`.

## Significance for RH research

The result selects a practical finite dimension for rigorous Arb assembly and suggests that the available margin is on the order of `10^-3`, so interval/tail estimates must be relatively sharp.

## Limits

This is **not a proof**. The tail Gram matrices are truncated at a finite `max_mode` and therefore underestimate the infinite tail. Floating quadrature and eigenvalues are used only for reconnaissance.

## Verification

The script labels its output `floating_reconnaissance_only` and records the truncation warning in the JSON artifact.

## Timestamped addenda / corrections

None.
