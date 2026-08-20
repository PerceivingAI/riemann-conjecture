# Current Research Status

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T22:10:00Z`
- **RH status in this repository:** `UNRESOLVED`

This file is the maintained snapshot of the current research frontier. Historical reasoning belongs in timestamped attempt/finding/computation records and `LOG.md`.

## Current state

Four formal research attempts are recorded:

- [`A-20260820-001`](../attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md) — generalized Li/Laguerre route; `BLOCKED`, with later corrections preserved.
- [`A-20260820-002`](../attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md) — exact zeta-pole subtraction and discrepancy criterion; `COMPLETE` intermediate target.
- [`A-20260820-003`](../attempts/2026-08-20T210531Z-airy-saddle-discrepancy-kernel-route.md) — uniform asymptotic saddle analysis; now `SUPERSEDED` as the active frontier by the phase-sensitive refinement in `A-004`.
- [`A-20260820-004`](../attempts/2026-08-20T212000Z-post-turning-phase-aware-discrepancy-route.md) — post-turning saddle geometry, region-splitting test, exact zero-mode response, and averaging barriers; intermediate target `COMPLETE`.

The versioned Python research environment (`pyproject.toml`, lockfiles, `.venv`) and native Rust engine under [`../crates/rh_engine/`](../crates/rh_engine/) support the six retained computation records under [`../computations/`](../computations/). The current small-`u` phase helpers are explicitly diagnostic only; `A-005` must derive the uniform pre-turning phase before they can be generalized.

No proof of RH has been obtained.

## Active leads

### L1 — Phase-aware full Laguerre transform

**Status:** `ACTIVE / PRIMARY`

The authoritative sequence remains

```text
S_n
= A integral x^(-s0)L_(n-1)^(1)(A log x) d(psi(x)-x),
A=2s0-1,
```

with

```text
RH <=> limsup |S_n|^(1/n) <= 1.
```

`A-004` shows that the decisive object must retain complex phase. For a single explicit-formula zero mode,

```text
rho=beta+i gamma,
z_rho=(rho-s0)/(rho+s0-1),
```

the transform is exactly

```text
S_(n,rho)=z_rho^(-n)-1.
```

The imaginary part `gamma` can reduce the exact exponential rate dramatically relative to a beta-only absolute envelope (`F-20260820-015`).

### L2 — Pre-turning/Bessel-phase analysis

**Status:** `ACTIVE / NEXT`

The pre-turning region `0<u<1`, with

```text
nu=4n,
u=t/nu=t/(4n),
```

cannot be discarded by inserting current unconditional PNT error bounds into an absolute-value estimate. Its Bessel phase must be retained.

The next attempt should derive the phase explicitly and test phase-sensitive transform estimates rather than `|E|` bounds.

### L3 — Far post-turning tail

**Status:** `CLOSED / AVAILABLE BOUND`

For the smooth-density exponent there is a unique `u_0(A)>u_*` with `Phi_A(u_0)=0`. Any fixed region `u>=u_0+delta` is exponentially suppressed using the uniform post-turning Laguerre expansion and only `E(x)=o(x)` (`F-20260820-014`).

### L4 — Generic averaging

**Status:** `CIRCULARITY GUARD`

A dyadic mean-square bound at square-root scale is not a free input. Known mean-square theory gives exponent `2Theta+1` when the rightmost zero abscissa is `Theta>1/2`; therefore an `X^(2+epsilon)`-scale bound for every epsilon would force RH (`F-20260820-016`).

Recent smooth-weighted PNT converse results provide an additional warning that sufficiently strong smoothed prime-error estimates can directly encode zero-free regions.

## Strongest verified intermediate results

1. `RH <=> limsup |S_n|^(1/n)<=1` for every fixed `s0>1` (`C-0010`).
2. `S_n` is exactly the `d(psi-x)` Laguerre transform (`C-0011`).
3. The density mode `1-q^n` is removed exactly (`C-0009`, `C-0011`).
4. The smooth-density maximum is a post-turning Laplace saddle separated from the true Airy transition; its width is explicit (`C-0017`).
5. The sufficiently far post-turning tail is absolutely suppressible, but the pre-turning region is not controlled at root-growth level by current unconditional PNT errors (`C-0018`).
6. A single zero mode has the exact response `z_rho^(-n)-1`, proving that phase is structurally essential (`C-0019`).
7. Generic RH-scale dyadic mean-square control of `psi-x` already forces the RH zero boundary (`C-0020`).

## Computational observations

- `X-005` confirms the `n^(-1/2)` post-turning saddle width and quantifies the gap between beta-only envelopes and exact complex-phase rates.
- At `s0=3`, synthetic `beta=0.6`, `gamma=15` has beta-only envelope rate `1.08333...` but exact Cayley rate `1.002164...`.
- `X-006` reproduces the exact single-mode Laplace transform numerically and shows material cancellation between regional pieces.

These are diagnostics only, not proof claims.

## Open requirements / blockers

The primary blocker is now:

> Prove a phase-sensitive arithmetic estimate for the full generalized Laguerre transform of `Lambda-1` / `d(psi-x)` that excludes exponential root growth without replacing the transform by absolute values or importing a norm estimate already equivalent to the RH zero boundary.

Pointwise square-root control and generic RH-scale mean-square control remain forbidden as assumptions.

## Invalidated or closed directions

### I1 — Critical-line quartet contribution `8 sin^2(...)`

**Status:** `INVALIDATED / CORRECTED`

Correct distinct-pair contribution: `4 sin^2(n theta/2)`.

### I2 — Move the Li center right and gain arbitrarily stronger prime decay

**Status:** `CLOSED AS A SIMPLE ASYMPTOTIC SHORTCUT`

The fixed-prime Laguerre envelope restores the `m^(-1/2)` scale.

### I3 — Raw generalized prime trace is subexponential

**Status:** `INVALIDATED / CORRECTED`

The raw trace contains the deterministic `1-q^n` pole mode. The authoritative target is the pole-subtracted `S_n`.

### I4 — Finish with any fixed pointwise PNT exponent above `1/2`

**Status:** `CLOSED AS SOLE MECHANISM`

Absolute-value insertion leaves exponential growth.

### I5 — Reduce the problem to one narrow Airy-transition window and bound all other regions absolutely

**Status:** `INVALIDATED / REFINED`

The smooth-density maximum is actually a post-turning Laplace saddle. The pre-turning region retains positive absolute-envelope root growth under current unconditional PNT errors, while phase-sensitive cancellations couple different regions. Only the sufficiently far post-turning tail is independently closed.

### I6 — Use a generic square-root-scale dyadic mean-square estimate as a weaker averaging input

**Status:** `CIRCULAR`

Such a bound already forces `Theta=1/2` by known mean-square theory.

## Next research action

Create `A-20260820-005` for the phase-aware pre-turning/full-transform route:

1. derive the DLMF Bessel-phase approximation explicitly for `0<u<1`;
2. derive the stationary-phase relation between `gamma` and `u` while retaining `x^(i gamma)`;
3. reformulate the prime side as a phase-sensitive transform rather than a norm of `E`;
4. investigate large-sieve/Parseval/correlation estimates tailored to that transform;
5. compare every candidate estimate against smooth-weighted-PNT converse theory and `C-0020` before attempting a proof.
