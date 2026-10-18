# X-20261018-001 — v3 acceptance hardening and independent candidate replay

- **Created:** 2026-10-18T00:42:00Z
- **Type:** PROOF_SYSTEM_HARDENING / ADVERSARIAL_CONTROLS / FULL FIXED-SUPPORT REPLAY
- **Status:** **PASS — HARDENED RESEARCH TWO-GATE REPLAY; CLEAN PROOF-BEARING ARTIFACT STILL NOT PRODUCED; NO THEOREM ADMITTED**
- **Prior:** [X-20261017-007](../2026-10-17T222400Z-v3-research-bundle/record.md) and [F-20261017-016](../../findings/2026-10-17T224310Z-v3-combined-schur-proof-system-implementation.md).
- **Candidate:** exact unchanged historical v3 research artifact at `T=11/20,N=192`, SHA-256 `1855d3b28ba6f9e76f2bbfa459f0893e57db85d915393212664a8b48780a7ea0`.
- **Repository:** `main` HEAD `bae1b975abc053f6aba12972621b540110b9b2f9`; preexisting and SYS-5 changes uncommitted, preserved.

## 1. Identified and corrected implementation acceptance issues

1. **Candidate-file time-of-check/time-of-use mismatch.** The original bundle checker decoded the candidate from a file after separately reading its bytes and had Rust reopen the original path later. Now both source Gate A and Rust Gate B operate on the **same initial immutable candidate byte snapshot**. The Python parser decodes the captured bytes directly, rejecting duplicate JSON keys. Rust receives a separately created temporary byte-for-byte copy; both that copy and the executable are SHA-256 checked immediately before/after Rust execution. The accepted record binds the original candidate digest and the canonical input digest. An intervening rewrite of the user's original file cannot change the checked mathematical input.
2. **Provenance label ambiguity.** The producer records **different exact scripts** for historical research exports and newly clean-generated candidates. Python, v3 schema and Rust all reject a status/script/dirty-flag mismatch. For `clean_candidate_pending_admission` the two-gate checker also requires the exact recorded HEAD commit and a clean source tree, with only the input artifact itself excluded if it is untracked. Source fingerprints are separate from and never replace the mathematical analytical checks.
3. **Rust result consistency.** The audit compares source and Rust claim/format/dimension/support, exact positive margin, explicit unadmitted status, and source-versus-Rust proof-role flags. It rejects inconsistent or unexpected reports rather than interpreting exit status alone.
4. **Adversarial trust boundary.** New Python fail-closed tests reject forged clean status and mismatched analytical-auditor source fingerprints **before** the expensive audit. A separate real 192-dimensional Rust negative control supplies a structurally valid fixed-profile **synthetic** matrix with a strictly negative Schur direction; the exact rational checker exits **1 / NONPOSITIVE_RATIONAL_SCHUR_LOWER**, not structural error 2 or theorem admission. This synthetic matrix is **NOT** a valid Suzuki analytical source enclosure and is not falsely reported as such.

No old v1/v2 certificate parser, admitted proof registration, or mathematical bound was altered.

## 2. Final bounded full-size verification

Command:

```text
uv run --locked python -m scripts.verify_combined_schur_v3_bundle --candidate computations/2026-10-17T222400Z-v3-research-bundle/data/certificate-v3-research.json --rust-binary target/debug/rh_cert.exe --output computations/2026-10-18T004000Z-v3-gate-hardening-replay/data/two-gate-audit-hardened.json
```

**Exit 0**. Separate independent Arb-2048 assembly took 54.025 seconds; overall command completed normally.

| Independent acceptance | Executed outcome |
|---|---|
| Complete \(N=192\) low-form intervals | **18,528 / 18,528 strictly contained** |
| Complete combined \(V/P/R_K\) Gram intervals | **18,528 / 18,528 strictly contained** |
| Positive complementary scalar interval \(\mu\) | **Contained** |
| Full Suzuki residual scalar interval \(\delta_K\) | **Contained** |
| Exact Rust full conservative Schur/congruence | **Strict positive margin; PASS** |
| Exact rational margin vs original SYS-4 witness | **EQUAL** |
| Claim/format/support/trust/byte-snapshot binding | **PASS** |
| Admitted theorem | **NO** |

Output `data/two-gate-audit-hardened.json` SHA-256 `a69f4d9c9e1e38185228502de59abe7822af5d8c0ff44c792e5c576d018fa40e`. Canonical exact input SHA-256 remains `6c5afa8958cc47750290776ce3cd59cd7873a34d03d148fcfa8e90afb69aea63`.

## 3. Scoped regression and negative-control results

- Python v1/v2/v3 and analytical source focused suite: **37 / 37 PASS**, including new forged clean-producer and source-fingerprint controls.
- Additional full-profile v3 *synthetic structurally valid but analytically invalid negative* Rust CLI test: **1 / 1 PASS**, returns exact rational mathematical failure with exit 1 and `theorem_admitted=false`.
- Full Rust `cargo test -p rh_cert --quiet`: **73 / 73 PASS**, including frozen existing v1/v2 and the new v3 tests.
- `cargo fmt --all`, `cargo clippy -p rh_cert --all-targets -- -D warnings` and `cargo build -p rh_cert --quiet`: **PASS** after the provenance updates.
- Prior SYS-5.3 full Lean `lake build Cert`: **PASS**; no Lean sources were modified during this hardening run.
- The clean-source producer's rejection of a dirty source tree, and ordinary production Rust `verify` rejection of v3 due to its empty admission list, were confirmed in the preceding [X-20261017-007](../2026-10-17T222400Z-v3-research-bundle/record.md).

### As-executed source SHA-256

- `scripts/verify_combined_schur_v3_bundle.py`: `ebd79b5763d2f1bca3c2919b7db05e4d689d874bdd7586974fbf3cbfe4f5355f`
- `scripts/cert/export_combined_schur_v3.py`: `756308a22161b91cdcec2f169cc6003322fec94f588fa7634dceca2fb71edf9d`
- `scripts/cert/export_combined_schur_v3_clean.py`: `eabb3a27d7917db3ec5b83c6c6ed1413d45ec70121ee4baed2e4470c8ddffa84`
- `crates/rh_cert/src/v3.rs`: `5bf954c658c32fb2126fc8e7071c341b2373e93ea9d8ccbeeec0193d48509990`
- `docs/contracts/rh-weil-certificate-v3.json`: `48e6185bb891498a4700b85b127b51c357b0ee9c95a1b80eb58ac47ac1b96880`

## 4. Remaining hard completion boundary

The current research candidate is an original uncommitted-source certificate with **honest dirty provenance**. The guarded code for fresh clean-source proof-bearing generation exists but cannot correctly execute from this dirty project state, and **no automatic repository commit or push** was performed. Therefore **no clean-committed candidate has yet been generated or independently replayed**, and the strict proof-bearing completion condition of SYS-5.3 **remains open**.

This is an engineering/provenance gate, not a failed matrix positivity test. It is distinct from any future **explicit theorem-admission decision**. The research-only result cannot be silently added to the retained-proof ledger or reported as RH.
