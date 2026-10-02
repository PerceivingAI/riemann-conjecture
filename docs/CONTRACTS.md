# Repository Architecture & Proof Contracts

- **Created:** `2026-08-21T06:00:00Z`
- **Last updated:** `2026-10-01T21:04:17Z`
- **Status:** Authoritative

This document defines the formal software architecture, proof-certificate contracts, and dependency policies governing research and computation in this repository.

---

## 1. The Decoupled Trust Chain

### Architectural Invariant
> **Decoupled Verification Principle**: The computational environment generating a mathematical certificate MUST NEVER be the sole environment deciding its validity.

In mathematical research, numerical bugs, floating-point rounding, compiler optimizations, or library quirks can lead a single program to falsely validate its own output. To eliminate single-point-of-failure risks, all numerical proof claims in this repository follow a decoupled three-tier trust chain:

```text
+-------------------------------------------------------------------+
| 1. Analytic Derivation & Rigorous Generator (Python / Arb)        |
|    - Scripts under scripts/cert/ using python-flint (Arb/ACB/FMPQ)|
|    - Computes proven interval enclosures of integrals & constants |
|    - Emits outward rational endpoints (lo_num, lo_den, etc.)      |
+-------------------------------------------------------------------+
                                  │
                                  ▼
+-------------------------------------------------------------------+
| 2. Standardized Mathematical Proof Artifact (JSON Certificate)    |
|    - Format: rh-weil-certificate-v1                               |
|    - Strictly exact rational arithmetic; zero floating-point data |
|    - Schema: docs/contracts/rh-weil-certificate-v1.json           |
+-------------------------------------------------------------------+
                                  │
                                  ▼
+-------------------------------------------------------------------+
| 3. Independent Exact Verifier (Rust: crates/rh_cert)              |
|    - Pure-Rust arbitrary-precision arithmetic (num-bigint,        |
|      num-rational). Zero f32/f64 types allowed.                   |
|    - Exact interval Schur complement / LDLᵀ decomposition         |
|    - Emits deterministic binary PASS (exit 0) or FAIL (exit 1)    |
+-------------------------------------------------------------------+
```

---

## 2. Certificate Specification (`rh-weil-certificate-v1`)

All mathematical certificates produced by the repository must conform to the JSON Schema at `docs/contracts/rh-weil-certificate-v1.json`.

### 2.1 Mandatory fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `format` | `string` | Must be strictly `"rh-weil-certificate-v1"`. |
| `claim` | `string` | Non-empty certificate identifier. It does not select verifier behavior. |
| `claim_profile` | `string` | Closed verifier profile: `synthetic_matrix`, `digamma_finite_block`, or `exact_prime_legendre_schur`. |
| `support_T` | `object` | Canonical exact rational support parameter $T$ (`num`, `den`, `frac`). |
| `basis` | `object` | Closed basis parameterization (`type`, `dimension`, `domain`). |
| `parity_sector`| `string` | Parity sector under verification: `"even"`, `"odd"`, or `"both"`. |
| `dimension` | `integer` | Finite block matrix dimension $N \ge 1$. |
| `constants` | `object` | Closed set of rational intervals required by the selected claim profile. |
| `matrix` | `object` | Exactly $N^2$ rational interval entries. |
| `tail_bound` | `object` | Closed profile-specific proof rule. Depending on the claim profile, Rust derives either a scalar identity remainder, a nonnegative remainder, or the Legendre complement/Schur factor. |
| `schur_proof` | `object` | Required only by `exact_prime_legendre_schur`; contains rigorous component tail-Gram matrices and exact rational parity congruence witnesses. |
| `generator_metadata` | `object` | Generator, script, versions, Git commit and dirty state, precision, and UTC timestamp. |

### 2.2 PASS semantics

The verifier first validates every structural and cross-field invariant, then executes only the proof rule associated with the closed `claim_profile`. There is no generic free-form theorem assertion.

For `synthetic_matrix`, let $\mathcal A$ be the exact symmetric matrix family represented by the serialized intervals. `exact_scalar_identity` supplies an exact rational $\lambda$, Rust forms
$$\mathcal A_{\rm adjusted}=\{A+\lambda I:A\in\mathcal A\},$$
and PASS means exact interval $LDL^T$ proves every adjusted matrix positive definite. This profile exists only to test verifier arithmetic.

For `digamma_finite_block`, the serialized finite partial-sum matrix is checked by exact interval $LDL^T$. The `nonnegative_digamma_remainder` theorem gives zero as a rigorous lower bound for the omitted brackets, extending the result to the full digamma series on the selected finite basis. It does not control an infinite-dimensional basis complement and is not a full localized-Weil profile.

For `exact_prime_legendre_schur`, v1 uses a **closed whitelist**, not a parameter-open theorem profile. The admitted configurations are exactly

```text
(T,N)=(7/20,32)
(T,N)=(2/5,40)
(T,N)=(17/40,48)
(T,N)=(9/20,56)
(T,N)=(19/40,68)
(T,N)=(1/2,80)
(T,N)=(21/40,96)
(T,N)=(27/50,104)
```

with both parity sectors, residual order `32`, and exact Schur factor `3`. Rust does **not** trust a precomputed Schur matrix. For the admitted dimension `N`, it derives
$$\mu_N=H_N-c_T^{\rm hi}-c_2^{\rm hi}-\rho_R^{\rm hi},$$
requires $\mu_N>0$, and forms
$$S_N=A_N-\frac{3}{\mu_N}(G_V+G_2+G_R).$$
The certificate supplies exact rational invertible lower-triangular congruence witnesses for the even and odd `N/2 x N/2` blocks. Rust recomputes each interval congruence $CSC^T$ and requires every row to have a strictly positive Gershgorin lower margin. PASS therefore certifies positivity of the full localized operator for that explicitly whitelisted support/dimension pair through the separately proved complement/Schur reduction, not merely positivity of a finite Ritz block.

Rust must reject the certificate before theorem verification if the claim profile, support, basis, parity, constants, matrices, proof witness, or provenance is invalid or inconsistent. A finite-block diagnostic must not be reported as a full-operator result.

### 2.3 Rational interval entry semantics
Every matrix entry is serialized as an exact rational interval $[lo, hi]$ using integer string numerators and denominators:
```json
{
  "row": 0,
  "col": 1,
  "lo_num": "1",
  "lo_den": "2",
  "hi_num": "3",
  "hi_den": "4"
}
```
- A valid entry must satisfy $\text{lo\_den} > 0$, $\text{hi\_den} > 0$, and $\frac{\text{lo\_num}}{\text{lo\_den}} \le \frac{\text{hi\_num}}{\text{hi\_den}}$.
- Floating-point representations (e.g. `0.5`, `1.2e-4`) are strictly prohibited in certificate entries.

### 2.4 Pinned theorem inputs

The finite-support residual claim uses Masatoshi Suzuki, "Weil's quadratic form via the screw function," arXiv `2606.09096v2`, dated August 18, 2026. The pinned arXiv source archive has SHA-256 `96183f5aea5367e7a483809a96e8dc791b7672bac07fb57ccfa9da82d8295002`. The extracted `screwzelf_7.tex` file has SHA-256 `7a295689e9add1fd0ed25c34f61b7288ee25cb0f1bbd52ec6250bf2e62e03964`.

The certificate normalization comes from these equations:

- Equation (2.2) defines the local expansion and the even residual function `r`.
- The discussion after equation (2.7) decomposes
  $$r(t)=r_0(t)+r_1(t),$$
  where
  $$r_0(t)=-4\left(e^{t/2}+e^{-t/2}-2\right)$$
  and
  $$r_1(t)=\frac14\sum_{n=2}^{\infty}\zeta(2-n,1/4)\frac{(-2|t|)^n}{n!}.$$
- For $t\ne0$, the resulting even second derivative is
  $$r''(t)=-\left(e^{t/2}+e^{-t/2}\right)
  +\frac{e^{-|t|/2}}{1-e^{-2|t|}}-\frac{1}{2|t|},$$
  with the removable value $r''(0)=-7/4$.
- Equation (4.5) contributes the scaled residual quadratic form
  $$-T\int_{-1}^{1}\int_{-1}^{1}
  r''\!\left(T(x-y)\right)w(y)\overline{w(x)}\,dx\,dy.$$

Any certificate profile that names the Suzuki residual must use this normalization. A later paper version requires a new source hash and an explicit normalization review before use.

### 2.5 Closed proof rules

Version 1 contains three closed proof rules.

`exact_scalar_identity` defines the certified operator remainder to be exactly $\lambda I$, where $\lambda$ is an exact rational in the certificate. This rule is restricted to synthetic verifier claims. Rust adds $\lambda$ to every diagonal entry before LDL.

`nonnegative_digamma_remainder` applies only to the `digamma_finite_block` claim profile. For
$$a_k=k+\frac14,$$
the omitted bracket is
$$B_k=\frac{1}{a_k}I-K_k,$$
where $K_k$ has kernel $e^{-2a_k|t-s|}$. Zero extension to the real line and the $L^1$ norm
$$\int_{\mathbb R}e^{-2a_k|u|}\,du=\frac1{a_k}$$
give $\langle f,K_kf\rangle\le a_k^{-1}\lVert f\rVert_2^2$. Hence every omitted $B_k$ is nonnegative and the verifier-derived tail lower bound is exactly zero. The witness contains `k_max` and `first_omitted_k`; Rust must check `first_omitted_k = k_max + 1`.

`legendre_component_gram_schur` applies only to `exact_prime_legendre_schur`. In v1, `harmonic_index` must equal the whitelisted finite dimension (`32`, `40`, `48`, `56`, `68`, `80`, `96`, or `104`) and the factor must be the exact rational `3`. The required constants are only `c2`, `c_T`, and `rho_R`; the required proof matrices are `GV`, `G2`, and `GR`. Opposite-parity entries in `A`, `GV`, `G2`, and `GR` must be exactly zero. Rust derives the lower complement constant from the upper endpoints of those scalar intervals, reconstructs the factor-3 Schur matrix, extracts its even and odd blocks, and checks the supplied exact rational lower-triangular congruence witnesses for invertibility before applying exact interval Gershgorin positivity.

The retained `C-0050` (`T=7/20,N=32`), `C-0051` (`T=2/5,N=40`), `C-0052` (`T=17/40,N=48`), `C-0053` (`T=9/20,N=56`), `C-0054` (`T=19/40,N=68`), `C-0055` (`T=1/2,N=80`), `C-0056` (`T=21/40,N=96`), and `C-0057` (`T=27/50,N=104`) certificates use this rule and are proof-bearing because `C-0045`, `C-0047`, and `C-0048` provide the analytic complement and Schur semantics encoded by the profile. `C-0057` was generated afresh from clean committed provenance, independently accepted by zero-float Rust, passed real-certificate contract/theorem adversarial checks, and is explicitly registered in the retained-proof manifest. Each theorem-bearing pair requires explicit closed-contract admission followed by fresh independent replay and explicit registration; whitelist admission alone never grants theorem status. No other `(T,N)` pair is admitted.

**Frozen v1 boundary — `2026-10-01T09:46:49Z`.** The one-prime theorem contract above is now a historical compatibility boundary for multi-prime development. New structural-window work must not add `c3`, `G3`, new support/dimension admissions, or altered complement/Schur semantics to `rh-weil-certificate-v1`. The Python generator, Python semantic validator, JSON Schema, Rust v1 verifier, and retained `C-0050..C-0057` registrations remain independently closed to the eight configurations above. New prime-power semantics require a separate profile/format and verifier path. `tests/test_one_prime_v1_freeze.py` guards the fast semantic baseline; `scripts.cert.verify_retained_proofs` remains the byte-level and independent-replay authority for the eight stored theorem artifacts.

### 2.6 Retained theorem-artifact acceptance

Proof-bearing retention is governed by the closed manifest `computations/retained-proofs.json`. Its v1 entries bind each retained theorem claim to one computation ID, repository-relative certificate path, raw-byte SHA-256, support, dimension, claim profile, and verified scope. The manifest contains exactly `C-0050` through `C-0057`; pre-theorem candidates and tooling computations are not proof registrations. The canonical current replay passes `8/8`. The repository-wide closure acceptance also passes the default Python suite, full `rh_cert` tests, strict Clippy, and the authoritative Lean build; these quality gates validate the implementation/trust layers but do not broaden the mathematical scope beyond the eight explicitly retained finite-support claims.

The canonical audit is:

```text
uv run --locked python -m scripts.cert.verify_retained_proofs
```

The audit never regenerates a certificate. For each registered artifact it requires a safe regular-file path inside the repository, exact SHA-256 agreement before replay, `rh_cert` exit `0`, `passed=true`, and exact agreement on claim/support/dimension/profile/scope. Hash-invalid artifacts are never submitted to the verifier. The gate is exhaustive across the manifest and exits `0` only for a complete pass.

This retained-artifact gate does not create theorem status and does not replace the original admission + fresh independent replay required for a new theorem pair. It is a continuing integrity/replay assertion over theorem artifacts that already obtained proof-bearing status through the closed theorem contract.

The v1 registry is deliberately explicit: tooling must not discover or promote proof artifacts by scanning `computations/`. A certificate becomes part of this retained-proof gate only through an intentional manifest edit to the closed whitelist. The manifest records artifact identity and theorem identity only; derived verifier diagnostics such as Gershgorin margins are intentionally omitted because the certificate hash already fixes the proof bytes and `rh_cert` re-derives those diagnostics independently.

No other tail/proof type is valid. In particular, v1 does not accept a free-form description, an asserted lower bound for an unspecified operator, or a precomputed eigenvalue/positive-definite flag.

### 2.7 Admission-table consistency without shared production authority

The exact-prime whitelist is intentionally duplicated across independent production trust layers: the Python theorem exporter, Python semantic validator, JSON Schema, and Rust verifier. They must **not** load one shared production whitelist, because that would turn an admission mistake in the shared source into a correlated acceptance mistake across the supposedly independent layers.

`tests/data/exact-prime-admission-v1.json` is therefore a **test-only expectation corpus**, not production configuration. It lists the eight admitted pairs, all fifty-six mismatched cross-pairs formed from the admitted supports and dimensions, and selected external forbidden cases including `(T,N)=(19/40,64)`, `(19/40,72)`, `(1/2,76)`, `(21/40,92)`, `(21/40,100)`, `(27/50,100)`, and `(27/50,108)`. Python and Rust tests independently execute the corpus against their own hard-coded admission rules, while the raw JSON Schema branch is tested separately. `docs/CONTRACTS.md` is also checked to name every admitted pair.

Production Python/Rust source must not load the test corpus at runtime. Updating the corpus does not admit a theorem pair: admission still requires the explicit research decision, independent closed-contract edits, fresh certificate generation, and independent Rust PASS. The consistency corpus detects accidental whitelist drift; it is not mathematical evidence and cannot justify an admission by itself.

Canonical focused checks:

```text
uv run --locked --extra test python -m pytest -q tests/test_admission_consistency.py
cargo test -p rh_cert --test test_exact_prime_schur exact_prime_admission_matches_shared_test_corpus
```

### 2.8 Locked adversarial cases

The Python and Rust validators must reject the following cases before theorem verification unless the row explicitly names a theorem-verification failure:

| Case | Required result |
| :--- | :--- |
| Zero or negative support denominator | Semantic validation failure |
| Malformed or inconsistent support fraction | Semantic validation failure |
| Unknown basis or parity value | Schema validation failure |
| Basis, matrix, or top-level dimension mismatch | Semantic validation failure |
| Missing constants or generator metadata | Schema validation failure |
| Duplicate, missing, or out-of-range matrix coordinate | Semantic validation failure |
| Zero interval denominator or reversed interval | Semantic validation failure |
| Unknown, missing, or inconsistent tail witness | Schema or semantic validation failure |
| Ordinary floating-point proof data | Schema validation failure |
| `exact_prime_legendre_schur` with factor other than exact `3` | Semantic validation failure |
| `exact_prime_legendre_schur` with unsupported/mixed `(T,N)` pair | Schema or semantic validation failure |
| `exact_prime_legendre_schur` with nonpositive derived `mu_N` | Semantic validation failure |
| Singular/non-lower-triangular congruence witness | Semantic validation failure |
| Nonzero opposite-parity proof entry | Semantic validation failure |
| Contract-valid exact-prime perturbation that destroys a Gershgorin margin | Theorem failure, not contract failure |
| Matrix `[1]` with `exact_scalar_identity` value `-2` | Adjusted LDL failure |

### 2.9 Frozen multi-prime mathematical contract

The authoritative pre-implementation mathematical contract is [`docs/MULTI_PRIME_CONTRACT.md`](MULTI_PRIME_CONTRACT.md). It is additive to the frozen v1 theorem path and does not alter `rh-weil-certificate-v1`.

For any support `T`, active arithmetic terms are the prime powers

```text
A(T)={m=p^k : log(m)<2T},
tau_m=log(m)/T,
c_m=Lambda(m)/sqrt(m).
```

The signed arithmetic contribution is grouped as one operator `P=sum_m P_m`, with `P_m=-c_mS_m`. For rigorous compressed-shift norm bounds `||S_m||<=b_m`, the generic complement contract is

```text
mu_N=H_N-c_T-sum_m c_m b_m-rho_R.
```

In `(log3)/2<T<(log4)/2`, exactly `m={2,3}` are active and the exact shift-norm formula gives `b_2=b_3=1`, hence `mu_N=H_N-c_T-c_2-c_3-rho_R` (`C-0058`).

The critical factor-3 gate is explicitly closed by `C-0059`: after grouping arithmetic first, the cross block remains `B_V+B_P+B_R`, so the same three-component Cauchy-Schwarz argument gives

```text
S_N=A_N-(3/mu_N)(G_V+G_P+G_R).
```

The arithmetic tail Gram is the Gram of the **combined** operator:

```text
G_P=Pi_N P Q_N P Pi_N.
```

In the unnormalized low Legendre basis it is represented as

```text
G_P=P^2-PD^{-1}P,
```

where the first `P^2` is the low matrix of the operator square. For the immediate window `P=P_2+P_3`, this square includes the mixed terms `P_2P_3+P_3P_2`. A future implementation that substitutes `G_2+G_3` for `G_P` violates the frozen contract. The factor `3` counts grouped components `V,P,R`; it does not count prime powers.

This section closes the mathematical derivation only. No multi-prime certificate profile, verifier path, theorem whitelist, or retained theorem registration exists yet. Any such implementation must be separate from v1 and independently verified before theorem use.

**P2 operator-core implementation — `2026-10-01T10:28:50Z`.** `scripts/cert/prime_power_terms.py` now implements the generic arithmetic operator side of this contract without altering the frozen v1 path. It independently recognizes prime powers, rigorously derives their Arb constants, enumerates the strict active set with fail-closed threshold decisions, constructs the combined compressed translations by piecewise polynomial action, derives the combined `P` and operator-square `P^2`, and then computes `G_P=P^2-PD^{-1}P`. The implementation deliberately works beyond the `tau_m>1` geometry used by the historical edge shortcut; tests exercise `{2,3,4}` with `tau_2<1`. This does **not** create a certificate profile or PASS semantic: multi-prime certification remains absent until a later phase.

**P3 rigorous assembler bridge — `2026-10-01T10:55:56Z`.** `scripts/cert/multi_prime_legendre_schur.py` now assembles the complete grouped `V,P,R` Schur reduction using the generic P2 arithmetic operator. Canonical outputs include `active_terms`, `P`, `P_squared`, `A`, `GV`, `GP`, `GR`, `rho_R`, `mu`, and `schur`. Before `{2,3}` use, four one-prime overlap cases (`7/20,N=16`; `2/5,N=24`; `17/40,N=28`; `9/20,N=32`) reproduce the frozen path enclosure-by-enclosure for `P`, `P^2`, `GP/G2`, `A`, `mu`, and the Schur matrix, with the shared `GV`, `GR`, and `rho_R` also agreeing. A subsequent `{2,3}` test proves the combined `P^2` is not `P_2^2+P_3^2`: its constant-mode cross contribution is rigorously nonzero. The focused integrated target passes `31/31` and the complete default Python suite passes `574/574`. P3 still defines no serialized certificate or verifier semantics.

**P4 scout/candidate boundary — `2026-10-01T11:15:33Z`.** Multi-prime reconnaissance and exact candidate construction are now separate stages. `weil_multi_prime_schur_scout.py` is floating-only and has no Arb/certificate dependency; its truncated `GV/GP/GR` and conditioning values are non-proof diagnostics. `weil_multi_prime_support_candidate_check.py` uses the rigorous assembler and exact interval/witness primitives, but remains generator-side pre-theorem evidence. Its exact complement is reconstructed from `c_T + sum_m(c_m b_m) + rho_R`, with every active term outward-rounded and reported separately; the exact Schur uses `A/GV/GP/GR` and factor `3`. Precision, matrix-bit, and witness-bit controls are independent. Focused acceptance passes `24/24` and the complete default Python suite passes `578/578`. No P4 output is a theorem certificate or verifier PASS semantic.

**P5 continuation-driver contract — `2026-10-01T16:20:18Z`.** `scripts/weil_multi_prime_continuation_driver.py` is the canonical continuation orchestrator for new structural windows; it is not a mode switch in the frozen one-prime driver. Its initial admissible research window is strictly `log(3)/2 < T < log(4)/2`, and the driver independently fails closed unless the rigorous active set is exactly `{2,3}`. The driver may end only in the inherited terminal states, including `NO_CANDIDATE`, `SCOUT_UNSTABLE`, `PRECISION_LIMIT_REACHED`, structured candidate failures, or pre-theorem `CANDIDATE_READY`. Completion order is observational only: parallel scout/rigorous results are materialized in deterministic canonical order. Cache keys include a source fingerprint over the multi-prime mathematical dependencies. Bundle publication remains atomic/manifest-last and requires verified worker cleanup. The shared bundle format accepts exactly the historical and multi-prime pre-theorem driver roles; neither role can carry theorem admission or independent-verification status. The complete default Python suite passes `591/591` after this cutover.

**P6 certificate-v2 contract — `2026-10-01T17:51:51Z`.** `rh-weil-certificate-v2` is a separate format with the single current profile `multi_prime_power_legendre_schur`; v1 is frozen and is not migrated in place. V2 certificate structure is `support_T + Legendre basis + constants(c_T,rho_R) + arithmetic_terms + A matrix + tail_bound + schur_proof + generator_metadata`. Each `arithmetic_terms` entry contains exact identity `m,base_prime,exponent` and rational interval data for `log_m,tau,von_mangoldt,coefficient,compressed_shift_norm_bound,complement_contribution`. Canonical structural validation requires terms strictly increasing by `m`, verifies that the base is prime and `m=base_prime^exponent`, requires reduced rational interval endpoints, and checks cross-field matrix/parity dimensions. The Schur proof requires exactly `GV,GP,GR` plus exact even/odd witnesses; legacy `G2/G3` fields are invalid. The tail rule is closed to `prime_powers_with_log_m_lt_2T`, complement rule `H_N-c_T-sum(c_m*b_m)-rho_R`, grouped components `V,P,R`, factor exactly `3/1`, and `factor_claim=C-0059`. Schema/structure validity is explicitly not theorem admission. Production `V2_ALLOWED_CONFIGURATIONS` is empty; therefore no v2 support/dimension pair is currently admitted. Focused P6/frozen-v1/admission acceptance passes `21/21`, and the complete default Python suite passes `602/602`.

**P7 independent Rust-v2 verifier contract — `2026-10-01T18:22:11Z`.** Certificate dispatch first reads only `format` and routes v1 to the frozen `cert.rs` implementation or v2 to the separate `v2.rs` implementation. For v2, Rust independently enforces reduced exact-rational syntax, support/basis/parity consistency, canonical full matrices, sorted unique arithmetic terms, exact first-window active set `[2,3]`, prime-power identities, `b_m=1`, and the closed `C-0059` tail rule. It derives `tau_m=log_m/T` and `Lambda(m)=log_m/exponent` as exact-rational interval consistency checks, derives each prime loss as `coefficient * b_m`, requires the serialized complement contribution to enclose that derived interval, then computes the conservative exact-rational lower bound `mu_N=H_N-c_T.hi-rho_R.hi-sum(prime_loss_m.hi)`. Nonpositive `mu_N` is a contract failure. For an admitted pair, the verifier forms the even/odd blocks of `A-(3/mu_N)(GV+GP+GR)` and recomputes exact congruence/Gershgorin margins from the serialized exact witnesses. Production Rust `V2_ALLOWED_CONFIGURATIONS` is intentionally empty in P7: valid structure is not theorem admission. Malformed/unauthorized proof maps to contract failure; an admitted, structurally valid but nonpositive Schur proof maps to theorem failure. The verifier is zero-float exact-rational machinery, not a transcendental Arb re-prover: `log_m`, `c_m`, `c_T`, `rho_R`, and related rigorous transcendental enclosures remain outside the independent Rust trust boundary until a separate rigorous transcendental layer is added.

P7 acceptance: complete Rust verifier suite `63/63`; strict rustfmt and clippy with `-D warnings`; focused Python v2/v1 contract regression `21/21`; complete default Python suite `602/602`; retained v1 proof replay `8/8`. These checks do not alter the empty v2 theorem whitelist.

**P8 v2 adversarial/cross-layer contract — `2026-10-01T19:06:42Z`.** For the current first v2 structural window, the root JSON Schema fixes `arithmetic_terms` to exactly `[(2,2,1),(3,3,1)]` in canonical order and requires each serialized `compressed_shift_norm_bound` to be exactly `1/1`. Python semantic validation and Rust independently re-check the active set, prime-power identities, coefficient/norm/complement interval consistency, exact symmetry/parity of `A/GV/GP/GR`, and strict support-window relations from the serialized exact-rational log enclosures. The strict contract is fail-closed: lower-window validity requires `T > upper(log_3)/2`; upper-window validity requires `T < lower(log_2)=lower(log_4/2)`; equality or interval overlap is rejection. The test-only cross-layer corpus `tests/data/certificate-v2-cross-layer-v1.json` has 10 shared structural cases whose expected validity is independently checked by raw Python JSON Schema, Python semantic validation, and Rust. Cross-field threshold/parity attacks are tested separately in Python and Rust because JSON Schema has no mechanism for those rational matrix/support relations. The separate closed-grid admission corpus `tests/data/multi-prime-admission-v2.json` contains 16 forbidden support/dimension pairs and no allowed pair; the schema admission sub-contract `$defs.theoremAdmission`, Python `V2_ALLOWED_CONFIGURATIONS`, and Rust `V2_ALLOWED_CONFIGURATIONS` independently reject every grid entry. Neither test corpus is loaded by production code. A valid negative Schur proof remains theorem failure rather than malformed-contract failure. The production v2 theorem whitelist is still empty.

**P9 non-theorem qualification boundary — `2026-10-01T21:04:17Z`.** The first real qualification at `T=11/20` did not reach a proof-bearing terminal state. The original frozen grid `96..144 step 4` sealed `NO_CANDIDATE` at the floating stage. A separately predeclared extension `148..256 step 4` found the stable-positive scout frontier at `N=192` and selected rigorous targets `192,196`, but neither first 128-bit rigorous assembly completed before external execution limits of approximately 30 minutes and then one hour. Both workers remained CPU-active; no rigorous result or cache entry was committed. Therefore there is no completed P9 evidence for `GP`, `mu_N`, precision escalation, exact witnesses, candidate stability, `CANDIDATE_READY`, or reproducibility. This outcome is **NOT QUALIFIED — rigorous-stage performance blocker**, not a mathematical negative. P9 does not authorize grid extension, theorem admission, certificate generation, or any support/dimension claim. A separate performance-hardening slice is required before another qualification.

---

## 3. Computational Boundary & Division of Concerns

The repository enforces strict separation between reconnaissance tooling and proof machinery:

### 3.1 Python Environment Boundary
- **Reconnaissance & Preconditioning**: `float`, `numpy`, `scipy`, `matplotlib` are permitted *only* for heuristic plotting, condition number exploration, turning scale discovery, and basis optimization.
- **Proof & Certificate Generation**: `scripts/cert/` must rely exclusively on `python-flint` (`arb`, `acb`, `fmpq`, `arb_mat`, `fmpq_mat`). No standard floating-point operations may appear in the calculation of certificate entries.

### 3.2 Rust Environment Boundary
- **Engine / High-Throughput Exploration (`crates/rh_engine`)**: Uses optimized native routines and Rayon for fast numerical searches, turning-window sieves, and trace evaluations.
- **Trusted Verifier (`crates/rh_cert`)**: Zero-float trust base (`#![deny(clippy::float_arithmetic)]`). Rejects native C/C++ bindings (`rug`, GMP, MPFR) in favor of pure-Rust arbitrary precision integers and rationals (`num-bigint`, `num-rational`).

---

## 4. Zero Dependency-Zoo Policy

To preserve long-term auditability, reproducibility, and minimal trusted computing bases, the repository enforces a strict zero dependency-zoo policy:

1. **Prohibited Systems**:
   - **Monolithic CAS**: Adding SageMath, SymPy extensions, or Julia bridges is prohibited.
   - **Duplicate Floating/Interval Backends**: Adding alternative interval libraries or multiple overlapping arbitrary-precision packages is prohibited.
   - **Native Verifier Wrappers**: The Rust verifier must remain 100% pure Rust; native GMP/MPFR wrappers like `rug` are prohibited.
2. **Criteria for New Dependencies**:
   - Any proposed dependency must address a capability genuinely impossible with the existing stack.
   - Must not duplicate existing `python-flint`, `mpmath`, or `num-rational` capabilities.
   - Requires explicit justification in `notes/IMPROVEMENTS_LIST.md` or a dedicated architecture RFC.