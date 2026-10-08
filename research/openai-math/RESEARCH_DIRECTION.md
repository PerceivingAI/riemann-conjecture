# OAI-8 — Research-direction evaluation after OpenAI quasi-RH

- **Created:** `2026-10-08T03:15:03Z` (UTC)
- **Last updated:** `2026-10-08T03:15:03Z`
- **Status:** `COMPLETE — DIRECTION DECISION`
- **Decision authority:** Repository evidence and explicit comparative criteria; no claim of a proof of RH
- **External result:** `EXT-0001` — `openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`
- **OAI dependencies:** OAI-3 formal overlap; OAI-4 route-impact audit; OAI-5 `C-0061/0062`; OAI-6 reference-only source policy; OAI-7 external/local proof separation
- **Boundary:** This is a decision document, not a new theorem, numerical run, certificate, or formal proof.

## Decision first (OAI-8.5)

**PRIMARY:** the **localized Weil / exact Legendre–Schur** mathematical program, **with an explicit change of mathematical focus**: preserve the eight frozen one-prime theorems and investigate a new valid and stronger multi-prime sufficient positivity bound. The **current factor-3 grouped Schur inequality is rigorously rejected at the frozen `T=11/20`, `N=192/196` targets**, so repeating the same inequality at higher arithmetic precision or witness bits is *not* a viable next step. Maintaining this route as primary is a comparison of its proved intermediate results and audit infrastructure, **not** a prediction that it will prove RH.

**SECONDARY:** the **phase-aware/Laguerre prime-discrepancy route**, as a mathematically separate research program for precisely scoped intermediate results and possible new cancellation estimates. `EXT-0001` genuinely improves its quantitative input but does **not** remove its RH-strength obstruction. Do not make its current root criterion or a routine large-sieve estimate an active claim of progress to RH.

**DEFERRED:** a **Weil–phase-aware hybrid proof route** as an implementation or proof program. No established mapping from the compactly smoothed `C-0062` discrepancy bound to a stronger, rigorously positive full localized-Weil Schur/Gram operator estimate has been identified. Only a short, analytical bridge-feasibility investigation is permitted **if** it starts by stating an exact interface lemma and testing its required strength; no new hybrid code or theorem-admission machinery is justified now.

**Does `EXT-0001` change the best primary route?** **No.** It improves the secondary route's external arithmetic knowledge and produces `C-0060..C-0062`, but it provides no newly admissible finite-support positivity and does not repair the measured multi-prime Schur negative. The choice is supported by actual local achievements rather than by the novelty of the upstream theorem.

## Evidence and epistemic controls

### Common distinction between available facts and extrapolations

- **External established input:** `EXT-0001` says `zeta(s) != 0` for `Re(s)>7/8`. The upper boundary `Re(rho)=7/8` is not excluded. Its formal source is pinned and attributed; this project has **not** independently performed Comparator replay.
- **Our written deductions from it:** `C-0060` confines nontrivial zeros to `1/8<=Re(rho)<=7/8` and gives fixed-center Laguerre root `limsup |S_n(s0)|^(1/n) <= (s0-1/8)/(s0-7/8)>1`; `C-0061` supplies `psi(x)-x=O(x^(7/8)log²x)` and a prime-counting error; `C-0062` bounds fixed compact smoothed critical-half-weight discrepancy by `O_W((1+|tau|)X^(3/8)log²X)`. These are *written mathematical deductions*, not locally kernel-checked Lean statements.
- **Existing certified local positivity:** `C-0050..C-0057` are eight **finite-support** localized Weil statements, independently retained and checked with the exact-rational Rust certificate chain under their separate analytic assumptions. They do **not** prove positivity for arbitrary supports or all Weil test functions.
- **Current rigorous negative diagnostic:** the `T=11/20` tests at `N=192/196` exhibit *exact negative directions in the particular sufficient factor-3 Schur matrices*. Those negative directions are **not** evidence of negativity of the full Weil quadratic form and are **not** counterexamples to RH.
- **Stage distinction:** source review, mathematical derivation, exploratory scout, strict interval rejection of one sufficient criterion, exact Rust certificate acceptance, and a full RH proof are different levels. See [`docs/CONTRACTS.md`, Section 5](../../docs/CONTRACTS.md) and [`docs/PROTOCOL.md`, Section 7.2](../../docs/PROTOCOL.md).

### Evidence index used for this decision

| Evidence | Specific supported fact |
| --- | --- |
| [`docs/CLAIMS.md`](../../docs/CLAIMS.md), `C-0048`, `C-0050..C-0059` | Analytic complement/Schur semantics, eight admitted supports, generic complement and grouped-prime operator |
| [`computations/retained-proofs.json`](../../computations/retained-proofs.json); [`docs/CONTRACTS.md`](../../docs/CONTRACTS.md) | Eight registered proof artifacts, closed v1 acceptance, separate empty v2 admission table |
| [`X-20261001-001`](../../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md), phases 8, 9, 11 | Stabilized matrix enclosures, exact negative directions, preflight classification and measured performance; `P9` remains NOT QUALIFIED |
| [`docs/MULTI_PRIME_CONTRACT.md`](../../docs/MULTI_PRIME_CONTRACT.md) | Active set `{2,3}` in the first generic window, `P=P2+P3`, `G_P` with mixed arithmetic cross terms, factor-3 sufficient bound |
| [`OAI-4 impact audit`](../../references/external-results/EXT-0001-route-impact-audit.md) | Eleven historical routes checked; none of the existing RH-strength blockers removed by `EXT-0001` alone |
| [`OAI-5 finding`](../../findings/2026-10-08T024431Z-openai-seven-eighths-prime-distribution.md) | Precise ordinary and compactly weighted `7/8` prime-error bounds and missing cancellation |
| [`OAI-3 formal overlap`](../../references/external-results/EXT-0001-lean-overlap-audit.md) | Available Mathlib zeta, Mangoldt, matrix foundations; local four-module `Cert` formalization; different OpenAI Lean/Mathlib version |
| [`OAI-6 reuse decision`](../../references/external-results/EXT-0001-reuse-and-license-decision.md) | Citation-only external result; no imported source/toolchain upgrade |

## OAI-8.1 — Generic Weil: baseline with current mathematical obstruction

### What is proven and what is not

- The finite one-prime v1 support/dimension whitelist is exactly `(7/20,32)`, `(2/5,40)`, `(17/40,48)`, `(9/20,56)`, `(19/40,68)`, `(1/2,80)`, `(21/40,96)`, `(27/50,104)` (claims `C-0050..C-0057`). Retained independent replay was last recorded as **8/8 PASS**. These are precise bounded-support mathematical achievements, *not* RH.
- The next structural transition is `T=(log3)/2`. The generic prime-power mathematical contract `C-0058/0059` and additive v2 toolchain exist, with separate schema and Rust exact-verifier semantics. **The v2 theorem-admission grid is empty.**
- The first frozen generic target, `T=11/20`, `N=192/196`, does not pass the existing sufficient grouped-factor-3 Schur positivity gate. Phase 8's stable full intervals have exact negative Rayleigh upper bounds with nonzero witnesses. Phase 9 independently confirms those negatives, and Phase 11 produces **8/8 strict negative quadratic-form upper bounds** on the actual higher-precision/rounding candidate inputs.
- This is a **mathematical failure of that sufficient criterion at those two targets**, after numerical-conditioning repairs. It does not assert that another dimension, another support or a sharper *valid* inequality must pass. In particular, raising precision/witness bits on the *same sufficient matrix* cannot make a genuinely negative matrix positive.

### Missing mathematical work

**Near-term intermediate theorem:** Produce an independently justified sharper positive lower criterion for the localized operator (or a completely different valid sufficient operator reduction), demonstrate that it is not defeated by the retained negative witnesses to the *old* sufficient matrix, and then give rigorous enclosure, separate exact-verifier semantics and explicit theorem admission before any new support becomes proof-bearing. **At least two distinct gates remain**: a new sound analytic criterion and its independent numerical/certificate qualification; more than two technical subproblems may arise.

**Full RH:** Even success in one new support window would leave the fundamentally separate problem of positivity for the entire admissible Weil test class / arbitrarily large supports, including every subsequent prime-power transition and any required uniform estimates. No such all-support theorem is present or shown likely by the finite data. The number of necessary future mathematical breakthroughs is **not quantified**.

### Concrete research candidate, not an admitted theorem (W-1)

The existing decomposition writes the low-to-tail block as `B=B_V+B_P+B_R`, with `C_N>=mu_N I` and `mu_N>0`. The present sufficient matrix is

```text
S_old = A_N - (3/mu_N)(G_V+G_P+G_R),
G_i = B_i* B_i,  with B_i = Q_N O_i Pi_N.
```

A **mathematically valid but unverified-for-positivity** alternative is to retain the combined cross block exactly:

```text
G_all = B* B = Pi_N (V+P+R) Q_N (V+P+R) Pi_N,
S_new = A_N - (1/mu_N) G_all.
```

For self-adjoint `V,P,R` and well-defined indicated low-to-tail maps, the standard Schur/completing-square argument says `S_new>0` together with `C_N>=mu_N I>0` is a **sufficient** full-operator positivity condition. For each low vector `f`, set `v_i=B_i f`. The exact Hilbert-space identity `3 sum_i ||v_i||² - ||v_V+v_P+v_R||² = sum_(i<j) ||v_i-v_j||² >= 0` proves `G_all <= 3(G_V+G_P+G_R)` as quadratic forms, hence `S_new >= S_old` when the low-to-tail maps are well-defined on the trial space. The inequality is algebraically sound; **no positive lower eigenvalue for `S_new` is established or predicted**. Exact evaluation of the mixed `V/P/R` low-tail Gram terms, numerical enclosures, domain consistency, and certificate acceptance are all currently missing. The retained negative directions of `S_old` do **not** contradict positivity of `S_new`, but do not support it either.

**Gate for trying W-1:** first prove the operator/domain and exact mixed-tail identities on the repository's normalized basis; then a small focused, independently audited enclosure test at the frozen targets may assess whether the new criterion is even worth implementing. Do **not** change the existing factor-3 v2 certificate/profile, overwrite negative witnesses, or authorize new support admissions as part of this exploratory check.

### Verification maturity and cost

The **existing verifier/retained chain** is mature for its eight v1 pairs. The generic v2 generation and independent exact-verifier infrastructure is implemented and tested but has **no admissible theorem**. Recorded Phase 11 measurements (not general scaling laws):

- Rigorous isolated matrix assembly at `T=11/20,N=192/196`, Arb 512: **23.183 / 24.983 seconds**.
- Actual frozen two-worker `192/196` screening ladders: **109.598 seconds**, both `MATHEMATICAL_NEGATIVE`.
- One actual `N=196`, Arb 512, `104/56` candidate: native exact witness **53.525 seconds**, versus **541.946 seconds** old backend, with the *same rejection*.
- Post-cutover default Python suite **715/715**, with **77/77** focused; this is evidence of software correctness and efficiency, **not** positivity. Rust/Lean/retained proof gates were not rerun after that Python-only backend change (unchanged source/contract inputs).

No observed runtime bound is asserted for a new mathematical criterion, larger support or a full RH-scale program.

## OAI-8.2 — Phase-aware/Laguerre route under EXT-0001

**Verified existing structure:** `C-0010` gives an RH-equivalent fixed-center pole-subtracted coefficient root criterion; `C-0019`, `C-0021..C-0025`, and `C-0028..C-0035` record exact individual-zero responses, critical chirp/microlocal phase structure, the limitations of generic mean-value bounds, and the logarithmic Hessian rank-one obstruction. Some are kernel-level or fixed-mode results, *not* a uniform theorem over all prime powers and zeros.

**Verified improvement from the new external premise:** `C-0060` narrows off-line zeros to `1/2<beta<=7/8` on the right; its coefficient root upper bound remains strictly greater than `1` for every fixed `s0>1`. `C-0061` gives `psi(x)-x=O(x^(7/8)log²x)`. `C-0062`, for **fixed compact smooth** weights, gives critical-half-weight discrepancy `O_W((1+|tau|)X^(3/8)log²X)`. At fixed-interior `X=exp(cn)`, the upper bound permits `exp(3cn/8)` growth. This is **an insufficient upper bound**, not evidence of an actual exponential lower bound.

**Missing proof:** A noncircular, uniform-in-degree / all-relevant-cells signed prime-cancellation estimate (or genuinely new analytic mechanism) that reaches the `C-0010` root threshold `<=1`, with rigorous treatment of Laguerre/DLMF remainders, turning-region and endpoint behavior, unbounded Mellin frequencies and the full prime-power measure. The exact fixed-zero contribution still amplifies if `1/2<beta<=7/8`; no `EXT-0001` statement cancels it. Claiming `O(X^(11/4))` mean-square as the needed `O_epsilon(X^(2+epsilon))` would be circular/incorrect.

**Computational and formal status:** Current `scripts/` and `crates/rh_engine` can calculate finite diagnostics, phase identities and exploratory prime sums; these do not validate uniform asymptotic cancellation. Mathlib's ordinary zeta/Mangoldt identities exist, but our local `formal/Cert` layer does **not** contain a Lean proof of the full Laguerre criterion or its missing cancellation estimate. Importing OpenAI's 4.34.1 formal stack (versus our Lean 4.33.0) would add dependencies without proving the missing estimate.

**Secondary deliverable:** seek an independently proved *specific* signed local bound, or another bounded-range analytic statement with a clear fixed/variable-parameter contract, before building more large-scale numeric sweeps. Preserve phase-aware diagnostics as research tools, not theorem evidence.

## OAI-8.3 — Hybrid Weil + phase-aware route: proposed interfaces and rejection tests

An attractive narrative is not an interface theorem. `EXT-0001` constrains global zeta zeros while the existing Weil tests require operator positivity for functions with compact support. A usable hybrid must specify a **quantified implication connecting the exact analytic objects**, not merely observe that both involve primes.

| Proposed bridge | Existing facts it can use | Missing new lemma and required strength | Status |
| --- | --- | --- | --- |
| **H-1: Bound a Weil compressed prime operator using phase-aware arithmetic** | Exact `P=sum_mP_m` / `G_P` (`C-0058/0059`), written compact prime-error `C-0062` | A theorem mapping *the exact scaled compact-translation bilinear form* to a uniformly controlled prime-discrepancy functional for all tested low and tail inputs, with controlled support/dimension/frequency/remainders. A resulting quantitative bound must **improve the actual positive-matrix lower criterion**, not just be finite. | **NOT ESTABLISHED**; no such representation/estimate recorded |
| **H-2: Derive restricted Weil positivity from the 7/8 zero strip** | `EXT-0001`, known Weil positivity equivalence, `C-0060..62` | A new proof that the zero-location information rules out negative contributions for the **specific** test class and support despite possible `1/2<beta<=7/8`, including all analytic interchange/boundary terms. No known implication in the inspected record. | **NOT ESTABLISHED**; cannot assume theorem equivalence becomes a sufficient criterion |
| **H-3: Tighten finite-support Schur via combined low-tail cross Gram** | `C-0048/0059` decomposition and generic matrix tooling | The W-1 `G_all=B*B` identity is an **operator-algebraic Weil-only candidate**, not a phase-aware hybrid. Requires new mixed Gram enclosures and an actual strict positive bound. | **VALID FORMAL CANDIDATE, NOT A PROVED POSITIVITY RESULT; CLASSIFY UNDER PRIMARY WEIL, NOT HYBRID** |

**Prohibited shortcut:** Substituting `O_W((1+|tau|)X^(3/8)log²X)` for a spectral norm bound on `Q_N P Pi_N` is invalid. The former is a compact smooth arithmetic discrepancy bound with specified scalar weights; the latter is an operator norm/Gram bound over arbitrary vectors and includes basis-dependent support, mixed prime terms and possible endpoint singularities. Establishing one does **not** establish the other.

**Low-cost feasibility trigger only:** A hybrid route may be reopened if a written interface lemma precisely identifies (1) same quadratic form/normalization, (2) allowable test functions and parameter scaling, (3) explicit remainder and constants, and (4) a signed or positivity inequality strong enough to beat the old negative-matrix obstruction or provide a genuinely different positivity theorem. Until that exists, no hybrid implementation budget or theorem claims.

## OAI-8.4 — Comparison on identical criteria

Ratings describe **evidentiary/engineering maturity relative to the next independently checkable intermediate result**, not probability of RH success. Unknown proof-complexity and future runtime are not assigned numerical scores.

| Dimension | Generic Weil/Legendre–Schur | Phase-aware/Laguerre | Hybrid |
| --- | --- | --- | --- |
| **Mathematical obstruction** | Existing factor-3 sufficient Schur **fails rigorously** at `11/20,192/196`; need a new valid bound; all-support positivity remains unproved | Must prove RH-strength signed cancellation and control all degree/frequency/endpoint regimes; `7/8` exponent misses by `3/8` after half-weighting | No established bridge from `C-0062` to a sharper Weil operator estimate; inherits obligations of both |
| **Verification maturity** | **Highest for finite intermediates**: eight independently retained v1 positivity theorems; v2 tooling tested but 0 admissions; old sufficient test rejected at two targets | **Written derivations and diagnostics**: exact mode and phase identities plus `C-0060..62`; no proof of terminal root criterion | **None for an integrated theorem**; no mixed-result certificate or bridge theorem |
| **Remaining proof work** | At least valid new lower criterion + rigorous enclosure/verifier/admission before *a possible* ninth proof; full RH would require separate unbounded-support theorem | At least uniform signed cancellation and complete kernel/error/endpoint bridge to the root criterion; number of major advances unknown | At least a quantified cross-method interface + useful stronger bound + required verification; no credible total count |
| **Formalization** | Local Lean `Cert` provides interval/LDL/Gershgorin/endpoint foundations, while Rust certifies exact v1/v2 predicates; analytic all-support theorem not Lean-formalized | Mathlib zeta/log derivatives exist; full Laguerre cancellation not formalized; OpenAI theorem remains an attributed external input | No formal hybrid statement or compatible integrated build; adding OpenAI toolchain would be unjustified now |
| **Computational scalability** | Measured target assemblies/preflight feasible after P11 optimization; **mathematical negatives** still block old criterion; new criterion runtime unknown | Finite chirp/prime diagnostics supported; no compute-only path to uniform asymptotics; length/frequency barriers remain | No implemented pipeline or measured costs; integrating tools would be speculative before bridge theorem |
| **External dependence** | Suzuki source and standard analytic operator lemmas; v1 results **do not depend on `EXT-0001`** | `C-0060..62` explicitly depend on `EXT-0001` and classical `R-0035`; old Li/phase identities predate it | Would depend on both the Weil analytic machinery and the extra `EXT-0001` premise if the proposed analytic bridge used it |
| **Incremental value** | **Demonstrated** finite-support rigorous theorems; new operator inequality could offer a testable independent intermediate goal, not guaranteed positive | **Demonstrated** zero strip, prime-error, smoothed-error deductions; future local estimates worthwhile only if strictly new | **Currently not demonstrated**; value contingent on nontrivial bridging lemma |

### Relative conclusion (not speculative odds)

- Weil ranks **first for the next rigorously checkable finite-support mathematical result** because it already has a working analytic/certificate pipeline and eight successful admissions, even though its **current** multi-prime sufficient inequality cannot pass the frozen targets.
- Phase-aware ranks **second for independent analytic intermediate results**. The new `7/8` bound matters there, but no demonstrated route from it to the missing RH-strength estimate exists.
- Hybrid ranks **third/deferred** because it introduces at least one unproved cross-framework implication before any known acceptance test can even be formulated. No performance or success rating is assigned beyond this evidence.

## OAI-8.5 — Execution policy and evidence needed to change the decision

### Primary focused research actions

1. **Preserve baseline:** v1 `C-0050..C-0057` remains frozen. Keep `C-0058/0059`, v2 schema/verifier and the exact negative witnesses unchanged; no auto-admission.
2. **Analytic criterion study:** Start with W-1's combined cross-Gram Schur form (or an independently derived alternative). Prove the domain, normalization and cross-term formula against the exact Suzuki/Legendre operator. An operator-algebraic inequality without any strict positivity result counts as a **candidate**, not a new support theorem.
3. **Single diagnostic acceptance gate:** Only once the new mathematical criterion is closed, run small rigorous, audited tests at the same frozen supports/dimensions to determine whether **the new** criterion has a positive margin. Stop if it has an exact negative direction; do not escalate precision or grid to evade a theorem-valid negative witness.
4. **If a valid positive candidate emerges:** Require a separately approved new certificate/profile or proof rule, fresh exact independent verification, source/provenance checks, explicit whitelist admission and separate retained-artifact registration. This document itself authorizes none of those changes.

### Secondary permitted actions

Retain `C-0060..62` and the established Li/chirp identities as explicit mathematical inputs. Formulate **one precisely stated new cancellation estimate** and first check whether it would actually improve the RH-equivalent root criterion without circularity. Avoid routine full-size sweeps or importing OpenAI's entire formal proof environment.

### Defer / reopen triggers

- **Hybrid:** reopen only with a mathematically stated, proof-checkable interface lemma linking `C-0062` (or a later stronger signed estimate) to the **specific** Weil quadratic form, with enough uniform quantitative strength to affect a certified lower bound.
- **Reassess primary status:** if a new Weil criterion also has independently confirmed exact negative witnesses over the agreed frozen targets, this particular sufficiency direction must stop again. Do not interpret that as proving that *all* Weil or hybrid methods are impossible.
- **Reassess phase-aware priority:** promote it only after a rigorous signed estimate beyond `C-0062` is proved with the uniformity necessary for `C-0010`, not merely after numeric exploration or another partial zero-free strip.
- **RH promotion:** none of these choices authorizes `RH PROVED`; see `docs/PROTOCOL.md` proof-claim gate.

### Scope, cost and trust statement

This decision used existing pinned repository mathematical and measured-computation evidence. It did **not** recompute candidate matrices, independently verify the external Lean proof, run full Rust/Lean certification, infer asymptotic performance from timings, or establish the new W-1 positivity condition. No code import, dependency migration, certificate redefinition or theorem whitelist change is proposed.

**Final decision:** *keep the Weil program primary, pivot its next slice from precision/sweeps to a new sound positivity inequality; keep phase-aware arithmetic second as a distinct analytical research program; defer the hybrid until an explicit, noncircular cross-framework theorem exists.* The external `7/8` result is integrated as attributed mathematical evidence, not as a reason to switch research direction.
