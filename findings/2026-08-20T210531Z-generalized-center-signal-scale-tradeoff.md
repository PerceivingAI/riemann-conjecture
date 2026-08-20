# Generalized-center prime-scale / off-line-signal tradeoff

- **Finding ID:** `F-20260820-011`
- **Created:** `2026-08-20T21:05:31Z`
- **Last updated:** `2026-08-20T21:05:31Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

The Airy saddle corresponds to the prime scale

```text
x_*(n;s0)=exp[4nA/(A^2-1)],
A=2s0-1.
```

For a fixed hypothetical off-critical zero `rho=beta+i gamma`, `beta>1/2`, the Cayley amplification factor is

```text
R_rho=|(rho+s0-1)/(rho-s0)|.
```

As `s0->infinity`,

```text
log R_rho=(2beta-1)/s0+O(s0^-2),
log x_*=2n/s0+O(n s0^-2),
```

so

```text
log(R_rho^n)/log(x_*) -> (2beta-1)/2.
```

## Significance for RH research

Increasing `s0` lowers the prime cutoff needed to reach the moving kernel scale, but it simultaneously weakens the exponential signature of any off-line zero. A large generalized center is useful numerically, not an asymptotic shortcut.

## Limits

This is a scaling statement, not a theorem that all numerical conditioning is invariant in `s0`.

## Dependencies

- `C-0002`
- `F-20260820-010`
- `A-20260820-003`
