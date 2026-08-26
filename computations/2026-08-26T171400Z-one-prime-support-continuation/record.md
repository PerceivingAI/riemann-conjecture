# One-prime support continuation map and T=2/5 exact certificate

- **Computation ID:** `X-20260826-001`
- **Created:** `2026-08-26T17:14:00Z`
- **Last updated:** `2026-08-26T17:49:29Z`
- **Type:** `MIXED RIGOROUS-ASSEMBLY RECONNAISSANCE / INDEPENDENT EXACT CERTIFICATE`
- **Supports:** `A-20260826-001`, `F-20260826-001`, `C-0051`
- **Git base during work:** `6dd1d8f07e23dd39fcd2e36974c53a5054f810ec`

## Objective

Map how the exact-prime Legendre-Schur mechanism from `C-0050` changes as support `T` increases inside the one-prime window, identify the first failing component, determine whether a larger Legendre cutoff repairs it, and select one next support value for independent rigorous certification.

## Trust separation

Three evidence levels are retained separately:

1. `support-scan*.json` and `full-tail-*.json`: exact-polynomial/Arb full-tail assembly, followed by floating midpoint eigenvalue/norm diagnostics. The underlying entries are rigorous, but the reported eigenvalues are reconnaissance.
2. `dimension-scout-*.json`: fully floating orthonormal-Legendre Gauss-quadrature reconnaissance with finitely truncated tail Grams. These files are dimension-selection evidence only.
3. `candidate-T040-N40.json`: historical generator-side exact rational candidate used to select the proof target.
4. `certificate-T040-N40.json` plus `rust-verification-T040-N40.json`: proof-bearing exact rational interval certificate and independent zero-float Rust replay for `C-0051`.

## Main commands

Broad/fine full-tail maps:

```text
python -m scripts.weil_support_continuation_scout --prec 112 --output-json computations/2026-08-26T171400Z-one-prime-support-continuation/data/support-scan.json

python -m scripts.weil_support_continuation_scout --supports 71/200,9/25,73/200,37/100,3/8 --prec 112 --output-json computations/2026-08-26T171400Z-one-prime-support-continuation/data/support-scan-fine.json
```

High-precision full-tail checks:

```text
python -m scripts.weil_support_continuation_scout --supports 3/8 --dimension 40 --prec 256 --output-json computations/.../data/full-tail-T0375-N40.json
python -m scripts.weil_support_continuation_scout --supports 2/5 --dimension 40 --prec 256 --output-json computations/.../data/full-tail-T040-N40.json
python -m scripts.weil_support_continuation_scout --supports 17/40 --dimension 40 --prec 256 --output-json computations/.../data/full-tail-T0425-N40.json
python -m scripts.weil_support_continuation_scout --supports 9/20 --dimension 40 --prec 256 --output-json computations/.../data/full-tail-T045-N40.json
```

Stable truncated-tail dimension reconnaissance:

```text
python scripts/weil_legendre_schur_scout.py --support 3/8 --max-mode 120 --quadrature-order 700 --shift-order 350 --n 28,32,36,40,48,56,64 --output-json computations/.../data/dimension-scout-T0375.json
python scripts/weil_legendre_schur_scout.py --support 2/5 --max-mode 120 --quadrature-order 700 --shift-order 350 --n 32,40,48,56,64,72 --output-json computations/.../data/dimension-scout-T040.json
python scripts/weil_legendre_schur_scout.py --support 17/40 --max-mode 140 --quadrature-order 750 --shift-order 400 --n 40,48,56,64,72,80 --output-json computations/.../data/dimension-scout-T0425.json
python scripts/weil_legendre_schur_scout.py --support 9/20 --max-mode 140 --quadrature-order 750 --shift-order 400 --n 40,48,56,64,72,80 --output-json computations/.../data/dimension-scout-T045.json
```

Exact generator-side candidate:

```text
python -m scripts.weil_support_candidate_check --support 2/5 --dimension 40 --prec 256 --matrix-bits 72 --witness-bits 40 --output-json computations/2026-08-26T171400Z-one-prime-support-continuation/data/candidate-T040-N40.json
```

Final exact certificate and independent replay:

```text
python -m scripts.cert.exact_prime_schur_certificate --claim C-0051 --support 2/5 --dimension 40 --prec 256 --matrix-bits 72 --witness-bits 40 --output-json computations/2026-08-26T171400Z-one-prime-support-continuation/data/certificate-T040-N40.json

cargo run -q -p rh_cert -- verify --cert computations/2026-08-26T171400Z-one-prime-support-continuation/data/certificate-T040-N40.json --json
```

The retained Rust JSON output is `data/rust-verification-T040-N40.json`.

## Main observations

At fixed `N=32`, the full-tail Schur midpoint is positive at every tested support through `T=0.37`, then negative at `T=0.375`. The finite low block and rigorous `mu_32` remain positive at `0.375`, isolating the tail-Schur correction as the first failure of the fixed-dimension architecture.

At high precision with the full-tail formulas:

```text
T=3/8, N=40:  lambda_min(S)_mid ~ +4.833878461640637e-4
T=2/5, N=40:  lambda_min(S)_mid ~ +1.703016278161656e-4
T=17/40,N=40: lambda_min(S)_mid ~ -1.2834010528645523
T=9/20,N=40:  lambda_min(S)_mid ~ -4.234925915475505
```

The `T=2/5,N=40` exact candidate gives:

```text
mu_lower     ~ 0.7313021813837909
even_margin  ~ 0.004176569432300938
odd_margin   ~ 0.013120531611009081
```

All are exact rational quantities in `candidate-T040-N40.json` and strictly positive.

The final full certificate preserves the same exact lower values and independently replays in Rust with

```text
passed = true
verified_scope = localized_weil_positivity_T_2_5
even block dimension = 20
odd  block dimension = 20
```

Real-certificate adversarial replay:

```text
wrong exact Schur factor 3 -> 2      contract rejection, exit 2
contract-valid matrix (0,0) -> -1    theorem failure, exit 1
unchanged retained certificate        PASS, exit 0
```

Python semantic validation likewise rejects the factor mutation while accepting the contract-valid theorem-failure mutation.

## Precision incident

Unretained exploratory `N=40/48` midpoint runs at 104-bit Arb precision became catastrophically ill-conditioned because exact Legendre polynomials are represented in the monomial basis and large coefficients undergo severe cancellation. They were rejected as evidence. `N=40` full-tail runs used for the retained conclusions were rerun at 256 bits and agree in scale with the stable orthonormal-Legendre scout.

## Artifact hashes (SHA-256)

```text
7599ab68e232ccb1df0b6f4747c468a27db6d5ee03fd5c58beaac29283c705a9  data/support-scan.json
6ce54f099bb4bfa73750a52c439820d7b69864f7958293a82e42b2031b7ec592  data/support-scan-fine.json
e3c86ad9a179ab171a717e309c28a15dc5d40f56602fce28d6ce7df58c74bcda  data/full-tail-T0375-N40.json
4a92d496bb6074fe337d9260501b7d78565b8dc623e13dafa6fd47fd58b4a2f5  data/full-tail-T040-N40.json
c1ab7f139f9994f227a6cce6f6f00a525412f7c926f7efea13b67c9a388d39d6  data/full-tail-T0425-N40.json
9aae9634799cd7ca9a4ff19a02a197fe3f2fb736fb6aeb4737d4df0100e84445  data/full-tail-T045-N40.json
37ff9223793b6dab805dc8bc7cbb5248bfd1b3f9054e64fdad5e1182e05344d7  data/dimension-scout-T0375.json
43d63a2adaed3d477f3a25fba17d6ae826a493120a720c0968ffef6f97ada64d  data/dimension-scout-T040.json
0a70af0df80db32728fc8289788874f5564b318502599c42426050b118b5b3e8  data/dimension-scout-T0425.json
98909a89477df58adbccbad2abb151c4ab329ca7af806ccceb66b142fc9f13ff  data/dimension-scout-T045.json
b3bbada9443696944d9f80ecb78c5d66d1ac611eebdbbe84c2a679dc798fcffe  data/candidate-T040-N40.json
8f9fa235beb9b4ee3c4f7cde11732a1b0b5295a7bbc94c03857417ee8a2b1be2  data/certificate-T040-N40.json
85900f61c8105a87a19b2dfe9c4863d14fc7fbf0cef609801e435fdb0b296891  data/rust-verification-T040-N40.json
```

Relevant script hashes at the retained state:

```text
51bace1ded6eb111c99097beca9982730a19e31abc4f81337f781ae2c188f6a5  scripts/cert/legendre_schur.py
3035050a0da18341de48a462721f4e9421f869d54614708ed2cc72399bd5b8b4  scripts/weil_support_continuation_scout.py
79907a17c582928130caa85f75eae9bf2d03dfbbf0bce5ab6b39b76606160191  scripts/weil_support_candidate_check.py
017b39e669be3d1614e2192e9b62fc5e67549df34b61831ccb790ce1a90319fd  scripts/weil_legendre_schur_scout.py
```

Proof-generator/verifier sources at theorem replay:

```text
7bceb2baf3b99eee8abfc6ebd8bba6e97a1c3bfdc7770524e46dbcf34aecc1db  scripts/cert/exact_prime_schur_certificate.py
85e643ea130a27b79a65906927bcd4ad137a82392956d41987955d07ea7875b2  scripts/cert/export_certificate.py
f83310d1f9b71262775d910e5a8e75780d276128a1f3f08de4bb1cf987fc1762  crates/rh_cert/src/cert.rs
dfccb8cb69264688652d7eb53d2bd62c240e9cc1f5e5502efda16f0e9408ef8f  crates/rh_cert/src/gershgorin.rs
6fb3817e3f1d82a459d8b84df50a3283145c1726379eee15cf2bfe0ea6755392  docs/contracts/rh-weil-certificate-v1.json
```

The theorem certificate records Git commit `b5405a9347a8b6bc6d3a8c022c4e0fa60e425361` and `git_dirty=true`; the dirty state is part of the retained provenance rather than suppressed.

## Conclusion

The one-prime mechanism is not isolated at `T=0.35`. A moving Legendre cutoff restores the full-tail Schur architecture through `T=0.4`, and the retained exact certificate plus independent Rust replay prove `C-0051`: strict localized Weil positivity at `T=2/5`.

The computation does not prove a neighborhood in `T` and does not justify extrapolation to `T=17/40` or beyond. The next continuation target requires a fresh exact candidate and independent replay.
