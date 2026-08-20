# Research Documentation Protocol

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T22:10:00Z`
- **Status:** Authoritative

This document defines how all Riemann Hypothesis research in this repository must be recorded.

## 1. Timestamp standard

UTC is the authoritative repository time standard.

Use ISO 8601:

```text
YYYY-MM-DDTHH:MM:SSZ
```

Example:

```text
2026-08-20T20:33:00Z
```

Timestamped artifact filenames omit the punctuation in the time component:

```text
attempts/YYYY-MM-DDTHHMMSSZ-short-title.md
findings/YYYY-MM-DDTHHMMSSZ-short-title.md
computations/YYYY-MM-DDTHHMMSSZ-short-title/record.md
```

Every new attempt, finding, or computation must have:

- a creation timestamp in its filename;
- `Created` in the document header;
- `Last updated` in the document header;
- timestamps on any later correction, status transition, or material addendum.

## 2. Historical integrity

Files under `attempts/`, `findings/`, and `computations/` are historical research records.

Do not silently replace an incorrect derivation with a corrected one. Instead:

1. preserve the original text;
2. add a clearly timestamped correction/addendum; or
3. create a successor record and mark the earlier record as superseded or invalidated.

`STATUS.md`, `INDEX.md`, `CLAIMS.md`, `LOG.md`, and the bibliography are maintained documents and may be updated normally, but every material update must change their `Last updated` timestamp. `LOG.md` itself is append-only.

## 3. Record types

### Attempt

Use when exploring a possible route toward RH or an intermediate theorem.

Required content:

- question/goal;
- motivation;
- prerequisites and known results used;
- exact mathematical setup;
- derivation or argument, step by step;
- checks performed;
- result;
- obstruction or unresolved step;
- circularity check;
- new claims/findings produced;
- next action.

### Finding

Use for a reusable atomic result, including:

- proved lemma within our work;
- consequence of established literature;
- useful reformulation;
- obstruction;
- counterexample;
- negative result;
- computationally observed pattern worth tracking.

A finding must state exactly what kind of evidence supports it.

### Computation

Use for numerical, symbolic, or programmatic experiments.

Each computation run is stored as a self-contained **directory bundle**:

```text
computations/YYYY-MM-DDTHHMMSSZ-<short-title>/
├── record.md          # Primary computation record
├── plots/             # (Optional) Generated static visual artifacts (.svg, .png)
└── data/              # (Optional) Summary datasets or parameter tables (.json, .csv)
```

Required content in `record.md`:

- objective;
- code/script and revision when applicable;
- software/runtime;
- parameters and precision;
- inputs;
- outputs;
- interpretation;
- limitations;
- whether the result is evidence only or proves something.

Visual & Data Artifact Rules:
- **Static figures:** Generated figures must be saved directly into `plots/` within the computation bundle. Prefer `.svg` for line plots, phase functions, and asymptotic curves; use fixed-DPI `.png` (`dpi=200`) for dense 2D rasters.
- **Reproducible CLI execution:** Computations must run from a deterministic, versioned CLI entry point: either a script under `scripts/` or a native tool under `crates/`, with explicit CLI arguments. Interactive notebooks are prohibited.
- **Data size threshold:** Keep small summary outputs ($\le 2\text{ MB}$) in `data/`. Large raw datasets must be regenerable on demand via CLI arguments documented in `record.md`.

A numerical experiment must never be described as proving RH.

## 4. Certainty/status vocabulary

Use the following labels consistently.

### Claim type

- `ESTABLISHED_THEOREM` — accepted theorem from the literature, with source.
- `DERIVED_RESULT` — proved within this repository from stated dependencies.
- `COMPUTATIONAL_OBSERVATION` — supported numerically/symbolically only.
- `CONJECTURE` — proposed statement without proof.
- `HEURISTIC` — plausibility argument, not a proof.
- `OPEN_REQUIREMENT` — statement that would need to be proved for a route to work.
- `INVALIDATED` — previously considered statement shown false or argument shown invalid.

### Attempt status

- `ACTIVE` — currently being pursued.
- `PROMISING` — survives current checks and has a concrete next step.
- `BLOCKED` — needs a specific missing theorem, calculation, source, or tool result.
- `DEAD_END` — route does not work for a documented reason.
- `INVALID` — contains a decisive error or circular argument.
- `SUPERSEDED` — replaced by a later record.
- `COMPLETE` — attempt achieved its stated intermediate goal; this does not imply RH is proved.

### Finding status

- `PROVISIONAL` — not yet independently checked.
- `VERIFIED` — derivation/source has been checked sufficiently for current use.
- `REFUTED` — finding is false.
- `SUPERSEDED` — replaced by a stronger or corrected finding.

## 5. Claim IDs

Important mathematical statements receive stable IDs in `CLAIMS.md`:

```text
C-0001
C-0002
...
```

Claim entries record:

- statement;
- type;
- status;
- first recorded timestamp;
- dependencies;
- source or repository artifact;
- verification notes.

Attempt and finding documents should reference claim IDs rather than relying on memory.

## 6. Attempt and finding IDs

Use stable IDs inside documents:

```text
A-YYYYMMDD-NNN
F-YYYYMMDD-NNN
X-YYYYMMDD-NNN
```

where:

- `A` = attempt;
- `F` = finding;
- `X` = computation/experiment;
- `NNN` is the day's sequence starting at `001`.

The timestamped filename remains the globally unique filesystem identifier.

## 7. Literature and source discipline

Every external theorem, equivalence, formula, historical assertion, or quoted result that materially supports an argument must be traceable.

Prefer, in order:

1. original paper or authoritative monograph;
2. peer-reviewed secondary source;
3. authoritative institutional source;
4. reputable preprint when the result is not yet published;
5. tertiary source only for orientation, not as sole support for a delicate mathematical claim.

Bibliography entries should record:

- stable identifier (DOI, arXiv ID, ISBN, or canonical URL);
- authors/title;
- publication information when available;
- first verified/accessed timestamp;
- exact reason the source matters here.

### 7.1 External mathematical dataset provenance

When external numerical or certified datasets are used (such as verified zeta-zero tables, prime tables, or Dirichlet coefficients):

1. **Exploratory evaluation:** For standard ranges (e.g., first $10^2$–$10^3$ zeros), dynamic on-the-fly calculation via verified libraries (`mpmath.zetazero()`) is preferred over committing static data files.
2. **Dataset registration:** Any imported static dataset must be registered in `references/BIBLIOGRAPHY.md` with its canonical source, publication/retrieval timestamp, and SHA-256 cryptographic checksum.
3. **Repository size threshold:**
   - Small tables ($\le 2\text{ MB}$) may reside under `references/data/`.
   - Large tables ($> 2\text{ MB}$) must remain gitignored and be generated or downloaded on demand via a deterministic versioned CLI under `scripts/` or `crates/`, with SHA-256 verification when external data is retrieved.
## 8. Circularity test

Every serious attempt must explicitly answer:

> Does any required estimate, lemma, zero-free assertion, cancellation bound, positivity claim, or asymptotic already imply RH or an equivalent statement?

If yes, the route is not a proof unless that requirement is independently established.

Equivalent reformulations are useful, but must be labeled as such.

## 9. Proof-claim gate

No repository document may state that RH has been proved merely because:

- many zeros were numerically checked;
- an equivalent criterion was restated;
- a necessary condition was verified;
- a formal manipulation produced a positive-looking expression;
- an asymptotic was assumed outside its proven domain;
- an interchange of sum/limit/integral was used without justification;
- a divergent or conditionally convergent expression was rearranged without a valid theorem;
- a numerical computation matched the conjecture.

Before any `RH PROVED` status could be entered, the repository would need at minimum:

1. a complete written proof;
2. all dependency claims closed;
3. no `OPEN_REQUIREMENT` on the proof path;
4. all convergence/analytic-continuation/interchange steps justified;
5. independent line-by-line verification;
6. comparison against the known literature to rule out a rediscovered invalid route.

## 10. Session workflow

At the start of research:

1. read `STATUS.md`;
2. inspect recent `LOG.md` entries;
3. inspect relevant attempts/findings;
4. inspect related claims;
5. verify literature prerequisites when needed.

During research:

1. create or continue the appropriate timestamped record;
2. timestamp material corrections/addenda;
3. register important new claims;
4. keep computations reproducible.

At the end of research:

1. record the result/status in the attempt/computation;
2. create findings for reusable results or obstructions;
3. update `CLAIMS.md`;
4. append a timestamped entry to `LOG.md`;
5. update `STATUS.md` if the research frontier changed;
6. update `INDEX.md` if a new major document category or landmark artifact was added.

## 11. Navigation rule

Historical detail belongs in timestamped artifacts. Current truth belongs in `STATUS.md` and `CLAIMS.md`. Chronology belongs in `LOG.md`.

That separation is mandatory: it prevents current conclusions from destroying the record of how they were reached.
