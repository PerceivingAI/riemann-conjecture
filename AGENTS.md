# Agent Onboarding and Repository Operating Guide

This file is the operational entry point for coding and research agents working in this repository.

`README.md` and `AGENTS.md` are intentionally complementary:

- [`README.md`](README.md) explains the purpose of the repository, the research standard, the documentation model, the trust chain, and the broad project structure.
- `AGENTS.md` explains how an agent should enter the repository, where the active machinery lives, which tools are canonical, what to verify after changes, and where the hard research/proof boundaries are.

Do not try to rediscover the repository from source files alone. Start with this file, then follow the maintained documents below.

## 1. First five minutes

Before changing anything:

1. Run `git status --short` and preserve any pre-existing work. Do not overwrite, revert, stage, or commit unrelated changes.
2. Read [`docs/STATUS.md`](docs/STATUS.md). It is the authoritative maintained snapshot of the current research frontier.
3. Read the newest relevant entries in [`docs/LOG.md`](docs/LOG.md).
4. Read the active/relevant attempt in [`attempts/`](attempts/) before modifying research logic.
5. Read [`docs/CLAIMS.md`](docs/CLAIMS.md) before relying on an important mathematical statement.
6. Read [`docs/CONTRACTS.md`](docs/CONTRACTS.md) before touching proof certificates, theorem admission, or verifier semantics.
7. Read [`scripts/README.md`](scripts/README.md) before running or modifying research scripts.
8. If creating or modifying a historical research record, read [`docs/PROTOCOL.md`](docs/PROTOCOL.md) first.

Do not commit automatically. Leave changes available for review unless the task explicitly asks for a commit.

## 2. Current research orientation

RH is **UNRESOLVED** in this repository. Never describe a numerical result, candidate, finite-support theorem, or equivalent criterion as a proof of RH.

The current main route is the exact-prime localized Weil / Legendre-Schur continuation route. The maintained frontier and strongest results are in `docs/STATUS.md`; do not treat this summary as a replacement for that file.

The closed `exact_prime_legendre_schur` theorem contract currently admits exactly:

```text
(T,N)=(7/20,32)
(T,N)=(2/5,40)
(T,N)=(17/40,48)
(T,N)=(9/20,56)
(T,N)=(19/40,68)
(T,N)=(1/2,80)
(T,N)=(21/40,96)
```

These support the independently verified finite-support results `C-0050` through `C-0056`. At `T=21/40`, the floating scout first appeared positive at `N=88`, but rigorous full-tail screening rejected `N=88` and `N=92`; the canonical driver then selected `N=96`, whose exact candidate remained stable from 512 to 640 bits. A separate explicit admission added only `(21/40,96)`, while `(21/40,100)` remains forbidden, and fresh proof-bearing `X-20260828-001` independently established `C-0056`. The retained theorem gate now passes `7/7`. Exact-verifier optimization remains recorded separately in `X-20260827-003`. The current research frontier is therefore **above `T=21/40` but still strictly below `(1/2)log 3`**. The next planned canonical pre-theorem slice is `T=27/50=0.54`; let the driver choose the dimension rather than extrapolating `N=96`. Entry of the `p=3` compressed translation at `(1/2)log 3` remains a separate structural phase.

## 3. Repository map

Use this map before searching broadly.

| Location | Purpose |
| --- | --- |
| `README.md` | Human-facing project overview, research standard, trust chain, environment, broad structure |
| `AGENTS.md` | Agent onboarding, operational map, canonical workflows, verification and stop rules |
| `docs/STATUS.md` | Current research frontier, strongest verified results, blockers, next action |
| `docs/LOG.md` | Append-only chronological research history |
| `docs/CLAIMS.md` | Stable mathematical claim IDs, status, dependencies, evidence |
| `docs/CONTRACTS.md` | Authoritative certificate/verifier contract and PASS semantics |
| `docs/contracts/` | Machine-readable certificate schema/contract data |
| `docs/PROTOCOL.md` | Authoritative record/timestamp/status/history rules |
| `docs/INDEX.md` | Compact navigation index for attempts/findings/computations |
| `attempts/` | Timestamped coherent research routes; historical records |
| `findings/` | Timestamped atomic lemmas, obstructions, corrections, observations |
| `computations/` | Retained reproducible historical computation bundles |
| `computations/retained-proofs.json` | Closed registry of exact proof-bearing certificate artifacts and expected theorem identities |
| `scripts/` | Python research tooling and canonical continuation machinery |
| `scripts/cert/` | Rigorous Legendre-Schur assembly and certificate construction machinery |
| `crates/rh_cert/` | Independent zero-float exact rational Rust certificate verifier |
| `crates/rh_engine/` | Native high-throughput calculation engine for large prime/Laguerre workloads |
| `formal/` | Lean/Mathlib soundness layer for interval, LDL, endpoint, Gershgorin/congruence arguments |
| `tests/` | Python unit, property, integration, certificate, and boundary regressions |
| `references/` | Literature/source registry |
| `templates/` | Templates for new attempts, findings, and computation records |

## 4. Canonical continuation workflow

For **ordinary one-prime continuation**, use:

```text
scripts/weil_continuation_driver.py
```

Run it as a module from the repository root:

```text
uv run --locked python -m scripts.weil_continuation_driver \
  --support 19/40 \
  --n-min 48 \
  --n-max 80 \
  --n-step 4 \
  --output-dir computations/.../data/continuation-T019-040
```

Do not run the file path directly with `python scripts/weil_continuation_driver.py`; package imports are designed for `python -m scripts.weil_continuation_driver`.

The driver owns the pre-theorem chain:

```text
exact support/input validation
    -> multi-resolution floating scout
    -> convergence/sign classification
    -> smallest stable-positive dimension selection
    -> rigorous Arb full-tail precision search
    -> precision/conditioning diagnostics
    -> exact outward rational rounding
    -> exact rational witness check
    -> fixed-parameter candidate cross-precision confirmation
    -> CANDIDATE_READY or a fail-closed terminal state
```

It also writes the self-contained continuation bundle and prints a concise terminal summary. Use `--json` only when the full result object is needed on stdout.

### Continuation concurrency policy

The canonical CLI uses bounded **process** parallelism where stages are mathematically independent:

```text
floating scout resolutions: up to 3 worker processes
primary/fallback rigorous screens: up to 2 worker processes
```

The driver uses spawn-based workers and collects results back in deterministic resolution/dimension order. Numerical-library thread counts default to one per worker (`OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`, `NUMEXPR_NUM_THREADS`) unless the environment explicitly overrides them, avoiding process × BLAS oversubscription.

Do **not** parallelize the internal precision ladder, exact candidate construction, or candidate cross-precision confirmation. Those stages are intentionally sequential because later decisions depend on earlier precision results.

For exact sequential reproduction/debugging, force:

```text
--scout-workers 1 --rigorous-workers 1
```

`run_driver()` remains sequential by default for programmatic callers/tests; the CLI supplies the bounded `3/2` defaults. Parallel and sequential historical replays have been checked for semantic identity after removing execution-only metadata (`scout_workers`, `rigorous_workers`, `cache_hit`).

### Continuation terminal states

Important terminal states include:

```text
NO_CANDIDATE
SCOUT_UNSTABLE
RIGOROUS_ASSEMBLY_FAILED
PRECISION_LIMIT_REACHED
ROUNDING_FAILED
WITNESS_FAILED
CANDIDATE_CHECK_FAILED
CANDIDATE_READY
```

Precision diagnostics distinguish:

```text
INSUFFICIENT_PRECISION
PRECISION_STABLE
MATHEMATICAL_NEGATIVE
ASSEMBLY_FAILED
```

A conditioning-sensitive or unresolved negative numerical result must escalate precision. It must **not** become `NO_CANDIDATE` unless the mathematical negative is stable across improving rigorous precision.

After the first exact-positive candidate, the driver also holds matrix/witness resolution fixed and reassembles at higher Arb precision. It normally checks `p+128` and stops there when exact margins and enclosure widths are stable; `p+256` is used only when the first comparison remains unsettled. A contradiction at this stage is not a theorem failure or `NO_CANDIDATE`; it is a precision/conditioning limit and must not be promoted.

## 5. Standalone continuation tools: diagnostics/components, not the ordinary chain

These remain useful and supported, but do not manually chain them for ordinary continuation:

| Tool | Use directly when |
| --- | --- |
| `scripts/weil_legendre_schur_scout.py` | Isolated floating dimension reconnaissance, debugging, historical reproduction |
| `scripts/weil_support_continuation_scout.py` | Isolated rigorous full-tail Arb diagnostics at selected support/dimension/precision |
| `scripts/weil_support_candidate_check.py` | Isolated generator-side exact candidate construction/debugging |
| `scripts/continuation_bundle.py` | Bundle implementation/support code; normally called by the driver |

Read `scripts/README.md` for exact arguments and interpretation rules.

## 6. Proof/certificate tool boundaries

The proof-oriented trust chain is deliberately separated:

```text
Python + python-flint/Arb
    -> exact rational interval certificate
    -> crates/rh_cert independent zero-float Rust verifier
    -> Lean soundness layer
```

After theorem-bearing artifacts are retained, a separate operational audit layer binds their exact bytes and identities through `computations/retained-proofs.json` and `scripts.cert.verify_retained_proofs`. That retention gate checks continued integrity/replay; it is not a fourth theorem-derivation step and does not promote new claims.

Key locations:

| Component | Location |
| --- | --- |
| Shared rigorous Legendre-Schur assembly | `scripts/cert/legendre_schur.py` |
| Neutral exact rational construction helpers | `scripts/cert/exact_prime_schur_common.py` |
| Closed theorem certificate exporter | `scripts/cert/exact_prime_schur_certificate.py` |
| Other certificate export support | `scripts/cert/export_certificate.py` |
| Contract/schema | `docs/CONTRACTS.md`, `docs/contracts/rh-weil-certificate-v1.json` |
| Test-only admission drift corpus | `tests/data/exact-prime-admission-v1.json` |
| Independent verifier | `crates/rh_cert/` |
| Retained proof integrity/replay gate | `scripts/cert/verify_retained_proofs.py`, `computations/retained-proofs.json` |
| Formal soundness | `formal/` |

The admission corpus is **test-only**. Production generator, semantic-validator, schema, and Rust admission rules remain independently maintained; do not refactor them to load the corpus or another shared runtime whitelist. When a theorem pair is deliberately admitted, update each independent layer and then extend the corpus so the consistency tests can detect drift.

Focused admission consistency checks:

```text
uv run --locked --extra test python -m pytest -q tests/test_admission_consistency.py
cargo test -p rh_cert --test test_exact_prime_schur exact_prime_admission_matches_shared_test_corpus
```

The continuation driver and `weil_support_candidate_check.py` are **pre-theorem** modules. They must not import/call theorem-admission machinery or grant theorem status.

## 7. Hard stop: no automatic theorem promotion

`CANDIDATE_READY` means generator-side evidence only.

The required lifecycle is:

```text
canonical continuation driver
    -> CANDIDATE_READY
    -> STOP

separate human/research decision
    -> explicitly admit exact (T,N) pair to closed theorem contract
    -> generate proof certificate under the admitted contract
    -> fresh independent Rust replay
    -> theorem status only if the closed verifier passes
```

A continuation run must **not automatically**:

- edit the Rust whitelist;
- edit the Python whitelist;
- edit the JSON Schema;
- modify `docs/CLAIMS.md` or `docs/CONTRACTS.md` to manufacture theorem status;
- create a new `C-xxxx` merely because a candidate is positive;
- generate a finding that claims theorem status before admission/replay;
- invoke an unapproved pair through a weakened verifier mode;
- label `CANDIDATE_READY` as `VERIFIED`.

Tests in `tests/test_pre_theorem_boundary.py` and `tests/test_continuation_driver.py` enforce important parts of this boundary.

## 8. Python environment and test tiers

The supported Python baseline is 3.12+ and the environment is locked by `uv.lock`.

Setup:

```text
uv sync --locked --extra test
```

### Fast continuation/unit checks

Use these while iterating on driver orchestration or presentation logic:

```text
uv run --locked --extra test python -m pytest -q \
  -m "not integration" \
  tests/test_continuation_driver.py \
  tests/test_continuation_state_machine.py \
  tests/test_continuation_bundle.py \
  tests/test_pre_theorem_boundary.py
```

### Real continuation integration tests

These execute real Arb assembly and exact candidate construction and are materially slower:

```text
uv run --locked --extra test python -m pytest -q \
  -m integration \
  tests/test_continuation_integration.py
```

They cover known history including `T=2/5,N=40`, `T=17/40,N=48`, and the low-precision conditioning incident.

### Default Python suite

```text
uv run --locked --extra test python -m pytest -q
```

Important: the default pytest configuration runs with `pytest-xdist -n 2`, **includes integration tests**, and excludes the `slow_acceptance`, `retained_proofs`, and `parallel_acceptance` markers. On the current 6-core Windows research machine, the full 486-test default suite improved from about 559 seconds sequentially to about 378 seconds with two workers; four workers gave only a marginal further improvement (~372 seconds), so `-n 2` is the maintained default rather than `-n auto`. Use `-n 0` when debugging tests sequentially or when a test itself owns process parallelism.

### Slow/manual acceptance

The expensive `T=9/20,N=56` 512-bit certificate regression is intentionally excluded from normal pytest runs:

```text
uv run --locked --extra test python -m pytest -q \
  -m slow_acceptance \
  tests/test_exact_prime_schur_certificate.py
```

Do not casually add expensive high-dimensional certificate generation to the fast unit layer.

### Retained theorem-artifact acceptance

The seven proof-bearing retained certificates have their own real-artifact acceptance tier. It is excluded from the default pytest expression under the `retained_proofs` marker:

```text
uv run --locked --extra test python -m pytest -q \
  -m retained_proofs \
  tests/test_retained_proofs_acceptance.py
```

The canonical direct command is:

```text
uv run --locked python -m scripts.cert.verify_retained_proofs
```

This gate does **not** regenerate certificates. It validates `computations/retained-proofs.json`, checks raw-byte SHA-256 integrity, and replays each intact certificate through the current zero-float Rust verifier. Run it after changes to `rh_cert`, retained proof artifacts, the retained-proof manifest/tool, or proof-contract semantics before claiming the retained theorem trust chain is green. Fast fixture/adversarial logic remains in `tests/test_retained_proofs.py` and stays in the ordinary suite.

### Parallel-continuation acceptance

The driver multiprocessing path has its own expensive real-history tier, excluded from routine pytest:

```text
uv run --locked --extra test python -m pytest -n 0 -q \
  -m parallel_acceptance \
  tests/test_continuation_parallel_acceptance.py
```

Keep outer pytest sequential (`-n 0`) for this tier because the driver itself launches worker processes. The acceptance cases cover real `T=2/5`, `T=17/40`, and `T=19/40` histories and currently pass `3/3`. Do not rerun this tier casually after unrelated changes; use it when changing process orchestration, worker/cache behavior, or continuation semantics.

Completed continuation manifests record `process_lifecycle` for the Python driver's own managed process pools. Normal runs require `worker_model="spawn"`, `worker_cleanup_verified=true`, and `active_children_after_cleanup=0`; that zero is scoped to workers observed by the driver and must not be interpreted as an OS-wide process-tree guarantee.

## 9. Rust and Lean verification

Rust workspace crates are declared in the root `Cargo.toml`.

For certificate-verifier changes:

```text
cargo test -p rh_cert
cargo clippy -p rh_cert --all-targets -- -D warnings
```

For native calculation-engine changes, use the relevant `rh_engine` tests/builds in addition to any affected Python checks.

Lean is under `formal/` and uses Mathlib pinned by `formal/lakefile.lean` / `formal/lake-manifest.json`.

Authoritative formal acceptance:

```text
cd formal
lake build
```

Run the affected trust layer's checks. Do not claim the full trust chain is green if only Python tests ran.

## 10. Historical-record discipline

`attempts/`, `findings/`, and retained `computations/` are historical records.

Do not silently rewrite old reasoning to make it look as though the current understanding existed earlier. When correcting history:

- preserve the original context;
- add a timestamped correction/addendum; or
- create a successor record and mark the older route appropriately.

Maintained documents such as `docs/STATUS.md`, `docs/INDEX.md`, `docs/CLAIMS.md`, and `scripts/README.md` may be updated to current truth. Follow the timestamp/update rules in `docs/PROTOCOL.md`.

Historical computation commands are provenance. Do not rewrite them merely because a newer canonical tool now exists.

## 11. Creating new research artifacts

Use the repository templates:

```text
templates/ATTEMPT.md
templates/FINDING.md
templates/COMPUTATION.md
```

Use UTC timestamps and stable IDs according to `docs/PROTOCOL.md`.

A normal research lifecycle is:

```text
question/lead
    -> timestamped attempt or computation
    -> validated result / obstruction / negative result
    -> timestamped finding when worth preserving atomically
    -> claim-ledger update when appropriate
    -> LOG update
    -> STATUS update
```

For canonical continuation-driver runs, retain the driver's manifest-based continuation bundle. For historical/manual computation work, follow the computation bundle standard in `computations/README.md` and `docs/PROTOCOL.md`.

## 12. Source and mathematical discipline

Before relying on an external theorem, formula, equivalence, dataset, or literature claim, verify it against the source discipline in `docs/PROTOCOL.md` and record it in `references/BIBLIOGRAPHY.md` when material.

Always ask the circularity question:

> Does this missing estimate, positivity assertion, zero-free statement, cancellation bound, or asymptotic already imply RH or an equivalent statement?

Equivalent reformulations are useful but are not a proof mechanism by themselves.

Numerical evidence is never theorem evidence unless it is part of the repository's explicitly defined rigorous certificate trust chain and passes the required independent boundary.

## 13. Change workflow for agents

For code/tooling work:

1. Inspect `git status --short`.
2. Read the relevant source and nearby tests before editing.
3. Prefer the existing canonical component rather than duplicating logic.
4. Make the smallest coherent change.
5. Add a focused regression test for behavioral changes.
6. Run fast affected tests first.
7. Run real integration/full trust-layer checks when the change warrants them.
8. Run `git diff --check`.
9. Review `git diff --name-only` / `git diff` for scope creep.
10. Update maintained documentation when the canonical workflow, status, or tool contract changed.
11. Do not commit unless explicitly requested.

For mathematical/research work, additionally follow the documentation lifecycle in `docs/PROTOCOL.md`.

## 14. Common mistakes to avoid

- Starting from old computation commands instead of the current maintained workflow.
- Treating a standalone diagnostic script as the canonical continuation orchestration.
- Extrapolating the next Legendre dimension from the historical `32 -> 40 -> 48 -> 56` sequence.
- Treating low-precision monomial-conditioning artifacts as mathematical negatives.
- Treating `CANDIDATE_READY` as theorem status.
- Editing whitelist/schema/claims/contracts as an automatic side effect of continuation.
- Saying RH is proved because a localized finite-support theorem is verified.
- Rewriting historical attempts/computations to match current understanding.
- Running only Python tests after changing the Rust verifier or Lean soundness layer.
- Adding expensive real-certificate work to routine unit tests when a fake-stage orchestration test is sufficient.
- Overwriting unrelated working-tree changes.

## 15. Where to look when unsure

Use this order:

1. `AGENTS.md` — operational question.
2. `docs/STATUS.md` — what is currently true / active.
3. `scripts/README.md` — which research tool to run and how.
4. `docs/CONTRACTS.md` — proof-certificate/verifier semantics.
5. `docs/PROTOCOL.md` — record/timestamp/history policy.
6. relevant active attempt/finding/computation — why a decision was made.
7. tests — executable behavior and regression expectations.
8. source code — implementation detail.

If documents disagree, do not silently choose the convenient version. Determine whether one is historical and one maintained, verify the implementation/tests, and align the maintained documentation as part of the work.
