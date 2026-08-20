# Critical-half-weight Laguerre chirp on the prime discrepancy

- **Finding ID:** `F-20260820-019`
- **Created:** `2026-08-20T22:15:00Z`
- **Last updated:** `2026-08-20T22:15:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

Set

```text
y=log x,
u=Ay/(4n),
A=2s0-1.
```

On every fixed compact pre-turning interval `epsilon<=u<=1-delta`, the leading Laguerre kernel in the exact discrepancy transform

```text
S_n=A integral x^(-s0)L_(n-1)^(1)(A log x)d(psi(x)-x)
```

has phase

```text
Phi_n(y)=4n xi(Ay/(4n))-3pi/4
```

and instantaneous Mellin frequency

```text
Phi_n'(y)=A/2 sqrt((1-u)/u).
```

After the Laguerre exponential is combined with `x^(-s0)`, the arithmetic signed measure appears at exactly the critical half-weight

```text
dmu(y)=exp(-y/2)d(psi(e^y)-e^y).
```

Thus the fixed-interior pre-turning problem is a nonlinear Fourier/Mellin chirp transform of the critical-half-weight prime discrepancy.

## Evidence / derivation

The factor `exp(Ay/2)` in the Laguerre asymptotic combines with `exp(-s0 y)` and

```text
s0-A/2=1/2.
```

The phase and frequency follow from `F-20260820-017` and the chain rule.

## Dependencies

- `A-20260820-005`
- `C-0011`
- `F-20260820-017`
- `R-0011`
- `R-0018`

## Significance for RH research

The next missing theorem can be phrased arithmetically: establish cancellation of `Lambda-1` at the critical half-weight against this explicit chirp, rather than estimating `|psi-x|`.

## Limits

This is a kernel-level asymptotic on fixed interior regions. It does not by itself justify integrating the DLMF remainder against the full prime discrepancy measure. A proof must control the accumulated arithmetic remainder and separately handle the left endpoint/high-frequency regime.

## Verification

The phase derivative and half-weight identity were checked algebraically. The numerical stationary-map diagnostics are consistent with the frequency interpretation.

## Timestamped addenda / corrections

None.
