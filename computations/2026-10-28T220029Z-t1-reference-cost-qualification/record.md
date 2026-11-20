# T=1 supported reference and declared-cost qualification

- **Computation ID:** X-20261028-004
- **Created:** 2026-10-28T22:00:29Z
- **Last updated:** 2026-10-28T22:49:20Z
- **Status:** COMPLETE
- **Claim:** C-0125, source-conditional scalar reference/error result only
- **Code baseline:** 2fdb9cbca0d8789feabe1d872f177a8a93565839 plus new separately retained, uncommitted operation bytes

## Objective

Evaluate the inherited supported-reference policy at exact T=1, including newly active prime7, and quantify its declared computational shape without building a full target matrix. Distinguish a reference-policy cost obstacle from a negative sufficient matrix, unresolved arithmetic or a true positivity obstruction.

## Mathematical quantity tested

The [complete derivation](reference-contract-v1.md) transfers the accepted WHOLE-LINE T4/5 discrepancy inequality to new supported inputs. Added prime5/7 and continuum shifts all exceed T=1, so their compressed self-adjoint shift norms are1. This gives supported beta3359/1024 at alpha1/4, floor1/3 and eta1-2^-128. It is not a pointwise multiplier bound or a transport of old positivity.

The full outside reference, physical inverse, canonical residual error, frequency infinity and numerical starting policies are independently qualified. No actual T=1 low/coupled matrix, exact coupled sign, achieved high-mode width or smooth-test positivity is computed. C-0124 at T81/100 remains the retained positivity frontier. Production admission remains8v1/0v2/1v3; RH is unresolved.

## Environment

The actual environment receipt records Python3.14.0, python-flint0.9.0, FLINT3.6.0 and Windows x64. Scalar jobs use one native thread. Producer scalar precision is512 bits with192-bit publications. The separate consumer reconstructs native enclosures at both512 and1024 bits. No GPU, cloud, Docker or VM operation is used.

## Qualified parameters and exact shape

The prior row is retained evidence, not newly executed matrices. The new row is a scalar declaration, not target positivity.

| Quantity | Accepted T81/100 workload | Qualified T=1 policy |
| --- | ---: | ---: |
| Supported beta | 821/512 | 3359/1024 |
| Reference anchor R | 710 | 6641 |
| Low dimension N | 826 | 9072 |
| Residual order K | 86 | 132 |
| Physical extent M | 1652 | 18144 |
| Dimension per parity | 413 | 4536 |
| Six triangular analytical entries | 512946 | 61739496 |
| Source starting bits | 4608 | 40960 |
| Independent starting bits | 6144 | 55296 |
| Translation cells | 9 | 11 |

N9072 is the first even cutoff for the published fixed scalar policy, not a minimum positivity dimension. Its N9070 predecessor fails. Direct factorial leakage reconstruction and a strict monotonicity argument cover all4536 positive even policy candidates. Even N3320 is required merely for this geometric leakage expression to enter its valid regime.

Accuracy2^-78 is a choice below the accepted0.81 selected-low scalar divided by2^20, never an assumed new-support gap. K132 pays the full canonical model allowance below2.353e-24; all65 preceding even orders fail. All133 canonical coefficients match an independent formal quotient, and2K<N,M>=N+K hold. All60 inverse-frequency steps, including the positive terminal infinity weight, and the complete physical inverse are accepted.

## Actual execution and verification

1. `qualify-reference-v1.py` completes in3.863s and produces data/source-v1.json.
2. `verify-reference-v2.py` completes in2.812s. It reexecutes the entire inherited independent T4/5 native scalar proof, then checks302 native interval containments and252 rational upper bounds across512/1024 bits. It derives the policy cutoffs, coefficients, precision and shape independently; it imports no producer mathematics.
3. `assess-cost-v1.py` binds the accepted source/audit and corrected retained measurements, and reports exact shape indices separately from conditional memory models.
4. All seven [mathematical controls](data/negative-controls-v1.json) reject at their intended checks, with no PASS file: underreported added-prime norm, false complete leakage, omitted polar coefficient, unpaid terminal infinity, geometric-invalid small cutoff, unpaid model discrepancy and floating mathematical input. The control run takes15.351s.
5. A [20-destination captured replay](data/isolated-replay-v1.json) reproduces source, independent audit and cost-assessment bytes exactly, with no field exclusions. Expected outputs are withheld from the child tree. All three comparisons pass in6.913s and the owned tree is removed. The replay shares installed Python/FLINT; it is source/input isolation, not an OS sandbox or independent arithmetic implementation.

Raw argv, exit codes, elapsed times and streams are retained in data/*-receipt.json and matching stdout/stderr files. [Capture description](captured-source-inputs-v1.json) binds673644 source/input bytes. No full old or new matrix operation is replayed.

## Conditional resource assessment

[Cost assessment](data/cost-assessment-v1.json) uses the corrected T81/100 measured summary. The accepted0.81 source/audit walls were1767.866/2845.007s, with process committed peaks about6.436/7.861GiB. These are historical single-run observations, not a fitted scaling law.

Exact declared entry growth is163332/1357, about120.36 times. Dense-square growth is419904/3481, about120.63 times. The cell-times-dense-cubic work index is332563968/205379, about1619.27 times before precision-sensitive arithmetic. This is an operation-shape index, not a wall-time forecast.

Under an explicitly UNVALIDATED same-live-allocation N-squared-times-working-precision model, source/audit peaks would be about6901/8534GiB. The quadratic-only model is also retained. Neither is a measured target peak, an admission bound, a storage lower bound or proof that every implementation exceeds available RAM. No target wall-time prediction or target allocation attempt is made.

The established obstacle is the much larger shape forced by this inherited sufficient reference policy. Reference overestimation, numerical representation and implementation/storage cost remain distinct possible causes. The existing complete runner has fixed0.81 bindings and is not qualified at these new dimensions; its9GiB admission gate is not a target memory estimate.

## Reproduction

Run from the repository root, using fresh output files:

```text
uv run --locked python -B computations/2026-10-28T220029Z-t1-reference-cost-qualification/qualify-reference-v1.py --inputs computations/2026-10-28T220029Z-t1-reference-cost-qualification/inputs-v1.json --output <fresh-source.json>
uv run --locked python -B computations/2026-10-28T220029Z-t1-reference-cost-qualification/verify-reference-v2.py --inputs computations/2026-10-28T220029Z-t1-reference-cost-qualification/inputs-v1.json --source <fresh-source.json> --output <fresh-audit.json>
uv run --locked python -B computations/2026-10-28T220029Z-t1-reference-cost-qualification/assess-cost-v1.py --inputs computations/2026-10-28T220029Z-t1-reference-cost-qualification/inputs-v1.json --source <fresh-source.json> --audit <fresh-audit.json> --output <fresh-cost.json>
```

The self-contained reproduction is:

```text
uv run --locked python -B computations/2026-10-28T220029Z-t1-reference-cost-qualification/exercise-scalar-v1.py --mode replay --capture computations/2026-10-28T220029Z-t1-reference-cost-qualification/captured-source-inputs-v1.json --output <fresh-replay.json>
uv run --locked python -B computations/2026-10-28T220029Z-t1-reference-cost-qualification/exercise-scalar-v1.py --mode controls --output <fresh-controls.json>
```

## Preserved failed attempt and correction

The first consumer v1 rejects the valid packet with `nonexact JSON number` before mathematical verification, because it applies exact-math JSON parsing to historical floating time/memory metadata. Its code and failed receipt are retained unchanged. Consumer v2 permits those numbers ONLY in the SHA-pinned measurement record. All mathematical inputs still require exact parsing; the floating-math adversarial case confirms rejection. No exception, mathematical interval or proof gate was suppressed.

## Interpretation and limitations

This establishes a supported-reference/error qualification and a quantified policy-cost obstacle at one support. It does not establish T=1 positivity, a negative sufficient matrix, true Weil negativity, a universal memory/runtime obstruction, an optimal reference or dimension, literature priority, external-proof acceptance, global viability or RH. Existing research records, scientific helpers, full-source programs and production contracts are unchanged.
