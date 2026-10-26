# X-20261026-006: complete energy-aware Schur qualification

- **Created:** `2026-10-26T12:50:36Z`
- **Last updated:** `2026-10-26T13:09:30Z`
- **Status:** COMPLETE conditional mathematical criterion and bounded qualification, not an executed full positivity matrix
- **Claim:** C-0112

## Question and derived result

Can the fixed-case logarithmic discrepancy estimate support a complete low/coupling/infinite-complement criterion without collapsing the entire energy back to one scalar?

[The derivation](energy-aware-criterion-v1.md) answers yes at the level of a conditional acceptance operation. Starting from d_E<=alpha d+beta||.||², use the genuine Q-compressed unbounded reference c=gamma d-s||.||². A positive full-frequency weight h=max(m,g), together with complete low-band leakage, gives

    c[y]>=eta integral h|Jy|², eta=1-epsilon/m>0.

For exact full low A_low and complete dual weighted Gram G(K),

    A_low-eta^-1G(K)>0

suffices for positivity on the entire Fourier-form domain. The derivation also gives a positive norm gap, an explicit weighted low subtraction K_opt=M^-1R and a rigorous residual bracket for any approximate solve. Full finite-frequency and analytic infinite-tail enclosures make the resulting finite contraction well-defined and constructively enclosable at every fixed finite parameter tuple.

This is not a new full Weil positivity result. No actual A_low,M,R,H,G(K) array or Schur sign is generated. The accepted T3/4 frontier and C-0110/C-0111 remain unchanged.

## Risks resolved by the derivation

Low polynomial vectors really belong to the unbounded reference's operator domain. True cross columns therefore exist in H_T. The reference inverse is a form compression, not the reciprocal of a sign-changing whole-line symbol. Low-space subtraction is valid through orthogonality, but time compression does not commute with Fourier weights. The chosen whole-line dual representative may introduce extra outside-time loss; no equality or dominance is inferred.

The positive weight pays the complete leakage factor eta. Exact Schur algebra is standard and respects C-0093's matched-reference equivalence. The change is an unbounded outside reference, not relabeling finite coupled modes. C-0108's bounded scalar-plus-compact obstruction does not apply, but this supplies no favorable support law.

All active arithmetic and both pole signs enter the combined source before Gram products. Explicit BV constants, both Fourier tails and entrywise-to-operator uncertainty rules are retained. A finite solve, source precision or quadrature order is not substituted for those errors.

## Actual bounded controls and independent review

[Declared inputs](control-inputs-v1.json) fix seven non-Weil exact control groups and only the previously accepted T3/4,N312,alpha1/4,beta873/1024,R256 scalar case. [The program](qualify-controls-v1.py) executes all groups with exact fractions:

1. Compression and inverse do not commute.
2. Omitting leakage falsely passes a Schur matrix whose actual Schur is-1/44; the paid criterion rejects.
3. Weight-derived low subtraction improves its toy Gram from39/32 to67/60, with exact residual difference49/480.
4. A smaller-floor weighted reference beats a stronger scalar reference in one toy coupling direction and loses in another. Both are valid lower references to the same actual toy tail. Scalar-floor comparison alone cannot decide penalty order.
5. Strict eta positivity rejects equality and negative denominators.
6. Complete source-error payment rejects a nominally positive matrix at its zero lower boundary.
7. The whole-form norm-gap formula gives14/9 and a positive exact shifted determinant.

These are exact finite algebra controls, not sampled Weil modes or evidence of actual comparative advantage. The mathematical proof covers arbitrary finite low dimension and the full infinite complement.

At384-bit Arb precision the same program reconstructs the complete leakage and positive-weight hypotheses at the existing control. It proves g(256)>1/3 and epsilon<3/10^49, hence

    eta>=1-9/10^49,
    eta m>=1/3-3/10^49>1/4, m=1/3.

This qualifies the weight without reducing it to that scalar everywhere. It does not improve C-0111's outside lower1/3 or assert a new Schur sign. The independent reviewer approves the complete proof and the implemented formulas in a separate source/output audit. [Review](independent-review.md) distinguishes that read-only audit from actual executions.

## Reproduction and environment

Baseline commit is `0a10e5aef2ee451d224028f7746c55369002b36f`; this additive research source is uncommitted, not clean production-certificate provenance. Actual runtime is Python3.14.0/python-flint0.9.0. The initial canonical and captured-source program executions both pass. Their run receipts retain argv, cwd, stdout/stderr, exit0 and elapsed observations. These are not full-matrix benchmarks.

From the repository root, use a fresh output:

```text
uv run --locked python -B computations/2026-10-26T125036Z-energy-aware-schur-contract/qualify-controls-v1.py --output <fresh-controls.json>
```

The [six-file closure](source-v1/manifest.json) captures program, declared inputs, both imported project files and pyproject/lock. It runs with isolated Python and bytecode disabled. All imported project file origins are required to lie under the selected captured root. [Replay summary](data/replay-summary.json) records byte-identical canonical and isolated outputs, SHA256 `d8e59b87caebcb9494964650f7488624803f55c813b28a099a5e37bae911a9dc`.

[Preservation](data/preservation-check.json) verifies18 earlier bundle seals,1026 member bytes and16 protected public source/test/configuration files unchanged. No old test, procedure, packet, result, schema or admission is rewritten. The root manifest is written last and binds this new record, proof, controls, review, inputs, closure and receipts.

## Acceptance boundary

The complete conditional criterion, finite weighted projection, rigorous error rules and fixed-case positive-weight hypotheses are qualified. Actual complete source generation, full Schur positivity, dominance, extension beyond the known support, support-dependent useful constants, conditioning/work advantage and an unbounded family are not established.

There is no selected new support or dimension, full source/matrix/witness calculation, generic root CLI/library upgrade, new dependency, permanent regression suite, cloud/GPU operation or formal Rust/Lean run. The scalar premises inherit C-0110/C-0111's documented source and Arb trust. The new explicit finite/infinite proof is not production admission or a literature-originality claim. Frozen8v1/0v2/1v3 and RH unresolved remain unchanged. No commit or push is performed.
