# EXT-0001 — OpenAI quasi-Riemann zero-free half-plane

- **External result ID:** `EXT-0001`
- **Recorded:** `2026-10-07T10:06:02Z`
- **Authorship:** OpenAI
- **Repository:** `https://github.com/openai/math`
- **Pinned upstream commit:** `adc7f1241b42e322a6451854ab7e4b4c146bf78a`
- **Pinned tree:** `a8e3481a92772ee311cdc9dd6409cd7b927a3fc1`
- **Upstream commit date:** `2026-10-06T21:58:50Z`
- **Upstream commit signature status:** unsigned according to GitHub commit metadata
- **License:** Apache License 2.0
- **Repository status:** external theorem provenance recorded; independent local replay not yet performed

## Mathematical statement

OpenAI's formal theorem states:

```text
For s in C, if Re(s) > 7/8, then zeta(s) != 0.
```

The exact Lean declaration is:

```lean
OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re
```

from:

```text
lean/OAI/NumberTheory/DirichletL/Nonvanishing.lean
```

This record does **not** assign the theorem a repository `C-` claim ID and does not represent it as work proved by this project.

## Upstream formal provenance

Pinned source identities at the recorded commit:

| Item | Upstream path | Git blob SHA |
| --- | --- | --- |
| Riemann-zeta nonvanishing theorem | `lean/OAI/NumberTheory/DirichletL/Nonvanishing.lean` | `46c67f4000906b1391a471d6e6396ac0da3c16a5` |
| Comparator configuration | `lean/ComparatorChallenges/QuasiRiemannHypothesis.json` | `acf552468fc23c1a27d685d33983c58c50040542` |
| Lean toolchain | `lean/lean-toolchain` | `ba8ebf2dbaf6a668cd2a0e086186d6d569b69ff5` |
| Lake manifest | `lean/lake-manifest.json` | `67d01d2717d0aaff59fb8814bb53581b961f42b4` |
| Lake package definition | `lean/lakefile.lean` | `66c3867331c7c607ffc0e60955cc86cccf046e12` |
| License | `LICENSE` | `261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64` |
| Manuscript citation metadata | `preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/README.md` | `05daa0838d60781c338ac22a9b06e6990f970981` |

The Comparator configuration identifies:

```text
challenge_module:
  ComparatorChallenges.QuasiRiemannHypothesis

solution_module:
  OAI.NumberTheory.DirichletL.Nonvanishing

theorem:
  OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re

permitted axioms:
  propext
  Quot.sound
  Classical.choice

enable_nanoda:
  false
```

The pinned formal environment uses:

```text
Lean:    leanprover/lean4:v4.34.1
Mathlib: d13f23b723b8a846827a245b89c10fc7d3f11612
```

The upstream package is `OAI`, version `0.1.0`, with a fixed toolchain.

## Manuscript provenance

- **Author:** OpenAI
- **Title:** *The Quasi-Riemann Hypothesis: A Zero-Free Half-Plane Re(s)>7/8*
- **Date:** 30 September 2026
- **Publication form:** OpenAI Math Release preprint
- **Upstream directory:** `preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/`
- **Bibliography entry in this repository:** `R-0034`
- **Upstream citation key:** `OAI:The-Quasi-Riemann-Hypothesis-September-30-2026`

The upstream preprint supplies the following BibTeX verbatim:

```bibtex
@misc{OAI:The-Quasi-Riemann-Hypothesis-September-30-2026,
  author = {{OpenAI}},
  title = {{The Quasi-Riemann Hypothesis:
            A Zero-Free Half-Plane $\mathrm{Re}(s)>7/8$}},
  howpublished = {OpenAI Math Release preprint
                  \href{https://github.com/openai/math/blob/main/preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/paper.pdf}{OAI:The-Quasi-Riemann-Hypothesis-September-30-2026}},
  year = {2026}
}
```

The `blob/main` URL above is part of OpenAI's supplied citation, **not** this repository's verification or source pin. The provenance authority for OAI-0 is the exact upstream commit and blob identities recorded above.

## License and reuse boundary

The pinned repository is distributed under Apache-2.0.

At OAI-0 this repository copies **no OpenAI source code**. It records identifiers, metadata, the external theorem statement, and attribution only.

If a later phase vendors or modifies OpenAI source, Apache-2.0 redistribution requirements must be handled explicitly at that time. Citation or mathematical dependence alone does not require vendoring the source.

## OAI-0 verification snapshot (2026-10-07; historical)

OAI-0 establishes provenance only.

```text
upstream source pinned:            YES
theorem/source identity recorded:  YES
license recorded:                  YES
formal environment recorded:       YES
manuscript citation recorded:      YES
independent replay by this repo:    NOT YET
imported into formal/:             NO
vendored OpenAI source:            NO
repository C-claim assigned:       NO
used to alter theorem admission:   NO
```

Independent Comparator replay is **optional** additional assurance, not a prerequisite for using the properly attributed external theorem as a mathematical dependency. The upstream proof has **not** been independently replayed by this repository; do not describe it as independently verified here. The source identity was separately checked against a clean detached checkout at the pinned revision. Mathematical consequences derived here remain distinct from OpenAI's original theorem and must cite `EXT-0001`.

## OAI-9 accepted status — `2026-10-08T03:38:44Z`

This is the **maintained** status; the OAI-0 snapshot above describes only the initial provenance phase. Its dated statements are preserved rather than rewritten.

```text
external authored theorem:                 EXT-0001 (OpenAI)
pinned upstream commit/tree/blobs:         VERIFIED against clean detached checkout
upstream mathematical statement:           Re(s)>7/8 -> zeta(s) != 0
upstream formal solution source:           IDENTIFIED (Nonvanishing.lean)
Comparator challenge/solution mapping:     CHECKED
independent local Comparator replay:       NOT PERFORMED (optional)
Linux Comparator provisioning:             NOT COMPLETED / no validated secure runner
local Lean kernel import/build of theorem: NOT PERFORMED
vendored or imported upstream source:      NO
locally derived written consequences:      C-0060, C-0061, C-0062
new exact Weil theorem or RH claim:         NO
```

**Critical source distinction:** `lean/OAI/NumberTheory/DirichletL/Nonvanishing.lean` is OpenAI's supplied solution declaration. The separately mapped `lean/ComparatorChallenges/QuasiRiemannHypothesis.lean` is a *challenge template* containing `sorry`; it is **not** itself the completed proof. Neither the template nor this repository's source-hash checks constitute a local proof replay. The pinned Comparator JSON selects the solution module and permits `propext`, `Quot.sound`, and `Classical.choice`, with `enable_nanoda=false`.

At OAI-1, frozen source integrity and version candidates were investigated; isolated Linux/Comparator/real Landrun/systemd replay was **not completed**. The project subsequently chose independent replay to be **optional** because OAI-2 through OAI-8 depend mathematically on an explicitly attributed external theorem, not on a claim that our Lean kernel has compiled it. No local tool setup or insecure fallback is authorized by this documentation.

**Current downstream dependencies:** [`C-0060` / `F-20261008-001`](../../findings/2026-10-08T014258Z-openai-quasi-rh-cayley-consequence.md) confines nontrivial zeros to `1/8<=Re(rho)<=7/8` and gives a fixed-center Cayley root upper rate strictly above `1`; [`C-0061`/`C-0062` / `F-20261008-002`](../../findings/2026-10-08T024431Z-openai-seven-eighths-prime-distribution.md) derive classical explicit-formula prime errors and compactly smoothed half-weight error bounds using `R-0035`. These are **verified written mathematical deductions conditional on EXT-0001**, not local Lean proofs. The [OAI-8 route decision](../../research/openai-math/RESEARCH_DIRECTION.md) keeps localized Weil/Legendre–Schur primary, phase-aware arithmetic secondary and a hybrid deferred; neither RH nor a new v2 theorem is admitted.

**Replay reference for a future *optional* independent check:** retain this exact commit/tree/selected blobs; use the frozen Comparator configuration and solution module, Lean `v4.34.1`, Mathlib `d13f23b723b8a846827a245b89c10fc7d3f11612`, and record the actual isolated runner's supported security controls, all pinned extra dependency revisions, successful kernel/Comparator results and sanitizer-reviewed evidence. Comparator/Lean 4.34.0 candidates identified during OAI-1.3 are **not accepted as a verified 4.34.1 replay**. Do not report completion until the real isolated workflow passes. See [the external-results README](README.md) for the check order, [OAI-3 overlap](EXT-0001-lean-overlap-audit.md), [OAI-6 reuse decision](EXT-0001-reuse-and-license-decision.md), and [`docs/CONTRACTS.md` §5](../../docs/CONTRACTS.md) for the trust boundary.

## Relationship to existing work

No v1/v2 certificate, Rust verifier, Arb generator, retained theorem, or RH-status statement is changed by this provenance record.

Any future repository-derived statement using this theorem must distinguish the external dependency `EXT-0001` from the new deduction made by this project.
