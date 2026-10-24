# Reviewed uniform matrix bound: source-interface and exact algebra controls

- **Computation ID:** `X-20261024-001`
- **Created:** `2026-10-24T02:10:44Z`
- **Last updated:** `2026-10-24T02:33:37Z`
- **Status:** `COMPLETE` for the fixed operation-level source/algebra checks only
- **Finding:** [F-20261024-001](../../findings/2026-10-24T021044Z-uniform-harmonic-reference-matrix-bound.md), C-0082

## Objective and mathematical quantities

Exercise existing analytical operations needed by the reviewed uniform harmonic-reference inequality, without representing a sparse source sample as a complete target matrix. Check physical degree-indexed masses, both parities, signed off-diagonal pairings and the polynomial residual boundary. Independently check the matrix-order algebra on a non-diagonal finite fixture, including full cross residual.

The [predeclared contract](contract.json) fixes T=3/5, ambient N=192,K=32, low columns 0,1,190,191 and rows 0,1,190,191,192,193,224,225. There are 32 selected unnormalized pairings for each of V, combined P and R32. This is not all 192 low columns, all omitted tail rows or the Q192 image Gram.

## Environment and immutable inputs

- Windows 11 build 26300, local machine; one owned child at a time, numerical-library threads one.
- Python 3.14.0; python-flint 0.9.0; existing locked environment, no install or external runtime.
- Generator precision 1024 bits; separately coded analytical reconstruction 2048 bits; outward publication 352 bits.
- [Environment and source fingerprints](data/environment-inputs.json) bind the original reference input and nine executed analytical/configuration dependencies. Their exact source copies are under [source/](source/).
- Original source identity: `computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json`, SHA-256 `44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b`. It is not modified or regenerated. The operation-level check does not evaluate its reference weights or a target matrix sign.

## Reproduction procedure

From the repository root in PowerShell, using the locked repository environment:

```powershell
$env:PYTHONPATH = (Get-Location).Path
uv run --locked python computations/2026-10-24T021044Z-uniform-matrix-contract/probe-v1.py
uv run --locked python computations/2026-10-24T021044Z-uniform-matrix-contract/replay-v1.py
```

The actual captured executions used the existing environment's absolute Python path. Exact commands, process limits, exit codes and charged wall times are in the two `*-run.json` receipts. The source check had a 30-second timeout, zero retries; the serialized consequence replay had a five-second timeout. No new source installation, CLI integration or general execution module was used.

The replay consumes the retained first run's output. It does not silently regenerate analytical inputs.

## Source reconstruction and strict predicates

[probe-v1.py](probe-v1.py) calls existing grouped-harmonic potential matrices, the combined active-prime operator and residual polynomial image module. It takes raw pairings, not a Gram with an incorrect sparse low projection.

Separate reconstruction uses global monomial moment contractions, independently coded Taylor translations across all certified signed cells, and independent Bernoulli/split-kernel residual polynomials. Strict predicates require each independently reconstructed interval to lie inside its outward published generator interval. Midpoint agreement and overlap are insufficient.

Reflection establishes opposite-parity zeros mathematically; both calculation paths must contain zero before imposing that identity. All R32 pairings at rows 224 and 225 are exactly zero by the degree bound, not a numerical threshold. The exact four source residual polynomials agree. The original 192-dimensional reference is not replaced by a small-dimensional tail reference.

## Output

| Exercised property | Observed outcome |
| --- | --- |
| V/P/R component containments | 96/96 pass |
| Full residual norm-bound containment | 1/1 pass |
| Independent exact residual image equality | 4/4 pass |
| Physical low-coordinate masses | 2, 2/3, 2/381, 2/383 |
| Active terms and strict next threshold | [2,3]; log(4)>2T certified |
| Exact mixed-direction matrix-order controls | Pass, including nonidentity mass and signed cross residual |
| Indefinite lower versus actual positive matrix control | Distinguished correctly |
| Separate serialized endpoint replay | 97/97 pass |
| Altered nonzero potential publication | Rejected by separate replay |

[Complete analytical receipts](data/probe-v1.stdout.json) include every published interval and independent exact endpoint pair, not just pass flags. [Replay output](data/replay-v1.stdout.json) reports its scoped acceptance and altered-input rejection. Both stderr files are retained and empty.

The exact finite fixture has three tail rows and two low coordinates with D=diag(2,2/3). Principal-minor predicates verify the complete weighted upper, tail-error order, trace upper and signed full-residual perturbation. A constructed exact actual Schur matrix is positive while the conservative lower has a negative diagonal, demonstrating why a failed lower bound is inconclusive. This fixture is algebraic evidence, not a Weil source or the original trial.

## Independent mathematical review

[Original review](independent-bound-review.md) independently checked the uniform weighted identity, form-domain inclusion, ordinary-coordinate mass, complete residual cross error, square-root direction, parity, exact matrix sign and limitations. [Supplemental review](independent-review.md) checked the noncircular uniform tail-loss halving rule without assuming positive headroom. The reviewer changed no files and executed no numerical work.

The review required explicit accounting of the nonvanishing residual floor and the factor-two distinction between interval half-width and one-sided matrix overestimation. Those qualifications are included in C-0082. Source-helper reuse is not independent analytical verification; the separately coded reconstruction still shares Arb, Suzuki identities and some exact polynomial operations.

## Execution receipts and charge

| Execution | Wall seconds | Exit | Timeout / retry |
| --- | ---: | ---: | --- |
| Fixed source and exact algebra probe | 5.553956900024787 | 0 | none / none |
| Separate rational endpoint replay | 0.11738479998894036 | 0 | none / none |

Both direct children were observed exited and reaped. This is owned-child cleanup, not an OS-wide process-tree assertion. New charge is **5.671341700013727 seconds**, added to the carried **91.74805250007194 seconds**, yielding **97.41939420008566/180 seconds**. No analytical work or failures were excluded from this session's charge. Metadata/source-preservation/document checks do not run numerical research.

## Interpretation and limits

The actual source operations support these selected rectangular pairings and physical degree indices, and the finite algebra controls agree with the independently reviewed uniform implication. The check does **not** assemble or independently accept complete target A/G, a complete weighted head, a uniform target trace, either 96-dimensional target block or any target matrix sign. Selected runtime is not a whole-space estimate.

Reading the existing T=3/5,N192 source receipt found an earlier internal elapsed value of 112.429 seconds at 1024 bits. That is retained evidence, not a new run or a universal runtime lower bound. Likewise the earlier independent N192 audit at the different T=11/20 reported 53.972 seconds; it was not replayed here. Uniform convergence, sparse timing and old timings do not establish a practical target-scale cutoff, precision or budget.

No permanent research module, regression test, certificate/verifier contract, admission, Rust/Lean source or mathematical historical record is modified. The retained probe and replay are fixed computation-source snapshots, not canonical new tools. Earlier work, including failed versions and outputs, remains intact. RH unresolved; admissions remain eight frozen v1, zero v2 and one retained v3.

## 2026-10-24T02:33:37Z — Integrity and documentation verification

All 819 protected antecedent research/source files are unchanged. The nine retained dependency snapshots match their executed originals. All 412 checked local public-document links resolve, authored text has no trailing whitespace, and scoped attributes disable text conversion for the bundle's exact captured bytes. Both owned numerical children exited; no theorem or target matrix run was added by these metadata checks.

`data/integrity-validation.json` records these checks. The final `manifest.json` binds every other retained bundle member by relative path, byte size and SHA-256; it excludes itself to avoid self-reference.

Repository provenance: the recorded published baseline is `acc63ac6d41138280236850c3fbc586e20998cc4`, with pre-existing uncommitted research preserved. Executed dependency snapshots and source fingerprints identify this research procedure; this is not a clean-source proof-bearing run or theorem-admission artifact.
