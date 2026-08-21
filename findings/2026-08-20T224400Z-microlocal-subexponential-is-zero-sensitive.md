# Independent microlocal subexponential prime bounds are zero-sensitive

- **Finding ID:** `F-20260820-026`
- **Created:** `2026-08-20T22:44:00Z`
- **Last updated:** `2026-08-20T22:44:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

A fixed-interior smooth chirp cell centered at

```text
X=exp(4n u_0/A)
```

and Mellin frequency `gamma_0` is a smooth weighted prime discrepancy at the critical half-weight. Under the standard smooth explicit-formula/Mellin framework, a zero

```text
rho=beta+i gamma_0,
beta>1/2,
```

whose response is not annihilated by the chosen smooth weight contributes at exponential scale

```text
X^(beta-1/2)
= exp[4n u_0(beta-1/2)/A].
```

Therefore a theorem giving `exp(o(n))` control uniformly for a sufficiently rich family of such matched local cells would itself exclude right-of-line zeros in the corresponding frequency band.

## Evidence / derivation

The local Dirichlet reduction is `F-20260820-024`. Smooth Mellin inversion couples the weighted prime sum to `-zeta'/zeta`; a pole at a zero `rho` contributes the stated `X^(rho-1/2)` factor. This is the local form of the same zero sensitivity seen in `C-0019` and in smooth-weighted PNT converse theory.

## Dependencies

- `A-20260820-006`
- `C-0019`
- `F-20260820-024`
- `R-0013`

## Significance for RH research

It shows why partitioning the chirp and demanding an RH-scale estimate from each cell separately is not a safe simplification. The full transform may rely on cancellation across cells.

## Limits

The statement requires a weight whose Mellin response does not annihilate the candidate zero and the usual smooth explicit-formula hypotheses. It is not a claim that every individual arbitrary window estimate is exactly equivalent to RH.

## Verification

Derived from the smooth Mellin explicit formula and checked against the exact single-zero response already registered in `C-0019`.

## Timestamped addenda / corrections

None.
