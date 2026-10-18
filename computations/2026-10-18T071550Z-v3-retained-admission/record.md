# SYS-5.4: independently replayed v3 retained theorem admission

- **Computation ID:** X-20261018-003
- **Created:** 2026-10-18T07:18:03Z
- **Last updated:** 2026-10-18T07:28:19Z
- **Type:** FIRST-CLASS RETAINED FINITE-SUPPORT CERTIFICATE ADMISSION / INDEPENDENT MATHEMATICAL REPLAY
- **Decision:** **PASS — ONE EXACT ADMITTED V3 CONFIGURATION ONLY**
- **Claim:** C-0067; support T=11/20; Legendre dimension N=192; Suzuki smooth-test-class positivity.
- **Mathematical source revision:** clean pushed `f0350f89ec5189648cfc271c4ddd3a97355a2343`. The admission changes themselves are local working-tree changes pending separate commit/review.
- **Previously generated immutable proof input:** [X-20261018-002](../2026-10-18T010000Z-v3-clean-proof-candidate/record.md).
- **Replayed receipt:** [data/replay.json](data/replay.json), SHA-256 `37cdc433bc9b2a4f3438cc8d4b6db0e08f19f2078fcc0cb01f4c25a7d96293a6`.

## Closed inputs and reproducer

- v3 approved exact certificate path: `computations/2026-10-18T010000Z-v3-clean-proof-candidate/data/certificate-v3-clean.json`.
- Raw-byte SHA-256: `f9948f22010d258d1c01c988fd0f18a3110c3c13453473c8c48953560a7fffcb`; clean producer Git commit embedded in certificate matches the committed source.
- Explicit separate v3 manifest `computations/retained-proofs-v3.json` has exactly `C-0067`, no inferred additional configuration. Manifest SHA-256 during replay: `938a6530728647314b726ee2421518436da13d2037e47d0780a9fe5ad5fca650`.
- Mathematical input hash (canonical analytical packet) `6c5afa8958cc47750290776ce3cd59cd7873a34d03d148fcfa8e90afb69aea63`.
- Independent Arb analytical source SHA-256: `15961f4b337e1d26cc63aa41bcb3976fa975636d0b5e006b0f51bd3d625576e4`.
- Executed exact Rust binary SHA-256: `607589cac23c1873f1d667558c8a959efdcbb0596e05ba7884a7db219a00f99c`.

From repository root, build Rust and run:

```text
cargo build -p rh_cert --locked
uv run --locked --extra test python -m scripts.cert.verify_retained_v3 --output computations/2026-10-18T071550Z-v3-retained-admission/data/replay.json --rust-binary target/debug/rh_cert.exe
```

The script checks closed manifest identity, original byte SHA, source Git history and current source bytes, clean producer metadata, independently recomputes all mathematical input intervals at 2048-bit Arb precision, then runs production `rh_cert verify` on a separate captured immutable copy of those exact bytes. It verifies PASS scope, strict exact Gershgorin and both parity sectors, and checks the proof, manifest, source and Rust executable did not change during replay. It writes its result only on success.

## Observed results

- **Arb-2048 independent analytic intervals:** all 18,528 low entries plus all 18,528 complete mixed-Gram entries strictly contained within admitted rational input bounds; `mu_contained=true`, `delta_contained=true`; failures 0.
- **Zero-float Rust production verification:** exit 0; `passed=true`, `claim=C-0067`, `format=rh-weil-certificate-v3`, `claim_profile=combined_multi_prime_legendre_schur`, exact `support_T=11/20`, `dimension=192`, `parity_sector=both`.
- **Exact rational proof:** even and odd parity congruences each invertible and strictly Gershgorin positive. Exact lower rational margin is serialized in `data/replay.json`; both displayed block margins are conservative copies of the global exact minimum.
- **Admission decision:** **one** strictly positive fixed-support Suzuki test-class claim is admitted. The old one-prime v1 proof manifest is unmodified (eight retained claims `C-0050..C-0057`); v2 remains unadmitted.

## Negative controls, trust and scope

The separate v3 malformed/alternate-manifest tests reject additional claims, altered hashes, altered scope and path traversal. A semantically identical JSON certificate with even one extra whitespace byte is refused production admission as a contract error (exit 2). The preexisting structurally valid but mathematically negative synthetic v3 input remains a research arithmetic failure (exit 1) under `verify-candidate-v3`, and is **not** an analytically certified admitted theorem. Frozen v1/v2 checker semantics were not changed.

The independent Arb verifier checks the transcendental source enclosures; Rust itself **does not** prove those analytic inputs, Suzuki's source theorem, Arb primitive correctness or the full canonical operator-domain equality. The source identity on `C_c^∞(-T,T)` is the precise applicable test class; full domain equality is **not** asserted and is not needed for that scoped form statement. No positivity for all support values and **NO RIEMANN HYPOTHESIS PROOF** results. The isolated finite-support result is not generalized by continuity, interpolation or an unverified support grid.

The admission implementation and manifest were uncommitted when this execution completed; the historical mathematical-source revision is separately pinned to the clean pre-admission commit above. The saved receipt records the actual executed Rust binary hash, not a claim that a later rebuild has identical bytes.

## 2026-10-18T07:28:19Z — Final admission and frozen-v1 regression closure

The independent new-v3 acceptance above remains unchanged. Post-admission validation performed on this worktree:

- `uv run --locked --extra test python -m pytest -q -n 0 tests/test_retained_v3_admission.py`: **7/7 PASS**, including closed manifest and reencoded-certificate rejection.
- `cargo test -p rh_cert --locked`: **74/74 PASS**, including new v3 exact-artifact rejection tests, old v1/v2 independent proof semantics and research valid-negative controls.
- `cargo clippy --locked -p rh_cert --all-targets -- -D warnings`: **PASS**.
- `cargo fmt --all -- --check` and `git diff --check`: **PASS**.
- `uv run --locked --extra test python -m scripts.cert.verify_retained_proofs`: **8/8 PASS**, explicitly C-0050..C-0057 with hash + independent Rust replay; exit 0, no stderr. The v1 manifest was not modified.
- The combined-Schur Lean soundness lemmas are unchanged; **no claim is made that the full v3 source/Arb proof is Lean-formalized**.
- This completes SYS-5.4 only for the exact finite-support `C-0067`. No further v2/v3 support was admitted. **No Git commit/push performed**.
