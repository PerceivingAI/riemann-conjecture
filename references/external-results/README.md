# External Mathematical Results

This directory records externally authored mathematical results that may be used by this repository.

External-result IDs use the `EXT-` namespace so they cannot be confused with repository-derived `C-` claims or `F-` findings.

**OAI-7 governing trust boundary:** [`docs/CONTRACTS.md`, Section 5](../../docs/CONTRACTS.md) and [`docs/PROTOCOL.md`, Section 7.2](../../docs/PROTOCOL.md) distinguish external theorem attribution, locally checked deductions, local Lean-kernel results, and independently accepted exact certificates. Source integrity and upstream formalization do not imply a local proof replay. Independent replay is optional for **cited mathematical use** but cannot be claimed unless actually performed.

An `EXT-` record is a provenance object, not a claim of authorship by this project. Each record must identify the external author/source, an immutable upstream revision when source code is involved, the exact mathematical statement, formal theorem/source identifiers when available, licensing/provenance information, and the repository's own verification status.

Independent replay or adoption into the repository trust chain is a separate step. A record that has not yet been independently replayed must say so explicitly.

For `EXT-0001`, see `EXT-0001-openai-quasi-rh.md` for source provenance and
[`EXT-0001-lean-overlap-audit.md`](EXT-0001-lean-overlap-audit.md) for the
OAI-3 pinned Mathlib / OpenAI theorem-and-dependency classification.
Independent replay is optional; the absence of a replay must remain explicit.
For the OAI-4 route-by-route mathematical impact audit, see
[`EXT-0001-route-impact-audit.md`](EXT-0001-route-impact-audit.md).
OAI-6 source-reuse and licensing policy: [`EXT-0001-reuse-and-license-decision.md`](EXT-0001-reuse-and-license-decision.md).
The current decision is **reference-only**; imported sources, vendored proof files,
forks and new toolchain dependencies require a separate named consumer, rights
review and verification gate.

## OAI-9 — Current verification and optional replay workflow

1. **Locate/pin:** Read [`EXT-0001-openai-quasi-rh.md`](EXT-0001-openai-quasi-rh.md), including its **maintained OAI-9 status**, `R-0034`, and the pinned source commit/tree/blob identities. The authoritative solution is `OAI.NumberTheory.DirichletL.Nonvanishing`; the Comparator *challenge template* is not the completed proof.
2. **Check source integrity without asserting a proof:** On the separate detached upstream checkout verify `git rev-parse HEAD`, `git show -s --format=%T HEAD`, and `git ls-tree HEAD -- <relevant-repo-relative-file>` against the pinned identities. Source integrity `PASS` is not an independent kernel/Comparator proof replay.
3. **Use mathematically:** Depend on `EXT-0001` explicitly for `C-0060..C-0062`. Report `VERIFIED` only for the specific **written deductions** and cite their `F-` and classical `R-` dependencies. Do not claim local kernel verification or treat the external theorem as a new repository proof.
4. **Optional independent replay:** Only if a *separately authorized* need arises, provision an isolated compatible Linux execution environment with real required sandbox enforcement, pin Lean `v4.34.1`, upstream Mathlib and actual Comparator/Lake dependencies, compile/check the named solution and run the genuine Comparator challenge. Record versions, exact commands, checks, assumptions, PASS/FAIL and sanitized evidence. No secure runner or independent replay has been validated by this repository yet. OAI-1.3 dependency candidates are **not** a completed replay.
5. **Keep proof admission separate:** External mathematical use does not alter the frozen eight v1 retained claims, empty v2 admission list, Arb/Rust certificate PASS, or RH `UNRESOLVED`. For definitions see [`docs/CONTRACTS.md` §5](../../docs/CONTRACTS.md) and [`docs/PROTOCOL.md` §7.2](../../docs/PROTOCOL.md).

**Reuse decision:** Reference-only. No OpenAI source is vendored or imported; optional future source import must pass the explicit [OAI-6 license and dependency gates](EXT-0001-reuse-and-license-decision.md). The local original repository is MIT OR Apache-2.0; copied OpenAI code would retain its own Apache-2.0 requirements. See the [research-direction decision](../../research/openai-math/RESEARCH_DIRECTION.md).

The OAI-5 mathematical consequences are recorded separately in
[`F-20261008-002`](../../findings/2026-10-08T024431Z-openai-seven-eighths-prime-distribution.md); the classical explicit-formula source is `R-0035`.
