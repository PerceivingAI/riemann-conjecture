# Pointwise post-m4 Fourier scalar and cost assessment

- **Computation ID:** `X-20261025-008`
- **Created:** `2026-10-25T21:13:05Z`
- **Last updated:** `2026-10-25T21:19:30Z`
- **Status:** `COMPLETE` scalar/error and exact workload accounting, no low matrix or sign

## Objective

Evaluate how the qualified Fourier bounds and demonstrated source organizations change at an interior support beyond activation of4. Assess T=3/4,a7/2,Omega256,N312 using only complete scalar formulas and exact contraction dimensions. Do not infer a positive low gap or measured matrix runtime.

## Mathematical quantities

Both distances to log2 and log5/2 exceed1/20. A signed4 image overlaps7.58037592534% of the full interval; the central2/2 image intersection has the same scaled width. The active set is exactly2,3,4.

The complete C-0098 pointwise bounds give kappa<4e-49,eta<1.9e-24 and mixed allowance epsilon<6e-24. Thus the denominator63/32-4e-49 is positive. At this support, q49 is the least integer frequency order whose analytic operator-error bound is below the SHA-pinned corrected C-0096 q48 bound. This compares sufficient bounds, not actual Gaussian errors.

The [derivation](assessment-derivation-v1.md) accounts for source physical mass and full matrix-order inflation. For the existing symmetric entry-radius/row-sum conversion, the complete true-to-lower multiplier is below470 in both parity blocks. Under explicitly hypothetical numerical A/GP order budgets1e-27/1e-28, the complete sufficient lower differs from the ideal diagnostic A-GP/(63/32) by less than1.5e-18 D. This is a conditional resolution, not a known positive gap or measured source width.

## Environment and captured inputs

Python3.14.0, python-flint0.9.0, scalar Arb512 and exact rational arithmetic. [Environment](data/environment.json) and [source closure](source-v1/manifest.json) retain versions and lockfile identity.

The corrected C-0096 source packet is SHA256 `6f8994ee0d8813ddd0bbb3ba88e35b2070905199693788f9660906474edbeb66`. Only its certified quadrature-error field is used as a comparison value; its matrix positivity is not an input to a new sign. Its exact compressed bytes are copied into the closure for reproducibility. This retained comparison input exceeds2MB; it is an original byte-bound scientific artifact, not optional display data.

## Reproduction procedure

From the repository root, choose a fresh path:

```text
uv run --locked python computations/2026-10-25T211305Z-post-m4-scalar-cost-assessment/assessment-v1.py --output <fresh-assessment.json>
```

This preserved standalone calculation is not a new generic research CLI or matrix-source upgrade. It evaluates no low entries, directions or eigenvalues. [Canonical receipt](data/assessment.run.json) records exit0. The [output](data/assessment-v1.json) contains exact outward rational endpoints, scalar checks and exact accounting.

The isolated command uses Python-I-B and runpy on the captured calculation, whose imports resolve against its source closure. [Actual isolated receipt](data/isolated-assessment.run.json) and [summary](data/isolated-replay-summary.json) confirm exit0 and a byte-identical output. Public interpreter paths are repository-relative.

## Verification and interpretation

The [independent review](independent-assessment-review.md) checks the full physical-mass factor, denominator and mixed payment, outward-grid order bound, q49 comparison and contraction-volume algebra. No defect requiring repair was found. The reviewer inspected source and derivations but executed no numerical job, hash authentication or matrix check.

An exact nonuniform-mass interval-box control executes the existing order helper. It produces lower diag(-3,-6) and a true-to-lower loss4 on a unit-mass coordinate despite nominal entry-radius parameter1. This demonstrates why the box-to-order conversion cannot be omitted. The128-bit publication grid alone contributes less than3e-34 to a conservative order-loss bound; uncomputed working intervals still require their own numerical budgets.

Source/audit contraction-volume ratios relative to the demonstrated baseline organization are1964/1479 and6401/4210. Producer active cells change4 to7; independent low/square domains change4+8 to6+20. Source frequency-node evaluations change3264 to3332, while independent q64 stays4352. Six complete serialized triangles still contain292968 slots; parity blocks stay156+156.

These are exact accounting under a declared classical dense model, not FLOPs, native FLINT operation counts, runtime ratios, memory measurements or a scaling law. Baseline timings are context only. Scalar execution does not benchmark a post-transition source or audit.

## Related claim, limits and circularity

[C-0099 / F-20261025-008](../../findings/2026-10-25T211305Z-pointwise-fourier-resolution-accounting.md) records the quantitative conditional bound. Dependencies are C-0097/C-0098, the existing exact interval-order rule and C-0096's byte-bound comparison value. No new external theorem or RH-equivalent positivity is assumed.

No low matrix, proposed direction, eigenvalue, witness, complete analytical input acceptance, new support positivity, generalized source/checker, production certificate/profile, theorem admission or RH result is established. Numerical working-interval budgets are hypotheses, not executed achievements. Historical code, tests, computations and admissions remain unchanged.

## Integrity and corrections

The root manifest is written last and seals the captured source, exact comparison input, scalar outputs and receipts. No original method, test or result is overwritten. There are no corrections to an earlier run in this assessment.
