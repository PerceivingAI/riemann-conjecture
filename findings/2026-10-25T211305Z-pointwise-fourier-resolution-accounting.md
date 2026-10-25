# Pointwise Fourier complement and complete interval-order resolution accounting

- **Finding ID:** `F-20261025-008`
- **Created:** `2026-10-25T21:13:05Z`
- **Last updated:** `2026-10-25T21:19:30Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` scalar bounds and conditional matrix-order estimate, not positivity

## Statement

At T=3/4,a7/2,Omega256,N312, C-0097/C-0098's complete compact formulas give kappa<k0=4e-49,eta<1.9e-24 and mixed Gram allowance epsilon0=6e-24. With m0=63/32 and d0=m0-k0, a valid sufficient lower is S_-=A_- - [(GP)_+ +epsilon0 D]/d0. No low sign is supplied.

For ordinary Legendre mass D_j=2/(2j+1), the existing symmetric entry-box radius and row-sum conversion has complete true-to-ordered-bound loss at most F E D for a band error radius E sqrt(D_i D_j), where

F=156+max_i sum_j sqrt(D_j/D_i)<470

in both156-dimensional parity blocks. If all numerical low-A order losses excluding the analytic band radius are at most1e-27, GP numerical order losses are at most1e-28, and E<3e-21, then

0<=A-GP/m0-S_-<1.5e-18 D.

Those numerical width budgets are explicit hypotheses. The comparison matrix A-GP/m0 is not known positive. The estimate pays the complete compact mixed term and denominator change, not only low entry rounding.

## Evidence / derivation

[X-20261025-008](../computations/2026-10-25T211305Z-post-m4-scalar-cost-assessment/record.md) retains the [complete derivation](../computations/2026-10-25T211305Z-post-m4-scalar-cost-assessment/assessment-derivation-v1.md), executed scalar/exact controls and independent review. The mass-factor proof bounds both the normalized midpoint error and radius-row correction. A nonuniform-mass exact box control detects loss greater than the nominal entry-radius parameter.

At this support the complete analytic frequency bounds are about1.00426310714e-20 at q48,2.51065776786e-21 at q49 and2.33823225634e-30 at q64. The retained corrected C-0096 q48 upper is about4.32907935139e-21. Thus49 is the least integer order meeting this particular sufficient-bound comparison, not a necessary positivity condition. Canonical and isolated captured-source calculations reproduce byte-for-byte.

Exact contraction-volume accounting for the demonstrated source organizations gives ratios1964/1479 and6401/4210 with the changed geometry. Output slots and finite dimensions remain unchanged. This is a classical shape model, not observed runtime or native arithmetic complexity.

## Dependencies

C-0097/C-0098; C-0096's SHA-pinned quadrature comparison value and documented matrix organization; exact symmetric interval Loewner conversion. Scalar bounds share Arb/FLINT and the previously documented Suzuki/exterior premises. No new literature result or new low positive packet is assumed.

## Significance and limits

This turns the pointwise complete-complement formulas into an explicit, auditable accuracy comparison and accounts for conversion loss that an operator-error value alone does not describe. It does not infer a surviving positive gap from an earlier support.

No low matrix, new support positivity, source/audit implementation, actual numerical width budget, runtime or memory guarantee, generic continuation, production admission or RH proof is established. The complete conditional sign remains open. All historical versions and admissions retain their original scope.

## Verification

Scalar Arb512 and exact controls exit0. Python-I-B captured-source replay is byte-identical. Independent mathematical/source review finds no defect requiring repair, without performing numerical runs or hash authentication. No full suite, Rust, Lean or finite positivity computation was run for this assessment.

## Timestamped addenda / corrections

None.
