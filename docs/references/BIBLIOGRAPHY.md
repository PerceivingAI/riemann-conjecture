# Research Bibliography

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T20:49:00Z`

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
