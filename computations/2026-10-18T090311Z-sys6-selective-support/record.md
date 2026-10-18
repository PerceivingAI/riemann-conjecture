# SYS-6.4 — One selected two-prime support, sign of the full combined-Schur sufficient matrix

- **Computation ID:** X-20261018-005
- **Created:** 2026-10-18T09:03:11Z
- **Last updated:** 2026-10-18T09:11:52Z
- **Type:** SCOPED ARB RESEARCH INPUTS / EXACT RATIONAL NEGATIVE-DIRECTION UPPER / NO THEOREM PROMOTION
- **Status:** **COMPLETE — generator-side strict negative directional upper for the chosen sufficient criterion at T=3/5,N=192; independent exact-rational arithmetic replay PASS; no independent all-entry analytical rederivation.**
- **Research outcome:** [F-20261018-006](../../findings/2026-10-18T091152Z-sys6-selective-support-decision.md).
- **Git baseline:** `main` `97f34152929518ab8a991f7c174a7439b9b6c026`; preserve local uncommitted SYS-6.1–6.3 changes, no commit or push.
- **Runtime:** Windows CPython 3.14, locked uv, python-flint/Arb and NumPy (floating trial selection only); source file fingerprints embedded in the exact output.

## Selection and stop criterion actually used

Only **T=3/5=0.60**, \(N=192\), was investigated. This fixed T lies strictly in the first \(\{2,3\}\) prime-power window and is about \(0.050694\) above the \(3\) entry \(\tfrac12\log3\), compared with merely \(0.000694\) for admitted C-0067 at \(T=0.55\). The test therefore probes the same **combined** mechanism when the prime-3 support overlap is no longer minuscule. SYS-6.2 had already rigorously established that the conservative complement is positive at \(T=0.60,N=192\); thus failure, if found, is **not** merely \(\mu_N\le0\). No second arbitrary support, high-dimension sweep, v3 certificate export or theorem admission was authorized by this selection.

**Research question:** Does the *same* full \(V/P/R_K\) mixed-Gram Schur criterion (with the conservative \(\mu_N\) from C-0058) remain strictly positive at the existing proof dimension \(N=192\) when T grows from 0.55 to 0.60? Answer is **NO for this specific chosen sufficient bound and dimension**, conditional on the existing source-defined rigorous Arb enclosures. This says **NOTHING negative about the actual Weil form** and **DOES NOT exclude another N, a sharper complement estimate, or another decomposition**.

## Exact executed computation

```text
uv run --locked python -m scripts.weil_selective_support_probe --support 3/5 --dimension 192 --precision 1024 --output computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json
uv run --locked python -m scripts.verify_selective_support_probe --input computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json --output computations/2026-10-18T090311Z-sys6-selective-support/data/exact-recheck.json
```

- **Source assembly:** 111.555s; entire run 112.429s, exit 0; all complete \(N=192\) low and \(G_K\) source intervals constructed with Arb at **1024 bits** by the **unchanged** `assemble_truncated_mixed_gram` routine. Prime-power set exactly \(\{2,3\}\).
- **Parameters:** \(T=3/5\), \(N=192\), residual truncation order \(K=32\); exact Young \(\eta=2^{-24}\); ordinary unnormalized Legendre basis and \(D_N=\operatorname{diag}(2/(2i+1))\). Full residual restored via rigorous norm allowance \(\delta_K\), not omitted.
- **Source enclosure widths:** largest low-form Arb entry width (decimal display) \(3.4202049930888537\times10^{-237}\); largest complete truncated-Gram entry width \(1.0050677675935335\times10^{-92}\). These are **input interval widths**, not proof positivity margins.
- **Complement:** the same C-0058 conservative \(\underline\mu_{192}\) is strictly positive, decimal display **0.18491998558724346**. Its exact rational lower enclosure is retained.
- **Candidate direction:** floating eigendecomposition of the normalized approximate conservative Schur matrix proposes a direction **only**. Rounding it to exact rationals with denominator dividing \(2^{20}\) yields a nonzero **odd-parity** direction (\(96\) active Legendre coordinates), exact rational vector stored. The floating minimum eigenvalue display \(-3.123341656351557\) is **NOT** part of the proof.
- **Exact rigorous sign proof from source Arb intervals:** for this fixed rational \(u\), the full **low-form upper** was reconstructed via the truncated low form and the \(\delta_K\|u\|^2\) residual allowance. A full mixed **Gram lower** was reconstructed via reverse Young:
  \[
  \|Bu\|^2\ge(1-\eta)\|B_Ku\|^2-(\eta^{-1}-1)\delta_K^2\|u\|^2.
  \]
  After exact rational outward enclosures the displayed bound values are
  \[
  \begin{array}{rl}
  u^*A_{T,N}u&\le \overline a\approx6.407116781359653,\\
  u^*B^*Bu&\ge\underline g\approx1.762372008658217>0,\\
  \mu_{T,N}&\ge\underline\mu\approx0.18491998558724346>0,\\
  u^*(A_{T,N}-\underline\mu^{-1}B^*B)u
  &\le\overline a-\underline g/\underline\mu
  \approx\boxed{-3.1233404218545826}<0.
  \end{array}
  \]
  The **strict sign** and numerator/denominator arithmetic are exact `Fraction` comparisons against outward Arb enclosures; decimal values are displays only. The exact norm enclosure for \(u\) lies near \(1\), with strictly positive rational lower endpoint. This is a genuine negative-direction **upper bound** for the Schur sufficient matrix with **chosen** \(\underline\mu\), not a negative lower matrix, a negative underlying form, or a new theorem about RH.
- **Interpretive bound:** For this fixed \(u\) and fixed low/Gram data, \( \underline g/\overline a \approx 0.27506475514626477 \) is the complement magnitude needed before these *particular conservative scalar enclosures* cease to force a negative sign. This threshold is **not** a universal required \(\mu\), and changing N also changes A, B and the direction.

## Independent arithmetic and source-trust boundary

The distinct `scripts/verify_selective_support_probe.py` does **not** trust the saved sign flag or float eigenvalue. It verifies original source file byte hashes, the exact math-configuration identifiers, the nonzero odd-parity dyadic rational trial vector, positive norm, positive \(\underline\mu\), positive \(\underline g\), and independently recomputes the exact rational identity \(\overline a-\underline g/\underline\mu\) with a strict negative sign.

- **Exact recheck:** `PASS_EXACT_RATIONAL_ARITHMETIC_ONLY`, exit 0, negative upper \(-3.1233404218545826\) display, odd sector.
- **Focused regression checks:** `uv run --locked --extra test python -m pytest -q tests/test_selective_support_probe.py tests/test_support_scaling_scout.py tests/test_mixed_gram_research.py` → **31/31 PASS**, including spoofed sign, forged source fingerprint, altered \(\mu\), wrong support, and out-of-scope probe refusal.
- **Provenance:** source SHA-256 bindings in original JSON; no `scripts/cert/` or Rust/Lean source modified and the originally admitted v3 certificate has not been regenerated.
- **Explicit limitation:** The independent replay **does not independently rederive all Arb matrix entries**. It verifies the sign conditional on the generator-side outward interval values and their established mathematical source machinery, not an independently closed two-source 2048-bit analysis. Therefore its classification is research-level **GENERATOR_SIDE_RIGOROUS_NEGATIVE_CHOSEN_CRITERION**, not a complete independently admitted new theorem.

## Output identity

| Exact saved file | SHA-256 |
| --- | --- |
| `data/T-3-5-N192-probe.json` | `44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b` |
| `data/exact-recheck.json` | `531aa5e2b1c8f3345f351ff1860f1e5e2565ab5136af454e4cdbd3a4c881069b` |

Probe source at execution: `scripts/weil_selective_support_probe.py` SHA-256 `5386cf7d4d6f9f6952ef113927c770c969a7f05866f3c00bd12e8a737bd5297c`, with the canonical mixed-Gram and additional analytic sources separately hashed in original JSON. Subsequent independent exact recheck source `scripts/verify_selective_support_probe.py` SHA-256 `582620729710c003328aad9f42e87aa05f35b2c0fa4704ad027d73c1dd141f70`.

## Final SYS-6.4 theorem-admission decision

**NO ADDITIONAL SUPPORT ADMITTED.** This run adds meaningful *methodological* information: at a fixed larger T still within \(\{2,3\}\), the previous \(N=192\) sufficient Schur matrix is demonstrably non-positive although its high-tail complement is strictly positive, with an exact negative **odd-parity** Rayleigh-direction upper. It resolves the exact SYS-6.2 ambiguity ("mixed trace variation but no sign test") for **one selected T,N and chosen \(\mu\)**, without overstating wider failure. It does **not** show that N escalation, a sharper complement, or a different operator argument is impossible.

Given this outcome and the documented SYS-6.3 lack of an unbounded support-parameter argument, **no proof-bearing artifact, additional v3 admission, or numerical sweep was warranted** at this stage. The already admitted C-0067 and the eight frozen v1 results are untouched. This is a **scoped no-admission decision**, NOT a mathematical no-go theorem for the entire combined-Schur method, and RH remains unresolved.
