# Predeclared exact-prime Legendre-Schur certificate at T=27/50

- **Computation ID:** `X-20260924-001`
- **Created:** `2026-09-24T18:37:15Z`
- **Last updated:** `2026-09-24T18:37:15Z`
- **Status:** `PREDECLARED — NOT EXECUTED`
- **Type:** `RIGOROUS FULL-TAIL ASSEMBLY / EXACT RATIONAL CERTIFICATE / INDEPENDENT VERIFIER`
- **Supports:** `A-20260826-001`, `X-20260923-001`, provisional `C-0057`
- **Admission freeze Git commit:** `f2d284fd85bee8995ef267450e4038768678c3a3`
- **Required generation tree state:** clean and committed; generation must not begin from a dirty working tree

## Objective

Generate a **fresh** proof-bearing exact-prime Legendre-Schur certificate for the newly admitted pair

```text
(T,N)=(27/50,104)
```

from the committed closed-contract state, then submit that exact certificate to the independent zero-float Rust verifier. The historical continuation bundle `X-20260923-001` remains pre-theorem evidence only and must not be copied, renamed, or promoted into this computation.

This declaration does not assert `C-0057`. The claim remains `PROVISIONAL` / `OPEN_REQUIREMENT` until fresh generation, independent verifier PASS, adversarial checks, and later retained-proof registration all succeed.

## Frozen admission state

Phase 3 audited the Phase 2 production diff and found no accidental broadening:

- Python theorem-generator admission adds exactly `(Fraction(27, 50), 104)`;
- the independently maintained Python semantic validator adds exactly the same pair;
- the raw JSON Schema adds `104` to the exact-prime dimension/harmonic guards but binds it through the exact-pair `oneOf` branch to support `27/50`;
- Rust adds exactly `dimension == 104 && support == 27/50` to pair admission and separately permits dimension `104`;
- the test-only corpus contains 8 allowed matched pairs, all 56 off-diagonal combinations, and 9 external forbidden controls;
- `computations/retained-proofs.json` and `EXPECTED_RETAINED_CLAIMS_V1` remain unchanged at `C-0050` through `C-0056`.

The admission implementation is frozen in commit:

```text
f2d284fd85bee8995ef267450e4038768678c3a3
```

Phase 3 quality gates before this declaration:

```text
Focused Python contract suite: 15/15 passed
cargo test -p rh_cert: PASS
cargo clippy -p rh_cert --all-targets -- -D warnings: PASS
cargo fmt -p rh_cert -- --check: PASS
retained-proof manifest-only validation: 7 registered proofs, VALID
git diff --check: PASS
```

## Software/runtime

The declaration environment is:

```text
CPython      3.14.0
python-flint 0.9.0
rustc        1.97.1 (8bab26f4f 2026-07-14)
cargo        1.97.1 (c980f4866 2026-06-30)
```

The Python computation must run through the repository lock with `uv run --locked`. The certificate metadata must record the actual clean Git commit and dirty-state flag used at execution.

## Exact parameters

```text
claim             = C-0057
support T         = 27/50
Legendre N        = 104
Arb precision     = 512 bits
residual order    = 32
matrix endpoints  = 64-bit dyadic outward rounding
witness entries   = 32-bit dyadic rationals
Schur factor      = 3
claim profile     = exact_prime_legendre_schur
tail rule         = legendre_component_gram_schur
parity sector     = both
```

`residual_order=32` and Schur factor `3` are hard-locked by the v1 generator/profile rather than exposed as free CLI parameters.

The pre-theorem candidate in `X-20260923-001` provides only a comparison target. At the same parameterization it reported approximate positive quantities

```text
mu_104       > 0.6643369939721553
even margin  > 0.0002388902594756742
odd margin   > 0.000779387887620489
```

and remained exact-margin stable under fixed-parameter 640-bit reassembly. The fresh theorem run must recompute these quantities from scratch; agreement is expected but not assumed.

## Clean-tree precondition

Immediately before generation:

```text
git status --short
git rev-parse HEAD
```

`git status --short` must print nothing. The HEAD must be a committed descendant of the admission-freeze commit above and include this predeclaration. If the tree is dirty, stop and do not generate theorem artifacts.

## Fresh proof-certificate reproduction command

Run from the repository root:

```text
uv run --locked python -m scripts.cert.exact_prime_schur_certificate \
  --claim C-0057 \
  --support 27/50 \
  --dimension 104 \
  --prec 512 \
  --matrix-bits 64 \
  --witness-bits 32 \
  --output-json computations/2026-09-24T183715Z-t27-50-schur-certificate/data/certificate.json
```

The generator must create a fresh certificate and pass its Python schema/semantic checks. No artifact from `X-20260923-001` may be substituted.

## Independent Rust replay

Only after successful fresh generation:

```text
cargo run -q -p rh_cert -- verify \
  --cert computations/2026-09-24T183715Z-t27-50-schur-certificate/data/certificate.json \
  --json
```

The result is theorem-bearing only if the independent verifier returns exit `0`, `passed=true`, `claim=C-0057`, `support_T=27/50`, `dimension=104`, and `verified_scope=localized_weil_positivity_T_27_50`.

The verifier output should then be retained as `data/rust-verification.json` together with the exact certificate hash/size and execution provenance.

## Planned adversarial checks

After a successful independent PASS, test temporary copies without altering the retained certificate:

1. change exact Schur factor `3 -> 2`; contract validation must reject it;
2. replace a selected finite-matrix diagonal interval by an exact negative value while keeping the contract structurally valid; theorem verification must run and return `passed=false`;
3. confirm the unchanged certificate still returns exit `0` / `passed=true`.

Any unexpected acceptance or failure blocks theorem promotion.

## Retained-proof boundary

This computation is **not** registered in `computations/retained-proofs.json` by this declaration. `EXPECTED_RETAINED_CLAIMS_V1` must also remain unchanged until the fresh certificate, independent replay, and adversarial checks have succeeded and an explicit later registration phase is performed.

## Frozen source hashes at the admission state

```text
57c9f0a4d81fc35837bb37bf3c870ec2c13d2d99f599cd54cc5fce0793b76956  scripts/cert/legendre_schur.py
53cf49ba4a30ddd690a3898a373900e4bda978cc82a27764186eef4e0f398ea7  scripts/cert/exact_prime_schur_certificate.py
e8561a9afaf4dd0fb8815db29f2e0c80b5b3650bd2db8051e2b668da61407f96  scripts/cert/export_certificate.py
bd71fcf341d70a44e1fe8f126393e95b785c4164ea796ce69966f0af4ce10140  crates/rh_cert/src/cert.rs
0a58b6a36055b6b56720d275e96c19d0275948872542491099cd68c454bbed48  docs/contracts/rh-weil-certificate-v1.json
cf1a66ce9ef7321ddadd2df426d9721465110b4f550219db98063415f31f2fba  tests/data/exact-prime-admission-v1.json
5356b959391427a6817ae937d06678554f2761d825ea80fc23890ea9f5d37ac3  computations/retained-proofs.json
4900a4ea4bdb191608d84817af5aae912e5931d5bae82af6159e45c0279d4d89  scripts/cert/verify_retained_proofs.py
```

## Current interpretation

This record freezes the next proof-bearing computation before execution. No theorem computation has yet been run under this ID, no certificate exists yet, and `C-0057` is not verified.

The independently verified finite-support frontier therefore remains `(T,N)=(21/40,96)` / `C-0056`. RH remains unresolved.
