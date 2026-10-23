# Fixed directional source intervals with independent analytical reconstruction

- **Computation ID:** `X-20261022-001`
- **Created:** `2026-10-22T18:50:54Z`
- **Last updated:** `2026-10-22T18:52:27Z`
- **Status:** `COMPLETE`. `SOURCE_INPUTS_ACCEPTED`, research-only analytical inputs. No Schur sign evaluated and no theorem admission.
- **Source baseline:** `172469536bdce79757e591835c3b1331a861167d` for the existing analytical modules. The additive consumer and tests were uncommitted at execution; exact snapshots and hashes below preserve their as-run identity. No historical implementation or artifact was rewritten.

## Objective and quantity evaluated

Exercise the existing sparse polynomial source operations at fixed `T=3/5`, low cutoff `N=192`, residual order `K=32`, active prime powers `[2,3]`, and the exact odd trial retained in [SYS-6.4](../2026-10-18T090311Z-sys6-selective-support/record.md).

For each `k=193,195,197,199,201,203,205,207,209`, enclose the normalized high-mode source moment

\[
t_k^{(32)}=\langle e_k,(V+P_2+P_3+R_{32})u\rangle,
\qquad e_k=P_k\sqrt{(2k+1)/2}.
\]

The trial has ordinary Legendre coefficients, with physical squared mass `sum_i 2*z_i^2/(2i+1)`. It was neither renormalized nor reselected. The original packet hash is `44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b`; its 192 coefficients are exactly odd, with 96 nonzero entries and denominators dividing `2^20`. Direct exact mass-norm computation is inside the original enclosure and below one.

This computation evaluates linear source moments. It does not compute a complementary inverse, a new mixed Gram, a Schur matrix or an eigenvalue. Sparse-subspace Gram/square results produced incidentally by existing assemblers are ignored; their projection is not the original `Pi_192`.

## Implemented composition and independent controls

New research-only CLI `scripts/weil_directional_source_validation.py` composes existing analytical routines without changing them.

1. At 1024 bits, `_potential_matrices` supplies the endpoint-multiplier pairing by exact-grouped harmonic contractions. The existing prime-power assembler supplies separately signed P2 and P3 pairings in cell-local Legendre coordinates. `_residual_truncation_operator` supplies the exact polynomial residual image and its pairings. A ten-polynomial sparse orthogonal basis contains the original trial and the nine selected high modes.
2. At 2048 bits, helpers from `scripts/verify_combined_schur_analytic_entries.py` separately reconstruct the trial using native exact Legendre polynomials, directly contract whole-potential moments, integrate binomial-translated monomials on both compressed overlap cells for each prime, and rebuild the residual via independent Bernoulli and split-kernel formulas. Its support-fixed full-matrix `run()` is not used.
3. Exact trial and residual polynomials must agree. Independent scalar reconstruction checks the inherited positive `mu` lower and `delta` upper in the correct directions, strict prime-power activation/exclusion, and `1<tau_m<2`. Arithmetic constant intervals must overlap the separately evaluated source constants.
4. Each generator component and signed sum is published with outward 352-bit dyadic endpoints and one extra `2^-352` unit on each side. The independent reference interval must lie entirely inside the published interval. Unrounded generator/reference balls must also overlap, so padding cannot conceal a discrepancy. All unrounded endpoints remain in the artifact.
5. The full source moment is enclosed by adding `[-delta,+delta]` to the published truncated sum. This uses the directly certified `||u||<1` and the full operator-norm residual allowance, not an assumption that the polynomial truncation equals R. The actual `R_32 u` degree is **223**, so high residual pairings are retained.

A separate read-only source review found no blocking defect in the consumer/helper paths. That review did not execute computations and is not an additional analytical certificate.

## Environment and reproduction

- Windows x64, CPython 3.14.0, python-flint 0.9.0, locked `uv.lock` environment.
- One directly owned Python process, no child processes created by the consumer. Numerical-library thread limits were set to one.
- External finite timeout 600 seconds. No retry occurred.
- No floating quantities enter input acceptance. Decimal widths/timings are observational displays only.

From the repository root with the recorded source bytes:

```text
uv run --locked python -m scripts.weil_directional_source_validation --precision 1024 --output computations/2026-10-22T185054Z-directional-source-validation/data/replay-source-validation-1024.json
```

The actual supervised invocation used the locked environment's `.venv/Scripts/python.exe` directly, with the same module and arguments and output `data/source-validation-1024.json`. `data/execution.json` retains its argument list, owned PID, wall time, exit code and termination observation. The replay path is deliberately different because the CLI refuses to overwrite an earlier output before doing analytical work. Publication also refuses a racing destination through exclusive hard-link creation.

For reproduction after the main script changes, use an isolated checkout of the baseline and restore the additive script from `data/source/weil_directional_source_validation.py` to its original `scripts/` path. Its recorded bytes, the original analytical source hashes, and the locked dependencies define this method. The JSON also fingerprints all directly selected source files and lock/configuration files. The retained test snapshot identifies the tests actually run.

## Observed output and cost

Exit **0**. Terminal output:

```text
INPUT_IDENTITY_ACCEPTED
GENERATOR_COMPLETE 1.589
SOURCE_VALIDATION SOURCE_INPUTS_ACCEPTED SECONDS 5.405
```

All nine modes passed each of V, P2, P3, R32 and the signed truncated sum: **45/45 analytical interval checks**. The output records `schur_sign_evaluated=false`.

| Measured stage | Seconds |
| --- | ---: |
| Generator operations | 1.588718 |
| Independent reconstruction and checks | 3.769536 |
| Internal evaluation total | 5.363629 |
| Whole owned-process wall time | 5.675016 |

These are nested measurements, not additive independent charges. Aggregate substantial-run usage is the whole-process wall time, **5.6750155000481755 seconds**, including the independent reconstruction. `timed_out=false`, exit 0, owned-child exit confirmed. No target evaluation preceded this run, and no precision retry was used.

Maximum published component/sum width is `3/2^352`, approximately `3.2701e-106`, before full residual enlargement. The following widths describe unrounded analytical intervals. They are not positivity margins.

| Component | Maximum generator width | Maximum independent-reference width |
| --- | ---: | ---: |
| V | 2.8559e-308 | 1.4061e-465 |
| P2 | 3.0667e-230 | 5.8349e-412 |
| P3 | 6.7754e-230 | 8.8039e-391 |
| R32 | 3.2672e-315 | 1.8175e-623 |
| Signed truncated sum | 9.8420e-230 | 8.8039e-391 |

Exact rational endpoints, not underflow-prone binary floats, govern all checks. The full residual allowance dominates publication width and is retained exactly in `full_source_interval`.

## Regression and CLI checks

```text
uv run --locked --extra test python -m pytest -n 0 -q tests/test_directional_source_validation.py tests/test_prime_power_local_legendre.py tests/test_combined_analytic_entries.py
```

**18 passed in 1.43 seconds**, command wall time 2.75 seconds. Six new tests cover altered input bytes, physical mass/parity rejection, outward rounding of negative nondyadic values, discrepancies hidden by padding, overlapping but uncontained references, and real small source comparisons that detect omitted P3 and incorrect high-mode normalization. They also exercise even-mode cancellation and retained nonzero residual action. The other twelve tests are unchanged existing arithmetic/independent-entry checks.

Separate actual CLI smoke checks used throwaway files. Altered input returned exit 2 with a byte-identity rejection before source assembly; a second invocation to the existing output returned exit 2 before analytical work and left its bytes unchanged. Neither path left a partial publication. The checks did not compute another target-scale result. Summary evidence is retained in `data/validation-checks.json`.

No original negative-predicate replay, Rust verifier, retained-proof replay, Lean build, external fetch, commit or push occurred.

## Artifact identity

All paths below are relative to this bundle. Exact outputs and the additive code/test snapshots are retained.

| Path | SHA-256 |
| --- | --- |
| `data/source-validation-1024.json` | `9b9a1a0a0b420df0147f07c6fa1f5d9ee9005fb68dc8213cd8880d98556dd843` |
| `data/execution.json` | `df90352814c6a55c6bba2ac8680b11afdfcbab687399896bbb220a0befa51ec1` |
| `data/stdout.txt` | `2ac80995ea23861e62c34af2ea8c5c71a23a9c9f7bf5cf8e0105a67b69233e99` |
| `data/validation-checks.json` | `2cd7a182764c0909ef005ab5877a33beaca5caeee177965aacc9d2d9d476a8b0` |
| `data/source/weil_directional_source_validation.py` | `0b90d69be7d64c4a9093115da14c291ed7cc9728edf0a3004e33d1d427977fef` |
| `data/source/test_directional_source_validation.py` | `6cf628e9e6d3312e662db117711a32000c8c98c9e26df637f4c64feaddfdff82` |

## Interpretation and limitations

The existing sparse operations supplied the selected normalized source moments with accepted independent reconstruction at observed low cost. No new analytical formula, general inverse engine, proof profile or production verifier was needed. The additive consumer makes the executed composition reproducible and records its acceptance checks.

This is source acceptance for **these new moments and scalar prerequisites**, under the established local Suzuki form and trusted Arb arithmetic. The original SYS-6.4 A/G directional enclosures remain generator-source-qualified; they were not independently reconstructed by checking these moments. Source independence means distinct mathematical assembly here, not a second arithmetic library or a kernel proof of Suzuki's identities.

No decisive sufficient-matrix predicate was evaluated. No positivity, negativity of the Weil form, or unbounded support-covering result follows from this computation. C-0072 supplies the reviewed conditional inverse/majorant context; [F-20261022-001](../../findings/2026-10-22T183011Z-harmonic-tail-inverse-majorant-review.md) is the preceding written review, not an earlier execution of these target moments. Admissions remain eight frozen v1, zero v2 and one v3 C-0067; RH remains unresolved.
