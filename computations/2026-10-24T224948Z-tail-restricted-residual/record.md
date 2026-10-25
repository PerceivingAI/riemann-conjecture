# Tail-restricted residual norm and sufficient scalar cutoffs

- **Computation ID:** `X-20261024-005`
- **Created:** `2026-10-24T22:49:48Z`
- **Last updated:** `2026-10-24T23:00:41Z`
- **Status:** `COMPLETE`
- **Finding:** [F-20261024-007](../../findings/2026-10-24T224948Z-tail-restricted-residual-bound.md)
- **Claim:** C-0088

## Objective and mathematical quantity

Qualify a bound on the entire infinite residual tail compression Q_N R_T Q_N and evaluate its effect on conservative scalar dimensions at the existing C-0087 support. Do not infer a smaller whole-reference certificate from scalar success.

For the existing exact kernel coefficients c_d=-a_d T^(d+1), remove even polynomial terms only when d<2N. The independently reviewed result is

\[
\|Q_N R_T Q_N\|\le\delta+
\frac{6|c_1|+\sum_{\substack{d\ge2\\d\text{ odd or }d\ge2N}}
2^{d-1}(d+4)|c_d|}{N(N+1)}.
\]

The proof includes the distributional cusp, both endpoint boundary terms and range in the auxiliary Legendre operator's spectral domain. It does not differentiate the unknown full remainder. `derivation-v1.md` preserves the initial pre-review text; `independent-review.json` captures the separate read-only mathematical review, which required no mathematical correction. That review did not execute numerical checks; numerical evidence below was produced separately.

## Environment and inputs

`environment.json` records actual Python, python-flint and platform versions. Execution used this Windows x64 PC and its locked virtual environment, without a GPU, WSL, remote compute or a large matrix run. Source precision512 bits; separately organized native reconstruction1024 bits; published scalar intervals rounded outward to352-bit dyadics. Exact kernel coefficients and subsequent scalar arithmetic are rational.

The baseline checkout was local main commit `62f33b6f66f7e446a99a68f1a41bfa137f51592c`. The additive research source in this computation was uncommitted during execution; this is not a clean-source production proof artifact.

Parameters are T=1353/2048=.66064453125,K=38, active[2,3], current N=312. The strict arithmetic window and1<tau2<tau3<2 are freshly certified, so both arithmetic shift norm bounds equal1. The original exact positive reserve, displaying0.18491998558724346, is read only from pinned [C-0087 selection bytes](../2026-10-24T191616Z-weighted-support-extension/data/selection-v1.json), SHA256 `e120acab4919b9ab28e6fd6c7044053bb14514f300d810952a2d52e5dae6d7a3`. An exact copy is `data/baseline-selection-v1.json`.

The old selection is used as a parameter/reserve reference, not passed to a newer source-selection validator or relabeled as a newly produced selection. No old analytical matrices or heads are consumed by this scalar calculation.

## Reproduction procedure

From the repository root, choose fresh output names:

```text
uv run --locked python -m scripts.weil_residual_tail_bound --output computations/<fresh-bundle>/data/scalars.json
uv run --locked python -m scripts.verify_residual_tail_bound computations/<fresh-bundle>/data/scalars.json --output computations/<fresh-bundle>/data/audit.json
uv run --locked --extra test python -m pytest -n 0 -q tests/test_residual_tail_bound.py
```

The source calls the existing exact Suzuki coefficients, complete tail enclosure, c_T and prime-power norm helpers without changing them. The independent auditor does not import the new source module: it reconstructs coefficients by the native Bernoulli-polynomial formula, uses separate complete-tail arithmetic and the unsimplified differentiated-kernel norm sum, and independently recomputes all threshold decisions.

The actual mathematical CLI launches used the locked environment's Python executable directly. `data/*.run.json` and corresponding stdout/stderr retain exact commands, start times, exit codes and observed durations. The focused tests were invoked by the locked uv command above.

For historical reproduction independent of future live source changes:

```text
uv run --locked python computations/2026-10-24T224948Z-tail-restricted-residual/replay-archived-v1.py --output-dir computations/<fresh-replay-directory>
```

This copies the13 captured source/environment files and pinned baseline into an isolated temporary tree, launches Python in isolated mode, checks that loaded project scripts belong to that tree, and compares both JSON results byte-for-byte against the originals. Existing outputs are not overwritten. The current environment must supply the recorded locked dependencies; the launcher does not provision them.

## Output and acceptance

Exact complete results: `data/scalars-v1.json`. Independent receipt: `data/audit-v1.json`.

- Scalar result SHA256: `65cc22df9e5edfbaebd9b183edbc29b179c7d3474731e24170cc9abc543a0b9a`.
- Audit SHA256: `bfa5c1d9774282453b4a5a1022987dceb9db462870e4ffb665d98996106bc83a`.
- The audit checks all39 kernel coefficients exactly, strictly contains all four stored scalar intervals and recomputes every dimension1..312. No floating-point comparison decides a sign or cutoff.
- Full remainder upper displays3.1042360135654356e-15. The global residual upper displays3.0103260259559983; the new tail upper at N312 displays5.939234687167305e-7.
- First sufficient scalar-positive integer/even dimensions: old259/260, new13/14.
- First integer/even dimensions preserving the original exact reserve: old312/312, new15/16.
- At N312 the new complement lower displays3.196853421166317 instead of0.18652798913378738. The lower at N15 displays0.1930207801166317; at N16 it is0.25554921158237676.

All displayed decimals are explanatory approximations to retained rational bounds, not independent precision or optimality claims. The cutoffs refer to the published outward upper charges, not mathematically necessary dimensions.

## Executed checks

1. Actual source CLI: exit0,0.303252000012435 seconds.
2. Actual independent audit CLI: exit0,0.32380490005016327 seconds.
3. Focused exact-operator regression suite:4 passed in0.47 seconds; outer uv process2.785260699922219 seconds.
4. Finite controls: the degree4 kernel at N2 retains the exact nonzero eigenvalue16/15; at N3 its entire compressed operator vanishes. The constant and nonconstant |x-y| cusp identities reproduce their full differentiated images and differ if the diagonal term is omitted. A signed odd/even kernel's complete projected polynomial-image Gram satisfies an exact positive slack bound. Polynomial input images are integrated in full, not truncated to matching output columns. These finite controls supplement the infinite-dimensional proof; they do not establish it by sampling.
5. Actual omitted-remainder, false-reserve-cutoff and exaggerated-mu attacks: each exit1, each without a success output. Their input bytes, stderr and launch receipts are retained; `data/attack-summary.json` records outcomes. These are research-auditor exceptions, not Rust verifier exit semantics.
6. Isolated captured-source replay: exit0,0.9253400999587029 seconds, no live project-script imports and byte-identical source/audit JSON. Receipt: `data/archived-replay-v1/receipt.json`.

No broad Python suite, Rust, Lean or fresh full matrix assembly was run or claimed. All scientific source/audit/replay commands passed on first execution. The three deliberately altered packets failed as expected and are retained as such.

## Interpretation and limits

The full-space residual norm imposed a large avoidable scalar charge on this high tail. Exact two-sided polynomial annihilation and a proved N^-2 differential bound, with the complete remainder still paid, remove that charge. At fixed K, the upper tends to delta rather than zero.

This proves a stronger sufficient tail lower and explains why the old scalar dimension was expensive. It does not prove the weighted low reference at N16, identify an optimal dimension, measure the full-form spectral gap, extend support or establish comparative efficiency. It does not control Q_N R_T P_N by rho_tail. C-0085's full cross-block residual allowance is not changed.

Historical sources, tests, results, the existing C-0087 proof and production contracts/admissions remain unchanged. In particular, this research receipt is not an alternative production complement or an admitted theorem artifact. Admissions remain8v1/0v2/1v3; RH remains unresolved. No literature-priority claim is made for the standard Legendre, distributional or Schur tools.

## Preservation

`source-v1/manifest.json` binds the captured files. The bundle's `manifest.json` seals all retained members except itself, including source snapshots, the initial derivation, mathematical review, numerical outputs, controls and execution logs. Public maintained records describe completed work only; all hypotheses needed to assess this result are stated publicly here and in the finding.
