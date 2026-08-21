# Exact-prime Legendre complement is rigorously coercive from finite mode

- **Finding ID:** `F-20260821-018`
- **Created:** `2026-08-21T08:52:52Z`
- **Last updated:** `2026-08-21T08:56:20Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For the exact first-prime localized Weil form at `T=7/20`, let `Q_N` project onto Legendre modes `n>=N`. Then

```text
Q_T(q)>=mu_N ||q||^2
```

for `q` in the complement, with

```text
mu_N=H_N-c_T-c_2-rho_R,
rho_R=2T sup_{|u|<=2T}|r''(u)|.
```

The proof-path certificate gives a rigorous residual bound and verifies

```text
mu_14>0.
```

## Evidence / derivation

- `J(q)>=H_N||q||^2` by `F-20260821-016`.
- `V(q)>=0` and can be dropped in a lower bound.
- the exact first-prime compressed translation is bounded below by `-c_2 I` because the symmetrized shift norm is `1` (`C-0040`).
- the residual kernel satisfies the Schur bound `||R_T||<=2T sup|r''|`.
- the supremum is enclosed by the exact Suzuki Bernoulli/Taylor coefficients plus the rigorous tail bound in `scripts.cert.residual_kernel`.

At the retained precision, `rho_R` is approximately `1.33218539338044` and `mu_14` approximately `0.0639772546354`, both with rigorous enclosing intervals.

## Dependencies

- `C-0040`;
- `F-20260821-016`;
- `R-0028`;
- `X-20260821-004`.

## Significance for RH research

The infinite-dimensional complement itself is no longer an open qualitative obstacle. It has an explicit positive scalar lower bound from a modest Legendre cutoff onward.

## Limits

The finite-to-tail cross block is not controlled by this result. Full positivity still requires a rigorous Schur correction.

## Verification

`X-20260821-004` recomputes all transcendental/residual quantities with exact rational inputs and Arb balls and records the full `mu_N` table.

## Timestamped addenda / corrections

None.
