# Exact-prime Legendre-Schur certificate at T=27/50

- **Computation ID:** `X-20260924-001`
- **Created:** `2026-09-24T18:37:15Z`
- **Last updated:** `2026-09-24T21:34:11Z`
- **Status:** `VERIFIED / RETAINED PROOF`
- **Type:** `RIGOROUS FULL-TAIL ASSEMBLY / EXACT RATIONAL CERTIFICATE / INDEPENDENT VERIFIER`
- **Supports:** `A-20260826-001`, `F-20260924-001`, `C-0057`; historical precursor `X-20260923-001`
- **Admission freeze Git commit:** `f2d284fd85bee8995ef267450e4038768678c3a3`
- **Required generation tree state:** clean and committed; generation must not begin from a dirty working tree

## Objective

Generate a **fresh** proof-bearing exact-prime Legendre-Schur certificate for the newly admitted pair

```text
(T,N)=(27/50,104)
```

from the committed closed-contract state, then submit that exact certificate to the independent zero-float Rust verifier. The historical continuation bundle `X-20260923-001` remains pre-theorem evidence only and must not be copied, renamed, or promoted into this computation.

This declaration does not assert `C-0057`. The claim remains `PROVISIONAL` / `OPEN_REQUIREMENT` until fresh generation, independent verifier PASS, adversarial checks, and later retained-proof registration all succeed.

## Frozen admission state

Phase 3 audited the Phase 2 production diff and found no accidental broadening:

- Python theorem-generator admission adds exactly `(Fraction(27, 50), 104)`;
- the independently maintained Python semantic validator adds exactly the same pair;
- the raw JSON Schema adds `104` to the exact-prime dimension/harmonic guards but binds it through the exact-pair `oneOf` branch to support `27/50`;
- Rust adds exactly `dimension == 104 && support == 27/50` to pair admission and separately permits dimension `104`;
- the test-only corpus contains 8 allowed matched pairs, all 56 off-diagonal combinations, and 9 external forbidden controls;
- `computations/retained-proofs.json` and `EXPECTED_RETAINED_CLAIMS_V1` remain unchanged at `C-0050` through `C-0056`.

The admission implementation is frozen in commit:

```text
f2d284fd85bee8995ef267450e4038768678c3a3
```

Phase 3 quality gates before this declaration:

```text
Focused Python contract suite: 15/15 passed
cargo test -p rh_cert: PASS
cargo clippy -p rh_cert --all-targets -- -D warnings: PASS
cargo fmt -p rh_cert -- --check: PASS
retained-proof manifest-only validation: 7 registered proofs, VALID
git diff --check: PASS
```

## Software/runtime

The declaration environment is:

```text
CPython      3.14.0
python-flint 0.9.0
rustc        1.97.1 (8bab26f4f 2026-07-14)
cargo        1.97.1 (c980f4866 2026-06-30)
```

The Python computation must run through the repository lock with `uv run --locked`. The certificate metadata must record the actual clean Git commit and dirty-state flag used at execution.

## Exact parameters

```text
claim             = C-0057
support T         = 27/50
Legendre N        = 104
Arb precision     = 512 bits
residual order    = 32
matrix endpoints  = 64-bit dyadic outward rounding
witness entries   = 32-bit dyadic rationals
Schur factor      = 3
claim profile     = exact_prime_legendre_schur
tail rule         = legendre_component_gram_schur
parity sector     = both
```

`residual_order=32` and Schur factor `3` are hard-locked by the v1 generator/profile rather than exposed as free CLI parameters.

The pre-theorem candidate in `X-20260923-001` provides only a comparison target. At the same parameterization it reported approximate positive quantities

```text
mu_104       > 0.6643369939721553
even margin  > 0.0002388902594756742
odd margin   > 0.000779387887620489
```

and remained exact-margin stable under fixed-parameter 640-bit reassembly. The fresh theorem run must recompute these quantities from scratch; agreement is expected but not assumed.

## Clean-tree precondition

Immediately before generation:

```text
git status --short
git rev-parse HEAD
```

`git status --short` must print nothing. The HEAD must be a committed descendant of the admission-freeze commit above and include this predeclaration. If the tree is dirty, stop and do not generate theorem artifacts.

## Fresh proof-certificate reproduction command

Run from the repository root:

```text
uv run --locked python -m scripts.cert.exact_prime_schur_certificate \
  --claim C-0057 \
  --support 27/50 \
  --dimension 104 \
  --prec 512 \
  --matrix-bits 64 \
  --witness-bits 32 \
  --output-json computations/2026-09-24T183715Z-t27-50-schur-certificate/data/certificate.json
```

The generator must create a fresh certificate and pass its Python schema/semantic checks. No artifact from `X-20260923-001` may be substituted.

## Independent Rust replay

Only after successful fresh generation:

```text
cargo run -q -p rh_cert -- verify \
  --cert computations/2026-09-24T183715Z-t27-50-schur-certificate/data/certificate.json \
  --json
```

The result is theorem-bearing only if the independent verifier returns exit `0`, `passed=true`, `claim=C-0057`, `support_T=27/50`, `dimension=104`, and `verified_scope=localized_weil_positivity_T_27_50`.

The verifier output should then be retained as `data/rust-verification.json` together with the exact certificate hash/size and execution provenance.

## Planned adversarial checks

After a successful independent PASS, test temporary copies without altering the retained certificate:

1. change exact Schur factor `3 -> 2`; contract validation must reject it;
2. replace a selected finite-matrix diagonal interval by an exact negative value while keeping the contract structurally valid; theorem verification must run and return `passed=false`;
3. confirm the unchanged certificate still returns exit `0` / `passed=true`.

Any unexpected acceptance or failure blocks theorem promotion.

## Retained-proof boundary

This computation is **not** registered in `computations/retained-proofs.json` by this declaration. `EXPECTED_RETAINED_CLAIMS_V1` must also remain unchanged until the fresh certificate, independent replay, and adversarial checks have succeeded and an explicit later registration phase is performed.

## Frozen source hashes at the admission state

```text
57c9f0a4d81fc35837bb37bf3c870ec2c13d2d99f599cd54cc5fce0793b76956  scripts/cert/legendre_schur.py
53cf49ba4a30ddd690a3898a373900e4bda978cc82a27764186eef4e0f398ea7  scripts/cert/exact_prime_schur_certificate.py
e8561a9afaf4dd0fb8815db29f2e0c80b5b3650bd2db8051e2b668da61407f96  scripts/cert/export_certificate.py
bd71fcf341d70a44e1fe8f126393e95b785c4164ea796ce69966f0af4ce10140  crates/rh_cert/src/cert.rs
0a58b6a36055b6b56720d275e96c19d0275948872542491099cd68c454bbed48  docs/contracts/rh-weil-certificate-v1.json
cf1a66ce9ef7321ddadd2df426d9721465110b4f550219db98063415f31f2fba  tests/data/exact-prime-admission-v1.json
5356b959391427a6817ae937d06678554f2761d825ea80fc23890ea9f5d37ac3  computations/retained-proofs.json
4900a4ea4bdb191608d84817af5aae912e5931d5bae82af6159e45c0279d4d89  scripts/cert/verify_retained_proofs.py
```

## Current interpretation

This record freezes the next proof-bearing computation before execution. No theorem computation has yet been run under this ID, no certificate exists yet, and `C-0057` is not verified.

The independently verified finite-support frontier therefore remains `(T,N)=(21/40,96)` / `C-0056`. RH remains unresolved.

## Phase 4 execution result — `2026-09-24T19:47:39Z`

The predeclared fresh generation was executed exactly as written from clean committed HEAD `86f5fd75360892d92cd584bc5f2eab0cae56851b`, whose parent is the admission-freeze commit `f2d284fd85bee8995ef267450e4038768678c3a3`. `git status --short` was empty immediately before the generator started. No artifact from `X-20260923-001` was supplied to the theorem generator.

The generator ran with `T=27/50`, `N=104`, 512-bit Arb precision, residual order `32`, 64-bit outward matrix endpoints, and 32-bit witness entries. It completed with exit `0` after `494.529 s` and emitted `data/certificate.json`. Embedded generator metadata records:

```text
git_commit = 86f5fd75360892d92cd584bc5f2eab0cae56851b
git_dirty  = false
prec_bits  = 512
script     = scripts.cert.exact_prime_schur_certificate
```

The fresh certificate has:

```text
SHA-256 = 75187f3be283ca9596a714c4a12822c4c58cd4b33e7624110ff102d68c9aab3f
bytes   = 9084209
claim   = C-0057
support = 27/50
dimension = 104
profile = exact_prime_legendre_schur
harmonic_index = 104
Schur factor = 3
```

Fresh exact generator diagnostics are strictly positive:

```text
mu_104 = 5555286879239818446537772452241770055413474442715269417182811 / 8362151934403129389124989932521990256254768465142452064354304

even margin = 225795032211778199860554599793086932609334993295756235322614595054656966643661045652277426626799 / 945183084096279532531840801905299481742737949576160080016356461110647801069817649399237409828241408

odd margin = 92083030916052298411705194877268363638350130509372505435337748640783352529515447418897865313969 / 118147885512034941566480100238162435217842243697020010002044557638830975133727206174904676228530176
```

Numerically these are approximately `0.6643369939721553`, `0.0002388902594756742`, and `0.000779387887620489`, respectively. They agree exactly with the previously recorded pre-theorem candidate values, but this Phase 4 certificate was independently reassembled from scratch.

The exact certificate bytes were then replayed through the independent zero-floating-point Rust verifier:

```text
cargo run -q -p rh_cert -- verify \
  --cert computations/2026-09-24T183715Z-t27-50-schur-certificate/data/certificate.json \
  --json
```

The verifier completed with exit `0` after `147.541 s` and returned:

```text
passed=true
claim=C-0057
support_T=27/50
dimension=104
verified_scope=localized_weil_positivity_T_27_50
claim_profile=exact_prime_legendre_schur
tail_rule=legendre_component_gram_schur
```

Rust independently recomputed the positive complement bound, the exact factor-3 Schur reduction, and both exact rational congruence/Gershgorin checks. The even and odd blocks are each `52 x 52`; both witnesses are lower-triangular and invertible; both blocks return `is_positive_definite=true`; and Rust's exact lower bounds match the generator values above. The exact verifier output is retained as `data/rust-verification.json`:

```text
SHA-256 = e29e80bdb4af140db95934732095e45ce761ad82e6eb09b1bf8a5bd5931512ce
bytes   = 2157
```

No generator or verifier process remained after completion. The bundle now follows the proof-run pattern with exactly `record.md`, `data/certificate.json`, and `data/rust-verification.json`.

### Phase 4 boundary

Phase 4's exit gate is satisfied: a fresh clean-provenance certificate receives an independent zero-float Rust `PASS`.

This result is **not yet retained-proof registration or final claim promotion**. The planned real-certificate adversarial checks have not yet been executed in this phase, `computations/retained-proofs.json` and `EXPECTED_RETAINED_CLAIMS_V1` remain unchanged at `C-0050` through `C-0056`, and `C-0057` remains `PROVISIONAL` / `OPEN_REQUIREMENT` pending the later adversarial/registration gates. RH remains unresolved.

## Phase 5 adversarial verification and theorem registration — `2026-09-24T20:22:02Z`

Real-certificate trust-boundary attacks were run only on temporary copies; the retained source certificate was never modified. Contract-invalid cases all returned exit `2`: factor `3 -> 2`, mixed pairs `(21/40,104)` and `(1/2,104)`, a zero interval denominator, missing generator `git_commit`, and a missing matrix coordinate. A contract-valid exact `A(0,0)=-1` perturbation passed parsing, reached theorem verification, and returned exit `1` / `passed=false`; the even parity block failed with a negative exact margin while the odd block remained positive. An untouched certificate copy then returned exit `0` / `passed=true` again. After the attacks, the retained source certificate still hashed to `75187f3be283ca9596a714c4a12822c4c58cd4b33e7624110ff102d68c9aab3f`.

The exact certificate was then registered explicitly in `computations/retained-proofs.json` as `C-0057` / `X-20260924-001`, support `27/50`, dimension `104`, profile `exact_prime_legendre_schur`, and scope `localized_weil_positivity_T_27_50`. `EXPECTED_RETAINED_CLAIMS_V1` was extended through `C-0057`. Focused retained-proof tests pass `67/67`, and manifest-only validation reports `8 registered proofs`.

The complete canonical retained-proof replay then hash-checked and independently re-verified all eight retained certificates:

```text
C-0050 HASH PASS VERIFY PASS T=7/20 N=32
C-0051 HASH PASS VERIFY PASS T=2/5 N=40
C-0052 HASH PASS VERIFY PASS T=17/40 N=48
C-0053 HASH PASS VERIFY PASS T=9/20 N=56
C-0054 HASH PASS VERIFY PASS T=19/40 N=68
C-0055 HASH PASS VERIFY PASS T=1/2 N=80
C-0056 HASH PASS VERIFY PASS T=21/40 N=96
C-0057 HASH PASS VERIFY PASS T=27/50 N=104
RETAINED PROOF CHAIN: PASS - 8/8
```

The full replay exited `0` after `374.333 s`. This establishes `F-20260924-001` / `C-0057`: strict localized Weil positivity at the single finite support `T=27/50`. The independently verified finite-support frontier is now `(T,N)=(27/50,104)`. RH remains unresolved, and entry of the `p=3` compressed translation at `(1/2)log 3` remains a separate structural phase.

## Phase 6 repository-wide closure — `2026-09-24T21:34:11Z`

Repository-wide acceptance was run after the Phase 5 registration state was established. The default Python suite completed with `554 passed` in `714.33 s`. The explicit retained-artifact pytest acceptance completed with `1 passed` in `395.75 s`; that test requires the exact eight-line theorem replay plus final `RETAINED PROOF CHAIN: PASS - 8/8`. The complete `cargo test -p rh_cert` suite passed, including all 24 exact-prime integration/adversarial tests and direct `(27/50,104)` acceptance with nearby forbidden-pair rejection. `cargo fmt -p rh_cert -- --check` passed, and strict `cargo clippy -p rh_cert --all-targets -- -D warnings` passed. The authoritative formal layer `cd formal && lake build` completed successfully with `8711 jobs`.

A repository-wide stale-assumption audit found and corrected three current-facing seven-proof assumptions: the retained acceptance expectation, the agent onboarding retained-proof count, and the root README theorem/retention overview. Remaining `7/7`, seven-pair, or `C-0056`-frontier text occurs only in timestamped historical records describing the state before `C-0057` and is intentionally preserved under the historical-integrity protocol.

This closes the proof-bearing repository acceptance for `C-0057`. The independently verified finite-support frontier advances to `(T,N)=(27/50,104)` because Phases 4 and 5 both passed. RH remains unresolved.
