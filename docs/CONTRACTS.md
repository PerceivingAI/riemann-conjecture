# Repository Architecture & Proof Contracts

- **Created:** `2026-08-21T06:00:00Z`
- **Last updated:** `2026-08-27T14:37:56Z`
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
(T,N)=(19/40,68),
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

`legendre_component_gram_schur` applies only to `exact_prime_legendre_schur`. In v1, `harmonic_index` must equal the whitelisted finite dimension (`32`, `40`, `48`, `56`, or `68`) and the factor must be the exact rational `3`. The required constants are only `c2`, `c_T`, and `rho_R`; the required proof matrices are `GV`, `G2`, and `GR`. Opposite-parity entries in `A`, `GV`, `G2`, and `GR` must be exactly zero. Rust derives the lower complement constant from the upper endpoints of those scalar intervals, reconstructs the factor-3 Schur matrix, extracts its even and odd blocks, and checks the supplied exact rational lower-triangular congruence witnesses for invertibility before applying exact interval Gershgorin positivity.

The retained `C-0050` (`T=7/20,N=32`), `C-0051` (`T=2/5,N=40`), `C-0052` (`T=17/40,N=48`), `C-0053` (`T=9/20,N=56`), and `C-0054` (`T=19/40,N=68`) certificates use this rule and are proof-bearing because `C-0045`, `C-0047`, and `C-0048` provide the analytic complement and Schur semantics encoded by the profile. Each theorem-bearing pair required explicit closed-contract admission followed by a fresh independent Rust PASS; whitelist admission alone never grants theorem status. No other `(T,N)` pair is admitted.

### 2.6 Retained theorem-artifact acceptance

Proof-bearing retention is governed by the closed manifest `computations/retained-proofs.json`. Its v1 entries bind each retained theorem claim to one computation ID, repository-relative certificate path, raw-byte SHA-256, support, dimension, claim profile, and verified scope. The manifest contains exactly `C-0050` through `C-0054`; pre-theorem candidates and tooling computations are not proof registrations.

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

`tests/data/exact-prime-admission-v1.json` is therefore a **test-only expectation corpus**, not production configuration. It lists the five admitted pairs, all twenty mismatched cross-pairs formed from the admitted supports and dimensions, and selected external forbidden cases including `(T,N)=(19/40,64)` and `(19/40,72)`. Python and Rust tests independently execute the corpus against their own hard-coded admission rules, while the raw JSON Schema branch is tested separately. `docs/CONTRACTS.md` is also checked to name every admitted pair.

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
