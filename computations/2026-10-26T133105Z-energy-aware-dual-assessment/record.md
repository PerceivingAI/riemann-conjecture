# Unavoidable outside-time loss in the whole-line dual contraction

- **Computation ID:** `X-20261026-007`
- **Created:** `2026-10-26T13:31:05Z`
- **Last updated:** `2026-10-26T13:43:38Z`
- **Status:** `COMPLETE`
- **Claim / finding:** C-0113 / F-20261026-007
- **Assessment:** STOP selecting this whole-line dual contraction for full positivity generation. The genuine compressed energy reference remains unresolved, not rejected.

## Objective and mathematical quantity

Assess whether C-0112's complete conditional criterion is quantitatively useful, rather than obtain another positive outside scalar. The investigated loss is specific: its whole-line dual representative contains archimedean output outside the physical time interval.

[The derivation](dual-loss-assessment-v1.md) constructs the normalized physical constant p0 on(-T,T) and a translated adjacent box r on(T,3T). The latter is a dual witness, not a Weil test in H_T. Every bounded-source and low-subtraction term is supported in the physical interval and pairs to zero with r. Thus for every finite K,N containing p0,

    G(K)_00>=I(T)^2/[m+C(T)], C(T)=5/(8piT),
    [A_low-eta^-1G(K)]_00<=a(T)-I(T)^2/[m+C(T)], 0<eta<=1.

Here a(T) is the exact full physical constant low entry, not a bounded-minorant entry. I(T)>0 is the exact nonlocal archimedean adjacent-box coupling. Positive digamma-resolvent series and complete tails enclose both. Since g=A-alpha w-beta<=A, the bound is uniform over allowed relative pairs, including but not limited to the current alpha1/4,beta873/1024.

This is an actual necessary condition on the defined whole-line Gram, not a toy comparison, sampled eigenvector or guessed support experiment.

## Inputs, environment and actual outputs

[Declared inputs](assessment-inputs-v1.json) fix the already verified T3/4, current floor1/3, the physical constant and outside adjacent box. No support/dimension/alpha grid or full source array is generated. Python3.14.0/python-flint0.9.0 executes the producer at384bits with64 positive series terms; the separate verifier uses512bits,128 terms and narrower two-sided tails.

The independent complete enclosures imply the following outward-rounded displays. Exact rational endpoints are retained in the packets.

| Quantity | Independently enclosed result |
| --- | --- |
| Actual full physical constant value a(3/4) | Between0.05986 and0.05990, positive |
| Outside-time archimedean coupling I(3/4) | Between0.93690 and0.93692 |
| Exact ideal whole-line acceptance diagonal, m1/3 | At most-1431/1024<0 |
| Necessary floor for this contraction to have a positive diagonal | m>57/4 |

The negative upper holds for every finite supported low subtraction, including the weighted optimum, and every low dimension containing the constant at the same floor. It holds with zero source error and perfect arithmetic. More precision, tighter quadrature and adding low modes at that floor cannot repair it.

The actual physical form value is positive. This is not a Weil negative direction, a refutation of the known positive control, or evidence that the positive outside bound was wrong. The artificial loss enters when the inverse penalty is upper-bounded in the larger whole-line frequency space.

## Parameter, conditioning and work assessment

The proof also derives generic support-dependent conditions. For a(T)>0 this specific contraction needs m>I(T)^2/a(T)-C(T). Positive-weight qualification then requires an exponential frequency anchor. The accepted geometric leakage ratio imposes a necessary dimension lower. At this one control, using the certified weaker floor57/4 gives:

| Relative-bound parameters when raising the floor | Necessary dimension in the geometric leakage recipe |
| --- | --- |
| Any allowed nonnegative alpha,beta | N>2097152 |
| Fixed alpha1/4,beta873/1024 | N>8589934592 |

These are conservative necessary bounds, not sufficient working dimensions, minimum Weil-positivity dimensions, generated matrices or universal complexity lower bounds. The dimensionless floor is being raised within this explicit h/geometric construction. This is not a hardware cutoff or a claim that every energy-aware method incurs these costs.

A conditional sufficient N policy, the full weighted mass conditioning estimate, complete analytic source tails and actual error dependence are retained in the derivation. No useful unknown-support alpha/beta or low-gap law is supplied. Dense source arrays would still have quadratic entry count; no numerical memory/runtime extrapolation or precision law is asserted.

The reason not to generate the current full matrix is already mathematical: its ideal diagonal cannot be positive. Honest one-sided source errors only worsen it. Raising the floor relocates the loss into a large necessary reference/cutoff dimension in this recipe instead of demonstrating an efficient escape.

## Independent verification and rejection controls

[Mathematical and code/output review](independent-review.md) independently approves the domains, Fourier factors, exact source signs, positive series tails, full witness-energy upper, all-K obstruction, publication rules and recipe-specific parameter/work scope.

The [producer](assess-dual-v1.py) uses canonical strict prime-power enumeration and a rate-series/sinh organization. The [verifier](verify-dual-v1.py) does not import it or its enumeration. It manually reconstructs the strict2/3/4 window, uses the a_k-series, a different exponential pole expression and independently narrowed tails. It checks original scientific enclosures, published negative upper, floor and both necessary dimension rows. Both first scientific executions pass.

Three actual falsified research packets reject with exit2 and no success output: an understated physical low interval, an inflated outside coupling and a fabricated repair-dimension bound. [Rejection summary](data/rejection-summary.json) binds their inputs and receipts. They are not production certificates.

## Reproduction and preservation

From the repository root, use fresh outputs:

```text
uv run --locked python -B computations/2026-10-26T133105Z-energy-aware-dual-assessment/assess-dual-v1.py --output <fresh-assessment.json>
uv run --locked python -B computations/2026-10-26T133105Z-energy-aware-dual-assessment/verify-dual-v1.py <fresh-assessment.json> --output <fresh-audit.json>
```

The baseline is `0a10e5aef2ee451d224028f7746c55369002b36f`. New research source is uncommitted, not clean production-certificate provenance. Raw receipts retain actual argv/cwd, stdout/stderr, exit codes and elapsed observations; these scalar workloads are not full-matrix benchmarks.

The [eight-file source/input/environment closure](source-v1/manifest.json) captures both new programs, declarations, all three imported project files and pyproject/lock. Source and independent audit run with isolated Python, bytecode disabled and project file origins required under the captured root. Both reproduce canonical bytes on their first executions:

- Source SHA256 `cc0699b16362f228d20d55c0a54f8d7f343c089bc374feeb9d140805402ae7b0`.
- Audit SHA256 `d2e3f2f0baaf528d0f48b2ed2de7996000bf38e21548d2069f5573585ec33076`.

[Replay](data/replay-summary.json) and [preservation](data/preservation-check.json) retain the evidence. All19 previous seals,1046 historical members and16 protected public source/test/configuration files are unchanged. The root manifest is written last; scoped raw-byte attributes prevent checkout conversion. No historical method, test, result or schema is rewritten.

## Interpretation and limits

The usefulness assessment is complete with a scoped STOP: this whole-line dual contraction at the qualified floor fails even the known positive control, and the quantified larger-floor repair is not a demonstrated useful extension mechanism. The exact energy-reference Schur and another representation are not rejected. No full-matrix implementation or larger-support sign run is justified by this result.

C-0110/C-0111 and C-0112's conditional theorem remain valid. Shared qualified-source and Arb/FLINT correctness premises remain explicit; numerical verification is not a Lean/Rust proof. No new full positivity theorem, support extension, global no-go, originality, root tool/dependency upgrade, cloud operation, permanent test suite or admission is claimed. Frozen8v1/0v2/1v3 and RH unresolved remain unchanged. No commit or push.
