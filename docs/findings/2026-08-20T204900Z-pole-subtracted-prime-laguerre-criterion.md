# Pole-subtracted prime-Laguerre root-growth criterion

- **Finding ID:** `F-20260820-006`
- **Created:** `2026-08-20T20:49:00Z`
- **Last updated:** `2026-08-20T20:49:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For fixed `s0>1`, define

```text
A=2s0-1,
q=-s0/(s0-1),
S_n=P_n-(1-q^n),
```

with `P_n` the generalized prime-Laguerre trace from `C-0006`.

Then

```text
RH
<=> limsup_{n->infinity} |S_n|^(1/n) <= 1.
```

## Evidence / derivation

The generating function is

```text
d/dz log[(s(z)-1)zeta(s(z))]
 = -sum_{n>=1} S_n z^(n-1).
```

The Cayley map sends `|z|<1` to `Re(s)>1/2`. The function `(s-1)zeta(s)` has no pole at `s=1`, and its zeros in that half-plane are exactly the nontrivial zeros with `Re(rho)>1/2`. Hence the generating function is analytic on the full unit disk exactly when RH holds. Cauchy-Hadamard then gives the root-growth criterion.

## Dependencies

- `C-0002`
- `C-0006`
- `C-0009`
- `R-0010`
- `A-20260820-002`

## Significance for RH research

This is a minimal absolutely-convergent prime-side formulation in which the deterministic zeta-pole exponential has been removed exactly. Any exponential growth above rate `1` is tied to a zero inside the Cayley disk rather than to the pole at `s=1`.

## Limits

This criterion is equivalent to RH. It is a reformulation, not an independently established bound and not a proof.

## Verification

Mapped-domain geometry, pole removal, and the Cauchy-Hadamard implication were checked independently on `2026-08-20T20:49:00Z`.

## Timestamped addenda / corrections

None.
