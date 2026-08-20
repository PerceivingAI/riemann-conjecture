# Current Research Status

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T21:05:31Z`
- **RH status in this repository:** `UNRESOLVED`

This file is the maintained snapshot of the current research frontier. Historical reasoning belongs in timestamped attempt/finding/computation records and `LOG.md`.

## Current state

Three formal research attempts are recorded:

- [`A-20260820-001`](attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md) — generalized Li/Laguerre route; `BLOCKED`, with later corrections preserved.
- [`A-20260820-002`](attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md) — exact zeta-pole subtraction and discrepancy criterion; `COMPLETE` intermediate target.
- [`A-20260820-003`](attempts/2026-08-20T210531Z-airy-saddle-discrepancy-kernel-route.md) — uniform Airy-saddle analysis of the pole-subtracted discrepancy kernel; `PROMISING`.

A dependency-free Python research toolkit now lives in [`../scripts/`](../scripts/) and has four retained computation records under [`computations/`](computations/).

No proof of RH has been obtained.

## Active leads

### L1 — Airy-window prime discrepancy

**Status:** `ACTIVE / PRIMARY`

For fixed `s0>1`, the authoritative sequence remains

```text
S_n
= A integral x^(-s0)L_(n-1)^(1)(A log x) d(psi(x)-x),
A=2s0-1.
```

`A-003` identifies the correct uniform variable

```text
nu=4n,
u=t/(4n),
t=A log x,
```

and proves that the smooth prime-density kernel has its exponential saddle at

```text
u_* = A^2/(A^2-1),
```

with growth exactly

```text
[s0/(s0-1)]^n=|q|^n.
```

That is precisely the deterministic zeta-pole rate removed in `A-002`.

The remaining target is therefore not the smooth prime density: it is the signed discrepancy `psi(x)-x` in the Airy transition window around the moving scale

```text
x_*(n;s0)=exp[4nA/(A^2-1)].
```

### L2 — Exact integration-by-parts form

**Status:** `ACTIVE TOOL`

Using only the prime number theorem to close the boundary terms,

```text
S_n = A n - A integral E(x) f_n'(x) dx,
E(x)=psi(x)-x.
```

This exposes `E(x)` directly and is the preferred starting point for averaged or oscillatory estimates (`F-20260820-009`).

### L3 — Generalized center selection

**Status:** `NUMERICAL TOOL, NOT ASYMPTOTIC SHORTCUT`

Larger `s0` reduces the prime scale needed to resolve a given coefficient numerically, but it simultaneously moves any hypothetical off-line zero closer to the Cayley unit circle. The two effects scale together (`F-20260820-011`).

## Strongest verified intermediate results

1. `RH <=> limsup |S_n|^(1/n)<=1` for every fixed `s0>1` (`C-0010`).
2. `S_n` is exactly the `d(psi-x)` Laguerre transform (`C-0011`).
3. The exact integration-by-parts form requires only the ordinary prime number theorem for its boundary terms (`C-0013`).
4. The uniform Airy saddle of the smooth density kernel is `u_*=A^2/(A^2-1)` and has rate exactly `|q|^n` (`C-0014`).
5. Any direct absolute-value argument based only on a fixed pointwise exponent `|psi(x)-x|=O(x^theta)`, `theta>1/2`, still leaves exponential growth (`C-0016`).
6. Exact script-based checks found no sign/index error in the core identities through `n=40` at four rational centers (`X-20260820-001`).

## Computational observations

- Kernel maxima for `s0=3` move toward the predicted `u_*=25/24`: sampled `u_max=1.0211,1.0310,1.0362` for `n=64,128,256` (`X-002`).
- At `s0=3`, `n=16`, turning-region prime and continuous-density contributions of magnitude `~3.26e2` differed by only `~2.0e-2` in the `u in [0.75,1]` bin; doubling quadrature resolution preserved the difference (`X-004`).
- Fixed prime cutoffs lose convergence as `n` rises; moving `s0` right extends the numerically stable range, matching the analytic moving-scale prediction (`X-003`).

These are evidence and diagnostics only, not proof claims.

## Open requirements / blockers

The primary blocker is now localized:

> Prove sufficiently strong signed/averaged cancellation of `E(x)=psi(x)-x` against the uniform Airy-window kernel near `t=4nA^2/(A^2-1)`, without assuming square-root pointwise control of `E`.

The standard RH-equivalent input

```text
psi(x)=x+O(x^(1/2+epsilon))
```

for every `epsilon>0` remains forbidden as an assumption.

A fixed pointwise exponent above `1/2` is also insufficient if inserted only through absolute values; `A-003` records this barrier explicitly.

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

### I4 — Finish the discrepancy bound with any fixed pointwise PNT exponent above `1/2`

**Status:** `CLOSED AS SOLE MECHANISM`

Such an absolute bound still leaves positive exponential growth in the uniform Airy regime (`F-20260820-012`). Pointwise estimates may still be used as auxiliary bounds outside the critical window.

## Next research action

Create `A-20260820-004` focused only on the Airy-window discrepancy:

1. write the leading uniform Airy approximation with explicit error control on a fixed neighborhood of `u_*`;
2. split the discrepancy integral into pre-turning, Airy-window, and post-turning regions;
3. prove unconditional exponential suppression outside the critical region where possible;
4. investigate averaged/smoothed information on `psi(x)-x` matched to the Airy-window width;
5. use the scripts to reject false candidate estimates before formal proof work.
