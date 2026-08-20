# Square-root-scale Chebyshev-psi input is circular for this route

- **Finding ID:** `F-20260820-004`
- **Created:** `2026-08-20T20:37:00Z`
- **Last updated:** `2026-08-20T20:37:00Z`
- **Type:** `OPEN_REQUIREMENT`
- **Status:** `VERIFIED`

## Statement

A proof of the Li/Laguerre prime-trace bound in `A-20260820-001` cannot legitimately take as an input

```text
psi(x) = x + O(x^(1/2+epsilon))
```

for every `epsilon>0`, because that estimate is itself equivalent to the Riemann Hypothesis.

The route therefore requires a cancellation theorem tailored to the Laguerre kernel that is obtained unconditionally and is demonstrably weaker than a standard RH-equivalent pointwise prime-counting error estimate.

## Evidence / derivation

NIST DLMF 25.16.4 states the equivalence between RH and

```text
psi(x) = x + O(x^(1/2+epsilon))
```

for every positive `epsilon`.

Using that estimate to prove an RH-equivalent Li bound would simply move the hypothesis from the zero side to the prime side.

## Dependencies

- `C-0004`
- `A-20260820-001`
- `R-0008`

## Significance for RH research

This is the current circularity boundary for the prime-trace route. Any proposed estimate must be checked against this and other known RH equivalents before being treated as progress.

## Limits

This finding does not prove that every possible Laguerre-weighted cancellation estimate is equivalent to RH. It only excludes the direct use of the standard square-root-scale pointwise `psi` estimate as an independent input.

## Verification

Checked against NIST DLMF 25.16.4 on `2026-08-20T20:37:00Z`.

## Timestamped addenda / corrections

None.
