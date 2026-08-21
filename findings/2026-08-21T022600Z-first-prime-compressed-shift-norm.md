# Exact first-prime compressed-shift norm

- **Finding ID:** `F-20260821-010`
- **Created:** `2026-08-21T02:26:00Z`
- **Last updated:** `2026-08-21T02:26:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For shift `a>0` on `L2([-T,T])`, the symmetrized compression

```text
S_(T,a)=P_T(U_a+U_a^*)P_T
```

decomposes into path-graph adjacency operators. If

```text
L=ceil(2T/a)
```

is the essential maximal chain length, then

```text
||S_(T,a)||=2cos(pi/(L+1)).
```

Throughout the first-prime window

```text
(1/2)log2 < T < (1/2)log3,
```

only `m=2` is active, `L=2`, and

```text
||S_(T,log2)||=1.
```

Hence the exact scalar norm of the first arithmetic perturbation is

```text
log2/sqrt2=0.4901290717... .
```

## Dependencies

- `A-20260821-002`
- `F-20260821-009`

## Significance for RH research

Produces a concrete first-prime continuation inequality against the archimedean spectral gap.

## Limits

A scalar norm comparison is only sufficient and may be far from sharp on the constrained subspace.

## Verification

Direct-integral/path-graph derivation and deterministic checks in `X-20260821-002`.

## Timestamped addenda / corrections

None.
