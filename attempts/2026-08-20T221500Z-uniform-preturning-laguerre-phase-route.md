# Uniform pre-turning Laguerre phase and zero-frequency matching

- **Attempt ID:** `A-20260820-005`
- **Created:** `2026-08-20T22:15:00Z`
- **Last updated:** `2026-08-20T22:15:00Z`
- **Status:** `COMPLETE`
- **Success target:** Derive the correct uniform pre-turning Bessel phase for the generalized Laguerre kernel, obtain the stationary-frequency map for a zero mode without using the earlier small-`u` approximation as a uniform formula, determine how the saddle relates to the exact Cayley zero response, and decide whether a generic Parseval/large-sieve reformulation is genuinely weaker than RH.

## Question / goal

`A-20260820-004` established that the pre-turning region `0<u<1` cannot be controlled by current pointwise PNT error bounds after taking absolute values. It also showed that a single zero mode contributes exactly

```text
S_(n,rho)=z_rho^(-n)-1,
z_rho=(rho-s0)/(rho+s0-1).
```

The next question is therefore not whether the Laguerre kernel oscillates, but exactly **how** it oscillates on the uniform scale and how that oscillation matches the Mellin frequencies `gamma=Im(rho)` of zeta zeros.

The earlier tooling contained the diagnostic approximation

```text
u_small(gamma)=A^2/(4 gamma^2),
```

obtained from the fixed-argument phase `2 sqrt(n t)`. That approximation is valid only when the stationary point is already near `u=0`; it was deliberately not accepted as the uniform pre-turning relation.

This attempt derives the genuine map and tests what it changes.

## Motivation

A phase-sensitive arithmetic estimate can only be formulated correctly once the phase function and its stationary points are known on the same scaling regime as the Laguerre kernel.

Three issues must be separated:

1. **fixed-interior pre-turning asymptotics:** `u` stays away from `0` and `1`;
2. **zero-frequency matching:** a Mellin factor `x^(i gamma)` selects a stationary point of the Laguerre phase;
3. **high-zero endpoint regime:** as `gamma` increases, the stationary point moves toward `u=0`, where replacing the Bessel function by its large-argument cosine is no longer uniform.

The third issue is especially important because the zeta zero spectrum is infinite.

## Dependencies and known results

Repository claims:

- `C-0010` — `RH <=> limsup |S_n|^(1/n)<=1`;
- `C-0011` — exact `d(psi-x)` Laguerre representation;
- `C-0018` — pre-turning absolute-value barrier and far-tail suppression;
- `C-0019` — exact single-zero transform `z_rho^(-n)-1`;
- `C-0020` — generic RH-scale dyadic mean-square control of `psi-x` already detects the RH boundary.

External sources:

- `R-0011` — DLMF uniform Laguerre Bessel/Airy expansions;
- `R-0016` — Lagarias, Li coefficients and Weil's quadratic functional;
- `R-0017` — Arias de Reyna, an `ell^2` asymptotic condition on normalized Keiper-Li coefficients equivalent to RH;
- `R-0018` — DLMF large-argument Bessel asymptotics and stationary-phase method.

Computation:

- `X-20260820-007` — numerical evaluation of the exact stationary map for the first eight numerically evaluated zeta-zero ordinates at `s0=2,3,4`.

## Mathematical setup

Fix

```text
s0>1,
A=2s0-1,
N=n-1,
alpha=1,
nu=4N+2alpha+2=4n,
t=nu*u=4n*u,
y=log x=t/A.
```

DLMF 18.15.18 defines, for `0<=u<=1`,

```text
xi(u)
= 1/2 [sqrt(u-u^2) + asin(sqrt(u))].
```

DLMF 18.15.19 gives a Bessel expansion for

```text
L_(n-1)^(1)(nu*u)
```

uniformly on `0<=u<=1-delta` for every fixed `delta>0`.

For a nontrivial zero

```text
rho=beta+i gamma,
delta_rho=beta-1/2,
```

write

```text
p_rho=(s0-rho)/A.
```

The exact single-zero transform is

```text
S_(n,rho)
= - integral_0^infinity exp(-p_rho*t)L_(n-1)^(1)(t) dt.
```

## Derivation / argument

### Step 1 — extract the uniform pre-turning phase

On every fixed compact subinterval

```text
epsilon <= u <= 1-delta,
```

DLMF 18.15.19, with `alpha=1`, has leading term

```text
L_(n-1)^(1)(nu*u)
~ exp(nu*u/2)
   / [2 u^(3/4)(1-u)^(1/4)]
   * xi(u)^(1/2) J_1(nu*xi(u)).
```

DLMF 10.17.2-3 gives

```text
J_1(z)
~ sqrt(2/(pi z)) cos(z-3pi/4)
```

for large positive `z`. Since `xi(u)` is bounded away from zero on a fixed interior interval, `nu*xi(u)->infinity` uniformly there.

Therefore the leading fixed-interior pre-turning kernel is

```text
exp(-nu*u/2)L_(n-1)^(1)(nu*u)
~ sqrt(2/(pi*nu))
   / [2 u^(3/4)(1-u)^(1/4)]
   * cos(nu*xi(u)-3pi/4).
```

The uniform phase is thus

```text
Phi_n(u)=nu*xi(u)-3pi/4
        =4n*xi(u)-3pi/4.
```

This replaces the fixed-argument approximation `2 sqrt(n t)` whenever `u` is treated as a fixed pre-turning variable.

### Step 2 — differentiate the phase exactly

Direct differentiation gives

```text
xi'(u)=1/2 sqrt((1-u)/u),
```

and

```text
-xi''(u)=1/[4 u^(3/2) sqrt(1-u)] > 0
```

for `0<u<1`.

Thus `xi'` decreases strictly from `+infinity` at the left endpoint to `0` at the turning point.

In the logarithmic prime variable `y=log x`, where

```text
u*u=A*y,
```

the oscillatory phase is

```text
Phi_n(y)=4n*xi(Ay/(4n))-3pi/4,
```

with instantaneous Mellin frequency

```text
Phi_n'(y)
= A*xi'(u)
= A/2 sqrt((1-u)/u).
```

The pre-turning Laguerre kernel is therefore a monotone **downward chirp** in `y`: its local frequency runs from infinity near `u=0` to zero as `u->1-`.

### Step 3 — exact uniform stationary-frequency map

First take a critical-line mode

```text
rho=1/2+i gamma,
gamma>0.
```

After cancellation of the Laguerre `exp(t/2)` factor against `Re(p_rho)=1/2`, the relevant cosine branch has phase per `nu`

```text
Psi_gamma(u)=gamma*u/A-xi(u).
```

The other cosine branch has no stationary point for positive `gamma`.

The stationary condition is

```text
Psi_gamma'(u)=0
<=> gamma/A = xi'(u)
<=> gamma/A = 1/2 sqrt((1-u)/u).
```

Solving gives the exact uniform pre-turning map

```text
u_gamma
= A^2/(A^2+4 gamma^2).
```

Hence

```text
t_gamma
= 4n A^2/(A^2+4 gamma^2),
```

and the corresponding prime scale is

```text
log x_gamma
= 4n A/(A^2+4 gamma^2).
```

The inverse map is

```text
gamma(u)
= A/2 sqrt((1-u)/u).
```

Thus every positive Mellin frequency corresponds to exactly one pre-turning coordinate.

### Step 4 — the old small-u formula is the large-gamma limit

The previous diagnostic was

```text
u_small=A^2/(4 gamma^2).
```

Writing

```text
r=A^2/(4 gamma^2),
```

the exact result is

```text
u_gamma=r/(1+r).
```

Therefore

```text
(u_small-u_gamma)/u_gamma = r = u_small.
```

So the old formula was not arbitrary: it is precisely the `gamma->infinity`, `u->0` expansion of the uniform map. It is now retained only under the explicit `small_u_*` API.

For the first numerically evaluated zeta-zero ordinate and `s0=3`, `X-007` gives

```text
gamma = 14.1347251417...,
u_gamma = 0.03033384878...,
u_small = 0.03128277577...,
relative error of u_small = 3.128... percent.
```

### Step 5 — the critical saddle phase equals the exact Cayley phase

At the stationary point one obtains

```text
Psi_gamma(u_gamma)
= -1/2 atan(A/(2 gamma)).
```

Therefore

```text
nu*Psi_gamma(u_gamma)
= -2n atan(A/(2 gamma)).
```

For

```text
rho=1/2+i gamma,
```

the Cayley factor is

```text
z_rho^(-1)
= (A/2+i gamma)/(-A/2+i gamma).
```

Its principal argument is

```text
arg z_rho^(-1)
= -2 atan(A/(2 gamma)).
```

Hence

```text
nu*Psi_gamma(u_gamma)
= n arg z_rho^(-1).
```

The uniform Bessel stationary phase exactly reproduces the phase of the zero's Cayley multiplier.

### Step 6 — the leading stationary amplitude normalizes to one

At `u=u_gamma`,

```text
Psi_gamma''(u_gamma)
= (A^2+4 gamma^2)^2/(8 A^3 gamma).
```

The leading Bessel/Laguerre amplitude combined with the ordinary stationary-phase factor contains

```text
1/2
* u_gamma^(-3/4)(1-u_gamma)^(-1/4)
/ sqrt(Psi_gamma''(u_gamma)).
```

Substitution of `u_gamma=A^2/(A^2+4gamma^2)` simplifies this expression **exactly to 1**.

Tracking the Bessel phase constant `+3pi/4`, the stationary-phase factor `+pi/4`, and the outer minus sign in `S_(n,rho)` shows that the localized stationary contribution for fixed critical-line `gamma` is

```text
z_rho^(-n)
```

to leading stationary-phase order.

This gives a local asymptotic explanation of the dominant oscillatory term in the exact identity

```text
S_(n,rho)=z_rho^(-n)-1.
```

The exact identity implies that the complement of the localized saddle supplies the remaining `-1+o(1)` collectively. This attempt does **not** claim that the `-1` comes from one endpoint alone; proving such a sharper decomposition would require a separate endpoint analysis.

### Step 7 — off-line amplification appears as complexified saddle geometry

Let

```text
delta_rho=beta-1/2.
```

At the real critical-line saddle, the additional real exponential factor is

```text
exp[4n delta_rho u_gamma/A].
```

Its logarithmic rate per `n` is

```text
4A delta_rho/(A^2+4 gamma^2).
```

Meanwhile the exact Cayley rate satisfies

```text
log |z_rho|^(-1)
= 1/2 log(
    [ (delta_rho+A/2)^2 + gamma^2 ]
    / [ (delta_rho-A/2)^2 + gamma^2 ]
  )
```

and has expansion

```text
log |z_rho|^(-1)
= 4A delta_rho/(A^2+4 gamma^2)
  + O(delta_rho^3).
```

So the real saddle captures exactly the first-order off-critical amplification.

There is also a natural complex stationary candidate. If

```text
h=gamma-i delta_rho,
```

analytic continuation of the stationary equation gives

```text
u_c=A^2/[A^2+4h^2].
```

The corresponding formal saddle exponent satisfies algebraically

```text
exp[-2i n atan(A/(2h))]
= z_rho^(-n).
```

This identity is useful structural evidence, but no steepest-descent contour deformation for the complex saddle is proved here. It is therefore **not** promoted to a full complex stationary-phase theorem.

### Step 8 — the prime side is a critical-half-weight nonlinear Fourier/Mellin chirp

The exact discrepancy representation is

```text
S_n
= A integral x^(-s0)L_(n-1)^(1)(A log x)
    d(psi(x)-x).
```

Set `y=log x` and `u=Ay/(4n)`. In the fixed-interior pre-turning regime the Laguerre exponential contributes

```text
exp(Ay/2).
```

Since

```text
s0-A/2=1/2,
```

the arithmetic factor becomes exactly the critical half-weight

```text
exp(-y/2) d(psi(e^y)-e^y).
```

Define the signed measure

```text
dmu(y)
= exp(-y/2) d(psi(e^y)-e^y).
```

Then the leading fixed-interior kernel has the schematic form

```text
S_n(pre, interior)
~ A/[2 sqrt(2 pi n)]
   integral
   u^(-3/4)(1-u)^(-1/4)
   cos(4n xi(u)-3pi/4)
   dmu(y),

u=Ay/(4n).
```

This is a nonlinear Fourier/Mellin transform: the Laguerre phase sweeps through Mellin frequencies, and a zero mode of height `gamma` is matched precisely at `u_gamma`.

This formula is a **kernel-level asymptotic on fixed interior regions**. It is not yet a justified asymptotic for the full infinite prime discrepancy integral. Accumulating the DLMF remainder against the arithmetic signed measure requires its own proof and cannot be replaced by an absolute bound that recreates the obstruction in `C-0018`.

### Step 9 — high zero frequencies coalesce with the endpoint

The stationary curvature gives the Gaussian scale

```text
sigma_u
= [nu Psi_gamma''(u_gamma)]^(-1/2).
```

A direct simplification yields the exact relative-width formula

```text
sigma_u/u_gamma
= sqrt(2 gamma/(A n)).
```

Therefore the saddle is well separated from `u=0` when

```text
gamma=o(n),
```

but coalesces with the endpoint when `gamma` is of order `n`.

The Bessel argument at the stationary point also satisfies

```text
nu xi(u_gamma)
~ 2A n/gamma
```

for large `gamma`, so the large-argument cosine approximation ceases to be uniform in the same `gamma~n` transition.

Consequently, fixed-`gamma` stationary-phase formulas cannot simply be summed over the entire infinite zero spectrum. The exact DLMF Bessel representation remains the appropriate starting point near the endpoint; a joint `n,gamma` endpoint analysis is still required.

### Step 10 — generic coefficient-space Parseval/L2 control is not a weaker route

Define

```text
M_N=sum_(n=N)^(2N) |S_n|^2.
```

If

```text
limsup |S_n|^(1/n)<=1,
```

then for every `epsilon>0`, eventually `|S_n|<=(1+epsilon)^n`, so

```text
M_N^(1/(2N)) <= (1+epsilon)^2 * N^(1/(2N))
```

for large `N`, and hence

```text
limsup M_N^(1/(2N))<=1.
```

Conversely,

```text
|S_N|^2 <= M_N,
```

so

```text
|S_N|^(1/N) <= M_N^(1/(2N)).
```

Thus

```text
RH
<=> limsup_(N->infinity) M_N^(1/(2N)) <= 1.
```

by `C-0010`.

Therefore a Parseval or large-sieve argument whose conclusion is merely a subexponential block `L2` bound for the coefficient sequence is **another RH-equivalent criterion**, not an automatically weaker intermediate lemma.

This does not make large-sieve machinery useless. It means the useful theorem must be genuinely arithmetic and independently prove the required chirped prime cancellation; one cannot count an abstract coefficient-space norm reformulation itself as progress.

Arias de Reyna's established `ell^2` equivalence for normalized Keiper-Li errors provides a closely related literature warning. Lagarias' relation of Li coefficients to Weil's quadratic functional provides complementary spectral context.

## Checks performed

### Algebraic / symbolic

Using SymPy:

- differentiated `xi(u)` and obtained `xi'(u)=sqrt(1-u)/(2sqrt(u))`;
- solved the stationary equation exactly;
- differentiated again and obtained the stated curvature;
- simplified the stationary amplitude normalization exactly to `1`;
- expanded the exact off-line Cayley rate and recovered `4A delta/(A^2+4gamma^2)` as its linear term;
- checked the Cayley phase identity algebraically.

### Numerical

`scripts/uniform_phase_diagnostics.py` was run at

```text
s0=2,3,4
```

using the first eight zeta-zero ordinates numerically evaluated by `mpmath.zetazero` at 40 decimal digits.

For every retained row:

- the phase residual was at binary-roundoff scale (`~1e-17`);
- the stationary normalization evaluated to `1.000000000000`;
- the difference between the exact uniform map and the old small-`u` approximation decreased with zero height.

The numerical zero ordinates are diagnostics, not certificates.

### Automated verification

After adding the uniform phase helpers:

- Python research modules compiled;
- the pytest/Hypothesis suite passed `276/276` tests;
- the Rust workspace passed `15/15` tests (`11` unit plus `4` integration tests).

### Literature cross-check

- DLMF 18.15.17-19 checked for `nu`, `xi`, and the uniform Laguerre Bessel expansion;
- DLMF 10.17.2-3 checked for the large-argument `J_1` phase;
- DLMF 2.3(iv) checked as the stationary-phase reference;
- Lagarias (2007) checked for the relation between Li coefficients and Weil's quadratic functional;
- Arias de Reyna (2011) checked for an `ell^2` Keiper-Li asymptotic condition equivalent to RH.

## Circularity check

No RH assumption is used to derive the Laguerre phase or the stationary map. The critical-line calculation is conditional only in the local sense that it asks what the kernel does to a mode with `beta=1/2`; the resulting formulas are then compared with the exact mode identity already known from `C-0019`.

The following are **not** accepted as independent proof inputs:

1. coefficient-block `L2` subexponentiality, because it is RH-equivalent by Step 10;
2. the `ell^2` Keiper-Li asymptotic condition from the literature, because it is explicitly RH-equivalent;
3. generic square-root pointwise or mean-square bounds for `psi-x`, already excluded by `C-0004` and `C-0020`;
4. a full prime-side chirp asymptotic obtained by integrating the pointwise DLMF error without proving an arithmetic error estimate;
5. summation of fixed-`gamma` stationary asymptotics over all zeros without a joint high-frequency/endpoint justification.

## Result

The stated intermediate target is complete.

Established:

1. the exact uniform pre-turning phase `4n xi(u)-3pi/4`;
2. the exact stationary-frequency map
   `u_gamma=A^2/(A^2+4gamma^2)`;
3. the exact prime location scale
   `log x_gamma=4nA/(A^2+4gamma^2)`;
4. the old `A^2/(4gamma^2)` formula is exactly the small-`u` asymptotic of the uniform map;
5. for a fixed critical-line mode, the real stationary saddle reproduces the exact Cayley phase and has unit leading normalization;
6. the real saddle reproduces the first-order off-line exponential amplification, while the formal complex saddle has exactly the Cayley exponent algebraically;
7. the pre-turning prime discrepancy is naturally a chirped transform of the critical-half-weight signed measure `exp(-y/2)d(psi(e^y)-e^y)`;
8. high zero frequencies coalesce with the `u=0` endpoint on the scale `gamma~n`, so fixed-interior stationary phase is not uniform across the full zero spectrum;
9. a generic coefficient-block `L2`/Parseval root-growth bound is itself RH-equivalent.

No proof of RH has been obtained.

## Obstruction / unresolved step

The next genuinely arithmetic requirement is:

> Prove an unconditional cancellation estimate for the critical-half-weight prime discrepancy against the nonlinear Laguerre chirp, with a remainder strong enough at exponential-root scale, while also controlling the `u->0` endpoint/high-frequency regime.

The problem is no longer lack of a phase formula. The phase is explicit. The missing theorem is cancellation for the arithmetic measure against that phase.

## Findings produced

- [`F-20260820-017`](../findings/2026-08-20T221500Z-uniform-preturning-stationary-map.md) — exact uniform stationary-frequency map.
- [`F-20260820-018`](../findings/2026-08-20T221500Z-critical-saddle-reproduces-cayley-mode.md) — critical saddle reproduces Cayley phase with unit normalization.
- [`F-20260820-019`](../findings/2026-08-20T221500Z-critical-half-weight-laguerre-chirp.md) — critical-half-weight prime-discrepancy chirp structure.
- [`F-20260820-020`](../findings/2026-08-20T221500Z-coefficient-block-l2-is-rh-equivalent.md) — generic coefficient block `L2` criterion is RH-equivalent.
- [`F-20260820-021`](../findings/2026-08-20T221500Z-high-zero-endpoint-coalescence.md) — high-zero stationary points coalesce with the left endpoint.

## Claims affected

Created `C-0021` through `C-0025`.

## Next action

Create `A-20260820-006` for a **prime-side nonlinear chirp / Dirichlet-polynomial reduction**:

1. fix compact pre-turning `u` windows and derive a rigorously accumulated kernel remainder rather than only a pointwise remainder;
2. microlocalize the chirp in `y=log m` so each short window has nearly constant Mellin frequency `gamma(u)`;
3. reduce the discrete part to weighted Dirichlet-polynomial / exponential sums involving `Lambda(m)m^(-1/2)`;
4. compare available unconditional mean-value, zero-density, van der Corput, and large-sieve estimates with the exact exponential-root target;
5. treat the `u->0`, `gamma~n` endpoint regime separately using the uniform Bessel representation rather than the large-argument cosine;
6. reject any candidate estimate that is already equivalent to RH through `C-0020`, `C-0024`, smooth-weighted-PNT converse theory, or another known criterion.

## Timestamped addenda / corrections

None yet.
