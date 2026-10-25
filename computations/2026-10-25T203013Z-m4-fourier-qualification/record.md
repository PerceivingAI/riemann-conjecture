# First post-m4 Fourier-reference qualification

- **Computation ID:** `X-20261025-007`
- **Created:** `2026-10-25T20:30:13Z`
- **Last updated:** `2026-10-25T20:51:16Z`
- **Status:** `COMPLETE` mathematical qualification and scalar/exact controls; no new low sign

## Objective

Determine whether the complete bounded Fourier-reference argument remains mathematically valid after activation of4, including the changed2-chain geometry. Qualify the whole open window log2<T<log5/2, not a selected rational support.

## Mathematical quantities and derivations

The active prime powers are2,3,4. The one-sided coefficient is Lambda(m)/sqrt(m), so d4=log2/2. With tau4=2tau2, the dyadic pair acts on three-point fibers with exact eigenvalues log2 times -1/2,(1+sqrt17)/4,(1-sqrt17)/4. Adding the3 term gives ||P||<49/32 and, at a7/2, M>=63I/32. The old average2-shift norm1/2 fails once tau2<1.

There are seven strict cells and20 positive-length signed-image intersections among36 ordered pairs. Ten surviving pairs involve4. Two additional surviving opposite-sign2/2 image pairs represent the newly nonzero literal same-sign squares. Complete GP=P²-PD^-1P retains every mixed term and ordinary Legendre mass D_j=2/(2j+1).

The [arithmetic derivation](independent-arithmetic-qualification.md) and [complete Fourier contract](fourier-extension-contract-v1.md) state the proofs, operator/form domains, source premises, exterior, full one-sided and double-compression estimates, mixed Gram and source quadrature/anchor obligations. The [independent review](independent-fourier-contract-review.md) finds no blocking mathematical defect under those stated premises. Its inspection is not another numerical run.

## Environment and inputs

Python3.14.0, python-flint0.9.0, Arb512 and exact rational arithmetic; [environment receipt](data/environment.json). Source and lockfile bytes are captured in [source-v1/manifest.json](source-v1/manifest.json). The inherited C-0094 exterior scalar dataset is SHA-pinned and copied into this source closure. No production source, old proof, frozen research generator or historical test is modified.

The rational13/16 is an analytic upper bound for log5/2, NOT a support with active set2,3,4. At Omega256 it majorizes T Omega by208. N312 is the existing baseline used to compare sufficient complement bounds, not a new selected case or dimension search.

## Reproduction procedure

From the repository root, use fresh output paths:

```text
uv run --locked python -m scripts.weil_m4_fourier_qualification --output <fresh-scalar.json>
uv run --locked python -m scripts.weil_m4_geometry_controls --output <fresh-geometry.json>
```

Both modules are research-only controls. Neither accepts a support, generates a low positivity matrix, exports a theorem certificate or invokes admission.

Isolated replay uses Python -I, inserts only the captured source directory at the front of sys.path, then executes the same module through runpy. The expanded commands and actual return codes are retained in [scalar replay](data/isolated-qualification-controls.run.json) and [geometry replay](data/isolated-rational-geometry-controls.run.json). Both outputs are byte-identical to their canonical counterparts; [replay summary](data/isolated-replay-summary.json). Interpreter paths in public command metadata are repository-relative, without altering commands' arguments or numerical output.

## Executed outputs

[Scalar controls](data/qualification-controls-v1.json) verify exact exponential/radical envelopes, joint-fiber characteristic polynomial and weighted self-adjointness, symbolic signed-pair classification, inherited full-exterior reserve, fresh scalar band bound and complete uniform tails. The canonical run exited0 in about0.322 seconds; isolated replay exited0 in about0.393 seconds. These are operation receipts, not a matrix workload or scaling benchmark.

| Whole-window quantity at the baseline comparison | Certified rational bound |
| --- | --- |
| Arithmetic operator norm | less than49/32 |
| Positive M reference | at least63/32 |
| Full compact double tail kappa | less than3e-27 |
| Full compact one-sided tail eta | less than1.4e-13 |
| Complete mixed Gram allowance epsilon | less than5e-13 |
| Complete exterior A(t)-a for abs(t)>256 | greater than1/5 |
| Full frequency quadrature error, q48 | less than2e-20 |
| Full frequency quadrature error, q64 | less than5e-30 |

Thus the unchanged a and Omega remain admissible. An explicit uniform finite sufficient criterion is A_- - [(GP)_+ +5e-13 D]/[63/32-3e-27]>0. No finite matrix sign is supplied. Pointwise allowances can be sharper than this worst-window bound; the old3e-40 allowance cannot simply be reused.

The [exact geometry controls](data/rational-geometry-controls-v1.json) independently compare combined-image integration on seven rational toy cells with all36 direct pair intersections, using both degrees0 and1. They obtain low constant entry -47/10 and square121/10, with unforced parity cancellation. Dropping the two central pairs loses exactly1. Ordinary mass2 gives tail Gram211/200; incorrect identity mass gives a negative result. The toy shifts are not an arithmetic support probe. Canonical execution exited0; isolated reproduction is byte-identical.

The enlarged real anchor range w<208 admits a complete384-order finite0F1 tail below2^-720 for anchors n>=312. The128-order positive pole series has its own complete geometric tail. Recurrence propagation, interval source uncertainties and matrix Loewner conversion remain explicit requirements, not implied numerical success.

## Interpretation and limitations

C-0097 and C-0098 / [F-20261025-007](../../findings/2026-10-25T203013Z-m4-fourier-qualification.md) qualify arithmetic and full complement/source mathematics across this structural boundary. The norm improvement exploits the coupled2/4 fiber rather than guessing a larger projection. The complete exterior and positive outside denominator survive; no unproved estimate is needed to state the conditional finite criterion.

No rational post-transition case, new low source matrix, sign, witness, support theorem, timing advantage, full canonical operator-domain equality, generic pipeline, production profile or admission is established. Suzuki v3, the inherited C-0094 scalar proof and Arb/FLINT correctness remain explicit premises. The finite sign can still fail. RH is unresolved and admissions remain8v1/0v2/1v3.

## Integrity and historical preservation

The root manifest is written last and includes the executable closure and its nested manifest. Old records are not revised to reflect these new results. No previous math, source, test or artifact is overwritten. The complete new evidence is distinct from C-0096's fixed positive case and preserves that case's original limits.
