# Uniform 69-percent endpoint absorption is too lossy for the full first-prime proof

- **Finding ID:** `F-20260821-017`
- **Created:** `2026-08-21T08:52:52Z`
- **Last updated:** `2026-08-21T08:56:20Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

At `T=7/20`, the lower operator obtained by globally replacing

```text
V+P_2
```

with

```text
(69/100)V
```

is not positive semidefinite. The explicit polynomial

```text
w=P_0-P_2=(3/2)(1-x^2)
```

satisfies

```text
J(w)+(69/100)V(w)+R_T(w)-c_T||w||^2 < 0.
```

`C-0042` itself remains correct; this finding invalidates only the proposed use of that bound as the final global replacement in a full first-prime proof.

## Evidence / derivation

Exactly,

```text
||w||^2=12/5,
J(w)=3/5,
V(w)=47/25-(12/5)log2.
```

`X-20260821-004` evaluates the canonical Suzuki residual with Arb and certifies the entire quadratic form strictly below zero, near `-0.05275381732676`.

The same certificate places the critical retained fraction for this direction between `0.93` and `0.94`.

## Dependencies

- `C-0042` for the valid endpoint inequality being tested as a proof device;
- `C-0044` / `R-0028` for the mandatory Suzuki residual;
- `X-20260821-004`.

## Significance for RH research

This prevents spending effort on a false residual-positivity target. The prime translation must be retained more exactly in the low-mode block.

## Limits

This does not show the exact first-prime Weil form is negative. In fact, the exact prime contribution makes this particular test direction rigorously positive.

## Verification

The proof-path output uses exact rational test-function identities and Arb enclosures; the retained interval for the lower-operator value has strictly negative upper endpoint.

## Timestamped addenda / corrections

None.
