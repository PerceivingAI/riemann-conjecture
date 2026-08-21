# Legendre harmonic-number coercivity for the Weil jump form

- **Finding ID:** `F-20260821-016`
- **Created:** `2026-08-21T08:52:52Z`
- **Last updated:** `2026-08-21T08:56:20Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For

```text
J(w)=(1/4) int int |w(x)-w(y)|^2/|x-y| dx dy
```

on `[-1,1]`, the Legendre polynomial `P_n` is an eigenmode of the associated jump operator with quadratic-form eigenvalue

```text
H_n=sum_(k=1)^n 1/k.
```

Consequently, if `q` is orthogonal to `P_0,...,P_(N-1)`, then

```text
J(q)>=H_N ||q||_2^2.
```

## Evidence / derivation

Tuck's identity, as stated in `R-0032`, is

```text
int [P_n(x)-P_n(y)]/|x-y| dy = 2 H_n P_n(x).
```

Symmetrizing the double integral defining `J` gives the asserted quadratic eigenvalue. Orthogonality of Legendre polynomials then gives the complement inequality term by term.

## Dependencies

- `R-0032` — Gerontogiannis-Mesland modern statement;
- `R-0033` — Tuck original source;
- `A-20260821-004`.

## Significance for RH research

This supplies a quantitative high-mode coercivity estimate growing like `log N`, which is exactly what the finite-plus-infinite Schur strategy needs.

## Limits

It controls only the jump component. Other localized Weil terms still require norm or cross-tail bounds. It is a finite-support operator tool and does not imply RH.

## Verification

The normalization factor was checked directly against the quadratic-form symmetrization and Suzuki's `J` normalization.

## Timestamped addenda / corrections

None.
