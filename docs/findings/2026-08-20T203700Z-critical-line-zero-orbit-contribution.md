# Critical-line zero orbit contributes a nonnegative pair term

- **Finding ID:** `F-20260820-001`
- **Created:** `2026-08-20T20:37:00Z`
- **Last updated:** `2026-08-20T20:37:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For the standard Li transform

```text
w(rho) = (rho-1)/rho,
```

a genuinely off-critical nonreal zero with `w=r exp(i theta)` has four distinct symmetry images whose combined Li contribution is

```text
4 - 2(r^n+r^(-n)) cos(n theta).
```

On the critical line the orbit collapses to the two distinct zeros `rho` and `conjugate(rho)`, because `1-rho=conjugate(rho)`. Their actual contribution is

```text
2 - 2 cos(n theta) = 4 sin^2(n theta/2) >= 0.
```

The previously stated `8 sin^2(n theta/2)` value was a factor-of-two double count and is invalidated.

## Evidence / derivation

The functional equation and conjugation symmetry give the transformed values

```text
w, conjugate(w), 1/w, 1/conjugate(w)
```

when the four zeros are distinct. Summing `1-w^n` over those four values gives the off-line formula.

If `Re(rho)=1/2`, then `1-rho=conjugate(rho)` and `|w|=1`, so only the conjugate pair is distinct. Summing over that pair gives the corrected formula.

## Dependencies

- `C-0001`
- `C-0007`
- `A-20260820-001`
- `R-0001`, `R-0002` for the Li zero-sum convention and criterion.

## Significance for RH research

This gives the correct local positivity geometry on the critical line and prevents a persistent factor-of-two error from contaminating later filtered-zero calculations.

## Limits

This local orbit computation alone does not prove that one off-line orbit forces the full Li sequence to have a particular asymptotic after all zero contributions are combined. The global growth claim is taken from Voros (`C-0003`), not inferred from this identity alone.

## Verification

Algebraically rederived during `A-20260820-001` on `2026-08-20T20:37:00Z`; the orbit-size distinction was explicitly checked.

## Timestamped addenda / corrections

None.
