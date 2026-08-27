# Research scripts

- **Created:** `2026-08-20T20:59:00Z`
- **Last updated:** `2026-08-27T14:17:45Z`

These scripts are research instruments for the timestamped RH attempts. The core prime/Laguerre routines remain standard-library based where practical, while selected helpers use the scientific packages pinned by `pyproject.toml` and the project lockfiles. Every retained computation must record the environment actually used.

## Scripts

### `verify_identities.py`

Exact rational checks of the algebra used by `A-20260820-002`.

```text
python scripts/verify_identities.py --max-n 40
```

### `prime_trace.py`

High-precision `decimal.Decimal` cutoff study of the prime-Laguerre sequence.

```text
python scripts/prime_trace.py --s0 3 --n-max 16 --cutoffs 10000,100000,1000000 --precision 60
```

`S_n(X)` is a cutoff diagnostic, not the exact infinite `S_n` unless convergence is independently established.

### `kernel_scan.py`

Scans the smooth-density Laguerre kernel in `u=t/(4n)` and compares its sampled maximum with the analytic post-turning saddle.

```text
python scripts/kernel_scan.py --s0 3 --n 8,16,32,64 --u-max 1.6
```

### `prime_range_decomposition.py`

Breaks the truncated prime-power trace into `u=t/(4n)` bins and compares discrete prime contribution with continuous density.

```text
python scripts/prime_range_decomposition.py --s0 3 --n 8,12,16 --max-m 2000000
```

### `window_diagnostics.py`

Supports `A-20260820-004`. It reports:

- the post-turning smooth-density saddle and its Gaussian width;
- the post-turning root-one crossing;
- pre-turning absolute-envelope root rates;
- beta-only envelope rates versus exact complex Cayley rates.

```text
python scripts/window_diagnostics.py --s0 3 --n 64,128,256 --betas 0.5,0.6,0.9,1.0 --gammas 0,5,15
```

### `zero_mode_bins.py`

Numerically decomposes one exact complex zero-mode Laplace transform into `u` bins and compares the truncated integral with the analytic value `z_rho^(-n)-1`.

```text
python scripts/zero_mode_bins.py --s0 3 --beta 0.6 --gamma 5 --n 16,32,64 --steps-per-bin 5000
```

Synthetic beta/gamma inputs are diagnostics only and are not asserted to be actual zeta zeros.

### `uniform_phase_diagnostics.py`

Supports `A-20260820-005`. It evaluates the exact uniform pre-turning stationary map

```text
u_gamma=A^2/(A^2+4gamma^2)
```

against the older small-`u` approximation, checks the critical Cayley phase identity and unit stationary normalization, and can save JSON plus a static SVG plot.

```text
python scripts/uniform_phase_diagnostics.py --s0 3 --zeros 8 --dps 40 --output-json computations/.../data/s0-3.json --plot computations/.../plots/stationary-map-s0-3.svg
```

The zero ordinates are numerical `mpmath.zetazero` evaluations, not certificates.

### `chirp_window_diagnostics.py`

Supports `A-20260820-006`. It records the first-prime coordinate/frequency cap, the local chirp curvature and linearization width, and the exponential root base left by a generic Montgomery-Vaughan Dirichlet-polynomial length term.

```text
python scripts/chirp_window_diagnostics.py --s0 3 --n 1024 --output-json computations/.../data/s0-3-n1024.json
```

The script does not enumerate primes; it checks deterministic scale formulas only.

### `bilinear_chirp_geometry.py`

Supports `A-20260821-001`. It computes the four-corner nonseparability defect for `F(r,s)=Phi_n(r+s)`, checks its `1/n` decay on dyadic logarithmic boxes, records the balanced `sqrt(n)` log-width needed for unit cross phase, and verifies the formal pre-turning phase excursion `pi n`.

```text
python scripts/bilinear_chirp_geometry.py --s0 3 --n 1024 --output-json computations/.../data/s0-3-n1024.json
```

The script is deterministic phase geometry only; it does not enumerate primes or test arithmetic cancellation.

### `positivity_kernel_diagnostics.py`

Supports `A-20260821-002`. It checks synthetic Li Gram and Schoenberg matrices and the deterministic negative-diagonal structure of generalized prime-atom Gram contributions.

```text
python scripts/positivity_kernel_diagnostics.py --n-dim 8 --theta 0.7 --r 1.2 --search-n 100 --t 0.5 --x 0,1,5,10 --output-json computations/.../data/kernel-diagnostics.json
```

The zero orbits are synthetic diagnostics only.

### `weil_support_geometry.py`

Supports `A-20260821-002`. It records the half-log prime-power support thresholds and the exact path-graph norm of symmetrized compressed translations on `L2([-T,T])`. The later `A-20260821-003` work adds the exact finite-support normalization and residual-term requirements.

```text
python scripts/weil_support_geometry.py --T 0.45 --max-m 20 --output-json computations/.../data/support-T045.json
```

It does not approximate the archimedean Weil operator.

### `weil_endpoint_absorption_certificate.py`

Supports `A-20260821-003`. It proves the `T=7/20` first-prime endpoint absorption inequality using exact `Fraction` arithmetic, including certified rational logarithm bounds derived from the atanh series:

```text
V + P_2 >= (69/100) V >= 0.
```

```text
python scripts/weil_endpoint_absorption_certificate.py --output-json computations/.../data/endpoint-absorption-rational.json
```

### `weil_exact_constants.py`

Supports `A-20260821-003`. It uses python-flint/Arb to enclose the exact transcendental constants needed by future interval certificates, including `tau=log(2)/T`, `c_2=log(2)/sqrt(2)`, and `c_T=log(2*pi*T)+EulerGamma` at `T=7/20`.

```text
python scripts/weil_exact_constants.py --prec 256 --output-json computations/.../data/exact-constants-arb.json
```

### `weil_exact_prime_complement_certificate.py`

Supports `A-20260821-004`. This is a proof-path Arb script with exact rational inputs. It certifies that the globally absorbed `0.69V` residual target is negative on `P_0-P_2`, verifies the exact-prime value is positive on that same test, and derives the crude rigorous Legendre-complement bound `mu_N=H_N-c_T-c_2-rho_R`.

```text
python -m scripts.weil_exact_prime_complement_certificate --prec 224 --max-n 30 --residual-order 32 --output-json computations/.../data/certified-complement.json
```

Its retained JSON uses exact rational interval endpoints for proof quantities. It does not prove full first-prime positivity.

## Canonical one-prime continuation workflow

For ordinary one-prime continuation research, use `scripts.weil_continuation_driver`. It is the canonical pre-theorem workflow and owns reconnaissance, convergence classification, dimension selection, rigorous precision escalation, conditioning-incident handling, exact candidate construction, and the self-contained continuation bundle.

The standalone continuation scripts remain supported research instruments and implementation components. Use them for isolated diagnostics, debugging, or historical reproduction; do **not** manually chain them as the ordinary continuation workflow.

### `weil_continuation_driver.py`

Canonical pre-theorem continuation driver. It accepts an exact rational support and an explicit dimension list or range, runs three increasing reconnaissance resolutions derived from the requested maximum dimension, then rigorously screens only the smallest stable-positive dimension and its next larger fallback. Rigorous screening and candidate checks use the persistent cache `.cache/continuation-driver` by default; cache keys include support, dimension, precision, residual order, witness/rounding parameters, and a fingerprint of the continuation source files plus `uv.lock`. It accepts only the strict `log(2)/2 < T < log(3)/2` p=2-only support window. It never extrapolates dimensions, invokes the theorem exporter, edits the closed contract, or grants theorem status.

```text
uv run --locked python -m scripts.weil_continuation_driver \
  --support 19/40 \
  --n-min 48 \
  --n-max 80 \
  --n-step 4 \
  --output-dir computations/.../data/continuation-T019-040
```

An explicit dimension list can be supplied instead:

```text
uv run --locked python -m scripts.weil_continuation_driver \
  --support 19/40 \
  --n 48,52,56,60,64,68,72 \
  --output-dir computations/.../data/continuation-T019-040
```

The default terminal output is a concise human summary; pass `--json` when the full result object is needed on stdout. The bundle remains the durable audit artifact.

`CANDIDATE_READY` is generator-side evidence only and does **not** authorize theorem admission. The driver stops there. A separate human/research decision must first admit the exact support/dimension pair to the closed theorem contract; only after that separate change may a fresh independent Rust replay establish theorem status.

The driver escalates matrix rounding bits and witness bits independently when candidate construction fails. Rounding, witness, mathematical-negative, and insufficient-precision outcomes remain distinct.

### `weil_legendre_schur_scout.py`

**Diagnostic/component tool.** Use this directly for isolated floating reconnaissance or historical reproduction, not as the first manual step of the ordinary continuation workflow.

```text
python -m scripts.weil_legendre_schur_scout --support 2/5 --max-mode 120 --quadrature-order 700 --shift-order 350 --n 32,40,48,56,64,72 --output-json computations/.../data/dimension-scout-T040.json
```

This script is reconnaissance only. Its finite tail truncation is not an infinite-dimensional bound and cannot certify positivity.

### `weil_support_continuation_scout.py`

**Diagnostic/component tool.** Use this directly for isolated rigorous full-tail diagnostics or historical reproduction; ordinary continuation precision search is owned by the canonical driver.

Supports `A-20260826-001`. It reuses the exact-polynomial/Arb full-tail assembler at exact rational support values, then converts only normalized matrix midpoints to NumPy/SciPy for support-margin reconnaissance. It reports `mu_N`, finite-block midpoint minima, Schur midpoint minima, and component penalty scales. Positive rows are not theorem certificates.

```text
python -m scripts.weil_support_continuation_scout --supports 7/20,3/8,2/5,17/40,9/20 --dimension 32 --prec 112 --output-json computations/.../data/support-scan.json
```

### `weil_support_candidate_check.py`

**Diagnostic/component tool.** Generator-side exact candidate checker for a deliberately selected continuation point. It performs rigorous Arb assembly, outward dyadic rational rounding, exact rational Schur construction, and exact rational congruence/Gershgorin checks. Ordinary continuation candidate search is owned by the canonical driver. This standalone checker deliberately does **not** emit a theorem certificate, modify the closed contract, authorize admission, or invoke the independent verifier.

```text
python -m scripts.weil_support_candidate_check --support 2/5 --dimension 40 --prec 256 --matrix-bits 72 --witness-bits 40 --output-json computations/.../data/candidate-T040-N40.json
```

### `cert/exact_prime_schur_certificate.py`

Proof-path exporter for the closed `exact_prime_legendre_schur` whitelist. It assembles rigorous exact-prime Legendre-Schur certificates, outward-rounds Arb matrices to exact dyadic rational intervals, derives exact rational parity congruence witnesses from rational midpoint `LDL^T`, and exports only explicitly admitted support/dimension pairs.

Current admitted examples:

```text
python -m scripts.cert.exact_prime_schur_certificate --claim C-0050 --support 7/20 --dimension 32 --prec 160 --matrix-bits 64 --witness-bits 32 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0051 --support 2/5 --dimension 40 --prec 256 --matrix-bits 72 --witness-bits 40 --output-json computations/.../data/certificate-T040-N40.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0052 --support 17/40 --dimension 48 --prec 384 --matrix-bits 88 --witness-bits 48 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0053 --support 9/20 --dimension 56 --prec 512 --matrix-bits 104 --witness-bits 56 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0054 --support 19/40 --dimension 68 --prec 384 --matrix-bits 64 --witness-bits 32 --output-json computations/.../data/certificate.json
```

The generator does not decide the theorem. `crates/rh_cert` independently validates the whitelisted pair, reconstructs the complement lower bound and factor-3 Schur matrix, and proves the parity blocks positive using exact rational interval congruence/Gershgorin checks. The retained theorem runs are `X-20260821-005`, `X-20260826-001`, `X-20260826-002`, `X-20260826-003`, and `X-20260827-002`.

### `cert/verify_retained_proofs.py`

Canonical retained-theorem artifact acceptance gate. It loads the closed manifest at `computations/retained-proofs.json`, validates its five registered proof identities, hashes the exact certificate bytes, and replays every hash-valid artifact through the current independent zero-float `rh_cert` verifier.

```text
uv run --locked python -m scripts.cert.verify_retained_proofs
```

A successful run ends with `RETAINED PROOF CHAIN: PASS - 5/5`. The command is fail-closed and reports `MISSING`, `HASH_MISMATCH`, `VERIFIER_ERROR`, `THEOREM_FAILURE`, or `SEMANTIC_MISMATCH` per theorem while continuing through the full manifest. It **does not regenerate certificates** and it does not grant theorem status to a new support/dimension pair. It answers the narrower audit question: are the exact proof artifacts currently cited by the repository still byte-intact and accepted by the current independent verifier?

Fast manifest-only validation remains available as:

```text
uv run --locked python -m scripts.cert.verify_retained_proofs --manifest-only
```

The real five-artifact pytest acceptance is deliberately excluded from ordinary test runs and can be invoked explicitly with:

```text
uv run --locked --extra test python -m pytest -q -m retained_proofs tests/test_retained_proofs_acceptance.py
```

### `cert/legendre_schur.py`

Rigorous shared assembly for the exact-prime Legendre-Schur proof and continuation work. It uses exact rational polynomial algebra for Legendre actions and overlap identities, Arb only for transcendental enclosures, closed logarithmic/log-squared moments for `G_V`, exact edge-overlap geometry for `G_2`, and the canonical Suzuki residual series plus rigorous remainder for `G_R`. The reusable assembler accepts an exact rational one-prime support `T`; theorem-specific certificate wrappers remain responsible for locking allowed supports/dimensions.

## Shared implementation

`rh_tools.py` contains the standard-library Laguerre recurrence, prime sieve, von Mangoldt prime-power enumeration, pole parameters, high-precision trace accumulation, Simpson integration, turning-scale helpers, numerical zeta-zero evaluation via pinned `mpmath`, the retained small-`u` phase approximation, and the exact uniform pre-turning stationary map derived in `A-20260820-005`.

## Interpretation rule

These scripts can:

- falsify proposed identities or bounds;
- reveal numerical localization and scaling;
- expose phase loss caused by absolute values;
- identify unstable cutoff regimes;
- guide which analytic lemma is worth attempting.
They cannot prove RH by numerical verification. Retained historical/manual research runs use the established `computations/` record structure (`record.md`, `plots/`, `data/`) with exact parameters and limitations. Canonical continuation-driver runs use the driver's self-contained continuation bundle (`summary.json`, scout/rigorous artifacts, candidate data, and `run-manifest.json`). Both formats must retain enough parameters, provenance, and limitations for audit and reproduction.
