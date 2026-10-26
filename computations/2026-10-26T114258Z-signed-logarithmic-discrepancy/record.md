# X-20261026-005: a signed discrepancy bound in logarithmic energy

- **Created:** `2026-10-26T11:42:58Z`
- **Last updated:** `2026-10-26T12:12:12Z`
- **Status:** COMPLETE, uniform fixed-case form bound and complete outside lower independently accepted
- **Claims:** C-0110, C-0111

## Question and result

At the already accepted T3/4, obtain a signed discrepancy estimate at the logarithmic reference's own energy order, without the rejected derivative absorption and without demanding positive scalar aI+P first.

[The analytic contract](signed-symbol-contract-v1.md) and [qualified result](qualified-result-v1.md) establish

    d_E[f] <= (1/4)d_A[f]+(873/1024)||f||²,
    T=3/4, f in H_T intersect the logarithmic form domain.

Using the complete C-0107 Legendre/Fourier leakage bound at unchanged N312 and R256 then gives

    Q_W[f] >= (1/3)||f||²,
    f in Q_312 H_(3/4) intersect that form domain.

The independent conservative outside lower endpoint is about0.33486747806, strictly greater than the exact rational1/3. This closes the useful discrepancy-to-energy interface at this one control case. It is not a full low/cross positivity theorem, an all-support estimate or new support reach.

At this fixed case the earlier scalar-reference outside lower63/32-4e-49 is larger than1/3. No improved local coercivity is claimed. The contribution is an independently qualified, genuinely logarithmic-energy treatment of the signed discrepancy, with no derivative norm or bounded scalar reference substituted for that energy. Its comparative/global usefulness is not established by the control point.

## Why this is a uniform proof rather than sampling

The exact multiplier is

    rho(t)=2sum_active Lambda(m)/sqrt(m)*cos(t logm)
           -2Re[(exp((1/2+it)2T)-1)/(1/2+it)].

It includes every active term2,3,4 with Lambda(4)=log2, the complete signed continuum and a nonsingular zero-frequency value. The pole signs are retained through C-0107's exact identity P+K_pole=L_T-D_E with L_T>=0.

The producer starts with the declared2048 dyadic intervals covering[0,256]. Analytically proved global Lipschitz bounds and monotone lower logarithmic energy cover the whole of every closed interval. Deterministic refinement leaves2371 exact adjacent cells. The finite lower/upper supremum displays are0.8478898444883236/0.8517810378023383, a gap about0.003891193314 below1/256. A decreasing analytic bound proves both infinite tails, with producer upper about0.4464542510. It lies below the finite lower witness. Rounding the maximum upward on the declared1/1024 grid gives873/1024.

The reference is unbounded on the entire frequency line throughout. Frequency256 in the scalar proof is only the switch between finite certification and the infinity bound; R256 in the reference estimate bounds full Legendre-tail leakage. Neither is a discarded frequency band or a new compact bounded-H0 construction. C-0108's bounded scalar-plus-compact theorem is therefore not contradicted.

## Parameter declarations and both retained outcomes

[Initial pins](input-pins.json) fixed T3/4,alpha1/4,N312 and proof boundary256 before calculation. During mathematical qualification, before any scalar execution, [qualified inputs](qualified-inputs-v1.json) declared that both the inherited closed-policy reference anchor N/(3T)=416/3 and the already-qualified fixed-source anchor256 would be reported. The exact C-0104 geometric bound at c192 is available at N312; the coarse N>=3c policy is sufficient, not necessary.

Both results remain in the packets. The independent sufficient lower at the coarse anchor is about-0.125016; this estimate does not certify the true tail's sign. The retained fixed-source anchor gives the positive bound above. There is no support, dimension or alpha search, no post-execution anchor selection, and no new low matrix/sign.

## Independent verification and actual rejection controls

[Independent mathematical review](independent-mathematical-review.md) approved the signs, domains, uniform cover/tails, source rounding, independent numerical organization and form-to-outside implication without findings.

The standalone [producer](signed-bound-v1.py) works at Arb256 using the complex quotient and a coarse derivative constant. The separate [verifier](verify-signed-bound-v1.py), without importing the producer, checks all2371 intervals at Arb384. It reconstructs the real trigonometric quotient and source bounds, then independently certifies each interval with the sharper continuum derivative integral and alternative lower energy estimates. Those estimates use128 positive difference-series terms and C-0103's explicit logarithmic remainder. It verifies the exact cover, lower witness, finite gap, published beta, entire infinite tail and both complete reference margins. The exact E_N formula is reconstructed independently with factorials.

[source packet](data/signed-bound-v1.json) and [full independent acceptance](data/independent-audit-v1.json) retain exact rational bounds. Numerical and analytic interval uncertainty are enclosed, not inferred from decimal agreement or precision settings. Arb/FLINT enclosure correctness, the qualified source identities and cited mathematical inputs remain explicit premises; this is not a Lean/Rust kernel result.

Three actual altered scalar packets reject with exit2 and no success output: understated beta0, a missing interior frequency interval, and a false outside lower1. The [rejection summary](data/rejection-summary.json), altered input bytes and seven canonical/isolated/attack command receipts are retained. These are research scalar-proof checks, not production Weil certificates or a permanent test suite.

All original scientific executions pass on the first run. The intentionally rejected packets are not suppressed failed scientific cases. No existing producer/checker/test is changed.

## Commands, code closure and reproduction

Baseline public commit is `0a10e5aef2ee451d224028f7746c55369002b36f`. This new research calculation has its own captured uncommitted source, not clean production-certificate provenance. Actual runtime is Python3.14/python-flint0.9, with fixed256/384-bit source/audit settings. No precision ladder is used.

From the repository root, use fresh outputs:

```text
uv run --locked python -B computations/2026-10-26T114258Z-signed-logarithmic-discrepancy/signed-bound-v1.py --output <fresh-bound.json>
uv run --locked python -B computations/2026-10-26T114258Z-signed-logarithmic-discrepancy/verify-signed-bound-v1.py <fresh-bound.json> --output <fresh-audit.json>
```

Actual locked-environment executable paths, arguments, stdout/stderr, exit codes and elapsed times are in data/*.run.json. The producer and independent audit took about0.690/4.509seconds in the first receipts. These are scalar-proof observations, not a full source-generation benchmark or comparison with the old matrix workloads.

The [ten-file executable closure](source-v1/manifest.json) captures both programs, both input declarations, all four imported project files and pyproject/lock. Captured imports are enforced under their own root. Isolated Python with bytecode disabled regenerates both producer and independent-audit outputs byte-identically:

- Source packet SHA256 `872d643987790050f1f0414bd6473e7f76881e9b35b01fcf0ff8bbfe2f5ac792`.
- Independent audit SHA256 `1628749da24f8c47cefe12f79064dc6ac84bc767d97ab3bad619d8618958570b`.

[Replay summary](data/isolated-replay-summary.json) binds the observations. [Preservation receipt](data/preservation-check.json) checks17 preceding seals,988 historical members and16 protected public files unchanged. The root manifest is written last and preserves exact source/result bytes without newline conversion.

## Acceptance boundary

The fixed-case signed logarithmic form bound and positive complete outside estimate are accepted within the documented source/Arb trust model. Their positive contribution does not establish the finite low/cross arrays or a sufficient Schur sign for this different reference. Earlier positive matrices cannot be reused as those inputs merely because T is unchanged.

There is no new full positivity theorem, support extension, all-support parameter law, comparative dominance, practical global speed/RAM claim, literature originality or production admission. The full reference/coupling construction remains a separate obligation. Frozen8v1/0v2/1v3 and RH unresolved are unchanged. No root generic CLI/library, dependency, cloud operation, old-test rewrite, full suite, Rust or Lean run is introduced. The completed prior work was committed before this task; this new work is not committed or pushed.
