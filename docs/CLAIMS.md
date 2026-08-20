# Claim Ledger

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T20:33:00Z`

This ledger tracks mathematical statements important enough to be reused across attempts.

## Rules

- Claim IDs are stable and never recycled.
- Changing a claim's status requires a timestamped verification note.
- Literature claims must cite the bibliography/source.
- Repository-derived claims must link to the attempt/finding that derives them.
- Dependencies must identify other claim IDs when applicable.
- An equivalent reformulation of RH must be identified as such; it is not an independent proof step.

## Claims

No claims registered yet.

## Entry format

```markdown
### C-0001 — Short name

- **Statement:** ...
- **Type:** ESTABLISHED_THEOREM | DERIVED_RESULT | COMPUTATIONAL_OBSERVATION | CONJECTURE | HEURISTIC | OPEN_REQUIREMENT | INVALIDATED
- **Status:** PROVISIONAL | VERIFIED | REFUTED | SUPERSEDED
- **First recorded:** YYYY-MM-DDTHH:MM:SSZ
- **Last verified:** YYYY-MM-DDTHH:MM:SSZ
- **Dependencies:** C-.... / none
- **Source:** bibliography entry and/or repository artifact
- **Verification notes:** ...
```
