# Current Research Status

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T20:49:00Z`
- **RH status in this repository:** `UNRESOLVED`

This file is the maintained snapshot of the current research frontier. Historical reasoning belongs in timestamped attempt/finding/computation records and `LOG.md`.

## Current state

Two formal research attempts are now recorded:

- [`A-20260820-001`](attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md) — generalized Li/Laguerre route; status `BLOCKED` with a timestamped correction.
- [`A-20260820-002`](attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md) — exact pole subtraction and shift filtering; intermediate target `COMPLETE`.

No proof of RH has been obtained.

## Active leads

### L1 — Pole-subtracted prime-discrepancy trace

**Status:** `ACTIVE / PRIMARY`

For fixed `s0>1`, define

```text
A=2s0-1,
q=-s0/(s0-1),

S_n
= A sum_{m>=2} Lambda(m)m^(-s0)L_(n-1)^(1)(A log m)
  -(1-q^n).
```

`A-20260820-002` proves the exact reformulation

```text
RH <=> limsup |S_n|^(1/n) <= 1.
```

More importantly for further work,

```text
S_n
= A integral x^(-s0)L_(n-1)^(1)(A log x) d(psi(x)-x).
```

The deterministic prime-density contribution has therefore been removed exactly. The next task is to study cancellation of this discrepancy transform without importing an RH-equivalent pointwise bound.

### L2 — Exact pole-annihilating shift filter

**Status:** `AVAILABLE TOOL`

The shift operator

```text
T=(E-1)(E-q)
```

annihilates the known pole sequence `1-q^n` exactly and converts the prime kernel to

```text
L_(n+1)^(0)(A log m)-q L_n^(0)(A log m).
```

This is retained as an alternative if order-zero Laguerre estimates are more tractable than the direct discrepancy form.

### L3 — Generalized center `s0>1`

**Status:** `USEFUL TOOL, NOT SOLUTION`

The generalized center keeps every fixed-`n` prime series absolutely convergent. It does not by itself improve the critical fixed-prime `m^(-1/2)` envelope.

## Strongest verified intermediate results

1. `S_n=P_n-(1-q^n)` removes the zeta pole exactly, not heuristically (`F-20260820-005`, `F-20260820-006`).
2. For every fixed `s0>1`, `RH <=> limsup |S_n|^(1/n)<=1` (`C-0010`).
3. `S_n` is exactly a Laguerre transform of the prime-counting discrepancy measure `d(psi-x)` (`C-0011`).
4. `(E-1)(E-q)` annihilates the full deterministic pole sequence and preserves every nontrivial-zero singularity inside the Cayley disk (`C-0012`).
5. The earlier critical-line pair correction remains `4 sin^2(n theta/2)`, not `8 sin^2(n theta/2)` (`F-20260820-001`).

## Open requirements / blockers

The primary blocker is now precise:

> Prove the subexponential root-growth bound for the **pole-subtracted** discrepancy sequence `S_n`, or an equivalent pole-annihilated version, by exploiting cancellation of the Laguerre kernel against `d(psi-x)` without assuming RH or an RH-equivalent estimate.

The standard input

```text
psi(x)=x+O(x^(1/2+epsilon))
```

for every `epsilon>0` remains circular (`C-0004`).

The root-growth target itself is RH-equivalent. It is allowed as the theorem we are trying to prove; it is not allowed as an assumed estimate.

## Invalidated or closed directions

### I1 — Critical-line quartet contribution `8 sin^2(...)`

**Status:** `INVALIDATED / CORRECTED`

Correct distinct-pair contribution: `4 sin^2(n theta/2)`.

### I2 — Move the Li center right and gain arbitrarily stronger prime decay

**Status:** `CLOSED AS A SIMPLE ASYMPTOTIC SHORTCUT`

The fixed-prime Laguerre envelope restores the `m^(-1/2)` scale.

### I3 — Raw generalized prime trace is subexponential

**Status:** `INVALIDATED / CORRECTED`

For every `s0>1`, the raw trace `P_n` contains `1-q^n` with `|q|>1`, coming from the known pole of `zeta` at `s=1`. A raw subexponential bound is impossible even if RH holds. The authoritative target is `S_n=P_n-(1-q^n)` or an exact pole-annihilated filter.

## Next research action

Create `A-20260820-003` for the discrepancy-kernel analysis:

1. transform `S_n` to the logarithmic coordinate `t=A log x`;
2. derive exact integration-by-parts forms and boundary terms;
3. determine the dominant kernel region as `n` grows using uniform Laguerre asymptotics rather than fixed-argument extrapolation;
4. test orthogonality/oscillatory cancellation against unconditional information on `psi(x)-x`;
5. isolate the first estimate that is genuinely unavailable rather than replacing it with a known RH equivalent.
