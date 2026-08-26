# Current Research Status

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-26T18:31:25Z`
- **RH status in this repository:** `UNRESOLVED`

This file is the maintained snapshot of the current research frontier. Historical reasoning belongs in timestamped attempt/finding/computation records and `LOG.md`.

## Current state

Eleven formal research attempts are recorded:

- [`A-20260820-001`](../attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md) — generalized Li/Laguerre route; `BLOCKED`, with later corrections preserved.
- [`A-20260820-002`](../attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md) — exact zeta-pole subtraction and discrepancy criterion; `COMPLETE` intermediate target.
- [`A-20260820-003`](../attempts/2026-08-20T210531Z-airy-saddle-discrepancy-kernel-route.md) — uniform post-turning saddle analysis; `SUPERSEDED` as active frontier.
- [`A-20260820-004`](../attempts/2026-08-20T212000Z-post-turning-phase-aware-discrepancy-route.md) — exact zero-mode response and phase-sensitive averaging barriers; `COMPLETE`.
- [`A-20260820-005`](../attempts/2026-08-20T221500Z-uniform-preturning-laguerre-phase-route.md) — exact uniform pre-turning phase and Cayley saddle structure; `COMPLETE`.
- [`A-20260820-006`](../attempts/2026-08-20T224400Z-prime-side-chirp-dirichlet-reduction.md) — endpoint closure and microlocal Dirichlet reduction; `COMPLETE`.
- [`A-20260821-001`](../attempts/2026-08-21T020900Z-global-bilinear-vaughan-chirp-route.md) — global Vaughan/Heath-Brown phase test; `COMPLETE` negative diagnostic.
- [`A-20260821-002`](../attempts/2026-08-21T022600Z-positivity-moment-weil-mechanism-audit.md) — Li Gram/CND audit and restricted-support Weil operator mechanism; `COMPLETE`.
- [`A-20260821-003`](../attempts/2026-08-21T040654Z-first-prime-weil-support-continuation.md) — exact first-prime endpoint absorption, finite-support normalization guard, and external FP-0.35 source audit; `COMPLETE` intermediate target.
- [`A-20260821-004`](../attempts/2026-08-21T085252Z-exact-prime-legendre-schur-certificate.md) — exact-prime Legendre-Schur route; global 69% absorption is refuted as too lossy, while the exact-prime `N=32` Schur certificate proves strict localized Weil positivity at `T=7/20`; `COMPLETE`.
- [`A-20260826-001`](../attempts/2026-08-26T171400Z-one-prime-support-continuation.md) — one-prime support continuation from the verified `T=7/20` basepoint; moving Legendre dimension now yields independently verified theorems at `T=2/5,N=40` and `T=17/40,N=48`; continuation toward `T=9/20` remains active; `PROMISING`.

The repository now contains fifteen retained computation records. No proof of RH has been obtained.

## Active leads

### L1 — Exact-prime localized Weil positivity and support continuation

**Status:** `VERIFIED BASEPOINT / ACTIVE CONTINUATION FRONTIER`

`A-20260821-004` has now achieved its finite-support success target.

At

```text
T=7/20,
```

Suzuki's full scaled localized Weil form, including the exact `p=2` compressed translation and the mandatory residual kernel, is strictly positive (`C-0050`).

The proof uses the exact Legendre jump spectrum

```text
J(P_n)=H_n||P_n||^2,
```

and the complement lower bound

```text
C_32 >= mu_32 I,
mu_32=H_32-c_T-c_2-rho_R,
```

with the clean certificate proving

```text
mu_32 > 0.8709101235096008.
```

The infinite low-to-tail coupling is reduced by `C-0048` to

```text
S_32=A_32-(3/mu_32)(G_V+G_2+G_R).
```

`X-20260821-005` rigorously encloses all four finite matrices, outward-rounds them to exact rational intervals, and uses the closed certificate profile

```text
exact_prime_legendre_schur.
```

The independent zero-float Rust verifier reconstructs the Schur matrix and proves the even/odd parity blocks positive by exact rational congruence and interval Gershgorin, with retained lower margins approximately

```text
even > 0.01153505500311919
odd  > 0.04939032559587724.
```

The retained certificate was regenerated from clean commit

```text
d620aa649a2d0291e407d4c0c8bc7360b67efc38
```

with `git_dirty=false`. The Lean soundness layer for Gershgorin dominance and invertible congruence also builds successfully.

The earlier theorem

```text
V+P_2 >= (69/100)V
```

remains verified (`C-0042`), but `C-0046` proves that using it globally is too lossy. The successful theorem retains the exact first-prime geometry.

`A-20260826-001` has now mapped the first continuation slice. With the rigorous full-tail formulas, fixed `N=32` remains positive in midpoint reconnaissance through the tested `T=0.37` but its Schur midpoint fails at `T=0.375` while the low block and complement remain positive. Increasing to `N=40` restores positive full-tail Schur midpoints at `T=3/8` and `T=2/5`.

The next support theorem is now verified at

```text
T=2/5,
N=40.
```

`C-0051` uses a full exact rational interval certificate. Rust independently derives

```text
mu_40 > 0.7313021813837909
even margin > 0.004176569432300938
odd  margin > 0.013120531611009081,
```

reconstructs the factor-3 Schur matrix, and returns `passed=true` with scope `localized_weil_positivity_T_2_5`. The real-certificate adversarial replay distinguishes contract failure (exit `2`) from theorem failure (exit `1`).

The next support theorem is now also verified at

```text
T=17/40,
N=48.
```

`C-0052` uses a 384-bit full-tail assembly and a retained exact rational interval certificate. Rust independently derives

```text
mu_48 > 0.7326484380944506
even margin > 0.0028958690673761525
odd  margin > 0.010715413283695166,
```

reconstructs the factor-3 Schur matrix, and returns `passed=true` with scope `localized_weil_positivity_T_17_40`. The real-certificate adversarial replay again distinguishes contract failure (exit `2`) from theorem failure (exit `1`).

The active frontier has therefore moved to `T=9/20=0.45`, where earlier reconnaissance suggests that roughly `N=56` may be required. No theorem is claimed there yet.

### L2 — Exact transcendental interval inputs

**Status:** `CLOSED / AVAILABLE TOOL`

At `T=7/20`, `X-20260821-003` records 256-bit Arb enclosures for

```text
tau=log2/T,
c_2=log2/sqrt2,
c_T=log(2*pi*T)+EulerGamma.
```

Selected values are

```text
tau
= [1.98042051588555802690637748988050448021571466960072929748766 +/- 2.84e-60]

c_2
= [0.490129071734273595856950861817616690645730349549527360521123 +/- 1.24e-61]

c_T
= [1.36527060681220065583730073019427666472543738980832338274545 +/- 2.56e-60].
```

These are scalar inputs only; they do not certify the full operator.

### L3 — Positive-kernel decomposition of the digamma multiplier

**Status:** `ACTIVE TOOL / COMPONENT ONLY`

Let

```text
a_k=k+1/4,
m_0=psi(1/4)-log pi.
```

Then (`C-0043`)

```text
Re psi(1/4+i xi/2)-log pi
=m_0
+sum_(k>=0)
 [1/a_k - 4a_k/(xi^2+4a_k^2)].
```

Under the repository Fourier convention, each summand contributes

```text
(1/a_k)||f||_2^2
- double_integral exp(-2a_k|t-s|)
    f(t)conj(f(s)) dt ds,
```

which is nonnegative. Finite partial sums therefore give monotone lower bounds for the pure digamma-multiplier component.

This may be useful for the residual certificate, but it is **not** the whole finite-support Weil operator.

### L4 — Mandatory finite-support residual kernel

**Status:** `CORRECTNESS GUARD`

Suzuki's exact localized form contains, in addition to the digamma multiplier and finite prime-power symbol, a separate finite-support residual kernel (`C-0044`). In the scaled formula it appears as a double-integral residual term.

Any finite-dimensional scout or certificate that omits this term is rejected as a model of the full localized Weil form.

An exploratory sine-Galerkin calculation created during `A-20260821-003` was deleted before registration after this guard exposed the omission. No eigenvalue from that scout is retained as evidence.

### L5 — Public FP-0.35 certificate project

**Status:** `EXTERNAL / UNVERIFIED / BLUEPRINT ONLY`

The public `telleroutlook/weil-first-prime` repository claims strict finite-scale positivity at `T=7/20`. The pinned source audit in `A-20260821-003` does not accept that theorem as verified here.

At pinned commit

```text
e66f467bc4447c5b2491577cbb6c3ae0e721fb43
```

the inspected source paths are not a single internally consistent exact full-`c_T` replay:

- the advertised replay injects point approximations for `tau` and `c_2` into Arb;
- the full-`c_T` recomputation path uses floating `tau`, floating `c_2`, and a numerical LDL pivot;
- the exact-prime path sets `c_L=0`, so it is the easier O1-B gate rather than the full FP-0.35 form;
- lower-level source comments still distinguish interim interval-LDL machinery from the intended final exact certification;
- the repository README simultaneously reports FP-0.35 as holding while listing the trusted replay/release chain as in progress.

This is a source-audit conclusion only. It does **not** assert FP-0.35 is false.

The external code may be mined for proof architecture, but theorem status is not imported.

### L6 — Li/Laguerre direct prime cancellation

**Status:** `BLOCKED AS CURRENT MECHANISM`

The earlier branch remains mathematically useful but blocked at an essentially square-root prime-cancellation requirement. The most important retained facts are:

- exact pole-subtracted `d(psi-x)` transform (`C-0010`, `C-0011`);
- exact single-zero response (`C-0019`);
- explicit critical-half-weight nonlinear chirp (`C-0023`);
- direct fixed-interior magnitude estimates require square-root saving (`C-0034`);
- finite multiplicative divisor decompositions preserve rank-one phase geometry (`C-0031`);
- generic Vaughan/Heath-Brown phase decomposition is blocked (`C-0035`).

## Strongest verified intermediate results

1. `RH <=> limsup |S_n|^(1/n)<=1` for fixed `s0>1` (`C-0010`).
2. `S_n` is exactly the pole-subtracted `d(psi-x)` Laguerre transform (`C-0011`).
3. A single zero mode has exact response `z_rho^(-n)-1` (`C-0019`).
4. The uniform pre-turning stationary map is `u_gamma=A^2/(A^2+4gamma^2)` (`C-0021`).
5. Direct fixed-interior prime magnitude estimates require square-root saving (`C-0034`).
6. Generic Vaughan/Heath-Brown phase decomposition is blocked (`C-0035`).
7. Li Gram and Schoenberg/Herglotz positivity formulations are exact RH equivalents, not weaker mechanisms (`C-0036`, `C-0037`).
8. Prime powers enter the localized Weil form as thresholded compressed translations (`C-0039`).
9. The first-prime compressed shift has exact norm `1` throughout its support window (`C-0040`).
10. Restricted-support Weil positivity gives a genuine unconditional base regime (`C-0041`).
11. At `T=7/20`, the first-prime endpoint term is absorbed rigorously: `V+P_2 >= (69/100)V` (`C-0042`).
12. The pure digamma multiplier admits monotone nonnegative-kernel lower bounds (`C-0043`).
13. The finite-support residual kernel is mandatory in any full localized Weil computation (`C-0044`).
14. The logarithmic jump form is Legendre-diagonal with harmonic-number coercivity on high modes (`C-0045`).
15. The globally absorbed `0.69V` residual operator is rigorously not positive; the endpoint theorem remains valid but is too lossy for this use (`C-0046`).
16. The exact-prime Legendre complement has a rigorous positive lower bound already from `N=14` (`C-0047`).
17. Full exact-prime positivity reduces to a finite component tail-Gram Schur condition (`C-0048`).
18. Suzuki's full localized Weil quadratic form is strictly positive at `T=7/20`, with an independently verified exact-prime `N=32` Schur certificate (`C-0050`).
19. The same exact-prime Legendre-Schur mechanism, with `N=40`, proves strict localized Weil positivity at `T=2/5` under a fresh independently verified certificate (`C-0051`).
20. The exact-prime Legendre-Schur mechanism, with high-precision `N=48` assembly, proves strict localized Weil positivity at `T=17/40` under a fresh independently verified certificate (`C-0052`).
## Computational observations and certificates

- `X-20260821-001` checks dyadic bilinear phase separability.
- `X-20260821-002` checks Li Gram/Schoenberg synthetic examples and exact compressed-shift support geometry.
- `X-20260821-003` contains the exact rational first-prime absorption certificate and exact Arb constant enclosures.
- `X-20260821-004` contains the proof-path obstruction/complement certificate and a separately labeled floating Legendre-Schur dimension scout.
- `X-20260821-005` contains the clean exact-prime `N=32` Schur certificate, exact rational congruence witnesses, and independent Rust PASS for `C-0050`.
- `X-20260826-001` maps one-prime support continuation, records the moving-dimension diagnosis, and contains the proof-bearing exact `T=2/5,N=40` certificate plus independent Rust replay for `C-0051`.

- `X-20260826-002` contains the 384-bit `N=48` full-tail diagnostic, exact `T=17/40` certificate, adversarial checks, and independent Rust PASS for `C-0052`.

`X-20260821-005`, `X-20260826-001`, and `X-20260826-002` are proof-bearing for the finite-support theorems `C-0050`, `C-0051`, and `C-0052`, respectively. Their exact certificates and independent replays are retained with hashes and reproduction commands. None of these finite-support computations constitutes a proof of RH.

## Open requirements / blockers

There is no remaining blocker for the fixed support target `T=7/20`; `A-20260821-004` is complete.

There is no remaining blocker at `T=2/5`; `C-0051` is independently verified.

There is no remaining blocker at `T=17/40`; `C-0052` is independently verified.

The primary open requirement is now the next continuation target

```text
T=9/20=0.45.
```

Earlier stable reconnaissance suggests `N~56`. The next slice must:

1. run the full-tail exact-polynomial/Arb assembly at `T=9/20,N=56` with enough precision to defeat the known high-degree monomial-conditioning problem;
2. require a positive rigorous complement bound and positive full-tail Schur candidate after outward rational rounding;
3. construct exact rational parity congruence witnesses only if that candidate survives;
4. if successful, add only the single `(T,N)=(9/20,56)` pair to the closed whitelist and require a fresh independent Rust replay;
5. if it fails, determine whether the failure is precision/conditioning, dimension, or a genuine loss of the current Schur bound before moving farther toward `(1/2)log 3`.


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

### I8 — Li Gram or Schoenberg positivity is a weaker criterion

`CLOSED AS EQUIVALENT`: both immediately contain Li positivity.

### I9 — Prime-side Gram atoms are individually positive

`REFUTED IN NATURAL BASIS`: their first diagonal entry is negative.

### I10 — Digamma multiplier minus `p=2` is the full first-prime Weil operator

`INVALIDATED / NORMALIZATION ERROR`: Suzuki's localized formula contains an additional residual kernel.

### I11 — A positive finite Galerkin matrix proves first-prime positivity

`INVALIDATED AS SUFFICIENT EVIDENCE`: a rigorous infinite-dimensional complement bound is mandatory.

### I12 — Import the public FP-0.35 repository's PASS status

`REJECTED AS PROOF DEPENDENCY`: the public source tree remains useful architecture but was not imported as theorem evidence. `C-0050` is instead established by this repository's independent exact certificate and replay.

### I13 — Use `V+P_2 >= (69/100)V` globally and prove the remaining residual operator positive

`REFUTED AS SUFFICIENT LOWER TARGET`: `C-0042` remains correct, but `C-0046` gives the explicit polynomial `P_0-P_2` on which the resulting lower operator is strictly negative. The successful proof of `C-0050` retains the exact-prime translation more faithfully.

## Next research action

Continue `A-20260826-001` at the next candidate support `T=9/20`, starting with a high-precision full-tail `N=56` exact candidate check.

Do not extrapolate `C-0052` from `T=17/40`. Any theorem at `T=9/20` must come from a fresh exact certificate and independent replay under an explicitly whitelisted pair. The eventual structural transition remains the entry of the `p=3` compressed translation at `(1/2)log 3`.
