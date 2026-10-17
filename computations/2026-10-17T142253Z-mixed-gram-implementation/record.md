# X-20261017-002 — Rigorous mixed-Gram assembly, independent controls and precision measurements

- **Created:** 2026-10-17T14:22:53Z
- **Last updated:** 2026-10-17T14:44:16Z
- **Type:** COMPUTATION / source-level interval research qualification, NOT theorem acceptance
- **Status:** COMPLETE for tested enclosures; no new Schur positivity or certificate assertion
- **Finding:** F-20261017-009
- **Baseline tracked HEAD:** `a18746e437b52cdd0a3f0d4af1654df116be28de` (uncommitted research-only new files and previous SYS-3 documentation retained)
- **Environment:** Windows; locked `uv` / python-flint `0.9.0` / Arb
- **Support:** `T=11/20` with active prime powers `2,3`.
- **Residual truncation order:** `32`; full error bounded by the existing `delta_R`, not dropped.
- **Script:** `scripts/profile_mixed_gram_research.py` calls `scripts/cert/mixed_gram_research.py`. The precision `--precision` is in **bits**.

## Reproduction

```text
uv run --locked python -m scripts.profile_mixed_gram_research --dimension 32 --precision 384
uv run --locked python -m scripts.profile_mixed_gram_research --dimension 64 --precision 384
uv run --locked python -m scripts.profile_mixed_gram_research --dimension 128 --precision 384
uv run --locked python -m scripts.profile_mixed_gram_research --dimension 128 --precision 768
uv run --locked python -m scripts.profile_mixed_gram_research --dimension 192 --precision 1024
uv run --locked python -m scripts.profile_mixed_gram_research --dimension 196 --precision 1024
```

These commands compute all \(V/P/R_K\) ordered mixed image-image pairings, exact unnormalized low projection subtraction, the full matrix of outward Arb entry intervals \(G_K\), and the exact rational row-radius **Loewner majorant** \(\overline G_{\rm full}\) with the full Suzuki residual error. They print **nonproof diagnostic floats** of the maximum *exact-rational* interval width and the \((0,0)\) majorant entry. Complete matrix intervals are intentionally not serialized or called a certificate.

## Observations

| \(N\) | Bits | Time (s) | Max \(VP\) width | Max \(PR_K\) width | Max \(VR_K\) width | Max \(G_K\) width |
|---:|---:|---:|---:|---:|---:|---:|
| 32 | 384 | 0.799 | 1.08032e-80 | 4.92247e-86 | 8.51151e-115 | 2.16064e-80 |
| 64 | 384 | 4.582 | 2.88660e-44 | 3.04080e-50 | 8.51151e-115 | 5.77321e-44 |
| 128 | 384 | 31.328 | 9.30065e+29 | 9.38163e+22 | 8.51151e-115 | 1.86013e+30 |
| 128 | 768 | 32.903 | 2.30682e-86 | 2.38104e-93 | 2.16017e-230 | 4.61364e-86 |
| 192 | 1024 | 116.963 | 7.59050e-89 | 1.50701e-97 | 1.86556e-307 | 1.51810e-88 |
| 196 | 1024 | 136.252 | 3.74707e-84 | 5.47425e-93 | 1.86556e-307 | 7.49414e-84 |

The \(N=128\), Arb-384 row documents an **actual interval blow-up**. Comparing **the same implementation/input** at 384 versus 768 bits shows this is a finite-precision cancellation problem rather than an algebraic failure or a certified negative direction. Arb-1024 restores tight entries at both retained target sizes. No inference about matrix positivity or RH is made.

Representative diagonal \(G_K(0,0)\) (Arb enclosures, decimal displays) and full majorant \(\overline G_{\rm full}(0,0)\) from the two large runs:

| \(N\) | \(G_K(0,0)\) displayed | \(\overline G_{\rm full}(0,0)\) approximate |
|---:|---|---:|
| 192 | `[0.000883149566655667 +/- 2.18e-20]` | 0.0008831496192954832 |
| 196 | `[0.000869810159239016 +/- 4.54e-19]` | 0.000869810211083742 |

Here the relative allowance from fixed Young parameter \(\eta=2^{-24}\) dominates the *displayed* scalar majorant difference. The majorant applies to the **whole unnormalized coordinate Gram** as a matrix-order inequality, not just this entry.

## Control checks and scope

- New focused tests verify exact logarithmic endpoint guards, full/split moment overlap, \(V/R_K\) against separate grouped full-interval moments, \(P/R_K\) against a **different cell-local Legendre calculation**, and \(V/P\) against a **nonproof** high-precision direct-shift quadrature sample. Parity and hermitian identities, the finite-tail projection lower bound, exact rational row-radius majorant and correct \(D_N\) Suzuki allowance are also checked.
- A separate certified positive-complement example verifies construction of an exact-rational **Schur lower bound**; another test checks refusal when \(\mu_N>0\) is not established. Neither asserts the matrix is positive.
- Frozen v1/v2 Python assemblers, prior theorem admissions, certificate profiles/verifier, and source historical evidence remain unchanged.
- No new full-Schur positive/negative witness or theorem acceptance was attempted here. This is a **capability and interval-quality validation**, not a new mathematical result about the sign of \(S_{\mathrm{comb}}\).

**Focused regression result:** `uv run --locked --extra test python -m pytest -q tests/test_mixed_gram_research.py tests/test_prime_power_terms.py tests/test_multi_prime_legendre_schur.py tests/test_multi_prime_potential_grouping.py` — **37/37 PASS**, exit 0. This is a scoped new/overlap suite, not the full repository suite or independent Rust/Lean verification.

**Source file SHA-256 digests after final source/test edits:**

- `scripts/cert/mixed_gram_research.py`: `a9653e938261e827a068e49e7fabed17c581515a8547408784a18a88bf922d1d`.
- `scripts/profile_mixed_gram_research.py`: `40974bfc5baa4e033ff5fb005e5e4d88bed9c2ea4f06e0194403d60545f1b50b`.
- `tests/test_mixed_gram_research.py`: `0a3be3795bddd69d14dbb7beb3683fa4c1c23da7794d5e29f8aa19186880f2b2`.

These digests refer to files in the *present uncommitted working tree* and are not repository commit hashes.

---

## 2026-10-17T14:44:16Z — Independent post-implementation verification addendum

**This addendum supplements, and does not overwrite, the original X-20261017-002 as-run measurements and original SHA-256 fingerprints.** The source digests earlier in this record identify the previous snapshot at the original tests. The new research-only source was subsequently hardened in [F-20261017-010](../../findings/2026-10-17T144247Z-independent-mixed-gram-verification-and-tooling-closure.md):

- The exact-rational full-residual Young parameter now rejects non-`Fraction` inputs, preventing accidental float arithmetic.
- The rational Loewner helper now rejects non-square and contradictory asymmetric interval matrices rather than silently ignoring their lower triangles.

**Updated scoped test replay:** `uv run --locked --extra test python -m pytest -q tests/test_mixed_gram_research.py tests/test_prime_power_terms.py tests/test_multi_prime_legendre_schur.py tests/test_multi_prime_potential_grouping.py` — **40 passed**, exit 0. The additional tests independently check matrix validation, Young parameter exactness, and vector-specific finite Legendre tail projections.

**After-correction spot reproduction:** `uv run --locked python -m scripts.profile_mixed_gram_research --dimension 64 --precision 384` — **4.705 s**, maximum \(G_K\) entry-width diagnostic `5.773213736205091e-44`; the earlier `N=64` diagnostic width is identical. **No post-hardening 192/196 full matrix repeat was run**: the earlier 1024-bit measurements remain valid *as-run evidence* under their original source revision, not falsely relabeled as current-hash replays.

**Research-only current file fingerprints (SHA-256):**

- `scripts/cert/mixed_gram_research.py`: `61c830e808d281e9a0d61ad040f7ffaeaf42821ebf753f977887567a4fdf01f3`.
- `scripts/profile_mixed_gram_research.py`: `40974bfc5baa4e033ff5fb005e5e4d88bed9c2ea4f06e0194403d60545f1b50b`.
- `tests/test_mixed_gram_research.py`: `a88548b8787753af563bdba8a80084181542ce9c38d94037d32d021d55240ce2`.

These source corrections do not alter the valid mathematical combined-Gram formula, previously retained negative factor-3 results, production certificate semantics, or lack of new positivity finding. The report F-20261017-010 gives the precise proof/test boundary.
