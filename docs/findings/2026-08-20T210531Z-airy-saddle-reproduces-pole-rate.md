# Airy saddle reproduces the zeta-pole exponential rate

- **Finding ID:** `F-20260820-010`
- **Created:** `2026-08-20T21:05:31Z`
- **Last updated:** `2026-08-20T21:05:31Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For the smooth prime-density kernel

```text
D_n(t)=exp[-(s0-1)t/(2s0-1)] L_(n-1)^(1)(t),
```

set `A=2s0-1`, `nu=4n`, and `u=t/nu`. The DLMF uniform Airy exponent for `u>=1` has a unique maximum at

```text
u_* = A^2/(A^2-1).
```

At this saddle the exponential growth is exactly

```text
[s0/(s0-1)]^n = |q|^n,
q=-s0/(s0-1).
```

## Evidence / derivation

The Airy exponent is

```text
Phi_A(u)
= u/(2A)
  -(1/2)[sqrt(u^2-u)-arccosh(sqrt u)].
```

Differentiation gives `Phi_A'(u)=1/(2A)-(1/2)sqrt((u-1)/u)`, hence `u_*`. Substitution yields `Phi_A(u_*)=(1/2)artanh(1/A)`. Since `nu=4n`, `exp(nu Phi_A(u_*))=((A+1)/(A-1))^n=|q|^n`.

## Dependencies

- `R-0011`
- `C-0009`
- `A-20260820-003`
- computational cross-check: `X-20260820-002`

## Significance for RH research

This identifies the analytic origin of the deterministic pole mode found in `A-002`: the pole subtraction removes precisely the dominant exponential saddle of the smooth prime-density Laguerre transform.

## Limits

This does not estimate the remaining prime discrepancy. The Airy expansion controls the smooth kernel; the difficult object is its interaction with `psi(x)-x`.

## Verification

The predicted saddle was numerically approached from below at `s0=3` and `s0=4` through `n=256`; the proof is analytic and does not rely on those runs.
