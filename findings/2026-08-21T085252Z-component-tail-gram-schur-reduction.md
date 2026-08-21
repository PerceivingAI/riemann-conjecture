# Component tail-Gram Schur reduction for the exact-prime operator

- **Finding ID:** `F-20260821-019`
- **Created:** `2026-08-21T08:52:52Z`
- **Last updated:** `2026-08-21T08:56:20Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

Let the exact first-prime operator be split relative to low Legendre modes `P_N` and complement `Q_N`, and suppose the complement satisfies

```text
C_N>=mu_N I,
mu_N>0.
```

Write the cross block as

```text
B_N=B_V+B_2+B_R.
```

Define

```text
G_X=B_X B_X*=P_N X Q_N X P_N.
```

Then the finite matrix inequality

```text
A_N-(3/mu_N)(G_V+G_2+G_R)>0
```

is sufficient for positivity of the full operator.

Moreover, each tail Gram has the finite identity

```text
G_X=P_N X^2 P_N-(P_N X P_N)^2,
```

whenever the displayed products are defined on the low polynomial subspace.

## Evidence / derivation

For a low vector `u`,

```text
||(B_V*+B_2*+B_R*)u||^2
<=3 sum_X ||B_X*u||^2
```

by Cauchy-Schwarz in the three-component direct sum. The complement lower bound then gives

```text
2 Re <B_N q,u>
>= -mu_N||q||^2-mu_N^(-1)||B_N*u||^2.
```

Combining these inequalities proves the sufficient finite Schur condition. The tail-Gram identity follows from `Q_N=I-P_N`.

## Dependencies

- `F-20260821-018` for an explicit positive `mu_N`;
- `A-20260821-004`.

## Significance for RH research

This converts the remaining infinite-dimensional cross problem into rigorously computable finite matrices involving `V^2`, the squared compressed shift, and the residual operator square/projection tail.

## Limits

The matrices `G_V`, `G_2`, and `G_R` have not yet been certified. This finding is a reduction theorem, not a positivity result.

## Verification

The inequalities are elementary Hilbert-space Cauchy-Schwarz/completing-the-square arguments. No numerical premise is needed.

## Timestamped addenda / corrections

None.
