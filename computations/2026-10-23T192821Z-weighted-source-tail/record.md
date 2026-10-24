# Weighted-tail investigation and positive reference direction

- **Computation ID:** `X-20261023-004`
- **Created:** `2026-10-23T19:28:21Z`
- **Last updated:** `2026-10-23T19:45:46Z`
- **Status:** `COMPLETE`. Corrected source v2 returns `POSITIVE_DIAGONAL_REFERENCE_DIRECTION`; source v1 is a preserved implementation failure, not a mathematical outcome.

## Objective and quantity

Resolve the preserved trial's diagonal-reference direction using the actual inverse weights, with complete infinite-tail and full residual control. First assess the scalar harmonic-Cauchy estimate, then retain the same source's weighted spectral distribution when that scalar compression is too weak.

Fix T=3/5,N=192,K=32, active [2,3], original exact odd trial and exact rational mu. The original accepted prefix ends before 211; the residual polynomial has degree 223. No low-space dimension, trial, support, arithmetic term, reference or source formula changes.

[The finding](../../findings/2026-10-23T192821Z-weighted-source-tail-reference.md), C-0080/C-0081, gives the full derivation, domain proof, interval directions, failed scalar-rule assessment and resolved directional sign.

## Environment, versions and input identity

- Python 3.14.0, python-flint 0.9.0, pytest 9.1.1, Windows on the existing PC; exact platform and receipts in [execution.json](data/execution.json).
- Source baseline `acc63ac6d41138280236850c3fbc586e20998cc4` plus preserved pre-existing research and this new uncommitted consumer. Not a clean-source theorem producer.
- [Initial source v1](data/source/weil_weighted_source_tail.py), SHA-256 `05c744958e5e433afec9b572f02602f2a66922ace70aeb69a9fe4a1d7d71539c`.
- [Corrected source v2](data/source/weil_weighted_source_tail-v2.py), SHA-256 `7dddb9ce9b75c2bf30ccf8af4b3002828ea080cae3443aed624c1b4493f0c2c6`, matching the live canonical consumer's exercised bytes.
- [Corrected result](data/result-v2.json), SHA-256 `92cf2dbc31326167c34f795f72dff394efb57430c24f14d23706d73da63df667`. Its generator, reference and consequential endpoints remain exact rational enclosures.

Pinned inputs are the original SYS-6.4 trial packet, the accepted directional-source packet, the directional-loss audit, and the C-0079 joint-source result. Exact paths/hashes and dependency fingerprints are in result-v2.json. These inputs and their source modules are unchanged. Newly reconstructed data include one physical a scalar, not the original full A/G matrices.

## Predeclared accuracy and source operation

[The accuracy selector](data/source/select-accuracy.py) was executed before evaluating new source coefficients. It selected the smallest even B>=224 satisfying w_B*M224_upper<=h/4, obtaining **B=874**. The budget is about 0.4155833686 and the a-priori tail ceiling about 0.4151029307. This is a fixed error allocation, not a sign-based cutoff scan. No finite A-U_874 matrix is evaluated.

Precision was selected once by ceil-to-256(4B+512): generator 4096 bits, reference 8192 bits. Primary publication is outward 352 bits. Reference receipts are outward 512-bit enclosures of the much narrower raw reference intervals; both raw and rounded reference containments were required. The packet does not claim to retain all raw 8192-bit endpoints.

The generator uses the existing exact high-potential coefficient identity, Horner shifts, two doubled positive cells, scalar grouped potential moments and original exact residual action. The independently organized reference uses global monomial potential moments, Taylor shifts, four signed cells and separately coded exact residual action. Both share Arb, source identities, some polynomial primitives and projection algebra.

[contract.json](data/contract.json) and the initial source snapshot were retained before the first source execution. [contract-v2.json](data/contract-v2.json) and the corrected snapshot were retained before the corrected execution. The mathematical inputs, B and precisions are identical between source versions.

## Method and complete error accounting

For b=Q224(V+P)u, the harmonic energy D is finite by the reviewed coefficient decay and finite jump-aware variation. Scalar Cauchy gives J_b>=M^2/D, but a finite-band lower D_- also bounds this expression above by M_+^2/D_-. Its evaluated ceiling cannot make the specified scalar rule certify negativity. D itself and a target D_+ were not computed because that extra integral was unnecessary for this assessment.

For the complete weighted comparison, normalized signed V+P+R32 source coefficients are evaluated at k=211,213,...,873. The residual polynomial contributes through k=223 and vanishes only afterward. The accepted M224 minus resolved high-band mass pays the entire remaining source tail. The complete truncated inverse energy is bracketed by S and S+w_B*T_B.

One norm triangle restores the full residual in the bounded inverse-weighted norm using delta*sqrt(w211)*||u||. No harmonic-energy bound on the omitted residual is assumed. The physical scalar a is independently reconstructed with full error +/-delta*||u||^2; prefix endpoints retain their correct opposite roles. Old valid bounds are intersected, never added over overlapping modes.

## Outputs and acceptance

- 2 scalar and 1328 head raw-reference containments passed, as did their rounded-reference counterparts and 14 older joint-head compatibility checks.
- Full J at k>=211 lies near [0.8118726377190583,1.036603900014265].
- The exact reference direction lies near [0.6257295744306691,0.8504608367268481], strictly inside (3/5,9/10).
- The source harmonic moment has lower above 0.9120232714. The scalar Cauchy expression has upper below 0.5450345404, leaving a positive reported-upper floor above 0.8071149546 for that scalar rule. This is not an upper on the actual inverse energy.
- C-0072 inverse ordering transfers the strict reference lower to the true Schur quadratic value on the same trial. No direct true-inverse value or whole-matrix positivity is computed.

The producer's undetermined true-Schur/Weil flag concerns the overall form/operator sign. The finding explicitly supplies the distinct directional order-transfer consequence. Do not read that global flag as leaving this trial's true-Schur directional sign unresolved.

## Preserved implementation failure and correction

The initial canonical run returned exit 2 after hitting Python's 4300-digit integer-to-text limit. Its [result stdout](data/result.json) is deliberately empty, not a valid JSON result; [stderr](data/stderr.txt) records the rejection. No numerical sign is assigned to this run.

The [minimal finite-spectral reproduction](data/source/rational-repro.py) isolated exact consequence serialization, with [traceback](data/rational-repro-stderr.txt). [Two behavioral regressions](data/source/test_weighted_source_tail.py) then failed before correction and passed afterward. Their fixtures have known finite spectral energies and cover zero and nonzero collective residual error; they are not claimed Weil-source reconstructions.

The cause was unnecessary exact denominator growth from summing many unrelated inverse weights, plus unbounded-size high-precision consequent endpoints. V2 rounds each weighted term and consequential endpoint outward on the fixed 352-bit dyadic grid. This preserves the rigorous inequality directions while keeping exact rational endpoint sizes bounded. The Python guard was not raised or disabled. No exception was suppressed and no source interval was weakened to force a sign.

The corrected canonical execution returned 0. Versions, contracts, failures, tests and outputs remain separate; no old method or result was overwritten. Reproducing the old failure requires the archived v1 consumer in an isolated source copy, not invoking the reproduction against today's v2 module and calling that historical reproduction.

## Reproduction commands

From repository root with the locked environment:

```text
uv run --locked python -m scripts.weil_weighted_source_tail
uv run --locked --extra test python -m pytest -n 0 -q tests/test_weighted_source_tail.py
uv run --locked python computations/2026-10-23T192821Z-weighted-source-tail/data/source/replay-weighted.py computations/2026-10-23T192821Z-weighted-source-tail/data/result-v2.json
```

The first command performs source evaluation; the last uses only the standard library and checks serialized interval containments, minimal boundary selection, per-term directed accumulation, physical low-form/prefix endpoints, exact algebraic residual predicates and the strict positive bracket. It does not reconstruct analytical source inputs.

To reproduce historical source versions, use an isolated copy at the baseline with retained inputs and original dependency bytes. The earlier new consumers are retained in X-20261023-002/003; the weighted v1/v2 snapshots are separate here. Restore the intended version only in that isolated copy. Set PYTHONPATH to its root for direct-file snapshot invocation. Do not overwrite a live working tree or retained outputs. The v2 exact replay checks this bundle's v2 snapshot hash and the original dependency/input identities, not the mutable live weighted consumer's bytes.

The module has no numerical parameter options and writes its result to stdout. Capture replays separately. A changed first input was rejected at exit 2 with empty stdout before numerical work, in a removed disposable directory. Exact fixture bytes and diagnostics are in execution.json; original inputs were untouched.

## Execution, review and charge

| Owned direct execution | Exit | Wall seconds |
| --- | ---: | ---: |
| accuracy-selection | 0 | 0.1346206000307575 |
| canonical-weighted-source-evaluation | 2 | 36.63808289996814 |
| minimal-rational-failure | 2 | 0.38045990001410246 |
| regression-before-rounding-fix | 1 | 2.0677490999223664 |
| regression-after-rounding-fix | 0 | 1.3022569000022486 |
| canonical-weighted-source-v2 | 0 | 33.53869980003219 |
| independent-exact-weighted-replay | 0 | 0.2587158000096679 |
| altered-input-smoke | 2 | 0.32665379997342825 |

All eight direct executions exited, no timeout. Each had a 60-second ceiling. New charged execution **74.6472387999529 s**, including failed work and regressions; prior analytical-cycle charge 17.100813700119033 s; cumulative **91.74805250007194/180 s**. One explicit implementation-corrected run was performed, not a precision or cutoff retry. No external compute or OS-wide process-tree claim.

Independent read-only mathematical/static review accepted the source/domain arguments, Cauchy assessment, complete bracket, physical normalization, directed-rounding correction and true-Schur directional transfer. It did not run numerical code. The separate exact replay accepted all 1330 containments and proved the strict reference bracket using squared integer/rational predicates, with no Arb import.

No full Python suite, full A/G matrix reconstruction, dense inverse, Rust/retained-theorem replay, Lean build, certificate/admission change or support theorem. RH remains unresolved; admissions remain eight frozen v1, zero v2 and one v3 C-0067. The new manifest is written last and excludes only itself; older research and source bytes remain preserved.
