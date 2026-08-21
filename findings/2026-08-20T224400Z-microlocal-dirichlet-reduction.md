# Microlocal Laguerre chirp reduces to a critical-half-weight prime Dirichlet polynomial

- **Finding ID:** `F-20260820-024`
- **Created:** `2026-08-20T22:44:00Z`
- **Last updated:** `2026-08-20T22:44:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

Fix `u_0` in a compact subinterval of `(0,1)`, set

```text
y_0=4n u_0/A,
X=exp(y_0),
gamma_0=A/2 sqrt((1-u_0)/u_0).
```

Then

```text
Phi_n''(y_0)
= -A^2/[16n u_0^(3/2)sqrt(1-u_0)].
```

Hence on a logarithmic window `|y-y_0|<=H=o(sqrt(n))`, the Laguerre phase linearizes with `o(1)` phase error, and one cosine branch reduces schematically to

```text
sum Lambda(m)m^(-1/2+i gamma_0)W((log m-y_0)/H)
- continuous density,
```

up to algebraic prefactors and controlled local phase/amplitude errors.

## Evidence / derivation

Differentiate the exact chirp from `C-0023` twice in `y=log x` and apply Taylor's theorem. The half-weight follows from `s0-A/2=1/2`.

## Dependencies

- `A-20260820-006`
- `C-0023`
- `R-0011`
- `R-0018`

## Significance for RH research

This identifies precisely which classical analytic-number-theory object a local chirp cell becomes: a smooth prime Dirichlet polynomial on the critical half-weight.

## Limits

The reduction is fixed-interior and microlocal. It does not justify bounding cells independently or summing the local asymptotic remainder over the full prime measure.

## Verification

Exact differentiation and scale diagnostics in `X-008`.

## Timestamped addenda / corrections

None.
