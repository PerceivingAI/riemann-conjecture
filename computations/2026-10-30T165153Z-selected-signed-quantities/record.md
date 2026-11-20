# Complete selected signed low and exterior quantities

- **Computation ID:** `X-20261030-002`
- **Created:** `2026-10-30T16:51:53Z`
- **Last updated:** `2026-10-30T17:35:14Z`
- **Status:** `VERIFIED_SELECTED_COMPLETE_SIGNED_QUANTITIES`

## Objective

Implement and exercise the complete selected residual, potential, combined arithmetic square, ordered potential/arithmetic product, low model and physical exterior. Compare a native producer with separately implemented analytical reconstruction, through actual owned execution and persisted exact endpoints. Each selected expression must contain its entire mathematical domain; a selection is not a full source matrix.

## Mathematical quantities and complete domains

Use ordinary Legendre polynomials `L_n`, physical masses `d_n=2/(2n+1)` and the unchanged closed `T=81/100,N=826,K=86,M=1652` problem. The exact scalar/model/error/reference bindings are in [problem.json](data/run-v1/inputs/problem.json), not rounded replacements. Arithmetic terms are `(a,p)=(2,2),(3,3),(4,2),(5,5)`, with `tau_a=log(a)/T` and `c_a=log(p)/sqrt(a)`.

```text
V(x) = -log(1-x^2)/2.
(Pu)(x) = -sum_a c_a [1_[−1,1−tau_a](x) u(x+tau_a)
                         +1_[−1+tau_a,1](x) u(x−tau_a)].
F = V+P; F_kn = <L_k,F L_n>.
VV_mn = <V L_m,V L_n>.
P_squared_mn = <P L_m,P L_n>.
VP_mn = <V L_m,P L_n>; VP_nm is computed in its own order.
J_F_mn = VV_mn + P_squared_mn + VP_mn + VP_nm.
A_model_mn = delta_mn*d_m*(H_m−EulerGamma−log(2*pi*T))
             +F_mn+<L_m,R_K L_n>.
G_exterior_mn = J_F_mn−sum_[0<=k<M] F_km*F_kn/d_k.
weighted_complete_tail_mn = kappa*G_exterior_mn.
```

All projection sums use physical same-parity `k`, including **both** `k<N` and `N<=k<M`. The exterior is the full Parseval complement beyond `M`, not a finite sampled tail. The prescribed `kappa` remains unchanged. `R_K` is the complete finite residual model; its true residual discrepancy remains the bound `Lambda D` to be charged **once** in a later full-space argument. Recording `model_error_upper` does not subtract it from each selected `A_model` entry or establish positivity.

The six low Gram pairs are `(0,0),(1,1),(0,824),(1,825),(824,824),(825,825)`. Nine quantities are retained at each pair: `V,VV,P_squared,VP,J_F,A_model,P_L,G_exterior,weighted_complete_tail`; both off-diagonal reverse `VP` entries are also retained. Here `P_L` is the arithmetic low component, not the full `F`.

Four complete dependency columns, `n=0,1,824,825`, each contain every same-parity row `0<=k<1652`: **3,304 independently compared entries**. This is not a complete `F_L/F_H` matrix.

Twelve additional residual bilinears cover low, `K`, `K+1`, terminal band, interior band and rigorous band-zero cases:

```text
(0,0),(2,0),(86,86),(88,86),(87,87),(826,738),
(826,740),(826,824),(827,825),(910,824),(912,824),(1650,824).
```

There are **68 complete selected scalar quantities** and four complete dependency columns per role. Full-source sealing still requires the original complete family domains; these partial family manifests cannot seal a source.

## Separate mathematical implementations

- **Producer:** exact sparse Legendre primitive walks and low endpoint/polar polynomials for the complete `R_K`; harmonic closed potential bilinears; full logarithmic-square moments for `VV`; native composition and logarithmic window primitives for ordered `VP`; full combined signed images on every strict overlap cell for `P_squared`; streamed full operator columns. The square uses all **826 prescribed Gauss nodes on every one of nine cells**, after combining all active images. Columns use all **1,239 prescribed nodes for each of eight signed windows**, with 32-node native value panels. Every low and physical output position is retained.
- **Independent consumer:** separate formal exponential quotient for the residual coefficients, exact Rodrigues ratios, endpoint-normalized repeated primitives, independent binomial/logarithmic moment formulas and direct endpoint integration of the full combined polynomial on every cell. Its arithmetic square does not use the producer Gauss rule. It forms low/model/exterior expressions independently and subtracts every physical projection term in its own scalar loop; the producer uses a native matrix dot.
- **Shared neutral layer:** immutable input/collection binding, domains, bounded transport, sole-owner publication, exact endpoint conversion and independent containment/payment. `gram.py` does not implement a shared mathematical evaluator. Neither role imports the other role's mathematical implementation.

Source precision **4,608 bits**, independent precision **6,144 bits**, checkpoint grid **512 bits** and publication grid **256 bits** are unchanged. Cancellation-sensitive expressions finish at native precision before a closed checkpoint is staged. Each scalar checkpoint is one complete expression, not an uncompleted inner subtotal. Column checkpoints cover all physical rows for their declared input mode.

Publication rounds both endpoints outward and adds one publication-grid unit per side. Independent 512-bit checkpoints must be contained in the source publication. The physical radius uses `max(d_m^-1,d_n^-1)`, a conservative upper bound for `1/sqrt(d_m*d_n)`, and must satisfy the **original exact numerical goal** for every selected scalar and dependency entry. This is not a full-matrix row-radius or source-norm estimate.

## Persistence, ownership and compatible resume

The actual `slice` CLI accepts the bound signed-case format. Separate producer/analytic collections bind problem, original inputs, code closure, role, precision, grid, domains and execution policy. One OS-backed slice lock owns both collections, state and acceptance publication; workers stage closed chunks and only the owner publishes.

Completed producer tasks may be reused under compatible resume. Independent analytical tasks are freshly reconstructed even if their previous chunks exist; a fresh result must match any cached analytical content before acceptance. These quantities resume at complete-expression/column boundaries. This record does **not** claim new within-expression interruption, process-kill or power-loss qualification. The earlier arithmetic recovery evidence remains separate.

## Environment and resource observations

- Windows x64; locked Python **3.14** environment and `python-flint`/FLINT/Arb backend recorded by the worker runtime captures.
- Origin revision `b19905565ace1f4a1b9ea1387ce123377c65a0e0`, dirty; exact executed mathematical source is preserved in `data/run-v1/captured-code/` and bound worker captures. Historical source/program/input/test/schema bytes were not changed.
- One numerical worker and one native thread per owned stage; explicit **1,536 MiB hard cap**, **792 MiB declared owned account**, **256 MiB external increment allowance** and **128 MiB reserve**. These are admission settings, not measured requirements for a full matrix or another profile.
- Fresh actual CLI exit **0**; wall **1,328.204 seconds**. Each role completed 22 tasks over three stages; all six owned stages verified cleanup.

| Role | Stage | Observed owned peak bytes | Sampled external increment bytes |
| --- | --- | ---: | ---: |
| Producer | columns | 132792320 | 1560576 |
| Producer | gram | 85209088 | 1855488 |
| Producer | residual | 72032256 | 1855488 |
| Independent | columns | 103649280 | 1372160 |
| Independent | gram | 87891968 | 1400832 |
| Independent | residual | 74575872 | 1409024 |

The producer caches **one complete Gauss root/weight vector**, not a node-by-mode image table, and replaces it when order/precision/threads change. Its full image panels have 32 nodes. Only selected completed columns are persisted; a Gram task loads its own two column dependencies.

The independent representation retains eight shifted **coefficient polynomials** for one column, and at most sixteen for one selected pair, not a global window-by-mode image table. For this fixed profile, their coefficient-slot/midpoint account is at most `16*826*(48+8*ceil(6144/64)) = 10784256` bytes; diagonal pairs alias the same eight-image list. This is a representation account, **not a bound on Python wrappers, exact coefficient preparation, products or native workspace**. Those remain separately budgeted. A current output row, moment vector, product/antiderivative and accumulator are released/replaced as traversal advances. No image set for another input column or pair is retained across tasks. The measured high-mode/full-row stages above qualify this selected implementation; they do not establish a universal workspace bound, a full-target resource forecast, scaling law or speedup over a matched whole pipeline.

## Executed verification

- **48 mathematical tests pass**, with raw [JUnit](data/mathematical-tests-v2.xml) and the exact [expanded test source](data/mathematical-tests-v2-source.py). They cover separate residual constructions at the actual `K=86` low/band endpoints, potential/log-square identities, full combined signed-square interactions, both ordered `VP` orientations, complete physical columns, ordinary masses and complete low/head projection subtraction.
- Seven deterministic mathematical omission regressions exercise real structural staging, sole-owner publication, chunk reading and the actual independent endpoint checker: mixed arithmetic interactions, reverse `VP`, low projection, head projection, wrong inverse physical mass, low endpoint/polar constant and terminal residual band. Positive complete formulas pass first. Reduced controls are explicitly non-admissible `CONTROL_ONLY` algebra; they do not stand in for actual .81 execution.
- **11 affected ordinary contract/artifact/arithmetic tests pass**, raw [JUnit](data/affected-ordinary-tests-v1.xml). The final combined count is **59**, not a rerun of the entire Python suite or earlier operational/recovery controls.
- Fresh native acceptance independently checks all **3,304 dependency entries** and **68 completed scalar quantities**. All finite/radius/containment checks pass. The immutable [fresh acceptance](data/run-v1/collection/acceptances/032f46fa6a724a1c8f6c432127942352.json) and [invocation receipt](data/run-v1/fresh-invocation.json) retain exact inputs/results and raw stream identities.
- The read-only [retained verifier](verify-signed-v1.py) returns [PASS_RETAINED_SELECTED_SIGNED_EVIDENCE](data/retained-verification-v1.json). It recomputes selected exact publication/containment and full dependency-column checks from the consumed chunks, verifies owned cleanup/raw streams, and compares twelve new `A_model`/weighted-exterior enclosures with raw-hash-checked original retained source packets. Intersections pass; old source data are a supplementary comparison, **not inputs to the new mathematical evaluation**.

The earlier 41-case JUnit and initial captured test source remain retained as development evidence; the expanded 48-case source is captured separately rather than silently replacing that earlier snapshot. No old adversarial, corruption, ownership-attack or interruption programs ran for this computation. No Rust/Lean, full matrix/sign, T1 or GPU execution is claimed.

## Reproduction and retained inspection

From the repository root with the matching locked environment and immutable original dependency artifacts:

```text
uv run --locked --python 3.14 python -B computations/2026-10-30T165153Z-selected-signed-quantities/run-signed-v1.py --output-dir <fresh-run-directory>
uv run --locked --python 3.14 python -B computations/2026-10-30T165153Z-selected-signed-quantities/run-signed-v1.py --output-dir <same-compatible-run-directory> --resume
uv run --locked --python 3.14 python -B computations/2026-10-30T165153Z-selected-signed-quantities/verify-signed-v1.py --run-dir computations/2026-10-30T165153Z-selected-signed-quantities/data/run-v1 --output <fresh-verification.json>
```

The wrapper writes bound problem/cases/execution inputs for a fresh run and invokes the real `scripts.weil_whole_source_split slice` command. The fresh run directory must be **inside the repository**, because provenance paths are repository-relative. On resume it uses those original inputs without rebinding. Do not regenerate an old collection against changed code or replace retained scientific files. Retained inspection checks existing data and does not repeat native mathematics.

```text
uv run --locked --extra test --python 3.14 python -m pytest -n 0 -q tests/test_whole_source_gram.py
```

## Interpretation and limits

The delivered path computes and independently checks each selected expression over its **complete local mathematical domain**. It is not merely a sampled inner contraction, a sum of per-prime squares, an upper-triangle substitute for ordered `VP`, a low-only projection or a finite approximation to the physical exterior.

It is still a selected-quantity path. It does not build a complete low matrix, frequency/head source, all-entry analytical audit, congruence proposal, full-space exact proof, source seal, positivity result or complete target runner. No signed interval error is asserted Loewner-positive entrywise. Shared reviewed source-form, scalar-enclosure and FLINT/Arb/Gauss premises remain explicit; independently implemented formulas are not an independent proof of those libraries.

C-0124's retained source-conditional .81 smooth-test positivity, scalar-only C-0126 and production **eight v1, zero v2, one v3** remain unchanged. Full T1 execution remains unqualified. RH is unresolved. No commit or push was performed.

## Timestamped addendum — compatible resume, 2026-10-30T17:35:14Z

The actual compatible `--resume` invocation returned **0**, with wall **662.948 seconds** and empty stderr. Producer tasks/stages were **0/0**: all completed producer work was reused. The independent role executed **22 fresh tasks over three owned stages**. All scalar endpoints/publications and all complete dependency-column chunk references agree exactly with the fresh run; the actual [comparison](data/resume-comparison-v1.json), [resume invocation](data/run-v1/resume-invocation.json) and [second immutable acceptance](data/run-v1/collection/acceptances/721174b3d17f4271b72fd70a331bb529.json) are retained.

All three resumed stages verified cleanup. Observed owned peaks were102596608 bytes for columns,88530944 for Gram and74604544 for residual; the maximum sampled external increment was2117632 bytes. These are additional selected-resume observations, not a new full-target resource qualification.

The same read-only verifier returns [PASS_RETAINED_SELECTED_SIGNED_EVIDENCE](data/retained-verification-v2.json) on this resumed acceptance, including all3304 dependency entries,68 scalar quantities and twelve original-reference comparisons. No new interruption or old rejection-suite execution occurred.

[manifest.json](manifest.json) binds the retained member bytes, including both native invocations, immutable acceptances, consumed chunks, runtime captures/profiles/raw streams, test versions/JUnit, exact retained checks and this record. It excludes itself and the separate [raw-binding verification receipt](retained-manifest-verification-v1.json), avoiding a hash cycle. Reading/hashing these artifacts does not rerun native mathematics. Later scientific changes require new code bindings and evidence, not edits to these retained members.
