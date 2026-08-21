# Research Bibliography

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-21T04:09:56Z`

This is the authoritative source registry for literature materially used in the repository.

## Rules

- Prefer primary or authoritative sources.
- Record why each source matters to this repository.
- Record when the source was first verified/accessed.
- Use stable identifiers where possible.
- A source being listed here does not mean every claim in it has been independently checked.

## Sources

### R-0001 — Li criterion

- **Authors:** Xian-Jin Li
- **Title:** The Positivity of a Sequence of Numbers and the Riemann Hypothesis
- **Publication:** Journal of Number Theory, 65(2), 325-333
- **Year:** 1997
- **Stable identifier:** DOI `10.1006/jnth.1997.2137` — https://doi.org/10.1006/jnth.1997.2137
- **First verified/accessed:** `2026-08-20T20:37:00Z`
- **Used for:** Original Li positivity criterion and definition of the Li coefficients.
- **Verification notes:** Bibliographic metadata and abstract checked against the Journal of Number Theory/ScienceDirect record.

### R-0002 — Bombieri-Lagarias complement to Li

- **Authors:** Enrico Bombieri; Jeffrey C. Lagarias
- **Title:** Complements to Li's Criterion for the Riemann Hypothesis
- **Publication:** Journal of Number Theory, 77(2), 274-287
- **Year:** 1999
- **Stable identifier:** DOI `10.1006/jnth.1999.2392` — https://doi.org/10.1006/jnth.1999.2392
- **First verified/accessed:** `2026-08-20T20:37:00Z`
- **Used for:** Zero-sum form of the Li coefficients, generalized positivity framework, arithmetic/explicit-formula connection.
- **Verification notes:** Journal metadata checked; author-hosted PDF was inspected, including the first page showing the Li formula and symmetric zero-sum convention.

### R-0003 — Voros asymptotic Li dichotomy

- **Authors:** André Voros
- **Title:** Sharpenings of Li's Criterion for the Riemann Hypothesis
- **Publication:** Mathematical Physics, Analysis and Geometry, 9, 53-63
- **Year:** 2006
- **Stable identifier:** DOI `10.1007/s11040-005-9002-8`; arXiv `math/0506326` — https://arxiv.org/abs/math/0506326
- **First verified/accessed:** `2026-08-20T20:37:00Z`
- **Used for:** Large-`n` alternative: tame `n log n` behavior on RH versus non-tempered/exponentially amplified oscillatory behavior if RH fails.
- **Verification notes:** arXiv and publication metadata checked. This source, rather than a single-zero heuristic, supports the global growth conclusion used in `F-20260820-002`.

### R-0004 — Generalized Li criterion

- **Authors:** Sergey K. Sekatskii
- **Title:** Generalized Bombieri-Lagarias' Theorem and Generalized Li's Criterion with Its Arithmetic Interpretation
- **Publication:** Ukrainian Mathematical Journal, 66(3), 415-431 in English translation (original pagination 371-383)
- **Year:** 2014
- **Stable identifier:** DOI `10.1007/s11253-014-0940-9`; precursor arXiv `1304.7895` — https://arxiv.org/abs/1304.7895
- **First verified/accessed:** `2026-08-20T20:37:00Z`
- **Used for:** RH-equivalent generalized Li criteria evaluated away from the standard point `s=1`.
- **Verification notes:** arXiv abstract and independent publication metadata checked.

### R-0005 — Arithmetic generalized-Li formula

- **Authors:** Sergey K. Sekatskii
- **Title:** An Arithmetic Interpretation of Generalized Li's Criterion
- **Publication:** arXiv preprint
- **Year:** 2013
- **Stable identifier:** arXiv `1305.1421` — https://arxiv.org/abs/1305.1421
- **First verified/accessed:** `2026-08-20T20:37:00Z`
- **Used for:** Explicit Weil-formula/arithmetic representation of generalized Li sums and the appearance of generalized Laguerre polynomials with von Mangoldt weights.
- **Verification notes:** PDF inspected, including the Laguerre kernel construction and Theorem 1 for `Re(a)>1`. Used together with `R-0006` to fix the center/parameter convention.

### R-0006 — Generalized Li generating functions

- **Authors:** S. K. Sekatskii
- **Title:** Generating Functions for the Generalized Li's Sums
- **Publication:** arXiv preprint
- **Year:** 2014
- **Stable identifier:** arXiv `1411.6209` — https://arxiv.org/abs/1411.6209
- **First verified/accessed:** `2026-08-20T20:37:00Z`
- **Used for:** Taylor generating function of generalized Li sums. For the RH line and center `s0`, this gives the form `log xi(s0+(2s0-1)z/(1-z))`.
- **Verification notes:** arXiv abstract checked. This source makes the `s0>1` generating-function convention explicit.

### R-0007 — NIST DLMF Laguerre formulas

- **Authors:** NIST Digital Library of Mathematical Functions
- **Title:** Chapter 18, Orthogonal Polynomials — Laguerre generating functions, contiguous relations, and asymptotics
- **Publication:** NIST DLMF
- **Year:** continuously maintained
- **Stable identifier:** https://dlmf.nist.gov/18.12.E13 ; https://dlmf.nist.gov/18.9.E13 ; https://dlmf.nist.gov/18.15.E14
- **First verified/accessed:** `2026-08-20T20:37:00Z`
- **Used for:** Exact Laguerre generating function, the degree/parameter contiguous identity used by the shift filter, and fixed-positive-argument large-degree asymptotics.
- **Verification notes:** The contiguous relation was rechecked on `2026-08-20T20:49:00Z`. The asymptotic remains restricted to compact positive `x` intervals and is not uniform across the full prime sum.

### R-0008 — NIST DLMF Chebyshev-psi RH equivalence

- **Authors:** NIST Digital Library of Mathematical Functions
- **Title:** Section 25.16, Mathematical Applications
- **Publication:** NIST DLMF
- **Year:** continuously maintained
- **Stable identifier:** https://dlmf.nist.gov/25.16.E4
- **First verified/accessed:** `2026-08-20T20:37:00Z`
- **Used for:** Established equivalence `RH <=> psi(x)=x+O(x^(1/2+epsilon))` for every `epsilon>0`.
- **Verification notes:** Used as a circularity guard for prime-side estimates.

### R-0009 — Current official RH problem status

- **Authors:** Clay Mathematics Institute
- **Title:** Riemann Hypothesis / Millennium Prize Problems
- **Publication:** Clay Mathematics Institute
- **Year:** current web resource
- **Stable identifier:** https://www.claymath.org/millennium/riemann-hypothesis/ and https://www.claymath.org/millennium-problems/
- **First verified/accessed:** `2026-08-20T20:37:00Z`
- **Used for:** Authoritative current status that RH remains an unsolved Millennium Prize Problem.
- **Verification notes:** Clay's current Millennium Problems page lists RH among the unsolved problems.

### R-0010 — NIST DLMF zeta analytic structure at `s=1`

- **Authors:** NIST Digital Library of Mathematical Functions
- **Title:** Section 25.2, Definition and Expansions — Riemann Zeta Function
- **Publication:** NIST DLMF
- **Year:** continuously maintained
- **Stable identifier:** https://dlmf.nist.gov/25.2 and https://dlmf.nist.gov/25.2.E4
- **First verified/accessed:** `2026-08-20T20:49:00Z`
- **Used for:** The fact that `zeta(s)` is meromorphic with its only singularity a simple pole at `s=1` of residue `1`, and for the Laurent expansion used to isolate the exact pole mode.
- **Verification notes:** DLMF section and equation were checked directly. The pole-removal derivation in `A-20260820-002` is repository work based on this standard analytic fact.

### R-0011 — NIST DLMF uniform Laguerre asymptotics and derivatives

- **Authors:** NIST Digital Library of Mathematical Functions
- **Title:** Sections 18.15(iv) and 18.9(iii) — Laguerre asymptotic approximations and derivatives
- **Publication:** NIST DLMF
- **Year:** continuously maintained; version checked released 2026-06-15
- **Stable identifier:** https://dlmf.nist.gov/18.15 and https://dlmf.nist.gov/18.9.E23
- **First verified/accessed:** `2026-08-20T21:05:31Z`
- **Used for:** Uniform scaling `nu=4N+2alpha+2`, Bessel expansion below the turning point, Airy expansion through and beyond the turning point, and `dL_n^(alpha)/dx=-L_(n-1)^(alpha+1)`.
- **Verification notes:** DLMF 18.15.17, 18.15.19, 18.15.21-22, and 18.9.23 were checked directly. For `N=n-1`, `alpha=1`, `nu=4n` exactly.

### R-0012 — NIST DLMF prime number theorem in Chebyshev-psi form

- **Authors:** NIST Digital Library of Mathematical Functions
- **Title:** Section 25.16(i), Distribution of Primes
- **Publication:** NIST DLMF
- **Year:** continuously maintained
- **Stable identifier:** https://dlmf.nist.gov/25.16.E3
- **First verified/accessed:** `2026-08-20T21:05:31Z`
- **Used for:** `psi(x)=x+o(x)`, sufficient to close the integration-by-parts boundary at infinity for every fixed `n` and `s0>1`.
- **Verification notes:** This is only the prime number theorem, not an RH-strength error estimate.

### R-0013 — Smooth weighted PNT error and zero-free-region converses

- **Authors:** Songlin Han
- **Title:** The Error in a Smooth Weighted Prime Number Formula and Zero-free Regions for the Riemann Zeta Function
- **Publication:** arXiv preprint
- **Year:** 2025; current version checked dated 2026-03-22
- **Stable identifier:** arXiv `2505.23795` — https://arxiv.org/abs/2505.23795
- **First verified/accessed:** `2026-08-20T21:20:00Z`
- **Used for:** Literature guard showing that sufficiently strong errors in a smooth weighted prime number formula have converse implications for zero-free regions; smoothing does not automatically make the zero-location problem weaker.
- **Verification notes:** Current arXiv text and Theorem 1.1 discussion checked. No novelty claim is made for the general principle.

### R-0014 — Mean-square size of the PNT error versus rightmost zeros

- **Authors:** Tianyu Zhao
- **Title:** On the mean values of the error terms in Mertens’ theorems
- **Publication:** Research in Number Theory, 11, article 62
- **Year:** 2025
- **Stable identifier:** DOI `10.1007/s40993-025-00640-y` — https://doi.org/10.1007/s40993-025-00640-y
- **First verified/accessed:** `2026-08-20T21:20:00Z`
- **Used for:** Lemma 8: dyadic mean-square order of `psi(x)-x` in terms of `Theta=sup Re(rho)`, used as a circularity guard against importing RH-scale generic `L^2` bounds.
- **Verification notes:** Open-access published article checked directly, especially Lemma 8 and its two cases.

### R-0015 — Current zero-density/PNT-error framework

- **Authors:** Daniel R. Johnston
- **Title:** Zero-density estimates and the optimality of the error term in the prime number theorem
- **Publication:** arXiv preprint
- **Year:** 2024; current version checked dated 2026-03-22
- **Stable identifier:** arXiv `2411.13791` — https://arxiv.org/abs/2411.13791
- **First verified/accessed:** `2026-08-20T21:20:00Z`
- **Used for:** Current unconditional PNT-error scale derived from zero-free regions and zero-density estimates; in particular the Vinogradov-Korobov form `|psi(x)-x|/x <= exp[-c(log x)^(3/5)(log log x)^(-1/5)]` up to polylogarithmic factors.
- **Verification notes:** Current arXiv version, abstract, Theorem 2.1 framework, and Corollary 2.3 discussion checked. At `log x~cn`, this contributes only `exp[-o(n)]` and therefore cannot by itself remove a positive fixed root rate.

### R-0016 — Lagarias on Li coefficients and Weil's quadratic functional

- **Authors:** Jeffrey C. Lagarias
- **Title:** Li coefficients for automorphic L-functions
- **Publication:** Annales de l'Institut Fourier, 57(5), 1689-1740
- **Year:** 2007
- **Stable identifier:** DOI `10.5802/aif.2311` — https://doi.org/10.5802/aif.2311
- **First verified/accessed:** `2026-08-20T22:15:00Z`
- **Used for:** Spectral/explicit-formula context: Li coefficients are related to values of Weil's quadratic functional on suitable test functions, and their positivity gives an RH criterion in the automorphic setting.
- **Verification notes:** Publisher/Numdam metadata and abstract were checked. This source is contextual support for interpreting the Laguerre phase as spectral structure; the stationary-map derivation in `A-005` is repository work and does not depend on Lagarias for its algebra.

### R-0017 — Arias de Reyna on an ell2 Keiper-Li equivalent of RH

- **Authors:** Juan Arias de Reyna
- **Title:** Asymptotics of Keiper-Li coefficients
- **Publication:** Functiones et Approximatio Commentarii Mathematici, 45(1), 7-21
- **Year:** 2011
- **Stable identifier:** DOI `10.7169/facm/1317045228` — https://doi.org/10.7169/facm/1317045228
- **First verified/accessed:** `2026-08-20T22:15:00Z`
- **Used for:** Circularity/literature guard: the paper proves that a specific `ell^2` condition on the normalized Keiper-Li asymptotic error is equivalent to RH, illustrating that Hilbert-space or square-summability formulations can retain the full conjecture.
- **Verification notes:** Project Euclid DOI metadata and abstract were checked directly. The repository's block-`L2` equivalence `C-0024` is proved independently by elementary inequalities.

### R-0018 — NIST DLMF Bessel large-argument asymptotics and stationary phase

- **Authors:** NIST Digital Library of Mathematical Functions
- **Title:** Sections 10.17(i) and 2.3(iv) — Bessel large-argument expansions and method of stationary phase
- **Publication:** NIST DLMF
- **Year:** continuously maintained; version checked 2026-08-20
- **Stable identifier:** https://dlmf.nist.gov/10.17 and https://dlmf.nist.gov/2.3.iv
- **First verified/accessed:** `2026-08-20T22:15:00Z`
- **Used for:** `J_1(z)` large-positive-argument phase `z-3pi/4` and the standard stationary-phase asymptotic used to analyze the fixed-frequency pre-turning saddle.
- **Verification notes:** Equations 10.17.2-3 and DLMF section 2.3(iv) were checked directly. These are combined with the Laguerre Bessel expansion already registered as `R-0011`.

### R-0019 — NIST DLMF global Laguerre inequality

- **Authors:** NIST Digital Library of Mathematical Functions
- **Title:** Section 18.14(i), Inequalities for Laguerre Polynomials
- **Publication:** NIST DLMF
- **Year:** continuously maintained; version checked 2026-08-20
- **Stable identifier:** https://dlmf.nist.gov/18.14.E8
- **First verified/accessed:** `2026-08-20T22:44:00Z`
- **Used for:** The global bound `e^(-x/2)|L_n^(alpha)(x)|<=L_n^(alpha)(0)` for `x>=0`, `alpha>=0`, used to close the below-first-prime and shrinking-left-endpoint contributions without RH-strength prime information.
- **Verification notes:** Equation 18.14.8 checked directly; for `alpha=1`, `L_(n-1)^(1)(0)=n`.

### R-0020 — Montgomery and Vaughan mean-value length term

- **Authors:** H. L. Montgomery; R. C. Vaughan
- **Title:** Hilbert's Inequality
- **Publication:** Journal of the London Mathematical Society, Series 2, 8(1), 73-82
- **Year:** 1974
- **Stable identifier:** DOI `10.1112/jlms/s2-8.1.73` — https://doi.org/10.1112/jlms/s2-8.1.73
- **First verified/accessed:** `2026-08-20T22:44:00Z`
- **Used for:** Classical Hilbert-inequality/Dirichlet-polynomial mean-value framework yielding the standard `(T+O(N)) sum |a_n|^2` scale, used to quantify why generic one-dimensional mean values retain the exponential polynomial-length barrier in `A-006`.
- **Verification notes:** Publisher metadata and the original paper were checked; a modern published statement of the Dirichlet-polynomial mean-value theorem was also cross-checked.

### R-0021 — Helfgott treatment of Vaughan's identity and Type I/II sums

- **Authors:** Harald Andrés Helfgott
- **Title:** The ternary Goldbach problem
- **Publication:** monograph/preprint
- **Year:** 2015
- **Stable identifier:** arXiv `1501.05438` — https://arxiv.org/abs/1501.05438
- **First verified/accessed:** `2026-08-21T02:09:00Z`
- **Used for:** Explicit Vaughan identity, free truncation parameters `U,V`, and the standard Type I/Type II decomposition of prime exponential sums.
- **Verification notes:** Section 3.3.1 and the surrounding Type I/II discussion were checked directly; equation (3.6) gives the convolution identity used as literature context in `A-20260821-001`.

### R-0022 — Graham and Kolesnik on two-dimensional van der Corput methods

- **Authors:** S. W. Graham; Grigori Kolesnik
- **Title:** Van der Corput's Method of Exponential Sums
- **Publication:** London Mathematical Society Lecture Note Series 126, Cambridge University Press
- **Year:** 1991; digital edition 2010
- **Stable identifier:** DOI `10.1017/CBO9780511661976`
- **First verified/accessed:** `2026-08-21T02:09:00Z`
- **Used for:** Standard reference context for one- and two-dimensional exponential-sum methods and the idea that multidimensional phase curvature can yield cancellation when genuinely present.
- **Verification notes:** Book metadata and Chapter 6, "Two Dimensional Exponential Sums," were checked. The rank-one obstruction in `A-20260821-001` is derived independently.

### R-0023 — Montgomery and Vaughan modern framework for prime exponential and bilinear sums

- **Authors:** Hugh L. Montgomery; Robert C. Vaughan
- **Title:** Multiplicative Number Theory II: Primes and Sieves — Chapters 16-17 and Appendix G
- **Publication:** Cambridge University Press
- **Year:** 2026
- **Stable identifier:** Chapter 16 DOI `10.1017/9781009445030.002`; Chapter 17 DOI `10.1017/9781009445030.003`
- **First verified/accessed:** `2026-08-21T02:09:00Z`
- **Used for:** Current standard context for van der Corput estimates, estimates for sums over primes, the large sieve, and bilinear-form bounds.
- **Verification notes:** Publisher chapter metadata and summaries were checked. No theorem from this source is used to assert a stronger bound than what is derived explicitly in the repository.

### R-0024 — Bombieri on Weil's quadratic functional

- **Authors:** Enrico Bombieri
- **Title:** Remarks on Weil's quadratic functional in the theory of prime numbers, I
- **Publication:** Rendiconti Lincei - Matematica e Applicazioni, 11(3), 183-233
- **Year:** 2000
- **Stable identifier:** EuDML record `252338` — https://eudml.org/doc/252338
- **First verified/accessed:** `2026-08-21T02:26:00Z`
- **Used for:** Full Weil-functional PSD iff RH; variational formulation on compact-support Hilbert spaces; unconditional positive-definiteness for sufficiently small support; finite truncation/eigenvalue context.
- **Verification notes:** Published metadata and abstract checked directly through EuDML/BDIM. The repository's compressed-translation norm formula is derived independently.

### R-0025 — Connes and Consani on archimedean Weil positivity

- **Authors:** Alain Connes; Caterina Consani
- **Title:** Weil positivity and trace formula, the archimedean place
- **Publication:** Selecta Mathematica (N.S.) 27(4), Paper 77
- **Year:** 2021
- **Stable identifier:** DOI `10.1007/s00029-021-00689-4`; arXiv `2006.13771`
- **First verified/accessed:** `2026-08-21T02:26:00Z`
- **Used for:** Conceptual operator-theoretic explanation of archimedean-place Weil positivity, using compressed scaling, Sonin/prolate structure, and Hermitian Toeplitz matrices; prime-free support context.
- **Verification notes:** Publisher/author metadata, abstract, and arXiv record checked. Their result supplies literature context and a possible operator toolkit for `A-20260821-003`.

### R-0026 — Berg, Christensen, and Ressel on positive/negative definite kernels

- **Authors:** Christian Berg; Jens Peter Reus Christensen; Paul Ressel
- **Title:** Harmonic Analysis on Semigroups: Theory of Positive Definite and Related Functions
- **Publication:** Graduate Texts in Mathematics 100, Springer
- **Year:** 1984
- **Stable identifier:** DOI `10.1007/978-1-4612-1128-0`
- **First verified/accessed:** `2026-08-21T02:26:00Z`
- **Used for:** Standard positive-definite, negative-definite, moment, Bochner/Herglotz, and Schoenberg-type harmonic-analysis framework used to interpret the Li sequence.
- **Verification notes:** Springer book metadata and chapter structure checked; the Li CND calculation itself is repository-derived.

### R-0027 — Suzuki on screw functions and Weil hermitian forms

- **Authors:** Masatoshi Suzuki
- **Title:** Aspects of the screw function corresponding to the Riemann zeta-function
- **Publication:** Journal of the London Mathematical Society
- **Year:** 2023
- **Stable identifier:** DOI `10.1112/jlms.12785`
- **First verified/accessed:** `2026-08-21T02:26:00Z`
- **Used for:** Modern integral-operator/hermitian-form versions of Weil positivity and nondegeneracy criteria on compact-support spaces.
- **Verification notes:** Published theorem summaries checked; used as operator-framework context, not as a dependency of the elementary compressed-shift derivation.

### R-0028 — Suzuki 2026 finite-support Weil quadratic form

- **Authors:** Masatoshi Suzuki
- **Title:** Weil's quadratic form via the screw function
- **Publication:** arXiv preprint
- **Year:** 2026; version checked dated `2026-08-19`
- **Stable identifier:** arXiv `2606.09096` — https://arxiv.org/abs/2606.09096
- **First verified/accessed:** `2026-08-21T04:06:54Z`
- **Used for:** Authoritative finite-support normalization in `A-20260821-003`, including the self-adjoint localized operator, the prime-power finite symbol, the separate finite-support residual kernel, the scaled Rayleigh-quotient form, and `c_T=log(2*pi*T)+EulerGamma` normalization.
- **Verification notes:** Current arXiv text was checked directly. The paper explicitly emphasizes that its results do not assume RH and places Bombieri, Yoshida, and Connes-Consani in a unified finite-support framework.

### R-0029 — Connes and Consani on prime-threshold numerical compensation

- **Authors:** Alain Connes; Caterina Consani
- **Title:** Spectral triples and zeta-cycles
- **Publication:** L'Enseignement Mathématique, 69(1/2), 93-148
- **Year:** 2023
- **Stable identifier:** DOI `10.4171/LEM/1049`
- **First verified/accessed:** `2026-08-21T04:06:54Z`
- **Used for:** Published finite-matrix/core context and numerical observation that the localized archimedean low eigenvalue deteriorates at the first prime threshold while adding the `p=2` term restores positivity through the interval before `p=3` in their support convention.
- **Verification notes:** EMS Press metadata and the open-access paper were checked. The numerical compensation is literature context only, not a proof of first-prime positivity.

### R-0030 — NIST DLMF digamma representations

- **Authors:** NIST Digital Library of Mathematical Functions
- **Title:** Section 5.9(ii) — Psi Function, Euler's Constant, and Derivatives
- **Publication:** NIST DLMF
- **Year:** continuously maintained; version checked `2026-08-21`
- **Stable identifier:** https://dlmf.nist.gov/5.9.ii
- **First verified/accessed:** `2026-08-21T04:06:54Z`
- **Used for:** Standard digamma representations supporting the positive exponential-kernel decomposition in `C-0043`.
- **Verification notes:** Section 5.9(ii), including the standard integral/series representations for `psi`, was checked directly. The nonnegative-kernel decomposition is derived in the repository.

### R-0031 — Public `weil-first-prime` proof-code candidate

- **Authors:** GitHub repository `telleroutlook/weil-first-prime`
- **Title:** `weil-first-prime` — certificate-first proof infrastructure for FP-0.35
- **Publication:** Public source-code repository
- **Year:** 2026
- **Stable identifier:** https://github.com/telleroutlook/weil-first-prime ; pinned source audit commit `e66f467bc4447c5b2491577cbb6c3ae0e721fb43`
- **First verified/accessed:** `2026-08-21T04:06:54Z`
- **Used for:** External proof-architecture comparison and adversarial source audit only. The project claims finite-scale positivity at `T=7/20`; this repository does not import that theorem status.
- **Verification notes:** A temporary isolated clone of the pinned commit was inspected. The README currently reports FP-0.35 as holding while also listing the trusted proof-chain/replay work as in progress. Specific checker-path inconsistencies are documented in `F-20260821-015`. Treat this source as unverified proof code, not mathematical authority.

## Entry format

```markdown
### R-0001 — Short label

- **Authors:** ...
- **Title:** ...
- **Publication:** ...
- **Year:** ...
- **Stable identifier:** DOI / arXiv / ISBN / canonical URL
- **First verified/accessed:** YYYY-MM-DDTHH:MM:SSZ
- **Used for:** ...
- **Verification notes:** ...
```
