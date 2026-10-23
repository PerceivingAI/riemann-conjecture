# Fixed harmonic-tail majorant screen: strict negative directional upper

- **Computation ID:** `X-20261022-002`
- **Created:** `2026-10-22T19:05:32Z`
- **Last updated:** `2026-10-22T19:07:30Z`
- **Status:** `COMPLETE`, `NEGATIVE_SUFFICIENT_CRITERION` for finite `A-U_211` only.
- **Evidence class:** Exact rational consequence of pinned research inputs, conditional on their documented analytical trust. Not a certificate-admitted theorem or negative Weil form.
- **Related finding:** [F-20261022-002](../../findings/2026-10-22T190730Z-fixed-harmonic-majorant-negative-direction.md), claim C-0073.
- **Source baseline:** Existing analytical modules at `172469536bdce79757e591835c3b1331a861167d`. The additive exact consumer/tests were uncommitted at execution and are retained byte-for-byte below. No prior record or procedure was changed.

## Objective and fixed inputs

Evaluate the C-0072 one-sided finite-majorant screen at exactly `T=3/5,N=192,M=211,K=32`, active prime powers `[2,3]`, on the original exact rational odd trial. Use only the accepted nine high-mode source moments `k=193,195,...,209`. No new analytical evaluation or trial selection occurred.

| Input | SHA-256 |
| --- | --- |
| Original `computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json` | `44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b` |
| Accepted `computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json` | `9b9a1a0a0b420df0147f07c6fa1f5d9ee9005fb68dc8213cd8880d98556dd843` |

The [source-acceptance run](../2026-10-22T185054Z-directional-source-validation/record.md) independently reconstructed the new moments at 2048 bits against the existing 1024-bit source operations and 352-bit outward publication. That work is reused, not rerun here. Its original A/G inputs retain generator-source-qualified trust.

## Exact predicate

Let `mu>0`, `delta`, `a_up` and `g_low` be the exact one-sided rationals from the original packet. The ordinary-Legendre trial has exact physical squared norm `sum_i 2*z_i^2/(2i+1)<1`. Define

\[
w_k=\left(\mu+\sum_{j=193}^{k}\frac1j\right)^{-1},
\quad \theta=a_{\rm up}-w_{211}g_{\rm low}.
\]

For each accepted truncated signed-sum interval `[l_k,h_k]`, the full moment lies in `I_k=[l_k-delta,h_k+delta]`. Use

\[
d_k=\operatorname{dist}(0,I_k),\qquad
L_9=\sum_{k=193,195,\ldots,209}(w_k-w_{211})d_k^2.
\]

The reviewed C-0072 implication gives

\[
\langle u,(A-U_{211})u\rangle\le\theta-L_9.
\]

All harmonic sums, interval endpoints, squares and comparisons use standard-library `fractions.Fraction`. Decimal values are display only. The whole omitted infinite tail is paid by `w_211 G`; it is not silently projected away. The inherited `a_up,g_low` already cover the full residual and are not corrected a second time. Even high modes vanish by exact odd parity.

## Implemented consumer and checks

New `scripts/weil_directional_exact_screen.py` imports no analytical module or Arb library. It captures each input's bytes once, pins both SHA-256 values, verifies configuration/source provenance, recomputes the exact mass norm, and audits all 45 accepted component/sum intervals with exact rational arithmetic. It checks independent containment, unrounded overlap, outward rounding and full residual enlargement before the decision. It then emits exact weights, distances, weighted contributions and the resulting upper bound.

A nonnegative upper is `INCONCLUSIVE`, never positive evidence. Rejected input is `SOURCE_PROOF_GAP`, exit 2. A completed negative or inconclusive screen exits 0. The CLI preserves prior outputs and atomically publishes without overwriting a racing destination. There is no parameter grid, analytical rerun, precision retry, inverse computation or theorem-admission operation.

## Reproduction and observed result

From the repository root with the recorded source bytes and locked environment:

```text
uv run --locked python -m scripts.weil_directional_exact_screen --output computations/2026-10-22T190532Z-directional-exact-screen/data/replay-exact-screen.json
```

The actual supervised invocation used `.venv/Scripts/python.exe` directly with the same module and output `data/exact-screen.json`. Use a fresh output path for reproduction. For later reproduction after source maintenance, an isolated checkout can restore `data/source/weil_directional_exact_screen.py` to its original `scripts/` path; both analytical input packets are consumed by pinned byte identity rather than recomputed.

Observed terminal output, exit **0**:

```text
EXACT_SCREEN NEGATIVE_SUFFICIENT_CRITERION UPPER -1.2001752984084315
```

| Exact quantity, decimal display | Value |
| --- | ---: |
| Coarse upper theta | 0.09147222173693371 |
| Weighted correction lower L9 | 1.2916475201453652 |
| Weighted correction maximum from full intervals | 1.2916475201455806 |
| New directional upper theta minus L9 | -1.2001752984084315 |

The stored rational upper satisfies the exact comparison

\[
\theta-L_9<-\frac65<0.
\]

This is a quadratic-form upper on the fixed, unrenormalized physical trial, not a floating eigenvalue. It proves `A-U_211` cannot be positive at this configuration, under the stated source assumptions.

## Independent rational replay and behavioral checks

A separately coded replay uses direct harmonic sums for each weight and `min(lo^2,hi^2)` when a full interval excludes zero. It imports neither the screen consumer nor analytical source modules. It reproduced the complete exact theta, weighted sum and upper rationals and independently checked `<-6/5`. Executed replay code and output are retained as `data/independent-replay.py` and `data/independent-replay.json`.

```text
uv run --locked python computations/2026-10-22T190532Z-directional-exact-screen/data/independent-replay.py
uv run --locked --extra test python -m pytest -n 0 -q tests/test_directional_exact_screen.py
```

**12 tests passed in 0.51 seconds**, command wall 1.36 seconds. They cover positive/negative/zero-straddling intervals, strict versus equality/nonnegative outcomes, the retained whole-tail charge, reversed intervals, accidental float scalars, altered source bytes, omitted residual enlargement, unaccepted components, missing modes and incorrect coordinate metric. The test/source snapshot preserves this version without changing earlier research tests.

Actual CLI throwaway checks also passed altered-source rejection and existing-output preservation, both exit 2, with no partial publication left. They did not rerun the accepted screen. Summary evidence is in `data/validation-checks.json`.

## Runtime and ownership

Windows x64, locked CPython 3.14.0; the screen and independent replay use only the standard library. The screen process wall time was **0.41416180005762726 seconds**, independent replay **0.13748599996324629 seconds**. Each owned process exited 0; no timeout, descendant, retry or concurrent heavy worker was used. External caps were 60 seconds for the screen and 30 seconds for the replay.

Previous substantial source-run charge was 5.6750155000481755 seconds. Conservatively adding both rational process wall times gives total cycle charge **6.226663300069049 seconds**. Stage totals are not double-counted. Lightweight test/CLI-failure checks are reported separately.

## Artifact identity

| Bundle-relative path | SHA-256 |
| --- | --- |
| `data/exact-screen.json` | `c6ae1b0b5ab624df903c7c7a27179743d6f270cdb0a6b62c8ac644f48dc26b59` |
| `data/execution.json` | `eb620a96e53c3cbb9dadd86ce5b1bf9839342fe455419541ae1ab5af21bcf0b1` |
| `data/independent-execution.json` | `443593d37c54124816e88bbb417be5e75bf37891cd8cbbd1ece6e15de065a905` |
| `data/independent-replay.json` | `2939a7ad904b279153e88c3131c1b0870ded0c41990cd40d40bb624d7192c142` |
| `data/independent-replay.py` | `e78870753376a518643e7ffd33b024f7fb9e8ea27b65f163c453a77e2c64fb2a` |
| `data/stdout.txt` | `5069481a33b255b4f71b1e4f08a30a716ae68ffeea286a6e920ce100ae29c1be` |
| `data/validation-checks.json` | `a3b4fe1d62082de3743f6c8a00fbfae2019b8c2809725d397c547c10e6d4457e` |
| `data/source/weil_directional_exact_screen.py` | `18908e61cb4ad0ea652d4ad9974dfb3d1a49ffc2ce355d5f76a770ac776ecf9a` |
| `data/source/test_directional_exact_screen.py` | `f5e55581460f2f96548c04863d9404eb65611f7e7d981bfebef1adc9841edca8` |

## Interpretation and stop

The finite harmonic-tail majorant `A-U_211` is rejected at the fixed support, dimensions and original odd trial. The computation stops at that conclusion. No further cutoff, dimension, support, trial or precision was tried.

The exact diagonal-inverse reference satisfies `A-U_211 <= A-B* C0^-1 B <= A-B* C^-1 B`. A negative lower matrix does **not** determine the sign of those larger matrices. Therefore this result does not refute the exact diagonal reference, the true Schur complement, the Weil form, or any other configuration. It is not a global no-go result.

The original A/G bounds were not independently reconstructed, and the analytical source acceptance still trusts the documented Suzuki identities and Arb arithmetic. This command independently checks rational consequences, not transcendental mathematics or a Lean theorem. No source reassembly, Rust/retained-proof replay, external fetch, commit, push or admission occurred. Admissions remain eight frozen v1, zero v2 and one v3 C-0067. RH remains unresolved.
