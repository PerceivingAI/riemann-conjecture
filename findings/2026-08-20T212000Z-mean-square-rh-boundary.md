# Dyadic mean-square control already detects the RH boundary

- **Finding ID:** `F-20260820-016`
- **Created:** `2026-08-20T21:20:00Z`
- **Last updated:** `2026-08-20T21:20:00Z`
- **Type:** `ESTABLISHED_THEOREM`
- **Status:** `VERIFIED`

## Statement

Let

```text
Theta=sup{Re(rho): zeta(rho)=0}.
```

Zhao (2025), Lemma 8, records:

```text
Theta=1/2
=> integral_X^(2X) (psi(x)-x)^2 dx asymp X^2;

Theta>1/2
=> X^(2Theta+1-epsilon)
   << integral_X^(2X) (psi(x)-x)^2 dx
   << X^(2Theta+1).
```

Consequently, a generic estimate

```text
integral_X^(2X)(psi(x)-x)^2 dx
<<_epsilon X^(2+epsilon)
```

for every `epsilon>0` would force `Theta=1/2`, hence RH.

## Evidence / derivation

This is cited from Zhao's open-access Research in Number Theory paper, DOI `10.1007/s40993-025-00640-y`, Lemma 8. Choose `epsilon<2Theta-1` in the lower bound if `Theta>1/2` to contradict an `X^(2+epsilon)`-scale upper bound.

## Dependencies

- `R-0014`
- `A-20260820-004`

## Significance for RH research

It blocks a tempting shortcut: using an RH-scale dyadic mean-square estimate for `psi-x` inside Cauchy-Schwarz is not an independent averaging theorem; it already rules out zeros to the right of the critical line.

## Limits

This does not rule out every transform-specific averaged estimate. It rules out importing a generic square-root-scale dyadic `L^2` bound as if it were substantially weaker than RH.

## Verification

The cited lemma and its two cases were checked directly in the published article.

## Timestamped addenda / corrections

None.
