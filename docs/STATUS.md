# Current Research Status

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-10-08T03:44:13Z`
- **RH status in this repository:** `UNRESOLVED`

This file is the maintained snapshot of the current research frontier. Historical reasoning belongs in timestamped attempt/finding/computation records and `LOG.md`.

**OpenAI Math assimilation OAI-0 — `2026-10-07T10:06:02Z`.** External provenance is frozen for OpenAI's quasi-Riemann theorem as `EXT-0001`. The upstream source is pinned to `openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`; the exact Lean theorem, Comparator configuration, Lean 4.34.1 toolchain, Mathlib revision, Apache-2.0 license, manuscript citation metadata, and source blob identities are recorded in `references/external-results/EXT-0001-openai-quasi-rh.md`, with bibliography entry `R-0034`. OAI-0 is provenance only: no OpenAI source has been vendored, no repository `C-` claim has been assigned, no theorem/certificate admission changed, and independent replay was then pending OAI-1 (**dated OAI-0 snapshot**; later OAI-2 made the replay optional, and it remains **NOT PERFORMED**).

**OpenAI mathematical dependency OAI-2 — `2026-10-08T01:42:58Z`.** Independent Comparator replay is optional rather than a prerequisite for mathematical use of the clearly attributed external theorem `EXT-0001`. An isolated, clean, detached upstream checkout has been checked against the pinned commit/tree and eight selected source-blob identities; this is source integrity, not an independently verified proof replay. The exact deduction `C-0060` / `F-20261008-001` places nontrivial zeta zeros in `1/8<=Re(rho)<=7/8` and bounds the fixed-center pole-subtracted Laguerre coefficient root by `(s0-1/8)/(s0-7/8)>1`. Hence it does **not** satisfy the `C-0010` RH criterion, establish the square-root prime-cancellation input, or change localized Weil positivity/admission. Preliminary route impacts are in the finding; full individual OAI-4 route audits remain separate.

**OpenAI/Mathlib overlap OAI-3 — `2026-10-08T01:58:15Z`.** The source-grounded inventory in [`EXT-0001-lean-overlap-audit.md`](../references/external-results/EXT-0001-lean-overlap-audit.md) separates existing Mathlib machinery (Mangoldt/zeta log derivatives, zeta analyticity, `Re(s)≥1` nonvanishing, Gershgorin and finite Schur algebra), useful new OpenAI `Re(s)>7/8` nonvanishing, unrelated qualitative/number-field modules, and the high-cost OpenAI proof dependency stack. The upstream project's formal environment has a different Lean/Mathlib revision from `formal/`, 42 manifest packages, and a wide `Foundation` import surface. No theorem-equivalent replacement for our localized Weil certification, no drop-in prime-error bound, and no justification for vendoring or upgrading were established. This is a scoped source audit, not a Lean/Comparator build or exhaustive transitive closure. OAI-4 remains the route-by-route mathematical impact audit.

**OpenAI mathematical route-impact OAI-4 — `2026-10-08T02:38:25Z`.** [`EXT-0001-route-impact-audit.md`](../references/external-results/EXT-0001-route-impact-audit.md) checks all eleven historical attempts and the current frozen v1/generic v2 pathways against exactly `EXT-0001`. Proven changes: nontrivial zeros are confined to `1/8<=Re(rho)<=7/8`; `C-0060` bounds the fixed-center Laguerre root by `B(s0)>1`. As a dependency-level consequence of existing `C-0020`, the dyadic squared-prime-discrepancy upper scale is at most `O(X^(11/4))`, still insufficient for RH. A `7/8` pointwise error term is **not** imported without an explicit-formula proof; even a hypothetical `theta=7/8` absolute bound leaves `X^(3/8+o(1))` after critical half-weighting. No Li/phase/moment/weil blocker is removed; the genuine v2 negative directions remain failures of the sufficient Schur criterion only, not of the localized Weil form or RH. No theorem, certificate, source integration, or admission changes. The OAI-5 exact analytic corollary work remains separately scoped.

**OAI-5 — prime-distribution consequences, `2026-10-08T02:44:31Z`.** [`F-20261008-002`](../findings/2026-10-08T024431Z-openai-seven-eighths-prime-distribution.md) and `C-0061` derive `psi(x)=x+O(x^(7/8)log²x)`, `theta(x)=x+O(x^(7/8)log²x)`, and `pi(x)=Li_2(x)+O(x^(7/8)log x)`, using `EXT-0001` and the classical explicit formula/zero count `R-0035`, including jump-point correction. `C-0062` bounds compact smooth critical-half-weight discrepancy by `O_W((1+|tau|)X^(3/8)log²X)`. This closes OAI-4's *missing pointwise exponent derivation*, **not** its square-root cancellation obstruction. Frozen v1/v2 admission and RH `UNRESOLVED` are unchanged.

**OpenAI reuse and licensing decision OAI-6 — `2026-10-08T03:00:21Z`.** [`EXT-0001-reuse-and-license-decision.md`](../references/external-results/EXT-0001-reuse-and-license-decision.md) selects **reference-only** use of the frozen theorem `EXT-0001`: cite author/source/commit and keep our `C-0060..C-0062` deductions distinct, with independent Comparator replay optional and explicitly not claimed. No OpenAI proof code, manuscript or third-party dependency is copied; no Git submodule, fork, Lake dependency, toolchain upgrade or source vendoring is justified without a named local formal consumer and a separate reviewed import decision. The pinned upstream is Apache-2.0; any future redistribution must check source-specific license/NOTICE attribution and modifications. This does **not** license our own repository or change v1/v2 certificate admission, RH status, or proof machinery.

**OAI-6 license correction — `2026-10-08T03:03:46Z`.** The repository's own license was already explicitly **MIT OR Apache-2.0**, at the user's option: root `README.md`, `LICENSE-MIT`, and `LICENSE-APACHE`. The initial OAI-6 inspection checked only a literal root `LICENSE`/ `NOTICE` filename and incorrectly suggested no project license was established. [`EXT-0001-reuse-and-license-decision.md`](../references/external-results/EXT-0001-reuse-and-license-decision.md) is corrected. The reference-only/no-vendoring decision is unchanged. Any future imported OpenAI Apache-2.0 source would carry its own license obligations and would not automatically acquire our MIT option.

**OAI-7 external-theorem trust contract — `2026-10-08T03:07:13Z`.** [`docs/CONTRACTS.md`, Section 5](CONTRACTS.md) and [`docs/PROTOCOL.md`, Section 7.2](PROTOCOL.md) now explicitly separate attributed/pinned external `EXT-` evidence; checked local `C-/F-` deductions dependent on that premise; local pinned Lean-kernel proofs; Arb generator enclosure input; Rust exact certificate PASS; and separately admitted retained finite-support theorems. `EXT-0001` has no independent local Comparator replay; `C-0060..C-0062` are written derived consequences, **not** kernel-checked proofs. No cross-class promotion, source vendoring, changes to the eight v1 admissions, empty v2 admission set, or RH status. OAI-7 is documentation-only; no proof replay or verifier tests were run.

**OAI-8 research direction — `2026-10-08T03:16:56Z`.** [`research/openai-math/RESEARCH_DIRECTION.md`](../research/openai-math/RESEARCH_DIRECTION.md) completes the 8.1–8.5 three-route comparison using the same seven evidence criteria. **Primary:** preserve the independently retained eight finite-support localized Weil theorems, but pivot the generic multi-prime research from more precision/sweeps of the rejected sufficient factor-3 matrices at `T=11/20,N=192/196` to a **new, mathematically valid and strictly tested** operator-positivity criterion; an exact combined low-to-tail Gram is identified as a conditional candidate, *without any positivity claim*. **Secondary:** phase-aware/Laguerre analysis, with only the established `EXT-0001`/`C-0060..C-0062` improvements counted and RH-strength uniform cancellation still unproved. **Deferred:** hybrid Weil/phase implementation pending a quantified bridge theorem. P11 verifies feasible diagnostic tooling, not new positivity; v2 admission remains empty, frozen v1 and RH `UNRESOLVED` unchanged. This slice is comparative analysis and documentation only.

**OAI-9 repository documentation cutover — `2026-10-08T03:41:56Z`.** The [maintained `EXT-0001` status](../references/external-results/EXT-0001-openai-quasi-rh.md) and [bibliography `R-0034`](../references/BIBLIOGRAPHY.md) now distinguish **confirmed frozen upstream source identities** from **unperformed optional local Comparator/Lean replay**, and identify the real solution module separately from the `sorry` challenge template. [`references/external-results/README.md`](../references/external-results/README.md) defines the read-only provenance checks and separate optional real replay gates. `C-0060..C-0062` remain unique written derived results, dependent (directly/transitively) on external `EXT-0001` and classical `R-0035`; OAI-9 adds no new theorem. The [OAI-8 primary/secondary/deferred choice](../research/openai-math/RESEARCH_DIRECTION.md) now appears in `AGENTS.md`, root `README.md`, `scripts/README.md`, this maintained status, and the index. Timestamped October 8 addenda link the historical August Laguerre/chirp/Weil attempts without rewriting their original findings. Frozen v1 **8/8**, v2 **0** admissions, exact negative directions for the current factor-3 sufficient v2 matrices, and RH `UNRESOLVED` remain unchanged. **No external replay, proof-code change, certificate retest or admission is implied by documentation acceptance.**

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
- [`A-20260826-001`](../attempts/2026-08-26T171400Z-one-prime-support-continuation.md) — one-prime support continuation from the verified `T=7/20` basepoint; moving Legendre dimension now yields independently verified theorems at `T=2/5,N=40`, `T=17/40,N=48`, `T=9/20,N=56`, `T=19/40,N=68`, `T=1/2,N=80`, and `T=21/40,N=96`; `PROMISING`.

The repository retains the proof-bearing computations through `X-20260828-001` together with separate pre-theorem and tooling records. No proof of RH has been obtained.

## Active leads

### L1 — Exact-prime localized Weil positivity and support continuation

**Status:** `VERIFIED THROUGH T=21/40`

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

The canonical `T=1/2` pre-theorem run then mapped `N=56,60,...,104`. Floating reconnaissance found `N=56..68` negative, `N=72` unstable, and `N=76..104` stable-positive. Rigorous precision escalation classified `N=76` as a stable mathematical negative under the present full-tail Schur reduction, while fallback `N=80` stabilized positive at 512 bits. The exact 64-bit-matrix / 32-bit-witness candidate was then reassembled at 640 bits with unchanged exact `mu`, even margin, and odd margin while Arb enclosure widths contracted.

A separate explicit admission added only `(T,N)=(1/2,80)` to the closed v1 theorem contract. Fresh proof-bearing `X-20260827-004` reassembled the certificate from scratch at 512-bit Arb precision. The independent zero-float Rust verifier returns `passed=true` with scope `localized_weil_positivity_T_1_2`, deriving approximately

```text
mu_80       > 0.6983326376765460
even margin > 0.0006030229450313612
odd  margin > 0.002927388923852846.
```

The retained certificate SHA-256 is `95dd6c7a497ad605ddc81129a774bade5fbbc769d0f6fdf29172b89da2a57a7d`; the retained Rust replay SHA-256 is `7383c91f48ead83ac9268fcdb154f9372c45ac3510339b9eaac3bd6fd461322a`. Real-certificate adversarial replay again distinguishes contract failure (`factor=2`, exit `2`) from theorem failure (contract-valid negative diagonal perturbation, exit `1`). This establishes `F-20260827-002` / `C-0055`: strict localized Weil positivity at `T=1/2`.

Canonical pre-theorem `X-20260827-005` then continued to `T=21/40=0.525`. The truncated floating scout first appeared stable-positive at `N=88`, but rigorous full-tail precision escalation showed `N=88` and `N=92` to be genuine mathematical negatives, with converged Schur minima approximately `-0.5482556100498948` and `-0.12127824455981323`. Continuing over the unresolved higher range found `N=96` and `N=100` rigorously precision-stable positive at 512 bits. The driver selected the smaller `N=96`; its 64-bit-matrix / 32-bit-witness exact candidate remained unchanged under fixed 512-to-640-bit reassembly while Arb interval widths contracted.

A separate explicit admission added only `(T,N)=(21/40,96)` to the closed v1 theorem contract; `N=100` remains forbidden. Fresh proof-bearing `X-20260828-001` reassembled the theorem certificate from scratch at 512-bit Arb precision. The independent zero-float Rust verifier returns `passed=true` with scope `localized_weil_positivity_T_21_40`, deriving approximately

```text
mu_96       > 0.69600913384063989
even margin > 0.00090134267068206139
odd  margin > 0.0037494074424420441.
```

The retained certificate SHA-256 is `a455dcb995a56f6d387e79b199cfc6f18ba6fca108fcfe3c00987e1c47b44824`; the retained Rust replay SHA-256 is `9530b53b00c1e96a1be82b2127adc7d1424e63af444803f169be8434f51d2e83`. Real-certificate adversarial replay distinguishes contract failure (`factor=2`, exit `2`) from theorem failure (contract-valid negative diagonal perturbation, exit `1`). The canonical retained-proof audit passes `7/7`. This establishes `F-20260828-001` / `C-0056`: strict localized Weil positivity at `T=21/40`.

Clean canonical pre-theorem `X-20260923-001` then continued to `T=27/50=0.54`. Its p17 scout selected `N=100`, but rigorous full-tail screening rejected `N=100` as a mathematical negative and selected fallback `N=104`, whose exact candidate was stable under 640-bit fixed-parameter reassembly. A separate closed-contract admission added only `(27/50,104)`.

Fresh proof-bearing `X-20260924-001` reassembled `C-0057` from scratch at 512-bit Arb precision from clean committed HEAD `86f5fd75360892d92cd584bc5f2eab0cae56851b`, with certificate metadata `git_dirty=false`. Independent zero-float Rust replay returns `passed=true` and scope `localized_weil_positivity_T_27_50`, deriving approximately

```text
mu_104      > 0.6643369939721553
even margin > 0.0002388902594756742
odd  margin > 0.000779387887620489.
```

The retained certificate SHA-256 is `75187f3be283ca9596a714c4a12822c4c58cd4b33e7624110ff102d68c9aab3f`; the retained Rust replay SHA-256 is `e29e80bdb4af140db95934732095e45ce761ad82e6eb09b1bf8a5bd5931512ce`. Real-certificate attacks reject wrong factor, mixed pairs, malformed interval, missing provenance, and missing structure with contract exit `2`; a contract-valid exact negative diagonal reaches theorem verification and returns exit `1` / `passed=false`; an unchanged copy returns exit `0` / `passed=true`. The canonical retained-proof audit passes `8/8`. This establishes `F-20260924-001` / `C-0057`: strict localized Weil positivity at `T=27/50`.

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
23. After `N=76` was rigorously negative, explicit admission of `N=80` plus a fresh 512-bit exact certificate and independent Rust replay prove strict localized Weil positivity at `T=1/2` (`C-0055`).
24. At `T=21/40`, rigorous full-tail continuation rejects the false scout positives `N=88,92`, selects `N=96`, and separate closed-contract admission plus a fresh 512-bit exact certificate and independent Rust replay prove strict localized Weil positivity (`C-0056`).

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
- `computations/2026-08-27T151517Z-t1-2-continuation/` is the historical pre-theorem `T=1/2` bundle. It records `N=76` as rigorously stable-negative under the current Schur reduction and `N=80` as an exact `CANDIDATE_READY` point stable from 512 to 640 bits. It remains non-proof-bearing; the later separate admission and theorem replay are `X-20260827-004`.
- `X-20260827-004` contains the separately admitted fresh `T=1/2,N=80` theorem certificate, independent zero-float Rust PASS, real-certificate adversarial replays, and retained-proof registration establishing `C-0055`.
- `X-20260827-005` is the historical canonical pre-theorem `T=21/40` continuation: `N=88` and `N=92` are rigorous full-tail negatives despite positive scouts; `N=96` and `N=100` are rigorous positives, and the driver selects generator-side `CANDIDATE_READY` at `N=96`. It remains non-proof-bearing.
- `X-20260828-001` contains the separately admitted fresh `T=21/40,N=96` theorem certificate, independent zero-float Rust PASS, real-certificate adversarial replays, and retained-proof registration establishing `C-0056`.
- The closed exact-prime admission table now has a test-only cross-layer consistency corpus at `tests/data/exact-prime-admission-v1.json`. It exercises the independently hard-coded Python generator, Python semantic validator, raw JSON Schema, and Rust verifier admission logic over eight allowed pairs, all fifty-six off-diagonal pairs in the `8 x 8` admitted support/dimension grid, and external forbidden controls including `(1/2,76)`, `(21/40,92)`, `(21/40,100)`, `(27/50,100)`, and `(27/50,108)`. Production trust layers do not read this corpus, so decoupled verification is preserved while accidental whitelist drift remains test-detectable.
- The canonical continuation driver is now `continuation-driver-p17-v1` with cache contract `continuation-driver-v6`. P17 preserves the p16 lifecycle/observability/finalization contract and changes the canonical floating-scout policy to eight increasing resolutions, with all levels retained but convergence/sign classification evaluated on the highest three under the unchanged 1% relative Schur-movement tolerance. This was introduced after `T=27/50` diagnostics showed that a coarse scout level could make otherwise converging positive dimensions appear globally unstable. The rigorous Arb full-tail stage, exact outward rounding, exact witness checks, cross-precision candidate confirmation, and hard pre-theorem boundary are unchanged. The Windows publication path is also hardened: live JSON, final bundle artifacts, and continuation-cache entries share a bounded retry for transient `PermissionError`/sharing denials, while persistent denial still fails closed. The cache remains v6 because cached mathematical payload/key semantics did not change; the source fingerprint isolates the p17 implementation automatically. The existing `3/2` CLI worker defaults and sequential internal precision/candidate stages remain unchanged. Focused current-HEAD lifecycle/driver acceptance passes `126/126` across observability, driver, bundle, state-machine, and pre-theorem-boundary tests.
- The earlier dirty-tree p17 `T=27/50` diagnostic remains tooling evidence only. Clean canonical `X-20260923-001` reproduced the same transition from committed provenance `392aa3d3ae0583dc7a26956bf70295771af1faee` with `git_dirty=false`: scout stability begins at `N=100`, rigorous full-tail screening rejects `N=100` as `MATHEMATICAL_NEGATIVE`, fallback `N=104` is `PRECISION_STABLE` at 512 bits, and the exact 64-bit-matrix / 32-bit-witness candidate is `CANDIDATE_STABLE` under 640-bit fixed-parameter reassembly. The 19-artifact manifest audits without hash/size mismatch and records complete five-worker cleanup. `X-20260923-001` remains canonical **pre-theorem** evidence only; the later separate clean-provenance theorem run `X-20260924-001` now establishes `(27/50,104)` / `C-0057` after independent replay, adversarial verification, and retained-proof registration.
- `computations/retained-proofs.json` now provides a closed first-class retained-proof registry for exactly `C-0050` through `C-0057`. `scripts.cert.verify_retained_proofs` verifies each registered artifact's raw-byte SHA-256 before replay and then requires current `rh_cert` PASS plus exact theorem identity agreement. After registering `C-0057`, focused retained-proof tests pass `67/67`, manifest-only validation reports eight registrations, and the canonical gate passes `8/8`. The registry remains explicit—no automatic computation-directory discovery—and stores no derived margin diagnostics.


`X-20260821-005`, `X-20260826-001`, `X-20260826-002`, `X-20260826-003`, `X-20260827-002`, `X-20260827-004`, `X-20260828-001`, and `X-20260924-001` are proof-bearing for the finite-support theorems `C-0050`, `C-0051`, `C-0052`, `C-0053`, `C-0054`, `C-0055`, `C-0056`, and `C-0057`, respectively. Their exact certificates and independent replays are retained with hashes and reproduction commands. `X-20260827-001`, `X-20260827-005`, and `X-20260923-001` remain explicitly pre-theorem, while `X-20260827-003` is tooling/performance evidence only; none is part of that proof-bearing set. None of these finite-support results constitutes a proof of RH.

## Open requirements / blockers

There is no remaining blocker for the fixed support target `T=7/20`; `A-20260821-004` is complete.

There is no remaining blocker at `T=2/5`; `C-0051` is independently verified.

There is no remaining blocker at `T=17/40`; `C-0052` is independently verified.

There is no remaining blocker at `T=9/20`; `C-0053` is independently verified.

There is no remaining blocker at `T=19/40`; `C-0054` is independently verified. The hard pre-theorem boundary worked as intended: `X-20260827-001` stopped at `CANDIDATE_READY`, and theorem status was granted only after the separate admission and proof-bearing `X-20260827-002` replay.

There is no remaining blocker at `T=1/2`; `C-0055` is independently verified. The same hard boundary worked again: the `T=1/2` continuation bundle stopped at `CANDIDATE_READY`, and theorem status was granted only after the separate `(1/2,80)` admission and proof-bearing `X-20260827-004` replay.

There is no remaining blocker at `T=21/40`; `C-0056` is independently verified. `X-20260827-005` stopped at `CANDIDATE_READY`, and theorem status was granted only after the separate `(21/40,96)` admission and proof-bearing `X-20260828-001` replay. The larger generator-side `N=100` candidate remains unadmitted.

There is no remaining blocker at `T=27/50`; `C-0057` is independently verified. `X-20260923-001` stopped at `CANDIDATE_READY`; theorem status was granted only after the separate `(27/50,104)` admission, clean-provenance `X-20260924-001` generation, zero-float Rust PASS, real-certificate adversarial replay, explicit retained-proof registration, and full `8/8` retained replay.

The exact Rust verifier performance blocker is now closed by `X-20260827-003`. The implementation still validates full certificate parity/symmetry, remains pure exact rational and zero-float, and preserves the closed-contract/error semantics, but constructs parity Schur blocks directly and exploits lower-triangular/symmetric congruence structure. The previously measured `N=32,40,48,56` debug replays improve from approximately `11,25,54,102` seconds to `3.564,6.145,13.210,24.880` seconds; `N=68` replays in `31.408` seconds. A second replay produces exact parsed-JSON equality against every retained `C-0050` through `C-0054` Rust output, and the real `C-0054` adversarial cases remain contract error `exit 2` versus theorem failure `exit 1`.

There is therefore no current verifier- or orchestration-performance blocker to the one-prime route. Clean canonical `X-20260923-001` has completed the `T=27/50=0.54` pre-theorem slice and stopped correctly at generator-side `CANDIDATE_READY` for `N=104`. The independently verified finite-support frontier remains `T=21/40,N=96`; `(27/50,104)` must not be treated as theorem-bearing without a separate explicit admission decision and fresh independent proof-bearing replay. The eventual structural transition remains entry of the `p=3` compressed translation at `(1/2)log 3`, which requires a new mathematical/tooling phase rather than casually broadening the present one-prime driver.


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

Phase 5 is complete for `(27/50,104)`. The closed `exact_prime_legendre_schur` v1 contract admits exactly eight matched pairs. Fresh clean-provenance `X-20260924-001` generated `C-0057` from scratch at 512-bit Arb precision; independent zero-float Rust returns exit `0` / `passed=true`; real-certificate attacks correctly distinguish contract rejection from theorem failure; the exact certificate is explicitly registered in `computations/retained-proofs.json`; and the complete canonical retained-proof replay exits `0` with `RETAINED PROOF CHAIN: PASS - 8/8`. The independently verified finite-support frontier is therefore `(T,N)=(27/50,104)` / `C-0057`.

Repository-wide Phase 6 closure is green. The default Python suite passes `554/554`; the explicit retained-artifact pytest passes `1/1` and requires the complete `C-0050..C-0057` replay ending in `8/8`; full `cargo test -p rh_cert`, Rust format check, and strict Clippy pass; and authoritative `formal/lake build` completes successfully with `8711 jobs`. Current-facing stale seven-proof assumptions were removed from the retained acceptance test, `AGENTS.md`, and root `README.md`; older seven-pair and `C-0056` statements that remain are timestamped historical state and are preserved deliberately.

The next research slice should be chosen deliberately rather than extrapolated automatically. `T=27/50=0.54` lies only about `0.0093` below the structural threshold `(1/2)log 3 ≈ 0.5493`, where the `p=3` compressed translation enters. Any continuation beyond that threshold requires the separate multi-prime mathematical/tooling phase; RH remains unresolved.

**Multi-prime tooling upgrade P0 — `2026-10-01T09:46:49Z`.** The existing one-prime v1 theorem path is frozen before the new structural work begins. Its support gate, exact eight-pair admission grid, `c2/G2` v1 schema semantics, and retained `C-0050..C-0057` theorem identities now have an explicit fast regression guard in `tests/test_one_prime_v1_freeze.py`; the canonical retained proof audit continues to provide byte-hash and independent Rust replay protection. Multi-prime work must be additive and use a separate certificate/profile/verifier path rather than broadening v1. The next implementation phase is P1: freeze the generic active prime-power mathematical contract and the combined-prime Schur/complement semantics before production code is generalized.

**P0 verification closure — `2026-10-01T10:07:49Z`.** Focused freeze/admission/support tests pass `15/15`; the complete default Python suite passes `558/558`; full `cargo test -p rh_cert`, `cargo fmt -p rh_cert -- --check`, and strict `cargo clippy -p rh_cert --all-targets -- -D warnings` pass; authoritative `formal/lake build` completes successfully with `8711 jobs`; and the canonical retained-proof audit again reports `RETAINED PROOF CHAIN: PASS - 8/8`. A final process scan found no remaining repository pytest, retained-verifier, Rust-test, or Lean-build process. P0 is closed.

**Multi-prime tooling upgrade P1 — `2026-10-01T10:14:40Z`.** The pre-implementation mathematical contract is now frozen in `docs/MULTI_PRIME_CONTRACT.md`. `C-0058` proves the generic complement rule `mu_N=H_N-c_T-sum_m c_m b_m-rho_R`; in the immediate `(log3)/2<T<(log4)/2` window the active set is exactly `{2,3}` and `b_2=b_3=1`, giving the expected `c_2+c_3` loss. `C-0059` explicitly closes the critical factor-3 gate: all arithmetic terms are first grouped into the single signed operator `P`, so the cross block has exactly the three components `V,P,R` and the sufficient Schur matrix remains `A_N-(3/mu_N)(G_V+G_P+G_R)`. `G_P` is the tail Gram of the combined operator and includes the `P_2/P_3` mixed terms; `G_2+G_3` is not an allowed substitute. No theorem-certification code, v1 contract, or theorem admission changed. P1 is closed; subsequent implementation must consume this contract additively.

**P1 verification closure — `2026-10-01T10:19:42Z`.** The frozen-v1/admission regression target passes `10/10`, `git diff --check` passes, and direct repository scans confirm that neither `c3` nor `G3` was added to the v1 JSON Schema, `scripts/cert/`, or `crates/rh_cert`. The new contract uses `G_P` only as the combined arithmetic tail Gram and explicitly preserves the mixed `P_2/P_3` terms. No repository verification process remains running.

**Multi-prime tooling upgrade P2 — `2026-10-01T10:28:50Z`.** A new independent module, `scripts/cert/prime_power_terms.py`, now provides the generic prime-power arithmetic operator core while leaving `first_prime_matrices()` untouched. It performs exact integer prime-power recognition, computes rigorous Arb `log(m)`, `tau_m`, `Lambda(m)`, and `c_m`, enumerates the exact strict active set with fail-closed threshold handling, constructs every compressed translation by globally partitioned piecewise polynomial action, sums the active `P_m` before integration, and derives combined `P`, combined operator-square `P^2`, and `G_P=P^2-PD^{-1}P`. Focused tests prove agreement with the historical one-prime matrices, prove a nonzero `P_2/P_3` cross contribution in `P^2`, exercise the `{2,3,4}` regime with `tau_2<1`, and reject mixed-support term assembly. The combined focused regression target passes `24/24`; the complete default Python suite passes `567/567`. A final process scan is clean. No v1 production theorem implementation changed. P2 is closed.

**Multi-prime tooling upgrade P3 — `2026-10-01T10:55:56Z`.** `scripts/cert/multi_prime_legendre_schur.py` now provides `assemble_multi_prime_schur()`, the first full rigorous assembler using the generic arithmetic operator. It returns the certified `active_terms`, combined `P` and operator `P_squared`, `A`, `GV`, `GP`, `GR`, `rho_R`, `mu`, and Schur matrix. The bridge was intentionally verified before `{2,3}` use: at `(7/20,16)`, `(2/5,24)`, `(17/40,28)`, and `(9/20,32)`, the new path overlaps the frozen one-prime implementation entry-for-entry for `P`, `P^2`, `GP/G2`, `A`, `mu`, and Schur, with `GV`, `GR`, and `rho_R` agreeing as well. That bridge passes `4/4`; only afterward the `{2,3}` test runs and rigorously proves a nonzero mixed contribution to `P^2`, so the combined square is not `P_2^2+P_3^2`. The integrated P3/P2/frozen-v1 target passes `31/31`. The complete default Python suite passes `574/574` in `375.93 s`; a final process scan is clean. No v1 theorem or certificate code changed. P3 is closed.

**Multi-prime tooling upgrade P4 — `2026-10-01T11:15:33Z`.** Added `scripts/weil_multi_prime_schur_scout.py` and `scripts/weil_multi_prime_support_candidate_check.py` without modifying the frozen one-prime scout/candidate files. The scout is a genuinely floating/truncated reconnaissance path: it independently enumerates prime powers numerically, builds every active compressed translation, sums the combined `P`, and reports `A/GV/GP/GR` reconnaissance plus combined-prime conditioning. The candidate stage is separate and rigorous: it calls `assemble_multi_prime_schur()`, outward-rounds `A/GV/GP/GR`, rounds each active-term complement contribution separately, reconstructs the exact factor-3 Schur matrix, and derives exact even/odd rational witness margins. Diagnostics include active terms individually, per-term complement losses, combined `P/P^2/GP` conditioning widths, explicit `GP` widths, exact margins, and optional Arb precision-contraction comparison. Arb precision, matrix-rounding bits, and witness bits remain independent inputs; comparison precision is diagnostic-only. Focused P4/P3/P2/frozen-v1 tests pass `24/24`; the complete default Python suite passes `578/578` in `366.32 s`. A final process/diff audit is clean. No theorem profile, verifier path, or admission changed. P4 is closed.

**Multi-prime tooling upgrade P5 — `2026-10-01T16:20:18Z`.** Added `scripts/weil_multi_prime_continuation_driver.py` as a separate continuation implementation; the historical `scripts/weil_continuation_driver.py` is unchanged. P5 initially accepts only the strict window `log(3)/2 < T < log(4)/2`, proves those inequalities with Arb, and independently requires `enumerate_active_prime_power_terms()` to return exactly `{2,3}`. It preserves the established workflow: multi-resolution floating scout → stable dimension selection → primary plus fallback rigorous Arb precision ladders → independent matrix/witness bit escalation → exact candidate → higher-precision candidate confirmation → pre-theorem `CANDIDATE_READY`. Operational safeguards are preserved: spawn-based bounded process pools, `as_completed` observation with deterministic retained ordering, source-fingerprinted cache and corrupt-cache recovery, atomic cache/bundle writes, output locking, terminal-state machine, immutable result digest, manifest-last sealing, and explicit worker cleanup verification. A new `weil_multi_prime_support_continuation_scout.py` supplies the `A/GV/GP/GR` rigorous-screen hook. The shared continuation bundle writer now admits both known pre-theorem driver roles while retaining all non-promotion checks. Focused P5/P4/P3/P2/frozen-v1 acceptance passes `35/35`; bundle/P5 regression passes `29/29`. A real parallel CLI smoke at `T=3/5`, `N={8,12}` sealed a deterministic `NO_CANDIDATE` bundle with active set `[2,3]`, two scout workers reaped, and zero active children. The complete default Python suite passes `591/591` in `375.99 s`. P5 is closed.

**Multi-prime tooling upgrade P6 — `2026-10-01T17:51:51Z`.** Added a separate closed certificate contract at `docs/contracts/rh-weil-certificate-v2.json` with format `rh-weil-certificate-v2` and profile `multi_prime_power_legendre_schur`; v1 is byte-unchanged. V2 removes the one-prime `c2/G2` shape rather than extending it: global `constants` contain only `c_T` and `rho_R`, while a canonical `arithmetic_terms` array carries each prime-power identity `(m, base_prime, exponent)` plus exact rational intervals for `log_m`, `tau`, `Lambda(m)`, `c_m`, the compressed-shift norm bound, and its complement contribution. `schur_proof` contains `GV`, combined `GP`, `GR`, and exact even/odd witnesses; `G2` and `G3` are rejected. The tail rule is closed to active prime powers with `log(m)<2T`, complement `H_N-c_T-sum(c_m*b_m)-rho_R`, grouped components `[V,P,R]`, and factor exactly `3/1` tied explicitly to verified claim `C-0059`. `scripts/cert/certificate_v2_contract.py` adds schema and canonical-structure validation while keeping theorem admission separate; `V2_ALLOWED_CONFIGURATIONS` is intentionally empty, so structural validity cannot grant theorem status. Focused P6 plus frozen-v1/admission regression passes `21/21`. The complete default Python suite passes `602/602` in `374.14 s`. No v1 exporter or Rust verifier code changed. P6 is closed.

**Multi-prime tooling upgrade P7 — `2026-10-01T18:22:11Z`.** Added an independent zero-float Rust v2 path in `crates/rh_cert/src/v2.rs` plus format dispatch in `crates/rh_cert/src/dispatch.rs`; the historical v1 verifier implementation in `crates/rh_cert/src/cert.rs` is unchanged. V2 enforces canonical sorted unique arithmetic terms and, for the first structural window, requires exactly `[2,3]`; missing, duplicated, unsorted, substituted, and invalid prime-power identities fail as contract errors. Rust derives each prime loss from the serialized exact-rational `coefficient * compressed_shift_norm_bound` interval, derives `mu_N=H_N-c_T-sum(prime_loss_m)-rho_R`, requires `mu_N>0`, reconstructs `A-(3/mu_N)(GV+GP+GR)`, enforces exact parity block structure, and independently checks the exact lower-triangular congruence/Gershgorin witnesses. The production Rust v2 theorem whitelist remains empty, so implementation alone admits no theorem pair. Malformed or unauthorized v2 input remains contract failure (CLI exit `2`); the internal authorized arithmetic path preserves theorem-failure semantics as a normal `passed=false` result (future CLI exit `1` after explicit admission). Trust boundary: Rust independently verifies exact rational interval proof arithmetic and consistency, but does not independently establish the transcendental Arb enclosures. P7 acceptance is closed: the complete `rh_cert` suite passes `63/63`, strict clippy and rustfmt pass, focused Python v2/v1 regression passes `21/21`, the complete default Python suite passes `602/602` in `515.09 s`, and the retained theorem chain replays `8/8` through the new format dispatcher. No v2 theorem pair is admitted.

**Multi-prime tooling upgrade P8 — `2026-10-01T19:06:42Z`.** Added adversarial and cross-layer acceptance before any real v2 continuation. The v2 JSON Schema now closes the first structural certificate window to exactly two arithmetic terms with identities `[2,3]` and exact compressed-shift norm bounds `b_m=1`; Python semantic validation and Rust independently enforce the same active set and additionally prove the strict serialized support window from rational interval endpoints, requiring `T > upper(log(3))/2` and `T < lower(log(2)) = lower(log(4)/2)`. Equality, interval overlap, and low-precision near-threshold cases fail closed. Added test-only shared corpus `tests/data/certificate-v2-cross-layer-v1.json` covering valid structure plus missing/duplicate/substituted `m=3`, forbidden `m=4`, malformed coefficient/norm intervals, missing/malformed `GP`, and wrong factor; raw Python Schema, Python semantic validation, and Rust agree on all 10 cases. Parity and strict-threshold arithmetic are separately cross-checked in Python semantics and Rust because raw JSON Schema cannot express those cross-field arithmetic relations. Added closed 16-case v2 admission grid `tests/data/multi-prime-admission-v2.json` over four supports and four dimensions; schema-side `$defs.theoremAdmission`, Python production admission, and Rust production admission all reject every case because the v2 theorem whitelist remains empty. Existing regression also confirms a structurally valid negative certificate reaches theorem failure (`passed=false`) rather than contract failure. Focused P8/P6/v1 tests pass `41/41`; complete Rust verifier tests pass `67/67`; strict clippy/rustfmt pass; complete Python passes `608/608` in `387.29 s`; retained v1 proofs replay `8/8`. Frozen v1 verifier/schema/exporter remain unchanged. P8 is closed; no v2 theorem pair is admitted.

**Multi-prime tooling upgrade P9 — `2026-10-01T21:04:17Z`.** The non-theorem end-to-end qualification at predeclared support `T=11/20` is closed as **NOT QUALIFIED — rigorous-stage performance blocker**. Run A used the original frozen grid `N=96,100,...,144`, correctly detected active terms `[2,3]`, completed all eight scout resolutions, reaped all scout workers, sealed a valid `NO_CANDIDATE` bundle, and reported `active_children_after_cleanup=0`; no rigorous stage was reached. A separately predeclared diagnostic extension `N=148,152,...,256` found the stable-positive floating frontier at `N=192` and deterministically selected rigorous targets `192,196`. Run C reached the first 128-bit rigorous assemblies but the external 1800-second execution boundary terminated the process tree before either returned. Run E retried the identical frozen extension with a one-hour allowance; both rigorous workers remained CPU-active for the full run, but after `3590.867 s` neither 128-bit assembly had completed. The one-hour session limit terminated and reaped the entire process tree; final OS scan is clean. No rigorous cache entry was committed, so there is no resumable proof-bearing checkpoint. Consequently P9 did not demonstrate completed `GP`, rigorous `mu_N`, precision escalation, exact candidate construction, stability confirmation, `CANDIDATE_READY`, or completed-run reproducibility. This is an operational performance failure, **not** a mathematical negative for `T=11/20` or `N=192/196`. No further grid extension or tuning is part of P9. The next prerequisite is a separate performance-hardening slice for the generic rigorous multi-prime assembler. V2 theorem admission remains empty.

**Generic assembler performance hardening, phases 1 and 2, `2026-10-01T22:39:34Z`.** [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md) profiles and optimizes the new rigorous path without changing frozen v1 or the mathematical contract. Python Fraction convolution in the residual and repeated potential moments dominated the baseline. Native exact/Arb polynomial operations, assembly-local residual monomial reuse, coefficient-certified parity, and precomputed diagonal scaling reduce isolated 128-bit `N=128` assembly from `897.221 s` to `6.779 s`; `N=192/196` now complete in `26.259/28.069 s`. Focused acceptance passes `65/65`; a real new-path one-prime overlap candidate at `T=2/5,N=40` has positive exact margins and contracting widths. Seven frozen-file hashes are unchanged; no benchmark/candidate/test workers remain. Full acceptance and target higher-precision measurements remain pending. P9 itself was not rerun and remains **NOT QUALIFIED**. V2 theorem admission remains empty; RH remains unresolved.

**Generic assembler phase 3 verification, `2026-10-01T23:14:26Z`.** [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md) now closes equivalence and structural/cache regression guards with `121/121` focused tests. Independent small references cover empty, one-prime, two-prime, and `{2,3,4}` arithmetic; 128-bit balls contain tighter 384-bit optimized/reference enclosures; exact residual coefficients and rational inner products, arbitrary orthogonal basis norms, parity, strict topology, bounded invariant work, and real source-fingerprint invalidation are guarded. Real candidate tests independently reconstruct outward dyadic bounds, factor-3 Schur blocks, and exact congruence margins. A fresh CLI overlap smoke at `T=2/5,N=40`, Arb `384` and matrix/witness `72/40`, has positive exact margins and nonincreasing widths but remains pre-theorem. Production code was not edited in phase 3; seven frozen hashes still match the original capture; no verification workers remain after excluding the live tool harness. Phase 4 target higher-precision/throughput measurements and full Python/Rust/retained-proof acceptance remain pending. P9 is still NOT QUALIFIED; no qualification, reproduction, or v2 admission occurred.

**Generic assembler phase 4 — `2026-10-02T00:29:37Z`, readiness BLOCKED.** [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md) completes isolated precision/throughput measurements and all acceptance executions. `N=192/196` assembly takes `34.893/37.460 s` at Arb 512 and `39.205/41.951 s` at 768; the two-worker 512-bit pair takes `38.208 s`. Full Python passes `647/647`, focused Python `121/121`, Rust `67/67`, strict Clippy and retained byte-integrity/independent replay `8/8`; all seven frozen hashes remain unchanged. Workspace `cargo fmt --all -- --check` fails in four untouched `rh_engine` files; scoped `rh_cert` formatting passes but does not replace that gate. Actual target candidates fail midpoint LDL witnesses at 512/640/768; even 768-bit `GP` widths are about `2.819e64/4.574e70`. This is unresolved arithmetic conditioning, not a mathematical negative. The cost model predeclares a conservative estimated 12-hour external allowance, not launch permission or a runtime bound. Stop before P9; any stable polynomial-coordinate/basis evaluation redesign is separately scoped. No qualification/reproduction or admission occurred; v2 admission remains empty and RH unresolved.

**Post-hardening frozen P9 execution, phase 5 — `2026-10-02T01:06:38Z`.** User authorized the frozen run after the phase 4 blocker report. [X-20261002-001](../computations/2026-10-02T010121Z-t11-20-multi-prime-qualification-after-hardening/record.md) retains the dirty tracked patch, exact source snapshot/hashes and predeclared command. The unchanged driver terminated naturally in `168.78 s` at **`PRECISION_LIMIT_REACHED`**, selecting `192/196` without intervention. Both 128-bit screens reported float-conversion `OverflowError`; both dimensions then exhausted `256/384/512` as insufficient precision. At 512, complements are positive but maximum `GP` widths remain `3.553e141/1.049e148` and midpoints are unstable. No candidate construction or mathematical rejection occurred. The driver emitted a final manifest and reported five managed workers reaped with zero active children; phase 6 byte audit, independent cleanup audit and reproduction were not performed. P9 remains **NOT QUALIFIED**; conditioning and the workspace formatting blocker remain. Source and all numerical controls stayed unchanged. No theorem admission or certificate was generated.

**Phase 6 audit/reproduction — `2026-10-02T01:25:32Z`.** [X-20261002-001](../computations/2026-10-02T010121Z-t11-20-multi-prime-qualification-after-hardening/record.md) now independently audits both final manifests, all `18/18` listed artifacts per run, and both ordered result-payload digests. Fresh-cache Run B uses the same 19-file source snapshot and frozen settings, naturally finishing in `169.39 s` at `PRECISION_LIMIT_REACHED`, versus Run A's `168.78 s`. Exact recursive comparison passes with zero mathematical/diagnostic differences after predeclared execution-metadata exclusions; `17/18` artifacts are byte-identical. Both runs select scout targets `192/196`, exhaust the same rigorous history, and never construct a candidate. The independent Windows process scan finds zero qualification-related survivors, separate from each driver's five reaped workers/zero active children. Seven frozen hashes remain unchanged. Audit/reproducibility/cleanup PASS, but the two-`CANDIDATE_READY` qualification gate **FAILS** and P9 remains NOT QUALIFIED. Exact margins/bits/candidate stability were not reached; conditioning and the prior workspace-formatting blocker remain. No source change, weakened controls, third retry or theorem admission occurred.

**Multi-prime diagnostic hardening, Phase 7, `2026-10-02T02:58:34Z`.** [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md) closes the exact-safe diagnostic prerequisite. Multi-prime screening, candidate construction and confirmation now retain rational bounds/widths and use exact contraction and margin-tolerance comparisons. Power-of-two scaling precedes numerical eigendiagnostics; unavailable diagnostics require more precision and cannot accept or reject a target. Workflow/cache contracts advance separately to `multi-prime-continuation-driver-p9-phase7-v2` / `multi-prime-continuation-driver-v2`; frozen v1 and shared helpers are byte-unchanged. Focused acceptance passes `144/144`. Actual uncached Arb-128 `192/196` screens complete in `29.171/31.254 s` without conversion exceptions, but remain insufficient precision. The known one-prime overlap candidate confirms at fixed `64/32` bits from Arb `256` to `384`; that is not `{2,3}` target readiness. Phase 8 enclosure-growth diagnosis is next; no conditioning redesign or qualification retry occurred. P9 remains NOT QUALIFIED and P10 remains blocked.

**Multi-prime conditioning diagnosis, Phase 8, `2026-10-02T04:24:32Z`.** [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md) closes the diagnosis/representation-selection gate without changing production. Global translation/product/endpoint amplification precedes tail subtraction; cell-local Legendre recurrences and exact local-basis norm contractions stabilize combined arithmetic while retaining mixed terms. Exact rational grouping of the existing potential moments is also required for full-Schur conditioning. At Arb 512, selected Schur widths at `192/196` are `6.5763e-82/2.1290e-80`, versus global `1.8827e142/5.3628e148`; all eight matrix-stage widths contract through `128/256/384/512`.

**Frozen-target sufficient-Schur rejection / stop.** Actual selected-representation candidates at Arb 384 fail even LDL pivots `95/97` at both `64/32` and frozen-maximal `104/56` bits. Retained 56-bit dyadic vectors have exact interval Rayleigh upper bounds `-0.139224102100/-0.0452493461716`, or `-1.50060485641e-5/-2.93867348887e-5` after division by original basis norm squared; independent zero-float input replay passes `2/2`. This is generator-side rejection of the unchanged factor-3 sufficient Schur matrices, **not localized Weil-form negativity or an RH counterexample**. Production and all 23 Phase 7 source/test inputs are byte-unchanged. Phase 9 and qualification have not started; P9 remains NOT QUALIFIED/P10 blocked. The plan's stop condition requires a separate research decision before changing support, grid or acceptance criteria. No theorem admission or new claim follows.

**Stable generic implementation, Phase 9, `2026-10-02T05:44:54Z`.** [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md) implements cell-local Legendre arithmetic for arbitrary exact orthogonal polynomial bases and exact grouped potential moments. Mixed terms, original norms/coefficient parity, strict topology, residual/complement and factor `3` remain intact; no frozen-v1 or admission change occurs. Focused acceptance passes `159/159`; full default Python passes `696/696`. Successful candidate results retain exact matrices/scalars/witnesses; independent rational replay verifies the real one-prime overlap base/confirmation at fixed `64/32`, Arb `256 -> 384`, `2/2`. Positive multi-prime bundles now require separate manifest-listed base and fixed-input confirmation proofs; workflow/cache versions are `multi-prime-continuation-driver-p9-phase9-v3` / `multi-prime-continuation-driver-v3`.

**Phase 9 implementation verified; full readiness gate BLOCKED.** Real `11/20,192/196` outward candidates at Arb 384, `104/56`, still fail even LDL pivots `95/97`. Schur widths contract to `6.5763e-82/2.1290e-80` at 512, but independent exact reconstruction proves strict negative directions in both rounded candidate matrices, `2/2`, and all four Arb-384/512 matrices, `4/4`. The positive overlap control is not substitute target qualification. No positive frozen-target base or confirmation exists. P9 remains NOT QUALIFIED/P10 blocked; no qualification or Phase 10 formatting work occurred. A separate research decision is required before support/grid/criterion changes. This is sufficient-test rejection, not localized Weil negativity or an RH counterexample.

**Phase 10 workspace formatting, `2026-10-02T06:23:49Z`, COMPLETE.** The four recorded `rh_engine` files receive a separate rustfmt-only patch. Source tokens preserve literals/comments/identifiers/operators; five other engine files and all `30` Phase 9 source/test inputs are byte-unchanged. Full workspace `cargo fmt --all -- --check` passes; affected Rust tests pass `15/15`; strict `cargo clippy --locked --workspace --all-targets -- -D warnings` passes. The actual engine CLI produces `8/8` prime-trace rows matching independent finite prime-power/polynomial references. Separate snapshots, patch, console results and byte manifest are retained in [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md). This closes formatting only; frozen-target mathematical rejection, P9 NOT QUALIFIED and P10 upgrade-closure blockage remain. No qualification or Phase 11/12 work occurred.

**Phase 11 tooling acceptance and native witness cutover, `2026-10-02T09:49:35Z`, COMPLETE.** The user clarified that tool improvement does not require target positivity and stopped excessive repeated benchmarking. Multi-prime witnesses now use fraction-free integer elimination with direct inverse-factor accumulation and native exact congruence. One same-input smoke reduces the complete 97-mode proper-block witness from `1306.928 s` to `22.725 s` and the actual frozen N196 candidate from `541.946 s` to `53.525 s`; exact witness/margin, full rounded inputs and rejection reason are unchanged. Post-cutover focused/default Python pass `77/77` and `715/715`; twelve frozen/shared byte controls remain unchanged. Pre-cutover workspace Rust `82/82`, format, strict Clippy and retained replay `8/8` pass; no Rust/Lean change follows.

Actual complete `192/196` screen ladders both classify `MATHEMATICAL_NEGATIVE`, with `109.598 s` two-worker lifecycle. Independent rounded rejection replay passes `8/8`; real positive overlap controls confirm `512 -> 640` and `640 -> 768`, all four proofs replay. The proper-block smoke is not positive full-target evidence. The obsolete 60-hour draft is withdrawn; the native operation-envelope proxy supports a reassessed two-hour external allowance per fresh run, not a bound or launch authorization. Native memory and complete positive integrated costs are not claimed measured. Source snapshots, raw-byte evidence and a zero-survivor scoped Windows scan are retained in [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md). Phase 12 has not launched. Frozen support/grid/criteria and empty v2 admission remain unchanged; mathematical rejection does not block engineering acceptance or prove localized Weil negativity.

