# Current Research Status

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T22:15:00Z`
- **RH status in this repository:** `UNRESOLVED`

This file is the maintained snapshot of the current research frontier. Historical reasoning belongs in timestamped attempt/finding/computation records and `LOG.md`.

## Current state

Five formal research attempts are recorded:

- [`A-20260820-001`](../attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md) — generalized Li/Laguerre route; `BLOCKED`, with later corrections preserved.
- [`A-20260820-002`](../attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md) — exact zeta-pole subtraction and discrepancy criterion; `COMPLETE` intermediate target.
- [`A-20260820-003`](../attempts/2026-08-20T210531Z-airy-saddle-discrepancy-kernel-route.md) — uniform post-turning saddle analysis; `SUPERSEDED` as active frontier by later phase-sensitive work.
- [`A-20260820-004`](../attempts/2026-08-20T212000Z-post-turning-phase-aware-discrepancy-route.md) — region-splitting test, exact zero-mode response, and averaging barriers; `COMPLETE` intermediate target.
- [`A-20260820-005`](../attempts/2026-08-20T221500Z-uniform-preturning-laguerre-phase-route.md) — exact uniform pre-turning phase, zero-frequency matching, Cayley saddle structure, and coefficient-`L2` circularity guard; `COMPLETE` intermediate target.

The versioned Python environment, pytest/Hypothesis suite, and native Rust engine support seven retained computation records under [`../computations/`](../computations/).

No proof of RH has been obtained.

## Active leads

### L1 — Prime-side nonlinear chirp / Dirichlet-polynomial reduction

**Status:** `ACTIVE / PRIMARY / NEXT`

The authoritative sequence remains

```text
S_n
= A integral x^(-s0)L_(n-1)^(1)(A log x)
    d(psi(x)-x),
A=2s0-1,
```

with

```text
RH <=> limsup |S_n|^(1/n) <= 1.
```

`A-005` gives the fixed-interior pre-turning phase explicitly. With

```text
y=log x,
u=Ay/(4n),
xi(u)=1/2[sqrt(u-u^2)+asin(sqrt(u))],
```

the leading phase is

```text
Phi_n(y)=4n xi(u)-3pi/4,
```

and its local Mellin frequency is

```text
Phi_n'(y)=A/2 sqrt((1-u)/u).
```

The arithmetic measure appears at the critical half-weight:

```text
dmu(y)=exp(-y/2)d(psi(e^y)-e^y).
```

The next task is to microlocalize this chirp and determine whether known unconditional estimates for weighted `Lambda(m)m^(-1/2)` Dirichlet/exponential sums can yield the required cancellation without importing an RH-equivalent statement.

### L2 — Endpoint / high-frequency regime

**Status:** `ACTIVE / REQUIRED`

A zero frequency `gamma>0` is matched at

```text
u_gamma=A^2/(A^2+4gamma^2).
```

The stationary relative width satisfies

```text
sigma_u/u_gamma=sqrt(2gamma/(A n)).
```

Therefore high frequencies accumulate at `u=0`, and the fixed-interior cosine/stationary-phase reduction is not uniform when `gamma` is of order `n`. The exact DLMF Bessel representation must be retained for this endpoint transition (`C-0025`).

### L3 — Uniform pre-turning stationary map

**Status:** `CLOSED / AVAILABLE TOOL`

The phase derivation itself is complete:

```text
nu=4n,
nu*u=t,
u=t/(4n),
```

```text
u_gamma=A^2/(A^2+4gamma^2),
log x_gamma=4nA/(A^2+4gamma^2).
```

For a fixed critical-line mode, the saddle phase is exactly the Cayley phase and the leading normalization is `1` (`C-0021`, `C-0022`).

The old helper

```text
u_small=A^2/(4gamma^2)
```

is retained only as the large-`gamma` / small-`u` approximation.

### L4 — Far post-turning tail

**Status:** `CLOSED / AVAILABLE BOUND`

For the smooth-density exponent there is a unique post-turning `u_0(A)` beyond which the relevant exponential rate is negative. Any fixed region `u>=u_0+delta` is exponentially suppressed using uniform Laguerre decay and only the ordinary PNT (`C-0018`).

### L5 — Generic averaging / Parseval

**Status:** `CIRCULARITY GUARD`

Two generic Hilbert-space shortcuts are now closed as independent intermediate targets:

1. RH-scale dyadic mean-square control of `psi-x` already forces the rightmost-zero boundary (`C-0020`).
2. For `M_N=sum_(n=N)^(2N)|S_n|^2`, the condition `limsup M_N^(1/(2N))<=1` is itself equivalent to RH (`C-0024`).

Large-sieve or Parseval machinery can still be useful **only if it proves a genuinely arithmetic prime-side estimate independently**.

## Strongest verified intermediate results

1. `RH <=> limsup |S_n|^(1/n)<=1` for every fixed `s0>1` (`C-0010`).
2. `S_n` is exactly the `d(psi-x)` Laguerre transform after the deterministic zeta-pole mode is removed (`C-0011`).
3. The smooth-density pole mode is the post-turning saddle removed in `A-002`/`A-003` (`C-0014`).
4. Current pointwise PNT bounds cannot control the pre-turning region after absolute values (`C-0018`).
5. A single zero mode has exact response `z_rho^(-n)-1` (`C-0019`).
6. The uniform pre-turning stationary map is `u_gamma=A^2/(A^2+4gamma^2)` (`C-0021`).
7. A fixed critical-line saddle reproduces the exact Cayley phase with unit leading normalization (`C-0022`).
8. The prime discrepancy is probed by an explicit nonlinear chirp at the critical half-weight (`C-0023`).
9. Coefficient-block `L2` root control is RH-equivalent (`C-0024`).
10. High zero frequencies coalesce with the left endpoint on the joint `gamma~n` scale (`C-0025`).

## Computational observations

- `X-005` quantified the loss from discarding complex zero phase.
- `X-006` numerically reproduced exact single-zero transforms and regional cancellation.
- `X-007` evaluated the new uniform stationary map for the first eight numerically computed zero ordinates at `s0=2,3,4`; phase residuals were at roundoff scale and the derived stationary normalization evaluated to `1` for every retained row.
- At `s0=3`, the first numerical zero gives `u_gamma=0.03033384878...`, versus the old small-`u` approximation `0.03128277577...`, a relative error of about `3.128%`.

These are diagnostics only, not proof claims.

## Open requirements / blockers

The primary blocker is now:

> Prove an unconditional, phase-sensitive cancellation estimate for the critical-half-weight prime discrepancy against the explicit nonlinear Laguerre chirp, with accumulated kernel error controlled at exponential-root scale and with a separate valid treatment of the `u->0`, `gamma~n` endpoint regime.

The phase formula itself is no longer missing.

## Invalidated, corrected, or closed directions

### I1 — Critical-line quartet contribution `8 sin^2(...)`

**Status:** `INVALIDATED / CORRECTED`

Correct distinct-pair contribution: `4 sin^2(n theta/2)`.

### I2 — Move the Li center right and gain arbitrarily stronger prime decay

**Status:** `CLOSED AS A SIMPLE ASYMPTOTIC SHORTCUT`

The fixed-prime Laguerre envelope restores the `m^(-1/2)` scale.

### I3 — Raw generalized prime trace is subexponential

**Status:** `INVALIDATED / CORRECTED`

The raw trace contains the deterministic `1-q^n` pole mode. The authoritative target is pole-subtracted `S_n`.

### I4 — Finish with any fixed pointwise PNT exponent above `1/2`

**Status:** `CLOSED AS SOLE MECHANISM`

Absolute-value insertion leaves exponential growth.

### I5 — Reduce the problem to one narrow Airy window and bound all other regions absolutely

**Status:** `INVALIDATED / REFINED`

Only the sufficiently far post-turning tail closes independently; pre-turning cancellation is phase-sensitive.

### I6 — Use a generic square-root-scale dyadic mean-square estimate as a weaker averaging input

**Status:** `CIRCULAR`

Such a bound already forces the RH zero boundary.

### I7 — Treat `A^2/(4gamma^2)` as the uniform pre-turning stationary map

**Status:** `CORRECTED / RETAINED ONLY AS ASYMPTOTIC`

The exact map is

```text
u_gamma=A^2/(A^2+4gamma^2).
```

The previous formula is its large-`gamma`, small-`u` expansion.

## Next research action

Create `A-20260820-006` for the prime-side nonlinear chirp / Dirichlet-polynomial route:

1. derive a rigorously accumulated DLMF-kernel remainder on compact pre-turning windows;
2. partition `y=log m` into windows on which the chirp can be linearized with controlled quadratic error;
3. express each discrete window as a weighted Dirichlet/exponential sum with coefficients `Lambda(m)m^(-1/2)`;
4. compare unconditional mean-value, large-sieve, van der Corput, exponent-pair, and zero-density estimates with the exact root-growth target;
5. separately analyze the `u->0`, `gamma~n` endpoint using the uniform Bessel representation rather than the cosine approximation;
6. apply `C-0020`, `C-0024`, and smooth-weighted-PNT converse results as circularity guards before accepting any proposed estimate.
