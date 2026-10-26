# X-20261026-001 — Quantitative arithmetic-reference and exterior-cutoff envelopes

- **Created:** `2026-10-26T00:19:54Z`
- **Last updated:** `2026-10-26T00:28:18Z`
- **Status:** COMPLETE — independently reviewed derivation and scalar/exact replay; no new matrix or support sign
- **Claims:** C-0102, C-0103

## Objective and result

Quantify C-0101's necessary growth for the complete positive arithmetic reference M_T=aI+P_T and nonnegative Fourier exterior, separating intrinsic requirements from conservative sufficient bounds.

The [complete derivation](quantitative-envelope-v1.md) proves:

- The normalized constant trial satisfies r(T)=Theta(exp(T)/T), with explicit finite inequalities and validity ranges.
- A different, normalized two-boundary-cap trial proves a_*(T)=sup sigma(-P_T)>(3/20)exp(T) for T>=7/2. This is a necessary reference bound, not a new Weil sign.
- Exact compressed-shift chains give a finite sufficient norm sum; globally ||P_T||<=(21/5)exp(T)-21/10. The necessary/sufficient scale gap is below28 on that range. Thus a_*(T)=Theta(exp(T)); the exponential rate is not solely a loss of the upper norm sum.
- For A(t)=Re psi(1/4+it/2)-log pi, the sourced complex remainder gives |A(t)-log(t/(2pi))|<=2/t² for t>0. For every b>=0, the unique inverse cutoff is bracketed by2pi exp(b±1/8). The upper endpoint is constructively sufficient for the complete exterior.
- Positive support-dependent arithmetic/exterior reserves m(T)>0,e(T)>=0 enter additively in the cutoff exponent. Even if they tend to zero, this positive-M/exterior construction requires a double-exponential cutoff order in support. A separately constructed envelope attains that order when m+e=O(exp(T)).

This does not establish H0 positivity, low Schur positivity, any all-support Weil mechanism, practical computational cost, or a general no-go for Fourier methods. Earlier accepted finite cases remain valid and byte-preserved.

## Sources and mathematical verification

[R-0038](../../references/BIBLIOGRAPHY.md#r-0038--rosser-schoenfeld-explicit-chebyshev-bounds) is the original Rosser–Schoenfeld1962 paper. The publisher blocked automated access; the original scanned facsimile was opened in Chromium. Printed p.70 Theorem4(3.14) and p.71 Theorem12(3.35) were visually checked. They imply psi(x)>=0.9x for x>=563 and psi(x)<=1.05x for x>0. Their published finite verification is an external premise, not independently replayed here. No paper/source code was imported.

[R-0039](../../references/BIBLIOGRAPHY.md#r-0039--nist-digamma-expansion-and-complex-remainder) supplies the exact digamma expansion and complex remainder. All subsequent normalizations, overlap, partial summation and cutoff inequalities are derived locally. [Independent mathematical review](independent-envelope-review.md) approves all domains, endpoints, constants, rates and distinctions between necessary/sufficient claims. The review is not a formal kernel proof.

## Declared finite controls and observations

[input-pins.json](input-pins.json), written before calculation, fixes the two retained scalar cases and source-byte bindings, five exact cap displacements, the independent-series length16384, and exterior reserves0 and1/5. Frequency controls are the analytic boundary4, the two certified adjacent integers around2pi exp(7/2), and the existing cutoff256. These are checks of proved inequalities, not a support-selection grid.

| Existing support | Constant-trial r | Selected sufficient p | Separate-chain p | Selected p/r |
|---|---:|---:|---:|---:|
| 1353/2048 | 0.6798072389653591 | 1.124413172331838 | 1.124413172331838 | 1.654017650713976 |
| 3/4 | 0.9192843178575409 | 1.522050655624483 | 1.674004871437482 | 1.655690873930856 |

These displays are rounded; [controls-v1.json](data/controls-v1.json) retains outward rational enclosures. The second row uses the already qualified joint2/4 bound only in its valid window. The simple rational caps9/8 and49/32 recover the retained arithmetic reserves19/8 and63/32 at a7/2. Neither row measures the actual arithmetic norm or a Weil spectral gap.

All eight constant/boundary checks, five exact signed-cap overlap controls and four digamma controls pass. Direct Arb digamma enclosures fit both the independently summed convergent-series bounds and the proved analytic envelopes. The derived integer frequencies208 and209 bracket A(t)=7/2; at256, A is about3.707299742285642, independently confirming the existing exterior reserve1/5. The broad constructive cutoff for that reserve is sufficient, not necessary: its being above256 does not invalidate the stronger direct finite check at256.

## Actual execution and isolated replay

Baseline revision: `9cde2f4dc148b0de309e0d5f462072fbf571cfca`. Runtime: Python3.14, python-flint0.9; Arb512. Exact environment and actual commands/stdout/stderr are captured under data/. No research producer, matrix assembly, eigenvector, certificate, Rust verifier or Lean build was run.

From the repository root:

```text
uv run --locked python computations/2026-10-26T001954Z-quantitative-reference-cutoff/envelope-controls-v1.py --output <new-output.json>
```

The actual exercised command uses the current locked-environment Python executable, as recorded in [the receipt](data/scalar-exact-controls-final.run.json). The retained output path must not be reused: the program opens it exclusively.

A [ten-file source snapshot](source-v1/manifest.json) captures the script, pins, all four imported project modules, pyproject/lock and the two inherited scalar-input files. The same program was actually run from that snapshot as its own execution root, using only the pinned helper copies. All imported project files and namespace paths are required to lie under that root. Canonical and isolated outputs are byte-identical, SHA-256 `16810d339ed0d43a3dafbd158eafeb98a0b7ee0499772cdfe7b46611b7918f7d`. [Replay summary](data/isolated-replay-summary.json) and [isolated command receipt](data/isolated-scalar-exact-controls.run.json) retain the observations. Scalar execution took about0.475/0.465seconds; these are observations, not a benchmark or cost forecast.

## Initial calculation defects, preserved

Two initial executions failed before an output packet was published. Their receipts and exact source snapshots are retained; no mathematical negative or historical result is hidden.

1. [Initial source](data/initial-failed-control-source.py) asserted an uncertain Arb ball <= itself when the baseline selected bound was the same assigned object as the chain sum. Interval comparison cannot certify that numerical assertion. The final program uses the known assignment identity at baseline and tests the genuinely strict improvement only in the post-transition case. Receipt: [initial failure](data/scalar-exact-controls.run.json).
2. [Second source](data/second-failed-control-source.py) reached provenance capture after the mathematical controls but assumed every imported package had a __file__. The scripts namespace package does not. The final program validates its namespace search paths under the execution root separately. Receipt: [second failure](data/scalar-exact-controls-corrected.run.json).

These are new calculation defects, not edits to old production sources. Both old producer/checker/test implementations and all earlier sealed records are preserved.

## Retention and limitations

The root manifest is published last and binds all bundle members. The preservation receipt checks the13 preceding bundle seals and their887 members, plus16 protected public source/config/test files. Source and result bytes are retained without newline conversion.

The two positive-reference/exterior inequalities alone do not settle whether this reference remains useful at a finite range or can support a useful global proof. Variable tail, frequency, mixed-error, width and low-gap obligations are still distinct. No common positive coercivity constant is imposed. No literature-priority claim, RH conclusion, production profile/whitelist/schema/retained-registry change or theorem admission is made. Admissions remain8v1/0v2/1v3. No commit or push was performed.
