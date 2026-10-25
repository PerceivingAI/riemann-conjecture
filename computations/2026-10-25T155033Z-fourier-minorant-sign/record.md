# Complete fixed Fourier-minorant source and sign experiment

- **Computation ID:** `X-20261025-006`
- **Created:** `2026-10-25T15:50:33Z`
- **Last updated:** `2026-10-25T18:25:39Z`
- **Status:** `COMPLETE` corrected full source independently accepted and both exact sufficient blocks positive

## Objective

Evaluate the actual fixed bounded Fourier minorant of C-0094. Seek a genuine negative direction first. Positive probes alone do not establish positivity, so the positive branch requires a complete finite sufficient matrix and the already qualified infinite complement.

## Mathematical quantities

T=1353/2048,a=7/2,Omega256,N312 remain fixed throughout. Ordinary unnormalized Legendre degrees0,...,311 have mass D_j=2/(2j+1). The complete source matrices are P,P²,GP,pole,band,A, with GP=P²-PD^-1P and A=aD+P+pole+band. Both mixed prime products and the negative odd pole are retained.

The full exact sufficient lower is A_--[(GP)_++3e-40 D]/(19/8-1e-82). Positive exact rational congruences in both156-dimensional parity blocks, combined with the SHA-bound C-0094 infinite-complement premise, prove H0>0 on the whole Hilbert space. The source split then gives smooth-test Weil positivity. This is a different reference proof at an already positive support, not a new support theorem.

The complete analytical accounting is in [matrix-enclosure-derivation-v1.md](matrix-enclosure-derivation-v1.md). The independently written [qualification](independent-direction-qualification.md) records the initial directional and subsequent operator-quadrature reasoning before execution. Its unevaluated statements describe that stage, not the final outcome.

## Environment and implemented operations

- Python3.14.0 and python-flint0.9.0; NumPy/SciPy versions and interpreter details are captured in [environment.json](data/environment.json).
- Source Arb512,128 fractional outward bits, polynomial Gauss312 and frequency Gauss48 on all exact panels.
- Independent source Arb768, polynomial Gauss313 and frequency Gauss64, with separately derived weights and finite hypergeometric anchors of order384 plus explicit tails.
- Floating reconnaissance is explicitly non-proof. Its eigenvectors and numerical Cholesky inverses are proposals only.
- Exact positivity uses rational interval Loewner bounds, rational congruences, nonsingularity and exact Gershgorin margins. No floating sign establishes the result.
- Existing generic active-term/partition code and existing exact witness helpers are reused unchanged. No prior positive K312 packet or witness is an analytical premise.

Canonical modules are [`scripts.weil_fourier_minorant_scout`](../../scripts/weil_fourier_minorant_scout.py), [`scripts.weil_fourier_minorant_matrix`](../../scripts/weil_fourier_minorant_matrix.py) and [`scripts.verify_fourier_minorant_matrix`](../../scripts/verify_fourier_minorant_matrix.py). Snapshot closures [source-v1/manifest.json](source-v1/manifest.json) and [source-v2/manifest.json](source-v2/manifest.json) preserve exact executable versions. The research packet's version2 is not the production Weil certificate-v2 format.

## Executed sequence and outputs

The two non-proof band quadrature resolutions64 and96 gave positive full H0 minima in both parities. Both retained C-0091 directions were positive too. This did not settle the sign. The complete source/proof branch followed rather than treating those directions as a certificate.

The first producer had an arithmetic coefficient defect. The canonical API's coefficient already multiplies each one-sided shift, but the consumer divided by two again. The original [source-v1.json.gz](data/source-v1.json.gz), failed proof and [initial executable](development/producer-initial.py) are preserved. A minimized constant-trial control detects half P and quarter P², with [before](data/coefficient-regression-before-v1.json) and [after](data/coefficient-regression-after-v2.json) results. The original version is invalid for the intended H0, not a mathematical negative result. Its original failed proof remains reproducible through the frozen source-v1 closure.

The corrected packet is [source-v2.json.gz](data/source-v2.json.gz), SHA256 `6f8994ee0d8813ddd0bbb3ba88e35b2070905199693788f9660906474edbeb66`. The exact [proof-v2.json.gz](data/proof-v2.json.gz), SHA256 `02ee0e095a23c6c09949fe51b0833d541cb76a3298402d84609950619b07612d`, includes both complete congruences.

| Complete finite sufficient block | Certified mass-normalized lower display |
| --- | --- |
| Even | 1.3995633634664128e-11 |
| Odd | 8.213611938461616e-9 |

These are not full-form spectral minima. The complete quadrature operator-error upper is1473109368278075125/340282366920938463463374607431768211456, displaying4.329079351385665e-21. Every source entry pays its appropriate physical-mass error.

The [independent audit](data/independent-audit-v2.json) checks48828 entries in each of six matrices,292968 in total. Its fresh narrower enclosures are contained in the published bounds. It independently verifies the complete rational sufficient lower, congruence margins and mass lower. The shared premises are Suzuki v3, C-0094 and Arb/FLINT transcendental/root correctness. This is independent source organization, not a second arithmetic library or formal kernel proof.

## Reproduction procedure

From the repository root, always choose fresh output paths:

```text
uv run --locked python -m scripts.weil_fourier_minorant_scout --order 64 --output <fresh-scout.json>
uv run --locked python -m scripts.weil_fourier_minorant_matrix source --output <fresh-source.json.gz>
uv run --locked python -m scripts.weil_fourier_minorant_matrix prove --source <fresh-source.json.gz> --output <fresh-proof.json.gz>
uv run --locked python -m scripts.verify_fourier_minorant_matrix <fresh-proof.json.gz> --source <fresh-source.json.gz> --output <fresh-audit.json>
uv run --locked python -m scripts.verify_fourier_minorant_matrix <fresh-proof.json.gz> --source <fresh-source.json.gz> --exact-only --output <fresh-exact-replay.json>
uv run --locked --extra test python -m pytest -n 0 -q tests/test_fourier_minorant_matrix.py
```

Exact-only replay deliberately reports EXACT_ONLY_PASS and rebuilds no analytical inputs. It is not a substitute for the full audit command.

Isolated reproduction uses Python `-I`, inserts only the captured source-v2 directory at the front of sys.path and invokes the same module with runpy.run_module. [Isolated proof](data/isolated-proof-v2.run.json) and [isolated exact replay](data/isolated-exact-replay-v2.run.json) retain the actual expanded commands. Source regeneration, proof regeneration and exact receipt are all byte-identical, as recorded in [isolated-replay-summary.json](data/isolated-replay-summary.json). The isolated run did not repeat the separate full768-bit audit.

## Verification and timings

| Corrected operation | Observed seconds |
| --- | --- |
| Fresh source generation | 25.12 |
| Exact positive witness construction/check | 3.01 |
| Complete fresh independent audit | 73.30 |
| Separate exact-only replay | about1.91 |
| Isolated source regeneration | 24.92 |

These are operation receipts, not a controlled end-to-end comparison to the older physical pipeline. They omit reconnaissance, debugging, documentation and other verification. No matched-workload speedup or global scaling law is inferred.

Four focused regressions pass. Five altered report/source-binding cases are actually rejected: changed band input, unpaid complement, forged margin, forged mass lower and singular transform. [Rejection summary](data/rejection-summary-v2.json) and individual receipts retain exact inputs and error outcomes; no success output is written. These controls exercise byte/source binding and exact consequences, not five repeated analytical source reconstructions. The unmodified source receives the full independent audit separately.

The compressed source packets exceed2MB because their exact enclosure bytes are retained trust evidence, not optional plotting data. Their deterministic regeneration commands, sizes, hashes, original invalid version, exact proof and audit are preserved. The altered proof fixtures are retained too so the recorded rejections can be replayed directly.

## Interpretation and limits

C-0096 / [F-20261025-006](../../findings/2026-10-25T155033Z-positive-fourier-minorant.md) closes this fixed whole-space bounded-minorant sign question. It establishes a complete alternative reference proof without inheriting the old positive physical construction. The new finite-band source and independent checker are implemented and exercised, not specifications for future tools.

No new support, unbounded support family, external originality finding, full operator-domain identification, production certificate/profile, Rust/Lean acceptance or theorem admission is established. The4 transition and larger-support constants/costs were not tested. C-0087 already proves smooth-test positivity at this support under its own different documented premises. All original source/test/theorem records retain their historical identity. Admissions remain8v1/0v2/1v3; RH is unresolved.

## Integrity and timestamped corrections

The final root manifest is written last and seals nested source manifests as ordinary members. It excludes only itself. The source-v1 arithmetic normalization defect and its corrected version2 are recorded as distinct runs. No earlier finding, frozen arithmetic API or historical result was silently revised.

### Primary source checks, 2026-10-25T18:25:39Z

The exact Legendre Fourier normalization and Gaussian positive-weight/exactness statements were checked directly in [DLMF10.54.2](https://dlmf.nist.gov/10.54.E2) and [DLMF3.5(v)](https://dlmf.nist.gov/3.5#v), registered as R-0037. No external implementation was imported.

### Diagnostic and metadata limits

One exploratory diagnostic printed the defective arithmetic coefficients and source entries, then timed out before completing additional floating scalar integrals. No accepted sign or bound relies on those unfinished integrals. The decisive checks use the recorded canonical CLIs and exact inputs above. Public command metadata uses repository-relative paths; local workspace prefixes were removed before publication without changing numerical output or method identity.

The permanent constant-overlap/combined-square regression was also executed against the frozen defective source-v1 closure. It fails as expected; [the actual receipt](data/preserved-v1-regression-test.run.json) preserves that failing-before check. The corrected complete four-test file passes separately.
