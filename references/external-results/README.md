# External Mathematical Results

This directory records externally authored mathematical results that may be used by this repository.

External-result IDs use the `EXT-` namespace so they cannot be confused with repository-derived `C-` claims or `F-` findings.

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

The OAI-5 mathematical consequences are recorded separately in
[`F-20261008-002`](../../findings/2026-10-08T024431Z-openai-seven-eighths-prime-distribution.md); the classical explicit-formula source is `R-0035`.
