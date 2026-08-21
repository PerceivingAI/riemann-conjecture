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

### 2.1 Mandatory Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `format` | `string` | Must be strictly `"rh-weil-certificate-v1"`. |
| `claim` | `string` | Explicit mathematical proposition being certified (e.g. `"T=7/20 residual positivity"`). |
| `support_T` | `object` | Exact rational representation of support parameter $T$ (`num`, `den`, `frac`). |
| `basis` | `object` | Basis function parameterization (`type`, `dimension`, `domain`). |
| `parity_sector`| `string` | Parity sector under verification: `"even"`, `"odd"`, or `"both"`. |
| `dimension` | `integer` | Finite block matrix dimension $N \ge 1$. |
| `constants` | `object` | Certified rational enclosures for all transcendental constants used. |
| `matrix` | `object` | Exactly $N^2$ rational interval entries with exact string numerator/denominators. |
| `tail_bound` | `object` | Formal enclosure and parameterization of infinite-dimensional remainder operators. |
| `generator_metadata` | `object` | Script name, generator version, FLINT version, precision bits, and UTC timestamp. |

### 2.2 Rational Interval Entry Semantics
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
