# Finite multiplicative convolutions preserve rank-one Laguerre chirp geometry

- **Finding ID:** `F-20260821-001`
- **Created:** `2026-08-21T02:09:00Z`
- **Last updated:** `2026-08-21T02:09:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For any finite factorization `m=a_1...a_k`, with logarithmic variables `r_j=log a_j`, the Laguerre phase is

```text
F_k(r_1,...,r_k)=Phi_n(r_1+...+r_k).
```

Hence

```text
Hess F_k = Phi_n'' * 1 1^T
```

and has rank at most one. The `k-1` directions preserving the product are exactly phase-flat.

## Evidence / derivation

Differentiate the composite function directly. Every second partial derivative equals `Phi_n''`.

## Dependencies

- `A-20260821-001`
- `C-0023`
- `R-0021`

## Significance for RH research

Vaughan, Heath-Brown, and other finite multiplicative convolution identities add arithmetic variables but do not create new independent oscillatory directions in this phase.

## Limits

This does not rule out cancellation specific to the arithmetic convolution coefficients.

## Verification

Direct calculus; bilinear case numerically checked in `X-20260821-001`.

## Timestamped addenda / corrections

None.
