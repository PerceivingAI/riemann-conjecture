# Grouped arithmetic preserves the three-component Schur factor

- **Finding ID:** `F-20261001-002`
- **Created:** `2026-10-01T10:14:40Z`
- **Last updated:** `2026-10-01T10:14:40Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

Let `Pi_N` be the low Legendre projection and `Q_N=I-Pi_N`. Let the total signed arithmetic operator be

```text
P=sum_{m in A(T)}P_m.
```

Suppose the full low-to-tail cross block is grouped as

```text
B_N=B_V+B_P+B_R
```

and the complement obeys `C_N>=mu_N I` with `mu_N>0`. Define

```text
G_X=B_XB_X*=Pi_N X Q_N X Pi_N
```

for `X in {V,P,R}`. Then strict positivity of

```text
S_N=A_N-(3/mu_N)(G_V+G_P+G_R)
```

is sufficient for strict positivity of the full operator.

For the combined arithmetic operator,

```text
G_P=Pi_N P^2 Pi_N-Pi_N P Pi_N P Pi_N.
```

In the unnormalized low Legendre basis, with diagonal Gram matrix `D`, this is represented by

```text
G_P=P^2-PD^{-1}P,
```

where the first `P^2` denotes the low matrix of the operator square. In the immediate `{2,3}` window, this square contains the mixed products `P_2P_3+P_3P_2`; therefore `G_P` is generally not `G_2+G_3`.

## Evidence / derivation

Relative to the low/high decomposition, write the full operator as

```text
[ A_N   B_N  ]
[ B_N*  C_N  ].
```

From `C_N>=mu_N I`, completing the square gives

```text
2 Re <B_N q,u>
>=-mu_N||q||^2-mu_N^(-1)||B_N*u||^2.
```

Because the arithmetic terms have first been summed into the single self-adjoint operator `P`, the cross block has exactly three grouped components. Hence

```text
||(B_V*+B_P*+B_R*)u||^2
<=3(||B_V*u||^2+||B_P*u||^2+||B_R*u||^2)
```

by Cauchy-Schwarz in the three-component direct sum. Combining the two inequalities yields the factor-3 sufficient Schur condition.

The tail-Gram identity follows from `Q_N=I-Pi_N`:

```text
Pi_N P Q_N P Pi_N
=Pi_N P(I-Pi_N)P Pi_N
=Pi_N P^2 Pi_N-Pi_N P Pi_N P Pi_N.
```

In a nonorthonormal Legendre basis, composition through the low space inserts the inverse Gram matrix `D^{-1}`, producing the stated matrix identity. No positivity or commutativity assumption on the individual `P_m` is used.

## Dependencies

- `C-0048` — historical three-component Schur argument;
- `C-0058` — generic prime-power complement bound;
- `F-20261001-001`;
- `docs/MULTI_PRIME_CONTRACT.md`.

## Significance for RH research

This explicitly closes the critical factor-3 mathematical gate before multi-prime certification code is built. The factor depends on the three grouped components `V,P,R`, not on the number of active prime powers.

## Limits

This result does not compute `G_P`, prove a positive Schur margin, admit any support/dimension pair, or authorize reuse of the frozen v1 certificate profile. A future implementation must compute the combined arithmetic square including all mixed prime-power products and must be independently verified before theorem use.

## Verification

The derivation was checked directly against the original `F-20260821-019` proof. Replacing the historical arithmetic component `P_2` by the self-adjoint sum `P` leaves the three-vector Cauchy-Schwarz argument unchanged. Expanding `P=P_2+P_3` confirms that the exact combined tail Gram contains the required mixed terms.

## Timestamped addenda / corrections

None.
