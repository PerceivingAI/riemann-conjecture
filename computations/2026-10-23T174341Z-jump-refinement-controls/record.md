# Jump-resolved mathematical controls and original-model comparison

- **Computation ID:** `X-20261023-002`
- **Created:** `2026-10-23T17:43:41Z`
- **Last updated:** `2026-10-23T18:10:37Z`
- **Status:** `COMPLETE` — fixed controls and arithmetic-model/control comparison, not the original full joint-tail evaluation or theorem admission.

## Objective and mathematical quantities

Check the signed jump decomposition, regular-remainder derivative bound, full-source correlation identity and collective residual accounting. On the unchanged original T=3/5,N=192,K=32 trial, compare its explicit jump model at L=224 and a separate retained-norm control. Mathematical derivation and limits: [F-20261023-004](../../findings/2026-10-23T174341Z-jump-resolved-tail-correlation.md), C-0077/C-0078.

## Environment and source provenance

- Existing project interpreter: CPython 3.14.0, python-flint 0.9.0, Windows.
- Small exact fixtures: Python Fraction. Log-potential controls: 256-bit generator, separately coded 512-bit checks. Original jump model/control: one fixed 512-bit precision.
- Source baseline `acc63ac6d41138280236850c3fbc586e20998cc4` plus the new uncommitted fixed replay consumer. Working tree was dirty; this is NOT a clean-source proof-generating run.
- Canonical consumer SHA-256 `73262f1dcf5ffcf88698f6e879e44aae27aa922c67af3049d7ac42163c2543a7`, retained at [data/source/weil_jump_refinement_check.py](data/source/weil_jump_refinement_check.py).
- Scoped Git attributes preserve the new consumer in LF and this bundle verbatim. Earlier artifact bytes/policies are not changed.

## Inputs and frozen parameters

1. Original trial packet `computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json`, SHA-256 `44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b`.
2. Accepted source constants/norm/residual metadata `computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json`, SHA-256 `9b9a1a0a0b420df0147f07c6fa1f5d9ee9005fb68dc8213cd8880d98556dd843`.
3. Existing scalar audit `computations/2026-10-23T105408Z-directional-loss-review/data/loss-audit.json`, SHA-256 `0a2458b5ead5245a439647b2a127ef267e7c8c98f11b9d4cfdb63b2bd49bcc18`.

The original support, dimension, trial, source formulas and accepted prefix are unchanged. L=224 is residual image degree plus one, not a search-selected source cutoff. The model uses complete step norm minus 112 odd head coefficients; it does not generate full q/source moments. Original A/G remains generator-source-qualified.

The separate rational fixture is u=x,tau=3/2,c=2, with fixed L=3,4,8,12. It is a formula/control fixture, not another investigated Weil support or trial.

## Reproduction procedure

From the repository root, canonical current command:

```text
uv run --locked python -m scripts.weil_jump_refinement_check
```

It has no support/dimension/precision controls and prints research JSON, not a certificate. Input bytes/source fingerprints are checked before its calculations. Exit 0 includes the scoped arithmetic cancellation/control result; exit 2 rejects malformed/changed/missing inputs. `SIGNED_CANCELLATION_CERTIFIED` is NOT a Weil or exact-reference sign.

For historical source identity rather than future live code, verify [data/manifest.json](data/manifest.json), restore the pinned source dependencies/lockfile in an isolated checkout, then execute the retained canonical snapshot from the repository root:

```text
uv run --locked python -c "from pathlib import Path; exec(compile(Path('computations/2026-10-23T174341Z-jump-refinement-controls/data/source/weil_jump_refinement_check.py').read_bytes(), 'retained-jump-check', 'exec'))"
```

The same retained-block invocation with `toy-control.py`, `model-v1.py` or `model-v2.py` reproduces their exact historical arithmetic. Canonical module execution is the supported research entry; source snapshots document the original procedures, not additional production APIs. Replays should produce new outputs, never overwrite this bundle. Internal timings need not reproduce exactly.

## Executed versions and retained output

- [toy-control.py](data/source/toy-control.py) / [toy-result.json](data/toy-result.json): 96 exact step-coefficient identities, 16 Gram identities, complete exact tail/derivative identities, full potential/source controls, nine separately coded cell containments plus one V2 containment, and two collective residual controls.
- [model-v1.py](data/source/model-v1.py) / [model-result-v1.json](data/model-result-v1.json): original arithmetic step-model and mixed-tail comparison at fixed L=224,512 bits. Preserved verbatim, including an unused drafting branch; that branch was never executed.
- [model-v2.py](data/source/model-v2.py) / [model-result-v2.json](data/model-result-v2.json): separate same-method extension adding the retained-norm full-source control and required-cap comparison; unused branch removed. v1 was not rewritten, retried at another precision, or treated as an independent reconstruction.
- [canonical source](data/source/weil_jump_refinement_check.py) / [canonical-result.json](data/canonical-result.json): maintained fixed consumer with explicit fail-closed checks; its exact numerical comparison fields matched v2.
- [execution.json](data/execution.json): all five process receipts, including changed-input smoke. The disposable first packet contained `{}\n`; exit 2 and empty result stdout specifically reported input-identity rejection. The temporary fixture was removed; original inputs were not touched.

Stdout/stderr were captured in text mode and retained as UTF-8 LF, not asserted to be raw OS pipe bytes. Historical script strings are retained exactly. Managed direct-child exit was confirmed; these controls spawn no descendants. No OS-wide process-tree claim is made.

## Output and interpretation

Original-model arithmetic mixed-tail upper is strictly negative, demonstrating actual cancellation between the signed step model and regular remainder. It does not include the additional potential/remainder correlation of the FULL new bound. The separate retained-norm full-source control strictly improves the old variation envelope but remains too large for the fixed negative-upper test. Exact rational endpoints are retained in the result JSON; the finding contains the display table and mathematical comparisons.

No original-trial G_L,C_L or regular-tail source enclosure was evaluated. No actual reference, true Schur or Weil sign follows. A fixture or model-control success is not full source acceptance, a new theorem or RH evidence.

## Cost and limitations

New charged execution, including canonical/integrity smokes: 2.438724899897352 s. Prior analytical-check use: 2.181619500159286 s. Cumulative **4.620344400056638/180 s**. Each managed process had a 60-second deadline, with no timeout or precision retry. The exact run-by-run values are in execution.json. Numerical version changes are distinguished from proof arguments and from implementation of the replay consumer.

No source image/matrix assembly, new full-source moment, full joint-tail evaluator, test suite, Rust verifier or Lean acceptance was executed. This is research evidence under the documented existing Suzuki/Arb and original A/G premises. No production admission changes; eight frozen v1, zero v2, one v3; RH unresolved.
