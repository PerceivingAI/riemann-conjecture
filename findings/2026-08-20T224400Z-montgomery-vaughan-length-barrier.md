# Generic Dirichlet-polynomial mean values retain the exponential length barrier

- **Finding ID:** `F-20260820-025`
- **Created:** `2026-08-20T22:44:00Z`
- **Last updated:** `2026-08-20T22:44:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For a fixed-interior chirp cell centered at `u_0>0`, the Dirichlet-polynomial length is

```text
N=exp(4n u_0/A+o(n)).
```

The Montgomery-Vaughan mean-value theorem has a length term `O(N)`. Since the Laguerre prime-side frequency range is only polynomial in `n` and `sum |a_m|^2=exp(o(n))` for the half-weight localized coefficients, the resulting RMS scale is at best

```text
exp(2n u_0/A+o(n)),
```

with root base

```text
exp(2u_0/A)>1.
```

Thus the generic mean-value/large-sieve theorem does not remove the exponential obstruction.

## Evidence / derivation

Apply the classical mean-value scale

```text
integral_0^T |sum_(m<=N)a_m m^(-it)|^2 dt
= (T+O(N))sum |a_m|^2
```

with `T=exp(o(n))`, `N=exp(4nu_0/A+o(n))`, and `a_m=Lambda(m)m^(-1/2)W(...)`.

## Dependencies

- `A-20260820-006`
- `F-20260820-023`
- `F-20260820-024`
- `R-0020`
- `X-20260820-008`

## Significance for RH research

It rules out a generic one-dimensional Dirichlet-polynomial `L2` estimate as the missing theorem. Any successful mean-value argument must exploit additional arithmetic/bilinear structure beyond the classical length term.

## Limits

This does not rule out specialized prime-supported or bilinear estimates that genuinely beat the generic length barrier.

## Verification

Exponential-scale calculation checked symbolically and numerically in `X-008`.

## Timestamped addenda / corrections

None.
