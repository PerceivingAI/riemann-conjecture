# Bilinear nonseparability appears only on square-root-n logarithmic scale

- **Finding ID:** `F-20260821-003`
- **Created:** `2026-08-21T02:09:00Z`
- **Last updated:** `2026-08-21T02:09:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For factor log-widths `H_r,H_s` on a fixed-interior scale, the cross-phase size is

```text
|Delta F| ~ |Phi_n''| H_r H_s,
|Phi_n''|~c/n.
```

Thus `O(1)` bilinear nonseparability requires `H_r H_s~n`; balanced blocks require `H_r,H_s~sqrt(n)`.

The formal full pre-turning Bessel phase has excursion

```text
4n[xi(1)-xi(0)] = pi n,
```

or `n/2` full cycles.

## Dependencies

- `A-20260821-001`
- `C-0023`
- `X-20260821-001`

## Significance for RH research

The phase complexity is polynomial in `n`, while fixed-interior prime scales are exponential in `n`. Broad bilinear boxes do not reveal exponentially many new phase oscillations.

## Limits

The `pi n` statement concerns the formal Bessel phase function; the cosine asymptotic itself is not uniform at both endpoints.

## Verification

Direct algebra and numerical scale checks in `X-20260821-001`.

## Timestamped addenda / corrections

None.
