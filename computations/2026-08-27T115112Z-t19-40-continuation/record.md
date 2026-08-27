# T=19/40 one-prime continuation candidate search

- **Computation ID:** `X-20260827-001`
- **Created:** `2026-08-27T11:51:12Z`
- **Last updated:** `2026-08-27T12:06:30Z`
- **Status:** `COMPLETE`

## Objective

Run the canonical pre-theorem one-prime continuation workflow at the next active support

```text
T=19/40=0.475
```

without extrapolating the Legendre dimension from the earlier `32 -> 40 -> 48 -> 56` sequence. Search the explicit range `N=48,52,...,80`, distinguish numerical conditioning from stable mathematical rejection, and stop at the repository's `CANDIDATE_READY` boundary if an exact generator-side candidate survives.

## Mathematical quantity tested

The run uses the existing exact-prime Legendre-Schur continuation mechanism inside the strict one-prime support window. For each selected rigorous dimension it assembles the finite block and component tail-Gram Schur reduction using exact-polynomial/Arb machinery, with

```text
S_N=A_N-(3/mu_N)(G_V+G_2+G_R),
mu_N=H_N-c_T-c_2-rho_R.
```

Floating reconnaissance is used only for dimension selection. Rigorous screening escalates Arb precision before classifying a negative result. Exact candidate construction outward-rounds the rigorous matrices to rational intervals and checks exact rational parity congruence/Gershgorin witnesses.

## Environment

- software/runtime: CPython `3.14.0` under the locked `uv` environment;
- rigorous backend: `python-flint 0.9.0` / Arb;
- generator commit: `206f5678ca598568c4dfda65218d007f43a292ea`;
- generator provenance: `git_dirty=false`;
- driver: `scripts.weil_continuation_driver`, version `continuation-driver-p13-v1`;
- cache contract: `continuation-driver-v4`;
- rigorous precision ladder: `128,256,384,512` bits;
- residual order: `32`.

## Inputs and parameters

```text
support:       19/40
dimensions:    48,52,56,60,64,68,72,76,80
scout passes:  3
matrix bits:   64,80,96,104
witness bits:  32,40,48,56
```

The three floating scout resolutions were:

```text
(max_mode, quadrature_order, shift_order)
(120, 700, 350)
(160, 860, 430)
(200, 1020, 510)
```

## Reproduction procedure

The historical run was launched with:

```text
uv run --locked python -m scripts.weil_continuation_driver \
  --support 19/40 \
  --n-min 48 \
  --n-max 80 \
  --n-step 4 \
  --output-dir computations/2026-08-27T120000Z-t19-40-continuation/data/continuation-T019-040
```

Before registration, the uncommitted computation directory was renamed to `2026-08-27T115112Z-t19-40-continuation` so its repository timestamp matches the driver's manifest start time `2026-08-27T11:51:12Z`. The bundle itself is retained unchanged under:

```text
data/continuation-T019-040/
```

Its `run-manifest.json` lists twelve artifacts with SHA-256 hashes. A post-run mechanical replay of every manifest hash returned `hashes_ok=True` with no mismatches.

## Output

The floating scout classified:

```text
N=48  negative
N=52  negative
N=56  negative
N=60  unstable
N=64  stable-positive
N=68  stable-positive
N=72  stable-positive
N=76  stable-positive
N=80  stable-positive
```

The canonical driver therefore selected `N=64` as the primary rigorous target and `N=68` as the single fallback.

At `N=64`, the known monomial-conditioning failure pattern is visible at low precision, but the precision ladder resolves it rather than misclassifying it. The 384- and 512-bit results agree and give a stable negative Schur midpoint:

```text
mu_64 midpoint/lower ~ +0.6583679342698018
finite A_64 minimum  ~ +3.8671406454e-6
Schur minimum        ~ -0.18090174481401158
```

The driver therefore classifies `N=64` as `MATHEMATICAL_NEGATIVE`, not `INSUFFICIENT_PRECISION`.

At `N=68`, the 128-bit result is conditioning-corrupted, 256 bits restores the expected positive scale, and 384 bits is stable against the previous precision:

```text
mu_68 lower          ~ +0.7185353202932019
finite A_68 minimum  ~ +3.8668365900e-6
Schur minimum        ~ +3.6658868513e-6
selected precision   = 384 bits
```

Exact candidate construction succeeds immediately at the first rationalization settings:

```text
matrix bits   = 64
witness bits  = 32
mu lower      ~ +0.7185353202932019
even margin   ~ +0.0013831260220094517
odd margin    ~ +0.006360318287493695
```

The terminal state is:

```text
CANDIDATE_READY
selected dimension = 68
```

## Interpretation

This is strong generator-side evidence that the existing exact-prime Legendre-Schur mechanism continues to `T=19/40` when the cutoff is increased to `N=68`. It also resolves the dimension-selection question at this support: `N=64` is not merely a low-precision failure; under the present Schur reduction it is stably negative, while `N=68` survives rigorous screening and exact rational witness construction.

The result is deliberately **pre-theorem**. The pair `(T,N)=(19/40,68)` is not admitted to the closed `exact_prime_legendre_schur` theorem contract, has not produced a theorem certificate, and has not been independently replayed by `crates/rh_cert`.

## Limitations

- `CANDIDATE_READY` is generator-side evidence only and does not prove localized Weil positivity at `T=19/40`.
- The closed v1 theorem profile still admits only `(7/20,32)`, `(2/5,40)`, `(17/40,48)`, and `(9/20,56)`.
- No change was made to the Python/Rust whitelists, JSON schema, claim ledger, or theorem findings.
- No independent Rust theorem replay was invoked because theorem admission requires a separate human/research decision.
- The run encountered an execution-environment observability incident: the original Portus batch call timed out at the tool boundary while leaving duplicate copies of the identical continuation command running. The duplicates were identified by process command line and terminated. The retained bundle was completed by the original run, records `git_dirty=false`, and all twelve manifest artifact hashes were checked successfully after completion. This incident affects execution efficiency/provenance discussion, not the mathematical inputs or the retained exact data; a future theorem-admission slice must generate a fresh proof certificate and perform a fresh independent replay in any case.

## Related claims / attempts / findings

- active attempt: `A-20260826-001`;
- existing verified theorem claims: `C-0050`, `C-0051`, `C-0052`, `C-0053`;
- continuation mechanism: `C-0048`;
- earlier moving-dimension finding: `F-20260826-001`;
- this computation creates no new theorem claim or verified finding.

## Timestamped addenda / corrections

- `2026-08-27T12:06:30Z` — registered the completed canonical continuation bundle as `X-20260827-001`, verified all manifest artifact hashes, and recorded the duplicate-execution incident without promoting the candidate across the theorem boundary.
