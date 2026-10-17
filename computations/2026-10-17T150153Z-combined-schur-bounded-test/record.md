# X-20261017-003 — Bounded rigorous combined low-to-tail Schur experiment

- **Created:** 2026-10-17T15:01:53Z
- **Last updated:** 2026-10-17T15:37:41Z
- **Type:** COMPUTATION / rigorous generator-side Arb intervals plus independently rechecked exact rational matrix implications
- **Status:** **POSITIVE_CANDIDATE — PRE-THEOREM** at \((T,N)=(11/20,192)\); **NO NEW THEOREM ADMISSION**
- **Mathematical object:** The exact combined-block sufficient matrix \(S_{\mathrm{comb}}=A_N-\mu_N^{-1}B^*B\), \(B=Q_N(V+P_T+R_T)\Pi_N\) on the closed Suzuki-scaled form, with the source normalization/domain assumptions `C-0063..C-0065`.
- **Public scope:** This record discloses **executed** inputs, computations, classification, evidence and independent exact check. Decisions made before execution remain private.
- **Tracked baseline HEAD:** `a18746e437b52cdd0a3f0d4af1654df116be28de`. The research sources were **uncommitted** at execution; HEAD is **NOT** the complete source fingerprint. See SHA-256 of source and output below.
- **Environment:** Windows, locked project `uv`, CPython 3.14, python-flint 0.9.0 / Arb, NumPy 2.5.2 (floating proposal only).

## 1. Executed configuration and complete decision rule

| Parameter | Executed value |
|---|---|
| Exact support | `T=11/20` |
| First dimension | `N=192` |
| Secondary dimension | **NOT RUN** — a positive exact rational witness was independently checked at N=192; stop rule |
| Active prime powers | **Exactly [2,3]**, verified by the rigorous assembler |
| Arb precision | **1024 bits** |
| Residual truncation | **order 32**, *full* Suzuki residual restored by operator-norm allowance |
| Young parameter | Exact \(\eta=2^{-24}\), represented as `Fraction(1,2**24)` |
| Matrix coordinates | Ordinary **unnormalized** Legendre basis, \(D_N=\operatorname{diag}(2/(2i+1))\) |
| Rational input enclosure | **352-bit outward dyadic** intervals, including complete low-form and combined truncated Gram |
| Enclosure quality gate | Absolute max entry width \( \le 2^{-128}\); **PASS** |
| Positive-definiteness proof | Exact rational lower Schur matrix; invertible rational congruence; strictly positive exact Gershgorin margins |
| Theorem admission | **PROHIBITED; NOT ATTEMPTED** |

The implemented generator-side analytical inequalities are, in unnormalized Legendre coordinates:
\[
G_K=\sum_{X,Y\in\{V,P,R_K\}}M_{XY}-KD_N^{-1}K,
\quad G_{\mathrm{full}}\preceq(1+\eta)G_K+(1+\eta^{-1})\delta_K^2D_N,
\]
and \(\underline A_N=A_{N,K}-\delta_KD_N\preceq A_{N,\mathrm{full}}\). The exact rational interval center plus row-radius inflation yields
\(\overline G_{\mathrm{full}}\succeq G_{\mathrm{full}}\) and
\(\underline A\preceq A_{\mathrm{full}}\). With rigorously certified \(\underline\mu_N>0\), the **actual criterion** satisfies
\[
\boxed{
\underline S=\underline A-\underline\mu_N^{-1}\overline G_{\mathrm{full}}
\preceq
S_{\mathrm{comb}}.
}
\]
The positive-definiteness claim below is a statement about **this complete, conservatively bounded \(\underline S\)**, not about a matrix that neglects its residual, any mixed term, the metric \(D_N\), or the complement. The analytic validity of the upstream Arb enclosures remains a separately documented generator-side proof obligation; exact arithmetic independently checked below does **not** reconstruct every transcendental input from first principles.

## 2. Controls and recorded execution

**Before the new full-size experiment:**

1. Scoped test command:
   `uv run --locked --extra test python -m pytest -q tests/test_one_prime_v1_freeze.py tests/test_mixed_gram_research.py tests/test_prime_power_terms.py tests/test_multi_prime_legendre_schur.py tests/test_multi_prime_potential_grouping.py` — **44/44 PASS**. This includes the unchanged retained v1 theorem-identity/admission-grid guard, independent low-degree mixed-image controls and generic prime-power overlap.
2. Retained one-prime reference on new research assembler: `T=7/20,N=32,prec=384,K=32` produced **exactly [2]** active, certified \(\mu_{32}>0\) (lower approximately `0.8709101235096008`), and a well-defined full-residual conservative combined Schur lower matrix. The old registered proof was **not edited or regenerated**.
3. The existing `C-0063..C-0065` form, full-residual and mixed-Gram identities were inspected; no prior SYS-2 claim was changed.

**Full-size executable command:**

```text
uv run --locked python -m scripts.run_combined_schur_experiment --dimension 192 --precision 1024 --output computations/2026-10-17T150153Z-combined-schur-bounded-test/data/matrix-N192.json.gz
```

**Execution result:** Exit **0**, **114.83 s** total, with actual Arb core assembly **114.242 s**. Strict positive complement: \(\underline\mu_{192}\) decimal display `0.5662083067859621`. Rigorous full-residual upper allowance \(\overline\delta_K\) decimal display `9.828028288169228e-16`. The **maximum low A dyadic enclosure width** was `1/2^352`; maximum combined truncated Gram entry dyadic width `1392703803551121409/2^352` (about \(1.52\cdot 10^{-88}\)). Both pass \(\max\mathrm{width}\le2^{-128}\) **as exact rational comparisons**, not by float rounding.

The `matrix-N192.json.gz` packet contains **every upper-triangular** low A and combined \(G_K\) entry's outward 352-bit dyadic bounds (all 18,528 entries per matrix), the rigorous \(\mu_N\) and \(\delta_K\) dyadic bounds, active terms, normalization, precision, Young parameter, and the running source SHA-256 inputs. It is a full re-evaluable exact rational input packet, **not just a width profile**, and is not a v1/v2 certificate.

## 3. Sign test and exact rational witness

Initial rational-packet inspection:
```text
uv run --locked python -m scripts.inspect_combined_schur_packet --packet computations/2026-10-17T150153Z-combined-schur-bounded-test/data/matrix-N192.json.gz --output computations/2026-10-17T150153Z-combined-schur-bounded-test/data/trial-N192.json
```
reported **unverified floating diagnostics only**: minimum eigenvalue of the conservatively bounded \(\underline S\) approximately **\(3.62626260596458\cdot10^{-8}\)**, and midpoint analog approximately **\(3.6262626259090595\cdot10^{-8}\)**. The independent exact direction upper Rayleigh evaluated on a rounded float-proposed trial direction was **positive** \(\approx3.626309962332175\cdot10^{-8}\), hence **not** a negative witness. **No mathematical positivity claim comes from either float eigenvalue or that positive upper bound.**

A first native fraction-free exact LDL *witness-construction method* was terminated after **149.452 s** without result; this was an **algorithmic cost** of one witness *construction method*, not any contradictory mathematical evidence. Portus confirmed full process-tree termination and **zero descendants remaining**. A separate narrow construction, using float Cholesky **only to propose a lower-triangular transform**, rounded it to exact dyadic denominator \(2^{48}\), then calculated its **full rational congruence** and strict Gershgorin bounds using native fmpq matrices. This approach is mathematically justified because **an arbitrary invertible exact rational transform with a strictly positive exact congruence is sufficient**; the proposed transform need not itself be created by exact LDL.

Executable generator-side witness command:
```text
uv run --locked python -m scripts.prove_combined_schur_fast --packet computations/2026-10-17T150153Z-combined-schur-bounded-test/data/matrix-N192.json.gz --output computations/2026-10-17T150153Z-combined-schur-bounded-test/data/positive-witness-N192.json.gz --witness-bits 48
```

**Exit 0**, native exact congruence/Gershgorin computation completed in **1.495 s**. The *exact rational* minimum Gershgorin margin is retained as its complete numerator/denominator in the compressed `positive-witness-N192.json.gz` packet, with the complete invertible \(192\times192\) dyadic triangular witness. The margin is **strictly positive**; its displayed decimal approximation is **`0.9999999993343024`**. The float-only proposal margin is evidence of candidate selection, **not** proof; the exact rational congruence verifies the result.

**Independently rechecked rational consequences:**

```text
uv run --locked python -m scripts.verify_combined_schur_research --packet computations/2026-10-17T150153Z-combined-schur-bounded-test/data/matrix-N192.json.gz --proof computations/2026-10-17T150153Z-combined-schur-bounded-test/data/positive-witness-N192.json.gz --output computations/2026-10-17T150153Z-combined-schur-bounded-test/data/independent-exact-check-N192.json
```

The *separate checker* ignores the generator's boolean/float conclusions and reconstructs from **exact integer dyadic endpoint inputs**: the symmetric low A and \(G_K\) interval midpoint/radius matrices, independent row-radius matrix-order inflation, the full Suzuki residual \((1+\eta^{-1})\delta_K^2D_N\), the complement \(\underline\mu_N\), and exact Schur \(\underline S\). It reconstructs \(W\) from witness dyadic integers, checks lower triangularity/nonzero diagonal, forms \(W\underline SW^{\mathsf T}\) using native exact rational arithmetic, computes every Gershgorin margin, checks all are strictly positive, and requires its computed exact margin to **match** the serialized witness margin.

**Exit 0 — `INDEPENDENT_EXACT_POSITIVE_CONGRUENCE_PASS`**, elapsed **1.296 s**; identical rigorously positive exact margin (decimal display `0.9999999993343024`).

An initial checker invocation failed immediately on a **Python interop type error** converting `flint.fmpq` to `fractions.Fraction`; the checker was narrowly corrected to extract explicit exact numerator/denominator. The corrected checker replay passed; there was **no failed mathematical inequality** and the input/witness packet hashes were unchanged.

**Result:** The rational conservatively bounded \(\underline S\) has been independently verified strictly positive definite. Given the previously proved analytic operator and matrix-order enclosures, this is a valid **POSITIVE_CANDIDATE** in the explicitly limited generator-side/pre-theorem trust layer. It is **NOT** theorem admission or proof of RH.

## 4. Artifact fingerprints and independent reproducibility

All listed files exist under `data/` and must be SHA-256 matched before reuse:

| Exact artifact | SHA-256 |
|---|---|
| `matrix-N192.json.gz` (complete rational input packet) | `655d481d638f8b6fba0f95d01a4bab45079d905fbc6cb4f3e822571729d4d7c1` |
| `trial-N192.json` (nonproof float diagnostic and exact-direction upper) | `d792ca1bc31dfdea0d5a2d00e7a1db3fb2a2090c292c2af857d3a89c70e20afc` |
| `positive-witness-N192.json.gz` (full exact rational congruence) | `d9130344b09978fe84026dff0cbe3bf54cbda4c0603828af9f36cc84a32fc48f` |
| `independent-exact-check-N192.json` (separate verified rational outcome) | `4132b23ee9017553a878887bfbc96e54db7cb0d2b8d182fb3e9c8cd8c7316e65` |

The complete rational source packet records the exact SHA-256 hashes **at generator execution**:
- `scripts/cert/mixed_gram_research.py`: `61c830e808d281e9a0d61ad040f7ffaeaf42821ebf753f977887567a4fdf01f3`
- `scripts/run_combined_schur_experiment.py`: `d1f21f3e4f10e0768b1707e8756d52a2969a67829b7a207ee26d335950d45e15`
- `scripts/profile_mixed_gram_research.py`: `40974bfc5baa4e033ff5fb005e5e4d88bed9c2ea4f06e0194403d60545f1b50b`
- `tests/test_mixed_gram_research.py`: `a88548b8787753af563bdba8a80084181542ce9c38d94037d32d021d55240ce2`
- `scripts/weil_projected_mixed_schur_check.py`: `cfa899e7031f9d4e56803f7d3d55cfbb618be4384a7a0a342bb0ea22d0daa16e`

The witness and independent checker source are **additional**, separately finger-printed in the repository at verification. The checker operates on a complete packet, not on an asserted generator sign.



**Final bounded-run source inventory (SHA-256; these scripts are research-only):**

- `scripts/run_combined_schur_experiment.py`: `d1f21f3e4f10e0768b1707e8756d52a2969a67829b7a207ee26d335950d45e15` (recorded in matrix input packet).
- `scripts/inspect_combined_schur_packet.py`: `7db4f1256389e977d2c2ba33c958239a97f9ac69e1400d56d230695486212197`.
- `scripts/prove_combined_schur_fast.py`: `78469b3523b07541d4911ba13db86f86098a12cb5899124c886764b9850c41a0`.
- `scripts/verify_combined_schur_research.py`: `a9c5cca07c493b7c32cb07f71893785881a9e235f00203f9b203ad7c0fc349c7`.

The superseded high-cost exact-LDL generator *prototype* was removed from the live research tree after its explicitly recorded terminated run; the existing canonical exact witness library remains unchanged. The successful alternative is **not** a floating proof: only its rounded candidate uses floats, and the exact native rational congruence is independently recalculated. None of these research scripts edits the frozen v1/v2 theorem contracts.
## 5. Bounded completion and interpretation

- **Positive candidate sign criterion:** **MET** for exact rational lower Schur and independently computed exact congruence with strictly positive margins.
- **Mathematical source validity:** conditional on previously justified Suzuki normalization, closed form domain, analytic mixed-image integrals and Arb enclosure correctness. The exact checker validates rational consequences; it does **not** independently reprove the transcendental source inputs.
- **Numerical uncertainty:** NOT the explanation for the result; exact dyadic intervals pass the pre-set width gate. The generator proof packet is robust under the prescribed \(\eta,\delta_K,\mu_N\).
- **Negative criterion:** NOT claimed. The earlier grouped factor-3 negative witnesses are for a different sufficient matrix, and the current directional upper trial is positive.
- **Stop:** **N=196 NOT EXECUTED**, as required after independent exact rational positive result at primary N=192. No support/dimension grid, precision escalation, new certificate format, Rust/Lean verifier, theorem admission or RH conclusion.
- **Operational:** The expensive unsuccessful *witness-construction method* was terminated with verified process-tree cleanup; the successful exact witness and independent checker completed normally. **Final session inventory at 2026-10-17T15:15:32Z confirmed zero active/queued project execution sessions.** The specifically terminated exact-LDL prototype session reported `processTreeKillSucceeded=true`, `reaped=true`, `descendantsRemaining=0`, and `terminationVerification=confirmed_absent`.
- **Final classification for this experiment:** `POSITIVE_CANDIDATE`, **PRE-THEOREM / GENERATOR-SIDE ANALYTICAL INPUTS**.
- **Next trust gate:** A separate independent mathematical/source audit of the new analytic bound and source packet, as opposed to simply repeating exact rational checking. Do not promote without a closed, separately authorized proof contract.

This experiment is a rigorous finite-support research **candidate** for the named combined sufficient criterion, not a formalized theorem or RH proof.

---

## 2026-10-17T15:34:11Z — Separate analytical-input/source verification addendum

[Independent analytical review F-20261017-012](../../findings/2026-10-17T153222Z-independent-analytic-audit-positive-combined-schur.md) / [X-20261017-004](../2026-10-17T153222Z-analytic-source-review/record.md) audited the existing, **unchanged** full \(N=192\) rational packet and positive congruence against Suzuki's primary scaled source expression, direct high-degree cell quadrature, six separate low-block references, independently adjusted full-tail complement, and the historical rigorous finite-tail Gram lower bound. No contradictory analytical computation was found. A narrow additional input-validation hardening of the **research-only independent exact checker** rejected malformed dyadic/\(\mu,\delta\) interval packets and then reconfirmed the full strict positive exact rational Gershgorin matrix claim, without changing the original packet or witness.

**Addendum artifacts** in this same `data/` directory:
- `source-audit-N192.json` SHA-256 `0228929f8ca5d884816897e3b7624e395db0c0cf13f9ac72175e1dfadee6fa10`;
- `independent-exact-check-N192-audited.json` SHA-256 `23f0d79fd8d54fe2890da97a2a4335821b04dfdbfc33463873bb394c1e81809c`.

Current audit-only source SHA-256: `scripts/audit_combined_schur_analytic_inputs.py` `3cfb8d4c22c776c6a9325c496931a42d041abf37ba4f0fef4054c5d35f2e3db3`; hardened exact checker `scripts/verify_combined_schur_research.py` `069a9f8d5fe22c0ad55adebfc843913630465d45a6544627afd0eb6946b70f3e`. The original source and artifact SHA-256 records above remain historical **as-executed** evidence, not retrospectively rewritten.

**Trust limit unchanged:** the independent checker proves exact rational matrix consequences of the provided analytically justified Arb enclosures, while the new analytic spot checks do not amount to an independently closed all-entry transcendental verification. The status remains `POSITIVE_CANDIDATE`, PRE-THEOREM; no theorem or RH result.

---

## 2026-10-17T15:37:41Z — Final bounded experiment classification and closure

The previously executed \(T=11/20,N=192\) computation is **classified and CLOSED** as `POSITIVE_CANDIDATE` — **PRE-THEOREM**, as documented by [`F-20261017-013`](../../findings/2026-10-17T153741Z-bounded-combined-schur-experiment-closure.md). The complete original rational input packet, exact congruence witness and independently checked positive margin remain unchanged. The additional independently executed source audit [`X-20261017-004`](../2026-10-17T153222Z-analytic-source-review/record.md) found no source-form, scaling, mixed image, residual or historical projection contradiction within its documented scope.

The experimental stop rule was honored: **no \(N=196\) experiment or other support/dimension sweep occurred** after positive rational verification at \(N=192\). The result shows strict positivity of the conservative rational lower Schur matrix **given the documented source-Arb enclosures**; it is not an accepted theorem because a separately closed, all-entry independent analytical input acceptance has not been established. The established distinction between the constructed closed form and unproved canonical source operator-domain equality is preserved. No changes to frozen one-prime v1 theorems, generic multi-prime v2 admission, exact certificate acceptance profiles, Rust/Lean theorem machinery, or RH status occurred.

The final classification closes this one experimental run without authorizing any additional mathematical or implementation campaign.
