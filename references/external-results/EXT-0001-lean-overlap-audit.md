# OAI-3 — Formal mathematics overlap and reuse audit

- **Recorded:** `2026-10-08T01:58:15Z` (UTC)
- **Status:** `COMPLETE — TARGETED SOURCE AUDIT`
- **External source:** `EXT-0001`, `openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`
- **OpenAI-pinned Mathlib:** `leanprover-community/mathlib4@d13f23b723b8a846827a245b89c10fc7d3f11612`
- **Local formal toolchain:** Lean `v4.33.0`, Mathlib `db584cd6d46c92f209a44c0f1c829460d327499d`
- **OpenAI formal toolchain:** Lean `v4.34.1`
- **Scope:** Source-level overlap, precise theorem hypotheses, focused import/dependency mapping, and reuse classification. No Lean build, full transitive import closure, proof replay, theorem admission, or source import is claimed.

## OAI-3.1 — Current repository formal inventory

The local Lean library has only `formal/Cert.lean` and these four modules:

| Module | Existing proof scope | Overlap decision |
| --- | --- | --- |
| `formal/Cert/Interval.lean` | Rational interval enclosures and operation/strict-positivity soundness | Retain; not provided by the inspected OpenAI nonvanishing proof |
| `formal/Cert/LDL.lean` | Rational LDL and positive-definite certificate soundness | Retain; uses existing Mathlib matrix machinery |
| `formal/Cert/Gershgorin.lean` | Symmetric strict-row-dominance positivity and invertible congruence | Retain; **already imports** `Mathlib.LinearAlgebra.Matrix.Gershgorin` and `Mathlib.Analysis.Matrix.PosDef` |
| `formal/Cert/EndpointAbsorption.lean` | Bounds for `log 2`, `sqrt 2`, endpoint coercivity, and first-prime absorption at `T=7/20` | Retain; no matching OpenAI theorem established |

The local formal tree does **not** contain a zeta zero-free-half-plane proof, Dirichlet-`L` nonvanishing theorem, or Lean formalization of the full `C-0010` Cayley/Laguerre criterion. Conversely, inspection of the OpenAI theorem chain does not yield a direct replacement for our exact interval/Gershgorin/LDL soundness layer or the localized Weil `C-0048` Schur estimate.

## OAI-3.2 — Existing pinned Mathlib results: class A

These declarations and source paths were inspected at **OpenAI's locked Mathlib revision**, not inferred from current branches.

| Mathlib source | Exact relevant declaration or capability | Reuse boundary |
| --- | --- | --- |
| `Mathlib/NumberTheory/ArithmeticFunction/VonMangoldt.lean` | `ArithmeticFunction.vonMangoldt`, `vonMangoldt_apply`, `vonMangoldt_sum`, `vonMangoldt_mul_zeta` | Prime-power and Mangoldt arithmetic already formalized; reuse rather than re-prove |
| `Mathlib/NumberTheory/LSeries/Dirichlet.lean` | `ArithmeticFunction.LSeries_vonMangoldt_eq_deriv_riemannZeta_div` under `1 < s.re`: `L ↗Λ s = - deriv riemannZeta s / riemannZeta s` | Direct match for the standard arithmetic/zeta log-derivative identity, **only in `Re(s)>1`**; does not provide zero-free continuation to `7/8` |
| `Mathlib/NumberTheory/LSeries/Nonvanishing.lean` | `riemannZeta_ne_zero_of_one_le_re` for `1 ≤ s.re`; `DirichletCharacter.LFunction_ne_zero_of_one_le_re` with `χ ≠ 1 ∨ s ≠ 1` | Established nonvanishing in the classical right half-plane; strictly weaker region than OpenAI's result |
| `Mathlib/NumberTheory/LSeries/RiemannZeta.lean` | `riemannZeta`, `differentiableAt_riemannZeta`, functional equation and `riemannZeta_residue_one` | Existing zeta analytic foundation; no need to recreate |
| `Mathlib/NumberTheory/LSeries/ZetaZeros.lean` | `riemannZetaZeros`, `mem_riemannZetaZeros`, `isDiscrete_riemannZetaZeros`, `IsCompact.inter_riemannZetaZeros_finite` | Existing zero-set vocabulary and compact finiteness for potential formal consequences |
| `Mathlib/NumberTheory/LSeries/Deriv.lean` | `LSeries_deriv` and differentiability/series-control lemmas | Existing Dirichlet-series differentiation |
| `Mathlib/LinearAlgebra/Matrix/Gershgorin.lean` | Gershgorin eigenvalue/invertibility results | Already used by our `Cert/Gershgorin.lean`; no parallel implementation needed |
| `Mathlib/LinearAlgebra/Matrix/SchurComplement.lean` | Finite block-matrix Schur determinant and invertibility identities | Algebraic support only; **not** a ready formal theorem for the infinite-dimensional localized Weil positivity/tail-Gram bound `C-0048` |

The Mathlib zeta function is totalized at `s=1`, with a nonzero designated value; the source explicitly explains why its `riemannZeta_ne_zero_of_one_le_re` statement does not exclude `s=1`. This is a semantic detail to preserve when comparing Lean statements with the usual meromorphic zeta notation.

**No local upgrade is implied:** These declarations were inspected at `d13f...`, while our already-retained Lean certificates use the distinct `v4.33.0` / `db584...` environment. An API-compatible upgrade must be independently justified, not presumed.

## OAI-3.3 — New or distinct OpenAI results: class B

The checked declarations are:

1. `lean/OAI/NumberTheory/DirichletL/Nonvanishing.lean`:
   `OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re` states, for **every** `s : ℂ`, `7/8 < s.re → riemannZeta s ≠ 0`. There is **no extra `s ≠ 1` hypothesis**.
2. The same source:
   `OAI.DirichletCharacter.LFunction_ne_zero_of_seven_eighths_lt_re` assumes `q : ℕ` with `[NeZero q]`, `χ : DirichletCharacter ℂ q`, `7/8 < s.re`, and `¬ (χ = 1 ∧ s = 1)`. This is a more general L-function result but must **not** be represented as unconditional nonvanishing at the principal-character pole.
3. `lean/OAI/NumberTheory/DirichletL/RowCompletion/ZeroFreeRegion.lean` contains `ShortDraft.riemannZeta_ne_zero_of_re_gt` using **`23/24 < s.re` and `s ≠ 1`**. It is strictly weaker for our intended use; do not confuse it with the final `7/8` theorem.
4. `lean/OAI/NumberTheory/DirichletL/Detector/FinalAssemblyCertifiedBands.lean` exposes `DetectorCertifiedBands`, `dirichlet_of_certified`, and `zeta_of_certified`; `Detector/FinalAssemblyUnconditional.lean` discharges the certificate and supplies the final `zeta_nonzero`. These are theorem-specific proof architecture, not ready replacements for our rational interval/matrix certificate format.

**Hypothesis and equivalence decision:** The OpenAI zeta theorem strictly extends the known Mathlib `Re(s)≥1` zero-free region into `Re(s)>7/8`; neither theorem states RH. The OpenAI Dirichlet-character result has a separate pole-exclusion hypothesis. Importing a Lean declaration into our `formal/` code is *not* currently required to use `EXT-0001` as an explicitly attributed external mathematical input. `C-0060` and `F-20261008-001` remain our derived consequences, not claims that our Lean kernel compiled the external proof.

## OAI-3.4 — Focused source/dependency graph and cost

Verified import edges:

```text
OAI.NumberTheory.DirichletL.Nonvanishing
  ├─ OAI.NumberTheory.DirichletL.Foundation
  │    └─ 286 direct import declarations (wide analytic/arithmetic foundation)
  └─ OAI.NumberTheory.DirichletL.Detector.FinalAssemblyUnconditional
       ├─ OAI.NumberTheory.DirichletL.Energy.CertifiedExistence
       ├─ OAI.NumberTheory.DirichletL.Detector.FinalAssemblyCertifiedBands
       └─ OAI.NumberTheory.DirichletL.Moments.DetectorPlainSlotProfile
```

The inspected `FinalAssemblyCertifiedBands` imports further detector, energy, and fine-field modules. The `DirichletL` subtree contains **2,926 `.lean` files**; this is its total source-file count, **not** a claim that all are transitively imported by the target theorem.

The upstream `lean/lake-manifest.json` pins **42 packages** overall, including Mathlib, `PrimeNumberTheoremAnd`, `StrongPNT`, `leancert`, and `PrimeCert`. Again, this is the whole package manifest, **not** proof that every package is required in the minimal theorem import closure.

Other inspected provenance edge: `PrimeCounting/Progressions.lean` imports `PrimeNumberTheoremAnd.Wiener`, which comes from an independently pinned package. This module gives qualitative arithmetic-progression prime-mass asymptotics, not an unconditional `psi(x)-x=O(x^{7/8})` theorem.

**Cost assessment:** Importing or vendoring the full OpenAI proof closure would require nontrivial package/version reconciliation and a fresh trust/build qualification. A complete transitive file-by-file closure, minimum build footprint, and actual compilation cost were **not** measured; no lightweight source extraction is claimed viable.

## OAI-3.5 — Classification

| Class | Candidate | Conclusion |
| --- | --- | --- |
| **A — Existing Mathlib** | Mangoldt definitions/identities; zeta basic analytic facts, residues/functional equation, the `Re(s)≥1` nonvanishing theorem, zero-set facts; matrix Gershgorin/Schur algebra | **Reuse existing foundations.** Most are already imported indirectly in the existing local formal layer. Do not duplicate. |
| **B — Useful OpenAI** | `OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re` | **Retain as pinned external theorem `EXT-0001`**, with mathematical deductions kept separate. Highest direct value. |
| **B — Conditional future relevance** | General Dirichlet-`L` `7/8` theorem; `DetectorCertifiedBands` mechanism | Consider only if a future route genuinely needs characters or a formal proof of a new detector implication. No source import now. |
| **C — No current direct need** | Arithmetic-progression qualitative PNT, Eisenstein/Hecke-specific ideal log derivatives, weaker `23/24` result | Not a drop-in proof of square-root prime cancellation, localized Weil positivity, or RH. |
| **D — Too heavy without a concrete consumer** | Wholesale OpenAI `Foundation`/detector/energy proof closure and its package stack; wholesale version upgrade | **Do not vendor or merge** under OAI-3. Package/build burden is disproportionate without a named Lean target. |

### Explicit non-equivalences / gaps

- `ArithmeticFunction.LSeries_vonMangoldt_eq_deriv_riemannZeta_div` is an identity on `Re(s)>1`, **not** an estimate for `psi(x)-x` or the local Laguerre chirp (`C-0028`, `C-0034`).
- Mathlib's finite matrix Schur-complement identities are **not** the independently certified infinite-tail coercivity plus grouped `V,P,R` theorem (`C-0048`, `C-0059`).
- OpenAI's half-plane theorem places zeros inside a narrower strip, but it does **not** eliminate all possible off-line modes, prove the `C-0010` root bound `≤1`, or supply new finite-support `T,N` admissions.
- Exact equivalence of definitions and any prospective Lean imports beyond the inspected declarations would need a separate type-check/build. No claim of a Mathlib-wide negative search or full-import graph is made.

## Actionable consequences and acceptance boundary

1. **OAI-4:** Audit individual research routes against only the exact `EXT-0001` half-plane and any independently derived consequences. Preserve the boundary `1/2<Re(rho)≤7/8` as an unresolved possibility.
2. **OAI-5:** Derive any proposed prime-counting or smoothed-error consequences with the actual explicit-formula hypotheses and error terms; do not insert an assumed `O(x^{7/8})` estimate.
3. **OAI-6:** Default to no vendoring. Re-evaluate version upgrades or minimal Lean imports only after a named consumer and a proven need.
4. **OAI-7 onward:** Keep OpenAI formal provenance, our mathematical deductions, our local Lean soundness, and Rust/Arb certificate acceptance as distinct trust boundaries.

**Verification performed:** Read-only exact upstream Git status/commit check, local four-module Lean inventory, pinned Mathlib source inspection, exact theorem/hypothesis comparison, focused import-edge inspection, upstream manifest parsing, and module/file counts. **Not performed:** full transitive proof closure, Lean compilation, independent Comparator replay, OAI-4 mathematical route audits, or any certificate modification.

**Privacy:** Only upstream/public source identities, repository-relative paths, version pins and mathematical conclusions are recorded. No host/environment inventory, private path, user identity, credential, or raw execution log is included.
