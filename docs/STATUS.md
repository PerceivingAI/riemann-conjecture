# Current Research Status

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-21T02:26:00Z`
- **RH status in this repository:** `UNRESOLVED`

This file is the maintained snapshot of the current research frontier. Historical reasoning belongs in timestamped attempt/finding/computation records and `LOG.md`.

## Current state

Eight formal research attempts are recorded:

- [`A-20260820-001`](../attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md) — generalized Li/Laguerre route; `BLOCKED`, with later corrections preserved.
- [`A-20260820-002`](../attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md) — exact zeta-pole subtraction and discrepancy criterion; `COMPLETE` intermediate target.
- [`A-20260820-003`](../attempts/2026-08-20T210531Z-airy-saddle-discrepancy-kernel-route.md) — uniform post-turning saddle analysis; `SUPERSEDED` as active frontier.
- [`A-20260820-004`](../attempts/2026-08-20T212000Z-post-turning-phase-aware-discrepancy-route.md) — exact zero-mode response and phase-sensitive averaging barriers; `COMPLETE`.
- [`A-20260820-005`](../attempts/2026-08-20T221500Z-uniform-preturning-laguerre-phase-route.md) — exact uniform pre-turning phase and Cayley saddle structure; `COMPLETE`.
- [`A-20260820-006`](../attempts/2026-08-20T224400Z-prime-side-chirp-dirichlet-reduction.md) — endpoint closure and microlocal Dirichlet reduction; `COMPLETE`.
- [`A-20260821-001`](../attempts/2026-08-21T020900Z-global-bilinear-vaughan-chirp-route.md) — global Vaughan/Heath-Brown phase test; `COMPLETE` negative diagnostic.
- [`A-20260821-002`](../attempts/2026-08-21T022600Z-positivity-moment-weil-mechanism-audit.md) — Li Gram/CND audit and restricted-support Weil operator mechanism; `COMPLETE`.

The repository now contains ten retained computation records. No proof of RH has been obtained.

## Active leads

### L1 — First-prime Weil support continuation

**Status:** `ACTIVE / PRIMARY / NEXT`

The positivity audit found the first mechanism in this project with a genuinely unconditional base regime.

For logarithmic support

```text
supp f subset [-T,T],
```

the autocorrelation is supported in `[-2T,2T]`, so prime power `m` enters Weil's explicit-formula quadratic form only at

```text
T>(1/2)log m.
```

The prime-free regime is

```text
T<(1/2)log2.
```

Restricted-support archimedean Weil positivity is known unconditionally (`C-0041`).

The first arithmetic window is

```text
(1/2)log2 < T < (1/2)log3,
```

where only `m=2` is active.

On the standard constrained Weil space, the full operator has the form

```text
A_infinity(T)
- [log2/sqrt2] S_(T,log2),
```

where

```text
S_(T,a)=P_T(U_a+U_a^*)P_T.
```

Throughout this entire first-prime window,

```text
||S_(T,log2)||=1,
```

so the exact scalar size of the first arithmetic perturbation is

```text
log2/sqrt2
=0.4901290717... .
```

The next task is a **relative operator comparison**, not another global prime bound.

### L2 — Li Gram / moment formulations

**Status:** `CLOSED AS EQUIVALENT CRITERIA / AVAILABLE STRUCTURE`

The finite kernel

```text
K_jk=lambda_j+lambda_k-lambda_|j-k|
```

is a Gram matrix under RH, but

```text
K_nn=2lambda_n.
```

Hence

```text
RH <=> K^(N) PSD for every N.
```

The matrix criterion contains Li positivity directly on its diagonal (`C-0036`).

Likewise,

```text
psi(n)=lambda_|n|
```

is conditionally negative definite under RH, so

```text
exp[-t lambda_|n|]
```

is positive definite and gives a Herglotz probability-measure convolution semigroup. But the two-point CND test immediately gives `lambda_n>=0`, so this is again exactly RH (`C-0037`).

These formulations are structural tools, not independent progress toward RH.

### L3 — Prime/archimedean compensation in the generalized Li basis

**Status:** `STRUCTURAL OBSTRUCTION`

A single generalized prime-power atom contributes to the natural Li Gram kernel with

```text
K_11^(m)=-2A Lambda(m)m^(-s0)<0.
```

Thus the prime side is not a sum of positive Gram pieces (`C-0038`). Full positivity must come from compensation with pole/archimedean terms.

This supports the pivot toward Weil's full quadratic operator, where that compensation is explicit.

### L4 — Direct Li/Laguerre prime cancellation

**Status:** `BLOCKED AS CURRENT MECHANISM`

The earlier branch established:

- exact pole-subtracted discrepancy transform (`C-0010`, `C-0011`);
- explicit nonlinear critical-half-weight chirp (`C-0023`);
- fixed-interior microlocal Dirichlet reduction (`C-0028`);
- generic one-dimensional mean values leave positive exponential root growth (`C-0029`);
- finite multiplicative divisor decompositions preserve rank-one phase geometry (`C-0031`);
- dyadic Type-II chirp kernels are asymptotically separable (`C-0032`);
- direct magnitude estimates need essentially square-root saving (`C-0034`).

Therefore the conventional Vaughan/Heath-Brown phase route is closed as a demonstrably weaker mechanism (`C-0035`).

### L5 — Restricted Weil positivity / operator literature

**Status:** `AVAILABLE TOOLKIT`

Bombieri's Weil-functional work provides the variational/finite-truncation framework and restricted-support positivity. Connes-Consani give a conceptual archimedean positivity mechanism using compressed scaling, Sonin/prolate structure, and Hermitian Toeplitz matrices. Suzuki supplies a modern integral-operator/hermitian-form formulation.

These are the main external tools for the next attempt (`R-0024` through `R-0027`).

## Strongest verified intermediate results

1. `RH <=> limsup |S_n|^(1/n)<=1` for fixed `s0>1` (`C-0010`).
2. `S_n` is exactly the pole-subtracted `d(psi-x)` Laguerre transform (`C-0011`).
3. A single zero mode has exact response `z_rho^(-n)-1` (`C-0019`).
4. The uniform pre-turning stationary map is `u_gamma=A^2/(A^2+4gamma^2)` (`C-0021`).
5. The prime discrepancy is probed by a nonlinear critical-half-weight chirp (`C-0023`).
6. Direct fixed-interior prime magnitude estimates require square-root saving (`C-0034`).
7. Generic Vaughan/Heath-Brown phase decomposition is blocked (`C-0035`).
8. `K_jk=lambda_j+lambda_k-lambda_|j-k|` gives an exact Li Gram criterion, but it is immediately RH-equivalent (`C-0036`).
9. Li CND/Schoenberg-Herglotz structure is also exactly RH-equivalent (`C-0037`).
10. Natural generalized prime Gram atoms are not PSD (`C-0038`).
11. Weil prime powers enter at thresholds `T=(1/2)log m` as compressed translations (`C-0039`).
12. The first-prime compressed shift has exact norm `1` and perturbation size `log2/sqrt2` (`C-0040`).
13. Restricted-support Weil positivity provides a genuine unconditional base regime (`C-0041`).

## Computational observations

- `X-20260821-001` verified `1/n` dyadic bilinear phase separability and the `sqrt(n)` nonseparability scale.
- `X-20260821-002` checked the finite Li Gram/Schoenberg behavior on synthetic on-line/off-line orbits and the deterministic Weil support geometry.
- In the synthetic off-line quartet diagnostic (`r=1.2`, `theta=0.7`), the first negative Li coefficient occurred at `n=8`, and both Gram and Schoenberg matrices became indefinite.
- At `T=0.34`, no prime powers are active.
- At `T=0.45`, only `m=2` is active with compressed-shift norm `1` and scalar penalty `0.490129071734...`.
- At `T=0.60`, `m=2,3` are active; the crude sum of individual operator-norm penalties is `1.124413172332...`.

These are diagnostics only, not evidence for RH.

## Open requirements / blockers

The primary blocker is now sharply localized:

> Prove nonnegativity of the constrained first-prime Weil operator `A_infinity(T)-(log2/sqrt2)S_(T,log2)` for `(1/2)log2<T<(1/2)log3`, or identify the exact point/mechanism at which such continuation fails.

The crude sufficient condition

```text
lambda_min(A_infinity(T)) > log2/sqrt2
```

may be too strong. A successful proof should preferably exploit the **relative geometry** of the archimedean operator and the compressed shift.

## Invalidated, corrected, or closed directions

### I1 — Critical-line quartet contribution `8 sin^2(...)`

`INVALIDATED / CORRECTED`: correct distinct-pair contribution is `4 sin^2(n theta/2)`.

### I2 — Raw generalized prime trace is subexponential

`INVALIDATED / CORRECTED`: the zeta pole contributes the exact exponential mode `1-q^n`.

### I3 — Fixed pointwise PNT exponent above `1/2` closes the Laguerre transform

`CLOSED`: absolute values retain exponential growth.

### I4 — One narrow Airy window plus absolute bounds elsewhere

`INVALIDATED / REFINED`: pre-turning cross-region phase matters.

### I5 — Generic square-root dyadic mean-square bound as a weaker input

`CIRCULAR`: it already detects the RH zero boundary.

### I6 — Generic Montgomery-Vaughan / large-sieve control of independent chirp cells

`CLOSED`: exponential length term leaves root base greater than `1`.

### I7 — Vaughan/Heath-Brown divisor identities create a new multidimensional oscillatory phase

`CLOSED`: logarithmic Hessian remains rank one and dyadic boxes become asymptotically separable.

### I8 — Li Gram PSD is a new weaker positivity mechanism

`CLOSED AS EQUIVALENT`: `K_nn=2lambda_n`.

### I9 — Schoenberg/Herglotz positivity weakens Li's criterion

`CLOSED AS EQUIVALENT`: conditional negative definiteness already implies every `lambda_n>=0`.

### I10 — Prime-side Gram atoms are individually positive

`REFUTED IN NATURAL BASIS`: the first diagonal entry of every generalized prime atom is negative.

## Next research action

Create `A-20260821-003` for the **first-prime Weil support-continuation problem**:

1. fix the precise Bombieri/Connes-Consani normalization and the admissible pole-constraint subspace;
2. construct the constrained archimedean operator `A_infinity(T)` for `(1/2)log2<T<(1/2)log3`;
3. represent the only arithmetic perturbation as `(log2/sqrt2)S_(T,log2)`;
4. derive the relative operator `A_infinity(T)^(-1/2) S A_infinity(T)^(-1/2)` where justified;
5. use the Sonin/prolate/Toeplitz representation if it improves control;
6. build certified Galerkin lower bounds with python-flint/Arb and a rigorous truncation/tail estimate;
7. distinguish finite-dimensional certified positivity from the infinite-dimensional theorem;
8. if scalar gap comparison fails, identify whether the extremal direction is controlled by the pole constraints or by a low-dimensional relative-shift subspace.
