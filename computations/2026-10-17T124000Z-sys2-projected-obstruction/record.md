# X-20261017-001 — Focused rigorous projected mixed-Schur obstruction trial

- **Created:** 2026-10-17T12:40:00Z
- **Last updated:** 2026-10-17T12:48:27Z
- **Type:** COMPUTATION (pre-theorem, no admission)
- **Status:** COMPLETED — **INCONCLUSIVE** for both targeted \(N\), not a positive/negative theorem
- **Research finding:** F-20261017-005 / C-0066
- **Repository baseline revision:** `fcf4353adaf090480b695cf089bf9f17f5ad9f04` (with uncommitted research documentation and new script)
- **Environment:** Windows, CPython 3.14, python-flint / Arb via locked `uv` project environment
- **Executed support:** `T=11/20`; only active prime powers `[2,3]`; residual order `32`
- **Precision:** Arb `384` bits; exact historical dyadic test vectors `56` bits
- **Targets:** \(N=192\) and \(N=196\); enlarged finite tail projection dimensions \(M=204\), then \(M=224\)
- **Purpose:** Seek a **rigorously negative upper bound** for one Rayleigh direction of the *new exact combined Schur sufficient criterion*, using only already implemented low-image matrix elements.

## Mathematical method and trust boundary

The formal obstruction lemma is in [F-20261017-005](../../findings/2026-10-17T124537Z-projected-mixed-schur-obstruction.md). For each retained exact low vector \(u\), take a rigorous **lower bound** on the projected full-tail norm using enlarged low-matrix cross entries:
\[
 g=\sum_{k=N}^{M-1}\frac{|\langle P_k,(V+P_T+R_K)u\rangle|^2}{d_k},\qquad
 \|Q_N(V+P_T+R_T)u\|^2
 \ge\bigl[\max(0,\sqrt g-\delta_R\|u\|)\bigr]^2.
\]
Together with the full low-block **upper** bound and the strictly positive complement \(\mu_N\), this gives an **upper** enclosure of the exact new criterion's Rayleigh value at \(u\). Only an upper endpoint **strictly below zero** would establish a mathematical rejection at that \(N\). A positive upper endpoint cannot establish the opposite sign.

The script uses `assemble_multi_prime_schur(M,require_positive_mu=False)`, which **does not** change or bypass any frozen mathematical contract. It correctly restores the `A_K` upper allowance (the assembler's `A` already subtracts \(\delta_RD\)) and re-bases \(\mu_M\) to **\(\mu_N\)** by the exact harmonic difference \(H_N-H_M\). No independent Rust verifier is claimed: evidence depends on existing Python/Arb generator-side analyticity and interval correctness.

## Reproduction commands

Run from the repository root with the locked environment:

```text
uv run --locked python -m scripts.weil_projected_mixed_schur_check --tail-dimension 204 --precision 384 --residual-order 32 --output-json computations/2026-10-17T124000Z-sys2-projected-obstruction/data/projected-M204.json
uv run --locked python -m scripts.weil_projected_mixed_schur_check --tail-dimension 224 --precision 384 --residual-order 32 --output-json computations/2026-10-17T124000Z-sys2-projected-obstruction/data/projected-M224.json
```

**Scoped script and input fingerprints:**

- `scripts/weil_projected_mixed_schur_check.py` SHA-256 `cfa899e7031f9d4e56803f7d3d55cfbb618be4384a7a0a342bb0ea22d0daa16e`.
- First run `data/projected-M204.json` SHA-256 `7772be2a187a28f38c63578ec0215ed44ef0a8fd66eae1fe3e9ec8dd5724e063`.
- Second run `data/projected-M224.json` SHA-256 `18fa768885fcab8a8e013dcc286cb33c19b29ffe3d8147d5ff0f190528a671f6`.
- Source test vectors are read directly from the historical immutable evidence ZIPs `computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase8-rayleigh-cli-N192-p384-cell-legendre.zip` and `...N196...`; the script checks dimension, support, even parity and vector length and never modifies those ZIPs.

**Run status:** both processes exited \(0\) with results written. Observed durations \(27.011\) and \(36.195\) seconds, respectively; timing does not contribute to a proof.

## Results (decimal displays)

| \(N\) | \(M\) | Certified \(\mu_N\) lower | Projected full norm-squared lower | New Schur upper Rayleigh | Rigorous conclusion |
|---:|---:|---:|---:|---:|---|
| 192 | 204 | 0.566208306786 | 0.413979913404 | +4.858448157122 | INCONCLUSIVE |
| 196 | 204 | 0.586774539056 | 0.0631292496533 | +0.785257080755 | INCONCLUSIVE |
| 192 | 224 | 0.566208306786 | 0.586928736900 | +4.552997280786 | INCONCLUSIVE |
| 196 | 224 | 0.586774539056 | 0.0967507600968 | +0.727958223689 | INCONCLUSIVE |

The two JSON files retain the Arb outward interval displays for the complement, \(\delta_R\), exact rational \(u\)-norm, the **upper** full low-form Rayleigh, projected full-tail **lower**, error allowance, and **upper** new-Schur Rayleigh. The computation's semantic interpretation relies on sign checks inside Arb, not rounding the printed decimal displays.

The enlarged projection provides a larger certified Gram lower bound and a tighter Rayleigh upper bound in both target cases. However, each final **upper** is **positive**, and none proves the sign of the actual new combined Schur Rayleigh. **No new positive or negative direction for the combined criterion was established.**

## Interpretation and validation

- Both \(\mu_N\) values are certified strictly positive; the full residual truncation is bounded by \(\delta_R\approx9.82803\cdot10^{-16}\), not set to zero.
- The retained negative witnesses of the **old** grouped factor-3 matrix are merely low vectors to probe the new criterion, not direct evidence of its sign.
- This is an actual rigorous *finite-tail projected* calculation, not a rigorous enclosure of the **full** mixed Gram; the omitted tail contribution may be substantial.
- The calculation never claims independent analytic verification of the upstream Arb kernels or Rust certificate PASS, new theorem admission, or RH.
- No source-code implementation of combined mixed image-image integrals was added. The research script is narrowly scoped to this experiment and makes no changes to production code.
- **Conclusion:** the focused obstruction test is **INCONCLUSIVE**. It neither disqualifies the new combined criterion nor establishes its positivity. The separate `F-20261017-005` finding gives the exact mathematical boundary and the full-Gram evaluability assessment.
