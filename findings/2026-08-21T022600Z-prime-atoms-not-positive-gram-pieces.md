# Generalized prime atoms are not positive Gram pieces

- **Finding ID:** `F-20260821-008`
- **Created:** `2026-08-21T02:26:00Z`
- **Last updated:** `2026-08-21T02:26:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For generalized Li coefficients at `s0>1`, one prime-power atom contributes

```text
-c_m B_n(x),
c_m=A Lambda(m)m^(-s0)>0,
B_n=L_(n-1)^(1)(x), B_0=0.
```

Its contribution to the natural Li Gram kernel is

```text
-c_m[B_j+B_k-B_|j-k|],
```

and in particular

```text
K_11^(m)=-2c_m<0.
```

Thus the prime side cannot be decomposed into PSD atoms in this natural moment basis.

## Dependencies

- `A-20260821-002`
- `C-0006`

## Significance for RH research

Any positivity proof must use compensation between prime terms and archimedean/pole terms rather than prime-by-prime squares.

## Limits

This rules out the natural atomwise Gram decomposition, not every conceivable nonlinear factorization.

## Verification

Exact first-diagonal calculation; sampled matrices checked in `X-20260821-002`.

## Timestamped addenda / corrections

None.
