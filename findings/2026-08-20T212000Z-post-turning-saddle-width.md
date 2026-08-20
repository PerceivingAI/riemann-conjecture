# Post-turning saddle classification and width

- **Finding ID:** `F-20260820-013`
- **Created:** `2026-08-20T21:20:00Z`
- **Last updated:** `2026-08-20T21:20:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For fixed `s0>1`, `A=2s0-1`, the smooth-density maximum

```text
u_* = A^2/(A^2-1)
```

is separated from the Laguerre turning point `u=1` by the fixed distance `1/(A^2-1)`. The genuine Airy transition has width `O(n^(-2/3))` in `u`, so `u_*` is asymptotically a post-turning Laplace saddle rather than an Airy-transition point.

Its quadratic exponent is

```text
4n[Phi_A(u)-Phi_A(u_*)]
= -[(A^2-1)^2/(2A^3)] n (u-u_*)^2
  + O(n|u-u_*|^3).
```

Hence the natural saddle width is `O(n^(-1/2))` in `u`, `O(sqrt(n))` in `t`, with

```text
delta log x
~ 4 sqrt(2A n)/(A^2-1)
```

at the `e^(-1)` scale.

## Evidence / derivation

Differentiate the `A-003` exponent twice and substitute `u_*`. The Airy-transition width follows from the DLMF argument `nu^(2/3)zeta(u)` and the linear behavior of `zeta(u)` at the turning point.

## Dependencies

- `A-20260820-004`
- `C-0014`
- `R-0011`
- `X-20260820-005`

## Significance for RH research

This corrects the previous narrow "Airy-window" interpretation. The smooth-density saddle is useful asymptotically, but it is not the entire turning transition and, moreover, belongs to the density contribution already removed exactly in `A-002`.

## Limits

This finding describes the smooth-density envelope. It does not by itself localize the pole-subtracted discrepancy `S_n`.

## Verification

Algebra checked directly; numerical kernel scans at `s0=2,3,4` are consistent with the predicted curvature as `n` increases.

## Timestamped addenda / corrections

None.
