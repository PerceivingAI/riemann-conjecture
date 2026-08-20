# Moving the generalized Li center right restores the half-weight in the fixed-prime Laguerre envelope

- **Finding ID:** `F-20260820-003`
- **Created:** `2026-08-20T20:37:00Z`
- **Last updated:** `2026-08-20T20:37:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

Let `s0>1`, `A=2s0-1`, and consider the generalized Li prime trace

```text
P_n(s0) = A sum_{m>=2} Lambda(m) m^(-s0) L_(n-1)^(1)(A log m).
```

For each fixed prime power `m`, the fixed-argument large-degree Laguerre asymptotic contains the factor

```text
e^(A log(m)/2) = m^(A/2).
```

Therefore the Dirichlet weight and this Laguerre envelope combine exactly as

```text
m^(-s0) m^(A/2) = m^(-1/2),
```

independently of `s0`.

## Evidence / derivation

- The exact generalized generating function and arithmetic interpretation supply the kernel `m^(-s0)L_(n-1)^(1)((2s0-1)log m)`.
- NIST DLMF 18.15.14 supplies the fixed-positive-argument `n -> infinity` Laguerre asymptotic with envelope `e^(x/2)`.
- Substituting `x=A log m` yields the cancellation algebraically.

## Dependencies

- `C-0002`
- `C-0005`
- `C-0006`
- `C-0008`
- `A-20260820-001`
- `R-0005`, `R-0006`, `R-0007`

## Significance for RH research

Centering in the absolutely convergent Euler-product region is still analytically useful, but it does not create a simple per-prime large-`n` exponential-envelope advantage. The critical `1/2` scale reappears in the kernel.

## Limits

This is **not** a global asymptotic for the infinite prime sum. DLMF 18.15.14 is uniform only on compact intervals of the Laguerre argument. Since `A log m` is unbounded as `m -> infinity`, this result does not justify interchanging the `n -> infinity` asymptotic with the prime sum.

No claim is made that `P_n(s0)` itself behaves like an ordinary `m^(-1/2)` sum.

## Verification

The exponent identity was checked algebraically and the exact scope of the DLMF asymptotic was checked on `2026-08-20T20:37:00Z`.

## Timestamped addenda / corrections

None.
