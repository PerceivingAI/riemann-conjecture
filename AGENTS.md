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
```

These support the independently verified finite-support results `C-0050` through `C-0054`. The pre-theorem driver isolated `(T,N)=(19/40,68)` after showing `N=64` precision-stable negative under the current Schur reduction; the pair was then separately admitted and independently verified in proof-bearing `X-20260827-002`. The immediate engineering frontier is to optimize the zero-float exact Rust verifier before pushing `N` substantially farther, while preserving exact semantics and replaying the retained theorem/adversarial corpus after any optimization. The eventual mathematical structural transition remains entry of the `p=3` compressed translation at `(1/2)log 3`.

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
    -> CANDIDATE_READY or a fail-closed terminal state
```

It also writes the self-contained continuation bundle and prints a concise terminal summary. Use `--json` only when the full result object is needed on stdout.

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

Key locations:

| Component | Location |
| --- | --- |
| Shared rigorous Legendre-Schur assembly | `scripts/cert/legendre_schur.py` |
| Neutral exact rational construction helpers | `scripts/cert/exact_prime_schur_common.py` |
| Closed theorem certificate exporter | `scripts/cert/exact_prime_schur_certificate.py` |
| Other certificate export support | `scripts/cert/export_certificate.py` |
| Contract/schema | `docs/CONTRACTS.md`, `docs/contracts/rh-weil-certificate-v1.json` |
| Independent verifier | `crates/rh_cert/` |
| Formal soundness | `formal/` |

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

Important: the default pytest configuration **includes integration tests** and excludes only the `slow_acceptance` marker. A full default run therefore takes minutes, not seconds.

### Slow/manual acceptance

The expensive `T=9/20,N=56` 512-bit certificate regression is intentionally excluded from normal pytest runs:

```text
uv run --locked --extra test python -m pytest -q \
  -m slow_acceptance \
  tests/test_exact_prime_schur_certificate.py
```

Do not casually add expensive high-dimensional certificate generation to the fast unit layer.

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
