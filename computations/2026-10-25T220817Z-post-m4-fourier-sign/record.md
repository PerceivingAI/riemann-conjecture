# Complete post-m4 bounded Fourier-minorant source and positivity

- **Computation ID:** `X-20261025-009`
- **Created:** `2026-10-25T22:08:17Z`
- **Last updated:** `2026-10-25T23:08:20Z`
- **Status:** `COMPLETE` fresh analytical acceptance and both exact finite parity lowers positive

## Objective and fixed mathematical case

Evaluate the complete bounded Fourier minorant at T=3/4,a=7/2,Omega256,N312, after genuine activation of4. These parameters and accuracy requirements were fixed before new low signs. The active terms are exactly2,3,4. One signed4 image overlaps about7.58% of the whole interval, and both threshold margins exceed1/20.

Ordinary scaled Legendre mass is D_j=2/(2j+1). The six complete source matrices are P,P²,GP,pole,band,A, with GP=P²-PD^-1P and A=aD+P+pole+band. Every signed mixed arithmetic product and the negative odd pole remain present. C-0097/C-0098/C-0099 give the full exterior, one-sided/double compact and mixed-Gram premises, independently of this new low sign.

The exact finite sufficient lower is

S_-=A_- -[(GP)_++6e-24 D]/[63/32-4e-49].

Positive exact congruences in BOTH complete156-dimensional parity blocks, the full positive outside denominator and the nonnegative complete Fourier exterior establish H0>0 on all L²(-T,T), then original complex smooth-test Weil positivity under the documented Suzuki/Arb premises. Finite sufficient-block lowers are not full-form spectral minima.

## Implemented source and independent operations

New separate modules are [`scripts.weil_m4_fourier_matrix`](../../scripts/weil_m4_fourier_matrix.py) and [`scripts.verify_m4_fourier_matrix`](../../scripts/verify_m4_fourier_matrix.py). The old C-0096 producer, checker and historical tests are unchanged. The new research packet is `research-fourier-m4-minorant-matrix-v1`, not a production Weil certificate format.

The source uses the unchanged generic prime-power definitions and seven-cell combined-image integration at polynomial Gauss312. The independent source uses six signed shifts, all36 direct image-pair intersections and polynomial Gauss313. Exactly20 domains have positive length, including the newly nonempty opposite-sign2/2 pair; coefficient d4=log2/2. The complete combined square, mass correction and parity are independently reconstructed.

Source Arb512/frequency Gauss49 and independent Arb768/frequency Gauss64 pay the whole band quadrature remainder. The independent entire Fourier vectors use384 inclusive finite-series orders and complete tails; pole vectors use128. Every prefactor and interval recurrence is propagated. Both Fourier-node ranges are strictly below192.

The [complete enclosure derivation](matrix-enclosure-derivation-v1.md) explains the numerical/analytic split. Numerical matrices are rounded first. Exact integer square-root ceilings then add the required analytic band radius directly on the dyadic endpoint grid, avoiding confusion with Arb's coarser radius-storage inflation. The independent checker strips those radii and recomputes the actual numerical order-loss reports. It does not trust the reported budgets.

## Environment and byte identities

Python3.14.0 and python-flint0.9.0. [Environment](data/environment.json), source lockfile and [complete executable closure](source-v1/manifest.json) are retained. Shared premises are Suzuki arXiv2606.09096v3, the qualified full Fourier mathematics, and Arb/FLINT transcendental and rigorous-root correctness. This is independent source organization, not a second arithmetic library or formal kernel proof.

- [Source packet](data/source-v1.json.gz), SHA256 `cd254a2a7002e17b56dce12a0ec00166eac8023e30374e38053d8963ade28b9c`.
- [Exact proof packet](data/proof-v1.json.gz), SHA256 `9e7b0e03254261e4a971be192d21c7991faefaf2f71b0cbbfe8faf946b186cef`.
- [Full independent acceptance](data/independent-audit-v1.json).
- [Separate exact-only replay](data/exact-replay-v1.json).

The compressed source/proof and altered input fixtures exceed2MB because their exact bytes are scientific trust evidence. All are reproducible and hashed, not optional plotting data.

The executed T3/4 producer was created with CRLF line endings. Its exact root source is explicitly pinned to CRLF on checkout; the new checker/tests are pinned to LF and the captured bundle is verbatim. No normalization rewrites the source fingerprint or requires pretending a later source version produced these packets. The line-ending policy does not change the numerical method or output.

## Accepted result and measured source quality

All48828 serialized slots in each of six matrices are independently contained,292968 in total. Neither inherited low arrays nor an old positive witness is an authority for this case. The first frozen source/proof/audit succeeds without a precision retry, changed dimension or support search.

| Complete finite sufficient block | Certified mass-normalized lower display |
| --- | --- |
| Even | 3.4303902537912005e-15 |
| Odd | 3.215845801374643e-12 |

The complete source quadrature operator-error upper is854332567774897665/340282366920938463463374607431768211456, about2.51065776786e-21. The full C-0099 matrix-order conversion remains paid; this scalar error alone is not the final lower loss.

The actual numerical-only A true-to-ordered-bound allowance is272251/340282366920938463463374607431768211456, about8.00073781264e-34. GP's is2238439/680564733841876926926749214863536422912, about3.28909049895e-33. Both include their relevant outward-grid consequences and are below the predeclared1e-27/1e-28 budgets. Full analytic uncertainty is separate and is not removed by reporting tiny numerical widths.

## Reproduction procedure

From the repository root, always use fresh output paths:

```text
uv run --locked python -m scripts.weil_m4_fourier_matrix source --output <fresh-source.json.gz>
uv run --locked python -m scripts.weil_m4_fourier_matrix prove --source <fresh-source.json.gz> --output <fresh-proof.json.gz>
uv run --locked python -m scripts.verify_m4_fourier_matrix <fresh-proof.json.gz> --source <fresh-source.json.gz> --output <fresh-audit.json>
uv run --locked python -m scripts.verify_m4_fourier_matrix <fresh-proof.json.gz> --source <fresh-source.json.gz> --exact-only --output <fresh-exact.json>
uv run --locked python -m scripts.verify_m4_fourier_matrix <fresh-source.json.gz> --source <fresh-source.json.gz> --source-only --output <fresh-source-audit.json>
uv run --locked --extra test python -m pytest -n 0 -q tests/test_fourier_minorant_matrix.py tests/test_m4_fourier_matrix.py tests/test_m4_fourier_audit.py
```

EXACT_ONLY_PASS never means fresh analytical acceptance. ANALYTICAL_SOURCE_PASS checks the complete source but claims no positivity on its own. The full PASS verifies both analytical source and exact positive finite consequences.

Isolated Python-I-B reproduction loads only the captured source prefix and invokes the same modules through runpy. The [source](data/isolated-source-v1.run.json), [proof](data/isolated-proof-v1.run.json) and [exact receipt](data/isolated-exact-replay-v1.run.json) regenerate byte-for-byte. A separate [fresh isolated analytical audit](data/isolated-source-audit-v1.json) also accepts all292968 entries in source-only mode. [Summary](data/isolated-replay-summary.json) records the precise distinctions. Public interpreter/command metadata is repository-relative; no numerical output or procedure is redacted.

## Behavioral and adversarial verification

All21 focused tests pass: the four original fixed-case regressions plus17 new producer/auditor cases. They cover the fourth coefficient, complete central/mixed square, physical GP mass, expanded transforms, negative odd pole, outward-grid inflation, actual numerical-width measurement, strict identity/byte binding and exact finite consequences. The old tests are not rewritten for this new support.

Seven actual altered inputs reject without success output. [Summary](data/rejection-summary-v1.json) and individual inputs/receipts retain the evidence. Unpaid mixed allowance, dishonest numerical-width report, forged margin, forged mass lower, singular witness and altered source-byte binding reject through exact/contract checks. A separately rebound source with a shifted band entry preserves its width reports but is rejected by actual fresh full analytical reconstruction at band[0,0]. That final attack is a genuine source-enclosure check, not merely an unchanged packet hash failure.

## Observed operation costs

| Operation | Observed seconds |
| --- | --- |
| Initial complete source | 34.20 |
| Initial exact positive proof | 3.79 |
| Complete independent audit | 96.83 |
| Separate exact-only replay | 2.60 |
| Isolated source regeneration | 33.07 |
| Isolated proof regeneration | 2.85 |
| Isolated exact-only replay | 2.54 |
| Fresh isolated analytical source audit | 96.40 |

These are actual operation receipts, not total session time, a matched speedup, a native complexity law or a peak-memory measurement. One heavy owned operation runs at a time. No GPU/cloud resource or altered precision is used. The earlier contraction-volume model remains a model, not an empirical scaling law inferred from this single new point.

## Interpretation and limits

C-0100 / [F-20261025-009](../../findings/2026-10-25T220817Z-positive-post-m4-fourier-minorant.md) establishes a new locally verified research support at T3/4. It demonstrates that the implemented full bounded reference can cross this genuine arithmetic boundary with complete source acceptance and exact finite proof at unchanged N312. No global support-covering family, literature originality, best support/dimension, asymptotic efficiency, comparative superiority or full canonical operator-domain equality is established.

Production theorem admissions remain8v1/0v2/1v3. No Rust/Lean acceptance, certificate schema, whitelist or retained-proof registry is changed. No full default test suite, Rust or Lean run is claimed. RH remains unresolved.

## Historical integrity

Original sources, tests, computation records and theorem artifacts retain their bytes and historical scope. This result has separate programs, tests, packets, execution receipts and captured executable closure. The root manifest is written last and seals all members except itself. No substantive failed source/proof run was suppressed; the first frozen scientific run passes, and the deliberately rejected altered inputs are retained separately.
