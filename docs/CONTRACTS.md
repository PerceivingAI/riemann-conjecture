# Repository Architecture & Proof Contracts

- **Created:** `2026-08-21T06:00:00Z`
- **Last updated:** `2026-08-21T06:00:00Z`
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
| `claim_profile` | `string` | Closed verifier profile: `synthetic_matrix` or `digamma_finite_block`. |
| `support_T` | `object` | Canonical exact rational support parameter $T$ (`num`, `den`, `frac`). |
| `basis` | `object` | Closed basis parameterization (`type`, `dimension`, `domain`). |
| `parity_sector`| `string` | Parity sector under verification: `"even"`, `"odd"`, or `"both"`. |
| `dimension` | `integer` | Finite block matrix dimension $N \ge 1$. |
| `constants` | `object` | Closed set of rational intervals required by the selected claim profile. |
| `matrix` | `object` | Exactly $N^2$ rational interval entries. |
| `tail_bound` | `object` | Closed proof rule from which Rust derives a scalar identity lower bound. |
| `generator_metadata` | `object` | Generator, script, versions, Git commit and dirty state, precision, and UTC timestamp. |

### 2.2 PASS semantics

Let $\mathcal A$ be the set of exact symmetric rational matrices represented by the serialized entry intervals. The verifier first validates every structural and cross-field invariant. It then evaluates the selected tail rule to obtain an exact rational $\lambda_{\rm tail}$ and forms
$$\mathcal A_{\rm adjusted}=\{A+\lambda_{\rm tail}I:A\in\mathcal A\}.$$
PASS means exact interval LDL proves every matrix in $\mathcal A_{\rm adjusted}$ positive definite.

For `digamma_finite_block`, the nonnegative omitted-bracket theorem extends this conclusion from the serialized partial sum to the full digamma series on the selected finite basis. It does not prove positivity on the infinite-dimensional basis complement. It therefore cannot certify `A-004`.

For `synthetic_matrix`, `exact_scalar_identity` defines the remainder exactly as $\lambda I$. This profile exists only to test verifier arithmetic. It is not an analytic proof claim.

Rust must reject the certificate before LDL if the claim profile, support, basis, parity, constants, matrix, tail witness, or provenance is invalid or inconsistent. A finite-block diagnostic must not be reported as a full-operator result.

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

### 2.5 Initial tail proof rules

Version 1 starts with two closed tail rules.

`exact_scalar_identity` defines the certified operator remainder to be exactly $\lambda I$, where $\lambda$ is an exact rational in the certificate. This rule is restricted to synthetic verifier claims. Rust adds $\lambda$ to every diagonal entry before LDL.

`nonnegative_digamma_remainder` applies only to the `digamma_partial_sum` claim profile. For
$$a_k=k+\frac14,$$
the omitted bracket is
$$B_k=\frac{1}{a_k}I-K_k,$$
where $K_k$ has kernel $e^{-2a_k|t-s|}$. Zero extension to the real line and the $L^1$ norm
$$\int_{\mathbb R}e^{-2a_k|u|}\,du=\frac1{a_k}$$
give $\langle f,K_kf\rangle\le a_k^{-1}\lVert f\rVert_2^2$. Hence every omitted $B_k$ is nonnegative and the verifier-derived tail lower bound is exactly zero. The witness contains `k_max` and `first_omitted_k`; Rust must check `first_omitted_k = k_max + 1`.

No other tail type is valid. In particular, v1 does not accept a free-form description or an asserted lower bound for an unspecified operator.

### 2.6 Locked adversarial cases

The Python and Rust validators must reject the following cases before adjusted LDL unless the row explicitly names an LDL failure:

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
