# Weil prime powers are thresholded compressed translations

- **Finding ID:** `F-20260821-009`
- **Created:** `2026-08-21T02:26:00Z`
- **Last updated:** `2026-08-21T02:26:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For logarithmic support `supp f subset [-T,T]`, the autocorrelation is supported in `[-2T,2T]`. Therefore prime power `m` enters the Weil form only after

```text
T>(1/2)log m.
```

Its quadratic contribution is the self-adjoint compressed-translation term

```text
-[Lambda(m)/sqrt(m)] P_T(U_(log m)+U_(log m)^*)P_T.
```

Thus fixed-support Weil positivity is an archimedean operator perturbed by finitely many explicit translations, with new arithmetic terms entering at discrete half-log prime-power thresholds.

## Dependencies

- `A-20260821-002`
- `R-0024`, `R-0025`

## Significance for RH research

Turns support continuation into a concrete operator perturbation problem rather than a global prime-cancellation estimate.

## Limits

Does not itself prove positivity after any prime threshold.

## Verification

Support geometry and correlation identity; threshold diagnostics in `X-20260821-002`.

## Timestamped addenda / corrections

None.
