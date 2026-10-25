# Assessment of the completed Fourier structural crossing

- **Computation ID:** `X-20261025-010`
- **Created:** `2026-10-25T23:23:20Z`
- **Last updated:** `2026-10-25T23:33:31Z`
- **Status:** `COMPLETE` retained-case comparison, exact/scalar controls and mathematical scope assessment

## Objective and conclusion

Compare the accepted C-0096 Fourier baseline with the accepted C-0100 post-m4 case on mathematical scope, complete inputs, accuracy and actual work. Do not generate a new matrix or treat a finite continuation as an all-support mechanism.

The completed work demonstrates an implemented, independently checked structural crossing on the owner CPU at unchanged finite dimension and working precisions. It does not demonstrate lower data requirements, a timing speedup, a global support family or an efficient support-scaling law. The present globally positive arithmetic reference and nonnegative exterior cannot retain fixed a and Omega on unbounded supports. This is a specific necessary-parameter obligation, not a failure theorem for Fourier or Weil methods.

## Compared evidence and held controls

The original accepted packets, audits and timing receipts are inherited unchanged through [input-pins.json](input-pins.json). All12 inputs are bound both by exact raw-byte hashes and their original bundle seals. The calculation checks source/proof/audit linkage and full accepted slot inventories; it does not repeat the original analytical or exact proof audits.

| Quantity | C-0096 baseline | C-0100 structural case |
| --- | --- | --- |
| Support T | 1353/2048 | 3/4 |
| Active arithmetic terms | 2,3 | 2,3,4 |
| a,Omega,N | 7/2,256,312 | 7/2,256,312 |
| Complete parity block dimensions | 156+156 | 156+156 |
| Six serialized matrix slots | 292968 | 292968 |
| Source / audit working precision | 512 / 768 bits | 512 / 768 bits |
| Published fractional precision | 128 bits | 128 bits |
| Source / audit arithmetic order | 312 / 313 | 312 / 313 |
| Source / audit frequency order | 48 / 64 | 49 / 64 |
| Source nonempty combined-image cells | 4 | 7 |
| Independent low/square image domains | 4+8 | 6+20 |
| Complete source packet, compressed bytes | 3331807 | 3398061 |
| Complete proof packet, compressed bytes | 3557084 | 3627039 |

The later case has real4 overlap and the new central2/2 domain, not a relabeled two-term formula. Both use complete signed pole, band and combined GP with physical mass. No old low matrix or witness is a sign authority for the new case. Packet sizes are observations of different exact values and metadata; their small difference is not an information-complexity law.

## Reference and accuracy are not identical workloads

The baseline uses d0=19/8-1e-82,epsilon0=3e-40. The new case uses d0=63/32-4e-49,epsilon0=6e-24. The same mathematical source decomposition and a/Omega do not make those finite sufficient matrices identical.

| Certified quantity | Baseline | Structural case |
| --- | --- | --- |
| Complete quadrature operator upper, display | 4.32907935139e-21 | 2.51065776786e-21 |
| Reported finite even mass lower | 1.39956336347e-11 | 3.43039025379e-15 |
| Reported finite odd mass lower | 8.21361193846e-9 | 3.21584580137e-12 |
| Constant-trial necessary lower on a, display | 0.679807238965 | 0.919284317858 |

Order49 restores a sufficient quadrature-error comparison; it does not make actual errors or low gaps equal. The reported finite certificate lowers are smaller at the new point, but they come from different sufficient matrices and congruence/trace witnesses. Their ratios are NOT spectral-gap ratios or evidence of a critical support threshold.

The new source separates numerical intervals from analytic band inflation using exact grid ceilings. Its measured numerical A/GP order losses are about8.00e-34/3.29e-33. The old accepted packet has no equivalent separated report. No numerical-width improvement over the old implementation is inferred. Its actual complete intervals remain valid under the original proof.

C-0099's conditional resolution below1.5e-18 is justified by the new case's achieved budgets. It is a current-case sufficient error account, not a lower bound on an unknown future support gap.

## Actual operation receipts and model scope

| Accepted operation | Baseline seconds | Structural seconds | Observed ratio |
| --- | --- | --- | --- |
| Source generation | 25.12 | 34.1968 | 1.3613 |
| Exact finite proof | 3.01 | 3.7866 | 1.2580 |
| Complete independent audit | 73.30 | 96.8287 | 1.3210 |

Baseline values are tool-wall receipts reported to two decimals. Structural values are recorded subprocess perf-counter measurements. Supports, arithmetic domain counts, frequency order and inflation/width bookkeeping differ. There is no controlled timing experiment, warm/cold control, common end-to-end workload, peak-memory measurement or statistical speedup conclusion. Development, exploratory, regression, attack and isolation work is excluded from these stage figures.

The previously declared classical contraction-volume model gives source/audit ratios1964/1479 and6401/4210, about1.328/1.520. Those are shape accounting, not native FLINT operations or forecasts fitted by the observed ratios. Two supports do not establish a global computational law or superiority over the physical/harmonic route or external tools.

What is observed is narrower and useful: the structural case completed on the same local resources at the original precision settings. It required no GPU/cloud resource, larger dimension or accuracy retry. The implementation and independent acceptance capability are contributions even though no global mechanism follows.

## Necessary parameter growth of this reference

The [self-contained argument](reference-scaling-obligation-v1.md) proves C-0101. For normalized constant u_T on L²(-T,T),

r(T)=-<u_T,P_T u_T>=sum_(log(m)<2T) Lambda(m)/sqrt(m)*(2-log(m)/T).

If M_T=a(T)I+P_T is nonnegative, then a(T)>=r(T). Elementary finite Euler products and harmonic divergence show r(T)->infinity. No prime number theorem, RH, cancellation estimate or common positive coercivity constant is assumed.

If A(t)-a(T)>=0 on the whole exterior abs(t)>Omega(T), continuity requires a(T)<=A(Omega(T)). Thus along T_j->infinity these particular positive references require both a(T_j)->infinity and Omega(T_j)->infinity.

Using the current geometric Legendre tail formula additionally requires N>sqrt((T Omega)^2+1)/2-1, so that formula's dimension must also grow. Its six full matrix triangles have3N(N+1) serialized slots. These are obligations of the present sufficient construction and representation. They are not minimum positivity dimensions, lower bounds for all algorithms, H0/Weil negativity, or a proved growth rate for practical cost.

The argument supplies no quantitative usable a(T),Omega(T),N(T), conditioning, source accuracy or low positive-gap law. Neither do the two finite certificates. The fact that a7/2,Omega256 work through this boundary therefore cannot be extrapolated indefinitely.

## Executed controls and independent review

The fresh scalar evaluation of r(T) at BOTH already accepted supports is contained in the original P00-derived rational interval, including ordinary mass2. No new low matrix or support sign is computed.

An exact finite Euler-product control includes all prime factors through10 and dominates the harmonic sum through10; omitting3 breaks that comparison. A separate exact boundary control distinguishes the forbidden geometric ratio1 from a strict ratio below1. These finite controls corroborate formulas and edge directions; the unbounded conclusion comes from the written proof, not finite samples.

The [independent mathematical review](independent-scaling-review.md) accepts the scaling argument under its explicit hypotheses. It preceded execution of the comparison and correctly notes that no numerical result was then available. Its stage-specific limitation is preserved. The subsequent [canonical output](data/comparison-v1.json) and [actual receipt](data/comparison.run.json) provide that separate computational evidence.

## Reproduction and data closure

From the repository root, use a fresh output path:

```text
uv run --locked python computations/2026-10-25T232320Z-fourier-structural-assessment/comparison-v1.py --output <fresh-comparison.json>
```

The [captured code closure](source-v1/manifest.json) contains the calculation, exact input pins, unchanged scalar dependencies and lockfile. Original source/proof/audit inputs are inherited from their SHA-pinned public bundles, not copied into this assessment or regenerated. The input-root option names their repository root for data reads only. A separate [isolated import-origin control](data/isolated-import-origins.run.json) verifies that the scalar package and both imported modules resolve within the captured code closure.

Python-I-B execution of the captured calculation with `--input-root .` gives a byte-identical report; [isolated receipt](data/isolated-comparison.run.json) and [summary](data/isolated-replay-summary.json). Canonical and isolated runs exit0 in about1.07/1.08 seconds. Those are assessment-operation timings, not source-performance measurements. [Environment](data/environment.json) records Python3.14.0, python-flint0.9.0 and scalar Arb512.

No new source job, matrix sign, witness, permanent test, full suite, Rust or Lean run is performed. The old accepted evidence is not silently replayed through a changed method.

## Scope and preservation

[F-20261025-010](../../findings/2026-10-25T232320Z-fourier-reference-scaling-obligation.md) / C-0101 preserve the necessary-growth result and completed assessment limits. No existing producer, checker, test, source packet, proof or earlier record changes. The new root manifest is written last and excludes only itself.

Production admissions remain8v1/0v2/1v3. No schema, whitelist, retained-proof registry or production trust profile changes. No literature originality, unbounded positive family or RH conclusion is established. RH remains unresolved.
