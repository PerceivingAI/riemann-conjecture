# Subexponential growth of the standard Li coefficients would imply RH

- **Finding ID:** `F-20260820-002`
- **Created:** `2026-08-20T20:37:00Z`
- **Last updated:** `2026-08-20T20:37:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

A proof that the standard Li coefficients satisfy

```text
lambda_n = exp(o(n))
```

would imply the Riemann Hypothesis. Consequently, any eventual polynomial upper bound on `|lambda_n|` would also imply RH.

## Evidence / derivation

Voros proves a large-`n` dichotomy for Li coefficients: under RH they have tame `n log n`-scale growth, while if RH is false the sequence has a non-tempered oscillatory form with exponentially growing amplitude. A subexponential bound rules out the latter alternative.

## Dependencies

- `C-0003`
- `A-20260820-001`
- `R-0003`

## Significance for RH research

The target need not initially be positivity of every Li coefficient. A sufficiently strong growth bound is already decisive, potentially allowing tools designed for cancellation rather than sign.

## Limits

This finding does not provide such a bound. It only identifies a sufficient target using an established asymptotic theorem.

## Verification

Checked against Voros's paper/preprint metadata and abstract on `2026-08-20T20:37:00Z`.

## Timestamped addenda / corrections

None.
