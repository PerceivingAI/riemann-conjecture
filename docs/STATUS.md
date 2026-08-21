# Current Research Status

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-21T08:56:20Z`
- **RH status in this repository:** `UNRESOLVED`

This file is the maintained snapshot of the current research frontier. Historical reasoning belongs in timestamped attempt/finding/computation records and `LOG.md`.

## Current state

Ten formal research attempts are recorded:

- [`A-20260820-001`](../attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md) — generalized Li/Laguerre route; `BLOCKED`, with later corrections preserved.
- [`A-20260820-002`](../attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md) — exact zeta-pole subtraction and discrepancy criterion; `COMPLETE` intermediate target.
- [`A-20260820-003`](../attempts/2026-08-20T210531Z-airy-saddle-discrepancy-kernel-route.md) — uniform post-turning saddle analysis; `SUPERSEDED` as active frontier.
- [`A-20260820-004`](../attempts/2026-08-20T212000Z-post-turning-phase-aware-discrepancy-route.md) — exact zero-mode response and phase-sensitive averaging barriers; `COMPLETE`.
- [`A-20260820-005`](../attempts/2026-08-20T221500Z-uniform-preturning-laguerre-phase-route.md) — exact uniform pre-turning phase and Cayley saddle structure; `COMPLETE`.
- [`A-20260820-006`](../attempts/2026-08-20T224400Z-prime-side-chirp-dirichlet-reduction.md) — endpoint closure and microlocal Dirichlet reduction; `COMPLETE`.
- [`A-20260821-001`](../attempts/2026-08-21T020900Z-global-bilinear-vaughan-chirp-route.md) — global Vaughan/Heath-Brown phase test; `COMPLETE` negative diagnostic.
- [`A-20260821-002`](../attempts/2026-08-21T022600Z-positivity-moment-weil-mechanism-audit.md) — Li Gram/CND audit and restricted-support Weil operator mechanism; `COMPLETE`.
- [`A-20260821-003`](../attempts/2026-08-21T040654Z-first-prime-weil-support-continuation.md) — exact first-prime endpoint absorption, finite-support normalization guard, and external FP-0.35 source audit; `COMPLETE` intermediate target.
- [`A-20260821-004`](../attempts/2026-08-21T085252Z-exact-prime-legendre-schur-certificate.md) — exact-prime Legendre-Schur route; the uniform 69% residual target is rigorously refuted, while high-mode complement coercivity and a finite Schur reduction make the exact-prime route `PROMISING`.

The repository now contains twelve retained computation records. No proof of RH has been obtained.

## Active leads

### L1 — Exact-prime Legendre-Schur certificate at `T=7/20`

**Status:** `ACTIVE / PRIMARY / PROMISING`

The current primary route is finite-scale and deliberately does **not** claim an RH implication.

`A-20260821-004` has materially changed the target. The exact endpoint inequality

```text
V+P_2 >= (69/100)V
```

remains verified (`C-0042`), but using it globally is too lossy: the explicit polynomial

```text
w=P_0-P_2=(3/2)(1-x^2)
```

rigorously satisfies

```text
J(w)+(69/100)V(w)+R_T(w)-c_T||w||^2 < 0
```

(`C-0046`). Therefore the former plan to prove the globally absorbed residual operator positive is closed.

The new route retains the **exact** `p=2` compressed translation in the low-mode block. The jump component has the exact Legendre spectrum

```text
J(P_n)=H_n||P_n||^2,
H_n=sum_(k=1)^n 1/k,
```

so the complement above the first `N` modes obeys `J>=H_N I` (`C-0045`). With the prime norm and a rigorous Schur bound for Suzuki's residual,

```text
C_N >= mu_N I,
mu_N=H_N-c_T-c_2-rho_R.
```

`X-20260821-004` certifies `mu_14>0` (`C-0047`). Thus high modes are already rigorously coercive.

Writing the cross block as `B_V+B_2+B_R`, full positivity follows from the finite sufficient condition

```text
A_N-(3/mu_N)(G_V+G_2+G_R)>0,
G_X=P_N X Q_N X P_N
   =P_N X^2 P_N-(P_N X P_N)^2.
```

This reduction is rigorous (`C-0048`). Floating reconnaissance with finitely truncated tail Grams becomes positive near `N=28`; `N=32` is the recommended first rigorous target (`C-0049`).

The immediate research task is therefore to enclose `A_32`, `G_V`, `G_2`, and `G_R` rigorously and certify the finite Schur matrix. The certificate contract should be extended only after those mathematical semantics are fixed.

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

## Computational observations and certificates

- `X-20260821-001` checks dyadic bilinear phase separability.
- `X-20260821-002` checks Li Gram/Schoenberg synthetic examples and exact compressed-shift support geometry.
- `X-20260821-003` contains the exact rational first-prime absorption certificate and exact Arb constant enclosures.
- `X-20260821-004` contains the proof-path obstruction/complement certificate and a separately labeled floating Legendre-Schur dimension scout.

The exact rational certificate is a proof of `C-0042`; the Arb constants are certified scalar enclosures. Neither constitutes a proof of full first-prime positivity.

## Open requirements / blockers

The primary blocker is now:

> Prove the exact-prime component tail-Gram Schur matrix at `T=7/20` positive, using the already-certified high-mode Legendre complement bound and rigorous infinite-tail Gram enclosures.

Required pieces:

1. rigorous `N=32` low matrix `A_N` with exact endpoint, exact `p=2` translation, Suzuki residual, jump diagonal, and `c_T`;
2. rigorous finite matrix `G_V=P_N V Q_N V P_N`, preferably via `P_NV^2P_N-(P_NVP_N)^2`;
3. rigorous `G_2` from the explicit compressed-shift overlap geometry;
4. rigorous `G_R`, using the residual series structure plus a certified analytic tail bound;
5. propagation of the certified `mu_N` interval into the factor-3 Schur correction;
6. exact-rational/interval positive-definiteness verification with a margin surviving all interval widths;
7. only after these semantics are fixed, a closed `rh-weil-certificate-v1` exact-prime Schur profile;
8. no reliance on a positive finite Ritz matrix or a finitely truncated tail Gram alone.

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

`REJECTED AS PROOF DEPENDENCY`: the current public source tree is useful architecture but has not passed this repository's independent exact replay standard.

### I13 — Use `V+P_2 >= (69/100)V` globally and prove the remaining residual operator positive

`REFUTED AS SUFFICIENT LOWER TARGET`: `C-0042` remains correct, but `C-0046` gives the explicit polynomial `P_0-P_2` on which the resulting lower operator is strictly negative. The exact-prime translation must be retained more faithfully.

## Next research action

Continue `A-20260821-004` with a rigorous **exact-prime `N=32` Legendre-Schur certificate**:

1. retain Suzuki's full scaled form and the exact `p=2` translation;
2. assemble `A_32` with Arb interval entries;
3. derive and enclose `G_V=P_32 V Q_32 V P_32` using finite `log^2(1-x^2)` moments;
4. derive and enclose `G_2` from exact shifted-polynomial overlap integrals;
5. derive `G_R` from the Suzuki residual series plus a rigorous operator/matrix tail bound;
6. use the certified `mu_32` complement lower bound and form `A_32-(3/mu_32)(G_V+G_2+G_R)`;
7. require positive definiteness to survive all Arb widths and rational outward rounding;
8. only then add a closed exact-prime Schur profile to `rh-weil-certificate-v1` and verify it independently in Rust;
9. if successful, record only finite-scale positivity at `T=7/20` — not RH.
