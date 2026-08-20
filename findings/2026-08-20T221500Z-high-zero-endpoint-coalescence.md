# High zero frequencies coalesce with the pre-turning endpoint

- **Finding ID:** `F-20260820-021`
- **Created:** `2026-08-20T22:15:00Z`
- **Last updated:** `2026-08-20T22:15:00Z`
- **Type:** `OPEN_REQUIREMENT`
- **Status:** `VERIFIED`

## Statement

For the critical-line stationary point

```text
u_gamma=A^2/(A^2+4gamma^2),
```

the Gaussian stationary width satisfies

```text
sigma_u/u_gamma
= sqrt(2gamma/(A n)).
```

Also, as `gamma->infinity`,

```text
nu xi(u_gamma) ~ 2A n/gamma.
```

Thus fixed-interior, large-Bessel-argument stationary phase is uniform for fixed `gamma` and remains separated from the endpoint when `gamma=o(n)`, but it necessarily enters an endpoint/coalescing regime when `gamma` is of order `n`.

## Evidence / derivation

Use

```text
Psi_gamma''(u_gamma)
=(A^2+4gamma^2)^2/(8A^3gamma),
nu=4n,
```

and `sigma_u=[nu Psi_gamma''(u_gamma)]^(-1/2)`. Division by `u_gamma` gives the exact relative-width formula. The Bessel-argument asymptotic follows from `xi(u)~sqrt(u)` as `u->0` and `u_gamma~A^2/(4gamma^2)`.

## Dependencies

- `A-20260820-005`
- `F-20260820-017`
- `R-0011`
- `R-0018`

## Significance for RH research

The infinite zero spectrum cannot be represented rigorously by simply summing fixed-frequency stationary-phase formulas. High Mellin frequencies accumulate at `u=0`, exactly where the large-argument cosine reduction of the Bessel function stops being uniform.

## Limits

This identifies the transition but does not solve it. The DLMF Bessel representation itself remains uniform to the left endpoint and should be used in the next joint `n,gamma` analysis.

## Verification

The width formula was simplified algebraically. Direct numerical saddle-isolation experiments show the expected endpoint contamination at moderate `n`, but no quantitative numerical asymptotic from those experiments is promoted to a claim.

## Timestamped addenda / corrections

None.
