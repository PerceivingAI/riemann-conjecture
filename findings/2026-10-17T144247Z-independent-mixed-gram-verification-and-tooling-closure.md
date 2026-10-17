# Independent verification and closure of the cancellation-sensitive mixed-Gram research capability

- **Finding ID:** F-20261017-010
- **Created:** 2026-10-17T14:42:47Z
- **Last updated:** 2026-10-17T14:44:16Z
- **Type:** SOURCE_VERIFIED / independent mathematical and implementation review; tooling-phase closure
- **Status:** VERIFIED for **research-side combined-Gram enclosure capability**, with explicit generator-side trust and numerical-sign limitations
- **Related research:** F-20261017-007, F-20261017-008, F-20261017-009; X-20261017-002
- **Baseline HEAD:** `a18746e437b52cdd0a3f0d4af1654df116be28de`; this review concerns the uncommitted additive research-only source and documentation
- **Scope:** Final focused review, necessary research-only boundary corrections, focused regression, comparison with measured behavior, conclusion. No new theorem or certificate admission, no v1/v2 rewrite, no new positivity experiment, and no future planning disclosure.

## 1. Result and decision

**The computational capability sought in this tooling phase has been implemented and independently reviewed, within its stated research-side trust boundary.** The separate Python/Arb implementation computes a rigorous, cancellation-sensitive finite Legendre **combined truncated image Gram**, converts entrywise Arb intervals into a valid exact rational **Loewner majorant**, and accounts for the *full* Suzuki residual through its existing operator-norm bound. It can form a conservative combined Schur lower matrix **provided \(\mu_N>0\) is independently certified**. Constructing a rational lower matrix is not a proof that this matrix is positive.

**Mathematical result remains unresolved:** Neither the research implementation nor the verification produces a new positive or negative result for the full combined Schur at the retained \(T=11/20,N=192/196\). The previous four projected obstruction tests remain INCONCLUSIVE, the old grouped factor-3 negatives remain unchanged, v2 admits no theorems, and RH remains unresolved.

This is a completion of an explicitly scoped **computational tool capability**, not a completion of the larger Weil positivity problem or a claim that a newly generated matrix has passed a closed independent verifier.

## 2. Independent mathematical-interface review

Let \(E_N=\operatorname{span}\{P_0,\ldots,P_{N-1}\}\) with ordinary, unnormalized \(P_i\), \(d_i=2/(2i+1)\), \(D_N=\operatorname{diag}(d_i)\), \(Q_N=I-\Pi_N\). On finite low Legendre inputs, \(V,P_T,R_K\) have well-defined \(L^2\) images, despite the unbounded potential \(V\). The research implementation computes
\[
 G_{K,\mathrm{coord}}
  =\bigl[\langle Q_N(V+P_T+R_K)P_i,\,
                  Q_N(V+P_T+R_K)P_j\rangle\bigr]_{ij}
  = M_{\mathrm{all}}-K_{\mathrm{all}}D_N^{-1}K_{\mathrm{all}}.
\]
Direct code inspection confirms **all nine ordered component image terms** \(VV,VP,VR_K,PV,PP,PR_K,R_KV,R_KP,R_KR_K\) and matching low-projection subtraction. In particular the ordered \(VP,VR_K,PR_K\) matrices are independently evaluated before adding their *correctly transposed* partners; they are not presumed symmetric individually. The combined signed \(P_T\) retains all active prime-power images, including \((2,3)\) cross terms, rather than splitting off an invalid per-prime square.

- **\(VP\):** Endpoint-aware antiderivatives for weighted logarithmic polynomial moments are evaluated only on rigorously certified translated support intervals. For singular endpoints \(x=\pm1\), the analytic limits replace invalid \(\log0\) products; uncertain interior logarithm domains fail closed. Active two-sided translations use the existing rigorously enclosed \(-\Lambda(m)/\sqrt m\) signs.
- **\(VR_K\):** Polynomial residual images with rational coefficients are contracted against whole-interval *exact rational grouped logarithmic moments*, adding the rigorous \(\log2\) ball only at the final step. No new unverified global \(V^2\) domain assumption is used.
- **\(PR_K\):** Shifted polynomial images are contracted with polynomial moment integrals on their correct support intervals. This is independently cross-checked by a *different* affine cell-local Legendre basis pairing at representative indices.
- **Projection, symmetry, and parity:** \(K D_N^{-1}K\) uses the correct Legendre metric. The Gram is symmetric, and opposite-parity zero entries are set exactly only after checking their calculated balls contain zero.
- **Full Suzuki residual:** If \(B=B_K+\Delta B\) and \(\|\Delta B\|\le\delta_K\), the existing proved Young inequality gives, for exact rational \(\eta>0\),
  \[
  G_{\mathrm{full,coord}}\preceq
        (1+\eta)G_{K,\mathrm{coord}}
        +(1+\eta^{-1})\delta_K^2D_N.
  \]
  Use of **\(D_N\)**, rather than an unnormalized-coordinate identity matrix, is essential.
- **Matrix-order bounds:** A symmetric rational center and nonnegative per-entry radius yield exact row-sum diagonal inflation \(G_K\preceq C+\operatorname{diag}(\sum_jr_{ij})\). This proves a *Loewner* bound; raw entrywise inequalities alone would not.
- **Full Schur lower:** With a rigorously positive lower endpoint \(\underline\mu_N>0\), the routine combines a correctly bounded \(\underline A_N\) with \(\overline G_{\mathrm{full}}\) to return \(\underline S=\underline A_N-\underline\mu_N^{-1}\overline G_{\mathrm{full}}\preceq S_{\mathrm{comb}}\). This is a conditional matrix-order computation, **not** a positivity assertion.

The underlying exact identity and Suzuki normalization were established earlier in C-0063 through C-0065, and the numerical routine is **generator-side** rather than a closed exact proof-contract verifier. Independent domain equality with Suzuki's entire canonical Friedrichs operator has not been established and is not inferred here.

## 3. Two fail-closed trust-boundary corrections made during this review

Independent source inspection found **two correctable input-validation gaps** in the new research implementation. They were not observed to falsify any previously reported legitimate test, but could permit incorrect behavior on *unvalidated caller inputs*:

1. **Young parameter was not forced to be an exact rational.** Previously `rigorous_full_gram_upper` accepted an arbitrary positive `eta` even though the proof and output require exact \(\mathbb Q\) arithmetic. An `int` or `float` argument could cause Python floating arithmetic in `1/eta`, silently violating the stated exact-rational enclosure contract. It now requires an actual `fractions.Fraction` and **strict positivity**, rejecting all floats and other types.
2. **The Loewner-enclosure helper did not validate matrix symmetry/shape.** Previously `_rational_order_bounds` read only the upper triangle without rejecting a caller-supplied contradictory lower triangle. Although the internal Gram assembler itself constructed a symmetric matrix, this exposed helper could silently treat malformed data as a symmetric Gram. It now rejects empty/non-square inputs and any mismatched off-diagonal intervals that fail to overlap. Compatible but nonidentical overlapping interval pairs remain allowed.

The changes are **research-only corrections**; they do not modify the core mathematical identities, v1/v2 contracts or admitted results. Regression controls explicitly exercise these rejection conditions.

## 4. Independent controls and actual measured comparison

**Focused updated verification:** The project-local locked command

```text
uv run --locked --extra test python -m pytest -q tests/test_mixed_gram_research.py tests/test_prime_power_terms.py tests/test_multi_prime_legendre_schur.py tests/test_multi_prime_potential_grouping.py
```

completed with **40/40 PASS** after the two input-boundary corrections, including three new controls for rejected invalid matrix shapes/asymmetry, exact rational \(\eta\) and independent nontrivial low-vector finite-tail projections. The original source-checked tests also independently exercise endpoint moment identities and parity, a separate local-Legendre \(PR_K\) representation, sampled high-precision direct \(VP\) quadrature (**nonproof**), \(\delta_K^2D_N\) residual normalization, and positive-complement gating.

**Measured precision/conditioning from X-20261017-002:** Earlier actual runs at \(T=11/20\), residual order 32 showed a catastrophic enclosure width of approximately \(1.86013\cdot10^{30}\) at \(N=128\), Arb-384, but approximately \(4.61364\cdot10^{-86}\) at the same \(N\) with Arb-768. Earlier \(N=192/196\), Arb-1024 runs attained maximum combined Gram entry widths of about \(1.51810\cdot10^{-88}\) and \(7.49414\cdot10^{-84}\), in 116.963 and 136.252 seconds. **These are earlier as-run measurements**, not re-executions of the amended source at both full target dimensions. The two changes in §3 reject unsupported input forms; they do not change numerical formulas when the validated internal arguments are used.

**A fresh after-correction reproducibility control** reran `N=64`, Arb-384, residual order 32 and obtained maximum \(G_K\) entry width **\(5.773213736205091\cdot10^{-44}\)** in **4.705 s**, matching the earlier \(5.773213736205091\cdot10^{-44}\) diagnostic value. This supports unchanged valid-input behavior at this control dimension. The completed source also passed the full focused 40-test suite.

**What is NOT established:** Any positive eigenvalue/LDL/Gershgorin result for the *new* \(N=192/196\) combined Schur lower matrices; an independently closed Rust acceptance contract for the mixed image inputs; independent Lean formalization; universal stability for other supports/orders/dimensions; independent replay of the *new source revision* at \(N=192/196\). Retained numerical width observations and mathematical derivations are separate forms of evidence. **Do not promote this research generator output to a theorem or certificate.**

## 5. Completion gate and outcome

| Requirement | Disposition |
|---|---|
| Identify the specific missing information | **MET** — cancellation-sensitive upper combined Gram, or equivalent direct Schur bound |
| Check existing primitives before new machinery | **MET** — Arb potential moments, signed translations, exact residual polynomials and rational intervals reused |
| Implement only the selected justified scope | **MET** — research-only analytic cell moments and ordered mixed image products, no new integrator/framework |
| Rigorous enclosure and normalization | **MET within generator-side analytical trust** — correct \(D_N^{-1}\), \(\delta_K^2D_N\), exact rational Loewner inflation |
| Independent controls and failure guards | **MET** — cross-representation, full/split moments, projected-tail vectors; **40/40 PASS**, two gaps corrected |
| Measured comparison of enclosure quality | **MET for tested inputs** — actual Arb widths, 384→768 precision recovery, earlier 192/196 and fresh 64 control; not universal qualification |
| Preserve frozen v1/v2 and historic evidence | **MET** — additive separate code, no changes to old claim/certificate/verifier/Lean implementations |
| Establish full combined Schur positivity or new theorem | **NOT MET / NOT A COMPLETION REQUIREMENT** |
| Build an independent closed theorem acceptance profile | **NOT IMPLEMENTED / NOT AUTHORIZED** |

**Final research-tooling disposition: COMPLETE with explicitly limited trust and no new mathematical sign result.** The intended rigorously enclosed mixed-Gram upper capability is available; future use requires a separately justified mathematical calculation and must not reinterpret generator-side enclosures as admitted theorems. No speculative orchestration, new dependency, general-purpose numerical integration framework, or alternative polynomial representation was necessary for this bounded delivery.

## Sources and reproduction

- [Necessity assessment F-20261017-007](2026-10-17T134402Z-combined-gram-computational-necessity-assessment.md).
- [Existing primitive feasibility F-20261017-008](2026-10-17T140216Z-mixed-gram-primitives-source-audit.md).
- [As-run implementation and measured evidence F-20261017-009](2026-10-17T142253Z-combined-mixed-gram-implementation-and-validation.md).
- [Original computation X-20261017-002](../computations/2026-10-17T142253Z-mixed-gram-implementation/record.md).
- [Amended independent research-only implementation](../scripts/cert/mixed_gram_research.py), [focused tests](../tests/test_mixed_gram_research.py), and [research profile](../scripts/profile_mixed_gram_research.py).
