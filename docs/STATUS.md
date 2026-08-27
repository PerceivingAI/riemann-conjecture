# Current Research Status

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-27T16:55:13Z`
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
- [`A-20260826-001`](../attempts/2026-08-26T171400Z-one-prime-support-continuation.md) — one-prime support continuation from the verified `T=7/20` basepoint; moving Legendre dimension now yields independently verified theorems at `T=2/5,N=40`, `T=17/40,N=48`, `T=9/20,N=56`, and `T=19/40,N=68`; `PROMISING`.

The repository now contains nineteen retained computation records. No proof of RH has been obtained.

## Active leads

### L1 — Exact-prime localized Weil positivity and support continuation

**Status:** `VERIFIED THROUGH T=19/40`

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

The next support theorem is now also verified at

```text
T=9/20,
N=56.
```

`C-0053` uses a 512-bit full-tail assembly and a retained exact rational interval certificate. Rust independently derives

```text
mu_56 > 0.7060951994695617
even margin > 0.003888027441177187
odd  margin > 0.004366893328949625,
```

reconstructs the factor-3 Schur matrix, and returns `passed=true` with scope `localized_weil_positivity_T_9_20`. The real-certificate adversarial replay again distinguishes contract failure (exit `2`) from theorem failure (exit `1`).

The canonical continuation driver completed the `T=19/40=0.475` slice over the explicit range `N=48,52,...,80` in pre-theorem `X-20260827-001`. Precision escalation showed that `N=64` is genuinely negative under the present full-tail Schur reduction, while `N=68` stabilizes positive at 384 bits and reaches exact `CANDIDATE_READY`. A separate explicit admission then added only `(T,N)=(19/40,68)` to the closed v1 theorem contract. Fresh proof-bearing run `X-20260827-002` reassembled the certificate from scratch at 384-bit Arb precision with 64-bit outward matrix endpoints and 32-bit exact witnesses. The independent zero-float Rust verifier returns `passed=true` with scope `localized_weil_positivity_T_19_40`, deriving approximately

```text
mu_68       > 0.7185353202932019
even margin > 0.0013831260220094517
odd  margin > 0.006360318287493695.
```

Real-certificate adversarial replay again distinguishes contract failure (`factor=2`, exit `2`) from theorem failure (contract-valid negative diagonal perturbation, exit `1`). This establishes `F-20260827-001` / `C-0054`: strict localized Weil positivity at `T=19/40`.

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
21. The exact-prime Legendre-Schur mechanism, with 512-bit `N=56` assembly, proves strict localized Weil positivity at `T=9/20` under a fresh independently verified certificate (`C-0053`).
22. After the canonical pre-theorem boundary isolated `N=68`, explicit closed-contract admission plus a fresh 384-bit exact certificate and independent Rust replay prove strict localized Weil positivity at `T=19/40` (`C-0054`).

## Computational observations and certificates

- `X-20260821-001` checks dyadic bilinear phase separability.
- `X-20260821-002` checks Li Gram/Schoenberg synthetic examples and exact compressed-shift support geometry.
- `X-20260821-003` contains the exact rational first-prime absorption certificate and exact Arb constant enclosures.
- `X-20260821-004` contains the proof-path obstruction/complement certificate and a separately labeled floating Legendre-Schur dimension scout.
- `X-20260821-005` contains the clean exact-prime `N=32` Schur certificate, exact rational congruence witnesses, and independent Rust PASS for `C-0050`.
- `X-20260826-001` maps one-prime support continuation, records the moving-dimension diagnosis, and contains the proof-bearing exact `T=2/5,N=40` certificate plus independent Rust replay for `C-0051`.

- `X-20260826-002` contains the 384-bit `N=48` full-tail diagnostic, exact `T=17/40` certificate, adversarial checks, and independent Rust PASS for `C-0052`.

- `X-20260826-003` contains the 512-bit `N=56` full-tail diagnostic, exact `T=9/20` certificate, adversarial checks, and independent Rust PASS for `C-0053`.
- `X-20260827-001` contains the canonical pre-theorem `T=19/40` continuation bundle: `N=64` is precision-stable negative under the current Schur reduction, while `N=68` reaches generator-side exact `CANDIDATE_READY` at 384-bit precision. It remains non-proof-bearing; the later separate admission and independent replay are `X-20260827-002`.
- `X-20260827-002` contains the separately admitted fresh `T=19/40,N=68` theorem certificate, independent zero-float Rust PASS, adversarial replays, and full Python/Rust/Lean acceptance checks for `C-0054`.
- `X-20260827-003` records the non-proof-bearing zero-float Rust verifier optimization. Direct parity Schur construction plus lower-triangular/symmetric exact congruence reduces debug replay times to `3.564, 6.145, 13.210, 24.880, 31.408` seconds for `N=32,40,48,56,68`; all retained `C-0050` through `C-0054` verifier JSON objects match exactly after optimization.
- `computations/2026-08-27T151517Z-t1-2-continuation/` contains the current pre-theorem `T=1/2` frontier bundle. Floating reconnaissance over `N=56,60,...,104` classified `N=56..68` negative, `N=72` unstable, and `N=76..104` stable-positive. The primary rigorous target `N=76` did not become the selected exact candidate; fallback `N=80` stabilized positive at 512-bit Arb precision and its fixed 64-bit matrix / 32-bit witness candidate remained stable at 640 bits. The terminal state is `CANDIDATE_READY`. This bundle is non-proof-bearing: `(T,N)=(1/2,80)` has **not** been admitted to the closed theorem contract and has no theorem status.
- The closed exact-prime admission table now has a test-only cross-layer consistency corpus at `tests/data/exact-prime-admission-v1.json`. It exercises the independently hard-coded Python generator, Python semantic validator, raw JSON Schema, and Rust verifier admission logic over five allowed pairs, all twenty mixed cross-pairs, and five external forbidden cases. Production trust layers do not read this corpus, so decoupled verification is preserved while accidental whitelist drift becomes test-detectable.
- The canonical continuation driver is now `continuation-driver-p15-v1` with cache contract `continuation-driver-v6`. It retains the p14 conditioning observability and fixed-parameter candidate confirmation, and now uses bounded spawn-based process parallelism only across mathematically independent work: up to three floating-scout resolutions and up to two primary/fallback rigorous screens. Results are merged deterministically; each rigorous precision ladder, exact candidate construction, and candidate cross-precision confirmation remain sequential. Worker processes default BLAS/OpenMP-style thread counts to one unless explicitly overridden, and cache writes use process-unique temporary paths followed by atomic replacement. CLI defaults are `3/2`; programmatic `run_driver()` remains sequential by default and `--scout-workers 1 --rigorous-workers 1` forces sequential reproduction. Real historical multiprocessing acceptance passes `3/3` (`T=2/5`, `17/40`, `19/40`), and a parallel versus sequential `T=2/5` replay is semantically identical after removing execution-only metadata. Routine pytest now uses `pytest-xdist -n 2`; on the current 6-core Windows machine the 486-test default suite improved from about 559 seconds sequentially to about 378 seconds, while four workers only improved to about 372 seconds.
- `computations/retained-proofs.json` now provides a closed first-class retained-proof registry for exactly `C-0050` through `C-0054`. `scripts.cert.verify_retained_proofs` verifies each registered artifact's raw-byte SHA-256 before replay and then requires current `rh_cert` PASS plus exact theorem identity agreement. P8 independently recomputed all five raw-byte hashes from disk and found exact agreement with the manifest and historical records. P9 completed the full Python/Rust/Lean acceptance snapshot; the canonical five-artifact gate passes `5/5`, while a temporary tampered `C-0050` copy produces `HASH_MISMATCH`, skips Rust for that artifact, continues through `C-0051`–`C-0054`, and exits `1` with `FAIL - 4/5`. Temporary tamper files were removed and the originals rehashed cleanly. The registry remains explicit—no automatic computation-directory discovery—and stores no derived margin diagnostics.


`X-20260821-005`, `X-20260826-001`, `X-20260826-002`, `X-20260826-003`, and `X-20260827-002` are proof-bearing for the finite-support theorems `C-0050`, `C-0051`, `C-0052`, `C-0053`, and `C-0054`, respectively. Their exact certificates and independent replays are retained with hashes and reproduction commands. `X-20260827-001` remains explicitly pre-theorem and `X-20260827-003` is tooling/performance evidence only; neither is part of that proof-bearing set. None of these finite-support results constitutes a proof of RH.

## Open requirements / blockers

There is no remaining blocker for the fixed support target `T=7/20`; `A-20260821-004` is complete.

There is no remaining blocker at `T=2/5`; `C-0051` is independently verified.

There is no remaining blocker at `T=17/40`; `C-0052` is independently verified.

There is no remaining blocker at `T=9/20`; `C-0053` is independently verified.

There is no remaining blocker at `T=19/40`; `C-0054` is independently verified. The hard pre-theorem boundary worked as intended: `X-20260827-001` stopped at `CANDIDATE_READY`, and theorem status was granted only after the separate admission and proof-bearing `X-20260827-002` replay.

The exact Rust verifier performance blocker is now closed by `X-20260827-003`. The implementation still validates full certificate parity/symmetry, remains pure exact rational and zero-float, and preserves the closed-contract/error semantics, but constructs parity Schur blocks directly and exploits lower-triangular/symmetric congruence structure. The previously measured `N=32,40,48,56` debug replays improve from approximately `11,25,54,102` seconds to `3.564,6.145,13.210,24.880` seconds; `N=68` replays in `31.408` seconds. A second replay produces exact parsed-JSON equality against every retained `C-0050` through `C-0054` Rust output, and the real `C-0054` adversarial cases remain contract error `exit 2` versus theorem failure `exit 1`.

There is therefore no current verifier- or orchestration-performance blocker to continuing the one-prime route. The canonical pre-theorem frontier has reached `T=1/2,N=80` with `CANDIDATE_READY`, but that point remains deliberately outside the closed theorem whitelist pending a separate explicit admission decision and fresh proof-bearing replay. The eventual structural transition remains entry of the `p=3` compressed translation at `(1/2)log 3`, which requires a new mathematical/tooling phase rather than casually broadening the present one-prime driver.


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

Resume the canonical one-prime continuation at a deliberately selected larger support still below `(1/2)log 3`. Do not extrapolate the next dimension from `68`; let `scripts.weil_continuation_driver` perform fresh multi-resolution reconnaissance, rigorous precision classification, exact candidate construction, and the new fixed-parameter candidate cross-precision confirmation under the existing hard stop.

Keep `X-20260827-003` as the verifier-performance baseline. If verifier cost again becomes material at larger dimensions, profile first and preserve the same exact semantic regression corpus rather than changing certificate format preemptively. The eventual structural transition remains entry of the `p=3` compressed translation at `(1/2)log 3`.
