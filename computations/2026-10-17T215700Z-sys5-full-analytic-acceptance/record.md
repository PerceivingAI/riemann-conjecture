# X-20261017-006 — Independent rigorous containment of every combined-Schur analytical input

- **Created:** 2026-10-17T21:57:50Z
- **Last updated:** 2026-10-17T22:06:11Z
- **Type:** INDEPENDENT_ANALYTIC_INPUT_VERIFICATION / 2048-bit Arb finite-expression reference with complete interval containment
- **Status:** **PASS — ALL 37,056 MATRIX INTERVAL SLOTS AND \(\mu,\delta\) CONTAIN INDEPENDENT RIGOROUS INTERVALS**
- **Evidence:** [F-20261017-015](../../findings/2026-10-17T220105Z-complete-independent-analytic-enclosure-closure.md).
- **Original immutable candidate:** [X-20261017-003](../2026-10-17T150153Z-combined-schur-bounded-test/record.md), [X-20261017-004](../2026-10-17T153222Z-analytic-source-review/record.md).
- **Git baseline:** `bae1b975abc053f6aba12972621b540110b9b2f9` plus uncommitted SYS-5 research. No v1/v2 certificate, Rust, Lean or theorem-admission code was modified.

## 1. Acceptance question and strict inclusion rule

Given the original executed `T=11/20,N=192,K=32,Arb-1024,\eta=2^{-24}` positive candidate, independently rederive and rigorously enclose every finite low-form input \(A_{ij}\), truncated combined-Gram input \((G_K)_{ij}\), complementary \(\mu_{192}\), and full Suzuki remainder \(\delta_K\).

The archived inputs are **outward 352-bit dyadic rational intervals**, not symbolic expressions or merely floating diagnostics. For each independent Arb interval \(I_{\rm new}=[a,b]\) at 2048-bit precision and archived exact rational interval \(I_{\rm old}=[L,U]\), the verifier enforces the strong inclusion
\[
  L\le a\le b\le U
\]
using **exact rational** endpoints extracted from Arb. Mere overlap, agreement of midpoints, equality of displayed decimals, or generator self-assertion is **NOT** accepted. This implication guarantees the old interval contains the exact analytic value whenever the independently reconstructed interval does.

The result is a **complete** check: 18,528 upper-triangular low entries + 18,528 upper-triangular combined Gram entries, and the full scalar \(\mu,\delta\) intervals; exact reflection parity verifies other entries are mathematical zeros. This is a fixed existing research candidate, not a new dimension/support sweep or theorem admission.

## 2. Distinct reconstruction and trusted mathematical foundations

`scripts/verify_combined_schur_analytic_entries.py` independently constructs the entire finite expression chain without importing the SYS-3/SYS-4 `assemble_truncated_mixed_gram`, `_mixed_by_shifts`, `_potential_matrices`, `_residual_truncation_operator`, `assemble_active_prime_power_operator`, or any other original matrix generator **at N=192**. It uses the independent formulas:

1. Exact ordinary Legendre recurrence over \(\mathbb Q\), including the exact diagonal norm \(d_i=2/(2i+1)\). Python-flint `fmpq_poly` implements exact finite polynomial operations.
2. Exact Bernoulli-polynomial coefficients \(\sum_{j}\binom{n+1}{j}B_j(3/4)^{n+1-j}\), and a **separately implemented two-sided endpoint expansion** for \(\int_{-1}^1|x-y|^d y^kdy\). The resulting exact residual image polynomials have degree at most 223.
3. Whole-interval \(V,V^2\), and \(VR_K\) moments from the analytically derived beta-derivative formulas with exact harmonic coefficients. Only \(\log2,\pi\) enter via rigorous Arb enclosures; no direct singular quadrature is used.
4. Strictly certified arithmetic support: \(\log2<2T,\log3<2T,\log4>2T\); signed \(-\log m/\sqrt m\) for both prime terms; every signed two-sided shift. All ordered breakpoints are proposed then verified strictly with Arb; activity at the rigorously interior cell midpoint is constant across each already partitioned interval.
5. Independently computed local-Legendre affine recurrences for each active shift cell and independent cell Gram products for \(\langle P_i,PP_j\rangle\) and \(\langle PP_i,PP_j\rangle\), including **mixed \(m=2/m=3\)** terms before squaring.
6. Separate **global monomial translations** and analytic logarithmic subinterval primitives to compute ordered \(\langle VP_i,PP_j\rangle\) and \(\langle PP_i,R_KP_j\rangle\), with independent exact polynomial moments. Endpoint singularities are handled only via mathematically proved removable limits; uncertified logarithm arguments fail closed.
7. Independent finite-expression matrix contractions for \(VV,PP,R_KR_K,VP,VR_K,PR_K\) and their reverse ordered counterparts, followed by exact unnormalized \(\Pi_N\) subtraction \(KD_N^{-1}K\). The calculated truncated Gram is the full **combined** \(V+P+R_K\) one, not the previous factor-3 upper bound.
8. Independent \(c_T=\log(2\pi T)+\gamma\), exact harmonic jump diagonal, full Suzuki \(\delta_K=2T\cdot\mathrm{tailRadius}\), positive complement \(\mu_N=H_N-c_T-\sum c_mb_m-\rho_R\) (here each certified path-chain norm is exactly 1), and low-form **LOWER** correction \(-\delta_K D_N\).

Each infinite-analytic formula used is derived/proved as an elementary beta derivative, binomial polynomial integral, logarithmic antiderivative, or uniformly bounded Bernoulli/exponential tail; the basis and mixed-image identities are finite algebra. Arb's documented **correct outward ball arithmetic** and exact `fmpq` operations are the explicitly relied-upon trusted numerical primitives. Independent implementation here means **separate mathematical assembly and rigorous per-entry values**, not a different underlying MPFI/Arb arithmetic library or a Lean proof of Arb's C code.

For the small `N=8` structural check only, the independently assembled full Gram was compared against the existing generator: **all 64 entries interval-overlapped**, including parity. This small comparison was a diagnostic prior to the full run and **is not used** to generate or accept the `N=192` results.

## 3. Executed proof input verification

Command:

```text
uv run --locked python -m scripts.verify_combined_schur_analytic_entries --dimension 192 --precision 2048 --verbose --packet computations/2026-10-17T150153Z-combined-schur-bounded-test/data/matrix-N192.json.gz --output computations/2026-10-17T215700Z-sys5-full-analytic-acceptance/data/independent-entry-containment-N192.json
```

**Exit 0**, wall time **53.972 s** reported by independent auditor, separately observable process normal completion.

| Independently certified comparison | Exact outcome |
|---|---|
| Archived \(A\) upper triangle | **18,528 / 18,528 contained** |
| Archived combined \(G_K\) upper triangle | **18,528 / 18,528 contained** |
| Archived \(\mu_N\) rigorous interval | **Contained** |
| Archived \(\delta_K\) rigorous interval | **Contained** |
| Opposite-parity input cells | Mathematical exact zero verified inside archived endpoints |
| Failures | **0** |
| Independent Arb precision | **2048 bits** |
| Original source Arb precision | 1024 bits |
| Original archive dyadic precision | 352 bits |

**Important:** This is a strict independent `new \subseteq old` containment proof, not a test that the old/new ranges merely overlap. The independent routine constructs all indexed matrices from its own exact finite polynomial and analytical moment formulas; the only reused numerical kernel is rigorous Arb.

The exact comparison output `data/independent-entry-containment-N192.json` has **SHA-256 `f410045743461cd09c97cda0fa1119ecea2111d738982381ff89542c5058bb2f`**. Independent source SHA-256 **`15961f4b337e1d26cc63aa41bcb3976fa975636d0b5e006b0f51bd3d625576e4`**. The source/packet are immutable as executed: original full input SHA-256 **`655d481d638f8b6fba0f95d01a4bab45079d905fbc6cb4f3e822571729d4d7c1`**, and original 48-bit dyadic positive witness SHA-256 **`d9130344b09978fe84026dff0cbe3bf54cbda4c0603828af9f36cc84a32fc48f`**.

## 4. Independent exact-rational proof replay and controls

After the separate full input validation, reran the existing independent research rational verifier on the **unchanged archived packet and witness**:

```text
uv run --locked python -m scripts.verify_combined_schur_research --packet computations/2026-10-17T150153Z-combined-schur-bounded-test/data/matrix-N192.json.gz --proof computations/2026-10-17T150153Z-combined-schur-bounded-test/data/positive-witness-N192.json.gz --output computations/2026-10-17T215700Z-sys5-full-analytic-acceptance/data/independent-exact-replay-N192.json
```

**Exit 0** — `INDEPENDENT_EXACT_POSITIVE_CONGRUENCE_PASS`; independently reconstructed entire conservative rational \(S_{\rm low}\), exact rational \(W S_{\rm low}W^\mathsf T\), and all exact Gershgorin row margins. The minimum *exact* rational margin is strictly positive (decimal diagnostic `0.9999999993343024`). The original witness remains unmodified; this checker does not depend on a float eigenvalue.

Replay output SHA-256: **`f90f40ffb84c9b550b1e489d29d4028f75417b3b17723a80413f9b3af65082f9`**.

Controls:
- Previously scoped frozen v1/mixed-Gram tests: **44/44 PASS**.
- New `tests/test_combined_analytic_entries.py`: **5/5 PASS**; rejects altered exact interval endpoints, an unreliably ordered dyadic interval, a singular logarithmic cell, out-of-radius residual support and incorrect prime-power header. Its small-\(N=8\) full Gram reference checks every entry; no new large \(N\) experiment.
- Earlier source audit [X-20261017-005](../2026-10-17T214044Z-sys5-analytic-proof-audit/record.md) independently tested 81 exact rational split-kernel polynomial identities and eight nonproof high-degree moment references.
- All active processes are required to be cleaned up; no descendant is intentionally left running.

## 5. Mathematical conclusion and exact scope

The earlier statement that complete independent analytical input containment was missing is **no longer true** for the single executed \(T=11/20,N=192\) case, because all stored scalar bounds and every low/combined-Gram entry were independently reconstructed rigorously and checked by strict interval inclusion.

Given this independent analytical reconstruction, the existing strict exact rational positive-definiteness witness and the prior source-domain/form-Schur proof, the **mathematical proof obligations for the precise fixed-support test-class positivity statement are satisfied within the explicit Arb soundness and Suzuki source-form assumptions**. It is mathematically significant to distinguish this from a new **accepted repository theorem**: the separate proof-bearing certificate profile, exact independent Rust acceptance, Lean soundness and explicit theorem-admission decision have **not** been performed. No claim ledger theorem is silently promoted.

**Scope:** \(Q_W(f)\ge\varepsilon\|f\|_2^2\) for all \(f\in C_c^\infty(-11/20,11/20)\) in Suzuki's stated normalization, with \(\varepsilon>0\) from the form-Schur coercivity argument. No conclusion is drawn at any other support, for arbitrary \(T\), for equality of all canonical Friedrichs operator domains, or for RH.

**Final source-side mathematical gate:** `SATISFIED / READY FOR SEPARATE CERTIFICATE PROFILE AND ADMISSION WORK`. The status of theorem admission remains `NO NEW THEOREM ADMITTED`.

---

## 2026-10-17T22:06:11Z — Final execution and repository integrity gate

The final Portus project session inventory confirmed **zero running/queued execution sessions**. The independent 2048-bit source audit, original independent rational congruence replay, 44/44 existing focused regressions, and five new fail-closed tests all exited successfully; no processes remain active. Final consistency check independently matched immutable packet and witness SHA-256, the source code as-executed SHA-256 and both evidence artifact hashes, verified all 37,056 strict entry containments and two scalar containments, and checked 417 current local documentation links without missing targets. `git diff --check` passed; all SYS-5 files remain uncommitted and the separate private notes are Git-ignored. No theorem admission or RH claim was performed.
