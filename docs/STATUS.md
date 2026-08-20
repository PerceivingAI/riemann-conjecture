# Current Research Status

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T20:37:00Z`
- **RH status in this repository:** `UNRESOLVED`

This file is the maintained snapshot of the current research frontier. Historical reasoning belongs in timestamped attempt/finding/computation records and `LOG.md`.

## Current state

The first research route has been formally imported and source-checked as `A-20260820-001`:

- [`attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md`](attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md)

It studies standard and generalized Li coefficients, their Möbius zero geometry, and their Laguerre-weighted prime representation.

No proof of RH has been obtained.

## Active leads

### L1 — Filtered Li/Laguerre prime trace

**Status:** `ACTIVE / NEXT`

The strongest surviving direction is to apply an explicit finite-difference filter to the Li or generalized-Li sequence so that:

- the known archimedean `n log n` trend is strongly suppressed;
- an off-unit-circle zero mode remains exponentially visible;
- the prime side becomes one explicit filtered Laguerre trace;
- the sufficient bound on that trace can be compared against known RH equivalents before any proof attempt.

### L2 — Generalized center `s0>1`

**Status:** `USEFUL TOOL, NOT SOLUTION`

Moving the generating center into the Euler-product half-plane gives an absolutely convergent prime series for each fixed coefficient and may be useful for rigorous manipulations. It does not provide a simple large-`n` decay gain: the fixed-prime Laguerre envelope restores the `m^(-1/2)` scale (`F-20260820-003`).

## Strongest verified intermediate results

1. By Voros's established asymptotic dichotomy, any proved subexponential bound `lambda_n=exp(o(n))` would imply RH (`F-20260820-002`).
2. The generalized coefficients centered at `s0>1` have an exact absolutely convergent prime-Laguerre component for every fixed `n` (`C-0006`).
3. The critical-line zero contribution has been corrected to the distinct-pair value `4 sin^2(n theta/2)`; the earlier factor `8` was double counting (`F-20260820-001`).
4. Moving `s0` right does not improve the fixed-prime exponential envelope: `m^(-s0)m^((2s0-1)/2)=m^(-1/2)` (`F-20260820-003`).

## Open requirements / blockers

The primary blocker is an unconditional, `n`-uniform cancellation bound for the relevant prime-Laguerre trace (or a rigorously filtered version of it) that is strong enough to rule out off-critical exponential modes but does **not** assume a known RH-equivalent estimate.

In particular, directly inserting

```text
psi(x)=x+O(x^(1/2+epsilon))
```

for every `epsilon>0` is circular because that statement is equivalent to RH (`F-20260820-004`).

## Invalidated or closed directions

### I1 — Critical-line quartet contribution `8 sin^2(...)`

**Status:** `INVALIDATED / CORRECTED`

The critical-line symmetry orbit has two distinct zeros, not four. Correct contribution: `4 sin^2(n theta/2)`.

### I2 — Move the Li center right and gain an arbitrarily stronger prime decay exponent

**Status:** `CLOSED AS A SIMPLE ASYMPTOTIC SHORTCUT`

Although the fixed-`n` Dirichlet series becomes absolutely convergent, the fixed-prime large-`n` Laguerre envelope exactly cancels the apparent extra `s0` decay down to the `m^(-1/2)` scale. This does not close all uses of generalized centers; it closes the naive decay-gain argument.

## Next research action

Create `A-20260820-002` for the finite-difference-filter route. Before attempting any bound:

1. derive the filter exactly on the zero side;
2. derive it exactly on the generalized prime-Laguerre side;
3. identify the weakest bound that would exclude an off-unit-circle singularity;
4. run a circularity comparison against established RH equivalents;
5. only then attempt analytic or computational estimates.
