# SYS-6.5 — Support continuation: final evidence classification and research decision

- **Finding ID:** F-20261018-007
- **Created:** 2026-10-18T09:24:56Z
- **Last updated:** 2026-10-18T09:24:56Z
- **Type:** FINAL SYS-6 RESEARCH SYNTHESIS / METHODOLOGICAL CONTINUATION STOP DECISION
- **Status:** **VERIFIED SCOPE-BOUND ASSESSMENT — SYS-6.1–6.5 COMPLETE; UNRESTRICTED WEIL POSITIVITY OPEN**
- **Baseline:** `main` `97f34152929518ab8a991f7c174a7439b9b6c026`; pending SYS-6.1–6.4 work in the local working tree remains uncommitted and is preserved.
- **Evidence:** [F-20261018-003](2026-10-18T075359Z-sys6-support-baseline.md), [F-20261018-004](2026-10-18T081419Z-sys6-support-scaling-analysis.md), [F-20261018-005](2026-10-18T084633Z-sys6-global-support-obligation.md), [F-20261018-006](2026-10-18T091152Z-sys6-selective-support-decision.md); exact run records [X-20261018-004](../computations/2026-10-18T080600Z-sys6-support-scaling/record.md), [X-20261018-005](../computations/2026-10-18T090311Z-sys6-selective-support/record.md), and independently retained original [X-20261018-003](../computations/2026-10-18T071550Z-v3-retained-admission/record.md).
- **Claims/trust:** C-0063–C-0069, C-0071; open C-0070. Suzuki arXiv 2606.09096v3 (R-0028 / EXT-0002) is an attributed **external** mathematical source; Arb numerical enclosure and independently exact rational acceptance are distinct verification layers.
- **Admissions unchanged:** eight frozen one-prime v1 C-0050–C-0057, zero v2, one v3 C-0067 at \((T,N)=(11/20,192)\). **RH remains unresolved.**

## 1. Completion of the precise SYS-6 question

SYS-6 asked whether the successful intermediate combined-Schur criterion generalizes and, separately, whether a plausible **mathematically justified** path exists from finite localized Weil test-function positivity to the unrestricted criterion. Its success condition was a documented difference among **proved finite-support consequences**, **support-scaling evidence**, and the **still-unproved all-support implication**. It was **not** a requirement to obtain another certificate or solve RH.

**Outcome:** The comparison exposes a **real change in behavior** of the same conservative bound at a materially larger support, a **provable local analytical applicability limit**, and an **unclosed global quantifier**. It does **not** establish an unavoidable obstruction to all combined-Schur schemes. The only justified decision is a **methodological STOP** on routine continuation by isolated certificate accumulation while leaving structural mathematical possibilities **unresolved**.

## 2. Exact evidence and classification

| Evidence class | What is established | What is NOT established |
| --- | --- | --- |
| **Independently retained finite-support theorem** | v3 C-0067: strict localized Suzuki/Weil positivity on \(C_c^\infty(-11/20,11/20)\) at T=0.55 using N=192, complete mixed \(V/P/R\), independently rederived 37,056 Arb inputs and exact rational positive congruence, under explicitly documented Suzuki/Arb trust assumptions | Positivity of the Schur criterion at any prescribed larger T; RH; all canonical full-operator-domain equality |
| **Immediate mathematical support consequence** | For every \(0<t\le11/20\), the **same unscaled Weil form** is strictly positive on \(C_c^\infty(-t,t)\) by inclusion, with the original existential coercivity constant | New admissions, validity of fixed N=192 Schur matrices at smaller T, or all-support positivity |
| **External-source-dependent consequence** | C-0068: Suzuki v3 smooth-test-core identity and continuous lowest eigenvalue imply *some unspecified* \(\delta>0\) with strict test-class positivity on \(0<t<11/20+\delta\) | A quantitative \(\delta\), a proved explicitly chosen T>0.55, a new Arb/Rust proof, or a separate admitted certificate |
| **Rigorous sufficient-tail scalar scaling** | SYS-6.2 Arb-256 conservative \(\mu_N>0\) first passing cutoffs: at T=0.55/0.60/0.65/0.69/0.70 respectively N=109/160/238/331/624; at every fixed T in the **current** \(0<T<\pi/2\) local range, some (possibly enormous) N passes by finiteness of losses plus \(H_N\to\infty\) (C-0071) | Necessary cutoff for actual Weil positivity; an all-support N(T); positivity of the low combined-Schur matrix |
| **Numerical input/cost scaling** | Arb full-truncated-image Gram reconstruction at N=64/128 for selected T succeeds with sufficiently high precision; mixed trace changes sign across support and input widths can grow catastrophically when precision is inadequate | Sign or spectral lower bound for full Schur from trace alone; reliable complexity law beyond executed samples; general positivity/negativity of the Weil form |
| **Selective rigorous-sign research result** | At T=3/5=0.60,N=192,K=32, with strictly positive chosen conservative \(\underline\mu\approx0.18492\), one odd-parity exact rational direction gives an outward-interval **negative upper** \(\approx-3.12334042\) for the chosen full-residual combined-Schur sufficient matrix; independent Fraction replay confirms exact arithmetic and fingerprints | An independent second reconstruction of *all* 37,056 Arb inputs for T=0.60; negativity of the underlying Weil form; failure for other N/stronger complement/other sufficient bounds |
| **Unrestricted logical obligation** | C-0069: RH is equivalent, under the externally cited Weil criterion, to nonnegativity on **all** compact smooth test functions, or a mathematically **proved unbounded covering family** of test supports; a support-independent positive coercivity constant is **not required** | Discharging the universal quantifier by finitely many certificates or by unquantified local eigenvalue continuity |
| **Analytic scope limitation** | Local C-0063 and the implemented Bernoulli/Taylor residual enclosure need \(2T<\pi\); source code refuses T=2. Suzuki's Weil form itself is globally defined | A global residual enclosure or full-Schur inequality for unrestricted T; a no-go theorem beyond this code's convergence domain |

The original eight v1 retained theorems and one v3 theorem remain **nine retained fixed-support admissions**, *not* infinitely many admissions from support nesting. C-0068/C-0069/C-0071 are **source-dependent or elementary deductions**, not admissions. The negative research sign at T=0.60 is a statement **about a chosen sufficient bound**, not a new negative-form theorem.

## 3. Mathematical continuation assessment

**Criterion under discussion.** For an admissible T and Legendre cutoff N, the existing **full** combined-Schur sufficient matrix is
\[
S_{T,N}(\underline\mu)=A_{T,N}-\underline\mu_{T,N}^{-1}B_{T,N}^*B_{T,N},\qquad
\underline\mu_{T,N}>0,
\]
with complete mixed images and full residual. Its strict positivity is sufficient for the form, but its failure need **not** imply the form is negative. The bound is **not** known necessary, nor known to be equivalent to the unrestricted Weil criterion.

**Verified successes:** Positive complete fixed-support theorem at T=0.55,N=192; exact reconstruction/verification is feasible at this finite size. A positive conservative high-tail scalar is pointwise achievable throughout the current local range, so **that scalar gate alone is not a mathematical no-go**.

**Verified new limitation:** Holding N=192 and the conservative complement strategy fixed, the same sufficient Schur matrix is **not positive** at T=0.60: a strict negative odd-sector directional upper survives exact rational rechecking. Even with rigorous \(\underline\mu_{192}>0\), the low mixed-Schur positivity needed by the theorem does not follow. The negative result is generator-source-qualified, not yet independently all-entry accepted at T=0.60. It is not a universal statement across N and does not rule out sharper \(\mu\) or stronger inequalities.

**Scalability:** Increasing support raises conservative residual/normalization losses and the number/geometry of active prime powers. Required \(N\) and rigorous Arb precision both become more costly for **these** estimates. It is unknown whether improved analytic bounds control these effects uniformly or whether a viable non-conservative replacement exists. Neither a finite numerical trend nor a certificate verifier establishes an unbounded parameter family.

**Decisive proof gap:** A universal argument would require valid source representation and residual control at arbitrarily large supports, alongside full low-matrix Schur positivity (or a *different* independently justified global inequality). The current local residual evaluator itself stops at \(2T<\pi\). Even within that interval, the existence of N making \(\mu_N>0\) says nothing about the second low-block sign. Proving **all** necessary Schur inequalities for an unbounded support-covering family would, by C-0069, **imply RH**; this universal sufficient criterion is **not proven equivalent in reverse**, and no claim is made that it is intrinsically easier.

**Classification of the method:** **CONDITIONALLY EXTENSIBLE AS A FINITE-SUPPORT TOOL; UNRESTRICTED GENERALIZATION UNPROVED / NOT CURRENTLY JUSTIFIED.** The existing fixed-parameter continuation workflow is **BLOCKED AS AN RH-SCALING STRATEGY** by the absence of a support-parameter positive low-Schur inequality and by the local residual domain. A theorem that the method itself is structurally impossible is **NOT established**.

## 4. Explicit continuation and no-go decision

**Decision: NO-GO for routine continuation by accumulating isolated finite-support positive matrices or certifying arbitrary nearby supports as an RH research strategy.** This is a prioritization and proof-standard judgment based on the already executed evidence; it is **not** a statement that a new finite-support theorem would have zero intrinsic mathematical value.

- Do not interpret larger N, more Arb bits, more certificates, or a successful scalar \(\mu_N\) as a justified path to unrestricted positivity **without an independent structural argument**.
- Do not promote either the SYS-6.2 diagnostic traces or the SYS-6.4 negative sufficient-Schur result to new positivity/negativity of the actual Weil form.
- Preserve the existing full mixed-Gram/Suzuki/Arb/Rust infrastructure and all admitted theorem evidence unchanged. Avoid a new generic production admission or verifier contract solely to add isolated theorem counts.
- This is **NOT a mathematical no-go** for other cutoffs N, sharper complementary bounds, all-support analytic decompositions, or the underlying Weil criterion. An independently justified new *mathematical or methodological* insight can warrant renewed selective testing, but testing itself is not the justification.
- No prospective research sequence or detailed private roadmap decisions are published here. This is the completed **factual assessment**, explicit methodological decision and current proof boundary, not an action plan.

**Consequent theorem-admission decision:** **NO NEW ADMISSIONS IN SYS-6.** Leave frozen v1 at eight, v2 at zero, v3 at **C-0067 only**. No negative Weil claim, no RH claim.

## 5. Completion gate and reproducible review integrity

All SYS-6 completion obligations are satisfied **as an assessment**:

- [x] Correctly separate inherited positivity for smaller supports and Suzuki's external-source existential right neighborhood from an independently verified explicit larger-support certificate.
- [x] Document rigorous scalar sufficient-tail costs, prime-power/shift thresholds, complete mixed-interaction changes, residual growth, numerical enclosure width and verification costs.
- [x] Select and test one mathematically informative larger support rather than proliferating identical certificates; give an exact scope-qualified negative sufficient-matrix result and independent arithmetic replay.
- [x] Express unrestricted Weil positivity with correct global logical quantifiers, requiring no single uniform positive constant.
- [x] Identify which combined-Schur proof hypotheses are still missing in a universal family and distinguish the \(2T<\pi\) implementation restriction from Suzuki's globally defined form.
- [x] Classify the current method as **locally valid, conditionally extensible, but lacking a justified unrestricted argument**; take a methodological no-go on certificate proliferation without claiming a global mathematical no-go.
- [x] Preserve exact retained proof and public/private documentation boundaries and explicitly record no theorem admission and unresolved RH.

**Mathematical integrity note:** The present synthesis **does not introduce a new mathematical theorem**, independently reconstruct new Arb matrix inputs, or rerun the expensive v3 retained theorem proof; it reviews verified source-controlled prior results. Prior independent numerical acceptance belongs specifically to X-20261018-003 at T=0.55; the T=0.60 research negative check has narrower single-generator/source and independent exact-arithmetic scope. Future work may not treat these trust layers as interchangeable.

**Final SYS-6 gate: SATISFIED. RH: UNRESOLVED.** This is the closure of the *support continuation assessment*, not of the Riemann Hypothesis or the more general global Weil-form positivity question.
