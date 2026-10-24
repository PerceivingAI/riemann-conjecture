# Fixed complete joint-source tail and concentration consequence

- **Computation ID:** `X-20261023-003`
- **Created:** `2026-10-23T18:52:53Z`
- **Last updated:** `2026-10-23T19:02:50Z`
- **Status:** `COMPLETE`, evaluated bound remains `INCONCLUSIVE`.

## Objective and mathematical quantity

Enclose the complete Q_224 tail of the original signed source at T=3/5,N=192,K=32 and compare C-0077's joint bound with the earlier model/control. The exact odd trial, active terms [2,3], retained prefix ending before 211 and source hypotheses are unchanged. Compute G,C,regular-tail and the directly formed tail of Vu+q by whole norms minus 112 odd head coefficients. Restore the full residual after the square root and evaluate the retained one-sided concentration predicate.

The mathematical derivation, evaluated values, fixed-index limitation and trust boundary are in [F-20261023-005](../../findings/2026-10-23T185253Z-joint-source-tail-enclosure.md), C-0079. This is a complete infinite-tail scalar via projection, not a finite high-tail sum, full matrix, inverse, sign-resolving result or theorem admission.

## Environment and provenance

- Source baseline: `acc63ac6d41138280236850c3fbc586e20998cc4`, with pre-existing uncommitted research plus the new uncommitted consumer. Not a clean-source theorem producer.
- Python 3.14.0, python-flint 0.9.0, Windows on the existing PC. Exact environment is in [execution.json](data/execution.json).
- Generator: fixed 1536-bit Arb; separately organized reconstruction: fixed 3072-bit Arb; publication: fixed outward 352-bit dyadic intervals. This pair was declared before the first run, not a precision ladder or retry.
- Executed consumer SHA-256: `04ccd864c4a350767291d1751d499a39325a40ffdd843f827fbac59d56d40dde`.
- Input/source raw-byte fingerprints are in [result.json](data/result.json); its SHA-256 is `67eba074fdc79e48934fbb2ae80212fa920f62bddc6a324e500bf8c4a296c2c8`.
- [contract.json](data/contract.json) was retained before execution. Its source snapshot matches the live consumer's executed bytes.

All source/method versions and preceding computation bundles remain separate. The older replay consumer still computes only its recorded model/control. No migration or replacement of historical records is performed.

## Inputs

SHA-pinned packets:

1. Original trial, mu and one-sided A/G premises: `computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json`.
2. Accepted source constants, norm, residual degree/error and nine V/P2/P3/R32 moments: `computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json`.
3. Retained h and omitted-mass lower: `computations/2026-10-23T105408Z-directional-loss-review/data/loss-audit.json`.
4. Earlier comparison control: `computations/2026-10-23T174341Z-jump-refinement-controls/data/canonical-result.json`.

No new trial, support/dimension grid, prefix selection or residual order is introduced. The newly evaluated heads are projection bookkeeping for the same scalar tail, not a replacement accepted prefix.

## Reproduction procedure

From repository root, using the locked project environment:

```text
uv run --locked python -m scripts.weil_joint_source_tail
```

Frozen exact consumer snapshot, using the same repository dependencies:

```text
uv run --locked python computations/2026-10-23T185253Z-joint-source-tail/data/source/weil_joint_source_tail.py
```

For that direct-file invocation, set PYTHONPATH to the repository root if the shell does not already provide it. The canonical module command avoids that requirement.

Historical reproduction requires the recorded dependency bytes, not whichever production modules exist later. Use an isolated copy at the baseline revision with these retained inputs and new source files. If production consumers have changed, populate `scripts/weil_joint_source_tail.py` from this bundle's snapshot and `scripts/weil_jump_refinement_check.py` from [its earlier retained snapshot](../2026-10-23T174341Z-jump-refinement-controls/data/source/weil_jump_refinement_check.py). Their hashes must match the recorded source identities. Do not restore old code over a working tree containing unrelated work. The exact consequence replay deliberately checks those original source paths too.

Exact rational consequence replay, which does not reconstruct analytical source inputs:

```text
uv run --locked python computations/2026-10-23T185253Z-joint-source-tail/data/source/consequence-check.py computations/2026-10-23T185253Z-joint-source-tail/data/result.json
```

These commands print to stdout. Do not overwrite retained outputs on replay; capture to a new destination. The module has no support, precision or cutoff options and verifies input identities before numerical construction. Missing, changed or rejected inputs return exit 2. No automatic fallback or retry.

## Output and acceptance

[The result packet](data/result.json) retains all 15 published scalar intervals, 336 published normalized V/q/s head intervals and their raw reconstruction endpoints. It is below the protocol's 2 MiB threshold. All 351 full containments passed, along with 18 checks against the earlier accepted V/q prefix and the older complete step-tail model. Generator two-cell/Horner/grouped contractions and reconstruction four-cell/Taylor/per-monomial contractions have shared Arb and projection-algebra dependencies.

- Complete truncated joint tail near 0.7050419736007247.
- Full collective-residual upper near 0.7050419736007582, strictly below the previous separate control 6.664365418102699.
- Signed full mixed tail C near -5.035764911900693; this is not the older arithmetic-only mixed upper.
- Positive concentration correction near 0.2804530089619544.
- Positive, inconclusive directional upper near 1.3818804654839518.

[The separate rational result](data/consequence-result.json) reproduces the exact weight and predicate and validates the full residual upper by squaring a nonnegative rational remainder. Reverse triangle gives a full-tail lower exceeding 7/10. Consequently any valid tail cap in this same L=224 concentration formula produces a reported upper exceeding 69/50. This is not a lower bound on the actual reference; it diagnoses loss in that fixed formula, not source failure or a general no-go.

## Execution and ownership

| Owned direct child | Exit | Wall seconds | Meaning |
| --- | ---: | ---: | --- |
| Canonical joint evaluation, including reconstruction | 0 | 11.994052800000645 | Source enclosures accepted; final predicate inconclusive |
| Exact consequence replay | 0 | 0.23110089998226613 | 351 containments and rational consequences accepted |
| Changed-first-input smoke | 2 | 0.2553156000794843 | Expected fail-closed rejection before numerical work |

Each child had a 60-second cap and confirmed exit; no timeout or retry. New charge 12.480469300062396 seconds; prior charge 4.620344400056638; cumulative 17.100813700119033/180 seconds. No external compute, parallel worker pools or OS-wide process-tree guarantee is claimed. Captured stdout/stderr are retained as UTF-8 LF text, not asserted to be raw OS pipe bytes.

The changed-input smoke used a removed disposable working directory with first input set to the three UTF-8 bytes `{}\n` and repository PYTHONPATH supplied. It returned empty result stdout and the specific input-identity diagnostic recorded in execution.json; the originals were untouched. A parent-side display initially lacked a Fraction alias after the numerical output was captured; correcting that display did not rerun the numerical child or change its successful output.

## Limits and evidence preservation

Independent mathematical/static implementation review passed, including the lower-tail argument. It did not rerun the numerical construction. The standard-library consequence checker validates exact consequences of the source packet, not the source mathematics itself. No fresh checkout, full test suite, Rust/retained-proof replay or Lean build was exercised.

Original A/G remains generator-source-qualified; new source-image scalar acceptance does not retroactively reconstruct it. The Suzuki identities, Arb arithmetic and local 2T<pi source/residual premises remain trusted. Actual reference, true Schur and Weil signs are unknown. RH and the eight v1/zero v2/one v3 admissions are unchanged.

The manifest is written last and binds exact sizes/hashes of all bundle members except itself. The canonical source snapshot and exact consequence procedure are distinct retained executed methods. Earlier research sources, outputs, conclusions and schemas remain untouched.
