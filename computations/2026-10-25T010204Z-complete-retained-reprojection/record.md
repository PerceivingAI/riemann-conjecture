# Complete P20 harmonic-reference assessment from retained larger tensors

- **Computation ID:** `X-20261025-002`
- **Created:** `2026-10-25T01:02:04Z`
- **Last updated:** `2026-10-25T01:20:21Z`
- **Status:** `COMPLETE`, source-conditional negative reference directions in both parity sectors
- **Finding / claim:** [F-20261025-002](../../findings/2026-10-25T010204Z-complete-retained-reprojection.md) / C-0091
- **Revision:** local main baseline `ed6946669b459c261f7670a849d4cb3240ecfc48`, additive uncommitted sources captured exactly; no commit or push in this operation

## Objective and fixed parameters

Assess the **entire** P20 reference selected after C-0090's positive old-P16 compression. Include degrees16..19, all their cross couplings and both10-dimensional parity blocks. Keep T=1353/2048,K38, selected mu20 displaying0.4726350157991974 and existing head boundary1018. No larger projection/support grid is run.

The accepted C-0087 original low dimension M312 already contains every needed low entry and source pairing. This operation derives new consequences of that evidence rather than generating another analytical source.

## Mathematical contract

The [finding](../../findings/2026-10-25T010204Z-complete-retained-reprojection.md) gives the derivation preserved before execution in [derivation-v1.md](derivation-v1.md). Ordinary Legendre masses are d_k=2/(2k+1). For20<=k<312, source pairings are the off-diagonal A_M entries: the extra harmonic/c_T term is diagonal and cannot enter those rows. For312<=k<1018, sum signed V/P/RK component amplitudes before multiplication.

The complete new Gram is G20=G_M|P20+sum_(20<=k<312)t_k*t_k/d_k. With w_k=1/(mu20+H_k-H20), the full inverse-energy majorant is

```text
U = w1018 G_M|P20
    + sum_(20<=k<312) w_k t_k*t_k/d_k
    + sum_(312<=k<1018) (w_k-w1018) t_k*t_k/d_k.
```

Every coefficient is nonnegative; all infinite energy beyond1017 is paid through the Gram remainder. No prefix or sign correlation is discarded. The full R_T-R_K error delta and full cross norm b remain unchanged. The sharp double-tail norm is used only for mu20. A failed lower would be inconclusive; this assessment instead obtains genuine full-source directional uppers using finite energy lower bounds and the full residual reverse-triangle allowance.

## Original-version evidence and inputs

[inputs/manifest.json](inputs/manifest.json) binds32 exact input files totaling47165382 bytes. It includes the original source-v2 closure, old full-selection checker and selector, original selection/source/native receipt/result, their earlier baseline inputs, the C-0090 projection/receipt and C-0088 scalar input. Copies preserve original compressed and uncompressed bytes.

The original sealed C-0087 manifest SHA256 is `28eff565a893a54b5ae111e6b70dd92f46d9440b736aa8ac5469bdf3b487da92`. Its source SHA256 is `c9790a7b129aae0d410670830e8a472d639105d01884a041165fc119e627671e`; native receipt SHA256 is `e23fa00b66d5ebe5ccc261e23b886c10e2e4fdd3f816d9a8a3dcbca38282408e`.

The original-v2 full frozen-selection checker and exact replay execute in a restored, isolated old code tree. Source/native interval storage is352/512 bits. Their original analytical generation and independent acceptance remain the C-0087 evidence; the new Arb1536 evaluator performs interval consequences on those accepted tensors, not fresh transcendental reconstruction. The later version3 metadata validator is neither weakened nor called to reinterpret the old packet.

## Code and environment

New public consumers are [weil_complete_reprojection.py](../../scripts/weil_complete_reprojection.py) and [verify_complete_reprojection.py](../../scripts/verify_complete_reprojection.py). Their hashes are `efb9db0d98187d20ddf75a75d2e3de4875c722ae7e7da23a27955a099ade30ef` and `676fa27ecfff79c65c62398ab3e93dd195552aba7559a67f98992472ce1780f5`.

[source-v1/manifest.json](source-v1/manifest.json) binds20 captured source/environment files, including the new finite-operator regressions and unchanged dependency closure. Windows11 build26300, Python3.14.0 x64, python-flint0.9.0, NumPy2.5.2, pytest9.1.1, hypothesis6.165.10 and pytest-xdist3.8.0. Full details are in [environment.json](environment.json). No GPU/cloud runtime is used.

## Executed commands and observed outputs

Commands below use the same repository virtual environment as the captured receipts. Output files must be fresh; the consumers refuse overwrite.

```text
uv run --locked --extra test python -m pytest -n 0 -q tests/test_complete_reprojection.py
uv run --locked python -m scripts.weil_complete_reprojection origin --output computations/2026-10-25T010204Z-complete-retained-reprojection/data/original-v2-gate-v1.json
uv run --locked python -m scripts.weil_complete_reprojection analyze --origin computations/2026-10-25T010204Z-complete-retained-reprojection/data/original-v2-gate-v1.json --output computations/2026-10-25T010204Z-complete-retained-reprojection/data/complete-reference-v1.json
uv run --locked python -m scripts.verify_complete_reprojection computations/2026-10-25T010204Z-complete-retained-reprojection/data/complete-reference-v1.json --origin computations/2026-10-25T010204Z-complete-retained-reprojection/data/original-v2-gate-v1.json --output computations/2026-10-25T010204Z-complete-retained-reprojection/data/independent-audit-v1.json
uv run --locked python -m scripts.weil_complete_reprojection replay --origin computations/2026-10-25T010204Z-complete-retained-reprojection/data/original-v2-gate-v1.json --result computations/2026-10-25T010204Z-complete-retained-reprojection/data/complete-reference-v1.json --output computations/2026-10-25T010204Z-complete-retained-reprojection/data/exact-replay-v1.json
```

All commands exit0. Captured `.run.json`, stdout and stderr files give actual executable paths, arguments and measured timings. Focused tests:2 passed. Original gate: `ORIGINAL_V2_ACCEPTANCE_PASS`,16.02119 seconds. Assessment: `NEGATIVE_REFERENCE_DIRECTION`,2.84256 seconds. Audit: `RETAINED_INPUT_CONSEQUENCES_ACCEPTED`,7.09452 seconds. Replay: `EXACT_COMPLETE_REPROJECTION_REPLAY_PASS`,2.65776 seconds. These are retained-input consequence timings, not fresh analytical generation costs or a production verification benchmark.

The independent evaluator checks210 A and210 U upper-triangular entries, all998 combined rows20..1017, physical masses, correct H20 weights, complete omitted tail, scalar complement and full source error. It uses a different Gram organization: first enlarge G_M to G20, then apply the weighted correction. Both complete parity dimensions are10; neither block receives a positive lower witness.

| Parity | Physical squared mass, display | Full low upper, display | Full inverse-energy lower, display | Full-reference upper, display |
| --- | ---: | ---: | ---: | ---: |
| Even | 0.9999999999999972 | 5.49620519673116e-5 | 6.74301189147085e-5 | -1.24680669473969e-5 |
| Odd | 0.9999999999999998 | 1.02419185055060e-7 | 1.44173624229759e-7 | -4.17544391746990e-8 |

Exact rational grid trials and outward bounds are in the report. The negative conclusions concern the full reference, not just the conservative U lower matrix.

## Behavioral and adversarial controls

The two new finite-operator regressions enforce the restored20..311 prefix identity on a small exact model, signed component summation, physical high/low masses, correct harmonic rebasing and preservation of an unobserved tail. They do not alter previous tests.

[run-controls-v1.py](run-controls-v1.py) generated and exercised five distinct invalid inputs. [data/rejection-summary.json](data/rejection-summary.json) records exit2 and no success artifact for each:

1. Drop every restored low-cross prefix row while retaining the old high Gram.
2. Alter the newly included low degree19 diagonal.
3. Borrow the genuine old eight-dimensional witness to claim a complete ten-dimensional block.
4. Forge a stronger negative full-reference upper.
5. Relabel the original-version gate as source-v3.

The control command is preserved in `data/rejection-controls.run.json`; from the repository root it uses Python `runpy.run_path` to execute this bundle's retained procedure with `--bundle` pointing here. No old packet or validator is changed.

## Isolated reproduction

```text
uv run --locked python computations/2026-10-25T010204Z-complete-retained-reprojection/replay-archived-v1.py --output-dir <new-directory>
```

The [versioned launcher](replay-archived-v1.py) restores20 captured source/environment files and32 exact inputs in a temporary root. It validates every captured SHA, reruns the original-v2 gate, exact new consequence replay and independent native-receipt audit. Every loaded project script must originate within the isolated tree. It uses the preserved original gate for the report's exact byte binding; the newly executed gate must reproduce all non-timing/non-log acceptance fields.

The actual isolated run exits0 in27.39239 seconds with `ARCHIVED_COMPLETE_REFERENCE_REPLAY_PASS`. The exact replay receipt is byte-identical; every independent audit field except elapsed time matches. Evidence is in `data/archived-replay-v1/`. No fresh analytical source, broad Python suite, Rust or Lean check was run.

## Core hashes

| Artifact | SHA256 |
| --- | --- |
| Original-version gate | `9e7837dceefc3b3b35d0700077aec2157348c3610a07a82ccb9c76d83567ffcf` |
| Complete-reference report | `35468a0d04b26d3f94aff718f90009a42f260e7caa80dafbf50e56f71bce37c3` |
| Independent consequence receipt | `6729834e3c35bf85faf735da87865ea7db28636b90c4d8a2b46fbbb1f234920e` |
| Exact replay receipt | `990d7080cb5e4f3b55b5055f92ccdaef67246d750f729801b5690baab0fb21e2` |

The bundle manifest seals all retained members and is published last. It is an integrity/reproduction record, not theorem admission.

## Interpretation, circularity and limits

C-0090's P16-compression witnesses remain correct. The new result shows why they did not certify P20: promoting tail modes adds low coordinates and joint couplings that a principal-compression test cannot control. Reusing the old eight-dimensional witnesses would have missed a real full-space failure, and the actual control rejects it.

More head rows or precision cannot make this fixed exact reference positive. No blanket residual-only obstruction at N20, minimum dimension, true-Schur negativity, method-wide failure, literature priority or comparative efficiency is claimed. C-0087's positive N312 result at the same support remains intact. Its source-conditional smooth-test implication and C-0091's negative smaller sufficient reference are compatible.

No RH-equivalent premise is assumed to force a positive answer. The result rejects one reference at one support/projection. Production admissions, certificates, Rust/Lean boundaries and all historical research remain unchanged:8v1/0v2/1v3; RH unresolved.
