# Research Log

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-27T17:26:10Z`
- **Policy:** Append-only

This is the chronological master log. Add newest entries at the top, immediately below this introduction. Existing entries must not be silently altered.

## 2026-08-27T17:26:10Z — T=1/2,N=80 admitted and independently verified

**Type:** Finite-support theorem / explicit closed-contract admission / retained proof

The historical pre-theorem `T=1/2` continuation mapped `N=56,60,...,104`, with `N=76` ultimately classified as a precision-stable mathematical negative under the current full-tail Schur reduction and fallback `N=80` stabilized positive at 512-bit Arb precision. The fixed 64-bit-matrix / 32-bit-witness exact candidate remained unchanged under 640-bit reassembly while the underlying Arb widths contracted.

A separate admission decision extended the closed `exact_prime_legendre_schur` profile by exactly `(T,N)=(1/2,80)`. The cross-layer consistency gate caught two stale independent dimension guards—JSON Schema enums and Rust's internal exact-prime dimension guard—before theorem generation; both were extended to `80`, while the expanded test-only corpus continues to reject all off-diagonal admitted-grid combinations and explicitly rejects `(1/2,76)`.

Fresh proof-bearing `X-20260827-004` generated `C-0055` from scratch at 512-bit Arb precision with 64-bit outward matrix endpoints and 32-bit exact witnesses. Certificate SHA-256 is `95dd6c7a497ad605ddc81129a774bade5fbbc769d0f6fdf29172b89da2a57a7d`. The independent zero-float Rust verifier returns `passed=true`, scope `localized_weil_positivity_T_1_2`, and exact lower bounds corresponding approximately to `mu_80>0.6983326376765460`, even margin `>0.0006030229450313612`, and odd margin `>0.002927388923852846`. Rust replay SHA-256 is `7383c91f48ead83ac9268fcdb154f9372c45ac3510339b9eaac3bd6fd461322a`.

Real-certificate adversarial replay gives contract failure `exit 2` for `factor=2` and theorem failure `exit 1` for a contract-valid negative diagonal perturbation. Full `rh_cert` tests and strict Clippy pass. `C-0055` / `X-20260827-004` is now registered in the explicit retained-proof manifest, and the canonical retained-proof gate passes `6/6`. This establishes `F-20260827-002` / `C-0055`: strict localized Weil positivity at the single finite support `T=1/2`. It does not prove RH or imply positivity at larger supports; the `p=3` entry at `(1/2)log 3` remains a separate structural transition.

---

## 2026-08-27T16:55:13Z — Bounded process parallelism adopted; T=1/2 becomes the pre-theorem frontier

**Type:** Research-tool performance / deterministic multiprocessing / continuation frontier

The canonical one-prime driver is now `continuation-driver-p15-v1` with cache contract `continuation-driver-v6`. The CLI parallelizes only mathematically independent work: up to three floating-scout resolutions and up to two primary/fallback rigorous screens run in spawn-based worker processes, with deterministic result ordering. Each rigorous precision ladder, exact candidate construction, and fixed-parameter candidate cross-precision confirmation remain sequential. Worker processes default `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`, and `NUMEXPR_NUM_THREADS` to one unless explicitly overridden; cache writes now use process-unique temporary paths followed by atomic replacement. Programmatic `run_driver()` remains sequential by default, and `--scout-workers 1 --rigorous-workers 1` provides exact sequential reproduction.

`pytest-xdist` was added to the existing `test` extra and routine pytest now defaults to `-n 2`. On the current six-core Windows research machine, the full 486-test default suite improved from about `559 s` sequentially to `378.10 s` with two workers; four workers completed in `372.27 s`, too small an incremental gain to justify `-n auto`. The driver multiprocessing path has a separate `parallel_acceptance` tier that must be run with outer pytest `-n 0`; the real `T=2/5`, `17/40`, and `19/40` histories pass `3/3`. A real parallel and forced-sequential `T=2/5` replay is semantically identical after removing execution-only worker/cache-hit metadata.

Immediately before this optimization, the canonical p14 driver completed the fresh `T=1/2` continuation over `N=56,60,...,104` in `1619.029 s`. Floating reconnaissance found `N=56..68` negative, `N=72` unstable, and `N=76..104` stable-positive. Rigorous screening selected fallback `N=80`; it stabilized positive at 512 bits, then the exact 64-bit-matrix / 32-bit-witness candidate remained stable at 640 bits. The terminal result is `CANDIDATE_READY`, retained under `computations/2026-08-27T151517Z-t1-2-continuation/`. This is pre-theorem evidence only: `(1/2,80)` was not added to the closed whitelist, no theorem claim changed, and RH remains unresolved.

---

## 2026-08-27T15:01:21Z — Candidate-level precision stability added to canonical continuation

**Type:** Pre-theorem tooling / conditioning diagnostics / fail-closed precision classification

Upgraded `scripts.weil_continuation_driver` to `continuation-driver-p14-v1` (`continuation-driver-v5` cache semantics). The existing rigorous precision ladder now records richer cross-precision diagnostics: `mu`/finite-block/Schur movement, residual/component changes, interval-width contraction, and the location/radius/midpoint of the widest Arb matrix entries. The generator-side exact candidate checker also retains raw Arb conditioning diagnostics and exact outward-rounded matrix-width diagnostics.

After the first exact-positive candidate, the driver now freezes support, dimension, residual order, matrix bits, and witness bits and reassembles the same candidate at higher working precision. It checks `p+128` first and stops early when exact `mu_N`/even/odd margins are stable and positive while raw enclosures contract and rounded exact intervals do not widen; otherwise it attempts `p+256`. Persistent contradiction or unresolved movement is fail-closed as `PRECISION_LIMIT_REACHED`, explicitly without mathematical rejection or theorem promotion. Each continuation bundle gets a dedicated `candidate/precision-stability-Nxxx.json` artifact.

Fast continuation/state/bundle/support tests pass `57/57`; selected certificate/pre-theorem regressions pass `56/56` with two deliberately slow tests deselected. A real `T=7/20,N=32` candidate replay at 160 then 288 bits classified `CANDIDATE_STABLE`: the widest `A` Arb interval contracted from about `2.16e-14`, exact rounding remained non-expanding, and exact even/odd margin relative changes were about `2.8e-14` and `8.9e-13`. The dedicated real continuation integration tier also passes `3/3` in `301.43 s`, including the documented `N=40` low-precision conditioning incident and the historical `T=17/40,N=48` candidate path under the new confirmation gate. This is tooling/conditioning evidence only; no theorem claim changed and RH remains unresolved.

---

## 2026-08-27T14:37:56Z — Cross-layer admission consistency corpus added without weakening verifier independence

**Type:** Trust-chain consistency / closed-whitelist drift detection / test tooling

Added the test-only corpus `tests/data/exact-prime-admission-v1.json`. It records exactly five allowed exact-prime theorem pairs, all twenty mismatched combinations of those admitted supports and dimensions, and five external forbidden cases including the historically relevant `(19/40,64)` and `(19/40,72)` points. Python tests independently check the generator whitelist, semantic-validator whitelist, and raw JSON Schema branch; Rust independently consumes the same test corpus through its own exact-prime certificate validation path. The authoritative contract documentation is also checked to name every admitted pair.

The production implementations remain independent and hard-coded. Neither `scripts/cert/` nor `crates/rh_cert/src/` loads the test corpus, and a regression enforces that boundary. The corpus is an acceptance-policy oracle for tests only: changing it cannot grant theorem status and supplies no mathematical evidence.

Focused acceptance passes: six Python admission-consistency tests and the Rust 30-case corpus replay both pass. No theorem claim or whitelist entry changed; RH remains unresolved.

---

## 2026-08-27T14:30:20Z — Retained-proof bootstrap and final trust-chain acceptance close P8/P9

**Type:** Trust-chain bootstrap audit / full acceptance / live tamper rejection

Independently recomputed SHA-256 over the raw bytes of all five retained theorem certificates directly from disk. The resulting hashes exactly match `computations/retained-proofs.json` and the historical computation records; `C-0052` through `C-0054` also repeat the same certificate hashes in `docs/CLAIMS.md`. `C-0050` and `C-0051` retain their hash provenance in their computation/finding records rather than duplicating it in claim prose. No discrepancy was found and no theorem claim changed.

Final acceptance passes: `66/66` fast retained-proof tests; full `cargo test -p rh_cert`; strict `cargo clippy -p rh_cert --all-targets -- -D warnings`; `58/58` selected certificate/pre-theorem Python tests with the two explicitly slow acceptance tests deselected; and `lake build` with `8711` jobs. The canonical retained-proof command then returned `RETAINED PROOF CHAIN: PASS - 5/5` with exit `0`.

A live fail-closed check used a temporary modified copy of the retained `C-0050` certificate while preserving its registered original hash in a temporary five-entry manifest. The canonical gate reported `C-0050 HASH_MISMATCH VERIFY SKIPPED`, independently replayed and passed `C-0051` through `C-0054`, and exited `1` with `RETAINED PROOF CHAIN: FAIL - 4/5`. Both temporary files were deleted afterward and all five originals were rehashed successfully.

The v1 retained-proof registry remains an explicit whitelist. It does not scan `computations/` for certificates and does not duplicate derived Gershgorin margins or similar verifier diagnostics; the certificate hash fixes the proof bytes and `rh_cert` re-derives the theorem result.

**Outcome:** P0–P9 of the retained-certificate integrity/replay slice are complete. The trust-chain addition changes no mathematical claim; RH remains unresolved.

---

## 2026-08-27T14:17:45Z — Retained theorem artifacts gain a first-class integrity/replay gate

**Type:** Trust-chain tooling / retained-proof integrity / explicit acceptance tier

Added the closed `computations/retained-proofs.json` registry for exactly the five proof-bearing theorem certificates `C-0050` through `C-0054`, together with `scripts.cert.verify_retained_proofs`. The gate validates the manifest contract, resolves only safe repository-contained regular files, hashes exact raw certificate bytes, refuses to replay hash-invalid artifacts, invokes the current zero-float Rust verifier on intact artifacts, and requires exact claim/support/dimension/profile/scope agreement. Operational failures are classified as `MISSING`, `HASH_MISMATCH`, `VERIFIER_ERROR`, `THEOREM_FAILURE`, or `SEMANTIC_MISMATCH`; the command continues through the full manifest and exits `0` only for a complete pass.

Fast fixture/adversarial coverage lives in `tests/test_retained_proofs.py`. A separate `retained_proofs` pytest marker now owns the real five-certificate acceptance test and is excluded from ordinary pytest runs so the approximately 80-second replay does not inflate routine unit/integration work. The canonical direct command remains `uv run --locked python -m scripts.cert.verify_retained_proofs`; it **does not regenerate certificates**.

The real retained chain passes `5/5`. This adds an ongoing artifact-integrity/replay assertion and does not alter the closed theorem whitelist, certificate semantics, or any mathematical claim. RH remains unresolved.

---

## 2026-08-27T13:42:54Z — Zero-float Rust verifier optimization removes immediate scaling bottleneck

**Type:** Tooling performance / exact semantic equivalence / retained-certificate replay

Optimized `crates/rh_cert` without changing `rh-weil-certificate-v1`, the closed exact-prime whitelist, proof semantics, arithmetic types, or CLI exit meanings. The verifier still validates the full input matrices for exact symmetry and parity zeros, but now constructs even/odd Schur blocks directly; exact interval scaling by rational witnesses avoids generic point-interval multiplication; congruence uses lower-triangular witness support; and symmetric theorem blocks compute one output triangle using `A C^T=(C A)^T`.

The public generic congruence helper remains valid for non-symmetric matrices and has a dedicated regression. The optimized debug replay profile is

```text
N=32   3.564 s   (prior ~11 s)
N=40   6.145 s   (prior ~25 s)
N=48  13.210 s   (prior ~54 s)
N=56  24.880 s   (prior ~102 s)
N=68  31.408 s   (no retained clean pre-optimization baseline)
```

A separate semantic replay compares the newly emitted JSON object against each retained Rust-verification JSON object for `C-0050` through `C-0054`; all five are exact parsed-JSON matches with `exit 0` and `passed=true`. Real `C-0054` adversarial replay remains fail-closed: wrong factor gives contract error `exit 2`, while a contract-valid negative diagonal gives theorem failure `exit 1` with the even block false and odd block true.

`cargo fmt -p rh_cert -- --check`, full `cargo test -p rh_cert --quiet`, and strict `cargo clippy -p rh_cert --all-targets -- -D warnings` pass. `X-20260827-003` retains the benchmark and implementation details. This is a tooling result only; no mathematical claim changed and RH remains unresolved.

**Outcome:** the immediate exact-verifier performance blocker is closed. Canonical one-prime continuation may resume with fresh dimension selection; do not extrapolate from `N=68`.

---

## 2026-08-27T13:16:15Z — Separate admission and independent replay establish T=19/40 theorem

**Type:** Closed-contract admission / fresh exact certificate / independent zero-float verifier / adversarial replay / theorem promotion

Following the deliberate `CANDIDATE_READY` stop in `X-20260827-001`, explicitly admitted only

```text
(T,N)=(19/40,68)
```

to the closed v1 `exact_prime_legendre_schur` profile. Admission testing exposed two stale shared dimension guards that still stopped at `56` (the JSON Schema exact-prime dimension/harmonic-index enums and Rust's internal exact-prime dimension guard); both were corrected while mixed `19/40` pairs remain rejected.

A fresh certificate was then reassembled from scratch at 384-bit Arb precision with 64-bit dyadic outward matrix endpoints and 32-bit exact rational witnesses. The independent Rust verifier returns

```text
passed=true
verified_scope=localized_weil_positivity_T_19_40
mu_68       > 0.7185353202932019
even margin > 0.0013831260220094517
odd  margin > 0.006360318287493695.
```

Real-certificate adversarial replay preserves the trust boundary: `factor=2` is a contract error (`exit 2`), while a contract-valid negative diagonal perturbation reaches theorem verification and fails (`exit 1`). The unchanged retained certificate exits `0`.

The current acceptance snapshot is green: default Python suite `409 passed, 2 slow tests deselected`; the new real `N=68` slow-acceptance generator test separately passes; the full `rh_cert` Rust suite passes; strict clippy passes; and `lake build` completes successfully.

The proof-bearing theorem run is `X-20260827-002`, establishing `F-20260827-001` / `C-0054`. The original `X-20260827-001` remains preserved as pre-theorem evidence. RH remains unresolved.

The next engineering slice is to optimize the exact zero-float Rust verifier before pushing the Legendre cutoff substantially farther, using the retained `C-0050` through `C-0054` certificates and adversarial cases as the semantic regression corpus.

---

## 2026-08-27T12:06:30Z — Canonical T=19/40 continuation reaches pre-theorem N=68 candidate

**Type:** Research continuation / canonical driver / precision-classified full-tail assembly / exact generator-side candidate

Continued `A-20260826-001` from the independently verified `T=9/20,N=56` theorem using the canonical `scripts.weil_continuation_driver` over the explicit range `N=48,52,...,80`.

The three-resolution floating scout classified `N=64,68,72,76,80` as stable-positive candidates, with `N=64` selected as the primary rigorous target and `N=68` as the fallback. Rigorous Arb precision escalation then separates a real failure from conditioning:

```text
N=64: 384/512-bit Schur midpoint ~ -0.18090174481401158
      => MATHEMATICAL_NEGATIVE

N=68: 256/384-bit Schur midpoint ~ +3.6658868513e-6
      => PRECISION_STABLE at 384 bits
```

At `N=68`, exact outward rationalization and exact parity congruence/Gershgorin witnesses succeed at the first attempted settings (`matrix_bits=64`, `witness_bits=32`), with approximate exact-rational lower margins

```text
mu_68       > 0.7185353202932019
even margin > 0.0013831260220094517
odd margin  > 0.006360318287493695.
```

The driver terminates at `CANDIDATE_READY`. The retained pre-theorem bundle is `X-20260827-001`; its manifest records clean commit `206f5678ca598568c4dfda65218d007f43a292ea` with `git_dirty=false`, and all twelve manifest artifact hashes were mechanically rechecked with no mismatch.

An execution-observability incident caused duplicate copies of the identical long-running driver command after the first Portus batch call crossed its tool timeout. The duplicate process trees were identified and terminated; the completed original bundle is retained and the incident is documented in the computation record.

**Outcome:** `(T,N)=(19/40,68)` is strong generator-side continuation evidence only. It has not been admitted to the closed theorem contract, no theorem certificate has been generated, no independent Rust theorem replay has been invoked, and no new theorem claim/finding has been created. The next action is the explicit human/research admission decision required by the hard pre-theorem boundary.

---

## 2026-08-26T19:05:17Z — One-prime continuation reaches T=9/20 with 512-bit N=56 certificate

**Type:** Research continuation / high-precision full-tail assembly / closed contract extension / exact rational certificate / independent verifier

Continued `A-20260826-001` from the verified `T=17/40,N=48` support theorem.

At

```text
T=9/20,
N=56,
```

the exact-polynomial/Arb full-tail assembly was run at 512-bit precision to control high-degree monomial conditioning. The Schur midpoint remains positive near `1.50e-5`, and the generator-side exact candidate survives 104-bit outward dyadic matrix rounding plus 56-bit rational congruence witnesses.

The closed `exact_prime_legendre_schur` v1 whitelist was extended by **only** `(T,N)=(9/20,56)` in addition to the three previously certified pairs.

The full `C-0053` certificate is independently accepted by Rust. The verifier derives

```text
mu_56 > 0.7060951994695617
even margin > 0.003888027441177187
odd  margin > 0.004366893328949625,
```

reconstructs the factor-3 Schur matrix, and returns `passed=true` with scope `localized_weil_positivity_T_9_20`.

The real certificate was adversarially replayed: a wrong factor is rejected as a contract error (`exit 2`), while a contract-valid negative finite-matrix perturbation produces theorem failure (`exit 1`). The retained certificate exits `0`.

Recorded `F-20260826-004`, `C-0053`, and `X-20260826-003`. The retained certificate SHA-256 is `98f2b839d7f52c971966e7f9da9ae4e318c30a491821ad86abee6411b51932e0`; the Rust replay SHA-256 is `e8f7b0b99e41687829da795582690af141e0c7fb833d273767b255bdc53180fe`. Generator provenance records commit `1336bf9c06460d4c4e1fda5f1a37a1f511d1bd3e` with `git_dirty=true`.

**Outcome:** strict localized Weil positivity is now independently verified at `T=7/20`, `T=2/5`, `T=17/40`, and `T=9/20`. RH remains unresolved. `A-20260826-001` stays `PROMISING`; the next support under study is `T=19/40`, beginning with fresh dimension selection.

---

## 2026-08-26T18:31:25Z — One-prime continuation reaches T=17/40 with high-precision N=48 certificate

**Type:** Research continuation / high-precision full-tail assembly / closed contract extension / exact rational certificate / independent verifier

Continued `A-20260826-001` from the verified `T=2/5,N=40` support theorem.

Because high-degree Legendre polynomials are represented in the monomial basis, the next candidate was assembled at 384-bit Arb precision rather than reusing low-precision exploratory settings. At

```text
T=17/40,
N=48,
```

the rigorous full-tail assembly has a positive Schur midpoint near `5.53e-5`, and the generator-side exact rational candidate survives 88-bit outward dyadic matrix rounding plus 48-bit rational congruence witnesses.

The closed `exact_prime_legendre_schur` v1 whitelist was extended by **only**

```text
(T,N)=(17/40,48),
```

in addition to the previously certified `(7/20,32)` and `(2/5,40)` pairs.

The full `C-0052` certificate is independently accepted by Rust. The verifier derives

```text
mu_48 > 0.7326484380944506
even margin > 0.0028958690673761525
odd  margin > 0.010715413283695166,
```

reconstructs the factor-3 Schur matrix, and returns `passed=true` with scope `localized_weil_positivity_T_17_40`.

The real certificate was adversarially replayed: a wrong factor is rejected as a contract error (`exit 2`), while a contract-valid negative finite-matrix perturbation produces theorem failure (`exit 1`). The retained certificate exits `0`.

Recorded `F-20260826-003`, `C-0052`, and `X-20260826-002`. The retained certificate SHA-256 is `6c74a386097bb30c2924f70d82e90d5ffc4d2dcb029543b7c973949948bdd325`; the Rust replay SHA-256 is `0378e6419b322eca7fc077271b1694bcb43e916592969e26827387aa8489958c`. Generator provenance records commit `b5405a9347a8b6bc6d3a8c022c4e0fa60e425361` with `git_dirty=true`.

**Outcome:** strict localized Weil positivity is now independently verified at `T=7/20`, `T=2/5`, and `T=17/40`. RH remains unresolved. `A-20260826-001` stays `PROMISING`; the next candidate support is `T=9/20`, where earlier reconnaissance suggests `N~56`.

---

## 2026-08-26T17:49:29Z — One-prime continuation reaches T=2/5 with independent exact certificate

**Type:** Research continuation / closed contract extension / exact rational certificate / independent verifier

Continued `A-20260826-001` from the provisional `T=2/5,N=40` candidate.

The `exact_prime_legendre_schur` v1 profile remains closed and now explicitly whitelists only

```text
(T,N)=(7/20,32)
(T,N)=(2/5,40).
```

A full `T=2/5,N=40` certificate was generated with 256-bit Arb assembly, 72-bit outward dyadic matrix endpoints, residual order `32`, and 40-bit exact rational congruence witnesses. The independent zero-float Rust verifier derives

```text
mu_40 > 0.7313021813837909,
even margin > 0.004176569432300938,
odd  margin > 0.013120531611009081,
```

reconstructs the factor-3 Schur matrix, and returns `passed=true` with scope `localized_weil_positivity_T_2_5`.

The real certificate was adversarially replayed: changing factor `3` to `2` is a contract error (`exit 2`), while a contract-valid negative diagonal perturbation produces theorem failure (`exit 1`). The unchanged certificate exits `0`.

Recorded `F-20260826-002` and promoted `C-0051` to `VERIFIED`. `X-20260826-001` now retains the proof-bearing certificate and Rust replay in addition to the earlier support/dimension diagnostics.

The theorem certificate records commit `b5405a9347a8b6bc6d3a8c022c4e0fa60e425361` with `git_dirty=true`; the dirty provenance is explicit in the artifact.

**Outcome:** strict localized Weil positivity is independently verified at both `T=7/20` and `T=2/5`. RH remains unresolved. `A-20260826-001` stays `PROMISING`; the next candidate support is `T=17/40`, where reconnaissance suggests `N~48`.

---

## 2026-08-26T17:28:53Z — One-prime support continuation selects T=2/5, N=40 as next exact target

**Type:** New research attempt / parameterized rigorous assembly / support reconnaissance / moving-dimension diagnosis / exact candidate witness

Started `A-20260826-001` from the verified `C-0050` basepoint at `T=7/20`.

The shared exact-prime Legendre-Schur assembler was parameterized in exact rational support `T` while the proof-bearing v1 certificate profile remains locked to the already proved `T=7/20,N=32` semantics.

A full-tail `N=32` support scan shows the Schur midpoint remains positive through the tested `T=0.37` but becomes negative at `T=0.375`. At that point the finite low block and the rigorous complement lower bound remain positive, so the first fixed-dimension failure is the low-to-tail Schur correction rather than observed operator negativity or immediate loss of complement coercivity.

Stable orthonormal-Legendre dimension reconnaissance suggested that increasing `N` should repair the tail correction. High-precision full-tail Arb assembly confirmed this:

```text
T=3/8, N=40:  Schur midpoint min ~ +4.83388e-4
T=2/5, N=40:  Schur midpoint min ~ +1.70302e-4
T=17/40,N=40: Schur midpoint min ~ -1.28340
T=9/20, N=40: Schur midpoint min ~ -4.23493.
```

The later supports are therefore not closed; truncated-tail reconnaissance suggests their required dimensions continue to grow (`~48` near `0.425`, `~56` near `0.45`).

The selected next rigorous point is

```text
T=2/5,
N=40.
```

A generator-side exact candidate was then constructed with rigorous Arb/exact-polynomial matrices, 72-bit outward rational endpoints, exact rational Schur construction, and 40-bit dyadic rational congruence witnesses. It gives strictly positive exact margins:

```text
mu_40 > 0.7313021813837909
even margin > 0.004176569432300938
odd  margin > 0.013120531611009081.
```

This is registered only as provisional `C-0051`: the independent Rust profile still rejects/generalizes nothing beyond its locked `C-0050` support. No theorem at `T=2/5` is claimed yet.

Recorded `F-20260826-001`, `C-0051`, and computation `X-20260826-001`.

**Outcome:** RH remains unresolved. `A-20260826-001` is `PROMISING`. The immediate next slice is independent Rust/schema verification of the single `T=2/5,N=40` candidate under a closed contract.

---

## 2026-08-21T13:52:37Z — A-004 closes with strict localized Weil positivity at T=7/20

**Type:** Research attempt completion / rigorous infinite-dimensional reduction / exact rational certificate / independent verifier / formal soundness

Completed `A-20260821-004`.

The exact-prime Legendre-Schur route now proves strict positivity of Suzuki's full scaled localized Weil quadratic form at

```text
T=7/20,
```

including the exact `p=2` compressed translation and the mandatory finite-support residual kernel.

The proof retains the earlier exact Legendre complement theorem and component tail-Gram Schur reduction. At `N=32`, the rigorous generator encloses `A_32`, `G_V`, `G_2`, and `G_R` using exact rational polynomial identities plus python-flint/Arb enclosures. The certified complement constant satisfies

```text
mu_32 > 0.8709101235096008.
```

The closed `rh-weil-certificate-v1` profile `exact_prime_legendre_schur` requires Rust to reconstruct

```text
S_32=A_32-(3/mu_32)(G_V+G_2+G_R)
```

rather than trusting a precomputed Schur matrix or eigenvalue. The even and odd `16 x 16` blocks are transformed by exact rational lower-triangular congruence witnesses and verified with exact interval Gershgorin bounds.

A final retained certificate was regenerated from clean commit

```text
d620aa649a2d0291e407d4c0c8bc7360b67efc38
```

with `git_dirty=false`. The independent Rust verifier returns `passed=true`, with exact positive margins approximately

```text
even > 0.01153505500311919
odd  > 0.04939032559587724.
```

Adversarial integration checks distinguish malformed contract data (exit `2`) from a contract-valid perturbation that destroys positivity (exit `1`); the retained theorem certificate exits `0`.

The Suzuki normalization was re-audited against pinned `R-0028`, including `c_T=log(2*pi*T)+EulerGamma`, the first-prime sign/coefficient, and the residual `-T r''(T(x-y))` scaling.

The formal layer was extended with `formal/Cert/Gershgorin.lean`, proving strict positive row Gershgorin dominance implies positive definiteness and that invertible congruence transfers positivity back to the original matrix. The full Lean build completed successfully with `8711` jobs.

Recorded `F-20260821-021`, `C-0050`, and computation `X-20260821-005`.

**Outcome:** `A-20260821-004` is `COMPLETE`; the fixed support theorem at `T=7/20` is `VERIFIED`. RH remains unresolved. The next frontier is support continuation in `T` through the one-prime window toward `(1/2)log 3`, where the `p=3` translation enters.

---

---

## 2026-08-21T08:52:52Z — A-004 pivots to exact-prime Legendre-Schur route

**Type:** Research attempt / rigorous obstruction / infinite-complement theorem / Schur reduction / numerical reconnaissance

Started `A-20260821-004`.

The initially planned target after `A-003` was to replace the exact first-prime pair by

```text
V+P_2 >= (69/100)V
```

and prove the remaining residual lower operator positive. This target is now rigorously refuted without invalidating the endpoint theorem itself. For the explicit polynomial

```text
w=P_0-P_2=(3/2)(1-x^2),
```

224-bit Arb computation with exact rational identities and the canonical Suzuki residual proves

```text
J(w)+(69/100)V(w)+R_T(w)-c_T||w||^2 < 0,
```

with value near `-0.05275381732676`. The critical retained scalar fraction for this direction lies between `0.93` and `0.94`.

Retaining the exact `p=2` translation instead changes the picture: the prime loss on this same smooth direction is only about `5.05e-5` of `V`, and the full exact-prime value is rigorously positive near `0.0143337515668`.

The decisive structural input is Tuck's Legendre identity. In Suzuki's jump normalization,

```text
J(P_n)=H_n||P_n||^2.
```

Therefore the high-mode Legendre complement has explicit logarithmically growing coercivity. Combining this with the exact prime norm and a rigorous Schur bound for Suzuki's residual gives

```text
C_N >= mu_N I,
mu_N=H_N-c_T-c_2-rho_R,
```

and `X-20260821-004` certifies `mu_14>0`.

The remaining infinite-dimensional cross problem is reduced to finite component tail Grams:

```text
G_X=P_N X Q_N X P_N
   =P_N X^2 P_N-(P_N X P_N)^2,
```

with the sufficient finite condition

```text
A_N-(3/mu_N)(G_V+G_2+G_R)>0.
```

A deliberately non-rigorous floating scout with tail Grams truncated at mode `120` becomes positive around `N=28`; `N=32` is selected as the first rigorous target, with an observed margin around `1.18e-3`.

Recorded `F-20260821-016` through `F-20260821-020`, `C-0045` through `C-0049`, computation `X-20260821-004`, and references `R-0032` through `R-0033`.

**Outcome:** RH remains unresolved. `A-20260821-004` is `PROMISING`. The next task is rigorous Arb assembly of `A_32`, `G_V`, `G_2`, and `G_R`, followed by exact interval Schur verification. The certificate contract will not be extended until those mathematical semantics are fixed.

---

## 2026-08-21T04:06:54Z — First-prime continuation sharpened; exact endpoint absorption proved

**Type:** Research attempt / exact rational certificate / finite-support normalization / external proof-code audit

Completed `A-20260821-003`.

At `T=7/20`, an exact rational certificate now proves the first-prime endpoint absorption estimate

```text
V + P_2 >= (69/100) V >= 0.
```

The proof establishes the required bounds for `log 2`, the endpoint parameter, and `log(2)/sqrt(2)` using exact `Fraction` arithmetic and a rational atanh-series remainder; no floating approximation is treated as a certificate.

The exact digamma multiplier also admits a monotone positive-kernel decomposition into terms

```text
(1/a_k)||f||^2 - integral integral exp[-2a_k|t-s|] f(t) conjugate(f(s)) dt ds >= 0.
```

A normalization audit of Suzuki's finite-support formula established that its residual finite-support kernel is mandatory. An exploratory Galerkin model that omitted this residual was therefore discarded before being registered as evidence.

The public `weil-first-prime` FP-0.35 proof-code architecture was audited at pinned commit `e66f467bc4447c5b2491577cbb6c3ae0e721fb43`. It is retained only as an unverified proof candidate: the inspected full-constant replay paths use point approximations or non-final LDL paths, while the more exact prime-layer gate corresponds to an easier `c_L=0` auxiliary problem. No external `FP-0.35 HOLDS` status was imported into this repository.

`X-20260821-003` retains the exact endpoint certificate and 256-bit Arb enclosures for `tau`, `c_2`, and the exact Suzuki Weil constant.

Recorded `F-20260821-012` through `F-20260821-015`, `C-0042` through `C-0044`, computation `X-20260821-003`, and references `R-0028` through `R-0031`.

**Outcome:** RH remains unresolved. The next target is an independent rigorous residual/Schur certificate at `T=7/20`, with exact transcendental intervals, the mandatory finite-support residual, parity-adapted finite blocks, and a justified infinite-dimensional complement bound.

---

## 2026-08-21T02:26:00Z — Positivity audit completed; first-prime Weil continuation becomes frontier

**Type:** Research attempt / positivity mechanism audit / operator reduction / literature cross-check

Completed `A-20260821-002`.

The ordinary Li coefficients admit the exact finite Gram kernel

```text
K_jk=lambda_j+lambda_k-lambda_|j-k|.
```

Under RH this is a sum of rank-one Gram matrices over Cayley zero phases. However `K_nn=2lambda_n`, so PSD of all finite matrices is immediately equivalent to Li's criterion rather than a weaker positivity theorem.

Likewise, under RH `lambda_|n|` is conditionally negative definite on `Z`; Schoenberg and Herglotz then produce the positive-definite semigroup `exp[-t lambda_|n|]` and a convolution semigroup of probability measures on the circle. The converse two-point CND test gives `lambda_n>=0`, so this structure is also exactly RH-equivalent.

The natural generalized prime contribution is not positive atom-by-atom: every prime-power Gram atom has first diagonal entry `-2A Lambda(m)m^(-s0)<0`.

The useful pivot is Weil's support formulation. For `supp f subset [-T,T]`, prime power `m` enters only at `T>(1/2)log m` and contributes a compressed translation operator. Restricted-support archimedean Weil positivity is known unconditionally from the Bombieri/Yoshida line and receives an operator-theoretic explanation in Connes-Consani.

For one shift `a`, the symmetrized compression decomposes into finite path graphs and has exact norm `2cos(pi/(L+1))`, `L=ceil(2T/a)`. Throughout the first-prime window `(1/2)log2<T<(1/2)log3`, only `m=2` is active and the shift norm is exactly `1`. The scalar size of the first arithmetic perturbation is therefore `log2/sqrt2=0.4901290717...`.

Recorded `F-20260821-006` through `F-20260821-011`, `C-0036` through `C-0041`, computation `X-20260821-002`, and references `R-0024` through `R-0027`.

**Outcome:** RH remains unresolved. The active target is now the constrained first-prime Weil operator `A_infinity(T)-(log2/sqrt2)S_(T,log2)` on `(1/2)log2<T<(1/2)log3`, preferably via a relative operator/Gram argument rather than a crude scalar norm comparison.

---

## 2026-08-21T02:09:00Z — Vaughan bilinear phase route closed; mechanism pivot required

**Type:** Research attempt / bilinear geometry / scale barrier / route closure

The UTC date rolled over before execution, so the item previously planned informally as `A-20260820-007` is formally recorded as `A-20260821-001` under the repository ID convention.

Completed `A-20260821-001`.

A Vaughan/Heath-Brown factorization of `Lambda` does not create new independent Laguerre phase directions. For `m=a_1...a_k` and `r_j=log a_j`, the phase is `Phi_n(r_1+...+r_k)` and its logarithmic Hessian is `Phi_n'' 1 1^T`, of rank one. The factor-redistribution directions preserving the product are exactly phase-flat.

On standard dyadic Type-II boxes the four-corner phase defect is `O(1/n)`, so the kernel is asymptotically separable into one-variable phases. `X-20260821-001` verifies the predicted `1/n` scaling. An `O(1)` cross phase first appears when balanced factor log-widths are of order `sqrt(n)`.

The formal full pre-turning Bessel phase has excursion `pi n`, only `n/2` full cycles, while fixed-interior prime scales are `X=exp(cn)`.

Most importantly, an unweighted prime estimate `X^(1-delta+o(1))` becomes `X^(1/2-delta+o(1))` after the critical half-weight. Reaching `exp(o(n))` therefore requires `delta>=1/2`: essentially square-root cancellation. A conventional fixed power saving below square-root remains exponentially too large.

Recorded `F-20260821-001` through `F-20260821-005`, `C-0031` through `C-0035`, computation `X-20260821-001`, and references `R-0021` through `R-0023`.

**Outcome:** RH remains unresolved. The direct Li/Laguerre prime-cancellation branch is blocked at an RH-scale arithmetic boundary; the next research action is a mechanism pivot to positivity/moment-matrix formulations rather than another finite divisor decomposition.

---

## 2026-08-20T22:44:00Z — Microlocal Dirichlet reduction completed; global bilinear structure becomes frontier

**Type:** Research attempt / endpoint closure / mean-value barrier / circularity check

Completed `A-20260820-006`.

The below-first-prime segment was closed exactly using DLMF 18.14.8:

```text
|S_n^[1,2)| <= 2A(sqrt(2)-1)n.
```

More generally, every shrinking endpoint `u<=eta_n=o(1)` is `exp(o(n))` by the same global Laguerre inequality and trivial `Lambda(m)<=log m`.

Actual prime atoms begin at `m=2`, so their maximal local Mellin frequency is

```text
gamma_2(n)
= A/2 sqrt(4n/(A log 2)-1)
~ sqrt(A n/log 2).
```

Thus the discrete prime side carries only `O(sqrt(n))` frequencies; the formal `gamma~n` endpoint from `A-005` lies below the first prime and is not the primary prime-sum obstruction.

On a fixed interior chirp cell, Taylor expansion in `y=log x` gives `Phi_n''(y)=O(1/n)`, so windows `H=o(sqrt(n))` linearize to smooth prime Dirichlet polynomials with coefficients `Lambda(m)m^(-1/2+i gamma_0)`.

The classical Montgomery-Vaughan mean-value theorem was then tested at the exact exponential scale. A cell centered at `u_0` has length `N=exp(4n u_0/A+o(n))`; because the available frequency range is only subexponential, the `O(N)` length term dominates and leaves RMS scale `exp(2n u_0/A+o(n))`, root base `exp(2u_0/A)>1`. Generic one-dimensional large-sieve/Dirichlet-polynomial `L2` machinery therefore does not close the route (`R-0020`).

A second guard was recorded: a matched smooth local cell is itself zero-sensitive through the Mellin explicit formula. Demanding `exp(o(n))` control independently for every such cell can reconstruct a zero-free statement window-by-window, consistent with the smooth-weighted PNT converse literature.

Created `F-20260820-022` through `F-20260820-026`, `C-0026` through `C-0030`, computation `X-20260820-008`, source `R-0019` for the DLMF Laguerre inequality, and `R-0020` for Montgomery-Vaughan.

**Outcome:** RH remains unresolved. The active target is now global arithmetic cancellation that preserves cross-cell structure, beginning with a Vaughan/Heath-Brown bilinear decomposition of the nonlinear chirp.

## 2026-08-20T22:15:00Z — Uniform pre-turning phase derived; arithmetic chirp becomes frontier

**Type:** Research attempt / asymptotic derivation / computation / circularity check

Completed `A-20260820-005`.

DLMF's uniform Laguerre Bessel expansion gives, for `L_(n-1)^(1)(4n*u)`, the phase

```text
4n xi(u)-3pi/4,
xi(u)=1/2[sqrt(u-u^2)+asin(sqrt(u))].
```

The exact frequency derivative is

```text
xi'(u)=1/2 sqrt((1-u)/u),
```

so a Mellin frequency `gamma>0` is matched at

```text
u_gamma=A^2/(A^2+4gamma^2),
A=2s0-1.
```

The earlier `A^2/(4gamma^2)` helper is exactly the large-`gamma` / small-`u` approximation of this uniform map.

For a fixed critical-line mode, the stationary phase equals the exact Cayley phase `n arg(z_rho^(-1))`, and the leading stationary amplitude simplifies exactly to `1`. This gives a local asymptotic mechanism for the `z_rho^(-n)` term in the exact zero response `z_rho^(-n)-1`.

On the prime side, the pre-turning kernel becomes an explicit nonlinear Mellin chirp acting on the critical-half-weight signed measure

```text
exp(-y/2)d(psi(e^y)-e^y).
```

A new limitation was also isolated: the relative stationary width is

```text
sigma_u/u_gamma=sqrt(2gamma/(A n)),
```

so high zero frequencies coalesce with the `u=0` endpoint when `gamma` is of order `n`; fixed-frequency stationary formulas cannot simply be summed over the entire zero spectrum.

Finally, if `M_N=sum_(n=N)^(2N)|S_n|^2`, then `limsup M_N^(1/(2N))<=1` is itself equivalent to RH. Generic coefficient-space Parseval/`L2` control is therefore a circular reformulation unless an independent arithmetic prime-side estimate is proved.

Created `F-20260820-017` through `F-20260820-021`, `C-0021` through `C-0025`, and computation `X-20260820-007`. Added `R-0016` through `R-0018` for Lagarias, Arias de Reyna, and the DLMF Bessel/stationary-phase sources.

Automated verification after the phase-tooling changes: Python `276/276` tests passed and the Rust workspace passed `15/15` tests.

**Outcome:** RH remains unresolved. The active target is now an unconditional arithmetic cancellation theorem for the critical-half-weight nonlinear prime chirp, together with a valid high-frequency endpoint treatment.

---

## 2026-08-20T22:10:00Z — Research environment and phase-helper contract hardened

**Type:** Research infrastructure / reproducibility / correctness guard

Verified the project `.venv` on CPython 3.14.0 with the pinned scientific stack, including `mpmath`, SciPy, NumPy, SymPy, Matplotlib, python-flint/Arb, GMPY2, pytest, and Hypothesis. The Python test suite and Rust workspace tests were passing before this cleanup.

Corrected the maintained environment contract to Python `>=3.12`, aligned repository documentation with the scientific environment and native `crates/rh_engine` CLI, and added `uv.lock` as the resolver lockfile.

Removed the unregistered hard-coded zeta-zero fallback from `scripts/rh_tools.py`; zero ordinates are now explicitly numerical values produced by the pinned `mpmath` dependency, not described as certified data.

Hard-cut the provisional phase API from generic `stationary_*` names to `small_u_stationary_*`. These formulas only encode the small-`u` approximation obtained from the phase `2 sqrt(n t)` and are not accepted as the uniform pre-turning stationary map. `A-20260820-005` remains responsible for deriving the genuine uniform Bessel phase before any broader phase helper is introduced.

Historical computation records that truthfully used only the standard library were left unchanged.

Post-change verification: `uv sync --extra test --locked` completed without environment changes, all research scripts compiled, the Python suite passed `273/273`, and the Rust workspace passed `13/13` tests.

**Outcome:** infrastructure corrected without changing any RH claim or research conclusion.

---

## 2026-08-20T21:20:00Z — Airy-window plan refined to phase-aware full transform

**Type:** Research attempt / correction / computation / literature boundary check

Completed `A-20260820-004`.

The planned narrow Airy-window strategy was tested rather than assumed. The smooth-density maximum from `A-003` is separated from the true Airy turning transition by a fixed distance in `u`; its Gaussian width is `O(n^(-1/2))`, while the Airy transition itself has width `O(n^(-2/3))`. It is therefore more accurately a post-turning Laplace saddle represented by the uniform Airy formula.

The sufficiently far post-turning tail can be suppressed unconditionally. However, the pre-turning region retains positive absolute-envelope root growth under current unconditional PNT errors, so it cannot be discarded by absolute-value estimates.

A new exact identity was derived for one explicit-formula zero mode:

```text
S_(n,rho)=z_rho^(-n)-1,
z_rho=(rho-s0)/(rho+s0-1).
```

This shows directly that the complex phase is essential. `X-005` quantifies the gap between beta-only envelopes and exact Cayley rates, while `X-006` numerically reproduces the exact complex Laplace transform and shows cancellation across `u` regions.

A literature check also closed the generic mean-square shortcut: Zhao's published Lemma 8 shows that the dyadic mean-square exponent of `psi(x)-x` changes with `Theta=sup Re(rho)`, so RH-scale `L^2` control already forces the RH boundary. Han's smooth-weighted-PNT converse results provide a parallel circularity warning for strong smoothed error estimates.

Recorded `F-20260820-013` through `F-20260820-016`, `C-0017` through `C-0020`, `X-20260820-005` through `X-20260820-006`, and sources `R-0013` through `R-0015`.

`A-003` is preserved but marked `SUPERSEDED` as the active frontier, with a timestamped terminology/strategy addendum.

**Outcome:** RH remains unresolved. The next route must preserve phase in the full Laguerre transform rather than reduce the problem to absolute local discrepancy norms.

---

## 2026-08-20T21:05:31Z — Research tooling added; Airy saddle identified

**Type:** Research attempt / computation / derived asymptotic structure

Created `A-20260820-003` and a dependency-free Python research toolkit under `scripts/`.

The tooling includes exact rational identity verification, high-precision prime-trace cutoff studies, uniform-scale kernel scans, and prime-versus-density range decomposition. Four reproducible computation records were created as `X-20260820-001` through `X-20260820-004`.

### Analytic findings

The pole-subtracted discrepancy transform was integrated by parts exactly:

```text
S_n=A n-A integral E(x)f_n'(x)dx,
E(x)=psi(x)-x.
```

Only the ordinary prime number theorem `E(x)=o(x)` is needed to close the upper boundary for fixed `n`.

Using DLMF's uniform Laguerre scaling, `L_(n-1)^(1)` has

```text
nu=4n,
u=t/(4n).
```

The smooth prime-density Airy envelope has its unique exponential saddle at

```text
u_*=A^2/(A^2-1).
```

Its exponential rate simplifies exactly to

```text
[s0/(s0-1)]^n=|q|^n.
```

Thus the deterministic zeta-pole mode removed algebraically in `A-002` is also the dominant smooth-density saddle of the uniform Laguerre asymptotics.

A generalized-center tradeoff was derived: increasing `s0` lowers the moving prime scale but proportionally weakens the Cayley amplification of a hypothetical off-line zero. No free asymptotic gain appears.

Finally, `A-003` shows that a direct absolute-value estimate using any fixed pointwise exponent `|psi(x)-x|=O(x^theta)` with `theta>1/2` still leaves positive exponential growth. The next route must use signed/averaged cancellation in the Airy window rather than a pointwise estimate alone.

### Computation highlights

- exact core identities passed through `n=40` at `s0=2,3,5/2,4`;
- for `s0=3`, the sampled kernel maximum moved from `u=1.0211` at `n=64` to `u=1.0362` at `n=256`, toward the predicted `25/24`;
- a turning-region bin at `s0=3`, `n=16` had prime and smooth-density contributions around `-325.8` differing by about `-0.0203`; doubling Simpson resolution preserved the discrepancy;
- cutoff studies confirmed that the necessary prime range moves rapidly with `n` and that larger `s0` improves numerical reach without changing the underlying analytic difficulty.

Recorded `F-20260820-009` through `F-20260820-012`, `C-0013` through `C-0016`, and sources `R-0011` through `R-0012`.

**Outcome:** RH remains unresolved. The active target is now localized to prime-counting discrepancy in a uniform Airy window.

---

## 2026-08-20T20:49:00Z — Raw prime target corrected; pole-subtracted criterion derived

**Type:** Research attempt / correction / derived criterion

Completed `A-20260820-002`.

The planned finite-difference analysis exposed a more basic issue: for every generalized center `s0>1`, the raw prime-Laguerre sequence contains the deterministic exponential mode

```text
1-q^n,
q=-s0/(s0-1),
```

coming from the known pole of `zeta(s)` at `s=1`. Therefore the previous broad target "prove the generalized prime trace subexponential" is impossible even under RH.

A timestamped correction was appended to `A-20260820-001`; its historical derivation was not silently rewritten.

The hard-cut replacement is

```text
S_n=P_n-(1-q^n).
```

This subtraction is exact: `-S_n` is the Taylor coefficient sequence of

```text
d/dz log[(s(z)-1)zeta(s(z))].
```

Consequently, for every fixed `s0>1`,

```text
RH <=> limsup |S_n|^(1/n) <= 1.
```

The same sequence has the exact prime-discrepancy representation

```text
S_n
= A integral x^(-s0)L_(n-1)^(1)(A log x) d(psi(x)-x).
```

The degree-two shift filter `(E-1)(E-q)` was also derived; it annihilates the pole sequence exactly and converts the prime kernel to an order-zero Laguerre combination.

Recorded `F-20260820-005` through `F-20260820-008`, `C-0009` through `C-0012`, and `R-0010`.

**Outcome:** no proof of RH. The research target is now the pole-subtracted discrepancy kernel, not the raw prime density.

---

## 2026-08-20T20:37:00Z — First RH attempt imported and source-verified

**Type:** Research attempt / literature verification / correction

Created `A-20260820-001`, documenting the Li-coefficient / generalized-center / Laguerre-weighted prime-trace route explored before the repository protocol was initialized.

Recorded `F-20260820-001` through `F-20260820-004`, `C-0001` through `C-0008`, and `R-0001` through `R-0009`.

The pre-protocol critical-line "quartet" value `8 sin^2(n theta/2)` was corrected to the distinct-pair contribution `4 sin^2(n theta/2)`; the historical error remains explicitly documented.

**Outcome:** the generalized center is analytically useful but does not give a simple escape from the critical `1/2` scale. The raw-prime-trace part of this attempt was later corrected by `A-002`.

---

## 2026-08-20T20:33:00Z — Documentation system initialized

**Type:** Repository governance / research infrastructure

Created the authoritative timestamped documentation structure, claim ledger, bibliography, templates, and README navigation instructions.

No mathematical proof claim was created by this initialization.
