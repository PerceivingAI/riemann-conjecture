# Exact-prime Legendre-Schur certificate at T=17/40

- **Computation ID:** `X-20260826-002`
- **Created:** `2026-08-26T18:31:25Z`
- **Last updated:** `2026-08-26T18:31:25Z`
- **Type:** `RIGOROUS FULL-TAIL ASSEMBLY / EXACT RATIONAL CERTIFICATE / INDEPENDENT RUST VERIFICATION`
- **Supports:** `A-20260826-001`, `F-20260826-003`, `C-0052`
- **Git commit recorded by certificate generator:** `b5405a9347a8b6bc6d3a8c022c4e0fa60e425361`
- **Generator dirty state:** `true` (explicitly retained in certificate provenance)

## Objective

Test the next one-prime continuation point

```text
T=17/40=0.425,
N=48,
```

using the same rigorous exact-prime Legendre-Schur architecture that proved `C-0050` and `C-0051`, while using enough Arb precision to avoid the known high-degree monomial-conditioning failure.

## Proof architecture

The proof uses the exact Suzuki localized form with the exact `p=2` compressed translation and canonical residual normalization. For the first `N=48` Legendre modes, the generator rigorously encloses

```text
A_48,
G_V,
G_2,
G_R,
```

and derives the high-mode complement lower bound

```text
mu_48 = H_48 - c_T^hi - c_2^hi - rho_R^hi.
```

The sufficient Schur matrix is

```text
S_48 = A_48 - (3/mu_48)(G_V + G_2 + G_R).
```

The even and odd `24 x 24` blocks are supplied with exact rational lower-triangular congruence witnesses. Rust independently reconstructs the complement bound and Schur matrix and verifies strict positive interval Gershgorin margins after exact rational congruence.

## High-precision candidate stage

The full-tail exact-polynomial/Arb assembly was run at `384` bits:

```text
python -m scripts.weil_support_continuation_scout --supports 17/40 --dimension 48 --prec 384 --output-json computations/2026-08-26T183125Z-seventeen-fortieths-schur-certificate/data/full-tail-T0425-N48.json
```

The retained midpoint diagnostics are reconnaissance only, but show the expected scale:

```text
mu_48 lower midpoint diagnostic ~ 0.7326484380944506
finite A_48 minimum midpoint eigenvalue ~ 5.86139746887575e-5
full-tail Schur midpoint minimum eigenvalue ~ 5.52986775504016e-5
```

The generator-side exact candidate used `88`-bit outward dyadic matrix intervals and `48`-bit dyadic rational congruence witnesses:

```text
python -m scripts.weil_support_candidate_check --support 17/40 --dimension 48 --prec 384 --residual-order 32 --matrix-bits 88 --witness-bits 48 --output-json computations/2026-08-26T183125Z-seventeen-fortieths-schur-certificate/data/candidate-T0425-N48.json
```

All exact rational candidate margins were positive.

## Proof certificate generation

After the closed v1 whitelist was extended only by the pair `(17/40,48)`, the full theorem certificate was generated with:

```text
python -m scripts.cert.exact_prime_schur_certificate --claim C-0052 --support 17/40 --dimension 48 --prec 384 --matrix-bits 88 --witness-bits 48 --output-json computations/2026-08-26T183125Z-seventeen-fortieths-schur-certificate/data/certificate.json
```

The serialized exact complement lower bound is

```text
224071698160852932949382266409674305902789201
------------------------------------------------
305837952434106425451293864644226406835814400
```

so

```text
mu_48 > 0.7326484380944506.
```

## Independent Rust replay

The retained proof object was verified independently with:

```text
cargo run -q -p rh_cert -- verify --cert computations/2026-08-26T183125Z-seventeen-fortieths-schur-certificate/data/certificate.json --json
```

The verifier returns:

```text
passed=true
claim=C-0052
verified_scope=localized_weil_positivity_T_17_40
dimension=48
support_T=17/40
even block dimension=24
odd block dimension=24
```

The exact positive margins are approximately

```text
mu_48       > 0.7326484380944506
even margin > 0.0028958690673761525
odd margin  > 0.010715413283695166.
```

## Adversarial replay

The real certificate was mutated in two different ways and the temporary files were deleted after testing.

1. Replacing the exact Schur factor `3` by `2` causes a contract rejection with verifier exit code `2`.
2. Replacing the `(0,0)` finite matrix interval by the exact point `-1` preserves the structural contract but destroys positivity; Rust returns `passed=false` with exit code `1`.
3. The unchanged retained certificate returns `passed=true` with exit code `0`.

Python schema semantics agree: the malformed factor is rejected while the theorem-breaking matrix perturbation remains contract-valid and is left to theorem verification.

## Artifact hashes (SHA-256)

```text
684108e373725ddf442914b34e382ad6ef459e82c686ce0d2020e4a8f30947e4  data/full-tail-T0425-N48.json
f788011d4ec7738bd07f7ca295c32ca46cf8fc5dc8fd9280d379c5c4540b4241  data/candidate-T0425-N48.json
6c74a386097bb30c2924f70d82e90d5ffc4d2dcb029543b7c973949948bdd325  data/certificate.json
0378e6419b322eca7fc077271b1694bcb43e916592969e26827387aa8489958c  data/rust-verification.json
```

Relevant implementation hashes at theorem registration:

```text
df2ca408c2d6d61017319c09ea4f11d50231a325e2d757c4d3293a3e6d4bb930  scripts/cert/exact_prime_schur_certificate.py
a54b7508d9dee2db54db71be66f05a0f14b170e1ddead675df5e52f6d34587f6  scripts/cert/export_certificate.py
5aa1ba87b1d70d6c5dfcfa252dff3b2b0d2b035623fe4e3d8d4619f04f8bd417  crates/rh_cert/src/cert.rs
5855ccdf5a1203948d22c94fe70e6f3e4747b23c804bf79006cb7b52ded8e88b  docs/contracts/rh-weil-certificate-v1.json
```

## Limits

This computation proves one finite-support localized Weil theorem at `T=17/40`. It does not establish positivity at nearby supports, does not cross the `p=3` threshold, and does not prove RH.

The generator provenance is explicitly dirty. The theorem evidence is the retained exact certificate plus the independent verifier replay and the separately established analytic/formal soundness of the Legendre complement, Schur reduction, and congruence/Gershgorin judge.

## Conclusion

`C-0052` is supported as `VERIFIED`: Suzuki's localized Weil quadratic form is strictly positive at `T=17/40` under the exact-prime `N=48` certificate. The one-prime continuation attempt remains active; the next candidate region is `T=9/20=0.45`, where earlier reconnaissance suggested a larger cutoff near `N=56`.
