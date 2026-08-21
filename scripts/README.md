# Research scripts

- **Created:** `2026-08-20T20:59:00Z`
- **Last updated:** `2026-08-21T08:56:20Z`

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

### `weil_legendre_schur_scout.py`

Supports dimension selection for `A-20260821-004`. It uses NumPy/SciPy floating point to assemble normalized-Legendre exact-prime finite matrices and **finitely truncated** tail Grams for the factor-3 Schur reduction.

```text
python -m scripts.weil_legendre_schur_scout --max-mode 120 --quadrature-order 700 --shift-order 350 --n 18,20,22,24,28,32,40,50 --output-json computations/.../data/schur-scout.json
```

This script is reconnaissance only. Its finite tail truncation is not an infinite-dimensional bound and cannot certify positivity.

## Shared implementation

`rh_tools.py` contains the standard-library Laguerre recurrence, prime sieve, von Mangoldt prime-power enumeration, pole parameters, high-precision trace accumulation, Simpson integration, turning-scale helpers, numerical zeta-zero evaluation via pinned `mpmath`, the retained small-`u` phase approximation, and the exact uniform pre-turning stationary map derived in `A-20260820-005`.

## Interpretation rule

These scripts can:

- falsify proposed identities or bounds;
- reveal numerical localization and scaling;
- expose phase loss caused by absolute values;
- identify unstable cutoff regimes;
- guide which analytic lemma is worth attempting.
They cannot prove RH by numerical verification. Every retained run belongs in `computations/` as a self-contained directory bundle (`record.md`, `plots/`, `data/`) with exact parameters and limitations.
