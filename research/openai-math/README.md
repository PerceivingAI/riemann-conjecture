# OpenAI Math — Research, provenance, and documentation acceptance

- **Created:** `2026-10-08T03:41:56Z` (UTC)
- **Last updated:** `2026-10-08T03:44:13Z`
- **Scope:** OAI-9 documentation cutover and ongoing source map; **not** a proof or independent Comparator replay
- **Current decision:** OAI-8 is complete; localized Weil primary, phase-aware secondary, proposed hybrid deferred

## Agent reading map

| Question | Maintained source |
| --- | --- |
| What exactly did OpenAI prove, who owns it, and which source was checked? | [`EXT-0001`](../../references/external-results/EXT-0001-openai-quasi-rh.md), [`R-0034`](../../references/BIBLIOGRAPHY.md) |
| Was OpenAI's Lean proof independently rerun by this project? | **No.** See the maintained OAI-9 verification snapshot in `EXT-0001` and the [external-results optional replay checklist](../../references/external-results/README.md) |
| What mathematical consequences were *derived here*? | [`C-0060..C-0062`](../../docs/CLAIMS.md), [`F-20261008-001`](../../findings/2026-10-08T014258Z-openai-quasi-rh-cayley-consequence.md), [`F-20261008-002`](../../findings/2026-10-08T024431Z-openai-seven-eighths-prime-distribution.md) |
| What does local verification mean? | [`docs/CONTRACTS.md` §5](../../docs/CONTRACTS.md), [`docs/PROTOCOL.md` §7.2](../../docs/PROTOCOL.md) |
| Did OpenAI source get copied into the repo? | **No**; [OAI-6 reference-only reuse policy](../../references/external-results/EXT-0001-reuse-and-license-decision.md) |
| Which route should new mathematics pursue? | [`RESEARCH_DIRECTION.md`](RESEARCH_DIRECTION.md), OAI-8.1–8.5 |
| What is actually verified on the Weil branch? | [`docs/STATUS.md`](../../docs/STATUS.md), [closed retained-proof registry](../../computations/retained-proofs.json), [multi-prime negative diagnostic](../../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md) |
| What is the historical context? | [OAI-4 route audit](../../references/external-results/EXT-0001-route-impact-audit.md); timestamped addenda to the [pole-subtracted Laguerre attempt](../../attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md), [microlocal chirp attempt](../../attempts/2026-08-20T224400Z-prime-side-chirp-dirichlet-reduction.md), [first Legendre–Schur certificate](../../attempts/2026-08-21T085252Z-exact-prime-legendre-schur-certificate.md) and [one-prime continuation](../../attempts/2026-08-26T171400Z-one-prime-support-continuation.md) |

## OAI-9.1–9.5 acceptance checklist

- **9.1 Reference integration:** Source/theorem/Comparator JSON and Lean/Mathlib pins agree with pinned upstream checkout; `R-0034` identifies `EXT-0001` and its status. Challenge-template `sorry` is not confused with the actual OpenAI solution. **Independent local replay: NOT PERFORMED, optional**.
- **9.2 Claims and contracts:** Exactly the existing `C-0060`, `C-0061`, `C-0062` written derivations are documented with direct or transitive dependency on `EXT-0001`. `docs/CONTRACTS.md` §5 records the trust graph, no source copying, no local Lean assertion and no theorem promotion. Python/JSON/Rust contracts were **not modified**.
- **9.3 Historical meaning:** Dated October addenda to four existing attempts preserve August proof stages, original dead ends and the original `P9` performance observation. Later rigorous v2 sufficient-matrix negatives are identified as later findings, not silently read into the historical run.
- **9.4 Agent onboarding:** `AGENTS.md` → pinned `EXT-0001` + optional replay checklist → `C-0060..C-0062` → trust contract → OAI-8 decision. Root `README.md` and `scripts/README.md` distinguish external replay from the **8/8 local retained-certificate** verification CLI.
- **9.5 Consistency:** `docs/STATUS.md`, `docs/LOG.md`, `docs/INDEX.md` and this map expose the current state. Historical statements stay dated; no old OAI-1 instructions are treated as present replay PASS. Verify all local links, unique claim IDs, absence of code/claim-admission changes, and private-data hygiene before reporting OAI-9 complete.

## OAI-9 acceptance actually executed — `2026-10-08T03:44:13Z`

- **9.1:** Pinned OpenAI checkout HEAD, Git tree, source theorem blob, Comparator JSON blob, upstream license blob and 4.34.1/Mathlib identities were checked. **Theorem replay was not executed.**
- **9.2:** `C-0060`, `C-0061`, and `C-0062` each have exactly **one** claim heading. The frozen v1 / v2 focused regression target returned **15/15 PASS**. The retained-proof **manifest-only** command returned **8 registered proofs VALID**, not a fresh 8/8 independent certificate replay.
- **9.3:** Automated historical-text comparisons confirm original text is retained in **4/4** updated attempt files, apart from their `Last updated` metadata and explicitly dated addenda.
- **9.4:** The `AGENTS.md` onboarding path resolves through the external result, exact trust status, derived claims, and the OAI-8 decision. No CLI is represented as a local `EXT-0001` proof replay.
- **9.5:** **314** local Markdown references across **18** relevant documentation files resolved; a source-level check found no missing links. The scope scan found **18 changed Markdown files and no code/schema/admission edits**. A targeted privacy-pattern scan of new/changed lines and new files passed. `git diff --check` passed with no whitespace errors (line-ending conversion warnings are environment notices only).

**Non-performed work:** no independent Comparator replay, Lean kernel compilation of upstream source, full retained-proof Rust replay, full Python suite, or new expensive Arb qualification. These tests assert documentary consistency and existing contract enforcement only.

**Mathematical boundary:** OpenAI's `Re(s)>7/8` theorem is not RH; its separately derived `7/8` prime-distribution bounds do not establish RH-strength cancellation. The eight v1 finite-support proofs remain independently retained. In the first generic multi-prime window, strict negatives concern the **specific sufficient factor-3 Schur matrices**, *not* the full Weil form. No generic v2 theorem has been admitted.

**OAI-9 verification evidence:** The session's focused source-integrity, cross-reference, duplicate-claim, history-preservation, private-data and `git diff --check` checks should be consulted in the acceptance report. This document does not claim fresh Lean, Comparator, Rust or retained-certificate replay merely from documentation checks.
