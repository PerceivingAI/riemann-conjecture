# Computations

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-21T08:56:20Z`

This directory contains timestamped numerical and symbolic experiments. Every retained computation must be reproducible and must distinguish numerical evidence from proof.

## Current computation records

- [`X-20260820-001`](2026-08-20T210531Z-exact-identity-verification/record.md) — exact rational checks of identities used by `A-002` and `A-003`.
- [`X-20260820-002`](2026-08-20T210531Z-airy-kernel-localization/record.md) — numerical localization of the uniform saddle.
- [`X-20260820-003`](2026-08-20T210531Z-prime-trace-cutoff-study/record.md) — high-precision cutoff/stability study of the generalized prime trace.
- [`X-20260820-004`](2026-08-20T210531Z-prime-density-turning-window/record.md) — discrete-prime versus continuous-density decomposition in turning-scale bins.
- [`X-20260820-005`](2026-08-20T212000Z-saddle-window-phase-loss/record.md) — post-turning saddle width, pre-turning envelope rates, and phase-loss diagnostics.
- [`X-20260820-006`](2026-08-20T212000Z-single-zero-regional-cancellation/record.md) — regional decomposition of exact complex zero-mode Laguerre transforms.
- [`X-20260820-007`](2026-08-20T221500Z-uniform-preturning-phase/record.md) — uniform pre-turning stationary map, small-`u` comparison, Cayley phase, and stationary-normalization diagnostics.

- [`X-20260820-008`](2026-08-20T224400Z-chirp-window-reduction/record.md) — first-prime frequency cap, local chirp linearization scales, and generic Dirichlet-polynomial mean-value root barrier.

- [`X-20260821-001`](2026-08-21T020900Z-bilinear-chirp-geometry/record.md) — dyadic Type-II cross-defect, rank-one phase geometry, and `sqrt(n)` nonseparability-scale diagnostics.

- [`X-20260821-002`](2026-08-21T022600Z-positivity-kernel-audit/record.md) — finite Li Gram/Schoenberg diagnostics, prime-atom sign checks, and exact Weil support/translation geometry.
- [`X-20260821-003`](2026-08-21T034825Z-first-prime-weil-continuation/record.md) — exact rational endpoint absorption at `T=7/20` and certified Arb enclosures for `tau`, `log(2)/sqrt(2)`, and the Suzuki Weil constant.
- [`X-20260821-004`](2026-08-21T085252Z-exact-prime-legendre-schur/record.md) — proof-path Arb certificate for the `0.69V` obstruction and exact-prime high-mode complement, plus a separate floating Schur-dimension scout.

## Directory Bundle Standard

Each computation run is stored as a self-contained bundle directory:

```text
computations/
├── README.md
└── YYYY-MM-DDTHHMMSSZ-<short-kebab-title>/
    ├── record.md          # Primary computation record (objective, parameters, outputs, limits)
    ├── plots/             # (Optional) Generated visual artifacts (.svg, .png)
    └── data/              # (Optional) Small summary datasets or parameter tables (.json, .csv)
```

### Visual and Data Artifact Rules
1. **Static Plot Artifacts:** Save plots directly into `plots/` within the computation bundle. Prefer `.svg` for line plots/asymptotics; use fixed DPI `.png` (`dpi=200`) for dense 2D rasters.
2. **No Interactive Notebooks:** All computations run from deterministic, versioned CLI entry points under `scripts/` or `crates/`.
3. **Data Threshold:** Datasets $\le 2\text{ MB}$ can be saved to `data/`. Large raw datasets must be regenerable on demand via CLI arguments documented in `record.md`.
## Code

Authoritative computation entry points live under [`../scripts/`](../scripts/) and [`../crates/rh_engine/`](../crates/rh_engine/). Core Python prime/Laguerre routines remain standard-library based where practical; selected helpers use the scientific environment pinned by `pyproject.toml` and the project lockfiles.

When a script is modified after a recorded experiment, the computation record retains the command, relevant environment, and script hash/version information needed to distinguish the historical run.

Use [`../templates/COMPUTATION.md`](../templates/COMPUTATION.md) for new records.
