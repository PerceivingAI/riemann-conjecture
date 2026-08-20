# Exact uniform pre-turning stationary-frequency map

- **Finding ID:** `F-20260820-017`
- **Created:** `2026-08-20T22:15:00Z`
- **Last updated:** `2026-08-20T22:15:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For `L_(n-1)^(1)(4n*u)` in the fixed-interior pre-turning regime, define

```text
xi(u)=1/2[sqrt(u-u^2)+asin(sqrt(u))].
```

The leading Bessel phase is

```text
4n xi(u)-3pi/4,
```

and

```text
xi'(u)=1/2 sqrt((1-u)/u).
```

A Mellin mode of positive frequency `gamma` therefore has the unique stationary coordinate

```text
u_gamma=A^2/(A^2+4gamma^2),
A=2s0-1,
```

with

```text
t_gamma=4n u_gamma,
log x_gamma=4nA/(A^2+4gamma^2).
```

The inverse map is

```text
gamma=A/2 sqrt((1-u)/u).
```

## Evidence / derivation

DLMF 18.15.17-19 gives the uniform Laguerre Bessel expansion and the exact `xi(u)`. DLMF 10.17.2-3 gives the large-argument phase of `J_1`. Differentiating and solving the stationary equation is elementary algebra.

The old diagnostic `A^2/(4gamma^2)` equals the `gamma->infinity` / `u->0` asymptotic of the exact map.

## Dependencies

- `A-20260820-005`
- `R-0011`
- `R-0018`
- `X-20260820-007`

## Significance for RH research

The Laguerre kernel is now an explicit frequency-selective chirp rather than an unspecified oscillatory weight. Every positive zero height is matched to exactly one pre-turning location.

## Limits

The cosine form is uniform only on fixed interior `u` intervals after applying the large-argument Bessel asymptotic. The exact DLMF Bessel representation, rather than the cosine approximation, is needed near `u=0` for the joint high-frequency limit.

## Verification

Symbolic differentiation and algebra were checked with SymPy. Python/Hypothesis and Rust tests verify the map and its inverse numerically over broad parameter ranges. `X-007` checks the first eight numerically evaluated zero ordinates at three generalized centers.

## Timestamped addenda / corrections

None.
