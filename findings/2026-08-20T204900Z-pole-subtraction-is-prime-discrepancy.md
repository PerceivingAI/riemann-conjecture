# Pole subtraction is exactly a prime-counting discrepancy transform

- **Finding ID:** `F-20260820-007`
- **Created:** `2026-08-20T20:49:00Z`
- **Last updated:** `2026-08-20T20:49:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For fixed `s0>1`, `A=2s0-1`, `q=-s0/(s0-1)`, and

```text
f_n(x)=x^(-s0)L_(n-1)^(1)(A log x),
```

the pole-subtracted sequence satisfies the exact Stieltjes identity

```text
S_n
= A integral_[1,infinity) f_n(x) d(psi(x)-x).
```

The continuous density term is exactly

```text
A integral_1^infinity f_n(x) dx = 1-q^n.
```

## Evidence / derivation

The discrete part is the definition of `P_n`. For the continuous part, substitute `t=A log x`, set `p=(s0-1)/A`, and use the Laguerre generating function to obtain

```text
integral_0^infinity e^(-pt)L_(n-1)^(1)(t)dt
=1-[(p-1)/p]^n
=1-q^n.
```

## Dependencies

- `C-0005`
- `C-0006`
- `C-0009`
- `A-20260820-002`

## Significance for RH research

This identifies the remaining RH obstruction as the action of a specific oscillatory Laguerre kernel on the **prime-counting error measure** rather than on the full prime density. It is the correct starting point for integration-by-parts and oscillatory-cancellation analysis.

## Limits

No bound on the discrepancy transform is proved here. In particular, no RH-equivalent pointwise estimate for `psi(x)-x` may be inserted as an input.

## Verification

The Laplace/Laguerre coefficient extraction and Stieltjes decomposition were checked on `2026-08-20T20:49:00Z`.

## Timestamped addenda / corrections

None.
