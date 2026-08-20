# Riemann Conjecture Research Repository

This repository is an organized, auditable research record for attempts to understand or prove the Riemann Hypothesis (RH).

The repository is **not** a collection of informal notes. Every substantive research action, derivation, finding, computation, correction, and dead end must be timestamped and recorded so that later work can reconstruct exactly what was tried, what was learned, and why a direction was continued or abandoned.

## Research standard

The governing rules are:

1. **Timestamp everything substantive.** Use UTC ISO 8601 timestamps (`YYYY-MM-DDTHH:MM:SSZ`) inside documents. Timestamped research artifacts also use a UTC timestamp in the filename.
2. **Never silently rewrite history.** Attempt, finding, and computation records are historical records. Correct them by adding a timestamped correction or by creating a successor record; do not erase the original reasoning.
3. **Separate certainty levels.** Every mathematical statement that matters must be identified as one of: established theorem, derived result, computational observation, conjecture, heuristic, open requirement, or disproved/invalidated claim.
4. **Record dependencies.** A result is only as strong as the claims it depends on. Important claims must be registered in `docs/CLAIMS.md`.
5. **Record failure usefully.** A failed proof attempt is valuable if the exact obstruction, circular dependency, invalid inference, or missing theorem is documented.
6. **Do not call something a proof until the dependency chain is closed.** A reformulation equivalent to RH is not progress toward a proof unless some part of the new formulation is established independently of RH.
7. **Verify external facts.** Literature claims, known theorems, formulas, and equivalences must be tied to a source in `docs/references/BIBLIOGRAPHY.md` or directly cited in the research record.
8. **Keep the current state separate from history.** `docs/STATUS.md` is the maintained snapshot; timestamped files and `docs/LOG.md` preserve the history.

The full documentation protocol is in [`docs/PROTOCOL.md`](docs/PROTOCOL.md).

## How to navigate the documentation

Start here depending on what you need:

| Need | Go to |
| --- | --- |
| Current research state, active leads, blockers | [`docs/STATUS.md`](docs/STATUS.md) |
| Chronological record of all research activity | [`docs/LOG.md`](docs/LOG.md) |
| Registry of important mathematical claims and dependencies | [`docs/CLAIMS.md`](docs/CLAIMS.md) |
| Proof/research attempts | [`docs/attempts/`](docs/attempts/) |
| Atomic findings, lemmas, negative results, observations | [`docs/findings/`](docs/findings/) |
| Numerical/symbolic experiments | [`docs/computations/`](docs/computations/) |
| Research scripts used by computations | [`scripts/`](scripts/) |
| Sources and literature | [`docs/references/BIBLIOGRAPHY.md`](docs/references/BIBLIOGRAPHY.md) |
| Naming, timestamps, status rules, update procedure | [`docs/PROTOCOL.md`](docs/PROTOCOL.md) |
| Templates for new records | [`docs/templates/`](docs/templates/) |

### Recommended reading order for a new research session

1. Read `docs/STATUS.md` to understand the current frontier.
2. Read the newest relevant entries in `docs/LOG.md`.
3. Follow links to the relevant attempt/finding records.
4. Check `docs/CLAIMS.md` before relying on an important intermediate statement.
5. Check the bibliography when a step depends on known literature.
6. If a computation is involved, read its record first and use the exact script/parameters under `scripts/`; never treat numerical output as proof.
7. Create a new timestamped attempt/computation/finding record rather than appending unrelated work to an older artifact.
8. At the end of the session, update `docs/LOG.md`, `docs/STATUS.md`, and any affected claim entries.

## Directory model

```text
.
├── README.md
├── scripts/
│   ├── README.md
│   ├── rh_tools.py
│   ├── verify_identities.py
│   ├── prime_trace.py
│   ├── kernel_scan.py
│   └── prime_range_decomposition.py
└── docs/
    ├── INDEX.md
    ├── PROTOCOL.md
    ├── STATUS.md
    ├── LOG.md
    ├── CLAIMS.md
    ├── attempts/
    │   └── README.md
    ├── findings/
    │   └── README.md
    ├── computations/
    │   └── README.md
    ├── references/
    │   └── BIBLIOGRAPHY.md
    └── templates/
        ├── ATTEMPT.md
        ├── FINDING.md
        └── COMPUTATION.md
```

## Artifact naming

Timestamped artifacts use:

```text
YYYY-MM-DDTHHMMSSZ-<short-kebab-case-title>.md
```

Example:

```text
2026-08-20T203300Z-li-coefficient-growth-route.md
```

The filename timestamp is the artifact's creation time in UTC. All later updates inside that file must carry their own UTC timestamp.

## Research lifecycle

A normal piece of work moves through the repository like this:

```text
question / lead
    ↓
timestamped attempt or computation
    ↓
validated result, obstruction, or negative result
    ↓
timestamped finding (when worth preserving atomically)
    ↓
claim ledger update
    ↓
LOG update
    ↓
STATUS update
```

This structure is deliberately optimized for long-running mathematical work: we should be able to return months later, identify the strongest surviving routes, see exactly why old routes failed, and avoid unknowingly repeating a circular or disproved argument.

## Documentation system initialized

- **Created:** `2026-08-20T20:33:00Z`
- **Purpose:** establish the authoritative research-record system before further RH work is added.
