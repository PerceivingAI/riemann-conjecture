# Riemann Conjecture Research Repository

This repository is an organized, auditable research record for attempts to understand or prove the Riemann Hypothesis (RH).

The repository is **not** a collection of informal notes. Every substantive research action, derivation, finding, computation, correction, and dead end must be timestamped and recorded so that later work can reconstruct exactly what was tried, what was learned, and why a direction was continued or abandoned.

## Agent onboarding

Coding or research agents should read [`AGENTS.md`](AGENTS.md) before exploring the repository broadly. This README explains the project, research standard, trust chain, and human-facing structure; `AGENTS.md` is the complementary operational guide with the current tool map, canonical continuation workflow, test tiers, theorem-admission stop boundary, and change/verification checklist.

Agents should still treat [`docs/STATUS.md`](docs/STATUS.md), [`docs/PROTOCOL.md`](docs/PROTOCOL.md), and [`docs/CONTRACTS.md`](docs/CONTRACTS.md) as authoritative for current research state, record discipline, and proof-certificate semantics respectively.

## Current research direction and external mathematics (OAI-9)

**RH remains unresolved.** The independent retained certificate chain establishes exactly eight finite-support localized Weil positivity theorems `C-0050..C-0057`. Generic multi-prime tooling exists but has **no** admitted v2 theorem. At frozen `T=11/20,N=192/196`, the existing factor-3 **sufficient** Schur matrices have independently audited negative directions; this does *not* imply negativity of the full Weil operator.

The [OAI-8 research-direction decision](research/openai-math/RESEARCH_DIRECTION.md) keeps exact Weil/Legendre–Schur as the **primary** research program, with the next work being a justified new multi-prime positivity criterion rather than repeating the old failed sufficient matrix. Laguerre/phase-aware prime arithmetic is **secondary**; a Weil/phase hybrid is **deferred** until an exact, noncircular bridge is proved.

This repository uses OpenAI's formal zero-free result `Re(s)>7/8` as an **external, pinned, attributed mathematical input** [`EXT-0001`](references/external-results/EXT-0001-openai-quasi-rh.md) / bibliography `R-0034`. Source identities have been checked; **independent local Comparator replay has not been performed** and is optional for cited mathematical use. The new `C-0060..C-0062` are this project's written mathematical deductions (including `psi(x)-x=O(x^(7/8)log²x)`), **not** locally compiled Lean theorems or newly admitted Weil certificates. See the [external-results guide](references/external-results/README.md) and [trust contract](docs/CONTRACTS.md) §5. No OpenAI code was copied; future imports follow the [OAI-6 reuse decision](references/external-results/EXT-0001-reuse-and-license-decision.md). Our existing code remains dual-licensed **MIT OR Apache-2.0**.

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
| Pinned external OpenAI theorem, exact trust/replay status | [`EXT-0001`](references/external-results/EXT-0001-openai-quasi-rh.md) and [external-results guide](references/external-results/README.md) |
| Current Weil vs phase-aware vs hybrid decision | [`OAI-8 research direction`](research/openai-math/RESEARCH_DIRECTION.md) |
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

Routine pytest uses `pytest-xdist` with the repository default `-n 2`. This was chosen empirically on the current 6-core Windows research machine: the 486-test default suite improved from about 559 seconds sequentially to about 378 seconds with two workers, while four workers only improved to about 372 seconds. Use `-n 0` for sequential debugging; do not assume `-n auto` is better for the Arb/NumPy-heavy tail.

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

Canonical one-prime research continuation also uses bounded process parallelism: the CLI runs up to three independent floating-scout resolutions concurrently and up to two independent primary/fallback rigorous screens concurrently, while each precision ladder, exact candidate construction, and candidate cross-precision confirmation remain sequential. Use `--scout-workers 1 --rigorous-workers 1` for exact sequential reproduction. The multiprocessing path has a separate `parallel_acceptance` pytest tier and should be run with outer pytest `-n 0` to avoid nested test-worker parallelism.

The exact retained theorem artifacts have a separate first-class acceptance gate:

```text
uv run --locked python -m scripts.cert.verify_retained_proofs
```

This command does **not** regenerate certificates. It checks the closed manifest in `computations/retained-proofs.json`, requires every registered certificate SHA-256 to match its raw bytes, and replays each intact artifact through the current `rh_cert` verifier with exact claim/support/dimension/profile/scope agreement. The real seven-certificate pytest wrapper is marked `retained_proofs` and excluded from routine pytest runs; invoke it explicitly with `uv run --locked --extra test python -m pytest -q -m retained_proofs tests/test_retained_proofs_acceptance.py`.

## Rigorous certificate trust chain

Proof-oriented finite-dimensional calculations use a deliberately separated trust chain:

```text
Python + python-flint/Arb
    -> exact rational interval certificate
    -> crates/rh_cert zero-float Rust verifier
    -> Lean proof of interval/LDL/endpoint/Gershgorin-congruence soundness
```

The closed certificate syntax and exact PASS semantics are authoritative in [`docs/CONTRACTS.md`](docs/CONTRACTS.md), with the frozen theorem-bearing v1 syntax in [`docs/contracts/rh-weil-certificate-v1.json`](docs/contracts/rh-weil-certificate-v1.json) and the separate currently non-admitted v2 syntax in [`docs/contracts/rh-weil-certificate-v2.json`](docs/contracts/rh-weil-certificate-v2.json). The v1 `exact_prime_legendre_schur` profile is a closed whitelist, currently admitting exactly `(T,N)=(7/20,32)`, `(2/5,40)`, `(17/40,48)`, `(9/20,56)`, `(19/40,68)`, `(1/2,80)`, `(21/40,96)`, and `(27/50,104)`. For each admitted pair it derives the Legendre complement bound, reconstructs the factor-3 component-Gram Schur matrix, and verifies exact rational congruence/Gershgorin witnesses. Fresh independently replayed certificates establish `C-0050` through `C-0057` as localized finite-support theorems; the profile does not accept arbitrary nearby support/dimension pairs such as `(21/40,100)` or `(27/50,100)`.

Whitelist consistency is checked separately without centralizing production authority. `tests/data/exact-prime-admission-v1.json` is a test-only corpus of allowed and forbidden `(T,N)` cases; Python generator/semantic/schema tests and Rust independently execute those expectations against their own hard-coded admission logic. Production verifier/generator code does not load the corpus.

Retention adds an additional audit layer without changing those theorem semantics: `computations/retained-proofs.json` explicitly names the eight proof-bearing certificate files and their expected hashes/theorem identities, while `scripts.cert.verify_retained_proofs` verifies that those exact stored artifacts remain intact and are still accepted by the current independent verifier. The current closed retained chain is `C-0050` through `C-0057` and replays `8/8`.

As of `2026-10-01T09:46:49Z`, this one-prime v1 path is frozen as the historical theorem path while separate multi-prime tooling is developed. Future structural-window work must not silently change the meaning of `rh-weil-certificate-v1`, the eight-pair `exact_prime_legendre_schur` whitelist, or the existing Rust v1 replay. `tests/test_one_prime_v1_freeze.py` provides the fast semantic regression guard; the retained-proof replay remains the authoritative artifact-integrity guard.

The separate multi-prime mathematical contract is frozen in [`docs/MULTI_PRIME_CONTRACT.md`](docs/MULTI_PRIME_CONTRACT.md). In the immediate `(log 3)/2<T<(log 4)/2` window the active arithmetic set is exactly `{2,3}`. The combined signed arithmetic operator `P=P_2+P_3` remains one Schur component, so `C-0059` proves that the three-component `V,P,R` reduction retains factor `3`; its arithmetic tail Gram must be computed from the combined operator square and includes the mixed `P_2/P_3` terms. This is mathematical infrastructure only, not a new theorem admission or certificate profile.

The generic arithmetic implementation now lives separately in `scripts/cert/prime_power_terms.py`. It derives active prime powers and all arithmetic constants rigorously with Arb, fails closed on unresolved strict thresholds, and implements compressed translations by piecewise polynomial action over every translation breakpoint. Active terms are combined before integration, so the generated operator-square matrix includes cross-prime products automatically. The same code has been exercised after the `m=4` threshold with `tau_2<1`; no operator redesign is tied to the `{2,3}` window. This P2 core remains pre-certificate infrastructure and does not modify the closed v1 theorem path.

The corresponding full rigorous assembler is `scripts/cert/multi_prime_legendre_schur.py`. Its `assemble_multi_prime_schur()` combines the existing rigorous archimedean/residual components with the generic arithmetic operator and produces `A`, `GV`, `GP`, `GR`, `rho_R`, `mu`, and the grouped factor-3 Schur matrix. Before the new `{2,3}` window was exercised, four one-prime overlap cases reproduced the frozen implementation for `P`, operator `P^2`, `GP/G2`, `A`, `mu`, and Schur enclosures. A separate direct test then proves the `{2,3}` combined `P^2` has a rigorously nonzero cross term and therefore is not merely `P_2^2+P_3^2`. This remains tooling infrastructure, not a new theorem or certificate profile.

P4 adds separate multi-prime scout and exact-candidate stages. `scripts/weil_multi_prime_schur_scout.py` is floating reconnaissance only and builds the combined active-prime operator numerically. `scripts/weil_multi_prime_support_candidate_check.py` is generator-side rigorous: it outward-rounds `A/GV/GP/GR`, reconstructs the exact factor-3 Schur bound with per-prime-power complement contributions, and computes exact parity witness margins. Neither stage changes theorem admission or verifier semantics.

P5 adds `scripts/weil_multi_prime_continuation_driver.py` as the separate canonical continuation implementation for new structural windows. Its first supported window is strictly `log(3)/2 < T < log(4)/2`, with an independently verified active set exactly `{2,3}`. It carries forward the proven scout/rigorous/fallback/exact-candidate/stability workflow and the existing process, cache, atomic-write, observability, deterministic-ordering, and fail-closed safeguards. The historical `weil_continuation_driver.py` remains unchanged and canonical only for the one-prime path.

P6 introduces `docs/contracts/rh-weil-certificate-v2.json` instead of extending v1. The v2 profile `multi_prime_power_legendre_schur` serializes active prime powers through a canonical `arithmetic_terms` array and uses the combined arithmetic Gram `GP`; it does not add `c3/G3` beside `c2/G2`. The tail rule fixes the grouped `V,P,R` factor to `3/1` under verified claim `C-0059`. Structural validation is available in `scripts/cert/certificate_v2_contract.py`, but the production v2 theorem whitelist is empty, so no v2 pair is currently admitted.

P7 adds a separate independent Rust v2 verifier in `crates/rh_cert/src/v2.rs` and format dispatcher in `crates/rh_cert/src/dispatch.rs`; the frozen v1 `cert.rs` implementation remains unchanged. V2 requires canonical sorted unique arithmetic terms and exactly `{2,3}` in its first structural window, independently derives exact-rational prime-loss intervals and `mu_N`, reconstructs `A-(3/mu_N)(GV+GP+GR)`, enforces exact parity structure, and recomputes exact congruence/Gershgorin witness margins. Its production theorem whitelist remains empty, so no v2 theorem is admitted. As with v1, the zero-float Rust layer verifies exact rational interval proof arithmetic; it does not independently prove the correctness of the upstream transcendental Arb enclosures.

P8 adds the pre-continuation adversarial gate. The v2 schema structurally fixes the first window to canonical terms `[2,3]` with exact unit compressed-shift norm bounds; Python semantics and Rust independently prove the strict serialized window and reject threshold overlap, malformed arithmetic intervals, missing/malformed `GP`, wrong parity, wrong factor, and active-set substitution. A shared 10-case structural corpus is replayed independently by JSON Schema, Python semantics, and Rust, while a separate 16-case closed admission grid is independently rejected by schema admission metadata, Python, and Rust. The v2 production whitelist remains empty.

P9 attempted the first non-theorem end-to-end qualification at `T=11/20`. The floating stack worked and found stable-positive behavior beginning at `N=192` with fallback `N=196`, but the generic rigorous assembler did not finish either first 128-bit assembly within a one-hour execution window despite both workers remaining CPU-active. No rigorous cache entry, exact candidate, or reproducibility bundle exists. P9 is therefore **NOT QUALIFIED — rigorous-stage performance blocker**, not a mathematical negative; the v2 theorem whitelist remains empty. A separate performance-hardening slice is required before another qualification.

Support-continuation tooling may produce generator-side exact candidates, but those candidates do **not** inherit theorem status from earlier results. Both continuation drivers stop at `CANDIDATE_READY`: `weil_continuation_driver.py` is the historical one-prime path, while `weil_multi_prime_continuation_driver.py` is the canonical implementation for future structural windows. A separate human/research decision must admit an exact support/dimension pair to a closed theorem contract before certificate generation and a fresh independent Rust replay can establish theorem status.

Before emitting `CANDIDATE_READY`, the current driver now performs candidate-level precision stability: with `T`, `N`, residual order, matrix rounding bits, and witness bits fixed, it reassembles at higher Arb precision and checks exact margins together with raw and rounded enclosure contraction. This is specifically meant to distinguish monomial-basis/working-precision instability from a stable mathematical sign. It remains pre-theorem diagnostics and does not weaken the independent admission/verifier boundary.

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

## License

This repository is dual-licensed under either:

- [MIT License](LICENSE-MIT) (`MIT`)
- [Apache License, Version 2.0](LICENSE-APACHE) (`Apache-2.0`)

at your option.
