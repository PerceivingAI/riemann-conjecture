# X-20261017-007 — v3 combined-Schur research verification

- **Created:** 2026-10-17T22:24:00Z
- **Last updated:** 2026-10-17T22:43:10Z
- **Type:** Separate proof-profile implementation and exact research replay
- **Status:** **TWO-GATE RESEARCH PASS; CLEAN PROOF-BEARING REPRODUCTION NOT RUN; NO THEOREM ADMITTED**
- **Related:** [F-20261017-016](../../findings/2026-10-17T224310Z-v3-combined-schur-proof-system-implementation.md) and [F-20261017-015](../../findings/2026-10-17T220105Z-complete-independent-analytic-enclosure-closure.md).
- **Baseline HEAD:** `bae1b975abc053f6aba12972621b540110b9b2f9`, dirty with uncommitted SYS-5 research.

## Implemented contract

The distinct `rh-weil-certificate-v3` / `combined_multi_prime_legendre_schur` is fixed to exact `T=11/20,N=192,K=32,eta=2^-24`, two active prime powers `[2,3]`, ordinary unnormalized Legendre basis, two complete dyadic 352-bit rational interval upper-triangles for low form and full truncated combined Gram, positive complement, nonnegative Suzuki residual, and full invertible dyadic 48-bit congruence.

New implementation: `docs/contracts/rh-weil-certificate-v3.json`; `scripts/cert/export_combined_schur_v3.py`; `scripts/cert/export_combined_schur_v3_clean.py`; `scripts/verify_combined_schur_v3_bundle.py`; `crates/rh_cert/src/v3.rs`; narrow dispatch/CLI updates; `formal/Cert/CombinedSchur.lean`; and Python/Rust targeted negative tests.

The mathematical Schur lower matrix is
\[
 S_{\rm low}=\underline A-\underline\mu^{-1}
   ((1+\eta)\overline G_K+(1+\eta^{-1})\overline\delta^2 D_N).
\]
The first matrix is **already residual-corrected** and must not have that correction subtracted again. Independent row-radius inflation supplies the Loewner lower/upper bounds, not entrywise optimistic estimates. The full combined Gram includes all ordered mixed terms and prime-power crosses.

Rust exact verification uses a mathematically identical common-denominator **integer** matrix. With \(Q=2^{352}\), \(E=2^{24}\), \(m>0\) the complement lower dyadic numerator and \(L=\operatorname{lcm}(1,3,\dots,383)\), each Schur entry is integer numerator over \(D=2QEmL>0\). The exact 48-bit dyadic witness congruence is an integer matrix divided by \(D2^{96}\). Source and witness are proved parity-preserving, so independent exact 96-by-96 even/odd checks are mathematically equivalent to the entire 192-by-192 congruence. **The minimum exact resulting margin matches the original SYS-4 exact rational witness.**

## Real executed evidence

- Research-only certificate: `data/certificate-v3-research.json`, 4,438,067 bytes, SHA-256 `1855d3b28ba6f9e76f2bbfa459f0893e57db85d915393212664a8b48780a7ea0`. Metadata is **explicitly dirty** and historical input is not relabeled clean.
- Full actual-certificate two-gate audit: `data/two-gate-audit.json`, SHA-256 `8208aee1533fca65bd1093c063774f15f515cccc731f29585755eb64f25a6a67`.
- Gate A: independently generated rigorous **2048-bit** enclosure for all **18,528 low** + **18,528 combined Gram** entries; exact rational strong containment in the original v3 packet **37,056/37,056**. Full complement and residual intervals **both contained**. No source-input failures.
- Gate B: Rust independent exact integer-rational Schur and congruence check **PASS**; same original minimum exact rational positive margin; mathematical result `POSITIVE_RATIONAL_SCHUR_LOWER`, `theorem_admitted=false`, `analytic_inputs_independently_verified_here=false`.
- Full candidate input canonical digest `6c5afa8958cc47750290776ce3cd59cd7873a34d03d148fcfa8e90afb69aea63`.
- Focused Python v1/v2/v3/analytic tests **34/34 PASS**; complete Rust suite **73/73 PASS**; strict Rust Clippy **PASS**; rustfmt completed.
- Production `rh_cert verify --cert ...` rejects v3 (exit 2, empty v3 theorem whitelist). The clean-source producer correctly rejects this dirty working tree (exit 1). A mathematical negative one-dimensional exact Gershgorin control is correctly reported negative, not accepted as positive.
- Initial naive Rust 192-dimensional rational arithmetic ran excessively long and was stopped twice with confirmed tree cleanup; the exact integer/parity algorithm subsequently finished the same full mathematical result successfully.
- Narrow scalar Lean proof compiles using locally installed mathlib (additional complete project build result recorded only if verified).

## Trust boundary and remaining admission gates

The independent all-entry analytic check was actually **rerun on the candidate's own input**, not accepted from a self-reported generator PASS. The Rust result is a separate **zero-float exact rational** consequence of those bounds, not an independent Arb transcendental evaluation.

The clean producer is implemented to *regenerate* a fresh packet, witness and independent all-entry audit from a **clean committed** source. It has NOT been executed because this working tree contains uncommitted SYS-5.1 and SYS-5.3 code. The exact new theorem certificate, fresh clean-source proof-bearing replay, v3 production admission and retained-proof registration are **NOT complete**. SYS-5.3 therefore has a **research-verified implementation** but does not yet satisfy the strict clean-proof completion condition. No frozen v1/v2 semantics or RH status changed.
