# Below-first-prime endpoint is polynomially bounded

- **Finding ID:** `F-20260820-022`
- **Created:** `2026-08-20T22:44:00Z`
- **Last updated:** `2026-08-20T22:44:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For fixed `s0>1`, `A=2s0-1`, the portion of the exact discrepancy transform supported on `1<=x<2` satisfies

```text
|S_n^[1,2)| <= 2A(sqrt(2)-1)n.
```

Hence it is polynomial and contributes root rate `1`.

More generally, any shrinking endpoint `u<=eta_n=o(1)` is `exp(o(n))` under the global Laguerre inequality and trivial `Lambda(m)<=log m`.

## Evidence / derivation

On `[1,2)` there are no prime-power atoms, so `d(psi-x)=-dx`. DLMF 18.14.8 gives

```text
exp(-t/2)|L_(n-1)^(1)(t)| <= n.
```

Since `x^(-s0)exp[(A/2)log x]=x^(-1/2)`, direct integration gives the stated bound.

## Dependencies

- `A-20260820-006`
- `C-0011`
- `R-0019`

## Significance for RH research

The formal high-frequency endpoint in the zero-mode stationary picture is not a new prime-sum obstruction below the first prime. The primary arithmetic difficulty lies in the fixed-interior exponentially large prime ranges.

## Limits

This does not control fixed positive `u`; absolute bounds there retain a root base greater than `1`.

## Verification

Direct application of DLMF 18.14.8 and elementary integration.

## Timestamped addenda / corrections

None.
