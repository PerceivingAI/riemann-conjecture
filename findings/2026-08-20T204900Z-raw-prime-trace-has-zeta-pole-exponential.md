# Raw generalized prime trace contains a deterministic zeta-pole exponential

- **Finding ID:** `F-20260820-005`
- **Created:** `2026-08-20T20:49:00Z`
- **Last updated:** `2026-08-20T20:49:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For every fixed `s0>1`, let

```text
A=2s0-1,
q=-s0/(s0-1),
P_n=A sum Lambda(m)m^(-s0)L_(n-1)^(1)(A log m).
```

The simple pole of `zeta(s)` at `s=1` contributes exactly

```text
h_n = 1-q^n
```

to `P_n`. Since `|q|>1`, the raw sequence `P_n` necessarily contains deterministic exponential growth even if RH is true.

Therefore a target of the form `P_n=exp(o(n))` is invalid.

## Evidence / derivation

Under the generalized Cayley map, `s=1` maps to `z=1/q`, which lies strictly inside the unit disk. Expanding

```text
s'(z)/(s(z)-1)
```

gives the coefficient sequence `1-q^n` exactly. See `A-20260820-002`.

## Dependencies

- `C-0006`
- `R-0010`
- `A-20260820-002`

## Significance for RH research

This corrects the blocker stated too broadly in `A-20260820-001`. Future prime-side work must first subtract or annihilate the known pole mode.

## Limits

This does not say anything about RH by itself. The exponential mode comes from the known pole at `s=1`, not from an off-critical zero.

## Verification

Algebraic coefficient extraction and the mapped pole location were independently checked on `2026-08-20T20:49:00Z`.

## Timestamped addenda / corrections

None.
