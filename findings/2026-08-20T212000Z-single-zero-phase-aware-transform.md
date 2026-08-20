# Exact phase-aware transform of a single zero mode

- **Finding ID:** `F-20260820-015`
- **Created:** `2026-08-20T21:20:00Z`
- **Last updated:** `2026-08-20T21:20:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For any nontrivial zeta zero `rho`, fixed `s0>1`, `A=2s0-1`, and

```text
z_rho=(rho-s0)/(rho+s0-1),
```

the explicit-formula mode `E_rho(x)=-x^rho/rho` contributes to the generalized Laguerre discrepancy transform exactly

```text
S_(n,rho)=z_rho^(-n)-1.
```

Equivalently,

```text
-integral_0^infinity exp[-(s0-rho)t/A]
 L_(n-1)^(1)(t) dt
= z_rho^(-n)-1.
```

## Evidence / derivation

The Laguerre generating function gives, for `Re(p)>0`,

```text
integral_0^infinity e^(-pt)L_(n-1)^(1)(t)dt
=1-[(p-1)/p]^n.
```

For `p=(s0-rho)/A`, `(p-1)/p=z_rho^(-1)`.

## Dependencies

- `A-20260820-004`
- `C-0011`
- `R-0007`
- `X-20260820-006`

## Significance for RH research

The identity exposes the exact role of phase. On the critical line `|z_rho|=1`, while every right-of-line zero gives `|z_rho|^(-1)>1`. Absolute envelopes that discard `gamma=Im(rho)` can greatly overestimate the actual rate.

## Limits

This is an exact reformulation of the zero response, not a proof that all zeros lie on the critical line. Infinite zero sums still require the standard convergence conventions.

## Verification

Algebra checked directly. Numerical complex Simpson integration in `X-20260820-006` reproduces the exact value for synthetic complex modes over the retained finite tests.

## Timestamped addenda / corrections

None.
