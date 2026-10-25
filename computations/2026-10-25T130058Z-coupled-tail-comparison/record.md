# Coupled-tail comparison on the two complete P20 failing trials

- **Computation ID:** `X-20261025-003`
- **Created:** `2026-10-25T13:00:58Z`
- **Last updated:** `2026-10-25T13:16:42Z`
- **Status:** `COMPLETE`, both true-Schur directional lowers positive with full outside-tail control
- **Finding / claim:** [F-20261025-003](../../findings/2026-10-25T130058Z-coupled-tail-comparison.md) / C-0092
- **Revision:** local main baseline `ed6946669b459c261f7670a849d4cb3240ecfc48`, additive uncommitted sources captured exactly; no commit or push

## Objective and fixed geometry

Compare the unchanged C-0091 negative harmonic-reference trials with the retained coupled tail block E=degrees20..311 at T=1353/2048,N20,K38. The outside infinite tail F>=312 must remain paid. No support/projection grid or new analytical source is run.

The question is quantitative: how much does the diagonal model overpay inverse response on these specific trials, what retained stiffness does it omit, and how much outside-response uncertainty remains? Positivity of the full form at this support was already known from C-0087. This experiment does not claim a new support theorem.

## Qualified mathematics

The complete [pre-execution derivation](derivation-v1.md) and [qualification](mathematical-review.md) distinguish three objects: the harmonic inverse reference, the finite true C_E inverse and the full infinite true C inverse.

C-0087's accepted lower K312 bounds the complete Schur after eliminating F. Its inherited exact parity congruences give K312>=gD, with ordinary Legendre d_j=2/(2j+1). Domain-safe successive infima therefore give

```text
true S20(z) >= min_y (z,y)*K312*(z,y).
```

For any proposed y on E, let r=(K312*(z,y))_E. Completing the square with K_EE>=gD_E gives the certified lower qK(z,y)-sum_j r_j^2/d_j/g. Numerical solves produce proposals only. The exact residual, inherited coercivity and physical masses decide validity.

A separate finite response v gives a variational upper for the true Schur through the full form q(z,-v), enlarged by the full residual delta times its physical norm. A complete low-form bracket then encloses the full inverse energy a-S20. The finite inverse is independently bounded by its variational energy and its physical dual residual divided by mu20, including both low-to-tail and tail-to-tail source error. The outside excess I_true-I_E is nonnegative and has an explicit upper bound.

The fixed harmonic-response probe measures the retained stiffness h*(C_E-D0_E)*h. Its diagonal/off-diagonal components use the truncated source; their combined interval alone restores the full delta allowance. This directional quadratic diagnostic is not an additive attribution of inverse-energy gain or a new uniform operator-order result. A positive finite compression cannot be inserted into an infinite reference without controlling cross coupling.

## Accepted inputs and common authority

[inputs/manifest.json](inputs/manifest.json) binds36 exact retained files totaling47295789 bytes, including original-v2 C-0087 data/code/baselines and C-0091's bound original-version gate, negative-reference report, consequence receipt and seal. No old byte is changed or reinterpreted through the later version3 validator.

The common upstream loader validates these identities, uses the unchanged legacy weighted matrix kernel to reconstruct the accepted K312, restores the original full C-0085 residual charge and re-verifies both old exact congruences and mass-normalized gaps. The independent new auditor shares **this already accepted upstream reconstruction**, not the producer's new comparison formulas. It is an independent consequence check, not a fresh independent analytical audit of the original758475 inputs.

Original source/native interval storage remains352/512 bits. All full source errors and the complete infinite tail remain paid. Source conditioning and original high-precision analytical acceptance remain the distinct C-0087 evidence.

## Source versions and regression failure

New consumers are [weil_coupled_tail_comparison.py](../../scripts/weil_coupled_tail_comparison.py), SHA256 `1a1a82207870cb063f213274f2021f27bbde7859f45838103b4220cade0f10ad`, and [verify_coupled_tail_comparison.py](../../scripts/verify_coupled_tail_comparison.py), SHA256 `36116eff01132e98516206091880917e9613d6a60c89a9f4a8933131c782c860`.

The initial focused run passed one regression and failed the other because flint fmpq does not support `>` against Fraction. The mathematical result 2/3 was correct; the test harness needed an exact conversion before comparison. [source-v1/manifest.json](source-v1/manifest.json), the original test and captured failure remain intact. [source-v2/manifest.json](source-v2/manifest.json) captures the corrected bridge. No producer/auditor mathematics or historical test was changed. Numerical assessment was gated on the corrected run, which passes both regressions.

The regressions cover physical dual residual completion, exact elimination, full residual perturbation, and a finite example where the outside mode raises inverse response from1/2 to2/3. They prevent treating the finite inverse as a full inverse.

## Actual execution

Windows11 build26300, Python3.14.0 x64, python-flint0.9.0, NumPy2.5.2 and pytest9.1.1, with complete package/runtime details in [environment.json](environment.json). CPU-only, one mathematical subprocess at a time. Proposals are rounded to a fixed2^80 grid; all decisive calculations use exact outward352-bit rational endpoints.

The following commands ran from the repository root in the locked virtual environment. Use fresh filenames for reproduction.

```text
uv run --locked --extra test python -m pytest -n 0 -q tests/test_coupled_tail_comparison.py
uv run --locked python -m scripts.weil_coupled_tail_comparison analyze --output computations/2026-10-25T130058Z-coupled-tail-comparison/data/comparison-v1.json
uv run --locked python -m scripts.verify_coupled_tail_comparison computations/2026-10-25T130058Z-coupled-tail-comparison/data/comparison-v1.json --output computations/2026-10-25T130058Z-coupled-tail-comparison/data/independent-audit-v1.json
uv run --locked python -m scripts.weil_coupled_tail_comparison replay --result computations/2026-10-25T130058Z-coupled-tail-comparison/data/comparison-v1.json --output computations/2026-10-25T130058Z-coupled-tail-comparison/data/exact-replay-v1.json
```

The corrected test run and all three mathematical commands exit0. Assessment takes7.96184 seconds, independent audit10.21715 and replay8.01728. The result is `BOTH_TRUE_SCHUR_DIRECTIONS_POSITIVE`; audit is `INHERITED_INPUT_CONSEQUENCES_ACCEPTED`; replay is `EXACT_COUPLED_TAIL_REPLAY_PASS`. These are inherited-consequence costs including old K verification, not fresh analytical or production proof costs.

The auditor independently checks46 scalar fields and1752 response coordinates using Fraction interval loops. It verifies unchanged physical trials, both10-coordinate low parity inventories, all146+146 tail coordinates, three response vectors per trial, fixed harmonic quantization, exact residual bounds, finite/full inverse separation, source error and signed stiffness. The parent and independent implementer both qualified the inequalities before execution; the implementer ran no tests or numerical jobs.

## Directional results

| Parity | Harmonic-reference upper | True-Schur lower | True-Schur upper | Reference-loss lower |
| --- | ---: | ---: | ---: | ---: |
| Even | -1.24680669473969e-5 | 3.98712016963808e-5 | 4.05773002085533e-5 | 5.23392686437777e-5 |
| Odd | -4.17544391746990e-8 | 6.46271561971094e-8 | 6.53072619327084e-8 | 1.06381595371808e-7 |

Physical trial squared masses remain approximately1, without renormalization. The exact residual penalties are about2.44057608e-25 and1.67866814e-30. Positivity is not inferred from floating-point proposal eigenvalues.

| Parity | Finite inverse interval, display | Full inverse interval, display | Outside excess upper |
| --- | --- | --- | ---: |
| Even | [1.43847517587431e-5, 1.43847517587735e-5] | [1.43847517525498e-5, 1.50908502709308e-5] | 7.06098512187744e-7 |
| Odd | [3.71119231215178e-8, 3.71119231231855e-8] | [3.71119169138796e-8, 3.77920288579506e-8] | 6.80105736432798e-10 |

The full brackets are conservatively wider than the finite ones. The outside-excess upper is below1.35% even and0.64% odd of the certified reference-loss lower. This comparison does not assign those percentages as unique causal shares.

| Parity | Truncated diagonal stiffness increment | Truncated signed off-diagonal increment | Full total stiffness, approximate |
| --- | ---: | ---: | ---: |
| Even | 2.41165278995451e-4 | 5.97612892885851e-5 | 3.00926568284036e-4 |
| Odd | 4.21580512582700e-7 | 7.90654170753935e-8 | 5.00645929658094e-7 |

The report stores lower/upper endpoints, not these displays. Both signed off-diagonal contributions are positive on the selected probes; no separate-prime attribution or claim that off-diagonals always help is made.

## Actual rejection controls

[run-controls-v1.py](run-controls-v1.py) executes five modified reports with the same source/inputs. All exit2 and leave no success receipt, as recorded in [data/rejection-summary.json](data/rejection-summary.json):

1. Substitute an uncertified larger coercivity gap.
2. Set the outside-tail excess allowance to zero.
3. Relabel the finite inverse upper as the full inverse upper.
4. Remove the Schur residual penalty from the certified lower.
5. Erase the positive signed off-diagonal stiffness interval.

All original and rejected reports, stdout/stderr and actual command/timing receipts remain retained. No original packet or old validation rule is weakened.

## Isolated captured-source replay

```text
uv run --locked python computations/2026-10-25T130058Z-coupled-tail-comparison/replay-archived-v2.py --output-dir <new-directory>
```

The launcher restores22 captured source/environment files and36 exact inputs in a temporary root, checks all hashes and imports no live project script. Its wrapper checks origins even for modules returning SystemExit0. It reproduces the exact replay receipt byte-for-byte and every independent audit field except elapsed time. The actual run exits0 in18.43099 seconds with `ARCHIVED_COUPLED_TAIL_REPLAY_PASS`; artifacts are in `data/archived-replay-v2/`.

| Core artifact | SHA256 |
| --- | --- |
| Comparison | `e21b06e294f3a35a3d8870697b297a98551a2bf2d4106ce47bcaa1fbec5c7550` |
| Independent audit | `7e1eae38096dbf8f6737bb4862f530297f87ab8e1df0ac19b007786135c6b2a1` |
| Exact replay | `f972d4e3a37b353e860f61c4a3077c9598919f802d38109d0fa723fbcd52956e` |

No broad Python suite, Rust or Lean check was run. The bundle's manifest is published last and binds all preserved versions, data and controls.

## Interpretation and circularity boundary

The negative P20 harmonic reference is materially more pessimistic than the true coupled response on both unchanged trials. The retained finite block explains a large, measurable response difference while the remaining outside uncertainty is explicitly small relative to the certified loss. Both diagonal and signed off-diagonal stiffness omitted from the model matter on the probes.

This is quantitative diagnosis, not a new proof of positivity: it deliberately depends on already positive complete K312. It supplies no smaller-data certificate, new support, chosen coupled-block size, uniform improved P20 reference or demonstrated cost reduction. A uniform change needs all low directions and complete outside-cross control, not only these two probes. The new calculation cannot be used to claim that a principal positive stiffness correction is automatically dominated by the infinite operator.

No RH-equivalent premise is introduced to force the outcome. All historical procedures, source bytes, findings and theorem artifacts remain intact. Admissions remain8v1/0v2/1v3, RH unresolved.
