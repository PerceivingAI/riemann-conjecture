# Prime-side chirp microlocalization, endpoint closure, and Dirichlet-polynomial barriers

- **Attempt ID:** `A-20260820-006`
- **Created:** `2026-08-20T22:44:00Z`
- **Last updated:** `2026-08-20T22:44:00Z`
- **Status:** `COMPLETE`
- **Success target:** Reduce the phase-aware pre-turning prime side from `A-005` to explicit local Dirichlet/exponential sums, determine whether the below-first-prime endpoint is a genuine obstruction, and test whether standard unconditional large-sieve/Dirichlet-polynomial tools can reach the RH-equivalent exponential-root target without circular assumptions.

## Question / goal

`A-005` identified the fixed-interior pre-turning phase

```text
Phi_n(y)=4n xi(Ay/(4n))-3pi/4,
y=log x,
xi(u)=1/2[sqrt(u-u^2)+asin(sqrt(u))],
```

with local Mellin frequency

```text
gamma(u)=Phi_n'(y)=A/2 sqrt((1-u)/u),
A=2s0-1.
```

The prime discrepancy is tested at the critical half-weight

```text
dmu(y)=exp(-y/2)d(psi(e^y)-e^y).
```

This attempt asks:

1. what happens to the formal high-frequency endpoint once the first prime `m=2` is taken into account;
2. what one fixed interior chirp window becomes after linearization;
3. whether standard Dirichlet-polynomial mean-value/large-sieve estimates beat the positive exponential root rate;
4. whether proving each microlocal window subexponential would actually be a weaker theorem than RH.

## Dependencies and known results

Repository claims:

- `C-0010` — `RH <=> limsup |S_n|^(1/n)<=1`;
- `C-0011` — exact `d(psi-x)` Laguerre transform;
- `C-0018` — pointwise absolute-value barrier in fixed pre-turning regions;
- `C-0019` — exact zero response `z_rho^(-n)-1`;
- `C-0021` — exact uniform pre-turning stationary-frequency map;
- `C-0023` — critical-half-weight nonlinear Laguerre chirp;
- `C-0024` — coefficient-block `L2` root criterion is RH-equivalent;
- `C-0025` — fixed-frequency stationary saddles formally coalesce with `u=0` for sufficiently high zero frequencies.

External sources:

- `R-0011`, `R-0018` — DLMF uniform Laguerre/Bessel phase;
- `R-0013` — smooth weighted PNT converse/zero-free-region guard;
- `R-0019` — DLMF global Laguerre inequality;
- `R-0020` — Montgomery-Vaughan mean-value/Hilbert-inequality framework for Dirichlet polynomials.

Computation:

- `X-20260820-008` — logarithmic chirp-window scales, first-prime frequency cap, and generic mean-value root scales.

## Mathematical setup

Fix `s0>1` and

```text
A=2s0-1.
```

The pole-subtracted sequence is

```text
S_n
= A integral_[1,infinity)
  x^(-s0)L_(n-1)^(1)(A log x) d(psi(x)-x).
```

Write

```text
t=A log x,
nu=4n,
u=t/nu,
y=log x.
```

On fixed compact pre-turning intervals, `A-005` gives

```text
exp(-t/2)L_(n-1)^(1)(t)
~ 1/[2 sqrt(2 pi n)]
   u^(-3/4)(1-u)^(-1/4)
   cos(4n xi(u)-3pi/4).
```

## Derivation / argument

### Step 1 — the interval below the first prime is deterministic and polynomially bounded

On

```text
1 <= x < 2,
```

there are no prime-power atoms, so

```text
d(psi(x)-x)=-dx.
```

Hence

```text
S_n^[1,2)
= -A integral_1^2
    x^(-s0)L_(n-1)^(1)(A log x) dx.
```

DLMF 18.14.8 gives, for `alpha>=0`,

```text
exp(-t/2)|L_N^(alpha)(t)|
<= L_N^(alpha)(0).
```

For `N=n-1`, `alpha=1`,

```text
L_(n-1)^(1)(0)=n.
```

Since

```text
x^(-s0) exp[(A/2)log x]
= x^(-1/2),
```

we obtain the exact elementary bound

```text
|S_n^[1,2)|
<= A n integral_1^2 x^(-1/2) dx
= 2A(sqrt(2)-1)n.
```

Therefore the whole below-first-prime endpoint is polynomial and irrelevant to exponential root growth.

### Step 2 — the discrete prime chirp has only an O(sqrt(n)) frequency range

The first prime atom is at

```text
y_2=log 2,
t_2=A log 2,
u_2=A log 2/(4n).
```

The instantaneous Mellin frequency there is

```text
gamma_2(n)
= A/2 sqrt((1-u_2)/u_2)
= A/2 sqrt(4n/(A log 2)-1).
```

Thus

```text
gamma_2(n)
~ sqrt(A n/log 2).
```

For prime atoms `m>=2`, the coordinate `u=A log m/(4n)` is at least `u_2`, and `gamma(u)` is decreasing. Hence the discrete prime side never reaches the formal `gamma~n` regime from `A-005`; its maximal local Mellin frequency is only `O(sqrt(n))`.

This does not invalidate `C-0025`: the exact zero-mode transform still has a formal high-frequency endpoint transition. It changes the **prime-side interpretation**. Frequencies much larger than `sqrt(n)` correspond below the first prime and are not a new arithmetic prime-sum obstacle.

### Step 3 — a shrinking prime endpoint is subexponential by absolute values

More generally, take any sequence

```text
eta_n -> 0,
0 < eta_n < 1.
```

The range

```text
u <= eta_n
```

corresponds to

```text
log x <= 4n eta_n/A.
```

Using DLMF 18.14.8 again, the discrete prime part is bounded by

```text
A n sum_(m<=exp(4n eta_n/A))
    Lambda(m)m^(-1/2),
```

and the continuous-density part has the same `x^(1/2)` exponential scale. The trivial estimates `Lambda(m)<=log m` and summation/integration give

```text
|S_n^(u<=eta_n)|
<= exp[2n eta_n/A+o(n)].
```

Therefore, if `eta_n=o(1)`,

```text
S_n^(u<=eta_n)=exp(o(n)).
```

So a genuinely shrinking left endpoint can be closed without any PNT error estimate at all.

### Step 4 — local linearization on a fixed interior window

Fix

```text
0 < epsilon <= u_0 <= 1-delta < 1
```

and let

```text
y_0=4n u_0/A,
X=exp(y_0).
```

The exact phase derivative is

```text
Phi_n'(y_0)=gamma_0
= A/2 sqrt((1-u_0)/u_0).
```

A second differentiation gives

```text
Phi_n''(y_0)
= -A^2/[16n u_0^(3/2)sqrt(1-u_0)].
```

Thus for a logarithmic window

```text
|y-y_0| <= H,
```

Taylor linearization has phase error

```text
O(H^2/n)
```

uniformly on fixed interior `u_0` ranges.

Consequently:

- `H=o(sqrt(n))` gives `o(1)` phase error;
- `H=O(sqrt(n))` gives bounded quadratic error and is the natural chirp-cell scale.

Even `H=o(sqrt(n))` corresponds to a multiplicative interval of ratio `exp(o(sqrt(n)))`, while its center is

```text
X=exp(4n u_0/A),
```

which is exponentially large in `n`.

### Step 5 — the microlocal prime discrepancy is a half-weight Dirichlet polynomial

Let `W` be a fixed smooth compactly supported cutoff and localize to

```text
W((log m-y_0)/H).
```

After freezing the algebraic amplitude and linearizing the phase, one cosine branch has the schematic arithmetic term

```text
D_(n,u0)
= sum_m Lambda(m)m^(-1/2+i gamma_0)
    W((log m-y_0)/H)
  - integral_0^infinity
    x^(-1/2+i gamma_0)
    W((log x-y_0)/H) dx,
```

up to the common phase, an `n^(-1/2)` algebraic prefactor, and controlled Taylor/amplitude corrections.

The conjugate cosine branch gives the opposite frequency.

Thus microlocalizing the Laguerre chirp really does reduce it to a smooth **prime Dirichlet polynomial at the critical half-weight**.

### Step 6 — generic Montgomery-Vaughan mean values retain the full exponential length

For a Dirichlet polynomial

```text
F(t)=sum_(m<=N) a_m m^(-it),
```

the classical Montgomery-Vaughan mean-value theorem has the scale

```text
integral_0^T |F(t)|^2 dt
= (T+O(N)) sum |a_m|^2
```

in the standard form relevant here.

For a localized chirp cell,

```text
N=exp(y_0+o(n))
 = exp(4n u_0/A+o(n)).
```

For

```text
a_m=Lambda(m)m^(-1/2)W(...),
```

a trivial bound already gives

```text
sum |a_m|^2=exp(o(n))
```

when `H=o(n)`, because the square weight is `Lambda(m)^2/m` over a logarithmic interval of sublinear width.

Any frequency range supplied by the Laguerre chirp is at most polynomial in `n` (indeed the discrete prime range is `O(sqrt(n))` by Step 2), so

```text
T=exp(o(n)).
```

The `O(N)` term therefore dominates. Taking square roots leaves

```text
RMS(F)
<= exp(2n u_0/A+o(n)).
```

Equivalently, the generic mean-value root base is

```text
exp(2u_0/A)>1.
```

This is exactly the positive exponential scale already visible in the absolute Laguerre envelope. Generic Dirichlet-polynomial `L2` machinery has not removed it.

`X-008` records the scale numerically. At `s0=3` (`A=5`), for example:

```text
u_0=0.10 -> root base exp(0.04)=1.040810...
u_0=0.50 -> root base exp(0.20)=1.221402...
u_0=0.75 -> root base exp(0.30)=1.349858...
```

### Step 7 — standard additive oscillation is intrinsically slow on the x-scale

The chirp is rapidly structured in `y=log x`, not in `x` itself. If

```text
f(x)=Phi_n(log x),
```

then on a fixed interior window

```text
f'(x)=gamma(u)/x,
```

and

```text
f''(x)
= [Phi_n''(log x)-Phi_n'(log x)]/x^2
= -gamma(u)/x^2+O(1/(n x^2)).
```

At `x~X=exp(cn)`, these derivatives are exponentially small. Classical additive van-der-Corput reasoning therefore sees only polynomially many phase revolutions over an exponentially long prime range and cannot by itself supply a square-root-in-`X` saving sufficient to reach root `1`.

The natural language of the phase is Mellin/Dirichlet frequency, not additive frequency.

### Step 8 — independently bounding every microlocal cell is too strong a target

The smooth local expression in Step 5 is precisely the kind of weighted prime error whose Mellin transform couples to `-zeta'/zeta` and hence to zeta zeros.

If a zero

```text
rho=beta+i gamma_0,
beta>1/2,
```

is present and a chosen smooth local weight has nonzero Mellin response at that zero, the explicit-formula contribution to a window centered at

```text
X=exp(4n u_0/A)
```

has exponential scale

```text
X^(beta-1/2)
= exp[4n u_0(beta-1/2)/A].
```

Thus a theorem asserting `exp(o(n))` control for all such matched local smooth discrepancies would itself exclude right-of-line zeros in the corresponding frequency band. This is not a surprising free consequence of smoothing; it is a local zero-free statement in another form.

This agrees with `R-0013`, where sufficiently strong smooth weighted PNT errors have converse implications for zero-free regions.

Therefore the strategy

```text
partition the full chirp into cells
+ prove every cell subexponential
+ sum absolutely over cells
```

is generally too strong and risks rebuilding RH window-by-window.

This also matches the numerical lesson of `A-004`: cancellation can occur between different `u` regions, so independent regional bounds may destroy the very cancellation the full transform uses.

### Step 9 — what standard tools do and do not close

Closed:

1. the exact `1<=x<2` endpoint is polynomial;
2. any shrinking `u=o(1)` endpoint is subexponential by the global Laguerre inequality;
3. the prime-side frequency range is only `O(sqrt(n))`;
4. the fixed-interior chirp has an explicit local Dirichlet-polynomial reduction.

Not closed:

1. fixed-interior prime cancellation across exponentially large `X=exp(cn)`;
2. global cancellation between microlocal frequency cells;
3. accumulation of the uniform Laguerre remainder against the signed prime discrepancy at root scale.

Standard generic mean-value/large-sieve estimates fail at item 1 because their Dirichlet-polynomial length term is exponentially large.

## Checks performed

### Algebraic / analytic

- differentiated the chirp phase in the logarithmic and ordinary prime variables;
- derived the first-prime frequency cap exactly;
- proved the below-first-prime polynomial bound from DLMF 18.14.8;
- proved the shrinking-endpoint `exp(o(n))` bound using only `Lambda(m)<=log m` and the global Laguerre inequality;
- derived the local Taylor scale `H=o(sqrt(n))`;
- derived the Montgomery-Vaughan exponential-length barrier.

### Computation

`scripts/chirp_window_diagnostics.py` was run at `n=1024` and `s0=2,3,4`.

For `s0=3`:

```text
u_2 = 8.461269293945e-4,
gamma_2 = 85.90895535014,
gamma_2/sqrt(n) = 2.684654854692.
```

The exact asymptotic constant is

```text
sqrt(A/log 2)=2.685...
```

and the recorded generic mean-value root bases agree with `exp(2u/A)`.

### Literature cross-check

- DLMF 18.14.8 checked directly for the global Laguerre inequality;
- Montgomery-Vaughan's 1974 Hilbert-inequality paper and modern statements of the resulting Dirichlet-polynomial mean-value theorem were checked;
- Han's smooth weighted PNT converse result (`R-0013`) retained as a circularity guard.

## Circularity check

No zero-free region beyond known unconditional results is assumed.

The following are rejected as independent proof inputs:

1. subexponential control of **every** matched fixed-interior smooth prime cell without an independent arithmetic proof, because such a family is zero-sensitive and can exclude `beta>1/2` zeros directly;
2. a generic Dirichlet-polynomial `L2`/large-sieve estimate asserted to remove the `O(N)` length term at exponentially long `N` without new arithmetic structure;
3. a square-root pointwise or mean-square PNT error;
4. independent absolute summation of all microlocal cells if the full transform relies on cross-cell cancellation.

## Result

The stated intermediate target is complete.

Established:

1. `|S_n^[1,2)| <= 2A(sqrt(2)-1)n`;
2. the maximal Mellin frequency carried by actual prime atoms is
   `gamma_2(n)~sqrt(A n/log 2)=O(sqrt(n))`;
3. every shrinking endpoint `u<=eta_n=o(1)` is `exp(o(n))` by absolute values;
4. a fixed-interior chirp cell linearizes on logarithmic width `H=o(sqrt(n))` to a critical-half-weight smoothed prime Dirichlet polynomial;
5. the Montgomery-Vaughan length term leaves RMS exponential scale `exp(2n u_0/A+o(n))`, so generic mean-value/large-sieve machinery does not reach root `1`;
6. proving all matched microlocal cells independently subexponential is itself a zero-sensitive target and is not a demonstrably weaker route than RH.

No proof of RH has been obtained.

## Obstruction / unresolved step

The remaining obstruction is now **global arithmetic cancellation**:

> Exploit arithmetic structure of `Lambda` and correlations across the nonlinear chirp without requiring each fixed-frequency microlocal prime discrepancy to satisfy an RH-strength bound on its own.

The endpoint/high-frequency regime is no longer the primary prime-side blocker.

## Findings produced

- `F-20260820-022` — below-first-prime polynomial bound.
- `F-20260820-023` — actual prime-side frequency cap is `O(sqrt(n))`.
- `F-20260820-024` — microlocal critical-half-weight Dirichlet-polynomial reduction.
- `F-20260820-025` — Montgomery-Vaughan exponential-length barrier.
- `F-20260820-026` — independent microlocal subexponential control is zero-sensitive.

## Claims affected

Created `C-0026` through `C-0030`.

## Next action

Create `A-20260820-007` for a **global bilinear/Vaughan decomposition of the nonlinear chirp**:

1. do not bound fixed-frequency cells independently;
2. apply a Vaughan/Heath-Brown-type identity to `Lambda(m)` in the global weighted chirp;
3. derive the Type I/II bilinear phases after writing `m=ab`, where the phase depends on `log a+log b`;
4. test whether mixed curvature and bilinear averaging can produce cancellation unavailable to one-dimensional Dirichlet-polynomial mean values;
5. quantify the result directly at exponential-root scale;
6. reject any bilinear estimate whose required hypothesis is already equivalent to RH or to a square-root PNT bound.

## Timestamped addenda / corrections

None yet.
