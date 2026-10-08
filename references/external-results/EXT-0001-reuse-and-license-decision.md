# OAI-6 — Source reuse, licensing, and vendoring decision for EXT-0001

- **Recorded:** `2026-10-08T03:00:21Z` (UTC)
- **Corrected:** `2026-10-08T03:03:46Z` (UTC) — existing repository dual-license files were missed in the initial root-filename check.
- **Decision status:** `COMPLETE — REFERENCE-ONLY DEFAULT`
- **Upstream:** `https://github.com/openai/math`
- **Immutable pin:** `adc7f1241b42e322a6451854ab7e4b4c146bf78a`
- **Upstream tree:** `a8e3481a92772ee311cdc9dd6409cd7b927a3fc1`
- **External theorem:** `EXT-0001`; formal declaration `OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re`
- **Prior audits:** `EXT-0001-lean-overlap-audit.md` (OAI-3); `EXT-0001-route-impact-audit.md` (OAI-4)
- **Mathematical consumers so far:** `C-0060`, `C-0061`, `C-0062` and their `F-20261008-001/002` deductions

## Decision

**Do not vendor, fork, submodule, mirror, or add `openai/math` as a Lake dependency at this time.** Preserve immutable source identifiers and attribution; cite the external theorem as `EXT-0001` and distinguish it from our derived claims. Independent Comparator replay remains optional, and **has not been performed by this repository**. The existing local formal and independent certificate-verification infrastructure remains unchanged.

The mathematical dependency does not require possession or duplication of the full proof source. A code import would need a specifically named local formal theorem consumer and a separate, evidence-backed integration decision. Neither OAI-3 nor OAI-5 identified such a consumer.

## Evidence and legal boundary

At the frozen OpenAI upstream revision, the root `LICENSE` is the **Apache License, Version 2.0** (recorded Git blob `261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64`). The root `NOTICE` is absent in the inspected upstream tree.

**This repository is already dual-licensed, MIT OR Apache-2.0, at the recipient's option.** Its root `README.md` expressly says so, and both `LICENSE-MIT` and `LICENSE-APACHE` are tracked, with PerceivingAI's 2026 copyright statement. The earlier conclusion that it lacked licensing resulted from checking only the conventional filename `LICENSE`; that check was incomplete and is **corrected as of `2026-10-08T03:03:46Z`**. The two existing license files and root README are authoritative for our repository's own licensing.

The authoritative license text is https://www.apache.org/licenses/LICENSE-2.0.html, especially section 4 (redistribution). If upstream source or derivative source is **actually copied and distributed**, then at minimum:
- Provide recipients a copy of Apache-2.0 as applicable to the included licensed work;
- retain pertinent copyright, patent, trademark and attribution notices from the copied source;
- mark modified source files prominently as changed;
- preserve applicable NOTICE attribution content **if any** included work requires it;
- separately inventory and comply with licenses of every copied dependency/file, rather than assuming the whole transitive source tree is uniformly licensed.

Apache-2.0 permits redistribution and modification subject to conditions; it **does not** grant use of OpenAI trademarks as an endorsement. Our MIT OR Apache-2.0 dual license does **not** automatically turn imported OpenAI Apache-2.0-only source into MIT-licensed code: any future copied upstream portions retain their applicable license conditions, even when distributed alongside our dual-licensed original work. No third-party dependencies, manuscript PDFs, preprint sources, or formal modules were copied as part of OAI-6. The source-level license and NOTICE state must be rechecked **per selected revision and copied component** if copying is later proposed. The mere public availability of a dependency does not settle its redistribution terms.

**Reference-only mode:** The existing bibliography `R-0034`, the exact theorem statement/source pin in `EXT-0001`, and our separately derived `C-` claims remain the appropriate academic attribution. They are **not** presented as a reproduction of OpenAI's copyrighted proof files. Link to pinned source rather than a moving default branch when identifying a proof dependency. The external source is not misrepresented as a locally kernel-checked formal theorem.

This document is an engineering/source-reuse decision, not a legal opinion. It respects the existing MIT OR Apache-2.0 dual-license policy in the root README and does not alter it.

## Reuse options considered

| Mode | Current decision | Why |
| --- | --- | --- |
| **A. Cited external theorem and independent mathematical deductions** | **ADOPTED** | Exact frozen pin and authorship; no dependency/compile or license-redistribution burden |
| **B. Reuse existing Mathlib results already present in our formal environment** | **PREFERRED WHEN NEEDED** | Avoid duplication; account for different pinned Mathlib versions before using newer declarations |
| **C. Pinned external Lean/Lake dependency** | **DEFERRED** | No named formal consumer; OpenAI requires Lean 4.34.1 and another Mathlib revision |
| **D. Minimal selected-source vendoring** | **DEFERRED** | A single theorem wrapper imports a broad foundation/detector proof closure; minimum viable import footprint unverified |
| **E. Wholesale source copy, submodule, or fork** | **REJECTED FOR CURRENT NEED** | Large unrelated surface and 42 upstream manifest packages; no identified benefit to current certificate route |
| **F. Copy manuscript/preprint PDFs or proof narrative** | **NOT NEEDED** | Canonical immutable links, citation metadata and original files remain upstream |

**Dependency-size precision:** The 42 packages count is the **entire upstream manifest**, not a proven minimum compilation closure for `EXT-0001`. Avoid treating code availability, mathematical dependency, or a passing upstream claim as locally replayed proof evidence.

## Gates for any future source import (new separate slice)

1. **Consumer gate:** Identify the new mathematical target, exact required declaration(s), and why cited external input or current Mathlib does not suffice.
2. **Scope gate:** Determine the *actual* minimum transitive source/import dependency closure and record immutable commit/blob identities for all source units selected.
3. **Rights gate:** Inspect each included component's provenance/license, source headers, and NOTICE obligations. Preserve this repository's existing MIT OR Apache-2.0 option for its own work; preserve Apache-2.0 obligations for any copied OpenAI components without representing those components as MIT-licensed. Prepare any additional attribution/distribution artifacts **only if copying occurs**.
4. **Toolchain gate:** Independently check Lean/Mathlib API and version compatibility. Do not update the current formally retained certificate environment silently; a distinct formal package/workspace is acceptable if justified.
5. **Verification gate:** Build and kernel-check the named consumer with pinned inputs; document precisely which verification was run. An upstream Comparator replay may be added for independent assurance, but is not a prerequisite for writing external-dependent mathematical consequences.
6. **Trust/admission gate:** Do not rewrite provenance `EXT-` as local authorship, imply automatic transfer of OpenAI proof acceptance into `formal/`, or alter `C-0050..C-0057`, the empty v2 theorem whitelist, Rust/Arb certificate semantics, or RH status.
7. **Privacy gate:** Any retained audit/artifact must contain public hashes, source-relative paths, sanitized tool versions and essential results only. Never record raw terminal output, user/host identifiers, absolute paths, credentials, network identifiers or private environment characteristics.
8. **Review gate:** Require an explicit research/engineering decision approving the *new* import and its scope before any source copy or toolchain migration.

## Result and next boundary

**OAI-6 is a no-code reuse decision.** There is no current reason to ingest OpenAI source. The cited theorem, the three separately derived claims and existing analyses remain usable with their precise attribution and non-replay qualification.

**OAI-7** may codify the external-theorem vs local-formal vs certificate-verification trust boundary in the repository contracts. OAI-9 can perform the eventual documentation/onboarding cutover. OAI-6 makes **no mathematical or certificate admissions** and did **not** execute a formal proof replay or Lean build.
