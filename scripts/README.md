# Research scripts

- **Created:** `2026-08-20T20:59:00Z`
- **Last updated:** `2026-10-25T18:25:39Z`

These scripts are research instruments for the timestamped RH attempts. The core prime/Laguerre routines remain standard-library based where practical, while selected helpers use the scientific packages pinned by `pyproject.toml` and the project lockfiles. Every retained computation must record the environment actually used.

## Byte identity on checkout

The directional research consumers verify raw-byte SHA-256 identities. Scoped rules in [`.gitattributes`](../.gitattributes) keep their pinned sources/configuration in LF, the original SYS-6.4 probe in its recorded CRLF checkout format, and retained bundles verbatim. This avoids platform-default line-ending conversion invalidating evidence on a fresh checkout. The rules do not rewrite historical working artifacts, broaden theorem admission, or impose a new format on unrelated records.

## Complete fixed bounded Fourier minorant

The research-only fixed-case workflow in [X-20261025-006](../computations/2026-10-25T155033Z-fourier-minorant-sign/record.md) separately generates sources, proposes exact witnesses and independently accepts all source entries:

```text
uv run --locked python -m scripts.weil_fourier_minorant_scout --order 64 --output <fresh-scout.json>
uv run --locked python -m scripts.weil_fourier_minorant_matrix source --output <fresh-source.json.gz>
uv run --locked python -m scripts.weil_fourier_minorant_matrix prove --source <fresh-source.json.gz> --output <fresh-proof.json.gz>
uv run --locked python -m scripts.verify_fourier_minorant_matrix <fresh-proof.json.gz> --source <fresh-source.json.gz> --output <fresh-audit.json>
uv run --locked python -m scripts.verify_fourier_minorant_matrix <fresh-proof.json.gz> --source <fresh-source.json.gz> --exact-only --output <fresh-exact-replay.json>
uv run --locked --extra test python -m pytest -n 0 -q tests/test_fourier_minorant_matrix.py
```

The accepted packet is research format `research-fourier-minorant-matrix-v2`, not production certificate-v2. Parameters are closed at T1353/2048,a7/2,Omega256,N312. The full audit checks292968 entries and both exact sufficient parity blocks with the complete C-0094 outside allowance. Exact-only replay never rebuilds analytical inputs. All outputs require fresh paths. The original defective coefficient consumer and its failed version remain reproducible in the bundle; no frozen historical arithmetic code changed. No new support, production profile, Rust/Lean verification or theorem admission is implied.

## Quantitative reference and global-residual scalar controls

`scripts.weil_reference_route_controls` is a research-only scalar procedure for the executed [X-20261025-005 comparison](../computations/2026-10-25T142424Z-reference-route-selection/record.md):

```text
uv run --locked python -m scripts.weil_reference_route_controls --input computations/2026-10-25T142424Z-reference-route-selection/data/matched-local-input-v1.json --output <fresh-output.json>
```

It evaluates rigorous exterior and compact-complement constants, exact bump upper obstructions, global real-residual tails and direct/partial-fraction corroborations. Canonical and isolated captured-source outputs are byte-identical. The complete inequalities, sources and limits are in [F-20261025-005](../findings/2026-10-25T142424Z-reference-route-selection.md). It does not generate a low Fourier matrix, certify its sign, prove a concentration lower gap, broaden old local-kernel acceptance, export certificates or change admissions. Use a fresh output path to preserve earlier records.

## Matched coupled-tail criterion assessment

The versioned [X-20261025-004 procedure](../computations/2026-10-25T134254Z-coupled-route-viability/assess-v1.py) checks exact finite algebra and retained data/work accounting without generating a new positivity matrix:

```text
uv run --locked python computations/2026-10-25T134254Z-coupled-route-viability/assess-v1.py --output <fresh-output.json>
uv run --locked python -I computations/2026-10-25T134254Z-coupled-route-viability/assess-v1.py --root computations/2026-10-25T134254Z-coupled-route-viability/inputs --output <another-fresh-output.json>
```

Both executions pass and their reports are byte-identical. The [record](../computations/2026-10-25T134254Z-coupled-route-viability/record.md) distinguishes matched-reference equivalence, dense accounting identities, inherited diagnostic timings and fresh analytical workloads. This is an assessment artifact, not a new coupled solver, a complexity lower bound or an external benchmark.

## Retained coupled-tail directional comparison

`scripts.weil_coupled_tail_comparison` compares the exact C-0091 negative harmonic-reference trials with the retained coupled block20..311. The complete accepted K312 pays the entire outside tail. A finite inverse is separately bounded and is never used as the full inverse; solve proposals are certified by exact physical residuals.

```text
uv run --locked python -m scripts.weil_coupled_tail_comparison analyze --output computations/<fresh-bundle>/data/comparison.json
uv run --locked python -m scripts.verify_coupled_tail_comparison computations/<fresh-bundle>/data/comparison.json --output computations/<fresh-bundle>/data/audit.json
uv run --locked python -m scripts.weil_coupled_tail_comparison replay --result computations/<fresh-bundle>/data/comparison.json --output computations/<fresh-bundle>/data/replay.json
uv run --locked --extra test python -m pytest -n 0 -q tests/test_coupled_tail_comparison.py
```

Use an existing output directory and fresh filenames. [X-20261025-003](../computations/2026-10-25T130058Z-coupled-tail-comparison/record.md) retains positive true-Schur bounds on both preserved trials, quantitative diagonal-reference loss, full outside-response bounds, independent46-scalar/1752-coordinate checks,2 regressions,5 rejections and isolated replay. The operation inherits original analytical evidence and common legacy K reconstruction. It does not certify a new uniform P20 reference, choose a new projection, establish a smaller-data proof or grant admission.

## Complete retained-source reprojection

`scripts.weil_complete_reprojection` and `scripts.verify_complete_reprojection` assess all20 low directions at fixed T=1353/2048,K38 using the accepted original-v2 M312 tensors. The exact Gram identity restores rows20..311; the unknown infinite tail and full residual/cross error stay paid. The original old-version checker/replay runs before the new consequence, without weakening the current version3 validator.

With an existing output directory and fresh filenames:

```text
uv run --locked python -m scripts.weil_complete_reprojection origin --output computations/<fresh-bundle>/data/origin.json
uv run --locked python -m scripts.weil_complete_reprojection analyze --origin computations/<fresh-bundle>/data/origin.json --output computations/<fresh-bundle>/data/reference.json
uv run --locked python -m scripts.verify_complete_reprojection computations/<fresh-bundle>/data/reference.json --origin computations/<fresh-bundle>/data/origin.json --output computations/<fresh-bundle>/data/audit.json
uv run --locked python -m scripts.weil_complete_reprojection replay --origin computations/<fresh-bundle>/data/origin.json --result computations/<fresh-bundle>/data/reference.json --output computations/<fresh-bundle>/data/replay.json
uv run --locked --extra test python -m pytest -n 0 -q tests/test_complete_reprojection.py
```

[X-20261025-002](../computations/2026-10-25T010204Z-complete-retained-reprojection/record.md) records negative full-reference upper directions in both10-dimensional parity blocks, native512/Arb1536 consequence checks,2 regressions,5 rejected alterations and isolated replay. The analytical evidence is inherited, not freshly generated. Old-subspace witnesses cannot certify new low coordinates; neither this negative reference nor its exact replay grants a production admission or proves Weil negativity.

## Retained-data coupled modes and projection selection

`scripts.weil_coupling_projection` diagnoses the accepted C-0089 source by signed V/P/RK mode energy, then tests changed projections on the original P16 space. It uses the complete Gram-prefix identity, physical masses, the correct H_L reference and full tail/residual allowances. It does not silently reuse G16 after deleting head rows.

```text
uv run --locked python -m scripts.weil_coupling_projection analyze --output computations/<fresh-bundle>/data/projection.json
uv run --locked python -m scripts.verify_coupling_projection computations/<fresh-bundle>/data/projection.json --output computations/<fresh-bundle>/data/audit.json
uv run --locked python -m scripts.weil_coupling_projection replay --result computations/<fresh-bundle>/data/projection.json --output computations/<fresh-bundle>/data/replay.json
uv run --locked --extra test python -m pytest -n 0 -q tests/test_coupling_projection.py
```

Use an existing output directory and fresh filenames. The source pins its historical input bytes and replays the original result. The independent auditor uses narrower native512 inputs and separately organized Arb1536 consequences. Neither reruns analytical source generation.

[X-20261025-001](../computations/2026-10-25T001555Z-coupling-derived-projection/record.md) retains mode16/17 attribution, the first certified projection20 under the whole-known-space rule,2 regressions,5 rejected altered reports and isolated replay. The certificates cover only the original16 low coordinates. They do not test the added directions16..19 or establish full P20 positivity, a minimum dimension, new support or theorem admission.

## Complete reference with the tail-restricted complement

`scripts.weil_tail_complement_assessment` and `scripts.verify_tail_complement_inputs` are a separate research pair at T=1353/2048,N16,K38. They apply C-0088's sharper tail-to-tail norm, preserve the full cross-block residual allowance and independently reconstruct every low/Gram/head entry. They do not modify historical source formats or production admission.

With a fresh, existing output directory:

```text
uv run --locked python -m scripts.weil_tail_complement_assessment generate --boundary 54 --output computations/<fresh-bundle>/data/source.json.gz
uv run --locked python -m scripts.verify_tail_complement_inputs computations/<fresh-bundle>/data/source.json.gz --output computations/<fresh-bundle>/data/audit.json.gz
uv run --locked python -m scripts.weil_tail_complement_assessment assess --packet computations/<fresh-bundle>/data/source.json.gz --audit computations/<fresh-bundle>/data/audit.json.gz --output computations/<fresh-bundle>/data/result.json
uv run --locked python -m scripts.weil_tail_complement_assessment replay --packet computations/<fresh-bundle>/data/source.json.gz --audit computations/<fresh-bundle>/data/audit.json.gz --result computations/<fresh-bundle>/data/result.json --output computations/<fresh-bundle>/data/replay.json
uv run --locked --extra test python -m pytest -n 0 -q tests/test_tail_complement_assessment.py
```

`select` records the initial inverse-weight-cap choice. `refine` is allowed only after replaying an `INCONCLUSIVE_LOWER` result and doubles retained tail-row count; it does not promise a halved error. All outputs refuse overwrite. A genuine negative reference upper stops that fixed-reference refinement.

[X-20261024-006](../computations/2026-10-24T231555Z-tail-complement-weighted-reference/record.md) retains the actual m54 operation, all2099 accepted inputs, exact negative directions in both parity sectors,4 regressions, rejected altered inputs and isolated source regeneration/replay. Its separate `residual-only-limit-v1.py` diagnostic evaluates an optimistic reference while keeping the full source and error; even zero residual norm charge cannot rescue this fixed N16 scalar-reference family. This is not a positivity certificate, Weil negativity or production theorem admission.

## Residual-tail scalar bound at the controlled support

`scripts.weil_residual_tail_bound` evaluates [C-0088](../findings/2026-10-24T224948Z-tail-restricted-residual-bound.md) at the pinned T=1353/2048,K=38 baseline. It removes only even polynomial degrees below2N from the double-compressed residual, bounds the remaining operator by delta+M_N/[N(N+1)], and compares exact scalar positivity/reserve cutoffs. The full residual remainder is retained.

```text
uv run --locked python -m scripts.weil_residual_tail_bound --output computations/<fresh-bundle>/data/scalars.json
uv run --locked python -m scripts.verify_residual_tail_bound computations/<fresh-bundle>/data/scalars.json --output computations/<fresh-bundle>/data/audit.json
uv run --locked --extra test python -m pytest -n 0 -q tests/test_residual_tail_bound.py
```

The first command creates its parent directory; both refuse to overwrite output files. The independent auditor uses separate coefficient/remainder formulas and higher precision, verifies source fingerprints and every reported cutoff/row, and executes exact cusp, polynomial-boundary and signed-image controls. [X-20261024-005](../computations/2026-10-24T224948Z-tail-restricted-residual/record.md) retains the successful commands,4 regressions, actual rejected alterations and an isolated byte-identical replay launcher.

These are separate research scalar consumers. N=16 preserves the old scalar reserve; it is not a new low Schur certificate. The bound does not control Q_N R_T P_N, does not replace the full cross-block residual allowance and is not accepted as an alternative complement by existing production contracts or historical matrix tools.

## Controlled weighted support extension

`scripts.weil_weighted_extension_diagnostics` decomposes exact retained316/626 directional losses and selects a new support by nearly doubling the prime3 translation overlap. The source selection preserves the original exact positive reference mu, an accepted full residual budget and an omitted inverse-weight cap before new matrix signs. Matching this cap does not match omitted mass or prove positivity.

`scripts.weil_weighted_support_extension` generates a new parameter-bearing research packet with fresh complete A_K/G_K and signed V/P/RK heads. `scripts.verify_weighted_support_extension_inputs` reconstructs all low/Gram entries, every head component, the complement, full residual and uniform cross-norm bound using separately organized global moments and Taylor transforms. It has no inherited-low option. Physical Legendre masses, both parity blocks, full mixed terms and infinite residual/tail errors are retained.

```text
uv run --locked python -m scripts.weil_weighted_extension_diagnostics select --output computations/<new-bundle>/data/selection.json
uv run --locked python -m scripts.weil_weighted_support_extension generate --selection computations/<new-bundle>/data/selection.json --output computations/<new-bundle>/data/source.json.gz
uv run --locked python -m scripts.verify_weighted_support_extension_inputs --packet computations/<new-bundle>/data/source.json.gz --output computations/<new-bundle>/data/audit.json.gz
uv run --locked python -m scripts.weil_weighted_support_extension assess --packet computations/<new-bundle>/data/source.json.gz --audit computations/<new-bundle>/data/audit.json.gz --output computations/<new-bundle>/data/result.json
uv run --locked python -m scripts.weil_weighted_support_extension replay --packet computations/<new-bundle>/data/source.json.gz --audit computations/<new-bundle>/data/audit.json.gz --result computations/<new-bundle>/data/result.json --output computations/<new-bundle>/data/replay.json
uv run --locked --extra test python -m pytest -n 0 -q tests/test_weighted_support_extension.py
```

Selection creates its parent directory; later outputs refuse overwrite. Use a fresh selection from the source version being executed, not edited budget/parameter metadata. Historical replay restores captured source versions in an isolated repository copy, retaining the original inputs and hashes rather than relabeling old output as current.

[X-20261024-004](../computations/2026-10-24T191616Z-weighted-support-extension/record.md) retains the actual selected T=1353/2048,N=312,K=38,m=1018 operation, source versions, status, controls and corrections. [C-0085's finding](../findings/2026-10-24T193421Z-cross-cut-norm-controlled-continuation.md) proves the uniform cross-cut potential norm and complete dimension-independent residual allowance. `scripts.weil_weighted_dimension_cost` implements [C-0086's conditional completeness/cost calculation](../findings/2026-10-24T194945Z-conditional-schur-completeness-cost.md) from an already known gap, not a new-support positivity premise.

The selected operation completed with all758475 inputs freshly accepted and both156-dimensional parity lowers positive. Separate exact replay, real altered-witness/source-byte rejection and an isolated replay from archived numerical version2 pass. [C-0087's finding](../findings/2026-10-24T202855Z-controlled-weighted-support-positivity.md) gives the precise source-conditional implication and reference bounds. Current version3 additionally enforces complete typed selection/budget/provenance and input serialization;4 focused controls and actual pre-generation rejection pass. Historical numerical arrays are not relabeled as outputs of that later correction.

These are research consumers, not new certificate profiles or admission tools. The existing fixed3/5 procedures below remain unchanged. A failed lower is inconclusive unless a separate negative actual-reference upper is verified; no finite successful operation proves RH.

## Fixed weighted low-space research

`scripts.weil_weighted_low_space` generates raw A_K, the complete Q192 mixed-image Gram and signed rectangular V/P/R32 pairings at T=3/5,N=192,K=32, keeping the original exact reference mu. It uses ordinary Legendre coordinates and records source fingerprints. The boundary must be even in [224,1024]; its degree-based head precision is separate from the 1024-bit low/Gram construction. `--base` reuses unchanged low/Gram source bytes, not a previously accepted matrix sign.

`scripts.verify_weighted_low_space_inputs` independently reconstructs every low/Gram entry at 2048 bits and every head component at twice its generator precision. It requires strict containment, exact residual polynomial agreement, source identity, certified geometry and validity of the original chosen mu. Per-column residual-degree orthogonality is enforced only after the computed interval contains the proved zero. A global degree cutoff alone is insufficient. Optional `--reuse-accepted-low` reuses only the exact retained224 source/audit pinned in the implementation, requiring unchanged low definitions, payload and source fingerprints. It rechecks every inherited reference enclosure and freshly rebuilds all residual polynomials and requested heads; provenance distinguishes reuse from fresh reconstruction.

`scripts.verify_weighted_low_space` checks all serialized reference containments and constructs the complete weighted matrix lower, uniform tail trace and full residual cross allowance with directed dyadic/native integer center-radius contractions. These retain signed off-diagonal terms and pay coefficient/weight uncertainty before Loewner conversion. Floating candidates are accepted only through exact rational congruence on both blocks or a verified negative directional upper for the actual reference. A failed lower is inconclusive, not reference or Weil negativity.

```text
uv run --locked python -m scripts.weil_weighted_low_space --boundary 224 --output computations/<new-bundle>/data/source.json.gz
uv run --locked python -m scripts.verify_weighted_low_space_inputs --packet computations/<new-bundle>/data/source.json.gz --output computations/<new-bundle>/data/audit.json.gz
uv run --locked python -m scripts.verify_weighted_low_space --packet computations/<new-bundle>/data/source.json.gz --audit computations/<new-bundle>/data/audit.json.gz --output computations/<new-bundle>/data/result.json
uv run --locked python -m scripts.verify_weighted_low_space --packet computations/<new-bundle>/data/source.json.gz --audit computations/<new-bundle>/data/audit.json.gz --result computations/<new-bundle>/data/result.json --output computations/<new-bundle>/data/replay.json
uv run --locked --extra test python -m pytest -n 0 -q tests/test_weighted_low_space.py
```

Create the output directory before analytical auditing. All outputs refuse overwrite. These are research procedures, not certificate profiles, theorem admission or evaluation of the true inverse. [C-0082's finding](../findings/2026-10-24T021044Z-uniform-harmonic-reference-matrix-bound.md) gives the conditional source, mass, domain and complete-error implications. Existing directional consumers and historical methods remain unchanged.

[X-20261024-002](../computations/2026-10-24T124142Z-weighted-low-space/record.md) retains the actual implementation, seven controls, full source audits, exact replay, rejected attacks and failed/corrected versions. At316, the even reference lower is rigorously positive; the odd sign remains unresolved. Source generation at the next accuracy-selected626 boundary timed out before publication. [F-20261024-002](../findings/2026-10-24T140543Z-weighted-even-reference-block.md) gives C-0083, its exact mass-normalized gap and explicit partial scope. No whole-reference or Weil positivity is claimed.

The separate [m626 continuation, X-20261024-003](../computations/2026-10-24T153012Z-weighted-reference-continuation/record.md), completes with `POSITIVE_REFERENCE_LOWER` on both parity blocks and `EXACT_REPLAY_PASS`, without changing the scientific implementations. All287042 analytical slots are accepted with37056 low/Gram entries and2 scalars inherited from pinned independent evidence,249984 heads reconstructed afresh. Exact mass-gap calculation and an altered odd-witness rejection also pass. [C-0084's finding](../findings/2026-10-24T154006Z-positive-whole-harmonic-reference.md) gives the whole-reference and source-conditional smooth-test implication. This supersedes the earlier unresolved run's current-state limitation, not its historical record. No clean-source production theorem, Rust/Lean acceptance or admission is added.

## Fixed weighted source-tail direction

`scripts.weil_weighted_source_tail` evaluates the original T=3/5,N=192,K=32 trial with the unchanged exact mu. Its one accuracy-selected boundary B=874 pays the complete inverse-weighted omitted tail; it does not construct a new finite sufficient matrix or search cutoffs. Fixed generator/reference precisions are 4096/8192 bits. Signed source components, the residual polynomial through degree 223, the full residual norm and a newly enclosed physical low-form scalar supply both directional endpoints.

```text
uv run --locked python -m scripts.weil_weighted_source_tail
uv run --locked --extra test python -m pytest -n 0 -q tests/test_weighted_source_tail.py
```

The exercised result is `POSITIVE_DIAGONAL_REFERENCE_DIRECTION`, with a strict bracket inside (3/5,9/10). This is one trial, not a positive reference/Schur matrix or a support theorem. C-0072 separately transfers its lower to the true Schur direction; the true inverse is not evaluated. The producer's undetermined true-Schur/Weil field refers to the overall form/operator sign.

All 1330 source containments, independent exact consequence replay, 2/2 regressions and changed-input rejection passed. V2 outward dyadic accumulation fixes a preserved v1 exact-rational serialization failure without relaxing Python's integer guard. The CLI has no numerical options, prints JSON to stdout, rejects changed/missing/rejected inputs at exit 2 and does not overwrite retained outputs. Capture replays separately.

[F-20261023-006](../findings/2026-10-23T192821Z-weighted-source-tail-reference.md) / C-0080/C-0081 state the mathematics and limitations. [X-20261023-004](../computations/2026-10-23T192821Z-weighted-source-tail/record.md) retains both implementation versions, failure/regression evidence, corrected source enclosures and bounded execution history. Existing source modules, older consumers and theorem admissions are unchanged.

## Fixed complete joint-source tail

`scripts.weil_joint_source_tail` encloses the complete source tail at the original T=3/5,N=192,K=32,L=224, retaining signed jump/remainder correlations and restoring the full residual collectively. It uses whole image norms minus 112 odd head projections, not a truncated high-tail sum. The fixed 1536-bit generator and separately organized 3072-bit reconstruction publish outward 352-bit intervals; there are no parameter or precision options.

```text
uv run --locked python -m scripts.weil_joint_source_tail
```

The actual run passed all 351 scalar/head containments and accepted-prefix/model compatibility checks. The resulting directional upper is `INCONCLUSIVE`, not reference positivity. Changed/missing/rejected inputs return exit 2; an altered-byte smoke rejected before numerical construction. The command prints to stdout and never overwrites a retained output itself. Replays should be captured separately.

[F-20261023-005](../findings/2026-10-23T185253Z-joint-source-tail-enclosure.md) / C-0079 state the signed formulas, complete residual, fixed-index limitation and trust boundary. [X-20261023-003](../computations/2026-10-23T185253Z-joint-source-tail/record.md) retains the exact executed source, raw reconstruction endpoints, output, separate rational replay and receipts. Existing mathematical primitives and older consumers are unchanged. This is a fixed research calculation, not a generalized evaluator, certificate path or theorem admission.

## Fixed jump-refinement model/control replay

`scripts/weil_jump_refinement_check.py` replays the original T=3/5,N=192,K=32 arithmetic jump model at L=224 using accepted constants and fixed 512-bit interval arithmetic. It verifies immutable inputs/source identities, retains mixed step products, reports an arithmetic mixed-tail upper and a separate retained-norm full-source control. It has no support, dimension or precision options.

```text
uv run --locked python -m scripts.weil_jump_refinement_check
```

`SIGNED_CANCELLATION_CERTIFIED` refers only to the arithmetic mixed-tail comparison, not Weil/reference positivity or negativity. The command does not assemble source images, new full-source moments, matrices or the full joint-correlation bound. Exit 2 rejects changed/missing/malformed inputs; altered-byte rejection and the actual canonical replay were exercised.

[F-20261023-004](../findings/2026-10-23T174341Z-jump-resolved-tail-correlation.md) gives the reviewed mathematics and limitations. [X-20261023-002](../computations/2026-10-23T174341Z-jump-refinement-controls/record.md) retains exact outputs, historical control versions and the canonical source snapshot. This is a research reproducibility consumer, not a certificate/export/admission path.

## Existing-data directional loss audit

`scripts/weil_directional_loss_audit.py` performs exact rational bookkeeping on the same pinned original/accepted packets, reusing the existing rational input validator. It reports known mass and inverse-cost intervals, the physical omitted-mass lower and the prefix-only exact-reference upper. It does not call the decisive screen, regenerate sources, evaluate another cutoff or implement an analytical upgrade.

```text
uv run --locked python -m scripts.weil_directional_loss_audit --output computations/<new-bundle>/data/loss-audit.json
```

[X-20261023-001](../computations/2026-10-23T105408Z-directional-loss-review/record.md) records the executed audit; [F-20261023-001](../findings/2026-10-23T105526Z-directional-cutoff-and-reference-loss-separation.md) / C-0074 separates finite-cutoff loss from inverse-reference loss. The actual exact-reference sign remains undetermined. Existing outputs are preserved; this is a small reproducibility procedure, not a certificate or source evaluator.

## Fixed exact directional screen

`scripts/weil_directional_exact_screen.py` consumes the approved original trial and accepted directional-source packet by exact raw-byte SHA-256 identity. It audits physical norm, coordinate/configuration, all accepted component intervals and full residual enlargement, then evaluates the fixed C-0072 rational predicate for T=3/5,N=192,M=211,K=32. It imports no analytical module and does not regenerate moments.

```text
uv run --locked python -m scripts.weil_directional_exact_screen --output computations/<new-bundle>/data/exact-screen.json
uv run --locked --extra test python -m pytest -n 0 -q tests/test_directional_exact_screen.py
```

A completed screen exits 0 with `NEGATIVE_SUFFICIENT_CRITERION` or `INCONCLUSIVE`; rejected input exits 2 with `SOURCE_PROOF_GAP`. Existing outputs are preserved. A negative result concerns only finite A-U_211, not the exact inverse reference or Weil form. There is no positive-theorem outcome.

Executed [X-20261022-002](../computations/2026-10-22T190532Z-directional-exact-screen/record.md) obtained an exact upper below -6/5, independently replayed the rational consequence, and passed 12 behavioral tests. [F-20261022-002](../findings/2026-10-22T190730Z-fixed-harmonic-majorant-negative-direction.md) / C-0073 state the source-qualified scope. No new support or theorem was admitted.

## Fixed directional source validation

`scripts/weil_directional_source_validation.py` is a research-only consumer of the existing sparse polynomial assemblers. It validates normalized high-mode V/P2/P3/R32 moments for the pinned SYS-6.4 odd trial at T=3/5, N=192, K=32 and k=193,195,...,209. Independent monomial/cell/split-residual reconstruction must be contained in outward 352-bit component and signed-sum intervals. Full residual uncertainty is restored separately. Sparse-subspace Gram outputs are never used as the original Q_192 Gram.

```text
uv run --locked python -m scripts.weil_directional_source_validation --precision 1024 --output computations/<new-bundle>/data/source-validation.json
```

The input byte hash and original source fingerprints are mandatory. The CLI preserves existing outputs and has no automatic retry. Exit 0 means `SOURCE_INPUTS_ACCEPTED`; a rejected or unresolved source packet returns exit 2. This is not a certificate, a Schur sign test or theorem admission. Original A/G enclosures retain their earlier generator-source trust.

Executed evidence: [X-20261022-001](../computations/2026-10-22T185054Z-directional-source-validation/record.md), 45/45 new component/sum enclosures accepted at 1024/2048 bits, whole-process wall time 5.675 seconds, no sign evaluated. Focused checks:

```text
uv run --locked --extra test python -m pytest -n 0 -q tests/test_directional_source_validation.py tests/test_prime_power_local_legendre.py tests/test_combined_analytic_entries.py
```

## SYS-6.4 — One selective larger-support Schur-sign research check (NO ADMISSION)

The **research-only** `scripts/weil_selective_support_probe.py` evaluates the unchanged complete \(V/P/R_K\) low block and mixed-image Gram at exactly \(T=3/5,N=192,K=32\) with Arb-1024, maintaining \(\eta=2^{-24}\), a strictly positive conservative full-tail \(\underline\mu\), and the complete Suzuki residual norm correction. A floating eigenvector is merely a direction **selector**. The script rounds it to a dyadic **odd-parity** vector and uses outward Arb intervals plus exact rational arithmetic to obtain an **upper** Rayleigh bound for the chosen Schur sufficient matrix. At the tested support, this upper is strictly **negative**, so **this sufficient matrix** cannot be positive. It says nothing negative about the actual Weil quadratic form or a changed N/stronger complement.

`scripts/verify_selective_support_probe.py` rechecks the strict rational sign and original source SHA-256 fingerprints without trusting the research sign label; it **does not independently rederive** the full transcendental Arb source entries or admit any theorem. [`X-20261018-005`](../computations/2026-10-18T090311Z-sys6-selective-support/record.md) retains the scoped original inputs and exact arithmetic replay; [`F-20261018-006`](../findings/2026-10-18T091152Z-sys6-selective-support-decision.md) records the **no-admission** outcome. Focused checks: `uv run --locked --extra test python -m pytest -q tests/test_selective_support_probe.py tests/test_support_scaling_scout.py tests/test_mixed_gram_research.py` (**31/31 PASS**). The closed proof-bearing v1/v3 systems and independent full source theorem verification remain separate and unchanged.

**SYS-6.3 verified applicability limit (2026-10-18):** The current `_suzuki_residual_tail_radius` and its `_residual_rho` wrapper explicitly require the full scaled kernel arguments \(|T(x-y)|<\pi\) throughout \([-1,1]^2\), i.e. \(2T<\pi\). Directly using them for \(T=2\) correctly fails closed. **This is not a limitation of Suzuki's globally defined Weil quadratic form.** Separately, the conservative scalar \(\mu_N(T)>0\) eventually holds at **each fixed T** within that local range as N increases (C-0071), but that does **not** establish the complete Schur matrix sign or any global positivity. [F-20261018-005](../findings/2026-10-18T084633Z-sys6-global-support-obligation.md) records the exact source and quantifier checks, with no changes to source or theorem admissions.

## SYS-6.2 — Support-scaling research tools (NOT theorem admission)

Two additive small-scope CLI tools complement the existing **unaltered** mathematical mixed-Gram source:

- `scripts/weil_support_scaling_scout.py`: for a list of exact rational supports, compute certified Arb outward intervals for the existing conservative tail-complement scalar \(H_N-c_T-\sum c_mb_m-\rho_R\), exact prime-power activation, and the first \(N\) where the *bound* is rigorously positive. It does **not** compute or certify the full combined Schur matrix.
- `scripts/weil_combined_scaling_profile.py`: rerun `assemble_truncated_mixed_gram` at a small requested \(N\) with rigorous Arb source inputs, report widths, signed mixed trace displays, elapsed time and truncation residual bound. Traces/ratios are **floating displays** of source balls, **not** eigenvalue lower bounds, full-residual Schur signs or theorem claims. The original proof-bearing source modules remain unchanged.

The completed reproducible support/\(N\)/precision comparison and commands are [`X-20261018-004`](../computations/2026-10-18T080600Z-sys6-support-scaling/record.md); classification [`F-20261018-004`](../findings/2026-10-18T081419Z-sys6-support-scaling-analysis.md). Focused checks: `uv run --locked --extra test python -m pytest -q tests/test_support_scaling_scout.py` (**6/6 PASS**). The tool output must **never** be interpreted as a separate admission under `rh-weil-certificate-v3`; there is still exactly one v3 retained support pair \(T=11/20,N=192\).

## SYS-5.4 — One admitted v3 finite-support theorem: canonical replay

`rh-weil-certificate-v3` now has exactly **one** separately admitted theorem, `C-0067` at `T=11/20,N=192`, from a previously clean-source regenerated certificate, and **no further inferred support**. Its canonical complete retained-proof replay (source/analytical Arb-2048 plus exact Rust production verification) is:

```text
cargo build -p rh_cert --locked
uv run --locked --extra test python -m scripts.cert.verify_retained_v3 --output computations/2026-10-18T071550Z-v3-retained-admission/data/replay.json --rust-binary target/debug/rh_cert.exe
```

The implementation `scripts/cert/verify_retained_v3.py` binds an exact approved byte-hash certificate and separately pinned committed source, rejects altered or expanded `computations/retained-proofs-v3.json`, independently rigorously reconstructs all **37,056** source intervals plus `mu,delta`, then invokes zero-float Rust `verify` on a private immutable byte snapshot; output is published atomically only after all checks pass. The fully executed reference replay and detailed trust boundary are [`X-20261018-003`](../computations/2026-10-18T071550Z-v3-retained-admission/record.md). For cheap manifest/adversarial controls run `uv run --locked --extra test python -m pytest -n 0 tests/test_retained_v3_admission.py`. The **separate historical v1 replay** remains `uv run --locked python -m scripts.cert.verify_retained_proofs` (eight claims only). The v3 `verify-candidate-v3` research command **still never admits a theorem**, even for a positive rational matrix. The full v3 theorem depends on the distinct independently checked Suzuki/Arb analytical source trust layer; Rust/Lean do not independently prove that source identity or all-support RH.

## OAI-9: External OpenAI theorem is not a local verification CLI

The pinned `EXT-0001` theorem is a **cited external Lean result**, not a theorem exported or independently replayed by this repository. For source identity and optional independent Comparator replay **status/checklist**, use [`references/external-results/README.md`](../references/external-results/README.md) and [`EXT-0001`](../references/external-results/EXT-0001-openai-quasi-rh.md). Its upstream solution uses **Lean 4.34.1**, distinct from our local soundness layer. No `scripts/` command builds or verifies the upstream theorem, and source-hash checks do not prove it.

**Do not confuse verification workflows:**
- `uv run --locked python -m scripts.cert.verify_retained_proofs` checks the closed **eight local finite-support** `C-0050..C-0057` artifacts by byte hash and independent Rust exact replay. It does **not** replay `EXT-0001`.
- `scripts/weil_continuation_driver.py` is the **frozen one-prime** continuation workflow; `scripts/weil_multi_prime_continuation_driver.py` is the **separate generic multi-prime** workflow with no admitted v2 theorems. `CANDIDATE_READY` is not an admission.
- OAI-8 identifies rigorously negative factor-3 *sufficient* Schur matrices at `T=11/20,N=192/196`. Before another post-`p=3` qualification, the mathematical bound itself needs a separately justified improvement. Repeating the same negative matrix with more precision does not help.

See [`research/openai-math/RESEARCH_DIRECTION.md`](../research/openai-math/RESEARCH_DIRECTION.md), [`docs/CONTRACTS.md` §5](../docs/CONTRACTS.md) and [`docs/PROTOCOL.md` §7.2](../docs/PROTOCOL.md). Mathematical external-dependent deductions `C-0060..C-0062` introduce no new CLI, code dependency, certificate format, or theorem admission.

## Research-only combined mixed-Gram diagnostic

`scripts/cert/mixed_gram_research.py` constructs a rigorously enclosed **truncated** combined low-to-tail Gram from all ordered `V/P/R_K` image cross terms and the correct Legendre `D_N^-1` projection. Its separate `rigorous_full_gram_upper` applies the rigorous Suzuki residual norm bound as a **matrix-order** exact rational upper enclosure; `rigorous_combined_schur_lower` constructs a lower form matrix **only** with a certified positive complement. Neither claims positive definiteness or issues a certificate. The narrowly scoped `scripts/profile_mixed_gram_research.py` measures actual Arb enclosure widths/timing. Reproduction, precision requirements and explicit inconclusive mathematical status are documented in [`X-20261017-002`](../computations/2026-10-17T142253Z-mixed-gram-implementation/record.md) and [`F-20261017-009`](../findings/2026-10-17T142253Z-combined-mixed-gram-implementation-and-validation.md). Existing one-prime and generic multi-prime continuation drivers remain canonical for their respective frozen research/certificate paths.

**Independent validation / trust update (2026-10-17):** [\`F-20261017-010\`](../findings/2026-10-17T144247Z-independent-mixed-gram-verification-and-tooling-closure.md) independently checked the mixed analytical formulas, matrix-order and residual normalization, and fail-closed input contracts; **40/40** focused current tests pass. The full-residual Young parameter must be an exact positive \`Fraction\`; malformed nonsquare/contradictory asymmetric Gram intervals are rejected. Previously reported \`N=192/196\` Arb-1024 interval widths are retained *as-run* measurements; the modified source was not re-executed at those dimensions merely for documentation closure. The generated matrices remain **research evidence, not independently admitted theorems**.

## Bounded combined-Schur research experiment — pre-theorem

\`scripts/run_combined_schur_experiment.py\` evaluates one fixed combined \(V+P+R\) low-to-tail Gram configuration rigorously with Arb, writes a **complete** compressed 352-bit outward-dyadic rational low-form/Gram input packet, and rejects failed active-term/complement/interval-width gates. The independent-exact-research layer is separated from the analytical generator: \`scripts/inspect_combined_schur_packet.py\` makes explicitly nonproof float diagnostics and checks exact candidate Rayleigh directions; \`scripts/prove_combined_schur_fast.py\` uses a float Cholesky factor **only to propose** an invertible dyadic congruence matrix, then checks strict positive exact rational Gershgorin margins; \`scripts/verify_combined_schur_research.py\` independently reconstructs the rational Schur lower matrix and congruence from **the saved input packet and witness** without trusting any generator sign flag. Neither this path nor its exact checker is a v1/v2 certificate/verifier or theorem admission.

The **executed** \`T=11/20,N=192\`, Arb-1024 positive **pre-theorem candidate** with full rational evidence, source and artifact hashes, bounded termination record, and precise analytical-trust boundary is [\`X-20261017-003\`](../computations/2026-10-17T150153Z-combined-schur-bounded-test/record.md) / [\`F-20261017-011\`](../findings/2026-10-17T151010Z-positive-combined-schur-pretheorem-candidate.md). Follow that evidence rather than repeating full-size support/dimension experiments automatically. **N=196 was not executed** because the exact rational lower bound at N=192 was positively confirmed. Existing canonical frozen one-prime and multi-prime v2 paths remain separate.

**Independent analytical research audit (2026-10-17):** \`scripts/audit_combined_schur_analytic_inputs.py\` audits the existing \(T=11/20,N=192\) rational packet against the independent older low \(A\)/complement assembler, high-degree direct \`mpmath\` quadrature for the new \(VP\) cell (diagnostic, **not a proof**) and an exact rational comparison with the previous finite-tail Gram lower bound. See [\`X-20261017-004\`](../computations/2026-10-17T153222Z-analytic-source-review/record.md) / [\`F-20261017-012\`](../findings/2026-10-17T153222Z-independent-analytic-audit-positive-combined-schur.md). The separate research exact-rational checker now fails closed for noncanonical dyadic precision and reversed/invalid complement/residual intervals, and correctly reverified the **original unchanged** matrix and witness. These are source-level and mathematical controls, **not** a new proof profile, theorem admission or second all-entry Arb reconstruction.

**Source-level finite-support proof audit (2026-10-17):** \`scripts/audit_suzuki_math_closure.py\` independently checks 81 exact rational \(|x-y|^d\) kernel-polynomial actions and compares whole-interval \(V,V^2\) moments at degrees \(0,2,20,190\) to separate high-precision numerical references (**nonproof**). Its result is [\`X-20261017-005\`](../computations/2026-10-17T214044Z-sys5-analytic-proof-audit/record.md); the exact mathematical implication and unclosed analytical trust boundary are documented in [\`F-20261017-014\`](../findings/2026-10-17T214129Z-finite-support-theorem-analytic-proof-obligations.md). This **does not** independently certify all 37,056 archived Arb input interval contents, and is **not** a new theorem verifier or admitted finite-support claim.

**Complete mathematical source-input acceptance (2026-10-17):** \`scripts/verify_combined_schur_analytic_entries.py\` separately reconstructs the fixed \(T=11/20,N=192\) low-form and **full combined** truncated mixed Gram from exact Legendre/Bernoulli polynomials, alternate translated-cell affine Legendre contraction, beta/logarithmic moments and uniform Suzuki residual formulas. The 2048-bit independent reference checks **full exact rational interval containment** against the archived 352-bit dyadic packet (not just overlap); all **37,056 entries** plus \(\mu,\delta\) passed. See [\`X-20261017-006\`](../computations/2026-10-17T215700Z-sys5-full-analytic-acceptance/record.md) and [\`F-20261017-015\`](../findings/2026-10-17T220105Z-complete-independent-analytic-enclosure-closure.md). The original exact rational positive congruence was separately replayed. New \`tests/test_combined_analytic_entries.py\` checks fail-closed interval/domain/header inputs and the small complete mixed Gram. **Trust:** rigorous Arb primitive arithmetic and Suzuki's original analytical identity; this independently certifies the mathematical source packet **but is not a new Rust/Lean certificate profile or automatically admitted theorem**. Frozen one-prime and unrelated v2 semantics stay unchanged.

**Clean v3 proof-bearing reproduction completed (2026-10-18):** `uv run --locked python -m scripts.cert.export_combined_schur_v3_clean --output computations/2026-10-18T010000Z-v3-clean-proof-candidate/data/certificate-v3-clean.json` was successfully run from **clean committed** `f0350f89ec5189648cfc271c4ddd3a97355a2343`. It recomputed the full Arb-1024 input and exact congruence witness, matched both original SHA-256 byte-for-byte, and ran a fresh complete Arb-2048 containment audit. The generated clean certificate was then independently replayed using `scripts.verify_combined_schur_v3_bundle` and Rust `verify-candidate-v3` against the exact same certificate bytes. All 37,056 entries plus two scalar bounds passed and the original **exact** positive congruence margin was recovered. See [`X-20261018-002`](../computations/2026-10-18T010000Z-v3-clean-proof-candidate/record.md). This is a **clean, verified pre-admission candidate**; production theorem `verify` continues to reject because v3 admission remains empty.

## v3 full combined-Schur research acceptance (pre-admission)

The distinct rh-weil-certificate-v3 / combined_multi_prime_legendre_schur path applies to executed T=11/20,N=192. scripts/cert/export_combined_schur_v3.py creates the honestly dirty research candidate; scripts/cert/export_combined_schur_v3_clean.py implements fresh clean-source packet, witness and independent analytical reconstruction but correctly refuses the current uncommitted tree. scripts/verify_combined_schur_v3_bundle.py reruns the independent rigorous Arb-2048 37,056-entry analytical containment and scalar bounds from the actual serialized v3 input, then invokes a separate zero-float exact Rust proof. Both gates passed and produced the original exact positive margin. The Rust verify-candidate-v3 command is PRE-THEOREM ONLY; ordinary verify rejects v3 due to empty production admission. [X-20261017-007](../computations/2026-10-17T222400Z-v3-research-bundle/record.md) / [F-20261017-016](../findings/2026-10-17T224310Z-v3-combined-schur-proof-system-implementation.md). Python 34/34, Rust 73/73, strict Clippy and full Lean lake build Cert passed. Clean proof-bearing generation/acceptance and theorem admission were NOT performed.

**v3 acceptance hardening (2026-10-18):** The later [X-20261018-001](../computations/2026-10-18T004000Z-v3-gate-hardening-replay/record.md) records independent Arb-2048 and exact Rust replay against one immutable v3 certificate byte snapshot, after fixing input reopening and strengthening clean-source/provenance cross-checks. All 37,056 entries and both scalar bounds were contained; the exact minimum margin is unchanged. Python 37/37, Rust 73/73, plus a full 192-dimensional **synthetic, analytically invalid but structurally valid** exact negative control passed (mathematical exit 1). Clean-source generation and theorem admission remain unperformed.

## SYS-2.5: finite-tail projected research diagnostic (non-production)

`scripts/weil_projected_mixed_schur_check.py` is a scoped, reproducible mathematical diagnostic. It reuses the existing rigorous assembler and immutable exact vectors solely to test whether finite additional Legendre tail modes **disprove** the new combined Schur sufficient condition. Its output is pre-theorem research evidence, not a combined-Gram certificate or theorem admission. The exact two runs, source fingerprint, and inconclusive evidence are in [`X-20261017-001`](../computations/2026-10-17T124000Z-sys2-projected-obstruction/record.md). It is not a replacement for the canonical v1/v2 drivers.

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

## Canonical one-prime continuation workflow

For ordinary one-prime continuation research, use `scripts.weil_continuation_driver`. It is the canonical pre-theorem workflow and owns reconnaissance, convergence classification, dimension selection, rigorous precision escalation, conditioning-incident handling, exact candidate construction, candidate-level cross-precision stability confirmation, and the self-contained continuation bundle.

The standalone continuation scripts remain supported research instruments and implementation components. Use them for isolated diagnostics, debugging, or historical reproduction; do **not** manually chain them as the ordinary continuation workflow.

### `weil_continuation_driver.py`

Canonical pre-theorem continuation driver. It accepts an exact rational support and an explicit dimension list or range. The p17 canonical scout runs eight increasing reconnaissance resolutions derived from the requested maximum dimension, retains all eight runs for audit, and applies the existing sign/convergence classifier to the highest three levels. The 1% relative Schur-movement tolerance is unchanged. This lets coarse under-resolution wash out without weakening the rigorous gate; `--scout-resolutions` may still be set explicitly for historical reproduction or diagnostics, and when fewer than three levels are supplied the classifier necessarily uses all supplied levels. The driver then rigorously screens only the smallest stable-positive dimension and its next larger fallback. Rigorous screening and candidate checks use the persistent cache `.cache/continuation-driver` by default; cache keys include support, dimension, precision, residual order, witness/rounding parameters, and a fingerprint of the continuation source files plus `uv.lock`. It accepts only the strict `log(2)/2 < T < log(3)/2` p=2-only support window. It never extrapolates dimensions, invokes the theorem exporter, edits the closed contract, or grants theorem status.

The current canonical workflow version is `continuation-driver-p17-v1`; the cache contract remains `continuation-driver-v6`. `driver_version` identifies the complete canonical workflow/provenance contract, including scout selection semantics, lifecycle, observability, cleanup, and finalization as well as mathematical orchestration. It must advance when those semantics materially change, even if the cached mathematical payload format is unchanged. `cache_version` is narrower: it advances when cached mathematical payload/key semantics change. P17 changes the canonical reconnaissance policy but not the cache payload/key contract, so cache v6 remains correct; cache keys also include a fingerprint of the continuation sources (including this driver) and `uv.lock`, isolating changed implementations automatically. Historical bundles keep the driver/cache versions they were actually produced with.

```text
uv run --locked python -m scripts.weil_continuation_driver \
  --support 19/40 \
  --n-min 48 \
  --n-max 80 \
  --n-step 4 \
  --output-dir computations/.../data/continuation-T019-040
```

An explicit dimension list can be supplied instead:

```text
uv run --locked python -m scripts.weil_continuation_driver \
  --support 19/40 \
  --n 48,52,56,60,64,68,72 \
  --output-dir computations/.../data/continuation-T019-040
```

The default final stdout output is a concise human summary; pass `--json` when the full result object is needed on stdout. During the run, the CLI emits short elapsed-time progress lines to **stderr** and flushes every line immediately, keeping stdout reserved for the final human or JSON result. Live messages cover stage starts/completions, scout resolution completion, stable-positive selection, rigorous targets, per-precision Arb attempts (including from spawned rigorous workers), candidate rounding/confirmation, bundle writing, and the final terminal state. Stderr is advisory: a closed or broken stderr stream cannot invalidate computation/finalization because `.live/` remains the durable operational channel. Pass `--quiet` to suppress these live stderr messages without changing final stdout or the `.live/` observability files. The bundle remains the durable audit artifact.

Before creating live state or doing scout/Arb work, the CLI acquires an exclusive OS-backed lock at `<output-dir>/.run.lock`. Windows uses a nonblocking `msvcrt` byte-range lock and POSIX uses `flock`; the JSON file carries the owning `run_id`, parent PID, command, support, and start time for diagnostics, but the kernel lock—not the PID metadata—decides whether the directory is active. If another process targets the same directory while the lock is held, it exits immediately with the active run ID/PID/start time before any expensive work begins. If a process crashes, the OS releases ownership automatically; a stale `.run.lock` file alone therefore does not block a later run and is overwritten after successful reacquisition. The lock pathname is intentionally never unlinked as part of release/rejection, because deleting a shared lock path after releasing the OS lock can race with a new POSIX owner and create two lock inodes; an unlocked stale file is harmless. The lock file is operational metadata and is excluded from the continuation manifest just like `.live/`.

Immediately after lock acquisition, the CLI captures one start-of-run provenance snapshot and writes `<output-dir>/.live/run.json` before status/events or mathematical computation begin. `run.json` is immutable for the lifetime of the directory and records the shared `run_id`, driver and driver version, exact support, requested dimensions, parent PID, start time, Git commit, and Git dirty flag. When the output directory is inside the repository, the owned output directory itself is excluded from the Git status query so `.run.lock`/`.live` do not make a clean checkout appear dirty; source-tree changes elsewhere still set `git_dirty=true`. The same provenance object is reused for the final bundle rather than queried again. A surviving `run.json` therefore identifies an interrupted/prior run and causes ordinary fresh-run reuse to fail closed even after the OS lock has disappeared.

Finalization is transactional. Reaching a mathematical terminal state does not by itself create a completed bundle. The driver first exits every process-pool context, requires access to the spawned-worker registry, verifies that each captured worker process is no longer alive and has an exit code, verifies that no executor remains active, and only then freezes the final result through JSON and records its SHA-256. The bundle boundary independently validates the complete cleanup-report shape, requires a known pre-theorem terminal state, rejects theorem/admission flags, and recomputes the frozen-result digest rather than trusting the caller. Stage artifacts are written first, `summary.json` is written after them, and `run-manifest.json` is written **last** as the bundle completion seal; artifact writes are flushed/fsynced before publication, with directory metadata fsynced on POSIX. The manifest also records a top-level `process_lifecycle` summary derived from that already-validated cleanup report: the parent PID, canonical `spawn` worker model, `worker_cleanup_verified=true`, `active_children_after_cleanup=0`, and executor/reaped-worker counts. Canonical finalization cross-checks that parent PID against immutable `.live/run.json`, while tests also require it to agree with `.run.lock` and `run-status.json`. Here `active_children_after_cleanup` is deliberately scoped to driver-managed process-pool workers observed by Python; it is not an OS-wide descendant-process claim, which remains Portus's responsibility. After the manifest write, the heartbeat supervisor must stop and join cleanly. Only then is `BUNDLE_FINALIZATION_COMPLETED` appended, live status set `terminal=true`, and `RUN_COMPLETED` appended. A heartbeat I/O failure therefore rolls the manifest back instead of allowing a completed run after supervision was lost. The output-directory lock is then released before final stdout is emitted. Therefore a valid `run-manifest.json` means the mathematical result had already been reached, parallel worker cleanup had been verified, the frozen payload matched its recorded digest, and live supervision survived through bundle finalization—not merely that computation stopped producing output.

Executor cleanup has an explicit defense-in-depth recovery path without replacing the existing `with ProcessPoolExecutor(...)` architecture. After normal pool shutdown returns, the driver checks the exact captured executor `Process` objects and cross-checks them against `multiprocessing.active_children()`. If an owned worker is still alive or unreaped, cleanup escalates through a short join (`0.5s`), `terminate()` plus join (`1.0s`), then `kill()` where available plus join (`1.0s`). Only the captured executor workers are eligible for those actions; unrelated children returned by `active_children()` are recorded diagnostically and never terminated by the continuation driver. Successful recovery is recorded in `.live/events.jsonl` and aggregated into the manifest cleanup fields. Any owned worker still unresolved after the final check fails the run and prevents a completed manifest. This does not solve a Python executor whose own `shutdown(wait=True)` never returns; Portus remains responsible for stronger OS-level process-tree containment, and bounded cancellation of a truly wedged executor is a separate later concern.

If execution raises after live state has started, the CLI does not leave a completed manifest. Runtime/finalization errors produce `<output-dir>/.live/failure.json` with operational state `RUN_FAILED`; `KeyboardInterrupt` produces `RUN_INTERRUPTED`. The same state is written to `run-status.json` with `terminal=true` and appended to `events.jsonl`. If a failure occurs after a manifest was tentatively written but before completion status/events finish, the manifest is removed. Partial scout/rigorous/candidate/summary files may remain for diagnosis, but without `run-manifest.json` they are explicitly incomplete and must not be treated as a finalized continuation bundle.

While the CLI is running, it maintains `<output-dir>/.live/run-status.json` as a tiny atomically replaced operational snapshot. The file records the same stable run ID, command, support, parent PID, start/update timestamps, elapsed time, current workflow state, a bounded current-operation payload, and whether final bundle writing has completed. In addition to milestone-driven updates, a parent-owned heartbeat thread refreshes `last_heartbeat_utc` and `elapsed_seconds` every 12 seconds by default. A heartbeat claims only that the parent process and its heartbeat supervision are alive: it does not change the workflow state/current operation and does not claim mathematical progress. The heartbeat thread is explicitly stopped and joined on every CLI exit path covered by the driver lifecycle.

The same run also maintains `<output-dir>/.live/events.jsonl` as an append-only structured event journal. Each flushed/fsynced JSON line carries a monotonically increasing sequence number, timestamp, run ID, event name, and only small event-specific fields. Canonical driver event/status payloads bound long strings and replace oversized lists with count/preview/truncated summaries, so a large requested dimension range cannot silently turn operational telemetry into multi-kilobyte state; retained mathematical results are not changed by this live-only bounding. The journal records run start/completion, workflow transitions, scout stage/resolution milestones, rigorous dimension milestones, candidate construction/confirmation milestones, bounded failure diagnostics, and bundle finalization. The parent process remains the sole journal writer, so parallel child processes never race on the JSONL file. R4's exact in-child rigorous precision messages are intentionally stderr-only; adding those child details to the durable parent-owned event chronology still belongs to the later worker-observability hardening. All `.live/` files are operational metadata rather than mathematical evidence and are intentionally excluded from `run-manifest.json` artifact hashes.

The CLI uses bounded spawn-based process parallelism by default: up to three workers for the independent floating-scout resolutions and up to two workers for the independent primary/fallback rigorous screens. Parallel futures are observed with completion-order semantics, so `.live/events.jsonl`, live status, and stderr report a completed/failed scout resolution or rigorous dimension as soon as the parent can consume that future; they do not wait for an earlier-submitted job. Completion chronology is operational only. Successful/failed outcomes are buffered by stable resolution level or dimension and then materialized into `scout_runs`, per-dimension scout series, `scout_failures`, `rigorous_screening`, `rigorous_failures`, and survivor/candidate priority in canonical resolution/dimension order. Worker timing therefore cannot change reconnaissance sample order, retained bundle ordering, or which surviving dimension is tried first. Each worker defaults BLAS/OpenMP-style thread counts to one unless explicitly overridden, preventing process-level parallelism from multiplying hidden library threads. The precision ladder inside each rigorous screen, exact candidate construction, and candidate cross-precision confirmation remain sequential by design.

For deterministic sequential reproduction or debugging:

```text
uv run --locked python -m scripts.weil_continuation_driver \
  ... \
  --scout-workers 1 \
  --rigorous-workers 1
```

Programmatic `run_driver()` callers remain sequential by default; the CLI owns the bounded parallel defaults. Cache writes use process-unique temporary files followed by atomic replacement so parallel jobs cannot collide on one generic `.tmp` path. On Windows, short-lived sharing/access denials during atomic publication are retried with a small bounded backoff for live status, bundle artifacts, and cache entries; persistent denial still raises and fails the run rather than silently degrading durability.

The CLI rejects a `--cache-dir` located inside its `--output-dir` before acquiring the run lock. Cache files are operational reuse data rather than bundle artifacts; allowing them inside the output directory would otherwise guarantee a late finalization failure after expensive work.

`CANDIDATE_READY` is generator-side evidence only and does **not** authorize theorem admission. The driver stops there. A separate human/research decision must first admit the exact support/dimension pair to the closed theorem contract; only after that separate change may a fresh independent Rust replay establish theorem status.

The driver escalates matrix rounding bits and witness bits independently when candidate construction fails. Once an exact positive candidate exists, it freezes `T`, `N`, residual order, matrix bits, and witness bits and reassembles at `p+128`; if that comparison is not stable it tries `p+256` before stopping. Candidate confirmation compares exact `mu_N`/even/odd margins, raw Arb enclosure contraction, exact rounded interval widths, and widest-entry conditioning diagnostics. A higher-precision contradiction or unresolved movement ends fail-closed as `PRECISION_LIMIT_REACHED`, not `CANDIDATE_READY`. The defaults are configurable with `--candidate-precision-step` and `--candidate-precision-extra-steps`. Rounding, witness, mathematical-negative, and insufficient-precision outcomes remain distinct.

### `weil_legendre_schur_scout.py`

**Diagnostic/component tool.** Use this directly for isolated floating reconnaissance or historical reproduction, not as the first manual step of the ordinary continuation workflow.

```text
python -m scripts.weil_legendre_schur_scout --support 2/5 --max-mode 120 --quadrature-order 700 --shift-order 350 --n 32,40,48,56,64,72 --output-json computations/.../data/dimension-scout-T040.json
```

This script is reconnaissance only. Its finite tail truncation is not an infinite-dimensional bound and cannot certify positivity.

### `weil_support_continuation_scout.py`

**Diagnostic/component tool.** Use this directly for isolated rigorous full-tail diagnostics or historical reproduction; ordinary continuation precision search is owned by the canonical driver.

Supports `A-20260826-001`. It reuses the exact-polynomial/Arb full-tail assembler at exact rational support values, then converts only normalized matrix midpoints to NumPy/SciPy for support-margin reconnaissance. It reports `mu_N`, finite-block midpoint minima, Schur midpoint minima, and component penalty scales. Positive rows are not theorem certificates.

```text
python -m scripts.weil_support_continuation_scout --supports 7/20,3/8,2/5,17/40,9/20 --dimension 32 --prec 112 --output-json computations/.../data/support-scan.json
```

### `weil_support_candidate_check.py`

**Diagnostic/component tool.** Generator-side exact candidate checker for a deliberately selected continuation point. It performs rigorous Arb assembly, outward dyadic rational rounding, exact rational Schur construction, and exact rational congruence/Gershgorin checks. Ordinary continuation candidate search is owned by the canonical driver. This standalone checker deliberately does **not** emit a theorem certificate, modify the closed contract, authorize admission, or invoke the independent verifier.

```text
python -m scripts.weil_support_candidate_check --support 2/5 --dimension 40 --prec 256 --matrix-bits 72 --witness-bits 40 --output-json computations/.../data/candidate-T040-N40.json
```

### `cert/exact_prime_schur_certificate.py`

Proof-path exporter for the closed `exact_prime_legendre_schur` whitelist. It assembles rigorous exact-prime Legendre-Schur certificates, outward-rounds Arb matrices to exact dyadic rational intervals, derives exact rational parity congruence witnesses from rational midpoint `LDL^T`, and exports only explicitly admitted support/dimension pairs.

Current admitted examples:

```text
python -m scripts.cert.exact_prime_schur_certificate --claim C-0050 --support 7/20 --dimension 32 --prec 160 --matrix-bits 64 --witness-bits 32 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0051 --support 2/5 --dimension 40 --prec 256 --matrix-bits 72 --witness-bits 40 --output-json computations/.../data/certificate-T040-N40.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0052 --support 17/40 --dimension 48 --prec 384 --matrix-bits 88 --witness-bits 48 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0053 --support 9/20 --dimension 56 --prec 512 --matrix-bits 104 --witness-bits 56 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0054 --support 19/40 --dimension 68 --prec 384 --matrix-bits 64 --witness-bits 32 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0055 --support 1/2 --dimension 80 --prec 512 --matrix-bits 64 --witness-bits 32 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0056 --support 21/40 --dimension 96 --prec 512 --matrix-bits 64 --witness-bits 32 --output-json computations/.../data/certificate.json

python -m scripts.cert.exact_prime_schur_certificate --claim C-0057 --support 27/50 --dimension 104 --prec 512 --matrix-bits 64 --witness-bits 32 --output-json computations/.../data/certificate.json
```

`(27/50,104)` is contract-admitted and theorem-bearing as `C-0057`. `X-20260924-001` executed the command above from clean committed provenance, received independent zero-float Rust exit `0` / `passed=true`, passed real-certificate adversarial checks, and is explicitly registered in the retained-proof manifest.

The generator does not decide the theorem. `crates/rh_cert` independently validates the whitelisted pair, reconstructs the complement lower bound and factor-3 Schur matrix, and proves the parity blocks positive using exact rational interval congruence/Gershgorin checks. The retained theorem runs are `X-20260821-005`, `X-20260826-001`, `X-20260826-002`, `X-20260826-003`, `X-20260827-002`, `X-20260827-004`, `X-20260828-001`, and `X-20260924-001`.

### `cert/verify_retained_proofs.py`

Canonical retained-theorem artifact acceptance gate. It loads the closed manifest at `computations/retained-proofs.json`, validates its eight registered proof identities, hashes the exact certificate bytes, and replays every hash-valid artifact through the current independent zero-float `rh_cert` verifier.

```text
uv run --locked python -m scripts.cert.verify_retained_proofs
```

A successful run ends with `RETAINED PROOF CHAIN: PASS - 8/8`. The command is fail-closed and reports `MISSING`, `HASH_MISMATCH`, `VERIFIER_ERROR`, `THEOREM_FAILURE`, or `SEMANTIC_MISMATCH` per theorem while continuing through the full manifest. It **does not regenerate certificates** and it does not grant theorem status to a new support/dimension pair. It answers the narrower audit question: are the exact proof artifacts currently cited by the repository still byte-intact and accepted by the current independent verifier?

Fast manifest-only validation remains available as:

```text
uv run --locked python -m scripts.cert.verify_retained_proofs --manifest-only
```

The real eight-artifact pytest acceptance is deliberately excluded from ordinary test runs and can be invoked explicitly with:

```text
uv run --locked --extra test python -m pytest -q -m retained_proofs tests/test_retained_proofs_acceptance.py
```

### `cert/legendre_schur.py`

Rigorous shared assembly for the exact-prime Legendre-Schur proof and continuation work. It uses exact rational polynomial algebra for Legendre actions and overlap identities, Arb only for transcendental enclosures, closed logarithmic/log-squared moments for `G_V`, exact edge-overlap geometry for `G_2`, and the canonical Suzuki residual series plus rigorous remainder for `G_R`. The reusable assembler accepts an exact rational one-prime support `T`; theorem-specific certificate wrappers remain responsible for locking allowed supports/dimensions.

### `cert/prime_power_terms.py`

Additive multi-prime arithmetic operator core. Unlike the frozen one-prime edge-overlap implementation, this module is generic in the active prime powers and translation geometry. It recognizes `m=p^k` with exact integer arithmetic; rigorously constructs `log(m)`, `tau_m`, `Lambda(m)`, and `c_m` using Arb; enumerates the strict active set `log(m)<2T` and fails closed when a requested precision cannot settle a threshold; constructs the left/right translated polynomial pieces on `[-1,1]`; globally partitions by every translation breakpoint; sums all active signed arithmetic images on each cell; and integrates those combined images to obtain `P`, `P^2`, and `G_P=P^2-PD^{-1}P`.

`P^2` is computed from `<P phi_i,P phi_j>`, so mixed terms are present automatically. The focused regression suite includes exact overlap agreement with `first_prime_matrices()` in the one-prime window, a nonzero `P_2/P_3` cross-term test, and a `{2,3,4}` case at `T=7/10` where `tau_2<1`. This module is not yet connected to a multi-prime certificate exporter or verifier.

### `cert/multi_prime_legendre_schur.py`

Full rigorous post-v1 Legendre-Schur assembler. `assemble_multi_prime_schur()` uses the established potential moment formulas and Suzuki residual coefficients/remainder, with native exact polynomial convolution and assembly-local residual monomial-action reuse on the new path. The arithmetic block comes from `cert/prime_power_terms.py`, which uses native Arb shifts, products, and antiderivative evaluation on the shared partition, with coefficient-certified parity. Outputs include the active terms, combined `P`, operator `P_squared`, `A`, `GV`, `GP`, `GR`, `rho_R`, `mu`, and `schur`. The complement derives each compressed-shift norm from the rigorous path-graph chain length rather than assuming the one-prime `tau>1` geometry. Frozen v1 implementation and mathematical estimates are unchanged.

The P3 bridge tests are deliberate: before the `{2,3}` case is accepted, the generic assembler is compared against the frozen v1 path at four historical supports and dimensions 16 through 32. All relevant matrix/scalar enclosures overlap. Only after that bridge passes does the direct `{2,3}` test verify that the combined operator square contains a strictly nonzero cross term and does not reduce to the sum of the two individual squares.

P3 acceptance closes with the integrated focused target at `31/31` and the complete default Python suite at `574/574`. The frozen `cert/legendre_schur.py` remains unchanged.

### `weil_multi_prime_schur_scout.py`

Floating-only reconnaissance for the post-`p=3` path. It independently enumerates the numerically active prime powers, constructs each compressed translation in NumPy/SciPy quadrature, sums the combined `P`, and forms truncated component tail Grams labelled `GV`, `GP`, and `GR`. It reports per-term complement estimates and combined-prime singular-value/tail conditioning. These values are intentionally not Arb bounds and must never be used as theorem evidence.

### `weil_multi_prime_support_candidate_check.py`

Rigorous generator-side exact candidate stage. It consumes `assemble_multi_prime_schur()`, outward-rounds `A`, `GV`, `GP`, and `GR`, outward-rounds every active term's `c_m b_m` contribution separately, reconstructs the exact complement lower bound and factor-3 Schur matrix, and derives exact rational even/odd congruence witnesses. Output diagnostics include the individual active-term constants, `P/P_squared/GP` width conditioning, explicit `GP` widths, exact even/odd Gershgorin margins, and optional lower-vs-higher Arb precision contraction. `--prec`, `--matrix-bits`, and `--witness-bits` are independent controls; `--compare-prec` is diagnostic-only. `--dimension` is required rather than guessed.

P4 acceptance closes with the focused multi-prime/frozen-v1 target at `24/24` and the complete default Python suite at `578/578`.

### `weil_multi_prime_support_continuation_scout.py`

Rigorous-screen adapter for the multi-prime driver. It assembles `A/GV/GP/GR/mu` with `assemble_multi_prime_schur()` and independently confirms active terms `[2,3]`. Endpoints, widths and widest-entry diagnostics serialize as exact rationals. Midpoint eigendiagnostics use power-of-two scaling before binary64 conversion and restore units as rational numerical values, not certified spectral bounds. Unavailable diagnostics are explicit and require more precision, not failed assembly or mathematical rejection. It does not construct exact candidates.

### `weil_multi_prime_continuation_driver.py`

Canonical continuation workflow for future structural windows, initially hard-limited to `log(3)/2 < T < log(4)/2` with exact active set `{2,3}`. It intentionally duplicates the mature operational orchestration rather than refactoring the historical one-prime driver. Workflow: floating multi-resolution scout → stable dimensions → primary/fallback rigorous Arb precision search → exact matrix/witness bit ladders → generator-side exact candidate → higher Arb precision confirmation → `CANDIDATE_READY` or a fail-closed terminal state. Parallel stages use bounded spawn pools and `as_completed` for immediate observation, then materialize retained output in canonical order. Cache publication and result bundles are atomic; the manifest is the completion seal; worker cleanup must verify zero owned active children before finalization. The old `weil_continuation_driver.py` remains the historical one-prime path.

P5 acceptance closes with focused multi-prime/frozen-v1 tests at `35/35`, bundle/P5 regression at `29/29`, a real parallel CLI smoke with verified cleanup, and the complete default Python suite at `591/591`.

### `cert/certificate_v2_contract.py`

P6 structural contract helper for `rh-weil-certificate-v2`. It loads and validates `docs/contracts/rh-weil-certificate-v2.json`, then applies canonical cross-field checks that JSON Schema alone cannot express: no floats, reduced support/interval rationals, strictly increasing `arithmetic_terms`, prime base validation, `m=base_prime^exponent`, full matrix coordinate coverage, and correct even/odd witness dimensions. This module does **not** export theorem certificates and does not call the Rust verifier. `V2_ALLOWED_CONFIGURATIONS` is deliberately an empty `frozenset`; structure-valid v2 data is not theorem-admitted data.

P6 acceptance closes with `21/21` focused certificate-v2/frozen-v1/admission tests and `602/602` for the complete default Python suite.

P7 adds the independent Rust consumer for this structure under `crates/rh_cert/src/v2.rs` with format routing in `crates/rh_cert/src/dispatch.rs`. The Python helper above remains structural/generator-side tooling and does not call or substitute for the Rust verifier. Rust requires exact first-window terms `[2,3]`, independently derives the exact-rational prime losses and `mu_N`, rebuilds the factor-3 `GV+GP+GR` Schur blocks, and checks exact parity witnesses. The production v2 theorem whitelist is still empty. The Rust trust boundary remains exact-rational: it checks serialized interval arithmetic and relationships but does not independently establish the underlying transcendental Arb enclosures.

P7 closure: Rust `63/63`, strict clippy/rustfmt, focused Python `21/21`, complete default Python `602/602`, and retained theorem replay `8/8`.

P8 hardens the pre-continuation boundary. `certificate_v2_contract.py` now semantically enforces exact first-window terms `[2,3]`, exact `b_m=1`, coefficient/norm/complement relationships, matrix symmetry/parity, and fail-closed strict support from the serialized log intervals. The JSON Schema independently closes the serializable term shape to `[2,3]`. Cross-layer structural cases live in `tests/data/certificate-v2-cross-layer-v1.json`; closed theorem-admission cases live in `tests/data/multi-prime-admission-v2.json`. These are test-only oracles and are never production inputs. P8 closure is focused Python `41/41`, Rust `67/67`, full Python `608/608`, retained replay `8/8`, with strict clippy/rustfmt.

### P9 qualification performance result

The first real `T=11/20` qualification exposed a performance boundary in the generic rigorous path. The floating scout completed normally and selected `N=192` with fallback `N=196`, but two independent retries failed to finish even the first 128-bit rigorous assemblies within external execution allowances of roughly 30 minutes and one hour. The workers remained CPU-active; this was not a deadlock. No rigorous cache entry was committed before termination.

Treat this as **NOT QUALIFIED**, not as a mathematical negative. Do not keep extending the dimension grid or retry the same command expecting cached progress. Before another end-to-end qualification, profile and optimize the generic multi-prime rigorous assembler while preserving P2/P3 equivalence and P8 cross-layer gates.

### `profile_multi_prime_assembly.py`

Manual sequential rigorous-assembly timing CLI. It uses no continuation cache or process pool, permits nonpositive diagnostic complement at small dimensions, records source/runtime provenance, and publishes each completed sample. `--mode timing` measures uninstrumented wall/CPU totals; `--mode stages` reports nested inclusive/exclusive stage timings; `--mode cprofile` retains the hottest cumulative call records. Peak memory is a process-lifetime high-water mark. Interrupted output remains marked running, not completed. Diagnostic strings and JSON conversion occur outside the assembly timer.

```text
uv run --locked python -m scripts.profile_multi_prime_assembly --support 11/20 --dimensions 32,64,96,128 --precision 128 --residual-order 32 --mode timing --output-json computations/.../data/assembly-timings.json
```

[Phase 1/2 performance record](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md): 128-bit isolated `N=128` falls from `897.221 s` to `6.779 s`; `N=192/196` complete in `26.259/28.069 s`. Focused tests pass `65/65`, including exact residual-image and unoptimized interval references. These timings do not establish target candidate positivity, higher-precision readiness, full acceptance, or P9 closure. The frozen P9 driver was not run.

Phase 3 extends that record with `121/121` focused checks. `tests/test_multi_prime_assembly_performance.py` compares independent unskipped small references, exact residual coefficients/norms, and tighter high-precision enclosures, and couples bounded work counts to mathematical output comparisons. Driver tests exercise real support/precision cache isolation and generic-source fingerprint invalidation. Candidate tests independently reconstruct outward dyadic bounds, grouped factor-3 Schur blocks, and exact congruence/Gershgorin margins with separate Arb/matrix/witness controls. No runtime thresholds or new production caches were added. The timestamped phase 4 addendum retains higher-precision/throughput measurements and full acceptance executions; its readiness gate is blocked by target conditioning and unrelated workspace formatting failures.

### `profile_multi_prime_workflow.py`

Manual component-cost CLI, not qualification. `--mode throughput` measures uncached assembly in the driver's bounded verified spawn pool; `--mode candidate` times actual sequential candidate assembly, rounding, exact Schur and witness work, retaining expected stage failures and exact native conditioning widths outside the timer; `--mode scout` measures only the floating component over the requested dimension grid/resolutions. Every mode records provenance, lifetime peak memory and atomic JSON publication costs. Pool modes preserve completion observation, canonical result order and cleanup verification. No mode calls `run_driver()`, selects a candidate, uses continuation caches or seals qualification.

```text
uv run --locked python -m scripts.profile_multi_prime_workflow --mode throughput --support 11/20 --dimensions 192,196 --precision 512 --workers 2 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase4-throughput-512.json
uv run --locked python -m scripts.profile_multi_prime_workflow --mode candidate --support 11/20 --dimensions 192,196 --precision 512 --matrix-bits 64 --witness-bits 32 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase4-candidates-512-64-32.json
```

Phase 4 observes `34.893/37.460 s` isolated 512-bit assembly and `38.208 s` two-worker throughput, but target candidates fail exact midpoint LDL witnesses through Arb 768. Native combined-prime widths remain enormous despite precision contraction; this is not a mathematical negative. Full Python `647/647`, Rust `67/67`, strict Clippy and retained replay `8/8` pass; workspace formatting fails in untouched `rh_engine` files. Stop before P9. The retained cost model estimates a conservative 12-hour external allowance, not a runtime guarantee or launch authorization.

The user subsequently authorized the unchanged phase 5 qualification despite those blockers. [X-20261002-001](../computations/2026-10-02T010121Z-t11-20-multi-prime-qualification-after-hardening/record.md) records natural completion in `168.78 s` at `PRECISION_LIMIT_REACHED`: scout selects `192/196`; 128-bit screens report float-conversion overflow, and 256/384/512 remain insufficient. No candidate construction or mathematical rejection occurred. Source snapshots and final driver artifacts are retained, but phase 6 byte audit/reproduction was not run. P9 remains NOT QUALIFIED; do not change frozen controls to hide the conditioning limit.

Phase 6 independently audits both final manifests and every listed artifact, `18/18` per run, plus ordered result-payload digests. Fresh-cache Run B uses the same source snapshot and settings, naturally finishing in `169.39 s` at `PRECISION_LIMIT_REACHED`. Exact recursive canonical comparison passes with zero mathematical/diagnostic differences after predeclared metadata exclusions; `17/18` artifacts are byte-identical. A separate Windows process scan finds zero qualification survivors. These operational checks pass, but the qualification gate fails because both runs stop before candidate construction. P9 remains NOT QUALIFIED; no admission or further retry occurred.

Phase 7 separates exact-safe multi-prime diagnostics in `multi_prime_precision_diagnostics.py`, leaving the shared frozen-v1 helpers unchanged. Screening and candidate confirmation use exact width, sign and margin-tolerance comparisons, including overflow/underflow cases. The workflow version is `multi-prime-continuation-driver-p9-phase7-v2`; cache contract is `multi-prime-continuation-driver-v2`, with the new numerical dependency fingerprinted. Old float-payload cache entries cannot be reused. Rational-valued diagnostic fields now serialize as strings rather than binary64 numbers.

Phase 7 focused acceptance passes `144/144`. Real uncached 128-bit `192/196` screens complete without conversion exceptions but remain insufficient precision. A known one-prime overlap candidate confirms from Arb `256` to `384` at fixed `64/32` bits; this is not `{2,3}` target readiness. Commands, exact outputs and source hashes are retained in [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md). No conditioning redesign or qualification retry occurred; P9 remains NOT QUALIFIED.


### `profile_multi_prime_conditioning.py`

Enclosure diagnostic, never qualification. `--representations cell-legendre` now exercises production generic arithmetic. `global` and `cell-monomial` are explicit historical controls confined to this diagnostic. `--group-potential` uses production exact harmonic contractions; omitting it selects historical per-moment rounding as a control, not a production fallback. The diagnostic CLI uses canonical Legendre modes; the production operator also accepts arbitrary exact orthogonal polynomial bases.

Profiles retain exact rational widths/coefficient bounds through basis conversion, local affine coefficients, combined images, sampled control products/primitives/endpoints, and full `P/P_squared/PD^-1P/GP/A/GV/GR/Schur` matrices. Local Legendre integration uses diagonal exact norms instead of primitives. Product-stage probes sample diagonal degrees `0,N//2,N-2,N-1`; coefficient/matrix profiles are full. Basis-conversion measurements in local runs are controls. No wall-clock figure or width threshold grants acceptance.

`--witness-precision` requests actual outward candidate construction at that Arb precision, with independent `--matrix-bits` and `--witness-bits`. It reuses the genuinely assembled matrices. Exact rounded inputs are retained in candidate ZIPs, including when witness construction fails; failed inputs do not contain a successful witness. `--rayleigh-check` checks a leading-midpoint-system last-coordinate direction rounded to the requested witness bits against the rigorous even Schur block; it is not a spectral sign oracle. Complete intervals/vectors carry SHA-256 and are diagnostic inputs, never theorem certificates.

```text
uv run --locked python -m scripts.profile_multi_prime_conditioning --dimensions 16 --precisions 128,256 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase8-small-comparison.json
uv run --locked python -m scripts.profile_multi_prime_conditioning --dimensions 192,196 --precisions 128,256,384,512 --representations cell-legendre --group-potential --witness-precision 384 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase8-grouped-potential-targets.json
uv run --locked python -m scripts.profile_multi_prime_conditioning --dimensions 192,196 --precisions 384 --representations cell-legendre --group-potential --rayleigh-check --matrix-bits 104 --witness-bits 56 --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase8-rayleigh-cli.json
```

[X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md) records Phase 8 selected Arb-512 full-Schur widths `6.5763e-82/2.1290e-80`, but actual candidates fail at both `64/32` and frozen-maximal `104/56` bits. Strict negative exact interval directions at `192/196` independently replay `2/2`. Phase 9 implements the selected representation without changing the sufficient Schur test, support/grid, bounds or precision caps. P9 remains NOT QUALIFIED/P10 blocked. The rejection is not localized Weil-form negativity or an RH counterexample.

### `audit_multi_prime_candidate.py`

Standalone zero-float replay of `rh-multi-prime-candidate-audit-v1` inputs. Successful `weil_multi_prime_support_candidate_check.run_candidate()` results now contain `audit_inputs`: outward-rounded `A/GV/GP/GR`, exact complement inputs and prime losses, controls/basis/factor, both dyadic witness matrices and exact margins. The auditor reconstructs the positive complement and factor-3 Schur matrix, checks dimensions, parity and scalar relationships, and independently evaluates congruence centers/radii with native rational matrices. Reported margins must match the recomputed strictly positive values.

```text
uv run --locked python -m scripts.audit_multi_prime_candidate --input computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-overlap-base-audit-inputs.json --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-overlap-base-audit.json
uv run --locked python -m scripts.audit_multi_prime_candidate --input computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-overlap-confirmation-audit-inputs.json --output-json computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase9-overlap-confirmation-audit.json
```

These exercised inputs are the existing one-prime overlap control `T=2/5,N=40`, with fixed `64/32` bits and real Arb `256 -> 384` confirmation. They are not substitute qualification evidence for frozen `{2,3}` targets. Replay checks serialized rational arithmetic, not upstream transcendental enclosures or theorem admission; it never calls Rust.

The multi-prime workflow/cache versions are `multi-prime-continuation-driver-p9-phase9-v3` / `multi-prime-continuation-driver-v3`. Old cache entries cannot satisfy the new proof-input contract. Source fingerprints include the auditor and bundle publisher. Multi-prime bundle format is `rh-multi-prime-continuation-candidate-bundle-v2`; positive bundles require separate manifest-listed base and fixed-input higher-precision audit artifacts. Frozen one-prime bundle format and behavior remain unchanged.

Production piecewise images in `cert/prime_power_terms.py` expose `PiecewisePolynomial.legendre_coefficients`, representing `t=(x-(lower+upper)/2)/((upper-lower)/2)`. Global monomial `coefficients` and global translation/integration helpers are removed from that production module. An empty local coefficient tuple denotes the zero image on an inactive cell.

Phase 9 implementation/equivalence verification passes `159/159` focused and `696/696` default Python tests. The real frozen `192/196` candidates at Arb 384 and `104/56` bits still fail final even pivots `95/97`. Fresh independent exact replay proves strict negative directions in both complete rounded candidate Schur matrices (`2/2`) and all four Arb-384/512 matrices (`4/4`); all eight matrix-stage widths contract (`16/16`). The positive overlap control and component packaging smoke are not substitute qualification. Full readiness remains **BLOCKED**; no frozen-target positive base/confirmation exists, no qualification ran, and no support/grid/criterion or theorem-admission change occurred. Exact inputs, source snapshots, commands and audits are retained in [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md).

### Native multi-prime exact witnesses

`cert/multi_prime_exact_witness.py` implements the candidate's exact witness path separately from frozen v1. Fraction-free integer midpoint elimination accumulates inverse unit-lower LDL rows directly; exact quotient/remainder rounding and native midpoint/radius congruence preserve the same dyadic witness and strict Gershgorin margin. The independent auditor remains separate. Cache and candidate-profile fingerprints include the backend.

Phase 11's one retained-input smoke produces identical full rounded candidate inputs/rejection and identical proper-block witness/margin. Actual N196 candidate time falls `541.946 -> 53.525 s`; complete 97-mode proper witness time falls `1306.928 -> 22.725 s`. This is not positive full-target evidence. Post-cutover focused/default Python pass `77/77` and `715/715`; twelve frozen/shared byte controls remain unchanged. The reassessed external allowance is two hours per fresh run, four hours for the pair, not a launch authorization or full-positive runtime bound. Native memory is not claimed measured. See the Phase 11 addendum in [X-20261001-001](../computations/2026-10-01T215617Z-multi-prime-assembly-performance/record.md). No further benchmark sweep or Phase 12 run occurred.


## Shared implementation

`rh_tools.py` contains the standard-library Laguerre recurrence, prime sieve, von Mangoldt prime-power enumeration, pole parameters, high-precision trace accumulation, Simpson integration, turning-scale helpers, numerical zeta-zero evaluation via pinned `mpmath`, the retained small-`u` phase approximation, and the exact uniform pre-turning stationary map derived in `A-20260820-005`.

## Interpretation rule

These scripts can:

- falsify proposed identities or bounds;
- reveal numerical localization and scaling;
- expose phase loss caused by absolute values;
- identify unstable cutoff regimes;
- guide which analytic lemma is worth attempting.
They cannot prove RH by numerical verification. Retained historical/manual research runs use the established `computations/` record structure (`record.md`, `plots/`, `data/`) with exact parameters and limitations. Canonical continuation-driver runs use the driver's self-contained continuation bundle (`summary.json`, scout/rigorous artifacts, candidate data, and `run-manifest.json`). Both formats must retain enough parameters, provenance, and limitations for audit and reproduction.