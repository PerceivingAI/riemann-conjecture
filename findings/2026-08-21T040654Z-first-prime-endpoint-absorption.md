# Exact first-prime endpoint absorption at T=7/20

- **Finding ID:** `F-20260821-012`
- **Created:** `2026-08-21T04:06:54Z`
- **Last updated:** `2026-08-21T04:06:54Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

At `T=7/20`, let

```text
tau=log2/T,
epsilon=2-tau,
V(x)=-(1/2)log(1-x^2),
c_2=log2/sqrt2.
```

For the first-prime compressed translation quadratic form `P_2`,

```text
V + P_2 >= (69/100)V >= 0.
```

## Derivation

The translation couples only the two edge intervals of length `epsilon`, and

```text
|<C_tau w,w>| <= ||w||_edge^2.
```

On those edges,

```text
V(x) >= kappa_edge
=(1/2)log(1/(2epsilon)).
```

`scripts/weil_endpoint_absorption_certificate.py` proves with exact rational series bounds that

```text
epsilon < 34/1701,
kappa_edge > 8/5,
c_2 < 62/125.
```

Hence

```text
c_2/kappa_edge < 31/100
```

and the result follows.

The certificate proves its `log2` inequalities from the exact atanh series; it does not merely bracket a decimal approximation.

## Dependencies

- `C-0039`
- `C-0040`
- `A-20260821-003`
- `X-20260821-003`

## Circularity check

No RH assumption or RH-equivalent estimate is used. This is a finite-support operator inequality only.
