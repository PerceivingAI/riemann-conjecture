# Li sequence as a conditional-negative-definite exponent

- **Finding ID:** `F-20260821-007`
- **Created:** `2026-08-21T02:26:00Z`
- **Last updated:** `2026-08-21T02:26:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

Under RH, `psi(n)=lambda_|n|` is conditionally negative definite on `Z`. Hence for every `t>0`,

```text
exp[-t lambda_|n|]
```

is positive definite and is the Fourier sequence of a probability measure `mu_t` on the unit circle. These measures form a convolution semigroup.

Conversely conditional negative definiteness immediately forces every `lambda_n>=0`, so the property is equivalent to RH.

## Evidence / derivation

For zero-sum coefficients the constant term cancels and the quadratic form is minus a sum of absolute squares over the Cayley zero phases. Apply Schoenberg and Herglotz; test the converse with coefficients `(1,-1)`.

## Dependencies

- `A-20260821-002`
- `C-0001`
- `R-0026`

## Significance for RH research

Gives a harmonic-analysis/probability interpretation of the Li sequence but also closes it as an independent proof shortcut.

## Limits

No unconditional construction of the measures `mu_t` is obtained.

## Verification

Direct algebra; finite Schoenberg matrices checked in `X-20260821-002`.

## Timestamped addenda / corrections

None.
