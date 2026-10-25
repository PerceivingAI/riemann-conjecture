# Quantitative reference and global-residual comparison

- **Computation ID:** `X-20261025-005`
- **Created:** `2026-10-25T14:24:24Z`
- **Last updated:** `2026-10-25T15:08:18Z`
- **Status:** `COMPLETE` analytical qualification and actual scalar controls; no low-matrix sign or new support theorem

## Objective

Determine what quantitative information follows from a positive full-space arithmetic reference with Fourier exterior control, and compare a concrete complete real-residual inequality with the existing local residual allowance. Do not confuse source range, a sufficient tail budget or changed representation with positivity.

## Mathematical quantities tested

The [bounded-minorant derivation](bounded-minorant-closure-v1.md) gives the smooth-core Fourier identity, explicit complete compact-tail estimates and a full sufficient Schur predicate. The [global residual derivation](physical-tail-derivation-v1.md) and [independent qualification](physical-tail-qualification.md) give derivative, cusp, rank-two and one-sided tail bounds without a Taylor truncation. The independent [Fourier qualification](fourier-qualification.md) checks normalization, signs, domains and exterior estimates before numerical execution.

Actual quantities are A(256), its separately organized finite-series enclosure, the arithmetic norm allowance, compact Legendre tails, exact bump exterior-mass upper bounds, global real-residual tail bounds and direct-versus-partial-fraction kernel/derivative controls. The finite H0 low-matrix sign is not a tested quantity.

## Environment

- Python3.14.0, MSC v.1944, AMD64, Windows10.0.26300; exact details in [environment-v1.json](data/environment-v1.json).
- python-flint0.9.0;512-bit Arb for numerical enclosures, Fraction for rational majorants and final threshold comparisons.
- New research-only CLI: [`scripts.weil_reference_route_controls`](../../scripts/weil_reference_route_controls.py), final LF source SHA256 `adee8020419038735b8e1b8f7bff830d6d22adb06a3e09597902d0454fba1b13`.
- The existing `arb_to_rational_enclosure` helper is reused unchanged. All required source bytes, including the module and package markers, are captured in [source-snapshot/manifest.json](source-snapshot/manifest.json).
- Serial scalar work only. No GPU, cloud runtime, new solver, full test suite, Rust or Lean execution.

## Inputs and parameters

- Fourier controls: T=3/5 and1353/2048, a=7/2, Omega256; active terms2,3; Legendre orders192 and312 are existing baseline orders, not an optimized dimension search.
- Exterior corroboration: DLMF5.7.6 with4096 summands and explicit signed omitted-series bounds. Direct digamma is a second formula within the same Arb trust premise.
- Time-band upper obstruction: zero-extended polynomial bump of degree floor(T Omega/2), respectively76 and84. An upper bound is never relabeled a lower certificate.
- Global real-residual controls: T=1353/2048 and2, N20 and312; exact C(T)=11T²/24+23T³/144. The rank-two polar allowance is included in every full residual bound.
- Kernel point corroboration: t=0,1/2,1,4;32 partial-fraction terms and explicit tails for g,g',g''. The global inequalities follow from the analytical proof, not from sampling these points.
- Local comparison: the exact retained N312 C-0088 upper, copied with original file SHA256 into [matched-local-input-v1.json](data/matched-local-input-v1.json). No old scalar run or known local-radius refusal was repeated.
- Primary sources and exact formulas are identified in [source-provenance-v1.json](data/source-provenance-v1.json), `R-0028`, `R-0030`, `R-0036`, and [F-20261025-005](../../findings/2026-10-25T142424Z-reference-route-selection.md). No external implementation was imported.

## Reproduction procedure

From the repository root, with a fresh output path:

```text
uv run --locked python -m scripts.weil_reference_route_controls --input computations/2026-10-25T142424Z-reference-route-selection/data/matched-local-input-v1.json --output <fresh-output.json>
```

The exact actual command, stdout, stderr, exit status and timing are in [uv-module-qualified.run.json](data/uv-module-qualified.run.json). The direct canonical module and isolated captured-module executions are retained separately. For isolated replay, start Python with `-I`, insert only this bundle's `source-snapshot` at the front of sys.path, and use runpy.run_module("scripts.weil_reference_route_controls",run_name="__main__"); the fully expanded executed command is in [isolated-module-qualified.run.json](data/isolated-module-qualified.run.json).

The final canonical, isolated canonical, retained procedure and locked-uv outputs are byte-identical. This proves source replay, not independent transcendental verification. The complete report is [scalar-controls-v1.json](data/scalar-controls-v1.json); exact decision thresholds are in [rational-decision-checks-v1.json](data/rational-decision-checks-v1.json).

## Output

| Control | Actual result |
| --- | --- |
| A(256) | 3.707299742285642, rigorous enclosure retained |
| Independent exterior lower A(256)-7/2 | greater than1/5; displayed lower about0.206811600632522 |
| Arithmetic lower a-norm(P) | greater than19/8; displayed bound about2.375586827668162 |
| Compact double tail at T=1353/2048,N312 | upper display1.325825351758598e-83 |
| Compact one-sided/cross tail at the same parameters | upper display1.084572067806546e-41 |
| Compact double tail at T=3/5,N312 | upper display9.575604330891237e-110 |
| Global real-residual double tail at T=1353/2048,N312 | upper display2.520012011673555e-6 |
| Ratio to retained local C-0088 upper | display4.242991133383660; new bound is coarser locally |
| Global real-residual double tail at T=2,N312 | upper display3.185785933389767e-5; outside the old Taylor radius |
| Final locked CLI and isolated CLI | exit0; about0.292/0.274 seconds in captured runs |

The N192 scalar compact majorant does not certify a positive bounded-minorant tail with these parameters. That is a failure of this sufficient estimate, not a negative H0 direction. The bump upper bounds are8.623820666106795e-66 and1.633374179487202e-72; neither is a concentration lower bound.

## Interpretation

The Fourier calculation closes the infinite-complement allowance for one explicit bounded minorant. With d=19/8-10^-82, all mixed compact/arithmetic cross terms can be paid by3e-40 I on top of the combined GP. The remaining conditional predicate is exactly the finite A312-(GP+3e-40 I)/d sign, not a qualitative compactness assertion or an uncomputed exterior-gap lower bound.

The real-source calculation gives an independently qualified global residual and one-sided range-gain inequality. It is a source-range contribution beyond2T<pi, not a stronger current local double-tail allowance. Its smooth part grows polynomially in T while the separated polar component must still be paid. Neither source range nor a positive tail alone yields an unbounded positive family.

These are new explicit repository derivations and controls based on standard external identities. Novelty, comparative implementation speed and literature priority have not been established.

## Limitations

No finite-band matrix source, independent matrix acceptance, H0 sign, fresh positivity witness, new support, production certificate or theorem admission is produced. Root certificate/verifier behavior and old local-radius refusals remain unchanged. The global residual estimate does not identify complete operator domains with Suzuki's canonical realization. The two-prime arithmetic constants do not extend automatically across m4. Numerical enclosures rely on python-flint/Arb; written independent qualification is not a Lean or Rust verification.

Admissions remain8v1/0v2/1v3, with C-0067 at T11/20; RH is unresolved. Historical mathematical sources, tests, computation bundles and theorem artifacts were not rewritten.

## Related claims / findings

- C-0094 and C-0095 / [F-20261025-005](../../findings/2026-10-25T142424Z-reference-route-selection.md).
- C-0088 for the distinct retained local residual comparison.
- C-0093 for the distinction between a new full-space reference and a matched finite elimination rearrangement.
- A manifest-last [manifest.json](manifest.json) seals the complete retained evidence, excluding only its own root manifest.

## Timestamped execution corrections

- `2026-10-25T15:04:56Z`: final canonical source and captured module replay agree. The initial procedure failed before producing a mathematical report because Arb does not subtract a Fraction directly. The one-line explicit ball conversion fixed that interface. [Initial source](data/scalar-controls.initial.py) and [failure receipt](data/scalar-controls.run.json) preserve the failure.
- The first canonical root-file copy used CRLF, so its report differed only in script_sha256. Its exact [CRLF source](data/canonical-controls.initial-crlf.py), original canonical output and run are retained. The final source uses the existing LF convention; captured and canonical final results match exactly. No earlier mathematical result was changed by line-ending normalization.
