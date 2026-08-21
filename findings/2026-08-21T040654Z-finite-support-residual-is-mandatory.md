# The finite-support Weil residual kernel is mandatory

- **Finding ID:** `F-20260821-014`
- **Created:** `2026-08-21T04:06:54Z`
- **Last updated:** `2026-08-21T04:06:54Z`
- **Type:** `ESTABLISHED_THEOREM`
- **Status:** `VERIFIED`

## Statement

Suzuki's exact finite-support Weil quadratic form is not equal to only

```text
digamma Fourier multiplier - finite prime symbol.
```

It also contains a finite-support residual term involving the truncated `r_0''` / residual kernel. In Suzuki's scaled equation (4.5), this appears as

```text
-T * double_integral r''(T(x-y)) w(y)conj(w(x)) dxdy.
```

Any finite-dimensional computation that omits this term is not a computation of the full finite-support Weil form.

## Evidence

Suzuki `R-0028`, equations around (2.7) and (4.5), explicitly separates the digamma multiplier, prime symbol, and residual kernel.

## Consequence

An exploratory multiplier-plus-prime Galerkin scout created during `A-20260821-003` was discarded before registration after this normalization check.

## Dependencies

- `R-0028`
- `A-20260821-003`
