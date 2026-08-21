# Current Research Status

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-21T02:09:00Z`
- **RH status in this repository:** `UNRESOLVED`

This file is the maintained snapshot of the current research frontier. Historical reasoning belongs in timestamped attempt/finding/computation records and `LOG.md`.

## Current state

Seven formal research attempts are recorded:

- [`A-20260820-001`](../attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md) — generalized Li/Laguerre route; `BLOCKED`, with later corrections preserved.
- [`A-20260820-002`](../attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md) — exact zeta-pole subtraction and discrepancy criterion; `COMPLETE` intermediate target.
- [`A-20260820-003`](../attempts/2026-08-20T210531Z-airy-saddle-discrepancy-kernel-route.md) — uniform post-turning saddle analysis; `SUPERSEDED` as active frontier by later phase-sensitive work.
- [`A-20260820-004`](../attempts/2026-08-20T212000Z-post-turning-phase-aware-discrepancy-route.md) — region-splitting test, exact zero-mode response, and averaging barriers; `COMPLETE` intermediate target.
- [`A-20260820-005`](../attempts/2026-08-20T221500Z-uniform-preturning-laguerre-phase-route.md) — exact uniform pre-turning phase, stationary-frequency map, Cayley saddle structure, and coefficient-`L2` circularity guard; `COMPLETE` intermediate target.
- [`A-20260820-006`](../attempts/2026-08-20T224400Z-prime-side-chirp-dirichlet-reduction.md) — endpoint closure, microlocal Dirichlet-polynomial reduction, and generic one-dimensional mean-value barrier; `COMPLETE` intermediate target.
- [`A-20260821-001`](../attempts/2026-08-21T020900Z-global-bilinear-vaughan-chirp-route.md) — global Vaughan/Heath-Brown bilinear phase test; rank-one/separability and square-root-saving barriers; `COMPLETE` negative diagnostic.

The versioned Python environment, pytest/Hypothesis suite, and native Rust engine support nine retained computation records under [`../computations/`](../computations/).

No proof of RH has been obtained.

## Active frontier

### L1 — Mechanism pivot: positivity / moment-matrix structure

**Status:** `ACTIVE / PRIMARY / NEXT`

The direct Li/Laguerre prime-cancellation branch has now been pushed to a clear boundary. The exact Cayley/Laguerre sequence remains useful:

```text
RH <=> limsup |S_n|^(1/n) <= 1,
```

and a single zero mode contributes

```text
z_rho^(-n)-1.
```

But `A-006` and `A-20260821-001` show that direct prime-side magnitude estimates require essentially square-root cancellation at exponentially large prime scales, while standard multiplicative convolution identities do not create new independent oscillatory phase directions.

The next attempt should therefore change mechanism rather than further refactor `Lambda`.

Concrete target:

1. derive the exact generalized-Cayley moment sequence associated with the zero multiset;
2. determine the natural Toeplitz/Herglotz or Weil quadratic form built from those moments;
3. characterize precisely what positivity/positive-semidefiniteness means in terms of zeros lying on the critical line;
4. inspect the prime plus archimedean explicit-formula side for any structural positivity that is not merely an immediate restatement of RH;
5. stop immediately if the proposed PSD condition is just another equivalent criterion with no new unconditional mechanism.

### L2 — Direct Li/Laguerre prime cancellation

**Status:** `BLOCKED AS CURRENT PROOF MECHANISM / RESULTS RETAINED`

The authoritative prime-discrepancy transform is still

```text
S_n
= A integral x^(-s0)L_(n-1)^(1)(A log x)
    d(psi(x)-x),
A=2s0-1.
```

Established structural results remain valid:

- exact zeta-pole subtraction (`C-0009`-`C-0011`);
- exact zero-mode response (`C-0019`);
- uniform pre-turning stationary map (`C-0021`);
- critical-half-weight nonlinear chirp (`C-0023`);
- shrinking endpoint closure and prime-frequency cap (`C-0026`, `C-0027`);
- microlocal Dirichlet reduction (`C-0028`).

But the direct cancellation target now has two independent barriers:

1. matched local smooth cells are zero-sensitive (`C-0030`);
2. any direct fixed-interior magnitude estimate `X^(1-delta)` must have `delta>=1/2` to reach root `1` (`C-0034`).

No currently identified unconditional arithmetic input supplies that scale without approaching an RH-equivalent prime error estimate.

### L3 — Vaughan / Heath-Brown finite convolution route

**Status:** `CLOSED AS NEW PHASE MECHANISM`

For a finite factorization

```text
m=a_1...a_k,
r_j=log a_j,
```

the phase is

```text
F_k(r_1,...,r_k)=Phi_n(r_1+...+r_k)
```

and

```text
Hess F_k=Phi_n'' 1 1^T.
```

Thus its logarithmic Hessian has rank at most one (`C-0031`). The `k-1` directions preserving the product are phase-flat.

On standard dyadic Type-II boxes,

```text
|Delta F|=O(1/n),
```

so the kernel is asymptotically separable (`C-0032`). Generic arbitrary-coefficient bilinear estimates therefore cannot obtain exponential saving from this phase alone.

Balanced `O(1)` cross-phase coupling first appears on factor log-widths of order `sqrt(n)` (`C-0033`), but this does not create exponentially many independent oscillations. The formal total pre-turning phase excursion is only `pi n`.

Further finite divisor identities are not a justified next step unless a genuinely new arithmetic mechanism is identified.

### L4 — Generic one-dimensional mean values / large sieve

**Status:** `CLOSED AS SOLE MECHANISM`

`A-006` established that a fixed-interior chirp cell has exponentially long Dirichlet-polynomial length

```text
N=exp(4n*u/A+o(n)),
```

while the available Mellin-frequency range is subexponential. The Montgomery-Vaughan length term therefore leaves RMS root base

```text
exp(2u/A)>1
```

(`C-0029`).

### L5 — Left endpoint / high-frequency prime side

**Status:** `CLOSED AS PRIMARY BLOCKER / AVAILABLE BOUNDS`

Actual prime atoms begin at

```text
u_2=A log 2/(4n),
```

so their maximum local Mellin frequency is only

```text
gamma_2(n)~sqrt(A n/log 2)=O(sqrt(n)).
```

The deterministic interval `[1,2)` is polynomially bounded and every shrinking `u=o(1)` endpoint is subexponential (`C-0026`, `C-0027`).

### L6 — Far post-turning tail

**Status:** `CLOSED / AVAILABLE BOUND`

Any fixed region beyond the post-turning root-one crossing is exponentially suppressed using uniform Laguerre decay and only the ordinary PNT (`C-0018`).

## Strongest verified intermediate results

1. `RH <=> limsup |S_n|^(1/n)<=1` for every fixed `s0>1` (`C-0010`).
2. `S_n` is exactly the pole-subtracted `d(psi-x)` Laguerre transform (`C-0011`).
3. A single zero mode has exact response `z_rho^(-n)-1` (`C-0019`).
4. The uniform pre-turning stationary map is `u_gamma=A^2/(A^2+4gamma^2)` (`C-0021`).
5. A fixed critical-line saddle reproduces the Cayley phase with unit leading normalization (`C-0022`).
6. The prime discrepancy is probed by a nonlinear chirp at the critical half-weight (`C-0023`).
7. Coefficient-block `L2` root control is RH-equivalent (`C-0024`).
8. Every shrinking left endpoint is subexponential, and `[1,2)` is polynomially bounded (`C-0026`).
9. Actual prime atoms sample only `O(sqrt(n))` Mellin frequencies (`C-0027`).
10. A fixed-interior chirp cell reduces to a smooth critical-half-weight prime Dirichlet polynomial (`C-0028`).
11. Classical one-dimensional mean values retain a positive exponential root base (`C-0029`).
12. Uniform independent subexponential control of matched local cells is zero-sensitive (`C-0030`).
13. Every finite multiplicative convolution preserves rank-one phase geometry (`C-0031`).
14. Standard dyadic Type-II chirp kernels are asymptotically separable (`C-0032`).
15. Balanced bilinear nonseparability begins only at `sqrt(n)` logarithmic scale; total formal phase excursion is `pi n` (`C-0033`).
16. Direct prime magnitude estimates require square-root saving `delta>=1/2` (`C-0034`).
17. The generic Vaughan/Heath-Brown phase route is blocked (`C-0035`).

## Computational observations

- `X-005` quantified phase loss caused by absolute values.
- `X-006` reproduced exact single-zero transforms and cross-region cancellation.
- `X-007` checked the uniform stationary map and Cayley phase on numerical zero ordinates.
- `X-008` checked prime-frequency caps, chirp-cell scales, and the one-dimensional mean-value root barrier.
- `X-20260821-001` checks dyadic bilinear cross defects and `sqrt(n)` nonseparability scales.
- At `s0=3`, `u=0.25`, the dyadic four-corner defect decreases from about `2.709e-2` at `n=256` to `6.772e-3` at `n=1024` and `1.693e-3` at `n=4096`, matching `1/n` scaling.
- The formal pre-turning phase count is exactly `n/2`; `X-20260821-001` returns `512` cycles at `n=1024`.

These are diagnostics only, not proof claims.

## Primary blocker

The Li/Laguerre prime route is now blocked at an RH-scale arithmetic boundary:

> Direct fixed-interior magnitude control requires essentially square-root cancellation at `X=exp(cn)`, while finite multiplicative divisor decompositions preserve a rank-one, asymptotically separable phase and do not supply that saving through new oscillatory dimensions.

Continuing to refactor `Lambda` without a new mechanism would risk producing further equivalent restatements rather than proof progress.

## Invalidated, corrected, or closed directions

### I1 — Critical-line quartet contribution `8 sin^2(...)`

**Status:** `INVALIDATED / CORRECTED`

Correct distinct-pair contribution: `4 sin^2(n theta/2)`.

### I2 — Move the Li center right for arbitrarily stronger prime decay

**Status:** `CLOSED`

Fixed-prime Laguerre asymptotics restore the half-weight.

### I3 — Raw generalized prime trace is subexponential

**Status:** `INVALIDATED`

The raw trace contains the deterministic zeta-pole mode.

### I4 — Finish with a fixed pointwise PNT exponent above `1/2`

**Status:** `CLOSED AS SOLE MECHANISM`

Absolute-value insertion leaves exponential growth.

### I5 — Reduce to a single narrow Airy window

**Status:** `INVALIDATED / REFINED`

Cross-region phase matters; only the sufficiently far tail closes independently.

### I6 — Use RH-scale dyadic mean square as a weaker input

**Status:** `CIRCULAR`

It already forces the RH zero boundary.

### I7 — Treat `A^2/(4gamma^2)` as the uniform stationary map

**Status:** `CORRECTED / ASYMPTOTIC ONLY`

Exact map: `A^2/(A^2+4gamma^2)`.

### I8 — Treat `gamma~n` as the main discrete-prime endpoint difficulty

**Status:** `REFINED / CLOSED AS PRIMARY BLOCKER`

Actual prime atoms only reach `O(sqrt(n))` frequencies.

### I9 — Generic one-dimensional Montgomery-Vaughan mean values

**Status:** `CLOSED AS SOLE MECHANISM`

The length term leaves a positive exponential root base.

### I10 — Prove every microlocal cell independently subexponential

**Status:** `TOO STRONG / ZERO-SENSITIVE`

Matched cells directly detect right-of-line zeros.

### I11 — Obtain the missing saving from Vaughan/Heath-Brown phase geometry

**Status:** `CLOSED AS NEW PHASE MECHANISM`

Finite multiplicative convolutions retain rank-one logarithmic phase geometry; dyadic Type-II boxes are asymptotically separable and direct magnitude estimates still require square-root saving.

## Next research action

Create `A-20260821-002` for a **positivity / moment-matrix mechanism audit**:

1. define the generalized Cayley moments of the zero multiset with the same regularization used by the Li coefficients;
2. derive the Toeplitz/Herglotz moment matrices or the corresponding Weil quadratic form;
3. prove exactly which positivity condition is equivalent to all zero images lying on the unit circle;
4. derive the explicit prime plus archimedean form for finite quadratic test vectors;
5. search for a structural Gram/sum-of-squares decomposition or other unconditional positivity mechanism;
6. apply a strict circularity check: if the PSD condition is simply another immediate RH equivalent with no weaker verifiable subclaim, record that and do not count it as progress.
