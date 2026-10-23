# Existing-data audit of directional cutoff and reference losses

- **Computation ID:** `X-20261023-001`
- **Created:** `2026-10-23T10:54:08Z`
- **Last updated:** `2026-10-23T10:55:26Z`
- **Status:** `COMPLETE`, retained scalar information does not determine the exact diagonal-reference sign.
- **Type:** Exact rational audit and written spectral loss review. No new analytical experiment or cutoff trial.
- **Finding:** [F-20261023-001](../../findings/2026-10-23T105526Z-directional-cutoff-and-reference-loss-separation.md), C-0074.
- **Source state:** Existing analytical baseline `172469536bdce79757e591835c3b1331a861167d`. The small additive research audit is uncommitted and retained exactly below; no prior procedure, test, result or artifact changed.

## Objective and inputs

Separate the loss from charging all omitted modes at `w_211` from the loss of replacing the true complementary inverse by its diagonal lower reference. Use the already approved T=3/5,N=192 odd trial and nine accepted full-source intervals at k=193,195,...,209. This audit does not choose or evaluate another support, dimension, trial, precision or cutoff.

| Input | SHA-256 |
| --- | --- |
| `computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json` | `44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b` |
| `computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json` | `9b9a1a0a0b420df0147f07c6fa1f5d9ee9005fb68dc8213cd8880d98556dd843` |

The completed finite-majorant rejection X-20261022-002 is an existing premise, not rerun to confirm its sign. The audit reuses that consumer's input validation, not its `_bound` or `run` predicate.

## Quantities and method

For full source moments t_k and w_k=(mu+H_k-H_192)^-1, define known prefix mass Q, known inverse cost P, omitted mass R and omitted inverse cost J as in the finding. From each full interval I_k, compute exact rational squared-distance lower and squared-absolute-maximum upper bounds. Sum them unweighted and with the existing w_k.

The audit obtains

- `Q_-<=Q<=Q_+` and `P_-<=P<=P_+`;
- `R>=max(0,g_low-Q_+)` using the correct upper bound on known mass;
- the prefix-only upper `s_0<=a_up-P_-` for the exact diagonal reference;
- the finite-tail charge lower `w_211 max(0,g_low-Q_+)`, a bound on the finite allowance, not the actual cutoff loss.

The last quantity must not be called a lower bound on the missing inverse contribution J. Its distribution-dependent weights are exactly what the retained data do not specify.

All calculations use `fractions.Fraction`. A separate inline Fraction accumulation matched all four prefix mass/inverse endpoints exactly. A read-only mathematical review separately checked the loss identities, scalar-information argument and conditional two-sided bracket; it did not run new numerical/source calculations.

## Reproduction and runtime

From the repository root:

```text
uv run --locked python -m scripts.weil_directional_loss_audit --output computations/2026-10-23T105408Z-directional-loss-review/data/replay-loss-audit.json
```

The actual supervised invocation used the locked environment's `.venv/Scripts/python.exe` with the same module/arguments and output `data/loss-audit.json`. The retained audit snapshot can be restored to its original `scripts/` path in an isolated checkout for later reproduction. The output fingerprints the audit and the unchanged rational-validation dependency. Both input packets are bound by immutable bytes.

The CLI refuses to overwrite an existing output and publishes by exclusive hard-link creation. It imports only standard-library arithmetic and the existing standard-library exact-input validator. It does not invoke analytical generators, the previous decisive predicate, a continuation driver or an external program.

Observed exit **0**:

```text
LOSS_AUDIT exact reference UNDETERMINED; prefix upper 1.6623334744459064
```

CPython 3.14.0 on Windows x64, locked environment. One owned process, 60-second external timeout, wall **0.33552349999081343 seconds**, exit confirmed, no timeout. Conservatively adding this audit to prior cycle usage gives **6.562186800059862 seconds**. There were no new source moments or alternative cutoff evaluations, and no test suite was run for this review.

## Observed exact-data conclusions

All endpoints and individual terms are retained as rational strings in `data/loss-audit.json`; decimal displays below are not acceptance conditions.

| Quantity | Decimal display |
| --- | ---: |
| Known mass lower | 0.9635928360509430 |
| Known mass upper | 0.9635928360511430 |
| Known inverse cost lower | 4.744783306913747 |
| Known inverse cost upper | 4.744783306914679 |
| Low-form upper a_up | 6.407116781359653 |
| Prefix-only exact-reference upper | 1.6623334744459064 |
| Omitted mass lower | 0.7987791726070741 |
| Finite-tail allowance lower | 2.862508772853621 |
| Known inverse interval width | 9.321833155950718e-13 |

Exact comparisons establish that every admissible prefix leaves positive upper headroom, the omitted-mass lower is positive, and the prefix uncertainty width is below 10^-12. These do not establish actual positive reference value. The original packet lacks the opposite directional low-form/full-Gram scalar bounds; no such bounds were inferred from observational width fields.

The audit also reports a negative separated finite upper, consistent with the established finite-majorant failure. This is a loss-budget decomposition, not a new trial or a new sign for the exact reference.

## Artifact identity

| Bundle-relative artifact | SHA-256 |
| --- | --- |
| `data/loss-audit.json` | `0a2458b5ead5245a439647b2a127ef267e7c8c98f11b9d4cfdb63b2bd49bcc18` |
| `data/execution.json` | `531ccae10c060ed7f7b7ed2a391df390eae71b70a106463314f7868bc262e780` |
| `data/verification.json` | `2dd8e08155b0492a68f1d2b3caeaa681f87ce36b08dded4e8b17c16db7c0eb5d` |
| `data/source/weil_directional_loss_audit.py` | `a6c6f7b5efd857f1750a6b1bca8b990d33451f920390d765fe53a31db193059f` |

## Interpretation and limitations

Finite cutoff loss `w_211 R-J` and true inverse-reference loss `<Bu,(C0^-1-C^-1)Bu>` are different nonnegative quantities. Neither is numerically determined by the finite negative result. Prefix plus unweighted mass constraints alone admit abstract completions of either exact-reference sign, even with the same scalar a and total mass; those completions are not claimed to be alternate Suzuki sources.

A sign-resolving exact-reference bracket requires bounds on the inverse-weighted tail J and the low form in the directions of inequality needed by the proposed conclusion. Merely increasing precision on the accepted prefix does not supply the distribution. The written review further proves that, for this unchanged prefix/mu and worst-tail-weight estimate, even best admissible opposite low-form/Gram endpoints leave the cheap bracket straddling zero. This is not a claim that a distribution-sensitive bound or the actual exact reference must fail.

The complete written argument is in F-20261023-001. This work changes no prior finite negative conclusion and proves no exact-reference, true Schur or Weil sign. Original A/G trust remains generator-source-qualified; source identity and local Suzuki/Arb hypotheses remain external analytical premises. No new analytical evaluator, general framework, Rust certificate, Lean proof or admission is created. Admissions remain eight v1, zero v2 and one v3; RH unresolved.
