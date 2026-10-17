# X-20261017-004 — Independent analytical-input review of the N=192 combined-Schur candidate

- **Created:** 2026-10-17T15:32:22Z
- **Last updated:** 2026-10-17T15:34:11Z
- **Type:** RESEARCH_AUDIT / independent analytical derivations, numerical source cross-controls, exact rational evidence reconciliation
- **Status:** **PASS within stated source-level/Arb trust boundary; POSITIVE_CANDIDATE retained, PRE-THEOREM**
- **Previous primary result:** [X-20261017-003](../2026-10-17T150153Z-combined-schur-bounded-test/record.md), same frozen `T=11/20,N=192, Arb-1024, K=32`. **NO new large-dimensional assembly or dimension sweep.**
- **Main finding:** [F-20261017-012](../../findings/2026-10-17T153222Z-independent-analytic-audit-positive-combined-schur.md).
- **Primary source:** Masatoshi Suzuki, *Weil's quadratic form via the screw function*, arXiv:2606.09096v3 (2026-09-23), https://arxiv.org/html/2606.09096v3, especially equations (2.2)–(2.5) and (4.4)–(4.5).
- **Baseline:** Git HEAD `a18746e437b52cdd0a3f0d4af1654df116be28de` with uncommitted SYS-3/SYS-4 additive research. The generator/witness packet fingerprints identify the actual source rather than relying on HEAD.

## 1. Independent mathematical proof checks — PASS, with explicit domain scope

The directly consulted source's scaled Rayleigh expression (4.5) has: coefficient \(-\log T-(2A_{\rm Suzuki}+1)=-\log(2\pi T)-\gamma\); the \(\frac14\) difference quotient \(J\); multiplication \(v(x)=-\frac12\log(1-x^2)\); prime-power terms \(-\Lambda(m)/\sqrt m\) acting by the TWO actual compressed translations; and full negative residual convolution \(-T r''(T(x-y))\). This agrees with `F-20261017-004` and the current `V/P/R` source signs and Jacobian. The external source formula is established on the original Sobolev admissible class; equality of the entire constructed and canonical Friedrichs-extension domains **remains not independently established**, nor is it needed for the claimed implication to the original admissible smooth test functions.

For ordinary **unnormalized** Legendre \(\ell_i\), \(d_i=2/(2i+1)\), \(\Pi_N=\sum_{i<N}\ell_i\langle\ell_i,\cdot\rangle/d_i\), exact finite-column image pairing yields
\[
  \langle Q_NW_K\ell_i,Q_NW_K\ell_j\rangle
 =\sum_{X,Y\in\{V,P,R_K\}}\langle X\ell_i,Y\ell_j\rangle
  -\left(KD_N^{-1}K\right)_{ij}.
\]
Thus all **nine ordered \(V/P/R_K\)** image pairs and mixed \(\{2,3\}\) prime powers inside the ONE signed \(P\) must be kept. The inspected source includes them; no cross term is omitted or individually symmetrized before transposition. Exact opposite-parity zeros follow from reflection invariance.

The new cell moment uses elementary primitives
\[
 F_n^-(x)=\frac{(x^{n+1}-1)\log(1-x)-\sum_{j=1}^{n+1}x^j/j}{n+1},\quad
 F_n^+(x)=\frac{(x^{n+1}-(-1)^{n+1})\log(1+x)-\sum_{j=0}^n(-1)^jx^{n-j+1}/(n-j+1)}{n+1}.
\]
Independent differentiation using integration by parts/polynomial division yields \((F_n^\pm)'=x^n\log(1\mp x)\) with the appropriate signs in the logarithms, and the singular-endpoint products have finite removable limits. Consequently
\(\int_a^b x^n[-\log(1-x^2)/2]dx=-[F_n^-(b)-F_n^-(a)+F_n^+(b)-F_n^+(a)]/2\).
These are exact analytic identities, not an appeal to quadrature. For the moving breakpoints \(a,b\), Arb's strict positivity of each log argument and certified interval topology are required and implemented; questionable endpoint balls fail closed. Direct higher-degree numerical quadrature below independently probes this formula but **is not itself a rigorous enclosure proof**.

Residual and tail: the original `C-0063..C-0065` / `F-20261017-004` analytic proof establishes \(\|R_T-R_K\|\le\delta_K\) using the Bernoulli series uniform error for \(2T<\pi\). The source `_residual_truncation_operator` uses the exact rational polynomial kernel and its tested full \(\delta_K\). Then for exact \(\eta>0\),
\(G_{\rm full}\preceq(1+\eta)G_K+(1+\eta^{-1})\delta_K^2D_N\).
This audit rechecked why **\(D_N\)** rather than an identity is mandatory in unnormalized coordinates. Similarly \(\underline A=A_K-\delta_KD_N\) is a **LOWER** matrix. Row-radius rational inflation is proved from \(|z_i z_j|\le(|z_i|^2+|z_j|^2)/2\); entrywise Arb intervals ALONE would not be a Loewner upper/lower bound.

Complement:
\[
 \mathfrak c_N[q]\ge
 (H_N-c_T-\sum_m c_m b_m-\rho_R)\|q\|^2,
\]
from \(J\) spectral orthogonality, \(V\ge0\), compressed-shift norm bounds and the full residual norm. With \(\underline\mu_N>0\), completing the square on \(Q_N\mathcal F_T\) gives
\(\underline S\preceq S_{\rm comb}=A_N-\mu_N^{-1}B^*B\).
**Strict positive exact rational \(\underline S\) therefore has the correct direction of implication.** The source formula and full-domain caveat remain as in F-20261017-004, not overstated.

## 2. Independent computation against the immutable primary rational packet

The independent control script `scripts/audit_combined_schur_analytic_inputs.py` consumes the already hashed `matrix-N192.json.gz` packet. It does **NOT** compute another `N=192` Arb mixed matrix, select a new dimension, or mutate the original witness. Its independent reference calculations are:

1. **Low A:** run existing separate `assemble_multi_prime_schur(n=12,prec=384,K=32,T=11/20)` and compare Arb intervals against *six selected entries of the saved \(N=192\) low matrix*: \((0,0),(1,1),(0,2),(2,4),(5,7),(10,10)\). **6/6 interval overlaps PASS**. The low-form entries at these indices do not depend on the requested low dimension.
2. **Complement:** the independent \(n=12\) \(\mu\) value is corrected by the EXACT harmonic difference \(H_{192}-H_{12}\) and the resulting independent interval overlaps the packet's \(\underline\mu_{192}\) interval. **PASS.** Directly comparing \(\mu_{12}\) and \(\mu_{192}\) without this adjustment would be an incorrect audit test.
3. **High-degree `VP`:** directly integrate the actual translated interval integrands with high-precision `mpmath` Legendre functions at \((i,j)=(0,96)\), both shifts for each \(m=2,3\), without calling the Arb antiderivative in the numerical reference. Versus the separate high-precision Arb cross-term calculation the absolute midpoint discrepancy is approximately `1.44222149031997457e-96`. **NONPROOF diagnostic PASS**, tolerance `1e-55`.
4. **High-degree log cell:** independently integrate \(x^{96}[-\log(1-x^2)/2]\) on the translated \(m=2\) left cell by `mpmath`, compare with the Arb elementary endpoint primitive. Midpoint discrepancy approximately `5.85209544336524791e-98`. **NONPROOF diagnostic PASS**, tolerance `1e-55`.
5. **Cross-generation full-tail inequality:** independently read the *retained* historical exact 56-bit rational trial direction \(u\) and the **previous** `M=224` rigorous finite-tail Gram LOWER datum, \(\gtrsim0.5869287369002801\). From every matching saved \(N=192\) full Gram entry interval in the NEW packet, compute the exact rational directional **UPPER** estimate with its \(\eta,\delta_K,D_N\) correction. **PASS:** new rigorous upper \(\lesssim1.1360573392146218\) exceeds the old rigorous lower. This is a necessary compatibility check, not a proof of the full Gram on all directions.
6. **Source packet integrity:** original matrix packet's SHA-256 `655d481d638f8b6fba0f95d01a4bab45079d905fbc6cb4f3e822571729d4d7c1` verified. Its frozen `T,N,K,prec,\eta`, all source SHA-256 and active terms remain unchanged.

Reproduce source control:

```text
uv run --locked python -m scripts.audit_combined_schur_analytic_inputs --output computations/2026-10-17T150153Z-combined-schur-bounded-test/data/source-audit-N192.json
```

**Exit 0; 1.512 s; source audit PASS.** The JSON file `source-audit-N192.json` has SHA-256 `0228929f8ca5d884816897e3b7624e395db0c0cf13f9ac72175e1dfadee6fa10`. Audited source file SHA-256: `3cfb8d4c22c776c6a9325c496931a42d041abf37ba4f0fef4054c5d35f2e3db3`.

**Audit-script-only fixes before PASS:** An initial reference erroneously compared \(\mu_{12}\) directly with \(\mu_{192}\); corrected by \(H_{192}-H_{12}\). A second reference mistakenly used the **sum** of the rational interval endpoints rather than their **midpoint**, creating a spurious factor of two in one *diagnostic comparison*; corrected. Neither error occurred in the original generator or witness packet. The final corrected source hash, PASS and complete output are retained, and no failed audit attempt was misrepresented as a mathematical contradiction.

## 3. Exact rational proof-layer separation and hardening

The original immutable packets remain:
- full source rational matrix `matrix-N192.json.gz`, SHA-256 `655d481d638f8b6fba0f95d01a4bab45079d905fbc6cb4f3e822571729d4d7c1`;
- full invertible dyadic congruence witness `positive-witness-N192.json.gz`, SHA-256 `d9130344b09978fe84026dff0cbe3bf54cbda4c0603828af9f36cc84a32fc48f`;
- first independent rational result `independent-exact-check-N192.json` (retained unchanged), SHA-256 `4132b23ee9017553a878887bfbc96e54db7cb0d2b8d182fb3e9c8cd8c7316e65`.

A narrow source-audit hardening changed **ONLY the research verifier** `scripts/verify_combined_schur_research.py` to fail closed if `dyadic_bits` is not the fixed canonical integer `352`, if either `mu_dyadic`/`delta_dyadic` is malformed or reverses its exact rational endpoints, or if the complete residual lower endpoint is negative. This is not a new certificate or verifier admission profile.

**With the original matrix and witness unchanged**, the hardened separate exact checker again reconstructed all rational midpoint/radius row-inflated low/Gram bounds, \(\delta_K^2D_N\) Young allowance, and \(\underline S\). It recomputed the complete **exact** \(192\times192\) congruence \(W\underline SW^{\mathsf T}\), checked every exact Gershgorin row and matched the entire original exact rational minimum margin. **Exit 0; `INDEPENDENT_EXACT_POSITIVE_CONGRUENCE_PASS`, minimum exact margin strictly positive** (display approximately `0.9999999993343024`). The new output `independent-exact-check-N192-audited.json` has SHA-256 `23f0d79fd8d54fe2890da97a2a4335821b04dfdbfc33463873bb394c1e81809c`. Hardened research verifier source SHA-256: `069a9f8d5fe22c0ad55adebfc843913630465d45a6544627afd0eb6946b70f3e`.

Adversarial fail-closed reference checks: (i) modify the serialized exact witness's claimed margin to zero and verify exact checker rejects it after full congruence recomputation; (ii) mutate `dyadic_bits` to 351 and `mu_dyadic` to reversed endpoints, updating the associated witness packet hash to avoid only triggering the checksum layer. Each corrupted input was **rejected** at the intended mathematical-parameter gate. Temporary mutated files are discarded, **not** published as new mathematical experiments.

## 4. Verdict, limits and disposition

**ANALYTICAL AUDIT RESULT: PASS with scoped research-level trust.** No counterexample to the Suzuki scaling, mixed cross images, endpoint moments, residual error, complement lower bound or exact proof directions was found. The immutable primary positive exact rational matrix proof survives separate source computations, historical projected-tail inequality compatibility, an amended independently executed rational verifier and negative-controls.

**Classification remains `POSITIVE_CANDIDATE`, PRE-THEOREM.** An exact rational Schur lower matrix has been independently certified positive relative to its source-provided Arb interval packet. Direct differentiation and prior independent analytic proof support the underlying formulas; independent higher-degree numerical quadrature is a **spot diagnostic**, not an all-entry rigorous replacement. In particular **this audit does not independently recreate all 18,528 high-dimensional Gram entries from an unrelated mathematically rigorous implementation**, or provide an independent **closed** acceptance contract for each transcendental Arb source enclosure. This trust boundary is essential and unresolved for theorem admission.

No additional full-size support/dimension/precision run, new v2 theorem, Lean formalization, Rust verification contract, whitelist change, or RH conclusion occurred. The earlier factor-3 negative conservative bound remains valid but logically distinct. Frozen v1/v2 paths and historical claims are unchanged. This audit supports moving to bounded classification/closure documentation, **not automatic theorem promotion**.
