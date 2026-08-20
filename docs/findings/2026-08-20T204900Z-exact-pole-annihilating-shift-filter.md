# Exact pole-annihilating shift filter

- **Finding ID:** `F-20260820-008`
- **Created:** `2026-08-20T20:49:00Z`
- **Last updated:** `2026-08-20T20:49:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

Let `E` be the forward shift `(Ea)_n=a_(n+1)` and let `q=-s0/(s0-1)`. The degree-two operator

```text
T=(E-1)(E-q)
```

annihilates the full deterministic pole sequence `1-q^n`.

Applied to the generalized prime-Laguerre trace,

```text
T P_n
= A sum_{m>=2} Lambda(m)m^(-s0)
  [L_(n+1)^(0)(A log m)-q L_n^(0)(A log m)].
```

Moreover,

```text
RH <=> limsup |T P_n|^(1/n) <= 1.
```

## Evidence / derivation

`(E-1)(E-q)(1-q^n)=0` directly. DLMF 18.9.13 gives

```text
L_n^(0)=L_n^(1)-L_(n-1)^(1),
```

so `(E-1)L_(n-1)^(1)=L_n^(0)`, yielding the displayed kernel after applying `E-q`.

On generating functions the filter can cancel singularities only at `z=1` and `z=1/q=z(1)`. Neither point is the image of a nontrivial zeta zero, so an off-critical zero in the disk survives the filter.

## Dependencies

- `C-0005`
- `C-0009`
- `C-0010`
- `R-0007`
- `A-20260820-002`

## Significance for RH research

This is an exact discrete alternative to explicit pole subtraction. It may be useful if the order-zero Laguerre kernel admits stronger oscillatory estimates than the original order-one kernel.

## Limits

The filtered root-growth bound is itself RH-equivalent. The filter restructures the problem; it does not prove the required bound.

## Verification

Shift algebra and low-degree Laguerre cases were checked symbolically and against DLMF on `2026-08-20T20:49:00Z`.

## Timestamped addenda / corrections

None.
