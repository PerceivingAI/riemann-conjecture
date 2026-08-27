# Riemann Conjecture Research Repository

This repository is an organized, auditable research record for attempts to understand or prove the Riemann Hypothesis (RH).

The repository is **not** a collection of informal notes. Every substantive research action, derivation, finding, computation, correction, and dead end must be timestamped and recorded so that later work can reconstruct exactly what was tried, what was learned, and why a direction was continued or abandoned.

## Agent onboarding

Coding or research agents should read [`AGENTS.md`](AGENTS.md) before exploring the repository broadly. This README explains the project, research standard, trust chain, and human-facing structure; `AGENTS.md` is the complementary operational guide with the current tool map, canonical continuation workflow, test tiers, theorem-admission stop boundary, and change/verification checklist.

Agents should still treat [`docs/STATUS.md`](docs/STATUS.md), [`docs/PROTOCOL.md`](docs/PROTOCOL.md), and [`docs/CONTRACTS.md`](docs/CONTRACTS.md) as authoritative for current research state, record discipline, and proof-certificate semantics respectively.

## Research standard

The governing rules are:

1. **Timestamp everything substantive.** Use UTC ISO 8601 timestamps (`YYYY-MM-DDTHH:MM:SSZ`) inside documents. Timestamped research artifacts also use a UTC timestamp in the filename.
2. **Never silently rewrite history.** Attempt, finding, and computation records are historical records. Correct them by adding a timestamped correction or by creating a successor record; do not erase the original reasoning.
3. **Separate certainty levels.** Every mathematical statement that matters must be identified as one of: established theorem, derived result, computational observation, conjecture, heuristic, open requirement, or disproved/invalidated claim.
4. **Record dependencies.** A result is only as strong as the claims it depends on. Important claims must be registered in `docs/CLAIMS.md`.
5. **Record failure usefully.** A failed proof attempt is valuable if the exact obstruction, circular dependency, invalid inference, or missing theorem is documented.
6. **Do not call something a proof until the dependency chain is closed.** A reformulation equivalent to RH is not progress toward a proof unless some part of the new formulation is established independently of RH.
7. **Verify external facts.** Literature claims, known theorems, formulas, and equivalences must be tied to a source in `references/BIBLIOGRAPHY.md` or directly cited in the research record.
8. **Keep the current state separate from history.** `docs/STATUS.md` is the maintained snapshot; timestamped files and `docs/LOG.md` preserve the history.

The full documentation protocol is in [`docs/PROTOCOL.md`](docs/PROTOCOL.md).

## How to navigate the documentation

Start here depending on what you need:

| Need | Go to |
| --- | --- |
| Agent onboarding, tool map, canonical workflows, verification rules | [`AGENTS.md`](AGENTS.md) |
| Current research state, active leads, blockers | [`docs/STATUS.md`](docs/STATUS.md) |
| Chronological record of all research activity | [`docs/LOG.md`](docs/LOG.md) |
| Registry of important mathematical claims and dependencies | [`docs/CLAIMS.md`](docs/CLAIMS.md) |
| Proof/research attempts | [`attempts/`](attempts/) |
| Atomic findings, lemmas, negative results, observations | [`findings/`](findings/) |
| Numerical/symbolic experiments | [`computations/`](computations/) |
| Research scripts used by computations | [`scripts/`](scripts/) |
| Rigorous certificate contract and PASS semantics | [`docs/CONTRACTS.md`](docs/CONTRACTS.md) |
| Exact Rust certificate verifier | [`crates/rh_cert/`](crates/rh_cert/) |
| Lean formalization of interval/LDL/endpoint/Gershgorin soundness | [`formal/`](formal/) |
| Sources and literature | [`references/BIBLIOGRAPHY.md`](references/BIBLIOGRAPHY.md) |
| Naming, timestamps, status rules, update procedure | [`docs/PROTOCOL.md`](docs/PROTOCOL.md) |
| Templates for new records | [`templates/`](templates/) |

### Recommended reading order for a new research session

1. Read `docs/STATUS.md` to understand the current frontier.
2. Read the newest relevant entries in `docs/LOG.md`.
3. Follow links to the relevant attempt/finding records.
4. Check `docs/CLAIMS.md` before relying on an important intermediate statement.
5. Check the bibliography when a step depends on known literature.
6. If a computation is involved, read its record first and use the exact versioned CLI/parameters recorded there (`scripts/` or `crates/`); never treat numerical output as proof.
7. Create a new timestamped attempt/computation/finding record rather than appending unrelated work to an older artifact.
8. At the end of the session, update `docs/LOG.md`, `docs/STATUS.md`, and any affected claim entries.

## Directory model

```text
.
├── README.md
├── AGENTS.md
├── .gitignore
├── Cargo.toml
├── pyproject.toml
├── requirements.txt
├── requirements.lock
├── uv.lock
├── attempts/
│   └── README.md
├── computations/
│   ├── README.md
│   └── YYYY-MM-DDTHHMMSSZ-<title>/
│       ├── record.md
│       ├── plots/
│       └── data/
├── crates/
│   ├── rh_engine/
│   │   ├── Cargo.toml
│   │   ├── src/
│   │   └── tests/
│   └── rh_cert/
│       ├── Cargo.toml
│       ├── src/
│       └── tests/
├── docs/
│   ├── contracts/
│   │   └── rh-weil-certificate-v1.json
│   ├── CONTRACTS.md
│   ├── INDEX.md
│   ├── PROTOCOL.md
│   ├── STATUS.md
│   ├── LOG.md
│   └── CLAIMS.md
├── formal/
│   ├── Cert/
│   │   ├── Interval.lean
│   │   ├── EndpointAbsorption.lean
│   │   ├── LDL.lean
│   │   └── Gershgorin.lean
│   ├── Cert.lean
│   ├── lakefile.lean
│   └── lean-toolchain
├── findings/
│   └── README.md
├── references/
│   └── BIBLIOGRAPHY.md
├── scripts/
│   ├── README.md
│   ├── rh_tools.py
│   ├── verify_identities.py
│   ├── prime_trace.py
│   ├── kernel_scan.py
│   ├── prime_range_decomposition.py
│   ├── window_diagnostics.py
│   ├── zero_mode_bins.py
│   ├── uniform_phase_diagnostics.py
│   ├── chirp_window_diagnostics.py
│   ├── bilinear_chirp_geometry.py
│   ├── continuation_bundle.py
│   ├── weil_continuation_driver.py
│   ├── cert/
│   │   ├── constants.py
│   │   ├── quadrature.py
│   │   ├── residual_kernel.py
│   │   ├── matrices.py
│   │   ├── legendre_schur.py
│   │   ├── exact_prime_schur_common.py
│   │   ├── exact_prime_schur_certificate.py
│   │   └── export_certificate.py
│   ├── positivity_kernel_diagnostics.py
│   ├── weil_support_geometry.py
│   ├── weil_endpoint_absorption_certificate.py
│   ├── weil_exact_constants.py
│   ├── weil_exact_prime_complement_certificate.py
│   ├── weil_legendre_schur_scout.py
│   ├── weil_support_continuation_scout.py
│   └── weil_support_candidate_check.py
├── templates/
│   ├── ATTEMPT.md
│   ├── FINDING.md
│   └── COMPUTATION.md
└── tests/
    ├── __init__.py
    ├── certificate_conformance.json
    ├── test_cert_pipeline.py
    ├── test_continuation_bundle.py
    ├── test_continuation_driver.py
    ├── test_continuation_integration.py
    ├── test_continuation_state_machine.py
    ├── test_exact_prime_schur_certificate.py
    ├── test_support_continuation.py
    ├── test_identities.py
    ├── test_properties.py
    ├── test_pre_theorem_boundary.py
    └── test_rh_tools.py
```

## Python research environment

The supported project baseline is **Python 3.12+**; the currently verified local environment is CPython 3.14.0. Scientific and testing dependencies are declared in `pyproject.toml` and resolved in `uv.lock`. `requirements.lock` preserves the currently verified `.venv` package snapshot.

Preferred setup:

```text
uv sync --locked --extra test
```

The `--locked` flag requires the environment to match `uv.lock`; `--extra test`
installs the test dependencies without requiring shell activation. The `.venv/`
directory is intentionally gitignored. Historical computation records remain
authoritative about the exact environment used for each retained run.

## Testing & Verification

Property-based and exact algebraic tests are executed with the locked `uv`
environment:

```text
uv run --locked --extra test python -m pytest
```

Tests cover:
- Laguerre polynomial contiguous relations $L_n^{(\alpha)} = L_n^{(\alpha+1)} - L_{n-1}^{(\alpha+1)}$ across randomized $(n, \alpha)$ pairs.
- Exact rational Laplace pole/density integrals $1 - q^n$ for randomized rational $s_0 > 1$ and degrees $n$.
- Exact shift filter $T = (E-1)(E-q)$ annihilation of the pole mode $1 - q^n$.
- Sieve and von Mangoldt $\Lambda(m)$ generator properties.
- Rigorous Arb/Acb certificate generation, exact-input quadrature guards, Suzuki residual-kernel checks, and shared Python/Rust certificate conformance cases.
- Hypothesis property tests for exact Laguerre, pole-density, shift-filter, small-`u` diagnostic identities, and the uniform pre-turning stationary/Cayley phase map.

The certificate verifier and formal layer have separate acceptance checks:

```text
cargo test -p rh_cert
cargo clippy -p rh_cert --all-targets -- -D warnings
cd formal && lake build
```

The exact retained theorem artifacts have a separate first-class acceptance gate:

```text
uv run --locked python -m scripts.cert.verify_retained_proofs
```

This command does **not** regenerate certificates. It checks the closed manifest in `computations/retained-proofs.json`, requires every registered certificate SHA-256 to match its raw bytes, and replays each intact artifact through the current `rh_cert` verifier with exact claim/support/dimension/profile/scope agreement. The real five-certificate pytest wrapper is marked `retained_proofs` and excluded from routine pytest runs; invoke it explicitly with `uv run --locked --extra test python -m pytest -q -m retained_proofs tests/test_retained_proofs_acceptance.py`.

## Rigorous certificate trust chain

Proof-oriented finite-dimensional calculations use a deliberately separated trust chain:

```text
Python + python-flint/Arb
    -> exact rational interval certificate
    -> crates/rh_cert zero-float Rust verifier
    -> Lean proof of interval/LDL/endpoint/Gershgorin-congruence soundness
```

The closed certificate syntax and exact PASS semantics are authoritative in [`docs/CONTRACTS.md`](docs/CONTRACTS.md) and [`docs/contracts/rh-weil-certificate-v1.json`](docs/contracts/rh-weil-certificate-v1.json). The v1 `exact_prime_legendre_schur` profile is a closed whitelist, currently admitting exactly `(T,N)=(7/20,32)`, `(2/5,40)`, `(17/40,48)`, `(9/20,56)`, and `(19/40,68)`. For each admitted pair it derives the Legendre complement bound, reconstructs the factor-3 component-Gram Schur matrix, and verifies exact rational congruence/Gershgorin witnesses. Fresh independently replayed certificates establish `C-0050` through `C-0054` as localized finite-support theorems; the profile does not accept arbitrary nearby supports.

Whitelist consistency is checked separately without centralizing production authority. `tests/data/exact-prime-admission-v1.json` is a test-only corpus of allowed and forbidden `(T,N)` cases; Python generator/semantic/schema tests and Rust independently execute those expectations against their own hard-coded admission logic. Production verifier/generator code does not load the corpus.

Retention adds an additional audit layer without changing those theorem semantics: `computations/retained-proofs.json` explicitly names the five proof-bearing certificate files and their expected hashes/theorem identities, while `scripts.cert.verify_retained_proofs` verifies that those exact stored artifacts remain intact and are still accepted by the current independent verifier.

Support-continuation tooling may parameterize the shared exact assembler and may produce generator-side exact candidates at other rational one-prime supports. Those candidates do **not** inherit theorem status from `C-0050`. The canonical continuation driver stops at `CANDIDATE_READY`; a separate human/research decision must admit the exact support/dimension pair to the closed theorem contract before certificate generation and a fresh independent Rust replay can establish theorem status.

The Lean project in `formal/` now deliberately uses **Mathlib**, pinned to `v4.33.0` in `formal/lakefile.lean` and resolved by `formal/lake-manifest.json`. This is a larger formal dependency than the original lightweight-Core-only idea, but it supports the current general finite-dimensional LDL theorem, analytic endpoint-absorption proof, and exact-prime Gershgorin/invertible-congruence soundness theorem. `lake build` is the authoritative formal acceptance check.

## Native Calculation Engine (`crates/rh_engine`)

For large cutoffs ($X \ge 10^7, 10^8$) where Python becomes a bottleneck, the multi-threaded Rayon engine provides high-throughput segmented sieving and batch Laguerre recurrences:

```text
# Prime-Laguerre trace calculation across cutoffs
cargo run --release -- prime-trace --s0 3 --n-max 16 --cutoffs 1000000,10000000 --output-json computations/.../data/trace.json

# Range decomposition in turning-scale u=t/(4n) bins
cargo run --release -- range-bins --s0 3 --n 8,12,16 --max-m 5000000

# Throughput benchmark across cores
cargo run --release -- benchmark --cutoffs 1000000,10000000,50000000
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
