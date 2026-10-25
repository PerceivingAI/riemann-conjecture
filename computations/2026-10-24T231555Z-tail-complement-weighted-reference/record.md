# Complete weighted reference with the tail-restricted residual complement

- **Computation ID:** `X-20261024-006`
- **Created:** `2026-10-24T23:15:55Z`
- **Last updated:** `2026-10-24T23:28:30Z`
- **Status:** `COMPLETE`, negative reference directions in both parity sectors
- **Finding:** [F-20261024-008](../../findings/2026-10-24T231555Z-tail-complement-weighted-reference.md)
- **Claim:** C-0089

## Objective

Determine whether the stronger C-0088 tail complement supports the complete weighted reference at its first even scalar-reserve dimension N16, at the existing support T=1353/2048. Assess both whole8-dimensional parity blocks with complete signed low/Gram/head inputs, physical masses, full residual and cross errors. A positive scalar complement alone is not a successful reference.

The executed answer is negative. Both reference directions have genuine exact uppers below zero. A further reviewed monotonicity control shows that eliminating only the residual norm charge entirely would not rescue this same fixed-N scalar-reference family. No longer head, larger dimension or new support was run.

## Environment and provenance

`environment.json` records actual Python3.14, python-flint, NumPy, pytest, platform and precision. This Windows x64 PC executed one scientific process at a time, without WSL, a GPU or external compute. The baseline main commit is `62f33b6f66f7e446a99a68f1a41bfa137f51592c`; the preexisting uncommitted C-0088 work was preserved. New scripts were uncommitted during execution. This is not clean-source production proof generation.

Source low/head precision is768 bits; independent reconstruction1536 bits. Source dyadic publication uses352 bits, independent receipt publication512 bits. All decisions and witness checks use exact rational bounds. Floating computation only proposes trial vectors and possible congruences; no floating sign is accepted as evidence.

`source-v1/` captures22 source/environment files and binds them with its manifest. Historical producer, auditor, exact matrix consumer, kernel helpers and tests were not modified. The separate new producer is `scripts.weil_tail_complement_assessment`; the separately implemented auditor is `scripts.verify_tail_complement_inputs`.

## Fixed parameters and selection

T=1353/2048,N16,K38, active[2,3], ordinary unnormalized Legendre basis, d_j=2/(2j+1). C-0088 supplies the exact available scalar lower mu, displaying0.25554921158237676. This is stronger than the original reserve0.18491998558724346; the latter is a minimum requirement, not the reference parameter used here.

The source and native auditor independently reconstruct the tail smoothing constant, complete remainder and new complement. The full cross norm remains b=pi/2+p+rho_global. Only the double-tail residual norm is sharpened. C-0085's complete residual allowance remains delta*(1+2b/mu)+delta^2/mu.

The initial head boundary is the smallest even m>=N+K satisfying the old accepted inverse-weight cap. This selects m54. A geometric accuracy ladder m_next=N+2*(m-N) was defined before execution, but never advanced because the initial reference assessment was already conclusively negative. Increasing m cannot change the sign of the same exact reference.

All2099 analytical slots are fresh:272 low/Gram triangular entries,1824 V/P/RK head slots and3 scalar/cross bounds. The16 exact residual images agree independently and have maximum degree53. Thus m54 contains all finite RK head rows; the infinite source tail and full R_T-R_K error remain accounted for. The exact arithmetic consumer's internal legacy `R32` slot receives the declared RK data; the actual source order remains38.

Pinned dependencies are retained in `data/baseline-selection-v1.json` and `data/prior-scalars-v1.json`. Their original public artifacts are the C-0087 [selection](../2026-10-24T191616Z-weighted-support-extension/data/selection-v1.json), SHA256 `e120acab4919b9ab28e6fd6c7044053bb14514f300d810952a2d52e5dae6d7a3`, and C-0088 [scalars](../2026-10-24T224948Z-tail-restricted-residual/data/scalars-v1.json), SHA256 `65cc22df9e5edfbaebd9b183edbc29b179c7d3474731e24170cc9abc543a0b9a`. No old analytical array is reused.

## Reproduction procedure

Run from the repository root with the locked dependencies and a fresh, already-created output directory. Each output refuses overwrite:

```text
uv run --locked python -m scripts.weil_tail_complement_assessment select --output computations/<fresh-bundle>/data/selection.json
uv run --locked python -m scripts.weil_tail_complement_assessment generate --boundary 54 --output computations/<fresh-bundle>/data/source.json.gz
uv run --locked python -m scripts.verify_tail_complement_inputs computations/<fresh-bundle>/data/source.json.gz --output computations/<fresh-bundle>/data/audit.json.gz
uv run --locked python -m scripts.weil_tail_complement_assessment assess --packet computations/<fresh-bundle>/data/source.json.gz --audit computations/<fresh-bundle>/data/audit.json.gz --output computations/<fresh-bundle>/data/result.json
uv run --locked python -m scripts.weil_tail_complement_assessment replay --packet computations/<fresh-bundle>/data/source.json.gz --audit computations/<fresh-bundle>/data/audit.json.gz --result computations/<fresh-bundle>/data/result.json --output computations/<fresh-bundle>/data/replay.json
uv run --locked --extra test python -m pytest -n 0 -q tests/test_tail_complement_assessment.py
```

`residual-only-limit-v1.py` is a separate deterministic diagnostic CLI, not an alternative acceptance mode. Pass it the accepted packet, audit and result using `--packet`, `--audit`, `--result`, and a fresh `--output`. It keeps the full source but evaluates a more optimistic hypothetical reference. Its invocation is retained in `data/residual-only-limit.run.json`.

For isolated historical regeneration and exact replay:

```text
uv run --locked python computations/2026-10-24T231555Z-tail-complement-weighted-reference/replay-archived-v1.py --output-dir computations/<fresh-replay-directory>
```

The launcher verifies captured source bytes, restores the two pinned inputs and code into an isolated tree, checks that loaded project scripts originate there, regenerates analytical arrays, independently audits the original packet, replays the original exact result and reproduces the optimistic control. It uses the recorded installed dependencies rather than provisioning them. Scientific and binding fields match; only source/audit elapsed times are excluded from regeneration equality. The optimistic control JSON is byte-identical.

## Outputs

- Source: `data/source-m54-v1.json.gz`, SHA256 `8c7626b05e5f686155eca520d05c9908f829f3c78fbfe3cea900cd22b63da8af`.
- Independent audit: `data/audit-m54-v1.json.gz`, SHA256 `563f7ad158e7362d5417166c01b9a63e4289378961cc70c85f885c7c0d477335`.
- Exact result: `data/result-m54-v1.json`, SHA256 `ce6f31d8393452ee5d55b1c8e12049d8090b60556d1ab4c689d788a4d9c521d9`.
- Result status: `NEGATIVE_REFERENCE_DIRECTION`.
- Genuine full-reference uppers display-1.5426897127630486 even and-0.7551166256493715 odd. The exact rational values lie below-3/2 and-3/4 respectively. Trial physical squared norms display approximately1, not exactly1.
- Complete optimistic control: `data/residual-only-limit-v1.json`. Its scalar upper displays0.2557624475748877 and its reference uppers remain below-3/2 even and-3/4 odd.
- Exact replay: `data/replay-m54-v1.json`.
- Diagnostic copies and exact loss accounting: `data/result-summary.json` and `data/timing-error-summary.json`.

The even signed head inverse-energy lower displays3.49272 against full low-form upper1.95003. The odd comparison is2.10344 against1.34832. Directional omitted allowances are about0.09669 and0.06848, whereas negativity is already forced without them. The total whole-space omitted-tail allowance displays0.598339; it is not the value subtracted to prove the genuine negative uppers.

The full residual allowance is about1.4171807672134253e-13. One-sided A/U interval errors display1.35165e-104 and2.46567e-103. These error scales cannot explain order-one negative reference values.

## Optimistic residual-only control and its proof

Let mu_star=H16-cT-p and choose bar_mu>=mu_star by subtracting rigorous lower enclosures of cT and p from exact H16. A separately organized1536-bit native evaluation checks that the entire fresh mu_star enclosure is below bar_mu. No tail-domination claim at bar_mu is made.

The diagnostic changes only the reference parameter, never the signed source, R_T interpretation or delta. For every positive mu<=mu_star<=bar_mu, the diagonal reference and inverse ordering give S0(mu)<=S0(bar_mu). Both true-reference directional uppers at bar_mu are still negative. Hence reducing only a nonnegative residual norm charge in this fixed scalar-complement rule cannot rescue N16. Neither source arithmetic norms nor the positive potential contribution are sharpened by this control.

Separate read-only review accepted endpoint directions, inverse monotonicity and the complete reverse-triangle residual error. `independent-review.json` captures its final verdict. The reviewer did not run numerical jobs, tests or independent hash verification. The earlier form-order and geometric-refinement qualification was also supplied separately from the primary producer implementation.

## Executed verification

Actual source, native acceptance, assessment, exact replay, residual-only control and isolated regeneration all exit0. The4 focused regressions pass in1.29 seconds. They reject substituting the small tail norm into the full cross norm, altering both reference metadata copies, an optimistic scalar enclosure and a boundary outside the declared accuracy ladder.

Actual altered-reference-upper, changed-source/stale-audit and attempted refinement after a conclusive negative reference each exit2 without success output. Inputs, stdout/stderr and exact launch receipts are preserved, with outcomes in `data/rejection-summary.json`. These are research CLI semantics, not Rust verifier exit semantics.

Observed command durations in seconds: source0.6399912, independent audit0.6675638, assessment0.5015918, replay0.3336474, optimistic control0.3660813, isolated regeneration/replay2.4789704. These are this small negative assessment's costs, not a speedup measurement for the earlier successful N312 proof. No broad Python suite, Rust or Lean run is claimed.

## Interpretation and preservation

C-0088's scalar improvement is valid, but its first scalar-reserve dimension is not sufficient for this complete harmonic reference. The obstruction is resolved inverse-weighted source coupling, not head truncation, arithmetic precision or the small residual remainder. Even zeroing the tail residual norm charge would not fix this N16 scalar-reference family.

A negative lower alone would be inconclusive; this computation instead provides negative uppers for the actual chosen reference. Nevertheless S_true>=S0, so reference negativity proves neither true-Schur nor Weil negativity. C-0087's positive whole reference at the same support with N312 is unaffected. No method-wide failure, optimal dimension, support extension, comparative superiority, new admission, literature-priority or RH claim follows. Admissions remain8v1/0v2/1v3.

All preexisting research code, tests, source versions and sealed bundles remain unchanged. The bundle manifest binds retained source snapshots, exact inputs/results, reviewed diagnostic, numerical receipts, failed controls and reproduction launcher. Public records contain the mathematics and evidence needed to evaluate this completed assessment.
