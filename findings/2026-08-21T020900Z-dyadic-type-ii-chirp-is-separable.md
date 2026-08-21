# Dyadic Type-II Laguerre chirp is asymptotically separable

- **Finding ID:** `F-20260821-002`
- **Created:** `2026-08-21T02:09:00Z`
- **Last updated:** `2026-08-21T02:09:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

On any fixed-interior Type-II box `a~M`, `b~N`, the logarithmic widths are at most `log 2` and `Phi_n''=O(1/n)`. The four-corner phase defect therefore satisfies

```text
|Delta F| <= C (log 2)^2/n.
```

Consequently

```text
exp(i Phi_n(log ab))
= C_0 P(a)Q(b)[1+O(1/n)]
```

for unimodular one-variable factors `P,Q`.

## Evidence / derivation

The four-corner defect is the double integral of `Phi_n''` over the logarithmic rectangle.

## Dependencies

- `A-20260821-001`
- `C-0023`
- `X-20260821-001`

## Significance for RH research

Standard dyadic Vaughan Type-II decomposition does not expose a genuinely two-dimensional oscillatory kernel. Any useful saving must exploit arithmetic coefficient structure.

## Limits

The `O(1/n)` statement is uniform only on fixed compact subintervals of the pre-turning range.

## Verification

`X-20260821-001` confirms `1/n` scaling at several centers and values of `n`.

## Timestamped addenda / corrections

None.
