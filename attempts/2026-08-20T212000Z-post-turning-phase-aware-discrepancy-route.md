# Post-turning saddle geometry, phase-sensitive zero modes, and averaging barriers

- **Attempt ID:** `A-20260820-004`
- **Created:** `2026-08-20T21:20:00Z`
- **Last updated:** `2026-08-20T21:20:00Z`
- **Status:** `COMPLETE`
- **Success target:** Determine whether the `A-003` plan can reduce the remaining RH problem to independent control of a narrow Airy/turning window, quantify the actual saddle width and suppressible regions, test generic averaged information on `psi(x)-x`, and identify the next mathematically valid target without discarding phase information.

## Question / goal

`A-20260820-003` used the DLMF uniform Airy representation to identify the smooth-density exponential maximum

```text
u = 4n,
u u_* = A^2/(A^2-1),
A = 2s0-1,
```

with rate `|q|^n`. The next planned step was to isolate an "Airy window" around that point, prove the rest negligible, and attack the prime discrepancy only inside that window.

This attempt asks whether that localization is actually valid for the **pole-subtracted discrepancy transform**

```text
S_n
= A integral_[1,infinity)
    x^(-s0)L_(n-1)^(1)(A log x) d(psi(x)-x),
```

and whether pointwise or mean-square information on `E(x)=psi(x)-x` can close the required root-growth estimate.

## Motivation

A narrow-window decomposition is useful only if contributions outside the chosen window can be bounded without assuming RH-strength information and without destroying cancellations that are essential to the full transform.

There are two hazards:

1. the smooth-density saddle identified in `A-003` belongs to the part already removed exactly in `A-002`;
2. the Laguerre transform of a complex zero mode contains an oscillatory factor `x^(i gamma)`, so replacing it by an absolute envelope can be dramatically non-sharp.

The goal here is therefore diagnostic: determine which parts of the `A-003` localization remain valid after those facts are accounted for.

## Dependencies and known results

Repository claims:

- `C-0010` — exact RH-equivalent root-growth criterion for `S_n`;
- `C-0011` — exact `d(psi-x)` Laguerre representation;
- `C-0013` — exact integration-by-parts representation;
- `C-0014` — smooth-density post-turning saddle and pole rate;
- `C-0016` — fixed pointwise exponents above `1/2` fail by absolute values.

External sources:

- `R-0011` — DLMF uniform Bessel/Airy Laguerre asymptotics;
- `R-0013` — Han, smooth weighted PNT errors and converse implications for zeta zero-free regions;
- `R-0014` — Zhao, dyadic mean-square size of `psi(x)-x` in terms of the rightmost zero abscissa;
- `R-0015` — Johnston, current zero-density/PNT-error framework and Vinogradov-Korobov-scale unconditional error.

Reproducible computations:

- `X-20260820-005` — saddle width, region rates, and phase-loss diagnostics;
- `X-20260820-006` — regional decomposition of exact single-zero Laplace modes.

## Mathematical setup

Fix

```text
s0 > 1,
A = 2s0-1,
nu = 4n,
u = t/nu = t/(4n),
t = A log x.
```

For the smooth density removed in `A-002`, define

```text
D_n(t)
= exp[-p t] L_(n-1)^(1)(t),
p=(s0-1)/A.
```

For `u>=1`, write its DLMF exponential rate per `nu` as

```text
Phi_A(u)
= u/(2A)
  - (1/2)[sqrt(u^2-u)-arccosh(sqrt(u))].
```

`A-003` proved

```text
u_* = A^2/(A^2-1)
```

and

```text
exp[4n Phi_A(u_*)]=|q|^n,
q=-s0/(s0-1).
```

For a complex explicit-formula mode

```text
rho=beta+i gamma,
```

define

```text
p_rho=(s0-rho)/A,
z_rho=(rho-s0)/(rho+s0-1).
```

## Derivation / argument

### Step 1 — the smooth-density maximum is not asymptotically inside the Airy transition

DLMF's Airy approximation uses the argument

```text
nu^(2/3) zeta(u).
```

Near the turning point `u=1`, `zeta(u)` is linear in `u-1` to leading order. Hence the genuine Airy transition has width

```text
|u-1| = O(nu^(-2/3)) = O(n^(-2/3)).
```

But the smooth-density maximum satisfies

```text
u_*-1 = 1/(A^2-1),
```

which is a positive constant for every fixed `s0`.

Therefore, as `n->infinity`, the maximum is separated from the shrinking Airy transition by a fixed distance. The uniform Airy formula is a valid tool for deriving it, but the maximum itself is asymptotically a **post-turning Laplace saddle**, not an Airy-transition-window point.

This is a terminology and strategy correction to the wording used in `A-003` and the previous `STATUS.md`.

### Step 2 — exact quadratic width of the post-turning density saddle

From

```text
Phi_A'(u)
= 1/(2A) - (1/2)sqrt((u-1)/u),
```

we obtain

```text
Phi_A''(u)
= -1/[4 u^2 sqrt((u-1)/u)].
```

At `u=u_*`,

```text
Phi_A''(u_*)
= -(A^2-1)^2/(4A^3).
```

Thus

```text
4n[Phi_A(u)-Phi_A(u_*)]
= -k_A n (u-u_*)^2
  + O(n|u-u_*|^3),
```

where

```text
k_A=(A^2-1)^2/(2A^3).
```

The natural `e^(-1)` half-width is therefore

```text
delta u
~ sqrt(2A^3)/(A^2-1) * n^(-1/2).
```

Equivalently,

```text
delta t
~ 4 sqrt(2A^3 n)/(A^2-1),

delta log x
~ 4 sqrt(2A n)/(A^2-1).
```

So the smooth-density saddle occupies a window of order `sqrt(n)` in `t=log(x^A)`, not the `n^(1/3)` turning-transition scale.

`X-20260820-005` numerically checks the quadratic prediction at several centers.

### Step 3 — only the sufficiently far post-turning tail is absolutely suppressible

Because `Phi_A` is strictly decreasing after `u_*` and tends to `-infinity`, there is a unique

```text
u_0(A)>u_*
```

such that

```text
Phi_A(u_0)=0.
```

For example, the diagnostic script gives

```text
s0=2: u_0 = 2.334730444...
s0=3: u_0 = 1.722864153...
s0=4: u_0 = 1.515406554...
```

For any fixed `delta>0`, DLMF's uniform post-turning expansion therefore gives a negative exponential rate on

```text
u >= u_0+delta.
```

Since the ordinary PNT gives `E(x)=o(x)`, the corresponding portion of the integration-by-parts discrepancy integral is exponentially suppressed. This genuinely closes the sufficiently far post-turning tail.

That conclusion does **not** extend to the whole complement of a narrow saddle window.

### Step 4 — the pre-turning region cannot be discarded by known absolute PNT bounds

For `0<u<1` away from the turning point, the DLMF Bessel representation has only algebraic Bessel amplitude after its main Laguerre exponential factor is extracted. For the smooth-density scale the exponential part is

```text
exp[nu u/(2A)]
= exp[(2u/A)n]
```

or, per coefficient index `n`, the root rate is

```text
exp(2u/A)>1
```

for every fixed `u>0`.

More directly, after using an unconditional PNT error of Vinogradov-Korobov type,

```text
|E(x)|/x
<= exp[-c (log x)^(3/5)(log log x)^(-1/5)]
   * polylog(x),
```

and substituting the moving scale `log x ~ c_A n`, the relative-error factor is only

```text
exp[-o(n)].
```

It therefore does not change the positive exponential root rate `exp(2u/A)` produced by an absolute-value bound in any fixed pre-turning subregion.

So the plan "bound everything outside the Airy window absolutely" fails. The pre-turning region requires signed/oscillatory information.

### Step 5 — exact phase-aware transform of one zero mode

The explicit formula contains terms of the form

```text
E_rho(x)=-x^rho/rho.
```

Their differential is

```text
dE_rho(x)=-x^(rho-1) dx.
```

Substituting one such mode into the exact Stieltjes representation gives

```text
S_(n,rho)
= -A integral_1^infinity
    x^(rho-s0-1)L_(n-1)^(1)(A log x) dx.
```

With `t=A log x`, this becomes

```text
S_(n,rho)
= - integral_0^infinity
    exp[-p_rho t] L_(n-1)^(1)(t) dt,

p_rho=(s0-rho)/A.
```

For `Re(p)>0`, the Laguerre generating function gives the exact Laplace transform

```text
integral_0^infinity
  exp(-p t)L_(n-1)^(1)(t)dt
= 1 - [(p-1)/p]^n.
```

But

```text
(p_rho-1)/p_rho
= (rho+s0-1)/(rho-s0)
= z_rho^(-1).
```

Therefore

```text
S_(n,rho)=z_rho^(-n)-1.
```

This identity is exact.

Consequences:

- if `Re(rho)=1/2`, then `|z_rho|=1`, so an individual critical-line mode has no exponential amplitude;
- if `Re(rho)>1/2`, then `|z_rho|<1`, so the mode grows exponentially at rate `|z_rho|^(-1)>1`;
- the imaginary part `gamma` is essential: it can greatly reduce the exact rate relative to a `beta`-only absolute envelope.

For instance, at `s0=3` a hypothetical `beta=0.6` mode has beta-only envelope rate

```text
1.083333...,
```

whereas retaining `gamma=15` gives exact Cayley rate

```text
1.002164411....
```

The absolute envelope has discarded almost all of the phase cancellation.

### Step 6 — region-by-region estimates can destroy the cancellation we need

`X-20260820-006` numerically integrates the exact single-mode Laplace transform over bins in `u=t/(4n)` and compares the sum with `z_rho^(-n)-1`.

For the synthetic mode

```text
s0=3,
beta=0.6,
gamma=5,
n=64,
```

the two adjacent bins around the turning region have magnitudes approximately

```text
u in [0.75,1.00]: 6.6663
u in [1.00,1.25]: 5.9135,
```

while the exact full-transform magnitude is only

```text
3.73625....
```

The truncated numerical integral agrees with the exact Laplace value to about `1e-4` in that run, and substantially better at smaller `n`.

This does not prove an asymptotic cancellation theorem. It does prove a methodological point: the transform's phase couples different `u` regions, so demanding a strong independent bound for every region may be substantially stronger than bounding the full transform and may even eliminate cancellations that make the exact coefficient small.

### Step 7 — generic RH-scale mean-square input is circular

Let

```text
Theta = sup{Re(rho): zeta(rho)=0}.
```

Zhao (2025), Lemma 8, records the established dyadic mean-square behavior

```text
if Theta=1/2:
    integral_X^(2X) (psi(x)-x)^2 dx ~asymp X^2;

if Theta>1/2:
    X^(2Theta+1-epsilon)
    << integral_X^(2X) (psi(x)-x)^2 dx
    << X^(2Theta+1).
```

Therefore any theorem of the generic form

```text
for every epsilon>0,
integral_X^(2X) (psi(x)-x)^2 dx
<<_epsilon X^(2+epsilon)
```

would force `Theta=1/2`, hence RH.

So Cauchy-Schwarz combined with an RH-scale dyadic mean-square estimate is not an independent shortcut. It imports the same zero boundary in averaged form.

This is consistent with recent smooth-weighted PNT work: Han explicitly studies converse implications from sufficiently strong smooth weighted prime errors back to zero-free regions. Smoothing alone does not erase zero-location information.

### Step 8 — what remains of the three-region program

The original `A-004` plan can now be classified precisely:

1. **Far post-turning tail:** can be suppressed unconditionally by uniform Laguerre decay plus the ordinary PNT.
2. **Post-turning region before the root-one crossing:** has positive absolute envelope and cannot be discarded generically.
3. **Pre-turning/oscillatory region `0<u<1`:** also has positive absolute envelope under known unconditional PNT errors; phase must be used.
4. **True Airy transition near `u=1`:** is only a shrinking `O(n^(-2/3))` region and is not by itself the whole obstruction.
5. **Full transform:** preserves the complex phase and has the exact zero-mode response `z_rho^(-n)-1`.

Thus the mathematically correct next object is not an absolute Airy-window discrepancy norm. It is the **phase-aware Laguerre transform as a whole**.

## Checks performed

### Algebraic checks

- differentiated `Phi_A` twice and simplified the curvature at `u_*`;
- verified the `sqrt(n)` saddle-width formulas;
- verified the single-zero Laplace transform by the Laguerre generating function;
- verified `(p_rho-1)/p_rho=z_rho^(-1)` exactly.

### Analytic/domain checks

- `Re(p_rho)>0` holds for every nontrivial zeta zero because `Re(rho)<1<s0`;
- DLMF Airy uniformity applies on fixed post-turning neighborhoods;
- the actual Airy transition scale follows from the `nu^(2/3)zeta(u)` argument;
- far-tail suppression uses only `E(x)=o(x)` once the Laguerre exponential rate is strictly negative;
- the pre-turning failure statement is tied to current unconditional PNT error scale, not to an assumption that `E(x)` is as large as `x`.

### Numerical checks

- `scripts/window_diagnostics.py` compiled and ran at `s0=2,3,4`;
- the sampled kernel is consistent with the derived saddle curvature at increasing `n`;
- the phase-loss diagnostic reproduces exact Cayley rates and shows large gaps from beta-only envelopes;
- `scripts/zero_mode_bins.py` numerically reproduces the exact single-mode Laplace transform in the retained tests.

### Literature cross-check

- DLMF uniform Laguerre formulas rechecked;
- Zhao's 2025 Lemma 8 checked directly in the open-access paper;
- Han's current arXiv version on smooth weighted PNT/zero-free-region converses checked;
- Johnston's current version of the PNT-error/zero-density analysis checked for the unconditional Vinogradov-Korobov-scale error form.

## Circularity check

No RH-equivalent estimate is assumed in the new derivations.

The following candidate inputs are explicitly rejected as proof inputs:

1. square-root pointwise control of `psi(x)-x`;
2. RH-scale dyadic mean-square control of `psi(x)-x`;
3. a full smooth-weighted error estimate already known, by converse theory, to imply a zero-free region reaching the critical line;
4. region-by-region subexponential bounds asserted without proving that such bounds are actually true under RH.

The exact single-zero transform is an identity, not a proof: it exposes how the transform detects the zeros.

## Result

This attempt achieved its diagnostic target and changes the research frontier.

Established:

1. the `A-003` smooth-density maximum is a post-turning Laplace saddle, not an asymptotic Airy-transition-window point;
2. its Gaussian width is `O(n^(-1/2))` in `u`, `O(sqrt(n))` in `t`, with explicit curvature;
3. the sufficiently far post-turning tail is unconditionally exponentially suppressible;
4. the pre-turning region is **not** suppressible by inserting current unconditional PNT errors into an absolute-value bound;
5. a single explicit-formula zero mode has exact response `z_rho^(-n)-1`;
6. the imaginary phase can reduce the exact mode rate drastically compared with the beta-only absolute envelope;
7. generic dyadic mean-square control at square-root scale already detects `Theta=1/2` and therefore cannot be used as an independent shortcut.

The previous narrow "Airy-window discrepancy" target is therefore superseded.

No proof of RH has been obtained.

## Obstruction / unresolved step

The first genuinely open requirement is now:

> Find a phase-sensitive arithmetic estimate for the **full** Laguerre transform of `Lambda-1` / `d(psi-x)` that controls its exponential root growth without replacing the transform by absolute values or importing a zero-location-equivalent norm bound.

The known pointwise and generic mean-square tools either lose the decisive phase or already encode the RH boundary.

## Findings produced

- [`F-20260820-013`](../findings/2026-08-20T212000Z-post-turning-saddle-width.md) — post-turning classification and exact Gaussian width.
- [`F-20260820-014`](../findings/2026-08-20T212000Z-regionwise-absolute-bound-barrier.md) — far tail closes, pre-turning absolute route does not.
- [`F-20260820-015`](../findings/2026-08-20T212000Z-single-zero-phase-aware-transform.md) — exact phase-aware response `z_rho^(-n)-1`.
- [`F-20260820-016`](../findings/2026-08-20T212000Z-mean-square-rh-boundary.md) — RH-scale dyadic mean square already detects the rightmost-zero boundary.

## Claims affected

Created `C-0017` through `C-0020`.

`A-20260820-003` receives a timestamped terminology/strategy addendum and is superseded as the active frontier; its established formulas remain valid.

## Next action

Create `A-20260820-005` for a **phase-aware pre-turning / full-transform analysis**:

1. write the DLMF Bessel-phase approximation explicitly for `0<u<1`;
2. derive the stationary-phase map between zero height `gamma` and Laguerre coordinate `u`;
3. keep the `x^(i gamma)` phase rather than bounding it absolutely;
4. investigate whether a large-sieve, Parseval, or arithmetic correlation estimate for this specific transform is genuinely weaker than RH;
5. use the smooth-weighted-PNT converse literature and `C-0020` as circularity guards before accepting any candidate estimate.

## Timestamped addenda / corrections

None yet.
