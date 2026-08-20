# Exact discrepancy integration-by-parts representation

- **Finding ID:** `F-20260820-009`
- **Created:** `2026-08-20T21:05:31Z`
- **Last updated:** `2026-08-20T21:05:31Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For fixed `s0>1`, `A=2s0-1`, `E(x)=psi(x)-x`, and

```text
f_n(x)=x^(-s0)L_(n-1)^(1)(A log x),
```

the exact discrepancy sequence satisfies

```text
S_n = A n - A integral_1^infinity E(x) f_n'(x) dx.
```

Equivalently, with `t=A log x`,

```text
S_n
= A n
  + integral_0^infinity E(exp(t/A)) exp(-s0 t/A)
      [s0 L_(n-1)^(1)(t)+A L_(n-2)^(2)(t)] dt,
```

where the second Laguerre term is zero for `n=1`.

## Evidence / derivation

Stieltjes integration by parts is applied to `C-0011`. DLMF's prime number theorem gives `E(x)=o(x)`, sufficient to make the upper boundary vanish for every fixed `n` because `s0>1`. At `x=1`, `E(1)=-1` and `L_(n-1)^(1)(0)=n`, giving the boundary term `A n`. DLMF 18.9.23 supplies the Laguerre derivative formula.

## Dependencies

- `C-0011`
- `R-0011`
- `R-0012`
- `A-20260820-003`

## Significance for RH research

This exposes the ordinary prime-counting error `E(x)` directly and closes the boundary terms without any RH-strength estimate.

## Limits

The formula does not bound `S_n`. Taking absolute values and inserting standard pointwise bounds still leaves an exponential barrier.

## Verification

Boundary signs and the Laguerre derivative index were independently rederived during `A-003`.
