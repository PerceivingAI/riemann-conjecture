# X-20261026-002: variable Fourier error and work requirements

- **Created:** `2026-10-26T02:04:35Z`
- **Last updated:** `2026-10-26T02:21:56Z`
- **Status:** COMPLETE, independently reviewed variable bounds and exercised scalar/exact controls
- **Claims:** C-0104, C-0105, C-0106

## Objective

Translate C-0102/C-0103's positive-reference/exterior envelopes into explicit truncation, source-accuracy and representation-work requirements. No new support matrix, sign, eigenvector, witness or certificate is generated. All earlier implementations and evidence remain unchanged.

## Mathematical deliverables

[Variable compact and work derivation](variable-complement-work-v1.md) retains the entire signed pole, full active arithmetic, combined mixed Gram and physical Legendre mass. With m=a-p>0, variable real-band weight W, c=T Omega and H=4T exp(T), it rederives complete double/one-sided bounds kappa and eta. The outside denominator is d=m-kappa>0; the mixed payment is epsilon=2p eta+eta². For genuine one-sided ordered source losses ell_A and ell_G,

    0 <= (A-GP/m)-S_lower
      <= [ell_A+ell_G/d+epsilon/d+p² kappa/(dm)] D.

A declared tolerance is not a proved positive gap. An explicit integer policy based on E_N(z)<3*2^(-N) for N>=max(1,3z) makes the complete compact/mixed loss at most any prescribed delta>0. This is sufficient, not minimal; the old geometric denominator condition alone does not certify small error.

[Variable quadrature and source map](quadrature-source-map-v1.md) proves a pole-free strip, explicit complex digamma envelope and finite-series remainder. Exact uniform panels and a complete operator Taylor/Gauss bound give a computable sufficient frequency order for any declared analytic tolerance. First-omitted0F1 bounds cover every finite argument, Fourier prefactors, both high anchors, positive-argument pole transforms and all downward propagation. Uncertain reciprocal coefficients and local residuals are retained.

The maps distinguish analytic quadrature, analytic series, finite arithmetic/root/argument widths, publication rounding, and conversion to ordered physical-mass bounds. Center-radius and true-to-ordered losses differ, including the factor of two. Fixed4096/208/384/128/470 constants are not extrapolated. A working-precision guarantee still needs quantitative input widths, node separation, recurrence amplification, intermediate magnitudes and implementation rounding bounds. No unknown low gap is assumed.

The complete active count satisfies J_ar(T)=Theta(exp(2T)/T). Exact square-domain count is2J_ar² plus twice the number of strictly active ordered products mn. Combined nonempty cells and independent direct pair domains are distinguished. Six full triangles have3N(N+1) interval slots. Continuing to use the present geometric enclosure forces N>c/2-1, hence more than3c²/16 serialized slots for c>=4. With C-0103 this is a double-exponential dimension/payload obligation for that enclosure and representation, not for every basis, representation or analytical proof. Classical contraction volumes are explicitly identified as shapes, not FLOPs, runtime, peak RAM or bit complexity.

## Verification and primary sources

[Independent mathematical review](independent-map-review.md) approved both maps without findings. The reviewer independently checked normalization, endpoints, signed pole, denominator, mixed terms, dimension policy, complex domain, quadrature constant, first-omitted indexing, recurrence, mass conversion and scoped work claims.

The exact primary [DLMF5.7.6](https://dlmf.nist.gov/5.7.E6.tex) and [16.2.1](https://dlmf.nist.gov/16.2.E1.tex) formulas were inspected. Gauss exactness/positive weights remain the existing R-0037 premise. R-0040 records the newly used hypergeometric definition; the geometric remainder and closed truncation policy are derived locally. Suzuki, the cited mathematical identities and Arb/FLINT numerical correctness remain explicit premises. No external implementation was imported, no literature originality is claimed and no Lean/Rust acceptance is implied.

## Declared controls and actual observations

[input-pins.json](input-pins.json) was published before execution. It pins the already retained two-case scalar evidence and pointwise assessment through their original bundle seals. Declared budgets are compact comparison loss1e-18, boxed analytic quadrature order loss1e-24 and publication order loss1e-27, with theta1/2. None is an assumed low positive gap.

The following are derived scalar-policy requirements on the two existing supports, not selected new matrix experiments or claims that their already accepted N312 must be increased.

| Existing support | Coarse sufficient N | Uniform panels | Sufficient q | Publication bits for declared rounding loss |
| --- | ---: | ---: | ---: | ---: |
| 1353/2048 | 508 | 1024 | 55 | 108 |
| 3/4 | 576 | 1024 | 55 | 109 |

The uniform-panel policy is deliberately conservative and does not supersede the successful68-panel fixed implementations. The published128-bit grid exceeds the stated rounding-only requirements; no conclusion about sufficient working precision follows. Scalar N312 checks reproduce the earlier complete post4 kappa/mixed allowances and the two cases'4/7 nonempty cells and8/20 square domains.

Additional exercised controls:

- Four exact toy geometric-tail arguments0,1/4,1,2 satisfy the closed sufficient bound. A noncontracting denominator is actually rejected.
- An exact uncertain-reciprocal toy gives final center17/3 and required radius25/3. The endpoint true value14 is excluded by ignoring coefficient width. These are recurrence test data, not Bessel anchors or a Weil support.
- The unchanged independent checker's entire-series routine encloses the independent sin(w)/w and sinh(w)/w identities at w3/2, with both signs and order40, summands0 through40 inclusive.
- Both retained cases meet the complete derived compact/mixed and boxed quadrature budgets, source-publication inequality and exact domain-count identity.
- Eight complex digamma probes across the two cases fit the new strip envelope and independent finite-prefix remainder. These probes check the proof implementation, not uniform validity by sampling.
- For declared positive argument intervals around half-band arguments, the full anchor-prefactor/recurrence analytic bound meets vector-tail target2^-80. Positive amplification majorants are about2.26e170 and2.40e157, illustrating why tiny anchor tails cannot be treated as final errors. The resulting first omitted indices189/203 apply only to these scalar control intervals. They do not replace the complete fixed source's384-order policy or prove a working-width target.

[controls-v1.json](data/controls-v1.json) retains exact rational bounds and qualified displays. Canonical execution passed on the first run. No permanent test, producer/checker edit, dependency or generic tool was introduced.

## Actual command, source closure and isolated replay

Baseline public revision is `9cde2f4dc148b0de309e0d5f462072fbf571cfca`. Runtime is Python3.14, python-flint0.9, Arb512. Exact environment and actual executable/command/stdout/stderr are retained under data/.

Equivalent invocation from the repository root:

```text
uv run --locked python computations/2026-10-26T020435Z-variable-fourier-error-work/variable-controls-v1.py --output <new-output.json>
```

The actually exercised invocation used the locked environment's Python executable, as captured in [the canonical receipt](data/scalar-exact-controls.run.json). Outputs use exclusive creation; do not overwrite the historical result.

The [thirteen-file source snapshot](source-v1/manifest.json) includes five imported project files, script/pins, both pairs of inherited input/seal files, and pyproject/lock. The same scalar program was run under that snapshot's own root. Every imported project file and namespace path is required to belong to the execution root. Canonical and isolated outputs are byte-identical, SHA256 `4a9591e1ef2cd99ab09b6e0942bb2694cb0e19bc8370487263b34564cd889431`. See [isolated receipt](data/isolated-scalar-exact-controls.run.json) and [replay summary](data/isolated-replay-summary.json). About0.330seconds in each receipt is scalar-control wall time only, not source-generation/audit cost.

[Preservation receipt](data/preservation-check.json) verifies14 previous bundle seals,915 historical members and16 protected public files unchanged. The root manifest is sealed last and preserves all exact bundle bytes without newline conversion.

## Remaining uncertainty and interpretation

There is now an explicit parameter-to-analytic-error and representation-work map, rather than fixed constants silently carried into new ranges. There is still no unknown-support low positive gap, universal successful working-precision law, practical global continuation proof or reason to treat sufficient tolerances as positivity.

The documented dimension/payload obligation is serious for the current dense geometric-tail execution strategy. It does not prove general computational impossibility, H0/Weil negativity, or failure of other positive references/Fourier arguments. An analytical all-support proof need not serialize separate dense certificates at every support. The existing T3/4 research positivity remains intact. Production admissions remain8v1/0v2/1v3 and RH unresolved. No full suite, Rust/Lean run, commit or push was performed.
