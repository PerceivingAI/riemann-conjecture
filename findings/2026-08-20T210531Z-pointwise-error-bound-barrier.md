# Pointwise prime-error bound barrier after pole subtraction

- **Finding ID:** `F-20260820-012`
- **Created:** `2026-08-20T21:05:31Z`
- **Last updated:** `2026-08-20T21:05:31Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

In the integration-by-parts representation of `S_n`, inserting an absolute pointwise estimate

```text
|psi(x)-x| <= C x^theta
```

with any fixed `theta>1/2` leaves a positive exponential factor in the uniform Laguerre/Airy regime and therefore cannot establish the required root-growth rate `<=1` by a direct absolute-value bound.

At the limiting square-root exponent one reaches RH-strength pointwise information.

## Significance for RH research

The next proof attempt must exploit signed/oscillatory or averaged cancellation specific to the Airy-window transform. Simply improving a classical pointwise PNT error exponent while remaining above `1/2` cannot finish this route.

## Limits

This does not rule out using pointwise estimates as auxiliary bounds outside the critical Airy window. It rules out their use as the sole global mechanism.

## Dependencies

- `F-20260820-009`
- `R-0011`
- `C-0004`
- `A-20260820-003`
