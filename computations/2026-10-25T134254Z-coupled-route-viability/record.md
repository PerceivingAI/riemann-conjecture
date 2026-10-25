# Viability assessment of the demonstrated dense coupled-tail construction

- **Computation ID:** `X-20261025-004`
- **Created:** `2026-10-25T13:42:54Z`
- **Last updated:** `2026-10-25T13:52:37Z`
- **Status:** `COMPLETE`, common-reference equivalence qualified and retained accounting executed
- **Finding / claim:** [F-20261025-004](../../findings/2026-10-25T134254Z-coupled-route-equivalence-and-viability.md) / C-0093
- **Disposition:** Narrow the demonstrated dense rearrangement to diagnostics. No evidence supports promoting it as a distinct primary continuation mechanism.
- **Revision:** local main baseline `ed6946669b459c261f7670a849d4cb3240ecfc48`; additive assessment artifacts only, with no commit or push

## Question and assessed scope

C-0092 measured substantial avoidable loss in the P20 diagonal reference. This assessment asks whether the particular finite coupled-tail construction supplies practical or mathematical leverage beyond the existing larger-projection method. It does not build another improved reference merely to obtain a positive result at an already positive support.

The assessed construction retains E=degrees20..311, the full M312 source and its accepted positive complete lower, with F>=312 paid by the same chosen outside reference in a fair comparison. No general impossibility of coupled-tail methods is assumed or concluded.

## General mathematical qualification

The [finding](../../findings/2026-10-25T134254Z-coupled-route-equivalence-and-viability.md) states the result. The [independent review](mathematical-review.md) gives the complete domain, coercivity and square-completion argument. The initial statement is preserved in [derivation-v1.md](derivation-v1.md).

Fix the same uniformly positive outside reference D for both methods, retain the same actual cross maps and finite source blocks, and use the C-0063/C-0072 domain inclusion. Eliminating F gives H_M=A_M-B_M*D^-1B_M. If G=(H_M)_EE>0, eliminating E gives the coupled low reference Schur_E(H_M). Thus

```text
H_M positive
    iff G positive and Schur_E(H_M) positive
    iff coupled tail positive and its low reference positive.
```

This is an elimination-order identity, not a stronger exact criterion. The same finite statement holds for one fixed complete Loewner lower K_M. A positive formal low Schur with an indefinite E block is not a positivity certificate.

The historical N20 and M312 references have different chosen reserves. They are not identified by this assessment. Changing the outside reference or enclosures can change the resulting criterion or certificate; that is a separate change from relabeling a retained block. A reference lower remains distinct from the true form, and failed conservative certificates do not establish true negativity.

## Executed procedure and inputs

[assess-v1.py](assess-v1.py) is a standalone, versioned investigation procedure using the standard library and FLINT exact rational matrices. It creates no new solver, analytical source producer, permanent test or proof profile. [inputs/manifest.json](inputs/manifest.json) binds15 captured inputs, including the actual M312 and earlier N192 source bytes, original runtime receipts, original seal, C-0092 report/receipt/seal and its producer source identity. The original seal binds all four fresh-workload receipts.

Commands actually executed from the repository virtual environment, with fresh output paths:

```text
uv run --locked python computations/2026-10-25T134254Z-coupled-route-viability/assess-v1.py --root . --output computations/2026-10-25T134254Z-coupled-route-viability/data/assessment-v1.json
uv run --locked python -I computations/2026-10-25T134254Z-coupled-route-viability/assess-v1.py --root computations/2026-10-25T134254Z-coupled-route-viability/inputs --output computations/2026-10-25T134254Z-coupled-route-viability/data/captured-input-replay-v1.json
```

Both exit0 with `MATCHED_CRITERION_AND_COST_ACCOUNTING_PASS`, taking1.21767 and1.21300 seconds. The reports are byte-identical, SHA256 `d295b3a1c54832f353efb3c1916a93831e731c1dc546f9077d5e020004117a75`. This is assessment execution time, not a mathematical generation or performance benchmark. Full actual argv, stdout/stderr and timings are retained in `data/`.

Runtime is Windows11 build26300, Python3.14.0 x64, python-flint0.9.0. [environment.json](environment.json) and copied lock/config files preserve the environment identity. The replay uses isolated Python and captured inputs; the versioned procedure imports no live project scripts.

## Exact boundary controls

Four rational control groups execute successfully:

1. Matched direct and nested elimination both give10/3. Ignoring the outside cross coupling instead gives7/2, an unsafe overstatement.
2. An indefinite E block gives a positive algebraic low Schur5 while the full determinant is negative. The E positivity condition cannot be omitted.
3. Changing the outside reference changes the result to3. This is not the same matched criterion.
4. A conservative finite Loewner enclosure gives223/70, below10/3. Certificate bounds must not be identified with the exact reference.

These finite controls illustrate mistakes the general proof excludes; they do not replace its infinite-form domain argument. The independent reviewer ran no numerical commands. No test suite, fresh analytical generation, new positivity run, Rust or Lean check was performed.

## Actual data and full-work accounting

The procedure counts the serialized arrays in the retained sources, including exact parity zeros. These counts are not the number of distinct transcendental integrals.

| Retained source | Low/Gram slots | Signed head slots | Scalar slots | Total |
| --- | ---: | ---: | ---: | ---: |
| N192,m626 | 37056 | 249984 | 2 | 287042 |
| M312,m1018 | 97656 | 660816 | 3 | 758475 |

The demonstrated coupled construction still inherits the complete second row. A final low label P20 does not make the full analytical construction a20-coordinate construction. The two source observations also differ in support, residual order, precision and inherited-versus-fresh work. Their ratio is not a support-scaling law or controlled timing comparison.

For one parity, m=156, n=10 and e=146. The conventional dense block-Cholesky leading model satisfies e^3/3+e²n+en²+n³/3=m³/3. The full triangular-factor parameter identity is e(e+1)/2+en+n(n+1)/2=m(m+1)/2.

| Matched dense accounting, both parities | Unreduced | Coupled elimination order |
| --- | ---: | ---: |
| Leading arithmetic model | 2530944 | 2530944 |
| Full triangular-factor parameters | 24492 | 24492 |

These are conventional dense identities, not universal algorithmic lower bounds, actual serialized proof sizes, bit-complexity estimates or measured runtime predictions. Structured algorithms and better conditioning are not excluded. The identities show why counting only the final10-coordinate block per parity omits the retained tail and cross work.

Recorded C-0087 fresh work costs795.2479036 seconds for source generation,1903.3478026 for complete independent input acceptance,14.9745588 for assessment and13.7074870 for separate replay, total2727.277752 seconds. C-0092's inherited comparison takes7.961843 seconds and excludes fresh analytical construction/acceptance. Those are different workloads. No speedup ratio is reported, and a fresh complete coupled pipeline cost remains unmeasured.

## Decision and evidentiary strength

The [decision receipt](data/decision.json) records `NARROW_TO_DIAGNOSTICS` and `NO_GO_FOR_THE_DEMONSTRATED_DENSE_REARRANGEMENT` as primary-continuation promotion. The reasons are:

- With the same outside model and retained blocks, the exact criterion is unchanged.
- The demonstrated procedure depends on the complete larger positive construction and all its analytical inputs.
- The dense split alone removes neither the full factor work nor its parameters.
- No independent fresh-data saving, new-support mechanism or support-dependent cost advantage is demonstrated.

This allocation judgment is narrower than a mathematical no-go. It does not show that all coupled references fail or cannot be useful. Nor does it invalidate the existing controlled extension, the negative reference results, or C-0092's measured inverse overcharge. Diagnostic code, independent checks, preserved failures and the corrected understanding remain completed contributions.

No prospective replacement design or implementation sequence is selected in this public record. No new support, minimum dimension, comparative external efficiency, originality or RH claim follows. Admissions remain8v1/0v2/1v3 and RH remains unresolved. Existing local source and arithmetic-window boundaries are unchanged by reordering a finite elimination.

## Preservation

All earlier research procedures, sources, tests, findings, computation bundles and theorem artifacts remain unchanged. The new bundle preserves the pre-execution statement, independent qualification, accounting procedure, exact inputs, run receipts, byte-identical replay and decision. Its integrity manifest is published last. No production code, test, dependency or verifier configuration was changed.
