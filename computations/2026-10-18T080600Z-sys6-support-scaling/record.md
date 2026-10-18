# SYS-6.2 — Bounded support scaling and combined-Gram reconnaissance

- **Computation ID:** X-20261018-004
- **Created:** 2026-10-18T08:06:00Z
- **Last updated:** 2026-10-18T08:21:04Z
- **Type:** CERTIFIED ARB SCALAR-COMPLEMENT RECONNAISSANCE + RESEARCH-ONLY COMBINED-GRAM DIAGNOSTICS
- **Status:** COMPLETE FOR SELECTED SUPPORTS; NO NEW FINITE-SUPPORT THEOREM OR SCHUR POSITIVITY VERDICT
- **Mathematical reference:** F-20261018-004, C-0058, C-0063..C-0068; fixed source certificate C-0067 is unchanged.
- **Codebase baseline:** `97f34152929518ab8a991f7c174a7439b9b6c026`, on `main`; earlier uncommitted SYS-6.1 documents preserved. This research adds only separate scripts, tests and results.
- **Runtime:** Windows, CPython 3.14.0, locked `uv`, python-flint 0.9.0 / Arb; no additional dependency.

## Objective and strictly separated evidence

Measure **actual support dependence** of the conservative full-tail complement and of rigorous truncated mixed-image Gram input enclosures, without assuming every such bound is a positivity certificate. Analyze a minimal selected set crossing an arithmetic threshold, and distinguish a failed sufficient inequality from negativity of the Weil form. No production v1/v2/v3 code, certified original mathematical source or theorem admission was modified.

**Research-only, exact scalar gate:** `scripts/weil_support_scaling_scout.py` uses Arb-256 enclosures with the current \(K=32\) Suzuki absolute-series residual norm \(\rho_R(T)\), certified exact active prime-power set and compressed-shift norm \(\|S_m(T)\|\), exact rational harmonic number \(H_N\), and the existing exact source rule
\[
\mu_N(T)=H_N-\left[\log(2\pi T)+\gamma+
\sum_{\log m<2T}{\Lambda(m)\over\sqrt m}\|S_m(T)\|+\rho_R(T)\right].
\]
The Python `Fraction` cutoff search finds the **first integer** \(N\) with \(H_N>\overline C(T)\), where \(\overline C(T)\) is an Arb-to-rational outward *upper enclosure* of the scalar cost. This is a *valid sufficient tail-complement criterion*, not a lower bound on the dimension needed for the true form to be positive. Reported decimal endpoints are diagnostic displays; proof-relevant scalar lower/upper rational endpoints remain serialized in `data/scalar-budget.json`.

**Research-only full truncated combined-image Gram:** `scripts/weil_combined_scaling_profile.py` calls the **unchanged canonical** `assemble_truncated_mixed_gram`, which computes all mixed \(V/P/R_K\) images with Arb and the correct low projection. It assesses \(G_K\) entry interval widths, exact selected support/terms, full-residual norm allowance \(\delta_K\), and **approximate displays** of normalized trace \(\sum_iG_{K,ii}/d_i\). The signed mixed correction on the same low subspace is computed using
\[
\mathcal C_{XY,ii}=2\left(M_{XY,ii}-\sum_{k<N}K_{X,ik}K_{Y,ki}/d_k\right)
\quad (XY\in\{VP,VR_K,PR_K\});
\]
its sum over \(i\), weighted by \(d_i^{-1}\), yields the displayed combined-minus-separate trace. Because these are *traces of truncated-source Gram matrices*, not spectral extremal inequalities, they can change sign and do **not** certify Schur positivity or a global mixed-term cancellation factor. Opposite parity, unbounded \(V\) and full Suzuki remainder handling remain as in the original source.

## Executed, reproducible commands

```text
uv run --locked python -m scripts.weil_support_scaling_scout --output-json computations/2026-10-18T080600Z-sys6-support-scaling/data/scalar-budget.json
uv run --locked python -m scripts.weil_combined_scaling_profile --output-json computations/2026-10-18T080600Z-sys6-support-scaling/data/mixed-n64.json
uv run --locked python -m scripts.weil_combined_scaling_profile --precision 256 --output-json computations/2026-10-18T080600Z-sys6-support-scaling/data/mixed-n64-p256.json
uv run --locked python -m scripts.weil_combined_scaling_profile --supports 11/20,3/5 --dimension 128 --precision 768 --output-json computations/2026-10-18T080600Z-sys6-support-scaling/data/mixed-n128-p768.json
uv run --locked --extra test python -m pytest -q tests/test_support_scaling_scout.py
```

Every experiment output is JSON and includes mathematical metadata; no heavy raw matrix output was committed. `N=64,128` below are **Gram-image diagnostics dimensions**, not admitted Legendre theorem cutoffs.

## Results A — Rigorous complement pressure (Arb-256, K=32)

| T | Active prime powers | c_T upper (~) | rho_R upper (~) | Full scalar cost upper (~) | Smallest N with certified positive conservative mu |
| --- | --- | ---: | ---: | ---: | ---: |
| 11/20 = 0.55 | [2,3] | 1.817256 | 2.329436 | 5.271105 | **109** |
| 3/5 = 0.60 | [2,3] | 1.904267 | 2.623713 | 5.652393 | **160** |
| 13/20 = 0.65 | [2,3] | 1.984310 | 2.939959 | 6.048682 | **238** |
| 69/100 = 0.69 | [2,3] | 2.044029 | 3.210235 | 6.378677 | **331** |
| 7/10 = 0.70 | [2,3,4] | 2.058418 | 3.280356 | 7.012779 | **624** |

**Exact sign controls:** The lower cutoff \(N-1\) has rigorously *negative* computed conservative \(\mu\), while the displayed minimum \(N\) has rigorously *positive* computed \(\mu\) for every row. These negative bounds prove **only failure of this conservative complement formula**, not a negative direction of the true high tail. The change from [2,3] to [2,3,4] occurs strictly after \(T=\log2\); at 0.70 the \(m=2\) shift norm has risen from 1 to \(\sqrt2\) and the \(m=4\) term contributes. At \(N=192\), rigorous complement values are approximately \(0.5662083\) at \(0.55\), \(0.1849200\) at \(0.60\), and \(-0.2113689\) at \(0.65\). At \((T,N)=(0.55,192)\) the first value independently matches the archived C-0067 mathematical proof scalar.

**Source of cost:** The prime loss \(c_2+c_3\approx1.124413\) stays constant within the first two-prime interval; the difference in scalar cost from 0.55 to 0.65 is mainly the increasing *absolute-bound* Suzuki residual \(\rho_R\) (2.3294 to 2.9400) and the scalar \(c_T\). At 0.70 a new arithmetic term and the m=2 path-length transition incur an additional step. Since \(H_N\sim\log N+\gamma\), positive \(\mu_N\) alone forces a cutoff on the approximate scale \(\exp(C(T)-\gamma)\) **for this sufficient estimate**, with no demonstrated numerical or mathematical scaling law for the full combined Schur matrix.

## Results B — Rigorous source enclosures / research-only mixed-trace comparison

| T | Gram N | Arb bits | Assembly seconds | Max Arb Gram entry width (~) | Mixed cross trace (~) | Combined / separate trace (~) | Rigorous mu positive at this N? |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.55 | 64 | 384 | 4.785 | 5.7732e-44 | +0.111808 | 1.015375 | NO |
| 0.60 | 64 | 384 | 4.407 | 6.0848e-46 | -0.072120 | 0.993410 | NO |
| 0.65 | 64 | 384 | 4.602 | 2.3795e-47 | -0.139747 | 0.988739 | NO |
| 0.55 | 128 | 768 | 33.567 | 4.6136e-86 | +0.069069 | 1.005441 | YES |
| 0.60 | 128 | 768 | 32.406 | 7.8508e-89 | +0.011122 | 1.000555 | NO |

The **mixed trace changes sign** across the displayed \(N=64\) supports. Small average trace effects **do not** imply negligible mixed corrections in the *smallest-eigenvector direction*, which controls the criterion. The old factor-three separation additionally inflates the entire separated Gram by 3; a near-unit trace ratio does **not** justify dropping any mixed term. At \(T=0.60,N=128\), tight Arb Gram intervals exist, but \(\mu_N\) is independently rigorously negative for the current complement bound, so **the Schur criterion is not applicable at that dimension**.

**Precision conditioning control:** At the *same* \(N=64,T=0.55\), Arb-256 yields max Gram interval width \(1.9599\cdot10^{-5}\), while Arb-384 yields \(5.7732\cdot10^{-44}\) with consistent displayed trace to the limited digit precision of the latter. At \(T=0.60\), Arb-256 width \(\approx1.9817\cdot10^{-7}\) versus Arb-384 \(\approx6.0848\cdot10^{-46}\). This is loss of enclosure sharpness under cancellation, **not mathematical negativity**. Prior measured \(N=128,\) Arb-384 at 0.55 had width \(1.86013\cdot10^{30}\); repeating at Arb-768 gave \(4.61364\cdot10^{-86}\) (`X-20261017-002`), and the present 768-bit re-execution independently reproduces that latter scale. At \(N=192,T=0.55\), SYS-5 required 1024-bit analytical generation and 2048-bit independent source acceptance. The current runs **do not** establish an optimal-bit or runtime-vs-support law.

**Full Suzuki residual:** The same \(K=32\) bounded norm remainder display \(\delta_K\) grows from \(9.8280\cdot10^{-16}\) at 0.55 to \(1.9911\cdot10^{-14}\) at 0.60 and \(3.1913\cdot10^{-13}\) at 0.65. The full residual is not ignored: it is separately bounded by the unchanged correct \((1+\eta^{-1})\delta_K^2D_N\) Young allowance, with \(\eta>0\). These diagnostic truncated-image traces are **not** the full residual-corrected Schur spectrum.

## Exact JSON files and recorded hashes

| Data file | SHA-256 |
| --- | --- |
| `data/scalar-budget.json` | `b82cbb769ccb6e681a6a69d3dc7ce5dc8d42f3f7ed0524c7c2e40da732ada02f` |
| `data/mixed-n64.json` | `568cdce587c2b91237eedb796e45c41e057a9b1462dd20fdd21696c05814efe1` |
| `data/mixed-n64-p256.json` | `30cafce1ef6201b4629193307c63089d4b29161141c87d562b161fa028faca3b` |
| `data/mixed-n128-p768.json` | `b79ac6f360cc034708a7858a14b2c79c6788094cf14eedf99eb96f8294ac1510` |

The probe source SHAs were `b70c544df93335dadbb8e3949bbead72dd77f9fe623adfbf4cb8c5c36279a851` (scalar) and `6ebbde4006996dd7019992f21d43a8e6fc406f4c7496415b40744031d7c7d67f` (combined). The *existing proof-bearing source modules* have NOT been changed, preserving original v3 source SHA bindings.

## Independent controls and limitations

`uv run --locked --extra test python -m pytest -q tests/test_support_scaling_scout.py` **6/6 PASS**. Tests enforce support activation [2,3] versus [2,3,4], reproduce the complement cutoffs [109,160,238,624] from exact rational sign inequalities, check archived C-0067 \(\mu_{192}\), reject invalid research profile ranges and check the truncated image Gram mixed-trace decomposition. Focused tests do **not** independently rederive all source transcendental matrix entries; existing SYS-5 full input acceptance remains specific to the admitted \(T=11/20,N=192\).

**Not investigated by these runs:** any sign of the **full** infinite-tail combined Schur matrix at a chosen \(T>11/20\), a new certified positivity margin, a proof of a dimension function \(N(T)\), a quantitative support-neighborhood radius, or uniform all-support control. The modest \(N=64/128\) Gram profiles do not refute positivity; some lack \(\mu_N>0\) altogether. Diagnostic traces and timings are not theorem evidence.

## Disposition

The *current conservative tail-complement rule* experiences an unequivocal dimension/cost escalation with support and a sharp arithmetic-step increase on entering \(m=4\). Gram enclosure conditioning adds an independent, potentially substantial numerical cost; rigorous generation is **possible at the tested lower dimensions**, but no support-scaled general positivity certificate has been obtained. **Increasing \(N\) can restore this specific \(\mu_N>0\) gate at every tested support, but does not by itself establish the full combined-Schur sign.**

**SYS-6.2 classification:** **CONDITIONALLY EXTENSIBLE / MATHEMATICALLY UNDETERMINED FOR LARGER SUPPORTS.** No structural impossibility theorem for the combined-Schur method or negative Weil direction has been found. The bounded evidence does **not justify a mass rollout of isolated certificates** or the claim that positive Gram matrices at additional supports would prove RH. SYS-6.2 is a closed *scaling investigation*, not an all-support proof and not an instruction to publish private roadmap details.

## 2026-10-18T08:21:04Z — Post-record focused cross-layer regression

Rechecked the final research source with the **five** support cutoffs (including the `T=69/100` strict predecessor/successor sign control) and the existing full mixed-Gram research test file:

```text
uv run --locked --extra test python -m pytest -q tests/test_support_scaling_scout.py tests/test_mixed_gram_research.py
```

**21/21 PASS**, exit 0. `git diff --check` PASS (routine CRLF conversion warnings only). No production `rh_cert` or Lean source changed; no remaining active Python/`rh_cert` research processes. Earlier separately tested 6/6 new support-scaling controls remains the narrower initial result. Final strict first-complement-cutoff vector is `[109,160,238,331,624]`.
