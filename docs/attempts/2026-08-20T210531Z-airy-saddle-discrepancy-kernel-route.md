# Airy-saddle structure of the pole-subtracted discrepancy kernel

- **Attempt ID:** `A-20260820-003`
- **Created:** `2026-08-20T21:05:31Z`
- **Last updated:** `2026-08-20T21:05:31Z`
- **Status:** `PROMISING`
- **Success target:** Put the exact discrepancy transform from `A-20260820-002` into a rigorous large-`n` uniform-asymptotic framework, identify the exponential saddle responsible for the removed zeta-pole mode, and isolate the first remaining estimate that cannot be supplied by a pointwise prime-number-theorem bound.

## Question / goal

For fixed `s0>1`, let

```text
A = 2s0-1,
q = -s0/(s0-1),
E(x) = psi(x)-x,

S_n
= A integral_[1,infinity)
    x^(-s0)L_(n-1)^(1)(A log x) dE(x).
```

Can the large-`n` behavior of this exact RH-equivalent sequence be localized sharply enough to reveal a cancellation mechanism that is not just the pointwise bound `E(x)=O(x^(1/2+epsilon))` in disguise?

This attempt uses both analytic derivation and reproducible scripts. Numerical work is used only to identify and falsify candidate asymptotic regimes; the mathematical claims below are proved independently where stated.

## Dependencies and known results

- `C-0010` — RH-equivalent root-growth criterion for `S_n`.
- `C-0011` — exact `d(psi-x)` representation.
- `C-0004` — square-root pointwise `psi` bound is RH-equivalent.
- `R-0011` — DLMF uniform Laguerre Bessel/Airy scaling and Laguerre derivative formula.
- `R-0012` — DLMF prime number theorem `psi(x)=x+o(x)`.

Reproducible computations:

- `X-20260820-001` — exact identity verification;
- `X-20260820-002` — kernel localization / Airy-saddle scan;
- `X-20260820-003` — high-precision prime-trace cutoff study;
- `X-20260820-004` — prime-density range decomposition.

## Mathematical setup

Use the logarithmic coordinate

```text
t = A log x,
x = exp(t/A).
```

Define

```text
g_n(t) = exp(-s0 t/A) L_(n-1)^(1)(t).
```

The continuous prime-density integral removed in `A-002` becomes

```text
integral_0^infinity exp(-p t)L_(n-1)^(1)(t) dt,

p=(s0-1)/A.
```

For `L_(n-1)^(1)`, DLMF's uniform Laguerre scale is

```text
nu = 4(n-1)+2(1)+2 = 4n.
```

It is therefore natural to define

```text
u = 4n,
u u = t,
u u = 4n u.
```

The Airy transition occurs at `u=1`.

## Derivation / argument

### Step 1 — rigorous integration by parts

For each fixed `n`, `f_n(x)=x^(-s0)L_(n-1)^(1)(A log x)` is smooth for `x>=1` and decays like `x^(-s0)` times a fixed polynomial in `log x`.

The prime number theorem gives

```text
E(x)=psi(x)-x=o(x).
```

Therefore, because `s0>1`,

```text
f_n(x)E(x) -> 0
```

as `x->infinity` for every fixed `n`.

At the lower endpoint,

```text
E(1)=-1,
L_(n-1)^(1)(0)=n,
f_n(1)=n.
```

Stieltjes integration by parts therefore gives the exact formula

```text
S_n
= A n - A integral_1^infinity E(x) f_n'(x) dx.
```

Changing to `t=A log x` gives

```text
S_n
= A n - A integral_0^infinity E(exp(t/A)) g_n'(t) dt.
```

Using DLMF's derivative identity

```text
d/dt L_k^(alpha)(t) = -L_(k-1)^(alpha+1)(t),
```

we obtain, for `n>=2`,

```text
S_n
= A n
  + integral_0^infinity E(exp(t/A)) exp(-s0 t/A)
      [s0 L_(n-1)^(1)(t) + A L_(n-2)^(2)(t)] dt.
```

For `n=1`, the `L_(-1)^(2)` term is understood as zero.

This is the first exact form in this project that exposes `E(x)` itself rather than `dE`.

### Step 2 — use the uniform Laguerre scale rather than fixed-argument asymptotics

DLMF defines

```text
nu=4N+2alpha+2
```

for degree `N`. With `N=n-1`, `alpha=1`, this is exactly `nu=4n`.

Its Bessel expansion is uniform on `0<=u<=1-delta`; the Airy expansion continues uniformly through and beyond the turning point. Thus the relevant large-`n` coordinate is

```text
nu=4n,
u=t/nu=t/(4n),
t=nu*u=4n*u.
```

not fixed `t`.

This corrects the qualitative limitation identified in `A-001`: fixed-argument Laguerre asymptotics cannot locate the moving prime range that dominates high-degree coefficients.

### Step 3 — derive the continuous-density Airy saddle

The continuous density kernel is

```text
D_n(t)=exp(-p t)L_(n-1)^(1)(t),
p=(s0-1)/A.
```

For `u>1`, the DLMF Airy expansion has exponential factors

```text
exp(nu u/2)
```

from the Laguerre prefactor and

```text
exp[-(2/3)nu zeta(u)^(3/2)]
```

from `Ai(nu^(2/3)zeta)`.

Since

```text
1/2-p = 1/(2A),
```

the exponential rate per `nu` is

```text
Phi_A(u)
= u/(2A)
  - (1/2)[sqrt(u^2-u)-arccosh(sqrt(u))],
  u>=1.
```

Differentiate the bracket:

```text
d/du [sqrt(u^2-u)-arccosh(sqrt(u))]
= sqrt((u-1)/u).
```

Hence

```text
Phi_A'(u)
= 1/(2A) - (1/2)sqrt((u-1)/u).
```

The unique stationary point is

```text
u_* = A^2/(A^2-1).
```

It is the exponential-envelope maximum. At this point,

```text
sqrt(u_*^2-u_*) = A/(A^2-1),

arccosh(sqrt(u_*)) = artanh(1/A),
```

and therefore

```text
Phi_A(u_*) = (1/2) artanh(1/A).
```

Because `nu=4n`, the resulting exponential factor is

```text
exp[4n Phi_A(u_*)]
= exp[2n artanh(1/A)]
= [(A+1)/(A-1)]^n
= [s0/(s0-1)]^n
= |q|^n.
```

This is an exact structural match:

> the dominant Airy saddle of the smooth prime-density Laguerre kernel has exactly the same exponential rate as the deterministic zeta-pole mode `1-q^n` removed in `A-20260820-002`.

Thus the pole subtraction is also, asymptotically, subtraction of the unique smooth-density exponential saddle.

### Step 4 — identify the moving prime scale

At the saddle,

```text
t_* = 4n A^2/(A^2-1).
```

Since `x=exp(t/A)`, the corresponding prime scale is

```text
x_*(n;s0)
= exp[4n A/(A^2-1)].
```

For large `s0`, this is approximately

```text
x_* ~ exp(2n/s0).
```

This explains the cutoff behavior seen in `X-20260820-003`: a fixed prime cutoff can resolve only a bounded range of `n`, and increasing `s0` moves the relevant prime range downward.

### Step 5 — center-choice tradeoff: no free numerical gain

For a hypothetical off-critical zero

```text
rho=beta+i gamma,
beta>1/2,
```

the Cayley singularity is

```text
z_rho=(rho-s0)/(rho+s0-1).
```

Its coefficient amplification factor is

```text
R_rho = |z_rho|^(-1),
```

with

```text
R_rho^2
= [(s0+beta-1)^2+gamma^2]
  /[(s0-beta)^2+gamma^2]
>1.
```

For fixed `rho` and `s0->infinity`,

```text
log R_rho
= (2beta-1)/s0 + O(1/s0^2).
```

Meanwhile

```text
log x_* = 2n/s0 + O(n/s0^2).
```

Thus

```text
log(R_rho^n)/log(x_*) -> (2beta-1)/2.
```

Moving the center farther right makes the necessary prime range numerically easier, but it simultaneously moves every off-line zero singularity closer to the unit circle at the matching scale. There is no obvious free asymptotic gain from taking `s0` very large.

### Step 6 — pointwise prime-error estimates remain the wrong tool

The integration-by-parts form contains

```text
E(exp(t/A)) exp(-s0 t/A) Laguerre(t).
```

If one inserts a fixed pointwise estimate

```text
E(x)=O(x^theta),
theta>1/2,
```

then the effective exponential prefactor before the Airy decay is positive at scale `(theta-1/2)/A`. The resulting uniform saddle still has exponential growth.

Therefore no fixed exponent `theta>1/2` can directly yield

```text
limsup |S_n|^(1/n)<=1
```

through absolute-value estimation of the integration-by-parts integral.

At the limiting `theta=1/2` one is back at RH-strength pointwise information.

So the remaining route must exploit cancellation — oscillatory, averaged, signed, or transform-specific — rather than a stronger absolute pointwise estimate for `E(x)`.

### Step 7 — computational reconnaissance

The scripts added under `scripts/` were run before drawing numerical conclusions.

Exact finite checks (`X-001`) passed through `n=40` for four rational centers.

The kernel scan (`X-002`) shows sampled maxima moving toward the analytic saddle:

```text
s0=3, A=5, predicted u_*=25/24=1.041666...

n=64   u_max=1.0211
n=128  u_max=1.0310
n=256  u_max=1.0362
```

and the observed logarithmic growth rate per `n` moves toward

```text
log|q|=log(3/2)=0.405465...
```

from below.

For `s0=4`, the predicted saddle is `49/48=1.020833...`; the scan moves from `u_max=1.0080` at `n=128` to `1.0141` at `n=256`.

The range decomposition (`X-004`) found that around the turning/saddle region the discrete prime contribution and continuous density contribution can each have magnitude hundreds while their difference is only `10^-2` to `10^-1` at the tested `n`. Doubling Simpson resolution preserved these differences, so they are not a quadrature artifact at the reported precision.

This is evidence only, but it supports studying **local discrepancy in the Airy window** rather than cancellation inside the raw Laguerre prime sum.

## Checks performed

- exact rational verification of the pole integral, shift annihilation, and Laguerre contiguous identity through `n=40` (`X-001`);
- Python bytecode compilation of all research scripts;
- DLMF uniform-scale and derivative formulas checked against the current 2026 DLMF pages;
- prime number theorem boundary condition checked against DLMF `psi(x)=x+o(x)`;
- kernel saddle differentiated independently and simplified algebraically to rate `|q|^n`;
- kernel localization scanned at two centers through `n=256`;
- prime-density range decomposition rerun at double quadrature resolution for the `n=16`, `s0=3` turning region.

## Circularity check

No RH-equivalent estimate is used to derive the integration-by-parts formula, uniform scale, Airy saddle, center tradeoff, or computational observations.

The route remains incomplete because the required final cancellation estimate for the discrepancy transform is itself RH-equivalent when stated as the full root-growth conclusion.

A direct assumption of `E(x)=O(x^(1/2+epsilon))` for every epsilon remains forbidden by `C-0004`.

## Result

This attempt advances the route in four concrete ways:

1. gives an exact integration-by-parts formula with all boundary terms closed using only the prime number theorem;
2. identifies the correct uniform variable `u=t/(4n)`;
3. proves that the smooth-density Airy saddle has rate exactly `|q|^n`, explaining the deterministic pole mode from `A-002` on the asymptotic side;
4. shows why pointwise bounds with any fixed exponent above `1/2` cannot finish the argument by absolute-value estimation.

No proof of RH has been obtained.

## Obstruction / unresolved step

The first genuinely open analytic requirement is now:

> Control the signed/oscillatory contribution of `E(x)=psi(x)-x` in the Airy transition window centered at `t ~ 4n A^2/(A^2-1)` strongly enough to beat every fixed exponential rate, without assuming square-root pointwise control of `E`.

The numerical range decomposition suggests that prime-density matching is already very strong in this window at modest `n`, but turning that observation into an unconditional asymptotic theorem is the unresolved step.

## Findings produced

- [`F-20260820-009`](../findings/2026-08-20T210531Z-exact-discrepancy-integration-by-parts.md) — exact integration-by-parts representation.
- [`F-20260820-010`](../findings/2026-08-20T210531Z-airy-saddle-reproduces-pole-rate.md) — smooth-density Airy saddle has exact rate `|q|^n`.
- [`F-20260820-011`](../findings/2026-08-20T210531Z-generalized-center-signal-scale-tradeoff.md) — generalized-center numerical scale and off-line signal weaken together.
- [`F-20260820-012`](../findings/2026-08-20T210531Z-pointwise-error-bound-barrier.md) — fixed pointwise exponents above `1/2` cannot close the discrepancy estimate by absolute bounds.

## Claims affected

Created `C-0013` through `C-0016`.

## Next action

Create a new attempt focused narrowly on the **Airy-window discrepancy**:

1. write the leading uniform Airy kernel explicitly with rigorous error terms on a fixed window around `u_*`;
2. split the integral into pre-turning, Airy-window, and post-turning regions;
3. prove unconditional exponential suppression outside the critical window where possible;
4. investigate averaged/smoothed estimates for `psi(x)-x` matched to the Airy-window width rather than pointwise estimates;
5. use the scripts to falsify candidate bounds before attempting proofs.

## Timestamped addenda / corrections

None yet.
